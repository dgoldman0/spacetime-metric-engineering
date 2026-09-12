#!/usr/bin/env python3
"""Re-solve registered active support with potential or a conserved vortex bundle.

These are necessary component and conservation gates. The potential case
allows independent positive local potential energy; it supplies no scalar
field equation. The vortex case subtracts a single conserved A/R^2 tensor
from the total response and tests the remainder against the old component
basis. All registered material controls and both route fractions remain free.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess
import time

import numpy as np
from scipy.sparse import csr_matrix, vstack

from adm_harness.composite_capacitor import anisotropic_moments
from adm_harness.cutting_plane_lp import solve_with_cuts
from adm_harness.field_membrane_support import decompose as old_decompose
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.scalar_flux_support import decompose
from adm_harness.source_ledger import sha256_file
from audit_joint_support import bilinear
from run_joint_response_family import ResponseFamily, NPARAM
from run_joint_continuum_projection import fixed_coefficients
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'scalar_flux_response_family'


def evaluate(spec):
    intervals, mode = spec
    start = time.monotonic()
    basis_name = 'joint_refined_response' if intervals == 256 else 'joint_route_response'
    with np.load(BASE/basis_name/'responses.npz') as z:
        b = {key:z[key] for key in z.files}
    t, x = b['t'], b['x']
    family = ResponseFamily(intervals, 2 if intervals == 256 else 1)
    c = fixed_coefficients(family.h, t, x)
    old = family.h.reference.h.state
    thermal = bilinear(old['t'], old['x'], old['thermal'], t, x)[0]
    number = np.interp(x, old['x'], old['number'])
    m = b['energy']/c['D'][:, :, None]
    p = b['pressure']; q = b['angular']/c['D'][:, :, None]
    dim = NPARAM+2+(mode == 'conserved_vortex')
    arrays, rhs = [], []

    def add(value, vortex_coefficient=0., peak_coefficient=0.):
        flat = value.reshape(-1, NPARAM+3)
        a = np.zeros((len(flat), dim+1))
        a[:, :NPARAM+2] = flat[:, 1:]
        if mode == 'conserved_vortex':
            a[:, NPARAM+2] = np.broadcast_to(vortex_coefficient, (len(t), len(x))).ravel()
        a[:, -1] = peak_coefficient
        arrays.append(csr_matrix(a)); rhs.append(-flat[:, 0])

    if mode == 'potential':
        for radial, angular in [(1., 2.), (1., -1.), (-1., 0.), (0., -1.)]:
            add(radial*p+angular*q-m)
    else:
        for radial, angular in [(1., 2.), (1., -1.), (-2., -1.)]:
            add(radial*p+angular*q-m, (radial+1)/c['radius']**2)
    for z in np.linspace(-1., 1., 7):
        rr = c['gamma']**2*(1-c['v']*z)**2
        pr = c['gamma']**2*(c['v']-z)**2
        value = rr[:, :, None]*m+pr[:, :, None]*p+(1-z*z)*q
        value[..., 0] += (number+thermal)/c['D']*rr+thermal/(3*c['D'])*(pr+1-z*z)
        add(value, peak_coefficient=-1.)
    matrix = vstack(arrays, format='csr'); vector = np.concatenate(rhs)
    del arrays, rhs
    cost = np.zeros(dim+1); cost[-1] = 1.
    bounds = [(None, None)]*NPARAM+[(0., 1.)]*2
    if mode == 'conserved_vortex':
        bounds.append((0., None))
    bounds.append((0., None))
    result = solve_with_cuts(cost, matrix, vector, bounds, deadline=180.)
    label = f'n{intervals}_{mode}'
    summary = dict(label=label, mode=mode, basis=str((BASE/basis_name/'responses.npz').relative_to(ROOT)),
        success=bool(result.success), status=int(result.status), message=result.message,
        cut_history=result.cut_history, total_constraints=result.total_rows,
        material_control_amplitude_bounds=None, route_fraction_bounds=[0., 1.],
        intervals=len(x)-1, temporal_nodes=len(t),
        scalar_field_equations_supplied=False, current_carrier_energy_supplied=False,
        continuing_rail_connections_supplied=False, changed_route_stress_counted=False,
        continuum_convergence_established=False)
    if result.success:
        parameters = result.x[:NPARAM+2]
        weights = np.r_[1., parameters]
        rho, radial, angular = m@weights, p@weights, q@weights
        tensor = anisotropic_moments((number+thermal)/c['D']+rho,
            thermal/(3*c['D'])+radial, thermal/(3*c['D'])+angular, c['v'])
        upper = float(maximum_null(tensor)[0].max())
        checked = result.x.copy(); checked[-1] = max(upper, checked[-1])
        violation = float(np.maximum(matrix@checked-vector, 0.).max())
        if mode == 'potential':
            components = decompose(rho, radial, angular)
        else:
            amplitude = float(result.x[NPARAM+2])
            s = amplitude/c['radius']**2
            components = np.r_[old_decompose(rho-s, radial+s, angular), s[None, ...]]
            summary['conserved_vortex_amplitude'] = amplitude
        summary.update(material_peak_sampled_lower=float(result.fun), material_peak_upper=upper,
            maximum_original_inequality_violation=violation,
            minimum_component_energy=float(components.min()),
            initial_support_rest=float(4*np.pi*np.trapezoid(rho[0]*c['D'][0], x)),
            final_support_rest=float(4*np.pi*np.trapezoid(rho[-1]*c['D'][-1], x)),
            absorption_left_feed_fraction=float(parameters[NPARAM]),
            recovery_left_emission_fraction=float(parameters[NPARAM+1]),
            parameters=parameters.tolist())
        if violation > 2e-7 or components.min() < -2e-7:
            summary['success'] = False
        np.savez_compressed(OUTPUT/(label+'_states.npz'), t=t, x=x,
            support_energy=rho*c['D'], radial_pressure=radial, radial_volume=radial*c['D'],
            angular_volume=angular*c['D'], parameters=parameters,
            component_energy=components, local_exchange=b['local_exchange'])
    summary['elapsed_seconds'] = time.monotonic()-start
    write_json(OUTPUT/(label+'_summary.json'), summary)
    print(label+': '+json.dumps({key:summary[key] for key in
          ['success', 'message', 'material_peak_upper', 'conserved_vortex_amplitude'] if key in summary}), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if OUTPUT.exists():
        raise RuntimeError('preserve completed scalar/flux response evidence')
    hashes = {}
    for directory in ['joint_route_response', 'joint_refined_response']:
        path = BASE/directory/'manifest.json'; manifest = json.loads(path.read_text())
        hashes.update(manifest['input_sha256'])
        basis = path.parent/'responses.npz'
        if sha256_file(basis) != manifest['output_sha256']['responses.npz']:
            raise RuntimeError('changed conservative response basis: '+directory)
        hashes[str(path.relative_to(ROOT))] = sha256_file(path)
        hashes[str(basis.relative_to(ROOT))] = sha256_file(basis)
    for path in [Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/scalar_flux_support.py']:
        hashes[str(path.relative_to(ROOT))] = sha256_file(path)
    for relative, expected in hashes.items():
        if sha256_file(ROOT/relative) != expected:
            raise RuntimeError('changed response input: '+relative)
    OUTPUT.mkdir()
    specs = [(n, mode) for n in [128, 256] for mode in ['potential', 'conserved_vortex']]
    with ProcessPoolExecutor(max_workers=max(1, min(args.workers, len(specs))),
                             mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(evaluate, specs))
    write_json(OUTPUT/'summary.json', dict(cases=results))
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        input_sha256=hashes,
        output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
