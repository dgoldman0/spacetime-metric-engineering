from white_casimir_audit.constants import (
    parallel_plate_em_energy_density_J_m3,
    parallel_plate_scalar_dirichlet_energy_density_J_m3,
)


def test_parallel_plate_energy_density_scales_as_gap_to_minus_four():
    em_2 = abs(parallel_plate_em_energy_density_J_m3(2.0))
    em_4 = abs(parallel_plate_em_energy_density_J_m3(4.0))
    scalar_2 = abs(parallel_plate_scalar_dirichlet_energy_density_J_m3(2.0))
    scalar_4 = abs(parallel_plate_scalar_dirichlet_energy_density_J_m3(4.0))

    assert em_2 / em_4 == 16.0
    assert scalar_2 / scalar_4 == 16.0
