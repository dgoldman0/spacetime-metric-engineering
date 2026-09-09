#!/usr/bin/env python3
"""Check the tabulated static source against the independent 4D curvature code."""
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path
import argparse
import csv
import hashlib
import json
import multiprocessing

import numpy as np

from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.geometry_opening import StaticSlice
from adm_harness.metric_regularity import regularized_scalars
from adm_harness.source_ledger import SourceParams

ROOT = Path(__file__).resolve().parents[3]


def witness(task):
    label, coordinate, base, overrides, path = task
    with np.load(path) as data:
        profile = StaticSlice(**{name: data[name] for name in
            ('coordinate', 'radius', 'lapse', 'radial_scale')})
    params = replace(SourceParams(**base), **overrides)
    r, a, b, rp, rpp, ap, app = profile.jets(coordinate)
    tensor = np.array([(1-rp*rp)/(r*r)-2*rpp/r,
        -(1-rp*rp)/(r*r)+2*ap*rp/r, app+ap*ap+ap*rp/r+rpp/r])/(8*np.pi)
    rows = []
    for step in (.0005, .00025, .000125):
        result = evaluate_demand(.745, coordinate, params, step, step,
            holding=True, scalar_evaluator=regularized_scalars)
        direct = np.array([result[key] for key in ('rho', 'p_l', 'p_omega')])
        error = float(np.max(abs(direct-tensor))/max(np.max(abs(tensor)), 1e-30))
        rows.append(dict(label=label, coordinate=coordinate, stencil_step=step,
            analytic_density=float(tensor[0]), analytic_radial_pressure=float(tensor[1]),
            analytic_angular_pressure=float(tensor[2]),
            four_dimensional_density=float(direct[0]), four_dimensional_radial_pressure=float(direct[1]),
            four_dimensional_angular_pressure=float(direct[2]), normalized_tensor_error=error,
            absolute_static_current=abs(result['j_l'])))
    if rows[-1]['normalized_tensor_error'] > 5e-5:
        raise RuntimeError(f'independent curvature mismatch at {label}, {coordinate}: {rows[-1]}')
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT/'supporting_reports/data/archived_geometry_opening')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    manifest = ROOT/'supporting_reports/data/le_coupled_reset_source/manifest.json'
    specifications = ROOT/'toolkit/adm_harness_cli/specs/archived_geometry_opening.json'
    base = json.loads(manifest.read_text())['params']
    specs = {s['label']: s for s in json.loads(specifications.read_text())}
    cases = ('reference', 'radius205')
    tasks = [(label, x, base, specs[label]['overrides'], args.root/f'{label}_metric.npz')
             for label in cases for x in (-2.5, -.5, 0., .5, 2.5)]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        rows = [row for group in pool.map(witness, tasks) for row in group]
    with (args.root/'curvature_audit.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    sources = [manifest, specifications, Path(__file__),
        *[ROOT/'toolkit/adm_harness_cli/adm_harness'/name for name in
          ('geometry_boundary.py', 'geometry_opening.py', 'metric_regularity.py', 'source_ledger.py', 'receiver_regularity.py')],
        *[args.root/f'{label}_metric.npz' for label in cases]]
    finest = [row for row in rows if row['stencil_step'] == .000125]
    summary = dict(witnesses=len(tasks), stencil_levels=3,
        maximum_finest_tensor_error=max(row['normalized_tensor_error'] for row in finest),
        maximum_static_current=max(row['absolute_static_current'] for row in rows),
        source_hashes={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
    (args.root/'curvature_audit.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='source_hashes'}, indent=2))


if __name__ == '__main__':
    main()
