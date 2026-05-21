from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SERVICE_STAGES = {"catch_rematch", "held_carry", "release_shift_fade"}
CARRY_STAGES = {"held_carry", "release_shift_fade"}
SUPPORT_PLANT_REGIONS = {"core_throat", "support_edge", "outer_quarantine_shell", "packet_in_support"}
MAIN_CARRIER_REGIONS = {"core_throat", "support_edge", "packet_in_support"}


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


def _prepare_points(path: Path) -> pd.DataFrame:
    points = pd.read_csv(path)
    required = ["s", "l", "stage", "region", "alpha", "beta", "gamma_ll", "gamma_omega"]
    missing = [column for column in required if column not in points.columns]
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")
    for column in ["s", "l", "alpha", "beta", "gamma_ll", "gamma_omega"]:
        points[column] = pd.to_numeric(points[column], errors="coerce")
    points = points.dropna(subset=["s", "l", "alpha", "beta", "gamma_ll", "gamma_omega"]).copy()
    points["stage"] = points["stage"].astype(str)
    points["region"] = points["region"].astype(str)
    points["inside_packet_live_bool"] = (
        _bool_series(points["inside_packet_live"]) if "inside_packet_live" in points else False
    )
    points["inside_packet_geom_bool"] = (
        _bool_series(points["inside_packet_geom"]) if "inside_packet_geom" in points else False
    )
    points["service_stage_bool"] = points["stage"].isin(SERVICE_STAGES)
    points["carry_stage_bool"] = points["stage"].isin(CARRY_STAGES)
    points["post_release_bool"] = points["stage"].eq("post_release_buffer")
    points["reset_tail_bool"] = (
        points["stage"].eq("reset_decompression")
        & points["inside_packet_geom_bool"]
        & ~points["inside_packet_live_bool"]
    )
    points["main_carrier_bool"] = points["region"].isin(MAIN_CARRIER_REGIONS)
    points["support_plant_bool"] = points["region"].isin(SUPPORT_PLANT_REGIONS)
    points["volume_weight"] = _as_float(points, "volume_weight", 1.0).fillna(1.0)
    return points


def _compute_expansion_points(points: pd.DataFrame, theta_eps: float) -> pd.DataFrame:
    s_axis = np.array(sorted(points["s"].dropna().unique()), dtype=float)
    l_axis = np.array(sorted(points["l"].dropna().unique()), dtype=float)
    if len(s_axis) < 3 or len(l_axis) < 3:
        raise ValueError("null-expansion proxy requires at least a 3x3 grid")

    alpha = _pivot_float(points, s_axis, l_axis, "alpha")
    beta = _pivot_float(points, s_axis, l_axis, "beta")
    gamma_ll = _pivot_float(points, s_axis, l_axis, "gamma_ll")
    gamma_omega = _pivot_float(points, s_axis, l_axis, "gamma_omega")
    radius = np.sqrt(np.maximum(gamma_omega, 0.0))

    dR_ds, dR_dl = np.gradient(radius, s_axis, l_axis, edge_order=2)
    sqrt_gamma_ll = np.sqrt(np.maximum(gamma_ll, 1.0e-30))
    plus_speed = -beta + alpha / sqrt_gamma_ll
    minus_speed = -beta - alpha / sqrt_gamma_ll
    denom = np.maximum(radius, 1.0e-30)
    plus_areal_drift = dR_ds + plus_speed * dR_dl
    minus_areal_drift = dR_ds + minus_speed * dR_dl
    theta_plus = 2.0 * plus_areal_drift / denom
    theta_minus = 2.0 * minus_areal_drift / denom
    branch_abs_margin = np.minimum(np.abs(plus_speed), np.abs(minus_speed))

    grid = pd.DataFrame({
        "s": np.repeat(s_axis, len(l_axis)),
        "l": np.tile(l_axis, len(s_axis)),
        "areal_radius": radius.reshape(-1),
        "dR_ds": dR_ds.reshape(-1),
        "dR_dl": dR_dl.reshape(-1),
        "plus_null_speed": plus_speed.reshape(-1),
        "minus_null_speed": minus_speed.reshape(-1),
        "branch_abs_margin": branch_abs_margin.reshape(-1),
        "theta_plus": theta_plus.reshape(-1),
        "theta_minus": theta_minus.reshape(-1),
        "plus_areal_drift": plus_areal_drift.reshape(-1),
        "minus_areal_drift": minus_areal_drift.reshape(-1),
    })
    out = points.merge(grid, on=["s", "l"], how="left")
    out["both_shrinking_proxy"] = (out["theta_plus"] < -theta_eps) & (out["theta_minus"] < -theta_eps)
    out["both_expanding_proxy"] = (out["theta_plus"] > theta_eps) & (out["theta_minus"] > theta_eps)
    out["near_marginal_proxy"] = (
        (out["theta_plus"].abs() <= theta_eps) | (out["theta_minus"].abs() <= theta_eps)
    )
    out["split_expansion_proxy"] = (
        ~(out["both_shrinking_proxy"] | out["both_expanding_proxy"] | out["near_marginal_proxy"])
        & np.isfinite(out["theta_plus"])
        & np.isfinite(out["theta_minus"])
    )
    out["trapped_like_strength"] = np.where(
        out["both_shrinking_proxy"],
        np.minimum(-out["theta_plus"], -out["theta_minus"]),
        0.0,
    )
    out["anti_trapped_like_strength"] = np.where(
        out["both_expanding_proxy"],
        np.minimum(out["theta_plus"], out["theta_minus"]),
        0.0,
    )
    return out


