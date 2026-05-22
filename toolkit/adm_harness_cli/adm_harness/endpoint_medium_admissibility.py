from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .endpoint_current_regulator import (
    _load_fit_sector_stress,
    build_current_regulator_layer_frame,
    build_current_regulator_point_table,
    build_regulated_current_medium_frame,
)
from .endpoint_j_conservation import ASSIGNMENT_SCOPES, build_endpoint_j_conservation_tables
from .endpoint_j_source_class_screen import classify_endpoint_source_frame
from .source_ledger import sha256_file, write_manifest


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


def _top_share(weights: np.ndarray, row_fraction: float) -> float:
    total = float(np.sum(weights))
    if len(weights) == 0 or total <= 0.0:
        return float("nan")
    count = max(1, int(math.ceil(float(row_fraction) * len(weights))))
    return float(np.sort(weights)[::-1][:count].sum() / total)


def _median_spacing(values: pd.Series) -> float:
    coords = np.array(sorted({_finite(value, float("nan")) for value in values}), dtype=float)
    coords = coords[np.isfinite(coords)]
    if len(coords) < 2:
        return float("nan")
    diffs = np.diff(coords)
    diffs = diffs[diffs > 0.0]
    return float(np.median(diffs)) if len(diffs) else float("nan")


def _axis_derivative(frame: pd.DataFrame, value_col: str, axis_col: str, fixed_col: str) -> pd.Series:
    result = pd.Series(np.nan, index=frame.index, dtype=float)
    for _, group in frame.groupby(fixed_col, sort=False, dropna=False):
        if len(group) < 2:
            continue
        ordered = group.sort_values(axis_col)
        coords = ordered[axis_col].astype(float).to_numpy()
        values = ordered[value_col].astype(float).to_numpy()
        derivatives = np.full(len(ordered), np.nan, dtype=float)
        for idx in range(len(ordered)):
            if idx == 0:
                dx = coords[1] - coords[0]
                if dx != 0.0:
                    derivatives[idx] = (values[1] - values[0]) / dx
            elif idx == len(ordered) - 1:
                dx = coords[-1] - coords[-2]
                if dx != 0.0:
                    derivatives[idx] = (values[-1] - values[-2]) / dx
            else:
                dx = coords[idx + 1] - coords[idx - 1]
                if dx != 0.0:
                    derivatives[idx] = (values[idx + 1] - values[idx - 1]) / dx
        result.loc[ordered.index] = derivatives
    return result


