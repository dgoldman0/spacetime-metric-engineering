from __future__ import annotations

import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .endpoint_current_regulator import _load_fit_sector_stress
from .endpoint_medium_admissibility import build_admissibility_point_table
from .source_ledger import sha256_file, write_manifest


EPS = 1.0e-30


@dataclass(frozen=True)
class AngularResponseSpec:
    s_centers: int
    l_centers: int
    width_multiplier: float
    ridge: float


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
    if int(count) <= 1 or float(np.max(finite)) == float(np.min(finite)):
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


def _gaussian(s_values: np.ndarray, l_values: np.ndarray, center_s: float, center_l: float, sigma_s: float, sigma_l: float) -> np.ndarray:
    return np.exp(
        -0.5
        * (
            np.square((s_values - center_s) / max(sigma_s, EPS))
            + np.square((l_values - center_l) / max(sigma_l, EPS))
        )
    )


def _basis_matrix(frame: pd.DataFrame, spec: AngularResponseSpec) -> tuple[np.ndarray, pd.DataFrame]:
    s_values = frame["s"].astype(float).to_numpy()
    l_values = frame["l"].astype(float).to_numpy()
    s_grid = _centers(frame["s"], spec.s_centers)
    l_grid = _centers(frame["l"], spec.l_centers)
    sigma_s = _sigma(s_grid, frame["s"], spec.width_multiplier)
    sigma_l = _sigma(l_grid, frame["l"], spec.width_multiplier)
    columns: list[np.ndarray] = [np.ones(len(frame), dtype=float)]
    rows: list[dict[str, Any]] = [{
        "basis_name": "assignment_uniform",
        "basis_kind": "uniform",
        "center_s": float("nan"),
        "center_l": float("nan"),
        "sigma_s": float("nan"),
        "sigma_l": float("nan"),
    }]
    for center_s in s_grid:
        for center_l in l_grid:
            columns.append(_gaussian(s_values, l_values, float(center_s), float(center_l), sigma_s, sigma_l))
            rows.append({
                "basis_name": f"angular_response_s{center_s:.6g}_l{center_l:.6g}",
                "basis_kind": "finite_grid",
                "center_s": float(center_s),
                "center_l": float(center_l),
                "sigma_s": sigma_s,
                "sigma_l": sigma_l,
            })
    basis = np.column_stack(columns)
    peaks = np.max(np.abs(basis), axis=0)
    peaks = np.where(peaks > 0.0, peaks, 1.0)
    return basis / peaks, pd.DataFrame(rows)


def _ridge_fit(design: np.ndarray, y: np.ndarray, weights: np.ndarray, ridge: float) -> np.ndarray:
    w = np.sqrt(np.clip(weights.astype(float), 0.0, np.inf))
    aw = design * w[:, None]
    yw = y * w
    lhs = aw.T @ aw
    scale = float(np.trace(lhs) / max(lhs.shape[0], 1))
    lam = float(ridge) * scale if scale > 0.0 else float(ridge)
    return np.linalg.solve(lhs + lam * np.eye(lhs.shape[0]), aw.T @ yw)


def _candidate_specs(
    s_centers: list[int] | None,
    l_centers: list[int] | None,
    width_multipliers: list[float] | None,
    ridges: list[float] | None,
) -> list[AngularResponseSpec]:
    return [
        AngularResponseSpec(int(sc), int(lc), float(width), float(ridge))
        for sc, lc, width, ridge in itertools.product(
            s_centers or [8, 10, 12],
            l_centers or [6, 8],
            width_multipliers or [0.45, 0.65, 0.90],
            ridges or [1.0e-8, 1.0e-7, 1.0e-6],
        )
    ]


def _fit_assignment(frame: pd.DataFrame, spec: AngularResponseSpec) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    basis, basis_meta = _basis_matrix(frame, spec)
    y = frame["regulated_rest_frame_angular_pressure"].astype(float).to_numpy()
    weights = frame["volume_weight"].astype(float).to_numpy()
    coefficients = _ridge_fit(basis, y, weights, float(spec.ridge))
    pred = basis @ coefficients
    fit = frame.copy()
    fit["target_angular_pressure"] = y
    fit["fit_angular_pressure"] = pred
    fit["fit_error_angular_pressure"] = pred - y
    fit["fit_abs_error_angular_pressure"] = np.abs(pred - y)
    coeffs = basis_meta.copy()
    coeffs["coefficient"] = coefficients
    coeffs["s_centers"] = int(spec.s_centers)
    coeffs["l_centers"] = int(spec.l_centers)
    coeffs["width_multiplier"] = float(spec.width_multiplier)
    coeffs["ridge"] = float(spec.ridge)
    return fit, coeffs, coefficients


