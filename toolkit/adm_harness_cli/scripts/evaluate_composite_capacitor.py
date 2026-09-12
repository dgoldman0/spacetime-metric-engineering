#!/usr/bin/env python3
"""Count composite capacitor backing and its connections on the pinned rail.

Writes compact numerical evidence. The narrative report is maintained by hand.
Each spatial resolution/recovery case is independent and runs in a worker.
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

from adm_harness.composite_capacitor import (
    anisotropic_moments, local_mechanical_reuse, prepared_skin_backing,
    pressure_shared_floor, retained_support_energy,
)
from adm_harness.finite_work_interface import capacitor_step_work
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.source_ledger import sha256_file
from evaluate_finite_work_interface import InterfaceHistory
from evaluate_recovery_work_interface import recovery_state
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'composite_capacitor'
FAMILIES = ('dec_floor', 'directional', 'stiff_fluid', 'radiation_fluid')


def history(model, state):
    c = model.c
    ell, radius = c['gamma']*c['b'], c['radius']
    volume = c['rest_volume']
    flux = model.hf-state['share']
    electric = flux/radius**4
    inverse_c = ell/radius**2
    electrical, mechanical, change = capacitor_step_work(
        np.sqrt(2*flux[:-1]), np.sqrt(2*flux[1:]), inverse_c[:-1], inverse_c[1:])
    energy = electric*volume
    thermal = model.h.interpolate_state(model.h.state['thermal'])
    pressure = np.maximum(thermal/(3*volume), 0.)
    fluid_work = -(pressure[1:]+pressure[:-1])/2*np.diff(volume, axis=0)
    # The paired radial guide has the same longitudinal pressure as radial E.
    # Its static flux has zero charging port and a nonzero deformation port.
    guide_energy = state['flux']*inverse_c
    guide_work = np.diff(guide_energy, axis=0)
    return dict(ell=ell, radius=radius, volume=volume, electric=electric,
                energy=energy, electrical=electrical, mechanical=mechanical,
                pressure=pressure, fluid_work=fluid_work, guide_work=guide_work,
                guide_energy=guide_energy, energy_residual=float(abs(electrical+mechanical-change).max()))


def family_history(h, family):
    floor = pressure_shared_floor(h['electric'], h['pressure'], family)
    used = floor['used_pressure']
    used_fluid_work = -(used[1:]+used[:-1])/2*np.diff(h['volume'], axis=0)
    # Support has stresses opposite E minus the credited isotropic pressure.
    mechanical = -h['mechanical']-used_fluid_work
    minimum = floor['density']*h['volume']
    retained = retained_support_energy(minimum, mechanical)
    active_port = np.diff(minimum, axis=0)-mechanical
    return dict(**floor, minimum_energy=minimum, retained_energy=retained,
                mechanical_work=mechanical, active_port=active_port,
                used_fluid_work=used_fluid_work)


def evaluate(task):
    cells, fraction = task
    model = InterfaceHistory(cells)
    state = recovery_state(model, fraction)
    h = history(model, state)
    c, integrate = model.c, model.integrate
    phase_rows, cases, histories = [], [], []

    def phases(name, moments):
        for it, time, demand in model.phases:
            tensor = model.supply[:, it]+state['auxiliary'][:, it]+moments[:, it]-demand
            value, direction = maximum_null(tensor)
            j = int(np.argmax(value))
            phase_rows.append(dict(case=name, time=time,
                required_negative_null=float(max(0., value[j])), peak_x=float(model.x[j]),
                peak_null_cosine=float(direction[j]),
                added_support_ADM=float(integrate(model.volume[it]*moments[0, it]))))

    phases('zero_added_capacitor_material', np.zeros_like(model.supply))
    prepared = prepared_skin_backing(h['energy'], h['ell'], h['radius'])
    skin, backing = prepared['skin_energy'], prepared['backing_energy']
    prepared_moments = anisotropic_moments((skin+backing)/h['volume'], backing/h['volume'],
                                          -skin/h['volume'], c['v'])
    phases('prepared_skin_directional_backing_coverage', prepared_moments)
    cases.append(dict(case='prepared_skin_directional_backing_coverage',
        initial_added_rest=float(integrate((skin+backing)[0])),
        final_added_rest=float(integrate((skin+backing)[-1])),
        initial_skin_rest=float(integrate(skin[0])), final_skin_rest=float(integrate(skin[-1])),
        initial_backing_rest=float(integrate(backing[0])), final_backing_rest=float(integrate(backing[-1])),
        maximum_excess_radial_pressure=float(np.max(prepared['excess_radial_stress_energy']/h['volume'])),
        maximum_excess_angular_tension=float(np.max(prepared['excess_angular_tension_energy']/h['volume'])),
        force_equilibrium_supplied=False))

    for family in FAMILIES:
        f = family_history(h, family)
        for regime, energy in (('retained', f['retained_energy']), ('controlled_floor', f['minimum_energy'])):
            name = family+'_'+regime
            moments = anisotropic_moments(energy/h['volume'], f['radial_pressure'], f['angular_pressure'], c['v'])
            phases(name, moments)
            row = dict(case=name, initial_added_rest=float(integrate(energy[0])),
                final_added_rest=float(integrate(energy[-1])),
                support_mechanical_work=float(integrate(f['mechanical_work'].sum(axis=0))),
                credited_fluid_compression=float(integrate(f['used_fluid_work'].sum(axis=0))),
                energy_condition_floor_margin=float(np.min(energy-f['minimum_energy'])),
                additional_transport_counted=False, constitutive_trajectory_supplied=False)
            if regime == 'controlled_floor':
                joint = h['electrical']+f['active_port']
                row.update(support_port_input=float(integrate(np.maximum(f['active_port'], 0).sum(axis=0))),
                    support_port_export=float(integrate(np.maximum(-f['active_port'], 0).sum(axis=0))),
                    joint_port_input=float(integrate(np.maximum(joint, 0).sum(axis=0))),
                    joint_port_export=float(integrate(np.maximum(-joint, 0).sum(axis=0))),
                    work_residual=float(abs(np.diff(h['energy']+energy, axis=0)-joint+f['used_fluid_work']).max()))
            else:
                row['work_residual'] = float(abs(np.diff(energy, axis=0)-f['mechanical_work']).max())
            cases.append(row)

    connection_rows = []
    for name, first in (('electric_cells', h['mechanical']),
                        ('delivery_guides', h['guide_work']),
                        ('electric_and_guides', h['mechanical']+h['guide_work'])):
        reuse = local_mechanical_reuse(first, h['fluid_work'])
        connection_rows.append(dict(case=name,
            mechanical_work_net=float(integrate(first.sum(axis=0))),
            gross_mechanical_output=float(integrate(np.maximum(-first, 0).sum(axis=0))),
            gross_mechanical_input=float(integrate(np.maximum(first, 0).sum(axis=0))),
            optimistic_colocated_fluid_reuse=float(integrate(reuse['reused'].sum(axis=0))),
            remaining_mechanical_export=float(integrate(reuse['remaining_export'].sum(axis=0))),
            remaining_mechanical_input=float(integrate(reuse['remaining_input'].sum(axis=0))),
            coupling_supplied=False))
    for it, time in enumerate(model.t):
        histories.append(dict(time=float(time), electric_rest=float(integrate(h['energy'][it])),
            guide_rest=float(integrate(h['guide_energy'][it])),
            fluid_pressure_volume=float(integrate(h['pressure'][it]*h['volume'][it])),
            skin_rest=float(integrate(skin[it])), backing_rest=float(integrate(backing[it]))))
    dt = np.diff(model.t)[:, None]
    weight = dt*(c['lapse'][1:]+c['lapse'][:-1])/2*(h['energy'][1:]+h['energy'][:-1])/2
    mid_p = (h['pressure'][1:]+h['pressure'][:-1])/2
    mid_e = (h['electric'][1:]+h['electric'][:-1])/2
    exposure_credit = float(np.sum(weight*np.minimum(mid_p/mid_e, 1.))/np.sum(weight))
    stem = f'n{cells}_recovery{int(100*fraction)}'
    summary = dict(cells=cells, recovery_fraction=fraction, guide_flux=float(state['flux']),
        electric_work_identity_residual=h['energy_residual'],
        radial_length_fade_to_start_quantiles=np.quantile(h['ell'][-1]/h['ell'][0], [0,.25,.5,.75,1]).tolist(),
        radius_fade_to_start_quantiles=np.quantile(h['radius'][-1]/h['radius'][0], [0,.25,.5,.75,1]).tolist(),
        electric_work_input=float(integrate(np.maximum(h['electrical'], 0).sum(axis=0))),
        electric_work_export=float(integrate(np.maximum(-h['electrical'], 0).sum(axis=0))),
        fluid_compression_net=float(integrate(h['fluid_work'].sum(axis=0))),
        fluid_compression_positive=float(integrate(np.maximum(h['fluid_work'], 0).sum(axis=0))),
        pressure_credit_energy_duration_fraction=exposure_credit,
        cases=cases, connections=connection_rows,
        normalization='Sum of local material-frame label energies/work; L is free. These are not globally conserved ADM work.',
        open_attachment='The standing support response and the reciprocal mechanical work are exposed duties.')
    write_json(OUTPUT/(stem+'_summary.json'), summary)
    pd.DataFrame(phase_rows).to_csv(OUTPUT/(stem+'_phases.csv'), index=False)
    pd.DataFrame(histories).to_csv(OUTPUT/(stem+'_history.csv'), index=False)
    print(f'{stem}: composite and mechanical connection controls complete', flush=True)
    return summary


def input_hashes():
    hashes = {}
    for name in ('finite_work_interface_recovery', 'charged_capacitor_work_delivery'):
        path = BASE/name/'manifest.json'
        hashes[str(path.relative_to(ROOT))] = sha256_file(path)
        for relative, expected in json.loads(path.read_text())['input_sha256'].items():
            if sha256_file(ROOT/relative) != expected:
                raise RuntimeError(f'inherited source changed: {relative}')
            hashes[relative] = expected
    for path in (Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/composite_capacitor.py',
                 ROOT/'toolkit/adm_harness_cli/tests/test_composite_capacitor.py'):
        hashes[str(path.relative_to(ROOT))] = sha256_file(path)
    # Also pin all archived numeric payloads read through InterfaceHistory.
    for cells in (512,1024):
        for path in (BASE/f'poynting_delivery/spatial_refinement/right_n{cells}_t1_states.npz',
                     BASE/f'poynting_delivery/finite_taps/finite_n{cells}_states.npz'):
            hashes[str(path.relative_to(ROOT))] = sha256_file(path)
    return hashes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if OUTPUT.exists():
        raise RuntimeError('preserve completed composite evidence')
    before = input_hashes()
    OUTPUT.mkdir(parents=True)
    with ProcessPoolExecutor(max_workers=min(4,args.workers), mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(evaluate, ((512,.9),(1024,.9),(512,1.),(1024,1.))))
    if max(c.get('work_residual',0.) for result in results for c in result['cases']) > 1e-10:
        raise ArithmeticError('composite work balance failed')
    if before != input_hashes():
        raise RuntimeError('inputs changed during composite calculation')
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=before,
        output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
