from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .source_ledger import sha256_file, write_manifest
from .source_screening import resolve_manifest_path


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if not math.isfinite(number):
        return default
    return number


def _weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    v = values.astype(float).to_numpy()
    w = weights.astype(float).to_numpy()
    mask = np.isfinite(v) & np.isfinite(w) & (w > 0.0)
    if int(mask.sum()) == 0:
        return float("nan")
    return float(np.sum(v[mask] * w[mask]) / np.sum(w[mask]))


def _weighted_sign_fraction(values: pd.Series, weights: pd.Series, sign: int) -> float:
    v = values.astype(float).to_numpy()
    w = weights.astype(float).to_numpy()
    mask = np.isfinite(v) & np.isfinite(w) & (w > 0.0)
    if int(mask.sum()) == 0:
        return float("nan")
    if sign > 0:
        selected = v > 0.0
    elif sign < 0:
        selected = v < 0.0
    else:
        selected = v == 0.0
    denom = float(np.sum(w[mask]))
    return float(np.sum(w[mask & selected]) / denom) if denom > 0.0 else float("nan")


def _mode_text(values: pd.Series) -> str:
    if values.empty:
        return ""
    modes = values.astype(str).mode(dropna=False)
    return str(modes.iloc[0]) if not modes.empty else ""


