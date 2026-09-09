#!/usr/bin/env python3
"""Parallel smooth-condensate vacuum response and curvature-junction audit."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import resource
import time

import numpy as np
import pandas as pd

from adm_harness.condensate_vacuum import (JoinedProfile, SmoothRadialProblem,
    join_curvature, junction_asymptote)
from adm_harness.curved_boundary import frequency_quadrature, tensor_from_moments
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
CHANNELS = ['energy', 'radial_pressure', 'angular_pressure', 'radial_enthalpy', 'angular_enthalpy']
PROBLEM = FREQUENCIES = WEIGHTS = PORTALS = DEADLINE = None


def initialize(problem, frequency_nodes, upper, lower, portals, deadline):
    global PROBLEM, FREQUENCIES, WEIGHTS, PORTALS, DEADLINE
    PROBLEM, PORTALS, DEADLINE = problem, portals, deadline
    FREQUENCIES, WEIGHTS = frequency_quadrature(frequency_nodes, upper, lower)


def angular_mode(index):
    result = np.zeros((len(PORTALS), len(PROBLEM.probes), 3))
    for frequency, weight in zip(FREQUENCIES, WEIGHTS):
        if time.monotonic() > DEADLINE:
            raise TimeoutError('registered mode budget exhausted')
        result += weight*PROBLEM.mode(frequency, index, PORTALS)
    return index, result*(2*index+1)/(4*np.pi**2), resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--spacing', type=float, default=1/256)
    parser.add_argument('--extent', type=float, default=96.)
    parser.add_argument('--angular-max', type=int, default=24)
    parser.add_argument('--frequency-nodes', type=int, default=80)
    parser.add_argument('--frequency-upper', type=float, default=64.)
    parser.add_argument('--frequency-lower', type=float, default=1e-7)
    parser.add_argument('--plateau', type=float, default=1e-7)
    parser.add_argument('--budget-seconds', type=float, default=600.)
    args = parser.parse_args()
    if not 1 <= args.workers <= 6 or args.angular_max < 0 or args.budget_seconds <= 0:
        parser.error('one to six workers and positive numerical allowances required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    started = time.monotonic()
    profile = JoinedProfile(ROOT)
    radii = np.linspace(2.18, 6.2, 65)
    main = profile.retained.negative_branch_coordinate(radii)
    centers, step = np.array([-1.5, -2.8, -4., -5.5]), .008
    probes = np.unique(np.r_[main, (centers[:, None]+step*np.arange(-2, 3)).ravel()])
    problem = SmoothRadialProblem.create(profile, probes, args.spacing, args.extent, args.plateau)
    portals = [.14, 1.4, 14.]
    sources = [Path(__file__).resolve(), profile.path,
        ROOT/'toolkit/adm_harness_cli/adm_harness/condensate_vacuum.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/condensate_joint.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/condensate_joint_audit.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/condensate_rail.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/curved_boundary.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/screened_condensate.py',
        ROOT/'supporting_reports/data/curved_quantum_boundary/geometry.npz']
    hashes = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    moments = np.zeros((args.angular_max+1, len(portals), len(probes), 3))
    peak, last = 0, started
    print(f'{len(problem.coordinate)} radial nodes, {len(probes)} witnesses, {args.angular_max+1} harmonics, {portals}', flush=True)
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn'),
            initializer=initialize, initargs=(problem, args.frequency_nodes, args.frequency_upper,
                args.frequency_lower, portals, started+args.budget_seconds)) as pool:
        for done, future in enumerate(as_completed([pool.submit(angular_mode, j) for j in range(args.angular_max+1)]), 1):
            j, result, rss = future.result()
            moments[j] = result
            peak = max(peak, rss)
            if time.monotonic()-last > 15 or done == args.angular_max+1:
                print(f'{done}/{args.angular_max+1} harmonics; {time.monotonic()-started:.1f} s', flush=True)
                last = time.monotonic()
    tensors = tensor_from_moments(moments.sum(axis=0))
    required = profile.demanded_remainder(probes).T
    r, a, b = profile.values(probes)
    records, balances = [], []
    for portal, tensor in zip(portals, tensors):
        for i, x in enumerate(probes):
            records.append({'portal': portal, 'coordinate': x, 'radius': r[i],
                'main_witness': bool(np.any(main == x)), 'higgs': float(profile.higgs(x)),
                **{k: tensor[i, j] for j, k in enumerate(CHANNELS)},
                **{'geometric_'+k: profile.eta*tensor[i, j] for j, k in enumerate(CHANNELS)},
                **{'required_remainder_'+k: required[i, j] for j, k in enumerate(CHANNELS)}})
        for center in centers:
            ix = np.array([np.argmin(abs(probes-center-k*step)) for k in range(-2, 3)])
            p = tensor[ix, 1]
            derivative = (p[0]-8*p[1]+8*p[3]-p[4])/(12*step)
            rlog, alog, _ = profile.retained.values(center, 1)
            rho, pr, pt = tensor[ix[2], :3]
            terms = np.array([derivative, alog*(rho+pr), 2*rlog*(pr-pt)])
            balances.append({'portal': portal, 'coordinate': center, 'step': step,
                'relative_residual': abs(terms.sum())/max(abs(terms).sum(), 1e-30)})
    args.output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(args.output/'response.csv.gz', index=False)
    pd.DataFrame(balances).to_csv(args.output/'conservation.csv', index=False)
    np.savez_compressed(args.output/'angular_moments.npz', moments=moments, coordinate=probes)
    jump = join_curvature(profile)
    asymptote = junction_asymptote(jump['inside_tensor'], jump['outside_tensor'])
    jump.update({k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in asymptote.items()})
    jump['geometric_tensor_d_minus_2'] = (profile.eta*asymptote['tensor_d_minus_2']).tolist()
    jump['eta'] = profile.eta
    (args.output/'junction.json').write_text(json.dumps(jump, indent=2)+'\n')
    for path in sources:
        if sha256_file(path) != hashes[str(path.relative_to(ROOT))]:
            raise RuntimeError('source changed during run: '+str(path))
    manifest = {**vars(args), 'output': str(args.output.relative_to(ROOT)) if args.output.is_relative_to(ROOT) else str(args.output),
        'completed_utc': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': time.monotonic()-started,
        'worker_peak_rss_kib': peak, 'radial_nodes': len(problem.coordinate), 'portals': portals,
        'eta': profile.eta, 'source_hashes': hashes,
        'scope': 'Neutral Higgs-portal scalar, static ground-state response relative to massless vacuum on the same joined geometry; controlled transparent Higgs plateau.',
        'output_hashes': {p.name: sha256_file(p) for p in sorted(args.output.iterdir()) if p.is_file()}}
    (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(f'completed in {manifest["elapsed_seconds"]:.1f} s; peak worker {peak/1024:.1f} MiB', flush=True)


if __name__ == '__main__':
    main()
