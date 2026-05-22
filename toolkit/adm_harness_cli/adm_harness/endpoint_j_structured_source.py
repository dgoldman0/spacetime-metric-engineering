from __future__ import annotations

import itertools
import json
import math
from dataclasses import dataclass
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
FIELD_NAMES = tuple(FIELD_COLUMNS.keys())
FIELD_SOURCE_COLUMNS = tuple(FIELD_COLUMNS.values())
ASSIGNMENTS = (SUPPORT_ASSIGNMENT, RESET_ASSIGNMENT)
EPS = 1.0e-30


@dataclass(frozen=True)
class StructuredFitSpec:
    mode_count: int
    s_centers: int
    l_centers: int
    width_multiplier: float
    ridge: float
    edge_tail_count: int


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
    spec: StructuredFitSpec,
    conservation_points: pd.DataFrame | None,
) -> tuple[np.ndarray, pd.DataFrame]:
    s_values = frame["s"].astype(float).to_numpy()
    l_values = frame["l"].astype(float).to_numpy()
    s_grid = _centers(frame["s"], spec.s_centers)
    l_grid = _centers(frame["l"], spec.l_centers)
    sigma_s = _sigma(s_grid, frame["s"], spec.width_multiplier)
    sigma_l = _sigma(l_grid, frame["l"], spec.width_multiplier)

    columns: list[np.ndarray] = [np.ones(len(frame), dtype=float)]
    meta: list[dict[str, Any]] = [{
        "basis_name": "assignment_uniform",
        "basis_kind": "broad_assignment",
        "center_s": float("nan"),
        "center_l": float("nan"),
        "sigma_s": float("nan"),
        "sigma_l": float("nan"),
    }]

    for center_s in s_grid:
        for center_l in l_grid:
            columns.append(_gaussian(s_values, l_values, float(center_s), float(center_l), sigma_s, sigma_l))
            meta.append({
                "basis_name": f"grid_s{center_s:.6g}_l{center_l:.6g}",
                "basis_kind": "finite_grid",
                "center_s": float(center_s),
                "center_l": float(center_l),
                "sigma_s": sigma_s,
                "sigma_l": sigma_l,
            })

    if conservation_points is not None and spec.edge_tail_count > 0:
        tail = conservation_points.sort_values(
            ["conservation_residual_norm", "sector_selected_null_deficit_density_volume"],
            ascending=[False, False],
            na_position="last",
        ).drop_duplicates(["s", "l"]).head(int(spec.edge_tail_count))
        tail_sigma_s = max(sigma_s * 0.45, EPS)
        tail_sigma_l = max(sigma_l * 0.45, EPS)
        for _, row in tail.iterrows():
            center_s = float(row["s"])
            center_l = float(row["l"])
            columns.append(_gaussian(s_values, l_values, center_s, center_l, tail_sigma_s, tail_sigma_l))
            meta.append({
                "basis_name": f"edge_tail_s{center_s:.6g}_l{center_l:.6g}",
                "basis_kind": "edge_tail_counterterm",
                "center_s": center_s,
                "center_l": center_l,
                "sigma_s": tail_sigma_s,
                "sigma_l": tail_sigma_l,
            })

    basis = np.column_stack(columns)
    peaks = np.max(np.abs(basis), axis=0)
    peaks = np.where(peaks > 0.0, peaks, 1.0)
    return basis / peaks, pd.DataFrame(meta)


def _gaussian(
    s_values: np.ndarray,
    l_values: np.ndarray,
    center_s: float,
    center_l: float,
    sigma_s: float,
    sigma_l: float,
) -> np.ndarray:
    return np.exp(
        -0.5 * (
            np.square((s_values - center_s) / max(sigma_s, EPS))
            + np.square((l_values - center_l) / max(sigma_l, EPS))
        )
    )


def _component_scales(target: np.ndarray, weights: np.ndarray) -> np.ndarray:
    scales: list[float] = []
    for idx in range(target.shape[1]):
        values = np.abs(target[:, idx])
        denom = float(np.sum(weights))
        mean = float(np.sum(values * weights) / denom) if denom > 0.0 else float(np.mean(values))
        rms = float(math.sqrt(np.sum(np.square(values) * weights) / denom)) if denom > 0.0 else float(np.sqrt(np.mean(np.square(values))))
        scale = max(mean, rms * 0.5, float(np.max(values)) * 1.0e-3, 1.0e-12)
        scales.append(scale)
    return np.array(scales, dtype=float)


