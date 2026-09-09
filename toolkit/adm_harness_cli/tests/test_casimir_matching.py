import numpy as np
from scipy.integrate import quad

from adm_harness.casimir_matching import interaction, gap_profile, interaction_partition, gaussian_overlap


def test_dirichlet_and_weak_coupling_limits():
    strong = interaction(1., 1e8, 1e8)
    np.testing.assert_allclose(strong['energy'], -np.pi**2/1440, rtol=7e-8)
    np.testing.assert_allclose(strong['pressure'], -np.pi**2/480, rtol=9e-8)
    weak = interaction(1., 1e-7, 1e-7)
    np.testing.assert_allclose(weak['energy'], -1e-14/(32*np.pi**2), rtol=4e-6)


def test_pressure_is_separation_derivative_at_fixed_material_response():
    a, h = .91, .001
    energies = [interaction(a+j*h, 2., 17.)['energy'] for j in [-2, -1, 1, 2]]
    derivative = (energies[0]-8*energies[1]+8*energies[2]-energies[3])/(12*h)
    assert abs(derivative+interaction(a, 2., 17.)['pressure']) < 3e-12


def test_physical_scale_covariance_and_interchange_symmetry():
    base = interaction(1., 2., 17.)
    scaled = interaction(3., 2/3, 17/3)
    np.testing.assert_allclose(base['energy']/27, scaled['energy'], rtol=1e-14)
    np.testing.assert_allclose(base['pressure']/81, scaled['pressure'], rtol=1e-14)
    left = gap_profile(1., 2., 17., [.2, .4, .8])
    right = gap_profile(1., 17., 2., [.8, .6, .2])
    np.testing.assert_allclose(left, right, rtol=1e-13)


def test_conformal_gap_trace_and_full_surface_energy_accounting():
    fractions = np.linspace(.1, .9, 9)
    channels = gap_profile(1., 8., 8., fractions, xi=1/6)
    np.testing.assert_allclose(-channels[:, 0]+channels[:, 1]+2*channels[:, 2], 0., atol=1e-16)
    for xi in [0., 1/6, .25]:
        partition = interaction_partition(1., 8., 8., xi)
        np.testing.assert_allclose(partition['total'], partition['interaction_energy'], rtol=2e-12)
    assert interaction_partition(1., 8., 8., .25)['surface'] == 0.


def test_minimal_gap_stress_retains_isolated_wall_polarization():
    canonical = gap_profile(1., 8., 8., [.1, .5, .9])
    conformal = gap_profile(1., 8., 8., [.1, .5, .9], xi=1/6)
    assert np.all(canonical[:, 0] < conformal[:, 0])
    assert np.all(canonical[:, 0]+canonical[:, 1] < 0)
    assert canonical[0, 0] < canonical[1, 0]


def test_positive_sheet_family_holding_floor_and_virial_identity():
    for first, second in [(1e-4, 1e-4), (1e-4, 1e4), (.1, 100.), (8., 8.), (1e4, 1e4)]:
        result = interaction(1., first, second)
        assert 1 < result['effective_exponent'] < 3
        assert result['zero_wall_mass_held_energy_floor'] > 0
        assert abs(result['virial_identity_error']/result['energy']) < 1e-11


def test_gaussian_overlap_has_separation_dependent_local_counterterm():
    width, strength, a = .16, 8., 1.
    normalization = strength/(np.sqrt(2*np.pi)*width)
    numerical = quad(lambda z: normalization**2*np.exp(-((z-a/2)**2+(z+a/2)**2)/(2*width**2)), -2., 2., epsabs=1e-14)[0]
    np.testing.assert_allclose(gaussian_overlap(a), numerical, rtol=2e-13)
