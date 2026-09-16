import numpy as np
import pytest
from numpy.testing import assert_allclose
from scipy.integrate import quad_vec
from scipy.optimize import linprog

from adm_harness.containment_ensemble import required_exchange
from adm_harness.distributed_reconfiguration import (
    exchange_power_bounds, instantaneous_exchange_power, joint_transport_envelope, joint_work_capacity,
    lipschitz_interval_path, scheduled_replay, transport_capacity,
)
from adm_harness.finite_containment import annular_factor
from adm_harness.material_reconfiguration import elastic_state_from_tension


def interval_lp(lo, hi, time):
    n = len(time)
    matrix = np.zeros((2*(n-1), n+1))
    for i, dt in enumerate(np.diff(time)):
        matrix[2*i, [i, i+1, -1]] = [-1, 1, -dt]
        matrix[2*i+1, [i, i+1, -1]] = [1, -1, -dt]
    return linprog(np.r_[np.zeros(n), 1.], A_ub=matrix,
        b_ub=np.zeros(2*(n-1)), bounds=[*zip(lo, hi), (0, None)], method="highs")


def example():
    t = np.linspace(0, 1, 25)[:, None]
    target = np.stack([5+.2*np.sin(t), .15*np.cos(2*t), .1*np.sin(3*t)])
    hi, ho = .1+.01*t, .3+.06*t
    dt = np.diff(t, axis=0)
    result = scheduled_replay(target, .02+0*t, hi, ho, dt)
    return result, hi, ho, np.exp(.2*t), np.exp(-.1*t), dt


def test_lipschitz_envelope_matches_independent_full_history_optimization():
    rng = np.random.default_rng(654)
    for _ in range(30):
        time = np.cumsum(rng.uniform(.03, .2, 18))
        lo = rng.uniform(0, 2, 18)
        hi = lo+rng.uniform(.01, .4, 18)
        result = lipschitz_interval_path(lo[:, None], hi[:, None], time[:, None])
        lp = interval_lp(lo, hi, time)
        assert lp.success
        assert_allclose(result["rate"][0], lp.fun, rtol=2e-8, atol=2e-9)
        path = result["path"][:, 0]
        assert np.all(path >= lo)
        assert np.all(path <= hi)
        assert np.max(np.abs(np.diff(path))/np.diff(time)) <= result["rate"][0]+2e-10
    constant = lipschitz_interval_path(np.zeros((3, 2)), np.ones((3, 2)),
                                      np.broadcast_to(np.arange(3)[:, None], (3, 2)))
    assert_allclose(constant["path"], .5)
    assert np.max(constant["rate"]) < 1e-12


def test_scheduled_roles_keep_tensor_boundaries_and_conserved_material():
    result, hi, ho, _, _, _ = example()
    T = result["material_tension"]
    assert_allclose(result["reconstructed_tensor"], result["target"], atol=2e-14)
    assert_allclose(T[0]+T[1], hi)
    assert_allclose(T[2]+T[3]+2*T[4], ho)
    assert_allclose(T[4], annular_factor(1.01)*result["field_energy"])
    assert np.all(result["remaining_reserve"] >= result["guaranteed_reserve"]-1e-13)
    assert np.all(T[[1, 2, 4, 5]] > 0)
    assert np.all(T[[0, 3]] == 0)
    assert_allclose(result["law"]["energy"][[0, 3]],
                    np.broadcast_to(result["inventory"][[0, 3], None], T[[0, 3]].shape))
    assert_allclose(result["inventory"].sum(axis=0), .25*result["reference_reserve"])


def test_true_power_integrates_to_work_exchange_and_has_reciprocal_rail_port():
    result, _, _, lr, lt, dt = example()
    expected = required_exchange(result["component_energy"], result["component_pressure"][0],
                                 result["component_pressure"][1], lr, lt)
    integral, _ = quad_vec(lambda u: instantaneous_exchange_power(result, lr, lt, dt, u)*dt,
                           0., 1., epsabs=1e-12, epsrel=1e-12)
    assert_allclose(integral[:-1], expected, atol=1e-12)
    assert_allclose(integral.sum(axis=0), 0., atol=1e-13)
    for u in [0., .13, .8, 1.]:
        power = instantaneous_exchange_power(result, lr, lt, dt, u)
        assert_allclose(power.sum(axis=0), 0., atol=1e-13)


