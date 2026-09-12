#!/usr/bin/env python3
"""Audit fixed-inventory hot/cold routing of complementary-photon power.

Existing hot withdrawal and cold intake are divided between the fluid and
the complementary photons. Their stored histories, ratings, selected bath
coefficients and original support power remain fixed.
"""
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
from audit_virtual_cell_guided_contact import (guided_interval, finite_or_none,
    POWER_TOLERANCE, POPULATION_TOLERANCE)
from audit_virtual_cell_thermal_replay import geometry, linear_history
from run_poynting_delivery import BASE, ROOT, write_json

TRAFFIC_ABSOLUTE_TOLERANCE = 1e-9
TRAFFIC_RELATIVE_TOLERANCE = 1e-8


def routing_traffic(power, hot_withdrawal, cold_intake, *, extra_cycle=0.):
    """Proper-label powers; additional simultaneous traffic can only cost more."""
    power, hot_withdrawal, cold_intake, cycle = np.broadcast_arrays(
        *[np.asarray(a, float) for a in (power, hot_withdrawal, cold_intake, extra_cycle)])
    if (not all(np.isfinite(a).all() for a in (power, hot_withdrawal, cold_intake, cycle))
            or np.any(hot_withdrawal < 0) or np.any(cold_intake < 0) or np.any(cycle < 0)):
        raise ValueError('finite power and nonnegative original heat traffic/cycle required')
    emission, absorption = np.maximum(power, 0.)+cycle, np.maximum(-power, 0.)+cycle
    hot_remaining, cold_remaining = hot_withdrawal-emission, cold_intake-absorption
    hot_scale = np.maximum(hot_withdrawal, emission)
    cold_scale = np.maximum(cold_intake, absorption)
    hot_tolerance = TRAFFIC_ABSOLUTE_TOLERANCE+TRAFFIC_RELATIVE_TOLERANCE*hot_scale
    cold_tolerance = TRAFFIC_ABSOLUTE_TOLERANCE+TRAFFIC_RELATIVE_TOLERANCE*cold_scale
    return dict(emission=emission, absorption=absorption,
        redirected_hot_to_fluid=hot_remaining, redirected_fluid_to_cold=cold_remaining,
        hot_margin=hot_remaining, cold_margin=cold_remaining,
        relative_hot_margin=hot_remaining/np.maximum(hot_scale, TRAFFIC_ABSOLUTE_TOLERANCE),
        relative_cold_margin=cold_remaining/np.maximum(cold_scale, TRAFFIC_ABSOLUTE_TOLERANCE),
        hot_tolerance=hot_tolerance, cold_tolerance=cold_tolerance,
        compatible=(hot_remaining >= -hot_tolerance) & (cold_remaining >= -cold_tolerance))


def mixed_bank_interval(power_density, counter, radius, hot_temperature, cold_temperature):
    """Use the chosen hot bath for emission and chosen cold bath for absorption."""
    selected = np.where(np.asarray(power_density) >= 0, hot_temperature, cold_temperature)
    return guided_interval(power_density, counter, radius, selected)


def counter_donor_rate(absorption, donor_inventory, active_absorption):
    """Required proper turnover; positive tiny populations retain their sign.

    A nonrepresentable rate is unresolved numerically. Empty active donors
    violate the finite-rate condition; neither case receives a combined pass.
    """
    absorption, donor_inventory, active_absorption = np.broadcast_arrays(
        np.asarray(absorption, float), np.asarray(donor_inventory, float),
        np.asarray(active_absorption, bool))
    if (not np.isfinite(absorption).all() or not np.isfinite(donor_inventory).all()
            or np.any(absorption < 0)):
        raise ValueError('finite nonnegative absorption and finite inventory required')
    with np.errstate(over='ignore', divide='ignore', invalid='ignore'):
        rate = np.divide(absorption, donor_inventory,
            out=np.where(absorption > 0, np.inf, 0.), where=donor_inventory > 0)
    empty = active_absorption & (donor_inventory <= 0)
    unresolved = active_absorption & (donor_inventory > 0) & ~np.isfinite(rate)
    return rate, empty, unresolved


