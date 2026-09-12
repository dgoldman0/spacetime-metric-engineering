import numpy as np
from numpy.testing import assert_allclose
from scipy.integrate import quad

from adm_harness.charged_capacitor import (
    condenser_parameters, electric_gap_energy, electrovacuum_jet,
    magnetic_cell_work, shell_potential_jet, shell_state,
    transverse_magnetic_moments,
)


def test_surface_density_and_pressure_match_single_shell_mass_formula():
    radius, rest_mass, charge = 2., .3, .5
    mass = rest_mass+(charge**2-rest_mass**2)/(2*radius)
    sigma, p = shell_state(radius, 0., 0., mass, charge)
    assert_allclose(4*np.pi*radius**2*sigma, rest_mass, rtol=1e-14)
    expected = (rest_mass**2-charge**2)/(16*np.pi*radius**2*(radius-rest_mass))
    assert_allclose(p, expected, rtol=1e-13)


def test_fixed_charge_potential_is_static_and_has_independent_curvature():
    r, mass, charge, eta = 1., .245, .3, .4
    sigma, p = shell_state(r, 0., 0., mass, charge)
    value, first, second = shell_potential_jet(r, 0., 0., mass, charge, eta)
    assert_allclose([value, first], 0., atol=4e-15)
    # Integrate conservation analytically for p(sigma)=p0+eta*(sigma-sigma0).
    constant = p-eta*sigma
    def potential(x):
        density = (sigma+constant/(1+eta))*(r/x)**(2*(1+eta))-constant/(1+eta)
        y = 4*np.pi*x*density
        f = electrovacuum_jet(x, mass, charge)[0]
        return (1+f)/2-y*y/4-(1-f)**2/(4*y*y)
    eps = 2e-4
    fd = (-potential(r+2*eps)+16*potential(r+eps)-30*potential(r)
          +16*potential(r-eps)-potential(r-2*eps))/(12*eps**2)
    assert_allclose(second, fd, atol=3e-8)


def test_uncharged_shell_agrees_with_published_critical_sound_slope():
    # Reyes et al., EPJC 82, 151 (2022), stability boundary following Eq. (39).
    for rest_mass in (.05, .3, .6):
        mass = rest_mass-rest_mass**2/2
        sigma, p = shell_state(1., 0., 0., mass, 0.)
        x = p/sigma
        eta = x*(8*x*x+8*x+3)/(2*(x+1))
        assert_allclose(shell_potential_jet(1., 0., 0., mass, 0., eta)[2], 0., atol=1e-13)


def test_both_condenser_shell_rest_masses_reconstruct_the_geometry():
    b, q, mi, fraction = 2., .3, .1, .02
    mu, mass, mo, fmin = condenser_parameters(b, q, mi, fraction)
    assert fmin > 0
    assert_allclose(shell_state(1., 0., 0., mu, q)[0]*4*np.pi, mi)
    assert_allclose(shell_state(b, mu, q, mass, 0.)[0]*4*np.pi*b*b, mo)
    for args in ((1., 0., 0., mu, q), (b, mu, q, mass, 0.)):
        assert_allclose(shell_potential_jet(*args, .5)[:2], 0., atol=1e-13)


def test_proper_field_energy_matches_adaptive_integral_and_flat_limit():
    b, mu, q = 3., .1, .2
    proper, coordinate = electric_gap_energy(1., b, mu, q)
    independent = quad(lambda r: q*q/(2*r*r*np.sqrt(1-2*mu/r+q*q/r**2)), 1., b)[0]
    assert_allclose(proper, independent, rtol=1e-13)
    weak, coord = electric_gap_energy(1., b, 1e-8, 1e-5)
    assert_allclose(weak, coord, rtol=1e-8)
    assert_allclose(coordinate, q*q/2*(1-1/b))


def test_transverse_magnetic_tensor_is_trace_free_and_boosted_correctly():
    for v in (0., .2, -.5):
        rho, pr, j, pt = transverse_magnetic_moments(2., v)
        assert_allclose(-rho+pr+2*pt, 0.)
        assert_allclose((rho-2*v*j+v*v*pr)/(1-v*v), 2.)
        assert rho >= abs(j)


def test_frozen_transverse_flux_has_pure_radial_compression_work():
    ell = np.array([4., 2., 1.])[:, None]
    radius = np.array([2., 3., 2.])[:, None]
    density = 5/(ell*radius)**2
    port, mechanical, energy = magnetic_cell_work(density, ell, radius)
    assert_allclose(port, 0., atol=1e-14)
    assert_allclose(mechanical, np.diff(energy, axis=0))
    assert_allclose(energy[:, 0], [1.25, 2.5, 5.])


def test_controlled_transverse_field_counts_external_and_mechanical_work():
    density = np.array([.2, .3, .1])[:, None]
    ell = np.array([4., 2., 1.])[:, None]
    radius = np.array([2., 3., 2.])[:, None]
    port, mechanical, energy = magnetic_cell_work(density, ell, radius)
    assert_allclose(port+mechanical, np.diff(energy, axis=0), atol=1e-14)
    assert np.any(abs(port) > 0)
