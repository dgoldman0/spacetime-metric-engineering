from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .field_names import FIELD_BLOCKS, internal_field_name, service_field_name, service_delta_name


@dataclass
class FieldDeltaResult:
    delta: dict[str, np.ndarray]
    metadata: dict[str, Any]
    summaries: list[dict[str, Any]]


def _array_from_ledger(ledger: pd.DataFrame, column: str, shape: tuple[int, int], default: float = 0.0) -> np.ndarray:
    if column not in ledger.columns:
        return np.full(shape, default, dtype=float)
    return ledger[column].to_numpy(dtype=float).reshape(shape)


def _bool_col(ledger: pd.DataFrame, name: str, default: bool = False) -> pd.Series:
    if name in ledger.columns:
        return ledger[name].astype(bool)
    return pd.Series(default, index=ledger.index)


def mask_from_ledger(ledger: pd.DataFrame, name: str | None, shape: tuple[int, int]) -> np.ndarray:
    scope = (name or "global").lower()
    true = np.ones(shape, dtype=bool)
    false = np.zeros(shape, dtype=bool)
    if scope == "global":
        return true

    stage = ledger.get("stage", pd.Series("", index=ledger.index)).astype(str)
    region = ledger.get("region", pd.Series("", index=ledger.index)).astype(str)
    packet_live = _bool_col(ledger, "packet_live") | _bool_col(ledger, "inside_packet_live")
    packet_edge = _bool_col(ledger, "packet_edge") | _bool_col(ledger, "packet_edge_strip")
    support_shell = _bool_col(ledger, "support_shell")

    stage_aliases = {
        "catch": "catch_rematch",
        "catch_rematch": "catch_rematch",
        "handoff": "catch_rematch",
        "release": "release_shift_fade",
        "fade": "release_shift_fade",
        "release_shift_fade": "release_shift_fade",
        "reset": "reset_decompression",
        "decompression": "reset_decompression",
        "reset_decompression": "reset_decompression",
        "post_release": "post_release_buffer",
        "post_release_buffer": "post_release_buffer",
    }

    if scope in {"packet", "packet_corridor", "live_packet", "packet_live"}:
        return packet_live.to_numpy().reshape(shape)
    if scope in {"packet_edge", "packet_edge_strip", "packet_boundary"}:
        return packet_edge.to_numpy().reshape(shape)
    if scope == "packet_core":
        return (packet_live & ~packet_edge).to_numpy().reshape(shape)
    if scope in {"support", "support_shell", "service_support_shell"}:
        return support_shell.to_numpy().reshape(shape)
    if scope in {"catch_edge", "catch_rematch_edge", "handoff_edge"}:
        return (stage.eq("catch_rematch") & packet_edge).to_numpy().reshape(shape)
    if scope in {"catch_support", "catch_rematch_support", "catch_rematch_support_shell", "handoff_support"}:
        return (stage.eq("catch_rematch") & support_shell).to_numpy().reshape(shape)
    if scope in {"catch_packet", "catch_rematch_packet", "handoff_packet"}:
        return (stage.eq("catch_rematch") & packet_live).to_numpy().reshape(shape)
    if scope in stage_aliases:
        return stage.eq(stage_aliases[scope]).to_numpy().reshape(shape)
    if scope.startswith("region:"):
        wanted = scope.split(":", 1)[1]
        return region.eq(wanted).to_numpy().reshape(shape)
    return false


def _smooth_window(window: np.ndarray, passes: int = 2) -> np.ndarray:
    w = np.asarray(window, dtype=float)
    for _ in range(max(0, int(passes))):
        padded = np.pad(w, 1, mode="edge")
        w = (
            4.0 * padded[1:-1, 1:-1]
            + padded[:-2, 1:-1]
            + padded[2:, 1:-1]
            + padded[1:-1, :-2]
            + padded[1:-1, 2:]
        ) / 8.0
    w = np.clip(w, 0.0, None)
    max_w = float(np.nanmax(w)) if w.size else 0.0
    if max_w > 0:
        w = w / max_w
    return np.clip(w * w * (3.0 - 2.0 * w), 0.0, 1.0)


