import numpy as np
import pytest
from numpy.testing import assert_allclose

from adm_harness.constitutive_joints_and_optics import ring_equilibrium, ring_rhs, ring_state
from adm_harness.controlled_optical_transfer import (
    dispatch_power, regulator_command, sampled_control_modes, simulate_transfer,
    square_demand_integral, transfer_envelope,
)


def test_preparation_counts_both_paths_guide_and_a_positive_receiver_floor():
    peak, delay = np.array([0., 2., 3.]), np.array([1., 4., 2.])
    prep = transfer_envelope(peak, delay)
    C = peak*delay
    assert_allclose(prep["guide_reference_inventory"], (10/3)*C)
    assert_allclose(prep["prepared_energy"], (23/3)*C)
    assert_allclose(prep["nominal_path_energy"], C)
    assert_allclose(prep["initial_buffer"]+prep["nominal_path_energy"]+prep["nominal_guide_energy"], prep["prepared_energy"])
    worst = (prep["prepared_energy"]-prep["guide_energy_ceiling"]-C
             -prep["feed_path_energy_ceiling"]-prep["output_path_energy_ceiling"])
    assert_allclose(worst, prep["buffer_floor"])


def test_tensile_energy_envelope_bounds_the_actual_outgoing_photon_flux():
    rng = np.random.default_rng(842)
    x = rng.uniform(1, 1.5, 500)
    material = .5*(x+1/x)
    photons = rng.uniform(size=x.shape)*(1.4-material)
    momentum = rng.uniform(-1, 1, x.shape)*np.sqrt(1.4**2-(material+photons)**2)
    state = ring_state(x, momentum, x*photons)
    assert np.max(state["energy"]) <= 1.4+1e-14
    actual = photons/(2*np.pi*x)
    assert np.max(actual) < (1.4-1)/(2*np.pi)
    assert_allclose((1.4-1)/(2*np.pi), 2*ring_equilibrium(.4)["input_power"])


def test_dispatch_routes_every_request_and_conserves_the_arriving_light():
    demand, arriving = np.array([0., 1., 4., 2.]), np.array([2., 4., 1., 2.])
    result = dispatch_power(demand, arriving)
    assert_allclose(result["direct"]+result["recycle"], arriving)
    assert_allclose(result["direct"]+result["bypass"], demand)
    assert_allclose(result["recycle"]-result["bypass"], arriving-demand)


def test_square_transfer_starts_and_drains_with_bounded_external_transit():
    time = np.linspace(-3, 20, 1001)
    energy = square_demand_integral(time, 2., 1.5, 12.)
    transit = energy-square_demand_integral(time-2., 2., 1.5, 12.)
    assert np.min(transit) >= -1e-13
    assert np.max(transit) <= 4+1e-13
    assert_allclose(energy[time < 0], 0.)
    assert_allclose(energy[time >= 12], 12.)
    assert_allclose(transit[time >= 14], 0.)


def test_steady_loading_meets_resonant_demand_without_driving_ring_motion():
    result = simulate_transfer(demand_intervals=6, half_period=3.8238248063636506)
    state, history = result["ring"], result["history"]
    expected = np.broadcast_to(result["equilibrium"]["state"][:, None], history[:3].shape)
    assert result["complete"]
    assert_allclose(history[:3], expected, atol=2e-13)
    assert_allclose(state["pressure_trace"], 0, atol=2e-13)
    assert_allclose(result["dispatch"]["delivered"], result["useful_power"])
    assert_allclose(result["useful_energy"][-1], result["requested_useful_energy"])
    assert_allclose(result["external_inflight_energy"][-1], 0, atol=1e-14)
    assert_allclose(result["ledger_energy"], result["envelope"]["prepared_energy"], atol=3e-12)
    assert np.min(result["buffer_energy"]) >= result["envelope"]["buffer_floor"]


def test_sampled_plant_and_feedback_jacobians_match_independent_differences():
    eq = ring_equilibrium(.4)
    initial = np.r_[eq["state"], eq["input_power"]]
    def rhs(y):
        return np.r_[ring_rhs(y[:3], y[3])[:3], (eq["input_power"]-y[3])/.25]
    h = 1e-6
    jacobian = np.column_stack([(rhs(initial+h*np.eye(4)[i])-rhs(initial-h*np.eye(4)[i]))/(2*h) for i in range(4)])
    for mode in ("constant", "feedback", "aggressive"):
        sampled = sampled_control_modes(mode=mode, momentum_gain=-.05)
        assert_allclose(jacobian, sampled["continuous_matrix"], atol=1e-9)
        feedback = np.array([(regulator_command(initial+h*np.eye(4)[i], mode=mode, momentum_gain=-.05)
                             -regulator_command(initial-h*np.eye(4)[i], mode=mode, momentum_gain=-.05))/(2*h) for i in range(4)])
        assert_allclose(feedback, sampled["command_derivative"], atol=1e-9)


def test_sampled_delay_modes_select_stable_phase_adjustment_and_reject_aggressive_law():
    passive = sampled_control_modes()
    controlled = sampled_control_modes(mode="feedback", momentum_gain=-.05)
    aggressive = sampled_control_modes(mode="aggressive")
    assert controlled["spectral_radius"] < passive["spectral_radius"] < 1
    assert aggressive["spectral_radius"] > 1
    # With zero feedback the delayed registers add zero eigenvalues only.
    nonzero = passive["eigenvalues"][abs(passive["eigenvalues"]) > 1e-10]
    expected = np.exp(np.linalg.eigvals(passive["continuous_matrix"])*3*np.pi/20)
    assert_allclose(np.sort_complex(nonzero), np.sort_complex(expected), atol=2e-14)


def test_controller_cannot_change_ring_input_before_signal_and_power_flights():
    result = simulate_transfer(mode="feedback", initial_radius_fraction=.02,
        initial_momentum=.01, initial_action_fraction=-.02, momentum_gain=-.05, demand_intervals=8)
    q0 = result["equilibrium"]["input_power"]
    before = result["time"] < 3*np.pi-1e-10
    assert_allclose(result["input_power"][before], q0, atol=1e-14)
    assert np.max(abs(result["input_power"][~before]-q0)) > 1e-5
    assert_allclose(result["ledger_energy"], result["envelope"]["prepared_energy"], atol=2e-9)
    assert np.min(result["buffer_energy"]) > result["envelope"]["buffer_floor"]


def test_invalid_preparation_and_noninteger_delay_are_rejected():
    with pytest.raises(ValueError):
        transfer_envelope(-1, 1)
    with pytest.raises(ValueError):
        transfer_envelope(1, 1, energy_cap=1.1)
    with pytest.raises(ValueError):
        sampled_control_modes(total_flight_delay=.7, sample_period=.3)
    with pytest.raises(ValueError):
        simulate_transfer(initial_radius_fraction=-.5)
