import numpy as np
import pytest

from adm_harness.active_transfer_reservoir import MetricJets, divergence_projections
from adm_harness.graded_electrothermal import (
    contact_profiles, fixed_kinematics, force_ports, hoop_force_cone, maximum_null,
    moments, solve_schedule, smooth_spline_scalars,
)


def scalars(t, x):
    return np.array([np.exp(.12*np.sin(t+x)), .1*np.cos(t-x),
                     np.exp(.08*t*np.cos(x)), np.sqrt(x*x+4)*np.exp(.03*t)])


def jets(t, x):
    h = 1e-5
    a, beta, b, r = scalars(t, x)
    dt = (scalars(t+h, x)-scalars(t-h, x))/(2*h)
    dx = (scalars(t, x+h)-scalars(t, x-h))/(2*h)
    return MetricJets(a, beta, b, r, dx[0], dx[1], dt[2]/b, dx[2]/b, dt[3]/r, dx[3]/r), dt


def tensor(t, x):
    a, beta, b, r = scalars(t, x)
    v = b*beta/a
    gamma = 1/np.sqrt(1-v*v)
    m, hh = 2+.3*np.sin(t+x), 1.5+.2*np.cos(.7*t-x)
    return moments(m, hh, dict(gamma=gamma, b=b, radius=r, v=v))


@pytest.mark.parametrize('t,x', [(.3, -1.2), (.9, .4), (1.3, 1.5)])
def test_reduced_equations_match_covariant_tensor_divergence(t, x):
    h = 1e-5
    g, dt = jets(t, x)
    v, gamma, lapse, acc, _ = fixed_kinematics(g, dt[0], dt[1])
    power, force = divergence_projections(g, tensor(t, x),
        (tensor(t+h, x)-tensor(t-h, x))/(2*h), (tensor(t, x+h)-tensor(t, x-h))/(2*h))
    m, mt = 2+.3*np.sin(t+x), .3*np.cos(t+x)
    ht, hx = -.14*np.sin(.7*t-x), .2*np.sin(.7*t-x)
    w = m/(gamma*g.volume)
    expected_power = (mt+gamma*g.b/g.radius**2*ht)/(g.alpha*g.volume)
    expected_force = w*acc-hx/(gamma*g.b*g.radius**4)-v*ht/(lapse*g.radius**4)
    np.testing.assert_allclose([gamma*(power-v*force), gamma*(force-v*power)],
                              [expected_power, expected_force], rtol=2e-8, atol=1e-10)


def test_coordinate_acceleration_from_metric_worldline_definition():
    t, x, h = .7, -1.1, 1e-5
    g, dt = jets(t, x)
    _, gamma, lapse, acc, _ = fixed_kinematics(g, dt[0], dt[1])
    def lapse_and_shift_cov(t, x):
        a, beta, b, _ = scalars(t, x)
        nn = np.sqrt(a*a-b*b*beta*beta)
        return nn, b*b*beta/nn
    n_x = (lapse_and_shift_cov(t, x+h)[0]-lapse_and_shift_cov(t, x-h)[0])/(2*h)
    u_x_t = (lapse_and_shift_cov(t+h, x)[1]-lapse_and_shift_cov(t-h, x)[1])/(2*h)
    independent = (u_x_t+n_x)/(lapse*gamma*g.b)
    np.testing.assert_allclose(acc, independent, rtol=1e-8)


def test_exact_oblique_null_maximum_against_dense_angular_search():
    rng = np.random.default_rng(260910)
    stress = rng.normal(size=(4, 30))
    exact, direction = maximum_null(stress)
    z = np.linspace(-1, 1, 20001)[:, None]
    rho, radial, current, angular = stress
    sampled = rho+radial*z*z+angular*(1-z*z)-2*current*z
    assert np.max(exact-sampled.max(axis=0)) < 2e-8
    assert np.min(exact-sampled.max(axis=0)) > -1e-14
    np.testing.assert_allclose(exact, rho+radial*direction**2+angular*(1-direction**2)-2*current*direction)


