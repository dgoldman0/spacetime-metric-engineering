"""Independent physical limits and conservative causal-delivery checks."""
import numpy as np

from adm_harness.active_transfer_reservoir import MetricJets, divergence_projections
from adm_harness.poynting_delivery import (
    guide_energy_bound, propagate, reflection_guide_multiplier, wave_moments,
)


def test_least_preparation_matches_flat_constant_absorber():
    # D_t+D_x=-1, D(T,x)=0, D(t,1)=0 gives min(T-t,1-x).
    errors = []
    for n in (40, 80):
        edges = np.linspace(0., 1., n+1)
        x = (edges[1:]+edges[:-1])/2
        t = np.linspace(0., .5, n+1)
        coeff = lambda unused_t, unused_i: (np.ones(n+1), np.zeros(n), np.ones(n))
        h, ledger = propagate(t, edges, coeff, backwards=True)
        exact = np.minimum(.5-t[:, None], 1-x[None, :])
        errors.append(np.mean(abs(h-exact)))
        assert abs(sum(row['balance_residual'] for row in ledger)) < 1e-13
        assert np.min(h) >= 0
    assert errors[1] < .7*errors[0]


def test_empty_channel_emission_and_recovery_have_causal_front():
    n = 80
    e = np.linspace(0., 1., n+1)
    x = (e[1:]+e[:-1])/2
    t = np.linspace(0., .2, 61)
    coeff = lambda unused_t, unused_i: (-np.ones(n+1), np.zeros(n), (x > .8).astype(float))
    h, ledger = propagate(t, e, coeff)
    assert h[0].max() == 0
    assert h[-1, x < .4].max() < 1e-6
    assert np.max(np.abs([row['balance_residual'] for row in ledger])) < 1e-14


def test_geometric_redshift_for_spherical_null_tensor_is_independent():
    # Static alpha=exp(a*x), B=1, R=exp(b*x). A free outgoing ray has
    # mu proportional to alpha^-2 R^-2, independently of the transport code.
    a, b = .13, .21
    x = np.array([.3, .7])
    z = np.zeros_like(x)
    g = MetricJets(np.exp(a*x), z, np.ones_like(x), np.exp(b*x),
                   a*np.exp(a*x), z, z, z, z, np.full_like(x, b))
    mu = np.exp(-2*(a+b)*x)
    tensor = wave_moments(mu, z)
    p, f = divergence_projections(g, tensor, tensor*0, -2*(a+b)*tensor)
    np.testing.assert_allclose(p, 0., atol=1e-15)
    np.testing.assert_allclose(f, 0., atol=1e-15)


def test_static_redshift_absorber_has_analytic_transport_solution():
    # Along + rays D_t+alpha D_x=-2 alpha_x D-alpha q for B=R=1.
    # For q=1 and time-independent flux at x=1 equal to zero,
    # D(x)=exp(-2*a*x) integral_x^1 exp(2*a*y) dy.
    a, n = .2, 120
    e = np.linspace(0., 1., n+1)
    x = (e[1:]+e[:-1])/2
    coeff = lambda unused_t, unused_i: (np.exp(a*e), -a*np.exp(a*x), np.exp(a*x))
    h, unused = propagate(np.linspace(0., 2., 241), e, coeff, backwards=True)
    exact = (np.exp(2*a*(1-x))-1)/(2*a)
    assert np.mean(abs(h[0]-exact)) < 3e-4


def test_guide_field_controls_drift_and_pays_for_reflection():
    wave = np.array([.2, 1., 3.])
    for speed in (.2, .5, .8):
        guide = guide_energy_bound(wave, speed)
        np.testing.assert_allclose(np.sqrt(wave/(2*guide+wave)), speed)
        for r in (0., .1, .5, 1.):
            g = reflection_guide_multiplier(r, speed)*wave
            electric = (1+r)**2*wave
            magnetic = 2*g+(1-r)**2*wave
            np.testing.assert_allclose(electric/magnetic, speed**2)
            assert np.all(g >= guide)
