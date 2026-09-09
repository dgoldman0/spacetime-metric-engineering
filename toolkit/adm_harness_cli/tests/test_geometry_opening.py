import numpy as np
import pytest
from adm_harness.geometry_opening import StaticSlice
from adm_harness.longitudinal_balance import weighted_balance


def example(x):
    l = 2*np.sinh(x)
    b = 2*np.cosh(x)
    r = np.sqrt(4+l*l)
    a = np.exp(.03*l*l+.04*l)
    return l, r, a, b


def test_coordinate_gate_against_analytic_proper_geometry():
    x = np.linspace(-1., 1.2, 8001)
    l, r, a, b = example(x)
    chart = StaticSlice(x, r, a, b)
    computed = chart.quadrature(-.9, 1.1, .08).balance(.08, .7)
    proper = np.linspace(2*np.sinh(-.9), 2*np.sinh(1.1), 40001)
    rr = np.sqrt(4+proper*proper)
    reference = weighted_balance(proper, rr, np.exp(.03*proper*proper+.04*proper),
        proper/rr, 4/rr**3, .06*proper+.04, .08, 2., .7)
    for key in ('supply', 'required', 'optical_length'):
        np.testing.assert_allclose(computed[key], reference[key], rtol=2e-8)
    assert computed['curvature_identity_error'] < 2e-8
    assert computed['einstein_cft_identity_error'] < 2e-8


def test_small_kappa_quadrature_and_clock_normalization():
    x = np.linspace(-2., 2., 1001)
    r, a, b = np.sqrt(4+x*x), np.exp(.04*x), np.ones_like(x)
    first = StaticSlice(x, r, a, b)
    scaled = StaticSlice(x, r, 97*a, b)
    for k in (1e-7, .01, .5):
        q8 = first.quadrature(-1.8, 1.8, k, order=8).balance(k)
        q16 = first.quadrature(-1.8, 1.8, k, order=16).balance(k)
        qscaled = scaled.quadrature(-1.8, 1.8, k).balance(k)
        np.testing.assert_allclose(q8['supply'], q16['supply'], rtol=1e-9)
        np.testing.assert_allclose(q8['required'], q16['required'], rtol=1e-9)
        np.testing.assert_allclose(q8['supply_over_required'], qscaled['supply_over_required'], rtol=1e-10)


def test_endpoints_remain_in_first_derivative_identity():
    x = np.linspace(-.5, .6, 4001)
    chart = StaticSlice(x, np.sqrt(4+x*x), np.exp(.3*x*x), np.ones_like(x))
    result = chart.quadrature(-.4, .5, 1.3).balance(1.3)
    assert result['radial_endpoint'] > .1
    assert result['clock_endpoint'] > .1
    assert result['curvature_identity_error'] < 1e-8
    assert result['einstein_cft_identity_error'] < 1e-8


def test_static_tensor_matches_analytic_ultrastatic_throat():
    x = np.linspace(-3., 3., 8001)
    r = np.sqrt(4+x*x)
    chart = StaticSlice(x, r, np.ones_like(x), np.ones_like(x))
    q = chart.quadrature(-2., 2., .1)
    result = q.tensor_summary()
    expected_minimum = -1/(32*np.pi)
    np.testing.assert_allclose(result['minimum_density'], expected_minimum, rtol=2e-6)
    np.testing.assert_allclose(result['minimum_radial_null'], 2*expected_minimum, rtol=2e-6)
    # Second derivatives of the logarithmic cubic interpolant have O(dx²) error.
    assert abs(result['minimum_angular_null']) < 2e-9


def test_invalid_slice_is_rejected():
    x = np.linspace(-1., 1., 31)
    with pytest.raises(ValueError):
        StaticSlice(x, x, x*0+1, x*0+1)
    chart = StaticSlice(x, np.sqrt(4+x*x), x*0+1, x*0+1)
    with pytest.raises(ValueError):
        chart.quadrature(-2., 2., .1)
