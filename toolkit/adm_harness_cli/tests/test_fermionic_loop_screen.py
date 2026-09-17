import numpy as np
from numpy.testing import assert_allclose
from scipy.integrate import quad

from adm_harness.fermionic_loop_screen import (
    exterior_barrier_exponent, required_loop_radius, required_node_action, rotor_lab_fermi_bound,
)


def test_exterior_wkb_action_matches_independent_radial_quadrature():
    for E, m, R, width in ((3., 1., 100., 0.), (3., 1., 100., 2.), (1.2, 1., 30., 1.)):
        n, k = E*R, np.sqrt(E*E-m*m)
        expected = 2*quad(lambda r: np.sqrt(max(n*n/(r*r)-k*k, 0)), R+width,
                          n/k, epsabs=1e-10)[0]
        assert_allclose(exterior_barrier_exponent(E, m, R, width), expected, rtol=2e-12)


def test_thin_high_energy_limit_and_finite_core_reduce_barrier():
    for E in (10., 30., 100.):
        R = 1e5
        actual = exterior_barrier_exponent(E, 1., R)
        asymptotic = 2/3*R/(E*E)
        assert_allclose(actual, asymptotic, rtol=.0061)
        assert exterior_barrier_exponent(E, 1., R, .1) < actual
    assert exterior_barrier_exponent(3., 1., 100., 20.) == 0.
    assert np.isinf(exterior_barrier_exponent(.9, 1., 100.))


def test_radius_screen_respects_both_width_and_exponent_requirements():
    result = required_loop_radius(1., 4., yukawa=1., target_exponent=100.)
    assert result["core_over_loop_radius"] <= .01
    assert result["exterior_wkb_exponent"] >= 100*(1-2e-13)
    assert result["semiclassical_mode_number"] >= 100
    assert result["fermi_over_bulk_mass"] > 1


def test_replica_action_counts_each_counterrotating_axis():
    R, inventory, r0, x, copies = 2500., 19., 1/(12*np.pi), 1.068, 6
    action = required_node_action(R, inventory=inventory, replicas=copies)
    mass_per_copy = inventory*action/copies
    mu = mass_per_copy/(4*np.pi*r0)
    assert_allclose(x*r0*np.sqrt(mu), R, rtol=3e-16)
    assert_allclose(action, copies*required_node_action(R, inventory=inventory, replicas=1))


def test_rotor_forward_energy_matches_doppler_shift_and_encloses_domain():
    result = rotor_lab_fermi_bound()
    j, lam = result["spin"], result["proper_stretch"]
    assert_allclose(np.sqrt(2*np.pi)/lam*(1+j)/np.sqrt(1-j*j),
                    result["fermi_energy_over_sqrt_mu"], rtol=3e-16)
    h, w = np.meshgrid(np.linspace(1.08, 1.32, 200), np.linspace(-.0114, .0114, 151))
    spin = np.sqrt(h*h-w*w-1)
    assert np.max(np.sqrt(2*np.pi)*(1+spin)/(h+w)) <= result["fermi_energy_over_sqrt_mu"]*(1+1e-15)
    for radial_speed in (0., .004, .00905):
        gamma = 1/np.sqrt(1-radial_speed**2)
        x = h+w
        for heat in (0., .02, .05):
            j2 = 2*h*x/gamma-x*x-1-2*heat
            valid = j2 >= 0
            j = np.sqrt(np.maximum(j2, 0))
            energy = gamma*np.sqrt(2*np.pi)*(1+j)/x
            assert energy[valid].max() <= result["fermi_energy_over_sqrt_mu"]*(1+1e-15)


def test_radial_motion_uses_separate_energy_and_angular_momentum():
    E, m, R, width, v = 3., 1., 100., 1., .1
    n = E*R*np.sqrt(1-v*v)
    k = np.sqrt(E*E-m*m)
    expected = 2*quad(lambda r: np.sqrt(max(n*n/(r*r)-k*k, 0)), R+width,
                      n/k, epsabs=1e-10)[0]
    actual = exterior_barrier_exponent(E, m, R, width, mode_number=n)
    assert_allclose(actual, expected, rtol=2e-12)
    assert actual < exterior_barrier_exponent(E, m, R, width)
    Emax = rotor_lab_fermi_bound()["fermi_energy_over_sqrt_mu"]
    frozen = required_loop_radius(1., 4., yukawa=.3,
                                  lab_fermi_energy_over_sqrt_mu=Emax)
    moving = required_loop_radius(1., 4., yukawa=.3, radial_speed_bound=.00905,
                                  lab_fermi_energy_over_sqrt_mu=Emax)
    assert moving["required_radius_sqrt_mu"] > frozen["required_radius_sqrt_mu"]
    assert moving["exterior_wkb_exponent"] >= 100*(1-2e-12)
    R = moving["required_radius_sqrt_mu"]
    m, width = moving["bulk_mass_over_sqrt_mu"]*.99, moving["scalar_core_radius_sqrt_mu"]
    for E in np.linspace(.5*Emax, Emax, 50):
        for speed in (0., .004, .00905):
            assert exterior_barrier_exponent(E, m, R, width,
                mode_number=E*R*np.sqrt(1-speed*speed)) >= 100*(1-2e-12)
