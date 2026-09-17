"""Finite reflecting conformal channels on a supplied static C1 geometry.

This is a necessary source screen. The bulk field law is the strip ground
state of independent unitary 1+1 dimensional conformal channels. It includes
the Weyl anomaly and distributional endpoint momentum exchange. Reflector
mass, transverse confinement and boundary polarization require a microscopic
model; an ordinary DEC completion is granted as an optimistic relaxation.
"""
from __future__ import annotations

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq, linprog
from scipy.sparse import csr_matrix


def quadrature(chart, lower, upper, *, order=8, extra_cuts=()):
    """Composite native-knot quadrature, splitting every declared boundary."""
    if (not chart.coordinate[0] <= lower < upper <= chart.coordinate[-1]
            or order < 2 or int(order) != order):
        raise ValueError("ordered in-chart limits and integer order >= 2 required")
    extra = np.asarray(extra_cuts, float).ravel()
    if not np.isfinite(extra).all():
        raise ValueError("finite cuts required")
    cuts = np.unique(np.r_[lower, chart.coordinate[(chart.coordinate > lower)
        & (chart.coordinate < upper)], extra[(extra > lower) & (extra < upper)], upper])
    nodes, weights = leggauss(order)
    half = np.diff(cuts)/2.
    return ((cuts[:-1, None]+half[:, None]*(1.+nodes)).ravel(),
            (half[:, None]*weights).ravel())


def optical_partitions(chart, domain, count, *, order=8):
    """Equal optical-length reflecting compartments in one material module.

    A spline integral locates the partitions. Independent composite Gaussian
    integrals of B/A define the lengths used in the field law.
    """
    lower, upper = map(float, domain)
    if (not chart.coordinate[0] <= lower < upper <= chart.coordinate[-1]
            or count < 1 or int(count) != count):
        raise ValueError("in-chart domain and positive integer compartment count required")
    antiderivative = CubicSpline(chart.coordinate,
        chart.radial_scale/chart.lapse).antiderivative()
    offset = float(antiderivative(lower))
    total = float(antiderivative(upper)-offset)
    ends = np.array([lower]+[brentq(lambda x: float(antiderivative(x)-offset)-total*i/count,
        lower, upper, xtol=2e-14) for i in range(1, count)]+[upper])
    lengths = []
    for lo, hi in zip(ends[:-1], ends[1:]):
        x, w = quadrature(chart, lo, hi, order=order)
        _, a, b, *_ = chart.jets(x)
        lengths.append(float(w @ (b/a)))
    return ends, np.asarray(lengths)


def strip_tensor(radius, lapse, acceleration, acceleration_derivative,
                 optical_length, *, strength=1.):
    """Bulk (rho, p_r, p_t) for strength=eta*c, with p_t=0.

    The reflecting strip has rho_2=p_2=-pi*c/(24 L_opt^2 A^2)
    in its Casimir part. The spherical average divides by 4*pi*R^2.
    No statement about a four-dimensional scalar vacuum is implied.
    """
    r, a, ap, app, length = np.broadcast_arrays(*[np.asarray(v, float) for v in
        (radius, lapse, acceleration, acceleration_derivative, optical_length)])
    if (not all(np.isfinite(v).all() for v in (r, a, ap, app, length))
            or any(np.any(v <= 0) for v in (r, a, length))
            or not np.isfinite(strength) or strength < 0):
        raise ValueError("positive geometry/length and nonnegative finite strength required")
    casimir = -np.pi/(24.*(length*a)**2)
    rho2 = casimir+(2.*app+ap*ap)/(24.*np.pi)
    pr2 = casimir-ap*ap/(24.*np.pi)
    return strength*np.stack((rho2, pr2, np.zeros_like(r)), axis=-1)/(4.*np.pi*r*r)[..., None]


