import numpy as np
import pytest
from scipy.integrate import solve_ivp

from adm_harness.comer_two_current import (
    TwoCurrentDomain, EvolutionDomainError, conserved_integrals, evolve,
    fluid_moments, metric_and_fluids, recover_fluid, resistance, rhs,
)


def static_domain(cells, drift=0.):
    faces = np.linspace(2., 4., cells+1)
    r = .5*(faces[:-1]+faces[1:])
    rn, rs = np.full(cells, .0005), np.full(cells, .0003)
    wn, ws = .2, 1/3
    support = .5*((1+3*wn)*rn+(1+3*ws)*rs)
    total = support+rn+rs
    mass = 4*np.pi*total*r**3/3
    face_mass = 4*np.pi*total[0]*faces**3/3
    pressure = -total/3
    domain = TwoCurrentDomain(r, faces, np.diff(faces**3)/3, mass, face_mass,
        np.ones(cells), pressure, pressure, rn+rs, support, -support)
    v = drift*np.sin(np.pi*(r-2)/2)**2
    j = rn*(1+wn)*v/(1+wn*v*v)
    state = np.r_[np.stack([rn, j, rs, -j], axis=-1).ravel(), 0.]
    return domain, state


def test_exact_two_fluid_moments_and_timelike_domain():
    rest = np.geomspace(1e-10, 1e-2, 71)
    velocity = np.linspace(-.97, .97, 71)
    for w in [.2, 1/3]:
        tensor = fluid_moments(rest, velocity, w)
        rho, v, _ = recover_fluid(tensor[:, 0], tensor[:, 1], w)
        np.testing.assert_allclose(rho, rest, rtol=1e-13)
        np.testing.assert_allclose(v, velocity, rtol=1e-13)
        np.testing.assert_allclose((tensor[:, 0]+tensor[:, 2])**2-4*tensor[:, 1]**2,
                                   ((1+w)*rest)**2, rtol=1e-10)
    with pytest.raises(EvolutionDomainError):
        recover_fluid(np.array([1.]), np.array([1.]), 1/3)


def test_covariant_drag_conserves_particles_and_creates_entropy():
    vn, vs = np.linspace(-.6, .4, 31), np.linspace(.5, -.2, 31)
    rn, rs = np.full(31, .03), np.full(31, .02)
    re, rj, entropy_rate, relative_gamma = resistance(rn, vn, rs, vs, .7)
    gn, gs = 1/np.sqrt(1-vn*vn), 1/np.sqrt(1-vs*vs)
    np.testing.assert_allclose(-gn*re+gn*vn*rj, 0., atol=1e-17)
    temperature = (4/3)*rs**.25
    np.testing.assert_allclose(-gs*re+gs*vs*rj, temperature*entropy_rate, rtol=1e-13)
    assert np.min(entropy_rate) >= 0
    assert np.min(relative_gamma) >= 1


def test_nonlinear_homogeneous_relaxation_obeys_both_current_balances():
    n0 = fluid_moments(.02, .3, .2)
    s0 = fluid_moments(.015, -.2, 1/3)
    initial = np.r_[n0[:2], s0[:2], 0.]
    def equation(t, y):
        rn, vn, gn = recover_fluid(y[0], y[1], .2)
        rs, vs, gs = recover_fluid(y[2], y[3], 1/3)
        re, rj, creation, _ = resistance(rn, vn, rs, vs, .5)
        return [re, rj, -re, -rj, creation]
    solution = solve_ivp(equation, (0., 3.), initial, method='DOP853', rtol=1e-11, atol=1e-13)
    assert solution.success
    y = solution.y
    np.testing.assert_allclose(y[0]+y[2], initial[0]+initial[2], atol=1e-14)
    np.testing.assert_allclose(y[1]+y[3], initial[1]+initial[3], atol=1e-14)
    rn, vn, gn = recover_fluid(y[0], y[1], .2)
    rs, vs, gs = recover_fluid(y[2], y[3], 1/3)
    number, entropy = rn**(1/1.2)*gn, rs**.75*gs
    np.testing.assert_allclose(number, number[0], rtol=1e-10)
    np.testing.assert_allclose(entropy-entropy[0], y[4], atol=1e-11)
    assert abs(vn[-1]-vs[-1]) < .01*abs(vn[0]-vs[0])


def test_signed_support_is_covariantly_conserved_for_arbitrary_polar_metric():
    import sympy as sp
    t, r, theta, phi = sp.symbols('t r theta phi', positive=True)
    coordinates = [t, r, theta, phi]
    lapse, radial = sp.Function('N')(t, r), sp.Function('A')(t, r)
    energy = sp.Function('I')(r)
    metric = sp.diag(-lapse**2, radial**2, r**2, r**2*sp.sin(theta)**2)
    inverse = metric.inv()
    mixed = sp.diag(-energy, -energy, -energy-r*energy.diff(r)/2, -energy-r*energy.diff(r)/2)
    for b in range(4):
        divergence = sp.diff(mixed[b, b], coordinates[b])
        for a in range(4):
            gamma = sum(inverse[a, k]*(sp.diff(metric[k, b], coordinates[a])
                +sp.diff(metric[k, a], coordinates[b])-sp.diff(metric[a, b], coordinates[k]))/2 for k in range(4))
            divergence += gamma*(mixed[b, b]-mixed[a, a])
        assert sp.simplify(divergence) == 0


def test_static_einstein_control_stays_static_with_two_independent_currents():
    domain, initial = static_domain(48)
    rate, fields, _ = rhs(domain, initial, .7)
    assert np.max(abs(rate)) < 1e-16
    np.testing.assert_allclose(fields['alpha'], 1., atol=1e-14)
    result = evolve(domain, initial, .7, duration=.5, snapshots=3)
    np.testing.assert_allclose(result['state'], initial, atol=1e-15)
    assert result['records'][-1]['max_current'] < 1e-16


def test_coupled_counterflow_converges_in_particle_and_entropy_balance():
    errors = []
    for cells in [32, 64]:
        domain, initial = static_domain(cells, drift=.04)
        result = evolve(domain, initial, .7, duration=.6, snapshots=13)
        assert result['status'] == 'duration_completed'
        row = result['records'][-1]
        assert row['created_entropy'] > 0 and row['max_mass_change'] > 0
        assert row['min_f'] > 0 and row['min_entropy_creation'] >= 0
        errors.append(max(abs(row['particle_balance_relative_error']), abs(row['entropy_balance_relative_error'])))
    assert errors[-1] < .6*errors[0]
    assert errors[-1] < 1e-4
