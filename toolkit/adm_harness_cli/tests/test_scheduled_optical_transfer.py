import numpy as np
import pytest
from numpy.testing import assert_allclose

from adm_harness.constitutive_joints_and_optics import ring_rhs, prepare_series_joints, series_panel_state
from adm_harness.distributed_reconfiguration import scheduled_replay
from adm_harness.scheduled_optical_transfer import (
    GUIDE_MASS, GUIDE_RADIUS, PILOT_POWER, RAMP_TIME, ROTOR_MASS, ROTOR_RADIUS, ROTOR_DAMPING,
    guide_bounds, guide_radius, inverse_guide, preparation, reflect_seed,
    rotor_optical_ports, rotor_rhs, rotor_state, schedule_exposure,
    simulate_transition, smooth_step,
    receipt_derivative_bound, delayed_receipt_l2_bound, frozen_thermal_gain,
)


def test_rotor_hamiltonian_matches_independent_worldsheet_legendre_transform():
    M, R, x, vr, omega = 2.1, .3, 1.17, .13, 1.9
    def lagrangian(v, o):
        return -M/2*((x+1/x)*np.sqrt(1-v*v)-x*R*R*o*o/np.sqrt(1-v*v))
    eps = 1e-6
    p = (lagrangian(vr+eps, omega)-lagrangian(vr-eps, omega))/(2*eps)
    J = (lagrangian(vr, omega+eps)-lagrangian(vr, omega-eps))/(2*eps)
    H = p*vr+J*omega-lagrangian(vr, omega)
    s = rotor_state([x, p/M, J/(M*R), 0.])
    assert_allclose(M*s["energy"], H, atol=3e-10)
    assert_allclose(s["radial_speed"], vr, atol=1e-10)
    assert_allclose(s["tangential_speed"], R*x*omega, atol=1e-10)


@pytest.mark.parametrize("power", [-.8, 0., .7])
def test_powered_rotor_counts_radial_work_torque_and_heat(power):
    y = np.array([1.2, -.04, .63, .02])
    eps = 1e-6
    grad = np.array([(rotor_state(y+eps*e)["energy"]-rotor_state(y-eps*e)["energy"])/(2*eps)
                     for e in np.eye(4)])
    rhs = rotor_rhs(y, power)
    assert_allclose(ROTOR_MASS*grad@rhs, power, atol=3e-9)
    assert rhs[3] >= 0
    ports = rotor_optical_ports(power, y[2])
    assert_allclose(ports["incoming"]-ports["outgoing"], power)
    assert_allclose(ports["incoming"]+ports["outgoing"], abs(power)/y[2])


def test_idle_rotor_holds_energy_without_incident_light_or_radial_motion():
    h = 1.3
    state = [h, 0., np.sqrt(h*h-1), 0.]
    assert_allclose(rotor_rhs(state, 0), 0, atol=2e-14)
    assert_allclose(rotor_state(state)["pressure_trace"], 0, atol=1e-14)
    assert_allclose(rotor_state(state)["proper_stretch"], h/np.sqrt(2-h*h))
    assert_allclose(rotor_optical_ports(0, state[2])["incoming"], 0)


@pytest.mark.parametrize("direction", [-1, 1])
def test_finite_reflected_pulse_conserves_energy_and_angular_momentum(direction):
    state = np.array([1.25, .04, .6, .01])
    initial = rotor_state(state)
    Ein = .03
    result = reflect_seed(state, Ein, direction=direction)
    Eout, new = result["outgoing_energy"], rotor_state(result["state"])
    assert_allclose(ROTOR_MASS*(new["energy"]-initial["energy"]), Ein-Eout, atol=4e-15)
    assert_allclose(result["angular_impulse_over_reference_radius"],
                    direction*state[0]*(Ein+Eout)/initial["gamma"], atol=3e-15)
    assert_allclose(new["radial_speed"], initial["radial_speed"])
    assert (Eout > Ein) == (direction == -1)


def test_septic_ramp_has_continuous_endpoint_power_and_three_flat_derivatives():
    f, d1, d2, d3 = smooth_step(np.array([-1., 0., 128., 129.]), 128.)
    assert_allclose(f, [0, 0, 1, 1])
    for d in (d1, d2, d3):
        assert_allclose(d, 0)
    for t, p in [(0., PILOT_POWER), (RAMP_TIME, 1+PILOT_POWER)]:
        g = inverse_guide(t, PILOT_POWER, 1+PILOT_POWER)
        assert_allclose(g["input_power"], p, atol=2e-14)
        assert_allclose(g["output_power"], p, atol=2e-14)


def test_inverse_guide_satisfies_original_equations_with_finite_acceleration():
    for t in [1.3, 21.7, 73.9, 120.5]:
        for a, b in [(PILOT_POWER, 1+PILOT_POWER), (1+PILOT_POWER, PILOT_POWER)]:
            g = inverse_guide(t, a, b)
            def state(time):
                r = inverse_guide(time, a, b)
                return np.array([r["radius"], r["momentum"], r["photon_action"]])
            dt = 1e-4
            derivative = (state(t+dt)-state(t-dt))/(2*dt)
            rhs = ring_rhs(state(t), g["input_power"]*GUIDE_RADIUS/GUIDE_MASS)[:3]/GUIDE_RADIUS
            assert_allclose(derivative, rhs, atol=2e-9)


