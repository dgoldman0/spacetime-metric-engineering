from __future__ import annotations

import os
import math
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .endpoint_support_principal_symbol import PrincipalSymbolSpec, _bool_series, _finite
from .endpoint_support_rapidity_advection import _apply_budget_limiter, _upwind_step
from .endpoint_support_rapidity_budget import (
    RapidityBudgetSpec,
    _budget_row,
    _source_delta_psi_for_heat_delta,
    _symbol_at_delta_psi,
)
from .endpoint_support_source_dynamics import (
    _load_closure_dir,
    _smooth_profile,
    _source_column,
    _temporal_envelope,
)
from .source_ledger import sha256_file, write_manifest


@dataclass(frozen=True)
class PackageCouplingSpec:
    observed_heat_ratio_delta: float = 1.0e-4
    reference_large_heat_ratio_delta: float = 5.0e-4
    steps: int = 40
    cfl: float = 0.45
    limiter_safety_fraction: float = 0.95
    source_column: str = "candidate_support_abs_PF_density"
    source_smoothing_passes: int = 0
    temporal_profile: str = "raised_cosine"
    budget_bisection_steps: int = 48
    s_round_decimals: int = 12
    top_row_count: int = 160
    max_workers: int | None = 4
    budget_chunksize: int = 64
    slice_chunksize: int = 8


@dataclass(frozen=True)
class PackageCouplingScenario:
    label: str
    heat_ratio_delta: float
    direction: str
    budget_limiter: bool = False
    source_scale: float = 1.0


def default_scenarios(spec: PackageCouplingSpec | None = None) -> list[PackageCouplingScenario]:
    spec = spec or PackageCouplingSpec()
    return [
        PackageCouplingScenario("observed_source_outward_unlimited", spec.observed_heat_ratio_delta, "outward", False),
        PackageCouplingScenario("observed_source_inward_unlimited", spec.observed_heat_ratio_delta, "inward", False),
        PackageCouplingScenario("observed_source_outward_budget_limited", spec.observed_heat_ratio_delta, "outward", True),
        PackageCouplingScenario("large_source_outward_unlimited", spec.reference_large_heat_ratio_delta, "outward", False),
        PackageCouplingScenario("large_source_outward_budget_limited", spec.reference_large_heat_ratio_delta, "outward", True),
    ]


def _active_nonlive_mask(frame: pd.DataFrame) -> pd.Series:
    active = _bool_series(frame["medium_source_active"]) if "medium_source_active" in frame else pd.Series(True, index=frame.index)
    live = _bool_series(frame["covariant_divergence_live"]) if "covariant_divergence_live" in frame else pd.Series(False, index=frame.index)
    return active & (~live)


def _worker_count(max_workers: int | None) -> int:
    if max_workers is not None and int(max_workers) > 0:
        return int(max_workers)
    cpu_count = os.cpu_count() or 1
    return min(4, max(1, cpu_count - 1))


def _prepared_active_frame(point: pd.DataFrame, spec: PackageCouplingSpec) -> pd.DataFrame:
    source = _source_column(point, spec.source_column)
    active = point.loc[_active_nonlive_mask(point)].copy()
    active["source_row_index"] = active.index.astype(int)
    active["slice_s_key"] = active["s"].astype(float).round(int(spec.s_round_decimals))
    active["support_source_density"] = active[source].astype(float).abs().replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return active.loc[active["support_source_density"].gt(0.0)].copy()


def _build_budget_rows(
    active: pd.DataFrame,
    *,
    symbol_spec: PrincipalSymbolSpec,
    budget_spec: RapidityBudgetSpec,
    coupling_spec: PackageCouplingSpec,
) -> pd.DataFrame:
    payloads = [
        (int(row["source_row_index"]), row.to_dict(), symbol_spec, budget_spec)
        for _, row in active.iterrows()
    ]
    workers = _worker_count(coupling_spec.max_workers)
    if workers <= 1 or len(payloads) <= 1:
        rows = [_budget_row_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(_budget_row_worker, payloads, chunksize=max(1, int(coupling_spec.budget_chunksize))))
    return pd.DataFrame(rows)


def _budget_row_worker(payload: tuple[int, dict[str, Any], PrincipalSymbolSpec, RapidityBudgetSpec]) -> dict[str, Any]:
    source_index, row, symbol_spec, budget_spec = payload
    return _budget_row(source_index, pd.Series(row), symbol_spec, budget_spec)


