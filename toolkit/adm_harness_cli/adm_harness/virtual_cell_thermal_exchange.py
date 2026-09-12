"""Counted local material storage coupled to phase and radial photons.

This sampled energy/cone gate permits bidirectional exchange with a positive
material reservoir of isotropic EOS p=w*B. Opacity, detailed balance, force
exchange, and the remaining auxiliary constituent laws are separate gates.
"""
from __future__ import annotations

import warnings

import numpy as np
from scipy.optimize import OptimizeWarning, linprog
from scipy.sparse import coo_matrix


def thermal_exchange_problem(rho, p, q, wall, radius, ell,
                             panel_mean_ell_squared, panel_mean_exchange_weight,
                             *, w, fixed_amplitude=None, radiation_floor=None):
    """Build a local LP for A,U=M*W,K=D**(1+w)*B and uniform extra rho.

Here D=ell*R**2 and M=(ell*R)**2. For piecewise-linear A,K the exact
panel energy law is delta U + mean(ell**2)*delta A +
mean(M/D**(1+w))*delta K=0. The three positive-mixture facets subtract
the counted thermal tensor B*(1,w,w). The existing interface wall is
retained; the additional explicit-wave guide floor is omitted favorably.
"""
    if w not in (0.,1/3):raise ValueError('w must be 0 or 1/3 for this bounded gate')
    rho,p,q,h,r,length=np.broadcast_arrays(rho,p,q,wall,radius,ell)
    if rho.ndim!=1 or len(rho)<2 or np.any(r<=0) or np.any(length<=0) or np.any(h<0):
        raise ValueError('one-dimensional history with positive geometry and nonnegative wall required')
    n=len(rho);phi=np.asarray(panel_mean_ell_squared,dtype=float)
    psi=np.asarray(panel_mean_exchange_weight,dtype=float)
    if phi.shape!=(n-1,) or psi.shape!=(n-1,) or np.any(phi<=0) or np.any(psi<=0):
        raise ValueError('positive geometry means are required for every panel')
    fixed=None if fixed_amplitude is None else np.asarray(fixed_amplitude,dtype=float)
    floor=np.zeros(n) if radiation_floor is None else np.asarray(radiation_floor,dtype=float)
    if floor.shape!=(n,) or np.any(floor<0):
        raise ValueError('radiation_floor must be a nonnegative node history')
    if fixed is not None and (fixed.shape!=(n,) or np.any(fixed<0)):
        raise ValueError('fixed_amplitude must be a nonnegative node history')
    arrays=(rho,p,q,h,r,length,phi,psi,floor) if fixed is None else (rho,p,q,h,r,length,phi,psi,floor,fixed)
    if not all(np.isfinite(a).all() for a in arrays):raise ValueError('finite histories required')
    measure=(length*r)**2;volume=length*r*r;thermal_weight=volume**(1+w)
    rhs=np.concatenate([rho-p+q,rho-p-2*q-3*h,rho+2*p+q])
    node=np.arange(n);rows=np.arange(3*n);panel=np.arange(n-1)
    a_coeff=np.r_[2/r**2,2/r**2,-1/r**2]
    k_coeff=np.concatenate([1/thermal_weight,(1-3*w)/thermal_weight,(1+3*w)/thermal_weight])
    inequality=coo_matrix((np.r_[a_coeff,3/measure,k_coeff,-np.ones(3*n)],
        (np.r_[rows,2*n+node,rows,rows],
         np.r_[np.tile(node,3),n+node,2*n+np.tile(node,3),np.full(3*n,3*n)])),
        shape=(3*n,3*n+1)).tocsr()
    equality=coo_matrix((np.r_[-phi,phi,-np.ones(n-1),np.ones(n-1),-psi,psi],
        (np.tile(panel,6),np.r_[panel,panel+1,n+panel,n+panel+1,2*n+panel,2*n+panel+1])),
        shape=(n-1,3*n+1)).tocsr()

    # An explicit feasible competitor bounds the minimizing allowance:
    # constant U above every wave floor, prescribed A (or zero), and enough
    # prepared K to keep its exactly balanced panel history nonnegative.
    trial_a=np.zeros(n) if fixed is None else fixed.copy()
    trial_u=np.full(n,float(np.max(measure*floor)))
    trial_k=np.r_[0.,np.cumsum(-phi*np.diff(trial_a)/psi)]
    trial_k-=min(0.,float(trial_k.min()))
    competitor=np.r_[trial_a,trial_u,trial_k,0.]
    competitor[-1]=max(0.,float((inequality@competitor-rhs).max()))+1e-8
    epsilon_upper=competitor[-1]
    a_upper=.5*r*r*np.minimum(rhs[:n]+epsilon_upper,rhs[n:2*n]+epsilon_upper)
    u_upper=(measure/3)*(rhs[2*n:]+epsilon_upper+a_upper/r**2)
    k_upper=np.minimum(thermal_weight*(rhs[:n]+epsilon_upper),
        thermal_weight/(1+3*w)*(rhs[2*n:]+epsilon_upper+a_upper/r**2))
    if w==0.:k_upper=np.minimum(k_upper,thermal_weight*(rhs[n:2*n]+epsilon_upper))
    lower=np.r_[np.zeros(n) if fixed is None else fixed,measure*floor,np.zeros(n),0.]
    upper=np.r_[a_upper if fixed is None else fixed,u_upper,k_upper,epsilon_upper]
    if np.any(upper<lower):raise ValueError('feasible competitor yielded inconsistent variable bounds')
    cost=np.zeros(3*n+1);cost[-1]=1.
    return dict(cost=cost,inequality=inequality,rhs=rhs,equality=equality,
        lower=lower,upper=upper,measure=measure,volume=volume,thermal_weight=thermal_weight,
        node_count=n,feasible_competitor=competitor,fixed_amplitude=fixed is not None,
        radiation_floor=floor,w=float(w))


