#!/usr/bin/env python3
"""Plot measured conductor response, refinement, and counted work."""
from pathlib import Path
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT/'supporting_reports/data/causal_reservoir_transport/conductor'
FIGURES = ROOT/'supporting_reports/figures'


def main():
    FIGURES.mkdir(exist_ok=True)
    sources = [Path(__file__)]
    def read(directory, prefix, suffix='history.csv'):
        paths = sorted((DATA/directory).glob(prefix+'*_'+suffix))
        if len(paths) != 1:
            raise ValueError(f'expected one input for {directory}/{prefix}: {paths}')
        sources.append(paths[0])
        return json.loads(paths[0].read_text()) if suffix.endswith('json') else pd.read_csv(paths[0])
    best = read('refined', 'slow_long_thermal_only_history64_heat513')
    local = read('refined', 'slow_long_thermal_only_history64_heat513', 'local_audit.csv')
    summary = read('refined', 'slow_long_thermal_only_history64_heat513', 'summary.json')
    slow = read('refined', 'slow_thermal_only_history64_heat257')
    fast_long = read('refined', 'fast_long_thermal_only_history64_heat257')
    fast = read('resolved_inversion', 'fast_thermal_only_history64_heat129')
    colors = dict(best='#0072B2', slow='#D55E00', fast='#CC79A7', fast_long='#009E73')
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(2, 2, figsize=(11.8, 8.2), constrained_layout=True)
    ax = axes[0, 0]
    ax.plot(local.s, local.receiver_archived_heat, color='.35', ls='--', label='Archived heat')
    ax.plot(best.s, best.receiver_heat, color=colors['best'], label=r'$c_h=0.3,\ \tau=10$')
    ax.plot(fast_long.s, fast_long.receiver_heat, color=colors['fast_long'], label=r'$c_h=1/\sqrt{3},\ \tau=10$')
    ax.scatter([best.s.iloc[-1]], [best.receiver_heat.iloc[-1]], color=colors['best'], s=20, zorder=3)
    ax.set(xlim=(.70, .823), ylim=(-.03, 2.65), xlabel='Service coordinate s', ylabel='Heat per material reference q',
           title='A. The cold element continues to drain')
    ax.axvline(.745, color='.75', ls=':', label='Release begins')
    ax.legend(fontsize=8)
    ax = axes[0, 1]
    for cells, tab, style, color in ((129, '.000125', ':', '.5'), (257, '.00025', '--', '#56B4E9'), (513, '.000125', '-', colors['best'])):
        prefix = f'slow_long_thermal_only_history64_heat{cells}_tab0{tab}'
        frame = read('refined', prefix)
        if len(frame) != len(local):
            raise ValueError('the successful comparisons must share their output times')
        ax.plot(frame.s, frame.receiver_heat-local.receiver_archived_heat, ls=style, color=color, label=f'{cells} heat cells')
    ax.axhline(0., color='.65', lw=.8)
    ax.set(xlabel='Service coordinate s', ylabel='Conductor heat minus archived heat',
           title='B. Refinement retains a small final heat gain')
    ax.legend(fontsize=8)
    ax = axes[1, 0]
    for frame, name, label in ((slow, 'slow', r'$0.3,\ 1$'), (best, 'best', r'$0.3,\ 10$'),
                                (fast, 'fast', r'$1/\sqrt{3},\ 1$'), (fast_long, 'fast_long', r'$1/\sqrt{3},\ 10$')):
        ax.plot(frame.s, frame.maximum_material_frame_signal_speed, color=colors[name], label=label)
        ax.scatter([frame.s.iloc[-1]], [frame.maximum_material_frame_signal_speed.iloc[-1]], color=colors[name], s=18)
    ax.axhline(1., color='.35', ls='--', lw=1)
    ax.set(xlim=(.73, .823), ylim=(.25, 1.05), xlabel='Service coordinate s', ylabel='Largest material-frame characteristic speed',
           title='C. Three settings reach the causal boundary')
    ax.legend(title=r'$c_h,\ \tau$', fontsize=8, title_fontsize=8)
    ax = axes[1, 1]
    values = [summary[key] for key in ('holding_positive_work_integral', 'holding_negative_work_integral',
                                       'geometric_work_integral', 'canonical_energy_change')]
    labels = ['Mechanical work supplied', 'Mechanical work removed', 'Work from active metric', 'Additional canonical energy']
    ax.barh(labels, values, color=['#D55E00', '#E69F00', '#009E73', colors['best']], height=.6)
    ax.axvline(0., color='.55', lw=.8)
    for i, value in enumerate(values):
        ax.text(value+(.25 if value >= 0 else -.25), i, f'{value:.3f}', va='center', ha='left' if value >= 0 else 'right', fontsize=9)
    ax.set(xlim=(-8.5, 16.5), xlabel='Integrated canonical work / energy',
           title='D. Cost of retaining the archived motion')
    ax.invert_yaxis()
    fig.suptitle('Causal heat transport in the moving endpoint reservoir\n'
                 'Prescribed thermal-only motion; active metric; insulated reference band 0.375–0.625', fontsize=13)
    for extension in ('png', 'pdf'):
        fig.savefig(FIGURES/f'active_reservoir_causal_transport.{extension}', dpi=170)
    plt.close(fig)
    (DATA/'figure_inputs.json').write_text(json.dumps(
        {'source_sha256': {str(path.relative_to(ROOT)): sha256_file(path) for path in dict.fromkeys(sources)}},
        indent=2)+'\n')


if __name__ == '__main__':
    main()
