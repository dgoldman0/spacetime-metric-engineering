from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .beta075_constitutive_1p1_source_coupled import (
    Constitutive1p1Scenario,
    Constitutive1p1Spec,
    _evolution_spec,
    _run_scenario_worker,
    _source_law_gate,
    _source_law_summary,
)
from .beta075_full_system_evolution import (
    _build_groups,
    _domain_audit,
    _prepare_domain,
    _worker_count,
)
from .endpoint_support_principal_symbol import PrincipalSymbolSpec
from .endpoint_support_source_dynamics import _load_closure_dir
from .source_ledger import sha256_file, write_manifest


@dataclass(frozen=True)
class Constitutive1p1ProofSpec(Constitutive1p1Spec):
    jitter_radius_steps: int = 8
    top_row_count: int = 160


def default_proof_scenarios(spec: Constitutive1p1ProofSpec | None = None) -> list[Constitutive1p1Scenario]:
    spec = spec or Constitutive1p1ProofSpec()
    observed = float(spec.observed_heat_ratio_delta)
    bases = [
        ("outward_forward", "outward", "forward"),
        ("inward_forward", "inward", "forward"),
        ("outward_backward", "outward", "backward"),
    ]
    scenarios: list[Constitutive1p1Scenario] = []
    for base, radial_direction, service_direction in bases:
        for offset in range(-int(spec.jitter_radius_steps), int(spec.jitter_radius_steps) + 1):
            label = f"proof_observed_{base}_offset_{offset:+d}".replace("+", "p").replace("-", "m")
            scenarios.append(
                Constitutive1p1Scenario(
                    label,
                    observed,
                    radial_direction,
                    service_direction,
                    False,
                    timing_offset_steps=int(offset),
                    gate_role="observed_driver",
                )
            )
    return scenarios