def _load_component_detail(component_dir: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    manifest_path = component_dir / "component_source_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    detail_value = manifest.get("files", {}).get("detail", "component_source_assignment_detail.csv")
    detail_path = resolve_manifest_path(component_dir, detail_value)
    return pd.read_csv(detail_path), {"manifest_path": manifest_path, "manifest": manifest, "detail_path": detail_path}


def _add_algebra_columns(detail: pd.DataFrame) -> pd.DataFrame:
    out = detail.copy()
    out["rho_plus_p_l"] = out["rho_euler"].astype(float) + out["p_l_unit"].astype(float)
    out["two_j_l"] = 2.0 * out["j_l_unit"].astype(float)
    out["rho_plus_p_plus_2j"] = out["rho_plus_p_l"] + out["two_j_l"]
    out["rho_plus_p_minus_2j"] = out["rho_plus_p_l"] - out["two_j_l"]
    out["selected_null_residual"] = out[["rho_plus_p_plus_2j", "rho_plus_p_minus_2j"]].min(axis=1)
    out["selected_null_branch_proxy"] = np.where(
        out["rho_plus_p_plus_2j"] <= out["rho_plus_p_minus_2j"], "plus", "minus"
    )
    denom = (
        out["rho_euler"].abs()
        + out["p_l_unit"].abs()
        + out["two_j_l"].abs()
        + 1.0e-30
    )
    out["null_cancellation_ratio_proxy"] = 1.0 - np.minimum(
        out["rho_plus_p_plus_2j"].abs(),
        out["rho_plus_p_minus_2j"].abs(),
    ) / denom
    out["pressure_cancel_ratio"] = 1.0 - out["rho_plus_p_l"].abs() / (
        out["rho_euler"].abs() + out["p_l_unit"].abs() + 1.0e-30
    )
    out["current_dominance_ratio"] = out["two_j_l"].abs() / (out["rho_plus_p_l"].abs() + 1.0e-30)
    out["angular_dominance_ratio"] = out["p_omega_unit"].abs() / (
        out["rho_euler"].abs() + out["p_l_unit"].abs() + out["j_l_unit"].abs() + 1.0e-30
    )
    return out


def _summarize_component(group: pd.DataFrame) -> dict[str, Any]:
    weights = group["demand_volume_burden"].astype(float)
    idx_peak = weights.idxmax()
    peak = group.loc[idx_peak]
    return {
        "rows": int(len(group)),
        "total_burden": float(weights.sum()),
        "live_burden": float(group.loc[group["inside_packet_live"].astype(bool), "demand_volume_burden"].sum()),
        "live_fraction": float(group.loc[group["inside_packet_live"].astype(bool), "demand_volume_burden"].sum() / weights.sum())
        if float(weights.sum()) > 0.0 else float("nan"),
        "dominant_stage": _mode_text(group["stage"]),
        "dominant_region": _mode_text(group["region"]),
        "peak_stage": str(peak["stage"]),
        "peak_region": str(peak["region"]),
        "peak_s": _finite(peak.get("s")),
        "peak_l": _finite(peak.get("l")),
        "peak_channel": str(peak["channel"]),
        "peak_demand": _finite(peak.get("demand")),
        "peak_volume_burden": _finite(peak.get("demand_volume_burden")),
        "mean_rho_euler": _weighted_mean(group["rho_euler"], weights),
        "mean_p_l": _weighted_mean(group["p_l_unit"], weights),
        "mean_j_l": _weighted_mean(group["j_l_unit"], weights),
        "mean_pOmega": _weighted_mean(group["p_omega_unit"], weights),
        "rho_positive_fraction": _weighted_sign_fraction(group["rho_euler"], weights, +1),
        "p_l_positive_fraction": _weighted_sign_fraction(group["p_l_unit"], weights, +1),
        "j_l_positive_fraction": _weighted_sign_fraction(group["j_l_unit"], weights, +1),
        "pOmega_positive_fraction": _weighted_sign_fraction(group["p_omega_unit"], weights, +1),
        "mean_rho_plus_p_l": _weighted_mean(group["rho_plus_p_l"], weights),
        "mean_two_j_l": _weighted_mean(group["two_j_l"], weights),
        "mean_selected_null_residual": _weighted_mean(group["selected_null_residual"], weights),
        "mean_null_cancellation": _weighted_mean(group["null_cancellation_ratio_proxy"], weights),
        "mean_pressure_cancel": _weighted_mean(group["pressure_cancel_ratio"], weights),
        "mean_current_dominance": _weighted_mean(group["current_dominance_ratio"], weights),
        "mean_angular_dominance": _weighted_mean(group["angular_dominance_ratio"], weights),
        "dominant_null_branch": _mode_text(group["selected_null_branch_proxy"]),
    }


def _component_summary(detail: pd.DataFrame) -> pd.DataFrame:
    assigned = detail.loc[detail["assigned"].astype(bool)].copy()
    rows: list[dict[str, Any]] = []
    for (label, component), group in assigned.groupby(["label", "component"], sort=False):
        rows.append({"label": label, "component": component, **_summarize_component(group)})
    return pd.DataFrame(rows).sort_values(["label", "component"])


def _component_channel_summary(detail: pd.DataFrame) -> pd.DataFrame:
    assigned = detail.loc[detail["assigned"].astype(bool)].copy()
    rows: list[dict[str, Any]] = []
    for (label, component, channel), group in assigned.groupby(["label", "component", "channel"], sort=False):
        rows.append({"label": label, "component": component, "channel": channel, **_summarize_component(group)})
    return pd.DataFrame(rows).sort_values(["label", "component", "channel"])


def _overlap_matrix(detail: pd.DataFrame) -> pd.DataFrame:
    assigned = detail.loc[detail["assigned"].astype(bool)].copy()
    if assigned.empty:
        return pd.DataFrame()
    point_component = (
        assigned.groupby(["label", "point_index", "component"], dropna=False)
        .agg(component_burden=("demand_volume_burden", "sum"))
        .reset_index()
    )
    rows: list[dict[str, Any]] = []
    for label, group in point_component.groupby("label", sort=False):
        by_point = {
            int(point): set(sub["component"].astype(str))
            for point, sub in group.groupby("point_index", sort=False)
        }
        burden_by_point = group.groupby("point_index")["component_burden"].sum().to_dict()
        components = sorted(group["component"].astype(str).unique())
        for left in components:
            left_points = {point for point, comps in by_point.items() if left in comps}
            left_burden = float(group.loc[group["component"] == left, "component_burden"].sum())
            for right in components:
                right_points = {point for point, comps in by_point.items() if right in comps}
                overlap_points = left_points & right_points
                overlap_point_burden = float(sum(burden_by_point[point] for point in overlap_points))
                overlap_component_burden = float(
                    group.loc[
                        (group["component"] == left)
                        & group["point_index"].isin(overlap_points),
                        "component_burden",
                    ].sum()
                )
                rows.append({
                    "label": label,
                    "component": left,
                    "other_component": right,
                    "overlap_points": int(len(overlap_points)),
                    "overlap_point_burden": overlap_point_burden,
                    "overlap_component_burden": overlap_component_burden,
                    "component_burden": left_burden,
                    "overlap_fraction_vs_component_burden": overlap_component_burden / left_burden
                    if left_burden > 0.0 else float("nan"),
                })
    return pd.DataFrame(rows).sort_values(["label", "component", "other_component"])


def _current_residual_summary(detail: pd.DataFrame) -> pd.DataFrame:
    residual = detail.loc[(~detail["assigned"].astype(bool)) & (detail["channel"] == "abs_j_l")].copy()
    if residual.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for keys, group in residual.groupby(["label", "stage", "region", "inside_packet_live"], sort=False):
        label, stage, region, live = keys
        weights = group["demand_volume_burden"].astype(float)
        rows.append({
            "label": label,
            "stage": stage,
            "region": region,
            "inside_packet_live": bool(live),
            "rows": int(len(group)),
            "current_burden": float(weights.sum()),
            "mean_j_l": _weighted_mean(group["j_l_unit"], weights),
            "max_abs_j_l": float(group["j_l_unit"].abs().max()),
            "mean_current_dominance": _weighted_mean(group["current_dominance_ratio"], weights),
        })
    return pd.DataFrame(rows).sort_values(["label", "current_burden"], ascending=[True, False])


def _decision_hints(component_summary: pd.DataFrame, current_residual: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for label in sorted(component_summary["label"].unique()):
        current_rows = current_residual.loc[current_residual["label"] == label] if not current_residual.empty else pd.DataFrame()
        current_burden = float(current_rows["current_burden"].sum()) if not current_rows.empty else 0.0
        top_current = current_rows.iloc[0].to_dict() if not current_rows.empty else {}
        components = component_summary.loc[component_summary["label"] == label]
        live_handoff = components.loc[components["component"].isin([
            "C_live_handoff_angular_current",
            "E_live_handoff_radial_null_trim",
            "F_live_handoff_radial_pressure_trim",
        ])]
        infrastructure = components.loc[components["component"].isin([
            "A_infrastructure_radial_null_support",
            "B_core_radial_pressure_balance",
            "I_support_edge_radial_pressure_balance",
            "G_infrastructure_angular_capacity",
        ])]
        rows.append({
            "label": label,
            "unassigned_current_burden": current_burden,
            "top_current_stage": top_current.get("stage", ""),
            "top_current_region": top_current.get("region", ""),
            "top_current_live": bool(top_current.get("inside_packet_live", False)) if top_current else False,
            "live_handoff_total_burden": float(live_handoff["total_burden"].sum()),
            "infrastructure_total_burden": float(infrastructure["total_burden"].sum()),
            "suggest_add_H": bool(current_burden > 0.0 and top_current),
            "suggest_physical_ansatz_before_snec": True,
            "suggest_snec_ready": False,
            "reason": (
                "Use component signatures to choose a composite source ansatz first; "
                "run hard SNEC after source-sector assumptions are less oracle-like."
            ),
        })
    return pd.DataFrame(rows)


def build_component_algebra_ledger(component_dir: Path) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    detail, metadata = _load_component_detail(component_dir)
    detail = _add_algebra_columns(detail)
    outputs = {
        "component_summary": _component_summary(detail),
        "component_channel_summary": _component_channel_summary(detail),
        "overlap_matrix": _overlap_matrix(detail),
        "current_residual_summary": _current_residual_summary(detail),
    }
    outputs["decision_hints"] = _decision_hints(outputs["component_summary"], outputs["current_residual_summary"])
    return outputs, metadata


def write_component_algebra_outputs(
    outdir: Path,
    component_dir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "component_summary": outdir / "component_algebra_summary.csv",
        "component_channel_summary": outdir / "component_algebra_channel_summary.csv",
        "overlap_matrix": outdir / "component_algebra_overlap_matrix.csv",
        "current_residual_summary": outdir / "component_algebra_current_residual.csv",
        "decision_hints": outdir / "component_algebra_decision_hints.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "component_algebra_manifest.json"
    manifest = {
        "caveat": (
            "Algebra/signature readout of an oracle component-source assignment. "
            "This summarizes demanded ADM signs, cancellation proxies, and overlap; "
            "it is not a physical stress-tensor construction."
        ),
        "component_source_dir": str(component_dir),
        "component_source_manifest": str(metadata["manifest_path"]),
        "component_detail": str(metadata["detail_path"]),
        "component_detail_sha256": sha256_file(metadata["detail_path"]),
        "files": {key: str(path) for key, path in paths.items()},
        "rows": {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths},
        "sha256": {key: sha256_file(path) for key, path in paths.items()},
    }
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
