#!/usr/bin/env python3
"""Bounded two-cell phase-volume conversion and common-port transport runs."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess
import time

import numpy as np
from scipy.integrate import cumulative_trapezoid

from adm_harness.source_ledger import sha256_file
from adm_harness.virtual_cell_transport import solve_pair
from audit_joint_dense_work import DenseHistory
from run_poynting_delivery import BASE, ROOT, write_json


def evaluate(spec):
    width, intervals, stride, eta, sigma, output, selected_center, coherent, return_heat, reserve = spec
    started=time.monotonic()
    center=selected_center if selected_center is not None else (-1.3 if width>1 else -1.9875)
    path=BASE/'joint_refined_response/members_fraction0.99_states.npz'
    h=DenseHistory('routed_family',path)
    # Include the known startup witnesses in both temporal resolutions.
    t=np.unique(np.r_[h.state['t'][::stride],h.state['t'][-1],
                      .047685546875,.0501953125,.072783203125,.5])
    edges=np.linspace(center-width/2,center+width/2,intervals+1)
    x=(edges[:-1]+edges[1:])/2; dx=edges[1]-edges[0]
    tm=(t[1:]+t[:-1])/2
    nodes=h.coefficients(t,x); mids=h.coefficients(tm,x)
    rho=h.energy(x).evaluate(t)[0]/nodes['D']
    target=np.array([rho,h.pressure(t,x)[0],nodes['Q']/nodes['D']])
    model=h.h.reference.h.model
    gm=[model.metric(float(now),x) for now in tm]
    ge=[model.metric(float(now),edges) for now in tm]
    wave={sign:dict(faces=np.array([-g.beta+sign*g.alpha/g.b for g in ge]),
                    gain=np.array([g.alpha*g.k_l-sign*g.alpha_x/g.b for g in gm]))
          for sign in [-1,1]}
    budget=target.copy(); budget[0]*=1-reserve
    r=solve_pair(t,edges,budget,nodes,mids,wave,efficiency=eta,interface_sigma=sigma,
                 coherent_cells=coherent,return_heat=return_heat,deadline=240.)
    label=f'x{center:g}_w{width:g}_n{intervals}_s{stride}_eta{eta:g}_sigma{sigma:g}'
    summary={k:v for k,v in r.items() if not isinstance(v,np.ndarray)}
    summary.update(label=label,width=width,center=center,intervals=intervals,time_nodes=len(t),
        efficiency=eta,interface_sigma=sigma,
        coherent_cell_amplitudes=coherent,heat_return=return_heat,
        reserved_density_fraction=reserve,
        input=str(path.relative_to(ROOT)),
        scope='two finite phase-volume cells with optimized activation and causal radial work streams',
        microscopic_phase_fronts_solved=False,guide_and_current_carrier_energy_supplied=False,
        interface_energy_model='two volume-averaged angular end membranes per cell',
        continuing_support_constitutive_law_supplied=False,
        external_common_port_stress_supplied=False,full_construction_supplied=False)
    if r['success']:
        a=r['amplitude']; ua=r['absorption_rest']; ur=r['recovery_rest']
        d=np.r_[-np.ones(intervals//2),np.ones(intervals//2)]
        positive=r['positive_increment']/np.diff(t)[:,None]
        negative=r['negative_increment']/np.diff(t)[:,None]
        at=positive-negative
        ax=np.gradient((a[1:]+a[:-1])/2,x,axis=1,edge_order=2)
        core_power=at/(mids['lapse']*mids['radius']**2)
        core_force=-(ax/mids['ell']+mids['v']*at/mids['lapse'])/mids['radius']**2
        losses=(1/eta-1)*positive+(1-eta)*negative
        returned=eta*negative+(losses if return_heat else 0.)
        tap_force=-d*(positive/eta+returned)/(mids['lapse']*mids['radius']**2)
        heat_power=(np.zeros_like(losses) if return_heat else losses)/(mids['lapse']*mids['radius']**2)
        photon_power=(-positive/eta+returned)/(mids['lapse']*mids['radius']**2)
        power_residual=core_power+photon_power+heat_power
        # Common middle port: convert ADM photon energy into the same local
        # material-frame energy on both sides before integrating the buffer.
        port=h.coefficients(tm,np.array([center]))
        incoming=np.zeros(len(tm)); outgoing=np.zeros(len(tm)); thermal_out=np.zeros(len(tm))
        for j,sign in [(intervals//2-1,-1),(intervals//2,1)]:
            f=intervals//2
            boost=port['gamma'][:,0]*(1-sign*port['v'][:,0])
            incoming+=4*np.pi*abs(wave[sign]['faces'][:,f])*r['absorption_state'][:-1,j]*boost
            boost_return=port['gamma'][:,0]*(1+sign*port['v'][:,0])
            outgoing+=4*np.pi*abs(wave[-sign]['faces'][:,f])*r['recovery_state'][1:,j]*boost_return
            thermal_out+=4*np.pi*abs(wave[-sign]['faces'][:,f])*r['thermal_return_state'][1:,j]*boost_return
        drawn=np.r_[0.,np.cumsum(np.diff(t)*(incoming-outgoing))]
        initial=max(0.,float(drawn.max())); buffer=initial-drawn
        spare=4*np.pi*dx*np.sum(nodes['D']*np.maximum(-r['density_shortfall'],0),axis=1)
        upper=float(np.min(drawn+spare))
        summary.update(target_budget_passes=bool(r['exact_added_density']<=2e-7),
            maximum_travelling_rest_density=float((ua+ur).max()),
            maximum_countercurrent_density=float(abs(d*(ua-ur)).max()),
            maximum_conversion_heat_density=float(r['heat_rest'].max()),
            maximum_travelling_heat_density=float(r['thermal_return_rest'].max()),
            maximum_interface_density=float(r['wall_rest'].max()),
            maximum_phase_power=float(abs(core_power).max()),
            maximum_phase_force=float(abs(core_force).max()),
            maximum_combined_phase_and_tap_force=float(abs(core_force+tap_force).max()),
            maximum_internal_power_residual=float(abs(power_residual).max()),
            incident_common_port_energy=float(np.sum(np.diff(t)*incoming)),
            recovered_common_port_energy=float(np.sum(np.diff(t)*outgoing)),
            returned_heat_energy=float(np.sum(np.diff(t)*thermal_out)),
            returned_useful_work_energy=float(np.sum(np.diff(t)*(outgoing-thermal_out))),
            minimum_closed_buffer_initial_energy=initial,
            closed_buffer_maximum_energy=float(buffer.max()),
            maximum_closed_buffer_initial_energy_permitted_by_spare=upper,
            closed_rest_buffer_fits_spare_energy=bool(initial<=upper+1e-8),
            initial_target_rest_energy=float(4*np.pi*dx*np.sum(nodes['D'][0]*rho[0])),
            maximum_target_spare_rest_energy=float(spare.max()),
            minimum_cell_proper_length=float(np.min(np.sum(nodes['ell'].reshape(len(t),2,intervals//2),axis=2)*dx)),
            maximum_cell_proper_length=float(np.max(np.sum(nodes['ell'].reshape(len(t),2,intervals//2),axis=2)*dx)))
        np.savez_compressed(Path(output)/(label+'_states.npz'),t=t,x=x,edges=edges,
            target=target,radius=nodes['radius'],D=nodes['D'],lapse=nodes['lapse'],ell=nodes['ell'],
            v=nodes['v'],**{k:v for k,v in r.items() if isinstance(v,np.ndarray)},
            shared_port_incoming=incoming,shared_port_outgoing=outgoing,
            shared_port_heat=thermal_out,
            closed_buffer_energy=buffer,target_spare_energy=spare,
            core_force=core_force,tap_force=tap_force,core_power=core_power)
    summary['elapsed_seconds']=time.monotonic()-started
    write_json(Path(output)/(label+'_summary.json'),summary)
    print(label+': '+json.dumps({k:summary[k] for k in ['success','minimum_added_density',
        'target_budget_passes','closed_rest_buffer_fits_spare_energy'] if k in summary}),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--widths',type=float,nargs='+',default=[1.6,.05,.005,.0005])
    parser.add_argument('--intervals',type=int,default=24)
    parser.add_argument('--stride',type=int,default=4)
    parser.add_argument('--efficiency',type=float,default=1.)
    parser.add_argument('--sigma',type=float,default=0.)
    parser.add_argument('--centers',type=float,nargs='+')
    parser.add_argument('--coherent',action='store_true')
    parser.add_argument('--return-heat',action='store_true')
    parser.add_argument('--reserve',type=float,default=0.)
    parser.add_argument('--output-name',default='virtual_cell_transport')
    args=parser.parse_args(); output=BASE/args.output_name
    if output.exists(): raise RuntimeError('preserve completed transport evidence')
    source=BASE/'joint_refined_response/manifest.json'; previous=json.loads(source.read_text())
    hashes=dict(previous['input_sha256'])
    path=source.parent/'members_fraction0.99_states.npz'
    if sha256_file(path)!=previous['output_sha256'][path.name]: raise RuntimeError('changed support target')
    for item in [source,path,Path(__file__),
            ROOT/'toolkit/adm_harness_cli/adm_harness/virtual_cell_transport.py',
            ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_transport.py',
            Path(__file__).with_name('audit_joint_dense_work.py')]:
        hashes[str(item.relative_to(ROOT))]=sha256_file(item)
    for relative,expected in hashes.items():
        if sha256_file(ROOT/relative)!=expected: raise RuntimeError('changed dependency: '+relative)
    output.mkdir()
    specs=[(w,args.intervals,args.stride,args.efficiency,args.sigma,str(output),center,
            args.coherent,args.return_heat,args.reserve) for center in (args.centers or [None]) for w in args.widths]
    with ProcessPoolExecutor(max_workers=max(1,min(args.workers,len(specs))),
                             mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,specs))
    write_json(output/'summary.json',dict(cases=results))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes,output_sha256={p.name:sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__=='__main__': main()
