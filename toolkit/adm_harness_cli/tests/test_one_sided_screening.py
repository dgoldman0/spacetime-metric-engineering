import numpy as np
import pytest
from scipy.integrate import quad

from adm_harness.one_sided_screening import (one_sided_cloud, cloud_stiffness_ratio,
    boundary_amplitudes, independent_energy_ratio, independent_response_bvp)


@pytest.mark.parametrize('q', [.05, .2, 1., 3., 10., 30.])
def test_force_matches_independent_energy_and_boundary_value_solve(q):
    expected = cloud_stiffness_ratio(q)
    assert abs(independent_energy_ratio(q)['energy_stiffness_ratio']-expected) < 2e-9
    assert abs(independent_response_bvp(q)['bvp_stiffness_ratio']-expected) < 2e-6


def test_one_sided_counted_energy_and_charge():
    e, n = .3, 2.
    cloud = one_sided_cloud(n, charge=e)
    a = cloud['cloud_length']
    c = np.sqrt(6)*np.pi/e
    number = quad(lambda z: (c/(z+a))**3/(3*np.pi**2), 0, np.inf)[0]
    energy = quad(lambda z: (c/(z+a))**4/(3*np.pi**2), 0, np.inf)[0]
    assert np.isclose(number, n, rtol=2e-10)
    assert np.isclose(energy, cloud['cloud_energy'], rtol=2e-10)
    assert np.isclose(energy, 2*n*cloud['chemical_at_wall']/3)


def test_translation_continuity_and_large_wave_number_limit():
    assert cloud_stiffness_ratio(0) == -1
    for q in [.001, .1, 1., 10.]:
        outside, inside = boundary_amplitudes(q)
        assert np.isclose(outside-inside, 1)
        d = q+3*(q+2)/(q*q+3*q+3)
        assert np.isclose(-d*outside-q*inside, -2)
    assert np.isclose(1e6*cloud_stiffness_ratio(1e6), -1.5, rtol=1e-6)


def test_tension_can_win_only_after_the_cloud_response_is_counted():
    cloud = one_sided_cloud(1001.10836411, eta=1.04559995291e-7)
    tension = .00013563018433
    for k in [2., 4., 8.]:
        assert tension+cloud['cloud_pressure']*cloud_stiffness_ratio(k*cloud['cloud_length']) < 0
    assert tension+cloud['cloud_pressure']*cloud_stiffness_ratio(100*cloud['cloud_length']) > 0
