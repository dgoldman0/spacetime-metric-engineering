import numpy as np
from numpy.testing import assert_allclose
from scipy.integrate import quad

from adm_harness.fermionic_string_material import solve_vortex
from adm_harness.neutral_fermionic_hosts import (
    collision_pair_fraction, dirac_matrices, flavor_screen, mode_bilinears,
    normalized_zero_mode, transverse_dirac_residual, zero_mode_spinor,
)


def test_dirac_clifford_algebra_and_chiral_velocities():
    beta, alpha, gamma5 = dirac_matrices()
    gamma = [beta, *(beta@a for a in alpha)]
    metric = [1., -1., -1., -1.]
    for i, left in enumerate(gamma):
        for j, right in enumerate(gamma):
            assert_allclose(left@right+right@left, 2*metric[i]*np.eye(4) if i == j else 0)
    assert_allclose(gamma5, 1j*gamma[0]@gamma[1]@gamma[2]@gamma[3])
    for species in (-1, 1):
        psi = zero_mode_spinor(species)
        assert_allclose(alpha[2]@psi, -species*psi)


def test_four_component_hamiltonian_and_local_sources_for_both_species():
    rng = np.random.default_rng(94372)
    for _ in range(120):
        radius, angle, f, a, mass = rng.uniform(.02, 10), rng.uniform(0, 2*np.pi), rng.random(), rng.random(), rng.uniform(.1, 3)
        for species in (-1, 1):
            residual = transverse_dirac_residual(radius, angle, f, a, mass, species=species)
            assert abs(residual).max() < 1e-13
            bilinear = mode_bilinears(angle=angle, amplitude=rng.uniform(.1, 3), species=species)
            assert_allclose(bilinear["gauge_current"], 0, atol=1e-14)
            assert bilinear["scalar_amplitude_source"] == bilinear["scalar_phase_source"] == 0
    # Gauge invariance and gauge/gravitational anomaly sums use the actual
    # left/right charges, independently of the spinor matrix projection.
    charges = np.array([[.5, -.5], [-.5, .5]])
    assert_allclose(charges[:, 0]-charges[:, 1], [1., -1.])
    assert np.sum(charges[:, 0]**3-charges[:, 1]**3) == 0
    assert np.sum(charges[:, 0]-charges[:, 1]) == 0
    assert_allclose(charges[:, 0]**2-charges[:, 1]**2, 0)


def test_normalized_profile_and_independent_radial_derivative():
    profile = solve_vortex(1., tolerance=2e-8, inner_radius=1e-6, outer_minimum=50.)
    mode = normalized_zero_mode(profile, mass_ratio=.7)
    refined = normalized_zero_mode(profile, mass_ratio=.7, order=24)
    assert_allclose(mode["unnormalized_probability"], refined["unnormalized_probability"], rtol=2e-11)
    rho, F = np.exp(mode["log_rho"]), mode["radial_amplitude"]
    # A fifth-order local polynomial differentiates the computed normalized
    # profile without substituting its first-order ODE.
    for index in np.linspace(30, len(rho)-31, 35).astype(int):
        ids = np.arange(index-3, index+4)
        scaled = (rho[ids]-rho[index])/rho[index]
        coefficient = np.polynomial.polynomial.polyfit(scaled, F[ids], 6)
        derivative = coefficient[1]/rho[index]
        f, _, a, _ = profile.state[:, index]
        residual = transverse_dirac_residual(rho[index], .63, f, a, .7,
                    amplitude=F[index], radial_derivative=derivative)
        assert abs(residual).max() < 2e-7
    assert mode["exterior_probability_fraction"] < 1e-20


def test_collision_phase_space_matches_independent_pair_integral():
    for ratio in (.4, 1., 1.1, 2., 6.):
        a = 1/ratio**2
        expected = quad(lambda x: max(0., 1-a/x), max(a, 1e-8), 1)[0] if a < 1 else 0.
        assert_allclose(collision_pair_fraction(ratio), expected, atol=2e-15)


def test_flavor_count_preserves_elastic_energy_and_counts_collective_couplings():
    result = flavor_screen(1., pair_flavors=70, yukawa=.5, gauge_coupling=.5)
    kf = result["proper_fermi_over_bulk_mass"]*.5
    mu = np.pi
    assert_allclose(70*kf*kf/(2*np.pi), mu/result["proper_stretch"]**2)
    assert result["two_bulk_equal_mass_channel_kinematically_closed"]
    assert result["unit_coefficient_collective_yukawa_loop"] > .2
    assert flavor_screen(1.)["opposite_branch_open_pair_fraction"] > .7
