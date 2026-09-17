import numpy as np
from numpy.testing import assert_allclose
from scipy.integrate import quad

from adm_harness.finite_reaction_transport import (
    SupportWithPhotons, TwoDelayLine, channel_powers, finite_branch_power,
    inverse_commands, inverse_filter_certificate,
)
from adm_harness.scheduled_optical_transfer import rotor_rhs, rotor_state


def test_stable_inverse_and_certified_absolute_impulse_sum():
    impulse = np.r_[1., np.zeros(511)]
    h = inverse_commands(impulse, 1)
    proof = inverse_filter_certificate()
    assert np.sum(abs(h)) <= proof["l1_upper"] < 2.638293
    assert proof["tail_upper"] < 8.5e-10
    assert_allclose(h[2:]+.5*h[1:-1]+.5*h[:-2], 0., atol=1e-16)


def test_delayed_power_balance_and_prepared_positive_streams():
    line = TwoDelayLine(.125, 0., 300., peak=1., pilot=1.)
    time = np.arange(0., 5., .125/8)
    power = .2*np.sin(time*7)
    result = channel_powers(time, power, line, samples_per_delay=8)
    assert_allclose(result["support_power_error"], 0., atol=3e-16)
    assert_allclose(result["source_power_error"], 0., atol=3e-16)
    assert result["minimum_emitted_power"].min() > 0
    assert_allclose(result["energy"], .375, atol=2e-15)


def test_uncharged_bootstrap_exposes_negative_return_power():
    line = TwoDelayLine(.125, 0., 300., peak=1e-12, pilot=1e-12)
    time = np.arange(0., 1., .125/4)
    result = channel_powers(time, np.ones_like(time), line, samples_per_delay=4)
    assert result["minimum_emitted_power"][0] < -.49


def test_photon_inventory_matches_spatial_integral_and_boundary_flux():
    line = TwoDelayLine(.125, 0., 300.)
    for time in (0., .05, 80., 255.99, 350., 555.99):
        actual = sum(quad(line.bias, time-k*.125, time, epsabs=1e-13)[0] for k in (1, 2))
        state = line.state(time)
        assert_allclose(state["energy"], actual, atol=4e-12)
        step = .01
        derivative = (line.state(time+step)["energy"]-line.state(time-step)["energy"])/(2*step)
        assert_allclose(derivative, state["energy_rate"], atol=2e-10)


def test_coupled_energy_derivative_includes_photon_stress_and_filling():
    support = SupportWithPhotons(np.array([4., 100.]), np.array([.7, 16.]), np.array([.006, .13]), .1)
    state = np.array([1.22, .001, np.sqrt(1.22**2-1-2e-4), 1e-4])
    W, Wdot, guide_trace, guide_rate = .03, .002, .001, -.0003
    for N in (-1., .3, 1.):
        result = finite_branch_power(state, N, support, W, Wdot, guide_trace, guide_rate)
        rhs = rotor_rhs(state, result["rotor_power"])
        def energy(dt):
            z = state+dt*rhs
            s = rotor_state(z)
            trace = 18*(s["pressure_trace"]-.4*z[0]*z[1])+guide_trace+dt*guide_rate+W+dt*Wdot
            return 18*s["energy"]+support.state(trace)["energy"]+W+dt*Wdot
        step = 1e-6
        assert_allclose((energy(step)-energy(-step))/(2*step), N, atol=5e-8)
        assert_allclose(result["rotor_power"]+result["support_power"]+Wdot, N, atol=3e-16)


def test_vector_history_evaluation_agrees_with_scalar_original_equations():
    support = SupportWithPhotons(np.array([4., 100.]), np.array([.7, 16.]), np.array([.006, .13]), .1)
    state = np.array([1.22, .001, np.sqrt(1.22**2-1-2e-4), 1e-4])
    states = np.repeat(state[:, None], 9, axis=1)
    states[1] = np.linspace(-.001, .001, 9)
    power = np.linspace(-1, 1, 9)
    vector = finite_branch_power(states, power, support, .03, .002)
    scalar = [finite_branch_power(states[:, i], power[i], support, .03, .002) for i in range(9)]
    for key in vector:
        assert_allclose(vector[key], [s[key] for s in scalar], rtol=2e-12, atol=2e-13)
