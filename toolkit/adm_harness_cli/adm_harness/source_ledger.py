from __future__ import annotations

import hashlib
import json
import math
import zipfile
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


PI8 = 8.0 * math.pi
THETA0 = math.pi / 2.0

CHANNELS = {
    "neg_Tkk_radial": "negative radial null contraction",
    "abs_p_l": "radial pressure magnitude",
    "abs_pOmega": "angular pressure magnitude",
    "abs_j_l": "radial current magnitude",
    "neg_rho_euler": "negative Eulerian density",
    "neg_rho_packet": "negative packet-comoving density",
}

STAGE_ORDER = [
    "pre_entry_setup",
    "entry_precatch",
    "catch_rematch",
    "held_carry",
    "release_shift_fade",
    "post_release_buffer",
    "reset_decompression",
]


def _token(value: float) -> str:
    text = f"{float(value):.10g}"
    return text.replace("-", "m").replace("+", "").replace(".", "p").replace("e", "e")


@dataclass(frozen=True)
class SourceParams:
    """Metric and ledger knobs for the 4D demanded-source harness.

    Keep this class aligned with the "SourceParams Reference" section in the
    README. The fields are grouped by the service subsystem they control:
    baseline packet/catch kinematics, standing support geometry, carried shift
    release, angular throat capacity, live-packet accounting, support-shell
    overlays, and packet-local redesign controls.
    """

    # Packet and service speed. V is the main service/load factor; Rpass
    # defines the modeled packet tube used by both geometry and accounting.
    V: float = 5.0
    v_exit: float = 0.5
    p_beta: float = 4.0
    Rpass: float = 0.35

    # Catch/rematch timing. The support-side beta catch may lead the packet
    # rematch; widths set the temporal transition scales.
    x_catch_beta: float = -0.05
    w_catch_beta: float = 0.32
    x_catch_packet: float = 0.00
    w_catch_packet: float = 0.32
    catch_profile: str = "minjerk"

    # Standing support plant. These fields define the support bump, radial rail
    # stretch/lapse scale, throat radius, packet transition width, and numerical
    # regularization used in packet-window formulas.
    C0: float = 100.0
    lam: float = 6.0
    B0: float = 8.0
    eta_N: float = 2.0
    Rth: float = 1.75
    w_th: float = 0.569
    w_th_inner: float | None = None
    w_th_outer: float | None = None
    w_pass: float = 0.06
    eps: float = 1.0e-5

    # Carrying-flow release and support decompression schedule.
    x_beta: float = 0.70
    w_beta: float = 0.18
    q_t0: float = -0.40
    q_Tr: float = 3.00
    release_choreography_mode: str = "legacy"
    release_matched_hold_widths: float = 0.0
    release_beta_profile: str = "tanh"
    release_beta_width_multiplier: float = 1.0
    release_lapse_lag_widths: float = 0.0
    release_carve_lag_widths: float = 0.0

    # Angular/throat-capacity jacket. These fields shape the gamma_omega
    # channel independently from the radial support bump.
    aOmega: float = 0.20
    ROmega: float = 1.75
    wOmega: float = 1.40
    xOmega: float = 2.00
    wtOmega: float = 0.60

    # Live-packet accounting window. The optional start lets extended-domain
    # service screens separate prepared entry infrastructure from live entry.
    live_packet_start: float | None = None
    live_packet_end_margin_widths: float = 2.0

    # Support-shell overlay: an infrastructure-local carrying-flow actuator
    # plus optional metric partners on alpha, gamma_ll, and gamma_omega.
    # Disabled by default so regenerated reference ledgers match old bundles.
    support_shell_overlay_enabled: bool = False
    support_shell_amplitude: float = 1.0e-7
    support_shell_catch_lead: float = 1.0
    support_shell_temporal_width: float = 0.35
    support_shell_temporal_profile: str = "gaussian"
    support_shell_temporal_shoulder: float | None = None
    support_shell_radial_profile: str = "smooth_box"
    support_shell_smoothness_order: int = 1
    support_shell_inner_multiplier: float = 0.65
    support_shell_radial_multiplier: float = 1.20
    support_shell_radial_width: float | None = None
    support_shell_packet_exclusion: float = 1.0
    support_shell_time_anchor: float | None = None
    support_shell_catch_edge_width: float | None = None
    support_shell_clock_lapse_log_gain: float = 0.0
    support_shell_rail_stretch_log_gain: float = 0.0
    support_shell_throat_capacity_log_gain: float = 0.0

    # Beta-memory support-edge receiver: a non-live endpoint layer driven by
    # accumulated beta release rather than instantaneous release slope alone.
    support_edge_receiver_enabled: bool = False
    support_edge_receiver_memory_reference_width: float = 0.25
    support_edge_receiver_memory_gain: float = 1.0
    support_edge_receiver_post_release_widths: float = 2.0
    support_edge_receiver_inner_multiplier: float = 0.65
    support_edge_receiver_outer_multiplier: float = 1.20
    support_edge_receiver_radial_width: float | None = None
    support_edge_receiver_outer_power: float = 1.0
    support_edge_receiver_packet_exclusion: float = 1.0
    support_edge_receiver_lapse_log_gain: float = 0.0
    support_edge_receiver_radial_log_gain: float = 0.0
    support_edge_receiver_beta_relaxation_gain: float = 0.0
    support_edge_receiver_angular_log_gain: float = 0.0
    support_edge_receiver_angular_side: str = "positive"

    # Packet-local redesign controls. These edit the standing support under or
    # around the packet tube, then optionally compensate causal margin through
    # alpha or beta channels using independent packet-window footprints.
    standing_support_packet_exclusion: float = 0.0
    standing_support_packet_exclusion_radius_multiplier: float = 1.0
    standing_support_packet_exclusion_width_multiplier: float = 1.0
    standing_support_packet_exclusion_schedule: str = "live_only"
    standing_support_packet_exclusion_temporal_profile: str = "tanh"
    standing_support_packet_exclusion_catch: float = 0.0
    standing_support_packet_exclusion_catch_radius_multiplier: float = 1.0
    standing_support_packet_exclusion_catch_width_multiplier: float = 1.0
    standing_support_packet_exclusion_catch_schedule: str = "catch_only"
    standing_support_packet_exclusion_catch_temporal_profile: str = "tanh"
    standing_support_packet_exclusion_shoulder: float = 0.0
    standing_support_packet_exclusion_shoulder_mode: str = "filled"
    standing_support_packet_exclusion_shoulder_radius_multiplier: float = 1.4
    standing_support_packet_exclusion_shoulder_width_multiplier: float = 1.8
    standing_support_packet_exclusion_shoulder_schedule: str = "live_only"
    standing_support_packet_exclusion_shoulder_temporal_profile: str = "tanh"
    standing_support_packet_lapse_log_gain: float = 0.0
    standing_support_packet_lapse_radius_multiplier: float = 1.0
    standing_support_packet_lapse_width_multiplier: float = 1.0
    standing_support_packet_lapse_schedule: str = "live_only"
    standing_support_packet_lapse_temporal_profile: str = "tanh"
    standing_support_packet_null_cushion_log_gain: float = 0.0
    standing_support_packet_null_cushion_mode: str = "filled"
    standing_support_packet_null_cushion_inner_radius_multiplier: float = 1.0
    standing_support_packet_null_cushion_radius_multiplier: float = 1.7
    standing_support_packet_null_cushion_width_multiplier: float = 2.0
    standing_support_packet_null_cushion_schedule: str = "catch_only"
    standing_support_packet_null_cushion_temporal_profile: str = "tanh"
    standing_support_packet_smooth_split_enabled: bool = False
    standing_support_packet_smooth_split_entry_carve: float = 0.0
    standing_support_packet_smooth_split_catch_carve: float = 0.0
    standing_support_packet_smooth_split_edge_carve: float = 0.0
    standing_support_packet_smooth_split_entry_radius_multiplier: float = 1.0
    standing_support_packet_smooth_split_entry_width_multiplier: float = 1.0
    standing_support_packet_smooth_split_catch_radius_multiplier: float = 1.0
    standing_support_packet_smooth_split_catch_width_multiplier: float = 1.0
    standing_support_packet_smooth_split_edge_inner_radius_multiplier: float = 1.0
    standing_support_packet_smooth_split_edge_outer_radius_multiplier: float = 1.7
    standing_support_packet_smooth_split_edge_width_multiplier: float = 2.2
    standing_support_packet_smooth_split_entry_schedule: str = "live_only"
    standing_support_packet_smooth_split_catch_schedule: str = "catch_only"
    standing_support_packet_smooth_split_edge_schedule: str = "catch_only"
    standing_support_packet_smooth_split_temporal_profile: str = "minimum_jerk"
    standing_support_packet_smooth_split_temporal_width_multiplier: float = 1.0
    standing_support_packet_smooth_split_radial_profile: str = "tanh"
    standing_support_packet_smooth_split_composition: str = "smooth_union"
    standing_support_packet_smooth_split_null_cushion_log_gain: float = 0.0
    standing_support_packet_smooth_split_current_guard_fraction: float = 0.0
    standing_support_packet_smooth_split_current_guard_inner_radius_multiplier: float = 1.0
    standing_support_packet_smooth_split_current_guard_outer_radius_multiplier: float = 1.7
    standing_support_packet_smooth_split_current_guard_width_multiplier: float = 2.2
    standing_support_packet_smooth_split_current_guard_schedule: str = "catch_only"
    standing_support_packet_smooth_split_current_guard_temporal_width_multiplier: float = 1.0
    standing_support_packet_smooth_split_current_guard_mode: str = "attenuate"
    standing_support_packet_smooth_split_angular_log_gain: float = 0.0
    standing_support_packet_coupled_profile_enabled: bool = False
    standing_support_packet_coupled_entry_carve: float = 0.0
    standing_support_packet_coupled_catch_carve: float = 0.0
    standing_support_packet_coupled_edge_carve: float = 0.0
    standing_support_packet_coupled_radius_multiplier: float = 1.0
    standing_support_packet_coupled_width_multiplier: float = 1.6
    standing_support_packet_coupled_entry_schedule: str = "live_only"
    standing_support_packet_coupled_catch_schedule: str = "catch_only"
    standing_support_packet_coupled_temporal_profile: str = "minimum_jerk"
    standing_support_packet_coupled_edge_inner_radius_multiplier: float = 1.0
    standing_support_packet_coupled_edge_outer_radius_multiplier: float = 1.7
    standing_support_packet_coupled_edge_width_multiplier: float = 2.2
    standing_support_packet_coupled_rebate_fraction: float = 0.0
    standing_support_packet_coupled_radial_log_gain: float = 0.0
    standing_support_packet_coupled_null_cushion_log_gain: float = 0.0
    standing_support_packet_radial_log_gain: float = 0.0
    standing_support_packet_radial_radius_multiplier: float = 1.0
    standing_support_packet_radial_width_multiplier: float = 1.0
    standing_support_packet_radial_schedule: str = "live_only"
    standing_support_packet_radial_temporal_profile: str = "tanh"
    standing_support_packet_radial_shoulder_log_gain: float = 0.0
    standing_support_packet_radial_shoulder_mode: str = "annular"
    standing_support_packet_radial_shoulder_radius_multiplier: float = 1.5
    standing_support_packet_radial_shoulder_width_multiplier: float = 2.0
    standing_support_packet_radial_shoulder_schedule: str = "live_only"
    standing_support_packet_radial_shoulder_temporal_profile: str = "tanh"
    standing_support_packet_radial_skirt_log_gain: float = 0.0
    standing_support_packet_radial_skirt_mode: str = "annular"
    standing_support_packet_radial_skirt_inner_radius_multiplier: float = 2.4
    standing_support_packet_radial_skirt_radius_multiplier: float = 2.6
    standing_support_packet_radial_skirt_width_multiplier: float = 3.6
    standing_support_packet_radial_skirt_schedule: str = "live_only"
    standing_support_packet_radial_skirt_temporal_profile: str = "tanh"
    standing_support_packet_beta_rematch_gain: float = 0.0
    standing_support_packet_beta_rematch_shape: str = "core"
    standing_support_packet_beta_rematch_radius_multiplier: float = 1.0
    standing_support_packet_beta_rematch_width_multiplier: float = 1.0
    standing_support_packet_beta_rematch_inner_radius_multiplier: float = 0.85
    standing_support_packet_beta_rematch_outer_radius_multiplier: float = 1.10
    standing_support_packet_beta_rematch_edge_softness: float = 1.0
    standing_support_packet_beta_rematch_temporal_width_multiplier: float = 1.0
    standing_support_packet_beta_rematch_temporal_profile: str = "tanh"
    standing_support_packet_beta_rematch_center_floor: float = 0.0
    standing_support_packet_beta_rematch_floor_mode: str = "max"
    standing_support_packet_beta_rematch_schedule: str = "live_only"
    causal_margin_guard_enabled: bool = False
    causal_margin_guard_margin: float = 0.05
    causal_margin_guard_strength: float = 1.0
    causal_margin_guard_window_mode: str = "packet"
    causal_margin_guard_radius_multiplier: float = 1.0
    causal_margin_guard_width_multiplier: float = 1.0
    causal_margin_guard_schedule: str = "live_only"
    causal_margin_guard_temporal_width_multiplier: float = 1.0
    causal_margin_guard_temporal_profile: str = "tanh"
    causal_margin_guard_radial_profile: str = "tanh"


@dataclass(frozen=True)
class SourceCase:
    name: str
    params: SourceParams
    note: str


def smoothstep_minjerk(t: np.ndarray | float) -> np.ndarray:
    x = np.clip(np.asarray(t, dtype=float), 0.0, 1.0)
    return 10.0 * x**3 - 15.0 * x**4 + 6.0 * x**5


def smoothstep7(t: np.ndarray | float) -> np.ndarray:
    x = np.clip(np.asarray(t, dtype=float), 0.0, 1.0)
    return 35.0 * x**4 - 84.0 * x**5 + 70.0 * x**6 - 20.0 * x**7


def smoothstep_profile(t: np.ndarray | float, profile: str) -> np.ndarray:
    key = profile.strip().lower()
    if key in {"minimum_jerk", "minjerk", "smoothstep5"}:
        return smoothstep_minjerk(t)
    if key == "smoothstep7":
        return smoothstep7(t)
    raise ValueError(f"Unknown smoothstep profile: {profile}")


def minjerk_down_window(s: np.ndarray | float, x: float, w: float) -> np.ndarray:
    t = (np.asarray(s, dtype=float) - (x - 2.0 * w)) / max(4.0 * w, 1.0e-12)
    return 1.0 - smoothstep_minjerk(t)


def falloff(z: np.ndarray | float, w: float) -> np.ndarray:
    return 0.5 * (1.0 - np.tanh(np.asarray(z, dtype=float) / w))


def catch_factor(s: np.ndarray | float, x: float, w: float, profile: str = "minjerk") -> np.ndarray:
    if profile == "minjerk":
        return minjerk_down_window(s, x, w)
    if profile == "tanh":
        return falloff(np.asarray(s, dtype=float) - x, w)
    raise ValueError(f"Unknown catch profile: {profile}")


def minjerk_down(s: np.ndarray | float, t0: float, tr: float) -> np.ndarray:
    t = (np.asarray(s, dtype=float) - t0) / max(tr, 1.0e-12)
    return 1.0 - smoothstep_minjerk(t)


def release_choreography_enabled(params: SourceParams) -> bool:
    return params.release_choreography_mode.strip().lower() not in {"legacy", "off", "none"}


def release_beta_interval(params: SourceParams, lag_widths: float = 0.0) -> tuple[float, float]:
    start = params.x_beta + (float(params.release_matched_hold_widths) + float(lag_widths)) * params.w_beta
    duration = max(4.0 * params.w_beta * float(params.release_beta_width_multiplier), 1.0e-12)
    return start, start + duration


def release_profile_down(s: np.ndarray | float, params: SourceParams, lag_widths: float = 0.0) -> np.ndarray:
    values = np.asarray(s, dtype=float)
    if not release_choreography_enabled(params):
        return falloff(values - (params.x_beta + float(lag_widths) * params.w_beta), params.w_beta)

    start, end = release_beta_interval(params, lag_widths=lag_widths)
    duration = max(end - start, 1.0e-12)
    profile = params.release_beta_profile.strip().lower()
    if profile == "tanh":
        return falloff(values - 0.5 * (start + end), duration / 4.0)

    t = (values - start) / duration
    if profile in {"minimum_jerk", "minjerk", "smoothstep5"}:
        return 1.0 - smoothstep_minjerk(t)
    if profile == "smoothstep7":
        return 1.0 - smoothstep7(t)
    raise ValueError(f"Unknown release beta profile: {params.release_beta_profile}")


def release_beta_fade_end(params: SourceParams) -> float:
    if not release_choreography_enabled(params):
        return params.x_beta + 2.0 * params.w_beta
    _start, end = release_beta_interval(params)
    return end


def live_packet_end(params: SourceParams) -> float:
    if not release_choreography_enabled(params):
        return params.x_beta + params.live_packet_end_margin_widths * params.w_beta
    return release_beta_fade_end(params) + params.live_packet_end_margin_widths * params.w_beta


def bump_sq(x2: np.ndarray | float, radius: float, width: float) -> np.ndarray:
    z = (np.asarray(x2, dtype=float) - radius * radius) / max(2.0 * radius * width, 1.0e-12)
    return 0.5 * (1.0 - np.tanh(z))