def _safe_budget_fraction(delta: np.ndarray, budget: np.ndarray) -> np.ndarray:
    out = np.zeros_like(delta, dtype=float)
    finite = np.isfinite(budget) & (budget > 0.0)
    out[finite] = delta[finite] / budget[finite]
    exhausted = (~np.isfinite(budget) & (budget <= 0.0)) | ((budget <= 0.0) & np.isfinite(budget))
    out[exhausted & (delta > 0.0)] = np.inf
    return out


def _slice_source_profile(
    group: pd.DataFrame,
    budget: pd.DataFrame,
    scenario: PackageCouplingScenario,
    spec: PackageCouplingSpec,
) -> tuple[np.ndarray, dict[str, Any]]:
    density = _smooth_profile(group["support_source_density"].astype(float).to_numpy(), spec.source_smoothing_passes)
    candidates = budget.copy()
    candidates["budget_sort"] = candidates["max_admissible_delta_psi"].astype(float).replace([np.inf], np.nan)
    candidates = candidates.sort_values(["budget_sort", "observed_budget_fraction"], ascending=[True, False], na_position="last")
    bottleneck = candidates.iloc[0]
    row_ids = group["source_row_index"].astype(int).to_numpy()
    match = np.flatnonzero(row_ids == int(bottleneck["source_row_index"]))
    normalizer_pos = int(match[0]) if len(match) else int(np.argmax(density))
    normalizer = float(density[normalizer_pos]) if len(density) else 0.0
    if not math.isfinite(normalizer) or normalizer <= 0.0:
        normalizer_pos = int(np.argmax(density)) if len(density) else 0
        normalizer = float(density[normalizer_pos]) if len(density) else 0.0
    normalized = density / normalizer if math.isfinite(normalizer) and normalizer > 0.0 else np.zeros_like(density)
    target_delta = _source_delta_psi_for_heat_delta(
        _finite(bottleneck["baseline_heat_ratio"], 0.0),
        float(scenario.heat_ratio_delta) * float(scenario.source_scale),
    )
    meta = {
        "normalizer_source_row_index": int(row_ids[normalizer_pos]) if len(row_ids) else -1,
        "normalizer_l": _finite(group.iloc[normalizer_pos].get("l"), float("nan")) if len(group) else float("nan"),
        "normalizer_density": normalizer,
        "normalizer_is_budget_bottleneck": bool(len(match) and int(match[0]) == normalizer_pos),
        "bottleneck_source_row_index": int(bottleneck["source_row_index"]),
        "bottleneck_l": _finite(bottleneck["l"], float("nan")),
        "bottleneck_budget_delta_psi": _finite(bottleneck["max_admissible_delta_psi"], float("nan")),
        "bottleneck_observed_budget_fraction": _finite(bottleneck["observed_budget_fraction"], float("nan")),
        "target_bottleneck_delta_psi": target_delta,
        "source_density_sum": float(np.sum(density)),
        "max_normalized_source_density": float(np.max(normalized)) if len(normalized) else float("nan"),
    }
    return normalized * float(target_delta), meta


def _sample_min_symbol_margin(
    group: pd.DataFrame,
    row_max_delta: np.ndarray,
    row_max_fraction: np.ndarray,
    symbol_spec: PrincipalSymbolSpec,
) -> tuple[float, int]:
    finite = np.isfinite(row_max_fraction)
    if not np.any(finite):
        return float("nan"), -1
    order = np.argsort(np.where(finite, row_max_fraction, -np.inf))[::-1][: min(6, len(row_max_fraction))]
    min_margin = float("inf")
    worst_index = -1
    for pos in order:
        symbol = _symbol_at_delta_psi(group.iloc[int(pos)], float(row_max_delta[int(pos)]), symbol_spec)
        margin = _finite(symbol.get("relative_cone_margin"), float("nan"))
        if math.isfinite(margin) and margin < min_margin:
            min_margin = margin
            worst_index = int(group.iloc[int(pos)]["source_row_index"])
    return (min_margin if math.isfinite(min_margin) else float("nan")), worst_index


