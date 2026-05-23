from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .beta075_action_pde_obligation import ActionPDEScenario, default_action_scenarios
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
from .beta075_service_aligned_schedule import _aligned_temporal_weights
from .endpoint_support_principal_symbol import PrincipalSymbolSpec, _finite
from .endpoint_support_source_coupling_package import _safe_budget_fraction
from .endpoint_support_source_dynamics import _load_closure_dir
from .source_ledger import sha256_file, write_manifest


@dataclass(frozen=True)
class AlignedEnvelopeSpec:
    observed_heat_ratio_delta: float = 1.0e-4
    steps: int = 48
    tail_steps: int = 48
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


def _evolution_spec(spec: AlignedEnvelopeSpec) -> FullSystemEvolutionSpec:
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


def _full_scenario(scenario: ActionPDEScenario, spec: AlignedEnvelopeSpec) -> FullSystemEvolutionScenario:
    return FullSystemEvolutionScenario(
        label=scenario.label,
        heat_ratio_delta=float(spec.observed_heat_ratio_delta),
        radial_direction=str(scenario.radial_direction),
        service_direction=str(scenario.service_direction),
        budget_limiter=False,
    )


def _basis_source_bins(active: pd.DataFrame, *, steps: int, service_direction: str) -> np.ndarray:
    weights = _aligned_temporal_weights(
        active["s"].astype(float).to_numpy(),
        steps=int(steps),
        width_steps=1,
        service_direction=service_direction,
    )
    return np.argmax(weights, axis=0).astype(int)


def _max_fraction_position(fraction: np.ndarray) -> int:
    if not len(fraction):
        return 0
    return int(np.nanargmax(np.where(np.isfinite(fraction), fraction, -np.inf)))


def _service_bin_summary(
    active: pd.DataFrame,
    source_profile: np.ndarray,
    bins: np.ndarray,
    scenario: ActionPDEScenario,
    spec: AlignedEnvelopeSpec,
) -> pd.DataFrame:
    total = float(np.sum(source_profile))
    rows: list[dict[str, Any]] = []
    for step in range(int(spec.steps)):
        mask = bins == step
        source_sum = float(np.sum(source_profile[mask]))
        rows.append({
            "scenario": scenario.label,
            "service_direction": scenario.service_direction,
            "step": int(step),
            "rows": int(np.sum(mask)),
            "source_delta_psi_sum": source_sum,
            "source_fraction": source_sum / total if total > 0.0 else 0.0,
        })
    return pd.DataFrame(rows)


def _run_basis_response(
    active: pd.DataFrame,
    budget: pd.DataFrame,
    scenario: ActionPDEScenario,
    *,
    radial_groups: list[np.ndarray],
    service_groups: list[np.ndarray],
    spec: AlignedEnvelopeSpec,
    symbol_spec: PrincipalSymbolSpec,
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    evolution_spec = _evolution_spec(spec)
    source_profile, _ = _source_profile_for_scenario(active, budget, _full_scenario(scenario, spec), evolution_spec)
    bins = _basis_source_bins(active, steps=int(spec.steps), service_direction=scenario.service_direction)
    bin_summary = _service_bin_summary(active, source_profile, bins, scenario, spec)
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
        "basis_response_pass": bool(max_fraction <= 1.0 and max_state_sum_to_source <= 1.0 + 1.0e-9),
        "convex_kernel_bound_pass": bool(max_fraction <= 1.0),
        "convex_kernel_bound_budget_fraction": max_fraction,
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
    }
    sampled["scenario"] = scenario.label
    sampled["certificate"] = "service_aligned_convex_kernel_envelope"
    return summary, bin_summary, sampled


