from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from .source_ledger import sha256_file, write_manifest


@dataclass(frozen=True)
class SourceLawDefinitionInputs:
    source_class_dir: Path
    covariant_dense_dir: Path
    principal_symbol_dir: Path
    source_law_feasibility_dir: Path
    proof_obligation_dir: Path
    robustness_dir: Path


@dataclass(frozen=True)
class SourceLawDefinitionSpec:
    scalar_compatibility_gate: float = 0.95
    ordinary_fluid_compatibility_gate: float = 0.95
    principal_symbol_fail_status: str = "fail"
    source_law_status_prefix: str = "phase_local_source_law_candidate"
    proof_pass_status: str = "constitutive_1p1_observed_class_proof_obligation_pass"
    robustness_pass_prefix: str = "discretization_robustness_pass"


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _source_law_terms() -> pd.DataFrame:
    rows = [
        {
            "term": "covariant_endpoint_tensor",
            "definition": "T_mu_nu = rho u_mu u_nu + p_l s_mu s_nu + pOmega Q_mu_nu + u_mu q_nu + u_nu q_mu",
            "variables": "rho,p_l,pOmega,u_mu,s_mu,Q_mu_nu,q_mu",
            "role": "covariant stress-energy target reproduced by ADM projections",
        },
        {
            "term": "radial_director",
            "definition": "u.u=-1, s.s=1, u.s=0, q_mu = j_l s_mu",
            "variables": "u_mu,s_mu,j_l",
            "role": "preferred service-radial/support direction for heat/current and exchange",
        },
        {
            "term": "bounded_rapidity_state",
            "definition": "regulated heat-current perturbation is transported as a bounded rapidity psi",
            "variables": "psi,tanh(psi),regulated_heat_flux_ratio",
            "role": "keeps heat/current updates inside causal transport coordinates",
        },
        {
            "term": "phase_local_source_scaling",
            "definition": "cap-0.95 scaling applies only to support_edge_endpoint_junction entry/catch support-edge slices",
            "variables": "source_profile_scale,stage,region,assignment",
            "role": "observed source law used by the full 1+1 proof class",
        },
        {
            "term": "service_schedule",
            "definition": "source rows release by service-coordinate order with bounded common timing jitter",
            "variables": "s,service_direction,timing_offset_steps",
            "role": "prevents arbitrary all-domain impulse collapse",
        },
        {
            "term": "positive_transport_semigroup",
            "definition": "radial and service upwind steps use nonnegative convex coefficients in the CFL range",
            "variables": "radial_cfl,service_cfl,state",
            "role": "maps nonnegative state to nonnegative state and is L1 non-amplifying",
        },
        {
            "term": "localized_support_exchange",
            "definition": "J_support^nu = -nabla_mu T_endpoint^{mu nu} localized to endpoint/support masks",
            "variables": "J_support^0,J_support^1,divergence_mask",
            "role": "open-system exchange channel rather than hidden live support",
        },
        {
            "term": "reduced_principal_symbol",
            "definition": "U=(h,psi,chi_Omega,pi_Omega,Phi_support,Pi_support,n_l)",
            "variables": "characteristic speeds,eigenbasis,cone margin",
            "role": "necessary local hyperbolicity/causality evidence for the constitutive sector",
        },
    ]
    return pd.DataFrame(rows)


