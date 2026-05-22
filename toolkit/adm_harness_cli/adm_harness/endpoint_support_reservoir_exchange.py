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
class ExchangeFitSpec:
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
    active = _bool_series(divergence_points["medium_source_active"]) if "medium_source_active" in divergence_points else pd.Series(True, index=divergence_points.index)
    frame = divergence_points.loc[active].copy().reset_index(drop=True)
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
        fit_j = power * u + radial_force * s
        rows.append({
            "target_power_P": power,
            "target_radial_F": radial_force,
            "target_angular_theta": angular_theta,
            "target_angular_phi": angular_phi,
            "target_abs_PF_density": abs(power) + abs(radial_force),
            "target_norm_PF_density": math.sqrt(power * power + radial_force * radial_force),
            "target_abs_angular_density": abs(angular_theta) + abs(angular_phi),
            "target_J_from_PF_0": float(fit_j[0]),
            "target_J_from_PF_1": float(fit_j[1]),
            "target_J_from_PF_2": float(fit_j[2]),
            "target_J_from_PF_3": float(fit_j[3]),
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


def _gaussian(s_values: np.ndarray, l_values: np.ndarray, center_s: float, center_l: float, sigma_s: float, sigma_l: float) -> np.ndarray:
    return np.exp(
        -0.5
        * (
            np.square((s_values - center_s) / max(sigma_s, EPS))
            + np.square((l_values - center_l) / max(sigma_l, EPS))
        )
    )


def _basis_matrix(frame: pd.DataFrame, spec: ExchangeFitSpec) -> tuple[np.ndarray, pd.DataFrame]:
    s_values = frame["s"].astype(float).to_numpy()
    l_values = frame["l"].astype(float).to_numpy()
    s_grid = _centers(frame["s"], spec.s_centers)
    l_grid = _centers(frame["l"], spec.l_centers)
    sigma_s = _sigma(s_grid, frame["s"], spec.width_multiplier)
    sigma_l = _sigma(l_grid, frame["l"], spec.width_multiplier)
    columns: list[np.ndarray] = [np.ones(len(frame), dtype=float)]
    rows: list[dict[str, Any]] = [{
        "basis_name": "support_exchange_uniform",
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
                "basis_name": f"support_exchange_s{center_s:.6g}_l{center_l:.6g}",
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
) -> list[ExchangeFitSpec]:
    return [
        ExchangeFitSpec(int(sc), int(lc), float(width), float(ridge))
        for sc, lc, width, ridge in itertools.product(
            s_centers or [8, 12, 16],
            l_centers or [6, 10],
            width_multipliers or [0.35, 0.50, 0.70],
            ridges or [1.0e-7, 1.0e-6, 1.0e-5],
        )
    ]


def _group_columns_for_scope(fit_scope: str) -> list[str]:
    if fit_scope == "assignment":
        return ["assignment"]
    if fit_scope == "stage_region":
        return ["assignment", "stage", "region"]
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


def _fit_component(
    fit_scope: str,
    group_key: str,
    component: str,
    frame: pd.DataFrame,
    spec: ExchangeFitSpec,
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    basis, basis_meta = _basis_matrix(frame, spec)
    y = frame[_component_field(component)].astype(float).to_numpy()
    weights = frame["volume_weight"].astype(float).to_numpy()
    coefficients = _ridge_fit(basis, y, weights, float(spec.ridge))
    pred = basis @ coefficients
    fit = pd.DataFrame({
        "exchange_point_id": frame["exchange_point_id"].astype(int).to_numpy(),
        f"fit_{component}": pred,
        f"fit_error_{component}": pred - y,
        f"fit_abs_error_{component}": np.abs(pred - y),
    })
    coeffs = basis_meta.copy()
    coeffs["coefficient"] = coefficients
    coeffs["fit_scope"] = fit_scope
    coeffs["group_key"] = group_key
    coeffs["component"] = component
    coeffs["s_centers"] = int(spec.s_centers)
    coeffs["l_centers"] = int(spec.l_centers)
    coeffs["width_multiplier"] = float(spec.width_multiplier)
    coeffs["ridge"] = float(spec.ridge)
    return fit, coeffs, coefficients


def _component_summary(
    fit_scope: str,
    group_key: str,
    component: str,
    frame: pd.DataFrame,
    fit: pd.DataFrame,
    coefficients: np.ndarray,
    spec: ExchangeFitSpec,
    score: float,
) -> dict[str, Any]:
    y = frame[_component_field(component)].astype(float).to_numpy()
    pred = fit[f"fit_{component}"].astype(float).to_numpy()
    err = pred - y
    weights = frame["volume_weight"].astype(float).to_numpy()
    coeff_abs = np.abs(coefficients)
    coeff_l2_sq = float(np.sum(np.square(coeff_abs)))
    target_l1 = float(np.sum(np.abs(y) * weights))
    err_l1 = float(np.sum(np.abs(err) * weights))
    live = _bool_series(frame["inside_packet_live"]) if "inside_packet_live" in frame else pd.Series(False, index=frame.index)
    return {
        "fit_scope": fit_scope,
        "group_key": group_key,
        "component": component,
        "rows": int(len(frame)),
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
        "max_abs_coefficient": float(np.max(coeff_abs)) if len(coeff_abs) else float("nan"),
        "coefficient_l1": float(np.sum(coeff_abs)),
        "coefficient_l2": float(math.sqrt(coeff_l2_sq)),
        "effective_coefficient_count": float(np.square(np.sum(coeff_abs)) / coeff_l2_sq) if coeff_l2_sq > 0.0 else float("nan"),
    }


def _score(summary: dict[str, Any], coefficient_weight: float, effective_count_weight: float) -> float:
    coeff = math.log10(1.0 + max(_finite(summary.get("max_abs_coefficient"), 0.0), 0.0))
    return float(
        _finite(summary.get("normalized_l1_error"), 1.0)
        + float(coefficient_weight) * coeff
        + float(effective_count_weight) * max(_finite(summary.get("effective_coefficient_count"), 0.0), 0.0)
    )


def _fit_scope(
    exchange: pd.DataFrame,
    fit_scope: str,
    specs: list[ExchangeFitSpec],
    coefficient_weight: float,
    effective_count_weight: float,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    group_cols = _group_columns_for_scope(fit_scope)
    point = exchange.copy()
    point["fit_scope"] = fit_scope
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
        for component in ("P", "F"):
            best: tuple[float, pd.DataFrame, pd.DataFrame, np.ndarray, ExchangeFitSpec, dict[str, Any]] | None = None
            for spec in specs:
                fit, coeffs, coefficients = _fit_component(fit_scope, key, component, group, spec)
                summary = _component_summary(fit_scope, key, component, group, fit, coefficients, spec, score=0.0)
                score = _score(summary, coefficient_weight, effective_count_weight)
                summary["candidate_score"] = score
                candidate_rows.append(summary)
                if best is None or score < best[0]:
                    best = (score, fit, coeffs, coefficients, spec, summary)
            if best is None:
                continue
            score, fit, coeffs, coefficients, spec, _ = best
            summary = _component_summary(fit_scope, key, component, group, fit, coefficients, spec, score=score)
            selected_rows.append(summary)
            coeff_frames.append(coeffs)
            fit_map = fit.set_index("exchange_point_id")
            ids = group["exchange_point_id"].astype(int)
            point.loc[point["exchange_point_id"].isin(ids), f"fit_{component}"] = ids.map(fit_map[f"fit_{component}"]).to_numpy()
            point.loc[point["exchange_point_id"].isin(ids), f"fit_error_{component}"] = ids.map(fit_map[f"fit_error_{component}"]).to_numpy()
            point.loc[point["exchange_point_id"].isin(ids), f"fit_abs_error_{component}"] = ids.map(fit_map[f"fit_abs_error_{component}"]).to_numpy()

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


def _scope_summary(
    point: pd.DataFrame,
    selected: pd.DataFrame,
    *,
    fit_scope: str,
    pf_l1_gate: float,
    coordinate_error_gate: float,
    coefficient_gate: float,
    effective_coefficient_count_gate: float,
    high_psi_source_fraction_gate: float,
) -> dict[str, Any]:
    volume = point["volume_weight"].astype(float)
    source_abs_volume = point["guard_source_abs_volume"].astype(float) if "guard_source_abs_volume" in point else point["source_abs_density"].astype(float) * volume
    target_abs_pf = float(point["target_abs_PF_density_volume"].astype(float).sum())
    target_norm_pf = float(point["target_norm_PF_density_volume"].astype(float).sum())
    error_abs_pf = float(point["fit_error_abs_PF_density_volume"].astype(float).sum())
    error_norm_pf = float(point["fit_error_norm_PF_density_volume"].astype(float).sum())
    coordinate_error = float(point["fit_coordinate_error_l2_density_volume"].astype(float).sum())
    coordinate_target = float(point["covariant_divergence_l2_density"].astype(float).mul(volume).sum())
    angular_target = float(point["target_abs_angular_density_volume"].astype(float).sum())
    angular_fit = float(point["fit_angular_abs_density_volume"].astype(float).sum())
    live = _bool_series(point["inside_packet_live"]) if "inside_packet_live" in point else pd.Series(False, index=point.index)
    high_psi = point["transport_rapidity_abs"].astype(float) > 4.0 if "transport_rapidity_abs" in point else pd.Series(False, index=point.index)
    high_psi_source = float(source_abs_volume.loc[high_psi].sum())
    source_total = float(source_abs_volume.sum())
    component_p = selected.loc[selected["component"].astype(str) == "P"]
    component_f = selected.loc[selected["component"].astype(str) == "F"]
    max_component_error = float(selected["normalized_l1_error"].astype(float).max()) if len(selected) else float("nan")
    max_abs_coefficient = float(selected["max_abs_coefficient"].astype(float).max()) if len(selected) else float("nan")
    effective_total = float(selected["effective_coefficient_count"].astype(float).sum()) if len(selected) else float("nan")
    pf_l1_error = _safe_ratio(error_abs_pf, target_abs_pf)
    coordinate_ratio = _safe_ratio(coordinate_error, coordinate_target)
    fit_quality_pass = bool(pf_l1_error <= float(pf_l1_gate) and coordinate_ratio <= float(coordinate_error_gate))
    coefficient_pass = bool(max_abs_coefficient <= float(coefficient_gate) and effective_total <= float(effective_coefficient_count_gate))
    guard_pass = bool(
        float(point["enthalpy_buffer_density"].astype(float).min()) > 0.0
        and float(point["transport_margin"].astype(float).min()) >= -1.0e-12
        and float(point["regulated_type_i_margin"].astype(float).min()) > 0.0
        and _safe_ratio(high_psi_source, source_total) <= float(high_psi_source_fraction_gate)
    )
    hidden_support_pass = bool(int(live.sum()) == 0 and angular_target <= 1.0e-14 and angular_fit <= 1.0e-14)
    return {
        "fit_scope": fit_scope,
        "rows": int(len(point)),
        "groups": int(selected["group_key"].nunique()) if len(selected) else 0,
        "source_abs_volume": source_total,
        "target_abs_PF_volume": target_abs_pf,
        "target_norm_PF_volume": target_norm_pf,
        "fit_error_abs_PF_volume": error_abs_pf,
        "fit_error_norm_PF_volume": error_norm_pf,
        "normalized_abs_PF_l1_error": pf_l1_error,
        "normalized_norm_PF_error": _safe_ratio(error_norm_pf, target_norm_pf),
        "coordinate_l2_error_volume": coordinate_error,
        "coordinate_l2_target_volume": coordinate_target,
        "coordinate_l2_error_ratio": coordinate_ratio,
        "component_P_normalized_l1_error": float(component_p["weighted_error_l1"].astype(float).sum() / component_p["weighted_target_l1"].astype(float).sum()) if len(component_p) else float("nan"),
        "component_F_normalized_l1_error": float(component_f["weighted_error_l1"].astype(float).sum() / component_f["weighted_target_l1"].astype(float).sum()) if len(component_f) else float("nan"),
        "max_component_normalized_l1_error": max_component_error,
        "pf_l1_gate": float(pf_l1_gate),
        "coordinate_error_gate": float(coordinate_error_gate),
        "fit_quality_pass": fit_quality_pass,
        "max_abs_coefficient": max_abs_coefficient,
        "coefficient_l1": float(selected["coefficient_l1"].astype(float).sum()) if len(selected) else float("nan"),
        "effective_coefficient_count_total": effective_total,
        "coefficient_gate": float(coefficient_gate),
        "effective_coefficient_count_gate": float(effective_coefficient_count_gate),
        "coefficient_pass": coefficient_pass,
        "h_reg_min": float(point["enthalpy_buffer_density"].astype(float).min()),
        "transport_margin_min": float(point["transport_margin"].astype(float).min()),
        "type_i_margin_min": float(point["regulated_type_i_margin"].astype(float).min()),
        "max_transport_rapidity_abs": float(point["transport_rapidity_abs"].astype(float).max()),
        "high_psi_source_fraction": _safe_ratio(high_psi_source, source_total),
        "high_psi_source_fraction_gate": float(high_psi_source_fraction_gate),
        "guard_pass": guard_pass,
        "target_angular_exchange_volume": angular_target,
        "fit_angular_exchange_volume": angular_fit,
        "live_rows": int(live.sum()),
        "hidden_support_pass": hidden_support_pass,
        "support_reservoir_fit_pass": bool(fit_quality_pass and coefficient_pass and guard_pass and hidden_support_pass),
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


def build_support_reservoir_exchange_tables(
    point_projection: pd.DataFrame,
    divergence_points: pd.DataFrame,
    *,
    fit_scopes: list[str] | None = None,
    pf_l1_gate: float = 0.50,
    coordinate_error_gate: float = 0.50,
    coefficient_gate: float = 1.0,
    effective_coefficient_count_gate: float = 120.0,
    high_psi_source_fraction_gate: float = 0.005,
    coefficient_weight: float = 0.02,
    effective_count_weight: float = 0.0005,
    s_centers: list[int] | None = None,
    l_centers: list[int] | None = None,
    width_multipliers: list[float] | None = None,
    ridges: list[float] | None = None,
) -> dict[str, pd.DataFrame]:
    exchange = _add_local_exchange_components(divergence_points)
    exchange = _merge_guards(exchange, point_projection)
    specs = _candidate_specs(s_centers, l_centers, width_multipliers, ridges)
    scopes = fit_scopes or ["assignment", "stage_region"]
    point_frames: list[pd.DataFrame] = []
    selected_frames: list[pd.DataFrame] = []
    candidate_frames: list[pd.DataFrame] = []
    coeff_frames: list[pd.DataFrame] = []
    summary_rows: list[dict[str, Any]] = []

    for fit_scope in scopes:
        point, selected, candidate, coeffs = _fit_scope(
            exchange,
            fit_scope,
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
            pf_l1_gate=pf_l1_gate,
            coordinate_error_gate=coordinate_error_gate,
            coefficient_gate=coefficient_gate,
            effective_coefficient_count_gate=effective_coefficient_count_gate,
            high_psi_source_fraction_gate=high_psi_source_fraction_gate,
        ))

    fit_scope_summary = pd.DataFrame(summary_rows)
    if fit_scope_summary.empty:
        decision = pd.DataFrame([{
            "support_reservoir_exchange_status": "missing_support_exchange_fit",
            "passes_support_reservoir_exchange_fit": False,
        }])
    else:
        best = fit_scope_summary.sort_values("normalized_abs_PF_l1_error").iloc[0]
        hard_pass = bool(fit_scope_summary["support_reservoir_fit_pass"].astype(bool).any())
        decision = pd.DataFrame([{
            "support_reservoir_exchange_status": "support_reservoir_exchange_fit_pass" if hard_pass else "support_reservoir_exchange_fit_watch",
            "passes_support_reservoir_exchange_fit": hard_pass,
            "best_fit_scope": str(best["fit_scope"]),
            "best_normalized_abs_PF_l1_error": float(best["normalized_abs_PF_l1_error"]),
            "best_coordinate_l2_error_ratio": float(best["coordinate_l2_error_ratio"]),
            "best_max_abs_coefficient": float(best["max_abs_coefficient"]),
            "best_effective_coefficient_count_total": float(best["effective_coefficient_count_total"]),
            "best_high_psi_source_fraction": float(best["high_psi_source_fraction"]),
            "pf_l1_gate": float(pf_l1_gate),
            "coordinate_error_gate": float(coordinate_error_gate),
            "coefficient_gate": float(coefficient_gate),
            "effective_coefficient_count_gate": float(effective_coefficient_count_gate),
            "high_psi_source_fraction_gate": float(high_psi_source_fraction_gate),
            "decision_read": (
                "bounded localized smooth support-reservoir ansatz reproduces P/F exchange within gates"
                if hard_pass
                else "first bounded smooth support-reservoir ansatz does not yet reproduce the measured P/F exchange; support coupling needs sharper structure or a different ansatz"
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


def build_support_reservoir_exchange_fit(
    covariant_dir: Path,
    *,
    source_name: str = "endpoint_support_reservoir_exchange",
    fit_scopes: list[str] | None = None,
    pf_l1_gate: float = 0.50,
    coordinate_error_gate: float = 0.50,
    coefficient_gate: float = 1.0,
    effective_coefficient_count_gate: float = 120.0,
    high_psi_source_fraction_gate: float = 0.005,
    coefficient_weight: float = 0.02,
    effective_count_weight: float = 0.0005,
    s_centers: list[int] | None = None,
    l_centers: list[int] | None = None,
    width_multipliers: list[float] | None = None,
    ridges: list[float] | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    point_projection, divergence_points, manifest, paths = _load_covariant_dir(covariant_dir)
    outputs = build_support_reservoir_exchange_tables(
        point_projection,
        divergence_points,
        fit_scopes=fit_scopes,
        pf_l1_gate=pf_l1_gate,
        coordinate_error_gate=coordinate_error_gate,
        coefficient_gate=coefficient_gate,
        effective_coefficient_count_gate=effective_coefficient_count_gate,
        high_psi_source_fraction_gate=high_psi_source_fraction_gate,
        coefficient_weight=coefficient_weight,
        effective_count_weight=effective_count_weight,
        s_centers=s_centers,
        l_centers=l_centers,
        width_multipliers=width_multipliers,
        ridges=ridges,
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
        "fit_scopes": fit_scopes or ["assignment", "stage_region"],
        "pf_l1_gate": float(pf_l1_gate),
        "coordinate_error_gate": float(coordinate_error_gate),
        "coefficient_gate": float(coefficient_gate),
        "effective_coefficient_count_gate": float(effective_coefficient_count_gate),
        "high_psi_source_fraction_gate": float(high_psi_source_fraction_gate),
        "caveat": (
            "Narrow heavy-duty support-reservoir exchange fit. This tests whether "
            "the measured local tetrad exchange current J_endpoint^nu = P u^nu + F s^nu "
            "can be supplied by bounded localized smooth support-sector fields. "
            "It is a falsification screen for the support-coupled action story, not a final action proof."
        ),
    }
    return outputs, metadata


def write_support_reservoir_exchange_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "point_fit": outdir / "endpoint_support_reservoir_exchange_point_fit.csv",
        "selected_component_summary": outdir / "endpoint_support_reservoir_exchange_selected_component_summary.csv",
        "candidate_scan": outdir / "endpoint_support_reservoir_exchange_candidate_scan.csv",
        "coefficients": outdir / "endpoint_support_reservoir_exchange_coefficients.csv",
        "fit_scope_summary": outdir / "endpoint_support_reservoir_exchange_fit_scope_summary.csv",
        "decision": outdir / "endpoint_support_reservoir_exchange_decision.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "endpoint_support_reservoir_exchange_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
