"""Inverse conservation test for a connected thermal fluid and radial field.

The fluid carries conserved rest mass and thermal energy with rho=n+kappa*p.
Its pressure transmits the field segments' reactions across the full patch.
Worldlines remain prescribed; electrical carrier dynamics and stability are
separate gates. Every interior force equation is retained. End tractions are
either exposed explicitly or set to zero in a stronger closure control.
"""
from __future__ import annotations

import warnings

import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.optimize import linprog, OptimizeWarning

from .graded_electrothermal import (
    SparseRows, coefficients, maximum_null,
)


def retained_coefficient_program(cost, *, method, deadline, presolve=True, **kwargs):
    """Keep small shift coefficients multiplying large volume-weighted stores.

HiGHS defaults to deleting matrix entries at or below 1e-9. The active metric
can produce small coefficients with measurable products. Its supported 1e-12
threshold preserves these terms; full unmodified-matrix residuals are audited.
"""
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='Unrecognized options detected.*small_matrix_value', category=OptimizeWarning)
        return linprog(cost, method=method,
            options=dict(time_limit=deadline, presolve=presolve, small_matrix_value=1e-12,
                         primal_feasibility_tolerance=1e-9, dual_feasibility_tolerance=1e-9), **kwargs)


def minimum_positive_pressure(x, coefficient, drive):
    """Minimum nonnegative solution of p_x+coefficient*p=drive.

Both end pressures are free and remain reported loads. Adding any homogeneous
solution increases pressure everywhere. The minimum is therefore obtained by
raising the integrating-factor primitive until its minimum reaches zero.
"""
    x, coefficient, drive = map(np.asarray, (x, coefficient, drive))
    if len(x) < 3 or np.any(np.diff(x) <= 0):
        raise ValueError('ordered resolved pressure path required')
    integral = cumulative_trapezoid(coefficient, x, initial=0.)
    if abs(integral).max() > 500:
        raise ArithmeticError('pressure integrating factor exceeds bounded range')
    primitive = cumulative_trapezoid(np.exp(integral)*drive, x, initial=0.)
    return np.exp(-integral)*(primitive-primitive.min()), integral


def balanced_end_witness(x, c, number, log_radius_x, conductivity_ceiling=1.):
    """Integrated force/energy obstruction, retaining the shift and U_t term.

For rho=n+3p, q=p-u_E and r=-H_t/H in [0,2*sigma*N_lapse],
q_x+C*q+[C-4*(ln R)_x+b*D*r]*u_E=drive, where
b=4*v/(3*N_lapse*R^2), C=4*Gamma*B*a-b*lambda*D.
If the last coefficient is positive for every allowed r and the weighted
drive integral is negative, q=0 at both ends is impossible for u_E>=0.
"""
    if conductivity_ceiling <= 0:
        raise ValueError('positive finite discharge bound required')
    d = c['rest_volume']
    b = 4*c['v']/(3*c['lapse']*c['radius']**2)
    coefficient = 4*c['gamma']*c['b']*c['acceleration']-b*c['volume_rate']*d
    drive = -c['b']*c['normal_force']-c['gamma']*c['b']*c['acceleration']*number/d-b*c['source']
    field_min = coefficient-4*log_radius_x+np.minimum(0., b*d*2*conductivity_ceiling*c['lapse'])
    weight = np.exp(cumulative_trapezoid(coefficient, x, initial=0.))
    return dict(weight=weight, coefficient=coefficient, drive=drive, field_min=field_min,
                weighted_drive_integral=float(np.trapezoid(weight*drive, x)),
                minimum_field_coefficient=float(field_min.min()))


