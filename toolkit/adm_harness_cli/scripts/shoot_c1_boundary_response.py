#!/usr/bin/env python3
"""Independent shooting integral of finite child-minus-parent scalar states."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import argparse
import json
import multiprocessing
import shutil

import numpy as np
from numpy.polynomial.legendre import leggauss

from adm_harness.c1_angular_absolute import AbsoluteComparison
from screen_c1_angular_response import ROOT,digest,load_chart,verify_manifest


def run(task):
    spec,base,eta,level,output=task;g=load_chart(spec);x=base['coordinate']
    a=float(g.jets(np.array([x]))[1][0]);maximum=(16 if level==0 else 24)/(a*base['minimum_optical_distance'])
    q=32 if level==0 else 48;spacing=.005 if level==0 else .0025;phase=.01 if level==0 else .005
    nodes,weights=leggauss(q);edges=[0.,min(.25,maximum)]
    while edges[-1]<maximum:edges.append(min(maximum,2*edges[-1]))
    w=np.concatenate([lo+(nodes+1)*(hi-lo)/2 for lo,hi in zip(edges[:-1],edges[1:])])
    measure=np.concatenate([weights*(hi-lo)/2 for lo,hi in zip(edges[:-1],edges[1:])])
    j=np.arange(base['angular_max']+1)
    parent=AbsoluteComparison(g,base['domain'],x,spacing)
    child=AbsoluteComparison(g,base['compartment_domain'],x,spacing)
    delta=child.differences(w[None,:],j[:,None],0.,phase_step=phase,single_mass=True)
    delta-=parent.differences(w[None,:],j[:,None],0.,phase_step=phase,single_mass=True)
    harmonic=eta*np.einsum('jwk,w->jk',delta,measure)*(2*j[:,None]+1)/(4*np.pi**2)
    tensor=harmonic.sum(axis=0);artifact=f'shooting_{x:.12f}_{level}.npz'
    np.savez_compressed(Path(output)/artifact,harmonic_tensor=harmonic)
    return dict(coordinate=x,division=.3,level=level,proper_spacing=spacing,phase_step=phase,
        local_frequency_max=maximum,frequency_order=q,angular_max=base['angular_max'],
        tensor_per_real_field=tensor.tolist(),trace_difference=float(-tensor[0]+tensor[1]+2*tensor[2]),
        tail_last_quarter=harmonic[3*len(j)//4:].sum(axis=0).tolist(),artifact=artifact,
        finite_volume_reference=base['tensor_per_real_field'])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data',type=Path,default=ROOT/'supporting_reports/data/c1_population_boundary')
    p.add_argument('--workers',type=int,default=4);args=p.parse_args()
    out=args.data/'shooting_response'
    if args.workers<1 or (out.exists() and any(out.iterdir())):p.error('positive workers and empty output required')
    verified=verify_manifest(args.data/'manifest.json');s=json.loads((args.data/'summary.json').read_text())
    spec_path=ROOT/'toolkit/adm_harness_cli/specs/c1_joint_sources.json';spec=json.loads(spec_path.read_text())
    tasks=[]
    for x in (.2768310546875,.4,.5178507081509361):
        base=next(r for r in s['response'] if r['division']==.3 and r['coordinate']==x and r['name']=='fine')
        for level in (0,1):tasks.append((spec,base,s['eta'],level,str(out)))
    out.mkdir(exist_ok=True)
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
        values=list(pool.map(run,tasks))
    (out/'summary.json').write_text(json.dumps(dict(verified_input_hashes=verified,cases=values),indent=2)+'\n')
    script=Path(__file__).resolve();snapshot=out/('execution_'+script.name);shutil.copy2(script,snapshot)
    inputs=[script,spec_path,args.data/'manifest.json',args.data/'summary.json',
            ROOT/'toolkit/adm_harness_cli/adm_harness/c1_angular_absolute.py',
            ROOT/'toolkit/adm_harness_cli/adm_harness/c1_angular_absolute_kernel.c']
    manifest=dict(workers=args.workers,input_sha256={str(p.relative_to(ROOT)):digest(p) for p in inputs},
                  output_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(values,indent=2))


if __name__=='__main__':main()
