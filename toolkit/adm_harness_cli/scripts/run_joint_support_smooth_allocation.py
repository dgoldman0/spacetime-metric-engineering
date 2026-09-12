#!/usr/bin/env python3
"""Joint conserved support with finite member margins and direct input divergence."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import multiprocessing
import subprocess

import numpy as np
from numpy.polynomial.legendre import leggauss

from adm_harness.graded_electrothermal import maximum_null
from adm_harness.monotone_field_allocation import monotone_allocation
from adm_harness.shared_field_delivery import average_electric_rate
from adm_harness.joint_support_least_squares import solve_least_squares
from adm_harness.poynting_delivery import wave_moments
from adm_harness.regenerative_converter import compact_cell_moments
from adm_harness.shared_field_delivery import radial_field_moments
from adm_harness.source_ledger import sha256_file
from audit_joint_support import bilinear
from run_joint_backing_link import JointHistory
from run_joint_continuum_projection import fixed_coefficients
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'joint_support_smooth_allocation'


def audit_schedule(h, state, *, order=3):
    t, x = state['t'], state['x']; old = h.reference.h.state
    z, w = leggauss(order)
    te = np.unique(np.r_[t, old['t']]); xe = np.unique(np.r_[x, old['x']])
    at = (te[:-1,None]+np.diff(te)[:,None]*(z+1)/2).ravel()
    ax = (xe[:-1,None]+np.diff(xe)[:,None]*(z+1)/2).ravel()
    wt = (np.diff(te)[:,None]*w/2).ravel(); wx = (np.diff(xe)[:,None]*w/2).ravel()
    sums = np.zeros(4); max_force = max_power = max_shortfall = 0.; min_density = np.inf
    for begin in range(0,len(at),24):
        tt = at[begin:begin+24]; c = fixed_coefficients(h,tt,ax)
        m, mt, unused = bilinear(t,x,state['support_energy'],tt,ax)
        p, pt, px = bilinear(t,x,state['radial_volume'],tt,ax)
        q, unused, unused = bilinear(t,x,state['angular_volume'],tt,ax)
        d = c['D']; inertia = (m+p)/d*c['acceleration']
        temporal = c['v']/c['lapse']*(pt-c['volume_rate']*p)/d
        gradient = (px-c['log_volume_x']*p)/(d*c['ell'])
        angular = 2*(p-q)/d*c['angular_gradient']
        power_s = (mt+p*c['log_ell_t']+2*q*c['log_radius_t'])/(c['lapse']*d)
        delta = np.zeros_like(m)
        if hasattr(h,'actual_allocation'):
            actual_s, actual_sx = h.actual_allocation(ax)
            linear_s, linear_sx = h.allocation(ax)
            du = (actual_s-linear_s)[None,:]/c['radius']**4
            delta = d*du
            df = (actual_sx-linear_sx)[None,:]/(c['ell']*c['radius']**4)
            temporal += 4*c['v']/c['lapse']*du*c['log_radius_t']
            gradient += -df+4*du*(c['angular_gradient']-c['v']/c['lapse']*c['log_radius_t'])
            angular -= 4*du*c['angular_gradient']
            c['field_force'] += df
            c['fixed_force'] += df
        force = inertia+temporal+gradient+angular+c['fixed_force']
        power = power_s+c['fixed_power']
        proper = wt[begin:begin+24,None]*wx[None,:]*c['lapse']*d
        sums += [np.sum(proper*abs(force)),np.sum(proper*abs(power)),
                 np.sum(proper*(abs(inertia)+abs(temporal)+abs(gradient)+abs(angular)+
                    sum(abs(c[k]) for k in ('fluid_force','field_force','wave_force','heat_force')))),
                 np.sum(proper*(abs(power_s)+sum(abs(c[k]) for k in
                    ('fluid_power','field_power','wave_power','heat_power'))))]
        max_force = max(max_force,float(abs(force).max())); max_power = max(max_power,float(abs(power).max()))
        max_shortfall = max(max_shortfall,float(np.maximum(abs(p-delta)+np.maximum(-q-delta,2*(q+delta))-m-delta,0).max()))
        min_density = min(min_density,float(((m+delta)/d).min()))
    return dict(weighted_force_residual=float(sums[0]/sums[2]),weighted_power_residual=float(sums[1]/sums[3]),
                maximum_force_residual=max_force,maximum_power_residual=max_power,
                maximum_separate_member_shortfall_per_label=max_shortfall,minimum_support_density=min_density,
                audit_time_samples=len(at),audit_spatial_samples=len(ax))


def assemble_fixed(h,t,x,c):
    old = h.reference.h.state
    field = bilinear(old['t'],old['x'],old['flux_energy'],t,x)[0]
    share, unused = h.allocation(x)
    plus = bilinear(h.reference.t,h.reference.x,h.state['plus'],t,x)[0]
    minus = bilinear(h.reference.t,h.reference.x,h.state['minus'],t,x)[0]
    heat = bilinear(h.reference.t,h.reference.x,h.state['heat']+h.state['heat_cap']/3,t,x)[0]
    radial = (field+h.state['flux']-share)/c['radius']**4
    return radial_field_moments(radial)+wave_moments(plus,minus)+compact_cell_moments(heat,c), radial


def evaluate(spec):
    intervals,stride,fraction,allocation,cap,surface_width = spec
    h = JointHistory(32,8); old = h.reference.h.state
    if allocation == 'pchip':
        h.allocation = monotone_allocation(h.knots,h.share_values)
    if allocation == 'zero':
        h.allocation = lambda x:(np.zeros_like(x),np.zeros_like(x))
    indices = np.unique(np.r_[np.arange(0,len(h.reference.t),stride),len(h.reference.t)-1,
                              [i for i,unused,unused in h.reference.phases]])
    t = h.reference.t[indices]; x = np.linspace(h.knots[0],h.knots[-1],intervals+1)
    if allocation == 'linear_basis':
        actual_allocation = h.allocation
        samples = actual_allocation(x)[0]
        def linear_allocation(ax):
            j = np.clip(np.searchsorted(x,ax,side='right')-1,0,len(x)-2)
            slope = np.diff(samples)[j]/np.diff(x)[j]
            return samples[j]+slope*(ax-x[j]),slope
        h.allocation = linear_allocation
        h.actual_allocation = actual_allocation
    coefficients = lambda at,ax:fixed_coefficients(h,at,ax)
    c = coefficients(t,x)
    u = bilinear(old['t'],old['x'],old['thermal'],t,x)[0]
    number = np.interp(x,old['x'],old['number'])
    with np.load(BASE/'joint_component_cone/separate_members_scheduled_states.npz') as zz:
        reference = np.array([bilinear(zz['t'],zz['x'],zz[k],t,x)[0] for k in
                              ('support_energy','radial_volume','angular_volume')])
    reference[0] /= fraction
    H = bilinear(old['t'],old['x'],old['flux_energy'],t,x)[0]
    electric = (H-h.allocation(x)[0])/c['radius']**4
    result = solve_least_squares(t,x,coefficients,number,u,reference,fraction=fraction,material_cap=cap,
                                subpanels=max(1,128//intervals),deadline=300.,
                                surface_width=surface_width,electric=electric)
    label = f'n{intervals}_stride{stride}_fraction{fraction:g}_{allocation}_cap{cap:g}'
    if surface_width is not None: label += f'_jacket{surface_width:g}'
    summary = {k:v for k,v in result.items() if not isinstance(v,np.ndarray)}
    summary.update(label=label,intervals=intervals,time_stride=stride,fraction=fraction,allocation=allocation)
    checked_share = h.allocation(h.reference.check_x)[0]
    checked_electric = h.reference.check_h-checked_share
    summary['allocation_cap_violation'] = float(np.maximum(checked_share-np.minimum(h.state['flux'],h.reference.cap),0).max())
    summary['minimum_electric_retained_fraction'] = float((checked_electric/h.reference.check_h).min())
    summary['maximum_electric_average_rate'] = float(average_electric_rate(h.reference.t,checked_electric,h.reference.check_c['lapse']).max())
    summary['field_allocation_regularity'] = 'C1 shape-preserving cubic; no singular force layer'
    if summary['allocation_cap_violation']>1e-10 or summary['maximum_electric_average_rate']>1+1e-8:
        summary['success']=False
    if 'support_energy' in result:
        state = dict(t=t,x=x,thermal=u,**{k:result[k] for k in
                     ('support_energy','radial_volume','angular_volume','local_exchange')})
        summary.update(audit_schedule(h,state))
        if summary['maximum_separate_member_shortfall_per_label'] > 1e-5:
            summary['success'] = False
            summary['admissibility_message'] = 'enriched member-energy inequality failed'
        if surface_width is not None:
            state['surface_energy'] = result['surface_energy']
            state['surface_angular_stress'] = result['surface_angular_stress']
            summary['maximum_jacket_acceleration_thickness'] = float(np.max(abs(c['acceleration'][:,[0,-1]])*c['ell'][:,[0,-1]]*surface_width))
            summary['maximum_jacket_angular_thickness'] = float(np.max(abs(c['angular_gradient'][:,[0,-1]])*c['ell'][:,[0,-1]]*surface_width))
        fixed, radial = assemble_fixed(h,t,x,c)
        phases = []
        for original,time,demand in h.reference.phases:
            i = int(np.where(indices==original)[0][0])
            target = np.array([np.interp(x,h.reference.x,row) for row in demand])
            value,direction = maximum_null(result['tensor'][:,i]+fixed[:,i]-target)
            phases.append(dict(time=time,required_negative_null=float(value.max()),
                               peak_x=float(x[np.argmax(value)])))
        traction = (u/3+result['radial_volume'])/c['D']-radial
        end_force = 4*np.pi*c['radius'][:,[0,-1]]**2*traction[:,[0,-1]]*np.array([-1.,1.])
        end_power = c['alpha'][:,[0,-1]]*c['v'][:,[0,-1]]*end_force
        summary.update(phases=phases,initial_support_rest=float(4*np.pi*np.trapezoid(result['support_energy'][0],x)),
                       final_support_rest=float(4*np.pi*np.trapezoid(result['support_energy'][-1],x)),
                       gross_local_exchange=float(4*np.pi*np.trapezoid(abs(result['local_exchange']).sum(axis=0),x)),
                       end_connections=[dict(end=end,min_force=float(end_force[:,j].min()),max_force=float(end_force[:,j].max()),
                            signed_ADM_work_out=float(np.trapezoid(end_power[:,j],t)),peak_abs_ADM_power=float(abs(end_power[:,j]).max()))
                            for j,end in enumerate(('left','right'))],constitutive_law_supplied=False)
        state.update(end_force=end_force,end_power_out=end_power)
        np.savez_compressed(OUTPUT/(label+'_states.npz'),**state)
    write_json(OUTPUT/(label+'_summary.json'),summary)
    print(label+': '+json.dumps({k:v for k,v in summary.items() if k in
          ('success','message','material_peak_upper','weighted_force_residual','weighted_power_residual','phases')}),flush=True)
    return summary


def main():
    if OUTPUT.exists():
        raise RuntimeError('preserve completed spacetime-support evidence')
    previous = BASE/'joint_component_cone/manifest.json'
    hashes = json.loads(previous.read_text())['input_sha256']
    for p in (Path(__file__),previous,ROOT/'toolkit/adm_harness_cli/adm_harness/joint_support_gauss.py',
              ROOT/'toolkit/adm_harness_cli/adm_harness/joint_support_least_squares.py',
              ROOT/'toolkit/adm_harness_cli/adm_harness/monotone_field_allocation.py',
              BASE/'joint_component_cone/separate_members_scheduled_states.npz',
              ROOT/'toolkit/adm_harness_cli/requirements-joint-support.txt',
              ROOT/'toolkit/adm_harness_cli/scripts/run_joint_continuum_projection.py',
              ROOT/'toolkit/adm_harness_cli/scripts/audit_joint_support.py'):
        hashes[str(p.relative_to(ROOT))] = sha256_file(p)
    for p,expected in hashes.items():
        if sha256_file(ROOT/p) != expected:
            raise RuntimeError('changed spacetime support input: '+p)
    OUTPUT.mkdir()
    with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(evaluate,[(64,1,.9,'pchip',.2,None),(128,1,.9,'pchip',.2,None),
                                          (128,1,.9,'pchip',.4,None),(64,1,.9,'pchip',.4,.01)]))
    write_json(OUTPUT/'summary.json',dict(cases=results))
    write_json(OUTPUT/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes,output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
