from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def _smooth_window(window: np.ndarray, passes: int) -> np.ndarray:
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
    if max_w > 0.0:
        w = w / max_w
    return np.clip(w * w * (3.0 - 2.0 * w), 0.0, 1.0)


def _weighted_center(values: np.ndarray, weights: np.ndarray, axis: int) -> float:
    axis_weights = np.asarray(weights, dtype=float).sum(axis=axis)
    total = float(axis_weights.sum())
    if total <= 0.0:
        return float(np.mean(values))
    return float(np.dot(values, axis_weights) / total)


def _gaussian_axis(values: np.ndarray, center: float, width: float) -> np.ndarray:
    if width <= 0.0:
        raise ValueError("width must be positive")
    return np.exp(-0.5 * ((values - center) / width) ** 2)


def _read_point_ledger(path_or_zip: str, member: str | None) -> pd.DataFrame:
    path = Path(path_or_zip)
    if member:
        with zipfile.ZipFile(path) as zf:
            with zf.open(member) as f:
                return pd.read_csv(f)
    return pd.read_csv(path)


def _grid_arrays(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, tuple[int, int]]:
    s_values = np.array(sorted(df["s"].unique()), dtype=float)
    l_values = np.array(sorted(df["l"].unique()), dtype=float)
    shape = (len(s_values), len(l_values))
    if len(df) != shape[0] * shape[1]:
        raise ValueError(f"Input ledger is not a complete rectangular grid: rows={len(df)}, shape={shape}")
    return s_values, l_values, shape


def _to_grid(df: pd.DataFrame, column: str, shape: tuple[int, int]) -> np.ndarray:
    return df.sort_values(["s", "l"])[column].to_numpy().reshape(shape)


def _support_window(
    df: pd.DataFrame,
    *,
    support_radius: float,
    support_multiplier: float,
    catch_lead: float,
    temporal_width: float,
    smoothing_passes: int,
) -> np.ndarray:
    s_values, l_values, shape = _grid_arrays(df)
    ordered = df.sort_values(["s", "l"]).copy()
    stage = _to_grid(ordered, "stage", shape)
    l_grid = np.tile(l_values, (shape[0], 1))
    live_packet = _to_grid(ordered, "inside_packet_live", shape).astype(bool)

    support_limit = support_radius * support_multiplier
    mask = (stage == "catch_rematch") & (np.abs(l_grid) <= support_limit)
    window = mask.astype(float)
    window *= (~live_packet).astype(float)

    schedule_center = _weighted_center(s_values, np.abs(window), axis=1) - catch_lead
    temporal = _gaussian_axis(s_values, schedule_center, temporal_width)
    window *= temporal[:, None]
    return _smooth_window(window, smoothing_passes)


def _packet_norm_with_delta(df: pd.DataFrame, delta_beta: np.ndarray) -> np.ndarray:
    ordered = df.sort_values(["s", "l"]).copy()
    _, _, shape = _grid_arrays(ordered)
    alpha = _to_grid(ordered, "alpha", shape).astype(float)
    gamma_ll = _to_grid(ordered, "gamma_ll", shape).astype(float)
    beta = _to_grid(ordered, "beta", shape).astype(float)
    u_packet = _to_grid(ordered, "U_packet", shape).astype(float)
    b_field = _to_grid(ordered, "B", shape).astype(float)
    vcoord = u_packet / b_field
    return -alpha * alpha + gamma_ll * (vcoord + beta + delta_beta) ** 2


def _summarize_case(df: pd.DataFrame, packet_norm_new: np.ndarray, delta_beta: np.ndarray, name: str, spec: dict[str, Any]) -> dict[str, Any]:
    ordered = df.sort_values(["s", "l"]).copy()
    _, _, shape = _grid_arrays(ordered)
    live = _to_grid(ordered, "inside_packet_live", shape).astype(bool)
    packet_norm_old = _to_grid(ordered, "packet_norm", shape).astype(float)
    live_old = packet_norm_old[live]
    live_new = packet_norm_new[live]
    live_delta = live_new - live_old

    return {
        "run_name": name,
        **spec,
        "baseline_max_packet_norm_live": float(np.nanmax(live_old)),
        "baseline_min_packet_norm_live": float(np.nanmin(live_old)),
        "max_packet_norm_live": float(np.nanmax(live_new)),
        "min_packet_norm_live": float(np.nanmin(live_new)),
        "positive_packet_norm_live": int(np.sum(live_new > 0.0)),
        "max_packet_norm_live_change": float(np.nanmax(live_delta)),
        "min_packet_norm_live_change": float(np.nanmin(live_delta)),
        "max_abs_packet_norm_live_change": float(np.nanmax(np.abs(live_delta))),
        "max_abs_delta_beta_global": float(np.nanmax(np.abs(delta_beta))),
        "max_abs_delta_beta_live_packet": float(np.nanmax(np.abs(delta_beta[live])) if np.any(live) else 0.0),
        "nonzero_delta_beta_live_packet_points": int(np.sum(np.abs(delta_beta[live]) > 0.0)) if np.any(live) else 0,
        "live_points": int(np.sum(live)),
        "packet_safe": bool(np.sum(live_new > 0.0) == 0),
    }