def _add_gradient_columns(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    h_s = _median_spacing(out["s"])
    h_l = _median_spacing(out["l"])
    finite_spacings = [value for value in (h_s, h_l) if math.isfinite(value) and value > 0.0]
    h_ref = min(finite_spacings) if finite_spacings else 1.0
    out["d_s_regulator"] = _axis_derivative(out, "endpoint_current_regulator", "s", "l")
    out["d_l_regulator"] = _axis_derivative(out, "endpoint_current_regulator", "l", "s")
    out["d_s_transport_margin"] = _axis_derivative(out, "transport_margin", "s", "l")
    out["d_l_transport_margin"] = _axis_derivative(out, "transport_margin", "l", "s")
    out["regulator_gradient_cost_density"] = h_ref * np.sqrt(
        np.square(out["d_s_regulator"].fillna(0.0).astype(float))
        + np.square(out["d_l_regulator"].fillna(0.0).astype(float))
    )
    out["transport_margin_gradient_cost_density"] = h_ref * np.sqrt(
        np.square(out["d_s_transport_margin"].fillna(0.0).astype(float))
        + np.square(out["d_l_transport_margin"].fillna(0.0).astype(float))
    )
    volume = out["volume_weight"].astype(float)
    out["regulator_gradient_cost_volume"] = out["regulator_gradient_cost_density"] * volume
    out["transport_margin_gradient_cost_volume"] = out["transport_margin_gradient_cost_density"] * volume
    out["h_s_median"] = h_s
    out["h_l_median"] = h_l
    out["h_ref"] = h_ref
    return out


def build_admissibility_point_table(
    fit_sector_stress: pd.DataFrame,
    *,
    regulator_safety_factor: float,
    regulator_density_floor: float = 1.0e-14,
    type_tolerance: float = 1.0e-12,
) -> pd.DataFrame:
    points = build_current_regulator_point_table(
        fit_sector_stress,
        regulator_safety_factor=float(regulator_safety_factor),
        regulator_density_floor=regulator_density_floor,
        type_tolerance=type_tolerance,
    )
    medium = build_regulated_current_medium_frame(points)
    regulated = classify_endpoint_source_frame(medium, type_tolerance=type_tolerance)
    out = points.copy()
    out["regulated_boost_velocity_to_flux_frame"] = regulated["boost_velocity_to_flux_frame"].astype(float).to_numpy()
    out["regulated_abs_boost_velocity"] = out["regulated_boost_velocity_to_flux_frame"].abs()
    out["regulated_rest_frame_energy_density"] = regulated["rest_frame_energy_density"].astype(float).to_numpy()
    out["regulated_rest_frame_radial_pressure"] = regulated["rest_frame_radial_pressure"].astype(float).to_numpy()
    out["regulated_rest_frame_angular_pressure"] = regulated["rest_frame_angular_pressure"].astype(float).to_numpy()
    out["regulated_heat_flux_ratio"] = out["regulated_radial_flux_ratio"].astype(float)
    out["transport_margin"] = 1.0 - out["regulated_heat_flux_ratio"].astype(float)
    out["enthalpy_buffer_density"] = out["regulated_type_i_margin"].astype(float)
    out["rest_frame_radial_inertia_density"] = (
        out["regulated_rest_frame_energy_density"].astype(float)
        + out["regulated_rest_frame_radial_pressure"].astype(float)
    )
    out["rest_frame_angular_inertia_density"] = (
        out["regulated_rest_frame_energy_density"].astype(float)
        + out["regulated_rest_frame_angular_pressure"].astype(float)
    )
    out["regulator_active"] = out["endpoint_current_regulator"].astype(float) > float(regulator_density_floor)
    out["boost_superluminal_or_nan"] = (
        ~np.isfinite(out["regulated_abs_boost_velocity"].astype(float))
        | (out["regulated_abs_boost_velocity"].astype(float) > 1.0 + 1.0e-10)
    )
    out["boost_luminal_boundary"] = out["regulated_abs_boost_velocity"].astype(float) >= 1.0 - 1.0e-9
    out["radial_inertia_negative"] = out["rest_frame_radial_inertia_density"].astype(float) < -abs(float(type_tolerance))
    out["angular_inertia_negative"] = out["rest_frame_angular_inertia_density"].astype(float) < -abs(float(type_tolerance))
    return _add_gradient_columns(out)


def _conservation_pass(conservation: pd.DataFrame, source_name: str, scope: str) -> tuple[bool, str, float, float]:
    selected = conservation.loc[
        (conservation["source_name"].astype(str) == source_name)
        & (conservation["scope"].astype(str) == scope)
    ]
    if selected.empty:
        return False, "missing_conservation_row", float("nan"), float("nan")
    row = selected.iloc[0]
    read = str(row.get("diagnostic_read", ""))
    burden = _finite(row.get("burden_weighted_mean_conservation_residual_norm"), 0.0)
    peak_share = _finite(row.get("peak_conservation_residual_burden_share"), 0.0)
    hard_fail = {"fails_non_live_endpoint_gate", "large_conservation_residual_watch", "insufficient_derivative_stencil"}
    return bool(read not in hard_fail and burden <= 1.0), read, burden, peak_share


def _scope_summary(
    scope: str,
    frame: pd.DataFrame,
    conservation: pd.DataFrame,
    *,
    regulator_source_ratio_gate: float,
    boundary_gradient_ratio_gate: float,
    transport_p99_gate: float,
    regulator_density_floor: float,
) -> dict[str, Any]:
    live = _bool_series(frame["inside_packet_live"]) if "inside_packet_live" in frame else pd.Series(False, index=frame.index)
    active = frame["endpoint_current_regulator"].astype(float) > float(regulator_density_floor)
    source_volume = frame["source_abs_volume"].astype(float).to_numpy()
    volume = frame["volume_weight"].astype(float).to_numpy()
    regulator_volume = frame["regulator_abs_volume"].astype(float).to_numpy()
    gradient_volume = frame["regulator_gradient_cost_volume"].astype(float).to_numpy()
    source_total = float(np.sum(source_volume))
    regulator_total = float(np.sum(regulator_volume))
    gradient_total = float(np.sum(gradient_volume))
    active_regulator_volume = float(np.sum(volume[active.to_numpy()]))
    density_l2_volume = float(np.sum(np.square(frame["endpoint_current_regulator"].astype(float).to_numpy()) * volume))
    effective_volume = regulator_total * regulator_total / density_l2_volume if density_l2_volume > 0.0 else float("nan")
    effective_fraction = _safe_ratio(effective_volume, active_regulator_volume)
    regulated_pass, regulated_read, regulated_burden_residual, regulated_peak_share = _conservation_pass(
        conservation,
        "regulated_endpoint_current_medium",
        scope,
    )
    layer_pass, layer_read, layer_burden_residual, layer_peak_share = _conservation_pass(
        conservation,
        "endpoint_current_regulator_layer",
        scope,
    )
    if layer_read == "large_conservation_residual_watch" and layer_burden_residual <= 1.0 and layer_peak_share <= 0.01:
        layer_pass = True

    heat_ratio = frame["regulated_heat_flux_ratio"].astype(float)
    type_iv_rows = int((frame["regulated_stress_algebraic_type"].astype(str) == "type_iv_flux_dominant").sum())
    unresolved_rows = int((frame["regulated_minimal_type_i_regulator"].astype(float) > max(regulator_density_floor, 1.0e-12)).sum())
    delta_current = float(np.sum(np.abs(frame["regulator_delta_sector_j_l"].astype(float).to_numpy()) * volume))
    delta_angular = float(np.sum(np.abs(frame["regulator_delta_sector_p_omega"].astype(float).to_numpy()) * volume))
    budget_ratio = _safe_ratio(regulator_total, source_total)
    gradient_ratio = _safe_ratio(gradient_total, source_total)
    p99_heat = _quantile(heat_ratio, 0.99)
    p01_margin = _quantile(frame["transport_margin"], 0.01)

    zero_live = int((active & live).sum()) == 0
    algebraic = type_iv_rows == 0 and unresolved_rows == 0
    boost = int(frame["boost_superluminal_or_nan"].astype(bool).sum()) == 0
    budget = budget_ratio <= regulator_source_ratio_gate
    boundary = gradient_ratio <= boundary_gradient_ratio_gate
    transport = p99_heat <= transport_p99_gate and p01_margin >= -1.0e-10
    finite_support = bool(
        regulator_total <= 0.0
        or (effective_fraction >= 0.01 and _top_share(regulator_volume[active.to_numpy()], 0.01) <= 0.50)
    )
    no_hidden = delta_current == 0.0 and delta_angular == 0.0 and regulated_pass and layer_pass
    hard_pass = bool(zero_live and algebraic and boost and budget and boundary and transport and finite_support and no_hidden)

    return {
        "scope": scope,
        "assignment": "" if scope == "J_total" else str(frame["assignment"].iloc[0]) if len(frame) else "",
        "assignment_scope": "" if scope == "J_total" else ASSIGNMENT_SCOPES.get(str(frame["assignment"].iloc[0]), "other_endpoint"),
        "rows": int(len(frame)),
        "regulator_safety_factor": float(frame["regulator_safety_factor"].iloc[0]) if len(frame) else float("nan"),
        "regulator_rows": int(active.sum()),
        "regulator_live_rows": int((active & live).sum()),
        "regulator_to_source_abs_ratio": budget_ratio,
        "regulator_budget_gate": float(regulator_source_ratio_gate),
        "regulator_budget_pass": budget,
        "boundary_gradient_to_source_ratio": gradient_ratio,
        "boundary_gradient_ratio_gate": float(boundary_gradient_ratio_gate),
        "boundary_gradient_pass": boundary,
        "effective_regulator_volume_fraction": effective_fraction,
        "top_1pct_regulator_burden_share": _top_share(regulator_volume[active.to_numpy()], 0.01),
        "finite_support_pass": finite_support,
        "post_regulator_type_iv_rows": type_iv_rows,
        "post_regulator_unresolved_rows": unresolved_rows,
        "algebraic_closure_pass": algebraic,
        "boost_superluminal_or_nan_rows": int(frame["boost_superluminal_or_nan"].astype(bool).sum()),
        "boost_luminal_boundary_rows": int(frame["boost_luminal_boundary"].astype(bool).sum()),
        "max_abs_boost_velocity": float(frame["regulated_abs_boost_velocity"].astype(float).replace([np.inf], np.nan).max())
        if len(frame)
        else float("nan"),
        "boost_frame_pass": boost,
        "max_heat_flux_ratio": float(heat_ratio.replace([np.inf], np.nan).max()) if len(frame) else float("nan"),
        "p99_heat_flux_ratio": p99_heat,
        "transport_p99_gate": float(transport_p99_gate),
        "p01_transport_margin": p01_margin,
        "transport_margin_pass": transport,
        "radial_inertia_negative_rows": int(frame["radial_inertia_negative"].astype(bool).sum()),
        "angular_inertia_negative_rows": int(frame["angular_inertia_negative"].astype(bool).sum()),
        "regulated_total_conservation_pass": regulated_pass,
        "regulated_total_conservation_read": regulated_read,
        "regulated_total_burden_weighted_residual_norm": regulated_burden_residual,
        "regulated_total_peak_residual_burden_share": regulated_peak_share,
        "regulator_layer_conservation_pass": layer_pass,
        "regulator_layer_conservation_read": layer_read,
        "regulator_layer_burden_weighted_residual_norm": layer_burden_residual,
        "regulator_layer_peak_residual_burden_share": layer_peak_share,
        "delta_current_abs_volume": delta_current,
        "delta_pomega_abs_volume": delta_angular,
        "no_hidden_component_pass": no_hidden,
        "hard_admissibility_pass": hard_pass,
    }


def _scan_one_factor(
    fit_sector_stress: pd.DataFrame,
    *,
    regulator_safety_factor: float,
    regulator_source_ratio_gate: float,
    boundary_gradient_ratio_gate: float,
    transport_p99_gate: float,
    regulator_density_floor: float,
    type_tolerance: float,
    top_limit: int,
) -> dict[str, pd.DataFrame]:
    points = build_admissibility_point_table(
        fit_sector_stress,
        regulator_safety_factor=regulator_safety_factor,
        regulator_density_floor=regulator_density_floor,
        type_tolerance=type_tolerance,
    )
    layer = build_current_regulator_layer_frame(points)
    medium = build_regulated_current_medium_frame(points)
    conservation = pd.concat(
        [
            build_endpoint_j_conservation_tables(layer, source_name="endpoint_current_regulator_layer", top_limit=top_limit)["summary"],
            build_endpoint_j_conservation_tables(medium, source_name="regulated_endpoint_current_medium", top_limit=top_limit)["summary"],
        ],
        ignore_index=True,
    )
    summary_rows = [
        _scope_summary(
            "J_total",
            points,
            conservation,
            regulator_source_ratio_gate=regulator_source_ratio_gate,
            boundary_gradient_ratio_gate=boundary_gradient_ratio_gate,
            transport_p99_gate=transport_p99_gate,
            regulator_density_floor=regulator_density_floor,
        )
    ]
    for assignment, group in points.groupby("assignment", sort=False, dropna=False):
        summary_rows.append(
            _scope_summary(
                str(ASSIGNMENT_SCOPES.get(str(assignment), assignment)),
                group,
                conservation,
                regulator_source_ratio_gate=regulator_source_ratio_gate,
                boundary_gradient_ratio_gate=boundary_gradient_ratio_gate,
                transport_p99_gate=transport_p99_gate,
                regulator_density_floor=regulator_density_floor,
            )
        )
    top = (
        points.sort_values(
            ["regulator_gradient_cost_volume", "regulator_abs_volume", "endpoint_current_regulator"],
            ascending=[False, False, False],
        )
        .head(int(top_limit))
        .reset_index(drop=True)
    )
    return {
        "point_admissibility": points,
        "scope_summary": pd.DataFrame(summary_rows),
        "conservation_summary": conservation,
        "top_boundary_points": top,
    }


def _decision_from_scan(scan: pd.DataFrame, decision_safety_factor: float) -> pd.DataFrame:
    j_total = scan.loc[scan["scope"].astype(str) == "J_total"].copy()
    if j_total.empty:
        return pd.DataFrame([{
            "decision_safety_factor": float(decision_safety_factor),
            "admissibility_status": "missing_j_total_scan",
            "hard_admissibility_pass": False,
        }])
    idx = (j_total["regulator_safety_factor"].astype(float) - float(decision_safety_factor)).abs().idxmin()
    selected = j_total.loc[idx].to_dict()
    hard_pass = bool(selected.get("hard_admissibility_pass", False))
    margin_watches = []
    if int(selected.get("boost_luminal_boundary_rows", 0)) > 0:
        margin_watches.append("luminal_boundary_rows")
    if _finite(selected.get("p99_heat_flux_ratio"), 1.0) > 0.98:
        margin_watches.append("thin_transport_margin")
    if int(selected.get("radial_inertia_negative_rows", 0)) > 0:
        margin_watches.append("negative_radial_inertia_rows")
    if int(selected.get("angular_inertia_negative_rows", 0)) > 0:
        margin_watches.append("negative_angular_inertia_rows")
    return pd.DataFrame([{
        "decision_safety_factor": float(selected.get("regulator_safety_factor", decision_safety_factor)),
        "admissibility_status": "no_hard_obstruction" if hard_pass else "necessary_condition_watch",
        "hard_admissibility_pass": hard_pass,
        "margin_watch_count": len(margin_watches),
        "margin_watches": ";".join(margin_watches),
        "regulator_to_source_abs_ratio": _finite(selected.get("regulator_to_source_abs_ratio"), float("nan")),
        "boundary_gradient_to_source_ratio": _finite(selected.get("boundary_gradient_to_source_ratio"), float("nan")),
        "p99_heat_flux_ratio": _finite(selected.get("p99_heat_flux_ratio"), float("nan")),
        "p01_transport_margin": _finite(selected.get("p01_transport_margin"), float("nan")),
        "max_abs_boost_velocity": _finite(selected.get("max_abs_boost_velocity"), float("nan")),
        "regulator_live_rows": int(selected.get("regulator_live_rows", 0)),
        "post_regulator_type_iv_rows": int(selected.get("post_regulator_type_iv_rows", 0)),
        "boost_superluminal_or_nan_rows": int(selected.get("boost_superluminal_or_nan_rows", 0)),
        "regulated_total_conservation_read": str(selected.get("regulated_total_conservation_read", "")),
        "regulator_layer_conservation_read": str(selected.get("regulator_layer_conservation_read", "")),
        "decision_read": (
            "necessary conditions show no hard obstruction at the selected safety factor"
            if hard_pass
            else "one or more necessary-condition gates require interpretation before constructive field-equation validation"
        ),
    }])


def build_endpoint_medium_admissibility_tables(
    fit_sector_stress: pd.DataFrame,
    *,
    source_name: str = "endpoint_j_frozen_source",
    regulator_safety_factors: list[float] | None = None,
    decision_safety_factor: float = 1.10,
    regulator_source_ratio_gate: float = 0.06,
    boundary_gradient_ratio_gate: float = 0.06,
    transport_p99_gate: float = 0.995,
    regulator_density_floor: float = 1.0e-14,
    type_tolerance: float = 1.0e-12,
    top_limit: int = 80,
) -> dict[str, pd.DataFrame]:
    factors = regulator_safety_factors or [1.0, 1.05, 1.10, 1.25]
    point_frames: list[pd.DataFrame] = []
    scope_frames: list[pd.DataFrame] = []
    conservation_frames: list[pd.DataFrame] = []
    top_frames: list[pd.DataFrame] = []
    for factor in factors:
        outputs = _scan_one_factor(
            fit_sector_stress,
            regulator_safety_factor=float(factor),
            regulator_source_ratio_gate=regulator_source_ratio_gate,
            boundary_gradient_ratio_gate=boundary_gradient_ratio_gate,
            transport_p99_gate=transport_p99_gate,
            regulator_density_floor=regulator_density_floor,
            type_tolerance=type_tolerance,
            top_limit=top_limit,
        )
        for value in outputs.values():
            if "source_name" in value.columns:
                value["screen_source_name"] = source_name
            else:
                value.insert(0, "source_name", source_name)
        point_frames.append(outputs["point_admissibility"])
        scope_frames.append(outputs["scope_summary"])
        conservation_frames.append(outputs["conservation_summary"])
        top_frames.append(outputs["top_boundary_points"])
    scope_summary = pd.concat(scope_frames, ignore_index=True) if scope_frames else pd.DataFrame()
    return {
        "point_admissibility": pd.concat(point_frames, ignore_index=True) if point_frames else pd.DataFrame(),
        "scope_summary": scope_summary,
        "conservation_summary": pd.concat(conservation_frames, ignore_index=True) if conservation_frames else pd.DataFrame(),
        "top_boundary_points": pd.concat(top_frames, ignore_index=True) if top_frames else pd.DataFrame(),
        "feasibility_decision": _decision_from_scan(scope_summary, decision_safety_factor),
    }


def build_endpoint_medium_admissibility_audit(
    fit_dir: Path,
    *,
    source_name: str = "endpoint_j_frozen_source",
    regulator_safety_factors: list[float] | None = None,
    decision_safety_factor: float = 1.10,
    regulator_source_ratio_gate: float = 0.06,
    boundary_gradient_ratio_gate: float = 0.06,
    transport_p99_gate: float = 0.995,
    regulator_density_floor: float = 1.0e-14,
    type_tolerance: float = 1.0e-12,
    top_limit: int = 80,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    fit, manifest, fit_path = _load_fit_sector_stress(fit_dir)
    outputs = build_endpoint_medium_admissibility_tables(
        fit,
        source_name=source_name,
        regulator_safety_factors=regulator_safety_factors,
        decision_safety_factor=decision_safety_factor,
        regulator_source_ratio_gate=regulator_source_ratio_gate,
        boundary_gradient_ratio_gate=boundary_gradient_ratio_gate,
        transport_p99_gate=transport_p99_gate,
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
        "regulator_safety_factors": regulator_safety_factors or [1.0, 1.05, 1.10, 1.25],
        "decision_safety_factor": float(decision_safety_factor),
        "regulator_source_ratio_gate": float(regulator_source_ratio_gate),
        "boundary_gradient_ratio_gate": float(boundary_gradient_ratio_gate),
        "transport_p99_gate": float(transport_p99_gate),
        "regulator_density_floor": float(regulator_density_floor),
        "type_tolerance": float(type_tolerance),
        "caveat": (
            "Necessary-condition audit for the regulated anisotropic heat/current medium. "
            "This is an admissibility screen before constructive field-equation validation; "
            "it does not prove a matter action or full physical viability."
        ),
    }
    return outputs, metadata


def write_endpoint_medium_admissibility_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "point_admissibility": outdir / "endpoint_medium_admissibility_point_screen.csv",
        "scope_summary": outdir / "endpoint_medium_admissibility_scope_summary.csv",
        "conservation_summary": outdir / "endpoint_medium_admissibility_conservation_summary.csv",
        "top_boundary_points": outdir / "endpoint_medium_admissibility_top_boundary_points.csv",
        "feasibility_decision": outdir / "endpoint_medium_admissibility_decision.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "endpoint_medium_admissibility_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
