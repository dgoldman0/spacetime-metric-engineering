from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .beta075_aligned_envelope_certificate import _basis_source_bins, _max_fraction_position
from .beta075_full_system_evolution import (
    FullSystemEvolutionScenario,
    FullSystemEvolutionSpec,
    _advect_groups,
    _build_groups,
    _domain_audit,
    _prepare_domain,
    _sample_symbol_margins,
    _source_profile_for_scenario,
    _worker_count,
)
from .endpoint_support_principal_symbol import PrincipalSymbolSpec, _finite
from .endpoint_support_rapidity_advection import _apply_budget_limiter
from .endpoint_support_source_coupling_package import _safe_budget_fraction
from .endpoint_support_source_dynamics import _load_closure_dir
from .source_ledger import sha256_file, write_manifest


@dataclass(frozen=True)
class Constitutive1p1Spec:
    observed_heat_ratio_delta: float = 1.0e-4
    reference_large_heat_ratio_delta: float = 5.0e-4
    steps: int = 48
    tail_steps: int = 48
    radial_cfl: float = 0.40
    service_cfl: float = 0.20
    limiter_safety_fraction: float = 0.95
    source_column: str = "candidate_support_abs_PF_density"
    source_smoothing_passes: int = 0
    source_profile_budget_cap_scope: str = "support_edge_entry_catch"
    source_profile_budget_cap_fraction: float = 0.95
    source_profile_budget_cap_reference_delta: float | None = None
    s_round_decimals: int = 12
    l_round_decimals: int = 12
    top_row_count: int = 160
    max_workers: int | None = 6


@dataclass(frozen=True)
class Constitutive1p1Scenario:
    label: str
    heat_ratio_delta: float
    radial_direction: str
    service_direction: str
    budget_limiter: bool = False
    source_scale: float = 1.0
    timing_offset_steps: int = 0
    gate_role: str = "observed"


def default_constitutive_scenarios(spec: Constitutive1p1Spec | None = None) -> list[Constitutive1p1Scenario]:
    spec = spec or Constitutive1p1Spec()
    observed = float(spec.observed_heat_ratio_delta)
    large = float(spec.reference_large_heat_ratio_delta)
    return [
        Constitutive1p1Scenario(
            "observed_constitutive_outward_forward_unlimited",
            observed,
            "outward",
            "forward",
            False,
            gate_role="observed_driver",
        ),
        Constitutive1p1Scenario(
            "observed_constitutive_inward_forward_unlimited",
            observed,
            "inward",
            "forward",
            False,
            gate_role="observed_driver",
        ),
        Constitutive1p1Scenario(
            "observed_constitutive_outward_backward_unlimited",
            observed,
            "outward",
            "backward",
            False,
            gate_role="observed_driver",
        ),
        Constitutive1p1Scenario(
            "observed_constitutive_outward_forward_budget_limited",
            observed,
            "outward",
            "forward",
            True,
            gate_role="observed_limiter_guard",
        ),
        Constitutive1p1Scenario(
            "observed_constitutive_inward_forward_budget_limited",
            observed,
            "inward",
            "forward",
            True,
            gate_role="observed_limiter_guard",
        ),
        Constitutive1p1Scenario(
            "observed_constitutive_outward_backward_budget_limited",
            observed,
            "outward",
            "backward",
            True,
            gate_role="observed_limiter_guard",
        ),
        Constitutive1p1Scenario(
            "large_constitutive_outward_forward_unlimited",
            large,
            "outward",
            "forward",
            False,
            gate_role="engineering_margin_watch",
        ),
        Constitutive1p1Scenario(
            "large_constitutive_outward_forward_budget_limited",
            large,
            "outward",
            "forward",
            True,
            gate_role="engineering_margin_watch",
        ),
    ]


