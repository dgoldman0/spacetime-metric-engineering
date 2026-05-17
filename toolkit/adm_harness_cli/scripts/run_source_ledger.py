from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
import sys

if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.source_ledger import (  # noqa: E402
    branch_case,
    case_metadata,
    compare_to_reference,
    compute_case,
    read_reference_table,
    sha256_file,
    summarize,
    top_bad_points,
    write_manifest,
)


DEFAULT_S_MIN = -0.35
DEFAULT_S_MAX = 1.65
DEFAULT_S_STEP = 0.05
DEFAULT_NS = 41


def _case_overrides(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "w_th": args.w_th,
        "eta_N": args.eta_N,
        "Rth": args.support_radius,
        "ROmega": args.support_radius,
        "w_pass": args.w_pass,
        "x_catch_beta": args.x_catch_beta,
        "x_catch_packet": args.x_catch_packet,
        "w_catch_beta": args.w_catch_beta,
        "w_catch_packet": args.w_catch_packet,
        "support_shell_overlay_enabled": args.support_shell_overlay,
        "support_shell_amplitude": args.support_shell_amplitude,
        "support_shell_catch_lead": args.support_shell_catch_lead,
        "support_shell_temporal_width": args.support_shell_temporal_width,
        "support_shell_temporal_profile": args.support_shell_temporal_profile,
        "support_shell_temporal_shoulder": args.support_shell_temporal_shoulder,
        "support_shell_radial_profile": args.support_shell_radial_profile,
        "support_shell_smoothness_order": args.support_shell_smoothness_order,
        "support_shell_inner_multiplier": args.support_shell_inner_multiplier,
        "support_shell_radial_multiplier": args.support_shell_radial_multiplier,
        "support_shell_radial_width": args.support_shell_radial_width,
        "support_shell_packet_exclusion": args.support_shell_packet_exclusion,
        "support_shell_time_anchor": args.support_shell_time_anchor,
        "support_shell_catch_edge_width": args.support_shell_catch_edge_width,
        "support_shell_clock_lapse_log_gain": args.support_shell_clock_lapse_log_gain,
        "support_shell_rail_stretch_log_gain": args.support_shell_rail_stretch_log_gain,
        "support_shell_throat_capacity_log_gain": args.support_shell_throat_capacity_log_gain,
        "standing_support_packet_exclusion": args.standing_support_packet_exclusion,
        "standing_support_packet_exclusion_radius_multiplier": args.standing_support_packet_exclusion_radius_multiplier,
        "standing_support_packet_exclusion_width_multiplier": args.standing_support_packet_exclusion_width_multiplier,
        "standing_support_packet_exclusion_schedule": args.standing_support_packet_exclusion_schedule,
    }


def _resolve_grid(args: argparse.Namespace, case) -> dict[str, Any]:
    params = case.params
    s_max = float(args.s_max)
    s_min = DEFAULT_S_MIN if args.s_min is None else float(args.s_min)
    if args.s_min is None and params.support_shell_overlay_enabled:
        catch_width = max(params.w_catch_packet, params.w_catch_beta)
        edge_width = params.support_shell_catch_edge_width if params.support_shell_catch_edge_width is not None else catch_width / 4.0
        s_min = min(s_min, params.x_catch_packet - 2.0 * catch_width - 4.0 * edge_width)

    ns = int(args.ns) if args.ns is not None else int(round((s_max - s_min) / DEFAULT_S_STEP)) + 1
    if not params.support_shell_overlay_enabled and args.s_min is None and args.ns is None:
        ns = DEFAULT_NS

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


