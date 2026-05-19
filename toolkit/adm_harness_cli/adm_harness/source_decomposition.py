from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .source_ledger import CHANNELS, sha256_file, write_manifest
from .source_screening import resolve_manifest_path


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if not math.isfinite(number):
        return default
    return number


def _load_points(ledger_dir: Path) -> tuple[pd.DataFrame, dict[str, Any], Path]:
    manifest_path = ledger_dir / "source_ledger_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    files = manifest.get("files", {})
    point_value = files.get("point_ledger", "source_ledger_point_ledger.csv")
    point_path = resolve_manifest_path(ledger_dir, point_value)
    return pd.read_csv(point_path), manifest, point_path


def _badness(row: pd.Series, channel: str) -> float:
    if channel == "neg_Tkk_radial":
        return max(-_finite(row.get("Tkk_min_radial")), 0.0)
    if channel == "abs_p_l":
        return abs(_finite(row.get("p_l_unit")))
    if channel == "abs_j_l":
        return abs(_finite(row.get("j_l_unit")))
    if channel == "abs_pOmega":
        return abs(_finite(row.get("p_omega_unit")))
    return _finite(row.get(f"bad_{channel}"))


def _channel_role(channel: str) -> str:
    return {
        "neg_Tkk_radial": "radial_null_exotic_support",
        "abs_p_l": "radial_pressure_balance",
        "abs_j_l": "radial_current_shift_momentum",
        "abs_pOmega": "angular_pressure_capacity",
        "neg_rho_euler": "negative_eulerian_density",
        "neg_rho_packet": "packet_frame_negative_density",
    }.get(channel, "unclassified")


def _source_assignment(row: pd.Series, channel: str) -> str:
    live = bool(row.get("inside_packet_live", False))
    stage = str(row.get("stage", ""))
    region = str(row.get("region", ""))
    if channel == "neg_Tkk_radial":
        if not live and region in {"core_throat", "support_edge"}:
            return "infrastructure_radial_null_support"
        if live:
            return "packet_contaminating_radial_null_support"
        return "background_or_reset_radial_null_support"
    if channel == "abs_p_l":
        if region == "core_throat":
            return "core_radial_pressure_balance"
        if region == "support_edge":
            return "support_edge_radial_pressure_balance"
        return "distributed_radial_pressure_balance"
    if channel == "abs_j_l":
        if live:
            return "live_shift_current_or_momentum_flux"
        if stage in {"catch_rematch", "entry_precatch"}:
            return "infrastructure_shift_current"
        return "reset_or_background_current"
    if channel == "abs_pOmega":
        if live:
            return "live_angular_pressure_capacity"
        if region == "support_edge":
            return "support_edge_angular_capacity"
        return "distributed_angular_pressure"
    return _channel_role(channel)


def _algebra_signature(row: pd.Series, channel: str) -> dict[str, Any]:
    alpha = max(abs(_finite(row.get("alpha"), 1.0)), 1.0e-30)
    rho = _finite(row.get("rho_euler"))
    p_l = _finite(row.get("p_l_unit"))
    j_l = _finite(row.get("j_l_unit"))
    p_omega = _finite(row.get("p_omega_unit"))
    rho_plus_p = rho + p_l
    current_term = 2.0 * j_l
    tkk_plus = _finite(row.get("Tkk_plus")) / (alpha * alpha)
    tkk_minus = _finite(row.get("Tkk_minus")) / (alpha * alpha)
    branch = "plus" if tkk_plus <= tkk_minus else "minus"
    selected_tkk = min(tkk_plus, tkk_minus)
    denom = abs(rho) + abs(p_l) + abs(current_term) + 1.0e-30
    cancellation_ratio = 1.0 - min(abs(rho_plus_p + current_term), abs(rho_plus_p - current_term)) / denom
    pressure_cancel_ratio = 1.0 - abs(rho + p_l) / (abs(rho) + abs(p_l) + 1.0e-30)
    current_dominance = abs(current_term) / (abs(rho_plus_p) + 1.0e-30)
    angular_dominance = abs(p_omega) / (abs(p_l) + abs(j_l) + abs(rho) + 1.0e-30)
    if channel == "neg_Tkk_radial":
        if current_dominance > 1.0:
            mechanism = "current_selected_null_branch"
        elif pressure_cancel_ratio > 0.90:
            mechanism = "rho_p_l_cancellation_null_residual"
        elif selected_tkk < 0.0:
            mechanism = "direct_radial_null_deficit"
        else:
            mechanism = "weak_or_weighted_null_deficit"
    elif channel == "abs_p_l":
        mechanism = "rho_p_l_pressure_balance" if pressure_cancel_ratio > 0.75 else "direct_radial_pressure"
    elif channel == "abs_j_l":
        mechanism = "shift_current_momentum"
    elif channel == "abs_pOmega":
        mechanism = "angular_capacity_pressure" if angular_dominance > 1.0 else "mixed_angular_pressure"
    else:
        mechanism = "unclassified"
    return {
        "rho_euler": rho,
        "p_l_unit": p_l,
        "j_l_unit": j_l,
        "p_omega_unit": p_omega,
        "rho_plus_p_l": rho_plus_p,
        "two_j_l": current_term,
        "Tkk_plus_orthonormal": tkk_plus,
        "Tkk_minus_orthonormal": tkk_minus,
        "selected_null_branch": branch,
        "selected_Tkk_orthonormal": selected_tkk,
        "null_cancellation_ratio": float(cancellation_ratio),
        "rho_p_l_pressure_cancel_ratio": float(pressure_cancel_ratio),
        "current_dominance_ratio": float(current_dominance),
        "angular_dominance_ratio": float(angular_dominance),
        "algebraic_mechanism": mechanism,
    }


