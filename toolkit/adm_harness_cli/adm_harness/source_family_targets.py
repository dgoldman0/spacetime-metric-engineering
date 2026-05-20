from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .source_ledger import sha256_file, write_manifest
from .source_screening import resolve_manifest_path


SECTOR_TARGETS: dict[str, dict[str, str]] = {
    "infrastructure_radial_support": {
        "candidate_family": "anisotropic_radial_tension_shell",
        "support_class": "exotic_near_nec_radial_infrastructure",
        "model_target": (
            "Non-live radial support with rho positive, p_l approximately -rho, "
            "and negligible current. Cover A/B/I together before tuning residuals."
        ),
        "scalar_suitability": "poor_as_single_scalar",
        "risk": "Dominant burden; a scalar-only replacement is unlikely to keep p_l and current quiet.",
    },
    "infrastructure_angular_capacity": {
        "candidate_family": "angular_capacity_jacket",
        "support_class": "anisotropic_regular_infrastructure",
        "model_target": "Non-live pOmega-dominant jacket with small radial pressure and current leakage.",
        "scalar_suitability": "possible_as_auxiliary_not_primary",
        "risk": "Must not contaminate the radial-tension sector or live packet.",
    },
    "live_handoff_trim": {
        "candidate_family": "transient_handoff_boundary_layer",
        "support_class": "live_packet_trim",
        "model_target": "Localized live packet-in-support trim carrying radial-null, radial-pressure, angular, and current terms.",
        "scalar_suitability": "poor_as_stationary_scalar",
        "risk": "Live burden is allowed here, but packet contamination outside the handoff layer is the main failure mode.",
    },
    "reset_current_sink": {
        "candidate_family": "localized_vector_current_sink",
        "support_class": "non_live_current_control",
        "model_target": "Small reset/support-edge current sink with minimal energy/pressure baggage.",
        "scalar_suitability": "poor",
        "risk": "Needs a current-carrying family; scalar replacements tend to add stress without directed flux.",
    },
    "distributed_current_relaxation_H": {
        "candidate_family": "distributed_vector_current_relaxation",
        "support_class": "non_live_current_control",
        "model_target": "Distributed non-live current-relaxation sector H, larger than D but small in absolute burden.",
        "scalar_suitability": "poor",
        "risk": "This is the sector to watch for hidden conservation cost, not raw exotic magnitude.",
    },
}


COMPONENT_TO_SECTOR = {
    "A_infrastructure_radial_null_support": "infrastructure_radial_support",
    "B_core_radial_pressure_balance": "infrastructure_radial_support",
    "I_support_edge_radial_pressure_balance": "infrastructure_radial_support",
    "G_infrastructure_angular_capacity": "infrastructure_angular_capacity",
    "C_live_handoff_angular_current": "live_handoff_trim",
    "E_live_handoff_radial_null_trim": "live_handoff_trim",
    "F_live_handoff_radial_pressure_trim": "live_handoff_trim",
    "D_reset_support_edge_current_sink": "reset_current_sink",
    "H_distributed_current_relaxation": "distributed_current_relaxation_H",
}


CHANNEL_FAMILY_HINTS = {
    "neg_Tkk_radial": "radial_null_exotic_support",
    "abs_p_l": "radial_pressure_balance",
    "abs_j_l": "current_relaxation",
    "abs_pOmega": "angular_capacity",
}


def _read_csv(path: Path | None) -> pd.DataFrame:
    if path is None or not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if not math.isfinite(number):
        return default
    return number


def _bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin({"1", "true", "yes"})


def _weighted_mean(frame: pd.DataFrame, column: str, weight_column: str = "demand_volume_burden") -> float:
    if frame.empty or column not in frame.columns or weight_column not in frame.columns:
        return float("nan")
    values = frame[column].astype(float).to_numpy()
    weights = frame[weight_column].astype(float).to_numpy()
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0.0)
    if int(mask.sum()) == 0:
        return float("nan")
    return float(np.sum(values[mask] * weights[mask]) / np.sum(weights[mask]))


def _dominant_value(frame: pd.DataFrame, column: str, weight_column: str = "demand_volume_burden") -> tuple[str, float]:
    if frame.empty or column not in frame.columns or weight_column not in frame.columns:
        return "", float("nan")
    grouped = frame.groupby(column, dropna=False)[weight_column].sum().sort_values(ascending=False)
    if grouped.empty:
        return "", float("nan")
    total = float(grouped.sum())
    value = str(grouped.index[0])
    fraction = float(grouped.iloc[0] / total) if total > 0.0 else float("nan")
    return value, fraction


