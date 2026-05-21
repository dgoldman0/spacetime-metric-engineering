from __future__ import annotations

import argparse
import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SERVICE_STAGES = {"catch_rematch", "held_carry", "release_shift_fade"}


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


def _pivot_float(frame: pd.DataFrame, s_axis: np.ndarray, l_axis: np.ndarray, column: str) -> np.ndarray:
    return (
        frame.pivot_table(index="s", columns="l", values=column, aggfunc="mean")
        .reindex(index=s_axis, columns=l_axis)
        .to_numpy(dtype=float)
    )


@dataclass
class ExpansionGrid:
    s_axis: np.ndarray
    l_axis: np.ndarray
    arrays: dict[str, np.ndarray]

    @property
    def step_s(self) -> float:
        return float(np.median(np.diff(self.s_axis))) if len(self.s_axis) > 1 else 1.0

    def in_bounds(self, s_value: float, l_value: float) -> bool:
        return self.s_axis[0] <= s_value <= self.s_axis[-1] and self.l_axis[0] <= l_value <= self.l_axis[-1]

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


def _prepare_points(path: Path) -> pd.DataFrame:
    points = pd.read_csv(path)
    required = ["s", "l", "stage", "region", "alpha", "beta", "gamma_ll", "gamma_omega"]
    missing = [column for column in required if column not in points.columns]
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")
    for column in ["s", "l", "alpha", "beta", "gamma_ll", "gamma_omega"]:
        points[column] = pd.to_numeric(points[column], errors="coerce")
    points = points.dropna(subset=["s", "l", "alpha", "beta", "gamma_ll", "gamma_omega"]).copy()
    points["inside_packet_live_bool"] = (
        _bool_series(points["inside_packet_live"]) if "inside_packet_live" in points else False
    )
    points["inside_packet_geom_bool"] = (
        _bool_series(points["inside_packet_geom"]) if "inside_packet_geom" in points else False
    )
    points["service_stage_bool"] = points["stage"].astype(str).isin(SERVICE_STAGES)
    points["packet_coord_speed"] = _as_float(points, "U_packet", 0.0) / np.maximum(_as_float(points, "B", 1.0), 1.0e-12)
    points["packet_norm"] = _as_float(points, "packet_norm")
    return points


def _build_expansion_grid(points: pd.DataFrame) -> ExpansionGrid:
    s_axis = np.array(sorted(points["s"].dropna().unique()), dtype=float)
    l_axis = np.array(sorted(points["l"].dropna().unique()), dtype=float)
    if len(s_axis) < 3 or len(l_axis) < 3:
        raise ValueError("trace expansion audit requires at least a 3x3 grid")
    alpha = _pivot_float(points, s_axis, l_axis, "alpha")
    beta = _pivot_float(points, s_axis, l_axis, "beta")
    gamma_ll = _pivot_float(points, s_axis, l_axis, "gamma_ll")
    gamma_omega = _pivot_float(points, s_axis, l_axis, "gamma_omega")
    packet_speed = _pivot_float(points, s_axis, l_axis, "packet_coord_speed")
    packet_norm = _pivot_float(points, s_axis, l_axis, "packet_norm")
    live = (
        points.pivot_table(index="s", columns="l", values="inside_packet_live_bool", aggfunc="max")
        .reindex(index=s_axis, columns=l_axis)
        .fillna(False)
        .astype(float)
        .to_numpy(dtype=float)
    )
    geom = (
        points.pivot_table(index="s", columns="l", values="inside_packet_geom_bool", aggfunc="max")
        .reindex(index=s_axis, columns=l_axis)
        .fillna(False)
        .astype(float)
        .to_numpy(dtype=float)
    )
    radius = np.sqrt(np.maximum(gamma_omega, 0.0))
    dR_ds, dR_dl = np.gradient(radius, s_axis, l_axis, edge_order=2)
    sqrt_gamma_ll = np.sqrt(np.maximum(gamma_ll, 1.0e-30))
    plus_speed = -beta + alpha / sqrt_gamma_ll
    minus_speed = -beta - alpha / sqrt_gamma_ll
    denom = np.maximum(radius, 1.0e-30)
    theta_plus = 2.0 * (dR_ds + plus_speed * dR_dl) / denom
    theta_minus = 2.0 * (dR_ds + minus_speed * dR_dl) / denom
    arrays = {
        "alpha": alpha,
        "beta": beta,
        "gamma_ll": gamma_ll,
        "radius": radius,
        "dR_ds": dR_ds,
        "dR_dl": dR_dl,
        "packet_coord_speed": packet_speed,
        "packet_norm": packet_norm,
        "inside_packet_live": live,
        "inside_packet_geom": geom,
        "plus_speed": plus_speed,
        "minus_speed": minus_speed,
        "branch_abs_margin": np.minimum(np.abs(plus_speed), np.abs(minus_speed)),
        "theta_plus": theta_plus,
        "theta_minus": theta_minus,
    }
    return ExpansionGrid(s_axis=s_axis, l_axis=l_axis, arrays=arrays)


