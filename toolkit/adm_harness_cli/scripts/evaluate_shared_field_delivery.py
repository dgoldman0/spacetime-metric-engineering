#!/usr/bin/env python3
"""Rate-preserving field allocation and finite-current screening of the selected route."""
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess

import numpy as np
import pandas as pd
from scipy.constants import c as C_SI, G, mu_0, e, m_e, m_p

from adm_harness.pressure_linked_storage import fluid_coefficients, fluid_moments
from adm_harness.regenerative_converter import compact_cell_moments
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.poynting_delivery import wave_moments, reflection_guide_multiplier
from adm_harness.shared_field_delivery import (
    average_electric_rate, cold_current_velocities, electric_share_cap,
    radial_field_moments, smooth_under_cap,
)
from adm_harness.source_ledger import sha256_file
from run_poynting_delivery import DeliveryHistory, BASE, ROOT, INPUT, STORES, write_json

OUTPUT = BASE/'poynting_delivery/shared_field'


def evaluate(cells):
    h = DeliveryHistory(cells)
    path = BASE/f'poynting_delivery/spatial_refinement/right_n{cells}_t1_states.npz'
    with np.load(path) as z:
        waves = {k: z[k] for k in z.files}
    x, t = h.x, h.t
    if not np.array_equal(x, waves['x']) or not np.array_equal(t, waves['t']):
        raise RuntimeError('pinned selected route grid mismatch')
    c = fluid_coefficients(h.model, t, x)
    volume = c['b']*c['radius']**2
    dx = h.edges[1]-h.edges[0]
    integrate = lambda a: 4*np.pi*dx*np.sum(a, axis=-1)
    plus, minus = waves['mu_plus'], waves['mu_minus']
    wave = wave_moments(plus, minus)
    hp = np.max(plus*c['gamma']**2*(1-c['v'])**2*c['radius']**4)
    hm = np.max(minus*c['gamma']**2*(1+c['v'])**2*c['radius']**4)
    electric_original = h.interpolate_state(h.state['flux_energy'])
    thermal = compact_cell_moments(waves['heat']+waves['heat_capacity']/3, c)
    supply = fluid_moments(h.interpolate_state(h.state['thermal']), electric_original,
                          h.spatial(h.state['number'])[0], c)
    # The original material knots can contain tighter rate constraints than
    # the finite-volume cell centers. Both grids enter the allocation cap.
    check_x = np.unique(np.r_[x, h.state['x']])
    selection = np.searchsorted(check_x, x)
    check_h = np.array([np.interp(check_x, h.state['x'], row) for row in h.state['flux_energy']])
    check_c = fluid_coefficients(h.model, t, check_x)
    cap_check = electric_share_cap(t, check_h, check_c['lapse'], rate_ceiling=1., electric_floor=.1)
    cap = cap_check[selection]
    knots = h.state['x']
    archived = pd.read_csv(str(INPUT)+'_points.csv')
    tm = (t[1:]+t[:-1])/2
    cm = fluid_coefficients(h.model, tm, x)
    hd = h.spatial(h.hdot)
    charge = np.maximum(hd, 0)/(.98*cm['lapse']*cm['radius']**4)
    recovery = .98*np.maximum(-hd, 0)/(cm['lapse']*cm['radius']**4)
    wave_force = charge+recovery  # Incoming - wave and emitted + recovery.
    heat_force = (.5*(waves['heat'][1:]+waves['heat'][:-1])+waves['heat_capacity']/3)/cm['rest_volume']*cm['acceleration']
    endpoint_force = cm['gamma']*(cm['normal_force']-cm['v']*cm['power'])
    phases, cases, source_rows = [], [], []
    for speed in (.2, .5, .8):
        for reflection in (0., .05, .1):
            # Equal-area feed/recovery legs, plus a 3% wave-energy margin.
            flux = 2*1.03*reflection_guide_multiplier(reflection, speed)*max(hp, hm)
            check_share, check_gradient, values = smooth_under_cap(check_x, np.minimum(flux, cap_check), knots, safety=.98)
            share, share_x = check_share[selection], check_gradient[selection]
            electrical = electric_original-share[None, :]
            check_electric = check_h-check_share[None, :]
            check_rate = average_electric_rate(t, check_electric, check_c['lapse'])
            if np.min(check_electric) <= 0 or np.max(check_rate) > 1+1e-7:
                raise RuntimeError('original-knot and transport-grid electric rate gate failed')
            extra_flux = flux-share
            extra = extra_flux[None, :]/c['radius']**4
            auxiliary = wave+thermal+radial_field_moments(extra)
            extra_force = share_x[None, :]/(cm['gamma']*cm['b']*cm['radius']**4)
            remainder = endpoint_force-wave_force-heat_force-extra_force
            case = f'n{cells}_v{round(speed*100):03d}_r{round(reflection*100):03d}'
            result = dict(case=case, cells=cells, drift_comparison=speed,
                reflection_guide_margin=reflection, wave_energy_margin=1.03,
                guide_flux_energy=flux, maximum_share_cap_violation=float(max(0, (share-cap).max())),
                minimum_remaining_electric_fraction=float(np.min(check_electric/check_h)),
                maximum_averaged_electric_rate=float(check_rate.max()),
                original_averaged_electric_rate=float(average_electric_rate(t, check_h, check_c['lapse']).max()),
                original_and_transport_check_points=len(check_x),
                electrical_work_identity_residual=float(abs(np.diff(electrical, axis=0)-np.diff(electric_original, axis=0)).max()),
                initial_total_guide_slice_energy=float(integrate(volume[0]*flux/c['radius'][0]**4)),
                initial_shared_slice_energy=float(integrate(volume[0]*share/c['radius'][0]**4)),
                initial_extra_field_slice_energy=float(integrate(volume[0]*extra[0])),
                initial_auxiliary_slice_energy=float(integrate(volume[0]*auxiliary[0, 0])),
                maximum_extra_field_force=float(abs(extra_force).max()),
                maximum_remaining_endpoint_force=float(abs(remainder).max()),
                peak_left_guide_cut_traction=float((flux/c['radius'][:, 0]**4).max()),
                peak_right_guide_cut_traction=float((flux/c['radius'][:, -1]**4).max()),
                peak_extra_left_traction=float(extra[:, 0].max()),
                peak_extra_right_traction=float(extra[:, -1].max()))
            cases.append(result)
            for time, frame in archived.groupby('s'):
                it = int(np.argmin(abs(t-time)))
                demand = np.array([np.interp(x, frame.l, frame['geometry_'+key]) for key in ('rho', 'pr', 'j', 'pt')])
                endpoint = np.array([np.interp(x, frame.l, frame['endpoint_'+key]) for key in ('rho', 'pr', 'j', 'pt')])
                value, direction = maximum_null(supply[:, it]+auxiliary[:, it]-demand)
                residue = maximum_null(auxiliary[:, it]-endpoint)[0]
                phases.append(dict(case=case, cells=cells, s=float(time), drift_comparison=speed,
                    reflection_guide_margin=reflection, required_negative_null=float(max(0, value.max())),
                    auxiliary_slice_energy=float(integrate(volume[it]*auxiliary[0, it])),
                    remaining_endpoint_negative_null=float(max(0, residue.max()))))
                if speed == .5 and reflection == 0:
                    source_rows.extend(dict(s=float(time), x=float(xx),
                        required_negative_null=float(max(0, value[j])), worst_direction=float(direction[j]))
                        for j, xx in enumerate(x))
            if speed == .5 and reflection == 0:
                np.savez_compressed(OUTPUT/f'selected_n{cells}_states.npz', t=t, x=x, shared_flux=share,
                    shared_flux_x=share_x, extra_flux=extra_flux, electric_flux=electrical,
                    guide_flux=np.full_like(x, flux), rate_cap=cap, allocation_knots=knots,
                    allocation_values=values, remaining_endpoint_force=remainder)
                pd.DataFrame(dict(s=t, auxiliary_slice_energy=integrate(volume*auxiliary[0]),
                    existing_field_reallocated_energy=integrate(volume*share/c['radius']**4),
                    extra_field_slice_energy=integrate(volume*extra),
                    wave_slice_energy=integrate(volume*(plus+minus)),
                    thermal_slice_energy=integrate(volume*thermal[0]))).to_csv(
                    OUTPUT/f'selected_n{cells}_inventories.csv', index=False)
    pd.DataFrame(source_rows).to_csv(OUTPUT/f'selected_n{cells}_source.csv', index=False)
    write_json(OUTPUT/f'n{cells}_summary.json', dict(cases=cases, phases=phases))
    return max(float(np.max(plus*c['gamma']**2*(1-c['v'])**2)),
               float(np.max(minus*c['gamma']**2*(1+c['v'])**2)))


