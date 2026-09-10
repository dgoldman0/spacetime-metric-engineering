"""Field-role sharing, finite conversion, and independent covariant reactions."""
import numpy as np

from adm_harness.active_transfer_reservoir import MetricJets, divergence_projections
from adm_harness.shared_field_delivery import (
    average_electric_rate, cold_current_velocities, electric_share_cap,
    radial_field_moments, smooth_under_cap,
)


def test_static_electric_magnetic_reallocation_preserves_total_tensor_and_work():
    t = np.linspace(0., 1., 31)
    h = np.exp(.3*t[:, None])*np.array([[1., 2.]])
    share = np.array([.2, .7])
    radius = 1+.2*t[:, None]+np.array([[0., .3]])
    np.testing.assert_allclose(radial_field_moments((h-share)/radius**4)
                              +radial_field_moments(share/radius**4),
                              radial_field_moments(h/radius**4))
    np.testing.assert_allclose(np.diff(h-share, axis=0), np.diff(h, axis=0))


def test_share_cap_preserves_both_charging_and_discharge_rates():
    t = np.linspace(0., 2., 71)
    lapse = np.ones((len(t), 3))
    h = 2+np.sin(2*t[:, None]+np.array([[0., .5, 1.]]))
    cap = electric_share_cap(t, h, lapse, electric_floor=.15)
    electric = h-cap
    assert (electric >= .15*h.min(axis=0)-1e-14).all()
    assert average_electric_rate(t, electric, lapse).max() <= 1+1e-12
    assert cap.max() > .2


def test_under_cap_smoothing_preserves_narrow_low_inventory_region():
    x = np.linspace(0., 1., 1001)
    cap = .03+(x-.413)**2
    value, gradient, unused = smooth_under_cap(x, cap, np.linspace(0, 1, 21))
    assert np.all(value <= cap+1e-14)
    assert value.min() > 0
    assert np.max(abs(gradient[::50])) < 1e-12


def test_original_knots_constrain_allocation_between_transport_centers():
    t = np.array([0., 1., 2.])
    knots = np.array([0., .5, 1.])
    original = np.column_stack((2*np.ones(3), np.exp(-2*t), 2*np.ones(3)))
    # The original middle knot saturates the rate ceiling. Averaging its
    # neighbours onto transport centers creates artificial spare capacity.
    x = np.array([0., .25, .5, .75, 1.])
    field = np.array([np.interp(x, knots, row) for row in original])
    cap = electric_share_cap(t, field, np.ones_like(field))
    assert cap[1] > .5 and cap[2] < 1e-14
    share, unused, unused_values = smooth_under_cap(x, cap, knots)
    assert share[2] < 1e-14
    assert average_electric_rate(t, field-share, np.ones_like(field)).max() <= 1+1e-12


def test_shared_field_reaction_from_full_divergence_has_zero_rest_work():
    t, x, v = .4, np.array([.2, .7]), .12
    alpha, b, radius = np.exp(.1*x), np.exp(.2*t+.03*x), np.exp(.08*t+.04*x)
    beta = v*alpha/b
    g = MetricJets(alpha, beta, b, radius, .1*alpha, .07*beta,
                   np.full_like(x, .2), np.full_like(x, .03),
                   np.full_like(x, .08), np.full_like(x, .04))
    h = .5+.2*x*x
    moment = radial_field_moments(h/radius**4)
    p, f = divergence_projections(g, moment, -.32*moment,
        radial_field_moments(.4*x/radius**4)-.16*moment)
    gamma = 1/np.sqrt(1-v*v)
    np.testing.assert_allclose(gamma*(p-v*f), 0., atol=1e-15)
    np.testing.assert_allclose(gamma*(f-v*p), -.4*x/(gamma*b*radius**4), atol=1e-15)


def test_cold_current_solution_conserves_each_species_and_mass_weighted_invariant():
    for mass in (1., 1836.15267343):
        for k in (-.2, -.1, 0., .1, .2, 1., 10.):
            bp, bm = cold_current_velocities(k, mass)
            qp, qm = np.sqrt((1-bp)/(1+bp)), np.sqrt((1-bm)/(1+bm))
            # Reconstructing q from beta loses precision near |beta|=1.
            np.testing.assert_allclose(mass*qp+qm, mass+1, rtol=1e-9)
            np.testing.assert_allclose(1/(1-bp)-1/(1-bm), k, atol=1e-9)
            assert max(abs(bp), abs(bm)) < 1
    bp, bm = cold_current_velocities(.2, 1836.15267343)
    assert max(abs(bp), abs(bm)) < .26