def _speed_for_branch(grid: ExpansionGrid, branch: str, s_value: float, l_value: float, angular_fraction: float) -> float:
    if branch == "packet":
        return grid.interp("packet_coord_speed", s_value, l_value)
    if branch == "plus":
        return grid.interp("plus_speed", s_value, l_value)
    if branch == "minus":
        return grid.interp("minus_speed", s_value, l_value)
    if branch in {"offaxis_plus", "offaxis_minus"}:
        alpha = grid.interp("alpha", s_value, l_value)
        beta = grid.interp("beta", s_value, l_value)
        gamma_ll = grid.interp("gamma_ll", s_value, l_value)
        if not all(math.isfinite(value) for value in [alpha, beta, gamma_ll]) or gamma_ll <= 0.0:
            return math.nan
        radial_fraction = math.sqrt(max(0.0, 1.0 - float(angular_fraction) ** 2))
        sign = 1.0 if branch == "offaxis_plus" else -1.0
        return float(-beta + sign * radial_fraction * alpha / math.sqrt(gamma_ll))
    raise ValueError(f"unknown branch {branch!r}")


def _branch_theta(grid: ExpansionGrid, s_value: float, l_value: float, speed: float) -> float:
    radius = grid.interp("radius", s_value, l_value)
    dR_ds = grid.interp("dR_ds", s_value, l_value)
    dR_dl = grid.interp("dR_dl", s_value, l_value)
    if not all(math.isfinite(value) for value in [radius, dR_ds, dR_dl, speed]) or radius <= 0.0:
        return math.nan
    return float(2.0 * (dR_ds + speed * dR_dl) / radius)


def _classification(theta_plus: float, theta_minus: float, theta_eps: float) -> str:
    if not all(math.isfinite(value) for value in [theta_plus, theta_minus]):
        return "invalid"
    if theta_plus < -theta_eps and theta_minus < -theta_eps:
        return "both_shrinking"
    if theta_plus > theta_eps and theta_minus > theta_eps:
        return "both_expanding"
    if abs(theta_plus) <= theta_eps or abs(theta_minus) <= theta_eps:
        return "near_marginal"
    return "split"


