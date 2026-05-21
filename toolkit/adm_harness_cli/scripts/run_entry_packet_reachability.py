from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


CARRY_STAGES = {"held_carry", "release_shift_fade"}
SERVICE_STAGES = {"catch_rematch", "held_carry", "release_shift_fade"}
SUPPORT_PLANT_REGIONS = {"core_throat", "support_edge", "outer_quarantine_shell", "packet_in_support"}
MAIN_SUPPORT_REGIONS = {"core_throat", "support_edge", "packet_in_support"}


def _bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def _git_commit(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return None
    return result.stdout.strip() or None


def _load_metadata(path: Path) -> list[tuple[Path, str]]:
    data = json.loads(path.read_text())
    out: list[tuple[Path, str]] = []
    for item in data.get("point_ledgers", []):
        out.append((Path(item["path"]), str(item["label"])))
    return out


def _pivot_bool(frame: pd.DataFrame, s_vals: np.ndarray, l_vals: np.ndarray, column: str) -> np.ndarray:
    return (
        frame.pivot_table(index="s", columns="l", values=column, aggfunc="max")
        .reindex(index=s_vals, columns=l_vals)
        .fillna(False)
        .to_numpy(dtype=bool)
    )


def _pivot_float(frame: pd.DataFrame, s_vals: np.ndarray, l_vals: np.ndarray, column: str) -> np.ndarray:
    return (
        frame.pivot_table(index="s", columns="l", values=column, aggfunc="mean")
        .reindex(index=s_vals, columns=l_vals)
        .to_numpy(dtype=float)
    )


def _pivot_text(frame: pd.DataFrame, s_vals: np.ndarray, l_vals: np.ndarray, column: str) -> np.ndarray:
    if column not in frame:
        return np.full((len(s_vals), len(l_vals)), "", dtype=object)
    return (
        frame.pivot_table(index="s", columns="l", values=column, aggfunc=lambda values: str(values.iloc[0]))
        .reindex(index=s_vals, columns=l_vals)
        .fillna("")
        .to_numpy(dtype=object)
    )


def _interval_indices(l_vals: np.ndarray, lo: float, hi: float, *, nearest_fallback: bool) -> np.ndarray:
    indices = np.where((l_vals >= lo) & (l_vals <= hi))[0]
    if len(indices) == 0 and nearest_fallback:
        midpoint = 0.5 * (lo + hi)
        indices = np.array([int(np.argmin(np.abs(l_vals - midpoint)))])
    return indices


def _seed_indices_for_slice(
    *,
    regions: np.ndarray,
    l_vals: np.ndarray,
    row: int,
    entry_side: str,
    width: int,
    seed_mode: str,
) -> np.ndarray:
    if seed_mode == "domain_boundary":
        return np.arange(width) if entry_side == "lower" else np.arange(len(l_vals) - width, len(l_vals))

    region_set = SUPPORT_PLANT_REGIONS if seed_mode == "support_outer_edge" else MAIN_SUPPORT_REGIONS
    row_regions = np.asarray([str(value) for value in regions[row]], dtype=object)
    candidates = np.where(np.isin(row_regions, list(region_set)))[0]
    if len(candidates) == 0:
        return np.array([], dtype=int)
    if entry_side == "lower":
        edge = int(candidates.min())
        return np.arange(edge, min(edge + width, len(l_vals)))
    edge = int(candidates.max())
    return np.arange(max(0, edge - width + 1), edge + 1)


def _format_stage_counts(counts: pd.Series) -> str:
    if counts.empty:
        return ""
    return ";".join(f"{stage}:{int(count)}" for stage, count in counts.sort_index().items())


def _prepare_points(path: Path, label: str | None) -> pd.DataFrame:
    points = pd.read_csv(path)
    if label is not None and "label" in points.columns:
        points = points.loc[points["label"].astype(str).eq(str(label))].copy()
    if points.empty:
        raise ValueError(f"No rows loaded from {path} for label {label!r}")

    required = ["s", "l", "alpha", "beta", "gamma_ll"]
    missing = [column for column in required if column not in points.columns]
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")
    for column in required:
        points[column] = pd.to_numeric(points[column], errors="coerce")
    points = points.dropna(subset=required).copy()

    if "inside_packet_live" in points:
        points["inside_packet_live_bool"] = _bool_series(points["inside_packet_live"])
    elif "inside_packet_live_bool" in points:
        points["inside_packet_live_bool"] = _bool_series(points["inside_packet_live_bool"])
    else:
        points["inside_packet_live_bool"] = False

    if "plus_null_speed" not in points or "minus_null_speed" not in points:
        sqrt_gamma_ll = np.sqrt(points["gamma_ll"].astype(float))
        points["plus_null_speed"] = -points["beta"] + points["alpha"] / sqrt_gamma_ll
        points["minus_null_speed"] = -points["beta"] - points["alpha"] / sqrt_gamma_ll
    else:
        points["plus_null_speed"] = pd.to_numeric(points["plus_null_speed"], errors="coerce")
        points["minus_null_speed"] = pd.to_numeric(points["minus_null_speed"], errors="coerce")
    return points


def _run_case(
    *,
    points: pd.DataFrame,
    label: str,
    entry_side: str,
    entry_width: int,
    seed_mode: str,
    source_mode: str,
    nearest_fallback: bool,
) -> tuple[dict[str, Any], pd.DataFrame]:
    s_vals = np.array(sorted(points["s"].dropna().unique()), dtype=float)
    l_vals = np.array(sorted(points["l"].dropna().unique()), dtype=float)
    if len(s_vals) < 2 or len(l_vals) < 2:
        raise ValueError(f"{label}: need at least a 2x2 grid")

    v_plus = _pivot_float(points, s_vals, l_vals, "plus_null_speed")
    v_minus = _pivot_float(points, s_vals, l_vals, "minus_null_speed")
    packet = _pivot_bool(points, s_vals, l_vals, "inside_packet_live_bool")
    stages = _pivot_text(points, s_vals, l_vals, "stage")
    regions = _pivot_text(points, s_vals, l_vals, "region")

    reachable = np.zeros_like(packet, dtype=bool)
    width = max(1, min(int(entry_width), len(l_vals)))
    if source_mode == "initial_boundary":
        seeds = _seed_indices_for_slice(
            regions=regions,
            l_vals=l_vals,
            row=0,
            entry_side=entry_side,
            width=width,
            seed_mode=seed_mode,
        )
        reachable[0, seeds] = True

    hit_rows: list[dict[str, Any]] = []
    for i in range(len(s_vals) - 1):
        if source_mode == "persistent_boundary":
            seeds = _seed_indices_for_slice(
                regions=regions,
                l_vals=l_vals,
                row=i,
                entry_side=entry_side,
                width=width,
                seed_mode=seed_mode,
            )
            reachable[i, seeds] = True
        ds = float(s_vals[i + 1] - s_vals[i])
        if ds <= 0.0 or not math.isfinite(ds):
            continue

        for j in np.where(reachable[i])[0]:
            lo_speed = float(np.nanmin([v_minus[i, j], v_plus[i, j]]))
            hi_speed = float(np.nanmax([v_minus[i, j], v_plus[i, j]]))
            if not math.isfinite(lo_speed) or not math.isfinite(hi_speed):
                continue
            lo, hi = sorted([l_vals[j] + lo_speed * ds, l_vals[j] + hi_speed * ds])
            js = _interval_indices(l_vals, lo, hi, nearest_fallback=nearest_fallback)
            reachable[i + 1, js] = True

        hit_js = np.where(reachable[i + 1] & packet[i + 1])[0]
        for j in hit_js:
            hit_rows.append(
                {
                    "label": label,
                    "entry_side": entry_side,
                    "seed_mode": seed_mode,
                    "source_mode": source_mode,
                    "entry_width": width,
                    "s": float(s_vals[i + 1]),
                    "l": float(l_vals[j]),
                    "stage": str(stages[i + 1, j]),
                    "region": str(regions[i + 1, j]),
                    "v_plus": float(v_plus[i + 1, j]),
                    "v_minus": float(v_minus[i + 1, j]),
                }
            )

    hits = pd.DataFrame(hit_rows)
    hit_stages = hits["stage"].astype(str) if not hits.empty else pd.Series(dtype=str)
    packet_points = int(packet.sum())
    packet_slices = int(np.sum(packet.any(axis=1)))
    reachable_packet_mask = reachable & packet
    summary: dict[str, Any] = {
        "label": label,
        "entry_side": entry_side,
        "seed_mode": seed_mode,
        "source_mode": source_mode,
        "entry_width": width,
        "grid_s": int(len(s_vals)),
        "grid_l": int(len(l_vals)),
        "packet_points": packet_points,
        "packet_slices": packet_slices,
        "reachable_cells": int(reachable.sum()),
        "reachable_packet_points_final_mask": int(reachable_packet_mask.sum()),
        "reachable_packet_hits": int(len(hits)),
        "reachable_packet_hit_slices": int(hits["s"].nunique()) if not hits.empty else 0,
        "reachable_packet_hit_fraction": float(len(hits) / packet_points) if packet_points else 0.0,
        "service_stage_hits": int(hit_stages.isin(SERVICE_STAGES).sum()) if not hits.empty else 0,
        "carry_stage_hits": int(hit_stages.isin(CARRY_STAGES).sum()) if not hits.empty else 0,
        "hit_stage_counts": _format_stage_counts(hit_stages.value_counts()) if not hits.empty else "",
        "first_hit_s": float(hits["s"].min()) if not hits.empty else math.nan,
        "last_hit_s": float(hits["s"].max()) if not hits.empty else math.nan,
        "first_hit_stage": str(hits.sort_values("s").iloc[0]["stage"]) if not hits.empty else "",
        "last_hit_stage": str(hits.sort_values("s").iloc[-1]["stage"]) if not hits.empty else "",
        "first_hit_l": float(hits.sort_values("s").iloc[0]["l"]) if not hits.empty else math.nan,
        "last_hit_l": float(hits.sort_values("s").iloc[-1]["l"]) if not hits.empty else math.nan,
    }
    return summary, hits


def _markdown_report(summary: pd.DataFrame, args: argparse.Namespace) -> str:
    lines = [
        "# Entry-to-Packet Reachability",
        "",
        "## Purpose",
        "",
        "This diagnostic propagates a conservative 1+1 radial null reachability mask from a service-side boundary "
        "and records whether that mask intersects live packet cells in existing ADM point ledgers.",
        "",
        "## Settings",
        "",
        f"- source mode: `{args.source_mode}`",
        f"- seed mode: `{args.seed_mode}`",
        f"- entry width: `{args.entry_width}` grid column(s)",
        f"- nearest-cell fallback: `{not args.no_nearest_fallback}`",
        "",
        "## Summary",
        "",
    ]
    display_cols = [
        "label",
        "entry_side",
        "seed_mode",
        "reachable_packet_hits",
        "reachable_packet_hit_slices",
        "service_stage_hits",
        "carry_stage_hits",
        "first_hit_s",
        "last_hit_s",
        "hit_stage_counts",
    ]
    display = summary[display_cols].copy() if not summary.empty else pd.DataFrame(columns=display_cols)
    lines.append(display.to_markdown(index=False))
    lines.append("")
    lines.append("## Interpretation Limits")
    lines.append("")
    lines.append(
        "A hit is a sampled-ledger causal-reachability result, not a proof of a global horizon or a theorem-level "
        "GZ obstruction. A miss is likewise limited by grid extent and radial-only reduction. The diagnostic is "
        "intended to separate local branch-pinch signatures from live service-entry access to the carried packet."
    )
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a 1+1 radial entry-to-live-packet causal reachability test.")
    parser.add_argument("--point-ledger", type=Path, action="append", default=[])
    parser.add_argument("--label", action="append", default=[])
    parser.add_argument("--metadata", type=Path, action="append", default=[], help="GZ metadata JSON with point_ledgers.")
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--entry-side", choices=["lower", "upper"], action="append", default=None)
    parser.add_argument("--entry-width", type=int, default=1)
    parser.add_argument(
        "--seed-mode",
        choices=["domain_boundary", "support_outer_edge", "main_support_outer_edge"],
        default="domain_boundary",
        help="Where to inject the service-entry reachability mask on each side.",
    )
    parser.add_argument("--source-mode", choices=["persistent_boundary", "initial_boundary"], default="persistent_boundary")
    parser.add_argument("--no-nearest-fallback", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    cases: list[tuple[Path, str]] = []
    for metadata in args.metadata:
        cases.extend(_load_metadata(metadata))
    if len(args.point_ledger) != len(args.label):
        raise SystemExit("--point-ledger and --label counts must match")
    cases.extend(zip(args.point_ledger, args.label))
    if not cases:
        raise SystemExit("Provide --metadata or at least one --point-ledger/--label pair")

    entry_sides = args.entry_side or ["lower", "upper"]
    args.outdir.mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict[str, Any]] = []
    hit_frames: list[pd.DataFrame] = []
    for path, label in cases:
        points = _prepare_points(path, None)
        for entry_side in entry_sides:
            summary, hits = _run_case(
                points=points,
                label=label,
                entry_side=entry_side,
                entry_width=args.entry_width,
                seed_mode=args.seed_mode,
                source_mode=args.source_mode,
                nearest_fallback=not args.no_nearest_fallback,
            )
            summary["point_ledger"] = str(path)
            summary_rows.append(summary)
            if not hits.empty:
                hits["point_ledger"] = str(path)
                hit_frames.append(hits)
            print(json.dumps({k: summary[k] for k in [
                "label",
                "entry_side",
                "seed_mode",
                "reachable_packet_hits",
                "service_stage_hits",
                "carry_stage_hits",
            ]}), flush=True)

    summary_frame = pd.DataFrame(summary_rows)
    hits_frame = pd.concat(hit_frames, ignore_index=True) if hit_frames else pd.DataFrame()

    summary_path = args.outdir / "entry_packet_reachability_summary.csv"
    hits_path = args.outdir / "entry_packet_reachability_hits.csv"
    report_path = args.outdir / "entry_packet_reachability_report.md"
    metadata_path = args.outdir / "entry_packet_reachability_metadata.json"
    summary_frame.to_csv(summary_path, index=False)
    hits_frame.to_csv(hits_path, index=False)
    report_path.write_text(_markdown_report(summary_frame, args), encoding="utf-8")
    repo_root = Path(__file__).resolve().parents[3]
    metadata_path.write_text(
        json.dumps(
            {
                "cases": [{"path": str(path), "label": label} for path, label in cases],
                "entry_sides": entry_sides,
                "entry_width": args.entry_width,
                "seed_mode": args.seed_mode,
                "source_mode": args.source_mode,
                "nearest_fallback": not args.no_nearest_fallback,
                "commit": _git_commit(repo_root),
                "files": {
                    "summary": str(summary_path),
                    "hits": str(hits_path),
                    "report": str(report_path),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "outdir": str(args.outdir), "cases": len(cases)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
