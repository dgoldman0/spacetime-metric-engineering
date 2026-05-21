from __future__ import annotations

import argparse
import json
import math
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SERVICE_STAGES = {"catch_rematch", "held_carry", "release_shift_fade"}
CARRY_STAGES = {"held_carry", "release_shift_fade"}
SUPPORT_PLANT_REGIONS = {"core_throat", "support_edge", "outer_quarantine_shell", "packet_in_support"}
MAIN_CARRIER_REGIONS = {"core_throat", "support_edge", "packet_in_support"}
DEFAULT_SEED_SCOPES = [
    "packet_live",
    "packet_geom",
    "main_carrier",
    "support_plant",
    "branch_band_live",
    "post_release_packet",
    "post_release_carrier",
    "lower_boundary",
    "upper_boundary",
]


def _bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def _as_float(frame: pd.DataFrame, column: str, default: float = math.nan) -> pd.Series:
    if column not in frame:
        return pd.Series(default, index=frame.index, dtype=float)
    return pd.to_numeric(frame[column], errors="coerce").astype(float)


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
    return [(Path(item["path"]), str(item["label"])) for item in data.get("point_ledgers", [])]


def _pivot_float(frame: pd.DataFrame, s_axis: np.ndarray, l_axis: np.ndarray, column: str) -> np.ndarray:
    return (
        frame.pivot_table(index="s", columns="l", values=column, aggfunc="mean")
        .reindex(index=s_axis, columns=l_axis)
        .to_numpy(dtype=float)
    )


def _pivot_text(frame: pd.DataFrame, s_axis: np.ndarray, l_axis: np.ndarray, column: str) -> np.ndarray:
    if column not in frame:
        return np.full((len(s_axis), len(l_axis)), "", dtype=object)
    return (
        frame.pivot_table(index="s", columns="l", values=column, aggfunc=lambda values: str(values.iloc[0]))
        .reindex(index=s_axis, columns=l_axis)
        .fillna("")
        .to_numpy(dtype=object)
    )


@dataclass
class HorizonGrid:
    s_axis: np.ndarray
    l_axis: np.ndarray
    arrays: dict[str, np.ndarray]
    stage: np.ndarray
    region: np.ndarray

    @property
    def step_s(self) -> float:
        return float(np.median(np.diff(self.s_axis))) if len(self.s_axis) > 1 else 1.0

    def in_bounds(self, s_value: float, l_value: float) -> bool:
        return (
            self.s_axis[0] <= s_value <= self.s_axis[-1]
            and self.l_axis[0] <= l_value <= self.l_axis[-1]
        )

    def interp(self, key: str, s_value: float, l_value: float) -> float:
        if key not in self.arrays or not self.in_bounds(s_value, l_value):
            return math.nan
        s_hi = int(np.searchsorted(self.s_axis, s_value, side="right"))
        l_hi = int(np.searchsorted(self.l_axis, l_value, side="right"))
        s_hi = min(max(s_hi, 1), len(self.s_axis) - 1)
        l_hi = min(max(l_hi, 1), len(self.l_axis) - 1)
        s_lo = s_hi - 1
        l_lo = l_hi - 1
        s0 = self.s_axis[s_lo]
        s1 = self.s_axis[s_hi]
        l0 = self.l_axis[l_lo]
        l1 = self.l_axis[l_hi]
        if s1 == s0 or l1 == l0:
            return math.nan
        ws = (s_value - s0) / (s1 - s0)
        wl = (l_value - l0) / (l1 - l0)
        arr = self.arrays[key]
        values = [arr[s_lo, l_lo], arr[s_lo, l_hi], arr[s_hi, l_lo], arr[s_hi, l_hi]]
        if not all(math.isfinite(float(value)) for value in values):
            return math.nan
        return float(
            (1.0 - ws) * (1.0 - wl) * values[0]
            + (1.0 - ws) * wl * values[1]
            + ws * (1.0 - wl) * values[2]
            + ws * wl * values[3]
        )

    def nearest_text(self, values: np.ndarray, s_value: float, l_value: float) -> str:
        s_index = int(np.argmin(np.abs(self.s_axis - s_value)))
        l_index = int(np.argmin(np.abs(self.l_axis - l_value)))
        return str(values[s_index, l_index])