def solve_thermal_exchange(rho, p, q, wall, radius, ell,
                           panel_mean_ell_squared, panel_mean_exchange_weight,
                           *, w, fixed_amplitude=None, radiation_floor=None, solver_threads=None):
    """Solve the sampled counted-reservoir gate with a reproducible dual bound."""
    if solver_threads is not None and (
            isinstance(solver_threads,(bool,np.bool_)) or
            not isinstance(solver_threads,(int,np.integer)) or solver_threads<1):
        raise ValueError('solver_threads must be a positive integer or None')
    problem=thermal_exchange_problem(rho,p,q,wall,radius,ell,
        panel_mean_ell_squared,panel_mean_exchange_weight,w=w,
        fixed_amplitude=fixed_amplitude,radiation_floor=radiation_floor)
    a=problem['inequality'];b=problem['rhs'];e=problem['equality'];cost=problem['cost']
    lower=problem['lower'];upper=problem['upper'];n=problem['node_count']
    options=dict(primal_feasibility_tolerance=1e-9,dual_feasibility_tolerance=1e-9,time_limit=90.)
    if solver_threads is not None:options['threads']=int(solver_threads)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore',message='Unrecognized options detected',category=OptimizeWarning)
        result=linprog(cost,A_ub=a,b_ub=b,A_eq=e,b_eq=np.zeros(n-1),
            bounds=np.column_stack([lower,upper]),method='highs-ds',options=options)
    if not result.success:raise RuntimeError('thermal exchange LP failed: '+result.message)
    x=result.x;y=np.minimum(result.ineqlin.marginals,0.);z=np.asarray(result.eqlin.marginals)
    reduced=cost-a.T@y-e.T@z
    box=float(np.maximum(reduced,0.)@lower+np.minimum(reduced,0.)@upper)
    raw=float(b@y);dual_lower=raw+box
    inequalities=a@x-b;equalities=e@x
    return dict(amplitude=x[:n],radiation_inventory=x[n:2*n],thermal_inventory=x[2*n:3*n],
        radiation_density=x[n:2*n]/problem['measure'],
        thermal_density=x[2*n:3*n]/problem['thermal_weight'],density_allowance=float(x[-1]),
        maximum_inequality_violation=float(max(0.,inequalities.max())),
        maximum_equality_residual=float(abs(equalities).max()),
        maximum_bound_violation=float(max(0.,(lower-x).max(),(x-upper).max())),
        dual_inequality=y,dual_equality=z,dual_reduced_cost=reduced,
        dual_raw_objective=raw,dual_box_correction=box,dual_lower_bound=dual_lower,
        primal_dual_gap=float(x[-1]-dual_lower),variable_lower_bounds=lower,
        variable_upper_bounds=upper,feasible_competitor=problem['feasible_competitor'],
        inequality_slack=-inequalities,equality_residual=equalities,
        fixed_amplitude=problem['fixed_amplitude'],additional_guide_floor_retained=False,
        solver_status=int(result.status),solver_iterations=int(result.nit))
