#!/usr/bin/env python3
"""Integrated bank-capacity bounds for fixed complementary-photon histories.

Hot photon production uses initial hot inventory and registered converter
losses. Absorbed photons accumulate in the cold bank without export. The
screen grants both banks all their capacity for these duties; their remaining
fluid heat contacts supply no additional credit.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess
import sys

import numpy as np

from adm_harness.source_ledger import sha256_file
from audit_joint_dense_work import DenseHistory
from audit_joint_support import bilinear
from audit_virtual_cell_bank_routing import verify_archive
from audit_virtual_cell_thermal_replay import geometry, integrate_panels, linear_history
from run_poynting_delivery import BASE, ROOT, write_json

CAPACITY_ABSOLUTE_TOLERANCE = 1e-7
CAPACITY_RELATIVE_TOLERANCE = 1e-8
QUADRATURE_ABSOLUTE_TOLERANCE = 1e-7
QUADRATURE_RELATIVE_TOLERANCE = 1e-6


def counter_energy_source(U0, U0_t, logD_t, Z0_t, K_t, D, lapse,
                          converter_loss, hot_rate, cold_rate):
    """Coordinate-label S=N D P_c and the applied receiver derivative.

    Hot/cold rates are proper-label powers; converter_loss is coordinate-label
    energy per coordinate time. Original fluid and receiver duties occur once.
    """
    Z_t = converter_loss-lapse*hot_rate+lapse*cold_rate
    source = U0_t+U0*logD_t/3+Z0_t-Z_t-K_t/D**(1/3)
    return source, Z_t


def capacity_bounds(positive_panels, negative_panels, converter_loss_panels,
                    capacity, hot_initial, *, positive_proper_peak=None, turnover=None):
    """Favorable necessary ratings from separate positive and negative energy."""
    positive, negative, loss = [np.asarray(v, float) for v in
        (positive_panels, negative_panels, converter_loss_panels)]
    capacity, hot_initial = map(lambda v: np.asarray(v, float), (capacity, hot_initial))
    if (positive.ndim != 2 or min(positive.shape) < 1 or negative.shape != positive.shape
            or loss.shape != positive.shape or capacity.shape != positive.shape[1:]
            or hot_initial.shape != capacity.shape
            or not all(np.isfinite(v).all() for v in (positive, negative, loss, capacity, hot_initial))
            or any(np.any(v < 0) for v in (positive, negative, loss, capacity))):
        raise ValueError('nonnegative finite panel energies and matching local capacities required')
    cumulative = [np.vstack([np.zeros(positive.shape[1]), np.cumsum(v, axis=0)])
                  for v in (positive, negative, loss)]
    emitted, absorbed, supplied = cumulative
    hot_deficit = emitted-supplied
    hot_lower = np.maximum(0., hot_deficit.max(axis=0))
    cold_lower = absorbed[-1]
    result = dict(cumulative_positive_counter=emitted, cumulative_negative_counter=absorbed,
        cumulative_converter_loss=supplied, cumulative_hot_draw_without_initial=hot_deficit,
        cumulative_net_counter=emitted-absorbed,
        required_hot_initial=hot_lower, required_cold_rating=cold_lower,
        rate_independent_total_rating_lower=hot_lower+cold_lower,
        rate_independent_capacity_margin=capacity-hot_lower-cold_lower,
        retained_hot_initial_margin=hot_initial-hot_lower,
        hot_initial_witness_index=np.argmax(hot_deficit, axis=0))
    if (positive_proper_peak is None) != (turnover is None):
        raise ValueError('sampled proper power and turnover must be supplied together')
    if turnover is not None:
        peak = np.asarray(positive_proper_peak, float)
        if (peak.shape != capacity.shape or not np.isfinite(peak).all() or np.any(peak < 0)
                or not np.isfinite(turnover) or turnover <= 0):
            raise ValueError('finite nonnegative sampled powers and positive turnover required')
        rate_hot_lower = peak/turnover
        hot_rating = np.maximum(hot_lower, rate_hot_lower)
        result.update(sampled_turnover_hot_rating_lower=rate_hot_lower,
            required_hot_rating_with_turnover=hot_rating,
            total_rating_lower_with_turnover=hot_rating+cold_lower,
            capacity_margin_with_turnover=capacity-hot_rating-cold_lower)
    return result


def evaluate(spec):
    path, output = map(Path, spec)
    label = path.stem.removesuffix('_states')
    meta = json.loads(path.with_name(label+'_summary.json').read_text())
    with np.load(path) as f:
        s = {key: f[key] for key in f.files}
    t, x = s['t'], s['x']
    if (t.ndim != 1 or x.ndim != 1 or len(t) < 2 or not len(x)
            or not np.isfinite(t).all() or not np.isfinite(x).all()
            or np.any(np.diff(t) <= 0) or np.any(np.diff(x) <= 0)):
        raise ValueError('ordered finite replay time and spatial grids required')
    contact_time, contact_x = s['contact_control_time'], s['contact_control_position']
    hot_rate, cold_rate = [s[key] for key in
        ('applied_hot_parent_proper_rate', 'applied_cold_parent_proper_rate')]
    expected = (len(contact_time)-1, len(x))
    if (not np.array_equal(contact_x, x) or np.any(np.diff(contact_time) <= 0)
            or t[0] < contact_time[0] or t[-1] > contact_time[-1]
            or hot_rate.shape != expected or cold_rate.shape != expected
            or not all(np.isfinite(a).all() for a in (contact_time, hot_rate, cold_rate))
            or np.any(hot_rate < 0) or np.any(cold_rate < 0)):
        raise ValueError('saved nonnegative proper contact rates covering the replay are required')
    h = DenseHistory('routed_family', ROOT/meta['input'])
    model, old, ref = h.h.reference.h.model, h.h.reference.h.state, h.h.reference
    original_capacity = np.interp(x, ref.x, h.h.state['heat_cap'])
    if not np.allclose(original_capacity, s['receiver_rated_capacity'], rtol=0., atol=1e-10):
        raise ValueError('replay bank rating differs from the registered original capacity')
    metric_knots = np.unique(np.concatenate([spline.get_knots()[0] for spline in model.metric_splines]))
    knots = np.unique(np.r_[t, contact_time, s['control_time'], old['t'], ref.t, metric_knots])
    cuts = knots[(knots >= t[0]) & (knots <= t[-1])]
    efficiency = meta.get('original_converter_efficiency', .98)
    if not np.isfinite(efficiency) or not 0 < efficiency <= 1:
        raise ValueError('registered converter efficiency must lie in (0,1]')

    def rates(at):
        g = geometry(model, at, x)
        U0, U0_t, _ = bilinear(old['t'], old['x'], old['thermal'], at, x)
        Z0_t = bilinear(ref.t, ref.x, h.h.state['heat'], at, x)[1]
        flux_t = bilinear(old['t'], old['x'], old['flux_energy'], at, x)[1]
        K_t = linear_history(t, s['thermal_inventory'], at)[1]
        loss = g['ell']/g['radius']**2*((1/efficiency-1)*np.maximum(flux_t, 0.)
                +(1-efficiency)*np.maximum(-flux_t, 0.))
        owner = np.clip(np.searchsorted(contact_time, at, side='right')-1, 0, len(contact_time)-2)
        source, Z_t = counter_energy_source(U0, U0_t, g['logD_t'], Z0_t, K_t,
            g['D'], g['lapse'], loss, hot_rate[owner], cold_rate[owner])
        return dict(source=source, loss=loss, receiver_rate=Z_t,
            proper_counter_power=source/g['lapse'], lapse=g['lapse'], D=g['D'],
            proper_hot_rate=hot_rate[owner], proper_cold_rate=cold_rate[owner])

    def integrand(at):
        r = rates(at)
        return np.array([np.maximum(r['source'], 0.), np.maximum(-r['source'], 0.),
                         r['loss'], r['source'], r['receiver_rate']])

    panel8 = integrate_panels(t, cuts, integrand, order=8)
    panel4 = integrate_panels(t, cuts, integrand, order=4)
    # Sample both interiors next to derivative knots. This is a lower bound
    # on a continuous supremum; no maximum between samples is asserted.
    rate_times = np.unique(np.r_[t, cuts[:-1]+np.diff(cuts)/4,
                                (cuts[:-1]+cuts[1:])/2, cuts[:-1]+3*np.diff(cuts)/4])
    sampled = rates(rate_times)
    positive_power = np.maximum(sampled['proper_counter_power'], 0.)
    peak = positive_power.max(axis=0)
    turnover = meta.get('receiver_contact_turnover_bound')
    if turnover is None or not np.isfinite(turnover) or turnover <= 0:
        raise ValueError('a positive archived contact turnover is required for the separate rate screen')
    initial_hot = s['receiver_hot_energy'][0]
    bounds8 = capacity_bounds(*panel8[:3], original_capacity, initial_hot,
                             positive_proper_peak=peak, turnover=turnover)
    bounds4 = capacity_bounds(*panel4[:3], original_capacity, initial_hot,
                             positive_proper_peak=peak, turnover=turnover)
    tolerance = CAPACITY_ABSOLUTE_TOLERANCE+CAPACITY_RELATIVE_TOLERANCE*original_capacity
    cumulative_difference = np.array([bounds8[k]-bounds4[k] for k in
        ('cumulative_positive_counter','cumulative_negative_counter','cumulative_converter_loss')])
    quadrature_scale = np.maximum.reduce([bounds8[k].max(axis=0) for k in
        ('cumulative_positive_counter','cumulative_negative_counter','cumulative_converter_loss')])
    quadrature_tolerance = QUADRATURE_ABSOLUTE_TOLERANCE+QUADRATURE_RELATIVE_TOLERANCE*quadrature_scale
    quadrature_ok = bool(np.all(abs(cumulative_difference).max(axis=(0,1)) <= quadrature_tolerance))
    capacity_ok = bool(np.all(bounds8['rate_independent_capacity_margin'] >= -tolerance))
    capacity4_ok = bool(np.all(bounds4['rate_independent_capacity_margin'] >= -tolerance))
    rate_ok = bool(np.all(bounds8['capacity_margin_with_turnover'] >= -tolerance))
    retained_initial_ok = bool(np.all(bounds8['retained_hot_initial_margin'] >= -tolerance))
    parent_ok = bool(meta.get('success') and meta.get('full_sampled_gate_passes'))
    source_identity = np.cumsum(panel8[0]-panel8[1]-panel8[3], axis=0)
    receiver_identity = np.diff(s['receiver_thermal_energy'], axis=0)-panel8[4]

    def witness(j):
        i = int(bounds8['hot_initial_witness_index'][j])
        k = int(positive_power[:,j].argmax())
        return dict(x=float(x[j]), hot_initial_witness_time=float(t[i]),
            cumulative_emission=float(bounds8['cumulative_positive_counter'][i,j]),
            cumulative_converter_loss=float(bounds8['cumulative_converter_loss'][i,j]),
            required_hot_initial=float(bounds8['required_hot_initial'][j]),
            retained_hot_initial=float(initial_hot[j]),
            required_cold_rating=float(bounds8['required_cold_rating'][j]),
            original_total_rating=float(original_capacity[j]),
            rate_independent_total_rating_lower=float(bounds8['rate_independent_total_rating_lower'][j]),
            rate_independent_capacity_margin=float(bounds8['rate_independent_capacity_margin'][j]),
            sampled_peak_emission_time=float(rate_times[k]),
            sampled_peak_proper_emission=float(positive_power[k,j]),
            sampled_turnover_hot_rating_lower=float(bounds8['sampled_turnover_hot_rating_lower'][j]),
            total_rating_lower_with_turnover=float(bounds8['total_rating_lower_with_turnover'][j]),
            final_net_counter_energy=float(bounds8['cumulative_net_counter'][-1,j]),
            gauss4_8_required_hot_initial_difference=float(abs(bounds8['required_hot_initial'][j]-bounds4['required_hot_initial'][j])),
            gauss4_8_cold_rating_difference=float(abs(bounds8['required_cold_rating'][j]-bounds4['required_cold_rating'][j])))

    summary = dict(label=label, input=str(path.relative_to(ROOT)),
        parent_full_sampled_gate_passes=parent_ok,
        time_samples=len(t), spatial_samples=len(x), integration_subpanels=len(cuts)-1,
        rate_sample_count=len(rate_times),
        rate_independent_capacity_gate_passes=capacity_ok,
        gauss4_rate_independent_capacity_gate_passes=capacity4_ok,
        sampled_turnover_capacity_gate_passes=rate_ok,
        retained_initial_hot_inventory_gate_passes=retained_initial_ok,
        quadrature_comparison_passes=quadrature_ok,
        fixed_history_integrated_capacity_gate_passes=bool(parent_ok and quadrature_ok and capacity_ok
            and retained_initial_ok and rate_ok),
        rate_independent_failing_positions=int((bounds8['rate_independent_capacity_margin'] < -tolerance).sum()),
        rate_independent_minimum_capacity_margin=float(bounds8['rate_independent_capacity_margin'].min()),
        maximum_required_hot_initial=float(bounds8['required_hot_initial'].max()),
        maximum_required_cold_rating=float(bounds8['required_cold_rating'].max()),
        maximum_total_rating_lower=float(bounds8['rate_independent_total_rating_lower'].max()),
        maximum_absolute_final_net_counter_energy=float(abs(bounds8['cumulative_net_counter'][-1]).max()),
        gauss4_8_maximum_panel_difference=float(abs(panel8-panel4).max()),
        gauss4_8_maximum_cumulative_energy_difference=float(abs(cumulative_difference).max()),
        gauss4_8_maximum_total_rating_lower_difference=float(abs(
            bounds8['rate_independent_total_rating_lower']-bounds4['rate_independent_total_rating_lower']).max()),
        integrated_positive_negative_source_identity_residual=float(abs(source_identity).max()),
        reconstructed_receiver_energy_identity_residual=float(abs(receiver_identity).max()),
        archived_turnover=float(turnover), original_converter_efficiency=float(efficiency),
        capacity_absolute_tolerance=CAPACITY_ABSOLUTE_TOLERANCE,
        capacity_relative_tolerance=CAPACITY_RELATIVE_TOLERANCE,
        quadrature_absolute_tolerance=QUADRATURE_ABSOLUTE_TOLERANCE,
        quadrature_relative_tolerance=QUADRATURE_RELATIVE_TOLERANCE,
        fixed_phase_fluid_and_receiver_histories=True, cold_initial_lower_bound_assumed=0.,
        cold_export_allowed=False, remaining_fluid_heat_contacts_credited=False,
        inventories_or_capacity_modified=False, opacity_or_force_law_supplied=False,
        continuum_quadrature_error_bound_certified=False,
        scope='fixed reconstructed histories; favorable necessary separate bank ratings; positive and negative counter energy integrated separately; contact turnover screen reported separately',
        source_method='exact registered geometry and baseline histories, piecewise-linear replay K, saved proper hot/cold rates giving Z_t=Lcoord-N qh+N qc',
        integration_method='Gauss8 with Gauss4 comparison split at every replay, control, contact, baseline and metric time knot; cumulative lower bounds at replay times',
        rate_method='proper counter power sampled at replay nodes and quarter/mid/three-quarter integration panels; sampled maximum bounds the continuous supremum from below',
        worst_capacity_witness=witness(int(bounds8['rate_independent_capacity_margin'].argmin())),
        positions=[witness(j) for j in range(len(x))])
    arrays = dict(t=t,x=x,integration_cuts=cuts,original_capacity=original_capacity,
        retained_hot_initial=initial_hot,retained_cold_initial=s['receiver_cold_energy'][0],
        positive_counter_panel=panel8[0],negative_counter_panel=panel8[1],
        converter_loss_panel=panel8[2],signed_counter_panel=panel8[3],receiver_energy_panel=panel8[4],
        gauss4_panels=panel4,gauss8_panels=panel8,
        gauss4_8_cumulative_energy_difference=cumulative_difference,
        integrated_source_identity_residual=source_identity,
        reconstructed_receiver_energy_identity_residual=receiver_identity,
        capacity_tolerance=tolerance,quadrature_tolerance=quadrature_tolerance,
        rate_times=rate_times,**{'sampled_'+key:value for key,value in sampled.items()},**bounds8)
    arrays.update({'gauss4_'+key:value for key,value in bounds4.items()})
    np.savez_compressed(output/(label+'_capacity.npz'), **arrays)
    write_json(output/(label+'_summary.json'), summary)
    print(label+': '+json.dumps({key:summary[key] for key in
        ('rate_independent_capacity_gate_passes','rate_independent_minimum_capacity_margin',
         'gauss4_8_maximum_cumulative_energy_difference')}), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay',required=True)
    parser.add_argument('--output-name',required=True)
    parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--labels',nargs='+')
    args = parser.parse_args()
    if not 1 <= args.workers <= 2:
        parser.error('one or two workers required')
    source, output = BASE/args.replay, BASE/args.output_name
    if output.exists():
        raise RuntimeError('preserve completed integrated bank-capacity audit')
    manifest, hashes = verify_archive(source)
    labels = args.labels or [p.stem.removesuffix('_states') for p in sorted(source.glob('*_states.npz'))]
    if not labels:
        raise ValueError('completed replay states required')
    paths = [source/(label+'_states.npz') for label in labels]
    for path in paths:
        if path.name not in manifest['output_sha256']:
            raise RuntimeError('unregistered replay state: '+str(path))
        summary = path.with_name(path.stem.removesuffix('_states')+'_summary.json')
        if summary.name not in manifest['output_sha256']:
            raise RuntimeError('unregistered replay summary: '+str(summary))
    runtime = [Path(__file__),ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_bank_capacity.py']
    for module in list(sys.modules.values()):
        filename = getattr(module,'__file__',None)
        if filename:
            path = Path(filename).resolve()
            if path.suffix == '.py' and path.is_relative_to(ROOT):
                runtime.append(path)
    for path in runtime:
        hashes[str(path.relative_to(ROOT))] = sha256_file(path)
    output.mkdir()
    with ProcessPoolExecutor(max_workers=min(args.workers,len(paths)),
            mp_context=multiprocessing.get_context('spawn')) as pool:
        cases = list(pool.map(evaluate, [(p,output) for p in paths]))
    for relative, expected in hashes.items():
        if sha256_file(ROOT/relative) != expected:
            raise RuntimeError('input changed during bank-capacity audit: '+relative)
    write_json(output/'summary.json',dict(cases=cases))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        workers=min(args.workers,len(paths)),input_sha256=hashes,
        output_sha256={p.name:sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
