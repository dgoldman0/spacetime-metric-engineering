#!/usr/bin/env python3
"""Refine the coherent cell test with exponential transport and field reuse."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from functools import partial
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

from adm_harness.source_ledger import sha256_file
from adm_harness.virtual_cell_semigroup import solve_pair
import run_virtual_cell_transport as transport_run
from run_poynting_delivery import BASE,ROOT,write_json


def evaluate(item):
    spec,guide,envelope=item
    # The common runner retains identical geometry, target and diagnostics;
    # each worker injects only the alternate finite-volume optimization.
    transport_run.solve_pair=partial(solve_pair,guide_drift=guide,wave_envelope=envelope)
    result=transport_run.evaluate(spec)
    output=Path(spec[5]); old_label=result['label']
    new_label=old_label+('_guide_none' if guide is None else f'_guide{guide:g}')
    for suffix in ['_states.npz','_summary.json']:
        path=output/(old_label+suffix)
        if path.exists(): path.rename(output/(new_label+suffix))
    result['label']=new_label
    write_json(output/(new_label+'_summary.json'),result)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--workers',type=int,default=3)
    parser.add_argument('--centers',type=float,nargs='+',default=[-2.,-1.975])
    parser.add_argument('--width',type=float,default=.0005)
    parser.add_argument('--intervals',type=int,default=24)
    parser.add_argument('--stride',type=int,default=1)
    parser.add_argument('--guides',type=float,nargs='+',default=[0.,.5])
    parser.add_argument('--efficiency',type=float,default=.98)
    parser.add_argument('--sigma',type=float,default=1e-7)
    parser.add_argument('--reserve',type=float,default=.002)
    parser.add_argument('--output-name',default='virtual_cell_semigroup')
    parser.add_argument('--envelope',action='store_true')
    args=parser.parse_args(); output=BASE/args.output_name
    if output.exists(): raise RuntimeError('preserve completed exponential transport evidence')
    source=BASE/'joint_refined_response/manifest.json'; previous=json.loads(source.read_text())
    hashes=dict(previous['input_sha256'])
    path=source.parent/'members_fraction0.99_states.npz'
    if sha256_file(path)!=previous['output_sha256'][path.name]: raise RuntimeError('changed target')
    files=[source,path,Path(__file__),Path(transport_run.__file__),
        ROOT/'toolkit/adm_harness_cli/adm_harness/virtual_cell_transport.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/virtual_cell_semigroup.py',
        ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_semigroup.py',
        ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_transport.py',
        Path(__file__).with_name('audit_joint_dense_work.py')]
    for p in files: hashes[str(p.relative_to(ROOT))]=sha256_file(p)
    for relative,expected in hashes.items():
        if sha256_file(ROOT/relative)!=expected: raise RuntimeError('changed dependency: '+relative)
    output.mkdir()
    # Separate subdirectories prevent same-target guide variants from writing
    # through the common runner's original case name concurrently.
    specs=[]
    for center in args.centers:
        for guide in args.guides:
            case=output/f'x{center:g}_guide{guide:g}'; case.mkdir()
            spec=(args.width,args.intervals,args.stride,args.efficiency,args.sigma,
                  str(case),center,True,True,args.reserve)
            specs.append((spec,None if guide==0 else guide,args.envelope))
    with ProcessPoolExecutor(max_workers=max(1,min(args.workers,len(specs))),
                             mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,specs))
    # Flatten only after all independent calculations have finished.
    for case in sorted(output.iterdir()):
        if case.is_dir():
            for p in case.iterdir(): p.rename(output/p.name)
            case.rmdir()
    write_json(output/'summary.json',dict(cases=results))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes,output_sha256={p.name:sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__=='__main__': main()
