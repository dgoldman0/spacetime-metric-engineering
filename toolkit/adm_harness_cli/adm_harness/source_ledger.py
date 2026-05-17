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
    V: float = 5.0
    v_exit: float = 0.5
    p_beta: float = 4.0
    Rpass: float = 0.35

    x_catch_beta: float = -0.05
    w_catch_beta: float = 0.32
    x_catch_packet: float = 0.00
    w_catch_packet: float = 0.32
    catch_profile: str = "minjerk"

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

    x_beta: float = 0.70
    w_beta: float = 0.18
    q_t0: float = -0.40
    q_Tr: float = 3.00

    aOmega: float = 0.20
    ROmega: float = 1.75
    wOmega: float = 1.40
    xOmega: float = 2.00
    wtOmega: float = 0.60

    live_packet_end_margin_widths: float = 2.0

    # Frozen support-shell carrying-flow overlay. Disabled by default so the
    # regenerated reference ledgers still reproduce the historical bundles.
    support_shell_overlay_enabled: bool = False
    support_shell_amplitude: float = 1.0e-7
    support_shell_catch_lead: float = 1.0
    support_shell_temporal_width: float = 0.35
    support_shell_smoothness_order: int = 1
    support_shell_inner_multiplier: float = 0.65
    support_shell_radial_multiplier: float = 1.20
    support_shell_radial_width: float | None = None
    support_shell_packet_exclusion: float = 1.0
    support_shell_time_anchor: float | None = None
    support_shell_catch_edge_width: float | None = None


@dataclass(frozen=True)
class SourceCase:
    name: str
    params: SourceParams
    note: str


def smoothstep_minjerk(t: np.ndarray | float) -> np.ndarray:
    x = np.clip(np.asarray(t, dtype=float), 0.0, 1.0)
    return 10.0 * x**3 - 15.0 * x**4 + 6.0 * x**5


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


def bump_sq(x2: np.ndarray | float, radius: float, width: float) -> np.ndarray:
    z = (np.asarray(x2, dtype=float) - radius * radius) / max(2.0 * radius * width, 1.0e-12)
    return 0.5 * (1.0 - np.tanh(z))


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
    support = smooth_box(np.abs(l_arr), support_inner, support_outer, support_width)

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
    temporal = np.exp(-0.5 * ((s_arr - center) / temporal_width) ** 2)
    closest_in_catch = min(max(center, lo), hi)
    temporal_norm = math.exp(-0.5 * ((closest_in_catch - center) / temporal_width) ** 2)
    temporal = np.clip(temporal / max(temporal_norm, 1.0e-12), 0.0, 1.0)

    packet = bump_sq((l_arr - s_arr) ** 2 + params.eps * params.eps, params.Rpass, params.w_pass)
    live_end = params.x_beta + params.live_packet_end_margin_widths * params.w_beta
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


def scalars(s: float, l: float, params: SourceParams) -> dict[str, float]:
    s_arr = np.asarray(s, dtype=float)
    l_arr = np.asarray(l, dtype=float)

    c_beta = catch_factor(s_arr, params.x_catch_beta, params.w_catch_beta, params.catch_profile)
    c_packet = catch_factor(s_arr, params.x_catch_packet, params.w_catch_packet, params.catch_profile)
    u_beta = params.v_exit + (params.V - params.v_exit) * c_beta
    u_packet = params.v_exit + (params.V - params.v_exit) * c_packet

    e_release = falloff(s_arr - params.x_beta, params.w_beta)
    q = minjerk_down(s_arr, params.q_t0, params.q_Tr)
    w_support = support_bump(l_arr, params)
    s_packet = bump_sq((l_arr - s_arr) ** 2 + params.eps * params.eps, params.Rpass, params.w_pass)

    a_spatial = np.exp(q * w_support * math.log(params.C0))
    t_lapse = np.exp(q * w_support * math.log(params.lam * params.C0))
    b_angular = 1.0 + (params.B0 - 1.0) * w_support * q
    shoulder = np.exp(-((np.abs(l_arr) - 1.05) / 0.35) ** 2)
    n_cushion = np.exp(params.eta_N * 0.18 * q * shoulder)

    beta_base = -u_beta * e_release * (w_support ** params.p_beta) * s_packet / b_angular
    delta_beta_shell = support_shell_delta_beta(float(s), float(l), params)
    beta = beta_base + delta_beta_shell
    alpha = n_cushion * t_lapse
    sqrt_gamma_ll = b_angular * a_spatial
    gamma_ll = sqrt_gamma_ll * sqrt_gamma_ll
    vcoord = u_packet / b_angular
    gtt = -alpha * alpha + gamma_ll * beta * beta
    packet_norm = -alpha * alpha + gamma_ll * (vcoord + beta) ** 2

    w_omega = bump_sq(l_arr * l_arr, params.ROmega, params.wOmega)
    q_omega = falloff(s_arr - params.xOmega, params.wtOmega)
    c_omega = np.exp(params.aOmega * q_omega * w_omega)
    gamma_omega = (l_arr * l_arr + params.Rth * params.Rth) * c_omega * c_omega

    return {
        "U_beta": float(u_beta),
        "U_packet": float(u_packet),
        "E": float(e_release),
        "q": float(q),
        "W": float(w_support),
        "S": float(s_packet),
        "A": float(a_spatial),
        "T": float(t_lapse),
        "B": float(b_angular),
        "N": float(n_cushion),
        "beta": float(beta),
        "alpha": float(alpha),
        "beta_base": float(beta_base),
        "support_shell_window": support_shell_overlay_window(float(s), float(l), params),
        "support_shell_delta_beta": float(delta_beta_shell),
        "sqrt_gamma_ll": float(sqrt_gamma_ll),
        "gamma_ll": float(gamma_ll),
        "vcoord": float(vcoord),
        "gtt": float(gtt),
        "packet_norm": float(packet_norm),
        "WOmega": float(w_omega),
        "QOmega": float(q_omega),
        "COmega": float(c_omega),
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
            "support_shell_window",
            "support_shell_delta_beta",
            "gamma_ll",
            "gamma_omega",
            "COmega",
        ]},
    }


def stage_name(s: float, params: SourceParams) -> str:
    width = max(params.w_catch_packet, params.w_catch_beta)
    center = params.x_catch_packet
    if s < center - 2.0 * width:
        return "entry_precatch"
    if abs(s - center) <= 2.0 * width:
        return "catch_rematch"
    if center + 2.0 * width < s < params.x_beta - 2.0 * params.w_beta:
        return "held_carry"
    if abs(s - params.x_beta) <= 2.0 * params.w_beta:
        return "release_shift_fade"
    if params.x_beta + 2.0 * params.w_beta < s < params.x_beta + 4.0 * params.w_beta:
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
    live_end = params.x_beta + params.live_packet_end_margin_widths * params.w_beta
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
    if params.support_shell_overlay_enabled:
        case_name = (
            f"{case_name}_shell_a{_token(params.support_shell_amplitude)}"
            f"_lead{_token(params.support_shell_catch_lead)}"
            f"_tw{_token(params.support_shell_temporal_width)}"
        )
        note = f"{note}; continuous frozen support-shell carrying-flow overlay"
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
