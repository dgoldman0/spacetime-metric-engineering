from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .source_ledger import sha256_file, write_manifest
from .source_screening import resolve_manifest_path


EPS = 1.0e-30
TENSOR_COMPONENTS = tuple((mu, nu) for mu in range(4) for nu in range(4))
TENSOR_COLUMNS = tuple(f"Tuu_{mu}{nu}" for mu, nu in TENSOR_COMPONENTS)
DT_S_COLUMNS = tuple(f"d_s_Tuu_{mu}{nu}" for mu, nu in TENSOR_COMPONENTS)
DT_L_COLUMNS = tuple(f"d_l_Tuu_{mu}{nu}" for mu, nu in TENSOR_COMPONENTS)
KEY_COLUMNS = ("case", "s", "l")
MERGE_KEY_COLUMNS = ("case", "s_key", "l_key")


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


def _quantile(series: pd.Series, q: float) -> float:
    values = series.astype(float).replace([np.inf, -np.inf], np.nan).dropna()
    return float(values.quantile(q)) if len(values) else float("nan")


def _top_share(weights: np.ndarray, row_fraction: float) -> float:
    total = float(np.sum(weights))
    if len(weights) == 0 or total <= 0.0:
        return float("nan")
    count = max(1, int(math.ceil(float(row_fraction) * len(weights))))
    return float(np.sort(weights)[::-1][:count].sum() / total)


def _median_spacing(values: pd.Series) -> float:
    coords = np.array(sorted({_finite(value, float("nan")) for value in values}), dtype=float)
    coords = coords[np.isfinite(coords)]
    if len(coords) < 2:
        return float("nan")
    diffs = np.diff(coords)
    diffs = diffs[diffs > 0.0]
    return float(np.median(diffs)) if len(diffs) else float("nan")


def _axis_derivative(frame: pd.DataFrame, value_col: str, axis_col: str, fixed_col: str) -> pd.Series:
    result = pd.Series(np.nan, index=frame.index, dtype=float)
    for _, group in frame.groupby(fixed_col, sort=False, dropna=False):
        if len(group) < 2:
            continue
        ordered = group.sort_values(axis_col)
        coords = ordered[axis_col].astype(float).to_numpy()
        values = ordered[value_col].astype(float).to_numpy()
        derivatives = np.full(len(ordered), np.nan, dtype=float)
        for idx in range(len(ordered)):
            if idx == 0:
                dx = coords[1] - coords[0]
                if dx != 0.0:
                    derivatives[idx] = (values[1] - values[0]) / dx
            elif idx == len(ordered) - 1:
                dx = coords[-1] - coords[-2]
                if dx != 0.0:
                    derivatives[idx] = (values[-1] - values[-2]) / dx
            else:
                dx = coords[idx + 1] - coords[idx - 1]
                if dx != 0.0:
                    derivatives[idx] = (values[idx + 1] - values[idx - 1]) / dx
        result.loc[ordered.index] = derivatives
    return result