def _stress_vectors(target: np.ndarray, weights: np.ndarray, mode_count: int) -> np.ndarray:
    scales = _component_scales(target, weights)
    weighted = (target / scales) * np.sqrt(np.clip(weights, 0.0, np.inf))[:, None]
    if not np.isfinite(weighted).all() or np.allclose(weighted, 0.0):
        vectors = np.eye(len(FIELD_NAMES), dtype=float)
    else:
        _u, _s, vh = np.linalg.svd(weighted, full_matrices=False)
        vectors = vh[: max(1, min(int(mode_count), len(FIELD_NAMES)))] * scales
    normalized: list[np.ndarray] = []
    for vector in vectors:
        denom = float(np.max(np.abs(vector)))
        if denom <= 0.0 or not math.isfinite(denom):
            continue
        out = vector / denom
        peak = int(np.argmax(np.abs(out)))
        if out[peak] < 0.0:
            out = -out
        normalized.append(out)
    return np.vstack(normalized) if normalized else np.eye(1, len(FIELD_NAMES), dtype=float)


def _design_matrix(basis: np.ndarray, vectors: np.ndarray) -> np.ndarray:
    rows = basis.shape[0]
    cols: list[np.ndarray] = []
    for basis_idx in range(basis.shape[1]):
        for mode_idx in range(vectors.shape[0]):
            block = basis[:, basis_idx][:, None] * vectors[mode_idx][None, :]
            cols.append(block.reshape(rows * len(FIELD_NAMES)))
    return np.column_stack(cols)


def _ridge_fit(design: np.ndarray, y: np.ndarray, row_weights: np.ndarray, ridge: float) -> np.ndarray:
    w = np.sqrt(np.clip(row_weights.astype(float), 0.0, np.inf))
    aw = design * w[:, None]
    yw = y.astype(float) * w
    lhs = aw.T @ aw
    scale = float(np.trace(lhs) / max(lhs.shape[0], 1))
    lam = float(ridge) * scale if scale > 0.0 else float(ridge)
    lhs = lhs + lam * np.eye(lhs.shape[0])
    rhs = aw.T @ yw
    return np.linalg.solve(lhs, rhs)


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


def _fit_one_assignment(
    frame: pd.DataFrame,
    *,
    spec: StructuredFitSpec,
    conservation_points: pd.DataFrame | None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray]:
    local = frame.copy().reset_index(drop=True)
    target = local.loc[:, FIELD_SOURCE_COLUMNS].astype(float).to_numpy()
    weights = local["volume_weight"].astype(float).to_numpy()
    basis, basis_meta = _basis_matrix(local, spec=spec, conservation_points=conservation_points)
    vectors = _stress_vectors(target, weights, int(spec.mode_count))
    design = _design_matrix(basis, vectors)
    scales = _component_scales(target, weights)
    y = target.reshape(target.shape[0] * target.shape[1])
    row_weights = np.repeat(weights, len(FIELD_NAMES)) / np.tile(np.square(scales), target.shape[0])
    coefficients = _ridge_fit(design, y, row_weights, float(spec.ridge))
    pred = (design @ coefficients).reshape(target.shape[0], target.shape[1])

    fit = local.copy()
    for idx, column in enumerate(FIELD_SOURCE_COLUMNS):
        fit[f"target_{column}"] = fit[column].astype(float)
        fit[column] = pred[:, idx]
        fit[f"fit_error_{column}"] = fit[column] - fit[f"target_{column}"]
    fit["sector_description"] = "Structured finite endpoint-J source model with coupled stress-vector modes."
    fit = _derive_sector_columns(fit)

    coeff_rows: list[dict[str, Any]] = []
    for basis_idx, basis_row in basis_meta.iterrows():
        for mode_idx, vector in enumerate(vectors):
            coeff_index = int(basis_idx) * vectors.shape[0] + mode_idx
            coeff_rows.append({
                "basis_name": basis_row["basis_name"],
                "basis_kind": basis_row["basis_kind"],
                "center_s": _finite(basis_row["center_s"], float("nan")),
                "center_l": _finite(basis_row["center_l"], float("nan")),
                "sigma_s": _finite(basis_row["sigma_s"], float("nan")),
                "sigma_l": _finite(basis_row["sigma_l"], float("nan")),
                "mode_index": int(mode_idx),
                "coefficient": float(coefficients[coeff_index]),
                "mode_rho": float(vector[0]),
                "mode_p_l": float(vector[1]),
                "mode_j_l": float(vector[2]),
                "mode_p_omega": float(vector[3]),
            })
    mode_rows = []
    for mode_idx, vector in enumerate(vectors):
        mode_rows.append({
            "mode_index": int(mode_idx),
            "mode_rho": float(vector[0]),
            "mode_p_l": float(vector[1]),
            "mode_j_l": float(vector[2]),
            "mode_p_omega": float(vector[3]),
        })
    return fit, pd.DataFrame(coeff_rows), pd.DataFrame(mode_rows), coefficients


