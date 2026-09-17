#!/usr/bin/env python3
"""Normalized angular coverage with explicit C1 radial and angular partitions."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import argparse
import json
import multiprocessing
import shutil

import numpy as np
from scipy.optimize import linprog

from adm_harness.c1_joint_sources import joint_cone, PROJECTION_NAMES
from adm_harness.c1_population_boundary import (
    cell_columns, cell_costs, occupied_intervals, overlap_intervals,
    proper_length, refine_partition)
from adm_harness.c1_signed_channels import dec_projections, einstein_source
from assess_c1_joint_sources import library
from audit_c1_angular_absolute import extrapolate
from screen_c1_angular_response import ROOT, digest, load_chart, verify_manifest
from screen_c1_signed_channels import fields


def source_library(control, data):
    spec=json.loads((ROOT/control['base_specification']).read_text())
    parent=ROOT/control['parent_data'];lib=library(spec,parent);g=load_chart(spec)
    old=json.loads((parent/'spatial/assessment.json').read_text())
    old_raw=json.loads((parent/'spatial/tensors.json').read_text())['cases']
    new=json.loads((data/'summary.json').read_text())
    controls=json.loads((data/'response_controls/summary.json').read_text())['cases']
    shooting=json.loads((data/'shooting_response/summary.json').read_text())['cases']
    unique=old['coordinate']+control['absolute_coordinates'];eta=lib['eta']
    tensors=np.zeros((len(unique),2,3));logs=np.zeros_like(tensors)
    errors=np.zeros((len(unique),2));limits=[]
    for s in lib['states']:
        if s['count']==1:
            m=s['module'];tensors[:4,m]=s['tensor'];logs[:4,m]=s['log_source'];errors[:4,m]=s['error']
    for i,v in enumerate(old['limits'],4):
        r=next(r for r in old_raw if r['coordinate']==unique[i])
        tensors[i,0]=eta*np.array(v['tensor']);logs[i,0]=eta*np.array(r['log_source'])
        errors[i,0]=eta*max(3e-11,abs(v['trace_error']),2*max(abs(np.array(v['fit_spread']))))
    for i,x in enumerate(control['absolute_coordinates'],len(old['coordinate'])):
        v=extrapolate(new['absolute'],'broad_left',x)
        r=next(r for r in new['absolute'] if r['coordinate']==x)
        t=np.array(v['tensor']);trace=float(-t[0]+t[1]+2*t[2]-r['anomaly'])
        numerical=0.
        for c in new['absolute']:
            if c['coordinate']==x and c['name']=='numerical_control':
                b=next(b for b in new['absolute'] if b['coordinate']==x and b['name']=='base'
                       and b['mass']==c['mass'] and b['cut']==c['cut'])
                numerical=2*max(abs(np.array(c['tensor'])-np.array(b['tensor'])))
        err=max(abs(trace),2*max(abs(np.array(v['fit_spread']))),numerical)
        v.update(coordinate=x,anomaly=r['anomaly'],trace_error=trace,
                 twice_numerical_change=numerical,raw_component_envelope=err)
        limits.append(v);tensors[i,0]=eta*t;logs[i,0]=eta*np.array(r['log_source']);errors[i,0]=eta*err
    # Scalar walls are elsewhere. Their interior tensors are continuous across
    # these radial walls, so the same scalar calculation supplies both limits.
    indices=list(range(len(unique)));sides=['right']*len(unique)
    for x in (0.4,control['absolute_coordinates'][-1]):
        indices.append(unique.index(x));sides.append('left')
    xx=np.array(unique)[indices];tensors=tensors[indices];logs=logs[indices];errors=errors[indices]
    demand_spec=json.loads((ROOT/spec['parent_specification']).read_text())
    em=json.loads((ROOT/demand_spec['parent_specification']).read_text())
    target=einstein_source(g,xx)-fields(g,xx,em,lib['row']['overlap'])[:,None]*[1.,-1.,1.]
    meshes={}
    outer=[lib['row']['partitions'][0]['coordinate'][i] for i in (0,-1)]
    right=[lib['row']['partitions'][1]['coordinate'][i] for i in (0,-1)]
    for division in [None]+control['angular_divisions']:
        groups=[(0,outer,'left_whole'),(1,right,'right_whole')] if division is None else [
            (0,[outer[0],division],'left_prefix'),(0,[division,outer[1]],'left_suffix'),(1,right,'right_whole')]
        ts=[];hs=[];es=[];metadata=[]
        for m,domain,label in groups:
            t=tensors[:,m].copy();e=errors[:,m].copy()
            mask=(xx>domain[0])&(xx<domain[1])
            if division is not None and m==0:
                for i,x in enumerate(xx):
                    if not mask[i]:continue
                    f=next(r for r in new['response'] if r['division']==division and r['coordinate']==x and r['name']=='fine')
                    b=next(r for r in new['response'] if r['division']==division and r['coordinate']==x and r['name']=='base')
                    refined=[r for r in controls if r['division']==division and r['coordinate']==x]
                    chosen=max(refined,key=lambda r:r['nodes']) if refined else f
                    delta=np.array(chosen['tensor_per_real_field'])
                    t[i]+=delta
                    # Keep the observed coarser-grid variation in the envelope.
                    e[i]+=2*max(max(abs(delta-np.array(r['tensor_per_real_field']))) for r in [b,f]+refined)
                    independent=[r for r in shooting if r['division']==division and r['coordinate']==x]
                    if independent:
                        e[i]+=2*max(max(abs(delta-np.array(r['tensor_per_real_field']))) for r in independent)
            ts.append(t*mask[:,None]);hs.append(logs[:,m]*mask[:,None]);es.append(e*mask)
            metadata.append(dict(module=m,label=label,domain=domain,proper_length=proper_length(g,*domain)))
        key='whole' if division is None else f'divide_{division}'
        meshes[key]=dict(tensor=np.stack(ts,axis=1),log_source=np.stack(hs,axis=1),
                         error=np.stack(es,axis=1),metadata=metadata,division=division)
    return spec,lib['row'],g,xx,sides,target,meshes,limits,old,new


def radial_layout(g,row,x,sides,eta,name,unit):
    parts=[(np.array(p['coordinate']),np.array(p['optical_lengths'])) for p in row['partitions']]
    central=[np.array(c) for c in row['central_charge_per_compartment']]
    added=None
    if name.startswith('split_'):
        added=float(name[6:]);e,l,c=refine_partition(g,*parts[0],central[0],added)
        parts[0]=(e,l);central[0]=c
    single=cell_columns(g,x,sides,parts,eta);old=np.concatenate(central)
    cost=cell_costs(g,parts,eta);groups=[];labels=[]
    nleft=len(parts[0][1]);total=len(old)
    if name=='cells':
        groups=[[j] for j in range(total) if np.any(single[:,j])]
        labels=[f'cell_{j}' for (j,) in groups]
    elif name!='fixed':
        cut=21 if name=='zones_21' else 22
        if added is not None:cut=int(np.searchsorted(parts[0][0],added))
        left_cuts=[0,8,21,22,nleft] if name=='bridge' else [0,8,cut,nleft]
        for lo,hi in zip(left_cuts[:-1],left_cuts[1:]):
            groups.append(list(range(lo,hi)));labels.append(f'left_{parts[0][0][lo]:.12g}_{parts[0][0][hi]:.12g}')
        groups.extend([list(range(nleft,nleft+8)),list(range(nleft+24,total))])
        labels+=['right_overlap_0_8','right_transition_24_32']
    population=np.zeros((total,len(groups)))
    background=old.copy()
    for j,cells in enumerate(groups):population[cells,j]=unit;background[cells]=0
    columns=np.einsum('nct,cs->nst',single,population)
    return dict(name=name,partitions=parts,old=old,background_charge=background,
                population=population,columns=columns,background=np.einsum('nct,c->nt',single,background),
                weights=cost['proper_length']@population/unit,cost=cost,labels=labels,
                added_wall=added,single=single)


def exclusion(target,columns,error,x,sides):
    n=columns.shape[1]
    matrix=dec_projections(columns).transpose(0,2,1).reshape(-1,n)
    matrix+=np.repeat(2*error[:,None,:],4,axis=1).reshape(-1,n)
    bound=dec_projections(target).ravel()-1e-10
    scale=np.maximum(np.maximum(abs(matrix).max(axis=1),abs(bound)),1e-12)
    a,b=matrix/scale[:,None],bound/scale
    d=linprog(b,A_ub=-a.T,b_ub=np.zeros(n),A_eq=np.ones((1,len(b))),b_eq=[1.],bounds=(0,None),method='highs')
    if not d.success or d.fun>=-1e-9 or min(a.T@d.x)<-1e-8:
        raise RuntimeError('unresolved infeasibility certificate')
    return dict(negative_target=float(d.fun),minimum_source_projection=float(min(a.T@d.x)),
        weights=d.x.tolist(),terms=[dict(coordinate=float(x[j//4]),side=sides[j//4],
        projection=PROJECTION_NAMES[j%4],weight=float(d.x[j])) for j in np.flatnonzero(d.x>1e-7)])


def solve(task):
    radial,mesh,mesh_name,ell,sensitivity,target,x,sides,unit,normalization=task
    ac=unit*(mesh['tensor']-2*(ell-1)*mesh['log_source'])
    ae=unit*mesh['error']*(1 if sensitivity else 0)
    rc=radial['columns'];cs=np.concatenate([rc,ac],axis=1)
    es=np.c_[np.zeros(rc.shape[:2]),ae]
    weights=np.r_[radial['weights'],[m['proper_length'] for m in mesh['metadata']]]/normalization
    result=joint_cone(target-radial['background'],cs,weights,es,reserve=1e-10)
    out=dict(radial_layout=radial['name'],angular_mesh=mesh_name,reference_log=ell,
             empirical_sensitivity=sensitivity,allocation=result)
    if not result['feasible']:
        out['certificate']=exclusion(target-radial['background'],cs,es,x,sides)
        return out
    coefficients=np.array(result['coefficients']);n=rc.shape[1]
    central=radial['background_charge']+radial['population']@coefficients[:n]
    scalar=coefficients[n:]*unit;cost=radial['cost']
    force=cost['force_matrix']@central
    occupied=occupied_intervals(radial['partitions'],central)
    angular=[dict(m,fields=float(c)) for m,c in zip(mesh['metadata'],scalar) if c>1e-6]
    angular_domains=[[p['domain'] for p in angular if p['module']==m] for m in (0,1)]
    out.update(radial_central_charges=central.tolist(),angular_populations=angular,
        adjustable_radial_populations=n,occupied_angular_populations=len(angular),
        radial_total_central_charge=float(central.sum()),
        radial_charge_times_proper_length=float(cost['proper_length']@central),
        radial_killing_bulk_energy=float(cost['killing_energy']@central),
        radial_sum_absolute_cell_energy=float(abs(cost['killing_energy']*central).sum()),
        angular_fields_times_proper_length=float(sum(p['fields']*p['proper_length'] for p in angular)),
        radial_wall_forces=force.tolist(),maximum_absolute_radial_wall_force=float(abs(force).max()),
        sum_absolute_radial_wall_force=float(abs(force).sum()),
        changes=dict(geometry='unchanged',maxwell_placement='unchanged',material_outer_envelopes='unchanged',
                     electric_overlap=[.5,2.5],added_radial_wall=radial['added_wall'],
                     added_left_angular_wall=mesh['division'],active_radial_intervals=occupied,
                     active_radial_overlap=overlap_intervals(*occupied),
                     active_angular_intervals=angular_domains,active_angular_overlap=overlap_intervals(*angular_domains),
                     exterior='uncomputed separate state',scalar_internal_wall_material='uncomputed'))
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec',type=Path,default=ROOT/'toolkit/adm_harness_cli/specs/c1_population_boundary.json')
    p.add_argument('--data',type=Path,default=ROOT/'supporting_reports/data/c1_population_boundary')
    p.add_argument('--workers',type=int,default=4);args=p.parse_args()
    if args.workers<1:p.error('positive worker count required')
    control=json.loads(args.spec.read_text());verified=verify_manifest(args.data/'manifest.json')
    verified+=verify_manifest(args.data/'response_controls/manifest.json')
    verified+=verify_manifest(args.data/'shooting_response/manifest.json')
    spec,row,g,x,sides,target,meshes,limits,old,new=source_library(control,args.data)
    eta=new['eta'];unit=spec['charge_unit']
    names=['fixed','zones_22','zones_21','bridge','split_0.35','split_0.4','cells']
    layouts={name:radial_layout(g,row,x,sides,eta,name,unit) for name in names}
    frozen=[]
    for i,c in enumerate(old['six_probe_cases']):
        if not c['empirical_sensitivity'] or not c['all_library']['feasible']:continue
        scalar=np.zeros_like(target);error=np.zeros(len(x));mesh=meshes['whole']
        for population in c['angular_fields']:
            m=population['module'];count=population['fields']
            scalar+=count*(mesh['tensor'][:,m]-2*(c['reference_log']-1)*mesh['log_source'][:,m])
            error+=count*mesh['error'][:,m]
        radial=np.einsum('nct,c->nt',layouts['fixed']['single'],np.array(c['radial_central_charges']).ravel())
        material=target-radial-scalar
        frozen.append(dict(parent_case=i,radial_mode=c['radial_mode'],reference_log=c['reference_log'],
            material=material.tolist(),margins_after_envelope=(dec_projections(material)-2*error[:,None]).tolist()))
    norm=proper_length(g,*[row['partitions'][0]['coordinate'][i] for i in (0,-1)])
    tasks=[(radial,mesh,m,ell,sensitive,target,x,sides,unit,norm)
           for radial in layouts.values() for m,mesh in meshes.items()
           for ell in control['reference_logs'] for sensitive in (False,True)]
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
        cases=list(pool.map(solve,tasks))
    for c in cases:
        if not c['allocation']['feasible']:continue
        increments=[];mesh=meshes[c['angular_mesh']]
        if mesh['division'] is not None:
            for pop in c['angular_populations']:
                if pop['module']!=0:continue
                endpoint=pop['domain'][0] if pop['label']=='left_prefix' else pop['domain'][1]
                r=next(r for r in new['response'] if r['division']==mesh['division'] and r['coordinate']==endpoint and r['name']=='fine')
                increments.append(dict(coordinate=endpoint,force_increment=r['force_increment_per_real_field']*pop['fields'],
                    reference='same population in original whole left cavity'))
        c['finite_angular_original_end_force_increments']=increments
    def serial(v):
        if isinstance(v,np.ndarray):return v.tolist()
        if isinstance(v,dict):return {k:serial(a) for k,a in v.items()}
        if isinstance(v,(list,tuple)):return [serial(a) for a in v]
        return v
    result=dict(verified_input_hashes=verified,coordinate=x.tolist(),sides=sides,eta=eta,charge_unit=unit,
        target=target.tolist(),normalized_angular_library=serial(meshes),new_absolute_limits=limits,
        radial_layouts=serial(layouts),frozen_six_probe_allocations=frozen,cases=cases,
        objective='central charge and field-copy counts weighted by proper occupied length, divided by left-module proper length; heterogeneous carrier-extent proxy',
        common_extent_normalization=norm,scope='nine distinct bulk coordinates, including both limits at radial walls 0.4 and 0.5178507081509361',
        full_spatial_source_material_and_exterior_closure=False)
    output=args.data/'assessment.json';output.write_text(json.dumps(result,indent=2)+'\n')
    script=Path(__file__).resolve();snapshot=args.data/('execution_'+script.name);shutil.copy2(script,snapshot)
    inputs=[args.spec,script,ROOT/control['base_specification'],args.data/'manifest.json',args.data/'summary.json',
        args.data/'response_controls/summary.json',args.data/'response_controls/manifest.json',
        args.data/'shooting_response/summary.json',args.data/'shooting_response/manifest.json',
        ROOT/control['parent_data']/'spatial/assessment.json',ROOT/control['parent_data']/'spatial/tensors.json',
        ROOT/'toolkit/adm_harness_cli/adm_harness/c1_population_boundary.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/c1_joint_sources.py',
        ROOT/'toolkit/adm_harness_cli/scripts/assess_c1_joint_sources.py',
        ROOT/'toolkit/adm_harness_cli/scripts/audit_c1_angular_absolute.py']
    manifest=dict(workers=args.workers,input_sha256={str(p.relative_to(ROOT)):digest(p) for p in inputs},
                  output_sha256={p.name:digest(p) for p in (output,snapshot)})
    (args.data/'assessment_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),feasible=sum(c['allocation']['feasible'] for c in cases),new_limits=limits),indent=2))


if __name__=='__main__':main()
