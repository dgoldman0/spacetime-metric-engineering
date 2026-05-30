"""Superconducting-resonator backend for the Stage 5 White Casimir ladder."""

from __future__ import annotations

import math
from dataclasses import asdict
from typing import Mapping

import numpy as np
import pandas as pd

from .readout_transduction import ReadoutCandidate, TransductionResult
from .stage5_models import EPSILON, Stage5InputContext
from .stage5_physical_priors import superconducting_priors


def _required_gain(required_sbr: float, predicted_sbr: float) -> float:
    return float(required_sbr / max(predicted_sbr, EPSILON))


def evaluate_superconducting_backend(
    candidate: ReadoutCandidate,
    context: Stage5InputContext,
    schedule: pd.DataFrame,
    shell_template: Mapping[str, np.ndarray],
) -> tuple[list[TransductionResult], pd.DataFrame]:
    template = np.asarray(shell_template[candidate.candidate_id], dtype=float)
    shell_energy = max(context.max_integrated_shell_energy_J, EPSILON)
    rows: list[TransductionResult] = []
    detail_rows: list[dict[str, object]] = []

    for prior in superconducting_priors():
        shell_shift = shell_energy / max(prior.stored_energy_J, EPSILON) * prior.mode_overlap
        kinetic = shell_shift * prior.kinetic_inductance_fraction
        surface_loss = shell_shift * prior.surface_loss_fraction
        vortex = shell_shift * prior.vortex_fraction
        quasiparticle = shell_shift * prior.quasiparticle_fraction
        thermal = shell_shift * prior.thermal_fraction
        material_control = shell_shift * prior.material_control_fraction
        background = math.sqrt(
            prior.frequency_floor_fraction**2
            + kinetic**2
            + surface_loss**2
            + vortex**2
            + quasiparticle**2
            + thermal**2
            + material_control**2
        )
        predicted_sbr = float(shell_shift / max(background, EPSILON))
        nuisance_to_shell = float(max(kinetic, surface_loss, vortex, quasiparticle, thermal, material_control) / max(shell_shift, EPSILON))
        adversarial_status = "controlled" if nuisance_to_shell <= 0.18 else "superconducting_material_degenerate"
        model_status = (
            "physical_backend_controlled" if adversarial_status == "controlled" else "physical_backend_nuisance_degenerate"
        )
        detail = {
            **asdict(prior),
            "candidate_id": candidate.candidate_id,
            "scenario": prior.case_id,
            "backend": "superconducting_resonator_physical",
            "shell_fractional_frequency_shift": shell_shift,
            "kinetic_inductance_fractional_shift": kinetic,
            "surface_loss_fractional_shift": surface_loss,
            "vortex_fractional_shift": vortex,
            "quasiparticle_fractional_shift": quasiparticle,
            "thermal_fractional_shift": thermal,
            "material_control_fractional_shift": material_control,
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
                    dominant_nuisance="surface_loss" if surface_loss >= vortex else "vortex_loss",
                    model_status=model_status,
                    model_provenance="superconducting_backend_with_mode_overlap_kinetic_loss_vortex_quasiparticle_priors",
                    optimism_level=prior.case_id,
                    model_notes=(
                        "Superconducting resonator backend with shell overlap, kinetic inductance, surface loss, "
                        "vortex, quasiparticle, thermal, and material-control nuisance priors."
                    ),
                )
            )
    return rows, pd.DataFrame(detail_rows)
