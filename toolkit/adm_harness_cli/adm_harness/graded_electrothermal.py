"""Conservation screen for a graded radial capacitor and local energy buffers.

Prescribed coordinate-fixed worldlines are an inverse construction target.
The pressure-free buffer is an optimistic effective store. Charge-carrier
inertia, confinement, terminal electrodes, and feedback stability require
separate physical completion. Optional finite collars expose force ports.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

from .active_transfer_reservoir import divergence_projections


def fixed_kinematics(g, alpha_t, beta_t):
    v = g.b*g.beta/g.alpha
    if np.any(abs(v) >= 1):
        raise ValueError('coordinate-fixed worldlines must be timelike')
    gamma = 1/np.sqrt(1-v*v)
    lapse = g.alpha/gamma
    vt = v*(g.logb_t-alpha_t/g.alpha)+g.b*beta_t/g.alpha
    acceleration = gamma*(gamma**2*vt/g.alpha+g.alpha_x/(g.alpha*g.b)-v*g.k_l)
    angular_gradient = g.logr_x/(gamma*g.b)+gamma*v*g.logr_t/g.alpha
    return v, gamma, lapse, acceleration, angular_gradient


def coefficients(model, times, positions):
    result = {key: [] for key in ('c', 'd', 'a', 'source', 'force', 'v', 'gamma',
                                  'b', 'radius', 'alpha', 'lapse', 'acceleration',
                                  'angular_gradient', 'power', 'normal_force')}
    for t in times:
        g = model.metric(float(t), positions)
        if hasattr(model, 'metric_splines'):
            tt = np.full_like(positions, t)
            alpha_t = g.alpha*model.metric_splines[0].ev(tt, positions, dx=1)
            beta_t = model.metric_splines[1].ev(tt, positions, dx=1)
        else:
            h = 1e-5
            gp, gm = model.metric(float(t+h), positions), model.metric(float(t-h), positions)
            alpha_t, beta_t = (gp.alpha-gm.alpha)/(2*h), (gp.beta-gm.beta)/(2*h)
        v, gamma, lapse, acceleration, angular_gradient = fixed_kinematics(g, alpha_t, beta_t)
        power, force = divergence_projections(g, *model.medium(float(t), positions))
        values = (gamma*g.b/g.radius**2, v*g.radius**2/lapse, g.radius**2*acceleration,
                  -g.alpha*gamma*g.volume*(power-v*force), g.b*g.radius**4*force,
                  v, gamma, g.b, g.radius, g.alpha, lapse, acceleration, angular_gradient,
                  power, force)
        for key, value in zip(result, values):
            result[key].append(value)
    return {key: np.asarray(value) for key, value in result.items()}


def smooth_spline_scalars(model, time, position):
    """C2 temporal continuation for a curvature stencil at a table boundary.

The tabulated core is unblended. RectBivariateSpline clamps values outside
its time domain while still returning endpoint derivatives; a quadratic jet
extension preserves those derivatives for this diagnostic stencil.
"""
    if abs(position) >= 5:
        raise ValueError('temporal jet continuation applies to the unblended core')
    boundary = np.clip(time, model.t_min, model.t_max)
    delta = time-boundary
    values = []
    for spline in model.metric_splines:
        value = float(spline.ev(boundary, position))
        if delta:
            value += delta*float(spline.ev(boundary, position, dx=1))
            value += delta**2/2*float(spline.ev(boundary, position, dx=2))
        values.append(value)
    return dict(alpha=np.exp(values[0]), beta=values[1],
                gamma_ll=np.exp(2*values[2]), gamma_omega=np.exp(2*values[3]))


def moments(mass_energy, electric_flux_energy, c):
    """M=Gamma B R^2 w; H=R^4 u_E=Q^2/2; orthonormal moments."""
    w = mass_energy/(c['gamma']*c['b']*c['radius']**2)
    electric = electric_flux_energy/c['radius']**4
    moving = w*c['gamma']**2
    return np.array([moving+electric, moving*c['v']**2-electric,
                     moving*c['v'], electric])


def maximum_null(stress):
    """Exact maximum over the unit sphere of null directions, k^0=1."""
    rho, radial, current, angular = np.asarray(stress)
    aa, bb, cc = radial-angular, -2*current, rho+angular
    vertex = np.zeros_like(aa)
    np.divide(-bb, 2*aa, out=vertex, where=aa < 0)
    vertex = np.clip(vertex, -1, 1)
    values = np.array([cc+aa-bb, cc+aa+bb, cc+aa*vertex**2+bb*vertex])
    candidates = np.array([-np.ones_like(aa), np.ones_like(aa), vertex])
    index = values.argmax(axis=0)
    return np.take_along_axis(values, index[None], axis=0)[0], np.take_along_axis(candidates, index[None], axis=0)[0]


def hoop_force_cone(acceleration, angular_gradient, required_force):
    """Necessary local condition for a co-moving radial-pressure-free collar.

