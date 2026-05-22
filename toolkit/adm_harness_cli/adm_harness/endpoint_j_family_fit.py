from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .endpoint_j_conservation import (
    ASSIGNMENT_SCOPES,
    J_SECTOR,
    RESET_ASSIGNMENT,
    SUPPORT_ASSIGNMENT,
    build_endpoint_j_conservation_tables,
)
from .source_ledger import sha256_file, write_manifest
from .source_screening import resolve_manifest_path


FIELD_COLUMNS = {
    "rho": "sector_rho",
    "p_l": "sector_p_l",
    "j_l": "sector_j_l",
    "p_omega": "sector_p_omega",
}
ASSIGNMENTS = (SUPPORT_ASSIGNMENT, RESET_ASSIGNMENT)
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


def _centers(values: pd.Series, count: int) -> np.ndarray:
    finite = values.astype(float).replace([np.inf, -np.inf], np.nan).dropna().to_numpy()
    if len(finite) == 0:
        return np.array([0.0], dtype=float)
    if count <= 1 or float(np.max(finite)) == float(np.min(finite)):
        return np.array([float(np.mean(finite))], dtype=float)
    return np.linspace(float(np.min(finite)), float(np.max(finite)), int(count))


def _sigma(centers: np.ndarray, values: pd.Series, width_multiplier: float) -> float:
    if len(centers) > 1:
        spacing = float(np.median(np.diff(centers)))
    else:
        finite = values.astype(float).replace([np.inf, -np.inf], np.nan).dropna().to_numpy()
        spacing = float(np.max(finite) - np.min(finite)) if len(finite) else 1.0
    if spacing <= 0.0 or not math.isfinite(spacing):
        spacing = 1.0
    return float(spacing * width_multiplier)


def _basis_matrix(
    frame: pd.DataFrame,
    *,
    s_centers: int,
    l_centers: int,
    width_multiplier: float,
) -> tuple[np.ndarray, pd.DataFrame]:
    s_values = frame["s"].astype(float).to_numpy()
    l_values = frame["l"].astype(float).to_numpy()
    s_grid = _centers(frame["s"], s_centers)
    l_grid = _centers(frame["l"], l_centers)
    sigma_s = _sigma(s_grid, frame["s"], width_multiplier)
    sigma_l = _sigma(l_grid, frame["l"], width_multiplier)
    columns: list[np.ndarray] = [np.ones(len(frame), dtype=float)]
    meta: list[dict[str, Any]] = [{
        "basis_name": "assignment_uniform",
        "center_s": float("nan"),
        "center_l": float("nan"),
        "sigma_s": float("nan"),
        "sigma_l": float("nan"),
    }]
    for center_s in s_grid:
        for center_l in l_grid:
            values = np.exp(
                -0.5 * (
                    np.square((s_values - float(center_s)) / sigma_s)
                    + np.square((l_values - float(center_l)) / sigma_l)
                )
            )
            columns.append(values)
            meta.append({
                "basis_name": f"rbf_s{center_s:.6g}_l{center_l:.6g}",
                "center_s": float(center_s),
                "center_l": float(center_l),
                "sigma_s": sigma_s,
                "sigma_l": sigma_l,
            })
    basis = np.column_stack(columns)
    peaks = np.max(np.abs(basis), axis=0)
    peaks = np.where(peaks > 0.0, peaks, 1.0)
    basis = basis / peaks
    return basis, pd.DataFrame(meta)


def _ridge_fit(a: np.ndarray, y: np.ndarray, weights: np.ndarray, ridge: float) -> np.ndarray:
    w = np.sqrt(np.clip(weights.astype(float), 0.0, np.inf))
    aw = a * w[:, None]
    yw = y.astype(float) * w
    lhs = aw.T @ aw
    scale = float(np.trace(lhs) / max(lhs.shape[0], 1))
    lam = float(ridge) * scale if scale > 0.0 else float(ridge)
    lhs = lhs + lam * np.eye(lhs.shape[0])
    rhs = aw.T @ yw
    return np.linalg.solve(lhs, rhs)


