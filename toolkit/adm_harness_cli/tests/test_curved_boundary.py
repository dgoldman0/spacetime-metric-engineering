"""Independent continuum and operator checks for the spherical field response."""
import numpy as np
import pytest

from adm_harness.casimir_matching import gap_profile
from adm_harness.curved_boundary import (RadialProblem, constant_green, frequency_quadrature,
    radial_mesh, response_kernel, tensor_from_moments)


def cylinder_problem(spacing):
    x = radial_mesh(spacing, 12., [-.5, .5, -.2, 0., .2])
    return RadialProblem(x, np.ones_like(x), np.ones_like(x), np.ones_like(x),
        np.ones(len(x)-1), np.searchsorted(x, [-.5, .5]), np.searchsorted(x, [-.2, 0., .2]))


@pytest.mark.parametrize('frequency,angular_index', [(0., 0), (.4, 0), (2., 3)])
def test_positive_discretization_converges_to_exact_cylinder(frequency, angular_index):
    errors = []
    k = np.sqrt(frequency**2+angular_index*(angular_index+1))
    for spacing in [1/64, 1/128, 1/256]:
        problem = cylinder_problem(spacing)
        columns = problem.green_columns(frequency, angular_index)
        exact = constant_green(k, problem.coordinate[problem.probe_nodes], [-.5, .5], 12.)
        errors.append(np.max(np.abs(columns[problem.probe_nodes]-exact)))
    if k == 0:
        assert max(errors) < 3e-10
    else:
        assert errors[-1] < errors[0]/10
        assert errors[-1] < 1e-5


def test_rank_update_matches_a_direct_material_operator():
    # An independently inverted dense positive operator checks the delta-sheet
    # normalization and mixed derivative sign without the mode integrator.
    n, step = 121, .05
    stiffness = np.diag(np.full(n, 2/step+.7**2*step))
    stiffness += np.diag(np.full(n-1, -1/step), 1)+np.diag(np.full(n-1, -1/step), -1)
    walls = np.array([35, 85]); probes = np.array([50, 60, 70]); v = np.array([2., 7.])
    base = np.linalg.inv(stiffness)
    modified = stiffness.copy(); modified[walls, walls] += v
    difference = np.linalg.inv(modified)-base
    values = base[np.ix_(probes, walls)]
    derivative = (base[np.ix_(probes+1, walls)]-base[np.ix_(probes-1, walls)])/(2*step)
    diagonal, mixed = response_kernel(values, derivative, base[np.ix_(walls, walls)], v)
    direct_mixed = (difference[probes+1, probes+1]+difference[probes-1, probes-1]
        -difference[probes+1, probes-1]-difference[probes-1, probes+1])/(4*step**2)
    assert np.allclose(diagonal, difference[probes, probes], atol=3e-13, rtol=2e-11)
    assert np.allclose(mixed, direct_mixed, atol=4e-12, rtol=2e-10)
    assert np.all(diagonal < 0) and np.all(mixed < 0)


@pytest.mark.parametrize('coupling', [.1, 8., 100.])
def test_lorentzian_derivative_moments_reproduce_planar_continuum(coupling):
    # The spherical convention becomes dζ k dk/(2π²) in the planar limit.
    # Angular averaging in the (ζ,kx,ky) half-space gives <ζ²>=κ²/3,
    # <kx²>=κ²/3. The radial derivative is evaluated on the Green function.
    fractions = np.array([.2, .5, .8]); walls = np.array([0., 1.])
    kappa, weights = frequency_quadrature(256, upper=300.)
    moments = np.zeros((len(fractions), 3))
    for k, weight in zip(kappa, weights):
        distances = fractions[:, None]-walls[None, :]
        values = np.exp(-k*np.abs(distances))/(2*k)
        derivatives = -k*np.sign(distances)*values
        wall_green = np.exp(-k*np.abs(walls[:, None]-walls[None, :]))/(2*k)
        diagonal, mixed = response_kernel(values, derivatives, wall_green, [coupling]*2)
        moments += weight*k*k/(2*np.pi**2)*np.stack([-k*k*diagonal/3, mixed, k*k*diagonal/3], axis=-1)
    actual = tensor_from_moments(moments)[:, :3]
    expected = gap_profile(1., coupling, coupling, fractions, nodes=512)
    assert np.allclose(actual, expected, rtol=2e-8, atol=2e-10)


def test_invalid_optical_coupling_is_rejected():
    with pytest.raises(ValueError):
        response_kernel(np.ones((2, 1)), np.zeros((2, 1)), np.ones((1, 1)), [-1.])
