import numpy as np
import pytest
from numpy.testing import assert_allclose

from adm_harness.shared_rail_reactions import reaction_state, rotor_trace_and_rate
from adm_harness.scheduled_optical_transfer import rotor_rhs, rotor_state, ROTOR_MASS, ROTOR_DAMPING


@pytest.mark.parametrize("family", ["maxwell", "photon"])
def test_shared_sheets_and_positive_pressure_bias_cancel_both_stress_channels(family):
    trace = np.linspace(-.03, .03, 101)
    T = np.array([[.6], [.2]])
    M, m = np.array([[.05], [.03]]), np.array([[.002], [.001]])
    r = reaction_state(trace, .01, T, M, m, field_family=family)
    assert_allclose(r["stress_identity_error"], 0, atol=2e-17)
    assert np.all(r["additional_energy"] <= r["continuous_energy_ceiling"])
    assert np.all(r["force_margin"] > 0)
    assert np.all(r["sheet_energy_derivative"] <= 2)
    assert_allclose(r["additional_field_energy"].sum(axis=0), .03)


def test_shared_energy_derivative_counts_core_and_both_joint_directions():
    args = (.01, np.array([.6, .2]), np.array([.05, .03]), np.array([.002, .001]))
    for trace in (-.02, 0., .02):
        step = 1e-6
        actual = (reaction_state(trace+step, *args)["additional_energy"]
                  -reaction_state(trace-step, *args)["additional_energy"])/(2*step)
        assert_allclose(actual, reaction_state(trace, *args)["energy_trace_derivative"], rtol=2e-8)


def test_rotor_reaction_derivative_matches_independent_state_differentiation():
    state = np.array([1.22, -.003, .65, .01])
    for power in (-1., .2, 1.):
        r = rotor_trace_and_rate(state, power)
        rhs = rotor_rhs(state, power)
        def trace(y):
            return ROTOR_MASS*(rotor_state(y)["pressure_trace"]-ROTOR_DAMPING*y[0]*y[1])
        step = 1e-7
        derivative = (trace(state+step*rhs)-trace(state-step*rhs))/(2*step)
        assert_allclose(r["trace"], trace(state), atol=3e-15)
        assert_allclose(r["trace_rate"], derivative, atol=3e-8)
    zero = rotor_trace_and_rate(state, 0.)
    one = rotor_trace_and_rate(state, 1.)
    assert_allclose(one["trace_rate"]-zero["trace_rate"], zero["input_rate_coefficient"], atol=1e-14)
