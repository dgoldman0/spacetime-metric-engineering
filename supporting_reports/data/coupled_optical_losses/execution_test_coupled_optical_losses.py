import numpy as np
import pytest
from numpy.testing import assert_allclose
from scipy.integrate import solve_ivp

from adm_harness.coupled_optical_losses import (
    absorption_gain, absorbing_rotor_ports, absorbing_rotor_rhs,
    effective_input_l1_bounds, energy_only_replacement,
    retained_rotor_heat_bound, rotor_absorption_ceiling,
)
from adm_harness.scheduled_optical_transfer import (
    guide_radius, inverse_guide, rotor_optical_ports, rotor_rhs, rotor_state,
)


def test_partial_absorption_conserves_photon_power_and_torque_work():
    q, j = np.array([-1., -.03, 0., .2, 1.]), np.array([.3, .51, .63, .72, .84])
    a = .025
    p = absorbing_rotor_ports(q, j, a)
    assert_allclose(p["incoming"]-p["outgoing"], q, atol=3e-16)
    assert_allclose(j*p["signed_impulse"]+p["heating"], q, atol=3e-16)
    assert np.all(p["heating"] >= 0)
    for key in ("incoming", "outgoing", "total_port_exposure"):
        assert_allclose(absorbing_rotor_ports(q, j)[key], rotor_optical_ports(q, j)[key], atol=5e-16)


def test_absorption_bound_covers_both_directions_and_inverts_heat_headroom():
    j = np.linspace(.3, .999, 400)
    for a in (6.2e-7, .01, .1):
        for direction in (-1, 1):
            p = absorbing_rotor_ports(direction*np.ones_like(j), j, a)
            assert np.max(p["heating"]) <= absorption_gain(a)*(1+3e-15)
            assert np.all(p["total_port_exposure"] <= (1+absorption_gain(a))/.3)
        bound = retained_rotor_heat_bound(np.array([15., 100., 1000.]), absorption=a)
        assert_allclose(rotor_absorption_ceiling(np.array([15., 100., 1000.]), bound), a, rtol=3e-15)
    with pytest.raises(ValueError, match="extractable"):
        absorbing_rotor_ports(-1., .3, .5)


def test_absorbed_heat_preserves_total_radial_input_and_changes_spin():
    state = np.array([1.2, .015, .6, .007])
    M, q = 19., -.8
    base = rotor_rhs(state, q, inventory=M, damping=.8)
    changed = absorbing_rotor_rhs(state, q, inventory=M, absorption=.02)
    assert_allclose(changed[:2], base[:2], atol=0)
    assert_allclose(2*state[2]*(changed[2]-base[2])+2*(changed[3]-base[3]), 0., atol=1e-16)
    x, p, j, b = state
    V = .5*(x+(1+j*j+2*b)/x)
    h = np.hypot(p, V)
    gradient = np.array([V/h*.5*(1-(1+j*j+2*b)/x**2), p/h, V/h*j/x, V/h/x])
    assert_allclose(M*gradient@changed, q, atol=4e-15)
    assert changed[3] > base[3]
    assert changed[2] < base[2]


def test_integrated_absorption_preserves_radial_trajectory_and_energy():
    initial = [1.2, 0., np.sqrt(1.2**2-1-.002), .001]
    time = np.linspace(0, 3, 501)
    def solve(a):
        return solve_ivp(lambda t, s: absorbing_rotor_rhs(s, -.1, absorption=a),
            [0, 3], initial, t_eval=time, method="DOP853", rtol=2e-11, atol=2e-13,
            max_step=.01).y
    cold, warm = solve(0.), solve(.015)
    assert_allclose(cold[:2], warm[:2], atol=2e-12)
    assert_allclose(rotor_state(cold)["energy"], rotor_state(warm)["energy"], atol=2e-12)
    assert_allclose(rotor_state(warm)["energy"], 1.2-.1/19*time, atol=2e-12)
    assert warm[3, -1] > cold[3, -1]
    assert warm[2, -1] < cold[2, -1]


def test_receipt_variation_bound_covers_slope_jumps_and_endpoint_flights():
    peak = np.array([[2.]])
    duration = np.array([[4.], [5.]])
    left = np.array([[[.2], [1.2]]])
    right = np.array([[[.8], [.4]]])
    deriv = abs(right-left)/duration
    bounds = effective_input_l1_bounds(np.maximum(left, right), left, right,
        deriv, peak, duration, np.array([.25]), np.zeros_like(duration))
    t = np.linspace(-1, 10, 200001)
    def receipt(t):
        return np.where((t >= 0) & (t < 4), .2+.6*t/4,
            np.where((t >= 4) & (t < 9), 1.2-.8*(t-4)/5, 0.))
    actual = np.trapezoid(abs(receipt(t)-receipt(t-.25)), t)/(2*.25)
    assert actual <= bounds["receipt"][0, -1, 0]+2e-5
    assert bounds["receipt"][0, -1, 0] == pytest.approx((.6+.8+.2+.4+.4)/2)


def test_guide_variation_bound_covers_complete_delayed_transition():
    powers = np.array([[[1.]]])
    result = effective_input_l1_bounds(powers, powers, powers, np.zeros_like(powers),
        np.ones((1, 1)), np.array([[1000.]]), np.ones(1), np.zeros((1, 1)))
    t = np.linspace(-1, 130, 30001)
    actual = np.trapezoid(abs(inverse_guide(t-.5, .001, 1.001)["output_power"]
                             -inverse_guide(t+.5, .001, 1.001)["input_power"]), t)
    # One up and one down excursion are paid in the panel bound.
    assert 2*actual <= result["guide"][0, -1, 0]
    assert_allclose(result["radius_variation"][0, -1, 0],
                    2*(guide_radius(1.001)-guide_radius(.001)))


def test_replacement_budget_solves_the_stated_feedback_inequality():
    exposure, alpha, gain = np.array([0., 10., 100.]), 1e-3, 9.5
    energy = energy_only_replacement(exposure, alpha, feedback_gain=gain)
    assert_allclose(energy, alpha*(exposure+gain*energy))
    with pytest.raises(ValueError, match="contractive"):
        energy_only_replacement(1., .2)