def _fit_error_summary(
    *,
    label: str,
    assignment: str,
    component: str,
    y: np.ndarray,
    pred: np.ndarray,
    weights: np.ndarray,
    coefficients: np.ndarray,
    basis_count: int,
) -> dict[str, Any]:
    err = pred - y
    abs_y = np.abs(y)
    abs_err = np.abs(err)
    weight_sum = float(np.sum(weights))
    target_l1 = float(np.sum(abs_y * weights))
    error_l1 = float(np.sum(abs_err * weights))
    coeff_abs = np.abs(coefficients)
    coeff_l1 = float(np.sum(coeff_abs))
    coeff_l2 = float(math.sqrt(float(np.sum(np.square(coefficients)))))
    coeff_l2_den = float(np.sum(np.square(coeff_abs)))
    effective_coeff_count = coeff_l1 * coeff_l1 / coeff_l2_den if coeff_l2_den > 0.0 else float("nan")
    return {
        "label": label,
        "assignment": assignment,
        "assignment_scope": ASSIGNMENT_SCOPES.get(assignment, "other_endpoint"),
        "component": component,
        "rows": int(len(y)),
        "basis_count": int(basis_count),
        "weighted_target_l1": target_l1,
        "weighted_error_l1": error_l1,
        "normalized_l1_error": _safe_ratio(error_l1, target_l1),
        "weighted_rmse": (
            float(math.sqrt(np.sum(np.square(err) * weights) / weight_sum)) if weight_sum > 0.0 else float("nan")
        ),
        "max_abs_error": float(np.max(abs_err)) if len(abs_err) else float("nan"),
        "mean_abs_target_density": _safe_ratio(target_l1, weight_sum),
        "peak_abs_target_density": float(np.max(abs_y)) if len(abs_y) else float("nan"),
        "max_abs_coefficient": float(np.max(coeff_abs)) if len(coeff_abs) else float("nan"),
        "coefficient_l1": coeff_l1,
        "coefficient_l2": coeff_l2,
        "effective_coefficient_count": effective_coeff_count,
        "max_coeff_to_mean_target": _safe_ratio(float(np.max(coeff_abs)) if len(coeff_abs) else 0.0, _safe_ratio(target_l1, weight_sum)),
    }


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


def _assignment_summary(target: pd.DataFrame, fitted: pd.DataFrame, label: str, assignment: str, basis_count: int) -> dict[str, Any]:
    live = _bool_series(fitted["inside_packet_live"])
    row = {
        "label": label,
        "assignment": assignment,
        "assignment_scope": ASSIGNMENT_SCOPES.get(assignment, "other_endpoint"),
        "rows": int(len(fitted)),
        "basis_count": int(basis_count),
        "target_selected_null_deficit": float(target["sector_selected_null_deficit_density_volume"].sum()),
        "fit_selected_null_deficit": float(fitted["sector_selected_null_deficit_density_volume"].sum()),
        "target_pair_l1": float(target["sector_pair_l1_density_volume"].sum()),
        "fit_pair_l1": float(fitted["sector_pair_l1_density_volume"].sum()),
        "target_abs_current": float(target["sector_abs_current_density_volume"].sum()),
        "fit_abs_current": float(fitted["sector_abs_current_density_volume"].sum()),
        "target_abs_pomega": float(target["sector_abs_pomega_density_volume"].sum()),
        "fit_abs_pomega": float(fitted["sector_abs_pomega_density_volume"].sum()),
        "fit_live_rows": int(live.sum()),
        "fit_live_selected_null_deficit": float(fitted.loc[live, "sector_selected_null_deficit_density_volume"].sum()),
    }
    row["fit_selected_ratio"] = _safe_ratio(row["fit_selected_null_deficit"], row["target_selected_null_deficit"])
    row["fit_current_ratio"] = _safe_ratio(row["fit_abs_current"], row["target_abs_current"])
    row["fit_pomega_ratio"] = _safe_ratio(row["fit_abs_pomega"], row["target_abs_pomega"])
    return row


