#!/usr/bin/env python3
"""Audit retained screening response, energy accounting, and junction bounds."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import argparse
import json
import multiprocessing
from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy.optimize import brentq, minimize_scalar

from adm_harness.screened_wall import independent_response_bvp, independent_response_energy
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]


def energy_crossing(task):
    """Locate K=0 using integrated deformation energy, without analytic kernel."""
    flavors, beta = task
    if beta <= 1:
        return {'flavors': flavors, 'beta': beta, 'finite_crossing': False,
                'energy_q_crossing': np.nan, 'bvp_stiffness_at_crossing': np.nan}
    function = lambda q: -1+beta*(1+independent_response_energy(q)['cloud_stiffness_ratio'])
    q = brentq(function, .001, 500., xtol=2e-11)
    residual = -1+beta*(1+independent_response_bvp(q, 1e-10)['cloud_stiffness_ratio'])
    return {'flavors': flavors, 'beta': beta, 'finite_crossing': True,
            'energy_q_crossing': q, 'bvp_stiffness_at_crossing': residual}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--input', type=Path, default=ROOT/'supporting_reports/data/screened_charged_wall')
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/screened_charged_wall_audit')
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    started = time.monotonic()
    manifest = json.loads((args.input/'manifest.json').read_text())
    # Near-horizon control rows amplify a one-ulp mass parse change. Preserve
    # the written floating-point inputs before reconstructing their junction.
    tables = {name: pd.read_csv(args.input/name, float_precision='round_trip') for name in
        ['response_checks.csv', 'cloud_integrals.csv', 'junction_scan.csv.gz',
         'registered_modes.csv.gz', 'selected_matches.csv', 'response_curve.csv']}
    hashes = {p.name: sha256_file(p) for p in sorted(args.input.iterdir()) if p.is_file()}
    checks = {f'source:{path}': sha256_file(ROOT/path) == digest
              for path, digest in manifest['source_hashes'].items()}
    response = tables['response_checks.csv']
    fine = response[response.bvp_tolerance == 1e-10]
    coarse = response[response.bvp_tolerance == 1e-6]
    checks['poisson_force_maximum_error'] = fine.bvp_absolute_error.max() < 5e-9
    checks['poisson_refinement_reduces_maximum_error'] = (
        fine.bvp_absolute_error.max() < coarse.bvp_absolute_error.max()/100)
    checks['energy_force_agreement'] = response.energy_absolute_error.max() < 2e-10
    checks['pressure_free_control_has_positive_shape_energy'] = (1+response.energy_cloud_stiffness_ratio > 0).all()
    integrals = tables['cloud_integrals.csv']
    for column in integrals:
        if column.endswith('_relative_error'):
            checks['integral:'+column] = integrals[column].max() < 1e-10
    checks['cloud_normal_stress_cancels'] = (integrals.normal_pressure == 0).all()

    r, b = manifest['radius'], manifest['throat']
    mass = tables['junction_scan.csv.gz']
    inside, outside = np.sqrt(1-b*b/r**2), np.sqrt(1-2*mass.exterior_mass/r)
    sigma = (inside-outside)/(4*np.pi*r)
    pressure = ((outside+1/outside)/2-inside)/(8*np.pi*r)
    counted_sigma = mass.wall_tension+mass.fermi_energy+mass.cloud_energy
    counted_pressure = -mass.wall_tension+(mass.fermi_energy+mass.cloud_energy)/2
    checks['counted_energy_matches_israel'] = np.max(abs(counted_sigma-sigma)) < 1e-14
    checks['counted_pressure_matches_israel'] = np.max(abs(counted_pressure-pressure)) < 1e-13
    checks['cloud_energy_pressure_identity'] = np.allclose(mass.cloud_energy, 2*mass.cloud_pressure, rtol=1e-12)
    checks['all_flavors_have_registered_mass_grid'] = list(mass.groupby('flavors').size()) == [2001]*4

    def pressure_to_energy(m):
        outside = np.sqrt(1-2*m/r)
        return ((outside+1/outside)/2-inside)/(2*(inside-outside))

    opt = minimize_scalar(pressure_to_energy, bounds=(.46, 2.96), method='bounded',
                          options={'xatol': 1e-13})
    bound = manifest['global_bound']
    checks['independent_optimal_mass'] = abs(opt.x-bound['best_exterior_mass']) < 2e-7
    checks['independent_minimum_pressure_ratio'] = abs(opt.fun-bound['minimum_pressure_to_energy']) < 2e-12
    numerical_beta_max = (1+1/opt.fun)/3
    checks['independent_global_cloud_ceiling'] = abs(numerical_beta_max-bound['maximum_cloud_restoring_ceiling']) < 2e-12
    checks['all_mass_rows_respect_global_cloud_ceiling'] = (
        mass.restoring_ceiling_over_required.max() <= numerical_beta_max)
    for flavors in [1, 4]:
        checks[f'{flavors}_flavors_no_planar_crossing'] = np.isinf(mass.loc[mass.flavors == flavors, 'critical_q']).all()

    selected = tables['selected_matches.csv']
    selected = selected[abs(selected.exterior_mass-bound['best_exterior_mass']) < 1e-10]
    tasks = [(int(row.flavors), float(row.restoring_ceiling_over_required)) for row in selected.itertuples()]
    tasks.append((0, numerical_beta_max))  # zero labels the optimistic cloud-only bound
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        crossings = pd.DataFrame(pool.map(energy_crossing, tasks))
    for row in crossings[crossings.finite_crossing].itertuples():
        expected = bound['minimum_critical_q'] if row.flavors == 0 else float(
            selected.loc[selected.flavors == row.flavors, 'critical_q'].iloc[0])
        checks[f'energy_crossing:{row.flavors}'] = abs(row.energy_q_crossing-expected) < 1e-7
        checks[f'poisson_crossing:{row.flavors}'] = abs(row.bvp_stiffness_at_crossing) < 1e-8

    modes = tables['registered_modes.csv.gz']
    registered = modes[modes.registered_hierarchy]
    checks['registered_mode_count'] = len(registered) == manifest['registered_hierarchy_mode_rows'] == 420
    checks['all_registered_mode_energies_negative'] = (registered.total_static_stiffness < 0).all()
    checks['all_displayed_mode_energies_negative'] = (modes.total_static_stiffness < 0).all()
    checks['counted_mode_stiffness_identity'] = np.allclose(modes.total_static_stiffness,
        modes.additional_stiffness-modes.required_stiffness, atol=1e-14, rtol=1e-12)
    checks['registered_hierarchy_applied'] = np.array_equal(modes.registered_hierarchy,
        (modes.cloud_length_over_radius <= .05)&(modes.width_over_cloud_length <= .2))
    checks['old_local_mode_window_applied'] = ((modes.wave_number*r >= 10)&
        (modes.wave_number*modes.width <= .2+1e-14)).all()
    checks['quartic_false_passes_retained'] = int(((registered.quartic_total_static_stiffness > 0)&
        (registered.total_static_stiffness < 0)).sum()) == manifest['false_quartic_passes_registered_modes'] == 72
    checks['evidence_bound'] = sum(p.stat().st_size for p in args.input.iterdir()) < 5e6
    checks['inputs_unchanged_during_audit'] = all(sha256_file(args.input/name) == digest for name, digest in hashes.items())
    args.output.mkdir(parents=True, exist_ok=True)
    crossings.to_csv(args.output/'independent_crossings.csv', index=False)
    result = {'completed_utc': datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds': time.monotonic()-started, 'workers': args.workers,
        'audit_source_sha256': sha256_file(Path(__file__).resolve()),
        'input_hashes': hashes, 'checks': {key: bool(value) for key, value in checks.items()},
        'passed': bool(all(checks.values())), 'check_count': len(checks),
        'independent_optimal_mass': float(opt.x), 'independent_minimum_pressure_ratio': float(opt.fun)}
    (args.output/'audit.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(result, indent=2, allow_nan=False), flush=True)
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
