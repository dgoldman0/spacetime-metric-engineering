"""Local C2 receiver repair candidate for the angular-only beta075 receiver.

The frozen source kernel remains the reference implementation. This candidate
replaces its angular metric factor through an explicit scalar evaluator.
"""
from __future__ import annotations

from dataclasses import replace
from functools import lru_cache
import math

from .source_ledger import SourceParams, scalars, support_edge_receiver_radial_shape

FIELDS = (
    "alpha", "beta", "gamma_ll", "gamma_omega", "W_raw", "support_shell_window",
    "standing_support_packet_beta_rematch_window", "support_edge_receiver_memory_driver",
    "support_edge_receiver_radial_cap_window", "support_edge_receiver_angular_flange_window",
    "support_edge_receiver_angular_factor", "support_edge_receiver_delta_gamma_omega",
)


def c2_clipped_power(z: float, power: float, blend_fraction: float = .125) -> float:
    """Match clipped z**power with quintic C2 joins near zero and one.

    The supported power range (0, 2] includes the frozen square root and
    preserves monotonicity of these Hermite patches. The interval [b, 1-b]
    retains the exact power law; [0,b] joins zero value/slope/curvature to
    the power law and [1-b,1] joins it to the constant value one.
    """
    if not all(math.isfinite(value) for value in (z, power, blend_fraction)):
        raise ValueError("regularized power arguments must be finite")
    if not 0 < power <= 2:
        raise ValueError("C2 receiver power must lie in (0, 2]")
    if not 0 < blend_fraction < .5:
        raise ValueError("blend fraction must lie in (0, 0.5)")
    if z <= 0:
        return 0.
    if z >= 1:
        return 1.
    b = blend_fraction
    if z < b:
        t = z/b
        a3 = .5*(power-4)*(power-5)
        a4 = -(power-3)*(power-5)
        a5 = .5*(power-3)*(power-4)
        return b**power*t**3*(a3+t*(a4+t*a5))
    if z > 1-b:
        t = (1-z)/b
        value = (1-b)**power-1
        slope = -b*power*(1-b)**(power-1)
        curvature = b*b*power*(power-1)*(1-b)**(power-2)
        a3 = 10*value-4*slope+.5*curvature
        a4 = -15*value+7*slope-curvature
        a5 = 6*value-3*slope+.5*curvature
        return 1+t**3*(a3+t*(a4+t*a5))
    return z**power


def repaired_receiver_radial_shape(s, l, params, *, blend_fraction=.125):
    """Preserve the original shell, temporal, and packet-exclusion windows."""
    inner = params.Rth*params.support_edge_receiver_inner_multiplier
    outer = params.Rth*params.support_edge_receiver_outer_multiplier
    if not 0 < inner < outer:
        raise ValueError("receiver requires 0 < inner < outer")
    z = (abs(l)-inner)/(outer-inner)
    weight = c2_clipped_power(z, params.support_edge_receiver_outer_power, blend_fraction)
    original = support_edge_receiver_radial_shape(s, l, params)
    if z <= 0 or z >= 1 or blend_fraction <= z <= 1-blend_fraction:
        return original
    return original*(weight/z**params.support_edge_receiver_outer_power)


@lru_cache(maxsize=2048)
def repaired_receiver_scalars(s: float, l: float, params: SourceParams, *, blend_fraction=.125):
    """Supply a full candidate metric with the receiver angular factor repaired.

    The beta075 reference uses the receiver only in gamma_omega. Additional
    receiver metric channels require their own complete reconstruction, so
    this bounded repair rejects those configurations. Original diagnostic
    windows are retained except for the explicitly updated receiver fields;
    the curvature evaluator consumes alpha, beta, gamma_ll and gamma_omega.
    Only these metric and selected window fields are returned; downstream
    curvature-dependent source products must be recomputed for the candidate.
    """
    if any(getattr(params, key) != 0 for key in (
        "support_edge_receiver_lapse_log_gain", "support_edge_receiver_radial_log_gain",
        "support_edge_receiver_beta_relaxation_gain")):
        raise ValueError("this repair candidate supports the angular-only receiver")
    if params.causal_margin_guard_enabled:
        raise ValueError("candidate reconstruction requires the frozen disabled causal guard")
    original = {key: value for key, value in scalars(s, l, params).items() if key in FIELDS}
    shape = repaired_receiver_radial_shape(s, l, params, blend_fraction=blend_fraction)
    cap = original["support_edge_receiver_memory_driver"]*shape
    side = params.support_edge_receiver_angular_side.lower()
    if side in {"negative", "neg", "-", "left"}:
        flange = cap if l < 0 else 0.
    elif side in {"positive", "pos", "+", "right"}:
        flange = cap if l > 0 else 0.
    elif side in {"bilateral", "both", "all"}:
        flange = cap
    else:
        raise ValueError("unknown receiver angular side")
    # Preserve bitwise equality wherever the repaired profile is unchanged.
    if flange == original["support_edge_receiver_angular_flange_window"]:
        return original | {"support_edge_receiver_radial_cap_window": cap}
    base = scalars(s, l, replace(params, support_edge_receiver_angular_log_gain=0.))
    factor = math.exp(params.support_edge_receiver_angular_log_gain*flange)
    angular = base["gamma_omega"]*factor
    return original | {
        "gamma_omega": angular,
        "support_edge_receiver_radial_cap_window": cap,
        "support_edge_receiver_angular_flange_window": flange,
        "support_edge_receiver_angular_factor": factor,
        "support_edge_receiver_delta_gamma_omega": angular-base["gamma_omega"],
    }