def _evidence_summary(
    *,
    source_class_decision: pd.DataFrame,
    source_class_models: pd.DataFrame,
    covariant_decision: pd.DataFrame,
    principal_decision: pd.DataFrame,
    principal_run_summary: pd.DataFrame,
    source_law_decision: pd.DataFrame,
    proof_decision: pd.DataFrame,
    robustness_decision: pd.DataFrame,
) -> pd.DataFrame:
    source_class = source_class_decision.iloc[0]
    covariant = covariant_decision.iloc[0]
    principal = principal_decision.iloc[0]
    source_law = source_law_decision.iloc[0]
    proof = proof_decision.iloc[0]
    robust = robustness_decision.iloc[0]
    promoted = principal_run_summary.loc[principal_run_summary["kind"].astype(str).eq("reference_24x14")]
    dense = promoted.loc[promoted["mesh"].astype(str).eq("dense")]
    dense_row = dense.iloc[0] if len(dense) else promoted.iloc[0]
    regulated = source_class_models.loc[
        source_class_models["model_class"].astype(str).eq("regulated_anisotropic_heat_flux_medium")
    ]
    regulated_fraction = float(regulated["compatible_volume_fraction"].iloc[0]) if len(regulated) else float("nan")
    return pd.DataFrame([
        {
            "evidence": "source_class_screen",
            "status": "pass" if bool(source_class["regulated_anisotropic_passes"]) else "fail",
            "primary_value": regulated_fraction,
            "watch": False,
            "read": str(source_class["decision_read"]),
        },
        {
            "evidence": "covariant_tensor_identity",
            "status": "pass" if bool(covariant["passes_covariant_identity_audit"]) else "fail",
            "primary_value": float(covariant["max_projection_linf_error"]),
            "watch": False,
            "read": str(covariant["decision_read"]),
        },
        {
            "evidence": "exchange_localization",
            "status": "pass" if bool(covariant["exchange_localization_pass"]) else "fail",
            "primary_value": float(covariant["outside_allowed_divergence_fraction"]),
            "watch": float(covariant["live_divergence_fraction"]) > 0.0,
            "read": "covariant divergence is localized to allowed endpoint/support exchange masks",
        },
        {
            "evidence": "principal_symbol_hyperbolicity",
            "status": str(principal["principal_symbol_status"]),
            "primary_value": float(principal["dense_tightest_relative_cone_margin"]),
            "watch": str(principal["principal_symbol_status"]) == "watch",
            "read": str(principal["decision_read"]),
        },
        {
            "evidence": "dense_reference_principal_symbol",
            "status": str(dense_row["symbol_status"]),
            "primary_value": float(dense_row["min_relative_cone_margin"]),
            "watch": str(dense_row["symbol_status"]) == "watch",
            "read": "dense promoted reference has no fail rows and finite in-cone characteristic speeds",
        },
        {
            "evidence": "phase_local_source_law",
            "status": str(source_law["source_law_feasibility_status"]),
            "primary_value": float(source_law["min_source_profile_scale"]),
            "watch": bool(source_law["severe_scale_watch"]) or bool(source_law["smoothness_watch"]),
            "read": str(source_law["decision_read"]),
        },
        {
            "evidence": "observed_1p1_proof_class",
            "status": str(proof["constitutive_1p1_proof_status"]),
            "primary_value": float(proof["max_observed_budget_fraction"]),
            "watch": False,
            "read": "observed source-coupled 1+1 class preserves local rapidity budget without limiter",
        },
        {
            "evidence": "discretization_robustness",
            "status": str(robust["discretization_robustness_status"]),
            "primary_value": float(robust["max_budget_fraction"]),
            "watch": bool(robust["drift_watch"]),
            "read": "observed proof class is stable across service-step, tail, and positive-CFL variants",
        },
    ])