def decompose_ledger(
    ledger_dir: Path,
    *,
    label: str | None = None,
    channels: Iterable[str] = ("neg_Tkk_radial", "abs_p_l", "abs_j_l", "abs_pOmega"),
    limit_per_channel: int = 40,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    points, manifest, point_path = _load_points(ledger_dir)
    case_label = label or str(manifest.get("label") or manifest.get("case") or ledger_dir.name)
    rows: list[dict[str, Any]] = []
    for channel in channels:
        burden_col = f"volume_burden_{channel}"
        if burden_col not in points.columns:
            points[burden_col] = points.apply(lambda row: _badness(row, channel) * _finite(row.get("volume_weight"), 1.0), axis=1)
        ranked = points.sort_values(burden_col, ascending=False).head(int(limit_per_channel))
        for rank, (_, row) in enumerate(ranked.iterrows(), start=1):
            signature = _algebra_signature(row, channel)
            rows.append({
                "label": case_label,
                "case": manifest.get("case", case_label),
                "channel": channel,
                "channel_description": CHANNELS.get(channel, ""),
                "rank": rank,
                "s": _finite(row.get("s")),
                "l": _finite(row.get("l")),
                "stage": row.get("stage", ""),
                "region": row.get("region", ""),
                "inside_packet_live": bool(row.get("inside_packet_live", False)),
                "inside_packet_geom": bool(row.get("inside_packet_geom", False)),
                "badness": _badness(row, channel),
                "volume_burden": _finite(row.get(burden_col)),
                "packet_norm": _finite(row.get("packet_norm")),
                "source_role": _source_assignment(row, channel),
                "channel_role": _channel_role(channel),
                **signature,
            })
    detail = pd.DataFrame(rows)
    if detail.empty:
        summary = pd.DataFrame()
    else:
        summary = (
            detail.groupby(
                ["label", "channel", "source_role", "algebraic_mechanism", "stage", "region", "inside_packet_live"],
                dropna=False,
            )
            .agg(
                rows=("rank", "count"),
                mean_badness=("badness", "mean"),
                max_badness=("badness", "max"),
                total_volume_burden=("volume_burden", "sum"),
                mean_null_cancellation=("null_cancellation_ratio", "mean"),
                mean_current_dominance=("current_dominance_ratio", "mean"),
            )
            .reset_index()
            .sort_values(["label", "channel", "total_volume_burden"], ascending=[True, True, False])
        )
    metadata = {
        "label": case_label,
        "ledger_dir": str(ledger_dir),
        "source_manifest": str(ledger_dir / "source_ledger_manifest.json"),
        "point_ledger": str(point_path),
        "point_ledger_sha256": sha256_file(point_path),
        "case": manifest.get("case"),
        "rows": int(len(detail)),
        "limit_per_channel": int(limit_per_channel),
        "channels": list(channels),
    }
    return detail, summary, metadata


def write_decomposition_outputs(
    outdir: Path,
    decompositions: list[tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    detail = pd.concat([item[0] for item in decompositions], ignore_index=True) if decompositions else pd.DataFrame()
    summary = pd.concat([item[1] for item in decompositions], ignore_index=True) if decompositions else pd.DataFrame()
    detail_path = outdir / "source_decomposition_detail.csv"
    summary_path = outdir / "source_decomposition_summary.csv"
    detail.to_csv(detail_path, index=False)
    summary.to_csv(summary_path, index=False)
    manifest_path = outdir / "source_decomposition_manifest.json"
    write_manifest(manifest_path, {
        "inputs": [item[2] for item in decompositions],
        "files": {
            "detail": str(detail_path),
            "summary": str(summary_path),
        },
        "detail_rows": int(len(detail)),
        "summary_rows": int(len(summary)),
        "detail_sha256": sha256_file(detail_path),
        "summary_sha256": sha256_file(summary_path),
        "caveat": "Algebraic demanded-source role map; source assignments are diagnostic labels, not matter-model solves.",
    })
    return {"detail": detail_path, "summary": summary_path, "manifest": manifest_path}
