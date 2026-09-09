#!/usr/bin/env python3
"""Compare bounded vacuum orientations and material costs on the initial rail."""
from __future__ import annotations

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
from scipy.integrate import simpson

from adm_harness.reset_inverse_search import reference_grid
from adm_harness.source_ledger import sha256_file
from adm_harness.vacuum_support import (
    initial_ordinary, minimum_dec_weights, minimum_vacuum_split,
    static_force, supported_cell_floor,
)

ROOT = Path(__file__).resolve().parents[3]
SCENARIOS = [('zero_preload', 0., 0.), ('low_preload_zero_drift', .01, 0.),
             ('low_preload_counterflow', .01, .04), ('high_preload_counterflow', .1, .04)]
POINTS = [513, 1025, 2049]


def run_scenario(task):
    name, fraction, drift, reference, output, deadline, memory_mib = task
    resource.setrlimit(resource.RLIMIT_AS, (memory_mib*1024**2, memory_mib*1024**2))
    summaries = []
    for count in POINTS:
        if time.monotonic() > deadline:
            raise TimeoutError('registered compute allowance exhausted')
        grid = reference_grid(reference, count, 2, path_kind='direct')
        r, rootf = grid.r, np.sqrt(grid.f[0])
        total = np.stack([grid.energy[0], grid.pressure[0], grid.transverse[0]], axis=-1)
        ordinary, states = initial_ordinary(r, fraction, drift)
        target = total-ordinary
        hr, ht = target[:, 0]+target[:, 1], target[:, 0]+target[:, 2]
        all_points = []
        for cap in [1., .5]:
            for family, radial_only in [('radial_only', True), ('two_orientations', False)]:
                split = minimum_vacuum_split(target, cap, radial_only)
                ok, weights = split['feasible'], split['weights']
                host, vacuum = split['host'], split['vacuum']
                points = pd.DataFrame({'scenario': name, 'points': count,
                    'pressure_cap': cap, 'family': family, 'radius': r, 'f': grid.f[0],
                    'alpha': np.exp(grid.nu[0]), 'feasible': ok,
                    'radial_weight': weights[:, 0], 'angular_weight': weights[:, 1],
                    'support_radial_enthalpy': hr, 'support_angular_enthalpy': ht,
                    'supported_cell_energy_floor': supported_cell_floor(*weights.T)})
                for component, data in [('total', total), ('ordinary', ordinary),
                                         ('support', target), ('host', host), ('vacuum', vacuum)]:
                    for k, key in enumerate(['energy', 'radial', 'angular']):
                        points[f'{component}_{key}'] = data[:, k]
                for k, key in enumerate(['host_energy_margin', 'host_radial_margin', 'host_angular_margin']):
                    points[key] = split['host_margins'][:, k]
                for k, key in enumerate(['particle_rest', 'particle_velocity', 'entropy_rest', 'entropy_velocity']):
                    points[key] = states[:, k]
                err = abs(host+vacuum+ordinary-total)
                scale = np.maximum(abs(total).max(axis=1), 1e-30)
                points['max_normalized_tensor_error'] = err.max(axis=1)/scale
                coordinate_measure = 4*np.pi*r*r
                proper_measure = coordinate_measure/rootf
                summary = {'scenario': name, 'preload_fraction': fraction, 'initial_drift': drift,
                    'points': count, 'pressure_cap': cap, 'family': family,
                    'feasible_points': int(ok.sum()), 'infeasible_points': int((~ok).sum()),
                    'all_points_algebraically_feasible': bool(ok.all()),
                    'min_support_radial_enthalpy': float(hr.min()),
                    'max_support_radial_enthalpy': float(hr.max()),
                    'min_support_angular_enthalpy': float(ht.min()),
                    'negative_support_radial_points': int((hr < 0).sum()),
                    'negative_support_angular_points': int((ht < 0).sum()),
                    'max_normalized_tensor_error': float(points.max_normalized_tensor_error.max()),
                    'minimum_host_margin': float(np.nanmin(split['host_margins'])),
                    'initial_ordinary_coordinate_mass': float(simpson(coordinate_measure*ordinary[:, 0], x=r)),
                    'reference_coordinate_mass': float(simpson(coordinate_measure*total[:, 0], x=r)),
                    'reference_proper_energy': float(simpson(proper_measure*total[:, 0], x=r)),
                    'complete_material_candidate_pass': False}
                if ok.all():
                    for component, data in [('host', host), ('vacuum', vacuum), ('support', target)]:
                        summary[f'{component}_coordinate_mass'] = float(simpson(coordinate_measure*data[:, 0], x=r))
                        summary[f'{component}_proper_energy'] = float(simpson(proper_measure*data[:, 0], x=r))
                    for component, data in [('host', host), ('vacuum', vacuum), ('ordinary', ordinary), ('total', total)]:
                        force = static_force(r, rootf, grid.nu_r[0], data)
                        points[f'{component}_required_static_force'] = force
                        summary[f'max_{component}_required_static_force'] = float(abs(force).max())
                    forces = [points[f'{k}_required_static_force'] for k in ['host', 'vacuum', 'ordinary']]
                    summary['force_sum_identity_error'] = float(abs(sum(forces)-points.total_required_static_force).max())
                    if cap == 1.:
                        summary['closed_form_weight_error'] = float(abs(weights-minimum_dec_weights(target)).max())
                    for label, i in [('inner', 0), ('outer', -1)]:
                        summary[f'{label}_pressure_matching_error'] = float(err[i, 1])
                        summary[f'{label}_normal_acceleration_matching_error'] = float(4*np.pi*r[i]*err[i, 1]/rootf[i])
                summaries.append(summary)
                all_points.append(points)
        pd.concat(all_points, ignore_index=True).to_csv(Path(output)/f'{name}_{count}.csv.gz', index=False)
    return {'summaries': summaries,
            'worker_peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def plot_results(output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    data = pd.read_csv(output/'low_preload_counterflow_2049.csv.gz')
    data = data[data.family.eq('two_orientations') & data.pressure_cap.eq(1.)]
    r = data.radius
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    axes[0, 0].plot(r, data.support_radial_enthalpy, label='radial')
    axes[0, 0].plot(r, data.support_angular_enthalpy, label='angular')
    axes[0, 0].set(title='Initial support demand', ylabel='energy + pressure')
    axes[0, 1].plot(r, data.radial_weight, label='radial vacuum weight')
    axes[0, 1].plot(r, data.angular_weight, label='each angular weight')
    axes[0, 1].set(title='Minimum vacuum magnitude with DEC host', ylabel='vacuum weight')
    axes[1, 0].plot(r, data.total_energy, label='retained total energy')
    axes[1, 0].plot(r, data.host_energy, label='material remainder')
    axes[1, 0].plot(r, data.vacuum_energy, label='vacuum contribution')
    axes[1, 0].set(title='All energies counted in the split', ylabel='energy density')
    axes[1, 1].plot(r, data.vacuum_required_static_force, label='vacuum')
    axes[1, 1].plot(r, data.host_required_static_force, label='material remainder')
    axes[1, 1].set(title='Force required to hold each component static', ylabel='orthonormal force density')
    for ax in axes.ravel():
        ax.axhline(0., color='black', linewidth=.5)
        ax.set_xlabel('areal radius')
        ax.legend(fontsize=8)
        ax.grid(alpha=.2)
    fig.savefig(output/'vacuum_support_split.png', dpi=170)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--budget-seconds', type=float, default=600.)
    parser.add_argument('--worker-memory-mib', type=int, default=1536)
    parser.add_argument('--output-cap-mb', type=float, default=30.)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/vacuum_support')
    args = parser.parse_args()
    if not 1 <= args.workers <= 6 or min(args.budget_seconds, args.worker_memory_mib, args.output_cap_mb) <= 0:
        parser.error('one to six workers and positive resource budgets required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    reference = ROOT/'supporting_reports/data/le_coupled_reset_source/reference_tensors.csv.gz'
    sources = [reference, ROOT/'toolkit/adm_harness_cli/adm_harness/source_ledger.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/reset_inverse_search.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/vacuum_support.py', Path(__file__).resolve()]
    hashes = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    tasks = [(name, frac, drift, str(reference), str(args.output), started+args.budget_seconds,
              args.worker_memory_mib) for name, frac, drift in SCENARIOS]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(run_scenario, tasks))
    summaries = pd.DataFrame([row for result in results for row in result['summaries']])
    summaries.to_csv(args.output/'summaries.csv', index=False)
    plot_results(args.output)
    for p in sources:
        if sha256_file(p) != hashes[str(p.relative_to(ROOT))]:
            raise RuntimeError(f'input changed during run: {p}')
    elapsed = time.monotonic()-started
    size = sum(p.stat().st_size for p in args.output.iterdir())
    if elapsed > args.budget_seconds or size > args.output_cap_mb*1e6:
        raise RuntimeError('registered compute or evidence allowance exceeded')
    manifest = {'created_utc': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': elapsed,
        'workers': args.workers, 'worker_memory_mib': args.worker_memory_mib,
        'max_worker_peak_rss_kib': max(x['worker_peak_rss_kib'] for x in results),
        'evidence_bytes_before_manifest': size, 'source_hashes': hashes,
        'scenarios': SCENARIOS, 'radial_points': POINTS, 'comparisons': len(summaries),
        'full_algebraic_fits': int(summaries.all_points_algebraically_feasible.sum()),
        'full_material_candidates': 0,
        'scope': 'Planar vacuum tensor weights plus pressure-bounded material remainder; boundary and constitutive checks separate.'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