def _gaussian_axis(values: np.ndarray, center: float | None, width: float | None) -> np.ndarray:
    if center is None or width is None:
        return np.ones_like(values, dtype=float)
    width = float(width)
    if width <= 0:
        raise ValueError("window widths must be positive when supplied")
    return np.exp(-0.5 * ((values - float(center)) / width) ** 2)


def build_service_window(fields: dict[str, np.ndarray], ledger: pd.DataFrame, spec: dict[str, Any], default_scope: str = "global") -> np.ndarray:
    shape = fields["rho"].shape
    scope = spec.get("scope", spec.get("support_scope", spec.get("support_mask", default_scope)))
    window = mask_from_ledger(ledger, scope, shape).astype(float)

    s = fields["s_grid"]
    l = fields["l_grid"]
    sw = _gaussian_axis(s, spec.get("schedule_center", spec.get("time_center")), spec.get("schedule_width", spec.get("temporal_width")))
    lw = _gaussian_axis(l, spec.get("radial_center"), spec.get("radial_width"))
    window *= sw[:, None] * lw[None, :]

    stage_weights = spec.get("stage_weights") or {}
    if stage_weights:
        stage = ledger.get("stage", pd.Series("", index=ledger.index)).astype(str).to_numpy().reshape(shape)
        stage_factor = np.zeros(shape, dtype=float)
        for stage_name, weight in stage_weights.items():
            stage_factor[stage == str(stage_name)] += float(weight)
        window *= stage_factor

    packet_exclusion = float(spec.get("packet_exclusion", 0.0) or 0.0)
    if packet_exclusion:
        packet_live = mask_from_ledger(ledger, "packet_live", shape).astype(float)
        window *= np.clip(1.0 - packet_exclusion * packet_live, 0.0, 1.0)

    support_shell_gain = float(spec.get("support_shell_gain", 0.0) or 0.0)
    if support_shell_gain:
        support_shell = mask_from_ledger(ledger, "support_shell", shape).astype(float)
        window *= 1.0 + support_shell_gain * support_shell

    edge_bias = float(spec.get("edge_bias", 0.0) or 0.0)
    if edge_bias:
        packet_edge = mask_from_ledger(ledger, "packet_edge", shape).astype(float)
        window *= 1.0 + edge_bias * packet_edge

    smoothness = int(spec.get("smoothness_order", spec.get("smoothing_passes", 2)) or 0)
    window = _smooth_window(window, smoothness)
    return window


