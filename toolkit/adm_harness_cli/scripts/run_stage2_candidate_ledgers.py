from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import replace
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from adm_harness.source_ledger import (  # noqa: E402
    case_metadata,
    compute_case,
    sha256_file,
    smeared_null_summary,
    summarize,
    top_bad_points,
    write_manifest,
)
from adm_harness.source_screening import (  # noqa: E402
    load_source_screen_context,
    load_spec_list,
    select_specs,
)
from run_smooth_split_screen import BASE_SPECS, _case_for_spec  # noqa: E402


def _write_tables(outdir: Path, points: pd.DataFrame) -> dict[str, Path]:
    summary, compact, stage, safety, decision = summarize(points)
    files = {
        "point_ledger": outdir / "source_ledger_point_ledger.csv",
        "summary_long": outdir / "source_ledger_summary_long.csv",
        "global_compact": outdir / "source_ledger_global_compact.csv",
        "stage_summary": outdir / "source_ledger_stage_summary.csv",
        "safety": outdir / "source_ledger_safety.csv",
        "decision_table": outdir / "source_ledger_decision_table.csv",
        "top_bad_points": outdir / "source_ledger_top_bad_points.csv",
        "smeared_null": outdir / "source_ledger_smeared_null.csv",
    }
    points.to_csv(files["point_ledger"], index=False)
    summary.to_csv(files["summary_long"], index=False)
    compact.to_csv(files["global_compact"], index=False)
    stage.to_csv(files["stage_summary"], index=False)
    safety.to_csv(files["safety"], index=False)
    decision.to_csv(files["decision_table"], index=False)
    top_bad_points(points).to_csv(files["top_bad_points"], index=False)
    smeared_null_summary(points).to_csv(files["smeared_null"], index=False)
    return files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Replay selected smooth-split candidate specs into full source-ledger "
            "directories suitable for Stage II source-family screening."
        )
    )
    parser.add_argument(
        "--source-ledger-dir",
        type=Path,
        required=True,
        help="Reference Stage I source-ledger directory whose params/grid seed the candidate specs.",
    )
    parser.add_argument("--spec-file", type=Path, default=None)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--only-labels", nargs="+", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--ns", type=int, default=61)
    parser.add_argument("--nl", type=int, default=83)
    parser.add_argument("--s-min", type=float, default=-0.96)
    parser.add_argument("--s-max", type=float, default=1.65)
    parser.add_argument("--l-min", type=float, default=-2.80)
    parser.add_argument("--l-max", type=float, default=2.80)
    parser.add_argument("--h-s", type=float, default=None)
    parser.add_argument("--h-l", type=float, default=None)
    parser.add_argument(
        "--progress",
        dest="progress",
        action="store_true",
        default=True,
        help="Print row-level progress while computing uncached candidate ledgers.",
    )
    parser.add_argument(
        "--no-progress",
        dest="progress",
        action="store_false",
        help="Suppress row-level progress for quiet batch runs.",
    )
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    context = load_source_screen_context(
        args.source_ledger_dir,
        ns=args.ns,
        nl=args.nl,
        s_min=args.s_min,
        s_max=args.s_max,
        l_min=args.l_min,
        l_max=args.l_max,
        h_s=args.h_s,
        h_l=args.h_l,
    )
    specs = select_specs(load_spec_list(args.spec_file, BASE_SPECS, "stage2 candidate"), args.only_labels, args.limit)
    args.outdir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for spec in specs:
        label = str(spec["label"])
        params = context.params
        support_updates: dict[str, float] = {}
        if "support_radius" in spec:
            support_updates["Rth"] = float(spec["support_radius"])
            support_updates["ROmega"] = float(spec["support_radius"])
        if "support_width" in spec:
            support_updates["w_th"] = float(spec["support_width"])
        if "angular_width" in spec:
            support_updates["wOmega"] = float(spec["angular_width"])
        if "angular_amplitude" in spec:
            support_updates["aOmega"] = float(spec["angular_amplitude"])
        if support_updates:
            params = replace(params, **support_updates)
        case = _case_for_spec(label, spec, params)
        case_dir = args.outdir / label
        point_path = case_dir / "source_ledger_point_ledger.csv"
        started_at = time.perf_counter()
        if point_path.exists() and not args.force:
            points = pd.read_csv(point_path)
            cache_status = "reused"
        else:
            case_dir.mkdir(parents=True, exist_ok=True)
            print(json.dumps({
                "event": "compute_start",
                "label": label,
                "case": case.name,
                "grid": context.grid,
                "outdir": str(case_dir),
            }), flush=True)
            points = compute_case(case, progress=args.progress, **context.grid)
            cache_status = "computed"
        elapsed_s = time.perf_counter() - started_at
        files = _write_tables(case_dir, points)
        file_strings = {key: str(path) for key, path in files.items()}
        manifest = case_metadata(case, context.grid, file_strings)
        manifest.update({
            "label": label,
            "spec": spec,
            "source_manifest": str(context.manifest_path),
            "cache_status": cache_status,
            "rows": int(len(points)),
            "point_ledger_sha256": sha256_file(files["point_ledger"]),
        })
        write_manifest(case_dir / "source_ledger_manifest.json", manifest)
        row = {
            "label": label,
            "case": case.name,
            "outdir": str(case_dir),
            "cache_status": cache_status,
            "elapsed_s": round(elapsed_s, 3),
            "rows": int(len(points)),
            "positive_packet_norm_live": int((points.loc[points["inside_packet_live"].astype(bool), "packet_norm"] > 0).sum()),
        }
        rows.append(row)
        print(json.dumps(row), flush=True)

    index_path = args.outdir / "stage2_candidate_ledgers_index.csv"
    pd.DataFrame(rows).to_csv(index_path, index=False)
    manifest_path = args.outdir / "stage2_candidate_ledgers_manifest.json"
    write_manifest(manifest_path, {
        "source_manifest": str(context.manifest_path),
        "spec_file": str(args.spec_file) if args.spec_file else None,
        "grid": context.grid,
        "rows": len(rows),
        "index": str(index_path),
        "index_sha256": sha256_file(index_path),
    })
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": len(rows),
        "index": str(index_path),
        "manifest": str(manifest_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