def _scope_masks(points: pd.DataFrame) -> dict[str, pd.Series]:
    live_branch = points.loc[points["inside_packet_live_bool"], "branch_abs_margin"].dropna()
    branch_cutoff = float(live_branch.quantile(0.20)) if not live_branch.empty else math.nan
    false = pd.Series(False, index=points.index)
    masks = {
        "all": pd.Series(True, index=points.index),
        "packet_live": points["inside_packet_live_bool"],
        "packet_geom": points["inside_packet_geom_bool"],
        "service_live": points["inside_packet_live_bool"] & points["service_stage_bool"],
        "branch_band_live_q20": (
            points["inside_packet_live_bool"] & (points["branch_abs_margin"] <= branch_cutoff)
            if math.isfinite(branch_cutoff)
            else false
        ),
        "main_carrier": points["main_carrier_bool"],
        "support_plant": points["support_plant_bool"],
        "post_release_packet": points["post_release_bool"] & points["inside_packet_geom_bool"],
        "reset_tail_packet_geom": points["reset_tail_bool"],
    }
    return masks


def _weighted_fraction(frame: pd.DataFrame, mask: pd.Series) -> float:
    total = float(frame["volume_weight"].sum())
    if total <= 0.0:
        return math.nan
    return float(frame.loc[mask, "volume_weight"].sum() / total)


