"""Bounded inverse construction of a spherical reset and its explicit sources.

The mass history fixes energy density and conserved luminosity. A nonlinear
radial lapse solve enforces a material radial equation of state. The angular
Einstein equation, source admissibility, and exchanges remain independent
acceptance conditions. A small residual is required before calling this a
coupled solution; the construction is a local necessary relaxation of rail
matching and service, which require separate verification on any survivor.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import CubicSpline
from scipy.optimize import linprog

PI = np.pi
NAMES = ("duration", "time_skew", "storage_mass", "donor_radius", "donor_width",
         "reservoir_radius", "reservoir_width", "string_release", "radial_ratio", "tangential_ratio")
BOUNDS = np.array([(4., 14.255), (-.65, .65), (0., .25), (2.35, 2.9), (.16, .42),
                   (3.4, 5.55), (.25, .65), (0., 1.), (0., 1.), (0., 1.)])


def controls_from_unit(unit):
    z=np.asarray(unit,dtype=float)
    x=BOUNDS[:,0]+z*(BOUNDS[:,1]-BOUNDS[:,0])
    for i in [2,7]:
        x[...,i]=1e-5*np.expm1(z[...,i]*np.log1p(BOUNDS[i,1]/1e-5))
    return np.clip(x,BOUNDS[:,0],BOUNDS[:,1])


def controls_to_unit(controls):
    x=np.asarray(controls,dtype=float)
    z=(x-BOUNDS[:,0])/(BOUNDS[:,1]-BOUNDS[:,0])
    for i in [2,7]:
        z[...,i]=np.log1p(x[...,i]/1e-5)/np.log1p(BOUNDS[i,1]/1e-5)
    return np.clip(z,0.,1.)


def rise(x):
    x = np.clip(np.asarray(x), 0., 1.)
    return x**3*(10.-15.*x+6.*x*x)


def compact_cdf(r, center, width):
    """C3 cumulative distribution with a compact nonnegative density."""
    x = np.clip((np.asarray(r)-center+width)/(2*width), 0., 1.)
    cdf = x**4*(35.-84.*x+70.*x*x-20.*x**3)
    density = 140*x**3*(1-x)**3/(2*width)
    return cdf, density


def phase_blend(phases, values, targets):
    """C2 interpolation bounded by adjacent static controls, including long tails.

    Each reference shape is a rest waypoint. Zero first and second phase
    derivatives join adjacent quintic interpolants without generating a late
    oscillation between nearly identical settled controls.
    """
    phases, values, targets = map(np.asarray, (phases, values, targets))
    index = np.clip(np.searchsorted(phases, targets, side='right')-1,0,len(phases)-2)
    width = phases[index+1]-phases[index]
    z = np.clip((targets-phases[index])/width,0.,1.)
    w = rise(z)
    ws = 30*z*z*(1-z)**2/width
    wss = 60*z*(1-z)*(1-2*z)/width**2
    extra = (None,)*(values.ndim-1)
    delta = values[index+1]-values[index]
    return (values[index]+w[(slice(None),)+extra]*delta,
            ws[(slice(None),)+extra]*delta,wss[(slice(None),)+extra]*delta)


@dataclass
class ReferenceGrid:
    u: np.ndarray
    r: np.ndarray
    phase: np.ndarray
    mass: np.ndarray
    mass_r: np.ndarray
    mass_u: np.ndarray
    mass_uu: np.ndarray
    f: np.ndarray
    f_r: np.ndarray
    nu: np.ndarray
    nu_u: np.ndarray
    nu_r: np.ndarray
    nu_rr: np.ndarray
    energy: np.ndarray
    pressure: np.ndarray
    transverse: np.ndarray
    reference_path: str
    path_kind: str = 'waypoints'


def reference_grid(path: str | Path, radial_points=129, temporal_points=49, path_kind='waypoints'):
    frame = pd.read_csv(path)
    frame = frame[frame.holding & frame.level.eq(2)]
    phases = np.sort(frame.s.unique())
    if path_kind == 'direct':
        phases = phases[[0,-1]]
    elif path_kind != 'waypoints':
        raise ValueError('path_kind must be direct or waypoints')
    r = np.linspace(2.15, 6.25, radial_points)
    reference_radius = np.linspace(2.15, 6.25, 1025)
    u = np.linspace(0., 1., temporal_points)
    # Allocate clock time to the active part of the reset while retaining the
    # late s=15 endpoint. All endpoint phase derivatives through order two vanish.
    q = rise(u)
    q_u, q_uu = 30*u*u*(1-u)**2, 60*u*(1-u)*(1-2*u)
    factor = (phases[-1]-phases[0])*4*np.exp(4*q)/np.expm1(4.)
    phase = phases[0]+(phases[-1]-phases[0])*np.expm1(4*q)/np.expm1(4.)
    phase_u = factor*q_u
    phase_uu = factor*(q_uu+4*q_u*q_u)
    if path_kind == 'direct':
        # The endpoint blend itself supplies the C2 start and finish.
        phase = phases[0]+(phases[-1]-phases[0])*u
        phase_u = np.full_like(u,phases[-1]-phases[0])
        phase_uu = np.zeros_like(u)
    logs_f, logs_a = [], []
    for s in phases:
        g = frame[frame.s.eq(s)].sort_values("areal_radius")
        rr = g.areal_radius.to_numpy()
        if r[0] < rr[0] or r[-1] > rr[-1]+1e-12:
            raise ValueError("the construction grid must lie inside every reference annulus")
        f = 1.-2*g.reference_static_mass.to_numpy()/rr
        if np.min(f) <= 0:
            raise ValueError("reference areal chart is nonpositive")
        logs_f.append(CubicSpline(rr, np.log(f))(reference_radius))
        logs_a.append(CubicSpline(rr, np.log(g.alpha.to_numpy()))(reference_radius))
    sf = CubicSpline(reference_radius,np.array(logs_f),axis=1)
    sa = CubicSpline(reference_radius,np.array(logs_a),axis=1)
    logf,ls,lss = phase_blend(phases,sf(r),phase)
    f = np.exp(logf)
    f_r = f*phase_blend(phases,sf(r,1),phase)[0]
    f_u = f*ls*phase_u[:, None]
    f_uu = f*((ls*ls+lss)*phase_u[:, None]**2+ls*phase_uu[:, None])
    mass = .5*r*(1-f)
    mass_r = .5*(1-f-r*f_r)
    mass_u, mass_uu = -.5*r*f_u, -.5*r*f_uu
    nu,nus,_ = phase_blend(phases,sa(r),phase)
    nu_r = phase_blend(phases,sa(r,1),phase)[0]
    nu_rr = phase_blend(phases,sa(r,2),phase)[0]
    nu_u = nus*phase_u[:, None]
    energy = mass_r/(4*PI*r*r)
    pressure = f*nu_r/(4*PI*r)-mass/(4*PI*r**3)
    transverse = (f*(nu_rr+nu_r*nu_r+nu_r/r)+.5*f_r*(nu_r+1/r))/(8*PI)
    return ReferenceGrid(u, r, phase, mass, mass_r, mass_u, mass_uu, f, f_r,
                         nu, nu_u, nu_r, nu_rr, energy, pressure, transverse, str(path),path_kind)


def polar_areal_channels(r, f, f_r, f_t, f_tt, nu, nu_r, nu_rr, nu_t):
    """Exact reduced Einstein tensor, in the stationary orthonormal frame."""
    r, f = np.asarray(r), np.asarray(f)
    if np.any(f <= 0):
        raise ValueError("positive f is required by this areal frame")
    alpha = np.exp(nu)
    energy = (1-f-r*f_r)/(8*PI*r*r)
    pressure = (f-1+2*r*f*nu_r)/(8*PI*r*r)
    current = f_t/(8*PI*r*alpha*np.sqrt(f))
    transverse = (f*(nu_rr+nu_r*nu_r+nu_r/r)+.5*f_r*(nu_r+1/r)
                  +(f_tt-f_t*nu_t-1.5*f_t*f_t/f)/(2*alpha*alpha*f))/(8*PI)
    return np.stack([energy, pressure, current, transverse], axis=-1)


def infrastructure_boost(enthalpy, current, moving, maximum_speed=.5):
    """Smooth bounded current response of the existing rest-frame stress.

    j_b = j c^2 h^2/(j^2+c^2 h^2), with c=2 gamma_max^2 v_max.
    Hence |j_b/h| <= gamma_max^2 v_max. The response approaches j at
    small current and vanishes quadratically as h approaches zero.
    """
    h, j = np.broadcast_arrays(enthalpy, current)
    if not moving:
        return np.zeros_like(j), np.zeros_like(j), np.zeros_like(j)
    c = 2*maximum_speed/(1-maximum_speed**2)
    den = j*j+(c*h)**2
    jb = np.divide(j*(c*h)**2, den, out=np.zeros_like(j), where=den > 0)
    q = np.divide(jb, h, out=np.zeros_like(j), where=h != 0)
    root = np.sqrt(1+4*q*q)
    kinetic = 2*q*jb/(root+1)
    rapidity = .5*np.arcsinh(2*q)
    return kinetic, jb, np.tanh(rapidity)


def ordinary_energy_lower_bound(enthalpy, current, branch=1, carrier_current=None):
    """Optimistic added energy under E_c>=|j| and |P_c|<=E_c.

    h denotes the retained background after any chosen frame transformation.
    current is the total current; carrier_current is the remaining ordinary
    carrier current when the background also carries momentum.
    The positive-enthalpy branch requires E_c >= |j|-h/2. The negative
    branch is feasible only for h<=-2|j|, and then E_c=|j| is an optimistic
    lower bound (allowing p_c=-E_c). Smoothness, transfer, and equations of
    state impose further restrictions. This is a local necessary bound.
    """
    h, j = np.broadcast_arrays(enthalpy, np.abs(current))
    q = j if carrier_current is None else np.abs(np.asarray(carrier_current))
    if branch == 1:
        return np.maximum(q, j-.5*h)
    if branch == -1:
        return np.where(h <= -2*j, q, np.inf)
    raise ValueError("branch must be +1 or -1")


def minimum_energy_lp(enthalpy, current, weights, branch=1, carrier_current=None):
    """Independent LP check of the relaxed ordinary-carrier energy bound."""
    h, j, weights = map(lambda v: np.asarray(v, dtype=float), (enthalpy, current, weights))
    n = len(h)
    q = abs(j) if carrier_current is None else abs(np.asarray(carrier_current, dtype=float))
    if j.shape != h.shape or weights.shape != h.shape or np.any(weights <= 0):
        raise ValueError("positive weights and aligned one-dimensional source data required")
    from scipy.sparse import eye, hstack, vstack
    identity = eye(n, format="csr")
    # x=(E_c,P_c), E_c>=|j|, -E_c<=P_c<=E_c, branch*(h+E_c+P_c)>=2|j|.
    matrix = vstack([hstack([-identity, identity]), hstack([-identity, -identity]),
                     hstack([-branch*identity, -branch*identity])], format="csr")
    rhs = np.r_[np.zeros(2*n), branch*h-2*np.abs(j)]
    result = linprog(np.r_[weights, np.zeros(n)], A_ub=matrix, b_ub=rhs,
                     bounds=[(v, None) for v in q]+[(None, None)]*n,
                     method="highs", options={"time_limit": 20.})
    return result


def _history(grid, x):
    duration, skew, amount, donor, donor_width, receiver, receiver_width, release, wr, wt = x
    u, r = grid.u, grid.r
    time = .745+duration*(u+skew*u*(1-u))
    t_u = duration*(1+skew*(1-2*u))
    t_uu = -2*duration*skew
    k = np.sin(PI*u)**4
    k_u = 4*PI*np.sin(PI*u)**3*np.cos(PI*u)
    k_uu = 4*PI*PI*(3*np.sin(PI*u)**2*np.cos(PI*u)**2-np.sin(PI*u)**4)
    end_cdf, end_density = compact_cdf(r, donor, donor_width)
    res_cdf, res_density = compact_cdf(r, receiver, receiver_width)
    # Truncation at the inner domain is explicit and normalized; endpoints
    # retain zero added mass. Width bounds keep the outer supports contained.
    def normalize(cdf, density):
        z = cdf[-1]-cdf[0]
        if z <= 0:
            raise ValueError("empty reservoir/donor profile")
        return (cdf-cdf[0])/z, density/z
    end_cdf, end_density = normalize(end_cdf, end_density)
    res_cdf, res_density = normalize(res_cdf, res_density)
    c, c_r = res_cdf-end_cdf, res_density-end_density
    mass = grid.mass+amount*k[:, None]*c
    mass_r = grid.mass_r+amount*k[:, None]*c_r
    mass_u = grid.mass_u+amount*k_u[:, None]*c
    mass_uu = grid.mass_uu+amount*k_uu[:, None]*c
    mt = mass_u/t_u[:, None]
    mtt = mass_uu/t_u[:, None]**2-mass_u*t_uu/t_u[:, None]**3
    f = 1.-2*mass/r
    f_r = -2*mass_r/r+2*mass/r**2
    z = (r-r[0])/(r[-1]-r[0])
    window = rise(z/.03)*rise((1-z)/.03)
    released = .039783*release*k[:, None]*window/r**2
    return {"time": time, "t_u": t_u, "mass": mass, "mass_r": mass_r,
            "mass_t": mt, "mass_tt": mtt, "f": f, "f_r": f_r,
            "released": released, "storage_state": amount*k,
            "storage_luminosity": -amount*k_u[:, None]*c/t_u[:, None],
            "donor_mass_density": -amount*k[:, None]*end_density,
            "reservoir_mass_density": amount*k[:, None]*res_density}


def _sources(grid, history, alpha, moving, radial_ratio, indices=None):
    ix = (...,) if indices is None else indices
    r = grid.r if indices is None else grid.r[indices[1]]
    f, mt, released = (history[k][ix] for k in ("f", "mass_t", "released"))
    eb, pb = grid.energy[ix], grid.pressure[ix]
    energy = history["mass_r"][ix]/(4*PI*r*r)
    current = -mt/(4*PI*r*r*alpha*np.sqrt(f))
    kinetic, jb, speed = infrastructure_boost(eb+pb, current, moving)
    null_current = current-jb
    transfer = np.hypot(null_current, .01*released)
    material = energy-eb+released-kinetic-transfer
    pressure = pb+released+kinetic+radial_ratio*material+transfer
    return energy, pressure, current, material, transfer, kinetic, jb, speed


def construct(grid: ReferenceGrid, controls, *, moving=False, retain=False):
    """Solve radial source/lapse coupling and evaluate remaining field equations.

    No algebraic type or energy sign is repaired after solving. The grid is a
    numerical construction of one mass history; angular closure is a separate
    residual driven by the bounded outer search.
    """
    x = np.asarray(controls, dtype=float)
    if x.shape != (10,) or not np.isfinite(x).all():
        raise ValueError("ten finite controls required")
    if np.any(x < BOUNDS[:, 0]-1e-12) or np.any(x > BOUNDS[:, 1]+1e-12):
        raise ValueError("controls exceed the registered search bounds")
    h = _history(grid, x)
    r, u, wr, wt = grid.r, grid.u, x[-2], x[-1]
    if np.min(h["f"]) <= 0:
        return {"status": "nonpositive_areal_metric", "objective": 1e6+abs(float(h['f'].min())),
                "min_f": float(h["f"].min()), "controls": x.tolist(), "moving": bool(moving)}
    # Solve for alpha/alpha_b; exact baseline cancellation avoids subtracting
    # large independent pressure and mass terms near the compact inner edge.
    ratio = np.ones_like(h["f"])
    if wr == 1.:
        pressure = grid.pressure+2*h["released"]+(h["mass_r"]-grid.mass_r)/(4*PI*r*r)
        gradient = (h["mass"]+4*PI*r**3*pressure)/(r*r*h["f"])
        delta = cumulative_trapezoid(gradient-grid.nu_r, r, axis=1, initial=0.)
        logs = delta-delta[:, -1:]
        if np.max(abs(logs)) > 60:
            return {"status": "lapse_range_exhausted", "objective": 1e5+float(np.max(abs(logs))),
                    "min_f": float(h["f"].min()), "controls": x.tolist(), "moving": bool(moving)}
        ratio = np.exp(logs)
    else:
        # RK4 with time slices vectorized on the selected radial grid.
        def rhs(i, y):
            if np.any(y <= 1e-12) or np.max(abs(y)) > 1e12:
                raise FloatingPointError("positive lapse range exhausted")
            a = np.exp(grid.nu[:, i])*y
            e, p, *_ = _sources(grid, h, a, moving, wr, (slice(None), i))
            grad = (h["mass"][:, i]+4*PI*r[i]**3*p)/(r[i]**2*h["f"][:, i])
            return y*(grad-grid.nu_r[:, i])
        try:
            # Midpoint data are averaged; refinement controls this second-order
            # coefficient interpolation independently of the RK stages.
            for i in range(len(r)-1, 0, -1):
                dr = r[i-1]-r[i]
                y = ratio[:, i]
                k1 = rhs(i, y)
                k2 = .5*(rhs(i, y+.5*dr*k1)+rhs(i-1, y+.5*dr*k1))
                k3 = .5*(rhs(i, y+.5*dr*k2)+rhs(i-1, y+.5*dr*k2))
                k4 = rhs(i-1, y+dr*k3)
                ratio[:, i-1] = y+dr*(k1+2*k2+2*k3+k4)/6
                if np.any(ratio[:, i-1] <= 1e-12) or np.max(ratio[:, i-1]) > 1e12:
                    raise FloatingPointError("positive lapse range exhausted")
        except FloatingPointError:
            return {"status": "lapse_range_exhausted", "objective": 1e5,
                    "min_f": float(h["f"].min()), "controls": x.tolist(), "moving": bool(moving)}
    alpha = np.exp(grid.nu)*ratio
    e, p, j, material, transfer, kinetic, jb, speed = _sources(grid, h, alpha, moving, wr)
    nu = np.log(alpha)
    nu_r = (h["mass"]+4*PI*r**3*p)/(r*r*h["f"])
    # Differentiate only the changed lapse. The analytic reference jets avoid
    # mistaking an unresolved narrow reference feature for a new field residual.
    nu_rr = grid.nu_rr+CubicSpline(r, nu_r-grid.nu_r, axis=1)(r, 1)
    nu_t = (grid.nu_u+CubicSpline(u, np.log(ratio), axis=0)(u, 1))/h["t_u"][:, None]
    geometric = polar_areal_channels(r, h["f"], h["f_r"], -2*h["mass_t"]/r,
                                    -2*h["mass_tt"]/r, nu, nu_r, nu_rr, nu_t)
    transverse = grid.transverse+wt*material
    source = np.stack([e, p, j, transverse], axis=-1)
    source_h = e+p
    margin = abs(source_h)-2*abs(j)
    angular = geometric[..., 3]-transverse
    # A fixed physical scale prevents broad low-density tails from diluting
    # finite violations or singular near-zero normalizers dominating a score.
    scale = .01
    negative_material = np.maximum(-material, 0.)/scale
    radial_bad = np.maximum(-margin, 0.)/scale
    angular_bad = abs(angular)/scale
    interior = (slice(1, -1), slice(2, -2))
    endpoint_mass_error = float(np.max(abs(h["mass"][[0, -1]]-grid.mass[[0, -1]])))
    boundary_mass_error = float(np.max(abs(h["mass"][:, [0, -1]]-grid.mass[:, [0, -1]])))
    extrema = np.array([negative_material.max(), radial_bad.max(), angular_bad[interior].max()])
    objective = float(np.max(extrema)+.1*np.sum(extrema))
    result = {"status": "evaluated", "objective": objective, "controls": x.tolist(), "moving": bool(moving),
              "min_f": float(h["f"].min()), "min_material_density": float(material.min()),
              "min_radial_margin": float(margin.min()),
              "max_angular_residual": float(abs(angular[interior]).max()),
              "max_energy_residual": float(abs(geometric[..., 0]-e).max()),
              "max_radial_pressure_residual": float(abs(geometric[..., 1]-p).max()),
              "max_momentum_residual": float(abs(geometric[..., 2]-j).max()),
              "max_background_speed": float(abs(speed).max()),
              "endpoint_mass_error": endpoint_mass_error, "boundary_mass_error": boundary_mass_error,
              "min_lapse_ratio": float(ratio.min()), "max_lapse_ratio": float(ratio.max()),
              "max_inner_lapse_relative_change": float(abs(ratio[:, 0]-1).max()),
              "type_iv_points": int((margin < -1e-10).sum()), "points": int(margin.size),
              "local_necessary_conditions_pass": bool(material.min() >= -1e-9 and margin.min() >= -1e-9
                  and abs(angular[interior]).max() < 1e-6 and endpoint_mass_error < 1e-10
                  and boundary_mass_error < 1e-10)}
    if retain:
        result["fields"] = {**h, "radius": r, "u": u, "phase": grid.phase,
                            "alpha": alpha, "nu_r": nu_r, "nu_t": nu_t,
                            "source": source, "geometric": geometric,
                            "material_density": material, "transfer_density": transfer,
                            "background_kinetic": kinetic, "background_current": jb,
                            "background_speed": speed, "angular_residual": angular,
                            "radial_margin": margin, "background_energy": grid.energy,
                            "background_pressure": grid.pressure, "background_transverse": grid.transverse}
    return result


def exchange_channels(time, radius, f, f_t, nu_r, alpha, source):
    """Covariant energy and radial-force transfer to a spherical component."""
    t, r = np.asarray(time), np.asarray(radius)
    e, p, j, pt = (source[..., i] for i in range(4))
    e_t = CubicSpline(t, e, axis=0)(t, 1)
    j_t = CubicSpline(t, j, axis=0)(t, 1)
    j_r = CubicSpline(r, j, axis=1)(r, 1)
    p_r = CubicSpline(r, p, axis=1)(r, 1)
    lambda_t = -.5*f_t/f
    power = (e_t+lambda_t*(e+p))/alpha+np.sqrt(f)*(j_r+2*(nu_r+1/r)*j)
    force = (j_t+2*lambda_t*j)/alpha+np.sqrt(f)*(p_r+nu_r*(e+p)+2*(p-pt)/r)
    return np.stack([power, force], axis=-1)