def fluid_coefficients(model, times, positions):
    c = coefficients(model, times, positions)
    expansion_rate = []
    for i, time in enumerate(times):
        g = model.metric(float(time), positions)
        if hasattr(model, 'metric_splines'):
            tt = np.full_like(positions, time)
            alpha_t = g.alpha*model.metric_splines[0].ev(tt, positions, dx=1)
            beta_t = model.metric_splines[1].ev(tt, positions, dx=1)
        else:
            step = 1e-5
            gp, gm = model.metric(float(time+step), positions), model.metric(float(time-step), positions)
            alpha_t = (gp.alpha-gm.alpha)/(2*step)
            beta_t = (gp.beta-gm.beta)/(2*step)
        v = c['v'][i]
        vt = v*(g.logb_t-alpha_t/g.alpha)+g.b*beta_t/g.alpha
        expansion_rate.append(g.logb_t+2*g.logr_t+c['gamma'][i]**2*v*vt)
    c['volume_rate'] = np.asarray(expansion_rate)  # d_t ln(Gamma B R^2)
    c['rest_volume'] = c['gamma']*c['b']*c['radius']**2
    return c


def fluid_moments(thermal, field, number, c, kappa=3.):
    """U=D*kappa*p; H=R^4*u_E; N=D*n with D=Gamma*B*R^2."""
    d = c['rest_volume']
    pressure = thermal/(kappa*d)
    enthalpy = number/d+(kappa+1)*pressure
    moving = enthalpy*c['gamma']**2
    electric = field/c['radius']**4
    return np.array([moving-pressure+electric, moving*c['v']**2+pressure-electric,
                     moving*c['v'], pressure+electric])


def reduced_divergence(c, number, thermal, thermal_t, pressure_x, field_t, field_x, kappa=3.):
    """Rest-frame full tensor divergence from independent scalar fluid laws."""
    d, lapse, gamma, b = (c[key] for key in ('rest_volume', 'lapse', 'gamma', 'b'))
    pressure = thermal/(kappa*d)
    pressure_t = (thermal_t-c['volume_rate']*thermal)/(kappa*d)
    energy = (thermal_t+c['volume_rate']*thermal/kappa)/(lapse*d)
    energy += field_t/(lapse*c['radius']**4)
    force = (number/d+(kappa+1)*pressure)*c['acceleration']
    force += pressure_x/(gamma*b)+c['v']*pressure_t/lapse
    force -= (field_x/(gamma*b)+c['v']*field_t/lapse)/c['radius']**4
    return energy, force