def _summarize_scope(points: pd.DataFrame, scope: str, mask: pd.Series) -> dict[str, Any]:
    group = points.loc[mask].copy()
    row: dict[str, Any] = {"scope": scope, "rows": int(len(group))}
    if group.empty:
        row.update({
            "both_shrinking_rows": 0,
            "both_expanding_rows": 0,
            "near_marginal_rows": 0,
            "split_expansion_rows": 0,
            "both_shrinking_fraction": math.nan,
            "both_shrinking_volume_fraction": math.nan,
            "max_trapped_like_strength": math.nan,
            "min_theta_plus": math.nan,
            "min_theta_minus": math.nan,
            "min_branch_abs_margin": math.nan,
            "max_packet_norm": math.nan,
        })
        return row
    shrink = group["both_shrinking_proxy"].astype(bool)
    expand = group["both_expanding_proxy"].astype(bool)
    marginal = group["near_marginal_proxy"].astype(bool)
    split = group["split_expansion_proxy"].astype(bool)
    row.update({
        "both_shrinking_rows": int(shrink.sum()),
        "both_expanding_rows": int(expand.sum()),
        "near_marginal_rows": int(marginal.sum()),
        "split_expansion_rows": int(split.sum()),
        "both_shrinking_fraction": float(shrink.mean()),
        "both_expanding_fraction": float(expand.mean()),
        "near_marginal_fraction": float(marginal.mean()),
        "split_expansion_fraction": float(split.mean()),
        "both_shrinking_volume_fraction": _weighted_fraction(group, shrink),
        "both_expanding_volume_fraction": _weighted_fraction(group, expand),
        "max_trapped_like_strength": float(group["trapped_like_strength"].max()),
        "max_anti_trapped_like_strength": float(group["anti_trapped_like_strength"].max()),
        "min_theta_plus": float(group["theta_plus"].min()),
        "max_theta_plus": float(group["theta_plus"].max()),
        "min_theta_minus": float(group["theta_minus"].min()),
        "max_theta_minus": float(group["theta_minus"].max()),
        "min_branch_abs_margin": float(group["branch_abs_margin"].min()),
        "max_packet_norm": float(_as_float(group, "packet_norm", math.nan).max()),
        "live_rows": int(group["inside_packet_live_bool"].sum()),
        "service_rows": int(group["service_stage_bool"].sum()),
    })
    return row


def _top_points(points: pd.DataFrame, limit: int) -> pd.DataFrame:
    display = [
        "s",
        "l",
        "stage",
        "region",
        "inside_packet_live_bool",
        "inside_packet_geom_bool",
        "theta_plus",
        "theta_minus",
        "trapped_like_strength",
        "anti_trapped_like_strength",
        "branch_abs_margin",
        "packet_norm",
        "areal_radius",
        "plus_null_speed",
        "minus_null_speed",
    ]
    available = [column for column in display if column in points.columns]
    top_shrink = points.sort_values("trapped_like_strength", ascending=False).head(limit).copy()
    top_expand = points.sort_values("anti_trapped_like_strength", ascending=False).head(limit).copy()
    top_shrink["top_kind"] = "both_shrinking"
    top_expand["top_kind"] = "both_expanding"
    combined = pd.concat([top_shrink, top_expand], ignore_index=True)
    return combined[["top_kind", *available]]


def _decision(summary: pd.DataFrame) -> str:
    watched = summary.loc[summary["scope"].isin(["packet_live", "service_live", "branch_band_live_q20"])]
    if watched.empty:
        return "undecidable_no_watched_scope"
    shrinking = int(watched["both_shrinking_rows"].sum())
    marginal = int(watched["near_marginal_rows"].sum())
    if shrinking > 0:
        return "adverse_live_trapped_like_proxy"
    if marginal > 0:
        return "watch_live_near_marginal_proxy"
    return "favorable_no_live_trapped_like_proxy"


