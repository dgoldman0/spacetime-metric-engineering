"""Implicit time evolution of a pressure-constrained support history.

Energy work is centered; the momentum equation uses backward Euler pressure
rates. Spatial pressure equations are marched from the incoming right cut.
The initial pressure is equilibrated against a specified initial pressure rate.
This treats zero-shift intervals as algebraic force constraints and avoids
inferring initial pressure from a whole-history temporal collocation block.
"""
import numpy as np
from numpy.polynomial.legendre import leggauss


def evolve_support(t,x,coefficients,initial_energy,incoming_pressure,initial_pressure_rate,
                   *,subpanels=1,initial_pressure=None):
    t,x=np.asarray(t),np.asarray(x);nt,nx=len(t),len(x)
    if np.any(np.diff(t)<=0) or np.any(np.diff(x)<=0):raise ValueError('ordered grids required')
    z,w=leggauss(4);theta=(z+1)/2;weights=w/2
    te=(t[:-1,None]+np.diff(t)[:,None]*theta).ravel()
    ce=coefficients(te,x);shape=(nt-1,4,nx)
    measure=np.diff(t)[:,None,None]*weights[None,:,None]
    work=(ce['D']*ce['log_ell_t']).reshape(shape)
    old=np.sum(measure*work*(1-theta)[None,:,None],axis=1)
    new=np.sum(measure*work*theta[None,:,None],axis=1)
    exchange=np.sum(measure*(-ce['lapse']*ce['D']*ce['fixed_power']).reshape(shape),axis=1)
    increment=exchange-np.sum(measure*(2*ce['Q']*ce['log_radius_t']).reshape(shape),axis=1)
    fractions=((np.arange(subpanels)[:,None]+theta)/subpanels).ravel()
    xq=(x[:-1,None]+np.diff(x)[:,None]*fractions).ravel()
    # Original source time derivatives are piecewise constant. Use the side
    # belonging to the interval just evolved, including at native source knots.
    tf=np.r_[t[0],np.nextafter(t[1:],-np.inf)]
    cf=coefficients(tf,xq);fshape=(nt,nx-1,len(fractions))
    measure_x=np.diff(x)[None,:,None]*np.tile(weights/subpanels,subpanels)[None,None,:]
    integrate=lambda a:np.sum(a.reshape(fshape)*measure_x,axis=2)
    bodies=[]
    for side in (1-fractions,fractions):
        basis=np.tile(side,nx-1)[None,:]
        bodies.append(dict(M=integrate(cf['ell']*cf['acceleration']/cf['D']*basis),
                           P=integrate(cf['ell']*(cf['acceleration']+2*cf['angular_gradient'])*basis),
                           Pt=integrate(cf['ell']*cf['v']/cf['lapse']*basis)))
    rhs=integrate(-cf['ell']*cf['fixed_force']+2*cf['ell']*cf['angular_gradient']*cf['Q']/cf['D'])
    m=np.empty((nt,nx));p=np.empty((nt,nx));m[0]=initial_energy
    p[:,-1]=incoming_pressure
    min_pivot=np.inf;max_residual=0.
    if initial_pressure is None:
        for j in range(nx-2,-1,-1):
            left=-1+bodies[0]['P'][0,j];right=1+bodies[1]['P'][0,j]
            value=(rhs[0,j]-bodies[0]['M'][0,j]*m[0,j]-bodies[1]['M'][0,j]*m[0,j+1]-
                   bodies[0]['Pt'][0,j]*initial_pressure_rate[j]-bodies[1]['Pt'][0,j]*initial_pressure_rate[j+1])
            p[0,j]=(value-right*p[0,j+1])/left
            min_pivot=min(min_pivot,abs(left))
    else:
        p[0]=initial_pressure
        if abs(p[0,-1]-incoming_pressure[0])>1e-10:raise ValueError('initial pressure and incoming corner disagree')
    for i,dt in enumerate(np.diff(t),1):
        b=m[i-1]+increment[i-1]-old[i-1]*p[i-1]
        for j in range(nx-2,-1,-1):
            left=-1+bodies[0]['P'][i,j]+bodies[0]['Pt'][i,j]/dt-bodies[0]['M'][i,j]*new[i-1,j]
            right=1+bodies[1]['P'][i,j]+bodies[1]['Pt'][i,j]/dt-bodies[1]['M'][i,j]*new[i-1,j+1]
            value=(rhs[i,j]-bodies[0]['M'][i,j]*b[j]-bodies[1]['M'][i,j]*b[j+1]+
                   bodies[0]['Pt'][i,j]*p[i-1,j]/dt+bodies[1]['Pt'][i,j]*p[i-1,j+1]/dt)
            p[i,j]=(value-right*p[i,j+1])/left
            min_pivot=min(min_pivot,abs(left))
            max_residual=max(max_residual,abs(left*p[i,j]+right*p[i,j+1]-value))
        m[i]=b-new[i-1]*p[i]
    return dict(support_energy=m,radial_pressure=p,local_exchange=exchange,
                minimum_spatial_pivot=float(min_pivot),maximum_step_force_residual=float(max_residual))
