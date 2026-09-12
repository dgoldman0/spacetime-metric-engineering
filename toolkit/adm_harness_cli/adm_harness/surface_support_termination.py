"""Energy and normal-force gate for material termination jackets.

Y=R^2 sigma and Z=R^2 tau are surface energy and angular stress per steradian.
The continuing magnetic guide has the same traction on each side. The jacket
terminates the pressure fluid, electric store, and added material support.
"""
from __future__ import annotations

import numpy as np


def minimum_surface_inventory(t,radius,acceleration,angular_gradient,pressure_jump,
                              *,outward_sign=1.,stress_fraction=1.):
    t,r,a,k,jump=map(np.asarray,(t,radius,acceleration,angular_gradient,pressure_jump))
    if (len(t)<3 or np.any(np.diff(t)<=0) or np.any(r<=0) or
            np.any(abs(k)<1e-12) or outward_sign not in (-1.,1.) or not 0<stress_fraction<=1):
        raise ValueError('resolved timelike surface with finite angular curvature required')
    load=outward_sign*r*r*jump
    lower_force=a-2*stress_fraction*abs(k)
    upper_force=a+2*stress_fraction*abs(k)
    opposite=((load<0)&(lower_force>0))|((load>0)&(upper_force<0))
    # This sign witness uses the entire allowed stress cone and is independent
    # of the integration scheme and the prepared surface energy.
    witness=np.flatnonzero(opposite)
    base=dict(pointwise_force_cone_incompatible=bool(len(witness)),
              incompatible_sample_fraction=float(np.mean(opposite)))
    if len(witness):
        i=int(witness[np.argmax(abs(load[witness]))])
        return dict(success=False,reason='surface force has the opposite sign to every positive-energy admissible jacket',
                    witness_time=float(t[i]),witness_load=float(load[i]),
                    witness_acceleration=float(a[i]),witness_angular_gradient=float(k[i]),
                    witness_force_interval_per_unit_energy=[float(lower_force[i]),float(upper_force[i])],**base)
    # Y'=-2Z (ln R)', Z=(aY-load)/(2k). Integrate the linear scalar equation
    # with centered endpoint work, retaining the affine dependence on Y(0).
    ca=a/(2*k);cb=-load/(2*k)
    A=np.ones(len(t));B=np.zeros(len(t))
    for i,dr in enumerate(np.diff(np.log(r)),1):
        denominator=1+dr*ca[i]
        if abs(denominator)<1e-8:
            return dict(success=False,reason='surface integration requires finer temporal resolution',**base)
        factor=(1-dr*ca[i-1])/denominator
        A[i]=factor*A[i-1]
        B[i]=(B[i-1]*(1-dr*ca[i-1])-dr*(cb[i]+cb[i-1]))/denominator
    C=ca*A;D=ca*B+cb
    lower=0.;upper=np.inf
    for slope,offset in ((A,B),(stress_fraction*A-C,stress_fraction*B-D),
                         (stress_fraction*A+C,stress_fraction*B+D)):
        positive=slope>1e-12;negative=slope<-1e-12;zero=~(positive|negative)
        if np.any(zero&(offset<-1e-10)):
            return dict(success=False,reason='surface energy history and stress cone conflict',**base)
        if np.any(positive):lower=max(lower,float(np.max(-offset[positive]/slope[positive])))
        if np.any(negative):upper=min(upper,float(np.min(-offset[negative]/slope[negative])))
    if lower>upper+1e-9:
        return dict(success=False,reason='prepared surface inventory has an empty admissible interval',
                    initial_energy_lower=lower,initial_energy_upper=upper,**base)
    Y=A*lower+B;Z=C*lower+D
    force=a*Y-2*k*Z-load
    work=np.diff(Y)+(Z[1:]+Z[:-1])*np.diff(np.log(r))
    violation=np.maximum(abs(Z)-stress_fraction*Y,0)
    return dict(success=True,initial_energy_per_steradian=lower,
                initial_energy_upper=upper if np.isfinite(upper) else None,
                surface_energy=Y,surface_angular_stress=Z,
                max_force_residual=float(abs(force).max()),max_work_residual=float(abs(work).max()),
                max_stress_cone_violation=float(violation.max()),**base)
