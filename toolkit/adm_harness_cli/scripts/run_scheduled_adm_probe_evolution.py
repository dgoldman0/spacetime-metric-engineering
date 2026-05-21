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
SOURCE_CHANNELS = {
    "alpha": [
        "standing_support_packet_delta_alpha",
        "standing_support_packet_null_cushion_delta_alpha",
        "standing_support_packet_coupled_null_cushion_delta_alpha",
        "standing_support_packet_smooth_split_null_cushion_delta_alpha",
        "support_edge_receiver_delta_alpha",
        "support_shell_delta_alpha",
    ],
    "beta": [
        "standing_support_packet_delta_beta",
        "support_edge_receiver_delta_beta",
        "causal_margin_guard_delta_beta",
        "support_shell_delta_beta",
    ],
    "gamma_ll": [
        "standing_support_packet_delta_gamma_ll",
        "standing_support_packet_coupled_delta_gamma_ll",
        "support_edge_receiver_delta_gamma_ll",
        "support_shell_delta_gamma_ll",
    ],
    "gamma_omega": [
        "standing_support_packet_smooth_split_delta_gamma_omega",
        "support_edge_receiver_delta_gamma_omega",
        "support_shell_delta_gamma_omega",
    ],
}


def _bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def _as_float(frame: pd.DataFrame, column: str, default: float = math.nan) -> pd.Series:
    if column not in frame.columns:
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


def _pivot_text(frame: pd.DataFrame, s_axis: np.ndarray, l_axis: np.ndarray, column: str) -> np.ndarray:
    if column not in frame:
        return np.full((len(s_axis), len(l_axis)), "", dtype=object)
    return (
        frame.pivot_table(index="s", columns="l", values=column, aggfunc=lambda values: str(values.iloc[0]))
        .reindex(index=s_axis, columns=l_axis)
        .fillna("")
        .to_numpy(dtype=object)
    )


def _pivot_bool(frame: pd.DataFrame, s_axis: np.ndarray, l_axis: np.ndarray, column: str) -> np.ndarray:
    if column not in frame:
        return np.zeros((len(s_axis), len(l_axis)), dtype=bool)
    return (
        frame.pivot_table(index="s", columns="l", values=column, aggfunc="max")
        .reindex(index=s_axis, columns=l_axis)
        .fillna(False)
        .astype(bool)
        .to_numpy(dtype=bool)
    )


@dataclass
class ScheduledGrid:
    s_axis: np.ndarray
    l_axis: np.ndarray
    arrays: dict[str, np.ndarray]
    texts: dict[str, np.ndarray]
    bools: dict[str, np.ndarray]

    @property
    def step_s(self) -> float:
        return float(np.median(np.diff(self.s_axis))) if len(self.s_axis) > 1 else 1.0

    @property
    def step_l(self) -> float:
        return float(np.median(np.diff(self.l_axis))) if len(self.l_axis) > 1 else 1.0

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

    def nearest_text(self, key: str, s_value: float, l_value: float) -> str:
        values = self.texts.get(key)
        if values is None:
            return ""
        s_index = int(np.argmin(np.abs(self.s_axis - s_value)))
        l_index = int(np.argmin(np.abs(self.l_axis - l_value)))
        return str(values[s_index, l_index])

    def nearest_bool(self, key: str, s_value: float, l_value: float) -> bool:
        values = self.bools.get(key)
        if values is None:
            return False
        s_index = int(np.argmin(np.abs(self.s_axis - s_value)))
        l_index = int(np.argmin(np.abs(self.l_axis - l_value)))
        return bool(values[s_index, l_index])


