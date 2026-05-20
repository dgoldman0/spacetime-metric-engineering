from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .source_ledger import sha256_file, write_manifest
from .source_screening import resolve_manifest_path


BRANCH_SIGNS = {
    "plus": -1.0,
    "minus": 1.0,
}

SECTOR_ORDER = [
    "S0_constant_flux_string_cloud",
    "J_endpoint_junction_layer",
    "core_body_residual_leakage",
]


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


def _load_string_residuals(string_cloud_dir: Path) -> tuple[pd.DataFrame, dict[str, Any], Path]:
    manifest_path = string_cloud_dir / "radial_string_cloud_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    value = manifest.get("files", {}).get("point_residuals", "radial_string_cloud_point_residuals.csv")
    point_path = resolve_manifest_path(string_cloud_dir, value)
    return pd.read_csv(point_path), manifest, point_path


def _load_component_detail(component_dir: Path) -> tuple[pd.DataFrame, dict[str, Any], Path]:
    manifest_path = component_dir / "component_source_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    value = manifest.get("files", {}).get("detail", "component_source_assignment_detail.csv")
    detail_path = resolve_manifest_path(component_dir, value)
    return pd.read_csv(detail_path), manifest, detail_path


def _sector_description(sector: str) -> str:
    return {
        "S0_constant_flux_string_cloud": "Constant areal-flux radial string cloud: rho=Phi/gamma_omega, p_l=-rho.",
        "J_endpoint_junction_layer": (
            "Coupled non-live endpoint/junction layer carrying shoulder/reset radial trim, "
            "current relaxation, and angular endpoint capacity together."
        ),
        "core_body_residual_leakage": "Small residual left in the clean core body after S0 subtraction.",
    }.get(sector, "")


def _sector_rows_for_point(row: pd.Series) -> list[dict[str, Any]]:
    base = {
        "label": row.get("label", ""),
        "case": row.get("case", ""),
        "point_index": int(row.get("point_index", 0)),
        "s": _finite(row.get("s")),
        "l": _finite(row.get("l")),
        "stage": row.get("stage", ""),
        "region": row.get("region", ""),
        "inside_packet_live": bool(row.get("inside_packet_live", False)),
        "inside_packet_geom": bool(row.get("inside_packet_geom", False)),
        "residual_zone": row.get("residual_zone", ""),
        "volume_weight": _finite(row.get("volume_weight"), 1.0),
    }
    zone = str(row.get("residual_zone", ""))
    items: list[tuple[str, str, float, float, float, float]] = [
        (
            "S0_constant_flux_string_cloud",
            "constant_flux_body",
            _finite(row.get("string_cloud_rho")),
            _finite(row.get("string_cloud_p_l")),
            0.0,
            0.0,
        )
    ]
    residual_rho = _finite(row.get("residual_rho"))
    residual_p_l = _finite(row.get("residual_p_l"))
    residual_j_l = _finite(row.get("residual_j_l"))
    residual_p_omega = _finite(row.get("residual_p_omega"))
    if zone == "support_edge_shoulder":
        items.append((
            "J_endpoint_junction_layer",
            "support_edge_endpoint_junction",
            residual_rho,
            residual_p_l,
            residual_j_l,
            residual_p_omega,
        ))
    elif zone == "reset_cap":
        items.append((
            "J_endpoint_junction_layer",
            "reset_decompression_endpoint_junction",
            residual_rho,
            residual_p_l,
            residual_j_l,
            residual_p_omega,
        ))
    else:
        items.append((
            "core_body_residual_leakage",
            "core_body_after_string_cloud_residual",
            residual_rho,
            residual_p_l,
            residual_j_l,
            residual_p_omega,
        ))

    rows: list[dict[str, Any]] = []
    for sector, assignment, rho, p_l, j_l, p_omega in items:
        out = dict(base)
        out.update({
            "sector": sector,
            "sector_description": _sector_description(sector),
            "assignment": assignment,
            "sector_rho": float(rho),
            "sector_p_l": float(p_l),
            "sector_j_l": float(j_l),
            "sector_p_omega": float(p_omega),
        })
        for branch, sign in BRANCH_SIGNS.items():
            out[f"sector_Tkk_{branch}"] = float(rho + p_l + sign * 2.0 * j_l)
        out["sector_selected_null_margin"] = float(rho + p_l - 2.0 * abs(j_l))
        out["sector_selected_null_deficit_density"] = max(-out["sector_selected_null_margin"], 0.0)
        out["sector_pair_l1_density"] = abs(float(rho)) + abs(float(p_l))
        out["sector_abs_current_density"] = abs(float(j_l))
        out["sector_abs_pomega_density"] = abs(float(p_omega))
        volume = out["volume_weight"]
        for col in [
            "sector_selected_null_deficit_density",
            "sector_pair_l1_density",
            "sector_abs_current_density",
            "sector_abs_pomega_density",
        ]:
            out[f"{col}_volume"] = out[col] * volume
        rows.append(out)
    return rows


