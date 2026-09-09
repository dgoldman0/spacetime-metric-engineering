#!/usr/bin/env python3
"""Refine retained curvature witnesses and independently verify saved evidence."""
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
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import RectBivariateSpline
from scipy.optimize import linear_sum_assignment

from run_comer_andersson_startup import CONTROLS, fields_for_grid
from run_le_geometry_boundary import ROOT, save_records
from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.reset_inverse_search import reference_grid
from adm_harness.source_ledger import SourceParams, sha256_file


TIME_STEPS = [2e-4, 5e-5, 1.25e-5, 3.125e-6]


def refine_scenario(task):
    scenario, witnesses, reference, memory_mib = task
    resource.setrlimit(resource.RLIMIT_AS, (memory_mib*1024**2, memory_mib*1024**2))
    kind, speed = scenario.rsplit('_', 1)
    duration, skew = (4., -.65) if speed == 'fast' else (14.255, .65)
    rows = []
    for level in sorted({row['level'] for row in witnesses}):
        grid = reference_grid(reference, 128*2**level+1, 64*2**level+1, path_kind=kind)
        fields = fields_for_grid(grid, duration, skew)
        sf = RectBivariateSpline(grid.u, grid.r, np.log(fields['f']), kx=3, ky=3, s=0)
        sa = RectBivariateSpline(grid.u, grid.r, np.log(fields['alpha']), kx=3, ky=3, s=0)

        def inverse_clock(t):
            v = (t-.745)/duration
            return 2*v/(1+skew+np.sqrt((1+skew)**2-4*skew*v))

        def metric(t, r, params):
            u = inverse_clock(t)
            return {'alpha': float(np.exp(sa.ev(u, r))), 'beta': 0.,
                    'gamma_ll': float(np.exp(-sf.ev(u, r))), 'gamma_omega': r*r}

        for witness in [row for row in witnesses if row['level'] == level]:
            t, r = witness['s'], witness['l']
            u = inverse_clock(t)
            tu, tuu = duration*(1+skew*(1-2*u)), -2*duration*skew
            f, alpha = np.exp(sf.ev(u, r)), np.exp(sa.ev(u, r))
            lu, luu, nuu = sf.ev(u, r, dx=1), sf.ev(u, r, dx=2), sa.ev(u, r, dx=1)
            # Direct log-metric derivative formulas, separate from rate-action
            # channel assembly. These are the jets of the metric actually
            # passed to the independent four-dimensional curvature stencil.
            logf_t, logf_tt = lu/tu, luu/tu**2-lu*tuu/tu**3
            h = -logf_t/(2*alpha)
            dh = -(logf_tt-logf_t*nuu/tu)/(2*alpha**2)
            correction = np.array([0., 0., np.sqrt(f)*logf_t/(8*np.pi*r*alpha),
                                   -(dh+h*h)/(8*np.pi)])
            scale = max(float(abs(correction).max()), 1e-30)
            for step in TIME_STEPS:
                dynamic = evaluate_demand(t, r, SourceParams(), step, .000625, scalar_evaluator=metric)
                holding = evaluate_demand(t, r, SourceParams(), step, .000625,
                                          holding=True, scalar_evaluator=metric)
                difference = np.array([dynamic[k]-holding[k] for k in ['rho', 'p_l', 'j_l', 'p_omega']])
                error = float(abs(difference-correction).max())
                for mode, row in [('dynamic', dynamic), ('holding', holding)]:
                    row.update(scenario=scenario, level=level, sample=witness['sample'], mode=mode,
                               dynamic_difference_max_error=error,
                               dynamic_difference_relative_error=error/scale,
                               rate_angular_pressure=float(correction[3]), required_current=float(correction[2]))
                    rows.append(row)
    return rows, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def verify_eigensystems(output, stem):
    frame = pd.read_csv(output/f'{stem}.csv.gz', float_precision='round_trip')
    assert frame.full_eigensystem_certified.all()
    eta = np.diag([-1., 1., 1., 1.])
    errors, raw_errors, raw_complex = [], [], 0
    with np.load(output/f'{stem}_eigensystems.npz') as data:
        np.testing.assert_array_equal(data['row_index'], np.arange(len(frame)))
        for key in ['s', 'l']:
            np.testing.assert_array_equal(data[key], frame[key].to_numpy())
        tensor = data['tensor_orthonormal']
        for key, values in [('rho', tensor[:, 0, 0]), ('p_l', tensor[:, 1, 1]),
                            ('j_l', -tensor[:, 0, 1]), ('p_omega', tensor[:, 2, 2])]:
            np.testing.assert_array_equal(values, frame[key].to_numpy())
        for i in range(len(frame)):
            matrix = eta@tensor[i]
            values, vectors = data['eigenvalues'][i], data['eigenvectors'][i]
            scale = max(float(np.linalg.norm(matrix)), 1e-30)
            errors.append(float(np.linalg.norm(matrix@vectors-vectors*values)/(scale*np.linalg.norm(vectors))))
            raw_values = np.linalg.eigvals(eta@data['raw_tensor_orthonormal'][i])
            cost = abs(raw_values[:, None]-data['raw_eigenvalues'][i][None, :])
            j, k = linear_sum_assignment(cost)
            raw_errors.append(float(cost[j, k].max()/scale))
            raw_complex += int(abs(raw_values.imag).max() > 1e-10*scale)
    assert max(errors) < 1e-12 and max(raw_errors) < 1e-12
    return {'records': len(frame), 'max_eigen_equation_relative_error': max(errors),
            'max_replayed_raw_eigenvalue_relative_error': max(raw_errors),
            'raw_complex_pair_records': raw_complex,
            'classification_counts': frame.groupby('mode').stress_algebraic_type.value_counts().to_dict()}


