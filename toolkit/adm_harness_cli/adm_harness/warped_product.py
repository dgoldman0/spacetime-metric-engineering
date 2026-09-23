"""Spherical demanded tensor from the warped-product Einstein identities.

For g = g_ab dx^a dx^b + R^2 dOmega^2 on the (sigma, l) quotient,

    G_ab = -(2/R) H_ab + g_ab [(2/R) box R + ((grad R)^2 - 1)/R^2],
    G^theta_theta = box R / R - K,

where H_ab = D_a D_b R is the Hessian of the areal radius, box R its trace
and K the Gaussian curvature of g_ab. Every radial null vector k obeys
T(k, k) = -H(k, k)/(4 pi R), so the radial block is Type IV exactly where the
two radial null energies have opposite signs. Where R is constant on the
stencil the Hessian vanishes identically: rho = -p_l = 1/(8 pi R^2), j = 0,
and all two-dimensional dynamics enter the angular pressure through K.
"""
from __future__ import annotations

import math

import numpy as np

from .radial_stress import certify_radial_eigensystem, radial_tensor


def _two_metric(alpha: float, beta: float, radial: float) -> np.ndarray:
    return np.array([[-alpha*alpha+radial*beta*beta, radial*beta], [radial*beta, radial]])


def evaluate_spherical_demand(s, l, params, h_s, h_l, *, scalar_evaluator, holding=False):
    """Evaluate G/8pi through the areal-radius Hessian and certify its eigensystem.

    scalar_evaluator(sigma, ell, params) supplies alpha, beta, gamma_ll and
    gamma_omega. Derivatives use the same nested central differences as the
    frozen curvature kernel: connections from central metric differences,
    then central differences of connections and of the radius gradient.
    Holding freezes every field at sigma=s and sets beta=0, as in the
    geometry-boundary controls.
    """
    if min(h_s, h_l) <= 0 or not all(math.isfinite(x) for x in (s, l, h_s, h_l)):
        raise ValueError("finite coordinates and positive finite steps are required")
    steps = np.array([float(h_s), float(h_l)])
    cache, gradient_cache = {}, {}

    def point_fields(point):
        if point not in cache:
            sigma, ell = point
            fields = scalar_evaluator(float(s) if holding else sigma, ell, params)
            beta = 0. if holding else fields["beta"]
            radius = math.sqrt(fields["gamma_omega"])
            cache[point] = (_two_metric(fields["alpha"], beta, fields["gamma_ll"]), radius, fields)
        return cache[point]

    def shifted(point, axis, direction):
        moved = list(point)
        moved[axis] += direction*steps[axis]
        return tuple(moved)

    def gradients(point):
        if point not in gradient_cache:
            dg = [(point_fields(shifted(point, a, 1))[0]-point_fields(shifted(point, a, -1))[0])/(2*steps[a])
                  for a in range(2)]
            dr = np.array([(point_fields(shifted(point, a, 1))[1]-point_fields(shifted(point, a, -1))[1])
                           / (2*steps[a]) for a in range(2)])
            gradient_cache[point] = (dg, dr)
        return gradient_cache[point]

    def connection(point):
        g = point_fields(point)[0]
        inverse = np.linalg.inv(g)
        dg, _ = gradients(point)
        gamma = np.zeros((2, 2, 2))
        for c in range(2):
            for a in range(2):
                for b in range(2):
                    gamma[c, a, b] = .5*sum(inverse[c, d]*(dg[a][b, d]+dg[b][a, d]-dg[d][a, b]) for d in range(2))
        return gamma

    x = (float(s), float(l))
    g, radius, fields = point_fields(x)
    inverse = np.linalg.inv(g)
    gamma = connection(x)
    dgamma = [(connection(shifted(x, a, 1))-connection(shifted(x, a, -1)))/(2*steps[a]) for a in range(2)]
    _, dr = gradients(x)
    ddr = np.array([[(gradients(shifted(x, a, 1))[1][b]-gradients(shifted(x, a, -1))[1][b])/(2*steps[a])
                     for b in range(2)] for a in range(2)])
    ddr = .5*(ddr+ddr.T)
    hessian = ddr-np.einsum("cab,c->ab", gamma, dr)
    ricci = np.zeros((2, 2))
    for a in range(2):
        for b in range(2):
            ricci[a, b] = (sum(dgamma[c][c, a, b] for c in range(2))-sum(dgamma[b][c, a, c] for c in range(2))
                           + sum(gamma[c, c, d]*gamma[d, a, b] for c in range(2) for d in range(2))
                           - sum(gamma[c, b, d]*gamma[d, a, c] for c in range(2) for d in range(2)))
    gaussian = .5*float(np.einsum("ab,ab->", inverse, ricci))
    box = float(np.einsum("ab,ab->", inverse, hessian))
    gradient_squared = float(dr @ inverse @ dr)
    alpha, radial = fields["alpha"], fields["gamma_ll"]
    beta = 0. if holding else fields["beta"]
    normal = np.array([1/alpha, -beta/alpha])
    radial_unit = np.array([0., 1/math.sqrt(radial)])
    h_nn, h_ee, h_ne = (float(u @ hessian @ v) for u, v in
                        ((normal, normal), (radial_unit, radial_unit), (normal, radial_unit)))
    trace_term = 2*box/radius+(gradient_squared-1)/radius**2
    g_nn = -2*h_nn/radius-trace_term
    g_ee = -2*h_ee/radius+trace_term
    g_ne = -2*h_ne/radius
    g_angular = box/radius-gaussian
    scale = 8*math.pi
    tensor = radial_tensor(g_nn/scale, g_ee/scale, -g_ne/scale, g_angular/scale)
    result = certify_radial_eigensystem(tensor)
    result.update({
        "s": float(s), "l": float(l), "holding": holding, "h_s": float(h_s), "h_l": float(h_l),
        "rho": float(tensor[0, 0]), "p_l": float(tensor[1, 1]), "j_l": float(-tensor[0, 1]),
        "p_omega": float(tensor[2, 2]),
        "null_energy_outgoing": -(h_nn+h_ee+2*h_ne)/(4*math.pi*radius),
        "null_energy_ingoing": -(h_nn+h_ee-2*h_ne)/(4*math.pi*radius),
        "hessian_nn": h_nn, "hessian_ee": h_ee, "hessian_ne": h_ne,
        "areal_radius": radius, "radius_gradient_squared": gradient_squared,
        "gaussian_curvature": gaussian, "radius_box": box,
        "radius_constant_on_stencil": bool(np.all(dr == 0) and np.all(ddr == 0)),
        "alpha": alpha, "beta": beta, "gamma_ll": radial, "gamma_omega": fields["gamma_omega"],
        "tensor_orthonormal": tensor,
        "imaginary_eigenvalue_scale": float(np.max(np.abs(result["eigenvalues"].imag))),
    })
    return result
