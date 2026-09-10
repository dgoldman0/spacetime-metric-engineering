import numpy as np
import pytest

from adm_harness.active_transfer_reservoir import (
    MetricJets, TabulatedActiveMedium, divergence_projections, medium_mask, required_preload,
    trace_characteristics,
)


def analytic_fields(t, x):
    return np.array([np.exp(.1*np.sin(t*x)), .2*np.tanh(x+.3*t),
                     np.exp(.07*t*np.cos(x)), np.sqrt(x*x+4)*np.exp(.03*np.sin(t)*np.exp(-x*x))])


def analytic_moments(t, x):
    return np.array([1+.1*t*np.cos(x), .2+.1*np.cos(x), .03*np.sin(t)*x, .15+.03*np.cos(t)])


def four_geometry_and_tensor(z):
    t, x, theta, _ = z
    a, beta, b, r = analytic_fields(t, x)
    rho, pressure, current, angular = analytic_moments(t, x)
    g = np.diag([-a*a+b*b*beta*beta, b*b, r*r, r*r*np.sin(theta)**2])
    g[0, 1] = g[1, 0] = b*b*beta
    n = np.array([1/a, -beta/a, 0., 0.])
    e = np.array([0., 1/b, 0., 0.])
    et = np.array([0., 0., 1/r, 0.])
    ep = np.array([0., 0., 0., 1/(r*np.sin(theta))])
    tensor = (rho*np.outer(n, n)+pressure*np.outer(e, e)
              +current*(np.outer(n, e)+np.outer(e, n))
              +angular*(np.outer(et, et)+np.outer(ep, ep)))
    return g, tensor


@pytest.mark.parametrize('t,x', [(.5, 1.4), (-.3, -.9), (1.1, .2)])
def test_medium_sources_match_independent_four_dimensional_divergence(t, x):
    step = 1e-5
    z = np.array([t, x, 1.1, 0.])
    g, tensor = four_geometry_and_tensor(z)
    dg, d_tensor = [], []
    for axis in range(4):
        offset = np.eye(4)[axis]*step
        gp, tp = four_geometry_and_tensor(z+offset)
        gm, tm = four_geometry_and_tensor(z-offset)
        dg.append((gp-gm)/(2*step)); d_tensor.append((tp-tm)/(2*step))
    inverse = np.linalg.inv(g)
    connection = np.zeros((4, 4, 4))
    for k in range(4):
        for i in range(4):
            for j in range(4):
                connection[k, i, j] = .5*sum(inverse[k, q]*(dg[i][j, q]+dg[j][i, q]-dg[q][i, j]) for q in range(4))
    divergence = np.array([sum(d_tensor[m][m, n] for m in range(4))
                           +sum(connection[m, m, k]*tensor[k, n]+connection[n, m, k]*tensor[m, k]
                                for m in range(4) for k in range(4)) for n in range(4)])
    values = analytic_fields(t, x)
    dt = (analytic_fields(t+step, x)-analytic_fields(t-step, x))/(2*step)
    dx = (analytic_fields(t, x+step)-analytic_fields(t, x-step))/(2*step)
    a, beta, b, r = values
    jets = MetricJets(a, beta, b, r, dx[0], dx[1], dt[2]/b, dx[2]/b, dt[3]/r, dx[3]/r)
    expected = np.array([a*divergence[0], b*(divergence[1]+beta*divergence[0])])
    actual = divergence_projections(jets, analytic_moments(t, x),
        (analytic_moments(t+step, x)-analytic_moments(t-step, x))/(2*step),
        (analytic_moments(t, x+step)-analytic_moments(t, x-step))/(2*step))
    np.testing.assert_allclose(actual, expected, rtol=2e-8, atol=2e-10)


def test_stationary_radial_radiation_redshift_and_spherical_dilution():
    x = np.array([.5, 1., 2.])
    a, b, r = np.exp(.2*x), np.exp(-.1*x), np.sqrt(x*x+4.)
    jets = MetricJets(a, np.zeros(3), b, r, .2*a, np.zeros(3), np.zeros(3),
                      np.full(3, -.1), np.zeros(3), x/(x*x+4.))
    mu = 1/(a*a*r*r)
    mu_x = mu*(-.4-2*x/(x*x+4.))
    for direction in [-1, 1]:
        moments = np.array([mu, mu, direction*mu, np.zeros(3)])
        dx = np.array([mu_x, mu_x, direction*mu_x, np.zeros(3)])
        np.testing.assert_allclose(divergence_projections(jets, moments, moments*0, dx), 0., atol=2e-16)


