"""Differential-pressure physical backend for the Stage 5 White Casimir ladder."""

from __future__ import annotations

import math
from dataclasses import asdict
from typing import Mapping

import numpy as np
import pandas as pd

from .readout_transduction import ReadoutCandidate, TransductionResult
from .stage5_models import EPSILON, Stage5InputContext
from .stage5_physical_priors import pressure_priors


def _required_gain(required_sbr: float, predicted_sbr: float) -> float:
    return float(required_sbr / max(predicted_sbr, EPSILON))


def evaluate_pressure_backend(
    candidate: ReadoutCandidate,
    context: Stage5InputContext,
    schedule: pd.DataFrame,
    shell_template: Mapping[str, np.ndarray],
) -> tuple[list[TransductionResult], pd.DataFrame]:
    template = np.asarray(shell_template[candidate.candidate_id], dtype=float)
    pressure = max(context.max_shell_pressure_Pa, EPSILON)
    rows: list[TransductionResult] = []
    detail_rows: list[dict[str, object]] = []

    for prior in pressure_priors():
        shell_pressure = pressure * prior.shell_gap_modulation
        patch_pressure = pressure * context.median_patch_to_casimir_ratio * prior.patch_residual_fraction
        patch_pressure /= max(prior.common_mode_rejection, 1.0)
        roughness_pressure = pressure * prior.roughness_fraction
        background = math.sqrt(
            prior.pressure_floor_Pa**2
            + patch_pressure**2
            + roughness_pressure**2
            + prior.membrane_drift_Pa**2
            + prior.thermal_drift_Pa**2
        )
        predicted_sbr = float(shell_pressure / max(background, EPSILON))
        nuisance_to_shell = float(max(patch_pressure, roughness_pressure, prior.membrane_drift_Pa, prior.thermal_drift_Pa) / max(shell_pressure, EPSILON))
        adversarial_status = "controlled" if nuisance_to_shell <= 0.5 else "dominant_nuisance"
        model_status = (
            "physical_backend_controlled" if adversarial_status == "controlled" else "physical_backend_nuisance_degenerate"
        )
        detail = {
            **asdict(prior),
            "candidate_id": candidate.candidate_id,
            "scenario": prior.case_id,
            "backend": "differential_pressure_physical",
            "shell_pressure_Pa": shell_pressure,
            "patch_pressure_Pa": patch_pressure,
            "roughness_pressure_Pa": roughness_pressure,
            "background_pressure_rms_Pa": background,
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
                    shell_observable=float(shell_pressure * value),
                    shell_observable_unit="Pa",
                    background_observable_rms=float(background),
                    predicted_sbr=predicted_sbr,
                    required_gain_to_stage4_gate=_required_gain(context.stage4_required_sbr, predicted_sbr),
                    claim_class=candidate.claim_class,
                    allowed_claim=candidate.allowed_claim,
                    dominant_nuisance="patch_potential" if patch_pressure >= roughness_pressure else "surface_roughness",
                    model_status=model_status,
                    model_provenance="differential_pressure_backend_with_patch_roughness_membrane_thermal_priors",
                    optimism_level=prior.case_id,
                    model_notes=(
                        "Paired-cell shell pressure contrast with common-mode rejection, "
                        "patch residual, roughness, membrane drift, and thermal drift."
                    ),
                )
            )
    return rows, pd.DataFrame(detail_rows)
