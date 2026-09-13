#!/usr/bin/env python3
"""Shared-phase local bank gate retaining original stress, storage and hot rate."""
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
from scipy.sparse import block_diag, csr_matrix, vstack

from adm_harness.highs_feasible import verify_candidate
from adm_harness.source_ledger import sha256_file
import run_virtual_cell_local_bank_relaxation as local
from run_poynting_delivery import BASE, ROOT, write_json


def raw_matrix(state, kind):
    prefix='lp_'+kind
    return csr_matrix((state[prefix+'_data'],state[prefix+'_indices'],state[prefix+'_indptr']),
                      shape=tuple(state[prefix+'_shape']))


def finite_check_summary(check):
    result={key:bool(check[key]) for key in ('verified_feasible','candidate_finite')}
    for key in ('equality_residual','inequality_violation','lower_bound_violation',
                'upper_bound_violation','maximum_feasibility_violation'):
        value=float(check[key]);result[key]=value if np.isfinite(value) else None
    return result


def solve_shared_phase(blocks, *, deadline=60.):
    """Append common A equalities to complete original local LPs, at zero cost.

    Each block uses the existing local A,V,K,H,C ordering and its own two
    bank ratings. Every original row, RHS, bound and physical input is kept.
    The shared phase adds no spatial transport, interface or guide cost.
    """
    if not np.isfinite(deadline) or not 0<deadline<=60:
        raise ValueError('deadline must lie in (0,60]')
    if len(blocks)<2:raise ValueError('at least two original local LP blocks required')
    t=np.asarray(blocks[0]['t']);nt=len(t);nb=len(blocks)
    if t.ndim!=1 or nt<2 or not np.isfinite(t).all() or np.any(np.diff(t)<=0):
        raise ValueError('finite ordered common time nodes required')
    sizes=[];equalities=[];inequalities=[]
    for state in blocks:
        if not np.array_equal(state['t'],t):raise ValueError('identical local time nodes required')
        cost=np.asarray(state['lp_cost'])
        if cost.shape!=(5*nt+2,) or np.any(cost!=0):
            raise ValueError('original zero-cost A,V,K,H,C and two-rating block required')
        ae,au=raw_matrix(state,'equality'),raw_matrix(state,'inequality')
        lower,upper=state['lp_lower_bound'],state['lp_upper_bound']
        if (ae.shape!=(len(state['lp_equality_rhs']),len(cost)) or
                au.shape!=(len(state['lp_inequality_rhs']),len(cost)) or
                np.shape(lower)!=cost.shape or np.shape(upper)!=cost.shape or
                not np.isfinite(ae.data).all() or not np.isfinite(au.data).all() or
                not np.isfinite(state['lp_equality_rhs']).all() or
                not np.isfinite(state['lp_inequality_rhs']).all() or
                np.isnan(lower).any() or np.isnan(upper).any() or np.any(lower>upper)):
            raise ValueError('finite original row coefficients and consistent bounds required')
        sizes.append(len(cost));equalities.append(ae);inequalities.append(au)
    offsets=np.r_[0,np.cumsum(sizes)];columns=int(offsets[-1])
    common=local.RawRows(columns)
    for j in range(1,nb):
        for i in range(nt):
            common.add([(offsets[j]+i,1),(i,-1)],0.,f'shared_phase:block:{j}:node:{i}')
    base_eq=block_diag(equalities,format='csr')
    ae=vstack([base_eq,common.matrix()],format='csr')
    au=block_diag(inequalities,format='csr')
    be=np.r_[np.concatenate([s['lp_equality_rhs'] for s in blocks]),common.rhs]
    bu=np.concatenate([s['lp_inequality_rhs'] for s in blocks])
    lower=np.concatenate([s['lp_lower_bound'] for s in blocks])
    upper=np.concatenate([s['lp_upper_bound'] for s in blocks])
    bounds=np.column_stack([lower,upper]);cost=np.zeros(columns)
    labels=lambda kind:[f'block:{j}:{label}' for j,s in enumerate(blocks)
                        for label in s['lp_'+kind+'_labels']]
    started=time.monotonic()
    result=linprog(cost,A_eq=ae,b_eq=be,A_ub=au,b_ub=bu,bounds=bounds,method='highs',
        options=dict(time_limit=float(deadline),primal_feasibility_tolerance=1e-9,
                     dual_feasibility_tolerance=1e-9,ipm_optimality_tolerance=1e-10))
    check=verify_candidate(cost,result.x,A_eq=ae,b_eq=be,A_ub=au,b_ub=bu,bounds=bounds)
    passed=bool(result.success and check.verified_feasible)
    summary=dict(success=passed,shared_phase_local_relaxation_passes=passed,
        ordinary_solver_success=bool(result.success),status=int(result.status),message=str(result.message),
        solver_method='highs',solver_objective='zero_feasibility',solver_deadline=float(deadline),
        solver_seconds=time.monotonic()-started,solver_iterations=int(result.nit),
        variables=columns,equalities=len(be),inequalities=len(bu),local_blocks=nb,
        time_nodes=nt,shared_phase_equalities=len(common.rhs),
        original_lp_rows_and_bounds_verified=bool(check.verified_feasible),
        common_phase_enforced=True,original_local_rows_preserved=True,
        added_density=0.,reserved_density_fraction=0.,
        inventory_minimization_requested=False,infeasibility_independently_certified=False,
        omitted_constraints=['explicit work-wave transport','wave population floors',
            'guide and new interface costs','fluid-to-cold donor-rate limits','photon donor-rate law'],
        full_source_construction_supplied=False,
        scope='favorable common-phase local net-bank-power necessity gate; original local stress, energy, capacity and supplied hot donor rows retained; wave transport, guide/interface costs and constitutive contacts remain separate',
        **finite_check_summary(check))
    arrays=dict(t=t,local_block_offsets=offsets,lp_cost=cost,lp_lower_bound=lower,
        lp_upper_bound=upper,lp_equality_rhs=be,lp_inequality_rhs=bu,
        lp_equality_labels=np.array(labels('equality')+common.labels),
        lp_inequality_labels=np.array(labels('inequality')),
        local_equality_rows=np.array(base_eq.shape[0]),shared_phase_rows=np.array(len(common.rhs)))
    for prefix,matrix in (('lp_equality',ae),('lp_inequality',au)):
        arrays.update({prefix+'_data':matrix.data,prefix+'_indices':matrix.indices,
                       prefix+'_indptr':matrix.indptr,prefix+'_shape':np.array(matrix.shape)})
    # Archive full physical inputs and each original individual witness,
    # including any finite candidate from a failed local solve.
    for j,state in enumerate(blocks):
        arrays.update({f'local{j}_'+key:value for key,value in state.items()})
    if check.candidate_finite:
        arrays['lp_x']=np.asarray(result.x)
        states=np.stack([result.x[offsets[j]:offsets[j]+5*nt].reshape(5,nt)
                         for j in range(nb)],axis=-1)
        for key,value in zip(('amplitude','balanced_radiation_inventory','thermal_inventory',
                              'receiver_hot_energy','receiver_cold_energy'),states):arrays[key]=value
        arrays['receiver_thermal_energy']=states[3]+states[4]
        arrays['hot_rated_capacity']=np.array([result.x[offsets[j]+5*nt] for j in range(nb)])
        arrays['cold_rated_capacity']=np.array([result.x[offsets[j]+5*nt+1] for j in range(nb)])
        arrays['shared_phase_residual']=states[0,:,1:]-states[0,:,:1]
        summary['shared_phase_residual']=float(abs(arrays['shared_phase_residual']).max())
        block_checks=[]
        for j,state in enumerate(blocks):
            block_check=verify_candidate(state['lp_cost'],result.x[offsets[j]:offsets[j+1]],
                A_eq=equalities[j],b_eq=state['lp_equality_rhs'],
                A_ub=inequalities[j],b_ub=state['lp_inequality_rhs'],
                bounds=np.column_stack([state['lp_lower_bound'],state['lp_upper_bound']]))
            block_checks.append(finite_check_summary(block_check))
        summary['joint_candidate_original_local_checks']=block_checks
    return summary,arrays


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--center',type=float,default=-1.975)
    parser.add_argument('--width',type=float,default=.0005)
    parser.add_argument('--temperature-floor',type=float,default=.01)
    parser.add_argument('--hot-donor-turnover',type=float,default=10.)
    parser.add_argument('--deadline',type=float,default=60.)
    parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--output-name',required=True)
    args=parser.parse_args()
    if (not np.isfinite([args.center,args.width,args.temperature_floor,args.hot_donor_turnover,args.deadline]).all()
            or args.width<=0 or args.temperature_floor<0 or args.hot_donor_turnover<=0
            or not 0<args.deadline<=60 or not 1<=args.workers<=2):
        parser.error('finite center, positive width/turnover, nonnegative floor, deadline in (0,60], and one or two workers required')
    edges=np.linspace(args.center-args.width/2,args.center+args.width/2,5)
    positions=(edges[:-1]+edges[1:])/2
    output=BASE/args.output_name
    if output.exists():raise RuntimeError('preserve completed shared-phase local evidence')
    source=BASE/'joint_refined_response/manifest.json';previous=json.loads(source.read_text())
    target=source.parent/'members_fraction0.99_states.npz'
    if sha256_file(target)!=previous['output_sha256'][target.name]:raise RuntimeError('changed registered backing target')
    hashes=local.verified_data_dependencies(source)
    files=[source,target,Path(__file__),
           ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_shared_phase_local.py',
           ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_local_bank_relaxation.py']
    for module in list(sys.modules.values()):
        filename=getattr(module,'__file__',None)
        if filename:
            path=Path(filename).resolve()
            if path.suffix=='.py' and path.is_relative_to(ROOT):files.append(path)
    hashes.update({str(path.relative_to(ROOT)):sha256_file(path) for path in files})
    output.mkdir()
    specs=[(float(x),args.temperature_floor,'highs',args.deadline,str(output),args.hot_donor_turnover,None)
           for x in positions]
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
        individual=list(pool.map(local.evaluate,specs))
    blocks=[]
    for case in individual:
        with np.load(output/(case['label']+'_states.npz'),allow_pickle=False) as saved:
            blocks.append(dict(saved))
    joint,arrays=solve_shared_phase(blocks,deadline=args.deadline)
    joint.update(center=args.center,width=args.width,positions=positions.tolist(),
        temperature_floor=args.temperature_floor,hot_donor_turnover=args.hot_donor_turnover,
        hot_endpoint_donor_bound_enforced=True,remaining_fluid_donor_bound_enforced=False,
        original_cold_rest_mass_retained=True,original_receiver_containment_retained=True,
        baseline_stress_and_power_credited_once=True,
        independent_local_all_pass=all(case['success'] for case in individual))
    arrays.update(x=positions,edges=edges)
    np.savez_compressed(output/'shared_phase_local_states.npz',**arrays)
    write_json(output/'summary.json',dict(individual_cases=individual,joint_case=joint))
    for relative,expected in hashes.items():
        if sha256_file(ROOT/relative)!=expected:raise RuntimeError('runtime input changed: '+relative)
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        workers=args.workers,input_sha256=hashes,historical_source=previous,
        output_sha256={path.name:sha256_file(path) for path in sorted(output.iterdir()) if path.is_file()}))
    print('shared phase: '+json.dumps({key:joint[key] for key in
        ('success','status','solver_seconds','maximum_feasibility_violation','independent_local_all_pass')}),flush=True)


if __name__=='__main__':main()
