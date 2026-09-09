#!/usr/bin/env python3
"""Parallel material controls and tensor accounting for screened condensates."""
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
from scipy.integrate import simpson, cumulative_simpson

from adm_harness.screened_condensate import solve_flat_reference, field_stress
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]


def calculate(task):
    kind, tolerance, extent, points = task
    started = time.monotonic()
    p, omega, solution = solve_flat_reference(kind, tolerance=tolerance, extent=extent, points=points)
    r = np.linspace(0, extent, 16001)
    fields = solution.sol(r)
    t = field_stress(fields, omega, p)
    energy = 4*np.pi*simpson(r*r*t['energy'], x=r)
    number = 4*np.pi*simpson(r*r*t['matter_number'], x=r)
    higgs_charge = 4*np.pi*simpson(r*r*t['higgs_charge'], x=r)
    radial = simpson(t['radial_pressure'], x=r)
    tangent = simpson(t['tangential_pressure'], x=r)
    column_energy = simpson(t['energy'], x=r)
    cumulative = cumulative_simpson(r*r*t['energy'], x=r, initial=0)
    r05, r50, r95 = np.interp(np.array([.05, .5, .95])*cumulative[-1], cumulative, r)
    virial = 4*np.pi*simpson(r*r*(t['radial_pressure']+2*t['tangential_pressure']), x=r)/energy
    dp = np.gradient(t['radial_pressure'], r, edge_order=2)
    mask = (r > .1) & (t['energy'] > 1e-7*np.max(t['energy']))
    force = np.zeros_like(r)
    force[1:] = 2*(t['tangential_pressure'][1:]-t['radial_pressure'][1:])/r[1:]
    conservation = np.max(abs(dp[mask]-force[mask]))/max(np.max(abs(force[mask])), 1e-30)
    row = {'kind': kind, 'tolerance': tolerance, 'extent': extent, 'initial_points': points,
        'omega': omega, 'charge_coupling': p.charge, 'higgs_coupling': p.higgs_coupling,
        'matter_coupling': p.matter_coupling, 'energy': energy, 'matter_number': number,
        'energy_per_free_particle_energy': energy/(np.sqrt(p.matter_coupling)*number),
        'net_charge_relative_error': abs(p.charge*number+higgs_charge)/(p.charge*number),
        'number_relative_error': abs(number/(4*np.pi*({'homogeneous': 58000., 'hollow': 85600.}[kind]))-1),
        'u_at_origin': fields[0, 0], 'higgs_at_origin': fields[2, 0],
        'energy_peak_radius': r[np.argmax(t['energy'])], 'energy_r05': r05,
        'energy_r50': r50, 'energy_r95': r95, 'energy_90_width_over_r50': (r95-r05)/r50,
        'radial_column_pressure': radial, 'tangential_column_pressure': tangent,
        'column_energy': column_energy, 'column_pressure_to_energy': tangent/column_energy,
        'flat_virial_relative_error': abs(virial),
        'column_force_identity_relative_error': abs(2*tangent-radial)/column_energy,
        'stress_conservation_relative_error': conservation,
        'maximum_bvp_residual': np.max(solution.rms_residuals), 'bvp_nodes': len(solution.x),
        'minimum_tangential_pressure': np.min(t['tangential_pressure']),
        'maximum_tangential_pressure': np.max(t['tangential_pressure']),
        'seconds': time.monotonic()-started,
        'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    # Retain small profiles for the central refinement only.
    profile = None
    if tolerance == 1e-7 and extent == 250. and points == 1001:
        rr = np.linspace(0, extent, 2001)
        ff = solution.sol(rr)
        profile = {'radius': rr, 'matter_field': ff[0], 'matter_derivative': ff[1],
            'higgs_field': ff[2], 'higgs_derivative': ff[3], 'gauge_potential': ff[4],
            'gauge_derivative': ff[5], **field_stress(ff, omega, p)}
    return row, profile


def plot(profiles, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 3, figsize=(11, 6), constrained_layout=True)
    for j, (kind, a) in enumerate(profiles.items()):
        r = a['radius']
        for field, label in [('matter_field', 'Matter'), ('higgs_field', 'Higgs'),
                             ('gauge_potential', 'Gauge potential')]:
            axes[j, 0].plot(r, a[field], label=label)
        for field, label in [('energy', 'Energy'), ('radial_pressure', 'Radial pressure'),
                             ('tangential_pressure', 'Tangential pressure')]:
            axes[j, 1].plot(r, a[field], label=label)
        axes[j, 2].plot(r, a['matter_charge'], label='Matter charge')
        axes[j, 2].plot(r, a['higgs_charge'], label='Higgs charge')
        axes[j, 2].plot(r, a['matter_charge']+a['higgs_charge'], label='Net charge')
        axes[j, 0].set_ylabel(kind.capitalize()+' reference')
        for ax in axes[j]:
            ax.set(xlabel='Radius × Higgs vacuum amplitude', xlim=(0, 160))
            ax.legend(fontsize=7)
            ax.grid(alpha=.2)
    fig.savefig(output, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/screened_condensate')
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    sources = [Path(__file__).resolve(), ROOT/'toolkit/adm_harness_cli/adm_harness/screened_condensate.py']
    hashes = {str(path.relative_to(ROOT)): sha256_file(path) for path in sources}
    tasks = [(kind, tol, extent, points) for kind in ['homogeneous', 'hollow']
        for tol, extent, points in [(1e-5, 250., 1001), (1e-7, 250., 1001),
                                  (1e-9, 250., 1001), (1e-7, 300., 1401)]]
    started = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(calculate, tasks))
    rows = [row for row, profile in results]
    profiles = {row['kind']: profile for row, profile in results if profile is not None}
    args.output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output/'reference_checks.csv', index=False)
    for name, profile in profiles.items():
        pd.DataFrame(profile).to_csv(args.output/(name+'_profile.csv.gz'), index=False)
    plot(profiles, args.output/'condensate_reference_profiles.png')
    for path in sources:
        if sha256_file(path) != hashes[str(path.relative_to(ROOT))]:
            raise RuntimeError('source changed during computation')
    manifest = {'created_utc': datetime.now(timezone.utc).isoformat(), 'workers': args.workers,
        'seconds': time.monotonic()-started, 'input_sha256': hashes,
        'model': 'Ishihara-Ogawa U(1) matter-Higgs condensates, flat material references',
        'reduced_particle_numbers': {'homogeneous': 58000., 'hollow': 85600.},
        'references': ['https://arxiv.org/abs/1901.08799', 'https://arxiv.org/abs/2103.13732',
                       'https://arxiv.org/abs/2409.07818'],
        'rail_thin_junction_minimum_pressure_to_energy': 1.75/(2*(6.8-1.75)),
        'rail_static_matching_evaluated': False, 'full_perturbation_stability_evaluated': False,
        'absolute_quantum_stress_evaluated': False,
        'output_sha256': {path.name: sha256_file(path) for path in args.output.iterdir()}}
    (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    size = sum(path.stat().st_size for path in args.output.iterdir())
    if manifest['seconds'] > 600 or size > 5e6:
        raise RuntimeError('bounded runtime or retained-size allowance exceeded')
    print(pd.DataFrame(rows)[['kind', 'tolerance', 'omega', 'net_charge_relative_error',
        'flat_virial_relative_error', 'column_pressure_to_energy']].to_string(index=False))
    print(json.dumps({'seconds': manifest['seconds'], 'retained_bytes': size}))


if __name__ == '__main__':
    main()