def _add_merge_keys(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["s_key"] = out["s"].astype(float).round(12)
    out["l_key"] = out["l"].astype(float).round(12)
    return out


def _metric_matrices(alpha: float, beta: float, gamma_ll: float, gamma_omega: float) -> tuple[np.ndarray, np.ndarray]:
    g = np.zeros((4, 4), dtype=float)
    g[0, 0] = -alpha * alpha + gamma_ll * beta * beta
    g[0, 1] = g[1, 0] = gamma_ll * beta
    g[1, 1] = gamma_ll
    g[2, 2] = gamma_omega
    g[3, 3] = gamma_omega

    invg = np.zeros((4, 4), dtype=float)
    invg[0, 0] = -1.0 / (alpha * alpha)
    invg[0, 1] = invg[1, 0] = beta / (alpha * alpha)
    invg[1, 1] = 1.0 / gamma_ll - beta * beta / (alpha * alpha)
    invg[2, 2] = 1.0 / gamma_omega
    invg[3, 3] = 1.0 / gamma_omega
    return g, invg


def _adm_tetrad(alpha: float, beta: float, gamma_ll: float, gamma_omega: float) -> tuple[np.ndarray, ...]:
    n = np.array([1.0 / alpha, -beta / alpha, 0.0, 0.0], dtype=float)
    e_l = np.array([0.0, 1.0 / math.sqrt(gamma_ll), 0.0, 0.0], dtype=float)
    e_th = np.array([0.0, 0.0, 1.0 / math.sqrt(gamma_omega), 0.0], dtype=float)
    e_ph = np.array([0.0, 0.0, 0.0, 1.0 / math.sqrt(gamma_omega)], dtype=float)
    return n, e_l, e_th, e_ph


def _build_tensor_row(row: pd.Series) -> dict[str, Any]:
    alpha = _finite(row["alpha"], float("nan"))
    beta = _finite(row["beta"], float("nan"))
    gamma_ll = _finite(row["gamma_ll"], float("nan"))
    gamma_omega = _finite(row["gamma_omega"], float("nan"))
    g, invg = _metric_matrices(alpha, beta, gamma_ll, gamma_omega)
    n, e_l, e_th, e_ph = _adm_tetrad(alpha, beta, gamma_ll, gamma_omega)

    rho = _finite(row["regulated_sector_rho"], float("nan"))
    p_l = _finite(row["regulated_sector_p_l"], float("nan"))
    q_l = _finite(row["regulated_sector_j_l"], float("nan"))
    p_omega = _finite(row["medium_angular_pressure"], float("nan"))
    v = _finite(row["medium_boost_velocity_to_flux_frame"], float("nan"))
    abs_v = abs(v)
    gamma = 1.0 / math.sqrt(max(1.0 - v * v, EPS)) if math.isfinite(v) and abs_v < 1.0 else float("nan")

    u = n
    s_vec = e_l
    u_cov = g @ u
    s_cov = g @ s_vec
    q_cov_vec = q_l * s_cov
    q_projector = g + np.outer(u_cov, u_cov) - np.outer(s_cov, s_cov)
    t_cov = (
        rho * np.outer(u_cov, u_cov)
        + p_l * np.outer(s_cov, s_cov)
        + p_omega * q_projector
        + np.outer(u_cov, q_cov_vec)
        + np.outer(q_cov_vec, u_cov)
    )
    t_con = invg @ t_cov @ invg

    projection = {
        "covariant_projection_rho": float(n @ t_cov @ n),
        "covariant_projection_j_l": float(-(e_l @ t_cov @ n)),
        "covariant_projection_p_l": float(e_l @ t_cov @ e_l),
        "covariant_projection_p_omega": 0.5 * float(e_th @ t_cov @ e_th + e_ph @ t_cov @ e_ph),
    }
    projection["covariant_projection_Tkk_plus_orthonormal"] = (
        projection["covariant_projection_rho"]
        + projection["covariant_projection_p_l"]
        - 2.0 * projection["covariant_projection_j_l"]
    )
    projection["covariant_projection_Tkk_minus_orthonormal"] = (
        projection["covariant_projection_rho"]
        + projection["covariant_projection_p_l"]
        + 2.0 * projection["covariant_projection_j_l"]
    )

    mixed = invg @ t_cov
    eigen = np.linalg.eigvals(mixed) if np.isfinite(mixed).all() else np.full(4, np.nan)
    max_imag = float(np.max(np.abs(np.imag(eigen)))) if len(eigen) else float("nan")
    eigen_real = np.sort(np.real(eigen)).tolist() if np.isfinite(np.real(eigen)).all() else [float("nan")] * 4

    out = {
        "medium_frame_boost_gamma": gamma,
        "medium_frame_abs_boost_velocity": abs_v,
        "mixed_eigen_max_abs_imag": max_imag,
        "mixed_eigen_all_real": bool(max_imag <= 1.0e-9),
        **{f"mixed_eigen_real_{idx}": float(value) for idx, value in enumerate(eigen_real)},
        **projection,
    }
    for mu, nu in TENSOR_COMPONENTS:
        out[f"Tcov_{mu}{nu}"] = float(t_cov[mu, nu])
        out[f"Tuu_{mu}{nu}"] = float(t_con[mu, nu])
    return out


def _prepare_projection_table(point_validation: pd.DataFrame, point_ledger: pd.DataFrame) -> pd.DataFrame:
    metric_cols = [
        "case",
        "s",
        "l",
        "stage",
        "region",
        "inside_packet_live",
        "alpha",
        "beta",
        "gamma_ll",
        "gamma_omega",
        "volume_weight",
    ]
    metric = _add_merge_keys(point_ledger[[col for col in metric_cols if col in point_ledger.columns]].copy())
    validation = _add_merge_keys(point_validation)
    merged = validation.merge(
        metric,
        on=list(MERGE_KEY_COLUMNS),
        how="left",
        suffixes=("", "_ledger"),
    )
    if "volume_weight_ledger" in merged.columns:
        merged["ledger_volume_weight"] = merged["volume_weight_ledger"].astype(float)
    else:
        merged["ledger_volume_weight"] = merged["volume_weight"].astype(float)
    required = {"alpha", "beta", "gamma_ll", "gamma_omega"}
    missing = sorted(required - set(merged.columns))
    if missing:
        raise ValueError(f"point ledger merge is missing metric columns: {missing}")
    if merged[["alpha", "beta", "gamma_ll", "gamma_omega"]].isna().any().any():
        raise ValueError("point ledger merge left missing metric values")

    tensor_rows = [_build_tensor_row(row) for _, row in merged.iterrows()]
    tensor = pd.DataFrame(tensor_rows, index=merged.index)
    out = pd.concat([merged.reset_index(drop=True), tensor.reset_index(drop=True)], axis=1)
    expected = {
        "rho": "regulated_sector_rho",
        "j_l": "regulated_sector_j_l",
        "p_l": "regulated_sector_p_l",
        "p_omega": "medium_angular_pressure",
    }
    for short, column in expected.items():
        out[f"covariant_expected_{short}"] = out[column].astype(float)
        out[f"covariant_projection_error_{short}"] = (
            out[f"covariant_projection_{short}"].astype(float) - out[f"covariant_expected_{short}"].astype(float)
        )
    out["covariant_expected_Tkk_plus_orthonormal"] = (
        out["covariant_expected_rho"] + out["covariant_expected_p_l"] - 2.0 * out["covariant_expected_j_l"]
    )
    out["covariant_expected_Tkk_minus_orthonormal"] = (
        out["covariant_expected_rho"] + out["covariant_expected_p_l"] + 2.0 * out["covariant_expected_j_l"]
    )
    for branch in ("plus", "minus"):
        out[f"covariant_projection_error_Tkk_{branch}_orthonormal"] = (
            out[f"covariant_projection_Tkk_{branch}_orthonormal"].astype(float)
            - out[f"covariant_expected_Tkk_{branch}_orthonormal"].astype(float)
        )
    error_cols = [
        "covariant_projection_error_rho",
        "covariant_projection_error_j_l",
        "covariant_projection_error_p_l",
        "covariant_projection_error_p_omega",
        "covariant_projection_error_Tkk_plus_orthonormal",
        "covariant_projection_error_Tkk_minus_orthonormal",
    ]
    out["covariant_projection_linf_error"] = out[error_cols].abs().max(axis=1)
    local_scale = (
        out["covariant_expected_rho"].abs()
        + out["covariant_expected_p_l"].abs()
        + 2.0 * out["covariant_expected_j_l"].abs()
        + out["covariant_expected_p_omega"].abs()
    )
    out["covariant_projection_relative_error"] = out["covariant_projection_linf_error"] / (local_scale + EPS)
    return out


def _add_metric_derivatives(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["g00"] = -np.square(out["alpha"].astype(float)) + out["gamma_ll"].astype(float) * np.square(out["beta"].astype(float))
    out["g01"] = out["gamma_ll"].astype(float) * out["beta"].astype(float)
    out["g11"] = out["gamma_ll"].astype(float)
    out["g22"] = out["gamma_omega"].astype(float)
    out["g33"] = out["gamma_omega"].astype(float)
    for col in ("g00", "g01", "g11", "g22", "g33"):
        out[f"d_s_{col}"] = _axis_derivative(out, col, "s", "l")
        out[f"d_l_{col}"] = _axis_derivative(out, col, "l", "s")
    return out


def _christoffel_from_row(row: pd.Series) -> np.ndarray:
    alpha = float(row["alpha"])
    beta = float(row["beta"])
    gamma_ll = float(row["gamma_ll"])
    gamma_omega = float(row["gamma_omega"])
    _g, invg = _metric_matrices(alpha, beta, gamma_ll, gamma_omega)
    dg = np.zeros((4, 4, 4), dtype=float)
    for coord, prefix in ((0, "d_s"), (1, "d_l")):
        dg[coord, 0, 0] = _finite(row[f"{prefix}_g00"])
        dg[coord, 0, 1] = dg[coord, 1, 0] = _finite(row[f"{prefix}_g01"])
        dg[coord, 1, 1] = _finite(row[f"{prefix}_g11"])
        dg[coord, 2, 2] = _finite(row[f"{prefix}_g22"])
        dg[coord, 3, 3] = _finite(row[f"{prefix}_g33"])

    gamma = np.zeros((4, 4, 4), dtype=float)
    for rho in range(4):
        for mu in range(4):
            for nu in range(4):
                total = 0.0
                for sig in range(4):
                    total += invg[rho, sig] * (dg[mu, nu, sig] + dg[nu, mu, sig] - dg[sig, mu, nu])
                gamma[rho, mu, nu] = 0.5 * total
    return gamma


def _prepare_divergence_table(point_projection: pd.DataFrame, point_ledger: pd.DataFrame) -> pd.DataFrame:
    base_cols = [
        "case",
        "s",
        "l",
        "stage",
        "region",
        "inside_packet_live",
        "inside_packet_geom",
        "alpha",
        "beta",
        "gamma_ll",
        "gamma_omega",
        "volume_weight",
        "support_shell_window",
        "support_edge_receiver_radial_cap_window",
        "support_edge_receiver_angular_flange_window",
    ]
    full = _add_merge_keys(point_ledger[[col for col in base_cols if col in point_ledger.columns]].copy())
    tensor_cols = list(KEY_COLUMNS) + [
        "assignment",
        "source_abs_density",
        "medium_frame_abs_boost_velocity",
        "mixed_eigen_max_abs_imag",
        *TENSOR_COLUMNS,
    ]
    active = _add_merge_keys(point_projection[tensor_cols].copy())
    full = full.merge(active, on=list(MERGE_KEY_COLUMNS), how="left", suffixes=("", "_active"))
    full["medium_source_active"] = full["assignment"].notna()
    full["assignment"] = full["assignment"].fillna("")
    full["source_abs_density"] = full["source_abs_density"].fillna(0.0)
    for col in TENSOR_COLUMNS:
        full[col] = full[col].fillna(0.0)
    full = _add_metric_derivatives(full)
    h_s = _median_spacing(full["s"])
    h_l = _median_spacing(full["l"])
    finite_spacings = [value for value in (h_s, h_l) if math.isfinite(value) and value > 0.0]
    h_ref = min(finite_spacings) if finite_spacings else 1.0

    for col, (mu, nu) in zip(TENSOR_COLUMNS, TENSOR_COMPONENTS):
        full[f"d_s_Tuu_{mu}{nu}"] = _axis_derivative(full, col, "s", "l")
        full[f"d_l_Tuu_{mu}{nu}"] = _axis_derivative(full, col, "l", "s")

    derivative_scale = np.zeros(len(full), dtype=float)
    for col in (*DT_S_COLUMNS, *DT_L_COLUMNS):
        derivative_scale += np.square(full[col].fillna(0.0).astype(float).to_numpy())
    tensor_scale = np.zeros(len(full), dtype=float)
    for col in TENSOR_COLUMNS:
        tensor_scale += np.square(full[col].astype(float).to_numpy())
    scoreable = (derivative_scale > 0.0) | (tensor_scale > 0.0)

    divergences = np.zeros((len(full), 4), dtype=float)
    selected_indices = np.flatnonzero(scoreable)
    for idx in selected_indices:
        row = full.iloc[int(idx)]
        gamma = _christoffel_from_row(row)
        t_con = np.zeros((4, 4), dtype=float)
        ds_t = np.zeros((4, 4), dtype=float)
        dl_t = np.zeros((4, 4), dtype=float)
        for mu, nu in TENSOR_COMPONENTS:
            t_con[mu, nu] = float(row[f"Tuu_{mu}{nu}"])
            ds_t[mu, nu] = _finite(row[f"d_s_Tuu_{mu}{nu}"])
            dl_t[mu, nu] = _finite(row[f"d_l_Tuu_{mu}{nu}"])
        for nu in range(4):
            value = ds_t[0, nu] + dl_t[1, nu]
            for mu in range(4):
                for lam in range(4):
                    value += gamma[mu, mu, lam] * t_con[lam, nu]
                    value += gamma[nu, mu, lam] * t_con[mu, lam]
            divergences[idx, nu] = value

    for nu in range(4):
        full[f"covariant_divergence_{nu}"] = divergences[:, nu]
    full["covariant_divergence_l2_density"] = np.sqrt(np.sum(np.square(divergences), axis=1))
    full["covariant_divergence_volume"] = full["covariant_divergence_l2_density"] * full["volume_weight"].astype(float)
    full["covariant_divergence_norm_on_active"] = np.where(
        full["source_abs_density"].astype(float) > 0.0,
        full["covariant_divergence_l2_density"] / (full["source_abs_density"].astype(float) / h_ref + EPS),
        np.nan,
    )
    live = _bool_series(full["inside_packet_live"]) if "inside_packet_live" in full else pd.Series(False, index=full.index)
    full["covariant_divergence_live"] = live
    allowed = full["medium_source_active"].astype(bool)
    if "region" in full:
        allowed = allowed | full["region"].astype(str).isin({"support_edge", "core_throat"})
    if "stage" in full:
        allowed = allowed | (full["stage"].astype(str) == "reset_decompression")
    for col in (
        "support_shell_window",
        "support_edge_receiver_radial_cap_window",
        "support_edge_receiver_angular_flange_window",
    ):
        if col in full:
            allowed = allowed | (full[col].fillna(0.0).astype(float).abs() > 1.0e-12)
    full["covariant_exchange_allowed_mask"] = allowed & (~live)
    full["h_s_median"] = h_s
    full["h_l_median"] = h_l
    full["h_ref"] = h_ref
    return full.loc[scoreable | (full["covariant_divergence_l2_density"] > 0.0)].copy()


def _scope_summary(scope: str, frame: pd.DataFrame, *, projection_error_gate: float) -> dict[str, Any]:
    volume = frame["ledger_volume_weight"].astype(float).to_numpy()
    source_volume = frame["source_abs_density"].astype(float).to_numpy() * volume
    error_volume = frame["covariant_projection_linf_error"].astype(float).to_numpy() * volume
    return {
        "scope": scope,
        "assignment": "" if scope == "J_total" else str(frame["assignment"].iloc[0]) if len(frame) else "",
        "rows": int(len(frame)),
        "source_abs_volume": float(np.sum(source_volume)),
        "max_projection_linf_error": float(frame["covariant_projection_linf_error"].astype(float).max()) if len(frame) else float("nan"),
        "p99_projection_linf_error": _quantile(frame["covariant_projection_linf_error"], 0.99),
        "projection_error_to_source_ratio": _safe_ratio(float(np.sum(error_volume)), float(np.sum(source_volume))),
        "projection_relative_error_p99": _quantile(frame["covariant_projection_relative_error"], 0.99),
        "projection_error_gate": float(projection_error_gate),
        "projection_reconstruction_pass": bool(
            len(frame) > 0 and float(frame["covariant_projection_linf_error"].astype(float).max()) <= float(projection_error_gate)
        ),
        "max_abs_boost_velocity": float(frame["medium_frame_abs_boost_velocity"].astype(float).max()) if len(frame) else float("nan"),
        "boost_subluminal_rows": int((frame["medium_frame_abs_boost_velocity"].astype(float) < 1.0).sum()),
        "boost_superluminal_or_nan_rows": int(
            (~np.isfinite(frame["medium_frame_abs_boost_velocity"].astype(float))
             | (frame["medium_frame_abs_boost_velocity"].astype(float) >= 1.0)).sum()
        ),
        "mixed_eigen_complex_rows": int((frame["mixed_eigen_max_abs_imag"].astype(float) > 1.0e-9).sum()),
        "max_mixed_eigen_imag": float(frame["mixed_eigen_max_abs_imag"].astype(float).max()) if len(frame) else float("nan"),
    }


def _build_scope_summary(point_projection: pd.DataFrame, *, projection_error_gate: float) -> pd.DataFrame:
    rows = [_scope_summary("J_total", point_projection, projection_error_gate=projection_error_gate)]
    for assignment, group in point_projection.groupby("assignment", sort=False, dropna=False):
        rows.append(_scope_summary(str(assignment), group, projection_error_gate=projection_error_gate))
    return pd.DataFrame(rows)


def _divergence_summary(divergence: pd.DataFrame, *, outside_exchange_gate: float, live_exchange_gate: float) -> pd.DataFrame:
    volume = divergence["covariant_divergence_volume"].astype(float).to_numpy()
    total = float(np.sum(volume))
    live = divergence["covariant_divergence_live"].astype(bool).to_numpy()
    allowed = divergence["covariant_exchange_allowed_mask"].astype(bool).to_numpy()
    active = divergence["medium_source_active"].astype(bool).to_numpy()
    live_total = float(np.sum(volume[live]))
    allowed_total = float(np.sum(volume[allowed]))
    active_total = float(np.sum(volume[active]))
    outside_total = float(np.sum(volume[~allowed]))
    outside_fraction = 0.0 if total <= 0.0 else _safe_ratio(outside_total, total)
    live_fraction = 0.0 if total <= 0.0 else _safe_ratio(live_total, total)
    rows = [{
        "scope": "full_grid_exchange",
        "rows": int(len(divergence)),
        "scoreable_divergence_volume": total,
        "active_source_divergence_volume": active_total,
        "allowed_exchange_divergence_volume": allowed_total,
        "outside_allowed_divergence_volume": outside_total,
        "live_divergence_volume": live_total,
        "active_source_divergence_fraction": _safe_ratio(active_total, total),
        "allowed_exchange_divergence_fraction": _safe_ratio(allowed_total, total),
        "outside_allowed_divergence_fraction": outside_fraction,
        "live_divergence_fraction": live_fraction,
        "outside_exchange_gate": float(outside_exchange_gate),
        "live_exchange_gate": float(live_exchange_gate),
        "exchange_localization_pass": bool(
            outside_fraction <= float(outside_exchange_gate)
            and live_fraction <= float(live_exchange_gate)
        ),
        "weighted_mean_active_divergence_norm": float(
            np.average(
                divergence.loc[active, "covariant_divergence_norm_on_active"].fillna(0.0).astype(float),
                weights=divergence.loc[active, "volume_weight"].astype(float),
            )
        )
        if np.any(active)
        else float("nan"),
        "peak_active_divergence_norm": float(
            divergence.loc[active, "covariant_divergence_norm_on_active"].astype(float).replace([np.inf, -np.inf], np.nan).max()
        )
        if np.any(active)
        else float("nan"),
        "peak_divergence_density": float(divergence["covariant_divergence_l2_density"].astype(float).max())
        if len(divergence)
        else float("nan"),
        "top_1pct_divergence_burden_share": _top_share(volume, 0.01),
    }]
    for assignment, group in divergence.loc[divergence["medium_source_active"].astype(bool)].groupby("assignment", sort=False):
        group_volume = group["covariant_divergence_volume"].astype(float).to_numpy()
        rows.append({
            "scope": str(assignment),
            "rows": int(len(group)),
            "scoreable_divergence_volume": float(np.sum(group_volume)),
            "active_source_divergence_volume": float(np.sum(group_volume)),
            "allowed_exchange_divergence_volume": float(np.sum(group_volume)),
            "outside_allowed_divergence_volume": 0.0,
            "live_divergence_volume": float(np.sum(group.loc[group["covariant_divergence_live"].astype(bool), "covariant_divergence_volume"])),
            "active_source_divergence_fraction": 1.0,
            "allowed_exchange_divergence_fraction": 1.0,
            "outside_allowed_divergence_fraction": 0.0,
            "live_divergence_fraction": _safe_ratio(
                float(np.sum(group.loc[group["covariant_divergence_live"].astype(bool), "covariant_divergence_volume"])),
                float(np.sum(group_volume)),
            ),
            "outside_exchange_gate": float(outside_exchange_gate),
            "live_exchange_gate": float(live_exchange_gate),
            "exchange_localization_pass": bool(
                _safe_ratio(
                    float(np.sum(group.loc[group["covariant_divergence_live"].astype(bool), "covariant_divergence_volume"])),
                    float(np.sum(group_volume)),
                )
                <= float(live_exchange_gate)
            ),
            "weighted_mean_active_divergence_norm": float(
                np.average(
                    group["covariant_divergence_norm_on_active"].fillna(0.0).astype(float),
                    weights=group["volume_weight"].astype(float),
                )
            )
            if len(group)
            else float("nan"),
            "peak_active_divergence_norm": float(group["covariant_divergence_norm_on_active"].astype(float).max())
            if len(group)
            else float("nan"),
            "peak_divergence_density": float(group["covariant_divergence_l2_density"].astype(float).max())
            if len(group)
            else float("nan"),
            "top_1pct_divergence_burden_share": _top_share(group_volume, 0.01),
        })
    return pd.DataFrame(rows)


def _decision(scope_summary: pd.DataFrame, divergence_summary: pd.DataFrame) -> pd.DataFrame:
    projection_pass = bool(scope_summary["projection_reconstruction_pass"].astype(bool).all())
    boost_pass = int(scope_summary["boost_superluminal_or_nan_rows"].astype(int).sum()) == 0
    eigen_pass = int(scope_summary["mixed_eigen_complex_rows"].astype(int).sum()) == 0
    exchange = divergence_summary.loc[divergence_summary["scope"].astype(str) == "full_grid_exchange"]
    exchange_pass = bool(exchange["exchange_localization_pass"].astype(bool).iloc[0]) if len(exchange) else False
    hard_pass = bool(projection_pass and boost_pass and eigen_pass and exchange_pass)
    total = scope_summary.loc[scope_summary["scope"].astype(str) == "J_total"].iloc[0]
    exchange_row = exchange.iloc[0] if len(exchange) else {}
    return pd.DataFrame([{
        "covariant_identity_status": "covariant_endpoint_medium_identity_pass" if hard_pass else "covariant_endpoint_medium_identity_watch",
        "passes_covariant_identity_audit": hard_pass,
        "projection_reconstruction_pass": projection_pass,
        "max_projection_linf_error": _finite(total.get("max_projection_linf_error"), float("nan")),
        "projection_error_to_source_ratio": _finite(total.get("projection_error_to_source_ratio"), float("nan")),
        "boost_subluminal_pass": boost_pass,
        "max_abs_boost_velocity": _finite(total.get("max_abs_boost_velocity"), float("nan")),
        "mixed_eigen_real_pass": eigen_pass,
        "max_mixed_eigen_imag": _finite(total.get("max_mixed_eigen_imag"), float("nan")),
        "exchange_localization_pass": exchange_pass,
        "outside_allowed_divergence_fraction": _finite(exchange_row.get("outside_allowed_divergence_fraction"), float("nan"))
        if len(exchange)
        else float("nan"),
        "live_divergence_fraction": _finite(exchange_row.get("live_divergence_fraction"), float("nan"))
        if len(exchange)
        else float("nan"),
        "weighted_mean_active_divergence_norm": _finite(
            exchange_row.get("weighted_mean_active_divergence_norm"),
            float("nan"),
        )
        if len(exchange)
        else float("nan"),
        "peak_active_divergence_norm": _finite(exchange_row.get("peak_active_divergence_norm"), float("nan"))
        if len(exchange)
        else float("nan"),
        "decision_read": (
            "regulated medium variables lift to one tensor whose ADM projections close; divergence is localized to allowed endpoint/support exchange masks"
            if hard_pass
            else "one or more covariant identity gates require interpretation before promotion beyond field-closure level"
        ),
    }])


def build_endpoint_medium_covariant_audit_tables(
    point_validation: pd.DataFrame,
    point_ledger: pd.DataFrame,
    *,
    projection_error_gate: float = 1.0e-9,
    outside_exchange_gate: float = 0.05,
    live_exchange_gate: float = 0.005,
    top_limit: int = 80,
) -> dict[str, pd.DataFrame]:
    point_projection = _prepare_projection_table(point_validation, point_ledger)
    divergence_points = _prepare_divergence_table(point_projection, point_ledger)
    scope_summary = _build_scope_summary(point_projection, projection_error_gate=projection_error_gate)
    div_summary = _divergence_summary(
        divergence_points,
        outside_exchange_gate=outside_exchange_gate,
        live_exchange_gate=live_exchange_gate,
    )
    decision = _decision(scope_summary, div_summary)
    top_divergence = (
        divergence_points.sort_values("covariant_divergence_volume", ascending=False)
        .head(int(top_limit))
        .reset_index(drop=True)
    )
    keep_cols = [
        "case",
        "s",
        "l",
        "stage",
        "region",
        "assignment",
        "medium_source_active",
        "covariant_exchange_allowed_mask",
        "covariant_divergence_live",
        "covariant_divergence_l2_density",
        "covariant_divergence_volume",
        "covariant_divergence_norm_on_active",
        "source_abs_density",
    ]
    top_divergence = top_divergence[[col for col in keep_cols if col in top_divergence.columns]]
    return {
        "point_projection": point_projection,
        "divergence_points": divergence_points,
        "scope_summary": scope_summary,
        "divergence_summary": div_summary,
        "top_divergence": top_divergence,
        "decision": decision,
    }


def _load_field_closure_dir(field_closure_dir: Path) -> tuple[pd.DataFrame, dict[str, Any], Path]:
    manifest_path = field_closure_dir / "endpoint_medium_field_closure_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    value = manifest.get("files", {}).get("point_validation", "endpoint_medium_field_closure_point_validation.csv")
    path = resolve_manifest_path(field_closure_dir, value)
    return pd.read_csv(path), manifest, path


def _infer_point_ledger_from_field_manifest(field_closure_dir: Path, manifest: dict[str, Any]) -> Path:
    fit_dir = resolve_manifest_path(field_closure_dir, manifest["fit_dir"])
    closure_manifest_path = fit_dir / "endpoint_j_closure_component_manifest.json"
    closure_manifest = json.loads(closure_manifest_path.read_text())
    intermediate_dir = resolve_manifest_path(fit_dir, closure_manifest["intermediate_dir"])
    intermediate_manifest = json.loads((intermediate_dir / "intermediate_source_model_manifest.json").read_text())
    component_dir = resolve_manifest_path(intermediate_dir, intermediate_manifest["component_source_dir"])
    component_manifest = json.loads((component_dir / "component_source_manifest.json").read_text())
    ledger_entry = component_manifest["ledgers"][0]
    return resolve_manifest_path(component_dir, ledger_entry["point_ledger"])


def build_endpoint_medium_covariant_audit(
    field_closure_dir: Path,
    *,
    point_ledger_path: Path | None = None,
    projection_error_gate: float = 1.0e-9,
    outside_exchange_gate: float = 0.05,
    live_exchange_gate: float = 0.005,
    top_limit: int = 80,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    point_validation, manifest, point_validation_path = _load_field_closure_dir(field_closure_dir)
    ledger_path = point_ledger_path or _infer_point_ledger_from_field_manifest(field_closure_dir, manifest)
    point_ledger = pd.read_csv(ledger_path)
    outputs = build_endpoint_medium_covariant_audit_tables(
        point_validation,
        point_ledger,
        projection_error_gate=projection_error_gate,
        outside_exchange_gate=outside_exchange_gate,
        live_exchange_gate=live_exchange_gate,
        top_limit=top_limit,
    )
    metadata = {
        "field_closure_dir": str(field_closure_dir),
        "field_closure_manifest": str(field_closure_dir / "endpoint_medium_field_closure_manifest.json"),
        "point_validation": str(point_validation_path),
        "point_validation_sha256": sha256_file(point_validation_path),
        "point_ledger": str(ledger_path),
        "point_ledger_sha256": sha256_file(ledger_path),
        "projection_error_gate": float(projection_error_gate),
        "outside_exchange_gate": float(outside_exchange_gate),
        "live_exchange_gate": float(live_exchange_gate),
        "top_limit": int(top_limit),
        "caveat": (
            "Covariant endpoint-medium identity audit. The regulated medium is lifted to a "
            "spacetime stress tensor on the service metric using ADM-frame radial heat/current "
            "variables; the boost-to-flux-frame remains an admissibility diagnostic. The tensor "
            "is projected back to ADM channels and checked with a "
            "finite-difference covariant-divergence diagnostic. This is not a matter-action theorem."
        ),
    }
    return outputs, metadata


def write_endpoint_medium_covariant_audit_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "point_projection": outdir / "endpoint_medium_covariant_point_projection.csv",
        "divergence_points": outdir / "endpoint_medium_covariant_divergence_points.csv",
        "scope_summary": outdir / "endpoint_medium_covariant_scope_summary.csv",
        "divergence_summary": outdir / "endpoint_medium_covariant_divergence_summary.csv",
        "top_divergence": outdir / "endpoint_medium_covariant_top_divergence.csv",
        "decision": outdir / "endpoint_medium_covariant_decision.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "endpoint_medium_covariant_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
