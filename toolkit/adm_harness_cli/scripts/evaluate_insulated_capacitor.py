#!/usr/bin/env python3
"""Count transverse magnetic insulation and work on the pinned rail history.

Controls include actively prescribed minimum field and a minimum frozen flux
that covers the entire interval. Extra converter, confinement, return and
carrier tensors remain exposed construction duties. The output is numerical
evidence; narrative conclusions belong in the manually written report.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import multiprocessing

import numpy as np
import pandas as pd
from scipy.constants import c as LIGHT, G, epsilon_0, e, m_e, m_p, hbar

from adm_harness.charged_capacitor import magnetic_cell_work, transverse_magnetic_moments
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.source_ledger import sha256_file
from evaluate_finite_work_interface import InterfaceHistory
from evaluate_recovery_work_interface import recovery_state
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'charged_capacitor_insulation'
DRIFTS = (.9, .7, .5)


def evaluate_case(task):
    cells, recovery = task
    model = InterfaceHistory(cells)
    state = recovery_state(model, recovery)
    c = model.c
    ell, radius = c['gamma']*c['b'], c['radius']
    volume = c['rest_volume']
    electric = (model.hf-state['share'])/radius**4
    pressure = model.h.interpolate_state(model.h.state['thermal'])/(3*volume)
    required_flux = electric*(ell*radius)**2
    prepared_flux = required_flux.max(axis=0)
    initial_frozen = electric[0]*(ell[0]*radius[0])**2
    rows, histories, points = [], [], []
    # A proper-volume/proper-duration weight is explicitly used for pressure
    # coverage. It is a diagnostic of this fixed fluid history, independent
    # of any unconstructed standing-support load response.
    duration = np.diff(model.t)[:, None]*(c['lapse'][1:]+c['lapse'][:-1])/2
    weight = duration*(volume[1:]+volume[:-1])/2*(electric[1:]+electric[:-1])/2
    for drift in DRIFTS:
        for regime in ('controlled_minimum', 'frozen_flux_cover'):
            magnetic = (electric if regime == 'controlled_minimum'
                        else prepared_flux[None, :]/(ell*radius)**2)/drift**2
            moments = transverse_magnetic_moments(magnetic, c['v'])
            port, mechanical, energy = magnetic_cell_work(magnetic, ell, radius)
            adm = model.integrate(model.volume*moments[0])
            rest = model.integrate(energy)
            p_mid = (pressure[1:]+pressure[:-1])/2
            ub_mid = (magnetic[1:]+magnetic[:-1])/2
            coverage = float(np.sum(weight*(p_mid >= ub_mid))/np.sum(weight))
            row = dict(cells=cells, recovery=recovery, regime=regime, drift=drift,
                initial_extra_magnetic_ADM=float(adm[0]), final_extra_magnetic_ADM=float(adm[-1]),
                peak_extra_magnetic_ADM=float(adm.max()),
                total_interface_initial_ADM=float(state['initial']+adm[0]),
                initial_extra_magnetic_rest=float(rest[0]), final_extra_magnetic_rest=float(rest[-1]),
                magnetic_external_work_net=float(model.integrate(port.sum(axis=0))),
                magnetic_external_work_input=float(model.integrate(np.maximum(port, 0).sum(axis=0))),
                magnetic_external_work_recovered=float(model.integrate(np.maximum(-port, 0).sum(axis=0))),
                magnetic_mechanical_work=float(model.integrate(mechanical.sum(axis=0))),
                discrete_work_residual=float(abs(port+mechanical-np.diff(energy, axis=0)).max()),
                pressure_covers_magnetic_energy_weighted_fraction=coverage,
                peak_magnetic_to_electric_ratio=float((magnetic/electric).max()),
                minimum_insulation_ratio=float((magnetic*drift**2/electric).min()))
            for it, time, demand in model.phases:
                residual = model.supply[:, it]+state['auxiliary'][:, it]+moments[:, it]-demand
                required, direction = maximum_null(residual)
                j = int(np.argmax(required))
                points.append(dict(cells=cells, recovery=recovery, regime=regime, drift=drift,
                    time=time, required_negative_null=float(max(0., required[j])),
                    peak_x=float(model.x[j]), peak_null_cosine=float(direction[j]),
                    extra_magnetic_ADM=float(adm[it])))
                if it == len(model.t)-1:
                    row['fade_required_negative_null'] = float(max(0., required[j]))
            rows.append(row)
            for it, time in enumerate(model.t):
                histories.append(dict(regime=regime, drift=drift, time=float(time),
                    extra_magnetic_ADM=float(adm[it]), extra_magnetic_rest=float(rest[it])))
    electric_coefficient = LIGHT**2*np.sqrt(2*electric/(epsilon_0*G))
    critical_field = m_e*m_e*LIGHT**3/(e*hbar)
    # Conditional comparison from the archived matched-load capacitor audit.
    budget = .32431293 if recovery == .9 else .40105503
    scale = dict(peak_E_times_L_volts=float(electric_coefficient.max()),
        critical_electric_field_V_per_m=float(critical_field),
        L_for_peak_E_equals_critical_m=float(electric_coefficient.max()/critical_field),
        L_for_peak_E_equals_one_percent_critical_m=float(100*electric_coefficient.max()/critical_field),
        assumed_added_mass_energy_per_capacity=budget,
        independent_electron_positron_plate_min_voltage_for_mass_budget_V=float(4*m_e*LIGHT**2/(e*budget)),
        quasistatic_local_pair_threshold_voltage_V=float(2*m_e*LIGHT**2/e),
        independent_electron_proton_plate_min_voltage_for_mass_budget_V=float(2*(m_p+m_e)*LIGHT**2/(e*budget)),
        interpretation='Field-strength scale markers, with L free. Pair leakage requires the actual finite '
            'gap, duration and field invariants. The plate mass comparison counts two independent charged layers.')
    stem = f'n{cells}_recovery{int(100*recovery)}'
    pd.DataFrame(rows).to_csv(OUTPUT/(stem+'_cases.csv'), index=False)
    pd.DataFrame(points).to_csv(OUTPUT/(stem+'_phases.csv'), index=False)
    pd.DataFrame(histories).to_csv(OUTPUT/(stem+'_history.csv'), index=False)
    np.savez_compressed(OUTPUT/(stem+'_inputs.npz'), t=model.t, x=model.x, electric=electric,
                        ell=ell, radius=radius, pressure=pressure, prepared_transverse_flux=prepared_flux)
    result = dict(cells=cells, recovery=recovery, scale=scale, cases=rows,
        initial_only_frozen_flux_minimum_cover=float((initial_frozen[None, :]/required_flux).min()),
        initial_only_frozen_flux_maximum_cover=float((initial_frozen[None, :]/required_flux).max()),
        capacitor_boundary_material_supplied=False, magnetic_current_and_return_supplied=False,
        magnetic_work_transport_and_loss_supplied=False,
        tensor_comparison='Necessary paired transverse-field tensor on the existing material and delivery history.')
    write_json(OUTPUT/(stem+'_summary.json'), result)
    print(f'{stem}: controlled/frozen insulation and scale controls complete', flush=True)
    return result


def main():
    if OUTPUT.exists():
        raise RuntimeError('preserve completed capacitor insulation evidence')
    OUTPUT.mkdir(parents=True)
    with ProcessPoolExecutor(max_workers=4, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(evaluate_case, ((512, .9), (1024, .9), (512, 1.), (1024, 1.))))
    if max(row['discrete_work_residual'] for result in results for row in result['cases']) > 1e-10:
        raise ArithmeticError('transverse field energy accounting failed')
    pd.DataFrame([row for result in results for row in result['cases']]).to_csv(OUTPUT/'all_cases.csv', index=False)
    sources = {str(Path(__file__).relative_to(ROOT)): sha256_file(Path(__file__)),
               'toolkit/adm_harness_cli/adm_harness/charged_capacitor.py':
               sha256_file(ROOT/'toolkit/adm_harness_cli/adm_harness/charged_capacitor.py')}
    for name in ('finite_work_interface', 'finite_work_interface_recovery'):
        path = BASE/name/'manifest.json'
        sources[str(path.relative_to(ROOT))] = sha256_file(path)
        for relative, expected in json.loads(path.read_text())['input_sha256'].items():
            if sha256_file(ROOT/relative) != expected:
                raise ArithmeticError(f'inherited producer/input changed: {relative}')
            sources[relative] = expected
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        input_sha256=sources,
        output_sha256={p.name: sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