def _component_summary(label: str, assignment: str, target: pd.DataFrame, fit: pd.DataFrame, coefficients: np.ndarray) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    weights = target["volume_weight"].astype(float).to_numpy()
    weight_sum = float(np.sum(weights))
    coeff_abs = np.abs(coefficients)
    coeff_l2_den = float(np.sum(np.square(coeff_abs)))
    effective_count = float(np.square(coeff_abs.sum()) / coeff_l2_den) if coeff_l2_den > 0.0 else float("nan")
    for component, column in FIELD_COLUMNS.items():
        y = target[column].astype(float).to_numpy()
        pred = fit[column].astype(float).to_numpy()
        err = pred - y
        target_l1 = float(np.sum(np.abs(y) * weights))
        error_l1 = float(np.sum(np.abs(err) * weights))
        mean_target = _safe_ratio(target_l1, weight_sum)
        rows.append({
            "label": label,
            "assignment": assignment,
            "assignment_scope": ASSIGNMENT_SCOPES.get(assignment, "other_endpoint"),
            "component": component,
            "weighted_target_l1": target_l1,
            "weighted_error_l1": error_l1,
            "normalized_l1_error": _safe_ratio(error_l1, target_l1),
            "weighted_rmse": float(math.sqrt(np.sum(np.square(err) * weights) / weight_sum)) if weight_sum > 0.0 else float("nan"),
            "max_abs_error": float(np.max(np.abs(err))) if len(err) else float("nan"),
            "mean_abs_target_density": mean_target,
            "peak_abs_target_density": float(np.max(np.abs(y))) if len(y) else float("nan"),
            "max_abs_coefficient": float(np.max(coeff_abs)) if len(coeff_abs) else float("nan"),
            "effective_coefficient_count": effective_count,
            "max_coeff_to_mean_target": _safe_ratio(float(np.max(coeff_abs)) if len(coeff_abs) else 0.0, mean_target),
        })
    return pd.DataFrame(rows)


def _assignment_summary(
    label: str,
    assignment: str,
    target: pd.DataFrame,
    fit: pd.DataFrame,
    coefficients: np.ndarray,
    spec: StructuredFitSpec,
) -> dict[str, Any]:
    live = _bool_series(fit["inside_packet_live"])
    coeff_abs = np.abs(coefficients)
    row = {
        "label": label,
        "assignment": assignment,
        "assignment_scope": ASSIGNMENT_SCOPES.get(assignment, "other_endpoint"),
        "rows": int(len(fit)),
        "mode_count": int(spec.mode_count),
        "s_centers": int(spec.s_centers),
        "l_centers": int(spec.l_centers),
        "width_multiplier": float(spec.width_multiplier),
        "ridge": float(spec.ridge),
        "edge_tail_count": int(spec.edge_tail_count),
        "target_selected_null_deficit": float(target["sector_selected_null_deficit_density_volume"].sum()),
        "fit_selected_null_deficit": float(fit["sector_selected_null_deficit_density_volume"].sum()),
        "target_abs_current": float(target["sector_abs_current_density_volume"].sum()),
        "fit_abs_current": float(fit["sector_abs_current_density_volume"].sum()),
        "target_abs_pomega": float(target["sector_abs_pomega_density_volume"].sum()),
        "fit_abs_pomega": float(fit["sector_abs_pomega_density_volume"].sum()),
        "fit_live_rows": int(live.sum()),
        "fit_live_selected_null_deficit": float(fit.loc[live, "sector_selected_null_deficit_density_volume"].sum()),
        "max_abs_coefficient": float(np.max(coeff_abs)) if len(coeff_abs) else float("nan"),
        "coefficient_l1": float(np.sum(coeff_abs)),
        "coefficient_l2": float(math.sqrt(float(np.sum(np.square(coefficients))))),
    }
    row["fit_selected_ratio"] = _safe_ratio(row["fit_selected_null_deficit"], row["target_selected_null_deficit"])
    row["fit_current_ratio"] = _safe_ratio(row["fit_abs_current"], row["target_abs_current"])
    row["fit_pomega_ratio"] = _safe_ratio(row["fit_abs_pomega"], row["target_abs_pomega"])
    return row


