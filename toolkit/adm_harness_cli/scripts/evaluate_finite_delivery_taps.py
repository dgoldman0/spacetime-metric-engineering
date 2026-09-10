#!/usr/bin/env python3
"""Finite tap opacity using a counted transparent carrier and paired return."""
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess

import numpy as np
import pandas as pd

from adm_harness.poynting_delivery import transport_rhs, wave_moments
from adm_harness.pressure_linked_storage import fluid_coefficients, fluid_moments
from adm_harness.regenerative_converter import compact_cell_moments
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.shared_field_delivery import electric_share_cap, smooth_under_cap, radial_field_moments
from adm_harness.source_ledger import sha256_file
from run_poynting_delivery import DeliveryHistory, BASE, ROOT, INPUT, write_json

OUTPUT = BASE/'poynting_delivery/finite_taps'


def transparent_wave(h, direction, initial, boundary):
    """Conservative free wave with a supplied incident boundary value of D.

The input boundary carries the same Doppler and coordinate-worldtube factors
as the work route. The scalar reference normalization is arbitrary; its final
amplitude is fixed by the required finite tap absorption rate.
"""
    t, x = h.t, h.x
    dx = h.edges[1]-h.edges[0]
    state = np.asarray(initial).copy()
    result = np.zeros((len(t), len(x)))
    result[0] = state
    records = []
    for i, duration in enumerate(np.diff(t)):
        rate = 0.
        for tt in (t[i], (t[i]+t[i+1])/2, t[i+1]):
            g, edge, unused = h.geometry(float(tt))
            rate = max(rate, abs(-edge.beta+direction*edge.alpha/edge.b).max()/dx
                       +abs(g.alpha*g.k_l-direction*g.alpha_x/g.b).max())
        count = max(1, int(np.ceil(duration*rate/.35)))
        step = duration/count
        ledger = np.zeros(4)
        before = dx*state.sum()

        def rhs(y, tt):
            g, edge, unused = h.geometry(float(tt))
            velocity = -edge.beta+direction*edge.alpha/edge.b
            gain = g.alpha*g.k_l-direction*g.alpha_x/g.b
            derivative, terms = transport_rhs(y, velocity, gain, np.zeros_like(x), dx)
            side = 0 if direction == 1 else -1
            incident = abs(velocity[side])*boundary(tt)
            derivative[side] += incident/dx
            outgoing = -terms[0]
            return derivative, np.array([incident, outgoing, terms[1], incident-outgoing+terms[1]])

        for k in range(count):
            now = t[i]+k*step
            d1, l1 = rhs(state, now)
            trial = state+step*d1
            d2, l2 = rhs(trial, now+step)
            state = .5*(state+trial+step*d2)
            if state.min() < -1e-12:
                raise ArithmeticError('transparent wave lost positivity')
            ledger += .5*step*(l1+l2)
        result[i+1] = state
        records.append(dict(interval=i, incoming=float(ledger[0]), outgoing=float(ledger[1]),
            geometric=float(ledger[2]), balance_residual=float(dx*state.sum()-before-ledger[3])))
    return result, records