def _trace_seed(
    grid: ExpansionGrid,
    seed: pd.Series,
    *,
    step_scale: float,
    max_steps: int,
    theta_eps: float,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    ds = max(grid.step_s * float(step_scale), 1.0e-8)
    branch = str(seed["branch"])
    angular_fraction = float(seed.get("angular_fraction", 0.0))
    s_value = float(seed["seed_s"])
    l_value = float(seed["seed_l"])
    samples: list[dict[str, Any]] = []
    outcome = "max_steps"
    both_run = 0
    longest_both_run = 0
    integrated_trapped = 0.0
    integrated_negative_branch = 0.0
    integrated_abs_branch = 0.0
    min_branch_theta = math.inf
    max_branch_theta = -math.inf
    entered_live = bool(seed.get("seed_inside_packet_live", False))
    entered_both_shrinking = False
    last_class = "invalid"

    for sample_index in range(int(max_steps)):
        if not grid.in_bounds(s_value, l_value):
            outcome = "out_of_bounds"
            break
        speed = _speed_for_branch(grid, branch, s_value, l_value, angular_fraction)
        theta_plus = grid.interp("theta_plus", s_value, l_value)
        theta_minus = grid.interp("theta_minus", s_value, l_value)
        branch_theta = _branch_theta(grid, s_value, l_value, speed)
        packet_norm = grid.interp("packet_norm", s_value, l_value)
        branch_margin = grid.interp("branch_abs_margin", s_value, l_value)
        if not all(math.isfinite(value) for value in [speed, theta_plus, theta_minus, branch_theta]):
            outcome = "invalid_metric"
            break
        classification = _classification(theta_plus, theta_minus, theta_eps)
        trapped_strength = min(-theta_plus, -theta_minus) if classification == "both_shrinking" else 0.0
        if classification == "both_shrinking":
            both_run += 1
            entered_both_shrinking = True
            integrated_trapped += trapped_strength * ds
        else:
            both_run = 0
        longest_both_run = max(longest_both_run, both_run)
        integrated_negative_branch += max(-branch_theta, 0.0) * ds
        integrated_abs_branch += abs(branch_theta) * ds
        min_branch_theta = min(min_branch_theta, branch_theta)
        max_branch_theta = max(max_branch_theta, branch_theta)
        entered_live = entered_live or bool(grid.interp("inside_packet_live", s_value, l_value) >= 0.5)
        last_class = classification
        samples.append({
            "seed_index": int(seed["seed_index"]),
            "probe_family": str(seed["probe_family"]),
            "branch": branch,
            "sample_index": int(sample_index),
            "s": float(s_value),
            "l": float(l_value),
            "theta_plus": float(theta_plus),
            "theta_minus": float(theta_minus),
            "branch_theta": float(branch_theta),
            "expansion_class": classification,
            "trapped_like_strength": float(trapped_strength),
            "branch_abs_margin": float(branch_margin) if math.isfinite(branch_margin) else math.nan,
            "packet_norm": float(packet_norm) if math.isfinite(packet_norm) else math.nan,
            "inside_packet_live": bool(grid.interp("inside_packet_live", s_value, l_value) >= 0.5),
            "inside_packet_geom": bool(grid.interp("inside_packet_geom", s_value, l_value) >= 0.5),
        })

        mid_s = s_value + 0.5 * ds
        mid_l = l_value + 0.5 * speed * ds
        mid_speed = _speed_for_branch(grid, branch, mid_s, mid_l, angular_fraction)
        if not math.isfinite(mid_speed):
            mid_speed = speed
        next_s = s_value + ds
        next_l = l_value + mid_speed * ds
        if next_l <= grid.l_axis[0]:
            outcome = "l_lower_boundary"
            s_value = min(next_s, float(grid.s_axis[-1]))
            l_value = float(grid.l_axis[0])
            break
        if next_l >= grid.l_axis[-1]:
            outcome = "l_upper_boundary"
            s_value = min(next_s, float(grid.s_axis[-1]))
            l_value = float(grid.l_axis[-1])
            break
        if next_s > grid.s_axis[-1]:
            outcome = "s_upper_boundary"
            s_value = float(grid.s_axis[-1])
            l_value = float(next_l)
            break
        s_value = next_s
        l_value = next_l

    both_samples = sum(1 for sample in samples if sample["expansion_class"] == "both_shrinking")
    recovered = bool(entered_both_shrinking and last_class != "both_shrinking")
    sustained = bool(entered_both_shrinking and last_class == "both_shrinking")
    trace = {
        "probe_family": str(seed["probe_family"]),
        "branch": branch,
        "seed_index": int(seed["seed_index"]),
        "bundle_id": str(seed.get("bundle_id", "")),
        "seed_s": float(seed["seed_s"]),
        "seed_l": float(seed["seed_l"]),
        "seed_stage": str(seed.get("seed_stage", "")),
        "seed_region": str(seed.get("seed_region", "")),
        "seed_inside_packet_live": bool(seed.get("seed_inside_packet_live", False)),
        "seed_inside_packet_geom": bool(seed.get("seed_inside_packet_geom", False)),
        "trace_outcome": outcome,
        "trace_samples": int(len(samples)),
        "final_s": float(s_value),
        "final_l": float(l_value),
        "entered_live_packet": bool(entered_live),
        "entered_both_shrinking": bool(entered_both_shrinking),
        "recovered_from_both_shrinking": recovered,
        "sustained_both_shrinking_to_end": sustained,
        "both_shrinking_samples": int(both_samples),
        "both_shrinking_fraction": float(both_samples / len(samples)) if samples else math.nan,
        "longest_both_shrinking_run": int(longest_both_run),
        "integrated_trapped_like_strength": float(integrated_trapped),
        "integrated_negative_branch_expansion": float(integrated_negative_branch),
        "negative_branch_expansion_share": (
            float(integrated_negative_branch / integrated_abs_branch) if integrated_abs_branch > 0.0 else math.nan
        ),
        "min_branch_theta": float(min_branch_theta) if math.isfinite(min_branch_theta) else math.nan,
        "max_branch_theta": float(max_branch_theta) if math.isfinite(max_branch_theta) else math.nan,
        "last_expansion_class": last_class,
    }
    return trace, samples


def _summarize_traces(traces: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (family, branch), group in traces.groupby(["probe_family", "branch"], sort=False):
        rows.append({
            "probe_family": family,
            "branch": branch,
            "traces": int(len(group)),
            "radial_escape_count": int(group["trace_outcome"].isin(["l_lower_boundary", "l_upper_boundary"]).sum()),
            "s_upper_boundary_count": int(group["trace_outcome"].eq("s_upper_boundary").sum()),
            "traces_entering_both_shrinking": int(group["entered_both_shrinking"].sum()),
            "traces_recovered": int(group["recovered_from_both_shrinking"].sum()),
            "traces_sustained_to_end": int(group["sustained_both_shrinking_to_end"].sum()),
            "max_integrated_trapped_like_strength": float(group["integrated_trapped_like_strength"].max()),
            "mean_integrated_trapped_like_strength": float(group["integrated_trapped_like_strength"].mean()),
            "max_longest_both_shrinking_run": int(group["longest_both_shrinking_run"].max()),
            "max_both_shrinking_fraction": float(group["both_shrinking_fraction"].max()),
            "min_branch_theta": float(group["min_branch_theta"].min()),
            "max_branch_theta": float(group["max_branch_theta"].max()),
            "max_integrated_negative_branch_expansion": float(group["integrated_negative_branch_expansion"].max()),
            "max_negative_branch_expansion_share": float(group["negative_branch_expansion_share"].max()),
            "outcome_counts": ";".join(
                f"{name}:{int(count)}" for name, count in group["trace_outcome"].value_counts().sort_index().items()
            ),
        })
    return pd.DataFrame(rows)


def _decision(summary: pd.DataFrame) -> str:
    watched = summary.loc[
        summary["probe_family"].isin(["radial_null_branch_band", "offaxis_null_branch_band", "congruence_branch_band"])
    ]
    if watched.empty:
        return "undecidable_no_branch_band_traces"
    sustained = int(watched["traces_sustained_to_end"].sum())
    entered = int(watched["traces_entering_both_shrinking"].sum())
    recovered = int(watched["traces_recovered"].sum())
    if sustained > 0:
        return "adverse_sustained_branch_band_focusing"
    if entered > 0 and recovered == entered:
        return "favorable_transient_branch_band_focusing"
    if entered > 0:
        return "mixed_branch_band_focusing"
    return "favorable_no_branch_band_focusing"


def _markdown_report(args: argparse.Namespace, summary: pd.DataFrame, decision: str) -> str:
    lines = [
        "# Trace Expansion Audit",
        "",
        "## Purpose",
        "",
        "This diagnostic retraces scheduled ADM probe seeds through the prescribed metric and samples the null-expansion proxy along each path.",
        "It asks whether pointwise both-branch areal shrinking is transient and recovered, or sustained along probe evolution.",
        "",
        "## Settings",
        "",
        f"- point ledger: `{args.point_ledger}`",
        f"- seeds: `{args.seeds}`",
        f"- label: `{args.label}`",
        f"- theta epsilon: `{args.theta_eps}`",
        f"- trace step scale: `{args.trace_step_scale}`",
        f"- max steps: `{args.max_steps}`",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Probe Summary",
        "",
    ]
    cols = [
        "probe_family",
        "branch",
        "traces",
        "radial_escape_count",
        "s_upper_boundary_count",
        "traces_entering_both_shrinking",
        "traces_recovered",
        "traces_sustained_to_end",
        "max_integrated_trapped_like_strength",
        "max_longest_both_shrinking_run",
        "max_both_shrinking_fraction",
        "min_branch_theta",
        "max_branch_theta",
        "outcome_counts",
    ]
    available = [column for column in cols if column in summary.columns]
    lines.append(summary[available].to_markdown(index=False) if not summary.empty else "_No trace summary._")
    lines.extend([
        "",
        "## Caveat",
        "",
        "This is still a prescribed-metric probe diagnostic. It is not a full trapped-surface theorem, matter evolution, or dynamical Einstein evolution.",
    ])
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace) -> dict[str, Path]:
    points = _prepare_points(args.point_ledger)
    grid = _build_expansion_grid(points)
    seeds = pd.read_csv(args.seeds)
    if "seed_index" not in seeds:
        seeds["seed_index"] = range(len(seeds))
    trace_rows: list[dict[str, Any]] = []
    sample_rows: list[dict[str, Any]] = []
    for _, seed in seeds.iterrows():
        trace, samples = _trace_seed(
            grid,
            seed,
            step_scale=float(args.trace_step_scale),
            max_steps=int(args.max_steps),
            theta_eps=float(args.theta_eps),
        )
        trace_rows.append(trace)
        if int(args.sample_stride) > 0:
            sample_rows.extend(samples[:: int(args.sample_stride)])
    traces = pd.DataFrame(trace_rows)
    samples = pd.DataFrame(sample_rows)
    summary = _summarize_traces(traces)
    decision = _decision(summary)

    args.outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "traces": args.outdir / "trace_expansion_audit_traces.csv",
        "samples": args.outdir / "trace_expansion_audit_samples.csv",
        "summary": args.outdir / "trace_expansion_audit_summary.csv",
        "report": args.outdir / "trace_expansion_audit_report.md",
        "metadata": args.outdir / "trace_expansion_audit_metadata.json",
    }
    traces.to_csv(paths["traces"], index=False)
    samples.to_csv(paths["samples"], index=False)
    summary.to_csv(paths["summary"], index=False)
    paths["report"].write_text(_markdown_report(args, summary, decision), encoding="utf-8")
    metadata = {
        "label": args.label,
        "point_ledger": str(args.point_ledger),
        "seeds": str(args.seeds),
        "repo_commit": _git_commit(Path.cwd()),
        "theta_eps": float(args.theta_eps),
        "trace_step_scale": float(args.trace_step_scale),
        "max_steps": int(args.max_steps),
        "decision": decision,
        "rows": {
            "traces": int(len(traces)),
            "samples": int(len(samples)),
            "summary": int(len(summary)),
        },
        "files": {key: str(path) for key, path in paths.items() if key != "metadata"},
        "caveat": "Prescribed-metric trace expansion audit; not a full trapped-surface theorem or matter evolution.",
    }
    paths["metadata"].write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    if args.progress:
        print(json.dumps({
            "event": "trace_expansion_audit_complete",
            "label": args.label,
            "decision": decision,
            "traces": int(len(traces)),
            "samples": int(len(samples)),
            "outdir": str(args.outdir),
        }), flush=True)
        watched = summary.loc[
            summary["probe_family"].isin(["radial_null_branch_band", "offaxis_null_branch_band", "congruence_branch_band"])
        ]
        if not watched.empty:
            print(watched[[
                "probe_family",
                "branch",
                "traces",
                "traces_entering_both_shrinking",
                "traces_recovered",
                "traces_sustained_to_end",
                "max_integrated_trapped_like_strength",
                "max_longest_both_shrinking_run",
                "outcome_counts",
            ]].to_string(index=False), flush=True)
    return paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit trace-integrated null-expansion proxy along scheduled ADM seeds.")
    parser.add_argument("--point-ledger", type=Path, required=True)
    parser.add_argument("--seeds", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--label", default="trace_expansion_audit")
    parser.add_argument("--theta-eps", type=float, default=1.0e-6)
    parser.add_argument("--trace-step-scale", type=float, default=0.5)
    parser.add_argument("--max-steps", type=int, default=12000)
    parser.add_argument("--sample-stride", type=int, default=1)
    parser.add_argument("--progress", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
