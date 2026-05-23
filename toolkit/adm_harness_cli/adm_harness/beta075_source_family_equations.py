from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from .source_ledger import sha256_file, write_manifest


@dataclass(frozen=True)
class SourceFamilyEquationInputs:
    source_law_dir: Path
    principal_symbol_dir: Path
    field_closure_dir: Path
    stroke_exchange_dir: Path
    total_closure_dir: Path
    robustness_dir: Path


@dataclass(frozen=True)
class SourceFamilyEquationSpec:
    source_law_status_prefix: str = "source_law_definition_candidate"
    principal_symbol_fail_status: str = "fail"
    source_law_feasibility_prefix: str = "phase_local_source_law_candidate"
    robustness_pass_prefix: str = "discretization_robustness_pass"
    component_pf_l1_gate: float = 0.50
    component_pf_l1_watch_fraction: float = 0.80
    total_closure_local_pf_watch_fraction: float = 0.90
    principal_margin_watch_gate: float = 1.0e-3
    source_profile_scale_watch_gate: float = 0.15
    required_blocks: tuple[str, ...] = (
        "endpoint_medium",
        "director_constraints",
        "regulator_transport",
        "support_exchange",
        "support_reservoir",
        "source_response",
        "hyperbolic_evolution",
        "open_system_action",
    )


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if not math.isfinite(number):
        return default
    return number


