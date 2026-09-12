#!/usr/bin/env python3
"""Count separate radial and angular members with freely scheduled response.

The prepared elastic law is relaxed, while its component energy inequalities
remain enforced. The optional axial monotonicity constraint screens uncoupled
members with positive incremental stiffness along the prescribed deformation.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
import json
import multiprocessing
import subprocess
import time

import numpy as np

from adm_harness.composite_capacitor import anisotropic_moments
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.joint_support_envelope import build_envelope
from adm_harness.pressure_linked_storage import retained_coefficient_program
from adm_harness.source_ledger import sha256_file
from run_joint_backing_link import JointHistory
from run_poynting_delivery import BASE,ROOT,write_json

OUTPUT=BASE/'joint_component_cone'


def evaluate(spec):
    separate,monotone=spec;h=JointHistory(32,8);nt,nx=len(h.t),len(h.x)
    label=('separate_members' if separate else 'general_DEC')+('_monotone' if monotone else '_scheduled')
    p=build_envelope(h.t,h.x,h.c,h.log_radius_t,h.thermal,h.number,h.force_rhs,h.radial_field,
                     stress_fraction=1.,ends='exposed',freeze_fluid=True)
    size=p['size'];ell=h.c['gamma']*h.c['b'];eq,ub=p['eq'],p['ub']
    if separate:
        # Radial members cost |P|; angular skins cost -Q in tension,
        # and circumferential compressed rods cost 2Q in compression.
        for k in range(size):
            for radial in (-1.,1.):
                for angular in (-1.,2.):
                    ub.add([(2*size+k,radial),(3*size+k,angular),(size+k,-1.)])
    if monotone:
        for i in range(1,nt):
            for j in range(nx):
                sign=float(np.sign(ell[i,j]-ell[i-1,j]))
                if abs(np.log(ell[i,j]/ell[i-1,j]))>1e-8:
                    ub.add([(2*size+i*nx+j,sign/ell[i,j]),
                            (2*size+(i-1)*nx+j,-sign/ell[i-1,j])])
    matrix=eq.matrix();trace=[];start=time.monotonic();last=None
    for iteration in range(6):
        remaining=120.-(time.monotonic()-start)
        if remaining<=0:
            break
        r=retained_coefficient_program(p['cost'],method='highs-ipm',deadline=min(40.,remaining),
            A_eq=matrix,b_eq=eq.rhs,A_ub=ub.matrix(),b_ub=ub.rhs,bounds=p['bounds'])
        if r.success and (np.max(ub.matrix()@r.x-ub.rhs)>2e-7 or np.max(abs(matrix@r.x-eq.rhs))>2e-7):
            # Independently verify presolve/postsolve before accepting a
            # nearly degenerate axial monotonicity constraint.
            r=retained_coefficient_program(p['cost'],method='highs-ds',presolve=False,
                deadline=min(40.,max(1.,120.-(time.monotonic()-start))),
                A_eq=matrix,b_eq=eq.rhs,A_ub=ub.matrix(),b_ub=ub.rhs,bounds=p['bounds'])
        if not r.success:
            if last is None:
                summary=dict(label=label,success=False,status=int(r.status),message=r.message,
                    separate_members=separate,monotone_axial_response=monotone)
                write_json(OUTPUT/(label+'_summary.json'),summary)
                print(label+': '+r.message,flush=True);return summary
            break
        u,m,pr,pt=r.x[:-1].reshape(4,nt,nx);vol=h.c['rest_volume']
        tensor=anisotropic_moments((h.number[None,:]+u+m)/vol,(u/3+pr)/vol,(u/3+pt)/vol,h.c['v'])
        value,z=maximum_null(tensor);upper=float(value.max());lower=float(r.x[-1])
        trace.append(dict(lower=lower,upper=upper))
        last=(r,u,m,pr,pt,tensor,upper,lower)
        bad=np.argwhere(value>lower+5e-5)
        if not len(bad):
            break
        for i,j in bad:
            p['null_row'](int(i),int(j),float(z[i,j]))
    r,u,m,pr,pt,tensor,upper,lower=last
    # Raising only the epigraph peak to its exact angular maximum provides
    # a feasible upper bound, even when a tighter angular optimum is pending.
    checked=r.x.copy();checked[-1]=upper
    eqres=matrix@checked-eq.rhs;ubres=ub.matrix()@checked-ub.rhs
    integrate=lambda a:4*np.pi*np.trapezoid(a,h.x,axis=-1)
    phases=[]
    for i,t,demand in h.phases:
        val,direction=maximum_null(tensor[:,i]+h.fixed[:,i]-demand)
        phases.append(dict(time=t,required_negative_null=float(val.max())))
    summary=dict(label=label,success=True,separate_members=separate,monotone_axial_response=monotone,
        material_peak_lower=lower,material_peak_upper=upper,angular_trace=trace,
        max_raw_equality_residual=float(np.max(abs(eqres)*eq.scales)),
        max_inequality_violation=float(max(0.,ubres.max())),phases=phases,
        initial_support_rest=float(integrate(m[0])),final_support_rest=float(integrate(m[-1])),
        elapsed_seconds=time.monotonic()-start,constitutive_law_supplied=False)
    if summary['max_inequality_violation']>2e-7 or summary['max_raw_equality_residual']>2e-7:
        summary.update(success=False,status=-3,message='independent original-matrix verification failed')
    write_json(OUTPUT/(label+'_summary.json'),summary)
    np.savez_compressed(OUTPUT/(label+'_states.npz'),t=h.t,x=h.x,thermal=u,support_energy=m,
        radial_volume=pr,angular_volume=pt)
    print(label+': peak bracket '+str((lower,upper)),flush=True)
    return summary


def main():
    if OUTPUT.exists():
        raise RuntimeError('preserve completed component-cone evidence')
    preceding=BASE/'joint_support_envelope/manifest.json'
    hashes=json.loads(preceding.read_text())['input_sha256']
    for path in (Path(__file__),preceding):
        hashes[str(path.relative_to(ROOT))]=sha256_file(path)
    for path,expected in hashes.items():
        if sha256_file(ROOT/path)!=expected:
            raise RuntimeError('changed component cone input: '+path)
    OUTPUT.mkdir(parents=True)
    with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,[(True,False),(False,True),(True,True)]))
    write_json(OUTPUT/'summary.json',dict(cases=results))
    write_json(OUTPUT/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),input_sha256=hashes,
        output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__=='__main__':
    main()
