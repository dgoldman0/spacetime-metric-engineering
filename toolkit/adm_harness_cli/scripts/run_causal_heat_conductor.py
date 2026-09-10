#!/usr/bin/env python3
"""Run a bounded entropy-current conductor on archived material motion."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import argparse
import json
import multiprocessing
from pathlib import Path

import numpy as np
import pandas as pd

from adm_harness.causal_heat_conductor import (
    HeatConductorLaw, FrozenHeatBackground, HeatConductor, evolve_heat_conductor, thermal_primitive,
)
from adm_harness.source_ledger import sha256_file
from audit_material_ensemble import ROOT, OUTPUT as ARCHIVE, load_case

OUTPUT = ROOT/'supporting_reports/data/causal_reservoir_transport/conductor'
CASES = {'zero': (0., 1.), 'slow': (.3, 1.), 'slow_long': (.3, 10.),
         'fast': (1/np.sqrt(3), 1.), 'fast_long': (1/np.sqrt(3), 10.)}


def run_case(task):
    name, archive, cells, tabulation_step, max_step, deadline, output = task
    metadata, patch, times, states, _ = load_case(archive)
    background = FrozenHeatBackground(patch, times, states, cells=cells, tabulation_step=tabulation_step)
    law = HeatConductorLaw(*CASES[name])
    conductor = HeatConductor(background, law)
    result = evolve_heat_conductor(conductor, max_step=max_step, deadline_seconds=deadline)
    label = f'{name}_{archive.split("/")[-1].split("_baseline")[0]}_history{metadata["cells"]}_heat{cells}_tab{tabulation_step:g}_dt{max_step:g}'
    frame = pd.DataFrame(result['history'])
    frame.to_csv(output/f'{label}_history.csv', index=False)
    q, r = [], []
    for t, state in zip(result['times'], result['states']):
        bg, _ = background.sample(float(t))
        qq, rr = thermal_primitive(state, bg['v'], law)
        q.append(qq); r.append(rr)
    np.savez_compressed(output/f'{label}_states.npz', t=result['times'], state=result['states'],
                         q=np.array(q), r=np.array(r), material_reference=background.a)
    summary = dict(case=label, archive=archive, heat_law=law.__dict__, cells=cells,
                   band=background.band, background_tabulation_step=tabulation_step, max_step=max_step,
                   status=result['status'], failure=result['failure'], steps=result['steps'],
                   elapsed_seconds=result['elapsed_seconds'],
                   target_time=background.end_time,
                   initial_thermal_inventory=float(frame.thermal_inventory.iloc[0]),
                   maximum_tilted_heat_balance_error=float(abs(frame.tilted_heat_balance).max()),
                   maximum_canonical_balance_error=float(abs(frame.canonical_balance_residual).max()),
                   minimum_entropy_excess=float(frame.entropy_excess.min()),
                   maximum_entropy_excess=float(frame.entropy_excess.max()),
                   maximum_added_normal_density_over_run=float(frame.maximum_relative_added_normal_density.max()),
                   minimum_packet_gap=float(np.min(abs(background.tables['x']-background.times[:, None]))-.35),
                   **frame.iloc[-1].to_dict())
    sources = (Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/causal_heat_conductor.py',
                ROOT/'toolkit/adm_harness_cli/scripts/audit_material_ensemble.py',
                ARCHIVE/f'{archive}_states.npz', ARCHIVE/f'{archive}_summary.json',
                ARCHIVE.parent/'active_transfer_reservoir/metric_fine.npz')
    manifest = dict(completed_utc=datetime.now(timezone.utc).isoformat(),
                     scope='entropy-consistent causal-conductor replay on prescribed archived material motion and heat source; additional stress and trajectory-maintenance force work are counted; joint mechanical feedback remains open',
                     source_sha256={str(p.relative_to(ROOT)): sha256_file(p) for p in sources})
    for suffix, data in (('summary', summary), ('manifest', manifest)):
        (output/f'{label}_{suffix}.json').write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')
    print(f'{label}: {result["status"]} at s={summary["s"]:.9g}; '
          f'q_min={summary["minimum_heat"]:.6g}; |r|={summary["maximum_relative_heat_flux"]:.5g}; '
          f'canonical error={summary["maximum_canonical_balance_error"]:.5g}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', default='relaxing/thermal_only_baseline_n64_end3_dt0.0005_snap601_cfl0.05')
    parser.add_argument('--cells', type=int, default=129)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--tabulation-step', type=float, default=.0005)
    parser.add_argument('--max-step', type=float, default=.0005)
    parser.add_argument('--deadline', type=float, default=180.)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--cases', nargs='+', choices=list(CASES), default=list(CASES))
    args = parser.parse_args()
    if not 1 <= args.workers <= 6 or args.cells < 9 or args.cells % 2 != 1:
        parser.error('one to six workers and an odd number of heat cells >=9 required')
    args.output.mkdir(parents=True, exist_ok=True)
    tasks = [(name, args.archive, args.cells, args.tabulation_step, args.max_step, args.deadline, args.output) for name in args.cases]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        list(pool.map(run_case, tasks))


if __name__ == '__main__':
    main()
