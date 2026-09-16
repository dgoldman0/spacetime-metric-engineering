import numpy as np
from numpy.testing import assert_allclose
import pytest
from scipy.optimize import linprog

from adm_harness.magnetic_load_balance import (
    radiation_inventory, loop_field, support_cone, attached_bank,
    loop_currents, carrier_limit, loop_work, straight_sleeve, conserved_sleeve_interval,
    balance_pitch, sleeve_at_inventory,
)


def test_compressed_radiation_retains_adiabatic_work_and_supplied_heat():
    # V**(1/3)=exp(-t); constant heat rate 2 has an analytic integrating factor.
    t = np.linspace(0, 1, 21)
    root = np.exp(-t)
    means = (root[:-1]-root[1:])/np.diff(t)
    result = radiation_inventory(np.array([3.]), 2*np.diff(t)[:, None],
                                 np.exp(-3*t)[:, None], means[:, None])
    expected = np.exp(t)*(3+2*(1-np.exp(-t)))
    assert_allclose(result["energy"][:, 0], expected, atol=1e-13)
    assert_allclose(result["balance_residual"], 0, atol=1e-14)
    assert np.all(result["compression_work"] > 0)


def test_zero_heat_adiabatic_invariant_and_constant_volume_receipts():
    volume = np.array([[8.], [1.]])
    result = radiation_inventory(np.array([1.]), np.zeros((1, 1)), volume, np.ones((1, 1)))
    assert_allclose(result["energy"][:, 0], [1, 2])
    result = radiation_inventory(np.array([1.]), np.array([[2.]]),
                                 np.ones((2, 1)), np.ones((1, 1)))
    assert_allclose(result["energy"][:, 0], [1, 3])


def test_loop_tensor_against_direct_flux_and_direction_quadrature():
    # Direct integration of the two straight legs and a full circle of bends.
    aspect, angle, lr, lt, heat = .12, .37, .3, .97, 3.4
    field = loop_field(heat, lr, lt, aspect=aspect, angle=angle)
    phi = 2*np.pi*(np.arange(10000)+.5)/10000
    ds = 2*np.pi*aspect/len(phi)
    ar = 2*lr**2*np.cos(angle)**2+ds*np.sum(lr**2*np.cos(phi)**2)
    at = 2*lt**2*np.sin(angle)**2+ds*np.sum(lt**2*np.sin(phi)**2)
    normalization = heat/(3*(2+2*np.pi*aspect)*min(lr, lt)**2)
    assert_allclose([field["radial"], field["transverse"]], normalization*np.array([ar, at]))
    # The complete magnetic spatial trace equals its positive energy.
    assert_allclose(field["radial_pressure_energy"]+2*field["angular_pressure_energy"],
                    field["energy"])


def test_minimum_field_meets_pressure_at_the_weakest_bend():
    e, volume, lr, lt, aspect, angle, beta = 3., 2., .4, 1., .1, .3, .8
    field = loop_field(e, lr, lt, aspect=aspect, angle=angle, beta_limit=beta)
    # Normalize the affine field independently from its integrated energy,
    # then sample the local magnetic pressure over both legs and every bend.
    bend_angles = np.linspace(0, 2*np.pi, 10001)
    tangent_squared = (lr*np.cos(bend_angles))**2+(lt*np.sin(bend_angles))**2
    straight_squared = (lr*np.cos(angle))**2+(lt*np.sin(angle))**2
    mean_square = (straight_squared+np.pi*aspect*(lr*lr+lt*lt)/2)/(1+np.pi*aspect)
    pressure = field["energy"]/volume*tangent_squared/mean_square
    local_beta = e/(3*volume)/pressure
    assert_allclose(local_beta.max(), beta)
    assert np.all(local_beta <= beta+1e-14)
    assert_allclose(field["radial"]/field["energy"],
        lr*lr*(np.cos(angle)**2+np.pi*aspect/2)/((1+np.pi*aspect)*mean_square))


