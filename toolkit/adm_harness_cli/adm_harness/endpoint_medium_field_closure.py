from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .endpoint_current_regulator import (
    _derive_sector_columns,
    _load_fit_sector_stress,
    build_regulated_current_medium_frame,
)
from .endpoint_j_conservation import ASSIGNMENT_SCOPES, build_endpoint_j_conservation_tables
from .endpoint_medium_admissibility import (
    _axis_derivative,
    _bool_series,
    _finite,
    _median_spacing,
    _quantile,
    _safe_ratio,
)
from .endpoint_medium_constructive_probe import build_constructive_medium_probe_tables
from .source_ledger import sha256_file, write_manifest


FIELD_MEDIUM_SOURCE = "regulated_endpoint_medium_with_internal_angular_response"
TARGET_MEDIUM_SOURCE = "regulated_endpoint_current_medium_target"
EPS = 1.0e-30


def _assignment_axis_derivative(frame: pd.DataFrame, value_col: str, axis_col: str, fixed_col: str) -> pd.Series:
    result = pd.Series(np.nan, index=frame.index, dtype=float)
    for _, group in frame.groupby("assignment", sort=False, dropna=False):
        result.loc[group.index] = _axis_derivative(group, value_col, axis_col, fixed_col)
    return result


def _add_field_closure_columns(point_fit: pd.DataFrame) -> pd.DataFrame:
    out = point_fit.copy()
    volume = out["volume_weight"].astype(float)
    out["medium_energy_density"] = out["regulated_rest_frame_energy_density"].astype(float)
    out["medium_radial_pressure"] = out["regulated_rest_frame_radial_pressure"].astype(float)
    out["medium_angular_pressure"] = out["fit_angular_pressure"].astype(float)
    out["target_medium_angular_pressure"] = out["target_angular_pressure"].astype(float)
    out["medium_radial_heat_flux_ratio"] = out["regulated_heat_flux_ratio"].astype(float)
    out["medium_transport_margin"] = out["transport_margin"].astype(float)
    out["medium_boost_velocity_to_flux_frame"] = out["regulated_boost_velocity_to_flux_frame"].astype(float)
    out["internal_angular_response_density"] = out["medium_angular_pressure"] - out["medium_radial_pressure"]
    out["angular_closure_residual_density"] = out["medium_angular_pressure"] - out["target_medium_angular_pressure"]
    out["angular_closure_abs_residual_density"] = out["angular_closure_residual_density"].abs()
    out["angular_target_abs_volume"] = out["target_medium_angular_pressure"].abs() * volume
    out["angular_closure_abs_residual_volume"] = out["angular_closure_abs_residual_density"] * volume
    out["radial_heat_current_residual_density"] = (out["medium_radial_heat_flux_ratio"] - 1.0).clip(lower=0.0)
    out["transport_margin_deficit_density"] = (-out["medium_transport_margin"]).clip(lower=0.0)
    out["radial_heat_current_residual_volume"] = out["radial_heat_current_residual_density"] * volume
    out["transport_margin_deficit_volume"] = out["transport_margin_deficit_density"] * volume

    h_s = _median_spacing(out["s"])
    h_l = _median_spacing(out["l"])
    finite_spacings = [value for value in (h_s, h_l) if math.isfinite(value) and value > 0.0]
    h_ref = min(finite_spacings) if finite_spacings else 1.0
    gradient_columns = {
        "internal_angular_response": "internal_angular_response_density",
        "medium_angular_pressure": "medium_angular_pressure",
        "angular_closure_residual": "angular_closure_residual_density",
        "medium_heat_flux_ratio": "medium_radial_heat_flux_ratio",
        "medium_transport_margin": "medium_transport_margin",
    }
    for name, column in gradient_columns.items():
        out[f"d_s_{name}"] = _assignment_axis_derivative(out, column, "s", "l")
        out[f"d_l_{name}"] = _assignment_axis_derivative(out, column, "l", "s")
        out[f"{name}_gradient_cost_density"] = h_ref * np.sqrt(
            np.square(out[f"d_s_{name}"].fillna(0.0).astype(float))
            + np.square(out[f"d_l_{name}"].fillna(0.0).astype(float))
        )
        out[f"{name}_gradient_cost_volume"] = out[f"{name}_gradient_cost_density"] * volume
    out["h_s_median"] = h_s
    out["h_l_median"] = h_l
    out["h_ref"] = h_ref
    return out


