#!/usr/bin/env python3
"""Rebuild waves and whole-panel bounds from reconstructed phase controls."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess
import numpy as np

from adm_harness.source_ledger import sha256_file
from adm_harness.virtual_cell_transport import upwind_operator
from adm_harness.virtual_cell_semigroup import transport_map
from adm_harness.virtual_cell_envelope_audit import least_upwind_supersolution
from audit_joint_dense_work import DenseHistory
from run_poynting_delivery import BASE,ROOT,write_json


def audit(item):
    path,output=item; path=Path(path)
    meta=json.loads(path.with_name(path.name.replace('_states.npz','_summary.json')).read_text())
    with np.load(path) as data: z={k:data[k] for k in data.files}
    t,x,edges=z['t'],z['x'],z['edges']; nt,nx=len(t),len(x); half=nx//2; dx=edges[1]-edges[0]
    tm=(t[:-1]+t[1:])/2; eta=meta['efficiency']; model_history=DenseHistory('routed_family',ROOT/meta['input'])
    mids=model_history.coefficients(tm,x); model=model_history.h.reference.h.model
    gm=[model.metric(float(now),x) for now in tm]
    ge=[model.metric(float(now),edges) for now in tm]
    wave={sign:dict(faces=np.array([-g.beta+sign*g.alpha/g.b for g in ge]),
        gain=np.array([g.alpha*g.k_l-sign*g.alpha_x/g.b for g in gm])) for sign in [-1,1]}
    states={}; ceilings={}; max_residual=0.
    for back in [True,False]:
        y=np.zeros((nt,nx)); ceiling=np.zeros((nt-1,nx))
        for i in (range(nt-2,-1,-1) if back else range(nt-1)):
            dt=t[i+1]-t[i]
            for region in (0,1):
                start=region*half; stop=start+half; sl=slice(start,stop)
                sign=(-1 if region==0 else 1)*(1 if back else -1)
                faces=wave[sign]['faces'][i,start:stop+1]; gain=wave[sign]['gain'][i,sl]
                coefficient=mids['b'][i,sl]/(1-sign*mids['v'][i,sl])
                increment=(z['positive_increment'][i,sl]/eta if back else
                    z['negative_increment'][i,sl]+(1/eta-1)*z['positive_increment'][i,sl])
                matrix,response=transport_map(dt,faces,gain,coefficient,dx,back)
                at,other=(i,i+1) if back else (i+1,i)
                # The coherent control has the same increment at every point
                # of its cell, as required by the source response above.
                if np.ptp(increment)>1e-14: raise ValueError('control has lost cell coherence')
                y[at,sl]=matrix@y[other,sl]+response*increment[0]
                generator=upwind_operator(-faces if back else faces,dx)+np.diag(-gain if back else gain)
                source_rate=coefficient*increment/dt
                ceiling[i,sl]=least_upwind_supersolution(generator,source_rate,y[other,sl])
                max_residual=max(max_residual,float(np.max(generator@ceiling[i,sl]+source_rate)))
        states[back]=y; ceilings[back]=ceiling
    # The wave ceiling holds continuously for frozen-panel transport. Resolve
    # the actual target/boost variation at five points through every panel.
    fine_t=np.r_[(t[:-1,None]+np.diff(t)[:,None]*np.arange(4)[None,:]/4).ravel(),t[-1]]
    coeff=model_history.coefficients(fine_t,x)
    density=model_history.energy(x).evaluate(fine_t)[0]/coeff['D']
    pressure=model_history.pressure(fine_t,x)[0]; angular=coeff['Q']/coeff['D']
    direction=np.r_[-np.ones(half),np.ones(half)]
    ua_factor=coeff['gamma']**2*(1-direction*coeff['v'])**2/(coeff['b']*coeff['radius']**2)
    ur_factor=coeff['gamma']**2*(1+direction*coeff['v'])**2/(coeff['b']*coeff['radius']**2)
    amplitude=np.array([np.interp(fine_t,t,z['amplitude'][:,j]) for j in range(nx)]).T
    core=amplitude/coeff['radius']**2
    wall=2*meta['interface_sigma']/(coeff['ell']*(edges[-1]-edges[0])/2)
    guide=.5*(meta['guide_drift_bound']**-2-1)
    worst=-np.inf; witness=None
    for i in range(nt-1):
        sl=slice(4*i,4*i+5)
        ua=ua_factor[sl]*ceilings[True][i]; ur=ur_factor[sl]*ceilings[False][i]
        s=core[sl]; rho,p,q=density[sl],pressure[sl],angular[sl]
        shortage=np.maximum.reduce([p+2*q+2*s+3*wall[sl],p-q+2*s,
            -2*p-q-s+6*ua,-2*p-q-s+6*ur,p-q+.5*s+3*guide*(ua+ur)])-rho
        if shortage.max()>worst:
            row,col=np.unravel_index(shortage.argmax(),shortage.shape); worst=float(shortage[row,col])
            witness=dict(time=float(fine_t[4*i+row]),x=float(x[col]),density=float(rho[row,col]))
    result=dict(label=meta['label'],minimum_density_margin=-worst,target_budget_passes=bool(worst<=2e-7),
        supersolution_maximum_inequality_residual=max_residual,worst_sample=witness,
        source_controls_reconstructed=True,activation_reoptimized=False,
        wave_bound='continuous in time for frozen-panel finite-volume transport',
        geometry_target_samples_per_panel=5,variable_geometry_explicit_replay_required=True)
    label=meta['label']; write_json(Path(output)/(label+'_summary.json'),result)
    np.savez_compressed(Path(output)/(label+'_states.npz'),t=t,x=x,
        absorption_state=states[True],recovery_state=states[False],
        absorption_ceiling=ceilings[True],recovery_ceiling=ceilings[False])
    print(label+': margin='+str(-worst),flush=True)
    return result


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--source',default='virtual_cell_reconstructed_controls')
    parser.add_argument('--output-name',default='virtual_cell_reconstructed_envelopes')
    args=parser.parse_args(); source=BASE/args.source; output=BASE/args.output_name
    if output.exists(): raise RuntimeError('preserve reconstructed envelope evidence')
    manifest=source/'manifest.json'; previous=json.loads(manifest.read_text()); hashes=dict(previous['input_sha256'])
    for p in [manifest,Path(__file__),ROOT/'toolkit/adm_harness_cli/adm_harness/virtual_cell_envelope_audit.py',
              ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_envelope_audit.py']:
        hashes[str(p.relative_to(ROOT))]=sha256_file(p)
    specs=[]
    for path in sorted(source.glob('*_states.npz')):
        for p in [path,path.with_name(path.name.replace('_states.npz','_summary.json'))]:
            if sha256_file(p)!=previous['output_sha256'][p.name]: raise RuntimeError('changed reconstructed controls')
            hashes[str(p.relative_to(ROOT))]=sha256_file(p)
        specs.append((str(path),str(output)))
    for relative,expected in hashes.items():
        if sha256_file(ROOT/relative)!=expected: raise RuntimeError('changed dependency: '+relative)
    output.mkdir()
    with ProcessPoolExecutor(max_workers=max(1,min(args.workers,len(specs))),
                             mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(audit,specs))
    write_json(output/'summary.json',dict(cases=results))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes,output_sha256={p.name:sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__=='__main__': main()
