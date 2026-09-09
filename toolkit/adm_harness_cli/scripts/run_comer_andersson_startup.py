#!/usr/bin/env python3
"""Bounded spherical model-(iii) rate, heat-budget, and kinetic diagnostic."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import json
import multiprocessing
from pathlib import Path
import resource
import time

import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import RectBivariateSpline

from run_le_geometry_boundary import ROOT, save_records
from adm_harness.comer_andersson_startup import (
    areal_rates, cattaneo_required_drive, entropy_embedding, fit_constant_rate_response,
    heat_from_energy_current, kinetic_conditions, minimum_heat_energy,
    quadratic_rate_channels, startup_orders,
)
from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.reset_inverse_search import polar_areal_channels, reference_grid
from adm_harness.source_ledger import SourceParams, sha256_file


CONTROLS = [
    ('zero_rate', 0., 0.),
    ('exact_tensor_match', 1., -1.),
    ('positive_bulk', 1., 0.),
    ('positive_squared_rate', 0., 1.),
    ('near_match_positive_tensor_kinetic', .975, -.95),
    ('negative_tensor_kinetic', 1., -1.25),
]


def symbolic_variation_audit():
    import sympy as sp
    t = sp.symbols('t', real=True)
    lapse = sp.Function('N')(t)
    qs = [sp.Function(f'q{i}')(t) for i in range(3)]
    a, b = sp.symbols('a b', real=True)
    rates = [q.diff(t)/lapse for q in qs]
    theta = sum(rates)
    q = (a*theta**2+b*sum(h*h for h in rates))/2
    volume = sp.exp(sum(qs))
    lagrangian = lapse*volume*q
    residuals = [sp.simplify(-sp.diff(lagrangian,lapse)/volume-q)]
    for i in range(3):
        derivative = (sp.diff(lagrangian,qs[i])-sp.diff(sp.diff(lagrangian,qs[i].diff(t)),t))/(lapse*volume)
        conjugate = a*theta+b*rates[i]
        residuals.append(sp.simplify(derivative-(q-conjugate.diff(t)/lapse-theta*conjugate)))
    assert residuals == [0,0,0,0]
    kinetic = (sum(h*h for h in rates)-theta**2)/(16*sp.pi)+q
    cancellation = sp.simplify(kinetic.subs({a:1/(8*sp.pi),b:-1/(8*sp.pi)}))
    assert cancellation == 0
    return {'density_and_three_pressure_variation_residuals':[str(x) for x in residuals],
            'total_adm_kinetic_density_at_exact_match':str(cancellation),
            'tensor_kinetic_ratio':'1 + 8*pi*b',
            'source_match_coefficients':{'a':'1/(8*pi)','b':'-1/(8*pi)'},
            'variation_precedes_areal_restriction':True}


def fields_for_grid(grid, duration, skew):
    r, u = grid.r, grid.u
    t = .745+duration*(u+skew*u*(1-u))
    tu, tuu = duration*(1+skew*(1-2*u)), -2*duration*skew
    ft = -2*grid.mass_u/(r*tu[:,None])
    ftt = -2*(grid.mass_uu/tu[:,None]**2-grid.mass_u*tuu/tu[:,None]**3)/r
    alpha, nu_t = np.exp(grid.nu), grid.nu_u/tu[:,None]
    h, dh = areal_rates(grid.f,ft,ftt,alpha,nu_t)
    geometric = polar_areal_channels(r,grid.f,grid.f_r,ft,ftt,grid.nu,grid.nu_r,grid.nu_rr,nu_t)
    current = -np.sqrt(grid.f)*h/(4*np.pi*r)
    current_dot = -np.sqrt(grid.f)*(dh-h*h)/(4*np.pi*r)
    # Tolman temperature at the initial static slice, followed by a comoving
    # adiabatic reference. This sets a diagnostic thermal scale, not a solved
    # two-current temperature or conserved heat-carrier evolution.
    thermal_shape = np.exp(4*(grid.nu[0,-1]-grid.nu[0]))*(grid.f/grid.f[0])**(2/3)
    return {'time':t,'f':grid.f,'alpha':alpha,'radial_rate':h,'radial_rate_dot':dh,
            'current':current,'current_dot':current_dot,
            'angular_time_demand':-(dh+h*h)/(8*np.pi),'geometric':geometric,
            'thermal_shape':thermal_shape}


def curvature_probes(grid, fields, duration, skew, scenario, level):
    sf = RectBivariateSpline(grid.u,grid.r,np.log(fields['f']),kx=3,ky=3,s=0)
    sa = RectBivariateSpline(grid.u,grid.r,np.log(fields['alpha']),kx=3,ky=3,s=0)
    def clock_inverse(t):
        v = np.clip((t-.745)/duration,0.,1.)
        return 2*v/(1+skew+np.sqrt((1+skew)**2-4*skew*v))
    def provider(t,r,params):
        u = clock_inverse(t)
        return {'alpha':float(np.exp(sa.ev(u,r))),'beta':0.,
                'gamma_ll':float(np.exp(-sf.ev(u,r))),'gamma_omega':r*r}
    g = fields['geometric']
    delta = (g[...,0]+g[...,1])**2-4*g[...,2]**2
    indices = {(len(grid.u)//2,len(grid.r)//2)}
    for values in [delta,-abs(fields['angular_time_demand'])]:
        j,k = np.unravel_index(np.argmin(values[2:-2,2:-2]),values[2:-2,2:-2].shape)
        indices.add((j+2,k+2))
    rows = []
    for sample,(it,ir) in enumerate(sorted(indices)):
        u,r,t = float(grid.u[it]),float(grid.r[ir]),float(fields['time'][it])
        tu,tuu = duration*(1+skew*(1-2*u)),-2*duration*skew
        f = float(np.exp(sf.ev(u,r)))
        lu,luu = float(sf.ev(u,r,dx=1)),float(sf.ev(u,r,dx=2))
        alpha,nu_t = float(np.exp(sa.ev(u,r))),float(sa.ev(u,r,dx=1)/tu)
        ft,ftt = f*lu/tu,f*((luu+lu*lu)/tu**2-lu*tuu/tu**3)
        h,dh = areal_rates(f,ft,ftt,alpha,nu_t)
        correction = quadratic_rate_channels(h,0.,dh,0.,1/(8*np.pi),-1/(8*np.pi))
        correction[2] = ft/(8*np.pi*r*alpha*np.sqrt(f))
        for step in [.0025,.00125,.000625]:
            dynamic = evaluate_demand(t,r,SourceParams(),step,step,scalar_evaluator=provider)
            static = evaluate_demand(t,r,SourceParams(),step,step,holding=True,scalar_evaluator=provider)
            difference = np.array([dynamic[k]-static[k] for k in ['rho','p_l','j_l','p_omega']])
            error = float(abs(difference-correction).max())
            for mode,row in [('dynamic',dynamic),('holding',static)]:
                row.update(scenario=scenario,level=level,sample=sample,mode=mode,
                           dynamic_difference_max_error=error,
                           rate_angular_pressure=float(correction[3]),
                           required_current=float(correction[2]))
                rows.append(row)
    return rows


def run_scenario(task):
    scenario,kind,duration,skew,reference,output,deadline,memory_mib = task
    resource.setrlimit(resource.RLIMIT_AS,(memory_mib*1024**2,memory_mib*1024**2))
    output = Path(output)
    finest = reference_grid(reference,513,257,path_kind=kind)
    finest_fields = fields_for_grid(finest,duration,skew)
    # Use one fixed positive normalization across every resolution and rate
    # control. It makes all entropy roots real and bounds the kinematic heat
    # drift. Its mass cost is recorded explicitly, without adding it to the rail.
    shape = finest_fields['thermal_shape']
    h = finest_fields['radial_rate']
    heat_floor = minimum_heat_energy(finest_fields['current'],.1)
    q_positive = h*h/(16*np.pi)
    normalization = 1.05*max(1e-6,float((heat_floor/shape).max()),float((2*q_positive/shape).max()))
    initial_energy = normalization*shape[0]
    added_mass = cumulative_trapezoid(4*np.pi*finest.r**2*initial_energy,finest.r,initial=0.)
    preload = {'scenario':scenario,'path_kind':kind,'duration':duration,'time_skew':skew,
        'thermal_normalization':normalization,'diagnostic_initial_thermal_mass':float(added_mass[-1]),
        'min_f_if_thermal_energy_is_added_to_frozen_initial_source':float((finest.f[0]-2*added_mass/finest.r).min()),
        'scope':'Tolman initial and comoving adiabatic thermal reference; carrier kinematics and mass price only'}
    summaries, fits, probes, onsets = [],[],[],[]
    for level in range(3):
        if time.monotonic()>deadline:
            raise TimeoutError('bounded diagnostic exceeded its compute allowance')
        grid = finest if level==2 else reference_grid(reference,128*2**level+1,64*2**level+1,path_kind=kind)
        fields = finest_fields if level==2 else fields_for_grid(grid,duration,skew)
        h,dh = fields['radial_rate'],fields['radial_rate_dot']
        energy = normalization*fields['thermal_shape']
        heat = heat_from_energy_current(energy,fields['current'])
        fit = fit_constant_rate_response(h,dh)
        fit.update(scenario=scenario,level=level,path_kind=kind)
        fits.append(fit)
        g = fields['geometric']
        for name,aa,bb in CONTROLS:
            a,b = aa/(8*np.pi),bb/(8*np.pi)
            rate = quadratic_rate_channels(h,0.,dh,0.,a,b)
            q = rate[...,0]
            qdot = (a+b)*h*dh
            entropy = entropy_embedding(energy,q,qdot,h)
            assert entropy['valid'].all()
            mismatch = np.stack([rate[...,0],rate[...,1],rate[...,3]-fields['angular_time_demand']],axis=-1)
            row = {'scenario':scenario,'path_kind':kind,'duration':duration,'time_skew':skew,
                'level':level,'control':name,'a_times_8pi':aa,'b_times_8pi':bb,
                'max_density_change':float(abs(rate[...,0]).max()),
                'max_radial_pressure_change':float(abs(rate[...,1]).max()),
                'max_angular_mismatch':float(abs(mismatch[...,2]).max()),
                'max_three_channel_mismatch':float(abs(mismatch).max()),
                'min_comoving_entropy_rate_per_entropy':float(entropy['entropy_rate_per_entropy'].min()),
                'max_comoving_entropy_rate_per_entropy':float(entropy['entropy_rate_per_entropy'].max()),
                'min_entropy_factor':float(entropy['entropy_factor'].min()),
                'max_entropy_factor':float(entropy['entropy_factor'].max()),
                'max_heat_drift':float(abs(heat['velocity']).max()),
                'min_heat_rest_energy':float(heat['rest_energy'].min()),
                'min_geometric_radial_discriminant':float(((g[...,0]+g[...,1])**2-4*g[...,2]**2).min()),
                'points':int(h.size),**kinetic_conditions(a,b)}
            row['fixed_path_rate_gate_pass'] = bool(row['max_three_channel_mismatch']<1e-9
                and row['tensor_kinetic_strictly_positive']
                and row['min_comoving_entropy_rate_per_entropy']>=-1e-12)
            summaries.append(row)
        probes.extend(curvature_probes(grid,fields,duration,skew,scenario,level))
        if level==2:
            thermal_expansion = {name:entropy_embedding(energy,
                quadratic_rate_channels(h,0.,dh,0.,aa/(8*np.pi),bb/(8*np.pi))[...,0],
                (aa+bb)*h*dh/(8*np.pi),h)['entropy_rate_per_entropy']
                for name,aa,bb in CONTROLS if name in ['positive_bulk','near_match_positive_tensor_kinetic']}
            np.savez_compressed(output/f'{scenario}_fields.npz',radius=grid.r,u=grid.u,
                **{k:v for k,v in fields.items() if k!='thermal_shape'},
                diagnostic_thermal_energy=energy,heat_drift=heat['velocity'],heat_rest_energy=heat['rest_energy'],
                required_cattaneo_drive=cattaneo_required_drive(fields['current'],fields['current_dot'],1.,1.),
                **{f'{name}_entropy_rate':values for name,values in thermal_expansion.items()})
    # Resolve the onset orders directly; no subtraction of a static transverse
    # pressure is needed for the exactly known time-curvature channel.
    u = np.r_[0.,2.**(-np.arange(12,2,-1)),1.]
    grid = reference_grid(reference,129,path_kind=kind,u_values=u)
    fields = fields_for_grid(grid,duration,skew)
    n = 3 if kind=='direct' else 9
    for name,aa,bb in CONTROLS:
        h,dh = fields['radial_rate'][:,-1],fields['radial_rate_dot'][:,-1]
        energy = normalization*fields['thermal_shape'][:,-1]
        rate = quadratic_rate_channels(h,0.,dh,0.,aa/(8*np.pi),bb/(8*np.pi))
        entropy = entropy_embedding(energy,rate[:,0],(aa+bb)*h*dh/(8*np.pi),h)
        for i in range(1,len(u)-1):
            onsets.append({'scenario':scenario,'path_kind':kind,'control':name,'u':float(u[i]),
                'angular_time_demand':float(fields['angular_time_demand'][i,-1]),
                'rate_radial_pressure':float(rate[i,1]),'rate_angular_pressure':float(rate[i,3]),
                'density_change':float(rate[i,0]),
                'comoving_entropy_rate_per_entropy':float(entropy['entropy_rate_per_entropy'][i]),
                'scaled_angular_demand':float(fields['angular_time_demand'][i,-1]/u[i]**(n-2)),
                'scaled_rate_angular_pressure':float(rate[i,3]/u[i]**(n-2)),
                'scaled_entropy_rate':float(entropy['entropy_rate_per_entropy'][i]/u[i]**(2*n-3))})
    return {'summaries':summaries,'fits':fits,'probes':probes,'onsets':onsets,'preload':preload,
            'worker_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def plot_results(output, summaries, onsets):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes = plt.subplots(1,3,figsize=(13,4),constrained_layout=True)
    g = onsets[onsets.scenario.eq('direct_fast')]
    demand = g[g.control.eq('exact_tensor_match')]
    axes[0].loglog(demand.u,abs(demand.angular_time_demand),'k-',label='required angular stress')
    for name,label in [('exact_tensor_match','quadratic exact match'),('positive_bulk','positive bulk rate')]:
        sub = g[g.control.eq(name)]
        axes[0].loglog(sub.u,abs(sub.rate_angular_pressure),'--',label=label)
    axes[0].set(xlabel='startup parameter u',ylabel='absolute angular time stress',title='Early angular response')
    axes[0].legend(fontsize=7);axes[0].grid(alpha=.2)
    sub = summaries[(summaries.level==2)&summaries.scenario.eq('direct_fast')]
    for row in sub.itertuples():
        axes[1].scatter(row.tensor_kinetic_ratio,max(row.max_three_channel_mismatch,1e-18),s=35)
        axes[1].annotate(row.control.replace('_',' '),(row.tensor_kinetic_ratio,max(row.max_three_channel_mismatch,1e-18)),
                         fontsize=6,xytext=(3,5),textcoords='offset points')
    axes[1].axvline(0,color='black',lw=.8)
    axes[1].set(yscale='log',xlabel='gravitational tensor kinetic coefficient / GR',
                ylabel='maximum density / radial / angular mismatch',title='Tensor fit and kinetic regularity')
    axes[1].grid(alpha=.2)
    with np.load(output/'direct_fast_fields.npz') as data:
        radius_index = len(data['radius'])//2
        for name,label in [('positive_bulk','positive bulk rate'),('near_match_positive_tensor_kinetic','near match')]:
            axes[2].plot(data['time'],data[f'{name}_entropy_rate'][:,radius_index],label=label)
    axes[2].axhline(0,color='black',lw=.8)
    axes[2].set(xlabel='reset time',ylabel='convective entropy production / entropy',
                title='Entropy test of the explicit rate functional')
    axes[2].legend(fontsize=7);axes[2].grid(alpha=.2)
    fig.savefig(output/'comer_startup_diagnostic.png',dpi=170)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--budget-seconds',type=float,default=600.)
    parser.add_argument('--worker-memory-mib',type=int,default=1536)
    parser.add_argument('--output-cap-mb',type=float,default=100.)
    parser.add_argument('--output',type=Path,default=ROOT/'supporting_reports/data/comer_andersson_startup')
    args = parser.parse_args()
    if args.workers<1 or args.budget_seconds<=0 or args.output_cap_mb<=0:
        parser.error('positive worker count and budgets required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    args.output.mkdir(parents=True,exist_ok=True)
    started = time.monotonic()
    reference = ROOT/'supporting_reports/data/le_coupled_reset_source/reference_tensors.csv.gz'
    kernel = ROOT/'toolkit/adm_harness_cli/adm_harness/source_ledger.py'
    expected = json.loads((ROOT/'supporting_reports/data/le_reset_inverse_search/manifest.json').read_text())
    if sha256_file(kernel)!=expected['source_kernel_sha256'] or sha256_file(reference)!=expected['reference_sha256']:
        raise ValueError('the frozen source or reference data changed')
    symbolic = symbolic_variation_audit()
    (args.output/'symbolic_variation_audit.json').write_text(json.dumps(symbolic,indent=2)+'\n')
    tasks = [(f'{kind}_{clock}',kind,duration,skew,str(reference),str(args.output),
              started+args.budget_seconds,args.worker_memory_mib)
             for kind in ['direct','waypoints'] for clock,duration,skew in [('fast',4.,-.65),('slow',14.255,.65)]]
    results = []
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
        for result in pool.map(run_scenario,tasks):
            results.append(result)
            print(f"completed {result['preload']['scenario']}",flush=True)
            if sum(p.stat().st_size for p in args.output.iterdir() if p.is_file())>args.output_cap_mb*1e6:
                raise RuntimeError('bounded diagnostic exceeded its output allowance')
    frames = {}
    for name in ['summaries','fits','onsets']:
        frames[name] = pd.DataFrame([row for result in results for row in result[name]])
        frames[name].to_csv(args.output/f'{name}.csv',index=False)
    pd.DataFrame([r['preload'] for r in results]).to_csv(args.output/'thermal_scale_accounting.csv',index=False)
    pd.DataFrame([{'path_kind':kind,**startup_orders(n)} for kind,n in [('direct',3),('waypoints',9)]]).to_csv(
        args.output/'startup_orders.csv',index=False)
    probes = [row for result in results for row in result['probes']]
    probe_frame = save_records(probes,args.output,'independent_curvature_probes')
    if not probe_frame.full_eigensystem_certified.all():
        raise ArithmeticError('a retained curvature eigensystem failed certification')
    survivors = frames['summaries'][frames['summaries'].fixed_path_rate_gate_pass]
    plot_results(args.output,frames['summaries'],frames['onsets'])
    size = sum(p.stat().st_size for p in args.output.iterdir() if p.is_file())
    if size>args.output_cap_mb*1e6:
        raise RuntimeError('bounded diagnostic exceeded its output allowance')
    metadata = {'completed_utc':datetime.now(timezone.utc).isoformat(),
        'status':('local_rate_candidate_requires_full_two_current_evolution' if len(survivors)
                  else 'minimal_model_iii_rate_specialization_rejected'),
        'scope':'fixed static-start paths; published onset closure and one quadratic rate-action choice',
        'elapsed_seconds':time.monotonic()-started,'workers':args.workers,
        'scenarios':len(tasks),'refinements':len(frames['fits']),'rate_controls':len(CONTROLS),
        'evaluations':len(frames['summaries']),'curvature_records':len(probes),
        'rate_gate_survivors':survivors[['scenario','level','control']].to_dict('records'),
        'max_worker_peak_rss_kib':max(r['worker_peak_rss_kib'] for r in results),
        'parent_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'worker_address_space_cap_mib':args.worker_memory_mib,
        'compute_cap_seconds':args.budget_seconds,'output_cap_mb':args.output_cap_mb,
        'output_bytes_before_manifest':size,
        'source_kernel_sha256':sha256_file(kernel),'reference_sha256':sha256_file(reference),
        'full_two_current_evolution_solved':False,'full_rail_service_certified':False,
        'general_comer_andersson_framework_excluded':False,
        'software_sha256':{str(p.relative_to(ROOT)):sha256_file(p) for p in [Path(__file__).resolve(),
            ROOT/'toolkit/adm_harness_cli/adm_harness/comer_andersson_startup.py',
            ROOT/'toolkit/adm_harness_cli/adm_harness/reset_inverse_search.py']},
        'paper_sources':[
            'https://arxiv.org/html/2606.17686v1',
            'https://eprints.soton.ac.uk/495878/1/entropy-26-00621.pdf']}
    (args.output/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps({k:metadata[k] for k in ['status','elapsed_seconds','evaluations',
        'curvature_records','output_bytes_before_manifest']}),flush=True)


if __name__=='__main__':
    main()
