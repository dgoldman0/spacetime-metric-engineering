"""Minimize resolved conservation error under a finite material inventory cap.

Energy remains integrated exactly in each temporal panel. Two temporal force
samples and two power samples bound a common rest-frame divergence error.
This prevents declaring failure from overdetermined exact low-order fitting,
and prevents an optimizer from hiding rapid variation at temporal midpoints.
"""
from __future__ import annotations

import time
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.sparse import hstack, vstack, csr_matrix

from .composite_capacitor import anisotropic_moments
from .graded_electrothermal import SparseRows, maximum_null
from .joint_support_gauss import build_spacetime
from .pressure_linked_storage import retained_coefficient_program


def solve_residual(t,x,coefficients,number,thermal,*,fraction=.9,material_cap=.2,
                   subpanels=1,deadline=240.,inspect=False):
    start = time.monotonic()
    p = build_spacetime(t,x,coefficients,number,thermal,fraction=fraction,subpanels=subpanels)
    nt,nx,size = len(t),len(x),p['size']; epsilon = p['peak']+1; columns = epsilon+1
    nenergy = (nt-1)*nx
    matrix = p['eq'].matrix(); scales = np.asarray(p['eq'].scales)
    eq = hstack([matrix[:nenergy],csr_matrix((nenergy,1))],format='csr')
    eqrhs = np.asarray(p['eq'].rhs[:nenergy])
    momentum = matrix[nenergy:]
    temporal_nodes = (leggauss(2)[0]+1)/2
    tf = (t[:-1,None]+np.diff(t)[:,None]*temporal_nodes).ravel()
    z,w = leggauss(4); theta=(z+1)/2
    fractions = ((np.arange(subpanels)[:,None]+theta)/subpanels).ravel()
    xq = (x[:-1,None]+np.diff(x)[:,None]*fractions).ravel()
    cf = coefficients(tf,xq)
    iell = np.sum(cf['ell'].reshape(len(tf),nx-1,len(fractions))*
                   np.tile(w/(2*subpanels),subpanels)[None,None,:],axis=2)*np.diff(x)
    epsilon_coefficient = (iell.ravel()/scales[nenergy:])[:,None]
    force_ub = [hstack([sign*momentum,csr_matrix(-epsilon_coefficient)],format='csr') for sign in (1.,-1.)]
    force_rhs = np.asarray(p['eq'].rhs[nenergy:])
    extra = SparseRows(columns)
    c = coefficients(tf,x)
    for i in range(len(tf)):
        lo,hi = i//2,i//2+1; weight = temporal_nodes[i%2]; dt=t[hi]-t[lo]
        for j in range(nx):
            inv = 1/(c['lapse'][i,j]*c['D'][i,j])
            items = [(hi*nx+j,inv/dt),(lo*nx+j,-inv/dt)]
            for ii,ww in ((lo,1-weight),(hi,weight)):
                items.extend([(size+ii*nx+j,ww*c['log_ell_t'][i,j]*inv),
                              (2*size+ii*nx+j,ww*2*c['log_radius_t'][i,j]*inv)])
            for sign in (1.,-1.):
                extra.add([(k,sign*v) for k,v in items]+[(epsilon,-1.)],-sign*c['fixed_power'][i,j])
    c = p['c']
    # Conservative all-angle cap: in the rest frame a null projection is
    # at most rho+max(p_r,p_t), with boost factor <= Gamma^2(1+|v|)^2.
    for i in range(nt):
        for j in range(nx):
            k=i*nx+j
            factor=c['gamma'][i,j]**2*(1+abs(c['v'][i,j]))**2/c['D'][i,j]
            rhs=material_cap-factor*(number[j]+4*thermal[i,j]/3)
            for component in (1,2):
                extra.add([(k,factor),(component*size+k,factor)],rhs)
    baseub=hstack([p['ub'].matrix(),csr_matrix((len(p['ub'].rhs),1))],format='csr')
    ub=vstack([baseub,*force_ub,extra.matrix()],format='csr')
    ubrhs=np.r_[p['ub'].rhs,force_rhs,-force_rhs,extra.rhs]
    bounds=p['bounds']+[(0.,None)]
    bounds[p['peak']] = (0.,material_cap)
    cost=np.zeros(columns);cost[epsilon]=1.
    if inspect:
        return dict(A_eq=eq,b_eq=eqrhs,A_ub=ub,b_ub=ubrhs,bounds=bounds,cost=cost,
                    equation_scales=scales[:nenergy],problem=p,epsilon_index=epsilon)
    remaining=deadline-(time.monotonic()-start)
    if remaining<1:
        return dict(success=False,status=-2,message='build exhausted total deadline')
    r=retained_coefficient_program(cost,method='highs-ipm',deadline=remaining,
        A_eq=eq,b_eq=eqrhs,A_ub=ub,b_ub=ubrhs,bounds=bounds)
    if not r.success:
        return dict(success=False,status=int(r.status),message=r.message,
                    elapsed_seconds=time.monotonic()-start)
    er=eq@r.x-eqrhs;ur=ub@r.x-ubrhs
    error=max(float(abs(er).max()),float(np.maximum(ur,0).max()))
    m,pr,pt=r.x[:3*size].reshape(3,nt,nx)
    tensor=anisotropic_moments((number+thermal+m)/c['D'],(thermal/3+pr)/c['D'],
                               (thermal/3+pt)/c['D'],c['v'])
    exact=float(maximum_null(tensor)[0].max())
    valid=error<=2e-7 and exact<=material_cap+2e-7
    return dict(success=valid,message='verified residual minimum' if valid else 'independent verification failed',
        support_energy=m,radial_volume=pr,angular_volume=pt,tensor=tensor,
        material_peak_upper=exact,conservative_material_cap=material_cap,
        resolved_divergence_bound=float(r.x[epsilon]),max_scaled_equality_residual=float(abs(er).max()),
        max_raw_equality_residual=float(np.max(abs(er)*scales[:nenergy])),
        max_inequality_violation=float(np.maximum(ur,0).max()),
        local_exchange=p['energy_rhs'],elapsed_seconds=time.monotonic()-start,
        variables=columns,equalities=eq.shape[0],inequalities=ub.shape[0])