def compact_bump_sq(x2: np.ndarray | float, radius: float, width: float, profile: str) -> np.ndarray:
    z = (np.asarray(x2, dtype=float) - radius * radius) / max(2.0 * radius * width, 1.0e-12)
    t = 0.5 * (z + 1.0)
    key = profile.strip().lower()
    if key in {"compact_minjerk", "compact_smoothstep5"}:
        transition = smoothstep_minjerk(t)
    elif key in {"compact_smoothstep7", "compact_jerk_limited"}:
        transition = smoothstep7(t)
    else:
        raise ValueError(f"Unknown compact packet radial profile: {profile}")
    return np.where(z <= -1.0, 1.0, np.where(z >= 1.0, 0.0, 1.0 - transition))


def packet_bump_sq(x2: np.ndarray | float, radius: float, width: float, profile: str = "tanh") -> np.ndarray:
    key = profile.strip().lower()
    if key == "tanh":
        return bump_sq(x2, radius, width)
    return compact_bump_sq(x2, radius, width, key)


def support_bump(l: np.ndarray | float, params: SourceParams) -> np.ndarray:
    l_arr = np.asarray(l, dtype=float)
    if params.w_th_inner is None or params.w_th_outer is None:
        return bump_sq(l_arr * l_arr, params.Rth, params.w_th)
    al = np.abs(l_arr)
    width = np.where(al <= params.Rth, params.w_th_inner, params.w_th_outer)
    return bump_sq(l_arr * l_arr, params.Rth, width)


def smooth_box(x: np.ndarray | float, lo: float, hi: float, edge_width: float) -> np.ndarray:
    values = np.asarray(x, dtype=float)
    edge = max(float(edge_width), 1.0e-12)
    left = 1.0 - falloff(values - lo, edge)
    right = falloff(values - hi, edge)
    return np.clip(left * right, 0.0, 1.0)


def temporal_rise(s: np.ndarray | float, x: float, w: float, profile: str) -> np.ndarray:
    values = np.asarray(s, dtype=float)
    key = profile.strip().lower()
    if key == "tanh":
        return 1.0 - falloff(values - x, w)
    t = (values - (x - 2.0 * w)) / max(4.0 * w, 1.0e-12)
    return smoothstep_profile(t, key)


def temporal_fall(s: np.ndarray | float, x: float, w: float, profile: str) -> np.ndarray:
    values = np.asarray(s, dtype=float)
    key = profile.strip().lower()
    if key == "tanh":
        return falloff(values - x, w)
    t = (values - (x - 2.0 * w)) / max(4.0 * w, 1.0e-12)
    return 1.0 - smoothstep_profile(t, key)


def temporal_box(s: np.ndarray | float, lo: float, hi: float, edge_width: float, profile: str) -> np.ndarray:
    values = np.asarray(s, dtype=float)
    key = profile.strip().lower()
    if key == "tanh":
        return smooth_box(values, lo, hi, edge_width)
    edge = max(float(edge_width), 1.0e-12)
    return np.clip(temporal_rise(values, lo, edge, key) * temporal_fall(values, hi, edge, key), 0.0, 1.0)


def raised_cosine_compact(distance: np.ndarray | float, radius: float) -> np.ndarray:
    values = np.asarray(distance, dtype=float)
    scale = max(float(radius), 1.0e-12)
    x = np.clip(values / scale, 0.0, 1.0)
    window = 0.5 * (1.0 + np.cos(math.pi * x))
    return np.where(values <= scale, window, 0.0)


def minjerk_compact(distance: np.ndarray | float, radius: float) -> np.ndarray:
    values = np.asarray(distance, dtype=float)
    scale = max(float(radius), 1.0e-12)
    x = np.clip(values / scale, 0.0, 1.0)
    window = 1.0 - smoothstep_minjerk(x)
    return np.where(values <= scale, window, 0.0)


def support_shell_radial_window(abs_l: np.ndarray | float, inner: float, outer: float, width: float, profile: str) -> np.ndarray:
    profile_key = profile.strip().lower()
    values = np.asarray(abs_l, dtype=float)
    if profile_key == "smooth_box":
        return smooth_box(values, inner, outer, width)

    center = 0.5 * (inner + outer)
    default_half_width = max(0.5 * (outer - inner), 1.0e-12)
    if profile_key == "gaussian_annulus":
        sigma = max(float(width), default_half_width / 2.0, 1.0e-12)
        return np.exp(-0.5 * ((values - center) / sigma) ** 2)
    if profile_key == "raised_cosine_annulus":
        half_width = max(float(width), default_half_width, 1.0e-12)
        return raised_cosine_compact(np.abs(values - center), half_width)
    raise ValueError(f"Unknown support-shell radial profile: {profile}")


def support_shell_temporal_window(
    s: np.ndarray | float,
    center: float,
    width: float,
    catch_lo: float,
    catch_hi: float,
    profile: str,
    shoulder: float | None,
) -> np.ndarray:
    values = np.asarray(s, dtype=float)
    scale = max(float(width), 1.0e-12)
    closest_in_catch = min(max(center, catch_lo), catch_hi)
    profile_key = profile.strip().lower()

    if profile_key == "gaussian":
        temporal = np.exp(-0.5 * ((values - center) / scale) ** 2)
        temporal_norm = math.exp(-0.5 * ((closest_in_catch - center) / scale) ** 2)
        return np.clip(temporal / max(temporal_norm, 1.0e-12), 0.0, 1.0)

    distance_to_catch = abs(closest_in_catch - center)
    compact_radius = max(distance_to_catch + scale, 1.0e-12)
    raw_distance = np.abs(values - center)
    norm_distance = abs(closest_in_catch - center)

    if profile_key == "raised_cosine":
        temporal = raised_cosine_compact(raw_distance, compact_radius)
        temporal_norm = float(raised_cosine_compact(norm_distance, compact_radius))
    elif profile_key == "minjerk_pulse":
        temporal = minjerk_compact(raw_distance, compact_radius)
        temporal_norm = float(minjerk_compact(norm_distance, compact_radius))
    elif profile_key == "smooth_box":
        edge = max(float(shoulder) if shoulder is not None else scale / 4.0, 1.0e-12)
        temporal = smooth_box(raw_distance, 0.0, compact_radius, edge)
        temporal_norm = float(smooth_box(norm_distance, 0.0, compact_radius, edge))
    else:
        raise ValueError(f"Unknown support-shell temporal profile: {profile}")
    return np.clip(temporal / max(temporal_norm, 1.0e-12), 0.0, 1.0)


def support_shell_overlay_window(s: float, l: float, params: SourceParams) -> float:
    if not params.support_shell_overlay_enabled:
        return 0.0

    s_arr = np.asarray(s, dtype=float)
    l_arr = np.asarray(l, dtype=float)

    support_inner = params.Rth * params.support_shell_inner_multiplier
    support_outer = params.Rth * params.support_shell_radial_multiplier
    if support_inner >= support_outer:
        raise ValueError("support-shell inner multiplier must be smaller than outer multiplier")
    default_radial_width = max((support_outer - support_inner) / 8.0, 1.0e-12)
    support_width = params.support_shell_radial_width if params.support_shell_radial_width is not None else default_radial_width
    support = support_shell_radial_window(
        np.abs(l_arr),
        support_inner,
        support_outer,
        support_width,
        params.support_shell_radial_profile,
    )

    catch_width = max(params.w_catch_packet, params.w_catch_beta)
    lo = params.x_catch_packet - 2.0 * catch_width
    hi = params.x_catch_packet + 2.0 * catch_width
    edge_width = params.support_shell_catch_edge_width if params.support_shell_catch_edge_width is not None else catch_width / 4.0
    catch = smooth_box(s_arr, lo, hi, edge_width)

    anchor = params.support_shell_time_anchor
    if anchor is None:
        anchor = params.x_catch_packet
    center = float(anchor) - params.support_shell_catch_lead
    temporal_width = max(float(params.support_shell_temporal_width), 1.0e-12)
    temporal = support_shell_temporal_window(
        s_arr,
        center,
        temporal_width,
        lo,
        hi,
        params.support_shell_temporal_profile,
        params.support_shell_temporal_shoulder,
    )

    packet = bump_sq((l_arr - s_arr) ** 2 + params.eps * params.eps, params.Rpass, params.w_pass)
    live_end = live_packet_end(params)
    live_schedule = falloff(s_arr - live_end, params.w_beta)
    packet_exclusion = np.clip(1.0 - params.support_shell_packet_exclusion * packet * live_schedule, 0.0, 1.0)

    window = support * catch * temporal * packet_exclusion
    for _ in range(max(0, int(params.support_shell_smoothness_order))):
        window = smoothstep_minjerk(window)
    return float(np.clip(window, 0.0, 1.0))


def support_shell_delta_beta(s: float, l: float, params: SourceParams) -> float:
    if not params.support_shell_overlay_enabled:
        return 0.0
    return float(params.support_shell_amplitude) * support_shell_overlay_window(s, l, params)


def support_shell_metric_factor(log_gain: float, window: float) -> float:
    return float(math.exp(float(log_gain) * float(window)))


def support_edge_receiver_active(params: SourceParams) -> bool:
    return bool(params.support_edge_receiver_enabled)


def support_edge_receiver_memory_driver(s: float, params: SourceParams) -> float:
    if not support_edge_receiver_active(params):
        return 0.0
    width_excess = (
        float(params.release_beta_width_multiplier)
        - float(params.support_edge_receiver_memory_reference_width)
    )
    strength = max(width_excess, 0.0) * max(float(params.support_edge_receiver_memory_gain), 0.0)
    if strength <= 0.0:
        return 0.0

    release_complete = 1.0 - float(release_profile_down(float(s), params))
    _start, release_end = release_beta_interval(params)
    post_width = max(float(params.support_edge_receiver_post_release_widths), 0.0) * float(params.w_beta)
    fade_width = max(2.0 * float(params.w_beta), 1.0e-12)
    t = (float(s) - (release_end + post_width)) / fade_width
    persistence = 1.0 - float(smoothstep_minjerk(t))
    return float(np.clip(strength * release_complete * persistence, 0.0, 1.0))


def support_edge_receiver_radial_shape(s: float, l: float, params: SourceParams) -> float:
    if not support_edge_receiver_active(params):
        return 0.0
    inner = float(params.Rth) * float(params.support_edge_receiver_inner_multiplier)
    outer = float(params.Rth) * float(params.support_edge_receiver_outer_multiplier)
    if inner >= outer:
        raise ValueError("support-edge receiver inner multiplier must be smaller than outer multiplier")
    default_width = max((outer - inner) / 8.0, 1.0e-12)
    width = (
        float(params.support_edge_receiver_radial_width)
        if params.support_edge_receiver_radial_width is not None
        else default_width
    )
    abs_l = abs(float(l))
    support = support_shell_radial_window(abs_l, inner, outer, width, "smooth_box")
    span = max(outer - inner, 1.0e-12)
    outer_weight = np.clip((abs_l - inner) / span, 0.0, 1.0)
    power = max(float(params.support_edge_receiver_outer_power), 0.0)
    outer_weight = float(outer_weight**power) if power else 1.0

    packet = float(bump_sq((float(l) - float(s)) ** 2 + params.eps * params.eps, params.Rpass, params.w_pass))
    live_schedule = float(falloff(float(s) - live_packet_end(params), params.w_beta))
    packet_exclusion = np.clip(
        1.0 - float(params.support_edge_receiver_packet_exclusion) * packet * live_schedule,
        0.0,
        1.0,
    )
    non_live = 0.0 if live_packet_mask(float(s), float(l), params) else 1.0
    return float(np.clip(support * outer_weight * packet_exclusion * non_live, 0.0, 1.0))


def support_edge_receiver_radial_cap_window(s: float, l: float, params: SourceParams) -> float:
    memory = support_edge_receiver_memory_driver(s, params)
    if memory <= 0.0:
        return 0.0
    return float(np.clip(memory * support_edge_receiver_radial_shape(s, l, params), 0.0, 1.0))


def support_edge_receiver_angular_flange_window(s: float, l: float, params: SourceParams) -> float:
    radial = support_edge_receiver_radial_cap_window(s, l, params)
    if radial <= 0.0:
        return 0.0
    side = params.support_edge_receiver_angular_side.strip().lower()
    if side in {"bilateral", "both", "all"}:
        side_weight = 1.0
    elif side in {"positive", "pos", "+", "right"}:
        side_weight = 1.0 if float(l) > 0.0 else 0.0
    elif side in {"negative", "neg", "-", "left"}:
        side_weight = 1.0 if float(l) < 0.0 else 0.0
    else:
        raise ValueError(f"Unknown support-edge receiver angular side: {params.support_edge_receiver_angular_side}")
    return float(np.clip(radial * side_weight, 0.0, 1.0))


def smooth_union(*values: float) -> float:
    complement = 1.0
    for value in values:
        complement *= 1.0 - float(np.clip(value, 0.0, 1.0))
    return float(np.clip(1.0 - complement, 0.0, 1.0))


def compose_packet_windows(values: tuple[float, ...], mode: str) -> float:
    key = mode.strip().lower()
    if key in {"smooth_union", "union"}:
        return smooth_union(*values)
    if key in {"additive", "linear", "linear_clip"}:
        return float(np.clip(sum(float(value) for value in values), 0.0, 1.0))
    raise ValueError(f"Unknown packet window composition mode: {mode}")


def standing_support_packet_temporal_schedule(
    s: float,
    params: SourceParams,
    *,
    schedule_name: str,
    temporal_width_multiplier: float = 1.0,
    temporal_profile: str = "tanh",
    release_lag_widths: float = 0.0,
) -> float:
    s_arr = np.asarray(s, dtype=float)
    schedule_key = schedule_name.strip().lower()
    live_end = live_packet_end(params)
    temporal_width = max(float(params.w_beta) * float(temporal_width_multiplier), 1.0e-12)
    if schedule_key == "live_only":
        schedule = temporal_fall(s_arr, live_end, temporal_width, temporal_profile)
    elif schedule_key == "coordinated_release":
        catch_width = max(params.w_catch_packet, params.w_catch_beta) * float(temporal_width_multiplier)
        lo = params.x_catch_packet - 0.75 * catch_width
        onset = temporal_rise(s_arr, lo, max(temporal_width / 2.0, 1.0e-12), temporal_profile)
        schedule = onset * release_profile_down(s_arr, params, lag_widths=release_lag_widths)
    elif schedule_key == "entry_catch_release":
        catch_width = max(params.w_catch_packet, params.w_catch_beta) * float(temporal_width_multiplier)
        lo = params.x_catch_packet - 2.0 * catch_width
        hi = live_end
        schedule = temporal_box(s_arr, lo, hi, max(temporal_width / 2.0, 1.0e-12), temporal_profile)
    elif schedule_key == "catch_release":
        catch_width = max(params.w_catch_packet, params.w_catch_beta) * float(temporal_width_multiplier)
        lo = params.x_catch_packet - 0.75 * catch_width
        hi = live_end
        schedule = temporal_box(s_arr, lo, hi, max(temporal_width / 2.0, 1.0e-12), temporal_profile)
    elif schedule_key == "catch_only":
        catch_width = max(params.w_catch_packet, params.w_catch_beta) * float(temporal_width_multiplier)
        lo = params.x_catch_packet - 2.0 * catch_width
        hi = params.x_catch_packet + 2.0 * catch_width
        schedule = temporal_box(s_arr, lo, hi, max(temporal_width / 2.0, 1.0e-12), temporal_profile)
    elif schedule_key == "always":
        schedule = np.asarray(1.0, dtype=float)
    else:
        raise ValueError(f"Unknown standing support packet schedule: {schedule_name}")
    return float(np.clip(schedule, 0.0, 1.0))


def standing_support_packet_window(
    s: float,
    l: float,
    params: SourceParams,
    *,
    radius_multiplier: float,
    width_multiplier: float,
    schedule_name: str,
    temporal_width_multiplier: float = 1.0,
    temporal_profile: str = "tanh",
    radial_profile: str = "tanh",
    release_lag_widths: float = 0.0,
) -> float:
    s_arr = np.asarray(s, dtype=float)
    l_arr = np.asarray(l, dtype=float)
    radius = max(float(params.Rpass) * float(radius_multiplier), 1.0e-12)
    width = max(float(params.w_pass) * float(width_multiplier), 1.0e-12)
    packet = packet_bump_sq((l_arr - s_arr) ** 2 + params.eps * params.eps, radius, width, radial_profile)
    schedule = standing_support_packet_temporal_schedule(
        s,
        params,
        schedule_name=schedule_name,
        temporal_width_multiplier=temporal_width_multiplier,
        temporal_profile=temporal_profile,
        release_lag_widths=release_lag_widths,
    )
    return float(np.clip(packet * schedule, 0.0, 1.0))


def standing_support_packet_coupled_profile_active(params: SourceParams) -> bool:
    return bool(
        params.standing_support_packet_coupled_profile_enabled
        and (
            params.standing_support_packet_coupled_entry_carve
            or params.standing_support_packet_coupled_catch_carve
            or params.standing_support_packet_coupled_edge_carve
            or params.standing_support_packet_coupled_radial_log_gain
            or params.standing_support_packet_coupled_null_cushion_log_gain
        )
    )