Its rest-frame radial divergence is w*a-2*p_t*s(ln R), with w>=|p_t|.
This screen grants an arbitrary positive density and arbitrary allowed hoop
stress. Other stress channels and separate momentum routes remain open.
"""
    low = acceleration-2*abs(angular_gradient)
    high = acceleration+2*abs(angular_gradient)
    allowed = ((required_force >= 0) & (high > 0)) | ((required_force <= 0) & (low < 0)) | (required_force == 0)
    return allowed, low, high


def contact_profiles(positions, centers, width):
    """C2 coordinate profiles with unit discrete integral, independent of time."""
    midpoint = .5*(positions[1:]+positions[:-1])
    values = []
    for center in centers:
        z = 2*(midpoint-center)/width
        profile = np.maximum(0., 1-z*z)**3
        normalization = np.dot(profile, np.diff(positions))
        if normalization <= 0:
            raise ValueError('contact band requires resolved interior quadrature points')
        values.append(profile/normalization)
    return np.array(values).reshape(len(centers), len(midpoint))


class SparseRows:
    def __init__(self, columns):
        self.columns = columns
        self.rows, self.cols, self.values, self.rhs, self.scales = [], [], [], [], []

    def add(self, items, rhs=0.):
        scale = max(1e-15, abs(rhs), *(abs(value) for _, value in items))
        row = len(self.rhs)
        for col, value in items:
            self.rows.append(row); self.cols.append(col); self.values.append(value/scale)
        self.rhs.append(rhs/scale); self.scales.append(scale)

    def matrix(self):
        return coo_matrix((self.values, (self.rows, self.cols)),
                          shape=(len(self.rhs), self.columns)).tocsr()


def solve_linear_program(cost, *, method, deadline, **kwargs):
    options = dict(time_limit=deadline, primal_feasibility_tolerance=1e-9,
                   dual_feasibility_tolerance=1e-9)
    return linprog(cost, method=method, options=options, **kwargs)


def solve_schedule(times, positions, c, number, initial_energy, *, ports=(), port_width=.1,
                   passive=True, flux_floor=1e-8, deadline=120., smooth_contacts=False,
                   conductivity_ceiling=None, primary_solver='highs'):
    """Minimax supplied null stress, followed by minimum time-integrated energy.