def _evolution_spec(spec: Constitutive1p1Spec) -> FullSystemEvolutionSpec:
    return FullSystemEvolutionSpec(
        observed_heat_ratio_delta=float(spec.observed_heat_ratio_delta),
        reference_large_heat_ratio_delta=float(spec.reference_large_heat_ratio_delta),
        steps=int(spec.steps),
        radial_cfl=float(spec.radial_cfl),
        service_cfl=float(spec.service_cfl),
        limiter_safety_fraction=float(spec.limiter_safety_fraction),
        source_column=str(spec.source_column),
        source_smoothing_passes=int(spec.source_smoothing_passes),
        source_profile_budget_cap_scope=str(spec.source_profile_budget_cap_scope),
        source_profile_budget_cap_fraction=float(spec.source_profile_budget_cap_fraction),
        source_profile_budget_cap_reference_delta=spec.source_profile_budget_cap_reference_delta,
        s_round_decimals=int(spec.s_round_decimals),
        l_round_decimals=int(spec.l_round_decimals),
        top_row_count=int(spec.top_row_count),
        max_workers=1,
    )


def _full_scenario(scenario: Constitutive1p1Scenario) -> FullSystemEvolutionScenario:
    return FullSystemEvolutionScenario(
        label=scenario.label,
        heat_ratio_delta=float(scenario.heat_ratio_delta),
        radial_direction=str(scenario.radial_direction),
        service_direction=str(scenario.service_direction),
        budget_limiter=bool(scenario.budget_limiter),
        source_scale=float(scenario.source_scale),
    )


def _scheduled_bins(active: pd.DataFrame, scenario: Constitutive1p1Scenario, spec: Constitutive1p1Spec) -> np.ndarray:
    base = _basis_source_bins(
        active,
        steps=int(spec.steps),
        service_direction=str(scenario.service_direction),
    )
    return np.clip(base + int(scenario.timing_offset_steps), 0, int(spec.steps) - 1).astype(int)


def _scenario_source_bin_summary(
    active: pd.DataFrame,
    source_profile: np.ndarray,
    bins: np.ndarray,
    scenario: Constitutive1p1Scenario,
    spec: Constitutive1p1Spec,
) -> pd.DataFrame:
    total = float(np.sum(source_profile))
    rows: list[dict[str, Any]] = []
    for step in range(int(spec.steps)):
        mask = bins == step
        source_sum = float(np.sum(source_profile[mask]))
        rows.append({
            "scenario": scenario.label,
            "gate_role": scenario.gate_role,
            "service_direction": scenario.service_direction,
            "timing_offset_steps": int(scenario.timing_offset_steps),
            "step": int(step),
            "rows": int(np.sum(mask)),
            "source_delta_psi_sum": source_sum,
            "source_fraction": source_sum / total if total > 0.0 else 0.0,
        })
    return pd.DataFrame(rows)