def channel_tensor(chart, coordinate, ends, lengths, *, strength=1.):
    """Piecewise strip tensor; zero beyond the declared channel endpoints.

    At a wall this function selects the right limit. Endpoint forces use both
    limits explicitly in boundary_exchange, so no averaged wall is inserted.
    """
    x = np.asarray(coordinate, float)
    ends, lengths = np.asarray(ends, float), np.asarray(lengths, float)
    if (ends.ndim != 1 or lengths.shape != (len(ends)-1,)
            or len(ends) < 2 or not np.isfinite(ends).all()
            or np.any(np.diff(ends) <= 0) or not np.isfinite(lengths).all()
            or np.any(lengths <= 0)):
        raise ValueError("ordered endpoints and aligned positive optical lengths required")
    r, a, _, _, _, ap, app = chart.jets(x)
    index = np.clip(np.searchsorted(ends, x, side="right")-1, 0, len(lengths)-1)
    tensor = strip_tensor(r, a, ap, app, lengths[index], strength=strength)
    return tensor*((x >= ends[0]) & (x < ends[-1]))[..., None]


def boundary_exchange(chart, ends, lengths, *, strength=1.):
    """Area-integrated radial force on each reflector: -4*pi*R^2 [p_Q].

    These scalar radial forces specify material reaction duties. They are
    neither a center-of-mass vector force nor a supplied equilibrium solution.
    """
    ends, lengths = np.asarray(ends, float), np.asarray(lengths, float)
    if len(ends) != len(lengths)+1 or np.any(np.diff(ends) <= 0):
        raise ValueError("ordered walls and aligned optical lengths required")
    r, a, _, _, _, ap, app = chart.jets(ends)
    left = np.zeros(len(ends))
    right = np.zeros(len(ends))
    left[1:] = strip_tensor(r[1:], a[1:], ap[1:], app[1:], lengths,
                            strength=strength)[:, 1]
    right[:-1] = strip_tensor(r[:-1], a[:-1], ap[:-1], app[:-1], lengths,
                              strength=strength)[:, 1]
    return dict(coordinate=ends, pressure_left=left, pressure_right=right,
                force_on_material=4.*np.pi*r*r*(left-right))


def einstein_source(chart, coordinate):
    r, _, _, rp, rpp, ap, app = chart.jets(coordinate)
    return np.stack((((1.-rp*rp)/r**2-2.*rpp/r)/(8.*np.pi),
        (-(1.-rp*rp)/r**2+2.*ap*rp/r)/(8.*np.pi),
        (app+ap*ap+ap*rp/r+rpp/r)/(8.*np.pi)), axis=-1)


def dec_projections(tensor):
    t = np.asarray(tensor, float)
    if t.shape[-1] != 3 or not np.isfinite(t).all():
        raise ValueError("finite diagonal (rho, pr, pt) tensor required")
    return np.stack((t[..., 0]+t[..., 1], t[..., 0]-t[..., 1],
                     t[..., 0]+t[..., 2], t[..., 0]-t[..., 2]), axis=-1)


def angular_target_completion(remainder):
    """Optimistic angular target (-2v,+2v,-2v), v >= 0, plus ordinary DEC.

    The angular target is an independently unsupplied source requirement.
    It changes neither rho+pr nor rho-pt. Nonnegative values of those two
    projections are necessary and sufficient for this pointwise relaxation.
    """
    margins = dec_projections(remainder)
    v = np.maximum.reduce((np.zeros(margins.shape[:-1]), -margins[..., 1]/4.,
                           -margins[..., 2]/4.))
    target = v[..., None]*np.array([-2., 2., -2.])
    return v, np.asarray(remainder)-target


