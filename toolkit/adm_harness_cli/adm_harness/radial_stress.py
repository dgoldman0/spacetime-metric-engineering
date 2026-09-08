"""Algebraic diagnostics for a spherical stress tensor with radial heat flux.

Channels refer to an orthonormal frame with signature (-+++), j=-T_01.
The full eigensystem certifier requires that spherical block structure; it
rejects tensors with additional angular flux or shear beyond its tolerance.
"""
from __future__ import annotations

import numpy as np


TYPE_I = "type_i_boost_diagonalizable"
TYPE_II = "type_ii_null_boundary"
TYPE_IV = "type_iv_flux_dominant"
UNRESOLVED = "indeterminate_radial_boundary"
ETA = np.diag([-1., 1., 1., 1.])


def classify_radial_stress(rho, pressure, current, angular, *, rtol=1e-12):
    """Classify supplied floating-point channels using a relative stress margin.

Exact diagonal blocks include vacuum and degenerate Type I. Exact nonzero
null-flux boundaries are Type II. Other rows within rtol of |rho+p|=2|j|
are explicitly unresolved. rtol concerns algebraic conditioning, while a
physical verdict also requires a separate source-discretization error study.
"""
    if not np.isfinite(rtol) or rtol < 0:
        raise ValueError("rtol must be finite and nonnegative")
    rho, pressure, current, angular = np.broadcast_arrays(
        *[np.atleast_1d(np.asarray(value, dtype=float)) for value in (rho, pressure, current, angular)]
    )
    if not all(np.isfinite(value).all() for value in (rho, pressure, current, angular)):
        raise ValueError("stress channels must be finite")
    scale = np.maximum.reduce([np.abs(rho), np.abs(pressure), np.abs(current)])
    r, p, j = [np.divide(value, scale, out=np.zeros_like(scale), where=scale > 0)
               for value in (rho, pressure, current)]
    h = r + p
    delta = (h - 2*j) * (h + 2*j)
    margin = np.abs(h) - 2*np.abs(j)
    diagonal = current == 0
    kind = np.full(rho.shape, UNRESOLVED, dtype=object)
    kind[diagonal | (margin > rtol)] = TYPE_I
    kind[(~diagonal) & (margin < -rtol)] = TYPE_IV
    kind[(~diagonal) & (margin == 0)] = TYPE_II
    type_i = kind == TYPE_I
    root = np.sqrt(np.maximum(delta, 0))
    velocity = np.full(rho.shape, np.nan)
    velocity[diagonal] = 0.
    boosted = type_i & (~diagonal)
    denominator = h + np.copysign(root, h)
    np.divide(2*j, denominator, out=velocity, where=boosted)
    if (np.abs(velocity[type_i]) >= 1).any():
        raise ArithmeticError("resolved Type-I boost is not timelike")
    energy = np.full(rho.shape, np.nan)
    radial = np.full(rho.shape, np.nan)
    energy[type_i] = .5 * scale[type_i] * (r[type_i] - p[type_i] + np.sign(h[type_i])*root[type_i])
    radial[type_i] = .5 * scale[type_i] * (p[type_i] - r[type_i] + np.sign(h[type_i])*root[type_i])
    energy[diagonal] = rho[diagonal]
    radial[diagonal] = pressure[diagonal]
    flux_ratio = np.divide(2*np.abs(j), np.abs(h), out=np.full(rho.shape, np.inf), where=h != 0)
    flux_ratio[(h == 0) & (j == 0)] = 0.
    nec = np.minimum(energy + radial, energy + angular)
    wec = np.minimum(energy, nec)
    dec = np.minimum(energy - np.abs(radial), energy - np.abs(angular))
    return {
        "stress_algebraic_type": kind,
        "classification_radial_scale": scale,
        "radial_discriminant_normalized": delta,
        "radial_type_margin_normalized": margin,
        "radial_block_discriminant": (rho + pressure)**2 - 4*current**2,
        "rho_plus_p_l": rho + pressure,
        "radial_flux_ratio": flux_ratio,
        "boost_velocity_to_flux_frame": velocity,
        "rest_frame_energy_density": energy,
        "rest_frame_radial_pressure": radial,
        "rest_frame_angular_pressure": np.where(type_i, angular, np.nan),
        "type_i_heat_flux_compatible": type_i,
        "minimal_type_i_regulator": np.maximum(-margin, 0) * scale,
        "nec_margin": nec, "wec_margin": wec, "dec_margin": dec,
        "classification_resolved": kind != UNRESOLVED,
        "exact_vacuum": (rho == 0) & (pressure == 0) & (current == 0) & (angular == 0),
    }


