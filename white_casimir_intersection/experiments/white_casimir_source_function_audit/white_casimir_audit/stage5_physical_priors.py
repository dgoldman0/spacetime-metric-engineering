"""Physical-prior grids for Stage 5 closeout readout backends."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PressurePrior:
    case_id: str
    shell_gap_modulation: float
    effective_area_m2: float
    common_mode_rejection: float
    pressure_floor_Pa: float
    patch_residual_fraction: float
    roughness_fraction: float
    membrane_drift_Pa: float
    thermal_drift_Pa: float
    control_status: str


@dataclass(frozen=True)
class CavityPrior:
    case_id: str
    mode_overlap: float
    stored_energy_J: float
    frequency_floor_fraction: float
    finite_conductivity_fraction: float
    thermal_fraction: float
    waveguide_fraction: float
    mode_mixing_fraction: float
    loss_channel_fraction: float
    control_status: str


@dataclass(frozen=True)
class SuperconductingPrior:
    case_id: str
    mode_overlap: float
    stored_energy_J: float
    frequency_floor_fraction: float
    kinetic_inductance_fraction: float
    surface_loss_fraction: float
    vortex_fraction: float
    quasiparticle_fraction: float
    thermal_fraction: float
    material_control_fraction: float
    control_status: str


def pressure_priors() -> tuple[PressurePrior, ...]:
    area = 3.0e-12
    return (
        PressurePrior("pressure_conservative_patchy", 0.18, area, 6.0, 2.0e-6, 0.40, 0.25, 1.2e-6, 8.0e-7, "patch_map_required"),
        PressurePrior("pressure_conservative_balanced", 0.22, area, 10.0, 1.5e-6, 0.25, 0.20, 8.0e-7, 5.0e-7, "dummy_cell_required"),
        PressurePrior("pressure_conservative_quiet", 0.28, area, 18.0, 1.0e-6, 0.18, 0.15, 5.0e-7, 3.0e-7, "roughness_prior_required"),
        PressurePrior("pressure_nominal_patchy", 0.34, area, 30.0, 8.0e-7, 0.14, 0.10, 3.0e-7, 2.0e-7, "common_mode_controls_declared"),
        PressurePrior("pressure_nominal_balanced", 0.42, area, 55.0, 6.0e-7, 0.08, 0.08, 2.0e-7, 1.4e-7, "common_mode_controls_declared"),
        PressurePrior("pressure_nominal_quiet", 0.50, area, 85.0, 4.0e-7, 0.05, 0.06, 1.5e-7, 1.0e-7, "common_mode_controls_declared"),
        PressurePrior("pressure_optimistic_patchy", 0.58, area, 120.0, 3.0e-7, 0.04, 0.05, 1.0e-7, 8.0e-8, "strong_controls_assumed"),
        PressurePrior("pressure_optimistic_balanced", 0.68, area, 180.0, 2.0e-7, 0.025, 0.035, 8.0e-8, 6.0e-8, "strong_controls_assumed"),
        PressurePrior("pressure_optimistic_quiet", 0.78, area, 250.0, 1.5e-7, 0.015, 0.025, 5.0e-8, 4.0e-8, "strong_controls_assumed"),
    )


def cavity_priors() -> tuple[CavityPrior, ...]:
    return (
        CavityPrior("cavity_conservative_lossy", 3.0e-4, 5.0e-12, 3.0e-11, 0.45, 0.30, 0.40, 0.25, 0.50, "mode_solver_required"),
        CavityPrior("cavity_conservative_matched", 6.0e-4, 3.0e-12, 2.0e-11, 0.30, 0.22, 0.28, 0.18, 0.35, "thermal_monitor_required"),
        CavityPrior("cavity_conservative_clean", 1.0e-3, 2.0e-12, 1.5e-11, 0.22, 0.18, 0.20, 0.12, 0.25, "dummy_cavity_required"),
        CavityPrior("cavity_nominal_lossy", 1.6e-3, 1.5e-12, 1.0e-11, 0.16, 0.12, 0.16, 0.08, 0.18, "mode_overlap_declared"),
        CavityPrior("cavity_nominal_matched", 2.5e-3, 1.0e-12, 7.0e-12, 0.10, 0.08, 0.10, 0.05, 0.12, "mode_overlap_declared"),
        CavityPrior("cavity_nominal_clean", 4.0e-3, 8.0e-13, 5.0e-12, 0.07, 0.06, 0.07, 0.035, 0.08, "mode_overlap_declared"),
        CavityPrior("cavity_optimistic_lossy", 6.0e-3, 6.0e-13, 3.0e-12, 0.05, 0.04, 0.05, 0.025, 0.06, "strong_mode_control_assumed"),
        CavityPrior("cavity_optimistic_matched", 8.0e-3, 4.0e-13, 2.0e-12, 0.035, 0.03, 0.035, 0.018, 0.04, "strong_mode_control_assumed"),
        CavityPrior("cavity_optimistic_clean", 1.2e-2, 3.0e-13, 1.5e-12, 0.025, 0.02, 0.025, 0.012, 0.025, "strong_mode_control_assumed"),
    )


def superconducting_priors() -> tuple[SuperconductingPrior, ...]:
    return (
        SuperconductingPrior("sc_conservative_lossy", 2.0e-4, 3.0e-13, 5.0e-13, 0.35, 0.70, 0.55, 0.45, 0.30, 0.70, "surface_loss_model_required"),
        SuperconductingPrior("sc_conservative_balanced", 4.0e-4, 2.5e-13, 3.0e-13, 0.25, 0.50, 0.35, 0.30, 0.22, 0.50, "vortex_control_required"),
        SuperconductingPrior("sc_conservative_clean", 7.0e-4, 2.0e-13, 2.0e-13, 0.18, 0.35, 0.22, 0.20, 0.15, 0.35, "material_resonator_required"),
        SuperconductingPrior("sc_nominal_lossy", 1.0e-3, 1.5e-13, 1.4e-13, 0.12, 0.25, 0.16, 0.14, 0.10, 0.24, "loss_controls_declared"),
        SuperconductingPrior("sc_nominal_balanced", 1.6e-3, 1.0e-13, 1.0e-13, 0.08, 0.15, 0.10, 0.09, 0.07, 0.16, "loss_controls_declared"),
        SuperconductingPrior("sc_nominal_clean", 2.4e-3, 8.0e-14, 7.0e-14, 0.05, 0.10, 0.07, 0.06, 0.05, 0.10, "loss_controls_declared"),
        SuperconductingPrior("sc_optimistic_lossy", 3.5e-3, 6.0e-14, 5.0e-14, 0.035, 0.07, 0.045, 0.04, 0.035, 0.07, "strong_loss_control_assumed"),
        SuperconductingPrior("sc_optimistic_balanced", 5.0e-3, 5.0e-14, 3.5e-14, 0.025, 0.045, 0.030, 0.025, 0.025, 0.045, "strong_loss_control_assumed"),
        SuperconductingPrior("sc_optimistic_clean", 7.5e-3, 4.0e-14, 2.5e-14, 0.018, 0.030, 0.020, 0.018, 0.018, 0.030, "strong_loss_control_assumed"),
    )

