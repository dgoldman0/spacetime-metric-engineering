#!/usr/bin/env python3
"""Record outer-shell material bounds and the exact thin-sheet obstruction."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import argparse
import json
import multiprocessing
from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy.optimize import brentq

from adm_harness.curved_boundary import StaticGeometry
from adm_harness.spherical_support import outer_shell, planar_sheet_limit
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]


def local_limit(task):
    coupling, nodes = task
    distance = np.geomspace(1e-6, .5, 81)
    return pd.DataFrame({'coupling': coupling, 'nodes': nodes, 'proper_distance': distance,
                         **planar_sheet_limit(distance, coupling, nodes)})


def zero_crossings(mass, values, function):
    indices = np.flatnonzero(values[:-1]*values[1:] < 0)
    return [brentq(function, mass[i], mass[i+1], xtol=1e-13) for i in indices]


def plot_results(table, limits, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.7), constrained_layout=True)
    axes[0].plot(table.exterior_mass, table.surface_energy, label='surface energy')
    axes[0].plot(table.exterior_mass, table.surface_pressure, label='surface pressure')
    axes[0].set(xlabel='exterior mass', ylabel='surface stress', title='Ordinary shell requirements', ylim=(0, .015))
    axes[1].plot(table.exterior_mass, table.fluid_radial_frequency_squared, label='conditional radial frequency²')
    axes[1].axhline(0., color='black', linewidth=.5)
    axes[1].set(xlabel='exterior mass', ylabel='frequency²', title='Specified surface-fluid response', ylim=(-.003, .001))
    selected = limits[limits.coupling.eq(8.) & limits.nodes.eq(256)]
    axes[2].loglog(selected.proper_distance, selected.angular_pressure, label='finite-transparency pressure')
    axes[2].loglog(selected.proper_distance, selected.asymptotic_magnitude, '--', label='coupling / (48π² distance³)')
    axes[2].set(xlabel='proper distance from sheet', ylabel='angular vacuum pressure', title='Thin-sheet material barrier')
    for ax in axes:
        ax.grid(alpha=.2); ax.legend(fontsize=8)
    fig.savefig(output, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/spherical_boundary_support')
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    started = time.monotonic()
    args.output.mkdir(parents=True, exist_ok=True)
    radius, throat = 6.8, 1.75
    sources = [Path(__file__).resolve(), ROOT/'toolkit/adm_harness_cli/adm_harness/spherical_support.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/curved_boundary.py',
        ROOT/'supporting_reports/data/curved_quantum_boundary/geometry.npz']
    hashes = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    mass = np.linspace(throat**2/(2*radius)+1e-6, radius/2-1e-6, 2001)
    values = outer_shell(radius, mass, throat)
    table = pd.DataFrame({'exterior_mass': mass, **values})
    table.to_csv(args.output/'junction_scan.csv.gz', index=False)
    dec_roots = zero_crossings(mass, values['surface_energy']-values['surface_pressure'],
        lambda m: outer_shell(radius, m)['surface_energy']-outer_shell(radius, m)['surface_pressure'])
    stability_roots = zero_crossings(mass, values['fluid_radial_frequency_squared'],
        lambda m: outer_shell(radius, m)['fluid_radial_frequency_squared'])
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        limits = pd.concat(pool.map(local_limit, [(c, n) for c in [1., 8., 64.] for n in [64, 128, 256]]), ignore_index=True)
    limits.to_csv(args.output/'local_quantum_limit.csv.gz', index=False)
    finest = limits[limits.nodes.eq(256)].reset_index(drop=True)
    medium = limits[limits.nodes.eq(128)].reset_index(drop=True)
    quadrature_error = float(np.max(np.abs(finest.angular_pressure/medium.angular_pressure-1)))
    with np.load(sources[-1]) as data:
        geometry = StaticGeometry(**dict(data))
    x = float(geometry.negative_branch_coordinate(radius))
    r, n, a = geometry.values(x); rl, _, _ = geometry.values(x, 1)
    metric_error = {'lapse_difference_from_one': float(n-1), 'radial_scale_difference_from_one': float(a-1),
                    'areal_f_difference_from_tail': float((r*rl/a)**2-(1-throat**2/radius**2))}
    example = {key: float(value) if np.asarray(value).dtype != bool else bool(value)
               for key, value in outer_shell(radius, 1.5).items()}
    example['surface_rest_density_parameter'] = example['surface_energy']-example['surface_pressure']
    example['surface_eos_coefficient'] = example['surface_pressure']/example['surface_rest_density_parameter']**2
    example['exterior_lapse_at_shell'] = float(np.sqrt(1-3/radius))
    plot_results(table, limits, args.output/'material_closure.png')
    for p in sources:
        if sha256_file(p) != hashes[str(p.relative_to(ROOT))]:
            raise RuntimeError(f'input changed during computation: {p}')
    result = {'completed_utc': datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds': time.monotonic()-started, 'workers': args.workers, 'radius': radius,
        'interior_mass': throat**2/(2*radius), 'dec_mass_interval': dec_roots,
        'specified_fluid_positive_frequency_mass_interval': stability_roots,
        'example_exterior_mass_1p5': example, 'tail_metric_check': metric_error,
        'previous_mass_025_to_junction_ceiling_ratio': .25/example['ordinary_surface_mass_density_ceiling'],
        'previous_mass_1_to_junction_ceiling_ratio': 1/example['ordinary_surface_mass_density_ceiling'],
        'max_flux_identity_error': float(np.max(np.abs(values['conservation_identity_residual']))),
        'local_limit_quadrature_relative_difference': quadrature_error,
        'minimum_distance_asymptotic_ratios': finest[finest.proper_distance.eq(finest.proper_distance.min())][['coupling', 'asymptotic_ratio']].to_dict('records'),
        'hard_barrier': 'Positive finite optical coupling produces a d^-3 off-wall angular pressure beside the ideal sheet; finite surface-mass matching does not remove this bulk singularity. A regular complete source requires a resolved material layer and its matched quantum stress.',
        'surface_response_scope': 'Static prescribed ultrastatic interior and Schwarzschild exterior; total barotropic surface response with nonzero momentum flux; quantum and material perturbations are not evolved.',
        'source_hashes': hashes}
    (args.output/'manifest.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
