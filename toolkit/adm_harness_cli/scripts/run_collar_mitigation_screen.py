from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from run_dense_congruence_caustic_audit import (
    _build_dense_seeds,
    _bundle_evolution,
    _bundle_summary,
    _dense_offsets,
    _select_centers,
    _trace_dense_seeds,
)
from run_trace_expansion_audit import (
    _build_expansion_grid,
    _classification,
    _git_commit,
    _prepare_points,
)


MITIGATION_VARIANTS = [
    "beta_l_smooth",
    "areal_l_smooth",
    "gamma_ll_l_smooth",
    "packet_beta_relax",
    "beta_areal_l_smooth",
]


def _parse_csv_floats(raw: str) -> list[float]:
    values = [float(item.strip()) for item in raw.split(",") if item.strip()]
    return values or [0.0]


def _parse_csv_strings(raw: str) -> list[str]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    return values or list(MITIGATION_VARIANTS)


def _pivot_float(frame: pd.DataFrame, s_axis: np.ndarray, l_axis: np.ndarray, column: str) -> np.ndarray:
    return (
        frame.pivot_table(index="s", columns="l", values=column, aggfunc="mean")
        .reindex(index=s_axis, columns=l_axis)
        .to_numpy(dtype=float)
    )


def _grid_to_points(frame: pd.DataFrame, s_axis: np.ndarray, l_axis: np.ndarray, values: np.ndarray) -> pd.Series:
    lookup = pd.DataFrame(values, index=s_axis, columns=l_axis).stack(future_stack=True).rename("_value").reset_index()
    lookup.columns = ["s", "l", "_value"]
    merged = frame[["s", "l"]].merge(lookup, on=["s", "l"], how="left", sort=False)
    return pd.to_numeric(merged["_value"], errors="coerce")


def _normalized(values: np.ndarray) -> np.ndarray:
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return np.zeros_like(values, dtype=float)
    vmax = float(np.nanmax(finite))
    if vmax <= 0.0:
        return np.zeros_like(values, dtype=float)
    return np.clip(values / vmax, 0.0, 1.0)


def _collar_weight(
    points: pd.DataFrame,
    grid: Any,
    *,
    theta_eps: float,
    temporal_width_steps: float,
    radial_width_steps: float,
    core_limit: int,
) -> tuple[pd.Series, pd.DataFrame]:
    live = grid.arrays["inside_packet_live"] >= 0.5
    theta_plus = grid.arrays["theta_plus"]
    theta_minus = grid.arrays["theta_minus"]
    both = (theta_plus < -theta_eps) & (theta_minus < -theta_eps)
    strength = np.where(both, np.minimum(-theta_plus, -theta_minus), 0.0)
    branch_margin = grid.arrays["branch_abs_margin"]
    core_mask = live & both & np.isfinite(strength) & (strength > 0.0)
    if not np.any(core_mask):
        raise ValueError("no live both-shrinking collar core points found")

    s_mesh, l_mesh = np.meshgrid(grid.s_axis, grid.l_axis, indexing="ij")
    core_rows = pd.DataFrame({
        "s": s_mesh[core_mask],
        "l": l_mesh[core_mask],
        "theta_plus": theta_plus[core_mask],
        "theta_minus": theta_minus[core_mask],
        "trapped_like_strength": strength[core_mask],
        "branch_abs_margin": branch_margin[core_mask],
    }).sort_values(
        ["trapped_like_strength", "branch_abs_margin"],
        ascending=[False, True],
    )
    core_rows = core_rows.head(max(1, int(core_limit))).reset_index(drop=True)

    step_s = grid.step_s
    step_l = float(np.median(np.diff(grid.l_axis))) if len(grid.l_axis) > 1 else 1.0
    sigma_s = max(float(temporal_width_steps) * step_s, 1.0e-12)
    sigma_l = max(float(radial_width_steps) * step_l, 1.0e-12)
    weight = np.zeros_like(theta_plus, dtype=float)
    for row in core_rows.itertuples(index=False):
        candidate = np.exp(
            -0.5 * ((s_mesh - float(row.s)) / sigma_s) ** 2
            -0.5 * ((l_mesh - float(row.l)) / sigma_l) ** 2
        )
        weight = np.maximum(weight, candidate)
    weight = np.where(live, weight, 0.0)
    weight = _normalized(weight)
    return _grid_to_points(points, grid.s_axis, grid.l_axis, weight).fillna(0.0), core_rows