def _channel_magnitude(points: pd.DataFrame, columns: list[str]) -> pd.Series:
    existing = [column for column in columns if column in points.columns]
    if not existing:
        return pd.Series(0.0, index=points.index, dtype=float)
    values = points[existing].apply(pd.to_numeric, errors="coerce").fillna(0.0).abs()
    return values.max(axis=1)


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
    points["red_tag_reset_tail_bool"] = (
        points["stage"].eq("reset_decompression")
        & points["inside_packet_geom_bool"]
        & ~points["inside_packet_live_bool"]
    )

    sqrt_gamma_ll = np.sqrt(np.maximum(points["gamma_ll"].to_numpy(dtype=float), 1.0e-30))
    alpha = points["alpha"].to_numpy(dtype=float)
    beta = points["beta"].to_numpy(dtype=float)
    points["plus_null_speed"] = -beta + alpha / sqrt_gamma_ll
    points["minus_null_speed"] = -beta - alpha / sqrt_gamma_ll
    points["branch_abs_margin"] = np.minimum(points["plus_null_speed"].abs(), points["minus_null_speed"].abs())
    points["g_sigma_sigma"] = -points["alpha"] * points["alpha"] + points["gamma_ll"] * points["beta"] * points["beta"]
    points["gtt"] = _as_float(points, "gtt").fillna(points["g_sigma_sigma"])
    points["areal_radius"] = np.sqrt(np.maximum(points["gamma_omega"].to_numpy(dtype=float), 0.0))
    points["packet_coord_speed"] = _as_float(points, "U_packet", 0.0) / np.maximum(_as_float(points, "B", 1.0), 1.0e-12)
    computed_packet_norm = -points["alpha"] * points["alpha"] + points["gamma_ll"] * (
        points["packet_coord_speed"] + points["beta"]
    ) ** 2
    points["packet_norm"] = _as_float(points, "packet_norm").fillna(computed_packet_norm)
    points["cond_metric"] = _as_float(points, "cond_metric")
    points["ricci_scalar"] = _as_float(points, "ricci_scalar")
    for name, columns in SOURCE_CHANNELS.items():
        points[f"{name}_channel_abs"] = _channel_magnitude(points, columns)
    return points


def _build_grid(points: pd.DataFrame) -> ScheduledGrid:
    s_axis = np.array(sorted(points["s"].dropna().unique()), dtype=float)
    l_axis = np.array(sorted(points["l"].dropna().unique()), dtype=float)
    arrays = {
        column: _pivot_float(points, s_axis, l_axis, column)
        for column in [
            "alpha",
            "beta",
            "gamma_ll",
            "gamma_omega",
            "areal_radius",
            "packet_norm",
            "packet_coord_speed",
            "plus_null_speed",
            "minus_null_speed",
            "branch_abs_margin",
            "gtt",
            "cond_metric",
            "ricci_scalar",
            "alpha_channel_abs",
            "beta_channel_abs",
            "gamma_ll_channel_abs",
            "gamma_omega_channel_abs",
        ]
    }
    texts = {
        "stage": _pivot_text(points, s_axis, l_axis, "stage"),
        "region": _pivot_text(points, s_axis, l_axis, "region"),
    }
    bools = {
        "inside_packet_live": _pivot_bool(points, s_axis, l_axis, "inside_packet_live_bool"),
        "inside_packet_geom": _pivot_bool(points, s_axis, l_axis, "inside_packet_geom_bool"),
        "red_tag_reset_tail": _pivot_bool(points, s_axis, l_axis, "red_tag_reset_tail_bool"),
    }
    return ScheduledGrid(s_axis=s_axis, l_axis=l_axis, arrays=arrays, texts=texts, bools=bools)


def _branch_band_mask(points: pd.DataFrame) -> pd.Series:
    live = points.loc[points["inside_packet_live_bool"], "branch_abs_margin"]
    if live.empty:
        return pd.Series(False, index=points.index)
    cutoff = float(live.quantile(0.20))
    return points["inside_packet_live_bool"] & (points["branch_abs_margin"] <= cutoff)


def _select_quantile_rows(candidates: pd.DataFrame, count: int, *, prefer_high_l: bool = False) -> pd.DataFrame:
    if candidates.empty:
        return pd.DataFrame()
    rows: list[pd.Series] = []
    quantiles = np.linspace(0.10, 0.90, max(1, int(count)))
    for quantile in quantiles:
        target = float(candidates["s"].quantile(quantile))
        near = candidates.assign(_s_distance=(candidates["s"] - target).abs())
        sort_cols = ["_s_distance", "branch_abs_margin", "l"]
        ascending = [True, True, not prefer_high_l]
        rows.append(near.sort_values(sort_cols, ascending=ascending).iloc[0])
    out = pd.DataFrame(rows).drop_duplicates(subset=["s", "l", "stage", "region"]).copy()
    return out.head(max(1, int(count))).copy()


