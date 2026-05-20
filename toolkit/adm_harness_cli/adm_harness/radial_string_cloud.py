from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .radial_shell_viability import build_radial_shell_viability
from .source_ledger import sha256_file, write_manifest


CAP_STAGES = {"reset_decompression"}
CAP_REGIONS = {"core_throat", "support_edge"}


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


def _fit_phi(
    points: pd.DataFrame,
    *,
    mask: pd.Series | None = None,
    weight_column: str = "string_scaffold_density_volume",
) -> float:
    if points.empty or "gamma_omega" not in points.columns:
        return float("nan")
    frame = points if mask is None else points.loc[mask].copy()
    if frame.empty:
        return float("nan")
    flux = frame["best_string_density"].astype(float).to_numpy() * frame["gamma_omega"].astype(float).to_numpy()
    weights = frame[weight_column].astype(float).to_numpy() if weight_column in frame.columns else np.ones(len(frame))
    valid = np.isfinite(flux) & np.isfinite(weights) & (weights > 0.0)
    if int(valid.sum()) == 0:
        return float("nan")
    return float(np.sum(flux[valid] * weights[valid]) / np.sum(weights[valid]))


def _fit_phi_pair_l2(points: pd.DataFrame, *, mask: pd.Series | None = None) -> float:
    if points.empty or "gamma_omega" not in points.columns:
        return float("nan")
    frame = points if mask is None else points.loc[mask].copy()
    if frame.empty:
        return float("nan")
    gamma = frame["gamma_omega"].astype(float).to_numpy()
    volume = frame["volume_weight"].astype(float).to_numpy()
    rho = frame["rho_euler"].astype(float).to_numpy()
    minus_pl = -frame["p_l_unit"].astype(float).to_numpy()
    x = 1.0 / gamma
    valid = (
        np.isfinite(gamma)
        & np.isfinite(volume)
        & np.isfinite(rho)
        & np.isfinite(minus_pl)
        & (gamma > 0.0)
        & (volume > 0.0)
    )
    if int(valid.sum()) == 0:
        return float("nan")
    xv = x[valid]
    wv = volume[valid]
    denom = float(np.sum(2.0 * wv * xv * xv))
    if denom <= 0.0:
        return float("nan")
    numer = float(np.sum(wv * xv * (rho[valid] + minus_pl[valid])))
    return numer / denom


def _cap_mask(points: pd.DataFrame) -> pd.Series:
    return points["stage"].astype(str).isin(CAP_STAGES) & points["region"].astype(str).isin(CAP_REGIONS)


def _residual_zone(points: pd.DataFrame) -> np.ndarray:
    cap = _cap_mask(points)
    region = points["region"].astype(str)
    return np.select(
        [
            cap,
            region.eq("support_edge"),
            region.eq("core_throat"),
        ],
        [
            "reset_cap",
            "support_edge_shoulder",
            "core_cloud_body",
        ],
        default="other_body",
    )


