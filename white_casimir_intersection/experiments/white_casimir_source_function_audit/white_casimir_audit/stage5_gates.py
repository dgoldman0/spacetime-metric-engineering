"""Gate evaluation for the White Casimir Stage 5 readout ladder."""

from __future__ import annotations

from typing import Mapping

import pandas as pd

from .readout_transduction import ReadoutCandidate, Stage5Config
from .stage5_models import Stage5InputContext


def _candidate_map(candidates: list[ReadoutCandidate]) -> dict[str, ReadoutCandidate]:
    return {candidate.candidate_id: candidate for candidate in candidates}


def _status_and_action(row: Mapping[str, object], candidate: ReadoutCandidate) -> tuple[str, str]:
    if candidate.claim_class == "material_response":
        return (
            "background_calibration_only",
            "Use as a material/ordinary-EM competitor calibration row, not as shell or metric evidence.",
        )
    if not bool(row["claim_identity_pass"]):
        return "closed_identity", "Clarify the observable identity before treating this as shell evidence."
    if not bool(row["amplitude_gate_pass"]):
        return "closed_amplitude", "A stronger physical transduction model or lower background floor is required."
    if not bool(row["recovery_gate_pass"]):
        return "closed_amplitude", "The candidate amplitude does not recover reliably in the synthetic gate."
    if not bool(row["false_positive_gate_pass"]):
        return "closed_false_positive", "Add controls or schedule dimensions to reduce EM-only recovery."
    if "high_fidelity" in str(candidate.model_status):
        return "candidate_for_apparatus_design", "Amplitude, recovery, false-positive, and identity gates pass."
    return "candidate_for_fidelity_upgrade", "Upgrade this analytic survivor with a candidate-specific physics backend."


def build_gate_ledgers(
    candidates: list[ReadoutCandidate],
    transduction: pd.DataFrame,
    recovery: pd.DataFrame,
    template_metrics: pd.DataFrame,
    context: Stage5InputContext,
    cfg: Stage5Config,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    candidate_by_id = _candidate_map(candidates)
    rows: list[dict[str, object]] = []
    grouped = transduction.groupby(["candidate_id", "scenario"], sort=True)
    for (candidate_id, scenario), group in grouped:
        candidate = candidate_by_id[str(candidate_id)]
        predicted_sbr = float(group["predicted_sbr"].iloc[0])
        required_gain = float(group["required_gain_to_stage4_gate"].iloc[0])
        rec_group = recovery[
            (recovery["candidate_id"] == candidate_id)
            & (recovery["scenario"] == scenario)
            & (recovery["simulation_family"] == "shell_plus_background")
        ]
        em_group = recovery[
            (recovery["candidate_id"] == candidate_id)
            & (recovery["scenario"] == scenario)
            & (recovery["simulation_family"] == "em_only")
        ]
        metrics = template_metrics[
            (template_metrics["candidate_id"] == candidate_id) & (template_metrics["scenario"] == scenario)
        ]
        recovery_fraction = float(rec_group["shell_recovered"].mean()) if not rec_group.empty else 0.0
        false_positive_rate = float(em_group["false_positive"].mean()) if not em_group.empty else 0.0
        max_corr = (
            float(metrics["max_abs_shell_nuisance_correlation"].iloc[0])
            if not metrics.empty
            else context.stage4_max_shell_nuisance_correlation
        )
        condition = float(metrics["template_condition_number"].iloc[0]) if not metrics.empty else 0.0
        row = {
            "candidate_id": candidate.candidate_id,
            "scenario": str(scenario),
            "claim_class": candidate.claim_class,
            "allowed_claim": candidate.allowed_claim,
            "predicted_sbr": predicted_sbr,
            "stage4_required_sbr": context.stage4_required_sbr,
            "required_gain_to_stage4_gate": required_gain,
            "recovery_fraction_at_predicted_sbr": recovery_fraction,
            "em_only_false_positive_rate": false_positive_rate,
            "max_abs_shell_nuisance_correlation": max_corr,
            "template_condition_number": condition,
            "dominant_nuisance": str(group["dominant_nuisance"].iloc[0]),
            "calibration_control_status": "declared_controls_required",
            "model_status": candidate.model_status,
            "amplitude_gate_pass": predicted_sbr >= context.stage4_required_sbr,
            "recovery_gate_pass": recovery_fraction >= cfg.recovery_threshold,
            "false_positive_gate_pass": false_positive_rate <= cfg.false_positive_threshold,
            "orthogonality_preferred_pass": max_corr <= cfg.preferred_correlation_threshold,
            "claim_identity_pass": candidate.claim_class in {"casimir_boundary", "metric_proxy", "material_response", "control"},
        }
        status, action = _status_and_action(row, candidate)
        row["gate_status"] = status
        row["recommended_next_action"] = action
        rows.append(row)

    gate_ledger = pd.DataFrame(rows).sort_values(
        ["gate_status", "predicted_sbr", "candidate_id", "scenario"],
        ascending=[True, False, True, True],
    )
    required_gain_ledger = gate_ledger[
        [
            "candidate_id",
            "scenario",
            "claim_class",
            "predicted_sbr",
            "stage4_required_sbr",
            "required_gain_to_stage4_gate",
            "gate_status",
            "recommended_next_action",
        ]
    ].copy()
    return gate_ledger.reset_index(drop=True), required_gain_ledger.reset_index(drop=True)

