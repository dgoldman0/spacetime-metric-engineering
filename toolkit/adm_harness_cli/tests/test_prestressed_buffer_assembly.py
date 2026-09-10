import numpy as np

from adm_harness.active_transfer_reservoir import MetricJets
from adm_harness.elastic_endpoint_reservoir import ElasticLaw
from adm_harness.electrothermal_endpoint import ElectricalLaw
from adm_harness.material_ensemble import MaterialEnsemble, evolve_material_ensemble
from adm_harness.prestressed_buffer_assembly import PrestressedBufferAssembly


class Model:
    def __init__(self, active=False):
        self.active = active

    def metric(self, t, x):
        if not self.active:
            one, zero = np.ones_like(x), np.zeros_like(x)
            alpha = np.exp(.4*x)
            return MetricJets(alpha, zero, one, 2*one, .4*alpha, zero, zero, zero, zero, zero)
        a, b = np.exp(.07*t*x), np.exp(.1*t*np.cos(x))
        return MetricJets(a, .13*np.sin(x+.2*t), b, np.sqrt(x*x+3)*np.exp(.04*t),
                          .07*t*a, .13*np.cos(x+.2*t), .1*np.cos(x), -.1*t*np.sin(x),
                          np.full_like(x, .04), x/(x*x+3))

    def medium(self, t, x):
        return [np.zeros((4, x.size)) for _ in range(3)]


def make_patch(active=False, cells=12):
    template = MaterialEnsemble(Model(active), ElasticLaw(stiffness=.1, scale=.4),
                                 ElectricalLaw(energy_ratio=0.), cells=cells, thermal_share=1., forcing=0.)
    patch = PrestressedBufferAssembly(template)
    if active:
        patch.backbone_weight = np.linspace(.03, .1, cells)*patch.reference**2
    return patch


def test_bonded_characteristics_match_the_compression_derivative():
    # A local common deformation scales both conserved material densities.
    nt, nb = np.geomspace(.001, 100, 101), np.geomspace(100, .001, 101)
    q, k = .3, .001
    def rest(stretch):
        n, b = stretch*nt, stretch*nb
        return n*(1+q)+.5*k*(b*b+1), .5*k*(b*b-1)
    h = 1e-5
    ep, pp = rest(1+h); em, pm = rest(1-h)
    e, p = rest(1.)
    np.testing.assert_allclose((ep-em)/(2*h)-e, p, rtol=1e-6, atol=1e-9)
    cs2 = k*nb**2/(nt*(1+q)+k*nb**2)
    np.testing.assert_allclose((pp-pm)/(ep-em), cs2, rtol=1e-6, atol=1e-10)
    assert np.min(e-abs(p)) > 0 and np.min(cs2) > 0 and np.max(cs2) < 1


def test_backbone_hamiltonian_generates_force_and_velocity():
    patch = make_patch(active=True)
    state, t, h = patch.initial(), .2, 2e-7
    state[patch.cells-1:2*(patch.cells-1)] += np.linspace(-.01, .02, patch.cells-1)
    rate, _ = patch.rhs(t, state)
    for i in (1, 5, 9):
        a, b = state.copy(), state.copy(); a[i] += h; b[i] -= h
        hx = (patch.fields(t, a)['canonical'].sum()-patch.fields(t, b)['canonical'].sum())/(2*h)
        np.testing.assert_allclose(rate[patch.cells-1+i], -hx, rtol=3e-6, atol=1e-8)
        a, b = state.copy(), state.copy(); a[patch.cells-1+i] += h; b[patch.cells-1+i] -= h
        hp = (patch.fields(t, a)['canonical'].sum()-patch.fields(t, b)['canonical'].sum())/(2*h)
        np.testing.assert_allclose(rate[i], hp, rtol=3e-6, atol=1e-8)


def test_active_backbone_counts_metric_work_and_end_reactions():
    patch = make_patch(active=True)
    state, t, h = patch.initial(), .2, 2e-6
    rate, diag = patch.rhs(t, state)
    plus, minus = patch.fields(t+h, state+h*rate), patch.fields(t-h, state-h*rate)
    energy_rate = (plus['canonical'].sum()-minus['canonical'].sum())/(2*h)
    momentum_rate = (plus['momentum'].sum()-minus['momentum'].sum())/(2*h)
    np.testing.assert_allclose(energy_rate, diag['canonical_geometry'], rtol=3e-6, atol=1e-8)
    np.testing.assert_allclose(momentum_rate, diag['momentum_free']+diag['anchor_left']+diag['anchor_right'],
                               rtol=3e-6, atol=1e-8)


def test_initial_preload_supports_a_static_lapse_without_motion_constraints_inside():
    patch = make_patch()
    preload = patch.equilibrate_initial_preload()
    assert preload['maximum_initial_momentum_residual'] < 1e-10
    result = evolve_material_ensemble(patch, duration=.05, snapshots=5, max_step=.001, cfl=.05)
    assert result['status'] == 'duration_completed'
    assert max(row['maximum_abs_velocity'] for row in result['history']) < 1e-8
    assert abs(result['history'][-1]['canonical_balance_residual']) < 1e-10


def test_preload_converges_to_the_continuum_minimum_energy_profile():
    errors = []
    for cells in (32, 64):
        patch = make_patch(cells=cells)
        patch.equilibrate_initial_preload()
        f = patch.fields(0., patch.initial())
        centers = .5*(f['x'][:-1]+f['x'][1:])
        # rho_b+p_b=w*((alpha_right/alpha)**2-1) at the limiting unloaded end.
        exact = 1.25*(np.exp(.8*(centers[-1]-centers))-1)
        actual = patch.backbone_weight/np.diff(f['x'])**2
        errors.append(np.max(abs(actual-exact)))
    assert errors[1] < .6*errors[0]
    assert errors[1] < .05


def test_budget_control_preserves_heat_and_matches_declared_total_energy():
    patch = make_patch()
    first_heat = patch.fields(0., patch.initial())['heat'].copy()
    preload = patch.equilibrate_initial_preload()
    target = preload['zero_preload_slice_energy']+.4*(preload['initial_slice_energy']-preload['zero_preload_slice_energy'])
    patch.template_initial_slice_energy = target
    np.testing.assert_allclose(patch.match_template_energy(preload), .4, atol=1e-12)
    f = patch.fields(0., patch.initial())
    np.testing.assert_allclose(4*np.pi*f['matter_adm'].sum(), target, rtol=1e-12)
    np.testing.assert_array_equal(f['heat'], first_heat)
