import numpy as np
import pytest
from numpy.testing import assert_allclose

from adm_harness.constitutive_joints_and_optics import series_state
from adm_harness.finite_reaction_transport import SupportWithPhotons, finite_branch_power
from adm_harness.hosted_reaction_dynamics import HostedSupport, hosted_branch_power
from adm_harness.scheduled_optical_transfer import rotor_rhs, rotor_state
from adm_harness.shared_rail_reactions import total_trace_bound


def model(bias=.62):
    return HostedSupport(np.array([2., 20.]), np.array([1., 8.]), np.array([.01, .03]), .05625, bias)


def test_shifted_preload_recovers_original_constitutive_energy():
    m = model()
    trace = np.linspace(-.2, .3, 23)
    before = series_state(m.tension[:, None], m.core_inventory[:, None], m.joint_inventory[:, None], dimension=2)
    after = series_state(m.tension[:, None]+np.array([1., .5])[:, None]*(m.bias+trace)/3,
        m.core_inventory[:, None], m.joint_inventory[:, None], dimension=2)
    assert_allclose(m.state(trace)["energy"], (after["total_energy"]-before["total_energy"]).sum(axis=0)+m.bias,
                    atol=2e-14)


def test_parameterized_old_limit_matches_finite_branch():
    state = np.array([1.25, -.001, .75, .01])
    m = model(total_trace_bound())
    old = SupportWithPhotons(m.tension, m.core_inventory, m.joint_inventory, .05625)
    expected = finite_branch_power(state, .6, old, .04, .001)
    actual = hosted_branch_power(state, .6, m, .04, .001, damping=.4)
    for key in ("rotor_power", "support_power", "total_trace", "support_energy"):
        assert_allclose(actual[key], expected[key], atol=1e-13)


def test_hosted_coupled_energy_differentiates_to_external_network_power():
    state = np.array([1.25, -.001, .75, .01])
    m = model()
    q = hosted_branch_power(state, .6, m, .04, .001)
    rhs = rotor_rhs(state, q["rotor_power"], damping=.8)
    eps = 1e-6
    def energy(t):
        y = state+t*rhs
        r = hosted_branch_power(y, .6, m, .04+t*.001, .001)
        return 18*rotor_state(y)["energy"]+r["support_energy"]+.04+t*.001
    assert_allclose((energy(eps)-energy(-eps))/(2*eps), .6, rtol=2e-8)


def test_electric_and_complementary_ports_supply_exact_sheet_work():
    m = model()
    trace = np.linspace(-.2, .25, 13)
    rate = np.linspace(-.8, .7, 13)
    e = m.endpoints(trace, rate)
    assert e["capacitor_gap"].min() > 0
    assert e["complementary_field_energy"].min() > 0
    assert_allclose(e["mechanical_power"], m.state(trace)["derivative"]*rate, atol=2e-15)
    assert_allclose(e["terminal_work_error"], 0, atol=2e-15)


def test_electrode_ports_reject_an_insufficient_field_bias():
    m = model(total_trace_bound())
    trace = np.linspace(-m.trace_bound, m.trace_bound+m.line_ceiling, 41)
    with pytest.raises(ValueError, match="Maxwell channel"):
        m.endpoints(trace, np.zeros_like(trace))
