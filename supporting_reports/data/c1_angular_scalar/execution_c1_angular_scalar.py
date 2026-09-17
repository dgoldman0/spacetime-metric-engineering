"""A separate four-dimensional conformal scalar for C1's angular source role.

The finite-domain spectral problem uses the retained metric exactly as
tabulated. Its eigenvalues address stationary-state construction. The
renormalized tensor and physical reflecting material remain separate inputs.
Butcher's cylindrical tensor is supplied only as a limiting benchmark.
"""
from __future__ import annotations

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh


def scalar_curvature(chart, coordinate):
    """Four-dimensional Ricci scalar, with proper-distance metric derivatives."""
    r, _, _, rp, rpp, ap, app = chart.jets(coordinate)
    return -2.*(app+ap*ap)-4.*(rpp+ap*rp)/r+2.*(1.-rp*rp)/r**2


def mode_potential(chart, coordinate, *, angular_index=0, mass=0., coupling=1./6.):
    """Potential of -d_y^2+V_j, dy=B dx/A and u=R phi_j.

    The time dependence is exp(-i omega t). Each angular multiplet has
    degeneracy 2*j+1. Independent radial-channel fields are retained elsewhere.
    """
    if (not isinstance(angular_index, (int, np.integer)) or angular_index < 0
            or not np.isfinite([mass, coupling]).all() or mass < 0):
        raise ValueError("nonnegative integer angular index/mass and finite coupling required")
    r, a, _, rp, rpp, ap, _ = chart.jets(coordinate)
    return a*a*((rpp+ap*rp)/r+angular_index*(angular_index+1.)/r**2
                +mass*mass+coupling*scalar_curvature(chart, coordinate))


def finite_element_problem(chart, domain, *, nodes=1025, order=6, angular_index=0,
                           mass=0., coupling=1./6., boundary="dirichlet"):
    """Consistent-mass linear finite elements for the optical Schrödinger form.

    natural_u is the auxiliary zero-normal-derivative condition on u=R phi,
    not the Neumann condition on the physical scalar phi. It supplies a
    finite-interval variational comparison, not an exterior matching law.
    """
    lo, hi = np.asarray(domain, float)
    if (not np.isfinite([lo, hi]).all()
            or not chart.coordinate[0] <= lo < hi <= chart.coordinate[-1]
            or not isinstance(nodes, (int, np.integer)) or nodes < 9
            or not isinstance(order, (int, np.integer)) or order < 2
            or boundary not in ("dirichlet", "natural_u")):
        raise ValueError("in-chart interval, integer resolution and specified boundary required")
    x = np.linspace(lo, hi, nodes)
    dx = np.diff(x)
    t, w = leggauss(order)
    t, w = (t+1.)/2., w/2.
    gx = x[:-1, None]+dx[:, None]*t
    _, a, b, *_ = chart.jets(gx)
    v = mode_potential(chart, gx, angular_index=angular_index, mass=mass, coupling=coupling)
    weight, density = dx[:, None]*w, b/a

    def elements(value):
        return [np.sum(weight*value*f, axis=1)
                for f in ((1.-t)**2, t*(1.-t), t*t)]

    stiffness, inertia = elements(density*v), elements(density)
    derivative = np.sum(weight*a/b, axis=1)/dx**2
    stiffness[0] += derivative
    stiffness[1] -= derivative
    stiffness[2] += derivative

    def matrix(elements):
        off = elements[1]
        diagonal = np.r_[elements[0][0], elements[2][:-1]+elements[0][1:], elements[2][-1]]
        if boundary == "dirichlet":
            diagonal, off = diagonal[1:-1], off[1:-1]
        return diags((off, diagonal, off), (-1, 0, 1), format="csc")

    # This bound belongs to the quadrature-defined matrices. The kinetic
    # form is positive, and every quadrature weight in the mass form is positive.
    lower = float(np.min(v))
    return dict(coordinate=x, stiffness=matrix(stiffness), inertia=matrix(inertia),
                quadrature_potential_lower_bound=lower, boundary=boundary)


def lowest_modes(chart, domain, *, modes=3, **kwargs):
    problem = finite_element_problem(chart, domain, **kwargs)
    k, m = problem["stiffness"], problem["inertia"]
    if not isinstance(modes, (int, np.integer)) or not 1 <= modes < k.shape[0]:
        raise ValueError("positive mode count below matrix dimension required")
    lower = problem["quadrature_potential_lower_bound"]
    shift = lower-max(1., abs(lower))
    eigenvalues, vectors = eigsh(k, M=m, k=modes, sigma=shift, which="LM",
        v0=np.linspace(1., 2., k.shape[0]), tol=2e-11)
    order = np.argsort(eigenvalues)
    eigenvalues, vectors = eigenvalues[order], vectors[:, order]
    kv, mv = k@vectors, m@vectors
    residual = np.linalg.norm(kv-mv*eigenvalues, axis=0)/np.maximum(
        np.linalg.norm(kv, axis=0)+np.linalg.norm(mv*eigenvalues, axis=0), 1e-30)
    norm_error = float(abs(vectors.T@mv-np.eye(modes)).max())
    if problem["boundary"] == "dirichlet":
        vectors = np.pad(vectors, ((1, 1), (0, 0)))
    return dict(coordinate=problem["coordinate"], eigenvalues=eigenvalues,
                modes=vectors, relative_residual=residual,
                mass_orthogonality_error=norm_error,
                quadrature_potential_lower_bound=lower)


def cylinder_tensor(radius, reference_radius, reference_log, *, strength=1.):
    """Butcher Eq. (59), (rho, p_r, p_t), for strength=eta*N.

    reference_log=log(reference_radius/a0) fixes one renormalization parameter.
    Evaluating this formula at R(x) is a local cylindrical diagnostic, not the
    renormalized scalar tensor on the general rail metric.
    """
    r = np.asarray(radius, float)
    if (not np.isfinite(r).all() or np.any(r <= 0)
            or not np.isfinite([reference_radius, reference_log, strength]).all()
            or reference_radius <= 0 or strength < 0):
        raise ValueError("positive radii and finite log/nonnegative strength required")
    logarithm = np.log(r/reference_radius)+reference_log
    return strength*np.stack((-2.*logarithm, 2.*logarithm, 1.-2.*logarithm), axis=-1)/(
        2880.*np.pi**2*r[..., None]**4)


def cylindrical_indicators(chart, coordinate):
    """Dimensionless departures from constant R and A in the proper chart.

    These are diagnostic expansion parameters, not a bound on tensor error.
    """
    r, _, _, rp, rpp, ap, app = chart.jets(coordinate)
    entries = np.stack((rp, r*ap, r*rpp, r*r*(app+ap*ap)), axis=-1)
    return entries, np.max(abs(entries), axis=-1)
