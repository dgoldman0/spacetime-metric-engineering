"""Local sampled relaxation of a passive phase and balanced radial radiation.

The phase and radiation may be reoptimized independently at each position.
Only energy exchange and the positive component cone are imposed. Source
rates, currents, spatial coherence, and constituent response remain free.
"""
from __future__ import annotations

import warnings

import numpy as np
from scipy.optimize import OptimizeWarning, linprog
from scipy.sparse import coo_matrix


def passive_phase_problem(density, radial, angular, wall, radius, ell,
                          panel_mean_ell_squared):
    """Build min epsilon for A>=0, U=(ell R)^2 W>=0 at one position.

For piecewise-linear A, panel conservation is
U[i+1]-U[i]+mean_panel(ell^2)*(A[i+1]-A[i])=0.
The three remaining cone facets are 2s<=rho-p+q,
2s<=rho-p-2q-3wall, and 3W-s<=rho+2p+q, with s=A/R^2.
A uniform density allowance epsilon is added to rho in all three facets.
"""
    rho,p,q,h,r,length=np.broadcast_arrays(density,radial,angular,wall,radius,ell)
    if rho.ndim!=1 or len(rho)<2 or np.any(r<=0) or np.any(length<=0):
        raise ValueError('one-dimensional positive-geometry history required')
    n=len(rho);average=np.asarray(panel_mean_ell_squared,dtype=float)
    if average.shape!=(n-1,) or np.any(average<=0):
        raise ValueError('one positive ell-squared average is required per panel')
    if not all(np.isfinite(a).all() for a in (rho,p,q,h,r,length,average)):
        raise ValueError('finite histories required')
    measure=(length*r)**2
    rhs=np.concatenate([rho-p+q,rho-p-2*q-3*h,rho+2*p+q])
    node=np.arange(n);rows=np.arange(3*n)
    ai=np.concatenate([2/r**2,2/r**2,-1/r**2])
    inequality=coo_matrix((np.r_[ai,3/measure,-np.ones(3*n)],
        (np.r_[rows,2*n+node,rows],np.r_[np.tile(node,3),n+node,np.full(3*n,2*n)])),
        shape=(3*n,2*n+1)).tocsr()
    panel=np.arange(n-1)
    equality=coo_matrix((np.r_[-average,average,-np.ones(n-1),np.ones(n-1)],
        (np.tile(panel,4),np.r_[panel,panel+1,n+panel,n+panel+1])),
        shape=(n-1,2*n+1)).tocsr()
    # A=U=0 with this allowance is an explicit feasible competitor. The
    # derived finite bounds preserve the optimum and support a dual check.
    epsilon_upper=max(0.,float(-rhs.min()))+1e-8
    amplitude_upper=.5*r*r*np.minimum(rhs[:n]+epsilon_upper,rhs[n:2*n]+epsilon_upper)
    radiation_upper=(measure/3)*(rhs[2*n:]+epsilon_upper+amplitude_upper/r**2)
    upper=np.r_[amplitude_upper,radiation_upper,epsilon_upper]
    if np.any(upper<0):raise ValueError('inconsistent feasible-competitor bounds')
    cost=np.zeros(2*n+1);cost[-1]=1.
    return dict(cost=cost,inequality=inequality,rhs=rhs,equality=equality,
                upper=upper,measure=measure,node_count=n)


def solve_passive_phase(density, radial, angular, wall, radius, ell,
                        panel_mean_ell_squared):
    """Solve the sampled LP and retain a checkable bounded-domain dual witness."""
    problem=passive_phase_problem(density,radial,angular,wall,radius,ell,
                                 panel_mean_ell_squared)
    a=problem['inequality'];b=problem['rhs'];e=problem['equality']
    upper=problem['upper'];cost=problem['cost'];n=problem['node_count']
    # The HiGHS thread limit is passed through by scipy. Every independent
    # location can be scheduled by the caller without solver oversubscription.
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore',message='Unrecognized options detected',category=OptimizeWarning)
        result=linprog(cost,A_ub=a,b_ub=b,A_eq=e,b_eq=np.zeros(n-1),
            bounds=np.column_stack([np.zeros_like(upper),upper]),method='highs-ds',
            options=dict(threads=1,primal_feasibility_tolerance=1e-9,
                         dual_feasibility_tolerance=1e-9,time_limit=90.))
    if not result.success:
        raise RuntimeError('passive phase LP failed: '+result.message)
    x=result.x;y=np.minimum(result.ineqlin.marginals,0.)
    z=np.asarray(result.eqlin.marginals)
    reduced=cost-a.T@y-e.T@z
    correction=float(np.minimum(reduced,0.)@upper)
    dual_raw=float(b@y);dual_lower=dual_raw+correction
    # For y<=0 and any z, c.x >= b.y + sum min(c-A^T y-E^T z,0)*upper
    # throughout the bounded feasible set. Floating arithmetic is reported;
    # this is an independently reproducible LP witness, not interval proof.
    inequalities=a@x-b;equalities=e@x
    return dict(amplitude=x[:n],radiation_inventory=x[n:2*n],
        radiation_density=x[n:2*n]/problem['measure'],density_allowance=float(x[-1]),
        maximum_inequality_violation=float(max(0.,inequalities.max())),
        maximum_equality_residual=float(abs(equalities).max()),
        maximum_bound_violation=float(max(0.,(-x).max(),(x-upper).max())),
        dual_inequality=y,dual_equality=z,dual_reduced_cost=reduced,
        dual_raw_objective=dual_raw,dual_box_correction=correction,
        dual_lower_bound=dual_lower,primal_dual_gap=float(x[-1]-dual_lower),
        variable_upper_bounds=upper,inequality_slack=-inequalities,
        equality_residual=equalities,solver_status=int(result.status),
        solver_iterations=int(result.nit))
