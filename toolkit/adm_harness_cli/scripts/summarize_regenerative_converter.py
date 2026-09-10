#!/usr/bin/env python3
"""Quadrature controls, numeric integrity, and converter inventory figures."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import multiprocessing

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from adm_harness.active_transfer_reservoir import TabulatedActiveMedium
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.pressure_linked_storage import fluid_coefficients
from adm_harness.regenerative_converter import (
    compact_cell_moments, conversion_ports, finite_local_stores, isotropic_wall_energy,
    work_reserve_lower_bound,
)
from adm_harness.source_ledger import sha256_file
from run_regenerative_converter import HISTORIES, BENCHMARK, BASE, ROOT, OUTPUT

DERIVED = OUTPUT/'derived'
FIGURES = ROOT/'supporting_reports/figures'


def quadrature_case(task):
    history, factor = task
    path = HISTORIES[history]
    with np.load(str(path)+'_states.npz') as z:
        state = {key: z[key] for key in z.files}
    oldt, x, h = state['t'], state['x'], state['flux_energy']
    t = np.r_[np.concatenate([np.linspace(a, b, factor+1)[:-1] for a, b in zip(oldt[:-1], oldt[1:])]), oldt[-1]]
    tm, dt = (t[1:]+t[:-1])/2, np.diff(t)[:, None]
    model = TabulatedActiveMedium(BASE/'active_transfer_reservoir/metric_fine.npz',
                                  BASE/'active_transfer_reservoir/medium_baseline.npz')
    c = fluid_coefficients(model, tm, x)
    # Preserve the actual archived piecewise-linear H; refine only integration.
    ht = np.repeat(np.diff(h, axis=0)/np.diff(oldt)[:, None], factor, axis=0)
    charging = ht/(c['lapse']*c['radius']**4)
    net = -c['gamma']*(c['power']-c['v']*c['normal_force'])
    weight = c['lapse']*c['rest_volume']
    integrate = lambda v: float(4*np.pi*np.trapezoid(v, x))
    throughput = lambda v: integrate(np.sum(weight*v*dt, axis=0))
    points = pd.read_csv(str(path)+'_points.csv')
    fade = points[abs(points.s-oldt[-1]) < 1e-12]
    keys = ('rho', 'pr', 'j', 'pt')
    supply = fade[['supply_'+k for k in keys]].to_numpy().T
    demand = fade[['geometry_'+k for k in keys]].to_numpy().T
    cfinal = {key: state[key][-1] for key in ('rest_volume', 'gamma', 'v')}
    rows = []
    for efficiency, voltage_fraction in ((1., 0.), (.98, .5)):
        ports = conversion_ports(charging, net, efficiency=efficiency, recovery=1.)
        stores = finite_local_stores(t, weight, ports['bank_output'], ports['receiver_input'],
                                    voltage_fraction=voltage_fraction)
        bound = work_reserve_lower_bound(t, weight, charging, efficiency=efficiency,
                                        voltage_fraction=voltage_fraction)
        cold = bound['bank_capacity']*BENCHMARK['cold_mass_energy_per_rated_energy']
        wall = isotropic_wall_energy(stores['bank_capacity'], stores['heat_capacity'])
        formal = compact_cell_moments(stores['bank'][-1]+stores['heat'][-1]+wall, cfinal)
        hardware = compact_cell_moments(cold, cfinal)
        rows.append(dict(history=history, temporal_subdivision=factor, efficiency=efficiency,
            voltage_fraction=voltage_fraction, charging_work=throughput(np.maximum(charging, 0.)),
            discharge_work=throughput(np.maximum(-charging, 0.)),
            converter_loss=throughput(ports['converter_loss']),
            bank_initial=integrate(stores['bank_initial']), bank_capacity=integrate(stores['bank_capacity']),
            heat_initial=integrate(stores['heat_initial']), heat_capacity=integrate(stores['heat_capacity']),
            initial_work_lower_bound_any_recovery=integrate(bound['initial_work']),
            bank_capacity_lower_bound_any_recovery=integrate(bound['bank_capacity']),
            hardware_negative_null_lower_bound_at_fade=float(maximum_null(supply+hardware-demand)[0].max()),
            isotropic_wall_control_negative_null_at_fade=float(maximum_null(supply+formal-demand)[0].max())))
    return rows


def verify_production():
    manifest = json.loads((OUTPUT/'manifest.json').read_text())
    rows = []
    for relative, expected in manifest['output_sha256'].items():
        rows.append(dict(kind='production_output', path=relative,
                         match=sha256_file(OUTPUT/relative) == expected))
    # The manually maintained report advances after production; its original
    # registration is retained in the recorded source revision.
    for relative, expected in manifest['software_and_input_sha256'].items():
        if relative.endswith('REGENERATIVE_CONVERTER_EVALUATION.md'):
            import hashlib
            import subprocess
            original = subprocess.check_output(['git', 'show', manifest['git_revision']+':'+relative], cwd=ROOT)
            actual = hashlib.sha256(original).hexdigest()
        else:
            actual = sha256_file(ROOT/relative)
        rows.append(dict(kind='production_source_or_input', path=relative, match=actual == expected))
    frame = pd.DataFrame(rows)
    frame.to_csv(DERIVED/'integrity.csv', index=False)
    if not frame.match.all():
        raise RuntimeError('production integrity mismatch')
    return len(frame)


def main():
    if DERIVED.exists():
        raise RuntimeError('derived output already exists; retain the completed audit')
    DERIVED.mkdir()
    hashes = {str(p.relative_to(ROOT)): sha256_file(p) for p in (
        Path(__file__), Path(__file__).with_name('run_regenerative_converter.py'),
        ROOT/'toolkit/adm_harness_cli/adm_harness/regenerative_converter.py', OUTPUT/'manifest.json')}
    with ProcessPoolExecutor(max_workers=4, mp_context=multiprocessing.get_context('spawn')) as pool:
        groups = list(pool.map(quadrature_case, [(name, factor) for name in HISTORIES for factor in (2, 4)]))
    quadrature = pd.DataFrame([row for group in groups for row in group])
    quadrature.to_csv(DERIVED/'quadrature.csv', index=False)
    count = verify_production()

    case = 'refined_eta098_recovery100_voltage050'
    inventory = pd.read_csv(OUTPUT/(case+'_inventories.csv'))
    source = pd.read_csv(OUTPUT/(case+'_source.csv'))
    source = source[source.s == source.s.max()]
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.6), constrained_layout=True)
    axes[0].plot(inventory.s, inventory.bank_rest_energy, label='Electrical bank')
    axes[0].plot(inventory.s, inventory.heat_rest_energy, label='Thermal receiver')
    axes[0].plot(inventory.s, inventory.wall_rest_energy, label='Enclosure energy bound', linestyle=':')
    axes[0].set(xlabel='Active time s', ylabel='Integrated local rest energy (model units)',
                title='Finite inventories, 98% conversion, full recovery')
    axes[0].legend(fontsize=9)
    inv = source[source.model == 'inventory_only']
    walls = source[source.model == 'isotropic_wall_bound']
    axes[1].plot(inv.x, inv.baseline_required_negative_null, label='Previous interface estimate', color='black')
    axes[1].plot(inv.x, inv.required_negative_null, label='Finite inventory only')
    axes[1].plot(walls.x, walls.required_negative_null, label='With enclosure energy bound')
    axes[1].set(xlabel='Rail coordinate x', ylabel='Required negative null contribution',
                title='Formal small-cell source screen at fade')
    axes[1].legend(fontsize=9)
    for ax in axes:
        ax.grid(alpha=.2)
    fig.suptitle('Field-energy control; physical converters and supporting material remain open', fontsize=11)
    paths = []
    for suffix in ('png', 'pdf'):
        path = FIGURES/('regenerative_converter_inventory.'+suffix)
        fig.savefig(path, dpi=180)
        paths.append(path)
    plt.close(fig)
    for relative, expected in hashes.items():
        if sha256_file(ROOT/relative) != expected:
            raise RuntimeError('postprocessing source changed during evaluation')
    paths += [p for p in DERIVED.iterdir() if p.is_file()]
    (DERIVED/'manifest.json').write_text(json.dumps(dict(completed_utc=datetime.now(timezone.utc).isoformat(),
        production_integrity_comparisons=count, source_sha256=hashes,
        output_sha256={str(p.relative_to(ROOT)): sha256_file(p) for p in paths}), indent=2)+'\n')
    print(quadrature.to_string(index=False))
    print(f'Production integrity comparisons: {count}')


if __name__ == '__main__':
    main()
