#!/usr/bin/env python3
"""Plot the measured velocity, thermal, and stress tradeoff of the new assembly."""
from pathlib import Path
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from adm_harness.source_ledger import sha256_file
from audit_material_ensemble import ROOT, OUTPUT as ARCHIVE, load_case

DATA = ROOT/'supporting_reports/data/prestressed_buffer_assembly'
FIGURES = ROOT/'supporting_reports/figures'
OLD = 'relaxing/thermal_only_baseline_n64_end3_dt0.0005_snap601_cfl0.05'


def main():
    sources = [Path(__file__), ARCHIVE/f'{OLD}_states.npz', ARCHIVE/f'{OLD}_summary.json']
    metadata, old, times, states, _ = load_case(OLD)
    reference = []
    for t, state in zip(times, states):
        f = old.fields(float(t), state)
        stress = old.law.scale*f['radial_int']/(f['volume']*f['metric'].radius**2)
        reference.append(dict(s=t, maximum_abs_velocity=max(abs(f['velocity'])), receiver_heat=f['heat'][32],
                               maximum_abs_radial_stress=max(abs(stress))))
    reference = pd.DataFrame(reference)
    def read(case, cells, suffix='history.csv'):
        path = DATA/'finite_stiffness'/f'{case}_n{cells}_end1.285_dt0.0005_cfl0.05_{suffix}'
        sources.append(path)
        return json.loads(path.read_text()) if suffix.endswith('json') else pd.read_csv(path)
    balanced, cheap = read('equilibrated', 128), read('energy_matched', 64)
    comparison = read('equilibrated', 64)
    rich_summary, cheap_summary = read('equilibrated', 128, 'summary.json'), read('energy_matched', 64, 'summary.json')
    blue, orange, gray = '#0072B2', '#D55E00', '.35'
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(2, 2, figsize=(11.6, 8.1), constrained_layout=True)
    curves = [(reference, gray, 'Previous assembly, 64 cells'), (cheap, orange, 'New assembly, prior energy budget'),
              (balanced, blue, 'New assembly, balanced preload')]
    ax = axes[0, 0]
    for frame, color, label in curves:
        ax.plot(frame.s, frame.maximum_abs_velocity, color=color, label=label)
    ax.plot(comparison.s, comparison.maximum_abs_velocity, color=blue, ls=':', alpha=.6, label='Balanced preload, 64-cell control')
    ax.axhline(1., color='.65', lw=.8, ls='--')
    ax.set(xlabel='Service coordinate s', ylabel='Peak material speed / c', ylim=(0, 1.05),
           title='A. Prestress changes the freely evolved motion')
    ax.legend(fontsize=8)
    ax = axes[0, 1]
    for frame, color, label in curves:
        ax.plot(frame.s, frame.receiver_heat, color=color)
    ax.set(xlabel='Service coordinate s', ylabel='Heat per material reference q',
           title='B. The former cold element retains heat')
    ax.axvline(.745, color='.7', ls=':', label='Release begins')
    ax.legend(fontsize=8)
    ax = axes[1, 0]
    for frame, color, label in curves:
        ax.semilogy(frame.s, frame.maximum_abs_radial_stress, color=color)
    ax.set(xlabel='Service coordinate s', ylabel='Peak absolute normal-frame radial stress',
           title='C. Slower motion requires concentrated support stress')
    ax = axes[1, 1]
    labels = ['Previous assembly', 'Prior-budget replacement', 'Balanced-preload replacement']
    values = [metadata['initial_slice_energy'], cheap_summary['initial_slice_energy'], rich_summary['initial_slice_energy']]
    ax.barh(labels, values, color=[gray, orange, blue], height=.6)
    for i, value in enumerate(values):
        ax.text(value+15, i, f'{value:.1f}', va='center', fontsize=9)
    ax.invert_yaxis()
    ax.set(xlim=(0, 1170), xlabel='Initial ADM-slice material energy',
           title='D. Initial heat is shared; mechanical energy differs')
    fig.suptitle('A different endpoint reservoir assembly\n'
                 'Full active metric; evolved interior motion; finite-stiffness backbone with bonded thermal buffers', fontsize=13)
    FIGURES.mkdir(exist_ok=True)
    for extension in ('png', 'pdf'):
        fig.savefig(FIGURES/f'prestressed_buffer_velocity.{extension}', dpi=170)
    plt.close(fig)
    (DATA/'figure_inputs.json').write_text(json.dumps(
        {'source_sha256':{str(path.relative_to(ROOT)):sha256_file(path) for path in sources}}, indent=2)+'\n')


if __name__ == '__main__':
    main()
