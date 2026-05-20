from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .source_ledger import sha256_file, write_manifest
from .source_screening import resolve_manifest_path


RESIDUAL_KINDS = {
    "selected_null": "residual_selected_null_deficit_density_volume",
    "radial_pair": "residual_pair_l1_density_volume",
    "current": "residual_abs_current_density_volume",
    "angular": "residual_abs_pomega_density_volume",
}


DESIGN_AXES: dict[str, dict[str, Any]] = {
    "entry_pressure_containment": {
        "owner": "compact handoff entry window / radial pressure preparation",
        "columns": [
            "standing_support_packet_smooth_split_entry_window",
            "standing_support_packet_coupled_entry_window",
        ],
    },
    "compact_catch_bearing": {
        "owner": "compact handoff catch/rematch bearing",
        "columns": [
            "standing_support_packet_smooth_split_catch_window",
            "standing_support_packet_carve_catch_window",
        ],
    },
    "compact_edge_smoothing": {
        "owner": "compact handoff edge smoothing",
        "columns": [
            "standing_support_packet_smooth_split_edge_window",
            "standing_support_packet_smooth_split_guarded_edge_window",
            "standing_support_packet_coupled_edge_window",
            "standing_support_packet_smooth_split_edge_window_slope_abs",
            "standing_support_packet_smooth_split_guarded_edge_window_slope_abs",
        ],
    },
    "radial_support_profile": {
        "owner": "gamma_ll radial support / support-edge bearing",
        "columns": [
            "standing_support_packet_radial_window",
            "standing_support_packet_radial_shoulder_window",
            "standing_support_packet_radial_skirt_window",
            "standing_support_packet_delta_gamma_ll",
            "standing_support_packet_coupled_delta_gamma_ll",
        ],
    },
    "throat_angular_capacity": {
        "owner": "gamma_omega throat-capacity / angular jacket G",
        "columns": [
            "standing_support_packet_smooth_split_angular_window",
            "standing_support_packet_smooth_split_delta_gamma_omega",
            "support_shell_delta_gamma_omega",
            "metric_delta_gamma_omega",
        ],
    },
    "carrying_flow_current": {
        "owner": "beta carrying-flow / D-H current relaxation",
        "columns": [
            "standing_support_packet_smooth_split_current_guard_window",
            "standing_support_packet_delta_beta",
            "support_shell_delta_beta",
            "metric_delta_beta_base",
        ],
    },
    "packet_beta_rematch": {
        "owner": "packet beta-rematch sleeve",
        "columns": [
            "standing_support_packet_beta_rematch_window",
            "standing_support_packet_beta_rematch_window_slope_abs",
            "metric_delta_beta_rematch",
        ],
    },
    "release_choreography": {
        "owner": "release choreography slope",
        "columns": [
            "release_profile_slope_abs",
        ],
    },
    "reset_endpoint_stage": {
        "owner": "reset-decompression endpoint",
        "columns": [
            "reset_decompression_indicator",
        ],
    },
    "support_shell_overlay": {
        "owner": "annular support-shell overlay",
        "columns": [
            "support_shell_window",
            "support_shell_delta_alpha",
            "support_shell_delta_beta",
            "support_shell_delta_gamma_ll",
            "support_shell_delta_gamma_omega",
        ],
    },
}


POINT_CONTEXT_COLUMNS = sorted({
    col
    for axis in DESIGN_AXES.values()
    for col in axis["columns"]
    if not col.startswith("metric_delta_") and not col.endswith("_indicator")
} | {
    "alpha",
    "alpha_base",
    "beta",
    "beta_base",
    "beta_pre_packet_rematch",
    "gamma_ll",
    "gamma_ll_base",
    "gamma_omega",
    "gamma_omega_base",
})


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


def _sum(frame: pd.DataFrame, column: str) -> float:
    return float(frame[column].sum()) if column in frame.columns else 0.0


def _load_manifest(component_dir: Path) -> dict[str, Any]:
    return json.loads((component_dir / "component_source_manifest.json").read_text())


