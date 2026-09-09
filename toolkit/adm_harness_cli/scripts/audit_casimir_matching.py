#!/usr/bin/env python3
"""Adaptive-integral and two-sheet Green-function audit of matched masses."""
from concurrent.futures import ProcessPoolExecutor
import argparse
import hashlib
import json
import math
import multiprocessing
from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[3]


def adaptive_interaction(row):
    first, second = row['lambda1'], row['lambda2']
    # A weak sheet opposite a strong one has energy of order lambda_weak,
    # whereas two weak sheets scale as their product. Normalize both regimes
    # before the adaptive routine applies its absolute error threshold.
    scale = min(1., first, second, first*second)
    breaks = sorted(set([0., 1., 5., 20., 80.]+[x for x in [first, second] if 0 < x < 80]))
    def integrand(y, component):
        if y == 0.:
            return 0.
        logt = -y-math.log1p(y/first)-math.log1p(y/second)
        denominator = -math.expm1(logt)
        odds = math.exp(logt)/denominator
        magnitude = -math.log(denominator) if logt > -.5 else -math.log1p(-math.exp(logt))
        return (y*y*magnitude if component == 0 else y**3*odds)/scale
    integrals = [sum(quad(integrand, low, high, args=(component,), epsabs=2e-12, epsrel=2e-11, limit=160)[0]
                      for low, high in zip(breaks[:-1], breaks[1:]))*scale/(32*np.pi**2) for component in [0, 1]]
    energy, pressure = -integrals[0], -integrals[1]
    # Surface binding from the change of the Green function on each sheet.
    def surface_integrand(u):
        k = math.exp(u)
        r1, r2 = first/(2*k+first), second/(2*k+second)
        determinant = -math.expm1(-2*k-math.log1p(2*k/first)-math.log1p(2*k/second))
        dg1 = -2*k*r2*math.exp(-2*k)/((2*k+first)**2*determinant)
        dg2 = -2*k*r1*math.exp(-2*k)/((2*k+second)**2*determinant)
        return k**3*(first*dg1+second*dg2)/(4*np.pi**2*scale)
    surface = quad(surface_integrand, -30., math.log(80.), epsabs=2e-12, epsrel=2e-11, limit=160)[0]*scale
    energy_error = abs(energy-row['energy'])/abs(energy)
    pressure_error = abs(pressure-row['pressure'])/abs(pressure)
    return {'lambda1': first, 'lambda2': second, 'energy': energy, 'pressure': pressure,
        'relative_energy_error': energy_error, 'relative_pressure_error': pressure_error,
        'canonical_surface_binding': surface, 'held_floor': energy-pressure,
        'passed': bool(energy_error < 2e-9 and pressure_error < 2e-9 and energy-pressure > 0)}


