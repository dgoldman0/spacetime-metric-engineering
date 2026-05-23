from __future__ import annotations

import argparse
import json
from dataclasses import fields, replace
from pathlib import Path
from typing import Any

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
import sys

if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.source_ledger import (  # noqa: E402
    SourceCase,
    SourceParams,
    case_metadata,
    compute_case,
    sha256_file,
    smeared_null_summary,
    summarize,
    top_bad_points,
    write_manifest,
)
from adm_harness.source_ledger_parallel import (  # noqa: E402
    compute_case_sharded,
    compute_case_sharded_parquet,
    resolve_s_shard_count,
)
from adm_harness.table_io import read_table, write_table  # noqa: E402


PARAM_KEYS = {field.name for field in fields(SourceParams)}


def _parse_candidate(raw: str) -> tuple[str, dict[str, Any]]:
    label, sep, body = raw.partition(":")
    if not sep or not label.strip():
        raise ValueError(f"candidate must look like label:key=value,key=value, got {raw!r}")
    overrides: dict[str, Any] = {}
    for item in body.split(","):
        item = item.strip()
        if not item:
            continue
        key, item_sep, value = item.partition("=")
        if not item_sep or not key.strip():
            raise ValueError(f"candidate item must look like key=value, got {item!r}")
        key = key.strip()
        if key not in {
            "gain",
            "shape",
            "width",
            "temporal",
            "floor",
            "floor_mode",
            "inner",
            "outer",
            "edge",
            "schedule",
            "temporal_profile",
        }:
            raise ValueError(f"unknown candidate key {key!r}")
        if key in {"shape", "floor_mode", "schedule", "temporal_profile"}:
            overrides[key] = value.strip()
        else:
            overrides[key] = float(value)
    return label.strip(), overrides


def _apply_candidate(base: SourceParams, overrides: dict[str, Any]) -> SourceParams:
    mapped: dict[str, Any] = {}
    key_map = {
        "gain": "standing_support_packet_beta_rematch_gain",
        "shape": "standing_support_packet_beta_rematch_shape",
        "width": "standing_support_packet_beta_rematch_width_multiplier",
        "temporal": "standing_support_packet_beta_rematch_temporal_width_multiplier",
        "floor": "standing_support_packet_beta_rematch_center_floor",
        "floor_mode": "standing_support_packet_beta_rematch_floor_mode",
        "inner": "standing_support_packet_beta_rematch_inner_radius_multiplier",
        "outer": "standing_support_packet_beta_rematch_outer_radius_multiplier",
        "edge": "standing_support_packet_beta_rematch_edge_softness",
        "schedule": "standing_support_packet_beta_rematch_schedule",
        "temporal_profile": "standing_support_packet_beta_rematch_temporal_profile",
    }
    for key, value in overrides.items():
        mapped[key_map[key]] = value
    return replace(base, **mapped)


def _write_tables(outdir: Path, points: pd.DataFrame, *, point_format: str) -> dict[str, Path]:
    summary, compact, stage, safety, decision = summarize(points)
    smeared_null = smeared_null_summary(points)
    point_suffix = "parquet" if point_format == "parquet" else "csv"
    files = {
        "point_ledger": outdir / f"source_ledger_point_ledger.{point_suffix}",
        "summary_long": outdir / "source_ledger_summary_long.csv",
        "global_compact": outdir / "source_ledger_global_compact.csv",
        "stage_summary": outdir / "source_ledger_stage_summary.csv",
        "safety": outdir / "source_ledger_safety.csv",
        "decision_table": outdir / "source_ledger_decision_table.csv",
        "top_bad_points": outdir / "source_ledger_top_bad_points.csv",
        "smeared_null": outdir / "source_ledger_smeared_null.csv",
    }
    write_table(points, files["point_ledger"])
    summary.to_csv(files["summary_long"], index=False)
    compact.to_csv(files["global_compact"], index=False)
    stage.to_csv(files["stage_summary"], index=False)
    safety.to_csv(files["safety"], index=False)
    decision.to_csv(files["decision_table"], index=False)
    top_bad_points(points).to_csv(files["top_bad_points"], index=False)
    smeared_null.to_csv(files["smeared_null"], index=False)
    return files


