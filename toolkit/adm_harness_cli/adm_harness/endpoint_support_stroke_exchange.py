from __future__ import annotations

import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .source_ledger import sha256_file, write_manifest
from .source_screening import resolve_manifest_path


EPS = 1.0e-30


@dataclass(frozen=True)
class StrokeFitSpec:
    s_centers: int
    l_centers: int
    width_multiplier: float
    ridge: float
    include_laplacian: bool = True


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


def _add_keys(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["s_key"] = out["s"].astype(float).round(12)
    out["l_key"] = out["l"].astype(float).round(12)
    return out


def _metric_tetrad(alpha: float, beta: float, gamma_ll: float, gamma_omega: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    g = np.zeros((4, 4), dtype=float)
    g[0, 0] = -alpha * alpha + gamma_ll * beta * beta
    g[0, 1] = g[1, 0] = gamma_ll * beta
    g[1, 1] = gamma_ll
    g[2, 2] = gamma_omega
    g[3, 3] = gamma_omega
    u = np.array([1.0 / alpha, -beta / alpha, 0.0, 0.0], dtype=float)
    s = np.array([0.0, 1.0 / math.sqrt(gamma_ll), 0.0, 0.0], dtype=float)
    e_theta = np.array([0.0, 0.0, 1.0 / math.sqrt(gamma_omega), 0.0], dtype=float)
    e_phi = np.array([0.0, 0.0, 0.0, 1.0 / math.sqrt(gamma_omega)], dtype=float)
    return g, u, s, e_theta, e_phi


def _add_local_exchange_components(divergence_points: pd.DataFrame) -> pd.DataFrame:
    frame = divergence_points.copy().reset_index(drop=True)
    rows: list[dict[str, float]] = []
    for _, row in frame.iterrows():
        alpha = _finite(row["alpha"], float("nan"))
        beta = _finite(row["beta"], float("nan"))
        gamma_ll = _finite(row["gamma_ll"], float("nan"))
        gamma_omega = _finite(row["gamma_omega"], float("nan"))
        g, u, s, e_theta, e_phi = _metric_tetrad(alpha, beta, gamma_ll, gamma_omega)
        j = np.array([_finite(row[f"covariant_divergence_{nu}"], 0.0) for nu in range(4)], dtype=float)
        u_cov = g @ u
        s_cov = g @ s
        theta_cov = g @ e_theta
        phi_cov = g @ e_phi
        power = -float(u_cov @ j)
        radial_force = float(s_cov @ j)
        angular_theta = float(theta_cov @ j)
        angular_phi = float(phi_cov @ j)
        target_j = power * u + radial_force * s
        rows.append({
            "target_power_P": power,
            "target_radial_F": radial_force,
            "target_angular_theta": angular_theta,
            "target_angular_phi": angular_phi,
            "target_abs_PF_density": abs(power) + abs(radial_force),
            "target_norm_PF_density": math.sqrt(power * power + radial_force * radial_force),
            "target_abs_angular_density": abs(angular_theta) + abs(angular_phi),
            "target_J_from_PF_0": float(target_j[0]),
            "target_J_from_PF_1": float(target_j[1]),
            "target_J_from_PF_2": float(target_j[2]),
            "target_J_from_PF_3": float(target_j[3]),
            "tetrad_power_unit_0": float(u[0]),
            "tetrad_power_unit_1": float(u[1]),
            "tetrad_power_unit_2": float(u[2]),
            "tetrad_power_unit_3": float(u[3]),
            "tetrad_radial_unit_0": float(s[0]),
            "tetrad_radial_unit_1": float(s[1]),
            "tetrad_radial_unit_2": float(s[2]),
            "tetrad_radial_unit_3": float(s[3]),
        })
    out = pd.concat([frame.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
    out["exchange_point_id"] = np.arange(len(out), dtype=int)
    return out


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


def _h_ref(frame: pd.DataFrame) -> float:
    if "h_ref" not in frame:
        return 1.0
    value = float(frame["h_ref"].astype(float).replace([np.inf, -np.inf], np.nan).dropna().median())
    return value if math.isfinite(value) and value > 0.0 else 1.0


def _stroke_basis_matrix(frame: pd.DataFrame, spec: StrokeFitSpec) -> tuple[np.ndarray, pd.DataFrame]:
    s_values = frame["s"].astype(float).to_numpy()
    l_values = frame["l"].astype(float).to_numpy()
    s_grid = _centers(frame["s"], spec.s_centers)
    l_grid = _centers(frame["l"], spec.l_centers)
    sigma_s = _sigma(s_grid, frame["s"], spec.width_multiplier)
    sigma_l = _sigma(l_grid, frame["l"], spec.width_multiplier)
    h_ref = _h_ref(frame)
    columns: list[np.ndarray] = [np.ones(len(frame), dtype=float)]
    rows: list[dict[str, Any]] = [{
        "basis_name": "support_stroke_uniform_body",
        "basis_kind": "stroke_body",
        "center_s": float("nan"),
        "center_l": float("nan"),
        "sigma_s": float("nan"),
        "sigma_l": float("nan"),
        "h_ref": h_ref,
    }]
    for center_s in s_grid:
        for center_l in l_grid:
            ds = (s_values - float(center_s)) / max(sigma_s, EPS)
            dl = (l_values - float(center_l)) / max(sigma_l, EPS)
            gaussian = np.exp(-0.5 * (np.square(ds) + np.square(dl)))
            d_s = h_ref * (-(s_values - float(center_s)) / max(sigma_s, EPS) ** 2) * gaussian
            d_l = h_ref * (-(l_values - float(center_l)) / max(sigma_l, EPS) ** 2) * gaussian
            columns.extend([gaussian, d_s, d_l])
            rows.extend([
                {
                    "basis_name": f"support_stroke_body_s{center_s:.6g}_l{center_l:.6g}",
                    "basis_kind": "stroke_body",
                    "center_s": float(center_s),
                    "center_l": float(center_l),
                    "sigma_s": sigma_s,
                    "sigma_l": sigma_l,
                    "h_ref": h_ref,
                },
                {
                    "basis_name": f"support_stress_div_s_s{center_s:.6g}_l{center_l:.6g}",
                    "basis_kind": "stress_divergence_s",
                    "center_s": float(center_s),
                    "center_l": float(center_l),
                    "sigma_s": sigma_s,
                    "sigma_l": sigma_l,
                    "h_ref": h_ref,
                },
                {
                    "basis_name": f"support_stress_div_l_s{center_s:.6g}_l{center_l:.6g}",
                    "basis_kind": "stress_divergence_l",
                    "center_s": float(center_s),
                    "center_l": float(center_l),
                    "sigma_s": sigma_s,
                    "sigma_l": sigma_l,
                    "h_ref": h_ref,
                },
            ])
            if spec.include_laplacian:
                lap_s = np.square(s_values - float(center_s)) / max(sigma_s, EPS) ** 4 - 1.0 / max(sigma_s, EPS) ** 2
                lap_l = np.square(l_values - float(center_l)) / max(sigma_l, EPS) ** 4 - 1.0 / max(sigma_l, EPS) ** 2
                columns.append(h_ref * h_ref * (lap_s + lap_l) * gaussian)
                rows.append({
                    "basis_name": f"support_stress_lap_s{center_s:.6g}_l{center_l:.6g}",
                    "basis_kind": "stress_potential_laplacian",
                    "center_s": float(center_s),
                    "center_l": float(center_l),
                    "sigma_s": sigma_s,
                    "sigma_l": sigma_l,
                    "h_ref": h_ref,
                })
    basis = np.column_stack(columns)
    peaks = np.max(np.abs(basis), axis=0)
    peaks = np.where(peaks > 0.0, peaks, 1.0)
    meta = pd.DataFrame(rows)
    meta["basis_peak_normalizer"] = peaks
    return basis / peaks, meta


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
    include_laplacian: bool,
) -> list[StrokeFitSpec]:
    return [
        StrokeFitSpec(int(sc), int(lc), float(width), float(ridge), bool(include_laplacian))
        for sc, lc, width, ridge in itertools.product(
            s_centers or [16, 20, 24],
            l_centers or [10, 12, 14],
            width_multipliers or [0.30, 0.35],
            ridges or [1.0e-5, 3.0e-6],
        )
    ]


def _group_columns_for_scope(fit_scope: str) -> list[str]:
    if fit_scope == "assignment":
        return ["assignment"]
    if fit_scope == "assignment_stage_region":
        return ["assignment", "stage", "region"]
    if fit_scope == "phase_region":
        return ["stage", "region"]
    raise ValueError(f"unknown fit scope {fit_scope!r}")


def _group_key(group_values: tuple[Any, ...] | Any) -> str:
    if not isinstance(group_values, tuple):
        group_values = (group_values,)
    return "|".join(str(value) for value in group_values)


def _component_field(component: str) -> str:
    if component == "P":
        return "target_power_P"
    if component == "F":
        return "target_radial_F"
    raise ValueError(f"unknown exchange component {component!r}")


def _domain_mask(frame: pd.DataFrame, fit_domain: str) -> pd.Series:
    live = _bool_series(frame["covariant_divergence_live"]) if "covariant_divergence_live" in frame else pd.Series(False, index=frame.index)
    if fit_domain == "active":
        base = _bool_series(frame["medium_source_active"]) if "medium_source_active" in frame else pd.Series(True, index=frame.index)
    elif fit_domain == "allowed":
        base = _bool_series(frame["covariant_exchange_allowed_mask"]) if "covariant_exchange_allowed_mask" in frame else pd.Series(True, index=frame.index)
    else:
        raise ValueError(f"unknown fit domain {fit_domain!r}")
    return base & (~live) & (frame["target_abs_PF_density"].astype(float) > 0.0)


def _weighted_component_error(frame: pd.DataFrame, component: str, pred: np.ndarray, mask: pd.Series) -> tuple[float, float, float]:
    selected = mask.to_numpy(dtype=bool)
    if not np.any(selected):
        return 0.0, 0.0, float("nan")
    y = frame[_component_field(component)].astype(float).to_numpy()
    weights = frame["volume_weight"].astype(float).to_numpy()
    target = float(np.sum(np.abs(y[selected]) * weights[selected]))
    error = float(np.sum(np.abs(pred[selected] - y[selected]) * weights[selected]))
    return target, error, _safe_ratio(error, target)


def _component_candidate_summary(
    fit_scope: str,
    fit_domain: str,
    group_key: str,
    component: str,
    frame: pd.DataFrame,
    train_mask: pd.Series,
    pred: np.ndarray,
    coefficients: np.ndarray,
    spec: StrokeFitSpec,
    score: float,
) -> dict[str, Any]:
    active = _bool_series(frame["medium_source_active"]) if "medium_source_active" in frame else pd.Series(True, index=frame.index)
    allowed = _bool_series(frame["covariant_exchange_allowed_mask"]) if "covariant_exchange_allowed_mask" in frame else pd.Series(True, index=frame.index)
    live = _bool_series(frame["covariant_divergence_live"]) if "covariant_divergence_live" in frame else pd.Series(False, index=frame.index)
    train_target, train_error, train_norm = _weighted_component_error(frame, component, pred, train_mask)
    active_target, active_error, active_norm = _weighted_component_error(frame, component, pred, active & (~live))
    allowed_target, allowed_error, allowed_norm = _weighted_component_error(frame, component, pred, allowed & (~live))
    outside = (~allowed) & (~live)
    weights = frame["volume_weight"].astype(float).to_numpy()
    coeff_abs = np.abs(coefficients)
    coeff_l2_sq = float(np.sum(np.square(coeff_abs)))
    outside_fit = float(np.sum(np.abs(pred[outside.to_numpy(dtype=bool)]) * weights[outside.to_numpy(dtype=bool)])) if np.any(outside) else 0.0
    live_fit = float(np.sum(np.abs(pred[live.to_numpy(dtype=bool)]) * weights[live.to_numpy(dtype=bool)])) if np.any(live) else 0.0
    return {
        "fit_scope": fit_scope,
        "fit_domain": fit_domain,
        "group_key": group_key,
        "component": component,
        "rows": int(len(frame)),
        "train_rows": int(train_mask.sum()),
        "s_centers": int(spec.s_centers),
        "l_centers": int(spec.l_centers),
        "width_multiplier": float(spec.width_multiplier),
        "ridge": float(spec.ridge),
        "include_laplacian": bool(spec.include_laplacian),
        "candidate_score": float(score),
        "train_weighted_target_l1": train_target,
        "train_weighted_error_l1": train_error,
        "train_normalized_l1_error": train_norm,
        "active_weighted_target_l1": active_target,
        "active_weighted_error_l1": active_error,
        "active_normalized_l1_error": active_norm,
        "allowed_weighted_target_l1": allowed_target,
        "allowed_weighted_error_l1": allowed_error,
        "allowed_normalized_l1_error": allowed_norm,
        "outside_allowed_fit_volume": outside_fit,
        "live_fit_volume": live_fit,
        "max_abs_coefficient": float(np.max(coeff_abs)) if len(coeff_abs) else float("nan"),
        "coefficient_l1": float(np.sum(coeff_abs)),
        "coefficient_l2": float(math.sqrt(coeff_l2_sq)),
        "effective_coefficient_count": float(np.square(np.sum(coeff_abs)) / coeff_l2_sq) if coeff_l2_sq > 0.0 else float("nan"),
    }


def _score(summary: dict[str, Any], coefficient_weight: float, effective_count_weight: float) -> float:
    active_error = _finite(summary.get("active_normalized_l1_error"), _finite(summary.get("train_normalized_l1_error"), 1.0))
    allowed_error = _finite(summary.get("allowed_normalized_l1_error"), active_error)
    coeff = math.log10(1.0 + max(_finite(summary.get("max_abs_coefficient"), 0.0), 0.0))
    return float(
        active_error
        + 0.35 * allowed_error
        + float(coefficient_weight) * coeff
        + float(effective_count_weight) * max(_finite(summary.get("effective_coefficient_count"), 0.0), 0.0)
    )


def _fit_scope_domain(
    exchange: pd.DataFrame,
    fit_scope: str,
    fit_domain: str,
    specs: list[StrokeFitSpec],
    coefficient_weight: float,
    effective_count_weight: float,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    group_cols = _group_columns_for_scope(fit_scope)
    point = exchange.copy()
    point["fit_scope"] = fit_scope
    point["fit_domain"] = fit_domain
    point["fit_P"] = 0.0
    point["fit_F"] = 0.0
    point["fit_error_P"] = -point["target_power_P"].astype(float)
    point["fit_error_F"] = -point["target_radial_F"].astype(float)
    point["fit_abs_error_P"] = point["fit_error_P"].abs()
    point["fit_abs_error_F"] = point["fit_error_F"].abs()

    candidate_rows: list[dict[str, Any]] = []
    selected_rows: list[dict[str, Any]] = []
    coeff_frames: list[pd.DataFrame] = []

    for group_values, group in exchange.groupby(group_cols, sort=False, dropna=False):
        key = _group_key(group_values)
        train_mask = _domain_mask(group, fit_domain)
        if int(train_mask.sum()) < 4:
            continue
        group_positions = {idx: pos for pos, idx in enumerate(group.index)}
        train_positions = np.array([group_positions[idx] for idx in group.index[train_mask.to_numpy(dtype=bool)]], dtype=int)
        weights = group.loc[train_mask, "volume_weight"].astype(float).to_numpy()
        basis_cache: dict[StrokeFitSpec, tuple[np.ndarray, pd.DataFrame]] = {}
        for component in ("P", "F"):
            best: tuple[float, np.ndarray, pd.DataFrame, np.ndarray, StrokeFitSpec, dict[str, Any]] | None = None
            y = group.loc[train_mask, _component_field(component)].astype(float).to_numpy()
            for spec in specs:
                if spec not in basis_cache:
                    basis_cache[spec] = _stroke_basis_matrix(group, spec)
                basis, basis_meta = basis_cache[spec]
                coefficients = _ridge_fit(basis[train_positions, :], y, weights, float(spec.ridge))
                pred = basis @ coefficients
                summary = _component_candidate_summary(
                    fit_scope,
                    fit_domain,
                    key,
                    component,
                    group,
                    train_mask,
                    pred,
                    coefficients,
                    spec,
                    score=0.0,
                )
                score = _score(summary, coefficient_weight, effective_count_weight)
                summary["candidate_score"] = score
                candidate_rows.append(summary)
                if best is None or score < best[0]:
                    coeffs = basis_meta.copy()
                    coeffs["coefficient"] = coefficients
                    coeffs["fit_scope"] = fit_scope
                    coeffs["fit_domain"] = fit_domain
                    coeffs["group_key"] = key
                    coeffs["component"] = component
                    coeffs["s_centers"] = int(spec.s_centers)
                    coeffs["l_centers"] = int(spec.l_centers)
                    coeffs["width_multiplier"] = float(spec.width_multiplier)
                    coeffs["ridge"] = float(spec.ridge)
                    coeffs["include_laplacian"] = bool(spec.include_laplacian)
                    best = (score, pred, coeffs, coefficients, spec, summary)
            if best is None:
                continue
            score, pred, coeffs, coefficients, spec, _ = best
            summary = _component_candidate_summary(
                fit_scope,
                fit_domain,
                key,
                component,
                group,
                train_mask,
                pred,
                coefficients,
                spec,
                score=score,
            )
            selected_rows.append(summary)
            coeff_frames.append(coeffs)
            point.loc[group.index, f"fit_{component}"] = pred
            point.loc[group.index, f"fit_error_{component}"] = pred - group[_component_field(component)].astype(float).to_numpy()
            point.loc[group.index, f"fit_abs_error_{component}"] = np.abs(
                pred - group[_component_field(component)].astype(float).to_numpy()
            )

    return (
        point,
        pd.DataFrame(selected_rows),
        pd.DataFrame(candidate_rows),
        pd.concat(coeff_frames, ignore_index=True) if coeff_frames else pd.DataFrame(),
    )


def _finalize_point_fit(point: pd.DataFrame) -> pd.DataFrame:
    out = point.copy()
    for nu in range(4):
        out[f"fit_J_{nu}"] = (
            out["fit_P"].astype(float) * out[f"tetrad_power_unit_{nu}"].astype(float)
            + out["fit_F"].astype(float) * out[f"tetrad_radial_unit_{nu}"].astype(float)
        )
        out[f"fit_J_error_{nu}"] = out[f"fit_J_{nu}"].astype(float) - out[f"covariant_divergence_{nu}"].astype(float)
    out["fit_abs_PF_density"] = out["fit_P"].abs() + out["fit_F"].abs()
    out["fit_error_abs_PF_density"] = out["fit_abs_error_P"].astype(float) + out["fit_abs_error_F"].astype(float)
    out["fit_norm_PF_density"] = np.sqrt(np.square(out["fit_P"].astype(float)) + np.square(out["fit_F"].astype(float)))
    out["fit_error_norm_PF_density"] = np.sqrt(np.square(out["fit_error_P"].astype(float)) + np.square(out["fit_error_F"].astype(float)))
    out["fit_coordinate_error_l2_density"] = np.sqrt(
        sum(np.square(out[f"fit_J_error_{nu}"].astype(float)) for nu in range(4))
    )
    out["fit_angular_abs_density"] = 0.0
    volume = out["volume_weight"].astype(float)
    for column in [
        "target_abs_PF_density",
        "target_norm_PF_density",
        "target_abs_angular_density",
        "fit_abs_PF_density",
        "fit_error_abs_PF_density",
        "fit_norm_PF_density",
        "fit_error_norm_PF_density",
        "fit_coordinate_error_l2_density",
        "fit_angular_abs_density",
        "covariant_divergence_l2_density",
    ]:
        out[f"{column}_volume"] = out[column].astype(float) * volume
    return out


def _merge_guards(exchange: pd.DataFrame, point_projection: pd.DataFrame) -> pd.DataFrame:
    guard_cols = [
        "case",
        "s",
        "l",
        "assignment",
        "enthalpy_buffer_density",
        "transport_margin",
        "regulated_heat_flux_ratio",
        "regulated_type_i_margin",
        "source_abs_volume",
    ]
    guards = _add_keys(point_projection[[col for col in guard_cols if col in point_projection.columns]].copy())
    base = _add_keys(exchange)
    merged = base.merge(
        guards.drop(columns=["s", "l"], errors="ignore"),
        on=["case", "s_key", "l_key", "assignment"],
        how="left",
        suffixes=("", "_guard"),
    )
    if "source_abs_volume_guard" in merged:
        merged["guard_source_abs_volume"] = merged["source_abs_volume_guard"].astype(float)
    elif "source_abs_volume" in merged:
        merged["guard_source_abs_volume"] = merged["source_abs_volume"].astype(float)
    else:
        merged["guard_source_abs_volume"] = merged["source_abs_density"].astype(float) * merged["volume_weight"].astype(float)
    ratio = merged["regulated_heat_flux_ratio"].astype(float).clip(lower=0.0, upper=1.0 - 1.0e-15)
    merged["transport_rapidity_abs"] = np.arctanh(ratio)
    return merged


def _mask(point: pd.DataFrame, name: str) -> pd.Series:
    live = _bool_series(point["covariant_divergence_live"]) if "covariant_divergence_live" in point else pd.Series(False, index=point.index)
    active = _bool_series(point["medium_source_active"]) if "medium_source_active" in point else pd.Series(True, index=point.index)
    allowed = _bool_series(point["covariant_exchange_allowed_mask"]) if "covariant_exchange_allowed_mask" in point else pd.Series(True, index=point.index)
    if name == "active":
        return active & (~live)
    if name == "allowed":
        return allowed & (~live)
    if name == "outside":
        return (~allowed) & (~live)
    if name == "live":
        return live
    raise ValueError(f"unknown mask {name!r}")


def _volume_sum(point: pd.DataFrame, column: str, mask: pd.Series | None = None) -> float:
    selected = point if mask is None else point.loc[mask]
    return float(selected[column].astype(float).sum()) if len(selected) else 0.0


def _scope_summary(
    point: pd.DataFrame,
    selected: pd.DataFrame,
    *,
    fit_scope: str,
    fit_domain: str,
    active_pf_l1_gate: float,
    allowed_pf_l1_gate: float,
    coordinate_error_gate: float,
    coefficient_gate: float,
    effective_coefficient_count_gate: float,
    outside_tail_fraction_gate: float,
    live_tail_fraction_gate: float,
    high_psi_source_fraction_gate: float,
) -> dict[str, Any]:
    active = _mask(point, "active")
    allowed = _mask(point, "allowed")
    outside = _mask(point, "outside")
    live = _mask(point, "live")
    active_target = _volume_sum(point, "target_abs_PF_density_volume", active)
    allowed_target = _volume_sum(point, "target_abs_PF_density_volume", allowed)
    active_error = _volume_sum(point, "fit_error_abs_PF_density_volume", active)
    allowed_error = _volume_sum(point, "fit_error_abs_PF_density_volume", allowed)
    active_coordinate = _volume_sum(point, "fit_coordinate_error_l2_density_volume", active)
    allowed_coordinate = _volume_sum(point, "fit_coordinate_error_l2_density_volume", allowed)
    active_coordinate_target = _volume_sum(point, "covariant_divergence_l2_density_volume", active)
    allowed_coordinate_target = _volume_sum(point, "covariant_divergence_l2_density_volume", allowed)
    fit_total = _volume_sum(point, "fit_abs_PF_density_volume")
    outside_fit = _volume_sum(point, "fit_abs_PF_density_volume", outside)
    live_fit = _volume_sum(point, "fit_abs_PF_density_volume", live)
    active_fit = _volume_sum(point, "fit_abs_PF_density_volume", active)
    allowed_fit = _volume_sum(point, "fit_abs_PF_density_volume", allowed)
    active_guard = point.loc[active].copy()
    source_abs_volume = active_guard["guard_source_abs_volume"].astype(float) if "guard_source_abs_volume" in active_guard else active_guard["source_abs_density"].astype(float) * active_guard["volume_weight"].astype(float)
    high_psi = active_guard["transport_rapidity_abs"].astype(float) > 4.0 if "transport_rapidity_abs" in active_guard else pd.Series(False, index=active_guard.index)
    source_total = float(source_abs_volume.sum())
    high_psi_source = float(source_abs_volume.loc[high_psi].sum())
    max_abs_coefficient = float(selected["max_abs_coefficient"].astype(float).max()) if len(selected) else float("nan")
    effective_total = float(selected["effective_coefficient_count"].astype(float).sum()) if len(selected) else float("nan")
    active_pf_l1 = _safe_ratio(active_error, active_target)
    allowed_pf_l1 = _safe_ratio(allowed_error, allowed_target)
    active_coordinate_ratio = _safe_ratio(active_coordinate, active_coordinate_target)
    allowed_coordinate_ratio = _safe_ratio(allowed_coordinate, allowed_coordinate_target)
    outside_tail_fraction = _safe_ratio(outside_fit, fit_total)
    live_tail_fraction = _safe_ratio(live_fit, fit_total)
    fit_quality_pass = bool(
        active_pf_l1 <= float(active_pf_l1_gate)
        and allowed_pf_l1 <= float(allowed_pf_l1_gate)
        and active_coordinate_ratio <= float(coordinate_error_gate)
        and allowed_coordinate_ratio <= float(coordinate_error_gate)
    )
    coefficient_pass = bool(
        max_abs_coefficient <= float(coefficient_gate)
        and effective_total <= float(effective_coefficient_count_gate)
    )
    guard_pass = bool(
        len(active_guard) > 0
        and float(active_guard["enthalpy_buffer_density"].astype(float).min()) > 0.0
        and float(active_guard["transport_margin"].astype(float).min()) >= -1.0e-12
        and float(active_guard["regulated_type_i_margin"].astype(float).min()) > 0.0
        and _safe_ratio(high_psi_source, source_total) <= float(high_psi_source_fraction_gate)
    )
    target_angular = _volume_sum(point, "target_abs_angular_density_volume", allowed)
    fit_angular = _volume_sum(point, "fit_angular_abs_density_volume", allowed)
    tail_audit_pass = bool(
        outside_tail_fraction <= float(outside_tail_fraction_gate)
        and live_tail_fraction <= float(live_tail_fraction_gate)
    )
    hidden_support_pass = bool(target_angular <= 1.0e-14 and fit_angular <= 1.0e-14 and live_fit <= 1.0e-14)
    return {
        "fit_scope": fit_scope,
        "fit_domain": fit_domain,
        "rows": int(len(point)),
        "active_rows": int(active.sum()),
        "allowed_rows": int(allowed.sum()),
        "outside_allowed_rows": int(outside.sum()),
        "live_rows": int(live.sum()),
        "groups": int(selected["group_key"].nunique()) if len(selected) else 0,
        "active_target_abs_PF_volume": active_target,
        "allowed_target_abs_PF_volume": allowed_target,
        "active_fit_error_abs_PF_volume": active_error,
        "allowed_fit_error_abs_PF_volume": allowed_error,
        "normalized_active_abs_PF_l1_error": active_pf_l1,
        "normalized_allowed_abs_PF_l1_error": allowed_pf_l1,
        "active_coordinate_l2_error_ratio": active_coordinate_ratio,
        "allowed_coordinate_l2_error_ratio": allowed_coordinate_ratio,
        "active_pf_l1_gate": float(active_pf_l1_gate),
        "allowed_pf_l1_gate": float(allowed_pf_l1_gate),
        "coordinate_error_gate": float(coordinate_error_gate),
        "fit_quality_pass": fit_quality_pass,
        "fit_abs_PF_volume_total": fit_total,
        "active_fit_abs_PF_volume": active_fit,
        "allowed_fit_abs_PF_volume": allowed_fit,
        "outside_allowed_fit_abs_PF_volume": outside_fit,
        "live_fit_abs_PF_volume": live_fit,
        "active_fit_fraction": _safe_ratio(active_fit, fit_total),
        "allowed_fit_fraction": _safe_ratio(allowed_fit, fit_total),
        "outside_tail_fraction": outside_tail_fraction,
        "live_tail_fraction": live_tail_fraction,
        "outside_tail_fraction_gate": float(outside_tail_fraction_gate),
        "live_tail_fraction_gate": float(live_tail_fraction_gate),
        "tail_audit_pass": tail_audit_pass,
        "max_abs_coefficient": max_abs_coefficient,
        "coefficient_l1": float(selected["coefficient_l1"].astype(float).sum()) if len(selected) else float("nan"),
        "effective_coefficient_count_total": effective_total,
        "coefficient_gate": float(coefficient_gate),
        "effective_coefficient_count_gate": float(effective_coefficient_count_gate),
        "coefficient_pass": coefficient_pass,
        "h_reg_min": float(active_guard["enthalpy_buffer_density"].astype(float).min()) if len(active_guard) else float("nan"),
        "transport_margin_min": float(active_guard["transport_margin"].astype(float).min()) if len(active_guard) else float("nan"),
        "type_i_margin_min": float(active_guard["regulated_type_i_margin"].astype(float).min()) if len(active_guard) else float("nan"),
        "max_transport_rapidity_abs": float(active_guard["transport_rapidity_abs"].astype(float).max()) if len(active_guard) else float("nan"),
        "high_psi_source_fraction": _safe_ratio(high_psi_source, source_total),
        "high_psi_source_fraction_gate": float(high_psi_source_fraction_gate),
        "guard_pass": guard_pass,
        "target_angular_exchange_volume": target_angular,
        "fit_angular_exchange_volume": fit_angular,
        "hidden_support_pass": hidden_support_pass,
        "support_stroke_fit_pass": bool(fit_quality_pass and coefficient_pass and guard_pass and tail_audit_pass and hidden_support_pass),
    }


def _load_covariant_dir(covariant_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any], dict[str, Path]]:
    manifest_path = covariant_dir / "endpoint_medium_covariant_manifest.json"
    manifest: dict[str, Any] = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
    files = manifest.get("files", {})
    projection_path = resolve_manifest_path(covariant_dir, files.get("point_projection", "endpoint_medium_covariant_point_projection.csv"))
    divergence_path = resolve_manifest_path(covariant_dir, files.get("divergence_points", "endpoint_medium_covariant_divergence_points.csv"))
    projection = pd.read_csv(projection_path)
    divergence = pd.read_csv(divergence_path)
    return projection, divergence, manifest, {
        "manifest": manifest_path,
        "point_projection": projection_path,
        "divergence_points": divergence_path,
    }


def build_support_stroke_exchange_tables(
    point_projection: pd.DataFrame,
    divergence_points: pd.DataFrame,
    *,
    fit_scopes: list[str] | None = None,
    fit_domains: list[str] | None = None,
    active_pf_l1_gate: float = 0.50,
    allowed_pf_l1_gate: float = 0.50,
    coordinate_error_gate: float = 0.55,
    coefficient_gate: float = 4.0,
    effective_coefficient_count_gate: float = 18000.0,
    outside_tail_fraction_gate: float = 0.001,
    live_tail_fraction_gate: float = 0.0001,
    high_psi_source_fraction_gate: float = 0.005,
    coefficient_weight: float = 0.02,
    effective_count_weight: float = 0.000002,
    s_centers: list[int] | None = None,
    l_centers: list[int] | None = None,
    width_multipliers: list[float] | None = None,
    ridges: list[float] | None = None,
    include_laplacian: bool = True,
) -> dict[str, pd.DataFrame]:
    exchange = _add_local_exchange_components(divergence_points)
    exchange = _merge_guards(exchange, point_projection)
    specs = _candidate_specs(s_centers, l_centers, width_multipliers, ridges, include_laplacian=include_laplacian)
    scopes = fit_scopes or ["phase_region"]
    domains = fit_domains or ["allowed"]
    point_frames: list[pd.DataFrame] = []
    selected_frames: list[pd.DataFrame] = []
    candidate_frames: list[pd.DataFrame] = []
    coeff_frames: list[pd.DataFrame] = []
    summary_rows: list[dict[str, Any]] = []

    for fit_scope in scopes:
        for fit_domain in domains:
            point, selected, candidate, coeffs = _fit_scope_domain(
                exchange,
                fit_scope,
                fit_domain,
                specs,
                coefficient_weight=float(coefficient_weight),
                effective_count_weight=float(effective_count_weight),
            )
            point = _finalize_point_fit(point)
            point_frames.append(point)
            if len(selected):
                selected_frames.append(selected)
            if len(candidate):
                candidate_frames.append(candidate)
            if len(coeffs):
                coeff_frames.append(coeffs)
            summary_rows.append(_scope_summary(
                point,
                selected,
                fit_scope=fit_scope,
                fit_domain=fit_domain,
                active_pf_l1_gate=active_pf_l1_gate,
                allowed_pf_l1_gate=allowed_pf_l1_gate,
                coordinate_error_gate=coordinate_error_gate,
                coefficient_gate=coefficient_gate,
                effective_coefficient_count_gate=effective_coefficient_count_gate,
                outside_tail_fraction_gate=outside_tail_fraction_gate,
                live_tail_fraction_gate=live_tail_fraction_gate,
                high_psi_source_fraction_gate=high_psi_source_fraction_gate,
            ))

    fit_scope_summary = pd.DataFrame(summary_rows)
    if fit_scope_summary.empty:
        decision = pd.DataFrame([{
            "support_stroke_exchange_status": "missing_support_stroke_exchange_fit",
            "passes_support_stroke_exchange_fit": False,
        }])
    else:
        score = (
            fit_scope_summary["normalized_active_abs_PF_l1_error"].astype(float)
            + fit_scope_summary["normalized_allowed_abs_PF_l1_error"].astype(float)
            + 0.05 * np.log10(1.0 + fit_scope_summary["max_abs_coefficient"].astype(float).clip(lower=0.0))
        )
        best = fit_scope_summary.loc[score.sort_values().index[0]]
        hard_pass = bool(fit_scope_summary["support_stroke_fit_pass"].astype(bool).any())
        decision = pd.DataFrame([{
            "support_stroke_exchange_status": "support_stroke_exchange_fit_pass" if hard_pass else "support_stroke_exchange_fit_watch",
            "passes_support_stroke_exchange_fit": hard_pass,
            "best_fit_scope": str(best["fit_scope"]),
            "best_fit_domain": str(best["fit_domain"]),
            "best_normalized_active_abs_PF_l1_error": float(best["normalized_active_abs_PF_l1_error"]),
            "best_normalized_allowed_abs_PF_l1_error": float(best["normalized_allowed_abs_PF_l1_error"]),
            "best_active_coordinate_l2_error_ratio": float(best["active_coordinate_l2_error_ratio"]),
            "best_allowed_coordinate_l2_error_ratio": float(best["allowed_coordinate_l2_error_ratio"]),
            "best_max_abs_coefficient": float(best["max_abs_coefficient"]),
            "best_effective_coefficient_count_total": float(best["effective_coefficient_count_total"]),
            "best_outside_tail_fraction": float(best["outside_tail_fraction"]),
            "best_live_tail_fraction": float(best["live_tail_fraction"]),
            "best_high_psi_source_fraction": float(best["high_psi_source_fraction"]),
            "active_pf_l1_gate": float(active_pf_l1_gate),
            "allowed_pf_l1_gate": float(allowed_pf_l1_gate),
            "coordinate_error_gate": float(coordinate_error_gate),
            "coefficient_gate": float(coefficient_gate),
            "effective_coefficient_count_gate": float(effective_coefficient_count_gate),
            "outside_tail_fraction_gate": float(outside_tail_fraction_gate),
            "live_tail_fraction_gate": float(live_tail_fraction_gate),
            "high_psi_source_fraction_gate": float(high_psi_source_fraction_gate),
            "decision_read": (
                "phase-aware support stroke/stress ansatz reproduces the P/F exchange within gates while keeping full-grid tails localized"
                if hard_pass
                else "phase-aware support stroke/stress ansatz improves the exchange fit but one or more quality, coefficient, guard, or tail gates remain on watch"
            ),
        }])

    return {
        "point_fit": pd.concat(point_frames, ignore_index=True) if point_frames else pd.DataFrame(),
        "selected_component_summary": pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame(),
        "candidate_scan": pd.concat(candidate_frames, ignore_index=True) if candidate_frames else pd.DataFrame(),
        "coefficients": pd.concat(coeff_frames, ignore_index=True) if coeff_frames else pd.DataFrame(),
        "fit_scope_summary": fit_scope_summary,
        "decision": decision,
    }


def build_support_stroke_exchange_fit(
    covariant_dir: Path,
    *,
    source_name: str = "endpoint_support_stroke_exchange",
    fit_scopes: list[str] | None = None,
    fit_domains: list[str] | None = None,
    active_pf_l1_gate: float = 0.50,
    allowed_pf_l1_gate: float = 0.50,
    coordinate_error_gate: float = 0.55,
    coefficient_gate: float = 4.0,
    effective_coefficient_count_gate: float = 18000.0,
    outside_tail_fraction_gate: float = 0.001,
    live_tail_fraction_gate: float = 0.0001,
    high_psi_source_fraction_gate: float = 0.005,
    coefficient_weight: float = 0.02,
    effective_count_weight: float = 0.000002,
    s_centers: list[int] | None = None,
    l_centers: list[int] | None = None,
    width_multipliers: list[float] | None = None,
    ridges: list[float] | None = None,
    include_laplacian: bool = True,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    point_projection, divergence_points, manifest, paths = _load_covariant_dir(covariant_dir)
    outputs = build_support_stroke_exchange_tables(
        point_projection,
        divergence_points,
        fit_scopes=fit_scopes,
        fit_domains=fit_domains,
        active_pf_l1_gate=active_pf_l1_gate,
        allowed_pf_l1_gate=allowed_pf_l1_gate,
        coordinate_error_gate=coordinate_error_gate,
        coefficient_gate=coefficient_gate,
        effective_coefficient_count_gate=effective_coefficient_count_gate,
        outside_tail_fraction_gate=outside_tail_fraction_gate,
        live_tail_fraction_gate=live_tail_fraction_gate,
        high_psi_source_fraction_gate=high_psi_source_fraction_gate,
        coefficient_weight=coefficient_weight,
        effective_count_weight=effective_count_weight,
        s_centers=s_centers,
        l_centers=l_centers,
        width_multipliers=width_multipliers,
        ridges=ridges,
        include_laplacian=include_laplacian,
    )
    metadata = {
        "covariant_dir": str(covariant_dir),
        "covariant_manifest": str(paths["manifest"]),
        "point_projection": str(paths["point_projection"]),
        "point_projection_sha256": sha256_file(paths["point_projection"]),
        "divergence_points": str(paths["divergence_points"]),
        "divergence_points_sha256": sha256_file(paths["divergence_points"]),
        "source_name": source_name,
        "covariant_input_caveat": manifest.get("caveat", ""),
        "fit_scopes": fit_scopes or ["phase_region"],
        "fit_domains": fit_domains or ["allowed"],
        "active_pf_l1_gate": float(active_pf_l1_gate),
        "allowed_pf_l1_gate": float(allowed_pf_l1_gate),
        "coordinate_error_gate": float(coordinate_error_gate),
        "coefficient_gate": float(coefficient_gate),
        "effective_coefficient_count_gate": float(effective_coefficient_count_gate),
        "outside_tail_fraction_gate": float(outside_tail_fraction_gate),
        "live_tail_fraction_gate": float(live_tail_fraction_gate),
        "high_psi_source_fraction_gate": float(high_psi_source_fraction_gate),
        "caveat": (
            "Phase-aware support stroke/stress exchange screen. This tests whether "
            "local storage/body modes plus finite-difference stress-divergence modes can generate "
            "J_endpoint^nu = P u^nu + F s^nu on the full covariant divergence surface. "
            "It includes a full-grid tail audit for predicted support exchange outside allowed masks and in live rows."
        ),
    }
    return outputs, metadata


def write_support_stroke_exchange_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "point_fit": outdir / "endpoint_support_stroke_exchange_point_fit.csv",
        "selected_component_summary": outdir / "endpoint_support_stroke_exchange_selected_component_summary.csv",
        "candidate_scan": outdir / "endpoint_support_stroke_exchange_candidate_scan.csv",
        "coefficients": outdir / "endpoint_support_stroke_exchange_coefficients.csv",
        "fit_scope_summary": outdir / "endpoint_support_stroke_exchange_fit_scope_summary.csv",
        "decision": outdir / "endpoint_support_stroke_exchange_decision.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "endpoint_support_stroke_exchange_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
