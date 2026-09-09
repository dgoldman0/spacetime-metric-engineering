#!/usr/bin/env python3
"""Apply the longitudinal opening gate to archived controls on repaired beta075.

Independent candidates use up to six processes. The output contains numeric
tables, metric samples, exact parameter overrides, and input hashes. Narrative
interpretation belongs in the manually maintained investigation report.
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import replace
from pathlib import Path
import argparse
import csv
import hashlib
import json
import multiprocessing
import resource
import time

import numpy as np
from scipy.integrate import simpson

from adm_harness.geometry_opening import StaticSlice
from adm_harness.metric_regularity import regularized_scalars
from adm_harness.source_ledger import SourceParams, live_packet_end, live_packet_mask, scalars

ROOT = Path(__file__).resolve().parents[3]
PHASE = .745
EXTENTS = (3., 5., 7.)
CLOCK_BOXES = (0., .1, .5)
METRIC_FIELDS = ('alpha', 'gamma_ll', 'gamma_omega', 'beta')


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def service_check(params, deadline):
    """A necessary scalar packet screen; full carrier/source gates stay pending."""
    start = float(params.live_packet_start)
    end = live_packet_end(params)
    times = np.linspace(start, end, 65)
    offsets = np.linspace(-params.Rpass, params.Rpass, 41)
    maximum, failures, samples = -np.inf, 0, 0
    witness = None
    speeds, coordinate_speeds = [], []
    for s in times:
        if time.monotonic() > deadline:
            raise TimeoutError('registered computation allowance exhausted in packet screen')
        center = scalars(float(s), float(s), params)
        speeds.append(center['U_packet'])
        coordinate_speeds.append(center['vcoord'])
        for dx in offsets:
            x = float(s+dx)
            if not live_packet_mask(float(s), x, params):
                continue
            original = scalars(float(s), x, params)
            repaired = regularized_scalars(float(s), x, params)
            norm = -repaired['alpha']**2+repaired['gamma_ll']*(original['vcoord']+repaired['beta'])**2
            normalized = norm/repaired['alpha']**2
            if normalized > maximum:
                maximum, witness = float(normalized), [float(s), x, float(norm)]
            failures += int(norm >= 0)
            samples += 1
    return dict(live_start=start, restored_arrival=end, prepared_duration=end-start,
        samples=samples, non_timelike_samples=failures, maximum_norm_over_lapse_squared=maximum,
        worst_witness_phase_coordinate_norm=witness,
        schedule_factor_proxy_ratio=float(simpson(speeds, x=times)/(end-start)),
        packet_coordinate_proxy_ratio=float(simpson(coordinate_speeds, x=times)/(end-start)),
        scope='Necessary scalar checks on 65 times and 41 packet offsets; full carrier and source checks pending')


def relative_change(first, second, keys):
    return max(abs(first[k]-second[k])/max(abs(second[k]), 1e-30) for k in keys)


def run_candidate(task):
    spec, base, coarse_points, kappas, eta, reference_r0, output, deadline = task
    params = replace(SourceParams(**base), **spec['overrides'])
    x = np.linspace(-8., 8., 2*coarse_points-1)
    values = np.empty((len(x), 4))
    for i, point in enumerate(x):
        if i % 256 == 0 and time.monotonic() > deadline:
            raise TimeoutError('registered computation allowance exhausted in metric sampling')
        row = regularized_scalars(PHASE, float(point), params)
        values[i] = [row[key] for key in METRIC_FIELDS]
    a, b, r = values[:, 0], np.sqrt(values[:, 1]), np.sqrt(values[:, 2])
    slices = [StaticSlice(x[::2], r[::2], a[::2], b[::2]), StaticSlice(x, r, a, b)]
    fine = slices[-1]
    rows, metrics = [], {}
    for extent in EXTENTS:
        quadratures = [slices[0].quadrature(-extent, extent, min(kappas)),
            fine.quadrature(-extent, extent, min(kappas)),
            fine.quadrature(-extent, extent, min(kappas), order=16)]
        metrics[str(extent)] = quadratures[-1].tensor_summary()
        for kappa in kappas:
            if time.monotonic() > deadline:
                raise TimeoutError('registered computation allowance exhausted in opening gate')
            coarse, resolved, checked = [q.balance(kappa) for q in quadratures]
            if checked['required'] <= 0:
                raise RuntimeError('positive opening demand required by this registered comparison')
            sample_error = relative_change(coarse, checked, ('required', 'supply', 'optical_length'))
            gauss_error = relative_change(resolved, checked, ('required', 'supply', 'optical_length'))
            identity = max(checked['curvature_identity_error'], checked['einstein_cft_identity_error'])
            if max(sample_error, gauss_error, identity) > 1e-3:
                raise RuntimeError(f'{spec["label"]} requires refinement: {sample_error}, {gauss_error}, {identity}')
            for fraction in CLOCK_BOXES:
                # All interior clocks may vary in the box, with endpoint jets
                # retained. Taking opposite extremes in numerator/length is an
                # optimistic upper bound, irrespective of service admissibility.
                upper = checked['supply']*((1+fraction)/(1-fraction))**2
                rows.append(dict(label=spec['label'], coordinate_half_extent=extent,
                    kappa=kappa, central_charge=12*np.pi*kappa/eta,
                    kappa_over_reference_r0_squared=kappa/reference_r0**2,
                    kappa_over_candidate_r0_squared=kappa/fine.throat_radius**2,
                    lapse_fractional_change=fraction,
                    optical_length=checked['optical_length'], required=checked['required'],
                    original_supply=checked['supply'], original_ratio=checked['supply_over_required'],
                    optimistic_upper_ratio=upper/checked['required'],
                    necessary_gate_excludes=bool(upper < checked['required']*(1-max(1e-4, 10*sample_error))),
                    radial_endpoint=checked['radial_endpoint'], clock_endpoint=checked['clock_endpoint'],
                    sampling_relative_change=sample_error, quadrature_relative_change=gauss_error,
                    identity_scaled_error=identity))
    out = Path(output)
    cache = out/f'{spec["label"]}_metric.npz'
    np.savez_compressed(cache, coordinate=x, radius=r, lapse=a, radial_scale=b, beta=values[:, 3])
    throat = fine.jets(fine.throat_coordinate)
    summary = dict(label=spec['label'], overrides=spec['overrides'], provenance=spec['provenance'],
        throat_coordinate=fine.throat_coordinate, throat_radius=fine.throat_radius,
        throat_lapse=float(throat[1]), throat_radial_scale=float(throat[2]),
        throat_radius_times_second_derivative=float(throat[0]*throat[4]),
        receiver_memory_driver=float(scalars(PHASE, 0., params)['support_edge_receiver_memory_driver']),
        static_metric_sha256=hashlib.sha256(np.ascontiguousarray(values[:, :3]).tobytes()).hexdigest(),
        cache=cache.name, cache_sha256=sha256(cache), tensor_metrics=metrics,
        service=service_check(params, deadline), peak_worker_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return rows, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--points', type=int, default=8193, help='coarse native-coordinate samples; fine has 2n-1')
    parser.add_argument('--budget-seconds', type=float, default=900.)
    parser.add_argument('--output-cap-mb', type=float, default=20.)
    parser.add_argument('--specs', type=Path, default=ROOT/'toolkit/adm_harness_cli/specs/archived_geometry_opening.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 6 or args.points < 2049 or args.points % 2 != 1 or min(args.budget_seconds, args.output_cap_mb) <= 0:
        parser.error('one to six workers, odd points >= 2049, and positive allowances required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    sources = [ROOT/'supporting_reports/data/le_coupled_reset_source/manifest.json',
        ROOT/'supporting_reports/data/coupled_reorientation/longitudinal_gate/gate.json',
        ROOT/'supporting_reports/data/curved_quantum_boundary/geometry.npz', args.specs, Path(__file__),
        *[ROOT/'toolkit/adm_harness_cli/adm_harness'/name for name in
          ('geometry_opening.py', 'longitudinal_balance.py', 'source_ledger.py', 'metric_regularity.py', 'receiver_regularity.py')]]
    base = json.loads(sources[0].read_text())['params']
    old_gate = json.loads(sources[1].read_text())
    eta, reference_r0 = old_gate['eta'], old_gate['throat_radius']
    specs = json.loads(args.specs.read_text())
    if len({s['label'] for s in specs}) != len(specs) or not any(s['label'] == 'reference' and not s['overrides'] for s in specs):
        parser.error('distinct labels and an unchanged reference are required')
    for spec in specs:
        if not spec['label'].replace('_', '').isalnum() or not (ROOT/spec['provenance']).is_file():
            parser.error('simple labels and existing provenance files required')
    kappas = [eta/(12*np.pi)]+[reference_r0**2*q for q in (1e-6, 1e-5, 1e-4, .001, .01, .03, .1, .3, .6, .9)]
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    tasks = [(spec, base, args.points, kappas, eta, reference_r0, str(args.output), started+args.budget_seconds) for spec in specs]
    completed = {}
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        futures = {pool.submit(run_candidate, task): task[0]['label'] for task in tasks}
        for future in as_completed(futures):
            name = futures[future]
            completed[name] = future.result()
            print(f'Completed {name} ({len(completed)}/{len(tasks)})', flush=True)
    rows = [row for spec in specs for row in completed[spec['label']][0]]
    candidates = [completed[spec['label']][1] for spec in specs]
    reference = next(c for c in candidates if c['label'] == 'reference')
    with np.load(args.output/reference['cache']) as data:
        base_metric = np.vstack([data[k] for k in ('lapse', 'radial_scale', 'radius')])
        base_coordinate = data['coordinate'].copy()
    with np.load(sources[2]) as retained:
        cache_error = max(float(np.max(abs(np.interp(retained['coordinate'], base_coordinate, values)
            /retained[name]-1))) for values, name in zip(base_metric, ('lapse', 'radial_scale', 'radius')))
    if cache_error > 5e-6:
        raise RuntimeError(f'reference differs from the retained quantum geometry cache: {cache_error}')
    for candidate in candidates:
        with np.load(args.output/candidate['cache']) as data:
            compared = np.vstack([data[k] for k in ('lapse', 'radial_scale', 'radius')])
        candidate['maximum_relative_A_B_R_change'] = np.max(abs(compared/base_metric-1), axis=1).tolist()
        candidate['static_metric_identical_to_reference'] = candidate['static_metric_sha256'] == reference['static_metric_sha256']
    refs = {(row['coordinate_half_extent'], row['kappa'], row['lapse_fractional_change']): row for row in rows if row['label'] == 'reference'}
    for row in rows:
        ref = refs[row['coordinate_half_extent'], row['kappa'], row['lapse_fractional_change']]
        row['original_ratio_over_reference'] = row['original_ratio']/ref['original_ratio']
    with (args.output/'gates.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    summary = dict(scope='Necessary static longitudinal-source gate for archived controls transferred to repaired beta075; ordinary aggregate radial null stress >= 0',
        phase=PHASE, eta=eta, reference_r0=reference_r0,
        quantum_strength='Same eta and central charge for every geometry',
        geometry='Direct C2 repaired static slice; no added proper-distance mollifier or transplanted condensate exterior',
        clock_boxes='Exploratory pointwise bounds with fixed endpoint jets; service admissibility untested',
        optical_path='Coordinate intervals [-3,3], [-5,5], [-7,7]; zero exterior return gives optimistic supply',
        coarse_metric_points=args.points, fine_metric_points=2*args.points-1, workers=args.workers,
        elapsed_seconds=time.monotonic()-started, candidates=candidates,
        gates=len(rows), excluded_gates=sum(row['necessary_gate_excludes'] for row in rows),
        reference_cache_relative_error=cache_error,
        checks={key:max(row[key] for row in rows) for key in
                ('sampling_relative_change', 'quadrature_relative_change', 'identity_scaled_error')},
        source_hashes={str(path.relative_to(ROOT)):sha256(path) for path in sources})
    (args.output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    size = sum(p.stat().st_size for p in args.output.iterdir() if p.is_file())
    if size > args.output_cap_mb*1e6:
        raise RuntimeError(f'output allowance exceeded: {size} bytes')
    print(json.dumps(dict(candidates=len(candidates), gates=len(rows), excluded=summary['excluded_gates'],
        checks=summary['checks'], elapsed_seconds=summary['elapsed_seconds'], output_bytes=size), indent=2))


if __name__ == '__main__':
    main()
