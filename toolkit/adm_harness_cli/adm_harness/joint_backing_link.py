"""Counted elastic frame, angular rings, warm store and pressure-link inverse.

The electric/transport history and material congruence are prescribed inputs.
Prepared radial and circumferential elastic coefficients are fixed in material
labels. The fluid and warm backing may exchange heat, with zero additional
net local energy port. This is a constitutive mechanical model and an inverse
thermal coupling calculation; a heat-transfer law is a separate constraint.
"""
from __future__ import annotations

import numpy as np

from .composite_capacitor import anisotropic_moments
from .graded_electrothermal import SparseRows, maximum_null
from .pressure_linked_storage import retained_coefficient_program

FAMILIES=('radial_tension','radial_compression','ring_tension','ring_compression','skin')


def elastic_basis(c, log_radius_t):
    """Prepared U=A*ell+B/ell+C*R+D/R+T*R^2 per material label.

    The A/B and C/D pairs are the causal rigid-rod energy, with independently
    selected reference lengths. Their longitudinal sound speed is unity in
    the cold limit; co-moving pressure-free thermal inertia reduces it.
    The two equally populated angular directions share the ring pressure.
    """
    ell=c['gamma']*c['b'];r=c['radius'];volume=c['rest_volume']
    energy=np.array([ell,1/ell,r,1/r,r*r])
    density=energy/volume
    radial=np.zeros_like(density);angular=np.zeros_like(density)
    radial[0]=-density[0];radial[1]=density[1]
    angular[2]=-density[2]/2;angular[3]=density[3]/2;angular[4]=-density[4]
    log_ell_t=c['volume_rate']-2*log_radius_t
    radial_t=np.zeros_like(radial)
    radial_t[0]=2*log_radius_t*density[0]
    radial_t[1]=-2*(log_ell_t+log_radius_t)*density[1]
    return dict(energy=energy,density=density,radial=radial,angular=angular,radial_t=radial_t)


def assembled_material(thermal,warm,prepared,number,c,basis):
    density=number[None,:]/c['rest_volume']+(thermal+warm)/c['rest_volume']
    radial=thermal/(3*c['rest_volume'])
    angular=radial.copy()
    density=density+np.sum(basis['density']*prepared[:,None,:],axis=0)
    radial=radial+np.sum(basis['radial']*prepared[:,None,:],axis=0)
    angular=angular+np.sum(basis['angular']*prepared[:,None,:],axis=0)
    return anisotropic_moments(density,radial,angular,c['v'])


