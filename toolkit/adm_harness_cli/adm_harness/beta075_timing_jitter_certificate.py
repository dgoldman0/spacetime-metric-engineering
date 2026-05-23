from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .beta075_action_pde_obligation import ActionPDEScenario, default_action_scenarios
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
from .endpoint_support_source_coupling_package import _safe_budget_fraction
from .endpoint_support_source_dynamics import _load_closure_dir
from .source_ledger import sha256_file, write_manifest


@dataclass(frozen=True)
class TimingJitterSpec:
    observed_heat_ratio_delta: float = 1.0e-4
    steps: int = 48
    tail_steps: int = 48
    jitter_radii: tuple[int, ...] = (0, 1, 2, 3, 4, 6, 8)
    radial_cfl: float = 0.40
    service_cfl: float = 0.20
    source_column: str = "candidate_support_abs_PF_density"
    source_smoothing_passes: int = 0
    source_profile_budget_cap_scope: str = "support_edge_entry_catch"
    source_profile_budget_cap_fraction: float = 0.95
    source_profile_budget_cap_reference_delta: float | None = None
    s_round_decimals: int = 12
    l_round_decimals: int = 12
    top_row_count: int = 120
    max_workers: int | None = 6


def _evolution_spec(spec: TimingJitterSpec) -> FullSystemEvolutionSpec:
    return FullSystemEvolutionSpec(
        observed_heat_ratio_delta=float(spec.observed_heat_ratio_delta),
        reference_large_heat_ratio_delta=float(spec.observed_heat_ratio_delta),
        steps=int(spec.steps),
        radial_cfl=float(spec.radial_cfl),
        service_cfl=float(spec.service_cfl),
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


def _full_scenario(scenario: ActionPDEScenario, spec: TimingJitterSpec) -> FullSystemEvolutionScenario:
    return FullSystemEvolutionScenario(
        label=scenario.label,
        heat_ratio_delta=float(spec.observed_heat_ratio_delta),
        radial_direction=str(scenario.radial_direction),
        service_direction=str(scenario.service_direction),
        budget_limiter=False,
    )


def _jittered_source_bins(
    active: pd.DataFrame,
    *,
    steps: int,
    service_direction: str,
    offset_steps: int,
) -> np.ndarray:
    base = _basis_source_bins(active, steps=int(steps), service_direction=service_direction)
    return np.clip(base + int(offset_steps), 0, int(steps) - 1).astype(int)


def _jitter_bin_summary(
    active: pd.DataFrame,
    source_profile: np.ndarray,
    bins: np.ndarray,
    scenario: ActionPDEScenario,
    *,
    jitter_radius_steps: int,
    offset_steps: int,
    steps: int,
) -> pd.DataFrame:
    total = float(np.sum(source_profile))
    rows: list[dict[str, Any]] = []
    for step in range(int(steps)):
        mask = bins == step
        source_sum = float(np.sum(source_profile[mask]))
        rows.append({
            "scenario": scenario.label,
            "service_direction": scenario.service_direction,
            "jitter_radius_steps": int(jitter_radius_steps),
            "offset_steps": int(offset_steps),
            "step": int(step),
            "rows": int(np.sum(mask)),
            "source_delta_psi_sum": source_sum,
            "source_fraction": source_sum / total if total > 0.0 else 0.0,
        })
    return pd.DataFrame(rows)


def _run_offset_response(
    active: pd.DataFrame,
    source_profile: np.ndarray,
    scenario: ActionPDEScenario,
    *,
    jitter_radius_steps: int,
    offset_steps: int,
    radial_groups: list[np.ndarray],
    service_groups: list[np.ndarray],
    spec: TimingJitterSpec,
    symbol_spec: PrincipalSymbolSpec,
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    bins = _jittered_source_bins(
        active,
        steps=int(spec.steps),
        service_direction=scenario.service_direction,
        offset_steps=int(offset_steps),
    )
    bin_summary = _jitter_bin_summary(
        active,
        source_profile,
        bins,
        scenario,
        jitter_radius_steps=int(jitter_radius_steps),
        offset_steps=int(offset_steps),
        steps=int(spec.steps),
    )
    budgets = active["max_admissible_delta_psi"].astype(float).to_numpy()
    state = np.zeros(len(active), dtype=float)
    state_max = np.zeros(len(active), dtype=float)
    fraction_max = np.zeros(len(active), dtype=float)
    source_total = float(np.sum(source_profile))
    injected_total = 0.0
    max_state_sum_to_source = 0.0
    max_step_source_fraction = 0.0
    active_source_steps = 0
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
        state_max = np.maximum(state_max, state)
        fraction_max = np.maximum(fraction_max, _safe_budget_fraction(state, budgets))
        if injected_total > 0.0:
            max_state_sum_to_source = max(max_state_sum_to_source, float(np.sum(state) / injected_total))
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
    max_fraction = float(fraction_max[worst_pos]) if len(fraction_max) else float("nan")
    summary = {
        "scenario": scenario.label,
        "radial_direction": scenario.radial_direction,
        "service_direction": scenario.service_direction,
        "steps": int(spec.steps),
        "tail_steps": int(spec.tail_steps),
        "heat_ratio_delta": float(spec.observed_heat_ratio_delta),
        "jitter_radius_steps": int(jitter_radius_steps),
        "offset_steps": int(offset_steps),
        "offset_response_pass": bool(max_fraction <= 1.0 and max_state_sum_to_source <= 1.0 + 1.0e-9),
        "max_budget_fraction": max_fraction,
        "worst_source_row_index": int(active.iloc[worst_pos]["source_row_index"]) if len(active) else -1,
        "worst_assignment": str(active.iloc[worst_pos]["assignment"]) if len(active) else "",
        "worst_stage": str(active.iloc[worst_pos]["stage"]) if len(active) else "",
        "worst_region": str(active.iloc[worst_pos]["region"]) if len(active) else "",
        "worst_s": _finite(active.iloc[worst_pos]["s"], float("nan")) if len(active) else float("nan"),
        "worst_l": _finite(active.iloc[worst_pos]["l"], float("nan")) if len(active) else float("nan"),
        "min_relative_cone_margin_sample": min_margin,
        "min_relative_cone_margin_sample_row": min_margin_row,
        "min_transport_margin": float(np.min(1.0 - final_ratio)) if len(final_ratio) else float("nan"),
        "source_delta_psi_sum": source_total,
        "injected_delta_psi_sum": injected_total,
        "active_source_steps": active_source_steps,
        "max_step_source_fraction": max_step_source_fraction,
        "max_state_sum_to_source_sum": max_state_sum_to_source,
        "state_amplification_violation": bool(max_state_sum_to_source > 1.0 + 1.0e-9),
        "limiter_clipped_rows": 0,
    }
    sampled["scenario"] = scenario.label
    sampled["jitter_radius_steps"] = int(jitter_radius_steps)
    sampled["offset_steps"] = int(offset_steps)
    sampled["certificate"] = "service_timing_common_offset_jitter"
    return summary, bin_summary, sampled


def _run_radius_worker(
    payload: tuple[
        pd.DataFrame,
        np.ndarray,
        ActionPDEScenario,
        int,
        list[np.ndarray],
        list[np.ndarray],
        TimingJitterSpec,
        PrincipalSymbolSpec,
    ]
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    active, source_profile, scenario, radius, radial_groups, service_groups, spec, symbol_spec = payload
    summaries: list[dict[str, Any]] = []
    bin_frames: list[pd.DataFrame] = []
    sampled_frames: list[pd.DataFrame] = []
    for offset in range(-int(radius), int(radius) + 1):
        summary, bin_summary, sampled = _run_offset_response(
            active,
            source_profile,
            scenario,
            jitter_radius_steps=int(radius),
            offset_steps=int(offset),
            radial_groups=radial_groups,
            service_groups=service_groups,
            spec=spec,
            symbol_spec=symbol_spec,
        )
        summaries.append(summary)
        bin_frames.append(bin_summary)
        sampled_frames.append(sampled)
    return (
        pd.DataFrame(summaries),
        pd.concat(bin_frames, ignore_index=True) if bin_frames else pd.DataFrame(),
        pd.concat(sampled_frames, ignore_index=True) if sampled_frames else pd.DataFrame(),
    )


def _radius_summary(offset_summary: pd.DataFrame) -> pd.DataFrame:
    if not len(offset_summary):
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for radius, group in offset_summary.groupby("jitter_radius_steps", sort=True):
        max_idx = int(group["max_budget_fraction"].astype(float).idxmax())
        worst = offset_summary.loc[max_idx]
        radius_pass = bool(
            group["offset_response_pass"].astype(bool).all()
            and (group["state_amplification_violation"].astype(bool) == False).all()
            and int(group["limiter_clipped_rows"].astype(int).max()) == 0
        )
        rows.append({
            "jitter_radius_steps": int(radius),
            "radius_response_pass": radius_pass,
            "scenario_count": int(group["scenario"].nunique()),
            "offset_case_count": int(len(group)),
            "max_budget_fraction": float(group["max_budget_fraction"].astype(float).max()),
            "worst_scenario": str(worst["scenario"]),
            "worst_offset_steps": int(worst["offset_steps"]),
            "worst_source_row_index": int(worst["worst_source_row_index"]),
            "worst_assignment": str(worst["worst_assignment"]),
            "worst_stage": str(worst["worst_stage"]),
            "worst_region": str(worst["worst_region"]),
            "worst_s": _finite(worst["worst_s"], float("nan")),
            "worst_l": _finite(worst["worst_l"], float("nan")),
            "max_state_sum_to_source_sum": float(group["max_state_sum_to_source_sum"].astype(float).max()),
            "max_step_source_fraction": float(group["max_step_source_fraction"].astype(float).max()),
        })
    return pd.DataFrame(rows)


def _decision(radius_summary: pd.DataFrame, offset_summary: pd.DataFrame, domain_audit: pd.DataFrame) -> pd.DataFrame:
    live_pass = bool(domain_audit["live_support_exclusion_pass"].iloc[0])
    if not len(radius_summary):
        return pd.DataFrame([{
            "timing_jitter_status": "timing_jitter_fail_no_cases",
            "timing_jitter_pass": False,
            "live_support_exclusion_pass": live_pass,
            "tested_radius_count": 0,
            "largest_passing_jitter_radius_steps": -1,
            "max_budget_fraction": float("nan"),
            "worst_jitter_radius_steps": -1,
            "worst_offset_steps": 0,
            "worst_scenario": "",
            "worst_source_row_index": -1,
        }])
    passing = radius_summary.loc[radius_summary["radius_response_pass"].astype(bool)]
    all_radii_pass = bool(live_pass and len(passing) == len(radius_summary))
    any_radii_pass = bool(live_pass and len(passing) > 0)
    worst_idx = int(radius_summary["max_budget_fraction"].astype(float).idxmax())
    worst = radius_summary.loc[worst_idx]
    largest_pass = int(passing["jitter_radius_steps"].astype(int).max()) if len(passing) else -1
    state_clean = bool((offset_summary["state_amplification_violation"].astype(bool) == False).all()) if len(offset_summary) else False
    limiter_clean = bool(int(offset_summary["limiter_clipped_rows"].astype(int).max()) == 0) if len(offset_summary) else False
    status = (
        "timing_jitter_pass_all_tested_offsets"
        if all_radii_pass
        else "timing_jitter_pass_with_radius_limit"
        if any_radii_pass
        else "timing_jitter_fail_all_tested_offsets"
    )
    return pd.DataFrame([{
        "timing_jitter_status": status,
        "timing_jitter_pass": all_radii_pass,
        "live_support_exclusion_pass": live_pass,
        "state_amplification_clean": state_clean,
        "limiter_clean": limiter_clean,
        "tested_radius_count": int(len(radius_summary)),
        "largest_passing_jitter_radius_steps": largest_pass,
        "max_budget_fraction": float(radius_summary["max_budget_fraction"].astype(float).max()),
        "worst_jitter_radius_steps": int(worst["jitter_radius_steps"]),
        "worst_offset_steps": int(worst["worst_offset_steps"]),
        "worst_scenario": str(worst["worst_scenario"]),
        "worst_source_row_index": int(worst["worst_source_row_index"]),
    }])


def build_timing_jitter_certificate(
    closure_dir: Path,
    source_coupling_dir: Path,
    *,
    symbol_spec: PrincipalSymbolSpec | None = None,
    spec: TimingJitterSpec | None = None,
    scenarios: list[ActionPDEScenario] | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    symbol_spec = symbol_spec or PrincipalSymbolSpec()
    spec = spec or TimingJitterSpec()
    scenarios = scenarios or default_action_scenarios()
    point_closure, closure_manifest, point_path = _load_closure_dir(closure_dir)
    evolution_spec = _evolution_spec(spec)
    active, budget, provenance = _prepare_domain(closure_dir, source_coupling_dir, evolution_spec)
    radial_groups = _build_groups(active, ["assignment", "stage", "region", "slice_s_key"], "l")
    service_groups = _build_groups(active, ["assignment", "region", "l_key"], "s")
    source_profiles: dict[str, np.ndarray] = {}
    source_profile_frames: list[pd.DataFrame] = []
    for scenario in scenarios:
        profile, rows = _source_profile_for_scenario(active, budget, _full_scenario(scenario, spec), evolution_spec)
        source_profiles[scenario.label] = profile
        rows = rows.copy()
        rows["scenario"] = scenario.label
        source_profile_frames.append(rows)
    radii = tuple(sorted({max(0, int(radius)) for radius in spec.jitter_radii}))
    payloads = [
        (
            active,
            source_profiles[scenario.label],
            scenario,
            int(radius),
            radial_groups,
            service_groups,
            spec,
            symbol_spec,
        )
        for scenario in scenarios
        for radius in radii
    ]
    workers = min(_worker_count(spec.max_workers), max(1, len(payloads)))
    if workers <= 1 or len(payloads) <= 1:
        mapped = [_run_radius_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            mapped = list(pool.map(_run_radius_worker, payloads))
    offset_summary = pd.concat([frame for frame, _, _ in mapped], ignore_index=True) if mapped else pd.DataFrame()
    jitter_bin_summary = pd.concat([frame for _, frame, _ in mapped], ignore_index=True) if mapped else pd.DataFrame()
    sampled = pd.concat([frame for _, _, frame in mapped], ignore_index=True) if mapped else pd.DataFrame()
    if len(sampled):
        sampled = sampled.sort_values(["max_budget_fraction"], ascending=False).head(int(spec.top_row_count))
    domain_audit = _domain_audit(point_closure, active)
    radius = _radius_summary(offset_summary)
    decision = _decision(radius, offset_summary, domain_audit)
    source_profile_summary = (
        pd.concat(source_profile_frames, ignore_index=True) if source_profile_frames else pd.DataFrame()
    )
    outputs = {
        "domain_audit": domain_audit,
        "offset_summary": offset_summary,
        "radius_summary": radius,
        "jitter_bin_summary": jitter_bin_summary,
        "source_profile_summary": source_profile_summary,
        "sampled_worst_rows": sampled,
        "decision": decision,
    }
    metadata = {
        "source_name": "beta075_timing_jitter_certificate",
        "closure_dir": str(closure_dir),
        "source_coupling_dir": str(source_coupling_dir),
        "point_closure": str(point_path),
        "point_closure_sha256": sha256_file(point_path),
        "closure_source_name": closure_manifest.get("source_name", ""),
        "symbol_spec": symbol_spec.__dict__,
        "timing_jitter_spec": {
            **spec.__dict__,
            "jitter_radii": list(radii),
        },
        "scenarios": [scenario.__dict__ for scenario in scenarios],
        "radial_group_count": len(radial_groups),
        "service_group_count": len(service_groups),
        "radius_workers": workers,
        "provenance": provenance,
        "claim_boundary": (
            "Fixed-background action-level timing robustness certificate for the sealed beta075 package. "
            "The tested class is a common bounded service-timing offset around the service-aligned source "
            "envelope. It does not admit row-independent arbitrary impulse collapse and is not a coupled "
            "Einstein-matter evolution theorem."
        ),
    }
    return outputs, metadata


def write_timing_jitter_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "domain_audit": outdir / "beta075_timing_jitter_domain_audit.csv",
        "offset_summary": outdir / "beta075_timing_jitter_offset_summary.csv",
        "radius_summary": outdir / "beta075_timing_jitter_radius_summary.csv",
        "jitter_bin_summary": outdir / "beta075_timing_jitter_bin_summary.csv",
        "source_profile_summary": outdir / "beta075_timing_jitter_source_profile_summary.csv",
        "sampled_worst_rows": outdir / "beta075_timing_jitter_sampled_worst_rows.csv",
        "decision": outdir / "beta075_timing_jitter_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    manifest_path = outdir / "beta075_timing_jitter_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
