from fractions import Fraction

import numpy as np
import pytest
from numpy.testing import assert_allclose

from adm_harness.coupled_holding_certificate import (
    DAMPING, coupled_reduced_rhs, storage_matrix,
)
from adm_harness.reaction_endpoint_certificate import (
    INVERSE_L1, _ramp_derivative_upper, _septic_lower, event_certificate,
    guide_derivative_certificate, quiet_pilot, separation_certificate,
    tracking_coefficient_certificate,
)
from adm_harness.scheduled_optical_transfer import (
    ROTOR_RADIUS, inverse_guide, rotor_optical_ports, smooth_step,
)


def test_tracking_equilibrium_output_identity_includes_all_work_branches():
    rng = np.random.default_rng(250917)
    for _ in range(80):
        h, c, w, v = rng.uniform(1.08, 1.32), rng.uniform(0, .5001), rng.uniform(-.012, .012), rng.uniform(-.012, .012)
        inventory, N, Wdot, guide_rate, baseline = 19., rng.uniform(-1, 1), .0003, -4e-7, 7e-5
        n0 = ROTOR_RADIUS*N/inventory
        n = ROTOR_RADIUS*(N-(1+c)*Wdot-c*guide_rate-baseline)/inventory
        z = np.array([w, h*v])
        rhs = coupled_reduced_rhs(*z, h, c, n)
        f, a = rhs["free_trace_coefficients"], rhs["input_trace_coefficient"]
        q = inventory/ROTOR_RADIUS*rhs["rotor_input"]
        P = N-Wdot-q
        equilibrium = np.array([-DAMPING*h*h*n0, h*n0])
        phi_f = np.array([f[0], f[1]-DAMPING*h*f[0]])
        direct = h*(phi_f[1]+1/h)+a-1
        expected = (c*inventory/ROTOR_RADIUS*(f@(z-equilibrium))+c*direct*N
                    +c*(1-a)*Wdot+c*guide_rate+baseline)/(1+c*a)
        assert_allclose(expected, P, rtol=1e-12, atol=1e-15)
        # Independently form the frozen actual matrix and differentiate z*.
        S, x = np.sqrt(1-v*v), h+w
        d0 = DAMPING+S*v/(x*(1+S))
        B = np.array([-1., v])
        A = np.array([[0., 1/h], [-S/x, -d0]])-c/(1+c*a)*np.outer(B, f)
        T = np.array([[1., DAMPING*h], [0., 1.]])
        Bphi = T@B/(1+c*a)
        Aphi = T@A@np.linalg.inv(T)
        g = Aphi@np.array([0., h])+Bphi
        u, n0prime = rhs["rotor_input"], 3e-7
        eqprime = np.array([-2*DAMPING*h*u*n0-DAMPING*h*h*n0prime, u*n0+h*n0prime])
        residual = T@(rhs["derivative"][:2]-A@(z-equilibrium)-eqprime)
        predicted = g*n0+Bphi*(n-n0)+np.array([DAMPING*h, -1.])*u*n0-np.array([0., h])*n0prime
        assert_allclose(residual, predicted, atol=8e-18)
        # The equilibrium displacement at an N jump has exact P-norm h|delta n0|.
        unit = np.array([-DAMPING*h*h, h])
        assert_allclose(unit@storage_matrix(c, h, kind="invariant")@unit, h*h, atol=2e-15)


def test_exact_tracking_coefficient_certificate_and_guide_derivatives():
    result = tracking_coefficient_certificate()
    assert result["exact_integer_interval_arithmetic"]
    assert result["boxes"] == 16384
    assert Fraction(result["input_norm_numerator_upper"]) < Fraction("1.017")
    result = guide_derivative_certificate()
    assert all(a < b for a, b in zip(result["measured_upper"], result["declared_upper"]))
    times = np.linspace(-1, 129, 20003)
    step = 1e-4
    for left, right in ((.001, 1.001), (1.001, .001)):
        def network(t):
            return inverse_guide(t-.5, left, right)["output_power"]-inverse_guide(t+.5, left, right)["input_power"]
        derivative = (network(times+step)-network(times-step))/(2*step)
        assert abs(derivative).max() < result["declared_upper"][1]


def test_septic_interval_bounds_cover_off_grid_points_and_clipped_endpoints():
    rng = np.random.default_rng(432)
    left = rng.uniform(-2, 258, 1200)
    right = left+rng.uniform(0, .04, len(left))
    for order in (1, 2):
        upper = _ramp_derivative_upper(left, right, 0., 1000., order)
        for fraction in (0., .13, .73, 1.):
            sample = smooth_step(left+fraction*(right-left), 256)[order]
            assert np.all(abs(sample) <= upper+1e-18)
    s = np.linspace(0, 1, 1001)
    exact = np.array([float(sum(Fraction(coefficient)*Fraction(float(x))**power*(1-Fraction(float(x)))**(7-power)
                               for power, coefficient in ((4, 35), (5, 21), (6, 7), (7, 1)))) for x in s])
    assert np.all(_septic_lower(s) <= exact)


def test_pilot_pays_quiet_reaction_port_without_guide_pilot_credit():
    result = quiet_pilot(np.array([0, .005244306]), np.array([0, .000118776]))
    assert np.all(result["pilot"] >= result["command_upper"]/.3)
    assert result["pilot"].max() < .011
    assert_allclose(result["command_upper"], INVERSE_L1*result["support_power_upper"])
    with pytest.raises(ValueError, match="nonnegative"):
        quiet_pilot(-1, 0)


def test_independent_branch_incident_inequality_has_correct_doppler_signs():
    rng = np.random.default_rng(1312)
    for _ in range(400):
        j = rng.uniform(.3, .9)
        a, delayed, dB = rng.uniform(-1, 1, 3)
        support = a+delayed-dB
        bias = abs(delayed)+abs(dB)+(1+j)/(2*j)*(abs(support)+2*abs(dB))+.01
        incoming = bias-dB-delayed
        q = -dB-a-delayed
        required = rotor_optical_ports(q, j)["incoming"]
        assert incoming >= required


@pytest.mark.parametrize("direction", [True, False])
def test_event_comparison_certifies_both_emitters_and_rotor_incident_port(direction):
    row, arrays = event_certificate(direction)
    assert row["complete_bin_enclosures"]
    assert row["maximum_event_command"] < .92
    assert row["minimum_emitted_margin"] > .00069
    assert row["minimum_incident_margin_after_allowance"] > .00099
    assert np.all(arrays["time_right"] > arrays["time_left"])
    assert row["final_comparison_state"] < 1e-40


def test_separated_event_tail_and_invalid_short_intervals():
    result = separation_certificate(784)
    assert result["forcing_gap_lower"] == 11.875
    assert result["remote_command_upper"] < 1e-20
    with pytest.raises(ValueError, match="784"):
        separation_certificate(783)
    with pytest.raises(ValueError, match="power-of-two"):
        event_certificate(True, samples_per_delay=3)
