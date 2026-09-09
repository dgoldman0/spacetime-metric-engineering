"""Covariance, force exchange, and analytic controls for the joint equations."""
import numpy as np
from scipy.integrate import solve_ivp

from adm_harness.absolute_vacuum_control import AbsoluteRadialControl, flat_mode
from adm_harness.screened_condensate import CondensateParameters
from adm_harness.semiclassical_joint import (PV_WEIGHTS, pv_masses, curvature,
    coupled_rhs, radial_constraint, local_action_source, flat_renormalized_source)


def test_pauli_villars_cancels_all_three_ultraviolet_orders():
    for potential in (0., .4, 4.36):
        masses = potential+pv_masses(2.7)
        np.testing.assert_allclose([PV_WEIGHTS@masses**k for k in range(3)], 0., atol=1e-12)


def test_flat_and_product_geometry_curvature():
    r = 2.3
    jets = np.array([np.log(r), 1/r, -1/r**2, 2/r**3, -6/r**4])
    _, einstein, scalar, ricci2 = curvature(jets, np.zeros(5))
    np.testing.assert_allclose(einstein, 0., atol=1e-16)
    assert abs(scalar)+abs(ricci2) < 1e-15
    product = jets.copy(); product[1:] = 0.
    np.testing.assert_allclose(curvature(product, np.zeros(5))[1], [1/r**2, -1/r**2, 0.])


def test_local_variation_matches_constant_curvature_product():
    r = 2.3
    jr = np.array([np.log(r), 0., 0., 0., 0.])
    zero = np.zeros(5)
    # W=J R+k1 R^2+k2 Ricci^2 on R^(1,1) x S^2.
    j, k1, k2 = .2, .3, .4
    out = local_action_source(jr, zero, zero, [0., 0., 0., j, 0., k1, k2])
    f = 2*j/r**2+(4*k1+2*k2)/r**4
    np.testing.assert_allclose(out, [f, -f, (4*k1+2*k2)/r**4, 0.], rtol=1e-12)


def test_local_action_stress_and_force_obey_ward_identity():
    import sympy as sp
    x = sp.Symbol('x')
    expr = [sp.log(2+x+x*x/10), x/7+x*x/20, 1+x/3+x*x/5]
    functions = [sp.lambdify(x, [sp.diff(f, x, n) for n in range(5)], 'numpy') for f in expr]
    coefficients = [.1, -.3, .2, -.04, .07, .02, -.01]
    center, step = .31, 2e-4
    def evaluate(t):
        return local_action_source(*(np.array(fn(t)) for fn in functions), coefficients)
    values = np.array([evaluate(center+k*step) for k in (-2, -1, 0, 1, 2)])
    derivative = (values[0, 1]-8*values[1, 1]+8*values[3, 1]-values[4, 1])/(12*step)
    rho, pr, pt, polarization = values[2]
    rp, ap, vp = [fn(center)[1] for fn in functions]
    residual = derivative+ap*(rho+pr)+2*rp*(pr-pt)+.5*polarization*vp
    assert abs(residual) < 2e-10


def test_homogeneous_renormalization_conditions_and_force():
    m = 4.36
    np.testing.assert_allclose(flat_renormalized_source(m, m), 0., atol=1e-16)
    v, step = 1.7, 1e-4
    plus, center, minus = [flat_renormalized_source(z, m) for z in (v+step, v, v-step)]
    assert abs((plus[0]-minus[0])/step-center[3]) < 1e-10
    assert abs((flat_renormalized_source(m+step, m)[3]-
                flat_renormalized_source(m-step, m)[3])/(2*step)) < 1e-11


def test_quantum_force_preserves_radial_einstein_constraint():
    material = CondensateParameters()
    v, eta, omega, kappa, coefficient = 1.7, 2e-5, .7, 1.4, .03
    y = np.array([np.log(3.), .1, 0., 0., .5, .02, .4, -.03, .9, .01, 0.])
    def sources(y):
        mass = kappa*v*v*y[6]**2
        energy = coefficient*mass*mass
        return np.array([energy, -energy, -energy]), 4*coefficient*mass
    q, _ = sources(y)
    c = radial_constraint(y, omega, material, v, eta, q)
    y[3] -= c*8*np.pi/(2*y[1])
    def rhs(x, state):
        q, pol = sources(state)
        return coupled_rhs(x, state, omega, material, v, eta, q, pol, kappa)
    sol = solve_ivp(rhs, (0., .4), y, rtol=2e-11, atol=2e-13)
    assert sol.success
    residuals = [radial_constraint(state, omega, material, v, eta, sources(state)[0])
                 for state in sol.y.T]
    assert np.max(abs(np.array(residuals))) < 2e-12


def test_radial_modes_converge_to_exact_flat_bessel_control():
    exact = flat_mode(.7, 3, 2., 2., 1.)
    errors = []
    for step in (.04, .02, .01):
        p = AbsoluteRadialControl.flat(spacing=step, far_spacing=step)
        errors.append(np.max(abs(p.mode(.7, 3, 2.)-exact)))
    assert errors[1] < .3*errors[0]
    assert errors[2] < .3*errors[1]


def test_bessel_small_argument_large_order_fallback():
    import mpmath as mp
    mp.mp.dps = 55
    frequency, j, radius, scale = 1e-8, 128, 2., .03
    reference = []
    nu = mp.mpf(j)+mp.mpf('.5')
    for mass in pv_masses(scale):
        k = mp.sqrt(mp.mpf(frequency)**2+float(mass))
        z = k*radius
        iv, kv = mp.besseli(nu, z), mp.besselk(nu, z)
        green = iv*kv/radius
        pl = k*mp.besseli(nu-1, z)/iv-(nu+mp.mpf('.5'))/radius
        qr = -k*mp.besselk(nu-1, z)/kv-(nu+mp.mpf('.5'))/radius
        mixed, time = pl*qr*green, -mp.mpf(frequency)**2*green
        angle, potential = j*(j+1)*green/(2*radius**2), mass*green
        reference.append([(time+mixed+2*angle+potential)/2,
            (time+mixed-2*angle-potential)/2, (time-mixed-potential)/2, green])
    ref = [float(sum(int(c)*row[i] for c, row in zip(PV_WEIGHTS, reference))) for i in range(4)]
    np.testing.assert_allclose(flat_mode(frequency, j, scale, radius, 0.), ref, atol=2e-14, rtol=1e-6)