def evaluate(cells):
    h = DeliveryHistory(cells)
    x, t = h.x, h.t
    dx = h.edges[1]-h.edges[0]
    c = fluid_coefficients(h.model, t, x)
    volume = c['b']*c['radius']**2
    integrate = lambda a: 4*np.pi*dx*np.sum(a, axis=-1)
    z = np.load(BASE/f'poynting_delivery/spatial_refinement/right_n{cells}_t1_states.npz')
    baseline_plus, baseline_minus = z['mu_plus'], z['mu_minus']
    initial = c['b'][0]/c['alpha'][0]**2

    def incident(tt):
        g = h.model.metric(float(tt), h.edges[-1:])
        return float(g.b[0]/g.alpha[0]**2)

    background_D, forward_ledger = transparent_wave(h, -1, initial, incident)
    background_minus = background_D/volume

    def return_boundary(tt):
        # Zero-length ideal bend, returning energy in the local material frame.
        # Finite bend field inventory and its traction are reported separately.
        g = h.model.metric(float(tt), h.edges[:1])
        v = float(g.b[0]*g.beta[0]/g.alpha[0])
        outgoing = float(np.interp(tt, t, background_D[:, 0]))
        return outgoing*((1+v)/(1-v))**2

    return_D, return_ledger = transparent_wave(h, 1, np.zeros_like(x), return_boundary)
    background_plus = return_D/volume
    hf = h.interpolate_state(h.state['flux_energy'])
    check_x = np.unique(np.r_[x, h.state['x']])
    selection = np.searchsorted(check_x, x)
    check_h = np.array([np.interp(check_x, h.state['x'], row) for row in h.state['flux_energy']])
    check_c = fluid_coefficients(h.model, t, check_x)
    cap_check = electric_share_cap(t, check_h, check_c['lapse'])
    supply = fluid_moments(h.interpolate_state(h.state['thermal']), hf, h.spatial(h.state['number'])[0], c)
    thermal = compact_cell_moments(z['heat']+z['heat_capacity']/3, c)
    hd = h.spatial(h.hdot)
    check_hd = np.array([np.interp(check_x, h.state['x'], row) for row in h.hdot])
    interpolate_check = lambda array: np.array([np.interp(check_x, x, row) for row in array])
    base_check = interpolate_check(baseline_minus)
    background_check = interpolate_check(background_minus)
    archived = pd.read_csv(str(INPUT)+'_points.csv')
    cases, phases = [], []
    for opacity in (1., 10., 100.):
        scale = 0.
        for fraction in (0., .25, .5, .75, 1.):
            tt = t[:-1]+fraction*np.diff(t)
            cc = fluid_coefficients(h.model, tt, check_x)
            q = np.maximum(check_hd, 0)/(.98*cc['lapse']*cc['radius']**4)
            doppler2 = cc['gamma']**2*(1+cc['v'])**2
            base = ((1-fraction)*base_check[:-1]+fraction*base_check[1:])*doppler2
            unit = ((1-fraction)*background_check[:-1]+fraction*background_check[1:])*doppler2
            scale = max(scale, float(np.max(np.maximum(q/opacity-base, 0)/unit)))
        scale *= 1.03
        minus = baseline_minus+scale*background_minus
        plus = baseline_plus+scale*background_plus
        flux = 2*1.03*1.5*max(float(np.max(minus*c['gamma']**2*(1+c['v'])**2*c['radius']**4)),
                              float(np.max(plus*c['gamma']**2*(1-c['v'])**2*c['radius']**4)))
        check_share, check_gradient, unused = smooth_under_cap(check_x, np.minimum(flux, cap_check), h.state['x'])
        share, derivative = check_share[selection], check_gradient[selection]
        extra = (flux-share)[None, :]/c['radius']**4
        auxiliary = wave_moments(plus, minus)+thermal+radial_field_moments(extra)
        measured = 0.
        minus_check = interpolate_check(minus)
        for fraction in (0., .25, .5, .75, 1.):
            tt = t[:-1]+fraction*np.diff(t)
            cc = fluid_coefficients(h.model, tt, check_x)
            q = np.maximum(check_hd, 0)/(.98*cc['lapse']*cc['radius']**4)
            mu = ((1-fraction)*minus_check[:-1]+fraction*minus_check[1:])*cc['gamma']**2*(1+cc['v'])**2
            measured = max(measured, float(np.max(q/mu)))
        rest_turn_wave = scale*background_minus[:, 0]*c['gamma'][:, 0]**2*(1+c['v'][:, 0])**2
        turn_wave_force = 2*rest_turn_wave
        from adm_harness.shared_field_delivery import average_electric_rate
        rate = float(average_electric_rate(t, check_h-check_share, check_c['lapse']).max())
        if rate > 1+1e-7 or measured > opacity:
            raise RuntimeError('finite electric or tap response gate failed on union grid')
        result = dict(cells=cells, opacity_ceiling=opacity, maximum_sampled_opacity=measured,
            original_and_transport_check_points=len(check_x), maximum_electric_rate=rate,
            transparent_wave_multiplier=scale, guide_flux_energy=flux,
            initial_extra_travelling_energy=float(integrate(scale*background_D[0])),
            final_extra_travelling_energy=float(integrate(scale*(background_D[-1]+return_D[-1]))),
            extra_incoming_boundary_energy=float(4*np.pi*scale*sum(row['incoming'] for row in forward_ledger)),
            extra_returned_boundary_energy=float(4*np.pi*scale*sum(row['outgoing'] for row in return_ledger)),
            extra_wave_geometric_energy=float(4*np.pi*scale*sum(row['geometric'] for row in forward_ledger+return_ledger)),
            initial_extra_guide_energy=float(integrate(volume[0]*extra[0])),
            initial_auxiliary_slice_energy=float(integrate(volume[0]*auxiliary[0, 0])),
            maximum_ideal_bend_wave_reaction_pressure=float(turn_wave_force.max()),
            peak_bend_power_times_proper_delay_coefficient=float((4*np.pi*c['radius'][:, 0]**2*rest_turn_wave).max()),
            maximum_free_wave_balance_residual=float(max(abs(row['balance_residual']) for row in forward_ledger+return_ledger)))
        cases.append(result)
        for time, frame in archived.groupby('s'):
            it = int(np.argmin(abs(t-time)))
            demand = np.array([np.interp(x, frame.l, frame['geometry_'+key]) for key in ('rho', 'pr', 'j', 'pt')])
            val = maximum_null(supply[:, it]+auxiliary[:, it]-demand)[0]
            phases.append(dict(cells=cells, opacity_ceiling=opacity, s=float(time),
                required_negative_null=float(max(0, val.max())),
                auxiliary_slice_energy=float(integrate(volume[it]*auxiliary[0, it]))))
        if opacity == 100:
            np.savez_compressed(OUTPUT/f'finite_n{cells}_states.npz', t=t, x=x, mu_plus=plus, mu_minus=minus,
                guide_flux=np.full_like(x, flux), shared_flux=share, extra_flux=flux-share)
    write_json(OUTPUT/f'n{cells}_summary.json', dict(cases=cases, phases=phases))
    pd.DataFrame(forward_ledger).to_csv(OUTPUT/f'n{cells}_forward_balance.csv', index=False)
    pd.DataFrame(return_ledger).to_csv(OUTPUT/f'n{cells}_return_balance.csv', index=False)
    print('finite taps', cells, [(r['opacity_ceiling'], round(r['initial_auxiliary_slice_energy'],4)) for r in cases], flush=True)


def main():
    if OUTPUT.exists():
        raise RuntimeError('preserve completed finite-tap evidence')
    files = [Path(__file__), Path(__file__).with_name('run_poynting_delivery.py'),
        ROOT/'toolkit/adm_harness_cli/adm_harness/poynting_delivery.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/shared_field_delivery.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/active_transfer_reservoir.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/pressure_linked_storage.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/graded_electrothermal.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/regenerative_converter.py',
        Path(str(INPUT)+'_states.npz'), Path(str(INPUT)+'_points.csv'),
        BASE/'active_transfer_reservoir/metric_fine.npz', BASE/'active_transfer_reservoir/medium_baseline.npz']
    files += [BASE/f'poynting_delivery/spatial_refinement/right_n{n}_t1_states.npz' for n in (512, 1024)]
    before = {str(p.relative_to(ROOT)): sha256_file(p) for p in files}
    OUTPUT.mkdir(parents=True)
    for cells in (512, 1024):
        evaluate(cells)
    if before != {str(p.relative_to(ROOT)): sha256_file(p) for p in files}:
        raise RuntimeError('input changed during finite-tap test')
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        input_sha256=before,
        output_sha256={p.name: sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
