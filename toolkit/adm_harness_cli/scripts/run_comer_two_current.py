#!/usr/bin/env python3
"""Bounded two-current Einstein evolution and independent initial-junction audit."""
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

from run_le_geometry_boundary import ROOT, save_records
from adm_harness.comer_two_current import prepare_domain, evolve, resistance
from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.radial_stress import ETA, certify_radial_eigensystem, radial_tensor
from adm_harness.reset_inverse_search import reference_grid
from adm_harness.source_ledger import SourceParams, sha256_file


SCENARIOS = [
    ('low_preload_slow_drag', .01, 2., .04),
    ('low_preload_fast_drag', .01, .25, .04),
    ('high_preload_slow_drag', .1, 2., .04),
    ('zero_initial_drift', .01, 2., 0.),
]


def initial_junctions(reference, name, fraction):
    grid = reference_grid(reference, 2049, 2, path_kind='direct')
    rows = []
    for label, index in [('inner', 0), ('outer', -1)]:
        r, f = grid.r[index], grid.f[0, index]
        e, p = grid.energy[0, index], grid.pressure[0, index]
        preload = .039783*fraction*1e-8/r**2
        candidate_h = (1+.5*(.2+1/3))*preload
        jump_p = candidate_h-(e+p)
        rows.append({'scenario': name, 'boundary': label, 'radius': r, 'reference_f': f,
            'reference_energy': e, 'reference_radial_pressure': p, 'reference_radial_enthalpy': e+p,
            'candidate_radial_enthalpy': candidate_h,
            'radial_pressure_jump': jump_p,
            'normal_acceleration_jump': 4*np.pi*r*jump_p/np.sqrt(f),
            'zero_preload_pressure_jump_lower_bound': -(e+p),
            'initial_mass_jump': 0., 'initial_current_jump': 0.,
            'shell_free_initial_junction_pass': bool(abs(jump_p) < 1e-10)})
    return rows


