#!/usr/bin/env python3
"""Numerical tables and a figure; narrative findings are maintained manually."""
from pathlib import Path
import argparse
import json

import numpy as np
import pandas as pd

from adm_harness.source_ledger import sha256_file


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    root = args.output
    audit = json.loads((root/'audit.json').read_text())
    for name, expected in audit['output_hashes'].items():
        if sha256_file(root/name) != expected:
            raise RuntimeError('audit evidence changed: '+name)
    all_rows = pd.read_csv(root/'plateau/response.csv.gz')
    frame = all_rows[all_rows.main_witness].copy()
    summaries = []
    for portal, group in frame.groupby('portal'):
        row = {'portal': portal, 'witnesses': len(group)}
        for channel in ['energy', 'radial_pressure', 'angular_pressure', 'radial_enthalpy', 'angular_enthalpy']:
            required = group['required_remainder_'+channel]
            supplied = group['geometric_'+channel]
            selected = required < 0
            row[channel+'_negative_required'] = int(selected.sum())
            row[channel+'_negative_supplied_where_required'] = int((supplied[selected] < 0).sum())
            if channel.endswith('enthalpy'):
                ratio = supplied[selected]/required[selected]
                row[channel+'_fraction_min'] = ratio.min()
                row[channel+'_fraction_median'] = ratio.median()
                row[channel+'_fraction_max'] = ratio.max()
        summaries.append(row)
    pd.DataFrame(summaries).to_csv(root/'supply_summary.csv', index=False)
    selected = frame[frame.portal == 1.4].sort_values('radius').iloc[[0, 16, 32, 48, 64]]
    selected.to_csv(root/'selected_witnesses.csv', index=False)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figure, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for axis, channel, title in zip(axes, ['radial_enthalpy', 'angular_enthalpy'],
                                   ['Radial null stress', 'Angular null stress']):
        for portal, group in frame.groupby('portal'):
            group = group.sort_values('radius')
            required = group['required_remainder_'+channel]
            ratio = (group['geometric_'+channel]/required).where(required < 0)
            axis.semilogy(group.radius, ratio, label=rf'$\kappa={portal:g}$')
        axis.axhline(1., color='black', linestyle='--', linewidth=1, label='Required contribution')
        axis.set(xlabel='Areal radius (rail units)', ylabel='Optical response / required remainder',
                 title=title, ylim=(1e-9, 3.))
        axis.grid(alpha=.2)
    axes[0].legend(fontsize=8)
    figure.savefig(root/'supplied_stress_fraction.png', dpi=170)
    plt.close(figure)
    numerical = {'summary_script_sha256': sha256_file(Path(__file__)),
        'audit_sha256': sha256_file(root/'audit.json'),
        'output_hashes': {name: sha256_file(root/name) for name in
            ['supply_summary.csv', 'selected_witnesses.csv', 'supplied_stress_fraction.png']}}
    (root/'summary_manifest.json').write_text(json.dumps(numerical, indent=2)+'\n')


if __name__ == '__main__':
    main()
