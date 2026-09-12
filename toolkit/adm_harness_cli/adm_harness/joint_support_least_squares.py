"""Sparse convex conservation fit with counted material and optional end jackets.

Quadratic rest-frame force/power residuals replace a highly degenerate minimax
epigraph. Bilinear member costs, integrated work, and all-angle inventory caps
remain constraints. OSQP is an optional research dependency.
"""
from __future__ import annotations

import time
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.sparse import csr_matrix, diags, hstack, vstack, eye

from .composite_capacitor import anisotropic_moments
from .graded_electrothermal import SparseRows, maximum_null
from .joint_support_gauss import build_spacetime


def solve_least_squares(t,x,coefficients,number,thermal,reference,*,fraction=.9,
                        material_cap=.2,subpanels=1,deadline=150.,regularization=1e-10,
                        surface_width=None,electric=None,inspect=False):
    import osqp
    start=time.monotonic()
    p=build_spacetime(t,x,coefficients,number,thermal,fraction=fraction,subpanels=subpanels)
    nt,nx,size=len(t),len(x),p['size']; bulk=3*size
    nenergy=(nt-1)*nx; extra_size=4*nt if surface_width is not None else 0
    columns=bulk+extra_size
    eq=p['eq'].matrix();eqrhs=np.asarray(p['eq'].rhs);eqscales=np.asarray(p['eq'].scales)
    tnodes=(leggauss(2)[0]+1)/2
    tf=(t[:-1,None]+np.diff(t)[:,None]*tnodes).ravel()
    z,w=leggauss(4);fractions=((np.arange(subpanels)[:,None]+(z+1)/2)/subpanels).ravel()
    wx=np.tile(w/(2*subpanels),subpanels)
    xq=(x[:-1,None]+np.diff(x)[:,None]*fractions).ravel()
    cf=coefficients(tf,xq)
    shape=(len(tf),nx-1,len(fractions))
    iell=np.sum(cf['ell'].reshape(shape)*wx[None,None,:],axis=2)*np.diff(x)
    proper_f=np.sum((cf['lapse']*cf['D']).reshape(shape)*wx[None,None,:],axis=2)*np.diff(x)
    proper_f*=np.repeat(np.diff(t)/2,2)[:,None]
    force=diags(eqscales[nenergy:]/iell.ravel())@eq[nenergy:,:bulk]
    force_rhs=eqrhs[nenergy:]*eqscales[nenergy:]/iell.ravel()
    powers=SparseRows(bulk);c=coefficients(tf,x)
    for i in range(len(tf)):
        lo,hi=i//2,i//2+1;ww=tnodes[i%2];dt=t[hi]-t[lo]
        for j in range(nx):
            inv=1/(c['lapse'][i,j]*c['D'][i,j])
            items=[(hi*nx+j,inv/dt),(lo*nx+j,-inv/dt)]
            for ii,weight in ((lo,1-ww),(hi,ww)):
                items.extend([(size+ii*nx+j,weight*c['log_ell_t'][i,j]*inv),
                              (2*size+ii*nx+j,weight*2*c['log_radius_t'][i,j]*inv)])
            powers.add(items,-c['fixed_power'][i,j])
    power=diags(powers.scales)@powers.matrix();power_rhs=np.asarray(powers.rhs)*powers.scales
    dx=np.r_[np.diff(x)[0]/2,(x[2:]-x[:-2])/2,np.diff(x)[-1]/2]
    proper_p=(c['lapse']*c['D'])*np.repeat(np.diff(t)/2,2)[:,None]*dx
    normalization=float(proper_f.sum()+proper_p.sum())
    wf=np.sqrt(proper_f.ravel()/normalization);wp=np.sqrt(proper_p.ravel()/normalization)
    residual=vstack([diags(wf)@force,diags(wp)@power],format='csr')
    residual_rhs=np.r_[wf*force_rhs,wp*power_rhs]
    residual=hstack([residual,csr_matrix((residual.shape[0],extra_size))],format='csr')

    baseub=p['ub'].matrix()
    ub=baseub[:,:bulk]
    ubrhs=np.asarray(p['ub'].rhs)-baseub[:,bulk].toarray().ravel()*material_cap
    constraints=[hstack([eq[:nenergy,:bulk],csr_matrix((nenergy,extra_size))],format='csr'),
                 hstack([ub,csr_matrix((ub.shape[0],extra_size))],format='csr')]
    lower=[eqrhs[:nenergy],np.full(ub.shape[0],-np.inf)]
    upper=[eqrhs[:nenergy],ubrhs]
    extra=SparseRows(columns);exact=SparseRows(columns)
    nodes=p['c']
    for i in range(nt):
        for j in range(nx):
            k=i*nx+j;factor=nodes['gamma'][i,j]**2*(1+abs(nodes['v'][i,j]))**2/nodes['D'][i,j]
            fixed=factor*(number[j]+4*thermal[i,j]/3)
            for component in (1,2):
                extra.add([(k,factor),(component*size+k,factor)],material_cap-fixed)
            extra.add([(k,-1.)])
    scale=np.tile(nodes['D'].ravel(),3)
    reference_vector=np.asarray(reference).reshape(-1)/scale
    if surface_width is not None:
        if electric is None or surface_width<=0:
            raise ValueError('positive declared jacket width and capacitor field required')
        for end,j,orientation in ((0,0,-1.),(1,nx-1,1.)):
            iy=bulk+2*nt*end;iz=iy+nt
            r=nodes['radius'][:,j];ell=nodes['ell'][:,j]
            for i in range(nt):
                exact.add([(iy+i,nodes['acceleration'][i,j]),(iz+i,-2*nodes['angular_gradient'][i,j]),
                           (size+i*nx+j,-orientation/ell[i])],
                          orientation*(thermal[i,j]/(3*ell[i])-r[i]**2*electric[i,j]))
                extra.add([(iy+i,-1.)])
                for sign in (-1.,1.):extra.add([(iz+i,sign),(iy+i,-fraction)])
                factor=nodes['gamma'][i,j]**2*(1+abs(nodes['v'][i,j]))**2/(nodes['D'][i,j]*surface_width)
                extra.add([(iy+i,factor)],material_cap)
                extra.add([(iy+i,factor),(iz+i,factor)],material_cap)
            for i,dr in enumerate(np.diff(np.log(r)),1):
                exact.add([(iy+i,1.),(iy+i-1,-1.),(iz+i,dr),(iz+i-1,dr)])
            scale=np.r_[scale,nodes['D'][:,j]*surface_width,nodes['D'][:,j]*surface_width]
        reference_vector=np.r_[reference_vector,np.zeros(extra_size)]
    constraints.append(extra.matrix());lower.append(np.full(len(extra.rhs),-np.inf));upper.append(np.asarray(extra.rhs))
    if exact.rhs:
        constraints.append(exact.matrix());lower.append(np.asarray(exact.rhs));upper.append(np.asarray(exact.rhs))
    A=vstack(constraints,format='csr')@diags(scale)
    l=np.concatenate(lower);u=np.concatenate(upper)
    rowmax=np.asarray(abs(A).max(axis=1).toarray()).ravel()
    rowmax=np.maximum(rowmax,1e-20)
    A=(diags(1/rowmax)@A).tocsc();l=l/rowmax;u=u/rowmax
    R=(residual@diags(scale)).tocsc()
    P=(R.T@R+regularization*eye(columns,format='csc')).tocsc()
    q=-np.asarray(R.T@residual_rhs).ravel()-regularization*reference_vector
    if inspect:return dict(P=P,q=q,A=A,l=l,u=u,scale=scale,residual=R,residual_rhs=residual_rhs)
    solver=osqp.OSQP()
    solver.setup(P=P,q=q,A=A,l=l,u=u,verbose=False,eps_abs=2e-8,eps_rel=2e-8,
                 max_iter=60000,polishing=True,adaptive_rho=True,
                 time_limit=max(1.,deadline-(time.monotonic()-start)))
    solver.warm_start(x=reference_vector)
    result=solver.solve(raise_error=False)
    if result.x is None or not np.isfinite(result.x).all():
        return dict(success=False,message=result.info.status,optimizer_converged=False,
                    elapsed_seconds=time.monotonic()-start)
    z=result.x;v=A@z
    error=float(max(np.maximum(l-v,0).max(),np.maximum(v-u,0).max()))
    value=z*scale;m,pr,pt=value[:bulk].reshape(3,nt,nx)
    d=nodes['D'];tensor=anisotropic_moments((number+thermal+m)/d,(thermal/3+pr)/d,
                                          (thermal/3+pt)/d,nodes['v'])
    peak=float(maximum_null(tensor)[0].max())
    member=float(np.maximum((abs(pr)+np.maximum(-pt,2*pt)-fraction*m)/d,0).max())
    min_density=float((m/d).min())
    energy_error=eq[:nenergy,:bulk]@value[:bulk]-eqrhs[:nenergy]
    out=dict(success=error<2e-6 and member<2e-7 and min_density>-2e-7 and peak<material_cap+2e-7,
             message=result.info.status,optimizer_converged=result.info.status_val==1,
             optimizer_iterations=result.info.iter,optimizer_primal_residual=result.info.prim_res,
             optimizer_dual_residual=result.info.dual_res,maximum_scaled_constraint_violation=error,
             max_member_density_violation=member,minimum_support_density=min_density,
             max_raw_energy_residual=float(np.max(abs(energy_error)*eqscales[:nenergy])),
             weighted_squared_divergence=float(np.sum((R@z-residual_rhs)**2)),
             material_peak_upper=peak,conservative_material_cap=material_cap,
             support_energy=m,radial_volume=pr,angular_volume=pt,tensor=tensor,
             local_exchange=p['energy_rhs'],surface_width=surface_width,regularization=regularization,
             elapsed_seconds=time.monotonic()-start,variables=columns,constraints=A.shape[0],
             osqp_version=osqp.__version__)
    if surface_width is not None:
        out['surface_energy']=np.array([value[bulk:bulk+nt],value[bulk+2*nt:bulk+3*nt]]).T
        out['surface_angular_stress']=np.array([value[bulk+nt:bulk+2*nt],value[bulk+3*nt:]]).T
    return out
