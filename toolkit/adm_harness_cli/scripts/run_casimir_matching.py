#!/usr/bin/env python3
"""Matched-mass Casimir support screen and retained-rail placement comparison."""
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

from adm_harness.casimir_matching import interaction, gap_profile, interaction_partition, gaussian_overlap, reference_placement
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
LEVELS = [128, 256, 512]


def parameter_pairs():
    equal = [float(f'{x:.12g}') for x in np.logspace(-4, 4, 81)]
    decade = [float(x) for x in np.logspace(-4, 4, 9)]
    return sorted(set([(x, x) for x in equal]+[(x, y) for x in decade for y in decade]+[(8., 8.)]))


def calculate(task):
    first, second, memory_mib, deadline = task
    resource.setrlimit(resource.RLIMIT_AS, (memory_mib*1024**2, memory_mib*1024**2))
    rows, profiles, partitions = [], [], []
    for nodes in LEVELS:
        if time.monotonic() > deadline:
            raise TimeoutError('registered compute allowance exhausted')
        result = interaction(1., first, second, nodes)
        rows.append({'lambda1': first, 'lambda2': second, 'nodes': nodes, **result,
            'measured_mass_025_released_energy': .5+result['energy'],
            'measured_mass_025_held_floor': .5+result['zero_wall_mass_held_energy_floor'],
            'measured_mass_1_released_energy': 2.+result['energy'],
            'measured_mass_1_held_floor': 2.+result['zero_wall_mass_held_energy_floor'],
            'released_zero_energy_mass_per_wall': -result['energy']/2})
        if first == second and first in [.01, 1., 8., 100.]:
            fractions = np.linspace(.05, .95, 19)
            for xi in [0., 1/6]:
                channels = gap_profile(1., first, second, fractions, xi, nodes)
                for fraction, values in zip(fractions, channels):
                    profiles.append({'lambda1': first, 'lambda2': second, 'nodes': nodes, 'xi': xi,
                        'fraction': fraction, 'energy': values[0], 'normal_pressure': values[1],
                        'transverse_pressure': values[2], 'radial_enthalpy': values[0]+values[1]})
    for xi in [0., 1/6, .25]:
        partitions.append({'lambda1': first, 'lambda2': second, 'xi': xi,
                           **interaction_partition(1., first, second, xi)})
    return {'rows': rows, 'profiles': profiles, 'partitions': partitions,
            'worker_peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def plot_results(output, results, profiles, reference):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    local = profiles[profiles.nodes.eq(512) & profiles.lambda1.eq(8.)]
    for xi, label in [(0., 'canonical scalar'), (1/6, 'conformal control')]:
        p = local[np.isclose(local.xi, xi)]
        axes[0, 0].semilogy(p.fraction, -p.radial_enthalpy, label=label)
    axes[0, 0].set(title='Continuum negative gap enthalpy', xlabel='gap fraction', ylabel='magnitude of energy + normal pressure')
    equal = results[results.nodes.eq(512) & results.lambda1.eq(results.lambda2)]
    axes[0, 1].semilogx(equal.lambda1, equal.effective_exponent, label='holding energy / binding magnitude')
    axes[0, 1].axhline(1., color='black', linewidth=.7, linestyle='--', label='equal cost and binding')
    axes[0, 1].set(title='Ordinary holding cost', xlabel='sheet coupling × gap', ylabel='energy ratio')
    axes[1, 0].plot(reference.radius, reference.energy, label='required energy')
    axes[1, 0].plot(reference.radius, reference.radial_enthalpy, label='required radial enthalpy')
    axes[1, 0].axhline(0., color='black', linewidth=.5)
    axes[1, 0].set(title='Initial rail source', xlabel='areal radius', ylabel='density in rail units')
    axes[1, 1].plot(reference.radius, reference.radius*(1-reference.f)/2, label='enclosed Misner–Sharp mass')
    axes[1, 1].set(title='Positive enclosed mass with an annular decrease', xlabel='areal radius', ylabel='mass in rail units')
    for ax in axes.ravel():
        ax.grid(alpha=.2)
        ax.legend(fontsize=8)
    fig.savefig(output/'matched_boundary_findings.png', dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--budget-seconds', type=float, default=300.)
    parser.add_argument('--worker-memory-mib', type=int, default=1536)
    parser.add_argument('--output-cap-mb', type=float, default=8.)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/casimir_mass_matching')
    args = parser.parse_args()
    if not 1 <= args.workers <= 6 or min(args.budget_seconds, args.worker_memory_mib, args.output_cap_mb) <= 0:
        parser.error('one to six workers and positive resource allowances required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    sources = [Path(__file__).resolve(), ROOT/'toolkit/adm_harness_cli/adm_harness/casimir_matching.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/source_ledger.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/reset_inverse_search.py',
        ROOT/'supporting_reports/data/le_coupled_reset_source/reference_tensors.csv.gz',
        ROOT/'supporting_reports/data/comer_two_current/reference_initial_profile.csv',
        ROOT/'supporting_reports/data/quantum_boundary/static_cutoffs.csv']
    hashes = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    tasks = [(first, second, args.worker_memory_mib, started+args.budget_seconds) for first, second in parameter_pairs()]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        calculations = list(pool.map(calculate, tasks))
    results = pd.DataFrame([r for c in calculations for r in c['rows']])
    profiles = pd.DataFrame([r for c in calculations for r in c['profiles']])
    partitions = pd.DataFrame([r for c in calculations for r in c['partitions']])
    results.to_csv(args.output/'interaction_summaries.csv', index=False)
    profiles.to_csv(args.output/'gap_profiles.csv.gz', index=False)
    partitions.to_csv(args.output/'boundary_partitions.csv', index=False)
    gaussian = pd.read_csv(sources[-1], float_precision='round_trip')
    gaussian['potential_overlap'] = gaussian_overlap(gaussian.separation)
    gaussian['joint_uv_log_interaction_coefficient'] = -gaussian.potential_overlap/(16*np.pi**2)
    gaussian['isolated_mass_only_held_floor'] = gaussian.interaction_energy-gaussian.separation*gaussian.force
    gaussian['isolated_mass_only_released_energy_with_mass_1'] = 2+gaussian.interaction_energy
    gaussian.to_csv(args.output/'gaussian_accounting_comparison.csv', index=False)
    reference = pd.read_csv(sources[-2], float_precision='round_trip')
    reference.to_csv(args.output/'rail_placement_profile.csv.gz', index=False)
    placement = [reference_placement(reference.iloc[::stride]) for stride in [4, 2, 1]]
    pd.DataFrame(placement).to_csv(args.output/'rail_placement_levels.csv', index=False)
    (args.output/'rail_placement.json').write_text(json.dumps(placement[-1], indent=2)+'\n')
    plot_results(args.output, results, profiles, reference)
    for path in sources:
        if sha256_file(path) != hashes[str(path.relative_to(ROOT))]:
            raise RuntimeError(f'input changed during run: {path}')
    elapsed = time.monotonic()-started
    size = sum(p.stat().st_size for p in args.output.iterdir())
    if elapsed > args.budget_seconds or size > args.output_cap_mb*1e6:
        raise RuntimeError('registered compute or evidence allowance exceeded')
    manifest = {'created_utc': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': elapsed,
        'workers': args.workers, 'worker_memory_mib': args.worker_memory_mib,
        'max_worker_peak_rss_kib': max(c['worker_peak_rss_kib'] for c in calculations),
        'evidence_bytes_before_manifest': size, 'source_hashes': hashes,
        'parameter_pairs': len(tasks), 'quadrature_levels': LEVELS,
        'interaction_comparisons': len(results), 'gap_stress_rows': len(profiles),
        'boundary_partitions': len(partitions),
        'all_held_floors_positive': bool((results.zero_wall_mass_held_energy_floor > 0).all()),
        'all_gap_radial_enthalpies_negative': bool((profiles.radial_enthalpy < 0).all()),
        'scope': 'Disjoint scalar sheets with fixed isolated physical masses; exact static continuum interaction, bulk stress and surface binding; necessary initial rail placement constraints.'}
    (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
