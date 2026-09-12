"""Linear continuum projection with prescribed angular support and end loading.

The unknowns are support energy per material label M and physical radial
pressure p. Angular stress-volume Q, initial M, and left p are supplied.
Energy is integrated in time and momentum across radial cells. A spatial
march solves dense time blocks, avoiding a global nonlinear search.
"""
from __future__ import annotations

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.linalg import solve


def time_maps(t):
    """Values and derivatives at initial time and every interval midpoint."""
    nt = len(t)
    value = np.zeros((nt, nt)); derivative = np.zeros((nt, nt))
    value[0, 0] = 1.
    derivative[0, :2] = [-1/np.diff(t)[0], 1/np.diff(t)[0]]
    for i, dt in enumerate(np.diff(t), 1):
        value[i, i-1:i+1] = .5
        derivative[i, i-1:i+1] = [-1/dt, 1/dt]
    return value, derivative


def project_balance(t, x, coefficients, initial_energy, left_pressure, *,
                    spatial_subpanels=1, quadrature_order=4):
    """Solve the two conservation equations for a declared angular history.

    The callback supplies ell, D, lapse, v, acceleration, angular_gradient,
    log_ell_t, log_radius_t, Q, fixed_power, and fixed_force on Cartesian
    time/position arrays. Fixed divergences include every other component.
    The support absorbs -fixed_power locally; that exchange is reported.
    """
    t, x = np.asarray(t), np.asarray(x)
    nt, nx = len(t), len(x)
    if nt < 3 or nx < 3 or np.any(np.diff(t) <= 0) or np.any(np.diff(x) <= 0):
        raise ValueError('ordered time and radial grids with at least three nodes required')
    z, w = leggauss(quadrature_order)
    theta, weights = (z+1)/2, w/2
    te = (t[:-1, None]+np.diff(t)[:, None]*theta).ravel()
    ce = coefficients(te, x)
    shape = (nt-1, quadrature_order, nx)
    scale = np.diff(t)[:, None, None]*weights[None, :, None]
    work = (ce['D']*ce['log_ell_t']).reshape(shape)
    old = np.sum(scale*work*(1-theta)[None, :, None], axis=1)
    new = np.sum(scale*work*theta[None, :, None], axis=1)
    exchange = (-ce['lapse']*ce['D']*ce['fixed_power']).reshape(shape)
    angular = (-2*ce['Q']*ce['log_radius_t']).reshape(shape)
    increment = np.sum(scale*(exchange+angular), axis=1)
    b = np.asarray(initial_energy)[None, :]+np.vstack([np.zeros(nx), np.cumsum(increment, axis=0)])

    tf = np.r_[t[0], (t[:-1]+t[1:])/2]
    fractions = ((np.arange(spatial_subpanels)[:, None]+theta)/spatial_subpanels).ravel()
    wx = np.tile(weights/spatial_subpanels, spatial_subpanels)
    xq = (x[:-1, None]+np.diff(x)[:, None]*fractions).ravel()
    cf = coefficients(tf, xq)
    fshape = (nt, nx-1, len(fractions))
    measure = np.diff(x)[None, :, None]*wx[None, None, :]
    integrate = lambda a: np.sum(a.reshape(fshape)*measure, axis=2)
    integrate_basis = lambda a, side: integrate(a*np.tile(side, nx-1)[None, :])
    bodies = []
    for side in (1-fractions, fractions):
        bodies.append(dict(
            energy=integrate_basis(cf['ell']*cf['acceleration']/cf['D'], side),
            pressure=integrate_basis(cf['ell']*(cf['acceleration']+2*cf['angular_gradient']), side),
            temporal=integrate_basis(cf['ell']*cf['v']/cf['lapse'], side)))
    force_rhs = integrate(-cf['ell']*cf['fixed_force']+
                          2*cf['ell']*cf['angular_gradient']*cf['Q']/cf['D'])
    value, derivative = time_maps(t)

    def energy_map(j):
        a = np.zeros((nt, nt))
        ii = np.arange(nt-1)
        a[ii+1, ii] = -old[:, j]
        a[ii+1, ii+1] = -new[:, j]
        return np.cumsum(a, axis=0)

    p = np.empty((nt, nx)); m = np.empty((nt, nx))
    p[:, 0] = left_pressure
    left_map = energy_map(0)
    m[:, 0] = b[:, 0]+left_map@p[:, 0]
    residual = 0.; max_condition = 0.
    for j in range(nx-1):
        right_map = energy_map(j+1)
        matrices = []
        for side, sign, emap in ((0, -1., left_map), (1, 1., right_map)):
            body = bodies[side]
            a = ((sign+body['pressure'][:, j])[:, None]*value+
                 body['temporal'][:, j, None]*derivative+
                 body['energy'][:, j, None]*(value@emap))
            matrices.append(a)
        rhs = (force_rhs[:, j]-bodies[0]['energy'][:, j]*(value@b[:, j])-
               bodies[1]['energy'][:, j]*(value@b[:, j+1])-matrices[0]@p[:, j])
        p[:, j+1] = solve(matrices[1], rhs, assume_a='gen', check_finite=False)
        m[:, j+1] = b[:, j+1]+right_map@p[:, j+1]
        residual = max(residual, float(abs(matrices[1]@p[:, j+1]-rhs).max()))
        if j in (0, (nx-2)//2, nx-2):
            max_condition = max(max_condition, float(np.linalg.cond(matrices[1])))
        left_map = right_map
    local_exchange = np.sum(scale*exchange, axis=1)
    return dict(support_energy=m, radial_pressure=p, local_exchange=local_exchange,
                maximum_block_residual=residual, sampled_maximum_block_condition=max_condition)
