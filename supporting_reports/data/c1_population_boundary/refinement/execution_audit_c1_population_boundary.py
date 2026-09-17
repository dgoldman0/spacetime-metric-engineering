#!/usr/bin/env python3
"""Independent reconstruction, cost integrals and infeasibility certificates."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import argparse
import json
import multiprocessing
import shutil

import numpy as np

from adm_harness.c1_angular_absolute import AbsoluteComparison
from adm_harness.c1_angular_response import AngularResponse
from adm_harness.c1_signed_channels import channel_tensor,dec_projections,einstein_source,quadrature,strip_tensor
from audit_c1_angular_absolute import independent_mode, mode_job
from screen_c1_angular_response import ROOT,digest,load_chart,verify_manifest
from screen_c1_signed_channels import fields,wall_forces


def finite_mode(task):
    spec,x,w,j=task;g=load_chart(spec);domain=[-2.95,2.45]
    child=[-2.95,.3] if x<.3 else [.3,2.45]
    exact=independent_mode(g,child,x,w,j,0.)-independent_mode(g,domain,x,w,j,0.)
    a=float(g.jets(np.array([x]))[1][0]);values=[]
    for nodes in (8193,32769,65537):
        problem=AngularResponse(g,domain,[.3],np.array([x]),nodes)
        value=a*problem.tensor(w*a,j)[0]
        values.append(dict(nodes=nodes,tensor=value.tolist(),absolute_error=float(abs(value-exact).max())))
    return dict(coordinate=x,local_frequency=w,harmonic=j,independent=exact.tolist(),finite_volume=values)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,default=ROOT/'supporting_reports/data/c1_population_boundary')
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--refinement',action='store_true');args=p.parse_args()
    if args.workers<1:p.error('positive worker count required')
    verified=sum(verify_manifest(args.data/n) for n in ('manifest.json','response_controls/manifest.json','assessment_manifest.json'))
    output_dir=args.data/'refinement' if args.refinement else args.data
    if args.refinement:verified+=verify_manifest(output_dir/'manifest.json')
    a=json.loads((output_dir/'assessment.json').read_text());raw=json.loads((args.data/'summary.json').read_text())
    control=json.loads((ROOT/'toolkit/adm_harness_cli/specs/c1_population_boundary.json').read_text())
    spec=json.loads((ROOT/control['base_specification']).read_text());g=load_chart(spec)
    x=np.array(a['coordinate']);eta=a['eta'];unit=a['charge_unit'];checks=[];costs=[]
    for name,r in a['radial_layouts'].items():
        parts=[(np.array(e),np.array(l)) for e,l in r['partitions']]
        energies=[];optical=[];offset=0;independent=np.zeros_like(np.array(r['single']))
        for ends,lengths in parts:
            for j,length in enumerate(lengths):
                xx,ww=quadrature(g,ends[j],ends[j+1],order=12)
                rr,aa,bb,_,_,ap,app=g.jets(xx)
                tensor=strip_tensor(rr,aa,ap,app,length,strength=eta)
                energies.append(float(ww@(4*np.pi*rr*rr*aa*bb*tensor[:,0])))
                optical.append(float(ww@(bb/aa)))
                for i,(pnt,side) in enumerate(zip(x,a['sides'])):
                    inside=(ends[j]<pnt<=ends[j+1]) if side=='left' else (ends[j]<=pnt<ends[j+1])
                    if inside:
                        rr,aa,_,_,_,ap,app=g.jets(np.array([pnt]))
                        independent[i,offset+j]=strip_tensor(rr,aa,ap,app,length,strength=eta)[0]
            offset+=len(lengths)
        old=np.array(r['old']);split=np.cumsum([len(l) for _,l in parts])[:-1]
        force=wall_forces(g,parts,[eta*c for c in np.split(old,split)])
        fv=np.concatenate([v['force_on_material'] for v in force])
        expected=np.array(r['cost']['force_matrix'])@old
        cost_error=float(abs(np.array(energies)-r['cost']['killing_energy']).max())
        optical_error=float(abs(np.array(optical)-np.concatenate([l for _,l in parts])).max())
        bulk_error=float(abs(independent-r['single']).max());force_error=float(abs(fv-expected).max())
        if cost_error>1e-12 or optical_error>1e-10 or bulk_error>1e-14 or force_error>1e-10:
            raise RuntimeError('radial source or cost reconstruction failed')
        costs.append(dict(layout=name,energy_absolute_error=cost_error,optical_length_error=optical_error,
                          bulk_error=bulk_error,force_absolute_error=force_error))
    for index,c in enumerate(a['cases']):
        r=a['radial_layouts'][c['radial_layout']];s=a['normalized_angular_library'][c['angular_mesh']]
        ac=unit*(np.array(s['tensor'])-2*(c['reference_log']-1)*np.array(s['log_source']))
        rc=np.array(r['columns']).reshape(len(x),-1,3);cs=np.concatenate([rc,ac],axis=1)
        error=np.c_[np.zeros(rc.shape[:2]),unit*np.array(s['error'])*(1 if c['empirical_sensitivity'] else 0)]
        target=np.array(a['target'])-r['background'];n=cs.shape[1]
        matrix=dec_projections(cs).transpose(0,2,1).reshape(-1,n)
        matrix+=np.repeat(2*error[:,None,:],4,axis=1).reshape(-1,n)
        bound=dec_projections(target).ravel()-1e-10
        scale=np.maximum(np.maximum(abs(matrix).max(axis=1),abs(bound)),1e-12)
        if c['allocation']['feasible']:
            coeff=np.array(c['allocation']['coefficients'])
            material=target-np.einsum('nst,s->nt',cs,coeff)
            margin=float((dec_projections(material)-2*(error@coeff)[:,None]).min())
            diff=float(abs(material-c['allocation']['material']).max())
            if margin<-2e-9 or diff>2e-12:raise RuntimeError('allocation reconstruction failed')
            checks.append(dict(case=index,minimum_margin_after_envelope=margin,reconstruction_error=diff))
        else:
            weights=np.array(c['certificate']['weights']);source=(matrix/scale[:,None]).T@weights
            demand=float((bound/scale)@weights)
            if min(weights)<-1e-12 or abs(sum(weights)-1)>1e-8 or min(source)<-1e-8 or demand>=-1e-9:
                raise RuntimeError('dual certificate failed')
            checks.append(dict(case=index,negative_target=demand,minimum_source=float(min(source))))
    tasks=[(spec,[-2.95,2.45],xx,w,j,mass)
           for xx in control['absolute_coordinates'] for w,j,mass in ((.3,0,0.),(2.,3,8.))]
    ftasks=[(spec,xx,w,j) for xx in control['absolute_coordinates'] for w,j in ((.2,0),(1.,2))]
    if args.refinement:
        verified+=verify_manifest(args.data/'audit_manifest.json')
        original=json.loads((args.data/'audit.json').read_text())
        modes=original['independent_absolute_modes'];finite=original['independent_finite_response_modes']
    else:
        with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
            modes=list(pool.map(mode_job,tasks));finite=list(pool.map(finite_mode,ftasks))
    if max(r['absolute_error'] for r in modes)>2e-6:raise RuntimeError('independent original-mode check failed')
    response=raw['response']+json.loads((args.data/'response_controls/summary.json').read_text())['cases']
    metrics=dict(maximum_response_trace_error=max(abs(r['trace_difference']) for r in response),
        maximum_response_harmonic_tail=max(r['angular_tail_last_quarter_relative'] for r in response),
        finite_volume_ward_controls=[dict(coordinate=r['coordinate'],division=r['division'],nodes=r['nodes'],
            ward=r['ward_residual_times_radius_over_tensor']) for r in response if 'ward_residual_times_radius_over_tensor' in r],
        response_error_scope='empirical resolution envelope; Ward convergence nearest the 0.3 wall remains recorded separately')
    result=dict(verified_input_hashes=verified,cost_reconstruction=costs,allocations_and_certificates=checks,
                independent_absolute_modes=modes,independent_finite_response_modes=finite,metrics=metrics,
                full_spatial_source_material_and_exterior_closure=False)
    if args.refinement:
        parent=json.loads((ROOT/spec['parent_specification']).read_text())
        em=json.loads((ROOT/parent['parent_specification']).read_text())
        gaps=[];ledgers=[]
        for i,c in enumerate(a['cases']):
            if not c['allocation']['feasible'] or not c['empirical_sensitivity']:continue
            r=a['radial_layouts'][c['radial_layout']];force=np.array(c['radial_wall_forces'])
            left=np.array([w['module']==0 for w in r['cost']['walls']])
            added=left & np.array([w['coordinate'] in r['added_wall'] for w in r['cost']['walls']])
            ledgers.append(dict(case=i,maximum_left_radial_force=float(abs(force[left]).max()),
                maximum_added_radial_wall_force=float(abs(force[added]).max()),
                sum_absolute_added_radial_wall_force=float(abs(force[added]).sum()),
                occupied_radial_intervals=c['changes']['active_radial_intervals'],
                occupied_angular_intervals=c['changes']['active_angular_intervals']))
            # Known assigned interior sources in the interval between angular
            # populations. The omitted exterior vacuum remains an unknown duty.
            if any(p['module']==0 and p['domain'][1]>.3 for p in c['angular_populations']):continue
            for samples in (1025,4097):
                walls=np.concatenate([e for e,l in r['partitions']]);near=np.r_[walls-1e-9,walls+1e-9]
                xx=np.unique(np.r_[np.linspace(.300001,.549999,samples),near[(near>.300001)&(near<.549999)]])
                target=einstein_source(g,xx)-fields(g,xx,em,[.5,2.5])[:,None]*[1.,-1.,1.]
                radial=np.zeros_like(target);offset=0
                for ends,lengths in r['partitions']:
                    for j,length in enumerate(lengths):
                        radial+=channel_tensor(g,xx,ends[j:j+2],[length],strength=eta*c['radial_central_charges'][offset+j])
                    offset+=len(lengths)
                residual=target-radial;proj=dec_projections(residual);j,k=np.unravel_index(np.argmin(proj),proj.shape)
                artifact=f'angular_gap_{i:03d}_{samples}.npz'
                np.savez_compressed(output_dir/artifact,coordinate=xx,known_interior_remainder=residual,dec_margins=proj)
                gaps.append(dict(case=i,samples=samples,minimum_margin=float(proj[j,k]),
                    coordinate=float(xx[j]),projection_index=int(k),artifact=artifact,
                    interpretation='remaining demand after assigned Maxwell and radial interiors; exterior vacuum and wall material unsupplied'))
        result.update(radial_added_wall_ledger=ledgers,angular_gap_duties=gaps)
    output=output_dir/'audit.json';output.write_text(json.dumps(result,indent=2)+'\n')
    script=Path(__file__).resolve();snapshot=output_dir/('execution_'+script.name);shutil.copy2(script,snapshot)
    inputs=[script,output_dir/'assessment.json',args.data/'assessment_manifest.json',args.data/'manifest.json',
            args.data/'response_controls/manifest.json',ROOT/'toolkit/adm_harness_cli/scripts/audit_c1_angular_absolute.py',
            ROOT/'toolkit/adm_harness_cli/scripts/screen_c1_signed_channels.py']
    if args.refinement:inputs+=[output_dir/'manifest.json',args.data/'audit.json']
    manifest=dict(workers=args.workers,input_sha256={str(p.relative_to(ROOT)):digest(p) for p in inputs},
                  output_sha256={p.name:digest(p) for p in [output,snapshot]+sorted(output_dir.glob('angular_gap_*.npz'))})
    (output_dir/'audit_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(cases_checked=len(checks),cost_layouts=len(costs),
          maximum_original_mode_error=max(r['absolute_error'] for r in modes))))


if __name__=='__main__':main()
