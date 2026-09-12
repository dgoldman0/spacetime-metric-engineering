#!/usr/bin/env python3
"""Separate response-amplitude limits from a conserved prestress degree.

The optional tensor (A/R^2,-A/R^2,0) is an exact radial conserved increment.
It is a mathematical support adjustment. Its physical constituents and end
connections require their own construction after this necessary energy gate.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
import json
import multiprocessing
import subprocess
import time

import numpy as np
from scipy.sparse import csr_matrix, vstack

from adm_harness.composite_capacitor import anisotropic_moments
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.pressure_linked_storage import retained_coefficient_program
from adm_harness.source_ledger import sha256_file
from audit_joint_support import bilinear
from run_joint_response_family import ResponseFamily, NPARAM
from run_joint_time_projected_candidate import audit_projection
from run_joint_continuum_projection import fixed_coefficients
from run_joint_spacetime_support import assemble_fixed
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'joint_response_relaxation'
BASIS = BASE/'joint_response_family/responses.npz'


def evaluate(spec):
    fraction, prestress = spec; start = time.monotonic()
    family = ResponseFamily(); h = family.h
    with np.load(BASIS) as z: basis = {k:z[k] for k in z.files}
    t, x = basis['t'], basis['x']; c = fixed_coefficients(h, t, x)
    old = h.reference.h.state
    thermal = bilinear(old['t'], old['x'], old['thermal'], t, x)[0]
    number = np.interp(x, old['x'], old['number'])
    m = basis['energy']/c['D'][:, :, None]
    p = basis['pressure']; q = basis['angular']/c['D'][:, :, None]
    if prestress:
        radial = 1/c['radius']**2
        m = np.concatenate([m, radial[:, :, None]], axis=-1)
        p = np.concatenate([p, -radial[:, :, None]], axis=-1)
        q = np.concatenate([q, np.zeros_like(radial[:, :, None])], axis=-1)
    dim = m.shape[-1]-1; arrays = []; rhs = []

    def add(values, peak=0.):
        flat = values.reshape(-1, dim+1)
        arrays.append(csr_matrix(np.c_[flat[:, 1:], np.full(len(flat), peak)]))
        rhs.append(-flat[:, 0])

    for sr in (-1., 1.):
        for sq in (-1., 2.): add(sr*p+sq*q-fraction*m)
    for z in np.linspace(-1, 1, 7):
        rr = c['gamma']**2*(1-c['v']*z)**2
        pr = c['gamma']**2*(c['v']-z)**2; pt = 1-z*z
        val = rr[:, :, None]*m+pr[:, :, None]*p+pt*q
        val[..., 0] += (number+thermal)/c['D']*rr+thermal/(3*c['D'])*(pr+pt)
        add(val, -1.)
    matrix = vstack(arrays, format='csr'); vector = np.concatenate(rhs)
    cost = np.zeros(dim+1); cost[-1] = 1.
    bounds = [(None, None)]*NPARAM+([(0., None)] if prestress else [])+[(0., None)]
    result = retained_coefficient_program(cost, method='highs-ipm', deadline=120.,
        A_ub=matrix, b_ub=vector, bounds=bounds)
    label = f'fraction{fraction:g}'+('_prestress' if prestress else '_unbounded')
    summary = dict(label=label, success=bool(result.success), status=int(result.status),
        message=result.message, control_bounds=None, fraction=fraction,
        conserved_radial_increment=prestress, end_connections_supplied=False,
        constitutive_law_supplied=False)
    if result.success:
        weights = np.r_[1., result.x[:-1]]
        rho = m@weights; pressure = p@weights; angular = q@weights
        tensor = anisotropic_moments((number+thermal)/c['D']+rho,
            thermal/(3*c['D'])+pressure, thermal/(3*c['D'])+angular, c['v'])
        exact = float(maximum_null(tensor)[0].max())
        checked = result.x.copy(); checked[-1] = max(checked[-1], exact)
        violation = float(np.maximum(matrix@checked-vector, 0).max())
        state = dict(t=t, x=x, support_energy=rho*c['D'], radial_pressure=pressure,
            radial_volume=pressure*c['D'], angular_volume=angular*c['D'],
            local_exchange=basis['local_exchange'], parameters=result.x[:-1])
        proxy = SimpleNamespace(h=h, coefficients=lambda at, ax:
            family.selected_coefficients(result.x[:NPARAM], at, ax))
        audit = audit_projection(proxy, state)
        summary.update(audit, parameters=result.x[:-1].tolist(),
            material_peak_sampled_lower=float(result.fun), material_peak_exact_upper=exact,
            maximum_original_inequality_violation=violation,
            maximum_absolute_control=float(abs(result.x[:NPARAM]).max()),
            radial_increment=float(result.x[NPARAM]) if prestress else 0.,
            initial_support_rest=float(4*np.pi*np.trapezoid(state['support_energy'][0], x)),
            final_support_rest=float(4*np.pi*np.trapezoid(state['support_energy'][-1], x)),
            member_energy_admissible=bool(audit['maximum_separate_member_density_shortfall']<1e-7))
        fixed, unused = assemble_fixed(h, t, x, c); phases = []
        for it, now, demand in h.reference.phases:
            geom = np.array([np.interp(x, h.reference.x, row) for row in demand])
            phases.append(dict(time=now, required_negative_null=float(
                maximum_null(tensor[:, it]+fixed[:, it]-geom)[0].max())))
        summary['phases'] = phases
        if violation > 2e-7: summary['success'] = False
        np.savez_compressed(OUTPUT/(label+'_states.npz'), **state)
    summary['elapsed_seconds'] = time.monotonic()-start
    write_json(OUTPUT/(label+'_summary.json'), summary)
    print(label+': '+json.dumps(summary), flush=True)
    return summary


def main():
    if OUTPUT.exists(): raise RuntimeError('preserve completed relaxation evidence')
    previous = BASE/'joint_response_family/manifest.json'
    hashes = json.loads(previous.read_text())['input_sha256']
    for p in (Path(__file__), previous, BASIS,
              Path(__file__).with_name('run_joint_time_projected_candidate.py')):
        hashes[str(p.relative_to(ROOT))] = sha256_file(p)
    for p, expected in hashes.items():
        if sha256_file(ROOT/p) != expected: raise RuntimeError('changed response input: '+p)
    OUTPUT.mkdir()
    with ProcessPoolExecutor(max_workers=2, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(evaluate, [(.9, False), (1., False), (.9, True), (.75, True)]))
    write_json(OUTPUT/'summary.json', dict(cases=results))
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        input_sha256=hashes, output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__ == '__main__': main()
