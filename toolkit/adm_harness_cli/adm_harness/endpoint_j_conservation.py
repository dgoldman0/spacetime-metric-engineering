from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .source_ledger import sha256_file, write_manifest
from .source_screening import resolve_manifest_path


J_SECTOR = "J_endpoint_junction_layer"
SUPPORT_ASSIGNMENT = "support_edge_endpoint_junction"
RESET_ASSIGNMENT = "reset_decompression_endpoint_junction"
ASSIGNMENT_SCOPES = {
    SUPPORT_ASSIGNMENT: "support_edge",
    RESET_ASSIGNMENT: "reset_cap",
}
SUMMARY_SCOPES = {
    "J_total": None,
    "support_edge": SUPPORT_ASSIGNMENT,
    "reset_cap": RESET_ASSIGNMENT,
}
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


def _rows_for_fraction(weights: np.ndarray, fraction: float) -> float:
    total = float(np.sum(weights))
    if len(weights) == 0 or total <= 0.0:
        return float("nan")
    ordered = np.sort(weights)[::-1]
    return float((np.searchsorted(np.cumsum(ordered), fraction * total) + 1) / len(weights))


def _top_share(weights: np.ndarray, row_fraction: float) -> float:
    total = float(np.sum(weights))
    if len(weights) == 0 or total <= 0.0:
        return float("nan")
    count = max(1, int(math.ceil(row_fraction * len(weights))))
    return float(np.sort(weights)[::-1][:count].sum() / total)


def _weighted_quantile(values: np.ndarray, weights: np.ndarray, quantile: float) -> float:
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0.0)
    if not np.any(mask):
        return float("nan")
    ordered = np.argsort(values[mask])
    ordered_values = values[mask][ordered]
    ordered_weights = weights[mask][ordered]
    cumulative = np.cumsum(ordered_weights)
    target = float(quantile) * float(cumulative[-1])
    index = int(np.searchsorted(cumulative, target, side="left"))
    index = min(index, len(ordered_values) - 1)
    return float(ordered_values[index])


def _weighted_width(values: np.ndarray, weights: np.ndarray, lower: float, upper: float) -> float:
    lo = _weighted_quantile(values, weights, lower)
    hi = _weighted_quantile(values, weights, upper)
    return float(hi - lo) if math.isfinite(lo) and math.isfinite(hi) else float("nan")


def _weighted_std(values: np.ndarray, weights: np.ndarray) -> float:
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0.0)
    if not np.any(mask):
        return float("nan")
    selected_values = values[mask]
    selected_weights = weights[mask]
    total = float(selected_weights.sum())
    mean = float(np.sum(selected_values * selected_weights) / total)
    var = float(np.sum(np.square(selected_values - mean) * selected_weights) / total)
    return float(math.sqrt(max(var, 0.0)))


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