def _channel_burdens(frame: pd.DataFrame) -> dict[str, float]:
    if frame.empty:
        return {}
    grouped = frame.groupby("channel")["demand_volume_burden"].sum().sort_values(ascending=False)
    return {str(k): float(v) for k, v in grouped.items()}


def _dominant_channel(frame: pd.DataFrame) -> tuple[str, float]:
    burdens = _channel_burdens(frame)
    if not burdens:
        return "", float("nan")
    total = float(sum(burdens.values()))
    channel, burden = next(iter(burdens.items()))
    return channel, burden / total if total > 0.0 else float("nan")


def _format_channel_burdens(frame: pd.DataFrame) -> str:
    burdens = _channel_burdens(frame)
    return ";".join(f"{channel}:{burden:.12g}" for channel, burden in burdens.items())


def _safe_ratio(num: float, denom: float) -> float:
    return float(num / denom) if denom > 0.0 else float("nan")


def _component_frame(detail: pd.DataFrame, component: str) -> pd.DataFrame:
    if component == "H_distributed_current_relaxation":
        if detail.empty:
            return pd.DataFrame()
        assigned = _bool_series(detail["assigned"])
        live = _bool_series(detail["inside_packet_live"])
        frame = detail.loc[(~assigned) & (~live) & (detail["channel"] == "abs_j_l")].copy()
        frame["component"] = component
        frame["component_description"] = "Promoted non-live distributed current-relaxation residual."
        return frame
    return detail.loc[detail["component"] == component].copy()


def _component_targets(detail: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    assigned = detail.loc[detail["component"] != "unassigned"].copy()
    components = sorted(str(value) for value in assigned["component"].dropna().unique())
    if not detail.empty:
        components.append("H_distributed_current_relaxation")
    total_reference = float(detail["demand_volume_burden"].sum()) if "demand_volume_burden" in detail.columns else 0.0
    for component in components:
        frame = _component_frame(detail, component)
        if frame.empty:
            continue
        total = float(frame["demand_volume_burden"].sum())
        live_mask = _bool_series(frame["inside_packet_live"])
        live = float(frame.loc[live_mask, "demand_volume_burden"].sum())
        stage, stage_fraction = _dominant_value(frame, "stage")
        region, region_fraction = _dominant_value(frame, "region")
        channel, channel_fraction = _dominant_channel(frame)
        sector = COMPONENT_TO_SECTOR.get(component, "")
        target = SECTOR_TARGETS.get(sector, {})
        rows.append({
            "component": component,
            "sector": sector,
            "candidate_family": target.get("candidate_family", ""),
            "support_class": target.get("support_class", ""),
            "dominant_channel": channel,
            "dominant_channel_fraction": channel_fraction,
            "channel_burdens": _format_channel_burdens(frame),
            "total_burden": total,
            "burden_fraction_of_all_channels": _safe_ratio(total, total_reference),
            "live_burden": live,
            "live_fraction": _safe_ratio(live, total),
            "dominant_stage": stage,
            "dominant_stage_fraction": stage_fraction,
            "dominant_region": region,
            "dominant_region_fraction": region_fraction,
            "s_min": float(frame["s"].min()),
            "s_max": float(frame["s"].max()),
            "l_min": float(frame["l"].min()),
            "l_max": float(frame["l"].max()),
            "weighted_rho_euler": _weighted_mean(frame, "rho_euler"),
            "weighted_p_l_unit": _weighted_mean(frame, "p_l_unit"),
            "weighted_j_l_unit": _weighted_mean(frame, "j_l_unit"),
            "weighted_p_omega_unit": _weighted_mean(frame, "p_omega_unit"),
            "model_requirement": target.get("model_target", ""),
            "risk": target.get("risk", ""),
        })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["total_burden", "component"], ascending=[False, True])


