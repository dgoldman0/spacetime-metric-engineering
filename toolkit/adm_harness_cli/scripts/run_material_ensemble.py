#!/usr/bin/env python3
"""Run the variational active reservoir; numerical evidence only."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import multiprocessing
from pathlib import Path

import numpy as np
import pandas as pd

from adm_harness.active_transfer_reservoir import TabulatedActiveMedium
from adm_harness.elastic_endpoint_reservoir import ElasticLaw
from adm_harness.electrothermal_endpoint import ElectricalLaw
from adm_harness.material_ensemble import MaterialEnsemble, evolve_material_ensemble
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT/'supporting_reports/data/active_transfer_reservoir'
CASES = {
    'ideal_control': (4., 0., 0., 0.),
    'resistive_control': (4., 0., .1, 0.),
    'elastic_control': (0., 1., 0., 1.),
    'thermal_only': (4., 1., 0., 1.),
    'ensemble': (4., .75, .1, 1.),
    'field_only': (4., 0., .1, 1.),
    'ensemble_unforced': (4., .75, .1, 0.),
}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def run_case(task):
    name, cells, medium, duration, snapshots, max_step, deadline, output = task
    output = Path(output)
    ratio, share, sigma, forcing = CASES[name]
    law = ElasticLaw(stiffness=.1, scale=.4)
    electrical = ElectricalLaw(energy_ratio=ratio, conductivity=sigma, profile='capacitor')
    model = TabulatedActiveMedium(INPUT/'metric_fine.npz', INPUT/f'medium_{medium}.npz')
    patch = MaterialEnsemble(model, law, electrical, cells=cells, thermal_share=share, forcing=forcing)
    result = evolve_material_ensemble(patch, duration=duration, snapshots=snapshots, max_step=max_step,
                                      deadline_seconds=deadline)
    label = f'{name}_{medium}_n{cells}_end{duration:g}_dt{max_step:g}_snap{snapshots}'
    frame = pd.DataFrame(result['history'])
    frame.to_csv(output/f'{label}_history.csv', index=False)
    np.savez_compressed(output/f'{label}_states.npz', t=result['times'], states=result['states'],
                         initial_x=patch.initial_x, reference=patch.reference)
    first, last = frame.iloc[0], frame.iloc[-1]
    summary = dict(case=label, material_law=law.__dict__, electrical_law=electrical.__dict__,
                   thermal_share=share, forcing=forcing, cells=cells, medium=medium,
                   duration=duration, max_step=max_step, snapshots=snapshots,
                   status=result['status'], failure=result['failure'], elapsed_seconds=result['elapsed_seconds'],
                   initial_slice_energy=float(first.slice_energy), initial_canonical_energy=float(first.canonical_energy),
                   initial_thermal_inventory=float(first.thermal_inventory), initial_field_energy=float(first.field_slice_energy),
                   maximum_canonical_balance_error=float(abs(frame.canonical_balance_residual).max()),
                   maximum_momentum_balance_error=float(abs(frame.momentum_balance_residual).max()),
                   maximum_thermal_balance_error=float(abs(frame.thermal_balance_residual).max()),
                   minimum_heat_over_run=float(frame.minimum_heat.min()),
                   maximum_velocity_over_run=float(frame.maximum_abs_velocity.max()),
                   maximum_sound2_over_run=float(frame.maximum_sound2.max()), **last.to_dict())
    write_json(output/f'{label}_summary.json', summary)
    paths = [Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/material_ensemble.py',
             ROOT/'toolkit/adm_harness_cli/adm_harness/elastic_endpoint_reservoir.py',
             ROOT/'toolkit/adm_harness_cli/adm_harness/electrothermal_endpoint.py',
             ROOT/'toolkit/adm_harness_cli/adm_harness/active_transfer_reservoir.py']
    write_json(output/f'{label}_manifest.json', {
        'completed_utc': datetime.now(timezone.utc).isoformat(), 'case': name,
        'scope': 'variational material-coordinate forced response; full active metric; fixed endpoint worldtubes with counted reactions; explicit local heat and Maxwell storage',
        'software_sha256': {str(p.relative_to(ROOT)): sha256_file(p) for p in paths},
        'input_sha256': {name: sha256_file(INPUT/name) for name in ('metric_fine.npz', f'medium_{medium}.npz')},
    })
    print(f'{label}: {result["status"]} at s={last.s:.9g}; q_min={last.minimum_heat:.6g}; '
          f'energy residual={summary["maximum_canonical_balance_error"]:.6g}', flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/material_ensemble')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--cells', type=int, default=64)
    parser.add_argument('--medium', choices=['baseline', 'dense'], default='baseline')
    parser.add_argument('--duration', type=float, default=.5)
    parser.add_argument('--snapshots', type=int, default=101)
    parser.add_argument('--max-step', type=float, default=.002)
    parser.add_argument('--deadline', type=float, default=240.)
    parser.add_argument('--cases', nargs='+', choices=list(CASES), default=list(CASES))
    args = parser.parse_args()
    if not 1 <= args.workers <= 6 or args.cells < 8 or not 0 < args.duration <= 3 or args.max_step <= 0:
        parser.error('one to six workers, at least eight cells, 0<duration<=3, and positive time step required')
    args.output.mkdir(parents=True, exist_ok=True)
    tasks = [(name, args.cells, args.medium, args.duration, args.snapshots, args.max_step,
              args.deadline, str(args.output)) for name in args.cases]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        for future in as_completed([pool.submit(run_case, task) for task in tasks]):
            future.result()


if __name__ == '__main__':
    main()
