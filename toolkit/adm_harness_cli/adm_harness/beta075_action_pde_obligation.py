from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .beta075_full_system_evolution import (
    FullSystemEvolutionScenario,
    FullSystemEvolutionSpec,
    _advect_groups,
    _build_groups,
    _domain_audit,
    _prepare_domain,
    _run_domain_scenario,
    _sample_symbol_margins,
    _source_profile_for_scenario,
)
from .endpoint_support_principal_symbol import PrincipalSymbolSpec, _finite
from .endpoint_support_source_coupling_package import _safe_budget_fraction
from .endpoint_support_source_dynamics import _load_closure_dir
from .source_ledger import sha256_file, write_manifest


@dataclass(frozen=True)
class ActionPDEObligationSpec:
    observed_heat_ratio_delta: float = 1.0e-4
    steps: int = 48
    radial_cfl: float = 0.40
    service_cfl: float = 0.20
    source_column: str = "candidate_support_abs_PF_density"
    source_smoothing_passes: int = 0
    source_profile_budget_cap_scope: str = "support_edge_entry_catch"
    source_profile_budget_cap_fraction: float = 0.95
    source_profile_budget_cap_reference_delta: float | None = None
    temporal_profile: str = "raised_cosine"
    s_round_decimals: int = 12
    l_round_decimals: int = 12
    top_row_count: int = 120


@dataclass(frozen=True)
class ActionPDEScenario:
    label: str
    radial_direction: str
    service_direction: str


def default_action_scenarios() -> list[ActionPDEScenario]:
    return [
        ActionPDEScenario("observed_action_outward_forward", "outward", "forward"),
        ActionPDEScenario("observed_action_inward_forward", "inward", "forward"),
        ActionPDEScenario("observed_action_outward_backward", "outward", "backward"),
    ]


def _evolution_spec(spec: ActionPDEObligationSpec) -> FullSystemEvolutionSpec:
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
        temporal_profile=str(spec.temporal_profile),
        s_round_decimals=int(spec.s_round_decimals),
        l_round_decimals=int(spec.l_round_decimals),
        top_row_count=int(spec.top_row_count),
        max_workers=1,
    )


def _full_scenario(scenario: ActionPDEScenario, spec: ActionPDEObligationSpec) -> FullSystemEvolutionScenario:
    return FullSystemEvolutionScenario(
        label=scenario.label,
        heat_ratio_delta=float(spec.observed_heat_ratio_delta),
        radial_direction=str(scenario.radial_direction),
        service_direction=str(scenario.service_direction),
        budget_limiter=False,
    )


def _max_fraction_position(fraction: np.ndarray) -> int:
    if not len(fraction):
        return 0
    finite = np.where(np.isfinite(fraction), fraction, -np.inf)
    return int(np.nanargmax(finite))