def standing_support_packet_coupled_entry_window(s: float, l: float, params: SourceParams) -> float:
    if not standing_support_packet_coupled_profile_active(params):
        return 0.0
    return standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_coupled_radius_multiplier,
        width_multiplier=params.standing_support_packet_coupled_width_multiplier,
        schedule_name=params.standing_support_packet_coupled_entry_schedule,
        temporal_profile=params.standing_support_packet_coupled_temporal_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )


def standing_support_packet_coupled_catch_window(s: float, l: float, params: SourceParams) -> float:
    if not standing_support_packet_coupled_profile_active(params):
        return 0.0
    return standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_coupled_radius_multiplier,
        width_multiplier=params.standing_support_packet_coupled_width_multiplier,
        schedule_name=params.standing_support_packet_coupled_catch_schedule,
        temporal_profile=params.standing_support_packet_coupled_temporal_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )


def standing_support_packet_coupled_containment_window(s: float, l: float, params: SourceParams) -> float:
    if not standing_support_packet_coupled_profile_active(params):
        return 0.0
    entry = float(params.standing_support_packet_coupled_entry_carve) * standing_support_packet_coupled_entry_window(
        s, l, params
    )
    catch = float(params.standing_support_packet_coupled_catch_carve) * standing_support_packet_coupled_catch_window(
        s, l, params
    )
    edge = float(params.standing_support_packet_coupled_edge_carve) * standing_support_packet_coupled_entry_edge_window(
        s, l, params
    )
    return smooth_union(entry, catch, edge)


def standing_support_packet_coupled_edge_window(s: float, l: float, params: SourceParams) -> float:
    if not standing_support_packet_coupled_profile_active(params):
        return 0.0
    outer_entry = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_coupled_edge_outer_radius_multiplier,
        width_multiplier=params.standing_support_packet_coupled_edge_width_multiplier,
        schedule_name=params.standing_support_packet_coupled_entry_schedule,
        temporal_profile=params.standing_support_packet_coupled_temporal_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )
    inner_entry = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_coupled_edge_inner_radius_multiplier,
        width_multiplier=params.standing_support_packet_coupled_edge_width_multiplier,
        schedule_name=params.standing_support_packet_coupled_entry_schedule,
        temporal_profile=params.standing_support_packet_coupled_temporal_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )
    outer_catch = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_coupled_edge_outer_radius_multiplier,
        width_multiplier=params.standing_support_packet_coupled_edge_width_multiplier,
        schedule_name=params.standing_support_packet_coupled_catch_schedule,
        temporal_profile=params.standing_support_packet_coupled_temporal_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )
    inner_catch = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_coupled_edge_inner_radius_multiplier,
        width_multiplier=params.standing_support_packet_coupled_edge_width_multiplier,
        schedule_name=params.standing_support_packet_coupled_catch_schedule,
        temporal_profile=params.standing_support_packet_coupled_temporal_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )
    entry_edge = max(outer_entry - inner_entry, 0.0) * float(params.standing_support_packet_coupled_entry_carve)
    catch_edge = max(outer_catch - inner_catch, 0.0) * float(params.standing_support_packet_coupled_catch_carve)
    scale = max(
        float(params.standing_support_packet_coupled_entry_carve)
        + float(params.standing_support_packet_coupled_catch_carve),
        1.0e-12,
    )
    return float(np.clip((entry_edge + catch_edge) / scale, 0.0, 1.0))


def standing_support_packet_coupled_entry_edge_window(s: float, l: float, params: SourceParams) -> float:
    if not standing_support_packet_coupled_profile_active(params):
        return 0.0
    outer = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_coupled_edge_outer_radius_multiplier,
        width_multiplier=params.standing_support_packet_coupled_edge_width_multiplier,
        schedule_name=params.standing_support_packet_coupled_entry_schedule,
        temporal_profile=params.standing_support_packet_coupled_temporal_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )
    inner = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_coupled_edge_inner_radius_multiplier,
        width_multiplier=params.standing_support_packet_coupled_edge_width_multiplier,
        schedule_name=params.standing_support_packet_coupled_entry_schedule,
        temporal_profile=params.standing_support_packet_coupled_temporal_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )
    return float(np.clip(outer - inner, 0.0, 1.0))


def standing_support_packet_coupled_catch_edge_window(s: float, l: float, params: SourceParams) -> float:
    if not standing_support_packet_coupled_profile_active(params):
        return 0.0
    outer = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_coupled_edge_outer_radius_multiplier,
        width_multiplier=params.standing_support_packet_coupled_edge_width_multiplier,
        schedule_name=params.standing_support_packet_coupled_catch_schedule,
        temporal_profile=params.standing_support_packet_coupled_temporal_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )
    inner = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_coupled_edge_inner_radius_multiplier,
        width_multiplier=params.standing_support_packet_coupled_edge_width_multiplier,
        schedule_name=params.standing_support_packet_coupled_catch_schedule,
        temporal_profile=params.standing_support_packet_coupled_temporal_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )
    return float(np.clip(outer - inner, 0.0, 1.0))


def standing_support_packet_coupled_radial_window(s: float, l: float, params: SourceParams) -> float:
    if float(params.standing_support_packet_coupled_radial_log_gain) == 0.0:
        return 0.0
    return standing_support_packet_coupled_edge_window(s, l, params)


def standing_support_packet_coupled_null_cushion_window(s: float, l: float, params: SourceParams) -> float:
    if float(params.standing_support_packet_coupled_null_cushion_log_gain) == 0.0:
        return 0.0
    return standing_support_packet_coupled_catch_edge_window(s, l, params)


def standing_support_packet_coupled_rebate_window(s: float, l: float, params: SourceParams) -> float:
    if float(params.standing_support_packet_coupled_rebate_fraction) <= 0.0:
        return 0.0
    return standing_support_packet_coupled_edge_window(s, l, params)


def standing_support_packet_smooth_split_active(params: SourceParams) -> bool:
    return bool(
        params.standing_support_packet_smooth_split_enabled
        and (
            params.standing_support_packet_smooth_split_entry_carve
            or params.standing_support_packet_smooth_split_catch_carve
            or params.standing_support_packet_smooth_split_edge_carve
            or params.standing_support_packet_smooth_split_null_cushion_log_gain
            or params.standing_support_packet_smooth_split_angular_log_gain
        )
    )


def standing_support_packet_smooth_split_entry_window(s: float, l: float, params: SourceParams) -> float:
    if not standing_support_packet_smooth_split_active(params):
        return 0.0
    return standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_smooth_split_entry_radius_multiplier,
        width_multiplier=params.standing_support_packet_smooth_split_entry_width_multiplier,
        schedule_name=params.standing_support_packet_smooth_split_entry_schedule,
        temporal_width_multiplier=params.standing_support_packet_smooth_split_temporal_width_multiplier,
        temporal_profile=params.standing_support_packet_smooth_split_temporal_profile,
        radial_profile=params.standing_support_packet_smooth_split_radial_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )


def standing_support_packet_smooth_split_catch_window(s: float, l: float, params: SourceParams) -> float:
    if not standing_support_packet_smooth_split_active(params):
        return 0.0
    return standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_smooth_split_catch_radius_multiplier,
        width_multiplier=params.standing_support_packet_smooth_split_catch_width_multiplier,
        schedule_name=params.standing_support_packet_smooth_split_catch_schedule,
        temporal_width_multiplier=params.standing_support_packet_smooth_split_temporal_width_multiplier,
        temporal_profile=params.standing_support_packet_smooth_split_temporal_profile,
        radial_profile=params.standing_support_packet_smooth_split_radial_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )


def standing_support_packet_smooth_split_edge_window(s: float, l: float, params: SourceParams) -> float:
    if not standing_support_packet_smooth_split_active(params):
        return 0.0
    outer = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_smooth_split_edge_outer_radius_multiplier,
        width_multiplier=params.standing_support_packet_smooth_split_edge_width_multiplier,
        schedule_name=params.standing_support_packet_smooth_split_edge_schedule,
        temporal_width_multiplier=params.standing_support_packet_smooth_split_temporal_width_multiplier,
        temporal_profile=params.standing_support_packet_smooth_split_temporal_profile,
        radial_profile=params.standing_support_packet_smooth_split_radial_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )
    inner = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_smooth_split_edge_inner_radius_multiplier,
        width_multiplier=params.standing_support_packet_smooth_split_edge_width_multiplier,
        schedule_name=params.standing_support_packet_smooth_split_edge_schedule,
        temporal_width_multiplier=params.standing_support_packet_smooth_split_temporal_width_multiplier,
        temporal_profile=params.standing_support_packet_smooth_split_temporal_profile,
        radial_profile=params.standing_support_packet_smooth_split_radial_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )
    return float(np.clip(outer - inner, 0.0, 1.0))


def standing_support_packet_smooth_split_current_guard_window(s: float, l: float, params: SourceParams) -> float:
    if float(params.standing_support_packet_smooth_split_current_guard_fraction) <= 0.0:
        return 0.0
    outer = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_smooth_split_current_guard_outer_radius_multiplier,
        width_multiplier=params.standing_support_packet_smooth_split_current_guard_width_multiplier,
        schedule_name=params.standing_support_packet_smooth_split_current_guard_schedule,
        temporal_width_multiplier=params.standing_support_packet_smooth_split_current_guard_temporal_width_multiplier,
        temporal_profile=params.standing_support_packet_smooth_split_temporal_profile,
        radial_profile=params.standing_support_packet_smooth_split_radial_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )
    inner = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_smooth_split_current_guard_inner_radius_multiplier,
        width_multiplier=params.standing_support_packet_smooth_split_current_guard_width_multiplier,
        schedule_name=params.standing_support_packet_smooth_split_current_guard_schedule,
        temporal_width_multiplier=params.standing_support_packet_smooth_split_current_guard_temporal_width_multiplier,
        temporal_profile=params.standing_support_packet_smooth_split_temporal_profile,
        radial_profile=params.standing_support_packet_smooth_split_radial_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )
    return float(np.clip(outer - inner, 0.0, 1.0))


def standing_support_packet_smooth_split_guarded_edge_window(s: float, l: float, params: SourceParams) -> float:
    edge = standing_support_packet_smooth_split_edge_window(s, l, params)
    guard_fraction = float(params.standing_support_packet_smooth_split_current_guard_fraction)
    if guard_fraction <= 0.0:
        return edge
    guard = standing_support_packet_smooth_split_current_guard_window(s, l, params)
    mode = params.standing_support_packet_smooth_split_current_guard_mode.strip().lower()
    if mode == "attenuate":
        value = edge * (1.0 - guard_fraction * guard)
    elif mode in {"blend", "replace", "replacement"}:
        value = (1.0 - guard_fraction) * edge + guard_fraction * guard
    else:
        raise ValueError(
            "Unknown smooth split current guard mode: "
            f"{params.standing_support_packet_smooth_split_current_guard_mode}"
        )
    return float(np.clip(value, 0.0, 1.0))


def standing_support_packet_smooth_split_containment_window(s: float, l: float, params: SourceParams) -> float:
    if not standing_support_packet_smooth_split_active(params):
        return 0.0
    entry = (
        float(params.standing_support_packet_smooth_split_entry_carve)
        * standing_support_packet_smooth_split_entry_window(s, l, params)
    )
    catch = (
        float(params.standing_support_packet_smooth_split_catch_carve)
        * standing_support_packet_smooth_split_catch_window(s, l, params)
    )
    edge = (
        float(params.standing_support_packet_smooth_split_edge_carve)
        * standing_support_packet_smooth_split_guarded_edge_window(s, l, params)
    )
    return compose_packet_windows(
        (entry, catch, edge),
        params.standing_support_packet_smooth_split_composition,
    )


def standing_support_packet_smooth_split_null_cushion_window(s: float, l: float, params: SourceParams) -> float:
    if float(params.standing_support_packet_smooth_split_null_cushion_log_gain) == 0.0:
        return 0.0
    return standing_support_packet_smooth_split_guarded_edge_window(s, l, params)


def standing_support_packet_smooth_split_angular_window(s: float, l: float, params: SourceParams) -> float:
    if float(params.standing_support_packet_smooth_split_angular_log_gain) == 0.0:
        return 0.0
    return standing_support_packet_smooth_split_guarded_edge_window(s, l, params)


def standing_support_packet_carve_window(s: float, l: float, params: SourceParams) -> float:
    strength = float(params.standing_support_packet_exclusion)
    if strength <= 0.0:
        return 0.0
    return standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_exclusion_radius_multiplier,
        width_multiplier=params.standing_support_packet_exclusion_width_multiplier,
        schedule_name=params.standing_support_packet_exclusion_schedule,
        temporal_profile=params.standing_support_packet_exclusion_temporal_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )


def standing_support_packet_carve_catch_window(s: float, l: float, params: SourceParams) -> float:
    strength = float(params.standing_support_packet_exclusion_catch)
    if strength <= 0.0:
        return 0.0
    return standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_exclusion_catch_radius_multiplier,
        width_multiplier=params.standing_support_packet_exclusion_catch_width_multiplier,
        schedule_name=params.standing_support_packet_exclusion_catch_schedule,
        temporal_profile=params.standing_support_packet_exclusion_catch_temporal_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )


def standing_support_packet_carve_shoulder_window(s: float, l: float, params: SourceParams) -> float:
    strength = float(params.standing_support_packet_exclusion_shoulder)
    if strength <= 0.0:
        return 0.0
    outer = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_exclusion_shoulder_radius_multiplier,
        width_multiplier=params.standing_support_packet_exclusion_shoulder_width_multiplier,
        schedule_name=params.standing_support_packet_exclusion_shoulder_schedule,
        temporal_profile=params.standing_support_packet_exclusion_shoulder_temporal_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )
    mode = params.standing_support_packet_exclusion_shoulder_mode.strip().lower()
    if mode == "filled":
        return outer
    if mode == "annular":
        inner = standing_support_packet_window(
            s,
            l,
            params,
            radius_multiplier=params.standing_support_packet_exclusion_radius_multiplier,
            width_multiplier=params.standing_support_packet_exclusion_width_multiplier,
            schedule_name=params.standing_support_packet_exclusion_shoulder_schedule,
            temporal_profile=params.standing_support_packet_exclusion_shoulder_temporal_profile,
            release_lag_widths=params.release_carve_lag_widths,
        )
        return float(np.clip(outer - inner, 0.0, 1.0))
    raise ValueError(f"Unknown standing support packet shoulder mode: {params.standing_support_packet_exclusion_shoulder_mode}")


def standing_support_packet_lapse_window(s: float, l: float, params: SourceParams) -> float:
    if float(params.standing_support_packet_lapse_log_gain) == 0.0:
        return 0.0
    return standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_lapse_radius_multiplier,
        width_multiplier=params.standing_support_packet_lapse_width_multiplier,
        schedule_name=params.standing_support_packet_lapse_schedule,
        temporal_profile=params.standing_support_packet_lapse_temporal_profile,
        release_lag_widths=params.release_lapse_lag_widths,
    )


def standing_support_packet_null_cushion_window(s: float, l: float, params: SourceParams) -> float:
    if float(params.standing_support_packet_null_cushion_log_gain) == 0.0:
        return 0.0
    outer = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_null_cushion_radius_multiplier,
        width_multiplier=params.standing_support_packet_null_cushion_width_multiplier,
        schedule_name=params.standing_support_packet_null_cushion_schedule,
        temporal_profile=params.standing_support_packet_null_cushion_temporal_profile,
        release_lag_widths=params.release_lapse_lag_widths,
    )
    mode = params.standing_support_packet_null_cushion_mode.strip().lower()
    if mode == "filled":
        return outer
    if mode == "annular":
        inner = standing_support_packet_window(
            s,
            l,
            params,
            radius_multiplier=params.standing_support_packet_null_cushion_inner_radius_multiplier,
            width_multiplier=params.standing_support_packet_null_cushion_width_multiplier,
            schedule_name=params.standing_support_packet_null_cushion_schedule,
            temporal_profile=params.standing_support_packet_null_cushion_temporal_profile,
            release_lag_widths=params.release_lapse_lag_widths,
        )
        return float(np.clip(outer - inner, 0.0, 1.0))
    raise ValueError(f"Unknown standing support packet null cushion mode: {params.standing_support_packet_null_cushion_mode}")


def standing_support_packet_radial_window(s: float, l: float, params: SourceParams) -> float:
    if float(params.standing_support_packet_radial_log_gain) == 0.0:
        return 0.0
    return standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_radial_radius_multiplier,
        width_multiplier=params.standing_support_packet_radial_width_multiplier,
        schedule_name=params.standing_support_packet_radial_schedule,
        temporal_profile=params.standing_support_packet_radial_temporal_profile,
    )