def verify_fields(output):
    summaries = pd.read_csv(output/'summaries.csv', float_precision='round_trip')
    accounting = pd.read_csv(output/'thermal_scale_accounting.csv', float_precision='round_trip')
    records = []
    for entry in accounting.to_dict('records'):
        scenario = entry['scenario']
        with np.load(output/f'{scenario}_fields.npz') as data:
            assert all(np.isfinite(data[key]).all() for key in data.files)
            r, h, dh = data['radius'], data['radial_rate'], data['radial_rate_dot']
            np.testing.assert_allclose(data['current'], -np.sqrt(data['f'])*h/(4*np.pi*r), rtol=1e-13, atol=1e-15)
            np.testing.assert_allclose(data['angular_time_demand'], -(dh+h*h)/(8*np.pi), rtol=1e-13, atol=1e-15)
            np.testing.assert_allclose(data['required_cattaneo_drive'], -data['current']-data['current_dot'],
                                       rtol=1e-13, atol=1e-15)
            e, v, rest = data['diagnostic_thermal_energy'], data['heat_drift'], data['heat_rest_energy']
            np.testing.assert_allclose(e, rest*(1+v*v/3)/(1-v*v), rtol=1e-13, atol=1e-15)
            np.testing.assert_allclose(data['current'], (4/3)*rest*v/(1-v*v), rtol=1e-13, atol=1e-15)
            mass = cumulative_trapezoid(4*np.pi*r*r*e[0], r, initial=0.)
            np.testing.assert_allclose(mass[-1], entry['diagnostic_initial_thermal_mass'], rtol=1e-13)
            np.testing.assert_allclose((data['f'][0]-2*mass/r).min(),
                entry['min_f_if_thermal_energy_is_added_to_frozen_initial_source'], rtol=1e-13)
            max_summary_error = 0.
            for name, aa, bb in CONTROLS:
                row = summaries[summaries.scenario.eq(scenario) & summaries.level.eq(2)
                                & summaries.control.eq(name)].iloc[0]
                a, b = aa/(8*np.pi), bb/(8*np.pi)
                q = .5*(a+b)*h*h
                pr = -(a+b)*dh-q
                pt = -a*dh+.5*(b-a)*h*h
                entropy = -((a+b)*h*dh+(4/3)*h*q)/((4/3)*(e-q))
                checks = {'max_density_change': abs(q).max(), 'max_radial_pressure_change': abs(pr).max(),
                    'max_angular_mismatch': abs(pt-data['angular_time_demand']).max(),
                    'min_comoving_entropy_rate_per_entropy': entropy.min(),
                    'max_comoving_entropy_rate_per_entropy': entropy.max()}
                for key, value in checks.items():
                    np.testing.assert_allclose(value, row[key], rtol=1e-12, atol=2e-14)
                    max_summary_error = max(max_summary_error, float(abs(value-row[key])))
                if f'{name}_entropy_rate' in data:
                    np.testing.assert_allclose(entropy, data[f'{name}_entropy_rate'], rtol=1e-12, atol=1e-14)
            records.append({'scenario': scenario, 'points': int(h.size), 'fields': len(data.files),
                            'max_summary_replay_error': max_summary_error})
    return records


