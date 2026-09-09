#!/usr/bin/env python3
"""Bounded parallel smooth-wall and trapped-material diagnostics."""
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
from scipy.optimize import brentq

from adm_harness.smooth_mirror import (smooth_born_stress, independent_born_energy,
    fermi_surface_match, corrugation_energy, normal_mode_requirements)
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]


def profile(task):
    width, nodes = task
    started = time.monotonic()
    y = np.unique(np.r_[np.linspace(-24., 24., 769), -40., 40.])
    strength = .1/width
    values = smooth_born_stress(width*y, width, strength, 1/width, nodes=nodes)
    return pd.DataFrame({'width': width, 'nodes': nodes, 'normal_coordinate': width*y,
        'scaled_coordinate': y, 'integrated_strength': strength,
        'mu': 1/width, 'born_parameter': .05, **values}), {
        'width': width, 'nodes': nodes, 'seconds': time.monotonic()-started,
        'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def roots(mass, values, function):
    intervals = np.flatnonzero(values[:-1]*values[1:] < 0)
    return [brentq(function, mass[i], mass[i+1], xtol=1e-13) for i in intervals]


def plots(quantum, material, modes, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(12.4, 3.8), constrained_layout=True)
    q = quantum[(quantum.width == .05)&(quantum.nodes == 1024)]
    scaled = q.energy*q.width**3/q.integrated_strength
    axes[0].plot(q.scaled_coordinate, scaled, label='smooth first-order energy')
    axes[0].plot(q.scaled_coordinate, -scaled, label='angular pressure')
    axes[0].set(xlim=(-8, 8), xlabel='normal distance / width', ylabel='stress × width³ / strength',
                title='Resolved planar quantum stress')
    selected = material[material.positive_components]
    axes[1].plot(selected.exterior_mass, selected.wall_tension, label='wall tension energy')
    axes[1].plot(selected.exterior_mass, selected.fermi_energy, label='trapped gas energy')
    axes[1].set(xlabel='exterior mass', ylabel='surface energy', title='Leading material stress match')
    s = modes[modes.width == .05]
    axes[2].plot(s.wave_number, s.normal_frequency_squared, label='local normal mode')
    valid = s[s.scale_window]
    axes[2].scatter(valid.wave_number, valid.normal_frequency_squared, s=10,
                    label='10 ≤ kR and kd ≤ 0.2')
    axes[2].set(xlabel='surface wave number', ylabel='proper frequency²',
                title='Compressed surface shape response', xlim=(0, 5), ylim=(-4, .2))
    for ax in axes:
        ax.axhline(0, color='black', linewidth=.5)
        ax.grid(alpha=.2)
        ax.legend(fontsize=7)
    fig.savefig(output, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/smooth_quantum_material')
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    started = time.monotonic()
    sources = [Path(__file__).resolve(), ROOT/'toolkit/adm_harness_cli/adm_harness/smooth_mirror.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/spherical_support.py',
        ROOT/'supporting_reports/data/spherical_boundary_support/manifest.json',
        ROOT/'supporting_reports/data/curved_quantum_boundary/geometry.npz']
    hashes = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    tasks = [(d, n) for d in [.025, .05, .1] for n in [256, 512, 1024]]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(profile, tasks))
    quantum = pd.concat([x[0] for x in results], ignore_index=True)
    args.output.mkdir(parents=True, exist_ok=True)
    quantum.to_csv(args.output/'smooth_stress_profiles.csv.gz', index=False)
    convergence = []
    for d in [.025, .05, .1]:
        fine = quantum[(quantum.width == d)&(quantum.nodes == 1024)].reset_index(drop=True)
        for n in [256, 512]:
            coarse = quantum[(quantum.width == d)&(quantum.nodes == n)].reset_index(drop=True)
            err = abs(fine.energy-coarse.energy)
            convergence.append({'width': d, 'coarse_nodes': n, 'fine_nodes': 1024,
                'maximum_absolute_error': float(err.max()),
                'peak_normalized_error': float(err.max()/abs(fine.energy).max()),
                'tail_relative_error_at_40_widths': float(err.iloc[-1]/abs(fine.energy.iloc[-1]))})
    pd.DataFrame(convergence).to_csv(args.output/'quadrature_convergence.csv', index=False)
    independent = []
    for y in [0., .5, 1., 2., 4., 8., 16., 24., 40.]:
        d, strength = .05, 2.
        direct, bound = independent_born_energy(d*y, d, strength, 1/d)
        primary = float(smooth_born_stress(d*y, d, strength, 1/d, nodes=1024)['energy'])
        independent.append({'scaled_coordinate': y, 'direct_energy': direct,
            'primary_energy': primary, 'absolute_error': abs(primary-direct),
            'relative_error': abs(primary/direct-1), 'adaptive_error_estimate': bound})
    pd.DataFrame(independent).to_csv(args.output/'independent_quantum_checks.csv', index=False)

    radius, throat = 6.8, 1.75
    mass = np.linspace(throat**2/(2*radius)+1e-6, radius/2-1e-6, 2001)
    values = fermi_surface_match(radius, mass)
    material = pd.DataFrame({'exterior_mass': mass, **values})
    material.to_csv(args.output/'fermi_junction_scan.csv.gz', index=False)
    tension_roots = roots(mass, values['wall_tension'], lambda m: fermi_surface_match(radius, m)['wall_tension'])
    radial_roots = roots(mass, values['fermi_radial_frequency_squared'],
                         lambda m: fermi_surface_match(radius, m)['fermi_radial_frequency_squared'])
    example = {key: bool(value) if np.asarray(value).dtype == bool else float(value)
               for key, value in fermi_surface_match(radius, 1.5).items()}
    mode_tables = [pd.DataFrame({'width': d, **normal_mode_requirements(radius,
        example['surface_energy'], example['surface_pressure'], d, np.arange(1, 81))})
        for d in [.025, .05, .1]]
    modes = pd.concat(mode_tables, ignore_index=True)
    modes.to_csv(args.output/'shape_modes.csv', index=False)
    energy_checks = []
    k = np.sqrt(12*13)/radius
    for multiplier in [0., .5, 1., 2.]:
        fermi = multiplier*example['fermi_energy']
        tension = example['wall_tension']
        pressure = -tension+.5*fermi
        for a in [.01, .005, .0025, .00125]:
            change = corrugation_energy(a, k, tension, fermi)
            coefficient = change/a**2
            expected = -pressure*k*k/4
            energy_checks.append({'gas_multiplier': multiplier, 'amplitude': a,
                'wave_number': k, 'surface_pressure': pressure, 'energy_change': change,
                'quadratic_coefficient': coefficient, 'predicted_coefficient': expected,
                'absolute_error': abs(coefficient-expected)})
    pd.DataFrame(energy_checks).to_csv(args.output/'independent_shape_energy.csv', index=False)
    plots(quantum, material, modes, args.output/'smooth_material_findings.png')
    for p in sources:
        if sha256_file(p) != hashes[str(p.relative_to(ROOT))]:
            raise RuntimeError(f'input changed during calculation: {p}')
    elapsed = time.monotonic()-started
    size = sum(p.stat().st_size for p in args.output.iterdir())
    if elapsed > 600 or size > 20e6:
        raise RuntimeError('registered computation or evidence allowance exceeded')
    chosen = material.positive_components & (material.fermi_radial_frequency_squared > 0)
    summary = {'completed_utc': datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds': elapsed, 'workers': args.workers, 'profile_tasks': [x[1] for x in results],
        'evidence_bytes_before_manifest': size, 'source_hashes': hashes,
        'positive_tension_mass_interval': tension_roots,
        'conditional_positive_radial_frequency_mass_interval': radial_roots,
        'positive_material_and_radial_scan_rows': int(chosen.sum()),
        'negative_normal_stiffness_among_these_rows': int((chosen & (material.normal_speed_squared < 0)).sum()),
        'example_mass_1p5': example,
        'max_independent_quantum_relative_error': max(x['relative_error'] for x in independent),
        'max_medium_to_fine_peak_normalized_error': max(x['peak_normalized_error'] for x in convergence if x['coarse_nodes'] == 512),
        'negative_local_shape_modes_in_scale_window': int(((modes.normal_frequency_squared < 0)&modes.scale_window).sum()),
        'quantum_scope': 'Smooth planar massless minimal scalar stress at first order in V, Born parameter 0.05 and mu*width=1; finite inside the wall; full curved stress and quantum force remain unevaluated.',
        'material_scope': 'Leading measured wall tension plus trapped massless surface gas, pressure=gas_energy/2-wall_tension; prescribed-bulk radial diagnostic includes momentum flux; normal diagnostic is the local surface action with no added bending or nonlocal quantum response.',
        'promotion': 'Stopped at negative normal stiffness in the leading pressure-bearing surface description; a complete finite-width quantum material requires its own restoring response and coupled field equations.'}
    (args.output/'manifest.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
