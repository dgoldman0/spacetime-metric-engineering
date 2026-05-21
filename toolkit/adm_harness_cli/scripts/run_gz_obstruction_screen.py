from __future__ import annotations

import argparse
import json
import math
import subprocess
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SUPPORT_PLANT_REGIONS = {"core_throat", "support_edge", "outer_quarantine_shell"}
MAIN_SUPPORT_REGIONS = {"core_throat", "support_edge"}
WINDOW_COLUMNS = [
    "support_shell_window",
    "support_edge_receiver_memory_driver",
    "support_edge_receiver_radial_cap_window",
    "support_edge_receiver_angular_flange_window",
    "standing_support_packet_smooth_split_edge_window",
    "standing_support_packet_smooth_split_guarded_edge_window",
    "standing_support_packet_smooth_split_angular_window",
    "standing_support_packet_smooth_split_current_guard_window",
    "standing_support_packet_beta_rematch_window",
]
SLOPE_COLUMNS = [
    "release_profile_slope_abs",
    "support_edge_receiver_radial_cap_window_slope_abs",
    "support_edge_receiver_angular_flange_window_slope_abs",
    "standing_support_packet_smooth_split_edge_window_slope_abs",
    "standing_support_packet_smooth_split_guarded_edge_window_slope_abs",
    "standing_support_packet_smooth_split_angular_window_slope_abs",
    "standing_support_packet_smooth_split_current_guard_window_slope_abs",
    "standing_support_packet_beta_rematch_window_slope_abs",
]


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


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


def _safe_abs_max(frame: pd.DataFrame, columns: list[str]) -> pd.Series:
    existing = [column for column in columns if column in frame.columns]
    if not existing:
        return pd.Series(0.0, index=frame.index)
    values = frame[existing].apply(pd.to_numeric, errors="coerce").fillna(0.0).abs()
    return values.max(axis=1)


def _as_float(frame: pd.DataFrame, column: str, default: float = math.nan) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(default, index=frame.index, dtype=float)
    return pd.to_numeric(frame[column], errors="coerce").astype(float)


def _gradient_by_stage(frame: pd.DataFrame, value_col: str, gradient_col: str, axis: str) -> pd.Series:
    out = pd.Series(np.nan, index=frame.index, dtype=float)
    if value_col not in frame.columns:
        return out
    for _, group in frame.groupby("stage", sort=False):
        pivot = group.pivot_table(index="s", columns="l", values=value_col, aggfunc="mean")
        if pivot.shape[0] < 2 or pivot.shape[1] < 2:
            continue
        s_axis = pivot.index.to_numpy(dtype=float)
        l_axis = pivot.columns.to_numpy(dtype=float)
        values = pivot.to_numpy(dtype=float)
        if axis == "s":
            grad = np.gradient(values, s_axis, axis=0, edge_order=1)
        elif axis == "l":
            grad = np.gradient(values, l_axis, axis=1, edge_order=1)
        else:
            raise ValueError(f"unknown gradient axis {axis!r}")
        grad_frame = pd.DataFrame(grad, index=pivot.index, columns=pivot.columns)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            long = grad_frame.stack(dropna=False).rename(gradient_col).reset_index()
        merged = group[["s", "l"]].merge(long, on=["s", "l"], how="left")
        out.loc[group.index] = merged[gradient_col].to_numpy(dtype=float)
    return out


@dataclass
class StageGrid:
    s_axis: np.ndarray
    l_axis: np.ndarray
    arrays: dict[str, np.ndarray]

    def interp(self, key: str, s_value: float, l_value: float) -> float:
        if key not in self.arrays:
            return math.nan
        if (
            s_value < self.s_axis[0]
            or s_value > self.s_axis[-1]
            or l_value < self.l_axis[0]
            or l_value > self.l_axis[-1]
        ):
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
        v00 = arr[s_lo, l_lo]
        v01 = arr[s_lo, l_hi]
        v10 = arr[s_hi, l_lo]
        v11 = arr[s_hi, l_hi]
        if not all(math.isfinite(float(v)) for v in [v00, v01, v10, v11]):
            return math.nan
        return float((1.0 - ws) * (1.0 - wl) * v00 + (1.0 - ws) * wl * v01 + ws * (1.0 - wl) * v10 + ws * wl * v11)


