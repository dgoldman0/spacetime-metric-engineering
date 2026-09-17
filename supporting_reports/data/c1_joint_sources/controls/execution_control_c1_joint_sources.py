#!/usr/bin/env python3
"""Transition regulator controls and a coarser, independently assignable angular mesh."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import argparse
import json
import multiprocessing
import shutil

from screen_c1_angular_absolute import run_case as absolute_case
from screen_c1_angular_response import (
    ROOT, digest, load_chart, make_cases, retained_rows, run_case as response_case, verify_manifest)


def job(task):
    kind,payload=task
    return kind,(absolute_case(payload) if kind=='absolute' else response_case(payload))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec',type=Path,default=ROOT/'toolkit/adm_harness_cli/specs/c1_joint_source_controls.json')
    p.add_argument('--data',type=Path,default=ROOT/'supporting_reports/data/c1_joint_sources')
    p.add_argument('--workers',type=int,default=4);args=p.parse_args()
    control=json.loads(args.spec.read_text())
    spec=json.loads((ROOT/control['base_specification']).read_text())
    verified=verify_manifest(args.data/'transition_manifest.json')
    output=args.data/'controls'
    if args.workers<1 or (output.exists() and any(output.iterdir())):
        p.error('positive worker count and empty controls directory required')
    output.mkdir(parents=True,exist_ok=True)
    parent=json.loads((args.data/'transitions.json').read_text())
    tasks=[]
    for source in ('broad_left','shared_right'):
        inherited=next(r for r in parent['cases'] if r['source']==source)
        for mass,cut in control['transition_mass_cut_pairs']:
            case=dict(id=len(tasks),source=source,coordinate=inherited['coordinate'],domain=inherited['domain'],
                mass=mass,cut=cut,name='base',frequency_order=24,phase_step=.04,
                proper_spacing=.01,attenuation=40.,stride=1)
            tasks.append(('absolute',(spec,case,parent['calibration'],str(output))))
        case=dict(case,id=len(tasks),name='combined_numerical_control',**control['transition_numerical_control'])
        tasks.append(('absolute',(spec,case,parent['calibration'],str(output))))
    response_spec=json.loads((ROOT/'toolkit/adm_harness_cli/specs/c1_angular_response.json').read_text())
    response_spec['angular_compartment_counts']=control['additional_angular_compartment_counts']
    rows=retained_rows(spec);g=load_chart(spec)
    eta=json.loads((ROOT/spec['parent_specification']).read_text())['eta']
    for case in make_cases(response_spec,rows,g):
        if case['source']=='narrow_left':continue
        tasks.append(('response',(spec,case,eta,str(output))))
    records={'absolute':[],'response':[]}
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
        for f in as_completed([pool.submit(job,t) for t in tasks]):
            kind,row=f.result();records[kind].append(row)
            if kind=='response':
                (output/f"response_case_{row['id']:03d}.json").write_text(json.dumps(row,indent=2)+'\n')
            print(f"{sum(map(len,records.values()))}/{len(tasks)} {kind} {row['source']} "
                  f"{row.get('mass',row.get('probe_name'))} {row['name']}",flush=True)
    for values in records.values():values.sort(key=lambda r:r['id'])
    result=output/'summary.json'
    result.write_text(json.dumps(dict(verified_input_hashes=verified,**records),indent=2)+'\n')
    inputs=[args.spec,ROOT/control['base_specification'],Path(__file__).resolve(),
            ROOT/'toolkit/adm_harness_cli/scripts/screen_c1_angular_absolute.py',
            ROOT/'toolkit/adm_harness_cli/scripts/screen_c1_angular_response.py',
            ROOT/'toolkit/adm_harness_cli/specs/c1_angular_response.json',
            args.data/'transitions.json',args.data/'transition_manifest.json']
    for path in inputs[:3]:shutil.copy2(path,output/('execution_'+path.name))
    manifest=dict(workers=args.workers,input_sha256={str(p.relative_to(ROOT)):digest(p) for p in inputs},
                  output_sha256={p.name:digest(p) for p in sorted(output.iterdir()) if p.is_file()})
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':main()
