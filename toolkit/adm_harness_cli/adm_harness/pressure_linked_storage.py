"""Inverse conservation test for a connected thermal fluid and radial field.

The fluid carries conserved rest mass and thermal energy with rho=n+kappa*p.
Its pressure transmits the field segments' reactions across the full patch.
Worldlines remain prescribed; electrical carrier dynamics and stability are
separate gates. Every interior force equation is retained. End tractions are
either exposed explicitly or set to zero in a stronger closure control.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import cumulative_trapezoid

from .graded_electrothermal import (
    SparseRows, coefficients, maximum_null, solve_linear_program,
)


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
                             deadline=120., secondary_deadline=45., heat_floor=0.):
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
    for iteration in range(8):
        result = solve_linear_program(cost, method='highs-ipm', deadline=deadline,
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
        secondary = solve_linear_program(cost, method='highs-ipm', deadline=secondary_deadline,
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
