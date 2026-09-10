"""Independent energy and Maxwell controls for finite work interfaces."""
import numpy as np
import pytest

from adm_harness.finite_work_interface import (
    capacitor_port, capacitor_step_work, port_reflection,
    reflected_guide_factor, toroidal_bend_factors,
)


def test_frozen_capacitor_exponential_charge_matches_and_conserves_port_energy():
    t = np.linspace(0, 2, 71)
    capacitance, impedance = .7, 3.
    charge = np.exp(t/(impedance*capacitance))
    port = capacitor_port(charge, capacitance, charge/(impedance*capacitance))
    np.testing.assert_allclose(port_reflection(port['load_admittance'], impedance), 0., atol=2e-16)
    a = (port['voltage']+impedance*port['current'])/2
    np.testing.assert_allclose(a*a/impedance, port['electrical_power'])


def test_geometric_capacitance_change_is_mechanical_work_at_fixed_charge():
    electric, mechanical, change = capacitor_step_work(2., 2., .2, .9)
    assert electric == 0.
    np.testing.assert_allclose(mechanical, change)
    np.testing.assert_allclose(change, 1.4)


def test_two_port_discrete_energy_identity_for_general_cell_history():
    rng = np.random.default_rng(294)
    q, k = np.exp(rng.normal(size=(2, 51, 7)))
    electric, mechanical, change = capacitor_step_work(q[:-1], q[1:], k[:-1], k[1:])
    np.testing.assert_allclose(electric+mechanical, change, atol=2e-13)


def test_guide_factor_from_independent_crossed_fields():
    for r in (0., .01, .05, .1):
        energy = reflected_guide_factor(r, .5)
        e = 1+r
        b2 = (1-r)**2+2*energy
        np.testing.assert_allclose(e/np.sqrt(b2), .5)


def test_annular_bend_flux_and_energy_against_volume_quadrature():
    # Direct cylindrical field integration independently reconstructs factors.
    b, a, straight = .05, .01, 2.
    radius = np.linspace(b-a, b+a, 10001)
    flux_integral = np.trapezoid(1/radius, radius)
    constant = 2*a*straight/flux_integral
    field = constant/radius
    np.testing.assert_allclose(np.trapezoid(field, radius), 2*a*straight)
    energy = np.pi*np.trapezoid(.5*field**2*radius, radius)
    factor = toroidal_bend_factors(a/b)
    np.testing.assert_allclose(energy/(.5*straight**2*2*a*np.pi*b), factor['energy_factor'], rtol=1e-9)
    np.testing.assert_allclose((field[0]/straight)**2, factor['peak_energy_factor'], rtol=1e-9)


def test_recovery_is_distinct_from_passive_receiving_reflection():
    with pytest.raises(ValueError):
        port_reflection(-.5, 1.)
