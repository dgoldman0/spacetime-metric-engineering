from __future__ import annotations

import json
import math
import os
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .endpoint_support_principal_symbol import PrincipalSymbolSpec, _bool_series, _finite
from .endpoint_support_rapidity_advection import _apply_budget_limiter, _upwind_step
from .endpoint_support_rapidity_budget import RapidityBudgetSpec, _symbol_at_delta_psi
from .endpoint_support_source_coupling_package import (
    PackageCouplingScenario,
    PackageCouplingSpec,
    _prepared_active_frame,
    _safe_budget_fraction,
    _slice_source_profile,
)
from .endpoint_support_source_dynamics import _load_closure_dir
from .source_ledger import sha256_file, write_manifest


@dataclass(frozen=True)
class FullSystemEvolutionSpec:
    observed_heat_ratio_delta: float = 1.0e-4
    reference_large_heat_ratio_delta: float = 5.0e-4
    steps: int = 48
    radial_cfl: float = 0.40
    service_cfl: float = 0.20
    limiter_safety_fraction: float = 0.95
    source_column: str = "candidate_support_abs_PF_density"
    source_smoothing_passes: int = 0
    source_profile_budget_cap_scope: str = "support_edge_entry_catch"
    source_profile_budget_cap_fraction: float = 0.95
    source_profile_budget_cap_reference_delta: float | None = None
    temporal_profile: str = "raised_cosine"
    s_round_decimals: int = 12
    l_round_decimals: int = 12
    top_row_count: int = 120
    max_workers: int | None = 4


@dataclass(frozen=True)
class FullSystemEvolutionScenario:
    label: str
    heat_ratio_delta: float
    radial_direction: str
    service_direction: str
    budget_limiter: bool = False
    source_scale: float = 1.0


def default_scenarios(spec: FullSystemEvolutionSpec | None = None) -> list[FullSystemEvolutionScenario]:
    spec = spec or FullSystemEvolutionSpec()
    return [
        FullSystemEvolutionScenario(
            "observed_full_outward_forward_unlimited",
            spec.observed_heat_ratio_delta,
            "outward",
            "forward",
            False,
        ),
        FullSystemEvolutionScenario(
            "observed_full_inward_forward_unlimited",
            spec.observed_heat_ratio_delta,
            "inward",
            "forward",
            False,
        ),
        FullSystemEvolutionScenario(
            "observed_full_outward_backward_unlimited",
            spec.observed_heat_ratio_delta,
            "outward",
            "backward",
            False,
        ),
        FullSystemEvolutionScenario(
            "observed_full_outward_forward_budget_limited",
            spec.observed_heat_ratio_delta,
            "outward",
            "forward",
            True,
        ),
        FullSystemEvolutionScenario(
            "large_full_outward_forward_unlimited",
            spec.reference_large_heat_ratio_delta,
            "outward",
            "forward",
            False,
        ),
        FullSystemEvolutionScenario(
            "large_full_outward_forward_budget_limited",
            spec.reference_large_heat_ratio_delta,
            "outward",
            "forward",
            True,
        ),
    ]


def _package_spec(spec: FullSystemEvolutionSpec) -> PackageCouplingSpec:
    return PackageCouplingSpec(
        observed_heat_ratio_delta=float(spec.observed_heat_ratio_delta),
        reference_large_heat_ratio_delta=float(spec.reference_large_heat_ratio_delta),
        steps=int(spec.steps),
        cfl=float(spec.radial_cfl),
        limiter_safety_fraction=float(spec.limiter_safety_fraction),
        source_column=str(spec.source_column),
        source_smoothing_passes=int(spec.source_smoothing_passes),
        source_profile_budget_cap_scope=str(spec.source_profile_budget_cap_scope),
        source_profile_budget_cap_fraction=float(spec.source_profile_budget_cap_fraction),
        source_profile_budget_cap_reference_delta=spec.source_profile_budget_cap_reference_delta,
        temporal_profile=str(spec.temporal_profile),
        s_round_decimals=int(spec.s_round_decimals),
    )


