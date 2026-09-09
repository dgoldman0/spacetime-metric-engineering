#!/usr/bin/env python3
"""Numerical checks of the registered families' initial boundary asymptotics.

This audits the existing construction and renders its retained results.
It introduces no new source family or optimization controls. The argument
and its scope are written manually in LE_RESET_INVERSE_SEARCH.md.
"""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline

from run_le_geometry_boundary import ROOT
from adm_harness.reset_inverse_search import construct,infrastructure_boost,polar_areal_channels,reference_grid
from adm_harness.source_ledger import sha256_file


def onset_records(reference_path):
    frame=pd.read_csv(reference_path)
    frame=frame[frame.holding & frame.level.eq(2)]
    phases=np.sort(frame.s.unique())
    outer=6.25
    logfs=[]
    for s in phases:
        g=frame[frame.s.eq(s)].sort_values('areal_radius')
        r=g.areal_radius.to_numpy()
        logfs.append(float(CubicSpline(r,np.log(1-2*g.reference_static_mass.to_numpy()/r))(outer)))
    u=np.unique(np.r_[0.,2.**(-np.arange(3,13)),np.linspace(.15,1.,65)])
    records=[]
    for kind,n in [('direct',3),('waypoints',9)]:
        g=reference_grid(reference_path,129,path_kind=kind,u_values=u)
        f,fr=g.f[:,-1],g.f_r[:,-1]
        nu,nur,nurr=g.nu[:,-1],g.nu_r[:,-1],g.nu_rr[:,-1]
        eb,pb,ptb=g.energy[:,-1],g.pressure[:,-1],g.transverse[:,-1]
        if kind=='direct':
            a_log=10*(logfs[-1]-logfs[0])
        else:
            first_phase_coefficient=40*(phases[-1]-phases[0])/np.expm1(4.)
            a_log=10*(logfs[1]-logfs[0])*(first_phase_coefficient/(phases[1]-phases[0]))**3
        if a_log<=0 or eb[0]+pb[0]==0:
            raise ArithmeticError('the measured boundary coefficients do not satisfy the stated onset case')
        for duration,skew in [(4.,-.65),(14.255,.65)]:
            tu=duration*(1+skew*(1-2*u));tuu=-2*duration*skew
            ft=-2*g.mass_u[:,-1]/(outer*tu)
            ftt=-2*(g.mass_uu[:,-1]/tu**2-g.mass_u[:,-1]*tuu/tu**3)/outer
            geometric=polar_areal_channels(outer,f,fr,ft,ftt,nu,nur,nurr,g.nu_u[:,-1]/tu)
            leading=n*(n-1)*a_log/(16*np.pi*np.exp(2*nu[0])*(duration*(1+skew))**2)
            j_leading=n*np.sqrt(f[0])*a_log/(8*np.pi*outer*np.exp(nu[0])*duration*(1+skew))
            for moving in [False,True]:
                kinetic,jb,_=infrastructure_boost(eb+pb,geometric[:,2],moving)
                material=-kinetic-abs(geometric[:,2]-jb)
                residual=geometric[:,3]-(ptb+.25*material)
                material_order=2*n-2 if moving else n-1
                material_leading=-j_leading*j_leading/(eb[0]+pb[0]) if moving else -abs(j_leading)
                for i in np.flatnonzero((u>0)&(u<=.125)):
                    records.append({'path_kind':kind,'moving':moving,'duration':duration,'time_skew':skew,
                        'u':float(u[i]),'radius':outer,'mass_onset_order':n,
                        'predicted_angular_coefficient':float(leading),'angular_residual':float(residual[i]),
                        'scaled_angular_residual':float(residual[i]/u[i]**(n-2)),
                        'angular_coefficient_ratio':float(residual[i]/u[i]**(n-2)/leading),
                        'material_density':float(material[i]),'material_onset_order':material_order,
                        'predicted_material_coefficient':float(material_leading),
                        'scaled_material_density':float(material[i]/u[i]**material_order),
                        'predicted_current_coefficient':float(j_leading),
                        'current':float(geometric[i,2]),'initial_boundary_enthalpy':float(eb[0]+pb[0]),
                        'roundoff_floor':float(512*np.finfo(float).eps*max(abs(geometric[i,3]),abs(ptb[i]))),
                        'log_f_onset_coefficient':float(a_log)})
    return pd.DataFrame(records)