def _run_slice_scenario(
    group: pd.DataFrame,
    budget: pd.DataFrame,
    scenario: PackageCouplingScenario,
    *,
    coupling_spec: PackageCouplingSpec,
    symbol_spec: PrincipalSymbolSpec,
) -> tuple[dict[str, Any], dict[str, Any]]:
    source_profile, source_meta = _slice_source_profile(group, budget, scenario, coupling_spec)
    envelope = _temporal_envelope(coupling_spec.steps, coupling_spec.temporal_profile)
    state = np.zeros(len(group), dtype=float)
    row_max_delta = state.copy()
    row_max_fraction = np.zeros(len(group), dtype=float)
    row_clip_total = np.zeros(len(group), dtype=float)
    budget_values = budget["max_admissible_delta_psi"].astype(float).to_numpy()
    baseline_fail = budget["baseline_relative_cone_margin"].astype(float).to_numpy() < float(symbol_spec.speed_margin_gate)
    limiter_steps = 0
    max_clip = 0.0
    for weight in envelope:
        state = state + source_profile * float(weight)
        state = _upwind_step(state, cfl=coupling_spec.cfl, direction=scenario.direction)
        clipped = np.zeros_like(state)
        if scenario.budget_limiter:
            state, clipped = _apply_budget_limiter(
                state,
                budget_values,
                safety_fraction=coupling_spec.limiter_safety_fraction,
            )
            if bool(np.any(clipped > 0.0)):
                limiter_steps += 1
                row_clip_total += clipped
                max_clip = max(max_clip, float(np.max(clipped)))
        fraction = _safe_budget_fraction(state, budget_values)
        row_max_delta = np.maximum(row_max_delta, state)
        row_max_fraction = np.maximum(row_max_fraction, fraction)
    over_budget = row_max_fraction > 1.0
    fail_mask = baseline_fail | over_budget
    worst_pos = int(np.nanargmax(np.where(np.isfinite(row_max_fraction), row_max_fraction, np.inf))) if len(group) else 0
    if np.isinf(row_max_fraction[worst_pos]):
        finite = np.flatnonzero(np.isfinite(row_max_fraction))
        worst_pos = int(finite[np.argmax(row_max_fraction[finite])]) if len(finite) else 0
    min_margin, min_margin_row = _sample_min_symbol_margin(group, row_max_delta, row_max_fraction, symbol_spec)
    final_ratio = np.tanh(
        np.arctanh(group["regulated_heat_flux_ratio"].astype(float).clip(lower=0.0, upper=1.0 - 1.0e-15).to_numpy())
        + row_max_delta
    )
    min_transport = float(np.min(1.0 - final_ratio)) if len(final_ratio) else float("nan")
    summary = {
        "scenario": scenario.label,
        "heat_ratio_delta": float(scenario.heat_ratio_delta),
        "direction": scenario.direction,
        "budget_limiter": bool(scenario.budget_limiter),
        "source_scale": float(scenario.source_scale),
        "assignment": str(group["assignment"].iloc[0]),
        "stage": str(group["stage"].iloc[0]),
        "region": str(group["region"].iloc[0]),
        "s": _finite(group["s"].iloc[0], float("nan")),
        "slice_s_key": _finite(group["slice_s_key"].iloc[0], float("nan")),
        "rows": int(len(group)),
        "status": "fail" if bool(np.any(fail_mask)) else "limited_pass" if limiter_steps > 0 else "pass",
        "hard_pass": bool(not np.any(fail_mask)),
        "fail_rows_any_time": int(np.sum(fail_mask)),
        "baseline_fail_rows": int(np.sum(baseline_fail)),
        "over_budget_rows_any_time": int(np.sum(over_budget)),
        "max_budget_fraction": float(np.nanmax(row_max_fraction)) if len(row_max_fraction) else float("nan"),
        "worst_source_row_index": int(group.iloc[worst_pos]["source_row_index"]) if len(group) else -1,
        "worst_l": _finite(group.iloc[worst_pos].get("l"), float("nan")) if len(group) else float("nan"),
        "worst_delta_psi": float(row_max_delta[worst_pos]) if len(group) else float("nan"),
        "min_relative_cone_margin_sample": min_margin,
        "min_relative_cone_margin_sample_row": min_margin_row,
        "min_transport_margin": min_transport,
        "limiter_active_steps": int(limiter_steps),
        "limiter_clipped_rows": int(np.sum(row_clip_total > 0.0)),
        "max_limiter_clip_delta_psi": max_clip,
        **source_meta,
    }
    worst_row = {
        key: summary[key]
        for key in [
            "scenario",
            "assignment",
            "stage",
            "region",
            "s",
            "rows",
            "status",
            "max_budget_fraction",
            "worst_source_row_index",
            "worst_l",
            "worst_delta_psi",
            "min_relative_cone_margin_sample",
            "limiter_clipped_rows",
        ]
    }
    return summary, worst_row


