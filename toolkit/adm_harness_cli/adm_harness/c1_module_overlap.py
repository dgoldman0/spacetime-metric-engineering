"""Finite electrostatic source overlap and separate static material supports.

The metric is ds²=-A²dt²+B²dx²+R²dOmega², with c=epsilon_0=G=1.
Q=R²E is flux per solid angle. Two charge populations produce Q1+Q2=Q;
their shared Maxwell tensor includes the cross term. Material supports obey
the static radial equation and rho >= |pr|, |pt| on their own finite domains.
This is a fixed-background tensor construction, with constitutive evolution
and the remaining Einstein source evaluated separately.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, eye, hstack, vstack


def smooth_step(value):
    """C2 quintic step and derivative with respect to its argument."""
    raw = np.asarray(value, dtype=float)
    if not np.isfinite(raw).all():
        raise ValueError("finite step arguments required")
    z = np.clip(raw, 0., 1.)
    return z**3*(10.+z*(-15.+6.*z)), 30.*z*z*(1.-z)**2


def electric_pair(coordinate, radius, radial_scale, *, amplitude,
                  overlap, plateau=1., extent=3.):
    """Actual radial Maxwell field and Lorentz loads of two neutral sources.

    Each Qi vanishes beyond its finite source domain. In the overlap the
    Maxwell fields share the same gauge field, so energy is computed from
    the summed amplitude. Positive Lorentz force points toward increasing x.
    """
    x, r, b = np.broadcast_arrays(*[np.asarray(v, dtype=float)
                                  for v in (coordinate, radius, radial_scale)])
    a, c = map(float, overlap)
    if (not all(np.isfinite(v).all() for v in (x, r, b)) or
            not np.isfinite([amplitude, a, c, plateau, extent]).all() or
            np.any(r <= 0) or np.any(b <= 0) or amplitude <= 0 or
            not 0 <= plateau < extent or not -extent < a < c < extent):
        raise ValueError("positive finite geometry and interior overlap required")
    taper, taper_d = smooth_step((abs(x)-plateau)/(extent-plateau))
    q = amplitude*(1.-taper)
    qx = -amplitude*taper_d*np.sign(x)/(extent-plateau)
    right, right_x = smooth_step((x-a)/(c-a))
    right_x = right_x/(c-a)
    weights = np.stack((1.-right, right), axis=-1)
    wx = np.stack((-right_x, right_x), axis=-1)
    qi = weights*q[..., None]
    qix = weights*qx[..., None]+wx*q[..., None]
    charge = qix/(b*r*r)[..., None]
    field = q/(r*r)
    self_energy = qi**2/(2.*r[..., None]**4)
    cross_energy = qi[..., 0]*qi[..., 1]/r**4
    energy = field**2/2.
    force = charge*field[..., None]
    return dict(flux=q, flux_x=qx, module_flux=qi, module_flux_x=qix,
                charge_density=charge, total_charge_density=qx/(b*r*r),
                field=field, energy=energy, self_energy=self_energy,
                cross_energy=cross_energy, lorentz_force=force,
                total_lorentz_force=q*qx/(b*r**4))


def angular_support_floor(force, acceleration, radial_log_gradient,
                          *, stress_fraction=1.):
    """Necessary local floor for zero-radial-pressure static supports.

    F=a*rho-2*(R'/R)*pt with |pt| <= k*rho. A failed sign cone excludes
    this local contact specialization; radial stress transmission is separate.
    """
    f, a, r = np.broadcast_arrays(*[np.asarray(v, dtype=float) for v in
                                   (force, acceleration, radial_log_gradient)])
    if (not all(np.isfinite(v).all() for v in (f, a, r)) or
            not np.isfinite(stress_fraction) or not 0 < stress_fraction <= 1):
        raise ValueError("finite force/geometry and stress fraction in (0,1] required")
    coefficient = a+np.sign(f)*2.*stress_fraction*abs(r)
    feasible = (f == 0) | (f*coefficient > 0)
    density = np.full(f.shape, np.nan)
    density[f == 0] = 0.
    np.divide(f, coefficient, out=density, where=(f != 0) & feasible)
    return dict(feasible=feasible, density=density,
                lower=a-2.*stress_fraction*abs(r),
                upper=a+2.*stress_fraction*abs(r))


@dataclass
class StaticGeometry:
    """Geometry jets callback: R,A,B,R_l,(log A)_l."""

    evaluate: Callable

    def __call__(self, x):
        fields = tuple(np.asarray(v, dtype=float) for v in self.evaluate(x))
        if len(fields) != 5 or any(v.shape != np.asarray(x).shape for v in fields):
            raise ValueError("five aligned geometry fields required")
        if not all(np.isfinite(v).all() for v in fields) or any(
                np.any(v <= 0) for v in fields[:3]):
            raise ValueError("finite positive static geometry required")
        return fields


def static_support(coordinate, geometry, load, *, domain,
                   mass_per_charge=0., quadrature_order=8, guard_points=15,
                   density_ceiling=None, proper_gradient_limit=None):
    """Minimum proper energy in piecewise-linear weighted material tensors.

    Y=A R² rho, X=A R² pr, Z=A R² pt obey
       X_x + (log A)_x Y - 2 (log R)_x Z = A B R² F.
    Y and Z interpolate linearly. X is reconstructed by integrating its force
    equation inside each cell, and matches its nodal unknown at both ends.
    Interior guards enforce the radial stress bound on that reconstruction;
    an independent denser sample measures the remaining inequality error.
    All three variables vanish at each module end.
    load(x) returns Lorentz force and net charge density on the common metric.
    mass_per_charge=0 is an optimistic carrier-cost relaxation, not a species.
    """
    x = np.asarray(coordinate, dtype=float)
    start, end = map(float, domain)
    if (x.ndim != 1 or len(x) < 5 or not np.isfinite(x).all() or
            np.any(np.diff(x) <= 0) or not np.isfinite([start, end, mass_per_charge]).all() or
            not x[0] <= start < end <= x[-1] or mass_per_charge < 0 or
            quadrature_order < 2 or int(quadrature_order) != quadrature_order or
            guard_points < 1 or int(guard_points) != guard_points):
        raise ValueError("increasing grid, finite domain and nonnegative host coefficient required")
    if not np.any(x == start) or not np.any(x == end):
        raise ValueError("module boundaries must be grid nodes")
    for limit in (density_ceiling, proper_gradient_limit):
        if limit is not None and (not np.isfinite(limit) or limit <= 0):
            raise ValueError("density and proper gradient limits must be positive")
    n = len(x)
    nodes, weights = leggauss(quadrature_order)
    fraction = (nodes+1.)/2.
    dx = np.diff(x)
    xx = x[:-1, None]+dx[:, None]*fraction
    ww = dx[:, None]*weights/2.
    r, a, b, rp, ap = geometry(xx)
    f, _ = load(xx)
    f = np.asarray(f, dtype=float)
    rn, an, bn, _, _ = geometry(x)
    fn, charge = map(lambda z: np.asarray(z, dtype=float), load(x))
    if (f.shape != xx.shape or fn.shape != x.shape or charge.shape != x.shape or
            not all(np.isfinite(v).all() for v in (f, fn, charge))):
        raise ValueError("finite force and charge aligned with quadrature/grid required")
    occupied = (x > start) & (x < end)
    active_cells = (xx >= start) & (xx <= end)
    if (np.any(abs(f[~active_cells]) > 1e-12) or
            np.any(abs(fn[~occupied]) > 1e-12) or np.any(abs(charge[~occupied]) > 1e-12)):
        raise ValueError("the finite module must contain its force and charge")
    left, right = 1.-fraction, fraction
    ax, rx = ap*b, rp*b/r
    al = np.sum(ww*ax*left, axis=1)
    ar = np.sum(ww*ax*right, axis=1)
    rl = -2.*np.sum(ww*rx*left, axis=1)
    rr = -2.*np.sum(ww*rx*right, axis=1)
    rhs = np.sum(ww*a*b*r*r*f, axis=1)
    cell = np.arange(n-1)
    row = np.tile(cell, 6)
    column = np.concatenate((cell, cell+1, n+cell, n+cell+1,
                             2*n+cell, 2*n+cell+1))
    value = np.concatenate((al, ar, -np.ones(n-1), np.ones(n-1), rl, rr))
    equation = coo_matrix((value, (row, column)), shape=(n-1, 3*n)).tocsr()
    identity = eye(n, format="csr")
    zero = 0.*identity
    cone = vstack((hstack((-identity, identity, zero)),
                   hstack((-identity, -identity, zero)),
                   hstack((-identity, zero, identity)),
                   hstack((-identity, zero, -identity))), format="csr")
    guards = np.arange(1, guard_points+1)/(guard_points+1)
    partial = partial_force_integrals(x, guards, geometry, load, quadrature_order)
    gl, gr, gz_l, gz_r, gf = partial
    ci = np.repeat(cell, guard_points)
    zi = np.tile(guards, n-1)
    # X(s)=X_i+F_s-aL_s Y_i-aR_s Y_(i+1)-rL_s Z_i-rR_s Z_(i+1).
    guard_rows = np.arange(len(ci))
    guard_columns = np.concatenate((ci, ci+1, n+ci, 2*n+ci, 2*n+ci+1))
    guard_row_indices = np.tile(guard_rows, 5)
    pressure_operator = coo_matrix((np.concatenate((-gl.ravel(), -gr.ravel(),
        np.ones(len(ci)), -gz_l.ravel(), -gz_r.ravel())),
        (guard_row_indices, guard_columns)), shape=(len(ci), 3*n)).tocsr()
    energy_operator = coo_matrix((np.r_[1.-zi, zi],
        (np.r_[guard_rows, guard_rows], np.r_[ci, ci+1])), shape=(len(ci), 3*n)).tocsr()
    cone = vstack((cone, pressure_operator-energy_operator,
                   -pressure_operator-energy_operator), format="csr")
    cone_rhs = np.r_[np.zeros(4*n), -gf.ravel(), gf.ravel()]
    if density_ceiling is not None:
        gx = x[:-1, None]+dx[:, None]*guards
        gradius, glapse, _, _, _ = geometry(gx)
        cone = vstack((cone, energy_operator), format="csr")
        cone_rhs = np.r_[cone_rhs, density_ceiling*(glapse*gradius**2).ravel()]
    if proper_gradient_limit is not None:
        # Differentiate the actual weighted interpolant, including A,R,B.
        # Both one-sided endpoint derivatives are constrained in each cell.
        gz = np.r_[0., guards, 1.]
        gx = x[:-1, None]+dx[:, None]*gz
        gradius, glapse, gb, grp, gap = geometry(gx)
        log_weight_x = gb*(gap+2.*grp/gradius)
        gl = (-1./dx[:, None]-log_weight_x*(1.-gz))/(glapse*gb*gradius**2)
        gr = (1./dx[:, None]-log_weight_x*gz)/(glapse*gb*gradius**2)
        grad_cell = np.repeat(cell, len(gz))
        grad_row = np.arange(len(grad_cell))
        difference = coo_matrix((np.r_[gl.ravel(), gr.ravel()],
            (np.r_[grad_row, grad_row], np.r_[grad_cell, grad_cell+1])),
            shape=(len(grad_cell), n)).tocsr()
        empty = 0.*difference
        dy = hstack((difference, empty, empty))
        dz = hstack((empty, empty, difference))
        cone = vstack((cone, dy, -dy, dz, -dz), format="csr")
        cone_rhs = np.r_[cone_rhs, np.full(4*len(grad_cell), proper_gradient_limit)]
    objective = np.zeros(3*n)
    objective[:n-1] += 4.*np.pi*np.sum(ww*b/a*left, axis=1)
    objective[1:n] += 4.*np.pi*np.sum(ww*b/a*right, axis=1)
    floor = mass_per_charge*an*rn*rn*abs(charge)
    upper = an*rn*rn*density_ceiling if density_ceiling is not None else np.full(n, np.inf)
    bounds = ([(float(floor[i]), float(upper[i])) if occupied[i] else (0., 0.) for i in range(n)]
              +[(None, None) if inside else (0., 0.) for inside in occupied]*2)
    result = linprog(objective, A_ub=cone, b_ub=cone_rhs,
                     A_eq=equation, b_eq=rhs, bounds=bounds, method="highs",
                     options={"dual_feasibility_tolerance": 1e-10,
                              "primal_feasibility_tolerance": 1e-10})
    base = dict(success=bool(result.success), solver_status=int(result.status),
                solver_message=result.message, nodes=n, domain=[start, end],
                mass_per_charge=mass_per_charge, guard_points=guard_points,
                density_ceiling=density_ceiling, proper_gradient_limit=proper_gradient_limit)
    if not result.success:
        return base, {}
    y, pressure, tangent = result.x.reshape(3, n)
    yq = y[:-1, None]*left+y[1:, None]*right
    pq = pressure[:-1, None]*left+pressure[1:, None]*right
    zq = tangent[:-1, None]*left+tangent[1:, None]*right
    p_x = np.diff(pressure)[:, None]/dx[:, None]
    res = p_x+ax*yq-2.*rx*zq-a*b*r*r*f
    measure = a*b*r*r
    density, radial, angular = np.array((y, pressure, tangent))/(an*rn*rn)
    raw_norm = np.sum(ww*(abs(p_x)+abs(ax*yq)+2.*abs(rx*zq)+abs(measure*f)))
    upper_value = np.where(occupied & np.isfinite(upper), upper, 0.)
    dual = float(rhs @ result.eqlin.marginals+cone_rhs @ result.ineqlin.marginals
                 +floor @ result.lower.marginals[:n]+upper_value @ result.upper.marginals[:n])
    stationarity = (objective-equation.T @ result.eqlin.marginals
                    -cone.T @ result.ineqlin.marginals
                    -result.lower.marginals-result.upper.marginals)
    total_charge = np.sum(ww*4.*np.pi*b*r*r*np.asarray(load(xx)[1]))
    charge_inventory = np.sum(ww*4.*np.pi*b*r*r*abs(np.asarray(load(xx)[1])))
    # Dense Gaussian points differ from the equally spaced optimization guards.
    check_z = (leggauss(2*quadrature_order)[0]+1.)/2.
    cl, cr, czl, czr, cf = partial_force_integrals(x, check_z, geometry, load,
                                                2*quadrature_order)
    reconstructed = (pressure[:-1, None]+cf-cl*y[:-1, None]-cr*y[1:, None]
                     -czl*tangent[:-1, None]-czr*tangent[1:, None])
    cy = y[:-1, None]*(1.-check_z)+y[1:, None]*check_z
    cz = tangent[:-1, None]*(1.-check_z)+tangent[1:, None]*check_z
    cx = x[:-1, None]+dx[:, None]*check_z
    check_r, check_a, check_b, check_rp, check_ap = geometry(cx)
    offgrid_dec = np.minimum(cy-abs(reconstructed), cy-abs(cz))/(check_a*check_r**2)
    check_charge = np.asarray(load(cx)[1])
    mass_floor_margin = cy/(check_a*check_r**2)-mass_per_charge*abs(check_charge)
    log_weight_l = check_ap+2.*check_rp/check_r
    density_gradient = (np.diff(y)[:, None]/(dx[:, None]*check_b)-log_weight_l*cy)/(check_a*check_r**2)
    angular_gradient = (np.diff(tangent)[:, None]/(dx[:, None]*check_b)-log_weight_l*cz)/(check_a*check_r**2)
    base.update(proper_energy=float(result.fun), dual_energy=dual,
        duality_gap_relative=abs(float(result.fun)-dual)/max(abs(float(result.fun)), 1e-30),
        max_weighted_equilibrium_residual=float(np.max(abs(equation @ result.x-rhs))),
        max_dual_stationarity_residual=float(np.max(abs(stationarity))),
        minimum_dec_margin=float(np.min(np.minimum(density-abs(radial), density-abs(angular)))),
        max_density=float(density.max()),
        linear_pressure_force_residual_l1_relative=float(np.sum(ww*abs(res))/max(raw_norm, 1e-30)),
        minimum_reconstructed_offgrid_dec_margin=float(offgrid_dec.min()),
        minimum_offgrid_carrier_mass_margin=float(mass_floor_margin.min()),
        maximum_offgrid_density=float(np.max(cy/(check_a*check_r**2))),
        maximum_offgrid_density_or_angular_gradient=float(max(abs(density_gradient).max(), abs(angular_gradient).max())),
        max_linear_pressure_force_residual=float(np.max(abs(res/measure))),
        net_charge=float(total_charge), absolute_charge_inventory=float(charge_inventory),
        radial_lorentz_load_integral=float(np.sum(ww*4.*np.pi*b*r*r*f)),
        absolute_radial_lorentz_load_integral=float(np.sum(ww*4.*np.pi*b*r*r*abs(f))),
        boundary_radial_pressure=[float(radial[x == start][0]), float(radial[x == end][0])])
    return base, dict(coordinate=x, density=density, radial_pressure=radial,
                      angular_pressure=angular, weighted_energy=y,
                      weighted_radial_pressure=pressure, weighted_angular_pressure=tangent,
                      charge_density=charge, lorentz_force=fn)


def partial_force_integrals(coordinate, fractions, geometry, load, order=8):
    """Integrals to arbitrary fractions of each cell for exact force replay."""
    x, s = np.asarray(coordinate), np.asarray(fractions)
    nodes, weights = leggauss(order)
    z = s[None, :, None]*(nodes[None, None, :]+1.)/2.
    dx = np.diff(x)[:, None, None]
    xx = x[:-1, None, None]+dx*z
    ww = dx*s[None, :, None]*weights[None, None, :]/2.
    r, a, b, rp, ap = geometry(xx)
    f, _ = load(xx)
    return tuple(np.sum(ww*v, axis=-1) for v in
                 (ap*b*(1.-z), ap*b*z, -2.*rp*b/r*(1.-z),
                  -2.*rp*b/r*z, a*b*r*r*f))


def support_tensor_at(coordinate, state, geometry, load, order=16):
    """Replay rho,pr,pt at arbitrary points through the integrated force law."""
    x = np.asarray(coordinate, dtype=float)
    grid = state["coordinate"]
    if np.any(x < grid[0]) or np.any(x > grid[-1]):
        raise ValueError("support replay points must lie in its grid")
    i = np.clip(np.searchsorted(grid, x, side="right")-1, 0, len(grid)-2)
    dx = grid[i+1]-grid[i]
    z = (x-grid[i])/dx
    nodes, weights = leggauss(order)
    part = z[..., None]*(nodes+1.)/2.
    xx = grid[i, None]+dx[..., None]*part
    ww = dx[..., None]*z[..., None]*weights/2.
    r, a, b, rp, ap = geometry(xx)
    y, p, t = [state[k] for k in ("weighted_energy", "weighted_radial_pressure",
                                 "weighted_angular_pressure")]
    yy = y[i, None]*(1.-part)+y[i+1, None]*part
    zz = t[i, None]*(1.-part)+t[i+1, None]*part
    pq = p[i]+np.sum(ww*(a*b*r*r*load(xx)[0]-ap*b*yy+2.*rp*b/r*zz), axis=-1)
    rq, aq, _, _, _ = geometry(x)
    return np.stack((y[i]*(1.-z)+y[i+1]*z, pq, t[i]*(1.-z)+t[i+1]*z), axis=-1)/(aq*rq*rq)[..., None]
