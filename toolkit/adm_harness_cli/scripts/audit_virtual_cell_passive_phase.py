#!/usr/bin/env python3
"""Sampled local energy/cone relaxation with independently reoptimized phase."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

import numpy as np
from numpy.polynomial.legendre import leggauss

from adm_harness.active_transfer_reservoir import TabulatedActiveMedium
from adm_harness.source_ledger import sha256_file
from adm_harness.virtual_cell_counterstream import material_kinematics
from adm_harness.virtual_cell_passive_phase import solve_passive_phase
from audit_virtual_cell_counterstream import (
    BASE, ROOT, find_control, geometry, verify_input_identity, write_json,
)


def panel_mean_ell_squared(model,t,x,order):
    z,weights=leggauss(order)
    tt=((t[:-1]+t[1:])[:,None]/2+np.diff(t)[:,None]*z[None,:]/2).ravel()
    xx=np.full_like(tt,x)
    alpha=np.exp(model.metric_splines[0].ev(tt,xx))
    beta=model.metric_splines[1].ev(tt,xx)
    b=np.exp(model.metric_splines[2].ev(tt,xx))
    return ((b*b/(1-(b*beta/alpha)**2)).reshape(-1,order)*weights[None,:]).sum(axis=1)/2


def evaluate(spec):
    path,output,strides=spec;path=Path(path);output=Path(output)
    meta=json.loads(path.with_name(path.name.replace('_states.npz','_summary.json')).read_text())
    with np.load(path) as z:s={key:z[key] for key in z.files}
    middle=len(s['x'])//2;positions=s['x'][middle-1:middle+1]
    model=TabulatedActiveMedium(BASE/'active_transfer_reservoir/metric_fine.npz',
                               BASE/'active_transfer_reservoir/medium_baseline.npz')
    if np.any(positions<model.x_min) or np.any(positions>model.x_max):
        raise ValueError('selected positions must be inside the metric table')
    g=geometry(model,s['t'],positions);kin=material_kinematics(g)
    results=[]
    for side,index in enumerate((middle-1,middle)):
        for stride in strides:
            sample=np.arange(0,len(s['t']),stride)
            if sample[-1]!=len(s['t'])-1:
                raise ValueError('temporal stride must preserve the final node')
            t=s['t'][sample];x=float(s['x'][index])
            fields=[s[key][sample,index] for key in ('density','radial_pressure','angular_pressure','wall_rest')]
            radius=g['radius'][sample,side];ell=kin['ell'][sample,side]
            mean4=panel_mean_ell_squared(model,t,x,4)
            mean8=panel_mean_ell_squared(model,t,x,8)
            solved=solve_passive_phase(*fields,radius,ell,mean8)
            scalars={key:value for key,value in solved.items() if np.isscalar(value)}
            label=meta['label']+f'_side{side}_stride{stride}'
            result=dict(label=label,source=str(path.relative_to(ROOT)),position=x,
                source_spatial_index=int(index),temporal_stride=int(stride),time_samples=len(t),
                phase_independently_reoptimized=True,prepared_radiation_inventory_free=True,
                radiation_current_zero=True,conversion_efficiency=1.,minimum_travelling_inventory=0.,
                interface_wall_energy_retained=True,additional_guide_floor_retained=False,
                target_numerical_density_reserve_removed=False,
                panel_quadrature_orders=[4,8],maximum_panel_mean_quadrature_change=float(abs(mean8-mean4).max()),
                sampled_optimistic_gate_passes=bool(solved['density_allowance']<1e-8),
                positive_dual_density_gap=bool(solved['dual_lower_bound']>1e-8),
                certificate_scope='floating-point bounded-domain LP dual lower bound; saved multipliers and finite variable bounds permit independent reconstruction',
                scope='one spatial position with sampled cone constraints and piecewise-linear phase; excludes no general continuous-time or spatially coupled construction',
                full_source_construction_supplied=False,**scalars)
            write_json(output/(label+'_summary.json'),result)
            arrays={key:value for key,value in solved.items() if isinstance(value,np.ndarray)}
            np.savez_compressed(output/(label+'_states.npz'),t=t,x=np.array(x),
                density=fields[0],radial_pressure=fields[1],angular_pressure=fields[2],wall_rest=fields[3],
                radius=radius,ell=ell,panel_mean_ell_squared=mean8,
                panel_mean_ell_squared_order4=mean4,**arrays)
            print(f'{label}: density allowance={solved["density_allowance"]:.12g}, '
                  f'dual bound={solved["dual_lower_bound"]:.12g}',flush=True)
            results.append(result)
    return results


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,default=BASE/'virtual_cell_reconstructed_replay')
    parser.add_argument('--controls',type=Path)
    parser.add_argument('--output',type=Path,default=BASE/'virtual_cell_passive_phase')
    parser.add_argument('--strides',type=int,nargs='+',default=[2,1])
    parser.add_argument('--workers',type=int,default=1)
    args=parser.parse_args()
    if not 1<=args.workers<=2:parser.error('--workers must be 1 or 2')
    if min(args.strides)<1:parser.error('--strides must be positive')
    source=args.source.resolve();output=args.output.resolve()
    if output.exists():raise RuntimeError('preserve completed passive-phase audit')
    paths=sorted(source.glob('*_factor4_states.npz'))
    if not paths:raise ValueError('factor4 independent replay archives required')
    input_paths=[source/'manifest.json',BASE/'active_transfer_reservoir/metric_fine.npz',
        BASE/'active_transfer_reservoir/medium_baseline.npz',Path(__file__),
        ROOT/'toolkit/adm_harness_cli/scripts/audit_virtual_cell_counterstream.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/virtual_cell_passive_phase.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/virtual_cell_counterstream.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/active_transfer_reservoir.py',
        ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_passive_phase.py']
    checked=[]
    for path in paths:
        summary=path.with_name(path.name.replace('_states.npz','_summary.json'))
        control=find_control(source,json.loads(summary.read_text())['label'],args.controls)
        checks,manifest=verify_input_identity(source,path,control);checked.extend(checks)
        input_paths.extend([path,summary,control,manifest,
            control.with_name(control.name.replace('_states.npz','_summary.json'))])
    hashes={str(p.relative_to(ROOT)):sha256_file(p) for p in input_paths}
    output.mkdir(parents=True)
    with ProcessPoolExecutor(max_workers=min(args.workers,len(paths)),
                             mp_context=multiprocessing.get_context('spawn')) as pool:
        groups=list(pool.map(evaluate,[(str(p),str(output),args.strides) for p in paths]))
    results=[row for group in groups for row in group]
    comparisons=[]
    for path in paths:
        for side in (0,1):
            cases=[row for row in results if row['source']==str(path.relative_to(ROOT))
                   and '_side'+str(side)+'_' in row['label']]
            ordered=sorted(cases,key=lambda row:row['time_samples'])
            comparisons.append(dict(source=str(path.relative_to(ROOT)),side=side,
                position=ordered[0]['position'],time_samples=[row['time_samples'] for row in ordered],
                density_allowances=[row['density_allowance'] for row in ordered],
                maximum_allowance_change=max(row['density_allowance'] for row in ordered)-
                                         min(row['density_allowance'] for row in ordered)))
    write_json(output/'summary.json',dict(cases=results,temporal_comparisons=comparisons))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        workers=min(args.workers,len(paths)),input_sha256=hashes,immutable_input_checks=checked,
        output_sha256={p.name:sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__=='__main__':main()