def standing_support_packet_radial_shoulder_window(s: float, l: float, params: SourceParams) -> float:
    if float(params.standing_support_packet_radial_shoulder_log_gain) == 0.0:
        return 0.0
    outer = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_radial_shoulder_radius_multiplier,
        width_multiplier=params.standing_support_packet_radial_shoulder_width_multiplier,
        schedule_name=params.standing_support_packet_radial_shoulder_schedule,
        temporal_profile=params.standing_support_packet_radial_shoulder_temporal_profile,
    )
    mode = params.standing_support_packet_radial_shoulder_mode.strip().lower()
    if mode == "filled":
        return outer
    if mode == "annular":
        inner = standing_support_packet_window(
            s,
            l,
            params,
            radius_multiplier=params.standing_support_packet_radial_radius_multiplier,
            width_multiplier=params.standing_support_packet_radial_width_multiplier,
            schedule_name=params.standing_support_packet_radial_shoulder_schedule,
            temporal_profile=params.standing_support_packet_radial_shoulder_temporal_profile,
        )
        return float(np.clip(outer - inner, 0.0, 1.0))
    raise ValueError(f"Unknown standing support packet radial shoulder mode: {params.standing_support_packet_radial_shoulder_mode}")


def standing_support_packet_radial_skirt_window(s: float, l: float, params: SourceParams) -> float:
    if float(params.standing_support_packet_radial_skirt_log_gain) == 0.0:
        return 0.0
    outer = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_radial_skirt_radius_multiplier,
        width_multiplier=params.standing_support_packet_radial_skirt_width_multiplier,
        schedule_name=params.standing_support_packet_radial_skirt_schedule,
        temporal_profile=params.standing_support_packet_radial_skirt_temporal_profile,
    )
    mode = params.standing_support_packet_radial_skirt_mode.strip().lower()
    if mode == "filled":
        return outer
    if mode == "annular":
        inner = standing_support_packet_window(
            s,
            l,
            params,
            radius_multiplier=params.standing_support_packet_radial_skirt_inner_radius_multiplier,
            width_multiplier=params.standing_support_packet_radial_skirt_width_multiplier,
            schedule_name=params.standing_support_packet_radial_skirt_schedule,
            temporal_profile=params.standing_support_packet_radial_skirt_temporal_profile,
        )
        return float(np.clip(outer - inner, 0.0, 1.0))
    raise ValueError(f"Unknown standing support packet radial skirt mode: {params.standing_support_packet_radial_skirt_mode}")


def standing_support_packet_beta_rematch_window(s: float, l: float, params: SourceParams) -> float:
    if float(params.standing_support_packet_beta_rematch_gain) == 0.0:
        return 0.0
    shape = params.standing_support_packet_beta_rematch_shape.strip().lower()
    temporal_width_multiplier = params.standing_support_packet_beta_rematch_temporal_width_multiplier
    if shape == "core":
        return standing_support_packet_window(
            s,
            l,
            params,
            radius_multiplier=params.standing_support_packet_beta_rematch_radius_multiplier,
            width_multiplier=params.standing_support_packet_beta_rematch_width_multiplier,
            schedule_name=params.standing_support_packet_beta_rematch_schedule,
            temporal_width_multiplier=temporal_width_multiplier,
            temporal_profile=params.standing_support_packet_beta_rematch_temporal_profile,
        )
    core_floor = float(params.standing_support_packet_beta_rematch_center_floor) * standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.standing_support_packet_beta_rematch_radius_multiplier,
        width_multiplier=params.standing_support_packet_beta_rematch_width_multiplier,
        schedule_name=params.standing_support_packet_beta_rematch_schedule,
        temporal_width_multiplier=temporal_width_multiplier,
        temporal_profile=params.standing_support_packet_beta_rematch_temporal_profile,
    )

    outer_radius = params.standing_support_packet_beta_rematch_outer_radius_multiplier
    inner_radius = params.standing_support_packet_beta_rematch_inner_radius_multiplier
    edge_width = (
        params.standing_support_packet_beta_rematch_width_multiplier
        * params.standing_support_packet_beta_rematch_edge_softness
    )
    outer = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=outer_radius,
        width_multiplier=edge_width,
        schedule_name=params.standing_support_packet_beta_rematch_schedule,
        temporal_width_multiplier=temporal_width_multiplier,
        temporal_profile=params.standing_support_packet_beta_rematch_temporal_profile,
    )
    if shape == "shoulder":
        return outer

    inner = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=inner_radius,
        width_multiplier=edge_width,
        schedule_name=params.standing_support_packet_beta_rematch_schedule,
        temporal_width_multiplier=temporal_width_multiplier,
        temporal_profile=params.standing_support_packet_beta_rematch_temporal_profile,
    )
    annulus = float(np.clip(outer - inner, 0.0, 1.0))
    floor_mode = params.standing_support_packet_beta_rematch_floor_mode.strip().lower()

    def with_floor(value: float) -> float:
        if floor_mode == "max":
            return float(np.clip(max(value, core_floor), 0.0, 1.0))
        if floor_mode == "blend":
            return float(np.clip(value + core_floor * (1.0 - value), 0.0, 1.0))
        if floor_mode == "add":
            return float(np.clip(value + core_floor, 0.0, 1.0))
        raise ValueError(
            f"Unknown standing support packet beta rematch floor mode: "
            f"{params.standing_support_packet_beta_rematch_floor_mode}"
        )

    if shape == "annular":
        return with_floor(annulus)
    if shape == "edge_soften":
        d = abs(float(l) - float(s))
        center = max(float(params.Rpass) * float(outer_radius), 1.0e-12)
        sigma = max(float(params.w_pass) * float(edge_width), 1.0e-12)
        edge = math.exp(-((d - center) / sigma) ** 2)
        return with_floor(max(annulus, edge * outer))
    if shape == "trailing_edge":
        side_sigma = max(float(params.w_pass) * float(edge_width), 1.0e-12)
        trailing_side = falloff(float(l) - float(s), side_sigma)
        return with_floor(annulus * trailing_side)
    raise ValueError(f"Unknown standing support packet beta rematch shape: {params.standing_support_packet_beta_rematch_shape}")


def causal_margin_guard_window(s: float, l: float, params: SourceParams) -> float:
    if not params.causal_margin_guard_enabled:
        return 0.0

    packet = standing_support_packet_window(
        s,
        l,
        params,
        radius_multiplier=params.causal_margin_guard_radius_multiplier,
        width_multiplier=params.causal_margin_guard_width_multiplier,
        schedule_name=params.causal_margin_guard_schedule,
        temporal_width_multiplier=params.causal_margin_guard_temporal_width_multiplier,
        temporal_profile=params.causal_margin_guard_temporal_profile,
        radial_profile=params.causal_margin_guard_radial_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )
    mode = params.causal_margin_guard_window_mode.strip().lower()
    if mode in {"packet", "packet_only"}:
        return packet

    edge = smooth_union(
        standing_support_packet_smooth_split_edge_window(s, l, params),
        standing_support_packet_smooth_split_guarded_edge_window(s, l, params),
        standing_support_packet_smooth_split_current_guard_window(s, l, params),
        support_edge_receiver_radial_cap_window(s, l, params),
        support_edge_receiver_angular_flange_window(s, l, params),
    )
    if mode in {"edge", "packet_plus_edge"}:
        return smooth_union(packet, edge)

    guard_schedule = standing_support_packet_temporal_schedule(
        s,
        params,
        schedule_name=params.causal_margin_guard_schedule,
        temporal_width_multiplier=params.causal_margin_guard_temporal_width_multiplier,
        temporal_profile=params.causal_margin_guard_temporal_profile,
        release_lag_widths=params.release_carve_lag_widths,
    )
    support = float(np.clip(support_bump(float(l), params) * guard_schedule, 0.0, 1.0))
    shell = support_shell_overlay_window(s, l, params)
    if mode in {"support", "packet_plus_support"}:
        return smooth_union(packet, edge, support, shell)

    raise ValueError(f"Unknown causal margin guard window mode: {params.causal_margin_guard_window_mode}")


def _window_s_derivative_abs(fn: Any, s: float, l: float, params: SourceParams) -> float:
    step = max(min(float(params.w_beta), float(params.w_pass)) * 1.0e-3, 1.0e-6)
    plus = float(fn(s + step, l, params))
    minus = float(fn(s - step, l, params))
    return abs((plus - minus) / (2.0 * step))


