#!/usr/bin/env python3
"""Read-only state audit of total heat contact and photon receiver temperature."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

import numpy as np
from numpy.polynomial.legendre import leggauss

from adm_harness.source_ledger import sha256_file
from adm_harness.thermal_receiver_contact import photon_contact_interval
from audit_joint_dense_work import DenseHistory
from run_poynting_delivery import BASE,ROOT,write_json


def integrated_loss(history,t,x,order=8):
    z,w=leggauss(order)
    cuts=np.unique(np.r_[t,history.h.reference.h.state['t']])
    cuts=cuts[(cuts>=t[0])&(cuts<=t[-1])]
    at=(cuts[:-1,None]+np.diff(cuts)[:,None]*(z+1)/2).ravel()
    values=[];proper=[]
    for start in range(0,len(at),32):
        c=history.coefficients(at[start:start+32],x)
        values.append(c['lapse']*c['D']*(-c['field_power']-c['wave_power']))
        proper.append(c['lapse'])
    weight=np.diff(cuts)[:,None,None]*w[None,:,None]/2
    loss=np.sum(np.concatenate(values).reshape(len(cuts)-1,order,len(x))*weight,axis=1)
    time=np.sum(np.concatenate(proper).reshape(len(cuts)-1,order,len(x))*weight,axis=1)
    owner=np.searchsorted(t,(cuts[:-1]+cuts[1:])/2)-1
    output=np.zeros((len(t)-1,len(x)));duration=output.copy()
    np.add.at(output,owner,loss);np.add.at(duration,owner,time)
    return output,duration


def evaluate(spec):
    path,output=map(Path,spec)
    with np.load(path) as z:s={k:z[k] for k in z.files}
    h=DenseHistory('routed_family',BASE/'joint_refined_response/members_fraction0.99_states.npz')
    t,x=s['t'],s['x'];tm=(t[:-1]+t[1:])/2;c=h.coefficients(tm,x)
    loss,duration=integrated_loss(h,t,x)
    heat=loss-np.diff(s['receiver_thermal_energy'],axis=0)
    power=heat/duration
    K=(s['thermal_inventory'][:-1]+s['thermal_inventory'][1:])/2
    fluid=K/c['D']**(1/3)
    receiver=(s['receiver_thermal_energy'][:-1]+s['receiver_thermal_energy'][1:])/2
    result=photon_contact_interval(power,fluid,receiver,s['fluid_particle_number'])
    cases=[]
    for j,xx in enumerate(x):
        lo,hi=float(result['lower'][j]),float(result['upper'][j])
        low=int(result['lower_witness'][j]);high=int(result['upper_witness'][j])
        def witness(i):
            return dict(time=float(tm[i]),heat_power=float(power[i,j]),
                receiver_energy=float(receiver[i,j]),fluid_temperature=float(result['fluid_temperature'][i,j]))
        cases.append(dict(x=float(xx),compatible=bool(result['compatible'][j]),
            coefficient_lower=lo if np.isfinite(lo) else None,
            coefficient_upper=hi if np.isfinite(hi) else None,
            lower_unbounded=not np.isfinite(lo),upper_unbounded=not np.isfinite(hi),
            lower_witness=witness(low),upper_witness=witness(high),
            empty_receiver_outflow_samples=int(result['zero_energy_positive_outflow'][:,j].sum())))
    label=path.stem.removesuffix('_states')
    summary=dict(label=label,input=str(path.relative_to(ROOT)),
        compatible_positions=int(result['compatible'].sum()),spatial_samples=len(x),
        all_positions_compatible=bool(result['compatible'].all()),
        total_contact_used=True,temperature_law='T_receiver**4=constant(x)*Z; T_fluid=U/(3*N_mass)',
        fixed_proper_receiver_volume=True,finite_contact_law_constructed=False,
        scope='panel-averaged total contact with midpoint thermal states',positions=cases)
    write_json(output/(label+'_summary.json'),summary)
    np.savez_compressed(output/(label+'_contact.npz'),t=t,x=x,
        converter_loss_panel=loss,proper_duration=duration,total_contact_panel_heat=heat,
        total_contact_proper_power=power,fluid_thermal_energy=fluid,receiver_thermal_energy=receiver,**result)
    print(label+': compatible '+str(summary['compatible_positions'])+'/'+str(len(x)),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--inputs',nargs='+',required=True)
    parser.add_argument('--output-name',required=True);parser.add_argument('--workers',type=int,default=2)
    args=parser.parse_args();output=BASE/args.output_name
    if output.exists():raise RuntimeError('preserve completed receiver-contact audit')
    paths=[];sources=[Path(__file__),ROOT/'toolkit/adm_harness_cli/adm_harness/thermal_receiver_contact.py',
        ROOT/'toolkit/adm_harness_cli/tests/test_thermal_receiver_contact.py',
        Path(__file__).with_name('audit_joint_dense_work.py')]
    for folder in args.inputs:
        source=BASE/folder;manifest=source/'manifest.json';record=json.loads(manifest.read_text())
        sources.append(manifest)
        for path in sorted(source.glob('*_states.npz')):
            if sha256_file(path)!=record['output_sha256'][path.name]:raise RuntimeError('changed state '+str(path))
            sources.append(path);paths.append(path)
    output.mkdir()
    before={str(p.relative_to(ROOT)):sha256_file(p) for p in sources}
    with ProcessPoolExecutor(max_workers=min(2,args.workers,len(paths)),
            mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,[(p,output) for p in paths]))
    write_json(output/'summary.json',dict(cases=results))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=before,output_sha256={p.name:sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__=='__main__':main()
