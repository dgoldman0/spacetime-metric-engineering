"""Ordinary material and EM competitor estimates for the White audit."""

from __future__ import annotations

from math import log, pi

from .constants import C_M_S, um_to_m

EPS0_F_M = 8.854_187_8128e-12

MATERIAL_DENSITIES_KG_M3 = {
    "gold": 19_300.0,
    "copper": 8_960.0,
    "silicon": 2_330.0,
}


def sphere_volume_m3(diameter_um: float) -> float:
    radius_m = 0.5 * um_to_m(diameter_um)
    return (4.0 / 3.0) * pi * radius_m**3


def cylinder_wall_volume_m3(
    cylinder_diameter_um: float,
    wall_thickness_um: float,
    length_um: float,
) -> float:
    outer_m = 0.5 * um_to_m(cylinder_diameter_um)
    inner_m = max(outer_m - um_to_m(wall_thickness_um), 0.0)
    return pi * (outer_m * outer_m - inner_m * inner_m) * um_to_m(length_um)


def coaxial_capacitance_F(length_um: float, inner_radius_um: float, outer_radius_um: float) -> float:
    inner_m = max(um_to_m(inner_radius_um), 1.0e-12)
    outer_m = max(um_to_m(outer_radius_um), inner_m * 1.000001)
    return 2.0 * pi * EPS0_F_M * um_to_m(length_um) / max(log(outer_m / inner_m), 1.0e-12)


def estimate_em_competitors(
    casimir_energy_J: float,
    sphere_diameter_um: float,
    cylinder_diameter_um: float,
    cylinder_length_um: float,
    wall_thickness_um: float,
    readout_radius_um: float = 0.05,
    patch_potentials_V: tuple[float, ...] = (0.01, 0.10),
) -> list[dict[str, float | str | bool]]:
    """Estimate ordinary material/EM scales that can dominate the readout."""

    sphere_v = sphere_volume_m3(sphere_diameter_um)
    wall_v = cylinder_wall_volume_m3(cylinder_diameter_um, wall_thickness_um, cylinder_length_um)
    outer_radius_um = 0.5 * cylinder_diameter_um
    capacitance_F = coaxial_capacitance_F(cylinder_length_um, readout_radius_um, outer_radius_um)
    waveguide_cutoff_hz = 1.841 * C_M_S / (2.0 * pi * max(um_to_m(readout_radius_um), 1.0e-12))
    rows: list[dict[str, float | str | bool]] = []
    for material, density in MATERIAL_DENSITIES_KG_M3.items():
        mass_energy_J = (sphere_v + wall_v) * density * C_M_S**2
        for patch_v in patch_potentials_V:
            patch_energy_J = 0.5 * capacitance_F * patch_v * patch_v
            rows.append(
                {
                    "material": material,
                    "conductor_density_kg_m3": density,
                    "sphere_volume_m3": sphere_v,
                    "cylinder_wall_volume_m3": wall_v,
                    "material_mass_energy_J": mass_energy_J,
                    "casimir_energy_J": float(casimir_energy_J),
                    "casimir_to_material_rest_energy_ratio": abs(float(casimir_energy_J))
                    / max(mass_energy_J, 1.0e-300),
                    "readout_radius_um": float(readout_radius_um),
                    "capacitance_F": capacitance_F,
                    "patch_potential_V": float(patch_v),
                    "patch_energy_J": patch_energy_J,
                    "patch_to_casimir_energy_ratio": patch_energy_J / max(abs(float(casimir_energy_J)), 1.0e-300),
                    "waveguide_cutoff_hz": waveguide_cutoff_hz,
                    "patch_potential_flag": True,
                    "contact_loading_warning": True,
                    "open_bore_vs_conductor_distinction": "accounting_mask_only_until_modeled_bore_run",
                }
            )
    return rows