def _sector_targets(sector_fits: pd.DataFrame, detail: pd.DataFrame) -> pd.DataFrame:
    if sector_fits.empty:
        return pd.DataFrame()
    channel_total = float(detail["demand_volume_burden"].sum()) if not detail.empty else float(sector_fits["total_burden"].sum())
    sector_total = float(sector_fits["total_burden"].sum())
    rows: list[dict[str, Any]] = []
    for _, source_row in sector_fits.iterrows():
        sector = str(source_row["sector"])
        target = SECTOR_TARGETS.get(sector, {})
        total_burden = _finite(source_row.get("total_burden"))
        live_burden = _finite(source_row.get("live_burden"))
        rows.append({
            "label": source_row.get("label", ""),
            "sector": sector,
            "components": source_row.get("components", ""),
            "candidate_family": target.get("candidate_family", ""),
            "support_class": target.get("support_class", ""),
            "total_burden": total_burden,
            "sector_burden_fraction": _safe_ratio(total_burden, sector_total),
            "burden_fraction_of_all_channels": _safe_ratio(total_burden, channel_total),
            "live_burden": live_burden,
            "live_fraction": _finite(source_row.get("live_fraction"), float("nan")),
            "amplitude_variable": source_row.get("amplitude_variable", ""),
            "mean_amplitude": _finite(source_row.get("mean_amplitude"), float("nan")),
            "max_abs_amplitude": _finite(source_row.get("max_abs_amplitude"), float("nan")),
            "rho_euler_per_amplitude": _coefficient_for_amplitude(source_row, "rho_euler"),
            "p_l_unit_per_amplitude": _coefficient_for_amplitude(source_row, "p_l_unit"),
            "j_l_unit_per_amplitude": _coefficient_for_amplitude(source_row, "j_l_unit"),
            "p_omega_unit_per_amplitude": _coefficient_for_amplitude(source_row, "p_omega_unit"),
            "mean_null_cancellation": _finite(source_row.get("mean_null_cancellation"), float("nan")),
            "mean_pressure_cancel": _finite(source_row.get("mean_pressure_cancel"), float("nan")),
            "mean_current_dominance": _finite(source_row.get("mean_current_dominance"), float("nan")),
            "mean_angular_dominance": _finite(source_row.get("mean_angular_dominance"), float("nan")),
            "mean_cross_component_residual": _finite(source_row.get("mean_cross_component_residual"), float("nan")),
            "constraint_summary": source_row.get("constraint_summary", ""),
            "passes_primary_constraint": bool(source_row.get("passes_primary_constraint", False)),
            "secondary_warning_count": int(_finite(source_row.get("secondary_warning_count"), 0.0)),
            "scalar_suitability": target.get("scalar_suitability", ""),
            "model_target": target.get("model_target", ""),
            "risk": target.get("risk", ""),
        })
    out = pd.DataFrame(rows)
    return out.sort_values(["total_burden", "sector"], ascending=[False, True])


def _coefficient_for_amplitude(row: pd.Series, target: str) -> float:
    amp = str(row.get("amplitude_variable", ""))
    if not amp:
        return float("nan")
    if target == amp:
        return 1.0
    return _finite(row.get(f"{target}_per_{amp}"), float("nan"))


def _residual_action(channel: str, live: bool) -> str:
    if live:
        return "Fold into live handoff trim only if spatially packet-bound."
    if channel == "neg_Tkk_radial":
        return "Tighten radial support sector shape or add residual conservation correction."
    if channel == "abs_p_l":
        return "Tune radial pressure balance at the localized support edge/core row set."
    if channel == "abs_j_l":
        return "Assign to H/current-relaxation family; check conservation side effects."
    if channel == "abs_pOmega":
        return "Tune angular capacity jacket or support-edge residual correction."
    return "Inspect residual family assignment."


