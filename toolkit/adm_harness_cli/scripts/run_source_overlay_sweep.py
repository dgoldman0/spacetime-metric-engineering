from __future__ import annotations

import argparse
import hashlib
import json
import math
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
import sys

if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.source_ledger import (  # noqa: E402
    CHANNELS,
    branch_case,
    compute_case,
    summarize,
    summarize_safety,
    support_shell_overlay_window,
    write_manifest,
)


DEFAULT_S_MIN = -0.35
DEFAULT_S_MAX = 1.65
DEFAULT_S_STEP = 0.05
HARD_EXPOSURE_CHANNELS = ["neg_Tkk_radial", "abs_p_l", "neg_rho_euler", "neg_rho_packet"]


def _token(value: float) -> str:
    text = f"{float(value):.10g}"
    return text.replace("-", "m").replace("+", "").replace(".", "p").replace("e", "e")


def _case_slug(spec: dict[str, Any]) -> str:
    temporal_shoulder = spec.get("temporal_shoulder")
    radial_width = spec.get("support_shell_radial_width")
    parts = [
        f"a{_token(spec['abs_amplitude'])}",
        str(spec["sign"]),
        f"lead{_token(spec['catch_lead'])}",
        f"tw{_token(spec['temporal_width'])}",
        f"tp{spec['temporal_profile']}",
        f"ts{_token(temporal_shoulder) if temporal_shoulder is not None else 'none'}",
        f"rp{spec['radial_profile']}",
        f"rw{_token(radial_width) if radial_width is not None else 'default'}",
        f"cl{_token(spec['clock_lapse_ratio'])}",
        f"rs{_token(spec['rail_stretch_ratio'])}",
        f"tc{_token(spec['throat_capacity_ratio'])}",
        f"wc{_token(spec['standing_support_packet_exclusion'])}",
        f"wcr{_token(spec['standing_support_packet_exclusion_radius_multiplier'])}",
        f"wcw{_token(spec['standing_support_packet_exclusion_width_multiplier'])}",
        f"wcs{spec['standing_support_packet_exclusion_schedule']}",
        f"wsh{_token(spec['standing_support_packet_exclusion_shoulder'])}",
        f"wshm{spec['standing_support_packet_exclusion_shoulder_mode']}",
        f"wshr{_token(spec['standing_support_packet_exclusion_shoulder_radius_multiplier'])}",
        f"wshw{_token(spec['standing_support_packet_exclusion_shoulder_width_multiplier'])}",
        f"wshs{spec['standing_support_packet_exclusion_shoulder_schedule']}",
        f"wlap{_token(spec['standing_support_packet_lapse_log_gain'])}",
        f"wlr{_token(spec['standing_support_packet_lapse_radius_multiplier'])}",
        f"wlw{_token(spec['standing_support_packet_lapse_width_multiplier'])}",
        f"wls{spec['standing_support_packet_lapse_schedule']}",
        f"wb{_token(spec['standing_support_packet_beta_rematch_gain'])}",
        f"wbsh{spec['standing_support_packet_beta_rematch_shape']}",
        f"wbr{_token(spec['standing_support_packet_beta_rematch_radius_multiplier'])}",
        f"wbw{_token(spec['standing_support_packet_beta_rematch_width_multiplier'])}",
        f"wbi{_token(spec['standing_support_packet_beta_rematch_inner_radius_multiplier'])}",
        f"wbo{_token(spec['standing_support_packet_beta_rematch_outer_radius_multiplier'])}",
        f"wbe{_token(spec['standing_support_packet_beta_rematch_edge_softness'])}",
        f"wbt{_token(spec['standing_support_packet_beta_rematch_temporal_width_multiplier'])}",
        f"wbf{_token(spec['standing_support_packet_beta_rematch_center_floor'])}",
        f"wbs{spec['standing_support_packet_beta_rematch_schedule']}",
    ]
    if spec.get("target_delta_beta_abs_max") is not None:
        parts.append(f"tdb{_token(spec['target_delta_beta_abs_max'])}")
    slug = "_".join(parts)
    if len(slug) > 180:
        digest = hashlib.sha1(slug.encode("utf-8")).hexdigest()[:12]
        suffix_parts = []
        if spec.get("target_delta_beta_abs_max") is not None:
            suffix_parts.append(f"tdb{_token(spec['target_delta_beta_abs_max'])}")
        suffix = "_".join([*suffix_parts, f"h{digest}"])
        slug = f"{slug[: 179 - len(suffix)]}_{suffix}"
    return slug


def _sort_cols() -> list[str]:
    return [
        "nominal_abs_amplitude",
        "abs_amplitude",
        "sign",
        "catch_lead",
        "temporal_width",
        "temporal_profile",
        "temporal_shoulder",
        "radial_profile",
        "support_shell_radial_width",
        "clock_lapse_ratio",
        "rail_stretch_ratio",
        "throat_capacity_ratio",
        "standing_support_packet_exclusion",
        "standing_support_packet_exclusion_radius_multiplier",
        "standing_support_packet_exclusion_width_multiplier",
        "standing_support_packet_exclusion_schedule",
        "standing_support_packet_exclusion_shoulder",
        "standing_support_packet_exclusion_shoulder_mode",
        "standing_support_packet_exclusion_shoulder_radius_multiplier",
        "standing_support_packet_exclusion_shoulder_width_multiplier",
        "standing_support_packet_exclusion_shoulder_schedule",
        "standing_support_packet_lapse_log_gain",
        "standing_support_packet_lapse_radius_multiplier",
        "standing_support_packet_lapse_width_multiplier",
        "standing_support_packet_lapse_schedule",
        "standing_support_packet_beta_rematch_gain",
        "standing_support_packet_beta_rematch_shape",
        "standing_support_packet_beta_rematch_radius_multiplier",
        "standing_support_packet_beta_rematch_width_multiplier",
        "standing_support_packet_beta_rematch_inner_radius_multiplier",
        "standing_support_packet_beta_rematch_outer_radius_multiplier",
        "standing_support_packet_beta_rematch_edge_softness",
        "standing_support_packet_beta_rematch_temporal_width_multiplier",
        "standing_support_packet_beta_rematch_center_floor",
        "standing_support_packet_beta_rematch_schedule",
    ]


def _resolve_grid(args: argparse.Namespace, overlay_case) -> dict[str, Any]:
    params = overlay_case.params
    s_max = float(args.s_max)
    s_min = DEFAULT_S_MIN if args.s_min is None else float(args.s_min)
    if args.s_min is None:
        catch_width = max(params.w_catch_packet, params.w_catch_beta)
        edge_width = params.support_shell_catch_edge_width if params.support_shell_catch_edge_width is not None else catch_width / 4.0
        s_min = min(s_min, params.x_catch_packet - 2.0 * catch_width - 4.0 * edge_width)
    ns = int(args.ns) if args.ns is not None else int(round((s_max - s_min) / DEFAULT_S_STEP)) + 1
    return {
        "ns": ns,
        "nl": int(args.nl),
        "s_min": s_min,
        "s_max": s_max,
        "l_min": float(args.l_min),
        "l_max": float(args.l_max),
        "h_s": float(args.h_s),
        "h_l": float(args.h_l),
    }


def _compact_by_channel(points: pd.DataFrame) -> pd.DataFrame:
    _, compact, _, _, _ = summarize(points)
    return compact.set_index("channel")


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def _ratio_excess(summary: dict[str, Any], key: str) -> float:
    value = _finite(summary.get(key), 1.0)
    return max(value - 1.0, 0.0)


def _positive_fraction(summary: dict[str, Any], key: str) -> float:
    value = _finite(summary.get(key), 0.0)
    return max(value, 0.0)