def _prepare_points(path: Path, label_filter: str | None = None) -> pd.DataFrame:
    points = pd.read_csv(path)
    if label_filter is not None and "label" in points.columns:
        points = points.loc[points["label"].astype(str).eq(str(label_filter))].copy()
    if points.empty:
        raise ValueError(f"No rows loaded from {path} for label filter {label_filter!r}")

    required = ["s", "l", "alpha", "beta", "gamma_ll"]
    missing = [column for column in required if column not in points.columns]
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")
    for column in required:
        points[column] = pd.to_numeric(points[column], errors="coerce")
    points = points.dropna(subset=required).copy()
    points["stage"] = points["stage"].astype(str) if "stage" in points else ""
    points["region"] = points["region"].astype(str) if "region" in points else ""

    points["inside_packet_live_bool"] = (
        _bool_series(points["inside_packet_live"]) if "inside_packet_live" in points else False
    )
    points["inside_packet_geom_bool"] = (
        _bool_series(points["inside_packet_geom"]) if "inside_packet_geom" in points else False
    )
    sqrt_gamma_ll = np.sqrt(np.maximum(points["gamma_ll"].to_numpy(dtype=float), 0.0))
    alpha = points["alpha"].to_numpy(dtype=float)
    beta = points["beta"].to_numpy(dtype=float)
    points["plus_null_speed"] = -beta + alpha / sqrt_gamma_ll
    points["minus_null_speed"] = -beta - alpha / sqrt_gamma_ll
    points["branch_abs_margin"] = np.minimum(
        points["plus_null_speed"].abs(),
        points["minus_null_speed"].abs(),
    )
    points["g_sigma_sigma"] = -points["alpha"] * points["alpha"] + points["gamma_ll"] * points["beta"] * points["beta"]
    points["gtt"] = _as_float(points, "gtt").fillna(points["g_sigma_sigma"])
    points["cond_metric"] = _as_float(points, "cond_metric")
    points["ricci_scalar"] = _as_float(points, "ricci_scalar")
    points["support_plant_bool"] = points["region"].isin(SUPPORT_PLANT_REGIONS)
    points["main_carrier_bool"] = points["region"].isin(MAIN_CARRIER_REGIONS)
    points["service_stage_bool"] = points["stage"].isin(SERVICE_STAGES)
    points["carry_stage_bool"] = points["stage"].isin(CARRY_STAGES)
    points["post_release_bool"] = points["stage"].eq("post_release_buffer")
    return points


def _build_grid(points: pd.DataFrame) -> HorizonGrid:
    s_axis = np.array(sorted(points["s"].dropna().unique()), dtype=float)
    l_axis = np.array(sorted(points["l"].dropna().unique()), dtype=float)
    if len(s_axis) < 2 or len(l_axis) < 2:
        raise ValueError("horizon escape ladder requires at least a 2x2 grid")
    arrays = {
        column: _pivot_float(points, s_axis, l_axis, column)
        for column in ["plus_null_speed", "minus_null_speed", "branch_abs_margin", "gtt", "cond_metric", "ricci_scalar"]
    }
    return HorizonGrid(
        s_axis=s_axis,
        l_axis=l_axis,
        arrays=arrays,
        stage=_pivot_text(points, s_axis, l_axis, "stage"),
        region=_pivot_text(points, s_axis, l_axis, "region"),
    )


def _scope_mask(points: pd.DataFrame, scope: str, boundary_width: int) -> pd.Series:
    l_values = np.array(sorted(points["l"].dropna().unique()), dtype=float)
    width = max(1, min(int(boundary_width), len(l_values)))
    if scope == "packet_live":
        return points["inside_packet_live_bool"]
    if scope == "packet_geom":
        return points["inside_packet_geom_bool"]
    if scope == "main_carrier":
        return points["main_carrier_bool"]
    if scope == "support_plant":
        return points["support_plant_bool"]
    if scope == "branch_band_live":
        live = points.loc[points["inside_packet_live_bool"], "branch_abs_margin"]
        if live.empty:
            return pd.Series(False, index=points.index)
        cutoff = float(live.quantile(0.20))
        return points["inside_packet_live_bool"] & (points["branch_abs_margin"] <= cutoff)
    if scope == "post_release_packet":
        return points["post_release_bool"] & points["inside_packet_geom_bool"]
    if scope == "post_release_carrier":
        return points["post_release_bool"] & points["main_carrier_bool"]
    if scope == "lower_boundary":
        return points["l"].isin(l_values[:width])
    if scope == "upper_boundary":
        return points["l"].isin(l_values[-width:])
    raise ValueError(f"unknown seed scope {scope!r}")