def _markdown_report(args: argparse.Namespace, summary: pd.DataFrame, decision: str) -> str:
    lines = [
        "# Null Expansion Proxy",
        "",
        "## Purpose",
        "",
        "This diagnostic computes coordinate-time radial null areal-expansion proxies from a prescribed ADM point ledger.",
        "It uses `R = sqrt(gamma_omega)` and `theta_+/- = 2 (d_s R + v_+/- d_l R) / R`, with `v_+/- = -beta +/- alpha/sqrt(gamma_ll)`.",
        "It is a trapped-surface screen, not a theorem-level trapped-surface or global-horizon proof.",
        "",
        "## Settings",
        "",
        f"- point ledger: `{args.point_ledger}`",
        f"- label: `{args.label}`",
        f"- theta epsilon: `{args.theta_eps}`",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Scope Summary",
        "",
    ]
    display_cols = [
        "scope",
        "rows",
        "both_shrinking_rows",
        "both_expanding_rows",
        "near_marginal_rows",
        "split_expansion_rows",
        "both_shrinking_fraction",
        "both_shrinking_volume_fraction",
        "max_trapped_like_strength",
        "min_theta_plus",
        "min_theta_minus",
        "min_branch_abs_margin",
        "max_packet_norm",
    ]
    available = [column for column in display_cols if column in summary.columns]
    lines.append(summary[available].to_markdown(index=False) if not summary.empty else "_No scope rows._")
    lines.extend([
        "",
        "## Interpretation Guide",
        "",
        "`both_shrinking_rows` is the trapped-like warning proxy: both radial null areal derivatives are negative in the coordinate-time branch convention.",
        "`both_expanding_rows` is the time-reversed/anti-trapped-like companion proxy.",
        "`near_marginal_rows` marks rows where either branch expansion is within the configured epsilon of zero.",
        "The protected read is the packet/live and live branch-band scopes; support or reset-only hits should be treated as exterior source/carrier work unless they leak into live service.",
    ])
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace) -> dict[str, Path]:
    points = _prepare_points(args.point_ledger)
    diagnostics = _compute_expansion_points(points, theta_eps=float(args.theta_eps))
    masks = _scope_masks(diagnostics)
    summary = pd.DataFrame([_summarize_scope(diagnostics, scope, mask) for scope, mask in masks.items()])
    decision = _decision(summary)
    top_points = _top_points(diagnostics, int(args.top_limit))

    args.outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "points": args.outdir / "null_expansion_point_diagnostics.csv",
        "summary": args.outdir / "null_expansion_scope_summary.csv",
        "top_points": args.outdir / "null_expansion_top_points.csv",
        "report": args.outdir / "null_expansion_proxy_report.md",
        "metadata": args.outdir / "null_expansion_proxy_metadata.json",
    }
    diagnostics.to_csv(paths["points"], index=False)
    summary.to_csv(paths["summary"], index=False)
    top_points.to_csv(paths["top_points"], index=False)
    paths["report"].write_text(_markdown_report(args, summary, decision), encoding="utf-8")
    metadata = {
        "label": args.label,
        "point_ledger": str(args.point_ledger),
        "repo_commit": _git_commit(Path.cwd()),
        "theta_eps": float(args.theta_eps),
        "decision": decision,
        "rows": {
            "point_diagnostics": int(len(diagnostics)),
            "scope_summary": int(len(summary)),
            "top_points": int(len(top_points)),
        },
        "files": {key: str(path) for key, path in paths.items() if key != "metadata"},
        "caveat": (
            "Areal-expansion proxy on prescribed ADM ledger fields. This is not a "
            "full trapped-surface theorem, global event-horizon proof, or matter evolution."
        ),
    }
    paths["metadata"].write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    if args.progress:
        print(json.dumps({
            "event": "null_expansion_proxy_complete",
            "label": args.label,
            "decision": decision,
            "summary_rows": int(len(summary)),
            "point_rows": int(len(diagnostics)),
            "outdir": str(args.outdir),
        }), flush=True)
        watched = summary.loc[summary["scope"].isin(["packet_live", "service_live", "branch_band_live_q20"])]
        if not watched.empty:
            print(watched[[
                "scope",
                "rows",
                "both_shrinking_rows",
                "near_marginal_rows",
                "max_trapped_like_strength",
                "min_branch_abs_margin",
                "max_packet_norm",
            ]].to_string(index=False), flush=True)
    return paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a radial null areal-expansion proxy on a source point ledger.")
    parser.add_argument("--point-ledger", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--label", default="null_expansion_proxy")
    parser.add_argument("--theta-eps", type=float, default=1.0e-6)
    parser.add_argument("--top-limit", type=int, default=40)
    parser.add_argument("--progress", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