def _add_source_objective(summary: dict[str, Any]) -> None:
    aggregate = _ratio_excess(summary, "max_total_burden_ratio")
    radial_null = _ratio_excess(summary, "neg_Tkk_radial_total_ratio")
    radial_current = _ratio_excess(summary, "abs_j_l_total_ratio")
    angular_pressure = _ratio_excess(summary, "abs_pOmega_total_ratio")
    packet_drift = _finite(summary.get("packet_norm_live_delta_max_abs"))
    packet_unsafe = 10.0 if int(summary.get("positive_packet_norm_live", 0)) > 0 else 0.0
    packet_density = _ratio_excess(summary, "neg_rho_packet_total_ratio")
    point_peak = _ratio_excess(summary, "max_point_peak_ratio")
    shell_null = _ratio_excess(summary, "neg_Tkk_radial_shell_throat_weighted_ratio")
    shell_current_fraction = _positive_fraction(summary, "abs_j_l_shell_throat_delta_fraction")
    shell_angular_fraction = _positive_fraction(summary, "abs_pOmega_shell_throat_delta_fraction")

    packet_safety_score = packet_unsafe + 0.25 * packet_drift + packet_density
    shell_throat_score = 0.25 * shell_null + 0.25 * shell_current_fraction + 0.25 * shell_angular_fraction
    radial_transport_score = radial_null + radial_current
    angular_support_score = angular_pressure
    aggregate_source_score = aggregate
    point_peak_score = point_peak

    summary.update({
        "aggregate_source_score": aggregate_source_score,
        "packet_safety_score": packet_safety_score,
        "point_peak_score": point_peak_score,
        "shell_throat_score": shell_throat_score,
        "radial_transport_score": radial_transport_score,
        "angular_support_score": angular_support_score,
        "source_objective_score": (
            4.0 * aggregate_source_score
            + 2.0 * radial_null
            + 1.5 * radial_current
            + 1.5 * angular_pressure
            + packet_safety_score
            + 0.5 * point_peak_score
            + shell_throat_score
        ),
    })


def _add_worldtube_exposure_summary(summary: dict[str, Any], points: pd.DataFrame) -> None:
    live = points["inside_packet_live"].astype(bool)
    geom = points["inside_packet_geom"].astype(bool)
    packet_in_support = points["region"].astype(str).eq("packet_in_support")
    active_shell = points["support_shell_window"].astype(float).abs() > 1.0e-3

    max_live_fraction = 0.0
    max_geom_fraction = 0.0
    top_hard_live = 0
    top_hard_geom = 0
    hard_top_regions: list[str] = []
    hard_top_stages: list[str] = []
    for channel in CHANNELS:
        burden_col = f"volume_burden_{channel}"
        total = float(np.nansum(points[burden_col].astype(float).to_numpy()))
        live_burden = float(np.nansum(points.loc[live, burden_col].astype(float).to_numpy()))
        geom_burden = float(np.nansum(points.loc[geom, burden_col].astype(float).to_numpy()))
        packet_support_burden = float(np.nansum(points.loc[packet_in_support, burden_col].astype(float).to_numpy()))
        live_fraction = live_burden / total if total > 0.0 else math.nan
        geom_fraction = geom_burden / total if total > 0.0 else math.nan
        summary[f"{channel}_live_packet_fraction_absolute"] = live_fraction
        summary[f"{channel}_geometric_packet_fraction_absolute"] = geom_fraction
        summary[f"{channel}_packet_in_support_burden"] = packet_support_burden
        summary[f"{channel}_packet_in_support_fraction"] = packet_support_burden / total if total > 0.0 else math.nan
        if math.isfinite(live_fraction):
            max_live_fraction = max(max_live_fraction, live_fraction)
        if math.isfinite(geom_fraction):
            max_geom_fraction = max(max_geom_fraction, geom_fraction)

        if channel in HARD_EXPOSURE_CHANNELS and len(points):
            top = points.sort_values(burden_col, ascending=False).iloc[0]
            if bool(top["inside_packet_live"]):
                top_hard_live += 1
            if bool(top["inside_packet_geom"]):
                top_hard_geom += 1
            hard_top_regions.append(str(top["region"]))
            hard_top_stages.append(str(top["stage"]))

    summary["max_live_packet_fraction_any_channel_absolute"] = max_live_fraction
    summary["max_geometric_packet_fraction_any_channel_absolute"] = max_geom_fraction
    summary["top_hard_channels_in_live_packet"] = top_hard_live
    summary["top_hard_channels_in_geometric_packet"] = top_hard_geom
    summary["live_packet_active_shell_points"] = int((live & active_shell).sum())
    summary["geometric_packet_active_shell_points"] = int((geom & active_shell).sum())
    summary["hard_top_point_regions"] = ";".join(hard_top_regions)
    summary["hard_top_point_stages"] = ";".join(hard_top_stages)

    positive_packet_norm = int(summary.get("positive_packet_norm_live", 0))
    packet_unsafe = 10.0 + 0.05 * positive_packet_norm if positive_packet_norm > 0 else 0.0
    packet_margin = max(_finite(summary.get("max_packet_norm_live")) + 1.0, 0.0)
    point_peak = _ratio_excess(summary, "max_point_peak_ratio")
    live_tkk = _finite(summary.get("neg_Tkk_radial_live_packet_fraction_absolute"))
    live_pl = _finite(summary.get("abs_p_l_live_packet_fraction_absolute"))
    live_density = _finite(summary.get("neg_rho_packet_live_packet_fraction_absolute"))
    active_shell_penalty = 1.0 if int(summary["live_packet_active_shell_points"]) > 0 else 0.0
    top_hard_penalty = float(top_hard_live)
    summary["worldtube_exposure_score"] = (
        packet_unsafe
        + packet_margin
        + 4.0 * live_tkk
        + 4.0 * live_pl
        + 2.0 * live_density
        + top_hard_penalty
        + active_shell_penalty
        + 0.2 * point_peak
    )