def _slice_group_worker(
    payload: tuple[
        list[dict[str, Any]],
        list[dict[str, Any]],
        list[PackageCouplingScenario],
        PackageCouplingSpec,
        PrincipalSymbolSpec,
    ]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    group_records, budget_records, scenarios, coupling_spec, symbol_spec = payload
    group = pd.DataFrame(group_records)
    budget = pd.DataFrame(budget_records)
    slice_rows: list[dict[str, Any]] = []
    worst_rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        summary, worst = _run_slice_scenario(
            group,
            budget,
            scenario,
            coupling_spec=coupling_spec,
            symbol_spec=symbol_spec,
        )
        slice_rows.append(summary)
        worst_rows.append(worst)
    return slice_rows, worst_rows


def _package_summary(slice_summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for scenario, group in slice_summary.groupby("scenario", sort=False):
        fail_slices = int((~group["hard_pass"].astype(bool)).sum())
        limiter_slices = int((group["limiter_clipped_rows"].astype(int) > 0).sum())
        rows.append({
            "scenario": str(scenario),
            "heat_ratio_delta": float(group["heat_ratio_delta"].iloc[0]),
            "direction": str(group["direction"].iloc[0]),
            "budget_limiter": bool(group["budget_limiter"].iloc[0]),
            "status": "fail" if fail_slices else "limited_pass" if limiter_slices else "pass",
            "hard_pass": fail_slices == 0,
            "slices": int(len(group)),
            "rows": int(group["rows"].astype(int).sum()),
            "fail_slices": fail_slices,
            "fail_rows_any_time": int(group["fail_rows_any_time"].astype(int).sum()),
            "over_budget_rows_any_time": int(group["over_budget_rows_any_time"].astype(int).sum()),
            "limiter_active_slices": limiter_slices,
            "limiter_clipped_rows": int(group["limiter_clipped_rows"].astype(int).sum()),
            "max_budget_fraction": float(group["max_budget_fraction"].astype(float).replace([np.inf], np.nan).max()),
            "min_relative_cone_margin_sample": float(group["min_relative_cone_margin_sample"].astype(float).min()),
            "min_transport_margin": float(group["min_transport_margin"].astype(float).min()),
        })
    return pd.DataFrame(rows)


def _decision(package_summary: pd.DataFrame, observed_delta: float) -> pd.DataFrame:
    observed = package_summary.loc[
        (package_summary["heat_ratio_delta"].astype(float) <= float(observed_delta) + 1.0e-15)
        & (~package_summary["budget_limiter"].astype(bool))
    ]
    large_unlimited = package_summary.loc[
        (package_summary["heat_ratio_delta"].astype(float) > float(observed_delta) + 1.0e-15)
        & (~package_summary["budget_limiter"].astype(bool))
    ]
    observed_pass = bool(len(observed) and observed["hard_pass"].astype(bool).all())
    large_unlimited_fails = bool(len(large_unlimited) and (~large_unlimited["hard_pass"].astype(bool)).any())
    status = (
        "package_support_source_observed_clean"
        if observed_pass
        else "package_support_source_watch"
        if len(observed)
        else "package_support_source_incomplete"
    )
    read = (
        "observed support-source coupling stays clean package-wide under source-driven advection"
        if status == "package_support_source_observed_clean"
        else "observed support-source coupling has one or more package-wide slice failures"
        if status == "package_support_source_watch"
        else "observed support-source coupling scenarios are incomplete"
    )
    return pd.DataFrame([{
        "package_source_coupling_status": status,
        "observed_unlimited_pass": observed_pass,
        "large_unlimited_fails": large_unlimited_fails,
        "max_observed_unlimited_budget_fraction": float(observed["max_budget_fraction"].astype(float).max()) if len(observed) else float("nan"),
        "max_large_unlimited_budget_fraction": float(large_unlimited["max_budget_fraction"].astype(float).max()) if len(large_unlimited) else float("nan"),
        "decision_read": read,
    }])


def build_package_source_coupling(
    closure_dir: Path,
    *,
    symbol_spec: PrincipalSymbolSpec | None = None,
    budget_spec: RapidityBudgetSpec | None = None,
    coupling_spec: PackageCouplingSpec | None = None,
    scenarios: list[PackageCouplingScenario] | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    symbol_spec = symbol_spec or PrincipalSymbolSpec()
    coupling_spec = coupling_spec or PackageCouplingSpec()
    budget_spec = budget_spec or RapidityBudgetSpec(
        observed_heat_ratio_delta=coupling_spec.observed_heat_ratio_delta,
        reference_large_heat_ratio_delta=coupling_spec.reference_large_heat_ratio_delta,
        speed_margin_gate=symbol_spec.speed_margin_gate,
        bisection_steps=coupling_spec.budget_bisection_steps,
    )
    scenarios = scenarios or default_scenarios(coupling_spec)
    point_closure, manifest, point_path = _load_closure_dir(closure_dir)
    active = _prepared_active_frame(point_closure, coupling_spec)
    budget_rows = _build_budget_rows(
        active,
        symbol_spec=symbol_spec,
        budget_spec=budget_spec,
        coupling_spec=coupling_spec,
    )
    active_with_budget = active.merge(
        budget_rows[["source_row_index", "max_admissible_delta_psi", "baseline_relative_cone_margin", "observed_budget_fraction"]],
        on="source_row_index",
        how="left",
    )
    budget_by_row = budget_rows.set_index("source_row_index", drop=False)
    payloads: list[
        tuple[
            list[dict[str, Any]],
            list[dict[str, Any]],
            list[PackageCouplingScenario],
            PackageCouplingSpec,
            PrincipalSymbolSpec,
        ]
    ] = []
    group_cols = ["assignment", "stage", "region", "slice_s_key"]
    for _, group in active_with_budget.sort_values(["assignment", "stage", "region", "slice_s_key", "l"]).groupby(group_cols, sort=False, dropna=False):
        group = group.sort_values("l").reset_index(drop=True)
        budget = budget_by_row.loc[group["source_row_index"].astype(int).to_numpy()].reset_index(drop=True)
        payloads.append((group.to_dict("records"), budget.to_dict("records"), scenarios, coupling_spec, symbol_spec))
    workers = _worker_count(coupling_spec.max_workers)
    if workers <= 1 or len(payloads) <= 1:
        mapped = [_slice_group_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            mapped = list(pool.map(_slice_group_worker, payloads, chunksize=max(1, int(coupling_spec.slice_chunksize))))
    slice_rows: list[dict[str, Any]] = []
    worst_rows: list[dict[str, Any]] = []
    for slice_part, worst_part in mapped:
        slice_rows.extend(slice_part)
        worst_rows.extend(worst_part)
    slice_summary = pd.DataFrame(slice_rows)
    package_summary = _package_summary(slice_summary)
    decision = _decision(package_summary, coupling_spec.observed_heat_ratio_delta)
    worst = (
        pd.DataFrame(worst_rows)
        .sort_values(["max_budget_fraction", "rows"], ascending=[False, False])
        .head(int(coupling_spec.top_row_count))
    )
    outputs = {
        "active_budget": budget_rows,
        "slice_summary": slice_summary,
        "package_summary": package_summary,
        "worst_rows": worst,
        "decision": decision,
    }
    metadata = {
        "source_name": "endpoint_support_source_coupling_package",
        "closure_dir": str(closure_dir),
        "point_closure": str(point_path),
        "point_closure_sha256": sha256_file(point_path),
        "closure_source_name": manifest.get("source_name", ""),
        "stroke_dir": manifest.get("stroke_dir", ""),
        "symbol_spec": symbol_spec.__dict__,
        "budget_spec": budget_spec.__dict__,
        "coupling_spec": coupling_spec.__dict__,
        "scenarios": [scenario.__dict__ for scenario in scenarios],
        "caveat": (
            "Full-package reduced 1+1 fixed-background source-coupling sweep over active non-live support slices. "
            "This evolves the bounded-rapidity support-source drive along service-radial slices and audits local cone budgets; it is not full spacetime evolution."
        ),
    }
    return outputs, metadata


def write_package_source_coupling_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "active_budget": outdir / "endpoint_support_source_coupling_active_budget.csv",
        "slice_summary": outdir / "endpoint_support_source_coupling_slice_summary.csv",
        "package_summary": outdir / "endpoint_support_source_coupling_package_summary.csv",
        "worst_rows": outdir / "endpoint_support_source_coupling_worst_rows.csv",
        "decision": outdir / "endpoint_support_source_coupling_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    manifest_path = outdir / "endpoint_support_source_coupling_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