def radial_tensor(rho, pressure, current, angular):
    tensor = np.diag([rho, pressure, angular, angular]).astype(float)
    tensor[0, 1] = tensor[1, 0] = -current
    return tensor


def certify_radial_eigensystem(tensor, *, rtol=1e-12, symmetry_tolerance=1e-9):
    """Certify the full 4x4 mixed tensor using its causal eigenvectors.

Type I has a timelike eigenvector and a complete orthonormal eigenbasis.
Type II has a repeated null eigenvector and a nontrivial length-two Jordan
chain. Type IV has a complex pair. Eigen-equation errors are measured against
the supplied full tensor, including any numerical departures from symmetry.
"""
    tensor = np.asarray(tensor, dtype=float)
    if tensor.shape != (4, 4) or not np.isfinite(tensor).all():
        raise ValueError("a finite 4x4 orthonormal covariant tensor is required")
    if not np.isfinite(symmetry_tolerance) or symmetry_tolerance < 0:
        raise ValueError("symmetry_tolerance must be finite and nonnegative")
    magnitude = float(np.max(np.abs(tensor)))
    normalization = magnitude if magnitude > 0 else 1.
    rho, pressure = tensor[0, 0], tensor[1, 1]
    current = -.5 * (tensor[0, 1] + tensor[1, 0])
    angular = .5 * (tensor[2, 2] + tensor[3, 3])
    ideal = radial_tensor(rho, pressure, current, angular)
    symmetry_error = float(np.max(np.abs(tensor-ideal))/normalization)
    if symmetry_error > symmetry_tolerance:
        raise ValueError("tensor has angular flux/shear or asymmetry outside the spherical block tolerance")
    diagnostic = classify_radial_stress(rho, pressure, current, angular, rtol=rtol)
    kind = diagnostic["stress_algebraic_type"][0]
    mixed = ETA @ tensor / normalization
    jordan_error = None
    if kind == TYPE_I:
        velocity = diagnostic["boost_velocity_to_flux_frame"][0]
        gamma = 1/np.sqrt((1-velocity)*(1+velocity))
        vectors = np.eye(4, dtype=complex)
        vectors[:2, :2] = gamma*np.array([[1, velocity], [velocity, 1]])
        values = np.array([-diagnostic["rest_frame_energy_density"][0],
                           diagnostic["rest_frame_radial_pressure"][0], angular, angular], dtype=complex)/normalization
    elif kind == TYPE_II:
        eigenvalue = .5*(pressure-rho)/normalization
        direction = np.copysign(1., (rho+pressure)/current)
        null = np.array([1., direction, 0., 0.])/np.sqrt(2.)
        vectors = np.column_stack([null, null, np.eye(4)[:, 2], np.eye(4)[:, 3]]).astype(complex)
        values = np.array([eigenvalue, eigenvalue, angular/normalization, angular/normalization], dtype=complex)
        block = mixed - eigenvalue*np.eye(4)
        generalized = np.linalg.lstsq(block, null, rcond=None)[0]
        jordan_error = float(np.max(np.abs(block @ generalized-null)))
    else:
        values, vectors = np.linalg.eig(mixed)
        values, vectors = values.astype(complex), vectors.astype(complex)
    residual = float(np.max(np.abs(mixed @ vectors - vectors*values)) / max(float(np.max(np.abs(vectors))), 1.))
    real_vectors = np.max(np.abs(vectors.imag), axis=0) <= 1e-10
    norms = np.array([float(vectors[:, i].real @ ETA @ vectors[:, i].real) if real_vectors[i] else np.nan for i in range(4)])
    rank = int(np.linalg.matrix_rank(vectors))
    if kind == TYPE_I:
        causal_pass = bool(rank == 4 and norms[0] < 0 and np.all(norms[1:] > 0))
    elif kind == TYPE_II:
        causal_pass = bool(rank == 3 and abs(norms[0]) < 1e-10 and jordan_error < 1e-8)
    elif kind == TYPE_IV:
        causal_pass = bool(np.count_nonzero(np.abs(values.imag) > rtol) == 2)
    else:
        causal_pass = False
    certified = bool(causal_pass and residual <= max(1e-10, 4*symmetry_tolerance))
    return {
        **{key: value[0] for key, value in diagnostic.items()},
        "eigenvalues": values*normalization, "eigenvectors": vectors,
        "eigenvector_metric_norms": norms, "eigenbasis_rank": rank,
        "eigen_equation_relative_error": residual,
        "spherical_block_relative_error": symmetry_error,
        "jordan_chain_error": jordan_error,
        "full_eigensystem_certified": certified,
    }
