#!/usr/bin/env python3
"""Separate joint stress-selection envelope with counted energy and ends."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

import numpy as np
import pandas as pd

from adm_harness.graded_electrothermal import maximum_null
from adm_harness.joint_support_envelope import solve_envelope
from adm_harness.source_ledger import sha256_file
from run_joint_backing_link import JointHistory
from run_poynting_delivery import BASE,ROOT,write_json

OUTPUT=BASE/'joint_support_envelope'


def evaluate(spec):
    intervals,stride,fraction,ends,frozen=spec;h=JointHistory(intervals,stride)
    label=f'n{intervals}_stride{stride}_stress{fraction:g}_{ends}'+('_fixedfluid' if frozen else '')
    r=solve_envelope(h.t,h.x,h.c,h.log_radius_t,h.thermal,h.number,h.force_rhs,h.radial_field,
                     stress_fraction=fraction,ends=ends,freeze_fluid=frozen,deadline=100.)
    summary={key:value for key,value in r.items() if not isinstance(value,np.ndarray)}
    summary.update(label=label,intervals=intervals,time_stride=stride,stress_fraction=fraction,
                   ends=ends,fluid_fixed=frozen,constitutive_law_supplied=False)
    if r['success']:
        u,m,pr,pt=(r[k] for k in ('thermal','support_energy','radial_volume','angular_volume'))
        integrate=lambda a:4*np.pi*np.trapezoid(a,h.x,axis=-1)
        vol=h.c['rest_volume'];ell=h.c['gamma']*h.c['b'];radius=h.c['radius']
        work=-(pr[1:]+pr[:-1])/2*np.diff(np.log(ell),axis=0)-(pt[1:]+pt[:-1])*np.diff(np.log(radius),axis=0)
        fluidwork=-(u[1:]+u[:-1])/6*np.diff(np.log(vol),axis=0)
        oldwork=-(h.thermal[1:]+h.thermal[:-1])/6*np.diff(np.log(vol),axis=0)
        fluidheat=np.diff(u-h.thermal,axis=0)-fluidwork+oldwork
        residual=np.diff(m,axis=0)-work+fluidheat
        traction=(u/3+pr)/vol-h.radial_field
        rows=[]
        for i,time,demand in h.phases:
            val,direction=maximum_null(r['tensor'][:,i]+h.fixed[:,i]-demand);j=int(np.argmax(val))
            rows.append(dict(time=time,required_negative_null=float(val[j]),peak_x=float(h.x[j]),
                peak_null_cosine=float(direction[j]),material_ADM=float(integrate(h.c['b'][i]*radius[i]**2*r['tensor'][0,i]))))
        summary.update(phases=rows,initial_support_rest=float(integrate(m[0])),final_support_rest=float(integrate(m[-1])),
            initial_fluid_thermal=float(integrate(u[0])),final_fluid_thermal=float(integrate(u[-1])),
            support_mechanical_input=float(integrate(np.maximum(work,0).sum(axis=0))),
            support_mechanical_output=float(integrate(np.maximum(-work,0).sum(axis=0))),
            support_internal_heat_gross=float(integrate(abs(fluidheat).sum(axis=0))),
            energy_identity_residual=float(abs(residual).max()),
            maximum_left_end_force=float(np.max(abs(traction[:,0])*4*np.pi*radius[:,0]**2)),
            maximum_right_end_force=float(np.max(abs(traction[:,-1])*4*np.pi*radius[:,-1]**2)),
            max_support_radial_pressure=float(abs(pr/vol).max()),max_support_angular_pressure=float(abs(pt/vol).max()))
        np.savez_compressed(OUTPUT/(label+'_states.npz'),t=h.t,x=h.x,thermal=u,support_energy=m,
            radial_volume=pr,angular_volume=pt,traction=traction,reference_thermal=h.thermal,
            support_work=work,internal_heat=fluidheat)
        pd.DataFrame(rows).to_csv(OUTPUT/(label+'_phases.csv'),index=False)
    write_json(OUTPUT/(label+'_summary.json'),summary)
    print(label+': '+('success '+str(r['optimal_material_null_peak']) if r['success'] else r['message']),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    if OUTPUT.exists():
        raise RuntimeError('preserve completed joint support envelope evidence')
    preceding=BASE/'joint_backing_link_continuation/manifest.json'
    hashes=json.loads(preceding.read_text())['input_sha256']
    for path in (Path(__file__),preceding,ROOT/'toolkit/adm_harness_cli/adm_harness/joint_support_envelope.py',
                 ROOT/'toolkit/adm_harness_cli/tests/test_joint_support_envelope.py'):
        hashes[str(path.relative_to(ROOT))]=sha256_file(path)
    for path,expected in hashes.items():
        if sha256_file(ROOT/path)!=expected:
            raise RuntimeError(f'changed joint envelope input: {path}')
    OUTPUT.mkdir(parents=True)
    specs=[(32,8,f,'exposed',False) for f in (1.,.5,.1)]
    specs.extend([(32,8,1.,'balanced',False),(32,8,1.,'exposed',True)])
    with ProcessPoolExecutor(max_workers=min(4,args.workers),mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,specs))
    write_json(OUTPUT/'summary.json',dict(cases=results))
    write_json(OUTPUT/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),input_sha256=hashes,
        output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__=='__main__':
    main()
