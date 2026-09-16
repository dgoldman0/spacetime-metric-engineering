"""Independent field, thermodynamic and support-component checks."""
import numpy as np
import pytest
from numpy.testing import assert_allclose
from scipy.integrate import simpson

from adm_harness.current_carrying_wall import (
    WallParameters, component_feasibility, necessary_wall_gaps, potential,
    profile_observables, solve_profile, stress_components,
)
from adm_harness.magnetic_load_balance import support_cone


def test_potential_vacuum_constraint_and_linear_carrier_threshold():
    with pytest.raises(ValueError):
        WallParameters(coupling=1., mass_squared=.1)
    for f in (.35, .4, .45, .5):
        p = WallParameters(coupling=f, mass_squared=2*f-.6)
        phi, sigma = np.meshgrid(np.linspace(-2, 2, 201), np.linspace(0, 2, 151))
        assert np.min(potential(phi, sigma, p)) >= -1e-14
        # The analytic ground-state wavefunction is sech(a*n)**ell.
        n = np.linspace(-12, 12, 2001)
        a, ell = p.inverse_width, p.carrier_index
        wave = 1/np.cosh(a*n)**ell
        second = a*a*ell*(ell*np.tanh(a*n)**2-1/np.cosh(a*n)**2)*wave
        operator = -second+(p.mass_squared-2*f/np.cosh(a*n)**2)*wave
        assert_allclose(operator, -p.linear_quench_w*wave, atol=2e-15)


def test_stress_matches_energy_under_independent_spatial_dilations():
    p = WallParameters()
    n = np.linspace(-15, 15, 4001)
    th, sech = np.tanh(.35*n), 1/np.cosh(.35*n)
    fields = np.array([th, .35*sech**2, .7*sech, -.245*sech*th])
    omega, kz, kt = .23, .19, .41
    integrated = simpson(stress_components(fields, p, omega=omega, axial_k=kz, hoop_k=kt), x=n)
    normal = .5*(fields[1]**2+fields[3]**2)
    temporal, axial, hoop = [.5*k*k*fields[2]**2 for k in (omega, kz, kt)]
    V = potential(fields[0], fields[2], p)

    def energy(lengths):
        z, theta, normal_length = lengths
        volume = np.prod(lengths)
        # Fix the total Noether charge while dilating; frequency changes
        # inversely with the volume integral of the condensate squared.
        return volume*simpson(normal/normal_length**2+axial/z**2
                              + hoop/theta**2+temporal/volume**2+V, x=n)

    for i, pressure in enumerate(integrated[1:]):
        left, right = np.ones(3), np.ones(3)
        left[i] -= 1e-5
        right[i] += 1e-5
        assert_allclose(-(energy(right)-energy(left))/2e-5, pressure, atol=1e-9)


def test_bare_wall_agrees_with_analytic_kink_and_tension():
    p = WallParameters(mass_squared=2.)
    solution = solve_profile(p, .1, tolerance=1e-9)
    n = np.linspace(0, 30, 501)
    assert_allclose(solution.sol(n)[0], p.vacuum*np.tanh(p.inverse_width*n), atol=2e-9)
    assert_allclose(solution.sol(n)[2], 0., atol=1e-14)
    row = profile_observables(solution, p, .1)
    assert_allclose([row["energy"], -row["axial_pressure"], -row["hoop_pressure"]],
                    p.bare_tension, atol=2e-9)


def test_populated_wall_satisfies_first_integral_and_envelope_identity():
    p = WallParameters()
    w, step = .04, 5e-4
    central = solve_profile(p, w, tolerance=1e-9)
    row = profile_observables(central, p, w)
    low = profile_observables(solve_profile(p, w-step, previous=central, tolerance=1e-9), p, w-step)
    high = profile_observables(solve_profile(p, w+step, previous=central, tolerance=1e-9), p, w+step)
    assert row["center_condensate"] > .5
    assert row["max_normal_pressure"] < 1e-9
    assert_allclose(row["axial_pressure"], -row["energy"], atol=1e-12)
    assert_allclose(row["energy"]+row["hoop_pressure"], w*row["condensate_integral"], atol=1e-12)
    assert_allclose((high["energy"]-low["energy"])/(2*step),
                    row["condensate_integral"]/2, rtol=3e-6)


def test_canonical_joint_identity_for_general_phase_gradients():
    rng = np.random.default_rng(330)
    fields = rng.normal(size=(4, 70))
    p = WallParameters()
    stress = stress_components(fields, p, omega=.8, axial_k=.7, hoop_k=.3)
    rho, z, theta, normal = stress
    assert_allclose(rho-z+theta-normal,
                    2*.3**2*fields[2]**2+2*potential(fields[0], fields[2], p), atol=4e-15)


def test_plane_stress_elimination_against_full_component_program():
    rng = np.random.default_rng(866)
    successes = 0
    for _ in range(60):
        target = np.r_[rng.uniform(.1, 4), rng.uniform(-2, 2, 2)]
        floor, hoop = rng.uniform(0, .5, 2)
        facets = support_cone(*target, floor)["facets"]
        gap = necessary_wall_gaps(facets, hoop)["hoop_current_plane_stress"]
        result = component_feasibility(target, floor, hoop, law="hoop_current_plane_stress")
        assert result.success == (gap <= 0)
        successes += result.success
    assert 0 < successes < 60


def test_positive_gaps_reject_even_with_normal_compression():
    rng = np.random.default_rng(861)
    rejections = dict(canonical_joint_stress=0, hoop_current_normal_compression=0)
    for _ in range(50):
        target = np.r_[rng.uniform(.1, 4), rng.uniform(-2, 2, 2)]
        floor, hoop = rng.uniform(0, .5, 2)
        facets = support_cone(*target, floor)["facets"]
        gaps = necessary_wall_gaps(facets, hoop)
        for law in rejections:
            if gaps[law] > 1e-10:
                assert component_feasibility(target, floor, hoop, law=law).status == 2
                rejections[law] += 1
    assert min(rejections.values()) > 0