def _smooth_l(values: np.ndarray, passes: int) -> np.ndarray:
    out = values.astype(float).copy()
    for _ in range(max(1, int(passes))):
        padded = np.pad(out, ((0, 0), (1, 1)), mode="edge")
        out = 0.25 * padded[:, :-2] + 0.5 * padded[:, 1:-1] + 0.25 * padded[:, 2:]
    return out


def _blend_array(
    frame: pd.DataFrame,
    s_axis: np.ndarray,
    l_axis: np.ndarray,
    column: str,
    weight: pd.Series,
    strength: float,
    *,
    log_space: bool = False,
    passes: int = 2,
) -> pd.Series:
    values = _pivot_float(frame, s_axis, l_axis, column)
    if log_space:
        base = np.log(np.maximum(values, 1.0e-30))
        smooth = np.exp(_smooth_l(base, passes))
    else:
        smooth = _smooth_l(values, passes)
    target = values * (1.0 - float(strength)) + smooth * float(strength)
    target_points = _grid_to_points(frame, s_axis, l_axis, target)
    blend = np.clip(pd.to_numeric(weight, errors="coerce").fillna(0.0).to_numpy(dtype=float), 0.0, 1.0)
    original = pd.to_numeric(frame[column], errors="coerce").to_numpy(dtype=float)
    return pd.Series(original * (1.0 - blend) + target_points.to_numpy(dtype=float) * blend, index=frame.index)


