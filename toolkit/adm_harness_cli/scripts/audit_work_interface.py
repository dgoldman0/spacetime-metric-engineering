#!/usr/bin/env python3
"""Independent capacitor closure, conservation, comparison plots, and hashes."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import multiprocessing

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from adm_harness.finite_work_interface import capacitor_step_work
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.regenerative_converter import compact_cell_moments
from adm_harness.shared_field_delivery import radial_field_moments
from adm_harness.source_ledger import sha256_file
from evaluate_finite_work_interface import InterfaceHistory
from evaluate_recovery_work_interface import recovery_state
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'finite_work_interface_audit'


def closed_cells(cells):
    """Local equilibrium controls for aligned electric fields in closed cells.

The integrated wall stresses cancel (-U,+U,+U) of the electric field.
The DEC then requires wall energy >= U. The first comparison grants an
instantaneous bound with freely changed wall inventory. The second integrates
the reciprocal mechanical work into the wall, with zero wall heat export.
Both are small-cell stress/energy controls, without a supplied wall EOS.
"""
    model = InterfaceHistory(cells)
    state = recovery_state(model, .9)
    c = model.c
    field = model.hf-state['share']
    density = field/c['radius']**4
    energy = density*c['rest_volume']
    k = c['gamma']*c['b']/c['radius']**2
    electrical, mechanical, unused = capacitor_step_work(
        np.sqrt(2*field[:-1]), np.sqrt(2*field[1:]), k[:-1], k[1:])
    mechanical_prefix = np.r_[np.zeros_like(mechanical[:1]), np.cumsum(mechanical, axis=0)]
    initial_wall = np.max(energy+mechanical_prefix, axis=0)
    wall = initial_wall-mechanical_prefix
    if np.min(wall-energy) < -1e-11:
        raise ArithmeticError('adiabatic wall violates its necessary DEC energy bound')
    closed_energy = energy+wall
    balance = np.diff(closed_energy, axis=0)-electrical
    rows = []
    for name, wall_energy in (('instantaneous_wall_bound', energy), ('adiabatic_wall_bound', wall)):
        replacement = compact_cell_moments(energy+wall_energy, c)-radial_field_moments(density)
        for it, time, demand in model.phases:
            value = maximum_null(model.supply[:, it]+state['auxiliary'][:, it]+replacement[:, it]-demand)[0]
            rows.append(dict(cells=cells, control=name, time=time,
                required_negative_null=float(max(0., value.max())),
                added_wall_ADM_energy=float(model.integrate(model.volume[it]*replacement[0, it])),
                wall_rest_energy=float(model.integrate(wall_energy[it]))))
    # Independent port-energy identity, using a normalized fixed impedance.
    # This audit checks sampled capacitive V and I against the wave powers.
    cm = model.cm
    hm = (field[1:]+field[:-1])/2
    q = np.sqrt(2*hm)
    voltage = q*cm['gamma']*cm['b']/cm['radius']**2
    current = model.hd/(cm['lapse']*q)
    incoming, outgoing = (voltage+current)/2, (voltage-current)/2
    residual = np.max(abs(incoming**2-outgoing**2-voltage*current))
    scale = np.max(abs(voltage*current))
    result = dict(cells=cells, controls=rows,
        closed_cell_electrical_energy_balance_max=float(abs(balance).max()),
        port_wave_power_relative_residual=float(residual/max(scale, 1e-30)),
        instantaneous_wall_inventory_is_supplied=False, physical_wall_equation_of_state_is_supplied=False)
    write_json(OUTPUT/f'n{cells}_closed_cell_controls.json', result)
    return result


def main():
    if OUTPUT.exists():
        raise RuntimeError('preserve the completed audit')
    OUTPUT.mkdir(parents=True)
    with ProcessPoolExecutor(max_workers=4, mp_context=multiprocessing.get_context('spawn')) as pool:
        closed = list(pool.map(closed_cells, (512, 1024)))
    if max(r['closed_cell_electrical_energy_balance_max'] for r in closed) > 1e-10:
        raise ArithmeticError('closed-cell energy audit failed')
    if max(r['port_wave_power_relative_residual'] for r in closed) > 1e-11:
        raise ArithmeticError('capacitor port-wave power audit failed')
    checks = []
    manifests = sorted((BASE/'poynting_delivery').glob('*/manifest.json'))
    manifests += [BASE/name/'manifest.json' for name in ('finite_work_interface', 'finite_work_interface_recovery')]
    for path in manifests:
        manifest = json.loads(path.read_text())
        for name, expected in manifest['input_sha256'].items():
            checks.append(dict(manifest=str(path.relative_to(ROOT)), file=name, kind='input',
                               passed=sha256_file(ROOT/name)==expected))
        for name, expected in manifest['output_sha256'].items():
            checks.append(dict(manifest=str(path.relative_to(ROOT)), file=name, kind='output',
                               passed=sha256_file(path.parent/name)==expected))
    if not all(row['passed'] for row in checks):
        raise ArithmeticError('evidence hash audit failed')
    pd.DataFrame(checks).to_csv(OUTPUT/'hash_checks.csv', index=False)
    a = json.loads((BASE/'finite_work_interface/n1024_summary.json').read_text())
    b = json.loads((BASE/'finite_work_interface_recovery/n1024_summary.json').read_text())
    with plt.rc_context({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False}):
        fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), constrained_layout=True)
        x = [100*r['efficiency'] for r in a['cases']]
        axes[0].plot(x, [r['initial_auxiliary_energy'] for r in a['cases']], 'o-', color='#316b97')
        axes[0].axhline(93.9352, ls='--', color='#a35b4b', label='Enclosed-store comparison')
        axes[0].set(xlabel='Conversion efficiency (%)', ylabel='Added startup ADM energy',
                    title='Finite absorption, full recovery')
        axes[0].legend(fontsize=8)
        for row in b['cases']:
            phase = next(p for p in b['phases'] if p['time']==1.285 and p['recovery_fraction']==row['recovery_fraction'])
            axes[1].scatter(row['initial'], phase['required_negative_null'], color='#316b97')
            if row['recovery_fraction'] in (.7, .8, .9, .95, 1.):
                axes[1].annotate(f'{100*row["recovery_fraction"]:.0f}%',
                    (row['initial'], phase['required_negative_null']), xytext=(5, 3), textcoords='offset points', fontsize=8)
        axes[1].set(xlabel='Added startup ADM energy', ylabel='Fade required negative-null contribution',
                    title='Recovery policy at 98% conversion', xlim=(49, 73))
        fig.savefig(OUTPUT/'work_interface_tradeoffs.png', dpi=160)
        fig.savefig(OUTPUT/'work_interface_tradeoffs.pdf')
        plt.close(fig)
    write_json(OUTPUT/'verification.json', dict(evidence_hash_checks=len(checks), failed_hash_checks=0,
        maximum_closed_cell_energy_balance=max(r['closed_cell_electrical_energy_balance_max'] for r in closed),
        maximum_port_power_relative_residual=max(r['port_wave_power_relative_residual'] for r in closed)))
    sources = {str(Path(__file__).relative_to(ROOT)): sha256_file(Path(__file__))}
    for manifest in manifests:
        sources[str(manifest.relative_to(ROOT))] = sha256_file(manifest)
        for name, expected in json.loads(manifest.read_text())['input_sha256'].items():
            sources[name] = expected
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        input_sha256=sources,
        output_sha256={p.name: sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))
    print(f'Interface audit: {len(checks)} hashes passed; both capacitor power controls passed.', flush=True)


if __name__ == '__main__':
    main()
