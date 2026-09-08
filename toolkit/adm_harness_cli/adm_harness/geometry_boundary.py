"""Frozen-geometry source evaluation for the LE demanded-tensor diagnostic."""
from __future__ import annotations

from functools import lru_cache
import math

import numpy as np

from .radial_stress import ETA, certify_radial_eigensystem, radial_tensor
from .source_ledger import SourceParams, scalars


@lru_cache(maxsize=2048)
def metric_scalars(s: float, l: float, params: SourceParams):
    # scalars also builds diagnostic windows. Reuse its identical evaluations
    # at overlapping curvature stencil points without changing the source law.
    return scalars(s, l, params)


def evaluate_demand(s, l, params, h_s, h_l, *, holding=False, h_theta=1e-4):
    """Evaluate G/8pi and certify its full orthonormal mixed eigensystem.

    Holding is a family of static controls: for each requested s, freeze
    alpha and the spatial metric at that s and set beta=0 throughout its
    spacetime neighborhood. All temporal metric derivatives then vanish.
    The finite-difference curvature equations follow source_ledger exactly;
    local metric/connection caching removes repeated stencil evaluations.
    """
    if min(h_s, h_l, h_theta) <= 0:
        raise ValueError("finite-difference steps must be positive")
    x = np.array([float(s), float(l), math.pi/2, 0.])
    steps = np.array([h_s, h_l, h_theta, 1.])
    metrics, connections = {}, {}

    def metric(position):
        key = tuple(position)
        if key not in metrics:
            sigma, ell, theta, _ = position
            fields = metric_scalars(float(s) if holding else float(sigma), float(ell), params)
            alpha, beta, radial, angular = [fields[k] for k in ("alpha", "beta", "gamma_ll", "gamma_omega")]
            if holding:
                beta = 0.
            g = np.diag([-alpha**2+radial*beta**2, radial, angular, angular*math.sin(theta)**2])
            g[0, 1] = g[1, 0] = radial*beta
            metrics[key] = g
        return metrics[key]

    def shifted(position, axis, direction):
        result = position.copy()
        result[axis] += direction*steps[axis]
        return result

    def christoffel(position):
        key = tuple(position)
        if key not in connections:
            invg = np.linalg.inv(metric(position))
            dg = [(metric(shifted(position, a, 1))-metric(shifted(position, a, -1)))/(2*steps[a])
                  if a < 3 else np.zeros((4, 4)) for a in range(4)]
            gamma = np.zeros((4, 4, 4))
            for rho in range(4):
                for mu in range(4):
                    for nu in range(4):
                        gamma[rho, mu, nu] = .5*sum(invg[rho, sig]*(dg[mu][nu, sig]+dg[nu][mu, sig]-dg[sig][mu, nu]) for sig in range(4))
            connections[key] = gamma
        return connections[key]

    g = metric(x)
    gamma = christoffel(x)
    dgamma = [(christoffel(shifted(x, a, 1))-christoffel(shifted(x, a, -1)))/(2*steps[a])
              if a < 3 else np.zeros((4, 4, 4)) for a in range(4)]
    ricci = np.zeros((4, 4))
    for mu in range(4):
        for nu in range(4):
            term1 = sum(dgamma[rho][rho, mu, nu] for rho in range(4))
            term2 = sum(dgamma[nu][rho, mu, rho] for rho in range(4))
            term3 = term4 = 0.
            for rho in range(4):
                trace = sum(gamma[sig, rho, sig] for sig in range(4))
                term3 += gamma[rho, mu, nu]*trace
                for sig in range(4):
                    term4 += gamma[sig, mu, rho]*gamma[rho, nu, sig]
            ricci[mu, nu] = term1-term2+term3-term4
    scalar = float(np.einsum("ab,ab->", np.linalg.inv(g), ricci))
    demanded = (ricci-.5*g*scalar)/(8*math.pi)
    fields = metric_scalars(float(s), float(l), params)
    alpha, beta, radial, angular = [fields[k] for k in ("alpha", "beta", "gamma_ll", "gamma_omega")]
    if holding:
        beta = 0.
    tetrad = np.diag([1/alpha, 1/math.sqrt(radial), 1/math.sqrt(angular), 1/math.sqrt(angular)])
    tetrad[1, 0] = -beta/alpha
    raw = tetrad.T @ demanded @ tetrad
    # The exact Einstein tensor has symmetric spherical block structure.
    # Nested finite differences leave an antisymmetric truncation residual.
    # Retain that residual and the raw spectrum alongside the symmetry
    # projection so refinement can test its size against the physical signal.
    tensor = radial_tensor(raw[0, 0], raw[1, 1], -.5*(raw[0, 1]+raw[1, 0]),
                           .5*(raw[2, 2]+raw[3, 3]))
    result = certify_radial_eigensystem(tensor)
    raw_values = np.linalg.eigvals(ETA @ raw).astype(complex)
    scale = max(float(np.max(np.abs(raw))), np.finfo(float).tiny)
    result.update({
        "s": float(s), "l": float(l), "holding": holding, "h_s": h_s, "h_l": h_l, "h_theta": h_theta,
        "rho": float(tensor[0, 0]), "p_l": float(tensor[1, 1]), "j_l": float(-.5*(tensor[0, 1]+tensor[1, 0])),
        "p_omega": float(.5*(tensor[2, 2]+tensor[3, 3])),
        "alpha": alpha, "beta": beta, "gamma_ll": radial, "gamma_omega": angular,
        "source_frame_frobenius": float(np.linalg.norm(tensor)),
        "imaginary_eigenvalue_scale": float(np.max(np.abs(result["eigenvalues"].imag))),
        "tensor_orthonormal": tensor,
        "raw_tensor_orthonormal": raw,
        "raw_eigenvalues": raw_values,
        "raw_imaginary_eigenvalue_scale": float(np.max(np.abs(raw_values.imag))),
        "legacy_j_l": float(-raw[1, 0]),
        "spherical_projection_absolute_error": float(np.max(np.abs(raw-tensor))),
        "spherical_projection_relative_error": float(np.max(np.abs(raw-tensor))/scale),
    })
    return result
