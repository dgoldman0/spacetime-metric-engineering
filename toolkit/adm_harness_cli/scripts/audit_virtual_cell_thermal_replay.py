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


def audit(spec):
    source, label, factor, output, *options = spec
    prepare_radiation = bool(options[0]) if options else False
    started = time.monotonic()
    source, output = Path(source), Path(output)
    meta = json.loads((source/(label+'_summary.json')).read_text())
    with np.load(source/(label+'_states.npz')) as f:
        s = {key: f[key] for key in f.files}
    stem = label+f'_factor{factor}'
    minima = {key: float(s[key].min()) for key in ('positive_increment', 'negative_increment')}
    if min(minima.values()) < 0:
        result = dict(label=label, factor=factor, success=False,
            reason='negative archived conversion increment; controls were left unchanged',
            conversion_increment_minima=minima, conversion_increments_clipped=False)
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
    coherence = max(float(np.ptp(s[key], axis=1).max()) for key in
                    ('amplitude', 'positive_increment', 'negative_increment'))
    conversion = float(abs(np.diff(s['amplitude'], axis=0)-s['positive_increment']
                           +s['negative_increment']).max())
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
        return np.array([c['ell']**2*At, c['M']/c['D']**(4/3)*Kt,
            c['ell']*Zt, c['ell']*(U0t+U0*c['logD_t']/3+Z0t), loss, c['lapse']])

    panels = integrate_panels(t, knots, integrand, order=8)
    comparison = integrate_panels(t, knots, integrand, order=4)
    V = reconstruct_inventory(initial, *panels[:4])
    V4 = reconstruct_inventory(initial, *comparison[:4])
    # Independent explicit waves. Every control breakpoint remains a time node.
    geom = [model.metric(float(now), x) for now in t]
    edgegeom = [model.metric(float(now), edges) for now in t]
    tables = {sign: dict(faces=np.array([-gg.beta+sign*gg.alpha/gg.b for gg in edgegeom]),
        gain=np.array([gg.alpha*gg.k_l-sign*gg.alpha_x/gg.b for gg in geom]),
        source=g['b']/(1-sign*g['v'])) for sign in (-1, 1)}
    eta = meta['efficiency']
    beam = {name: np.zeros_like(V) for name in ('incident', 'useful', 'heat')}
    ledger_rows = []
    for half, direction in enumerate((-1, 1)):
        sl = slice(half*nx//2, (half+1)*nx//2)
        plus = s['positive_increment'].mean(axis=1)/np.diff(oldt)
        minus = s['negative_increment'].mean(axis=1)/np.diff(oldt)
        for name, sign, rates, back in (
                ('incident', direction, plus/eta, True),
                ('useful', -direction, eta*minus, False),
                ('heat', -direction, (1/eta-1)*plus+(1-eta)*minus, False)):
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
    contact = loss-np.diff(Z, axis=0)
    fluid_energy = K/g['D']**(1/3)
    number = np.interp(x, baseline['x'], baseline['number'])
    fluid_temperature = fluid_energy/(3*number)
    turnover = meta.get('receiver_donor_turnover')
    if 'receiver_hot_energy' in s and turnover is None:
        raise ValueError('split receiver archive must identify its donor turnover')
    contact_output = dict(receiver_total_contact_panel_heat=contact,
        receiver_converter_loss_panel=loss, receiver_contact_proper_duration=duration)
    diagnostics = dict(receiver_capacity_violation=capacity,
        receiver_capacity_interpolation_difference=float(abs(cap-original_cap).max()))
    if 'receiver_hot_energy' in s:
        H = linear_history(oldt, spatial_history(oldx, s['receiver_hot_energy'], x), t)[0]
        cold = Z-H
        qhot, qcold = loss-np.diff(H, axis=0), np.diff(cold, axis=0)
        diagnostics.update(split_direction_violation=max(positive_max(-qhot), positive_max(-qcold)),
            split_state_positivity_violation=max(positive_max(-H), positive_max(-cold)),
            split_fixed_rating_violation=positive_max(H.max(axis=0)+cold.max(axis=0)-original_cap),
            split_contact_identity=float(abs(qhot-qcold-contact).max()))
        contact_output.update(receiver_hot_energy=H, receiver_cold_energy=cold,
            receiver_hot_contact_panel_heat=qhot, receiver_cold_contact_panel_heat=qcold)
        if turnover is not None:
            rate = turnover*duration
            diagnostics['split_donor_violation'] = max(positive_max(qhot-rate*H[:-1]),
                positive_max(qhot-rate*H[1:]), positive_max(qcold-rate*fluid_energy[:-1]),
                positive_max(qcold-rate*fluid_energy[1:]))
    if turnover is not None:
        rate = turnover*duration
        diagnostics['receiver_donor_violation'] = max(positive_max(contact-rate*Z[:-1]),
            positive_max(contact-rate*Z[1:]), positive_max(-contact-rate*fluid_energy[:-1]),
            positive_max(-contact-rate*fluid_energy[1:]))
    i, j = np.unravel_index(np.argmax(deficit), deficit.shape)
    negative = max(positive_max(-core), positive_max(-B), positive_max(-Z/g['D']), positive_max(-W))
    tolerance = 2e-7
    thermal_floor_error = positive_max(meta.get('retained_uniform_fluid_temperature', 0.)-fluid_temperature)
    floor_pass = thermal_floor_error <= tolerance
    contact_pass = bool(max(value for key, value in diagnostics.items()
                           if key.endswith('violation')) <= tolerance)
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
        inventory_positivity_violation=negative, conversion_increment_minima=minima,
        conversion_increments_clipped=False, common_phase_spread=coherence, conversion_identity_residual=conversion,
        gauss4_8_panel_difference=float(abs(panels-comparison).max()),
        gauss4_8_radiation_density_difference=float((abs(V-V4)/g['M']).max()),
        aggregate_panel_balance_residual=float(abs(np.diff(V, axis=0)+panels[0]+panels[1]+panels[2]-panels[3]).max()),
        maximum_explicit_wave_balance_residual=max(abs(row['balance_residual']) for row in ledger_rows),
        receiver_contact_turnover_bound=turnover, original_converter_efficiency=.98,
        source_reference_reconstruction_errors=reference_errors,
        minimum_fluid_temperature=float(fluid_temperature.min()),
        archived_uniform_fluid_temperature_floor=meta.get('retained_uniform_fluid_temperature'),
        uniform_fluid_temperature_floor_violation=thermal_floor_error,
        receiver_donor_scope='endpoint donor-energy comparison on each replay panel',
        baseline_power_and_full_stress_credits_retained=True, full_balanced_radiation_inventory_retained=True,
        aggregate_energy_integrated=True, beam_transport_independently_replayed=True,
        counterstream_opacity_and_force_supplied=False, thermal_constitutive_law_supplied=False,
        scope='archived phase/fluid/receiver controls, explicitly recorded initial-radiation adjustment when requested; exact registered metric energy quadrature and explicit beam replay; sampled tensor and contact checks',
        spatial_extension='linear separately in each cell, constant from outermost sample to cell edge',
        **preparation,
        worst_density_sample=dict(time=float(t[i]), x=float(x[j]), original_density=float(rho[i,j]),
            phase_density=float(core[i,j]), radiation_density=float(W[i,j]), thermal_density=float(B[i,j]),
            receiver_density=float(Z[i,j]/g['D'][i,j])), elapsed_seconds=time.monotonic()-started, **diagnostics)
    write_json(output/(stem+'_summary.json'), result)
    write_json(output/(stem+'_wave_ledger.json'), ledger_rows)
    np.savez_compressed(output/(stem+'_states.npz'), t=t, x=x, edges=edges,
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
        additional_prepared_radiation_inventory=prepared_extra, **contact_output)
    print(stem+': '+json.dumps({key: result[key] for key in ('full_density_budget_passes',
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
    specs = [(str(source), label, factor, str(output), args.prepare_radiation)
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
