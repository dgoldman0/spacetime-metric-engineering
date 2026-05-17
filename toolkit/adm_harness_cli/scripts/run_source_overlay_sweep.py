from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
import sys

if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.source_ledger import CHANNELS, branch_case, compute_case, summarize, summarize_safety, write_manifest  # noqa: E402


DEFAULT_S_MIN = -0.35
DEFAULT_S_MAX = 1.65
DEFAULT_S_STEP = 0.05


def _token(value: float) -> str:
    text = f"{float(value):.10g}"
    return text.replace("-", "m").replace("+", "").replace(".", "p").replace("e", "e")


def _resolve_grid(args: argparse.Namespace, overlay_case) -> dict[str, Any]:
    params = overlay_case.params
    s_max = float(args.s_max)
    s_min = DEFAULT_S_MIN if args.s_min is None else float(args.s_min)
    if args.s_min is None:
        catch_width = max(params.w_catch_packet, params.w_catch_beta)
        edge_width = params.support_shell_catch_edge_width if params.support_shell_catch_edge_width is not None else catch_width / 4.0
        s_min = min(s_min, params.x_catch_packet - 2.0 * catch_width - 4.0 * edge_width)
    ns = int(args.ns) if args.ns is not None else int(round((s_max - s_min) / DEFAULT_S_STEP)) + 1
    return {
        "ns": ns,
        "nl": int(args.nl),
        "s_min": s_min,
        "s_max": s_max,
        "l_min": float(args.l_min),
        "l_max": float(args.l_max),
        "h_s": float(args.h_s),
        "h_l": float(args.h_l),
    }


def _compact_by_channel(points: pd.DataFrame) -> pd.DataFrame:
    _, compact, _, _, _ = summarize(points)
    return compact.set_index("channel")


