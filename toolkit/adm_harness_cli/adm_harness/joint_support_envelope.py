"""Joint energy/momentum envelope with freely scheduled material stresses.

This is a necessary constitutive target, not an equation of state. The support
owns its positive energy, radial/angular stresses, deformation work, and end
tractions. Its stress-to-energy ceiling is a declared comparison parameter.
"""
from __future__ import annotations

import numpy as np

from .composite_capacitor import anisotropic_moments
from .graded_electrothermal import SparseRows,maximum_null
from .pressure_linked_storage import retained_coefficient_program


def build_envelope(t,x,c,log_radius_t,thermal_reference,number,force_rhs,field_end,
                   *,stress_fraction=1.,ends='exposed',freeze_fluid=False):
    nt,nx=len(t),len(x);size=nt*nx;peak=4*size
    if not 0<stress_fraction<=1 or ends not in ('exposed','balanced'):
        raise ValueError('0 < stress fraction <= 1 and a registered end policy required')
    eq,ub=SparseRows(peak+1),SparseRows(peak+1)
    vol=c['rest_volume'];ell=c['gamma']*c['b'];radius=c['radius']
    # Variables: fluid thermal energy U, support energy M, support radial
    # stress-volume P, support angular stress-volume Q, peak null projection.
    for i in range(1,nt):
        dl=np.log(vol[i]/vol[i-1]);dr=np.log(radius[i]/radius[i-1])
        de=np.log(ell[i]/ell[i-1])
        for j in range(nx):
            now=i*nx+j;old=now-nx
            rhs=thermal_reference[i,j]*(1+dl[j]/6)-thermal_reference[i-1,j]*(1-dl[j]/6)
            eq.add([(now,1+dl[j]/6),(old,-1+dl[j]/6),
                    (size+now,1.),(size+old,-1.),
                    (2*size+now,de[j]/2),(2*size+old,de[j]/2),
                    (3*size+now,dr[j]),(3*size+old,dr[j])],rhs)
    for i in range(nt):
        i0,i1=(i-1,i) if i else (0,1);dt=t[i1]-t[i0]
        for j,dx in enumerate(np.diff(x)):
            items=[];rhs=float(force_rhs[i,j])
            for jj,sign in ((j,-1),(j+1,1)):
                k=i*nx+jj;inv=1/vol[i,jj]
                items.extend([(k,sign*inv/(3*dx)),(2*size+k,sign*inv/dx)])
                rhs+=sign*inv*thermal_reference[i,jj]/(3*dx)
                temporal=ell[i,jj]*c['v'][i,jj]/c['lapse'][i,jj]
                a=ell[i,jj]*c['acceleration'][i,jj]
                angular=ell[i,jj]*c['angular_gradient'][i,jj]
                rate=c['volume_rate'][i,jj]
                fc=.5*inv*(4*a-temporal*rate)/3
                items.append((k,fc));rhs+=fc*thermal_reference[i,jj]
                fr=.5*inv*temporal/(3*dt)
                items.extend([(i1*nx+jj,fr),(i0*nx+jj,-fr)])
                rhs+=fr*(thermal_reference[i1,jj]-thermal_reference[i0,jj])
                items.extend([(size+k,.5*inv*a),
                              (2*size+k,.5*inv*(a+2*angular-temporal*rate)),
                              (3*size+k,-inv*angular),
                              (2*size+i1*nx+jj,.5*inv*temporal/dt),
                              (2*size+i0*nx+jj,-.5*inv*temporal/dt)])
            eq.add(items,rhs)
        if ends=='balanced':
            for j in (0,nx-1):
                k=i*nx+j
                eq.add([(k,1/(3*vol[i,j])),(2*size+k,1/vol[i,j])],float(field_end[i,j]))
    for k in range(size):
        for component in (2,3):
            for sign in (-1.,1.):
                ub.add([(component*size+k,sign),(size+k,-stress_fraction)])

    def null_row(i,j,z):
        k=i*nx+j;v=c['v'][i,j];gamma=c['gamma'][i,j]
        rr=gamma**2*(1-v*z)**2;pr=gamma**2*(v-z)**2;pt=1-z*z
        inv=1/vol[i,j]
        ub.add([(k,(rr+(pr+pt)/3)*inv),(size+k,rr*inv),
                (2*size+k,pr*inv),(3*size+k,pt*inv),(peak,-1.)],-number[j]*rr*inv)
    for i in range(nt):
        for j in range(nx):
            for z in np.linspace(-1,1,5):
                null_row(i,j,float(z))
    bounds=[(0.,None)]*(2*size)+[(None,None)]*(2*size)+[(0.,None)]
    if freeze_fluid:
        for i in range(nt):
            for j in range(nx):
                bounds[i*nx+j]=(float(thermal_reference[i,j]),)*2
    cost=np.zeros(peak+1);cost[peak]=1.
    return dict(eq=eq,ub=ub,bounds=bounds,cost=cost,null_row=null_row,size=size,peak=peak,nt=nt,nx=nx)


def solve_envelope(t,x,c,log_radius_t,thermal_reference,number,force_rhs,field_end,
                   *,stress_fraction=1.,ends='exposed',freeze_fluid=False,deadline=100.,
                   angular_tolerance=1e-6,angular_rounds=24):
    p=build_envelope(t,x,c,log_radius_t,thermal_reference,number,force_rhs,field_end,
                     stress_fraction=stress_fraction,ends=ends,freeze_fluid=freeze_fluid)
    eq,ub=p['eq'],p['ub'];size=p['size'];nt,nx=p['nt'],p['nx'];vol=c['rest_volume']
    equality=eq.matrix()
    trace=[]
    for iteration in range(angular_rounds):
        result=retained_coefficient_program(p['cost'],method='highs-ipm',deadline=deadline,
            A_eq=equality,b_eq=eq.rhs,A_ub=ub.matrix(),b_ub=ub.rhs,bounds=p['bounds'])
        if not result.success:
            return dict(success=False,status=int(result.status),message=result.message,
                        variables=p['peak']+1,equalities=len(eq.rhs),inequalities=len(ub.rhs))
        u,m,pr,pt=result.x[:-1].reshape(4,nt,nx)
        tensor=anisotropic_moments((number[None,:]+u+m)/vol,(u/3+pr)/vol,(u/3+pt)/vol,c['v'])
        val,z=maximum_null(tensor)
        excess=float(val.max()-result.x[-1])
        trace.append(dict(round=iteration+1,lower_peak=float(result.x[-1]),exact_peak=float(val.max()),
                          angular_gap=excess))
        bad=np.argwhere(val>result.x[-1]+angular_tolerance*max(1.,result.x[-1]))
        if not len(bad):
            break
        for i,j in bad:
            p['null_row'](int(i),int(j),float(z[i,j]))
    else:
        return dict(success=False,status=-1,message='angular maximization remained unresolved',angular_trace=trace)
    residual=equality@result.x-np.asarray(eq.rhs)
    violation=ub.matrix()@result.x-np.asarray(ub.rhs)
    return dict(success=True,thermal=u,support_energy=m,radial_volume=pr,angular_volume=pt,tensor=tensor,
        optimal_material_null_peak=float(result.x[-1]),max_scaled_equality_residual=float(abs(residual).max()),
        exact_material_null_peak=float(val.max()),angular_optimization_gap=excess,angular_trace=trace,
        max_raw_equality_residual=float(np.max(abs(residual)*eq.scales)),
        max_inequality_violation=float(max(0.,violation.max())),angular_rounds=iteration+1,
        variables=p['peak']+1,equalities=len(eq.rhs),inequalities=len(ub.rhs))
