"""High-Q cavity physical backend for the Stage 5 White Casimir ladder."""

from __future__ import annotations

import math
from dataclasses import asdict
from typing import Mapping

import numpy as np
import pandas as pd

from .readout_transduction import ReadoutCandidate, TransductionResult
from .stage5_models import EPSILON, Stage5InputContext
from .stage5_physical_priors import cavity_priors


def _required_gain(required_sbr: float, predicted_sbr: float) -> float:
    return float(required_sbr / max(predicted_sbr, EPSILON))


def evaluate_cavity_backend(
    candidate: ReadoutCandidate,
    context: Stage5InputContext,
    schedule: pd.DataFrame,
    shell_template: Mapping[str, np.ndarray],
) -> tuple[list[TransductionResult], pd.DataFrame]:
    template = np.asarray(shell_template[candidate.candidate_id], dtype=float)
    shell_energy = max(context.max_integrated_shell_energy_J, EPSILON)
    rows: list[TransductionResult] = []
    detail_rows: list[dict[str, object]] = []

    for prior in cavity_priors():
        shell_shift = shell_energy / max(prior.stored_energy_J, EPSILON) * prior.mode_overlap
        finite_conductivity = shell_shift * prior.finite_conductivity_fraction
        thermal = shell_shift * prior.thermal_fraction
        waveguide = shell_shift * prior.waveguide_fraction
        mode_mixing = shell_shift * prior.mode_mixing_fraction
        loss_channel = shell_shift * prior.loss_channel_fraction
        background = math.sqrt(
            prior.frequency_floor_fraction**2
            + finite_conductivity**2
            + thermal**2
            + waveguide**2
            + mode_mixing**2
            + loss_channel**2
        )
        predicted_sbr = float(shell_shift / max(background, EPSILON))
        nuisance_to_shell = float(max(finite_conductivity, thermal, waveguide, mode_mixing, loss_channel) / max(shell_shift, EPSILON))
        adversarial_status = "controlled" if nuisance_to_shell <= 0.25 else "mode_or_loss_degenerate"
        model_status = (
            "physical_backend_controlled" if adversarial_status == "controlled" else "physical_backend_nuisance_degenerate"
        )
        detail = {
            **asdict(prior),
            "candidate_id": candidate.candidate_id,
            "scenario": prior.case_id,
            "backend": "high_q_cavity_physical",
            "shell_fractional_frequency_shift": shell_shift,
            "finite_conductivity_fractional_shift": finite_conductivity,
            "thermal_fractional_shift": thermal,
            "waveguide_fractional_shift": waveguide,
            "mode_mixing_fractional_shift": mode_mixing,
            "loss_channel_fractional_shift": loss_channel,
            "background_fractional_rms": background,
            "predicted_sbr": predicted_sbr,
            "required_gain_to_stage4_gate": _required_gain(context.stage4_required_sbr, predicted_sbr),
            "nuisance_to_shell_ratio": nuisance_to_shell,
            "adversarial_material_status": adversarial_status,
        }
        detail_rows.append(detail)
        for order, value in enumerate(template):
            rows.append(
                TransductionResult(
                    candidate_id=candidate.candidate_id,
                    scenario=prior.case_id,
                    schedule_step=str(schedule.loc[order, "schedule_step"]),
                    schedule_order=int(order),
                    shell_observable=float(shell_shift * value),
                    shell_observable_unit="fractional_delta_f",
                    background_observable_rms=float(background),
                    predicted_sbr=predicted_sbr,
                    required_gain_to_stage4_gate=_required_gain(context.stage4_required_sbr, predicted_sbr),
                    claim_class=candidate.claim_class,
                    allowed_claim=candidate.allowed_claim,
                    dominant_nuisance="loss_channel" if loss_channel >= waveguide else "waveguide_dispersion",
                    model_status=model_status,
                    model_provenance="cavity_backend_with_mode_overlap_finite_conductivity_thermal_waveguide_loss_priors",
                    optimism_level=prior.case_id,
                    model_notes=(
                        "Perturbative cavity frequency-shift backend with shell overlap, finite conductivity, "
                        "thermal drift, waveguide dispersion, mode mixing, and Q/loss nuisance terms."
                    ),
                )
            )
    return rows, pd.DataFrame(detail_rows)