def green_profile(row):
    first, second, z, xi = row['lambda1'], row['lambda2'], row['fraction'], row['xi']
    def primitive(u, component):
        k = math.exp(u)
        vacuum = np.array([[1., math.exp(-k)], [math.exp(-k), 1.]])/(2*k)
        matrix = vacuum+np.diag([1/first, 1/second])
        v = np.exp(-k*np.array([z, 1-z]))/(2*k)
        derivative = k*v*np.array([-1., 1.])
        vv = float(v@np.linalg.solve(matrix, v))
        dd = float(derivative@np.linalg.solve(matrix, derivative))
        green, cross, coincident_second = -vv, -dd, -2*(dd+k*k*vv)
        density = .5*(k*k*green/3+cross)-xi*coincident_second
        pressure = .5*(-k*k*green+cross)
        return k**3/(2*np.pi**2)*(density if component == 0 else pressure)
    values = [quad(primitive, -30., math.log(800.), args=(component,), epsabs=2e-12,
                   epsrel=2e-10, limit=160)[0] for component in [0, 1]]
    scale = max(abs(row['energy']), abs(row['normal_pressure']), 1e-30)
    error = max(abs(values[0]-row['energy']), abs(values[1]-row['normal_pressure']))/scale
    return {'lambda1': first, 'lambda2': second, 'xi': xi, 'fraction': z,
            'green_energy': values[0], 'green_pressure': values[1],
            'max_normalized_channel_error': error, 'passed': bool(error < 2e-8)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/casimir_mass_matching')
    args = parser.parse_args()
    started = time.monotonic()
    manifest = json.loads((args.output/'manifest.json').read_text())
    source_match = all(hashlib.sha256((ROOT/key).read_bytes()).hexdigest() == value
                       for key, value in manifest['source_hashes'].items())
    data = pd.read_csv(args.output/'interaction_summaries.csv', float_precision='round_trip')
    finest = data[data.nodes.eq(512)]
    profiles = pd.read_csv(args.output/'gap_profiles.csv.gz', float_precision='round_trip')
    chosen = profiles[profiles.nodes.eq(512) & profiles.fraction.apply(lambda z: any(np.isclose(z, x) for x in [.1, .35, .5, .9]))]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        checks = pd.DataFrame(pool.map(adaptive_interaction, finest.to_dict('records')))
        local = pd.DataFrame(pool.map(green_profile, chosen.to_dict('records')))
    checks.to_csv(args.output/'independent_interactions.csv', index=False)
    local.to_csv(args.output/'independent_gap_stresses.csv', index=False)
    partitions = pd.read_csv(args.output/'boundary_partitions.csv', float_precision='round_trip')
    canonical = partitions[partitions.xi.eq(0.)].merge(checks, on=['lambda1', 'lambda2'])
    surface_error = float((abs(canonical.surface-canonical.canonical_surface_binding)/abs(canonical.energy)).max())
    partition_error = float((abs(partitions.total-partitions.interaction_energy)/abs(partitions.interaction_energy)).max())
    refinement = []
    for nodes in [128, 256]:
        comparison = data[data.nodes.eq(nodes)].merge(finest, on=['lambda1', 'lambda2'], suffixes=('_coarse', '_fine'))
        refinement.append({'nodes': nodes, 'max_relative_energy_difference': float((abs(comparison.energy_coarse-comparison.energy_fine)/abs(comparison.energy_fine)).max()),
            'max_relative_pressure_difference': float((abs(comparison.pressure_coarse-comparison.pressure_fine)/abs(comparison.pressure_fine)).max())})
    pd.DataFrame(refinement).to_csv(args.output/'quadrature_refinement.csv', index=False)
    reference = pd.read_csv(args.output/'rail_placement_profile.csv.gz', float_precision='round_trip')
    original = pd.read_csv(ROOT/'supporting_reports/data/comer_two_current/reference_initial_profile.csv', float_precision='round_trip')
    rail_unchanged = bool(np.array_equal(reference.to_numpy(), original.to_numpy()))
    placement = json.loads((args.output/'rail_placement.json').read_text())
    mass_difference_error = abs(placement['endpoint_mass_change']-placement['coordinate_mass'])
    angular_negative = int(((reference.energy+reference.angular_pressure) < 0).sum())
    positive_with_negative_radial = int(((reference.energy > 0)&(reference.radial_enthalpy < 0)).sum())
    gap_angular_enthalpy_error = float(abs(profiles.energy+profiles.transverse_pressure).max())
    passed = bool(source_match and checks.passed.all() and local.passed.all()
                  and surface_error < 2e-9 and partition_error < 2e-9 and rail_unchanged and mass_difference_error < 1e-7)
    result = {'elapsed_seconds': time.monotonic()-started, 'workers': args.workers,
        'source_hashes_match': source_match, 'rail_profile_unchanged': rail_unchanged,
        'interaction_pairs_checked': len(checks), 'green_function_stresses_checked': len(local),
        'max_relative_energy_error': float(checks.relative_energy_error.max()),
        'max_relative_pressure_error': float(checks.relative_pressure_error.max()),
        'max_normalized_green_stress_error': float(local.max_normalized_channel_error.max()),
        'max_normalized_surface_binding_error': surface_error,
        'max_normalized_partition_error': partition_error,
        'mass_endpoint_vs_density_integral_error': mass_difference_error,
        'negative_rail_angular_enthalpy_points': angular_negative,
        'positive_rail_energy_points_with_negative_radial_enthalpy': positive_with_negative_radial,
        'max_gap_angular_enthalpy': gap_angular_enthalpy_error,
        'all_passed': passed, 'audit_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'method': 'Adaptive material-scale quadrature, direct two-by-two Green resolvent, explicit surface binding, fixed-input rail mass identity.'}
    (args.output/'audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
