#!/usr/bin/env python3
"""Measure the necessary integrated Einstein balance for quantum feedback."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import argparse
import json
import multiprocessing
import resource
import time

import numpy as np
import pandas as pd
from scipy.integrate import simpson
from scipy.interpolate import PchipInterpolator
from scipy.special import zeta

from adm_harness.condensate_vacuum import JoinedProfile
from adm_harness.curved_boundary import frequency_quadrature
from adm_harness.semiclassical_feedback import ProfileRadialControl
from adm_harness.semiclassical_joint import (SmoothJointSeed, heavy_coefficients,
    vacuum_finite_coefficients, local_action_source, flat_renormalized_source)
from adm_harness.semiclassical_material import UpdatedMaterialSeed
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
PROBLEM = OPTIONS = None


def initialize(problem, options):
    global PROBLEM, OPTIONS
    PROBLEM, OPTIONS = problem, options


def mode_sum(harmonic):
    p, options = PROBLEM, OPTIONS
    clocks = p.lapse[p.probes]
    frequencies, weights = frequency_quadrature(options['frequency_nodes'],
        options['local_frequency_upper']*max(clocks), 1e-6*min(clocks))
    result = np.zeros((len(options['regulators']), len(p.probes), 4), np.longdouble)
    flat = np.array([p.flat_references(frequencies, harmonic, scale)
                    for scale in options['regulators']])
    for n, (frequency, weight) in enumerate(zip(frequencies, weights)):
        if time.monotonic() > options['deadline']:
            raise TimeoutError('registered joint-feedback mode budget exhausted')
        active = frequency/clocks <= options['local_frequency_upper']
        for k, scale in enumerate(options['regulators']):
            result[k, active] += weight*(p.mode(frequency, harmonic, scale)[active]-flat[k, n, active])
    return harmonic, result*(2*harmonic+1)/(4*np.pi**2), resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def angular_tail(moments):
    last = len(moments)-1
    nu = np.arange(2*last//3, last+1)+.5
    powers = np.array([5, 7, 9, 11])
    matrix = (last/nu[:, None])**powers
    coefficients = np.linalg.lstsq(matrix, moments[2*last//3:].reshape(len(nu), -1), rcond=None)[0]
    return ((float(last)**powers*zeta(powers, last+1.5))@coefficients).reshape(moments.shape[1:])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--spacing', type=float, default=.005)
    parser.add_argument('--width', type=float, default=.25)
    parser.add_argument('--seed-spacing', type=float, default=.025)
    parser.add_argument('--end-coordinate', type=float, default=48.)
    parser.add_argument('--angular-max', type=int, default=128)
    parser.add_argument('--frequency-nodes', type=int, default=224)
    parser.add_argument('--local-frequency-upper', type=float, default=128.)
    parser.add_argument('--regulators', type=float, nargs='+', default=[4., 8.])
    parser.add_argument('--budget-seconds', type=float, default=900.)
    parser.add_argument('--material', type=Path)
    parser.add_argument('--witness-refinement', type=int, default=1)
    args = parser.parse_args()
    if (not 1 <= args.workers <= 6 or args.witness_refinement not in (1, 2, 4)
            or args.spacing <= 0 or args.angular_max < 32 or args.budget_seconds <= 0):
        parser.error('one to six workers, resolved mesh/harmonics, and positive budget required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    started = time.monotonic()
    profile = JoinedProfile(ROOT)
    seed = SmoothJointSeed(profile, args.width, args.seed_spacing)
    if args.material:
        checks = json.loads((args.material.parent/'checks.json').read_text())
        if not checks['accepted'] or sha256_file(args.material) != checks['output_hashes'][args.material.name]:
            raise ValueError('material archive failed its acceptance or hash check')
        with np.load(args.material) as saved:
            if float(saved['width']) != args.width or float(saved['seed_spacing']) != args.seed_spacing:
                raise ValueError('material and metric seed parameters must agree')
            seed = UpdatedMaterialSeed(seed, saved['proper'], saved['amplitudes'])
    witnesses = np.unique(np.r_[-40., -30., np.arange(-20., -6., .5),
        np.arange(-6., -2., .125), np.arange(-2., 2., .25),
        np.arange(2., 6., .125), np.arange(6., 20.01, .5), 30., 40.])
    if args.witness_refinement > 1:
        fractions = np.arange(args.witness_refinement)/args.witness_refinement
        witnesses = np.r_[(witnesses[:-1, None]+np.diff(witnesses)[:, None]*fractions).ravel(), witnesses[-1]]
    problem = ProfileRadialControl.from_seed(seed, witnesses, args.spacing, args.end_coordinate)
    sources = [Path(__file__).resolve(), profile.path, *[ROOT/'toolkit/adm_harness_cli/adm_harness'/name
        for name in ('semiclassical_joint.py', 'semiclassical_feedback.py', 'absolute_vacuum_control.py',
        'condensate_vacuum.py', 'condensate_joint.py', 'condensate_rail.py', 'curved_boundary.py',
        'screened_condensate.py', 'semiclassical_material.py')], ROOT/'supporting_reports/data/curved_quantum_boundary/geometry.npz']
    if args.material:
        sources.extend([args.material.resolve(), (args.material.parent/'checks.json').resolve()])
    def key(path):
        return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    hashes = {key(p): sha256_file(p) for p in sources}
    print(f'{len(problem.coordinate)} nodes; {len(problem.probes)} observations', flush=True)
    moments = np.zeros((args.angular_max+1, len(args.regulators), len(problem.probes), 4), np.longdouble)
    peak, last = 0, started
    options = {**vars(args), 'deadline': started+args.budget_seconds}
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn'),
            initializer=initialize, initargs=(problem, options)) as pool:
        for done, future in enumerate(as_completed([pool.submit(mode_sum, j)
                for j in range(args.angular_max+1)]), 1):
            j, result, rss = future.result(); moments[j] = result; peak = max(peak, rss)
            if time.monotonic()-last > 15 or done == args.angular_max+1:
                print(f'{done}/{args.angular_max+1}; {time.monotonic()-started:.1f} s', flush=True)
                last = time.monotonic()
    l = problem.coordinate[problem.probes]
    x = seed.coordinate_of_proper(l)
    jets = seed.jets(l)
    mu2 = 1.4*profile.v**2
    h = jets[:, 3]
    vjets = mu2*np.array([h[0]**2, 2*h[0]*h[1], 2*(h[1]**2+h[0]*h[2]),
                         np.zeros_like(l), np.zeros_like(l)])
    coefficients = vacuum_finite_coefficients(mu2); coefficients[:3] = 0.
    finite = local_action_source(jets[:, 0], jets[:, 1], vjets, coefficients).T
    flat = flat_renormalized_source(vjets[0], mu2).T
    tail = angular_tail(moments.astype(float))
    raw = moments.sum(axis=0).astype(float)
    estimates = []
    records = []
    for i, scale in enumerate(args.regulators):
        coefficients = heavy_coefficients(scale, mu2); coefficients[:3] = 0.
        heavy = local_action_source(jets[:, 0], jets[:, 1], vjets, coefficients).T
        estimate = raw[i]+tail[i]+flat-heavy+finite
        estimates.append(estimate)
        for n, proper in enumerate(l):
            records.append({'regulator': scale, 'proper': proper, 'coordinate': x[n],
                'radius': np.exp(jets[0, 0, n]), 'lapse': np.exp(jets[0, 1, n]),
                'rho': estimate[n, 0], 'pr': estimate[n, 1], 'pt': estimate[n, 2],
                'polarization': estimate[n, 3], 'radial_enthalpy': estimate[n, 0]+estimate[n, 1],
                'radial_enthalpy_tail': tail[i, n, 0]+tail[i, n, 1],
                'required_radial_enthalpy': seed.demanded_tensor(proper)[:2].sum()})
    integration_l = np.linspace(l[0], l[-1], 48001)
    r, a, _ = seed.values(integration_l)
    einstein = seed.demanded_tensor(integration_l)
    endpoint_jets = seed.jets([l[0], l[-1]], 1)
    slope_clock = np.exp(endpoint_jets[0, 0]-endpoint_jets[0, 1])*endpoint_jets[1, 0]
    demanded_balance = float(np.diff(slope_clock)[0])
    geometric_integral = -4*np.pi*simpson(r/a*(einstein[0]+einstein[1]), x=integration_l)
    balances = []
    for scale, estimate in zip(args.regulators, estimates):
        q = PchipInterpolator(l, estimate[:, 0]+estimate[:, 1])(integration_l)
        signed = -4*np.pi*profile.eta*simpson(r/a*q, x=integration_l)
        available = 4*np.pi*profile.eta*simpson(r/a*np.maximum(-q, 0.), x=integration_l)
        balances.append({'regulator': scale, 'required_opening_balance': demanded_balance,
            'geometric_integral': geometric_integral, 'signed_quantum_balance': signed,
            'maximum_quantum_opening_balance': available,
            'fraction_of_required_balance': available/demanded_balance,
            'required_weight_amplification_at_frozen_quantum_source': demanded_balance/available})
    args.output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(args.output/'source_profile.csv', index=False)
    pd.DataFrame(balances).to_csv(args.output/'opening_balance.csv', index=False)
    np.savez_compressed(args.output/'angular_sums.npz', moments=moments.astype(float), proper=l)
    for path in sources:
        if sha256_file(path) != hashes[key(path)]:
            raise RuntimeError('source changed during computation: '+str(path))
    manifest = {**vars(args), 'output': str(args.output),
        'material': str(args.material) if args.material else None, 'eta': profile.eta,
        'elapsed_seconds': time.monotonic()-started, 'worker_peak_rss_kib': peak,
        'scope': 'Necessary integrated Einstein balance for a frozen quantum update; full nonlinear fixed point remains separate',
        'nodes': len(problem.coordinate), 'probes': len(l), 'source_hashes': hashes,
        'geometric_integral_relative_error': abs(geometric_integral/demanded_balance-1),
        'output_hashes': {p.name: sha256_file(p) for p in args.output.iterdir()}}
    (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(pd.DataFrame(balances).to_string(index=False), flush=True)


if __name__ == '__main__':
    main()
