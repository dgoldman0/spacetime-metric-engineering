import numpy as np
import pytest
from numpy.testing import assert_allclose
from scipy.optimize import linprog

from adm_harness.containment_ensemble import required_exchange
from adm_harness.finite_containment import annular_factor
from adm_harness.material_reconfiguration import (
    MATERIAL_DIMENSIONS, configuration_coordinates, configuration_rate_bound, elastic_replay,
    elastic_state_from_strain, elastic_state_from_tension, finite_ideal_allocation,
    inventory_for_minimum_stretch, isometric_pool_bounds, isometric_pool_program, reciprocal_routes,
)


def finite_component_program(target, floor, hi, ho, eta):
    basis = np.array([[1., 1., 1., 1., 1., 1., 1., 1., 1., 1., 1.],
                      [-1., 0., -1., 0., 0., 1., -1., 1., 0., 0., 0.],
                      [-.5, -.5, -.5, -.5, -1., 0., 1., 0., .5, -1., 0.]])
    eq = np.zeros((6, 11)); eq[:3] = basis
    eq[3, :2] = 1
    eq[4, 2:5] = [1, 1, 2]
    eq[5, 4:6] = [1, -annular_factor(eta)]
    c = np.zeros(11); c[-1] = -1
    return linprog(c, A_eq=eq, b_eq=[*target, hi, ho, 0.],
        bounds=[(0, None)]*6+[(floor, None)]+[(0, None)]*3+[(None, None)], method="highs")


@pytest.mark.parametrize("eta", [1.01, 1.4])
def test_finite_minimax_agrees_with_independent_component_program(eta):
    rng = np.random.default_rng(515)
    for _ in range(60):
        T = np.r_[rng.uniform(.5, 4), rng.uniform(-1, 1, 2)]
        hi, ho, floor = rng.uniform(0, .4, 3)
        result = finite_ideal_allocation(T, floor, hi, ho, eta=eta)
        lp = finite_component_program(T, floor, hi, ho, eta)
        assert lp.success
        assert_allclose(result["shortfall"], lp.fun, atol=2e-10)


def test_fixed_pool_bound_includes_strings_and_arbitrary_reorientation():
    rng = np.random.default_rng(728)
    for _ in range(70):
        T = np.vstack([rng.uniform(.5, 4, 5), rng.uniform(-1, 1, (2, 5))])
        floor = rng.uniform(0, .2, 5)
        bound = isometric_pool_bounds(T, floor)
        lp = isometric_pool_program(T, floor)
        assert lp.success == (bound["lower"].max() <= bound["upper"].min())
        if lp.success:
            assert_allclose(lp.fun, 3*bound["lower"].max(), atol=1e-9)


@pytest.mark.parametrize("epsilon", [0., .1, .7])
def test_fixed_elastic_law_inverts_and_obeys_virtual_work(epsilon):
    tension = np.r_[0., np.geomspace(1e-9, 10, 100)]
    inventory = .003
    state = elastic_state_from_tension(tension, inventory, shear_fraction=epsilon)
    forward = elastic_state_from_strain(state["strain"], inventory, shear_fraction=epsilon)
    assert_allclose(forward["energy"], state["energy"], rtol=2e-14)
    assert_allclose(forward["tension"], tension, rtol=1e-9, atol=2e-14)
    assert_allclose(state["energy"][0], inventory)
    assert np.all(state["energy"] >= tension)
    assert np.max(state["energy"]-tension) <= inventory+1e-14
    # Differentiate the independently evaluated strain-energy function.
    h = 1e-5
    J = state["strain"][25:]
    plus = elastic_state_from_strain(J*np.exp(h), inventory, shear_fraction=epsilon)["energy"]
    minus = elastic_state_from_strain(J*np.exp(-h), inventory, shear_fraction=epsilon)["energy"]
    assert_allclose((plus-minus)/(2*h), tension[25:], rtol=1e-6, atol=1e-11)
    for name in ("out_of_plane_speed_squared", "longitudinal_speed_squared", "in_plane_shear_speed_squared"):
        assert state[name].min() >= 0
        assert state[name].max() <= 1+1e-14


def test_replay_preserves_inventory_full_tensor_and_separate_hoops():
    t = np.linspace(0, 1, 20)[:, None]
    hi, ho = .1+.01*t, .3+.1*t
    T = np.concatenate([np.full((1, 20, 1), 5.), np.zeros((2, 20, 1))])
    floor = .02+0*t
    result = elastic_replay(T, floor, hi, ho)
    assert_allclose(result["reconstructed_tensor"], T, atol=1e-14)
    tau = result["material_tension"]
    assert_allclose(tau[0]+tau[1], hi)
    assert_allclose(tau[2]+tau[3]+2*tau[4], ho)
    assert_allclose(tau[4], annular_factor(1.01)*result["ideal"]["field_energy"])
    assert np.min(result["remaining_reserve"]) > 0
    assert np.max(result["material_surcharge"]-result["inventory"].sum(axis=0)) < 1e-13
    assert np.all(result["law"]["energy"][tau == 0] > 0)


