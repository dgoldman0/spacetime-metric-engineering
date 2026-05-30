"""Representative Alcubierre source-demand scale estimates.

The functions in this module are deliberately scale estimates. They are not a
full Alcubierre stress-tensor reconstruction; they provide a transparent local
gradient-demand comparator for calibrated Casimir source brackets.
"""

from __future__ import annotations

from math import pi, sqrt

from .constants import C_M_S, G_M3_KG_S2, um_to_m


def target_energy_density_J_m3(speed_parameter: float, delta_um: float) -> float:
    """Return the negative Eulerian energy-density demand scale.

    The local estimate is

    rho ~ -c^4 v^2 / (32 pi G Delta^2).
    """

    if delta_um <= 0.0:
        raise ValueError("delta_um must be positive")
    v = float(speed_parameter)
    delta_m = um_to_m(delta_um)
    return -((C_M_S**4) / (32.0 * pi * G_M3_KG_S2)) * (v * v) / (delta_m * delta_m)


def equivalent_speed_parameter(abs_energy_density_J_m3: float, delta_um: float) -> float:
    """Invert the demand estimate for the speed parameter."""

    if delta_um <= 0.0:
        raise ValueError("delta_um must be positive")
    rho = abs(float(abs_energy_density_J_m3))
    delta_m = um_to_m(delta_um)
    return sqrt(rho * 32.0 * pi * G_M3_KG_S2 * delta_m * delta_m / (C_M_S**4))


def build_target_grid(
    casimir_energy_density_J_m3: float,
    material_factor: float,
    speeds: tuple[float, ...] = (1.0e-9, 1.0e-6, 1.0e-3, 1.0),
    delta_um_values: tuple[float, ...] = (0.75, 1.0, 1.5, 2.0),
    calibration_family: str = "unspecified",
) -> list[dict[str, float | str]]:
    """Build source-demand comparison rows for one calibrated bracket."""

    rho_casimir = float(casimir_energy_density_J_m3) * float(material_factor)
    rows: list[dict[str, float | str]] = []
    for delta_um in delta_um_values:
        v_equiv = equivalent_speed_parameter(rho_casimir, delta_um)
        for speed in speeds:
            rho_target = target_energy_density_J_m3(speed, delta_um)
            rows.append(
                {
                    "calibration_family": calibration_family,
                    "material_factor": float(material_factor),
                    "target_delta_um": float(delta_um),
                    "speed_parameter": float(speed),
                    "rho_casimir_J_m3": rho_casimir,
                    "rho_target_J_m3": rho_target,
                    "source_demand_ratio": abs(rho_casimir) / max(abs(rho_target), 1.0e-300),
                    "v_equivalent": v_equiv,
                }
            )
    return rows
