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
    parser.add_argument("--ns", type=int, default=41)
    parser.add_argument("--nl", type=int, default=73)
    parser.add_argument("--s-min", type=float, default=-0.35)
    parser.add_argument("--s-max", type=float, default=1.65)
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
        "--reference",
        default=None,
        help="Optional reference CSV, or zip path plus member as bundle.zip::member.csv.",
    )
    parser.add_argument("--reference-case", default=None, help="Optional case name to filter inside the reference table.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    case = branch_case(args.variant, args.service_factor, **_case_overrides(args))
    outdir = args.outdir or Path("runs") / "source_ledgers" / case.name
    outdir.mkdir(parents=True, exist_ok=True)

    point_path = outdir / "source_ledger_point_ledger.csv"
    if point_path.exists() and not args.force:
        points = pd.read_csv(point_path)
        cache_status = "reused"
    else:
        points = compute_case(
            case,
            args.ns,
            args.nl,
            args.s_min,
            args.s_max,
            args.l_min,
            args.l_max,
            args.h_s,
            args.h_l,
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

    grid = {
        "ns": args.ns,
        "nl": args.nl,
        "s_min": args.s_min,
        "s_max": args.s_max,
        "l_min": args.l_min,
        "l_max": args.l_max,
        "h_s": args.h_s,
        "h_l": args.h_l,
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