def _add_string_cloud_residuals(points: pd.DataFrame, phi: float) -> pd.DataFrame:
    out = points.copy()
    gamma = out["gamma_omega"].astype(float)
    volume = out["volume_weight"].astype(float)
    rho = out["rho_euler"].astype(float)
    p_l = out["p_l_unit"].astype(float)
    j_l = out["j_l_unit"].astype(float)
    p_omega = out["p_omega_unit"].astype(float)

    out["string_cloud_phi"] = float(phi)
    out["string_cloud_mu"] = float(phi) / gamma
    out["string_cloud_rho"] = out["string_cloud_mu"]
    out["string_cloud_p_l"] = -out["string_cloud_mu"]
    out["string_cloud_j_l"] = 0.0
    out["string_cloud_p_omega"] = 0.0

    out["residual_rho"] = rho - out["string_cloud_mu"]
    out["residual_p_l"] = p_l + out["string_cloud_mu"]
    out["residual_j_l"] = j_l
    out["residual_p_omega"] = p_omega
    out["residual_pair_l1_density"] = out["residual_rho"].abs() + out["residual_p_l"].abs()
    out["residual_radial_sum_density"] = out["residual_rho"] + out["residual_p_l"]
    out["residual_null_plus_density"] = out["residual_radial_sum_density"] - 2.0 * out["residual_j_l"]
    out["residual_null_minus_density"] = out["residual_radial_sum_density"] + 2.0 * out["residual_j_l"]
    out["residual_selected_null_margin_density"] = out["residual_radial_sum_density"] - 2.0 * out["residual_j_l"].abs()
    out["residual_selected_null_deficit_density"] = np.maximum(-out["residual_selected_null_margin_density"], 0.0)
    out["residual_static_null_deficit_density"] = np.maximum(-out["residual_radial_sum_density"], 0.0)
    out["residual_current_selected_deficit_density"] = np.maximum(
        out["residual_selected_null_deficit_density"] - out["residual_static_null_deficit_density"],
        0.0,
    )
    out["residual_abs_current_density"] = out["residual_j_l"].abs()
    out["residual_abs_pomega_density"] = out["residual_p_omega"].abs()
    out["residual_abs_rho_density"] = out["residual_rho"].abs()
    out["residual_abs_p_l_density"] = out["residual_p_l"].abs()
    out["string_cloud_mu_volume"] = out["string_cloud_mu"] * volume

    for col in [
        "residual_pair_l1_density",
        "residual_selected_null_deficit_density",
        "residual_static_null_deficit_density",
        "residual_current_selected_deficit_density",
        "residual_abs_current_density",
        "residual_abs_pomega_density",
        "residual_abs_rho_density",
        "residual_abs_p_l_density",
    ]:
        out[f"{col}_volume"] = out[col].astype(float) * volume

    cap = _cap_mask(out)
    out["residual_partition"] = np.where(cap, "reset_cap", "string_cloud_body")
    out["residual_zone"] = _residual_zone(out)
    out["cap_residual_target"] = np.where(
        cap,
        "cap_endpoint_trim_DH_G",
        "body_shape_residual",
    )
    out["live_residual_leak"] = _bool_series(out["inside_packet_live"])
    return out


def _partition_stats(frame: pd.DataFrame, name: str) -> dict[str, Any]:
    pair_norm = _sum(frame, "integral_abs_rho") + _sum(frame, "integral_abs_p_l")
    if pair_norm == 0.0:
        pair_norm = _sum(frame, "abs_rho_density_volume") + _sum(frame, "abs_p_l_density_volume")
    selected = _sum(frame, "residual_selected_null_deficit_density_volume")
    static = _sum(frame, "residual_static_null_deficit_density_volume")
    current_selected = _sum(frame, "residual_current_selected_deficit_density_volume")
    return {
        f"{name}_points": int(len(frame)),
        f"{name}_string_mu_integral": _sum(frame, "string_cloud_mu_volume"),
        f"{name}_residual_pair_l1": _sum(frame, "residual_pair_l1_density_volume"),
        f"{name}_residual_pair_fraction": _safe_ratio(_sum(frame, "residual_pair_l1_density_volume"), pair_norm),
        f"{name}_selected_null_deficit": selected,
        f"{name}_static_null_deficit": static,
        f"{name}_current_selected_deficit": current_selected,
        f"{name}_current_share_of_selected_deficit": _safe_ratio(current_selected, selected),
        f"{name}_abs_current": _sum(frame, "residual_abs_current_density_volume"),
        f"{name}_abs_pomega": _sum(frame, "residual_abs_pomega_density_volume"),
        f"{name}_abs_rho_residual": _sum(frame, "residual_abs_rho_density_volume"),
        f"{name}_abs_p_l_residual": _sum(frame, "residual_abs_p_l_density_volume"),
    }


