import numpy as np
import pytest
from numpy.testing import assert_allclose

from adm_harness.containment_ensemble import (
    allocate, average_tensor, component_program, host_cost_threshold,
    material_basis, required_exchange, tensile_strength_floor,
)
from adm_harness.magnetic_load_balance import support_cone


def test_local_tensors_follow_maxwell_and_membrane_projectors():
    # Independent projector construction, axes z,theta,n.
    eye = np.eye(3)
    basis = material_basis()
    for column, normal in ((0, eye[2]), (2, eye[0])):
        stress = -(eye-np.outer(normal, normal))
        assert_allclose(basis[1:, column], np.diag(stress))
    field = eye[1]
    assert_allclose(basis[1:, 3], np.diag(eye-2*np.outer(field, field)))


def test_equal_averaged_tensors_have_different_load_responses():
    tensors = [material_basis(field_kind=name)[:, 3]
               for name in ("hoop_maxwell", "normal_maxwell", "axial_photons")]
    for tensor in tensors:
        assert_allclose(average_tensor(tensor), [1., 1., 0.])
    assert_allclose([t[2] for t in tensors], [-1., 1., 0.])
    assert_allclose([t[3] for t in tensors], [1., -1., 0.])


def test_composite_counterexample_counts_normal_stress_and_every_energy():
    # One unit each of hoop field and transverse membrane: U=2,z=1,H=2,N=0.
    local = material_basis() @ np.array([0., 0., 1., 1., 0.])
    assert_allclose(local, [2., 1., -2., 0.])
    assert local[1]-local[2] > local[0]
    target = average_tensor(local)
    assert component_program(target, 0., 2.).success
    # Aliasing either alternative to the same averaged tensor invents hoop support.
    assert component_program(target, 0., 2., field_kind="axial_photons").status == 2
    assert component_program(target, 0., 2., field_kind="normal_maxwell").status == 2


@pytest.mark.parametrize("host,strength", [(0., 1.), (.1, 1.), (0., .85), (.6, .7), (1.2, 1.)])
def test_analytic_allocation_matches_independent_full_component_program(host, strength):
    rng = np.random.default_rng(994)
    for _ in range(35):
        target = np.r_[rng.uniform(.4, 5), rng.uniform(-2, 2, 2)]
        floor, H = rng.uniform(0, .5, 2)
        facets = support_cone(*target, floor)["facets"]
        result = allocate(facets, H, host_per_field=host, transverse_strength=strength)
        lp = component_program(target, floor, H, host_per_field=host, transverse_strength=strength)
        assert lp.success == (result["minimum_shortfall"] <= 0)
        assert_allclose(result["local_tensor"][2:], [-H, 0.], atol=2e-15)
        assert np.min(result["components"]) >= 0
        if lp.success:
            assert_allclose(-lp.fun, -result["minimum_shortfall"], atol=1e-10)


def test_local_material_constraints_apply_only_to_the_assigned_constituent():
    target = np.array([3., .75, -1.])
    facets = support_cone(*target)["facets"]
    result = allocate(facets, 2., transverse_strength=.8, host_per_field=.1)
    W, S, M, b, host = result["components"]
    assert_allclose(.8*M, b)
    assert_allclose(host, .1*b)
    assert_allclose(W+S+2*b, 2.)
    assert_allclose(result["local_tensor"][0], W+S+M+b+host)


def test_host_allowance_brackets_the_ensemble_failure():
    # A target with a strictly positive axial/hoop joint-stress demand.
    target = np.array([2.2, 1., -1.])
    facets = support_cone(*target)["facets"]
    bound = host_cost_threshold(facets, 2.)
    assert bound["field_required"]
    assert 0 < bound["lower"] < bound["upper"] < 1
    assert component_program(target, 0., 2., host_per_field=bound["lower"]-1e-5).success
    assert component_program(target, 0., 2., host_per_field=bound["upper"]+1e-5).status == 2


def test_required_exchange_converges_to_zero_for_free_adiabatic_primitives():
    errors = []
    for n in (101, 201):
        t = np.linspace(0, 1, n)[:, None]
        lr, lt = np.exp(-.4*t), np.exp(.2*t)
        # Constant-tension longitudinal sheet, transverse sheet, hoop field.
        E = np.stack([lr*lt, lt*lt, 1/lr])
        P = np.stack([-E[0], 0*E[1], E[2]])
        T = np.stack([-E[0], -2*E[1], 0*E[2]])
        transfer = required_exchange(E, P, T, lr, lt)
        errors.append(np.max(np.abs(transfer)))
    assert 7.9 < errors[0]/errors[1] < 8.1


def test_invalid_constituent_strength_and_host_cost_are_rejected():
    with pytest.raises(ValueError):
        material_basis(transverse_strength=0.)
    with pytest.raises(ValueError):
        allocate(np.zeros(3), 1., host_per_field=-.1)


def test_ensemble_strength_bound_is_saturated_by_field_and_transverse_sheet():
    for k in (.02, .2, .5, 1.):
        # A transverse sheet with energy one, balanced by field energy k.
        local = material_basis(transverse_strength=k) @ np.array([0., 0., 1., k, 0.])
        assert_allclose(local[3], 0.)
        assert_allclose(tensile_strength_floor(local[0], -local[2]), k)
        assert tensile_strength_floor(.9*local[0], -local[2]) > k
