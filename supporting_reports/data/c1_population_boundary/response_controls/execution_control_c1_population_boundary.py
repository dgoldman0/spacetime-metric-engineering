#!/usr/bin/env python3
"""Resolve finite angular state differences nearest the trial wall at x=0.3."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import argparse
import json
import multiprocessing
import shutil

from screen_c1_angular_response import ROOT,digest,run_case


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,default=ROOT/'supporting_reports/data/c1_population_boundary')
    p.add_argument('--workers',type=int,default=2);args=p.parse_args()
    output=args.data/'response_controls'
    if args.workers<1 or (output.exists() and any(output.iterdir())):
        p.error('positive workers and empty control directory required')
    spec_path=ROOT/'toolkit/adm_harness_cli/specs/c1_joint_sources.json'
    spec=json.loads(spec_path.read_text());eta=json.loads((ROOT/spec['parent_specification']).read_text())['eta']
    records=[json.loads(p.read_text()) for p in args.data.glob('response_case_*.json')]
    tasks=[];inputs=[]
    for x in (.2768310546875,.4,.5178507081509361):
        base=next(r for r in records if r['division']==.3 and r['coordinate']==x and r['name']=='fine')
        inputs.append(args.data/f"response_case_{base['id']:03d}.json")
        for nodes,freq in ((32769,160),(65537,200)):
            case=dict(base,id=len(tasks),name=f'resolution_{nodes}',nodes=nodes,frequency_nodes=freq)
            tasks.append((spec,case,eta,str(output)))
    output.mkdir(parents=True,exist_ok=True)
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(run_case,tasks))
    (output/'summary.json').write_text(json.dumps(dict(cases=results),indent=2)+'\n')
    script=Path(__file__).resolve();snapshot=output/('execution_'+script.name);shutil.copy2(script,snapshot)
    inputs += [spec_path,script,ROOT/'toolkit/adm_harness_cli/scripts/screen_c1_angular_response.py',
               ROOT/'toolkit/adm_harness_cli/adm_harness/c1_angular_response.py']
    manifest=dict(workers=args.workers,input_sha256={str(p.relative_to(ROOT)):digest(p) for p in inputs},
                  output_sha256={p.name:digest(p) for p in output.iterdir() if p.is_file()})
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps([dict(coordinate=r['coordinate'],nodes=r['nodes'],ward=r['ward_residual_times_radius_over_tensor']) for r in results]))


if __name__=='__main__':main()
