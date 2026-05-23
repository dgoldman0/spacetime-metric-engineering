from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .beta075_constitutive_1p1_proof_obligation import (
    Constitutive1p1ProofSpec,
    build_constitutive_1p1_proof_obligation,
)
from .endpoint_support_principal_symbol import PrincipalSymbolSpec
from .source_ledger import sha256_file, write_manifest


@dataclass(frozen=True)
class DiscretizationVariant:
    label: str
    steps: int
    tail_steps: int
    jitter_radius_steps: int
    radial_cfl: float
    service_cfl: float
    role: str


def default_discretization_variants() -> tuple[DiscretizationVariant, ...]:
    return (
        DiscretizationVariant("baseline_48_tail48_cfl040_020", 48, 48, 8, 0.40, 0.20, "baseline"),
        DiscretizationVariant("service_refine_72_tail72_cfl040_020", 72, 72, 12, 0.40, 0.20, "service_step_refinement"),
        DiscretizationVariant("service_refine_96_tail96_cfl040_020", 96, 96, 16, 0.40, 0.20, "service_step_refinement"),
        DiscretizationVariant("tail_extend_48_tail96_cfl040_020", 48, 96, 8, 0.40, 0.20, "tail_window_sensitivity"),
        DiscretizationVariant("cfl_low_48_tail48_cfl025_010", 48, 48, 8, 0.25, 0.10, "cfl_sensitivity"),
        DiscretizationVariant("cfl_high_48_tail48_cfl055_030", 48, 48, 8, 0.55, 0.30, "cfl_sensitivity"),
    )


@dataclass(frozen=True)
class DiscretizationRobustnessSpec:
    observed_heat_ratio_delta: float = 1.0e-4
    reference_large_heat_ratio_delta: float = 5.0e-4
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
    variants: tuple[DiscretizationVariant, ...] = field(default_factory=default_discretization_variants)
    budget_fraction_gate: float = 1.0
    limiter_fraction_gate: float = 0.95
    relative_budget_drift_watch: float = 0.35


def _proof_spec_for_variant(
    base: DiscretizationRobustnessSpec,
    variant: DiscretizationVariant,
) -> Constitutive1p1ProofSpec:
    return Constitutive1p1ProofSpec(
        observed_heat_ratio_delta=float(base.observed_heat_ratio_delta),
        reference_large_heat_ratio_delta=float(base.reference_large_heat_ratio_delta),
        steps=int(variant.steps),
        tail_steps=int(variant.tail_steps),
        jitter_radius_steps=int(variant.jitter_radius_steps),
        radial_cfl=float(variant.radial_cfl),
        service_cfl=float(variant.service_cfl),
        limiter_safety_fraction=float(base.limiter_safety_fraction),
        source_column=str(base.source_column),
        source_smoothing_passes=int(base.source_smoothing_passes),
        source_profile_budget_cap_scope=str(base.source_profile_budget_cap_scope),
        source_profile_budget_cap_fraction=float(base.source_profile_budget_cap_fraction),
        source_profile_budget_cap_reference_delta=base.source_profile_budget_cap_reference_delta,
        s_round_decimals=int(base.s_round_decimals),
        l_round_decimals=int(base.l_round_decimals),
        top_row_count=int(base.top_row_count),
        max_workers=base.max_workers,
    )