def _assignment_summary(label: str, assignment: str, fit: pd.DataFrame, coefficients: np.ndarray, spec: AngularResponseSpec, score: float) -> dict[str, Any]:
    weights = fit["volume_weight"].astype(float).to_numpy()
    y = fit["target_angular_pressure"].astype(float).to_numpy()
    err = fit["fit_error_angular_pressure"].astype(float).to_numpy()
    coeff_abs = np.abs(coefficients)
    coeff_l2 = float(np.sum(np.square(coeff_abs)))
    live = _bool_series(fit["inside_packet_live"])
    angular_watch = fit["angular_inertia_negative"].astype(bool) if "angular_inertia_negative" in fit else pd.Series(False, index=fit.index)
    target_l1 = float(np.sum(np.abs(y) * weights))
    err_l1 = float(np.sum(np.abs(err) * weights))
    angular_watch_target_l1 = float(np.sum(np.abs(y[angular_watch.to_numpy()]) * weights[angular_watch.to_numpy()]))
    angular_watch_err_l1 = float(np.sum(np.abs(err[angular_watch.to_numpy()]) * weights[angular_watch.to_numpy()]))
    angular_watch_norm = _safe_ratio(angular_watch_err_l1, angular_watch_target_l1) if angular_watch_target_l1 > 0.0 else 0.0
    return {
        "label": label,
        "assignment": assignment,
        "rows": int(len(fit)),
        "s_centers": int(spec.s_centers),
        "l_centers": int(spec.l_centers),
        "width_multiplier": float(spec.width_multiplier),
        "ridge": float(spec.ridge),
        "candidate_score": float(score),
        "weighted_target_l1": target_l1,
        "weighted_error_l1": err_l1,
        "normalized_l1_error": _safe_ratio(err_l1, target_l1),
        "weighted_rmse": float(math.sqrt(np.sum(np.square(err) * weights) / np.sum(weights))) if np.sum(weights) > 0.0 else float("nan"),
        "max_abs_error": float(np.max(np.abs(err))) if len(err) else float("nan"),
        "live_rows": int(live.sum()),
        "angular_watch_rows": int(angular_watch.sum()),
        "angular_watch_normalized_l1_error": angular_watch_norm,
        "max_abs_coefficient": float(np.max(coeff_abs)) if len(coeff_abs) else float("nan"),
        "coefficient_l1": float(np.sum(coeff_abs)),
        "coefficient_l2": float(math.sqrt(coeff_l2)),
        "effective_coefficient_count": float(np.square(np.sum(coeff_abs)) / coeff_l2) if coeff_l2 > 0.0 else float("nan"),
    }


def _score(summary: dict[str, Any], coefficient_weight: float) -> float:
    coeff = math.log10(1.0 + max(_finite(summary.get("max_abs_coefficient"), 0.0), 0.0))
    watch = _finite(summary.get("angular_watch_normalized_l1_error"), 0.0)
    return float(_finite(summary.get("normalized_l1_error"), 1.0) + 0.25 * watch + coefficient_weight * coeff)


