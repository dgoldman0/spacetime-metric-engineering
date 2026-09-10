import numpy as np
import pytest

from adm_harness.active_transfer_reservoir import divergence_projections
from adm_harness.graded_electrothermal import fixed_kinematics, maximum_null
from adm_harness.pressure_linked_storage import (
    balanced_end_witness, fluid_moments, minimum_positive_pressure, reduced_divergence, solve_connected_schedule,
)
from test_graded_electrothermal import jets


def test_connected_pressure_path_counts_accumulated_self_weight():
    errors = []
    for nodes in (129, 257):
        x = np.linspace(0, 2, nodes)
        p, integral = minimum_positive_pressure(x, np.ones(nodes)*2, -np.ones(nodes)*.3)
        exact = .15*(np.exp(2*(2-x))-1)
        errors.append(abs(p-exact).max())
        assert p.min() == 0
        np.testing.assert_allclose(integral, 2*x)
    assert 3.9 < errors[0]/errors[1] < 4.1


def test_mixed_signed_load_selects_positive_minimum_inside_path():
    x = np.linspace(-1, 1, 257)
    p, _ = minimum_positive_pressure(x, x*0, 2*x)
    np.testing.assert_allclose(p, x*x, atol=2e-15)


def coefficient_point(t, x):
    g, dt = jets(t, x)
    v, gamma, lapse, acc, angular = fixed_kinematics(g, dt[0], dt[1])
    vt = v*(g.logb_t-dt[0]/g.alpha)+g.b*dt[1]/g.alpha
    rate = g.logb_t+2*g.logr_t+gamma**2*v*vt
    return dict(v=v, gamma=gamma, lapse=lapse, b=g.b, radius=g.radius, alpha=g.alpha,
                acceleration=acc, rest_volume=gamma*g.b*g.radius**2, volume_rate=rate)


@pytest.mark.parametrize('t,x', [(.1, -.7), (.7, -1.1), (1.2, -.5)])
def test_fluid_and_field_rest_divergence_matches_covariant_tensor(t, x):
    def fields(time, position):
        return (1.1+.13*np.cos(position), 1.3+.2*time+.11*position**2,
                .7-.03*time+.08*position)
    def tensor(time, position):
        number, u, h = fields(time, position)
        return fluid_moments(u, h, number, coefficient_point(time, position))
    step = 1e-5
    g, _ = jets(t, x)
    c = coefficient_point(t, x)
    number, u, h = fields(t, x)
    def pressure(time, position):
        return fields(time, position)[1]/(3*coefficient_point(time, position)['rest_volume'])
    px = (pressure(t, x+step)-pressure(t, x-step))/(2*step)
    expected_p, expected_f = reduced_divergence(c, number, u, .2, px, -.03, .08)
    power, force = divergence_projections(g, tensor(t, x),
        (tensor(t+step, x)-tensor(t-step, x))/(2*step),
        (tensor(t, x+step)-tensor(t, x-step))/(2*step))
    np.testing.assert_allclose([c['gamma']*(power-c['v']*force),
                               c['gamma']*(force-c['v']*power)],
                              [expected_p, expected_f], rtol=1e-7, atol=1e-10)


def test_joint_energy_and_force_rows_cancel_the_endpoint_divergence_with_shift():
    c = coefficient_point(.7, -1.1)
    number, u, ut, px = 1.1, 1.4, -.3, .12
    power, force = .27, -.19
    source = -c['alpha']*c['rest_volume']*(power-c['v']*force)
    ce = c['gamma']*c['b']/c['radius']**2
    ht = (source-ut-c['volume_rate']*u/3)/ce
    hx = (c['radius']**4*px+c['radius']**2*c['acceleration']*(number+4*u/3)
          +4/3*c['v']*c['radius']**2/c['lapse']*ut+c['b']*c['radius']**4*force)
    energy, momentum = reduced_divergence(c, number, u, ut, px, ht, hx)
    np.testing.assert_allclose([energy, momentum],
        [-c['gamma']*(power-c['v']*force), -c['gamma']*(force-c['v']*power)], atol=1e-13)


def test_integrated_end_identity_keeps_time_dependent_shift_terms():
    x = np.linspace(-1.3, -.9, 21)
    t, number, thermal, field, rate = .7, 1.1, 1.4, .7, .23
    c = {key: [] for key in coefficient_point(t, x[0])}
    logrx = []
    for position in x:
        cc = coefficient_point(t, position)
        for key in c:
            c[key].append(float(cc[key]))
        logrx.append(float(jets(t, position)[0].logr_x))
    c = {key: np.array(value) for key, value in c.items()}
    c['source'] = -.27*c['alpha']*c['rest_volume']
    c['normal_force'] = np.ones(len(x))*(-.19)
    witness = balanced_end_witness(x, c, np.ones(len(x))*number, np.array(logrx))
    ht = -rate*field
    ut = c['source']-c['volume_rate']*thermal/3-c['rest_volume']/c['radius']**4*ht
    px = .12
    hx = (c['radius']**4*px+c['radius']**2*c['acceleration']*(number+4*thermal/3)
          +4/3*c['v']*c['radius']**2/c['lapse']*ut+c['b']*c['radius']**4*c['normal_force'])
    electric = field/c['radius']**4
    q = thermal/(3*c['rest_volume'])-electric
    qx = px-hx/c['radius']**4+4*electric*np.array(logrx)
    br = 4*c['v']*c['rest_volume']*rate/(3*c['lapse']*c['radius']**2)
    lhs = qx+witness['coefficient']*q+(witness['coefficient']-4*np.array(logrx)+br)*electric
    np.testing.assert_allclose(lhs, witness['drive'], atol=2e-13)


