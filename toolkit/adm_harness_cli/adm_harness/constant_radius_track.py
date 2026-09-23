"""Constant-radius track with static end transitions to an exactly flat exterior.

For radial null k in a spherical spacetime, T(k,k) = -H(k,k)/(4 pi R), where H
is the Hessian of the areal radius. The beta075 Type IV layer comes from
service dynamics acting where R varies along the rail. This candidate keeps R
equal to a track radius along the whole service length, confines every
time-dependent field to |l| < track_half_length with a C-infinity cutoff, and
places the widening into the model's two asymptotic ends in static
ultrastatic transitions that join flat space. The service metric (alpha,
beta, gamma_ll) is either the regularity-repaired beta075 metric, whose
repaired joins match through second derivatives, or a C-infinity
reconstruction of it; the reconstruction reproduces the frozen kernel exactly
when its legacy primitives are selected. Smoothness classes here are
differentiability classes, distinct from the topology family labels.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math

import numpy as np
from scipy.special import expit

from .metric_regularity import regularized_scalars
from .source_ledger import (
    SourceParams, bump_sq, falloff, live_packet_end, release_beta_interval, smooth_box,
    smoothstep7, smoothstep_minjerk,
)

_NODES, _WEIGHTS = np.polynomial.legendre.leggauss(48)


@dataclass(frozen=True)
class ConstantRadiusTrackDesign:
    track_radius: float = 1.75
    service_inner: float = 4.0
    track_half_length: float = 5.0
    transition_width: float = 1.5
    smooth_service: bool = True
    abs_width: float = .02
    cap_width: float = .25
    join_fraction: float = .1
    reset_front_start: float | None = None
    reset_front_speed: float = 1.
    reset_front_origin: float = -1.4
    reset_front_duration: float = 3.
    reset_front_ramp: float = .25
    standing_support: bool = False

    def __post_init__(self):
        values = (self.track_radius, self.service_inner, self.track_half_length, self.transition_width,
                  self.abs_width, self.cap_width, self.join_fraction)
        if not all(math.isfinite(x) for x in values):
            raise ValueError("flat-throat design values must be finite")
        if min(self.track_radius, self.service_inner, self.transition_width, self.abs_width) <= 0:
            raise ValueError("radius, widths and service extent must be positive")
        if self.track_half_length <= self.service_inner:
            raise ValueError("the service cutoff must end before the end transition begins")
        if not 0 < self.cap_width < .5 or not 0 < self.join_fraction < .5:
            raise ValueError("cap width and join fraction must lie in (0, 0.5)")
        if self.reset_front_start is not None:
            front = (self.reset_front_start, self.reset_front_speed, self.reset_front_origin,
                     self.reset_front_duration, self.reset_front_ramp)
            if not all(math.isfinite(x) for x in front) or min(front[1], front[3], front[4]) <= 0:
                raise ValueError("a reset front needs finite values and positive speed, duration and ramp")
            if self.standing_support:
                raise ValueError("a standing support has no decompression front")

    @property
    def reset_front(self):
        if self.reset_front_start is None:
            return None
        return (self.reset_front_start, self.reset_front_speed, self.reset_front_origin,
                self.reset_front_duration, self.reset_front_ramp)


def smooth_step(t: float) -> float:
    """C-infinity step: 0 for t <= 0, 1 for t >= 1, every derivative zero at both ends."""
    if t <= 0:
        return 0.
    if t >= 1:
        return 1.
    return float(expit(1/(1-t)-1/t))


def _step_array(t: np.ndarray) -> np.ndarray:
    inside = (t > 0) & (t < 1)
    safe = np.where(inside, t, .5)
    return np.where(t >= 1, 1., np.where(inside, expit(1/(1-safe)-1/safe), 0.))


def flattened_step(t: float, base, fraction: float) -> float:
    """C-infinity version of a polynomial step that is exact on [fraction, 1-fraction].

    The base step is multiplied by smooth_step on the first join fraction and
    its complement likewise on the last, so every derivative vanishes at both
    ends while the monotone interior profile is retained.
    """
    if t <= 0:
        return 0.
    if t >= 1:
        return 1.
    value = float(base(t))
    if t <= .5:
        return value*smooth_step(t/fraction)
    return 1.-(1.-value)*smooth_step((1.-t)/fraction)


def smooth_abs(x: float, width: float) -> float:
    """Even analytic stand-in for |x|; it differs from |x| by at most 2|x|exp(-2|x|/width)."""
    return x*math.tanh(x/width)


def smooth_cap(x: float, width: float) -> float:
    """Monotone C-infinity cap: identity below 1-width and exactly one from one upward."""
    if x <= 1-width:
        return x
    if x >= 1:
        return 1.
    weight = smooth_step((x-(1-width))/width)
    return x+(1-x)*weight


def transition_integral(t: float) -> float:
    """Integral of smooth_step from 0 to t; it equals t - 1/2 for t >= 1."""
    if t <= 0:
        return 0.
    if t >= 1:
        return t-.5
    if t > .5:
        return t-.5+transition_integral(1-t)
    return .5*t*float(_WEIGHTS @ _step_array(.5*t*(_NODES+1)))


def areal_radius(ell: float, design: ConstantRadiusTrackDesign) -> float:
    """Constant track radius, a static convex end transition, then R' = 1 exactly."""
    excess = abs(ell)-design.track_half_length
    if excess <= 0:
        return design.track_radius
    return design.track_radius+design.transition_width*transition_integral(excess/design.transition_width)


