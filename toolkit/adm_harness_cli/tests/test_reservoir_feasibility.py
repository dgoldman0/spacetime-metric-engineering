import numpy as np

from adm_harness.reservoir_feasibility import (
    C_LIGHT, G_NEWTON, MU_ZERO, boost_radial, radial_null,
    classical_completion_requirement, field_decomposition,
    minimize_initial_null_requirement, scale_coefficients, taub_mathews_pressure,
)
from test_prestressed_buffer_assembly import make_patch


def test_two_transverse_maxwell_orientations_supply_the_full_averaged_tensor():
    energy = 2.7
    tensor = np.zeros((4, 4))
    for magnetic in (np.array([0., np.sqrt(energy), 0.]), np.array([0., 0., np.sqrt(energy)])):
        u = .5*np.dot(magnetic, magnetic)
        tensor[0, 0] += u
        tensor[1:, 1:] += u*np.eye(3)-np.outer(magnetic, magnetic)
    np.testing.assert_allclose(tensor, np.diag([energy, energy, 0., 0.]), atol=1e-14)
    v = .63
    gamma = 1/np.sqrt(1-v*v)
    transform = np.eye(4)
    transform[:2, :2] = gamma*np.array([[1., v], [v, 1.]])
    boosted = transform@tensor@transform.T
    expected = np.array([boosted[0, 0], boosted[1, 1], boosted[0, 1], boosted[2, 2]])
    np.testing.assert_allclose(boost_radial(energy, energy, 0., v), expected, atol=1e-14)


def test_radial_string_cannot_change_either_null_budget_under_a_radial_boost():
    v = np.linspace(-.99, .99, 101)
    string = boost_radial(np.ones_like(v)*3., np.ones_like(v)*-3., 0., v)
    np.testing.assert_allclose(radial_null(string), 0., atol=1e-13)
    matter = boost_radial(np.ones_like(v)*2., np.ones_like(v)*.4, 0., v)
    remainder, requirement = classical_completion_requirement(string, string+matter)
    np.testing.assert_allclose(requirement, radial_null(matter), atol=1e-12)
    np.testing.assert_allclose(remainder, -matter, atol=1e-13)


def test_field_decomposition_reproduces_the_evolved_tensor_on_a_changing_metric():
    patch = make_patch(active=True)
    state = patch.initial()
    state[patch.cells-1:2*(patch.cells-1)] += np.linspace(-.3, .2, patch.cells-1)
    d = field_decomposition(patch, .31, state)
    assert d['decomposition_absolute_error'] < 2e-13
    assert np.min(d['magnetic']) > 0
    assert np.min(d['fast_speed2']) > 0 and np.max(d['fast_speed2']) < 1
    # Flux-frozen transverse energy responds to longitudinal compression as n^2.
    u, w = 2.3, 1.7
    h = 1e-5
    eplus, eminus = w*(1+h)+u*(1+h)**2, w*(1-h)+u*(1-h)**2
    pplus, pminus = u*(1+h)**2, u*(1-h)**2
    np.testing.assert_allclose((pplus-pminus)/(eplus-eminus), 2*u/(w+2*u), rtol=1e-10)


def test_physical_scale_matches_maxwell_energy_and_geometric_dilation():
    u, e, length = 3.2, 11., 1e5
    coefficients = scale_coefficients(u, u, e)
    b = coefficients['magnetic_tesla_metres']/length
    rho = coefficients['pressure_pascal_metres_squared']/length**2
    np.testing.assert_allclose(b*b/(2*MU_ZERO), rho, rtol=1e-14)
    np.testing.assert_allclose(rho, C_LIGHT**4/G_NEWTON*u/length**2)
    np.testing.assert_allclose(coefficients['slice_energy_joules_per_metre']*length,
                               C_LIGHT**4/G_NEWTON*e*length)
    demand = np.array([.2, -.3, .01, .1])
    supply = np.array([1., .7, .2, 0.])
    _, original = classical_completion_requirement(demand, supply)
    _, scaled = classical_completion_requirement(demand/9., supply/9.)
    np.testing.assert_allclose(scaled, original/9.)


def test_physical_gas_has_pressure_at_the_archived_heat_per_rest_mass():
    q = np.array([1e-7, .25, 3., 1e6])
    pressure = taub_mathews_pressure(np.ones(4), q)
    theta = pressure
    enthalpy = 2.5*theta+np.sqrt(2.25*theta**2+1)
    np.testing.assert_allclose(enthalpy-theta, 1+q, rtol=1e-14)
    np.testing.assert_allclose(pressure[0]/q[0], 2/3, rtol=1e-7)
    np.testing.assert_allclose(pressure[1:3]/(1+q[1:3]), [.12, .3125])
    np.testing.assert_allclose(pressure[-1]/(1+q[-1]), 1/3, rtol=1e-10)


def test_optimized_null_budget_has_a_dual_certificate_and_preserves_the_preload():
    patch = make_patch(cells=12)
    patch.equilibrate_initial_preload(minimum_sound_speed=.5)
    original = patch.backbone_weight.copy()
    zeros = np.zeros((4, patch.cells+1))
    result = minimize_initial_null_requirement(patch, zeros, zeros, minimum_sound_speed=.5)
    assert result['optimized_negative_null_requirement'] > 0
    assert result['maximum_equilibrium_residual'] < 1e-10
    assert result['minimum_cell_sound_speed'] >= .5-1e-10
    assert result['primal_dual_gap'] < 1e-9
    assert result['objective_measurement_error'] < 1e-9
    np.testing.assert_array_equal(patch.backbone_weight, original)
