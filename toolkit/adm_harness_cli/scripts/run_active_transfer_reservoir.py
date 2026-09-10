#!/usr/bin/env python3
"""Build and test a causal two-stream reservoir on the repaired active rail.

Writes numerical evidence only. Narrative reports are maintained manually.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import replace
from datetime import datetime, timezone
import json
import multiprocessing
from pathlib import Path
import time

import numpy as np
import pandas as pd

from adm_harness.active_transfer_reservoir import (
    TabulatedActiveMedium, required_preload, trace_characteristics,
)
from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.metric_regularity import regularized_scalars
from adm_harness.source_ledger import SourceParams, live_packet_end, scalars, sha256_file


ROOT = Path(__file__).resolve().parents[3]
REFERENCE = ROOT/'supporting_reports/data/le_metric_c2_repair/manifest.json'
RUNS = ROOT/'toolkit/adm_harness_cli/runs'
SURFACES = {
    'baseline': 'beta_collar_generator_beta075_p003_mid_s15',
    'dense': 'beta_collar_generator_beta075_p003_mid_dense377x241_sharded12',
}
MOMENTS = ('regulated_sector_rho', 'regulated_sector_p_l', 'regulated_sector_j_l', 'medium_angular_pressure')
CASES = {
    'coarse': ('coarse', 'baseline', 401, .01),
    'refined': ('fine', 'baseline', 801, .005),
    'time_refined': ('fine', 'baseline', 801, .0025),
    'dense_source': ('fine', 'dense', 801, .005),
}


def parameters():
    return json.loads(REFERENCE.read_text())['params']


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def metric_rows(task):
    times, positions, values = task
    params = SourceParams(**values)
    rows = np.empty((len(times), len(positions), 4))
    for i, t in enumerate(times):
        for j, x in enumerate(positions):
            g = regularized_scalars(float(t), float(x), params)
            rows[i, j] = (np.log(g['alpha']), g['beta'], .5*np.log(g['gamma_ll']), .5*np.log(g['gamma_omega']))
    return rows


def medium_table(surface, output):
    path = RUNS/SURFACES[surface]/'endpoint_medium_covariant_audit_freeze_rematch_w6_t1p5/endpoint_medium_covariant_point_projection.csv'
    frame = pd.read_csv(path, usecols=['s', 'l', *MOMENTS])
    if frame.duplicated(['s', 'l']).any():
        raise ValueError('duplicate medium spacetime keys')
    times = np.sort(frame.s.unique())
    positions = np.sort(frame.l.unique())
    arrays = {}
    for key, column in zip(('rho', 'pressure', 'current', 'angular'), MOMENTS):
        arrays[key] = frame.pivot(index='s', columns='l', values=column).reindex(index=times, columns=positions).fillna(0.).to_numpy()
    target = output/f'medium_{surface}.npz'
    np.savez_compressed(target, t=times, x=positions, **arrays)
    return {'source': str(path.relative_to(ROOT)), 'sha256': sha256_file(path), 'rows': len(frame),
            'interpolation_shape': [len(times), len(positions)], 'output': target.name}


def prepare(args):
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    params = parameters()
    medium = {name: medium_table(name, args.output) for name in SURFACES}
    for name, dt, dx in [('coarse', .025, .05), ('fine', .0125, .025)]:
        times = np.linspace(-1.5, 3., round(4.5/dt)+1)
        positions = np.linspace(-6., 6., round(12/dx)+1)
        tasks = [(chunk, positions, params) for chunk in np.array_split(times, args.workers*4)]
        print(f'preparing {name} active metric: {len(times)} x {len(positions)}', flush=True)
        with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
            data = np.concatenate(list(pool.map(metric_rows, tasks)), axis=0)
        np.savez_compressed(args.output/f'metric_{name}.npz', t=times, x=positions,
                            log_alpha=data[..., 0], beta=data[..., 1], log_b=data[..., 2],
                            log_r=data[..., 3], core_radius=params['Rth'])
    validation = []
    rng = np.random.default_rng(260909)
    probes = [(-1.5+4.5*u, -6+12*v) for u, v in rng.random((384, 2))]
    probes += [(s, s+offset) for s in np.linspace(-1.4, live_packet_end(SourceParams(**params)), 33)
               for offset in [-.3, 0., .3]]
    for name in ('coarse', 'fine'):
        model = TabulatedActiveMedium(args.output/f'metric_{name}.npz', args.output/'medium_baseline.npz')
        for t, x in probes:
            expected = regularized_scalars(float(t), float(x), SourceParams(**params))
            observed = model.metric(t, np.array([x]))
            for key, value in [('alpha', observed.alpha[0]), ('beta', observed.beta[0]),
                               ('gamma_ll', observed.b[0]**2), ('gamma_omega', observed.radius[0]**2)]:
                scale = max(abs(expected[key]), 1.) if key == 'beta' else abs(expected[key])
                validation.append({'grid': name, 's': t, 'l': x, 'field': key,
                                   'reference': expected[key], 'interpolated': value,
                                   'relative_error': abs(value-expected[key])/scale})
    pd.DataFrame(validation).to_csv(args.output/'metric_interpolation_checks.csv', index=False)
    # Record the initial bounded timing reconnaissance with the full active tensor.
    timing = []
    variants = [('reference', {}), ('receiver_early', {'support_edge_receiver_post_release_widths': 0.}),
                ('receiver_late', {'support_edge_receiver_post_release_widths': 8.}),
                ('jacket_early', {'xOmega': 1.}), ('jacket_late', {'xOmega': 3.}),
                ('jacket_broad', {'wtOmega': 1.2}), ('jacket_fast', {'wtOmega': .3}),
                ('early_both', {'xOmega': 1., 'support_edge_receiver_post_release_widths': 0.}),
                ('late_both', {'xOmega': 3., 'support_edge_receiver_post_release_widths': 8.})]
    for label, changes in variants:
        p = replace(SourceParams(**params), **changes)
        for t, x in [(-1.5, -1.3), (-.578457, -.75), (.650266, .65), (1.264628, 1.65),
                     (1.615691, -2.05), (1.878989361702128, -1.8), (1.878989361702128, -.981278)]:
            row = evaluate_demand(t, x, p, .000625, .000625, scalar_evaluator=regularized_scalars)
            timing.append({'variant': label, 's': t, 'l': x, **{k: row[k] for k in ('rho', 'p_l', 'j_l', 'p_omega', 'stress_algebraic_type')},
                           'radial_frame_margin': abs(row['rho']+row['p_l'])-2*abs(row['j_l'])})
    pd.DataFrame(timing).to_csv(args.output/'timing_reconnaissance.csv', index=False)
    write_json(args.output/'input_manifest.json', {
        'created_utc': datetime.now(timezone.utc).isoformat(), 'params': params,
        'reference_manifest_sha256': sha256_file(REFERENCE), 'medium': medium,
        'medium_representation': 'cubic moment interpolants, zero absent cells; C2 outer taper 1.9..2.1 and moving packet exclusion 0.35..0.45',
        'metric': 'full scheduled repaired ADM fields; unit lapse/radial-scale analytic tails outside |l|=6',
        'time_interval': [-1.5, 3.], 'cases': CASES, 'workers': args.workers,
        'elapsed_seconds': time.monotonic()-started,
    })
    print(f'inputs prepared in {time.monotonic()-started:.1f} s', flush=True)


def run_case(task):
    name, output = task
    output = Path(output)
    metric, medium, count, dt = CASES[name]
    model = TabulatedActiveMedium(output/f'metric_{metric}.npz', output/f'medium_{medium}.npz')
    params = SourceParams(**parameters())
    seeds = np.linspace(-9., 9., count)
    times = np.linspace(-1.5, 3., round(4.5/dt)+1)
    summaries, selected_records = [], []
    started = time.monotonic()
    for direction in (1, -1):
        history = trace_characteristics(model, seeds, times, direction)
        position, log_gain, integral = history[:, 0], history[:, 1], history[:, 2]
        preload = required_preload(integral)
        max_live = max_core = 0.
        witness = None
        core_witness = None
        for i, t in enumerate(times):
            if not params.live_packet_start <= t <= live_packet_end(params):
                continue
            g = model.metric(t, position[i])
            mu = np.exp(log_gain[i])*(preload+integral[i])/g.volume
            live = np.abs(position[i]-t) <= params.Rpass
            core = np.abs(position[i]-t) <= params.Rpass-.05
            if live.any():
                index = int(np.argmax(np.where(live, mu, -1.)))
                if mu[index] > max_live:
                    max_live = float(mu[index]); witness = (i, index)
            if core.any():
                index = int(np.argmax(np.where(core, mu, -1.)))
                if mu[index] > max_core:
                    max_core = float(mu[index]); core_witness = (i, index)
        chosen = core_witness or witness
        row = {'case': name, 'direction': direction, 'metric': metric, 'medium': medium,
               'rays': count, 'dt': dt, 'minimum_initial_proper_energy': float(4*np.pi*np.trapezoid(preload, seeds)),
               'max_required_initial_density_weight': float(preload.max()),
               'max_live_stream_density': max_live, 'max_packet_interior_stream_density': max_core,
               'minimum_ray_spacing': float(np.min(np.diff(position, axis=1))),
               'max_abs_log_gain': float(np.max(np.abs(log_gain))),
               'max_outer_seed_preload': float(max(preload[0], preload[-1]))}
        if chosen is not None:
            i, j = chosen
            row.update(witness_s=float(times[i]), witness_l=float(position[i, j]), initial_l=float(seeds[j]),
                       initial_preload=float(preload[j]), witness_integral=float(integral[i, j]),
                       minimum_integral=float(integral[:, j].min()),
                       minimum_integral_time=float(times[np.argmin(integral[:, j])]))
            for k, t in enumerate(times):
                x = position[k, j]
                g = model.metric(t, np.array([x]))
                v, gain, source = model.coefficients(t, np.array([x]), direction)
                selected_records.append({'case': name, 'direction': direction, 's': float(t), 'l': float(x),
                                         'initial_l': float(seeds[j]), 'log_gain': float(log_gain[k, j]),
                                         'source_integral': float(integral[k, j]), 'initial_preload': float(preload[j]),
                                         'minimum_stream_density': float(np.exp(log_gain[k, j])*(preload[j]+integral[k, j])/g.volume[0]),
                                         'source': float(source[0]), 'null_speed': float(v[0]),
                                         'inside_packet_live': bool(params.live_packet_start <= t <= live_packet_end(params) and abs(x-t) <= params.Rpass)})
        summaries.append(row)
        pd.DataFrame({'initial_l': seeds, 'minimum_preload': preload,
                      'min_source_integral': integral.min(axis=0)}).to_csv(output/f'{name}_seeds_{direction:+d}.csv', index=False)
        print(f'{name} direction {direction:+d}: packet interior density lower bound {max_core:.6g}', flush=True)
    pd.DataFrame(selected_records).to_csv(output/f'{name}_witnesses.csv', index=False)
    write_json(output/f'{name}_summary.json', {'results': summaries, 'elapsed_seconds': time.monotonic()-started})
    return summaries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/active_transfer_reservoir')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--cases', nargs='+', choices=list(CASES), default=list(CASES))
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('use between one and six independent workers')
    if args.prepare:
        prepare(args)
        return
    started = time.monotonic()
    records = []
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        futures = {pool.submit(run_case, (name, str(args.output))): name for name in args.cases}
        for future in as_completed(futures):
            records.extend(future.result())
            print(f'completed {futures[future]} after {time.monotonic()-started:.1f} s', flush=True)
    pd.DataFrame(records).to_csv(args.output/'reservoir_summary.csv', index=False)
    write_json(args.output/'run_manifest.json', {
        'completed_utc': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': time.monotonic()-started,
        'workers': args.workers, 'cases': args.cases,
        'software_sha256': {str(p.relative_to(ROOT)): sha256_file(p) for p in (
            Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/active_transfer_reservoir.py')},
        'input_manifest_sha256': sha256_file(args.output/'input_manifest.json'),
        'scope': 'fixed active metric; necessary positive radial-stream completion and packet-exclusion test; sampled optimal preload is a lower bound',
    })


if __name__ == '__main__':
    main()
