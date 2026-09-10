#!/usr/bin/env python3
"""Verify the dimensionless load envelope and plot the measured requirements."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT/'supporting_reports/data/reservoir_feasibility'
DERIVED = DATA/'derived'
FIGURES = ROOT/'supporting_reports/figures'


def main():
    DERIVED.mkdir(exist_ok=True)
    paths = sorted(DATA.glob('*_points.csv'))
    verified, errors = 0, []
    for path in paths:
        points = pd.read_csv(path)
        if 'sigma' not in points:
            continue
        v = abs(points.velocity.to_numpy())
        envelope = points.buffer.to_numpy()*(1+points.sigma.to_numpy())*(1+v)/(1-v)
        actual = (points.reservoir_rho+points.reservoir_p_l+2*abs(points.reservoir_j_l)).to_numpy()
        error = np.max(abs(envelope-actual)/np.maximum(abs(actual), 1e-30))
        if error > 1e-10:
            raise ValueError('radial-null envelope identity failed')
        errors.append(float(error))
        verified += len(points)
    phases = pd.read_csv(DATA/'phase_summary.csv')
    rows = []
    for _, row in phases[phases.case == 'equilibrated_n128'].iterrows():
        for ceiling in (100., 4.414e9):
            length = row.magnetic_tesla_metres/ceiling
            rows.append(dict(s=float(row.s), assumed_field_ceiling_tesla=ceiling,
                             minimum_model_length_conversion_metres=float(length),
                             slice_energy_at_that_conversion_joules=float(row.slice_energy_joules_per_metre*length)))
    pd.DataFrame(rows).to_csv(DERIVED/'conditional_scale_examples.csv', index=False)
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.1), sharey=True)
    for ax, phase, title in zip(axes, (0., 1.285), ('Prepared startup', 'Carrying-flow fade complete')):
        for cells, style in ((64, '--'), (128, '-')):
            points = pd.read_csv(DATA/f'equilibrated_n{cells}_points.csv')
            p = points[np.isclose(points.s, phase)]
            required = np.maximum(p.required_negative_null_plus, p.required_negative_null_minus)
            ax.plot(p.fraction, required, style, color='#b64a35', label=f'With reservoir, {cells} cells')
            if cells == 128:
                before = np.maximum(p.required_before_plus, p.required_before_minus)
                ax.plot(p.fraction, before, color='#375f87', label='Before reservoir')
        ax.axvspan(.15, .85, color='#87989e', alpha=.10)
        ax.set_yscale('log')
        ax.set_ylim(1e-7, 150)
        ax.set_xlabel('Conserved material fraction')
        ax.set_title(title)
        ax.grid(alpha=.2, which='major')
    axes[0].set_ylabel('Required negative radial-null contribution\n(model stress units)')
    axes[1].legend(fontsize=8, loc='lower left')
    fig.tight_layout()
    FIGURES.mkdir(exist_ok=True)
    for suffix in ('png', 'pdf'):
        fig.savefig(FIGURES/f'reservoir_feasibility_source.{suffix}', dpi=180)
    plt.close(fig)
    inputs = paths+[DATA/'phase_summary.csv', DATA/'manifest.json', Path(__file__)]
    outputs = [DERIVED/'conditional_scale_examples.csv']+[FIGURES/f'reservoir_feasibility_source.{s}' for s in ('png', 'pdf')]
    result = dict(verified_field_samples=verified, maximum_relative_null_envelope_error=max(errors),
                  scale_example_scope='conditional field ceilings, not acceptance limits; 4.414e9 T marks electron quantum-critical field scale; full construction feasibility remains unestablished',
                  inputs_sha256={str(p.relative_to(ROOT)):sha256_file(p) for p in inputs},
                  outputs_sha256={str(p.relative_to(ROOT)):sha256_file(p) for p in outputs})
    (DERIVED/'derived_envelope.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
