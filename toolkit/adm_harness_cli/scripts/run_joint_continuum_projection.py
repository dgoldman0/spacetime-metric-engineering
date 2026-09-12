#!/usr/bin/env python3
"""Refine the joint support directly under fixed angular and left-end history."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess
import time

import numpy as np

from adm_harness.joint_support_projection import project_balance
from adm_harness.pressure_linked_storage import fluid_coefficients
from adm_harness.source_ledger import sha256_file
from audit_joint_support import bilinear
from run_joint_backing_link import JointHistory
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'joint_support_projection'
TARGET = BASE/'joint_component_cone/separate_members_scheduled_states.npz'


def fixed_coefficients(h, at, ax):
    c = fluid_coefficients(h.reference.h.model, at, ax)
    metric = [h.reference.h.model.metric(float(time), ax) for time in at]
    lr = np.array([g.logr_t for g in metric])
    vx = np.array([c['v'][i]*(g.logb_x-g.alpha_x/g.alpha)+g.b*g.beta_x/g.alpha
                   for i, g in enumerate(metric)])
    lx = np.array([g.logb_x+2*g.logr_x for g in metric])+c['gamma']**2*c['v']*vx
    old = h.reference.h.state
    u, ut, ux = bilinear(old['t'], old['x'], old['thermal'], at, ax)
    field, ft, fx = bilinear(old['t'], old['x'], old['flux_energy'], at, ax)
    share, sx = h.allocation(ax)
    number = np.interp(ax, old['x'], old['number'])
    d, ell, lapse = c['rest_volume'], c['gamma']*c['b'], c['lapse']
    r4 = c['radius']**4
    fluid_f = ((number+4*u/3)/d*c['acceleration']+
               c['v']/lapse*(ut-c['volume_rate']*u)/(3*d)+(ux-lx*u)/(3*d*ell))
    fluid_p = (ut+c['volume_rate']*u/3)/(lapse*d)
    charge = ft/(lapse*r4)
    field_f = -(fx-sx)/(ell*r4)-c['v']*charge
    wave_f = np.maximum(charge, 0)/.98+.98*np.maximum(-charge, 0)
    wave_p = -np.maximum(charge, 0)/.98+.98*np.maximum(-charge, 0)
    receiver, receiver_t, unused = bilinear(h.reference.t, h.reference.x,
        h.state['heat']+h.state['heat_cap']/3, at, ax)
    heat_f = receiver/d*c['acceleration']
    heat_p = receiver_t/(lapse*d)
    c.update(ell=ell, D=d, log_radius_t=lr, log_ell_t=c['volume_rate']-2*lr,
             log_volume_x=lx, fixed_force=fluid_f+field_f+wave_f+heat_f,
             fixed_power=fluid_p+charge+wave_p+heat_p,
             fluid_force=fluid_f, field_force=field_f, wave_force=wave_f, heat_force=heat_f,
             fluid_power=fluid_p, field_power=charge, wave_power=wave_p, heat_power=heat_p)
    return c


class ProjectionHistory:
    def __init__(self, target=TARGET):
        self.h = JointHistory(32, 8)
        with np.load(target) as z:
            self.target = {k:z[k] for k in z.files}

    def coefficients(self, at, ax):
        c = fixed_coefficients(self.h, at, ax)
        s = self.target
        c['Q'] = bilinear(s['t'], s['x'], s['angular_volume'], at, ax)[0]
        return c


def audit_projection(history, state, quadrature_order=3):
    """Off-collocation force and power using analytic bilinear derivatives."""
    from numpy.polynomial.legendre import leggauss
    t, x = state['t'], state['x']
    z, w = leggauss(quadrature_order)
    # Use every original time panel and allocation panel, split at all new
    # support knots. This resolves discontinuities in the pinned inputs.
    old = history.h.reference.h.state
    te = np.unique(np.r_[t, old['t']]); xe = np.unique(np.r_[x, old['x']])
    at = (te[:-1, None]+np.diff(te)[:, None]*(z+1)/2).ravel()
    ax = (xe[:-1, None]+np.diff(xe)[:, None]*(z+1)/2).ravel()
    # Batched time slices keep refined audits within laptop memory.
    numerator_f = numerator_p = denominator_f = denominator_p = 0.
    max_force = max_power = max_cone = 0.; min_density = np.inf
    max_relative_cone = 0.
    wx = (np.diff(xe)[:, None]*w/2).ravel()
    wt = (np.diff(te)[:, None]*w/2).ravel()
    for begin in range(0, len(at), 24):
        tt = at[begin:begin+24]
        c = history.coefficients(tt, ax)
        m, mt, unused = bilinear(t, x, state['support_energy'], tt, ax)
        p, pt, px = bilinear(t, x, state['radial_pressure'], tt, ax)
        q = c['Q']/c['D']
        inertia = (m/c['D']+p)*c['acceleration']
        temporal = c['v']/c['lapse']*pt
        gradient = px/c['ell']
        angular = 2*(p-q)*c['angular_gradient']
        power_s = (mt+c['D']*p*c['log_ell_t']+2*c['Q']*c['log_radius_t'])/(c['lapse']*c['D'])
        force = inertia+temporal+gradient+angular+c['fixed_force']
        power = power_s+c['fixed_power']
        proper = wt[begin:begin+24, None]*wx[None, :]*c['lapse']*c['D']
        numerator_f += np.sum(proper*abs(force)); numerator_p += np.sum(proper*abs(power))
        denominator_f += np.sum(proper*(abs(inertia)+abs(temporal)+abs(gradient)+abs(angular)+
            sum(abs(c[k]) for k in ('fluid_force','field_force','wave_force','heat_force'))))
        denominator_p += np.sum(proper*(abs(power_s)+
            sum(abs(c[k]) for k in ('fluid_power','field_power','wave_power','heat_power'))))
        max_force = max(max_force, float(abs(force).max()))
        max_power = max(max_power, float(abs(power).max()))
        rho = m/c['D']; floor = abs(p)+np.maximum(-q, 2*q)
        max_cone = max(max_cone, float(np.maximum(floor-rho, 0).max()))
        max_relative_cone = max(max_relative_cone, float(np.maximum(floor-rho, 0).max()/max(abs(rho).max(), 1e-30)))
        min_density = min(min_density, float(rho.min()))
    return dict(weighted_force_residual=float(numerator_f/denominator_f),
                weighted_power_residual=float(numerator_p/denominator_p),
                maximum_force_residual=max_force, maximum_power_residual=max_power,
                maximum_separate_member_density_shortfall=max_cone,
                maximum_batch_relative_member_shortfall=max_relative_cone,
                minimum_support_density=min_density,
                audit_time_samples=len(at), audit_spatial_samples=len(ax))


def evaluate(spec):
    intervals, stride = spec
    start = time.monotonic(); history = ProjectionHistory(); h = history.h
    s = history.target
    indices = np.unique(np.r_[np.arange(0, len(h.reference.t), stride), len(h.reference.t)-1,
                               [i for i, unused, unused in h.reference.phases]])
    t = h.reference.t[indices]
    x = np.linspace(h.knots[0], h.knots[-1], intervals+1)
    c = history.coefficients(t, x)
    initial = np.interp(x, s['x'], s['support_energy'][0])
    left = np.interp(t, s['t'], s['radial_volume'][:, 0])/c['D'][:, 0]
    result = project_balance(t, x, history.coefficients, initial, left,
                             spatial_subpanels=max(1, 128//intervals))
    state = dict(t=t, x=x, support_energy=result['support_energy'], radial_pressure=result['radial_pressure'],
                 radial_volume=result['radial_pressure']*c['D'], angular_volume=c['Q'],
                 local_exchange=result['local_exchange'])
    audit = audit_projection(history, state)
    label = f'n{intervals}_stride{stride}'
    summary = dict(label=label, intervals=intervals, time_stride=stride, time_nodes=len(t),
        **audit, **{k:v for k,v in result.items() if not isinstance(v, np.ndarray)},
        initial_support_rest=float(4*np.pi*np.trapezoid(result['support_energy'][0], x)),
        final_support_rest=float(4*np.pi*np.trapezoid(result['support_energy'][-1], x)),
        gross_local_exchange=float(4*np.pi*np.trapezoid(abs(result['local_exchange']).sum(axis=0), x)),
        elapsed_seconds=time.monotonic()-start,
        constitutive_law_supplied=False)
    np.savez_compressed(OUTPUT/(label+'_states.npz'), **state)
    write_json(OUTPUT/(label+'_summary.json'), summary)
    print(label+': '+json.dumps(audit), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if OUTPUT.exists():
        raise RuntimeError('preserve completed projection evidence')
    previous = BASE/'joint_component_cone/manifest.json'
    hashes = json.loads(previous.read_text())['input_sha256']
    for p in (Path(__file__), previous, TARGET,
              ROOT/'toolkit/adm_harness_cli/adm_harness/joint_support_projection.py',
              ROOT/'toolkit/adm_harness_cli/scripts/audit_joint_support.py'):
        hashes[str(p.relative_to(ROOT))] = sha256_file(p)
    for p, expected in hashes.items():
        if sha256_file(ROOT/p) != expected:
            raise RuntimeError('changed projection input: '+p)
    OUTPUT.mkdir()
    with ProcessPoolExecutor(max_workers=min(4, args.workers), mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(evaluate, [(32,8), (64,4), (128,2), (256,1)]))
    write_json(OUTPUT/'summary.json', dict(cases=results))
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        input_sha256=hashes, output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