def _write_tables(outdir: Path, points: pd.DataFrame, prefix: str = "source_ledger") -> dict[str, Path]:
    summary, compact, stage, safety, decision = summarize(points)
    files = {
        "point_ledger": outdir / f"{prefix}_point_ledger.csv",
        "summary_long": outdir / f"{prefix}_summary_long.csv",
        "global_compact": outdir / f"{prefix}_global_compact.csv",
        "stage_summary": outdir / f"{prefix}_stage_summary.csv",
        "safety": outdir / f"{prefix}_safety.csv",
        "decision_table": outdir / f"{prefix}_decision_table.csv",
        "top_bad_points": outdir / f"{prefix}_top_bad_points.csv",
    }
    points.to_csv(files["point_ledger"], index=False)
    summary.to_csv(files["summary_long"], index=False)
    compact.to_csv(files["global_compact"], index=False)
    stage.to_csv(files["stage_summary"], index=False)
    safety.to_csv(files["safety"], index=False)
    decision.to_csv(files["decision_table"], index=False)
    top_bad_points(points).to_csv(files["top_bad_points"], index=False)
    return files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Regenerate report-grade active-rail 4D demanded-source ledgers.")
    parser.add_argument(
        "--variant",
        default="tuned_w0569_eta200",
        choices=["shaped_base", "tuned_w0569_eta200", "conservative_w0565_eta200", "cliff_w0570_eta200", "custom"],
        help="Branch geometry to regenerate. Use custom with explicit knob overrides.",
    )
    parser.add_argument("--service-factor", type=float, default=5.0)
    parser.add_argument("--outdir", type=Path, default=None)
    parser.add_argument("--ns", type=int, default=None)
    parser.add_argument("--nl", type=int, default=73)
    parser.add_argument("--s-min", type=float, default=None)
    parser.add_argument("--s-max", type=float, default=DEFAULT_S_MAX)
    parser.add_argument("--l-min", type=float, default=-2.80)
    parser.add_argument("--l-max", type=float, default=2.80)
    parser.add_argument("--h-s", type=float, default=2.5e-3)
    parser.add_argument("--h-l", type=float, default=2.5e-3)
    parser.add_argument("--force", action="store_true", help="Recompute even when a cached point ledger exists.")
    parser.add_argument("--quiet", action="store_true", help="Suppress row-progress output.")

    parser.add_argument("--w-th", type=float, default=None)
    parser.add_argument("--eta-N", type=float, default=None)
    parser.add_argument("--support-radius", type=float, default=None)
    parser.add_argument("--w-pass", type=float, default=None)
    parser.add_argument("--x-catch-beta", type=float, default=None)
    parser.add_argument("--x-catch-packet", type=float, default=None)
    parser.add_argument("--w-catch-beta", type=float, default=None)
    parser.add_argument("--w-catch-packet", type=float, default=None)

    parser.add_argument(
        "--support-shell-overlay",
        action="store_true",
        help="Add the frozen continuous support-shell carrying-flow overlay to the source metric.",
    )
    parser.add_argument("--support-shell-amplitude", type=float, default=None)
    parser.add_argument("--support-shell-catch-lead", type=float, default=None)
    parser.add_argument("--support-shell-temporal-width", type=float, default=None)
    parser.add_argument(
        "--support-shell-temporal-profile",
        choices=["gaussian", "raised_cosine", "minjerk_pulse", "smooth_box"],
        default=None,
    )
    parser.add_argument("--support-shell-temporal-shoulder", type=float, default=None)
    parser.add_argument(
        "--support-shell-radial-profile",
        choices=["smooth_box", "gaussian_annulus", "raised_cosine_annulus"],
        default=None,
    )
    parser.add_argument("--support-shell-smoothness-order", type=int, default=None)
    parser.add_argument("--support-shell-inner-multiplier", type=float, default=None)
    parser.add_argument("--support-shell-radial-multiplier", type=float, default=None)
    parser.add_argument("--support-shell-radial-width", type=float, default=None)
    parser.add_argument("--support-shell-packet-exclusion", type=float, default=None)
    parser.add_argument("--support-shell-time-anchor", type=float, default=None)
    parser.add_argument("--support-shell-catch-edge-width", type=float, default=None)
    parser.add_argument("--support-shell-clock-lapse-log-gain", type=float, default=None)
    parser.add_argument("--support-shell-rail-stretch-log-gain", type=float, default=None)
    parser.add_argument("--support-shell-throat-capacity-log-gain", type=float, default=None)

    parser.add_argument(
        "--standing-support-packet-exclusion",
        type=float,
        default=None,
        help="Experimental carve-out strength applied to the standing support bump under the packet tube.",
    )
    parser.add_argument("--standing-support-packet-exclusion-radius-multiplier", type=float, default=None)
    parser.add_argument("--standing-support-packet-exclusion-width-multiplier", type=float, default=None)
    parser.add_argument(
        "--standing-support-packet-exclusion-schedule",
        choices=["live_only", "entry_catch_release", "always"],
        default=None,
    )

    parser.add_argument(
        "--reference",
        default=None,
        help="Optional reference CSV, or zip path plus member as bundle.zip::member.csv.",
    )
    parser.add_argument("--reference-case", default=None, help="Optional case name to filter inside the reference table.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    case = branch_case(args.variant, args.service_factor, **_case_overrides(args))
    grid = _resolve_grid(args, case)
    outdir = args.outdir or Path("runs") / "source_ledgers" / case.name
    outdir.mkdir(parents=True, exist_ok=True)

    point_path = outdir / "source_ledger_point_ledger.csv"
    if point_path.exists() and not args.force:
        points = pd.read_csv(point_path)
        cache_status = "reused"
    else:
        points = compute_case(
            case,
            grid["ns"],
            grid["nl"],
            grid["s_min"],
            grid["s_max"],
            grid["l_min"],
            grid["l_max"],
            grid["h_s"],
            grid["h_l"],
            progress=not args.quiet,
        )
        cache_status = "computed"

    files = _write_tables(outdir, points)
    comparison_path = None
    reference_summary = None
    if args.reference:
        reference = read_reference_table(args.reference)
        comparison = compare_to_reference(points, reference, reference_case=args.reference_case)
        comparison_path = outdir / "reference_comparison.csv"
        comparison.to_csv(comparison_path, index=False)
        finite_errors = comparison["max_abs_error"].dropna() if len(comparison) else pd.Series(dtype=float)
        reference_summary = {
            "reference": args.reference,
            "reference_case": args.reference_case,
            "max_abs_error_max": float(finite_errors.max()) if len(finite_errors) else None,
            "matched_rows_min": int(comparison["matched_rows"].min()) if len(comparison) else 0,
            "columns_compared": int(len(comparison)),
        }

    file_strings = {key: str(path) for key, path in files.items()}
    if comparison_path:
        file_strings["reference_comparison"] = str(comparison_path)
    manifest = case_metadata(case, grid, file_strings)
    manifest.update({
        "cache_status": cache_status,
        "rows": int(len(points)),
        "point_ledger_sha256": sha256_file(files["point_ledger"]),
        "reference_comparison": reference_summary,
    })
    write_manifest(outdir / "source_ledger_manifest.json", manifest)
    print(json.dumps({
        "ok": True,
        "case": case.name,
        "cache_status": cache_status,
        "outdir": str(outdir),
        "rows": int(len(points)),
        "reference_comparison": reference_summary,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
