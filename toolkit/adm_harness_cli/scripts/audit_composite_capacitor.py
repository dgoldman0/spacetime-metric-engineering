#!/usr/bin/env python3
"""Independent force witness, resolution comparisons, hashes and figures.

The complete internally balanced cell plus allocated pressure fluid has
isotropic pressure p-p_*. Where p_*=p it is a co-moving zero-pressure tensor.
At positive material acceleration its density requires a positive holding
force. The selected work waves add a nonnegative radial divergence, while a
source-free constant-flux guide contributes zero. A separate mechanical
stress/force channel is therefore required by that completed-cell tensor.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import multiprocessing

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from adm_harness.active_transfer_reservoir import smooth_rise
from adm_harness.pressure_linked_storage import fluid_coefficients
from adm_harness.shared_field_delivery import smooth_under_cap
from adm_harness.source_ledger import sha256_file
from evaluate_finite_work_interface import InterfaceHistory
from evaluate_recovery_work_interface import recovery_state
from run_poynting_delivery import BASE,ROOT,write_json

OUTPUT=BASE/'composite_capacitor_audit'


def force_witness(spec):
    pinned_cells,evaluation_cells=spec
    model=InterfaceHistory(pinned_cells)
    state=recovery_state(model,1.)
    knots=model.h.state['x']
    unused,unused,values=smooth_under_cap(model.check_x,np.minimum(state['flux'],model.cap),knots)
    edges=np.linspace(knots[0],knots[-1],evaluation_cells+1)
    x=(edges[1:]+edges[:-1])/2
    ix=np.clip(np.searchsorted(knots,x,side='right')-1,0,len(knots)-2)
    width=knots[ix+1]-knots[ix]
    rise,derivative=smooth_rise((x-knots[ix])/width)
    share=values[ix]+(values[ix+1]-values[ix])*rise
    share_x=(values[ix+1]-values[ix])*derivative/width
    times=(model.t[1:]+model.t[:-1])/2
    c=fluid_coefficients(model.h.model,times,x)
    st=model.h.state
    interp=lambda array,xx: np.array([np.interp(x,xx,row) for row in np.atleast_2d(array)])
    hm=interp((st['flux_energy'][1:]+st['flux_energy'][:-1])/2,knots)
    um=interp((st['thermal'][1:]+st['thermal'][:-1])/2,knots)
    number=interp(st['number'],knots)[0]
    ue=(hm-share)/c['radius']**4
    pressure=um/(3*c['rest_volume'])
    heat_energy=interp((state['heat'][1:]+state['heat'][:-1])/2+state['heat_cap']/3,model.x)
    heat_density=heat_energy/c['rest_volume']
    charge=interp(model.h.hdot,knots)/(c['lapse']*c['radius']**4)
    wave_force=np.maximum(charge,0)/.98+.98*np.maximum(-charge,0)
    endpoint=c['gamma']*(c['normal_force']-c['v']*c['power'])
    heat_force=heat_density*c['acceleration']
    extra=share_x/(c['gamma']*c['b']*c['radius']**4)
    required=endpoint-wave_force-heat_force-extra
    # With p_*=p, E + used fluid + any DEC-balancing material has
    # rho >= n + 4*p + 2*u_E and pr=pt=0. No numerical pressure derivatives
    # enter this witness. More retained co-moving density raises its force.
    density_floor=number/c['rest_volume']+4*pressure+2*ue+heat_density
    witness=density_floor*c['acceleration']+wave_force
    applicable=(pressure<.999*ue)&(c['acceleration']>1e-10)
    weights=np.diff(model.t)[:,None]*c['lapse']*c['rest_volume']*abs(required)
    a,k=c['acceleration'],c['angular_gradient']
    gates=[]
    for name,lower,upper in (('charged_fermi_skin',np.minimum(a-k,a+2*k),np.maximum(a-k,a+2*k)),
                            ('any_DEC_skin',a-2*abs(k),a+2*abs(k))):
        allowed=((required>=0)&(upper>0))|((required<=0)&(lower<0))|(abs(required)<1e-12)
        bad=~allowed
        it,j=np.unravel_index(np.argmax(abs(required)*bad),required.shape)
        gates.append(dict(skin=name,unsupported_force_weighted_fraction=float(np.sum(weights*bad)/np.sum(weights)),
            maximum_unsupported_force=float(np.max(abs(required)*bad)),peak_time=float(times[it]),peak_x=float(x[j]),
            required_at_peak=float(required[it,j]),lower_force_per_energy_at_peak=float(lower[it,j]),
            upper_force_per_energy_at_peak=float(upper[it,j])))
    it,j=np.unravel_index(np.argmax(np.where(applicable,witness,-np.inf)),witness.shape)
    result=dict(pinned_cells=pinned_cells,evaluation_cells=evaluation_cells,
        maximum_original_holding_force=float(np.max(abs(required))),skins=gates,
        closed_cell_witness_force_weighted_coverage=float(np.sum(weights*applicable)/np.sum(weights)),
        maximum_closed_cell_force_lower_bound=float(witness[it,j]),
        force_witness_peak_time=float(times[it]),force_witness_peak_x=float(x[j]),
        force_witness_pressure_to_electric=float(pressure[it,j]/ue[it,j]),
        force_witness_acceleration=float(a[it,j]),
        force_witness_density_floor=float(density_floor[it,j]),
        force_witness_wave_force=float(wave_force[it,j]))
    stem=f'pinned{pinned_cells}_sample{evaluation_cells}'
    write_json(OUTPUT/(stem+'_force.json'),result)
    pd.DataFrame(dict(x=x,time=times[-1],required_endpoint_completion=required[-1],
        closed_cell_force_lower_bound=witness[-1],witness_applies=applicable[-1],
        acceleration=a[-1],pressure_to_electric=pressure[-1]/ue[-1],
        dec_skin_force_per_energy_min=(a-2*abs(k))[-1],
        dec_skin_force_per_energy_max=(a+2*abs(k))[-1])).to_csv(OUTPUT/(stem+'_fade_force.csv'),index=False)
    return result


def verify_manifest(directory):
    path=directory/'manifest.json'
    manifest=json.loads(path.read_text())
    count=0
    for relative,expected in manifest['input_sha256'].items():
        if sha256_file(ROOT/relative)!=expected:
            raise RuntimeError(f'changed input: {relative}')
        count+=1
    for relative,expected in manifest['output_sha256'].items():
        if sha256_file(directory/relative)!=expected:
            raise RuntimeError(f'changed output: {directory/relative}')
        count+=1
    return count


def comparisons():
    directory=BASE/'composite_capacitor_transport'
    keys=['family','unload_fraction','route','time']
    frames=[pd.read_csv(directory/(stem+'_phases.csv')).set_index(keys)
            for stem in ('n512_geometry2','n1024_geometry2','n1024_geometry4')]
    rows=[]
    for name,a,b in (('512_to_1024_cells',frames[0],frames[1]),('2_to_4_geometry_subdivisions',frames[1],frames[2])):
        absolute=(a.required_negative_null-b.required_negative_null).abs()
        relative=absolute/np.maximum(b.required_negative_null,1e-10)
        rows.append(dict(comparison=name,max_absolute=float(absolute.max()),max_relative=float(relative.max()),
                         relative_peak_case=list(relative.idxmax())))
    records=[]
    for stem in ('n512_geometry2','n1024_geometry2','n1024_geometry4'):
        data=json.loads((directory/(stem+'_summary.json')).read_text())
        records.extend(data['cases'])
    best=frames[-1].reset_index()
    best=best[best.time==best.time.max()]
    selections=[]
    for (family,route),group in best.groupby(['family','route']):
        selections.append(group.loc[group.required_negative_null.idxmin()].to_dict())
    write_json(OUTPUT/'numerical_audit.json',dict(refinements=rows,best_sampled_unloading=selections,
        maximum_work_identity_residual=max(row['maximum_work_identity_residual'] for row in records),
        maximum_stream_balance_residual=max(row['maximum_stream_balance_residual'] for row in records),
        field_time_intervals=257,time_refinement_scope='Transport geometry interpolation; original material/field time history retained.'))


def figures():
    path=BASE/'composite_capacitor_transport/n1024_geometry4_phases.csv'
    data=pd.read_csv(path)
    data=data[data.time==data.time.max()]
    force=pd.read_csv(OUTPUT/'pinned1024_sample4096_fade_force.csv')
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(12,4.5),layout='constrained')
    for family,label,color in (('dec_floor','Anisotropic energy floor','#405e8a'),
                               ('directional','Directional backing + skins','#b7662f')):
        for route,style in (('delivery_drift050','-'),('guide_omitted_tensor_bound','--')):
            group=data[(data.family==family)&(data.route==route)].sort_values('unload_fraction')
            axes[0].plot(group.unload_fraction,group.required_negative_null,style+'o',color=color,
                         markersize=3,label=label+(' (guide omitted)' if style=='--' else ''))
    axes[0].axhline(.262788,color='.4',linewidth=1,label='Earlier assembly comparison')
    axes[0].set(xlabel='Fraction of support unloading sent to the work route',
                ylabel='Fade required negative-null remainder',yscale='log',title='Retention and return remain coupled')
    axes[0].legend(fontsize=7.5)
    axes[1].plot(force.x,force.required_endpoint_completion,label='Endpoint completion required',color='#405e8a')
    selected=force.witness_applies.astype(bool)
    axes[1].plot(force.x,np.where(selected,force.closed_cell_force_lower_bound,np.nan),
                 label='Closed-cell residual: optimistic lower bound',color='#b7662f')
    axes[1].axhline(0,color='.5',linewidth=.8)
    axes[1].set(xlabel='Support-patch coordinate x',ylabel='Material-frame force density',
                title='A longitudinal support channel is still required')
    axes[1].legend(fontsize=7.5)
    for extension in ('png','pdf'):
        fig.savefig(OUTPUT/('composite_capacitor_connections.'+extension),dpi=170)
    plt.close(fig)


def main():
    if OUTPUT.exists():
        raise RuntimeError('preserve completed composite audit')
    directories=[BASE/'composite_capacitor',BASE/'composite_capacitor_transport']
    count=sum(verify_manifest(directory) for directory in directories)
    OUTPUT.mkdir(parents=True)
    with ProcessPoolExecutor(max_workers=3,mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(force_witness,((512,512),(1024,1024),(1024,4096))))
    write_json(OUTPUT/'force_witnesses.json',dict(cases=results,verified_hashes=count))
    comparisons()
    figures()
    sources=[Path(__file__),ROOT/'toolkit/adm_harness_cli/tests/test_composite_capacitor_transport.py']
    sources.extend(directory/'manifest.json' for directory in directories)
    write_json(OUTPUT/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        input_sha256={str(p.relative_to(ROOT)):sha256_file(p) for p in sources},
        output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))
    print(f'composite audit complete; {count} inherited and new hashes checked',flush=True)


if __name__=='__main__':
    main()