def build_endpoint_j_family_fit_tables(
    sectors: pd.DataFrame,
    *,
    labels: list[str] | None = None,
    s_centers: int = 8,
    l_centers: int = 6,
    width_multiplier: float = 1.25,
    ridge: float = 1.0e-8,
) -> dict[str, pd.DataFrame]:
    selected = sectors.loc[sectors["sector"].astype(str) == J_SECTOR].copy()
    if labels:
        label_set = {str(label) for label in labels}
        selected = selected.loc[selected["label"].astype(str).isin(label_set)].copy()
    fit_frames: list[pd.DataFrame] = []
    point_frames: list[pd.DataFrame] = []
    coefficient_frames: list[pd.DataFrame] = []
    component_rows: list[dict[str, Any]] = []
    assignment_rows: list[dict[str, Any]] = []

    for (label, assignment), group in selected.groupby(["label", "assignment"], sort=False, dropna=False):
        if str(assignment) not in ASSIGNMENTS:
            continue
        frame = group.copy().reset_index(drop=True)
        basis, basis_meta = _basis_matrix(
            frame,
            s_centers=int(s_centers),
            l_centers=int(l_centers),
            width_multiplier=float(width_multiplier),
        )
        weights = frame["volume_weight"].astype(float).to_numpy()
        predictions: dict[str, np.ndarray] = {}
        for component, column in FIELD_COLUMNS.items():
            y = frame[column].astype(float).to_numpy()
            coef = _ridge_fit(basis, y, weights, ridge=float(ridge))
            pred = basis @ coef
            predictions[component] = pred
            component_rows.append(
                _fit_error_summary(
                    label=str(label),
                    assignment=str(assignment),
                    component=component,
                    y=y,
                    pred=pred,
                    weights=weights,
                    coefficients=coef,
                    basis_count=basis.shape[1],
                )
            )
            coef_frame = basis_meta.copy()
            coef_frame.insert(0, "component", component)
            coef_frame.insert(0, "assignment_scope", ASSIGNMENT_SCOPES.get(str(assignment), "other_endpoint"))
            coef_frame.insert(0, "assignment", str(assignment))
            coef_frame.insert(0, "label", str(label))
            coef_frame["coefficient"] = coef
            coefficient_frames.append(coef_frame)

        fit = frame.copy()
        for component, column in FIELD_COLUMNS.items():
            fit[f"target_{column}"] = fit[column].astype(float)
            fit[column] = predictions[component]
            fit[f"fit_error_{column}"] = fit[column] - fit[f"target_{column}"]
        fit["sector_description"] = "Finite smooth endpoint-J basis-family fit to the demanded intermediate target."
        fit = _derive_sector_columns(fit)
        fit_frames.append(fit)
        assignment_rows.append(_assignment_summary(frame, fit, str(label), str(assignment), basis.shape[1]))

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
            "residual_zone",
            "volume_weight",
            "sector",
            "assignment",
        ]
        present = [col for col in point_cols if col in fit.columns]
        extra = [
            "target_sector_rho",
            "target_sector_p_l",
            "target_sector_j_l",
            "target_sector_p_omega",
            "sector_rho",
            "sector_p_l",
            "sector_j_l",
            "sector_p_omega",
            "fit_error_sector_rho",
            "fit_error_sector_p_l",
            "fit_error_sector_j_l",
            "fit_error_sector_p_omega",
            "sector_selected_null_deficit_density_volume",
        ]
        point_frames.append(fit[present + extra].copy())

    fitted = pd.concat(fit_frames, ignore_index=True) if fit_frames else pd.DataFrame()
    conservation = (
        build_endpoint_j_conservation_tables(fitted, source_name="finite_endpoint_family_fit")["summary"]
        if not fitted.empty
        else pd.DataFrame()
    )
    return {
        "assignment_summary": pd.DataFrame(assignment_rows),
        "component_summary": pd.DataFrame(component_rows),
        "coefficients": pd.concat(coefficient_frames, ignore_index=True) if coefficient_frames else pd.DataFrame(),
        "point_fit": pd.concat(point_frames, ignore_index=True) if point_frames else pd.DataFrame(),
        "fit_sector_stress": fitted,
        "fit_conservation_summary": conservation,
    }


def _load_intermediate_sectors(intermediate_dir: Path) -> tuple[pd.DataFrame, dict[str, Any], Path]:
    manifest_path = intermediate_dir / "intermediate_source_model_manifest.json"
    manifest: dict[str, Any] = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        stress_value = manifest.get("files", {}).get("point_sector_stress", "intermediate_source_point_sector_stress.csv")
        stress_path = resolve_manifest_path(intermediate_dir, stress_value)
    else:
        stress_path = intermediate_dir / "intermediate_source_point_sector_stress.csv"
    return pd.read_csv(stress_path), manifest, stress_path


def build_endpoint_j_family_fit(
    intermediate_dir: Path,
    *,
    labels: list[str] | None = None,
    s_centers: int = 8,
    l_centers: int = 6,
    width_multiplier: float = 1.25,
    ridge: float = 1.0e-8,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    sectors, manifest, stress_path = _load_intermediate_sectors(intermediate_dir)
    outputs = build_endpoint_j_family_fit_tables(
        sectors,
        labels=labels,
        s_centers=s_centers,
        l_centers=l_centers,
        width_multiplier=width_multiplier,
        ridge=ridge,
    )
    metadata = {
        "intermediate_dir": str(intermediate_dir),
        "intermediate_manifest_model": manifest.get("model", ""),
        "point_sector_stress": str(stress_path),
        "point_sector_stress_sha256": sha256_file(stress_path),
        "labels": labels or sorted(sectors["label"].astype(str).unique().tolist()),
        "basis": {
            "kind": "assignment_local_gaussian_rbf_plus_uniform",
            "s_centers": int(s_centers),
            "l_centers": int(l_centers),
            "width_multiplier": float(width_multiplier),
            "ridge": float(ridge),
        },
        "caveat": (
            "Finite anisotropic endpoint-source family fit. This fits smooth, finite-width "
            "basis envelopes to the demanded J stress components and then reruns the endpoint "
            "conservation proxy. It is not a matter Lagrangian, an energy-condition proof, "
            "or a covariant conservation solve."
        ),
    }
    return outputs, metadata


def write_endpoint_j_family_fit_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "assignment_summary": outdir / "endpoint_j_family_assignment_summary.csv",
        "component_summary": outdir / "endpoint_j_family_component_summary.csv",
        "coefficients": outdir / "endpoint_j_family_coefficients.csv",
        "point_fit": outdir / "endpoint_j_family_point_fit.csv",
        "fit_sector_stress": outdir / "endpoint_j_family_sector_stress.csv",
        "fit_conservation_summary": outdir / "endpoint_j_family_conservation_summary.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "endpoint_j_family_fit_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