def _score_candidate(
    assignment: str,
    assignment_row: dict[str, Any],
    component_summary: pd.DataFrame,
    *,
    overburden_weight: float,
    coefficient_weight: float,
) -> float:
    mean_error = float(component_summary["normalized_l1_error"].astype(float).replace([np.inf, -np.inf], np.nan).mean())
    selected_excess = max(_finite(assignment_row.get("fit_selected_ratio"), 0.0) - 1.0, 0.0)
    current_excess = max(_finite(assignment_row.get("fit_current_ratio"), 0.0) - 1.0, 0.0)
    pomega_excess = max(_finite(assignment_row.get("fit_pomega_ratio"), 0.0) - 1.0, 0.0)
    overburden = selected_excess * selected_excess + current_excess * current_excess + pomega_excess * pomega_excess
    coeff_penalty = math.log10(1.0 + max(_finite(assignment_row.get("max_abs_coefficient"), 0.0), 0.0))
    live_penalty = 1.0e6 if int(assignment_row.get("fit_live_rows", 0)) > 0 else 0.0
    support_multiplier = 1.0 if assignment == SUPPORT_ASSIGNMENT else 0.35
    return float(mean_error + support_multiplier * float(overburden_weight) * overburden + coefficient_weight * coeff_penalty + live_penalty)


def _candidate_specs(
    *,
    s_centers: int,
    l_centers: int,
    mode_counts: list[int],
    width_multipliers: list[float],
    ridges: list[float],
    edge_tail_counts: list[int],
) -> list[StructuredFitSpec]:
    return [
        StructuredFitSpec(
            mode_count=int(mode_count),
            s_centers=int(s_centers),
            l_centers=int(l_centers),
            width_multiplier=float(width),
            ridge=float(ridge),
            edge_tail_count=int(edge_tail),
        )
        for mode_count, width, ridge, edge_tail in itertools.product(
            mode_counts,
            width_multipliers,
            ridges,
            edge_tail_counts,
        )
    ]


def build_structured_endpoint_j_source_tables(
    sectors: pd.DataFrame,
    *,
    labels: list[str] | None = None,
    s_centers: int = 8,
    l_centers: int = 6,
    mode_counts: list[int] | None = None,
    width_multipliers: list[float] | None = None,
    ridges: list[float] | None = None,
    edge_tail_counts: list[int] | None = None,
    overburden_weight: float = 10.0,
    coefficient_weight: float = 0.02,
) -> dict[str, pd.DataFrame]:
    selected = sectors.loc[sectors["sector"].astype(str) == J_SECTOR].copy()
    if labels:
        label_set = {str(label) for label in labels}
        selected = selected.loc[selected["label"].astype(str).isin(label_set)].copy()

    specs = _candidate_specs(
        s_centers=s_centers,
        l_centers=l_centers,
        mode_counts=mode_counts or [2, 3, 4],
        width_multipliers=width_multipliers or [0.45, 0.65, 0.90],
        ridges=ridges or [1.0e-8, 1.0e-7, 1.0e-6],
        edge_tail_counts=edge_tail_counts or [0, 8],
    )
    conservation_points = build_endpoint_j_conservation_tables(selected, source_name="target")["point_residuals"]

    fit_frames: list[pd.DataFrame] = []
    coefficient_frames: list[pd.DataFrame] = []
    mode_frames: list[pd.DataFrame] = []
    point_frames: list[pd.DataFrame] = []
    assignment_rows: list[dict[str, Any]] = []
    component_frames: list[pd.DataFrame] = []
    candidate_rows: list[dict[str, Any]] = []

    for (label, assignment), group in selected.groupby(["label", "assignment"], sort=False, dropna=False):
        if str(assignment) not in ASSIGNMENTS:
            continue
        assignment_points = conservation_points.loc[
            (conservation_points["label"].astype(str) == str(label))
            & (conservation_points["assignment"].astype(str) == str(assignment))
        ].copy()
        best: tuple[float, StructuredFitSpec, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray] | None = None
        for spec in specs:
            fit, coeffs, modes, coefficients = _fit_one_assignment(
                group,
                spec=spec,
                conservation_points=assignment_points,
            )
            assignment_row = _assignment_summary(str(label), str(assignment), group, fit, coefficients, spec)
            comp = _component_summary(str(label), str(assignment), group, fit, coefficients)
            score = _score_candidate(
                str(assignment),
                assignment_row,
                comp,
                overburden_weight=overburden_weight,
                coefficient_weight=coefficient_weight,
            )
            candidate_row = dict(assignment_row)
            candidate_row.update({
                "candidate_score": score,
                "mean_component_normalized_l1": float(comp["normalized_l1_error"].mean()),
            })
            candidate_rows.append(candidate_row)
            if best is None or score < best[0]:
                best = (score, spec, fit, coeffs, modes, comp, coefficients)
        if best is None:
            continue
        score, spec, fit, coeffs, modes, comp, coefficients = best
        final_assignment = _assignment_summary(str(label), str(assignment), group, fit, coefficients, spec)
        final_assignment["candidate_score"] = score
        assignment_rows.append(final_assignment)
        component_frames.append(comp)
        coeffs.insert(0, "assignment_scope", ASSIGNMENT_SCOPES.get(str(assignment), "other_endpoint"))
        coeffs.insert(0, "assignment", str(assignment))
        coeffs.insert(0, "label", str(label))
        coefficient_frames.append(coeffs)
        modes.insert(0, "assignment_scope", ASSIGNMENT_SCOPES.get(str(assignment), "other_endpoint"))
        modes.insert(0, "assignment", str(assignment))
        modes.insert(0, "label", str(label))
        mode_frames.append(modes)
        fit_frames.append(fit)
        point_frames.append(_point_fit_table(fit))

    fitted = pd.concat(fit_frames, ignore_index=True) if fit_frames else pd.DataFrame()
    conservation = (
        build_endpoint_j_conservation_tables(fitted, source_name="structured_endpoint_source")["summary"]
        if not fitted.empty
        else pd.DataFrame()
    )
    return {
        "assignment_summary": pd.DataFrame(assignment_rows),
        "component_summary": pd.concat(component_frames, ignore_index=True) if component_frames else pd.DataFrame(),
        "candidate_scan": pd.DataFrame(candidate_rows),
        "mode_vectors": pd.concat(mode_frames, ignore_index=True) if mode_frames else pd.DataFrame(),
        "coefficients": pd.concat(coefficient_frames, ignore_index=True) if coefficient_frames else pd.DataFrame(),
        "point_fit": pd.concat(point_frames, ignore_index=True) if point_frames else pd.DataFrame(),
        "fit_sector_stress": fitted,
        "fit_conservation_summary": conservation,
    }