def _impulse_certificate(
    active: pd.DataFrame,
    budget: pd.DataFrame,
    scenario: ActionPDEScenario,
    *,
    radial_groups: list[np.ndarray],
    service_groups: list[np.ndarray],
    spec: ActionPDEObligationSpec,
    symbol_spec: PrincipalSymbolSpec,
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    evolution_spec = _evolution_spec(spec)
    full_scenario = _full_scenario(scenario, spec)
    source_profile, profile_rows = _source_profile_for_scenario(active, budget, full_scenario, evolution_spec)
    budgets = active["max_admissible_delta_psi"].astype(float).to_numpy()
    state = source_profile.copy()
    state_max = state.copy()
    fraction_max = _safe_budget_fraction(state, budgets)
    initial_fraction = fraction_max.copy()
    source_sum = float(np.sum(source_profile))
    max_state_sum_to_source = float(np.sum(state) / source_sum) if source_sum > 0.0 else 0.0
    for _ in range(int(spec.steps)):
        state = _advect_groups(state, radial_groups, cfl=float(spec.radial_cfl), direction=scenario.radial_direction)
        state = _advect_groups(state, service_groups, cfl=float(spec.service_cfl), direction=scenario.service_direction)
        state_max = np.maximum(state_max, state)
        fraction_max = np.maximum(fraction_max, _safe_budget_fraction(state, budgets))
        if source_sum > 0.0:
            max_state_sum_to_source = max(max_state_sum_to_source, float(np.sum(state) / source_sum))
    min_margin, min_margin_row, sampled = _sample_symbol_margins(
        active,
        state_max,
        fraction_max,
        symbol_spec,
        int(spec.top_row_count),
    )
    worst_pos = _max_fraction_position(fraction_max)
    initial_worst_pos = _max_fraction_position(initial_fraction)
    summary = {
        "scenario": scenario.label,
        "radial_direction": scenario.radial_direction,
        "service_direction": scenario.service_direction,
        "heat_ratio_delta": float(spec.observed_heat_ratio_delta),
        "steps": int(spec.steps),
        "max_impulse_budget_fraction": float(fraction_max[worst_pos]) if len(fraction_max) else float("nan"),
        "max_initial_source_budget_fraction": (
            float(initial_fraction[initial_worst_pos]) if len(initial_fraction) else float("nan")
        ),
        "impulse_bound_pass": bool(len(fraction_max) and float(fraction_max[worst_pos]) <= 1.0),
        "worst_source_row_index": int(active.iloc[worst_pos]["source_row_index"]) if len(active) else -1,
        "worst_assignment": str(active.iloc[worst_pos]["assignment"]) if len(active) else "",
        "worst_stage": str(active.iloc[worst_pos]["stage"]) if len(active) else "",
        "worst_region": str(active.iloc[worst_pos]["region"]) if len(active) else "",
        "worst_s": _finite(active.iloc[worst_pos]["s"], float("nan")) if len(active) else float("nan"),
        "worst_l": _finite(active.iloc[worst_pos]["l"], float("nan")) if len(active) else float("nan"),
        "min_relative_cone_margin_sample": min_margin,
        "min_relative_cone_margin_sample_row": min_margin_row,
        "source_delta_psi_sum": source_sum,
        "max_state_sum_to_source_sum": max_state_sum_to_source,
        "state_amplification_violation": bool(max_state_sum_to_source > 1.0 + 1.0e-9),
    }
    sampled["scenario"] = scenario.label
    sampled["certificate"] = "impulse_response_upper_bound"
    profile_rows["scenario"] = scenario.label
    return summary, profile_rows, sampled


def _group_edge_rows(
    active: pd.DataFrame,
    groups: list[np.ndarray],
    *,
    cfl: float,
    direction: str,
    axis: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    budgets = active["max_admissible_delta_psi"].astype(float).to_numpy()
    mapped = "outward" if direction == "forward" else "inward" if direction == "backward" else direction
    for idx in groups:
        if len(idx) <= 1:
            continue
        receivers = idx[1:] if mapped == "outward" else idx[:-1]
        donors = idx[:-1] if mapped == "outward" else idx[1:]
        for receiver, donor in zip(receivers, donors, strict=True):
            receiver_budget = float(budgets[int(receiver)])
            donor_budget = float(budgets[int(donor)])
            if receiver_budget <= 0.0 or not np.isfinite(receiver_budget):
                ratio = float("inf")
                row_sum = float("inf")
            else:
                ratio = donor_budget / receiver_budget
                row_sum = (1.0 - float(cfl)) + float(cfl) * ratio
            receiver_row = active.iloc[int(receiver)]
            donor_row = active.iloc[int(donor)]
            rows.append({
                "axis": axis,
                "direction": direction,
                "receiver_source_row_index": int(receiver_row["source_row_index"]),
                "donor_source_row_index": int(donor_row["source_row_index"]),
                "receiver_assignment": str(receiver_row["assignment"]),
                "receiver_stage": str(receiver_row["stage"]),
                "receiver_region": str(receiver_row["region"]),
                "receiver_s": _finite(receiver_row["s"], float("nan")),
                "receiver_l": _finite(receiver_row["l"], float("nan")),
                "donor_budget_delta_psi": donor_budget,
                "receiver_budget_delta_psi": receiver_budget,
                "inflow_budget_ratio": ratio,
                "normalized_row_sum_bound": row_sum,
                "normalized_row_sum_expansive": bool(row_sum > 1.0 + 1.0e-12),
            })
    return rows


def _transport_edge_certificate(
    active: pd.DataFrame,
    radial_groups: list[np.ndarray],
    service_groups: list[np.ndarray],
    scenarios: list[ActionPDEScenario],
    spec: ActionPDEObligationSpec,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        rows.extend(
            _group_edge_rows(
                active,
                radial_groups,
                cfl=float(spec.radial_cfl),
                direction=scenario.radial_direction,
                axis=f"{scenario.label}:radial",
            )
        )
        rows.extend(
            _group_edge_rows(
                active,
                service_groups,
                cfl=float(spec.service_cfl),
                direction=scenario.service_direction,
                axis=f"{scenario.label}:service_time",
            )
        )
    return pd.DataFrame(rows)


def _edge_summary(edge_rows: pd.DataFrame) -> pd.DataFrame:
    if not len(edge_rows):
        return pd.DataFrame([{
            "edge_rows": 0,
            "expansive_edge_rows": 0,
            "max_inflow_budget_ratio": float("nan"),
            "max_normalized_row_sum_bound": float("nan"),
            "worst_receiver_source_row_index": -1,
        }])
    finite = edge_rows["normalized_row_sum_bound"].astype(float).replace([np.inf], np.nan)
    worst_idx = int(finite.idxmax()) if finite.notna().any() else int(edge_rows.index[0])
    return pd.DataFrame([{
        "edge_rows": int(len(edge_rows)),
        "expansive_edge_rows": int(edge_rows["normalized_row_sum_expansive"].astype(bool).sum()),
        "max_inflow_budget_ratio": float(
            edge_rows["inflow_budget_ratio"].astype(float).replace([np.inf], np.nan).max()
        ),
        "max_normalized_row_sum_bound": float(finite.max()),
        "worst_receiver_source_row_index": int(edge_rows.loc[worst_idx, "receiver_source_row_index"]),
        "worst_axis": str(edge_rows.loc[worst_idx, "axis"]),
        "worst_direction": str(edge_rows.loc[worst_idx, "direction"]),
    }])


def _decision(
    domain_audit: pd.DataFrame,
    scheduled_summary: pd.DataFrame,
    impulse_summary: pd.DataFrame,
    edge_summary: pd.DataFrame,
) -> pd.DataFrame:
    schedule_pass = bool(len(scheduled_summary) and scheduled_summary["hard_pass"].astype(bool).all())
    state_nonamp = bool(
        len(impulse_summary)
        and (impulse_summary["state_amplification_violation"].astype(bool) == False).all()
        and (scheduled_summary["state_amplification_violation"].astype(bool) == False).all()
    )
    live_pass = bool(domain_audit["live_support_exclusion_pass"].iloc[0])
    impulse_pass = bool(len(impulse_summary) and impulse_summary["impulse_bound_pass"].astype(bool).all())
    transport_row_sum_contract = bool(
        len(edge_summary)
        and int(edge_summary["expansive_edge_rows"].iloc[0]) == 0
    )
    if live_pass and schedule_pass and state_nonamp and impulse_pass:
        status = "action_pde_obligation_pass_temporal_profile_independent"
    elif live_pass and schedule_pass and state_nonamp:
        status = "action_pde_obligation_gap_temporal_regularization_required"
    else:
        status = "action_pde_obligation_fail_observed_schedule"
    return pd.DataFrame([{
        "action_pde_obligation_status": status,
        "observed_schedule_pass": schedule_pass,
        "impulse_bound_pass": impulse_pass,
        "transport_row_sum_contract": transport_row_sum_contract,
        "state_nonamplification_pass": state_nonamp,
        "live_support_exclusion_pass": live_pass,
        "max_observed_scheduled_budget_fraction": (
            float(scheduled_summary["max_budget_fraction"].astype(float).max()) if len(scheduled_summary) else float("nan")
        ),
        "max_impulse_budget_fraction": (
            float(impulse_summary["max_impulse_budget_fraction"].astype(float).max()) if len(impulse_summary) else float("nan")
        ),
        "max_initial_source_budget_fraction": (
            float(impulse_summary["max_initial_source_budget_fraction"].astype(float).max()) if len(impulse_summary) else float("nan")
        ),
        "max_normalized_row_sum_bound": (
            float(edge_summary["max_normalized_row_sum_bound"].astype(float).max()) if len(edge_summary) else float("nan")
        ),
        "expansive_edge_rows": int(edge_summary["expansive_edge_rows"].iloc[0]) if len(edge_summary) else 0,
    }])


def build_action_pde_obligation(
    closure_dir: Path,
    source_coupling_dir: Path,
    *,
    symbol_spec: PrincipalSymbolSpec | None = None,
    spec: ActionPDEObligationSpec | None = None,
    scenarios: list[ActionPDEScenario] | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    symbol_spec = symbol_spec or PrincipalSymbolSpec()
    spec = spec or ActionPDEObligationSpec()
    scenarios = scenarios or default_action_scenarios()
    point_closure, closure_manifest, point_path = _load_closure_dir(closure_dir)
    evolution_spec = _evolution_spec(spec)
    active, budget, provenance = _prepare_domain(closure_dir, source_coupling_dir, evolution_spec)
    radial_groups = _build_groups(active, ["assignment", "stage", "region", "slice_s_key"], "l")
    service_groups = _build_groups(active, ["assignment", "region", "l_key"], "s")
    scheduled_rows: list[dict[str, Any]] = []
    impulse_rows: list[dict[str, Any]] = []
    profile_frames: list[pd.DataFrame] = []
    sampled_frames: list[pd.DataFrame] = []
    for scenario in scenarios:
        full_scenario = _full_scenario(scenario, spec)
        scheduled_summary, _, scheduled_sampled = _run_domain_scenario(
            active,
            budget,
            full_scenario,
            radial_groups=radial_groups,
            service_groups=service_groups,
            spec=evolution_spec,
            symbol_spec=symbol_spec,
        )
        impulse_summary, profile_rows, impulse_sampled = _impulse_certificate(
            active,
            budget,
            scenario,
            radial_groups=radial_groups,
            service_groups=service_groups,
            spec=spec,
            symbol_spec=symbol_spec,
        )
        scheduled_summary["certificate"] = "observed_temporal_profile"
        impulse_summary["certificate"] = "temporal_profile_independent_impulse_upper_bound"
        scheduled_rows.append(scheduled_summary)
        impulse_rows.append(impulse_summary)
        profile_frames.append(profile_rows)
        sampled_frames.extend([scheduled_sampled, impulse_sampled])
    scheduled_summary = pd.DataFrame(scheduled_rows)
    impulse_summary = pd.DataFrame(impulse_rows)
    source_profile_summary = pd.concat(profile_frames, ignore_index=True) if profile_frames else pd.DataFrame()
    sampled_worst = pd.concat(sampled_frames, ignore_index=True) if sampled_frames else pd.DataFrame()
    if len(sampled_worst):
        sampled_worst = sampled_worst.sort_values(["max_budget_fraction"], ascending=False).head(int(spec.top_row_count))
    domain_audit = _domain_audit(point_closure, active)
    edge_rows = _transport_edge_certificate(active, radial_groups, service_groups, scenarios, spec)
    edge_summary = _edge_summary(edge_rows)
    decision = _decision(domain_audit, scheduled_summary, impulse_summary, edge_summary)
    outputs = {
        "domain_audit": domain_audit,
        "scheduled_summary": scheduled_summary,
        "impulse_summary": impulse_summary,
        "transport_edge_summary": edge_summary,
        "transport_edge_rows": edge_rows,
        "source_profile_summary": source_profile_summary,
        "sampled_worst_rows": sampled_worst,
        "decision": decision,
    }
    metadata = {
        "source_name": "beta075_action_pde_obligation",
        "closure_dir": str(closure_dir),
        "source_coupling_dir": str(source_coupling_dir),
        "point_closure": str(point_path),
        "point_closure_sha256": sha256_file(point_path),
        "closure_source_name": closure_manifest.get("source_name", ""),
        "symbol_spec": symbol_spec.__dict__,
        "action_pde_obligation_spec": spec.__dict__,
        "scenarios": [scenario.__dict__ for scenario in scenarios],
        "radial_group_count": len(radial_groups),
        "service_group_count": len(service_groups),
        "provenance": provenance,
        "claim_boundary": (
            "Finite-horizon fixed-background proof-obligation certificate for the observed-amplitude "
            "bounded-rapidity system on the sealed beta075 package. It compares the observed temporal "
            "profile with a temporal-profile-independent nonnegative impulse upper bound. It is not a "
            "coupled Einstein-matter evolution or final PDE theorem."
        ),
    }
    return outputs, metadata


def write_action_pde_obligation_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "domain_audit": outdir / "beta075_action_pde_domain_audit.csv",
        "scheduled_summary": outdir / "beta075_action_pde_scheduled_summary.csv",
        "impulse_summary": outdir / "beta075_action_pde_impulse_summary.csv",
        "transport_edge_summary": outdir / "beta075_action_pde_transport_edge_summary.csv",
        "transport_edge_rows": outdir / "beta075_action_pde_transport_edge_rows.csv",
        "source_profile_summary": outdir / "beta075_action_pde_source_profile_summary.csv",
        "sampled_worst_rows": outdir / "beta075_action_pde_sampled_worst_rows.csv",
        "decision": outdir / "beta075_action_pde_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    manifest_path = outdir / "beta075_action_pde_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
