#!/usr/bin/env python3
"""Audit the compact equilibrium and compare its leading local cloud response."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import json
import multiprocessing
from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy.integrate import cumulative_simpson, quad, simpson
from scipy.optimize import brentq, minimize_scalar

from adm_harness.gravitating_atmosphere import (AtmosphereParameters,
    solve_atmosphere, atmosphere_profile, surface_match)
from adm_harness.one_sided_screening import (one_sided_cloud, cloud_stiffness_ratio,
    independent_energy_ratio, independent_response_bvp)
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]


def response_task(q):
    energy = independent_energy_ratio(q)
    bvp = independent_response_bvp(q, 1e-10)
    exact = float(cloud_stiffness_ratio(q))
    return {'q': q, 'analytic_ratio': exact, **energy, **bvp,
        'energy_absolute_error': abs(energy['energy_stiffness_ratio']-exact),
        'bvp_absolute_error': abs(bvp['bvp_stiffness_ratio']-exact)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--input', type=Path, default=ROOT/'supporting_reports/data/gravitating_atmosphere')
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/gravitating_atmosphere_audit')
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    started = time.monotonic()
    manifest = json.loads((args.input/'manifest.json').read_text())
    checks = []

    def check(name, value):
        checks.append({'check': name, 'passed': bool(value)})

    for name, expected in manifest['input_sha256'].items():
        check('source hash '+name, sha256_file(ROOT/name) == expected)
    for name, expected in manifest['output_sha256'].items():
        check('output hash '+name, sha256_file(args.input/name) == expected)
    selected = manifest['selected_equilibrium']
    p = AtmosphereParameters()
    solution = solve_atmosphere(p, selected['adm_mass_ratio'], method='Radau', rtol=2e-12)
    match = surface_match(p, solution)
    a = atmosphere_profile(p, solution, 8001)
    r, f, alpha = a['radius'], a['metric_f'], a['lapse']
    check('independent integrator preserves charge-constrained gas match',
          abs(match['scaled_matching_residual']) < 1e-9)
    check('independent integrator preserves tensile positive-energy wall',
          match['tensile_wall'] and match['positive_components'])
    integrated_charge = p.charge*simpson(4*np.pi*r*r*a['screening_number_density']/np.sqrt(f), x=r)
    integrated_mass = simpson(4*np.pi*r*r*a['total_energy_density'], x=r)
    check('independent proper particle integral neutralizes wall',
          abs(integrated_charge/match['wall_charge']-1) < 2e-9)
    check('independent energy integral reproduces atmosphere ADM mass',
          abs(integrated_mass/match['cloud_adm_mass']-1) < 2e-9)
    check('screening Klein integral remains constant',
          np.max(abs(a['klein_energy']/a['klein_energy'][-1]-1)) < 1e-10)
    check('all atmosphere points are outside a horizon', np.min(f) > 0)
    check('cold compact edge is neutral and empty', a['charge'][-1] == a['fermi_momentum'][-1] == 0)
    check('gas and electric fields satisfy dominant energy inequalities',
          np.all(a['total_energy_density'] >= np.maximum(abs(a['radial_pressure']), abs(a['tangential_pressure']))))

    # Momentum-space quadrature independently checks the physical normalization.
    eos_rows = []
    for index in [0, 500, 2000, 4000, 7000]:
        momentum, rest = a['fermi_momentum'][index], match['screening_rest_mass']
        energy = p.eta/np.pi**2*quad(lambda q: q*q*np.hypot(q, rest), 0, momentum)[0]
        pressure = p.eta/(3*np.pi**2)*quad(lambda q: q**4/np.hypot(q, rest), 0, momentum)[0]
        ee = abs(energy/a['gas_energy_density'][index]-1)
        pe = abs(pressure/a['gas_pressure'][index]-1)
        eos_rows.append({'radius': r[index], 'energy_relative_error': ee, 'pressure_relative_error': pe})
        check('momentum quadrature at index '+str(index), max(ee, pe) < 1e-8)

    inside_s = np.sqrt(1-(p.throat/p.radius)**2)
    outside_s = np.sqrt(f[0])
    outside_acceleration = outside_s*match['wall_log_lapse_slope']/p.radius
    normal_jump = a['radial_pressure'][0]+p.throat**2/(8*np.pi*p.radius**4)
    surface_force = -match['surface_energy']*outside_acceleration/2
    surface_force += match['surface_pressure']*(inside_s+outside_s)/p.radius
    check('normal junction force matches both bulk radial stresses', abs(normal_jump-surface_force) < 1e-14)

    context = multiprocessing.get_context('spawn')
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=context) as pool:
        response = list(pool.map(response_task, [.05, .1, .2, .5, 1., 2., 3., 5., 10., 30.]))
    for row in response:
        check('independent local response q='+str(row['q']),
              row['energy_absolute_error'] < 1e-8 and row['bvp_absolute_error'] < 5e-7)

    cloud = one_sided_cloud(match['wall_number_per_area'], p.eta, p.charge)
    proper = cumulative_simpson(1/np.sqrt(f), x=r, initial=0)
    local_rows = []
    for width in [.025, .05, .1]:
        for ell in range(10, 81):
            k = np.sqrt(ell*(ell+1))/p.radius
            q = k*cloud['cloud_length']
            cloud_coefficient = cloud['cloud_pressure']*float(cloud_stiffness_ratio(q))
            tension = -match['surface_pressure']
            gravity_ratio = 8*np.pi*a['total_energy_density'][0]/k**2
            mass_ratio = match['screening_rest_mass']/match['screening_chemical_at_wall']
            local_window = (k*width <= .2 and k*p.radius >= 10 and
                k/a['fermi_momentum'][0] <= .2 and gravity_ratio <= .05 and
                width/cloud['cloud_length'] <= .2 and cloud['cloud_length']/p.radius <= .1 and
                mass_ratio <= .25)
            probe = np.linspace(0, min(cloud['cloud_length'], 1/k), 101)
            actual_mu = np.interp(probe, proper, a['chemical_potential'])
            planar_mu = cloud['chemical_at_wall']/(1+probe/cloud['cloud_length'])
            local_rows.append({'width': width, 'angular_index': ell, 'wave_number': k,
                'q': q, 'k_width': k*width, 'k_radius': k*p.radius,
                'k_over_screening_momentum': k/a['fermi_momentum'][0],
                'gravitational_curvature_proxy_over_k_squared': gravity_ratio,
                'screening_mass_over_chemical': mass_ratio,
                'local_estimate_window': local_window,
                'chemical_profile_maximum_relative_difference': float(np.max(abs(planar_mu/actual_mu-1))),
                'wall_tension_coefficient': tension, 'cloud_coefficient': cloud_coefficient,
                'local_total_stiffness': k*k*(tension+cloud_coefficient),
                'destabilizing_cloud_over_wall_tension': -cloud_coefficient/tension})
    modes = pd.DataFrame(local_rows)
    kept = modes[modes.local_estimate_window]
    check('local estimate window contains sampled ripples', len(kept) > 0)
    check('registered local estimates retain negative deformation stiffness',
          np.all(kept.local_total_stiffness < 0))
    crossing = brentq(lambda k: -match['surface_pressure']+
        cloud['cloud_pressure']*cloud_stiffness_ratio(k*cloud['cloud_length']), 1., 1000.)

    # A gravitational well can bind escaped heavy particles even when their
    # energy lies below the continuum at infinity. Check the whole exterior.
    heavy_chemical = (match['wall_fermi_energy_at_infinity']-a['electric_potential_energy'])/alpha

    def negative_heavy_chemical(t):
        u, z, mass, phi, potential = solution.sol(t)
        electric_energy = p.chemical_scale*potential/p.radius
        return -(match['wall_fermi_energy_at_infinity']-electric_energy)/np.exp(phi)

    optimum = minimize_scalar(negative_heavy_chemical, bounds=(0., np.log(p.edge_ratio)),
                              method='bounded', options={'xatol': 1e-13})
    bulk_exclusion_mass = max(-optimum.fun, heavy_chemical[0], heavy_chemical[-1],
                              match['wall_fermi_energy_at_infinity'])
    check('independent optimization resolves heavy-particle gravitational well',
          optimum.success and abs(np.max(heavy_chemical)/bulk_exclusion_mass-1) < 1e-6 and
          bulk_exclusion_mass > max(heavy_chemical[0], heavy_chemical[-1]))
    confinement = []
    for width in [.025, .05, .1]:
        v2 = 3*match['wall_tension']*width/(4*p.eta)
        escape_mass = max(match['wall_fermi_momentum'], match['wall_fermi_energy_at_infinity'])
        exclusion_yukawa = (match['screening_chemical_at_wall']-match['screening_rest_mass'])/(2*np.sqrt(v2))
        confinement.append({'width': width, 'scalar_v': np.sqrt(v2),
            'asymptotic_escape_mass_necessary_lower_bound': escape_mass,
            'bulk_exclusion_mass_local_density_lower_bound': bulk_exclusion_mass,
            'collective_yukawa_local_density_lower_bound': p.flavors*bulk_exclusion_mass**2/(16*np.pi**2*v2),
            'interior_screening_mass_necessary_lower_bound': match['screening_chemical_at_wall'],
            'linear_mass_contrast_yukawa_necessary_lower_bound': exclusion_yukawa})

    args.output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(response).to_csv(args.output/'response_checks.csv', index=False)
    pd.DataFrame(eos_rows).to_csv(args.output/'momentum_quadrature.csv', index=False)
    pd.DataFrame(confinement).to_csv(args.output/'confinement_thresholds.csv', index=False)
    modes.to_csv(args.output/'local_response_estimates.csv', index=False)
    report = {'created_utc': datetime.now(timezone.utc).isoformat(), 'workers': args.workers,
        'seconds': time.monotonic()-started, 'input_manifest_sha256': sha256_file(args.input/'manifest.json'),
        'source_sha256': {str(path.relative_to(ROOT)): sha256_file(path) for path in
            [Path(__file__).resolve(), ROOT/'toolkit/adm_harness_cli/adm_harness/one_sided_screening.py',
             ROOT/'toolkit/adm_harness_cli/adm_harness/screened_wall.py']},
        'checks': checks, 'passed': sum(row['passed'] for row in checks),
        'failed': sum(not row['passed'] for row in checks),
        'local_comparison_cloud': cloud, 'normal_force_absolute_error': abs(normal_jump-surface_force),
        'local_estimate_mode_count': len(kept), 'local_estimate_negative_count': int(sum(kept.local_total_stiffness < 0)),
        'minimum_cloud_over_tension_in_window': float(kept.destabilizing_cloud_over_wall_tension.min()),
        'maximum_chemical_profile_difference_in_window': float(kept.chemical_profile_maximum_relative_difference.max()),
        'formal_planar_crossing_wave_number': crossing,
        'formal_crossing_k_over_screening_momentum': crossing/a['fermi_momentum'][0],
        'formal_crossing_maximum_width_for_kd_point2': .2/crossing,
        'heavy_particle_bulk_exclusion_mass': bulk_exclusion_mass,
        'heavy_particle_chemical_maximum_radius': p.radius*np.exp(optimum.x),
        'full_curved_response_evaluated': False, 'finite_width_confinement_evaluated': False,
        'absolute_quantum_stress_evaluated': False,
        'output_sha256': {path.name: sha256_file(path) for path in args.output.iterdir()}}
    (args.output/'audit.json').write_text(json.dumps(report, indent=2)+'\n')
    if report['failed']:
        raise RuntimeError('audit checks failed: '+str([r for r in checks if not r['passed']]))
    print(json.dumps({k: v for k, v in report.items() if k not in
        ['checks', 'source_sha256', 'output_sha256']}, indent=2))


if __name__ == '__main__':
    main()
