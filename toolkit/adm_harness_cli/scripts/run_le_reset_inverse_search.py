#!/usr/bin/env python3
"""Run the bounded reset construction search and retain numerical evidence."""
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
from scipy.optimize import minimize
from scipy.stats import qmc

from run_le_geometry_boundary import ROOT, save_records
from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.radial_stress import certify_radial_eigensystem, radial_tensor
from adm_harness.reset_inverse_search import (
    BOUNDS, NAMES, construct, controls_from_unit, controls_to_unit, exchange_channels, minimum_energy_lp,
    ordinary_energy_lower_bound, reference_grid,
)
from adm_harness.source_ledger import SourceParams, sha256_file

GRIDS = None
DEADLINE = None


def initialize(reference_path, deadline, worker_memory_mib):
    global GRIDS, DEADLINE
    if worker_memory_mib:
        cap = int(worker_memory_mib)*1024**2
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    GRIDS = {kind:reference_grid(reference_path,129,65,path_kind=kind) for kind in ['direct','waypoints']}
    DEADLINE = deadline


def evaluate(task):
    number, moving, kind, x = task
    if time.monotonic() > DEADLINE:
        return {"candidate": number, "moving": moving, "path_kind":kind,"controls": list(x),
                "status": "budget_exhausted", "objective": 1e9}
    result = construct(GRIDS[kind], x, moving=moving)
    result.update(candidate=number,path_kind=kind,worker_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return result


def local_solve(task):
    number, moving, kind, start, max_evaluations = task
    best, evaluations, exhausted = None, 0, False
    class TimeBudget(Exception):
        pass
    def objective(z):
        nonlocal best, evaluations
        if time.monotonic() > DEADLINE:
            raise TimeBudget()
        x = controls_from_unit(np.clip(z,0.,1.))
        result = construct(GRIDS[kind], x, moving=moving)
        evaluations += 1
        if best is None or result['objective'] < best['objective']:
            best = result
        return result['objective']
    z0 = controls_to_unit(start)
    try:
        objective(z0)
        fit = minimize(objective, z0, method='Powell', bounds=[(0.,1.)]*10,
                       options={"maxfev": max_evaluations, "maxiter": 8, "xtol": .002, "ftol": .002})
        message, converged = str(fit.message), bool(fit.success)
    except TimeBudget:
        message, converged, exhausted = "registered time budget exhausted", False, True
    if best is None:
        best={'status':'budget_exhausted','objective':1e9,'controls':list(start),'moving':moving}
    best.update(candidate=number,path_kind=kind,local_evaluations=evaluations, optimizer_converged=converged,
                optimizer_message=message, budget_exhausted=exhausted,
                worker_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return best


def compact_table(results):
    rows = []
    for result in results:
        row = {k:v for k,v in result.items() if k not in ['controls','fields']}
        row.update(dict(zip(NAMES,result['controls'])))
        rows.append(row)
    return pd.DataFrame(rows)


def reference_energy_bounds(output):
    path = ROOT/'supporting_reports/data/le_coupled_reset_source/prescribed_source.csv.gz'
    frame = pd.read_csv(path)
    summaries, witnesses = [], []
    for (s,level), group in frame.groupby(['s','level']):
        g = group.sort_values('areal_radius')
        r = g.areal_radius.to_numpy()
        h = g.background_enthalpy.to_numpy()
        j = g.j_l.to_numpy()
        bound = ordinary_energy_lower_bound(h,j,branch=1)
        weights = np.r_[np.diff(r)[0]/2, (np.diff(r)[:-1]+np.diff(r)[1:])/2, np.diff(r)[-1]/2]*4*np.pi*r*r
        lp = minimum_energy_lp(h,j,weights,branch=1)
        if not lp.success:
            raise ArithmeticError('positive-branch reference LP did not solve')
        mismatch = abs(lp.fun-weights@bound)
        if mismatch > 1e-7:
            raise ArithmeticError('independent energy bound and LP disagree')
        increment = cumulative_trapezoid(4*np.pi*r*r*(bound-g.released_string_density.to_numpy()),r,initial=0.)
        f_bound = 1-2*(g.reference_static_mass.to_numpy()+increment)/r
        i = int(np.argmin(f_bound))
        summaries.append({'s':s,'level':level,'points':len(r),'min_optimistic_f':float(f_bound[i]),
            'witness_l':float(g.l.iloc[i]),'witness_r':float(r[i]),
            'lp_analytic_objective_error':float(mismatch),'ordinary_energy_lower_bound':float(lp.fun),
            'outer_mass_increment_lower_bound':float(increment[-1]),
            'scope':'fixed reference current and static background; positive total-enthalpy branch'})
        witnesses.extend({'s':s,'level':level,'r':float(rr),'l':float(ll),'minimum_carrier_energy':float(ee),
                          'optimistic_f':float(ff)} for rr,ll,ee,ff in zip(r,g.l,bound,f_bound))
    pd.DataFrame(summaries).to_csv(output/'reference_energy_bounds.csv',index=False)
    pd.DataFrame(witnesses).to_csv(output/'reference_energy_profiles.csv.gz',index=False,
                                  compression={'method':'gzip','mtime':0})
    return summaries


def detailed_candidate(candidate, level, reference_path, output, output_cap_bytes):
    nr, nt = 128*2**level+1, 64*2**level+1
    grid = reference_grid(reference_path,nr,nt,path_kind=candidate['path_kind'])
    result = construct(grid,candidate['controls'],moving=candidate['moving'],retain=True)
    result['level'] = level
    result['candidate'] = candidate['candidate']
    result['path_kind'] = candidate['path_kind']
    if 'fields' not in result:
        return result, []
    fields = result.pop('fields')
    x = candidate['controls']
    e,p,j,pt = [fields['source'][...,i] for i in range(4)]
    eb = fields['background_energy']-fields['released']+fields['background_kinetic']
    pb = fields['background_pressure']+fields['released']+fields['background_kinetic']
    jb = fields['background_current']
    zero = np.zeros_like(e)
    bg = np.stack([eb,pb,jb,fields['background_transverse']],axis=-1)
    material = np.stack([fields['material_density'],x[-2]*fields['material_density'],zero,
                         x[-1]*fields['material_density']],axis=-1)
    plus = .5*(fields['transfer_density']+j-jb)
    minus = .5*(fields['transfer_density']-j+jb)
    outgoing = np.stack([plus,plus,plus,zero],axis=-1)
    incoming = np.stack([minus,minus,-minus,zero],axis=-1)
    components = np.stack([bg,material,outgoing,incoming],axis=0)
    result['max_component_sum_error'] = float(abs(components.sum(axis=0)-fields['source']).max())
    exchanges = np.stack([exchange_channels(fields['time'],fields['radius'],fields['f'],
        -2*fields['mass_t']/fields['radius'],fields['nu_r'],fields['alpha'],component) for component in components])
    core = (slice(2,-2),slice(2,-2))
    result['max_total_energy_exchange_residual'] = float(abs(exchanges.sum(axis=0)[...,0][core]).max())
    result['max_total_force_exchange_residual'] = float(abs(exchanges.sum(axis=0)[...,1][core]).max())
    result['max_null_exchange_direction_error'] = float(max(abs(exchanges[2,...,1]-exchanges[2,...,0]).max(),
                                                         abs(exchanges[3,...,1]+exchanges[3,...,0]).max()))
    carrier_energy = e-eb
    lower_plus = ordinary_energy_lower_bound(eb+pb,j,branch=1,carrier_current=j-jb)
    lower_minus = ordinary_energy_lower_bound(eb+pb,j,branch=-1,carrier_current=j-jb)
    deficit = np.maximum(np.minimum(lower_plus,lower_minus)-carrier_energy,0.)
    result['max_relaxed_carrier_energy_deficit'] = float(deficit.max())
    result['endpoint_source_max_error'] = float(abs(fields['source'][[0,-1]]-
        np.stack([grid.energy,grid.pressure,np.zeros_like(grid.energy),grid.transverse],axis=-1)[[0,-1]]).max())
    result['net_mass_transfer_quadrature_error'] = float(abs(np.trapezoid(-fields['mass_t'],fields['time'],axis=0)-
        (fields['mass'][0]-fields['mass'][-1])).max())
    tag = f"candidate_{candidate['candidate']}_level_{level}"
    uncompressed_bytes=sum(v.nbytes for v in fields.values())+components.nbytes+exchanges.nbytes+deficit.nbytes
    used_bytes=sum(p.stat().st_size for p in output.iterdir() if p.is_file())
    if used_bytes+uncompressed_bytes+2_000_000>output_cap_bytes:
        result['status']='output_budget_exhausted'
        return result,[]
    np.savez_compressed(output/f'{tag}.npz',**fields,components=components,exchanges=exchanges,
                        relaxed_carrier_energy_deficit=deficit)
    # Independent four-dimensional curvature, on the actual interpolated
    # candidate metric. Positive f and alpha are preserved by log interpolation.
    sf = RectBivariateSpline(grid.u,grid.r,np.log(fields['f']),kx=3,ky=3,s=0)
    sa = RectBivariateSpline(grid.u,grid.r,np.log(fields['alpha']),kx=3,ky=3,s=0)
    duration,skew = x[:2]
    def provider(t,r,params):
        tt = np.clip((t-.745)/duration,0.,1.)
        u = 2*tt/(1+skew+np.sqrt((1+skew)**2-4*skew*tt))
        return {'alpha':float(np.exp(sa.ev(u,r))),'beta':0.,
                'gamma_ll':float(np.exp(-sf.ev(u,r))),'gamma_omega':r*r}
    indices = set()
    for field, want_max in [(fields['material_density'],False),(fields['radial_margin'],False),
                            (abs(fields['angular_residual']),True),(deficit,True)]:
        trimmed = field[2:-2,2:-2]
        loc = np.unravel_index(np.argmax(trimmed) if want_max else np.argmin(trimmed),trimmed.shape)
        indices.add((loc[0]+2,loc[1]+2))
    indices.add((len(grid.u)//2,len(grid.r)//2))
    probes = []
    for it,ir in sorted(indices):
        t,r = float(fields['time'][it]),float(grid.r[ir])
        for hh in [.0025,.00125,.000625]:
            row = evaluate_demand(t,r,SourceParams(),hh,hh,scalar_evaluator=provider)
            target = fields['source'][it,ir]
            demanded = np.array([row[k] for k in ['rho','p_l','j_l','p_omega']])
            prescribed = certify_radial_eigensystem(radial_tensor(*target))
            row.update(candidate=candidate['candidate'],level=level,
                prescribed_source_type=prescribed['stress_algebraic_type'],
                prescribed_delta=float(prescribed['radial_block_discriminant']),
                reduced_geometric_max_error=float(abs(demanded-fields['geometric'][it,ir]).max()),
                actual_source_geometric_max_error=float(abs(demanded-target).max()),
                material_density=float(fields['material_density'][it,ir]),
                reduced_angular_residual=float(fields['angular_residual'][it,ir]),
                grid_u=float(grid.u[it]),radius=r)
            probes.append(row)
    return result,probes


def plot_results(output, table, finalist):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(13,4),constrained_layout=True)
    valid=table[table.status.eq('evaluated')]
    for kind in ['direct','waypoints']:
        for moving,label in [(False,'stationary'),(True,'moving')]:
            g=valid[valid.moving.eq(moving)&valid.path_kind.eq(kind)]
            axes[0].scatter(g.min_material_density,g.max_angular_residual,s=10,alpha=.5,label=f'{kind}, {label}')
    axes[0].set(xlabel='minimum material density',ylabel='maximum angular equation residual',yscale='log')
    axes[0].axvline(0,color='black',lw=.7);axes[0].legend(fontsize=7)
    fields=np.load(output/f"candidate_{finalist['candidate']}_level_2.npz")
    r,t=fields['radius'],fields['time']
    for ax,key,title in [(axes[1],'material_density','Material density'),(axes[2],'radial_margin','Radial stress margin')]:
        data=fields[key]
        scale=np.quantile(abs(data),.995)
        mesh=ax.pcolormesh(r,t,data,shading='auto',cmap='coolwarm',vmin=-scale,vmax=scale)
        ax.set(xlabel='areal radius',ylabel='reset time',title=title)
        fig.colorbar(mesh,ax=ax)
    fig.savefig(output/'inverse_search_diagnostic.png',dpi=150)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--sobol-power',type=int,default=8)
    parser.add_argument('--local-evaluations',type=int,default=240)
    parser.add_argument('--budget-seconds',type=float,default=7200.)
    parser.add_argument('--worker-memory-mib',type=int,default=1536)
    parser.add_argument('--output-cap-mb',type=float,default=500.)
    parser.add_argument('--output',type=Path,default=ROOT/'supporting_reports/data/le_reset_inverse_search')
    args=parser.parse_args()
    if args.workers < 1 or not 1 <= args.sobol_power <= 12 or args.budget_seconds <= 0:
        parser.error('positive workers/budget and Sobol power from 1 through 12 required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('output directory must be empty; choose a new --output path for a repeat run')
    args.output.mkdir(parents=True,exist_ok=True)
    started=time.monotonic();deadline=started+args.budget_seconds
    reference_path=ROOT/'supporting_reports/data/le_coupled_reset_source/reference_tensors.csv.gz'
    kernel=ROOT/'toolkit/adm_harness_cli/adm_harness/source_ledger.py'
    manifest0=json.loads((ROOT/'supporting_reports/data/le_coupled_reset_source/manifest.json').read_text())
    if sha256_file(kernel) != manifest0['source_kernel_sha256']:
        raise ValueError('frozen source kernel changed')
    bounds=reference_energy_bounds(args.output)
    sample=qmc.Sobol(d=10,scramble=True,rng=8172026).random_base2(args.sobol_power)
    controls=controls_from_unit(sample)
    tasks=[]
    for x in controls:
        for kind in ['direct','waypoints']:
            for moving in [False,True]:
                tasks.append((len(tasks),moving,kind,x.tolist()))
    # Boundary controls are additional analytic seeds, outside the Sobol batch.
    for kind in ['direct','waypoints']:
        for moving in [False,True]:
            for release,amount in [(0.,0.),(.05,0.),(.2,.04),(.5,.12)]:
                tasks.append((len(tasks),moving,kind,[14.255,.5,amount,2.65,.25,4.8,.45,release,1.,.25]))
    results=[];last=started
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn'),
        initializer=initialize,initargs=(str(reference_path),deadline,args.worker_memory_mib)) as pool:
        for result in pool.map(evaluate,tasks,chunksize=4):
            results.append(result)
            if time.monotonic()-last > 20:
                print(f"exploration {len(results)}/{len(tasks)}, best objective {min(x['objective'] for x in results):.5g}",flush=True)
                last=time.monotonic()
        compact_table(results).to_csv(args.output/'exploration.csv',index=False)
        seeds=[]
        for kind in ['direct','waypoints']:
            for moving in [False,True]:
                group=sorted([r for r in results if r['moving']==moving and r['path_kind']==kind and r['status']=='evaluated'],key=lambda x:x['objective'])
                for seed in group:
                    z=controls_to_unit(seed['controls'])
                    if all(np.linalg.norm(z-controls_to_unit(s[3]))>.1 for s in seeds if s[1]==moving and s[2]==kind):
                        seeds.append((len(tasks)+len(seeds),moving,kind,seed['controls'],args.local_evaluations))
                    if sum(s[1]==moving and s[2]==kind for s in seeds)==2:
                        break
        refinements=[]
        for result in pool.map(local_solve,seeds):
            refinements.append(result)
            print(f"local solve {len(refinements)}/{len(seeds)}, best objective {result['objective']:.5g}",flush=True)
    compact_table(refinements).to_csv(args.output/'local_solves.csv',index=False)
    ranked=sorted([r for r in results+refinements if r['status']=='evaluated'],key=lambda x:x['objective'])
    finalists=[]
    for candidate in ranked:
        if all(np.linalg.norm(controls_to_unit(candidate['controls'])-controls_to_unit(c['controls']))>.05
               or candidate['moving']!=c['moving'] or candidate['path_kind']!=c['path_kind'] for c in finalists):
            finalists.append(candidate)
        if len(finalists)==3:
            break
    summaries,probes=[],[]
    for candidate in finalists:
        for level in range(3):
            if time.monotonic()>deadline:
                break
            summary,rows=detailed_candidate(candidate,level,reference_path,args.output,args.output_cap_mb*1e6)
            summaries.append(summary);probes.extend(rows)
            print(f"candidate {candidate['candidate']} refinement {level}: {summary['status']}, objective {summary['objective']:.5g}",flush=True)
            if sum(p.stat().st_size for p in args.output.iterdir() if p.is_file())>args.output_cap_mb*1e6:
                raise RuntimeError('registered output cap exceeded')
    compact_table(summaries).to_csv(args.output/'refinement_summary.csv',index=False)
    if probes:
        save_records(probes,args.output,'independent_curvature_probes')
    if finalists and (args.output/f"candidate_{finalists[0]['candidate']}_level_2.npz").exists():
        plot_results(args.output,compact_table(results+refinements),finalists[0])
    survivors=[r for r in summaries if r.get('local_necessary_conditions_pass') and r['level']==2]
    metadata={'completed_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-started,
        'workers':args.workers,'worker_address_space_cap_mib':args.worker_memory_mib,
        'compute_budget_seconds':args.budget_seconds,'output_cap_mb':args.output_cap_mb,
        'sobol_candidates':4*len(controls),'additional_seed_controls':len(tasks)-4*len(controls),
        'local_solves':len(refinements),'local_evaluations':sum(r['local_evaluations'] for r in refinements),
        'control_names':NAMES,'bounds':BOUNDS.tolist(),'finalists':[r['candidate'] for r in finalists],
        'families':['direct/stationary','direct/moving','waypoints/stationary','waypoints/moving'],
        'compute_budget_exhausted':bool(time.monotonic()>deadline or any(r['status']=='budget_exhausted' for r in results)),
        'completed_exploration':sum(r['status']!='budget_exhausted' for r in results),
        'completed_refinements':len(summaries),
        'output_budget_exhausted':any(r['status']=='output_budget_exhausted' for r in summaries),
        'amplitude_coordinate_mapping':'A and string release use 1e-5*expm1(z*log1p(upper/1e-5)); other controls are linear',
        'local_necessary_survivors':[r['candidate'] for r in survivors],
        'status':'local_candidate_requires_remaining_closure_and_rail_matching' if survivors else 'bounded_search_found_no_local_construction',
        'full_rail_service_certified':False,'microscopic_source_realization_certified':False,
        'universal_infeasibility_claim':False,
        'source_kernel_sha256':sha256_file(kernel),'reference_sha256':sha256_file(reference_path),
        'software_sha256':{str(p.relative_to(ROOT)):sha256_file(p) for p in [Path(__file__).resolve(),
            ROOT/'toolkit/adm_harness_cli/adm_harness/reset_inverse_search.py',
            ROOT/'toolkit/adm_harness_cli/adm_harness/geometry_boundary.py',
            ROOT/'toolkit/adm_harness_cli/adm_harness/radial_stress.py']},
        'independent_curvature_probes':len(probes),
        'max_reference_lp_error':max(x['lp_analytic_objective_error'] for x in bounds),
        'max_worker_peak_rss_kib':max(r.get('worker_peak_rss_kib',0) for r in results+refinements),
        'parent_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'output_bytes_before_manifest':sum(p.stat().st_size for p in args.output.iterdir() if p.is_file())}
    (args.output/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps({k:metadata[k] for k in ['status','elapsed_seconds','sobol_candidates','local_evaluations',
        'local_necessary_survivors','output_bytes_before_manifest']}),flush=True)


if __name__=='__main__':
    main()
