import numpy as np
import pytest
from numpy.testing import assert_allclose
from scipy.integrate import solve_ivp

from adm_harness.constitutive_joints_and_optics import (
    panel_reserve_lower_bound, prepare_series_joints, ring_equilibrium, ring_rhs, ring_state,
    series_panel_state, series_power_bounds, series_state,
)
from adm_harness.distributed_reconfiguration import scheduled_replay
from adm_harness.material_reconfiguration import MATERIAL_DIMENSIONS, PRESSURE_BASIS, elastic_state_from_tension


def test_uniform_string_splice_recovers_one_continuous_constitutive_law():
    alpha, M = .07, .03
    loads = np.r_[0., np.geomspace(1e-7, 3, 90)]
    state = series_state(loads, M, alpha*M, reference_fraction=alpha)
    whole = elastic_state_from_tension(loads, (1+alpha)*M)
    assert_allclose(state["total_energy"], whole["energy"], rtol=2e-13)
    assert_allclose(state["cell_linear_stretch"], whole["strain"], rtol=3e-12)
    assert_allclose(state["joint_stretch"], state["core_linear_stretch"], rtol=3e-12)


@pytest.mark.parametrize("dimension", [1, 2])
def test_series_force_geometry_and_virtual_work(dimension):
    T = np.geomspace(.0001, .5, 70)
    M, m, alpha = .02, .001, .003
    state = series_state(T, M, m, dimension=dimension, reference_fraction=alpha)
    assert_allclose(state["effective_tension"], T, atol=2e-14)
    f = state["core_tension"]/state["core_linear_stretch"]
    assert_allclose(state["joint_tension"]/(alpha*state["joint_stretch"]), f, rtol=2e-13)
    assert_allclose(.5*m*(state["joint_stretch"]-1/state["joint_stretch"]),
                    state["joint_tension"], atol=1e-15)
    assert_allclose(state["core_energy_derivative"]+state["joint_energy_derivative"],
                    dimension*T*state["cell_log_derivative"], rtol=2e-13)
    h = 1e-5
    plus = series_state(T*np.exp(h), M, m, dimension=dimension, reference_fraction=alpha)
    minus = series_state(T*np.exp(-h), M, m, dimension=dimension, reference_fraction=alpha)
    derivative = (plus["total_energy"]-minus["total_energy"])/(2*h*T)
    assert_allclose(derivative, state["core_energy_derivative"]+state["joint_energy_derivative"], rtol=3e-7)


def test_prepared_joint_inventories_bound_stretch_and_count_unloaded_directions():
    rng = np.random.default_rng(404)
    tension = rng.uniform(0, 1, (6, 25, 3))
    tension[0] = 0.
    M = rng.uniform(.001, .01, (6, 3))
    result = prepare_series_joints(tension, M)
    state, m = result["state"], result["joint_inventory_per_direction"]
    assert state["joint_stretch"].max() <= 2+1e-13
    assert np.all(m > 0)
    assert_allclose(state["total_energy"][0], np.broadcast_to((M[0]+2*m[0]), (25, 3)))
    assert_allclose(result["total_joint_reference_energy"], (MATERIAL_DIMENSIONS[:, None]*m).sum(axis=0))


def test_series_power_intervals_cover_independently_evaluated_panel_states():
    time = np.linspace(0, 1, 8)[:, None]
    target = np.stack([5+time, .3*np.sin(7*time), .2*np.cos(5*time)])
    lr, lt, dt = np.exp(.1*time), np.exp(-.2*time), np.diff(time, axis=0)
    replay = scheduled_replay(target, .02+0*time, .1+.03*time, .4+.1*time, dt)
    T, M = replay["material_tension"], replay["inventory"]
    prep = prepare_series_joints(T, M)
    m = prep["joint_inventory_per_direction"]
    fields = replay["component_energy"][6:10]
    bound = series_power_bounds(T, M, m, fields, target, lr, lt, dt)
    dz, da = np.diff(np.log(lr), axis=0)/dt, np.diff(np.log(lt), axis=0)/dt
    work = PRESSURE_BASIS[0, :6, None, None]*dz+PRESSURE_BASIS[1, :6, None, None]*da
    dT = np.diff(T, axis=1)/dt
    for u in np.linspace(0, 1, 41):
        state = series_state((1-u)*T[:, :-1]+u*T[:, 1:], M[:, None], m[:, None],
                             dimension=MATERIAL_DIMENSIONS[:, None, None])
        core = state["core_energy_derivative"]*dT+state["core_tension"]*work
        joint = state["joint_energy_derivative"]*dT+state["joint_tension"]*work
        material = np.concatenate([core, joint])
        assert np.max(material-bound["upper"][:12]) < 1e-12
        assert np.max(bound["lower"][:12]-material) < 1e-12
        actual = series_panel_state(T, M, m, fields, target, lr, lt, dt, u)["power"]
        assert np.max(actual-bound["upper"]) < 1e-12
        assert np.max(bound["lower"]-actual) < 1e-12
        assert_allclose(actual.sum(axis=0), 0, atol=2e-14)


