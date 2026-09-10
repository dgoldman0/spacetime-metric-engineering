#!/usr/bin/env python3
"""Test finite material relaxation in the active reservoir; numerical evidence."""
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
from adm_harness.relaxing_material_ensemble import StrainRelaxation, RelaxingMaterialEnsemble, evolve_relaxing_ensemble
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT/'supporting_reports/data/active_transfer_reservoir'
CASES = {'ensemble': (.75, True, 1.), 'thermal_only': (1., True, 1.),
         'frozen_internal': (.75, False, 1.), 'unforced': (.75, True, 0.)}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def run_case(task):
    name, cells, medium, duration, snapshots, max_step, cfl, deadline, output = task
    output = Path(output)
    share, enabled, forcing = CASES[name]
    law = ElasticLaw(stiffness=.1, scale=.4)
    electrical = ElectricalLaw(energy_ratio=4., conductivity=.1, profile='capacitor')
    relaxation = StrainRelaxation(stiffness=.1, proper_time=1., enabled=enabled)
    model = TabulatedActiveMedium(INPUT/'metric_fine.npz', INPUT/f'medium_{medium}.npz')
    patch = RelaxingMaterialEnsemble(model, law, electrical, relaxation=relaxation,
                                     cells=cells, thermal_share=share, forcing=forcing)
    result = evolve_relaxing_ensemble(patch, duration=duration, snapshots=snapshots, max_step=max_step,
                                      cfl=cfl, deadline_seconds=deadline)
    label = f'{name}_{medium}_n{cells}_end{duration:g}_dt{max_step:g}_snap{snapshots}_cfl{cfl:g}'
    frame = pd.DataFrame(result['history'])
    frame.to_csv(output/f'{label}_history.csv', index=False)
    np.savez_compressed(output/f'{label}_states.npz', t=result['times'], states=result['states'],
                         initial_x=patch.initial_x, reference=patch.reference)
    first, last = frame.iloc[0], frame.iloc[-1]
    summary = dict(case=label, material_law=law.__dict__, electrical_law=electrical.__dict__,
                   relaxation=relaxation.__dict__, thermal_share=share, forcing=forcing, cells=cells, medium=medium,
                   duration=duration, max_step=max_step, cfl=cfl, snapshots=snapshots,
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
    sources = [Path(__file__)]+[ROOT/'toolkit/adm_harness_cli/adm_harness'/name for name in (
        'relaxing_material_ensemble.py', 'material_ensemble.py', 'elastic_endpoint_reservoir.py',
        'electrothermal_endpoint.py', 'active_transfer_reservoir.py')]
    write_json(output/f'{label}_manifest.json', {
        'completed_utc': datetime.now(timezone.utc).isoformat(), 'case': name,
        'scope': 'variational material reservoir with passive local internal-strain relaxation and counted heat; full active metric and pinned endpoint exchange',
        'software_sha256': {str(p.relative_to(ROOT)): sha256_file(p) for p in sources},
        'input_sha256': {name: sha256_file(INPUT/name) for name in ('metric_fine.npz', f'medium_{medium}.npz')},
    })
    print(f'{label}: {result["status"]} at s={last.s:.9g}; q_min={last.minimum_heat:.6g}; '
          f'energy residual={summary["maximum_canonical_balance_error"]:.6g}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/material_ensemble/relaxing')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--cells', type=int, default=32)
    parser.add_argument('--medium', choices=['baseline', 'dense'], default='baseline')
    parser.add_argument('--duration', type=float, default=.5)
    parser.add_argument('--snapshots', type=int, default=101)
    parser.add_argument('--max-step', type=float, default=.0005)
    parser.add_argument('--cfl', type=float, default=.05)
    parser.add_argument('--deadline', type=float, default=360.)
    parser.add_argument('--cases', nargs='+', choices=list(CASES), default=list(CASES))
    args = parser.parse_args()
    if not 1 <= args.workers <= 6 or args.cells < 8 or not 0 < args.duration <= 3 or not 0 < args.cfl <= .2:
        parser.error('one to six workers, at least eight cells, 0<duration<=3, 0<cfl<=.2 required')
    args.output.mkdir(parents=True, exist_ok=True)
    tasks = [(name, args.cells, args.medium, args.duration, args.snapshots, args.max_step,
              args.cfl, args.deadline, str(args.output)) for name in args.cases]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        for future in as_completed([pool.submit(run_case, task) for task in tasks]):
            future.result()


if __name__ == '__main__':
    main()