def readable_figure(output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    exploration=pd.read_csv(output/'exploration.csv')
    local=pd.read_csv(output/'local_solves.csv',float_precision='round_trip')
    all_rows=pd.concat([exploration,local],ignore_index=True)
    valid=all_rows[all_rows.status.eq('evaluated')]
    result=json.loads((output/'manifest.json').read_text())
    chosen=result['finalists'][0]
    fields=np.load(output/f'candidate_{chosen}_level_2.npz')
    fig,axes=plt.subplots(1,3,figsize=(13,4),constrained_layout=True)
    for kind in ['direct','waypoints']:
        for moving in [False,True]:
            mask=valid.path_kind.eq(kind)&valid.moving.eq(moving)
            g=valid[mask]
            deficit=np.maximum(-g.min_material_density,0.)
            axes[0].scatter(deficit,g.max_angular_residual,s=12,alpha=.65,
                            label=f"{kind}, {'moving' if moving else 'stationary'}")
    shown=(valid.min_material_density.between(-.1,-1e-7)&valid.max_angular_residual.between(1e-5,100))
    axes[0].set(xscale='log',yscale='log',xlim=(1e-7,.1),ylim=(1e-5,100),
                xlabel='ordinary material energy deficit',ylabel='angular Einstein mismatch',
                title=f'Candidate comparison ({len(valid)-int(shown.sum())} outside view)')
    axes[0].legend(fontsize=7);axes[0].grid(alpha=.2)
    for ax,key,title in [(axes[1],'material_density','Negative material density'),
                         (axes[2],'radial_margin','Type IV margin deficit')]:
        deficit=np.maximum(-fields[key],0.)
        mesh=ax.pcolormesh(fields['radius'],fields['time'],deficit,shading='auto',cmap='magma_r')
        ax.set(xlabel='areal radius',ylabel='reset time',title=title)
        fig.colorbar(mesh,ax=ax)
    fig.savefig(output/'inverse_search_analysis.png',dpi=170)
    plt.close(fig)


def verify_saved_artifacts(output):
    """Check retained arrays and numerical ledgers without repeating the search."""
    from scipy.optimize import linear_sum_assignment
    manifest=json.loads((output/'manifest.json').read_text())
    kernel=ROOT/'toolkit/adm_harness_cli/adm_harness/source_ledger.py'
    reference=ROOT/'supporting_reports/data/le_coupled_reset_source/reference_tensors.csv.gz'
    assert sha256_file(kernel)==manifest['source_kernel_sha256']
    assert sha256_file(reference)==manifest['reference_sha256']
    rows=pd.read_csv(output/'independent_curvature_probes.csv.gz',float_precision='round_trip')
    eigen=np.load(output/'independent_curvature_probes_eigensystems.npz')
    assert len(rows)==manifest['independent_curvature_probes']
    assert rows.full_eigensystem_certified.all()
    assert np.array_equal(eigen['row_index'],np.arange(len(rows)))
    assert np.array_equal(eigen['s'],rows.s.to_numpy())
    assert np.array_equal(eigen['l'],rows.l.to_numpy())
    mixed=eigen['tensor_orthonormal']*np.array([-1.,1.,1.,1.])[None,:,None]
    vectors=eigen['eigenvectors'];values=eigen['eigenvalues']
    residual=mixed@vectors-vectors*values[:,None,:]
    relative=np.linalg.norm(residual,axis=(1,2))/(np.linalg.norm(mixed,axis=(1,2))*
                np.linalg.norm(vectors,axis=(1,2)))
    raw_mixed=eigen['raw_tensor_orthonormal']*np.array([-1.,1.,1.,1.])[None,:,None]
    raw_values=np.linalg.eigvals(raw_mixed)
    raw_error=0.
    for actual,stored in zip(raw_values,eigen['raw_eigenvalues']):
        cost=abs(actual[:,None]-stored[None,:])
        ix,jx=linear_sum_assignment(cost)
        raw_error=max(raw_error,float(cost[ix,jx].max()))
    raw_complex=(abs(raw_values.imag).max(axis=1)>1e-12*abs(raw_mixed).max(axis=(1,2)))
    expected=rows.stress_algebraic_type.eq('type_iv_flux_dominant').to_numpy()
    assert np.array_equal(raw_complex,expected)
    assert relative.max()<1e-12 and raw_error<1e-12
    summaries=pd.read_csv(output/'refinement_summary.csv',float_precision='round_trip')
    checks=[]
    for row in summaries.itertuples():
        with np.load(output/f'candidate_{row.candidate}_level_{row.level}.npz') as f:
            source,geometric,components=f['source'],f['geometric'],f['components']
            component_error=float(abs(components.sum(axis=0)-source).max())
            equation_error=float(abs(geometric[...,:3]-source[...,:3]).max())
            angular=float(abs(geometric[...,3]-source[...,3])[1:-1,2:-2].max())
            material=float(f['material_density'].min())
            margin=float((abs(source[...,0]+source[...,1])-2*abs(source[...,2])).min())
            luminosity=4*np.pi*f['radius']**2*f['alpha']*np.sqrt(f['f'])*source[...,2]
            luminosity_error=float(abs(luminosity+f['mass_t']).max())
            transfer_error=float(abs(np.trapezoid(luminosity,f['time'],axis=0)-
                (f['mass'][0]-f['mass'][-1])).max())
            mass=reference_grid(reference,len(f['radius']),len(f['u']),path_kind=row.path_kind).mass
            endpoint_error=float(abs(f['mass'][[0,-1]]-mass[[0,-1]]).max())
            boundary_error=float(abs(f['mass'][:,[0,-1]]-mass[:,[0,-1]]).max())
            table_error=max(abs(angular-row.max_angular_residual),abs(material-row.min_material_density),
                            abs(margin-row.min_radial_margin))
            null_min=float(components[2:,...,0].min())
            assert np.isfinite(source).all() and np.isfinite(geometric).all()
            assert f['f'].min()>0 and f['alpha'].min()>0
            assert max(component_error,equation_error,luminosity_error,table_error)<1e-12
            assert max(endpoint_error,boundary_error)<1e-12 and null_min>=-1e-14
            assert np.max(abs(f['background_speed']))<=.5+1e-12
            checks.append({'candidate':row.candidate,'level':row.level,
                'component_sum_max_error':component_error,'energy_radial_current_max_error':equation_error,
                'luminosity_identity_max_error':luminosity_error,'net_transfer_quadrature_error':transfer_error,
                'endpoint_mass_error':endpoint_error,'boundary_mass_error':boundary_error,
                'summary_extrema_max_error':table_error,'min_null_density':null_min,
                'min_material_density':material,'min_radial_margin':margin,'max_angular_residual':angular})
    result={'verified_utc':datetime.now(timezone.utc).isoformat(),
        'source_kernel_sha256':sha256_file(kernel),'reference_sha256':sha256_file(reference),
        'curvature_eigensystems':len(rows),'raw_complex_pairs':int(raw_complex.sum()),
        'max_eigen_equation_relative_error':float(relative.max()),'raw_eigenvalue_max_error':raw_error,
        'row_alignment_exact':True,'refinements':checks,
        'artifact_sha256':{p.name:sha256_file(p) for p in sorted(output.iterdir())
                           if p.is_file() and p.name!='artifact_verification.json'}}
    (output/'artifact_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'supporting_reports/data/le_reset_inverse_search')
    output=parser.parse_args().output
    reference=ROOT/'supporting_reports/data/le_coupled_reset_source/reference_tensors.csv.gz'
    records=onset_records(reference)
    records.to_csv(output/'onset_boundary_audit.csv',index=False)
    # Extending the grid API for the audit must preserve the stored search.
    original=pd.read_csv(output/'refinement_summary.csv').iloc[0]
    local=pd.read_csv(output/'local_solves.csv',float_precision='round_trip')
    best=local[local.candidate.eq(original.candidate)].iloc[0]
    from adm_harness.reset_inverse_search import NAMES
    grid=reference_grid(reference,129,65,path_kind=best.path_kind)
    regenerated=construct(grid,[best[name] for name in NAMES],moving=bool(best.moving),retain=True)
    stored=np.load(output/f'candidate_{int(best.candidate)}_level_0.npz')
    identity=max(float(abs(regenerated['fields'][name]-stored[name]).max()) for name in ['source','geometric','mass','alpha'])
    if identity>1e-12:
        raise ArithmeticError('default construction changed during the diagnostic extension')
    readable_figure(output)
    resolved=records[abs(records.angular_residual)>records.roundoff_floor]
    checked=resolved.sort_values('u').groupby(['path_kind','moving','duration','time_skew'],as_index=False).first()
    if np.max(abs(checked.angular_coefficient_ratio-1))>.15:
        raise ArithmeticError('numerical onset coefficient did not approach the predicted value')
    metadata={'completed_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'audit of the registered source families; no additional construction or parameter search',
        'rows':len(records),'max_default_reproduction_error':identity,
        'max_checked_onset_coefficient_relative_error':float(abs(checked.angular_coefficient_ratio-1).max()),
        'software_sha256':{str(p.relative_to(ROOT)):sha256_file(p) for p in [Path(__file__).resolve(),
            ROOT/'toolkit/adm_harness_cli/adm_harness/reset_inverse_search.py']}}
    (output/'onset_audit_manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
    verification=verify_saved_artifacts(output)
    print(checked[['path_kind','moving','duration','time_skew','u','predicted_angular_coefficient',
                   'angular_coefficient_ratio','material_density']].to_string(index=False))
    print(json.dumps(metadata,indent=2))
    print(f"Verified {verification['curvature_eigensystems']} eigensystems, "
          f"{verification['raw_complex_pairs']} raw complex pairs, and {len(verification['refinements'])} field files")


if __name__=='__main__':
    main()
