import numpy as np
import pytest
from numpy.testing import assert_allclose

from adm_harness.coupled_holding_certificate import C_MAX, history_result
from adm_harness.coupled_optical_losses import ROTOR_L1_GAIN
from adm_harness.finite_thermal_budget import finite_heat_closure, finite_heat_history, passive_heat_gain
from adm_harness.scheduled_optical_transfer import preparation
from adm_harness.shared_rail_reactions import guide_trace_bound


def test_finite_heat_gain_solves_the_delayed_port_feedback_bound():
    a = 6.2e-7
    r = finite_heat_closure(a)
    kappa, gain = r["passive_heat_gain"], r["port_l1_gain"]
    assert_allclose(gain, ROTOR_L1_GAIN+(ROTOR_L1_GAIN*(1+C_MAX)+1)*2*kappa*gain)
    assert_allclose(r["port_power_peak"]*(1-kappa), 19*.006/(1/(12*np.pi)))
    assert r["feedback_denominator"] > .99998
    with pytest.raises(ValueError, match="contractive"):
        finite_heat_closure(.1)


def test_positive_delayed_heat_obeys_peak_variation_and_l2_bounds():
    tau, a = .037, 1e-3
    kappa = passive_heat_gain(a)
    time = np.linspace(-1, 4, 300001)
    def q(t):
        return np.where((t >= 0) & (t <= 3), np.sin(np.pi*np.clip(t, 0, 3)/3)**2, 0.)
    emitted, arrived = kappa*q(time), kappa*q(time-tau)
    wdot = emitted-arrived
    emitted_l1 = np.trapezoid(emitted, time)
    assert np.max(abs(wdot)) <= kappa
    assert np.trapezoid(abs(wdot), time) <= 2*emitted_l1
    assert np.trapezoid(wdot*wdot, time) <= 2*kappa*emitted_l1
    flight = np.cumsum(wdot)*np.diff(time)[0]
    assert np.min(flight) >= -1e-13
    assert np.max(flight) <= tau*kappa*(1+1e-8)


def test_zero_absorption_recovers_parent_thermal_bound():
    mass = 19.
    prep = preparation(inventory=mass)
    l2 = np.array([[25., 40.], [120., 160.]])
    parent = history_result(l2, np.array([.75, .90]), inventory=mass,
        original_energy_floor=prep["quasistatic_rotor_energy_floor"],
        original_dynamic_energy=prep["initial_dynamic_energy"], guide_trace_bound=guide_trace_bound())
    r = finite_heat_history(np.full_like(l2, 1000.), l2, parent["energy_floor"],
        parent["energy_ceiling"], np.array([.0014, .0015]), inventory=mass, absorption=0.)
    assert_allclose(r["spin_squared_lower"], parent["spin_squared_lower"], atol=3e-17)
    assert_allclose(r["damping_action_upper"], parent["thermal_action_upper"])
    assert np.max(r["absorption_action_upper"]) == 0


def test_heat_and_flight_costs_increase_with_delay_and_absorption():
    args = (np.array([[1000.]]), np.array([[150.]]),
            np.array([1.11]), np.array([1.316]), np.array([.00147]))
    small = finite_heat_history(*args, absorption=6.2e-7, flight_delay=1/64)
    long = finite_heat_history(*args, absorption=6.2e-7, flight_delay=1/8)
    warm = finite_heat_history(*args, absorption=1e-3, flight_delay=1/64)
    assert long["flight_energy_ceiling"] == pytest.approx(8*small["flight_energy_ceiling"])
    assert np.all(long["spin_squared_lower"] < small["spin_squared_lower"])
    assert np.all(warm["absorption_action_upper"] > small["absorption_action_upper"])
    assert not warm["thermal_spin_passed"][0, 0]