def _run_scenario(
    active: pd.DataFrame,
    budget: pd.DataFrame,
    scenario: Constitutive1p1Scenario,
    *,
    radial_groups: list[np.ndarray],
    service_groups: list[np.ndarray],
    spec: Constitutive1p1Spec,
    evolution_spec: FullSystemEvolutionSpec,
    symbol_spec: PrincipalSymbolSpec,
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    source_profile, profile_rows = _source_profile_for_scenario(active, budget, _full_scenario(scenario), evolution_spec)
    profile_rows = profile_rows.copy()
    profile_rows["scenario"] = scenario.label
    profile_rows["gate_role"] = scenario.gate_role
    profile_rows["heat_ratio_delta"] = float(scenario.heat_ratio_delta)
    profile_rows["budget_limiter"] = bool(scenario.budget_limiter)
    bins = _scheduled_bins(active, scenario, spec)
    bin_summary = _scenario_source_bin_summary(active, source_profile, bins, scenario, spec)
    budgets = active["max_admissible_delta_psi"].astype(float).to_numpy()
    baseline_fail = active["baseline_relative_cone_margin"].astype(float).to_numpy() < float(symbol_spec.speed_margin_gate)
    state = np.zeros(len(active), dtype=float)
    state_max = np.zeros(len(active), dtype=float)
    fraction_max = np.zeros(len(active), dtype=float)
    clip_total = np.zeros(len(active), dtype=float)
    source_total = float(np.sum(source_profile))
    injected_total = 0.0
    active_source_steps = 0
    max_step_source_fraction = 0.0
    max_state_sum_to_source = 0.0
    limiter_steps = 0
    for step in range(int(spec.steps) + int(spec.tail_steps)):
        if step < int(spec.steps):
            increment = np.where(bins == step, source_profile, 0.0)
            step_source = float(np.sum(increment))
            if step_source > 0.0:
                active_source_steps += 1
            injected_total += step_source
            if source_total > 0.0:
                max_step_source_fraction = max(max_step_source_fraction, step_source / source_total)
            state = state + increment
        state = _advect_groups(state, radial_groups, cfl=float(spec.radial_cfl), direction=scenario.radial_direction)
        state = _advect_groups(state, service_groups, cfl=float(spec.service_cfl), direction=scenario.service_direction)
        clipped = np.zeros_like(state)
        if scenario.budget_limiter:
            state, clipped = _apply_budget_limiter(
                state,
                budgets,
                safety_fraction=float(spec.limiter_safety_fraction),
            )
            if bool(np.any(clipped > 0.0)):
                limiter_steps += 1
                clip_total += clipped
        state_max = np.maximum(state_max, state)
        fraction_max = np.maximum(fraction_max, _safe_budget_fraction(state, budgets))
        if injected_total > 0.0:
            max_state_sum_to_source = max(max_state_sum_to_source, float(np.sum(state) / injected_total))
    over_budget = fraction_max > 1.0
    fail_mask = baseline_fail | over_budget
    min_margin, min_margin_row, sampled = _sample_symbol_margins(
        active,
        state_max,
        fraction_max,
        symbol_spec,
        int(spec.top_row_count),
    )
    final_ratio = np.tanh(
        np.arctanh(active["regulated_heat_flux_ratio"].astype(float).clip(lower=0.0, upper=1.0 - 1.0e-15).to_numpy())
        + state_max
    )
    worst_pos = _max_fraction_position(fraction_max)
    status = "fail" if bool(np.any(fail_mask)) else "limited_pass" if limiter_steps else "pass"
    summary = {
        "scenario": scenario.label,
        "gate_role": scenario.gate_role,
        "heat_ratio_delta": float(scenario.heat_ratio_delta),
        "radial_direction": scenario.radial_direction,
        "service_direction": scenario.service_direction,
        "budget_limiter": bool(scenario.budget_limiter),
        "source_scale": float(scenario.source_scale),
        "timing_offset_steps": int(scenario.timing_offset_steps),
        "status": status,
        "hard_pass": bool(not np.any(fail_mask)),
        "steps": int(spec.steps),
        "tail_steps": int(spec.tail_steps),
        "rows": int(len(active)),
        "fail_rows_any_time": int(np.sum(fail_mask)),
        "baseline_fail_rows": int(np.sum(baseline_fail)),
        "over_budget_rows_any_time": int(np.sum(over_budget)),
        "max_budget_fraction": float(fraction_max[worst_pos]) if len(fraction_max) else float("nan"),
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
        "source_delta_psi_sum": source_total,
        "min_source_delta_psi": float(np.min(source_profile)) if len(source_profile) else float("nan"),
        "negative_source_rows": int(np.sum(source_profile < -1.0e-15)),
        "injected_delta_psi_sum": injected_total,
        "active_source_steps": active_source_steps,
        "max_step_source_fraction": max_step_source_fraction,
        "final_state_delta_psi_sum": float(np.sum(state)),
        "max_state_sum_to_source_sum": max_state_sum_to_source,
        "state_amplification_violation": bool(max_state_sum_to_source > 1.0 + 1.0e-9),
        "limiter_active_steps": int(limiter_steps),
        "limiter_clipped_rows": int(np.sum(clip_total > 0.0)),
        "max_limiter_clip_delta_psi": float(np.max(clip_total)) if len(clip_total) else 0.0,
    }
    sampled["scenario"] = scenario.label
    sampled["gate_role"] = scenario.gate_role
    sampled["certificate"] = "constitutive_1p1_source_coupled"
    return summary, profile_rows, bin_summary, sampled


def _run_scenario_worker(
    payload: tuple[
        pd.DataFrame,
        pd.DataFrame,
        Constitutive1p1Scenario,
        list[np.ndarray],
        list[np.ndarray],
        Constitutive1p1Spec,
        FullSystemEvolutionSpec,
        PrincipalSymbolSpec,
    ]
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    active, budget, scenario, radial_groups, service_groups, spec, evolution_spec, symbol_spec = payload
    return _run_scenario(
        active,
        budget,
        scenario,
        radial_groups=radial_groups,
        service_groups=service_groups,
        spec=spec,
        evolution_spec=evolution_spec,
        symbol_spec=symbol_spec,
    )


def _source_law_summary(source_profile_summary: pd.DataFrame, observed_delta: float) -> pd.DataFrame:
    if not len(source_profile_summary):
        return pd.DataFrame()
    observed = source_profile_summary.loc[
        (source_profile_summary["heat_ratio_delta"].astype(float) <= float(observed_delta) + 1.0e-15)
        & source_profile_summary["gate_role"].astype(str).eq("observed_driver")
    ].copy()
    if not len(observed):
        return pd.DataFrame()
    observed = observed.drop_duplicates(["assignment", "stage", "region", "slice_s_key"]).copy()
    observed["source_profile_scale"] = pd.to_numeric(observed["source_profile_scale"], errors="coerce").fillna(1.0)
    observed["source_profile_budget_cap_applied"] = observed["source_profile_budget_cap_applied"].astype(bool)
    observed["scale_below_one"] = observed["source_profile_scale"].astype(float) < 1.0 - 1.0e-12
    rows: list[dict[str, Any]] = []
    for (assignment, stage, region), group in observed.groupby(["assignment", "stage", "region"], sort=True):
        rows.append({
            "assignment": str(assignment),
            "stage": str(stage),
            "region": str(region),
            "slices": int(len(group)),
            "rows": int(group["rows"].astype(int).sum()),
            "cap_applied_slices": int(group["source_profile_budget_cap_applied"].astype(bool).sum()),
            "scaled_slices": int(group["scale_below_one"].astype(bool).sum()),
            "min_source_profile_scale": float(group["source_profile_scale"].astype(float).min()),
            "max_source_profile_scale": float(group["source_profile_scale"].astype(float).max()),
            "max_raw_reference_budget_fraction": float(
                group["source_profile_raw_reference_budget_fraction"].astype(float).replace([np.inf, -np.inf], np.nan).max()
            ),
            "min_bottleneck_budget_delta_psi": float(group["bottleneck_budget_delta_psi"].astype(float).min()),
        })
    return pd.DataFrame(rows)


def _source_law_gate(source_law_summary: pd.DataFrame) -> dict[str, Any]:
    if not len(source_law_summary):
        return {
            "source_law_bounded": False,
            "source_law_phase_local": False,
            "scaled_slices": 0,
            "scaled_outside_expected_scope_slices": 0,
            "min_source_profile_scale": float("nan"),
        }
    scale = source_law_summary["min_source_profile_scale"].astype(float)
    bounded = bool((scale >= -1.0e-12).all() and (source_law_summary["max_source_profile_scale"].astype(float) <= 1.0 + 1.0e-12).all())
    expected = (
        source_law_summary["assignment"].astype(str).eq("support_edge_endpoint_junction")
        & source_law_summary["region"].astype(str).eq("support_edge")
        & source_law_summary["stage"].astype(str).isin(["entry_precatch", "catch_rematch"])
    )
    scaled = source_law_summary["scaled_slices"].astype(int) > 0
    outside = int((scaled & (~expected)).sum())
    return {
        "source_law_bounded": bounded,
        "source_law_phase_local": outside == 0,
        "scaled_slices": int(source_law_summary["scaled_slices"].astype(int).sum()),
        "scaled_outside_expected_scope_slices": outside,
        "min_source_profile_scale": float(scale.min()),
    }


def _decision(
    scenario_summary: pd.DataFrame,
    domain_audit: pd.DataFrame,
    source_law_summary: pd.DataFrame,
    observed_delta: float,
) -> pd.DataFrame:
    live_pass = bool(domain_audit["live_support_exclusion_pass"].iloc[0])
    observed = scenario_summary.loc[
        (scenario_summary["heat_ratio_delta"].astype(float) <= float(observed_delta) + 1.0e-15)
        & (~scenario_summary["budget_limiter"].astype(bool))
    ]
    observed_limited = scenario_summary.loc[
        (scenario_summary["heat_ratio_delta"].astype(float) <= float(observed_delta) + 1.0e-15)
        & scenario_summary["budget_limiter"].astype(bool)
    ]
    large_unlimited = scenario_summary.loc[
        (scenario_summary["heat_ratio_delta"].astype(float) > float(observed_delta) + 1.0e-15)
        & (~scenario_summary["budget_limiter"].astype(bool))
    ]
    large_limited = scenario_summary.loc[
        (scenario_summary["heat_ratio_delta"].astype(float) > float(observed_delta) + 1.0e-15)
        & scenario_summary["budget_limiter"].astype(bool)
    ]
    observed_pass = bool(len(observed) and observed["hard_pass"].astype(bool).all())
    observed_limiter_inactive = bool(
        len(observed_limited)
        and observed_limited["hard_pass"].astype(bool).all()
        and int(observed_limited["limiter_clipped_rows"].astype(int).max()) == 0
    )
    state_clean = bool((scenario_summary["state_amplification_violation"].astype(bool) == False).all())
    source_law = _source_law_gate(source_law_summary)
    hard_ready = (
        live_pass
        and observed_pass
        and observed_limiter_inactive
        and state_clean
        and bool(source_law["source_law_bounded"])
        and bool(source_law["source_law_phase_local"])
    )
    large_unlimited_pass = bool(len(large_unlimited) and large_unlimited["hard_pass"].astype(bool).all())
    large_limited_pass = bool(len(large_limited) and large_limited["hard_pass"].astype(bool).all())
    status = (
        "constitutive_1p1_observed_clean_with_margin_watches"
        if hard_ready
        else "constitutive_1p1_fail"
    )
    return pd.DataFrame([{
        "constitutive_1p1_status": status,
        "observed_unlimited_pass": observed_pass,
        "observed_limiter_inactive": observed_limiter_inactive,
        "live_support_exclusion_pass": live_pass,
        "state_amplification_clean": state_clean,
        "source_law_bounded": bool(source_law["source_law_bounded"]),
        "source_law_phase_local": bool(source_law["source_law_phase_local"]),
        "scaled_slices": int(source_law["scaled_slices"]),
        "scaled_outside_expected_scope_slices": int(source_law["scaled_outside_expected_scope_slices"]),
        "min_source_profile_scale": float(source_law["min_source_profile_scale"]),
        "large_unlimited_pass": large_unlimited_pass,
        "large_limited_pass": large_limited_pass,
        "max_observed_unlimited_budget_fraction": float(observed["max_budget_fraction"].astype(float).max()) if len(observed) else float("nan"),
        "max_large_unlimited_budget_fraction": float(large_unlimited["max_budget_fraction"].astype(float).max()) if len(large_unlimited) else float("nan"),
        "max_state_sum_to_source_sum": float(scenario_summary["max_state_sum_to_source_sum"].astype(float).max()) if len(scenario_summary) else float("nan"),
    }])


def build_constitutive_1p1_source_coupled(
    closure_dir: Path,
    source_coupling_dir: Path,
    *,
    symbol_spec: PrincipalSymbolSpec | None = None,
    spec: Constitutive1p1Spec | None = None,
    scenarios: list[Constitutive1p1Scenario] | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    symbol_spec = symbol_spec or PrincipalSymbolSpec()
    spec = spec or Constitutive1p1Spec()
    scenarios = scenarios or default_constitutive_scenarios(spec)
    point_closure, closure_manifest, point_path = _load_closure_dir(closure_dir)
    evolution_spec = _evolution_spec(spec)
    active, budget, provenance = _prepare_domain(closure_dir, source_coupling_dir, evolution_spec)
    radial_groups = _build_groups(active, ["assignment", "stage", "region", "slice_s_key"], "l")
    service_groups = _build_groups(active, ["assignment", "region", "l_key"], "s")
    payloads = [
        (active, budget, scenario, radial_groups, service_groups, spec, evolution_spec, symbol_spec)
        for scenario in scenarios
    ]
    workers = min(_worker_count(spec.max_workers), max(1, len(payloads)))
    if workers <= 1 or len(payloads) <= 1:
        mapped = [_run_scenario_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            mapped = list(pool.map(_run_scenario_worker, payloads))
    scenario_summary = pd.DataFrame([summary for summary, _, _, _ in mapped])
    source_profile_summary = pd.concat([frame for _, frame, _, _ in mapped], ignore_index=True) if mapped else pd.DataFrame()
    source_bin_summary = pd.concat([frame for _, _, frame, _ in mapped], ignore_index=True) if mapped else pd.DataFrame()
    sampled = pd.concat([frame for _, _, _, frame in mapped], ignore_index=True) if mapped else pd.DataFrame()
    if len(sampled):
        ordered = sampled.sort_values(["max_budget_fraction"], ascending=False)
        global_top = ordered.head(int(spec.top_row_count))
        per_scenario = ordered.groupby("scenario", sort=False, group_keys=False).head(
            max(1, min(20, int(spec.top_row_count)))
        )
        sampled = (
            pd.concat([global_top, per_scenario], ignore_index=True)
            .drop_duplicates(["scenario", "source_row_index"])
            .sort_values(["max_budget_fraction"], ascending=False)
            .reset_index(drop=True)
        )
    domain_audit = _domain_audit(point_closure, active)
    source_law_summary = _source_law_summary(source_profile_summary, spec.observed_heat_ratio_delta)
    decision = _decision(scenario_summary, domain_audit, source_law_summary, spec.observed_heat_ratio_delta)
    outputs = {
        "domain_audit": domain_audit,
        "scenario_summary": scenario_summary,
        "source_profile_summary": source_profile_summary,
        "source_bin_summary": source_bin_summary,
        "source_law_summary": source_law_summary,
        "sampled_worst_rows": sampled,
        "decision": decision,
    }
    metadata = {
        "source_name": "beta075_constitutive_1p1_source_coupled",
        "closure_dir": str(closure_dir),
        "source_coupling_dir": str(source_coupling_dir),
        "point_closure": str(point_path),
        "point_closure_sha256": sha256_file(point_path),
        "closure_source_name": closure_manifest.get("source_name", ""),
        "symbol_spec": symbol_spec.__dict__,
        "constitutive_1p1_spec": spec.__dict__,
        "scenarios": [scenario.__dict__ for scenario in scenarios],
        "radial_group_count": len(radial_groups),
        "service_group_count": len(service_groups),
        "scenario_workers": workers,
        "provenance": provenance,
        "claim_boundary": (
            "Full 1+1 fixed-background constitutive source-coupled evolution for the sealed beta075 package. "
            "The source term is the cap-0.95 phase-local support-source law released on the service-aligned "
            "schedule and evolved by radial plus service split-step bounded-rapidity transport. This is not "
            "a coupled Einstein-matter evolution or final matter-action theorem."
        ),
    }
    return outputs, metadata


def write_constitutive_1p1_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "domain_audit": outdir / "beta075_constitutive_1p1_domain_audit.csv",
        "scenario_summary": outdir / "beta075_constitutive_1p1_scenario_summary.csv",
        "source_profile_summary": outdir / "beta075_constitutive_1p1_source_profile_summary.csv",
        "source_bin_summary": outdir / "beta075_constitutive_1p1_source_bin_summary.csv",
        "source_law_summary": outdir / "beta075_constitutive_1p1_source_law_summary.csv",
        "sampled_worst_rows": outdir / "beta075_constitutive_1p1_sampled_worst_rows.csv",
        "decision": outdir / "beta075_constitutive_1p1_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    manifest_path = outdir / "beta075_constitutive_1p1_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