def _load_point_context(component_dir: Path, manifest: dict[str, Any]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for ledger in manifest.get("ledgers", []):
        point_value = ledger.get("point_ledger")
        if not point_value:
            continue
        point_path = resolve_manifest_path(component_dir, point_value)
        if not point_path.exists():
            ledger_dir = Path(str(ledger.get("ledger_dir", "")))
            point_path = resolve_manifest_path(ledger_dir, point_value)
        header = pd.read_csv(point_path, nrows=0).columns
        usecols = [col for col in POINT_CONTEXT_COLUMNS if col in header]
        frame = pd.read_csv(point_path, usecols=usecols)
        frame["point_index"] = np.arange(len(frame), dtype=int)
        frame["label"] = str(ledger.get("label", ""))
        frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _add_derived_context(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    pairs = [
        ("metric_delta_alpha_base", "alpha", "alpha_base"),
        ("metric_delta_beta_base", "beta", "beta_base"),
        ("metric_delta_beta_rematch", "beta", "beta_pre_packet_rematch"),
        ("metric_delta_gamma_ll", "gamma_ll", "gamma_ll_base"),
        ("metric_delta_gamma_omega", "gamma_omega", "gamma_omega_base"),
    ]
    for name, left, right in pairs:
        if left in out.columns and right in out.columns:
            out[name] = (out[left].astype(float) - out[right].astype(float)).abs()
    return out


def _load_string_residuals(string_cloud_dir: Path) -> tuple[pd.DataFrame, dict[str, Any], Path]:
    manifest_path = string_cloud_dir / "radial_string_cloud_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    value = manifest.get("files", {}).get("point_residuals", "radial_string_cloud_point_residuals.csv")
    point_path = resolve_manifest_path(string_cloud_dir, value)
    return pd.read_csv(point_path), manifest, point_path


def _axis_raw_score(frame: pd.DataFrame, axis: str) -> pd.Series:
    cols = [col for col in DESIGN_AXES[axis]["columns"] if col in frame.columns]
    if not cols:
        return pd.Series(np.zeros(len(frame), dtype=float), index=frame.index)
    return frame[cols].astype(float).abs().max(axis=1)


def _scale_score(values: pd.Series) -> tuple[pd.Series, float]:
    finite = values.astype(float).replace([np.inf, -np.inf], np.nan).dropna()
    finite = finite.loc[finite > 0.0]
    if finite.empty:
        return pd.Series(np.zeros(len(values), dtype=float), index=values.index), float("nan")
    scale = float(np.nanpercentile(finite.to_numpy(), 95.0))
    if scale <= 0.0 or not math.isfinite(scale):
        scale = float(finite.max())
    if scale <= 0.0 or not math.isfinite(scale):
        return pd.Series(np.zeros(len(values), dtype=float), index=values.index), float("nan")
    return (values.astype(float) / scale).clip(lower=0.0, upper=1.0), scale


def _add_axis_scores(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    out = frame.copy()
    scales: dict[str, float] = {}
    out["reset_decompression_indicator"] = out["stage"].astype(str).eq("reset_decompression").astype(float)
    for axis in DESIGN_AXES:
        raw = _axis_raw_score(out, axis)
        score, scale = _scale_score(raw)
        out[f"axis_raw::{axis}"] = raw
        out[f"axis_score::{axis}"] = score
        scales[axis] = scale
    return out, scales


def _weighted_mean(frame: pd.DataFrame, column: str, weight_column: str) -> float:
    if frame.empty or column not in frame.columns:
        return float("nan")
    values = frame[column].astype(float).to_numpy()
    weights = frame[weight_column].astype(float).to_numpy()
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0.0)
    if int(mask.sum()) == 0:
        return float("nan")
    return float(np.sum(values[mask] * weights[mask]) / np.sum(weights[mask]))


def _dominant_axis(frame: pd.DataFrame, weight_column: str) -> tuple[str, float]:
    if frame.empty or _sum(frame, weight_column) <= 0.0:
        return "", float("nan")
    values = []
    total_weight = float(frame[weight_column].sum())
    for axis in DESIGN_AXES:
        score_col = f"axis_score::{axis}"
        score_mass = float((frame[weight_column].astype(float) * frame[score_col].astype(float)).sum())
        values.append((axis, score_mass / total_weight))
    return max(values, key=lambda item: item[1])


def _zone_summary(points: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    grouped = points.groupby(["residual_zone", "stage", "region", "inside_packet_live"], dropna=False)
    for (zone, stage, region, live), group in grouped:
        row: dict[str, Any] = {
            "residual_zone": str(zone),
            "stage": str(stage),
            "region": str(region),
            "inside_packet_live": bool(live),
            "points": int(len(group)),
            "selected_null_burden": _sum(group, RESIDUAL_KINDS["selected_null"]),
            "radial_pair_burden": _sum(group, RESIDUAL_KINDS["radial_pair"]),
            "current_burden": _sum(group, RESIDUAL_KINDS["current"]),
            "angular_burden": _sum(group, RESIDUAL_KINDS["angular"]),
        }
        for kind, column in RESIDUAL_KINDS.items():
            axis, value = _dominant_axis(group, column)
            row[f"{kind}_dominant_axis"] = axis
            row[f"{kind}_dominant_axis_mean_score"] = value
        for axis in DESIGN_AXES:
            row[f"axis_score::{axis}"] = float(group[f"axis_score::{axis}"].mean())
        rows.append(row)
    out = pd.DataFrame(rows)
    return out.sort_values(["selected_null_burden", "angular_burden"], ascending=[False, False])


def _axis_summary(points: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (zone, partition), group in points.groupby(["residual_zone", "residual_partition"], dropna=False):
        for kind, burden_col in RESIDUAL_KINDS.items():
            burden = _sum(group, burden_col)
            if burden <= 0.0:
                continue
            for axis, spec in DESIGN_AXES.items():
                rows.append({
                    "residual_zone": str(zone),
                    "residual_partition": str(partition),
                    "residual_kind": kind,
                    "design_axis": axis,
                    "design_owner": spec["owner"],
                    "burden": burden,
                    "weighted_axis_score": _weighted_mean(group, f"axis_score::{axis}", burden_col),
                    "weighted_axis_raw_activity": _weighted_mean(group, f"axis_raw::{axis}", burden_col),
                    "score_mass": float(
                        (
                            group[burden_col].astype(float)
                            * group[f"axis_score::{axis}"].astype(float)
                        ).sum()
                    ),
                })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    total_score_mass = out.groupby(["residual_kind", "design_axis"])["score_mass"].transform("sum")
    out["zone_fraction_of_axis_score_mass"] = np.where(
        total_score_mass > 0.0,
        out["score_mass"] / total_score_mass,
        np.nan,
    )
    return out.sort_values(["residual_kind", "weighted_axis_score", "burden"], ascending=[True, False, False])


def _kind_zone_matrix(points: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for zone, group in points.groupby("residual_zone", dropna=False):
        row: dict[str, Any] = {"residual_zone": str(zone), "points": int(len(group))}
        for kind, col in RESIDUAL_KINDS.items():
            row[f"{kind}_burden"] = _sum(group, col)
        rows.append(row)
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    for kind in RESIDUAL_KINDS:
        total = float(out[f"{kind}_burden"].sum())
        out[f"{kind}_fraction"] = out[f"{kind}_burden"].map(lambda value: _safe_ratio(float(value), total))
    return out.sort_values("selected_null_burden", ascending=False)


def _top_points(points: pd.DataFrame, top_n: int = 80) -> pd.DataFrame:
    keep_cols = [
        "label",
        "point_index",
        "stage",
        "region",
        "residual_zone",
        "s",
        "l",
        *RESIDUAL_KINDS.values(),
        *[f"axis_score::{axis}" for axis in DESIGN_AXES],
    ]
    keep_cols = [col for col in keep_cols if col in points.columns]
    return (
        points.sort_values(RESIDUAL_KINDS["selected_null"], ascending=False)
        .head(int(top_n))[keep_cols]
        .reset_index(drop=True)
    )


def build_endpoint_shoulder_crosswalk(
    component_dir: Path,
    string_cloud_dir: Path,
    *,
    top_n: int = 80,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    residuals, string_manifest, point_residuals_path = _load_string_residuals(string_cloud_dir)
    component_manifest = _load_manifest(component_dir)
    context = _load_point_context(component_dir, component_manifest)
    context = _add_derived_context(context)
    points = residuals.merge(context, on=["label", "point_index"], how="left", suffixes=("", "_context"))
    points, axis_scales = _add_axis_scores(points)
    outputs = {
        "kind_zone_matrix": _kind_zone_matrix(points),
        "zone_summary": _zone_summary(points),
        "axis_summary": _axis_summary(points),
        "point_crosswalk": points,
        "top_points": _top_points(points, top_n=top_n),
    }
    metadata = {
        "component_dir": component_dir,
        "component_manifest": component_manifest,
        "string_cloud_dir": string_cloud_dir,
        "string_manifest": string_manifest,
        "point_residuals_path": point_residuals_path,
        "axis_scales": axis_scales,
        "top_n": int(top_n),
    }
    return outputs, metadata


def write_endpoint_shoulder_crosswalk_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "kind_zone_matrix": outdir / "endpoint_shoulder_kind_zone_matrix.csv",
        "zone_summary": outdir / "endpoint_shoulder_zone_summary.csv",
        "axis_summary": outdir / "endpoint_shoulder_axis_summary.csv",
        "point_crosswalk": outdir / "endpoint_shoulder_point_crosswalk.csv",
        "top_points": outdir / "endpoint_shoulder_top_points.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "endpoint_shoulder_crosswalk_manifest.json"
    manifest = {
        "caveat": (
            "Design-component crosswalk for radial string-cloud residual zones. "
            "Axis scores are normalized diagnostic overlaps with existing metric/service "
            "components; they are not causal attributions or source-family fits."
        ),
        "component_source_dir": str(metadata["component_dir"]),
        "string_cloud_dir": str(metadata["string_cloud_dir"]),
        "point_residuals": str(metadata["point_residuals_path"]),
        "point_residuals_sha256": sha256_file(Path(metadata["point_residuals_path"])),
        "design_axes": {
            axis: {
                "owner": spec["owner"],
                "columns": spec["columns"],
                "normalization_scale": metadata["axis_scales"].get(axis),
            }
            for axis, spec in DESIGN_AXES.items()
        },
        "files": {key: str(path) for key, path in paths.items()},
        "rows": {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths},
        "sha256": {key: sha256_file(path) for key, path in paths.items()},
    }
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
