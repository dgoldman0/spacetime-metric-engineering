import numpy as np
import pytest
from numpy.testing import assert_allclose

from adm_harness.fermionic_string_material import (
    critical_tension_factor, energy_terms, fermion_duty, profile_diagnostics,
    radius_at_fixed_tension, solve_vortex,
)


@pytest.fixture(scope="module")
def bps_profile():
    return solve_vortex(1., mesh_points=600, tolerance=2e-8)


def test_critical_vortex_saturates_topological_energy_and_first_order_equations(bps_profile):
    diagnostic = profile_diagnostics(bps_profile)
    assert_allclose(diagnostic["tension_factor_B"], 1., atol=3e-8)
    assert diagnostic["bps_squares_integral"] < 1e-12
    assert diagnostic["square_completion_identity_error"] < 1e-8
    assert diagnostic["virial_relative_to_total"] < 1e-8


def test_noncritical_vortex_is_stationary_under_independent_field_variations():
    profile = solve_vortex(.1, mesh_points=700, tolerance=2e-8)
    diagnostic = profile_diagnostics(profile)
    assert diagnostic["virial_relative_to_total"] < 1e-8
    assert .5 < diagnostic["tension_factor_B"] < .8
    # Smooth variations have compact numerical support away from both cuts.
    t = np.linspace(-4., 4., 12001)
    y = profile.evaluate_log(t)
    bump = np.exp(-2*(t-.5)**2)
    bump_prime = -4*(t-.5)*bump
    step = 1e-5
    for component in (0, 2):
        variation = np.zeros_like(y)
        variation[component] = bump
        variation[component+1] = bump_prime
        plus = np.trapezoid(energy_terms(t, y+step*variation, .1).sum(axis=0), t)
        minus = np.trapezoid(energy_terms(t, y-step*variation, .1).sum(axis=0), t)
        assert abs((plus-minus)/(2*step)) < 2e-7
    magnetic = diagnostic["energy_contributions"]["magnetic"]
    potential = diagnostic["energy_contributions"]["potential"]
    # The two gradient terms are invariant under dilation in two dimensions.
    assert abs(-2*magnetic+2*potential) < 2e-8


def test_small_beta_retains_a_finite_profile_with_separated_scalar_and_flux_widths(bps_profile):
    profile = bps_profile
    for beta in (.1, .01, .001, .0001):
        profile = solve_vortex(beta, previous=profile, tolerance=2e-7)
    diagnostic = profile_diagnostics(profile)
    assert .2 < diagnostic["tension_factor_B"] < .3
    assert diagnostic["scalar_radius_rho"]["0.9"] > 8*diagnostic["enclosed_flux_radius_rho"]["0.9"]
    assert diagnostic["virial_relative_to_total"] < 2e-7
    assert diagnostic["gauss8_gauss16_difference"] < 1e-10


def test_tiny_beta_completion_resolves_the_energy_after_large_square_cancellation(bps_profile):
    profile = bps_profile
    for exponent in range(1, 13):
        profile = solve_vortex(10.**-exponent, previous=profile)
    profile = solve_vortex(1e-12, mesh_points=1200, tolerance=2e-8,
        inner_radius=1e-6, outer_tail=30., previous=profile)
    diagnostic = profile_diagnostics(profile)
    assert_allclose(diagnostic["tension_factor_B"], .08329151381, atol=2e-9)
    assert diagnostic["bps_squares_integral"] > 1e9
    assert diagnostic["square_completion_identity_error"] < 2e-10
    assert diagnostic["topological_derivative_integral_error"] < 2e-10
    assert diagnostic["virial_relative_to_total"] < 2e-8
    assert diagnostic["scalar_radius_rho"]["0.9"] > 10000*diagnostic["enclosed_flux_radius_rho"]["0.9"]
    assert diagnostic["tension_factor_B"] < critical_tension_factor(1.17, .3, .1)
    assert diagnostic["tension_factor_B"] > critical_tension_factor(1., .3, .1)


def test_carrier_rectangle_uses_the_selected_branch_normalization():
    for normalization, expected in (("canonical_two_branches", .0985608),
                                     ("printed_ringeval_two_branches", .1971216)):
        B = critical_tension_factor(1.17, .3, .1, normalization=normalization)
        assert_allclose(B, expected, rtol=2e-15)
        screen = fermion_duty(B, 1.17, escape_ratio=.3, normalization=normalization)
        assert_allclose(screen["yukawa_loop_size_g2_over_16pi2"], .1, rtol=2e-15)
        above = fermion_duty(1.01*B, 1.17, escape_ratio=.3, normalization=normalization)
        assert above["yukawa_loop_size_g2_over_16pi2"] > .1


def test_fixed_tension_width_preserves_physical_length_under_eta_rescaling():
    B, rho, e = .0985608, 59372.88692, .3
    for eta in (.01, 1., 100.):
        mu = np.pi*eta*eta*B
        physical_radius = rho/(e*eta)
        assert_allclose(radius_at_fixed_tension(rho, B, gauge_coupling=e),
                        physical_radius*np.sqrt(mu), rtol=2e-15)


def test_canonical_two_branch_counting_reproduces_rigid_energy_and_tradeoff():
    B, eta, reference_length = .4, 2., 7.
    mu = np.pi*eta*eta*B
    N = reference_length*np.sqrt(mu/(2*np.pi))
    for stretch in (1., 1.17, 2.3349):
        screen = fermion_duty(B, stretch, escape_ratio=.3, gauge_coupling=.2, beta=.01)
        length = reference_length*stretch
        kf = 2*np.pi*N/length
        # Integrate the occupied momenta directly, one chiral state per dk/2pi.
        modes = np.linspace(0., kf, 10001)
        carrier_density = 2*np.trapezoid(modes, modes)/(2*np.pi)
        expected_energy = mu*reference_length*(stretch+1/stretch)
        assert_allclose((mu+carrier_density)*length, expected_energy, rtol=1e-13)
        assert_allclose(kf/eta, screen["fermi_momentum_over_eta"], rtol=1e-13)
        assert_allclose(screen["escape_ratio_squared_times_yukawa_loop_size"],
                        B/(8*stretch*stretch), rtol=1e-13)
        printed = fermion_duty(B, stretch, normalization="printed_ringeval_two_branches")
        assert_allclose(printed["fermi_momentum_over_eta"]*np.sqrt(2), kf/eta)


def test_invalid_inputs_are_rejected():
    for beta in (0., -1., np.nan):
        with pytest.raises(ValueError):
            solve_vortex(beta)
    with pytest.raises(ValueError):
        fermion_duty(1., 1., normalization="invented_extra_spin_degeneracy")
    with pytest.raises(ValueError):
        critical_tension_factor(1.17, 0., .1)
    with pytest.raises(ValueError):
        radius_at_fixed_tension(1., 1., gauge_coupling=0.)