def test_analytic_envelope_and_power_ceiling_cover_a_ramp_grid():
    b = guide_bounds()
    times = np.linspace(0, RAMP_TIME, 601)
    for a in [PILOT_POWER, .03, .2, .7, 1+PILOT_POWER]:
        for z in [PILOT_POWER, .03, .2, .7, 1+PILOT_POWER]:
            r = inverse_guide(times, a, z)
            eq = 2.5*(1-1/r["radius"]**2)
            assert np.max(abs(r["output_power"]-eq)) <= b["output_correction_bound"]
            assert r["input_power"].min() > 0
            assert r["input_power"].max() <= b["maximum_input_power"]
            assert r["energy"].max() <= b["maximum_energy"]
    assert b["output_envelope_margin"] > 0


def test_schedule_prices_preview_pilot_and_converter_exposure_for_zero_and_live_nodes():
    P = np.array([[[0.], [1.], [.2]], [[0.], [0.], [0.]]])
    r = schedule_exposure(P, np.array([[1.], [0.]]), np.full((3, 1), 1000.), np.ones(1))
    assert_allclose(r["useful_upper"][:, 0], [0, 1000, 1200])
    assert np.all(r["guide_upper"] > r["useful_upper"])
    assert np.all(np.diff(r["total_exposure_upper"], axis=0) > 0)
    assert_allclose(r["changed_plateaus"][:, 0], [3, 0])
    assert r["bootstrap_upper"][0, 0] > 0  # Prepares the upcoming increase.
    p = preparation()
    assert p["quasistatic_heat_energy_capacity"] > .28
    assert p["candidate_preparation"] > p["initial_dynamic_energy"]


def test_scheduled_step_preserves_receipt_timing_and_counts_both_flight_paths():
    r = simulate_transition(0., 1., maximum_step=.15, output_step=.15)
    assert r["complete"]
    assert np.min(r["guide_output"]-r["required_receipt"]) > 0
    assert np.max(abs(r["rotor_energy_balance_error"])) < 2e-8
    assert np.max(abs(r["complete_ledger_error"])) < 2e-6
    assert r["thermal_energy"][-1] > 0
    assert r["proper_stretch"].min() > 1


def test_joint_power_derivative_enclosure_covers_independent_finite_differences():
    time = np.linspace(0, 1, 8)[:, None]
    target = np.stack([5+time, .3*np.sin(7*time), .2*np.cos(5*time)])
    lr, lt, dt = np.exp(.1*time), np.exp(-.2*time), np.diff(time, axis=0)
    replay = scheduled_replay(target, .02+0*time, .1+.03*time, .4+.1*time, dt)
    T, M = replay["material_tension"], replay["inventory"]
    m = prepare_series_joints(T, M)["joint_inventory_per_direction"]
    args = (T, M, m, replay["component_energy"][6:10], target, lr, lt, dt)
    bound = receipt_derivative_bound(*args)
    step = 1e-5
    for u in np.linspace(.01, .99, 21):
        derivative = (series_panel_state(*args, u+step)["power"]
                      -series_panel_state(*args, u-step)["power"])/(2*step*dt)
        assert np.max(abs(derivative)-bound) < 1e-8


def test_delayed_receipt_quadratic_bound_covers_jumps_and_smooth_interiors():
    dt, delta = np.array([[3.], [2.], [4.]]), np.array([.2])
    left = np.array([[[0.2], [.8], [.1]]])
    right = np.array([[[.5], [.6], [.3]]])
    derivative = abs(right-left)/dt
    bound = delayed_receipt_l2_bound(left, right, derivative, np.ones((1, 1)), dt, delta)
    def demand(time):
        result = np.zeros_like(time)
        starts = np.array([0, 3, 5])
        for i, start in enumerate(starts):
            active = (time >= start) & (time < start+dt[i, 0])
            result[active] = left[0, i, 0]+(right[0, i, 0]-left[0, i, 0])*(time[active]-start)/dt[i, 0]
        return result
    t = np.linspace(-1, 10, 110001)
    value = np.trapezoid((demand(t)-demand(t-delta[0]))**2, t)/delta[0]
    assert value <= bound[0, -1, 0]


def test_invalid_spin_missing_seed_and_overlapping_schedule_are_rejected():
    with pytest.raises(ValueError):
        rotor_state([1, 0, 1., 0])
    with pytest.raises(ValueError):
        reflect_seed([1.2, 0, .6, 0], 0.)
    with pytest.raises(ValueError):
        schedule_exposure(np.ones((1, 2, 1)), np.ones((1, 1)), np.ones((2, 1)), np.ones(1))


@pytest.mark.parametrize("damping", [.2, .4, 2.])
def test_frozen_heat_gain_bounds_frequency_response_of_linearized_rotor(damping):
    h = 1.2
    omega = np.r_[0., np.geomspace(1e-5, 1e5, 10000)]
    z = 1j*omega
    # v/q from w'=v/R-q/M and v'=-w/(h²R)-k*v/R.
    transfer = (1/(ROTOR_MASS*h*h*ROTOR_RADIUS))/(
        z*z+damping/ROTOR_RADIUS*z+1/(h*h*ROTOR_RADIUS**2))
    heat_gain = ROTOR_MASS*damping*h/ROTOR_RADIUS*abs(transfer)**2
    ceiling = frozen_thermal_gain(h, damping=damping)
    assert heat_gain.max() <= ceiling*(1+1e-12)
    assert heat_gain.max() >= ceiling*.99999