def _point_fit_table(fit: pd.DataFrame) -> pd.DataFrame:
    cols = [
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
    return fit.loc[:, [col for col in cols if col in fit.columns]].copy()


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


def build_structured_endpoint_j_source_model(
    intermediate_dir: Path,
    *,
    labels: list[str] | None = None,
    s_centers: int = 8,
    l_centers: int = 6,
    mode_counts: list[int] | None = None,
    width_multipliers: list[float] | None = None,
    ridges: list[float] | None = None,
    edge_tail_counts: list[int] | None = None,
    overburden_weight: float = 10.0,
    coefficient_weight: float = 0.02,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    sectors, manifest, stress_path = _load_intermediate_sectors(intermediate_dir)
    outputs = build_structured_endpoint_j_source_tables(
        sectors,
        labels=labels,
        s_centers=s_centers,
        l_centers=l_centers,
        mode_counts=mode_counts,
        width_multipliers=width_multipliers,
        ridges=ridges,
        edge_tail_counts=edge_tail_counts,
        overburden_weight=overburden_weight,
        coefficient_weight=coefficient_weight,
    )
    metadata = {
        "intermediate_dir": str(intermediate_dir),
        "intermediate_manifest_model": manifest.get("model", ""),
        "point_sector_stress": str(stress_path),
        "point_sector_stress_sha256": sha256_file(stress_path),
        "labels": labels or sorted(sectors["label"].astype(str).unique().tolist()),
        "selection_objective": {
            "overburden_weight": float(overburden_weight),
            "coefficient_weight": float(coefficient_weight),
            "overburden_terms": ["selected_null_deficit", "abs_current", "abs_pomega"],
        },
        "caveat": (
            "Structured finite endpoint-J source model. The fit uses assignment-local "
            "stress-vector modes and finite basis envelopes with explicit overburden "
            "penalties in model selection. This is not a matter Lagrangian or a full "
            "covariant conservation solve."
        ),
    }
    return outputs, metadata


def write_structured_endpoint_j_source_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "assignment_summary": outdir / "endpoint_j_structured_assignment_summary.csv",
        "component_summary": outdir / "endpoint_j_structured_component_summary.csv",
        "candidate_scan": outdir / "endpoint_j_structured_candidate_scan.csv",
        "mode_vectors": outdir / "endpoint_j_structured_mode_vectors.csv",
        "coefficients": outdir / "endpoint_j_structured_coefficients.csv",
        "point_fit": outdir / "endpoint_j_structured_point_fit.csv",
        "fit_sector_stress": outdir / "endpoint_j_structured_sector_stress.csv",
        "fit_conservation_summary": outdir / "endpoint_j_structured_conservation_summary.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "endpoint_j_structured_source_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
