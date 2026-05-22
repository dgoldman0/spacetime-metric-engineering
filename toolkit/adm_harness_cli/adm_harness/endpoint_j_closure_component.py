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
    SUPPORT_ASSIGNMENT,
    _enrich_assignment_frame,
    build_endpoint_j_conservation_tables,
)
from .endpoint_j_structured_source import FIELD_COLUMNS, FIELD_NAMES, _derive_sector_columns
from .source_ledger import sha256_file, write_manifest
from .source_screening import resolve_manifest_path


FIELD_SOURCE_COLUMNS = tuple(FIELD_COLUMNS.values())
EPS = 1.0e-30


@dataclass(frozen=True)
class ClosureSpec:
    mode_count: int
    center_count: int
    width_multiplier: float
    ridge: float
    conservation_weight: float
    angular_weight: float


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


def _load_intermediate_target(intermediate_dir: Path) -> tuple[pd.DataFrame, dict[str, Any], Path]:
    manifest_path = intermediate_dir / "intermediate_source_model_manifest.json"
    manifest: dict[str, Any] = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        value = manifest.get("files", {}).get("point_sector_stress", "intermediate_source_point_sector_stress.csv")
        path = resolve_manifest_path(intermediate_dir, value)
    else:
        path = intermediate_dir / "intermediate_source_point_sector_stress.csv"
    return pd.read_csv(path), manifest, path


def _load_structured_fit(structured_source_dir: Path) -> tuple[pd.DataFrame, dict[str, Any], Path]:
    manifest_path = structured_source_dir / "endpoint_j_structured_source_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    value = manifest.get("files", {}).get("fit_sector_stress", "endpoint_j_structured_sector_stress.csv")
    path = resolve_manifest_path(structured_source_dir, value)
    return pd.read_csv(path), manifest, path


def _correction_target_frame(target: pd.DataFrame, base: pd.DataFrame, label: str) -> pd.DataFrame:
    keys = ["label", "point_index", "assignment"]
    target_support = target.loc[
        (target["label"].astype(str) == str(label))
        & (target["sector"].astype(str) == J_SECTOR)
        & (target["assignment"].astype(str) == SUPPORT_ASSIGNMENT)
    ].copy()
    base_support = base.loc[
        (base["label"].astype(str) == str(label))
        & (base["sector"].astype(str) == J_SECTOR)
        & (base["assignment"].astype(str) == SUPPORT_ASSIGNMENT)
    ].copy()
    merged = target_support.merge(
        base_support[keys + list(FIELD_SOURCE_COLUMNS)],
        on=keys,
        how="inner",
        suffixes=("_target", "_base"),
    )
    for column in FIELD_SOURCE_COLUMNS:
        merged[f"delta_{column}"] = merged[f"{column}_target"] - merged[f"{column}_base"]
        merged[column] = merged[f"{column}_base"]
        merged[f"target_{column}"] = merged[f"{column}_target"]
    return merged


def _top_centers(frame: pd.DataFrame, count: int) -> pd.DataFrame:
    base_like = _base_like_frame(frame)
    residuals = _enrich_assignment_frame(base_like)
    delta_cols = [f"delta_{column}" for column in FIELD_SOURCE_COLUMNS if f"delta_{column}" in residuals.columns]
    if delta_cols:
        delta_norm = np.sqrt(np.sum(np.square(residuals[delta_cols].astype(float).to_numpy()), axis=1))
        delta_peak = float(np.nanmax(delta_norm)) if len(delta_norm) else 0.0
        residuals["closure_center_rank"] = residuals["conservation_residual_norm"].fillna(0.0).astype(float)
        if delta_peak > 0.0 and math.isfinite(delta_peak):
            residuals["closure_center_rank"] += delta_norm / delta_peak
    else:
        residuals["closure_center_rank"] = residuals["conservation_residual_norm"].fillna(0.0).astype(float)
    ranked = residuals.sort_values(
        ["closure_center_rank", "conservation_residual_norm", "sector_selected_null_deficit_density_volume"],
        ascending=[False, False, False],
        na_position="last",
    ).drop_duplicates(["s", "l"])
    return ranked.head(max(1, int(count))).loc[:, ["s", "l", "conservation_residual_norm"]].reset_index(drop=True)


