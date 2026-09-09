#!/usr/bin/env python3
"""Bounded, parallel compact-atmosphere equilibrium and convergence scan."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import json
import multiprocessing
from pathlib import Path
import resource
import time

import numpy as np
import pandas as pd
from scipy.integrate import cumulative_simpson, simpson

from adm_harness.gravitating_atmosphere import (AtmosphereParameters,
    atmosphere_profile, find_surface_equilibrium, solve_atmosphere, surface_match)
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]


def integral_checks(p, solution):
    """Charge, energy, proper distance and Klein checks from the stored fields."""
    a = atmosphere_profile(p, solution, 4001)
    r, f = a['radius'], a['metric_f']
    wall = surface_match(p, solution)
    number = simpson(4*np.pi*r*r*a['screening_number_density']/np.sqrt(f), x=r)
    mass_density = 4*np.pi*r*r*a['total_energy_density']
    cloud_mass = simpson(mass_density, x=r)
    proper = cumulative_simpson(1/np.sqrt(f), x=r, initial=0)
    cumulative = cumulative_simpson(mass_density, x=r, initial=0)
    energy90 = np.interp(.9*cumulative[-1], cumulative, proper)
    number_cumulative = cumulative_simpson(
        4*np.pi*r*r*a['screening_number_density']/np.sqrt(f), x=r, initial=0)
    number90 = np.interp(.9*number_cumulative[-1], number_cumulative, proper)
    expected_klein = p.chemical_scale*p.screening_mass_parameter/p.radius*a['lapse'][-1]
    # Independent anisotropic stress conservation in the smooth exterior.
    dp = np.gradient(a['radial_pressure'], r, edge_order=2)
    dphi = np.gradient(np.log(a['lapse']), r, edge_order=2)
    rhs = -(a['total_energy_density']+a['radial_pressure'])*dphi
    rhs += 2*(a['tangential_pressure']-a['radial_pressure'])/r
    kept = slice(5, -5)
    conservation_error = np.max(np.abs((dp-rhs)[kept]))/np.max(np.abs(rhs[kept]))
    return {'charge_integral_relative_error': float(abs(p.charge*number/wall['wall_charge']-1)),
        'mass_integral_relative_error': float(abs(cloud_mass/wall['cloud_adm_mass']-1)),
        'klein_maximum_relative_error': float(np.max(abs(a['klein_energy']/expected_klein-1))),
        'stress_conservation_relative_error': float(conservation_error),
        'minimum_metric_f': float(np.min(f)),
        'proper_atmosphere_width': float(proper[-1]),
        'proper_mass_90_width': float(energy90), 'proper_number_90_width': float(number90),
        'screening_klein_to_rest_mass': float(a['lapse'][-1]),
        'wall_radial_pressure': float(a['radial_pressure'][0]),
        'wall_gas_energy_density': float(a['gas_energy_density'][0]),
        'wall_electric_energy_density': float(a['electric_energy_density'][0])}


def equilibrium_task(task):
    loading, flavors = task
    started = time.monotonic()
    p = AtmosphereParameters(loading=loading, flavors=flavors)
    roots, rejected = find_surface_equilibrium(p)
    rows = []
    for row, solution in roots:
        rows.append({**row, **integral_checks(p, solution),
            'rejected_search_samples': rejected, 'seconds': time.monotonic()-started,
            'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
    return {'loading': loading, 'flavors': flavors, 'roots': rows,
            'rejected_search_samples': rejected}


def refinement_task(task):
    mass, method, tolerance = task
    p = AtmosphereParameters()
    solution = solve_atmosphere(p, mass, rtol=tolerance, method=method)
    return {'method': method, 'tolerance': tolerance,
        **surface_match(p, solution), **integral_checks(p, solution)}


def plot_profile(profile, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.2), constrained_layout=True)
    r = profile['radius']/profile['radius'][0]
    axes[0].plot(r, profile['mass'], label='Enclosed gravitational mass')
    axes[0].set(xlabel='Areal radius / wall radius', ylabel='Geometric mass')
    axes[1].plot(r, profile['charge']/profile['charge'][0], label='Remaining charge / wall charge')
    axes[1].plot(r, profile['lapse'], label='Lapse')
    axes[1].plot(r, profile['metric_f'], label='1 − 2m/r')
    axes[1].set(xlabel='Areal radius / wall radius')
    for key, label in [('gas_energy_density', 'Gas energy'),
                       ('electric_energy_density', 'Electric energy'),
                       ('radial_pressure', 'Radial pressure')]:
        axes[2].plot(r, profile[key], label=label)
    axes[2].set(xlabel='Areal radius / wall radius', ylabel='Geometric density / pressure')
    for ax in axes:
        ax.legend(fontsize=7)
        ax.grid(alpha=.2)
    fig.savefig(output, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path,
                        default=ROOT/'supporting_reports/data/gravitating_atmosphere')
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    sources = [Path(__file__).resolve(),
        ROOT/'toolkit/adm_harness_cli/adm_harness/gravitating_atmosphere.py']
    hashes = {str(path.relative_to(ROOT)): sha256_file(path) for path in sources}
    started = time.monotonic()
    tasks = [(g, f) for g in [1e-4, 3e-4, 1e-3, 3e-3] for f in [1, 4, 16, 64]]
    context = multiprocessing.get_context('spawn')
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=context) as pool:
        searches = list(pool.map(equilibrium_task, tasks))
        rows = [row for search in searches for row in search['roots']]
        selected = [r for r in rows if r['loading'] == 1e-4 and r['flavors'] == 64]
        if len(selected) != 1:
            raise RuntimeError('registered candidate was not recovered uniquely')
        mass = selected[0]['adm_mass_ratio']
        refinements = list(pool.map(refinement_task, [(mass, method, tol)
            for method in ['DOP853', 'Radau'] for tol in [2e-8, 2e-10, 2e-12]]))
    p = AtmosphereParameters()
    solution = solve_atmosphere(p, mass)
    profile = atmosphere_profile(p, solution)
    args.output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output/'equilibria.csv', index=False)
    pd.DataFrame(refinements).to_csv(args.output/'refinements.csv', index=False)
    pd.DataFrame(profile).to_csv(args.output/'selected_profile.csv.gz', index=False)
    plot_profile(profile, args.output/'selected_atmosphere.png')
    elapsed = time.monotonic()-started
    for path in sources:
        if sha256_file(path) != hashes[str(path.relative_to(ROOT))]:
            raise RuntimeError('source changed during calculation')
    manifest = {'created_utc': datetime.now(timezone.utc).isoformat(),
        'model': 'one-sided, cold, compact Einstein-Maxwell-Thomas-Fermi exterior',
        'parameters': {'edge_ratio': 1.5, 'screening_mass_parameter': 3.,
            'radius': 6.8, 'throat': 1.75, 'loadings': [1e-4, 3e-4, 1e-3, 3e-3],
            'wall_species': [1, 4, 16, 64], 'mass_search_interval': [.12, .40]},
        'workers': args.workers, 'seconds': elapsed, 'input_sha256': hashes,
        'search_count': len(tasks), 'equilibrium_count': len(rows),
        'tensile_count': sum(r['tensile_wall'] for r in rows),
        'searches': [{k: v for k, v in search.items() if k != 'roots'} for search in searches],
        'selected_equilibrium': selected[0], 'full_coupled_stability_evaluated': False,
        'finite_width_exclusion_evaluated': False, 'absolute_quantum_stress_evaluated': False,
        'output_sha256': {path.name: sha256_file(path) for path in args.output.iterdir()}}
    (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    size = sum(path.stat().st_size for path in args.output.iterdir())
    if elapsed > 600 or size > 5e6:
        raise RuntimeError('bounded runtime or retained-size allowance exceeded')
    print(json.dumps({'equilibria': len(rows), 'tensile': manifest['tensile_count'],
        'seconds': elapsed, 'retained_bytes': size, 'selected': selected[0]}, indent=2))


if __name__ == '__main__':
    main()
