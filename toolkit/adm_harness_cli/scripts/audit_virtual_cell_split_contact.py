#!/usr/bin/env python3
"""Photon-temperature intervals for separately rated hot and cold receivers."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

import numpy as np

from adm_harness.source_ledger import sha256_file
from adm_harness.thermal_receiver_contact import photon_contact_interval
from audit_joint_dense_work import DenseHistory
from run_poynting_delivery import BASE,ROOT,write_json


def evaluate(spec):
    path,output=map(Path,spec)
    with np.load(path) as z:s={k:z[k] for k in z.files}
    h=DenseHistory('routed_family',BASE/'joint_refined_response/members_fraction0.99_states.npz')
    t,x=s['t'],s['x'];tm=(t[:-1]+t[1:])/2;c=h.coefficients(tm,x)
    midpoint=lambda a:(a[:-1]+a[1:])/2
    fluid=midpoint(s['thermal_inventory'])/c['D']**(1/3)
    duration=s['receiver_contact_proper_duration']
    hot=midpoint(s['receiver_hot_energy']);cold=midpoint(s['receiver_cold_energy'])
    minimum_energy=float(min(hot.min(),cold.min(),fluid.min()))
    if minimum_energy < -1e-9:
        raise ValueError('thermal energy negativity exceeds the diagnostic roundoff tolerance')
    hot_physical=np.maximum(hot,0);cold_physical=np.maximum(cold,0)
    qh=s['receiver_hot_contact_panel_heat']/duration
    qc=s['receiver_cold_contact_panel_heat']/duration
    rh=photon_contact_interval(qh,fluid,hot,s['fluid_particle_number'])
    rc=photon_contact_interval(-qc,fluid,cold,s['fluid_particle_number'])
    lo=float(rh['lower'].max());hi=float(rc['upper'].min())
    ok=bool(rh['compatible'].all() and rc['compatible'].all() and np.isfinite(lo) and hi>0)
    summary=dict(input=str(path.relative_to(ROOT)),spatial_samples=len(x),
        hot_compatible_positions=int(rh['compatible'].sum()),cold_compatible_positions=int(rc['compatible'].sum()),
        common_pair_temperature_coefficients_possible=ok,
        maximum_negative_thermal_roundoff=max(0.,-minimum_energy),
        hot_coefficient_lower=lo if np.isfinite(lo) else None,
        cold_coefficient_upper=hi if np.isfinite(hi) else None,
        cold_upper_unbounded=not np.isfinite(hi),
        scope='midpoint photon temperatures and panel heat rates; physical packing and optical coupling remain open')
    arrays=dict(t=t,x=x,fluid_thermal_energy=fluid,hot_energy=hot,cold_energy=cold,
        hot_contact_power=qh,cold_contact_power=qc,hot_coefficient_lower=rh['lower'],
        cold_coefficient_upper=rc['upper'])
    if ok:
        ah=max(2*lo,1e-20);ac=min(hi/2,ah/4)
        temperature=rh['fluid_temperature'];fourth=temperature**4
        h_active=rh['positive'];c_active=rc['negative']
        hot_gap=ah*hot_physical-fourth;cold_gap=fourth-ac*cold_physical
        gh=np.divide(qh,hot_gap,out=np.zeros_like(qh),where=h_active)
        gc=np.divide(qc,cold_gap,out=np.zeros_like(qc),where=c_active)
        summary.update(selected_hot_coefficient=ah,selected_cold_coefficient=ac,
            minimum_cold_to_hot_volume_ratio=lo/hi if np.isfinite(hi) else 0.,
            selected_cold_to_hot_volume_ratio=ah/ac,
            maximum_hot_radiative_conductance=float(gh.max()),maximum_cold_radiative_conductance=float(gc.max()),
            maximum_hot_energy_turnover=float((gh*ah).max()),
            maximum_fluid_energy_turnover=float(np.divide(qc,fluid,out=np.zeros_like(qc),where=c_active).max()),
            positive_hot_contact_at_zero_fluid_temperature=int((h_active&(fluid==0)).sum()),
            maximum_hot_temperature=float((ah*hot_physical).max()**.25),
            maximum_cold_temperature=float((ac*cold_physical).max()**.25))
        arrays.update(fluid_temperature=temperature,hot_temperature=(ah*hot_physical)**.25,
            cold_temperature=(ac*cold_physical)**.25,hot_radiative_conductance=gh,cold_radiative_conductance=gc)
    if any(not np.isfinite(v).all() for k,v in arrays.items()
           if k not in ('hot_coefficient_lower','cold_coefficient_upper')):
        raise ArithmeticError('nonfinite reconstructed physical state')
    label=path.stem.removesuffix('_states')
    write_json(output/(label+'_summary.json'),summary)
    np.savez_compressed(output/(label+'_contact.npz'),**arrays)
    print(label+': '+json.dumps({k:summary[k] for k in ('common_pair_temperature_coefficients_possible',
        'hot_coefficient_lower','cold_coefficient_upper')}),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--inputs',nargs='+',required=True)
    parser.add_argument('--output-name',required=True);parser.add_argument('--workers',type=int,default=2)
    args=parser.parse_args();output=BASE/args.output_name
    if output.exists():raise RuntimeError('preserve completed split-contact audit')
    sources=[Path(__file__),ROOT/'toolkit/adm_harness_cli/adm_harness/thermal_receiver_contact.py',
             Path(__file__).with_name('audit_joint_dense_work.py')];paths=[]
    for folder in args.inputs:
        source=BASE/folder;manifest=source/'manifest.json';m=json.loads(manifest.read_text());sources.append(manifest)
        for p in sorted(source.glob('*_states.npz')):
            if sha256_file(p)!=m['output_sha256'][p.name]:raise RuntimeError('changed input state')
            sources.append(p);paths.append(p)
    output.mkdir();before={str(p.relative_to(ROOT)):sha256_file(p) for p in sources}
    with ProcessPoolExecutor(max_workers=min(2,args.workers,len(paths)),
            mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,[(p,output) for p in paths]))
    write_json(output/'summary.json',dict(cases=results))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=before,output_sha256={p.name:sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__=='__main__':main()
