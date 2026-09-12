#!/usr/bin/env python3
"""Test an explicit electromagnetic, radiation, and membrane support basis."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import multiprocessing
import subprocess
import time

import numpy as np
from scipy.sparse import csr_matrix, vstack

from adm_harness.field_membrane_support import minimum_energy
from adm_harness.pressure_linked_storage import retained_coefficient_program
from adm_harness.source_ledger import sha256_file
from audit_joint_support import bilinear
from run_joint_response_family import ResponseFamily, NPARAM
from run_joint_continuum_projection import fixed_coefficients
from run_joint_route_response import routed_coefficients
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'joint_field_membrane_gate'
BASIS = BASE/'joint_route_response/responses.npz'


def evaluate(route):
    start=time.monotonic(); f=ResponseFamily();h=f.h
    with np.load(BASIS) as z:b={k:z[k] for k in z.files}
    t,x=b['t'],b['x'];c=fixed_coefficients(h,t,x)
    old=h.reference.h.state
    u=bilinear(old['t'],old['x'],old['thermal'],t,x)[0]
    n=np.interp(x,old['x'],old['number'])
    m=b['energy']/c['D'][:,:,None];p=b['pressure'];q=b['angular']/c['D'][:,:,None]
    dim=m.shape[-1]-1;arrays=[];rhs=[]
    def add(value,peak=0.):
        flat=value.reshape(-1,dim+1)
        arrays.append(csr_matrix(np.c_[flat[:,1:],np.full(len(flat),peak)]));rhs.append(-flat[:,0])
    for sr,sq in ((1.,2.),(1.,-1.),(-2.,-1.)):add(sr*p+sq*q-m)
    for z in np.linspace(-1,1,7):
        rr=c['gamma']**2*(1-c['v']*z)**2;pr=c['gamma']**2*(c['v']-z)**2
        value=rr[:,:,None]*m+pr[:,:,None]*p+(1-z*z)*q
        value[...,0]+=(n+u)/c['D']*rr+u/(3*c['D'])*(pr+1-z*z)
        add(value,-1.)
    matrix=vstack(arrays,format='csr');vector=np.concatenate(rhs)
    cost=np.zeros(dim+1);cost[-1]=1.
    result=retained_coefficient_program(cost,method='highs-ipm',deadline=150.,
        A_ub=matrix,b_ub=vector,
        bounds=[(None,None)]*NPARAM+([(0.,1.)]*2 if route else [(0.,0.)]*2)+[(0.,None)])
    label='variable_route' if route else 'original_route'
    summary=dict(label=label,success=bool(result.success),status=int(result.status),message=result.message,
        components=['radial Maxwell field','balanced radial radiation','angular radiation',
                    'angular tensile membrane','rest inventory'],
        control_amplitude_bounds=None,route_fraction_bounds=[0.,1.] if route else [0.,0.],
        currents_material_response_and_end_connections_supplied=False)
    if result.success:
        from types import SimpleNamespace
        from adm_harness.composite_capacitor import anisotropic_moments
        from adm_harness.graded_electrothermal import maximum_null
        from run_joint_time_projected_candidate import audit_projection
        weights=np.r_[1.,result.x[:-1]];rho=m@weights;pr=p@weights;pt=q@weights
        tensor=anisotropic_moments((n+u)/c['D']+rho,u/(3*c['D'])+pr,u/(3*c['D'])+pt,c['v'])
        upper=float(maximum_null(tensor)[0].max())
        checked=result.x.copy();checked[-1]=max(upper,checked[-1])
        violation=float(np.maximum(matrix@checked-vector,0).max())
        state=dict(t=t,x=x,support_energy=rho*c['D'],radial_pressure=pr,radial_volume=pr*c['D'],
            angular_volume=pt*c['D'],parameters=result.x[:-1],local_exchange=b['local_exchange'])
        proxy=SimpleNamespace(h=h,coefficients=lambda at,ax:routed_coefficients(f,result.x[:-1],at,ax))
        summary.update(audit_projection(proxy,state),material_peak_upper=upper,
            maximum_original_inequality_violation=violation,parameters=result.x[:-1].tolist(),
            maximum_component_density_shortfall=float(np.maximum(minimum_energy(pr,pt)-rho,0).max()))
        if violation>2e-7:summary['success']=False
        np.savez_compressed(OUTPUT/(label+'_states.npz'),**state)
    summary['elapsed_seconds']=time.monotonic()-start
    write_json(OUTPUT/(label+'_summary.json'),summary)
    print(label+': '+json.dumps(summary),flush=True)
    return summary


def current_candidates():
    from audit_joint_dense_work import DenseHistory
    rows=[]
    for kind,relative in [('family','joint_response_relaxation/fraction1_unbounded_states.npz'),
                          ('routed_family','joint_route_response/fraction0.99_states.npz')]:
        history=DenseHistory(kind,BASE/relative);s=history.state;t=s['t'];x=s['x']
        c=history.coefficients(t,x);m=history.energy(x).evaluate(t)[0]
        rho=m/c['D'];p=s['radial_pressure'];q=c['Q']/c['D']
        weight=m*np.gradient(t)[:,None]*np.gradient(x)[None,:]
        shortfall=minimum_energy(p,q)-rho
        rows.append(dict(input=relative,energy_reconstructed_from_work=True,
            maximum_density_shortfall=float(shortfall.max()),
            energy_weighted_deficient_fraction=float(weight[shortfall>1e-7].sum()/weight.sum()),
            energy_weighted_radial_tension_fraction=float(weight[p<0].sum()/weight.sum()),
            energy_weighted_tension_above_90_percent_fraction=float(weight[p<-.9*rho].sum()/weight.sum()),
            radial_pressure_density_ratio_range=[float((p/rho).min()),float((p/rho).max())]))
    return rows


def main():
    if OUTPUT.exists():raise RuntimeError('preserve completed field/membrane evidence')
    previous=BASE/'joint_route_response/manifest.json'
    hashes=json.loads(previous.read_text())['input_sha256']
    sources=[Path(__file__),previous,BASIS,
        ROOT/'toolkit/adm_harness_cli/adm_harness/field_membrane_support.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/integrated_support_energy.py',
        Path(__file__).with_name('audit_joint_dense_work.py'),
        Path(__file__).with_name('run_joint_route_response.py'),
        BASE/'joint_response_relaxation/fraction1_unbounded_states.npz',
        BASE/'joint_route_response/fraction0.99_states.npz']
    for p in sources:hashes[str(p.relative_to(ROOT))]=sha256_file(p)
    for p,expected in hashes.items():
        if sha256_file(ROOT/p)!=expected:raise RuntimeError('changed field/membrane input: '+p)
    OUTPUT.mkdir()
    with ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,(False,True)))
    write_json(OUTPUT/'summary.json',dict(cases=results,current_candidate_composition=current_candidates()))
    write_json(OUTPUT/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes,output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__=='__main__':main()