def bulk_completion_gate(demand_after_maxwell, basis, *, grant_angular_target=False,
                         inventory_weights=None):
    """Minimize the sum of nonnegative scaled channel strengths at bulk samples.

    basis has shape (samples, source groups, 3). The aggregate ordinary tensor is
    free inside the DEC, so old material profiles, density ceilings and all
    microscopic boundary costs are relaxed. A successful LP establishes only
    these sampled bulk inequalities.
    """
    demand, basis = np.asarray(demand_after_maxwell, float), np.asarray(basis, float)
    if (demand.ndim != 2 or demand.shape[1] != 3 or basis.ndim != 3
            or basis.shape[0] != len(demand) or basis.shape[2] != 3
            or not np.isfinite(demand).all() or not np.isfinite(basis).all()):
        raise ValueError("aligned finite target and module tensors required")
    target_margins = dec_projections(demand)
    projections = dec_projections(basis)
    selected = [0, 3] if grant_angular_target else [0, 1, 2, 3]
    # For each projection: P(Q) c <= P(target).
    matrix = projections[:, :, selected].transpose(0, 2, 1).reshape(-1, basis.shape[1])
    bound = target_margins[:, selected].ravel()
    scale = np.maximum.reduce((np.max(abs(matrix), axis=1), abs(bound),
                               np.full(len(bound), 1e-12)))
    cost = (np.ones(basis.shape[1]) if inventory_weights is None
            else np.asarray(inventory_weights, float))
    if cost.shape != (basis.shape[1],) or not np.isfinite(cost).all() or np.any(cost <= 0):
        raise ValueError("positive aligned inventory weights required")
    result = linprog(cost, A_ub=csr_matrix(matrix/scale[:, None]),
        b_ub=bound/scale, bounds=(0., None), method="highs",
        options={"dual_feasibility_tolerance": 1e-10, "primal_feasibility_tolerance": 1e-10})
    summary = dict(solver_status=int(result.status), solver_message=result.message,
        sampled_bulk_inequalities_solved=bool(result.success),
        angular_source_granted_as_target=grant_angular_target,
        boundary_material_closure_supplied=False)
    direct = np.flatnonzero((bound < 0.) & np.all(matrix >= 0., axis=1))
    if len(direct):
        worst = int(direct[np.argmin(bound[direct])])
        summary["direct_exclusion_witness"] = dict(sample_index=worst//len(selected),
            projection_index=selected[worst % len(selected)],
            target_projection=float(bound[worst]),
            minimum_basis_projection=float(matrix[worst].min()))
    arrays = {}
    if result.success:
        quantum = np.einsum("nmc,m->nc", basis, result.x)
        remainder = demand-quantum
        angular, material = (angular_target_completion(remainder) if grant_angular_target
                             else (np.zeros(len(demand)), remainder))
        margins = dec_projections(material)
        summary.update(scaled_channel_strengths=result.x.tolist(), objective=float(result.fun),
            minimum_sampled_dec_margin=float(margins.min()),
            scaled_constraint_max_violation=float((np.maximum(matrix @ result.x-bound, 0.)/scale).max()),
            dual_objective=float((bound/scale) @ result.ineqlin.marginals),
            dual_stationarity_max=float(abs(cost-(matrix/scale[:, None]).T @ result.ineqlin.marginals
                                               -result.lower.marginals).max()))
        arrays = dict(quantum=quantum, angular_weight=angular, material=material)
    return summary, arrays


def trace_witness(chart, coordinate, maxwell_energy):
    """Local exclusion for any nonnegative mixture of radial conformal channels.

    rho_Q-pr_Q = eta*c*(a''+a'^2)/(48*pi^2*R^2), independent of
    cavity length and the traceless state part. A negative target rho-pr at
    positive anomaly coefficient precludes an ordinary DEC remainder.
    """
    x = np.asarray(coordinate, float)
    r, _, _, _, _, ap, app = chart.jets(x)
    demanded = einstein_source(chart, x)
    bare_difference = demanded[..., 0]-demanded[..., 1]
    remaining_difference = bare_difference-2.*np.asarray(maxwell_energy, float)
    coefficient = (app+ap*ap)/(48.*np.pi**2*r*r)
    return dict(geometric_rho_minus_pr=bare_difference,
        after_maxwell_rho_minus_pr=remaining_difference,
        quantum_rho_minus_pr_per_strength=coefficient,
        excludes_radial_conformal_plus_dec=(remaining_difference < 0) & (coefficient >= 0))
