"""Finite-difference stress-channel proxies for the White Casimir audit."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd


ROLE_NAMES = (
    "source_shell_candidate",
    "boundary_infrastructure",
    "stress_shaping_body",
    "transit_readout_channel",
    "ordinary_em_competitor_region",
    "far_field_control",
)


def _fraction(part: float, whole: float) -> float:
    return float(part / whole) if abs(whole) > 0.0 else 0.0


def field_channel_metrics(
    grid: Mapping[str, np.ndarray],
    geometry: Any,
    field: np.ndarray,
) -> dict[str, float]:
    """Return signed and magnitude integrals by role for one proxy field."""

    arr = np.asarray(field, dtype=float)
    negative = np.maximum(-arr, 0.0)
    total_signed = float(np.sum(arr))
    total_negative = float(np.sum(negative))
    total_abs = float(np.sum(np.abs(arr)))
    metrics: dict[str, float] = {
        "signed_integral": total_signed,
        "negative_magnitude_integral": total_negative,
        "abs_integral": total_abs,
        "mean_proxy": float(np.mean(arr)),
        "min_proxy": float(np.min(arr)),
        "negative_fraction": float(np.count_nonzero(arr < 0.0) / arr.size),
    }
    roles = geometry.role_regions(grid)
    for role in ROLE_NAMES:
        mask = np.asarray(roles[role], dtype=bool)
        count = int(np.count_nonzero(mask))
        signed = float(np.sum(arr[mask]))
        mag = float(np.sum(negative[mask]))
        metrics[f"{role}_area_count"] = float(count)
        metrics[f"{role}_signed_integral"] = signed
        metrics[f"{role}_negative_magnitude_integral"] = mag
        metrics[f"{role}_signed_mean"] = signed / max(count, 1)
        metrics[f"{role}_negative_magnitude_mean"] = mag / max(count, 1)
        metrics[f"{role}_signed_fraction"] = _fraction(signed, total_signed)
        metrics[f"{role}_negative_magnitude_fraction"] = _fraction(mag, total_negative)
    shell = metrics["source_shell_candidate_negative_magnitude_integral"]
    readout = metrics["transit_readout_channel_negative_magnitude_integral"]
    if readout > 0.0:
        metrics["shell_to_readout_channel_ratio"] = shell / readout
    elif shell > 0.0:
        metrics["shell_to_readout_channel_ratio"] = float("inf")
    else:
        metrics["shell_to_readout_channel_ratio"] = 0.0
    metrics["far_field_leakage_fraction"] = metrics["far_field_control_negative_magnitude_fraction"]
    return metrics


def finite_difference_rows(
    baseline: dict[str, float],
    plus: dict[str, float],
    minus: dict[str, float],
    parameter: str,
    delta_um: float,
    block_id: int,
    wall_thickness_um: float,
    scale_window: str,
) -> list[dict[str, float | int | str]]:
    """Return finite-difference derivative rows for global and role channels."""

    rows: list[dict[str, float | int | str]] = []
    channel_keys = ["signed_integral", "negative_magnitude_integral"]
    for role in ROLE_NAMES:
        channel_keys.append(f"{role}_signed_integral")
        channel_keys.append(f"{role}_negative_magnitude_integral")

    for key in channel_keys:
        p = float(plus[key])
        m = float(minus[key])
        derivative = (p - m) / (2.0 * float(delta_um))
        rows.append(
            {
                "block_id": int(block_id),
                "wall_thickness_um": float(wall_thickness_um),
                "scale_window": scale_window,
                "parameter": parameter,
                "channel": key,
                "delta_um": float(delta_um),
                "baseline_value": float(baseline.get(key, np.nan)),
                "minus_value": m,
                "plus_value": p,
                "finite_difference_per_um": derivative,
                "proxy_status": "finite_difference_stress_channel_proxy_not_tensor_reconstruction",
            }
        )
    return rows


def summarize_bootstrap(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Summarize block derivatives with sign-stability diagnostics."""

    frame = pd.DataFrame(rows)
    if frame.empty:
        return pd.DataFrame()
    grouped = frame.groupby(["wall_thickness_um", "scale_window", "parameter", "channel"], dropna=False)
    summary_rows: list[dict[str, Any]] = []
    for keys, group in grouped:
        values = group["finite_difference_per_um"].astype(float).to_numpy()
        positive = float(np.count_nonzero(values > 0.0) / len(values))
        negative = float(np.count_nonzero(values < 0.0) / len(values))
        zero = float(np.count_nonzero(values == 0.0) / len(values))
        summary_rows.append(
            {
                "wall_thickness_um": keys[0],
                "scale_window": keys[1],
                "parameter": keys[2],
                "channel": keys[3],
                "n_blocks": int(len(values)),
                "median_per_um": float(np.median(values)),
                "q16_per_um": float(np.quantile(values, 0.16)),
                "q84_per_um": float(np.quantile(values, 0.84)),
                "mean_per_um": float(np.mean(values)),
                "std_per_um": float(np.std(values)),
                "positive_fraction": positive,
                "negative_fraction": negative,
                "zero_fraction": zero,
                "sign_stability": max(positive, negative, zero),
                "stable_sign_or_clear_null": bool(max(positive, negative, zero) >= 0.75),
            }
        )
    return pd.DataFrame(summary_rows)


def estimate_stress_proxy(*args: Any, **kwargs: Any) -> dict[str, str]:
    """Compatibility marker for Stage 3 callers."""

    return {"proxy_status": "finite_difference_stress_channel_proxy_not_tensor_reconstruction"}