def _field_medium_frame(point_validation: pd.DataFrame) -> pd.DataFrame:
    out = build_regulated_current_medium_frame(point_validation)
    out["sector_description"] = "Regulated endpoint medium with internal fitted angular response."
    out["sector_p_omega"] = point_validation["medium_angular_pressure"].astype(float).to_numpy()
    out["field_closure_delta_sector_j_l"] = 0.0
    out["field_closure_angular_residual_density"] = point_validation["angular_closure_residual_density"].astype(float).to_numpy()
    return _derive_sector_columns(out)


def _combined_conservation(point_validation: pd.DataFrame, top_limit: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    target = build_regulated_current_medium_frame(point_validation)
    target_conservation = build_endpoint_j_conservation_tables(
        target,
        source_name=TARGET_MEDIUM_SOURCE,
        top_limit=top_limit,
    )
    field = _field_medium_frame(point_validation)
    field_conservation = build_endpoint_j_conservation_tables(
        field,
        source_name=FIELD_MEDIUM_SOURCE,
        top_limit=top_limit,
    )
    summary = pd.concat(
        [target_conservation["summary"], field_conservation["summary"]],
        ignore_index=True,
    )
    top = field_conservation["top_residuals"].copy()
    if not top.empty:
        top.insert(0, "source_name", FIELD_MEDIUM_SOURCE)
    return summary, top


def _conservation_metrics(conservation: pd.DataFrame, source_name: str, scope: str) -> dict[str, Any]:
    selected = conservation.loc[
        (conservation["source_name"].astype(str) == source_name)
        & (conservation["scope"].astype(str) == scope)
    ]
    if selected.empty:
        return {
            "read": "missing_conservation_row",
            "weighted_mean": float("nan"),
            "burden_weighted_mean": float("nan"),
            "peak_norm": float("nan"),
            "peak_burden_share": float("nan"),
        }
    row = selected.iloc[0]
    return {
        "read": str(row.get("diagnostic_read", "")),
        "weighted_mean": _finite(row.get("weighted_mean_conservation_residual_norm"), float("nan")),
        "burden_weighted_mean": _finite(row.get("burden_weighted_mean_conservation_residual_norm"), float("nan")),
        "peak_norm": _finite(row.get("peak_conservation_residual_norm"), float("nan")),
        "peak_burden_share": _finite(row.get("peak_conservation_residual_burden_share"), float("nan")),
    }


def _conservation_pass(field: dict[str, Any], target: dict[str, Any], delta_gate: float) -> bool:
    hard_reads = {"missing_conservation_row", "fails_non_live_endpoint_gate", "large_conservation_residual_watch"}
    if str(field["read"]) in hard_reads:
        return False
    field_burden = _finite(field["burden_weighted_mean"], 0.0)
    target_burden = _finite(target["burden_weighted_mean"], 0.0)
    return bool(field_burden <= 1.0 and field_burden <= target_burden + float(delta_gate))


def _coefficient_summary(constructive_assignment: pd.DataFrame, assignment: str | None) -> dict[str, float]:
    if constructive_assignment.empty:
        return {
            "normalized_l1_error": float("nan"),
            "angular_watch_normalized_l1_error": float("nan"),
            "max_abs_coefficient": float("nan"),
            "coefficient_l1": float("nan"),
        }
    if assignment is None:
        selected = constructive_assignment
    else:
        selected = constructive_assignment.loc[constructive_assignment["assignment"].astype(str) == assignment]
    if selected.empty:
        return {
            "normalized_l1_error": float("nan"),
            "angular_watch_normalized_l1_error": float("nan"),
            "max_abs_coefficient": float("nan"),
            "coefficient_l1": float("nan"),
        }
    return {
        "normalized_l1_error": float(selected["normalized_l1_error"].astype(float).max()),
        "angular_watch_normalized_l1_error": float(selected["angular_watch_normalized_l1_error"].astype(float).max()),
        "max_abs_coefficient": float(selected["max_abs_coefficient"].astype(float).max()),
        "coefficient_l1": float(selected["coefficient_l1"].astype(float).sum()),
    }


def _scope_rows(point_validation: pd.DataFrame) -> list[tuple[str, str | None, pd.DataFrame]]:
    rows: list[tuple[str, str | None, pd.DataFrame]] = [("J_total", None, point_validation)]
    for assignment, group in point_validation.groupby("assignment", sort=False, dropna=False):
        rows.append((str(ASSIGNMENT_SCOPES.get(str(assignment), assignment)), str(assignment), group))
    return rows


def _scope_summary(
    scope: str,
    assignment: str | None,
    frame: pd.DataFrame,
    constructive_assignment: pd.DataFrame,
    conservation: pd.DataFrame,
    *,
    regulator_source_ratio_gate: float,
    boundary_gradient_ratio_gate: float,
    transport_p99_gate: float,
    angular_residual_source_gate: float,
    angular_watch_l1_gate: float,
    coefficient_gate: float,
    conservation_delta_gate: float,
    regulator_density_floor: float,
) -> dict[str, Any]:
    volume = frame["volume_weight"].astype(float).to_numpy()
    live = _bool_series(frame["inside_packet_live"]) if "inside_packet_live" in frame else pd.Series(False, index=frame.index)
    active = frame["endpoint_current_regulator"].astype(float) > float(regulator_density_floor)
    source_total = float(frame["source_abs_volume"].astype(float).sum())
    regulator_total = float(frame["regulator_abs_volume"].astype(float).sum())
    regulator_gradient_total = float(frame["regulator_gradient_cost_volume"].astype(float).sum())
    angular_target_total = float(frame["angular_target_abs_volume"].astype(float).sum())
    angular_residual_total = float(frame["angular_closure_abs_residual_volume"].astype(float).sum())
    angular_watch = frame["angular_inertia_negative"].astype(bool) if "angular_inertia_negative" in frame else pd.Series(False, index=frame.index)
    angular_watch_target = float(frame.loc[angular_watch, "angular_target_abs_volume"].astype(float).sum())
    angular_watch_residual = float(frame.loc[angular_watch, "angular_closure_abs_residual_volume"].astype(float).sum())
    angular_watch_norm = _safe_ratio(angular_watch_residual, angular_watch_target) if angular_watch_target > 0.0 else 0.0
    coefficient = _coefficient_summary(constructive_assignment, assignment)
    field_conservation = _conservation_metrics(conservation, FIELD_MEDIUM_SOURCE, scope)
    target_conservation = _conservation_metrics(conservation, TARGET_MEDIUM_SOURCE, scope)
    field_burden = _finite(field_conservation["burden_weighted_mean"], 0.0)
    target_burden = _finite(target_conservation["burden_weighted_mean"], 0.0)

    regulator_budget = _safe_ratio(regulator_total, source_total) <= float(regulator_source_ratio_gate)
    boundary = _safe_ratio(regulator_gradient_total, source_total) <= float(boundary_gradient_ratio_gate)
    transport = (
        _quantile(frame["medium_radial_heat_flux_ratio"], 0.99) <= float(transport_p99_gate)
        and _quantile(frame["medium_transport_margin"], 0.01) >= -1.0e-10
        and float(frame["radial_heat_current_residual_volume"].astype(float).sum()) <= 1.0e-12
    )
    finite_propagation = int(frame["boost_superluminal_or_nan"].astype(bool).sum()) == 0
    angular_residual_pass = (
        _safe_ratio(angular_residual_total, source_total) <= float(angular_residual_source_gate)
        and angular_watch_norm <= float(angular_watch_l1_gate)
    )
    coefficient_pass = _finite(coefficient["max_abs_coefficient"], float("inf")) <= float(coefficient_gate)
    hidden_current_pass = (
        float(np.sum(np.abs(frame["regulator_delta_sector_j_l"].astype(float).to_numpy()) * volume)) == 0.0
    )
    conservation_ok = _conservation_pass(field_conservation, target_conservation, conservation_delta_gate)
    no_live = int((active & live).sum()) == 0 and int(live.sum()) == 0
    hard_pass = bool(
        no_live
        and regulator_budget
        and boundary
        and transport
        and finite_propagation
        and angular_residual_pass
        and coefficient_pass
        and hidden_current_pass
        and conservation_ok
    )

    return {
        "scope": scope,
        "assignment": "" if assignment is None else assignment,
        "rows": int(len(frame)),
        "live_rows": int(live.sum()),
        "regulator_rows": int(active.sum()),
        "regulator_live_rows": int((active & live).sum()),
        "source_abs_volume": source_total,
        "regulator_abs_volume": regulator_total,
        "regulator_to_source_abs_ratio": _safe_ratio(regulator_total, source_total),
        "regulator_budget_gate": float(regulator_source_ratio_gate),
        "regulator_budget_pass": regulator_budget,
        "regulator_boundary_gradient_to_source_ratio": _safe_ratio(regulator_gradient_total, source_total),
        "boundary_gradient_ratio_gate": float(boundary_gradient_ratio_gate),
        "boundary_gradient_pass": boundary,
        "angular_target_abs_volume": angular_target_total,
        "angular_closure_residual_abs_volume": angular_residual_total,
        "angular_closure_residual_to_source_ratio": _safe_ratio(angular_residual_total, source_total),
        "angular_residual_source_gate": float(angular_residual_source_gate),
        "normalized_l1_error": _safe_ratio(angular_residual_total, angular_target_total),
        "constructive_normalized_l1_error": coefficient["normalized_l1_error"],
        "angular_watch_rows": int(angular_watch.sum()),
        "angular_watch_normalized_l1_error": angular_watch_norm,
        "constructive_angular_watch_normalized_l1_error": coefficient["angular_watch_normalized_l1_error"],
        "angular_watch_l1_gate": float(angular_watch_l1_gate),
        "angular_residual_pass": angular_residual_pass,
        "max_abs_coefficient": coefficient["max_abs_coefficient"],
        "coefficient_l1": coefficient["coefficient_l1"],
        "coefficient_gate": float(coefficient_gate),
        "coefficient_pass": coefficient_pass,
        "internal_angular_response_gradient_to_source_ratio": _safe_ratio(
            float(frame["internal_angular_response_gradient_cost_volume"].astype(float).sum()),
            source_total,
        ),
        "angular_closure_residual_gradient_to_source_ratio": _safe_ratio(
            float(frame["angular_closure_residual_gradient_cost_volume"].astype(float).sum()),
            source_total,
        ),
        "p99_heat_flux_ratio": _quantile(frame["medium_radial_heat_flux_ratio"], 0.99),
        "p01_transport_margin": _quantile(frame["medium_transport_margin"], 0.01),
        "transport_p99_gate": float(transport_p99_gate),
        "transport_margin_pass": transport,
        "max_abs_boost_velocity": float(frame["regulated_abs_boost_velocity"].astype(float).replace([np.inf], np.nan).max())
        if len(frame)
        else float("nan"),
        "boost_superluminal_or_nan_rows": int(frame["boost_superluminal_or_nan"].astype(bool).sum()),
        "finite_propagation_pass": finite_propagation,
        "radial_heat_current_residual_abs_volume": float(frame["radial_heat_current_residual_volume"].astype(float).sum()),
        "transport_margin_deficit_abs_volume": float(frame["transport_margin_deficit_volume"].astype(float).sum()),
        "field_delta_current_abs_volume": float(
            np.sum(np.abs(frame["regulator_delta_sector_j_l"].astype(float).to_numpy()) * volume)
        ),
        "hidden_current_pass": hidden_current_pass,
        "field_conservation_read": field_conservation["read"],
        "target_conservation_read": target_conservation["read"],
        "field_burden_weighted_residual_norm": field_burden,
        "target_burden_weighted_residual_norm": target_burden,
        "conservation_burden_delta": field_burden - target_burden,
        "conservation_delta_gate": float(conservation_delta_gate),
        "field_peak_residual_norm": field_conservation["peak_norm"],
        "field_peak_residual_burden_share": field_conservation["peak_burden_share"],
        "conservation_pass": conservation_ok,
        "field_closure_pass": hard_pass,
    }


def _decision_from_scope_summary(scope_summary: pd.DataFrame) -> pd.DataFrame:
    j_total = scope_summary.loc[scope_summary["scope"].astype(str) == "J_total"]
    if j_total.empty:
        return pd.DataFrame([{
            "field_closure_status": "missing_j_total_scope",
            "passes_constrained_field_closure": False,
        }])
    hard_pass = bool(scope_summary["field_closure_pass"].astype(bool).all())
    total = j_total.iloc[0]
    return pd.DataFrame([{
        "field_closure_status": "constrained_medium_field_closure_pass" if hard_pass else "constrained_medium_field_closure_watch",
        "passes_constrained_field_closure": hard_pass,
        "worst_normalized_l1_error": float(scope_summary["normalized_l1_error"].astype(float).max()),
        "worst_angular_watch_l1_error": float(scope_summary["angular_watch_normalized_l1_error"].astype(float).max()),
        "max_abs_coefficient": float(scope_summary["max_abs_coefficient"].astype(float).max()),
        "max_angular_residual_to_source_ratio": float(scope_summary["angular_closure_residual_to_source_ratio"].astype(float).max()),
        "regulator_to_source_abs_ratio": _finite(total.get("regulator_to_source_abs_ratio"), float("nan")),
        "regulator_boundary_gradient_to_source_ratio": _finite(
            total.get("regulator_boundary_gradient_to_source_ratio"),
            float("nan"),
        ),
        "p99_heat_flux_ratio": _finite(total.get("p99_heat_flux_ratio"), float("nan")),
        "p01_transport_margin": _finite(total.get("p01_transport_margin"), float("nan")),
        "max_abs_boost_velocity": _finite(total.get("max_abs_boost_velocity"), float("nan")),
        "live_rows": int(scope_summary["live_rows"].astype(int).sum()),
        "regulator_live_rows": int(scope_summary["regulator_live_rows"].astype(int).sum()),
        "boost_superluminal_or_nan_rows": int(scope_summary["boost_superluminal_or_nan_rows"].astype(int).sum()),
        "max_conservation_burden_delta": float(scope_summary["conservation_burden_delta"].astype(float).max()),
        "decision_read": (
            "same regulated medium supplies a finite internal angular response with no new component"
            if hard_pass
            else "one or more field-closure gates require interpretation before promotion"
        ),
    }])


def build_endpoint_medium_field_closure_tables(
    fit_sector_stress: pd.DataFrame,
    *,
    source_name: str = "endpoint_j_frozen_source",
    regulator_safety_factor: float = 1.10,
    normalized_l1_gate: float = 0.02,
    angular_watch_l1_gate: float = 0.02,
    coefficient_gate: float = 1.0,
    coefficient_weight: float = 0.02,
    regulator_source_ratio_gate: float = 0.06,
    boundary_gradient_ratio_gate: float = 0.06,
    transport_p99_gate: float = 0.995,
    angular_residual_source_gate: float = 0.01,
    conservation_delta_gate: float = 0.02,
    regulator_density_floor: float = 1.0e-14,
    top_limit: int = 80,
    s_centers: list[int] | None = None,
    l_centers: list[int] | None = None,
    width_multipliers: list[float] | None = None,
    ridges: list[float] | None = None,
) -> dict[str, pd.DataFrame]:
    constructive = build_constructive_medium_probe_tables(
        fit_sector_stress,
        source_name=source_name,
        regulator_safety_factor=regulator_safety_factor,
        normalized_l1_gate=normalized_l1_gate,
        angular_watch_l1_gate=angular_watch_l1_gate,
        coefficient_gate=coefficient_gate,
        coefficient_weight=coefficient_weight,
        s_centers=s_centers,
        l_centers=l_centers,
        width_multipliers=width_multipliers,
        ridges=ridges,
    )
    point_validation = _add_field_closure_columns(constructive["point_fit"])
    conservation_summary, top_field_residuals = _combined_conservation(point_validation, top_limit)
    summary_rows = [
        _scope_summary(
            scope,
            assignment,
            frame,
            constructive["assignment_summary"],
            conservation_summary,
            regulator_source_ratio_gate=regulator_source_ratio_gate,
            boundary_gradient_ratio_gate=boundary_gradient_ratio_gate,
            transport_p99_gate=transport_p99_gate,
            angular_residual_source_gate=angular_residual_source_gate,
            angular_watch_l1_gate=angular_watch_l1_gate,
            coefficient_gate=coefficient_gate,
            conservation_delta_gate=conservation_delta_gate,
            regulator_density_floor=regulator_density_floor,
        )
        for scope, assignment, frame in _scope_rows(point_validation)
    ]
    scope_summary = pd.DataFrame(summary_rows)
    return {
        "point_validation": point_validation,
        "scope_summary": scope_summary,
        "conservation_summary": conservation_summary,
        "top_field_residuals": top_field_residuals,
        "coefficients": constructive["coefficients"],
        "constructive_candidate_scan": constructive["candidate_scan"],
        "feasibility_decision": _decision_from_scope_summary(scope_summary),
    }


def build_endpoint_medium_field_closure_validation(
    fit_dir: Path,
    *,
    source_name: str = "endpoint_j_frozen_source",
    regulator_safety_factor: float = 1.10,
    normalized_l1_gate: float = 0.02,
    angular_watch_l1_gate: float = 0.02,
    coefficient_gate: float = 1.0,
    coefficient_weight: float = 0.02,
    regulator_source_ratio_gate: float = 0.06,
    boundary_gradient_ratio_gate: float = 0.06,
    transport_p99_gate: float = 0.995,
    angular_residual_source_gate: float = 0.01,
    conservation_delta_gate: float = 0.02,
    regulator_density_floor: float = 1.0e-14,
    top_limit: int = 80,
    s_centers: list[int] | None = None,
    l_centers: list[int] | None = None,
    width_multipliers: list[float] | None = None,
    ridges: list[float] | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    fit, manifest, fit_path = _load_fit_sector_stress(fit_dir)
    outputs = build_endpoint_medium_field_closure_tables(
        fit,
        source_name=source_name,
        regulator_safety_factor=regulator_safety_factor,
        normalized_l1_gate=normalized_l1_gate,
        angular_watch_l1_gate=angular_watch_l1_gate,
        coefficient_gate=coefficient_gate,
        coefficient_weight=coefficient_weight,
        regulator_source_ratio_gate=regulator_source_ratio_gate,
        boundary_gradient_ratio_gate=boundary_gradient_ratio_gate,
        transport_p99_gate=transport_p99_gate,
        angular_residual_source_gate=angular_residual_source_gate,
        conservation_delta_gate=conservation_delta_gate,
        regulator_density_floor=regulator_density_floor,
        top_limit=top_limit,
        s_centers=s_centers,
        l_centers=l_centers,
        width_multipliers=width_multipliers,
        ridges=ridges,
    )
    metadata = {
        "fit_dir": str(fit_dir),
        "fit_sector_stress": str(fit_path),
        "fit_sector_stress_sha256": sha256_file(fit_path),
        "source_name": source_name,
        "input_caveat": manifest.get("caveat", ""),
        "regulator_safety_factor": float(regulator_safety_factor),
        "normalized_l1_gate": float(normalized_l1_gate),
        "angular_watch_l1_gate": float(angular_watch_l1_gate),
        "coefficient_gate": float(coefficient_gate),
        "regulator_source_ratio_gate": float(regulator_source_ratio_gate),
        "boundary_gradient_ratio_gate": float(boundary_gradient_ratio_gate),
        "transport_p99_gate": float(transport_p99_gate),
        "angular_residual_source_gate": float(angular_residual_source_gate),
        "conservation_delta_gate": float(conservation_delta_gate),
        "regulator_density_floor": float(regulator_density_floor),
        "top_limit": int(top_limit),
        "caveat": (
            "Constructive field-closure validation for the regulated endpoint heat/current medium. "
            "The angular pressure is modeled as an internal anisotropic response of the same medium; "
            "this is a finite-difference closure and conservation screen, not a covariant matter-action proof."
        ),
    }
    return outputs, metadata


def write_endpoint_medium_field_closure_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "point_validation": outdir / "endpoint_medium_field_closure_point_validation.csv",
        "scope_summary": outdir / "endpoint_medium_field_closure_scope_summary.csv",
        "conservation_summary": outdir / "endpoint_medium_field_closure_conservation_summary.csv",
        "top_field_residuals": outdir / "endpoint_medium_field_closure_top_residuals.csv",
        "coefficients": outdir / "endpoint_medium_field_closure_coefficients.csv",
        "constructive_candidate_scan": outdir / "endpoint_medium_field_closure_candidate_scan.csv",
        "feasibility_decision": outdir / "endpoint_medium_field_closure_decision.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "endpoint_medium_field_closure_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
