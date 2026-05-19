from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .source_ledger import sha256_file, write_manifest
from .source_screening import resolve_manifest_path


DEFAULT_PHI0_VALUES = (0.05, 0.10, 0.20, 0.50, 1.00, 2.00)
DEFAULT_XI_VALUES = (0.0, 1.0 / 6.0, 0.50, 1.00, 2.00)
DEFAULT_PROFILES = ("standing_support", "compact_handoff", "core_throat", "support_edge")


@dataclass(frozen=True)
class LedgerInput:
    label: str
    ledger_dir: Path
    manifest_path: Path
    point_ledger_path: Path
    manifest: dict[str, Any]


def load_ledger_input(ledger_dir: Path, label: str | None = None) -> LedgerInput:
    manifest_path = ledger_dir / "source_ledger_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    files = manifest.get("files", {})
    point_value = files.get("point_ledger", "source_ledger_point_ledger.csv")
    point_ledger_path = resolve_manifest_path(ledger_dir, point_value)
    return LedgerInput(
        label=label or str(manifest.get("case") or ledger_dir.name),
        ledger_dir=ledger_dir,
        manifest_path=manifest_path,
        point_ledger_path=point_ledger_path,
        manifest=manifest,
    )


def _finite(values: pd.Series | np.ndarray, default: float = 0.0) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    return np.nan_to_num(arr, nan=default, posinf=default, neginf=default)