def _summary(points: pd.DataFrame, phi: float, body_phi: float, pair_l2_phi: float) -> pd.DataFrame:
    if points.empty:
        return pd.DataFrame()
    live = _bool_series(points["inside_packet_live"])
    cap = points["residual_partition"].astype(str).eq("reset_cap")
    pair_norm = _sum(points, "abs_rho_density_volume") + _sum(points, "abs_p_l_density_volume")
    total_selected = _sum(points, "residual_selected_null_deficit_density_volume")
    row: dict[str, Any] = {
        "support_points": int(len(points)),
        "live_points": int(live.sum()),
        "cap_points": int(cap.sum()),
        "string_cloud_phi": float(phi),
        "body_only_phi": float(body_phi),
        "pair_l2_phi": float(pair_l2_phi),
        "body_phi_relative_delta": _safe_ratio(abs(float(body_phi) - float(phi)), abs(float(phi))),
        "integral_abs_rho": _sum(points, "abs_rho_density_volume"),
        "integral_abs_p_l": _sum(points, "abs_p_l_density_volume"),
        "integral_string_cloud_mu": _sum(points, "string_cloud_mu_volume"),
        "target_pair_norm": pair_norm,
        "residual_pair_l1": _sum(points, "residual_pair_l1_density_volume"),
        "residual_pair_fraction": _safe_ratio(_sum(points, "residual_pair_l1_density_volume"), pair_norm),
        "selected_null_deficit": total_selected,
        "static_null_deficit": _sum(points, "residual_static_null_deficit_density_volume"),
        "current_selected_deficit": _sum(points, "residual_current_selected_deficit_density_volume"),
        "current_share_of_selected_deficit": _safe_ratio(
            _sum(points, "residual_current_selected_deficit_density_volume"),
            total_selected,
        ),
        "live_residual_pair_l1": _sum(points.loc[live], "residual_pair_l1_density_volume"),
        "live_selected_null_deficit": _sum(points.loc[live], "residual_selected_null_deficit_density_volume"),
        "cap_selected_null_deficit_fraction": _safe_ratio(
            _sum(points.loc[cap], "residual_selected_null_deficit_density_volume"),
            total_selected,
        ),
        "cap_residual_pair_l1_fraction": _safe_ratio(
            _sum(points.loc[cap], "residual_pair_l1_density_volume"),
            _sum(points, "residual_pair_l1_density_volume"),
        ),
    }
    row.update(_partition_stats(points.loc[~cap], "body"))
    row.update(_partition_stats(points.loc[cap], "cap"))
    zone = points["residual_zone"].astype(str)
    row.update(_partition_stats(points.loc[zone.eq("core_cloud_body")], "core_body"))
    row.update(_partition_stats(points.loc[zone.eq("support_edge_shoulder")], "edge_shoulder"))
    return pd.DataFrame([row])


def _by_location(points: pd.DataFrame) -> pd.DataFrame:
    if points.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    grouped = points.groupby(["stage", "region", "inside_packet_live", "residual_partition", "residual_zone"], dropna=False)
    for (stage, region, live, partition, zone), group in grouped:
        selected = _sum(group, "residual_selected_null_deficit_density_volume")
        pair = _sum(group, "residual_pair_l1_density_volume")
        pair_norm = _sum(group, "abs_rho_density_volume") + _sum(group, "abs_p_l_density_volume")
        rows.append({
            "stage": str(stage),
            "region": str(region),
            "inside_packet_live": bool(live),
            "residual_partition": str(partition),
            "residual_zone": str(zone),
            "support_points": int(len(group)),
            "string_mu_integral": _sum(group, "string_cloud_mu_volume"),
            "residual_pair_l1": pair,
            "residual_pair_fraction": _safe_ratio(pair, pair_norm),
            "selected_null_deficit": selected,
            "static_null_deficit": _sum(group, "residual_static_null_deficit_density_volume"),
            "current_selected_deficit": _sum(group, "residual_current_selected_deficit_density_volume"),
            "current_share_of_selected_deficit": _safe_ratio(
                _sum(group, "residual_current_selected_deficit_density_volume"),
                selected,
            ),
            "abs_current": _sum(group, "residual_abs_current_density_volume"),
            "abs_pomega": _sum(group, "residual_abs_pomega_density_volume"),
            "abs_rho_residual": _sum(group, "residual_abs_rho_density_volume"),
            "abs_p_l_residual": _sum(group, "residual_abs_p_l_density_volume"),
            "s_min": float(group["s"].min()),
            "s_max": float(group["s"].max()),
            "l_min": float(group["l"].min()),
            "l_max": float(group["l"].max()),
        })
    out = pd.DataFrame(rows)
    return out.sort_values(["selected_null_deficit", "residual_pair_l1"], ascending=[False, False])


