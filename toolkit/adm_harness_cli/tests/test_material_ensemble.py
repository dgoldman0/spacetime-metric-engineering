import numpy as np

from adm_harness.active_transfer_reservoir import MetricJets
from adm_harness.elastic_endpoint_reservoir import ElasticLaw
from adm_harness.electrothermal_endpoint import ElectricalLaw
from adm_harness.material_ensemble import MaterialEnsemble, evolve_material_ensemble


class Model:
    def __init__(self, varying=False):
        self.varying = varying

    def metric(self, t, x):
        if not self.varying:
            one, zero = np.ones_like(x), np.zeros_like(x)
            return MetricJets(one, zero, one, 2*one, zero, zero, zero, zero, zero, zero)
        a, b = np.exp(.07*t*x), np.exp(.1*t*np.cos(x))
        return MetricJets(a, .13*np.sin(x+.2*t), b, np.sqrt(x*x+3)*np.exp(.04*t),
                          .07*t*a, .13*np.cos(x+.2*t), .1*np.cos(x), -.1*t*np.sin(x),
                          np.full_like(x, .04), x/(x*x+3))

    def medium(self, t, x):
        return [np.zeros((4, x.size)) for _ in range(3)]


def make_patch(varying=False, sigma=.1, ratio=1.):
    return MaterialEnsemble(Model(varying), ElasticLaw(stiffness=.1, scale=.4),
                            ElectricalLaw(energy_ratio=ratio, conductivity=sigma, heat_target=2., profile='capacitor'),
                            cells=12, thermal_share=.3, forcing=0)


def test_hamiltonian_derivatives_generate_material_velocity_and_force():
    patch = make_patch(varying=True)
    state, t = patch.initial(), .2
    state[patch.cells-1:2*(patch.cells-1)] += np.linspace(-.01, .02, patch.cells-1)
    rhs, _ = patch.rhs(t, state)
    delta = 2e-7
    for i in (1, 5, 9):
        a, b = state.copy(), state.copy()
        a[i] += delta; b[i] -= delta
        gradient_x = (patch.fields(t, a)['canonical'].sum()-patch.fields(t, b)['canonical'].sum())/(2*delta)
        np.testing.assert_allclose(rhs[patch.cells-1+i], -gradient_x, rtol=2e-6, atol=3e-9)
        a, b = state.copy(), state.copy()
        a[patch.cells-1+i] += delta; b[patch.cells-1+i] -= delta
        gradient_p = (patch.fields(t, a)['canonical'].sum()-patch.fields(t, b)['canonical'].sum())/(2*delta)
        np.testing.assert_allclose(rhs[i], gradient_p, rtol=2e-6, atol=3e-9)


def test_explicit_metric_power_matches_hamiltonian_time_derivative():
    patch = make_patch(varying=True, sigma=0.)
    state, t, h = patch.initial(), .2, 2e-6
    _, diag = patch.rhs(t, state)
    derivative = (patch.fields(t+h, state)['canonical'].sum()-patch.fields(t-h, state)['canonical'].sum())/(2*h)
    np.testing.assert_allclose(diag['canonical_geometry'], derivative, rtol=2e-6, atol=3e-9)


def test_ohmic_transfer_preserves_combined_energy_at_fixed_canonical_momentum():
    patch = make_patch(varying=True)
    state, t = patch.initial(), .2
    rate, diag = patch.rhs(t, state)
    rate[:2*(patch.cells-1)] = 0.
    h = 2e-6
    power = (patch.fields(t, state+h*rate)['canonical'].sum()-patch.fields(t, state-h*rate)['canonical'].sum())/(2*h)
    assert diag['heat_electrical'] > 0
    assert abs(power) < 5e-9


def test_ideal_unforced_evolution_preserves_each_material_heat_and_flux():
    patch = make_patch(sigma=0., ratio=4.)
    result = evolve_material_ensemble(patch, duration=.08, snapshots=5)
    assert result['status'] == 'duration_completed'
    start, finish = patch.fields(0., result['states'][0]), patch.fields(.08, result['states'][-1])
    np.testing.assert_array_equal(start['heat'], finish['heat'])
    np.testing.assert_array_equal(start['charge'], finish['charge'])
    assert abs(result['history'][-1]['canonical_balance_residual']) < 1e-7
    assert abs(result['history'][-1]['momentum_balance_residual']) < 1e-7


def test_resistive_evolution_heats_material_with_counted_field_energy():
    patch = make_patch(ratio=2.)
    result = evolve_material_ensemble(patch, duration=.08, snapshots=5)
    assert result['status'] == 'duration_completed'
    final = result['history'][-1]
    assert final['heat_electrical_integral'] > 0
    assert abs(final['thermal_balance_residual']) < 1e-12
    assert abs(final['canonical_balance_residual']) < 1e-7


def test_real_imposed_heat_extraction_still_reaches_a_thermal_boundary():
    class HeatingModel(Model):
        def medium(self, t, x):
            moments, dt, dx = super().medium(t, x)
            moments[0] = .2*t
            dt[0] = .2
            return moments, dt, dx
    patch = MaterialEnsemble(HeatingModel(), ElasticLaw(scale=.4), ElectricalLaw(energy_ratio=0),
                             cells=8, thermal_share=1., forcing=1.)
    initial = patch.initial()
    initial[2*(patch.cells-1):2*(patch.cells-1)+patch.cells+1] = .25
    # Flat relaxed material: dq/ds=-R^2 P/(A n)=-2.
    result = evolve_material_ensemble(patch, duration=.2, snapshots=5, initial=initial)
    assert result['status'] == 'material_domain_limit'
    np.testing.assert_allclose(result['final_time'], .125, atol=1e-7)
    assert abs(result['history'][-1]['canonical_balance_residual']) < 1e-9


def test_discrete_field_force_converges_to_covariant_lorentz_force():
    errors = []
    for cells in (64, 128):
        patch = MaterialEnsemble(Model(varying=True), ElasticLaw(scale=.4), ElectricalLaw(energy_ratio=0),
                                 cells=cells, thermal_share=0., forcing=0.)
        state = patch.initial()
        x, p, q, _ = patch.split(state)
        charge = .4+.1*np.sin(x)
        charged = patch.pack(x, p, q, charge)
        bare = patch.pack(x, p, q, np.zeros_like(x))
        charged_rate, _ = patch.rhs(.2, charged)
        bare_rate, _ = patch.rhs(.2, bare)
        f = patch.fields(.2, charged)
        g = f['metric']
        computed = (charged_rate[cells-1:2*(cells-1)]-bare_rate[cells-1:2*(cells-1)])/f['volume'][1:-1]
        expected = (g.alpha*g.b*charge*.1*np.cos(x)/g.radius**2)[1:-1]
        errors.append(np.max(abs(computed-expected)))
    assert errors[1] < .3*errors[0]
    assert errors[1] < 1e-6
