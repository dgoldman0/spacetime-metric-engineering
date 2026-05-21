from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from run_trace_expansion_audit import (
    _build_expansion_grid,
    _git_commit,
    _prepare_points,
    _trace_seed,
)


WATCHED_CENTER_FAMILIES = {"radial_null_branch_band", "congruence_branch_band"}


def _bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def _finite_float(value: Any, default: float = math.nan) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def _center_families(raw: str) -> set[str]:
    families = {item.strip() for item in raw.split(",") if item.strip()}
    return families or set(WATCHED_CENTER_FAMILIES)


def _select_centers(
    traces: pd.DataFrame,
    *,
    top_centers: int,
    center_families: set[str],
    require_both_shrinking: bool,
) -> pd.DataFrame:
    required = [
        "probe_family",
        "branch",
        "seed_index",
        "seed_s",
        "seed_l",
        "integrated_trapped_like_strength",
        "both_shrinking_samples",
        "longest_both_shrinking_run",
    ]
    missing = [column for column in required if column not in traces.columns]
    if missing:
        raise ValueError(f"trace audit table is missing required columns: {missing}")

    candidates = traces.loc[
        traces["probe_family"].astype(str).isin(center_families)
        & traces["branch"].astype(str).eq("minus")
    ].copy()
    if require_both_shrinking and "entered_both_shrinking" in candidates:
        entered = _bool_series(candidates["entered_both_shrinking"])
        candidates = candidates.loc[entered].copy()
    if candidates.empty:
        raise ValueError("no minus-branch branch-band centers were available for dense congruence audit")

    for column in [
        "seed_index",
        "seed_s",
        "seed_l",
        "integrated_trapped_like_strength",
        "both_shrinking_samples",
        "longest_both_shrinking_run",
        "integrated_negative_branch_expansion",
        "min_branch_theta",
    ]:
        if column in candidates:
            candidates[column] = pd.to_numeric(candidates[column], errors="coerce")

    candidates = candidates.sort_values(
        [
            "integrated_trapped_like_strength",
            "both_shrinking_samples",
            "longest_both_shrinking_run",
            "integrated_negative_branch_expansion",
        ],
        ascending=[False, False, False, False],
        na_position="last",
    )
    candidates = candidates.drop_duplicates(subset=["seed_s", "seed_l"]).head(max(1, top_centers))
    candidates = candidates.reset_index(drop=True).copy()
    candidates["center_id"] = [f"center_{index:02d}" for index in range(len(candidates))]
    return candidates


def _dense_offsets(rays_per_bundle: int, half_width_steps: float) -> np.ndarray:
    rays = max(3, int(rays_per_bundle))
    if rays % 2 == 0:
        rays += 1
    return np.linspace(-float(half_width_steps), float(half_width_steps), rays)


def _grid_step_l(grid: Any) -> float:
    return float(np.median(np.diff(grid.l_axis))) if len(grid.l_axis) > 1 else 1.0


