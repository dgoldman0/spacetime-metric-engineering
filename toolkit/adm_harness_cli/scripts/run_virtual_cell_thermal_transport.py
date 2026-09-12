#!/usr/bin/env python3
"""Coherent paired phase, causal work waves, and counted thermal exchange."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess
import time

import numpy as np

from adm_harness.source_ledger import sha256_file
from adm_harness.virtual_cell_semigroup import solve_pair
from audit_joint_dense_work import DenseHistory
from audit_joint_support import bilinear
from run_poynting_delivery import BASE, ROOT, write_json


def evaluate(spec):
    (center, width, intervals, stride, reserve, output, deadline, solver_method,
     reallocate_fluid, reallocate_receiver, turnover, budget_only, split_receiver, warm_fluid,
     minimum_temperature, exact_midpoint)=spec
    output = Path(output)
    started = time.monotonic()
    path = BASE/'joint_refined_response/members_fraction0.99_states.npz'
    h = DenseHistory('routed_family', path)
    t = np.unique(np.r_[h.state['t'][::stride], h.state['t'][-1],
                        .047685546875, .0501953125, .072783203125, .5])
    edges = np.linspace(center-width/2, center+width/2, intervals+1)
    x = (edges[:-1]+edges[1:])/2
    tm = (t[:-1]+t[1:])/2
    nodes, mids = h.coefficients(t, x), h.coefficients(tm, x)
    target = np.array([h.energy(x).evaluate(t)[0]/nodes['D'],
                      h.pressure(t, x)[0], nodes['Q']/nodes['D']])
    budget = target.copy()
    budget[0] *= 1-reserve
    midpoint_budget=None
    if exact_midpoint:
        midpoint_budget=np.array([h.energy(x).evaluate(tm)[0]/mids['D'],
                                  h.pressure(tm,x)[0],mids['Q']/mids['D']])
        midpoint_budget[0]*=1-reserve
    extra={}
    reference=None
    receiver=None
    contact=None
    if reallocate_fluid:
        old=h.h.reference.h.state
        reference=bilinear(old['t'],old['x'],old['thermal'],t,x)[0]/nodes['D']
        number=np.interp(x,old['x'],old['number'])
        extra=dict(reference_fluid_density=reference,fluid_particle_number=number)
        if exact_midpoint:
            bm=bilinear(old['t'],old['x'],old['thermal'],tm,x)[0]/mids['D']
            midpoint_budget+=np.array([bm,bm/3,bm/3])
        if reallocate_receiver:
            ref=h.h.reference;state=h.h.state
            heat=bilinear(ref.t,ref.x,state['heat'],t,x)[0]
            capacity=np.interp(x,ref.x,state['heat_cap'])
            receiver=(heat,capacity)
            extra['receiver_fixed_containment_energy']=capacity/3
            if exact_midpoint:
                midpoint_budget[0]+=bilinear(ref.t,ref.x,state['heat'],tm,x)[0]/mids['D']
            if turnover is not None:
                from audit_virtual_cell_receiver_contact import integrated_loss
                loss,duration=integrated_loss(h,t,x,order=4)
                contact=(loss,duration,turnover)
    model = h.h.reference.h.model
    gm = [model.metric(float(now), x) for now in tm]
    ge = [model.metric(float(now), edges) for now in tm]
    wave = {sign: dict(faces=np.array([-g.beta+sign*g.alpha/g.b for g in ge]),
                       gain=np.array([g.alpha*g.k_l-sign*g.alpha_x/g.b for g in gm]))
            for sign in (-1, 1)}
    result = solve_pair(t, edges, budget, nodes, mids, wave, efficiency=.98,
        interface_sigma=1e-7, coherent_cells=True, return_heat=True,
        guide_drift=.5, wave_envelope=True, matched_pair=True,
        thermal_eos=1/3, thermal_reference_density=reference,
        receiver_reference=receiver,
        receiver_contact=contact, target_budget_only=budget_only,
        split_receiver=split_receiver,
        thermal_particle_number=number if warm_fluid or minimum_temperature is not None else None,
        maximize_thermal_floor=warm_fluid,minimum_thermal_floor=minimum_temperature,
        midpoint_credited_target=midpoint_budget,
        solver_threads=1, solver_method=solver_method, deadline=deadline)
    label = f'x{center:g}_w{width:g}_n{intervals}_s{stride}_thermal_joint'
    if reallocate_fluid: label+='_existing_fluid'
    if reallocate_receiver: label+='_receiver'
    if turnover is not None: label+=f'_rate{turnover:g}'
    if split_receiver: label+='_split'
    if warm_fluid: label+='_warm'
    if minimum_temperature is not None: label+=f'_floor{minimum_temperature:g}'
    if exact_midpoint: label+='_exactmid'
    summary = {key: value for key, value in result.items() if not isinstance(value, np.ndarray)}
    summary.update(label=label, input=str(path.relative_to(ROOT)), center=center,
        width=width, intervals=intervals, time_nodes=len(t), temporal_stride=stride,
        efficiency=.98, interface_sigma=1e-7, guide_drift=.5,
        reserved_density_fraction=reserve, common_phase_across_pair=True,
        midpoint_target_sampled_from_registered_history=exact_midpoint,
        distributed_thermal_reservoir_eos=1/3,
        existing_fluid_thermal_state_reallocated=reallocate_fluid,
        existing_fluid_original_power_duty_preserved=reallocate_fluid,
        existing_fluid_cold_particle_inventory_retained=reallocate_fluid,
        existing_receiver_heat_reallocated=reallocate_receiver,
        existing_receiver_rated_capacity_retained=reallocate_receiver,
        existing_receiver_containment_retained=reallocate_receiver,
        remaining_backing_original_power_duty_preserved=True,
        prepared_radiation_and_thermal_inventories_counted=True,
        endpoint_external_power_added=0.,
        scope='frozen-panel coherent phase and causal work-wave gate with counted bidirectional thermal exchange',
        independent_curved_geometry_replay_supplied=False,
        thermal_constitutive_opacity_and_force_supplied=False,
        additional_carrier_rest_mass_omitted=not reallocate_fluid,
        changed_fluid_contact_force_and_entropy_supplied=False,
        full_source_construction_supplied=False,
        elapsed_seconds=time.monotonic()-started)
    if result['success']:
        summary['target_budget_passes'] = bool(max(result['minimum_added_density'],
                                                   result['exact_added_density']) <= 2e-7)
        arrays = {key: value for key, value in result.items() if isinstance(value, np.ndarray)}
        if exact_midpoint:extra['midpoint_credited_target']=midpoint_budget
        np.savez_compressed(output/(label+'_states.npz'), t=t, x=x, edges=edges,
            target=target, budget_target=budget, radius=nodes['radius'], D=nodes['D'],
            lapse=nodes['lapse'], ell=nodes['ell'], v=nodes['v'], **extra, **arrays)
        if reallocate_fluid:
            delta=result['thermal_reservoir_rest']-reference
            summary.update(maximum_fluid_cooling_density=float(np.maximum(-delta,0).max()),
                maximum_fluid_heating_density=float(np.maximum(delta,0).max()),
                minimum_total_fluid_thermal_density=float(result['thermal_reservoir_rest'].min()))
    write_json(output/(label+'_summary.json'), summary)
    print(label+': '+json.dumps({key: summary[key] for key in
        ('success', 'status', 'minimum_added_density', 'exact_added_density',
         'target_budget_passes', 'elapsed_seconds') if key in summary}), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--centers', type=float, nargs='+', default=[-2., -1.975])
    parser.add_argument('--width', type=float, default=.0005)
    parser.add_argument('--intervals', type=int, default=12)
    parser.add_argument('--stride', type=int, default=4)
    parser.add_argument('--reserve', type=float, default=.002)
    parser.add_argument('--deadline', type=float, default=240.)
    parser.add_argument('--solver-method', choices=['highs-ds', 'highs-ipm'], default='highs-ds')
    parser.add_argument('--reallocate-fluid', action='store_true')
    parser.add_argument('--reallocate-receiver', action='store_true')
    parser.add_argument('--turnover',type=float)
    parser.add_argument('--target-budget-only',action='store_true')
    parser.add_argument('--split-receiver',action='store_true')
    parser.add_argument('--warm-fluid',action='store_true')
    parser.add_argument('--minimum-fluid-temperature',type=float)
    parser.add_argument('--exact-midpoint-target',action='store_true')
    parser.add_argument('--output-name', default='virtual_cell_thermal_transport_pilot')
    args = parser.parse_args()
    if not 1 <= args.workers <= 2 or args.intervals < 4 or args.intervals % 2:
        parser.error('one or two workers and an even spatial count >=4 required')
    if args.stride < 1 or args.width <= 0 or not 0 <= args.reserve < 1 or args.deadline <= 0:
        parser.error('positive scales and reserve in [0,1) required')
    if args.reallocate_receiver and not args.reallocate_fluid:
        parser.error('receiver exchange requires the reallocated pressure-link fluid')
    if args.turnover is not None and (not args.reallocate_receiver or args.turnover<=0):
        parser.error('positive donor turnover requires the receiver')
    if args.split_receiver and args.turnover is None:
        parser.error('split receiver requires a finite turnover comparison')
    if args.warm_fluid and (not args.target_budget_only or not args.reallocate_fluid):
        parser.error('warm fluid optimization requires a reallocated fluid and direct target budget')
    if args.minimum_fluid_temperature is not None and (
            args.warm_fluid or not args.reallocate_fluid or not args.target_budget_only
            or not np.isfinite(args.minimum_fluid_temperature) or args.minimum_fluid_temperature<0):
        parser.error('fixed nonnegative fluid temperature requires direct reallocated-fluid budget and no maximization')
    output = BASE/args.output_name
    if output.exists():
        raise RuntimeError('preserve completed thermal-transport evidence')
    source = BASE/'joint_refined_response/manifest.json'
    previous = json.loads(source.read_text())
    target = source.parent/'members_fraction0.99_states.npz'
    if sha256_file(target) != previous['output_sha256'][target.name]:
        raise RuntimeError('changed registered backing target')
    hashes = dict(previous['input_sha256'])
    files = [source, target, Path(__file__), Path(__file__).with_name('audit_joint_dense_work.py'),
        Path(__file__).with_name('audit_joint_support.py'),
        Path(__file__).with_name('audit_virtual_cell_receiver_contact.py'),
        ROOT/'toolkit/adm_harness_cli/adm_harness/virtual_cell_semigroup.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/virtual_cell_transport.py',
        ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_semigroup.py',
        ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_thermal_semigroup.py']
    for path in files:
        hashes[str(path.relative_to(ROOT))] = sha256_file(path)
    for relative, expected in hashes.items():
        if sha256_file(ROOT/relative) != expected:
            raise RuntimeError('changed input dependency: '+relative)
    output.mkdir()
    specs = [(center, args.width, args.intervals, args.stride, args.reserve,
              str(output), args.deadline, args.solver_method, args.reallocate_fluid,
              args.reallocate_receiver,args.turnover,args.target_budget_only,args.split_receiver,args.warm_fluid,
              args.minimum_fluid_temperature,args.exact_midpoint_target) for center in args.centers]
    with ProcessPoolExecutor(max_workers=min(args.workers, len(specs)),
                             mp_context=multiprocessing.get_context('spawn')) as pool:
        cases = list(pool.map(evaluate, specs))
    write_json(output/'summary.json', dict(cases=cases))
    write_json(output/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        workers=min(args.workers, len(specs)), input_sha256=hashes,
        output_sha256={path.name: sha256_file(path) for path in sorted(output.iterdir()) if path.is_file()}))


if __name__ == '__main__':
    main()
