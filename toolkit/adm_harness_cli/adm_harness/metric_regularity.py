"""C2 origin/window repairs and a uniform-rate diagnostic for frozen beta075."""
from __future__ import annotations

from functools import lru_cache
import math

import numpy as np

from .receiver_regularity import c2_clipped_power, repaired_receiver_scalars
from .source_ledger import (
    SourceParams, bump_sq, falloff, live_packet_end, minjerk_down, smooth_box,
    smoothstep_minjerk, support_shell_radial_window, support_shell_temporal_window,
)


def c2_radius(ell: float, width: float = .1) -> float:
    """Even polynomial at the origin, matching |ell| and two derivatives at width."""
    if not math.isfinite(ell) or not math.isfinite(width) or width <= 0:
        raise ValueError("finite ell and a positive finite origin width are required")
    radius = abs(ell)
    if radius >= width:
        return radius
    t = radius/width
    return width*t*t*(15/8+t*t*(-5/4+3*t*t/8))


def c2_upper_cap(value: float, width: float = .25) -> float:
    """Preserve a positive input below 1-width and join smoothly to a cap at one."""
    if not math.isfinite(value) or value < 0 or not 0 < width < .5:
        raise ValueError("cap requires a finite nonnegative input and width in (0, .5)")
    if value <= 1-width:
        return value
    return c2_clipped_power(value, 1., width)


def regularized_shell_window(s, ell, params, original, origin_width=.1, cap_width=.25):
    if not params.support_shell_overlay_enabled:
        return 0.
    if params.support_shell_radial_profile != "smooth_box" or params.support_shell_temporal_profile != "gaussian":
        raise ValueError("candidate shell reconstruction requires the frozen smooth-box/Gaussian profiles")
    catch_width = max(params.w_catch_packet, params.w_catch_beta)
    lo, hi = params.x_catch_packet-2*catch_width, params.x_catch_packet+2*catch_width
    anchor = params.x_catch_packet if params.support_shell_time_anchor is None else params.support_shell_time_anchor
    center = anchor-params.support_shell_catch_lead
    scale = params.support_shell_temporal_width
    if scale <= 0:
        raise ValueError("positive Gaussian width required")
    closest = min(max(center, lo), hi)
    log_ratio = .5*((closest-center)**2-(s-center)**2)/scale**2
    cap_changes = math.log1p(-cap_width) < log_ratio < 0
    if abs(ell) >= origin_width and not cap_changes:
        return original
    inner = params.Rth*params.support_shell_inner_multiplier
    outer = params.Rth*params.support_shell_radial_multiplier
    width = (outer-inner)/8 if params.support_shell_radial_width is None else params.support_shell_radial_width
    support = support_shell_radial_window(c2_radius(ell, origin_width), inner, outer, width, "smooth_box")
    edge = catch_width/4 if params.support_shell_catch_edge_width is None else params.support_shell_catch_edge_width
    catch = smooth_box(s, lo, hi, edge)
    temporal = (c2_upper_cap(math.exp(log_ratio), cap_width) if cap_changes else
                support_shell_temporal_window(s, center, scale, lo, hi, "gaussian", params.support_shell_temporal_shoulder))
    packet = bump_sq((ell-s)**2+params.eps**2, params.Rpass, params.w_pass)
    exclusion = np.clip(1-params.support_shell_packet_exclusion*packet*falloff(s-live_packet_end(params), params.w_beta), 0, 1)
    window = support*catch*temporal*exclusion
    for _ in range(max(0, int(params.support_shell_smoothness_order))):
        window = smoothstep_minjerk(window)
    return float(np.clip(window, 0, 1))


@lru_cache(maxsize=4096)
def regularized_scalars(s: float, ell: float, params: SourceParams, *, origin_width=.1, cap_width=.25):
    """Compose receiver repair, even origin profiles, and the shell's smooth time cap.

    All shell metric channels and the downstream beta rematch are reconstructed
    from the changed shell window. No Einstein-tensor channels are prescribed.
    """
    if not math.isfinite(origin_width) or origin_width <= 0 or not 0 < cap_width < .5:
        raise ValueError("positive origin width and cap width in (0, .5) required")
    base = repaired_receiver_scalars(s, ell, params)
    old_shell = base["support_shell_window"]
    shell = regularized_shell_window(s, ell, params, old_shell, origin_width, cap_width)
    delta_shell = shell-old_shell
    delta_shoulder = 0.
    if abs(ell) < origin_width:
        radius = c2_radius(ell, origin_width)
        old = float(np.exp(-((abs(ell)-1.05)/.35)**2))
        new = float(np.exp(-((radius-1.05)/.35)**2))
        delta_shoulder = new-old
    if delta_shell == 0 and delta_shoulder == 0:
        return base
    lapse_change = params.eta_N*.18*float(minjerk_down(s, params.q_t0, params.q_Tr))*delta_shoulder
    lapse_change += params.support_shell_clock_lapse_log_gain*delta_shell
    delta_beta = params.support_shell_amplitude*delta_shell if params.support_shell_overlay_enabled else 0.
    delta_beta *= 1-params.standing_support_packet_beta_rematch_gain*base["standing_support_packet_beta_rematch_window"]
    return base | {
        "alpha": base["alpha"]*math.exp(lapse_change),
        "beta": base["beta"]+delta_beta,
        "gamma_ll": base["gamma_ll"]*math.exp(params.support_shell_rail_stretch_log_gain*delta_shell),
        "gamma_omega": base["gamma_omega"]*math.exp(params.support_shell_throat_capacity_log_gain*delta_shell),
        "support_shell_window": shell,
    }


def rate_scaled_scalars(time, ell, params, *, rate=1.):
    """Slow the protocol phase and shift together while keeping lapse unchanged.

    phase=rate*time. At a matched phase the spatial geometry and lapse are
    identical. This changes physical evolution speed; a coordinate rescaling
    would also rescale lapse. Rates below one are diagnostic service changes.
    """
    if not math.isfinite(rate) or rate <= 0:
        raise ValueError("rate must be positive and finite; use holding for the zero-rate limit")
    fields = regularized_scalars(rate*time, ell, params)
    return fields | {"beta": rate*fields["beta"]}
