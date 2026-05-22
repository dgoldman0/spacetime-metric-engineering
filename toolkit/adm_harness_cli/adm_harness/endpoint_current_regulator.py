from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .endpoint_j_conservation import ASSIGNMENT_SCOPES, J_SECTOR, build_endpoint_j_conservation_tables
from .endpoint_j_source_class_screen import classify_endpoint_source_frame
from .source_ledger import sha256_file, write_manifest
from .source_screening import resolve_manifest_path


FIELD_COLUMNS = ("sector_rho", "sector_p_l", "sector_j_l", "sector_p_omega")
EPS = 1.0e-30


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if not math.isfinite(number):
        return default
    return number


def _safe_ratio(num: float, denom: float) -> float:
    return float(num / denom) if denom > 0.0 else float("nan")


def _bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin({"1", "true", "yes"})


def _quantile(series: pd.Series, q: float) -> float:
    values = series.astype(float).replace([np.inf, -np.inf], np.nan).dropna()
    return float(values.quantile(q)) if len(values) else float("nan")


def _rows_for_fraction(weights: np.ndarray, fraction: float) -> float:
    total = float(np.sum(weights))
    if len(weights) == 0 or total <= 0.0:
        return float("nan")
    ordered = np.sort(weights)[::-1]
    return float((np.searchsorted(np.cumsum(ordered), fraction * total) + 1) / len(weights))


def _top_share(weights: np.ndarray, row_fraction: float) -> float:
    total = float(np.sum(weights))
    if len(weights) == 0 or total <= 0.0:
        return float("nan")
    count = max(1, int(math.ceil(float(row_fraction) * len(weights))))
    return float(np.sort(weights)[::-1][:count].sum() / total)


def _weighted_quantile(values: np.ndarray, weights: np.ndarray, quantile: float) -> float:
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0.0)
    if not np.any(mask):
        return float("nan")
    ordered = np.argsort(values[mask])
    ordered_values = values[mask][ordered]
    ordered_weights = weights[mask][ordered]
    cumulative = np.cumsum(ordered_weights)
    target = float(quantile) * float(cumulative[-1])
    index = int(np.searchsorted(cumulative, target, side="left"))
    index = min(index, len(ordered_values) - 1)
    return float(ordered_values[index])


def _weighted_width(values: np.ndarray, weights: np.ndarray, lower: float, upper: float) -> float:
    lo = _weighted_quantile(values, weights, lower)
    hi = _weighted_quantile(values, weights, upper)
    return float(hi - lo) if math.isfinite(lo) and math.isfinite(hi) else float("nan")


def _weighted_std(values: np.ndarray, weights: np.ndarray) -> float:
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0.0)
    if not np.any(mask):
        return float("nan")
    selected_values = values[mask]
    selected_weights = weights[mask]
    total = float(selected_weights.sum())
    mean = float(np.sum(selected_values * selected_weights) / total)
    var = float(np.sum(np.square(selected_values - mean) * selected_weights) / total)
    return float(math.sqrt(max(var, 0.0)))