def build_constructive_medium_probe_tables(
    fit_sector_stress: pd.DataFrame,
    *,
    source_name: str = "endpoint_j_frozen_source",
    regulator_safety_factor: float = 1.10,
    normalized_l1_gate: float = 0.12,
    angular_watch_l1_gate: float = 0.16,
    coefficient_gate: float = 1.0,
    coefficient_weight: float = 0.02,
    s_centers: list[int] | None = None,
    l_centers: list[int] | None = None,
    width_multipliers: list[float] | None = None,
    ridges: list[float] | None = None,
) -> dict[str, pd.DataFrame]:
    points = build_admissibility_point_table(fit_sector_stress, regulator_safety_factor=regulator_safety_factor)
    specs = _candidate_specs(s_centers, l_centers, width_multipliers, ridges)
    point_frames: list[pd.DataFrame] = []
    coeff_frames: list[pd.DataFrame] = []
    assignment_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []

    for (label, assignment), group in points.groupby(["label", "assignment"], sort=False, dropna=False):
        best: tuple[float, pd.DataFrame, pd.DataFrame, np.ndarray, AngularResponseSpec, dict[str, Any]] | None = None
        for spec in specs:
            fit, coeffs, coefficients = _fit_assignment(group, spec)
            summary = _assignment_summary(str(label), str(assignment), fit, coefficients, spec, score=0.0)
            score = _score(summary, coefficient_weight)
            summary["candidate_score"] = score
            candidate_rows.append(summary)
            if best is None or score < best[0]:
                best = (score, fit, coeffs, coefficients, spec, summary)
        if best is None:
            continue
        score, fit, coeffs, coefficients, spec, summary = best
        summary = _assignment_summary(str(label), str(assignment), fit, coefficients, spec, score)
        assignment_rows.append(summary)
        coeffs.insert(0, "assignment", str(assignment))
        coeffs.insert(0, "label", str(label))
        coeff_frames.append(coeffs)
        point_frames.append(fit)

    assignment_summary = pd.DataFrame(assignment_rows)
    if assignment_summary.empty:
        decision = pd.DataFrame([{
            "source_name": source_name,
            "constructive_status": "missing_assignment_fit",
            "passes_internal_response_probe": False,
        }])
    else:
        pass_mask = (
            (assignment_summary["normalized_l1_error"].astype(float) <= float(normalized_l1_gate))
            & (assignment_summary["angular_watch_normalized_l1_error"].astype(float) <= float(angular_watch_l1_gate))
            & (assignment_summary["max_abs_coefficient"].astype(float) <= float(coefficient_gate))
            & (assignment_summary["live_rows"].astype(int) == 0)
        )
        decision = pd.DataFrame([{
            "source_name": source_name,
            "constructive_status": "internal_angular_response_plausible" if bool(pass_mask.all()) else "internal_angular_response_watch",
            "passes_internal_response_probe": bool(pass_mask.all()),
            "worst_normalized_l1_error": float(assignment_summary["normalized_l1_error"].astype(float).max()),
            "worst_angular_watch_l1_error": float(assignment_summary["angular_watch_normalized_l1_error"].astype(float).max()),
            "max_abs_coefficient": float(assignment_summary["max_abs_coefficient"].astype(float).max()),
            "normalized_l1_gate": float(normalized_l1_gate),
            "angular_watch_l1_gate": float(angular_watch_l1_gate),
            "coefficient_gate": float(coefficient_gate),
            "live_rows": int(assignment_summary["live_rows"].astype(int).sum()),
            "decision_read": (
                "finite smooth internal angular response can carry the angular watch without a new component"
                if bool(pass_mask.all())
                else "first internal angular response fit is not yet strong enough to rule out a new component"
            ),
        }])

    return {
        "point_fit": pd.concat(point_frames, ignore_index=True) if point_frames else pd.DataFrame(),
        "assignment_summary": assignment_summary,
        "candidate_scan": pd.DataFrame(candidate_rows),
        "coefficients": pd.concat(coeff_frames, ignore_index=True) if coeff_frames else pd.DataFrame(),
        "feasibility_decision": decision,
    }


def build_constructive_medium_probe(
    fit_dir: Path,
    *,
    source_name: str = "endpoint_j_frozen_source",
    regulator_safety_factor: float = 1.10,
    normalized_l1_gate: float = 0.12,
    angular_watch_l1_gate: float = 0.16,
    coefficient_gate: float = 1.0,
    coefficient_weight: float = 0.02,
    s_centers: list[int] | None = None,
    l_centers: list[int] | None = None,
    width_multipliers: list[float] | None = None,
    ridges: list[float] | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    fit, manifest, fit_path = _load_fit_sector_stress(fit_dir)
    outputs = build_constructive_medium_probe_tables(
        fit,
        source_name=source_name,
        regulator_safety_factor=regulator_safety_factor,
        normalized_l1_gate=normalized_l1_gate,
        angular_watch_l1_gate=angular_watch_l1_gate,
        coefficient_gate=coefficient_gate,
        coefficient_weight=coefficient_weight,
        s_centers=s_centers,
        l_centers=l_centers,
        width_multipliers=width_multipliers,
        ridges=ridges,
    )
    metadata = {
        "fit_dir": str(fit_dir),
        "fit_sector_stress": str(fit_path),
        "fit_sector_stress_sha256": sha256_file(fit_path),
        "source_name": source_name,
        "input_caveat": manifest.get("caveat", ""),
        "regulator_safety_factor": float(regulator_safety_factor),
        "normalized_l1_gate": float(normalized_l1_gate),
        "angular_watch_l1_gate": float(angular_watch_l1_gate),
        "coefficient_gate": float(coefficient_gate),
        "caveat": (
            "Constructive-medium open probe for the endpoint angular-pressure watch. "
            "This fits a finite smooth internal anisotropic response field of the same "
            "regulated medium; it is not a new component and not a final field-equation proof."
        ),
    }
    return outputs, metadata


def write_constructive_medium_probe_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "point_fit": outdir / "endpoint_medium_constructive_point_fit.csv",
        "assignment_summary": outdir / "endpoint_medium_constructive_assignment_summary.csv",
        "candidate_scan": outdir / "endpoint_medium_constructive_candidate_scan.csv",
        "coefficients": outdir / "endpoint_medium_constructive_coefficients.csv",
        "feasibility_decision": outdir / "endpoint_medium_constructive_decision.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "endpoint_medium_constructive_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
