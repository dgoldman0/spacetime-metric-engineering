#!/usr/bin/env python3
"""Independent radial equation, trace, conservation and fixed-budget checks."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import argparse
import json
import multiprocessing
import shutil

import numpy as np
from scipy.integrate import solve_ivp

from adm_harness.c1_angular_absolute import AbsoluteComparison, NativeMetric, conformal_log_source, conformal_anomaly
from adm_harness.c1_angular_response import improved_tensor
from adm_harness.c1_angular_scalar import scalar_curvature
from adm_harness.c1_signed_channels import dec_projections
from screen_c1_angular_absolute import chart, run_case
from screen_c1_angular_response import ROOT, digest, retained_rows, remainder, load_chart, verify_manifest


def independent_mode(g, domain, x, w, j, mass):
    """Integrate phi/phi_l directly in the original coordinate, using DOP853."""
    r0,a0,*_ = g.jets(np.array([x]))
    frequency = w*a0[0]

    def rhs(coordinate, h):
        r,a,b,rp,_,ap,_ = g.jets(np.array([coordinate]))
        q = frequency**2/a[0]**2+j*(j+1)/r[0]**2+mass**2+scalar_curvature(g,np.array([coordinate]))[0]/6
        return b[0]*(1+(ap[0]+2*rp[0]/r[0])*h-q*h*h)

    slopes=[]
    for end in domain:
        solution=solve_ivp(rhs,(end,x),[0.],method='DOP853',rtol=2e-11,atol=2e-13)
        if not solution.success:
            raise RuntimeError(solution.message)
        slopes.append(1/solution.y[0,-1])
    left,right = slopes
    f=np.array([1/(r0[0]**2*(left-right))])
    native=improved_tensor(g,np.array([x]),frequency,j,f,(left+right)*f,left*right*f)[0]
    native+=mass*mass*f[0]*np.array([1/6,-1/2,-1/6])
    k=np.sqrt(w*w+(j*(j+1)+1/3)/r0[0]**2+mass*mass)
    cylinder=np.array([-w*w,-k*k,(j*(j+1)+1/3)/(2*r0[0]**2)])/(2*r0[0]**2*k)
    return native-cylinder


def mode_job(task):
    spec,domain,x,w,j,mass=task
    g=chart(spec)
    exact=independent_mode(g,domain,x,w,j,mass)
    actual=AbsoluteComparison(g,domain,x).differences(w,j,mass,phase_step=.01,single_mass=True)
    return dict(domain=domain,coordinate=x,frequency=w,harmonic=j,mass=mass,
                independent=exact.tolist(),shooting=actual.tolist(),
                absolute_error=float(abs(exact-actual).max()),
                relative_error=float(abs(exact-actual).max()/max(abs(exact).max(),1e-100)))


def extrapolate(rows,source,coordinate):
    selected=[r for r in rows if r['source']==source and r['coordinate']==coordinate
              and r['name'] in ('base','cutoff_control')]
    masses=sorted(set(r['mass'] for r in selected))
    mass_values=[]
    for mass in masses:
        pair=sorted([r for r in selected if r['mass']==mass],key=lambda r:r['cut'])
        if len(pair)>1:
            lo,hi=pair[-2:]
            factor=(hi['cut']/lo['cut'])**4
            value=(factor*np.array(hi['tensor'])-np.array(lo['tensor']))/(factor-1)
        else:
            value=np.array(pair[0]['tensor'])
        mass_values.append(value)
    masses,values=np.array(masses[-3:]),np.array(mass_values[-3:])
    quadratic=np.polynomial.polynomial.polyfit(masses**-2,values,2)[0]
    linear=np.polynomial.polynomial.polyfit(masses[-2:]**-2,values[-2:],1)[0]
    return dict(masses=masses.tolist(),mass_tensors=values.tolist(),tensor=quadratic.tolist(),
                linear_tensor=linear.tolist(),fit_spread=(quadratic-linear).tolist())


def population_interval(target, source):
    a,b=dec_projections(target),dec_projections(source)
    lower=max(0.,max((ai/bi for ai,bi in zip(a,b) if bi<0),default=0.))
    upper=min((ai/bi for ai,bi in zip(a,b) if bi>0),default=np.inf)
    return dict(lower=float(lower),upper=float(upper) if np.isfinite(upper) else None,
                feasible=bool(lower<=upper and np.all(a[b==0]>=0)))


def geometry_controls(spec):
    """Check fourth derivatives against fresh evaluations of the archived metric."""
    from numpy.polynomial import Polynomial
    from adm_harness.metric_regularity import regularized_scalars
    from adm_harness.source_ledger import SourceParams
    params=SourceParams(**json.loads((ROOT/'supporting_reports/data/le_coupled_reset_source/manifest.json').read_text())['params'])
    result=[]
    for width in (.02,.04):
        x=np.linspace(-width,width,101)
        values=[regularized_scalars(.745,float(xx),params) for xx in x]
        arrays=np.array([[np.sqrt(v['gamma_omega']),v['alpha'],np.sqrt(v['gamma_ll'])] for v in values]).T
        polynomials=[Polynomial.fit(x,np.log(a),12).convert() for a in arrays]
        surrogate=object.__new__(NativeMetric)
        surrogate.splines=[lambda x,n=0,p=p:p.deriv(n)(x) for p in polynomials]
        jets=surrogate.proper_log_jets(0.)
        result.append(dict(method='native_evaluator_polynomial',width=width,jets=jets.tolist(),
                           log_source=conformal_log_source(*jets).tolist(),anomaly=float(conformal_anomaly(*jets))))
    for stride in (1,2,4):
        g=chart(spec,stride);jets=g.proper_log_jets(0.)
        result.append(dict(method='cached_samples',stride=stride,jets=jets.tolist(),
                           log_source=conformal_log_source(*jets).tolist(),anomaly=float(conformal_anomaly(*jets))))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,default=ROOT/'supporting_reports/data/c1_angular_absolute')
    parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    if args.workers<1:
        parser.error('positive workers required')
    verified=verify_manifest(args.data/'manifest.json')
    summary=json.loads((args.data/'summary.json').read_text())
    spec=json.loads((ROOT/summary['specification']).read_text())
    rows=summary['cases']; g=chart(spec)
    modes=[]
    for source,x in (('broad_left',0.),('broad_left',.75),('shared_right',.75)):
        domain=next(r['domain'] for r in rows if r['source']==source)
        modes.extend((spec,domain,x,w,j,m) for w,j,m in ((.5,0,0.),(1.,1,0.),(1.,0,2.)))
    center=next(r for r in rows if r['source']=='broad_left' and r['coordinate']==.75
                and r['mass']==4.)
    ward_tasks=[]
    for i,offset in enumerate((-.002,-.001,.001,.002)):
        case={key:center[key] for key in ('source','domain','mass','cut','frequency_order',
                                         'phase_step','proper_spacing','attenuation','stride')}
        case.update(id=100+i,coordinate=.75+offset,name='ward_control')
        ward_tasks.append((spec,case,summary['calibration'],str(args.data)))
    regulator_tasks=[]
    for source in ('broad_left','shared_right'):
        original=next(r for r in rows if r['source']==source and r['coordinate']==.75)
        for cut in (16.,32.):
            case={key:original[key] for key in ('source','domain','frequency_order',
                                               'phase_step','proper_spacing','attenuation','stride')}
            case.update(id=200+len(regulator_tasks),coordinate=.75,name='cutoff_control',mass=16.,cut=cut)
            regulator_tasks.append((spec,case,summary['calibration'],str(args.data)))
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
        independent=list(pool.map(mode_job,modes))
        ward_rows=list(pool.map(run_case,ward_tasks))
        regulator_rows=list(pool.map(run_case,regulator_tasks))
    rows=rows+regulator_rows
    tensors=np.array([ward_rows[0]['tensor'],ward_rows[1]['tensor'],center['tensor'],
                      ward_rows[2]['tensor'],ward_rows[3]['tensor']])
    r,_,b,rp,_,ap,_=g.jets(np.array([.75])); p=tensors[:,1]
    derivative=(p[0]-8*p[1]+8*p[3]-p[4])/(12*.001*b[0])
    residual=derivative+ap[0]*(tensors[2,0]+tensors[2,1])+2*rp[0]/r[0]*(tensors[2,1]-tensors[2,2])
    ward=dict(coordinate=.75,mass=4.,coordinate_step=.001,
              residual=float(residual),radius_scaled_relative=float(abs(residual)*r[0]/max(abs(tensors[2]))))
    limits={f'{source}_{x}':extrapolate(rows,source,x) for source,x in
            (('broad_left',0.),('broad_left',.75),('shared_right',.75))}
    for key,limit in limits.items():
        source,coordinate=key.rsplit('_',1)
        anomaly=next(r['anomaly'] for r in rows if r['source']==source and r['coordinate']==float(coordinate))
        t=np.array(limit['tensor'])
        limit['trace_error']=float(-t[0]+t[1]+2*t[2]-anomaly)
        limit['anomaly']=anomaly
    throat=limits['broad_left_0.0']; t=np.array(throat['tensor'])
    anomaly=rows[0]['anomaly']
    throat['trace_error']=float(-t[0]+t[1]+2*t[2]-anomaly)
    throat['anomaly']=anomaly
    parent=json.loads((ROOT/spec['parent_specification']).read_text())
    retained=retained_rows(spec); fixed_chart=load_chart(spec)
    eta=parent['eta']
    source=eta*t; target=remainder(fixed_chart,np.array([0.]),retained['broad'],parent)[0]
    interval=population_interval(target,source)
    n=int(np.ceil(interval['lower']))
    overlap_target=remainder(fixed_chart,np.array([.75]),retained['broad'],parent)[0]
    left=eta*np.array(limits['broad_left_0.75']['tensor'])
    right=eta*np.array(limits['shared_right_0.75']['tensor'])
    after_left=overlap_target-n*left
    budget=dict(eta=eta,throat_target=target.tolist(),throat_one_field=source.tolist(),
        throat_population_interval=interval,throat_minimum_integer=n,
        throat_remainder=(target-n*source).tolist(),
        throat_dec_margins=dec_projections(target-n*source).tolist(),
        overlap_target=overlap_target.tolist(),overlap_left_one_field=left.tolist(),
        overlap_right_one_field=right.tolist(),overlap_after_left=after_left.tolist(),
        overlap_right_population_interval=population_interval(after_left,right),
        overlap_after_equal_populations=(after_left-n*right).tolist(),
        radial_populations='retained unchanged',
        excluded_from_bulk_completion=['interface self/material stress','exterior stress',
                                      'end traction and recoil closure','transition source beyond sampled overlap'])
    # The earlier normalization brackets each fix one global physical curvature
    # coupling. dT/d log(R_ref/a0)=-2H_native is a local covariant tensor;
    # the finite part is varied uniformly, with the second coupling held fixed.
    normalization_cases=[]
    h_throat=np.array(rows[0]['log_source'])
    h_overlap=np.array(center['log_source'])
    for logarithm in (.5,1.,2.,4.):
        st=source-2*eta*(logarithm-1)*h_throat
        sl=left-2*eta*(logarithm-1)*h_overlap
        sr=right-2*eta*(logarithm-1)*h_overlap
        allowed=population_interval(target,st)
        count=int(np.ceil(allowed['lower']))
        after=overlap_target-count*sl
        right_allowed=population_interval(after,sr)
        normalization_cases.append(dict(reference_log=logarithm,
            fixed_a0=summary['calibration']['reference_radius']*float(np.exp(-logarithm)),
            throat_one_field=st.tolist(),overlap_left_one_field=sl.tolist(),overlap_right_one_field=sr.tolist(),
            throat_population_interval=allowed,minimum_left_integer=count,
            throat_remainder=(target-count*st).tolist(),
            throat_dec_margins=dec_projections(target-count*st).tolist(),
            overlap_after_left=after.tolist(),overlap_dec_after_left=dec_projections(after).tolist(),
            overlap_right_population_interval=right_allowed,
            equal_population_overlap_dec=dec_projections(after-count*sr).tolist(),
            two_probe_bulk_feasible=bool(allowed['feasible'] and right_allowed['feasible'])))
    budget['fixed_global_normalization_cases']=normalization_cases
    controls=[]
    base=next(r for r in rows if r['source']=='broad_left' and r['coordinate']==0.
              and r['mass']==4. and r['cut']==32. and r['name']=='base')
    for row in rows:
        if row['name'] in ('shooting_control','frequency_control','metric_control','narrow_throat'):
            controls.append(dict(name=row['name'],tensor_change=(np.array(row['tensor'])-base['tensor']).tolist()))
    result=dict(verified_production_hashes=verified,independent_modes=independent,
        maximum_independent_relative_error=max(r['relative_error'] for r in independent),
        conservation=ward,limits=limits,budget=budget,controls=controls,
        regulator_controls=regulator_rows,geometry_controls=geometry_controls(spec))
    (args.data/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    script=Path(__file__).resolve();shutil.copy2(script,args.data/('execution_'+script.name))
    outputs=[args.data/'audit.json',args.data/('execution_'+script.name)]
    outputs.extend(p for p in args.data.iterdir() if p.name.startswith(('absolute_10','case_10','absolute_20','case_20')))
    parent_path=(args.data/'manifest.json').resolve()
    parent_name=str(parent_path.relative_to(ROOT)) if parent_path.is_relative_to(ROOT) else str(parent_path)
    manifest=dict(input_sha256={parent_name:digest(parent_path),
                                 str(script.relative_to(ROOT)):digest(script)},
                  output_sha256={p.name:digest(p) for p in outputs})
    (args.data/'audit_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(maximum_independent_relative_error=result['maximum_independent_relative_error'],
                          conservation=ward,limits=limits,budget=budget,controls=controls),indent=2))


if __name__=='__main__':
    main()
