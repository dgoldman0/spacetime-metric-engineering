#!/usr/bin/env python3
"""Optimistic momentum-routing gate before paying for a changed wave route.

Absorption and recovery may independently split between the two directions.
Their counted rest power stays fixed. A failed material gate already rejects
that support history; a passing gate would require new causal wave transport,
guide stress, tap response, and end connections before source acceptance.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import multiprocessing
import subprocess

import numpy as np
from scipy.optimize import linprog

from adm_harness.source_ledger import sha256_file
from adm_harness.time_support_projection import evolve_support
from audit_joint_support import bilinear
from run_joint_time_projected_candidate import ProjectionHistory, audit_projection
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'joint_route_momentum_gate'
REFERENCE = BASE/'joint_time_projected_candidate/n256_timefactor2_states.npz'


class RoutedHistory(ProjectionHistory):
    def __init__(self, fractions=(0., 0.)):
        super().__init__()
        self.fractions = fractions

    def coefficients(self, at, ax):
        c = super().coefficients(at, ax)
        charge, recovery = self.fractions
        absorbed = np.maximum(c['field_power'], 0.)/.98
        emitted = .98*np.maximum(-c['field_power'], 0.)
        correction = -2*(charge*absorbed+recovery*emitted)
        c['wave_force'] += correction
        c['fixed_force'] += correction
        return c


def response(which):
    fractions = (1., 0.) if which == 'absorption' else (0., 1.)
    history = RoutedHistory(fractions)
    with np.load(REFERENCE) as z: base = {k:z[k] for k in z.files}
    t, x = base['t'], base['x']; s = history.target
    c = history.coefficients(t, x)
    initial = np.interp(x, s['x'], s['support_energy'][0])
    incoming = np.interp(t, s['t'], s['radial_volume'][:, -1])/c['D'][:, -1]
    p0, pt0, unused = bilinear(s['t'], s['x'], s['radial_volume'], t[:1], x)
    initial_rate = (pt0[0]-c['volume_rate'][0]*p0[0])/c['D'][0]
    result = evolve_support(t, x, history.coefficients, initial, incoming, initial_rate)
    state = dict(t=t, x=x, support_energy=result['support_energy'],
                 radial_pressure=result['radial_pressure'],
                 radial_volume=result['radial_pressure']*c['D'],
                 angular_volume=c['Q'], local_exchange=result['local_exchange'])
    np.savez_compressed(OUTPUT/(which+'_states.npz'), **state)
    audit = audit_projection(history, state)
    write_json(OUTPUT/(which+'_summary.json'), dict(fractions=fractions, **audit))
    print(which+': '+json.dumps(audit), flush=True)
    return which


def optimize():
    history = RoutedHistory()
    with np.load(REFERENCE) as z: base = {k:z[k] for k in z.files}
    t, x = base['t'], base['x']; c = history.coefficients(t, x)
    energies = [base['support_energy']]; pressures = [base['radial_pressure']]
    for name in ('absorption', 'recovery'):
        with np.load(OUTPUT/(name+'_states.npz')) as z:
            energies.append(z['support_energy']-energies[0])
            pressures.append(z['radial_pressure']-pressures[0])
    m = np.stack(energies, axis=-1)/c['D'][:, :, None]
    p = np.stack(pressures, axis=-1)
    q = base['angular_volume']/c['D']
    cost = np.array([0., 0., 1.]); A = []; b = []
    for sr in (-1., 1.):
        for sq in (-1., 2.):
            cone = sr*p-m; cone[..., 0] += sq*q
            A.append(np.c_[cone[..., 1:].reshape(-1, 2), -np.ones(q.size)])
            b.append(-cone[..., 0].ravel())
    result = linprog(cost, A_ub=np.concatenate(A), b_ub=np.concatenate(b),
                     bounds=[(0., 1.), (0., 1.), (0., None)], method='highs')
    if not result.success: raise ArithmeticError(result.message)
    fractions = result.x[:2]; weights = np.r_[1., fractions]
    energy = np.stack(energies, axis=-1)@weights
    pressure = p@weights
    history.fractions = fractions
    state = dict(t=t, x=x, support_energy=energy, radial_pressure=pressure,
                 radial_volume=pressure*c['D'], angular_volume=base['angular_volume'],
                 local_exchange=base['local_exchange'])
    audit = audit_projection(history, state)
    rho = energy/c['D']; shortfall = abs(pressure)+np.maximum(-q, 2*q)-rho
    i, j = np.unravel_index(np.argmax(shortfall), shortfall.shape)
    summary = dict(absorption_left_fraction=float(fractions[0]),
        recovery_left_fraction=float(fractions[1]), node_density_deficit=float(result.fun),
        witness=dict(t=float(t[i]), x=float(x[j]), density=float(rho[i,j]),
                     radial_pressure=float(pressure[i,j]), angular_pressure=float(q[i,j])),
        **audit, wave_power_history_unchanged=True, added_route_cost_included=False,
        member_energy_admissible=bool(audit['maximum_separate_member_density_shortfall']<1e-7),
        physical_route_supplied=False)
    np.savez_compressed(OUTPUT/'selected_states.npz', **state)
    write_json(OUTPUT/'summary.json', summary)
    print('selected: '+json.dumps(summary), flush=True)


def main():
    if OUTPUT.exists(): raise RuntimeError('preserve completed routing evidence')
    previous = BASE/'joint_time_projected_candidate/manifest.json'
    hashes = json.loads(previous.read_text())['input_sha256']
    for p in (Path(__file__), previous, REFERENCE):
        hashes[str(p.relative_to(ROOT))] = sha256_file(p)
    for p, expected in hashes.items():
        if sha256_file(ROOT/p) != expected: raise RuntimeError('changed route input: '+p)
    OUTPUT.mkdir()
    with ProcessPoolExecutor(max_workers=2, mp_context=multiprocessing.get_context('spawn')) as pool:
        list(pool.map(response, ('absorption', 'recovery')))
    optimize()
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        input_sha256=hashes, output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__ == '__main__': main()
