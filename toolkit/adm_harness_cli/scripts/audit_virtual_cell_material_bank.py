#!/usr/bin/env python3
"""Bound additive material-bank cost on immutable accepted thermal histories.

Constant heat capacity means E=B*Theta and b=1/B. The four active-contact
bounds are b_h>Lf, b_c<1/Bf, b_h*sqrt(a2)>Lg, b_c*sqrt(a2)<1/Bg.
The capacity-ratio infimum is max(Lf*Bf,Lg*Bg) when a2 is adjustable.
Rest inventory M and specific internal energy epsilon=u/c_light**2 obey
Delta E=M*Delta epsilon. All bank heat, existing walls, and original fluid
remain counted; this optimistic additive comparison charges only extra dust
rest energy. A material construction must also pay its pressure, containment,
hot-bank rest inventory, and any preparation offsets.
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
from audit_virtual_cell_ports import validate_controls
from run_poynting_delivery import BASE, ROOT, write_json

SAMPLES = ('midpoint', 'left_endpoint', 'right_endpoint', 'quarter', 'three_quarter')
BRANCHES = ('fluid_hot', 'fluid_cold', 'photon_hot', 'photon_cold')
LIMITS = ('Lf', 'Bf', 'Lg', 'Bg')
TOLERANCE = 1e-10


def constant_capacity_thresholds(H, C, T, counter, radius, active):
    """Return finite lower bounds; inverse cold bounds encode absent contacts as 0."""
    values = [np.asarray(v, float) for v in (H, C, T, counter, radius)]
    H, C, T, counter, radius = values
    active = np.asarray(active)
    if (H.ndim != 2 or min(H.shape) < 1 or any(v.shape != H.shape for v in values)
            or active.shape != (4,) + H.shape or active.dtype != bool
            or not all(np.isfinite(v).all() for v in values)
            or any(np.any(v < 0) for v in values[:-1]) or np.any(radius <= 0)):
        raise ValueError('finite nonnegative states, positive radius, and matching Boolean contacts required')
    if (np.any((active[0] | active[2]) & (H <= 0))
            or np.any(active[1] & (T <= 0)) or np.any(active[3] & (counter <= 0))):
        raise ValueError('every active donor requires positive energy or temperature')
    q = radius * np.sqrt(counter)
    out = np.zeros(active.shape)
    with np.errstate(over='ignore', divide='ignore', invalid='ignore'):
        for i, (numerator, denominator) in enumerate(((T, H), (C, T), (q, H), (C, q))):
            np.divide(numerator, denominator, out=out[i], where=active[i])
    if not np.isfinite(out).all():
        raise ValueError('nonrepresentable active caloric threshold')
    return out


def additive_inventory_bounds(D, density_shortfall, cold_energy, cold_panel_heat):
    """Per-label added rest allowance and heat/rest lower bounds, with all walls retained."""
    D, shortfall, C, heat = [np.asarray(v, float) for v in
                            (D, density_shortfall, cold_energy, cold_panel_heat)]
    if (D.ndim != 2 or D.shape[0] < 2 or D.shape[1] < 1 or shortfall.shape != D.shape
            or C.shape != D.shape or heat.shape != (D.shape[0]-1, D.shape[1])
            or not all(np.isfinite(v).all() for v in (D, shortfall, C, heat))
            or np.any(D <= 0) or np.any(C < 0) or np.any(heat < -TOLERANCE)):
        raise ValueError('finite compatible cold history and positive proper volume required')
    residual = np.diff(C, axis=0) - heat
    if np.max(np.abs(residual)) > TOLERANCE or np.any(np.diff(C, axis=0) < -TOLERANCE):
        raise ValueError('cold inventory must retain all counted receipts')
    instantaneous = -D * shortfall
    witness = np.argmin(instantaneous, axis=0)
    allowance = instantaneous[witness, np.arange(D.shape[1])]
    if np.any(allowance <= 0):
        raise ValueError('positive full density margin required for finite additive cost comparison')
    receipts = heat.sum(axis=0)
    result = dict(instantaneous_dust_rest_allowance=instantaneous,
        added_dust_rest_allowance=allowance, allowance_time_index=witness,
        cold_initial_energy=C[0], cold_final_energy=C[-1], cold_heat_receipts=receipts,
        cold_inventory_increase=C[-1]-C[0], cold_panel_conservation_residual=residual,
        required_specific_energy_increase=receipts/allowance,
        required_specific_energy_from_zero=C[-1]/allowance)
    if not all(np.isfinite(v).all() for v in result.values()):
        raise ValueError('nonrepresentable material inventory bound')
    return result


def verify_outputs(folder, filenames):
    """Authenticate inherited data and every actually consumed archive output."""
    folder = Path(folder)
    hashes, historical = validate_controls(folder, [])
    manifest = json.loads((folder/'manifest.json').read_text())
    for name in filenames:
        path = folder/name
        expected = manifest['output_sha256'].get(name)
        if expected is None or sha256_file(path) != expected:
            raise RuntimeError('changed or unregistered consumed output: ' + str(path))
        hashes[str(path.relative_to(ROOT))] = expected
    return hashes, historical


def summarize_range(values):
    return dict(minimum=float(np.min(values)), maximum=float(np.max(values)))


def evaluate(spec):
    temperature_path, temperature_meta, replay_path, replay_meta, output = map(Path, spec)
    meta = json.loads(temperature_meta.read_text())
    parent = json.loads(replay_meta.read_text())
    if (not meta.get('joint_bank_temperature_selection_passes')
            or not meta.get('independent_state_and_contact_checks_pass')
            or not parent.get('full_sampled_gate_passes')):
        raise ValueError('accepted temperature and full sampled replay gates required')
    with np.load(temperature_path) as f:
        a = {k: f[k] for k in f.files}
    with np.load(replay_path) as f:
        r = {k: f[k] for k in f.files}
    if not np.array_equal(a['t'], r['t']) or not np.array_equal(a['x'], r['x']):
        raise ValueError('temperature and replay grids differ')
    t, x = r['t'], r['x']
    if np.any(np.diff(t) <= 0) or np.any(np.diff(x) <= 0):
        raise ValueError('ordered temperature and spatial grids required')
    for suffix, key in (('H', 'receiver_hot_energy'), ('C', 'receiver_cold_energy')):
        if (not np.array_equal(a['left_endpoint_'+suffix], r[key][:-1])
                or not np.array_equal(a['right_endpoint_'+suffix], r[key][1:])):
            raise ValueError('temperature bank inventory differs from replay')
    heat = r['bank_fluid_cold_panel_heat'] + r['bank_photon_cold_panel_heat']
    result = additive_inventory_bounds(r['D'], r['density_shortfall'], r['receiver_cold_energy'], heat)
    result.update(t=t, x=x, allowance_time=t[result['allowance_time_index']])
    by_sample = []
    for name in SAMPLES:
        states = [a[name+'_'+key] for key in ('H', 'C', 'T', 'c', 'R')]
        active = np.array([a[name+'_'+key+'_active'] for key in BRANCHES])
        for i, branch in enumerate(BRANCHES):
            if not np.array_equal(active[i], r['bank_'+branch+'_panel_heat'] > meta['heat_activity_tolerance']):
                raise ValueError('temperature activity differs from archived gross heat')
        by_sample.append(constant_capacity_thresholds(*states, active))
    thresholds = np.stack(by_sample, axis=1)  # bound, sample, panel, material label
    flat = thresholds.reshape(4, -1, len(x))
    args = np.argmax(flat, axis=1)
    bounds = np.take_along_axis(flat, args[:, None, :], axis=1)[:, 0, :]
    sample_index, panel_index = np.divmod(args, len(t)-1)
    result.update(constant_capacity_lower_bounds=bounds,
        threshold_witness_sample_index=sample_index, threshold_witness_panel_index=panel_index)
    for key in ('H', 'C', 'T', 'c', 'R', 'time'):
        witness = np.empty_like(bounds)
        for i in range(4):
            for j in range(len(x)):
                val = a[SAMPLES[sample_index[i, j]]+'_'+key]
                witness[i, j] = val[panel_index[i, j]] if key == 'time' else val[panel_index[i, j], j]
        result['threshold_witness_'+key] = witness
    Lf, Bf, Lg, Bg = bounds.max(axis=1)
    a2 = float(meta['selected_channel_coefficient'])
    if not np.isfinite(a2) or a2 <= 0:
        raise ValueError('positive archived channel coefficient required')
    cold_capacity = np.maximum(bounds[1], bounds[3]*np.sqrt(a2))
    result['cold_rest_lower_bound_registered_beta3_fixed_a2'] = cold_capacity/3
    result['cold_rest_lower_bound_registered_beta3_fluid_only'] = bounds[1]/3
    result['cold_rest_to_added_allowance_registered_beta3_fixed_a2'] = cold_capacity/(3*result['added_dust_rest_allowance'])
    result['allowance_D'] = r['D'][result['allowance_time_index'], np.arange(len(x))]
    result['allowance_density_margin'] = -r['density_shortfall'][result['allowance_time_index'], np.arange(len(x))]
    if not all(np.isfinite(v).all() for v in result.values()):
        raise ValueError('nonfinite diagnostic output')
    witnesses = {}
    for i, key in enumerate(LIMITS):
        j = int(np.argmax(bounds[i]))
        witnesses[key] = dict(x=float(x[j]), sample=SAMPLES[sample_index[i, j]],
            panel_index=int(panel_index[i, j]), threshold=float(bounds[i, j]),
            **{k: float(result['threshold_witness_'+k][i, j]) for k in ('time', 'H', 'C', 'T', 'c', 'R')})
    ratio = max(Lf*Bf, Lg*Bg)
    fixed_ratio = max(Lf, Lg/np.sqrt(a2))*max(Bf, Bg*np.sqrt(a2))
    summary = dict(label=meta['label'], temperature_input=str(temperature_path.relative_to(ROOT)),
        replay_input=str(replay_path.relative_to(ROOT)), full_sampled_parent_gate_passes=True,
        independent_input_consistency_passes=True, diagnostic_finite=True,
        comparison='optimistic additive rest inventory on fixed counted histories; existing containment retained',
        additional_pressure_containment_hot_rest_and_preparation_offsets_counted=False,
        full_material_construction_supplied=False, continuous_time_bound_certified=False,
        temperature_normalization_modified=False, existing_fluid_inventory_reallocated=False,
        bank_heat_and_inventory_histories_modified=False,
        specific_energy_unit='u_specific/c_light**2; no length or particle-mass normalization required',
        general_material_bound='M_rest >= cold_heat_receipts / Delta(u_specific/c_light**2)',
        constant_capacity_law='E=B*Theta, b=1/B, epsilon=beta*Theta, M_rest=B/beta',
        constant_capacity_limits=dict(Lf=float(Lf), Uf=float(1/Bf) if Bf else None,
            Lg=float(Lg), Ug=float(1/Bg) if Bg else None),
        constant_capacity_ratio_infimum_adjustable_a2=float(ratio),
        constant_capacity_ratio_infimum_archived_a2=float(fixed_ratio),
        constant_capacity_ratio_scope='common capacities across sampled labels; cold/hot volume only for equal volumetric heat capacity',
        strict_ratio_infimum_attained=False, archived_channel_coefficient=a2,
        registered_beta3_scope='conditional existing U=3*M_rest*Theta caloric comparison with archived normalization; added mass only',
        limit_witnesses=witnesses,
        maximum_cold_panel_conservation_residual=float(np.max(np.abs(result['cold_panel_conservation_residual']))))
    for key in ('added_dust_rest_allowance', 'cold_heat_receipts', 'cold_initial_energy', 'cold_final_energy',
                'required_specific_energy_increase', 'required_specific_energy_from_zero',
                'cold_rest_lower_bound_registered_beta3_fixed_a2',
                'cold_rest_lower_bound_registered_beta3_fluid_only',
                'cold_rest_to_added_allowance_registered_beta3_fixed_a2'):
        summary[key] = summarize_range(result[key])
    label = meta['label']
    np.savez_compressed(output/(label+'_material_bank.npz'), **result)
    write_json(output/(label+'_summary.json'), summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', nargs='+', required=True)
    parser.add_argument('--output-name', required=True)
    parser.add_argument('--workers', type=int, default=2)
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one through six independent workers required')
    output = BASE/args.output_name
    if output.exists():
        raise RuntimeError('preserve completed material-bank diagnostic')
    hashes, historical, specs = {}, [], []
    for source in args.sources:
        folder = BASE/source
        files = sorted(folder.glob('*_temperature.npz'))
        if not files:
            raise ValueError('completed five-point temperature archive required')
        for path in files:
            meta_path = path.with_name(path.name.replace('_temperature.npz', '_summary.json'))
            checked, history = verify_outputs(folder, [path.name, meta_path.name])
            hashes.update(checked); historical.extend(history)
            meta = json.loads(meta_path.read_text())
            replay = ROOT/meta['input']
            replay_meta = replay.with_name(replay.name.replace('_states.npz', '_summary.json'))
            checked, history = verify_outputs(replay.parent, [replay.name, replay_meta.name])
            hashes.update(checked); historical.extend(history)
            specs.append((path, meta_path, replay, replay_meta, output))
    runtime = [Path(__file__), ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_material_bank.py']
    for module in list(sys.modules.values()):
        filename = getattr(module, '__file__', None)
        if filename:
            path = Path(filename).resolve()
            if path.suffix == '.py' and path.is_relative_to(ROOT):
                runtime.append(path)
    hashes.update({str(path.relative_to(ROOT)): sha256_file(path) for path in runtime})
    output.mkdir()
    workers = min(args.workers, len(specs))
    with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        cases = list(pool.map(evaluate, specs))
    for relative, expected in hashes.items():
        if sha256_file(ROOT/relative) != expected:
            raise RuntimeError('input changed during material-bank audit: ' + relative)
    write_json(output/'summary.json', dict(cases=cases))
    write_json(output/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        workers=workers, input_sha256=hashes, historical_source=historical,
        output_sha256={p.name: sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
