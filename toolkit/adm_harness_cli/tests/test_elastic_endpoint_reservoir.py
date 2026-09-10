import numpy as np
import pytest

from adm_harness.active_transfer_reservoir import MetricJets, divergence_projections
from adm_harness.elastic_endpoint_reservoir import (
    ElasticLaw, ElasticPatch, encode, evolve, flux, geometric_source, recover,
)


@pytest.mark.parametrize('stiffness', [.1, .8])
def test_stored_energy_generates_pressure_and_causal_sound(stiffness):
    law = ElasticLaw(stiffness=stiffness)
    n = np.geomspace(.02, 100., 101)
    q = np.geomspace(.01, 3., 101)
    h = 1e-5*n
    energy, pressure, sound2 = law.rest(n, q)
    plus, pp, _ = law.rest(n+h, q)
    minus, pm, _ = law.rest(n-h, q)
    derivative = (plus-minus)/(2*h)
    np.testing.assert_allclose(n*derivative-energy, pressure, rtol=1e-8, atol=1e-9)
    np.testing.assert_allclose((pp-pm)/(plus-minus), sound2, rtol=1e-8)
    assert np.min(energy-abs(pressure)) > 0
    assert np.min(sound2) > 0 and np.max(sound2) < 1


def test_primitive_recovery_with_tension_compression_heat_and_boosts():
    rng = np.random.default_rng(260910)
    n = np.exp(rng.uniform(-2., 3., 300))
    v = rng.uniform(-.9, .9, 300)
    q = np.exp(rng.uniform(-3., 2., 300))
    b = np.exp(rng.uniform(-2., 2., 300))
    law = ElasticLaw(stiffness=.4, scale=.07)
    recovered = recover(encode(n, v, q, b, law), b, law)
    for key, expected in [('n', n), ('velocity', v), ('thermal', q)]:
        np.testing.assert_allclose(recovered[key], expected, rtol=2e-9, atol=2e-10)


def manufactured_metric(t, x):
    return np.array([np.exp(.07*t*x), .13*np.sin(x+.2*t),
                     np.exp(.1*t*np.cos(x)), np.sqrt(x*x+3)*np.exp(.04*t)])


def metric_jets(t, x):
    h = 1e-5
    a, beta, b, r = manufactured_metric(t, x)
    dt = (manufactured_metric(t+h, x)-manufactured_metric(t-h, x))/(2*h)
    dx = (manufactured_metric(t, x+h)-manufactured_metric(t, x-h))/(2*h)
    return MetricJets(a, beta, b, r, dx[0], dx[1], dt[2]/b, dx[2]/b, dt[3]/r, dx[3]/r)


def manufactured_state(t, x, law):
    g = metric_jets(t, x)
    return encode(np.exp(.1*t*np.cos(x)), .17*np.sin(t+x), .4+.03*np.cos(t*x), g.b, law)


def manufactured_moments(t, x, law):
    g = metric_jets(t, x)
    f = recover(manufactured_state(t, x, law), g.b, law)
    return law.scale/g.radius**2*np.array([f['energy'], f['radial'], f['current'], np.zeros_like(x)])


@pytest.mark.parametrize('t,x', [(.4, -.8), (1.2, .5)])
def test_conservative_sources_match_covariant_spherical_divergence(t, x):
    x, h, law = np.array([x]), 2e-5, ElasticLaw(stiffness=.4, scale=.2)
    g = metric_jets(t, x)
    state = manufactured_state(t, x, law)
    derivative_t = (manufactured_state(t+h, x, law)-manufactured_state(t-h, x, law))/(2*h)
    derivative_x = (flux(manufactured_state(t, x+h, law), metric_jets(t, x+h), law)
                    -flux(manufactured_state(t, x-h, law), metric_jets(t, x-h), law))/(2*h)
    source = derivative_t+derivative_x-geometric_source(recover(state, g.b, law), g, law)
    moments = manufactured_moments(t, x, law)
    dt = (manufactured_moments(t+h, x, law)-manufactured_moments(t-h, x, law))/(2*h)
    dx = (manufactured_moments(t, x+h, law)-manufactured_moments(t, x-h, law))/(2*h)
    power, force = divergence_projections(g, moments, dt, dx)
    np.testing.assert_allclose(source[1], g.alpha*g.volume*power, rtol=2e-6, atol=1e-8)
    np.testing.assert_allclose(source[2], g.alpha*g.b*g.volume*force, rtol=2e-6, atol=1e-8)


class HomogeneousModel:
    def __init__(self, expansion=0., shift=0.):
        self.expansion, self.shift = expansion, shift

    def metric(self, t, x):
        zero, one = np.zeros_like(x), np.ones_like(x)
        return MetricJets(one, one*self.shift, one*np.exp(self.expansion*t), one*2,
                          zero, zero, one*self.expansion, zero, zero, zero)

    def medium(self, t, x):
        return [np.zeros((4, x.size)) for _ in range(3)]


def test_expanding_material_keeps_adiabatic_heat_and_conserved_labels():
    patch = ElasticPatch(HomogeneousModel(expansion=.3), ElasticLaw(stiffness=.4), cells=16)
    result = evolve(patch, duration=.2, snapshots=3)
    assert result['status'] == 'duration_completed'
    f = recover(result['states'][-1], patch.model.metric(.2, patch.x).b, patch.law)
    np.testing.assert_allclose(f['n'], .75*np.exp(-.06), rtol=1e-9)
    np.testing.assert_allclose(f['thermal'], .25, atol=2e-8)
    assert abs(result['history'][-1]['energy_balance_residual']) < 1e-13


def test_closed_ends_in_shifted_coordinates_have_counted_work_and_zero_mass_flux():
    patch = ElasticPatch(HomogeneousModel(shift=.2), ElasticLaw(stiffness=.4), cells=16)
    state = patch.initial()
    rate, fields, diag = patch.rhs(0., state)
    np.testing.assert_allclose(rate, 0., atol=1e-11)
    np.testing.assert_allclose(diag['boundary'], 0., atol=1e-11)
    np.testing.assert_allclose(diag['end_traction'], patch.law.scale*fields['pressure'][0], atol=1e-12)