def _recompute_metric_derived(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for column in ["alpha", "beta", "gamma_ll", "gamma_omega", "U_packet", "B"]:
        if column in out:
            out[column] = pd.to_numeric(out[column], errors="coerce")
    packet_speed = out["U_packet"] / np.maximum(out["B"], 1.0e-12)
    out["packet_coord_speed"] = packet_speed
    out["gtt"] = -out["alpha"] * out["alpha"] + out["gamma_ll"] * out["beta"] * out["beta"]
    out["packet_norm"] = -out["alpha"] * out["alpha"] + out["gamma_ll"] * (packet_speed + out["beta"]) ** 2
    return out


def _apply_variant(
    points: pd.DataFrame,
    grid: Any,
    weight: pd.Series,
    *,
    variant: str,
    strength: float,
    smooth_passes: int,
) -> pd.DataFrame:
    out = points.copy()
    s_axis = grid.s_axis
    l_axis = grid.l_axis
    variant = str(variant)
    if variant == "baseline" or float(strength) == 0.0:
        return _recompute_metric_derived(out)
    if variant in {"beta_l_smooth", "beta_areal_l_smooth"}:
        out["beta"] = _blend_array(out, s_axis, l_axis, "beta", weight, strength, passes=smooth_passes)
    if variant in {"areal_l_smooth", "beta_areal_l_smooth"}:
        out["gamma_omega"] = _blend_array(
            out,
            s_axis,
            l_axis,
            "gamma_omega",
            weight,
            strength,
            log_space=True,
            passes=smooth_passes,
        )
        out["gamma_omega"] = np.maximum(out["gamma_omega"], 1.0e-30)
    if variant == "gamma_ll_l_smooth":
        out["gamma_ll"] = _blend_array(
            out,
            s_axis,
            l_axis,
            "gamma_ll",
            weight,
            strength,
            log_space=True,
            passes=smooth_passes,
        )
        out["gamma_ll"] = np.maximum(out["gamma_ll"], 1.0e-30)
    if variant == "packet_beta_relax":
        packet_speed = pd.to_numeric(out["U_packet"], errors="coerce") / np.maximum(
            pd.to_numeric(out["B"], errors="coerce"),
            1.0e-12,
        )
        target_beta = -packet_speed
        blend = np.clip(weight.to_numpy(dtype=float) * float(strength), 0.0, 1.0)
        out["beta"] = out["beta"].astype(float) * (1.0 - blend) + target_beta.astype(float) * blend
    if variant not in MITIGATION_VARIANTS:
        raise ValueError(f"unknown mitigation variant {variant!r}")
    return _recompute_metric_derived(out)


def _pointwise_summary(points: pd.DataFrame, grid: Any, theta_eps: float) -> dict[str, Any]:
    rows = []
    for i_s, s_value in enumerate(grid.s_axis):
        for i_l, l_value in enumerate(grid.l_axis):
            theta_plus = float(grid.arrays["theta_plus"][i_s, i_l])
            theta_minus = float(grid.arrays["theta_minus"][i_s, i_l])
            rows.append({
                "s": float(s_value),
                "l": float(l_value),
                "inside_packet_live": bool(grid.arrays["inside_packet_live"][i_s, i_l] >= 0.5),
                "classification": _classification(theta_plus, theta_minus, theta_eps),
                "trapped_like_strength": (
                    min(-theta_plus, -theta_minus)
                    if theta_plus < -theta_eps and theta_minus < -theta_eps
                    else 0.0
                ),
            })
    diagnostic = pd.DataFrame(rows)
    live = diagnostic.loc[diagnostic["inside_packet_live"]]
    both_live = live.loc[live["classification"].eq("both_shrinking")]
    packet_live = points.loc[points["inside_packet_live_bool"]].copy()
    return {
        "pointwise_live_rows": int(len(live)),
        "pointwise_live_both_shrinking_rows": int(len(both_live)),
        "pointwise_live_max_trapped_like_strength": (
            float(both_live["trapped_like_strength"].max()) if len(both_live) else 0.0
        ),
        "positive_packet_norm_live": int((packet_live["packet_norm"].astype(float) > 0.0).sum()) if len(packet_live) else 0,
        "max_packet_norm_live": float(packet_live["packet_norm"].astype(float).max()) if len(packet_live) else math.nan,
        "min_packet_norm_live": float(packet_live["packet_norm"].astype(float).min()) if len(packet_live) else math.nan,
    }


def _trace_candidate(
    points: pd.DataFrame,
    centers: pd.DataFrame,
    *,
    rays_per_bundle: int,
    half_width_steps: float,
    trace_step_scale: float,
    max_steps: int,
    theta_eps: float,
    sample_stride: int,
    width_collapse_ratio: float,
    adjacent_collapse_ratio: float,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    grid = _build_expansion_grid(points)
    seeds = _build_dense_seeds(
        centers,
        grid,
        rays_per_bundle=rays_per_bundle,
        half_width_steps=half_width_steps,
    )
    traces, samples = _trace_dense_seeds(
        grid,
        seeds,
        trace_step_scale=trace_step_scale,
        max_steps=max_steps,
        theta_eps=theta_eps,
        sample_stride=sample_stride,
    )
    evolution = _bundle_evolution(samples, seeds, grid)
    bundle = _bundle_summary(
        traces,
        evolution,
        seeds,
        grid,
        width_collapse_ratio=width_collapse_ratio,
        adjacent_collapse_ratio=adjacent_collapse_ratio,
    )
    pointwise = _pointwise_summary(points, grid, theta_eps)
    return traces, evolution, bundle, pointwise


def _candidate_row(
    candidate_id: str,
    variant: str,
    strength: float,
    bundle: pd.DataFrame,
    pointwise: dict[str, Any],
    baseline: dict[str, Any] | None,
) -> dict[str, Any]:
    rays = int(bundle["rays"].sum()) if not bundle.empty else 0
    radial = int(bundle["radial_escape_count"].sum()) if not bundle.empty else 0
    sustained = int(bundle["sustained_both_shrinking_to_end_count"].sum()) if not bundle.empty else 0
    caustic = int(bundle["caustic_like_collapse"].sum()) if not bundle.empty else 0
    min_all_both_l = float(bundle["min_all_both_l_width_ratio"].min()) if not bundle.empty else math.nan
    min_all_both_radius = float(bundle["min_all_both_radius_width_ratio"].min()) if not bundle.empty else math.nan
    min_live_l = float(bundle["min_live_l_width_ratio"].min()) if not bundle.empty else math.nan
    max_integrated = float(bundle["max_integrated_trapped_like_strength"].max()) if not bundle.empty else math.nan
    max_both_fraction = float(bundle["max_bundle_both_shrinking_fraction"].max()) if not bundle.empty else math.nan
    row = {
        "candidate_id": candidate_id,
        "variant": variant,
        "strength": float(strength),
        "dense_rays": rays,
        "dense_radial_escape_count": radial,
        "dense_sustained_to_end_count": sustained,
        "caustic_like_bundle_count": caustic,
        "min_all_both_l_width_ratio": min_all_both_l,
        "min_all_both_radius_width_ratio": min_all_both_radius,
        "min_live_l_width_ratio": min_live_l,
        "max_integrated_trapped_like_strength": max_integrated,
        "max_bundle_both_shrinking_fraction": max_both_fraction,
        **pointwise,
    }
    if baseline:
        base_l = float(baseline.get("min_all_both_l_width_ratio", math.nan))
        base_radius = float(baseline.get("min_all_both_radius_width_ratio", math.nan))
        base_caustic = int(baseline.get("caustic_like_bundle_count", 0))
        row["delta_min_all_both_l_width_ratio"] = min_all_both_l - base_l
        row["delta_min_all_both_radius_width_ratio"] = min_all_both_radius - base_radius
        row["delta_caustic_like_bundle_count"] = caustic - base_caustic
        row["all_both_l_width_ratio_gain"] = min_all_both_l / base_l if base_l > 0.0 else math.nan
        row["all_both_radius_width_ratio_gain"] = min_all_both_radius / base_radius if base_radius > 0.0 else math.nan
    else:
        row["delta_min_all_both_l_width_ratio"] = math.nan
        row["delta_min_all_both_radius_width_ratio"] = math.nan
        row["delta_caustic_like_bundle_count"] = math.nan
        row["all_both_l_width_ratio_gain"] = math.nan
        row["all_both_radius_width_ratio_gain"] = math.nan
    if pointwise["positive_packet_norm_live"] > 0:
        decision = "reject_packet_timelikeness_loss"
    elif radial < rays:
        decision = "reject_radial_escape_loss"
    elif sustained > 0:
        decision = "reject_sustained_focusing"
    elif baseline and caustic < int(baseline.get("caustic_like_bundle_count", 0)):
        decision = "promising_caustic_count_reduction"
    elif baseline and math.isfinite(row["all_both_l_width_ratio_gain"]) and row["all_both_l_width_ratio_gain"] >= 1.25:
        decision = "promising_width_relief_signal"
    elif baseline and pointwise["pointwise_live_both_shrinking_rows"] < int(
        baseline.get("pointwise_live_both_shrinking_rows", 0)
    ):
        decision = "mixed_pointwise_relief_only"
    else:
        decision = "no_material_width_relief"
    row["screen_decision"] = decision
    return row


def _markdown_report(args: argparse.Namespace, summary: pd.DataFrame, core_rows: pd.DataFrame) -> str:
    lines = [
        "# Collar Mitigation Screen",
        "",
        "## Purpose",
        "",
        "This prescribed-metric screen probes the finite minus-branch carrier-focus collar with narrow in-memory field edits.",
        "It observes dense-bundle width preservation alongside packet timelikeness and radial escape before any full source-ledger rebuild.",
        "",
        "## Settings",
        "",
        f"- point ledger: `{args.point_ledger}`",
        f"- trace audit traces: `{args.trace_traces}`",
        f"- label: `{args.label}`",
        f"- variants: `{args.variants}`",
        f"- strengths: `{args.strengths}`",
        f"- rays per bundle: `{_dense_offsets(args.rays_per_bundle, args.half_width_steps).size}`",
        f"- half width: `{args.half_width_steps}` grid steps",
        f"- collar temporal width: `{args.collar_temporal_width_steps}` grid steps",
        f"- collar radial width: `{args.collar_radial_width_steps}` grid steps",
        "",
        "## Collar Core",
        "",
    ]
    core_cols = ["s", "l", "trapped_like_strength", "branch_abs_margin", "theta_plus", "theta_minus"]
    lines.append(core_rows[core_cols].head(12).to_markdown(index=False) if not core_rows.empty else "_No collar core._")
    lines.extend([
        "",
        "## Candidate Summary",
        "",
    ])
    display_cols = [
        "candidate_id",
        "variant",
        "strength",
        "screen_decision",
        "dense_radial_escape_count",
        "dense_rays",
        "positive_packet_norm_live",
        "max_packet_norm_live",
        "caustic_like_bundle_count",
        "min_all_both_l_width_ratio",
        "all_both_l_width_ratio_gain",
        "min_all_both_radius_width_ratio",
        "all_both_radius_width_ratio_gain",
        "pointwise_live_both_shrinking_rows",
    ]
    available = [column for column in display_cols if column in summary.columns]
    lines.append(summary[available].to_markdown(index=False) if not summary.empty else "_No candidate summary._")
    lines.extend([
        "",
        "## Caveat",
        "",
        "These are in-memory prescribed-field perturbations, not regenerated demanded-source ledgers or matter-model candidates.",
    ])
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace) -> dict[str, Path]:
    base_points = _prepare_points(args.point_ledger)
    base_grid = _build_expansion_grid(base_points)
    prior_traces = pd.read_csv(args.trace_traces)
    centers = _select_centers(
        prior_traces,
        top_centers=int(args.top_centers),
        center_families={"radial_null_branch_band", "congruence_branch_band"},
        require_both_shrinking=True,
    )
    weight, core_rows = _collar_weight(
        base_points,
        base_grid,
        theta_eps=float(args.theta_eps),
        temporal_width_steps=float(args.collar_temporal_width_steps),
        radial_width_steps=float(args.collar_radial_width_steps),
        core_limit=int(args.collar_core_limit),
    )

    args.outdir.mkdir(parents=True, exist_ok=True)
    variants = ["baseline"] + _parse_csv_strings(args.variants)
    strengths = _parse_csv_floats(args.strengths)
    candidate_rows: list[dict[str, Any]] = []
    bundle_frames: list[pd.DataFrame] = []
    evolution_frames: list[pd.DataFrame] = []
    trace_frames: list[pd.DataFrame] = []
    baseline_row: dict[str, Any] | None = None

    for variant in variants:
        variant_strengths = [0.0] if variant == "baseline" else strengths
        for strength in variant_strengths:
            candidate_id = "baseline" if variant == "baseline" else f"{variant}_s{str(strength).replace('.', 'p')}"
            candidate_points = _apply_variant(
                base_points,
                base_grid,
                weight,
                variant=variant,
                strength=float(strength),
                smooth_passes=int(args.smooth_passes),
            )
            traces, evolution, bundle, pointwise = _trace_candidate(
                candidate_points,
                centers,
                rays_per_bundle=int(args.rays_per_bundle),
                half_width_steps=float(args.half_width_steps),
                trace_step_scale=float(args.trace_step_scale),
                max_steps=int(args.max_steps),
                theta_eps=float(args.theta_eps),
                sample_stride=int(args.sample_stride),
                width_collapse_ratio=float(args.width_collapse_ratio),
                adjacent_collapse_ratio=float(args.adjacent_collapse_ratio),
            )
            row = _candidate_row(candidate_id, variant, float(strength), bundle, pointwise, baseline_row)
            if variant == "baseline":
                baseline_row = row
            candidate_rows.append(row)
            for frame in [bundle, evolution, traces]:
                frame.insert(0, "candidate_id", candidate_id)
                frame.insert(1, "variant", variant)
                frame.insert(2, "strength", float(strength))
            bundle_frames.append(bundle)
            evolution_frames.append(evolution)
            trace_frames.append(traces)
            if args.progress:
                print(json.dumps({
                    "event": "collar_candidate_complete",
                    "candidate_id": candidate_id,
                    "decision": row["screen_decision"],
                    "radial_escape": row["dense_radial_escape_count"],
                    "dense_rays": row["dense_rays"],
                    "positive_packet_norm_live": row["positive_packet_norm_live"],
                    "min_all_both_l_width_ratio": row["min_all_both_l_width_ratio"],
                    "gain": row["all_both_l_width_ratio_gain"],
                }), flush=True)

    summary = pd.DataFrame(candidate_rows)
    bundle_all = pd.concat(bundle_frames, ignore_index=True) if bundle_frames else pd.DataFrame()
    evolution_all = pd.concat(evolution_frames, ignore_index=True) if evolution_frames else pd.DataFrame()
    traces_all = pd.concat(trace_frames, ignore_index=True) if trace_frames else pd.DataFrame()
    paths = {
        "summary": args.outdir / "collar_mitigation_summary.csv",
        "bundle": args.outdir / "collar_mitigation_bundle_summary.csv",
        "evolution": args.outdir / "collar_mitigation_bundle_evolution.csv",
        "traces": args.outdir / "collar_mitigation_traces.csv",
        "centers": args.outdir / "collar_mitigation_centers.csv",
        "core": args.outdir / "collar_mitigation_core.csv",
        "report": args.outdir / "collar_mitigation_report.md",
        "metadata": args.outdir / "collar_mitigation_metadata.json",
    }
    summary.to_csv(paths["summary"], index=False)
    bundle_all.to_csv(paths["bundle"], index=False)
    evolution_all.to_csv(paths["evolution"], index=False)
    traces_all.to_csv(paths["traces"], index=False)
    centers.to_csv(paths["centers"], index=False)
    core_rows.to_csv(paths["core"], index=False)
    paths["report"].write_text(_markdown_report(args, summary, core_rows), encoding="utf-8")
    metadata = {
        "label": args.label,
        "point_ledger": str(args.point_ledger),
        "trace_traces": str(args.trace_traces),
        "repo_commit": _git_commit(Path.cwd()),
        "rows": {
            "summary": int(len(summary)),
            "bundle": int(len(bundle_all)),
            "evolution": int(len(evolution_all)),
            "traces": int(len(traces_all)),
            "centers": int(len(centers)),
            "core": int(len(core_rows)),
        },
        "settings": {
            "variants": variants,
            "strengths": strengths,
            "rays_per_bundle": int(_dense_offsets(args.rays_per_bundle, args.half_width_steps).size),
            "half_width_steps": float(args.half_width_steps),
            "theta_eps": float(args.theta_eps),
            "trace_step_scale": float(args.trace_step_scale),
            "collar_temporal_width_steps": float(args.collar_temporal_width_steps),
            "collar_radial_width_steps": float(args.collar_radial_width_steps),
            "smooth_passes": int(args.smooth_passes),
        },
        "files": {key: str(path) for key, path in paths.items() if key != "metadata"},
        "caveat": "Prescribed-metric in-memory collar perturbation screen; not a demanded-source ledger or matter model.",
    }
    paths["metadata"].write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Screen narrow prescribed-metric mitigations for the finite minus-branch carrier-focus collar."
    )
    parser.add_argument("--point-ledger", type=Path, required=True)
    parser.add_argument("--trace-traces", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--label", default="collar_mitigation_screen")
    parser.add_argument("--variants", default=",".join(MITIGATION_VARIANTS))
    parser.add_argument("--strengths", default="0.15,0.30,0.45")
    parser.add_argument("--top-centers", type=int, default=8)
    parser.add_argument("--rays-per-bundle", type=int, default=17)
    parser.add_argument("--half-width-steps", type=float, default=2.0)
    parser.add_argument("--theta-eps", type=float, default=1.0e-6)
    parser.add_argument("--trace-step-scale", type=float, default=0.5)
    parser.add_argument("--max-steps", type=int, default=12000)
    parser.add_argument("--sample-stride", type=int, default=1)
    parser.add_argument("--width-collapse-ratio", type=float, default=0.10)
    parser.add_argument("--adjacent-collapse-ratio", type=float, default=0.05)
    parser.add_argument("--collar-temporal-width-steps", type=float, default=4.0)
    parser.add_argument("--collar-radial-width-steps", type=float, default=4.0)
    parser.add_argument("--collar-core-limit", type=int, default=48)
    parser.add_argument("--smooth-passes", type=int, default=3)
    parser.add_argument("--progress", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
