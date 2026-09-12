#!/usr/bin/env python3
"""Optimistic gate for an arbitrary time-independent radial tube grading.

Each spatial node has its own positive amplitude A(x), fixed through time.
The total backing still solves the registered conservation equations. A
spatial gradient in A transfers force to the other backing components; the
physical field or material establishing that grading remains unconstructed.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

import numpy as np
from scipy.sparse import coo_matrix, csr_matrix, hstack, vstack

from adm_harness.composite_capacitor import anisotropic_moments
from adm_harness.cutting_plane_lp import solve_with_cuts
from adm_harness.field_membrane_support import decompose
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.source_ledger import sha256_file
from audit_joint_support import bilinear
from run_joint_response_family import ResponseFamily, NPARAM
from run_joint_continuum_projection import fixed_coefficients
from run_joint_route_response import routed_coefficients
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'graded_vortex_support_gate'


def evaluate(intervals):
    directory = 'joint_refined_response' if intervals == 256 else 'joint_route_response'
    with np.load(BASE/directory/'responses.npz') as archive:
        b = {key:archive[key] for key in archive.files}
    t, x = b['t'], b['x']; nt, nx = len(t), len(x)
    family = ResponseFamily(intervals, 2 if intervals == 256 else 1)
    c = fixed_coefficients(family.h, t, x)
    old = family.h.reference.h.state
    thermal = bilinear(old['t'], old['x'], old['thermal'], t, x)[0]
    number = np.interp(x, old['x'], old['number'])
    m = b['energy']/c['D'][:, :, None]
    p = b['pressure']; q = b['angular']/c['D'][:, :, None]
    blocks, rhs = [], []

    def add(values, amplitude_coefficient=0., peak=0.):
        flat = values.reshape(-1, NPARAM+3)
        amp = np.broadcast_to(amplitude_coefficient, (nt, nx)).ravel()
        grading = coo_matrix((amp, (np.arange(nt*nx), np.tile(np.arange(nx), nt))),
                             shape=(nt*nx, nx)).tocsr()
        grading.eliminate_zeros()
        blocks.append(hstack([csr_matrix(flat[:, 1:]), grading,
                              csr_matrix(np.full((len(flat), 1), peak))], format='csr'))
        rhs.append(-flat[:, 0])
    for radial, angular in [(1., 2.), (1., -1.), (-2., -1.)]:
        add(radial*p+angular*q-m, (radial+1)/c['radius']**2)
    for z in np.linspace(-1., 1., 7):
        rr = c['gamma']**2*(1-c['v']*z)**2
        pr = c['gamma']**2*(c['v']-z)**2
        values = rr[:, :, None]*m+pr[:, :, None]*p+(1-z*z)*q
        values[..., 0] += (number+thermal)/c['D']*rr+thermal/(3*c['D'])*(pr+1-z*z)
        add(values, peak=-1.)
    matrix = vstack(blocks, format='csr'); vector = np.concatenate(rhs)
    del blocks, rhs
    cost = np.zeros(NPARAM+2+nx+1); cost[-1] = 1.
    bounds = [(None, None)]*NPARAM+[(0., 1.)]*2+[(0., None)]*(nx+1)
    result = solve_with_cuts(cost, matrix, vector, bounds, deadline=180., max_rounds=60)
    label = f'n{intervals}'
    summary = dict(label=label, success=bool(result.success), status=int(result.status),
        message=result.message, cut_history=result.cut_history, total_constraints=result.total_rows,
        spatial_grading_parameters=nx, time_independent_grading=True,
        smoothness_restriction_imposed=False, grading_medium_tensor_supplied=False,
        grading_exchange_law_supplied=False, finite_connections_supplied=False)
    if result.success:
        params = result.x[:NPARAM+2]; weights = np.r_[1., params]
        amplitude = result.x[NPARAM+2:-1]
        rho, radial, angular = m@weights, p@weights, q@weights
        s = amplitude[None, :]/c['radius']**2
        components = decompose(rho-s, radial+s, angular)
        tensor = anisotropic_moments((number+thermal)/c['D']+rho,
            thermal/(3*c['D'])+radial, thermal/(3*c['D'])+angular, c['v'])
        upper = float(maximum_null(tensor)[0].max())
        checked = result.x.copy(); checked[-1] = max(checked[-1], upper)
        violation = float(np.maximum(matrix@checked-vector, 0.).max())
        selected = routed_coefficients(family, params, t, x)
        derivative = np.gradient(amplitude, x, edge_order=2)
        force = -derivative[None, :]/(selected['ell']*selected['radius']**2)
        summary.update(material_peak_upper=upper, sampled_peak_lower=float(result.fun),
            original_matrix_violation=violation, minimum_residual_component_energy=float(components.min()),
            grading_amplitude_range=[float(amplitude.min()), float(amplitude.max())],
            grading_total_variation=float(abs(np.diff(amplitude)).sum()),
            sampled_grading_force_range=[float(force.min()), float(force.max())],
            initial_support_rest=float(4*np.pi*np.trapezoid(rho[0]*c['D'][0], x)),
            final_support_rest=float(4*np.pi*np.trapezoid(rho[-1]*c['D'][-1], x)))
        if violation > 2e-7 or components.min() < -2e-7:
            summary['success'] = False
        np.savez_compressed(OUTPUT/(label+'_states.npz'), t=t, x=x,
            support_energy=rho*c['D'], radial_pressure=radial, radial_volume=radial*c['D'],
            angular_volume=angular*c['D'], parameters=params, vortex_amplitude=amplitude,
            sampled_grading_force=force, local_exchange=b['local_exchange'])
    write_json(OUTPUT/(label+'_summary.json'), summary)
    print(label+': '+json.dumps({key:summary[key] for key in
          ['success', 'message', 'material_peak_upper', 'grading_amplitude_range'] if key in summary}), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if OUTPUT.exists():
        raise RuntimeError('preserve completed graded-vortex evidence')
    hashes = {}
    for name in ['joint_route_response', 'joint_refined_response']:
        path = BASE/name/'manifest.json'; manifest = json.loads(path.read_text())
        hashes.update(manifest['input_sha256'])
        basis = path.parent/'responses.npz'
        if sha256_file(basis) != manifest['output_sha256']['responses.npz']:
            raise RuntimeError('changed response basis: '+name)
        for source in [path, basis]:
            hashes[str(source.relative_to(ROOT))] = sha256_file(source)
    hashes[str(Path(__file__).relative_to(ROOT))] = sha256_file(Path(__file__))
    for relative, expected in hashes.items():
        if sha256_file(ROOT/relative) != expected:
            raise RuntimeError('changed graded-vortex input: '+relative)
    OUTPUT.mkdir()
    with ProcessPoolExecutor(max_workers=max(1, min(args.workers, 2)),
                             mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(evaluate, [128, 256]))
    write_json(OUTPUT/'summary.json', dict(cases=results))
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        input_sha256=hashes,
        output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
