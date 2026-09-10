"""Finite disjoint scalar mirrors and their interaction opening contribution.

The interaction subtracts the two isolated-layer vacua and restores the
boundary-free one. Canonical material gradients are counted independently.
"""
from functools import lru_cache

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.linalg import solve_banded
from scipy.linalg.lapack import dpttrf


def bump(u):
    u = np.asarray(u, float)
    inside = abs(u) < 1
    safe = np.where(inside, u, 0.)
    value = np.where(inside, np.exp(-safe*safe/(1-safe*safe)), 0.)
    derivative = -2*safe*value/(1-safe*safe)**2
    return value, derivative


@lru_cache(maxsize=4)
def gradient_integral(nodes=256):
    u, weights = leggauss(nodes)
    return float(weights @ bump(u)[1]**2)


@lru_cache(maxsize=16)
def spectral_quadrature(nodes=128, lower=1e-9, upper=40.):
    x, weights = leggauss(nodes)
    low, high = np.log(lower), np.log(upper)
    k = np.exp((low+high)/2+(high-low)*x/2)
    return k, weights*(high-low)*k/2


def layer_reflection(k, potential, spacing):
    """Euclidean reflection at the front face of a finite positive layer.

    Exact constant-potential transfer in each cell propagates Y-k, where Y
    is the logarithmic derivative of the solution decaying into the left
    exterior. Complex potentials are permitted for response derivatives.
    """
    k = np.asarray(k)
    potential = np.asarray(potential)
    delta = np.zeros_like(k, dtype=np.result_type(k, potential))
    for value in potential:
        rate = np.sqrt(k*k+value)
        t = np.tanh(rate*spacing)
        delta = (delta*(rate-k*t)+value*t)/(rate+(k+delta)*t)
    return delta/(2*k+delta)


def planar_interaction(q, s, cells=256, nodes=128):
    """Dimensionless e=-a^3 E, f=a^4 F and complete interaction null stress."""
    if min(q, s) <= 0 or cells < 8 or nodes < 16:
        raise ValueError('positive shape parameters and resolved quadratures required')
    k, weights = spectral_quadrature(nodes)
    u = -1+(np.arange(cells)+.5)*2/cells
    shape = bump(u)[0]**2
    # A complex-step derivative keeps the optical-response derivative free
    # of subtraction error before assembling the stress scaling identity.
    reflection = layer_reflection(k, q*(1+1e-20j)*shape, 2*s/cells)
    roundtrip = reflection**2*np.exp(-2*k)
    binding = -np.dot(weights*k*k, np.log1p(-roundtrip))/(4*np.pi**2)
    traction = np.dot(weights*k**3, roundtrip/(1-roundtrip))/(2*np.pi**2)
    e, derivative = float(binding.real), float(binding.imag/1e-20)
    helpful = 4*e-2*derivative
    mirror = 2*q*gradient_integral()/s
    return dict(q=float(q), s=float(s), binding=e, traction=float(traction.real),
                strength_derivative=derivative, helpful_null=helpful,
                mirror_null_at_g1=mirror,
                crossing_coupling=mirror/helpful if helpful > 0 else None)


def _pivots(diagonal, links):
    pivots, _, info = dpttrf(np.array(diagonal, copy=True), -np.array(links, copy=True))
    if info:
        raise ValueError('positive Euclidean radial operator required')
    return pivots


def _shift_values(base, shifted, links, increment):
    band = np.zeros((2, len(base)))
    band[0] = 1.
    band[1, :-1] = -links**2/(base[:-1]*shifted[:-1])
    return solve_banded((1, 0), band, increment.copy(), check_finite=False)


def _pivot_tangent(pivots, links, diagonal_tangent, links_tangent):
    band = np.zeros((2, len(pivots)))
    band[0] = 1.
    band[1, :-1] = -links**2/pivots[:-1]**2
    rhs = diagonal_tangent.copy()
    rhs[1:] -= 2*links*links_tangent/pivots[:-1]
    return solve_banded((1, 0), band, rhs, check_finite=False)


def _shift_tangent(base, shifted, links, shift, db, ds, dl):
    factor = links**2/(base[:-1]*shifted[:-1])
    rhs = np.zeros_like(base)
    rhs[1:] = factor*shift[:-1]*(2*dl/links-db[:-1]/base[:-1]-ds[:-1]/shifted[:-1])
    band = np.zeros((2, len(base)))
    band[0] = 1.
    band[1, :-1] = -factor
    return solve_banded((1, 0), band, rhs, check_finite=False)


def interaction_logdet(diagonal, links, increment_left, increment_right, cut, tangent=None):
    """Stable four-operator determinant ratio for potentials separated at cut.

    Each material potential vanishes on the other side of the cut, including
    the cut itself. The left/right determinant factors cancel analytically.
    """
    if (np.any(increment_left[cut:] != 0) or np.any(increment_right[:cut+1] != 0)
            or np.any(increment_left < 0) or np.any(increment_right < 0)):
        raise ValueError('disjoint positive potentials separated by an empty cut required')
    dl, ll = diagonal[:cut+1], links[:cut]
    dr, lr = diagonal[cut:][::-1], links[cut:][::-1]
    vl, vr = increment_left[:cut+1], increment_right[cut:][::-1]
    bl, br = _pivots(dl, ll), _pivots(dr, lr)
    sl, sr = _pivots(dl+vl, ll), _pivots(dr+vr, lr)
    base = bl[-1]+br[-1]-diagonal[cut]
    xl, xr = _shift_values(bl, sl, ll, vl), _shift_values(br, sr, lr, vr)
    left, right = xl[-1], xr[-1]
    if left <= 0 or right <= 0:
        return 0. if tangent is None else (0., 0.)
    log_roundtrip = -np.log1p(base/left)-np.log1p(base/right)
    value = float(np.log(-np.expm1(log_roundtrip)))
    if tangent is None:
        return value
    dd, de = tangent
    ddl, del_ = dd[:cut+1], de[:cut]
    ddr, der = dd[cut:][::-1], de[cut:][::-1]
    dbl = _pivot_tangent(bl, ll, ddl, del_)
    dbr = _pivot_tangent(br, lr, ddr, der)
    dsl = _pivot_tangent(sl, ll, ddl, del_)
    dsr = _pivot_tangent(sr, lr, ddr, der)
    dxl = _shift_tangent(bl, sl, ll, xl, dbl, dsl, del_)[-1]
    dxr = _shift_tangent(br, sr, lr, xr, dbr, dsr, der)[-1]
    db = dbl[-1]+dbr[-1]-dd[cut]
    dlog = dxl/left+dxr/right-(db+dxl)/(base+left)-(db+dxr)/(base+right)
    odds = np.exp(log_roundtrip)/(-np.expm1(log_roundtrip))
    return value, float(-odds*dlog)