def service_cutoff(ell: float, design: ConstantRadiusTrackDesign) -> float:
    span = design.track_half_length-design.service_inner
    return 1.-smooth_step((abs(ell)-design.service_inner)/span)


class _Primitives:
    def __init__(self, smooth: bool, abs_width: float, cap_width: float, join_fraction: float):
        self.smooth = smooth
        if smooth:
            self.step5 = lambda t: flattened_step(t, smoothstep_minjerk, join_fraction)
            self.step7 = lambda t: flattened_step(t, smoothstep7, join_fraction)
            self.absolute = lambda x: smooth_abs(x, abs_width)
            self.cap = lambda x: smooth_cap(x, cap_width)
        else:
            self.step5 = lambda t: float(smoothstep_minjerk(t))
            self.step7 = lambda t: float(smoothstep7(t))
            self.absolute = abs
            self.cap = lambda x: float(np.clip(x, 0., 1.))


def _check_supported(params: SourceParams) -> None:
    unsupported = {
        "catch_profile": params.catch_profile != "minjerk",
        "release mode": params.release_choreography_mode.strip().lower() in {"legacy", "off", "none"},
        "release profile": params.release_beta_profile not in {"minimum_jerk", "minjerk", "smoothstep5"},
        "split support width": params.w_th_inner is not None or params.w_th_outer is not None,
        "shell profiles": params.support_shell_overlay_enabled and (
            params.support_shell_radial_profile != "smooth_box" or params.support_shell_temporal_profile != "gaussian"),
        "receiver metric channels": any(getattr(params, key) != 0 for key in (
            "support_edge_receiver_lapse_log_gain", "support_edge_receiver_radial_log_gain",
            "support_edge_receiver_beta_relaxation_gain")),
        "coupled profile": params.standing_support_packet_coupled_profile_enabled,
        "causal guard": params.causal_margin_guard_enabled,
        "shell metric partners": params.support_shell_rail_stretch_log_gain != 0,
        "packet null cushion": params.standing_support_packet_null_cushion_log_gain != 0,
        "carve composition": params.standing_support_packet_smooth_split_composition != "additive",
        "current guard": params.standing_support_packet_smooth_split_current_guard_fraction != 0,
        "beta rematch shape": params.standing_support_packet_beta_rematch_shape != "trailing_edge"
        or params.standing_support_packet_beta_rematch_floor_mode != "blend",
        "annular shoulders": params.standing_support_packet_exclusion_shoulder_mode != "annular"
        or params.standing_support_packet_radial_shoulder_mode != "annular"
        or params.standing_support_packet_radial_skirt_mode != "annular",
    }
    names = [name for name, flag in unsupported.items() if flag]
    if names:
        raise ValueError("service reconstruction covers the beta075 configuration; unsupported: "+", ".join(names))


