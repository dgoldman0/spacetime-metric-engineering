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


def test_replay_acceptance_requires_contact_and_energy_conservation():
    metrics={key:1e-14 for key in (
        'conversion_identity_residual','aggregate_panel_balance_residual',
        'maximum_explicit_wave_balance_residual','receiver_contact_subtraction_identity',
        'gauss4_8_panel_difference','gauss4_8_radiation_density_difference',
        'split_contact_identity','hot_contact_subtraction_identity','cold_contact_subtraction_identity',
        'hot_parent_heat_reconstruction_residual','cold_parent_heat_reconstruction_residual')}
    metrics['continuous_contact_reconstruction_applied']=True
    assert replay.replay_integrity(metrics)['numerical_integrity_checks_pass']
    for key in list(metrics)[:-1]:
        for error in (2e-9,np.nan):
            broken=dict(metrics,**{key:error})
            assert not replay.replay_integrity(broken)['numerical_integrity_checks_pass']
    del metrics['hot_parent_heat_reconstruction_residual']
    assert not replay.replay_integrity(metrics)['numerical_integrity_checks_pass']


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


def test_extra_preparation_is_one_conserved_inventory_with_its_full_stress_cost():
    one=np.ones((3,1)); M=np.array([[1.],[2.],[3.]])
    args=dict(phase=.1*one,radiation=.2*one,thermal=.2*one,receiver=.1*one,
              wall=0*one,incident=.2*one,returned=.1*one,guide_multiplier=1.5)
    lower,upper,fixed,possible=replay.preparation_interval(10*one,0*one,0*one,
                                                         metric_weight=M,**args)
    assert possible and fixed==0
    assert_allclose(lower,.6)
    assert np.all(upper>=lower)
    args['radiation']=args['radiation']+lower/M
    deficit,unused,floor=replay.full_budget(10*one,0*one,0*one,**args)
    assert deficit.max()<0 and floor.max()<=1e-15
    # The changing density has zero additional d(MW)/dt and needs no new feed.
    assert_allclose(np.diff(M*(args['radiation']-.2),axis=0),0.,atol=1e-15)


def test_initial_preparation_cannot_reuse_a_later_density_budget():
    zero=np.zeros((2,1));one=np.ones_like(zero)
    lower,upper,unused,possible=replay.preparation_interval(np.array([[10.],[.5]]),
        zero,zero,phase=zero,radiation=zero,thermal=zero,receiver=zero,wall=zero,
        incident=np.array([[1.],[0.]]),returned=zero,guide_multiplier=0.,metric_weight=one)
    assert not possible
    assert_allclose(lower,2.)
    assert_allclose(upper,1/6)


def test_bounded_conversion_repair_keeps_phase_and_existing_positive_cycles():
    amplitude=np.array([[.1],[.1-2e-10],[.3]])
    raw_amplitude=amplitude.copy()
    delta=np.diff(amplitude,axis=0)
    positive=np.array([[-1.954982948999832e-10],[delta[1,0]+.03]])
    negative=np.array([[0.],[.03]])
    raw_positive,raw_negative=positive.copy(),negative.copy()
    p,m,valid,reason,info=replay.conversion_controls(amplitude,positive,negative,repair=True)
    assert valid and reason is None and info['conversion_roundoff_repair_applied']
    assert p[0,0]==0. and m[0,0]==-delta[0,0]
    assert_allclose(p-m,delta,atol=0.,rtol=0.)
    assert p[1,0]==positive[1,0] and m[1,0]==negative[1,0]
    assert np.all(p>=0) and np.all(m>=0)
    assert_allclose(amplitude,raw_amplitude,atol=0.,rtol=0.)
    assert_allclose(positive,raw_positive,atol=0.,rtol=0.)
    assert_allclose(negative,raw_negative,atol=0.,rtol=0.)
    assert max(info['conversion_actual_maximum_changes'].values())<=1e-8


def test_conversion_repair_rejects_a_large_defect_and_returns_raw_controls():
    amplitude=np.array([[0.],[1e-5]])
    positive=np.zeros((1,1));negative=positive.copy()
    p,m,valid,reason,info=replay.conversion_controls(amplitude,positive,negative,repair=True)
    assert not valid and 'exceeds' in reason
    assert not info['conversion_roundoff_repair_applied']
    assert max(info['conversion_actual_maximum_changes'].values())==0.
    assert info['conversion_repair_proposed_maximum_changes']['positive_increment']==1e-5
    assert_allclose(p,positive,atol=0.,rtol=0.)
    assert_allclose(m,negative,atol=0.,rtol=0.)


def test_contact_roundoff_correction_is_bounded_and_explicit():
    hot=np.array([[-5e-11],[.2]]);cold=np.array([[0.],[.1]])
    qh,qc,valid,info=replay.nonnegative_contact_totals(hot,cold)
    assert valid and info['contact_roundoff_correction_applied']
    assert info['contact_roundoff_maximum_corrections']['hot']==5e-11
    assert qh[0,0]==0. and hot[0,0]==-5e-11
    qh,qc,valid,info=replay.nonnegative_contact_totals(-np.ones((2,1))*2e-10,cold)
    assert not valid and np.all(qh==-2e-10)
    assert not info['contact_roundoff_correction_applied']


