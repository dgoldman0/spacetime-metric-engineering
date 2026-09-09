"""Local covariant stored-energy test of the vacuum/material tensor fits.

This is a constitutive *specialization*: vacuum and host share three
material labels phi^I and a first-derivative action -rho(B), where
B^{IJ}=g^{ab} partial_a phi^I partial_b phi^J. The quantum state and
nonlocal boundary response are absent. A failed test of this specialization
does not imply a ghost in the electromagnetic Casimir quantum state.
"""
from __future__ import annotations

import numpy as np


def voigt(matrix):
    """Independent symmetric entries xx,yy,zz,yz,xz,xy (no shear factors)."""
    matrix = np.asarray(matrix)
    return np.stack([matrix[..., 0, 0], matrix[..., 1, 1], matrix[..., 2, 2],
                     matrix[..., 1, 2], matrix[..., 0, 2], matrix[..., 0, 1]], axis=-1)


def host_energy_gradient(host):
    e, pr, pt = np.moveaxis(np.asarray(host), -1, 0)
    return .5*np.stack([e+pr, e+pt, e+pt], axis=-1)


def orientation_vector(weights):
    weights = np.asarray(weights)
    return weights[..., [0, 1, 1]]


def stored_energy(b_matrix, host, weights, host_hessian):
    """Host Taylor law plus the exact local Casimir strain law -sum C_i B_ii^2.

    At B=I the host has the fitted energy and principal pressures. Arbitrary
    second derivatives of the host represent stiffness and shear response.
    They preserve the background tensor and enter the spatial principal part.
    """
    delta = voigt(np.asarray(b_matrix)-np.eye(3))
    gradient = host_energy_gradient(host)
    host_rho = np.asarray(host)[..., 0]+np.sum(gradient*delta[..., :3], axis=-1)
    host_rho += .5*np.einsum('...i,...ij,...j->...', delta, host_hessian, delta)
    return host_rho-np.sum(orientation_vector(weights)*(1+delta[..., :3])**2, axis=-1)


def action_increment(velocity, host, weights, host_hessian, gradient=None):
    """L-L_background from the action, with cancellation-free delta B.

    Spatial gradient has indices partial_i phi^I and defaults to identity.
    The velocity is partial_t phi^I in a local orthonormal frame.
    """
    velocity = np.asarray(velocity)
    db = -np.einsum('...i,...j->...ij', velocity, velocity)
    if gradient is not None:
        dg = np.asarray(gradient)-np.eye(3)
        db = db+dg+np.swapaxes(dg, -1, -2)+np.swapaxes(dg, -1, -2)@dg
    delta = voigt(db)
    host_linear = np.sum(host_energy_gradient(host)*delta[..., :3], axis=-1)
    host_quadratic = .5*np.einsum('...i,...ij,...j->...', delta, host_hessian, delta)
    vacuum_change = -np.sum(orientation_vector(weights)*(2*delta[..., :3]+delta[..., :3]**2), axis=-1)
    return -host_linear-host_quadratic-vacuum_change


def kinetic_from_stress(channels):
    e, pr, pt = np.moveaxis(np.asarray(channels), -1, 0)
    values = np.stack([e+pr, e+pt, e+pt], axis=-1)
    return np.eye(3)*values[..., None, :]


def action_kinetic_hessian(host, weights, host_hessian, step=.02):
    """Independent velocity finite differences of L, with quartic cancellation.

    Richardson extrapolation is exact in arithmetic for this quadratic-in-B
    Taylor action. The polynomial is quartic in velocities; the procedure
    calculates the full kinetic matrix, including off-diagonal entries.
    """
    if step <= 0:
        raise ValueError('positive differentiation step required')
    shape = np.asarray(host).shape[:-1]
    def finite(h):
        result = np.zeros(shape+(3, 3))
        for i in range(3):
            vi = np.eye(3)[i]*h
            result[..., i, i] = (action_increment(vi, host, weights, host_hessian)
                +action_increment(-vi, host, weights, host_hessian))/(h*h)
            for j in range(i):
                vj = np.eye(3)[j]*h
                value = (action_increment(vi+vj, host, weights, host_hessian)
                    +action_increment(-vi-vj, host, weights, host_hessian)
                    -action_increment(vi-vj, host, weights, host_hessian)
                    -action_increment(-vi+vj, host, weights, host_hessian))/(4*h*h)
                result[..., i, j] = result[..., j, i] = value
        return result
    return (4*finite(step/2)-finite(step))/3


def stiffness_controls(scale):
    """Three fixed derivative controls; none modifies the background tensor."""
    positive = np.diag([1., 2., 3., .5, .7, .9])
    mixed = np.array([[1., .2, -.1, .3, 0., .1], [.2, -2., .1, 0., -.2, .4],
        [-.1, .1, 3., .2, .1, 0.], [.3, 0., .2, -.5, .1, .2],
        [0., -.2, .1, .1, .7, -.1], [.1, .4, 0., .2, -.1, -.9]])
    factor = np.asarray(scale)[..., None, None]
    return {'zero': factor*np.zeros((6, 6)), 'positive': factor*positive, 'mixed': factor*mixed}