def current_screen(wave_mean):
    # Compact transverse profile psi=A(1-r^2/a^2)^3 inside r<a. Its net
    # longitudinal current integrates to zero and j_peak=sqrt(120*u_mean)/a.
    rows = []
    for width in (.003, .01, .03):
        for kappa in (.1, .2):
            current_L2 = np.sqrt(120*wave_mean)*C_SI**2/(np.sqrt(mu_0*G)*width)
            density_L2 = current_L2/(e*C_SI*kappa)
            mass_energy = density_L2*(m_p+m_e)*G/C_SI**2
            velocities = [cold_current_velocities(sign*kappa, m_p/m_e) for sign in (-1, 1)]
            electron_skin_over_L = np.sqrt(m_e/(mu_0*density_L2*e**2))
            rows.append(dict(transverse_radius_over_L=width, kappa_max=kappa,
                peak_current_density_times_L_squared_A=current_L2,
                background_number_density_times_L_squared_per_m=density_L2,
                background_mass_energy_density_model=mass_energy,
                mass_energy_over_peak_mean_wave_energy=mass_energy/wave_mean,
                maximum_longitudinal_ion_speed=max(abs(row[0]) for row in velocities),
                maximum_longitudinal_electron_speed=max(abs(row[1]) for row in velocities),
                electron_inertial_length_over_L=electron_skin_over_L))
    return rows


