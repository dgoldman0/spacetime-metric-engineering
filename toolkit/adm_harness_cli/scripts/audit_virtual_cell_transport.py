#!/usr/bin/env python3
"""Replay fixed coherent cell controls with independent explicit wave evolution."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

import numpy as np

from adm_harness.field_membrane_support import minimum_energy
from adm_harness.poynting_delivery import propagate
from adm_harness.source_ledger import sha256_file
from audit_joint_dense_work import DenseHistory
from run_poynting_delivery import BASE, ROOT, write_json


def interpolate_times(grid, values, now):
    index=int(np.clip(np.searchsorted(grid,now,side='right')-1,0,len(grid)-2))
    fraction=(now-grid[index])/(grid[index+1]-grid[index])
    return (1-fraction)*values[index]+fraction*values[index+1]


def audit(spec):
    source,label,factor,output=spec
    path=Path(source)/(label+'_states.npz')
    meta=json.loads(path.with_name(label+'_summary.json').read_text())
    if not meta['coherent_cell_amplitudes'] or not meta['heat_return']:
        raise ValueError('audit requires coherent cells with explicit heat return')
    with np.load(path) as z: s={k:z[k] for k in z.files}
    if min(s['positive_increment'].min(),s['negative_increment'].min()) < 0:
        raise ValueError('archived conversion source has a negative increment; no silent clipping is applied')
    h=DenseHistory('routed_family',ROOT/meta['input'])
    oldt,oldx=s['t'],s['x']; oldn=len(oldx)
    t=np.r_[(oldt[:-1,None]+np.diff(oldt)[:,None]*np.arange(factor)[None,:]/factor).ravel(),oldt[-1]]
    edges=np.linspace(s['edges'][0],s['edges'][-1],oldn*factor+1)
    x=(edges[:-1]+edges[1:])/2; nx=len(x); dx=edges[1]-edges[0]
    model=h.h.reference.h.model
    geom=[model.metric(float(now),x) for now in t]
    edgegeom=[model.metric(float(now),edges) for now in t]
    v=np.array([g.b*g.beta/g.alpha for g in geom]); gamma=1/np.sqrt(1-v*v)
    b=np.array([g.b for g in geom]); radius=np.array([g.radius for g in geom])
    tables={sign:dict(faces=np.array([-g.beta+sign*g.alpha/g.b for g in edgegeom]),
        gain=np.array([g.alpha*g.k_l-sign*g.alpha_x/g.b for g in geom]),
        source=b/(1-sign*v)) for sign in [-1,1]}
    eta=meta['efficiency']; all_states={}; ledgers=[]
    amplitude=np.empty((len(t),nx))
    for half in (0,1):
        sl=slice(half*(nx//2),(half+1)*(nx//2))
        so=slice(half*(oldn//2),(half+1)*(oldn//2))
        plus=np.array([np.interp(x[sl],oldx[so],row[so]) for row in s['positive_increment']])/np.diff(oldt)[:,None]
        minus=np.array([np.interp(x[sl],oldx[so],row[so]) for row in s['negative_increment']])/np.diff(oldt)[:,None]
        oldamp=s['amplitude'][:,so].mean(axis=1)
        amplitude[:,sl]=np.interp(t,oldt,oldamp)[:,None]
        direction=-1 if half==0 else 1
        for purpose,sign,rates,back in [('absorption',direction,plus/eta,True),
                ('work_return',-direction,eta*minus,False),
                ('heat_return',-direction,(1/eta-1)*plus+(1-eta)*minus,False)]:
            tab=tables[sign]
            faces=tab['faces'][:,half*(nx//2):(half+1)*(nx//2)+1]
            gain=tab['gain'][:,sl]; source_coeff=tab['source'][:,sl]
            def coefficients(now,interval):
                original=min(interval//factor,len(oldt)-2)
                return (interpolate_times(t,faces,now),interpolate_times(t,gain,now),
                        interpolate_times(t,source_coeff,now)*rates[original])
            result,ledger=propagate(t,edges[half*(nx//2):(half+1)*(nx//2)+1],coefficients,backwards=back)
            key=f'{purpose}_{half}'
            full=np.zeros((len(t),nx)); full[:,sl]=result
            all_states[key]=full
            for row in ledger: row['stream']=key
            ledgers.extend(ledger)
    volume=b*radius**2; direction=np.r_[-np.ones(nx//2),np.ones(nx//2)]
    absorption=sum(all_states[k] for k in all_states if k.startswith('absorption'))/volume*gamma**2*(1-direction*v)**2
    work=sum(all_states[k] for k in all_states if k.startswith('work_return'))/volume*gamma**2*(1+direction*v)**2
    heat=sum(all_states[k] for k in all_states if k.startswith('heat_return'))/volume*gamma**2*(1+direction*v)**2
    travelling=absorption+work+heat; current=direction*(absorption-work-heat)
    c=h.coefficients(t,x); rho=h.energy(x).evaluate(t)[0]/c['D']
    p=h.pressure(t,x)[0]; q=c['Q']/c['D']
    core=amplitude/radius**2
    wall=2*meta['interface_sigma']/(c['ell']*(edges[-1]-edges[0])/2)
    residual_p=p+core-travelling-abs(current); residual_q=q+wall
    drift=meta.get('guide_drift_bound')
    guide=0. if drift is None else .5*(drift**-2-1)
    extra_guide=np.maximum(guide*travelling-core/2,0.)
    auxiliary=np.maximum.reduce([residual_p+2*residual_q,
        residual_p-residual_q+3*extra_guide,-2*residual_p-residual_q])
    need=core+travelling+abs(current)+wall+auxiliary
    deficit=need-rho
    i,j=np.unravel_index(np.argmax(deficit),deficit.shape)
    result=dict(label=label,factor=factor,spatial_samples=nx,time_samples=len(t),
        independently_replayed_controls=True,activation_reoptimized=False,
        method='limited finite-volume SSP RK2, independent of the implicit optimization operator',
        target_budget_passes=bool(deficit.max()<=2e-7),
        maximum_density_shortfall=max(0.,float(deficit.max())),
        minimum_density_margin=float(-deficit.max()),
        worst_sample=dict(time=float(t[i]),x=float(x[j]),density=float(rho[i,j]),
            required_density=float(need[i,j]),core_density=float(core[i,j]),
            travelling_density=float(travelling[i,j]),countercurrent_density=float(abs(current[i,j])),
            wall_density=float(wall[i,j])),
        maximum_wave_balance_residual=float(max(abs(row['balance_residual']) for row in ledgers)),
        maximum_travelling_density=float(travelling.max()),
        maximum_travelling_heat_density=float(heat.max()),
        guide_drift_bound=drift,maximum_auxiliary_guide_floor=float(extra_guide.max()),
        simultaneous_conversion_increment=float(np.minimum(s['positive_increment'],s['negative_increment']).max()),
        phase_field_equations_solved=False,full_interface_and_guide_construction_supplied=False)
    stem=label+f'_factor{factor}'
    write_json(Path(output)/(stem+'_summary.json'),result)
    np.savez_compressed(Path(output)/(stem+'_states.npz'),t=t,x=x,amplitude=amplitude,
        absorption_rest=absorption,work_return_rest=work,heat_return_rest=heat,
        density=rho,radial_pressure=p,angular_pressure=q,density_shortfall=deficit,wall_rest=wall)
    print(stem+': pass='+str(result['target_budget_passes'])+
          ', margin='+str(result['minimum_density_margin']),flush=True)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',required=True)
    parser.add_argument('--labels',nargs='+',required=True)
    parser.add_argument('--factors',type=int,nargs='+',default=[2])
    parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--output-name',required=True)
    args=parser.parse_args(); source=BASE/args.source; output=BASE/args.output_name
    if output.exists(): raise RuntimeError('preserve completed independent replay')
    manifest=source/'manifest.json'; previous=json.loads(manifest.read_text())
    hashes=dict(previous['input_sha256'])
    for label in args.labels:
        for suffix in ['_states.npz','_summary.json']:
            path=source/(label+suffix)
            if sha256_file(path)!=previous['output_sha256'][path.name]: raise RuntimeError('changed controls')
            hashes[str(path.relative_to(ROOT))]=sha256_file(path)
    for path in [manifest,Path(__file__),ROOT/'toolkit/adm_harness_cli/adm_harness/poynting_delivery.py']:
        hashes[str(path.relative_to(ROOT))]=sha256_file(path)
    for relative,expected in hashes.items():
        if sha256_file(ROOT/relative)!=expected: raise RuntimeError('changed replay source: '+relative)
    output.mkdir()
    specs=[(str(source),label,factor,str(output)) for label in args.labels for factor in args.factors]
    with ProcessPoolExecutor(max_workers=max(1,min(args.workers,len(specs))),
                             mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(audit,specs))
    write_json(output/'summary.json',dict(cases=results))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes,output_sha256={p.name:sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__=='__main__': main()
