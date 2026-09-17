import numpy as np
import pytest

from adm_harness.c1_angular_response import (
    AngularResponse, cylinder_green_excess, cylinder_interaction,
    frequency_rule, improved_tensor, integrate_response,
)


class Cylinder:
    coordinate = np.linspace(-4., 4., 101)

    def __init__(self, clock=1., conformal_scale=0.):
        self.clock, self.conformal_scale = clock, conformal_scale

    def jets(self, x):
        x = np.asarray(x, float)
        k = self.conformal_scale
        omega = np.exp(k*x*x)
        return (2.*omega, self.clock*omega, omega, 4.*k*x,
                np.full_like(x, 4.*k)/omega, 2.*k*x/omega,
                2.*k*(1.-2.*k*x*x)/omega**2)


@pytest.mark.parametrize("frequency,j", [(0., 0), (.7, 0), (2., 1), (3., 4)])
def test_green_difference_against_analytic_cylinder(frequency, j):
    # Binary-aligned anchors preserve the mesh family for the order check.
    x, domain, walls = np.array([-.375, .375]), (-3., 3.), np.array([-.75, 1.5])
    exact = (cylinder_green_excess(frequency, j, x, walls, 2., 3.)
             -cylinder_green_excess(frequency, j, x, domain, 2., 3.))
    results = [np.array(AngularResponse(Cylinder(clock=3.), domain, walls, x,
               nodes=n).moments(frequency, j)) for n in (1025, 2049)]
    scale = np.max(abs(exact))
    assert abs(results[1]-exact).max() < 4e-5*scale
    assert abs(results[1]-exact).max() < .4*abs(results[0]-exact).max()


def test_conformal_state_difference_and_trace():
    x = np.array([-.4, .2, .6])
    plain = AngularResponse(Cylinder(clock=3.), (-3., 3.), np.array([-1., 1.5]), x, 4097)
    curved = AngularResponse(Cylinder(clock=3., conformal_scale=.1),
                             (-3., 3.), np.array([-1., 1.5]), x, 4097)
    for frequency, j in ((0., 0), (.9, 1), (3., 2)):
        t, u = plain.tensor(frequency, j), curved.tensor(frequency, j)
        np.testing.assert_allclose(u*np.exp(.4*x*x)[:, None], t, rtol=8e-5, atol=1e-11)
        np.testing.assert_allclose(-u[:, 0]+u[:, 1]+2*u[:, 2], 0., atol=4e-16)


def test_frequency_measure_and_clock_normalization():
    f, w = frequency_rule(80, 3.)
    np.testing.assert_allclose(w @ (1/(f*f+4.)), np.pi/4., rtol=3e-14)
    parameters = dict(angular_max=20, frequency_nodes=48, eta=2.4e-5)
    x = np.array([.2])
    a = integrate_response(AngularResponse(Cylinder(), (-3., 3.), np.array([-1., 1.5]), x, 1025),
                           frequency_scale=2., **parameters)
    b = integrate_response(AngularResponse(Cylinder(clock=7.), (-3., 3.),
                           np.array([-1., 1.5]), x, 1025), frequency_scale=14., **parameters)
    np.testing.assert_allclose(a["tensor"], b["tensor"], rtol=2e-10)


def test_original_end_force_has_finite_dirichlet_limit():
    problem = AngularResponse(Cylinder(), (-3., 3.), np.array([1.5]), np.array([3.]), 2049)
    f, first, mixed = problem.moments(.8, 2)
    np.testing.assert_array_equal(f, 0.)
    np.testing.assert_array_equal(first, 0.)
    np.testing.assert_allclose(problem.tensor(.8, 2), mixed[:, None]*np.array([1/6, 1/2, -1/6]), rtol=2e-15)
    assert mixed[0] < 0


def test_integrated_end_force_matches_independent_bessel_energy():
    eta = 2.4e-5
    problem = AngularResponse(Cylinder(), (-3., 3.), np.array([1.5]), np.array([3.]), 4097)
    t = integrate_response(problem, angular_max=40, frequency_nodes=80,
                           frequency_scale=1., eta=eta)["tensor"][0]
    energy_force = (cylinder_interaction(2., 1.5, eta=eta)["force"]
                    -cylinder_interaction(2., 6., eta=eta)["force"])
    np.testing.assert_allclose(4*np.pi*4*t[1], energy_force, rtol=8e-6)


def test_improved_bulk_tensor_is_conserved_on_conformal_cylinder():
    chart = Cylinder(clock=3., conformal_scale=.1)
    x = np.linspace(-.5, .7, 81)
    # Independent analytic Green and conformal field transform.
    k, frequency, j = .1, .8, 1
    f, first, mixed = (cylinder_green_excess(frequency, j, x, (-1., 1.5), 2., 3.)
                       -cylinder_green_excess(frequency, j, x, (-3., 3.), 2., 3.))
    omega, s = np.exp(k*x*x), 2*k*x
    fm = f/omega**2
    fp = (first-2*s*f)/omega**3
    mx = (mixed-s*first+s*s*f)/omega**4
    t = improved_tensor(chart, x, frequency, j, fm, fp, mx)
    r, _, b, rp, _, ap, _ = chart.jets(x)
    derivative = np.gradient(t[:, 1], x, edge_order=2)/b
    ward = derivative+ap*(t[:, 0]+t[:, 1])+2*rp/r*(t[:, 1]-t[:, 2])
    assert abs(ward[2:-2]).max() < 1e-4*abs(t).max()


def test_cylinder_interaction_virtual_work_and_holding_floor():
    radius, length, step = 2.3, 1.7, 1e-5
    r = cylinder_interaction(radius, length)
    force = -(cylinder_interaction(radius, length+step)["energy"]
              -cylinder_interaction(radius, length-step)["energy"])/(2*step)
    radial_work = -(cylinder_interaction(radius+step, length)["energy"]
                    -cylinder_interaction(radius-step, length)["energy"])/(2*step)
    np.testing.assert_allclose(force, r["force"], rtol=2e-9)
    np.testing.assert_allclose(radial_work/(8*np.pi*radius*length),
                               r["radius_virtual_work_over_volume"], rtol=2e-9)
    assert r["energy"] < 0 and r["interaction_plus_axial_floor"] > 0


def test_short_cylinder_planar_limit_and_sum_convergence():
    r = cylinder_interaction(2., .2, angular_max=128, winding_max=128)
    fine = cylinder_interaction(2., .2, angular_max=256, winding_max=256)
    np.testing.assert_allclose(r["energy"], fine["energy"], rtol=1e-8)
    np.testing.assert_allclose(r["energy_over_cavity_volume"], -np.pi**2/(1440*.2**4), rtol=3e-5)
    np.testing.assert_allclose(r["force_over_area"], -np.pi**2/(480*.2**4), rtol=3e-5)


def test_new_wall_probe_is_rejected():
    with pytest.raises(ValueError):
        AngularResponse(Cylinder(), (-3., 3.), np.array([.5]), np.array([.5]))