def test_derivative_envelope_covers_interior_minimum_and_exact_affine_reserves():
    # r(t)=(t-.5)^2+.1 has equal endpoints and a lower interior reserve.
    r = np.array([[.35], [.35]])
    bound = panel_reserve_lower_bound(r, np.ones((1, 1)), np.array([[-1.]]), np.array([[1.]]))
    assert_allclose(bound, -.15)
    for rate in (-.2, 0., .2):
        endpoints = np.array([[1.], [1+rate]])
        exact = panel_reserve_lower_bound(endpoints, np.ones((1, 1)), np.full((1, 1), rate), np.full((1, 1), rate))
        assert_allclose(exact, endpoints.min())


def test_optical_ring_open_ports_obey_energy_balance_with_radial_momentum():
    rng = np.random.default_rng(998)
    for _ in range(50):
        y = np.array([rng.uniform(1, 1.5), rng.uniform(-.2, .2), rng.uniform(.01, .4)])
        power = rng.uniform(0, .05)
        rhs = ring_rhs(y, power)
        h = 1e-6
        gradient = np.array([(ring_state(*(y+h*np.eye(3)[i]))["energy"]
                             -ring_state(*(y-h*np.eye(3)[i]))["energy"])/(2*h) for i in range(3)])
        assert_allclose(gradient @ rhs[:3], rhs[3], atol=5e-11)
        assert abs(ring_state(*y)["speed"]) < 1


@pytest.mark.parametrize("fraction", [.05, .25, .4, .8])
def test_ring_equilibrium_and_linear_modes_match_the_analytic_stability_polynomial(fraction):
    equilibrium = ring_equilibrium(fraction)
    y, power = equilibrium["state"], equilibrium["input_power"]
    assert_allclose(ring_rhs(y, power), 0., atol=2e-16)
    assert abs(ring_state(*y)["pressure_trace"]) < 1e-14
    h = 1e-6
    jacobian = np.column_stack([(ring_rhs(y+h*np.eye(3)[i], power)[:3]
                                -ring_rhs(y-h*np.eye(3)[i], power)[:3])/(2*h) for i in range(3)])
    actual = np.sort_complex(np.linalg.eigvals(jacobian))
    assert_allclose(actual, np.sort_complex(equilibrium["eigenvalues"]), atol=3e-10)
    assert actual.real.max() < 0


def test_closed_ring_conserves_energy_and_open_step_counts_kinetic_energy():
    initial = ring_equilibrium(.25)["state"]
    initial[1] = .01
    closed = solve_ivp(lambda t, y: ring_rhs(y, 0., escape_depth=0.)[:3], (0, 40), initial,
                       method="DOP853", rtol=1e-10, atol=1e-12, max_step=.2)
    states = ring_state(*closed.y)
    assert_allclose(states["energy"], states["energy"][0], atol=2e-11)
    assert closed.y[0].min() > 1
    start = ring_equilibrium(.25)["state"]
    driven = solve_ivp(lambda t, y: ring_rhs(y, ring_equilibrium(.4)["input_power"]),
                       (0, 100), np.r_[start, 0.], method="DOP853", rtol=1e-10, atol=1e-12, max_step=.25)
    state = ring_state(*driven.y[:3])
    assert state["kinetic_energy"].max() > 1e-6
    assert_allclose(state["energy"]-ring_state(*start)["energy"], driven.y[3], atol=3e-11)


def test_invalid_material_and_steady_overload_are_rejected():
    with pytest.raises(ValueError):
        series_state(1., 0., .1)
    with pytest.raises(ValueError):
        ring_equilibrium(1.)
    with pytest.raises(ValueError):
        ring_equilibrium(1.01)
