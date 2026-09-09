import numpy as np
import pytest
from scipy.integrate import simpson

from adm_harness.longitudinal_balance import (
    weighted_balance, lapse_box_upper_bound, lapse_box_from_integrals,
)


def geometry():
    l = np.linspace(-2., 3., 20001)
    r = 2+.04*l*l+.002*l**3
    rp = .08*l+.006*l*l
    rpp = .08+.012*l
    a = np.exp(.1*np.sin(l)+.025*l*l)
    ap = .1*np.cos(l)+.05*l
    app = -.1*np.sin(l)+.05
    return l, r, a, rp, rpp, ap, app


def test_weighted_identity_against_direct_einstein_and_cft_null_sources():
    l, r, a, rp, rpp, ap, app = geometry()
    k = .17
    result = weighted_balance(l, r, a, rp, rpp, ap, k, 2., .8)
    demanded_h = (ap*rp-rpp)/(4*np.pi*r)
    quantum_h = k/(4*np.pi*r*r)*(app-4*np.pi**2/(result['optical_length']**2*a*a))
    direct = 4*np.pi/k*simpson(result['weight']*r*r*(demanded_h-quantum_h), x=l)
    np.testing.assert_allclose(result['residual'], direct, rtol=2e-12, atol=1e-12)


def test_time_normalization_covariance_and_return_length_monotonicity():
    l, r, a, rp, rpp, ap, _ = geometry()
    first = weighted_balance(l, r, a, rp, rpp, ap, .17, 2., .8)
    scaled = weighted_balance(l, r, 53*a, rp, rpp, ap, .17, 2., .8/53)
    longer = weighted_balance(l, r, a, rp, rpp, ap, .17, 2., 8.)
    np.testing.assert_allclose(first['supply'], scaled['supply'], rtol=1e-14)
    assert longer['supply'] < first['supply']


def test_box_bound_contains_smooth_profiles_with_fixed_endpoint_jets():
    l, r, a, rp, rpp, ap, _ = geometry()
    base = weighted_balance(l, r, a, rp, rpp, ap, .17, 2.)
    mask = np.ones_like(l, dtype=bool)
    bound = lapse_box_upper_bound(l, a, base['weight'], mask, .5)
    t = (l-l[0])/(l[-1]-l[0])
    for mode in range(1, 9):
        changed = a*(1+.5*np.sin(np.pi*t)**2*np.cos(mode*np.pi*t))
        supply = 4*np.pi**2*simpson(base['weight']/changed**2, x=l)/simpson(1/changed, x=l)**2
        assert supply <= bound
    exact = lapse_box_upper_bound(l, a, base['weight'], mask, 0.)
    np.testing.assert_allclose(exact, base['supply'], rtol=1e-14)
    split = lapse_box_from_integrals(base['numerator'], base['optical_length'],
                                    base['numerator'], base['optical_length'], .5)
    np.testing.assert_allclose(split, bound, rtol=1e-14)


def test_flat_cylinder_with_radial_tension_and_zero_casimir_limit():
    l = np.linspace(-3., 3., 101)
    r, a, zero = l*0+2., l*0+1., l*0
    result = weighted_balance(l, r, a, zero, zero, zero, .1, 2., 1e20)
    assert result['required'] == 0
    assert 0 < result['supply'] < 1e-35


def test_ads2_cylinder_passes_the_integrated_necessary_gate():
    # Independent positive control with MMP's conformal clock and loop.
    # A constant-radius cylinder is a leading throat background, not its
    # backreacted full wormhole solution.
    radius, ell = 3., 400.
    l = np.linspace(-4*radius, 4*radius, 20001)
    r, zero = l*0+radius, l*0
    a = radius/ell*np.cosh(l/radius)
    ap = np.tanh(l/radius)/radius
    remainder = np.pi*ell-simpson(1/a, x=l)
    result = weighted_balance(l, r, a, zero, zero, ap, .1, radius, remainder)
    np.testing.assert_allclose(result['supply']/result['required'], 4., rtol=1e-12)
    assert result['residual'] > 0


def test_invalid_state_is_rejected():
    l, r, a, rp, rpp, ap, _ = geometry()
    with pytest.raises(ValueError):
        weighted_balance(l, r, a, rp, rpp, ap, -1., 2.)
    with pytest.raises(ValueError):
        lapse_box_upper_bound(l, a, np.ones_like(l), np.ones_like(l, dtype=bool), 1.)
