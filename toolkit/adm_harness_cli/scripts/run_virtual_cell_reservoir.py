#!/usr/bin/env python3
"""Jointly optimize a shared reservoir and both coherent support cells."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

from adm_harness.source_ledger import sha256_file
from adm_harness.virtual_cell_semigroup import solve_pair
import run_virtual_cell_transport as common
from run_poynting_delivery import BASE, ROOT, write_json


EOS={'rest':(0.,0.),'radiation':(1/3,1/3),'radial_stream':(1.,0.),'confined_radial_stream':(1.,0.)}


def evaluate(item):
    spec,kind=item
    common.solve_pair=partial(solve_pair,guide_drift=.5,reservoir_eos=EOS[kind],
                             confine_reservoir=kind=='confined_radial_stream')
    result=common.evaluate(spec)
    output=Path(spec[5]); old=result['label']; new=old+'_store_'+kind
    for suffix in ['_states.npz','_summary.json']:
        path=output/(old+suffix)
        if path.exists(): path.rename(output/(new+suffix))
    result.update(label=new,reservoir_kind=kind,
        scope='joint necessary comparison: coherent phase cells, waves, mixed shared inventory, heat export',
        stored_energy_and_pressure_counted=True,
        reservoir_internal_transport_supplied=False,
        reservoir_confinement_and_host_mass_supplied=False,
        heat_destination='existing endpoint heat medium; counted return stream, receiver remains external',
        posthoc_closed_buffer_fields='legacy diagnostic for additional rest inventory, separate from optimized reservoir')
    write_json(output/(new+'_summary.json'),result)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--centers',type=float,nargs='+',default=[-2.,-1.975])
    parser.add_argument('--kinds',choices=list(EOS),nargs='+',default=['rest','radiation','radial_stream'])
    parser.add_argument('--width',type=float,default=.0005)
    parser.add_argument('--intervals',type=int,default=24)
    parser.add_argument('--stride',type=int,default=1)
    parser.add_argument('--output-name',default='virtual_cell_joint_reservoir')
    args=parser.parse_args(); output=BASE/args.output_name
    if output.exists(): raise RuntimeError('preserve completed joint reservoir evidence')
    source=BASE/'joint_refined_response/manifest.json'; previous=json.loads(source.read_text())
    hashes=dict(previous['input_sha256']); path=source.parent/'members_fraction0.99_states.npz'
    if sha256_file(path)!=previous['output_sha256'][path.name]: raise RuntimeError('changed target')
    files=[source,path,Path(__file__),Path(common.__file__),
        ROOT/'toolkit/adm_harness_cli/adm_harness/virtual_cell_transport.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/virtual_cell_semigroup.py',
        ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_reservoir.py',
        Path(__file__).with_name('audit_joint_dense_work.py')]
    for p in files: hashes[str(p.relative_to(ROOT))]=sha256_file(p)
    for relative,expected in hashes.items():
        if sha256_file(ROOT/relative)!=expected: raise RuntimeError('changed dependency: '+relative)
    output.mkdir(); specs=[]
    for center in args.centers:
        for kind in args.kinds:
            case=output/f'x{center:g}_{kind}'; case.mkdir()
            spec=(args.width,args.intervals,args.stride,.98,1e-7,str(case),center,True,True,.002)
            specs.append((spec,kind))
    with ProcessPoolExecutor(max_workers=max(1,min(args.workers,len(specs))),
                             mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,specs))
    for case in sorted(output.iterdir()):
        if case.is_dir():
            for p in case.iterdir(): p.rename(output/p.name)
            case.rmdir()
    write_json(output/'summary.json',dict(cases=results))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes,output_sha256={p.name:sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__=='__main__': main()