def verify_archive(folder):
    """Verify all parent data products and recorded data dependencies in place.

    Historical Python dependencies remain identified by their parent manifest;
    this audit separately hashes every currently imported runtime module.
    """
    manifest_path = folder/'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    checked = {str(manifest_path.relative_to(ROOT)): sha256_file(manifest_path)}
    for name, expected in manifest['output_sha256'].items():
        path = folder/name
        if sha256_file(path) != expected:
            raise RuntimeError('changed parent product: '+str(path))
        checked[str(path.relative_to(ROOT))] = expected
    for relative, expected in manifest.get('input_sha256', {}).items():
        path = ROOT/relative
        if path.suffix == '.py':
            continue
        if sha256_file(path) != expected:
            raise RuntimeError('changed parent data dependency: '+relative)
        checked[relative] = expected
    return manifest, checked


def evaluate(spec):
    replay_folder, guided_folder, temperature_folder, label, output = spec
    replay_folder, guided_folder, temperature_folder, output = map(Path,
        (replay_folder, guided_folder, temperature_folder, output))
    replay_path = replay_folder/(label+'_states.npz')
    replay_meta = json.loads((replay_folder/(label+'_summary.json')).read_text())
    guided_meta = json.loads((guided_folder/(label+'_summary.json')).read_text())
    temperature_meta = json.loads((temperature_folder/(label+'_summary.json')).read_text())
    relative_replay = str(replay_path.relative_to(ROOT))
    if guided_meta['input'] != relative_replay or temperature_meta['input'] != relative_replay:
        raise ValueError('both derived audits must refer to the selected replay state')
    with np.load(replay_path) as f:
        s = {key: f[key] for key in f.files}
    with np.load(guided_folder/(label+'_contact.npz')) as f:
        guided = {key: f[key] for key in f.files}
    with np.load(temperature_folder/(label+'_contact.npz')) as f:
        bath = {key: f[key] for key in f.files}
    t, x = guided['t'], guided['x']
    if (not np.array_equal(x, s['x']) or not np.array_equal(x, bath['x'])
            or not np.array_equal(t, (s['t'][:-1]+s['t'][1:])/2)
            or not np.array_equal(bath['t'], s['t'])):
        raise ValueError('replay, power and bath audits must share exactly corresponding grids')
    h = DenseHistory('routed_family', ROOT/replay_meta['input'])
    g = geometry(h.h.reference.h.model, t, x)
    if not np.allclose(g['radius'], guided['radius'], rtol=2e-13, atol=0.):
        raise ValueError('guided archive differs from the registered midpoint geometry')
    control_t = s['contact_control_time']
    if (not np.array_equal(s['contact_control_position'], x) or np.any(np.diff(control_t) <= 0)
            or t[0] < control_t[0] or t[-1] > control_t[-1]):
        raise ValueError('saved reconstructed contact rates must cover the exact replay grid')
    owner = np.clip(np.searchsorted(control_t, t, side='right')-1, 0, len(control_t)-2)
    qh, qc = [s[key][owner] for key in
        ('applied_hot_parent_proper_rate', 'applied_cold_parent_proper_rate')]
    if qh.shape != (len(t), len(x)) or qc.shape != qh.shape:
        raise ValueError('matching saved hot/cold proper contact rates required')
    power_density = guided['required_counter_power']
    counter, current = guided['counter_density'], guided['counter_current']
    p = g['D']*power_density
    traffic = routing_traffic(p, qh, qc)
    f = g['D']*guided['fluid_power']
    fixed = g['D']*guided['retained_support_to_fluid_power']
    H = linear_history(s['t'], s['receiver_hot_energy'], t)[0]
    C = linear_history(s['t'], s['receiver_cold_energy'], t)[0]
    if not (np.allclose(H, bath['hot_energy'], rtol=1e-13, atol=1e-13)
            and np.allclose(C, bath['cold_energy'], rtol=1e-13, atol=1e-13)):
        raise ValueError('selected bath temperatures belong to different receiver histories')
    original_balance = f-(qh-qc+fixed-p)
    redirected_balance = f-(traffic['redirected_hot_to_fluid']-traffic['redirected_fluid_to_cold']+fixed)
    balance_scale = abs(f)+qh+qc+abs(fixed)+abs(p)
    balance_tolerance = TRAFFIC_ABSOLUTE_TOLERANCE+TRAFFIC_RELATIVE_TOLERANCE*balance_scale
    balance_pass = bool(np.all(abs(original_balance) <= balance_tolerance)
                        and np.all(abs(redirected_balance) <= balance_tolerance))
    ah, ac = temperature_meta.get('selected_hot_coefficient'), temperature_meta.get('selected_cold_coefficient')
    selected_coefficients_valid = (ah is not None and ac is not None
        and np.isfinite(ah) and np.isfinite(ac) and ah > 0 and ac > 0)
    energy_negative = max(0., float(-H.min()), float(-C.min()))
    bank_positive = energy_negative <= POPULATION_TOLERANCE
    # Match the explicitly declared roundoff treatment of the selected bath
    # audit while retaining the complete raw H,C arrays in the new product.
    hot_temperature = (ah*np.maximum(H, 0.))**.25 if selected_coefficients_valid else np.full_like(H, np.nan)
    cold_temperature = (ac*np.maximum(C, 0.))**.25 if selected_coefficients_valid else np.full_like(C, np.nan)
    theta_f = guided['fluid_temperature']
    temperature_result = None
    lower = upper = None
    mixed_ok = False
    remaining_temperature_ok = False
    if selected_coefficients_valid:
        temperature_result = mixed_bank_interval(power_density, counter, g['radius'],
                                                  hot_temperature, cold_temperature)
        lower, upper = float(temperature_result['lower'].max()), float(temperature_result['upper'].min())
        mixed_ok = bool(temperature_result['compatible'].all() and lower < upper and upper > 0 and np.isfinite(lower))
        remaining_temperature_ok = bool(np.all((traffic['redirected_hot_to_fluid'] <= traffic['hot_tolerance'])
            | (hot_temperature > theta_f)) and np.all((traffic['redirected_fluid_to_cold'] <= traffic['cold_tolerance'])
            | (theta_f > cold_temperature)))
    absorption = traffic['absorption']
    donor_inventory = g['D']*counter
    donor_rate, empty_absorption, unresolved_donor = counter_donor_rate(
        absorption, donor_inventory, power_density < -POWER_TOLERANCE)
    directional_violation = max(0., float((abs(current)-counter).max()))
    traffic_ok = bool(traffic['compatible'].all())
    parent_pass = bool(replay_meta.get('success') and replay_meta.get('full_sampled_gate_passes')
        and guided_meta.get('parent_full_sampled_gate_passes')
        and temperature_meta.get('common_pair_temperature_coefficients_possible'))

    def witness(index):
        i, j = index
        return dict(time=float(t[i]), x=float(x[j]), counter_power_per_label=float(p[i,j]),
            counter_power_density=float(power_density[i,j]), original_hot_withdrawal=float(qh[i,j]),
            original_cold_intake=float(qc[i,j]), emission=float(traffic['emission'][i,j]),
            absorption=float(absorption[i,j]), hot_margin=float(traffic['hot_margin'][i,j]),
            cold_margin=float(traffic['cold_margin'][i,j]),
            relative_hot_margin=float(traffic['relative_hot_margin'][i,j]),
            relative_cold_margin=float(traffic['relative_cold_margin'][i,j]),
            counter_density=float(counter[i,j]), counter_current=float(current[i,j]),
            fluid_temperature=float(theta_f[i,j]), hot_temperature=finite_or_none(hot_temperature[i,j]),
            cold_temperature=finite_or_none(cold_temperature[i,j]),
            required_counter_donor_rate=finite_or_none(donor_rate[i,j]))

    positions = []
    if temperature_result is not None:
        for j in range(len(x)):
            lo, hi = int(temperature_result['lower_witness'][j]), int(temperature_result['upper_witness'][j])
            positions.append(dict(x=float(x[j]), traffic_passes=bool(traffic['compatible'][:,j].all()),
                a2_lower=finite_or_none(temperature_result['lower'][j]), a2_upper=finite_or_none(temperature_result['upper'][j]),
                upper_unbounded=not np.isfinite(temperature_result['upper'][j]),
                temperature_interval_passes=bool(temperature_result['compatible'][j]),
                lower_witness=witness((lo,j)) if lo>=0 else None,
                upper_witness=witness((hi,j)) if hi>=0 else None))
    combined = bool(parent_pass and traffic_ok and mixed_ok and bank_positive and balance_pass
        and remaining_temperature_ok and not empty_absorption.any() and not unresolved_donor.any()
        and directional_violation <= POPULATION_TOLERANCE)
    summary = dict(label=label, replay_input=relative_replay,
        guided_input=str((guided_folder/(label+'_contact.npz')).relative_to(ROOT)),
        split_temperature_input=str((temperature_folder/(label+'_contact.npz')).relative_to(ROOT)),
        parent_full_sampled_gate_passes=bool(replay_meta.get('full_sampled_gate_passes')),
        guided_parent_full_sampled_gate_passes=bool(guided_meta.get('parent_full_sampled_gate_passes')),
        original_fluid_only_guided_interval_passes=bool(guided_meta.get('conditional_pair_power_interval_passes')),
        split_parent_temperature_coefficients_possible=bool(temperature_meta.get('common_pair_temperature_coefficients_possible')),
        selected_hot_coefficient=ah, selected_cold_coefficient=ac,
        traffic_gate_passes=traffic_ok, mixed_bank_temperature_interval_passes=mixed_ok,
        remaining_fluid_temperature_order_passes=remaining_temperature_ok,
        fixed_inventory_bank_routing_passes=combined,
        a2_lower=finite_or_none(lower) if lower is not None else None,
        a2_upper=finite_or_none(upper) if upper is not None else None,
        upper_unbounded=upper is not None and not np.isfinite(upper),
        minimum_hot_margin=float(traffic['hot_margin'].min()), minimum_cold_margin=float(traffic['cold_margin'].min()),
        minimum_relative_hot_margin=float(traffic['relative_hot_margin'].min()),
        minimum_relative_cold_margin=float(traffic['relative_cold_margin'].min()),
        maximum_hot_traffic_shortfall=max(0.,float(-traffic['hot_margin'].min())),
        maximum_cold_traffic_shortfall=max(0.,float(-traffic['cold_margin'].min())),
        worst_hot_traffic_witness=witness(np.unravel_index(np.argmin(traffic['hot_margin']),p.shape)),
        worst_cold_traffic_witness=witness(np.unravel_index(np.argmin(traffic['cold_margin']),p.shape)),
        original_hot_branch_minimum=float(qh.min()), original_cold_branch_minimum=float(qc.min()),
        redirected_hot_branch_minimum=float(traffic['redirected_hot_to_fluid'].min()),
        redirected_cold_branch_minimum=float(traffic['redirected_fluid_to_cold'].min()),
        original_power_identity_residual=float(abs(original_balance).max()),
        redirected_power_identity_residual=float(abs(redirected_balance).max()),
        counter_power_identity_residual=float(abs(traffic['emission']-absorption-p).max()),
        hot_total_withdrawal_identity=float(abs(traffic['redirected_hot_to_fluid']+traffic['emission']-qh).max()),
        cold_total_intake_identity=float(abs(traffic['redirected_fluid_to_cold']+absorption-qc).max()),
        maximum_finite_required_counter_donor_rate=float(np.max(donor_rate[np.isfinite(donor_rate)],initial=0.)),
        nonfinite_counter_donor_rate_samples=int((~np.isfinite(donor_rate)).sum()),
        active_empty_counter_absorption_samples=int(empty_absorption.sum()),
        active_nonrepresentable_counter_donor_rate_samples=int(unresolved_donor.sum()),
        active_finite_counter_donor_rate_passes=bool(not empty_absorption.any() and not unresolved_donor.any()),
        worst_counter_donor_witness=witness(np.unravel_index(np.argmax(donor_rate),p.shape)),
        maximum_directional_population_violation=directional_violation,
        maximum_negative_bank_energy=energy_negative,
        bank_temperature_negative_roundoff_mapped_to_zero=bool(np.any(H<0) or np.any(C<0)),
        absolute_traffic_tolerance=TRAFFIC_ABSOLUTE_TOLERANCE,
        relative_traffic_tolerance=TRAFFIC_RELATIVE_TOLERANCE,
        power_density_activity_tolerance=POWER_TOLERANCE, population_tolerance=POPULATION_TOLERANCE,
        inventories_and_selected_bath_coefficients_changed=False,
        retained_support_power_range=[float(fixed.min()),float(fixed.max())],
        scope='sampled fixed-inventory traffic and fixed 1D channel power-ordering conditions',
        midpoint_method='exact registered D,R; saved proper parent heat rates; linearly interpolated replay H,C and inherited guided photon moments',
        physical_opacity_supplied=False, momentum_closure_supplied=False,
        complete_entropy_closure_supplied=False, full_source_construction_supplied=False, positions=positions)
    write_json(output/(label+'_summary.json'),summary)
    arrays = dict(t=t,x=x,D=g['D'],radius=g['radius'],counter_density=counter,counter_current=current,
        counter_power_density=power_density,counter_power_per_label=p,
        original_hot_to_fluid=qh,original_fluid_to_cold=qc,
        original_fluid_power_per_label=f,retained_support_power_per_label=fixed,
        hot_energy=H,cold_energy=C,hot_temperature=hot_temperature,cold_temperature=cold_temperature,
        fluid_temperature=theta_f,required_counter_donor_rate=donor_rate,
        active_empty_counter_absorption=empty_absorption,
        active_nonrepresentable_counter_donor_rate=unresolved_donor,
        original_power_balance=original_balance,redirected_power_balance=redirected_balance,**traffic)
    if temperature_result is not None:
        arrays.update({'temperature_'+key:value for key,value in temperature_result.items()})
    np.savez_compressed(output/(label+'_routing.npz'),**arrays)
    print(label+': '+json.dumps({key:summary[key] for key in
        ('traffic_gate_passes','mixed_bank_temperature_interval_passes','fixed_inventory_bank_routing_passes')}),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay',required=True);parser.add_argument('--guided',required=True)
    parser.add_argument('--split-temperature',required=True);parser.add_argument('--output-name',required=True)
    parser.add_argument('--workers',type=int,default=2);parser.add_argument('--labels',nargs='+')
    args=parser.parse_args()
    if not 1<=args.workers<=2:parser.error('one or two workers required')
    folders=[BASE/name for name in (args.replay,args.guided,args.split_temperature)]
    output=BASE/args.output_name
    if output.exists():raise RuntimeError('preserve completed bank-routing audit')
    hashes={};manifests=[]
    for folder in folders:
        manifest,checked=verify_archive(folder);manifests.append(manifest)
        for relative,value in checked.items():
            if relative in hashes and hashes[relative]!=value:
                raise RuntimeError('parents disagree about input identity: '+relative)
            hashes[relative]=value
    labels=args.labels or [p.stem.removesuffix('_states') for p in sorted(folders[0].glob('*_states.npz'))]
    if not labels:raise ValueError('completed replay states required')
    # Explicit linkage closes the possibility of pairing unrelated derived
    # outputs which happen to share a filename or grid.
    for label in labels:
        state=folders[0]/(label+'_states.npz');relative=str(state.relative_to(ROOT));expected=sha256_file(state)
        for folder,manifest in zip(folders[1:],manifests[1:]):
            if manifest['input_sha256'].get(relative)!=expected:
                raise RuntimeError('derived audit lacks matching replay linkage: '+str(folder))
    sources=[Path(__file__),ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_bank_routing.py']
    for module in list(sys.modules.values()):
        filename=getattr(module,'__file__',None)
        if filename:
            path=Path(filename).resolve()
            if path.suffix=='.py' and path.is_relative_to(ROOT):sources.append(path)
    for path in sources:hashes[str(path.relative_to(ROOT))]=sha256_file(path)
    output.mkdir()
    specs=[(*map(str,folders),label,str(output)) for label in labels]
    with ProcessPoolExecutor(max_workers=min(args.workers,len(specs)),
            mp_context=multiprocessing.get_context('spawn')) as pool:
        cases=list(pool.map(evaluate,specs))
    for relative,expected in hashes.items():
        if sha256_file(ROOT/relative)!=expected:raise RuntimeError('input changed during bank audit: '+relative)
    write_json(output/'summary.json',dict(cases=cases))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        workers=min(args.workers,len(specs)),input_sha256=hashes,
        output_sha256={p.name:sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__=='__main__':main()
