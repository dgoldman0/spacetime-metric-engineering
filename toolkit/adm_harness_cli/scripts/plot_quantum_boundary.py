#!/usr/bin/env python3
"""Render the retained quantum-wall findings without repeating the evolution."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/quantum_boundary')
    args = parser.parse_args()
    output = args.output
    summaries = pd.read_csv(output/'summaries.csv', float_precision='round_trip')
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    for scenario in ['released', 'released_light', 'moving_held']:
        case = summaries[summaries.scenario.eq(scenario) & summaries.harmonics.eq(32)].iloc[0]['case']
        history = pd.read_csv(output/f'{case}_history.csv', float_precision='round_trip')
        label = scenario.replace('_', ' ')
        axes[0, 0].plot(history.time, history.separation, label=label)
        axes[0, 1].plot(history.time, history.excitation_above_instantaneous_ground, label=label)
        if scenario == 'moving_held':
            axes[1, 0].plot(history.time, history.quantum_force, label='evolving field')
            axes[1, 0].plot(history.time, history.instantaneous_ground_force, linestyle='--', label='instantaneous ground')
            profiles = pd.read_csv(output/f'{case}_profiles.csv.gz', float_precision='round_trip')
            for instant in [profiles.time.min(), profiles.time.max()]:
                profile = profiles[profiles.time.eq(instant) & profiles.z.abs().lt(.3)]
                axes[1, 1].plot(profile.z, profile.radial_enthalpy, label=f't = {instant:.2f}')
    axes[0, 0].axhline(1., color='black', linewidth=.5)
    axes[0, 0].set(title='Wall separation', xlabel='time / initial gap', ylabel='gap / initial gap', ylim=(.935, 1.065))
    axes[0, 1].set(title='Quantum excitation', xlabel='time / initial gap', ylabel='energy above instantaneous ground / area')
    axes[1, 0].set(title='Field force on moving held walls', xlabel='time / initial gap', ylabel='force / area')
    axes[1, 1].axhline(0., color='black', linewidth=.5)
    axes[1, 1].set(title='Radial enthalpy inside the gap', xlabel='normal position / initial gap', ylabel='free-subtracted energy + pressure')
    for ax in axes.ravel():
        ax.grid(alpha=.2)
        ax.legend(fontsize=8)
    figure = output/'quantum_boundary_response.png'
    fig.savefig(figure, dpi=160)
    plt.close(fig)
    provenance = {'renderer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'figure_sha256': hashlib.sha256(figure.read_bytes()).hexdigest(),
        'source': 'Existing m32 k16 h0.005 histories and scalar profiles; hbar = c = initial gap = 1.'}
    (output/'figure_provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')


if __name__ == '__main__':
    main()