def _truth(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _status(
    *,
    pass_condition: bool,
    watch_condition: bool = False,
    fail_status: str = "fail",
    pass_status: str = "pass",
    watch_status: str = "watch",
) -> str:
    if not pass_condition:
        return fail_status
    if watch_condition:
        return watch_status
    return pass_status


def _source_family_equations() -> pd.DataFrame:
    rows = [
        {
            "equation_id": "E01",
            "equation_block": "endpoint_medium",
            "equation_name": "regulated_anisotropic_endpoint_tensor",
            "equation": "T_endpoint^{mu nu}=rho u^mu u^nu+p_l s^mu s^nu+pOmega Q^{mu nu}+u^mu q^nu+u^nu q^mu",
            "variables": "rho,p_l,pOmega,u^mu,s^mu,Q^{mu nu},q^mu",
            "evidence_dependency": "covariant_tensor_identity,source_class_screen",
            "role": "stress-energy target for the endpoint medium",
        },
        {
            "equation_id": "E02",
            "equation_block": "director_constraints",
            "equation_name": "radial_director_constraints",
            "equation": "u.u=-1; s.s=1; u.s=0; q^mu=j_l s^mu; Q^{mu nu}=g^{mu nu}+u^mu u^nu-s^mu s^nu",
            "variables": "u^mu,s^mu,j_l,Q^{mu nu}",
            "evidence_dependency": "source_law_definition_terms,field_closure",
            "role": "fixes the entrained radial direction and removes angular exchange freedom",
        },
        {
            "equation_id": "E03",
            "equation_block": "regulator_transport",
            "equation_name": "bounded_rapidity_regulator",
            "equation": "v_q=2 j_l/|rho+p_l|=tanh(psi); h_reg=1-v_q^2 >= 0",
            "variables": "j_l,rho,p_l,psi,h_reg",
            "evidence_dependency": "principal_symbol,field_closure,source_law_feasibility",
            "role": "keeps heat-current transport subluminal by construction",
        },
        {
            "equation_id": "E04",
            "equation_block": "endpoint_medium",
            "equation_name": "angular_response_closure",
            "equation": "C_Omega[chi_Omega;rho,p_l,pOmega,j_l]=0 with finite chi_Omega",
            "variables": "chi_Omega,pOmega,rho,p_l,j_l",
            "evidence_dependency": "field_closure",
            "role": "keeps angular pressure as an internal response of the endpoint medium",
        },
        {
            "equation_id": "E05",
            "equation_block": "support_exchange",
            "equation_name": "open_endpoint_balance",
            "equation": "nabla_mu T_endpoint^{mu nu}+J_support^nu=0",
            "variables": "T_endpoint^{mu nu},J_support^nu",
            "evidence_dependency": "covariant_divergence,exchange_localization",
            "role": "makes endpoint non-conservation explicit instead of hiding it",
        },
        {
            "equation_id": "E06",
            "equation_block": "support_exchange",
            "equation_name": "two_channel_support_exchange",
            "equation": "J_support^nu=P u^nu+F s^nu+J_perp^nu with J_perp^theta=J_perp^phi=0 on the audited surface",
            "variables": "P,F,u^nu,s^nu,J_perp^nu",
            "evidence_dependency": "stroke_exchange,total_closure",
            "role": "splits support exchange into power and radial-force channels",
        },
        {
            "equation_id": "E07",
            "equation_block": "support_reservoir",
            "equation_name": "conservation_restoring_support_tensor",
            "equation": "nabla_mu T_support^{mu nu}=J_support^nu using phase-aware stroke and stress-potential variables",
            "variables": "T_support^{mu nu},Phi_support,Pi_support,Sigma_support",
            "evidence_dependency": "stroke_exchange,total_closure",
            "role": "restores total conservation through an explicit localized support sector",
        },
        {
            "equation_id": "E08",
            "equation_block": "source_response",
            "equation_name": "phase_local_bounded_source_response",
            "equation": "S_psi=kappa_phase(s,l,stage,region) B_service(s,t) R_psi with 0<=kappa_phase<=0.95 on the scaled support-edge entry/catch slices",
            "variables": "S_psi,kappa_phase,B_service,R_psi,stage,region",
            "evidence_dependency": "source_law_feasibility,observed_1p1_proof_class",
            "role": "turns the observed source law into a bounded constitutive response",
        },
        {
            "equation_id": "E09",
            "equation_block": "source_response",
            "equation_name": "service_scheduled_release",
            "equation": "B_service is released in service-coordinate order with bounded common timing jitter",
            "variables": "B_service,s,timing_offset_steps",
            "evidence_dependency": "proof_obligation,discretization_robustness",
            "role": "keeps source timing inside the physically scheduled rail class",
        },
        {
            "equation_id": "E10",
            "equation_block": "hyperbolic_evolution",
            "equation_name": "positive_transport_evolution",
            "equation": "partial_tau psi+v_l partial_l psi+v_s partial_s psi=S_psi with positive split-step CFL coefficients",
            "variables": "psi,v_l,v_s,S_psi,radial_cfl,service_cfl",
            "evidence_dependency": "observed_1p1_proof_class,discretization_robustness",
            "role": "evolves the rapidity state without state amplification in the observed class",
        },
        {
            "equation_id": "E11",
            "equation_block": "hyperbolic_evolution",
            "equation_name": "reduced_principal_symbol_gate",
            "equation": "A^0(U) partial_t U+A^l(U) partial_l U=B(U); det(A^l-lambda A^0)=0 has real complete in-cone characteristics",
            "variables": "U=(h,psi,chi_Omega,pi_Omega,Phi_support,Pi_support,n_l)",
            "evidence_dependency": "principal_symbol",
            "role": "necessary hyperbolicity and causal propagation condition for the source family",
        },
        {
            "equation_id": "E12",
            "equation_block": "open_system_action",
            "equation_name": "fixed_background_effective_action_skeleton",
            "equation": "S_eff=S_endpoint[u,s,psi,chi_Omega]+S_support[Phi_support,Pi_support,Sigma_support]+S_int[P,F;u,s]",
            "variables": "S_endpoint,S_support,S_int,P,F,Phi_support,Pi_support,Sigma_support",
            "evidence_dependency": "source_family_equation_package",
            "role": "conservative open-system container on the fixed background, not a final closed matter theorem",
        },
    ]
    return pd.DataFrame(rows)


def _evidence_value(evidence: pd.DataFrame, name: str, column: str = "primary_value") -> Any:
    row = evidence.loc[evidence["evidence"].astype(str).eq(name)]
    if not len(row):
        return float("nan")
    return row[column].iloc[0]


def _component_exchange_summary(component_summary: pd.DataFrame) -> pd.DataFrame:
    if not len(component_summary):
        return pd.DataFrame(columns=[
            "component",
            "max_active_normalized_l1_error",
            "worst_group_key",
            "worst_fit_scope",
        ])
    frame = component_summary.copy()
    frame["active_normalized_l1_error"] = pd.to_numeric(
        frame.get("active_normalized_l1_error", pd.Series(dtype=float)),
        errors="coerce",
    )
    frame = frame.dropna(subset=["active_normalized_l1_error"])
    rows: list[dict[str, Any]] = []
    for component, group in frame.groupby("component"):
        worst_idx = group["active_normalized_l1_error"].astype(float).idxmax()
        worst = group.loc[worst_idx]
        rows.append({
            "component": str(component),
            "max_active_normalized_l1_error": float(worst["active_normalized_l1_error"]),
            "worst_group_key": str(worst.get("group_key", "")),
            "worst_fit_scope": str(worst.get("fit_scope", "")),
        })
    return pd.DataFrame(rows)


def _constraint_audit(
    *,
    evidence: pd.DataFrame,
    source_law_decision: pd.DataFrame,
    principal_decision: pd.DataFrame,
    field_closure: pd.DataFrame,
    stroke_exchange: pd.DataFrame,
    total_closure: pd.DataFrame,
    robustness: pd.DataFrame,
    spec: SourceFamilyEquationSpec,
) -> pd.DataFrame:
    source_law = source_law_decision.iloc[0]
    principal = principal_decision.iloc[0]
    field = field_closure.iloc[0]
    stroke = stroke_exchange.iloc[0]
    total = total_closure.iloc[0]
    robust = robustness.iloc[0]

    principal_status = str(principal["principal_symbol_status"])
    source_profile_scale = _finite(_evidence_value(evidence, "phase_local_source_law"), float("nan"))
    dense_margin = _finite(principal["dense_tightest_relative_cone_margin"], float("nan"))
    local_pf = _finite(total["local_max_closure_residual_to_target_abs_PF_ratio"], float("nan"))
    local_pf_gate = _finite(total["local_closure_pf_gate"], 1.0)

    return pd.DataFrame([
        {
            "gate": "source_law_definition",
            "status": _status(
                pass_condition=str(source_law["source_law_definition_status"]).startswith(spec.source_law_status_prefix),
                watch_condition=int(source_law["watch_count"]) > 0,
            ),
            "value": str(source_law["source_law_definition_status"]),
            "gate_value": spec.source_law_status_prefix,
            "read": "source family is defined, with inherited watches carried explicitly",
        },
        {
            "gate": "endpoint_tensor_identity",
            "status": _status(pass_condition=str(_evidence_value(evidence, "covariant_tensor_identity", "status")) == "pass"),
            "value": _finite(_evidence_value(evidence, "covariant_tensor_identity")),
            "gate_value": "pass",
            "read": "endpoint variables reconstruct the audited tensor",
        },
        {
            "gate": "constrained_field_closure",
            "status": _status(pass_condition=_truth(field["passes_constrained_field_closure"])),
            "value": _finite(field["worst_normalized_l1_error"]),
            "gate_value": "passes_constrained_field_closure",
            "read": str(field["decision_read"]),
        },
        {
            "gate": "reduced_principal_symbol",
            "status": _status(
                pass_condition=principal_status != spec.principal_symbol_fail_status,
                watch_condition=principal_status == "watch" or dense_margin < spec.principal_margin_watch_gate,
            ),
            "value": dense_margin,
            "gate_value": spec.principal_margin_watch_gate,
            "read": str(principal["decision_read"]),
        },
        {
            "gate": "support_stroke_exchange",
            "status": _status(pass_condition=_truth(stroke["passes_support_stroke_exchange_fit"])),
            "value": _finite(stroke["best_normalized_active_abs_PF_l1_error"]),
            "gate_value": _finite(stroke["active_pf_l1_gate"], spec.component_pf_l1_gate),
            "read": str(stroke["decision_read"]),
        },
        {
            "gate": "support_total_conservation",
            "status": _status(
                pass_condition=_truth(total["passes_support_total_closure"]),
                watch_condition=local_pf > spec.total_closure_local_pf_watch_fraction * local_pf_gate,
            ),
            "value": local_pf,
            "gate_value": local_pf_gate,
            "read": str(total["decision_read"]),
        },
        {
            "gate": "phase_local_source_response",
            "status": _status(
                pass_condition=str(_evidence_value(evidence, "phase_local_source_law", "status")).startswith(
                    spec.source_law_feasibility_prefix
                ),
                watch_condition=source_profile_scale < spec.source_profile_scale_watch_gate
                or bool(_evidence_value(evidence, "phase_local_source_law", "watch")),
            ),
            "value": source_profile_scale,
            "gate_value": spec.source_profile_scale_watch_gate,
            "read": str(_evidence_value(evidence, "phase_local_source_law", "read")),
        },
        {
            "gate": "observed_discretization_robustness",
            "status": _status(
                pass_condition=str(robust["discretization_robustness_status"]).startswith(spec.robustness_pass_prefix),
                watch_condition=_truth(robust["drift_watch"]),
            ),
            "value": _finite(robust["max_budget_fraction"]),
            "gate_value": 1.0,
            "read": "observed source response survives discretization and CFL variation",
        },
    ])


def _exchange_channel_audit(
    *,
    component_summary: pd.DataFrame,
    stroke_exchange: pd.DataFrame,
    total_closure: pd.DataFrame,
    spec: SourceFamilyEquationSpec,
) -> pd.DataFrame:
    stroke = stroke_exchange.iloc[0]
    total = total_closure.iloc[0]
    components = _component_exchange_summary(component_summary)
    component_rows: list[dict[str, Any]] = []
    aggregate_exchange_pass = _truth(stroke["passes_support_stroke_exchange_fit"])
    for component in ("P", "F"):
        match = components.loc[components["component"].astype(str).eq(component)]
        if len(match):
            value = _finite(match["max_active_normalized_l1_error"].iloc[0], float("nan"))
            read = (
                f"{component} channel worst group {match['worst_group_key'].iloc[0]} "
                f"through {match['worst_fit_scope'].iloc[0]}"
            )
        else:
            value = _finite(stroke["best_normalized_active_abs_PF_l1_error"], float("nan"))
            read = f"{component} channel covered by aggregate P/F exchange fit"
        gate = spec.component_pf_l1_gate
        component_rows.append({
            "channel": "power_P" if component == "P" else "radial_force_F",
            "status": _status(
                pass_condition=aggregate_exchange_pass and math.isfinite(value),
                watch_condition=value > gate * spec.component_pf_l1_watch_fraction,
            ),
            "value": value,
            "gate_value": gate,
            "read": read,
        })

    rows = [
        *component_rows,
        {
            "channel": "aggregate_PF_exchange",
            "status": _status(pass_condition=_truth(stroke["passes_support_stroke_exchange_fit"])),
            "value": _finite(stroke["best_normalized_active_abs_PF_l1_error"]),
            "gate_value": _finite(stroke["active_pf_l1_gate"], spec.component_pf_l1_gate),
            "read": str(stroke["decision_read"]),
        },
        {
            "channel": "total_conservation_restoration",
            "status": _status(pass_condition=_truth(total["passes_support_total_closure"])),
            "value": _finite(total["active_closure_residual_to_target_abs_PF_ratio"]),
            "gate_value": _finite(total["active_closure_pf_gate"], spec.component_pf_l1_gate),
            "read": "endpoint plus support exchange closes in the active support sector",
        },
        {
            "channel": "angular_exchange_absence",
            "status": _status(pass_condition=_truth(total["angular_support_pass"])),
            "value": _finite(total["full_total_closure_residual_angular_volume"]),
            "gate_value": _finite(total["angular_support_gate"], 1.0e-14),
            "read": "support completion does not require angular exchange volume",
        },
        {
            "channel": "support_tail_localization",
            "status": _status(pass_condition=_truth(total["localization_pass"])),
            "value": _finite(total["outside_support_tail_fraction"]),
            "gate_value": _finite(total["support_tail_fraction_gate"], 1.0e-3),
            "read": "support tensor tail remains localized to allowed endpoint/support masks",
        },
        {
            "channel": "live_support_exclusion",
            "status": _status(pass_condition=_finite(total["live_support_tail_fraction"]) <= _finite(total["live_support_fraction_gate"], 1.0e-4)),
            "value": _finite(total["live_support_tail_fraction"]),
            "gate_value": _finite(total["live_support_fraction_gate"], 1.0e-4),
            "read": "support reservoir does not buy closure through live support tail",
        },
    ]
    return pd.DataFrame(rows)


def _inherited_gate_summary(
    evidence: pd.DataFrame,
    family: pd.DataFrame,
    principal_run_summary: pd.DataFrame,
    robustness: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, row in evidence.iterrows():
        rows.append({
            "source": "source_law_evidence",
            "item": str(row["evidence"]),
            "status": str(row["status"]),
            "value": _finite(row["primary_value"], float("nan")),
            "watch": _truth(row["watch"]),
            "read": str(row["read"]),
        })
    for _, row in family.iterrows():
        rows.append({
            "source": "family_compatibility",
            "item": str(row["family"]),
            "status": str(row["status"]),
            "value": _finite(row["compatibility_value"], float("nan")),
            "watch": "watch" in str(row["status"]),
            "read": str(row["reason"]),
        })
    dense = principal_run_summary.loc[
        principal_run_summary["label"].astype(str).str.contains("dense", regex=False)
        & principal_run_summary["kind"].astype(str).eq("reference_24x14")
    ]
    if len(dense):
        row = dense.iloc[0]
        rows.append({
            "source": "principal_symbol_run",
            "item": "dense_reference_24x14",
            "status": str(row["symbol_status"]),
            "value": _finite(row["min_relative_cone_margin"]),
            "watch": str(row["symbol_status"]) == "watch",
            "read": "dense reference run carries the inherited thin-cone-margin watch",
        })
    robust = robustness.iloc[0]
    rows.append({
        "source": "robustness_decision",
        "item": "max_observed_robust_budget_fraction",
        "status": str(robust["discretization_robustness_status"]),
        "value": _finite(robust["max_budget_fraction"]),
        "watch": _truth(robust["drift_watch"]),
        "read": "discretization robustness remains below local rapidity budget",
    })
    return pd.DataFrame(rows)


def _claim_boundary() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "claim": "regulated_director_support_reservoir_equation_skeleton",
            "status": "included",
            "read": "the package states variables, constraints, exchange channels, source response, and hyperbolicity gates",
        },
        {
            "claim": "fixed_background_open_system_constitutive_model",
            "status": "included",
            "read": "the equations live on the prescribed beta075 service metric and restore total conservation through explicit support exchange",
        },
        {
            "claim": "closed_isolated_fluid_matter_action",
            "status": "excluded",
            "read": "localized endpoint/support exchange means a closed ordinary fluid action is not the current claim",
        },
        {
            "claim": "coupled_einstein_matter_evolution",
            "status": "excluded",
            "read": "the rung is fixed-background source-family formalization, not dynamical metric evolution",
        },
        {
            "claim": "global_hyperbolicity_theorem",
            "status": "excluded",
            "read": "the principal-symbol evidence is local and watch-bounded by thin support-edge margins",
        },
    ])


