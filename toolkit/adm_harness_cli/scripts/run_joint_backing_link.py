#!/usr/bin/env python3
"""Parallel constitutive frame / pressure / warm-store inverse investigation."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

import numpy as np
import pandas as pd
from numpy.polynomial.legendre import leggauss

from adm_harness.active_transfer_reservoir import smooth_rise
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.joint_backing_link import FAMILIES,elastic_basis,solve_joint,passive_heat_capacity_interval
from adm_harness.poynting_delivery import wave_moments
from adm_harness.pressure_linked_storage import fluid_coefficients
from adm_harness.regenerative_converter import compact_cell_moments
from adm_harness.shared_field_delivery import radial_field_moments,smooth_under_cap
from adm_harness.source_ledger import sha256_file
from evaluate_finite_work_interface import InterfaceHistory
from evaluate_recovery_work_interface import recovery_state
from run_poynting_delivery import BASE,ROOT,write_json

OUTPUT=BASE/'joint_backing_link'


class JointHistory:
    def __init__(self,intervals,stride):
        reference=InterfaceHistory(1024);state=recovery_state(reference,1.)
        self.reference=reference;self.state=state
        self.indices=np.unique(np.r_[np.arange(0,len(reference.t),stride),len(reference.t)-1,
                                     [it for it,unused,unused in reference.phases]])
        self.t=reference.t[self.indices]
        self.x=np.linspace(reference.h.state['x'][0],reference.h.state['x'][-1],intervals+1)
        self.c=fluid_coefficients(reference.h.model,self.t,self.x)
        self.log_radius_t=np.array([reference.h.model.metric(float(t),self.x).logr_t for t in self.t])
        st=reference.h.state;knots=st['x'];self.knots=knots
        unused,unused,self.share_values=smooth_under_cap(reference.check_x,
            np.minimum(state['flux'],reference.cap),knots)
        self.thermal=self.interp(st['thermal'][self.indices],knots,self.x)
        self.number=np.interp(self.x,knots,st['number'])
        field=self.interp(st['flux_energy'][self.indices],knots,self.x)
        self.share,self.share_x=self.allocation(self.x)
        self.electric=(field-self.share)/self.c['radius']**4
        self.radial_field=(field+state['flux']-self.share)/self.c['radius']**4
        heat=self.interp(state['heat'][self.indices]+state['heat_cap']/3,reference.x,self.x)
        plus=self.interp(state['plus'][self.indices],reference.x,self.x)
        minus=self.interp(state['minus'][self.indices],reference.x,self.x)
        self.fixed=radial_field_moments(self.radial_field)+wave_moments(plus,minus)+compact_cell_moments(heat,self.c)
        self.phases=[]
        for old,time,demand in reference.phases:
            i=int(np.where(self.indices==old)[0][0])
            self.phases.append((i,time,self.interp(demand,reference.x,self.x)))
        # Integrate the required force across each control cell. Quadrature
        # panels follow all old allocation knots, avoiding aliasing their
        # zero derivatives at the knots themselves.
        z,w=leggauss(4);sub=max(1,128//intervals)
        fractions=(np.arange(sub)[:,None]+(z[None,:]+1)/2)/sub
        q=self.x[:-1,None,None]+np.diff(self.x)[:,None,None]*fractions[None,:,:]
        cq=fluid_coefficients(reference.h.model,self.t,q.ravel())
        force=self.required_force(q.ravel(),cq)
        weighted=(cq['gamma']*cq['b']*force).reshape(len(self.t),intervals,sub,4)
        self.force_rhs=np.sum(weighted*w[None,None,None,:]/(2*sub),axis=(2,3))

    @staticmethod
    def interp(array,old_x,new_x):
        return np.array([np.interp(new_x,old_x,row) for row in np.atleast_2d(array)])

    def allocation(self,x):
        j=np.clip(np.searchsorted(self.knots,x,side='right')-1,0,len(self.knots)-2)
        width=self.knots[j+1]-self.knots[j]
        rise,gradient=smooth_rise((x-self.knots[j])/width)
        delta=self.share_values[j+1]-self.share_values[j]
        return self.share_values[j]+delta*rise,delta*gradient/width

    def required_force(self,x,c):
        reference=self.reference;state=self.state
        intervals=np.clip(self.indices-1,0,len(reference.t)-2)
        hd=self.interp(reference.h.hdot[intervals],self.knots,x)
        charge=hd/(c['lapse']*c['radius']**4)
        wave=np.maximum(charge,0)/.98+.98*np.maximum(-charge,0)
        heat=self.interp(state['heat'][self.indices]+state['heat_cap']/3,reference.x,x)
        heat_force=heat/c['rest_volume']*c['acceleration']
        unused,derivative=self.allocation(x)
        field_force=derivative/(c['gamma']*c['b']*c['radius']**4)
        endpoint=c['gamma']*(c['normal_force']-c['v']*c['power'])
        return endpoint-wave-heat_force-field_force


def evaluate(spec):
    intervals,stride,delta,ends,frozen=spec
    h=JointHistory(intervals,stride)
    label=f'n{intervals}_stride{stride}_prestrain{delta:g}_{ends}'+('_fixedfluid' if frozen else '')
    result=solve_joint(h.t,h.x,h.c,h.log_radius_t,h.thermal,h.number,h.force_rhs,h.radial_field,
        prestrain_floor=delta,ends=ends,freeze_fluid=frozen,deadline=100.)
    summary={key:value for key,value in result.items() if not isinstance(value,np.ndarray)}
    summary.update(intervals=intervals,time_stride=stride,time_nodes=len(h.t),prestrain_floor=delta,
                   ends=ends,fluid_fixed=frozen,label=label)
    if result['success']:
        thermal,warm,prepared=(result[k] for k in ('thermal','warm','prepared'))
        basis=elastic_basis(h.c,h.log_radius_t)
        cold=np.sum(prepared[:,None,:]*basis['energy'],axis=0)
        radial=np.sum(prepared[:,None,:]*basis['radial'],axis=0)
        pressure=thermal/(3*h.c['rest_volume'])
        # Cold stress work is exactly the endpoint change of its stored energy.
        # The fluid's log-volume quadrature is the declared discrete energy law.
        fluid_work=-(thermal[1:]+thermal[:-1])/6*np.diff(np.log(h.c['rest_volume']),axis=0)
        old_work=-(h.thermal[1:]+h.thermal[:-1])/6*np.diff(np.log(h.c['rest_volume']),axis=0)
        internal_heat=np.diff(thermal-h.thermal,axis=0)-fluid_work+old_work
        identity=internal_heat+np.diff(warm,axis=0)
        integrate=lambda a:4*np.pi*np.trapezoid(a,h.x,axis=-1)
        heat=passive_heat_capacity_interval(h.t,thermal,warm)
        duty=np.sum(abs(heat['exchange']),axis=0)
        frac=float(np.sum(duty*heat['admissible'])/max(np.sum(duty),1e-30))
        traction=pressure+radial-h.radial_field
        summaries=[]
        for i,time,demand in h.phases:
            total=result['tensor'][:,i]+h.fixed[:,i]
            value,direction=maximum_null(total-demand);j=int(np.argmax(value))
            summaries.append(dict(time=time,required_negative_null=float(max(0.,value[j])),peak_x=float(h.x[j]),
                peak_null_cosine=float(direction[j]),material_ADM=float(integrate(h.c['b'][i]*h.c['radius'][i]**2*result['tensor'][0,i]))))
        summary.update(phases=summaries,initial_cold_rest=float(integrate(cold[0])),final_cold_rest=float(integrate(cold[-1])),
            initial_warm_rest=float(integrate(warm[0])),final_warm_rest=float(integrate(warm[-1])),
            initial_fluid_thermal=float(integrate(thermal[0])),final_fluid_thermal=float(integrate(thermal[-1])),
            internal_heat_gross=float(integrate(abs(internal_heat).sum(axis=0))),
            internal_heat_identity_residual=float(abs(identity).max()),
            heat_duty_with_compatible_constant_capacity_fraction=frac,
            maximum_left_traction=float(abs(traction[:,0]).max()),maximum_right_traction=float(abs(traction[:,-1]).max()),
            maximum_left_end_force=float(np.max(abs(traction[:,0])*4*np.pi*h.c['radius'][:,0]**2)),
            maximum_right_end_force=float(np.max(abs(traction[:,-1])*4*np.pi*h.c['radius'][:,-1]**2)),
            finite_charge_confinement_supplied=False,full_thermal_contact_law_supplied=False)
        np.savez_compressed(OUTPUT/(label+'_states.npz'),t=h.t,x=h.x,thermal=thermal,warm=warm,prepared=prepared,
            reference_thermal=h.thermal,force_rhs=h.force_rhs,traction=traction,internal_heat=internal_heat,
            capacity_lower=heat['lower'],capacity_upper=heat['upper'],capacity_admissible=heat['admissible'])
        pd.DataFrame(dict(x=h.x,**{name:prepared[i] for i,name in enumerate(FAMILIES)})).to_csv(OUTPUT/(label+'_prepared.csv'),index=False)
    write_json(OUTPUT/(label+'_summary.json'),summary)
    print(label+': '+('success' if result['success'] else result['message']),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    if OUTPUT.exists():
        raise RuntimeError('preserve completed joint backing evidence')
    preceding=BASE/'composite_capacitor_transport/manifest.json'
    hashes=json.loads(preceding.read_text())['input_sha256']
    for path in (Path(__file__),preceding,ROOT/'toolkit/adm_harness_cli/adm_harness/joint_backing_link.py',
                 ROOT/'toolkit/adm_harness_cli/tests/test_joint_backing_link.py'):
        hashes[str(path.relative_to(ROOT))]=sha256_file(path)
    for path,expected in hashes.items():
        if sha256_file(ROOT/path)!=expected:
            raise RuntimeError(f'changed joint input: {path}')
    OUTPUT.mkdir(parents=True)
    specs=[(32,8,delta,'exposed',False) for delta in (0.,.01,.1)]
    specs.extend([(32,8,.01,'balanced',False),(32,8,.01,'exposed',True)])
    with ProcessPoolExecutor(max_workers=min(4,args.workers),mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,specs))
    write_json(OUTPUT/'summary.json',dict(cases=results))
    write_json(OUTPUT/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),input_sha256=hashes,
        output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__=='__main__':
    main()
