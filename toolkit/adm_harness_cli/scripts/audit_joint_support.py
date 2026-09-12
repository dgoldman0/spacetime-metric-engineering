#!/usr/bin/env python3
"""Independent continuum residuals and mechanical end-work audit."""
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

from adm_harness.pressure_linked_storage import fluid_coefficients
from adm_harness.source_ledger import sha256_file
from run_joint_backing_link import JointHistory
from run_poynting_delivery import BASE,ROOT,write_json

OUTPUT=BASE/'joint_support_audit'


def bilinear(t,x,z,at,ax):
    """Values and analytic derivatives inside piecewise bilinear panels."""
    i=np.clip(np.searchsorted(t,at,side='right')-1,0,len(t)-2)
    j=np.clip(np.searchsorted(x,ax,side='right')-1,0,len(x)-2)
    dt=t[i+1]-t[i];dx=x[j+1]-x[j]
    a=(at-t[i])/dt;b=(ax-x[j])/dx
    ll=z[i[:,None],j[None,:]];lr=z[i[:,None],j[None,:]+1]
    ul=z[i[:,None]+1,j[None,:]];ur=z[i[:,None]+1,j[None,:]+1]
    left=(1-a[:,None])*ll+a[:,None]*ul
    right=(1-a[:,None])*lr+a[:,None]*ur
    value=(1-b[None,:])*left+b[None,:]*right
    temporal=((1-b[None,:])*(ul-ll)+b[None,:]*(ur-lr))/dt[:,None]
    spatial=(right-left)/dx[None,:]
    return value,temporal,spatial


