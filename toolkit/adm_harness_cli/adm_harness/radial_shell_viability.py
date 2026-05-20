from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .component_algebra_ledger import _add_algebra_columns
from .source_ledger import sha256_file, write_manifest
from .source_screening import resolve_manifest_path


RADIAL_COMPONENTS = (
    "A_infrastructure_radial_null_support",
    "B_core_radial_pressure_balance",
    "I_support_edge_radial_pressure_balance",
)


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


def _load_detail(component_dir: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    manifest_path = component_dir / "component_source_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    detail_value = manifest.get("files", {}).get("detail", "component_source_assignment_detail.csv")
    detail_path = resolve_manifest_path(component_dir, detail_value)
    return pd.read_csv(detail_path), {
        "manifest_path": manifest_path,
        "manifest": manifest,
        "detail_path": detail_path,
    }


def _radial_point_frame(detail: pd.DataFrame) -> pd.DataFrame:
    radial_rows = detail.loc[detail["component"].isin(RADIAL_COMPONENTS)].copy()
    if radial_rows.empty:
        return pd.DataFrame()
    channel_burden = (
        radial_rows.groupby("point_index")["demand_volume_burden"]
        .sum()
        .rename("radial_channel_burden")
        .reset_index()
    )
    components = (
        radial_rows.groupby("point_index")["component"]
        .agg(lambda values: ",".join(sorted(set(str(value) for value in values))))
        .rename("radial_components")
        .reset_index()
    )
    channels = (
        radial_rows.groupby("point_index")["channel"]
        .agg(lambda values: ",".join(sorted(set(str(value) for value in values))))
        .rename("radial_channels")
        .reset_index()
    )
    point_cols = [
        "label",
        "case",
        "point_index",
        "s",
        "l",
        "stage",
        "region",
        "inside_packet_live",
        "inside_packet_geom",
        "volume_weight",
        "rho_euler",
        "p_l_unit",
        "j_l_unit",
        "p_omega_unit",
        "Tkk_min_radial",
    ]
    point_cols = [col for col in point_cols if col in radial_rows.columns]
    points = radial_rows.sort_values(["point_index", "component"]).drop_duplicates("point_index")[point_cols].copy()
    out = points.merge(channel_burden, on="point_index", how="left")
    out = out.merge(components, on="point_index", how="left")
    out = out.merge(channels, on="point_index", how="left")
    out = _add_algebra_columns(out)
    rho = out["rho_euler"].astype(float)
    p_l = out["p_l_unit"].astype(float)
    j_l = out["j_l_unit"].astype(float)
    p_omega = out["p_omega_unit"].astype(float)
    positive_rho = np.maximum(rho, 0.0)
    radial_tension = np.maximum(-p_l, 0.0)
    scaffold = np.minimum(positive_rho, radial_tension)
    out["string_scaffold_density"] = scaffold
    out["radial_over_tension_density"] = np.maximum(radial_tension - positive_rho, 0.0)
    out["radial_under_tension_density"] = np.maximum(positive_rho - radial_tension, 0.0)
    out["negative_energy_density"] = np.maximum(-rho, 0.0)
    out["selected_null_deficit_density"] = np.maximum(-(rho + p_l - 2.0 * np.abs(j_l)), 0.0)
    out["selected_null_margin_density"] = rho + p_l - 2.0 * np.abs(j_l)
    out["abs_current_density"] = np.abs(j_l)
    out["abs_pomega_density"] = np.abs(p_omega)
    out["abs_rho_density"] = np.abs(rho)
    out["abs_p_l_density"] = np.abs(p_l)
    for col in [
        "string_scaffold_density",
        "radial_over_tension_density",
        "radial_under_tension_density",
        "negative_energy_density",
        "selected_null_deficit_density",
        "abs_current_density",
        "abs_pomega_density",
        "abs_rho_density",
        "abs_p_l_density",
    ]:
        out[f"{col}_volume"] = out[col].astype(float) * out["volume_weight"].astype(float)
    return out


def _sum(frame: pd.DataFrame, column: str) -> float:
    return float(frame[column].sum()) if column in frame.columns else 0.0


def _dominant_location(frame: pd.DataFrame, burden_col: str) -> tuple[str, str, bool, float]:
    if frame.empty or burden_col not in frame.columns:
        return "", "", False, float("nan")
    grouped = (
        frame.groupby(["stage", "region", "inside_packet_live"], dropna=False)[burden_col]
        .sum()
        .sort_values(ascending=False)
    )
    if grouped.empty:
        return "", "", False, float("nan")
    total = float(grouped.sum())
    stage, region, live = grouped.index[0]
    return str(stage), str(region), bool(live), _safe_ratio(float(grouped.iloc[0]), total)


def _summary(points: pd.DataFrame, detail: pd.DataFrame) -> pd.DataFrame:
    if points.empty:
        return pd.DataFrame()
    channel_burden = _sum(points, "radial_channel_burden")
    scaffold = _sum(points, "string_scaffold_density_volume")
    deficit = _sum(points, "selected_null_deficit_density_volume")
    over_tension = _sum(points, "radial_over_tension_density_volume")
    under_tension = _sum(points, "radial_under_tension_density_volume")
    negative_energy = _sum(points, "negative_energy_density_volume")
    current = _sum(points, "abs_current_density_volume")
    pomega = _sum(points, "abs_pomega_density_volume")
    abs_rho = _sum(points, "abs_rho_density_volume")
    abs_pl = _sum(points, "abs_p_l_density_volume")
    live = _bool_series(points["inside_packet_live"])
    def_stage, def_region, def_live, def_fraction = _dominant_location(points, "selected_null_deficit_density_volume")
    scaffold_stage, scaffold_region, scaffold_live, scaffold_fraction = _dominant_location(
        points,
        "string_scaffold_density_volume",
    )
    radial_detail = detail.loc[detail["component"].isin(RADIAL_COMPONENTS)]
    component_burdens = radial_detail.groupby("component")["demand_volume_burden"].sum().to_dict()
    return pd.DataFrame([{
        "radial_components": ",".join(RADIAL_COMPONENTS),
        "support_points": int(len(points)),
        "live_points": int(live.sum()),
        "radial_channel_burden": channel_burden,
        "A_burden": float(component_burdens.get("A_infrastructure_radial_null_support", 0.0)),
        "B_burden": float(component_burdens.get("B_core_radial_pressure_balance", 0.0)),
        "I_burden": float(component_burdens.get("I_support_edge_radial_pressure_balance", 0.0)),
        "integral_abs_rho": abs_rho,
        "integral_abs_p_l": abs_pl,
        "integral_string_scaffold": scaffold,
        "integral_selected_null_deficit": deficit,
        "integral_radial_over_tension": over_tension,
        "integral_radial_under_tension": under_tension,
        "integral_negative_energy": negative_energy,
        "integral_abs_current": current,
        "integral_abs_pomega": pomega,
        "selected_null_deficit_per_scaffold": _safe_ratio(deficit, scaffold),
        "radial_over_tension_per_scaffold": _safe_ratio(over_tension, scaffold),
        "radial_under_tension_per_scaffold": _safe_ratio(under_tension, scaffold),
        "negative_energy_per_scaffold": _safe_ratio(negative_energy, scaffold),
        "abs_current_per_scaffold": _safe_ratio(current, scaffold),
        "abs_pomega_per_scaffold": _safe_ratio(pomega, scaffold),
        "scaffold_per_radial_channel_burden": _safe_ratio(scaffold, channel_burden),
        "selected_null_deficit_per_radial_channel_burden": _safe_ratio(deficit, channel_burden),
        "live_scaffold_fraction": _safe_ratio(_sum(points.loc[live], "string_scaffold_density_volume"), scaffold),
        "live_deficit_fraction": _safe_ratio(_sum(points.loc[live], "selected_null_deficit_density_volume"), deficit),
        "dominant_scaffold_stage": scaffold_stage,
        "dominant_scaffold_region": scaffold_region,
        "dominant_scaffold_live": scaffold_live,
        "dominant_scaffold_fraction": scaffold_fraction,
        "dominant_deficit_stage": def_stage,
        "dominant_deficit_region": def_region,
        "dominant_deficit_live": def_live,
        "dominant_deficit_fraction": def_fraction,
    }])


def _by_location(points: pd.DataFrame) -> pd.DataFrame:
    if points.empty:
        return pd.DataFrame()
    grouped = points.groupby(["stage", "region", "inside_packet_live"], dropna=False)
    rows: list[dict[str, Any]] = []
    for (stage, region, live), group in grouped:
        scaffold = _sum(group, "string_scaffold_density_volume")
        deficit = _sum(group, "selected_null_deficit_density_volume")
        rows.append({
            "stage": str(stage),
            "region": str(region),
            "inside_packet_live": bool(live),
            "support_points": int(len(group)),
            "radial_channel_burden": _sum(group, "radial_channel_burden"),
            "integral_string_scaffold": scaffold,
            "integral_selected_null_deficit": deficit,
            "integral_radial_over_tension": _sum(group, "radial_over_tension_density_volume"),
            "integral_radial_under_tension": _sum(group, "radial_under_tension_density_volume"),
            "integral_negative_energy": _sum(group, "negative_energy_density_volume"),
            "integral_abs_current": _sum(group, "abs_current_density_volume"),
            "integral_abs_pomega": _sum(group, "abs_pomega_density_volume"),
            "selected_null_deficit_per_scaffold": _safe_ratio(deficit, scaffold),
            "s_min": float(group["s"].min()),
            "s_max": float(group["s"].max()),
            "l_min": float(group["l"].min()),
            "l_max": float(group["l"].max()),
        })
    out = pd.DataFrame(rows)
    return out.sort_values(["integral_selected_null_deficit", "integral_string_scaffold"], ascending=[False, False])


def _component_channels(detail: pd.DataFrame) -> pd.DataFrame:
    radial = detail.loc[detail["component"].isin(RADIAL_COMPONENTS)].copy()
    if radial.empty:
        return pd.DataFrame()
    rows = []
    for (component, channel), group in radial.groupby(["component", "channel"], dropna=False):
        burden = float(group["demand_volume_burden"].sum())
        rows.append({
            "component": str(component),
            "channel": str(channel),
            "rows": int(len(group)),
            "demand_burden": burden,
            "live_burden": float(group.loc[_bool_series(group["inside_packet_live"]), "demand_volume_burden"].sum()),
            "weighted_rho_euler": float((group["rho_euler"] * group["demand_volume_burden"]).sum() / burden)
            if burden > 0.0 else float("nan"),
            "weighted_p_l_unit": float((group["p_l_unit"] * group["demand_volume_burden"]).sum() / burden)
            if burden > 0.0 else float("nan"),
            "weighted_j_l_unit": float((group["j_l_unit"] * group["demand_volume_burden"]).sum() / burden)
            if burden > 0.0 else float("nan"),
            "weighted_p_omega_unit": float((group["p_omega_unit"] * group["demand_volume_burden"]).sum() / burden)
            if burden > 0.0 else float("nan"),
        })
    return pd.DataFrame(rows).sort_values(["demand_burden", "component"], ascending=[False, True])


def build_radial_shell_viability(component_dir: Path) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    detail, metadata = _load_detail(component_dir)
    points = _radial_point_frame(detail)
    outputs = {
        "summary": _summary(points, detail),
        "by_location": _by_location(points),
        "point_targets": points,
        "component_channels": _component_channels(detail),
    }
    metadata["component_dir"] = component_dir
    return outputs, metadata


def write_radial_shell_viability_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary": outdir / "radial_shell_viability_summary.csv",
        "by_location": outdir / "radial_shell_viability_by_location.csv",
        "point_targets": outdir / "radial_shell_viability_point_targets.csv",
        "component_channels": outdir / "radial_shell_viability_component_channels.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "radial_shell_viability_manifest.json"
    manifest = {
        "caveat": (
            "A/B/I radial shell decomposition against an ideal NEC-saturating radial string/tension scaffold. "
            "This is a diagnostic target split, not a conservation proof or physical matter-model solve."
        ),
        "component_source_dir": str(metadata["component_dir"]),
        "component_source_manifest": str(metadata["manifest_path"]),
        "component_detail": str(metadata["detail_path"]),
        "component_detail_sha256": sha256_file(metadata["detail_path"]),
        "radial_components": list(RADIAL_COMPONENTS),
        "files": {key: str(path) for key, path in paths.items()},
        "rows": {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths},
        "sha256": {key: sha256_file(path) for key, path in paths.items()},
    }
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