def _temporal_envelope(steps: int, profile: str) -> np.ndarray:
    count = int(steps)
    if count <= 0:
        return np.zeros(0, dtype=float)
    if profile == "flat":
        return np.full(count, 1.0 / count, dtype=float)
    if profile == "raised_cosine":
        x = (np.arange(count, dtype=float) + 0.5) / count
        weights = 0.5 - 0.5 * np.cos(2.0 * math.pi * x)
        total = float(weights.sum())
        return weights / total if total > 0.0 else np.full(count, 1.0 / count, dtype=float)
    raise ValueError(f"unknown temporal profile {profile!r}")


def _read_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def _worker_count(max_workers: int | None) -> int:
    if max_workers is not None and int(max_workers) > 0:
        return int(max_workers)
    cpu_count = os.cpu_count() or 1
    return min(4, max(1, cpu_count - 1))


def _load_budget_rows(source_coupling_dir: Path) -> tuple[pd.DataFrame, dict[str, Any], Path]:
    budget_path = source_coupling_dir / "endpoint_support_source_coupling_active_budget.csv"
    manifest_path = source_coupling_dir / "endpoint_support_source_coupling_manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    return _read_table(budget_path), manifest, budget_path


def _prepare_domain(
    closure_dir: Path,
    source_coupling_dir: Path,
    spec: FullSystemEvolutionSpec,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    point_closure, closure_manifest, point_path = _load_closure_dir(closure_dir)
    budget_rows, coupling_manifest, budget_path = _load_budget_rows(source_coupling_dir)
    active = _prepared_active_frame(point_closure, _package_spec(spec)).copy()
    active["domain_pos"] = np.arange(len(active), dtype=int)
    active["slice_s_key"] = active["s"].astype(float).round(int(spec.s_round_decimals))
    active["l_key"] = active["l"].astype(float).round(int(spec.l_round_decimals))
    keep_cols = [
        "source_row_index",
        "max_admissible_delta_psi",
        "baseline_relative_cone_margin",
        "baseline_heat_ratio",
        "observed_budget_fraction",
    ]
    active = active.merge(budget_rows[keep_cols], on="source_row_index", how="left", validate="one_to_one")
    if active["max_admissible_delta_psi"].isna().any():
        missing = int(active["max_admissible_delta_psi"].isna().sum())
        raise ValueError(f"active domain rows missing precomputed rapidity budgets: {missing}")
    budget = active[[
        "source_row_index",
        "s",
        "l",
        "assignment",
        "stage",
        "region",
        "baseline_heat_ratio",
        "baseline_relative_cone_margin",
        "max_admissible_delta_psi",
        "observed_budget_fraction",
    ]].copy()
    metadata = {
        "point_closure": str(point_path),
        "point_closure_sha256": sha256_file(point_path),
        "closure_source_name": closure_manifest.get("source_name", ""),
        "source_coupling_budget": str(budget_path),
        "source_coupling_budget_sha256": sha256_file(budget_path),
        "source_coupling_source_name": coupling_manifest.get("source_name", ""),
    }
    return active.reset_index(drop=True), budget.reset_index(drop=True), metadata


def _build_groups(frame: pd.DataFrame, group_cols: list[str], coord_col: str) -> list[np.ndarray]:
    groups: list[np.ndarray] = []
    for _, group in frame.sort_values(group_cols + [coord_col]).groupby(group_cols, sort=False, dropna=False):
        idx = group["domain_pos"].astype(int).to_numpy()
        if len(idx) > 1:
            groups.append(idx)
    return groups


def _advect_groups(state: np.ndarray, groups: list[np.ndarray], *, cfl: float, direction: str) -> np.ndarray:
    out = state.copy()
    mapped = "outward" if direction == "forward" else "inward" if direction == "backward" else direction
    for idx in groups:
        out[idx] = _upwind_step(out[idx], cfl=cfl, direction=mapped)
    return out


def _scenario_to_package_scenario(scenario: FullSystemEvolutionScenario) -> PackageCouplingScenario:
    return PackageCouplingScenario(
        scenario.label,
        float(scenario.heat_ratio_delta),
        str(scenario.radial_direction),
        bool(scenario.budget_limiter),
        float(scenario.source_scale),
    )


def _source_profile_for_scenario(
    active: pd.DataFrame,
    budget: pd.DataFrame,
    scenario: FullSystemEvolutionScenario,
    spec: FullSystemEvolutionSpec,
) -> tuple[np.ndarray, pd.DataFrame]:
    package_scenario = _scenario_to_package_scenario(scenario)
    package_spec = _package_spec(spec)
    profile = np.zeros(len(active), dtype=float)
    rows: list[dict[str, Any]] = []
    budget_by_row = budget.set_index("source_row_index", drop=False)
    group_cols = ["assignment", "stage", "region", "slice_s_key"]
    for _, group in active.sort_values(group_cols + ["l"]).groupby(group_cols, sort=False, dropna=False):
        group = group.sort_values("l").reset_index(drop=True)
        group_budget = budget_by_row.loc[group["source_row_index"].astype(int).to_numpy()].reset_index(drop=True)
        delta, meta = _slice_source_profile(group, group_budget, package_scenario, package_spec)
        positions = group["domain_pos"].astype(int).to_numpy()
        profile[positions] = delta
        row = {
            "scenario": scenario.label,
            "assignment": str(group["assignment"].iloc[0]),
            "stage": str(group["stage"].iloc[0]),
            "region": str(group["region"].iloc[0]),
            "s": _finite(group["s"].iloc[0], float("nan")),
            "slice_s_key": _finite(group["slice_s_key"].iloc[0], float("nan")),
            "rows": int(len(group)),
            **meta,
        }
        rows.append(row)
    return profile, pd.DataFrame(rows)


def _sample_symbol_margins(
    active: pd.DataFrame,
    state_max: np.ndarray,
    fraction_max: np.ndarray,
    symbol_spec: PrincipalSymbolSpec,
    limit: int,
) -> tuple[float, int, pd.DataFrame]:
    finite = np.isfinite(fraction_max)
    if not np.any(finite):
        return float("nan"), -1, pd.DataFrame()
    order = np.argsort(np.where(finite, fraction_max, -np.inf))[::-1][: max(1, int(limit))]
    rows: list[dict[str, Any]] = []
    min_margin = float("inf")
    min_row = -1
    for pos in order:
        row = active.iloc[int(pos)]
        symbol = _symbol_at_delta_psi(row, float(state_max[int(pos)]), symbol_spec)
        margin = _finite(symbol.get("relative_cone_margin"), float("nan"))
        if math.isfinite(margin) and margin < min_margin:
            min_margin = margin
            min_row = int(row["source_row_index"])
        rows.append({
            "source_row_index": int(row["source_row_index"]),
            "assignment": str(row["assignment"]),
            "stage": str(row["stage"]),
            "region": str(row["region"]),
            "s": _finite(row["s"], float("nan")),
            "l": _finite(row["l"], float("nan")),
            "max_delta_psi": float(state_max[int(pos)]),
            "max_budget_fraction": float(fraction_max[int(pos)]),
            "relative_cone_margin": margin,
            "transport_margin": _finite(symbol.get("transport_margin"), float("nan")),
            "symbol_status": str(symbol.get("symbol_status", "")),
        })
    if not math.isfinite(min_margin):
        min_margin = float("nan")
    return min_margin, min_row, pd.DataFrame(rows)


def _run_domain_scenario(
    active: pd.DataFrame,
    budget: pd.DataFrame,
    scenario: FullSystemEvolutionScenario,
    *,
    radial_groups: list[np.ndarray],
    service_groups: list[np.ndarray],
    spec: FullSystemEvolutionSpec,
    symbol_spec: PrincipalSymbolSpec,
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    source_profile, profile_rows = _source_profile_for_scenario(active, budget, scenario, spec)
    envelope = _temporal_envelope(spec.steps, spec.temporal_profile)
    state = np.zeros(len(active), dtype=float)
    state_max = np.zeros(len(active), dtype=float)
    fraction_max = np.zeros(len(active), dtype=float)
    clip_total = np.zeros(len(active), dtype=float)
    budgets = active["max_admissible_delta_psi"].astype(float).to_numpy()
    baseline_fail = active["baseline_relative_cone_margin"].astype(float).to_numpy() < float(symbol_spec.speed_margin_gate)
    source_sum = 0.0
    max_state_sum_to_source = 0.0
    limiter_steps = 0
    for weight in envelope:
        increment = source_profile * float(weight)
        source_sum += float(np.sum(increment))
        state = state + increment
        state = _advect_groups(state, radial_groups, cfl=spec.radial_cfl, direction=scenario.radial_direction)
        state = _advect_groups(state, service_groups, cfl=spec.service_cfl, direction=scenario.service_direction)
        clipped = np.zeros_like(state)
        if scenario.budget_limiter:
            state, clipped = _apply_budget_limiter(
                state,
                budgets,
                safety_fraction=spec.limiter_safety_fraction,
            )
            if bool(np.any(clipped > 0.0)):
                limiter_steps += 1
                clip_total += clipped
        fraction = _safe_budget_fraction(state, budgets)
        state_max = np.maximum(state_max, state)
        fraction_max = np.maximum(fraction_max, fraction)
        if source_sum > 0.0:
            max_state_sum_to_source = max(max_state_sum_to_source, float(np.sum(state) / source_sum))
    over_budget = fraction_max > 1.0
    fail_mask = baseline_fail | over_budget
    final_ratio = np.tanh(
        np.arctanh(active["regulated_heat_flux_ratio"].astype(float).clip(lower=0.0, upper=1.0 - 1.0e-15).to_numpy())
        + state_max
    )
    min_margin, min_margin_row, sampled = _sample_symbol_margins(
        active,
        state_max,
        fraction_max,
        symbol_spec,
        spec.top_row_count,
    )
    worst_pos = int(np.nanargmax(np.where(np.isfinite(fraction_max), fraction_max, -np.inf))) if len(fraction_max) else 0
    summary = {
        "scenario": scenario.label,
        "heat_ratio_delta": float(scenario.heat_ratio_delta),
        "radial_direction": str(scenario.radial_direction),
        "service_direction": str(scenario.service_direction),
        "budget_limiter": bool(scenario.budget_limiter),
        "source_scale": float(scenario.source_scale),
        "status": "fail" if bool(np.any(fail_mask)) else "limited_pass" if limiter_steps else "pass",
        "hard_pass": bool(not np.any(fail_mask)),
        "rows": int(len(active)),
        "fail_rows_any_time": int(np.sum(fail_mask)),
        "baseline_fail_rows": int(np.sum(baseline_fail)),
        "over_budget_rows_any_time": int(np.sum(over_budget)),
        "max_budget_fraction": float(np.nanmax(fraction_max)) if len(fraction_max) else float("nan"),
        "worst_source_row_index": int(active.iloc[worst_pos]["source_row_index"]) if len(active) else -1,
        "worst_assignment": str(active.iloc[worst_pos]["assignment"]) if len(active) else "",
        "worst_stage": str(active.iloc[worst_pos]["stage"]) if len(active) else "",
        "worst_region": str(active.iloc[worst_pos]["region"]) if len(active) else "",
        "worst_s": _finite(active.iloc[worst_pos]["s"], float("nan")) if len(active) else float("nan"),
        "worst_l": _finite(active.iloc[worst_pos]["l"], float("nan")) if len(active) else float("nan"),
        "max_delta_psi": float(np.nanmax(state_max)) if len(state_max) else float("nan"),
        "min_relative_cone_margin_sample": min_margin,
        "min_relative_cone_margin_sample_row": min_margin_row,
        "min_transport_margin": float(np.min(1.0 - final_ratio)) if len(final_ratio) else float("nan"),
        "limiter_active_steps": int(limiter_steps),
        "limiter_clipped_rows": int(np.sum(clip_total > 0.0)),
        "max_limiter_clip_delta_psi": float(np.max(clip_total)) if len(clip_total) else 0.0,
        "source_delta_psi_sum": source_sum,
        "final_state_delta_psi_sum": float(np.sum(state)),
        "max_state_sum_to_source_sum": max_state_sum_to_source,
        "state_amplification_violation": bool(max_state_sum_to_source > 1.0 + 1.0e-9),
    }
    sampled["scenario"] = scenario.label
    return summary, profile_rows, sampled


def _run_domain_scenario_worker(
    payload: tuple[
        pd.DataFrame,
        pd.DataFrame,
        FullSystemEvolutionScenario,
        list[np.ndarray],
        list[np.ndarray],
        FullSystemEvolutionSpec,
        PrincipalSymbolSpec,
    ]
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    active, budget, scenario, radial_groups, service_groups, spec, symbol_spec = payload
    return _run_domain_scenario(
        active,
        budget,
        scenario,
        radial_groups=radial_groups,
        service_groups=service_groups,
        spec=spec,
        symbol_spec=symbol_spec,
    )


def _domain_audit(point_closure: pd.DataFrame, active: pd.DataFrame) -> pd.DataFrame:
    active_source_rows = int(len(active))
    live_rows = int(_bool_series(active["covariant_divergence_live"]).sum()) if "covariant_divergence_live" in active else 0
    packet_live_rows = int(_bool_series(active["inside_packet_live"]).sum()) if "inside_packet_live" in active else 0
    active_assignments = ",".join(sorted(active["assignment"].astype(str).unique()))
    active_regions = ",".join(sorted(active["region"].astype(str).unique()))
    return pd.DataFrame([{
        "point_rows": int(len(point_closure)),
        "active_source_rows": active_source_rows,
        "active_live_rows": live_rows,
        "active_packet_live_rows": packet_live_rows,
        "active_assignments": active_assignments,
        "active_regions": active_regions,
        "live_support_exclusion_pass": bool(live_rows == 0 and packet_live_rows == 0),
    }])


def _decision(scenario_summary: pd.DataFrame, domain_audit: pd.DataFrame, observed_delta: float) -> pd.DataFrame:
    observed = scenario_summary.loc[
        (scenario_summary["heat_ratio_delta"].astype(float) <= float(observed_delta) + 1.0e-15)
        & (~scenario_summary["budget_limiter"].astype(bool))
    ]
    observed_limited = scenario_summary.loc[
        (scenario_summary["heat_ratio_delta"].astype(float) <= float(observed_delta) + 1.0e-15)
        & (scenario_summary["budget_limiter"].astype(bool))
    ]
    large_unlimited = scenario_summary.loc[
        (scenario_summary["heat_ratio_delta"].astype(float) > float(observed_delta) + 1.0e-15)
        & (~scenario_summary["budget_limiter"].astype(bool))
    ]
    large_limited = scenario_summary.loc[
        (scenario_summary["heat_ratio_delta"].astype(float) > float(observed_delta) + 1.0e-15)
        & (scenario_summary["budget_limiter"].astype(bool))
    ]
    observed_pass = bool(len(observed) and observed["hard_pass"].astype(bool).all())
    observed_limiter_inactive = bool(
        not len(observed_limited)
        or (
            observed_limited["hard_pass"].astype(bool).all()
            and int(observed_limited["limiter_clipped_rows"].astype(int).max()) == 0
        )
    )
    no_state_amplification = bool((scenario_summary["state_amplification_violation"].astype(bool) == False).all())
    live_exclusion = bool(domain_audit["live_support_exclusion_pass"].iloc[0])
    large_unlimited_fails = bool(len(large_unlimited) and (~large_unlimited["hard_pass"].astype(bool)).any())
    large_limited_passes = bool(len(large_limited) and large_limited["hard_pass"].astype(bool).all())
    hard_ready = observed_pass and observed_limiter_inactive and no_state_amplification and live_exclusion
    status = (
        "full_system_evolution_pass_with_watches"
        if hard_ready and (large_unlimited_fails or len(large_unlimited))
        else "full_system_evolution_pass"
        if hard_ready
        else "full_system_evolution_fail"
    )
    read = (
        "sealed beta075 passes the observed-amplitude fixed-background full-domain evolution stress test, with large-stress and smoothness watches carried forward"
        if status == "full_system_evolution_pass_with_watches"
        else "sealed beta075 passes the observed-amplitude fixed-background full-domain evolution stress test"
        if status == "full_system_evolution_pass"
        else "sealed beta075 fails the observed-amplitude fixed-background full-domain evolution stress test"
    )
    return pd.DataFrame([{
        "full_system_evolution_status": status,
        "observed_unlimited_pass": observed_pass,
        "observed_limiter_inactive": observed_limiter_inactive,
        "no_state_amplification": no_state_amplification,
        "live_support_exclusion_pass": live_exclusion,
        "large_unlimited_fails": large_unlimited_fails,
        "large_limited_passes": large_limited_passes,
        "max_observed_unlimited_budget_fraction": float(observed["max_budget_fraction"].astype(float).max()) if len(observed) else float("nan"),
        "max_large_unlimited_budget_fraction": float(large_unlimited["max_budget_fraction"].astype(float).max()) if len(large_unlimited) else float("nan"),
        "max_state_sum_to_source_sum": float(scenario_summary["max_state_sum_to_source_sum"].astype(float).max()) if len(scenario_summary) else float("nan"),
        "decision_read": read,
    }])


def build_full_system_evolution(
    closure_dir: Path,
    source_coupling_dir: Path,
    *,
    symbol_spec: PrincipalSymbolSpec | None = None,
    spec: FullSystemEvolutionSpec | None = None,
    scenarios: list[FullSystemEvolutionScenario] | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any], str]:
    symbol_spec = symbol_spec or PrincipalSymbolSpec()
    spec = spec or FullSystemEvolutionSpec()
    scenarios = scenarios or default_scenarios(spec)
    point_closure, closure_manifest, point_path = _load_closure_dir(closure_dir)
    active, budget, provenance = _prepare_domain(closure_dir, source_coupling_dir, spec)
    radial_groups = _build_groups(active, ["assignment", "stage", "region", "slice_s_key"], "l")
    service_groups = _build_groups(active, ["assignment", "region", "l_key"], "s")
    payloads = [
        (active, budget, scenario, radial_groups, service_groups, spec, symbol_spec)
        for scenario in scenarios
    ]
    workers = min(_worker_count(spec.max_workers), max(1, len(payloads)))
    if workers <= 1 or len(payloads) <= 1:
        mapped = [_run_domain_scenario_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            mapped = list(pool.map(_run_domain_scenario_worker, payloads))
    summary_rows = [summary for summary, _, _ in mapped]
    profile_frames = [profile for _, profile, _ in mapped]
    sampled_frames = [sampled for _, _, sampled in mapped]
    scenario_summary = pd.DataFrame(summary_rows)
    domain_audit = _domain_audit(point_closure, active)
    decision = _decision(scenario_summary, domain_audit, spec.observed_heat_ratio_delta)
    source_profile_summary = pd.concat(profile_frames, ignore_index=True) if profile_frames else pd.DataFrame()
    sampled_worst = pd.concat(sampled_frames, ignore_index=True) if sampled_frames else pd.DataFrame()
    if len(sampled_worst):
        sampled_worst = sampled_worst.sort_values(["max_budget_fraction"], ascending=False).head(int(spec.top_row_count))
    outputs = {
        "domain_audit": domain_audit,
        "scenario_summary": scenario_summary,
        "source_profile_summary": source_profile_summary,
        "sampled_worst_rows": sampled_worst,
        "decision": decision,
    }
    metadata = {
        "source_name": "beta075_full_system_evolution",
        "closure_dir": str(closure_dir),
        "source_coupling_dir": str(source_coupling_dir),
        "point_closure": str(point_path),
        "point_closure_sha256": sha256_file(point_path),
        "closure_source_name": closure_manifest.get("source_name", ""),
        "symbol_spec": symbol_spec.__dict__,
        "rapidity_budget_spec": RapidityBudgetSpec(
            observed_heat_ratio_delta=spec.observed_heat_ratio_delta,
            reference_large_heat_ratio_delta=spec.reference_large_heat_ratio_delta,
            speed_margin_gate=symbol_spec.speed_margin_gate,
        ).__dict__,
        "evolution_spec": spec.__dict__,
        "scenarios": [scenario.__dict__ for scenario in scenarios],
        "radial_group_count": len(radial_groups),
        "service_group_count": len(service_groups),
        "scenario_workers": workers,
        "provenance": provenance,
        "caveat": (
            "Fixed-background split-step evolution over the active non-live beta075 support-source domain. "
            "It evolves the bounded rapidity perturbation on the sealed prescribed metric and checks local "
            "cone/transport budgets, live exclusion, source localization, and state amplification. It is not "
            "a coupled Einstein-matter evolution or final PDE theorem."
        ),
    }
    return outputs, metadata, _report(outputs, metadata)


def _fmt(value: Any) -> str:
    number = _finite(value, float("nan"))
    if not math.isfinite(number):
        return "nan"
    if abs(number) > 0 and (abs(number) < 1.0e-4 or abs(number) >= 1.0e5):
        return f"{number:.3e}"
    return f"{number:.6f}"


def _report(outputs: dict[str, pd.DataFrame], metadata: dict[str, Any]) -> str:
    decision = outputs["decision"].iloc[0]
    domain = outputs["domain_audit"].iloc[0]
    summary = outputs["scenario_summary"]
    lines = [
        "# Stage II Beta075 Full-System Fixed-Background Evolution Stress Test",
        "",
        "## Status",
        "",
        f"Overall status: `{decision['full_system_evolution_status']}`.",
        "",
        str(decision["decision_read"]).capitalize() + ".",
        "",
        "This is the first full-domain fixed-background evolution rung after the bounded seal gate. It uses the sealed beta075 support package as input, not as an optimization target, and evolves a bounded-rapidity perturbation over the active non-live support-source surface with radial and service-time upwind transport.",
        "",
        "## Domain",
        "",
        "| point rows | active source rows | live evolved rows | packet-live evolved rows | radial groups | service groups |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
        f"| {int(domain['point_rows'])} | {int(domain['active_source_rows'])} | {int(domain['active_live_rows'])} | "
        f"{int(domain['active_packet_live_rows'])} | {int(metadata['radial_group_count'])} | {int(metadata['service_group_count'])} |",
        "",
        f"Scenario workers: `{int(metadata['scenario_workers'])}`.",
        "",
        "## Scenario Summary",
        "",
        "| scenario | status | limiter | fail rows | over-budget rows | max budget fraction | min cone margin | min transport margin | max state/source | clipped rows |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['scenario']} | {row['status']} | {bool(row['budget_limiter'])} | "
            f"{int(row['fail_rows_any_time'])} | {int(row['over_budget_rows_any_time'])} | "
            f"{_fmt(row['max_budget_fraction'])} | {_fmt(row['min_relative_cone_margin_sample'])} | "
            f"{_fmt(row['min_transport_margin'])} | {_fmt(row['max_state_sum_to_source_sum'])} | "
            f"{int(row['limiter_clipped_rows'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "The hard read is the observed-amplitude rows. They must pass without limiter clipping, live-row evolution, or state amplification. Large-amplitude rows are retained as engineering-margin watches, not as the observed-amplitude seal driver.",
        "",
        "If this rung fails, the failure location is allowed to point back to a component. If it passes, the sealed beta075 package should move upward to action-level, fixed-background PDE proof, or broader full-system obligations rather than same-level tuning.",
        "",
        "## Provenance",
        "",
        f"- closure dir: `{metadata['closure_dir']}`",
        f"- source-coupling dir: `{metadata['source_coupling_dir']}`",
        f"- point closure: `{metadata['point_closure']}`",
        f"- caveat: {metadata['caveat']}",
    ])
    return "\n".join(lines) + "\n"


def write_full_system_evolution_outputs(
    outdir: Path,
    report_path: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
    report: str,
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    paths = {
        "domain_audit": outdir / "beta075_full_system_evolution_domain_audit.csv",
        "scenario_summary": outdir / "beta075_full_system_evolution_scenario_summary.csv",
        "source_profile_summary": outdir / "beta075_full_system_evolution_source_profile_summary.csv",
        "sampled_worst_rows": outdir / "beta075_full_system_evolution_sampled_worst_rows.csv",
        "decision": outdir / "beta075_full_system_evolution_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    report_path.write_text(report)
    paths["report"] = report_path
    manifest_path = outdir / "beta075_full_system_evolution_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