def test_power_bounds_cover_interior_extremum_missed_by_endpoints():
    result, _, _, lr, lt, dt = example()
    # Make a two-state material example with a known interior power maximum.
    tiny = {k: result[k][..., :2, :].copy() for k in
            ("target", "component_energy", "component_pressure", "material_tension")}
    tiny["inventory"] = result["inventory"].copy()
    tiny["inventory"][1] = .3
    tiny["material_tension"][1, :, 0] = [.01, 4.]
    tiny["component_energy"][1] = elastic_state_from_tension(tiny["material_tension"][1], .3)["energy"]
    tiny["component_pressure"][1, 1] = -tiny["material_tension"][1]
    lr, lt, dt = np.ones((2, 1)), np.exp([[0.], [1.]]), np.ones((1, 1))
    bound = exchange_power_bounds(tiny, lr, lt, dt)
    endpoint = max(instantaneous_exchange_power(tiny, lr, lt, dt, u)[1, 0, 0] for u in (0., 1.))
    assert bound["upper"][1, 0, 0] > endpoint+1
    dense = np.stack([instantaneous_exchange_power(tiny, lr, lt, dt, u)
                      for u in np.linspace(0, 1, 1001)])
    assert np.max(dense-bound["upper"]) < 1e-12
    assert np.max(bound["lower"]-dense) < 1e-12
    assert_allclose(dense[:, 1].max(), bound["upper"][1].max(), rtol=1e-5)


def test_delay_buffers_conserve_prepared_energy_including_energy_in_flight():
    # Receipt waveforms in three separated intervals. A fixed delay produces
    # an exact outstanding inventory, including startup and final drainage.
    edges = np.array([0., .4, .6, 1.])
    receipt = np.array([[[2.], [0.], [3.]], [[0.], [4.], [1.]]])
    delay = np.array([.13])
    C = transport_capacity(receipt, delay)
    def cumulative(t):
        durations = np.clip(t-edges[:-1], 0., np.diff(edges))
        return (receipt[:, :, 0]*durations).sum(axis=1)
    for t in np.linspace(0, 1.2, 301):
        outstanding = cumulative(t)-cumulative(t-delay[0])
        buffers = C["node_capacity"][:, 0]-outstanding
        assert buffers.min() >= -1e-14
        assert_allclose(buffers.sum()+outstanding.sum(), C["total_capacity"][0])
    assert_allclose(cumulative(1.2)-cumulative(1.2-delay[0]), 0.)


def test_shared_joint_and_transit_stresses_reconstruct_neutral_package():
    rng = np.random.default_rng(333)
    T = rng.uniform(0., 1., (6, 8, 4))
    C = rng.uniform(.1, .4, 4)
    result = joint_transport_envelope(T, C, .04)
    Jz, Jt = result["axial_joint_tension"], result["transverse_joint_tension"]
    for fraction in np.linspace(0, 1, 21):
        u = fraction*C
        # Positive mismatch receives tensile ties, negative receives photons.
        residual = np.stack([u/3-Jz, 2*u/3-Jt])
        ties, photons = np.maximum(residual, 0.), np.maximum(-residual, 0.)
        assert_allclose(residual-ties+photons, 0., atol=1e-14)
        energy = (C-u)+u+Jz+Jt+(ties+photons).sum(axis=0)
        assert np.max(energy-result["energy_ceiling"]) < 1e-14
    assert np.all(result["energy_ceiling"] <= result["separate_package_ceiling"]+1e-14)
    assert_allclose(joint_transport_envelope(T, C, 0.)["energy_ceiling"],
                    np.broadcast_to(2*C, (8, 4)))


def test_invalid_histories_are_rejected():
    with pytest.raises(ValueError):
        lipschitz_interval_path(np.ones((2, 1)), np.zeros((2, 1)), np.arange(2)[:, None])
    with pytest.raises(ValueError):
        lipschitz_interval_path(np.zeros((2, 1)), np.ones((2, 1)), np.zeros((2, 1)))
    with pytest.raises(ValueError):
        transport_capacity(np.ones((2, 3, 1)), np.array([-.1]))
    with pytest.raises(ValueError):
        joint_transport_envelope(np.ones((6, 3, 1)), np.ones(1), -.1)


def test_joint_work_changes_the_dust_exchange_and_retains_reciprocity():
    result, _, _, lr, lt, dt = example()
    power = exchange_power_bounds(result, lr, lt, dt)
    delay = np.array([.002])
    expanded = joint_work_capacity(result, power, lr, lt, dt, delay, .02)
    assert_allclose(expanded["dust_power_correction"], -np.diff(expanded["joint_energy"], axis=0)/dt)
    for i, u in enumerate((0., 1.)):
        old = instantaneous_exchange_power(result, lr, lt, dt, u)
        old[-2] += expanded["dust_power_correction"]
        rates = np.concatenate([old[:-1], expanded["joint_endpoint_power"][i], old[-1:]])
        assert_allclose(rates.sum(axis=0), 0., atol=1e-13)
        assert np.max(rates-expanded["expanded_power_upper"]) < 1e-13
        assert np.max(expanded["expanded_power_lower"]-rates) < 1e-13
    # Their exact panel power integrals equal changing energy plus opposing
    # pressure work; the two pressure works cancel in the total package.
    integrated = .5*sum(expanded["joint_endpoint_power"])*dt
    assert_allclose(integrated.sum(axis=0), np.diff(expanded["joint_energy"], axis=0), atol=1e-13)
    zero = joint_work_capacity(result, power, lr, lt, dt, delay, 0.)
    assert_allclose(zero["total_capacity"], transport_capacity(power["upper"], delay)["total_capacity"])
