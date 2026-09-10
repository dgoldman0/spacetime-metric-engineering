#!/usr/bin/env python3
"""Bounded confined-field/material comparison; writes numerical evidence only."""
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
from adm_harness.electrothermal_endpoint import ElectricalLaw, ElectrothermalPatch, evolve_electrothermal
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT/'supporting_reports/data/active_transfer_reservoir'
CASES = {
    'elastic_control': (0., 0., 'field', 'thermal'),
    'field1_slow': (1., .03, 'field', 'thermal'),
    'field1_fast': (1., .1, 'field', 'thermal'),
    'field4_slow': (4., .03, 'field', 'thermal'),
    'field4_fast': (4., .1, 'field', 'thermal'),
    'field4_ideal': (4., 0., 'field', 'thermal'),
    'material4_control': (4., 0., 'material', 'thermal'),
    'capacitor4_fast': (4., .1, 'field', 'capacitor'),
    'capacitor4_ideal': (4., 0., 'field', 'capacitor'),
    'capacitor4_material': (4., 0., 'material', 'capacitor'),
}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def run_case(task):
    name, cells, medium, forcing, duration, snapshots, deadline, output = task
    output = Path(output)
    ratio, sigma, allocation, profile = CASES[name]
    model = TabulatedActiveMedium(INPUT/'metric_fine.npz', INPUT/f'medium_{medium}.npz')
    law, electrical = ElasticLaw(stiffness=.1, scale=.4), ElectricalLaw(energy_ratio=ratio, conductivity=sigma, profile=profile)
    patch = ElectrothermalPatch(model, law, electrical, allocation=allocation, cells=cells, forcing=forcing)
    result = evolve_electrothermal(patch, duration=duration, snapshots=snapshots, deadline_seconds=deadline)
    label = f'{name}_{medium}_n{cells}_force{forcing:g}_end{duration:g}_snap{snapshots}'
    frame = pd.DataFrame(result['history'])
    frame.to_csv(output/f'{label}_history.csv', index=False)
    np.savez_compressed(output/f'{label}_states.npz', t=result['times'], x=patch.x, faces=patch.faces,
                        states=result['states'], charges=result['charges'])
    summary = dict(case=label, material_law=law.__dict__, electrical_law=electrical.__dict__,
                   allocation=allocation, cells=cells, medium=medium, forcing=forcing,
                   duration=duration, snapshots=snapshots, status=result['status'], failure=result['failure'],
                   elapsed_seconds=result['elapsed_seconds'],
                   initial_total_energy=float(frame.total_slice_energy.iloc[0]),
                   initial_field_energy=float(frame.field_slice_energy.iloc[0]),
                   initial_thermal_inventory=float(frame.thermal_inventory.iloc[0]),
                   maximum_thermal_balance_error=float(abs(frame.thermal_balance_residual).max()),
                   maximum_velocity_over_run=float(frame.maximum_abs_velocity.max()),
                   maximum_sound2_over_run=float(frame.maximum_sound2.max()),
                   **frame.iloc[-1].to_dict())
    write_json(output/f'{label}_summary.json', summary)
    print(f'{label}: {result["status"]} at s={result["final_time"]:.9g}; '
          f'min heat={summary["minimum_thermal"]:.6g}; thermal residual={summary["thermal_balance_residual"]:.6g}', flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/electrothermal_endpoint')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--cells', type=int, default=128)
    parser.add_argument('--medium', choices=['baseline', 'dense'], default='baseline')
    parser.add_argument('--forcing', type=float, default=1.)
    parser.add_argument('--duration', type=float, default=.5)
    parser.add_argument('--snapshots', type=int, default=101)
    parser.add_argument('--deadline', type=float, default=240.)
    parser.add_argument('--cases', nargs='+', choices=list(CASES), default=list(CASES)[:7])
    args = parser.parse_args()
    if not 1 <= args.workers <= 6 or args.cells < 16 or not 0 < args.duration <= 3 or args.snapshots < 2:
        parser.error('one to six workers, at least 16 cells, 0<duration<=3, and at least two snapshots required')
    args.output.mkdir(parents=True, exist_ok=True)
    tasks = [(name, args.cells, args.medium, args.forcing, args.duration, args.snapshots,
              args.deadline, str(args.output)) for name in args.cases]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        rows = [f.result() for f in as_completed([pool.submit(run_case, task) for task in tasks])]
    suffix = f'{args.medium}_n{args.cells}_force{args.forcing:g}_end{args.duration:g}_snap{args.snapshots}'
    pd.DataFrame([{k: v for k, v in row.items() if k not in ('material_law', 'electrical_law')}
                  for row in sorted(rows, key=lambda row: row['case'])]).to_csv(args.output/f'summary_{suffix}.csv', index=False)
    paths = [Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/electrothermal_endpoint.py',
             ROOT/'toolkit/adm_harness_cli/adm_harness/elastic_endpoint_reservoir.py',
             ROOT/'toolkit/adm_harness_cli/adm_harness/active_transfer_reservoir.py']
    write_json(args.output/f'manifest_{suffix}.json', {
        'completed_utc': datetime.now(timezone.utc).isoformat(), 'cases': args.cases,
        'cells': args.cells, 'workers': args.workers, 'medium': args.medium, 'forcing': args.forcing,
        'duration': args.duration, 'snapshots': args.snapshots,
        'scope': 'forced combined Maxwell/elastic response on full active metric; pinned endpoint history; late non-live material patch; counted support-end ports',
        'software_sha256': {str(p.relative_to(ROOT)): sha256_file(p) for p in paths},
        'input_sha256': {name: sha256_file(INPUT/name) for name in ('metric_fine.npz', f'medium_{args.medium}.npz')},
    })


if __name__ == '__main__':
    main()
