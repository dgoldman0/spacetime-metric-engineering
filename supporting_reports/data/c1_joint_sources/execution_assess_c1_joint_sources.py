#!/usr/bin/env python3
"""Joint complete-tensor allocations with module and independently confined cells."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import combinations
from pathlib import Path
import argparse
import json
import multiprocessing
import shutil

import numpy as np

from adm_harness.c1_joint_sources import RADIAL_ZONES, joint_cone, radial_columns
from adm_harness.c1_signed_channels import channel_tensor
from adm_harness.c1_signed_channels import dec_projections, einstein_source
from audit_c1_angular_absolute import extrapolate
from screen_c1_angular_response import ROOT, digest, load_chart, remainder, retained_rows, verify_manifest
from screen_c1_signed_channels import fields, wall_forces


def library(spec, data):
    parent=json.loads((ROOT/spec['parent_specification']).read_text())
    row=retained_rows(spec)['broad'];g=load_chart(spec)
    absolute=json.loads((ROOT/spec['absolute_data']/'audit.json').read_text())
    response=json.loads((ROOT/spec['response_data']/'summary.json').read_text())['cases']
    transitions=json.loads((data/'transitions.json').read_text())['cases']
    controls=json.loads((data/'controls/summary.json').read_text())
    transitions+=controls['absolute'];response+=controls['response']
    coordinates=[next(r['coordinate'] for r in transitions if r['source']=='broad_left'),
                 0.,.75,next(r['coordinate'] for r in transitions if r['source']=='shared_right')]
    x=np.array(coordinates);eta=parent['eta']
    limits=dict(absolute['limits'])
    for source,p in (('broad_left',0),('shared_right',3)):
        r=next(r for r in transitions if r['source']==source)
        value=extrapolate(transitions,source,float(x[p]))
        tensor=np.array(value['tensor'])
        value.update(anomaly=r['anomaly'],trace_error=float(-tensor[0]+tensor[1]+2*tensor[2]-r['anomaly']))
        limits[f'{source}_{x[p]}']=value
    old=json.loads((ROOT/spec['absolute_data']/'summary.json').read_text())['cases']
    base=np.zeros((4,2,3));local=np.zeros_like(base);errors=np.zeros((4,2))
    for module,source in enumerate(('broad_left','shared_right')):
        for p in ([0,1,2] if module==0 else [2,3]):
            value=limits[f'{source}_{x[p]}']
            record=next(r for r in transitions+old if r['source']==source and r['coordinate']==x[p])
            base[p,module]=eta*np.array(value['tensor'])
            local[p,module]=eta*np.array(record['log_source'])
            floor=3e-11 if p==1 else (3e-7 if module==0 and p==2 else 6e-6 if p==2 else 0.)
            numerical=0.
            for c in transitions:
                if c['source']==source and c['coordinate']==x[p] and c['name']=='combined_numerical_control':
                    b=next(b for b in transitions if b['source']==source and b['coordinate']==x[p]
                           and b['name']=='base' and b['mass']==c['mass'] and b['cut']==c['cut'])
                    numerical=2*max(abs(np.array(c['tensor'])-np.array(b['tensor'])))
            # Empirical sensitivity: each component may vary independently.
            # Transition controls use the larger of fit and trace discrepancies.
            errors[p,module]=eta*max(floor,numerical,2*max(abs(np.array(value['fit_spread']))),
                                      abs(value['trace_error']))
    states=[]
    for module,source in enumerate(('broad_left','shared_right')):
        ends=np.array(row['partitions'][module]['coordinate'])
        counts=sorted(set(spec['angular_compartment_states'])|set(r['compartment_count'] for r in controls['response']))
        for count in counts:
            tensor=base[:,module].copy();error=errors[:,module].copy()
            selected=[r for r in response if r['source']==source and r['name']=='fine'
                      and r['compartment_count']==count]
            if count>1:
                for p in ([0,1,2] if module==0 else [2,3]):
                    r=next(r for r in selected if r['coordinate']==x[p])
                    delta=np.array(r['tensor_per_real_field'])
                    tensor[p]+=delta
                    coarse=next(r0 for r0 in response if r0['source']==source
                                and r0['name']=='base' and r0['compartment_count']==count
                                and r0['coordinate']==x[p])
                    error[p]+=2*max(abs(delta-np.array(coarse['tensor_per_real_field'])))
            states.append(dict(label=f'{source}_{count}_cells',module=module,count=count,
                ends=ends[::32//count].tolist(),tensor=tensor.tolist(),
                log_source=local[:,module].tolist(),error=error.tolist()))
    em_spec=json.loads((ROOT/parent['parent_specification']).read_text())
    target=einstein_source(g,x)-fields(g,x,em_spec,row['overlap'])[:,None]*np.array([1.,-1.,1.])
    retained=remainder(g,x,row,parent)
    radial={}
    for mode in ('module_scales','compartments','zones'):
        c,w,l=radial_columns(g,x,row,eta,mode,spec['charge_unit'])
        background=np.zeros_like(target)
        if mode=='zones':
            part=row['partitions'][1];ends=np.array(part['coordinate'])
            for j in range(8,24):
                background+=channel_tensor(g,x,ends[j:j+2],part['optical_lengths'][j:j+1],
                    strength=eta*row['central_charge_per_compartment'][1][j])
        radial[mode]=dict(columns=c.tolist(),weights=w.tolist(),labels=l,background=background.tolist())
    return dict(coordinate=coordinates,eta=eta,limits=limits,states=states,
                target=target.tolist(),retained_target=retained.tolist(),radial=radial,row=row)


def angular_columns(lib, ell, mesh, charge_unit):
    columns=[];envelopes=[];metadata=[]
    x=np.array(lib['coordinate'])
    for state in lib['states']:
        if mesh=='independent_cells_only' and state['count']==1:continue
        t=(np.array(state['tensor'])-2*(ell-1)*np.array(state['log_source']))*charge_unit
        e=np.array(state['error'])*charge_unit
        ends=np.array(state['ends'])
        if mesh=='module':
            groups=[None]
        else:
            if state['count']==1:
                groups=[None]
            else:
                index=np.searchsorted(ends,x,side='right')-1
                groups=sorted(set(index[(x>ends[0])&(x<ends[-1])].tolist()))
        for group in groups:
            mask=np.ones(len(x)) if group is None else (
                (x>ends[group])&(x<ends[group+1])).astype(float)
            domain=ends[[0,-1]].tolist() if group is None else ends[group:group+2].tolist()
            columns.append(t*mask[:,None]);envelopes.append(e*mask)
            metadata.append(dict(label=state['label']+(f'_independent_{group}' if group is not None else ''),
                module=state['module'],count=state['count'],cell=group,domain=domain,
                population_unit=charge_unit,
                physical_interpretation='complete interior Dirichlet cavity solution',
                exterior_and_wall_material='uncomputed separate contributions'))
    return np.stack(columns,axis=1),np.stack(envelopes,axis=1),metadata


def solve_case(task):
    lib,ell,mode,mesh,sensitivity,unit=task
    angular,errors,labels=angular_columns(lib,ell,mesh,unit)
    if not sensitivity:errors*=0
    if mode=='fixed':
        target=np.array(lib['retained_target'])
        radial=np.empty((len(target),0,3));weights=np.empty(0);radial_labels=[]
    else:
        r=lib['radial'][mode];target=np.array(lib['target'])-np.array(r['background'])
        radial=np.array(r['columns']);weights=np.array(r['weights']);radial_labels=r['labels']
    nrad=radial.shape[1]
    def solve(selected):
        cs=np.concatenate([radial,angular[:,selected,:]],axis=1)
        es=np.c_[np.zeros(radial.shape[:2]),errors[:,selected]]
        result=joint_cone(target,cs,np.r_[weights,np.ones(len(selected))],es,reserve=1e-10)
        result['angular_selected']=list(selected)
        return result
    full=solve(tuple(range(len(labels))))
    result=dict(reference_log=ell,radial_mode=mode,angular_mesh=mesh,
                empirical_sensitivity=sensitivity,all_library=full,
                angular_metadata=labels,radial_labels=radial_labels,
                physical_acceptance=False)
    if not full['feasible']:
        if 'direct_witness' in full:
            full['direct_witness']['coordinate']=lib['coordinate'][full['direct_witness']['sample']]
        return result
    # Cardinality counts configured angular populations. Radial mechanism and
    # microscopic inventory are reported separately from this combinatorial cost.
    tried=1;best=None
    for count in range(len(labels)+1):
        successes=[]
        for selected in combinations(range(len(labels)),count):
            candidate=solve(selected);tried+=1
            if candidate['feasible']:successes.append(candidate)
        if successes:
            best=min(successes,key=lambda r:r['inventory_proxy']);break
    result.update(minimum_angular_populations=count,subsets_evaluated=tried,best=best)
    coefficients=np.array(best['coefficients'])
    result['angular_fields']=[dict(labels[j],fields=float(unit*c))
                             for j,c in zip(best['angular_selected'],coefficients[nrad:]) if c>1e-8]
    old=np.array(lib['row']['central_charge_per_compartment'])
    if mode=='fixed':central=old
    elif mode=='module_scales':central=old*coefficients[:nrad,None]
    elif mode=='compartments':
        # Samples provide no information about the other compartments. Retain
        # their existing populations instead of treating zero as a solution.
        seen=np.any(radial!=0,axis=(0,2))
        coefficients[:nrad][~seen]=old.ravel()[~seen]/unit
        central=coefficients[:nrad].reshape(old.shape)*unit
        best['sample_optimized_inventory_proxy']=best['inventory_proxy']
        best['inventory_proxy']+=float((old.ravel()[~seen]/unit).sum())
        best['coefficients']=coefficients.tolist()
        result['unsampled_radial_cells_retained']=np.flatnonzero(~seen).tolist()
    else:
        central=old.copy()
        for coefficient,(module,lower,upper) in zip(coefficients[:nrad],RADIAL_ZONES):
            central[module,lower:upper]=unit*coefficient
        result['fixed_radial_background']='retained right-module cells 8 through 23'
    result['radial_central_charges']=central.tolist()
    result['radial_total_charge']=float(central.sum())
    return result


def add_boundary_ledger(result,lib,spec):
    if 'best' not in result:return
    g=load_chart(spec)
    parts=[(np.array(p['coordinate']),np.array(p['optical_lengths'])) for p in lib['row']['partitions']]
    wall=wall_forces(g,parts,lib['eta']*np.array(result['radial_central_charges']))
    old=wall_forces(g,parts,lib['eta']*np.array(lib['row']['central_charge_per_compartment']))
    for r,o in zip(wall,old):
        r['change_from_retained']=(np.array(r['force_on_material'])-np.array(o['force_on_material'])).tolist()
    result['radial_wall_forces']=wall
    response=json.loads((ROOT/spec['response_data']/'summary.json').read_text())['cases']
    response+=json.loads((ROOT/'supporting_reports/data/c1_joint_sources/controls/summary.json').read_text())['response']
    increments=[]
    for population in result['angular_fields']:
        if population['count']==1:continue
        source=('broad_left','shared_right')[population['module']]
        ends=np.array(lib['row']['partitions'][population['module']]['coordinate'])[[0,-1]]
        for side,coordinate in zip(('outer_left','outer_right'),ends):
            if coordinate not in population['domain']:continue
            r=next(r for r in response if r['source']==source and r['name']=='fine'
                   and r['compartment_count']==population['count'] and r['probe_name']==side)
            increments.append(dict(population=population['label'],coordinate=float(coordinate),
                relative_to='same population in original one-compartment module',
                force_increment=r['force_increment_per_real_field']*population['fields']))
    result['known_angular_original_end_force_increments']=increments
    occupied=[]
    for part,central in zip(lib['row']['partitions'],result['radial_central_charges']):
        intervals=[]
        for j,c in enumerate(central):
            if c<=1e-6:continue
            lo,hi=part['coordinate'][j:j+2]
            if intervals and intervals[-1][1]==lo:intervals[-1][1]=hi
            else:intervals.append([lo,hi])
        occupied.append(intervals)
    shared=[[max(a,c),min(b,d)] for a,b in occupied[0] for c,d in occupied[1] if max(a,c)<min(b,d)]
    angular_domains=[[p['domain'] for p in result['angular_fields'] if p['module']==m] for m in (0,1)]
    angular_shared=[[max(a,c),min(b,d)] for a,b in angular_domains[0]
                    for c,d in angular_domains[1] if max(a,c)<min(b,d)]
    result['changes']=dict(geometry='unchanged',maxwell_placement='unchanged',
        radial_boundaries='unchanged',electric_overlap='unchanged broad bracket',
        radial_populations='retained' if result['radial_mode']=='fixed' else 'changed; unsampled cells retained',
        active_radial_intervals=occupied,active_radial_overlap=shared,
        radial_support_reporting_threshold_central_charge=1e-6,
        angular_domains=[dict(label=p['label'],domain=p['domain'],fields=p['fields']) for p in result['angular_fields']],
        active_angular_cavity_overlap=angular_shared,
        angular_internal_walls='specified by selected cavity domains; independent of radial wall transparency',
        exterior='uncomputed; assigned cavity support is not an exterior state')
    result['uncomputed_boundary_demands']=[
        'absolute renormalized stresses and material at scalar walls, including independently populated internal walls',
        'radial reflector mass, transverse confinement, carrier constitutive response and recoil',
        'exterior field state and interface matching; zero outside an assigned interior is a ledger convention',
        'full spatial profile between the four probes and time-dependent handoff']


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec',type=Path,default=ROOT/'toolkit/adm_harness_cli/specs/c1_joint_sources.json')
    p.add_argument('--data',type=Path,default=ROOT/'supporting_reports/data/c1_joint_sources')
    p.add_argument('--workers',type=int,default=4);args=p.parse_args()
    if args.workers<1:p.error('positive worker count required')
    spec=json.loads(args.spec.read_text())
    verified=verify_manifest(args.data/'transition_manifest.json')
    verified+=verify_manifest(args.data/'controls/manifest.json')
    verified+=verify_manifest(ROOT/spec['parent_manifest'])
    lib=library(spec,args.data)
    tasks=[(lib,ell,mode,mesh,sensitive,spec['charge_unit'])
           for ell in spec['reference_logs'] for mode in spec['radial_modes']+['zones']
           for mesh in ('module','independent_cells','independent_cells_only') for sensitive in (False,True)]
    results=[]
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
        for f in as_completed([pool.submit(solve_case,t) for t in tasks]):
            r=f.result();add_boundary_ledger(r,lib,spec);results.append(r)
            print(f"{len(results)}/{len(tasks)} ell={r['reference_log']} {r['radial_mode']} "
                  f"{r['angular_mesh']} sensitivity={r['empirical_sensitivity']} "
                  f"feasible={r['all_library']['feasible']}",flush=True)
    result=dict(verified_input_hashes=verified,coordinate=lib['coordinate'],eta=lib['eta'],
                transition_limits={k:v for k,v in lib['limits'].items() if k.endswith(str(lib['coordinate'][0])) or k.endswith(str(lib['coordinate'][3]))},
                normalized_library=lib['states'],target=lib['target'],retained_target=lib['retained_target'],
                cases=sorted(results,key=lambda r:(r['reference_log'],r['radial_mode'],r['angular_mesh'],r['empirical_sensitivity'])),
                inventory_objective='sum of scalar field-copy populations and radial central charges; heterogeneous proxy, not physical energy or material cost',
                claim='necessary four-probe bulk allocations with declared finite cavity interiors; finite material and exterior closure open')
    output=args.data/'assessment.json';output.write_text(json.dumps(result,indent=2)+'\n')
    script=Path(__file__).resolve();snapshot=args.data/('execution_'+script.name);shutil.copy2(script,snapshot)
    inputs=[args.spec,script,ROOT/'toolkit/adm_harness_cli/adm_harness/c1_joint_sources.py',
            args.data/'transitions.json',args.data/'transition_manifest.json',
            args.data/'controls/summary.json',args.data/'controls/manifest.json',
            ROOT/spec['absolute_data']/'audit.json',ROOT/spec['response_data']/'summary.json',
            ROOT/spec['parent_summary'],ROOT/spec['parent_specification']]
    manifest=dict(workers=args.workers,input_sha256={str(p.relative_to(ROOT)):digest(p) for p in inputs},
                  output_sha256={p.name:digest(p) for p in (output,snapshot)})
    (args.data/'assessment_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':main()