def _normalize(arr: np.ndarray) -> np.ndarray:
    values = np.nan_to_num(np.asarray(arr, dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    max_abs = float(np.max(np.abs(values))) if values.size else 0.0
    if max_abs <= 0.0:
        return np.zeros_like(values)
    return values / max_abs


def _stage_weight(points: pd.DataFrame, names: Iterable[str]) -> np.ndarray:
    stages = points["stage"].astype(str)
    mask = np.zeros(len(points), dtype=bool)
    for name in names:
        mask |= stages.eq(name).to_numpy()
    return mask.astype(float)


def _region_weight(points: pd.DataFrame, names: Iterable[str]) -> np.ndarray:
    regions = points["region"].astype(str)
    mask = np.zeros(len(points), dtype=bool)
    for name in names:
        mask |= regions.eq(name).to_numpy()
    return mask.astype(float)


def scalar_profile(points: pd.DataFrame, profile: str) -> np.ndarray:
    """Return a dimensionless scalar support profile on the source-ledger grid.

    These profiles are deliberately reduced ansatz families. They are meant to
    screen whether a simple scalar support placement has the right broad signs
    and scales, not to certify a full scalar-tensor solution.
    """

    key = profile.strip().lower()
    zeros = np.zeros(len(points), dtype=float)
    if key == "standing_support":
        return _normalize(points.get("W_raw", points.get("W", zeros)))
    if key == "carved_support":
        return _normalize(points.get("W", zeros))
    if key == "compact_handoff":
        columns = [
            "standing_support_packet_smooth_split_entry_window",
            "standing_support_packet_smooth_split_catch_window",
            "standing_support_packet_smooth_split_edge_window",
            "standing_support_packet_smooth_split_null_cushion_window",
        ]
        parts = [_finite(points[col]) for col in columns if col in points.columns]
        if not parts:
            return _normalize(points.get("W", zeros))
        return _normalize(np.maximum.reduce(parts))
    if key == "core_throat":
        support = _normalize(points.get("W_raw", points.get("W", zeros)))
        return _normalize(support * _region_weight(points, ["core_throat"]))
    if key == "support_edge":
        support = _normalize(points.get("W_raw", points.get("W", zeros)))
        return _normalize(support * _region_weight(points, ["support_edge"]))
    if key == "catch_support":
        support = _normalize(points.get("W_raw", points.get("W", zeros)))
        return _normalize(support * _stage_weight(points, ["catch_rematch"]))
    if key == "packet_exclusion":
        columns = [
            "standing_support_packet_smooth_split_containment_window",
            "standing_support_packet_carve_window",
            "standing_support_packet_carve_catch_window",
        ]
        parts = [_finite(points[col]) for col in columns if col in points.columns]
        if not parts:
            return zeros
        return _normalize(np.maximum.reduce(parts))
    raise ValueError(f"unknown scalar profile: {profile}")


def _grid_values(points: pd.DataFrame, values: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    work = points[["s", "l"]].copy()
    work["_value"] = np.asarray(values, dtype=float)
    # Duplicates should not occur in a source ledger, but averaging makes the
    # screen robust to concatenated ledgers or hand-edited tables.
    table = work.pivot_table(index="s", columns="l", values="_value", aggfunc="mean").sort_index().sort_index(axis=1)
    if table.isna().any().any():
        table = table.interpolate(axis=0).interpolate(axis=1).fillna(0.0)
    s_grid = table.index.to_numpy(dtype=float)
    l_grid = table.columns.to_numpy(dtype=float)
    return s_grid, l_grid, table.to_numpy(dtype=float)


def _back_to_points(points: pd.DataFrame, values_2d: np.ndarray, s_grid: np.ndarray, l_grid: np.ndarray) -> np.ndarray:
    index_s = {float(value): idx for idx, value in enumerate(s_grid)}
    index_l = {float(value): idx for idx, value in enumerate(l_grid)}
    out = np.empty(len(points), dtype=float)
    for i, row in enumerate(points[["s", "l"]].itertuples(index=False)):
        out[i] = values_2d[index_s[float(row.s)], index_l[float(row.l)]]
    return out


def scalar_proxy_fields(points: pd.DataFrame, phi0: float, xi: float, profile: str) -> pd.DataFrame:
    profile_values = scalar_profile(points, profile)
    phi = float(phi0) * profile_values
    return scalar_proxy_fields_from_phi(points, phi, xi)


def scalar_proxy_fields_from_phi(points: pd.DataFrame, phi: np.ndarray, xi: float) -> pd.DataFrame:
    s_grid, l_grid, phi_2d = _grid_values(points, phi)
    edge_order = 2 if min(len(s_grid), len(l_grid)) >= 3 else 1
    d_s, d_l = np.gradient(phi_2d, s_grid, l_grid, edge_order=edge_order)
    d2_s, d_sl = np.gradient(d_s, s_grid, l_grid, edge_order=edge_order)
    _d_ls, d2_l = np.gradient(d_l, s_grid, l_grid, edge_order=edge_order)
    phi_sq = phi_2d * phi_2d
    q_s, q_l = np.gradient(phi_sq, s_grid, l_grid, edge_order=edge_order)
    q2_s, q_sl = np.gradient(q_s, s_grid, l_grid, edge_order=edge_order)
    _q_ls, q2_l = np.gradient(q_l, s_grid, l_grid, edge_order=edge_order)

    phi_v = _back_to_points(points, phi_2d, s_grid, l_grid)
    d_s_v = _back_to_points(points, d_s, s_grid, l_grid)
    d_l_v = _back_to_points(points, d_l, s_grid, l_grid)
    d2_s_v = _back_to_points(points, d2_s, s_grid, l_grid)
    d2_l_v = _back_to_points(points, d2_l, s_grid, l_grid)
    d_sl_v = _back_to_points(points, d_sl, s_grid, l_grid)
    q2_s_v = _back_to_points(points, q2_s, s_grid, l_grid)
    q2_l_v = _back_to_points(points, q2_l, s_grid, l_grid)
    q_sl_v = _back_to_points(points, q_sl, s_grid, l_grid)

    alpha = np.maximum(_finite(points.get("alpha", np.ones(len(points))), default=1.0), 1.0e-12)
    gamma_ll = np.maximum(_finite(points.get("gamma_ll", np.ones(len(points))), default=1.0), 1.0e-12)
    gamma_omega = np.maximum(_finite(points.get("gamma_omega", np.ones(len(points))), default=1.0), 1.0e-12)
    sqrt_gamma_ll = np.sqrt(gamma_ll)
    # A reduced orthonormal radial-null derivative. This is a proxy, not a
    # replacement for the full nonminimal scalar stress tensor.
    grad_null = d_s_v / alpha + d_l_v / sqrt_gamma_ll
    hess_null = q2_s_v / (alpha * alpha) + 2.0 * q_sl_v / (alpha * sqrt_gamma_ll) + q2_l_v / gamma_ll
    grad_norm = (d_s_v / alpha) ** 2 + (d_l_v / sqrt_gamma_ll) ** 2

    tkk_proxy = grad_null * grad_null - float(xi) * hess_null
    current_proxy = -d_s_v * d_l_v / (alpha * sqrt_gamma_ll) + float(xi) * q_sl_v / (alpha * sqrt_gamma_ll)
    radial_pressure_proxy = 0.5 * ((d_l_v / sqrt_gamma_ll) ** 2 - (d_s_v / alpha) ** 2) - float(xi) * q2_l_v / gamma_ll
    angular_pressure_proxy = 0.5 * grad_norm - float(xi) * phi_v * phi_v / gamma_omega
    stress_abs_proxy = (
        np.maximum(-tkk_proxy, 0.0)
        + np.abs(current_proxy)
        + np.abs(radial_pressure_proxy)
        + np.abs(angular_pressure_proxy)
    )

    return pd.DataFrame({
        "phi": phi_v,
        "d_s_phi": d_s_v,
        "d_l_phi": d_l_v,
        "d2_s_phi": d2_s_v,
        "d2_l_phi": d2_l_v,
        "d_sl_phi": d_sl_v,
        "grad_norm_proxy": grad_norm,
        "scalar_Tkk_radial_proxy": tkk_proxy,
        "scalar_abs_j_l_proxy": np.abs(current_proxy),
        "scalar_abs_p_l_proxy": np.abs(radial_pressure_proxy),
        "scalar_abs_pOmega_proxy": np.abs(angular_pressure_proxy),
        "scalar_stress_abs_proxy": stress_abs_proxy,
    })


def _weighted_corr(x: np.ndarray, y: np.ndarray, w: np.ndarray) -> float:
    mask = np.isfinite(x) & np.isfinite(y) & np.isfinite(w) & (w > 0.0)
    if int(mask.sum()) < 3:
        return float("nan")
    x_m = x[mask]
    y_m = y[mask]
    w_m = w[mask]
    w_sum = float(np.sum(w_m))
    x_mean = float(np.sum(w_m * x_m) / w_sum)
    y_mean = float(np.sum(w_m * y_m) / w_sum)
    cov = float(np.sum(w_m * (x_m - x_mean) * (y_m - y_mean)) / w_sum)
    vx = float(np.sum(w_m * (x_m - x_mean) ** 2) / w_sum)
    vy = float(np.sum(w_m * (y_m - y_mean) ** 2) / w_sum)
    if vx <= 0.0 or vy <= 0.0:
        return float("nan")
    return cov / math.sqrt(vx * vy)


def _fit_scale(demand: np.ndarray, supply: np.ndarray, weight: np.ndarray) -> tuple[float, float, float]:
    mask = np.isfinite(demand) & np.isfinite(supply) & np.isfinite(weight) & (weight > 0.0)
    if int(mask.sum()) == 0:
        return float("nan"), float("nan"), float("nan")
    d = demand[mask]
    s = supply[mask]
    w = weight[mask]
    denom = float(np.sum(w * s * s))
    scale = float(np.sum(w * d * s) / denom) if denom > 0.0 else 0.0
    fit = scale * s
    residual = float(np.sum(w * np.abs(d - fit)) / max(np.sum(w * np.abs(d)), 1.0e-30))
    coverage = float(np.sum(w * np.minimum(np.abs(fit), np.abs(d))) / max(np.sum(w * np.abs(d)), 1.0e-30))
    return scale, residual, coverage


def score_scalar_candidate(points: pd.DataFrame, proxy: pd.DataFrame) -> dict[str, float]:
    weight = _finite(points.get("volume_weight", np.ones(len(points))), default=1.0)
    live = points["inside_packet_live"].astype(bool).to_numpy() if "inside_packet_live" in points else np.zeros(len(points), dtype=bool)
    demands = {
        "neg_Tkk_radial": _finite(points["bad_neg_Tkk_radial"]),
        "abs_p_l": _finite(points["bad_abs_p_l"]),
        "abs_j_l": _finite(points["bad_abs_j_l"]),
        "abs_pOmega": _finite(points["bad_abs_pOmega"]),
    }
    supplies = {
        "neg_Tkk_radial": np.maximum(-_finite(proxy["scalar_Tkk_radial_proxy"]), 0.0),
        "abs_p_l": _finite(proxy["scalar_abs_p_l_proxy"]),
        "abs_j_l": _finite(proxy["scalar_abs_j_l_proxy"]),
        "abs_pOmega": _finite(proxy["scalar_abs_pOmega_proxy"]),
    }
    rows: dict[str, float] = {}
    residuals = []
    coverages = []
    for channel in demands:
        scale, residual, coverage = _fit_scale(demands[channel], supplies[channel], weight)
        corr = _weighted_corr(demands[channel], supplies[channel], weight)
        rows[f"{channel}_fit_scale"] = scale
        rows[f"{channel}_relative_l1_residual"] = residual
        rows[f"{channel}_coverage"] = coverage
        rows[f"{channel}_weighted_corr"] = corr
        if math.isfinite(residual):
            residuals.append(residual)
        if math.isfinite(coverage):
            coverages.append(coverage)

    stress = _finite(proxy["scalar_stress_abs_proxy"])
    total_stress = float(np.sum(weight * stress))
    live_stress = float(np.sum(weight[live] * stress[live])) if live.any() else 0.0
    rows["scalar_total_stress_proxy"] = total_stress
    rows["scalar_live_stress_proxy"] = live_stress
    rows["scalar_live_stress_fraction"] = live_stress / total_stress if total_stress > 0.0 else float("nan")
    rows["max_abs_phi"] = float(np.max(np.abs(_finite(proxy["phi"]))))
    rows["max_grad_phi_proxy"] = float(np.sqrt(np.max(_finite(proxy["grad_norm_proxy"]))))
    rows["max_abs_d2_phi_proxy"] = float(max(np.max(np.abs(_finite(proxy["d2_s_phi"]))), np.max(np.abs(_finite(proxy["d2_l_phi"])))))
    rows["mean_relative_l1_residual"] = float(np.mean(residuals)) if residuals else float("nan")
    rows["mean_coverage"] = float(np.mean(coverages)) if coverages else float("nan")
    return rows


def screen_ledger(
    ledger: LedgerInput,
    *,
    phi0_values: Iterable[float] = DEFAULT_PHI0_VALUES,
    xi_values: Iterable[float] = DEFAULT_XI_VALUES,
    profiles: Iterable[str] = DEFAULT_PROFILES,
) -> pd.DataFrame:
    points = pd.read_csv(ledger.point_ledger_path)
    rows: list[dict[str, Any]] = []
    for profile in profiles:
        for phi0 in phi0_values:
            for xi in xi_values:
                proxy = scalar_proxy_fields(points, float(phi0), float(xi), str(profile))
                score = score_scalar_candidate(points, proxy)
                effective_coupling_margin = 1.0 - 8.0 * math.pi * float(xi) * score["max_abs_phi"] ** 2
                warning_count = int(score["max_abs_phi"] > 1.0)
                warning_count += int(score["max_grad_phi_proxy"] > 1.0)
                warning_count += int(effective_coupling_margin <= 0.10)
                rows.append({
                    "label": ledger.label,
                    "case": ledger.manifest.get("case", ledger.label),
                    "profile": profile,
                    "phi0": float(phi0),
                    "xi": float(xi),
                    "effective_coupling_margin_proxy": float(effective_coupling_margin),
                    "planck_warning_count": warning_count,
                    **score,
                })
    out = pd.DataFrame(rows)
    out["compatibility_score"] = (
        out["mean_relative_l1_residual"].astype(float)
        + 0.50 * out["scalar_live_stress_fraction"].astype(float).fillna(0.0)
        + 0.25 * out["planck_warning_count"].astype(float)
        + 0.25 * np.maximum(0.0, -out["effective_coupling_margin_proxy"].astype(float))
    )
    return out.sort_values(["compatibility_score", "mean_relative_l1_residual", "scalar_live_stress_fraction"])


def screen_ledgers(
    ledgers: Iterable[LedgerInput],
    *,
    phi0_values: Iterable[float] = DEFAULT_PHI0_VALUES,
    xi_values: Iterable[float] = DEFAULT_XI_VALUES,
    profiles: Iterable[str] = DEFAULT_PROFILES,
) -> pd.DataFrame:
    frames = [
        screen_ledger(ledger, phi0_values=phi0_values, xi_values=xi_values, profiles=profiles)
        for ledger in ledgers
    ]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def summarize_screen(candidates: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    if candidates.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for label, group in candidates.groupby("label", sort=False):
        ranked = group.sort_values("compatibility_score").head(int(top_n))
        best = ranked.iloc[0]
        rows.append({
            "label": label,
            "case": best["case"],
            "best_profile": best["profile"],
            "best_phi0": float(best["phi0"]),
            "best_xi": float(best["xi"]),
            "best_score": float(best["compatibility_score"]),
            "best_mean_residual": float(best["mean_relative_l1_residual"]),
            "best_mean_coverage": float(best["mean_coverage"]),
            "best_live_stress_fraction": float(best["scalar_live_stress_fraction"]),
            "best_max_abs_phi": float(best["max_abs_phi"]),
            "best_max_grad_phi_proxy": float(best["max_grad_phi_proxy"]),
            "best_effective_coupling_margin_proxy": float(best["effective_coupling_margin_proxy"]),
            "best_planck_warning_count": int(best["planck_warning_count"]),
            "top_candidates": int(len(ranked)),
        })
    return pd.DataFrame(rows)


def write_screen_outputs(
    outdir: Path,
    ledgers: list[LedgerInput],
    candidates: pd.DataFrame,
    *,
    top_n: int = 10,
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    summary = summarize_screen(candidates, top_n=top_n)
    candidate_path = outdir / "scalar_source_screen_candidates.csv"
    summary_path = outdir / "scalar_source_screen_summary.csv"
    top_path = outdir / "scalar_source_screen_top_candidates.csv"
    candidates.to_csv(candidate_path, index=False)
    summary.to_csv(summary_path, index=False)
    if candidates.empty:
        top = pd.DataFrame()
    else:
        top_frames = [
            group.sort_values("compatibility_score").head(int(top_n))
            for _label, group in candidates.groupby("label", sort=False)
        ]
        top = pd.concat(top_frames, ignore_index=True)
    top.to_csv(top_path, index=False)
    manifest_path = outdir / "scalar_source_screen_manifest.json"
    manifest = {
        "caveat": (
            "Reduced scalar-source compatibility proxy. This screens simple nonminimal "
            "scalar ansatz placement against demanded-source ledgers; it is not a full "
            "scalar-tensor solve or a proof of physical viability."
        ),
        "ledgers": [
            {
                "label": ledger.label,
                "ledger_dir": str(ledger.ledger_dir),
                "manifest": str(ledger.manifest_path),
                "point_ledger": str(ledger.point_ledger_path),
                "point_ledger_sha256": sha256_file(ledger.point_ledger_path),
                "case": ledger.manifest.get("case"),
            }
            for ledger in ledgers
        ],
        "files": {
            "candidates": str(candidate_path),
            "summary": str(summary_path),
            "top_candidates": str(top_path),
        },
        "candidate_rows": int(len(candidates)),
        "summary_rows": int(len(summary)),
    }
    write_manifest(manifest_path, manifest)
    return {
        "candidates": candidate_path,
        "summary": summary_path,
        "top_candidates": top_path,
        "manifest": manifest_path,
    }
