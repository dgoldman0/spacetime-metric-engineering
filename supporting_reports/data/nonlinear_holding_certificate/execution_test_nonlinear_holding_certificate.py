import numpy as np
import pytest
from numpy.testing import assert_allclose

from adm_harness.nonlinear_holding_certificate import (
    H_MIN, H_MAX, P_INVARIANT, P_THERMAL, THERMAL_GAIN,
    guide_input_certificate, history_certificate, rational_certificate, reduced_rhs, spin_squared,
)
from adm_harness.scheduled_optical_transfer import (
    PILOT_POWER, RAMP_TIME, ROTOR_MASS, ROTOR_RADIUS,
    inverse_guide, rotor_rhs, rotor_state,
)


def test_exact_reduction_matches_full_material_heat_and_torque_equations():
    for state in ([1.2, .003, .61, .02], [1.25, -.006, .65, .03], [1.3, 0, np.sqrt(.69-2e-8), 1e-8]):
        x, p, j, b = state
        h = rotor_state(state)["energy"]
        for q in (-1., 0., .7):
            original = rotor_rhs(state, q)*ROTOR_RADIUS
            u = ROTOR_RADIUS*q/ROTOR_MASS
            result = reduced_rhs([x-h, p, h, b, u])
            assert_allclose(result, [original[0]-u, original[1], u, original[3]], atol=2e-15)
            assert_allclose(spin_squared(x-h, p, h, b), j*j, atol=8e-16)


def test_rational_vertex_certificate_and_nonlinear_dissipation_on_random_states():
    proof = rational_certificate()
    assert len(proof["vertices"]) == 8
    rng = np.random.default_rng(1907)
    for _ in range(1000):
        h, w, v, u = rng.uniform(H_MIN, H_MAX), rng.uniform(-.012, .012), rng.uniform(-.012, .012), rng.uniform(-.00155, .00155)
        z = np.array([w, h*v])
        dz = reduced_rhs([w, h*v, h, .001, u])
        assert 2*z@P_THERMAL@dz[:2]+dz[3] <= THERMAL_GAIN*u*u+2e-18
        # The invariant inequality uses the bounded input separately.
        autonomous = dz[:2]+np.array([u, 0.])
        assert 2*z@P_INVARIANT@autonomous <= -2*.175*(z@P_INVARIANT@z)+2e-18


def test_guide_input_bound_covers_all_endpoint_pairs_and_the_pilot_tail():
    bound = guide_input_certificate()
    t = RAMP_TIME*np.unique(np.r_[np.linspace(0, 1, 201), 1-np.geomspace(1e-9, .1, 101)])
    for left in np.linspace(PILOT_POWER, 1+PILOT_POWER, 9):
        for right in np.linspace(PILOT_POWER, 1+PILOT_POWER, 9):
            g = inverse_guide(t, left, right)
            assert g["input_power"].min() >= bound["input_power_lower_bound"]
    assert bound["input_power_lower_bound"] > .0009


def test_thermal_margin_requires_prepared_initial_state_and_rejects_excess_drive():
    good = history_certificate(np.array([0., 260.]))
    assert good["passed"].all()
    assert good["radius_minimum"] > 1
    assert good["spin_upper_squared"] < 1
    assert not history_certificate(np.array([1000.]))["passed"].all()
    with pytest.raises(ValueError):
        history_certificate(np.array([1.]), initial_error=(.1, 0.))
