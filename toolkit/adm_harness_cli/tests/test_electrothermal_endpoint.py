import numpy as np

from adm_harness.active_transfer_reservoir import MetricJets, divergence_projections
from adm_harness.elastic_endpoint_reservoir import ElasticLaw, ElasticPatch, evolve
from adm_harness.electrothermal_endpoint import (
    ElectricalLaw, ElectrothermalPatch, evolve_electrothermal, maxwell_currents, maxwell_moments,
)


def metric(t, x):
    a = np.exp(.07*t*x)
    return MetricJets(a, .13*np.sin(x+.2*t), np.exp(.1*t*np.cos(x)),
                      np.sqrt(x*x+3)*np.exp(.04*t), .07*t*a, .13*np.cos(x+.2*t),
                      .1*np.cos(x), -.1*t*np.sin(x), np.full_like(x, .04), x/(x*x+3))


def charge(t, x):
    return .8*np.exp(-.2*t)*(1+.1*np.sin(x))


def test_maxwell_divergence_matches_lorentz_power_and_force_on_active_metric():
    t, x, h = .7, np.linspace(-1.7, 1.3, 23), 1e-5
    g = metric(t, x)
    def tensor(t, x):
        return maxwell_moments(charge(t, x), metric(t, x).radius)
    dt = (tensor(t+h, x)-tensor(t-h, x))/(2*h)
    dx = (tensor(t, x+h)-tensor(t, x-h))/(2*h)
    p, f = divergence_projections(g, tensor(t, x), dt, dx)
    electric, density, current = maxwell_currents(
        g, charge(t, x), -.2*charge(t, x), .08*np.exp(-.2*t)*np.cos(x))
    np.testing.assert_allclose(p, -electric*current, rtol=2e-8, atol=1e-11)
    np.testing.assert_allclose(f, -electric*density, rtol=2e-8, atol=1e-11)


def test_ohmic_charge_evolution_gives_positive_material_frame_heating():
    x = np.linspace(-1.5, 1.2, 31)
    g, q = metric(.4, x), charge(.4, x)
    qx = .08*np.exp(-.08)*np.cos(x)
    v, sigma = .7*np.sin(x), .15
    gamma = 1/np.sqrt(1-v*v)
    qt = -(-g.beta+g.alpha*v/g.b)*qx-g.alpha*sigma*q/gamma
    electric, density, current = maxwell_currents(g, q, qt, qx)
    heat = gamma*electric*(current-v*density)
    np.testing.assert_allclose(heat, sigma*electric**2, rtol=1e-13, atol=1e-14)
    assert np.min(heat) > 0


class FlatModel:
    def metric(self, t, x):
        one, zero = np.ones_like(x), np.zeros_like(x)
        return MetricJets(one, zero, one, 2*one, zero, zero, zero, zero, zero, zero)

    def medium(self, t, x):
        return [np.zeros((4, x.size)) for _ in range(3)]


def test_zero_field_recovers_existing_elastic_response():
    model, law = FlatModel(), ElasticLaw(scale=.4)
    old = ElasticPatch(model, law, cells=16)
    new = ElectrothermalPatch(model, law, ElectricalLaw(energy_ratio=0), cells=16)
    total, q = new.initial_pair()
    old_state = old.initial(initialization='prepared_reference')
    np.testing.assert_array_equal(total, old_state)
    np.testing.assert_allclose(new.pair_rhs(0., total, q)[0], old.rhs(0., old_state)[0], atol=1e-14)
    a = evolve(old, duration=.1, snapshots=3, initialization='prepared_reference')
    b = evolve_electrothermal(new, duration=.1, snapshots=3)
    np.testing.assert_allclose(a['states'], b['states'], atol=1e-13)


def test_field_and_material_allocation_have_identical_initial_conserved_totals():
    electrical = ElectricalLaw(energy_ratio=4.)
    args = (FlatModel(), ElasticLaw(scale=.4), electrical)
    field = ElectrothermalPatch(*args, cells=32)
    material = ElectrothermalPatch(*args, cells=32, allocation='material')
    a, qa = field.initial_pair()
    b, qb = material.initial_pair()
    np.testing.assert_array_equal(a, b)
    assert qa.max() > 0 and qa[0] == qa[-1] == 0
    np.testing.assert_array_equal(qb, 0)


def test_capacitor_preparation_preserves_field_energy_with_charge_free_interior():
    class CurvedModel(FlatModel):
        def metric(self, t, x):
            return metric(t, x)
    args = (CurvedModel(), ElasticLaw(scale=.4))
    thermal = ElectrothermalPatch(*args, ElectricalLaw(energy_ratio=4.), cells=64)
    capacitor = ElectrothermalPatch(*args, ElectricalLaw(energy_ratio=4., profile='capacitor'), cells=64)
    a, qa = thermal.initial_pair()
    b, qb = capacitor.initial_pair()
    np.testing.assert_allclose(a[1].sum(), b[1].sum(), rtol=1e-14)
    interior = (capacitor.faces > capacitor.faces[0]+.15) & (capacitor.faces < capacitor.faces[-1]-.15)
    assert np.ptp(qa[interior]) > .01
    assert np.ptp(qb[interior]) == 0


def test_combined_evolution_conserves_energy_and_converges_to_joule_heat_balance():
    residuals = []
    # Resolve the 0.15-wide field taper; three-cell coarse tapers exhibit
    # competing spatial errors before reaching the asymptotic regime.
    for cells in (128, 256):
        patch = ElectrothermalPatch(FlatModel(), ElasticLaw(scale=.4),
                                   ElectricalLaw(energy_ratio=.2, conductivity=.1, heat_target=2.),
                                   cells=cells)
        result = evolve_electrothermal(patch, duration=.1, snapshots=3)
        assert result['status'] == 'duration_completed'
        final = result['history'][-1]
        assert final['thermal_electrical'] > 0
        assert final['net_charge'] == 0
        assert abs(final['energy_balance_residual']) < 1e-12
        residuals.append(abs(final['thermal_balance_residual']))
    assert residuals[1] < .6*residuals[0]
    assert residuals[1] < 1e-5