def build_point_sector_stress(points: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in points.iterrows():
        rows.extend(_sector_rows_for_point(row))
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["label", "point_index", "sector"]).reset_index(drop=True)


def _sector_summary(sectors: pd.DataFrame) -> pd.DataFrame:
    if sectors.empty:
        return pd.DataFrame()
    grouped = (
        sectors.groupby(["sector", "assignment"], dropna=False)
        .agg(
            rows=("sector", "count"),
            points=("point_index", "nunique"),
            live_points=("inside_packet_live", "sum"),
            pair_l1=("sector_pair_l1_density_volume", "sum"),
            selected_null_deficit=("sector_selected_null_deficit_density_volume", "sum"),
            abs_current=("sector_abs_current_density_volume", "sum"),
            abs_pomega=("sector_abs_pomega_density_volume", "sum"),
            rho_mean=("sector_rho", "mean"),
            p_l_mean=("sector_p_l", "mean"),
        )
        .reset_index()
    )
    grouped["live_fraction"] = np.where(grouped["points"] > 0, grouped["live_points"] / grouped["points"], np.nan)
    return grouped.sort_values(["sector", "assignment"])


def _zone_sector_summary(sectors: pd.DataFrame) -> pd.DataFrame:
    if sectors.empty:
        return pd.DataFrame()
    grouped = (
        sectors.groupby(["residual_zone", "sector"], dropna=False)
        .agg(
            rows=("sector", "count"),
            points=("point_index", "nunique"),
            pair_l1=("sector_pair_l1_density_volume", "sum"),
            selected_null_deficit=("sector_selected_null_deficit_density_volume", "sum"),
            abs_current=("sector_abs_current_density_volume", "sum"),
            abs_pomega=("sector_abs_pomega_density_volume", "sum"),
        )
        .reset_index()
    )
    return grouped.sort_values(["residual_zone", "sector"])


def _closure_summary(points: pd.DataFrame, sectors: pd.DataFrame) -> pd.DataFrame:
    if points.empty or sectors.empty:
        return pd.DataFrame()
    sector_sum = (
        sectors.groupby(["label", "point_index"], dropna=False)
        .agg(
            model_rho=("sector_rho", "sum"),
            model_p_l=("sector_p_l", "sum"),
            model_j_l=("sector_j_l", "sum"),
            model_p_omega=("sector_p_omega", "sum"),
        )
        .reset_index()
    )
    target_cols = [
        "label",
        "point_index",
        "rho_euler",
        "p_l_unit",
        "j_l_unit",
        "p_omega_unit",
        "inside_packet_live",
        "volume_weight",
    ]
    joined = points[target_cols].merge(sector_sum, on=["label", "point_index"], how="left")
    joined["rho_error"] = joined["rho_euler"].astype(float) - joined["model_rho"].astype(float)
    joined["p_l_error"] = joined["p_l_unit"].astype(float) - joined["model_p_l"].astype(float)
    joined["j_l_error"] = joined["j_l_unit"].astype(float) - joined["model_j_l"].astype(float)
    joined["p_omega_error"] = joined["p_omega_unit"].astype(float) - joined["model_p_omega"].astype(float)
    volume = joined["volume_weight"].astype(float)
    live = _bool_series(joined["inside_packet_live"])
    total_pair_norm = float(((joined["rho_euler"].abs() + joined["p_l_unit"].abs()) * volume).sum())
    total_error = float((
        joined["rho_error"].abs()
        + joined["p_l_error"].abs()
        + joined["j_l_error"].abs()
        + joined["p_omega_error"].abs()
    ).mul(volume).sum())
    return pd.DataFrame([{
        "points": int(len(joined)),
        "live_points": int(live.sum()),
        "model_rows": int(len(sectors)),
        "weighted_total_abs_error": total_error,
        "weighted_total_abs_error_per_pair_norm": _safe_ratio(total_error, total_pair_norm),
        "max_abs_rho_error": float(joined["rho_error"].abs().max()),
        "max_abs_p_l_error": float(joined["p_l_error"].abs().max()),
        "max_abs_j_l_error": float(joined["j_l_error"].abs().max()),
        "max_abs_p_omega_error": float(joined["p_omega_error"].abs().max()),
        "live_model_pair_l1": float(sectors.loc[_bool_series(sectors["inside_packet_live"]), "sector_pair_l1_density_volume"].sum()),
        "live_model_selected_null_deficit": float(
            sectors.loc[_bool_series(sectors["inside_packet_live"]), "sector_selected_null_deficit_density_volume"].sum()
        ),
    }])


