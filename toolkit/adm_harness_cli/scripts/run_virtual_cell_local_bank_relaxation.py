#!/usr/bin/env python3
"""Local necessary bank-power gate with full original stress and capacity."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess
import sys
import time

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix

from adm_harness.highs_feasible import verify_candidate
from adm_harness.source_ledger import sha256_file
from audit_joint_dense_work import DenseHistory
from audit_joint_support import bilinear
from audit_virtual_cell_receiver_contact import integrated_loss
from run_poynting_delivery import BASE, ROOT, write_json


class RawRows:
    """Retain original physical coefficients before solver transformations."""
    def __init__(self, columns):
        self.columns=columns; self.row=[]; self.col=[]; self.data=[]
        self.rhs=[]; self.labels=[]

    def add(self, entries, rhs, label):
        row=len(self.rhs)
        for column,value in entries:
            if value:
                self.row.append(row);self.col.append(int(column));self.data.append(float(value))
        self.rhs.append(float(rhs));self.labels.append(label)

    def matrix(self):
        matrix=csr_matrix((self.data,(self.row,self.col)),shape=(len(self.rhs),self.columns))
        matrix.sum_duplicates()
        return matrix


def _vector(value, size, name, *, nonnegative=False, positive=False):
    value=np.asarray(value,float)
    if (value.shape!=(size,) or not np.isfinite(value).all()
            or (nonnegative and np.any(value<0)) or (positive and np.any(value<=0))):
        raise ValueError('finite physical '+name+' vector required')
    return value


def _geometry(values, size):
    result={key:_vector(values[key],size,key,positive=True) for key in ('radius','ell','D')}
    if not np.allclose(result['D'],result['ell']*result['radius']**2,rtol=1e-10,atol=1e-12):
        raise ValueError('D must equal ell times radius squared')
    return result


def solve_local(t, target, midpoint_target, nodes, mids, *,
                reference_thermal_energy, midpoint_reference_thermal_energy,
                reference_receiver_energy, midpoint_reference_receiver_energy,
                cold_mass, receiver_capacity, converter_loss, temperature_floor=.01,
                bank_routing=True, method='highs', deadline=60.):
    """Check one material label; target inputs exclude reopened U0 and Z0.

    A,V,K,H,C are local nonnegative inventories. Stress uses actual geometry
    at nodes and midpoints, with linear midpoint inventories. Energy uses the
    registered frozen-panel weights. The false bank_routing option provides
    a manufactured comparison with unrestricted counter/material exchange;
    project runners always enforce the routing rows.
    """
    t=np.asarray(t,float);nt=len(t)
    if t.ndim!=1 or nt<2 or not np.isfinite(t).all() or np.any(np.diff(t)<=0):
        raise ValueError('finite ordered time nodes required')
    if (not np.isfinite(temperature_floor) or temperature_floor<0 or
            not np.isfinite(cold_mass) or cold_mass<=0 or
            not np.isfinite(receiver_capacity) or receiver_capacity<0 or
            not np.isfinite(deadline) or not 0<deadline<=60):
        raise ValueError('physical inventory, nonnegative floor and deadline in (0,60] required')
    if not isinstance(bank_routing,(bool,np.bool_)) or method not in ('highs','highs-ds','highs-ipm'):
        raise ValueError('boolean bank routing and an ordinary HiGHS method required')
    nodes,mids=_geometry(nodes,nt),_geometry(mids,nt-1)
    target,midpoint_target=map(lambda a:np.asarray(a,float),(target,midpoint_target))
    if (target.shape!=(3,nt) or midpoint_target.shape!=(3,nt-1) or
            not np.isfinite(target).all() or not np.isfinite(midpoint_target).all()):
        raise ValueError('finite uncredited node and midpoint stress targets required')
    U0=_vector(reference_thermal_energy,nt,'reference U',nonnegative=True)
    U0m=_vector(midpoint_reference_thermal_energy,nt-1,'midpoint reference U',nonnegative=True)
    Z0=_vector(reference_receiver_energy,nt,'reference Z',nonnegative=True)
    Z0m=_vector(midpoint_reference_receiver_energy,nt-1,'midpoint reference Z',nonnegative=True)
    loss=_vector(converter_loss,nt-1,'converter loss',nonnegative=True)
    if max(Z0.max(),Z0m.max())>receiver_capacity+1e-10:
        raise ValueError('reference receiver exceeds original capacity')
    B0,B0m=U0/nodes['D'],U0m/mids['D']
    credited=target+np.array([B0+Z0/nodes['D'],B0/3,B0/3])
    credited_mid=midpoint_target+np.array([B0m+Z0m/mids['D'],B0m/3,B0m/3])
    M=(nodes['ell']*nodes['radius'])**2;Mm=(mids['ell']*mids['radius'])**2
    thermal_weight=nodes['D']**(4/3);thermal_weight_mid=mids['D']**(4/3)
    phi=mids['ell']**2;psi=Mm/thermal_weight_mid;chi=Mm/mids['D']
    K0=nodes['D']**(1/3)*U0
    fluid_reference_panel=psi*np.diff(K0)
    receiver_reference_panel=chi*np.diff(Z0)
    forcing=fluid_reference_panel+receiver_reference_panel
    ids={key:np.arange(nt)+i*nt for i,key in enumerate(('A','V','K','H','C'))}
    hot_rating,cold_rating=5*nt,5*nt+1;columns=5*nt+2
    eq,ub=RawRows(columns),RawRows(columns)
    def terms(key,i,midpoint=False,scale=1.):
        return ([(ids[key][i],.5*scale),(ids[key][i+1],.5*scale)] if midpoint
                else [(ids[key][i],scale)])
    for midpoint,geometry,stress in ((False,nodes,credited),(True,mids,credited_mid)):
        for i in range(nt-1 if midpoint else nt):
            R,D,ell=[geometry[key][i] for key in ('radius','D','ell')]
            rho,p,q=stress[:,i];tag=('midpoint' if midpoint else 'node')+f':{i}'
            z=terms('H',i,midpoint,1/D)+terms('C',i,midpoint,1/D)
            ub.add(terms('A',i,midpoint,2/R**2)+z,rho-p-2*q,tag+':stress1')
            ub.add(terms('A',i,midpoint,2/R**2)+terms('K',i,midpoint,D**(-4/3))+z,
                   rho-p+q,tag+':stress2')
            ub.add(terms('V',i,midpoint,3/(ell*R)**2)+terms('A',i,midpoint,-1/R**2)
                   +terms('K',i,midpoint,2*D**(-4/3))+z,rho+2*p+q,tag+':stress3')
            ub.add(terms('K',i,midpoint,-1),-3*cold_mass*temperature_floor*D**(1/3),tag+':floor')
    for i in range(nt):
        ub.add([(ids['H'][i],1),(hot_rating,-1)],0.,f'node:{i}:hot_rating')
        ub.add([(ids['C'][i],1),(cold_rating,-1)],0.,f'node:{i}:cold_rating')
    ub.add([(hot_rating,1),(cold_rating,1)],receiver_capacity,'separate_original_ratings')
    for i in range(nt-1):
        delta=lambda key,weight=1.:[(ids[key][i+1],weight),(ids[key][i],-weight)]
        eq.add(delta('V')+delta('A',phi[i])+delta('K',psi[i])+delta('H',chi[i])+delta('C',chi[i]),
               forcing[i],f'panel:{i}:original_energy')
        ub.add(delta('H'),loss[i],f'panel:{i}:hot_direction')
        ub.add(delta('C',-1),0.,f'panel:{i}:cold_direction')
        if bank_routing:
            ub.add(delta('K',psi[i])+delta('H',chi[i]),forcing[i],f'panel:{i}:routing_lower')
            ub.add(delta('K',-psi[i])+delta('C',-chi[i]),chi[i]*loss[i]-forcing[i],f'panel:{i}:routing_upper')
    ae,au=eq.matrix(),ub.matrix();be,bu=np.array(eq.rhs),np.array(ub.rhs)
    lower=np.zeros(columns);upper=np.full(columns,np.inf)
    bounds=np.column_stack([lower,upper]);cost=np.zeros(columns)
    started=time.monotonic()
    result=linprog(cost,A_eq=ae,b_eq=be,A_ub=au,b_ub=bu,bounds=bounds,method=method,
        options=dict(time_limit=float(deadline),primal_feasibility_tolerance=1e-9,
                     dual_feasibility_tolerance=1e-9,ipm_optimality_tolerance=1e-10))
    check=verify_candidate(cost,result.x,A_eq=ae,b_eq=be,A_ub=au,b_ub=bu,bounds=bounds,
                           feasibility_tolerance=2e-7)
    passed=bool(result.success and check.verified_feasible)
    summary=dict(success=passed,local_necessary_relaxation_passes=passed,target_budget_passes=passed,
        ordinary_solver_success=bool(result.success),status=int(result.status),message=str(result.message),
        solver_method=method,solver_seconds=time.monotonic()-started,solver_deadline=float(deadline),
        solver_iterations=int(result.nit),variables=columns,equalities=len(be),inequalities=len(bu),
        original_lp_rows_and_bounds_verified=bool(check.verified_feasible),
        candidate_finite=bool(check.candidate_finite),temperature_floor=float(temperature_floor),
        bank_routing_enforced=bool(bank_routing),added_density=0.,reserved_density_fraction=0.,
        original_cold_rest_mass_retained=True,original_receiver_containment_retained=True,
        baseline_stress_and_power_credited_once=True,
        omitted_constraints=['explicit work-wave transport','wave population floors','guide and new interface costs',
            'shared spatial phase coherence','all hot and cold donor-rate limits'],
        full_source_construction_supplied=False,
        scope='favorable local net-bank-power necessity gate with full physical target, sampled stress and frozen-panel energy; transport, coherence, finite rates, optical and mechanical realization remain separate')
    for key in ('equality_residual','inequality_violation','lower_bound_violation','upper_bound_violation',
                'maximum_feasibility_violation'):
        value=float(check[key]);summary[key]=value if np.isfinite(value) else None
    arrays=dict(t=t,target=target,midpoint_target=midpoint_target,credited_target=credited,
        midpoint_credited_target=credited_mid,reference_thermal_energy=U0,
        midpoint_reference_thermal_energy=U0m,reference_receiver_energy=Z0,
        midpoint_reference_receiver_energy=Z0m,cold_rest_mass=np.array(cold_mass),
        receiver_rated_capacity=np.array(receiver_capacity),receiver_fixed_containment_energy=np.array(receiver_capacity/3),
        thermal_reference_inventory=K0,fluid_reference_power_panel=fluid_reference_panel,
        receiver_reference_power_panel=receiver_reference_panel,original_power_panel=forcing,
        converter_loss_panel=loss,phase_weight=phi,thermal_weight=psi,receiver_weight=chi,
        lp_cost=cost,lp_lower_bound=lower,lp_upper_bound=upper,
        lp_equality_rhs=be,lp_inequality_rhs=bu,
        lp_equality_labels=np.array(eq.labels),lp_inequality_labels=np.array(ub.labels))
    for prefix,matrix in (('lp_equality',ae),('lp_inequality',au)):
        arrays.update({prefix+'_data':matrix.data,prefix+'_indices':matrix.indices,
                       prefix+'_indptr':matrix.indptr,prefix+'_shape':np.array(matrix.shape)})
    for prefix,geometry in (('',nodes),('midpoint_',mids)):
        arrays.update({prefix+key:value for key,value in geometry.items()})
    if check.candidate_finite:
        state={key:result.x[index] for key,index in ids.items()}
        A,V,K,H,C=[state[key] for key in ('A','V','K','H','C')];Z=H+C
        qh=loss-np.diff(H);qc=np.diff(C)
        counter=(forcing-psi*np.diff(K))/chi-np.diff(Z)
        emitted=np.maximum(counter,0.);absorbed=np.maximum(-counter,0.)
        hot_to_fluid=qh-emitted;fluid_to_cold=qc-absorbed
        support=forcing/chi-loss;fluid=psi*np.diff(K)/chi
        balance=np.diff(V)+phi*np.diff(A)+psi*np.diff(K)+chi*np.diff(Z)-forcing
        arrays.update(lp_x=np.asarray(result.x),amplitude=A,balanced_radiation_inventory=V,
            thermal_inventory=K,receiver_hot_energy=H,receiver_cold_energy=C,receiver_thermal_energy=Z,
            hot_rated_capacity=np.array(result.x[hot_rating]),cold_rated_capacity=np.array(result.x[cold_rating]),
            balanced_radiation_rest=V/M,thermal_reservoir_rest=K/thermal_weight,
            receiver_rest=Z/nodes['D'],fluid_temperature=K/(3*cold_mass*nodes['D']**(1/3)),
            midpoint_fluid_temperature=(K[:-1]+K[1:])/(6*cold_mass*mids['D']**(1/3)),
            hot_contact_panel_heat=qh,cold_contact_panel_heat=qc,counter_panel_energy=counter,
            hot_to_counter_panel_heat=emitted,counter_to_cold_panel_heat=absorbed,
            hot_to_fluid_panel_heat=hot_to_fluid,fluid_to_cold_panel_heat=fluid_to_cold,
            retained_support_to_fluid_panel_energy=support,actual_fluid_power_panel_energy=fluid,
            original_energy_panel_residual=balance)
        summary.update(original_energy_panel_residual=float(abs(balance).max()),
            original_fluid_power_identity_residual=float(abs(fluid-support-hot_to_fluid+fluid_to_cold).max()),
            net_routing_violation=max(0.,float((counter-qh).max()),float((-counter-qc).max())),
            separate_rating_violation=max(0.,float(H.max()+C.max()-receiver_capacity)),
            minimum_fluid_temperature=float(min(arrays['fluid_temperature'].min(),arrays['midpoint_fluid_temperature'].min())))
    return summary,arrays


def evaluate(spec):
    center,floor,method,deadline,output=spec;output=Path(output)
    source=BASE/'joint_refined_response/members_fraction0.99_states.npz'
    h=DenseHistory('routed_family',source);x=np.array([center])
    t=np.unique(np.r_[h.state['t'],.047685546875,.0501953125,.072783203125,.5]);tm=(t[:-1]+t[1:])/2
    c,cm=h.coefficients(t,x),h.coefficients(tm,x);energy=h.energy(x)
    target=np.array([energy.evaluate(t)[0][:,0]/c['D'][:,0],h.pressure(t,x)[0][:,0],c['Q'][:,0]/c['D'][:,0]])
    midpoint=np.array([energy.evaluate(tm)[0][:,0]/cm['D'][:,0],h.pressure(tm,x)[0][:,0],cm['Q'][:,0]/cm['D'][:,0]])
    old=h.h.reference.h.state;ref=h.h.reference;receiver=h.h.state
    U0=bilinear(old['t'],old['x'],old['thermal'],t,x)[0][:,0]
    U0m=bilinear(old['t'],old['x'],old['thermal'],tm,x)[0][:,0]
    Z0=bilinear(ref.t,ref.x,receiver['heat'],t,x)[0][:,0]
    Z0m=bilinear(ref.t,ref.x,receiver['heat'],tm,x)[0][:,0]
    loss,duration=integrated_loss(h,t,x,order=8)
    summary,arrays=solve_local(t,target,midpoint,
        {key:c[key][:,0] for key in ('radius','ell','D')},
        {key:cm[key][:,0] for key in ('radius','ell','D')},
        reference_thermal_energy=U0,midpoint_reference_thermal_energy=U0m,
        reference_receiver_energy=Z0,midpoint_reference_receiver_energy=Z0m,
        cold_mass=float(np.interp(center,old['x'],old['number'])),
        receiver_capacity=float(np.interp(center,ref.x,receiver['heat_cap'])),
        converter_loss=loss[:,0],temperature_floor=floor,bank_routing=True,method=method,deadline=deadline)
    label=f'x{center:g}_floor{floor:g}_local_bank_relaxation'
    summary.update(label=label,center=center,time_nodes=len(t),spatial_samples=1,input=str(source.relative_to(ROOT)))
    arrays.update(x=x,proper_duration=duration[:,0])
    np.savez_compressed(output/(label+'_states.npz'),**arrays)
    write_json(output/(label+'_summary.json'),summary)
    print(label+': '+json.dumps({key:summary[key] for key in
        ('success','status','solver_seconds','maximum_feasibility_violation')}),flush=True)
    return summary


def verified_data_dependencies(source_manifest, root=ROOT):
    """Verify linked upstream data while current runtime Python is pinned separately."""
    root=Path(root).resolve();pending=[Path(source_manifest).resolve()];visited=set();hashes={}
    while pending:
        path=pending.pop()
        if path in visited:continue
        visited.add(path)
        if not path.is_relative_to(root):raise ValueError('source manifest must remain inside project root')
        relative=str(path.relative_to(root));current=sha256_file(path)
        if relative in hashes and hashes[relative]!=current:
            raise RuntimeError('changed upstream manifest: '+relative)
        hashes[relative]=current
        manifest=json.loads(path.read_text())
        for dependency,expected in manifest.get('input_sha256',{}).items():
            linked=(root/dependency).resolve()
            if not linked.is_relative_to(root):raise ValueError('upstream dependency escapes project root')
            if linked.suffix=='.py':continue
            if sha256_file(linked)!=expected:raise RuntimeError('changed upstream data: '+dependency)
            if dependency in hashes and hashes[dependency]!=expected:
                raise RuntimeError('conflicting upstream data identity: '+dependency)
            hashes[dependency]=expected
            if linked.name=='manifest.json':pending.append(linked)
    return hashes


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--centers',nargs='+',type=float,default=[-2.,-1.975])
    parser.add_argument('--temperature-floor',type=float,default=.01)
    parser.add_argument('--solver-method',choices=['highs','highs-ds','highs-ipm'],default='highs')
    parser.add_argument('--deadline',type=float,default=60.)
    parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--output-name',required=True)
    args=parser.parse_args()
    if (not np.isfinite(args.temperature_floor) or args.temperature_floor<0 or
            not np.isfinite(args.deadline) or not 0<args.deadline<=60 or not 1<=args.workers<=2 or
            not np.isfinite(args.centers).all()):
        parser.error('nonnegative floor, finite centers, deadline in (0,60], and one or two workers required')
    output=BASE/args.output_name
    if output.exists():raise RuntimeError('preserve completed local bank evidence')
    source=BASE/'joint_refined_response/manifest.json';previous=json.loads(source.read_text())
    target=source.parent/'members_fraction0.99_states.npz'
    if sha256_file(target)!=previous['output_sha256'][target.name]:raise RuntimeError('changed registered backing target')
    hashes=verified_data_dependencies(source)
    files=[source,target,Path(__file__),ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_local_bank_relaxation.py']
    for module in list(sys.modules.values()):
        filename=getattr(module,'__file__',None)
        if filename:
            path=Path(filename).resolve()
            if path.suffix=='.py' and path.is_relative_to(ROOT):files.append(path)
    hashes.update({str(path.relative_to(ROOT)):sha256_file(path) for path in files})
    output.mkdir()
    specs=[(center,args.temperature_floor,args.solver_method,args.deadline,str(output)) for center in args.centers]
    with ProcessPoolExecutor(max_workers=min(args.workers,len(specs)),mp_context=multiprocessing.get_context('spawn')) as pool:
        cases=list(pool.map(evaluate,specs))
    for relative,expected in hashes.items():
        if sha256_file(ROOT/relative)!=expected:raise RuntimeError('runtime input changed: '+relative)
    write_json(output/'summary.json',dict(cases=cases))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        workers=min(args.workers,len(specs)),input_sha256=hashes,historical_source=previous,
        output_sha256={path.name:sha256_file(path) for path in sorted(output.iterdir()) if path.is_file()}))


if __name__=='__main__':main()
