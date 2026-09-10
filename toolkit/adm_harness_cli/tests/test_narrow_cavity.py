import numpy as np
from numpy.testing import assert_allclose

from adm_harness.narrow_cavity import (
    gradient_integral, interaction_logdet, layer_reflection, planar_interaction,
    spectral_quadrature)


def test_finite_layer_reflection_matches_exact_rectangular_barrier():
    k = np.geomspace(1e-5, 100, 81)
    height, width = 3.2, .7
    rate = np.sqrt(k*k+height)
    t = np.tanh(rate*width)
    exact = height*t/((2*k*k+height)*t+2*k*rate)
    actual = layer_reflection(k, np.full(64, height), width/64)
    assert_allclose(actual, exact, rtol=2e-13, atol=1e-15)


def test_ideal_plate_energy_and_pressure_normalization():
    k, weights = spectral_quadrature(256)
    t = np.exp(-2*k)
    binding = -np.dot(weights*k*k, np.log(-np.expm1(-2*k)))/(4*np.pi**2)
    traction = np.dot(weights*k**3, t/(-np.expm1(-2*k)))/(2*np.pi**2)
    assert_allclose(binding, np.pi**2/1440, rtol=1e-10)
    assert_allclose(traction, np.pi**2/480, rtol=1e-10)


def test_disjoint_interaction_matches_direct_four_determinants():
    n, cut = 41, 20
    diagonal = np.full(n, 2.03)
    links = np.full(n-1, .99)
    left, right = np.zeros(n), np.zeros(n)
    left[11:16] = np.array([.1, .3, .5, .3, .1])
    right[26:31] = np.array([.2, .6, 1., .6, .2])
    matrix = np.diag(diagonal)-np.diag(links, 1)-np.diag(links, -1)
    direct = (np.linalg.slogdet(matrix+np.diag(left+right))[1]
              -np.linalg.slogdet(matrix+np.diag(left))[1]
              -np.linalg.slogdet(matrix+np.diag(right))[1]
              +np.linalg.slogdet(matrix)[1])
    actual = interaction_logdet(diagonal, links, left, right, cut)
    assert actual < 0
    assert_allclose(actual, direct, rtol=1e-8, atol=1e-13)


def test_material_integral_and_optical_response_converge():
    assert_allclose(gradient_integral(256), gradient_integral(512), rtol=1e-11)
    coarse = planar_interaction(10., .5, cells=128, nodes=128)
    fine = planar_interaction(10., .5, cells=256, nodes=256)
    assert fine['helpful_null'] > 0
    assert_allclose(coarse['binding'], fine['binding'], rtol=2e-4)
    step = 1e-3
    upper = planar_interaction(10*np.exp(step), .5, cells=256, nodes=256)
    lower = planar_interaction(10*np.exp(-step), .5, cells=256, nodes=256)
    derivative = (upper['binding']-lower['binding'])/(2*step)
    assert_allclose(derivative, fine['strength_derivative'], rtol=1e-6)


def test_interaction_metric_tangent_matches_direct_trace():
    n, cut = 41, 20
    diagonal, links = np.full(n, 2.2), np.full(n-1, .9)
    left, right = np.zeros(n), np.zeros(n)
    left[12:18], right[23:30] = .4, .6
    dd = .2*np.cos(np.arange(n)/9)
    de = .03*np.sin(np.arange(n-1)/8)
    matrix = np.diag(diagonal)-np.diag(links, 1)-np.diag(links, -1)
    derivative_matrix = np.diag(dd)-np.diag(de, 1)-np.diag(de, -1)
    expected = sum(sign*np.trace(np.linalg.solve(matrix+np.diag(v), derivative_matrix))
                   for sign, v in [(1, left+right), (-1, left), (-1, right), (1, np.zeros(n))])
    value, derivative = interaction_logdet(diagonal, links, left, right, cut, (dd, de))
    assert value < 0
    assert_allclose(derivative, expected, rtol=1e-7, atol=1e-13)
