#!/usr/bin/env python3
"""Extend the absolute angular-state library to the retained transition probes."""
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import shutil
import subprocess

from screen_c1_angular_absolute import run_case
from screen_c1_angular_response import ROOT,digest,verify_manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec',type=Path,default=ROOT/'toolkit/adm_harness_cli/specs/c1_joint_sources.json')
    parser.add_argument('--output',type=Path,default=ROOT/'supporting_reports/data/c1_joint_sources')
    parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    if args.workers<1 or (args.output.exists() and any(args.output.iterdir())):
        parser.error('positive workers and empty output required')
    spec=json.loads(args.spec.read_text())
    absolute=ROOT/spec['absolute_data'];response=ROOT/spec['response_data']
    verified=verify_manifest(absolute/'manifest.json')+verify_manifest(absolute/'audit_manifest.json')
    verified+=verify_manifest(response/'manifest.json')
    parent=json.loads((absolute/'summary.json').read_text())
    states=json.loads((response/'summary.json').read_text())['cases']
    tasks=[]
    for source in ('broad_left','shared_right'):
        row=next(r for r in states if r['source']==source and r['name']=='fine'
                 and r['probe_name']=='transition_cell_center' and r['compartment_count']==8)
        for mass in spec['transition_regulator_masses']:
            for cut in spec['transition_cutoffs']:
                case=dict(id=len(tasks),source=source,coordinate=row['coordinate'],domain=row['domain'],
                    mass=mass,cut=cut,name='base',frequency_order=24,phase_step=.04,
                    proper_spacing=.01,attenuation=40.,stride=1)
                tasks.append((spec,case,parent['calibration'],str(args.output)))
    args.output.mkdir(parents=True,exist_ok=True)
    records=[]
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
        for future in as_completed([pool.submit(run_case,task) for task in tasks]):
            r=future.result();records.append(r)
            print(f"{len(records)}/{len(tasks)} {r['source']} M={r['mass']} cut={r['cut']}",flush=True)
    result=dict(specification=str(args.spec.resolve().relative_to(ROOT)),
        calibration=parent['calibration'],cases=sorted(records,key=lambda r:r['id']),verified_parent_hashes=verified)
    (args.output/'transitions.json').write_text(json.dumps(result,indent=2)+'\n')
    files=[args.spec,Path(__file__).resolve(),ROOT/'toolkit/adm_harness_cli/scripts/screen_c1_angular_absolute.py',
           ROOT/'toolkit/adm_harness_cli/adm_harness/c1_angular_absolute.py',
           ROOT/'toolkit/adm_harness_cli/adm_harness/c1_angular_absolute_kernel.c',
           absolute/'audit.json',absolute/'summary.json',response/'summary.json',ROOT/spec['reference']]
    for p in files[:2]:shutil.copy2(p,args.output/('execution_'+p.name))
    manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),workers=args.workers,
        base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256={str(p.relative_to(ROOT)):digest(p) for p in files},
        output_sha256={p.name:digest(p) for p in sorted(args.output.iterdir()) if p.is_file()})
    (args.output/'transition_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':main()
