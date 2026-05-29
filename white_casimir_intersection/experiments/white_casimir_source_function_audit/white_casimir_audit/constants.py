"""Physical constants and simple scale helpers for the White Casimir audit."""

from __future__ import annotations

from math import pi

HBAR_J_S = 1.054_571_817e-34
C_M_S = 299_792_458.0
G_M3_KG_S2 = 6.674_30e-11
UM_TO_M = 1.0e-6


def um_to_m(length_um: float) -> float:
    return float(length_um) * UM_TO_M


def parallel_plate_em_energy_density_J_m3(gap_um: float) -> float:
    """Ideal EM Casimir energy density between perfect parallel plates."""

    d_m = um_to_m(gap_um)
    return -(pi**2 * HBAR_J_S * C_M_S) / (720.0 * d_m**4)


def parallel_plate_scalar_dirichlet_energy_density_J_m3(gap_um: float) -> float:
    """Massless scalar Dirichlet plate energy density in 3+1 dimensions."""

    d_m = um_to_m(gap_um)
    return -(pi**2 * HBAR_J_S * C_M_S) / (1440.0 * d_m**4)
