#!/usr/bin/env python3
"""Parallel spherical boundary-induced vacuum tensor on the retained rail."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import argparse
import json
import multiprocessing
from pathlib import Path
import resource
import time

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline

from adm_harness.curved_boundary import (StaticGeometry, RadialProblem, placements,
    frequency_quadrature, mode_moments, tensor_from_moments)
from adm_harness.metric_regularity import regularized_scalars
from adm_harness.source_ledger import SourceParams, sha256_file

ROOT = Path(__file__).resolve().parents[3]
CHANNELS = ['energy', 'radial_pressure', 'angular_pressure', 'radial_enthalpy', 'angular_enthalpy']
PROBLEM = FREQUENCIES = WEIGHTS = DEADLINE = None


def initialize(problem, nodes, upper, lower, memory_mib, deadline):
    global PROBLEM, FREQUENCIES, WEIGHTS, DEADLINE
    resource.setrlimit(resource.RLIMIT_AS, (memory_mib*1024**2, memory_mib*1024**2))
    PROBLEM = problem
    FREQUENCIES, WEIGHTS = frequency_quadrature(nodes, upper, lower)
    DEADLINE = deadline


def angular_mode(index):
    accumulated = np.zeros((len(placements()), len(PROBLEM.probe_nodes), 3))
    for frequency, weight in zip(FREQUENCIES, WEIGHTS):
        if time.monotonic() > DEADLINE:
            raise TimeoutError('registered mode-computation allowance exhausted')
        accumulated += weight*mode_moments(PROBLEM, frequency, index)
    return index, accumulated*(2*index+1)/(4*np.pi**2), resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def geometry_sources():
    return [ROOT/'supporting_reports/data/le_coupled_reset_source/manifest.json',
        ROOT/'toolkit/adm_harness_cli/adm_harness/source_ledger.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/metric_regularity.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/receiver_regularity.py']


def geometry_at_start(cache):
    sources = geometry_sources()
    hashes = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    metadata_path = cache.with_suffix('.json')
    if cache.exists():
        metadata = json.loads(metadata_path.read_text())
        if metadata['source_hashes'] != hashes or metadata['cache_sha256'] != sha256_file(cache):
            raise RuntimeError('geometry cache differs from its frozen inputs')
        with np.load(cache) as data:
            return StaticGeometry(**dict(data))
    parameters = SourceParams(**json.loads(sources[0].read_text())['params'])
    coordinates = np.linspace(-8., 8., 8193)
    arrays = []
    for x in coordinates:
        values = regularized_scalars(.745, float(x), parameters)
        arrays.append([np.sqrt(values['gamma_omega']), values['alpha'], np.sqrt(values['gamma_ll'])])
    r, n, a = np.array(arrays).T
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache, coordinate=coordinates, radius=r, lapse=n, radial_scale=a,
                        throat_parameter=parameters.Rth)
    metadata_path.write_text(json.dumps({'phase': .745, 'source_hashes': hashes,
        'cache_sha256': sha256_file(cache), 'tabulated_points': len(coordinates)}, indent=2)+'\n')
    return StaticGeometry(coordinates, r, n, a, parameters.Rth)


def observations(geometry, walls):
    target_r = np.linspace(2.18, 6.2, 65)
    candidates = geometry.negative_branch_coordinate(target_r)
    distance = np.abs(geometry.proper_coordinate(candidates)[:, None]-geometry.proper_coordinate(walls)[None, :])
    main = candidates[np.min(distance, axis=1) >= .5]
    # Independent five-point stress derivatives, with fixed positions at every level.
    centers, step = [-1.5, -2.8, -4., -5.5], .016
    conservation = np.array([x+k*step for x in centers for k in [-2, -1, 0, 1, 2]])
    probes = np.unique(np.r_[main, conservation])
    return probes, main, np.array(centers), step


def conservation_rows(geometry, probes, tensors, centers, step):
    rows = []
    for case, tensor in zip(placements(), tensors):
        for center in centers:
            i = np.array([np.argmin(np.abs(probes-(center+k*step))) for k in [-2, -1, 0, 1, 2]])
            pressure = tensor[i, 1]
            derivative = (pressure[0]-8*pressure[1]+8*pressure[3]-pressure[4])/(12*step)
            rlog, nlog, _ = geometry.values(center, 1)
            energy, radial, angular = tensor[i[2], :3]
            lapse_term, angular_term = nlog*(energy+radial), 2*rlog*(radial-angular)
            residual = derivative+lapse_term+angular_term
            scale = abs(derivative)+abs(lapse_term)+abs(angular_term)
            rows.append({'arrangement': case['name'], 'coupling': case['coupling'], 'coordinate': center,
                'pressure_derivative': derivative, 'lapse_term': lapse_term, 'angular_term': angular_term,
                'residual': residual, 'relative_residual': residual/max(scale, 1e-30)})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--spacing', type=float, default=1/256)
    parser.add_argument('--extent', type=float, default=48.)
    parser.add_argument('--angular-max', type=int, default=64)
    parser.add_argument('--frequency-nodes', type=int, default=96)
    parser.add_argument('--frequency-upper', type=float, default=2048.)
    parser.add_argument('--frequency-lower', type=float, default=1e-7)
    parser.add_argument('--budget-seconds', type=float, default=900.)
    parser.add_argument('--worker-memory-mib', type=int, default=1536)
    parser.add_argument('--output-cap-mb', type=float, default=12.)
    parser.add_argument('--geometry-cache', type=Path, default=ROOT/'supporting_reports/data/curved_quantum_boundary/geometry.npz')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 6 or args.angular_max < 0 or min(args.budget_seconds, args.worker_memory_mib, args.output_cap_mb) <= 0:
        parser.error('one to six workers, nonnegative angular maximum, and positive allowances required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    started = time.monotonic()
    sources = geometry_sources()+[Path(__file__).resolve(),
        ROOT/'toolkit/adm_harness_cli/adm_harness/curved_boundary.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/reset_inverse_search.py',
        ROOT/'supporting_reports/data/le_coupled_reset_source/reference_tensors.csv.gz',
        ROOT/'supporting_reports/data/comer_two_current/reference_initial_profile.csv']
    hashes = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    geometry = geometry_at_start(args.geometry_cache)
    walls = geometry.negative_branch_coordinate([2.35, 2.85, 6.8])
    probes, main_probes, centers, step = observations(geometry, walls)
    problem = RadialProblem.create(geometry, args.spacing, args.extent, walls, probes)
    args.output.mkdir(parents=True, exist_ok=True)
    contributions = np.zeros((args.angular_max+1, len(placements()), len(probes), 3))
    peak, completed, last = 0, 0, time.monotonic()
    print(f'{len(problem.coordinate)} radial nodes; {len(probes)} witnesses; {args.angular_max+1} angular modes; {len(placements())} placements/couplings', flush=True)
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn'),
            initializer=initialize, initargs=(problem, args.frequency_nodes, args.frequency_upper,
                args.frequency_lower, args.worker_memory_mib, started+args.budget_seconds)) as pool:
        futures = [pool.submit(angular_mode, j) for j in range(args.angular_max+1)]
        for future in as_completed(futures):
            index, value, rss = future.result()
            contributions[index] = value
            peak = max(peak, rss); completed += 1
            if time.monotonic()-last >= 15 or completed == len(futures):
                print(f'angular modes {completed}/{len(futures)}, elapsed {time.monotonic()-started:.1f} s', flush=True)
                last = time.monotonic()
    tensors = tensor_from_moments(np.sum(contributions, axis=0))
    reference = pd.read_csv(sources[-1], float_precision='round_trip')
    r, n, a = geometry.values(probes)
    demanded = {channel: CubicSpline(reference.radius, reference[channel])(r)
                for channel in CHANNELS if channel != 'angular_enthalpy'}
    demanded['angular_enthalpy'] = demanded['energy']+demanded['angular_pressure']
    rows = []
    for case, tensor in zip(placements(), tensors):
        for k, (x, values) in enumerate(zip(probes, tensor)):
            rows.append({'arrangement': case['name'], 'coupling': case['coupling'], 'coordinate': x,
                'radius': r[k], 'lapse': n[k], 'radial_scale': a[k],
                'main_witness': bool(np.any(main_probes == x)),
                **dict(zip(CHANNELS, values)),
                **{'demanded_'+key: value[k] for key, value in demanded.items()}})
    pd.DataFrame(rows).to_csv(args.output/'boundary_profiles.csv.gz', index=False)
    pd.DataFrame(conservation_rows(geometry, probes, tensors, centers, step)).to_csv(args.output/'conservation.csv', index=False)
    np.savez_compressed(args.output/'angular_moments.npz', moments=contributions, coordinate=probes)
    wall_r, wall_n, wall_a = geometry.values(walls)
    pd.DataFrame({'coordinate': walls, 'radius': wall_r, 'lapse': wall_n, 'radial_scale': wall_a}).to_csv(args.output/'walls.csv', index=False)
    for path in sources:
        if sha256_file(path) != hashes[str(path.relative_to(ROOT))]:
            raise RuntimeError(f'input changed during run: {path}')
    size = sum(p.stat().st_size for p in args.output.iterdir())
    elapsed = time.monotonic()-started
    if elapsed > args.budget_seconds or size > args.output_cap_mb*1e6:
        raise RuntimeError('registered compute or output allowance exceeded')
    manifest = {'completed_utc': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': elapsed,
        'workers': args.workers, 'worker_peak_rss_kib': peak, 'worker_memory_mib': args.worker_memory_mib,
        'spacing': args.spacing, 'extent': args.extent, 'radial_nodes': len(problem.coordinate),
        'angular_max': args.angular_max, 'frequency_nodes': args.frequency_nodes,
        'frequency_upper': args.frequency_upper, 'frequency_lower': args.frequency_lower,
        'main_witnesses': len(main_probes), 'total_witnesses': len(probes), 'cases': len(placements()),
        'evidence_bytes_before_manifest': size, 'geometry_cache_sha256': sha256_file(args.geometry_cache),
        'source_hashes': hashes,
        'scope': 'Minimal massless scalar ground-state boundary response on the complete frozen holding geometry; bulk differences away from sheets; absolute curved vacuum and material remain separate source terms.'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(manifest, indent=2), flush=True)


if __name__ == '__main__':
    main()
