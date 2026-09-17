import numpy as np
import pytest
from numpy.testing import assert_allclose

from adm_harness.constitutive_joints_and_optics import series_state
from adm_harness.coupled_rail_reactions import (
    FrozenReaction, coupled_power, guide_trace_rate, scalar_sheet_state,
)
from adm_harness.scheduled_optical_transfer import inverse_guide, rotor_rhs, rotor_state
from adm_harness.shared_rail_reactions import reaction_state


def test_scalar_inversion_agrees_with_conserved_series_law():
    for inventory, joints in ((.1, .0025), (10., .06), (100., .3)):
        for tension in (0., .01, 1., 100., 1000.):
            got = scalar_sheet_state(tension, inventory, joints)
            expected = series_state(tension, inventory, joints, dimension=2)
            assert_allclose(got["energy"], expected["total_energy"], rtol=2e-12)
            assert_allclose(got["derivative"], expected["core_energy_derivative"]
                            +expected["joint_energy_derivative"], rtol=2e-11, atol=1e-14)
            assert_allclose(got["joint_stretch"], expected["joint_stretch"], rtol=2e-11)


def test_scalar_solver_rejects_unresolved_force_capacity():
    with pytest.raises(ValueError, match="resolved joint force margin"):
        scalar_sheet_state(1000., .1, .001)


def test_frozen_reaction_uses_exact_shared_state_energy_and_derivative():
    model = FrozenReaction(np.array([4., 12000.]), np.array([.7, 16.]), np.array([.006, .13]))
    for trace in (-.2, 0., .2):
        got = model.state(trace)
        expected = reaction_state(trace, model.trace_bound/3,
            model.tension, model.core_inventory, model.joint_inventory)
        assert_allclose(got["energy"], expected["additional_energy"], atol=4e-11)
        assert_allclose(got["derivative"], expected["energy_trace_derivative"], rtol=3e-13)


def test_guide_trace_derivative_matches_independent_finite_difference():
    for left, right in ((.001, 1.001), (1.001, .001)):
        for time in (2., 40., 110.):
            step = .001
            derivative = (inverse_guide(time+step, left, right)["pressure_trace"]
                          -inverse_guide(time-step, left, right)["pressure_trace"])/(2*step)
            assert_allclose(guide_trace_rate(inverse_guide(time, left, right)), derivative, atol=4e-13)


def test_coupled_input_obeys_independently_differentiated_total_energy():
    model = FrozenReaction(np.array([4., 100.]), np.array([.7, 16.]), np.array([.006, .13]))
    y = np.array([1.22, .001, np.sqrt(1.22**2-1-2e-4), 1e-4])
    for network in (-1., .2, 1.):
        c = coupled_power(y, network, model)
        rhs = rotor_rhs(y, c["rotor_power"])
        def energy(z):
            s = rotor_state(z)
            trace = 18*(s["pressure_trace"]-.4*z[0]*z[1])
            return 18*s["energy"]+model.state(trace)["energy"]
        step = 1e-6
        derivative = (energy(y+step*rhs)-energy(y-step*rhs))/(2*step)
        assert_allclose(derivative, network, atol=5e-8)
        assert_allclose(c["rotor_power"]+c["reaction_power"], network, atol=3e-16)
