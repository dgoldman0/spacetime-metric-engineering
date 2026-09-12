#!/usr/bin/env python3
"""Refine the selected coupled route/material response with fixed controls."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import multiprocessing
import subprocess

import numpy as np

from adm_harness.source_ledger import sha256_file
from adm_harness.time_support_projection import evolve_support
from run_joint_response_family import ResponseFamily, NPARAM
from run_joint_route_response import routed_coefficients
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'joint_routed_support_refinement'
TARGET = BASE/'joint_route_response/fraction0.99_states.npz'


def build(intervals, time_factor):
    f = ResponseFamily(intervals, time_factor)
    with np.load(TARGET) as z: old = {k:z[k] for k in z.files}
    controls = old['parameters']; weights = np.r_[1., controls[:NPARAM]]
    initial, incoming, rate = f.preparation()
    coefficients = lambda t,x:routed_coefficients(f, controls, t, x)
    result = evolve_support(f.t, f.x, coefficients, initial@weights, incoming@weights, rate@weights)
    c = coefficients(f.t, f.x)
    state = dict(t=f.t, x=f.x, support_energy=result['support_energy'],
        radial_pressure=result['radial_pressure'], radial_volume=result['radial_pressure']*c['D'],
        angular_volume=c['Q'], local_exchange=result['local_exchange'], parameters=controls)
    return state, old


def evaluate(intervals):
    import audit_joint_dense_work as dense
    dense.OUTPUT = OUTPUT
    state, unused = build(intervals, 2)
    label = f'n{intervals}_timefactor2'
    path = OUTPUT/(label+'_states.npz')
    np.savez_compressed(path, **state)
    return dense.evaluate(('routed_family', str(path.relative_to(BASE))))


def main():
    if OUTPUT.exists(): raise RuntimeError('preserve completed refinement evidence')
    previous = BASE/'joint_route_response/manifest.json'
    hashes = json.loads(previous.read_text())['input_sha256']
    for p in (Path(__file__), previous, TARGET,
              Path(__file__).with_name('run_joint_route_response.py'),
              Path(__file__).with_name('audit_joint_dense_work.py'),
              ROOT/'toolkit/adm_harness_cli/adm_harness/integrated_support_energy.py',
              ROOT/'toolkit/adm_harness_cli/adm_harness/conserved_radial_prestress.py'):
        hashes[str(p.relative_to(ROOT))] = sha256_file(p)
    for p, expected in hashes.items():
        if sha256_file(ROOT/p) != expected: raise RuntimeError('changed refinement input: '+p)
    OUTPUT.mkdir()
    control, original = build(128, 1)
    errors = {key:float(abs(control[key]-original[key]).max())
              for key in ('support_energy', 'radial_pressure', 'angular_volume')}
    if max(errors.values()) > 1e-8: raise ArithmeticError('response superposition changed: '+str(errors))
    write_json(OUTPUT/'superposition_control.json', errors)
    with ProcessPoolExecutor(max_workers=2, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(evaluate, (256, 512)))
    write_json(OUTPUT/'summary.json', dict(cases=results, original_grid_superposition_errors=errors))
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes, output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__ == '__main__': main()
