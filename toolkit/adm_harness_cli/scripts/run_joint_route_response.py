#!/usr/bin/env python3
"""Joint material response and directional work-wave momentum screen."""
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
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
from adm_harness.time_support_projection import evolve_support
from audit_joint_support import bilinear
from run_joint_response_family import ResponseFamily, NPARAM
from run_joint_time_projected_candidate import audit_projection
from run_joint_continuum_projection import fixed_coefficients
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'joint_route_response'
ORIGINAL = BASE/'joint_response_family/responses.npz'


def routed_coefficients(family, controls, t, x):
    c = family.selected_coefficients(controls[:NPARAM], t, x)
    delta = -2*(controls[NPARAM]*np.maximum(c['field_power'], 0)/.98+
                controls[NPARAM+1]*.98*np.maximum(-c['field_power'], 0))
    c['fixed_force'] += delta; c['wave_force'] += delta
    return c


def build_basis():
    f = ResponseFamily()
    with np.load(ORIGINAL) as z: b = {k:z[k] for k in z.files}
    t, x = b['t'], b['x']
    def response(which):
        def coefficients(at, ax):
            c = fixed_coefficients(f.h, at, ax)
            charge = c['field_power']; zero = np.zeros_like(charge)
            force = -2*(np.maximum(charge, 0)/.98 if which == 0 else .98*np.maximum(-charge, 0))
            c.update(Q=zero, fixed_force=force, fixed_power=zero)
            return c
        return evolve_support(t, x, coefficients, np.zeros(len(x)),
                              np.zeros(len(t)), np.zeros(len(x)))
    with ThreadPoolExecutor(max_workers=2) as pool: r = list(pool.map(response, (0, 1)))
    for key, source in (('energy', 'support_energy'), ('pressure', 'radial_pressure')):
        b[key] = np.concatenate([b[key], np.stack([v[source] for v in r], axis=-1)], axis=-1)
    b['angular'] = np.concatenate([b['angular'], np.zeros((*b['angular'].shape[:2], 2))], axis=-1)
    np.savez_compressed(OUTPUT/'responses.npz', **b)


def evaluate(fraction):
    start = time.monotonic(); f = ResponseFamily(); h = f.h
    with np.load(OUTPUT/'responses.npz') as z: b = {k:z[k] for k in z.files}
    t, x = b['t'], b['x']; c = fixed_coefficients(h, t, x)
    old = h.reference.h.state
    u = bilinear(old['t'], old['x'], old['thermal'], t, x)[0]
    n = np.interp(x, old['x'], old['number'])
    m = b['energy']/c['D'][:, :, None]; p = b['pressure']; q = b['angular']/c['D'][:, :, None]
    dim = m.shape[-1]-1; arrays = []; rhs = []
    def add(val, peak=0.):
        a = val.reshape(-1, dim+1)
        arrays.append(csr_matrix(np.c_[a[:, 1:], np.full(len(a), peak)])); rhs.append(-a[:, 0])
    for sr in (-1., 1.):
        for sq in (-1., 2.): add(sr*p+sq*q-fraction*m)
    for z in np.linspace(-1, 1, 7):
        rr = c['gamma']**2*(1-c['v']*z)**2; pr = c['gamma']**2*(c['v']-z)**2
        val = rr[:, :, None]*m+pr[:, :, None]*p+(1-z*z)*q
        val[..., 0] += (n+u)/c['D']*rr+u/(3*c['D'])*(pr+1-z*z)
        add(val, -1.)
    matrix = vstack(arrays, format='csr'); vector = np.concatenate(rhs)
    objective = np.zeros(dim+1); objective[-1] = 1.
    result = retained_coefficient_program(objective, method='highs-ipm', deadline=150.,
        A_ub=matrix, b_ub=vector, bounds=[(None, None)]*NPARAM+[(0., 1.)]*2+[(0., None)])
    label = f'fraction{fraction:g}'
    summary = dict(label=label, fraction=fraction, success=bool(result.success),
        status=int(result.status), message=result.message, constitutive_law_supplied=False,
        physical_route_supplied=False, changed_route_stress_counted=False,
        end_connections_supplied=False)
    if result.success:
        weights = np.r_[1., result.x[:-1]]; rho = m@weights; pressure = p@weights; angular = q@weights
        tensor = anisotropic_moments((n+u)/c['D']+rho, u/(3*c['D'])+pressure,
                                     u/(3*c['D'])+angular, c['v'])
        upper = float(maximum_null(tensor)[0].max())
        checked = result.x.copy(); checked[-1] = max(upper, checked[-1])
        violation = float(np.maximum(matrix@checked-vector, 0).max())
        state = dict(t=t, x=x, support_energy=rho*c['D'], radial_pressure=pressure,
            radial_volume=pressure*c['D'], angular_volume=angular*c['D'],
            local_exchange=b['local_exchange'], parameters=result.x[:-1])
        proxy = SimpleNamespace(h=h, coefficients=lambda at, ax:routed_coefficients(f, result.x[:-1], at, ax))
        audit = audit_projection(proxy, state)
        summary.update(audit, parameters=result.x[:-1].tolist(),
            absorption_left_feed_fraction=float(result.x[NPARAM]),
            recovery_left_emission_fraction=float(result.x[NPARAM+1]),
            material_peak_lower=float(result.fun), material_peak_upper=upper,
            maximum_original_inequality_violation=violation,
            initial_support_rest=float(4*np.pi*np.trapezoid(state['support_energy'][0], x)),
            final_support_rest=float(4*np.pi*np.trapezoid(state['support_energy'][-1], x)),
            member_energy_admissible=bool(audit['maximum_separate_member_density_shortfall']<1e-7))
        if violation > 2e-7: summary['success'] = False
        np.savez_compressed(OUTPUT/(label+'_states.npz'), **state)
    summary['elapsed_seconds'] = time.monotonic()-start
    write_json(OUTPUT/(label+'_summary.json'), summary)
    print(label+': '+json.dumps(summary), flush=True)
    return summary


def main():
    if OUTPUT.exists(): raise RuntimeError('preserve completed joint routing evidence')
    previous = BASE/'joint_response_family/manifest.json'
    hashes = json.loads(previous.read_text())['input_sha256']
    for p in (Path(__file__), previous, ORIGINAL,
              Path(__file__).with_name('run_joint_time_projected_candidate.py')):
        hashes[str(p.relative_to(ROOT))] = sha256_file(p)
    for p, expected in hashes.items():
        if sha256_file(ROOT/p) != expected: raise RuntimeError('changed joint routing input: '+p)
    OUTPUT.mkdir(); build_basis()
    with ProcessPoolExecutor(max_workers=3, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(evaluate, (.75, .9, .99)))
    write_json(OUTPUT/'summary.json', dict(cases=results))
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        input_sha256=hashes, output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__ == '__main__': main()
