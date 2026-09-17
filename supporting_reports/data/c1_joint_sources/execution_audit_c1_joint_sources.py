#!/usr/bin/env python3
"""Independent tensor reconstruction, infeasibility witnesses and dense residual duties."""
from pathlib import Path
import argparse
import json
import shutil

import numpy as np
from scipy.optimize import linprog

from adm_harness.c1_joint_sources import PROJECTION_NAMES,radial_columns
from adm_harness.c1_signed_channels import channel_tensor, dec_projections, einstein_source
from assess_c1_joint_sources import angular_columns, library
from screen_c1_angular_response import ROOT,digest,load_chart,retained_rows,verify_manifest
from screen_c1_signed_channels import fields


def supplied_radial(chart,x,row,central,eta):
    total=np.zeros((len(x),3))
    for p,charges in zip(row['partitions'],central):
        ends=np.array(p['coordinate']);lengths=np.array(p['optical_lengths'])
        # Assemble each finite cell separately, including its zero exterior
        # in this interior source ledger.
        for j,c in enumerate(charges):
            total+=channel_tensor(chart,x,ends[j:j+2],lengths[j:j+1],strength=eta*c)
    return total


def spatial_checks(data,spec,lib,g):
    spatial=json.loads((data/'spatial/assessment.json').read_text())
    verified=verify_manifest(data/'spatial/assessment_manifest.json')
    x=np.array(spatial['coordinate']);eta=lib['eta'];unit=spec['charge_unit'];row=lib['row']
    original=[s for s in lib['states'] if s['count']==1]
    tensors=np.zeros((len(x),2,3));logs=np.zeros_like(tensors);errors=np.zeros((len(x),2))
    for m,state in enumerate(original):
        tensors[:4,m]=state['tensor'];logs[:4,m]=state['log_source'];errors[:4,m]=state['error']
    raw=json.loads((data/'spatial/tensors.json').read_text())['cases']
    for i,value in enumerate(spatial['limits'],4):
        tensors[i,0]=eta*np.array(value['tensor'])
        logs[i,0]=eta*np.array(next(r for r in raw if r['coordinate']==x[i])['log_source'])
        errors[i,0]=eta*max(3e-11,abs(value['trace_error']),2*max(abs(np.array(value['fit_spread']))))
    parent=json.loads((ROOT/spec['parent_specification']).read_text())
    em_spec=json.loads((ROOT/parent['parent_specification']).read_text())
    target=einstein_source(g,x)-fields(g,x,em_spec,row['overlap'])[:,None]*[1.,-1.,1.]
    records=[];artifacts=[]
    for i,case in enumerate(spatial['six_probe_cases']):
        phi=tensors-2*(case['reference_log']-1)*logs
        error=errors if case['empirical_sensitivity'] else np.zeros_like(errors)
        record={k:case[k] for k in ('reference_log','radial_mode','empirical_sensitivity')}
        record['spatial_case']=i
        if case['all_library']['feasible']:
            scalar=np.zeros_like(target);envelope=np.zeros(len(x))
            for p in case['angular_fields']:
                scalar+=p['fields']*phi[:,p['module']]
                envelope+=p['fields']*error[:,p['module']]
            radial=supplied_radial(g,x,row,case['radial_central_charges'],eta)
            material=target-radial-scalar
            err=float(abs(material-np.array(case['best']['material'])).max())
            margins=dec_projections(material)-2*envelope[:,None]
            if err>2e-12 or margins.min()<-2e-9:raise RuntimeError('six-probe reconstruction failed')
            record.update(reconstruction_error=err,minimum_margin_after_envelope=float(margins.min()),
                          material=material.tolist())
            if case['empirical_sensitivity'] and case['radial_mode']=='zones':
                lo,hi=spec['bulk_domain'];boundaries=np.concatenate([p['coordinate'] for p in row['partitions']])
                near=np.r_[boundaries-1e-9,boundaries+1e-9]
                profiles=[]
                for samples in spec['bulk_samples']:
                    xx=np.unique(np.r_[np.linspace(lo,hi,samples),x,near[(near>lo)&(near<hi)]])
                    demand=einstein_source(g,xx)-fields(g,xx,em_spec,row['overlap'])[:,None]*[1.,-1.,1.]
                    supply=supplied_radial(g,xx,row,case['radial_central_charges'],eta)
                    residual=demand-supply;projection=dec_projections(residual)
                    extrema=[]
                    for k,name in enumerate(PROJECTION_NAMES):
                        j=int(np.argmin(projection[:,k]))
                        extrema.append(dict(projection=name,coordinate=float(xx[j]),
                                            residual_before_angular=float(projection[j,k])))
                    path=data/f'six_probe_residual_{i:03d}_{samples}.npz'
                    np.savez_compressed(path,coordinate=xx,target_after_maxwell=demand,
                                        radial=supply,required_after_maxwell_and_radial=residual)
                    artifacts.append(path);profiles.append(dict(samples=samples,artifact=path.name,extrema=extrema))
                record['dense_residual_duty_controls']=profiles
        else:
            if case['radial_mode']=='fixed':
                demand=target-supplied_radial(g,x,row,row['central_charge_per_compartment'],eta)
                radial=np.empty((len(x),0,3))
            else:
                demand=target
                radial,_,_=radial_columns(g,x,row,eta,case['radial_mode'],unit)
            columns=np.concatenate([radial,unit*phi],axis=1)
            matrix=dec_projections(columns).transpose(0,2,1).reshape(4*len(x),-1)
            matrix+=np.repeat(2*np.c_[np.zeros(radial.shape[:2]),unit*error][:,None,:],4,axis=1).reshape(matrix.shape)
            bound=dec_projections(demand).ravel()-1e-10
            scale=np.maximum(np.maximum(abs(matrix).max(axis=1),abs(bound)),1e-12)
            a,b=matrix/scale[:,None],bound/scale
            dual=linprog(b,A_ub=-a.T,b_ub=np.zeros(a.shape[1]),
                         A_eq=np.ones((1,len(b))),b_eq=[1.],bounds=(0,None),method='highs')
            if not dual.success or dual.fun>=-1e-9 or min(a.T@dual.x)<-1e-8:
                raise RuntimeError('six-probe infeasibility certificate unresolved')
            record['infeasibility_certificate']=dict(weights=dual.x.tolist(),
                negative_target=float(b@dual.x),minimum_source_projection=float(min(a.T@dual.x)))
        records.append(record)
    return dict(verified_input_hashes=verified,cases=records),artifacts


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec',type=Path,default=ROOT/'toolkit/adm_harness_cli/specs/c1_joint_sources.json')
    p.add_argument('--data',type=Path,default=ROOT/'supporting_reports/data/c1_joint_sources')
    args=p.parse_args();spec=json.loads(args.spec.read_text())
    verified=sum(verify_manifest(args.data/name) for name in
                 ('transition_manifest.json','controls/manifest.json','assessment_manifest.json'))
    results=json.loads((args.data/'assessment.json').read_text())
    lib=library(spec,args.data);g=load_chart(spec);x=np.array(lib['coordinate']);row=lib['row']
    parent=json.loads((ROOT/spec['parent_specification']).read_text())
    em_spec=json.loads((ROOT/parent['parent_specification']).read_text())
    records=[];profiles=[]
    for i,case in enumerate(results['cases']):
        angular,error,metadata=angular_columns(lib,case['reference_log'],case['angular_mesh'],spec['charge_unit'])
        if not case['empirical_sensitivity']:error*=0
        record={k:case[k] for k in ('reference_log','radial_mode','angular_mesh','empirical_sensitivity')}
        record['assessment_case']=i
        if not case['all_library']['feasible']:
            if case['radial_mode']=='fixed':
                target=np.array(lib['retained_target']);radial=np.empty((len(x),0,3))
            else:
                r=lib['radial'][case['radial_mode']]
                target=np.array(lib['target'])-np.array(r['background']);radial=np.array(r['columns'])
            columns=np.concatenate([radial,angular],axis=1)
            matrix=dec_projections(columns).transpose(0,2,1).reshape(4*len(x),-1)
            matrix+=np.repeat(2*np.c_[np.zeros(radial.shape[:2]),error][:,None,:],4,axis=1).reshape(matrix.shape)
            bound=dec_projections(target).ravel()-1e-10
            scale=np.maximum(np.maximum(abs(matrix).max(axis=1),abs(bound)),1e-12)
            a,b=matrix/scale[:,None],bound/scale
            dual=linprog(b,A_ub=-a.T,b_ub=np.zeros(a.shape[1]),
                         A_eq=np.ones((1,len(b))),b_eq=[1.],bounds=(0,None),method='highs')
            if not dual.success or dual.fun>=-1e-9:
                raise RuntimeError(f'infeasibility certificate unresolved: {i}')
            y=dual.x
            if min(a.T@y)<-1e-8:raise RuntimeError('dual source sign violation')
            record['infeasibility_certificate']=dict(weights=y.tolist(),coordinates=x.tolist(),
                projection_order=PROJECTION_NAMES,negative_target=float(b@y),
                minimum_source_projection=float(min(a.T@y)),
                scope='chosen empirical error box' if case['empirical_sensitivity'] else 'nominal source library')
        else:
            radial=supplied_radial(g,x,row,case['radial_central_charges'],lib['eta'])
            scalar=np.zeros((len(x),3));empirical=np.zeros(len(x))
            rounded=np.zeros_like(scalar)
            for pop in case['angular_fields']:
                j=next(j for j,m in enumerate(metadata) if m['label']==pop['label'])
                n=pop['fields']/spec['charge_unit']
                scalar+=n*angular[:,j];empirical+=n*error[:,j]
                rounded+=np.ceil(pop['fields'])/spec['charge_unit']*angular[:,j]
            material=np.array(lib['target'])-radial-scalar
            reconstruction=float(abs(material-np.array(case['best']['material'])).max())
            margins=dec_projections(material)
            sensitive=margins-2*empirical[:,None]
            if reconstruction>2e-12 or sensitive.min()<-2e-9:
                raise RuntimeError(f'physical reconstruction failed: {i}, {reconstruction}, {sensitive.min()}')
            record.update(reconstruction_error=reconstruction,material=material.tolist(),
                dec_margins=margins.tolist(),margins_after_empirical_envelope=sensitive.tolist(),
                minimum_nominal_margin_with_integer_scalar_fields=float(dec_projections(
                    np.array(lib['target'])-radial-rounded).min()))
            if case['empirical_sensitivity']:
                # Export the source still required between samples. These are
                # residual duties, not an interpolation of the scalar RSET.
                boundaries=np.concatenate([p['coordinate'] for p in row['partitions']])
                near=np.r_[boundaries-1e-9,boundaries+1e-9]
                lo,hi=spec['bulk_domain']
                control=[]
                for samples in spec['bulk_samples']:
                    xx=np.unique(np.r_[np.linspace(lo,hi,samples),x,near[(near>lo)&(near<hi)]])
                    target=einstein_source(g,xx)-fields(g,xx,em_spec,row['overlap'])[:,None]*np.array([1.,-1.,1.])
                    current=supplied_radial(g,xx,row,case['radial_central_charges'],lib['eta'])
                    previous=supplied_radial(g,xx,row,row['central_charge_per_compartment'],lib['eta'])
                    remaining=target-current;projections=dec_projections(remaining)
                    extrema=[]
                    for k,name in enumerate(PROJECTION_NAMES):
                        idx=int(np.argmin(projections[:,k]))
                        extrema.append(dict(projection=name,coordinate=float(xx[idx]),
                            residual_before_angular=float(projections[idx,k])))
                    artifact=f'residual_{i:03d}_{samples}.npz'
                    np.savez_compressed(args.data/artifact,coordinate=xx,
                        target_after_maxwell=target,radial=current,retained_radial=previous,
                        required_after_maxwell_and_radial=remaining)
                    control.append(dict(samples=samples,actual_points=len(xx),artifact=artifact,extrema=extrema))
                record['dense_residual_duty_controls']=control
                profiles.extend(args.data/c['artifact'] for c in control)
        records.append(record)
    spatial,extra=spatial_checks(args.data,spec,lib,g);profiles+=extra
    audit=dict(verified_input_hashes=verified,cases=records,spatial_checks=spatial,
        completed_full_spatial_source=False,
        dense_array_scope='required residual after supplied Maxwell and radial tensors; angular stress between probes remains to compute')
    output=args.data/'audit.json';output.write_text(json.dumps(audit,indent=2)+'\n')
    script=Path(__file__).resolve();snapshot=args.data/('execution_'+script.name);shutil.copy2(script,snapshot)
    inputs=[script,args.data/'assessment.json',args.data/'assessment_manifest.json',
            ROOT/'toolkit/adm_harness_cli/adm_harness/c1_joint_sources.py',
            ROOT/'toolkit/adm_harness_cli/scripts/assess_c1_joint_sources.py',
            ROOT/'toolkit/adm_harness_cli/adm_harness/c1_signed_channels.py',
            ROOT/'toolkit/adm_harness_cli/scripts/screen_c1_signed_channels.py',
            ROOT/spec['reference'],ROOT/spec['parent_specification'],ROOT/spec['parent_summary'],
            args.data/'spatial/assessment.json',args.data/'spatial/assessment_manifest.json']
    manifest=dict(input_sha256={str(p.relative_to(ROOT)):digest(p) for p in inputs},
                  output_sha256={p.name:digest(p) for p in [output,snapshot]+profiles})
    (args.data/'audit_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(cases=len(records),dense_residual_profiles=len(profiles),verified_input_hashes=verified)))


if __name__=='__main__':main()
