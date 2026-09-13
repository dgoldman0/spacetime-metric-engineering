#!/usr/bin/env python3
"""Replay counted phase, waves, fluid and receiver on the changing metric.

The explicit beams use the independent limited finite-volume propagator.
Total balanced radiation follows its aggregate energy equation, retaining the
prepared inventory and prescribed fluid/receiver histories. Its constituent
opacity and reciprocal force equations remain separate construction duties.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess
import sys
import time

import numpy as np
from numpy.polynomial.legendre import leggauss

from adm_harness.poynting_delivery import propagate
from adm_harness.source_ledger import sha256_file
from audit_joint_dense_work import DenseHistory
from audit_joint_support import bilinear
from audit_virtual_cell_ports import validate_controls
from run_poynting_delivery import BASE, ROOT, write_json


def linear_history(times, values, at):
    """Piecewise-linear values and their one-sided interior derivatives."""
    times, values, at = map(np.asarray, (times, values, at))
    index = np.clip(np.searchsorted(times, at, side='right')-1, 0, len(times)-2)
    slope = (values[index+1]-values[index])/np.diff(times)[index, None]
    return values[index]+(at-times[index])[:, None]*slope, slope


def spatial_history(oldx, values, x):
    """Interpolate each cell separately, holding its outermost centre value."""
    oldx, values, x = map(np.asarray, (oldx, values, x))
    if oldx.size % 2 or x.size % 2:
        raise ValueError('paired even spatial grids required')
    rows = np.atleast_2d(values)
    result = np.empty((len(rows), len(x)))
    for half in (0, 1):
        old = slice(half*len(oldx)//2, (half+1)*len(oldx)//2)
        new = slice(half*len(x)//2, (half+1)*len(x)//2)
        result[:, new] = [np.interp(x[new], oldx[old], row[old]) for row in rows]
    return result[0] if values.ndim == 1 else result


def integrate_panels(times, breaks, evaluator, *, order=8, batch=64):
    """Gauss integration of (..., time, space) values, split at every knot."""
    times = np.asarray(times)
    if order < 2 or np.any(np.diff(times) <= 0):
        raise ValueError('ordered times and quadrature order >=2 required')
    cuts = np.unique(np.r_[times, breaks])
    cuts = cuts[(cuts >= times[0]) & (cuts <= times[-1])]
    z, w = leggauss(order)
    at = (cuts[:-1, None]+np.diff(cuts)[:, None]*(z+1)/2).ravel()
    values = np.concatenate([evaluator(at[i:i+batch])
                             for i in range(0, len(at), batch)], axis=-2)
    shape = values.shape[:-2]+(len(cuts)-1, order, values.shape[-1])
    pieces = np.sum(values.reshape(shape)*np.diff(cuts)[:, None, None]
                    *w[None, :, None]/2, axis=-2)
    result = np.zeros(values.shape[:-2]+(len(times)-1, values.shape[-1]))
    owner = np.searchsorted(times, (cuts[:-1]+cuts[1:])/2)-1
    # Quantities are few; this keeps panel accumulation transparent.
    for i in range(len(owner)):
        result[..., owner[i], :] += pieces[..., i, :]
    return result


def reconstruct_inventory(initial, phase, thermal, receiver, baseline):
    """V_t=-ell² A_t-psi K_t-ell Z_t+N M(P_fluid0+P_Z0)."""
    change = -phase-thermal-receiver+baseline
    return np.vstack([initial, initial+np.cumsum(change, axis=0)])


def full_budget(rho, p, q, *, phase, radiation, thermal, receiver, wall,
                incident, returned, guide_multiplier):
    """Full counted tensor and guide cone; radiation includes extra balance."""
    residual_rho = rho-phase-radiation-thermal-receiver-wall
    residual_p = p+phase-radiation-thermal/3
    residual_q = q+wall-thermal/3
    guide = np.maximum(guide_multiplier*(incident+returned)-phase/2, 0.)
    minimum = np.maximum.reduce([residual_p+2*residual_q,
        residual_p-residual_q+3*guide, -2*residual_p-residual_q])
    return minimum-residual_rho, guide, 2*np.maximum(incident, returned)-radiation


def preparation_interval(rho, p, q, *, phase, radiation, thermal, receiver,
                         wall, incident, returned, guide_multiplier, metric_weight):
    """Allowed time-independent addition to V=M*W at each material label.

    Two cone facets are independent of balanced radial radiation; the third
    pays three times its added density. A constant addition to V preserves
    the already integrated radiation energy equation, including its source.
    """
    rr = rho-phase-radiation-thermal-receiver-wall
    rp = p+phase-radiation-thermal/3
    rq = q+wall-thermal/3
    guide = np.maximum(guide_multiplier*(incident+returned)-phase/2, 0.)
    fixed = np.maximum(rp+2*rq-rr, rp-rq+3*guide-rr)
    lower = np.maximum(0., np.max(metric_weight*(2*np.maximum(incident, returned)-radiation), axis=0))
    upper = np.min(metric_weight*(rr+2*rp+rq)/3, axis=0)
    possible = bool(np.max(fixed) <= 2e-7 and np.all(upper >= lower))
    return lower, upper, positive_max(fixed), possible


def geometry(model, times, x):
    """Registered spline metric in its unblended interior, including gamma_t."""
    if (np.any(abs(x) >= 5) or np.any(x < model.x_min) or np.any(x > model.x_max)
            or times[0] < model.t_min or times[-1] > model.t_max):
        raise ValueError('thermal replay is restricted to the registered metric interior')
    tt, xx = np.meshgrid(times, x, indexing='ij')
    value = [s.ev(tt, xx) for s in model.metric_splines]
    dt = [s.ev(tt, xx, dx=1) for s in model.metric_splines]
    alpha, beta, b, radius = np.exp(value[0]), value[1], np.exp(value[2]), np.exp(value[3])
    v = b*beta/alpha
    if np.any(abs(v) >= 1):
        raise ValueError('material worldline must remain timelike')
    gamma = 1/np.sqrt(1-v*v)
    vt = v*(dt[2]-dt[0])+b*dt[1]/alpha
    ell = b*gamma
    return dict(alpha=alpha, b=b, radius=radius, v=v, gamma=gamma, ell=ell,
        D=ell*radius**2, M=(ell*radius)**2, lapse=alpha/gamma,
        logD_t=dt[2]+2*dt[3]+gamma**2*v*vt)


def positive_max(a):
    return max(0., float(np.max(a)))


def conversion_controls(amplitude, positive, negative, *, repair=False):
    """Explicit bounded repair, preserving phase and positive overlap cycles.

    Arrays returned on rejection are copies of the raw controls. Reconstruction
    uses d=DeltaA and overlap=max(0,min(p,m)); its hard absolute allowance is
    1e-8 for either increment. The source arrays are never modified in place.
    """
    amplitude, positive, negative = map(np.asarray, (amplitude, positive, negative))
    if (amplitude.ndim != 2 or positive.shape != (len(amplitude)-1, amplitude.shape[1])
            or negative.shape != positive.shape or not all(np.isfinite(a).all()
                for a in (amplitude, positive, negative))):
        raise ValueError('finite matching phase and conversion histories required')
    change = np.diff(amplitude, axis=0)
    minima = dict(positive_increment=float(positive.min()), negative_increment=float(negative.min()))
    original_error = float(abs(change-positive+negative).max())
    proposed = dict(positive_increment=0., negative_increment=0.)
    applied_positive, applied_negative = positive.copy(), negative.copy()
    valid, reason, applied = True, None, False
    if repair:
        overlap = np.maximum(0., np.minimum(positive, negative))
        candidate_positive = np.maximum(change, 0.)+overlap
        candidate_negative = np.maximum(-change, 0.)+overlap
        proposed = dict(positive_increment=float(abs(candidate_positive-positive).max()),
                        negative_increment=float(abs(candidate_negative-negative).max()))
        if max(proposed.values()) > 1e-8:
            valid = False
            reason = 'phase-preserving conversion repair exceeds the 1e-8 allowance; raw controls retained'
        else:
            applied_positive, applied_negative = candidate_positive, candidate_negative
            applied = max(proposed.values()) > 0.
    elif min(minima.values()) < 0:
        valid = False
        reason = 'negative archived conversion increment; controls were left unchanged'
    elif original_error > 1e-8:
        valid = False
        reason = 'archived phase/conversion identity exceeds tolerance; controls were left unchanged'
    actual = dict(positive_increment=float(abs(applied_positive-positive).max()),
                  negative_increment=float(abs(applied_negative-negative).max()))
    metadata = dict(conversion_increment_minima=minima, conversion_increments_clipped=False,
        conversion_roundoff_repair_requested=bool(repair), conversion_roundoff_repair_applied=applied,
        conversion_roundoff_repair_allowance=1e-8,
        conversion_repair_proposed_maximum_changes=proposed, conversion_actual_maximum_changes=actual,
        original_conversion_identity_residual=original_error,
        conversion_identity_residual=float(abs(change-applied_positive+applied_negative).max()),
        conversion_repair_method='d=DeltaA; overlap=max(0,min(p_old,m_old)); p=max(d,0)+overlap; m=max(-d,0)+overlap')
    return applied_positive, applied_negative, valid, reason, metadata


def nonnegative_contact_totals(hot, cold):
    """Explicitly correct only negative contact roundoff no larger than 1e-10."""
    hot, cold = map(np.asarray, (hot, cold))
    if hot.ndim != 2 or cold.shape != hot.shape or not all(np.isfinite(a).all() for a in (hot, cold)):
        raise ValueError('finite matching parent hot/cold contact arrays required')
    minimum = dict(hot=float(hot.min()), cold=float(cold.min()))
    valid = min(minimum.values()) >= -1e-10
    applied_hot = np.maximum(hot, 0.) if valid else hot.copy()
    applied_cold = np.maximum(cold, 0.) if valid else cold.copy()
    corrections = dict(hot=float(abs(applied_hot-hot).max()), cold=float(abs(applied_cold-cold).max()))
    return applied_hot, applied_cold, valid, dict(contact_original_parent_minima=minimum,
        contact_roundoff_allowance=1e-10, contact_roundoff_maximum_corrections=corrections,
        contact_roundoff_correction_applied=max(corrections.values()) > 0.)


def contact_preparation(hot, cold, thermal_inventory, D, hot_panel, cold_panel,
                        duration, number, *, turnover, temperature_floor=0.,
                        fluid_cold_panel=None):
    """Minimal nonnegative constant label inventories for sampled donor bounds."""
    hot, cold, thermal_inventory, D, hot_panel, cold_panel, duration, number = map(np.asarray,
        (hot, cold, thermal_inventory, D, hot_panel, cold_panel, duration, number))
    if (hot.shape != cold.shape or hot.shape != thermal_inventory.shape or D.shape != hot.shape
            or hot_panel.shape != (len(hot)-1, hot.shape[1]) or cold_panel.shape != hot_panel.shape
            or duration.shape != hot_panel.shape or number.shape != (hot.shape[1],)
            or np.any(duration <= 0) or np.any(D <= 0) or np.any(number <= 0)
            or np.any(hot_panel < 0) or np.any(cold_panel < 0)
            or not np.isfinite(turnover) or turnover <= 0 or not np.isfinite(temperature_floor)
            or temperature_floor < 0
            or not all(np.isfinite(a).all() for a in
                       (hot, cold, thermal_inventory, D, hot_panel, cold_panel, duration, number))):
        raise ValueError('finite physical states, nonnegative heats, and positive donor scales required')
    fluid_cold = cold_panel if fluid_cold_panel is None else np.asarray(fluid_cold_panel)
    if (fluid_cold.shape != cold_panel.shape or not np.isfinite(fluid_cold).all()
            or np.any(fluid_cold < 0)):
        raise ValueError('finite nonnegative actual fluid cold heat required')
    required_hot = hot_panel/(turnover*duration)
    required_fluid = fluid_cold/(turnover*duration)
    dh = np.maximum.reduce([np.zeros(hot.shape[1]), np.max(-hot, axis=0),
        np.max(required_hot-hot[:-1], axis=0), np.max(required_hot-hot[1:], axis=0)])
    dc = np.maximum(0., np.max(-cold, axis=0))
    dk = np.maximum.reduce([np.zeros(hot.shape[1]), np.max(-thermal_inventory, axis=0),
        np.max(required_fluid*D[:-1]**(1/3)-thermal_inventory[:-1], axis=0),
        np.max(required_fluid*D[1:]**(1/3)-thermal_inventory[1:], axis=0),
        np.max(3*number*temperature_floor*D**(1/3)-thermal_inventory, axis=0)])
    return dh, dc, dk


def replay_integrity(metrics):
    """Require conservation identities and quadrature agreement as well as stress."""
    keys = ['conversion_identity_residual', 'aggregate_panel_balance_residual',
        'maximum_explicit_wave_balance_residual', 'receiver_contact_subtraction_identity',
        'gauss4_8_panel_difference', 'gauss4_8_radiation_density_difference']
    if 'split_contact_identity' in metrics:
        keys += ['split_contact_identity', 'hot_contact_subtraction_identity',
                 'cold_contact_subtraction_identity']
    if metrics.get('continuous_contact_reconstruction_applied'):
        keys += ['hot_parent_heat_reconstruction_residual', 'cold_parent_heat_reconstruction_residual']
    if metrics.get('bank_counter_contact_reconstruction'):
        keys += ['bank_counter_panel_power_identity_residual',
                 'bank_hot_partition_identity_residual', 'bank_cold_partition_identity_residual']
    values = np.asarray([metrics.get(key, np.nan) for key in keys], dtype=float)
    return dict(numerical_integrity_checks_pass=bool(np.isfinite(values).all()
        and np.all(values >= 0) and np.max(values) <= 1e-9),
        numerical_integrity_absolute_tolerance=1e-9, numerical_integrity_checked_fields=keys)


def audit(spec):
    source, label, factor, output, *options = spec
    if len(options) > 3:
        raise ValueError('at most preparation, conversion-repair and contact-reconstruction options are accepted')
    prepare_radiation = bool(options[0]) if options else False
    repair_conversion = bool(options[1]) if len(options) > 1 else False
    reconstruct_contacts = bool(options[2]) if len(options) > 2 else False
    started = time.monotonic()
    source, output = Path(source), Path(output)
    meta = json.loads((source/(label+'_summary.json')).read_text())
    bank_mode = bool(meta.get('bank_counter_relaxation'))
    if bank_mode and not reconstruct_contacts:
        raise ValueError('bank-counter controls require continuous contact reconstruction')
    with np.load(source/(label+'_states.npz')) as f:
        s = {key: f[key] for key in f.files}
    stem = label+f'_factor{factor}'
    positive_applied, negative_applied, valid, reason, conversion_metadata = conversion_controls(
        s['amplitude'], s['positive_increment'], s['negative_increment'], repair=repair_conversion)
    if not valid:
        result = dict(label=label, factor=factor, success=False, reason=reason, **conversion_metadata)
        write_json(output/(stem+'_summary.json'), result)
        return result
    required = ('thermal_inventory', 'balanced_radiation_inventory', 'receiver_thermal_energy',
                'receiver_reference_energy', 'receiver_rated_capacity', 'reference_fluid_density',
                'receiver_fixed_containment_energy', 'D', 'thermal_return_rest')
    for key in required:
        if key not in s:
            raise ValueError('missing complete counted thermal state: '+key)
    if not (meta.get('common_phase_across_pair') and meta.get('existing_fluid_thermal_state_reallocated')
            and meta.get('existing_receiver_heat_reallocated')):
        raise ValueError('common phase and existing fluid/receiver credits required')
    coherence = max(float(np.ptp(a, axis=1).max()) for a in
                    (s['amplitude'], positive_applied, negative_applied))
    conversion = conversion_metadata['conversion_identity_residual']
    if coherence > 1e-10 or conversion > 1e-8:
        raise ValueError(f'incoherent phase or inconsistent conversion: {coherence}, {conversion}')
    oldt, oldx = s['t'], s['x']
    t = np.r_[(oldt[:-1, None]+np.diff(oldt)[:, None]*np.arange(factor)/factor).ravel(), oldt[-1]]
    edges = np.linspace(s['edges'][0], s['edges'][-1], len(oldx)*factor+1)
    x = (edges[:-1]+edges[1:])/2
    nx = len(x)
    h = DenseHistory('routed_family', ROOT/meta['input'])
    model = h.h.reference.h.model
    g = geometry(model, t, x)
    controls = {key: spatial_history(oldx, s[key], x) for key in
                ('amplitude', 'thermal_inventory', 'receiver_thermal_energy')}
    phase, unused = linear_history(oldt, controls['amplitude'], t)
    K, unused = linear_history(oldt, controls['thermal_inventory'], t)
    Z, unused = linear_history(oldt, controls['receiver_thermal_energy'], t)
    initial = spatial_history(oldx, s['balanced_radiation_inventory'][0], x)
    baseline = h.h.reference.h.state
    ref = h.h.reference
    receiver_state = h.h.state
    old_fluid = bilinear(baseline['t'], baseline['x'], baseline['thermal'], oldt, oldx)[0]/s['D']
    old_receiver = bilinear(ref.t, ref.x, receiver_state['heat'], oldt, oldx)[0]
    old_capacity = np.interp(oldx, ref.x, receiver_state['heat_cap'])
    reference_errors = dict(fluid_density=float(abs(old_fluid-s['reference_fluid_density']).max()),
        receiver_energy=float(abs(old_receiver-s['receiver_reference_energy']).max()),
        receiver_capacity=float(abs(old_capacity-s['receiver_rated_capacity']).max()),
        receiver_containment=float(abs(old_capacity/3-s['receiver_fixed_containment_energy']).max()))
    if max(reference_errors.values()) > 1e-10:
        raise ValueError('archived fluid/receiver reference differs from registered assembly: '+str(reference_errors))
    knots = np.unique(np.r_[oldt, baseline['t'], ref.t])
    number = np.interp(x, baseline['x'], baseline['number'])
    turnover = meta.get('receiver_donor_turnover')
    reconstruction = dict(continuous_contact_reconstruction_requested=reconstruct_contacts,
                          bank_counter_contact_reconstruction=bank_mode,
                          continuous_contact_reconstruction_applied=False)
    reconstruction_output = {}
    linear_receiver = Z.copy()
    if reconstruct_contacts:
        if turnover is None or not np.isfinite(turnover) or turnover <= 0:
            raise ValueError('continuous contact reconstruction requires a positive archived turnover')
        for key in ('receiver_hot_energy', 'receiver_hot_contact_panel_heat', 'receiver_cold_contact_panel_heat'):
            if key not in s:
                raise ValueError('continuous reconstruction requires split receiver field '+key)
        unused_hot, unused_cold, source_valid, source_correction = nonnegative_contact_totals(
            s['receiver_hot_contact_panel_heat'], s['receiver_cold_contact_panel_heat'])
        reconstruction['contact_original_source_grid_minima'] = source_correction['contact_original_parent_minima']
        raw_hot = spatial_history(oldx, s['receiver_hot_contact_panel_heat'], x)
        raw_cold = spatial_history(oldx, s['receiver_cold_contact_panel_heat'], x)
        parent_hot, parent_cold, valid, correction = nonnegative_contact_totals(raw_hot, raw_cold)
        reconstruction.update(correction)
        if not valid or not source_valid:
            result = dict(label=label, factor=factor, success=False,
                reason='negative parent contact exceeds 1e-10 allowance; source controls retained',
                **conversion_metadata, **reconstruction)
            write_json(output/(stem+'_summary.json'), result)
            return result
        parent_duration = integrate_panels(oldt, knots,
            lambda at: geometry(model, at, x)['lapse'], order=8)
        hot_rate, cold_rate = parent_hot/parent_duration, parent_cold/parent_duration
        linear_hot = linear_history(oldt, spatial_history(oldx, s['receiver_hot_energy'], x), t)[0]
        initial_hot, initial_cold = linear_hot[0], linear_receiver[0]-linear_hot[0]
        reconstruction_output.update(contact_control_time=oldt, contact_control_position=x,
            original_hot_parent_heat=raw_hot, original_cold_parent_heat=raw_cold,
            applied_hot_parent_heat=parent_hot, applied_cold_parent_heat=parent_cold,
            applied_hot_parent_proper_rate=hot_rate, applied_cold_parent_proper_rate=cold_rate,
            contact_parent_proper_duration=parent_duration)

    def integrand(at):
        c = geometry(model, at, x)
        At = linear_history(oldt, controls['amplitude'], at)[1]
        Kt = linear_history(oldt, controls['thermal_inventory'], at)[1]
        Zt = linear_history(oldt, controls['receiver_thermal_energy'], at)[1]
        U0, U0t, unused = bilinear(baseline['t'], baseline['x'], baseline['thermal'], at, x)
        Z0t = bilinear(ref.t, ref.x, receiver_state['heat'], at, x)[1]
        Ft = bilinear(baseline['t'], baseline['x'], baseline['flux_energy'], at, x)[1]
        # Original capacitor converters use the registered efficiency .98.
        loss = c['ell']/c['radius']**2*((1/.98-1)*np.maximum(Ft, 0)
                                      +(1-.98)*np.maximum(-Ft, 0))
        extra = []
        if reconstruct_contacts:
            owner = np.clip(np.searchsorted(oldt, at, side='right')-1, 0, len(oldt)-2)
            hot_source, cold_source = c['lapse']*hot_rate[owner], c['lapse']*cold_rate[owner]
            revised_Zt = loss-hot_source+cold_source
            extra = [c['ell']*(revised_Zt-Zt), hot_source, cold_source]
            Zt = revised_Zt
            if bank_mode:
                original_source = U0t+U0*c['logD_t']/3+Z0t
                fluid_net = Kt/c['D']**(1/3)-(original_source-loss)
                fluid_hot, fluid_cold = np.maximum(fluid_net, 0.), np.maximum(-fluid_net, 0.)
                extra += [fluid_hot, fluid_cold,
                    np.maximum(fluid_hot-hot_source, 0.),
                    np.maximum(fluid_cold-cold_source, 0.),
                    original_source-Kt/c['D']**(1/3)-Zt]
        return np.array([c['ell']**2*At, c['M']/c['D']**(4/3)*Kt,
            c['ell']*Zt, c['ell']*(U0t+U0*c['logD_t']/3+Z0t), loss, c['lapse'], *extra])

    panels = integrate_panels(t, knots, integrand, order=8)
    comparison = integrate_panels(t, knots, integrand, order=4)
    V = reconstruct_inventory(initial, *panels[:4])
    V4 = reconstruct_inventory(initial, *comparison[:4])
    if reconstruct_contacts:
        qhot, qcold = panels[7:9]
        H = np.vstack([initial_hot, initial_hot+np.cumsum(panels[4]-qhot, axis=0)])
        cold = np.vstack([initial_cold, initial_cold+np.cumsum(qcold, axis=0)])
        actual_fluid_cold = panels[10] if bank_mode else None
        dh, dc, dk = contact_preparation(H, cold, K, g['D'], qhot, qcold, panels[5], number,
            turnover=turnover, temperature_floor=meta.get('retained_uniform_fluid_temperature', 0.),
            fluid_cold_panel=actual_fluid_cold)
        H, cold, K = H+dh, cold+dc, K+dk
        Z = H+cold
        reconstruction.update(continuous_contact_reconstruction_applied=True,
            continuous_contact_method='parent hot/cold heat totals distributed uniformly in proper time; H_t=Lcoord-N*qh, C_t=N*qc; constant nonnegative prepared H,C,K increments cover sampled donor and temperature bounds',
            maximum_added_hot_inventory=float(dh.max()), maximum_added_cold_inventory=float(dc.max()),
            maximum_added_thermal_inventory=float(dk.max()),
            maximum_added_receiver_density=float(((dh+dc)/g['D']).max()),
            maximum_added_fluid_density=float((dk/g['D']**(4/3)).max()),
            maximum_receiver_history_change=float(abs(Z-linear_receiver).max()),
            maximum_hot_history_change=float(abs(H-linear_hot).max()),
            hot_parent_heat_reconstruction_residual=float(abs(qhot.reshape(len(oldt)-1,factor,nx).sum(axis=1)-parent_hot).max()),
            cold_parent_heat_reconstruction_residual=float(abs(qcold.reshape(len(oldt)-1,factor,nx).sum(axis=1)-parent_cold).max()),
            maximum_receiver_energy_source_panel_change=float(abs(panels[6]).max()),
            maximum_receiver_source_change_cumulative=float(abs(np.cumsum(panels[6], axis=0)).max()))
        if bank_mode:
            fluid_hot, fluid_cold = panels[9:11]
            photon_hot, photon_cold = qhot-fluid_hot, qcold-fluid_cold
            reconstruction.update(
                continuous_contact_method='parent bank rates constant in proper time; actual fluid nonadiabatic heat after retained support is split into positive and negative parts; remaining counted bank traffic supplies photons; prepared H,C,K offsets cover actual donor and temperature bounds',
                bank_fluid_partition='minimum fluid circulation at each quadrature sample; symmetric residual bank traffic passes through photons',
                bank_photon_donor_law_supplied=False,
                bank_hot_partition_identity_residual=float(abs(photon_hot+fluid_hot-qhot).max()),
                bank_cold_partition_identity_residual=float(abs(photon_cold+fluid_cold-qcold).max()),
                bank_counter_panel_power_identity_residual=float(abs(photon_hot-photon_cold-panels[13]).max()),
                bank_integrated_direction_violation=float(np.max(np.sum(panels[11]+panels[12], axis=0))),
                bank_panel_direction_violation=max(positive_max(-photon_hot),positive_max(-photon_cold)))
            reconstruction_output.update(bank_fluid_hot_panel_heat=fluid_hot,
                bank_fluid_cold_panel_heat=fluid_cold,bank_photon_hot_panel_heat=photon_hot,
                bank_photon_cold_panel_heat=photon_cold,bank_counter_panel_energy=panels[13],
                bank_hot_direction_deficit_panel=panels[11],bank_cold_direction_deficit_panel=panels[12])
        reconstruction_output.update(additional_prepared_hot_inventory=dh,
            additional_prepared_cold_inventory=dc, additional_prepared_thermal_inventory=dk,
            receiver_history_change=Z-linear_receiver, hot_history_change=H-linear_hot,
            receiver_energy_source_panel_change=panels[6])
    # Independent explicit waves. Every control breakpoint remains a time node.
    geom = [model.metric(float(now), x) for now in t]
    edgegeom = [model.metric(float(now), edges) for now in t]
    tables = {sign: dict(faces=np.array([-gg.beta+sign*gg.alpha/gg.b for gg in edgegeom]),
        gain=np.array([gg.alpha*gg.k_l-sign*gg.alpha_x/gg.b for gg in geom]),
        source=g['b']/(1-sign*g['v'])) for sign in (-1, 1)}
    eta = meta['efficiency']
    beam = {name: np.zeros_like(V) for name in ('incident', 'useful', 'heat')}
    ledger_rows = []
    # Interpolate the applied sources with the same spatial rule as A; this
    # retains DeltaA=p-m even for permitted roundoff-level spatial differences.
    plus = spatial_history(oldx, positive_applied, x)/np.diff(oldt)[:, None]
    minus = spatial_history(oldx, negative_applied, x)/np.diff(oldt)[:, None]
    for half, direction in enumerate((-1, 1)):
        sl = slice(half*nx//2, (half+1)*nx//2)
        for name, sign, rates, back in (
                ('incident', direction, plus[:, sl]/eta, True),
                ('useful', -direction, eta*minus[:, sl], False),
                ('heat', -direction, (1/eta-1)*plus[:, sl]+(1-eta)*minus[:, sl], False)):
            tab = tables[sign]
            faces = tab['faces'][:, half*nx//2:(half+1)*nx//2+1]
            def coefficients(now, interval):
                fraction = (now-t[interval])/(t[interval+1]-t[interval])
                interp = lambda a: (1-fraction)*a[interval]+fraction*a[interval+1]
                original = min(interval//factor, len(oldt)-2)
                return interp(faces), interp(tab['gain'][:, sl]), interp(tab['source'][:, sl])*rates[original]
            states, ledger = propagate(t, edges[half*nx//2:(half+1)*nx//2+1], coefficients, backwards=back)
            beam[name][:, sl] = states*g['gamma'][:, sl]**2*(1-sign*g['v'][:, sl])**2/(g['b'][:, sl]*g['radius'][:, sl]**2)
            for row in ledger:
                row.update(stream=name, side=half)
            ledger_rows.extend(ledger)
    U0 = bilinear(baseline['t'], baseline['x'], baseline['thermal'], t, x)[0]
    Z0 = bilinear(ref.t, ref.x, receiver_state['heat'], t, x)[0]
    rho = h.energy(x).evaluate(t)[0]/g['D']
    p = h.pressure(t, x)[0]
    q = h.coefficients(t, x)['Q']/g['D']
    available = np.array([rho+(U0+Z0)/g['D'], p+U0/(3*g['D']), q+U0/(3*g['D'])])
    B, W, core = K/g['D']**(4/3), V/g['M'], phase/g['radius']**2
    wall = 2*meta['interface_sigma']/(g['ell']*(edges[-1]-edges[0])/2)
    returned = beam['useful']+beam['heat']
    drift = meta.get('guide_drift_bound', meta.get('guide_drift'))
    multiplier = 0. if drift is None else .5*(drift**-2-1)
    deficit, guide, floor = full_budget(*available, phase=core, radiation=W, thermal=B,
        receiver=Z/g['D'], wall=wall, incident=beam['incident'], returned=returned,
        guide_multiplier=multiplier)
    reserve = meta.get('reserved_density_fraction', 0.)*rho
    preparation = dict(additional_radiation_preparation_requested=prepare_radiation,
                       additional_radiation_preparation_applied=False)
    prepared_extra = np.zeros(nx)
    if prepare_radiation:
        lower, upper, fixed_violation, possible = preparation_interval(*available,
            phase=core, radiation=W, thermal=B, receiver=Z/g['D'], wall=wall,
            incident=beam['incident'], returned=returned, guide_multiplier=multiplier,
            metric_weight=g['M'])
        preparation.update(preparation_interval_nonempty=possible,
            preparation_fixed_facet_violation=fixed_violation,
            preparation_minimum_interval_width=float((upper-lower).min()),
            before_preparation_density_shortfall=positive_max(deficit),
            before_preparation_wave_floor_violation=positive_max(floor))
        if possible:
            prepared_extra=lower
            V=V+prepared_extra
            V4=V4+prepared_extra
            W=V/g['M']
            deficit, guide, floor = full_budget(*available, phase=core, radiation=W,
                thermal=B, receiver=Z/g['D'], wall=wall, incident=beam['incident'],
                returned=returned, guide_multiplier=multiplier)
            preparation.update(additional_radiation_preparation_applied=True,
                maximum_added_prepared_inventory=float(prepared_extra.max()),
                maximum_added_radiation_density=float((prepared_extra/g['M']).max()))
    reserved_deficit = deficit+reserve
    direction = np.r_[-np.ones(nx//2), np.ones(nx//2)]
    wave = beam['incident']+returned
    current = direction*(beam['incident']-returned)
    counter = W-wave
    cap = spatial_history(oldx, s['receiver_rated_capacity'], x)
    original_cap = np.interp(x, ref.x, receiver_state['heat_cap'])
    # The registered local rating bounds the actual inventory. Spatially
    # extending a coarse allowance is reported separately; an unused excess
    # allowance consumes no heat capacity or additional wall energy.
    capacity = max(positive_max(-Z), positive_max(Z-original_cap))
    loss, duration = panels[4:6]
    contact = qhot-qcold if reconstruct_contacts else loss-np.diff(Z, axis=0)
    fluid_energy = K/g['D']**(1/3)
    fluid_temperature = fluid_energy/(3*number)
    if 'receiver_hot_energy' in s and turnover is None:
        raise ValueError('split receiver archive must identify its donor turnover')
    contact_output = dict(receiver_total_contact_panel_heat=contact,
        receiver_converter_loss_panel=loss, receiver_contact_proper_duration=duration)
    diagnostics = dict(receiver_capacity_violation=capacity,
        receiver_capacity_interpolation_difference=float(abs(cap-original_cap).max()),
        receiver_contact_subtraction_identity=float(abs(contact-(loss-np.diff(Z, axis=0))).max()))
    if 'receiver_hot_energy' in s:
        if not reconstruct_contacts:
            H = linear_history(oldt, spatial_history(oldx, s['receiver_hot_energy'], x), t)[0]
            cold = Z-H
            qhot, qcold = loss-np.diff(H, axis=0), np.diff(cold, axis=0)
        diagnostics.update(split_direction_violation=max(positive_max(-qhot), positive_max(-qcold)),
            split_state_positivity_violation=max(positive_max(-H), positive_max(-cold)),
            split_fixed_rating_violation=positive_max(H.max(axis=0)+cold.max(axis=0)-original_cap),
            split_contact_identity=float(abs(qhot-qcold-contact).max()),
            hot_contact_subtraction_identity=float(abs(qhot-(loss-np.diff(H, axis=0))).max()),
            cold_contact_subtraction_identity=float(abs(qcold-np.diff(cold, axis=0)).max()))
        contact_output.update(receiver_hot_energy=H, receiver_cold_energy=cold,
            receiver_hot_contact_panel_heat=qhot, receiver_cold_contact_panel_heat=qcold)
        if turnover is not None:
            rate = turnover*duration
            fluid_cold = panels[10] if bank_mode else qcold
            diagnostics['split_donor_violation'] = max(positive_max(qhot-rate*H[:-1]),
                positive_max(qhot-rate*H[1:]), positive_max(fluid_cold-rate*fluid_energy[:-1]),
                positive_max(fluid_cold-rate*fluid_energy[1:]))
    if turnover is not None:
        rate = turnover*duration
        diagnostics['receiver_donor_violation'] = max(positive_max(contact-rate*Z[:-1]),
            positive_max(contact-rate*Z[1:]),
            0. if bank_mode else positive_max(-contact-rate*fluid_energy[:-1]),
            0. if bank_mode else positive_max(-contact-rate*fluid_energy[1:]))
    i, j = np.unravel_index(np.argmax(deficit), deficit.shape)
    negative = max(positive_max(-core), positive_max(-B), positive_max(-Z/g['D']), positive_max(-W))
    tolerance = 2e-7
    thermal_floor_error = positive_max(meta.get('retained_uniform_fluid_temperature', 0.)-fluid_temperature)
    floor_pass = thermal_floor_error <= tolerance
    contact_pass = bool(max(value for key, value in diagnostics.items()
                           if key.endswith('violation')) <= tolerance)
    if bank_mode:
        contact_pass = bool(contact_pass and max(reconstruction['bank_integrated_direction_violation'],
            reconstruction['bank_panel_direction_violation']) <= tolerance)
    full_pass = bool(max(float(deficit.max()), float(floor.max()), negative) <= tolerance)
    reserve_pass = bool(max(float(reserved_deficit.max()), float(floor.max()), negative) <= tolerance)
    result = dict(label=label, factor=factor, success=True, time_samples=len(t), spatial_samples=nx,
        input=meta['input'], controls_source=str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source),
        efficiency=eta, interface_sigma=meta['interface_sigma'], guide_drift_bound=drift,
        full_density_budget_passes=full_pass, reserved_density_budget_passes=reserve_pass,
        receiver_contact_checks_pass=contact_pass, fluid_temperature_floor_passes=floor_pass,
        full_sampled_gate_passes=full_pass and contact_pass and floor_pass,
        maximum_density_shortfall=positive_max(deficit), minimum_density_margin=float(-deficit.max()),
        maximum_reserved_density_shortfall=positive_max(reserved_deficit),
        maximum_wave_floor_violation=positive_max(floor), minimum_counterstream_margin=float((counter-abs(current)).min()),
        inventory_positivity_violation=negative, common_phase_spread=coherence,
        **conversion_metadata,
        gauss4_8_panel_difference=float(abs(panels-comparison).max()),
        gauss4_8_radiation_density_difference=float((abs(V-V4)/g['M']).max()),
        aggregate_panel_balance_residual=float(abs(np.diff(V, axis=0)+panels[0]+panels[1]+panels[2]-panels[3]).max()),
        maximum_explicit_wave_balance_residual=max(abs(row['balance_residual']) for row in ledger_rows),
        receiver_contact_turnover_bound=turnover, original_converter_efficiency=.98,
        source_reference_reconstruction_errors=reference_errors,
        minimum_fluid_temperature=float(fluid_temperature.min()),
        archived_uniform_fluid_temperature_floor=meta.get('retained_uniform_fluid_temperature'),
        uniform_fluid_temperature_floor_violation=thermal_floor_error,
        receiver_donor_scope=('hot-bank and actual minimum fluid-cold endpoint comparisons; photon donor law remains separate'
                              if bank_mode else 'endpoint donor-energy comparison on each replay panel'),
        baseline_power_and_full_stress_credits_retained=True, full_balanced_radiation_inventory_retained=True,
        aggregate_energy_integrated=True, beam_transport_independently_replayed=True,
        counterstream_opacity_and_force_supplied=False, thermal_constitutive_law_supplied=False,
        scope='archived phase and fluid-shape controls with explicitly recorded conversion, contact and prepared-inventory adjustments when requested; exact registered metric energy quadrature and explicit beam replay; sampled tensor and contact checks',
        spatial_extension='linear separately in each cell, constant from outermost sample to cell edge',
        **preparation, **reconstruction,
        worst_density_sample=dict(time=float(t[i]), x=float(x[j]), original_density=float(rho[i,j]),
            phase_density=float(core[i,j]), radiation_density=float(W[i,j]), thermal_density=float(B[i,j]),
            receiver_density=float(Z[i,j]/g['D'][i,j])), elapsed_seconds=time.monotonic()-started, **diagnostics)
    result.update(replay_integrity(result))
    result['full_sampled_gate_passes'] = bool(result['full_sampled_gate_passes']
        and result['numerical_integrity_checks_pass'])
    write_json(output/(stem+'_summary.json'), result)
    write_json(output/(stem+'_wave_ledger.json'), ledger_rows)
    np.savez_compressed(output/(stem+'_states.npz'), t=t, x=x, edges=edges,
        control_time=oldt, control_position=oldx, control_amplitude=s['amplitude'],
        applied_positive_increment=positive_applied, applied_negative_increment=negative_applied,
        amplitude=phase, radius=g['radius'], ell=g['ell'], D=g['D'], lapse=g['lapse'],
        target=np.array([rho, p, q]), credited_target=available,
        thermal_inventory=K, thermal_reservoir_rest=B, receiver_thermal_energy=Z,
        receiver_rest=Z/g['D'], receiver_reference_energy=Z0, reference_fluid_density=U0/g['D'],
        receiver_rated_capacity=original_cap, receiver_fixed_containment_energy=original_cap/3,
        fluid_particle_number=number, fluid_temperature=fluid_temperature,
        balanced_radiation_inventory=V, balanced_radiation_rest=W, counterstream_rest=counter,
        counterstream_current=-current, absorption_rest=beam['incident'], work_return_rest=beam['useful'],
        heat_return_rest=beam['heat'], density_shortfall=deficit, reserved_density_shortfall=reserved_deficit,
        wave_floor_violation=floor, guide_rest=guide, wall_rest=wall,
        phase_energy_panel=panels[0], thermal_energy_panel=panels[1], receiver_energy_panel=panels[2],
        baseline_energy_panel=panels[3], gauss4_8_panel_difference=panels-comparison,
        additional_prepared_radiation_inventory=prepared_extra, **reconstruction_output, **contact_output)
    print(stem+': '+json.dumps({key: result[key] for key in ('full_sampled_gate_passes', 'full_density_budget_passes',
        'maximum_density_shortfall', 'maximum_wave_floor_violation', 'elapsed_seconds')}), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--labels', nargs='+')
    parser.add_argument('--factors', type=int, nargs='+', default=[2])
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--output-name', required=True)
    parser.add_argument('--prepare-radiation', action='store_true',
                        help='add only counted initial radiation within its sampled full-density interval')
    parser.add_argument('--repair-conversion-roundoff', action='store_true',
                        help='preserve phase and positive overlap while repairing increments by at most 1e-8')
    parser.add_argument('--reconstruct-contacts', action='store_true',
                        help='reconstruct positive proper-time heat rates and count required prepared donor inventory')
    args = parser.parse_args()
    if not 1 <= args.workers <= 2 or any(f < 1 for f in args.factors):
        parser.error('one or two workers and positive refinement factors required')
    source, output = BASE/args.source, BASE/args.output_name
    if output.exists():
        raise RuntimeError('preserve completed thermal replay')
    labels = args.labels or [p.stem.removesuffix('_states') for p in sorted(source.glob('*_states.npz'))]
    if not labels:
        raise ValueError('completed controls required')
    hashes, historical = validate_controls(source, labels)
    sources = [Path(__file__), Path(__file__).with_name('audit_virtual_cell_ports.py'),
        Path(__file__).with_name('audit_joint_dense_work.py'), Path(__file__).with_name('audit_joint_support.py'),
        ROOT/'toolkit/adm_harness_cli/adm_harness/poynting_delivery.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/active_transfer_reservoir.py',
        ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_thermal_replay.py']
    # DenseHistory imports the registered assembly through several local
    # modules. Pin their current runtime bytes as well as the inherited record.
    for module in list(sys.modules.values()):
        filename = getattr(module, '__file__', None)
        if filename:
            path = Path(filename).resolve()
            if path.suffix == '.py' and path.is_relative_to(ROOT):
                sources.append(path)
    for path in sources:
        hashes[str(path.relative_to(ROOT))] = sha256_file(path)
    output.mkdir()
    specs = [(str(source), label, factor, str(output), args.prepare_radiation,
              args.repair_conversion_roundoff, args.reconstruct_contacts)
             for label in labels for factor in args.factors]
    with ProcessPoolExecutor(max_workers=min(args.workers, len(specs)),
            mp_context=multiprocessing.get_context('spawn')) as pool:
        cases = list(pool.map(audit, specs))
    for relative, expected in hashes.items():
        if sha256_file(ROOT/relative) != expected:
            raise RuntimeError('runtime input changed during replay: '+relative)
    write_json(output/'summary.json', dict(cases=cases))
    write_json(output/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        workers=min(args.workers, len(specs)), input_sha256=hashes, historical_source=historical,
        output_sha256={p.name: sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
