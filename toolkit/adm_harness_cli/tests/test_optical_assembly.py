import numpy as np
import pytest
from numpy.testing import assert_allclose
from scipy.integrate import quad

from adm_harness.constitutive_joints_and_optics import ring_state
from adm_harness.controlled_optical_transfer import transfer_envelope
from adm_harness.optical_assembly import (
    assembly_energy_screen, loss_budget, polygon_reactions, simulate_store,
    splitter_matrix, store_rhs, switched_demand,
)


def test_splitter_conserves_arbitrary_two_input_amplitudes_at_each_phase():
    rng = np.random.default_rng(1709)
    U = splitter_matrix(np.linspace(-4, 7, 301))
    light = rng.normal(size=(301, 2))+1j*rng.normal(size=(301, 2))
    outgoing = np.einsum("nij,nj->ni", U, light)
    assert_allclose(np.sum(abs(outgoing)**2, axis=1), np.sum(abs(light)**2, axis=1), atol=2e-14)
    assert_allclose(abs(splitter_matrix([0, np.pi])[:, :, 0])**2, [[1, 0], [0, 1]], atol=1e-14)


@pytest.mark.parametrize("transition", [0., .17, .7])
def test_finite_phase_demand_has_exact_integral_and_bounded_transit(transition):
    opts = dict(half_period=.7, intervals=8, transition=transition)
    for t in [.13, .66, .74, 1.17, 1.53, 5.83]:
        cuts = sorted(set([0, t]+[a for k in range(9) for a in [k*.7, k*.7+transition] if 0 < a < t]))
        numerical = sum(quad(lambda s: switched_demand(s, **opts)[0], a, b, epsabs=2e-12)[0]
                        for a, b in zip(cuts[:-1], cuts[1:]))
        assert_allclose(switched_demand(t, **opts)[1], numerical, atol=1e-12)
    t = np.linspace(-1, 7, 1001)
    p, E = switched_demand(t, **opts)
    transit = E-switched_demand(t-1, **opts)[1]
    assert np.all((p >= 0) & (p <= 1))
    assert transit.min() >= -1e-13
    assert transit.max() <= 1+1e-13
    assert_allclose(E[-1], 2.8)
    assert_allclose(transit[-1], 0)


def test_constitutive_store_power_identity_independent_energy_gradient():
    M, radius = 8., .07
    for state, power in [(np.array([1.2, .03, .31]), .7), (np.array([1.31, -.1, .19]), -.8)]:
        eps = 1e-6
        gradient = np.array([(ring_state(*(state+eps*v))["energy"]
                              -ring_state(*(state-eps*v))["energy"])/(2*eps) for v in np.eye(3)])
        derivative = store_rhs(state, power, inventory=M, reference_radius=radius)
        assert_allclose(M*gradient@derivative, power, atol=2e-9)


def test_adequate_energy_capacity_does_not_prevent_store_resonance():
    result = simulate_store(intervals=16)
    assert result["quasistatic_energy_floor"] > result["reference_inventory"]
    assert not result["complete"]
    assert result["boundary"] == "tensile"
    assert 5 < result["time"][-1] < 6
    assert_allclose(result["state"][0, -1], 1, atol=1e-12)
    assert np.max(abs(result["balance_error"])) < 2e-8


def test_smaller_store_completes_the_same_finite_trial_with_counted_energy():
    result = simulate_store(reference_radius=1/(12*np.pi), intervals=16)
    assert result["complete"]
    assert np.max(abs(result["balance_error"])) < 2e-8
    assert result["extraction_depth"].max() < 1
    assert_allclose(result["inflight"][-1], 0, atol=1e-14)
    assert_allclose(result["energy"][-1], result["initial_energy"], atol=2e-8)
    # Circulation is a physical loss multiplier, even when the ports balance.
    assert result["circulating_power"].min() > 1


def test_polygon_balances_local_turns_and_full_stress_in_three_dimensions():
    vertices = np.array([[0., 0., 0.], [1.2, .2, .4], [1., 1., .7], [-.3, .4, .2]])
    result = polygon_reactions(vertices, power=2.3, stretch=1.5)
    assert_allclose(result["net_force"], 0, atol=1e-14)
    assert_allclose(result["net_torque"], 0, atol=1e-14)
    assert np.linalg.norm(result["vertex_force"], axis=1).min() > 0
    assert_allclose(result["wall_tensor"]+result["photon_tensor"], 0, atol=3e-14)
    assert_allclose(np.trace(result["photon_tensor"]), result["photon_energy"])
    assert_allclose(result["wall_energy"], 2.6*result["photon_energy"])
    shifted = polygon_reactions(vertices+np.array([3, -2, .7]), power=2.3)
    assert_allclose(shifted["wall_tensor"], result["wall_tensor"], atol=2e-14)


def test_store_replacement_counts_rest_inventory_and_avoids_charging_old_buffer_twice():
    C = np.array([0., 1., 2.])
    old = transfer_envelope(C, 1.)
    result = assembly_energy_screen(C, old["prepared_energy"], old["initial_buffer"])
    assert_allclose(result["candidate_preparation"],
                    old["nominal_guide_energy"]+old["nominal_path_energy"]
                    +result["store_energy"]+result["route_wall_energy"])
    assert_allclose(result["route_wall_energy"], 7.15*C)
    assert_allclose(result["store_energy"], 8/np.sqrt(.6)*C)


def test_loss_screen_counts_circulation_and_drive_and_separates_export_requirement():
    result = loss_budget(2., 10., circulation_multiple=4., round_trip_loss=.03,
                         splitter_unrecovered=.1, drive_energy=.3)
    assert_allclose(result["retained_energy"], 2.5)
    assert_allclose(result["remaining_reserve"], -.5)
    assert_allclose(result["conditional_heat_removal_fraction"], .2)
    assert_allclose(result["required_replacement_energy"], 2.5)
    assert_allclose(result["effective_loss_ceiling"], .17)
    assert np.isinf(loss_budget(2., 0.)["effective_loss_ceiling"])


def test_invalid_domains_fail_before_integration():
    with pytest.raises(ValueError):
        simulate_store(intervals=3)
    with pytest.raises(ValueError):
        simulate_store(reference_radius=1.)
    with pytest.raises(ValueError):
        polygon_reactions(np.zeros((4, 3)))
    with pytest.raises(ValueError):
        assembly_energy_screen(1, 1, 2)
