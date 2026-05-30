"""Analytic first-pass readout models for the White Casimir Stage 5 ladder."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd

from .readout_transduction import ReadoutCandidate, TransductionResult


EPSILON = 1.0e-300

SCENARIO_FACTORS: dict[str, dict[str, float]] = {
    "conservative": {"signal_gain": 0.25, "background_gain": 2.0, "control_gain": 0.5},
    "nominal": {"signal_gain": 1.0, "background_gain": 1.0, "control_gain": 1.0},
    "optimistic": {"signal_gain": 5.0, "background_gain": 0.5, "control_gain": 3.0},
}


@dataclass(frozen=True)
class Stage5InputContext:
    stage3_dir: str
    stage4_dir: str
    stage4_required_sbr: float
    stage4_false_positive_rate: float
    stage4_max_shell_nuisance_correlation: float
    stage4_recovery_fraction_at_max_sbr: float
    max_integrated_shell_energy_J: float
    max_shell_pressure_Pa: float
    max_timing_bound_s: float
    max_readout_coupled_energy_J: float
    median_readout_source_fraction: float
    median_shell_channel_fraction: float
    median_patch_to_casimir_ratio: float
    median_casimir_to_material_ratio: float
    median_patch_energy_J: float
    median_capacitance_F: float
    median_material_mass_energy_J: float


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _median(frame: pd.DataFrame, column: str, default: float) -> float:
    if frame.empty or column not in frame:
        return float(default)
    values = pd.to_numeric(frame[column], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    return float(values.median()) if not values.empty else float(default)


def _max_abs(frame: pd.DataFrame, column: str, default: float) -> float:
    if frame.empty or column not in frame:
        return float(default)
    values = pd.to_numeric(frame[column], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    return float(values.abs().max()) if not values.empty else float(default)


def load_stage5_input_context(stage3_dir: str | Path, stage4_dir: str | Path) -> Stage5InputContext:
    stage3 = Path(stage3_dir)
    stage4 = Path(stage4_dir)
    stage4_summary = _read_json(stage4 / "summary.json")
    metric = _read_csv(stage3 / "scale" / "linearized_metric_bound.csv")
    material = _read_csv(stage3 / "material" / "material_competitor_summary.csv")
    readout = _read_csv(stage3 / "readout" / "readout_coupling_summary.csv")

    return Stage5InputContext(
        stage3_dir=str(stage3),
        stage4_dir=str(stage4),
        stage4_required_sbr=float(stage4_summary.get("required_signal_to_background_ratio") or 1.2),
        stage4_false_positive_rate=float(stage4_summary.get("false_positive_rate") or 0.0),
        stage4_max_shell_nuisance_correlation=float(stage4_summary.get("max_abs_shell_nuisance_correlation") or 0.0),
        stage4_recovery_fraction_at_max_sbr=float(stage4_summary.get("recovery_fraction_at_max_sbr") or 0.0),
        max_integrated_shell_energy_J=_max_abs(metric, "integrated_shell_energy_J", 1.0e-22),
        max_shell_pressure_Pa=_max_abs(metric, "pressure_Pa_mid", 1.0e-5),
        max_timing_bound_s=_max_abs(metric, "timing_bound_s", 0.0),
        max_readout_coupled_energy_J=_max_abs(metric, "readout_path_energy_coupling_J", 0.0),
        median_readout_source_fraction=_median(readout, "readout_source_fraction", 0.0),
        median_shell_channel_fraction=_median(readout, "shell_channel_fraction", 0.0),
        median_patch_to_casimir_ratio=max(_median(material, "patch_to_casimir_energy_ratio", 1.0), 1.0),
        median_casimir_to_material_ratio=max(_median(material, "casimir_to_material_rest_energy_ratio", 1.0e-27), 1.0e-30),
        median_patch_energy_J=_median(material, "patch_energy_J", 1.0e-20),
        median_capacitance_F=_median(material, "capacitance_F", 1.0e-16),
        median_material_mass_energy_J=_median(material, "material_mass_energy_J", 1.0e4),
    )


def default_readout_candidates() -> list[ReadoutCandidate]:
    return [
        ReadoutCandidate(
            candidate_id="central_timing_reference",
            claim_class="metric_proxy",
            observable_name="central transit timing perturbation",
            observable_unit="s",
            transduction_family="direct_metric_timing_reference",
            sensitivity_floor=1.0e-18,
            sensitivity_floor_unit="s rms",
            dominant_nuisances=("capacitance_shift", "waveguide_dispersion", "readout_circuit_artifact"),
            control_requirements=("matched control path", "EM-only schedule", "capacitance calibration"),
            allowed_claim="metric proxy only if amplitude, nuisance, and control gates pass",
            model_status="analytic_reference_closure",
            notes="Keeps the old direct readout interpretation in the ladder as a closure check.",
        ),
        ReadoutCandidate(
            candidate_id="force_gradient_mems",
            claim_class="casimir_boundary",
            observable_name="force-gradient frequency shift",
            observable_unit="N/m",
            transduction_family="mechanical_boundary_force",
            sensitivity_floor=1.0e-9,
            sensitivity_floor_unit="N/m rms",
            dominant_nuisances=("patch_potential", "surface_roughness", "thermal_drift", "vibration_alignment"),
            control_requirements=("dummy conductor", "far-field offset", "patch-potential map"),
            allowed_claim="Casimir boundary morphology if gates pass",
        ),
        ReadoutCandidate(
            candidate_id="differential_pressure_cell",
            claim_class="casimir_boundary",
            observable_name="paired-cell pressure contrast",
            observable_unit="Pa",
            transduction_family="differential_boundary_pressure",
            sensitivity_floor=1.0e-6,
            sensitivity_floor_unit="Pa rms",
            dominant_nuisances=("patch_potential", "membrane_stress_drift", "temperature_gradient"),
            control_requirements=("opposite shell-gap modulation", "matched dummy cell", "roughness prior"),
            allowed_claim="Casimir boundary morphology if common-mode controls pass",
        ),
        ReadoutCandidate(
            candidate_id="high_q_cavity_shift",
            claim_class="casimir_boundary",
            observable_name="cavity fractional frequency shift",
            observable_unit="fractional_delta_f",
            transduction_family="electromagnetic_mode_boundary_shift",
            sensitivity_floor=1.0e-11,
            sensitivity_floor_unit="fractional frequency rms",
            dominant_nuisances=("thermal_drift", "finite_conductivity", "waveguide_dispersion", "mode_mixing"),
            control_requirements=("mode-overlap calculation", "thermal expansion monitor", "dummy cavity"),
            allowed_claim="Casimir boundary or material-response morphology depending on loss controls",
        ),
        ReadoutCandidate(
            candidate_id="superconducting_resonator_shift",
            claim_class="casimir_boundary",
            observable_name="superconducting resonator phase/frequency shift",
            observable_unit="fractional_delta_f",
            transduction_family="superconducting_boundary_resonator",
            sensitivity_floor=1.0e-13,
            sensitivity_floor_unit="fractional frequency rms",
            dominant_nuisances=("material_response", "vortex_loss", "quasiparticle_loss", "thermal_drift"),
            control_requirements=("surface-loss model", "vortex control", "material-only resonator"),
            allowed_claim="Casimir boundary only if material/loss channels are separated",
        ),
        ReadoutCandidate(
            candidate_id="material_impedance_control",
            claim_class="material_response",
            observable_name="impedance/capacitance/material response",
            observable_unit="relative_response",
            transduction_family="ordinary_material_competitor_control",
            sensitivity_floor=1.0e-3,
            sensitivity_floor_unit="relative rms",
            dominant_nuisances=("material_response", "patch_potential", "capacitance_shift", "contact_loading"),
            control_requirements=("four-terminal calibration", "surface-potential map", "dummy readout path"),
            allowed_claim="Material-response/background calibration, not metric proxy",
            model_status="control_channel_not_shell_measurement",
            notes="Tracks ordinary material channels as first-class competitors.",
        ),
    ]


def select_candidates(candidate_ids: tuple[str, ...] | list[str] | None = None) -> list[ReadoutCandidate]:
    candidates = default_readout_candidates()
    if not candidate_ids:
        return candidates
    selected = set(candidate_ids)
    return [candidate for candidate in candidates if candidate.candidate_id in selected]


def _patch_penalty(context: Stage5InputContext, control_gain: float) -> float:
    return max(1.0, math.sqrt(context.median_patch_to_casimir_ratio) / max(control_gain, 1.0e-12))


def _material_penalty(context: Stage5InputContext, control_gain: float) -> float:
    exponent = min(8.0, max(1.0, -math.log10(context.median_casimir_to_material_ratio) / 5.0))
    return max(1.0, exponent / max(control_gain, 1.0e-12))


def _candidate_sbr(candidate: ReadoutCandidate, scenario: str, context: Stage5InputContext) -> tuple[float, float, str, str]:
    factors = SCENARIO_FACTORS[scenario]
    signal_gain = factors["signal_gain"]
    background_gain = factors["background_gain"]
    control_gain = factors["control_gain"]
    floor = max(candidate.sensitivity_floor, EPSILON)
    pressure = max(context.max_shell_pressure_Pa, EPSILON)
    energy = max(context.max_integrated_shell_energy_J, EPSILON)

    if candidate.candidate_id == "central_timing_reference":
        signal = context.max_timing_bound_s * max(context.median_readout_source_fraction, 1.0e-6) * signal_gain
        background = floor * background_gain
        sbr = signal / max(background, EPSILON)
        notes = "Stage 3 linearized timing bound times readout-source fraction over timing floor."
        return sbr, background, "readout_circuit_artifact", notes

    if candidate.candidate_id == "force_gradient_mems":
        effective_area_m2 = math.pi * (0.5e-6) ** 2
        gradient_length_m = 1.0e-6
        signal = pressure * effective_area_m2 / gradient_length_m * signal_gain
        background = floor * background_gain
        sbr = signal / max(background, EPSILON) / _patch_penalty(context, control_gain)
        notes = "Calibrated shell pressure times micron probe area over gradient length, penalized by patch scale."
        return sbr, background, "patch_potential", notes

    if candidate.candidate_id == "differential_pressure_cell":
        shell_contrast = 0.40
        common_mode_gain = 2.5 * control_gain
        signal = pressure * shell_contrast * signal_gain
        background = floor * background_gain
        sbr = signal / max(background, EPSILON) / max(1.0, _patch_penalty(context, common_mode_gain))
        notes = "Paired cell pressure contrast with common-mode rejection and patch-potential penalty."
        return sbr, background, "patch_potential", notes

    if candidate.candidate_id == "high_q_cavity_shift":
        stored_mode_energy_J = 1.0e-12
        mode_overlap = 2.5e-3
        signal = energy / stored_mode_energy_J * mode_overlap * signal_gain
        background = floor * background_gain
        loss_penalty = max(1.0, (1.0 + math.log10(context.median_patch_to_casimir_ratio)) / control_gain)
        sbr = signal / max(background, EPSILON) / loss_penalty
        notes = "Perturbative fractional mode shift from shell energy over stored mode energy with loss penalty."
        return sbr, background, "waveguide_dispersion", notes

    if candidate.candidate_id == "superconducting_resonator_shift":
        stored_mode_energy_J = 5.0e-13
        mode_overlap = 7.5e-4
        signal = energy / stored_mode_energy_J * mode_overlap * signal_gain
        background = floor * background_gain
        sbr = signal / max(background, EPSILON) / _material_penalty(context, control_gain)
        notes = "Superconducting frequency-shift scaling with lower readout floor and material-loss penalty."
        return sbr, background, "material_response", notes

    if candidate.candidate_id == "material_impedance_control":
        background = floor * background_gain
        notes = "Material control intentionally carries no Casimir shell amplitude in the gate."
        return 0.0, background, "material_response", notes

    return 0.0, floor * background_gain, "unknown", "No model registered for candidate."


def _safe_required_gain(stage4_required_sbr: float, predicted_sbr: float) -> float:
    return float(stage4_required_sbr / max(float(predicted_sbr), 1.0e-300))


def evaluate_candidate_transduction(
    candidate: ReadoutCandidate,
    context: Stage5InputContext,
    schedule: pd.DataFrame,
    shell_templates: Mapping[str, np.ndarray],
) -> list[TransductionResult]:
    rows: list[TransductionResult] = []
    for scenario in SCENARIO_FACTORS:
        template = np.asarray(shell_templates[candidate.candidate_id], dtype=float)
        predicted_sbr, background, dominant_nuisance, notes = _candidate_sbr(candidate, scenario, context)
        coefficient = float(predicted_sbr * background)
        for order, value in enumerate(template):
            step = str(schedule.loc[order, "schedule_step"])
            rows.append(
                TransductionResult(
                    candidate_id=candidate.candidate_id,
                    scenario=scenario,
                    schedule_step=step,
                    schedule_order=int(order),
                    shell_observable=float(coefficient * value),
                    shell_observable_unit=candidate.observable_unit,
                    background_observable_rms=float(background),
                    predicted_sbr=float(predicted_sbr),
                    required_gain_to_stage4_gate=_safe_required_gain(context.stage4_required_sbr, predicted_sbr),
                    claim_class=candidate.claim_class,
                    allowed_claim=candidate.allowed_claim,
                    dominant_nuisance=dominant_nuisance,
                    model_status=candidate.model_status,
                    model_provenance="analytic_stage5_first_pass_from_stage3_stage4_summaries",
                    optimism_level=scenario,
                    model_notes=notes,
                )
            )
    return rows