Backward Euler energy balance and spatial finite-volume force balance retain
all active metric coefficients. A refinement comparison controls truncation.
The initial force row uses the first interval's charge rate. Optional collars
retain energy balance and expose the omitted mechanical force equation.
"""
    t, x = np.asarray(times), np.asarray(positions)
    nt, nx = len(t), len(x)
    if nt < 3 or nx < 3 or np.any(np.diff(t) <= 0) or np.any(np.diff(x) <= 0):
        raise ValueError('ordered grids of at least three points required')
    if np.any(number <= 0) or np.any(initial_energy < number) or flux_floor <= 0:
        raise ValueError('positive reference, admissible initial energy, and flux floor required')
    if conductivity_ceiling is not None and conductivity_ceiling <= 0:
        raise ValueError('positive proper conductivity ceiling required')
    if primary_solver not in ('highs', 'highs-ipm'):
        raise ValueError('registered HiGHS simplex or interior-point method required')
    amplitudes = nt*len(ports) if smooth_contacts else 0
    size, peak = nt*nx, 2*nt*nx+amplitudes
    eq, ub = SparseRows(peak+1), SparseRows(peak+1)
    profiles = contact_profiles(x, ports, port_width)
    midpoint = .5*(x[1:]+x[:-1])
    port_mask = np.zeros(nx-1, dtype=bool)
    for center in ports:
        port_mask |= abs(midpoint-center) < port_width/2-1e-10
    for j in range(nx):
        eq.add([(j, 1.)], float(initial_energy[j]))
    for i in range(1, nt):
        dt = t[i]-t[i-1]
        for j in range(nx):
            k = i*nx+j
            coeff = c['c'][i, j]
            eq.add([(k, 1/dt), (k-nx, -1/dt),
                    (size+k, coeff/dt), (size+k-nx, -coeff/dt)], c['source'][i, j])
            if passive:
                ub.add([(size+k, 1.), (size+k-nx, -1.)])
            if conductivity_ceiling is not None:
                decay = np.exp(-conductivity_ceiling*(c['lapse'][i, j]+c['lapse'][i-1, j])*dt)
                ub.add([(size+k-nx, decay), (size+k, -1.)])
    for i in range(nt):
        dt = t[max(1, i)]-t[max(0, i-1)]
        for j, dx in enumerate(np.diff(x)):
            if port_mask[j] and not smooth_contacts:
                continue
            items = [(size+i*nx+j+1, 1/dx), (size+i*nx+j, -1/dx)]
            rhs = .5*(c['force'][i, j]+c['force'][i, j+1])
            for jj in (j, j+1):
                k = i*nx+jj
                items.append((k, -.5*c['a'][i, jj]))
                if i:
                    value = .5*c['d'][i, jj]/dt
                    items.extend([(k, -value), (k-nx, value)])
                else:
                    value = .5*c['d'][0, jj]*c['c'][0, jj]/dt
                    items.extend([(size+nx+jj, value), (size+jj, -value)])
                    rhs += .5*c['d'][0, jj]*c['source'][0, jj]
            if smooth_contacts:
                radius = .5*(c['radius'][i, j]+c['radius'][i, j+1])
                for k in range(len(ports)):
                    items.append((2*size+i*len(ports)+k, radius**2*profiles[k, j]/(4*np.pi)))
            eq.add(items, rhs)

    def null_row(i, j, z):
        k = i*nx+j
        wm = c['gamma'][i, j]/(c['b'][i, j]*c['radius'][i, j]**2)*(1-c['v'][i, j]*z)**2
        wh = 2*(1-z*z)/c['radius'][i, j]**4
        ub.add([(k, wm), (size+k, wh), (peak, -1.)])

    for i in range(nt):
        for j in range(nx):
            for z in np.linspace(-1, 1, 9):
                null_row(i, j, z)
    bounds = [(float(number[k % nx]), None) for k in range(size)]
    bounds += [(flux_floor, None)]*size+[(None, None)]*amplitudes+[(0., None)]
    cost = np.zeros(peak+1); cost[peak] = 1.
    matrix = eq.matrix()
    last_result = None
    for iteration in range(7):
        result = solve_linear_program(cost, A_ub=ub.matrix(), b_ub=ub.rhs, A_eq=matrix, b_eq=eq.rhs,
                                      bounds=bounds, method=primary_solver, deadline=deadline)
        if not result.success:
            return dict(success=False, message=result.message)
        m = result.x[:size].reshape(nt, nx)
        h = result.x[size:2*size].reshape(nt, nx)
        real_peak, directions = maximum_null(moments(m, h, c))
        violations = np.argwhere(real_peak > result.x[peak]+2e-8*max(1., result.x[peak]))
        if not len(violations):
            last_result = result
            break
        for i, j in violations:
            null_row(i, j, directions[i, j])
    if last_result is None:
        return dict(success=False, message='angular cutting-plane tolerance unresolved')
    optimum = float(result.x[peak])
    # A secondary energy objective removes irrelevant stored energy at equal peak.
    dx = np.r_[np.diff(x)[0], np.diff(x)[:-1]+np.diff(x)[1:], np.diff(x)[-1]]/2
    dt = np.r_[np.diff(t)[0], np.diff(t)[:-1]+np.diff(t)[1:], np.diff(t)[-1]]/2
    weight = dt[:, None]*dx[None, :]
    cost[:] = 0.
    cost[:size] = (weight*c['gamma']).ravel()
    cost[size:2*size] = (weight*c['b']/c['radius']**2).ravel()
    cost /= cost.max()
    peak_allowance = 1e-6*max(1., optimum)
    bounds[-1] = (0., optimum+peak_allowance)
    secondary = solve_linear_program(cost, A_ub=ub.matrix(), b_ub=ub.rhs, A_eq=matrix, b_eq=eq.rhs,
                                     bounds=bounds, method='highs-ipm', deadline=min(deadline, 90.))
    # Preserve the verified primary optimum if the optional tie-break fails.
    secondary_used = bool(secondary.success)
    if secondary_used:
        sm = secondary.x[:size].reshape(nt, nx)
        sh = secondary.x[size:2*size].reshape(nt, nx)
        secondary_used = bool(maximum_null(moments(sm, sh, c))[0].max() <= optimum+peak_allowance+2e-8*max(1., optimum))
    vector = secondary.x if secondary_used else result.x
    return dict(success=True, mass_energy=vector[:size].reshape(nt, nx),
                flux_energy=vector[size:2*size].reshape(nt, nx), port_mask=port_mask,
                contact_amplitudes=vector[2*size:peak].reshape(nt, len(ports)) if smooth_contacts else np.zeros((nt, 0)),
                optimal_supplied_null_peak=optimum, angle_iterations=iteration+1,
                secondary_energy_optimization_used=secondary_used, secondary_status=secondary.message,
                secondary_peak_allowance=peak_allowance,
                primary_solver=primary_solver, interior_point_crossover=True,
                normalized_equality_residual=float(abs(matrix@vector-eq.rhs).max()),
                raw_equality_residual=float((abs(matrix@vector-eq.rhs)*eq.scales).max()),
                inequality_violation=float(max(0., np.max(ub.matrix()@vector-ub.rhs))),
                primary_dual_gap=float(abs(result.fun-(np.dot(result.eqlin.marginals, eq.rhs)
                    +np.dot(result.ineqlin.marginals, ub.rhs)
                    +np.dot(result.lower.marginals, [a if a is not None else 0. for a, _ in bounds])))))


def force_ports(times, positions, c, m, h):
    """Covariant force that a separate support must give the screened assembly.

The opposite divergence belongs to the support's own counted tensor. Normal
power equals v*normal force for these fixed-worldline mechanical contacts.
"""
    mt = np.empty_like(m)
    mt[1:] = np.diff(m, axis=0)/np.diff(times)[:, None]
    ht0 = (h[1]-h[0])/(times[1]-times[0])
    mt[0] = c['source'][0]-c['c'][0]*ht0
    drive = c['d']*mt+c['a']*m+c['force']
    residual = np.diff(h, axis=1)/np.diff(positions)[None, :]-.5*(drive[:, :-1]+drive[:, 1:])
    b = .5*(c['b'][:, :-1]+c['b'][:, 1:])
    radius = .5*(c['radius'][:, :-1]+c['radius'][:, 1:])
    gamma = .5*(c['gamma'][:, :-1]+c['gamma'][:, 1:])
    normal = -residual/(b*radius**4)
    return normal, normal/gamma, residual