def _residual_targets(detail: pd.DataFrame, top_unassigned: pd.DataFrame) -> pd.DataFrame:
    if detail.empty:
        return pd.DataFrame()
    assigned = _bool_series(detail["assigned"])
    residual = detail.loc[~assigned].copy()
    if residual.empty:
        return pd.DataFrame()
    channel_totals = detail.groupby("channel")["demand_volume_burden"].sum().to_dict()
    rows: list[dict[str, Any]] = []
    grouped = residual.groupby(["channel", "stage", "region", "inside_packet_live"], dropna=False)
    for (channel, stage, region, live), frame in grouped:
        total = float(frame["unassigned_volume_burden"].sum())
        if total <= 0.0:
            continue
        live_bool = bool(live)
        channel_total = float(channel_totals.get(channel, 0.0))
        rows.append({
            "target_kind": "unassigned_component_residual",
            "channel": str(channel),
            "family_hint": CHANNEL_FAMILY_HINTS.get(str(channel), ""),
            "stage": str(stage),
            "region": str(region),
            "inside_packet_live": live_bool,
            "rows": int(len(frame)),
            "unassigned_burden": total,
            "fraction_of_channel_total": _safe_ratio(total, channel_total),
            "s_min": float(frame["s"].min()),
            "s_max": float(frame["s"].max()),
            "l_min": float(frame["l"].min()),
            "l_max": float(frame["l"].max()),
            "weighted_rho_euler": _weighted_mean(frame, "rho_euler", "unassigned_volume_burden"),
            "weighted_p_l_unit": _weighted_mean(frame, "p_l_unit", "unassigned_volume_burden"),
            "weighted_j_l_unit": _weighted_mean(frame, "j_l_unit", "unassigned_volume_burden"),
            "weighted_p_omega_unit": _weighted_mean(frame, "p_omega_unit", "unassigned_volume_burden"),
            "suggested_action": _residual_action(str(channel), live_bool),
        })
    out = pd.DataFrame(rows)
    if not top_unassigned.empty:
        top_counts = (
            top_unassigned.groupby(["channel", "stage", "region", "inside_packet_live"], dropna=False)
            .size()
            .rename("top_unassigned_rows")
            .reset_index()
        )
        out = out.merge(top_counts, on=["channel", "stage", "region", "inside_packet_live"], how="left")
        out["top_unassigned_rows"] = out["top_unassigned_rows"].fillna(0).astype(int)
    else:
        out["top_unassigned_rows"] = 0
    return out.sort_values(["unassigned_burden", "channel"], ascending=[False, True])


def _snec_targets(top_windows: pd.DataFrame) -> pd.DataFrame:
    if top_windows.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for _, row in top_windows.head(50).iterrows():
        dominant = str(row.get("dominant_negative_sector", ""))
        target = SECTOR_TARGETS.get(dominant, {})
        rows.append({
            "target_kind": "snec_limiter_window",
            "branch": row.get("branch", ""),
            "smear_width_affine": _finite(row.get("smear_width_affine"), float("nan")),
            "center_s": _finite(row.get("center_s"), float("nan")),
            "center_l": _finite(row.get("center_l"), float("nan")),
            "center_stage": row.get("center_stage", ""),
            "center_region": row.get("center_region", ""),
            "center_inside_packet_live": bool(row.get("center_inside_packet_live", False)),
            "margin_to_benchmark_floor": _finite(row.get("margin_to_benchmark_floor"), float("nan")),
            "critical_B_for_zero_margin": _finite(row.get("critical_B_for_zero_margin"), float("nan")),
            "dominant_negative_sector": dominant,
            "candidate_family": target.get("candidate_family", "residual_conservation_closure"),
            "smeared_total_Tkk_hat": _finite(row.get("smeared_total_Tkk_hat"), float("nan")),
            "smeared_total_neg_part": _finite(row.get("smeared_total_neg_part"), float("nan")),
            "suggested_action": (
                "Reduce sector_closure_residual in support-edge windows before changing geometry."
                if dominant == "sector_closure_residual"
                else f"Check {dominant} shape in affine limiting windows."
            ),
        })
    out = pd.DataFrame(rows)
    return out.sort_values(["margin_to_benchmark_floor", "critical_B_for_zero_margin"])


