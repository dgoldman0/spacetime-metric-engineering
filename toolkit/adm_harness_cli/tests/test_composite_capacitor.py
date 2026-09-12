import numpy as np
from numpy.testing import assert_allclose

from adm_harness.composite_capacitor import (
    adiabatic_balancing_support, anisotropic_moments, charged_skin_eos,
    charged_skin_work, controlled_balancing_support, local_mechanical_reuse,
    prepared_skin_backing, pressure_shared_floor, retained_support_energy,
)
from adm_harness.finite_work_interface import capacitor_step_work


def test_skin_pressure_follows_area_variation_at_fixed_particle_number():
    area, number, tension, coefficient = 3., 2., .8, .4
    sigma, pressure = charged_skin_eos(tension, number/area, coefficient)
    energy = lambda a: tension*a+coefficient*number**1.5/np.sqrt(a)
    step = 1e-5
    assert_allclose(sigma*area, energy(area))
    assert_allclose(pressure, -(energy(area+step)-energy(area-step))/(2*step), rtol=1e-9)
    # Positive surface pressure is bounded by half the energy; a tension
    # dominated skin supplies the other sign without a compressive membrane.
    assert pressure < 0
    assert pressure <= sigma/2


def test_charge_injection_has_counted_chemical_work():
    area = np.array([4., 3., 3.5])[:, None]
    number = np.array([2., 2.5, 1.])[:, None]
    chemical, mechanical, energy = charged_skin_work(area, number, .8, .4)
    assert_allclose(chemical+mechanical, np.diff(energy, axis=0), atol=2e-15)
    fixed, unused, unused = charged_skin_work(area, np.ones_like(area), .8, .4)
    assert_allclose(fixed, 0.)
    assert np.max(abs(chemical)) > .1


def test_passive_backing_reproduces_inverse_length_compression_and_minimal_preparation():
    ell = np.array([4., 2., 1.])[:, None]
    r = np.ones_like(ell)*2
    electric = np.array([2., 3., 1.])[:, None]
    state = prepared_skin_backing(electric, ell, r)
    assert_allclose(state['skin_energy'][:, 0], [3., 3., 3.])
    assert_allclose(state['backing_energy'][:, 0], [2., 4., 8.])
    assert np.min(state['excess_radial_stress_energy']) == 0
    assert np.min(state['excess_angular_tension_energy']) == 0


def test_balancing_support_closes_full_tensor_after_a_boost():
    density, velocity = 2., -.3
    field = anisotropic_moments(density, -density, density, velocity)
    for ratio in (1., 2., 3., 5.):
        support = anisotropic_moments(ratio*density, density, -density, velocity)
        dust = anisotropic_moments((1+ratio)*density, 0., 0., velocity)
        assert_allclose(field+support, dust, atol=2e-15)


def test_adiabatic_and_controlled_balancing_supports_have_distinct_work_ports():
    charge = np.array([2., 3., 1.])[:, None]
    inverse_c = np.array([2., 1., .5])[:, None]
    energy = charge*charge*inverse_c/2
    electrical, mechanical, unused = capacitor_step_work(charge[:-1], charge[1:], inverse_c[:-1], inverse_c[1:])
    for ratio in (1., 3., 5.):
        passive = adiabatic_balancing_support(energy, mechanical, ratio)
        assert np.min(passive-ratio*energy) >= -1e-14
        assert_allclose(np.diff(passive+energy, axis=0), electrical, atol=2e-14)
        assert_allclose(np.min(passive-ratio*energy, axis=0), 0., atol=2e-14)
        controlled, port = controlled_balancing_support(energy, mechanical, ratio)
        assert_allclose(electrical+port, np.diff(controlled+energy, axis=0), atol=2e-14)


def test_reuse_requires_opposite_work_at_the_same_label_and_interval():
    state = local_mechanical_reuse(np.array([-4., 2., -1.]), np.array([1., -3., 2.]))
    assert_allclose(state['reused'], [1., 0., 1.])
    assert_allclose(state['remaining_export'], [3., 1., 0.])
    assert_allclose(state['remaining_input'], [0., 0., 1.])


def test_existing_pressure_credit_counts_the_skin_load_and_preserves_the_full_tensor():
    u, p, v = np.array([2., 2.]), np.array([.5, 3.]), .2
    fluid = anisotropic_moments(3*p, p, p, v)
    field = anisotropic_moments(u, -u, u, v)
    for family in ('dec_floor', 'directional', 'stiff_fluid', 'radiation_fluid'):
        state = pressure_shared_floor(u, p, family)
        support = anisotropic_moments(state['density'], state['radial_pressure'], state['angular_pressure'], v)
        pressure_left = p-state['used_pressure']
        expected = anisotropic_moments(3*p+u+state['density'], pressure_left, pressure_left, v)
        assert_allclose(field+fluid+support, expected, atol=1e-14)
        assert np.all(state['density'] >= abs(state['angular_pressure']))
    assert_allclose(pressure_shared_floor(u, p, 'directional')['density'], 2*u)


def test_retained_inventory_is_the_minimum_initial_energy_with_prescribed_work():
    floor = np.array([2., 1., 4.])[:, None]
    work = np.array([3., -2.])[:, None]
    energy = retained_support_energy(floor, work)
    assert_allclose(energy[:, 0], [3., 6., 4.])
    assert_allclose(np.diff(energy, axis=0), work)