def test_packet_and_outer_medium_exclusion_have_zero_first_derivatives():
    x = np.array([.2, .3, .5, 2.1, -2.1, 3.])
    mask, dt, dx = medium_mask(.2, x)
    np.testing.assert_array_equal(mask, 0.)
    np.testing.assert_array_equal(dt, 0.)
    np.testing.assert_array_equal(dx, 0.)
    for t, x in [(.7, 1.1), (.8, 2.), (-.7, -1.1)]:
        h = 1e-6
        _, mt, mx = medium_mask(t, x)
        np.testing.assert_allclose(mt, (medium_mask(t+h, x)[0]-medium_mask(t-h, x)[0])/(2*h), rtol=1e-7, atol=1e-8)
        np.testing.assert_allclose(mx, (medium_mask(t, x+h)[0]-medium_mask(t, x-h)[0])/(2*h), rtol=1e-7, atol=1e-8)


class ManufacturedTransport:
    def coefficients(self, t, x, direction):
        # y'=0.3y+exp(0.3t)cos(t); exact source integral sin(t).
        return np.full_like(x, direction*1.2), np.full_like(x, .3), np.full_like(x, np.exp(.3*t)*np.cos(t))


def test_characteristics_and_preload_against_exact_forced_transport():
    seeds = np.array([-1., 0., 1.])
    errors = []
    for step in [.1, .05]:
        times = np.linspace(0., 2*np.pi, round(2*np.pi/step)+1)
        result = trace_characteristics(ManufacturedTransport(), seeds, times, 1)
        np.testing.assert_allclose(result[:, 0], seeds[None, :]+1.2*times[:, None], atol=1e-13)
        np.testing.assert_allclose(result[:, 1], np.broadcast_to(.3*times[:, None], result[:, 1].shape), atol=1e-13)
        errors.append(np.max(abs(result[:, 2]-np.sin(times[:, None]))))
        preload = required_preload(result[:, 2])
        assert np.min(result[:, 2]+preload) >= -1e-15
        assert abs(preload[0]-1) < .002
    assert errors[1] < errors[0]/12


def test_later_withdrawal_sets_unavoidable_earlier_energy():
    integral = np.array([[0., 0.], [.2, -.1], [-.4, -.1]])
    initial = required_preload(integral)
    np.testing.assert_allclose(initial, [.4, .1])
    # If the middle event is in the packet, the first stream must carry 0.6
    # there. Additional initial preload only increases that exposure.
    np.testing.assert_allclose(initial+integral[1], [.6, 0.])


def test_exterior_completion_preserves_core_and_matches_smoothly(tmp_path):
    times, positions = np.linspace(-1., 1., 9), np.linspace(-6., 6., 97)
    tt, xx = np.meshgrid(times, positions, indexing='ij')
    values = dict(log_alpha=.03*tt+.02*xx, beta=.04*tt-.01*xx,
                  log_b=.02*tt-.01*xx,
                  log_r=.5*np.log(xx*xx+4.)+.01*tt+.03)
    metric = tmp_path/'metric.npz'
    medium = tmp_path/'medium.npz'
    np.savez(metric, t=times, x=positions, core_radius=2., **values)
    np.savez(medium, t=times, x=positions,
             **{key: np.zeros_like(tt) for key in ('rho', 'pressure', 'current', 'angular')})
    model = TabulatedActiveMedium(metric, medium)
    core = model.metric(.2, np.array([-2., 0., 2.]))
    np.testing.assert_allclose(core.alpha, np.exp(.006+.02*np.array([-2., 0., 2.])), atol=1e-14)
    np.testing.assert_allclose(core.logb_t, .02, atol=1e-14)
    for edge in (-6., -5., 5., 6.):
        h = 1e-5
        x = np.array([edge-h, edge, edge+h])
        jets = model.metric(.2, x)
        # The first metric derivatives also join with continuous slope (C2).
        for gradient in (jets.alpha_x, jets.beta_x, jets.logb_x, jets.logr_x):
            slopes = np.diff(gradient)/h
            assert abs(slopes[0]-slopes[1]) < 2e-4
        for values, gradient in ((jets.alpha, jets.alpha_x), (jets.beta, jets.beta_x),
                                 (np.log(jets.b), jets.logb_x), (np.log(jets.radius), jets.logr_x)):
            np.testing.assert_allclose((values[2]-values[0])/(2*h), gradient[1], atol=1e-8)
    exterior = model.metric(.2, np.array([-7., 7.]))
    np.testing.assert_array_equal(exterior.alpha, 1.)
    np.testing.assert_array_equal(exterior.beta, 0.)
    np.testing.assert_allclose(exterior.radius, np.sqrt(53.))
    np.testing.assert_array_equal(exterior.logr_t, 0.)