def test_field_floor_cone_matches_independent_linear_program():
    basis = np.array([[1, 1, 1, 1, 1], [-1, 1, 0, 0, 0], [1, 0, .5, -1, 0]])
    rng = np.random.default_rng(421)
    for p, q, floor in zip(rng.normal(size=30), rng.normal(size=30), rng.uniform(size=30)):
        result = linprog(np.ones(5), A_eq=basis[1:], b_eq=[p, q],
                         bounds=[(floor, None)]+[(0, None)]*4, method="highs")
        assert result.success
        actual = support_cone(result.fun+.2, p, q, floor)
        assert_allclose(actual["shortfall"], -.2, atol=1e-12)
        components = np.array([actual[k] for k in
                               ("field", "radial_wave", "angular_wave", "membrane", "spare")])
        assert components.min() >= 0
        assert_allclose(basis@components, [result.fun+.2, p, q], atol=1e-12)


def test_closed_loop_current_integrals_in_undeformed_geometry():
    e = np.full((3, 2), 3.)
    volume = np.full_like(e, 10.)
    leg = np.array([2., 3.])
    aspect, tube, fill, angle = .1, .08, .2, .4
    result = loop_currents(e, volume, np.ones_like(e), np.ones_like(e), leg,
                           aspect=aspect, angle=angle, fill_fraction=fill, tube_ratio=tube)
    radius = leg*aspect*tube
    length = 2*leg*(1+np.pi*aspect)
    b = np.sqrt(2*e/(3*fill*volume))
    sheet = 2*b*fill*volume/radius
    bulk = 2*np.pi*b*fill*volume/length
    assert_allclose(result["sheet_current_integral"], sheet)
    assert_allclose(result["bend_current_integral"], bulk)
    weight = (np.cos(angle)**2+np.pi*aspect/2)/(1+np.pi*aspect)
    assert_allclose(result["sheet_radial_fraction"], (1-weight)/2)
    assert_allclose(result["unit_tensor"][0], 2*(sheet+bulk)/volume)
    assert_allclose(result["maximum_drift"], 1/np.sqrt(2))
    assert_allclose(result["unit_tensor"][1]+2*result["unit_tensor"][2],
                    result["unit_tensor"][0]/2)


def test_current_quadrature_refines_under_strong_anisotropic_compression():
    e = np.array([[1.], [2.]])
    lr, lt = np.array([[1.], [.3]]), np.array([[1.], [.99]])
    D = 4*lr*lt**2
    results = [loop_currents(e, D, lr, lt, np.array([1.]), aspect=.1,
                             angle=.4, order=n) for n in (16, 32, 64)]
    errors = [np.max(abs(v["unit_tensor"]-results[-1]["unit_tensor"]))
              for v in results[:-1]]
    assert errors[1] < errors[0]/50
    assert errors[1] < 2e-4


def test_carrier_limit_fails_immediately_above_the_active_facet():
    facets = np.array([[[-1.]], [[-2.]], [[-3.]]])
    unit = np.array([[[2.]], [[.2]], [[.3]]])
    limit, slopes = carrier_limit(facets, unit)
    assert limit > 0
    assert np.max(facets+limit*slopes) == pytest.approx(0.)
    assert np.max(facets+(1+1e-5)*limit*slopes) > 0
    assert np.max(facets+.5*limit*slopes) < 0


def test_shared_core_field_is_credited_once_and_only_its_magnetic_half():
    shape = (2, 1)
    one, zero = np.ones(shape), np.zeros(shape)
    state = dict(D=one, radius=one, amplitude=2*one,
                 receiver_cold_energy=one, receiver_hot_energy=one,
                 receiver_thermal_energy=2*one, receiver_rest=2*one,
                 receiver_fixed_containment_energy=np.array([2/3]),
                 balanced_radiation_rest=zero, thermal_reservoir_rest=zero,
                 wall_rest=zero, guide_rest=zero,
                 credited_target=np.stack([10*one, zero, zero]))
    field = dict(radial=3*one, transverse=one)
    shared = attached_bank(state, one, field)
    separate = attached_bank(state, one, field, share_core=False)
    assert_allclose(shared["core_field_overlap"], one)
    assert_allclose(shared["radial_field_floor"], 2*one)
    assert_allclose(separate["radial_field_floor"], 3*one)
    assert_allclose(shared["released_enclosure_energy"], [1/3])
    assert_allclose(shared["residual_target"], separate["residual_target"])