def _build_stage_grids(points: pd.DataFrame) -> dict[str, StageGrid]:
    grids: dict[str, StageGrid] = {}
    value_cols = ["alpha", "beta", "gamma_ll", "plus_null_speed", "minus_null_speed", "branch_abs_margin"]
    for stage, group in points.groupby("stage", sort=False):
        pivots: dict[str, pd.DataFrame] = {}
        for col in value_cols:
            pivots[col] = group.pivot_table(index="s", columns="l", values=col, aggfunc="mean")
        first = pivots[value_cols[0]]
        if first.shape[0] < 2 or first.shape[1] < 2:
            continue
        arrays = {key: pivot.reindex(index=first.index, columns=first.columns).to_numpy(dtype=float) for key, pivot in pivots.items()}
        grids[str(stage)] = StageGrid(
            s_axis=first.index.to_numpy(dtype=float),
            l_axis=first.columns.to_numpy(dtype=float),
            arrays=arrays,
        )
    return grids


def _trace_branch(
    grid: StageGrid,
    seed_s: float,
    seed_l: float,
    branch: str,
    *,
    max_steps: int = 400,
    step_s: float | None = None,
) -> dict[str, Any]:
    if branch not in {"plus", "minus"}:
        raise ValueError(f"unknown branch {branch!r}")
    if step_s is None:
        step_s = float(np.median(np.diff(grid.s_axis))) if len(grid.s_axis) > 1 else 1.0
    s_value = float(seed_s)
    l_value = float(seed_l)
    l_start = float(seed_l)
    min_speed_abs = math.inf
    samples = 0
    outcome = "max_steps"
    for _ in range(max_steps):
        speed = grid.interp(f"{branch}_null_speed", s_value, l_value)
        margin = grid.interp("branch_abs_margin", s_value, l_value)
        if not math.isfinite(speed) or not math.isfinite(margin):
            outcome = "invalid_metric"
            break
        min_speed_abs = min(min_speed_abs, abs(speed), abs(margin))
        next_s = s_value + step_s
        next_l = l_value + speed * step_s
        samples += 1
        if next_l <= grid.l_axis[0]:
            outcome = "l_lower_boundary"
            l_value = float(grid.l_axis[0])
            s_value = next_s
            break
        if next_l >= grid.l_axis[-1]:
            outcome = "l_upper_boundary"
            l_value = float(grid.l_axis[-1])
            s_value = next_s
            break
        if next_s > grid.s_axis[-1]:
            outcome = "s_upper_boundary"
            s_value = float(grid.s_axis[-1])
            l_value = next_l
            break
        s_value = next_s
        l_value = next_l
    if not math.isfinite(min_speed_abs):
        min_speed_abs = math.nan
    expected_escape = "l_upper_boundary" if branch == "plus" else "l_lower_boundary"
    return {
        "branch": branch,
        "trace_outcome": outcome,
        "expected_escape_boundary": expected_escape,
        "escaped_expected_side": outcome == expected_escape,
        "trace_samples": samples,
        "seed_s": float(seed_s),
        "seed_l": float(seed_l),
        "final_s": float(s_value),
        "final_l": float(l_value),
        "delta_l": float(l_value - l_start),
        "min_abs_speed_along_trace": float(min_speed_abs),
    }