def _decision(
    *,
    equations: pd.DataFrame,
    constraint_audit: pd.DataFrame,
    exchange_audit: pd.DataFrame,
    spec: SourceFamilyEquationSpec,
) -> pd.DataFrame:
    blocks_present = set(equations["equation_block"].astype(str))
    required_present = all(block in blocks_present for block in spec.required_blocks)
    failed_constraints = constraint_audit.loc[constraint_audit["status"].astype(str).eq("fail")]
    failed_exchange = exchange_audit.loc[exchange_audit["status"].astype(str).eq("fail")]
    hard_pass = bool(required_present and len(failed_constraints) == 0 and len(failed_exchange) == 0)
    watch_count = int((constraint_audit["status"].astype(str) == "watch").sum()) + int(
        (exchange_audit["status"].astype(str) == "watch").sum()
    )
    status = (
        "formal_source_family_equations_candidate_with_hyperbolicity_and_exchange_watches"
        if hard_pass and watch_count
        else "formal_source_family_equations_candidate"
        if hard_pass
        else "formal_source_family_equations_incomplete"
    )
    principal = constraint_audit.loc[constraint_audit["gate"].eq("reduced_principal_symbol")].iloc[0]
    source_response = constraint_audit.loc[constraint_audit["gate"].eq("phase_local_source_response")].iloc[0]
    total = constraint_audit.loc[constraint_audit["gate"].eq("support_total_conservation")].iloc[0]
    exchange_max = float(exchange_audit["value"].astype(float).max()) if len(exchange_audit) else float("nan")
    return pd.DataFrame([{
        "formal_equation_status": status,
        "hard_equation_package_pass": hard_pass,
        "required_equation_blocks_present": required_present,
        "equation_count": int(len(equations)),
        "constraint_gate_count": int(len(constraint_audit)),
        "exchange_channel_gate_count": int(len(exchange_audit)),
        "failed_gate_count": int(len(failed_constraints) + len(failed_exchange)),
        "watch_count": watch_count,
        "lead_endpoint_medium": "regulated_anisotropic_heat_current_medium",
        "lead_dynamic_family": "entrained_radial_director_or_aether_like_medium",
        "lead_support_family": "localized_phase_aware_support_reservoir",
        "principal_symbol_status": str(principal["status"]),
        "dense_relative_cone_margin": _finite(principal["value"], float("nan")),
        "min_source_profile_scale": _finite(source_response["value"], float("nan")),
        "support_total_local_pf_ratio": _finite(total["value"], float("nan")),
        "max_exchange_channel_value": exchange_max,
        "decision_read": (
            "formal regulated-director/support-reservoir equations close as an observed fixed-background source-family skeleton, with hyperbolicity/source-shape/exchange-margin watches"
            if hard_pass and watch_count
            else "formal regulated-director/support-reservoir equations close without configured watches"
            if hard_pass
            else "formal source-family equations are missing a required block or inherited gate"
        ),
    }])


