#!/usr/bin/env python3
"""Circulation-aware endpoint donor comparisons for fixed bank histories."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess
import sys

import numpy as np

from adm_harness.source_ledger import sha256_file
from audit_joint_dense_work import DenseHistory
from audit_virtual_cell_ports import validate_controls
from audit_virtual_cell_thermal_replay import geometry
from run_poynting_delivery import BASE, ROOT, write_json

ENERGY_TOLERANCE = 2e-7
RELATIVE_TOLERANCE = 1e-8
POPULATION_TOLERANCE = 1e-10
ACTIVITY_TOLERANCE = 1e-10


def finite(value):
    return float(value) if np.isfinite(value) else None


def inventory_optimum_certified(parent):
    """An optimal zero objective certifies feasibility, not inventory cost."""
    return bool(parent.get('inventory_minimization_requested',True)
                and parent.get('inventory_minimization_success',False))


def circulation_interval(counter_energy, hot_heat, cold_heat, proper_duration,
                         minimum_fluid_energy, minimum_counter_energy, *,
                         fluid_turnover=10., photon_turnover=None):
    """Allow positive simultaneous hot-to-photon-to-cold circulation.

    All powers here are integrated proper-label energies. The endpoint
    comparison charges only the remaining fluid branch against fluid energy.
    Raw negative roundoff remains visible in the inputs and margins.
    """
    E,qh,qc,tau,U,c = np.broadcast_arrays(*[np.asarray(a,float) for a in
        (counter_energy,hot_heat,cold_heat,proper_duration,minimum_fluid_energy,minimum_counter_energy)])
    if (not all(np.isfinite(a).all() for a in (E,qh,qc,tau,U,c)) or np.any(tau<=0)
            or not np.isfinite(fluid_turnover) or fluid_turnover<=0
            or (photon_turnover is not None and (not np.isfinite(photon_turnover) or photon_turnover<=0))):
        raise ValueError('finite energies, positive durations and positive configured turnover required')
    fluid_allowance=fluid_turnover*tau*U
    lower=np.maximum.reduce([np.zeros_like(E),-E,qc-fluid_allowance])
    bank_upper=np.minimum(qc,qh-E)
    photon_allowance=None if photon_turnover is None else photon_turnover*tau*c
    upper=bank_upper if photon_allowance is None else np.minimum(bank_upper,photon_allowance)
    scale=np.maximum.reduce([abs(E),abs(qh),abs(qc),abs(fluid_allowance)])
    tolerance=ENERGY_TOLERANCE+RELATIVE_TOLERANCE*scale
    compatible=upper-lower>=-tolerance
    compatible_unbounded=bank_upper-lower>=-tolerance
    min_fluid=np.maximum(qc-qh+E,0.)
    with np.errstate(divide='ignore',invalid='ignore',over='ignore'):
        required=np.divide(lower,tau*c,out=np.where(lower>0,np.inf,0.),where=c>0)
        required_fluid=np.divide(min_fluid,tau*U,
            out=np.where(min_fluid>0,np.inf,0.),where=U>0)
    active=lower>ACTIVITY_TOLERANCE
    result=dict(absorption_lower=lower,absorption_bank_upper=bank_upper,absorption_upper=upper,
        interval_margin=upper-lower,unbounded_photon_interval_margin=bank_upper-lower,
        interval_tolerance=tolerance,compatible=compatible,compatible_unbounded_photon=compatible_unbounded,
        minimum_possible_fluid_to_cold=min_fluid,fluid_donor_allowance=fluid_allowance,
        minimum_fluid_donor_margin=fluid_allowance-min_fluid,
        minimum_required_fluid_turnover=required_fluid,
        required_photon_turnover=required,active_absorption_lower=active,
        active_empty_counter_donor=active&(c<=0),
        active_nonrepresentable_photon_turnover=active&(c>0)&~np.isfinite(required))
    if photon_allowance is not None:result['photon_donor_allowance']=photon_allowance
    # A complete fixed-history split is supplied only when every panel fits.
    # Its residuals retain any accepted numerical roundoff explicitly.
    if compatible.all():
        a=lower;e=E+a
        result.update(candidate_counter_to_cold=a,candidate_hot_to_counter=e,
            candidate_hot_to_fluid=qh-e,candidate_fluid_to_cold=qc-a)
    return result


def evaluate(spec):
    source,label,output,fluid_turnover,photon_turnover=spec
    source,output=Path(source),Path(output)
    path=source/(label+'_states.npz')
    meta=json.loads((source/(label+'_summary.json')).read_text())
    with np.load(path) as f:s={key:f[key] for key in f.files}
    if not meta.get('bank_counter_relaxation'):
        raise ValueError('bank-counter finite-pair controls are required')
    t,x=s['t'],s['x'];nt,nx=len(t),len(x)
    if (nt<2 or not nx or nx%2 or np.any(np.diff(t)<=0) or np.any(np.diff(x)<=0)
            or not np.isfinite(t).all() or not np.isfinite(x).all()):
        raise ValueError('ordered paired spatial and temporal grids required')
    keys=('D','ell','radius','thermal_inventory','receiver_hot_energy','receiver_cold_energy',
          'balanced_radiation_inventory','absorption_rest','recovery_rest')
    for key in keys:
        if s[key].shape!=(nt,nx) or not np.isfinite(s[key]).all():
            raise ValueError('finite matching node history required: '+key)
    D,R,ell=s['D'],s['radius'],s['ell']
    if np.any(D<=0) or np.any(R<=0) or np.any(ell<=0):
        raise ValueError('positive registered node geometry required')
    if not np.allclose(D,ell*R**2,rtol=1e-12,atol=1e-12):
        raise ValueError('stored node volume differs from ell R squared')
    K,H,C,V=[s[key] for key in ('thermal_inventory','receiver_hot_energy','receiver_cold_energy','balanced_radiation_inventory')]
    Z=H+C;U=K/D**(1/3);W=V/(ell*R)**2
    counter=W-s['absorption_rest']-s['recovery_rest']
    direction=np.r_[-np.ones(nx//2),np.ones(nx//2)]
    current=-direction*(s['absorption_rest']-s['recovery_rest'])
    counter_energy=D*counter
    tau=s['receiver_contact_proper_duration'];loss=s['receiver_converter_loss_panel']
    for value in (tau,loss):
        if value.shape!=(nt-1,nx) or not np.isfinite(value).all():
            raise ValueError('finite matching panel duration and loss required')
    if np.any(tau<=0) or np.any(loss<0):
        raise ValueError('positive proper durations and nonnegative converter loss required')
    qh=loss-np.diff(H,axis=0);qc=np.diff(C,axis=0)
    h=DenseHistory('routed_family',ROOT/meta['input'])
    g=geometry(h.h.reference.h.model,(t[:-1]+t[1:])/2,x)
    psi=g['M']/g['D']**(4/3);chi=g['M']/g['D'];phi=g['ell']**2
    F=s['thermal_reference_power_panel']+s['receiver_reference_power_panel']
    fluid=psi*np.diff(K,axis=0)/chi
    support=F/chi-loss
    E=F/chi-fluid-np.diff(Z,axis=0)
    X=fluid-support
    energy=np.diff(V,axis=0)+phi*np.diff(s['amplitude'],axis=0)+psi*np.diff(K,axis=0)+chi*np.diff(Z,axis=0)-F
    result=circulation_interval(E,qh,qc,tau,np.minimum(U[:-1],U[1:]),
        np.minimum(counter_energy[:-1],counter_energy[1:]),fluid_turnover=fluid_turnover,
        photon_turnover=photon_turnover)
    archive_errors=dict(counter_panel=float(abs(E-s['counter_panel_energy']).max()),
        counter_density=float(abs(counter-s['counterstream_rest']).max()),
        hot_heat=float(abs(qh-s['receiver_hot_contact_panel_heat']).max()),
        cold_heat=float(abs(qc-s['receiver_cold_contact_panel_heat']).max()),
        receiver_total=float(abs(Z-s['receiver_thermal_energy']).max()),
        original_support=float(abs(support-s['retained_support_to_fluid_panel_energy']).max()),
        fluid_power=float(abs(fluid-s['actual_fluid_power_panel_energy']).max()))
    identities=dict(weighted_energy=float(abs(energy).max()),
        original_power=float(abs(X-(qh-qc-E)).max()),
        minimum_fluid=float(abs(np.maximum(-X,0)-result['minimum_possible_fluid_to_cold']).max()),
        exported_split=float(abs(s['bank_hot_to_counter_panel_heat']-s['bank_counter_to_cold_panel_heat']-E).max()))
    capacity=s['receiver_rated_capacity']
    capacity_margin=capacity-H.max(axis=0)-C.max(axis=0)
    hot_turnover=meta.get('receiver_donor_turnover')
    if hot_turnover is None or not np.isfinite(hot_turnover) or hot_turnover<=0:
        raise ValueError('positive archived hot-donor turnover required')
    hot_margin=hot_turnover*tau[None,:,:]*np.array([H[:-1],H[1:]])-qh
    state_negative=max(0.,float(-K.min()),float(-H.min()),float(-C.min()),float(-V.min()))
    direction_violation=max(0.,float((abs(current)-counter).max()))
    raw_routing=max(0.,float((E-qh).max()),float((-E-qc).max()),float(-qh.min()),float(-qc.min()))
    parent_ok=bool(meta.get('success') and meta.get('target_budget_passes')
        and (not meta.get('native_feasible_interior_retention') or meta.get('verified_feasible')))
    state_ok=bool(max(archive_errors.values())<=ENERGY_TOLERANCE and max(identities.values())<=ENERGY_TOLERANCE
        and state_negative<=ENERGY_TOLERANCE and direction_violation<=POPULATION_TOLERANCE
        and raw_routing<=ENERGY_TOLERANCE and hot_margin.min()>=-ENERGY_TOLERANCE
        and capacity_margin.min()>=-ENERGY_TOLERANCE)
    unbounded_ok=bool(result['compatible_unbounded_photon'].all())
    configured_ok=bool(result['compatible'].all())
    finite_rate_possible=bool(not result['active_empty_counter_donor'].any()
                             and not result['active_nonrepresentable_photon_turnover'].any())
    # A candidate is an auditable whole-case split, conditional on its parent
    # state and all configured donor comparisons as well as the interval.
    candidate_ok=bool(parent_ok and state_ok and configured_ok and finite_rate_possible)
    if not candidate_ok:
        for key in list(result):
            if key.startswith('candidate_'):del result[key]

    def witness(i,j):
        return dict(time_start=float(t[i]),time_end=float(t[i+1]),x=float(x[j]),
            counter_energy=float(E[i,j]),hot_heat=float(qh[i,j]),cold_heat=float(qc[i,j]),
            proper_duration=float(tau[i,j]),fluid_energy_endpoints=U[i:i+2,j].tolist(),
            counter_density_endpoints=counter[i:i+2,j].tolist(),
            counter_label_energy_endpoints=counter_energy[i:i+2,j].tolist(),
            current_endpoints=current[i:i+2,j].tolist(),
            absorption_lower=float(result['absorption_lower'][i,j]),
            bank_upper=float(result['absorption_bank_upper'][i,j]),
            configured_upper=float(result['absorption_upper'][i,j]),
            interval_margin=float(result['interval_margin'][i,j]),
            minimum_fluid_heat=float(result['minimum_possible_fluid_to_cold'][i,j]),
            fluid_donor_allowance=float(result['fluid_donor_allowance'][i,j]),
            minimum_required_fluid_turnover=finite(result['minimum_required_fluid_turnover'][i,j]),
            required_photon_turnover=finite(result['required_photon_turnover'][i,j]))

    active=result['active_absorption_lower'];rate=result['required_photon_turnover']
    finite_active=active&np.isfinite(rate)
    fluid_rate=result['minimum_required_fluid_turnover']
    finite_fluid=(result['minimum_possible_fluid_to_cold']>ACTIVITY_TOLERANCE)&np.isfinite(fluid_rate)
    worst_rate=np.where(active,rate,-1.)
    summary=dict(label=label,input=str(path.relative_to(ROOT)),time_nodes=nt,spatial_samples=nx,
        parent_primal_and_target_pass=parent_ok,parent_solver_status=meta.get('status'),
        parent_inventory_optimality_certified=inventory_optimum_certified(meta),
        independent_state_and_power_checks_pass=state_ok,
        fluid_turnover=float(fluid_turnover),photon_turnover=photon_turnover,hot_turnover=float(hot_turnover),
        unbounded_photon_rate_interval_passes=unbounded_ok,
        configured_donor_interval_passes=configured_ok,
        finite_active_photon_donor_possible=finite_rate_possible,
        fixed_history_bank_donor_comparison_passes=candidate_ok,
        candidate_branch_split_supplied=candidate_ok,
        failing_intervals_without_photon_rate=int((~result['compatible_unbounded_photon']).sum()),
        failing_intervals_with_configured_rate=int((~result['compatible']).sum()),
        minimum_unbounded_photon_interval_margin=float(result['unbounded_photon_interval_margin'].min()),
        minimum_configured_interval_margin=float(result['interval_margin'].min()),
        minimum_fluid_donor_margin=float(result['minimum_fluid_donor_margin'].min()),
        minimum_hot_donor_margin=float(hot_margin.min()),minimum_capacity_margin=float(capacity_margin.min()),
        minimum_counter_density=float(counter.min()),maximum_directional_violation=direction_violation,
        maximum_negative_stored_inventory=state_negative,raw_net_routing_violation=raw_routing,
        active_required_absorption_samples=int(active.sum()),
        active_empty_counter_donor_samples=int(result['active_empty_counter_donor'].sum()),
        active_nonrepresentable_photon_rate_samples=int(result['active_nonrepresentable_photon_turnover'].sum()),
        maximum_required_finite_photon_turnover=float(rate[finite_active].max()) if finite_active.any() else None,
        maximum_minimum_required_finite_fluid_turnover=float(fluid_rate[finite_fluid].max()) if finite_fluid.any() else None,
        archive_reconstruction_errors=archive_errors,power_identity_residuals=identities,
        worst_interval_witness=witness(*np.unravel_index(np.argmin(result['interval_margin']),E.shape)),
        worst_fluid_donor_witness=witness(*np.unravel_index(np.argmin(result['minimum_fluid_donor_margin']),E.shape)),
        worst_photon_rate_witness=witness(*np.unravel_index(np.argmax(worst_rate),E.shape)) if active.any() else None,
        energy_tolerance=ENERGY_TOLERANCE,relative_tolerance=RELATIVE_TOLERANCE,
        population_tolerance=POPULATION_TOLERANCE,activity_tolerance=ACTIVITY_TOLERANCE,
        scope='fixed frozen-panel histories with positive simultaneous photon circulation; donor comparisons use both endpoint inventories and stored proper durations',
        optimal_circulation_for_all_physics_constructed=False,temperature_order_supplied=False,
        opacity_supplied=False,force_supplied=False,entropy_closure_supplied=False,
        full_source_construction_supplied=False,inventories_or_original_power_duties_changed=False,
        photon_turnover_condition='required rate uses the least absorption compatible with fluid and bank duties; finite endpoint comparison, without a continuum maximum-rate claim')
    if candidate_ok:
        a,e,hf,fc=[result[key] for key in ('candidate_counter_to_cold','candidate_hot_to_counter',
                                         'candidate_hot_to_fluid','candidate_fluid_to_cold')]
        summary.update(candidate_power_identity_residual=float(abs(e-a-E).max()),
            candidate_hot_identity_residual=float(abs(e+hf-qh).max()),
            candidate_cold_identity_residual=float(abs(a+fc-qc).max()),
            candidate_fluid_identity_residual=float(abs(fluid-support-hf+fc).max()),
            candidate_minimum_branch_heat=float(min(a.min(),e.min(),hf.min(),fc.min())))
    arrays=dict(t=t,x=x,D=D,radius=R,ell=ell,proper_duration=tau,thermal_inventory=K,
        amplitude=s['amplitude'],phase_weight=phi,thermal_exchange_weight=psi,receiver_weight=chi,
        fluid_energy=U,receiver_hot_energy=H,receiver_cold_energy=C,
        original_capacity=capacity,capacity_margin=capacity_margin,hot_endpoint_donor_margin=hot_margin,
        balanced_radiation_inventory=V,balanced_radiation_density=W,
        explicit_incident_density=s['absorption_rest'],explicit_return_density=s['recovery_rest'],
        counter_density=counter,counter_current=current,counter_label_energy=counter_energy,
        counter_panel_energy=E,converter_loss=loss,original_hot_heat=qh,original_cold_heat=qc,
        exported_hot_to_counter=s['bank_hot_to_counter_panel_heat'],
        exported_counter_to_cold=s['bank_counter_to_cold_panel_heat'],
        exported_hot_to_fluid=s['bank_hot_to_fluid_panel_heat'],
        exported_fluid_to_cold=s['bank_fluid_to_cold_panel_heat'],
        thermal_reference_power_panel=s['thermal_reference_power_panel'],
        receiver_reference_power_panel=s['receiver_reference_power_panel'],
        original_reference_power_panel=F,actual_fluid_panel_energy=fluid,
        retained_support_panel_energy=support,minimum_fluid_from_original_power=np.maximum(-X,0.),
        weighted_energy_residual=energy,**result)
    np.savez_compressed(output/(label+'_donors.npz'),**arrays)
    write_json(output/(label+'_summary.json'),summary)
    print(label+': '+json.dumps({key:summary[key] for key in
        ('unbounded_photon_rate_interval_passes','configured_donor_interval_passes','minimum_fluid_donor_margin')}),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True);parser.add_argument('--output-name',required=True)
    parser.add_argument('--labels',nargs='+');parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--fluid-turnover',type=float,default=10.)
    parser.add_argument('--photon-turnover',type=float)
    args=parser.parse_args()
    if (not 1<=args.workers<=2 or not np.isfinite(args.fluid_turnover) or args.fluid_turnover<=0
            or (args.photon_turnover is not None and (not np.isfinite(args.photon_turnover) or args.photon_turnover<=0))):
        parser.error('positive configured turnover and one or two workers required')
    source,output=BASE/args.source,BASE/args.output_name
    if output.exists():raise RuntimeError('preserve completed bank-donor audit')
    labels=args.labels or [p.stem.removesuffix('_states') for p in sorted(source.glob('*_states.npz'))]
    if not labels:raise ValueError('completed finite-pair states required')
    hashes,historical=validate_controls(source,labels)
    runtime=[Path(__file__),ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_bank_donors.py']
    for module in list(sys.modules.values()):
        filename=getattr(module,'__file__',None)
        if filename:
            path=Path(filename).resolve()
            if path.suffix=='.py' and path.is_relative_to(ROOT):runtime.append(path)
    hashes.update({str(path.relative_to(ROOT)):sha256_file(path) for path in runtime})
    output.mkdir()
    specs=[(source,label,output,args.fluid_turnover,args.photon_turnover) for label in labels]
    with ProcessPoolExecutor(max_workers=min(args.workers,len(specs)),
            mp_context=multiprocessing.get_context('spawn')) as pool:
        cases=list(pool.map(evaluate,specs))
    for relative,expected in hashes.items():
        if sha256_file(ROOT/relative)!=expected:raise RuntimeError('input changed during donor audit: '+relative)
    write_json(output/'summary.json',dict(cases=cases))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        workers=min(args.workers,len(specs)),input_sha256=hashes,historical_source=historical,
        output_sha256={p.name:sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__=='__main__':main()