def _transport_semigroup_certificate(
    *,
    radial_group_count: int,
    service_group_count: int,
    spec: Constitutive1p1ProofSpec,
    scenarios: list[Constitutive1p1Scenario],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for scenario in scenarios:
        for axis, direction, cfl, group_count in [
            ("radial", scenario.radial_direction, float(spec.radial_cfl), int(radial_group_count)),
            ("service", scenario.service_direction, float(spec.service_cfl), int(service_group_count)),
        ]:
            key = (axis, str(direction))
            if key in seen:
                continue
            seen.add(key)
            rows.append({
                "axis": axis,
                "direction": str(direction),
                "group_count": group_count,
                "cfl": cfl,
                "self_coefficient": 1.0 - cfl,
                "inflow_coefficient": cfl,
                "boundary_outflow_coefficient": 1.0 - cfl,
                "positive_coefficients_pass": bool(0.0 <= cfl <= 1.0),
                "l1_nonincrease_for_nonnegative_state": bool(0.0 <= cfl <= 1.0),
                "maps_nonnegative_state_to_nonnegative_state": bool(0.0 <= cfl <= 1.0),
            })
    return pd.DataFrame(rows)


def _offset_radius_summary(scenario_summary: pd.DataFrame) -> pd.DataFrame:
    if not len(scenario_summary):
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for radius, group in scenario_summary.assign(
        timing_radius_steps=scenario_summary["timing_offset_steps"].astype(int).abs()
    ).groupby("timing_radius_steps", sort=True):
        worst_idx = int(group["max_budget_fraction"].astype(float).idxmax())
        worst = scenario_summary.loc[worst_idx]
        rows.append({
            "timing_radius_steps": int(radius),
            "case_count": int(len(group)),
            "radius_pass": bool(
                group["hard_pass"].astype(bool).all()
                and (group["state_amplification_violation"].astype(bool) == False).all()
                and int(group["negative_source_rows"].astype(int).max()) == 0
            ),
            "max_budget_fraction": float(group["max_budget_fraction"].astype(float).max()),
            "worst_scenario": str(worst["scenario"]),
            "worst_offset_steps": int(worst["timing_offset_steps"]),
            "worst_source_row_index": int(worst["worst_source_row_index"]),
            "worst_stage": str(worst["worst_stage"]),
            "worst_region": str(worst["worst_region"]),
            "max_state_sum_to_source_sum": float(group["max_state_sum_to_source_sum"].astype(float).max()),
            "max_step_source_fraction": float(group["max_step_source_fraction"].astype(float).max()),
        })
    return pd.DataFrame(rows)


def _obligation_rows(
    scenario_summary: pd.DataFrame,
    radius_summary: pd.DataFrame,
    transport_semigroup: pd.DataFrame,
    domain_audit: pd.DataFrame,
    source_law_summary: pd.DataFrame,
    spec: Constitutive1p1ProofSpec,
) -> pd.DataFrame:
    source_gate = _source_law_gate(source_law_summary)
    max_budget = (
        float(scenario_summary["max_budget_fraction"].astype(float).max())
        if len(scenario_summary)
        else float("nan")
    )
    rows = [
        {
            "obligation": "live_and_packet_live_exclusion",
            "pass": bool(domain_audit["live_support_exclusion_pass"].iloc[0]),
            "measured_value": int(domain_audit["active_live_rows"].iloc[0]) + int(domain_audit["active_packet_live_rows"].iloc[0]),
            "bound": 0,
            "interpretation": "active support-source domain contains no live or packet-live rows",
        },
        {
            "obligation": "phase_local_bounded_source_law",
            "pass": bool(source_gate["source_law_bounded"] and source_gate["source_law_phase_local"]),
            "measured_value": float(source_gate["min_source_profile_scale"]),
            "bound": "0 <= scale <= 1, scaled slices only in entry/catch support-edge scope",
            "interpretation": "constitutive source scaling is bounded and localized to intended support-edge phases",
        },
        {
            "obligation": "source_nonnegativity",
            "pass": bool(len(scenario_summary) and int(scenario_summary["negative_source_rows"].astype(int).max()) == 0),
            "measured_value": int(scenario_summary["negative_source_rows"].astype(int).max()) if len(scenario_summary) else -1,
            "bound": 0,
            "interpretation": "observed source profiles are nonnegative, so positivity arguments apply",
        },
        {
            "obligation": "service_schedule_with_bounded_common_jitter",
            "pass": bool(len(radius_summary) and radius_summary["radius_pass"].astype(bool).all()),
            "measured_value": int(radius_summary["timing_radius_steps"].astype(int).max()) if len(radius_summary) else -1,
            "bound": int(spec.jitter_radius_steps),
            "interpretation": "all common offsets in the certified jitter class pass the observed budget gate",
        },
        {
            "obligation": "positive_transport_semigroup",
            "pass": bool(
                len(transport_semigroup)
                and transport_semigroup["positive_coefficients_pass"].astype(bool).all()
                and transport_semigroup["maps_nonnegative_state_to_nonnegative_state"].astype(bool).all()
            ),
            "measured_value": float(transport_semigroup["cfl"].astype(float).max()) if len(transport_semigroup) else float("nan"),
            "bound": "CFL in [0, 1]",
            "interpretation": "radial and service upwind steps have nonnegative convex coefficients",
        },
        {
            "obligation": "transport_l1_nonamplification",
            "pass": bool(
                len(transport_semigroup)
                and transport_semigroup["l1_nonincrease_for_nonnegative_state"].astype(bool).all()
            ),
            "measured_value": float(scenario_summary["max_state_sum_to_source_sum"].astype(float).max()) if len(scenario_summary) else float("nan"),
            "bound": "<= 1",
            "interpretation": "transport plus scheduled nonnegative source does not amplify total state beyond injected source",
        },
        {
            "obligation": "observed_budget_invariance",
            "pass": bool(len(scenario_summary) and scenario_summary["hard_pass"].astype(bool).all() and max_budget <= 1.0),
            "measured_value": max_budget,
            "bound": 1.0,
            "interpretation": "every observed-amplitude scenario and common jitter offset stays inside local rapidity budget",
        },
        {
            "obligation": "limiter_inactivity_implied",
            "pass": bool(max_budget < float(spec.limiter_safety_fraction)),
            "measured_value": max_budget,
            "bound": float(spec.limiter_safety_fraction),
            "interpretation": "budget fraction remains below the configured limiter cap, so the limiter is not needed for the observed proof class",
        },
    ]
    return pd.DataFrame(rows)


def _decision(obligation_summary: pd.DataFrame, scenario_summary: pd.DataFrame, radius_summary: pd.DataFrame) -> pd.DataFrame:
    proof_pass = bool(len(obligation_summary) and obligation_summary["pass"].astype(bool).all())
    worst_idx = (
        int(scenario_summary["max_budget_fraction"].astype(float).idxmax())
        if len(scenario_summary)
        else -1
    )
    worst = scenario_summary.loc[worst_idx] if len(scenario_summary) else pd.Series(dtype=object)
    return pd.DataFrame([{
        "constitutive_1p1_proof_status": (
            "constitutive_1p1_observed_class_proof_obligation_pass"
            if proof_pass
            else "constitutive_1p1_observed_class_proof_obligation_fail"
        ),
        "proof_obligations_pass": proof_pass,
        "obligation_count": int(len(obligation_summary)),
        "failed_obligation_count": int((~obligation_summary["pass"].astype(bool)).sum()) if len(obligation_summary) else 0,
        "scenario_count": int(len(scenario_summary)),
        "tested_jitter_radius_steps": int(radius_summary["timing_radius_steps"].astype(int).max()) if len(radius_summary) else -1,
        "max_observed_budget_fraction": (
            float(scenario_summary["max_budget_fraction"].astype(float).max())
            if len(scenario_summary)
            else float("nan")
        ),
        "worst_scenario": str(worst.get("scenario", "")) if len(scenario_summary) else "",
        "worst_offset_steps": int(worst.get("timing_offset_steps", 0)) if len(scenario_summary) else 0,
        "worst_source_row_index": int(worst.get("worst_source_row_index", -1)) if len(scenario_summary) else -1,
        "max_state_sum_to_source_sum": (
            float(scenario_summary["max_state_sum_to_source_sum"].astype(float).max())
            if len(scenario_summary)
            else float("nan")
        ),
    }])


def build_constitutive_1p1_proof_obligation(
    closure_dir: Path,
    source_coupling_dir: Path,
    *,
    symbol_spec: PrincipalSymbolSpec | None = None,
    spec: Constitutive1p1ProofSpec | None = None,
    scenarios: list[Constitutive1p1Scenario] | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    symbol_spec = symbol_spec or PrincipalSymbolSpec()
    spec = spec or Constitutive1p1ProofSpec()
    scenarios = scenarios or default_proof_scenarios(spec)
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
        sampled = (
            ordered.groupby("scenario", sort=False, group_keys=False)
            .head(max(1, min(12, int(spec.top_row_count))))
            .sort_values(["max_budget_fraction"], ascending=False)
            .head(int(spec.top_row_count))
            .reset_index(drop=True)
        )
    domain_audit = _domain_audit(point_closure, active)
    source_law_summary = _source_law_summary(source_profile_summary, spec.observed_heat_ratio_delta)
    radius_summary = _offset_radius_summary(scenario_summary)
    transport_semigroup = _transport_semigroup_certificate(
        radial_group_count=len(radial_groups),
        service_group_count=len(service_groups),
        spec=spec,
        scenarios=scenarios,
    )
    obligation_summary = _obligation_rows(
        scenario_summary,
        radius_summary,
        transport_semigroup,
        domain_audit,
        source_law_summary,
        spec,
    )
    decision = _decision(obligation_summary, scenario_summary, radius_summary)
    outputs = {
        "domain_audit": domain_audit,
        "scenario_summary": scenario_summary,
        "radius_summary": radius_summary,
        "transport_semigroup": transport_semigroup,
        "source_profile_summary": source_profile_summary,
        "source_bin_summary": source_bin_summary,
        "source_law_summary": source_law_summary,
        "obligation_summary": obligation_summary,
        "sampled_worst_rows": sampled,
        "decision": decision,
    }
    metadata = {
        "source_name": "beta075_constitutive_1p1_proof_obligation",
        "closure_dir": str(closure_dir),
        "source_coupling_dir": str(source_coupling_dir),
        "point_closure": str(point_path),
        "point_closure_sha256": sha256_file(point_path),
        "closure_source_name": closure_manifest.get("source_name", ""),
        "symbol_spec": symbol_spec.__dict__,
        "constitutive_1p1_proof_spec": spec.__dict__,
        "scenarios": [scenario.__dict__ for scenario in scenarios],
        "radial_group_count": len(radial_groups),
        "service_group_count": len(service_groups),
        "scenario_workers": workers,
        "provenance": provenance,
        "claim_boundary": (
            "Action-level fixed-background proof-obligation certificate for the observed-amplitude "
            "full 1+1 constitutive source-coupled beta075 class. It certifies the discrete scheduled "
            "source law, bounded common timing jitter, positive/nonamplifying split-step transport, "
            "and local rapidity-budget invariance on the sealed fixed background. It is not a coupled "
            "Einstein-matter theorem or final continuum action proof."
        ),
    }
    return outputs, metadata


def write_constitutive_1p1_proof_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "domain_audit": outdir / "beta075_constitutive_1p1_proof_domain_audit.csv",
        "scenario_summary": outdir / "beta075_constitutive_1p1_proof_scenario_summary.csv",
        "radius_summary": outdir / "beta075_constitutive_1p1_proof_radius_summary.csv",
        "transport_semigroup": outdir / "beta075_constitutive_1p1_proof_transport_semigroup.csv",
        "source_profile_summary": outdir / "beta075_constitutive_1p1_proof_source_profile_summary.csv",
        "source_bin_summary": outdir / "beta075_constitutive_1p1_proof_source_bin_summary.csv",
        "source_law_summary": outdir / "beta075_constitutive_1p1_proof_source_law_summary.csv",
        "obligation_summary": outdir / "beta075_constitutive_1p1_proof_obligation_summary.csv",
        "sampled_worst_rows": outdir / "beta075_constitutive_1p1_proof_sampled_worst_rows.csv",
        "decision": outdir / "beta075_constitutive_1p1_proof_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    manifest_path = outdir / "beta075_constitutive_1p1_proof_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
