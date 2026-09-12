#!/usr/bin/env python3
"""Audit scalar/flux allocation and conserved tube populations on active support."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import multiprocessing
import subprocess

import numpy as np
from numpy.polynomial.legendre import leggauss

from adm_harness.field_membrane_support import minimum_energy as old_minimum
from adm_harness.scalar_flux_support import (
    BASIS, bag_invariant_interval, decompose, equilibrium_vortex_interval,
    invariant_summary, minimum_energy, potential_interval,
)
from adm_harness.source_ledger import sha256_file
from audit_joint_dense_work import DenseHistory, surface_gate
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'scalar_flux_support_gate'


def tensors(history, times, positions, dense, time_weights=None, space_weights=None):
    if not dense:
        c = history.coefficients(times, positions)
        s = history.state
        return (s['support_energy']/c['D'], s['radial_pressure'],
                s['angular_volume']/c['D'], c['radius']), {}
    energy = history.energy(positions)
    values = [np.empty((len(times), len(positions))) for unused in range(4)]
    nf = npow = df = dp = 0.
    for begin in range(0, len(times), 24):
        now = times[begin:begin+24]
        c = history.coefficients(now, positions)
        mass, mass_t = energy.evaluate(now)
        p, pt, px = history.pressure(now, positions)
        rho = mass/c['D']; q = c['Q']/c['D']
        sample = (rho, p, q, c['radius'])
        inertia = (rho+p)*c['acceleration']
        temporal = c['v']/c['lapse']*pt
        gradient = px/c['ell']
        angular = 2*(p-q)*c['angular_gradient']
        support_power = (mass_t+c['D']*p*c['log_ell_t']+2*c['Q']*c['log_radius_t'])/(c['lapse']*c['D'])
        force = inertia+temporal+gradient+angular+c['fixed_force']
        power = support_power+c['fixed_power']
        measure = time_weights[begin:begin+len(now), None]*space_weights[None, :]*c['lapse']*c['D']
        nf += np.sum(measure*abs(force)); npow += np.sum(measure*abs(power))
        df += np.sum(measure*(abs(inertia)+abs(temporal)+abs(gradient)+abs(angular)+
                              sum(abs(c[k]) for k in ['fluid_force','field_force','wave_force','heat_force'])))
        dp += np.sum(measure*(abs(support_power)+
                              sum(abs(c[k]) for k in ['fluid_power','field_power','wave_power','heat_power'])))
        for output, value in zip(values, sample):
            output[begin:begin+len(now)] = value
    return tuple(values), dict(weighted_force_residual=float(nf/df), weighted_power_residual=float(npow/dp))


def audit(history, dense):
    s = history.state
    if dense:
        xe = np.unique(np.r_[s['x'], history.h.reference.h.state['x']])
        te = history.edges
        z, w = leggauss(3)
        gx = (xe[:-1, None]+np.diff(xe)[:, None]*(z+1)/2).ravel()
        gt = (te[:-1, None]+np.diff(te)[:, None]*(z+1)/2).ravel()
        x = np.unique(np.r_[xe, gx]); t = np.unique(np.r_[te, gt])
        wx = np.zeros(len(x)); wt = np.zeros(len(t))
        np.add.at(wx, np.searchsorted(x, gx), (np.diff(xe)[:, None]*w/2).ravel())
        np.add.at(wt, np.searchsorted(t, gt), (np.diff(te)[:, None]*w/2).ravel())
    else:
        t, x = s['t'], s['x']
        wt = wx = None
    (rho, p, q, radius), conservation = tensors(history, t, x, dense, wt, wx)
    shortfall = minimum_energy(p, q)-rho
    i, j = np.unravel_index(np.argmax(shortfall), shortfall.shape)
    summary = dict(temporal_samples=len(t), spatial_samples=len(x),
        local_component_gate_passes=bool(shortfall.max() <= 1e-8 and rho.min() >= 0.),
        maximum_scalar_flux_density_shortfall=float(np.maximum(shortfall, 0.).max()),
        maximum_old_field_membrane_shortfall=float(np.maximum(old_minimum(p, q)-rho, 0.).max()),
        minimum_density=float(rho.min()), **conservation,
        worst_local_margin=dict(time=float(t[i]), x=float(x[j]), density=float(rho[i, j]),
            radial_pressure=float(p[i, j]), angular_pressure=float(q[i, j]),
            energy_margin=float(-shortfall[i, j])))
    for name, function in [('equilibrium_vortices', equilibrium_vortex_interval),
                           ('leading_volume_bags', bag_invariant_interval)]:
        lo, hi = function(rho, p, q, radius)
        valid = np.isfinite(lo) & np.isfinite(hi)
        if np.all(valid):
            summary[name] = invariant_summary(lo, hi, t, x)
        else:
            summary[name] = dict(local_intervals_nonempty=False,
                common_invariant_feasible=False, invalid_samples=int(np.sum(~valid)),
                reason='local component interval is empty at the evaluated floating-point precision')
    vlo, vhi = potential_interval(rho, p, q)
    summary['fixed_core_potential'] = invariant_summary(vlo, vhi, t, x)
    if not dense:
        allocation = decompose(rho, p, q)
        rebuilt = np.einsum('ij,j...->i...', BASIS, allocation)
        summary['allocation_tensor_residual'] = float(np.max(np.abs(rebuilt-np.array([rho, p, q]))))
        summary['minimum_component_energy'] = float(allocation.min())
        np.savez_compressed(OUTPUT/(history.state_label+'_allocation.npz'), t=t, x=x,
            rho=rho, radial_pressure=p, angular_pressure=q, radius=radius,
            component_energy=allocation,
            component_names=np.array(['Maxwell','potential','radial_wave','angular_wave','angular_membrane','rest']))
    return summary


def evaluate(spec):
    source_directory, label, output_name = spec
    global OUTPUT
    OUTPUT = BASE/output_name
    path = BASE/source_directory/(label+'_states.npz')
    history = DenseHistory('routed_family', path)
    history.state_label = label
    result = dict(label=label, source=str(path.relative_to(ROOT)),
        node_audit=audit(history, False), dense_conserved_work_audit=audit(history, True),
        isolated_end_jackets=surface_gate(history),
        scope='prescribed active-rail backing target and registered component bases',
        field_equations_solved=False, finite_tube_wall_response_supplied=False,
        current_carrier_energy_supplied=False, continuing_rail_connections_supplied=False,
        quantum_source_supplied=False)
    write_json(OUTPUT/(label+'_summary.json'), result)
    print(label+': local='+str(result['dense_conserved_work_audit']['local_component_gate_passes'])+
          ', equilibrium='+str(result['dense_conserved_work_audit']['equilibrium_vortices']['common_invariant_feasible'])+
          ', bag='+str(result['dense_conserved_work_audit']['leading_volume_bags']['common_invariant_feasible']), flush=True)
    return result


def main():
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--source-directory', default='joint_refined_response')
    parser.add_argument('--labels', nargs='+', default=['members_fraction0.99', 'members_fraction1'])
    parser.add_argument('--output-name', default='scalar_flux_support_gate')
    args = parser.parse_args()
    global OUTPUT
    OUTPUT = BASE/args.output_name
    if OUTPUT.exists():
        raise RuntimeError('preserve completed scalar/flux evidence')
    labels = args.labels
    previous = BASE/args.source_directory/'manifest.json'
    manifest = json.loads(previous.read_text())
    hashes = dict(manifest['input_sha256'])
    for label in labels:
        name = label+'_states.npz'; path = previous.parent/name
        if sha256_file(path) != manifest['output_sha256'][name]:
            raise RuntimeError('changed archived target: '+name)
        hashes[str(path.relative_to(ROOT))] = sha256_file(path)
    for path in (previous, Path(__file__),
                 ROOT/'toolkit/adm_harness_cli/adm_harness/scalar_flux_support.py',
                 ROOT/'toolkit/adm_harness_cli/tests/test_scalar_flux_support.py'):
        hashes[str(path.relative_to(ROOT))] = sha256_file(path)
    for relative, expected in hashes.items():
        if sha256_file(ROOT/relative) != expected:
            raise RuntimeError('changed gate input: '+relative)
    OUTPUT.mkdir()
    with ProcessPoolExecutor(max_workers=max(1, min(args.workers, len(labels))),
                             mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(evaluate, [(args.source_directory, label, args.output_name) for label in labels]))
    write_json(OUTPUT/'summary.json', dict(cases=results))
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        input_sha256=hashes,
        output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
