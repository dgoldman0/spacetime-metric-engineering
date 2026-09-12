#!/usr/bin/env python3
"""Test existing angular jackets against the two directed-store histories."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess
import numpy as np

from adm_harness.source_ledger import sha256_file
from adm_harness.surface_support_termination import minimum_surface_inventory
from audit_joint_dense_work import DenseHistory
from run_poynting_delivery import BASE,ROOT,write_json


def audit(path):
    path=Path(path); meta=json.loads(path.with_name(path.name.replace('_states.npz','_summary.json')).read_text())
    with np.load(path) as z: state={k:z[k] for k in z.files}
    t=state['t']; cuts=state['edges'][[0,-1]]
    history=DenseHistory('routed_family',ROOT/meta['input']); c=history.coefficients(t,cuts)
    density=history.energy(cuts).evaluate(t)[0]/c['D']; p=history.pressure(t,cuts)[0]; q=c['Q']/c['D']
    # Preserve the registered fixed material weights at the physical cuts.
    dx=state['edges'][1]-state['edges'][0]
    normalization=4*np.pi*dx*np.sum(state['D'][0])
    buffer=state['reservoir_energy'][:,None]*c['D'][0]/(normalization*c['D'])
    core=np.maximum(state['amplitude'][:,[0,-1]],0.)/c['radius']**2
    # Grant every remaining radial field to axial restraint. Positive route
    # pressures and all separate attachment/host mass remain omitted here.
    max_field=np.maximum((density-p+q-2*core-buffer)/3,0.)
    residual=np.maximum(buffer-core-max_field,0.)
    results=[]
    for j,side in enumerate(['left','right']):
        gate=minimum_surface_inventory(t,c['radius'][:,j],c['acceleration'][:,j],
            c['angular_gradient'][:,j],residual[:,j],outward_sign=-1. if j==0 else 1.)
        summary={k:v for k,v in gate.items() if not isinstance(v,np.ndarray)}
        summary.update(side=side,x=float(cuts[j]),maximum_residual_pressure=float(residual[:,j].max()))
        results.append(summary)
    return dict(label=meta['label'],center=meta['center'],cuts=results,
        scope='existing directed-store histories after maximum radial field reuse; spherical angular jackets',
        cell_controls_reoptimized=False,full_connected_support_excluded=False)


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--output-name',default='virtual_cell_jacket_crosscheck')
    args=parser.parse_args(); source=BASE/'virtual_cell_joint_reservoir'; output=BASE/args.output_name
    if output.exists(): raise RuntimeError('preserve completed jacket crosscheck')
    parent=source/'manifest.json'; previous=json.loads(parent.read_text())
    background=BASE/'joint_refined_response/manifest.json'
    hashes=dict(json.loads(background.read_text())['input_sha256'])
    paths=sorted(source.glob('*_store_radial_stream_states.npz'))
    for path in paths:
        for p in [path,path.with_name(path.name.replace('_states.npz','_summary.json'))]:
            if sha256_file(p)!=previous['output_sha256'][p.name]: raise RuntimeError('changed stored history')
            hashes[str(p.relative_to(ROOT))]=sha256_file(p)
    for p in [parent,background,Path(__file__),Path(__file__).with_name('audit_joint_dense_work.py'),
              ROOT/'toolkit/adm_harness_cli/adm_harness/surface_support_termination.py']:
        hashes[str(p.relative_to(ROOT))]=sha256_file(p)
    for relative,expected in hashes.items():
        if sha256_file(ROOT/relative)!=expected: raise RuntimeError('changed dependency: '+relative)
    output.mkdir()
    with ProcessPoolExecutor(max_workers=max(1,min(args.workers,len(paths))),
                             mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(audit,map(str,paths)))
    write_json(output/'summary.json',dict(cases=results))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes,output_sha256={'summary.json':sha256_file(output/'summary.json')}))


if __name__=='__main__': main()
