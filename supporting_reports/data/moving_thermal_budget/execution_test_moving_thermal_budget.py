import numpy as np
from numpy.testing import assert_allclose

from adm_harness.coupled_holding_certificate import C_MAX
from adm_harness.coupled_optical_losses import ROTOR_L1_GAIN
from adm_harness.finite_thermal_budget import finite_heat_closure, finite_heat_history
from adm_harness.moving_thermal_budget import moving_heat_closure, moving_heat_history
from adm_harness.moving_thermal_relay import selected_route_bounds


def test_stationary_relays_recover_matched_finite_heat_law():
    new, old = moving_heat_closure(maximum_speed=0), finite_heat_closure()
    for key in ("passive_heat_gain", "feedback_denominator", "port_l1_gain",
                "port_power_peak", "additional_state_energy_ceiling"):
        assert_allclose(new[key], old[key], rtol=3e-16)
    assert new["work_flight_energy_ceiling"] == new["remote_work_net_power_peak"] == 0
    L1, L2 = np.array([[100., 200.], [60., 25.]]), np.array([[12., 16.], [6., 4.]])
    low, high, peak = np.array([1.1, 1.11]), np.array([1.3, 1.31]), np.array([.0015, .0016])
    new = moving_heat_history(L1, L2, low, high, peak, maximum_speed=0)
    old = finite_heat_history(L1, L2, low, high, peak)
    for key in ("spin_squared_lower", "damping_action_upper", "absorption_action_upper"):
        assert_allclose(new[key], old[key], rtol=3e-15)


def test_moving_feedback_fixed_point_includes_work_lead_photons():
    b = moving_heat_closure()
    incoming = 250.
    q = 0.
    # Independently iterate the two absolute-work inequalities.
    for _ in range(12):
        heat_difference = b["arriving_heat_l1_per_port_l1"]+b["passive_heat_gain"]
        q = ROTOR_L1_GAIN*(incoming+(1+C_MAX)*b["total_flight_rate_l1_per_port_l1"]*q)+heat_difference*q
    assert_allclose(q, b["port_l1_gain"]*incoming, rtol=3e-15)
    stationary = moving_heat_closure(maximum_speed=0)
    assert b["port_l1_gain"] > stationary["port_l1_gain"]
    assert b["additional_state_energy_ceiling"] > stationary["additional_state_energy_ceiling"]
    assert b["remote_work_incident_power_peak"] > 0


def test_zero_absorption_removes_both_thermal_and_reflector_work_paths():
    b = moving_heat_closure(absorption=0)
    assert b["port_l1_gain"] == ROTOR_L1_GAIN
    for key in ("thermal_flight_energy_ceiling", "work_flight_energy_ceiling",
                "total_flight_rate_peak", "remote_work_net_power_peak"):
        assert b[key] == 0


def test_shared_budget_uses_the_selected_geometric_route_bounds():
    b = moving_heat_closure()
    route = selected_route_bounds(b["maximum_actuator_gap"])
    scale = b["passive_heat_gain"]*b["port_power_peak"]
    assert_allclose(b["total_extra_flight_energy_ceiling"]/scale,
                    route["complete_flight_energy_per_emitted_peak"], rtol=3e-15)
    assert_allclose(b["total_flight_rate_peak"]/scale,
                    route["complete_flight_rate_peak_per_emitted_peak"], rtol=3e-15)
    assert_allclose(b["total_flight_rate_l1_per_port_l1"]/b["passive_heat_gain"],
                    route["complete_flight_rate_l1_per_emitted_energy"], rtol=3e-15)
