from fractions import Fraction

import numpy as np
import pytest
from numpy.testing import assert_allclose

from adm_harness.constitutive_joints_and_optics import series_state
from adm_harness.coupled_holding_certificate import (
    C_MAX, DAMPING, HEAT_GAIN, H_MAX, H_MIN, N_MAX, PHOTON_PEAK, PHOTON_PILOT,
    SHORT_DELAY, _Interval, constitutive_panel_bounds, coupled_reduced_rhs,
    forcing_history_bounds, guide_trace_rate_bounds, history_result, input_l1_certificate, matrix_certificate,
    storage_derivatives, storage_matrix,
)
from adm_harness.coupled_rail_reactions import guide_trace_rate
from adm_harness.finite_reaction_transport import TwoDelayLine
from adm_harness.scheduled_optical_transfer import (
    CONVERTER_DELAY, CONVERTER_NET_POWER, CONVERTER_RAMP, RAMP_TIME, ROTOR_RADIUS,
    SPIN_FLOOR, inverse_guide, preparation, rotor_rhs,
)
from adm_harness.shared_rail_reactions import guide_trace_bound, rotor_trace_and_rate


def test_integer_intervals_enclose_fraction_arithmetic_and_square_roots():
    a, b = _Interval(Fraction(1, 3)), _Interval(Fraction(2, 7))
    for interval, expected in ((a+b, Fraction(13, 21)), (a*b, Fraction(2, 21)),
                               (a/b, Fraction(7, 6)), (a-b, Fraction(1, 21))):
        assert Fraction(interval.lo, interval.SCALE) <= expected <= Fraction(interval.hi, interval.SCALE)
    root = _Interval(Fraction(2, 3)).sqrt()
    assert Fraction(root.lo, root.SCALE)**2 <= Fraction(2, 3) <= Fraction(root.hi, root.SCALE)**2
    with pytest.raises(ValueError, match="zero"):
        a/_Interval(-1, 1)


def test_exact_matrix_certificate_closes_its_invariant_bootstrap():
    result = matrix_certificate()
    assert result["exact_integer_interval_arithmetic"]
    for kind in ("heat", "invariant"):
        assert result["matrices"][kind]["accepted_boxes"] >= 256
        assert all(Fraction(x) > 0 for x in result["matrices"][kind]["minimum_negative_diagonal_and_determinant"])
    assert result["radius_error_upper"] < .01140
    assert result["radial_speed_upper"] < .00905
    assert result["reduced_input_upper"] < .006
    assert result["constitutive_rate_upper"] < .006


def test_trace_dual_norm_certificate_supplies_a_cold_start_l1_gain():
    result = input_l1_certificate()
    assert result["exact_integer_interval_arithmetic"]
    assert result["trace_dual_norm_upper"] == 1.13
    assert result["rotor_to_effective_network_l1_gain"] == 2.85
    for c, h, w, v in ((0., 1.08, -.012, -.012), (.5001, 1.32, .012, .012), (.2, 1.2, .004, -.01)):
        r = coupled_reduced_rhs(w, h*v, h, c, 0.)
        P = storage_matrix(c, h, kind="invariant")
        f = r["free_trace_coefficients"]
        assert f@np.linalg.solve(P, f) <= result["trace_dual_norm_upper"]**2


def test_coupled_reduction_matches_original_rotor_and_trace_equations():
    for w, y, h, c, n in ((.004, -.003, 1.2, .3, .001), (-.006, .005, 1.1, .49, -.0016)):
        got = coupled_reduced_rhs(w, y, h, c, n)
        x, v, heat = h+w, y/h, .01
        spin2 = 2*x*h*np.sqrt(1-v*v)-x*x-1-2*heat
        state = np.array([x, y, np.sqrt(spin2), heat])
        q = 18*got["rotor_input"]/ROTOR_RADIUS
        original = rotor_rhs(state, q, damping=DAMPING)
        expected = [ROTOR_RADIUS*original[0]-got["rotor_input"], ROTOR_RADIUS*original[1], got["rotor_input"]]
        assert_allclose(got["derivative"], expected, atol=4e-16)
        trace = rotor_trace_and_rate(state, q, damping=DAMPING)
        assert_allclose(got["trace_rate_per_inventory"], ROTOR_RADIUS*trace["trace_rate"]/18, atol=3e-16)
        assert_allclose(n, got["rotor_input"]+c*ROTOR_RADIUS*trace["trace_rate"]/18, atol=3e-16)


@pytest.mark.parametrize("kind", ["heat", "invariant"])
def test_parameter_derivatives_match_independent_storage_differentiation(kind):
    c, h, step = .31, 1.19, 1e-5
    pc, ph = storage_derivatives(c, h, kind=kind)
    assert_allclose(pc, (storage_matrix(c+step, h, kind=kind)-storage_matrix(c-step, h, kind=kind))/(2*step), atol=4e-11)
    assert_allclose(ph, (storage_matrix(c, h+step, kind=kind)-storage_matrix(c, h-step, kind=kind))/(2*step), atol=4e-11)