def _live_gate_summary(sectors: pd.DataFrame) -> pd.DataFrame:
    if sectors.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for sector, group in sectors.groupby("sector", sort=False):
        live = _bool_series(group["inside_packet_live"])
        total_pair = _sum(group, "sector_pair_l1_density_volume")
        live_pair = _sum(group.loc[live], "sector_pair_l1_density_volume")
        total_deficit = _sum(group, "sector_selected_null_deficit_density_volume")
        live_deficit = _sum(group.loc[live], "sector_selected_null_deficit_density_volume")
        rows.append({
            "sector": str(sector),
            "points": int(group["point_index"].nunique()),
            "live_rows": int(live.sum()),
            "pair_l1": total_pair,
            "live_pair_l1": live_pair,
            "live_pair_fraction": _safe_ratio(live_pair, total_pair),
            "selected_null_deficit": total_deficit,
            "live_selected_null_deficit": live_deficit,
            "live_selected_null_fraction": _safe_ratio(live_deficit, total_deficit),
            "passes_live_gate": bool(live_pair == 0.0 and live_deficit == 0.0),
        })
    return pd.DataFrame(rows).sort_values("sector")


def _component_context(detail: pd.DataFrame) -> pd.DataFrame:
    if detail.empty:
        return pd.DataFrame()
    live = _bool_series(detail["inside_packet_live"])
    role_map = {
        "C_live_handoff_angular_current": "CEF_live_handoff_trim",
        "E_live_handoff_radial_null_trim": "CEF_live_handoff_trim",
        "F_live_handoff_radial_pressure_trim": "CEF_live_handoff_trim",
        "G_infrastructure_angular_capacity": "G_component_ledger",
        "D_reset_support_edge_current_sink": "DH_component_ledger",
    }
    frame = detail.copy()
    frame["intermediate_role"] = frame["component"].map(role_map).fillna("")
    frame = frame.loc[frame["intermediate_role"].astype(str).ne("")]
    if frame.empty:
        return pd.DataFrame()
    return (
        frame.groupby(["intermediate_role", "component", "channel"], dropna=False)
        .agg(
            rows=("component", "count"),
            burden=("demand_volume_burden", "sum"),
            live_burden=("demand_volume_burden", lambda values: float(values[live.loc[values.index]].sum())),
        )
        .reset_index()
        .sort_values(["intermediate_role", "component", "channel"])
    )


def build_intermediate_source_model(
    component_dir: Path,
    string_cloud_dir: Path,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    points, string_manifest, point_residuals_path = _load_string_residuals(string_cloud_dir)
    detail, component_manifest, detail_path = _load_component_detail(component_dir)
    sectors = build_point_sector_stress(points)
    outputs = {
        "point_sector_stress": sectors,
        "sector_summary": _sector_summary(sectors),
        "zone_sector_summary": _zone_sector_summary(sectors),
        "closure_summary": _closure_summary(points, sectors),
        "live_gate_summary": _live_gate_summary(sectors),
        "component_context": _component_context(detail),
    }
    metadata = {
        "component_dir": component_dir,
        "component_manifest": component_manifest,
        "component_detail_path": detail_path,
        "string_cloud_dir": string_cloud_dir,
        "string_manifest": string_manifest,
        "point_residuals_path": point_residuals_path,
    }
    return outputs, metadata


def write_intermediate_source_model_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "point_sector_stress": outdir / "intermediate_source_point_sector_stress.csv",
        "sector_summary": outdir / "intermediate_source_sector_summary.csv",
        "zone_sector_summary": outdir / "intermediate_source_zone_sector_summary.csv",
        "closure_summary": outdir / "intermediate_source_closure_summary.csv",
        "live_gate_summary": outdir / "intermediate_source_live_gate_summary.csv",
        "component_context": outdir / "intermediate_source_component_context.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "intermediate_source_model_manifest.json"
    manifest = {
        "model": "S0_string_cloud_plus_coupled_endpoint_junction",
        "caveat": (
            "Intermediate demanded-source replacement ledger. Sector rows exactly "
            "reconstruct the A/B/I point stress after string-cloud subtraction. The "
            "endpoint/junction sector couples radial trim, angular capacity, and current "
            "relaxation diagnostically, but "
            "they are not a conservation proof or physical matter solve."
        ),
        "sectors": SECTOR_ORDER,
        "component_source_dir": str(metadata["component_dir"]),
        "component_detail": str(metadata["component_detail_path"]),
        "component_detail_sha256": sha256_file(Path(metadata["component_detail_path"])),
        "string_cloud_dir": str(metadata["string_cloud_dir"]),
        "point_residuals": str(metadata["point_residuals_path"]),
        "point_residuals_sha256": sha256_file(Path(metadata["point_residuals_path"])),
        "files": {key: str(path) for key, path in paths.items()},
        "rows": {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths},
        "sha256": {key: sha256_file(path) for key, path in paths.items()},
    }
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
