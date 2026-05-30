"""Small linearized metric/timing scale estimates for Stage 3."""

from __future__ import annotations

from .constants import C_M_S, G_M3_KG_S2, um_to_m


def gravitational_radius_m(energy_J: float) -> float:
    """Return ``2 G E / c^4`` using the magnitude of ``energy_J``."""

    return 2.0 * G_M3_KG_S2 * abs(float(energy_J)) / (C_M_S**4)


def estimate_timing_bound(
    energy_J: float,
    path_length_um: float,
    coupling_fraction: float = 1.0,
) -> dict[str, float | str]:
    """Return a conservative linearized timing-scale bound.

    This is an order-of-magnitude comparator, not a transport prediction. The
    bound uses the gravitational radius associated with the coupled energy and
    reports the corresponding light-time scale.
    """

    coupled_energy_J = abs(float(energy_J)) * max(float(coupling_fraction), 0.0)
    r_g_m = gravitational_radius_m(coupled_energy_J)
    path_length_m = um_to_m(path_length_um)
    return {
        "estimate_status": "linearized_metric_scale_bound_not_transport_prediction",
        "path_length_um": float(path_length_um),
        "coupling_fraction": float(coupling_fraction),
        "coupled_energy_J": coupled_energy_J,
        "gravitational_radius_m": r_g_m,
        "path_length_m": path_length_m,
        "fractional_path_scale": r_g_m / max(path_length_m, 1.0e-300),
        "timing_bound_s": r_g_m / C_M_S,
    }
