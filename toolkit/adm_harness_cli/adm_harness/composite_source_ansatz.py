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


SECTOR_COMPONENTS = {
    "infrastructure_radial_support": [
        "A_infrastructure_radial_null_support",
        "B_core_radial_pressure_balance",
    ],
    "infrastructure_angular_capacity": [
        "G_infrastructure_angular_capacity",
    ],
    "live_handoff_trim": [
        "C_live_handoff_angular_current",
        "E_live_handoff_radial_null_trim",
        "F_live_handoff_radial_pressure_trim",
    ],
    "reset_current_sink": [
        "D_reset_support_edge_current_sink",
    ],
    "distributed_current_relaxation_H": [
        "H_distributed_current_relaxation",
    ],
}


SECTOR_AMPLITUDE = {
    "infrastructure_radial_support": "rho_euler",
    "infrastructure_angular_capacity": "p_omega_unit",
    "live_handoff_trim": "rho_euler",
    "reset_current_sink": "j_l_unit",
    "distributed_current_relaxation_H": "j_l_unit",
    "residual_current_diagnostic": "j_l_unit",
}


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if not math.isfinite(number):
        return default
    return number


def _load_component_detail(component_dir: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    manifest_path = component_dir / "component_source_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    detail_value = manifest.get("files", {}).get("detail", "component_source_assignment_detail.csv")
    detail_path = resolve_manifest_path(component_dir, detail_value)
    return pd.read_csv(detail_path), {"manifest_path": manifest_path, "manifest": manifest, "detail_path": detail_path}


def _fit_linear(x: pd.Series, y: pd.Series, weights: pd.Series) -> tuple[float, float]:
    xv = x.astype(float).to_numpy()
    yv = y.astype(float).to_numpy()
    wv = weights.astype(float).to_numpy()
    mask = np.isfinite(xv) & np.isfinite(yv) & np.isfinite(wv) & (wv > 0.0)
    if int(mask.sum()) == 0:
        return float("nan"), float("nan")
    x_m = xv[mask]
    y_m = yv[mask]
    w_m = wv[mask]
    denom = float(np.sum(w_m * x_m * x_m))
    coeff = float(np.sum(w_m * x_m * y_m) / denom) if denom > 0.0 else 0.0
    fit = coeff * x_m
    residual = float(np.sum(w_m * np.abs(y_m - fit)) / max(np.sum(w_m * np.abs(y_m)), 1.0e-30))
    return coeff, residual


def _weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    v = values.astype(float).to_numpy()
    w = weights.astype(float).to_numpy()
    mask = np.isfinite(v) & np.isfinite(w) & (w > 0.0)
    if int(mask.sum()) == 0:
        return float("nan")
    return float(np.sum(v[mask] * w[mask]) / np.sum(w[mask]))


def _unassigned_current_frame(detail: pd.DataFrame) -> pd.DataFrame:
    return detail.loc[(~detail["assigned"].astype(bool)) & (detail["channel"] == "abs_j_l")].copy()


def _sector_frame(detail: pd.DataFrame, sector: str) -> pd.DataFrame:
    if sector in {"residual_current_diagnostic", "distributed_current_relaxation_H"}:
        frame = _unassigned_current_frame(detail)
        if sector == "distributed_current_relaxation_H":
            frame = frame.copy()
            frame["component"] = "H_distributed_current_relaxation"
            frame["component_description"] = "Promoted non-live distributed current-relaxation sector."
            frame["assignment_reason"] = "promoted_from_unassigned_non_live_current_residual"
            frame["assigned"] = True
        return frame
    components = SECTOR_COMPONENTS[sector]
    return detail.loc[detail["component"].isin(components)].copy()


def _fit_sector(label: str, sector: str, frame: pd.DataFrame) -> dict[str, Any]:
    weights = frame["demand_volume_burden"].astype(float)
    amp_col = SECTOR_AMPLITUDE[sector]
    amp = frame[amp_col].astype(float)
    row: dict[str, Any] = {
        "label": label,
        "sector": sector,
        "components": ",".join(SECTOR_COMPONENTS.get(sector, ["unassigned_abs_j_l"])),
        "amplitude_variable": amp_col,
        "rows": int(len(frame)),
        "total_burden": float(weights.sum()),
        "live_burden": float(frame.loc[frame["inside_packet_live"].astype(bool), "demand_volume_burden"].sum()),
        "live_fraction": float(frame.loc[frame["inside_packet_live"].astype(bool), "demand_volume_burden"].sum() / weights.sum())
        if float(weights.sum()) > 0.0 else float("nan"),
        "mean_amplitude": _weighted_mean(amp, weights),
        "max_abs_amplitude": float(np.nanmax(np.abs(amp.to_numpy(dtype=float)))) if len(frame) else float("nan"),
        "mean_null_cancellation": _weighted_mean(frame["null_cancellation_ratio_proxy"], weights),
        "mean_pressure_cancel": _weighted_mean(frame["pressure_cancel_ratio"], weights),
        "mean_current_dominance": _weighted_mean(frame["current_dominance_ratio"], weights),
        "mean_angular_dominance": _weighted_mean(frame["angular_dominance_ratio"], weights),
    }
    residuals: list[float] = []
    for target in ["rho_euler", "p_l_unit", "j_l_unit", "p_omega_unit"]:
        coeff, residual = _fit_linear(amp, frame[target], weights)
        row[f"{target}_per_{amp_col}"] = coeff
        row[f"{target}_relative_l1_residual"] = residual
        if target != amp_col and math.isfinite(residual):
            residuals.append(residual)
    row["mean_cross_component_residual"] = float(np.mean(residuals)) if residuals else float("nan")
    row.update(_sector_constraints(sector, row))
    return row


def _sector_constraints(sector: str, row: dict[str, Any]) -> dict[str, Any]:
    flags: dict[str, Any] = {}
    if sector == "infrastructure_radial_support":
        p_ratio = _finite(row.get("p_l_unit_per_rho_euler"), float("nan"))
        j_ratio = abs(_finite(row.get("j_l_unit_per_rho_euler"), float("nan")))
        omega_ratio = abs(_finite(row.get("p_omega_unit_per_rho_euler"), float("nan")))
        flags["constraint_summary"] = "rho_positive_radial_tension"
        flags["passes_primary_constraint"] = bool(-1.10 <= p_ratio <= -0.90 and j_ratio <= 0.10)
        flags["secondary_warning_count"] = int(omega_ratio > 0.25)
    elif sector == "infrastructure_angular_capacity":
        rho_ratio = abs(_finite(row.get("rho_euler_per_p_omega_unit"), float("nan")))
        pl_ratio = abs(_finite(row.get("p_l_unit_per_p_omega_unit"), float("nan")))
        flags["constraint_summary"] = "pOmega_dominant_support_jacket"
        flags["passes_primary_constraint"] = bool(rho_ratio <= 0.50 and pl_ratio <= 0.50)
        flags["secondary_warning_count"] = 0
    elif sector == "live_handoff_trim":
        p_ratio = _finite(row.get("p_l_unit_per_rho_euler"), float("nan"))
        omega_ratio = abs(_finite(row.get("p_omega_unit_per_rho_euler"), float("nan")))
        flags["constraint_summary"] = "coupled_live_handoff_trim"
        flags["passes_primary_constraint"] = bool(-1.30 <= p_ratio <= -0.70 and omega_ratio >= 1.0)
        flags["secondary_warning_count"] = int(_finite(row.get("live_fraction")) < 0.95)
    elif sector == "reset_current_sink":
        flags["constraint_summary"] = "localized_non_live_current_sink"
        flags["passes_primary_constraint"] = bool(_finite(row.get("live_fraction")) == 0.0)
        flags["secondary_warning_count"] = 0
    elif sector == "distributed_current_relaxation_H":
        current_dominance = _finite(row.get("mean_current_dominance"), float("nan"))
        live_fraction = _finite(row.get("live_fraction"), float("nan"))
        rho_ratio = abs(_finite(row.get("rho_euler_per_j_l_unit"), float("nan")))
        pl_ratio = abs(_finite(row.get("p_l_unit_per_j_l_unit"), float("nan")))
        flags["constraint_summary"] = "distributed_non_live_current_relaxation"
        flags["passes_primary_constraint"] = bool(live_fraction == 0.0 and current_dominance >= 2.0)
        flags["secondary_warning_count"] = int(max(rho_ratio, pl_ratio) > 0.30)
    else:
        flags["constraint_summary"] = "residual_current_diagnostic"
        flags["passes_primary_constraint"] = False
        flags["secondary_warning_count"] = 1
    return flags


def _sector_fit_table(detail: pd.DataFrame, promote_h: bool) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    sectors = [
        "infrastructure_radial_support",
        "infrastructure_angular_capacity",
        "live_handoff_trim",
        "reset_current_sink",
    ]
    sectors.append("distributed_current_relaxation_H" if promote_h else "residual_current_diagnostic")
    for label, label_group in detail.groupby("label", sort=False):
        for sector in sectors:
            frame = _sector_frame(label_group, sector)
            if frame.empty:
                continue
            rows.append(_fit_sector(str(label), sector, frame))
    return pd.DataFrame(rows).sort_values(["label", "sector"])


def _decision_table(sector_fits: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for label, group in sector_fits.groupby("label", sort=False):
        residual_current = group.loc[group["sector"] == "residual_current_diagnostic"]
        h_burden = float(residual_current["total_burden"].iloc[0]) if not residual_current.empty else 0.0
        promoted_h = group.loc[group["sector"] == "distributed_current_relaxation_H"]
        promoted_h_burden = float(promoted_h["total_burden"].iloc[0]) if not promoted_h.empty else 0.0
        reset = group.loc[group["sector"] == "reset_current_sink"]
        d_burden = float(reset["total_burden"].iloc[0]) if not reset.empty else 0.0
        required = group.loc[group["sector"].isin([
            "infrastructure_radial_support",
            "infrastructure_angular_capacity",
            "live_handoff_trim",
            "distributed_current_relaxation_H",
        ])]
        primary_passes = bool(required["passes_primary_constraint"].astype(bool).all()) if not required.empty else False
        rows.append({
            "label": label,
            "required_sector_constraints_pass": primary_passes,
            "residual_current_burden": h_burden,
            "promoted_H_current_burden": promoted_h_burden,
            "reset_current_sink_burden": d_burden,
            "residual_current_to_D_ratio": h_burden / d_burden if d_burden > 0.0 else float("inf"),
            "current_relaxation_to_D_ratio": (h_burden + promoted_h_burden) / d_burden
            if d_burden > 0.0 else float("inf"),
            "promote_H_now": bool(promoted_h_burden == 0.0 and h_burden > 0.0 and h_burden > 2.0 * max(d_burden, 1.0e-30)),
            "H_constraint_passes": bool(promoted_h["passes_primary_constraint"].astype(bool).all())
            if not promoted_h.empty else False,
            "hard_snec_ready": False,
            "recommended_next": "run_hard_affine_snec_after_source_sector_assumptions"
            if promoted_h_burden > 0.0 and primary_passes else "fit_composite_effective_source_then_reassess_H",
        })
    return pd.DataFrame(rows)


def build_composite_source_ansatz_screen(
    component_dir: Path,
    *,
    promote_h: bool = False,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    detail, metadata = _load_component_detail(component_dir)
    detail = _add_algebra_columns(detail)
    sector_fits = _sector_fit_table(detail, promote_h=promote_h)
    outputs = {
        "sector_fits": sector_fits,
        "decision": _decision_table(sector_fits),
    }
    metadata["promote_h"] = bool(promote_h)
    return outputs, metadata


def write_composite_source_ansatz_outputs(
    outdir: Path,
    component_dir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "sector_fits": outdir / "composite_source_ansatz_sector_fits.csv",
        "decision": outdir / "composite_source_ansatz_decision.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "composite_source_ansatz_manifest.json"
    manifest = {
        "ansatz": (
            "composite_anisotropic_support_with_H"
            if metadata.get("promote_h") else "composite_anisotropic_support_v0"
        ),
        "caveat": (
            "Reduced sector-level effective anisotropic stress fit. This tests algebraic "
            "compatibility of component-source sectors; it is not a field equation solve, "
            "conservation proof, or SNEC certification."
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
