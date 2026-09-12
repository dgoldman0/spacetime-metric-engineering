"""Joint support inverse with consistent spacetime quadrature.

M, P, Q are bilinear rest energy and radial/angular stress-volume fields.
The full fixed-component divergence supplies energy and momentum demand.
Separate-member energy inequalities hold throughout each bilinear panel.
"""
from __future__ import annotations

import time
import numpy as np
from numpy.polynomial.legendre import leggauss

from .composite_capacitor import anisotropic_moments
from .graded_electrothermal import SparseRows, maximum_null
from .pressure_linked_storage import retained_coefficient_program


def build_spacetime(t, x, coefficients, number, thermal, *, fraction=1., subpanels=1,
                    stress_rate=None, peak_cap=None):
    nt, nx = len(t), len(x); size = nt*nx; peak = 3*size
    eq, ub = SparseRows(peak+1), SparseRows(peak+1)
    z, w = leggauss(4); theta, weights = (z+1)/2, w/2
    te = (t[:-1,None]+np.diff(t)[:,None]*theta).ravel()
    ce = coefficients(te, x)
    shape = (nt-1, 4, nx)
    measure = np.diff(t)[:,None,None]*weights[None,:,None]
    work = []
    for a in (ce['log_ell_t'], 2*ce['log_radius_t']):
        work.append([np.sum(measure*a.reshape(shape)*b[None,:,None], axis=1)
                     for b in (1-theta, theta)])
    energy_rhs = np.sum(measure*(-ce['lapse']*ce['D']*ce['fixed_power']).reshape(shape), axis=1)
    for i in range(nt-1):
        for j in range(nx):
            old = i*nx+j; new = old+nx
            eq.add([(new,1.),(old,-1.),
                    (size+old,work[0][0][i,j]),(size+new,work[0][1][i,j]),
                    (2*size+old,work[1][0][i,j]),(2*size+new,work[1][1][i,j])], energy_rhs[i,j])

    tf = np.r_[t[0], (t[:-1]+t[1:])/2]
    fractions = ((np.arange(subpanels)[:,None]+theta)/subpanels).ravel()
    wx = np.tile(weights/subpanels, subpanels)
    xq = (x[:-1,None]+np.diff(x)[:,None]*fractions).ravel()
    cf, cb = coefficients(tf, xq), coefficients(tf, x)
    fshape = (nt, nx-1, len(fractions))
    measure = np.diff(x)[None,:,None]*wx[None,None,:]
    integrate = lambda a: np.sum(a.reshape(fshape)*measure, axis=2)
    parts = dict(M=cf['ell']*cf['acceleration']/cf['D'],
                 P=(cf['ell']*(cf['acceleration']+2*cf['angular_gradient'])-
                    cf['ell']*cf['v']/cf['lapse']*cf['volume_rate'])/cf['D'],
                 Pt=cf['ell']*cf['v']/(cf['lapse']*cf['D']),
                 Q=-2*cf['ell']*cf['angular_gradient']/cf['D'])
    bodies = [{key:integrate(a*np.tile(side,nx-1)[None,:]) for key,a in parts.items()}
              for side in (1-fractions, fractions)]
    rhs = integrate(-cf['ell']*cf['fixed_force'])
    for i in range(nt):
        lo, hi = (0,1) if i == 0 else (i-1,i)
        value = ((0,1.),) if i == 0 else ((lo,.5),(hi,.5))
        dt = t[hi]-t[lo]
        for j in range(nx-1):
            items = []
            for side, jj, sign in ((0,j,-1.),(1,j+1,1.)):
                b = bodies[side]
                for ii, weight in value:
                    k = ii*nx+jj
                    items.extend([(k,weight*b['M'][i,j]),
                                  (size+k,weight*(sign/cb['D'][i,jj]+b['P'][i,j])),
                                  (2*size+k,weight*b['Q'][i,j])])
                items.extend([(size+hi*nx+jj,b['Pt'][i,j]/dt),
                              (size+lo*nx+jj,-b['Pt'][i,j]/dt)])
            eq.add(items,rhs[i,j])
    for k in range(size):
        for radial in (-1.,1.):
            for angular in (-1.,2.):
                ub.add([(size+k,radial),(2*size+k,angular),(k,-fraction)])
    c = coefficients(t,x)
    if stress_rate is not None:
        for i in range(nt-1):
            for j in range(nx):
                old, new = i*nx+j, (i+1)*nx+j
                proper_dt = (t[i+1]-t[i])*(c['lapse'][i,j]+c['lapse'][i+1,j])/2
                for component in (1,2):
                    for sign in (-1.,1.):
                        ub.add([(component*size+new,sign),(component*size+old,-sign),
                                (new,-stress_rate*proper_dt/2),(old,-stress_rate*proper_dt/2)])

    def add_null(i,j,z):
        k = i*nx+j; v = c['v'][i,j]; gr = c['gamma'][i,j]**2
        rr = gr*(1-v*z)**2; pp = gr*(v-z)**2; qq = 1-z*z
        inv = 1/c['D'][i,j]
        fixed = (number[j]*rr+thermal[i,j]*(rr+(pp+qq)/3))*inv
        ub.add([(k,rr*inv),(size+k,pp*inv),(2*size+k,qq*inv),(peak,-1.)],-fixed)
    for i in range(nt):
        for j in range(nx):
            for z in np.linspace(-1,1,5):
                add_null(i,j,float(z))
    bounds = [(0.,None)]*size+[(None,None)]*(2*size)+[(0.,peak_cap)]
    cost = np.zeros(peak+1); cost[-1] = 1.
    return dict(eq=eq,ub=ub,bounds=bounds,cost=cost,size=size,peak=peak,c=c,
                add_null=add_null,energy_rhs=energy_rhs,nt=nt,nx=nx)