def build_problem(t,x,c,log_radius_t,thermal_reference,number,force_rhs,field_end,
                  *,prestrain_floor=.01,ends='exposed',freeze_fluid=False,thermal_constraint=None):
    """Finite-volume force and midpoint pressure-work equations, all linear.

    force_rhs is the cell average of ell times the force still required by
    the preceding endpoint realization. It is supplied by resolved quadrature.
    End balance sets fluid plus frame radial stress equal to radial field
    traction; propagating wave momentum remains an explicit boundary port.
    """
    t,x=np.asarray(t),np.asarray(x)
    nt,nx=len(t),len(x);size=nt*nx
    if nt<3 or nx<3 or prestrain_floor<0 or ends not in ('exposed','balanced'):
        raise ValueError('resolved history, nonnegative prestrain floor and valid end policy required')
    basis=elastic_basis(c,log_radius_t)
    peak=2*size+len(FAMILIES)*nx
    eq,ub=SparseRows(peak+1),SparseRows(peak+1)
    volume=c['rest_volume'];ell=c['gamma']*c['b'];v=c['v'];lapse=c['lapse']
    a,k=c['acceleration'],c['angular_gradient']
    cold=lambda family,j: 2*size+family*nx+j
    for i in range(1,nt):
        dl=np.log(volume[i]/volume[i-1])/6
        for j in range(nx):
            now=i*nx+j;old=now-nx
            rhs=(thermal_reference[i,j]*(1+dl[j])-thermal_reference[i-1,j]*(1-dl[j]))
            eq.add([(now,1+dl[j]),(old,-1+dl[j]),(size+now,1.),(size+old,-1.)],rhs)
    for i in range(nt):
        i0,i1=(i-1,i) if i else (0,1)
        dt=t[i1]-t[i0]
        for j,dx in enumerate(np.diff(x)):
            items=[];rhs=float(force_rhs[i,j])
            for jj,sign in ((j,-1),(j+1,1)):
                # Exact pressure difference across the spatial control cell.
                pscale=1/(3*volume[i,jj])
                items.append((i*nx+jj,sign*pscale/dx))
                rhs+=sign*thermal_reference[i,jj]*pscale/dx
                for b in range(len(FAMILIES)):
                    items.append((cold(b,jj),sign*basis['radial'][b,i,jj]/dx))
                # Trapezoidal geometry/body-force terms within this cell.
                temporal=ell[i,jj]*v[i,jj]/lapse[i,jj]
                enthalpy=ell[i,jj]*a[i,jj]
                weight=.5
                coefficient=weight*(4*enthalpy-temporal*c['volume_rate'][i,jj])*pscale
                items.append((i*nx+jj,coefficient))
                rhs+=coefficient*thermal_reference[i,jj]
                rate=weight*temporal*pscale/dt
                items.extend([(i1*nx+jj,rate),(i0*nx+jj,-rate)])
                rhs+=rate*(thermal_reference[i1,jj]-thermal_reference[i0,jj])
                items.append((size+i*nx+jj,weight*enthalpy/volume[i,jj]))
                for b in range(len(FAMILIES)):
                    rho=basis['density'][b,i,jj];pr=basis['radial'][b,i,jj];pt=basis['angular'][b,i,jj]
                    value=weight*(enthalpy*(rho+pr)+2*ell[i,jj]*k[i,jj]*(pr-pt)
                                  +temporal*basis['radial_t'][b,i,jj])
                    items.append((cold(b,jj),value))
            eq.add(items,rhs)
        if ends=='balanced':
            for j in (0,nx-1):
                items=[(i*nx+j,1/(3*volume[i,j]))]
                items.extend((cold(b,j),basis['radial'][b,i,j]) for b in range(len(FAMILIES)))
                eq.add(items,float(field_end[i,j]))
    # Positive finite compression terms keep the cold rods away from the
    # zero-stiffness pure-tension limit. Their relaxed lengths are counted.
    for j in range(nx):
        ub.add([(cold(0,j),prestrain_floor*np.max(ell[:,j]**2)),(cold(1,j),-1.)])
        ub.add([(cold(2,j),prestrain_floor*np.max(c['radius'][:,j]**2)),(cold(3,j),-1.)])
    if thermal_constraint is not None:
        sign,capacity_ratio,max_rate=thermal_constraint
        for i in range(1,nt):
            duration=(t[i]-t[i-1])*(lapse[i]+lapse[i-1])/2
            for j in range(nx):
                now=i*nx+j;old=now-nx;s=float(sign[i-1,j]);cap=float(capacity_ratio[j])
                if s==0:
                    eq.add([(size+now,1.),(size+old,-1.)])
                    continue
                # q=-Delta(warm); q and (warm-capacity*fluid) have the same
                # sign, with q bounded by a finite local exchange rate.
                ub.add([(size+now,s),(size+old,-s)])
                factor=.5*max_rate*duration[j]
                ub.add([(size+now,s*(-1-factor)),(size+old,s*(1-factor)),
                        (now,s*factor*cap),(old,s*factor*cap)])

    def null_row(i,j,z):
        gr=c['gamma'][i,j]**2
        rr=gr*(1-v[i,j]*z)**2;pp=gr*(v[i,j]-z)**2;tt=1-z*z
        coefficient=(rr+(pp+tt)/3)/volume[i,j]
        items=[(i*nx+j,coefficient),(size+i*nx+j,rr/volume[i,j]),(peak,-1.)]
        for b in range(len(FAMILIES)):
            val=(rr*basis['density'][b,i,j]+pp*basis['radial'][b,i,j]+tt*basis['angular'][b,i,j])
            items.append((cold(b,j),val))
        ub.add(items,-number[j]*rr/volume[i,j])
    for i in range(nt):
        for j in range(nx):
            for z in np.linspace(-1,1,5):
                null_row(i,j,float(z))
    bounds=[(0.,None)]*(peak+1)
    if freeze_fluid:
        for i in range(nt):
            for j in range(nx):
                bounds[i*nx+j]=(float(thermal_reference[i,j]),)*2
    cost=np.zeros(peak+1);cost[-1]=1.
    return dict(eq=eq,ub=ub,bounds=bounds,cost=cost,basis=basis,null_row=null_row,
                nt=nt,nx=nx,size=size,peak=peak)