def _family_compatibility(source_class_models: pd.DataFrame, evidence: pd.DataFrame) -> pd.DataFrame:
    def model_fraction(model: str) -> float:
        match = source_class_models.loc[source_class_models["model_class"].astype(str).eq(model)]
        return float(match["compatible_volume_fraction"].iloc[0]) if len(match) else float("nan")

    principal_watch = bool(evidence.loc[evidence["evidence"].eq("principal_symbol_hyperbolicity"), "watch"].iloc[0])
    source_watch = bool(evidence.loc[evidence["evidence"].eq("phase_local_source_law"), "watch"].iloc[0])
    return pd.DataFrame([
        {
            "family": "single_scalar",
            "status": "ruled_out_as_primary",
            "compatibility_value": max(
                model_fraction("single_canonical_scalar"),
                model_fraction("single_phantom_scalar"),
            ),
            "role": "not sufficient except possibly as a subcomponent",
            "reason": "single scalar branches fail the source-class compatibility gate and cannot span heat/current plus angular demand",
        },
        {
            "family": "ordinary_type_i_anisotropic_heat_flux",
            "status": "too_narrow_alone",
            "compatibility_value": model_fraction("ordinary_type_i_anisotropic_heat_flux"),
            "role": "useful limit, not the full source law",
            "reason": "ordinary anisotropic heat-flux form is close but does not carry the regulator and exchange structure alone",
        },
        {
            "family": "regulated_anisotropic_heat_current_medium",
            "status": "core_endpoint_medium",
            "compatibility_value": model_fraction("regulated_anisotropic_heat_flux_medium"),
            "role": "primary tensor/source medium",
            "reason": "source-class screen, admissibility, covariant tensor identity, and field closure all support this medium",
        },
        {
            "family": "entrained_radial_director_or_aether_like_medium",
            "status": "lead_physical_family_with_hyperbolicity_watch" if principal_watch else "lead_physical_family",
            "compatibility_value": 1.0,
            "role": "organizes preferred radial direction, bounded rapidity transport, and characteristic structure",
            "reason": "the reduced principal symbol has real complete in-cone characteristics, with thin-margin watch rows",
        },
        {
            "family": "localized_elastic_support_reservoir",
            "status": "required_support_exchange_component_with_shape_watch" if source_watch else "required_support_exchange_component",
            "compatibility_value": 1.0,
            "role": "supplies localized endpoint/support exchange and phase-local source scaling",
            "reason": "covariant divergence localizes to endpoint/support exchange and the phase-local source law is bounded but sharp",
        },
        {
            "family": "open_system_effective_action",
            "status": "plausible_next_formalization",
            "compatibility_value": 1.0,
            "role": "best action-level container for localized non-conserved endpoint exchange",
            "reason": "the endpoint tensor is coherent but has localized exchange, so a closed isolated fluid action is too small",
        },
        {
            "family": "broad_multifield_fallback",
            "status": "compatible_but_not_lead",
            "compatibility_value": model_fraction("multi_field_effective_potential_fallback"),
            "role": "fallback only if the regulated director/support story fails",
            "reason": "available degrees of freedom are broader than currently needed",
        },
    ])