def test_internal_coordinates_reconstruct_each_material_metric():
    t = np.linspace(0, 1, 20)[:, None]
    lr, lt = np.exp(-.3*t), np.exp(.1*t)
    logJ = np.broadcast_to(.2+t, (6, 20, 1))
    q = configuration_coordinates(logJ, lr, lt)
    for i, dim in enumerate(MATERIAL_DIMENSIONS):
        macro = np.log(lt) if dim == 1 else np.log(lr*lt if i in (0, 2) else lt**2)
        assert_allclose(q[i].sum(axis=0)+macro, logJ[i], atol=1e-14)


def test_constitutive_work_over_linear_tension_panels_and_reciprocal_routes():
    # Linear T and log-linear macro geometry make trapezoidal pressure work exact.
    T = np.array([0., .1, .3, .05])[:, None]
    lr = np.exp(np.array([0., .1, -.2, .2]))[:, None]
    lt = np.exp(np.array([0., .05, .1, .02]))[:, None]
    law = elastic_state_from_tension(T, .003, shear_fraction=.1)
    Q = required_exchange(law["energy"][None], -T[None], -T[None], lr, lt)
    material_change = np.diff(law["energy"], axis=0)
    macro_work = .5*(T[1:]+T[:-1])*np.diff(np.log(lr*lt), axis=0)
    assert_allclose(Q[0], material_change-macro_work)
    rng = np.random.default_rng(41)
    exchanges = rng.normal(size=(11, 40, 3))
    routes = reciprocal_routes(exchanges)
    flows = routes["transfer_totals"]
    full = np.concatenate([exchanges, routes["rail_exchange"][None]])
    assert_allclose(flows.sum(axis=0)-flows.sum(axis=1), full.sum(axis=1), atol=2e-14)
    assert routes["maximum_unmatched_exchange"] < 1e-14
    assert np.min(flows) >= 0


def test_zero_inventory_and_compressive_strain_are_rejected():
    with pytest.raises(ValueError):
        elastic_state_from_tension(1., 0.)
    with pytest.raises(ValueError):
        elastic_state_from_strain(.9, 1.)


def test_configuration_rate_bound_covers_the_whole_constitutive_panel():
    rng = np.random.default_rng(830)
    T = rng.uniform(0, .4, (6, 2, 3))
    M = rng.uniform(.001, .01, (6, 3))
    lr = np.exp(rng.uniform(-.2, .2, (2, 3)))
    lt = np.exp(rng.uniform(-.2, .2, (2, 3)))
    dt = np.full((1, 3), .07)
    bound = configuration_rate_bound(T, M, lr, lt, dt)
    sampled = np.zeros_like(bound)
    for u in np.linspace(0, 1, 1001):
        Tu = (1-u)*T[:, :1]+u*T[:, 1:]
        eps = np.where(MATERIAL_DIMENSIONS == 2, .1, 0.)[:, None, None]
        dlogJ = np.diff(T, axis=1)/(dt*np.hypot(Tu, (1-eps)*M[:, None]))
        dz, da = np.diff(np.log(lr), axis=0)/dt, np.diff(np.log(lt), axis=0)/dt
        for i, dim in enumerate(MATERIAL_DIMENSIONS):
            norm = abs(dlogJ[i]-da) if dim == 1 else np.hypot(.5*dlogJ[i]-(dz if i in (0, 2) else da), .5*dlogJ[i]-da)
            sampled[i] = np.maximum(sampled[i], norm)
    assert_allclose(bound, sampled, rtol=1e-14)


def test_initial_inventory_allocation_minimizes_the_worst_linear_stretch():
    peaks = np.array([[.02, .04], [.003, .005], [.1, .2], [0., 0.], [.07, .09], [1., .5]])
    budget = np.array([.001, .003])
    result = inventory_for_minimum_stretch(peaks, budget)
    M, cap = result["inventory"], result["linear_stretch_cap"]
    dims = MATERIAL_DIMENSIONS[:, None]
    eps = np.where(dims == 2, .1, 0.)
    state = elastic_state_from_tension(peaks, M, shear_fraction=eps)
    linear = state["strain"]**(1/dims)
    equal = elastic_state_from_tension(peaks, budget/6, shear_fraction=eps)["strain"]**(1/dims)
    assert_allclose(M.sum(axis=0), budget, atol=1e-16)
    assert_allclose(linear.max(axis=0), cap, rtol=1e-13)
    assert np.all(linear.max(axis=0) < equal.max(axis=0))
    # A lower stretch cap cannot fit the same six peak duties and rest budget.
    required = np.maximum(1e-6*budget, 2*peaks/((1-eps)*((.999*cap)**dims-(.999*cap)**(-dims))))
    assert np.all(required.sum(axis=0) > budget)