def _base_like_frame(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for column in FIELD_SOURCE_COLUMNS:
        out[column] = out[f"{column}_base"] if f"{column}_base" in out.columns else out[column]
    return _derive_sector_columns(out)


def _centers_and_basis(frame: pd.DataFrame, spec: ClosureSpec) -> tuple[np.ndarray, pd.DataFrame]:
    centers = _top_centers(frame, spec.center_count)
    s_values = frame["s"].astype(float).to_numpy()
    l_values = frame["l"].astype(float).to_numpy()
    s_span = max(float(frame["s"].max() - frame["s"].min()), 1.0)
    l_span = max(float(frame["l"].max() - frame["l"].min()), 1.0)
    sigma_s = max(s_span / max(int(spec.center_count), 1) * float(spec.width_multiplier), 1.0e-6)
    sigma_l = max(l_span / max(int(spec.center_count), 1) * float(spec.width_multiplier), 1.0e-6)
    columns: list[np.ndarray] = []
    rows: list[dict[str, Any]] = []
    for idx, row in centers.iterrows():
        center_s = float(row["s"])
        center_l = float(row["l"])
        values = np.exp(
            -0.5 * (
                np.square((s_values - center_s) / sigma_s)
                + np.square((l_values - center_l) / sigma_l)
            )
        )
        peak = float(np.max(np.abs(values))) if len(values) else 0.0
        columns.append(values / peak if peak > 0.0 else values)
        rows.append({
            "basis_name": f"closure_tail_{idx}_s{center_s:.6g}_l{center_l:.6g}",
            "center_s": center_s,
            "center_l": center_l,
            "sigma_s": sigma_s,
            "sigma_l": sigma_l,
            "source_residual_norm": _finite(row.get("conservation_residual_norm"), float("nan")),
        })
    return np.column_stack(columns), pd.DataFrame(rows)


def _stress_vectors(frame: pd.DataFrame, mode_count: int) -> np.ndarray:
    deltas = frame[[f"delta_{column}" for column in FIELD_SOURCE_COLUMNS]].astype(float).to_numpy()
    weights = frame["volume_weight"].astype(float).to_numpy()
    scales = []
    for idx in range(deltas.shape[1]):
        values = np.abs(deltas[:, idx])
        denom = float(weights.sum())
        rms = float(math.sqrt(np.sum(np.square(values) * weights) / denom)) if denom > 0.0 else float(np.sqrt(np.mean(np.square(values))))
        scales.append(max(rms, float(values.max()) * 1.0e-3, 1.0e-12))
    scaled = (deltas / np.array(scales)) * np.sqrt(np.clip(weights, 0.0, np.inf))[:, None]
    if not np.isfinite(scaled).all() or np.allclose(scaled, 0.0):
        vectors = np.eye(len(FIELD_NAMES), dtype=float)
    else:
        _u, _s, vh = np.linalg.svd(scaled, full_matrices=False)
        vectors = vh[: max(1, min(int(mode_count), len(FIELD_NAMES)))] * np.array(scales)
    normalized = []
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


def _design_field_block(basis: np.ndarray, vectors: np.ndarray) -> np.ndarray:
    rows = basis.shape[0]
    columns = []
    for basis_idx in range(basis.shape[1]):
        for vector in vectors:
            columns.append((basis[:, basis_idx][:, None] * vector[None, :]).reshape(rows * len(FIELD_NAMES)))
    return np.column_stack(columns)


def _column_residuals(template: pd.DataFrame, basis_column: np.ndarray, vector: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    frame = template.copy()
    for idx, column in enumerate(FIELD_SOURCE_COLUMNS):
        frame[column] = basis_column * vector[idx]
    frame = _derive_sector_columns(frame)
    enriched = _enrich_assignment_frame(frame)
    return (
        enriched["continuity_residual_density"].astype(float).to_numpy(),
        enriched["radial_momentum_residual_density"].astype(float).to_numpy(),
        enriched["angular_capacity_gradient_density"].astype(float).to_numpy(),
    )


def _design_residual_blocks(template: pd.DataFrame, basis: np.ndarray, vectors: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    continuity_cols = []
    radial_cols = []
    angular_cols = []
    for basis_idx in range(basis.shape[1]):
        for vector in vectors:
            cont, radial, angular = _column_residuals(template, basis[:, basis_idx], vector)
            continuity_cols.append(cont)
            radial_cols.append(radial)
            angular_cols.append(angular)
    return np.column_stack(continuity_cols), np.column_stack(radial_cols), np.column_stack(angular_cols)


def _fit_correction(frame: pd.DataFrame, spec: ClosureSpec) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray]:
    basis, basis_meta = _centers_and_basis(frame, spec)
    vectors = _stress_vectors(frame, spec.mode_count)
    field_design = _design_field_block(basis, vectors)
    target_delta = frame[[f"delta_{column}" for column in FIELD_SOURCE_COLUMNS]].astype(float).to_numpy()
    y_field = target_delta.reshape(target_delta.shape[0] * target_delta.shape[1])
    weights = frame["volume_weight"].astype(float).to_numpy()
    field_scales = np.array([
        max(float(np.sqrt(np.average(np.square(target_delta[:, idx]), weights=weights))), 1.0e-12)
        for idx in range(target_delta.shape[1])
    ])
    field_weights = np.repeat(weights, len(FIELD_NAMES)) / np.tile(np.square(field_scales), len(weights))

    template = frame.copy()
    for column in FIELD_SOURCE_COLUMNS:
        template[column] = 0.0
    template = _derive_sector_columns(template)
    cont_design, radial_design, angular_design = _design_residual_blocks(template, basis, vectors)
    base_enriched = _enrich_assignment_frame(_base_like_frame(frame))
    cont_target = -base_enriched["continuity_residual_density"].astype(float).to_numpy()
    radial_target = -base_enriched["radial_momentum_residual_density"].astype(float).to_numpy()
    angular_target = -base_enriched["angular_capacity_gradient_density"].astype(float).to_numpy()
    residual_scale = max(
        float(np.nanpercentile(np.abs(np.concatenate([cont_target, radial_target])), 90)),
        1.0e-12,
    )
    angular_scale = max(float(np.nanpercentile(np.abs(angular_target), 90)), 1.0e-12)

    design = np.vstack([
        field_design,
        cont_design,
        radial_design,
        angular_design,
    ])
    y = np.concatenate([y_field, cont_target, radial_target, angular_target])
    row_weights = np.concatenate([
        field_weights,
        np.full(len(cont_target), float(spec.conservation_weight) / (residual_scale * residual_scale)),
        np.full(len(radial_target), float(spec.conservation_weight) / (residual_scale * residual_scale)),
        np.full(len(angular_target), float(spec.angular_weight) / (angular_scale * angular_scale)),
    ])
    coefficients = _ridge_solve(design, y, row_weights, spec.ridge)
    correction = (field_design @ coefficients).reshape(target_delta.shape[0], target_delta.shape[1])

    out = frame.copy()
    for idx, column in enumerate(FIELD_SOURCE_COLUMNS):
        out[column] = out[f"{column}_base"] + correction[:, idx]
        out[f"closure_delta_{column}"] = correction[:, idx]
        out[f"fit_error_{column}"] = out[column] - out[f"{column}_target"]
    out["sector_description"] = "Structured endpoint-J source plus finite support-edge closure component."
    out = _derive_sector_columns(out)

    coeff_rows = []
    for basis_idx, basis_row in basis_meta.iterrows():
        for mode_idx, vector in enumerate(vectors):
            coeff_idx = int(basis_idx) * vectors.shape[0] + int(mode_idx)
            coeff_rows.append({
                "basis_name": basis_row["basis_name"],
                "center_s": _finite(basis_row["center_s"], float("nan")),
                "center_l": _finite(basis_row["center_l"], float("nan")),
                "sigma_s": _finite(basis_row["sigma_s"], float("nan")),
                "sigma_l": _finite(basis_row["sigma_l"], float("nan")),
                "source_residual_norm": _finite(basis_row["source_residual_norm"], float("nan")),
                "mode_index": int(mode_idx),
                "coefficient": float(coefficients[coeff_idx]),
                "mode_rho": float(vector[0]),
                "mode_p_l": float(vector[1]),
                "mode_j_l": float(vector[2]),
                "mode_p_omega": float(vector[3]),
            })
    mode_rows = [
        {
            "mode_index": int(idx),
            "mode_rho": float(vector[0]),
            "mode_p_l": float(vector[1]),
            "mode_j_l": float(vector[2]),
            "mode_p_omega": float(vector[3]),
        }
        for idx, vector in enumerate(vectors)
    ]
    return out, pd.DataFrame(coeff_rows), pd.DataFrame(mode_rows), coefficients


def _ridge_solve(design: np.ndarray, y: np.ndarray, row_weights: np.ndarray, ridge: float) -> np.ndarray:
    w = np.sqrt(np.clip(row_weights.astype(float), 0.0, np.inf))
    aw = design * w[:, None]
    yw = y * w
    lhs = aw.T @ aw
    scale = float(np.trace(lhs) / max(lhs.shape[0], 1))
    lam = float(ridge) * scale if scale > 0.0 else float(ridge)
    return np.linalg.solve(lhs + lam * np.eye(lhs.shape[0]), aw.T @ yw)


def _assignment_summary(label: str, target: pd.DataFrame, base: pd.DataFrame, fit: pd.DataFrame, coefficients: np.ndarray, spec: ClosureSpec, score: float) -> dict[str, Any]:
    live = _bool_series(fit["inside_packet_live"])
    coeff_abs = np.abs(coefficients)
    row = {
        "label": label,
        "assignment": SUPPORT_ASSIGNMENT,
        "assignment_scope": ASSIGNMENT_SCOPES[SUPPORT_ASSIGNMENT],
        "mode_count": int(spec.mode_count),
        "center_count": int(spec.center_count),
        "width_multiplier": float(spec.width_multiplier),
        "ridge": float(spec.ridge),
        "conservation_weight": float(spec.conservation_weight),
        "angular_weight": float(spec.angular_weight),
        "candidate_score": float(score),
        "target_selected_null_deficit": float(target["sector_selected_null_deficit_density_volume"].sum()),
        "base_selected_null_deficit": float(base["sector_selected_null_deficit_density_volume"].sum()),
        "fit_selected_null_deficit": float(fit["sector_selected_null_deficit_density_volume"].sum()),
        "target_abs_current": float(target["sector_abs_current_density_volume"].sum()),
        "base_abs_current": float(base["sector_abs_current_density_volume"].sum()),
        "fit_abs_current": float(fit["sector_abs_current_density_volume"].sum()),
        "target_abs_pomega": float(target["sector_abs_pomega_density_volume"].sum()),
        "base_abs_pomega": float(base["sector_abs_pomega_density_volume"].sum()),
        "fit_abs_pomega": float(fit["sector_abs_pomega_density_volume"].sum()),
        "fit_live_rows": int(live.sum()),
        "fit_live_selected_null_deficit": float(fit.loc[live, "sector_selected_null_deficit_density_volume"].sum()),
        "max_abs_coefficient": float(np.max(coeff_abs)) if len(coeff_abs) else float("nan"),
        "coefficient_l1": float(coeff_abs.sum()),
        "coefficient_l2": float(math.sqrt(float(np.sum(np.square(coefficients))))),
    }
    for prefix in ("base", "fit"):
        row[f"{prefix}_selected_ratio"] = _safe_ratio(row[f"{prefix}_selected_null_deficit"], row["target_selected_null_deficit"])
        row[f"{prefix}_current_ratio"] = _safe_ratio(row[f"{prefix}_abs_current"], row["target_abs_current"])
        row[f"{prefix}_pomega_ratio"] = _safe_ratio(row[f"{prefix}_abs_pomega"], row["target_abs_pomega"])
    return row


def _component_summary(label: str, target: pd.DataFrame, base: pd.DataFrame, fit: pd.DataFrame, coefficients: np.ndarray) -> pd.DataFrame:
    rows = []
    weights = target["volume_weight"].astype(float).to_numpy()
    weight_sum = float(weights.sum())
    coeff_abs = np.abs(coefficients)
    coeff_l2_den = float(np.sum(np.square(coeff_abs)))
    effective_count = float(np.square(coeff_abs.sum()) / coeff_l2_den) if coeff_l2_den > 0.0 else float("nan")
    for component, column in FIELD_COLUMNS.items():
        y = target[column].astype(float).to_numpy()
        base_y = base[column].astype(float).to_numpy()
        pred = fit[column].astype(float).to_numpy()
        for prefix, values in (("base", base_y), ("fit", pred)):
            err = values - y
            target_l1 = float(np.sum(np.abs(y) * weights))
            error_l1 = float(np.sum(np.abs(err) * weights))
            rows.append({
                "label": label,
                "assignment": SUPPORT_ASSIGNMENT,
                "assignment_scope": ASSIGNMENT_SCOPES[SUPPORT_ASSIGNMENT],
                "model": prefix,
                "component": component,
                "weighted_target_l1": target_l1,
                "weighted_error_l1": error_l1,
                "normalized_l1_error": _safe_ratio(error_l1, target_l1),
                "weighted_rmse": float(math.sqrt(np.sum(np.square(err) * weights) / weight_sum)) if weight_sum > 0.0 else float("nan"),
                "max_abs_error": float(np.max(np.abs(err))) if len(err) else float("nan"),
                "max_abs_coefficient": float(np.max(coeff_abs)) if len(coeff_abs) else float("nan"),
                "effective_coefficient_count": effective_count,
            })
    return pd.DataFrame(rows)


def _score_candidate(target: pd.DataFrame, fit: pd.DataFrame, conservation_summary: pd.DataFrame, coefficients: np.ndarray, overburden_weight: float, residual_weight: float, coefficient_weight: float) -> float:
    weights = target["volume_weight"].astype(float).to_numpy()
    errors = []
    for column in FIELD_SOURCE_COLUMNS:
        y = target[column].astype(float).to_numpy()
        pred = fit[column].astype(float).to_numpy()
        target_l1 = float(np.sum(np.abs(y) * weights))
        errors.append(_safe_ratio(float(np.sum(np.abs(pred - y) * weights)), target_l1))
    selected_ratio = _safe_ratio(float(fit["sector_selected_null_deficit_density_volume"].sum()), float(target["sector_selected_null_deficit_density_volume"].sum()))
    current_ratio = _safe_ratio(float(fit["sector_abs_current_density_volume"].sum()), float(target["sector_abs_current_density_volume"].sum()))
    pomega_ratio = _safe_ratio(float(fit["sector_abs_pomega_density_volume"].sum()), float(target["sector_abs_pomega_density_volume"].sum()))
    overburden = sum(max(_finite(value, 0.0) - 1.0, 0.0) ** 2 for value in (selected_ratio, current_ratio, pomega_ratio))
    support = conservation_summary.loc[conservation_summary["scope"].astype(str) == "support_edge"]
    residual = 0.0
    if not support.empty:
        row = support.iloc[0]
        residual = _finite(row.get("burden_weighted_mean_conservation_residual_norm"), 0.0)
        residual += 0.2 * max(_finite(row.get("peak_conservation_residual_norm"), 0.0) - 5.0, 0.0)
    coeff = math.log10(1.0 + float(np.max(np.abs(coefficients))) if len(coefficients) else 1.0)
    return float(np.nanmean(errors) + overburden_weight * overburden + residual_weight * residual + coefficient_weight * coeff)


def _candidate_specs(
    mode_counts: list[int] | None,
    center_counts: list[int] | None,
    width_multipliers: list[float] | None,
    ridges: list[float] | None,
    conservation_weights: list[float] | None,
    angular_weights: list[float] | None,
) -> list[ClosureSpec]:
    return [
        ClosureSpec(int(mode), int(center), float(width), float(ridge), float(cw), float(aw))
        for mode, center, width, ridge, cw, aw in itertools.product(
            mode_counts or [1, 2],
            center_counts or [6, 10],
            width_multipliers or [0.55, 0.85],
            ridges or [1.0e-8, 1.0e-7, 1.0e-6],
            conservation_weights or [0.0, 0.5, 1.5, 4.0],
            angular_weights or [0.25, 1.0],
        )
    ]


def build_endpoint_j_closure_component_tables(
    target_sectors: pd.DataFrame,
    structured_fit: pd.DataFrame,
    *,
    labels: list[str] | None = None,
    mode_counts: list[int] | None = None,
    center_counts: list[int] | None = None,
    width_multipliers: list[float] | None = None,
    ridges: list[float] | None = None,
    conservation_weights: list[float] | None = None,
    angular_weights: list[float] | None = None,
    overburden_weight: float = 10.0,
    residual_weight: float = 1.0,
    coefficient_weight: float = 0.02,
) -> dict[str, pd.DataFrame]:
    selected_labels = labels or sorted(target_sectors["label"].astype(str).unique().tolist())
    specs = _candidate_specs(mode_counts, center_counts, width_multipliers, ridges, conservation_weights, angular_weights)
    final_frames = []
    coeff_frames = []
    mode_frames = []
    assignment_rows = []
    component_frames = []
    candidate_rows = []

    for label in selected_labels:
        frame = _correction_target_frame(target_sectors, structured_fit, str(label))
        if frame.empty:
            continue
        target_support = _derive_sector_columns(_target_like(frame))
        base_support = _base_like_frame(frame)
        best = None
        for spec in specs:
            fit, coeffs, modes, coefficients = _fit_correction(frame, spec)
            combined = _combined_fit(structured_fit, fit, str(label))
            conservation = build_endpoint_j_conservation_tables(combined, source_name="closure_component")["summary"]
            score = _score_candidate(
                target_support,
                fit,
                conservation,
                coefficients,
                overburden_weight=overburden_weight,
                residual_weight=residual_weight,
                coefficient_weight=coefficient_weight,
            )
            summary = _assignment_summary(str(label), target_support, base_support, fit, coefficients, spec, score)
            candidate_rows.append(summary)
            if best is None or score < best[0]:
                best = (score, spec, fit, coeffs, modes, coefficients)
        if best is None:
            continue
        score, spec, fit, coeffs, modes, coefficients = best
        final_frames.append(fit)
        assignment_rows.append(_assignment_summary(str(label), target_support, base_support, fit, coefficients, spec, score))
        component_frames.append(_component_summary(str(label), target_support, base_support, fit, coefficients))
        coeffs.insert(0, "label", str(label))
        coeff_frames.append(coeffs)
        modes.insert(0, "label", str(label))
        mode_frames.append(modes)

    support_fit = pd.concat(final_frames, ignore_index=True) if final_frames else pd.DataFrame()
    fit_sector = _replace_support_assignments(structured_fit, support_fit)
    conservation = build_endpoint_j_conservation_tables(fit_sector, source_name="closure_component")["summary"] if not fit_sector.empty else pd.DataFrame()
    return {
        "assignment_summary": pd.DataFrame(assignment_rows),
        "component_summary": pd.concat(component_frames, ignore_index=True) if component_frames else pd.DataFrame(),
        "candidate_scan": pd.DataFrame(candidate_rows),
        "mode_vectors": pd.concat(mode_frames, ignore_index=True) if mode_frames else pd.DataFrame(),
        "coefficients": pd.concat(coeff_frames, ignore_index=True) if coeff_frames else pd.DataFrame(),
        "support_point_fit": support_fit,
        "fit_sector_stress": fit_sector,
        "fit_conservation_summary": conservation,
    }


def _target_like(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for column in FIELD_SOURCE_COLUMNS:
        out[column] = out[f"{column}_target"]
    return out


def _combined_fit(structured_fit: pd.DataFrame, support_fit: pd.DataFrame, label: str) -> pd.DataFrame:
    return _replace_support_assignments(
        structured_fit.loc[structured_fit["label"].astype(str) == str(label)].copy(),
        support_fit,
    )


def _replace_support_assignments(structured_fit: pd.DataFrame, support_fit: pd.DataFrame) -> pd.DataFrame:
    if structured_fit.empty:
        return support_fit.copy()
    if support_fit.empty:
        return structured_fit.copy()
    keys = set(zip(support_fit["label"].astype(str), support_fit["point_index"].astype(int), support_fit["assignment"].astype(str)))
    keep_mask = [
        (str(row["label"]), int(row["point_index"]), str(row["assignment"])) not in keys
        for _, row in structured_fit.iterrows()
    ]
    combined = pd.concat([structured_fit.loc[keep_mask].copy(), support_fit.copy()], ignore_index=True)
    return combined.sort_values(["label", "point_index", "sector", "assignment"]).reset_index(drop=True)


def build_endpoint_j_closure_component(
    intermediate_dir: Path,
    structured_source_dir: Path,
    *,
    labels: list[str] | None = None,
    mode_counts: list[int] | None = None,
    center_counts: list[int] | None = None,
    width_multipliers: list[float] | None = None,
    ridges: list[float] | None = None,
    conservation_weights: list[float] | None = None,
    angular_weights: list[float] | None = None,
    overburden_weight: float = 10.0,
    residual_weight: float = 1.0,
    coefficient_weight: float = 0.02,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    target, target_manifest, target_path = _load_intermediate_target(intermediate_dir)
    structured, structured_manifest, structured_path = _load_structured_fit(structured_source_dir)
    outputs = build_endpoint_j_closure_component_tables(
        target,
        structured,
        labels=labels,
        mode_counts=mode_counts,
        center_counts=center_counts,
        width_multipliers=width_multipliers,
        ridges=ridges,
        conservation_weights=conservation_weights,
        angular_weights=angular_weights,
        overburden_weight=overburden_weight,
        residual_weight=residual_weight,
        coefficient_weight=coefficient_weight,
    )
    metadata = {
        "intermediate_dir": str(intermediate_dir),
        "structured_source_dir": str(structured_source_dir),
        "target_point_sector_stress": str(target_path),
        "target_point_sector_stress_sha256": sha256_file(target_path),
        "structured_fit_sector_stress": str(structured_path),
        "structured_fit_sector_stress_sha256": sha256_file(structured_path),
        "labels": labels or sorted(target["label"].astype(str).unique().tolist()),
        "target_model": target_manifest.get("model", ""),
        "structured_source_caveat": structured_manifest.get("caveat", ""),
        "selection_objective": {
            "overburden_weight": float(overburden_weight),
            "residual_weight": float(residual_weight),
            "coefficient_weight": float(coefficient_weight),
        },
        "caveat": (
            "Support-edge endpoint-J closure component layered onto the structured "
            "source fit. This is an effective finite source-family correction, not "
            "a matter Lagrangian or full covariant conservation solve."
        ),
    }
    return outputs, metadata


def write_endpoint_j_closure_component_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "assignment_summary": outdir / "endpoint_j_closure_assignment_summary.csv",
        "component_summary": outdir / "endpoint_j_closure_component_summary.csv",
        "candidate_scan": outdir / "endpoint_j_closure_candidate_scan.csv",
        "mode_vectors": outdir / "endpoint_j_closure_mode_vectors.csv",
        "coefficients": outdir / "endpoint_j_closure_coefficients.csv",
        "support_point_fit": outdir / "endpoint_j_closure_support_point_fit.csv",
        "fit_sector_stress": outdir / "endpoint_j_closure_sector_stress.csv",
        "fit_conservation_summary": outdir / "endpoint_j_closure_conservation_summary.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "endpoint_j_closure_component_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