def _derive_sector_columns(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["sector_Tkk_plus"] = out["sector_rho"] + out["sector_p_l"] - 2.0 * out["sector_j_l"]
    out["sector_Tkk_minus"] = out["sector_rho"] + out["sector_p_l"] + 2.0 * out["sector_j_l"]
    out["sector_selected_null_margin"] = out["sector_rho"] + out["sector_p_l"] - 2.0 * out["sector_j_l"].abs()
    out["sector_selected_null_deficit_density"] = (-out["sector_selected_null_margin"]).clip(lower=0.0)
    out["sector_pair_l1_density"] = out["sector_rho"].abs() + out["sector_p_l"].abs()
    out["sector_abs_current_density"] = out["sector_j_l"].abs()
    out["sector_abs_pomega_density"] = out["sector_p_omega"].abs()
    volume = out["volume_weight"].astype(float)
    for col in [
        "sector_selected_null_deficit_density",
        "sector_pair_l1_density",
        "sector_abs_current_density",
        "sector_abs_pomega_density",
    ]:
        out[f"{col}_volume"] = out[col] * volume
    return out


def build_current_regulator_point_table(
    fit_sector_stress: pd.DataFrame,
    *,
    regulator_safety_factor: float = 1.0,
    regulator_density_floor: float = 1.0e-14,
    type_tolerance: float = 1.0e-12,
) -> pd.DataFrame:
    selected = fit_sector_stress.loc[fit_sector_stress["sector"].astype(str) == J_SECTOR].copy()
    classified = classify_endpoint_source_frame(selected, type_tolerance=type_tolerance)
    classified = _derive_sector_columns(classified)

    rho = classified["sector_rho"].astype(float).to_numpy()
    p_l = classified["sector_p_l"].astype(float).to_numpy()
    j_l = classified["sector_j_l"].astype(float).to_numpy()
    rho_plus_p = rho + p_l
    minimal = classified["minimal_type_i_regulator"].astype(float).to_numpy()
    regulator = minimal * max(float(regulator_safety_factor), 0.0)
    sign = np.where(np.abs(rho_plus_p) > EPS, np.sign(rho_plus_p), 1.0)
    delta_h = sign * regulator
    delta_rho = 0.5 * delta_h
    delta_p_l = 0.5 * delta_h

    regulated = classified.copy()
    regulated["sector_rho"] = rho + delta_rho
    regulated["sector_p_l"] = p_l + delta_p_l
    regulated["sector_j_l"] = j_l
    regulated["sector_p_omega"] = classified["sector_p_omega"].astype(float).to_numpy()
    regulated_classified = classify_endpoint_source_frame(regulated, type_tolerance=type_tolerance)

    out = classified.copy()
    out["minimal_current_regulator"] = minimal
    out["endpoint_current_regulator"] = regulator
    out["regulator_safety_factor"] = float(regulator_safety_factor)
    out["regulator_active"] = regulator > float(regulator_density_floor)
    out["regulator_sign"] = sign
    out["regulator_delta_sector_rho"] = delta_rho
    out["regulator_delta_sector_p_l"] = delta_p_l
    out["regulator_delta_sector_j_l"] = 0.0
    out["regulator_delta_sector_p_omega"] = 0.0
    out["regulated_sector_rho"] = regulated_classified["sector_rho"].astype(float).to_numpy()
    out["regulated_sector_p_l"] = regulated_classified["sector_p_l"].astype(float).to_numpy()
    out["regulated_sector_j_l"] = regulated_classified["sector_j_l"].astype(float).to_numpy()
    out["regulated_sector_p_omega"] = regulated_classified["sector_p_omega"].astype(float).to_numpy()
    out["regulated_rho_plus_p_l"] = regulated_classified["rho_plus_p_l"].astype(float).to_numpy()
    out["regulated_radial_block_discriminant"] = regulated_classified["radial_block_discriminant"].astype(float).to_numpy()
    out["regulated_radial_flux_ratio"] = regulated_classified["radial_flux_ratio"].astype(float).to_numpy()
    out["regulated_stress_algebraic_type"] = regulated_classified["stress_algebraic_type"].astype(str).to_numpy()
    out["regulated_type_i_heat_flux_compatible"] = regulated_classified["type_i_heat_flux_compatible"].astype(bool).to_numpy()
    out["regulated_minimal_type_i_regulator"] = regulated_classified["minimal_type_i_regulator"].astype(float).to_numpy()
    out["regulated_type_i_margin"] = np.abs(out["regulated_rho_plus_p_l"].astype(float).to_numpy()) - 2.0 * np.abs(j_l)
    out["regulator_abs_volume"] = out["endpoint_current_regulator"].astype(float) * out["volume_weight"].astype(float)
    out["regulator_pair_delta_abs_density"] = np.abs(delta_rho) + np.abs(delta_p_l)
    out["regulator_pair_delta_abs_volume"] = out["regulator_pair_delta_abs_density"].astype(float) * out["volume_weight"].astype(float)
    out["regulator_to_local_source_abs_density"] = out["endpoint_current_regulator"].astype(float) / (
        out["source_abs_density"].astype(float) + EPS
    )
    return out


def build_current_regulator_layer_frame(points: pd.DataFrame) -> pd.DataFrame:
    out = points.copy()
    out["sector_description"] = "Endpoint current-regulator constitutive layer."
    out["sector_rho"] = out["regulator_delta_sector_rho"].astype(float)
    out["sector_p_l"] = out["regulator_delta_sector_p_l"].astype(float)
    out["sector_j_l"] = out["regulator_delta_sector_j_l"].astype(float)
    out["sector_p_omega"] = out["regulator_delta_sector_p_omega"].astype(float)
    return _derive_sector_columns(out)


def build_regulated_current_medium_frame(points: pd.DataFrame) -> pd.DataFrame:
    out = points.copy()
    out["sector_description"] = "Frozen endpoint-J source with endpoint current regulator applied."
    out["sector_rho"] = out["regulated_sector_rho"].astype(float)
    out["sector_p_l"] = out["regulated_sector_p_l"].astype(float)
    out["sector_j_l"] = out["regulated_sector_j_l"].astype(float)
    out["sector_p_omega"] = out["regulated_sector_p_omega"].astype(float)
    return _derive_sector_columns(out)


def _summarize_scope(
    scope: str,
    frame: pd.DataFrame,
    *,
    regulator_source_ratio_gate: float,
    support_effective_volume_fraction_gate: float,
    top_1pct_burden_share_gate: float,
    regulator_density_floor: float,
) -> dict[str, Any]:
    if frame.empty:
        return {
            "scope": scope,
            "rows": 0,
            "regulator_budget_pass": False,
            "finite_support_pass": False,
        }

    live = _bool_series(frame["inside_packet_live"]) if "inside_packet_live" in frame else pd.Series(False, index=frame.index)
    active = frame["endpoint_current_regulator"].astype(float) > float(regulator_density_floor)
    volume = frame["volume_weight"].astype(float).to_numpy()
    regulator_density = frame["endpoint_current_regulator"].astype(float).to_numpy()
    regulator_volume = frame["regulator_abs_volume"].astype(float).to_numpy()
    source_volume = frame["source_abs_volume"].astype(float).to_numpy()
    pair_volume = frame["pair_abs_volume"].astype(float).to_numpy()
    active_volume = float(np.sum(volume[active.to_numpy()]))
    regulator_total = float(np.sum(regulator_volume))
    source_total = float(np.sum(source_volume))
    pair_total = float(np.sum(pair_volume))
    density_l2_volume = float(np.sum(np.square(regulator_density) * volume))
    effective_volume = regulator_total * regulator_total / density_l2_volume if density_l2_volume > 0.0 else float("nan")
    effective_fraction = _safe_ratio(effective_volume, active_volume)
    top_1pct = _top_share(regulator_volume[active.to_numpy()], 0.01)
    finite_support_pass = bool(
        regulator_total <= 0.0
        or (
            _finite(effective_fraction, 0.0) >= float(support_effective_volume_fraction_gate)
            and _finite(top_1pct, 1.0) <= float(top_1pct_burden_share_gate)
        )
    )
    unresolved = frame["regulated_minimal_type_i_regulator"].astype(float) > max(float(regulator_density_floor), 1.0e-12)
    type_iv = frame["regulated_stress_algebraic_type"].astype(str) == "type_iv_flux_dominant"

    return {
        "scope": scope,
        "assignment": "" if scope == "J_total" else str(frame["assignment"].iloc[0]),
        "assignment_scope": "" if scope == "J_total" else ASSIGNMENT_SCOPES.get(str(frame["assignment"].iloc[0]), "other_endpoint"),
        "rows": int(len(frame)),
        "regulator_rows": int(active.sum()),
        "regulator_live_rows": int((active & live).sum()),
        "active_volume": float(np.sum(volume)),
        "regulator_support_volume": active_volume,
        "source_abs_volume": source_total,
        "pair_abs_volume": pair_total,
        "regulator_abs_volume": regulator_total,
        "regulator_live_abs_volume": float(frame.loc[active & live, "regulator_abs_volume"].astype(float).sum()),
        "regulator_to_source_abs_ratio": _safe_ratio(regulator_total, source_total),
        "regulator_to_pair_abs_ratio": _safe_ratio(regulator_total, pair_total),
        "regulator_budget_gate": float(regulator_source_ratio_gate),
        "regulator_budget_pass": bool(_safe_ratio(regulator_total, source_total) <= float(regulator_source_ratio_gate)),
        "peak_regulator_density": float(np.max(regulator_density)) if len(regulator_density) else float("nan"),
        "p99_regulator_density": _quantile(frame["endpoint_current_regulator"], 0.99),
        "mean_regulator_density_on_support": _safe_ratio(regulator_total, active_volume),
        "effective_regulator_volume": effective_volume,
        "effective_regulator_volume_fraction": effective_fraction,
        "support_effective_volume_fraction_gate": float(support_effective_volume_fraction_gate),
        "rows_for_50pct_regulator": _rows_for_fraction(regulator_volume[active.to_numpy()], 0.50),
        "rows_for_80pct_regulator": _rows_for_fraction(regulator_volume[active.to_numpy()], 0.80),
        "top_1pct_regulator_burden_share": top_1pct,
        "top_5pct_regulator_burden_share": _top_share(regulator_volume[active.to_numpy()], 0.05),
        "top_10pct_regulator_burden_share": _top_share(regulator_volume[active.to_numpy()], 0.10),
        "top_1pct_burden_share_gate": float(top_1pct_burden_share_gate),
        "weighted_s_std": _weighted_std(frame["s"].astype(float).to_numpy(), regulator_volume),
        "weighted_l_std": _weighted_std(frame["l"].astype(float).to_numpy(), regulator_volume),
        "weighted_s_width_50pct": _weighted_width(frame["s"].astype(float).to_numpy(), regulator_volume, 0.25, 0.75),
        "weighted_l_width_50pct": _weighted_width(frame["l"].astype(float).to_numpy(), regulator_volume, 0.25, 0.75),
        "weighted_s_width_80pct": _weighted_width(frame["s"].astype(float).to_numpy(), regulator_volume, 0.10, 0.90),
        "weighted_l_width_80pct": _weighted_width(frame["l"].astype(float).to_numpy(), regulator_volume, 0.10, 0.90),
        "finite_support_pass": finite_support_pass,
        "post_regulator_type_iv_rows": int(type_iv.sum()),
        "post_regulator_unresolved_rows": int(unresolved.sum()),
        "post_regulator_peak_remaining_regulator": float(frame["regulated_minimal_type_i_regulator"].astype(float).max())
        if len(frame)
        else float("nan"),
        "delta_current_abs_volume": float(
            np.sum(np.abs(frame["regulator_delta_sector_j_l"].astype(float).to_numpy()) * volume)
        ),
        "delta_pomega_abs_volume": float(
            np.sum(np.abs(frame["regulator_delta_sector_p_omega"].astype(float).to_numpy()) * volume)
        ),
    }


def _assignment_summary(
    points: pd.DataFrame,
    *,
    regulator_source_ratio_gate: float,
    support_effective_volume_fraction_gate: float,
    top_1pct_burden_share_gate: float,
    regulator_density_floor: float,
) -> pd.DataFrame:
    rows = [
        _summarize_scope(
            "J_total",
            points,
            regulator_source_ratio_gate=regulator_source_ratio_gate,
            support_effective_volume_fraction_gate=support_effective_volume_fraction_gate,
            top_1pct_burden_share_gate=top_1pct_burden_share_gate,
            regulator_density_floor=regulator_density_floor,
        )
    ]
    for assignment, group in points.groupby("assignment", sort=False, dropna=False):
        rows.append(
            _summarize_scope(
                str(ASSIGNMENT_SCOPES.get(str(assignment), assignment)),
                group,
                regulator_source_ratio_gate=regulator_source_ratio_gate,
                support_effective_volume_fraction_gate=support_effective_volume_fraction_gate,
                top_1pct_burden_share_gate=top_1pct_burden_share_gate,
                regulator_density_floor=regulator_density_floor,
            )
        )
    return pd.DataFrame(rows)


def _top_regulator_points(points: pd.DataFrame, top_limit: int) -> pd.DataFrame:
    cols = [
        "label",
        "case",
        "assignment",
        "point_index",
        "s",
        "l",
        "stage",
        "region",
        "inside_packet_live",
        "sector_rho",
        "sector_p_l",
        "sector_j_l",
        "sector_p_omega",
        "rho_plus_p_l",
        "radial_block_discriminant",
        "minimal_current_regulator",
        "endpoint_current_regulator",
        "regulator_abs_volume",
        "regulator_to_local_source_abs_density",
        "regulated_rho_plus_p_l",
        "regulated_radial_block_discriminant",
        "regulated_stress_algebraic_type",
    ]
    available = [col for col in cols if col in points.columns]
    return (
        points.sort_values(["regulator_abs_volume", "endpoint_current_regulator"], ascending=[False, False])
        .head(int(top_limit))
        .loc[:, available]
        .reset_index(drop=True)
    )


def _decision_row(
    assignment_summary: pd.DataFrame,
    conservation_summary: pd.DataFrame,
    *,
    source_name: str,
) -> dict[str, Any]:
    total = assignment_summary.loc[assignment_summary["scope"].astype(str) == "J_total"].iloc[0].to_dict()
    layer = conservation_summary.loc[
        (conservation_summary["source_name"].astype(str) == "endpoint_current_regulator_layer")
        & (conservation_summary["scope"].astype(str) == "J_total")
    ]
    regulated = conservation_summary.loc[
        (conservation_summary["source_name"].astype(str) == "regulated_endpoint_current_medium")
        & (conservation_summary["scope"].astype(str) == "J_total")
    ]
    layer_row = layer.iloc[0].to_dict() if not layer.empty else {}
    regulated_row = regulated.iloc[0].to_dict() if not regulated.empty else {}
    layer_read = str(layer_row.get("diagnostic_read", ""))
    regulated_read = str(regulated_row.get("diagnostic_read", ""))
    layer_burden_spread_pass = bool(
        layer_read not in {"fails_non_live_endpoint_gate", "insufficient_derivative_stencil"}
        and _finite(layer_row.get("burden_weighted_mean_conservation_residual_norm"), 0.0) <= 1.0
        and _finite(layer_row.get("peak_conservation_residual_burden_share"), 0.0) <= 0.01
    )
    regulated_total_pass = bool(
        regulated_read
        not in {"fails_non_live_endpoint_gate", "large_conservation_residual_watch", "insufficient_derivative_stencil"}
    )
    conservation_pass = bool(layer_burden_spread_pass and regulated_total_pass)
    zero_live = int(total.get("regulator_live_rows", 0)) == 0
    budget = bool(total.get("regulator_budget_pass", False))
    finite_support = bool(total.get("finite_support_pass", False))
    algebraic = int(total.get("post_regulator_type_iv_rows", 0)) == 0 and int(total.get("post_regulator_unresolved_rows", 0)) == 0
    no_new_angular_or_current = (
        _finite(total.get("delta_current_abs_volume"), 0.0) == 0.0
        and _finite(total.get("delta_pomega_abs_volume"), 0.0) == 0.0
    )
    passes = bool(zero_live and budget and finite_support and algebraic and conservation_pass and no_new_angular_or_current)
    return {
        "source_name": source_name,
        "recommended_next_status": "regulator_constitutive_screen_pass" if passes else "regulator_constitutive_screen_watch",
        "passes_screen": passes,
        "zero_live_rows_pass": zero_live,
        "regulator_budget_pass": budget,
        "finite_support_pass": finite_support,
        "post_regulator_algebraic_pass": algebraic,
        "finite_conservation_spread_pass": conservation_pass,
        "regulator_layer_burden_conservation_pass": layer_burden_spread_pass,
        "regulated_total_conservation_pass": regulated_total_pass,
        "no_new_current_or_angular_component": no_new_angular_or_current,
        "regulator_to_source_abs_ratio": _finite(total.get("regulator_to_source_abs_ratio"), float("nan")),
        "regulator_gate": _finite(total.get("regulator_budget_gate"), float("nan")),
        "regulator_rows": int(total.get("regulator_rows", 0)),
        "regulator_live_rows": int(total.get("regulator_live_rows", 0)),
        "post_regulator_type_iv_rows": int(total.get("post_regulator_type_iv_rows", 0)),
        "post_regulator_unresolved_rows": int(total.get("post_regulator_unresolved_rows", 0)),
        "regulator_layer_conservation_read": layer_read,
        "regulated_total_conservation_read": regulated_read,
        "decision_read": (
            "minimal finite rho+p_l regulator is non-live, within budget, finite-spread, and algebraically closes the radial block"
            if passes
            else "current-regulator construction needs a follow-up before promotion"
        ),
    }


def build_endpoint_current_regulator_tables(
    fit_sector_stress: pd.DataFrame,
    *,
    source_name: str = "endpoint_j_frozen_source",
    regulator_source_ratio_gate: float = 0.06,
    support_effective_volume_fraction_gate: float = 0.01,
    top_1pct_burden_share_gate: float = 0.50,
    regulator_safety_factor: float = 1.0,
    regulator_density_floor: float = 1.0e-14,
    type_tolerance: float = 1.0e-12,
    top_limit: int = 80,
) -> dict[str, pd.DataFrame]:
    points = build_current_regulator_point_table(
        fit_sector_stress,
        regulator_safety_factor=regulator_safety_factor,
        regulator_density_floor=regulator_density_floor,
        type_tolerance=type_tolerance,
    )
    layer = build_current_regulator_layer_frame(points)
    regulated = build_regulated_current_medium_frame(points)
    assignment_summary = _assignment_summary(
        points,
        regulator_source_ratio_gate=regulator_source_ratio_gate,
        support_effective_volume_fraction_gate=support_effective_volume_fraction_gate,
        top_1pct_burden_share_gate=top_1pct_burden_share_gate,
        regulator_density_floor=regulator_density_floor,
    )
    base_conservation = build_endpoint_j_conservation_tables(points, source_name="frozen_endpoint_source", top_limit=top_limit)["summary"]
    layer_conservation = build_endpoint_j_conservation_tables(
        layer,
        source_name="endpoint_current_regulator_layer",
        top_limit=top_limit,
    )["summary"]
    regulated_conservation = build_endpoint_j_conservation_tables(
        regulated,
        source_name="regulated_endpoint_current_medium",
        top_limit=top_limit,
    )["summary"]
    conservation_summary = pd.concat(
        [base_conservation, layer_conservation, regulated_conservation],
        ignore_index=True,
    )
    decision = pd.DataFrame([_decision_row(assignment_summary, conservation_summary, source_name=source_name)])
    return {
        "point_regulator": points,
        "regulator_layer_stress": layer,
        "regulated_medium_stress": regulated,
        "assignment_summary": assignment_summary,
        "conservation_summary": conservation_summary,
        "top_regulator_points": _top_regulator_points(points, top_limit),
        "feasibility_decision": decision,
    }


def _load_fit_sector_stress(fit_dir: Path) -> tuple[pd.DataFrame, dict[str, Any], Path]:
    manifest_path = fit_dir / "endpoint_j_closure_component_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        value = manifest.get("files", {}).get("fit_sector_stress", "endpoint_j_closure_sector_stress.csv")
        path = resolve_manifest_path(fit_dir, value)
        return pd.read_csv(path), manifest, path
    path = fit_dir / "endpoint_j_closure_sector_stress.csv"
    return pd.read_csv(path), {}, path


def build_endpoint_current_regulator_screen(
    fit_dir: Path,
    *,
    source_name: str = "endpoint_j_frozen_source",
    regulator_source_ratio_gate: float = 0.06,
    support_effective_volume_fraction_gate: float = 0.01,
    top_1pct_burden_share_gate: float = 0.50,
    regulator_safety_factor: float = 1.0,
    regulator_density_floor: float = 1.0e-14,
    type_tolerance: float = 1.0e-12,
    top_limit: int = 80,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    fit, manifest, fit_path = _load_fit_sector_stress(fit_dir)
    outputs = build_endpoint_current_regulator_tables(
        fit,
        source_name=source_name,
        regulator_source_ratio_gate=regulator_source_ratio_gate,
        support_effective_volume_fraction_gate=support_effective_volume_fraction_gate,
        top_1pct_burden_share_gate=top_1pct_burden_share_gate,
        regulator_safety_factor=regulator_safety_factor,
        regulator_density_floor=regulator_density_floor,
        type_tolerance=type_tolerance,
        top_limit=top_limit,
    )
    metadata = {
        "fit_dir": str(fit_dir),
        "fit_sector_stress": str(fit_path),
        "fit_sector_stress_sha256": sha256_file(fit_path),
        "source_name": source_name,
        "input_caveat": manifest.get("caveat", ""),
        "regulator_source_ratio_gate": float(regulator_source_ratio_gate),
        "support_effective_volume_fraction_gate": float(support_effective_volume_fraction_gate),
        "top_1pct_burden_share_gate": float(top_1pct_burden_share_gate),
        "regulator_safety_factor": float(regulator_safety_factor),
        "regulator_density_floor": float(regulator_density_floor),
        "type_tolerance": float(type_tolerance),
        "caveat": (
            "Endpoint current-regulator constitutive feasibility screen. The screen keeps "
            "the frozen endpoint-J effective source as input and introduces only the minimal "
            "rho+p_l current-balancing layer needed by the regulated anisotropic heat/current "
            "medium. It is a finite support and conservation-spread screen, not a matter "
            "action or full covariant field-equation proof."
        ),
    }
    return outputs, metadata


def write_endpoint_current_regulator_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "point_regulator": outdir / "endpoint_current_regulator_point_screen.csv",
        "regulator_layer_stress": outdir / "endpoint_current_regulator_layer_stress.csv",
        "regulated_medium_stress": outdir / "endpoint_current_regulator_medium_stress.csv",
        "assignment_summary": outdir / "endpoint_current_regulator_assignment_summary.csv",
        "conservation_summary": outdir / "endpoint_current_regulator_conservation_summary.csv",
        "top_regulator_points": outdir / "endpoint_current_regulator_top_points.csv",
        "feasibility_decision": outdir / "endpoint_current_regulator_feasibility_decision.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "endpoint_current_regulator_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
