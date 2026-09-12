#!/usr/bin/env python3
"""Bounded convex-coupling screen for the scheduled radial/angular support.

These are necessary or sufficient interpolation conditions for a convex
two-stretch energy. Full relativistic material stability remains a separate
condition. The original discrete work quadrature is retained and declared.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import multiprocessing
import subprocess
import time

import numpy as np

from adm_harness.composite_capacitor import anisotropic_moments
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.joint_support_envelope import build_envelope
from adm_harness.pressure_linked_storage import retained_coefficient_program
from adm_harness.source_ledger import sha256_file
from run_joint_backing_link import JointHistory
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'joint_coupled_passivity'


def add_coupling_constraints(p, ell, radius, mode):
    nt, nx = ell.shape
    size, ub = p['size'], p['ub']
    for j in range(nx):
        pairs = ((i, k) for i in range(nt-1)
                 for k in (range(i+1, nt) if mode != 'tangent' else (i+1,)))
        for i, k in pairs:
            de, dr = ell[k, j]-ell[i, j], radius[k, j]-radius[i, j]
            if abs(de)/ell[i, j]+abs(dr)/radius[i, j] < 1e-10:
                continue
            ii, kk = i*nx+j, k*nx+j
            if mode == 'planes':
                # M_k >= M_i + grad M_i dot (stretch_k-stretch_i).
                ub.add([(size+ii, 1.), (size+kk, -1.),
                        (2*size+ii, -de/ell[i, j]), (3*size+ii, -2*dr/radius[i, j])])
                ub.add([(size+kk, 1.), (size+ii, -1.),
                        (2*size+kk, de/ell[k, j]), (3*size+kk, 2*dr/radius[k, j])])
            else:
                # Monotonicity of the coupled gradient (-P/ell,-2Q/R).
                ub.add([(2*size+kk, de/ell[k, j]), (2*size+ii, -de/ell[i, j]),
                        (3*size+kk, 2*dr/radius[k, j]), (3*size+ii, -2*dr/radius[i, j])])


def evaluate(spec):
    mode, fraction = spec
    start = time.monotonic()
    h = JointHistory(32, 8)
    label = mode+'_fraction'+str(fraction)
    p = build_envelope(h.t, h.x, h.c, h.log_radius_t, h.thermal, h.number,
                       h.force_rhs, h.radial_field, freeze_fluid=True)
    size = p['size']
    for k in range(size):
        for radial in (-1., 1.):
            for angular in (-1., 2.):
                p['ub'].add([(2*size+k, radial), (3*size+k, angular), (size+k, -fraction)])
    add_coupling_constraints(p, h.c['gamma']*h.c['b'], h.c['radius'], mode)
    eq, ub = p['eq'].matrix(), p['ub'].matrix()
    result = retained_coefficient_program(p['cost'], method='highs-ipm', deadline=100.,
        A_eq=eq, b_eq=p['eq'].rhs, A_ub=ub, b_ub=p['ub'].rhs, bounds=p['bounds'])
    s = dict(label=label, success=bool(result.success), status=int(result.status),
             message=result.message, mode=mode, separate_member_fraction=fraction,
             time_nodes=len(h.t), intervals=len(h.x)-1,
             constitutive_energy_supplied=False, relativistic_stability_supplied=False)
    if result.success:
        u, m, pr, pt = result.x[:-1].reshape(4, len(h.t), len(h.x))
        d = h.c['rest_volume']
        tensor = anisotropic_moments((h.number+u+m)/d, (u/3+pr)/d, (u/3+pt)/d, h.c['v'])
        upper = float(maximum_null(tensor)[0].max())
        checked = result.x.copy(); checked[-1] = max(upper, checked[-1])
        er = float(abs(eq@checked-p['eq'].rhs).max())
        ur = float(max(0., np.max(ub@checked-p['ub'].rhs)))
        s.update(material_peak_lower=float(result.x[-1]), material_peak_upper=upper,
                 max_scaled_equality_residual=er, max_inequality_violation=ur,
                 initial_support_rest=float(4*np.pi*np.trapezoid(m[0], h.x)),
                 final_support_rest=float(4*np.pi*np.trapezoid(m[-1], h.x)),
                 phases=[dict(time=t, required_negative_null=float(maximum_null(tensor[:,i]+h.fixed[:,i]-demand)[0].max()))
                         for i, t, demand in h.phases])
        if max(er, ur) > 2e-7:
            s.update(success=False, message='independent matrix verification failed')
        np.savez_compressed(OUTPUT/(label+'_states.npz'), t=h.t, x=h.x, thermal=u,
                            support_energy=m, radial_volume=pr, angular_volume=pt)
    s['elapsed_seconds'] = time.monotonic()-start
    write_json(OUTPUT/(label+'_summary.json'), s)
    print(label+': '+s['message'], flush=True)
    return s


def main():
    if OUTPUT.exists():
        raise RuntimeError('preserve completed coupled-passivity evidence')
    previous = BASE/'joint_component_cone/manifest.json'
    hashes = json.loads(previous.read_text())['input_sha256']
    for p in (Path(__file__), previous):
        hashes[str(p.relative_to(ROOT))] = sha256_file(p)
    for p, expected in hashes.items():
        if sha256_file(ROOT/p) != expected:
            raise RuntimeError('changed coupled-support input: '+p)
    OUTPUT.mkdir()
    with ProcessPoolExecutor(max_workers=4, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(evaluate, [('tangent', 1.), ('tangent', .9), ('pairs', 1.), ('planes', 1.)]))
    write_json(OUTPUT/'summary.json', dict(cases=results))
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        input_sha256=hashes, output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
