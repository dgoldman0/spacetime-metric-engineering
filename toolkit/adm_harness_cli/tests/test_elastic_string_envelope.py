"""Causal one-state string stresses lie inside the conserved-bundle gate."""
import numpy as np
from numpy.testing import assert_allclose

from adm_harness.scalar_flux_support import equilibrium_vortex_interval


def test_integrated_causal_equations_of_state_fit_the_relaxed_bundle():
    rng = np.random.default_rng(921)
    for unused in range(30):
        mu = rng.uniform(.2, 3.)
        u = mu+np.linspace(0., 1.8*mu, 200)
        # Independently prescribe c_L^2=-dT/dU in [0,1] on every interval.
        speed_squared = rng.uniform(0., 1., len(u)-1)
        tension = mu-np.r_[0., np.cumsum(speed_squared*np.diff(u))]
        stable = tension >= 0.
        u, tension = u[stable], tension[stable]
        wave = mu-tension
        rest = u+tension-2*mu
        assert np.min(wave) >= -1e-14
        assert np.min(rest) >= -1e-14
        assert_allclose(mu+wave+rest, u, atol=2e-14)
        assert_allclose(-mu+wave, -tension, atol=2e-14)
        # Extra arbitrary positive old-basis sectors can coexist with the
        # elastic tube; a conserved amplitude remains in the exact interval.
        rho = u+.2+.3
        radial = -tension+.2
        angular = np.full_like(u, -.3)
        lo, hi = equilibrium_vortex_interval(rho, radial, angular, 1.)
        assert np.all(lo <= mu+1e-13)
        assert np.all(hi >= mu-1e-13)


def test_transonic_equation_of_state_and_superluminal_control():
    mu = 2.
    u = np.linspace(mu, 6*mu, 101)
    tension = mu*mu/u
    assert np.all(u+tension >= 2*mu-1e-14)
    # A slope steeper than -1 escapes this envelope by violating the
    # assumed causal longitudinal speed. It is a negative control.
    tension_superluminal = mu-1.2*(u-mu)
    assert np.all((u+tension_superluminal-2*mu)[1:] < 0.)
