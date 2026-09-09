import numpy as np
import pytest
from scipy.integrate import quad

from adm_harness.smooth_mirror import (sech_optical_transform, smooth_born_stress,
    independent_born_energy, fermi_surface_match, corrugation_energy,
    normal_mode_requirements)


def test_sech_transform_against_direct_position_integral():
    for q in [0., .1, 1., 4.]:
        direct = quad(lambda x: np.cos(q*x)/np.cosh(x)**2, 0., 30., epsabs=1e-12)[0]
        assert np.isclose(sech_optical_transform(q), direct, rtol=1e-10, atol=1e-13)


def test_smooth_stress_inside_and_outside_against_independent_quadrature():
    d, strength = .05, 2.
    z = d*np.array([0., .5, 1., 2., 4., 8., 16.])
    actual = smooth_born_stress(z, d, strength, 1/d, nodes=768)
    expected = [independent_born_energy(x, d, strength, 1/d)[0] for x in z]
    assert np.allclose(actual['energy'], expected, rtol=2e-7, atol=1e-8)
    assert np.isfinite(actual['energy']).all()
    assert np.all(actual['radial_pressure'] == 0)
    assert np.all(actual['angular_enthalpy'] == 0)


def test_smooth_far_tail_recovers_the_finite_sheet_ultraviolet_coefficient():
    # The Born result is linear in integrated optical strength. Its far-wall
    # limit agrees with the small-strength planar sheet, not its Dirichlet limit.
    d, strength, z = .1, .1, 4.
    value, _ = independent_born_energy(z, d, strength, 1/d)
    asymptote = -strength/(48*np.pi**2*z**3)
    assert abs(value/asymptote-1) < .004


def test_renormalization_scale_change_is_the_required_local_derivative():
    d, strength = .1, 1.
    y = np.array([0., .3, .8, 1.5, 3.])
    z = d*y
    a = smooth_born_stress(z, d, strength, 1/d)
    b = smooth_born_stress(z, d, strength, 2/d)
    sech2 = 1/np.cosh(y)**2
    v_second = strength/(2*d**3)*(4*sech2-6*sech2**2)
    expected = -np.log(2)*v_second/(48*np.pi**2)
    assert np.allclose(b['energy']-a['energy'], expected, rtol=1e-10, atol=1e-10)


def test_material_match_has_causal_density_waves_and_negative_shape_stiffness():
    material = fermi_surface_match(6.8, 1.5)
    assert material['positive_components']
    assert abs(material['energy_reconstruction_error']) < 1e-17
    assert abs(material['pressure_reconstruction_error']) < 1e-17
    assert material['fermi_radial_frequency_squared'] > 0
    assert material['longitudinal_speed_squared'] == .5
    assert material['normal_speed_squared'] < 0


@pytest.mark.parametrize('fermi', [.5, 2., 4.])
def test_normal_stiffness_from_direct_fixed_particle_surface_energy(fermi):
    tension, k = 1., 1.3
    pressure = -tension+.5*fermi
    # Leading coefficient is -P*k^2/4. The zero-pressure control starts at a^4.
    amplitudes = [.01, .005, .0025]
    errors = [abs(corrugation_energy(a, k, tension, fermi)/a**2+pressure*k*k/4)
              for a in amplitudes]
    assert errors[-1] < errors[0]/14
    assert errors[-1] < 3e-6


def test_local_shape_modes_are_labelled_by_their_valid_scale_window():
    m = fermi_surface_match(6.8, 1.5)
    modes = normal_mode_requirements(6.8, m['surface_energy'], m['surface_pressure'], .05, np.arange(1, 81))
    chosen = modes['scale_window']
    assert np.any(chosen)
    assert np.all(modes['normal_frequency_squared'][chosen] < 0)
    k = modes['wave_number']
    fixed = modes['normal_frequency_squared']+modes['required_bending_coefficient']*k**4/m['surface_energy']
    assert np.max(abs(fixed)) < 1e-13