def _compare_channels(base_compact: pd.DataFrame, overlay_compact: pd.DataFrame, spec: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for channel in CHANNELS:
        base = base_compact.loc[channel]
        overlay = overlay_compact.loc[channel]
        row = {**spec, "channel": channel}
        for key in ["total_burden", "live_packet_burden", "live_packet_fraction", "point_peak", "live_packet_point_peak"]:
            base_value = float(base[key])
            overlay_value = float(overlay[key])
            row[f"{key}_base"] = base_value
            row[f"{key}_overlay"] = overlay_value
            row[f"{key}_delta"] = overlay_value - base_value
            row[f"{key}_ratio"] = overlay_value / base_value if base_value else math.nan
        rows.append(row)
    return rows


def _gradient_by_s(points: pd.DataFrame, value_col: str) -> pd.Series:
    gradients = pd.Series(np.nan, index=points.index, dtype=float)
    for _, group in points.sort_values(["s", "l"]).groupby("s", sort=False):
        values = group[value_col].astype(float).to_numpy()
        coords = group["l"].astype(float).to_numpy()
        if len(group) < 2:
            continue
        edge_order = 2 if len(group) > 2 else 1
        gradients.loc[group.index] = np.gradient(values, coords, edge_order=edge_order)
    return gradients


def _with_shell_throat_diagnostics(points: pd.DataFrame) -> pd.DataFrame:
    diag = points.copy()
    for col in ["alpha", "beta", "gamma_ll", "gamma_omega", "support_shell_window"]:
        diag[f"d_{col}_dl"] = _gradient_by_s(diag, col)
    eps = 1.0e-12
    diag["shell_throat_gradient"] = (
        diag["d_gamma_ll_dl"].abs() / np.maximum(diag["gamma_ll"].abs(), eps)
        + diag["d_gamma_omega_dl"].abs() / np.maximum(diag["gamma_omega"].abs(), eps)
    )
    active = diag["support_shell_window"].astype(float).abs() > 1.0e-3
    support = diag["region"].astype(str).isin(["support_edge", "core_throat"])
    active_gradient = diag.loc[active & support, "shell_throat_gradient"].replace([np.inf, -np.inf], np.nan).dropna()
    threshold = float(active_gradient.quantile(0.50)) if len(active_gradient) else math.inf
    diag["shell_throat_overlap"] = active & support & (diag["shell_throat_gradient"] >= threshold)
    scale = max(threshold, 1.0e-12) if math.isfinite(threshold) else 1.0
    diag["shell_throat_weight"] = np.where(
        diag["shell_throat_overlap"],
        diag["support_shell_window"].astype(float).abs() * diag["shell_throat_gradient"].astype(float) / scale,
        0.0,
    )
    return diag


def _compare_shell_throat_overlap(
    base_points: pd.DataFrame,
    overlay_points: pd.DataFrame,
    spec: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    overlay_diag = _with_shell_throat_diagnostics(overlay_points)
    base_diag = _with_shell_throat_diagnostics(base_points)
    merged = overlay_diag.merge(base_diag, on=["s", "l"], suffixes=("_overlay", "_base"))
    overlap = merged["shell_throat_overlap_overlay"].astype(bool)
    weight = merged["shell_throat_weight_overlay"].astype(float).clip(lower=0.0).to_numpy()

    rows: list[dict[str, Any]] = []
    for channel in CHANNELS:
        base_values = merged[f"volume_burden_{channel}_base"].astype(float).to_numpy()
        overlay_values = merged[f"volume_burden_{channel}_overlay"].astype(float).to_numpy()
        base_point = merged[f"bad_{channel}_base"].astype(float).to_numpy()
        overlay_point = merged[f"bad_{channel}_overlay"].astype(float).to_numpy()

        base_global = float(np.nansum(base_values))
        overlay_global = float(np.nansum(overlay_values))
        global_delta = overlay_global - base_global
        base_band = float(np.nansum(base_values[overlap]))
        overlay_band = float(np.nansum(overlay_values[overlap]))
        band_delta = overlay_band - base_band
        base_weighted = float(np.nansum(base_values * weight))
        overlay_weighted = float(np.nansum(overlay_values * weight))
        weighted_delta = overlay_weighted - base_weighted
        base_peak = float(np.nanmax(base_point[overlap])) if overlap.any() else math.nan
        overlay_peak = float(np.nanmax(overlay_point[overlap])) if overlap.any() else math.nan
        rows.append({
            **spec,
            "channel": channel,
            "shell_throat_overlap_points": int(overlap.sum()),
            "shell_throat_weight_sum": float(np.nansum(weight)),
            "shell_throat_gradient_max": float(merged.loc[overlap, "shell_throat_gradient_overlay"].astype(float).max()) if overlap.any() else math.nan,
            "global_burden_base": base_global,
            "global_burden_overlay": overlay_global,
            "global_burden_delta": global_delta,
            "shell_throat_burden_base": base_band,
            "shell_throat_burden_overlay": overlay_band,
            "shell_throat_burden_delta": band_delta,
            "shell_throat_burden_ratio": overlay_band / base_band if base_band else math.nan,
            "shell_throat_overlay_share": overlay_band / overlay_global if overlay_global else math.nan,
            "shell_throat_delta_fraction_of_global_delta": band_delta / global_delta if global_delta else math.nan,
            "shell_throat_weighted_burden_base": base_weighted,
            "shell_throat_weighted_burden_overlay": overlay_weighted,
            "shell_throat_weighted_burden_delta": weighted_delta,
            "shell_throat_weighted_burden_ratio": overlay_weighted / base_weighted if base_weighted else math.nan,
            "shell_throat_weighted_delta_fraction_of_global_delta": weighted_delta / global_delta if global_delta else math.nan,
            "shell_throat_point_peak_base": base_peak,
            "shell_throat_point_peak_overlay": overlay_peak,
            "shell_throat_point_peak_ratio": overlay_peak / base_peak if base_peak else math.nan,
        })

    focus = {row["channel"]: row for row in rows}
    summary: dict[str, Any] = {
        "shell_throat_overlap_points": int(overlap.sum()),
        "shell_throat_weight_sum": float(np.nansum(weight)),
        "shell_throat_gradient_max": float(merged.loc[overlap, "shell_throat_gradient_overlay"].astype(float).max()) if overlap.any() else math.nan,
    }
    finite_weighted = [row["shell_throat_weighted_burden_ratio"] for row in rows if math.isfinite(row["shell_throat_weighted_burden_ratio"])]
    finite_peaks = [row["shell_throat_point_peak_ratio"] for row in rows if math.isfinite(row["shell_throat_point_peak_ratio"])]
    summary["max_shell_throat_weighted_burden_ratio"] = max(finite_weighted) if finite_weighted else math.nan
    summary["max_shell_throat_point_peak_ratio"] = max(finite_peaks) if finite_peaks else math.nan
    for channel in ["neg_Tkk_radial", "abs_p_l", "abs_pOmega", "abs_j_l", "neg_rho_packet"]:
        row = focus[channel]
        summary[f"{channel}_shell_throat_weighted_ratio"] = row["shell_throat_weighted_burden_ratio"]
        summary[f"{channel}_shell_throat_peak_ratio"] = row["shell_throat_point_peak_ratio"]
        summary[f"{channel}_shell_throat_overlay_share"] = row["shell_throat_overlay_share"]
        summary[f"{channel}_shell_throat_delta_fraction"] = row["shell_throat_delta_fraction_of_global_delta"]
        summary[f"{channel}_shell_throat_weighted_delta_fraction"] = row["shell_throat_weighted_delta_fraction_of_global_delta"]
    return summary, rows


def _compare_case(
    base_points: pd.DataFrame,
    overlay_points: pd.DataFrame,
    spec: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    base_compact = _compact_by_channel(base_points)
    overlay_compact = _compact_by_channel(overlay_points)
    channel_rows = _compare_channels(base_compact, overlay_compact, spec)
    shell_throat_summary, shell_throat_rows = _compare_shell_throat_overlap(base_points, overlay_points, spec)

    merged = overlay_points.merge(base_points, on=["s", "l"], suffixes=("_overlay", "_base"))
    live = merged["inside_packet_live_overlay"].astype(bool).to_numpy()
    packet_delta = merged["packet_norm_overlay"].astype(float) - merged["packet_norm_base"].astype(float)
    safety = summarize_safety(overlay_points).iloc[0]

    burden_ratios = [row["total_burden_ratio"] for row in channel_rows if math.isfinite(row["total_burden_ratio"])]
    live_ratios = [row["live_packet_burden_ratio"] for row in channel_rows if math.isfinite(row["live_packet_burden_ratio"])]
    peak_ratios = [row["point_peak_ratio"] for row in channel_rows if math.isfinite(row["point_peak_ratio"])]
    max_window_row = overlay_points.loc[overlay_points["support_shell_window"].astype(float).idxmax()]

    summary = {
        **spec,
        "case": str(overlay_points["case"].iloc[0]),
        "rows": int(len(overlay_points)),
        "positive_packet_norm_live": int(safety["positive_packet_norm_live"]),
        "max_packet_norm_live": float(safety["max_packet_norm_live"]),
        "min_packet_norm_live": float(safety["min_packet_norm_live"]),
        "packet_norm_live_delta_max_abs": float(np.nanmax(np.abs(packet_delta.to_numpy()[live]))) if live.any() else math.nan,
        "packet_norm_live_delta_mean_abs": float(np.nanmean(np.abs(packet_delta.to_numpy()[live]))) if live.any() else math.nan,
        "support_shell_window_max": float(overlay_points["support_shell_window"].astype(float).max()),
        "support_shell_window_gt_1e_3_points": int((overlay_points["support_shell_window"].astype(float).abs() > 1.0e-3).sum()),
        "support_shell_delta_beta_abs_max": float(overlay_points["support_shell_delta_beta"].astype(float).abs().max()),
        "standing_support_packet_delta_beta_abs_max": float(overlay_points["standing_support_packet_delta_beta"].astype(float).abs().max()),
        "support_shell_delta_alpha_abs_max": float(overlay_points["support_shell_delta_alpha"].astype(float).abs().max()),
        "support_shell_delta_gamma_ll_abs_max": float(overlay_points["support_shell_delta_gamma_ll"].astype(float).abs().max()),
        "support_shell_delta_gamma_omega_abs_max": float(overlay_points["support_shell_delta_gamma_omega"].astype(float).abs().max()),
        "support_shell_window_peak_s": float(max_window_row["s"]),
        "support_shell_window_peak_l": float(max_window_row["l"]),
        "support_shell_window_peak_stage": str(max_window_row["stage"]),
        "support_shell_window_peak_region": str(max_window_row["region"]),
        "max_total_burden_ratio": max(burden_ratios) if burden_ratios else math.nan,
        "min_total_burden_ratio": min(burden_ratios) if burden_ratios else math.nan,
        "max_live_packet_burden_ratio": max(live_ratios) if live_ratios else math.nan,
        "max_point_peak_ratio": max(peak_ratios) if peak_ratios else math.nan,
        **shell_throat_summary,
    }

    focus = {row["channel"]: row for row in channel_rows}
    for channel in ["neg_Tkk_radial", "abs_p_l", "abs_pOmega", "abs_j_l", "neg_rho_euler", "neg_rho_packet"]:
        row = focus[channel]
        summary[f"{channel}_total_delta"] = row["total_burden_delta"]
        summary[f"{channel}_total_ratio"] = row["total_burden_ratio"]
        summary[f"{channel}_live_delta"] = row["live_packet_burden_delta"]
        summary[f"{channel}_live_ratio"] = row["live_packet_burden_ratio"]
        summary[f"{channel}_peak_ratio"] = row["point_peak_ratio"]
    _add_worldtube_exposure_summary(summary, overlay_points)
    _add_source_objective(summary)
    return summary, channel_rows, shell_throat_rows


def _build_specs(args: argparse.Namespace) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    support_carves = getattr(args, "standing_support_packet_exclusions", [0.0])
    support_carve_radii = getattr(args, "standing_support_packet_exclusion_radius_multipliers", [1.0])
    support_carve_widths = getattr(args, "standing_support_packet_exclusion_width_multipliers", [1.0])
    support_carve_schedules = getattr(args, "standing_support_packet_exclusion_schedules", ["live_only"])
    support_carve_shoulders = getattr(args, "standing_support_packet_exclusion_shoulders", [0.0])
    support_carve_shoulder_modes = getattr(args, "standing_support_packet_exclusion_shoulder_modes", ["filled"])
    support_carve_shoulder_radii = getattr(args, "standing_support_packet_exclusion_shoulder_radius_multipliers", [1.4])
    support_carve_shoulder_widths = getattr(args, "standing_support_packet_exclusion_shoulder_width_multipliers", [1.8])
    support_carve_shoulder_schedules = getattr(args, "standing_support_packet_exclusion_shoulder_schedules", ["live_only"])
    packet_lapse_gains = getattr(args, "standing_support_packet_lapse_log_gains", [0.0])
    packet_lapse_radii = getattr(args, "standing_support_packet_lapse_radius_multipliers", [1.0])
    packet_lapse_widths = getattr(args, "standing_support_packet_lapse_width_multipliers", [1.0])
    packet_lapse_schedules = getattr(args, "standing_support_packet_lapse_schedules", ["live_only"])
    packet_beta_rematch_gains = getattr(args, "standing_support_packet_beta_rematch_gains", [0.0])
    packet_beta_rematch_shapes = getattr(args, "standing_support_packet_beta_rematch_shapes", ["core"])
    packet_beta_rematch_radii = getattr(args, "standing_support_packet_beta_rematch_radius_multipliers", [1.0])
    packet_beta_rematch_widths = getattr(args, "standing_support_packet_beta_rematch_width_multipliers", [1.0])
    packet_beta_rematch_inner_radii = getattr(args, "standing_support_packet_beta_rematch_inner_radius_multipliers", [0.85])
    packet_beta_rematch_outer_radii = getattr(args, "standing_support_packet_beta_rematch_outer_radius_multipliers", [1.10])
    packet_beta_rematch_edge_softnesses = getattr(args, "standing_support_packet_beta_rematch_edge_softnesses", [1.0])
    packet_beta_rematch_temporal_widths = getattr(args, "standing_support_packet_beta_rematch_temporal_width_multipliers", [1.0])
    packet_beta_rematch_center_floors = getattr(args, "standing_support_packet_beta_rematch_center_floors", [0.0])
    packet_beta_rematch_schedules = getattr(args, "standing_support_packet_beta_rematch_schedules", ["live_only"])
    grid = product(
        args.amplitudes,
        args.signs,
        args.catch_leads,
        args.temporal_widths,
        args.temporal_profiles,
        args.temporal_shoulders,
        args.radial_profiles,
        args.support_shell_radial_widths,
        args.clock_lapse_ratios,
        args.rail_stretch_ratios,
        args.throat_capacity_ratios,
        support_carves,
        support_carve_radii,
        support_carve_widths,
        support_carve_schedules,
        support_carve_shoulders,
        support_carve_shoulder_modes,
        support_carve_shoulder_radii,
        support_carve_shoulder_widths,
        support_carve_shoulder_schedules,
        packet_lapse_gains,
        packet_lapse_radii,
        packet_lapse_widths,
        packet_lapse_schedules,
        packet_beta_rematch_gains,
        packet_beta_rematch_shapes,
        packet_beta_rematch_radii,
        packet_beta_rematch_widths,
        packet_beta_rematch_inner_radii,
        packet_beta_rematch_outer_radii,
        packet_beta_rematch_edge_softnesses,
        packet_beta_rematch_temporal_widths,
        packet_beta_rematch_center_floors,
        packet_beta_rematch_schedules,
    )
    for (
        abs_amplitude,
        sign_name,
        catch_lead,
        temporal_width,
        temporal_profile,
        temporal_shoulder,
        radial_profile,
        radial_width,
        clock_lapse_ratio,
        rail_stretch_ratio,
        throat_capacity_ratio,
        support_carve,
        support_carve_radius,
        support_carve_width,
        support_carve_schedule,
        support_carve_shoulder,
        support_carve_shoulder_mode,
        support_carve_shoulder_radius,
        support_carve_shoulder_width,
        support_carve_shoulder_schedule,
        packet_lapse_gain,
        packet_lapse_radius,
        packet_lapse_width,
        packet_lapse_schedule,
        packet_beta_rematch_gain,
        packet_beta_rematch_shape,
        packet_beta_rematch_radius,
        packet_beta_rematch_width,
        packet_beta_rematch_inner_radius,
        packet_beta_rematch_outer_radius,
        packet_beta_rematch_edge_softness,
        packet_beta_rematch_temporal_width,
        packet_beta_rematch_center_floor,
        packet_beta_rematch_schedule,
    ) in grid:
        sign = 1.0 if sign_name == "pos" else -1.0
        amplitude = sign * float(abs_amplitude)
        specs.append({
            "nominal_abs_amplitude": float(abs_amplitude),
            "abs_amplitude": float(abs_amplitude),
            "sign": sign_name,
            "amplitude": amplitude,
            "catch_lead": float(catch_lead),
            "temporal_width": float(temporal_width),
            "temporal_profile": str(temporal_profile),
            "temporal_shoulder": None if temporal_shoulder is None else float(temporal_shoulder),
            "radial_profile": str(radial_profile),
            "support_shell_radial_width": None if radial_width is None else float(radial_width),
            "clock_lapse_ratio": float(clock_lapse_ratio),
            "clock_lapse_log_gain": float(amplitude * float(clock_lapse_ratio)),
            "rail_stretch_ratio": float(rail_stretch_ratio),
            "rail_stretch_log_gain": float(amplitude * float(rail_stretch_ratio)),
            "throat_capacity_ratio": float(throat_capacity_ratio),
            "throat_capacity_log_gain": float(amplitude * float(throat_capacity_ratio)),
            "standing_support_packet_exclusion": float(support_carve),
            "standing_support_packet_exclusion_radius_multiplier": float(support_carve_radius),
            "standing_support_packet_exclusion_width_multiplier": float(support_carve_width),
            "standing_support_packet_exclusion_schedule": str(support_carve_schedule),
            "standing_support_packet_exclusion_shoulder": float(support_carve_shoulder),
            "standing_support_packet_exclusion_shoulder_mode": str(support_carve_shoulder_mode),
            "standing_support_packet_exclusion_shoulder_radius_multiplier": float(support_carve_shoulder_radius),
            "standing_support_packet_exclusion_shoulder_width_multiplier": float(support_carve_shoulder_width),
            "standing_support_packet_exclusion_shoulder_schedule": str(support_carve_shoulder_schedule),
            "standing_support_packet_lapse_log_gain": float(packet_lapse_gain),
            "standing_support_packet_lapse_radius_multiplier": float(packet_lapse_radius),
            "standing_support_packet_lapse_width_multiplier": float(packet_lapse_width),
            "standing_support_packet_lapse_schedule": str(packet_lapse_schedule),
            "standing_support_packet_beta_rematch_gain": float(packet_beta_rematch_gain),
            "standing_support_packet_beta_rematch_shape": str(packet_beta_rematch_shape),
            "standing_support_packet_beta_rematch_radius_multiplier": float(packet_beta_rematch_radius),
            "standing_support_packet_beta_rematch_width_multiplier": float(packet_beta_rematch_width),
            "standing_support_packet_beta_rematch_inner_radius_multiplier": float(packet_beta_rematch_inner_radius),
            "standing_support_packet_beta_rematch_outer_radius_multiplier": float(packet_beta_rematch_outer_radius),
            "standing_support_packet_beta_rematch_edge_softness": float(packet_beta_rematch_edge_softness),
            "standing_support_packet_beta_rematch_temporal_width_multiplier": float(packet_beta_rematch_temporal_width),
            "standing_support_packet_beta_rematch_center_floor": float(packet_beta_rematch_center_floor),
            "standing_support_packet_beta_rematch_schedule": str(packet_beta_rematch_schedule),
            "amplitude_normalization": "none",
            "target_delta_beta_abs_max": None,
            "window_max_for_normalization": None,
        })
    return specs


def _normalization_key(spec: dict[str, Any], config: dict[str, Any]) -> tuple[Any, ...]:
    return (
        spec["catch_lead"],
        spec["temporal_width"],
        spec["temporal_profile"],
        spec["temporal_shoulder"],
        spec["radial_profile"],
        spec["support_shell_radial_width"],
        config["variant"],
        config["service_factor"],
        config["smoothness_order"],
        config["support_shell_inner_multiplier"],
        config["support_shell_radial_multiplier"],
        config["support_shell_radial_width"],
        config["packet_exclusion"],
    )


def _window_max_for_spec(spec: dict[str, Any], grid: dict[str, Any], config: dict[str, Any]) -> float:
    overlay_case = branch_case(
        config["variant"],
        config["service_factor"],
        support_shell_overlay_enabled=True,
        support_shell_amplitude=1.0,
        support_shell_catch_lead=spec["catch_lead"],
        support_shell_temporal_width=spec["temporal_width"],
        support_shell_temporal_profile=spec["temporal_profile"],
        support_shell_temporal_shoulder=spec["temporal_shoulder"],
        support_shell_radial_profile=spec["radial_profile"],
        support_shell_smoothness_order=config["smoothness_order"],
        support_shell_inner_multiplier=config["support_shell_inner_multiplier"],
        support_shell_radial_multiplier=config["support_shell_radial_multiplier"],
        support_shell_radial_width=spec["support_shell_radial_width"],
        support_shell_packet_exclusion=config["packet_exclusion"],
    )
    params = overlay_case.params
    s_values = np.linspace(float(grid["s_min"]), float(grid["s_max"]), int(grid["ns"]))
    l_values = np.linspace(float(grid["l_min"]), float(grid["l_max"]), int(grid["nl"]))
    peak = 0.0
    for s in s_values:
        for l in l_values:
            peak = max(peak, abs(float(support_shell_overlay_window(float(s), float(l), params))))
    return peak


def _apply_delta_beta_normalization(
    specs: list[dict[str, Any]],
    grid: dict[str, Any],
    config: dict[str, Any],
    target_delta_beta_abs_max: float | None,
) -> list[dict[str, Any]]:
    if target_delta_beta_abs_max is None:
        return specs
    target = abs(float(target_delta_beta_abs_max))
    if target <= 0.0:
        raise ValueError("--target-delta-beta-abs-max must be positive")

    window_cache: dict[tuple[Any, ...], float] = {}
    normalized: list[dict[str, Any]] = []
    for spec in specs:
        key = _normalization_key(spec, config)
        window_max = window_cache.get(key)
        if window_max is None:
            window_max = _window_max_for_spec(spec, grid, config)
            window_cache[key] = window_max
        if window_max <= 0.0 or not math.isfinite(window_max):
            raise ValueError(f"Cannot normalize support shell with zero window max: {spec}")
        abs_amplitude = target / window_max
        sign = 1.0 if spec["sign"] == "pos" else -1.0
        amplitude = sign * abs_amplitude
        next_spec = {
            **spec,
            "abs_amplitude": abs_amplitude,
            "amplitude": amplitude,
            "clock_lapse_log_gain": amplitude * float(spec["clock_lapse_ratio"]),
            "rail_stretch_log_gain": amplitude * float(spec["rail_stretch_ratio"]),
            "throat_capacity_log_gain": amplitude * float(spec["throat_capacity_ratio"]),
            "amplitude_normalization": "target_delta_beta_abs_max",
            "target_delta_beta_abs_max": target,
            "window_max_for_normalization": window_max,
        }
        normalized.append(next_spec)
    return normalized


def _overlay_config(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "variant": args.variant,
        "service_factor": float(args.service_factor),
        "smoothness_order": int(args.smoothness_order),
        "support_shell_inner_multiplier": float(args.support_shell_inner_multiplier),
        "support_shell_radial_multiplier": float(args.support_shell_radial_multiplier),
        "support_shell_radial_width": args.support_shell_radial_width,
        "packet_exclusion": float(args.packet_exclusion),
    }


def _run_overlay_spec(
    spec: dict[str, Any],
    base_points: pd.DataFrame,
    grid: dict[str, Any],
    config: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    overlay_case = branch_case(
        config["variant"],
        config["service_factor"],
        support_shell_overlay_enabled=True,
        support_shell_amplitude=spec["amplitude"],
        support_shell_catch_lead=spec["catch_lead"],
        support_shell_temporal_width=spec["temporal_width"],
        support_shell_temporal_profile=spec["temporal_profile"],
        support_shell_temporal_shoulder=spec["temporal_shoulder"],
        support_shell_radial_profile=spec["radial_profile"],
        support_shell_smoothness_order=config["smoothness_order"],
        support_shell_inner_multiplier=config["support_shell_inner_multiplier"],
        support_shell_radial_multiplier=config["support_shell_radial_multiplier"],
        support_shell_radial_width=spec["support_shell_radial_width"],
        support_shell_packet_exclusion=config["packet_exclusion"],
        support_shell_clock_lapse_log_gain=spec["clock_lapse_log_gain"],
        support_shell_rail_stretch_log_gain=spec["rail_stretch_log_gain"],
        support_shell_throat_capacity_log_gain=spec["throat_capacity_log_gain"],
        standing_support_packet_exclusion=spec["standing_support_packet_exclusion"],
        standing_support_packet_exclusion_radius_multiplier=spec["standing_support_packet_exclusion_radius_multiplier"],
        standing_support_packet_exclusion_width_multiplier=spec["standing_support_packet_exclusion_width_multiplier"],
        standing_support_packet_exclusion_schedule=spec["standing_support_packet_exclusion_schedule"],
        standing_support_packet_exclusion_shoulder=spec["standing_support_packet_exclusion_shoulder"],
        standing_support_packet_exclusion_shoulder_mode=spec["standing_support_packet_exclusion_shoulder_mode"],
        standing_support_packet_exclusion_shoulder_radius_multiplier=spec["standing_support_packet_exclusion_shoulder_radius_multiplier"],
        standing_support_packet_exclusion_shoulder_width_multiplier=spec["standing_support_packet_exclusion_shoulder_width_multiplier"],
        standing_support_packet_exclusion_shoulder_schedule=spec["standing_support_packet_exclusion_shoulder_schedule"],
        standing_support_packet_lapse_log_gain=spec["standing_support_packet_lapse_log_gain"],
        standing_support_packet_lapse_radius_multiplier=spec["standing_support_packet_lapse_radius_multiplier"],
        standing_support_packet_lapse_width_multiplier=spec["standing_support_packet_lapse_width_multiplier"],
        standing_support_packet_lapse_schedule=spec["standing_support_packet_lapse_schedule"],
        standing_support_packet_beta_rematch_gain=spec["standing_support_packet_beta_rematch_gain"],
        standing_support_packet_beta_rematch_shape=spec["standing_support_packet_beta_rematch_shape"],
        standing_support_packet_beta_rematch_radius_multiplier=spec["standing_support_packet_beta_rematch_radius_multiplier"],
        standing_support_packet_beta_rematch_width_multiplier=spec["standing_support_packet_beta_rematch_width_multiplier"],
        standing_support_packet_beta_rematch_inner_radius_multiplier=spec["standing_support_packet_beta_rematch_inner_radius_multiplier"],
        standing_support_packet_beta_rematch_outer_radius_multiplier=spec["standing_support_packet_beta_rematch_outer_radius_multiplier"],
        standing_support_packet_beta_rematch_edge_softness=spec["standing_support_packet_beta_rematch_edge_softness"],
        standing_support_packet_beta_rematch_temporal_width_multiplier=spec["standing_support_packet_beta_rematch_temporal_width_multiplier"],
        standing_support_packet_beta_rematch_center_floor=spec["standing_support_packet_beta_rematch_center_floor"],
        standing_support_packet_beta_rematch_schedule=spec["standing_support_packet_beta_rematch_schedule"],
    )
    overlay_points = compute_case(overlay_case, progress=False, **grid)
    return _compare_case(base_points, overlay_points, spec)


def _case_dir(outdir: Path, spec: dict[str, Any]) -> Path:
    return outdir / "cases" / _case_slug(spec)


def _case_output_paths(outdir: Path, spec: dict[str, Any]) -> dict[str, Path]:
    case_dir = _case_dir(outdir, spec)
    return {
        "summary": case_dir / "summary.csv",
        "channel_deltas": case_dir / "channel_deltas.csv",
        "shell_throat_overlap": case_dir / "shell_throat_overlap.csv",
        "failure": case_dir / "failure.json",
    }


def _write_case_outputs(
    outdir: Path,
    summary: dict[str, Any],
    channels: list[dict[str, Any]],
    shell_throat: list[dict[str, Any]],
) -> None:
    spec = summary
    case_dir = _case_dir(outdir, spec)
    case_dir.mkdir(parents=True, exist_ok=True)
    paths = _case_output_paths(outdir, spec)
    pd.DataFrame([summary]).to_csv(paths["summary"], index=False)
    pd.DataFrame(channels).to_csv(paths["channel_deltas"], index=False)
    pd.DataFrame(shell_throat).to_csv(paths["shell_throat_overlap"], index=False)
    if paths["failure"].exists():
        paths["failure"].unlink()


def _write_case_failure(outdir: Path, failure: dict[str, Any]) -> None:
    case_dir = _case_dir(outdir, failure)
    case_dir.mkdir(parents=True, exist_ok=True)
    paths = _case_output_paths(outdir, failure)
    paths["failure"].write_text(json.dumps(failure, indent=2), encoding="utf-8")


def _load_case_outputs(
    outdir: Path,
    spec: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]] | None:
    paths = _case_output_paths(outdir, spec)
    if not (paths["summary"].exists() and paths["channel_deltas"].exists() and paths["shell_throat_overlap"].exists()):
        return None
    summary_rows = pd.read_csv(paths["summary"]).to_dict("records")
    if not summary_rows:
        return None
    channels = pd.read_csv(paths["channel_deltas"]).to_dict("records")
    shell_throat = pd.read_csv(paths["shell_throat_overlap"]).to_dict("records")
    return summary_rows[0], channels, shell_throat


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sweep the continuous support-shell metric overlay in the 4D source ledger.")
    parser.add_argument("--variant", default="tuned_w0569_eta200")
    parser.add_argument("--service-factor", type=float, default=5.0)
    parser.add_argument("--outdir", type=Path, default=Path("runs/source_overlay_sweep_v5"))
    parser.add_argument("--amplitudes", type=float, nargs="+", default=[1.0e-7, 1.0e-6, 1.0e-5, 1.0e-4, 1.0e-3, 1.0e-2])
    parser.add_argument(
        "--target-delta-beta-abs-max",
        type=float,
        nargs="+",
        default=None,
        help=(
            "Normalize each case amplitude so max |support_shell_delta_beta| matches one or more targets. "
            "This gives fair shape comparisons when radial/temporal windows have different peak values."
        ),
    )
    parser.add_argument("--signs", choices=["pos", "neg"], nargs="+", default=["pos", "neg"])
    parser.add_argument("--catch-leads", type=float, nargs="+", default=[1.0])
    parser.add_argument("--temporal-widths", type=float, nargs="+", default=[0.35])
    parser.add_argument(
        "--temporal-profiles",
        choices=["gaussian", "raised_cosine", "minjerk_pulse", "smooth_box"],
        nargs="+",
        default=["gaussian"],
        help="Support-shell temporal window families.",
    )
    parser.add_argument(
        "--temporal-shoulders",
        type=float,
        nargs="+",
        default=[None],
        help="Optional temporal shoulder widths for smooth_box profiles.",
    )
    parser.add_argument(
        "--radial-profiles",
        choices=["smooth_box", "gaussian_annulus", "raised_cosine_annulus"],
        nargs="+",
        default=["smooth_box"],
        help="Support-shell radial window families.",
    )
    parser.add_argument(
        "--clock-lapse-ratios",
        type=float,
        nargs="+",
        default=[0.0],
        help="Log-gain ratios against the signed carrying-flow amplitude for the support-shell clock-lapse partner.",
    )
    parser.add_argument(
        "--rail-stretch-ratios",
        type=float,
        nargs="+",
        default=[0.0],
        help="Log-gain ratios against the signed carrying-flow amplitude for the support-shell rail-stretch partner.",
    )
    parser.add_argument(
        "--throat-capacity-ratios",
        type=float,
        nargs="+",
        default=[0.0],
        help="Log-gain ratios against the signed carrying-flow amplitude for the support-shell throat-capacity partner.",
    )
    parser.add_argument("--smoothness-order", type=int, default=1)
    parser.add_argument("--support-shell-inner-multiplier", type=float, default=0.65)
    parser.add_argument("--support-shell-radial-multiplier", type=float, default=1.20)
    parser.add_argument("--support-shell-radial-width", type=float, default=None)
    parser.add_argument(
        "--support-shell-radial-widths",
        type=float,
        nargs="+",
        default=None,
        help="Optional sweep list for radial shoulder/sigma/half-width values.",
    )
    parser.add_argument("--packet-exclusion", type=float, default=1.0)
    parser.add_argument(
        "--standing-support-packet-exclusions",
        type=float,
        nargs="+",
        default=[0.0],
        help="Experimental standing-support packet carve-out strengths.",
    )
    parser.add_argument(
        "--standing-support-packet-exclusion-radius-multipliers",
        type=float,
        nargs="+",
        default=[1.0],
        help="Radius multipliers for the standing-support packet carve-out window.",
    )
    parser.add_argument(
        "--standing-support-packet-exclusion-width-multipliers",
        type=float,
        nargs="+",
        default=[1.0],
        help="Transition-width multipliers for the standing-support packet carve-out window.",
    )
    parser.add_argument(
        "--standing-support-packet-exclusion-schedules",
        choices=["live_only", "entry_catch_release", "catch_release", "always"],
        nargs="+",
        default=["live_only"],
        help="Temporal schedules for the standing-support packet carve-out window.",
    )
    parser.add_argument(
        "--standing-support-packet-exclusion-shoulders",
        type=float,
        nargs="+",
        default=[0.0],
        help="Wider/softer shoulder carve strengths added to the standing-support packet carve.",
    )
    parser.add_argument(
        "--standing-support-packet-exclusion-shoulder-modes",
        choices=["filled", "annular"],
        nargs="+",
        default=["filled"],
        help="Shape mode for the shoulder carve window.",
    )
    parser.add_argument(
        "--standing-support-packet-exclusion-shoulder-radius-multipliers",
        type=float,
        nargs="+",
        default=[1.4],
        help="Radius multipliers for the shoulder carve window.",
    )
    parser.add_argument(
        "--standing-support-packet-exclusion-shoulder-width-multipliers",
        type=float,
        nargs="+",
        default=[1.8],
        help="Transition-width multipliers for the shoulder carve window.",
    )
    parser.add_argument(
        "--standing-support-packet-exclusion-shoulder-schedules",
        choices=["live_only", "entry_catch_release", "catch_release", "always"],
        nargs="+",
        default=["live_only"],
        help="Temporal schedules for the shoulder carve window.",
    )
    parser.add_argument(
        "--standing-support-packet-lapse-log-gains",
        type=float,
        nargs="+",
        default=[0.0],
        help="Experimental packet-local lapse log-gains applied on a packet lapse window.",
    )
    parser.add_argument(
        "--standing-support-packet-lapse-radius-multipliers",
        type=float,
        nargs="+",
        default=[1.0],
        help="Radius multipliers for the packet-local lapse window.",
    )
    parser.add_argument(
        "--standing-support-packet-lapse-width-multipliers",
        type=float,
        nargs="+",
        default=[1.0],
        help="Transition-width multipliers for the packet-local lapse window.",
    )
    parser.add_argument(
        "--standing-support-packet-lapse-schedules",
        choices=["live_only", "entry_catch_release", "catch_release", "always"],
        nargs="+",
        default=["live_only"],
        help="Temporal schedules for the packet-local lapse window.",
    )
    parser.add_argument(
        "--standing-support-packet-beta-rematch-gains",
        type=float,
        nargs="+",
        default=[0.0],
        help="Packet-local beta rematch gains. Positive values nudge beta toward cancelling packet coordinate velocity.",
    )
    parser.add_argument(
        "--standing-support-packet-beta-rematch-shapes",
        choices=["core", "shoulder", "annular", "edge_soften", "trailing_edge"],
        nargs="+",
        default=["core"],
        help="Shape families for the packet-local beta rematch window.",
    )
    parser.add_argument(
        "--standing-support-packet-beta-rematch-radius-multipliers",
        type=float,
        nargs="+",
        default=[1.0],
        help="Radius multipliers for the packet-local beta rematch window.",
    )
    parser.add_argument(
        "--standing-support-packet-beta-rematch-width-multipliers",
        type=float,
        nargs="+",
        default=[1.0],
        help="Transition-width multipliers for the packet-local beta rematch window.",
    )
    parser.add_argument(
        "--standing-support-packet-beta-rematch-inner-radius-multipliers",
        type=float,
        nargs="+",
        default=[0.85],
        help="Inner radius multipliers for annular/trailing beta rematch windows.",
    )
    parser.add_argument(
        "--standing-support-packet-beta-rematch-outer-radius-multipliers",
        type=float,
        nargs="+",
        default=[1.10],
        help="Outer radius multipliers for annular/trailing beta rematch windows.",
    )
    parser.add_argument(
        "--standing-support-packet-beta-rematch-edge-softnesses",
        type=float,
        nargs="+",
        default=[1.0],
        help="Extra softness multipliers for annular/trailing beta rematch edges.",
    )
    parser.add_argument(
        "--standing-support-packet-beta-rematch-temporal-width-multipliers",
        type=float,
        nargs="+",
        default=[1.0],
        help="Temporal smoothing multipliers for beta rematch schedules.",
    )
    parser.add_argument(
        "--standing-support-packet-beta-rematch-center-floors",
        type=float,
        nargs="+",
        default=[0.0],
        help="Weak filled-core floor mixed into shaped beta rematch windows.",
    )
    parser.add_argument(
        "--standing-support-packet-beta-rematch-schedules",
        choices=["live_only", "entry_catch_release", "catch_release", "always"],
        nargs="+",
        default=["live_only"],
        help="Temporal schedules for the packet-local beta rematch window.",
    )
    parser.add_argument("--ns", type=int, default=None)
    parser.add_argument("--nl", type=int, default=73)
    parser.add_argument("--s-min", type=float, default=None)
    parser.add_argument("--s-max", type=float, default=DEFAULT_S_MAX)
    parser.add_argument("--l-min", type=float, default=-2.80)
    parser.add_argument("--l-max", type=float, default=2.80)
    parser.add_argument("--h-s", type=float, default=2.5e-3)
    parser.add_argument("--h-l", type=float, default=2.5e-3)
    parser.add_argument("--jobs", type=int, default=1, help="Number of worker processes for overlay cases.")
    parser.add_argument("--resume", action="store_true", help="Reuse completed per-case outputs when available.")
    parser.add_argument("--case-output", action="store_true", help="Write per-case outputs as each overlay case finishes.")
    parser.add_argument("--fail-fast", action="store_true", help="Stop the sweep at the first overlay failure.")
    parser.add_argument("--quiet", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    grid_case = branch_case(
        args.variant,
        args.service_factor,
        support_shell_overlay_enabled=True,
        support_shell_catch_lead=args.catch_leads[0],
        support_shell_temporal_width=args.temporal_widths[0],
        support_shell_temporal_profile=args.temporal_profiles[0],
        support_shell_temporal_shoulder=args.temporal_shoulders[0],
        support_shell_radial_profile=args.radial_profiles[0],
        support_shell_smoothness_order=args.smoothness_order,
        support_shell_inner_multiplier=args.support_shell_inner_multiplier,
        support_shell_radial_multiplier=args.support_shell_radial_multiplier,
        support_shell_radial_width=(args.support_shell_radial_widths or [args.support_shell_radial_width])[0],
        support_shell_packet_exclusion=args.packet_exclusion,
        support_shell_clock_lapse_log_gain=0.0,
        support_shell_rail_stretch_log_gain=0.0,
        support_shell_throat_capacity_log_gain=0.0,
    )
    grid = _resolve_grid(args, grid_case)
    base_case = branch_case(args.variant, args.service_factor)
    base_points = compute_case(base_case, progress=not args.quiet, **grid)
    args.support_shell_radial_widths = args.support_shell_radial_widths or [args.support_shell_radial_width]
    config = _overlay_config(args)
    base_specs = _build_specs(args)
    target_delta_beta_abs_maxs = args.target_delta_beta_abs_max or [None]
    specs = [
        spec
        for target_delta_beta_abs_max in target_delta_beta_abs_maxs
        for spec in _apply_delta_beta_normalization(
            base_specs,
            grid,
            config,
            target_delta_beta_abs_max,
        )
    ]
    case_output = bool(args.case_output or args.resume)

    summary_rows: list[dict[str, Any]] = []
    channel_rows: list[dict[str, Any]] = []
    shell_throat_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    remaining_specs: list[dict[str, Any]] = []
    resumed = 0
    for spec in specs:
        loaded = _load_case_outputs(args.outdir, spec) if args.resume else None
        if loaded is None:
            remaining_specs.append(spec)
            continue
        summary, channels, shell_throat = loaded
        summary_rows.append(summary)
        channel_rows.extend(channels)
        shell_throat_rows.extend(shell_throat)
        resumed += 1

    def record_success(summary: dict[str, Any], channels: list[dict[str, Any]], shell_throat: list[dict[str, Any]]) -> None:
        summary_rows.append(summary)
        channel_rows.extend(channels)
        shell_throat_rows.extend(shell_throat)
        if case_output:
            _write_case_outputs(args.outdir, summary, channels, shell_throat)

    def record_failure(spec: dict[str, Any], exc: Exception) -> None:
        failure = {**spec, "error": repr(exc)}
        failures.append(failure)
        if case_output:
            _write_case_failure(args.outdir, failure)

    fail_fast_triggered = False
    total = len(specs)
    if remaining_specs and int(args.jobs) > 1:
        workers = max(1, int(args.jobs))
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(_run_overlay_spec, spec, base_points, grid, config): spec
                for spec in remaining_specs
            }
            completed = resumed
            for future in as_completed(futures):
                spec = futures[future]
                completed += 1
                if not args.quiet:
                    print(
                        f"[{completed}/{total}] amp={spec['amplitude']:g} lead={spec['catch_lead']:g} "
                        f"tw={spec['temporal_width']:g} tp={spec['temporal_profile']} rp={spec['radial_profile']} "
                        f"cl={spec['clock_lapse_log_gain']:g} "
                        f"rs={spec['rail_stretch_log_gain']:g} tc={spec['throat_capacity_log_gain']:g} "
                        f"wc={spec['standing_support_packet_exclusion']:g} "
                        f"wsh={spec['standing_support_packet_exclusion_shoulder']:g} "
                        f"wshm={spec['standing_support_packet_exclusion_shoulder_mode']} "
                        f"wlap={spec['standing_support_packet_lapse_log_gain']:g} "
                        f"wlr={spec['standing_support_packet_lapse_radius_multiplier']:g} "
                        f"wlw={spec['standing_support_packet_lapse_width_multiplier']:g} "
                        f"wbeta={spec['standing_support_packet_beta_rematch_gain']:g} "
                        f"wbshape={spec['standing_support_packet_beta_rematch_shape']} "
                        f"wbr={spec['standing_support_packet_beta_rematch_radius_multiplier']:g} "
                        f"wbw={spec['standing_support_packet_beta_rematch_width_multiplier']:g} "
                        f"wbi={spec['standing_support_packet_beta_rematch_inner_radius_multiplier']:g} "
                        f"wbo={spec['standing_support_packet_beta_rematch_outer_radius_multiplier']:g} "
                        f"wbf={spec['standing_support_packet_beta_rematch_center_floor']:g}",
                        flush=True,
                    )
                try:
                    summary, channels, shell_throat = future.result()
                    record_success(summary, channels, shell_throat)
                except Exception as exc:
                    record_failure(spec, exc)
                    if args.fail_fast:
                        fail_fast_triggered = True
                        for pending in futures:
                            pending.cancel()
                        break
    else:
        completed = resumed
        for spec in remaining_specs:
            completed += 1
            if not args.quiet:
                print(
                    f"[{completed}/{total}] amp={spec['amplitude']:g} lead={spec['catch_lead']:g} "
                    f"tw={spec['temporal_width']:g} tp={spec['temporal_profile']} rp={spec['radial_profile']} "
                    f"cl={spec['clock_lapse_log_gain']:g} "
                    f"rs={spec['rail_stretch_log_gain']:g} tc={spec['throat_capacity_log_gain']:g} "
                    f"wc={spec['standing_support_packet_exclusion']:g} "
                    f"wsh={spec['standing_support_packet_exclusion_shoulder']:g} "
                    f"wshm={spec['standing_support_packet_exclusion_shoulder_mode']} "
                    f"wlap={spec['standing_support_packet_lapse_log_gain']:g} "
                    f"wlr={spec['standing_support_packet_lapse_radius_multiplier']:g} "
                    f"wlw={spec['standing_support_packet_lapse_width_multiplier']:g} "
                    f"wbeta={spec['standing_support_packet_beta_rematch_gain']:g} "
                    f"wbshape={spec['standing_support_packet_beta_rematch_shape']} "
                    f"wbr={spec['standing_support_packet_beta_rematch_radius_multiplier']:g} "
                    f"wbw={spec['standing_support_packet_beta_rematch_width_multiplier']:g} "
                    f"wbi={spec['standing_support_packet_beta_rematch_inner_radius_multiplier']:g} "
                    f"wbo={spec['standing_support_packet_beta_rematch_outer_radius_multiplier']:g} "
                    f"wbf={spec['standing_support_packet_beta_rematch_center_floor']:g}",
                    flush=True,
                )
            try:
                summary, channels, shell_throat = _run_overlay_spec(spec, base_points, grid, config)
                record_success(summary, channels, shell_throat)
            except Exception as exc:
                record_failure(spec, exc)
                if args.fail_fast:
                    fail_fast_triggered = True
                    break

    sort_cols = _sort_cols()
    summary_df = pd.DataFrame(summary_rows)
    channel_df = pd.DataFrame(channel_rows)
    shell_throat_df = pd.DataFrame(shell_throat_rows)
    if not summary_df.empty:
        summary_df = summary_df.sort_values([col for col in sort_cols if col in summary_df.columns])
    if not channel_df.empty:
        channel_df = channel_df.sort_values([col for col in [*sort_cols, "channel"] if col in channel_df.columns])
    if not shell_throat_df.empty:
        shell_throat_df = shell_throat_df.sort_values([col for col in [*sort_cols, "channel"] if col in shell_throat_df.columns])
    failure_df = pd.DataFrame(failures)

    summary_path = args.outdir / "source_overlay_sweep_summary.csv"
    channel_path = args.outdir / "source_overlay_sweep_channel_deltas.csv"
    shell_throat_path = args.outdir / "source_overlay_sweep_shell_throat_overlap.csv"
    objective_path = args.outdir / "source_overlay_sweep_objective_ranking.csv"
    worldtube_objective_path = args.outdir / "source_overlay_sweep_worldtube_ranking.csv"
    failure_path = args.outdir / "source_overlay_sweep_failures.csv"
    summary_df.to_csv(summary_path, index=False)
    channel_df.to_csv(channel_path, index=False)
    shell_throat_df.to_csv(shell_throat_path, index=False)
    objective_df = (
        summary_df.sort_values([col for col in ["source_objective_score", *sort_cols] if col in summary_df.columns])
        if not summary_df.empty
        else summary_df
    )
    objective_df.to_csv(objective_path, index=False)
    worldtube_objective_df = (
        summary_df.sort_values([col for col in ["worldtube_exposure_score", *sort_cols] if col in summary_df.columns])
        if not summary_df.empty
        else summary_df
    )
    worldtube_objective_df.to_csv(worldtube_objective_path, index=False)
    failure_df.to_csv(failure_path, index=False)

    metadata = {
        "variant": args.variant,
        "service_factor": args.service_factor,
        "grid": grid,
        "amplitudes": args.amplitudes,
        "target_delta_beta_abs_max": args.target_delta_beta_abs_max,
        "signs": args.signs,
        "catch_leads": args.catch_leads,
        "temporal_widths": args.temporal_widths,
        "temporal_profiles": args.temporal_profiles,
        "temporal_shoulders": args.temporal_shoulders,
        "radial_profiles": args.radial_profiles,
        "clock_lapse_ratios": args.clock_lapse_ratios,
        "rail_stretch_ratios": args.rail_stretch_ratios,
        "throat_capacity_ratios": args.throat_capacity_ratios,
        "standing_support_packet_exclusions": args.standing_support_packet_exclusions,
        "standing_support_packet_exclusion_radius_multipliers": args.standing_support_packet_exclusion_radius_multipliers,
        "standing_support_packet_exclusion_width_multipliers": args.standing_support_packet_exclusion_width_multipliers,
        "standing_support_packet_exclusion_schedules": args.standing_support_packet_exclusion_schedules,
        "standing_support_packet_exclusion_shoulders": args.standing_support_packet_exclusion_shoulders,
        "standing_support_packet_exclusion_shoulder_modes": args.standing_support_packet_exclusion_shoulder_modes,
        "standing_support_packet_exclusion_shoulder_radius_multipliers": args.standing_support_packet_exclusion_shoulder_radius_multipliers,
        "standing_support_packet_exclusion_shoulder_width_multipliers": args.standing_support_packet_exclusion_shoulder_width_multipliers,
        "standing_support_packet_exclusion_shoulder_schedules": args.standing_support_packet_exclusion_shoulder_schedules,
        "standing_support_packet_lapse_log_gains": args.standing_support_packet_lapse_log_gains,
        "standing_support_packet_lapse_radius_multipliers": args.standing_support_packet_lapse_radius_multipliers,
        "standing_support_packet_lapse_width_multipliers": args.standing_support_packet_lapse_width_multipliers,
        "standing_support_packet_lapse_schedules": args.standing_support_packet_lapse_schedules,
        "standing_support_packet_beta_rematch_gains": args.standing_support_packet_beta_rematch_gains,
        "standing_support_packet_beta_rematch_shapes": args.standing_support_packet_beta_rematch_shapes,
        "standing_support_packet_beta_rematch_radius_multipliers": args.standing_support_packet_beta_rematch_radius_multipliers,
        "standing_support_packet_beta_rematch_width_multipliers": args.standing_support_packet_beta_rematch_width_multipliers,
        "standing_support_packet_beta_rematch_inner_radius_multipliers": args.standing_support_packet_beta_rematch_inner_radius_multipliers,
        "standing_support_packet_beta_rematch_outer_radius_multipliers": args.standing_support_packet_beta_rematch_outer_radius_multipliers,
        "standing_support_packet_beta_rematch_edge_softnesses": args.standing_support_packet_beta_rematch_edge_softnesses,
        "standing_support_packet_beta_rematch_temporal_width_multipliers": args.standing_support_packet_beta_rematch_temporal_width_multipliers,
        "standing_support_packet_beta_rematch_center_floors": args.standing_support_packet_beta_rematch_center_floors,
        "standing_support_packet_beta_rematch_schedules": args.standing_support_packet_beta_rematch_schedules,
        "smoothness_order": args.smoothness_order,
        "support_shell_inner_multiplier": args.support_shell_inner_multiplier,
        "support_shell_radial_multiplier": args.support_shell_radial_multiplier,
        "support_shell_radial_width": args.support_shell_radial_width,
        "support_shell_radial_widths": args.support_shell_radial_widths,
        "packet_exclusion": args.packet_exclusion,
        "jobs": int(args.jobs),
        "resume": bool(args.resume),
        "case_output": case_output,
        "resumed_cases": resumed,
        "requested_cases": len(specs),
        "completed_cases": len(summary_df),
        "files": {
            "summary": str(summary_path),
            "channel_deltas": str(channel_path),
            "shell_throat_overlap": str(shell_throat_path),
            "objective_ranking": str(objective_path),
            "worldtube_ranking": str(worldtube_objective_path),
            "failures": str(failure_path),
        },
        "failures": len(failures),
    }
    write_manifest(args.outdir / "source_overlay_sweep_metadata.json", metadata)
    print(json.dumps({
        "ok": len(failures) == 0 and not fail_fast_triggered,
        "outdir": str(args.outdir),
        "rows": len(summary_df),
        "failures": len(failures),
        "resumed": resumed,
    }, indent=2))
    return 0 if not failures and not fail_fast_triggered else 1


if __name__ == "__main__":
    raise SystemExit(main())
