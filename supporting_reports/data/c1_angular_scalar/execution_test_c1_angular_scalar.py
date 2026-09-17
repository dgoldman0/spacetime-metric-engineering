import numpy as np
import pytest

from adm_harness.c1_angular_scalar import (
    cylinder_tensor, finite_element_problem, lowest_modes, mode_potential,
)


class Cylinder:
    coordinate = np.linspace(-2., 2., 1001)

    def __init__(self, clock=1., conformal_scale=0.):
        self.clock, self.conformal_scale = clock, conformal_scale

    def jets(self, x):
        x = np.asarray(x, float)
        k = self.conformal_scale
        omega = np.exp(k*x*x)
        return (2.*omega, self.clock*omega, omega, 4.*k*x,
                np.full_like(x, 4.*k)/omega, 2.*k*x/omega,
                2.*k*(1.-2.*k*x*x)/omega**2)


def test_cylinder_spectrum_against_separation_of_variables():
    expected = (np.arange(1, 4)*np.pi/3.)**2+(2.*3.+1./3.)/4.
    coarse = lowest_modes(Cylinder(), (-1.5, 1.5), nodes=129, angular_index=2)
    fine = lowest_modes(Cylinder(), (-1.5, 1.5), nodes=257, angular_index=2)
    assert np.all(coarse["eigenvalues"] > fine["eigenvalues"])
    np.testing.assert_allclose(fine["eigenvalues"], expected, rtol=1.1e-4)
    np.testing.assert_allclose((coarse["eigenvalues"]-expected)/(
        fine["eigenvalues"]-expected), 4., rtol=3e-4)


def test_four_dimensional_conformal_covariance_of_mode_operator():
    x = np.linspace(-1.8, 1.8, 37)
    for j in (0, 1, 7):
        plain = mode_potential(Cylinder(clock=3.), x, angular_index=j)
        scaled = mode_potential(Cylinder(clock=3., conformal_scale=.2), x, angular_index=j)
        np.testing.assert_allclose(plain, scaled, rtol=8e-15, atol=2e-15)
    a = lowest_modes(Cylinder(), (-1.7, 1.7), nodes=257)
    b = lowest_modes(Cylinder(conformal_scale=.2), (-1.7, 1.7), nodes=257)
    np.testing.assert_allclose(a["eigenvalues"], b["eigenvalues"], rtol=5e-12)


def test_higher_angular_modes_and_dirichlet_restriction_raise_spectrum():
    chart = Cylinder()
    low = lowest_modes(chart, (-2., 2.), nodes=257, boundary="natural_u")
    cut = lowest_modes(chart, (-1., 1.), nodes=257)
    high = lowest_modes(chart, (-2., 2.), nodes=257, angular_index=1, boundary="natural_u")
    np.testing.assert_allclose(high["eigenvalues"]-low["eigenvalues"], .5, atol=2e-11)
    assert cut["eigenvalues"][0] > low["eigenvalues"][0] > 0


def test_clock_rescaling_changes_frequency_but_not_physical_tensor():
    first = lowest_modes(Cylinder(), (-1.5, 1.5), nodes=129)
    second = lowest_modes(Cylinder(clock=11.), (-1.5, 1.5), nodes=129)
    np.testing.assert_allclose(second["eigenvalues"], 121.*first["eigenvalues"], rtol=3e-12)


def test_cylinder_stress_trace_and_virtual_work():
    radius, length, reference, logarithm, step = 2.3, 1.7, 2., .8, 1e-5
    def energy(r, d):
        return 4.*np.pi*r*r*d*cylinder_tensor(r, reference, logarithm)[0]
    rho, pr, pt = cylinder_tensor(radius, reference, logarithm)
    measured_pr = -(energy(radius, length+step)-energy(radius, length-step))/(2.*step*4.*np.pi*radius**2)
    measured_pt = -(energy(radius+step, length)-energy(radius-step, length))/(2.*step*8.*np.pi*radius*length)
    np.testing.assert_allclose([pr, pt], [measured_pr, measured_pt], rtol=4e-10)
    np.testing.assert_allclose(-rho+pr+2.*pt, 1./(1440.*np.pi**2*radius**4), rtol=2e-15)
    assert rho+pr == 0


def test_cylindrical_substitution_is_conserved_on_a_varying_radius():
    chart = Cylinder(conformal_scale=.12)
    x, step = np.linspace(-1.5, 1.5, 21), 1e-5
    r, _, b, rp, _, ap, _ = chart.jets(x)
    t = cylinder_tensor(r, 2., 1.)
    tp = cylinder_tensor(chart.jets(x+step)[0], 2., 1.)
    tm = cylinder_tensor(chart.jets(x-step)[0], 2., 1.)
    divergence = (tp[:, 1]-tm[:, 1])/(2.*step*b)+ap*(t[:, 0]+t[:, 1])+2.*rp/r*(t[:, 1]-t[:, 2])
    assert abs(divergence).max() < 1e-15


def test_modes_have_consistent_mass_normalization_and_small_residual():
    chart = Cylinder(conformal_scale=.1)
    result = lowest_modes(chart, (-1.5, 1.5), nodes=257)
    problem = finite_element_problem(chart, (-1.5, 1.5), nodes=257)
    u = result["modes"][1:-1]
    np.testing.assert_allclose(u.T@problem["inertia"]@u, np.eye(3), atol=2e-14)
    assert result["relative_residual"].max() < 1e-10
    np.testing.assert_array_equal(result["modes"][[0, -1]], 0.)


def test_invalid_scalar_domains_and_parameters_are_rejected():
    with pytest.raises(ValueError):
        mode_potential(Cylinder(), np.array([0.]), angular_index=-1)
    with pytest.raises(ValueError):
        mode_potential(Cylinder(), np.array([0.]), mass=-1.)
    with pytest.raises(ValueError):
        lowest_modes(Cylinder(), (-3., 1.))
    with pytest.raises(ValueError):
        lowest_modes(Cylinder(), (-1., 1.), boundary="neumann_phi")
    with pytest.raises(ValueError):
        cylinder_tensor(-1., 2., 1.)