def _build_dense_seeds(
    centers: pd.DataFrame,
    grid: Any,
    *,
    rays_per_bundle: int,
    half_width_steps: float,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    offsets = _dense_offsets(rays_per_bundle, half_width_steps)
    step_l = _grid_step_l(grid)
    for center_number, center in centers.iterrows():
        center_id = str(center["center_id"])
        center_s = float(center["seed_s"])
        center_l = float(center["seed_l"])
        bundle_id = f"{center_id}_minus_dense"
        for ray_index, offset_steps in enumerate(offsets):
            seed_l = float(np.clip(center_l + float(offset_steps) * step_l, grid.l_axis[0], grid.l_axis[-1]))
            rows.append({
                "seed_index": len(rows),
                "probe_family": "dense_congruence_caustic",
                "branch": "minus",
                "seed_s": center_s,
                "seed_l": seed_l,
                "seed_stage": str(center.get("seed_stage", "")),
                "seed_region": str(center.get("seed_region", "")),
                "seed_inside_packet_live": bool(grid.interp("inside_packet_live", center_s, seed_l) >= 0.5),
                "seed_inside_packet_geom": bool(grid.interp("inside_packet_geom", center_s, seed_l) >= 0.5),
                "angular_fraction": 0.0,
                "bundle_id": bundle_id,
                "center_id": center_id,
                "center_rank": int(center_number),
                "center_s": center_s,
                "center_l": center_l,
                "ray_index": int(ray_index),
                "offset_steps": float(offset_steps),
                "source_probe_family": str(center["probe_family"]),
                "source_seed_index": int(center["seed_index"]),
                "source_integrated_trapped_like_strength": _finite_float(
                    center.get("integrated_trapped_like_strength")
                ),
                "source_both_shrinking_samples": int(_finite_float(center.get("both_shrinking_samples"), 0.0)),
                "source_longest_both_shrinking_run": int(_finite_float(center.get("longest_both_shrinking_run"), 0.0)),
            })
    seeds = pd.DataFrame(rows).drop_duplicates(subset=["bundle_id", "seed_s", "seed_l", "ray_index"]).copy()
    seeds["seed_index"] = range(len(seeds))
    return seeds


def _trace_dense_seeds(
    grid: Any,
    seeds: pd.DataFrame,
    *,
    trace_step_scale: float,
    max_steps: int,
    theta_eps: float,
    sample_stride: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    trace_rows: list[dict[str, Any]] = []
    sample_rows: list[dict[str, Any]] = []
    metadata_by_seed = seeds.set_index("seed_index").to_dict(orient="index")
    for _, seed in seeds.iterrows():
        trace, samples = _trace_seed(
            grid,
            seed,
            step_scale=float(trace_step_scale),
            max_steps=int(max_steps),
            theta_eps=float(theta_eps),
        )
        metadata = metadata_by_seed[int(seed["seed_index"])]
        extra = {
            "bundle_id": str(metadata["bundle_id"]),
            "center_id": str(metadata["center_id"]),
            "center_rank": int(metadata["center_rank"]),
            "center_s": float(metadata["center_s"]),
            "center_l": float(metadata["center_l"]),
            "ray_index": int(metadata["ray_index"]),
            "offset_steps": float(metadata["offset_steps"]),
            "source_probe_family": str(metadata["source_probe_family"]),
            "source_seed_index": int(metadata["source_seed_index"]),
            "source_integrated_trapped_like_strength": float(metadata["source_integrated_trapped_like_strength"]),
            "source_both_shrinking_samples": int(metadata["source_both_shrinking_samples"]),
            "source_longest_both_shrinking_run": int(metadata["source_longest_both_shrinking_run"]),
        }
        trace.update(extra)
        trace_rows.append(trace)
        stride = max(1, int(sample_stride))
        for sample in samples[::stride]:
            sample.update(extra)
            sample["radius"] = grid.interp("radius", float(sample["s"]), float(sample["l"]))
            sample_rows.append(sample)
    return pd.DataFrame(trace_rows), pd.DataFrame(sample_rows)


def _initial_bundle_widths(seeds: pd.DataFrame, grid: Any) -> dict[str, dict[str, float]]:
    widths: dict[str, dict[str, float]] = {}
    for bundle_id, group in seeds.groupby("bundle_id", sort=False):
        ordered = group.sort_values("ray_index")
        l_values = ordered["seed_l"].to_numpy(dtype=float)
        radii = np.array([grid.interp("radius", float(row.seed_s), float(row.seed_l)) for row in ordered.itertuples()])
        l_gaps = np.diff(l_values)
        radius_gaps = np.diff(radii)
        widths[str(bundle_id)] = {
            "initial_l_width": float(np.nanmax(l_values) - np.nanmin(l_values)),
            "initial_radius_width": float(np.nanmax(radii) - np.nanmin(radii)),
            "initial_min_l_gap": float(np.nanmin(l_gaps)) if len(l_gaps) else math.nan,
            "initial_min_radius_gap": float(np.nanmin(radius_gaps)) if len(radius_gaps) else math.nan,
        }
    return widths


def _bundle_evolution(samples: pd.DataFrame, seeds: pd.DataFrame, grid: Any) -> pd.DataFrame:
    if samples.empty:
        return pd.DataFrame()
    widths = _initial_bundle_widths(seeds, grid)
    rows: list[dict[str, Any]] = []
    rays_per_bundle = seeds.groupby("bundle_id")["seed_index"].nunique().to_dict()
    for (bundle_id, sample_index), group in samples.groupby(["bundle_id", "sample_index"], sort=False):
        expected = int(rays_per_bundle.get(bundle_id, 0))
        if expected <= 0 or len(group) != expected:
            continue
        ordered = group.sort_values("ray_index")
        l_values = ordered["l"].to_numpy(dtype=float)
        radii = ordered["radius"].to_numpy(dtype=float)
        l_gaps = np.diff(l_values)
        radius_gaps = np.diff(radii)
        initial = widths[str(bundle_id)]
        l_width = float(np.nanmax(l_values) - np.nanmin(l_values))
        radius_width = float(np.nanmax(radii) - np.nanmin(radii))
        min_l_gap = float(np.nanmin(l_gaps)) if len(l_gaps) else math.nan
        min_radius_gap = float(np.nanmin(radius_gaps)) if len(radius_gaps) else math.nan
        initial_l_width = initial["initial_l_width"]
        initial_radius_width = initial["initial_radius_width"]
        initial_min_l_gap = initial["initial_min_l_gap"]
        initial_min_radius_gap = initial["initial_min_radius_gap"]
        rows.append({
            "bundle_id": str(bundle_id),
            "center_id": str(ordered["center_id"].iloc[0]),
            "sample_index": int(sample_index),
            "s": float(ordered["s"].mean()),
            "active_rays": int(len(ordered)),
            "l_width": l_width,
            "radius_width": radius_width,
            "l_width_ratio": l_width / initial_l_width if initial_l_width > 0.0 else math.nan,
            "radius_width_ratio": radius_width / initial_radius_width if initial_radius_width > 0.0 else math.nan,
            "min_adjacent_l_gap": min_l_gap,
            "min_adjacent_radius_gap": min_radius_gap,
            "min_adjacent_l_gap_ratio": (
                min_l_gap / initial_min_l_gap if initial_min_l_gap > 0.0 else math.nan
            ),
            "min_adjacent_radius_gap_ratio": (
                min_radius_gap / initial_min_radius_gap if initial_min_radius_gap > 0.0 else math.nan
            ),
            "ordering_crossed": bool(np.any(l_gaps <= 0.0)) if len(l_gaps) else False,
            "both_shrinking_rays": int(ordered["expansion_class"].eq("both_shrinking").sum()),
            "both_shrinking_fraction": float(ordered["expansion_class"].eq("both_shrinking").mean()),
            "mean_trapped_like_strength": float(ordered["trapped_like_strength"].mean()),
            "max_trapped_like_strength": float(ordered["trapped_like_strength"].max()),
            "min_branch_theta": float(ordered["branch_theta"].min()),
            "max_branch_theta": float(ordered["branch_theta"].max()),
            "mean_branch_theta": float(ordered["branch_theta"].mean()),
            "inside_packet_live_fraction": float(ordered["inside_packet_live"].mean()),
        })
    return pd.DataFrame(rows)


def _bundle_summary(
    traces: pd.DataFrame,
    evolution: pd.DataFrame,
    seeds: pd.DataFrame,
    grid: Any,
    *,
    width_collapse_ratio: float,
    adjacent_collapse_ratio: float,
) -> pd.DataFrame:
    widths = _initial_bundle_widths(seeds, grid)
    rows: list[dict[str, Any]] = []
    for bundle_id, group in traces.groupby("bundle_id", sort=False):
        bundle_evolution = evolution.loc[evolution["bundle_id"].eq(bundle_id)].copy() if not evolution.empty else pd.DataFrame()
        all_both_evolution = (
            bundle_evolution.loc[bundle_evolution["both_shrinking_fraction"].eq(1.0)].copy()
            if not bundle_evolution.empty
            else pd.DataFrame()
        )
        live_evolution = (
            bundle_evolution.loc[bundle_evolution["inside_packet_live_fraction"].gt(0.0)].copy()
            if not bundle_evolution.empty
            else pd.DataFrame()
        )
        min_l_width_ratio = float(bundle_evolution["l_width_ratio"].min()) if not bundle_evolution.empty else math.nan
        min_radius_width_ratio = (
            float(bundle_evolution["radius_width_ratio"].min()) if not bundle_evolution.empty else math.nan
        )
        min_adjacent_l_gap_ratio = (
            float(bundle_evolution["min_adjacent_l_gap_ratio"].min()) if not bundle_evolution.empty else math.nan
        )
        min_adjacent_radius_gap_ratio = (
            float(bundle_evolution["min_adjacent_radius_gap_ratio"].min()) if not bundle_evolution.empty else math.nan
        )
        crossing_samples = int(bundle_evolution["ordering_crossed"].sum()) if not bundle_evolution.empty else 0
        caustic_like = bool(
            crossing_samples > 0
            or (math.isfinite(min_l_width_ratio) and min_l_width_ratio <= width_collapse_ratio)
            or (math.isfinite(min_radius_width_ratio) and min_radius_width_ratio <= width_collapse_ratio)
            or (math.isfinite(min_adjacent_l_gap_ratio) and min_adjacent_l_gap_ratio <= adjacent_collapse_ratio)
            or (
                math.isfinite(min_adjacent_radius_gap_ratio)
                and min_adjacent_radius_gap_ratio <= adjacent_collapse_ratio
            )
        )
        entered_count = int(group["entered_both_shrinking"].sum())
        recovered_count = int(group["recovered_from_both_shrinking"].sum())
        sustained_count = int(group["sustained_both_shrinking_to_end"].sum())
        rows.append({
            "bundle_id": str(bundle_id),
            "center_id": str(group["center_id"].iloc[0]),
            "source_probe_family": str(group["source_probe_family"].iloc[0]),
            "source_seed_index": int(group["source_seed_index"].iloc[0]),
            "center_s": float(group["center_s"].iloc[0]),
            "center_l": float(group["center_l"].iloc[0]),
            "rays": int(len(group)),
            "radial_escape_count": int(group["trace_outcome"].isin(["l_lower_boundary", "l_upper_boundary"]).sum()),
            "l_lower_boundary_count": int(group["trace_outcome"].eq("l_lower_boundary").sum()),
            "s_upper_boundary_count": int(group["trace_outcome"].eq("s_upper_boundary").sum()),
            "invalid_metric_count": int(group["trace_outcome"].eq("invalid_metric").sum()),
            "entered_both_shrinking_count": entered_count,
            "recovered_from_both_shrinking_count": recovered_count,
            "sustained_both_shrinking_to_end_count": sustained_count,
            "initial_l_width": widths[str(bundle_id)]["initial_l_width"],
            "initial_radius_width": widths[str(bundle_id)]["initial_radius_width"],
            "common_samples": int(len(bundle_evolution)),
            "min_common_l_width_ratio": min_l_width_ratio,
            "min_common_radius_width_ratio": min_radius_width_ratio,
            "min_common_adjacent_l_gap_ratio": min_adjacent_l_gap_ratio,
            "min_common_adjacent_radius_gap_ratio": min_adjacent_radius_gap_ratio,
            "min_all_both_l_width_ratio": (
                float(all_both_evolution["l_width_ratio"].min()) if not all_both_evolution.empty else math.nan
            ),
            "min_all_both_radius_width_ratio": (
                float(all_both_evolution["radius_width_ratio"].min()) if not all_both_evolution.empty else math.nan
            ),
            "min_all_both_adjacent_l_gap_ratio": (
                float(all_both_evolution["min_adjacent_l_gap_ratio"].min())
                if not all_both_evolution.empty
                else math.nan
            ),
            "min_live_l_width_ratio": (
                float(live_evolution["l_width_ratio"].min()) if not live_evolution.empty else math.nan
            ),
            "min_live_radius_width_ratio": (
                float(live_evolution["radius_width_ratio"].min()) if not live_evolution.empty else math.nan
            ),
            "min_live_adjacent_l_gap_ratio": (
                float(live_evolution["min_adjacent_l_gap_ratio"].min()) if not live_evolution.empty else math.nan
            ),
            "crossing_samples": crossing_samples,
            "caustic_like_collapse": caustic_like,
            "max_bundle_both_shrinking_fraction": (
                float(bundle_evolution["both_shrinking_fraction"].max()) if not bundle_evolution.empty else math.nan
            ),
            "max_mean_trapped_like_strength": (
                float(bundle_evolution["mean_trapped_like_strength"].max()) if not bundle_evolution.empty else math.nan
            ),
            "max_integrated_trapped_like_strength": float(group["integrated_trapped_like_strength"].max()),
            "mean_integrated_trapped_like_strength": float(group["integrated_trapped_like_strength"].mean()),
            "max_longest_both_shrinking_run": int(group["longest_both_shrinking_run"].max()),
            "min_branch_theta": float(group["min_branch_theta"].min()),
            "max_branch_theta": float(group["max_branch_theta"].max()),
            "outcome_counts": ";".join(
                f"{name}:{int(count)}" for name, count in group["trace_outcome"].value_counts().sort_index().items()
            ),
        })
    return pd.DataFrame(rows)


def _decision(summary: pd.DataFrame) -> str:
    if summary.empty:
        return "undecidable_no_dense_bundles"
    if bool(summary["caustic_like_collapse"].any()):
        return "adverse_caustic_like_compression_with_later_escape"
    if int(summary["sustained_both_shrinking_to_end_count"].sum()) > 0:
        return "adverse_dense_bundle_sustained_focusing"
    entered = int(summary["entered_both_shrinking_count"].sum())
    recovered = int(summary["recovered_from_both_shrinking_count"].sum())
    radial = int(summary["radial_escape_count"].sum())
    rays = int(summary["rays"].sum())
    if entered > 0 and recovered == entered and radial == rays:
        return "favorable_dense_bundle_transient_focusing"
    if radial == rays and entered == 0:
        return "favorable_dense_bundle_no_focusing"
    return "mixed_dense_bundle_focusing"


def _markdown_report(args: argparse.Namespace, summary: pd.DataFrame, centers: pd.DataFrame, decision: str) -> str:
    lines = [
        "# Dense Congruence Caustic Audit",
        "",
        "## Purpose",
        "",
        "This diagnostic fans the strongest recovered minus-branch branch-band traces into dense fixed-time l-bundles.",
        "It asks whether nearby rays keep bounded width and separation while crossing the local both-null-focusing patch.",
        "",
        "## Settings",
        "",
        f"- point ledger: `{args.point_ledger}`",
        f"- trace audit traces: `{args.trace_traces}`",
        f"- label: `{args.label}`",
        f"- top centers: `{args.top_centers}`",
        f"- rays per bundle: `{_dense_offsets(args.rays_per_bundle, args.half_width_steps).size}`",
        f"- half width: `{args.half_width_steps}` grid steps",
        f"- theta epsilon: `{args.theta_eps}`",
        f"- trace step scale: `{args.trace_step_scale}`",
        f"- width collapse ratio: `{args.width_collapse_ratio}`",
        f"- adjacent collapse ratio: `{args.adjacent_collapse_ratio}`",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Selected Centers",
        "",
    ]
    center_cols = [
        "center_id",
        "probe_family",
        "seed_index",
        "seed_s",
        "seed_l",
        "integrated_trapped_like_strength",
        "both_shrinking_samples",
        "longest_both_shrinking_run",
        "trace_outcome",
    ]
    available_center_cols = [column for column in center_cols if column in centers.columns]
    lines.append(centers[available_center_cols].to_markdown(index=False) if not centers.empty else "_No centers selected._")
    lines.extend([
        "",
        "## Bundle Summary",
        "",
    ])
    summary_cols = [
        "bundle_id",
        "source_probe_family",
        "center_s",
        "center_l",
        "rays",
        "radial_escape_count",
        "entered_both_shrinking_count",
        "recovered_from_both_shrinking_count",
        "sustained_both_shrinking_to_end_count",
        "min_common_l_width_ratio",
        "min_common_radius_width_ratio",
        "min_common_adjacent_l_gap_ratio",
        "min_all_both_l_width_ratio",
        "min_all_both_radius_width_ratio",
        "min_live_l_width_ratio",
        "crossing_samples",
        "caustic_like_collapse",
        "max_integrated_trapped_like_strength",
        "max_longest_both_shrinking_run",
        "outcome_counts",
    ]
    available_summary_cols = [column for column in summary_cols if column in summary.columns]
    lines.append(summary[available_summary_cols].to_markdown(index=False) if not summary.empty else "_No bundle summary._")
    lines.extend([
        "",
        "## Caveat",
        "",
        "This is a prescribed-metric congruence proxy. It tests ray-bundle width, ordering, and sampled expansion recovery; it is not a caustic theorem or dynamical matter evolution.",
    ])
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace) -> dict[str, Path]:
    points = _prepare_points(args.point_ledger)
    grid = _build_expansion_grid(points)
    prior_traces = pd.read_csv(args.trace_traces)
    centers = _select_centers(
        prior_traces,
        top_centers=int(args.top_centers),
        center_families=_center_families(args.center_families),
        require_both_shrinking=bool(args.require_both_shrinking),
    )
    seeds = _build_dense_seeds(
        centers,
        grid,
        rays_per_bundle=int(args.rays_per_bundle),
        half_width_steps=float(args.half_width_steps),
    )
    traces, samples = _trace_dense_seeds(
        grid,
        seeds,
        trace_step_scale=float(args.trace_step_scale),
        max_steps=int(args.max_steps),
        theta_eps=float(args.theta_eps),
        sample_stride=int(args.sample_stride),
    )
    evolution = _bundle_evolution(samples, seeds, grid)
    summary = _bundle_summary(
        traces,
        evolution,
        seeds,
        grid,
        width_collapse_ratio=float(args.width_collapse_ratio),
        adjacent_collapse_ratio=float(args.adjacent_collapse_ratio),
    )
    decision = _decision(summary)

    args.outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "centers": args.outdir / "dense_congruence_caustic_centers.csv",
        "seeds": args.outdir / "dense_congruence_caustic_seeds.csv",
        "traces": args.outdir / "dense_congruence_caustic_traces.csv",
        "samples": args.outdir / "dense_congruence_caustic_samples.csv",
        "evolution": args.outdir / "dense_congruence_caustic_bundle_evolution.csv",
        "summary": args.outdir / "dense_congruence_caustic_summary.csv",
        "report": args.outdir / "dense_congruence_caustic_report.md",
        "metadata": args.outdir / "dense_congruence_caustic_metadata.json",
    }
    centers.to_csv(paths["centers"], index=False)
    seeds.to_csv(paths["seeds"], index=False)
    traces.to_csv(paths["traces"], index=False)
    samples.to_csv(paths["samples"], index=False)
    evolution.to_csv(paths["evolution"], index=False)
    summary.to_csv(paths["summary"], index=False)
    paths["report"].write_text(_markdown_report(args, summary, centers, decision), encoding="utf-8")
    metadata = {
        "label": args.label,
        "point_ledger": str(args.point_ledger),
        "trace_traces": str(args.trace_traces),
        "repo_commit": _git_commit(Path.cwd()),
        "center_families": sorted(_center_families(args.center_families)),
        "top_centers": int(args.top_centers),
        "rays_per_bundle": int(_dense_offsets(args.rays_per_bundle, args.half_width_steps).size),
        "half_width_steps": float(args.half_width_steps),
        "theta_eps": float(args.theta_eps),
        "trace_step_scale": float(args.trace_step_scale),
        "max_steps": int(args.max_steps),
        "sample_stride": int(args.sample_stride),
        "width_collapse_ratio": float(args.width_collapse_ratio),
        "adjacent_collapse_ratio": float(args.adjacent_collapse_ratio),
        "decision": decision,
        "rows": {
            "centers": int(len(centers)),
            "seeds": int(len(seeds)),
            "traces": int(len(traces)),
            "samples": int(len(samples)),
            "evolution": int(len(evolution)),
            "summary": int(len(summary)),
        },
        "files": {key: str(path) for key, path in paths.items() if key != "metadata"},
        "caveat": "Prescribed-metric dense congruence caustic proxy; not a full caustic theorem or matter evolution.",
    }
    paths["metadata"].write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    if args.progress:
        print(json.dumps({
            "event": "dense_congruence_caustic_audit_complete",
            "label": args.label,
            "decision": decision,
            "centers": int(len(centers)),
            "traces": int(len(traces)),
            "outdir": str(args.outdir),
        }), flush=True)
        display_cols = [
            "bundle_id",
            "rays",
            "radial_escape_count",
            "entered_both_shrinking_count",
            "recovered_from_both_shrinking_count",
            "sustained_both_shrinking_to_end_count",
            "min_common_l_width_ratio",
            "min_common_radius_width_ratio",
            "min_common_adjacent_l_gap_ratio",
            "min_all_both_l_width_ratio",
            "min_all_both_radius_width_ratio",
            "min_live_l_width_ratio",
            "crossing_samples",
            "caustic_like_collapse",
            "max_integrated_trapped_like_strength",
            "outcome_counts",
        ]
        print(summary[display_cols].to_string(index=False), flush=True)
    return paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a dense congruence width/caustic proxy around strong minus-branch branch-band seeds."
    )
    parser.add_argument("--point-ledger", type=Path, required=True)
    parser.add_argument("--trace-traces", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--label", default="dense_congruence_caustic")
    parser.add_argument("--top-centers", type=int, default=8)
    parser.add_argument("--center-families", default="radial_null_branch_band,congruence_branch_band")
    parser.add_argument("--require-both-shrinking", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--rays-per-bundle", type=int, default=17)
    parser.add_argument("--half-width-steps", type=float, default=2.0)
    parser.add_argument("--theta-eps", type=float, default=1.0e-6)
    parser.add_argument("--trace-step-scale", type=float, default=0.5)
    parser.add_argument("--max-steps", type=int, default=12000)
    parser.add_argument("--sample-stride", type=int, default=1)
    parser.add_argument("--width-collapse-ratio", type=float, default=0.10)
    parser.add_argument("--adjacent-collapse-ratio", type=float, default=0.05)
    parser.add_argument("--progress", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
