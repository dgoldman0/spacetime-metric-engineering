import numpy as np

from adm_harness.composite_capacitor import anisotropic_moments
from adm_harness.conserved_radial_prestress import admissible_amplitude, minimum_member_fraction


def test_complete_interval_and_radial_enthalpy_obstruction():
    r = np.array([2., 3.]); rho = np.array([1., 2.]); p = np.array([2., -1.]); q = np.zeros(2)
    result = admissible_amplitude(r, rho, p, q, .9)
    for amplitude in (result['lower'], result['upper']):
        s = amplitude/r**2
        assert np.max(abs(p-s)-.9*(rho+s)) < 1e-12
    assert abs(p[0]-(result['lower']-.01)/r[0]**2) > .9*(rho[0]+(result['lower']-.01)/r[0]**2)
    assert abs(p[1]-(result['upper']+.01)/r[1]**2) > .9*(rho[1]+(result['upper']+.01)/r[1]**2)
    assert not admissible_amplitude(r, rho, -rho-.1, q, 1.)['feasible']
    f = minimum_member_fraction(r, rho, p, q)
    assert admissible_amplitude(r, rho, p, q, f+1e-8)['feasible']
    assert not admissible_amplitude(r, rho, p, q, f-1e-8)['feasible']


def test_covariant_increment_and_boost_invariance():
    t = np.linspace(0., 1., 19); x = np.linspace(-1., 1., 19)
    r = np.exp(.2*t+.1*x); ell = np.exp(-.3*t+.07*x)
    lapse = 1.2+.1*t; velocity = -.2+.1*x
    k = velocity/lapse*.2+.1/ell
    rho = 2.3/r**2; mass = 2.3*ell
    force = 2*rho*k+2*(-rho)*k
    power = (-.3*mass+(-mass)*(-.3))/(lapse*ell*r*r)
    assert np.max(abs(force)) < 1e-14
    assert np.max(abs(power)) < 1e-14
    tensor = anisotropic_moments(rho, -rho, np.zeros_like(rho), velocity)
    np.testing.assert_allclose(tensor[0], rho)
    np.testing.assert_allclose(tensor[1], -rho)
    np.testing.assert_allclose(tensor[2], 0., atol=1e-14)
