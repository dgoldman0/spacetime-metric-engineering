#!/usr/bin/env python3
"""Actual nearby angular tensors and a small radial population-zone comparison."""
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import argparse
import json
import multiprocessing
import shutil

import numpy as np

from adm_harness.c1_joint_sources import RADIAL_ZONES,radial_columns
from adm_harness.c1_signed_channels import dec_projections,einstein_source
from audit_c1_angular_absolute import extrapolate
from audit_c1_joint_sources import supplied_radial
from assess_c1_joint_sources import add_boundary_ledger,library,solve_case
from screen_c1_angular_absolute import run_case
from screen_c1_angular_response import ROOT,digest,load_chart,remainder,verify_manifest
from screen_c1_signed_channels import fields


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec',type=Path,default=ROOT/'toolkit/adm_harness_cli/specs/c1_joint_source_spatial_check.json')
    p.add_argument('--data',type=Path,default=ROOT/'supporting_reports/data/c1_joint_sources')
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--compute-only',action='store_true');p.add_argument('--assess-only',action='store_true')
    p.add_argument('--refine-cutoffs',action='store_true')
    args=p.parse_args();control=json.loads(args.spec.read_text())
    spec=json.loads((ROOT/control['base_specification']).read_text());output=args.data/'spatial'
    if args.compute_only and args.assess_only:p.error('select only one partial stage')
    if args.workers<1:p.error('positive worker count required')
    verified=verify_manifest(args.data/'transition_manifest.json')
    parent=json.loads((args.data/'transitions.json').read_text())
    if not args.assess_only:
        work=output/'cutoff_controls' if args.refine_cutoffs else output
        if work.exists() and any(work.iterdir()):p.error('empty numerical output directory required for computation')
        work.mkdir(parents=True,exist_ok=True)
        inherited=next(r for r in parent['cases'] if r['source']=='broad_left')
        tasks=[]
        for x in control['coordinates']:
            pairs=control['mass_cut_pairs']
            if args.refine_cutoffs:
                pairs=[(mass,32.) for mass in sorted(set(m for m,c in pairs)) if [mass,32.] not in pairs]
            for mass,cut in pairs:
                case=dict(id=len(tasks)+(100 if args.refine_cutoffs else 0),source='broad_left',coordinate=x,domain=inherited['domain'],
                    mass=mass,cut=cut,name='base',frequency_order=control['frequency_order'],
                    phase_step=control['phase_step'],proper_spacing=control['proper_spacing'],
                    attenuation=40.,stride=1)
                tasks.append((spec,case,parent['calibration'],str(work)))
        records=[]
        with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
            for f in as_completed([pool.submit(run_case,t) for t in tasks]):
                r=f.result();records.append(r)
                print(f"{len(records)}/{len(tasks)} x={r['coordinate']} M={r['mass']} cut={r['cut']}",flush=True)
        (work/'tensors.json').write_text(json.dumps(dict(cases=sorted(records,key=lambda r:r['id'])),indent=2)+'\n')
        script=Path(__file__).resolve();shutil.copy2(script,work/('execution_'+script.name))
        shutil.copy2(args.spec,work/('execution_'+args.spec.name))
        inputs=[args.spec,script,args.data/'transitions.json',args.data/'transition_manifest.json',
                ROOT/'toolkit/adm_harness_cli/scripts/screen_c1_angular_absolute.py',
                ROOT/'toolkit/adm_harness_cli/adm_harness/c1_angular_absolute.py',
                ROOT/'toolkit/adm_harness_cli/adm_harness/c1_angular_absolute_kernel.c',ROOT/spec['reference']]
        manifest=dict(workers=args.workers,input_sha256={str(p.relative_to(ROOT)):digest(p) for p in inputs},
                      output_sha256={p.name:digest(p) for p in sorted(work.iterdir()) if p.is_file()})
        (work/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    if args.compute_only or args.refine_cutoffs:return
    verified+=verify_manifest(output/'manifest.json')+verify_manifest(args.data/'assessment_manifest.json')
    if tuple(map(tuple,control['radial_zones_module_lower_upper_cell_indices']))!=RADIAL_ZONES:
        raise RuntimeError('zone specification and implementation disagree')
    lib=library(spec,args.data);g=load_chart(spec);eta=lib['eta'];row=lib['row']
    samples=json.loads((output/'tensors.json').read_text())['cases']
    if (output/'cutoff_controls/manifest.json').exists():
        verified+=verify_manifest(output/'cutoff_controls/manifest.json')
        samples+=json.loads((output/'cutoff_controls/tensors.json').read_text())['cases']
    limits=[extrapolate(samples,'broad_left',x) for x in control['coordinates']]
    local=[];errors=[]
    for x,value in zip(control['coordinates'],limits):
        r=next(r for r in samples if r['coordinate']==x)
        tensor=np.array(value['tensor'])
        value.update(coordinate=x,anomaly=r['anomaly'],
            trace_error=float(-tensor[0]+tensor[1]+2*tensor[2]-r['anomaly']))
        local.append(r['log_source'])
        errors.append(eta*max(3e-11,2*max(abs(np.array(value['fit_spread']))),abs(value['trace_error'])))
    original=json.loads((args.data/'assessment.json').read_text())['cases']
    xx=np.array(control['coordinates'])
    parent_spec=json.loads((ROOT/spec['parent_specification']).read_text())
    em_spec=json.loads((ROOT/parent_spec['parent_specification']).read_text())
    target=einstein_source(g,xx)-fields(g,xx,em_spec,row['overlap'])[:,None]*[1.,-1.,1.]
    t1=eta*np.array([v['tensor'] for v in limits]);h=eta*np.array(local)
    frozen=[]
    for i,case in enumerate(original):
        if case['angular_mesh']!='module' or 'best' not in case or any(p['count']!=1 for p in case['angular_fields']):continue
        scalar=np.zeros_like(t1);error=np.zeros(len(xx))
        for population in case['angular_fields']:
            if population['module']==0:
                scalar+=population['fields']*(t1-2*(case['reference_log']-1)*h)
                error+=population['fields']*np.array(errors)
        material=target-supplied_radial(g,xx,row,case['radial_central_charges'],eta)-scalar
        frozen.append(dict(original_case=i,reference_log=case['reference_log'],radial_mode=case['radial_mode'],
            original_empirical_sensitivity=case['empirical_sensitivity'],material=material.tolist(),
            dec_margins=dec_projections(material).tolist(),
            margins_after_empirical_envelope=(dec_projections(material)-2*error[:,None]).tolist()))
    lib['coordinate']+=control['coordinates'];x=np.array(lib['coordinate'])
    lib['target']=np.r_[np.array(lib['target']),target].tolist()
    lib['retained_target']=remainder(g,x,row,parent_spec).tolist()
    lib['states']=[s for s in lib['states'] if s['count']==1]
    for state in lib['states']:
        own=state['module']==0
        state['tensor']+= (t1 if own else np.zeros_like(t1)).tolist()
        state['log_source']+=(h if own else np.zeros_like(h)).tolist()
        state['error']+=errors if own else [0.]*len(errors)
    for mode in lib['radial']:
        c,w,labels=radial_columns(g,x,row,eta,mode,spec['charge_unit'])
        lib['radial'][mode]=dict(columns=c.tolist(),weights=w.tolist(),labels=labels,
                                background=np.zeros((len(x),3)).tolist())
    six=[]
    for ell in spec['reference_logs']:
        for mode in spec['radial_modes']+['zones']:
            for sensitive in (False,True):
                r=solve_case((lib,ell,mode,'module',sensitive,spec['charge_unit']))
                add_boundary_ledger(r,lib,spec);six.append(r)
    result=dict(verified_input_hashes=verified,coordinate=x.tolist(),limits=limits,
                frozen_four_probe_witnesses=frozen,six_probe_cases=six,
                geometry_or_existing_boundaries_changed=False,
                full_spatial_source_and_material_closure=False)
    report=output/'assessment.json';report.write_text(json.dumps(result,indent=2)+'\n')
    inputs=[args.spec,Path(__file__).resolve(),output/'tensors.json',output/'manifest.json',
            args.data/'assessment.json',args.data/'assessment_manifest.json',
            ROOT/'toolkit/adm_harness_cli/scripts/assess_c1_joint_sources.py',
            ROOT/'toolkit/adm_harness_cli/adm_harness/c1_joint_sources.py']
    if (output/'cutoff_controls/manifest.json').exists():
        inputs.extend([output/'cutoff_controls/tensors.json',output/'cutoff_controls/manifest.json'])
    manifest=dict(input_sha256={str(p.relative_to(ROOT)):digest(p) for p in inputs},
                  output_sha256={report.name:digest(report)})
    (output/'assessment_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(frozen_checked=len(frozen),six_probe_cases=len(six),
                         nominal_or_empirical_feasible=sum(r['all_library']['feasible'] for r in six))))


if __name__=='__main__':main()
