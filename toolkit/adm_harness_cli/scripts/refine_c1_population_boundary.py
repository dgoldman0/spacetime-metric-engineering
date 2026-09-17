#!/usr/bin/env python3
"""Accounted radial-cavity refinement on both sides of the measured bottleneck."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import argparse
import json
import multiprocessing
import shutil

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq

from adm_harness.c1_population_boundary import cell_columns,cell_costs,refine_partition
from assess_c1_population_boundary import solve
from screen_c1_angular_response import ROOT,digest,load_chart,verify_manifest


def layout(g,original,x,sides,eta,unit,count,pattern,cells):
    parts=[(np.array(e),np.array(l)) for e,l in original['partitions']]
    old=np.array(original['old']);oldleft=len(parts[0][1]);left=old[:oldleft]
    ends,lengths=parts[0];primitive=CubicSpline(g.coordinate,g.radial_scale/g.lapse).antiderivative()
    walls=[]
    for j in cells:
        lo,hi=ends[j:j+2];vlo,vhi=primitive([lo,hi])
        for n in range(1,count):
            value=vlo+(vhi-vlo)*n/count
            walls.append(float(brentq(lambda xx:float(primitive(xx)-value),lo,hi,xtol=2e-14)))
    for wall in sorted(walls):ends,lengths,left=refine_partition(g,ends,lengths,left,wall)
    parts[0]=(ends,lengths);old=np.r_[left,old[oldleft:]];nleft=len(lengths)
    boundaries=[0,8,21,21+2*count,nleft] if pattern=='pair_uniform' else [0,8,21,21+count,21+2*count,nleft]
    groups=[list(range(lo,hi)) for lo,hi in zip(boundaries[:-1],boundaries[1:])]
    labels=[f'left_{ends[lo]:.12g}_{ends[hi]:.12g}' for lo,hi in zip(boundaries[:-1],boundaries[1:])]
    groups += [list(range(nleft,nleft+8)),list(range(nleft+24,len(old)))]
    labels += ['right_overlap_0_8','right_transition_24_32']
    population=np.zeros((len(old),len(groups)));background=old.copy()
    for j,indices in enumerate(groups):population[indices,j]=unit;background[indices]=0
    single=cell_columns(g,x,sides,parts,eta);cost=cell_costs(g,parts,eta)
    return dict(name=f'subdivide_{count}_{pattern}',partitions=parts,old=old,background_charge=background,
        population=population,columns=np.einsum('nct,cs->nst',single,population),
        background=np.einsum('nct,c->nt',single,background),weights=cost['proper_length']@population/unit,
        cost=cost,labels=labels,added_wall=sorted(walls),single=single,
        subdivisions_per_old_cell=count,population_pattern=pattern,
        refinement_optical_sum_error=float(lengths[21:21+2*count].sum()-np.array(original['partitions'][0][1])[21:23].sum()))


def serial(v):
    if isinstance(v,np.ndarray):return v.tolist()
    if isinstance(v,dict):return {k:serial(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [serial(x) for x in v]
    return v


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec',type=Path,default=ROOT/'toolkit/adm_harness_cli/specs/c1_population_refinement.json')
    p.add_argument('--workers',type=int,default=4);args=p.parse_args()
    if args.workers<1:p.error('positive worker count required')
    control=json.loads(args.spec.read_text());data=ROOT/control['parent_data'];output=data/'refinement'
    output.mkdir(exist_ok=True)
    if control['left_cells_to_subdivide']!=[21,22]:raise ValueError('this population comparison specifies old cells 21 and 22')
    verified=verify_manifest(data/'assessment_manifest.json')
    a=json.loads((data/'assessment.json').read_text());spec=json.loads((ROOT/control['base_specification']).read_text());g=load_chart(spec)
    x=np.array(a['coordinate']);sides=a['sides'];eta=a['eta'];unit=a['charge_unit'];target=np.array(a['target'])
    meshes=a['normalized_angular_library']
    for m in meshes.values():
        for key in ('tensor','log_source','error'):m[key]=np.array(m[key])
    layouts={}
    for count in control['subdivisions_per_old_cell']:
        for pattern in control['population_patterns']:
            r=layout(g,a['radial_layouts']['fixed'],x,sides,eta,unit,count,pattern,control['left_cells_to_subdivide'])
            layouts[r['name']]=r
    tasks=[(r,mesh,m,ell,sensitive,target,x,sides,unit,a['common_extent_normalization'])
           for r in layouts.values() for m,mesh in meshes.items()
           for ell in control['reference_logs'] for sensitive in (False,True)]
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
        cases=list(pool.map(solve,tasks))
    responses=json.loads((data/'summary.json').read_text())['response']
    for c in cases:
        if not c['allocation']['feasible']:continue
        inc=[];mesh=meshes[c['angular_mesh']]
        if mesh['division'] is not None:
            for pop in c['angular_populations']:
                if pop['module']!=0:continue
                endpoint=pop['domain'][0] if pop['label']=='left_prefix' else pop['domain'][1]
                r=next(r for r in responses if r['division']==mesh['division'] and r['coordinate']==endpoint and r['name']=='fine')
                inc.append(dict(coordinate=endpoint,force_increment=r['force_increment_per_real_field']*pop['fields'],
                                reference='same population in original whole left cavity'))
        c['finite_angular_original_end_force_increments']=inc
    result=dict(verified_input_hashes=verified,coordinate=x.tolist(),sides=sides,eta=eta,charge_unit=unit,
        target=target.tolist(),normalized_angular_library=serial(meshes),radial_layouts=serial(layouts),cases=cases,
        common_extent_normalization=a['common_extent_normalization'],objective=a['objective'],
        full_spatial_source_material_and_exterior_closure=False)
    result_path=output/'assessment.json';result_path.write_text(json.dumps(result,indent=2)+'\n')
    script=Path(__file__).resolve();snapshot=output/('execution_'+script.name);shutil.copy2(script,snapshot)
    inputs=[args.spec,script,data/'assessment.json',data/'assessment_manifest.json',
        ROOT/'toolkit/adm_harness_cli/scripts/assess_c1_population_boundary.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/c1_population_boundary.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/c1_joint_sources.py']
    manifest=dict(workers=args.workers,input_sha256={str(p.relative_to(ROOT)):digest(p) for p in inputs},
                  output_sha256={p.name:digest(p) for p in (result_path,snapshot)})
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    for c in cases:
        if c['empirical_sensitivity']:
            print(c['radial_layout'],c['angular_mesh'],c['reference_log'],c['allocation']['feasible'],
                  c.get('maximum_absolute_radial_wall_force'),flush=True)


if __name__=='__main__':main()
