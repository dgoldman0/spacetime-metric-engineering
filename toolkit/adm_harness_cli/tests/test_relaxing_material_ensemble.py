import numpy as np

from adm_harness.active_transfer_reservoir import MetricJets
from adm_harness.elastic_endpoint_reservoir import ElasticLaw
from adm_harness.electrothermal_endpoint import ElectricalLaw
from adm_harness.material_ensemble import MaterialEnsemble
from adm_harness.relaxing_material_ensemble import (
    StrainRelaxation, RelaxingMaterialEnsemble, relaxing_rest, evolve_relaxing_ensemble,
)


class Model:
    def metric(self, t, x):
        one, zero = np.ones_like(x), np.zeros_like(x)
        return MetricJets(one, zero, one, 2*one, zero, zero, zero, zero, zero, zero)

    def medium(self, t, x):
        return [np.zeros((4, x.size)) for _ in range(3)]


def test_relaxing_stress_comes_from_energy_and_keeps_causal_positive_domain():
    law, kappa = ElasticLaw(stiffness=.1), .1
    n = np.geomspace(.001, 100, 151)
    z = np.linspace(-5., 5., n.size)
    q, h = np.full_like(n, .2), 1e-5*n
    energy, pressure, sound2 = relaxing_rest(law, n, q, z, kappa)
    ep, pp, _ = relaxing_rest(law, n+h, q, z, kappa)
    em, pm, _ = relaxing_rest(law, n-h, q, z, kappa)
    np.testing.assert_allclose(n*(ep-em)/(2*h)-energy, pressure, rtol=1e-7, atol=1e-7)
    np.testing.assert_allclose((pp-pm)/(ep-em), sound2, rtol=1e-7, atol=1e-8)
    assert np.min(energy-abs(pressure)) > 0
    assert np.min(sound2) > 0 and np.max(sound2) < 1


def test_zero_relaxation_modulus_recovers_original_material_equations():
    args = (Model(), ElasticLaw(scale=.4), ElectricalLaw(energy_ratio=1., profile='capacitor'))
    base = MaterialEnsemble(*args, cells=12, forcing=0.)
    other = RelaxingMaterialEnsemble(*args, relaxation=StrainRelaxation(stiffness=0.), cells=12, forcing=0.)
    a, b = base.initial(), other.initial()
    np.testing.assert_allclose(a, b[:a.size], rtol=1e-11, atol=1e-12)
    ar, ad = base.rhs(0., a)
    br, bd = other.rhs(0., b)
    np.testing.assert_allclose(ar, br[:ar.size], rtol=1e-10, atol=1e-11)
    np.testing.assert_allclose(ad['canonical_geometry'], bd['canonical_geometry'], atol=1e-12)


def test_relaxation_converts_internal_strain_energy_to_heat_without_extra_power():
    patch = RelaxingMaterialEnsemble(Model(), ElasticLaw(scale=.4), ElectricalLaw(energy_ratio=1., conductivity=0.),
                                     cells=12, forcing=0.)
    state = patch.initial()
    state[-13:] += .4
    rate, diag = patch.rhs(0., state)
    h = 2e-6
    derivative = (patch.fields(0., state+h*rate)['canonical'].sum()-patch.fields(0., state-h*rate)['canonical'].sum())/(2*h)
    assert diag['heat_relaxation'] > 0 and diag['entropy_relaxation'] > 0
    assert abs(derivative) < 1e-8


def test_relaxing_force_is_generated_by_the_full_stored_energy():
    patch = RelaxingMaterialEnsemble(Model(), ElasticLaw(scale=.4), ElectricalLaw(energy_ratio=1., conductivity=0.),
                                     cells=12, forcing=0.)
    state = patch.initial()
    state[-13:] += np.linspace(-.2, .3, 13)
    rate, _ = patch.rhs(0., state)
    h = 1e-7
    for i in (1, 5, 9):
        a, b = state.copy(), state.copy()
        a[i] += h; b[i] -= h
        gradient = (patch.fields(0., a)['canonical'].sum()-patch.fields(0., b)['canonical'].sum())/(2*h)
        np.testing.assert_allclose(-gradient, rate[patch.cells-1+i], rtol=2e-6, atol=1e-8)


def test_evolving_relaxation_has_counted_heat_energy_and_anchor_momentum():
    patch = RelaxingMaterialEnsemble(Model(), ElasticLaw(scale=.4), ElectricalLaw(energy_ratio=4., conductivity=0.),
                                     cells=12, forcing=0., thermal_share=.75)
    result = evolve_relaxing_ensemble(patch, duration=.08, snapshots=5, max_step=.001)
    assert result['status'] == 'duration_completed'
    row = result['history'][-1]
    assert row['heat_relaxation_integral'] > 0 and row['entropy_relaxation_integral'] > 0
    assert abs(row['canonical_balance_residual']) < 1e-8
    assert abs(row['thermal_balance_residual']) < 1e-12
    assert abs(row['momentum_balance_residual']) < 1e-8


def test_active_geometry_relaxation_counts_metric_work_and_moving_frame_end_reactions():
    class VaryingModel(Model):
        def metric(self, t, x):
            a, b = np.exp(.07*t*x), np.exp(.1*t*np.cos(x))
            return MetricJets(a, .13*np.sin(x+.2*t), b, np.sqrt(x*x+3)*np.exp(.04*t),
                              .07*t*a, .13*np.cos(x+.2*t), .1*np.cos(x), -.1*t*np.sin(x),
                              np.full_like(x, .04), x/(x*x+3))

    patch = RelaxingMaterialEnsemble(VaryingModel(), ElasticLaw(scale=.4),
                                     ElectricalLaw(energy_ratio=2., conductivity=.1, heat_target=2.),
                                     cells=12, forcing=0.)
    state, t, h = patch.initial(), .2, 2e-6
    state[-13:] += np.linspace(-.3, .4, 13)
    rate, diag = patch.rhs(t, state)
    plus, minus = patch.fields(t+h, state+h*rate), patch.fields(t-h, state-h*rate)
    energy_rate = (plus['canonical'].sum()-minus['canonical'].sum())/(2*h)
    momentum_rate = (plus['momentum'].sum()-minus['momentum'].sum())/(2*h)
    np.testing.assert_allclose(energy_rate, diag['canonical_geometry'], rtol=2e-6, atol=1e-8)
    np.testing.assert_allclose(momentum_rate, diag['momentum_free']+diag['anchor_left']+diag['anchor_right'],
                               rtol=2e-6, atol=1e-8)