def _normalized_signal(ledger: pd.DataFrame, signal_name: str, window: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    signal = _array_from_ledger(ledger, signal_name, shape, default=0.0)
    scale = np.nanmax(np.abs(signal * window))
    if not np.isfinite(scale) or scale == 0:
        return np.zeros(shape, dtype=float)
    return (signal / scale) * window


def _clip_delta(delta: np.ndarray, spec: dict[str, Any]) -> np.ndarray:
    limit = spec.get("max_abs_change", spec.get("max_abs_delta"))
    if limit is None:
        return delta
    limit = abs(float(limit))
    return np.clip(delta, -limit, limit)


def _delta_for_modifier(fields: dict[str, np.ndarray], ledger: pd.DataFrame, block_name: str, spec: dict[str, Any]) -> tuple[str, np.ndarray, dict[str, Any]]:
    shape = fields["rho"].shape
    service_name = spec.get("target_service_field", spec.get("target_field", block_name))
    internal = internal_field_name(service_name)
    canonical = service_field_name(internal)
    law = str(spec.get("law", spec.get("mode", "identity"))).lower()

    window = build_service_window(fields, ledger, spec, default_scope=spec.get("scope", "global"))
    amplitude = float(spec.get("amplitude", spec.get("strength", 0.0)) or 0.0)
    gain = float(spec.get("gain", 1.0) or 1.0)

    if law in {"none", "identity", "removed", "zero", "off"} or not spec.get("enabled", True):
        delta = np.zeros(shape, dtype=float)
    elif law in {"windowed_adjustment", "additive_window", "service_window"}:
        delta = amplitude * gain * window
    elif law in {"scale_existing", "fractional_window", "windowed_scale"}:
        delta = fields[internal] * amplitude * gain * window
    elif law in {"compact_momentum_localizer", "compact_carrying_flow_localizer", "counterflow_localizer", "compact_shift_localizer"}:
        if internal != "beta":
            raise ValueError(f"{law} only applies to carrying_flow")
        signal_name = spec.get("signal", "delta_j_l")
        normalized = _normalized_signal(ledger, signal_name, window, shape)
        delta = -amplitude * gain * normalized
    else:
        raise ValueError(f"Unknown service modifier law: {law}")

    delta = _clip_delta(delta, spec)
    meta = {
        "block": block_name,
        "service_field": canonical,
        "delta_name": service_delta_name(internal),
        "law": law,
        "scope": spec.get("scope", spec.get("support_scope", spec.get("support_mask", "global"))),
        "amplitude": amplitude,
        "gain": gain,
        "max_abs_change": spec.get("max_abs_change", spec.get("max_abs_delta")),
        "window_abs_sum": float(np.abs(window).sum()),
        "window_max": float(np.nanmax(window)) if window.size else 0.0,
        "min": float(delta.min()),
        "max": float(delta.max()),
        "linf": float(np.abs(delta).max()),
        "l1": float(np.abs(delta).sum()),
        "nonzero_points": int((np.abs(delta) > 0).sum()),
    }
    return internal, delta, meta


def _service_modifier_specs(cfg: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    specs: list[tuple[str, dict[str, Any]]] = []
    service_cfg = cfg.get("service", {}) or {}
    for block_name in FIELD_BLOCKS:
        spec = service_cfg.get(block_name)
        if isinstance(spec, dict) and spec.get("enabled", True):
            spec = dict(spec)
            spec.setdefault("target_service_field", block_name)
            specs.append((block_name, spec))

    # Treat absorber/control law as a modifier inside the carrying-flow service.
    absorber = cfg.get("absorber", {}) or {}
    if absorber and absorber.get("mode", absorber.get("law", "none")) not in {"none", None}:
        spec = dict(absorber)
        spec.setdefault("target_service_field", "carrying_flow")
        spec.setdefault("scope", spec.get("support_mask", "catch_rematch_edge"))
        if "coefficients" in spec and isinstance(spec["coefficients"], dict):
            merged = dict(spec["coefficients"])
            merged.update({k: v for k, v in spec.items() if k != "coefficients"})
            spec = merged
        specs.append(("absorber_control", spec))
    return specs


def compute_service_field_delta(
    fields: dict[str, np.ndarray],
    preliminary_ledger: pd.DataFrame,
    cfg: dict[str, Any],
) -> FieldDeltaResult:
    shape = fields["rho"].shape
    deltas: dict[str, np.ndarray] = {}
    summaries: list[dict[str, Any]] = []

    for block_name, spec in _service_modifier_specs(cfg):
        internal, delta, meta = _delta_for_modifier(fields, preliminary_ledger, block_name, spec)
        if internal not in deltas:
            deltas[internal] = np.zeros(shape, dtype=float)
        deltas[internal] = deltas[internal] + delta
        summaries.append(meta)

    if not summaries:
        return FieldDeltaResult(delta={}, metadata={"enabled_modifiers": 0}, summaries=[])

    aggregate = {
        "enabled_modifiers": len(summaries),
        "modified_service_fields": sorted({row["service_field"] for row in summaries}),
        "modifiers": summaries,
    }
    return FieldDeltaResult(delta=deltas, metadata=aggregate, summaries=summaries)
