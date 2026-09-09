#!/usr/bin/env python3
"""Independent refinements and continuous-mode checks for condensate stress."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess
import sys
import time

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

from adm_harness.condensate_vacuum import (JoinedProfile, SmoothRadialProblem,
    join_curvature, junction_asymptote, local_born_reflection)
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
RUNNER = Path(__file__).with_name('run_condensate_vacuum.py')
BASE_OPTIONS = {'spacing': 1/256, 'extent': 96., 'angular_max': 24,
    'frequency_nodes': 80, 'frequency_lower': 1e-7, 'frequency_upper': 64., 'plateau': 1e-7}
LEVELS = {
    'base': {},
    'space512': {'spacing': 1/512},
    'space1024': {'spacing': 1/1024},
    'frequency': {'spacing': 1/1024, 'frequency_nodes': 144, 'frequency_lower': 1e-9, 'frequency_upper': 128},
    'angular': {'spacing': 1/1024, 'frequency_nodes': 144, 'frequency_lower': 1e-9, 'frequency_upper': 128, 'angular_max': 48},
    'ends': {'spacing': 1/1024, 'frequency_nodes': 144, 'frequency_lower': 1e-9, 'frequency_upper': 128, 'angular_max': 48, 'extent': 384},
    'plateau': {'spacing': 1/1024, 'frequency_nodes': 144, 'frequency_lower': 1e-9, 'frequency_upper': 128, 'angular_max': 48, 'extent': 384, 'plateau': 1e-9}}


def continuous_mode(task):
    frequency, angular_index = task
    profile = JoinedProfile(ROOT)
    probes = profile.retained.negative_branch_coordinate(np.array([3., 4., 5., 6.2]))
    portal, extent = 1.4, 192.
    def equation(x, state):
        r, a, b = profile.values(x)
        p = a*r*r/b
        q = a*b*(angular_index*(angular_index+1)+frequency**2*r*r/(a*a))
        dq = a*b*r*r*profile.mass_squared(x, portal)
        z, delta = state
        return [q-z*z/p, dq-(2*z*delta+delta*delta)/p]
    solutions = []
    for direction in [1., -1.]:
        start, stop = -direction*extent, (max(probes) if direction == 1 else min(probes))
        r, a, b = profile.values(start)
        p = a*r*r/b
        mass = profile.mass_squared(start, portal)
        # Decaying asymptotic Robin data. Both end distances exceed the
        # longest selected wavelength by more than nineteen e-folds.
        z = direction*p*b*frequency/a
        dz = direction*p*b*mass/(np.sqrt(frequency**2/a**2+mass)+frequency/a)
        result = solve_ivp(equation, (start, stop), [z, dz], method='DOP853',
            rtol=2e-11, atol=2e-13, dense_output=True)
        if not result.success:
            raise RuntimeError(result.message)
        solutions.append(result.sol(probes))
    (zl, dl), (zr, dr) = solutions
    denominator, ds = zl-zr, dl-dr
    gm = 1/(denominator+ds)
    dg = -ds/(denominator*(denominator+ds))
    r, a, b = profile.values(probes)
    p = a*r*r/b
    mixed = ((dl*zr+zl*dr+dl*dr)*gm+zl*zr*dg)/(p*p)
    expected = np.stack([-frequency**2*dg/(a*a), mixed/(b*b),
        angular_index*(angular_index+1)*dg/(2*r*r)], axis=-1)
    records = []
    for resolution in [256, 512, 1024]:
        finite = SmoothRadialProblem.create(profile, probes, spacing=1/resolution, extent=192.)
        actual = finite.mode(frequency, angular_index, [portal])[0]
        errors = np.max(abs(actual-expected), axis=1)/np.max(abs(expected), axis=1)
        for x, error in zip(probes, errors):
            records.append({'frequency': frequency, 'angular_index': angular_index,
                'coordinate': x, 'resolution': resolution, 'relative_moment_error': error})
    return records


def exact_local_reflection(k, cosine, a, b):
    """Full radial ODE on a C1 quadratic local metric, without a Born expansion."""
    def potential_scaled(z):
        x = z/k
        return (cosine**2*np.exp(-a*x*x)+(1-cosine**2)*np.exp(-b*x*x)
            +(b+a/2+(b+a/2)**2*x*x)/k**2)
    result = solve_ivp(lambda z, y: [potential_scaled(z)-y[0]**2], (30., 0.),
        [-np.sqrt(potential_scaled(30.))], method='DOP853', rtol=2e-13, atol=2e-14)
    if not result.success:
        raise RuntimeError(result.message)
    y = result.y[0, -1]
    return (1+y)/(1-y)


def junction_controls(profile):
    jump = join_curvature(profile)
    asymptote = junction_asymptote(jump['inside_tensor'], jump['outside_tensor'])
    a, b = asymptote['lapse_second_jump'], asymptote['radius_second_over_radius_jump']
    records = []
    for cosine in [0., .4, 1.]:
        predicted = -((1-cosine**2)*a+(1+cosine**2)*b)/8
        for k in [1., 3., 10., 30., 100.]:
            exact = exact_local_reflection(k, cosine, a, b)
            records.append({'cosine': cosine, 'momentum': k,
                'scaled_exact_reflection': k*k*exact, 'asymptotic_coefficient': predicted,
                'relative_exact_error': abs(k*k*exact/predicted-1),
                'compact_born_scaled': k*k*local_born_reflection(k, cosine, a, b)})
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    started = time.monotonic()
    for name, options in LEVELS.items():
        directory = args.output/name
        if (directory/'manifest.json').exists():
            manifest = json.loads((directory/'manifest.json').read_text())
            for filename, expected in manifest['source_hashes'].items():
                if sha256_file(ROOT/filename) != expected:
                    raise RuntimeError('cached run source changed: '+filename)
            for filename, expected in manifest['output_hashes'].items():
                if sha256_file(directory/filename) != expected:
                    raise RuntimeError('cached run evidence changed: '+filename)
            for key, expected in {**BASE_OPTIONS, **options}.items():
                if manifest[key] != expected:
                    raise RuntimeError('cached refinement arguments differ')
            continue
        command = [sys.executable, str(RUNNER), '--output', str(directory), '--workers', str(args.workers)]
        for key, value in options.items():
            command.extend(['--'+key.replace('_', '-'), str(value)])
        print('refinement '+name, flush=True)
        subprocess.run(command, check=True)
    comparisons = []
    previous = 'base'
    for name in list(LEVELS)[1:]:
        before = pd.read_csv(args.output/previous/'response.csv.gz')
        after = pd.read_csv(args.output/name/'response.csv.gz')
        cols = ['energy', 'radial_pressure', 'angular_pressure', 'radial_enthalpy', 'angular_enthalpy']
        old, new = before[cols].to_numpy(), after[cols].to_numpy()
        error = np.max(abs(new-old), axis=1)/np.maximum(np.max(abs(new), axis=1), 1e-30)
        comparisons.append({'before': previous, 'after': name, 'maximum_relative_tensor_change': error.max()})
        previous = name
    pd.DataFrame(comparisons).to_csv(args.output/'refinement_comparisons.csv', index=False)
    print('continuous radial-mode and junction controls', flush=True)
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        rows = list(pool.map(continuous_mode, [(.1, 0), (.2, 1), (.4, 2)]))
    pd.DataFrame([row for group in rows for row in group]).to_csv(args.output/'continuous_mode_checks.csv', index=False)
    profile = JoinedProfile(ROOT)
    pd.DataFrame(junction_controls(profile)).to_csv(args.output/'junction_scattering_checks.csv', index=False)
    # Derived figures and summaries depend on this manifest. Excluding them
    # keeps a cached audit followed by summarization free of circular hashes.
    derived = {'audit.json', 'summary_manifest.json', 'supply_summary.csv',
               'selected_witnesses.csv', 'supplied_stress_fraction.png'}
    audit = {'elapsed_seconds': time.monotonic()-started, 'workers': args.workers,
        'audit_script_sha256': sha256_file(Path(__file__)),
        'output_hashes': {str(p.relative_to(args.output)): sha256_file(p) for p in sorted(args.output.rglob('*')) if p.is_file() and p.name not in derived}}
    (args.output/'audit.json').write_text(json.dumps(audit, indent=2)+'\n')
    print(f'audit complete in {audit["elapsed_seconds"]:.1f} s', flush=True)


if __name__ == '__main__':
    main()
