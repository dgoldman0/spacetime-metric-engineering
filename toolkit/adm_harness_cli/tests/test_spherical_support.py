import numpy as np

from adm_harness.spherical_support import outer_shell, planar_sheet_limit


def test_outer_junction_includes_the_nonzero_bulk_momentum_flux():
    values = outer_shell(6.8, np.linspace(.34, 3., 21))
    assert np.max(abs(values['conservation_identity_residual'])) < 2e-18
    assert np.all(values['surface_momentum_flux'] > 0)
    assert np.all(values['dec'])


def test_static_stress_derivatives_agree_with_independent_radius_changes():
    radius, mass, step = 6.8, 1.5, .002
    values = outer_shell(radius, mass)
    samples = [outer_shell(radius+k*step, mass) for k in [-2, -1, 1, 2]]
    for name in ['surface_energy', 'surface_pressure']:
        derivative = (samples[0][name]-8*samples[1][name]+8*samples[2][name]-samples[3][name])/(12*step)
        assert np.isclose(derivative, values[name+'_derivative'], rtol=1e-10, atol=1e-14)
    assert values['positive_causal_fluid']
    assert values['fluid_radial_frequency_squared'] > 0


def test_positive_shell_mass_obeys_the_junction_square_root_bound():
    radius = 6.8
    values = outer_shell(radius, radius*(1-1e-10)/2)
    assert values['surface_energy'] < values['ordinary_surface_mass_density_ceiling']
    assert np.isclose(values['surface_energy']/values['ordinary_surface_mass_density_ceiling'], 1., atol=2e-5)


def test_transparent_and_dirichlet_scalings_of_the_off_sheet_stress():
    # At fixed finite coupling the leading divergence is d^-3. Sending
    # coupling to infinity at fixed distance instead gives the d^-4 limit.
    finite = planar_sheet_limit(np.array([1e-4, 1e-5, 1e-6]), 8.)
    assert abs(finite['asymptotic_ratio'][-1]-1) < 4.1e-6
    assert np.all(np.diff(finite['asymptotic_ratio']) > 0)
    strong = planar_sheet_limit(np.array([.2, .5, 1.]), 1e10)
    exact = 1/(16*np.pi**2*np.array([.2, .5, 1.])**4)
    assert np.allclose(strong['angular_pressure'], exact, rtol=3e-9)