def _role_targets(points: pd.DataFrame) -> pd.DataFrame:
    if points.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    role_specs = [
        (
            "core_body_radial_shape_residual",
            "core_cloud_body",
            "radial_pair",
            "residual_pair_l1_density_volume",
            "This is the clean body residual; check numerical/profile mismatch before adding a source family.",
        ),
        (
            "core_body_current_leakage",
            "core_cloud_body",
            "current",
            "residual_abs_current_density_volume",
            "Keep out of the primary string cloud; this should remain negligible.",
        ),
        (
            "core_body_angular_leakage",
            "core_cloud_body",
            "angular",
            "residual_abs_pomega_density_volume",
            "Keep separate from the radial cloud; compare against G only if it survives the edge split.",
        ),
        (
            "edge_shoulder_radial_endpoint_trim",
            "support_edge_shoulder",
            "radial_pair",
            "residual_pair_l1_density_volume",
            "Support-edge shoulder trim outside the reset cap; candidate endpoint/anchor correction.",
        ),
        (
            "edge_shoulder_current_relaxation_DH",
            "support_edge_shoulder",
            "current",
            "residual_abs_current_density_volume",
            "Non-reset support-edge current leakage; compare with D/H before adding live trim.",
        ),
        (
            "edge_shoulder_angular_capacity_G",
            "support_edge_shoulder",
            "angular",
            "residual_abs_pomega_density_volume",
            "Support-edge angular leakage; compare with G/angular-capacity target.",
        ),
        (
            "edge_shoulder_selected_null_deficit",
            "support_edge_shoulder",
            "selected_null",
            "residual_selected_null_deficit_density_volume",
            "Secondary null-deficit risk after the reset cap; keep non-live and edge-localized.",
        ),
        (
            "cap_radial_endpoint_trim",
            "reset_cap",
            "radial_pair",
            "residual_pair_l1_density_volume",
            "Endpoint/anchor trim for reset core/support-edge rows.",
        ),
        (
            "cap_current_relaxation_DH",
            "reset_cap",
            "current",
            "residual_abs_current_density_volume",
            "Assign to D/H current relaxation; do not hide in live C/E/F.",
        ),
        (
            "cap_angular_capacity_G",
            "reset_cap",
            "angular",
            "residual_abs_pomega_density_volume",
            "Assign to G/angular capacity or an endpoint jacket; do not hide in live C/E/F.",
        ),
        (
            "cap_selected_null_deficit",
            "reset_cap",
            "selected_null",
            "residual_selected_null_deficit_density_volume",
            "Primary cap risk; must stay non-live, localized, conserved, and SNEC-clean.",
        ),
    ]
    total_pair = _sum(points, "residual_pair_l1_density_volume")
    total_current = _sum(points, "residual_abs_current_density_volume")
    total_angular = _sum(points, "residual_abs_pomega_density_volume")
    total_selected = _sum(points, "residual_selected_null_deficit_density_volume")
    denominators = {
        "radial_pair": total_pair,
        "current": total_current,
        "angular": total_angular,
        "selected_null": total_selected,
    }
    for role, partition, kind, column, action in role_specs:
        frame = points.loc[points["residual_zone"].astype(str).eq(partition)].copy()
        burden = _sum(frame, column)
        if burden <= 0.0:
            continue
        live = _bool_series(frame["inside_packet_live"])
        rows.append({
            "role_target": role,
            "residual_partition": "reset_cap" if partition == "reset_cap" else "string_cloud_body",
            "residual_zone": partition,
            "residual_kind": kind,
            "burden": burden,
            "fraction_of_kind_total": _safe_ratio(burden, denominators[kind]),
            "live_burden": _sum(frame.loc[live], column),
            "live_fraction": _safe_ratio(_sum(frame.loc[live], column), burden),
            "dominant_stage": str(frame.groupby("stage")[column].sum().sort_values(ascending=False).index[0]),
            "dominant_region": str(frame.groupby("region")[column].sum().sort_values(ascending=False).index[0]),
            "suggested_assignment": action,
        })
    return pd.DataFrame(rows).sort_values(["burden", "role_target"], ascending=[False, True])


