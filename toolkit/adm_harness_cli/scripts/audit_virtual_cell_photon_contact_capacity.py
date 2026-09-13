#!/usr/bin/env python3
"""Favorable passive-port capacity and grey-contact recoil comparison.

The existing bidirectional gapless modes have one-way flux c_eq/2 in c=1
units. Symmetric access at both ends of a physical cell of proper length l
gives kappa_j=tau_j/l. The comparison l*(kappa_h+kappa_c)<=1 allocates a
shared passive transmission budget. It supplies neither a scattering
network nor its material, switching, bypass-heat, or mode-isolation costs.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess
import sys

import numpy as np

from adm_harness.source_ledger import sha256_file
from audit_joint_dense_work import DenseHistory
from audit_virtual_cell_ports import validate_controls
from audit_virtual_cell_thermal_replay import geometry
from run_poynting_delivery import BASE, ROOT, write_json


def passive_port_capacity(hot_heat,cold_heat,duration,volume,length,
                          hot_gap,cold_gap,current,density):
    values=np.broadcast_arrays(*[np.asarray(v,float) for v in
        (hot_heat,cold_heat,duration,volume,length,hot_gap,cold_gap,current,density)])
    ph,pc,dt,D,ell,gh,gc,j,c=values
    if (ph.ndim!=2 or not all(np.isfinite(v).all() for v in values)
            or np.any(ph<0) or np.any(pc<0) or np.any(dt<=0) or np.any(D<=0)
            or np.any(ell<=0) or np.any(c<0)):
        raise ValueError('finite physical panel arrays and positive scales required')
    valid=(~((ph>0)&(gh<=0)) & ~((pc>0)&(gc<=0)) & (abs(j)<=c+1e-10))
    with np.errstate(divide='ignore',over='ignore',invalid='ignore'):
        kh=np.divide(ph,D*dt*gh,out=np.where(ph>0,np.inf,0.),where=gh>0)
        kc=np.divide(pc,D*dt*gc,out=np.where(pc>0,np.inf,0.),where=gc>0)
    finite=np.isfinite(kh)&np.isfinite(kc)
    with np.errstate(over='ignore',invalid='ignore'):
        total=ell*(kh+kc)
        recoil=(kh+kc)*j
        residual=D*dt*(kh*gh-kc*gc)-(ph-pc)
    return dict(hot_coefficient=kh,cold_coefficient=kc,
        hot_transmission_budget=ell*kh,cold_transmission_budget=ell*kc,
        total_transmission_budget=total,material_recoil_force_density=recoil,
        photon_power_residual=residual,
        state_and_gap_valid=valid&finite,
        capacity_pass=valid&finite&(total<=1.+1e-10))


def finite(v):
    return float(v) if np.isfinite(v) else None


def reciprocal_star(hot,cold):
    """Instantaneous reciprocal lossless junction of three real-impedance lines.

    p_i are normalized line admittances; S=2 sqrt(p) sqrt(p)^T-I. The
    higher-p0 root minimizes the direct hot/cold bypass for prescribed
    transmissions from the cell line to the two bank lines.
    """
    hot,cold=np.broadcast_arrays(np.asarray(hot,float),np.asarray(cold,float))
    valid=np.isfinite(hot)&np.isfinite(cold)&(hot>=0)&(cold>=0)&(hot+cold<=1)
    with np.errstate(invalid='ignore',divide='ignore'):
        p0=(1+np.sqrt(1-hot-cold))/2
        p=np.stack((p0,hot/(4*p0),cold/(4*p0)),axis=-1)
        v=np.sqrt(p)
        matrix=2*v[..., :,None]*v[...,None,:]-np.eye(3)
        bypass=hot*cold/(4*p0*p0)
    return dict(valid=valid,admittance_fractions=p,scattering_matrix=matrix,
        direct_bank_transmission=bypass)


def evaluate(spec):
    folder,label,output=spec;folder,output=Path(folder),Path(output)
    meta=json.loads((folder/(label+'_summary.json')).read_text())
    with np.load(folder/(label+'_temperature.npz')) as f:s={k:f[k] for k in f.files}
    replay=ROOT/meta['input']
    replay_meta=json.loads(replay.with_name(replay.stem.removesuffix('_states')+'_summary.json').read_text())
    with np.load(replay) as f:
        edges=f['edges'];rated=f['receiver_rated_capacity']
        old_hot=f['receiver_hot_energy'];old_cold=f['receiver_cold_energy']
    physical_width=(float(edges[-1])-float(edges[0]))/2
    if physical_width<=0:raise ValueError('positive physical half-cell width required')
    history=DenseHistory('routed_family',ROOT/replay_meta['input'])
    ph,pc,dt=[s[k] for k in ('photon_hot_panel_heat','photon_cold_panel_heat','proper_duration')]
    result={};summaries=[];bypass_midpoint=None
    for location in meta['sampling_locations']:
        at=s[location+'_time'];g=geometry(history.h.reference.h.model,at,s['x'])
        geometry_error=float(abs(g['radius']-s[location+'_R']).max())
        if geometry_error>1e-10:raise ValueError('registered geometry differs from temperature archive')
        length=physical_width*g['ell']
        r=passive_port_capacity(ph,pc,dt,g['D'],length,
            s[location+'_hot_photon_gap'],s[location+'_cold_photon_gap'],
            s[location+'_j'],s[location+'_c'])
        star=reciprocal_star(r['hot_transmission_budget'],r['cold_transmission_budget'])
        bypass=g['D']*dt*star['direct_bank_transmission']/length*(
            s[location+'_hot_photon_gap']+s[location+'_cold_photon_gap'])
        if location=='midpoint':bypass_midpoint=bypass
        matrix=star['scattering_matrix']
        unitary_error=float(np.max(abs(matrix@np.swapaxes(matrix,-1,-2)-np.eye(3))))
        i,j=np.unravel_index(np.argmax(r['total_transmission_budget']),ph.shape)
        q=np.unravel_index(np.argmax(abs(r['material_recoil_force_density'])),ph.shape)
        summaries.append(dict(location=location,
            passive_capacity_comparison_passes=bool(r['capacity_pass'].all()),
            maximum_total_transmission_budget=finite(r['total_transmission_budget'][i,j]),
            maximum_hot_coefficient=finite(r['hot_coefficient'].max()),
            maximum_cold_coefficient=finite(r['cold_coefficient'].max()),
            maximum_absolute_material_recoil_force_density=finite(abs(r['material_recoil_force_density'][q])),
            maximum_photon_power_residual=finite(abs(r['photon_power_residual']).max()),
            star_unitarity_residual=finite(unitary_error),
            maximum_direct_bank_transmission=finite(star['direct_bank_transmission'].max()),
            maximum_accumulated_frozen_bypass_heat=finite(bypass.sum(axis=0).max()),
            maximum_directional_fraction=finite(np.max(np.divide(abs(s[location+'_j']),s[location+'_c'],
                out=np.zeros_like(ph),where=s[location+'_c']>0))),
            witness=dict(time=float(at[i]),panel_start=float(s['t'][i]),panel_end=float(s['t'][i+1]),
                x=float(s['x'][j]),proper_cell_length=float(length[i,j]),
                hot_coefficient=finite(r['hot_coefficient'][i,j]),cold_coefficient=finite(r['cold_coefficient'][i,j]),
                hot_budget=finite(r['hot_transmission_budget'][i,j]),cold_budget=finite(r['cold_transmission_budget'][i,j]),
                counter_density=float(s[location+'_c'][i,j]),counter_current=float(s[location+'_j'][i,j])),
            recoil_witness=dict(time=float(at[q[0]]),x=float(s['x'][q[1]]),
                force_density=finite(r['material_recoil_force_density'][q]))))
        for k in ('hot_coefficient','cold_coefficient','total_transmission_budget','material_recoil_force_density'):
            result[location+'_'+k]=r[k]
        result[location+'_direct_bank_transmission']=star['direct_bank_transmission']
        result[location+'_frozen_bypass_panel_heat']=bypass
    bypass_history=np.vstack((np.zeros_like(bypass_midpoint[0]),np.cumsum(bypass_midpoint,axis=0)))
    projected_hot=old_hot-bypass_history;projected_cold=old_cold+bypass_history
    rating_margin=rated-old_hot.max(axis=0)-old_cold.max(axis=0)
    projected_rating=rated-projected_hot.max(axis=0)-projected_cold.max(axis=0)
    result.update(midpoint_frozen_bypass_history=bypass_history,
        original_separate_rating_margin=rating_margin,
        projected_separate_rating_margin=projected_rating,
        projected_hot_energy=projected_hot,projected_cold_energy=projected_cold)
    parent_ok=bool(meta['joint_bank_temperature_selection_passes'])
    passed=bool(parent_ok and all(c['passive_capacity_comparison_passes'] for c in summaries))
    summary=dict(label=label,input=str((folder/(label+'_temperature.npz')).relative_to(ROOT)),
        parent_temperature_selection_passes=parent_ok,passive_capacity_comparison_passes=passed,
        physical_coordinate_cell_width=physical_width,
        maximum_total_transmission_budget=(max(c['maximum_total_transmission_budget'] for c in summaries)
            if all(c['maximum_total_transmission_budget'] is not None for c in summaries) else None),
        samples=summaries,
        midpoint_bypass_estimate=dict(maximum_total_heat=finite(bypass_history[-1].max()),
            minimum_original_rating_margin=finite(rating_margin.min()),
            minimum_projected_rating_margin=finite(projected_rating.min()),
            minimum_projected_hot_energy=finite(projected_hot.min()),
            projected_bank_total_energy_change=finite(abs(projected_hot+projected_cold-old_hot-old_cold).max()),
            bank_histories_self_consistently_evolved=False,
            scope='frozen sampled temperatures and average photon branch powers; transfer H->C cumulatively; temperature and coupling feedback remain open'),
        source_channel_multiplicity_unchanged=True,
        physical_cell_length_scope='local material proper length ell*physical half-cell width; never refined grid-bin width',
        capacity_model='symmetric access at both ends; each bank receives a share of the existing bidirectional channel flux; tau_hot+tau_cold<=1',
        coefficient_scope='archived panel branch heats divided by proper duration and sampled D*(c_eq-c) or D*(c-c_eq)',
        recoil_law='force on material=(kappa_hot+kappa_cold)*counter_current for isotropic grey emission in the common material frame',
        recoil_reaction_supplied=False,full_curved_transit_solution_supplied=False,
        instantaneous_passive_scattering_matrix_supplied=True,
        material_scattering_network_supplied=False,direct_bank_bypass_heat_evaluated=True,
        bank_bypass_reallocation_closed=False,
        work_channel_isolation_supplied=False,switching_work_and_bandwidth_supplied=False,
        microscopic_material_response_supplied=False,bank_mass_and_packing_supplied=False,
        full_source_construction_supplied=False)
    np.savez_compressed(output/(label+'_ports.npz'),t=s['t'],x=s['x'],**result)
    write_json(output/(label+'_summary.json'),summary)
    print(label+': '+json.dumps({k:summary[k] for k in
        ('passive_capacity_comparison_passes','maximum_total_transmission_budget')}),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources',nargs='+',required=True)
    parser.add_argument('--output-name',required=True)
    parser.add_argument('--workers',type=int,default=2)
    args=parser.parse_args()
    if not 1<=args.workers<=4:parser.error('one to four workers required')
    output=BASE/args.output_name
    if output.exists():raise RuntimeError('preserve completed contact-capacity comparison')
    inputs={};historical=[];jobs=[]
    for name in args.sources:
        folder=BASE/name;checked,old=validate_controls(folder,[])
        inputs.update(checked);historical.extend(old)
        manifest=json.loads((folder/'manifest.json').read_text())
        for path in sorted(folder.glob('*_temperature.npz')):
            label=path.stem.removesuffix('_temperature')
            for p in (path,folder/(label+'_summary.json')):
                expected=manifest['output_sha256'][p.name]
                if sha256_file(p)!=expected:raise RuntimeError('changed temperature input: '+str(p))
                inputs[str(p.relative_to(ROOT))]=expected
            jobs.append((folder,label,output))
    if not jobs:raise ValueError('completed temperature arrays required')
    runtime=[Path(__file__),ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_photon_contact_capacity.py']
    for module in list(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            p=Path(name).resolve()
            if p.suffix=='.py' and p.is_relative_to(ROOT):runtime.append(p)
    inputs.update({str(p.relative_to(ROOT)):sha256_file(p) for p in runtime})
    output.mkdir()
    with ProcessPoolExecutor(max_workers=min(args.workers,len(jobs)),
            mp_context=multiprocessing.get_context('spawn')) as pool:
        cases=list(pool.map(evaluate,jobs))
    for relative,expected in inputs.items():
        if sha256_file(ROOT/relative)!=expected:raise RuntimeError('input changed during port audit: '+relative)
    write_json(output/'summary.json',dict(cases=cases))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        workers=min(args.workers,len(jobs)),input_sha256=inputs,historical_source=historical,
        output_sha256={p.name:sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__=='__main__':main()