def test_loop_work_for_passively_compressed_flux_needs_no_electrical_input():
    t = np.linspace(0, 1, 4001)
    ell = np.exp(-t)[:, None]
    R = np.ones_like(ell)
    # Pure radial flux: E proportional to ell, p_r V=-E, p_t V=E.
    result = loop_work(t, ell, ell, ell, R)
    assert abs(result["electrical"].sum()) < 4e-9
    assert_allclose(result["balance_residual"], 0)


def test_straight_sleeve_against_full_material_and_field_linear_program():
    rng = np.random.default_rng(76)
    # Variables: sleeve density, sleeve axial stress, five ordinary
    # components, signed extra density. Hoop pressure has no free omission.
    basis = np.array([[1, 1, 1, 1, 1], [-1, 1, 0, 0, 0], [1, 0, .5, -1, 0]])
    for _ in range(15):
        rho, p, q = rng.normal(size=3)
        floor, k = rng.uniform(.01, .5), rng.uniform(.2, 1.)
        angle, lr, lt = rng.uniform(0, np.pi/2), rng.uniform(.2, 1.), .99
        raw = support_cone(rho, p, q, floor)
        result = straight_sleeve(raw["facets"], 1., 2., lr, lt,
                                aspect=.1, angle=angle, stress_fraction=k)
        H, f = result["hoop_energy_floor"], result["radial_tangent_fraction"]
        matrix = np.zeros((3, 8)); matrix[:, 2:7] = basis
        matrix[:, 0] = [1, 0, 0]; matrix[:, 1] = [0, f, (1-f)/2]
        matrix[0, -1] = -1
        inequalities = np.zeros((2, 8))
        inequalities[:, :2] = [[-k, 1], [-k, -1]]
        cost = np.zeros(8); cost[-1] = 1
        lp = linprog(cost, A_eq=matrix,
            b_eq=[rho, p+H*(1-f)/2, q+H*(1+f)/4],
            A_ub=inequalities, b_ub=[0, 0],
            bounds=[(H/k, None), (None, None), (floor, None)]
                   +[(0, None)]*4+[(None, None)], method="highs")
        assert lp.success
        assert_allclose(result["shortfall"], lp.fun, atol=2e-10)


