#!/usr/bin/env python3
"""Run the bounded active-metric thermoelastic endpoint response.

Numerical evidence only; the narrative report is maintained manually.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import multiprocessing
from pathlib import Path

import numpy as np
import pandas as pd

from adm_harness.active_transfer_reservoir import TabulatedActiveMedium, divergence_projections
from adm_harness.elastic_endpoint_reservoir import ElasticLaw, ElasticPatch, evolve, recover
from adm_harness.source_ledger import sha256_file


ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT/'supporting_reports/data/active_transfer_reservoir'
CASES = {
    'soft_low': (.1, .1), 'stiff_low': (.5, .1),
    'soft_high': (.1, .4), 'stiff_high': (.5, .4),
}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def run_case(task):
    name, cells, medium, forcing, output = task
    output = Path(output)
    stiffness, scale = CASES[name]
    law = ElasticLaw(stiffness=stiffness, scale=scale)
    model = TabulatedActiveMedium(INPUT/'metric_fine.npz', INPUT/f'medium_{medium}.npz')
    patch = ElasticPatch(model, law, cells=cells, forcing=forcing)
    result = evolve(patch, deadline_seconds=240.)
    label = f'{name}_{medium}_n{cells}_force{forcing:g}'
    history = pd.DataFrame(result['history'])
    history.to_csv(output/f'{label}_history.csv', index=False)
    np.savez_compressed(output/f'{label}_states.npz', t=result['times'], x=patch.x,
                         faces=patch.faces, states=result['states'])
    last = history.iloc[-1].to_dict()
    summary = dict(case=label, law=law.__dict__, cells=cells, medium=medium, forcing=forcing,
                   status=result['status'], failure=result['failure'], final_time=result['final_time'],
                   elapsed_seconds=result['elapsed_seconds'],
                   initial_proper_energy=float(history.proper_energy.iloc[0]), **last)
    final = recover(result['states'][-1], model.metric(result['final_time'], patch.x).b, law)
    coldest = int(np.argmin(final['thermal']))
    summary['coldest_l'] = float(patch.x[coldest])
    summary['minimum_thermal_over_run'] = float(history.minimum_thermal.min())
    summary['maximum_velocity_over_run'] = float(history.maximum_abs_velocity.max())
    summary['maximum_sound2_over_run'] = float(history.maximum_sound2.max())
    write_json(output/f'{label}_summary.json', summary)
    print(f'{label}: {result["status"]} at s={result["final_time"]:.9g}; min heat={summary["minimum_thermal_over_run"]:.6g}', flush=True)
    return summary


def scope_audit(output):
    model = TabulatedActiveMedium(INPUT/'metric_fine.npz', INPUT/'medium_baseline.npz')
    rows = []
    for t in np.linspace(0., 3., 301):
        x = np.array([-2.1, -.5])
        g = model.metric(t, x)
        for i in range(2):
            rows.append(dict(s=t, l=x[i], endpoint_speed=g.b[i]*g.beta[i]/g.alpha[i],
                             timelike_margin=1-(g.b[i]*g.beta[i]/g.alpha[i])**2,
                             packet_edge_distance=abs(x[i]-t)-.35))
    pd.DataFrame(rows).to_csv(output/'end_worldtube_audit.csv', index=False)
    rows = []
    x = np.linspace(-2.1, 2.1, 337)
    subset = (x >= -2.1) & (x <= -.5)
    for t in np.linspace(-1.5, 3., 361):
        g = model.metric(t, x)
        power, force = divergence_projections(g, *model.medium(t, x))
        burden = g.alpha*g.volume*(abs(power)+abs(force))
        rows.append(dict(s=t, full_exchange_weight=np.trapezoid(burden, x),
                         patch_exchange_weight=np.trapezoid(burden[subset], x[subset]) if t >= 0 else 0.))
    frame = pd.DataFrame(rows)
    frame.to_csv(output/'exchange_scope_audit.csv', index=False)
    write_json(output/'scope_manifest.json', {
        'time_interval': [0., 3.], 'radial_interval': [-2.1, -.5],
        'scope': 'forced longitudinal thermoelastic reservoir response to pinned endpoint divergence; finite end traction ports; full active metric; full-cycle preparation and anchor tensors remain open',
        'exchange_weight_definition': 'integral alpha B R^2 (abs(P)+abs(F)) dl ds; coordinate-time weighted ADM exchange diagnostic',
        'fraction_of_full_tested_exchange_weight': float(np.trapezoid(frame.patch_exchange_weight, frame.s)/np.trapezoid(frame.full_exchange_weight, frame.s)),
        'input_sha256': {name: sha256_file(INPUT/name) for name in ('metric_fine.npz', 'medium_baseline.npz', 'medium_dense.npz')},
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/elastic_endpoint_reservoir')
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--cells', type=int, default=128)
    parser.add_argument('--medium', choices=['baseline', 'dense'], default='baseline')
    parser.add_argument('--forcing', type=float, default=1.)
    parser.add_argument('--cases', nargs='+', choices=list(CASES), default=list(CASES))
    parser.add_argument('--scope-only', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.workers <= 6 or args.cells < 16:
        parser.error('one to six workers and at least 16 cells required')
    args.output.mkdir(parents=True, exist_ok=True)
    if args.scope_only:
        scope_audit(args.output); return
    tasks = [(name, args.cells, args.medium, args.forcing, str(args.output)) for name in args.cases]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        futures = [pool.submit(run_case, task) for task in tasks]
        rows = [future.result() for future in as_completed(futures)]
    suffix = f'{args.medium}_n{args.cells}_force{args.forcing:g}'
    pd.DataFrame([{k: v for k, v in row.items() if k != 'law'} for row in rows]).to_csv(args.output/f'summary_{suffix}.csv', index=False)
    write_json(args.output/f'run_manifest_{suffix}.json', {
        'completed_utc': datetime.now(timezone.utc).isoformat(), 'cases': args.cases,
        'cells': args.cells, 'workers': args.workers, 'medium': args.medium, 'forcing': args.forcing,
        'software_sha256': {str(p.relative_to(ROOT)): sha256_file(p) for p in (
            Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/elastic_endpoint_reservoir.py')},
    })


if __name__ == '__main__':
    main()