def scalars(s: float, l: float, params: SourceParams) -> dict[str, float]:
    s_arr = np.asarray(s, dtype=float)
    l_arr = np.asarray(l, dtype=float)

    c_beta = catch_factor(s_arr, params.x_catch_beta, params.w_catch_beta, params.catch_profile)
    c_packet = catch_factor(s_arr, params.x_catch_packet, params.w_catch_packet, params.catch_profile)
    u_beta = params.v_exit + (params.V - params.v_exit) * c_beta
    u_packet = params.v_exit + (params.V - params.v_exit) * c_packet

    e_release = release_profile_down(s_arr, params)
    q = minjerk_down(s_arr, params.q_t0, params.q_Tr)
    w_support_raw = support_bump(l_arr, params)
    s_packet = bump_sq((l_arr - s_arr) ** 2 + params.eps * params.eps, params.Rpass, params.w_pass)
    carve_window = standing_support_packet_carve_window(float(s), float(l), params)
    carve_catch_window = standing_support_packet_carve_catch_window(float(s), float(l), params)
    carve_shoulder_window = standing_support_packet_carve_shoulder_window(float(s), float(l), params)
    coupled_entry_window = standing_support_packet_coupled_entry_window(float(s), float(l), params)
    coupled_catch_window = standing_support_packet_coupled_catch_window(float(s), float(l), params)
    coupled_containment_window = standing_support_packet_coupled_containment_window(float(s), float(l), params)
    coupled_edge_window = standing_support_packet_coupled_edge_window(float(s), float(l), params)
    coupled_rebate_window = standing_support_packet_coupled_rebate_window(float(s), float(l), params)
    coupled_null_cushion_window = standing_support_packet_coupled_null_cushion_window(float(s), float(l), params)
    coupled_radial_window = standing_support_packet_coupled_radial_window(float(s), float(l), params)
    smooth_split_entry_window = standing_support_packet_smooth_split_entry_window(float(s), float(l), params)
    smooth_split_catch_window = standing_support_packet_smooth_split_catch_window(float(s), float(l), params)
    smooth_split_edge_window = standing_support_packet_smooth_split_edge_window(float(s), float(l), params)
    smooth_split_current_guard_window = standing_support_packet_smooth_split_current_guard_window(float(s), float(l), params)
    smooth_split_guarded_edge_window = standing_support_packet_smooth_split_guarded_edge_window(float(s), float(l), params)
    smooth_split_containment_window = standing_support_packet_smooth_split_containment_window(float(s), float(l), params)
    smooth_split_null_cushion_window = standing_support_packet_smooth_split_null_cushion_window(float(s), float(l), params)
    smooth_split_angular_window = standing_support_packet_smooth_split_angular_window(float(s), float(l), params)
    packet_lapse_window = standing_support_packet_lapse_window(float(s), float(l), params)
    packet_null_cushion_window = standing_support_packet_null_cushion_window(float(s), float(l), params)
    packet_radial_window = standing_support_packet_radial_window(float(s), float(l), params)
    packet_radial_shoulder_window = standing_support_packet_radial_shoulder_window(float(s), float(l), params)
    packet_radial_skirt_window = standing_support_packet_radial_skirt_window(float(s), float(l), params)
    packet_beta_rematch_window = standing_support_packet_beta_rematch_window(float(s), float(l), params)
    causal_guard_window = causal_margin_guard_window(float(s), float(l), params)
    receiver_memory_driver = support_edge_receiver_memory_driver(float(s), params)
    receiver_radial_cap_window = support_edge_receiver_radial_cap_window(float(s), float(l), params)
    receiver_angular_flange_window = support_edge_receiver_angular_flange_window(float(s), float(l), params)
    release_slope_abs = float(abs(
        (
            release_profile_down(s_arr + max(float(params.w_beta) * 1.0e-3, 1.0e-6), params)
            - release_profile_down(s_arr - max(float(params.w_beta) * 1.0e-3, 1.0e-6), params)
        )
        / (2.0 * max(float(params.w_beta) * 1.0e-3, 1.0e-6))
    ))
    legacy_carve_contribution = float(np.clip(
        float(params.standing_support_packet_exclusion) * carve_window
        + float(params.standing_support_packet_exclusion_catch) * carve_catch_window
        + float(params.standing_support_packet_exclusion_shoulder) * carve_shoulder_window,
        0.0,
        1.0,
    ))
    if standing_support_packet_smooth_split_active(params):
        raw_carve_contribution = compose_packet_windows(
            (legacy_carve_contribution, coupled_containment_window, smooth_split_containment_window),
            params.standing_support_packet_smooth_split_composition,
        )
    else:
        raw_carve_contribution = smooth_union(
            legacy_carve_contribution,
            coupled_containment_window,
            smooth_split_containment_window,
        )
    coupled_rebate_contribution = float(np.clip(
        min(
            raw_carve_contribution,
            float(params.standing_support_packet_coupled_rebate_fraction) * coupled_rebate_window,
        ),
        0.0,
        1.0,
    ))
    carve_contribution = float(np.clip(raw_carve_contribution - coupled_rebate_contribution, 0.0, 1.0))
    carve_factor = float(np.clip(1.0 - carve_contribution, 0.0, 1.0))
    w_support = w_support_raw * carve_factor

    a_spatial = np.exp(q * w_support * math.log(params.C0))
    t_lapse = np.exp(q * w_support * math.log(params.lam * params.C0))
    b_angular = 1.0 + (params.B0 - 1.0) * w_support * q
    shoulder = np.exp(-((np.abs(l_arr) - 1.05) / 0.35) ** 2)
    n_cushion = np.exp(params.eta_N * 0.18 * q * shoulder)

    shell_window = support_shell_overlay_window(float(s), float(l), params)
    beta_base = -u_beta * e_release * (w_support ** params.p_beta) * s_packet / b_angular
    delta_beta_shell = float(params.support_shell_amplitude) * shell_window if params.support_shell_overlay_enabled else 0.0
    beta_pre_rematch = beta_base + delta_beta_shell
    alpha_base = n_cushion * t_lapse
    packet_lapse_factor = support_shell_metric_factor(params.standing_support_packet_lapse_log_gain, packet_lapse_window)
    packet_null_cushion_factor = support_shell_metric_factor(
        params.standing_support_packet_null_cushion_log_gain,
        packet_null_cushion_window,
    )
    coupled_null_cushion_factor = support_shell_metric_factor(
        params.standing_support_packet_coupled_null_cushion_log_gain,
        coupled_null_cushion_window,
    )
    smooth_split_null_cushion_factor = support_shell_metric_factor(
        params.standing_support_packet_smooth_split_null_cushion_log_gain,
        smooth_split_null_cushion_window,
    )
    receiver_lapse_factor = support_shell_metric_factor(
        params.support_edge_receiver_lapse_log_gain,
        receiver_radial_cap_window,
    )
    clock_lapse_factor = support_shell_metric_factor(params.support_shell_clock_lapse_log_gain, shell_window)
    alpha = (
        alpha_base
        * packet_lapse_factor
        * packet_null_cushion_factor
        * coupled_null_cushion_factor
        * smooth_split_null_cushion_factor
        * receiver_lapse_factor
        * clock_lapse_factor
    )
    sqrt_gamma_ll_base = b_angular * a_spatial
    gamma_ll_base = sqrt_gamma_ll_base * sqrt_gamma_ll_base
    rail_stretch_factor = support_shell_metric_factor(params.support_shell_rail_stretch_log_gain, shell_window)
    legacy_packet_radial_factor = math.exp(
        float(params.standing_support_packet_radial_log_gain) * packet_radial_window
        + float(params.standing_support_packet_radial_shoulder_log_gain) * packet_radial_shoulder_window
        + float(params.standing_support_packet_radial_skirt_log_gain) * packet_radial_skirt_window
    )
    coupled_radial_factor = math.exp(
        float(params.standing_support_packet_coupled_radial_log_gain) * coupled_radial_window
    )
    receiver_radial_factor = support_shell_metric_factor(
        params.support_edge_receiver_radial_log_gain,
        receiver_radial_cap_window,
    )
    packet_radial_factor = legacy_packet_radial_factor * coupled_radial_factor * receiver_radial_factor
    gamma_ll = gamma_ll_base * rail_stretch_factor * packet_radial_factor
    sqrt_gamma_ll = np.sqrt(gamma_ll)
    vcoord = u_packet / b_angular
    delta_beta_receiver = (
        -float(params.support_edge_receiver_beta_relaxation_gain)
        * receiver_radial_cap_window
        * (vcoord + beta_pre_rematch)
    )
    beta_after_receiver = beta_pre_rematch + delta_beta_receiver
    delta_beta_packet = (
        -float(params.standing_support_packet_beta_rematch_gain)
        * packet_beta_rematch_window
        * (vcoord + beta_after_receiver)
    )
    beta_pre_causal_guard = beta_after_receiver + delta_beta_packet
    causal_guard_margin_fraction = float(np.clip(params.causal_margin_guard_margin, 0.0, 0.999999))
    causal_guard_strength = float(np.clip(params.causal_margin_guard_strength, 0.0, 1.0))
    local_light_speed = float(alpha / max(float(sqrt_gamma_ll), 1.0e-12))
    causal_guard_limit = max(0.0, 1.0 - causal_guard_margin_fraction) * local_light_speed
    if (
        params.causal_margin_guard_enabled
        and causal_guard_strength > 0.0
        and causal_guard_window > 0.0
        and abs(float(beta_pre_causal_guard)) > causal_guard_limit
    ):
        beta_clamped = math.copysign(causal_guard_limit, float(beta_pre_causal_guard))
        delta_beta_causal_guard = (
            causal_guard_strength
            * float(causal_guard_window)
            * (beta_clamped - float(beta_pre_causal_guard))
        )
    else:
        delta_beta_causal_guard = 0.0
    beta = beta_pre_causal_guard + delta_beta_causal_guard
    causal_guard_margin_pre = local_light_speed - abs(float(beta_pre_causal_guard))
    causal_guard_margin_post = local_light_speed - abs(float(beta))
    gtt = -alpha * alpha + gamma_ll * beta * beta
    packet_norm = -alpha * alpha + gamma_ll * (vcoord + beta) ** 2

    w_omega = bump_sq(l_arr * l_arr, params.ROmega, params.wOmega)
    q_omega = falloff(s_arr - params.xOmega, params.wtOmega)
    c_omega = np.exp(params.aOmega * q_omega * w_omega)
    gamma_omega_base = (l_arr * l_arr + params.Rth * params.Rth) * c_omega * c_omega
    throat_capacity_factor = support_shell_metric_factor(params.support_shell_throat_capacity_log_gain, shell_window)
    smooth_split_angular_factor = support_shell_metric_factor(
        params.standing_support_packet_smooth_split_angular_log_gain,
        smooth_split_angular_window,
    )
    receiver_angular_factor = support_shell_metric_factor(
        params.support_edge_receiver_angular_log_gain,
        receiver_angular_flange_window,
    )
    gamma_omega = gamma_omega_base * throat_capacity_factor * smooth_split_angular_factor * receiver_angular_factor

    return {
        "U_beta": float(u_beta),
        "U_packet": float(u_packet),
        "E": float(e_release),
        "q": float(q),
        "W": float(w_support),
        "W_raw": float(w_support_raw),
        "standing_support_packet_carve_window": float(carve_window),
        "standing_support_packet_carve_catch_window": float(carve_catch_window),
        "standing_support_packet_carve_shoulder_window": float(carve_shoulder_window),
        "standing_support_packet_coupled_entry_window": float(coupled_entry_window),
        "standing_support_packet_coupled_catch_window": float(coupled_catch_window),
        "standing_support_packet_coupled_containment_window": float(coupled_containment_window),
        "standing_support_packet_coupled_edge_window": float(coupled_edge_window),
        "standing_support_packet_coupled_rebate_window": float(coupled_rebate_window),
        "standing_support_packet_coupled_radial_window": float(coupled_radial_window),
        "standing_support_packet_coupled_null_cushion_window": float(coupled_null_cushion_window),
        "standing_support_packet_smooth_split_entry_window": float(smooth_split_entry_window),
        "standing_support_packet_smooth_split_catch_window": float(smooth_split_catch_window),
        "standing_support_packet_smooth_split_edge_window": float(smooth_split_edge_window),
        "standing_support_packet_smooth_split_current_guard_window": float(smooth_split_current_guard_window),
        "standing_support_packet_smooth_split_guarded_edge_window": float(smooth_split_guarded_edge_window),
        "standing_support_packet_smooth_split_containment_window": float(smooth_split_containment_window),
        "standing_support_packet_smooth_split_null_cushion_window": float(smooth_split_null_cushion_window),
        "standing_support_packet_smooth_split_angular_window": float(smooth_split_angular_window),
        "support_edge_receiver_memory_driver": float(receiver_memory_driver),
        "support_edge_receiver_radial_cap_window": float(receiver_radial_cap_window),
        "support_edge_receiver_angular_flange_window": float(receiver_angular_flange_window),
        "standing_support_packet_raw_carve_contribution": float(raw_carve_contribution),
        "standing_support_packet_coupled_rebate_contribution": float(coupled_rebate_contribution),
        "standing_support_packet_carve_contribution": float(carve_contribution),
        "standing_support_packet_carve_factor": float(carve_factor),
        "standing_support_packet_lapse_window": float(packet_lapse_window),
        "standing_support_packet_lapse_factor": float(packet_lapse_factor),
        "standing_support_packet_null_cushion_window": float(packet_null_cushion_window),
        "standing_support_packet_null_cushion_factor": float(packet_null_cushion_factor),
        "standing_support_packet_coupled_null_cushion_factor": float(coupled_null_cushion_factor),
        "standing_support_packet_smooth_split_null_cushion_factor": float(smooth_split_null_cushion_factor),
        "standing_support_packet_smooth_split_angular_factor": float(smooth_split_angular_factor),
        "support_edge_receiver_lapse_factor": float(receiver_lapse_factor),
        "support_edge_receiver_radial_factor": float(receiver_radial_factor),
        "support_edge_receiver_angular_factor": float(receiver_angular_factor),
        "standing_support_packet_radial_window": float(packet_radial_window),
        "standing_support_packet_radial_shoulder_window": float(packet_radial_shoulder_window),
        "standing_support_packet_radial_skirt_window": float(packet_radial_skirt_window),
        "standing_support_packet_radial_factor": float(packet_radial_factor),
        "standing_support_packet_beta_rematch_window": float(packet_beta_rematch_window),
        "causal_margin_guard_window": float(causal_guard_window),
        "release_profile_slope_abs": release_slope_abs,
        "standing_support_packet_carve_window_slope_abs": _window_s_derivative_abs(
            standing_support_packet_carve_window, float(s), float(l), params
        ),
        "standing_support_packet_carve_catch_window_slope_abs": _window_s_derivative_abs(
            standing_support_packet_carve_catch_window, float(s), float(l), params
        ),
        "standing_support_packet_coupled_containment_window_slope_abs": _window_s_derivative_abs(
            standing_support_packet_coupled_containment_window, float(s), float(l), params
        ),
        "standing_support_packet_coupled_edge_window_slope_abs": _window_s_derivative_abs(
            standing_support_packet_coupled_edge_window, float(s), float(l), params
        ),
        "standing_support_packet_coupled_rebate_window_slope_abs": _window_s_derivative_abs(
            standing_support_packet_coupled_rebate_window, float(s), float(l), params
        ),
        "standing_support_packet_coupled_null_cushion_window_slope_abs": _window_s_derivative_abs(
            standing_support_packet_coupled_null_cushion_window, float(s), float(l), params
        ),
        "standing_support_packet_smooth_split_containment_window_slope_abs": _window_s_derivative_abs(
            standing_support_packet_smooth_split_containment_window, float(s), float(l), params
        ),
        "standing_support_packet_smooth_split_edge_window_slope_abs": _window_s_derivative_abs(
            standing_support_packet_smooth_split_edge_window, float(s), float(l), params
        ),
        "standing_support_packet_smooth_split_current_guard_window_slope_abs": _window_s_derivative_abs(
            standing_support_packet_smooth_split_current_guard_window, float(s), float(l), params
        ),
        "standing_support_packet_smooth_split_guarded_edge_window_slope_abs": _window_s_derivative_abs(
            standing_support_packet_smooth_split_guarded_edge_window, float(s), float(l), params
        ),
        "standing_support_packet_smooth_split_null_cushion_window_slope_abs": _window_s_derivative_abs(
            standing_support_packet_smooth_split_null_cushion_window, float(s), float(l), params
        ),
        "standing_support_packet_smooth_split_angular_window_slope_abs": _window_s_derivative_abs(
            standing_support_packet_smooth_split_angular_window, float(s), float(l), params
        ),
        "support_edge_receiver_radial_cap_window_slope_abs": _window_s_derivative_abs(
            support_edge_receiver_radial_cap_window, float(s), float(l), params
        ),
        "support_edge_receiver_angular_flange_window_slope_abs": _window_s_derivative_abs(
            support_edge_receiver_angular_flange_window, float(s), float(l), params
        ),
        "standing_support_packet_lapse_window_slope_abs": _window_s_derivative_abs(
            standing_support_packet_lapse_window, float(s), float(l), params
        ),
        "standing_support_packet_null_cushion_window_slope_abs": _window_s_derivative_abs(
            standing_support_packet_null_cushion_window, float(s), float(l), params
        ),
        "standing_support_packet_radial_window_slope_abs": _window_s_derivative_abs(
            standing_support_packet_radial_window, float(s), float(l), params
        ),
        "standing_support_packet_radial_skirt_window_slope_abs": _window_s_derivative_abs(
            standing_support_packet_radial_skirt_window, float(s), float(l), params
        ),
        "standing_support_packet_beta_rematch_window_slope_abs": _window_s_derivative_abs(
            standing_support_packet_beta_rematch_window, float(s), float(l), params
        ),
        "causal_margin_guard_window_slope_abs": _window_s_derivative_abs(
            causal_margin_guard_window, float(s), float(l), params
        ),
        "S": float(s_packet),
        "A": float(a_spatial),
        "T": float(t_lapse),
        "B": float(b_angular),
        "N": float(n_cushion),
        "beta": float(beta),
        "alpha": float(alpha),
        "beta_base": float(beta_base),
        "beta_pre_packet_rematch": float(beta_pre_rematch),
        "alpha_base": float(alpha_base),
        "gamma_ll_base": float(gamma_ll_base),
        "support_shell_window": float(shell_window),
        "support_shell_delta_beta": float(delta_beta_shell),
        "standing_support_packet_delta_beta": float(delta_beta_packet),
        "standing_support_packet_delta_alpha": float(alpha_base * packet_lapse_factor - alpha_base),
        "standing_support_packet_null_cushion_delta_alpha": float(
            alpha_base * packet_lapse_factor * packet_null_cushion_factor - alpha_base * packet_lapse_factor
        ),
        "standing_support_packet_coupled_null_cushion_delta_alpha": float(
            alpha_base * packet_lapse_factor * packet_null_cushion_factor * coupled_null_cushion_factor
            - alpha_base * packet_lapse_factor * packet_null_cushion_factor
        ),
        "standing_support_packet_smooth_split_null_cushion_delta_alpha": float(
            alpha_base
            * packet_lapse_factor
            * packet_null_cushion_factor
            * coupled_null_cushion_factor
            * smooth_split_null_cushion_factor
            - alpha_base * packet_lapse_factor * packet_null_cushion_factor * coupled_null_cushion_factor
        ),
        "standing_support_packet_smooth_split_delta_gamma_omega": float(
            gamma_omega_base * throat_capacity_factor * smooth_split_angular_factor
            - gamma_omega_base * throat_capacity_factor
        ),
        "support_edge_receiver_delta_alpha": float(
            alpha_base
            * packet_lapse_factor
            * packet_null_cushion_factor
            * coupled_null_cushion_factor
            * smooth_split_null_cushion_factor
            * receiver_lapse_factor
            - alpha_base
            * packet_lapse_factor
            * packet_null_cushion_factor
            * coupled_null_cushion_factor
            * smooth_split_null_cushion_factor
        ),
        "support_edge_receiver_delta_beta": float(delta_beta_receiver),
        "causal_margin_guard_delta_beta": float(delta_beta_causal_guard),
        "causal_margin_guard_beta_pre": float(beta_pre_causal_guard),
        "causal_margin_guard_limit": float(causal_guard_limit),
        "causal_margin_guard_margin_pre": float(causal_guard_margin_pre),
        "causal_margin_guard_margin_post": float(causal_guard_margin_post),
        "causal_margin_guard_active": float(
            params.causal_margin_guard_enabled
            and causal_guard_window > 0.0
            and abs(float(delta_beta_causal_guard)) > 0.0
        ),
        "support_edge_receiver_delta_gamma_ll": float(
            gamma_ll_base * legacy_packet_radial_factor * coupled_radial_factor * receiver_radial_factor
            - gamma_ll_base * legacy_packet_radial_factor * coupled_radial_factor
        ),
        "support_edge_receiver_delta_gamma_omega": float(
            gamma_omega_base * throat_capacity_factor * smooth_split_angular_factor * receiver_angular_factor
            - gamma_omega_base * throat_capacity_factor * smooth_split_angular_factor
        ),
        "standing_support_packet_delta_gamma_ll": float(gamma_ll_base * packet_radial_factor - gamma_ll_base),
        "standing_support_packet_coupled_delta_gamma_ll": float(
            gamma_ll_base * legacy_packet_radial_factor * coupled_radial_factor
            - gamma_ll_base * legacy_packet_radial_factor
        ),
        "support_shell_clock_lapse_factor": float(clock_lapse_factor),
        "support_shell_delta_alpha": float(alpha - alpha_base),
        "support_shell_rail_stretch_factor": float(rail_stretch_factor),
        "support_shell_delta_gamma_ll": float(gamma_ll_base * rail_stretch_factor - gamma_ll_base),
        "support_shell_throat_capacity_factor": float(throat_capacity_factor),
        "support_shell_delta_gamma_omega": float(gamma_omega - gamma_omega_base),
        "sqrt_gamma_ll": float(sqrt_gamma_ll),
        "gamma_ll": float(gamma_ll),
        "vcoord": float(vcoord),
        "gtt": float(gtt),
        "packet_norm": float(packet_norm),
        "WOmega": float(w_omega),
        "QOmega": float(q_omega),
        "COmega": float(c_omega),
        "gamma_omega_base": float(gamma_omega_base),
        "gamma_omega": float(gamma_omega),
    }


def metric_at(x: np.ndarray, params: SourceParams) -> np.ndarray:
    s, l, theta, _phi = [float(z) for z in x]
    sc = scalars(s, l, params)
    g = np.zeros((4, 4), dtype=float)
    g[0, 0] = -sc["alpha"] ** 2 + sc["gamma_ll"] * sc["beta"] ** 2
    g[0, 1] = g[1, 0] = sc["gamma_ll"] * sc["beta"]
    g[1, 1] = sc["gamma_ll"]
    g[2, 2] = sc["gamma_omega"]
    g[3, 3] = sc["gamma_omega"] * math.sin(theta) ** 2
    return g


def metric_derivative(x: np.ndarray, coord: int, h: np.ndarray, params: SourceParams) -> np.ndarray:
    if coord == 3:
        return np.zeros((4, 4), dtype=float)
    xp = x.copy()
    xm = x.copy()
    xp[coord] += h[coord]
    xm[coord] -= h[coord]
    return (metric_at(xp, params) - metric_at(xm, params)) / (2.0 * h[coord])


def christoffel_at(x: np.ndarray, h: np.ndarray, params: SourceParams) -> np.ndarray:
    g = metric_at(x, params)
    invg = np.linalg.inv(g)
    dg = [metric_derivative(x, a, h, params) for a in range(4)]
    gamma = np.zeros((4, 4, 4), dtype=float)
    for rho in range(4):
        for mu in range(4):
            for nu in range(4):
                total = 0.0
                for sig in range(4):
                    total += invg[rho, sig] * (dg[mu][nu, sig] + dg[nu][mu, sig] - dg[sig][mu, nu])
                gamma[rho, mu, nu] = 0.5 * total
    return gamma


def christoffel_derivative(x: np.ndarray, coord: int, h: np.ndarray, params: SourceParams) -> np.ndarray:
    if coord == 3:
        return np.zeros((4, 4, 4), dtype=float)
    xp = x.copy()
    xm = x.copy()
    xp[coord] += h[coord]
    xm[coord] -= h[coord]
    return (christoffel_at(xp, h, params) - christoffel_at(xm, h, params)) / (2.0 * h[coord])


def einstein_tensor_at(
    s: float,
    l: float,
    params: SourceParams,
    h_s: float,
    h_l: float,
    h_theta: float = 1.0e-4,
) -> tuple[np.ndarray, dict[str, float]]:
    x = np.array([s, l, THETA0, 0.0], dtype=float)
    h = np.array([h_s, h_l, h_theta, 1.0], dtype=float)
    g = metric_at(x, params)
    invg = np.linalg.inv(g)
    gamma = christoffel_at(x, h, params)
    dgamma = [christoffel_derivative(x, a, h, params) for a in range(4)]

    ric = np.zeros((4, 4), dtype=float)
    for mu in range(4):
        for nu in range(4):
            term1 = sum(dgamma[rho][rho, mu, nu] for rho in range(4))
            term2 = sum(dgamma[nu][rho, mu, rho] for rho in range(4))
            term3 = 0.0
            term4 = 0.0
            for rho in range(4):
                trace = sum(gamma[sig, rho, sig] for sig in range(4))
                term3 += gamma[rho, mu, nu] * trace
                for sig in range(4):
                    term4 += gamma[sig, mu, rho] * gamma[rho, nu, sig]
            ric[mu, nu] = term1 - term2 + term3 - term4
    ricci_scalar = float(np.einsum("ab,ab->", invg, ric))
    einstein = ric - 0.5 * g * ricci_scalar
    diagnostics = {"ricci_scalar": ricci_scalar, "cond_metric": float(np.linalg.cond(g))}
    return einstein, diagnostics