def _load_manifest(path: Path) -> tuple[SourceParams, dict[str, Any], str, str]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    raw_params = manifest.get("params", {})
    params = SourceParams(**{key: value for key, value in raw_params.items() if key in PARAM_KEYS})
    grid = dict(manifest["grid"])
    return params, grid, str(manifest.get("case", "manifest_case")), str(manifest.get("note", "manifest case"))


def _grid_from_args(base_grid: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    grid = dict(base_grid)
    for key in ["ns", "nl"]:
        value = getattr(args, key)
        if value is not None:
            grid[key] = int(value)
    for key in ["s_min", "s_max", "l_min", "l_max", "h_s", "h_l"]:
        value = getattr(args, key)
        if value is not None:
            grid[key] = float(value)
    return grid


def _summarize_candidate(label: str, params: SourceParams, ledger_dir: Path, points: pd.DataFrame) -> dict[str, Any]:
    live = points.loc[points["inside_packet_live"].astype(bool)].copy()
    packet_norm = pd.to_numeric(live["packet_norm"], errors="coerce") if len(live) else pd.Series(dtype=float)
    return {
        "label": label,
        "ledger_dir": str(ledger_dir),
        "beta_rematch_gain": float(params.standing_support_packet_beta_rematch_gain),
        "beta_rematch_shape": params.standing_support_packet_beta_rematch_shape,
        "beta_rematch_width_multiplier": float(params.standing_support_packet_beta_rematch_width_multiplier),
        "beta_rematch_temporal_width_multiplier": float(
            params.standing_support_packet_beta_rematch_temporal_width_multiplier
        ),
        "beta_rematch_center_floor": float(params.standing_support_packet_beta_rematch_center_floor),
        "positive_packet_norm_live": int((packet_norm > 0.0).sum()) if len(packet_norm) else 0,
        "max_packet_norm_live": float(packet_norm.max()) if len(packet_norm) else None,
        "rows": int(len(points)),
    }


def _compute_points(case: SourceCase, grid: dict[str, Any], args: argparse.Namespace) -> tuple[pd.DataFrame, dict[str, Any]]:
    jobs = int(args.jobs)
    if jobs < 1:
        raise ValueError(f"--jobs must be positive, got {jobs}")
    if jobs <= 1:
        points = compute_case(
            case,
            int(grid["ns"]),
            int(grid["nl"]),
            float(grid["s_min"]),
            float(grid["s_max"]),
            float(grid["l_min"]),
            float(grid["l_max"]),
            float(grid["h_s"]),
            float(grid["h_l"]),
            progress=not args.quiet,
        )
        return points, {"source_compute": "serial", "jobs": 1, "s_shards": 1}

    if args.point_format == "parquet" and args.stream_shards:
        shard_dir = args.current_ledger_dir / "source_ledger_point_ledger_shards"
        progress_log = args.current_ledger_dir / "source_ledger_shard_progress.jsonl"
        return compute_case_sharded_parquet(
            case,
            int(grid["ns"]),
            int(grid["nl"]),
            float(grid["s_min"]),
            float(grid["s_max"]),
            float(grid["l_min"]),
            float(grid["l_max"]),
            float(grid["h_s"]),
            float(grid["h_l"]),
            jobs=jobs,
            s_shards=args.s_shards,
            shard_dir=shard_dir,
            progress_log=progress_log,
            force=bool(args.force),
            progress=not args.quiet,
        )

    s_shards = resolve_s_shard_count(int(grid["ns"]), jobs, args.s_shards)
    points = compute_case_sharded(
        case,
        int(grid["ns"]),
        int(grid["nl"]),
        float(grid["s_min"]),
        float(grid["s_max"]),
        float(grid["l_min"]),
        float(grid["l_max"]),
        float(grid["h_s"]),
        float(grid["h_l"]),
        jobs=jobs,
        s_shards=s_shards,
        progress=not args.quiet,
    )
    return points, {"source_compute": "sharded", "jobs": jobs, "s_shards": s_shards}


def run(args: argparse.Namespace) -> dict[str, Path]:
    base_params, base_grid, base_case, base_note = _load_manifest(args.source_manifest)
    grid = _grid_from_args(base_grid, args)
    outdir = args.outdir
    ledger_root = outdir / "ledgers"
    ledger_root.mkdir(parents=True, exist_ok=True)
    candidates = [_parse_candidate(raw) for raw in args.candidate]
    rows: list[dict[str, Any]] = []
    for label, overrides in candidates:
        params = _apply_candidate(base_params, overrides)
        case = SourceCase(name=f"{base_case}_{label}", params=params, note=f"{base_note}; beta collar generator screen")
        ledger_dir = ledger_root / label
        ledger_dir.mkdir(parents=True, exist_ok=True)
        point_suffix = "parquet" if args.point_format == "parquet" else "csv"
        point_path = ledger_dir / f"source_ledger_point_ledger.{point_suffix}"
        if point_path.exists() and not args.force:
            points = read_table(point_path)
            cache_status = "reused"
            execution = {"source_compute": "cache_reused", "jobs": int(args.jobs), "s_shards": args.s_shards}
        else:
            args.current_ledger_dir = ledger_dir
            points, execution = _compute_points(case, grid, args)
            cache_status = "computed"
        files = _write_tables(ledger_dir, points, point_format=args.point_format)
        file_strings = {key: str(path) for key, path in files.items()}
        manifest = case_metadata(case, grid, file_strings)
        manifest.update({
            "source_manifest": str(args.source_manifest),
            "screen_label": args.label,
            "candidate_label": label,
            "cache_status": cache_status,
            "execution": execution,
            "rows": int(len(points)),
            "point_ledger_sha256": sha256_file(files["point_ledger"]),
            "caveat": "Tensor-consistent source-ledger regeneration with beta-rematch/collar parameters changed.",
        })
        write_manifest(ledger_dir / "source_ledger_manifest.json", manifest)
        row = _summarize_candidate(label, params, ledger_dir, points)
        row["cache_status"] = cache_status
        row.update(execution)
        rows.append(row)
        if args.progress:
            print(json.dumps({"event": "beta_collar_candidate_complete", **row}), flush=True)

    summary = pd.DataFrame(rows)
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary": outdir / "beta_collar_generator_summary.csv",
        "metadata": outdir / "beta_collar_generator_metadata.json",
    }
    summary.to_csv(paths["summary"], index=False)
    metadata = {
        "label": args.label,
        "source_manifest": str(args.source_manifest),
        "grid": grid,
        "candidates": args.candidate,
        "execution_request": {"jobs": int(args.jobs), "s_shards": args.s_shards},
        "rows": int(len(summary)),
        "files": {key: str(path) for key, path in paths.items() if key != "metadata"},
    }
    paths["metadata"].write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Regenerate manifest-based source ledgers with tensor-consistent beta-collar rematch variants."
    )
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--label", default="beta_collar_generator_screen")
    parser.add_argument(
        "--candidate",
        action="append",
        required=True,
        help=(
            "Candidate spec label:key=value,key=value. Keys: gain, shape, width, temporal, floor, "
            "floor_mode, inner, outer, edge, schedule, temporal_profile."
        ),
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--progress", action="store_true")
    parser.add_argument(
        "--point-format",
        choices=("csv", "parquet"),
        default="csv",
        help="Dense point-ledger storage format. Summary and decision sidecars remain CSV.",
    )
    parser.add_argument(
        "--stream-shards",
        action="store_true",
        help="For sharded Parquet runs, checkpoint each completed s-shard and write JSONL progress metadata.",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="Parallel worker processes for source-ledger point evaluation. The default serial path is 1.",
    )
    parser.add_argument(
        "--s-shards",
        type=int,
        default=None,
        help="Contiguous s-row shards for --jobs runs. Defaults to 4 * jobs, capped at ns.",
    )
    parser.add_argument("--ns", type=int, default=None)
    parser.add_argument("--nl", type=int, default=None)
    parser.add_argument("--s-min", type=float, default=None)
    parser.add_argument("--s-max", type=float, default=None)
    parser.add_argument("--l-min", type=float, default=None)
    parser.add_argument("--l-max", type=float, default=None)
    parser.add_argument("--h-s", type=float, default=None)
    parser.add_argument("--h-l", type=float, default=None)
    return parser


def main() -> int:
    run(build_parser().parse_args())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
