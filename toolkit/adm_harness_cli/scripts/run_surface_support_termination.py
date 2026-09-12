#!/usr/bin/env python3
"""Test finite-inventory surface terminations against the active rail end loads."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
import json
import multiprocessing
import subprocess

import numpy as np

from adm_harness.pressure_linked_storage import fluid_coefficients
from adm_harness.source_ledger import sha256_file
from adm_harness.surface_support_termination import minimum_surface_inventory
from audit_joint_support import bilinear
from run_joint_backing_link import JointHistory
from run_poynting_delivery import BASE,ROOT,write_json

OUTPUT=BASE/'surface_support_termination'
INPUTS=[BASE/'joint_component_cone/separate_members_scheduled_states.npz',
        BASE/'joint_spacetime_support/n64_stride4_fraction0.9_shared_states.npz']


def evaluate(spec):
    path,fraction=spec;path=Path(path);h=JointHistory(32,8)
    with np.load(path) as z:state={k:z[k] for k in z.files}
    old=h.reference.h.state
    edges=np.unique(np.r_[state['t'],old['t']])
    t=np.r_[(edges[:-1,None]+np.diff(edges)[:,None]*np.arange(8)/8).ravel(),edges[-1]]
    x=state['x'][[0,-1]]
    c=fluid_coefficients(h.reference.h.model,t,x)
    u=bilinear(old['t'],old['x'],old['thermal'],t,x)[0]
    pr=bilinear(state['t'],state['x'],state['radial_volume'],t,x)[0]
    H=bilinear(old['t'],old['x'],old['flux_energy'],t,x)[0]
    share,unused=h.allocation(x)
    # The normal magnetic guide field G continues across the jacket, so its
    # radial traction cancels in the jump. The capacitor field H-S terminates
    # on charge; work waves retain their separate continuous transport ports.
    jump=(u/3+pr)/c['rest_volume']-(H-share)/c['radius']**4
    results=[];arrays=dict(t=t,x=x,pressure_jump=jump)
    for j,end in enumerate(('left','right')):
        r=minimum_surface_inventory(t,c['radius'][:,j],c['acceleration'][:,j],
            c['angular_gradient'][:,j],jump[:,j],outward_sign=(-1.,1.)[j],stress_fraction=fraction)
        summary={k:v for k,v in r.items() if not isinstance(v,np.ndarray)}
        summary.update(end=end,stress_fraction=fraction)
        if r['success']:
            summary.update(initial_surface_rest=float(4*np.pi*r['surface_energy'][0]),
                           final_surface_rest=float(4*np.pi*r['surface_energy'][-1]),
                           peak_surface_energy_density=float(np.max(r['surface_energy']/c['radius'][:,j]**2)))
            arrays[end+'_surface_energy']=r['surface_energy'];arrays[end+'_surface_angular_stress']=r['surface_angular_stress']
        results.append(summary)
    label=path.parent.name+'_'+path.stem+'_fraction'+str(fraction)
    summary=dict(label=label,input=str(path.relative_to(ROOT)),time_samples=len(t),ends=results,
                 continuing_guide_traction_matched=True,finite_thickness_construction_supplied=False)
    write_json(OUTPUT/(label+'_summary.json'),summary)
    np.savez_compressed(OUTPUT/(label+'_states.npz'),**arrays)
    print(label+': '+json.dumps(results),flush=True)
    return summary


def main():
    if OUTPUT.exists():raise RuntimeError('preserve completed termination evidence')
    paths=[*INPUTS,Path(__file__),ROOT/'toolkit/adm_harness_cli/adm_harness/surface_support_termination.py',
           ROOT/'toolkit/adm_harness_cli/tests/test_surface_support_termination.py',
           BASE/'joint_component_cone/manifest.json',BASE/'joint_spacetime_support/manifest.json']
    hashes={str(p.relative_to(ROOT)):sha256_file(p) for p in paths}
    for previous in paths[-2:]:
        m=json.loads(previous.read_text())
        for name,expected in m['input_sha256'].items():
            if sha256_file(ROOT/name)!=expected:raise RuntimeError('changed termination input: '+name)
            hashes[name]=expected
    OUTPUT.mkdir()
    with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,[(str(p),f) for p in INPUTS for f in (1.,.9)]))
    write_json(OUTPUT/'summary.json',dict(cases=results))
    write_json(OUTPUT/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes,output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__=='__main__':main()