def projections(s: float, l: float, einstein: np.ndarray, params: SourceParams) -> dict[str, float]:
    sc = scalars(s, l, params)
    alpha = sc["alpha"]
    beta = sc["beta"]
    sqrt_gamma_ll = math.sqrt(sc["gamma_ll"])
    gamma_omega = sc["gamma_omega"]
    demanded_t = einstein / PI8

    n = np.array([1.0 / alpha, -beta / alpha, 0.0, 0.0], dtype=float)
    e_l = np.array([0.0, 1.0 / sqrt_gamma_ll, 0.0, 0.0], dtype=float)
    e_th = np.array([0.0, 0.0, 1.0 / math.sqrt(gamma_omega), 0.0], dtype=float)
    e_ph = np.array([0.0, 0.0, 0.0, 1.0 / math.sqrt(gamma_omega)], dtype=float)

    rho_euler = float(n @ demanded_t @ n)
    j_l_unit = float(-e_l @ demanded_t @ n)
    p_l_unit = float(e_l @ demanded_t @ e_l)
    p_omega_unit = 0.5 * float(e_th @ demanded_t @ e_th + e_ph @ demanded_t @ e_ph)

    u_raw = np.array([1.0, sc["vcoord"], 0.0, 0.0], dtype=float)
    norm = sc["packet_norm"]
    rho_packet = float("nan")
    if norm < 0.0:
        u_packet = u_raw / math.sqrt(-norm)
        rho_packet = float(u_packet @ demanded_t @ u_packet)

    k_plus = np.array([1.0, -beta + alpha / sqrt_gamma_ll, 0.0, 0.0], dtype=float)
    k_minus = np.array([1.0, -beta - alpha / sqrt_gamma_ll, 0.0, 0.0], dtype=float)
    tkk_plus = float(k_plus @ demanded_t @ k_plus)
    tkk_minus = float(k_minus @ demanded_t @ k_minus)

    return {
        "rho_euler": rho_euler,
        "j_l_unit": j_l_unit,
        "p_l_unit": p_l_unit,
        "p_omega_unit": p_omega_unit,
        "rho_packet": rho_packet,
        "Tkk_plus": tkk_plus,
        "Tkk_minus": tkk_minus,
        "Tkk_min_radial": min(tkk_plus, tkk_minus),
        "packet_norm": norm,
        "gtt": sc["gtt"],
        "spatial_volume_density": sqrt_gamma_ll * gamma_omega,
        **{k: sc[k] for k in [
            "W",
            "W_raw",
            "standing_support_packet_carve_window",
            "standing_support_packet_carve_catch_window",
            "standing_support_packet_carve_shoulder_window",
            "standing_support_packet_coupled_entry_window",
            "standing_support_packet_coupled_catch_window",
            "standing_support_packet_coupled_containment_window",
            "standing_support_packet_coupled_edge_window",
            "standing_support_packet_coupled_rebate_window",
            "standing_support_packet_coupled_radial_window",
            "standing_support_packet_coupled_null_cushion_window",
            "standing_support_packet_smooth_split_entry_window",
            "standing_support_packet_smooth_split_catch_window",
            "standing_support_packet_smooth_split_edge_window",
            "standing_support_packet_smooth_split_current_guard_window",
            "standing_support_packet_smooth_split_guarded_edge_window",
            "standing_support_packet_smooth_split_containment_window",
            "standing_support_packet_smooth_split_null_cushion_window",
            "standing_support_packet_smooth_split_angular_window",
            "support_edge_receiver_memory_driver",
            "support_edge_receiver_radial_cap_window",
            "support_edge_receiver_angular_flange_window",
            "standing_support_packet_raw_carve_contribution",
            "standing_support_packet_coupled_rebate_contribution",
            "standing_support_packet_carve_contribution",
            "standing_support_packet_carve_factor",
            "standing_support_packet_lapse_window",
            "standing_support_packet_lapse_factor",
            "standing_support_packet_null_cushion_window",
            "standing_support_packet_null_cushion_factor",
            "standing_support_packet_coupled_null_cushion_factor",
            "standing_support_packet_smooth_split_null_cushion_factor",
            "standing_support_packet_smooth_split_angular_factor",
            "support_edge_receiver_lapse_factor",
            "support_edge_receiver_radial_factor",
            "support_edge_receiver_angular_factor",
            "standing_support_packet_radial_window",
            "standing_support_packet_radial_shoulder_window",
            "standing_support_packet_radial_skirt_window",
            "standing_support_packet_radial_factor",
            "standing_support_packet_beta_rematch_window",
            "causal_margin_guard_window",
            "release_profile_slope_abs",
            "standing_support_packet_carve_window_slope_abs",
            "standing_support_packet_carve_catch_window_slope_abs",
            "standing_support_packet_coupled_containment_window_slope_abs",
            "standing_support_packet_coupled_edge_window_slope_abs",
            "standing_support_packet_coupled_rebate_window_slope_abs",
            "standing_support_packet_coupled_null_cushion_window_slope_abs",
            "standing_support_packet_smooth_split_containment_window_slope_abs",
            "standing_support_packet_smooth_split_edge_window_slope_abs",
            "standing_support_packet_smooth_split_current_guard_window_slope_abs",
            "standing_support_packet_smooth_split_guarded_edge_window_slope_abs",
            "standing_support_packet_smooth_split_null_cushion_window_slope_abs",
            "standing_support_packet_smooth_split_angular_window_slope_abs",
            "support_edge_receiver_radial_cap_window_slope_abs",
            "support_edge_receiver_angular_flange_window_slope_abs",
            "standing_support_packet_lapse_window_slope_abs",
            "standing_support_packet_null_cushion_window_slope_abs",
            "standing_support_packet_radial_window_slope_abs",
            "standing_support_packet_radial_skirt_window_slope_abs",
            "standing_support_packet_beta_rematch_window_slope_abs",
            "causal_margin_guard_window_slope_abs",
            "standing_support_packet_delta_alpha",
            "standing_support_packet_null_cushion_delta_alpha",
            "standing_support_packet_coupled_null_cushion_delta_alpha",
            "standing_support_packet_smooth_split_null_cushion_delta_alpha",
            "standing_support_packet_smooth_split_delta_gamma_omega",
            "support_edge_receiver_delta_alpha",
            "support_edge_receiver_delta_beta",
            "causal_margin_guard_delta_beta",
            "causal_margin_guard_beta_pre",
            "causal_margin_guard_limit",
            "causal_margin_guard_margin_pre",
            "causal_margin_guard_margin_post",
            "causal_margin_guard_active",
            "support_edge_receiver_delta_gamma_ll",
            "support_edge_receiver_delta_gamma_omega",
            "standing_support_packet_delta_gamma_ll",
            "standing_support_packet_coupled_delta_gamma_ll",
            "standing_support_packet_delta_beta",
            "S",
            "q",
            "E",
            "U_beta",
            "U_packet",
            "B",
            "A",
            "T",
            "alpha",
            "beta",
            "beta_base",
            "beta_pre_packet_rematch",
            "alpha_base",
            "gamma_ll_base",
            "support_shell_window",
            "support_shell_delta_beta",
            "support_shell_clock_lapse_factor",
            "support_shell_delta_alpha",
            "support_shell_rail_stretch_factor",
            "support_shell_delta_gamma_ll",
            "support_shell_throat_capacity_factor",
            "support_shell_delta_gamma_omega",
            "gamma_ll",
            "gamma_omega_base",
            "gamma_omega",
            "COmega",
        ]},
    }


def stage_name(s: float, params: SourceParams) -> str:
    if params.live_packet_start is not None and s < float(params.live_packet_start):
        return "pre_entry_setup"
    width = max(params.w_catch_packet, params.w_catch_beta)
    center = params.x_catch_packet
    release_start, release_end = release_beta_interval(params)
    if s < center - 2.0 * width:
        return "entry_precatch"
    if abs(s - center) <= 2.0 * width:
        return "catch_rematch"
    if not release_choreography_enabled(params):
        release_start = params.x_beta - 2.0 * params.w_beta
        release_end = params.x_beta + 2.0 * params.w_beta
    if center + 2.0 * width < s < release_start:
        return "held_carry"
    if release_start <= s <= release_end:
        return "release_shift_fade"
    if release_end < s < release_end + 2.0 * params.w_beta:
        return "post_release_buffer"
    return "reset_decompression"


def region_name(s: float, l: float, params: SourceParams) -> str:
    al = abs(l)
    if abs(l - s) <= params.Rpass:
        return "packet_in_support" if al <= params.Rth else "packet_outer"
    if al <= 0.65 * params.Rth:
        return "core_throat"
    if al <= 1.20 * params.Rth:
        return "support_edge"
    if al <= 1.85 * params.Rth:
        return "outer_quarantine_shell"
    return "far_exterior"


def live_packet_mask(s: float, l: float, params: SourceParams) -> bool:
    live_end = live_packet_end(params)
    if params.live_packet_start is not None and s < float(params.live_packet_start):
        return False
    return bool(abs(l - s) <= params.Rpass and s <= live_end)


def channel_badness(row: pd.Series | dict[str, Any], channel: str) -> float:
    if channel == "neg_Tkk_radial":
        return max(-float(row["Tkk_min_radial"]), 0.0)
    if channel == "abs_p_l":
        return abs(float(row["p_l_unit"]))
    if channel == "abs_pOmega":
        return abs(float(row["p_omega_unit"]))
    if channel == "abs_j_l":
        return abs(float(row["j_l_unit"]))
    if channel == "neg_rho_euler":
        return max(-float(row["rho_euler"]), 0.0)
    if channel == "neg_rho_packet":
        value = float(row["rho_packet"])
        return max(-value, 0.0) if math.isfinite(value) else 0.0
    raise KeyError(channel)


def scalar_derivative_diagnostics(
    s: float,
    l: float,
    params: SourceParams,
    h_s: float,
    h_l: float,
) -> dict[str, float | str]:
    def scalar_at(s_value: float, l_value: float, key: str) -> float:
        return float(scalars(float(s_value), float(l_value), params)[key])

    rows: dict[str, float | str] = {}
    for key, label in [
        ("alpha", "alpha"),
        ("beta", "beta_l"),
        ("gamma_ll", "gamma_ll"),
        ("gamma_omega", "gamma_Omega"),
    ]:
        center = scalar_at(s, l, key)
        s_plus = scalar_at(s + h_s, l, key)
        s_minus = scalar_at(s - h_s, l, key)
        l_plus = scalar_at(s, l + h_l, key)
        l_minus = scalar_at(s, l - h_l, key)
        d_s = (s_plus - s_minus) / (2.0 * h_s)
        d_l = (l_plus - l_minus) / (2.0 * h_l)
        d2_l = (l_plus - 2.0 * center + l_minus) / (h_l * h_l)
        scale = max(abs(center), 1.0e-12)
        rows[f"d_s_{label}"] = float(d_s)
        rows[f"d_l_{label}"] = float(d_l)
        rows[f"d2_l_{label}"] = float(d2_l)
        rows[f"abs_d_s_{label}"] = float(abs(d_s))
        rows[f"abs_d_l_{label}"] = float(abs(d_l))
        rows[f"abs_d2_l_{label}"] = float(abs(d2_l))
        rows[f"rel_abs_d_s_{label}"] = float(abs(d_s) / scale)
        rows[f"rel_abs_d_l_{label}"] = float(abs(d_l) / scale)
        rows[f"rel_abs_d2_l_{label}"] = float(abs(d2_l) / scale)

    beta_score = (
        float(rows["abs_d_s_beta_l"])
        + float(rows["abs_d_l_beta_l"])
        + math.sqrt(float(rows["abs_d2_l_beta_l"]))
    )
    lapse_score = (
        float(rows["rel_abs_d_s_alpha"])
        + float(rows["rel_abs_d_l_alpha"])
        + math.sqrt(float(rows["rel_abs_d2_l_alpha"]))
    )
    radial_metric_score = (
        float(rows["rel_abs_d_s_gamma_ll"])
        + float(rows["rel_abs_d_l_gamma_ll"])
        + math.sqrt(float(rows["rel_abs_d2_l_gamma_ll"]))
    )
    angular_capacity_score = (
        float(rows["rel_abs_d_s_gamma_Omega"])
        + float(rows["rel_abs_d_l_gamma_Omega"])
        + math.sqrt(float(rows["rel_abs_d2_l_gamma_Omega"]))
    )
    scores = {
        "beta_gradient": beta_score,
        "lapse_curvature": lapse_score,
        "radial_metric": radial_metric_score,
        "angular_capacity": angular_capacity_score,
    }
    for key, value in scores.items():
        rows[f"{key}_score"] = float(value)
    rows["dominant_derivative_family"] = max(scores, key=scores.get)
    return rows


def channel_cause_ledger(
    points: pd.DataFrame,
    params: SourceParams,
    *,
    h_s: float,
    h_l: float,
    limit_per_channel: int = 20,
    channels: Iterable[str] | None = None,
) -> pd.DataFrame:
    selected_channels = list(channels or CHANNELS.keys())
    bad_points = top_bad_points(points, limit=limit_per_channel)
    if bad_points.empty:
        return bad_points
    bad_points = bad_points[bad_points["channel"].isin(selected_channels)].copy()
    point_cols = [
        "case",
        "s",
        "l",
        "stage",
        "region",
        "rho_euler",
        "j_l_unit",
        "p_l_unit",
        "p_omega_unit",
        "rho_packet",
        "Tkk_plus",
        "Tkk_minus",
        "Tkk_min_radial",
        "alpha",
        "beta",
        "gamma_ll",
        "gamma_omega",
        "packet_norm",
    ]
    available_cols = [col for col in point_cols if col in points.columns]
    merged = bad_points.merge(points[available_cols], on=["case", "s", "l", "stage", "region"], how="left")
    rows: list[dict[str, Any]] = []
    for _, row in merged.iterrows():
        rho_h = float(row["rho_euler"])
        p_l = float(row["p_l_unit"])
        j_l = float(row["j_l_unit"])
        alpha = float(row["alpha"])
        alpha_sq = alpha * alpha
        rho_plus_p_l = rho_h + p_l
        two_j_l = 2.0 * j_l
        tkk_plus_orthonormal = float(row["Tkk_plus"]) / alpha_sq if alpha_sq else float("nan")
        tkk_minus_orthonormal = float(row["Tkk_minus"]) / alpha_sq if alpha_sq else float("nan")
        plus_reconstructed = rho_plus_p_l - two_j_l
        minus_reconstructed = rho_plus_p_l + two_j_l
        cancellation_scale = abs(rho_plus_p_l) + abs(two_j_l)
        min_orthonormal = min(tkk_plus_orthonormal, tkk_minus_orthonormal)
        cancellation_ratio = abs(min_orthonormal) / cancellation_scale if cancellation_scale > 0.0 else float("nan")
        derivatives = scalar_derivative_diagnostics(float(row["s"]), float(row["l"]), params, h_s, h_l)
        rows.append({
            **row.to_dict(),
            "rho_H": rho_h,
            "p_l": p_l,
            "j_l": j_l,
            "rho_H_plus_p_l": rho_plus_p_l,
            "two_j_l": two_j_l,
            "Tkk_plus_orthonormal": tkk_plus_orthonormal,
            "Tkk_minus_orthonormal": tkk_minus_orthonormal,
            "Tkk_plus_orthonormal_reconstructed": plus_reconstructed,
            "Tkk_minus_orthonormal_reconstructed": minus_reconstructed,
            "Tkk_plus_reconstruction_error": tkk_plus_orthonormal - plus_reconstructed,
            "Tkk_minus_reconstruction_error": tkk_minus_orthonormal - minus_reconstructed,
            "null_cancellation_scale": cancellation_scale,
            "null_cancellation_ratio": cancellation_ratio,
            "cancellation_sensitive": bool(cancellation_scale > 0.0 and cancellation_ratio < 0.20),
            **derivatives,
        })
    return pd.DataFrame(rows)


def _corr_or_nan(frame: pd.DataFrame, left: str, right: str, method: str = "spearman") -> float:
    if left not in frame.columns or right not in frame.columns or len(frame) < 2:
        return float("nan")
    data = frame[[left, right]].astype(float).replace([np.inf, -np.inf], np.nan).dropna()
    if len(data) < 2 or data[left].nunique() < 2 or data[right].nunique() < 2:
        return float("nan")
    return float(data[left].corr(data[right], method=method))