def main():
    if OUTPUT.exists():
        raise RuntimeError('retain completed allocation evidence')
    sources = [Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/shared_field_delivery.py',
        ROOT/'toolkit/adm_harness_cli/tests/test_shared_field_delivery.py',
        ROOT/'toolkit/adm_harness_cli/scripts/run_poynting_delivery.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/active_transfer_reservoir.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/pressure_linked_storage.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/graded_electrothermal.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/regenerative_converter.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/poynting_delivery.py',
        Path(str(INPUT)+'_states.npz'), Path(str(INPUT)+'_points.csv'), STORES,
        BASE/'active_transfer_reservoir/metric_fine.npz', BASE/'active_transfer_reservoir/medium_baseline.npz']
    manifest_path = BASE/'poynting_delivery/spatial_refinement/manifest.json'
    manifest = json.loads(manifest_path.read_text())
    for cells in (512, 1024):
        path = manifest_path.parent/f'right_n{cells}_t1_states.npz'
        if sha256_file(path) != manifest['output_sha256'][path.name]:
            raise RuntimeError('selected transport evidence changed')
        sources.append(path)
    before = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    OUTPUT.mkdir(parents=True)
    waves = [evaluate(cells) for cells in (512, 1024)]
    write_json(OUTPUT/'current_screen.json', current_screen(max(waves)))
    if before != {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}:
        raise RuntimeError('source changed during allocation screen')
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        input_sha256=before,
        output_sha256={p.name: sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))
    print('Completed finite-rate shared-field allocation and local current screen.', flush=True)


if __name__ == '__main__':
    main()
