#!/usr/bin/env python3
"""Parallel work-port efficiency, impedance, and finite-bend controls.

Preserves completed delivery evidence and writes a separate evidence stage.
Reflected amplitudes are guide-margin envelopes, not propagated solutions.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

import numpy as np
import pandas as pd
from scipy.optimize import brentq, minimize_scalar

from adm_harness.finite_work_interface import (
    capacitor_port, capacitor_step_work, port_reflection,
    reflected_guide_factor, toroidal_bend_factors,
)
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.poynting_delivery import wave_moments
from adm_harness.pressure_linked_storage import fluid_coefficients, fluid_moments
from adm_harness.regenerative_converter import compact_cell_moments, proper_prefix
from adm_harness.shared_field_delivery import (
    average_electric_rate, electric_share_cap, radial_field_moments, smooth_under_cap,
)
from adm_harness.source_ledger import sha256_file
from run_poynting_delivery import BASE, ROOT, INPUT, DeliveryHistory, write_json

OUTPUT = BASE/'finite_work_interface'
REFERENCE_STARTUP = 93.9352
REFERENCE_FADE = .262788


class InterfaceHistory:
    def __init__(self, cells):
        self.h = h = DeliveryHistory(cells)
        self.t, self.x = h.t, h.x
        self.dx = h.edges[1]-h.edges[0]
        self.c = c = fluid_coefficients(h.model, h.t, h.x)
        self.volume = c['b']*c['radius']**2
        self.cm = cm = fluid_coefficients(h.model, (h.t[:-1]+h.t[1:])/2, h.x)
        self.hd = h.spatial(h.hdot)
        self.charge = self.hd/(cm['lapse']*cm['radius']**4)
        self.positive = np.maximum(self.charge, 0)
        self.negative = np.maximum(-self.charge, 0)
        with np.load(BASE/f'poynting_delivery/spatial_refinement/right_n{cells}_t1_states.npz') as z:
            self.absorption = z['mu_minus'].copy()
            self.recovery = z['mu_plus'].copy()
            self.old_heat = z['heat'].copy()
            self.old_heat_cap = z['heat_capacity'].copy()
        with np.load(BASE/f'poynting_delivery/finite_taps/finite_n{cells}_states.npz') as z:
            self.free_minus = z['mu_minus']-self.absorption
            self.free_plus = z['mu_plus']-self.recovery
        self.check_x = np.unique(np.r_[h.x, h.state['x']])
        self.selection = np.searchsorted(self.check_x, h.x)
        self.check_h = np.array([np.interp(self.check_x, h.state['x'], row) for row in h.state['flux_energy']])
        self.check_c = fluid_coefficients(h.model, h.t, self.check_x)
        self.cap = electric_share_cap(h.t, self.check_h, self.check_c['lapse'])
        self.hf = h.interpolate_state(h.state['flux_energy'])
        self.supply = fluid_moments(h.interpolate_state(h.state['thermal']), self.hf,
                                   h.spatial(h.state['number'])[0], c)
        self.phases = []
        for time, frame in pd.read_csv(str(INPUT)+'_points.csv').groupby('s'):
            it = int(np.argmin(abs(h.t-time)))
            demand = np.array([np.interp(h.x, frame.l, frame['geometry_'+key])
                               for key in ('rho', 'pr', 'j', 'pt')])
            self.phases.append((it, float(time), demand))

    def integrate(self, density):
        return 4*np.pi*self.dx*np.sum(density, axis=-1)

    def allocation(self, flux):
        check_share, derivative, unused = smooth_under_cap(
            self.check_x, np.minimum(flux, self.cap), self.h.state['x'])
        return check_share, check_share[self.selection], derivative[self.selection]

    def state(self, efficiency, amplitude=0.):
        c, cm = self.c, self.cm
        minus = (self.absorption+self.free_minus)*(.98/efficiency)
        plus = self.recovery*(efficiency/.98)+self.free_plus*(.98/efficiency)
        # Changes in loss integrate on the pinned material volume. The old
        # heat trajectory and its spatially interpolated capacity are retained
        # exactly at eta=.98. Optimizing the changed inventory can only improve
        # that original interpolation bound by its small interpolation slack.
        loss_delta = (1/efficiency-1/.98)*self.positive+(.98-efficiency)*self.negative
        prefix = proper_prefix(self.t, cm['lapse']*cm['rest_volume'], loss_delta)
        heat_unshifted = self.old_heat+prefix
        heat = heat_unshifted-heat_unshifted.min(axis=0)
        heat_cap = np.ptp(heat_unshifted, axis=0)
        if efficiency == .98:
            heat, heat_cap = self.old_heat.copy(), self.old_heat_cap.copy()
        thermal = compact_cell_moments(heat+heat_cap[None, :]/3, c)
        peak = max(float(np.max(minus*c['gamma']**2*(1+c['v'])**2*c['radius']**4)),
                   float(np.max(plus*c['gamma']**2*(1-c['v'])**2*c['radius']**4)))
        flux = 2*1.03*reflected_guide_factor(amplitude)*peak
        check_share, share, derivative = self.allocation(flux)
        extra = (flux-share)[None, :]/c['radius']**4
        auxiliary = wave_moments(plus, minus)+thermal+radial_field_moments(extra)
        return dict(minus=minus, plus=plus, flux=flux, share=share, check_share=check_share,
                    derivative=derivative, heat=heat, heat_cap=heat_cap, auxiliary=auxiliary,
                    initial=float(self.integrate(self.volume[0]*auxiliary[0, 0])),
                    heat_capacity=float(self.integrate(heat_cap)),
                    loss_change=float(self.integrate(prefix[-1])))


def weighted_quantile(values, weights, fractions):
    selected = weights > 0
    value, weight = np.asarray(values)[selected], np.asarray(weights)[selected]
    order = np.argsort(value)
    weight = np.cumsum(weight[order])
    return np.interp(np.asarray(fractions)*weight[-1], weight, value[order])


def port_audit(model, state):
    """Cell electrical/mechanical work and required local receiving impedance."""
    h, c, cm = model.h, model.c, model.cm
    field = model.hf-state['share']
    q = np.sqrt(2*field)
    inverse_c = c['gamma']*c['b']/c['radius']**2
    electrical, mechanical, change = capacitor_step_work(q[:-1], q[1:], inverse_c[:-1], inverse_c[1:])
    # dx=dOmega=1 normalization: actual Z gains dx/dOmega. The ratios
    # within one graded cell and its reflection are independent of that choice.
    midpoint_field = (field[:-1]+field[1:])/2
    midpoint_q = np.sqrt(2*midpoint_field)
    capacitance = cm['radius']**2/(cm['gamma']*cm['b'])
    qdot = model.hd/(cm['lapse']*midpoint_q)
    port = capacitor_port(midpoint_q, capacitance, qdot)
    weights = np.maximum(electrical, 0.)
    admittance = port['load_admittance']
    active = (admittance > 0)&(weights > 0)
    per_cell = []
    reflected_total, incoming_total, charge_total = 0., 0., weights.sum()
    for j, x in enumerate(h.x):
        selected = active[:, j]
        if not selected.any():
            continue
        a, w = admittance[selected, j], weights[selected, j]
        # a_wave^2/Z divided by VI = (1+Z*Y)^2/(4 Z*Y).
        # Minimize incident energy for a fixed real port impedance at this x.
        # This is exact analytically: Z^2=sum(w/Y)/sum(w*Y).
        impedance = np.sqrt(np.sum(w/a)/np.sum(w*a))
        y = impedance*a
        incoming = w*(1+y)**2/(4*y)
        reflected = incoming*port_reflection(a, impedance)**2
        reflected_total += reflected.sum()
        incoming_total += incoming.sum()
        zq = weighted_quantile(1/a, w, [.005, .5, .995])
        per_cell.append(dict(x=float(x), fixed_impedance=float(impedance),
            incident_energy=float(incoming.sum()), reflected_energy=float(reflected.sum()),
            reflection_energy_fraction=float(reflected.sum()/incoming.sum()),
            useful_work=float(w.sum()), impedance_q005=float(zq[0]),
            impedance_q500=float(zq[1]), impedance_q995=float(zq[2]),
            impedance_central99_ratio=float(zq[2]/zq[0])))
    capacity = np.max(field*inverse_c, axis=0)
    material_unit = compact_cell_moments(capacity[None, :], c)
    it, time, demand = model.phases[-1]
    base = model.supply[:, it]+state['auxiliary'][:, it]-demand
    def peak_with_mass(ratio):
        return float(maximum_null(base+ratio*material_unit[:, it])[0].max())
    mass_ratio = brentq(lambda ratio: peak_with_mass(ratio)-REFERENCE_FADE, 0, 1e5)
    summary = dict(
        normalized_cell_charge_min=float(q.min()), normalized_cell_charge_max=float(q.max()),
        initial_electric_rest_energy=float(model.integrate(field[0]*inverse_c[0])),
        initial_electric_ADM_energy=float(model.integrate(model.volume[0]*field[0]/c['radius'][0]**4)),
        final_electric_rest_energy=float(model.integrate(field[-1]*inverse_c[-1])),
        sum_local_electric_energy_capacities=float(model.integrate(capacity)),
        electrical_work_midpoint_identity=float(model.integrate(electrical.sum(axis=0))),
        mechanical_work_midpoint_identity=float(model.integrate(mechanical.sum(axis=0))),
        electric_rest_energy_change=float(model.integrate(change.sum(axis=0))),
        maximum_discrete_energy_identity_residual=float(abs(electrical+mechanical-change).max()),
        fixed_real_impedance_minimum_reflection_energy_fraction=float(reflected_total/incoming_total),
        fixed_real_impedance_incident_to_useful_work=float(incoming_total/charge_total),
        maximum_interval_electric_rate=float(average_electric_rate(h.t, model.check_h-state['check_share'],
                                                                model.check_c['lapse']).max()),
        conditional_capacitor_mass_energy_per_rated_energy=mass_ratio,
        conditional_capacitor_specific_energy_J_per_kg=float(299792458.**2/mass_ratio),
        capacitor_mass_comparison='All remaining radial electric cells; added conserved mass only. '
            'Headroom ends at the old formal fade value, not a universal feasibility limit.',
    )
    return summary, per_cell


def bend_audit(model, state):
    """Local finite vacuum bend. Field, boundary reaction, and scale separation."""
    h = model.h
    c = fluid_coefficients(h.model, h.t, np.array([h.edges[0], h.edges[-1]]))
    rows = []
    factor = toroidal_bend_factors(.2)
    for j, x in enumerate((h.edges[0], h.edges[-1])):
        for bend_radius in (.01, .05, .1):
            # Each leg carries half the paired guide flux; a U-turn connects
            # one forward leg to one return. Phi in [0,pi] gives <T_xx>=0.
            u_leg = state['flux']/(2*c['radius'][:, j]**4)
            area = 4*np.pi*c['radius'][:, j]**2
            rest_energy = u_leg*area*np.pi*bend_radius*factor['energy_factor']
            energy = c['gamma'][:, j]*rest_energy
            traction = 2*u_leg*area
            coordinate_span = bend_radius/(c['gamma'][:, j]*c['b'][:, j])
            minimum_clearance = np.min(h.t-(x+coordinate_span)-.35)
            # Local finite-bend metric error diagnostic: radial excursion only.
            variation = 0.
            for it, time in enumerate(h.t):
                xx = x+np.array([-1., 0., 1.])*coordinate_span[it]
                g = h.model.metric(float(time), xx)
                for a in (g.alpha, g.b, g.radius):
                    variation = max(variation, float(np.max(abs(a/a[1]-1))))
            rows.append(dict(end='left' if j == 0 else 'receiver', bend_radius=bend_radius,
                aperture_half_width=.2*bend_radius,
                initial_bend_ADM_energy=float(energy[0]), peak_bend_ADM_energy=float(energy.max()),
                peak_bend_guide_density=float(np.max(u_leg)*factor['peak_energy_factor']),
                peak_straight_cut_magnetic_reaction=float(traction.max()),
                minimum_packet_clearance=float(minimum_clearance),
                maximum_radial_metric_fractional_variation=variation,
                supplied_support_material=False, curved_background_Maxwell_solution=False))
    return rows


def evaluate(cells):
    model = InterfaceHistory(cells)
    cases, phase_rows, reflection_rows = [], [], []
    for efficiency in (1., .98, .95, .9, .85, .8):
        state = model.state(efficiency)
        entry = dict(efficiency=efficiency, cells=cells, initial_auxiliary_energy=state['initial'],
                     heat_capacity=state['heat_capacity'], converter_loss_change=state['loss_change'],
                     guide_flux=state['flux'])
        for it, time, demand in model.phases:
            val = maximum_null(model.supply[:, it]+state['auxiliary'][:, it]-demand)[0]
            phase_rows.append(dict(efficiency=efficiency, cells=cells, time=time,
                                  required_negative_null=float(max(0., val.max()))))
        for amplitude in (0., .005, .01, .02, .03, .05, .1):
            envelope = model.state(efficiency, amplitude)
            reflection_rows.append(dict(efficiency=efficiency, cells=cells, amplitude=amplitude,
                auxiliary_energy_with_guide_margin=envelope['initial'], guide_flux=envelope['flux'],
                calculation='Guide envelope only; reflected waves require separate propagation'))
        if state['initial'] < REFERENCE_STARTUP and model.state(efficiency, .2)['initial'] > REFERENCE_STARTUP:
            entry['startup_guide_only_break_even_amplitude'] = brentq(
                lambda r: model.state(efficiency, r)['initial']-REFERENCE_STARTUP, 0., .2)
        cases.append(entry)
    nominal = model.state(.98)
    nominal_expected = json.loads((BASE/f'poynting_delivery/finite_taps/n{cells}_summary.json').read_text())['cases'][-1]
    residual = abs(nominal['initial']-nominal_expected['initial_auxiliary_slice_energy'])
    if residual > 1e-10:
        raise ArithmeticError('nominal finite-tap control changed')
    eta_threshold = brentq(lambda eta: model.state(eta)['initial']-REFERENCE_STARTUP, .8, .98)
    ports, port_rows = port_audit(model, nominal)
    bends = bend_audit(model, nominal)
    write_json(OUTPUT/f'n{cells}_summary.json', dict(cases=cases, phases=phase_rows,
        minimum_matched_efficiency_to_retain_startup_comparison=eta_threshold,
        nominal_reproduction_residual=residual, capacitor_port=ports,
        finite_bends=bends, compared_spatial_points=len(model.check_x)))
    pd.DataFrame(reflection_rows).to_csv(OUTPUT/f'n{cells}_guide_envelopes.csv', index=False)
    pd.DataFrame(port_rows).to_csv(OUTPUT/f'n{cells}_capacitive_ports.csv', index=False)
    print(f'finite interface n={cells}: eta threshold={eta_threshold:.6g}; '
          f'fixed-port reflected energy={ports["fixed_real_impedance_minimum_reflection_energy_fraction"]:.6g}', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if OUTPUT.exists():
        raise RuntimeError('preserve completed interface evidence')
    sources = [Path(__file__), Path(__file__).with_name('run_poynting_delivery.py'),
        ROOT/'toolkit/adm_harness_cli/adm_harness/finite_work_interface.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/shared_field_delivery.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/active_transfer_reservoir.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/pressure_linked_storage.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/poynting_delivery.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/graded_electrothermal.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/regenerative_converter.py',
        ROOT/'toolkit/adm_harness_cli/tests/test_finite_work_interface.py',
        Path(str(INPUT)+'_states.npz'), Path(str(INPUT)+'_points.csv'),
        BASE/'active_transfer_reservoir/metric_fine.npz', BASE/'active_transfer_reservoir/medium_baseline.npz']
    for n in (512, 1024):
        sources += [BASE/f'poynting_delivery/spatial_refinement/right_n{n}_t1_states.npz',
                    BASE/f'poynting_delivery/finite_taps/finite_n{n}_states.npz',
                    BASE/f'poynting_delivery/finite_taps/n{n}_summary.json']
    before = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    OUTPUT.mkdir(parents=True)
    with ProcessPoolExecutor(max_workers=min(args.workers, 4), mp_context=multiprocessing.get_context('spawn')) as pool:
        list(pool.map(evaluate, (512, 1024)))
    if before != {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}:
        raise RuntimeError('input changed during interface evaluation')
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        input_sha256=before,
        output_sha256={p.name: sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