def shell_throat_mixed_diagnostics(
    s: float,
    l: float,
    params: SourceParams,
    h_s: float,
    h_l: float,
) -> dict[str, float | str]:
    """Return a shell/throat mixed-derivative proxy at one grid point.

    ``Wsh`` is represented by the effective standing-support profile ``W``.
    The proxy is intentionally comparative: it asks whether hard rows line up
    with products of support-window, shift, radial-metric, and angular-capacity
    derivatives, rather than claiming a symbolic stress-tensor decomposition.
    """

    def scalar_at(s_value: float, l_value: float, key: str) -> float:
        return float(scalars(float(s_value), float(l_value), params)[key])

    rows: dict[str, float | str] = {}
    for key, label in [
        ("W", "Wsh"),
        ("W_raw", "Wsh_raw"),
        ("support_shell_window", "support_shell_window"),
        ("beta", "beta_l"),
        ("gamma_ll", "gamma_ll"),
        ("gamma_omega", "gamma_Omega"),
    ]:
        center = scalar_at(s, l, key)
        s_plus = scalar_at(s + h_s, l, key)
        s_minus = scalar_at(s - h_s, l, key)
        l_plus = scalar_at(s, l + h_l, key)
        l_minus = scalar_at(s, l - h_l, key)
        d_s = (s_plus - s_minus) / (2.0 * h_s)
        d_l = (l_plus - l_minus) / (2.0 * h_l)
        d2_l = (l_plus - 2.0 * center + l_minus) / (h_l * h_l)
        scale = max(abs(center), 1.0e-12)
        rows[label] = float(center)
        rows[f"d_s_{label}"] = float(d_s)
        rows[f"d_l_{label}"] = float(d_l)
        rows[f"d2_l_{label}"] = float(d2_l)
        rows[f"abs_d_s_{label}"] = float(abs(d_s))
        rows[f"abs_d_l_{label}"] = float(abs(d_l))
        rows[f"abs_d2_l_{label}"] = float(abs(d2_l))
        rows[f"rel_abs_d_s_{label}"] = float(abs(d_s) / scale)
        rows[f"rel_abs_d_l_{label}"] = float(abs(d_l) / scale)
        rows[f"rel_abs_d2_l_{label}"] = float(abs(d2_l) / scale)

    wsh_shape_score = (
        float(rows["abs_d_s_Wsh"])
        + float(rows["abs_d_l_Wsh"])
        + math.sqrt(float(rows["abs_d2_l_Wsh"]))
    )
    beta_shape_score = (
        float(rows["abs_d_s_beta_l"])
        + float(rows["abs_d_l_beta_l"])
        + math.sqrt(float(rows["abs_d2_l_beta_l"]))
    )
    gamma_ll_shape_score = (
        float(rows["rel_abs_d_s_gamma_ll"])
        + float(rows["rel_abs_d_l_gamma_ll"])
        + math.sqrt(float(rows["rel_abs_d2_l_gamma_ll"]))
    )
    gamma_omega_shape_score = (
        float(rows["rel_abs_d_s_gamma_Omega"])
        + float(rows["rel_abs_d_l_gamma_Omega"])
        + math.sqrt(float(rows["rel_abs_d2_l_gamma_Omega"]))
    )
    shell_gamma_ll = wsh_shape_score * gamma_ll_shape_score
    shell_gamma_omega = wsh_shape_score * gamma_omega_shape_score
    shell_beta = wsh_shape_score * beta_shape_score
    beta_gamma_ll = beta_shape_score * gamma_ll_shape_score
    beta_gamma_omega = beta_shape_score * gamma_omega_shape_score
    ll_omega = gamma_ll_shape_score * gamma_omega_shape_score
    mixed_scores = {
        "shell_gamma_ll": shell_gamma_ll,
        "shell_gamma_omega": shell_gamma_omega,
        "shell_beta": shell_beta,
        "beta_gamma_ll": beta_gamma_ll,
        "beta_gamma_omega": beta_gamma_omega,
        "ll_omega": ll_omega,
    }
    rows.update({
        "Wsh_shape_score": float(wsh_shape_score),
        "beta_shape_score": float(beta_shape_score),
        "gamma_ll_shape_score": float(gamma_ll_shape_score),
        "gamma_Omega_shape_score": float(gamma_omega_shape_score),
        "shell_gamma_ll_mixed_score": float(shell_gamma_ll),
        "shell_gamma_Omega_mixed_score": float(shell_gamma_omega),
        "shell_beta_mixed_score": float(shell_beta),
        "beta_gamma_ll_mixed_score": float(beta_gamma_ll),
        "beta_gamma_Omega_mixed_score": float(beta_gamma_omega),
        "gamma_ll_gamma_Omega_mixed_score": float(ll_omega),
        "shell_throat_mixed_score": float(sum(mixed_scores.values())),
        "dominant_mixed_family": max(mixed_scores, key=mixed_scores.get),
    })
    return rows


def shell_throat_overlap_proxy_ledger(
    points: pd.DataFrame,
    params: SourceParams,
    *,
    h_s: float,
    h_l: float,
    limit_per_channel: int = 20,
    channels: Iterable[str] | None = None,
) -> pd.DataFrame:
    selected_channels = list(channels or ["neg_Tkk_radial", "abs_p_l", "abs_j_l", "abs_pOmega"])
    bad_points = top_bad_points(points, limit=limit_per_channel)
    if bad_points.empty:
        return bad_points
    bad_points = bad_points[bad_points["channel"].isin(selected_channels)].copy()
    point_cols = [
        "case",
        "s",
        "l",
        "stage",
        "region",
        "rho_euler",
        "j_l_unit",
        "p_l_unit",
        "p_omega_unit",
        "Tkk_min_radial",
        "packet_norm",
        "W",
        "W_raw",
        "support_shell_window",
        "beta",
        "gamma_ll",
        "gamma_omega",
    ]
    available_cols = [col for col in point_cols if col in points.columns]
    merged = bad_points.merge(points[available_cols], on=["case", "s", "l", "stage", "region"], how="left")
    rows: list[dict[str, Any]] = []
    for _, row in merged.iterrows():
        mixed = shell_throat_mixed_diagnostics(float(row["s"]), float(row["l"]), params, h_s, h_l)
        rows.append({**row.to_dict(), **mixed})
    return pd.DataFrame(rows)


def shell_throat_overlap_summary(proxy: pd.DataFrame) -> pd.DataFrame:
    if proxy.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    score_columns = [
        "shell_throat_mixed_score",
        "shell_gamma_ll_mixed_score",
        "shell_gamma_Omega_mixed_score",
        "shell_beta_mixed_score",
        "beta_gamma_ll_mixed_score",
        "beta_gamma_Omega_mixed_score",
        "gamma_ll_gamma_Omega_mixed_score",
    ]

    def bool_column(group: pd.DataFrame, name: str) -> pd.Series:
        for candidate in [name, f"{name}_x", f"{name}_y"]:
            if candidate in group.columns:
                return group[candidate].astype(bool)
        return pd.Series(False, index=group.index)

    for (case_name, channel), group in proxy.groupby(["case", "channel"], sort=False):
        finite_badness = group["badness"].astype(float).replace([np.inf, -np.inf], np.nan).dropna()
        dominant = group["dominant_mixed_family"].astype(str).mode()
        row: dict[str, Any] = {
            "case": case_name,
            "channel": channel,
            "rows": int(len(group)),
            "live_rows": int(bool_column(group, "inside_packet_live").sum()),
            "geometric_packet_rows": int(bool_column(group, "inside_packet_geom").sum()),
            "mean_badness": float(finite_badness.mean()) if len(finite_badness) else float("nan"),
            "max_badness": float(finite_badness.max()) if len(finite_badness) else float("nan"),
            "mean_Wsh": float(group["Wsh"].astype(float).mean()),
            "mean_Wsh_shape_score": float(group["Wsh_shape_score"].astype(float).mean()),
            "mean_beta_shape_score": float(group["beta_shape_score"].astype(float).mean()),
            "mean_gamma_ll_shape_score": float(group["gamma_ll_shape_score"].astype(float).mean()),
            "mean_gamma_Omega_shape_score": float(group["gamma_Omega_shape_score"].astype(float).mean()),
            "dominant_mixed_family_mode": str(dominant.iloc[0]) if not dominant.empty else "",
        }
        for column in score_columns:
            values = group[column].astype(float)
            row[f"mean_{column}"] = float(values.mean())
            row[f"max_{column}"] = float(values.max())
            row[f"spearman_badness_{column}"] = _corr_or_nan(group, "badness", column, method="spearman")
        rows.append(row)
    return pd.DataFrame(rows)


