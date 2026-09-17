import numpy as np
from numpy.testing import assert_allclose
from scipy.integrate import solve_ivp

from adm_harness.coupled_holding_certificate import C_MAX, ISS_DECAY
from adm_harness.prepared_transfer_budget import (
    apply_pilot_preparation, cold_preparation, thermal_endpoint_perturbation,
)
from adm_harness.reaction_endpoint_certificate import (
    CHI_UPPER, LINE_RATE_GAIN, WEIGHTED_TRACE_DUAL,
)
from adm_harness.scheduled_optical_transfer import ROTOR_RADIUS, preparation, rotor_state


def test_prepared_main_photons_preserve_total_energy_and_radial_equilibrium():
    A, B = np.meshgrid(np.linspace(0, 1, 11), np.array([0., .0062, .1]))
    for mass in (19., 20.):
        result = cold_preparation(A, B, inventory=mass)
        state = rotor_state(np.array([result["radius"], result["momentum"],
                                      result["spin"], result["thermal_action"]]))
        assert_allclose(state["energy"], result["energy"], atol=3e-16)
        assert_allclose(result["counted_dynamic_energy"],
                        preparation(inventory=mass)["initial_dynamic_energy"], atol=4e-15)
        assert_allclose(1+result["spin"]**2+2*result["thermal_action"]-result["radius"]**2,
                        0, atol=4e-16)
        unfilled = cold_preparation(A, 0, inventory=mass)
        assert_allclose(mass*(unfilled["energy"]-result["energy"]),
                        result["main_converter_flight_energy"], atol=5e-15)


def test_uniform_thermal_increment_encloses_driven_tracking_comparison():
    bound = thermal_endpoint_perturbation()
    X = bound["thermal_flight_derivative_peak"]
    def drive(t):
        return X*(.7+.3*np.sin(13*t))
    result = solve_ivp(lambda t, y: -ISS_DECAY/ROTOR_RADIUS*y+
        CHI_UPPER*(1+C_MAX)/ROTOR_RADIUS*drive(t), (0, 12), [0.],
        max_step=.004, rtol=1e-10, atol=1e-14, dense_output=True)
    t = np.linspace(0, 12, 3001)
    state = result.sol(t)[0]
    support = WEIGHTED_TRACE_DUAL*state+LINE_RATE_GAIN*drive(t)
    assert state.max() < bound["tracking_comparison_increment"]
    assert support.max() < bound["support_power_increment"]
    assert thermal_endpoint_perturbation(absorption=0)["incident_margin_debit"] == 0.


def test_revised_floor_preserves_the_separate_heat_and_motion_penalty():
    old_floor = np.array([1.10, 1.12])
    heat, motion = np.array([[.012, .018], [.015, .020]]), .0004
    old_spin2 = old_floor**2-1-2*heat-motion
    cold_floor = old_floor+np.array([[.0001], [.0002]])
    result = apply_pilot_preparation(old_floor, old_spin2, cold_floor, 1.316,
                                    thermal_state_ceiling=1e-7, inventory=19.)
    assert_allclose(result["spin_squared_lower"],
                    result["energy_floor"]**2-1-2*heat-motion, rtol=2e-15)
