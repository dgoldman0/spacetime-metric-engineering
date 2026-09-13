#!/usr/bin/env python3
"""Joint bank/fluid and guided-photon temperature coefficient selection.

Actual positive hot/cold branch heats select the inequalities. A common
gapless-channel coefficient a2 and fixed bank coefficients ah,ac obey
ah>Lf, ac<Uf, ah*a2**2>Lg, ac*a2**2<Ug. Source spectra, material packing,
momentum and complete entropy evolution remain separate construction duties.
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
from audit_virtual_cell_thermal_replay import geometry, linear_history
from run_poynting_delivery import BASE, ROOT, write_json

HEAT_ACTIVITY_TOLERANCE=1e-10
HEAT_VALIDATION_TOLERANCE=1e-10
POPULATION_TOLERANCE=1e-10


def finite(value):
    return float(value) if np.isfinite(value) else None


def joint_temperature_bounds(fluid_hot,fluid_cold,photon_hot,photon_cold,
                             fluid_temperature,hot_energy,cold_energy,counter,radius):
    """Strict positive-state tests use exact signs, including tiny populations."""
    fh,fc,ph,pc,T,H,C,c,R=np.broadcast_arrays(*[np.asarray(v,float) for v in
        (fluid_hot,fluid_cold,photon_hot,photon_cold,fluid_temperature,hot_energy,cold_energy,counter,radius)])
    if (fh.ndim!=2 or min(fh.shape)<1 or np.any(R<=0)
            or not all(np.isfinite(v).all() for v in (fh,fc,ph,pc,T,H,C,c,R))):
        raise ValueError('finite matching time-position histories and positive radius required')
    active=[v>HEAT_ACTIVITY_TOLERANCE for v in (fh,fc,ph,pc)]
    afh,afc,aph,apc=active
    negative=(fh < -HEAT_VALIDATION_TOLERANCE)|(fc < -HEAT_VALIDATION_TOLERANCE)
    negative|=(ph < -HEAT_VALIDATION_TOLERANCE)|(pc < -HEAT_VALIDATION_TOLERANCE)
    negative|=(H < -POPULATION_TOLERANCE)|(C < -POPULATION_TOLERANCE)
    negative|=(c < -POPULATION_TOLERANCE)|(T < -POPULATION_TOLERANCE)
    forbidden_hot=(afh|aph)&(H<=0)
    forbidden_fluid_cold=afc&(T<=0)
    forbidden_photon_cold=apc&(c<=0)
    with np.errstate(divide='ignore',over='ignore',under='ignore',invalid='ignore'):
        tf=T**4;cg=c**2*R**4
        lf=np.divide(tf,H,out=np.full_like(H,np.inf),where=H>0)
        uf=np.divide(tf,C,out=np.full_like(C,np.inf),where=C>0)
        lg=np.divide(cg,H,out=np.full_like(H,np.inf),where=H>0)
        ug=np.divide(cg,C,out=np.full_like(C,np.inf),where=C>0)
    tables=[np.where(afh,lf,-np.inf),np.where(afc,uf,np.inf),
            np.where(aph,lg,-np.inf),np.where(apc,ug,np.inf)]
    result=dict(fluid_hot_active=afh,fluid_cold_active=afc,photon_hot_active=aph,photon_cold_active=apc,
        negative_state_or_heat=negative,forbidden_hot_emission=forbidden_hot,
        forbidden_fluid_cold=forbidden_fluid_cold,forbidden_photon_cold=forbidden_photon_cold,
        fluid_hot_threshold=lf,fluid_cold_threshold=uf,
        photon_hot_threshold=lg,photon_cold_threshold=ug,
        state_valid=~np.any(negative|forbidden_hot|forbidden_fluid_cold|forbidden_photon_cold,axis=0))
    for key,table,mask,lower in zip(('Lf','Uf','Lg','Ug'),tables,active,(True,False,True,False)):
        result[key]=np.maximum(0.,table.max(axis=0)) if lower else table.min(axis=0)
        arg=np.argmax(table,axis=0) if lower else np.argmin(table,axis=0)
        result[key+'_witness']=np.where(mask.any(axis=0),arg,-1)
    return result


def choose_joint_coefficients(Lf,Uf,Lg,Ug):
    """Common positive coefficients with >=2 hot and <=1/2 cold safety.

    max(Lf/Uf,Lg/Ug) is the contrast infimum. A finite strict selection uses
    four times that ratio; unconstrained zero-infimum cases use contrast four.
    The cold/hot volume interpretation assumes equal bank photon caloric
    normalization. The selected coefficients themselves are dimensionless.
    """
    lower=np.array([Lf,Lg],float);upper=np.array([Uf,Ug],float)
    valid=bool(np.isfinite(lower).all() and np.all(lower>=0)
        and np.all(upper>0) and not np.isnan(upper).any())
    if not valid:return dict(selection_possible=False,contrast_infimum=None)
    with np.errstate(over='ignore',divide='ignore',invalid='ignore'):
        ratio=lower/upper
    infimum=float(ratio.max())
    contrast=4*infimum if infimum>0 else 4.
    if not np.isfinite(contrast) or contrast<=0:
        return dict(selection_possible=False,contrast_infimum=finite(infimum))
    # Each sector may choose its own overall normalization. Their common
    # contrast makes bh/bc=ah/ac and hence supplies a single a2.
    with np.errstate(over='ignore',divide='ignore',under='ignore',invalid='ignore'):
        ac=.5*Uf if np.isfinite(Uf) else 2*max(Lf,1.)/contrast
        ah=contrast*ac
        bc=.5*Ug if np.isfinite(Ug) else 2*max(Lg,1.)/contrast
        bh=contrast*bc
        a2=np.sqrt(bc/ac)
    coefficients=np.array([ah,ac,bh,bc,a2])
    possible=bool(np.isfinite(coefficients).all() and np.all(coefficients>0)
        and ah>Lf and ac<Uf and bh>Lg and bc<Ug)
    return dict(selection_possible=possible,contrast_infimum=infimum,
        fluid_contrast_infimum=float(ratio[0]),photon_contrast_infimum=float(ratio[1]),
        selected_hot_coefficient=finite(ah),selected_cold_coefficient=finite(ac),
        selected_channel_coefficient=finite(a2),selected_cold_to_hot_volume_ratio=finite(contrast),
        selected_hot_channel_product=finite(bh),selected_cold_channel_product=finite(bc),
        hot_safety_factor=2.,cold_safety_factor=.5,
        strict_contrast_infimum_attained=False)


def evaluate(spec):
    path,output=map(Path,spec);label=path.stem.removesuffix('_states')
    meta=json.loads(path.with_name(label+'_summary.json').read_text())
    if not meta.get('bank_counter_contact_reconstruction'):
        raise ValueError('accepted curved bank-contact replay arrays required')
    with np.load(path) as f:s={key:f[key] for key in f.files}
    t,x=s['t'],s['x'];tm=(t[:-1]+t[1:])/2
    if len(t)<2 or len(x)%2 or np.any(np.diff(t)<=0) or np.any(np.diff(x)<=0):
        raise ValueError('ordered times and equal paired spatial grids required')
    h=DenseHistory('routed_family',ROOT/meta['input']);g=geometry(h.h.reference.h.model,tm,x)
    midpoint=lambda name:linear_history(t,s[name],tm)[0]
    H,C,K,V=[midpoint(key) for key in ('receiver_hot_energy','receiver_cold_energy',
                                     'thermal_inventory','balanced_radiation_inventory')]
    incident=midpoint('absorption_rest')
    returned=midpoint('work_return_rest')+midpoint('heat_return_rest')
    counter=V/g['M']-incident-returned
    direction=np.r_[-np.ones(len(x)//2),np.ones(len(x)//2)]
    current=-direction*(incident-returned)
    number=s['fluid_particle_number']
    if number.shape!=(len(x),) or not np.isfinite(number).all() or np.any(number<=0):
        raise ValueError('positive archived fluid particle inventory required')
    registered=np.interp(x,h.h.reference.h.state['x'],h.h.reference.h.state['number'])
    number_error=float(abs(number-registered).max())
    if number_error>1e-10:raise ValueError('fluid normalization differs from registered material')
    Tf=K/(3*number*g['D']**(1/3))
    fh,fc,ph,pc=[s[key] for key in ('bank_fluid_hot_panel_heat','bank_fluid_cold_panel_heat',
                                  'bank_photon_hot_panel_heat','bank_photon_cold_panel_heat')]
    tau=s['receiver_contact_proper_duration']
    if tau.shape!=H.shape or not np.isfinite(tau).all() or np.any(tau<=0):
        raise ValueError('positive matching proper panel durations required')
    bounds=joint_temperature_bounds(fh,fc,ph,pc,Tf,H,C,counter,g['radius'])
    limits={key:float(bounds[key].max() if key.startswith('L') else bounds[key].min())
            for key in ('Lf','Uf','Lg','Ug')}
    selection=choose_joint_coefficients(**limits)
    identities=dict(hot_partition=float(abs(ph+fh-s['receiver_hot_contact_panel_heat']).max()),
        cold_partition=float(abs(pc+fc-s['receiver_cold_contact_panel_heat']).max()),
        counter_power=float(abs(ph-pc-s['bank_counter_panel_energy']).max()),
        total_bank_heat=float(abs(ph+fh-pc-fc-s['receiver_total_contact_panel_heat']).max()))
    direction_violation=max(0.,float((abs(current)-counter).max()))
    parent_ok=bool(meta.get('success') and meta.get('full_sampled_gate_passes'))
    state_ok=bool(bounds['state_valid'].all() and direction_violation<=POPULATION_TOLERANCE
                  and max(identities.values())<=1e-9)
    coefficient_arrays={};finite_contact=False;positive_gaps=False;grey_identity=None;full_grey_identity=None
    if selection['selection_possible'] and state_ok:
        ah,ac,a2=[selection[key] for key in ('selected_hot_coefficient','selected_cold_coefficient',
                                           'selected_channel_coefficient')]
        hot_fourth=ah*np.maximum(H,0.);cold_fourth=ac*np.maximum(C,0.)
        hot_eq=a2*np.sqrt(hot_fourth)/g['radius']**2
        cold_eq=a2*np.sqrt(cold_fourth)/g['radius']**2
        hot_gap=hot_eq-counter;cold_gap=counter-cold_eq
        fluid_hot_gap=hot_fourth-Tf**4;fluid_cold_gap=Tf**4-cold_fourth
        ahot,acold=bounds['photon_hot_active'],bounds['photon_cold_active']
        afhot,afcold=bounds['fluid_hot_active'],bounds['fluid_cold_active']
        positive_gaps=bool(np.all(hot_gap[ahot]>0) and np.all(cold_gap[acold]>0)
            and np.all(fluid_hot_gap[afhot]>0) and np.all(fluid_cold_gap[afcold]>0))
        with np.errstate(over='ignore',divide='ignore',invalid='ignore'):
            kh=np.divide(ph,g['D']*tau*hot_gap,out=np.zeros_like(ph),where=ahot&(hot_gap>0))
            kc=np.divide(pc,g['D']*tau*cold_gap,out=np.zeros_like(pc),where=acold&(cold_gap>0))
            kfh=np.divide(fh,tau*fluid_hot_gap,out=np.zeros_like(fh),where=afhot&(fluid_hot_gap>0))
            kfc=np.divide(fc,tau*fluid_cold_gap,out=np.zeros_like(fc),where=afcold&(fluid_cold_gap>0))
        finite_contact=bool(all(np.isfinite(a).all() and np.all(a>=0) for a in (kh,kc,kfh,kfc)))
        grey_identity=float(abs(g['D']*tau*(kh*hot_gap-kc*cold_gap)-
            (np.where(ahot,ph,0.)-np.where(acold,pc,0.))).max()) if finite_contact else None
        full_grey_identity=float(abs(g['D']*tau*(kh*hot_gap-kc*cold_gap)-(ph-pc)).max()) if finite_contact else None
        coefficient_arrays=dict(hot_temperature=hot_fourth**.25,cold_temperature=cold_fourth**.25,
            hot_equilibrium_counter_density=hot_eq,cold_equilibrium_counter_density=cold_eq,
            hot_photon_temperature_gap=hot_gap,cold_photon_temperature_gap=cold_gap,
            hot_fluid_temperature_fourth_gap=fluid_hot_gap,cold_fluid_temperature_fourth_gap=fluid_cold_gap,
            hot_photon_grey_coefficient=kh,cold_photon_grey_coefficient=kc,
            hot_fluid_heat_coefficient=kfh,cold_fluid_heat_coefficient=kfc)
    passed=bool(parent_ok and state_ok and selection['selection_possible'] and finite_contact
                and positive_gaps and full_grey_identity is not None and full_grey_identity<=1e-9)

    def witness(i,j,key=None):
        return dict(time=float(tm[i]),x=float(x[j]),fluid_temperature=float(Tf[i,j]),
            hot_energy=float(H[i,j]),cold_energy=float(C[i,j]),counter_density=float(counter[i,j]),
            counter_current=float(current[i,j]),radius=float(g['radius'][i,j]),
            fluid_hot_heat=float(fh[i,j]),fluid_cold_heat=float(fc[i,j]),
            photon_hot_heat=float(ph[i,j]),photon_cold_heat=float(pc[i,j]),
            threshold=finite(bounds[{'Lf':'fluid_hot_threshold','Uf':'fluid_cold_threshold',
                'Lg':'photon_hot_threshold','Ug':'photon_cold_threshold'}[key]][i,j]) if key else None)

    limit_witness={}
    for key in limits:
        j=int(np.argmax(bounds[key]) if key.startswith('L') else np.argmin(bounds[key]))
        i=int(bounds[key+'_witness'][j]);limit_witness[key]=witness(i,j,key) if i>=0 else None
    invalid=np.argwhere(bounds['negative_state_or_heat']|bounds['forbidden_hot_emission']|
                        bounds['forbidden_fluid_cold']|bounds['forbidden_photon_cold'])
    summary=dict(label=label,input=str(path.relative_to(ROOT)),parent_full_sampled_gate_passes=parent_ok,
        independent_state_and_contact_checks_pass=state_ok,
        joint_bank_temperature_selection_passes=passed,
        time_samples=len(tm),spatial_samples=len(x),limits={key:finite(value) for key,value in limits.items()},
        fluid_cold_upper_unbounded=not np.isfinite(limits['Uf']),
        photon_cold_upper_unbounded=not np.isfinite(limits['Ug']),**selection,
        positive_active_temperature_gaps=positive_gaps,finite_grey_contact_coefficients=finite_contact,
        contact_partition_residuals=identities,active_grey_counter_power_identity_residual=grey_identity,
        full_grey_counter_power_identity_residual=full_grey_identity,
        fluid_particle_normalization_error=number_error,maximum_directional_population_violation=direction_violation,
        active_fluid_hot_samples=int(bounds['fluid_hot_active'].sum()),
        active_fluid_cold_samples=int(bounds['fluid_cold_active'].sum()),
        active_photon_hot_samples=int(bounds['photon_hot_active'].sum()),
        active_photon_cold_samples=int(bounds['photon_cold_active'].sum()),
        invalid_state_or_donor_samples=len(invalid),first_invalid_witness=witness(*invalid[0]) if len(invalid) else None,
        limit_witnesses=limit_witness,
        heat_activity_tolerance=HEAT_ACTIVITY_TOLERANCE,heat_validation_tolerance=HEAT_VALIDATION_TOLERANCE,
        population_tolerance=POPULATION_TOLERANCE,
        inactive_heat_maximum=float(max(np.max(abs(a[~bounds[key]]),initial=0.) for a,key in
            ((fh,'fluid_hot_active'),(fc,'fluid_cold_active'),(ph,'photon_hot_active'),(pc,'photon_cold_active')))),
        bank_negative_roundoff_mapped_to_zero_for_temperature=bool(np.any(H<0) or np.any(C<0)),
        equilibrium_law='c_eq=a2*Theta**2/R**2 for fixed bidirectional gapless photon channels',
        bank_caloric_law='Theta_hot**4=ah*H, Theta_cold**4=ac*C',
        fluid_caloric_law='Theta_fluid=K/(3*N_mass*D**(1/3))',
        volume_contrast_interpretation='ah/ac equals cold/hot proper volume only for equal bank caloric normalization',
        midpoint_scope='exact registered midpoint geometry and stored particle normalization; linear interpolation of replay H,C,K,V and explicit beam densities; actual integrated branch heat divided by midpoint D and proper panel duration',
        temporal_grey_coefficients_selected=bool(selection['selection_possible'] and state_ok
                                               and finite_contact and positive_gaps),
        local_dynamical_opacity_law_supplied=False,
        spectrum_or_mode_selectivity_supplied=False,force_closure_supplied=False,
        complete_entropy_evolution_supplied=False,material_packing_supplied=False,
        full_source_construction_supplied=False,inventories_and_heat_branches_modified=False)
    if coefficient_arrays:
        summary['maximum_coefficients']={key:finite(float(coefficient_arrays[key].max())) for key in
            ('hot_photon_grey_coefficient','cold_photon_grey_coefficient',
             'hot_fluid_heat_coefficient','cold_fluid_heat_coefficient')}
    arrays=dict(t=t,midpoint_time=tm,x=x,D=g['D'],radius=g['radius'],proper_duration=tau,
        hot_energy=H,cold_energy=C,thermal_inventory=K,balanced_radiation_inventory=V,
        explicit_incident_density=incident,explicit_return_density=returned,
        counter_density=counter,counter_current=current,fluid_temperature=Tf,fluid_particle_number=number,
        fluid_hot_panel_heat=fh,fluid_cold_panel_heat=fc,photon_hot_panel_heat=ph,photon_cold_panel_heat=pc,
        **bounds,**coefficient_arrays)
    np.savez_compressed(output/(label+'_temperature.npz'),**arrays)
    write_json(output/(label+'_summary.json'),summary)
    print(label+': '+json.dumps({key:summary.get(key) for key in
        ('joint_bank_temperature_selection_passes','contrast_infimum','selected_cold_to_hot_volume_ratio')}),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True);parser.add_argument('--output-name',required=True)
    parser.add_argument('--labels',nargs='+');parser.add_argument('--workers',type=int,default=2)
    args=parser.parse_args()
    if not 1<=args.workers<=2:parser.error('one or two workers required')
    source,output=BASE/args.source,BASE/args.output_name
    if output.exists():raise RuntimeError('preserve completed joint bank-temperature audit')
    labels=args.labels or [p.stem.removesuffix('_states') for p in sorted(source.glob('*_states.npz'))]
    if not labels:raise ValueError('completed curved bank replay states required')
    hashes,historical=validate_controls(source,labels)
    runtime=[Path(__file__),ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_bank_temperature.py']
    for module in list(sys.modules.values()):
        filename=getattr(module,'__file__',None)
        if filename:
            path=Path(filename).resolve()
            if path.suffix=='.py' and path.is_relative_to(ROOT):runtime.append(path)
    hashes.update({str(path.relative_to(ROOT)):sha256_file(path) for path in runtime})
    output.mkdir()
    with ProcessPoolExecutor(max_workers=min(args.workers,len(labels)),
            mp_context=multiprocessing.get_context('spawn')) as pool:
        cases=list(pool.map(evaluate,[(source/(label+'_states.npz'),output) for label in labels]))
    for relative,expected in hashes.items():
        if sha256_file(ROOT/relative)!=expected:raise RuntimeError('input changed during temperature audit: '+relative)
    write_json(output/'summary.json',dict(cases=cases))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        workers=min(args.workers,len(labels)),input_sha256=hashes,historical_source=historical,
        output_sha256={p.name:sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__=='__main__':main()