def test_heat_storage_bounds_exact_nonlinear_dissipation_with_changing_parameters():
    rng = np.random.default_rng(482)
    for _ in range(160):
        c, h = rng.uniform(0, C_MAX), rng.uniform(H_MIN, H_MAX)
        w, v, n, cd = rng.uniform(-.012, .012), rng.uniform(-.012, .012), rng.uniform(-N_MAX, N_MAX), rng.uniform(-.006, .006)
        y = h*v
        r = coupled_reduced_rhs(w, y, h, c, n)
        P, z = storage_matrix(c, h), np.array([w, y])
        pc, ph = storage_derivatives(c, h)
        derivative = 2*z@P@r["derivative"][:2]+z@(pc*cd+ph*r["rotor_input"])@z
        assert derivative+r["heat_rate"] <= HEAT_GAIN*n*n+1e-16


def test_fixed_partition_preserves_original_series_inventory_and_energy():
    T, M, m = np.array([4., 120.]), np.array([.7, 16.]), np.array([.006, .13])
    fractions = np.array([.17, .29, .54])
    original = series_state(T, M, m, dimension=2)
    parts = series_state(T[:, None]*fractions, M[:, None]*fractions, m[:, None]*fractions, dimension=2)
    assert_allclose(parts["total_energy"].sum(axis=1), original["total_energy"], rtol=3e-15)
    assert_allclose(parts["effective_tension"].sum(axis=1), original["effective_tension"], rtol=3e-15)
    assert_allclose(parts["core_energy_derivative"]+parts["joint_energy_derivative"],
                    np.broadcast_to((original["core_energy_derivative"]+original["joint_energy_derivative"])[:, None], (2, 3)), rtol=3e-15)


def test_continuous_constitutive_curvature_and_baseline_power_enclosures():
    T = np.array([[[4.], [5.], [8.]], [[100.], [130.], [110.]]])
    M, m = np.array([[.7], [16.]]), np.array([[.006], [.13]])
    dt = np.array([[1000.], [1200.]])
    bound = constitutive_panel_bounds(T, M, m, dt)
    for panel in range(2):
        rate = (T[:, panel+1]-T[:, panel])/dt[panel]
        for phase in (0., .27, .81, 1.):
            base = (1-phase)*T[:, panel]+phase*T[:, panel+1]
            for increment in (np.array([[0.], [0.]]), np.array([[.19], [.095]]), np.array([[.32], [.16]])):
                state = series_state(base+increment, M, m, dimension=2)
                step = 1e-4
                def slope(duty):
                    a = series_state(duty, M, m, dimension=2)
                    return a["core_energy_derivative"]+a["joint_energy_derivative"]
                curvature = (slope(base+increment+step)-slope(base+increment-step))/(2*step)
                assert np.all(abs(curvature) <= bound["curvature"][:, panel]+1e-10)
                before = slope(base)
                power = ((state["core_energy_derivative"]+state["joint_energy_derivative"]-before)*rate).sum(axis=0)
                assert np.all(abs(power) <= bound["baseline_power_upper"][panel]+1e-14)


def test_guide_trace_rate_envelope_covers_both_ramp_directions():
    bounds = guide_trace_rate_bounds()
    time = np.linspace(0, RAMP_TIME, 2001)
    for left, right in ((.001, 1.001), (1.001, .001)):
        actual = guide_trace_rate(inverse_guide(time, left, right))
        assert np.max(abs(actual)) <= bounds["peak"]


def test_added_finite_line_l2_bound_covers_a_resolved_fill_and_drain():
    old_edge = 2*(CONVERTER_DELAY*CONVERTER_NET_POWER/SPIN_FLOOR*2.1875/CONVERTER_RAMP)**2*(CONVERTER_RAMP+CONVERTER_DELAY)
    result = forcing_history_bounds(np.zeros((1, 1)), np.zeros((1, 1)), np.array([[old_edge]]), np.zeros(1), np.zeros(1))
    line = TwoDelayLine(SHORT_DELAY, 0., 300., peak=PHOTON_PEAK, pilot=PHOTON_PILOT)
    time = np.linspace(-.1, 557., 40001)
    rate = line.state(time)["energy_rate"]
    actual = np.trapezoid(rate*rate, time)
    assert actual <= result["finite_line_l2"][0, 0]
    assert result["events"][0, 0] == 1


def test_history_screen_preserves_an_exceeded_heat_bound():
    prep = preparation()
    kwargs = dict(original_energy_floor=prep["quasistatic_rotor_energy_floor"],
                  original_dynamic_energy=prep["initial_dynamic_energy"], guide_trace_bound=guide_trace_bound())
    result = history_result(np.array([[1e6]]), np.array([.9]), **kwargs)
    assert not result["spin_passed"][0, 0]
    assert result["spin_squared_lower"][0, 0] < 0
    with pytest.raises(ValueError, match="nonnegative"):
        history_result(np.array([[-1.]]), np.array([.9]), **kwargs)