def _annotate_points(points: pd.DataFrame, label: str, shell_threshold: float) -> pd.DataFrame:
    required = {"s", "l", "stage", "region", "alpha", "beta", "gamma_ll", "gamma_omega"}
    missing = sorted(required - set(points.columns))
    if missing:
        raise ValueError(f"{label} point ledger is missing required columns: {missing}")
    out = points.copy()
    out["label"] = label
    out["s"] = pd.to_numeric(out["s"], errors="coerce").astype(float)
    out["l"] = pd.to_numeric(out["l"], errors="coerce").astype(float)
    out["alpha"] = _as_float(out, "alpha")
    out["beta"] = _as_float(out, "beta")
    out["gamma_ll"] = _as_float(out, "gamma_ll")
    out["gamma_omega"] = _as_float(out, "gamma_omega")
    sqrt_gamma_ll = np.sqrt(np.maximum(out["gamma_ll"].to_numpy(dtype=float), 0.0))
    alpha = out["alpha"].to_numpy(dtype=float)
    beta = out["beta"].to_numpy(dtype=float)
    out["plus_null_speed"] = -beta + alpha / sqrt_gamma_ll
    out["minus_null_speed"] = -beta - alpha / sqrt_gamma_ll
    out["branch_abs_margin"] = np.minimum(out["plus_null_speed"].abs(), out["minus_null_speed"].abs())
    out["g_sigma_sigma"] = -out["alpha"] * out["alpha"] + out["gamma_ll"] * out["beta"] * out["beta"]
    if "gtt" not in out.columns:
        out["gtt"] = out["g_sigma_sigma"]
    out["gtt"] = _as_float(out, "gtt")
    out["areal_radius"] = np.sqrt(np.maximum(out["gamma_omega"].to_numpy(dtype=float), 0.0))
    out["cond_metric"] = _as_float(out, "cond_metric")
    out["ricci_scalar"] = _as_float(out, "ricci_scalar")
    out["abs_ricci_scalar"] = out["ricci_scalar"].abs()
    out["inside_packet_live_bool"] = _bool_series(out["inside_packet_live"]) if "inside_packet_live" in out.columns else False
    out["inside_packet_geom_bool"] = _bool_series(out["inside_packet_geom"]) if "inside_packet_geom" in out.columns else False
    out["support_plant_bool"] = out["region"].astype(str).isin(SUPPORT_PLANT_REGIONS)
    out["main_support_bool"] = out["region"].astype(str).isin(MAIN_SUPPORT_REGIONS)
    out["window_intensity"] = _safe_abs_max(out, WINDOW_COLUMNS)
    out["slope_intensity"] = _safe_abs_max(out, SLOPE_COLUMNS)
    out["active_interpolation_bool"] = (
        (out["window_intensity"] > shell_threshold)
        | (out["slope_intensity"] > shell_threshold)
        | out["support_plant_bool"]
    )
    out["d_l_areal_radius"] = _gradient_by_stage(out, "areal_radius", "d_l_areal_radius", "l")
    out["d2_l_areal_radius"] = _gradient_by_stage(out.assign(d_l_areal_radius=out["d_l_areal_radius"]), "d_l_areal_radius", "d2_l_areal_radius", "l")
    out["d_l_gamma_ll"] = _gradient_by_stage(out, "gamma_ll", "d_l_gamma_ll", "l")
    out["d_s_gamma_ll"] = _gradient_by_stage(out, "gamma_ll", "d_s_gamma_ll", "s")
    out["d_l_beta"] = _gradient_by_stage(out, "beta", "d_l_beta", "l")
    out["d_s_beta"] = _gradient_by_stage(out, "beta", "d_s_beta", "s")
    radius = out["areal_radius"].replace([np.inf, -np.inf], np.nan)
    low_radius_cut = radius.quantile(0.10)
    if not math.isfinite(float(low_radius_cut)):
        low_radius_cut = float(radius.min()) if len(radius) else math.nan
    radius_scale = max(float(radius.max() - radius.min()) if len(radius) else 0.0, 1.0e-12)
    throat_low_radius = np.clip((float(radius.max()) - radius) / radius_scale, 0.0, 1.0)
    low_slope_scale = max(float(out["d_l_areal_radius"].abs().quantile(0.90)), 1.0e-12)
    throat_low_slope = 1.0 / (1.0 + out["d_l_areal_radius"].abs() / low_slope_scale)
    curvature_scale = max(float(out["d2_l_areal_radius"].abs().quantile(0.90)), 1.0e-12)
    throat_curvature = np.clip(out["d2_l_areal_radius"].abs() / curvature_scale, 0.0, 4.0)
    out["throat_proxy"] = throat_low_radius * throat_low_slope * (1.0 + throat_curvature)
    out["low_areal_radius_bool"] = out["areal_radius"] <= low_radius_cut
    shape_score = (
        out["slope_intensity"]
        + out["d_l_beta"].abs()
        + out["d_s_beta"].abs()
        + out["d_l_gamma_ll"].abs() / np.maximum(out["gamma_ll"].abs(), 1.0e-12)
        + out["d_s_gamma_ll"].abs() / np.maximum(out["gamma_ll"].abs(), 1.0e-12)
    )
    out["gz_overlap_score"] = out["window_intensity"] * out["throat_proxy"] * (1.0 + shape_score)
    return out