def _compare_channels(base_compact: pd.DataFrame, overlay_compact: pd.DataFrame, spec: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for channel in CHANNELS:
        base = base_compact.loc[channel]
        overlay = overlay_compact.loc[channel]
        row = {**spec, "channel": channel}
        for key in ["total_burden", "live_packet_burden", "live_packet_fraction", "point_peak", "live_packet_point_peak"]:
            base_value = float(base[key])
            overlay_value = float(overlay[key])
            row[f"{key}_base"] = base_value
            row[f"{key}_overlay"] = overlay_value
            row[f"{key}_delta"] = overlay_value - base_value
            row[f"{key}_ratio"] = overlay_value / base_value if base_value else math.nan
        rows.append(row)
    return rows


def _compare_case(base_points: pd.DataFrame, overlay_points: pd.DataFrame, spec: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    base_compact = _compact_by_channel(base_points)
    overlay_compact = _compact_by_channel(overlay_points)
    channel_rows = _compare_channels(base_compact, overlay_compact, spec)

    merged = overlay_points.merge(base_points, on=["s", "l"], suffixes=("_overlay", "_base"))
    live = merged["inside_packet_live_overlay"].astype(bool).to_numpy()
    packet_delta = merged["packet_norm_overlay"].astype(float) - merged["packet_norm_base"].astype(float)
    safety = summarize_safety(overlay_points).iloc[0]

    burden_ratios = [row["total_burden_ratio"] for row in channel_rows if math.isfinite(row["total_burden_ratio"])]
    live_ratios = [row["live_packet_burden_ratio"] for row in channel_rows if math.isfinite(row["live_packet_burden_ratio"])]
    peak_ratios = [row["point_peak_ratio"] for row in channel_rows if math.isfinite(row["point_peak_ratio"])]
    max_window_row = overlay_points.loc[overlay_points["support_shell_window"].astype(float).idxmax()]

    summary = {
        **spec,
        "case": str(overlay_points["case"].iloc[0]),
        "rows": int(len(overlay_points)),
        "positive_packet_norm_live": int(safety["positive_packet_norm_live"]),
        "max_packet_norm_live": float(safety["max_packet_norm_live"]),
        "min_packet_norm_live": float(safety["min_packet_norm_live"]),
        "packet_norm_live_delta_max_abs": float(np.nanmax(np.abs(packet_delta.to_numpy()[live]))) if live.any() else math.nan,
        "packet_norm_live_delta_mean_abs": float(np.nanmean(np.abs(packet_delta.to_numpy()[live]))) if live.any() else math.nan,
        "support_shell_window_max": float(overlay_points["support_shell_window"].astype(float).max()),
        "support_shell_window_gt_1e_3_points": int((overlay_points["support_shell_window"].astype(float).abs() > 1.0e-3).sum()),
        "support_shell_delta_beta_abs_max": float(overlay_points["support_shell_delta_beta"].astype(float).abs().max()),
        "support_shell_delta_alpha_abs_max": float(overlay_points["support_shell_delta_alpha"].astype(float).abs().max()),
        "support_shell_delta_gamma_ll_abs_max": float(overlay_points["support_shell_delta_gamma_ll"].astype(float).abs().max()),
        "support_shell_window_peak_s": float(max_window_row["s"]),
        "support_shell_window_peak_l": float(max_window_row["l"]),
        "support_shell_window_peak_stage": str(max_window_row["stage"]),
        "support_shell_window_peak_region": str(max_window_row["region"]),
        "max_total_burden_ratio": max(burden_ratios) if burden_ratios else math.nan,
        "min_total_burden_ratio": min(burden_ratios) if burden_ratios else math.nan,
        "max_live_packet_burden_ratio": max(live_ratios) if live_ratios else math.nan,
        "max_point_peak_ratio": max(peak_ratios) if peak_ratios else math.nan,
    }

    focus = {row["channel"]: row for row in channel_rows}
    for channel in ["neg_Tkk_radial", "abs_p_l", "abs_j_l", "neg_rho_packet"]:
        row = focus[channel]
        summary[f"{channel}_total_delta"] = row["total_burden_delta"]
        summary[f"{channel}_total_ratio"] = row["total_burden_ratio"]
        summary[f"{channel}_live_delta"] = row["live_packet_burden_delta"]
        summary[f"{channel}_live_ratio"] = row["live_packet_burden_ratio"]
        summary[f"{channel}_peak_ratio"] = row["point_peak_ratio"]
    return summary, channel_rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sweep the continuous support-shell metric overlay in the 4D source ledger.")
    parser.add_argument("--variant", default="tuned_w0569_eta200")
    parser.add_argument("--service-factor", type=float, default=5.0)
    parser.add_argument("--outdir", type=Path, default=Path("runs/source_overlay_sweep_v5"))
    parser.add_argument("--amplitudes", type=float, nargs="+", default=[1.0e-7, 1.0e-6, 1.0e-5, 1.0e-4, 1.0e-3, 1.0e-2])
    parser.add_argument("--signs", choices=["pos", "neg"], nargs="+", default=["pos", "neg"])
    parser.add_argument("--catch-leads", type=float, nargs="+", default=[1.0])
    parser.add_argument("--temporal-widths", type=float, nargs="+", default=[0.35])
    parser.add_argument(
        "--clock-lapse-ratios",
        type=float,
        nargs="+",
        default=[0.0],
        help="Log-gain ratios against the signed carrying-flow amplitude for the support-shell clock-lapse partner.",
    )
    parser.add_argument(
        "--rail-stretch-ratios",
        type=float,
        nargs="+",
        default=[0.0],
        help="Log-gain ratios against the signed carrying-flow amplitude for the support-shell rail-stretch partner.",
    )
    parser.add_argument("--smoothness-order", type=int, default=1)
    parser.add_argument("--support-shell-inner-multiplier", type=float, default=0.65)
    parser.add_argument("--support-shell-radial-multiplier", type=float, default=1.20)
    parser.add_argument("--support-shell-radial-width", type=float, default=None)
    parser.add_argument("--packet-exclusion", type=float, default=1.0)
    parser.add_argument("--ns", type=int, default=None)
    parser.add_argument("--nl", type=int, default=73)
    parser.add_argument("--s-min", type=float, default=None)
    parser.add_argument("--s-max", type=float, default=DEFAULT_S_MAX)
    parser.add_argument("--l-min", type=float, default=-2.80)
    parser.add_argument("--l-max", type=float, default=2.80)
    parser.add_argument("--h-s", type=float, default=2.5e-3)
    parser.add_argument("--h-l", type=float, default=2.5e-3)
    parser.add_argument("--quiet", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    grid_case = branch_case(
        args.variant,
        args.service_factor,
        support_shell_overlay_enabled=True,
        support_shell_catch_lead=args.catch_leads[0],
        support_shell_temporal_width=args.temporal_widths[0],
        support_shell_smoothness_order=args.smoothness_order,
        support_shell_inner_multiplier=args.support_shell_inner_multiplier,
        support_shell_radial_multiplier=args.support_shell_radial_multiplier,
        support_shell_radial_width=args.support_shell_radial_width,
        support_shell_packet_exclusion=args.packet_exclusion,
        support_shell_clock_lapse_log_gain=0.0,
        support_shell_rail_stretch_log_gain=0.0,
    )
    grid = _resolve_grid(args, grid_case)
    base_case = branch_case(args.variant, args.service_factor)
    base_points = compute_case(base_case, progress=not args.quiet, **grid)

    summary_rows: list[dict[str, Any]] = []
    channel_rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    total = (
        len(args.amplitudes)
        * len(args.signs)
        * len(args.catch_leads)
        * len(args.temporal_widths)
        * len(args.clock_lapse_ratios)
        * len(args.rail_stretch_ratios)
    )
    index = 0
    for abs_amplitude in args.amplitudes:
        for sign_name in args.signs:
            sign = 1.0 if sign_name == "pos" else -1.0
            for catch_lead in args.catch_leads:
                for temporal_width in args.temporal_widths:
                    for clock_lapse_ratio in args.clock_lapse_ratios:
                        for rail_stretch_ratio in args.rail_stretch_ratios:
                            index += 1
                            amplitude = sign * float(abs_amplitude)
                            clock_lapse_log_gain = amplitude * float(clock_lapse_ratio)
                            rail_stretch_log_gain = amplitude * float(rail_stretch_ratio)
                            spec = {
                                "abs_amplitude": float(abs_amplitude),
                                "sign": sign_name,
                                "amplitude": amplitude,
                                "catch_lead": float(catch_lead),
                                "temporal_width": float(temporal_width),
                                "clock_lapse_ratio": float(clock_lapse_ratio),
                                "clock_lapse_log_gain": float(clock_lapse_log_gain),
                                "rail_stretch_ratio": float(rail_stretch_ratio),
                                "rail_stretch_log_gain": float(rail_stretch_log_gain),
                            }
                            if not args.quiet:
                                print(
                                    f"[{index}/{total}] amp={amplitude:g} lead={catch_lead:g} tw={temporal_width:g} "
                                    f"cl={clock_lapse_log_gain:g} rs={rail_stretch_log_gain:g}",
                                    flush=True,
                                )
                            try:
                                overlay_case = branch_case(
                                    args.variant,
                                    args.service_factor,
                                    support_shell_overlay_enabled=True,
                                    support_shell_amplitude=amplitude,
                                    support_shell_catch_lead=catch_lead,
                                    support_shell_temporal_width=temporal_width,
                                    support_shell_smoothness_order=args.smoothness_order,
                                    support_shell_inner_multiplier=args.support_shell_inner_multiplier,
                                    support_shell_radial_multiplier=args.support_shell_radial_multiplier,
                                    support_shell_radial_width=args.support_shell_radial_width,
                                    support_shell_packet_exclusion=args.packet_exclusion,
                                    support_shell_clock_lapse_log_gain=clock_lapse_log_gain,
                                    support_shell_rail_stretch_log_gain=rail_stretch_log_gain,
                                )
                                overlay_points = compute_case(overlay_case, progress=False, **grid)
                                summary, channels = _compare_case(base_points, overlay_points, spec)
                                summary_rows.append(summary)
                                channel_rows.extend(channels)
                            except Exception as exc:
                                failures.append({**spec, "error": repr(exc)})

    sort_cols = [
        "abs_amplitude",
        "sign",
        "catch_lead",
        "temporal_width",
        "clock_lapse_ratio",
        "rail_stretch_ratio",
    ]
    summary_df = pd.DataFrame(summary_rows).sort_values(sort_cols)
    channel_df = pd.DataFrame(channel_rows).sort_values([*sort_cols, "channel"])
    failure_df = pd.DataFrame(failures)

    summary_path = args.outdir / "source_overlay_sweep_summary.csv"
    channel_path = args.outdir / "source_overlay_sweep_channel_deltas.csv"
    failure_path = args.outdir / "source_overlay_sweep_failures.csv"
    summary_df.to_csv(summary_path, index=False)
    channel_df.to_csv(channel_path, index=False)
    failure_df.to_csv(failure_path, index=False)

    metadata = {
        "variant": args.variant,
        "service_factor": args.service_factor,
        "grid": grid,
        "amplitudes": args.amplitudes,
        "signs": args.signs,
        "catch_leads": args.catch_leads,
        "temporal_widths": args.temporal_widths,
        "clock_lapse_ratios": args.clock_lapse_ratios,
        "rail_stretch_ratios": args.rail_stretch_ratios,
        "smoothness_order": args.smoothness_order,
        "support_shell_inner_multiplier": args.support_shell_inner_multiplier,
        "support_shell_radial_multiplier": args.support_shell_radial_multiplier,
        "support_shell_radial_width": args.support_shell_radial_width,
        "packet_exclusion": args.packet_exclusion,
        "files": {
            "summary": str(summary_path),
            "channel_deltas": str(channel_path),
            "failures": str(failure_path),
        },
        "failures": len(failures),
    }
    write_manifest(args.outdir / "source_overlay_sweep_metadata.json", metadata)
    print(json.dumps({"ok": len(failures) == 0, "outdir": str(args.outdir), "rows": len(summary_df), "failures": len(failures)}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