def solve_joint(t,x,c,log_radius_t,thermal_reference,number,force_rhs,field_end,
                *,prestrain_floor=.01,ends='exposed',freeze_fluid=False,deadline=90.,thermal_constraint=None):
    p=build_problem(t,x,c,log_radius_t,thermal_reference,number,force_rhs,field_end,
                    prestrain_floor=prestrain_floor,ends=ends,freeze_fluid=freeze_fluid,
                    thermal_constraint=thermal_constraint)
    eq,ub=p['eq'],p['ub'];size=p['size'];nt,nx=p['nt'],p['nx']
    equality=eq.matrix()
    for iteration in range(6):
        result=retained_coefficient_program(p['cost'],method='highs-ipm',deadline=deadline,
            A_eq=equality,b_eq=eq.rhs,A_ub=ub.matrix(),b_ub=ub.rhs,bounds=p['bounds'])
        if not result.success:
            return dict(success=False,status=int(result.status),message=result.message,
                        variables=p['peak']+1,equalities=len(eq.rhs),inequalities=len(ub.rhs))
        thermal=result.x[:size].reshape(nt,nx)
        warm=result.x[size:2*size].reshape(nt,nx)
        prepared=result.x[2*size:-1].reshape(len(FAMILIES),nx)
        tensor=assembled_material(thermal,warm,prepared,number,c,p['basis'])
        val,z=maximum_null(tensor)
        bad=np.argwhere(val>result.x[-1]+2e-8*max(1.,result.x[-1]))
        if not len(bad):
            break
        for i,j in bad:
            p['null_row'](int(i),int(j),float(z[i,j]))
    else:
        return dict(success=False,status=-1,message='angular maximization remained unresolved')
    residual=equality@result.x-np.asarray(eq.rhs)
    inequality=ub.matrix()@result.x-np.asarray(ub.rhs)
    return dict(success=True,thermal=thermal,warm=warm,prepared=prepared,tensor=tensor,
        optimal_material_null_peak=float(result.x[-1]),
        max_scaled_equality_residual=float(abs(residual).max()),
        max_raw_equality_residual=float(np.max(abs(residual)*eq.scales)),
        max_inequality_violation=float(max(0.,inequality.max())),
        angular_rounds=iteration+1,variables=p['peak']+1,equalities=len(eq.rhs),inequalities=len(ub.rhs))


def passive_heat_capacity_interval(t,thermal,warm):
    """Constant local heat-capacity ratios admitting down-temperature exchange.

    T_fluid=U/(3N), T_warm=Z/(3N*capacity_ratio), q=-Delta Z. A variable
    positive contact conductance is allowed; finite rates require an additional
    margin or a constrained solve. Tiny roundoff exchange is excluded.
    """
    u=(thermal[1:]+thermal[:-1])/2;z=(warm[1:]+warm[:-1])/2
    q=-np.diff(warm,axis=0)
    tolerance=1e-8*np.maximum(1.,np.max(abs(q),axis=0))
    positive=q>tolerance;negative=q<-tolerance
    ratio=np.divide(z,u,out=np.full_like(z,np.inf),where=u>1e-14)
    lo=np.max(np.where(negative,ratio,0.),axis=0)
    hi=np.min(np.where(positive,ratio,np.inf),axis=0)
    admissible=(lo<=hi)&(hi>0)&np.isfinite(lo)
    return dict(lower=lo,upper=hi,admissible=admissible,exchange=q,
                positive=positive,negative=negative,ratio=ratio)