def _watch_summary(evidence: pd.DataFrame, family: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in evidence.loc[evidence["watch"].astype(bool)].iterrows():
        rows.append({
            "watch": str(row["evidence"]),
            "source": "evidence",
            "status": str(row["status"]),
            "read": str(row["read"]),
        })
    for _, row in family.loc[family["status"].astype(str).str.contains("watch", regex=False)].iterrows():
        rows.append({
            "watch": str(row["family"]),
            "source": "family",
            "status": str(row["status"]),
            "read": str(row["reason"]),
        })
    return pd.DataFrame(rows)


def _decision(
    evidence: pd.DataFrame,
    family: pd.DataFrame,
    spec: SourceLawDefinitionSpec,
) -> pd.DataFrame:
    status_by_evidence = {str(row["evidence"]): str(row["status"]) for _, row in evidence.iterrows()}
    hard_pass = (
        status_by_evidence["source_class_screen"] == "pass"
        and status_by_evidence["covariant_tensor_identity"] == "pass"
        and status_by_evidence["exchange_localization"] == "pass"
        and status_by_evidence["principal_symbol_hyperbolicity"] != spec.principal_symbol_fail_status
        and status_by_evidence["phase_local_source_law"].startswith(spec.source_law_status_prefix)
        and status_by_evidence["observed_1p1_proof_class"] == spec.proof_pass_status
        and status_by_evidence["discretization_robustness"].startswith(spec.robustness_pass_prefix)
    )
    watches = int(evidence["watch"].astype(bool).sum()) + int(family["status"].astype(str).str.contains("watch", regex=False).sum())
    status = (
        "source_law_definition_candidate_with_hyperbolicity_watches"
        if hard_pass and watches
        else "source_law_definition_candidate"
        if hard_pass
        else "source_law_definition_incomplete"
    )
    return pd.DataFrame([{
        "source_law_definition_status": status,
        "hard_definition_pass": hard_pass,
        "watch_count": watches,
        "lead_endpoint_medium": "regulated_anisotropic_heat_current_medium",
        "lead_dynamic_family": "entrained_radial_director_or_aether_like_medium",
        "lead_exchange_family": "localized_elastic_support_reservoir/open_system_effective_action",
        "scalar_only_ruled_out": bool(family.loc[family["family"].eq("single_scalar"), "status"].iloc[0] == "ruled_out_as_primary"),
        "ordinary_fluid_alone_too_narrow": bool(family.loc[family["family"].eq("ordinary_type_i_anisotropic_heat_flux"), "status"].iloc[0] == "too_narrow_alone"),
        "principal_symbol_status": status_by_evidence["principal_symbol_hyperbolicity"],
        "decision_read": (
            "observed beta075 source law is a defined regulated anisotropic heat-current/director/support-exchange candidate with hyperbolicity and source-shape watches"
            if hard_pass and watches
            else "observed beta075 source law is a defined candidate without configured watches"
            if hard_pass
            else "source-law definition is missing at least one hard evidence gate"
        ),
    }])


def build_source_law_definition_package(
    inputs: SourceLawDefinitionInputs,
    *,
    spec: SourceLawDefinitionSpec | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    spec = spec or SourceLawDefinitionSpec()
    source_class_decision = _read_csv(inputs.source_class_dir / "endpoint_j_source_class_feasibility_decision.csv")
    source_class_models = _read_csv(inputs.source_class_dir / "endpoint_j_source_class_model_summary.csv")
    covariant_decision = _read_csv(inputs.covariant_dense_dir / "endpoint_medium_covariant_decision.csv")
    principal_decision = _read_csv(inputs.principal_symbol_dir / "endpoint_support_principal_symbol_decision.csv")
    principal_run_summary = _read_csv(inputs.principal_symbol_dir / "endpoint_support_principal_symbol_run_summary.csv")
    source_law_decision = _read_csv(inputs.source_law_feasibility_dir / "endpoint_support_source_law_feasibility_decision.csv")
    proof_decision = _read_csv(inputs.proof_obligation_dir / "beta075_constitutive_1p1_proof_decision.csv")
    robustness_decision = _read_csv(inputs.robustness_dir / "beta075_constitutive_1p1_discretization_decision.csv")

    definition = _source_law_terms()
    evidence = _evidence_summary(
        source_class_decision=source_class_decision,
        source_class_models=source_class_models,
        covariant_decision=covariant_decision,
        principal_decision=principal_decision,
        principal_run_summary=principal_run_summary,
        source_law_decision=source_law_decision,
        proof_decision=proof_decision,
        robustness_decision=robustness_decision,
    )
    family = _family_compatibility(source_class_models, evidence)
    watches = _watch_summary(evidence, family)
    decision = _decision(evidence, family, spec)
    outputs = {
        "law_definition": definition,
        "evidence_summary": evidence,
        "family_compatibility": family,
        "watch_summary": watches,
        "decision": decision,
    }
    input_paths = {
        "source_class_decision": inputs.source_class_dir / "endpoint_j_source_class_feasibility_decision.csv",
        "source_class_models": inputs.source_class_dir / "endpoint_j_source_class_model_summary.csv",
        "covariant_decision": inputs.covariant_dense_dir / "endpoint_medium_covariant_decision.csv",
        "principal_decision": inputs.principal_symbol_dir / "endpoint_support_principal_symbol_decision.csv",
        "principal_run_summary": inputs.principal_symbol_dir / "endpoint_support_principal_symbol_run_summary.csv",
        "source_law_decision": inputs.source_law_feasibility_dir / "endpoint_support_source_law_feasibility_decision.csv",
        "proof_decision": inputs.proof_obligation_dir / "beta075_constitutive_1p1_proof_decision.csv",
        "robustness_decision": inputs.robustness_dir / "beta075_constitutive_1p1_discretization_decision.csv",
    }
    metadata = {
        "source_name": "beta075_source_law_definition_package",
        "spec": spec.__dict__,
        "inputs": {key: str(path) for key, path in input_paths.items()},
        "input_sha256": {key: sha256_file(path) for key, path in input_paths.items()},
        "covariant_manifest": _read_json(inputs.covariant_dense_dir / "endpoint_medium_covariant_manifest.json").get("source_name", ""),
        "claim_boundary": (
            "Observed-amplitude source-law definition package. It states the effective constitutive law and "
            "maps it to source-family evidence, principal-symbol/hyperbolicity evidence, covariant tensor identity, "
            "and fixed-background proof-class robustness. It is not a final matter action or coupled Einstein-matter proof."
        ),
    }
    return outputs, metadata


def write_source_law_definition_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "law_definition": outdir / "beta075_source_law_definition_terms.csv",
        "evidence_summary": outdir / "beta075_source_law_evidence_summary.csv",
        "family_compatibility": outdir / "beta075_source_law_family_compatibility.csv",
        "watch_summary": outdir / "beta075_source_law_watch_summary.csv",
        "decision": outdir / "beta075_source_law_definition_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    manifest_path = outdir / "beta075_source_law_definition_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