def test_constant_prepared_inventories_cover_donors_without_changing_proper_power():
    hot=np.array([[.1],[.2],[.1]]);cold=np.array([[-.1],[0.],[.1]])
    K=np.ones((3,1))*.2;D=np.array([[1.],[8.],[27.]])
    qh=np.array([[.3],[.4]]);qc=np.array([[.2],[.3]]);dtau=np.array([[.1],[.2]])
    dh,dc,dk=replay.contact_preparation(hot,cold,K,D,qh,qc,dtau,np.ones(1),
                                       turnover=2.,temperature_floor=.4)
    assert_allclose(dh,1.4);assert_allclose(dc,.1);assert_allclose(dk,3.4)
    H,C,Knew=hot+dh,cold+dc,K+dk
    assert C.min()>=0
    for end in (slice(None,-1),slice(1,None)):
        assert np.max(qh-2*dtau*H[end])<1e-14
        assert np.max(qc-2*dtau*Knew[end]/D[end]**(1/3))<1e-14
    assert np.min(Knew/(3*D**(1/3)))>=.4-1e-14
    assert_allclose(np.diff(Knew,axis=0),np.diff(K,axis=0),atol=1e-15)
    assert_allclose(np.diff(H+C,axis=0),np.diff(hot+cold,axis=0),atol=1e-15)


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
    receiver_x = np.r_[edges[0], x, edges[-1]]
    capacity = .7+.6*(receiver_x-edges[0])/(edges[-1]-edges[0])
    local_capacity = np.interp(x, receiver_x, capacity)
    reference = SimpleNamespace(t=t, x=receiver_x, h=SimpleNamespace(state=old, model=model))
    state = dict(heat=.5*np.ones((len(t), len(receiver_x))), heat_cap=capacity)
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
        receiver_reference_energy=.5*one, receiver_rated_capacity=local_capacity,
        receiver_fixed_containment_energy=local_capacity/3, D=one,
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
    assert result['receiver_capacity_interpolation_difference'] > .01
    assert result['receiver_capacity_violation'] == 0.
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
    # Opting in reconstructs a tiny release from the exact archived phase and
    # reruns all six streams; the old cached zero-wave arrays are irrelevant.
    arrays['amplitude']=.1*one.copy()
    arrays['amplitude'][1:]-=2e-10
    arrays['positive_increment']=zero[:-1].copy()
    arrays['positive_increment'][0]=-1.954982948999832e-10
    arrays['negative_increment']=zero[:-1].copy()
    np.savez_compressed(source/'repaired_states.npz',**arrays)
    (source/'repaired_summary.json').write_text(json.dumps(meta))
    calls=[];original_propagate=replay.propagate
    def counted_propagate(*args,**kwargs):
        calls.append(1)
        return original_propagate(*args,**kwargs)
    monkeypatch.setattr(replay,'propagate',counted_propagate)
    repaired=replay.audit((str(source),'repaired',2,str(output),False,True))
    assert repaired['success'] and repaired['conversion_roundoff_repair_applied']
    assert len(calls)==6
    with np.load(output/'repaired_factor2_states.npz') as replayed:
        assert_allclose(replayed['control_time'],t,atol=0.,rtol=0.)
        assert_allclose(replayed['control_amplitude'],arrays['amplitude'],atol=0.,rtol=0.)
        assert_allclose(replayed['applied_positive_increment']-replayed['applied_negative_increment'],
                        np.diff(arrays['amplitude'],axis=0),atol=0.,rtol=0.)
        assert replayed['work_return_rest'].max()>0
        assert replayed['heat_return_rest'].max()>0
        assert_allclose(replayed['absorption_rest'],0.,atol=0.,rtol=0.)
    # The old converter has unresolved positive variations inside each coarse
    # control panel. Zero parent hot withdrawal should stay zero, whereas a
    # linear interpolation of the old hot store would create negative qh.
    baseline_t=np.linspace(0.,1.,5)
    old.update(t=baseline_t,thermal=np.ones((5,4)),flux_energy=baseline_t[:,None]**2*np.ones((5,4)))
    coefficient=1/.98-1
    arrays['amplitude']=.1*one
    arrays['positive_increment']=zero[:-1].copy()
    arrays['negative_increment']=zero[:-1].copy()
    arrays['receiver_hot_energy']=.4*one+coefficient*t[:,None]**2
    arrays['receiver_thermal_energy']=.5*one+coefficient*t[:,None]**2
    arrays['receiver_hot_contact_panel_heat']=zero[:-1].copy()
    arrays['receiver_cold_contact_panel_heat']=zero[:-1].copy()
    np.savez_compressed(source/'contact_states.npz',**arrays)
    (source/'contact_summary.json').write_text(json.dumps(meta))
    reconstructed=replay.audit((str(source),'contact',4,str(output),False,False,True))
    assert reconstructed['full_sampled_gate_passes']
    assert reconstructed['continuous_contact_reconstruction_applied']
    assert reconstructed['maximum_receiver_energy_source_panel_change']>1e-4
    assert reconstructed['receiver_contact_subtraction_identity']<1e-14
    with np.load(output/'contact_factor4_states.npz') as replayed:
        assert_allclose(replayed['receiver_hot_contact_panel_heat'],0.,atol=0.,rtol=0.)
        assert_allclose(replayed['receiver_cold_contact_panel_heat'],0.,atol=0.,rtol=0.)
        assert_allclose(replayed['balanced_radiation_inventory']+replayed['receiver_thermal_energy'],
                        2.5,atol=1e-14)
        assert np.all(np.diff(replayed['receiver_hot_energy'],axis=0)>=0)
        assert_allclose(replayed['additional_prepared_thermal_inventory'],0.)