def _mask_summary(points: pd.DataFrame, label: str, scope: str, mask: pd.Series) -> dict[str, Any]:
    group = points.loc[mask].copy()
    row: dict[str, Any] = {"label": label, "seed_scope": scope, "rows": int(len(group))}
    if group.empty:
        row.update({
            "service_rows": 0,
            "carry_rows": 0,
            "post_release_rows": 0,
            "min_branch_abs_margin": math.nan,
            "gtt_nonnegative_rows": 0,
            "max_gtt": math.nan,
        })
        return row
    row.update({
        "service_rows": int(group["service_stage_bool"].sum()),
        "carry_rows": int(group["carry_stage_bool"].sum()),
        "post_release_rows": int(group["post_release_bool"].sum()),
        "min_branch_abs_margin": float(group["branch_abs_margin"].min()),
        "gtt_nonnegative_rows": int((group["gtt"] >= 0.0).sum()),
        "max_gtt": float(group["gtt"].max()),
    })
    return row


def _select_seeds(points: pd.DataFrame, label: str, scope: str, mask: pd.Series, seeds_per_scope: int) -> pd.DataFrame:
    candidates = points.loc[mask].copy()
    if candidates.empty:
        return pd.DataFrame()
    selected: list[pd.Series] = []
    selected.extend(row for _, row in candidates.nsmallest(seeds_per_scope, "branch_abs_margin").iterrows())
    selected.extend(row for _, row in candidates.nlargest(max(1, seeds_per_scope // 2), "gtt").iterrows())

    s_quantiles = np.linspace(0.10, 0.90, max(1, seeds_per_scope))
    for quantile in s_quantiles:
        target = float(candidates["s"].quantile(quantile))
        near = candidates.assign(_s_distance=(candidates["s"] - target).abs())
        selected.append(near.sort_values(["_s_distance", "branch_abs_margin"]).iloc[0])

    seeds = pd.DataFrame(selected).drop_duplicates(subset=["s", "l", "stage", "region"]).copy()
    seeds = seeds.sort_values(["branch_abs_margin", "s", "l"]).head(seeds_per_scope).copy()
    seeds["label"] = label
    seeds["seed_scope"] = scope
    seeds["seed_index"] = range(len(seeds))
    return seeds


def _trace_branch(
    grid: HorizonGrid,
    *,
    seed_s: float,
    seed_l: float,
    branch: str,
    step_scale: float,
    max_steps: int,
) -> dict[str, Any]:
    if branch not in {"plus", "minus"}:
        raise ValueError(f"unknown branch {branch!r}")
    speed_key = f"{branch}_null_speed"
    ds = max(grid.step_s * float(step_scale), 1.0e-8)
    s_value = float(seed_s)
    l_value = float(seed_l)
    l_start = float(seed_l)
    min_abs_speed = math.inf
    min_abs_margin = math.inf
    sign_changes = 0
    previous_speed = math.nan
    samples = 0
    outcome = "max_steps"

    for _ in range(max_steps):
        if not grid.in_bounds(s_value, l_value):
            outcome = "out_of_bounds"
            break
        speed = grid.interp(speed_key, s_value, l_value)
        margin = grid.interp("branch_abs_margin", s_value, l_value)
        if not math.isfinite(speed) or not math.isfinite(margin):
            outcome = "invalid_metric"
            break
        if math.isfinite(previous_speed) and previous_speed * speed < 0.0:
            sign_changes += 1
        previous_speed = speed
        min_abs_speed = min(min_abs_speed, abs(speed))
        min_abs_margin = min(min_abs_margin, abs(margin))

        mid_s = s_value + 0.5 * ds
        mid_l = l_value + 0.5 * speed * ds
        mid_speed = grid.interp(speed_key, mid_s, mid_l)
        if not math.isfinite(mid_speed):
            mid_speed = speed

        next_s = s_value + ds
        next_l = l_value + mid_speed * ds
        samples += 1

        if next_l <= grid.l_axis[0]:
            outcome = "l_lower_boundary"
            l_value = float(grid.l_axis[0])
            s_value = min(next_s, float(grid.s_axis[-1]))
            break
        if next_l >= grid.l_axis[-1]:
            outcome = "l_upper_boundary"
            l_value = float(grid.l_axis[-1])
            s_value = min(next_s, float(grid.s_axis[-1]))
            break
        if next_s > grid.s_axis[-1]:
            outcome = "s_upper_boundary"
            s_value = float(grid.s_axis[-1])
            l_value = float(next_l)
            break

        s_value = next_s
        l_value = next_l

    if not math.isfinite(min_abs_speed):
        min_abs_speed = math.nan
    if not math.isfinite(min_abs_margin):
        min_abs_margin = math.nan
    expected_boundary = "l_upper_boundary" if branch == "plus" else "l_lower_boundary"
    return {
        "branch": branch,
        "trace_outcome": outcome,
        "expected_escape_boundary": expected_boundary,
        "escaped_expected_side": outcome == expected_boundary,
        "escaped_any_radial_boundary": outcome in {"l_lower_boundary", "l_upper_boundary"},
        "trace_samples": samples,
        "seed_s": float(seed_s),
        "seed_l": float(seed_l),
        "final_s": float(s_value),
        "final_l": float(l_value),
        "final_stage": grid.nearest_text(grid.stage, s_value, l_value),
        "final_region": grid.nearest_text(grid.region, s_value, l_value),
        "delta_l": float(l_value - l_start),
        "min_abs_speed_along_trace": float(min_abs_speed),
        "min_branch_abs_margin_along_trace": float(min_abs_margin),
        "branch_sign_changes_along_trace": int(sign_changes),
    }


def _run_label(
    *,
    points: pd.DataFrame,
    label: str,
    seed_scopes: list[str],
    seeds_per_scope: int,
    boundary_width: int,
    step_scale: float,
    max_steps: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    grid = _build_grid(points)
    mask_rows: list[dict[str, Any]] = []
    seed_frames: list[pd.DataFrame] = []
    for scope in seed_scopes:
        mask = _scope_mask(points, scope, boundary_width)
        mask_rows.append(_mask_summary(points, label, scope, mask))
        seeds = _select_seeds(points, label, scope, mask, seeds_per_scope)
        if not seeds.empty:
            seed_frames.append(seeds)
    seed_frame = pd.concat(seed_frames, ignore_index=True) if seed_frames else pd.DataFrame()
    trace_rows: list[dict[str, Any]] = []
    for _, seed in seed_frame.iterrows():
        for branch in ["plus", "minus"]:
            trace_rows.append({
                "label": label,
                "seed_scope": str(seed["seed_scope"]),
                "seed_index": int(seed["seed_index"]),
                "seed_stage": str(seed["stage"]),
                "seed_region": str(seed["region"]),
                "seed_inside_packet_live": bool(seed.get("inside_packet_live_bool", False)),
                "seed_inside_packet_geom": bool(seed.get("inside_packet_geom_bool", False)),
                "seed_branch_abs_margin": float(seed["branch_abs_margin"]),
                "seed_gtt": float(seed["gtt"]),
                **_trace_branch(
                    grid,
                    seed_s=float(seed["s"]),
                    seed_l=float(seed["l"]),
                    branch=branch,
                    step_scale=step_scale,
                    max_steps=max_steps,
                ),
            })
    traces = pd.DataFrame(trace_rows)
    return pd.DataFrame(mask_rows), seed_frame, traces


def _summarize_traces(traces: pd.DataFrame) -> pd.DataFrame:
    if traces.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for (label, seed_scope, branch), group in traces.groupby(["label", "seed_scope", "branch"], sort=False):
        service = group["seed_stage"].astype(str).isin(SERVICE_STAGES)
        carry = group["seed_stage"].astype(str).isin(CARRY_STAGES)
        rows.append({
            "label": label,
            "seed_scope": seed_scope,
            "branch": branch,
            "traces": int(len(group)),
            "expected_escape_count": int(group["escaped_expected_side"].sum()),
            "any_radial_escape_count": int(group["escaped_any_radial_boundary"].sum()),
            "s_upper_boundary_count": int(group["trace_outcome"].eq("s_upper_boundary").sum()),
            "invalid_or_stalled_count": int(group["trace_outcome"].isin(["invalid_metric", "max_steps", "out_of_bounds"]).sum()),
            "service_seed_traces": int(service.sum()),
            "service_expected_escape_count": int(group.loc[service, "escaped_expected_side"].sum()),
            "carry_seed_traces": int(carry.sum()),
            "carry_expected_escape_count": int(group.loc[carry, "escaped_expected_side"].sum()),
            "min_abs_speed_along_trace": float(group["min_abs_speed_along_trace"].min()),
            "min_branch_abs_margin_along_trace": float(group["min_branch_abs_margin_along_trace"].min()),
            "branch_sign_changes_along_trace": int(group["branch_sign_changes_along_trace"].sum()),
            "outcome_counts": ";".join(
                f"{name}:{int(count)}" for name, count in group["trace_outcome"].value_counts().sort_index().items()
            ),
        })
    return pd.DataFrame(rows)


def _markdown_report(mask_summary: pd.DataFrame, trace_summary: pd.DataFrame, args: argparse.Namespace) -> str:
    lines = [
        "# Horizon Escape Ladder Pilot",
        "",
        "## Purpose",
        "",
        "This is the first global-horizon ladder rung: a sampled 1+1 radial null-escape diagnostic from explicit "
        "packet, carrier, boundary, branch-band, wake, and post-release masks. It tests whether null families "
        "started in those regions escape to a radial boundary within the finite ledger domain, or instead remain "
        "unresolved at the upper sigma boundary.",
        "",
        "## Settings",
        "",
        f"- seeds per scope: `{args.seeds_per_scope}`",
        f"- boundary width: `{args.boundary_width}` grid column(s)",
        f"- trace step scale: `{args.trace_step_scale}`",
        f"- max steps: `{args.max_steps}`",
        f"- seed scopes: `{', '.join(args.seed_scope)}`",
        "",
        "## Mask Summary",
        "",
    ]
    mask_cols = [
        "label",
        "seed_scope",
        "rows",
        "service_rows",
        "carry_rows",
        "post_release_rows",
        "min_branch_abs_margin",
        "gtt_nonnegative_rows",
        "max_gtt",
    ]
    lines.append(mask_summary[mask_cols].to_markdown(index=False) if not mask_summary.empty else "_No masks._")
    lines.append("")
    lines.append("## Trace Summary")
    lines.append("")
    trace_cols = [
        "label",
        "seed_scope",
        "branch",
        "traces",
        "expected_escape_count",
        "any_radial_escape_count",
        "s_upper_boundary_count",
        "service_seed_traces",
        "service_expected_escape_count",
        "carry_seed_traces",
        "carry_expected_escape_count",
        "min_branch_abs_margin_along_trace",
        "outcome_counts",
    ]
    lines.append(trace_summary[trace_cols].to_markdown(index=False) if not trace_summary.empty else "_No traces._")
    lines.append("")
    lines.append("## Interpretation Limits")
    lines.append("")
    lines.append(
        "This is not yet a trapped-surface or theorem-level event-horizon proof. A radial escape is favorable "
        "evidence for finite-domain accessibility. An `s_upper_boundary` result means the tested domain ended "
        "before escape was decided, so the next ladder rung is domain extension and refinement around unresolved "
        "masks, not a design verdict by itself."
    )
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the first radial null-escape rung of the horizon-freedom ladder.")
    parser.add_argument("--point-ledger", type=Path, action="append", default=[])
    parser.add_argument("--label", action="append", default=[])
    parser.add_argument("--metadata", type=Path, action="append", default=[], help="Metadata JSON with point_ledgers.")
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--seed-scope", action="append", choices=DEFAULT_SEED_SCOPES, default=None)
    parser.add_argument("--seeds-per-scope", type=int, default=5)
    parser.add_argument("--boundary-width", type=int, default=1)
    parser.add_argument("--trace-step-scale", type=float, default=0.5)
    parser.add_argument("--max-steps", type=int, default=4000)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    args.seed_scope = args.seed_scope or DEFAULT_SEED_SCOPES
    cases: list[tuple[Path, str]] = []
    for metadata in args.metadata:
        cases.extend(_load_metadata(metadata))
    if len(args.point_ledger) != len(args.label):
        raise SystemExit("--point-ledger and --label counts must match")
    cases.extend(zip(args.point_ledger, args.label))
    if not cases:
        raise SystemExit("Provide --metadata or at least one --point-ledger/--label pair")

    args.outdir.mkdir(parents=True, exist_ok=True)
    all_mask_summaries: list[pd.DataFrame] = []
    all_seeds: list[pd.DataFrame] = []
    all_traces: list[pd.DataFrame] = []
    started_at = time.perf_counter()
    for path, label in cases:
        points = _prepare_points(path)
        mask_summary, seeds, traces = _run_label(
            points=points,
            label=label,
            seed_scopes=args.seed_scope,
            seeds_per_scope=max(1, int(args.seeds_per_scope)),
            boundary_width=max(1, int(args.boundary_width)),
            step_scale=max(float(args.trace_step_scale), 1.0e-6),
            max_steps=max(1, int(args.max_steps)),
        )
        mask_summary["point_ledger"] = str(path)
        seeds["point_ledger"] = str(path)
        traces["point_ledger"] = str(path)
        all_mask_summaries.append(mask_summary)
        all_seeds.append(seeds)
        all_traces.append(traces)
        label_trace_summary = _summarize_traces(traces)
        unresolved = int(label_trace_summary["s_upper_boundary_count"].sum()) if not label_trace_summary.empty else 0
        radial = int(label_trace_summary["any_radial_escape_count"].sum()) if not label_trace_summary.empty else 0
        print(json.dumps({"label": label, "radial_escapes": radial, "s_upper_boundary": unresolved}), flush=True)

    mask_frame = pd.concat(all_mask_summaries, ignore_index=True) if all_mask_summaries else pd.DataFrame()
    seeds_frame = pd.concat(all_seeds, ignore_index=True) if all_seeds else pd.DataFrame()
    traces_frame = pd.concat(all_traces, ignore_index=True) if all_traces else pd.DataFrame()
    trace_summary = _summarize_traces(traces_frame)

    paths = {
        "mask_summary": args.outdir / "horizon_escape_mask_summary.csv",
        "seeds": args.outdir / "horizon_escape_seeds.csv",
        "traces": args.outdir / "horizon_escape_traces.csv",
        "trace_summary": args.outdir / "horizon_escape_trace_summary.csv",
        "report": args.outdir / "horizon_escape_ladder_report.md",
        "metadata": args.outdir / "horizon_escape_ladder_metadata.json",
    }
    mask_frame.to_csv(paths["mask_summary"], index=False)
    seeds_frame.to_csv(paths["seeds"], index=False)
    traces_frame.to_csv(paths["traces"], index=False)
    trace_summary.to_csv(paths["trace_summary"], index=False)
    paths["report"].write_text(_markdown_report(mask_frame, trace_summary, args), encoding="utf-8")

    repo_root = Path(__file__).resolve().parents[3]
    elapsed_s = round(time.perf_counter() - started_at, 3)
    paths["metadata"].write_text(
        json.dumps(
            {
                "cases": [{"path": str(path), "label": label} for path, label in cases],
                "seed_scopes": args.seed_scope,
                "seeds_per_scope": args.seeds_per_scope,
                "boundary_width": args.boundary_width,
                "trace_step_scale": args.trace_step_scale,
                "max_steps": args.max_steps,
                "elapsed_s": elapsed_s,
                "commit": _git_commit(repo_root),
                "files": {key: str(value) for key, value in paths.items() if key != "metadata"},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "outdir": str(args.outdir), "cases": len(cases), "elapsed_s": elapsed_s}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