def flat_coefficients(nt, nx, rate=0.):
    one, zero = np.ones((nt, nx)), np.zeros((nt, nx))
    return dict(v=zero, gamma=one, lapse=one, b=one, radius=one*2, alpha=one,
                acceleration=zero, rest_volume=one*4, volume_rate=one*rate,
                c=one/4, d=zero, a=zero, source=zero.copy(), force=zero.copy())


def test_static_balanced_field_and_fluid_need_no_external_traction():
    t, x = np.linspace(0, 1, 9), np.linspace(0, 1, 9)
    c = flat_coefficients(len(t), len(x))
    result = solve_connected_schedule(t, x, c, np.ones(len(x)), np.ones(len(x))*3,
                                     ends='balanced')
    assert result['success'], result
    np.testing.assert_allclose(result['thermal'], 3., atol=3e-5)
    np.testing.assert_allclose(result['flux_energy'], 4., atol=3e-5)
    stress = fluid_moments(result['thermal'], result['flux_energy'], np.ones(len(x)), c)
    np.testing.assert_allclose(stress[1], 0., atol=2e-6)
    np.testing.assert_allclose(result['optimal_supplied_null_peak'], 1.75, atol=1e-8)
    assert result['primary_dual_gap'] < 1e-8


def test_no_field_constant_forced_thermal_profile_is_conserved():
    t, x = np.linspace(0, .5, 9), np.linspace(0, 1, 9)
    c = flat_coefficients(len(t), len(x))
    c['source'][:] = -.1
    initial = 3+.12*x
    # H_x-R^4*p_x=16*F_normal = -16*.12/(3*4).
    c['force'][:] = -.16
    result = solve_connected_schedule(t, x, c, np.ones(len(x)), initial,
                                     flux_floor=0., conductivity_ceiling=None)
    assert result['success'], result
    np.testing.assert_allclose(result['thermal'], initial[None, :]-.1*t[:, None], atol=3e-5)
    np.testing.assert_allclose(result['flux_energy'], 0., atol=3e-5)


def test_closed_uniform_force_has_no_fixed_rest_solution():
    t, x = np.linspace(0, 1, 5), np.linspace(0, 1, 5)
    c = flat_coefficients(len(t), len(x))
    c['force'][:] = .1
    result = solve_connected_schedule(t, x, c, np.ones(len(x)), np.ones(len(x))*3,
                                     ends='balanced', initial_mode='prepared')
    assert not result['success']
    assert result['status'] == 2


def test_thermal_pressure_and_field_obey_directional_null_formula():
    rng = np.random.default_rng(10337)
    c = flat_coefficients(1, 29)
    c['v'][:] = rng.uniform(-.6, .6, c['v'].shape)
    c['gamma'] = 1/np.sqrt(1-c['v']**2)
    c['rest_volume'] = c['gamma']*4
    u, h, number = rng.uniform(.1, 2, (3, 1, 29))
    stress = fluid_moments(u, h, number, c)
    peak, z = maximum_null(stress)
    direct = (number+4*u/3)/c['rest_volume']*c['gamma']**2*(1-c['v']*z)**2
    direct += 2*h/c['radius']**4*(1-z*z)
    np.testing.assert_allclose(peak, direct, atol=1e-14)


def test_adiabatic_homogeneous_expansion_retains_pressure_work():
    # A homogeneous expanding transverse area makes D=e^(rate*t), with
    # exact U=e^(-rate*t/kappa) and constant H for vanishing exchange.
    errors = []
    for steps in (16, 32):
        t, x, rate = np.linspace(0, 1, steps+1), np.linspace(0, 1, 5), .3
        c = flat_coefficients(len(t), len(x), rate)
        c['radius'] = np.broadcast_to(2*np.exp(rate*t[:, None]/2), c['radius'].shape)
        c['rest_volume'] = c['radius']**2
        c['c'] = 1/c['radius']**2
        result = solve_connected_schedule(t, x, c, np.ones(len(x)), np.ones(len(x))*3,
                                         flux_floor=0., conductivity_ceiling=None)
        assert result['success'], result
        # The primary optimum is initially fixed; the secondary selects H=0.
        np.testing.assert_allclose(result['flux_energy'], 0., atol=2e-5)
        errors.append(abs(result['thermal'][-1, 2]-3*np.exp(-rate/3)))
    assert 1.8 < errors[0]/errors[1] < 2.2


def test_direct_endpoint_work_gate_prevents_unfunded_field_charging():
    t, x = np.linspace(0, .5, 9), np.linspace(0, 1, 9)
    c = flat_coefficients(len(t), len(x))
    # A time-growing body-force gradient rewards growing H at the left end.
    c['force'] = np.broadcast_to(-.3*t[:, None], c['force'].shape)
    free = solve_connected_schedule(t, x, c, np.ones(len(x)), np.ones(len(x))*3,
        passive=False, conductivity_ceiling=1., charging_policy='unrestricted')
    gated = solve_connected_schedule(t, x, c, np.ones(len(x)), np.ones(len(x))*3,
        passive=False, conductivity_ceiling=1., charging_policy='endpoint_work')
    assert free['success'] and gated['success']
    assert np.diff(free['flux_energy'], axis=0).max() > 1e-4
    assert np.diff(gated['flux_energy'], axis=0).max() < 1e-8
    rate = np.log(free['flux_energy'][1:]/free['flux_energy'][:-1])/(2*np.diff(t)[:, None])
    assert abs(rate).max() < 1.0001