def flat_coefficients(nt, nx):
    ones = np.ones((nt, nx)); zero = ones*0
    return dict(c=ones/4, d=zero, a=zero, source=ones*(-.08), force=ones*.16,
                v=zero, gamma=ones, b=ones, radius=ones*2, alpha=ones, lapse=ones,
                acceleration=zero, angular_gradient=zero)


@pytest.mark.parametrize('solver', ['highs', 'highs-ipm'])
def test_passive_schedule_recovers_exact_flat_capacitor_and_positive_buffer(solver):
    t, x = np.linspace(0, 1, 9), np.linspace(0, 1, 9)
    c = flat_coefficients(len(t), len(x))
    result = solve_schedule(t, x, c, np.ones(len(x)), np.ones(len(x))*2, primary_solver=solver)
    assert result['success']
    np.testing.assert_allclose(result['flux_energy'], np.broadcast_to(1e-8+.16*x, (len(t), len(x))), atol=2e-6)
    np.testing.assert_allclose(result['mass_energy'], np.broadcast_to(2-.08*t[:, None], (len(t), len(x))), atol=2e-6)
    np.testing.assert_allclose(result['optimal_supplied_null_peak'], .52, atol=2e-8)
    normal, _, _ = force_ports(t, x, c, result['mass_energy'], result['flux_energy'])
    assert abs(normal).max() < 1e-9
    assert result['primary_dual_gap'] < 1e-8


def test_port_sign_and_hoop_force_cone_count_opposite_support_divergence():
    t, x = np.linspace(0, 1, 5), np.linspace(0, 1, 5)
    c = flat_coefficients(len(t), len(x)); c['source'][:] = 0.; c['force'][:] = 0.
    m = np.ones((len(t), len(x)))*2
    hh = np.broadcast_to(.2*x, m.shape)
    normal, proper, _ = force_ports(t, x, c, m, hh)
    np.testing.assert_allclose(normal, -.2/16)
    np.testing.assert_allclose(proper, normal)
    # The support's required divergence is opposite to the applied force.
    allowed, low, high = hoop_force_cone(np.array([2., -2., 0.]), np.array([.1, .1, .1]),
                                       np.array([-.1, -.1, .1]))
    np.testing.assert_array_equal(allowed, [False, True, True])
    assert low[0] > 0 and high[1] < 0


@pytest.mark.parametrize('solver', ['highs', 'highs-ipm'])
def test_smooth_contacts_preserve_finite_force_shape_and_discharge_bound(solver):
    t, x = np.linspace(0, 1, 13), np.linspace(0, 1, 17)
    c = flat_coefficients(len(t), len(x))
    c['force'][:] = 0.
    c['force'][:, 6:11] = .16
    result = solve_schedule(t, x, c, np.ones(len(x)), np.ones(len(x))*2,
                            ports=(.5,), port_width=.5, smooth_contacts=True, conductivity_ceiling=1., primary_solver=solver)
    assert result['success']
    normal, _, _ = force_ports(t, x, c, result['mass_energy'], result['flux_energy'])
    profile = contact_profiles(x, (.5,), .5)[0]
    expected = result['contact_amplitudes']*profile[None, :]/(4*np.pi*4)
    np.testing.assert_allclose(normal, expected, atol=1e-8)
    hh = result['flux_energy']
    rate = np.log(hh[:-1]/hh[1:])/(2*np.diff(t)[:, None])
    assert rate.max() < 1.0001
    assert np.diff(hh, axis=0).max() < 1e-9


def test_temporal_curvature_extension_preserves_quadratic_boundary_jets():
    from scipy.interpolate import RectBivariateSpline
    t, x = np.linspace(0, 1, 7), np.linspace(-2, 2, 9)
    tt, xx = np.meshgrid(t, x, indexing='ij')
    class Model:
        t_min, t_max = 0., 1.
        metric_splines = [RectBivariateSpline(t, x, factor*(.1*tt**2+.03*xx)) for factor in (1, 2, 3, 4)]
    value = smooth_spline_scalars(Model(), 1.002, -.3)
    base = .1*1.002**2-.009
    np.testing.assert_allclose([np.log(value['alpha']), value['beta'],
                               .5*np.log(value['gamma_ll']), .5*np.log(value['gamma_omega'])],
                              base*np.arange(1, 5), atol=1e-14)