def _enrich_assignment_frame(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["assignment_scope"] = out["assignment"].astype(str).map(ASSIGNMENT_SCOPES).fillna("other_endpoint")
    h_s = _median_spacing(out["s"])
    h_l = _median_spacing(out["l"])
    finite_spacings = [value for value in (h_s, h_l) if math.isfinite(value) and value > 0.0]
    h_ref = min(finite_spacings) if finite_spacings else 1.0

    out["d_s_rho"] = _axis_derivative(out, "sector_rho", "s", "l")
    out["d_l_j_l"] = _axis_derivative(out, "sector_j_l", "l", "s")
    out["d_s_j_l"] = _axis_derivative(out, "sector_j_l", "s", "l")
    out["d_l_p_l"] = _axis_derivative(out, "sector_p_l", "l", "s")
    out["d_l_p_omega"] = _axis_derivative(out, "sector_p_omega", "l", "s")
    out["continuity_residual_density"] = out["d_s_rho"] + out["d_l_j_l"]
    out["radial_momentum_residual_density"] = out["d_s_j_l"] + out["d_l_p_l"]
    out["angular_capacity_gradient_density"] = out["d_l_p_omega"]
    out["conservation_residual_l2_density"] = np.sqrt(
        np.square(out["continuity_residual_density"])
        + np.square(out["radial_momentum_residual_density"])
    )
    local_scale = (
        out["sector_rho"].abs()
        + out["sector_p_l"].abs()
        + 2.0 * out["sector_j_l"].abs()
        + out["sector_p_omega"].abs()
    )
    out["local_field_scale_density"] = local_scale
    out["conservation_residual_norm"] = out["conservation_residual_l2_density"] / (local_scale / h_ref + EPS)
    out["angular_gradient_norm"] = out["angular_capacity_gradient_density"].abs() / (
        out["sector_p_omega"].abs() / (h_l if math.isfinite(h_l) and h_l > 0.0 else h_ref) + EPS
    )
    volume = out["volume_weight"].astype(float)
    out["conservation_residual_l2_density_volume"] = out["conservation_residual_l2_density"] * volume
    out["h_s_median"] = h_s
    out["h_l_median"] = h_l
    out["h_ref"] = h_ref
    return out


def _interpret_summary(row: dict[str, Any]) -> str:
    if int(row.get("live_rows", 0)) > 0 or _finite(row.get("live_selected_null_deficit"), 0.0) > 0.0:
        return "fails_non_live_endpoint_gate"
    if int(row.get("scoreable_derivative_rows", 0)) == 0:
        return "insufficient_derivative_stencil"
    if (
        _finite(row.get("weighted_mean_conservation_residual_norm"), 0.0) > 1.0
        or _finite(row.get("burden_weighted_mean_conservation_residual_norm"), 0.0) > 1.0
        or (
            _finite(row.get("peak_conservation_residual_norm"), 0.0) > 5.0
            and _finite(row.get("peak_conservation_residual_burden_share"), 0.0) > 0.01
        )
    ):
        return "large_conservation_residual_watch"
    if _finite(row.get("peak_conservation_residual_norm"), 0.0) > 5.0:
        return "edge_tail_conservation_residual_watch"
    if (
        _finite(row.get("effective_volume_fraction"), 1.0) < 0.02
        or _finite(row.get("top_1pct_burden_share"), 0.0) > 0.50
    ):
        return "localized_coupling_watch"
    return "finite_spread_proxy_not_conservation_proof"


def _summarize_scope(frame: pd.DataFrame, label: str, source_name: str, scope: str) -> dict[str, Any]:
    volume = frame["volume_weight"].astype(float).to_numpy()
    selected_density = frame["sector_selected_null_deficit_density"].astype(float).to_numpy()
    selected_volume = frame["sector_selected_null_deficit_density_volume"].astype(float).to_numpy()
    current_volume = frame["sector_abs_current_density_volume"].astype(float).to_numpy()
    pomega_volume = frame["sector_abs_pomega_density_volume"].astype(float).to_numpy()
    pair_volume = frame["sector_pair_l1_density_volume"].astype(float).to_numpy()
    live = _bool_series(frame["inside_packet_live"])
    active_volume = float(np.sum(volume))
    selected = float(np.sum(selected_volume))
    density_l2_volume = float(np.sum(np.square(selected_density) * volume))
    effective_volume = selected * selected / density_l2_volume if density_l2_volume > 0.0 else float("nan")
    mean_density = selected / active_volume if active_volume > 0.0 else float("nan")
    scoreable = np.isfinite(frame["conservation_residual_l2_density"].astype(float).to_numpy())
    scoreable_volume = volume[scoreable]
    residual_density = frame["conservation_residual_l2_density"].astype(float).to_numpy()
    residual_norm = frame["conservation_residual_norm"].astype(float).to_numpy()
    continuity_abs = frame["continuity_residual_density"].abs().astype(float).to_numpy()
    radial_abs = frame["radial_momentum_residual_density"].abs().astype(float).to_numpy()
    angular_norm = frame["angular_gradient_norm"].abs().astype(float).to_numpy()
    weights = selected_volume
    scoreable_burden = selected_volume[scoreable]
    s_values = frame["s"].astype(float).to_numpy()
    l_values = frame["l"].astype(float).to_numpy()
    finite_peak = np.isfinite(residual_norm)
    peak_index = int(np.nanargmax(residual_norm)) if np.any(finite_peak) else -1
    peak_selected_volume = float(selected_volume[peak_index]) if peak_index >= 0 else float("nan")

    row: dict[str, Any] = {
        "label": label,
        "source_name": source_name,
        "scope": scope,
        "assignment": "" if scope == "J_total" else str(frame["assignment"].iloc[0]) if len(frame) else "",
        "rows": int(len(frame)),
        "scoreable_derivative_rows": int(np.count_nonzero(scoreable)),
        "scoreable_derivative_fraction": _safe_ratio(float(np.count_nonzero(scoreable)), float(len(frame))),
        "active_volume": active_volume,
        "selected_null_deficit": selected,
        "pair_l1": float(np.sum(pair_volume)),
        "abs_current": float(np.sum(current_volume)),
        "abs_pomega": float(np.sum(pomega_volume)),
        "live_rows": int(live.sum()),
        "live_selected_null_deficit": float(frame.loc[live, "sector_selected_null_deficit_density_volume"].sum()),
        "live_pair_l1": float(frame.loc[live, "sector_pair_l1_density_volume"].sum()),
        "mean_selected_density": mean_density,
        "peak_selected_density": float(np.max(selected_density)) if len(selected_density) else float("nan"),
        "peak_to_mean_density": (
            float(np.max(selected_density) / mean_density) if len(selected_density) and mean_density > 0.0 else float("nan")
        ),
        "effective_burden_volume": effective_volume,
        "effective_volume_fraction": _safe_ratio(effective_volume, active_volume),
        "rows_for_50pct_burden": _rows_for_fraction(selected_volume, 0.50),
        "rows_for_80pct_burden": _rows_for_fraction(selected_volume, 0.80),
        "top_1pct_burden_share": _top_share(selected_volume, 0.01),
        "top_5pct_burden_share": _top_share(selected_volume, 0.05),
        "top_10pct_burden_share": _top_share(selected_volume, 0.10),
        "current_to_selected_ratio": _safe_ratio(float(np.sum(current_volume)), selected),
        "pomega_to_selected_ratio": _safe_ratio(float(np.sum(pomega_volume)), selected),
        "weighted_s_std": _weighted_std(s_values, weights),
        "weighted_l_std": _weighted_std(l_values, weights),
        "weighted_s_width_50pct": _weighted_width(s_values, weights, 0.25, 0.75),
        "weighted_l_width_50pct": _weighted_width(l_values, weights, 0.25, 0.75),
        "weighted_s_width_80pct": _weighted_width(s_values, weights, 0.10, 0.90),
        "weighted_l_width_80pct": _weighted_width(l_values, weights, 0.10, 0.90),
        "h_s_median": float(frame["h_s_median"].dropna().iloc[0]) if frame["h_s_median"].notna().any() else float("nan"),
        "h_l_median": float(frame["h_l_median"].dropna().iloc[0]) if frame["h_l_median"].notna().any() else float("nan"),
        "weighted_mean_continuity_abs_density": (
            float(np.sum(continuity_abs[scoreable] * scoreable_volume) / np.sum(scoreable_volume))
            if len(scoreable_volume) and np.sum(scoreable_volume) > 0.0
            else float("nan")
        ),
        "weighted_mean_radial_momentum_abs_density": (
            float(np.sum(radial_abs[scoreable] * scoreable_volume) / np.sum(scoreable_volume))
            if len(scoreable_volume) and np.sum(scoreable_volume) > 0.0
            else float("nan")
        ),
        "weighted_mean_conservation_residual_density": (
            float(np.sum(residual_density[scoreable] * scoreable_volume) / np.sum(scoreable_volume))
            if len(scoreable_volume) and np.sum(scoreable_volume) > 0.0
            else float("nan")
        ),
        "peak_conservation_residual_density": (
            float(np.nanmax(residual_density)) if len(residual_density) else float("nan")
        ),
        "weighted_mean_conservation_residual_norm": (
            float(np.sum(residual_norm[scoreable] * scoreable_volume) / np.sum(scoreable_volume))
            if len(scoreable_volume) and np.sum(scoreable_volume) > 0.0
            else float("nan")
        ),
        "burden_weighted_mean_conservation_residual_norm": (
            float(np.sum(residual_norm[scoreable] * scoreable_burden) / np.sum(scoreable_burden))
            if len(scoreable_burden) and np.sum(scoreable_burden) > 0.0
            else float("nan")
        ),
        "peak_conservation_residual_norm": float(np.nanmax(residual_norm)) if len(residual_norm) else float("nan"),
        "peak_conservation_residual_selected_volume": peak_selected_volume,
        "peak_conservation_residual_burden_share": _safe_ratio(peak_selected_volume, selected),
        "weighted_mean_angular_gradient_norm": (
            float(np.nansum(angular_norm * volume) / np.sum(volume)) if len(volume) and np.sum(volume) > 0.0 else float("nan")
        ),
        "peak_angular_gradient_norm": float(np.nanmax(angular_norm)) if len(angular_norm) else float("nan"),
    }
    row["diagnostic_read"] = _interpret_summary(row)
    return row


def _top_residuals(enriched: pd.DataFrame, top_limit: int) -> pd.DataFrame:
    if enriched.empty:
        return pd.DataFrame()
    cols = [
        "label",
        "source_name",
        "assignment_scope",
        "assignment",
        "point_index",
        "s",
        "l",
        "stage",
        "region",
        "inside_packet_live",
        "sector_rho",
        "sector_p_l",
        "sector_j_l",
        "sector_p_omega",
        "sector_selected_null_deficit_density",
        "sector_selected_null_deficit_density_volume",
        "continuity_residual_density",
        "radial_momentum_residual_density",
        "conservation_residual_l2_density",
        "conservation_residual_norm",
        "angular_capacity_gradient_density",
        "angular_gradient_norm",
    ]
    available = [col for col in cols if col in enriched.columns]
    return (
        enriched.sort_values(
            ["conservation_residual_norm", "sector_selected_null_deficit_density_volume"],
            ascending=[False, False],
            na_position="last",
        )
        .head(int(top_limit))
        .loc[:, available]
        .reset_index(drop=True)
    )


def build_endpoint_j_conservation_tables(
    sectors: pd.DataFrame,
    *,
    source_name: str = "",
    labels: list[str] | None = None,
    top_limit: int = 80,
) -> dict[str, pd.DataFrame]:
    if sectors.empty:
        empty = pd.DataFrame()
        return {
            "summary": empty,
            "by_assignment": empty,
            "point_residuals": empty,
            "top_residuals": empty,
        }
    selected = sectors.loc[sectors["sector"].astype(str) == J_SECTOR].copy()
    if labels:
        label_set = {str(label) for label in labels}
        selected = selected.loc[selected["label"].astype(str).isin(label_set)].copy()
    enriched_frames: list[pd.DataFrame] = []
    for (_label, _assignment), group in selected.groupby(["label", "assignment"], sort=False, dropna=False):
        enriched_frames.append(_enrich_assignment_frame(group))
    enriched = pd.concat(enriched_frames, ignore_index=True) if enriched_frames else pd.DataFrame()
    if enriched.empty:
        empty = pd.DataFrame()
        return {
            "summary": empty,
            "by_assignment": empty,
            "point_residuals": empty,
            "top_residuals": empty,
        }

    summaries: list[dict[str, Any]] = []
    for label, group in enriched.groupby("label", sort=False):
        for scope, assignment in SUMMARY_SCOPES.items():
            frame = group if assignment is None else group.loc[group["assignment"].astype(str) == assignment]
            if frame.empty:
                continue
            summaries.append(_summarize_scope(frame, str(label), source_name, scope))
    summary = pd.DataFrame(summaries)
    by_assignment = summary.loc[summary["scope"].ne("J_total")].reset_index(drop=True)
    top = _top_residuals(enriched, top_limit)
    return {
        "summary": summary,
        "by_assignment": by_assignment,
        "point_residuals": enriched.reset_index(drop=True),
        "top_residuals": top,
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


def build_endpoint_j_conservation_diagnostic(
    intermediate_dir: Path,
    *,
    labels: list[str] | None = None,
    top_limit: int = 80,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    sectors, manifest, stress_path = _load_intermediate_sectors(intermediate_dir)
    outputs = build_endpoint_j_conservation_tables(
        sectors,
        source_name=intermediate_dir.name,
        labels=labels,
        top_limit=top_limit,
    )
    metadata = {
        "intermediate_dir": str(intermediate_dir),
        "intermediate_manifest_model": manifest.get("model", ""),
        "point_sector_stress": str(stress_path),
        "point_sector_stress_sha256": sha256_file(stress_path),
        "labels": labels or sorted(sectors["label"].astype(str).unique().tolist()),
        "j_sector": J_SECTOR,
        "assignment_scopes": ASSIGNMENT_SCOPES,
        "thresholds": {
            "large_weighted_mean_conservation_residual_norm": 1.0,
            "large_burden_weighted_mean_conservation_residual_norm": 1.0,
            "large_peak_conservation_residual_norm": 5.0,
            "large_peak_conservation_residual_burden_share": 0.01,
            "localized_effective_volume_fraction": 0.02,
            "localized_top_1pct_burden_share": 0.50,
        },
        "caveat": (
            "Finite-difference endpoint-J conservation proxy. The continuity-like residual "
            "d_s rho + d_l j_l and radial-momentum-like residual d_s j_l + d_l p_l are "
            "assignment-local diagnostics on the demanded intermediate source ledger. They "
            "screen whether the endpoint burden looks finite, distributed, and approximately "
            "self-closed; they are not a full covariant conservation solve or a physical "
            "matter Lagrangian construction."
        ),
    }
    return outputs, metadata


def write_endpoint_j_conservation_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary": outdir / "endpoint_j_conservation_summary.csv",
        "by_assignment": outdir / "endpoint_j_conservation_by_assignment.csv",
        "point_residuals": outdir / "endpoint_j_conservation_point_residuals.csv",
        "top_residuals": outdir / "endpoint_j_conservation_top_residuals.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "endpoint_j_conservation_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