def curvature_audit(domain, result, scenario, level):
    t, r, fields = result['time'], domain.r, result['fields']
    if len(t) < 8 or t[-1] <= 0:
        return []
    sf = RectBivariateSpline(t, r, np.log(fields['f']), kx=3, ky=3, s=0)
    sa = RectBivariateSpline(t, r, np.log(fields['alpha']), kx=3, ky=3, s=0)
    source = [RectBivariateSpline(t, r, fields[f'total_{k}'], kx=3, ky=3, s=0)
              for k in ['energy', 'radial', 'current', 'angular']]
    def provider(time_value, radius, params):
        return {'alpha': float(np.exp(sa.ev(time_value, radius))), 'beta': 0.,
                'gamma_ll': float(np.exp(-sf.ev(time_value, radius))), 'gamma_omega': radius*radius}
    rows = []
    sample = 0
    for time_index in [len(t)//4, len(t)//2, 3*len(t)//4]:
        peak = int(np.argmax(abs(fields['total_current'][time_index, 3:-3])))+3
        radii = sorted({3.2, 4.2, float(r[peak])})
        for radius in radii:
            time_value = float(t[time_index])
            channels = np.array([float(s.ev(time_value, radius)) for s in source])
            tensor = radial_tensor(*channels)
            source_row = certify_radial_eigensystem(tensor)
            source_row.update(tensor_orthonormal=tensor, raw_tensor_orthonormal=tensor.copy(),
                raw_eigenvalues=np.linalg.eigvals(ETA@tensor).astype(complex),
                s=time_value, l=radius, rho=channels[0], p_l=channels[1], j_l=channels[2],
                p_omega=channels[3], scenario=scenario, level=level, sample=sample, mode='source',
                h_s=0., h_l=0., max_source_mismatch=0.)
            rows.append(source_row)
            dr = r[1]-r[0]
            for factor in [1., .5, .25]:
                hs, hr = .01*factor, .25*dr*factor
                row = evaluate_demand(time_value, radius, SourceParams(), hs, hr, scalar_evaluator=provider)
                measured = np.array([row[k] for k in ['rho', 'p_l', 'j_l', 'p_omega']])
                errors = abs(measured-channels)
                row.update(scenario=scenario, level=level, sample=sample, mode='dynamic',
                    max_source_mismatch=float(errors.max()),
                    density_mismatch=float(errors[0]), radial_mismatch=float(errors[1]),
                    current_mismatch=float(errors[2]), angular_mismatch=float(errors[3]),
                    relative_source_mismatch=float(errors.max()/max(abs(channels).max(), 1e-30)))
                rows.append(row)
            sample += 1
    return rows


def run_scenario(task):
    name, fraction, relaxation, drift, reference, output, duration, deadline, memory_mib = task
    resource.setrlimit(resource.RLIMIT_AS, (memory_mib*1024**2, memory_mib*1024**2))
    summaries, records, probes = [], [], []
    for level, cells in enumerate([128, 256, 512]):
        domain, initial = prepare_domain(reference, cells, fraction, drift)
        result = evolve(domain, initial, relaxation, duration=duration, snapshots=81, deadline=deadline)
        f = result['fields']
        for row in result['records']:
            row.update(scenario=name, level=level, cells=cells)
            records.append(row)
        last = result['records'][-1]
        coefficient = (1.2*f['rest_n'])*(4*f['rest_s']/3)/(1.2*f['rest_n']+4*f['rest_s']/3)/relaxation
        summary = {'scenario': name, 'level': level, 'cells': cells, 'preload_fraction': fraction,
            'relaxation_scale': relaxation, 'initial_particle_drift': drift,
            'status': result['status'], 'steps': result['steps'], 'final_time': float(result['time'][-1]),
            'initial_preloaded_coordinate_mass': float(4*np.pi*(domain.volume@domain.initial_fluid_energy)),
            'initial_total_mass_change': 0., 'gr_tensor_kinetic_ratio': 1.,
            'min_resistance_coefficient': float(coefficient.min()), 'max_resistance_coefficient': float(coefficient.max()),
            'max_resistance_time_variation_factor': float((coefficient.max(axis=0)/coefficient.min(axis=0)).max()),
            'ordinary_sound_speeds': 'sqrt(1/5),sqrt(1/3)',
            'min_source_radial_discriminant': float(min(row['min_radial_discriminant'] for row in result['records'])),
            **{key: float(last[key]) for key in ['min_f', 'min_alpha', 'max_particle_speed', 'max_entropy_speed',
                'max_relative_drift', 'min_rest_energy', 'created_entropy', 'particle_balance_relative_error',
                'entropy_balance_relative_error', 'outer_mass_balance_error', 'max_current', 'max_mass_change']}}
        summary['initial_junction_pass'] = False
        summary['full_rail_candidate_pass'] = False
        summaries.append(summary)
        np.savez_compressed(Path(output)/f'{name}_level_{level}.npz', time=result['time'], radius=domain.r,
            faces=domain.faces, volume=domain.volume, support_energy=domain.support_energy,
            support_transverse=domain.support_transverse, reference_mass=domain.reference_mass,
            reference_alpha=domain.reference_alpha, reference_pressure=domain.reference_pressure,
            reference_transverse=domain.reference_transverse,
            initial_fluid_energy=domain.initial_fluid_energy, **f)
        probes.extend(curvature_audit(domain, result, name, level))
    return {'summaries': summaries, 'history': records, 'probes': probes,
            'junctions': initial_junctions(reference, name, fraction),
            'worker_peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def plot_results(output, summaries):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    with np.load(output/'low_preload_slow_drag_level_2.npz') as data:
        axes[0, 0].plot(data['radius'], data['mass'][0], label='initial mass')
        axes[0, 0].plot(data['radius'], data['mass'][-1], '--', label='evolved mass')
        axes[0, 0].set(xlabel='areal radius', ylabel='enclosed geometric mass', title='Geometry responds to both flows')
        axes[0, 0].legend(fontsize=8)
        for name, label in [('n', 'particles'), ('s', 'entropy')]:
            axes[0, 1].plot(data['radius'], data[f'velocity_{name}'][len(data['time'])//2], label=label)
        axes[0, 1].set(xlabel='areal radius', ylabel='radial velocity', title='Independent velocities at mid-run')
        axes[0, 1].legend(fontsize=8)
    history = pd.read_csv(output/'history.csv')
    for name, group in history[history.level.eq(2)].groupby('scenario'):
        axes[1, 0].plot(group.time, group.created_entropy, label=name.replace('_', ' '))
    axes[1, 0].set(xlabel='evolution time', ylabel='integrated physical entropy production', title='Covariant resistance produces entropy')
    axes[1, 0].legend(fontsize=7)
    for name, group in summaries.groupby('scenario'):
        error = np.maximum(abs(group.particle_balance_relative_error), abs(group.entropy_balance_relative_error))
        axes[1, 1].loglog(group.cells, error, 'o-', label=name.replace('_', ' '))
    axes[1, 1].set(xlabel='radial cells', ylabel='maximum relative current-balance error', title='Particle and entropy convergence')
    for ax in axes.ravel():
        ax.grid(alpha=.2)
    fig.savefig(output/'two_current_evolution.png', dpi=170)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--duration', type=float, default=4.)
    parser.add_argument('--budget-seconds', type=float, default=600.)
    parser.add_argument('--worker-memory-mib', type=int, default=1536)
    parser.add_argument('--output-cap-mb', type=float, default=80.)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/comer_two_current')
    args = parser.parse_args()
    if args.workers < 1 or args.duration <= 0 or args.budget_seconds <= 0 or args.output_cap_mb <= 0:
        parser.error('positive worker count, duration, and budgets required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    reference = ROOT/'supporting_reports/data/le_coupled_reset_source/reference_tensors.csv.gz'
    kernel = ROOT/'toolkit/adm_harness_cli/adm_harness/source_ledger.py'
    previous = json.loads((ROOT/'supporting_reports/data/comer_andersson_startup/manifest.json').read_text())
    assert sha256_file(reference) == previous['reference_sha256']
    assert sha256_file(kernel) == previous['source_kernel_sha256']
    tasks = [(name, fraction, relaxation, drift, str(reference), str(args.output), args.duration,
              started+args.budget_seconds, args.worker_memory_mib) for name, fraction, relaxation, drift in SCENARIOS]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(run_scenario, tasks))
    frames = {}
    for key in ['summaries', 'history', 'junctions']:
        frame = pd.DataFrame([row for result in results for row in result[key]])
        frame.to_csv(args.output/f'{key}.csv', index=False)
        frames[key] = frame
    probe_frame = save_records([row for result in results for row in result['probes']], args.output, 'curvature_probes')
    assert probe_frame.full_eigensystem_certified.all()
    grid = reference_grid(reference, 2049, 2, path_kind='direct')
    pd.DataFrame({'radius': grid.r, 'f': grid.f[0], 'alpha': np.exp(grid.nu[0]), 'energy': grid.energy[0],
        'radial_pressure': grid.pressure[0], 'angular_pressure': grid.transverse[0],
        'radial_enthalpy': grid.energy[0]+grid.pressure[0]}).to_csv(args.output/'reference_initial_profile.csv', index=False)
    plot_results(args.output, frames['summaries'])
    size = sum(path.stat().st_size for path in args.output.iterdir() if path.is_file())
    if size > args.output_cap_mb*1e6:
        raise RuntimeError('output budget exceeded')
    metadata = {'completed_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'coupled_evolution_measured_with_failed_initial_rail_junctions',
        'elapsed_seconds': time.monotonic()-started, 'workers': args.workers, 'scenarios': len(tasks),
        'evolutions': len(frames['summaries']), 'curvature_records': len(probe_frame),
        'evolution_status_counts': frames['summaries'].status.value_counts().to_dict(),
        'max_worker_peak_rss_kib': max(result['worker_peak_rss_kib'] for result in results),
        'parent_peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'worker_address_space_cap_mib': args.worker_memory_mib,
        'compute_cap_seconds': args.budget_seconds, 'output_cap_mb': args.output_cap_mb,
        'output_bytes_before_manifest': size, 'full_rail_candidate_pass': False,
        'signed_support_microscopic_dynamics_certified': False,
        'general_comer_framework_excluded': False,
        'source_kernel_sha256': sha256_file(kernel), 'reference_sha256': sha256_file(reference),
        'software_sha256': {str(path.relative_to(ROOT)): sha256_file(path) for path in [Path(__file__).resolve(),
            ROOT/'toolkit/adm_harness_cli/adm_harness/comer_two_current.py',
            ROOT/'toolkit/adm_harness_cli/adm_harness/reset_inverse_search.py']},
        'primary_paper': 'https://arxiv.org/html/2606.17686v1',
        'constitutive_scope': 'barotropic two-current force equations with positive covariant resistance; separately conserved radial-tension support'}
    (args.output/'manifest.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps({key: metadata[key] for key in ['status', 'elapsed_seconds', 'evolutions',
        'evolution_status_counts', 'curvature_records', 'output_bytes_before_manifest']}), flush=True)


if __name__ == '__main__':
    main()
