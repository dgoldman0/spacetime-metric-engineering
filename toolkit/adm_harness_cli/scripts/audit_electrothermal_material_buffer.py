#!/usr/bin/env python3
"""Audit heat budgets across resolved material labels in zero-field controls."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import multiprocessing
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid

from adm_harness.active_transfer_reservoir import TabulatedActiveMedium, divergence_projections
from adm_harness.elastic_endpoint_reservoir import ElasticLaw
from adm_harness.electrothermal_endpoint import ElectricalLaw, ElectrothermalPatch
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT/'supporting_reports/data/electrothermal_endpoint'
INPUT = OUTPUT.parent/'active_transfer_reservoir'


def audit(label):
    summary_path, state_path = OUTPUT/f'{label}_summary.json', OUTPUT/f'{label}_states.npz'
    info = json.loads(summary_path.read_text())
    model = TabulatedActiveMedium(INPUT/'metric_fine.npz', INPUT/f'medium_{info["medium"]}.npz')
    patch = ElectrothermalPatch(model, ElasticLaw(**info['material_law']),
                               ElectricalLaw(**info['electrical_law']), cells=info['cells'], forcing=info['forcing'])
    with np.load(state_path) as data:
        times, states, charges = data['t'], data['states'], data['charges']
    if np.any(charges != 0):
        raise ValueError('this thermal-buffer audit requires zero field throughout')
    labels0 = patch.dx*(np.cumsum(states[0, 0])-.5*states[0, 0])
    covered = np.ones(labels0.size, dtype=bool)
    rates, measured = [], []
    for t, state, charge in zip(times, states, charges):
        _, _, f = patch.material_fields(t, state, charge)
        labels = patch.dx*(np.cumsum(state[0])-.5*state[0])
        covered &= (labels0 >= labels[0]) & (labels0 <= labels[-1])
        positions = np.interp(labels0, labels, patch.x)
        n, v, q = [np.interp(labels0, labels, f[key]) for key in ('n', 'velocity', 'thermal')]
        g = model.metric(t, positions)
        power, force = divergence_projections(g, *model.medium(t, positions))
        rates.append(patch.forcing*g.alpha*g.radius**2*(-power+v*force)/(patch.law.scale*n))
        measured.append(q)
    measured = np.array(measured)[:, covered]
    budget = measured[0]+cumulative_trapezoid(np.array(rates)[:, covered], times, axis=0, initial=0.)
    discrepancy = measured-budget
    frame = pd.DataFrame(dict(s=times, minimum_integrated_heat=budget.min(axis=1),
                              minimum_evolved_heat=measured.min(axis=1),
                              maximum_absolute_heat_discrepancy=abs(discrepancy).max(axis=1),
                              mean_absolute_heat_discrepancy=abs(discrepancy).mean(axis=1)))
    frame.to_csv(OUTPUT/f'{label}_material_label_cloud.csv', index=False)
    result = dict(case=label, sampled_labels=int(labels0.size), fully_covered_labels=int(covered.sum()),
                  minimum_integrated_heat=float(budget.min()), minimum_evolved_heat=float(measured.min()),
                  maximum_absolute_heat_discrepancy=float(abs(discrepancy).max()),
                  scope='integrated smooth-material heat equation along the numerical material histories; labels requiring extrapolation outside cell-center coverage are excluded; no independent evolution or shock-heating term',
                  source_sha256={str(p.relative_to(ROOT)): sha256_file(p) for p in
                                 (Path(__file__), state_path, summary_path, INPUT/'metric_fine.npz', INPUT/f'medium_{info["medium"]}.npz')})
    (OUTPUT/f'{label}_material_label_cloud.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(f'{label}: {covered.sum()}/{labels0.size} labels covered; min integrated heat={budget.min():.6g}; '
          f'max local discrepancy={abs(discrepancy).max():.6g}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cases', nargs='+')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        for future in as_completed([pool.submit(audit, name) for name in args.cases]):
            future.result()


if __name__ == '__main__':
    main()
