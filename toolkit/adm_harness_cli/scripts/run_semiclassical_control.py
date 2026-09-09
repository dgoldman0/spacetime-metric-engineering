#!/usr/bin/env python3
"""Parallel absolute-source regulator controls on one smooth joint seed."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import argparse
import json
import multiprocessing
import resource
import time

import numpy as np
import pandas as pd

from adm_harness.absolute_vacuum_control import AbsoluteRadialControl, flat_mode
from adm_harness.condensate_vacuum import JoinedProfile
from adm_harness.curved_boundary import frequency_quadrature
from adm_harness.semiclassical_joint import (SmoothJointSeed, heavy_coefficients,
    vacuum_finite_coefficients, local_action_source, flat_renormalized_source)
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
PROBLEM = OPTIONS = None


def initialize(problem, options):
    global PROBLEM, OPTIONS
    PROBLEM, OPTIONS = problem, options


def mode_sum(harmonic):
    problem, options = PROBLEM, OPTIONS
    frequencies, weights = frequency_quadrature(options['frequency_nodes'],
        options['frequency_upper'], 1e-6)
    clock = problem.lapse[problem.probe]
    radius = problem.radius[problem.probe]
    potential = problem.potential[problem.probe]
    result = np.zeros((len(options['regulators']), 4), np.longdouble)
    flat = np.array([flat_mode(frequencies, harmonic, scale, radius, potential)
                     for scale in options['regulators']])
    for n, (frequency, weight) in enumerate(zip(frequencies, weights)):
        if time.monotonic() > options['deadline']:
            raise TimeoutError('registered absolute-source mode budget exhausted')
        for k, scale in enumerate(options['regulators']):
            result[k] += weight*(clock*problem.mode(clock*frequency, harmonic, scale,
                options['local_correction'])-flat[k, n])
    return harmonic, result*(2*harmonic+1)/(4*np.pi**2), resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--coordinate', type=float, default=-4.)
    parser.add_argument('--proper-offset', type=float, default=0.)
    parser.add_argument('--spacing', type=float, default=.01)
    parser.add_argument('--far-spacing', type=float, default=.04)
    parser.add_argument('--width', type=float, default=.25)
    parser.add_argument('--seed-spacing', type=float, default=.025)
    parser.add_argument('--extent', type=float, default=180.)
    parser.add_argument('--angular-max', type=int, default=32)
    parser.add_argument('--frequency-nodes', type=int, default=64)
    parser.add_argument('--frequency-upper', type=float, default=32.)
    parser.add_argument('--regulators', type=float, nargs='+', default=[1., 2., 4.])
    parser.add_argument('--budget-seconds', type=float, default=600.)
    parser.add_argument('--flat', action='store_true')
    parser.add_argument('--no-local-correction', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.workers <= 6 or args.angular_max < 0:
        parser.error('one to six workers and nonnegative harmonic limit required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    started = time.monotonic()
    profile = JoinedProfile(ROOT)
    mu2 = 1.4*profile.v**2
    if args.flat:
        problem = AbsoluteRadialControl.flat(spacing=args.spacing,
            far_spacing=args.far_spacing, potential=mu2)
        r = problem.radius[problem.probe]
        rjets = np.array([np.log(r), 1/r, -1/r**2, 2/r**3, -6/r**4])
        ajets, vjets = np.zeros(5), np.array([mu2, 0., 0., 0., 0.])
        required = np.zeros(3)
        proper = r
    else:
        seed = SmoothJointSeed(profile, args.width, args.seed_spacing, args.extent)
        proper = float(seed.proper_of_coordinate(args.coordinate))+args.proper_offset
        problem = AbsoluteRadialControl.from_seed(seed, proper, args.spacing, args.far_spacing)
        jets = seed.jets(proper)
        rjets, ajets = jets[:, 0], jets[:, 1]
        hh = jets[:, 3]
        vjets = mu2*np.array([hh[0]**2, 2*hh[0]*hh[1],
            2*(hh[1]**2+hh[0]*hh[2]), 0., 0.])
        required = seed.demanded_tensor(proper)
    options = {**vars(args), 'local_correction': not args.no_local_correction,
               'deadline': started+args.budget_seconds}
    print(f'{len(problem.coordinate)} nodes; x={args.coordinate}; flat={args.flat}', flush=True)
    moments = np.zeros((args.angular_max+1, len(args.regulators), 4), np.longdouble)
    peak, last = 0, started
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn'),
            initializer=initialize, initargs=(problem, options)) as pool:
        for done, future in enumerate(as_completed([pool.submit(mode_sum, j)
                for j in range(args.angular_max+1)]), 1):
            index, result, rss = future.result()
            moments[index] = result
            peak = max(peak, rss)
            if time.monotonic()-last > 15 or done == args.angular_max+1:
                print(f'{done}/{args.angular_max+1}; {time.monotonic()-started:.1f} s', flush=True)
                last = time.monotonic()
    finite_coefficients = vacuum_finite_coefficients(mu2)
    finite_coefficients[:3] = 0.
    local_finite = local_action_source(rjets, ajets, vjets, finite_coefficients)
    results = []
    for i, scale in enumerate(args.regulators):
        raw = moments[:, i].sum(axis=0).astype(float)
        # Restore the physical flat action exactly. Removing the heavy flat
        # potential to all orders in V changes only terms vanishing as M->inf;
        # stress and polarization receive the same local-action correction.
        exact_flat = flat_renormalized_source(vjets[0], mu2)
        coefficients = heavy_coefficients(scale, mu2)
        coefficients[:3] = 0.
        heavy = local_action_source(rjets, ajets, vjets, coefficients)
        estimate = raw+exact_flat-heavy+local_finite
        results.append({'regulator': scale, **{prefix+name: float(value[k])
            for prefix, value in [('difference_', raw), ('estimate_', estimate)]
            for k, name in enumerate(['rho', 'pr', 'pt', 'polarization'])}})
    args.output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).to_csv(args.output/'estimates.csv', index=False)
    np.savez_compressed(args.output/'angular_sums.npz', moments=moments.astype(float))
    sources = [Path(__file__).resolve(), profile.path,
        ROOT/'toolkit/adm_harness_cli/adm_harness/semiclassical_joint.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/absolute_vacuum_control.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/condensate_vacuum.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/condensate_joint.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/condensate_rail.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/curved_boundary.py',
        ROOT/'supporting_reports/data/curved_quantum_boundary/geometry.npz']
    manifest = {**vars(args), 'output': str(args.output),
        'scope': 'Finite-regulator absolute-source control; continuum and regulator limits pending',
        'elapsed_seconds': time.monotonic()-started, 'worker_peak_rss_kib': peak,
        'nodes': len(problem.coordinate), 'eta': profile.eta,
        'radius': float(problem.radius[problem.probe]), 'lapse': float(problem.lapse[problem.probe]),
        'proper_coordinate': proper, 'log_radius_gradient': float(rjets[1]),
        'log_lapse_gradient': float(ajets[1]), 'mass_squared_gradient': float(vjets[1]),
        'required_tensor': required.tolist(), 'mass_squared': float(vjets[0]),
        'source_hashes': {str(p.relative_to(ROOT)): sha256_file(p) for p in sources},
        'output_hashes': {p.name: sha256_file(p) for p in args.output.iterdir()}}
    (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(pd.DataFrame(results).to_string(index=False), flush=True)


if __name__ == '__main__':
    main()
