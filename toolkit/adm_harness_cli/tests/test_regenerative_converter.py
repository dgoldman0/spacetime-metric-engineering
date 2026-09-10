"""Physical balances and necessary bounds of the converter inventory screen."""
import numpy as np
import pytest

from adm_harness.active_transfer_reservoir import MetricJets, divergence_projections
from adm_harness.graded_electrothermal import fixed_kinematics
from adm_harness.regenerative_converter import (
    compact_cell_moments, conversion_ports, finite_local_stores,
    proper_prefix, work_reserve_lower_bound,
)


def test_work_heat_and_loss_conserve_both_ports():
    charging = np.array([[3., -4., 0.]])
    net = np.array([[.2, -.3, -.8]])
    p = conversion_ports(charging, net, efficiency=.8, recovery=.5)
    np.testing.assert_allclose(p['converter_loss'], [[.75, .4, 0.]])
    np.testing.assert_allclose(p['bank_output']-p['receiver_input'], net)
    # Fluid receives prescribed net minus reversible field charging.
    np.testing.assert_allclose(p['endpoint_heat']+p['local_discharge_heat'], net-charging)
    assert np.all(p['converter_loss'] >= 0)
    assert p['bank_output'][0, 0] > 0 and p['endpoint_heat'][0, 0] < 0


def test_recovery_requires_heat_supply_when_fluid_must_keep_its_history():
    p = conversion_ports(np.array([[-4.]]), np.array([[0.]]), recovery=1.)
    assert p['bank_output'].item() == -4.
    assert p['endpoint_heat'].item() == 4.
    assert p['receiver_input'].item() == -4.


def test_capacity_uses_prefixes_including_initial_overcharge():
    t = np.arange(5.)
    # Withdrawal prefix: 0, -2, 1, -1, 0. Initial level differs from capacity.
    work = np.array([-2., 3., -2., 1.])[:, None]
    result = finite_local_stores(t, np.ones_like(work), work, -work, voltage_fraction=.5)
    np.testing.assert_allclose(result['bank_capacity'], [4.])
    np.testing.assert_allclose(result['bank_initial'], [2.])
    np.testing.assert_allclose(result['bank'].ravel(), [2., 4., 1., 3., 2.])
    np.testing.assert_allclose(result['heat'].ravel(), [1., 3., 0., 2., 1.])


def test_local_capacity_cannot_instantly_share_across_positions():
    work = np.array([[2., -2.], [-2., 2.]])
    result = finite_local_stores(np.arange(3.), np.ones_like(work), work, work, voltage_fraction=0.)
    np.testing.assert_allclose(result['bank_capacity'], [2., 2.])
    assert np.max(abs(work.sum(axis=1))) == 0.


def test_geometry_weight_and_combined_store_balance():
    t = np.array([0., .2, .7, 1.])
    weight = np.array([[2., 1.], [4., 3.], [1., 2.]])
    c = np.array([[2., -1.], [-3., 2.], [1., -4.]])
    e = np.array([[.1, -.4], [-.3, .7], [.5, .2]])
    p = conversion_ports(c, e, efficiency=.95, recovery=.7)
    s = finite_local_stores(t, weight, p['bank_output'], p['receiver_input'])
    total = s['bank']+s['heat']
    np.testing.assert_allclose(total-total[0], -proper_prefix(t, weight, e), atol=1e-15)


def test_lower_bound_covers_arbitrary_variable_recovery():
    rng = np.random.default_rng(391)
    t = np.linspace(0., 2., 31)
    charging = rng.normal(size=(30, 5))
    weight = rng.uniform(.5, 2., size=charging.shape)
    bound = work_reserve_lower_bound(t, weight, charging, efficiency=.96, voltage_fraction=.6)
    for unused in range(12):
        ports = conversion_ports(charging, np.zeros_like(charging), efficiency=.96,
                                 recovery=rng.uniform(size=charging.shape))
        s = finite_local_stores(t, weight, ports['bank_output'], ports['receiver_input'], voltage_fraction=.6)
        assert np.all(s['bank_initial'] >= bound['initial_work']-1e-14)
        assert np.all(s['bank_capacity'] >= bound['bank_capacity']-1e-14)


def test_compact_cell_energy_and_acceleration_match_covariant_divergence():
    # An analytic time-dependent spherical metric with finite nonzero shift.
    def geometry(t, x):
        alpha = np.exp(.15*t+.1*x)
        b = np.exp(-.2*t+.08*x)
        radius = np.exp(.12*t+.07*x)
        beta = .13*np.ones_like(x)
        return MetricJets(alpha, beta, b, radius, .1*alpha, np.zeros_like(x),
                          -.2*np.ones_like(x), .08*np.ones_like(x),
                          .12*np.ones_like(x), .07*np.ones_like(x))

    def fields(t, x):
        g = geometry(t, x)
        v, gamma, lapse, acceleration, unused = fixed_kinematics(g, .15*g.alpha, np.zeros_like(x))
        c = dict(v=v, gamma=gamma, rest_volume=gamma*g.volume)
        energy = 2.+.3*t+.11*x
        return g, c, lapse, acceleration, energy

    def tensor(t, x):
        g, c, lapse, acceleration, energy = fields(t, x)
        return compact_cell_moments(energy, c)

    t, x, eps = .4, np.array([-.2, .3]), 1e-5
    g, c, lapse, acceleration, energy = fields(t, x)
    p, f = divergence_projections(g, tensor(t, x),
        (tensor(t+eps, x)-tensor(t-eps, x))/(2*eps),
        (tensor(t, x+eps)-tensor(t, x-eps))/(2*eps))
    rest_power = c['gamma']*(p-c['v']*f)
    rest_force = c['gamma']*(f-c['v']*p)
    np.testing.assert_allclose(rest_power, .3/(lapse*c['rest_volume']), rtol=1e-8)
    np.testing.assert_allclose(rest_force, energy/c['rest_volume']*acceleration, rtol=1e-8)


@pytest.mark.parametrize('efficiency,recovery', [(0., 1.), (1.01, 0.), (.9, -1.), (.9, 1.1)])
def test_unphysical_conversion_parameters_rejected(efficiency, recovery):
    with pytest.raises(ValueError):
        conversion_ports([[1.]], [[0.]], efficiency=efficiency, recovery=recovery)