def _mask_summary(points: pd.DataFrame, label: str, scope: str, mask: pd.Series, branch_eps: float) -> dict[str, Any]:
    group = points.loc[mask].copy()
    row: dict[str, Any] = {"label": label, "scope": scope, "rows": int(len(group))}
    if group.empty:
        row.update({
            "min_plus_null_speed": math.nan,
            "max_minus_null_speed": math.nan,
            "min_branch_abs_margin": math.nan,
            "plus_nonpositive_points": 0,
            "minus_nonnegative_points": 0,
            "near_branch_zero_points": 0,
            "same_sign_branch_points": 0,
            "gtt_nonnegative_points": 0,
            "max_gtt": math.nan,
            "min_alpha": math.nan,
            "max_gamma_ll": math.nan,
            "max_cond_metric": math.nan,
            "max_abs_ricci_scalar": math.nan,
            "max_gz_overlap_score": math.nan,
        })
        return row
    plus = group["plus_null_speed"].astype(float)
    minus = group["minus_null_speed"].astype(float)
    margin = group["branch_abs_margin"].astype(float)
    row.update({
        "min_plus_null_speed": float(plus.min()),
        "max_minus_null_speed": float(minus.max()),
        "min_branch_abs_margin": float(margin.min()),
        "plus_nonpositive_points": int((plus <= branch_eps).sum()),
        "minus_nonnegative_points": int((minus >= -branch_eps).sum()),
        "near_branch_zero_points": int((margin <= branch_eps).sum()),
        "same_sign_branch_points": int((plus * minus > 0.0).sum()),
        "gtt_nonnegative_points": int((group["gtt"].astype(float) >= 0.0).sum()),
        "max_gtt": float(group["gtt"].astype(float).max()),
        "min_alpha": float(group["alpha"].astype(float).min()),
        "max_gamma_ll": float(group["gamma_ll"].astype(float).max()),
        "max_cond_metric": float(group["cond_metric"].astype(float).replace([np.inf, -np.inf], np.nan).max()),
        "max_abs_ricci_scalar": float(group["abs_ricci_scalar"].astype(float).replace([np.inf, -np.inf], np.nan).max()),
        "max_gz_overlap_score": float(group["gz_overlap_score"].astype(float).replace([np.inf, -np.inf], np.nan).max()),
    })
    return row


def _edge_crossings_for_scope(points: pd.DataFrame, mask: pd.Series) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for branch, value_col in [("plus", "plus_null_speed"), ("minus", "minus_null_speed")]:
        crossing_edges = 0
        min_endpoint_abs = math.inf
        for _, group in points.assign(_scope_mask=mask).groupby("stage", sort=False):
            values = group.pivot_table(index="s", columns="l", values=value_col, aggfunc="mean")
            scope = group.pivot_table(index="s", columns="l", values="_scope_mask", aggfunc="max")
            scope = scope.reindex(index=values.index, columns=values.columns).fillna(False).astype(bool)
            value_arr = values.to_numpy(dtype=float)
            scope_arr = scope.to_numpy(dtype=bool)
            for axis in [0, 1]:
                if value_arr.shape[axis] < 2:
                    continue
                if axis == 0:
                    left = value_arr[:-1, :]
                    right = value_arr[1:, :]
                    edge_scope = scope_arr[:-1, :] | scope_arr[1:, :]
                else:
                    left = value_arr[:, :-1]
                    right = value_arr[:, 1:]
                    edge_scope = scope_arr[:, :-1] | scope_arr[:, 1:]
                finite = np.isfinite(left) & np.isfinite(right) & edge_scope
                crossing = finite & ((left == 0.0) | (right == 0.0) | (left * right < 0.0))
                crossing_edges += int(np.count_nonzero(crossing))
                if np.any(crossing):
                    endpoint_abs = np.minimum(np.abs(left[crossing]), np.abs(right[crossing]))
                    min_endpoint_abs = min(min_endpoint_abs, float(np.min(endpoint_abs)))
        if not math.isfinite(min_endpoint_abs):
            min_endpoint_abs = math.nan
        rows[f"{branch}_zero_crossing_edges"] = crossing_edges
        rows[f"{branch}_zero_crossing_min_endpoint_abs_speed"] = min_endpoint_abs
    rows["branch_zero_crossing_edges"] = int(rows["plus_zero_crossing_edges"] + rows["minus_zero_crossing_edges"])
    endpoint_mins = [
        _finite(rows["plus_zero_crossing_min_endpoint_abs_speed"], math.nan),
        _finite(rows["minus_zero_crossing_min_endpoint_abs_speed"], math.nan),
    ]
    finite_endpoint_mins = [value for value in endpoint_mins if math.isfinite(value)]
    rows["branch_zero_crossing_min_endpoint_abs_speed"] = min(finite_endpoint_mins) if finite_endpoint_mins else math.nan
    return rows


