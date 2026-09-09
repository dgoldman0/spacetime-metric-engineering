#!/usr/bin/env python3
"""Bounded Gaussian quantum-field / moving-wall comparisons and raw evidence."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from datetime import datetime, timezone
import json
import multiprocessing
from pathlib import Path
import resource
import time

import numpy as np
import pandas as pd

from adm_harness.quantum_boundary import PlanarField, prepare_mechanics, evolve
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
LEVELS = [(16, 8, .02), (24, 12, .01), (32, 16, .005)]
SCENARIOS = [('equilibrium', 1., .5, 0.), ('released', 1., 0., 0.),
             ('released_light', .25, 0., 0.), ('moving_held', 1., .5, .02)]


def run_case(task):
    name, mass, stiffness, velocity, harmonics, nodes, step, output, deadline, memory_mib = task
    resource.setrlimit(resource.RLIMIT_AS, (memory_mib*1024**2, memory_mib*1024**2))
    started = time.monotonic()
    field = PlanarField(harmonics, nodes)
    mechanics = prepare_mechanics(field, mass, stiffness)
    label = f'{name}_m{harmonics}_k{nodes}_h{step:g}'
    result = evolve(field, mechanics, velocity, step=step, deadline=deadline)
    history = pd.DataFrame(result['histories'])
    history.to_csv(Path(output)/f'{label}_history.csv', index=False)
    profiles = []
    for profile in result['profiles']:
        points = pd.DataFrame({'time': profile['time'], 'separation': profile['separation'],
            'coupling_factor': profile['coupling_factor'], 'z': profile['z'],
            'phi_squared': profile['phi_squared']})
        for k, key in enumerate(['energy', 'current', 'radial', 'angular']):
            points[key] = profile['free_subtracted_channels'][:, k]
        points['radial_enthalpy'] = points.energy+points.radial
        profiles.append(points)
    pd.concat(profiles, ignore_index=True).to_csv(Path(output)/f'{label}_profiles.csv.gz', index=False)
    np.savez_compressed(Path(output)/f'{label}_final.npz', f=result['f'], p=result['p'],
        free=field.free, initial_operator=field.operator(1.),
        final_operator=field.operator(history.iloc[-1].separation),
        final_derivative=field.operator(history.iloc[-1].separation, 1),
        transverse=field.transverse, weights=field.weights)
    final = history.iloc[-1]
    return {'case': label, 'scenario': name, 'harmonics': harmonics, 'nodes': nodes,
        'step': step, 'wall_mass': mass, 'stiffness': stiffness, 'initial_velocity': velocity,
        'natural_separation': mechanics.natural, 'holding_mass': mechanics.holding_mass,
        'bare_inertia': mechanics.inertia, 'status': result['status'],
        'final_time': final.time, 'final_separation': final.separation,
        'final_velocity': final.separation_velocity,
        'initial_interaction_energy': history.iloc[0].vacuum_interaction_energy,
        'initial_single_wall_dressing': field.single_energy-field.free_energy,
        'initial_quantum_force': history.iloc[0].quantum_force,
        'min_total_inertia': history.total_rest_separation_inertia.min(),
        'max_abs_energy_balance_error': abs(history.energy_balance_error).max(),
        'mode_normalization_error': result['mode_normalization_error'],
        'max_excitation': history.excitation_above_instantaneous_ground.max(),
        'min_excitation': history.excitation_above_instantaneous_ground.min(),
        'max_abs_nonadiabatic_force': abs(history.nonadiabatic_force).max(),
        'max_abs_field_energy_change': abs(history.field_energy_change).max(),
        'min_complete_regulated_energy': history.complete_regulated_energy.min(),
        'min_holding_energy_margin': history.holding_energy_margin.min(),
        'initial_center_energy': profiles[0].iloc[len(profiles[0])//2].energy,
        'initial_center_radial_enthalpy': profiles[0].iloc[len(profiles[0])//2].radial_enthalpy,
        'max_step_iterations': result['max_iterations'], 'elapsed_seconds': time.monotonic()-started,
        'worker_peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def static_case(task):
    harmonics, nodes, cutoff = task
    field = PlanarField(harmonics, nodes, cutoff=cutoff)
    rows = []
    free_f, free_p = field.operator_ground_state(field.free)
    _, free_channels, _ = field.spatial_profile(free_f, free_p, 1., coupling_factor=0.)
    for separation in [.7, 1., 1.2]:
        f, p = field.ground_state(separation)
        z, channels, _ = field.spatial_profile(f, p, separation)
        channels -= free_channels
        h = .002
        derivative = (field.interaction_energy(separation-2*h)-8*field.interaction_energy(separation-h)
                      +8*field.interaction_energy(separation+h)-field.interaction_energy(separation+2*h))/(12*h)
        center = len(z)//2
        rows.append({'harmonics': harmonics, 'nodes': nodes, 'cutoff': cutoff, 'separation': separation,
            'interaction_energy': field.interaction_energy(separation), 'force': field.ground_force(separation),
            'force_energy_derivative_error': field.ground_force(separation)+derivative,
            'single_wall_dressing': field.single_energy-field.free_energy,
            'two_wall_free_subtracted_energy': field.ground_energy(field.operator(separation))-field.free_energy,
            'interaction_inertia': field.interaction_expectation(f, separation)/4,
            'center_energy': channels[center, 0],
            'center_radial_enthalpy': channels[center, 0]+channels[center, 2],
            'min_frequency': field.spectrum(field.operator(separation))[0].min()})
    return rows


def plot_results(output, summaries):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    for name in ['released', 'released_light', 'moving_held']:
        row = summaries[summaries.scenario.eq(name) & summaries.harmonics.eq(32)].iloc[0]
        data = pd.read_csv(output/f'{row["case"]}_history.csv', float_precision='round_trip')
        axes[0, 0].plot(data.time, data.separation, label=name.replace('_', ' '))
        axes[0, 1].plot(data.time, data.excitation_above_instantaneous_ground, label=name.replace('_', ' '))
    moving = summaries[summaries.scenario.eq('moving_held') & summaries.harmonics.eq(32)].iloc[0]
    data = pd.read_csv(output/f'{moving["case"]}_history.csv', float_precision='round_trip')
    axes[1, 0].plot(data.time, data.field_energy_change, label='field')
    axes[1, 0].plot(data.time, data.mechanical_energy_change, label='mechanical')
    profiles = pd.read_csv(output/f'{moving["case"]}_profiles.csv.gz', float_precision='round_trip')
    for instant in [profiles.time.min(), profiles.time.max()]:
        profile = profiles[profiles.time.eq(instant) & profiles.z.abs().lt(1.)]
        axes[1, 1].plot(profile.z, profile.radial_enthalpy, label=f't = {instant:.2f}')
    axes[0, 0].set(title='Self-consistent wall motion', xlabel='time / initial gap', ylabel='gap / initial gap')
    axes[0, 1].set(title='Field excitation above moving instantaneous ground', xlabel='time / initial gap', ylabel='energy / area')
    axes[1, 0].set(title='Energy exchanged in moving held case', xlabel='time / initial gap', ylabel='change in energy / area')
    axes[1, 1].set(title='Free-subtracted scalar radial enthalpy', xlabel='normal position / initial gap', ylabel='energy + normal pressure')
    for ax in axes.ravel():
        ax.axhline(0., color='black', linewidth=.5)
        ax.grid(alpha=.2)
        ax.legend(fontsize=8)
    fig.savefig(output/'moving_boundary_findings.png', dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--budget-seconds', type=float, default=600.)
    parser.add_argument('--worker-memory-mib', type=int, default=1536)
    parser.add_argument('--output-cap-mb', type=float, default=40.)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/quantum_boundary')
    args = parser.parse_args()
    if not 1 <= args.workers <= 6 or min(args.budget_seconds, args.worker_memory_mib, args.output_cap_mb) <= 0:
        parser.error('one to six workers and positive resource budgets required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    sources = [ROOT/'toolkit/adm_harness_cli/adm_harness/quantum_boundary.py', Path(__file__).resolve(),
        ROOT/'toolkit/adm_harness_cli/adm_harness/source_ledger.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/reset_inverse_search.py',
        ROOT/'supporting_reports/data/le_coupled_reset_source/reference_tensors.csv.gz',
        ROOT/'supporting_reports/data/comer_two_current/reference_initial_profile.csv']
    hashes = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    choices = [(scenario, level) for scenario in SCENARIOS for level in LEVELS]
    # Fixed bandwidth isolates temporal accuracy from changes in field dressing.
    choices += [(scenario, (24, 12, step)) for scenario in SCENARIOS if scenario[0] in ['released', 'moving_held']
                for step in [.02, .005]]
    tasks = [(*scenario, *level, str(args.output), started+args.budget_seconds, args.worker_memory_mib)
             for scenario, level in choices]
    static_tasks = [(m, n, cut) for m, n in [(16, 8), (24, 12), (32, 16), (48, 24)] for cut in [8., 12.]]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        summaries = pd.DataFrame(list(pool.map(run_case, tasks)))
        static_rows = [row for rows in pool.map(static_case, static_tasks) for row in rows]
    summaries.to_csv(args.output/'summaries.csv', index=False)
    pd.DataFrame(static_rows).to_csv(args.output/'static_cutoffs.csv', index=False)
    reference = pd.read_csv(sources[-1], float_precision='round_trip')
    rail_screen = {'reference_points': len(reference), 'negative_energy_points': int((reference.energy < 0).sum()),
        'negative_radial_enthalpy_points': int((reference.radial_enthalpy < 0).sum()),
        'min_energy': float(reference.energy.min()), 'max_energy': float(reference.energy.max()),
        'min_radial_enthalpy': float(reference.radial_enthalpy.min()),
        'min_complete_cell_energy': float(summaries.min_complete_regulated_energy.min()),
        'positive_whole_cell_arrays_pass_reference_energy_sign': False,
        'scope': 'Locally homogenized complete cells including exterior field, finite-cutoff dressing, positive bare walls and holding structure.'}
    (args.output/'rail_screen.json').write_text(json.dumps(rail_screen, indent=2)+'\n')
    plot_results(args.output, summaries)
    for p in sources:
        if sha256_file(p) != hashes[str(p.relative_to(ROOT))]:
            raise RuntimeError(f'input changed during run: {p}')
    elapsed = time.monotonic()-started
    size = sum(p.stat().st_size for p in args.output.iterdir())
    if elapsed > args.budget_seconds or size > args.output_cap_mb*1e6:
        raise RuntimeError('registered compute or evidence allowance exceeded')
    manifest = {'created_utc': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': elapsed,
        'workers': args.workers, 'worker_memory_mib': args.worker_memory_mib,
        'max_worker_peak_rss_kib': int(summaries.worker_peak_rss_kib.max()),
        'evidence_bytes_before_manifest': size, 'source_hashes': hashes,
        'field': asdict(PlanarField(32, 16)), 'levels': LEVELS, 'scenarios': SCENARIOS,
        'evolutions': len(summaries), 'duration_completed': int(summaries.status.eq('duration_completed').sum()),
        'static_comparisons': len(static_rows),
        'scope': 'Finite Gaussian scalar field, semiclassical wall separation, positive proper-time interaction inertia; local planar source prototype.'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
