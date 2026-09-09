#!/usr/bin/env python3
"""Replay two-current artifacts and refine the retained narrow Type-I margins."""
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
from scipy.interpolate import RectBivariateSpline

from run_comer_two_current import SCENARIOS
from run_comer_andersson_audit import verify_eigensystems
from run_le_geometry_boundary import ROOT, save_records
from adm_harness.comer_two_current import prepare_domain, evolve
from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.radial_stress import ETA, certify_radial_eigensystem, radial_tensor
from adm_harness.source_ledger import SourceParams, sha256_file


def refine(task):
    name, fraction, relaxation, drift, reference, output, witnesses, deadline = task
    resource.setrlimit(resource.RLIMIT_AS, (1536*1024**2, 1536*1024**2))
    domain, initial = prepare_domain(reference, 1024, fraction, drift)
    result = evolve(domain, initial, relaxation, duration=4., snapshots=161, deadline=deadline)
    if result['status'] != 'duration_completed':
        raise RuntimeError(f'{name}: {result["status"]}')
    f, t, r = result['fields'], result['time'], domain.r
    sf = RectBivariateSpline(t, r, np.log(f['f']), kx=3, ky=3, s=0)
    sa = RectBivariateSpline(t, r, np.log(f['alpha']), kx=3, ky=3, s=0)
    source = [RectBivariateSpline(t, r, f[f'total_{key}'], kx=3, ky=3, s=0)
              for key in ['energy', 'radial', 'current', 'angular']]
    def metric(tv, rv, params):
        return {'alpha': float(np.exp(sa.ev(tv, rv))), 'beta': 0.,
                'gamma_ll': float(np.exp(-sf.ev(tv, rv))), 'gamma_omega': rv*rv}
    rows = []
    for witness in witnesses:
        tv, rv = witness['s'], witness['l']
        channels = np.array([float(s.ev(tv, rv)) for s in source])
        tensor = radial_tensor(*channels)
        row = certify_radial_eigensystem(tensor)
        row.update(s=tv, l=rv, scenario=name, level=3, cells=1024, sample=witness['sample'], mode='source',
            rho=channels[0], p_l=channels[1], j_l=channels[2], p_omega=channels[3],
            h_s=0., h_l=0., max_source_mismatch=0.,
            tensor_orthonormal=tensor, raw_tensor_orthonormal=tensor.copy(),
            raw_eigenvalues=np.linalg.eigvals(ETA@tensor).astype(complex))
        rows.append(row)
        for index, hs in enumerate([.0025, .00125, .000625]):
            hr = (r[1]-r[0])/(4*2**index)
            row = evaluate_demand(tv, rv, SourceParams(), hs, hr, scalar_evaluator=metric)
            errors = abs(np.array([row[k] for k in ['rho', 'p_l', 'j_l', 'p_omega']])-channels)
            row.update(scenario=name, level=3, cells=1024, sample=witness['sample'], mode='dynamic',
                max_source_mismatch=float(errors.max()), relative_source_mismatch=float(errors.max()/max(abs(channels).max(), 1e-30)),
                density_mismatch=float(errors[0]), radial_mismatch=float(errors[1]),
                current_mismatch=float(errors[2]), angular_mismatch=float(errors[3]))
            rows.append(row)
    np.savez_compressed(Path(output)/f'refinement_{name}_final.npz', radius=r,
        **{key: value[-1] for key, value in f.items()}, support_energy=domain.support_energy,
        support_transverse=domain.support_transverse, reference_mass=domain.reference_mass)
    history = result['records']
    for row in history:
        row.update(scenario=name, level=3, cells=1024)
    return {'probes': rows, 'history': history, 'summary': history[-1],
            'worker_peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def verify_fields(output):
    history = pd.read_csv(output/'history.csv', float_precision='round_trip')
    records = []
    for name, _, _, _ in SCENARIOS:
        for level in range(3):
            with np.load(output/f'{name}_level_{level}.npz') as d:
                assert all(np.isfinite(d[key]).all() for key in d.files)
                n, s = [], []
                plus, minus = np.zeros_like(d['energy_n']), np.zeros_like(d['energy_n'])
                radial, angular = -d['support_energy'].copy(), d['support_transverse'].copy()
                radial = np.broadcast_to(radial, d['energy_n'].shape).copy()
                angular = np.broadcast_to(angular, d['energy_n'].shape).copy()
                for label, w in [('n', .2), ('s', 1/3)]:
                    e, j = d[f'energy_{label}'], d[f'current_{label}']
                    assert (e > abs(j)).all()
                    root = np.sqrt((1+w)**2*e*e-4*w*j*j)
                    rest = 2*(e*e-j*j)/((1-w)*e+root)
                    np.testing.assert_allclose(rest, d[f'rest_{label}'], rtol=2e-12, atol=1e-20)
                    v, gamma = d[f'velocity_{label}'], d[f'gamma_{label}']
                    np.testing.assert_allclose(j, (1+w)*rest*gamma*gamma*v, rtol=2e-12, atol=1e-18)
                    h = (1+w)*rest*gamma*gamma
                    plus += h*(1+v)**2
                    minus += h*(1-v)**2
                    radial += h*v*v+w*rest
                    angular += w*rest
                    count = 4*np.pi*np.sum(d['volume']*rest**(1/(1+w))*gamma/np.sqrt(d['f']), axis=1)
                    if label == 'n':
                        n = count
                    else:
                        s = count
                np.testing.assert_allclose(d['total_energy'], d['support_energy']+d['energy_n']+d['energy_s'], atol=1e-16)
                np.testing.assert_allclose(d['total_current'], d['current_n']+d['current_s'], atol=1e-16)
                np.testing.assert_allclose(radial, d['total_radial'], rtol=1e-12, atol=1e-16)
                np.testing.assert_allclose(angular, d['total_angular'], rtol=1e-12, atol=1e-16)
                delta = plus*minus
                assert np.min(delta) > 0
                h = d['total_energy']+d['total_radial']
                np.testing.assert_allclose(h*h-4*d['total_current']**2, delta, rtol=1e-7, atol=1e-20)
                reference = history[history.scenario.eq(name) & history.level.eq(level)]
                np.testing.assert_array_equal(reference.time.to_numpy(), d['time'])
                np.testing.assert_allclose(n, reference.particle_number, rtol=2e-12)
                np.testing.assert_allclose(s, reference.entropy, rtol=2e-12)
                # Independent shell integration of the energy change.
                de = d['energy_n']+d['energy_s']-d['initial_fluid_energy']
                dm = 4*np.pi*de*d['volume']
                inner_change = d['face_mass'][:, 0]-d['face_mass'][0, 0]
                expected_faces = d['face_mass'][0]+inner_change[:, None]+np.c_[np.zeros(len(dm)), np.cumsum(dm, axis=1)]
                np.testing.assert_allclose(expected_faces, d['face_mass'], rtol=1e-13, atol=1e-14)
                records.append({'scenario': name, 'level': level, 'points': int(d['energy_n'].size),
                    'min_analytic_radial_discriminant': float(delta.min()),
                    'max_particle_integral_replay_error': float(abs(n-reference.particle_number.to_numpy()).max()),
                    'max_entropy_integral_replay_error': float(abs(s-reference.entropy.to_numpy()).max())})
    return records


def make_figure(output, refined):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for name, label in [('low_preload_slow_drag', 'low preload'), ('high_preload_slow_drag', 'high preload')]:
        with np.load(output/f'refinement_{name}_final.npz') as d:
            axes[0].plot(d['radius'], d['mass']-d['reference_mass'], label=label)
    axes[0].set(xlabel='areal radius', ylabel='change in enclosed geometric mass', title='Computed mass redistribution at time 4')
    axes[0].legend(fontsize=8)
    original = pd.read_csv(output/'curvature_probes.csv.gz')
    original = original[(original['mode']=='dynamic') & original.h_s.eq(.0025)]
    original['cells'] = 128*2**original.level
    final = refined[(refined['mode']=='dynamic') & refined.h_s.eq(.000625)]
    combined = pd.concat([original, final], ignore_index=True)
    for name, group in combined.groupby('scenario'):
        maxima = group.groupby('cells').max_source_mismatch.max()
        axes[1].loglog(maxima.index, maxima, 'o-', label=name.replace('_', ' '))
    axes[1].set(xlabel='radial cells', ylabel='maximum absolute four-channel discrepancy', title='Independent Einstein-tensor comparison')
    axes[1].legend(fontsize=7)
    for ax in axes:
        ax.grid(alpha=.2)
    fig.savefig(output/'two_current_audit.png', dpi=170)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/comer_two_current')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('positive worker count required')
    if (args.output/'refined_curvature_probes.csv.gz').exists():
        parser.error('audit output already exists')
    started = time.monotonic()
    main_files = {path.name: sha256_file(path) for path in args.output.iterdir() if path.is_file()}
    manifest = json.loads((args.output/'manifest.json').read_text())
    for path, digest in manifest['software_sha256'].items():
        assert sha256_file(ROOT/path) == digest, path
    reference = ROOT/'supporting_reports/data/le_coupled_reset_source/reference_tensors.csv.gz'
    assert sha256_file(reference) == manifest['reference_sha256']
    assert sha256_file(ROOT/'toolkit/adm_harness_cli/adm_harness/source_ledger.py') == manifest['source_kernel_sha256']
    field_results = verify_fields(args.output)
    original = pd.read_csv(args.output/'curvature_probes.csv.gz', float_precision='round_trip')
    witnesses = original[original['mode'].eq('source') & original.level.eq(2)]
    tasks = [(name, fraction, relaxation, drift, str(reference), str(args.output),
              witnesses[witnesses.scenario.eq(name)].to_dict('records'), started+600.)
             for name, fraction, relaxation, drift in SCENARIOS]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(refine, tasks))
    frame = save_records([row for result in results for row in result['probes']], args.output, 'refined_curvature_probes')
    pd.DataFrame([row for result in results for row in result['history']]).to_csv(args.output/'refinement_history.csv', index=False)
    systems = {}
    for stem in ['curvature_probes', 'refined_curvature_probes']:
        result = verify_eigensystems(args.output, stem)
        result['classification_counts'] = {f'{mode}/{kind}': count for (mode, kind), count in result['classification_counts'].items()}
        systems[stem] = result
    make_figure(args.output, frame)
    for name, digest in main_files.items():
        assert sha256_file(args.output/name) == digest, name
    finest = frame[frame['mode'].eq('dynamic') & frame.h_s.eq(.000625)]
    metadata = {'completed_utc': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': time.monotonic()-started,
        'refinement_cells': 1024, 'refinement_snapshots': 161, 'workers': args.workers,
        'main_fields_verified': field_results, 'refinement_final_balances': [result['summary'] for result in results],
        'eigensystems': systems, 'finest_curvature_by_scenario': finest.groupby('scenario')[[
            'max_source_mismatch', 'relative_source_mismatch', 'current_mismatch', 'angular_mismatch']].max().to_dict('index'),
        'finest_dynamic_type_counts': finest.stress_algebraic_type.value_counts().to_dict(),
        'max_worker_peak_rss_kib': max(result['worker_peak_rss_kib'] for result in results),
        'main_files_sha256': main_files, 'reference_sha256': manifest['reference_sha256'],
        'source_kernel_sha256': manifest['source_kernel_sha256'], 'audit_software_sha256': sha256_file(Path(__file__)),
        'output_bytes_before_verification': sum(path.stat().st_size for path in args.output.iterdir() if path.is_file())}
    (args.output/'artifact_verification.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps({key: metadata[key] for key in ['elapsed_seconds', 'finest_curvature_by_scenario',
        'finest_dynamic_type_counts', 'output_bytes_before_verification']}), flush=True)


if __name__ == '__main__':
    main()