def solve_connected_schedule(times, positions, c, number, initial_thermal, *,
                             kappa=3., initial_mode='fixed', ends='exposed',
                             conductivity_ceiling=1., passive=True, flux_floor=1e-8,
                             deadline=120., secondary_deadline=45., heat_floor=0.,
                             charging_policy='unrestricted', primary_solver='highs-ipm',
                             presolve=True, inspect_problem=False):
    """Minimize total fluid+field peak null stress under joint conservation.

U_t + (d_t ln D)*U/kappa + c*H_t = S,
H_x - R^4*p_x - a*[N+(1+1/kappa)*U] - d*(1+1/kappa)*U_t = F.

The endpoint tensor and metric coefficients retain time and shift terms.
First-order implicit time and midpoint spatial equations are refined by the
runner. The initial force equation uses a forward thermal derivative.
"""
    t, x, number, initial_thermal = map(np.asarray, (times, positions, number, initial_thermal))
    nt, nx = len(t), len(x)
    if nt < 3 or nx < 3 or np.any(np.diff(t) <= 0) or np.any(np.diff(x) <= 0):
        raise ValueError('ordered time and space grids with at least three points required')
    if kappa < 1 or np.any(number <= 0) or np.any(initial_thermal < 0) or heat_floor < 0:
        raise ValueError('causal fluid, positive rest mass, and nonnegative heat required')
    if initial_mode not in ('fixed', 'prepared') or ends not in ('exposed', 'balanced'):
        raise ValueError('registered initial preparation and end-traction cases required')
    if conductivity_ceiling is not None and conductivity_ceiling <= 0:
        raise ValueError('positive discharge rate required')
    if flux_floor < 0:
        raise ValueError('nonnegative field floor required')
    if charging_policy not in ('unrestricted', 'endpoint_work', 'heat_engine'):
        raise ValueError('registered local charging-energy policy required')
    size, peak = nt*nx, 2*nt*nx
    eq, ub = SparseRows(peak+1), SparseRows(peak+1)
    for j in range(nx):
        if initial_mode == 'fixed':
            eq.add([(j, 1.)], initial_thermal[j])
    for i in range(1, nt):
        dt = t[i]-t[i-1]
        for j in range(nx):
            k = i*nx+j
            eq.add([(k, 1/dt+c['volume_rate'][i, j]/kappa), (k-nx, -1/dt),
                    (size+k, c['c'][i, j]/dt), (size+k-nx, -c['c'][i, j]/dt)], c['source'][i, j])
            if passive:
                ub.add([(size+k, 1.), (size+k-nx, -1.)])
            if conductivity_ceiling is not None:
                decay = np.exp(-conductivity_ceiling*(c['lapse'][i, j]+c['lapse'][i-1, j])*dt)
                ub.add([(size+k-nx, decay), (size+k, -1.)])
                if not passive:
                    ub.add([(size+k, decay), (size+k-nx, -1.)])
            # Incoming endpoint energy is generously available as coherent
            # work. A heat engine can additionally extract fluid heat only
            # where the endpoint has a net outgoing-energy (dump) port.
            if charging_policy == 'endpoint_work' or (charging_policy == 'heat_engine' and c['source'][i, j] >= 0):
                supplied_work = max(0., c['source'][i, j])/c['c'][i, j]
                ub.add([(size+k, 1/dt), (size+k-nx, -1/dt)], supplied_work)
    enthalpy_factor = 1+1/kappa
    for i in range(nt):
        i0, i1 = (i-1, i) if i else (0, 1)
        dt = t[i1]-t[i0]
        for j, dx in enumerate(np.diff(x)):
            radius4 = (.5*(c['radius'][i, j]+c['radius'][i, j+1]))**4
            items = [(size+i*nx+j+1, 1/dx), (size+i*nx+j, -1/dx),
                     (i*nx+j+1, -radius4/(dx*kappa*c['rest_volume'][i, j+1])),
                     (i*nx+j, radius4/(dx*kappa*c['rest_volume'][i, j]))]
            rhs = .5*(c['force'][i, j]+c['force'][i, j+1])
            for jj in (j, j+1):
                rhs += .5*c['a'][i, jj]*number[jj]
                items.append((i*nx+jj, -.5*enthalpy_factor*c['a'][i, jj]))
                value = .5*enthalpy_factor*c['d'][i, jj]/dt
                items.extend([(i1*nx+jj, -value), (i0*nx+jj, value)])
            eq.add(items, rhs)
        if ends == 'balanced':
            for j in (0, nx-1):
                k = i*nx+j
                eq.add([(k, 1/(kappa*c['rest_volume'][i, j])), (size+k, -1/c['radius'][i, j]**4)])

    def null_row(i, j, z):
        k = i*nx+j
        factor = c['gamma'][i, j]**2*(1-c['v'][i, j]*z)**2/c['rest_volume'][i, j]
        ub.add([(k, enthalpy_factor*factor), (size+k, 2*(1-z*z)/c['radius'][i, j]**4),
                (peak, -1.)], -number[j]*factor)

    for i in range(nt):
        for j in range(nx):
            for z in np.linspace(-1, 1, 7):
                null_row(i, j, z)
    bounds = []
    for i in range(nt):
        for j in range(nx):
            lower = number[j]*heat_floor
            if i == 0 and initial_mode == 'prepared':
                lower = max(lower, initial_thermal[j])
            bounds.append((float(lower), None))
    bounds += [(flux_floor, None)]*size+[(0., None)]
    cost = np.zeros(peak+1); cost[-1] = 1.
    equality = eq.matrix()
    if inspect_problem:
        return dict(A_eq=equality, b_eq=np.asarray(eq.rhs), A_ub=ub.matrix(), b_ub=np.asarray(ub.rhs),
                    bounds=bounds, cost=cost, row_scales=np.asarray(eq.scales))
    for iteration in range(8):
        result = retained_coefficient_program(cost, method=primary_solver, deadline=deadline, presolve=presolve,
            A_eq=equality, b_eq=eq.rhs, A_ub=ub.matrix(), b_ub=ub.rhs, bounds=bounds)
        if not result.success:
            return dict(success=False, status=int(result.status), message=result.message,
                        variables=peak+1, equalities=len(eq.rhs), inequalities=len(ub.rhs))
        u, h = (result.x[offset:offset+size].reshape(nt, nx) for offset in (0, size))
        real, z = maximum_null(fluid_moments(u, h, number, c, kappa))
        violations = np.argwhere(real > result.x[peak]+2e-8*max(1., result.x[peak]))
        if not len(violations):
            break
        for i, j in violations:
            null_row(i, j, z[i, j])
    else:
        return dict(success=False, status=-1, message='angular cutting planes unresolved')
    primary = result
    optimum = float(result.x[peak])
    peak_allowance = 1e-6*max(1., optimum)
    secondary_used, secondary_message = False, 'disabled'
    if secondary_deadline > 0:
        dx = np.r_[np.diff(x)[0], np.diff(x)[:-1]+np.diff(x)[1:], np.diff(x)[-1]]/2
        dt = np.r_[np.diff(t)[0], np.diff(t)[:-1]+np.diff(t)[1:], np.diff(t)[-1]]/2
        weight = dt[:, None]*dx[None, :]
        cost[:] = 0.
        cost[:size] = (weight*(enthalpy_factor*c['gamma']-1/(kappa*c['gamma']))).ravel()
        cost[size:2*size] = (weight*c['b']/c['radius']**2).ravel()
        cost /= cost.max()
        bounds[-1] = (0., optimum+peak_allowance)
        secondary = retained_coefficient_program(cost, method='highs-ipm', deadline=secondary_deadline,
            A_eq=equality, b_eq=eq.rhs, A_ub=ub.matrix(), b_ub=ub.rhs, bounds=bounds)
        secondary_message = secondary.message
        if secondary.success:
            su, sh = (secondary.x[offset:offset+size].reshape(nt, nx) for offset in (0, size))
            real, _ = maximum_null(fluid_moments(su, sh, number, c, kappa))
            if real.max() <= optimum+peak_allowance+2e-8*max(1., optimum):
                result, u, h, secondary_used = secondary, su, sh, True
            else:
                secondary_message += '; retained primary after angular audit'
    eq_residual = equality@result.x-np.asarray(eq.rhs)
    ub_residual = ub.matrix()@result.x-np.asarray(ub.rhs)
    dual_objective = np.dot(primary.eqlin.marginals, eq.rhs)+np.dot(primary.ineqlin.marginals, ub.rhs)
    dual_objective += sum(primary.lower.marginals[k]*bound[0] for k, bound in enumerate(bounds) if bound[0] is not None)
    return dict(success=True, thermal=u, flux_energy=h, optimal_supplied_null_peak=optimum,
                peak_allowance=peak_allowance, secondary_energy_optimization_succeeded=secondary_used,
                secondary_message=secondary_message, angular_rounds=iteration+1,
                primary_dual_gap=float(abs(optimum-dual_objective)),
                maximum_scaled_equality_residual=float(abs(eq_residual).max()),
                maximum_raw_equality_residual=float((abs(eq_residual)*eq.scales).max()),
                maximum_inequality_violation=float(max(0., ub_residual.max())),
                variables=peak+1, equalities=len(eq.rhs), inequalities=len(ub.rhs))