def build_source_family_equation_package(
    inputs: SourceFamilyEquationInputs,
    *,
    spec: SourceFamilyEquationSpec | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    spec = spec or SourceFamilyEquationSpec()
    source_law_decision = _read_csv(inputs.source_law_dir / "beta075_source_law_definition_decision.csv")
    source_law_evidence = _read_csv(inputs.source_law_dir / "beta075_source_law_evidence_summary.csv")
    family_compatibility = _read_csv(inputs.source_law_dir / "beta075_source_law_family_compatibility.csv")
    principal_decision = _read_csv(inputs.principal_symbol_dir / "endpoint_support_principal_symbol_decision.csv")
    principal_run_summary = _read_csv(inputs.principal_symbol_dir / "endpoint_support_principal_symbol_run_summary.csv")
    field_closure = _read_csv(inputs.field_closure_dir / "endpoint_medium_field_closure_decision.csv")
    stroke_exchange = _read_csv(inputs.stroke_exchange_dir / "endpoint_support_stroke_exchange_decision.csv")
    stroke_components = _read_csv(inputs.stroke_exchange_dir / "endpoint_support_stroke_exchange_selected_component_summary.csv")
    total_closure = _read_csv(inputs.total_closure_dir / "endpoint_support_total_closure_decision.csv")
    robustness = _read_csv(inputs.robustness_dir / "beta075_constitutive_1p1_discretization_decision.csv")

    equations = _source_family_equations()
    constraints = _constraint_audit(
        evidence=source_law_evidence,
        source_law_decision=source_law_decision,
        principal_decision=principal_decision,
        field_closure=field_closure,
        stroke_exchange=stroke_exchange,
        total_closure=total_closure,
        robustness=robustness,
        spec=spec,
    )
    exchange = _exchange_channel_audit(
        component_summary=stroke_components,
        stroke_exchange=stroke_exchange,
        total_closure=total_closure,
        spec=spec,
    )
    inherited = _inherited_gate_summary(
        source_law_evidence,
        family_compatibility,
        principal_run_summary,
        robustness,
    )
    claim_boundary = _claim_boundary()
    decision = _decision(
        equations=equations,
        constraint_audit=constraints,
        exchange_audit=exchange,
        spec=spec,
    )
    outputs = {
        "equations": equations,
        "constraint_audit": constraints,
        "exchange_channel_audit": exchange,
        "inherited_gate_summary": inherited,
        "claim_boundary": claim_boundary,
        "decision": decision,
    }
    input_paths = {
        "source_law_decision": inputs.source_law_dir / "beta075_source_law_definition_decision.csv",
        "source_law_evidence": inputs.source_law_dir / "beta075_source_law_evidence_summary.csv",
        "source_law_family": inputs.source_law_dir / "beta075_source_law_family_compatibility.csv",
        "principal_decision": inputs.principal_symbol_dir / "endpoint_support_principal_symbol_decision.csv",
        "principal_runs": inputs.principal_symbol_dir / "endpoint_support_principal_symbol_run_summary.csv",
        "field_closure": inputs.field_closure_dir / "endpoint_medium_field_closure_decision.csv",
        "stroke_exchange": inputs.stroke_exchange_dir / "endpoint_support_stroke_exchange_decision.csv",
        "stroke_components": inputs.stroke_exchange_dir / "endpoint_support_stroke_exchange_selected_component_summary.csv",
        "total_closure": inputs.total_closure_dir / "endpoint_support_total_closure_decision.csv",
        "robustness": inputs.robustness_dir / "beta075_constitutive_1p1_discretization_decision.csv",
    }
    metadata = {
        "source_name": "beta075_source_family_equation_package",
        "spec": spec.__dict__,
        "inputs": {key: str(path) for key, path in input_paths.items()},
        "input_sha256": {key: sha256_file(path) for key, path in input_paths.items()},
        "source_law_manifest": _read_json(inputs.source_law_dir / "beta075_source_law_definition_manifest.json").get("source_name", ""),
        "claim_boundary": (
            "Formal source-family equation package for the observed beta075 regulated director/support-reservoir story. "
            "This is a fixed-background open-system constitutive skeleton with inherited local hyperbolicity and PDE proof gates; "
            "it is not a final closed matter action, coupled Einstein-matter evolution, or global hyperbolicity theorem."
        ),
    }
    return outputs, metadata


def write_source_family_equation_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "equations": outdir / "beta075_source_family_equations.csv",
        "constraint_audit": outdir / "beta075_source_family_constraint_audit.csv",
        "exchange_channel_audit": outdir / "beta075_source_family_exchange_channel_audit.csv",
        "inherited_gate_summary": outdir / "beta075_source_family_inherited_gate_summary.csv",
        "claim_boundary": outdir / "beta075_source_family_claim_boundary.csv",
        "decision": outdir / "beta075_source_family_equation_decision.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    manifest_path = outdir / "beta075_source_family_equation_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