def _candidate_matrix(sector_targets: pd.DataFrame, component_targets: pd.DataFrame, residual_targets: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if not sector_targets.empty:
        for family, frame in sector_targets.groupby("candidate_family", dropna=False):
            family = str(family)
            sectors = ",".join(str(value) for value in frame["sector"].tolist())
            burden = float(frame["total_burden"].sum())
            live = float(frame["live_burden"].sum())
            target = SECTOR_TARGETS.get(str(frame["sector"].iloc[0]), {})
            components = component_targets.loc[
                component_targets["candidate_family"].astype(str) == family, "component"
            ].tolist() if not component_targets.empty else []
            rows.append({
                "candidate_family": family,
                "target_sectors": sectors,
                "target_components": ",".join(components),
                "support_class": target.get("support_class", ""),
                "covered_burden": burden,
                "live_fraction": _safe_ratio(live, burden),
                "priority": _priority_for_family(family, burden, _safe_ratio(live, burden)),
                "scalar_suitability": target.get("scalar_suitability", ""),
                "first_fit_test": _first_fit_test(family),
                "conservation_watch": _conservation_watch(family),
                "packet_contamination_watch": _packet_watch(family),
                "model_target": target.get("model_target", ""),
                "risk": target.get("risk", ""),
            })
    if not residual_targets.empty:
        closure_residual = residual_targets.loc[residual_targets["channel"] != "abs_j_l"].copy()
        residual_burden = float(closure_residual["unassigned_burden"].sum())
        live_mask = closure_residual["inside_packet_live"].astype(bool) if not closure_residual.empty else pd.Series(dtype=bool)
        rows.append({
            "candidate_family": "residual_conservation_closure",
            "target_sectors": "sector_closure_residual",
            "target_components": "unassigned",
            "support_class": "closure_residual_control",
            "covered_burden": residual_burden,
            "live_fraction": _safe_ratio(
                float(closure_residual.loc[live_mask, "unassigned_burden"].sum()) if not closure_residual.empty else 0.0,
                residual_burden,
            ),
            "priority": "high_after_primary_family_shapes",
            "scalar_suitability": "not_a_source_family_by_itself",
            "first_fit_test": "Fit residual localization against support-edge/core row masks and re-run SNEC windows.",
            "conservation_watch": "Highest; residual closure must be tested as a divergence/conservation correction.",
            "packet_contamination_watch": "Do not absorb non-live residuals into live trim unless row masks prove live localization.",
            "model_target": "Remove the localized leftover support-edge/core residual without changing sector signs.",
            "risk": "Can hide failed sector shape if treated as an arbitrary counterterm.",
        })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(["covered_burden", "candidate_family"], ascending=[False, True])


def _priority_for_family(family: str, burden: float, live_fraction: float) -> str:
    if family == "anisotropic_radial_tension_shell":
        return "first"
    if family == "transient_handoff_boundary_layer":
        return "second_live_trim"
    if burden > 5.0:
        return "second_infrastructure"
    if live_fraction == 0.0:
        return "third_non_live_control"
    return "third"


def _first_fit_test(family: str) -> str:
    return {
        "anisotropic_radial_tension_shell": (
            "Solve A/B/I as one non-live radial shell with p_l/rho near -1, low j_l, and support-edge/core masks."
        ),
        "angular_capacity_jacket": (
            "Fit pOmega-dominant jacket on support-edge/core/outer-shell rows and verify radial-sector leakage."
        ),
        "transient_handoff_boundary_layer": (
            "Fit live packet-in-support boundary layer only after the infrastructure families are fixed."
        ),
        "localized_vector_current_sink": "Fit reset support-edge current sink D with minimal stress baggage.",
        "distributed_vector_current_relaxation": "Fit H as non-live vector/current relaxation and test conservation load.",
    }.get(family, "Fit candidate against localized target rows and re-run sector closure.")


def _conservation_watch(family: str) -> str:
    return {
        "anisotropic_radial_tension_shell": "High; dominant static support must close with radial pressure balance.",
        "angular_capacity_jacket": "Medium; angular jacket should not introduce radial pressure imbalance.",
        "transient_handoff_boundary_layer": "High locally; live trim must be packet-bound and time/localization consistent.",
        "localized_vector_current_sink": "High for current divergence in reset windows.",
        "distributed_vector_current_relaxation": "Highest for hidden divergence/current-relaxation burden.",
    }.get(family, "High until residual localization is explained.")


def _packet_watch(family: str) -> str:
    return {
        "anisotropic_radial_tension_shell": "Keep live_fraction at zero.",
        "angular_capacity_jacket": "Keep live_fraction at zero.",
        "transient_handoff_boundary_layer": "Allowed live_fraction near one; keep it inside packet_in_support.",
        "localized_vector_current_sink": "Keep live_fraction at zero.",
        "distributed_vector_current_relaxation": "Keep live_fraction at zero.",
    }.get(family, "Check live/non-live split explicitly.")


def _load_manifest_file(directory: Path, manifest_name: str, file_key: str, fallback: str) -> tuple[dict[str, Any], Path | None]:
    manifest_path = directory / manifest_name
    if not manifest_path.exists():
        return {}, None
    manifest = json.loads(manifest_path.read_text())
    value = manifest.get("files", {}).get(file_key, fallback)
    return manifest, resolve_manifest_path(directory, value)


def build_source_family_targets(
    component_dir: Path,
    *,
    ansatz_dir: Path | None = None,
    snec_dir: Path | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    component_manifest_path = component_dir / "component_source_manifest.json"
    component_manifest = json.loads(component_manifest_path.read_text())
    component_files = component_manifest.get("files", {})
    detail_path = resolve_manifest_path(
        component_dir,
        component_files.get("detail", "component_source_assignment_detail.csv"),
    )
    top_unassigned_path = resolve_manifest_path(
        component_dir,
        component_files.get("top_unassigned", "component_source_top_unassigned.csv"),
    )
    detail = pd.read_csv(detail_path)
    top_unassigned = _read_csv(top_unassigned_path)

    ansatz_manifest: dict[str, Any] = {}
    sector_fits_path: Path | None = None
    if ansatz_dir is not None:
        ansatz_manifest, sector_fits_path = _load_manifest_file(
            ansatz_dir,
            "composite_source_ansatz_manifest.json",
            "sector_fits",
            "composite_source_ansatz_sector_fits.csv",
        )
    sector_fits = _read_csv(sector_fits_path)

    snec_manifest: dict[str, Any] = {}
    top_windows_path: Path | None = None
    if snec_dir is not None:
        snec_manifest, top_windows_path = _load_manifest_file(
            snec_dir,
            "hard_affine_snec_manifest.json",
            "top_windows",
            "hard_affine_snec_top_windows.csv",
        )
    top_windows = _read_csv(top_windows_path)

    component_targets = _component_targets(detail)
    sector_targets = _sector_targets(sector_fits, detail)
    residual_targets = _residual_targets(detail, top_unassigned)
    snec_targets = _snec_targets(top_windows)
    candidate_matrix = _candidate_matrix(sector_targets, component_targets, residual_targets)
    outputs = {
        "sector_targets": sector_targets,
        "component_targets": component_targets,
        "residual_targets": residual_targets,
        "snec_targets": snec_targets,
        "candidate_matrix": candidate_matrix,
    }
    metadata = {
        "component_dir": component_dir,
        "component_manifest_path": component_manifest_path,
        "component_manifest": component_manifest,
        "detail_path": detail_path,
        "top_unassigned_path": top_unassigned_path,
        "ansatz_dir": ansatz_dir,
        "ansatz_manifest": ansatz_manifest,
        "sector_fits_path": sector_fits_path,
        "snec_dir": snec_dir,
        "snec_manifest": snec_manifest,
        "top_windows_path": top_windows_path,
    }
    return outputs, metadata


def write_source_family_target_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "sector_targets": outdir / "source_family_sector_targets.csv",
        "component_targets": outdir / "source_family_component_targets.csv",
        "residual_targets": outdir / "source_family_residual_targets.csv",
        "snec_targets": outdir / "source_family_snec_targets.csv",
        "candidate_matrix": outdir / "source_family_candidate_matrix.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "source_family_targets_manifest.json"
    manifest = {
        "caveat": (
            "Postprocessed source-family target extraction from component closure, composite ansatz, "
            "and optional hard-affine SNEC outputs. This is not a source solve; it defines fit targets "
            "and risk checks for later explicit source-family models."
        ),
        "component_source_dir": str(metadata["component_dir"]),
        "component_source_manifest": str(metadata["component_manifest_path"]),
        "component_detail": str(metadata["detail_path"]),
        "component_detail_sha256": sha256_file(metadata["detail_path"]),
        "component_top_unassigned": str(metadata["top_unassigned_path"]),
        "ansatz_dir": str(metadata["ansatz_dir"]) if metadata.get("ansatz_dir") else None,
        "ansatz_sector_fits": str(metadata["sector_fits_path"]) if metadata.get("sector_fits_path") else None,
        "snec_dir": str(metadata["snec_dir"]) if metadata.get("snec_dir") else None,
        "snec_top_windows": str(metadata["top_windows_path"]) if metadata.get("top_windows_path") else None,
        "files": {key: str(path) for key, path in paths.items()},
        "rows": {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths},
        "sha256": {key: sha256_file(path) for key, path in paths.items()},
    }
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
