#!/usr/bin/env python3
"""Replay immutable cell controls and retain their drive/return beam subledger."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import multiprocessing
import subprocess
import time

import numpy as np

from adm_harness.virtual_cell_ports import (instrumented_propagate, beam_port_moments,
    counterstream_moments, phase_port_traction)
from audit_joint_dense_work import DenseHistory
from run_poynting_delivery import BASE, ROOT, write_json


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def interp(grid, values, now):
    i=int(np.clip(np.searchsorted(grid,now,side='right')-1,0,len(grid)-2))
    f=(now-grid[i])/(grid[i+1]-grid[i])
    return (1-f)*values[i]+f*values[i+1]


def validate_controls(source, labels):
    """Verify data in place and inherited source provenance at its recorded commit.

    Historical solver code is not substituted into this new independent replay.
    Current runtime code has its own hashes in the new manifest. A changed
    historical solver is accepted only when git reproduces its recorded bytes.
    """
    manifest_path=source/'manifest.json'; manifest=json.loads(manifest_path.read_text())
    checked={}; historical=[]; commit=manifest['git_head']
    for label in labels:
        for suffix in ('_states.npz','_summary.json'):
            p=source/(label+suffix); expected=manifest['output_sha256'][p.name]
            if sha(p)!=expected: raise RuntimeError('changed controls: '+str(p))
            checked[str(p.relative_to(ROOT))]=expected
    for relative,expected in manifest['input_sha256'].items():
        p=ROOT/relative
        current=sha(p)
        if current==expected:
            checked[relative]=expected
        elif p.suffix=='.py':
            # A run records HEAD before its new code is committed. Locate the
            # exact recorded bytes, including the subsequent evidence commit.
            revisions=[commit]+subprocess.check_output(
                ['git','log','--all','-100','--format=%H','--',relative],cwd=ROOT,text=True).splitlines()
            verified=None
            for revision in dict.fromkeys(revisions):
                original=subprocess.run(['git','show',revision+':'+relative],cwd=ROOT,capture_output=True)
                if original.returncode==0 and hashlib.sha256(original.stdout).hexdigest()==expected:
                    verified=revision; break
            if verified is None: raise RuntimeError('unverified historical dependency: '+relative)
            historical.append(dict(path=relative,recorded_sha256=expected,
                current_sha256=current,verified_at_commit=verified))
        else:
            raise RuntimeError('changed input data: '+relative)
    checked[str(manifest_path.relative_to(ROOT))]=sha(manifest_path)
    return checked,historical


def audit(spec):
    source,label,factor,output=spec; started=time.monotonic(); source=Path(source); output=Path(output)
    path=source/(label+'_states.npz'); meta=json.loads(path.with_name(label+'_summary.json').read_text())
    with np.load(path) as f:z={k:f[k] for k in f.files}
    if not meta['coherent_cell_amplitudes'] or not meta['heat_return']:
        raise ValueError('coherent cells and separated heat return required')
    if min(z['positive_increment'].min(),z['negative_increment'].min())<0:
        raise ValueError('negative control increment')
    oldt,oldx=z['t'],z['x']; oldn=len(oldx); eta=meta['efficiency']
    for a in [z['amplitude'],z['positive_increment'],z['negative_increment']]:
        if max(np.ptp(a[:,:oldn//2],axis=1).max(),np.ptp(a[:,oldn//2:],axis=1).max())>1e-13:
            raise ValueError('each cell requires coherent control')
    t=np.r_[(oldt[:-1,None]+np.diff(oldt)[:,None]*np.arange(factor)[None,:]/factor).ravel(),oldt[-1]]
    edges=np.linspace(z['edges'][0],z['edges'][-1],oldn*factor+1)
    x=(edges[:-1]+edges[1:])/2; nx=len(x); half=nx//2; dx=edges[1]-edges[0]
    center=(edges[0]+edges[-1])/2
    h=DenseHistory('routed_family',ROOT/meta['input']); model=h.h.reference.h.model
    geom=[model.metric(float(now),x) for now in t]
    edgegeom=[model.metric(float(now),edges) for now in t]
    b=np.array([g.b for g in geom]); radius=np.array([g.radius for g in geom])
    v=np.array([g.b*g.beta/g.alpha for g in geom]); gamma=1/np.sqrt(1-v*v)
    port_v=np.array([g.b[half]*g.beta[half]/g.alpha[half] for g in edgegeom])
    port_gamma=1/np.sqrt(1-port_v**2)
    port_lapse=np.array([g.alpha[half] for g in edgegeom])/port_gamma
    port_radius=np.array([g.radius[half] for g in edgegeom])
    tables={sign:dict(faces=np.array([-g.beta+sign*g.alpha/g.b for g in edgegeom]),
        gain=np.array([g.alpha*g.k_l-sign*g.alpha_x/g.b for g in geom]),
        source=b/(1-sign*v),boost=port_gamma*(1-sign*port_v)) for sign in (-1,1)}
    speed=np.maximum(abs(tables[-1]['faces']).max(axis=1),abs(tables[1]['faces']).max(axis=1))
    gain=np.maximum(abs(tables[-1]['gain']).max(axis=1),abs(tables[1]['gain']).max(axis=1))
    # Interpolated coefficients have their largest absolute values at endpoints.
    counts=np.maximum(1,np.ceil(np.diff(t)*(np.maximum(speed[:-1],speed[1:])/dx+
        np.maximum(gain[:-1],gain[1:]))/.35).astype(int))
    states={}; ports={}; panel_energy={}; ledgers={}; phase=np.empty((len(t),nx))
    for side,direction in enumerate((-1,1)):
        sl=slice(side*half,(side+1)*half); oldsl=slice(side*(oldn//2),(side+1)*(oldn//2))
        plus=z['positive_increment'][:,oldsl].mean(axis=1)/np.diff(oldt)
        minus=z['negative_increment'][:,oldsl].mean(axis=1)/np.diff(oldt)
        phase[:,sl]=np.interp(t,oldt,z['amplitude'][:,oldsl].mean(axis=1))[:,None]
        for purpose,sign,rates,back in [('incident',direction,plus/eta,True),
                ('useful',-direction,eta*minus,False),
                ('heat',-direction,(1/eta-1)*plus+(1-eta)*minus,False)]:
            tab=tables[sign]; faces=tab['faces'][:,side*half:(side+1)*half+1]
            def coefficients(now,interval):
                original=min(interval//factor,len(oldt)-2)
                return (interp(t,faces,now),interp(t,tab['gain'][:,sl],now),
                        interp(t,tab['source'][:,sl],now)*rates[original])
            def port_geometry(now):
                return interp(t,tab['boost'],now),interp(t,port_lapse,now)
            result=instrumented_propagate(t,edges[side*half:(side+1)*half+1],coefficients,
                port_geometry,port_face=-1 if side==0 else 0,backwards=back,substeps=counts)
            key=purpose+'_'+str(side)
            states[key]=result['state']; ports[key]=result['coordinate_power']
            panel_energy[key]=result['port_energy']; ledgers[key]=result['ledger']
            if 'port_time' in locals() and not np.array_equal(port_time,result['port_time']):
                raise ArithmeticError('streams lost synchronized observation times')
            port_time=result['port_time']
    beam={purpose:np.column_stack([ports[purpose+'_'+str(side)] for side in (0,1)])
          for purpose in ('incident','useful','heat')}
    energy={purpose:np.column_stack([panel_energy[purpose+'_'+str(side)] for side in (0,1)])
            for purpose in beam}
    lapse=np.interp(port_time,t,port_lapse); pradius=np.interp(port_time,t,port_radius)
    supply,reaction=beam_port_moments(beam['incident'],beam['useful'],beam['heat'])
    supply_e,reaction_e=beam_port_moments(energy['incident'],energy['useful'],energy['heat'])
    rest={}
    for purpose in beam:
        field=np.empty((len(t),nx))
        for side,direction in enumerate((-1,1)):
            sl=slice(side*half,(side+1)*half); sign=direction if purpose=='incident' else -direction
            field[:,sl]=states[purpose+'_'+str(side)]*gamma[:,sl]**2*(1-sign*v[:,sl])**2/(b[:,sl]*radius[:,sl]**2)
        rest[purpose]=field
    direction=np.r_[-np.ones(half),np.ones(half)]
    counter=counterstream_moments(rest['incident'],rest['useful'],rest['heat'],direction)
    volume=gamma*b*radius**2
    inventory=lambda a:4*np.pi*dx*np.sum(volume*a,axis=1)
    counter_inventory=inventory(counter[0]); signed_wave_inventory=inventory(-counter[2])
    node_traction=phase_port_traction(phase[:,0],phase[:,-1])
    # Same-cut kinematic completion: opposite beam energy current, paid with a
    # positive radial-null density. No claim of a realizable counterstream path.
    beam_signed_flux=supply*np.array([-1.,1.])
    counter_signed_flux=-beam_signed_flux
    counter_flux_density=abs(counter_signed_flux)/(4*np.pi*pradius[:,None]**2*lapse[:,None])
    counter_supply=-supply
    # Per-side additional port traction is positive for the left material and
    # negative for the right material, whatever direction the null stream runs.
    counter_reaction=abs(supply)*np.array([1.,-1.])
    peak=lambda a:dict(maximum=float(np.max(a)),minimum=float(np.min(a)),maximum_absolute=float(np.max(abs(a))))
    summary=dict(label=label,factor=factor,center=float(center),time_start=float(t[0]),time_end=float(t[-1]),
        spatial_samples=nx,time_samples=len(t),synchronized_port_samples=len(port_time),
        subledger='drive/return photons only; excludes counterstream, connector and material attachments',
        energy_convention='material-frame photon energy integrated per coordinate time; 4*pi spherical normalization',
        radial_sign='positive toward increasing x in the common material tetrad; sphere-integrated radial component',
        beam_incident_energy_by_side=energy['incident'].sum(axis=0).tolist(),
        beam_useful_return_energy_by_side=energy['useful'].sum(axis=0).tolist(),
        beam_returned_heat_energy_by_side=energy['heat'].sum(axis=0).tolist(),
        beam_incident_energy=float(energy['incident'].sum()),
        beam_useful_return_energy=float(energy['useful'].sum()),
        beam_returned_heat_energy=float(energy['heat'].sum()),
        beam_signed_net_energy_to_cells=float(supply_e.sum()),
        beam_signed_port_reaction_impulse_by_side=reaction_e.sum(axis=0).tolist(),
        beam_signed_port_reaction_impulse=float(reaction_e.sum()),
        beam_peak_proper_power={k:peak(p.sum(axis=1)/lapse) for k,p in beam.items()},
        beam_peak_coordinate_power={k:peak(p.sum(axis=1)) for k,p in beam.items()},
        beam_port_reaction_proper=peak(reaction.sum(axis=1)/lapse),
        beam_port_reaction_proper_by_side=[peak(reaction[:,i]/lapse) for i in (0,1)],
        beam_port_signed_supply_proper=peak(supply.sum(axis=1)/lapse),
        peak_observation_scope='synchronized corrected SSP substep states; integrals use both RK stages',
        maximum_absolute_ADM_wave_balance_residual=max(float(abs(a[:,4]).max()) for a in ledgers.values()),
        ADM_wave_ledger_columns=['boundary','geometric','conversion_source','inventory_change','balance_residual','material_port_traffic'],
        ADM_wave_totals={k:dict(zip(['boundary','geometric','conversion_source','inventory_change','balance_residual','material_port_traffic'],a.sum(axis=0).tolist())) for k,a in ledgers.items()},
        ADM_initial_final_inventory={k:(4*np.pi*dx*a[[0,-1]].sum(axis=1)).tolist() for k,a in states.items()},
        maximum_required_counterstream_density=float(counter[0].max()),
        maximum_counterstream_rest_inventory=float(counter_inventory.max()),
        counterstream_initial_final_rest_inventory=counter_inventory[[0,-1]].tolist(),
        wave_signed_radial_inventory_initial_final=signed_wave_inventory[[0,-1]].tolist(),
        maximum_absolute_wave_signed_radial_inventory=float(abs(signed_wave_inventory).max()),
        counterstream_transport_supplied=False,
        same_cut_counterstream_completion='pointwise kinematic null tensor only; transport, exchange and delivery unspecified',
        same_cut_counterstream_peak_signed_proper_flux_by_side=[peak(counter_signed_flux[:,i]/lapse) for i in (0,1)],
        same_cut_counterstream_peak_density_by_side=[float(counter_flux_density[:,i].max()) for i in (0,1)],
        same_cut_completed_current_maximum_residual=float(abs(beam_signed_flux+counter_signed_flux).max()),
        same_cut_completed_signed_energy_supply_maximum_residual=float(abs(supply+counter_supply).max()),
        same_cut_completed_radiation_port_reaction_proper=peak((reaction+counter_reaction).sum(axis=1)/lapse),
        maximum_absolute_core_phase_traction_jump=float(abs(node_traction).max()),
        core_phase_traction_jump_extreme_time=float(t[abs(node_traction).argmax()]),
        core_phase_traction_convention='4*pi*(A_right-A_left), proper force on common interface; excludes attachment/inertia',
        simultaneous_conversion_increment=float(np.minimum(z['positive_increment'],z['negative_increment']).max()),
        original_stress_budget_retested=False,full_external_power_or_mechanical_closure=False,
        elapsed_seconds=time.monotonic()-started)
    stem=label+f'_factor{factor}'
    np.savez_compressed(output/(stem+'_states.npz'),t=t,x=x,port_time=port_time,port_lapse=lapse,
        port_radius=pradius,phase_traction=node_traction,counterstream_density=counter[0],counterstream_current=counter[2],
        counterstream_inventory=counter_inventory,wave_signed_inventory=signed_wave_inventory,
        port_incident=beam['incident'],port_useful_return=beam['useful'],port_heat_return=beam['heat'],
        port_reaction_by_side=reaction,port_signed_supply_by_side=supply,
        same_cut_counterstream_signed_flux=counter_signed_flux,
        same_cut_completed_radiation_reaction_by_side=reaction+counter_reaction,
        **{'panel_'+k:a for k,a in energy.items()},**{'ledger_'+k:a for k,a in ledgers.items()},
        **{'rest_'+k:a for k,a in rest.items()})
    write_json(output/(stem+'_summary.json'),summary)
    print(label+': beam incident='+str(summary['beam_incident_energy'])+', signed recoil='+str(summary['beam_signed_port_reaction_impulse']),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--source',default='virtual_cell_reconstructed_controls')
    parser.add_argument('--labels',nargs='+'); parser.add_argument('--factor',type=int,default=4)
    parser.add_argument('--workers',type=int,default=2); parser.add_argument('--output-name',default='virtual_cell_port_baseline')
    args=parser.parse_args()
    if args.factor<1 or not 1<=args.workers<=2: parser.error('factor >=1 and one or two workers required')
    source=BASE/args.source; output=BASE/args.output_name
    if output.exists(): raise RuntimeError('preserve completed port audit')
    labels=args.labels or [p.name.removesuffix('_states.npz') for p in sorted(source.glob('*_states.npz'))]
    inputs,historical=validate_controls(source,labels)
    runtime=[Path(__file__),ROOT/'toolkit/adm_harness_cli/adm_harness/virtual_cell_ports.py',
        ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_ports.py',
        Path(__file__).with_name('audit_joint_dense_work.py')]
    output.mkdir()
    specs=[(str(source),label,args.factor,str(output)) for label in labels]
    with ProcessPoolExecutor(max_workers=min(args.workers,len(specs)),mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(audit,specs))
    write_json(output/'summary.json',dict(cases=results))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=inputs,historical_source_dependencies=historical,
        runtime_sha256={str(p.relative_to(ROOT)):sha(p) for p in runtime},
        output_sha256={p.name:sha(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__=='__main__': main()
