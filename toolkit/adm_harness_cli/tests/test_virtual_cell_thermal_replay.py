"""Focused independent energy and component-accounting replay controls."""
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np
from numpy.testing import assert_allclose
from scipy.interpolate import RectBivariateSpline
from adm_harness.active_transfer_reservoir import MetricJets

SCRIPTS = Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('thermal_replay', SCRIPTS/'audit_virtual_cell_thermal_replay.py')
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


def test_quadrature_splits_unaligned_reference_knots():
    times = np.array([0., .2, .8, 1.])
    kink = .37
    def evaluator(at):
        # A continuous old energy with a derivative jump; grouping by replay
        # intervals must preserve its integrated source exactly.
        return np.where(at[:, None] < kink, 2*at[:, None], 3+2*at[:, None])
    integral = replay.integrate_panels(times, [kink], evaluator, order=4)
    primitive = times**2+3*np.maximum(times-kink, 0)
    assert_allclose(integral[:, 0], np.diff(primitive), atol=1e-15)


def test_curved_baseline_credits_cancel_actual_thermal_and_receiver_power():
    times = np.array([0., .3, .6, 1.])
    a, b = .23, .17
    # A=t; U0=1+t, Z0=2t. Reusing these exact baseline states must leave
    # only phase work, including the geometry term in K0=D^(1/3)U0.
    def evaluator(at):
        ell = np.exp(a*at)[:, None]
        volume_rate = a+2*b
        thermal = ell*(1+(1+at[:, None])*volume_rate/3)
        receiver = 2*ell
        return np.array([ell**2, thermal, receiver, thermal+receiver])
    terms = replay.integrate_panels(times, [], evaluator, order=8)
    V = replay.reconstruct_inventory(np.array([4.]), *terms)
    expected = 4.-np.expm1(2*a*times)/(2*a)
    assert_allclose(V[:, 0], expected, atol=1e-14)


def test_radiation_replay_retains_prepared_extra_balance():
    zero = np.zeros((3, 1))
    V = replay.reconstruct_inventory(np.array([2.]), zero, zero, zero, zero)
    incident = np.array([[.1], [.2], [.1], [.0]])
    returned = np.array([[0.], [.1], [.2], [.1]])
    counter = V-incident-returned
    assert np.all(counter > abs(incident-returned))
    assert_allclose(V, 2.)


def test_full_budget_pays_radiation_thermal_receiver_and_reuses_guide():
    # Maxwell remainder (rho,p,q)=(2,-2,2), phase=.2, balanced radial=.3,
    # thermal=.6 and receiver=.7. The first cone facet is exactly saturated.
    args = dict(phase=np.array([.2]), radiation=np.array([.3]), thermal=np.array([.6]),
        receiver=np.array([.7]), wall=np.array([0.]), incident=np.array([.1]),
        returned=np.array([.05]), guide_multiplier=1.5)
    deficit, guide, floor = replay.full_budget(np.array([3.8]), np.array([-1.7]),
                                              np.array([2.2]), **args)
    assert_allclose(deficit, 0., atol=1e-14)
    assert_allclose(guide, .125)
    assert_allclose(floor, -.1)
    args['radiation'] = np.array([.4])
    larger, unused, unused = replay.full_budget(np.array([3.8]), np.array([-1.7]),
                                                np.array([2.2]), **args)
    assert larger[0] > 0  # extra balanced photons retain their full cost


def test_spatial_interpolation_preserves_distinct_cell_profiles():
    oldx = np.array([-3., -1., 1., 3.])
    x = np.array([-3.5, -2.5, -1.5, -.5, .5, 1.5, 2.5, 3.5])
    result = replay.spatial_history(oldx, np.array([[2., 4., 10., 14.]]), x)
    assert_allclose(result, [[2., 2.5, 3.5, 4., 10., 11., 13., 14.]])


def test_material_volume_rate_contains_boost_evolution():
    class Model:
        t_min, t_max, x_min, x_max = 0., 1., -4., 4.
    model = Model()
    t = np.linspace(0., 1., 8)
    x = np.linspace(-4., 4., 9)
    tt, xx = np.meshgrid(t, x, indexing='ij')
    model.metric_splines = [RectBivariateSpline(t, x, field) for field in
        (.1*tt, .2+.03*tt+0*xx, .3*tt, .05*tt+.01*xx)]
    at = np.array([.2, .4, .6])
    c = replay.geometry(model, at, np.array([-2., -1.975]))
    v = np.exp(.2*at)*(.2+.03*at)
    vt = np.exp(.2*at)*(.2*(.2+.03*at)+.03)
    expected = .4+v*vt/(1-v*v)
    assert_allclose(c['logD_t'], np.broadcast_to(expected[:, None], (3, 2)), atol=1e-14)