def build_radial_string_cloud_replacement(component_dir: Path) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    radial_outputs, radial_metadata = build_radial_shell_viability(component_dir)
    points = radial_outputs["point_targets"].copy()
    if points.empty:
        outputs = {
            "summary": pd.DataFrame(),
            "by_location": pd.DataFrame(),
            "point_residuals": pd.DataFrame(),
            "role_targets": pd.DataFrame(),
        }
        return outputs, {"component_dir": component_dir, "radial_metadata": radial_metadata}
    if "gamma_omega" not in points.columns or points["gamma_omega"].isna().all():
        raise ValueError("radial string-cloud replacement requires gamma_omega in point targets")
    cap = _cap_mask(points)
    phi = _fit_phi(points)
    body_phi = _fit_phi(points, mask=~cap)
    pair_l2_phi = _fit_phi_pair_l2(points)
    point_residuals = _add_string_cloud_residuals(points, phi)
    outputs = {
        "summary": _summary(point_residuals, phi, body_phi, pair_l2_phi),
        "by_location": _by_location(point_residuals),
        "point_residuals": point_residuals,
        "role_targets": _role_targets(point_residuals),
    }
    metadata = {
        "component_dir": component_dir,
        "radial_metadata": radial_metadata,
        "cap_stages": sorted(CAP_STAGES),
        "cap_regions": sorted(CAP_REGIONS),
    }
    return outputs, metadata


def write_radial_string_cloud_replacement_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary": outdir / "radial_string_cloud_summary.csv",
        "by_location": outdir / "radial_string_cloud_by_location.csv",
        "point_residuals": outdir / "radial_string_cloud_point_residuals.csv",
        "role_targets": outdir / "radial_string_cloud_role_targets.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)

    radial_metadata = metadata.get("radial_metadata", {})
    manifest_path = outdir / "radial_string_cloud_manifest.json"
    manifest = {
        "caveat": (
            "A/B/I constant-areal-flux string-cloud replacement diagnostic. "
            "This builds target residuals after subtracting mu = Phi/gamma_omega; "
            "it is not a conservation proof, matter model, or SNEC certification."
        ),
        "model": "rho=Phi/gamma_omega, p_l=-Phi/gamma_omega, j_l=0, pOmega=0",
        "component_source_dir": str(metadata["component_dir"]),
        "component_source_manifest": str(radial_metadata.get("manifest_path", "")),
        "component_detail": str(radial_metadata.get("detail_path", "")),
        "component_detail_sha256": sha256_file(Path(radial_metadata["detail_path"]))
        if radial_metadata.get("detail_path") else "",
        "cap_stages": metadata.get("cap_stages", []),
        "cap_regions": metadata.get("cap_regions", []),
        "files": {key: str(path) for key, path in paths.items()},
        "rows": {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths},
        "sha256": {key: sha256_file(path) for key, path in paths.items()},
    }
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