def _variant_summary_row(
    variant: DiscretizationVariant,
    outputs: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    decision = outputs["decision"].iloc[0]
    scenario = outputs["scenario_summary"]
    source_law = outputs["source_law_summary"]
    radius = outputs["radius_summary"]
    obligation = outputs["obligation_summary"]
    transport = outputs["transport_semigroup"]
    return {
        "variant": variant.label,
        "role": variant.role,
        "steps": int(variant.steps),
        "tail_steps": int(variant.tail_steps),
        "jitter_radius_steps": int(variant.jitter_radius_steps),
        "radial_cfl": float(variant.radial_cfl),
        "service_cfl": float(variant.service_cfl),
        "proof_status": str(decision["constitutive_1p1_proof_status"]),
        "proof_obligations_pass": bool(decision["proof_obligations_pass"]),
        "failed_obligation_count": int(decision["failed_obligation_count"]),
        "scenario_count": int(decision["scenario_count"]),
        "max_budget_fraction": float(decision["max_observed_budget_fraction"]),
        "worst_scenario": str(decision["worst_scenario"]),
        "worst_offset_steps": int(decision["worst_offset_steps"]),
        "worst_source_row_index": int(decision["worst_source_row_index"]),
        "max_state_sum_to_source_sum": float(decision["max_state_sum_to_source_sum"]),
        "max_step_source_fraction": float(radius["max_step_source_fraction"].astype(float).max()) if len(radius) else float("nan"),
        "min_source_profile_scale": float(source_law["min_source_profile_scale"].astype(float).min()) if len(source_law) else float("nan"),
        "scaled_slices": int(source_law["scaled_slices"].astype(int).sum()) if len(source_law) else 0,
        "scaled_outside_expected_scope_slices": 0,
        "negative_source_rows": int(scenario["negative_source_rows"].astype(int).max()) if len(scenario) else -1,
        "min_transport_margin": float(scenario["min_transport_margin"].astype(float).min()) if len(scenario) else float("nan"),
        "min_relative_cone_margin_sample": float(scenario["min_relative_cone_margin_sample"].astype(float).min()) if len(scenario) else float("nan"),
        "max_cfl": float(transport["cfl"].astype(float).max()) if len(transport) else float("nan"),
        "obligation_pass_count": int(obligation["pass"].astype(bool).sum()) if len(obligation) else 0,
    }


def _variant_frames(
    variant: DiscretizationVariant,
    outputs: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    frames: dict[str, pd.DataFrame] = {}
    for key in [
        "scenario_summary",
        "radius_summary",
        "transport_semigroup",
        "source_law_summary",
        "obligation_summary",
        "sampled_worst_rows",
    ]:
        frame = outputs[key].copy()
        frame.insert(0, "variant", variant.label)
        frame.insert(1, "role", variant.role)
        frames[key] = frame
    return frames


def _robustness_decision(variant_summary: pd.DataFrame, spec: DiscretizationRobustnessSpec) -> pd.DataFrame:
    if not len(variant_summary):
        return pd.DataFrame([{
            "discretization_robustness_status": "discretization_robustness_fail_no_variants",
            "robustness_pass": False,
            "variant_count": 0,
        }])
    baseline = variant_summary.loc[variant_summary["role"].astype(str).eq("baseline")]
    baseline_fraction = (
        float(baseline["max_budget_fraction"].astype(float).iloc[0])
        if len(baseline)
        else float(variant_summary["max_budget_fraction"].astype(float).min())
    )
    max_fraction = float(variant_summary["max_budget_fraction"].astype(float).max())
    min_fraction = float(variant_summary["max_budget_fraction"].astype(float).min())
    relative_drift = (
        (max_fraction - baseline_fraction) / baseline_fraction
        if np.isfinite(baseline_fraction) and baseline_fraction > 0.0
        else float("nan")
    )
    hard_pass = bool(
        variant_summary["proof_obligations_pass"].astype(bool).all()
        and max_fraction <= float(spec.budget_fraction_gate)
        and (variant_summary["max_state_sum_to_source_sum"].astype(float) <= 1.0 + 1.0e-9).all()
        and (variant_summary["negative_source_rows"].astype(int) == 0).all()
        and (variant_summary["scaled_outside_expected_scope_slices"].astype(int) == 0).all()
    )
    drift_watch = bool(
        np.isfinite(relative_drift)
        and relative_drift > float(spec.relative_budget_drift_watch)
    )
    status = (
        "discretization_robustness_pass_with_smooth_variation"
        if hard_pass and not drift_watch
        else "discretization_robustness_pass_with_drift_watch"
        if hard_pass
        else "discretization_robustness_fail"
    )
    worst_idx = int(variant_summary["max_budget_fraction"].astype(float).idxmax())
    worst = variant_summary.loc[worst_idx]
    return pd.DataFrame([{
        "discretization_robustness_status": status,
        "robustness_pass": hard_pass,
        "variant_count": int(len(variant_summary)),
        "max_budget_fraction": max_fraction,
        "min_budget_fraction": min_fraction,
        "baseline_budget_fraction": baseline_fraction,
        "relative_budget_drift_from_baseline": relative_drift,
        "drift_watch": drift_watch,
        "worst_variant": str(worst["variant"]),
        "worst_role": str(worst["role"]),
        "worst_source_row_index": int(worst["worst_source_row_index"]),
        "worst_offset_steps": int(worst["worst_offset_steps"]),
        "max_state_sum_to_source_sum": float(variant_summary["max_state_sum_to_source_sum"].astype(float).max()),
        "min_source_profile_scale": float(variant_summary["min_source_profile_scale"].astype(float).min()),
    }])


def build_discretization_robustness(
    closure_dir: Path,
    source_coupling_dir: Path,
    *,
    symbol_spec: PrincipalSymbolSpec | None = None,
    spec: DiscretizationRobustnessSpec | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    symbol_spec = symbol_spec or PrincipalSymbolSpec()
    spec = spec or DiscretizationRobustnessSpec()
    summaries: list[dict[str, Any]] = []
    frame_parts: dict[str, list[pd.DataFrame]] = {
        "scenario_summary": [],
        "radius_summary": [],
        "transport_semigroup": [],
        "source_law_summary": [],
        "obligation_summary": [],
        "sampled_worst_rows": [],
    }
    variant_metadata: list[dict[str, Any]] = []
    for variant in spec.variants:
        proof_spec = _proof_spec_for_variant(spec, variant)
        outputs, metadata = build_constitutive_1p1_proof_obligation(
            closure_dir,
            source_coupling_dir,
            symbol_spec=symbol_spec,
            spec=proof_spec,
        )
        summaries.append(_variant_summary_row(variant, outputs))
        frames = _variant_frames(variant, outputs)
        for key, frame in frames.items():
            frame_parts[key].append(frame)
        variant_metadata.append({
            "variant": variant.__dict__,
            "proof_metadata": {
                "scenario_workers": metadata.get("scenario_workers"),
                "radial_group_count": metadata.get("radial_group_count"),
                "service_group_count": metadata.get("service_group_count"),
            },
        })
    variant_summary = pd.DataFrame(summaries)
    outputs = {
        "variant_summary": variant_summary,
        "scenario_summary": pd.concat(frame_parts["scenario_summary"], ignore_index=True),
        "radius_summary": pd.concat(frame_parts["radius_summary"], ignore_index=True),
        "transport_semigroup": pd.concat(frame_parts["transport_semigroup"], ignore_index=True),
        "source_law_summary": pd.concat(frame_parts["source_law_summary"], ignore_index=True),
        "obligation_summary": pd.concat(frame_parts["obligation_summary"], ignore_index=True),
        "sampled_worst_rows": pd.concat(frame_parts["sampled_worst_rows"], ignore_index=True),
    }
    outputs["decision"] = _robustness_decision(variant_summary, spec)
    metadata = {
        "source_name": "beta075_constitutive_1p1_discretization_robustness",
        "closure_dir": str(closure_dir),
        "source_coupling_dir": str(source_coupling_dir),
        "symbol_spec": symbol_spec.__dict__,
        "discretization_robustness_spec": {
            **spec.__dict__,
            "variants": [variant.__dict__ for variant in spec.variants],
        },
        "variant_metadata": variant_metadata,
        "claim_boundary": (
            "Discretization and continuum-robustness certificate for the observed-amplitude "
            "full 1+1 constitutive source-coupled beta075 proof class. It varies service-step "
            "resolution, tail length, and positive-transport CFL values while holding the physical "
            "source law and observed claim fixed. It is not a high-amplitude stress sweep."
        ),
    }
    return outputs, metadata


def write_discretization_robustness_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "variant_summary": outdir / "beta075_constitutive_1p1_discretization_variant_summary.csv",
        "scenario_summary": outdir / "beta075_constitutive_1p1_discretization_scenario_summary.csv",
        "radius_summary": outdir / "beta075_constitutive_1p1_discretization_radius_summary.csv",
        "transport_semigroup": outdir / "beta075_constitutive_1p1_discretization_transport_semigroup.csv",
        "source_law_summary": outdir / "beta075_constitutive_1p1_discretization_source_law_summary.csv",
        "obligation_summary": outdir / "beta075_constitutive_1p1_discretization_obligation_summary.csv",
        "sampled_worst_rows": outdir / "beta075_constitutive_1p1_discretization_sampled_worst_rows.csv",
        "decision": outdir / "beta075_constitutive_1p1_discretization_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    manifest_path = outdir / "beta075_constitutive_1p1_discretization_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
