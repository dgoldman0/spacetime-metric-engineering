#!/usr/bin/env python3
"""Bounded parallel response and counted-junction scan for a screened wall."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import argparse
import json
import multiprocessing
from pathlib import Path
import resource
import time

import numpy as np
import pandas as pd
from scipy.integrate import quad

from adm_harness.screened_wall import (REFERENCE_CHARGE, cold_cloud, cold_cloud_profile,
    restoring_fraction, independent_response_bvp, independent_response_energy,
    screened_surface_match, critical_cloud_wave_number, junction_restoring_bound)
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]


def response_check(task):
    q, tolerance = task
    started = time.monotonic()
    bvp = independent_response_bvp(q, tolerance)
    energy = independent_response_energy(q)
    exact = -3*(q+1)/(q*q+3*q+3)
    return {'q': q, 'bvp_tolerance': tolerance, 'analytic_cloud_stiffness_ratio': exact,
        'bvp_cloud_stiffness_ratio': bvp['cloud_stiffness_ratio'],
        'energy_cloud_stiffness_ratio': energy['cloud_stiffness_ratio'],
        'bvp_absolute_error': abs(bvp['cloud_stiffness_ratio']-exact),
        'energy_absolute_error': abs(energy['cloud_stiffness_ratio']-exact),
        'bvp_nodes': bvp['nodes'], 'bvp_maximum_residual': bvp['maximum_residual'],
        'quadrature_error_estimate': energy['quadrature_error_estimate'],
        'seconds': time.monotonic()-started,
        'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def cloud_integrals(n):
    cloud = cold_cloud(n)
    a = cloud['cloud_length']
    row = {'sheet_number': n, 'cloud_length': a}
    for key, expected in [('screening_number_density', n),
            ('electric_energy_density', cloud['electric_energy']),
            ('screening_energy_density', cloud['screening_particle_energy']),
            ('energy_density', cloud['cloud_energy']),
            ('tangential_pressure', cloud['cloud_pressure'])]:
        integral, error = quad(lambda x: cold_cloud_profile(a*x, n)[key],
                               0., np.inf, epsabs=1e-12, epsrel=1e-11)
        row[key+'_relative_error'] = abs(2*a*integral/expected-1)
    row['normal_pressure'] = float(cold_cloud_profile(a, n)['normal_pressure'])
    return row


def plots(curve, bound, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.), constrained_layout=True)
    axes[0].plot(curve.q, curve.restoring_fraction, label='Full static TF response')
    axes[0].plot(curve.q, curve.quartic_restoring_fraction, '--', label='Leading bending term')
    axes[0].axhline(1, color='black', linewidth=.7)
    axes[0].set(xscale='log', xlim=(.03, 50), ylim=(0, 1.4), xlabel='Wave number × cloud length, ka',
        ylabel='Additional stiffness / (cloud pressure × k²)', title='Bending benefit saturates')
    ratio = np.geomspace(.005, 2, 400)
    q = ratio*np.sqrt(110)
    b = bound['maximum_cloud_restoring_ceiling']
    axes[1].plot(ratio, b*restoring_fraction(q), color='black', linewidth=2,
                 label='All occupied energy in cloud: upper bound')
    for flavors in [1, 4, 16, 64]:
        m = screened_surface_match(6.8, bound['best_exterior_mass'], flavors)
        axes[1].plot(ratio, m['restoring_ceiling_over_required']*restoring_fraction(q),
                     label=f'{flavors} wall species')
    axes[1].axhline(1, color='black', linewidth=.7, linestyle='--')
    axes[1].axvspan(.005, .05, color='green', alpha=.1, label='Registered a/R ≤ 0.05')
    axes[1].text(.98, .04, 'Broad-cloud crossings are planar extrapolations',
                 transform=axes[1].transAxes, ha='right', fontsize=7)
    axes[1].set(xscale='log', xlim=(.005, 2), ylim=(0, 2.1), xlabel='Cloud length / enclosure radius',
        ylabel='Additional stiffness / required stiffness', title='Longest registered ripple, kR = √110')
    for ax in axes:
        ax.grid(alpha=.2)
        ax.legend(fontsize=7)
    fig.savefig(output, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/screened_charged_wall')
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    started = time.monotonic()
    sources = [Path(__file__).resolve(),
        ROOT/'toolkit/adm_harness_cli/adm_harness/screened_wall.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/smooth_mirror.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/spherical_support.py',
        ROOT/'supporting_reports/data/smooth_quantum_material/manifest.json',
        ROOT/'supporting_reports/data/smooth_quantum_material/shape_modes.csv']
    hashes = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    tasks = [(q, tolerance) for q in [.02, .05, .1, .2, .5, 1., 2., 3., 5., 10., 30.]
             for tolerance in [1e-6, 1e-8, 1e-10]]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        checks = pd.DataFrame(pool.map(response_check, tasks))
        integrals = pd.DataFrame(pool.map(cloud_integrals, [.03, .3, 3., 30.]))

    q = np.geomspace(.001, 100, 501)
    curve = pd.DataFrame({'q': q, 'restoring_fraction': restoring_fraction(q),
        'quartic_restoring_fraction': q*q/3,
        'cloud_stiffness_ratio': -3*(q+1)/(q*q+3*q+3),
        'k_over_screening_fermi_momentum_at_wall': q*REFERENCE_CHARGE/(np.sqrt(6)*np.pi)})
    radius, throat = 6.8, 1.75
    mass = np.linspace(throat**2/(2*radius)+1e-6, radius/2-1e-6, 2001)
    bound = junction_restoring_bound(radius, throat)
    mass_tables, examples = [], []
    for flavors in [1, 4, 16, 64]:
        m = screened_surface_match(radius, mass, flavors)
        qc = critical_cloud_wave_number(m['restoring_ceiling_over_required'])
        mass_tables.append(pd.DataFrame({'exterior_mass': mass, 'flavors': flavors,
            'surface_energy': m['surface_energy'], 'surface_pressure': m['surface_pressure'],
            'wall_tension': m['wall_tension'], 'fermi_energy': m['fermi_energy'],
            'cloud_energy': m['cloud_energy'], 'cloud_pressure': m['cloud_pressure'],
            'cloud_to_fermi_ratio': m['cloud_to_fermi_ratio'],
            'restoring_ceiling_over_required': m['restoring_ceiling_over_required'],
            'critical_q': qc, 'critical_cloud_length_over_radius_at_l10': qc/np.sqrt(110),
            'positive_components': m['positive_components'],
            'conditional_radial_frequency_squared': m['fermi_radial_frequency_squared'],
            'energy_reconstruction_error': m['energy_reconstruction_error'],
            'pressure_reconstruction_error': m['pressure_reconstruction_error']}))
        for chosen_mass in [1.5, bound['best_exterior_mass']]:
            m = screened_surface_match(radius, chosen_mass, flavors)
            qc = float(critical_cloud_wave_number(m['restoring_ceiling_over_required']))
            examples.append({'exterior_mass': chosen_mass, 'flavors': flavors,
                'cloud_to_fermi_ratio': float(m['cloud_to_fermi_ratio']),
                'cloud_energy': float(m['cloud_energy']), 'fermi_energy': float(m['fermi_energy']),
                'restoring_ceiling_over_required': float(m['restoring_ceiling_over_required']),
                'finite_planar_crossing': bool(np.isfinite(qc)),
                'critical_q': qc if np.isfinite(qc) else None,
                'critical_cloud_length_over_radius_at_l10': qc/np.sqrt(110) if np.isfinite(qc) else None})
    mass_table = pd.concat(mass_tables, ignore_index=True)

    previous_modes = pd.read_csv(sources[-1])
    previous_modes = previous_modes[previous_modes.scale_window]
    mode_tables = []
    for flavors in [1, 4, 16, 64]:
        m = screened_surface_match(radius, 1.5, flavors)
        for fraction in [.01, .025, .05, .1]:
            a = fraction*radius
            k = previous_modes.wave_number.to_numpy()
            pc, p = float(m['cloud_pressure']), float(m['surface_pressure'])
            restoring = pc*k*k*restoring_fraction(k*a)
            mode_tables.append(pd.DataFrame({'flavors': flavors, 'cloud_length_over_radius': fraction,
                'cloud_length': a, 'width': previous_modes.width.to_numpy(),
                'angular_index': previous_modes.angular_index.to_numpy(), 'wave_number': k,
                'k_cloud_length': k*a, 'width_over_cloud_length': previous_modes.width.to_numpy()/a,
                'registered_hierarchy': (fraction <= .05)&(previous_modes.width.to_numpy()/a <= .2),
                'required_stiffness': p*k*k, 'additional_stiffness': restoring,
                'total_static_stiffness': -p*k*k+restoring,
                'quartic_total_static_stiffness': -p*k*k+pc*a*a*k**4/3}))
    modes = pd.concat(mode_tables, ignore_index=True)
    args.output.mkdir(parents=True, exist_ok=True)
    for name, frame in [('response_checks.csv', checks), ('cloud_integrals.csv', integrals),
            ('response_curve.csv', curve), ('junction_scan.csv.gz', mass_table),
            ('registered_modes.csv.gz', modes), ('selected_matches.csv', pd.DataFrame(examples))]:
        frame.to_csv(args.output/name, index=False)
    plots(curve, bound, args.output/'screened_wall_response.png')
    for p in sources:
        if sha256_file(p) != hashes[str(p.relative_to(ROOT))]:
            raise RuntimeError(f'input changed during calculation: {p}')
    fine = checks[checks.bvp_tolerance == 1e-10]
    integral_error_columns = [c for c in integrals if c.endswith('_relative_error')]
    registered = modes[modes.registered_hierarchy]
    size = sum(p.stat().st_size for p in args.output.iterdir())
    elapsed = time.monotonic()-started
    if size > 5e6 or elapsed > 600:
        raise RuntimeError('registered evidence or computation allowance exceeded')
    manifest = {'completed_utc': datetime.now(timezone.utc).isoformat(),
        'source_hashes': hashes, 'workers': args.workers, 'elapsed_seconds': elapsed,
        'evidence_bytes_before_manifest': size, 'electric_charge': REFERENCE_CHARGE,
        'radius': radius, 'throat': throat, 'response_tasks': len(checks),
        'maximum_worker_peak_rss_kib': int(checks.peak_rss_kib.max()),
        'fine_bvp_maximum_absolute_error': float(fine.bvp_absolute_error.max()),
        'energy_maximum_absolute_error': float(checks.energy_absolute_error.max()),
        'cloud_integral_maximum_relative_error': float(integrals[integral_error_columns].to_numpy().max()),
        'mass_scan_rows': len(mass_table), 'mass_scan_rows_per_flavor': 2001,
        'positive_material_and_conditional_radial_rows': int((mass_table.positive_components &
            (mass_table.conditional_radial_frequency_squared > 0)).sum()),
        'mode_rows': len(modes), 'registered_hierarchy_mode_rows': len(registered),
        'negative_stiffness_registered_modes': int((registered.total_static_stiffness < 0).sum()),
        'negative_stiffness_all_displayed_modes': int((modes.total_static_stiffness < 0).sum()),
        'false_quartic_passes_all_displayed_modes': int(((modes.quartic_total_static_stiffness > 0)&
            (modes.total_static_stiffness < 0)).sum()),
        'false_quartic_passes_registered_modes': int(((registered.quartic_total_static_stiffness > 0)&
            (registered.total_static_stiffness < 0)).sum()),
        'global_bound': {**bound, 'minimum_cloud_length_over_radius_at_l10': bound['minimum_critical_q']/np.sqrt(110),
            'maximum_restoring_fraction_at_a_over_R_0p05': bound['maximum_cloud_restoring_ceiling']*
                float(restoring_fraction(.05*np.sqrt(110))),
            'maximum_restoring_fraction_at_a_over_R_0p1': bound['maximum_cloud_restoring_ceiling']*
                float(restoring_fraction(.1*np.sqrt(110)))},
        'selected_matches': examples,
        'scope': 'Static planar cold massless Thomas-Fermi cloud; counted leading neutral-composite junction; finite optical wall with charge-sheet approximation requiring d/a and kd small. Registered a/R<=0.05, d/a<=0.2, kR>=10, kd<=0.2.',
        'response_scope': 'Static stiffness, with all cloud electric and particle energy counted. The q curve outside the small-gradient TF regime is a formal model diagnostic. Frequency-dependent cloud response is unevaluated.',
        'outcome': 'Negative deformation energy in the registered thin-cloud hierarchy. Optimistic planar crossing at a/R>=0.299875 for the longest local mode requires a new curved atmosphere construction.'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False)+'\n')
    print(json.dumps(manifest, indent=2, allow_nan=False), flush=True)


if __name__ == '__main__':
    main()
