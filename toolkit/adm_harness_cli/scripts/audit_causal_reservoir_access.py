#!/usr/bin/env python3
"""Audit emission deadlines and causal access on saved active material motion."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import argparse
import json
import multiprocessing
from pathlib import Path

import numpy as np
import pandas as pd

from adm_harness.causal_reservoir_transport import MaterialHistory, trace_past_signal
from adm_harness.source_ledger import sha256_file
from audit_material_ensemble import ROOT, OUTPUT as ARCHIVE, load_case

OUTPUT = ROOT/'supporting_reports/data/causal_reservoir_transport'


def run_case(task):
    label, max_step = task
    metadata, patch, times, states, fraction = load_case(label)
    history = MaterialHistory(patch, times, states)
    cold = int(np.argmin(history.arrays['heat'][-1]))
    event_time, event_x = float(times[-1]), float(history.arrays['x'][-1, cold])
    rows, deadlines = [], []
    for speed in (.1, .3, 1/np.sqrt(3), .9, .99, 1.):
        rays = {direction: trace_past_signal(history, event_time, event_x, speed, direction,
                                             max_step=max_step) for direction in (-1, 1)}
        for t in (0., .1, .25, .5, .65, .7, .745, event_time):
            if t > event_time:
                continue
            left, right = rays[1]['position'](t), rays[-1]['position'](t)
            rows.append(dict(relative_speed=speed, s=t, left_l=left, right_l=right,
                              left_fraction=float(history.material_fraction(t, left)),
                              right_fraction=float(history.material_fraction(t, right)),
                              minimum_packet_gap=min(abs(left-t), abs(right-t))-.35))
        for donor in (.375, .4375, .46875, .53125, .5625, .59375, .625, .75):
            direction = 1 if donor < fraction[cold] else -1
            ray = rays[direction]
            emission = ray['latest_emission'](donor)
            deadlines.append(dict(relative_speed=speed, donor_fraction=donor, direction=direction,
                                   latest_emission=emission,
                                   null_comoving_energy_gain=None if emission is None else ray['null_comoving_gain'](emission)))
    name = label.replace('/', '_')+f'_step{max_step:g}'
    frame = pd.DataFrame(rows)
    frame.to_csv(OUTPUT/f'{name}_cones.csv', index=False)
    pd.DataFrame(deadlines).to_csv(OUTPUT/f'{name}_deadlines.csv', index=False)
    result = dict(case=label, event_time=event_time, event_x=event_x,
                   event_fraction=float(fraction[cold]), max_step=max_step,
                   scope='finite-speed causal-access screen on archived material motion, with full active metric; subluminal speeds specify signal cones, not an independently supplied heat-current tensor',
                   null_energy_scope='null packet frequency transport includes active metric and emitter/receiver boosts along the boundary ray; emission/absorption recoil and material feedback remain construction duties',
                   deadlines=deadlines, cones=rows,
                   completed_utc=datetime.now(timezone.utc).isoformat(),
                   source_sha256={str(p.relative_to(ROOT)): sha256_file(p) for p in (
                       Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/causal_reservoir_transport.py',
                       ARCHIVE/f'{label}_states.npz', ARCHIVE/f'{label}_summary.json',
                       ARCHIVE.parent/'active_transfer_reservoir/metric_fine.npz')})
    (OUTPUT/f'{name}.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(case=label, event_time=event_time,
                          right_donor_deadlines=[r for r in deadlines if r['donor_fraction'] == .53125]), indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--max-step', type=float, default=.002)
    parser.add_argument('--cases', nargs='+', default=[
        'relaxing/ensemble_baseline_n32_end3_dt0.0005_snap601_cfl0.05',
        'relaxing/ensemble_baseline_n64_end3_dt0.0005_snap601_cfl0.05',
        'relaxing/thermal_only_baseline_n64_end3_dt0.0005_snap601_cfl0.05'])
    args = parser.parse_args()
    if not 1 <= args.workers <= 6 or args.max_step <= 0:
        parser.error('one to six workers and positive integration step required')
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        list(pool.map(run_case, [(name, args.max_step) for name in args.cases]))


if __name__ == '__main__':
    main()