def _crossing_edges(points: pd.DataFrame, label: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    endpoint_flags = [
        "inside_packet_live_bool",
        "inside_packet_geom_bool",
        "active_interpolation_bool",
        "support_plant_bool",
        "top_gz_overlap_decile_bool",
    ]
    endpoint_values = ["gz_overlap_score", "gtt", "branch_abs_margin", "cond_metric", "abs_ricci_scalar"]
    for branch, value_col in [("plus", "plus_null_speed"), ("minus", "minus_null_speed")]:
        for stage, group in points.groupby("stage", sort=False):
            values = group.pivot_table(index="s", columns="l", values=value_col, aggfunc="mean")
            if values.shape[0] < 2 or values.shape[1] < 2:
                continue
            pivots = {
                key: group.pivot_table(index="s", columns="l", values=key, aggfunc="max").reindex(
                    index=values.index,
                    columns=values.columns,
                )
                for key in endpoint_flags + endpoint_values
                if key in group.columns
            }
            value_arr = values.to_numpy(dtype=float)
            s_axis = values.index.to_numpy(dtype=float)
            l_axis = values.columns.to_numpy(dtype=float)
            for axis_name, axis in [("s", 0), ("l", 1)]:
                if value_arr.shape[axis] < 2:
                    continue
                if axis == 0:
                    left = value_arr[:-1, :]
                    right = value_arr[1:, :]
                    edge_indices = np.argwhere(np.isfinite(left) & np.isfinite(right) & ((left == 0.0) | (right == 0.0) | (left * right < 0.0)))
                    for i, j in edge_indices:
                        endpoints = [(i, j), (i + 1, j)]
                        s_mid = 0.5 * (s_axis[i] + s_axis[i + 1])
                        l_mid = l_axis[j]
                        rows.append(_crossing_edge_row(label, str(stage), branch, axis_name, s_mid, l_mid, left[i, j], right[i, j], pivots, endpoints))
                else:
                    left = value_arr[:, :-1]
                    right = value_arr[:, 1:]
                    edge_indices = np.argwhere(np.isfinite(left) & np.isfinite(right) & ((left == 0.0) | (right == 0.0) | (left * right < 0.0)))
                    for i, j in edge_indices:
                        endpoints = [(i, j), (i, j + 1)]
                        s_mid = s_axis[i]
                        l_mid = 0.5 * (l_axis[j] + l_axis[j + 1])
                        rows.append(_crossing_edge_row(label, str(stage), branch, axis_name, s_mid, l_mid, left[i, j], right[i, j], pivots, endpoints))
    return pd.DataFrame(rows)


def _crossing_edge_row(
    label: str,
    stage: str,
    branch: str,
    edge_axis: str,
    s_mid: float,
    l_mid: float,
    left_speed: float,
    right_speed: float,
    pivots: dict[str, pd.DataFrame],
    endpoints: list[tuple[int, int]],
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "label": label,
        "stage": stage,
        "branch": branch,
        "edge_axis": edge_axis,
        "s_mid": float(s_mid),
        "l_mid": float(l_mid),
        "left_speed": float(left_speed),
        "right_speed": float(right_speed),
        "min_endpoint_abs_speed": float(min(abs(left_speed), abs(right_speed))),
    }
    for flag in [
        "inside_packet_live_bool",
        "inside_packet_geom_bool",
        "active_interpolation_bool",
        "support_plant_bool",
        "top_gz_overlap_decile_bool",
    ]:
        pivot = pivots.get(flag)
        row[flag.replace("_bool", "_endpoint")] = bool(
            pivot is not None and any(bool(pivot.iat[i, j]) for i, j in endpoints)
        )
    for value in ["gz_overlap_score", "gtt", "branch_abs_margin", "cond_metric", "abs_ricci_scalar"]:
        pivot = pivots.get(value)
        if pivot is None:
            row[f"max_endpoint_{value}"] = math.nan
        else:
            endpoint_numbers = [_finite(pivot.iat[i, j], math.nan) for i, j in endpoints]
            endpoint_numbers = [number for number in endpoint_numbers if math.isfinite(number)]
            row[f"max_endpoint_{value}"] = max(endpoint_numbers) if endpoint_numbers else math.nan
    return row


def _decision_for_label(summary: pd.DataFrame, label: str) -> dict[str, Any]:
    scopes = {str(row["scope"]): row for _, row in summary.loc[summary["label"] == label].iterrows()}
    overall = scopes.get("all_points", {})
    live = scopes.get("live_packet", {})
    active = scopes.get("active_interpolation", {})
    overlap = scopes.get("top_gz_overlap_decile", {})
    reasons: list[str] = []
    status = "pass"
    hard_fail_checks = [
        ("live packet branch pinch", live.get("near_branch_zero_points", 0)),
        ("live packet branch-zero crossing edge", live.get("branch_zero_crossing_edges", 0)),
        ("active interpolation branch-zero crossing edge", active.get("branch_zero_crossing_edges", 0)),
        ("top shell/throat-overlap branch-zero crossing edge", overlap.get("branch_zero_crossing_edges", 0)),
    ]
    for reason, count in hard_fail_checks:
        if int(_finite(count, 0.0)) > 0:
            status = "fail"
            reasons.append(reason)
    warning_checks = [
        ("branch pinch somewhere", overall.get("near_branch_zero_points", 0)),
        ("outgoing branch blocked somewhere", overall.get("plus_nonpositive_points", 0)),
        ("ingoing branch blocked somewhere", overall.get("minus_nonnegative_points", 0)),
        ("same-sign branch pair somewhere", overall.get("same_sign_branch_points", 0)),
        ("same-sign branch pair in live packet", live.get("same_sign_branch_points", 0)),
        ("nonnegative gtt in live packet", live.get("gtt_nonnegative_points", 0)),
        ("nonnegative gtt in active interpolation band", active.get("gtt_nonnegative_points", 0)),
    ]
    if status != "fail":
        for reason, count in warning_checks:
            if int(_finite(count, 0.0)) > 0:
                status = "warning"
                reasons.append(reason)
    if status == "pass":
        reasons.append("no branch pinch, branch sign flip, or nonnegative-gtt hit in tested scopes")
    return {"label": label, "gz_obstruction_status": status, "status_reason": "; ".join(reasons)}


def _select_seeds(points: pd.DataFrame, label: str) -> pd.DataFrame:
    rows: list[pd.Series] = []
    live = points.loc[points["inside_packet_live_bool"]].copy()
    if not live.empty:
        live = live.assign(packet_center_distance=(live["s"] - live["s"].median()).abs() + (live["l"] - live["l"].median()).abs())
        rows.append(live.sort_values("packet_center_distance").iloc[0])
    active = points.loc[points["active_interpolation_bool"]].copy()
    if not active.empty:
        rows.append(active.sort_values("gz_overlap_score", ascending=False).iloc[0])
    rows.append(points.sort_values("branch_abs_margin").iloc[0])
    seed_df = pd.DataFrame(rows).drop_duplicates(subset=["stage", "s", "l"]).copy()
    seed_df["label"] = label
    seed_names = []
    for _, row in seed_df.iterrows():
        if bool(row.get("inside_packet_live_bool", False)):
            seed_names.append("live_packet_representative")
        elif bool(row.get("active_interpolation_bool", False)):
            seed_names.append("max_overlap_representative")
        else:
            seed_names.append("worst_branch_margin_representative")
    seed_df["seed_kind"] = seed_names
    return seed_df


def _trace_label(points: pd.DataFrame, label: str) -> pd.DataFrame:
    grids = _build_stage_grids(points)
    seeds = _select_seeds(points, label)
    rows: list[dict[str, Any]] = []
    for _, seed in seeds.iterrows():
        stage = str(seed["stage"])
        grid = grids.get(stage)
        if grid is None:
            continue
        step_s = float(np.median(np.diff(grid.s_axis))) if len(grid.s_axis) > 1 else 1.0
        for branch in ["plus", "minus"]:
            trace = _trace_branch(
                grid,
                float(seed["s"]),
                float(seed["l"]),
                branch,
                step_s=step_s,
            )
            rows.append({
                "label": label,
                "stage": stage,
                "seed_kind": str(seed["seed_kind"]),
                "seed_region": str(seed["region"]),
                "seed_inside_packet_live": bool(seed["inside_packet_live_bool"]),
                "seed_active_interpolation": bool(seed["active_interpolation_bool"]),
                "seed_gz_overlap_score": float(seed["gz_overlap_score"]),
                "seed_branch_abs_margin": float(seed["branch_abs_margin"]),
                **trace,
            })
    return pd.DataFrame(rows)


def _markdown_report(
    ledgers: list[tuple[Path, str]],
    summary: pd.DataFrame,
    decision: pd.DataFrame,
    top_points: pd.DataFrame,
    traces: pd.DataFrame,
    crossing_edges: pd.DataFrame,
    args: argparse.Namespace,
) -> str:
    lines: list[str] = []
    lines.append("# GZ Obstruction Screen")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This screen checks the Garattini-Zatrimaylov-style obstruction channel that is not covered by selected-null "
        "or live packet-norm accounting: causal branch pinches, stationary-vector sign changes, and shell/throat "
        "interpolation overlap in the active-rail ADM point ledgers."
    )
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- branch zero threshold: `{args.branch_eps:g}`")
    lines.append(f"- active interpolation threshold: `{args.shell_threshold:g}`")
    for path, label in ledgers:
        lines.append(f"- `{label}`: `{path}`")
    lines.append("")
    lines.append("## Decision Sheet")
    lines.append("")
    display_decision = decision.copy()
    lines.append(display_decision.to_markdown(index=False))
    lines.append("")
    lines.append("## Causal Margins")
    lines.append("")
    key_scopes = summary[summary["scope"].isin(["all_points", "live_packet", "active_interpolation", "top_gz_overlap_decile"])].copy()
    display_cols = [
        "label",
        "scope",
        "rows",
        "min_plus_null_speed",
        "max_minus_null_speed",
        "min_branch_abs_margin",
        "near_branch_zero_points",
        "branch_zero_crossing_edges",
        "branch_zero_crossing_min_endpoint_abs_speed",
        "gtt_nonnegative_points",
        "max_gtt",
        "min_alpha",
        "max_gamma_ll",
        "max_cond_metric",
        "max_abs_ricci_scalar",
        "max_gz_overlap_score",
    ]
    display = key_scopes[display_cols].copy()
    for col in display.columns:
        if col not in {
            "label",
            "scope",
            "rows",
            "near_branch_zero_points",
            "branch_zero_crossing_edges",
            "gtt_nonnegative_points",
        }:
            display[col] = display[col].map(lambda value: _format_number(value))
    lines.append(display.to_markdown(index=False))
    lines.append("")
    lines.append("## Null Trace Smoke")
    lines.append("")
    if traces.empty:
        lines.append("No trace seeds were available.")
    else:
        trace_cols = [
            "label",
            "stage",
            "seed_kind",
            "seed_region",
            "branch",
            "trace_outcome",
            "escaped_expected_side",
            "delta_l",
            "min_abs_speed_along_trace",
        ]
        display_traces = traces[trace_cols].copy()
        for col in ["delta_l", "min_abs_speed_along_trace"]:
            display_traces[col] = display_traces[col].map(lambda value: _format_number(value))
        lines.append(display_traces.to_markdown(index=False))
    lines.append("")
    lines.append("## Branch Crossing Edges")
    lines.append("")
    if crossing_edges.empty:
        lines.append("No branch zero-crossing edges were detected.")
    else:
        crossing_display = crossing_edges.sort_values("min_endpoint_abs_speed").head(24).copy()
        crossing_cols = [
            "label",
            "stage",
            "branch",
            "edge_axis",
            "s_mid",
            "l_mid",
            "min_endpoint_abs_speed",
            "inside_packet_live_endpoint",
            "active_interpolation_endpoint",
            "top_gz_overlap_decile_endpoint",
            "max_endpoint_gz_overlap_score",
            "max_endpoint_gtt",
            "max_endpoint_cond_metric",
        ]
        display_crossings = crossing_display[crossing_cols].copy()
        for col in [
            "s_mid",
            "l_mid",
            "min_endpoint_abs_speed",
            "max_endpoint_gz_overlap_score",
            "max_endpoint_gtt",
            "max_endpoint_cond_metric",
        ]:
            display_crossings[col] = display_crossings[col].map(lambda value: _format_number(value))
        lines.append(display_crossings.to_markdown(index=False))
    lines.append("")
    lines.append("## Highest Overlap Points")
    lines.append("")
    overlap_cols = [
        "label",
        "stage",
        "region",
        "s",
        "l",
        "gz_overlap_score",
        "branch_abs_margin",
        "plus_null_speed",
        "minus_null_speed",
        "gtt",
        "cond_metric",
        "abs_ricci_scalar",
    ]
    display_top = top_points[overlap_cols].copy()
    for col in [c for c in overlap_cols if c not in {"label", "stage", "region"}]:
        display_top[col] = display_top[col].map(lambda value: _format_number(value))
    lines.append(display_top.to_markdown(index=False))
    lines.append("")
    lines.append("## Limits")
    lines.append("")
    lines.append(
        "A pass here is a ledger-level causal-structure screen, not a proof of global horizon absence. "
        "The null traces are finite-domain smoke traces, and the shell/throat score is a proxy for localized "
        "actuation overlap, not a symbolic GZ theorem."
    )
    lines.append("")
    return "\n".join(lines)


