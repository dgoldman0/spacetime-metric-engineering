import numpy as np
import pytest
from scipy.integrate import quad, simpson

from adm_harness.gravitating_atmosphere import (AtmosphereParameters,
    fermi_polynomials, solve_atmosphere, surface_match, atmosphere_profile)


@pytest.mark.parametrize('momentum_ratio', [1e-4, .01, .049, .051, .3, 2., 20.])
def test_equation_of_state_matches_independent_momentum_integrals(momentum_ratio):
    w = 2.3
    momentum = w*momentum_ratio
    u = np.hypot(w, momentum)
    energy, pressure, actual_p = fermi_polynomials(u, w)
    expected_e = 12*momentum**3*quad(
        lambda s: s*s*np.hypot(momentum*s, w), 0, 1, epsabs=1e-12)[0]
    expected_p = 4*momentum**5*quad(
        lambda s: s**4/np.hypot(momentum*s, w), 0, 1, epsabs=1e-12)[0]
    assert np.isclose(actual_p, momentum, rtol=1e-8)
    assert np.isclose(energy, expected_e, rtol=3e-8, atol=1e-25)
    assert np.isclose(pressure, expected_p, rtol=5e-8, atol=1e-30)


def test_empty_and_massless_gas_limits():
    assert fermi_polynomials(1., 2.) == (0., 0., 0.)
    assert fermi_polynomials(3., 0.) == (243., 81., 3.)
    u = np.array([.5, 1., 3.])
    energy, pressure, momentum = fermi_polynomials(u, 1.)
    assert np.all(energy >= 3*pressure)
    assert momentum[0] == momentum[1] == 0


@pytest.fixture(scope='module')
def candidate():
    p = AtmosphereParameters()
    return p, solve_atmosphere(p, .36837520511655, rtol=2e-11)


def test_globally_neutral_finite_cloud_counts_all_positive_energy(candidate):
    p, solution = candidate
    a = atmosphere_profile(p, solution, 4001)
    r = a['radius']
    charge = p.charge*simpson(4*np.pi*r*r*a['screening_number_density']/
                             np.sqrt(a['metric_f']), x=r)
    mass = simpson(4*np.pi*r*r*a['total_energy_density'], x=r)
    assert np.isclose(charge, a['charge'][0], rtol=2e-9)
    assert np.isclose(mass, a['mass'][-1]-a['mass'][0], rtol=2e-9)
    assert a['charge'][-1] == a['fermi_momentum'][-1] == 0
    assert np.min(a['metric_f']) > .33
    assert np.all(a['total_energy_density'] >= abs(a['radial_pressure']))
    assert np.all(a['total_energy_density'] >= abs(a['tangential_pressure']))


def test_klein_first_integral_and_schwarzschild_edge(candidate):
    p, solution = candidate
    a = atmosphere_profile(p, solution)
    bound_energy = p.chemical_scale*p.screening_mass_parameter/p.radius*a['lapse'][-1]
    assert np.allclose(a['klein_energy'], bound_energy, rtol=2e-10)
    assert np.isclose(a['lapse'][-1]**2, a['metric_f'][-1])
    assert a['electric_potential_energy'][-1] == 0
    assert bound_energy < p.chemical_scale*p.screening_mass_parameter/p.radius


def test_charge_fixes_the_same_wall_gas_used_by_the_israel_junction(candidate):
    p, solution = candidate
    match = surface_match(p, solution)
    kf, eta = match['wall_fermi_momentum'], p.eta
    microscopic_energy = eta*p.flavors*kf**3/(6*np.pi)
    assert np.isclose(microscopic_energy, match['surface_gas_energy'], rtol=2e-7)
    assert np.isclose(match['surface_energy'], match['wall_tension']+microscopic_energy, rtol=2e-7)
    assert np.isclose(match['surface_pressure'], -match['wall_tension']+microscopic_energy/2, rtol=2e-6)
    assert match['positive_components'] and match['tensile_wall']
    assert .08 < match['wall_only_transverse_speed_squared'] < .09


@pytest.mark.parametrize('changes', [{'radius': 1.}, {'edge_ratio': 1.},
    {'screening_mass_parameter': -1.}, {'loading': np.nan}, {'flavors': 1.5}])
def test_invalid_parameters_rejected(changes):
    with pytest.raises(ValueError):
        AtmosphereParameters(**changes)


def test_horizon_and_negative_core_mass_are_explicit_domain_rejections():
    p = AtmosphereParameters()
    with pytest.raises(ValueError, match='subhorizon'):
        solve_atmosphere(p, 1.)
    with pytest.raises(ValueError, match='negative core mass'):
        solve_atmosphere(p, .4)
