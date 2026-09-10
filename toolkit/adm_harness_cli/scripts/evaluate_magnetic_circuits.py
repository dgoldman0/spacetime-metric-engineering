#!/usr/bin/env python3
"""Count complete short flux circuits against the native rail opening measure."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import resource
import time

import numpy as np

from adm_harness.magnetic_circuits import RailChart, loop_integrals, magnetic_budget

ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT/'supporting_reports/data/archived_geometry_opening/reference_metric.npz'
ETA = 2.4127904527582454e-5
CHART = None


def initialize():
    global CHART
    CHART = RailChart(CACHE)


def one_loop(task):
    x, leg, cap, nodes = task
    center = float(CHART.proper_of_x(x))
    row = loop_integrals(CHART.fields, center, leg, cap, nodes)
    row['center_coordinate'] = x
    row['budgets'] = []
    for q in (1, 8, 24):
        for margin in (3, 5):
            budget = magnetic_budget(row, q, margin)
            budget['positive_cases'] = []
            for flavors in (1, 8, 54):
                for coupling in (.1, .3, 1.):
                    loop_measure = flavors*coupling**2/(16*np.pi**2)
                    net = ETA*(flavors*budget['quantum_opening_per_species']
                               -budget['magnetic_load_at_e1']/coupling**2)
                    if net > 0:
                        budget['positive_cases'].append(dict(flavors=flavors, coupling=coupling,
                            loop_measure=loop_measure, net_opening=net))
            row['budgets'].append(budget)
    row['max_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--nodes', type=int, default=128)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4 or args.nodes < 16:
        raise ValueError('one to four workers and at least 16 quadrature nodes required')
    if args.output.exists() and any(args.output.iterdir()):
        raise FileExistsError('use a fresh evidence directory')
    args.output.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    geometry = RailChart(CACHE)
    tasks, excluded = [], []
    for x in (-6., -4., -2.5, -1., 0., 1., 2.5, 4., 6.):
        r = float(geometry.fields(geometry.proper_of_x(x))[0])
        for leg in (0., .25, .5, 1., 2., 4., 8., 16., 32., 64., 128.):
            for cap in (.05, .1, .25, .5, 1.):
                if cap/r <= .25:
                    tasks.append((x, leg, cap, args.nodes))
                else:
                    excluded.append(dict(center=x, leg=leg, cap=cap, half_angle=cap/r))
    with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize) as pool:
        rows = list(pool.map(one_loop, tasks))
    candidates = [(loop, b) for loop in rows for b in loop['budgets']
                  if b['required_loop_measure'] is not None]
    best_loop, best = min(candidates, key=lambda pair: pair[1]['required_loop_measure'])
    positive = [b for loop in rows for b in loop['budgets'] for config in b['positive_cases']]
    preferred_positive = sum(config['loop_measure'] <= .1 for loop in rows
                            for b in loop['budgets'] for config in b['positive_cases'])
    best_record = dict(geometry={k:v for k,v in best_loop.items() if k != 'budgets'}, budget=best)
    sources = [Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/magnetic_circuits.py',
               ROOT/'toolkit/adm_harness_cli/adm_harness/curved_boundary.py', CACHE]
    result = dict(eta=ETA, geometry_cases=len(rows), excluded_geometry_cases=len(excluded),
        source_cases=len(rows)*6*9, positive_source_cases=len(positive),
        preferred_positive_source_cases=preferred_positive,
        negative_quantum_opening_geometries=sum(row['quantum_coefficient'] <= 0 for row in rows),
        best=best_record, parameters=dict(nodes=args.nodes, workers=args.workers),
        elapsed_seconds=time.monotonic()-start, loops=rows, excluded=excluded,
        source_hashes={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
    (args.output/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('loops','excluded','source_hashes')}, indent=2))
    if sum(p.stat().st_size for p in args.output.iterdir()) > 10_000_000:
        raise RuntimeError('magnetic-circuit evidence allowance exceeded')


if __name__ == '__main__':
    main()
