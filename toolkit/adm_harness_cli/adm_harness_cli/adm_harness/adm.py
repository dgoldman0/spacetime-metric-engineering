from __future__ import annotations

from copy import deepcopy

import numpy as np


def recompute_adm_fields(fields: dict[str, np.ndarray], recompute_r3: bool = False) -> dict[str, np.ndarray]:
    """Recompute ADM ledger channels for the radial active-rail metric.

    The metric convention is
        ds^2 = -alpha^2 dsigma^2 + A(dl + beta dsigma)^2 + B dOmega^2
    with A=gamma_ll and B=gamma_omega. The extrinsic-curvature convention is
    the one used by the exact-builder bundles.

    R3 is preserved by default. Turn on recompute_r3 only when a modifier changes
    gamma_ll or gamma_omega; that path uses the spherical finite-difference formula
    and should be treated as numerical rather than symbolic regeneration.
    """
    out = {k: np.array(v, copy=True) for k, v in fields.items()}
    s = out["s_grid"]
    l = out["l_grid"]
    alpha = out["alpha"]
    beta = out["beta"]
    A = out["gamma_ll"]
    B = out["gamma_omega"]

    A_s = np.gradient(A, s, axis=0, edge_order=2)
    B_s = np.gradient(B, s, axis=0, edge_order=2)
    A_l = np.gradient(A, l, axis=1, edge_order=2)
    B_l = np.gradient(B, l, axis=1, edge_order=2)
    beta_l = np.gradient(beta, l, axis=1, edge_order=2)

    K_ll = (-A_s + 2.0 * A * beta_l + A_l * beta) / (2.0 * alpha)
    K_oo = (-B_s + beta * B_l) / (2.0 * alpha)
    k_l = K_ll / A
    k_omega = K_oo / B
    K = k_l + 2.0 * k_omega

    if recompute_r3:
        r = np.sqrt(B)
        r_l = np.gradient(r, l, axis=1, edge_order=2)
        r_ll = np.gradient(r_l, l, axis=1, edge_order=2)
        R3 = -4.0 * r_ll / (A * r) + 2.0 * A_l * r_l / (A * A * r) + 2.0 * (1.0 - (r_l * r_l) / A) / (r * r)
    else:
        R3 = out.get("R3")
        if R3 is None:
            r = np.sqrt(B)
            r_l = np.gradient(r, l, axis=1, edge_order=2)
            r_ll = np.gradient(r_l, l, axis=1, edge_order=2)
            R3 = -4.0 * r_ll / (A * r) + 2.0 * A_l * r_l / (A * A * r) + 2.0 * (1.0 - (r_l * r_l) / A) / (r * r)

    rho = (R3 + K * K - (k_l * k_l + 2.0 * k_omega * k_omega)) / (16.0 * np.pi)
    k_omega_l = np.gradient(k_omega, l, axis=1, edge_order=2)
    j_l = (-2.0 * k_omega_l + (B_l / B) * (k_l - k_omega)) / (8.0 * np.pi)

    out["k_l"] = k_l
    out["k_omega"] = k_omega
    out["K"] = K
    out["R3"] = R3
    out["rho"] = rho
    out["j_l"] = j_l
    out["gtt"] = -alpha * alpha + A * beta * beta
    return out


def apply_field_delta(fields: dict[str, np.ndarray], delta: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    out = {k: np.array(v, copy=True) for k, v in fields.items()}
    for key, arr in delta.items():
        out[key] = out[key] + arr
    return out
