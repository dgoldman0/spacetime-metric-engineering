#!/usr/bin/env python3
"""Final refined response-family check with complete constraint verification."""
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import multiprocessing
import subprocess
import time

import numpy as np
from scipy.sparse import csr_matrix, vstack

from adm_harness.composite_capacitor import anisotropic_moments
from adm_harness.cutting_plane_lp import solve_with_cuts
from adm_harness.field_membrane_support import minimum_energy
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.source_ledger import sha256_file
from adm_harness.time_support_projection import evolve_support
from audit_joint_support import bilinear
from run_joint_response_family import ResponseFamily, NPARAM
from run_joint_continuum_projection import fixed_coefficients
from run_joint_route_response import routed_coefficients
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'joint_refined_response'


def build_basis():
    f = ResponseFamily(256, 2); b = f.build_responses()
    def route(which):
        def coefficients(t,x):
            c=f.cached_coefficients(t,x,0); zero=np.zeros_like(c['fixed_force'])
            charge=c['field_power']
            force=-2*(np.maximum(charge,0)/.98 if which==0 else .98*np.maximum(-charge,0))
            c.update(Q=zero,fixed_force=force,fixed_power=zero)
            return c
        return evolve_support(f.t,f.x,coefficients,np.zeros(len(f.x)),np.zeros(len(f.t)),np.zeros(len(f.x)))
    with ThreadPoolExecutor(max_workers=2) as pool: responses=list(pool.map(route,(0,1)))
    for key,source in (('energy','support_energy'),('pressure','radial_pressure')):
        b[key]=np.concatenate([b[key],np.stack([r[source] for r in responses],axis=-1)],axis=-1)
    b['angular']=np.concatenate([b['angular'],np.zeros((*b['angular'].shape[:2],2))],axis=-1)
    np.savez_compressed(OUTPUT/'responses.npz',**b)
    print('refined conservative response basis complete',flush=True)


def evaluate(spec):
    fraction,components=spec;start=time.monotonic();f=ResponseFamily(256,2);h=f.h
    with np.load(OUTPUT/'responses.npz') as z:b={k:z[k] for k in z.files}
    t,x=b['t'],b['x'];c=fixed_coefficients(h,t,x)
    old=h.reference.h.state
    u=bilinear(old['t'],old['x'],old['thermal'],t,x)[0];n=np.interp(x,old['x'],old['number'])
    m=b['energy']/c['D'][:,:,None];p=b['pressure'];q=b['angular']/c['D'][:,:,None]
    dim=m.shape[-1]-1;arrays=[];rhs=[]
    def add(value,peak=0.):
        flat=value.reshape(-1,dim+1)
        arrays.append(csr_matrix(np.c_[flat[:,1:],np.full(len(flat),peak)]));rhs.append(-flat[:,0])
    if components=='field_membrane':
        pairs=((1.,2.),(1.,-1.),(-2.,-1.))
    else:pairs=tuple((r,a) for r in (-1.,1.) for a in (-1.,2.))
    for radial,angular in pairs:add(radial*p+angular*q-fraction*m)
    for z in np.linspace(-1,1,7):
        rr=c['gamma']**2*(1-c['v']*z)**2;pr=c['gamma']**2*(c['v']-z)**2
        value=rr[:,:,None]*m+pr[:,:,None]*p+(1-z*z)*q
        value[...,0]+=(n+u)/c['D']*rr+u/(3*c['D'])*(pr+1-z*z)
        add(value,-1.)
    matrix=vstack(arrays,format='csr');vector=np.concatenate(rhs);del arrays,rhs
    objective=np.zeros(dim+1);objective[-1]=1.
    result=solve_with_cuts(objective,matrix,vector,
        [(None,None)]*NPARAM+[(0.,1.)]*2+[(0.,None)],deadline=180.)
    label=f'{components}_fraction{fraction:g}'
    summary=dict(label=label,fraction=fraction,components=components,success=bool(result.success),
        status=int(result.status),message=result.message,cut_history=result.cut_history,
        total_constraints=result.total_rows,intervals=len(x)-1,time_nodes=len(t),
        physical_material_law_supplied=False,end_connections_supplied=False,
        changed_route_stress_counted=False,continuum_validated=False)
    if result.success:
        weights=np.r_[1.,result.x[:-1]];rho=m@weights;radial=p@weights;angular=q@weights
        tensor=anisotropic_moments((n+u)/c['D']+rho,u/(3*c['D'])+radial,u/(3*c['D'])+angular,c['v'])
        upper=float(maximum_null(tensor)[0].max())
        checked=result.x.copy();checked[-1]=max(upper,checked[-1])
        violation=float(np.maximum(matrix@checked-vector,0).max())
        floor=minimum_energy(radial,angular) if components=='field_membrane' else abs(radial)+np.maximum(-angular,2*angular)
        summary.update(material_peak_upper=upper,material_peak_sampled_lower=float(result.fun),
            maximum_original_inequality_violation=violation,
            maximum_node_member_density_shortfall=float(np.maximum(floor-rho,0).max()),
            initial_support_rest=float(4*np.pi*np.trapezoid(rho[0]*c['D'][0],x)),
            final_support_rest=float(4*np.pi*np.trapezoid(rho[-1]*c['D'][-1],x)),
            absorption_left_feed_fraction=float(result.x[NPARAM]),
            recovery_left_emission_fraction=float(result.x[NPARAM+1]),parameters=result.x[:-1].tolist())
        if violation>2e-7:summary['success']=False
        np.savez_compressed(OUTPUT/(label+'_states.npz'),t=t,x=x,support_energy=rho*c['D'],
            radial_pressure=radial,radial_volume=radial*c['D'],angular_volume=angular*c['D'],
            local_exchange=b['local_exchange'],parameters=result.x[:-1])
    summary['elapsed_seconds']=time.monotonic()-start
    write_json(OUTPUT/(label+'_summary.json'),summary)
    print(label+': '+json.dumps(summary),flush=True)
    return summary


def main():
    if OUTPUT.exists():raise RuntimeError('preserve completed refined response evidence')
    previous=BASE/'joint_route_response/manifest.json'
    hashes=json.loads(previous.read_text())['input_sha256']
    for p in (Path(__file__),previous,Path(__file__).with_name('run_joint_route_response.py'),
              Path(__file__).with_name('audit_joint_dense_work.py'),
              ROOT/'toolkit/adm_harness_cli/adm_harness/cutting_plane_lp.py',
              ROOT/'toolkit/adm_harness_cli/adm_harness/field_membrane_support.py',
              ROOT/'toolkit/adm_harness_cli/adm_harness/integrated_support_energy.py',
              ROOT/'toolkit/adm_harness_cli/adm_harness/conserved_radial_prestress.py'):
        hashes[str(p.relative_to(ROOT))]=sha256_file(p)
    for p,expected in hashes.items():
        if sha256_file(ROOT/p)!=expected:raise RuntimeError('changed refined-family input: '+p)
    OUTPUT.mkdir();build_basis()
    specs=[(.9,'members'),(.99,'members'),(1.,'members'),(1.,'field_membrane')]
    with ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,specs))
    accepted=[r for r in results if r['success']]
    audit=None
    if accepted:
        chosen=min(accepted,key=lambda r:(r['components']!='field_membrane',r['fraction']))
        import audit_joint_dense_work as dense
        dense.OUTPUT=OUTPUT
        audit=dense.evaluate(('routed_family','joint_refined_response/'+chosen['label']+'_states.npz'))
    write_json(OUTPUT/'summary.json',dict(cases=results,selected_dense_work_audit=audit))
    write_json(OUTPUT/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes,output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__=='__main__':main()