def solve_spacetime(t, x, coefficients, number, thermal, *, fraction=1., subpanels=1,
                    stress_rate=None, deadline=120., angular_rounds=3):
    start = time.monotonic()
    p = build_spacetime(t,x,coefficients,number,thermal,fraction=fraction,
                        subpanels=subpanels,stress_rate=stress_rate)
    eq = p['eq'].matrix(); size = p['size']; trace = []; last = None
    for iteration in range(angular_rounds):
        remaining = deadline-(time.monotonic()-start)
        if remaining < 1:
            break
        r = retained_coefficient_program(p['cost'],method='highs-ipm',deadline=remaining,
            A_eq=eq,b_eq=p['eq'].rhs,A_ub=p['ub'].matrix(),b_ub=p['ub'].rhs,bounds=p['bounds'])
        if not r.success:
            if last is None:
                return dict(success=False,status=int(r.status),message=r.message,
                            elapsed_seconds=time.monotonic()-start)
            break
        m, pr, pt = r.x[:-1].reshape(3,len(t),len(x)); c = p['c']
        tensor = anisotropic_moments((number+thermal+m)/c['D'],(thermal/3+pr)/c['D'],
                                     (thermal/3+pt)/c['D'],c['v'])
        value, z = maximum_null(tensor); upper = float(value.max()); lower = float(r.x[-1])
        checked = r.x.copy(); checked[-1] = max(upper,lower)
        er = eq@checked-p['eq'].rhs; ur = p['ub'].matrix()@checked-p['ub'].rhs
        error = max(float(abs(er).max()),float(np.maximum(ur,0).max()))
        if error > 2e-7:
            return dict(success=False,status=-3,message='original matrix verification failed',
                        maximum_scaled_error=error,elapsed_seconds=time.monotonic()-start)
        last = dict(success=True,support_energy=m,radial_volume=pr,angular_volume=pt,tensor=tensor,
                    material_peak_lower=lower,material_peak_upper=upper,
                    max_scaled_equality_residual=float(abs(er).max()),
                    max_raw_equality_residual=float(np.max(abs(er)*p['eq'].scales)),
                    max_inequality_violation=float(np.maximum(ur,0).max()),
                    local_exchange=p['energy_rhs'])
        trace.append(dict(lower=lower,upper=upper))
        bad = np.argwhere(value>lower+5e-5)
        if not len(bad):
            break
        for i,j in bad:
            p['add_null'](int(i),int(j),float(z[i,j]))
    if last is None:
        return dict(success=False,status=-2,message='total deadline reached before a feasible solution',
                    elapsed_seconds=time.monotonic()-start)
    last.update(angular_trace=trace,elapsed_seconds=time.monotonic()-start)
    return last