def test_complete_adapter_preserves_prepared_inventory_and_split_receiver(tmp_path, monkeypatch):
    class StaticModel:
        t_min, t_max, x_min, x_max = 0., 1., -4., 4.
        def __init__(self):
            t, x = np.linspace(0., 1., 4), np.linspace(-4., 4., 4)
            self.metric_splines = [RectBivariateSpline(t, x, np.zeros((4, 4))) for unused in range(4)]
        def metric(self, time, x):
            one, zero = np.ones_like(x), np.zeros_like(x)
            return MetricJets(one, zero, one, one, zero, zero, zero, zero, zero, zero)
    t = np.array([0., .5, 1.])
    edges = np.linspace(-2.5, -1.5, 5)
    x = (edges[:-1]+edges[1:])/2
    one, zero = np.ones((3, 4)), np.zeros((3, 4))
    old = dict(t=t, x=x, thermal=one, flux_energy=one, number=np.ones(4))
    model = StaticModel()
    reference = SimpleNamespace(t=t, x=x, h=SimpleNamespace(state=old, model=model))
    state = dict(heat=.5*one, heat_cap=np.ones(4))
    history = SimpleNamespace(h=SimpleNamespace(reference=reference, state=state),
        coefficients=lambda at, ax: dict(Q=np.zeros((len(at), len(ax)))),
        pressure=lambda at, ax: (np.zeros((len(at), len(ax))), None, None),
        energy=lambda ax: SimpleNamespace(evaluate=lambda at: (10*np.ones((len(at), len(ax))), None)))
    monkeypatch.setattr(replay, 'DenseHistory', lambda kind, path: history)
    source, output = tmp_path/'controls', tmp_path/'replay'
    source.mkdir(); output.mkdir()
    arrays = dict(t=t, x=x, edges=edges, amplitude=.1*one,
        positive_increment=zero[:-1], negative_increment=zero[:-1], thermal_inventory=one,
        balanced_radiation_inventory=2*one, receiver_thermal_energy=.5*one,
        receiver_reference_energy=.5*one, receiver_rated_capacity=np.ones(4),
        receiver_fixed_containment_energy=np.ones(4)/3, D=one,
        reference_fluid_density=one, thermal_return_rest=zero, receiver_hot_energy=.4*one)
    np.savez_compressed(source/'case_states.npz', **arrays)
    meta = dict(input='manufactured', common_phase_across_pair=True,
        existing_fluid_thermal_state_reallocated=True, existing_receiver_heat_reallocated=True,
        efficiency=.98, interface_sigma=0., guide_drift=.5, receiver_donor_turnover=10.)
    (source/'case_summary.json').write_text(json.dumps(meta))
    result = replay.audit((str(source), 'case', 2, str(output)))
    assert result['full_sampled_gate_passes']
    assert result['aggregate_panel_balance_residual'] == 0.
    assert result['split_donor_violation'] == 0.
    with np.load(output/'case_factor2_states.npz') as replayed:
        assert_allclose(replayed['balanced_radiation_inventory'], 2.)
        assert_allclose(replayed['counterstream_rest'], 2.)
        assert_allclose(replayed['thermal_reservoir_rest'], 1.)
        assert_allclose(replayed['receiver_hot_energy'], .4)
        assert_allclose(replayed['receiver_cold_energy'], .1)
        assert_allclose(replayed['credited_target'][0], 11.5)
    arrays['positive_increment'] = zero[:-1].copy()
    arrays['positive_increment'][0, 0] = -1e-15
    np.savez_compressed(source/'negative_states.npz', **arrays)
    (source/'negative_summary.json').write_text(json.dumps(meta))
    rejected = replay.audit((str(source), 'negative', 2, str(output)))
    assert not rejected['success']
    assert not rejected['conversion_increments_clipped']
    assert rejected['conversion_increment_minima']['positive_increment'] == -1e-15
