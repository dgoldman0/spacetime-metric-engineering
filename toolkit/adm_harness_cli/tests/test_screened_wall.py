import numpy as np
import pytest
from scipy.integrate import quad
from scipy.optimize import minimize_scalar

from adm_harness.screened_wall import (REFERENCE_CHARGE, cold_cloud,
    cold_cloud_profile, restoring_fraction, displacement_profile,
    independent_response_bvp, independent_response_energy,
    screened_surface_match, critical_cloud_wave_number, junction_restoring_bound)


def test_cloud_integrals_count_charge_energy_and_stress():
    for n in [.3, 3.]:
        data = cold_cloud(n)
        a = data['cloud_length']
        for key, expected in [('screening_number_density', n),
                ('energy_density', data['cloud_energy']),
                ('tangential_pressure', data['cloud_pressure'])]:
            actual = 2*a*quad(lambda x: cold_cloud_profile(a*x, n)[key], 0, np.inf)[0]
            assert np.isclose(actual, expected, rtol=2e-10)
        assert np.isclose(data['cloud_energy'], 2*n*data['potential_at_wall']/3)
        assert cold_cloud_profile(a, n)['normal_pressure'] == 0


def test_translation_mode_and_linearized_poisson_equation():
    x = np.linspace(.1, 10., 80)
    w, wp = displacement_profile(x, 0)
    assert np.allclose(w, (1+x)**-2)
    for q in [.1, 1., 10.]:
        h = 1e-5
        w, wp = displacement_profile(x, q)
        wpp = (displacement_profile(x+h, q)[1]-displacement_profile(x-h, q)[1])/(2*h)
        assert np.allclose(wpp, (q*q+6/(1+x)**2)*w, rtol=2e-7, atol=2e-10)


@pytest.mark.parametrize('q', [.05, .2, 1., 3., 10.])
def test_force_kernel_matches_independent_poisson_and_energy_variations(q):
    expected = -3*(q+1)/(q*q+3*q+3)
    assert abs(independent_response_bvp(q)['cloud_stiffness_ratio']-expected) < 2e-7
    assert abs(independent_response_energy(q)['cloud_stiffness_ratio']-expected) < 2e-10


def test_bending_expansion_has_a_finite_pressure_ceiling():
    q = np.logspace(-5, 3, 100)
    response = restoring_fraction(q)
    assert np.all(np.diff(response) > 0)
    assert np.all((response > 0)&(response < 1))
    assert np.isclose(response[0]/q[0]**2, 1/3, rtol=2e-5)
    # Extrapolating the k^4 term to k*a=3 falsely predicts a larger benefit.
    assert 3**2/3 > 1
    assert restoring_fraction(3) < .5


def test_static_matching_uses_the_same_particle_number_for_both_energies():
    n = .7
    cloud = cold_cloud(n)
    for flavors in [1, 4, 16, 64]:
        match = screened_surface_match(6.8, 1.5, flavors)
        kf = np.sqrt(4*np.pi*n/flavors)
        gas = flavors*kf**3/(6*np.pi)
        assert np.isclose(cloud['cloud_energy']/gas, match['cloud_to_fermi_ratio'])
        assert np.isclose(cloud['potential_at_wall']/kf, match['cloud_to_fermi_ratio'])
        assert abs(match['energy_reconstruction_error']) < 1e-17
        assert abs(match['pressure_reconstruction_error']) < 1e-17


def test_global_mass_bound_matches_independent_optimization_and_crossing():
    bound = junction_restoring_bound(6.8)
    opt = minimize_scalar(lambda m: float(screened_surface_match(6.8, m)['surface_pressure']/
        screened_surface_match(6.8, m)['surface_energy']), bounds=(.46, 2.96), method='bounded')
    assert np.isclose(opt.x, bound['best_exterior_mass'], rtol=1e-6)
    assert np.isclose(opt.fun, bound['minimum_pressure_to_energy'], rtol=1e-11)
    b, q = bound['maximum_cloud_restoring_ceiling'], bound['minimum_critical_q']
    assert np.isclose(b*restoring_fraction(q), 1)
    assert b*restoring_fraction(.05*np.sqrt(110)) < .13
    assert b*restoring_fraction(.1*np.sqrt(110)) < .35
    assert np.isinf(critical_cloud_wave_number(1))


@pytest.mark.parametrize('function,args', [(cold_cloud, (-1,)),
    (restoring_fraction, (-.1,)), (restoring_fraction, (np.nan,)),
    (screened_surface_match, (6.8, 1.5, 1.5)), (junction_restoring_bound, (1.,))])
def test_invalid_model_parameters_fail(function, args):
    with pytest.raises(ValueError):
        function(*args)
