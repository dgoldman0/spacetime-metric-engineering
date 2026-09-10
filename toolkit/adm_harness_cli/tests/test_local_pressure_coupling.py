import numpy as np
import pytest

from adm_harness.local_pressure_coupling import positive_pressure_profile
from adm_harness.active_transfer_reservoir import MetricJets, divergence_projections
from adm_harness.graded_electrothermal import fixed_kinematics


@pytest.mark.parametrize('drive,expected', [(-2., lambda x: 2*(1-x)), (2., lambda x: 2*x)])
def test_pressure_gradient_supplies_either_signed_force_with_positive_pressure(drive, expected):
    x = np.linspace(0, 1, 33)
    p, direction = positive_pressure_profile(x, np.zeros_like(x), np.full_like(x, drive))
    np.testing.assert_allclose(p, expected(x), atol=1e-14)
    assert np.min(p) >= 0
    assert direction == int(np.sign(drive))


def test_pressure_self_weight_integrating_factor_converges_to_exact_solution():
    errors = []
    for points in (33, 65):
        x = np.linspace(0, 1, points)
        p, _ = positive_pressure_profile(x, np.ones_like(x)*.7, -np.ones_like(x))
        exact = (np.exp(.7*(1-x))-1)/.7
        errors.append(float(abs(p-exact).max()))
    assert errors[1] < errors[0]/3.99


def test_mixed_contact_force_needs_an_explicit_extra_interface():
    x = np.linspace(0, 1, 17)
    with pytest.raises(ValueError):
        positive_pressure_profile(x, x*0, x-.5)


@pytest.mark.parametrize('t,x', [(.3, -1.6), (.8, -.9), (1.2, .6)])
def test_instantaneous_pressure_force_and_heat_match_covariant_divergence(t, x):
    def metric(time, position):
        return np.array([np.exp(.1*np.sin(time+position)), .08*np.cos(time-position),
                         np.exp(.05*time*position), np.sqrt(position**2+4)*np.exp(.02*time)])
    def stress(time, position):
        a, beta, b, _ = metric(time, position)
        v = b*beta/a
        p = 1+.1*np.sin(position)
        moving = 4*p/(1-v*v)
        return np.array([moving-p, moving*v*v+p, moving*v, p])
    h = 1e-5
    a, beta, b, r = metric(t, x)
    dt = (metric(t+h, x)-metric(t-h, x))/(2*h)
    dx = (metric(t, x+h)-metric(t, x-h))/(2*h)
    g = MetricJets(a, beta, b, r, dx[0], dx[1], dt[2]/b, dx[2]/b, dt[3]/r, dx[3]/r)
    v, gamma, lapse, acc, _ = fixed_kinematics(g, dt[0], dt[1])
    power, force = divergence_projections(g, stress(t, x),
        (stress(t+h, x)-stress(t-h, x))/(2*h), (stress(t, x+h)-stress(t, x-h))/(2*h))
    vt = v*(g.logb_t-dt[0]/a)+b*dt[1]/a
    expansion = (g.logb_t+2*g.logr_t+gamma**2*v*vt)/lapse
    p = 1+.1*np.sin(x)
    np.testing.assert_allclose([gamma*(power-v*force), gamma*(force-v*power)],
                              [4*p*expansion, 4*p*acc+.1*np.cos(x)/(gamma*b)],
                              rtol=3e-8, atol=1e-10)