def _build_seeds(points: pd.DataFrame, grid: ScheduledGrid, seeds_per_family: int, red_tag_seeds: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    def add_rows(frame: pd.DataFrame, family: str, branch: str, angular_fraction: float = 0.0) -> None:
        for _, row in frame.iterrows():
            rows.append({
                "probe_family": family,
                "branch": branch,
                "seed_s": float(row["s"]),
                "seed_l": float(row["l"]),
                "seed_stage": str(row["stage"]),
                "seed_region": str(row["region"]),
                "seed_inside_packet_live": bool(row["inside_packet_live_bool"]),
                "seed_inside_packet_geom": bool(row["inside_packet_geom_bool"]),
                "seed_red_tag_reset_tail": bool(row["red_tag_reset_tail_bool"]),
                "seed_branch_abs_margin": float(row["branch_abs_margin"]),
                "angular_fraction": float(angular_fraction),
                "bundle_id": "",
            })

    live = points.loc[points["inside_packet_live_bool"]].copy()
    add_rows(_select_quantile_rows(live, seeds_per_family), "packet_centerline", "packet")

    tube = points.loc[points["inside_packet_geom_bool"] & ~points["inside_packet_live_bool"]].copy()
    add_rows(_select_quantile_rows(tube, seeds_per_family, prefer_high_l=True), "packet_tube_edge", "packet")

    branch_band = points.loc[_branch_band_mask(points)].copy()
    radial = branch_band.sort_values(["branch_abs_margin", "s", "l"]).head(max(1, seeds_per_family)).copy()
    add_rows(radial, "radial_null_branch_band", "plus")
    add_rows(radial, "radial_null_branch_band", "minus")
    add_rows(radial, "offaxis_null_branch_band", "offaxis_plus", angular_fraction=0.35)
    add_rows(radial, "offaxis_null_branch_band", "offaxis_minus", angular_fraction=0.35)

    core_bundle = branch_band.sort_values(["branch_abs_margin", "s", "l"]).head(5).copy()
    offsets = [-2, -1, 0, 1, 2]
    for bundle_index, (_, seed) in enumerate(core_bundle.iterrows()):
        for offset in offsets:
            l_value = float(np.clip(float(seed["l"]) + offset * grid.step_l, grid.l_axis[0], grid.l_axis[-1]))
            for branch in ["plus", "minus"]:
                rows.append({
                    "probe_family": "congruence_branch_band",
                    "branch": branch,
                    "seed_s": float(seed["s"]),
                    "seed_l": l_value,
                    "seed_stage": str(seed["stage"]),
                    "seed_region": str(seed["region"]),
                    "seed_inside_packet_live": True,
                    "seed_inside_packet_geom": True,
                    "seed_red_tag_reset_tail": False,
                    "seed_branch_abs_margin": float(seed["branch_abs_margin"]),
                    "angular_fraction": 0.0,
                    "bundle_id": f"bundle_{bundle_index:02d}_{branch}",
                })

    red_tag = points.loc[points["red_tag_reset_tail_bool"] & (points["l"].astype(float) > 0.0)].copy()
    red_tag = _select_quantile_rows(red_tag, red_tag_seeds, prefer_high_l=True)
    add_rows(red_tag, "red_tag_reset_tail", "minus")

    seeds = pd.DataFrame(rows).drop_duplicates(
        subset=["probe_family", "branch", "seed_s", "seed_l", "bundle_id"],
    ).copy()
    seeds["seed_index"] = range(len(seeds))
    return seeds


def _speed_for_probe(grid: ScheduledGrid, branch: str, s_value: float, l_value: float, angular_fraction: float) -> float:
    if branch == "packet":
        return grid.interp("packet_coord_speed", s_value, l_value)
    if branch == "plus":
        return grid.interp("plus_null_speed", s_value, l_value)
    if branch == "minus":
        return grid.interp("minus_null_speed", s_value, l_value)
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


def _trace_probe(grid: ScheduledGrid, seed: pd.Series, *, step_scale: float, max_steps: int) -> dict[str, Any]:
    ds = max(grid.step_s * float(step_scale), 1.0e-8)
    branch = str(seed["branch"])
    angular_fraction = float(seed.get("angular_fraction", 0.0))
    s_value = float(seed["seed_s"])
    l_value = float(seed["seed_l"])
    l_start = float(l_value)
    min_branch_margin = math.inf
    min_packet_norm = math.inf
    max_packet_norm = -math.inf
    min_theta_proxy = math.inf
    max_theta_proxy = -math.inf
    max_abs_ricci = 0.0
    max_cond_metric = 0.0
    source_max = {name: 0.0 for name in SOURCE_CHANNELS}
    entered_live_packet = bool(seed.get("seed_inside_packet_live", False))
    touched_red_tag = bool(seed.get("seed_red_tag_reset_tail", False))
    branch_sign_changes = 0
    previous_speed = math.nan
    previous_radius = grid.interp("areal_radius", s_value, l_value)
    outcome = "max_steps"
    samples = 0

    for _ in range(max_steps):
        if not grid.in_bounds(s_value, l_value):
            outcome = "out_of_bounds"
            break
        speed = _speed_for_probe(grid, branch, s_value, l_value, angular_fraction)
        margin = grid.interp("branch_abs_margin", s_value, l_value)
        packet_norm = grid.interp("packet_norm", s_value, l_value)
        radius = grid.interp("areal_radius", s_value, l_value)
        if not all(math.isfinite(value) for value in [speed, margin, packet_norm, radius]):
            outcome = "invalid_metric"
            break
        if math.isfinite(previous_speed) and previous_speed * speed < 0.0:
            branch_sign_changes += 1
        previous_speed = speed
        min_branch_margin = min(min_branch_margin, abs(margin))
        min_packet_norm = min(min_packet_norm, packet_norm)
        max_packet_norm = max(max_packet_norm, packet_norm)
        if math.isfinite(previous_radius) and previous_radius > 0.0 and radius > 0.0:
            theta = (math.log(radius) - math.log(previous_radius)) / ds
            min_theta_proxy = min(min_theta_proxy, theta)
            max_theta_proxy = max(max_theta_proxy, theta)
        previous_radius = radius
        ricci = grid.interp("ricci_scalar", s_value, l_value)
        cond = grid.interp("cond_metric", s_value, l_value)
        if math.isfinite(ricci):
            max_abs_ricci = max(max_abs_ricci, abs(ricci))
        if math.isfinite(cond):
            max_cond_metric = max(max_cond_metric, abs(cond))
        for name in SOURCE_CHANNELS:
            value = grid.interp(f"{name}_channel_abs", s_value, l_value)
            if math.isfinite(value):
                source_max[name] = max(source_max[name], abs(value))
        entered_live_packet = entered_live_packet or grid.nearest_bool("inside_packet_live", s_value, l_value)
        touched_red_tag = touched_red_tag or grid.nearest_bool("red_tag_reset_tail", s_value, l_value)

        mid_s = s_value + 0.5 * ds
        mid_l = l_value + 0.5 * speed * ds
        mid_speed = _speed_for_probe(grid, branch, mid_s, mid_l, angular_fraction)
        if not math.isfinite(mid_speed):
            mid_speed = speed
        next_s = s_value + ds
        next_l = l_value + mid_speed * ds
        samples += 1
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

    if not math.isfinite(min_branch_margin):
        min_branch_margin = math.nan
    if not math.isfinite(min_packet_norm):
        min_packet_norm = math.nan
    if not math.isfinite(max_packet_norm):
        max_packet_norm = math.nan
    if not math.isfinite(min_theta_proxy):
        min_theta_proxy = math.nan
    if not math.isfinite(max_theta_proxy):
        max_theta_proxy = math.nan

    return {
        "probe_family": str(seed["probe_family"]),
        "branch": branch,
        "seed_index": int(seed["seed_index"]),
        "bundle_id": str(seed.get("bundle_id", "")),
        "seed_s": float(seed["seed_s"]),
        "seed_l": float(seed["seed_l"]),
        "seed_stage": str(seed["seed_stage"]),
        "seed_region": str(seed["seed_region"]),
        "seed_inside_packet_live": bool(seed["seed_inside_packet_live"]),
        "seed_inside_packet_geom": bool(seed["seed_inside_packet_geom"]),
        "seed_red_tag_reset_tail": bool(seed["seed_red_tag_reset_tail"]),
        "seed_branch_abs_margin": float(seed["seed_branch_abs_margin"]),
        "angular_fraction": angular_fraction,
        "trace_outcome": outcome,
        "escaped_any_radial_boundary": outcome in {"l_lower_boundary", "l_upper_boundary"},
        "s_upper_boundary": outcome == "s_upper_boundary",
        "invalid_or_stalled": outcome in {"invalid_metric", "out_of_bounds", "max_steps"},
        "trace_samples": int(samples),
        "final_s": float(s_value),
        "final_l": float(l_value),
        "final_stage": grid.nearest_text("stage", s_value, l_value),
        "final_region": grid.nearest_text("region", s_value, l_value),
        "delta_l": float(l_value - l_start),
        "entered_live_packet": bool(entered_live_packet),
        "touched_red_tag_reset_tail": bool(touched_red_tag),
        "min_branch_abs_margin_along_trace": float(min_branch_margin),
        "branch_sign_changes_along_trace": int(branch_sign_changes),
        "min_packet_norm_along_trace": float(min_packet_norm),
        "max_packet_norm_along_trace": float(max_packet_norm),
        "min_areal_expansion_proxy": float(min_theta_proxy),
        "max_areal_expansion_proxy": float(max_theta_proxy),
        "max_abs_ricci_scalar_along_trace": float(max_abs_ricci),
        "max_cond_metric_along_trace": float(max_cond_metric),
        **{f"max_{name}_channel_abs_along_trace": float(value) for name, value in source_max.items()},
    }


def _summarize_traces(traces: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (family, branch), group in traces.groupby(["probe_family", "branch"], sort=False):
        rows.append({
            "probe_family": family,
            "branch": branch,
            "traces": int(len(group)),
            "radial_escape_count": int(group["escaped_any_radial_boundary"].sum()),
            "s_upper_boundary_count": int(group["s_upper_boundary"].sum()),
            "invalid_or_stalled_count": int(group["invalid_or_stalled"].sum()),
            "entered_live_packet_count": int(group["entered_live_packet"].sum()),
            "touched_red_tag_count": int(group["touched_red_tag_reset_tail"].sum()),
            "min_branch_abs_margin": float(group["min_branch_abs_margin_along_trace"].min()),
            "branch_sign_changes": int(group["branch_sign_changes_along_trace"].sum()),
            "min_packet_norm": float(group["min_packet_norm_along_trace"].min()),
            "max_packet_norm": float(group["max_packet_norm_along_trace"].max()),
            "min_areal_expansion_proxy": float(group["min_areal_expansion_proxy"].min()),
            "max_areal_expansion_proxy": float(group["max_areal_expansion_proxy"].max()),
            "max_abs_ricci_scalar": float(group["max_abs_ricci_scalar_along_trace"].max()),
            "max_cond_metric": float(group["max_cond_metric_along_trace"].max()),
            "max_alpha_channel_abs": float(group["max_alpha_channel_abs_along_trace"].max()),
            "max_beta_channel_abs": float(group["max_beta_channel_abs_along_trace"].max()),
            "max_gamma_ll_channel_abs": float(group["max_gamma_ll_channel_abs_along_trace"].max()),
            "max_gamma_omega_channel_abs": float(group["max_gamma_omega_channel_abs_along_trace"].max()),
            "outcome_counts": ";".join(
                f"{name}:{int(count)}" for name, count in group["trace_outcome"].value_counts().sort_index().items()
            ),
        })
    return pd.DataFrame(rows)


def _bundle_summary(traces: pd.DataFrame) -> pd.DataFrame:
    bundle = traces.loc[traces["bundle_id"].astype(str).ne("")].copy()
    if bundle.empty:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for bundle_id, group in bundle.groupby("bundle_id", sort=False):
        initial_width = float(group["seed_l"].max() - group["seed_l"].min())
        final_width = float(group["final_l"].max() - group["final_l"].min())
        rows.append({
            "bundle_id": bundle_id,
            "branch": str(group["branch"].iloc[0]),
            "traces": int(len(group)),
            "initial_l_width": initial_width,
            "final_l_width": final_width,
            "width_ratio": final_width / initial_width if initial_width > 0.0 else math.nan,
            "s_upper_boundary_count": int(group["s_upper_boundary"].sum()),
            "radial_escape_count": int(group["escaped_any_radial_boundary"].sum()),
            "min_areal_expansion_proxy": float(group["min_areal_expansion_proxy"].min()),
            "max_areal_expansion_proxy": float(group["max_areal_expansion_proxy"].max()),
        })
    return pd.DataFrame(rows)


def _red_tag_summary(traces: pd.DataFrame) -> pd.DataFrame:
    red = traces.loc[traces["probe_family"].eq("red_tag_reset_tail")].copy()
    if red.empty:
        return pd.DataFrame()
    return pd.DataFrame([{
        "probe_family": "red_tag_reset_tail",
        "traces": int(len(red)),
        "l_lower_boundary": int(red["trace_outcome"].eq("l_lower_boundary").sum()),
        "l_upper_boundary": int(red["trace_outcome"].eq("l_upper_boundary").sum()),
        "s_upper_boundary": int(red["trace_outcome"].eq("s_upper_boundary").sum()),
        "invalid_or_stalled": int(red["invalid_or_stalled"].sum()),
        "entered_live_packet": int(red["entered_live_packet"].sum()),
        "min_final_l": float(red["final_l"].min()),
        "max_final_l": float(red["final_l"].max()),
        "min_seed_s": float(red["seed_s"].min()),
        "max_seed_s": float(red["seed_s"].max()),
        "min_seed_l": float(red["seed_l"].min()),
        "max_seed_l": float(red["seed_l"].max()),
    }])


def _markdown_report(
    summary: pd.DataFrame,
    red_tag: pd.DataFrame,
    bundle: pd.DataFrame,
    args: argparse.Namespace,
) -> str:
    lines = [
        "# Scheduled ADM Probe Evolution Pilot",
        "",
        "## Purpose",
        "",
        "This is a semi-dynamical audit of the promoted beta075 `p003_mid` service program. "
        "It prescribes the ledger metric fields `alpha`, `beta`, `gamma_ll`, and `gamma_omega`, "
        "then evolves probe families through that scheduled geometry. It is not a matter evolution "
        "or a full Einstein evolution.",
        "",
        "## Settings",
        "",
        f"- point ledger: `{args.point_ledger}`",
        f"- label: `{args.label}`",
        f"- seeds per family: `{args.seeds_per_family}`",
        f"- red-tag seeds: `{args.red_tag_seeds}`",
        f"- trace step scale: `{args.trace_step_scale}`",
        f"- max steps: `{args.max_steps}`",
        f"- off-axis angular fraction: `{args.angular_fraction}`",
        "",
        "## Probe Summary",
        "",
    ]
    display_cols = [
        "probe_family",
        "branch",
        "traces",
        "radial_escape_count",
        "s_upper_boundary_count",
        "invalid_or_stalled_count",
        "entered_live_packet_count",
        "touched_red_tag_count",
        "min_branch_abs_margin",
        "branch_sign_changes",
        "min_packet_norm",
        "max_packet_norm",
        "min_areal_expansion_proxy",
        "max_areal_expansion_proxy",
        "outcome_counts",
    ]
    lines.append(summary[display_cols].to_markdown(index=False) if not summary.empty else "_No probe traces._")
    lines.append("")
    lines.append("## Red Tag Monitor")
    lines.append("")
    if red_tag.empty:
        lines.append("_No red-tag reset-decompression tails were selected._")
    else:
        lines.append(red_tag.to_markdown(index=False))
    lines.append("")
    lines.append("## Congruence Bundle Proxy")
    lines.append("")
    if bundle.empty:
        lines.append("_No congruence bundle traces were selected._")
    else:
        lines.append(bundle.to_markdown(index=False))
    lines.append("")
    lines.append("## Limits")
    lines.append("")
    lines.append(
        "Packet centerline and tube-edge probes follow the prescribed packet coordinate speed from the ledger. "
        "Radial and off-axis null probes use the ADM null speeds implied by the prescribed metric. "
        "The areal-expansion values are finite-difference proxies along sampled probes, not theorem-level "
        "trapped-surface diagnostics."
    )
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a scheduled ADM probe evolution audit on a point ledger.")
    parser.add_argument("--point-ledger", type=Path, required=True)
    parser.add_argument("--label", default="scheduled_adm_probe")
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--seeds-per-family", type=int, default=24)
    parser.add_argument("--red-tag-seeds", type=int, default=80)
    parser.add_argument("--trace-step-scale", type=float, default=0.5)
    parser.add_argument("--max-steps", type=int, default=8000)
    parser.add_argument("--angular-fraction", type=float, default=0.35)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    started_at = time.perf_counter()
    points = _prepare_points(args.point_ledger)
    grid = _build_grid(points)
    seeds = _build_seeds(points, grid, max(1, args.seeds_per_family), max(1, args.red_tag_seeds))
    if not seeds.empty:
        seeds.loc[seeds["probe_family"].eq("offaxis_null_branch_band"), "angular_fraction"] = float(args.angular_fraction)
    traces = pd.DataFrame([
        _trace_probe(
            grid,
            seed,
            step_scale=max(float(args.trace_step_scale), 1.0e-8),
            max_steps=max(1, int(args.max_steps)),
        )
        for _, seed in seeds.iterrows()
    ])
    summary = _summarize_traces(traces)
    red_tag = _red_tag_summary(traces)
    bundle = _bundle_summary(traces)

    args.outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "seeds": args.outdir / "scheduled_adm_probe_seeds.csv",
        "traces": args.outdir / "scheduled_adm_probe_traces.csv",
        "summary": args.outdir / "scheduled_adm_probe_summary.csv",
        "red_tag": args.outdir / "scheduled_adm_probe_red_tag.csv",
        "bundle": args.outdir / "scheduled_adm_probe_bundle_summary.csv",
        "report": args.outdir / "scheduled_adm_probe_report.md",
        "metadata": args.outdir / "scheduled_adm_probe_metadata.json",
    }
    seeds.to_csv(paths["seeds"], index=False)
    traces.to_csv(paths["traces"], index=False)
    summary.to_csv(paths["summary"], index=False)
    red_tag.to_csv(paths["red_tag"], index=False)
    bundle.to_csv(paths["bundle"], index=False)
    paths["report"].write_text(_markdown_report(summary, red_tag, bundle, args), encoding="utf-8")

    repo_root = Path(__file__).resolve().parents[3]
    elapsed_s = round(time.perf_counter() - started_at, 3)
    paths["metadata"].write_text(
        json.dumps(
            {
                "label": args.label,
                "point_ledger": str(args.point_ledger),
                "seeds_per_family": args.seeds_per_family,
                "red_tag_seeds": args.red_tag_seeds,
                "trace_step_scale": args.trace_step_scale,
                "max_steps": args.max_steps,
                "angular_fraction": args.angular_fraction,
                "rows": {
                    "points": int(len(points)),
                    "seeds": int(len(seeds)),
                    "traces": int(len(traces)),
                },
                "commit": _git_commit(repo_root),
                "elapsed_s": elapsed_s,
                "files": {key: str(path) for key, path in paths.items() if key != "metadata"},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    red_unresolved = int(red_tag["s_upper_boundary"].iloc[0]) if not red_tag.empty else 0
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "traces": int(len(traces)),
        "red_tag_s_upper_boundary": red_unresolved,
        "elapsed_s": elapsed_s,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