def _run_basis_response_worker(
    payload: tuple[
        pd.DataFrame,
        pd.DataFrame,
        ActionPDEScenario,
        list[np.ndarray],
        list[np.ndarray],
        AlignedEnvelopeSpec,
        PrincipalSymbolSpec,
    ]
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    active, budget, scenario, radial_groups, service_groups, spec, symbol_spec = payload
    return _run_basis_response(
        active,
        budget,
        scenario,
        radial_groups=radial_groups,
        service_groups=service_groups,
        spec=spec,
        symbol_spec=symbol_spec,
    )


def _decision(basis_summary: pd.DataFrame, domain_audit: pd.DataFrame) -> pd.DataFrame:
    live_pass = bool(domain_audit["live_support_exclusion_pass"].iloc[0])
    envelope_pass = bool(
        len(basis_summary)
        and live_pass
        and basis_summary["convex_kernel_bound_pass"].astype(bool).all()
        and (basis_summary["state_amplification_violation"].astype(bool) == False).all()
    )
    worst_idx = int(basis_summary["convex_kernel_bound_budget_fraction"].astype(float).idxmax()) if len(basis_summary) else -1
    status = (
        "aligned_envelope_pass_convex_kernel_bound"
        if envelope_pass
        else "aligned_envelope_fail_convex_kernel_bound"
    )
    return pd.DataFrame([{
        "aligned_envelope_status": status,
        "convex_kernel_bound_pass": envelope_pass,
        "live_support_exclusion_pass": live_pass,
        "scenario_count": int(len(basis_summary)),
        "max_convex_kernel_bound_budget_fraction": (
            float(basis_summary["convex_kernel_bound_budget_fraction"].astype(float).max())
            if len(basis_summary)
            else float("nan")
        ),
        "worst_scenario": str(basis_summary.loc[worst_idx, "scenario"]) if len(basis_summary) else "",
        "worst_source_row_index": int(basis_summary.loc[worst_idx, "worst_source_row_index"]) if len(basis_summary) else -1,
        "max_state_sum_to_source_sum": (
            float(basis_summary["max_state_sum_to_source_sum"].astype(float).max())
            if len(basis_summary)
            else float("nan")
        ),
    }])


def build_aligned_envelope_certificate(
    closure_dir: Path,
    source_coupling_dir: Path,
    *,
    symbol_spec: PrincipalSymbolSpec | None = None,
    spec: AlignedEnvelopeSpec | None = None,
    scenarios: list[ActionPDEScenario] | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    symbol_spec = symbol_spec or PrincipalSymbolSpec()
    spec = spec or AlignedEnvelopeSpec()
    scenarios = scenarios or default_action_scenarios()
    point_closure, closure_manifest, point_path = _load_closure_dir(closure_dir)
    evolution_spec = _evolution_spec(spec)
    active, budget, provenance = _prepare_domain(closure_dir, source_coupling_dir, evolution_spec)
    radial_groups = _build_groups(active, ["assignment", "stage", "region", "slice_s_key"], "l")
    service_groups = _build_groups(active, ["assignment", "region", "l_key"], "s")
    payloads = [
        (active, budget, scenario, radial_groups, service_groups, spec, symbol_spec)
        for scenario in scenarios
    ]
    workers = min(_worker_count(spec.max_workers), max(1, len(payloads)))
    if workers <= 1 or len(payloads) <= 1:
        mapped = [_run_basis_response_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            mapped = list(pool.map(_run_basis_response_worker, payloads))
    basis_summary = pd.DataFrame([summary for summary, _, _ in mapped])
    bin_summary = pd.concat([frame for _, frame, _ in mapped], ignore_index=True) if mapped else pd.DataFrame()
    sampled = pd.concat([frame for _, _, frame in mapped], ignore_index=True) if mapped else pd.DataFrame()
    if len(sampled):
        sampled = sampled.sort_values(["max_budget_fraction"], ascending=False).head(int(spec.top_row_count))
    domain_audit = _domain_audit(point_closure, active)
    decision = _decision(basis_summary, domain_audit)
    outputs = {
        "domain_audit": domain_audit,
        "basis_summary": basis_summary,
        "service_bin_summary": bin_summary,
        "sampled_worst_rows": sampled,
        "decision": decision,
    }
    metadata = {
        "source_name": "beta075_aligned_envelope_certificate",
        "closure_dir": str(closure_dir),
        "source_coupling_dir": str(source_coupling_dir),
        "point_closure": str(point_path),
        "point_closure_sha256": sha256_file(point_path),
        "closure_source_name": closure_manifest.get("source_name", ""),
        "symbol_spec": symbol_spec.__dict__,
        "aligned_envelope_spec": spec.__dict__,
        "scenarios": [scenario.__dict__ for scenario in scenarios],
        "radial_group_count": len(radial_groups),
        "service_group_count": len(service_groups),
        "scenario_workers": workers,
        "provenance": provenance,
        "claim_boundary": (
            "Fixed-background aligned-envelope certificate for the sealed beta075 package. "
            "A common nonnegative temporal kernel over the one-step service-coordinate source bins "
            "is bounded by the basis response by linearity and positivity of the split-step transport operator. "
            "This is not a coupled Einstein-matter evolution or final PDE theorem."
        ),
    }
    return outputs, metadata


def write_aligned_envelope_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "domain_audit": outdir / "beta075_aligned_envelope_domain_audit.csv",
        "basis_summary": outdir / "beta075_aligned_envelope_basis_summary.csv",
        "service_bin_summary": outdir / "beta075_aligned_envelope_service_bin_summary.csv",
        "sampled_worst_rows": outdir / "beta075_aligned_envelope_sampled_worst_rows.csv",
        "decision": outdir / "beta075_aligned_envelope_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    manifest_path = outdir / "beta075_aligned_envelope_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