def make_figure(output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    summaries = pd.read_csv(output/'summaries.csv')
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    subset = summaries[summaries.level.eq(2) & summaries.scenario.eq('direct_fast')]
    labels = {'zero_rate': ('zero rate', (-15, -18)), 'exact_tensor_match': ('exact match', (8, 8)),
              'positive_bulk': ('bulk rate', (8, -28)), 'positive_squared_rate': ('squared rate', (-55, 10)),
              'near_match_positive_tensor_kinetic': ('near match', (8, 8)),
              'negative_tensor_kinetic': ('negative kinetic term', (8, 12))}
    for row in subset.itertuples():
        x, y = row.tensor_kinetic_ratio, max(row.max_three_channel_mismatch, 1e-18)
        label, offset = labels[row.control]
        axes[0].scatter(x, y, s=35)
        axes[0].annotate(label, (x, y), xytext=offset, textcoords='offset points', fontsize=8)
    axes[0].axvline(0, color='black', lw=.8)
    axes[0].set(yscale='log', xlim=(-.4, 2.2), ylim=(1e-18, 1.),
                xlabel='tensor kinetic coefficient / GR', ylabel='maximum three-channel stress mismatch',
                title='Stress match and gravitational kinetics')
    with np.load(output/'direct_fast_fields.npz') as data:
        _, ir = np.unravel_index(np.argmin(data['positive_bulk_entropy_rate']), data['positive_bulk_entropy_rate'].shape)
        for name, label in [('positive_bulk', 'bulk rate'), ('near_match_positive_tensor_kinetic', 'near match')]:
            axes[1].plot(data['time'], data[f'{name}_entropy_rate'][:, ir], label=label)
        axes[1].set(title=f'Comoving entropy test at r = {data["radius"][ir]:.3f}',
                    xlabel='reset time', ylabel='entropy production / entropy')
    axes[1].axhline(0, color='black', lw=.8)
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(alpha=.2)
    fig.savefig(output/'comer_startup_findings.png', dpi=170)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/comer_andersson_startup')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--worker-memory-mib', type=int, default=1536)
    args = parser.parse_args()
    if args.workers < 1 or args.worker_memory_mib < 512:
        parser.error('positive worker count and at least 512 MiB address space required')
    if (args.output/'refined_curvature_probes.csv.gz').exists():
        parser.error('audit evidence already exists in this directory')
    started = time.monotonic()
    manifest = json.loads((args.output/'manifest.json').read_text())
    for path, expected in manifest['software_sha256'].items():
        assert sha256_file(ROOT/path) == expected, path
    reference = ROOT/'supporting_reports/data/le_coupled_reset_source/reference_tensors.csv.gz'
    assert sha256_file(reference) == manifest['reference_sha256']
    assert sha256_file(ROOT/'toolkit/adm_harness_cli/adm_harness/source_ledger.py') == manifest['source_kernel_sha256']
    main_files = {p.name: sha256_file(p) for p in args.output.iterdir() if p.is_file()}
    witnesses = pd.read_csv(args.output/'independent_curvature_probes.csv.gz', float_precision='round_trip')
    witnesses = witnesses[witnesses['mode'].eq('dynamic')].drop_duplicates(['scenario', 'level', 'sample'])
    tasks = [(name, group.to_dict('records'), str(reference), args.worker_memory_mib)
             for name, group in witnesses.groupby('scenario')]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(refine_scenario, tasks))
    refined = save_records([row for rows, _ in results for row in rows], args.output, 'refined_curvature_probes')
    systems = {}
    for stem in ['independent_curvature_probes', 'refined_curvature_probes']:
        result = verify_eigensystems(args.output, stem)
        result['classification_counts'] = {f'{mode}/{kind}': count for (mode, kind), count in result['classification_counts'].items()}
        systems[stem] = result
    fields = verify_fields(args.output)
    make_figure(args.output)
    for name, digest in main_files.items():
        assert sha256_file(args.output/name) == digest, name
    finest = refined[refined.h_s.eq(min(TIME_STEPS)) & refined['mode'].eq('dynamic')]
    metadata = {'completed_utc': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': time.monotonic()-started,
        'workers': args.workers, 'time_steps': TIME_STEPS, 'radial_step': .000625,
        'max_worker_peak_rss_kib': max(rss for _, rss in results),
        'witnesses': len(witnesses), 'refined_records': len(refined),
        'curvature_finest_step_by_scenario': finest.groupby('scenario')[[
            'dynamic_difference_max_error', 'dynamic_difference_relative_error']].max().to_dict('index'),
        'eigensystems': systems, 'field_verification': fields,
        'main_files_sha256': main_files, 'source_kernel_sha256': manifest['source_kernel_sha256'],
        'reference_sha256': manifest['reference_sha256'],
        'audit_software_sha256': sha256_file(Path(__file__)),
        'output_bytes_before_audit_manifest': sum(p.stat().st_size for p in args.output.iterdir() if p.is_file())}
    (args.output/'artifact_verification.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps({k: metadata[k] for k in ['elapsed_seconds', 'witnesses', 'refined_records',
        'curvature_finest_step_by_scenario', 'output_bytes_before_audit_manifest']}), flush=True)


if __name__ == '__main__':
    main()
