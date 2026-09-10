import numpy as np

from adm_harness.active_transfer_reservoir import MetricJets
from adm_harness.causal_reservoir_transport import signal_velocity, trace_past_signal


class FlatHistory:
    times = np.array([0., 1.])
    edges = (-3., 3.)

    def __init__(self, velocity=0.):
        self.v = velocity
        self.model = self

    def metric(self, t, x):
        one, zero = np.ones_like(x), np.zeros_like(x)
        return MetricJets(one, zero, one, one, zero, zero, zero, zero, zero, zero)

    def velocity(self, t, x):
        return np.full_like(x, self.v)

    def material_position(self, t, fraction):
        return fraction+self.v*t


def test_signal_cone_respects_relativistic_velocity_addition():
    history = FlatHistory(-.9)
    g = history.metric(0., np.array([0.]))
    for direction in (-1, 1):
        got = signal_velocity(g, np.array([-.9]), .5, direction)[0]
        np.testing.assert_allclose(got, (-.9+direction*.5)/(1-.9*direction*.5))
        assert abs(got) < 1


def test_null_access_is_independent_of_material_velocity():
    for v in (0., -.99, .7):
        h = FlatHistory(v)
        ray = trace_past_signal(h, 1., 0., 1., 1)
        np.testing.assert_allclose(ray['position'](0.), -1., atol=1e-10)
        np.testing.assert_allclose(ray['null_comoving_gain'](0.), 1., atol=1e-10)


def test_subluminal_latest_emission_matches_flat_moving_worldlines():
    h = FlatHistory(-.4)
    ray = trace_past_signal(h, 1., -.4, .5, -1)
    normal = (-.4-.5)/(1+.4*.5)
    donor = .1
    expected = (normal+.4+donor)/(normal+.4)
    np.testing.assert_allclose(ray['latest_emission'](donor), expected, atol=1e-9)
    assert ray['latest_emission'](1.) is None


def test_static_lapse_null_frequency_gain_has_the_tolman_redshift():
    class StaticHistory(FlatHistory):
        def metric(self, t, x):
            one, zero = np.ones_like(x), np.zeros_like(x)
            alpha = np.exp(.2*x)
            return MetricJets(alpha, zero, one, one, .2*alpha, zero, zero, zero, zero, zero)
    h = StaticHistory()
    ray = trace_past_signal(h, 1., 0., 1., 1)
    x0 = ray['position'](0.)
    np.testing.assert_allclose(ray['null_comoving_gain'](0.), np.exp(.2*x0), rtol=1e-8)


def test_reachable_edge_waits_at_a_timelike_material_end():
    h = FlatHistory()
    h.edges = (-.5, .5)
    ray = trace_past_signal(h, 1., 0., 1., 1)
    np.testing.assert_allclose(ray['first_time'], .5, atol=1e-9)
    np.testing.assert_allclose(ray['position'](0.), -.5, atol=1e-9)
    assert ray['null_comoving_gain'](0.) is None