def test_common_pitch_optimum_against_complete_component_linear_program():
    shape = (3, 2); one = np.ones(shape)
    ell = np.array([[1., 1.], [.5, .6], [.3, .4]])
    cold = np.array([[.01, .02], [.1, .12], [.2, .22]])
    state = dict(D=ell, ell=ell, radius=one, amplitude=.06*one,
        receiver_cold_energy=cold, receiver_hot_energy=.1*one,
        receiver_thermal_energy=cold+.1, receiver_rest=(cold+.1)/ell,
        receiver_fixed_containment_energy=np.array([.2, .2]),
        balanced_radiation_rest=.02*one, thermal_reservoir_rest=.03*one,
        wall_rest=.001*one, guide_rest=.01*one,
        credited_target=np.stack([one, .2*one, -.05*one]))
    aspect = .07
    solution = balance_pitch(state, cold, aspect=aspect)
    zero = dict(radial=np.zeros(shape), transverse=np.zeros(shape))
    base = attached_bank(state, cold, zero)["residual_target"].reshape(3, -1)
    f0 = loop_field(cold, ell, one, aspect=aspect, angle=np.pi/2)
    f1 = loop_field(cold, ell, one, aspect=aspect, angle=0)
    n = one.size; cols = 5*n+2; pitch, extra = 5*n, 5*n+1
    equality, rhs, inequality, ub = [], [], [], []
    basis = np.array([[1, 1, 1, 1, 1], [-1, 1, 0, 0, 0], [1, 0, .5, -1, 0]])
    for i in range(n):
        transverse0 = (f0["transverse"]/ell).ravel()[i]
        transverse_delta = ((f1["transverse"]-f0["transverse"])/ell).ravel()[i]
        for j in range(3):
            row = np.zeros(cols); row[5*i:5*i+5] = basis[j]
            row[pitch] = transverse_delta if j < 2 else 0
            row[extra] = -1 if j == 0 else 0
            equality.append(row); rhs.append(base[j, i]-(transverse0 if j < 2 else 0))
        row = np.zeros(cols); row[5*i] = -1
        row[pitch] = ((f1["radial"]-f0["radial"])/ell).ravel()[i]
        inequality.append(row); ub.append(.03-(f0["radial"]/ell).ravel()[i])
    bounds = ([(.01, None)]+[(0, None)]*4)*n+[(0, 1), (None, None)]
    cost = np.zeros(cols); cost[extra] = 1
    lp = linprog(cost, A_eq=equality, b_eq=rhs, A_ub=inequality, b_ub=ub,
                 bounds=bounds, method="highs")
    assert lp.success
    assert_allclose(solution["best_shortfall"], lp.fun, atol=1e-11)


def test_conserved_sleeve_projection_matches_joint_time_linear_program():
    rng = np.random.default_rng(181)
    for _ in range(20):
        n = 4
        D = rng.uniform(1, 3, (n, 1))
        H = rng.uniform(.01, .2, (n, 1))
        f = rng.uniform(0, 1, (n, 1))
        k = rng.uniform(.5, 1)
        facets = rng.uniform(-2, .2, (3, n, 1))
        result = conserved_sleeve_interval(facets, D, H, f, stress_fraction=k)
        offsets = facets+np.stack([H, H*(1-3*f)/4, -H*(5-3*f)/4])
        slopes = np.stack([-np.ones_like(f), (1-3*f)/2, (1+3*f)/2])
        rows, rhs = [], []
        for t in range(n):
            for j in range(3):
                row = np.zeros(n+1); row[0] = 1/D[t, 0]; row[t+1] = slopes[j, t, 0]
                rows.append(row); rhs.append(-offsets[j, t, 0])
            for sign in (-1, 1):
                row = np.zeros(n+1); row[0] = -k/D[t, 0]; row[t+1] = sign
                rows.append(row); rhs.append(0)
        bounds = [(float(np.max(D*H/k)), None)]+[(None, None)]*n
        cost = np.r_[1., np.zeros(n)]
        lo = linprog(cost, A_ub=rows, b_ub=rhs, bounds=bounds, method="highs")
        assert bool(result["feasible"][0]) == bool(lo.success)
        if lo.success:
            hi = linprog(-cost, A_ub=rows, b_ub=rhs, bounds=bounds, method="highs")
            assert hi.success
            assert_allclose([result["lower"][0], result["upper"][0]],
                            [lo.fun, -hi.fun], atol=1e-10)
            inventory = (result["lower"]+result["upper"])/2
            sleeve = sleeve_at_inventory(facets, D, H, f, inventory, stress_fraction=k)
            rho, pr, pt = sleeve["tensor"]
            reconstructed = facets+np.stack([rho-pr-2*pt, rho-pr+pt, rho+2*pr+pt])
            assert reconstructed.max() <= 2e-12
            assert_allclose(D*rho, np.broadcast_to(inventory, D.shape))


@pytest.mark.parametrize("aspect,angle,beta", [(0, 0, 1), (.1, -1, 1), (.1, 0, 0)])
def test_invalid_loop_parameters_rejected(aspect, angle, beta):
    with pytest.raises(ValueError):
        loop_field(1., 1., 1., aspect=aspect, angle=angle, beta_limit=beta)
