#!/usr/bin/env python3
"""Independent split replay and conditional local elastic kinetic audit."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import json
import multiprocessing
from pathlib import Path
import resource
import time
import warnings

import numpy as np
import pandas as pd
from scipy.optimize import linprog, OptimizeWarning

from adm_harness.reset_inverse_search import reference_grid
from adm_harness.source_ledger import sha256_file
from adm_harness.vacuum_support_elasticity import (
    action_kinetic_hessian, kinetic_from_stress, stiffness_controls,
)
from run_vacuum_support import ROOT, SCENARIOS, POINTS


def independent_lp(target, cap, radial_only):
    aeq = np.array([[-1., -2., 1., 0., 0.], [-3., 2., 0., 1., 0.], [1., -2., 0., 0., 1.]])
    aub = np.array([[0., 0., -cap, 1., 0.], [0., 0., -cap, -1., 0.],
                    [0., 0., -cap, 0., 1.], [0., 0., -cap, 0., -1.]])
    scale = max(np.max(abs(target)), 1e-300)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='Unrecognized options detected', category=OptimizeWarning)
        result = linprog([1., 2., 0., 0., 0.], A_eq=aeq, b_eq=target/scale,
            A_ub=aub, b_ub=np.zeros(4), options={'threads': 1},
            bounds=[(0., None), (0., 0. if radial_only else None), (0., None), (None, None), (None, None)])
    if result.status not in [0, 2]:
        raise RuntimeError(f'LP oracle failed: {result.message}')
    return result, scale


def audit_scenario(task):
    name, output, reference, deadline, memory_mib = task
    resource.setrlimit(resource.RLIMIT_AS, (memory_mib*1024**2, memory_mib*1024**2))
    output = Path(output)
    lp_rows, kinetic_rows = [], []
    retained = {}
    max_replay_error, count_checked = 0., 0
    for count in POINTS:
        if time.monotonic() > deadline:
            raise TimeoutError('registered audit allowance exhausted')
        # Preserve the writer's binary floats. The default CSV converter
        # perturbs small outer-tail kinetic margins through cancellation.
        data = pd.read_csv(output/f'{name}_{count}.csv.gz', float_precision='round_trip')
        grid = reference_grid(reference, count, 2, path_kind='direct')
        reference_channels = np.stack([grid.energy[0], grid.pressure[0], grid.transverse[0]], axis=-1)
        for (cap, family), block in data.groupby(['pressure_cap', 'family'], sort=True):
            block = block.sort_values('radius').reset_index(drop=True)
            assert len(block) == count and np.allclose(block.radius, grid.r, atol=1e-14, rtol=0)
            get = lambda prefix: block[[f'{prefix}_{k}' for k in ['energy', 'radial', 'angular']]].to_numpy()
            total, ordinary, support, host, vacuum = map(get, ['total', 'ordinary', 'support', 'host', 'vacuum'])
            scale = np.maximum(abs(total).max(axis=1), 1e-30)
            error = np.max(abs(total-reference_channels)/scale[:, None])
            assert error < 3e-12
            np.testing.assert_allclose(support+ordinary, total, atol=2e-15, rtol=0)
            # Rebuild both original currents from the retained primitive state.
            rebuilt = np.zeros_like(ordinary)
            current = np.zeros(count)
            for key, w in [('particle', .2), ('entropy', 1/3)]:
                rho, velocity = block[f'{key}_rest'].to_numpy(), block[f'{key}_velocity'].to_numpy()
                hgamma = (1+w)*rho/(1-velocity**2)
                rebuilt += np.stack([hgamma-w*rho, hgamma*velocity**2+w*rho, w*rho], axis=-1)
                current += hgamma*velocity
            np.testing.assert_allclose(rebuilt, ordinary, atol=2e-15, rtol=0)
            np.testing.assert_allclose(current, 0., atol=1e-18, rtol=0)
            ok = block.feasible.to_numpy()
            cr, ct = block.radial_weight.to_numpy(), block.angular_weight.to_numpy()
            rebuilt_vacuum = np.stack([-cr-2*ct, -3*cr+2*ct, cr-2*ct], axis=-1)
            np.testing.assert_allclose(rebuilt_vacuum[ok], vacuum[ok], atol=2e-15, rtol=0)
            np.testing.assert_allclose(host[ok]+vacuum[ok]+ordinary[ok], total[ok], atol=2e-15, rtol=0)
            assert np.min((cap*host[:, 0]-abs(host[:, 1]))[ok]) > -2e-15
            assert np.min((cap*host[:, 0]-abs(host[:, 2]))[ok]) > -2e-15
            assert np.isnan(cr[~ok]).all() and np.isnan(ct[~ok]).all()
            max_replay_error = max(max_replay_error, error)
            count_checked += count
            indices = set(np.linspace(0, count-1, 13, dtype=int)) | {1, count-2,
                int(np.argmin(support[:, 0]+support[:, 1])), int(np.argmin(support[:, 0]+support[:, 2])),
                int(np.argmax(support[:, 2]))}
            for i in sorted(indices):
                lp, normalization = independent_lp(support[i], cap, family == 'radial_only')
                assert lp.success == ok[i]
                row = {'scenario': name, 'points': count, 'pressure_cap': cap, 'family': family,
                    'radius': grid.r[i], 'success': lp.success, 'solver_status': lp.status,
                    'normalization': normalization}
                if lp.success:
                    expected = (cr[i]+2*ct[i])/normalization
                    gap = abs(lp.fun-expected)
                    assert gap < 3e-11
                    row.update(oracle_cost=lp.fun*normalization, retained_cost=cr[i]+2*ct[i],
                        normalized_objective_gap=gap)
                    for key, value in zip(['radial_weight', 'angular_weight', 'host_energy', 'host_radial', 'host_angular'], lp.x*normalization):
                        row[f'oracle_{key}'] = value
                lp_rows.append(row)
            if count == 2049 and family == 'two_orientations':
                assert ok.all()
                weights = np.stack([cr, ct], axis=-1)
                predicted = kinetic_from_stress(support)
                retained['radius'] = grid.r
                retained[f'cap_{cap}_stress_kinetic'] = predicted
                for kind, hessian in stiffness_controls(host[:, 0]).items():
                    for step in [.04, .02, .01]:
                        actual = action_kinetic_hessian(host, weights, hessian, step)
                        errors = abs(actual-predicted).max(axis=(1, 2))
                        assert np.max(errors/scale) < 3e-12
                        eigenvalues = np.linalg.eigvalsh(actual)
                        tag = f'cap_{cap}_{kind}_step_{step}'
                        retained[f'{tag}_kinetic'] = actual
                        retained[f'{tag}_eigenvalues'] = eigenvalues
                        kinetic_rows.append({'scenario': name, 'pressure_cap': cap,
                            'host_stiffness_control': kind, 'velocity_step': step, 'points': count,
                            'max_action_hessian_error': float(errors.max()),
                            'max_normalized_action_hessian_error': float(np.max(errors/scale)),
                            'min_radial_kinetic': float(actual[:, 0, 0].min()),
                            'max_radial_kinetic': float(actual[:, 0, 0].max()),
                            'min_angular_kinetic': float(actual[:, 1, 1].min()),
                            'negative_radial_kinetic_points': int((actual[:, 0, 0] < 0).sum()),
                            'negative_angular_kinetic_points': int((actual[:, 1, 1] < 0).sum()),
                            'positive_definite_kinetic_points': int((eigenvalues.min(axis=1) > 0).sum()),
                            'full_material_candidate_pass': False})
    np.savez_compressed(output/f'kinetic_{name}.npz', **retained)
    return {'lp_rows': lp_rows, 'kinetic_rows': kinetic_rows,
            'points_replayed': count_checked, 'max_reference_replay_error': float(max_replay_error),
            'worker_peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def plot_kinetic(output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    with np.load(output/'kinetic_low_preload_counterflow.npz') as data:
        r = data['radius']
        matrix = data['cap_1.0_mixed_step_0.01_kinetic']
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), constrained_layout=True)
    axes[0].plot(r, matrix[:, 0, 0], label='radial material motion')
    axes[0].plot(r, matrix[:, 1, 1], label='each angular material motion')
    axes[0].set(ylabel='quadratic kinetic coefficient', title='Local stored-energy realization')
    axes[1].plot(r, matrix[:, 1, 1], color='tab:orange')
    axes[1].set(xlim=(3.85, 6.25), ylim=(-.00045, .0001),
                ylabel='angular kinetic coefficient', title='Outer angular sign requirement')
    for ax in axes:
        ax.axhline(0., color='black', linewidth=.6)
        ax.set_xlabel('areal radius')
        ax.grid(alpha=.2)
    axes[0].legend(fontsize=8)
    fig.savefig(output/'vacuum_support_kinetic.png', dpi=170)
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
        parser.error('one to six workers and positive budgets required')
    if (args.output/'round_two_manifest.json').exists():
        parser.error('completed audit already exists; reproduce in a new main-run directory')
    started = time.monotonic()
    original = {p.name: sha256_file(p) for p in args.output.iterdir() if p.is_file()}
    manifest = json.loads((args.output/'manifest.json').read_text())
    for path, expected in manifest['source_hashes'].items():
        assert sha256_file(ROOT/path) == expected, f'original source changed: {path}'
    reference = ROOT/'supporting_reports/data/le_coupled_reset_source/reference_tensors.csv.gz'
    tasks = [(name, str(args.output), str(reference), started+args.budget_seconds,
              args.worker_memory_mib) for name, _, _ in SCENARIOS]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(audit_scenario, tasks))
    lp = pd.DataFrame([row for result in results for row in result['lp_rows']])
    kinetic = pd.DataFrame([row for result in results for row in result['kinetic_rows']])
    lp.to_csv(args.output/'independent_linear_programs.csv', index=False)
    kinetic.to_csv(args.output/'kinetic_summaries.csv', index=False)
    plot_kinetic(args.output)
    for path, expected in original.items():
        assert sha256_file(args.output/path) == expected, f'original evidence changed: {path}'
    size = sum(p.stat().st_size for p in args.output.iterdir() if p.is_file())
    elapsed = time.monotonic()-started
    if elapsed > args.budget_seconds or size > args.output_cap_mb*1e6:
        raise RuntimeError('registered compute or evidence allowance exceeded')
    sources = [Path(__file__).resolve(), ROOT/'toolkit/adm_harness_cli/adm_harness/vacuum_support_elasticity.py']
    report = {'created_utc': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': elapsed,
        'workers': args.workers, 'max_worker_peak_rss_kib': max(x['worker_peak_rss_kib'] for x in results),
        'main_points_replayed': sum(x['points_replayed'] for x in results),
        'max_reference_replay_error': max(x['max_reference_replay_error'] for x in results),
        'independent_linear_programs': len(lp), 'independently_infeasible_programs': int((~lp.success).sum()),
        'max_lp_normalized_objective_gap': float(lp.normalized_objective_gap.max()),
        'kinetic_comparisons': len(kinetic),
        'max_normalized_kinetic_hessian_error': float(kinetic.max_normalized_action_hessian_error.max()),
        'positive_definite_kinetic_points_across_comparisons': int(kinetic.positive_definite_kinetic_points.sum()),
        'total_evidence_bytes_before_audit_manifest': size, 'original_evidence_hashes': original,
        'audit_source_hashes': {str(p.relative_to(ROOT)): sha256_file(p) for p in sources},
        'scope': 'Local first-derivative material-label action for locked vacuum and host; independent quantum-state dynamics absent.'}
    (args.output/'round_two_manifest.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if not k.endswith('hashes')}, indent=2))


if __name__ == '__main__':
    main()