def continuum_check(h,state,*,preserve_reference_fluid=False):
    t,x=state['t'],state['x'];at=(t[:-1]+t[1:])/2
    # Four quadrature nodes inside every original allocation panel also
    # sample all microstructure that the coarse support grid averages over.
    z,w=leggauss(4);edges=h.knots
    ax=(edges[:-1,None]+np.diff(edges)[:,None]*(z[None,:]+1)/2).ravel()
    c=fluid_coefficients(h.reference.h.model,at,ax)
    metric=[h.reference.h.model.metric(float(time),ax) for time in at]
    lr=np.array([g.logr_t for g in metric]);le=c['volume_rate']-2*lr
    vx=np.array([c['v'][i]*(g.logb_x-g.alpha_x/g.alpha)+g.b*g.beta_x/g.alpha
                 for i,g in enumerate(metric)])
    volume_x=np.array([g.logb_x+2*g.logr_x for g in metric])+c['gamma']**2*c['v']*vx
    old=h.reference.h.state
    if preserve_reference_fluid:
        # The fixed-fluid control retains the full archived fluid. Only the
        # NEW support coefficients live on the smaller inverse grid.
        u,ut,ux=bilinear(old['t'],old['x'],old['thermal'],at,ax)
    else:
        u,ut,ux=bilinear(t,x,state['thermal'],at,ax)
    m,mt,mx=bilinear(t,x,state['support_energy'],at,ax)
    pr,prt,prx=bilinear(t,x,state['radial_volume'],at,ax)
    pt,unused,unused=bilinear(t,x,state['angular_volume'],at,ax)
    vol=c['rest_volume'];ell=c['gamma']*c['b'];lapse=c['lapse'];radius=c['radius']
    number=np.interp(ax,h.reference.h.state['x'],h.reference.h.state['number'])
    radial=(u/3+pr)/vol
    radial_t=(ut/3+prt-c['volume_rate']*(u/3+pr))/vol
    radial_x=(ux/3+prx-volume_x*(u/3+pr))/vol
    inertia=(number+4*u/3+m+pr)/vol*c['acceleration']
    gradient=c['v']/lapse*radial_t+radial_x/ell
    angular=2*(pr-pt)/vol*c['angular_gradient']
    material_force=inertia+gradient+angular
    material_power=(ut+mt+u/3*c['volume_rate']+pr*le+2*pt*lr)/(lapse*vol)
    field,field_t,field_x=bilinear(old['t'],old['x'],old['flux_energy'],at,ax)
    share,share_x=h.allocation(ax)
    field_force=-(field_x-share_x)/(ell*radius**4)
    charge=field_t/(lapse*radius**4)
    wave_force=np.maximum(charge,0)/.98+.98*np.maximum(-charge,0)
    wave_power=-np.maximum(charge,0)/.98+.98*np.maximum(-charge,0)
    receiver,receiver_t,unused=bilinear(h.reference.t,h.reference.x,
        h.state['heat']+h.state['heat_cap']/3,at,ax)
    receiver_force=receiver/vol*c['acceleration']
    receiver_power=receiver_t/(lapse*vol)
    force=material_force+field_force+wave_force+receiver_force
    power=material_power+charge+wave_power+receiver_power
    weights=(np.diff(edges)[:,None]*w[None,:]/2).ravel()
    duration=np.diff(t)
    proper=duration[:,None]*lapse*vol*weights[None,:]
    rel=lambda a,parts:float(np.sum(proper*abs(a))/max(np.sum(proper*sum(abs(p) for p in parts)),1e-30))
    sub=(len(edges)-1)//(len(x)-1)
    cellavg=lambda a: np.sum((ell*a).reshape(len(at),len(x)-1,sub,4)*w[None,None,None,:]/(2*sub),axis=(2,3))
    fa=cellavg(force);scale=np.sum([abs(cellavg(a)) for a in (inertia,gradient,angular,field_force,wave_force,receiver_force)],axis=0)
    # Equilibrated subcell reconstruction: a known, time-independent flux
    # difference has zero material-frame power and vanishes at support nodes.
    # It changes the TARGET material tensor by (du,-du,0,du), with positivity
    # and DEC checked on the corrected total support below. No extra field
    # hardware is inferred from this mathematical tensor reconstruction.
    coarse_share,unused=h.allocation(x)
    share_table=np.broadcast_to(coarse_share,(len(t),len(x)))
    linear_share,unused,linear_share_x=bilinear(t,x,share_table,at,ax)
    delta_u=(share[None,:]-linear_share)/radius**4
    lift_force=-(share_x[None,:]-linear_share_x)/(ell*radius**4)
    lifted_force=force+lift_force
    lifted_density=m/vol+delta_u
    lifted_radial=pr/vol-delta_u;lifted_angular=pt/vol+delta_u
    violation=np.maximum(np.maximum(abs(lifted_radial),abs(lifted_angular))-lifted_density,0.)
    return dict(pointwise_force_max=float(abs(force).max()),pointwise_power_max=float(abs(power).max()),
        force_sum_relative_residual=rel(force,(inertia,gradient,angular,field_force,wave_force,receiver_force)),
        power_sum_relative_residual=rel(power,(material_power,charge,wave_power,receiver_power)),
        cell_force_sum_relative_residual=float(np.sum(abs(fa))/max(np.sum(scale),1e-30)),
        max_cell_average_ell_force_residual=float(abs(fa).max()),sampled_times=len(at),sampled_positions=len(ax),
        preserved_full_reference_fluid=preserve_reference_fluid,
        allocation_lift_force_max=float(abs(lifted_force).max()),
        allocation_lift_force_sum_relative_residual=rel(lifted_force,(inertia,gradient+lift_force,angular,field_force,wave_force,receiver_force)),
        allocation_lift_max_DEC_violation=float(violation.max()),
        allocation_lift_min_density=float(lifted_density.min()),
        allocation_lift_max_abs_density_change=float(abs(delta_u).max()),
        t=at,x=ax,force=force,power=power,cell_force=fa,lifted_force=lifted_force)