def compute_case(
    case: SourceCase,
    ns: int,
    nl: int,
    s_min: float = -0.35,
    s_max: float = 1.65,
    l_min: float = -2.80,
    l_max: float = 2.80,
    h_s: float = 2.5e-3,
    h_l: float = 2.5e-3,
    progress: bool = True,
) -> pd.DataFrame:
    if ns < 3 or nl < 3:
        raise ValueError(f"source-ledger grid must be at least 3 x 3, got {ns} x {nl}")
    params = case.params
    s_grid = np.linspace(s_min, s_max, ns)
    l_grid = np.linspace(l_min, l_max, nl)
    ds = float((s_max - s_min) / max(ns - 1, 1))
    dl = float((l_max - l_min) / max(nl - 1, 1))
    rows: list[dict[str, Any]] = []
    for row_index, s in enumerate(s_grid, start=1):
        for l in l_grid:
            base = {
                "case": case.name,
                "s": float(s),
                "l": float(l),
                "stage": stage_name(float(s), params),
                "region": region_name(float(s), float(l), params),
                "inside_packet_geom": abs(float(l) - float(s)) <= params.Rpass,
                "inside_packet_live": live_packet_mask(float(s), float(l), params),
                "cell_area": ds * dl,
            }
            try:
                einstein, diagnostics = einstein_tensor_at(float(s), float(l), params, h_s, h_l)
                projected = projections(float(s), float(l), einstein, params)
                row = {**base, **projected, **diagnostics}
                row["point_weight"] = 1.0
                row["volume_weight"] = float(projected["spatial_volume_density"] * ds * dl)
                for channel in CHANNELS:
                    bad = channel_badness(row, channel)
                    row[f"bad_{channel}"] = bad
                    row[f"point_burden_{channel}"] = bad
                    row[f"volume_burden_{channel}"] = bad * row["volume_weight"]
                rows.append(row)
            except Exception as exc:
                rows.append({**base, "error": repr(exc)})
        if progress and (row_index == ns or row_index % max(1, ns // 5) == 0):
            print(f"{case.name}: row {row_index}/{ns}", flush=True)
    return pd.DataFrame(rows)


def summarize(points: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if "error" in points.columns:
        ok = points[points["error"].isna()].copy()
    else:
        ok = points.copy()
    long_rows: list[dict[str, Any]] = []
    for scope, cols in [
        ("global", ["case"]),
        ("stage", ["case", "stage"]),
        ("region", ["case", "region"]),
        ("stage_region", ["case", "stage", "region"]),
    ]:
        for key, group in ok.groupby(cols, dropna=False):
            if not isinstance(key, tuple):
                key = (key,)
            base = {"scope": scope, **{col: value for col, value in zip(cols, key)}, "points": int(len(group))}
            live = group["inside_packet_live"].astype(bool).to_numpy()
            geom = group["inside_packet_geom"].astype(bool).to_numpy()
            for channel, description in CHANNELS.items():
                for weight in ["point", "volume"]:
                    values = group[f"{weight}_burden_{channel}"].astype(float).to_numpy()
                    total = float(np.nansum(values))
                    live_burden = float(np.nansum(values[live]))
                    geom_burden = float(np.nansum(values[geom]))
                    live_group = group.loc[group["inside_packet_live"].astype(bool), f"bad_{channel}"].astype(float)
                    long_rows.append({
                        **base,
                        "channel": channel,
                        "description": description,
                        "weight": weight,
                        "total_burden": total,
                        "live_packet_burden": live_burden,
                        "geometric_packet_burden": geom_burden,
                        "infrastructure_or_reset_burden": total - live_burden,
                        "live_packet_fraction": live_burden / total if total > 0.0 else float("nan"),
                        "geometric_packet_fraction": geom_burden / total if total > 0.0 else float("nan"),
                        "point_peak": float(group[f"bad_{channel}"].astype(float).max()),
                        "live_packet_point_peak": float(live_group.max()) if len(live_group) else 0.0,
                    })
    summary = pd.DataFrame(long_rows)
    compact = summary[(summary["scope"] == "global") & (summary["weight"] == "volume")].copy()
    compact = compact[[
        "case",
        "channel",
        "description",
        "total_burden",
        "live_packet_burden",
        "live_packet_fraction",
        "point_peak",
        "live_packet_point_peak",
    ]]
    stage = summary[(summary["scope"] == "stage") & (summary["weight"] == "volume")].copy()
    stage["stage"] = pd.Categorical(stage["stage"], categories=STAGE_ORDER, ordered=True)
    stage = stage.sort_values(["case", "channel", "stage"])
    safety = summarize_safety(ok)
    decision = build_decision_table(compact, safety)
    return summary, compact, stage, safety, decision


def _smeared_scope_mask(points: pd.DataFrame, scope: str) -> pd.Series:
    if scope == "global":
        return pd.Series(True, index=points.index)
    if scope == "live_packet":
        return points["inside_packet_live"].astype(bool)
    if scope == "geometric_packet":
        return points["inside_packet_geom"].astype(bool)
    if scope == "catch_rematch":
        return points["stage"].astype(str).eq("catch_rematch")
    if scope == "catch_rematch_live_packet":
        return points["stage"].astype(str).eq("catch_rematch") & points["inside_packet_live"].astype(bool)
    if scope == "packet_in_support":
        return points["region"].astype(str).eq("packet_in_support")
    if scope == "catch_packet_in_support":
        return points["stage"].astype(str).eq("catch_rematch") & points["region"].astype(str).eq("packet_in_support")
    raise ValueError(f"unknown smeared-null scope: {scope}")


def smeared_null_summary(
    points: pd.DataFrame,
    *,
    smear_widths: Iterable[float] = (0.25, 0.50, 1.00),
    scopes: Iterable[str] | None = None,
    centers_per_scope: int = 20,
    benchmark_b: float = 1.0 / (32.0 * math.pi),
) -> pd.DataFrame:
    """Return local smeared radial-null diagnostics for source-ledger points.

    This is a semilocal harness diagnostic, not a full SNEC implementation.
    It uses Gaussian windows on the sampled (s, l) ledger grid, centered on
    the worst radial-null points inside each scope, to test whether a candidate
    reduces local accumulation of negative radial-null contraction. The
    benchmark floor reports the geometric SNEC scale -8*pi*B/tau^2 with
    tau identified with the chosen grid-coordinate smear width.
    """

    selected_scopes = list(scopes or [
        "global",
        "live_packet",
        "geometric_packet",
        "catch_rematch",
        "catch_rematch_live_packet",
        "packet_in_support",
        "catch_packet_in_support",
    ])
    if "error" in points.columns:
        ok = points[points["error"].isna()].copy()
    else:
        ok = points.copy()
    required = {"case", "s", "l", "Tkk_min_radial", "bad_neg_Tkk_radial"}
    missing = sorted(required.difference(ok.columns))
    if missing:
        raise ValueError(f"smeared-null summary missing required columns: {missing}")

    measure = ok["cell_area"].astype(float).to_numpy() if "cell_area" in ok.columns else np.ones(len(ok))
    rows: list[dict[str, Any]] = []
    for case_name, case_group in ok.groupby("case"):
        case_index = case_group.index.to_numpy()
        case_measure = measure[ok.index.get_indexer(case_index)]
        s_values = case_group["s"].astype(float).to_numpy()
        l_values = case_group["l"].astype(float).to_numpy()
        tkk_values = case_group["Tkk_min_radial"].astype(float).to_numpy()
        neg_values = np.maximum(-tkk_values, 0.0)
        for scope in selected_scopes:
            scope_mask = _smeared_scope_mask(case_group, scope).to_numpy()
            scoped = case_group.loc[scope_mask].copy()
            if scoped.empty:
                continue
            candidates = scoped.sort_values("bad_neg_Tkk_radial", ascending=False).head(centers_per_scope)
            if candidates.empty:
                continue
            for width in smear_widths:
                tau = float(width)
                if tau <= 0.0:
                    raise ValueError(f"smear widths must be positive, got {tau}")
                best: dict[str, Any] | None = None
                for _, center in candidates.iterrows():
                    ds = (s_values - float(center["s"])) / tau
                    dl = (l_values - float(center["l"])) / tau
                    gaussian = np.exp(-0.5 * (ds * ds + dl * dl))
                    weights = gaussian * scope_mask.astype(float) * case_measure
                    norm = float(np.nansum(weights))
                    if norm <= 0.0:
                        continue
                    smeared_tkk = float(np.nansum(weights * tkk_values) / norm)
                    smeared_neg_part = float(np.nansum(weights * neg_values) / norm)
                    point_badness = float(center["bad_neg_Tkk_radial"])
                    record = {
                        "case": case_name,
                        "scope": scope,
                        "smear_width": tau,
                        "center_s": float(center["s"]),
                        "center_l": float(center["l"]),
                        "center_stage": center.get("stage", ""),
                        "center_region": center.get("region", ""),
                        "center_inside_packet_live": bool(center.get("inside_packet_live", False)),
                        "center_bad_neg_Tkk_radial": point_badness,
                        "smeared_Tkk_min_radial": smeared_tkk,
                        "smeared_neg_Tkk_part": smeared_neg_part,
                        "window_weight_norm": norm,
                        "scope_points": int(scope_mask.sum()),
                    }
                    if best is None or smeared_tkk < float(best["smeared_Tkk_min_radial"]):
                        best = record
                if best is None:
                    continue
                floor = -8.0 * math.pi * float(benchmark_b) / (tau * tau)
                best["benchmark_B"] = float(benchmark_b)
                best["benchmark_geometric_floor"] = float(floor)
                best["margin_to_benchmark_geometric_floor"] = float(best["smeared_Tkk_min_radial"] - floor)
                rows.append(best)
    return pd.DataFrame(rows)


def top_bad_points(points: pd.DataFrame, limit: int = 20) -> pd.DataFrame:
    if "error" in points.columns:
        ok = points[points["error"].isna()].copy()
    else:
        ok = points.copy()
    rows: list[dict[str, Any]] = []
    for case_name, case_group in ok.groupby("case"):
        for channel, description in CHANNELS.items():
            burden_col = f"volume_burden_{channel}"
            if burden_col not in case_group.columns:
                continue
            ranked = case_group.sort_values(burden_col, ascending=False).head(limit)
            for rank, (_, row) in enumerate(ranked.iterrows(), start=1):
                rows.append({
                    "case": case_name,
                    "channel": channel,
                    "description": description,
                    "rank": rank,
                    "s": float(row["s"]),
                    "l": float(row["l"]),
                    "stage": row["stage"],
                    "region": row["region"],
                    "inside_packet_live": bool(row["inside_packet_live"]),
                    "inside_packet_geom": bool(row["inside_packet_geom"]),
                    "badness": float(row[f"bad_{channel}"]),
                    "volume_weight": float(row["volume_weight"]),
                    "volume_burden": float(row[burden_col]),
                    "point_burden": float(row[f"point_burden_{channel}"]),
                    "packet_norm": float(row["packet_norm"]),
                })
    return pd.DataFrame(rows)


def summarize_safety(points: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for case_name, group in points.groupby("case"):
        live = group[group["inside_packet_live"].astype(bool)]
        rows.append({
            "case": case_name,
            "live_points": int(len(live)),
            "max_packet_norm_live": float(live["packet_norm"].astype(float).max()) if len(live) else float("nan"),
            "min_packet_norm_live": float(live["packet_norm"].astype(float).min()) if len(live) else float("nan"),
            "positive_packet_norm_live": int((live["packet_norm"].astype(float) > 0.0).sum()) if len(live) else 0,
        })
    return pd.DataFrame(rows)


def build_decision_table(compact: pd.DataFrame, safety: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    pivot: dict[str, dict[str, Any]] = {}
    for case_name, group in compact.groupby("case"):
        row: dict[str, Any] = {"case": case_name}
        for _, item in group.iterrows():
            channel = str(item["channel"])
            for key in ["total_burden", "live_packet_burden", "live_packet_fraction", "point_peak", "live_packet_point_peak"]:
                row[f"{key}__{channel}"] = float(item[key])
        pivot[case_name] = row
    base = pivot.get("shaped_base") or next(iter(pivot.values()))
    for row in pivot.values():
        for channel in ["neg_Tkk_radial", "abs_p_l", "abs_pOmega", "abs_j_l"]:
            for key in ["live_packet_burden", "total_burden", "live_packet_fraction", "point_peak", "live_packet_point_peak"]:
                full_key = f"{key}__{channel}"
                denominator = base.get(full_key, float("nan"))
                numerator = row.get(full_key, float("nan"))
                if denominator and math.isfinite(float(denominator)):
                    row[f"{full_key}_ratio_vs_base"] = float(numerator) / float(denominator)
                else:
                    row[f"{full_key}_ratio_vs_base"] = float("nan")
        rows.append(row)
    decision = pd.DataFrame(rows).merge(safety, on="case", how="left")
    decision["unsafe_penalty"] = (decision["positive_packet_norm_live"] > 0).astype(float) * 10.0
    decision["pl_live_ratio"] = decision["live_packet_burden__abs_p_l_ratio_vs_base"]
    decision["tkk_live_ratio"] = decision["live_packet_burden__neg_Tkk_radial_ratio_vs_base"]
    decision["pl_peak_ratio"] = decision["point_peak__abs_p_l_ratio_vs_base"]
    decision["tkk_peak_ratio"] = decision["point_peak__neg_Tkk_radial_ratio_vs_base"]
    decision["infra_pressure_ratio"] = decision["total_burden__abs_p_l_ratio_vs_base"]
    decision["score"] = (
        decision["pl_live_ratio"]
        + 0.30 * np.maximum(decision["tkk_live_ratio"] - 1.0, 0.0)
        + 0.20 * np.maximum(decision["pl_peak_ratio"] - 1.0, 0.0)
        + 0.10 * np.maximum(decision["infra_pressure_ratio"] - 1.0, 0.0)
        + decision["unsafe_penalty"]
    )
    return decision.sort_values("score")


def branch_case(variant: str, service_factor: float = 5.0, **overrides: Any) -> SourceCase:
    base = SourceParams(V=float(service_factor))
    variant_key = variant.strip().lower()
    params = base
    note = "locked-lead shaped-catch baseline"
    name = "shaped_base"
    if variant_key in {"shaped", "shaped_base", "baseline"}:
        params = replace(base, eta_N=1.0, w_th=0.35)
        name = "shaped_base"
    elif variant_key in {"selected", "tuned", "tuned_w0569_eta200", "support_shell_reference"}:
        params = replace(base, w_th=0.569, eta_N=2.0)
        name = "tuned_w0569_eta200"
        note = "selected shaped-catch radial-soft lapse-cushion branch"
    elif variant_key in {"conservative", "conservative_w0565_eta200"}:
        params = replace(base, w_th=0.565, eta_N=2.0)
        name = "conservative_w0565_eta200"
        note = "slightly conservative radial-soft lapse-cushion branch"
    elif variant_key in {"cliff", "cliff_w0570_eta200"}:
        params = replace(base, w_th=0.570, eta_N=2.0)
        name = "cliff_w0570_eta200"
        note = "one-step widened cliff comparator"
    elif variant_key == "custom":
        name = "custom"
        note = "custom source-ledger branch"
    else:
        raise ValueError(f"Unknown source-ledger variant {variant!r}")

    valid_fields = set(SourceParams.__dataclass_fields__)
    filtered = {key: value for key, value in overrides.items() if key in valid_fields and value is not None}
    if filtered:
        params = replace(params, **filtered)
    case_name = f"V{params.V:g}_{name}"
    if release_choreography_enabled(params):
        case_name = (
            f"{case_name}_rel{params.release_choreography_mode}"
            f"_rhold{_token(params.release_matched_hold_widths)}"
            f"_rprof{params.release_beta_profile}"
            f"_rw{_token(params.release_beta_width_multiplier)}"
            f"_rllag{_token(params.release_lapse_lag_widths)}"
            f"_rclag{_token(params.release_carve_lag_widths)}"
        )
        note = f"{note}; coordinated release choreography"
    if params.live_packet_start is not None:
        case_name = f"{case_name}_livestart{_token(float(params.live_packet_start))}"
        note = f"{note}; explicit live packet entry start"
    if params.support_shell_overlay_enabled:
        case_name = (
            f"{case_name}_shell_a{_token(params.support_shell_amplitude)}"
            f"_lead{_token(params.support_shell_catch_lead)}"
            f"_tw{_token(params.support_shell_temporal_width)}"
        )
        if params.support_shell_temporal_profile != "gaussian":
            case_name = f"{case_name}_tp{params.support_shell_temporal_profile}"
        if params.support_shell_temporal_shoulder is not None:
            case_name = f"{case_name}_ts{_token(params.support_shell_temporal_shoulder)}"
        if params.support_shell_radial_profile != "smooth_box":
            case_name = f"{case_name}_rp{params.support_shell_radial_profile}"
        if params.support_shell_clock_lapse_log_gain:
            case_name = f"{case_name}_cl{_token(params.support_shell_clock_lapse_log_gain)}"
        if params.support_shell_rail_stretch_log_gain:
            case_name = f"{case_name}_rs{_token(params.support_shell_rail_stretch_log_gain)}"
        if params.support_shell_throat_capacity_log_gain:
            case_name = f"{case_name}_tc{_token(params.support_shell_throat_capacity_log_gain)}"
        note = f"{note}; continuous support-shell metric overlay"
    if params.standing_support_packet_exclusion:
        case_name = (
            f"{case_name}_wcarve{_token(params.standing_support_packet_exclusion)}"
            f"_wr{_token(params.standing_support_packet_exclusion_radius_multiplier)}"
            f"_ww{_token(params.standing_support_packet_exclusion_width_multiplier)}"
            f"_ws{params.standing_support_packet_exclusion_schedule}"
        )
        if params.standing_support_packet_exclusion_temporal_profile != "tanh":
            case_name = f"{case_name}_wtp{params.standing_support_packet_exclusion_temporal_profile}"
    if params.standing_support_packet_exclusion_catch:
        case_name = (
            f"{case_name}_wccarve{_token(params.standing_support_packet_exclusion_catch)}"
            f"_wcr{_token(params.standing_support_packet_exclusion_catch_radius_multiplier)}"
            f"_wcw{_token(params.standing_support_packet_exclusion_catch_width_multiplier)}"
            f"_wcs{params.standing_support_packet_exclusion_catch_schedule}"
        )
        if params.standing_support_packet_exclusion_catch_temporal_profile != "tanh":
            case_name = f"{case_name}_wctp{params.standing_support_packet_exclusion_catch_temporal_profile}"
    if params.standing_support_packet_exclusion_shoulder:
        case_name = (
            f"{case_name}_wshoulder{_token(params.standing_support_packet_exclusion_shoulder)}"
            f"_wsm{params.standing_support_packet_exclusion_shoulder_mode}"
            f"_wsr{_token(params.standing_support_packet_exclusion_shoulder_radius_multiplier)}"
            f"_wsw{_token(params.standing_support_packet_exclusion_shoulder_width_multiplier)}"
            f"_wss{params.standing_support_packet_exclusion_shoulder_schedule}"
        )
        if params.standing_support_packet_exclusion_shoulder_temporal_profile != "tanh":
            case_name = f"{case_name}_wstp{params.standing_support_packet_exclusion_shoulder_temporal_profile}"
        note = f"{note}; experimental standing-support packet carve-out"
    if params.standing_support_packet_lapse_log_gain:
        case_name = (
            f"{case_name}_wlap{_token(params.standing_support_packet_lapse_log_gain)}"
            f"_wlr{_token(params.standing_support_packet_lapse_radius_multiplier)}"
            f"_wlw{_token(params.standing_support_packet_lapse_width_multiplier)}"
            f"_wls{params.standing_support_packet_lapse_schedule}"
        )
        if params.standing_support_packet_lapse_temporal_profile != "tanh":
            case_name = f"{case_name}_wltp{params.standing_support_packet_lapse_temporal_profile}"
        note = f"{note}; experimental packet-local lapse compensator"
    if params.standing_support_packet_null_cushion_log_gain:
        case_name = (
            f"{case_name}_wnull{_token(params.standing_support_packet_null_cushion_log_gain)}"
            f"_wnm{params.standing_support_packet_null_cushion_mode}"
            f"_wnr{_token(params.standing_support_packet_null_cushion_radius_multiplier)}"
            f"_wnw{_token(params.standing_support_packet_null_cushion_width_multiplier)}"
            f"_wns{params.standing_support_packet_null_cushion_schedule}"
        )
        if params.standing_support_packet_null_cushion_temporal_profile != "tanh":
            case_name = f"{case_name}_wntp{params.standing_support_packet_null_cushion_temporal_profile}"
        note = f"{note}; experimental packet-local null cushion"
    if (
        params.standing_support_packet_radial_log_gain
        or params.standing_support_packet_radial_shoulder_log_gain
        or params.standing_support_packet_radial_skirt_log_gain
    ):
        case_name = (
            f"{case_name}_wrad{_token(params.standing_support_packet_radial_log_gain)}"
            f"_wrr{_token(params.standing_support_packet_radial_radius_multiplier)}"
            f"_wrw{_token(params.standing_support_packet_radial_width_multiplier)}"
            f"_wrs{params.standing_support_packet_radial_schedule}"
            f"_wrsh{_token(params.standing_support_packet_radial_shoulder_log_gain)}"
            f"_wrsm{params.standing_support_packet_radial_shoulder_mode}"
            f"_wrsr{_token(params.standing_support_packet_radial_shoulder_radius_multiplier)}"
            f"_wrsw{_token(params.standing_support_packet_radial_shoulder_width_multiplier)}"
            f"_wrss{params.standing_support_packet_radial_shoulder_schedule}"
            f"_wrsk{_token(params.standing_support_packet_radial_skirt_log_gain)}"
            f"_wrskr{_token(params.standing_support_packet_radial_skirt_radius_multiplier)}"
            f"_wrskw{_token(params.standing_support_packet_radial_skirt_width_multiplier)}"
        )
        if params.standing_support_packet_radial_temporal_profile != "tanh":
            case_name = f"{case_name}_wrtp{params.standing_support_packet_radial_temporal_profile}"
        if params.standing_support_packet_radial_shoulder_temporal_profile != "tanh":
            case_name = f"{case_name}_wrstp{params.standing_support_packet_radial_shoulder_temporal_profile}"
        if params.standing_support_packet_radial_skirt_temporal_profile != "tanh":
            case_name = f"{case_name}_wrsktp{params.standing_support_packet_radial_skirt_temporal_profile}"
        note = f"{note}; experimental packet-local radial metric smoothing"
    if params.standing_support_packet_beta_rematch_gain:
        case_name = (
            f"{case_name}_wbeta{_token(params.standing_support_packet_beta_rematch_gain)}"
            f"_wbshape{params.standing_support_packet_beta_rematch_shape}"
            f"_wbr{_token(params.standing_support_packet_beta_rematch_radius_multiplier)}"
            f"_wbw{_token(params.standing_support_packet_beta_rematch_width_multiplier)}"
            f"_wbi{_token(params.standing_support_packet_beta_rematch_inner_radius_multiplier)}"
            f"_wbo{_token(params.standing_support_packet_beta_rematch_outer_radius_multiplier)}"
            f"_wbe{_token(params.standing_support_packet_beta_rematch_edge_softness)}"
            f"_wbt{_token(params.standing_support_packet_beta_rematch_temporal_width_multiplier)}"
            f"_wbf{_token(params.standing_support_packet_beta_rematch_center_floor)}"
            f"_wbfm{params.standing_support_packet_beta_rematch_floor_mode}"
            f"_wbs{params.standing_support_packet_beta_rematch_schedule}"
        )
        if params.standing_support_packet_beta_rematch_temporal_profile != "tanh":
            case_name = f"{case_name}_wbtp{params.standing_support_packet_beta_rematch_temporal_profile}"
        note = f"{note}; experimental packet-local beta rematch"
    if params.causal_margin_guard_enabled:
        case_name = (
            f"{case_name}_cguard{_token(params.causal_margin_guard_margin)}"
            f"_cgs{_token(params.causal_margin_guard_strength)}"
            f"_cgw{params.causal_margin_guard_window_mode}"
            f"_cgr{_token(params.causal_margin_guard_radius_multiplier)}"
            f"_cgww{_token(params.causal_margin_guard_width_multiplier)}"
            f"_cgsch{params.causal_margin_guard_schedule}"
            f"_cgt{_token(params.causal_margin_guard_temporal_width_multiplier)}"
        )
        if params.causal_margin_guard_temporal_profile != "tanh":
            case_name = f"{case_name}_cgtp{params.causal_margin_guard_temporal_profile}"
        if params.causal_margin_guard_radial_profile != "tanh":
            case_name = f"{case_name}_cgrp{params.causal_margin_guard_radial_profile}"
        note = f"{note}; experimental causal-margin guard"
    return SourceCase(case_name, params, note)


def read_reference_table(path: str | Path) -> pd.DataFrame:
    text = str(path)
    if "::" in text:
        zip_path, member = text.split("::", 1)
        with zipfile.ZipFile(zip_path) as zf:
            with zf.open(member) as handle:
                return pd.read_csv(handle)
    return pd.read_csv(Path(path))


def compare_to_reference(
    generated: pd.DataFrame,
    reference: pd.DataFrame,
    *,
    reference_case: str | None = None,
    columns: Iterable[str] | None = None,
    coordinate_decimals: int = 12,
) -> pd.DataFrame:
    gen = generated.copy()
    ref = reference.copy()
    if reference_case and "case" in ref.columns:
        ref = ref[ref["case"].astype(str).eq(reference_case)].copy()
    for frame in (gen, ref):
        frame["_s_key"] = frame["s"].astype(float).round(coordinate_decimals)
        frame["_l_key"] = frame["l"].astype(float).round(coordinate_decimals)
    cols = list(columns or [
        "packet_norm",
        "rho_euler",
        "j_l_unit",
        "p_l_unit",
        "p_omega_unit",
        "rho_packet",
        "Tkk_min_radial",
        "bad_neg_Tkk_radial",
        "bad_abs_p_l",
        "bad_abs_pOmega",
        "bad_abs_j_l",
    ])
    merged = gen.merge(ref, on=["_s_key", "_l_key"], how="inner", suffixes=("_generated", "_reference"))
    rows: list[dict[str, Any]] = []
    for col in cols:
        gen_col = f"{col}_generated"
        ref_col = f"{col}_reference"
        if gen_col not in merged.columns or ref_col not in merged.columns:
            continue
        delta = merged[gen_col].astype(float) - merged[ref_col].astype(float)
        finite = np.isfinite(delta.to_numpy())
        values = delta.to_numpy()[finite]
        rows.append({
            "column": col,
            "generated_rows": int(len(gen)),
            "reference_rows": int(len(ref)),
            "matched_rows": int(len(merged)),
            "finite_rows": int(values.size),
            "max_abs_error": float(np.max(np.abs(values))) if values.size else float("nan"),
            "mean_abs_error": float(np.mean(np.abs(values))) if values.size else float("nan"),
            "rms_error": float(np.sqrt(np.mean(values * values))) if values.size else float("nan"),
        })
    return pd.DataFrame(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def source_module_sha() -> str:
    return sha256_file(Path(__file__))


def case_metadata(case: SourceCase, grid: dict[str, Any], files: dict[str, str]) -> dict[str, Any]:
    return {
        "case": case.name,
        "note": case.note,
        "params": asdict(case.params),
        "grid": grid,
        "files": files,
        "source_ledger_module_sha256": source_module_sha(),
        "caveat": "Finite-difference prescribed-geometry demanded-source diagnostic; not a matter model, not RSET, not a constraint solve.",
    }
