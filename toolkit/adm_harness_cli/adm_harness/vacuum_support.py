"""Bounded Casimir tensor decomposition of a specified static support demand.

An oriented planar vacuum tensor is an algebraic comparison family. Its
nonnegative weights are optimized independently at each radius; the result
does not specify conducting boundaries, their equilibrium, or a quantum
state on the rail geometry. Those are separate constitutive requirements.
Channel order throughout this module is energy, radial pressure, angular
pressure, with the two angular pressures equal and zero net current.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np
from scipy.interpolate import CubicSpline

from .comer_two_current import fluid_moments, recover_fluid


def casimir_channels(radial_weight, angular_weight):
    """C_r for radial normals, C_t for each of two angular normals.

    This superposition allows independent sectors or separated ideal cells;
    intersecting physical cavities do not in general have additive stresses.
    """
    cr, ct = np.broadcast_arrays(radial_weight, angular_weight)
    if np.any(cr < 0) or np.any(ct < 0):
        raise ValueError('vacuum orientation weights must be nonnegative')
    return np.stack([-cr-2*ct, -3*cr+2*ct, cr-2*ct], axis=-1)


def initial_ordinary(r, fraction, drift):
    """Same finite preload and opposite initial currents as the prior round."""
    r = np.asarray(r)
    if not 0 <= fraction <= 1 or abs(drift) > .1:
        raise ValueError('bounded nonnegative preload and drift required')
    window = np.sin(np.pi*(r-2.15)/4.10)**4
    preload = .039783*fraction*(window+1e-8)/r**2
    if fraction == 0:
        return np.zeros((len(r), 3)), np.zeros((len(r), 4))
    en, es = .5*preload, .5*preload
    vn = drift*window
    jn = en*1.2*vn/(1+.2*vn*vn)
    rn, vn, _ = recover_fluid(en, jn, .2)
    rs, vs, _ = recover_fluid(es, -jn, 1/3)
    total = fluid_moments(rn, vn, .2)+fluid_moments(rs, vs, 1/3)
    return total[:, [0, 2, 3]], np.stack([rn, vn, rs, vs], axis=-1)


def decomposition_constraints(target, pressure_cap=1., radial_only=False):
    """A x <= b for C_r,C_t and |P_host| <= cap E_host, E_host >= 0."""
    target = np.asarray(target, dtype=float)
    if target.shape[-1] != 3 or not np.isfinite(target).all():
        raise ValueError('finite three-channel support demand required')
    if not 0 < pressure_cap <= 1:
        raise ValueError('pressure cap must lie in (0,1]')
    e, pr, pt = np.moveaxis(target, -1, 0)
    q = pressure_cap
    a = np.array([[-1., 0.], [0., -1.], [-1., -2.],
                  [3-q, -2-2*q], [-3-q, 2-2*q],
                  [-1-q, 2-2*q], [1-q, -2-2*q]])
    b = np.stack([0*e, 0*e, e, q*e-pr, q*e+pr, q*e-pt, q*e+pt], axis=-1)
    if radial_only:
        a = np.vstack([a, [0., 1.]])
        b = np.concatenate([b, np.zeros_like(e)[..., None]], axis=-1)
    return a, b


def minimum_vacuum_split(target, pressure_cap=1., radial_only=False):
    """Enumerate vertices of the two-variable LP, minimizing C_r+2 C_t.

    Each demand is normalized before feasibility tests. Infeasible points
    retain NaNs and an explicit false flag; they never receive a fitted
    fallback. Independent scipy.optimize.linprog checks validate this solver.
    """
    target = np.asarray(target, dtype=float)
    shape = target.shape[:-1]
    scale = np.maximum(np.max(abs(target), axis=-1), 1e-300)
    normalized = target/scale[..., None]
    a, b = decomposition_constraints(normalized, pressure_cap, radial_only)
    best = np.full(shape, np.inf)
    weights = np.full(shape+(2,), np.nan)
    for pair in combinations(range(len(a)), 2):
        matrix = a[list(pair)]
        if abs(np.linalg.det(matrix)) < 1e-13:
            continue
        x = b[..., list(pair)]@np.linalg.inv(matrix).T
        residual = x@a.T-b
        valid = np.max(residual, axis=-1) <= 2e-12
        cost = x[..., 0]+2*x[..., 1]
        use = valid & (cost < best)
        weights = np.where(use[..., None], x, weights)
        best = np.where(use, cost, best)
    feasible = np.isfinite(best)
    # Roundoff at an active positivity constraint can produce -0 or ~1e-17.
    weights = np.maximum(weights, 0.)*scale[..., None]
    vacuum = casimir_channels(weights[..., 0], weights[..., 1])
    host = target-vacuum
    margins = np.stack([host[..., 0],
        pressure_cap*host[..., 0]-abs(host[..., 1]),
        pressure_cap*host[..., 0]-abs(host[..., 2])], axis=-1)
    return {'feasible': feasible, 'weights': weights, 'vacuum': vacuum,
            'host': host, 'host_margins': margins,
            'vacuum_magnitude': weights[..., 0]+2*weights[..., 1]}


def minimum_dec_weights(target):
    """Closed-form optimum for the two-orientation DEC (cap=1) problem."""
    e, pr, pt = np.moveaxis(np.asarray(target), -1, 0)
    cr = np.maximum.reduce([0*e, -(e+pr)/4, (pt-e)/2])
    ct = np.maximum.reduce([0*e, -(e+pt)/4, (2*cr+pr-e)/4])
    return np.stack([cr, ct], axis=-1)


def static_force(r, root_f, nu_r, channels):
    """Orthonormal radial divergence for a held static diagonal tensor.

    This is the force required to hold a proposed split static, not an
    independently derived exchange law for it.
    """
    e, pr, pt = np.asarray(channels).T
    return root_f*(CubicSpline(r, pr)(r, 1)+nu_r*(e+pr)+2*(pr-pt)/r)


def supported_cell_floor(radial_weight, angular_weight):
    """Independent planar cells with their own DEC struts: E_total >= 2 S.

    Each cell's normal strut stress is 3 C and costs at least 3 C in
    volume-averaged energy, while its vacuum contributes -C. This bound
    concerns locally flat, independently supported, static cells. It is
    not a theorem about arbitrary curved, externally loaded structures.
    """
    return 2*(np.asarray(radial_weight)+2*np.asarray(angular_weight))