def run_overlay(args: argparse.Namespace) -> tuple[pd.DataFrame, Path]:
    df = _read_point_ledger(args.input, args.member)
    required = {"s", "l", "stage", "inside_packet_live", "alpha", "beta", "gamma_ll", "U_packet", "B", "packet_norm"}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"Input point ledger missing columns: {sorted(missing)}")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    variants: list[tuple[str, dict[str, Any]]] = []
    for amp in args.amplitudes:
        for sign_name, sign in [("pos", 1.0), ("neg", -1.0)]:
            variants.append(
                (
                    f"amp_{sign_name}_{amp:g}_lead{args.catch_lead:g}_tw{args.temporal_width:g}",
                    {
                        "amplitude": sign * amp,
                        "abs_amplitude": amp,
                        "sign": sign_name,
                        "catch_lead": args.catch_lead,
                        "temporal_width": args.temporal_width,
                        "smoothing_passes": args.smoothing_passes,
                        "support_radius": args.support_radius,
                        "support_multiplier": args.support_multiplier,
                    },
                )
            )

    rows = []
    window = _support_window(
        df,
        support_radius=args.support_radius,
        support_multiplier=args.support_multiplier,
        catch_lead=args.catch_lead,
        temporal_width=args.temporal_width,
        smoothing_passes=args.smoothing_passes,
    )
    for name, spec in variants:
        delta_beta = float(spec["amplitude"]) * window
        packet_norm_new = _packet_norm_with_delta(df, delta_beta)
        rows.append(_summarize_case(df, packet_norm_new, delta_beta, name, spec))

    summary = pd.DataFrame(rows).sort_values(["abs_amplitude", "sign"])
    summary_path = out_dir / "support_shell_packet_safety_summary.csv"
    summary.to_csv(summary_path, index=False)

    metadata = {
        "input": args.input,
        "member": args.member,
        "method": "packet_norm_new = -alpha^2 + gamma_ll * (U_packet/B + beta + delta_beta)^2",
        "window": {
            "scope": "catch_rematch support shell",
            "support_limit": args.support_radius * args.support_multiplier,
            "packet_exclusion": "inside_packet_live",
            "catch_lead": args.catch_lead,
            "temporal_width": args.temporal_width,
            "smoothing_passes": args.smoothing_passes,
        },
        "amplitudes": args.amplitudes,
    }
    (out_dir / "support_shell_packet_safety_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    with (out_dir / "support_shell_packet_safety_report.md").open("w", encoding="utf-8") as f:
        f.write("# Support-Shell Packet-Safety Overlay\n\n")
        f.write("This is a packet-norm overlay on an existing shaped-catch/radial-soft/lapse-cushion point ledger. It modifies only the beta/carrying-flow channel used by the promoted support-shell component.\n\n")
        f.write("The recomputed packet norm is `-alpha^2 + gamma_ll * (U_packet/B + beta + delta_beta)^2`.\n\n")
        f.write("## Summary\n\n")
        cols = [
            "run_name",
            "amplitude",
            "max_packet_norm_live",
            "positive_packet_norm_live",
            "max_packet_norm_live_change",
            "max_abs_packet_norm_live_change",
            "max_abs_delta_beta_live_packet",
            "packet_safe",
        ]
        f.write(summary[cols].to_markdown(index=False))
        f.write("\n")

    return summary, summary_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Overlay the support-shell beta component on a freeze-branch point ledger and test packet norm safety.")
    parser.add_argument("--input", required=True, help="CSV path, or ZIP path when --member is supplied")
    parser.add_argument("--member", help="CSV member inside the ZIP input")
    parser.add_argument("--output-dir", default="runs/support_shell_packet_safety_overlay")
    parser.add_argument("--support-radius", type=float, default=1.75)
    parser.add_argument("--support-multiplier", type=float, default=1.2)
    parser.add_argument("--catch-lead", type=float, default=0.75)
    parser.add_argument("--temporal-width", type=float, default=0.5)
    parser.add_argument("--smoothing-passes", type=int, default=1)
    parser.add_argument(
        "--amplitudes",
        type=float,
        nargs="+",
        default=[5e-8, 1e-7, 2.5e-7, 5e-7, 1e-6, 2.5e-6, 5e-6, 1e-5],
    )
    args = parser.parse_args()
    _, summary_path = run_overlay(args)
    print(f"Wrote {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