def evaluate(path):
    path=Path(path);summary=json.loads(path.read_text())
    if path.parent.name=='joint_component_cone':
        summary=dict(intervals=32,time_stride=8,fluid_fixed=True,**summary)
    h=JointHistory(summary['intervals'],summary['time_stride'])
    statepath=path.with_name(summary['label']+'_states.npz')
    with np.load(statepath) as z:
        state={k:z[k] for k in z.files}
    audit=continuum_check(h,state,preserve_reference_fluid=summary['fluid_fixed'])
    scalars={key:value for key,value in audit.items() if not isinstance(value,np.ndarray)}
    t,x=state['t'],state['x'];radius=h.c['radius']
    traction=state.get('traction',(state['thermal']/3+state['radial_volume'])/h.c['rest_volume']-h.radial_field)
    # Outward ADM energy flux through coordinate-fixed material cuts:
    # alpha R^2 v p_r dOmega. Work waves have their separate transport ledger.
    outward=4*np.pi*h.c['alpha'][:,[0,-1]]*h.c['v'][:,[0,-1]]*radius[:,[0,-1]]**2*traction[:,[0,-1]]*np.array([-1.,1.])
    endforce=4*np.pi*radius[:,[0,-1]]**2*traction[:,[0,-1]]*np.array([-1.,1.])
    rows=[]
    for j,end in enumerate(('left','right')):
        rows.append(dict(end=end,signed_work_out=float(np.trapezoid(outward[:,j],t)),
            gross_work_out=float(np.trapezoid(np.maximum(outward[:,j],0),t)),
            gross_work_in=float(np.trapezoid(np.maximum(-outward[:,j],0),t)),
            max_abs_power=float(abs(outward[:,j]).max()),min_signed_force=float(endforce[:,j].min()),
            max_signed_force=float(endforce[:,j].max())))
    ell=h.c['gamma']*h.c['b'];axial=state['radial_volume']/ell
    dl=np.diff(np.log(ell),axis=0);df=np.diff(axial,axis=0)
    # Positive df*dl means tensile force strengthens under compression (or
    # the converse), requiring a coupled/internal-state response in an axial
    # member with otherwise positive incremental stiffness.
    activity=abs(df);reverse=df*dl>1e-10
    fraction=float(np.sum(activity*reverse)/max(np.sum(activity),1e-30))
    density=state['support_energy']/h.c['rest_volume']
    pr=state['radial_volume']/h.c['rest_volume'];pt=state['angular_volume']/h.c['rest_volume']
    separate_floor=abs(state['radial_volume'])+np.maximum(-state['angular_volume'],2*state['angular_volume'])
    shortfall=np.maximum(separate_floor-state['support_energy'],0.)
    scalars.update(label=summary['label'],source_directory=path.parent.name,end_connections=rows,
        axial_force_change_fraction_opposing_uncoupled_positive_stiffness=fraction,
        minimum_support_density=float(density.min()),minimum_radial_pressure=float(pr.min()),
        maximum_radial_pressure=float(pr.max()),minimum_angular_pressure=float(pt.min()),
        maximum_angular_pressure=float(pt.max()),
        max_separate_member_energy_shortfall_per_label=float(shortfall.max()),
        energy_weighted_node_fraction_with_separate_member_shortfall=float(
            np.sum(state['support_energy']*(shortfall>1e-7))/max(np.sum(state['support_energy']),1e-30)))
    label=path.parent.name+'_'+summary['label']
    write_json(OUTPUT/(label+'_audit.json'),scalars)
    np.savez_compressed(OUTPUT/(label+'_residuals.npz'),**{k:v for k,v in audit.items() if isinstance(v,np.ndarray)})
    pd.DataFrame(dict(t=t,left_force=endforce[:,0],right_force=endforce[:,1],
        left_power_out=outward[:,0],right_power_out=outward[:,1])).to_csv(OUTPUT/(label+'_ends.csv'),index=False)
    print(label+': cell force residual '+str(scalars['cell_force_sum_relative_residual']),flush=True)
    return scalars


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    if OUTPUT.exists():
        raise RuntimeError('preserve completed joint support audit')
    dirs=[BASE/name for name in ('joint_backing_link','joint_backing_link_continuation',
        'joint_support_envelope','joint_support_envelope_refinement','joint_component_cone')]
    checks=[];inputs={}
    for directory in dirs:
        manifest=directory/'manifest.json';m=json.loads(manifest.read_text())
        inputs[str(manifest.relative_to(ROOT))]=sha256_file(manifest)
        for mapping,base in ((m['input_sha256'],ROOT),(m['output_sha256'],directory)):
            for name,expected in mapping.items():
                actual=sha256_file(base/name);valid=actual==expected
                checks.append(dict(path=str((base/name).relative_to(ROOT)),valid=valid))
                if not valid:
                    raise RuntimeError('changed joint evidence: '+name)
                inputs[str((base/name).relative_to(ROOT))]=actual
    for path in (Path(__file__),ROOT/'toolkit/adm_harness_cli/tests/test_joint_support_audit.py'):
        inputs[str(path.relative_to(ROOT))]=sha256_file(path)
    OUTPUT.mkdir(parents=True)
    paths=[]
    for directory in dirs[2:]:
        for path in sorted(directory.glob('*_summary.json')):
            s=json.loads(path.read_text())
            if s['success'] and (s.get('fluid_fixed',False) or directory.name=='joint_component_cone'):
                paths.append(str(path))
    with ProcessPoolExecutor(max_workers=min(4,args.workers),mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,paths))
    pd.DataFrame(checks).to_csv(OUTPUT/'hash_checks.csv',index=False)
    write_json(OUTPUT/'summary.json',dict(cases=results,hash_checks=len(checks)))
    write_json(OUTPUT/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),input_sha256=inputs,
        output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__=='__main__':
    main()