def _format_number(value: Any) -> str:
    number = _finite(value, math.nan)
    if not math.isfinite(number):
        return "n/a"
    if abs(number) >= 1000.0 or (0.0 < abs(number) < 1.0e-4):
        return f"{number:.3e}"
    return f"{number:.6f}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a GZ-style causal obstruction screen on source-ledger point ledgers.")
    parser.add_argument("--point-ledger", type=Path, action="append", required=True)
    parser.add_argument("--label", action="append", required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--branch-eps", type=float, default=1.0e-4)
    parser.add_argument("--shell-threshold", type=float, default=1.0e-3)
    parser.add_argument("--top-n", type=int, default=12)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if len(args.point_ledger) != len(args.label):
        raise SystemExit("--point-ledger and --label counts must match")
    if args.top_n < 1:
        raise SystemExit("--top-n must be at least 1")
    ledgers = list(zip(args.point_ledger, args.label))
    args.outdir.mkdir(parents=True, exist_ok=True)

    all_points: list[pd.DataFrame] = []
    summary_rows: list[dict[str, Any]] = []
    top_rows: list[pd.DataFrame] = []
    trace_rows: list[pd.DataFrame] = []
    crossing_rows: list[pd.DataFrame] = []

    for path, label in ledgers:
        points = _annotate_points(pd.read_csv(path), label, args.shell_threshold)
        score_cut = points["gz_overlap_score"].replace([np.inf, -np.inf], np.nan).quantile(0.90)
        if not math.isfinite(float(score_cut)):
            score_cut = math.inf
        points["top_gz_overlap_decile_bool"] = points["gz_overlap_score"] >= score_cut
        all_points.append(points)
        scopes = {
            "all_points": pd.Series(True, index=points.index),
            "live_packet": points["inside_packet_live_bool"],
            "geometric_packet": points["inside_packet_geom_bool"],
            "support_plant": points["support_plant_bool"],
            "main_support": points["main_support_bool"],
            "active_interpolation": points["active_interpolation_bool"],
            "top_gz_overlap_decile": points["top_gz_overlap_decile_bool"],
        }
        for scope, mask in scopes.items():
            row = _mask_summary(points, label, scope, mask, args.branch_eps)
            row.update(_edge_crossings_for_scope(points, mask))
            summary_rows.append(row)
        top = points.sort_values("gz_overlap_score", ascending=False).head(args.top_n).copy()
        top_rows.append(top)
        trace_rows.append(_trace_label(points, label))
        crossing_rows.append(_crossing_edges(points, label))
        print(json.dumps({"label": label, "rows": int(len(points)), "max_gz_overlap_score": float(points["gz_overlap_score"].max())}), flush=True)

    point_diag = pd.concat(all_points, ignore_index=True)
    summary = pd.DataFrame(summary_rows)
    labels = [label for _, label in ledgers]
    decision = pd.DataFrame([_decision_for_label(summary, label) for label in labels])
    top_points = pd.concat(top_rows, ignore_index=True) if top_rows else pd.DataFrame()
    traces = pd.concat(trace_rows, ignore_index=True) if trace_rows else pd.DataFrame()
    crossing_edges = pd.concat(crossing_rows, ignore_index=True) if crossing_rows else pd.DataFrame()

    point_path = args.outdir / "gz_obstruction_point_diagnostics.csv"
    summary_path = args.outdir / "gz_obstruction_summary.csv"
    decision_path = args.outdir / "gz_obstruction_decision.csv"
    top_path = args.outdir / "gz_obstruction_top_overlap_points.csv"
    trace_path = args.outdir / "gz_obstruction_null_trace_summary.csv"
    crossing_path = args.outdir / "gz_obstruction_branch_crossing_edges.csv"
    report_path = args.outdir / "gz_obstruction_report.md"
    metadata_path = args.outdir / "gz_obstruction_metadata.json"

    point_diag.to_csv(point_path, index=False)
    summary.to_csv(summary_path, index=False)
    decision.to_csv(decision_path, index=False)
    top_points.to_csv(top_path, index=False)
    traces.to_csv(trace_path, index=False)
    crossing_edges.to_csv(crossing_path, index=False)
    report_path.write_text(_markdown_report(ledgers, summary, decision, top_points, traces, crossing_edges, args), encoding="utf-8")
    repo_root = Path(__file__).resolve().parents[3]
    metadata_path.write_text(
        json.dumps(
            {
                "point_ledgers": [{"path": str(path), "label": label} for path, label in ledgers],
                "branch_eps": args.branch_eps,
                "shell_threshold": args.shell_threshold,
                "top_n": args.top_n,
                "commit": _git_commit(repo_root),
                "files": {
                    "point_diagnostics": str(point_path),
                    "summary": str(summary_path),
                    "decision": str(decision_path),
                    "top_overlap_points": str(top_path),
                    "null_trace_summary": str(trace_path),
                    "branch_crossing_edges": str(crossing_path),
                    "report": str(report_path),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "outdir": str(args.outdir), "cases": len(ledgers)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