def service_fields(s: float, ell: float, params: SourceParams, *, smooth: bool = True,
                   abs_width: float = .02, cap_width: float = .25, join_fraction: float = .1,
                   reset_front: tuple[float, float, float, float, float] | None = None,
                   standing: bool = False) -> dict[str, float]:
    """Rebuild beta075's alpha, beta and gamma_ll with selectable primitives.

    Legacy primitives follow source_ledger.scalars operation by operation.
    Smooth primitives flatten the minimum-jerk and seventh-order polynomial
    joins within join_fraction of each end, replace |l| by smooth_abs and the
    shell Gaussian clip by smooth_cap. Annular differences and the additive carve are required to
    stay inside their unclipped ranges, so every remaining clip is inactive.
    A reset front (start, speed, origin, duration, ramp) replaces the uniform
    decompression: the support at ell begins to relax once a front leaving
    origin at time start with the given speed has passed it, with a C-infinity
    onset ramp, and completes over the given local duration.
    A standing support holds the spatial metric static: the decompression,
    the packet carve of the support weight and the packet windows on
    gamma_ll are removed, while the lapse windows and every shift window
    keep their schedules.
    """
    _check_supported(params)
    prim = _Primitives(smooth, abs_width, cap_width, join_fraction)
    s, ell = float(s), float(ell)
    live_end = live_packet_end(params)

    def rise(x, w, profile):
        if profile == "tanh":
            return float(1.0-falloff(s-x, w))
        return prim.step5((s-(x-2.0*w))/max(4.0*w, 1.0e-12))

    def fall(x, w, profile):
        if profile == "tanh":
            return float(falloff(s-x, w))
        return 1.0-prim.step5((s-(x-2.0*w))/max(4.0*w, 1.0e-12))

    def box(lo, hi, edge, profile):
        if profile == "tanh":
            return float(smooth_box(s, lo, hi, edge))
        return float(np.clip(rise(lo, edge, profile)*fall(hi, edge, profile), 0.0, 1.0))

    def schedule(name, multiplier, profile):
        width = max(float(params.w_beta)*float(multiplier), 1.0e-12)
        catch = max(params.w_catch_packet, params.w_catch_beta)*float(multiplier)
        if name == "live_only":
            value = fall(live_end, width, profile)
        elif name == "entry_catch_release":
            value = box(params.x_catch_packet-2.0*catch, live_end, max(width/2.0, 1.0e-12), profile)
        elif name == "catch_only":
            value = box(params.x_catch_packet-2.0*catch, params.x_catch_packet+2.0*catch,
                        max(width/2.0, 1.0e-12), profile)
        else:
            raise ValueError(f"unsupported packet schedule {name}")
        return float(np.clip(value, 0.0, 1.0))

    def packet_bump(radius, width, profile):
        x2 = (ell-s)**2+params.eps*params.eps
        if profile == "tanh":
            return float(bump_sq(x2, radius, width))
        z = (x2-radius*radius)/max(2.0*radius*width, 1.0e-12)
        if z <= -1.0:
            return 1.0
        if z >= 1.0:
            return 0.0
        return 1.0-prim.step7(0.5*(z+1.0))

    def window(radius_multiplier, width_multiplier, schedule_name, temporal_multiplier=1.0,
               temporal_profile="tanh", radial_profile="tanh"):
        radius = max(float(params.Rpass)*float(radius_multiplier), 1.0e-12)
        width = max(float(params.w_pass)*float(width_multiplier), 1.0e-12)
        value = packet_bump(radius, width, radial_profile)*schedule(schedule_name, temporal_multiplier, temporal_profile)
        return float(np.clip(value, 0.0, 1.0))

    def annulus(outer, inner):
        if outer-inner < -1e-15:
            raise ArithmeticError("annular window would activate its clip")
        return float(np.clip(outer-inner, 0.0, 1.0))

    start, end = release_beta_interval(params)
    c_beta = 1.0-prim.step5((s-(params.x_catch_beta-2.0*params.w_catch_beta))/max(4.0*params.w_catch_beta, 1.0e-12))
    c_packet = 1.0-prim.step5((s-(params.x_catch_packet-2.0*params.w_catch_packet))
                              / max(4.0*params.w_catch_packet, 1.0e-12))
    u_beta = params.v_exit+(params.V-params.v_exit)*c_beta
    u_packet = params.v_exit+(params.V-params.v_exit)*c_packet
    e_release = 1.0-prim.step5((s-start)/max(end-start, 1.0e-12))
    if standing:
        q = 1.0
    elif reset_front is None:
        q = 1.0-prim.step5((s-params.q_t0)/max(params.q_Tr, 1.0e-12))
    else:
        start, speed, origin, duration, ramp = reset_front
        onset = start+ramp*transition_integral((ell-origin)/ramp)/speed
        q = 1.0-prim.step5((s-onset)/duration)
    w_raw = float(bump_sq(ell*ell, params.Rth, params.w_th))
    s_packet = float(bump_sq((ell-s)**2+params.eps*params.eps, params.Rpass, params.w_pass))

    lag = float(params.release_carve_lag_widths)
    if lag or params.release_lapse_lag_widths:
        raise ValueError("release lag widths are outside the beta075 reconstruction")
    shoulder_strength = float(params.standing_support_packet_exclusion_shoulder)
    carve_shoulder = 0.0
    if shoulder_strength > 0.0:
        outer = window(params.standing_support_packet_exclusion_shoulder_radius_multiplier,
                       params.standing_support_packet_exclusion_shoulder_width_multiplier,
                       params.standing_support_packet_exclusion_shoulder_schedule,
                       temporal_profile=params.standing_support_packet_exclusion_shoulder_temporal_profile)
        inner = window(params.standing_support_packet_exclusion_radius_multiplier,
                       params.standing_support_packet_exclusion_width_multiplier,
                       params.standing_support_packet_exclusion_shoulder_schedule,
                       temporal_profile=params.standing_support_packet_exclusion_shoulder_temporal_profile)
        carve_shoulder = annulus(outer, inner)
    carve_main = 0.0
    if params.standing_support_packet_exclusion > 0.0:
        carve_main = window(params.standing_support_packet_exclusion_radius_multiplier,
                            params.standing_support_packet_exclusion_width_multiplier,
                            params.standing_support_packet_exclusion_schedule,
                            temporal_profile=params.standing_support_packet_exclusion_temporal_profile)
    carve_catch = 0.0
    if params.standing_support_packet_exclusion_catch > 0.0:
        carve_catch = window(params.standing_support_packet_exclusion_catch_radius_multiplier,
                             params.standing_support_packet_exclusion_catch_width_multiplier,
                             params.standing_support_packet_exclusion_catch_schedule,
                             temporal_profile=params.standing_support_packet_exclusion_catch_temporal_profile)
    legacy_carve = float(np.clip(
        float(params.standing_support_packet_exclusion)*carve_main
        + float(params.standing_support_packet_exclusion_catch)*carve_catch
        + shoulder_strength*carve_shoulder, 0.0, 1.0))

    split = params.standing_support_packet_smooth_split_enabled
    split_kwargs = dict(temporal_multiplier=params.standing_support_packet_smooth_split_temporal_width_multiplier,
                        temporal_profile=params.standing_support_packet_smooth_split_temporal_profile,
                        radial_profile=params.standing_support_packet_smooth_split_radial_profile)
    entry = catch = edge = 0.0
    if split:
        entry = window(params.standing_support_packet_smooth_split_entry_radius_multiplier,
                       params.standing_support_packet_smooth_split_entry_width_multiplier,
                       params.standing_support_packet_smooth_split_entry_schedule, **split_kwargs)
        catch = window(params.standing_support_packet_smooth_split_catch_radius_multiplier,
                       params.standing_support_packet_smooth_split_catch_width_multiplier,
                       params.standing_support_packet_smooth_split_catch_schedule, **split_kwargs)
        edge = annulus(
            window(params.standing_support_packet_smooth_split_edge_outer_radius_multiplier,
                   params.standing_support_packet_smooth_split_edge_width_multiplier,
                   params.standing_support_packet_smooth_split_edge_schedule, **split_kwargs),
            window(params.standing_support_packet_smooth_split_edge_inner_radius_multiplier,
                   params.standing_support_packet_smooth_split_edge_width_multiplier,
                   params.standing_support_packet_smooth_split_edge_schedule, **split_kwargs))
    split_sum = sum(float(v) for v in (float(params.standing_support_packet_smooth_split_entry_carve)*entry,
                                        float(params.standing_support_packet_smooth_split_catch_carve)*catch,
                                        float(params.standing_support_packet_smooth_split_edge_carve)*edge))
    if split_sum > 1.0:
        raise ArithmeticError("additive carve would activate its cap")
    split_containment = float(np.clip(split_sum, 0.0, 1.0))
    raw_carve = float(np.clip(sum(float(v) for v in (legacy_carve, 0.0, split_containment)), 0.0, 1.0))
    if raw_carve >= 1.0:
        raise ArithmeticError("total carve would activate its cap")
    carve_factor = 1.0 if standing else float(np.clip(1.0-raw_carve, 0.0, 1.0))
    w_support = w_raw*carve_factor

    a_spatial = float(np.exp(q*w_support*math.log(params.C0)))
    t_lapse = float(np.exp(q*w_support*math.log(params.lam*params.C0)))
    b_angular = 1.0+(params.B0-1.0)*w_support*q
    shoulder = float(np.exp(-((prim.absolute(ell)-1.05)/0.35)**2))
    n_cushion = float(np.exp(params.eta_N*0.18*q*shoulder))

    shell = 0.0
    if params.support_shell_overlay_enabled:
        inner = params.Rth*params.support_shell_inner_multiplier
        outer = params.Rth*params.support_shell_radial_multiplier
        default_width = max((outer-inner)/8.0, 1.0e-12)
        width = params.support_shell_radial_width if params.support_shell_radial_width is not None else default_width
        support = float(smooth_box(prim.absolute(ell), inner, outer, width))
        catch_width = max(params.w_catch_packet, params.w_catch_beta)
        lo, hi = params.x_catch_packet-2.0*catch_width, params.x_catch_packet+2.0*catch_width
        edge_width = (params.support_shell_catch_edge_width if params.support_shell_catch_edge_width is not None
                      else catch_width/4.0)
        catch_box = float(smooth_box(s, lo, hi, edge_width))
        anchor = params.x_catch_packet if params.support_shell_time_anchor is None else params.support_shell_time_anchor
        center = float(anchor)-params.support_shell_catch_lead
        scale = max(float(params.support_shell_temporal_width), 1.0e-12)
        closest = min(max(center, lo), hi)
        temporal = float(np.exp(-0.5*((s-center)/scale)**2))
        norm = math.exp(-0.5*((closest-center)/scale)**2)
        temporal = prim.cap(temporal/max(norm, 1.0e-12))
        packet = float(bump_sq((ell-s)**2+params.eps*params.eps, params.Rpass, params.w_pass))
        live = float(falloff(s-live_end, params.w_beta))
        exclusion = float(np.clip(1.0-params.support_shell_packet_exclusion*packet*live, 0.0, 1.0))
        shell = support*catch_box*temporal*exclusion
        for _ in range(max(0, int(params.support_shell_smoothness_order))):
            shell = float(smoothstep_minjerk(shell))
        shell = float(np.clip(shell, 0.0, 1.0))

    beta_base = -u_beta*e_release*(w_support**params.p_beta)*s_packet/b_angular
    delta_shell = float(params.support_shell_amplitude)*shell if params.support_shell_overlay_enabled else 0.0
    beta_pre = beta_base+delta_shell
    alpha_base = n_cushion*t_lapse
    lapse_window = 0.0
    if params.standing_support_packet_lapse_log_gain != 0.0:
        lapse_window = window(params.standing_support_packet_lapse_radius_multiplier,
                              params.standing_support_packet_lapse_width_multiplier,
                              params.standing_support_packet_lapse_schedule,
                              temporal_profile=params.standing_support_packet_lapse_temporal_profile)
    packet_lapse = float(math.exp(float(params.standing_support_packet_lapse_log_gain)*float(lapse_window)))
    cushion_window = edge if params.standing_support_packet_smooth_split_null_cushion_log_gain != 0.0 else 0.0
    split_cushion = float(math.exp(float(params.standing_support_packet_smooth_split_null_cushion_log_gain)
                                   * float(cushion_window)))
    clock = float(math.exp(float(params.support_shell_clock_lapse_log_gain)*float(shell)))
    alpha = alpha_base*packet_lapse*split_cushion*clock

    radial_window = shoulder_window = skirt_window = 0.0
    if params.standing_support_packet_radial_log_gain != 0.0:
        radial_window = window(params.standing_support_packet_radial_radius_multiplier,
                               params.standing_support_packet_radial_width_multiplier,
                               params.standing_support_packet_radial_schedule,
                               temporal_profile=params.standing_support_packet_radial_temporal_profile)
    if params.standing_support_packet_radial_shoulder_log_gain != 0.0:
        shoulder_window = annulus(
            window(params.standing_support_packet_radial_shoulder_radius_multiplier,
                   params.standing_support_packet_radial_shoulder_width_multiplier,
                   params.standing_support_packet_radial_shoulder_schedule,
                   temporal_profile=params.standing_support_packet_radial_shoulder_temporal_profile),
            window(params.standing_support_packet_radial_radius_multiplier,
                   params.standing_support_packet_radial_width_multiplier,
                   params.standing_support_packet_radial_shoulder_schedule,
                   temporal_profile=params.standing_support_packet_radial_shoulder_temporal_profile))
    if params.standing_support_packet_radial_skirt_log_gain != 0.0:
        skirt_window = annulus(
            window(params.standing_support_packet_radial_skirt_radius_multiplier,
                   params.standing_support_packet_radial_skirt_width_multiplier,
                   params.standing_support_packet_radial_skirt_schedule,
                   temporal_profile=params.standing_support_packet_radial_skirt_temporal_profile),
            window(params.standing_support_packet_radial_skirt_inner_radius_multiplier,
                   params.standing_support_packet_radial_skirt_width_multiplier,
                   params.standing_support_packet_radial_skirt_schedule,
                   temporal_profile=params.standing_support_packet_radial_skirt_temporal_profile))
    sqrt_radial = b_angular*a_spatial
    radial = sqrt_radial*sqrt_radial
    if not standing:
        radial *= math.exp(float(params.standing_support_packet_radial_log_gain)*radial_window
                           + float(params.standing_support_packet_radial_shoulder_log_gain)*shoulder_window
                           + float(params.standing_support_packet_radial_skirt_log_gain)*skirt_window)

    vcoord = u_packet/b_angular
    rematch = 0.0
    if params.standing_support_packet_beta_rematch_gain != 0.0:
        multiplier = params.standing_support_packet_beta_rematch_temporal_width_multiplier
        edge_width = (params.standing_support_packet_beta_rematch_width_multiplier
                      * params.standing_support_packet_beta_rematch_edge_softness)
        schedule_name = params.standing_support_packet_beta_rematch_schedule
        profile = params.standing_support_packet_beta_rematch_temporal_profile
        floor = float(params.standing_support_packet_beta_rematch_center_floor)*window(
            params.standing_support_packet_beta_rematch_radius_multiplier,
            params.standing_support_packet_beta_rematch_width_multiplier, schedule_name, multiplier, profile)
        ring = annulus(
            window(params.standing_support_packet_beta_rematch_outer_radius_multiplier, edge_width,
                   schedule_name, multiplier, profile),
            window(params.standing_support_packet_beta_rematch_inner_radius_multiplier, edge_width,
                   schedule_name, multiplier, profile))
        trailing = float(falloff(ell-s, max(float(params.w_pass)*float(edge_width), 1.0e-12)))
        value = ring*trailing
        rematch = float(np.clip(value+floor*(1.0-value), 0.0, 1.0))
    beta = beta_pre+(-float(params.standing_support_packet_beta_rematch_gain)*rematch*(vcoord+beta_pre))
    return {"alpha": alpha, "beta": beta, "gamma_ll": radial, "vcoord": vcoord, "q": q, "W": w_support,
            "U_beta": u_beta, "U_packet": u_packet, "B": b_angular, "E": e_release}


@lru_cache(maxsize=16384)
def track_scalars(s: float, ell: float, params: SourceParams, design: ConstantRadiusTrackDesign) -> dict[str, float]:
    """Metric fields of the candidate: service metric on the track, static transitions and flat space beyond."""
    cutoff = service_cutoff(ell, design)
    if cutoff > 0.:
        if design.smooth_service:
            service = service_fields(s, ell, params, smooth=True, abs_width=design.abs_width,
                                     cap_width=design.cap_width, join_fraction=design.join_fraction,
                                     reset_front=design.reset_front, standing=design.standing_support)
        else:
            service = regularized_scalars(s, ell, params)
        alpha = 1.+cutoff*(service["alpha"]-1.)
        beta = cutoff*service["beta"]
        radial = 1.+cutoff*(service["gamma_ll"]-1.)
    else:
        alpha, beta, radial = 1., 0., 1.
    radius = areal_radius(ell, design)
    return {"alpha": alpha, "beta": beta, "gamma_ll": radial, "gamma_omega": radius*radius,
            "service_cutoff": cutoff, "areal_radius": radius}
