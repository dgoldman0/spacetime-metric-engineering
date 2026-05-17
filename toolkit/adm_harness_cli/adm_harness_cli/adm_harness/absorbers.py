from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class FieldDeltaResult:
    delta: dict[str, np.ndarray]
    metadata: dict[str, Any]


def _array_from_ledger(ledger: pd.DataFrame, column: str, shape: tuple[int, int], default: float = 0.0) -> np.ndarray:
    if column not in ledger.columns:
        return np.full(shape, default, dtype=float)
    return ledger[column].to_numpy(dtype=float).reshape(shape)


def _mask_from_ledger(ledger: pd.DataFrame, name: str, shape: tuple[int, int]) -> np.ndarray:
    name = (name or "global").lower()
    true = np.ones(shape, dtype=bool)
    false = np.zeros(shape, dtype=bool)
    if name == "global":
        return true
    stage = ledger.get("stage", pd.Series("", index=ledger.index)).astype(str)
    packet_live = ledger.get("packet_live", ledger.get("inside_packet_live", pd.Series(False, index=ledger.index))).astype(bool)
    packet_edge = ledger.get("packet_edge", ledger.get("packet_edge_strip", pd.Series(False, index=ledger.index))).astype(bool)
    support_shell = ledger.get("support_shell", pd.Series(False, index=ledger.index)).astype(bool)
    if name in {"packet_live", "packet"}:
        return packet_live.to_numpy().reshape(shape)
    if name in {"packet_edge", "packet_edge_strip"}:
        return packet_edge.to_numpy().reshape(shape)
    if name == "packet_core":
        return (packet_live & ~packet_edge).to_numpy().reshape(shape)
    if name == "support_shell":
        return support_shell.to_numpy().reshape(shape)
    if name in {"catch", "catch_rematch"}:
        return stage.eq("catch_rematch").to_numpy().reshape(shape)
    if name in {"catch_rematch_edge", "catch_edge"}:
        return (stage.eq("catch_rematch") & packet_edge).to_numpy().reshape(shape)
    if name in {"catch_rematch_support", "catch_support"}:
        return (stage.eq("catch_rematch") & support_shell).to_numpy().reshape(shape)
    return false


def _c2_window_from_mask(mask: np.ndarray, passes: int = 2) -> np.ndarray:
    """Cheap smoothing for compact masks without introducing scipy dependency."""
    w = mask.astype(float)
    for _ in range(max(0, int(passes))):
        padded = np.pad(w, 1, mode="edge")
        w = (
            4.0 * padded[1:-1, 1:-1]
            + padded[:-2, 1:-1]
            + padded[2:, 1:-1]
            + padded[1:-1, :-2]
            + padded[1:-1, 2:]
        ) / 8.0
    w = np.clip(w, 0.0, 1.0)
    return w * w * (3.0 - 2.0 * w)


def compute_field_delta(
    fields: dict[str, np.ndarray],
    preliminary_ledger: pd.DataFrame,
    substrate_fields: dict[str, np.ndarray] | None,
    absorber_cfg: dict[str, Any],
    synthesis_cfg: dict[str, Any] | None = None,
) -> FieldDeltaResult:
    synthesis_cfg = synthesis_cfg or {}
    shape = fields["rho"].shape
    mode = (absorber_cfg.get("law") or absorber_cfg.get("mode") or "none").lower()
    target = absorber_cfg.get("target_field", "beta")
    coefficients = absorber_cfg.get("coefficients", {}) or {}
    support_mask_name = absorber_cfg.get("support_mask", "catch_rematch_edge")
    smoothing_passes = int(absorber_cfg.get("smoothing_passes", synthesis_cfg.get("smoothing_passes", 2)))

    zeros = {target: np.zeros(shape, dtype=float)} if target != "none" else {}
    if mode in {"none", "identity", "removed", "zero"}:
        return FieldDeltaResult(delta=zeros, metadata={"law": mode, "target_field": target, "identity": True})

    if target != "beta":
        raise ValueError("This first synthesis implementation only supports target_field: beta")

    mask = _mask_from_ledger(preliminary_ledger, support_mask_name, shape)
    window = _c2_window_from_mask(mask, smoothing_passes)
    amplitude = float(coefficients.get("amplitude", absorber_cfg.get("amplitude", 0.0)))
    gain = float(coefficients.get("gain", absorber_cfg.get("gain", 1.0)))
    max_abs_delta = coefficients.get("max_abs_delta", absorber_cfg.get("max_abs_delta"))
    signal_name = absorber_cfg.get("signal", "delta_j_l")
    signal = _array_from_ledger(preliminary_ledger, signal_name, shape, default=0.0)

    if mode in {"compact_beta_localizer", "compact", "beta_residual_localizer"}:
        scale = np.nanmax(np.abs(signal * window))
        if not np.isfinite(scale) or scale == 0:
            normalized = np.zeros(shape, dtype=float)
        else:
            normalized = (signal / scale) * window
        delta_beta = -gain * amplitude * normalized
    elif mode in {"constant_beta_window", "windowed_beta"}:
        delta_beta = amplitude * window
    else:
        raise ValueError(f"Unknown absorber synthesis law: {mode}")

    if max_abs_delta is not None:
        max_abs_delta = abs(float(max_abs_delta))
        delta_beta = np.clip(delta_beta, -max_abs_delta, max_abs_delta)

    metadata = {
        "law": mode,
        "target_field": target,
        "support_mask": support_mask_name,
        "smoothing_passes": smoothing_passes,
        "signal": signal_name,
        "amplitude": amplitude,
        "gain": gain,
        "max_abs_delta": max_abs_delta,
        "mask_points": int(mask.sum()),
        "window_abs_sum": float(np.abs(window).sum()),
        "delta_beta_min": float(delta_beta.min()),
        "delta_beta_max": float(delta_beta.max()),
        "delta_beta_linf": float(np.abs(delta_beta).max()),
        "delta_beta_l1": float(np.abs(delta_beta).sum()),
    }
    return FieldDeltaResult(delta={"beta": delta_beta}, metadata=metadata)
