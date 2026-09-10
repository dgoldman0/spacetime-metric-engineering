#!/usr/bin/env python3
"""Bounded parallel finite-inventory and necessary-stress converter evaluation."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess
import sys

import numpy as np
import pandas as pd

from adm_harness.active_transfer_reservoir import TabulatedActiveMedium, divergence_projections
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.pressure_linked_storage import fluid_coefficients, fluid_moments
from adm_harness.regenerative_converter import (
    compact_cell_moments, conversion_ports, finite_local_stores,
    isotropic_wall_energy, proper_prefix, work_reserve_lower_bound,
)
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/'supporting_reports/data'
OUTPUT = BASE/'regenerative_converter'
HISTORIES = {
    'refined': BASE/'pressure_linked_storage/retained_coefficients/powered_finite_joint',
    'coarse': BASE/'pressure_linked_storage/conversion_controls/powered_finite_n64',
}
LIGHT_SPEED = 299792458.
# Manufacturer Technical Data 10339, July 2020, lighter threaded-cell mass.
BENCHMARK = dict(name='Eaton XL60-3R0308T-R', capacitance_F=3000., voltage_V=3., mass_kg=.515,
    source_url='https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-xl60-supercapacitors-cylindrical-cells-data-sheet.pdf',
    source_date='2020-07', accessed_date='2026-09-10')
BENCHMARK['rated_energy_J'] = .5*BENCHMARK['capacitance_F']*BENCHMARK['voltage_V']**2
BENCHMARK['specific_energy_J_per_kg'] = BENCHMARK['rated_energy_J']/BENCHMARK['mass_kg']
BENCHMARK['cold_mass_energy_per_rated_energy'] = LIGHT_SPEED**2/BENCHMARK['specific_energy_J_per_kg']


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def independent_cell_check(model, times, positions, mass):
    """Independent covariant divergence of bilinear complete-cell inventories."""
    rows = []
    for i in np.unique(np.linspace(0, len(times)-2, 13).astype(int)):
        for j in np.unique(np.linspace(0, len(positions)-2, 13).astype(int)):
            t, x = (times[i]+times[i+1])/2, (positions[j]+positions[j+1])/2
            dt, dx = times[i+1]-times[i], positions[j+1]-positions[j]

            def energy(tt, xx):
                a, b = (tt-times[i])/dt, (xx-positions[j])/dx
                return ((1-a)*((1-b)*mass[i, j]+b*mass[i, j+1])
                        +a*((1-b)*mass[i+1, j]+b*mass[i+1, j+1]))

            def tensor(tt, xx):
                c = fluid_coefficients(model, np.array([tt]), np.array([xx]))
                return compact_cell_moments(energy(tt, xx), c)[:, 0]

            eps = min(1e-5, dt/100, dx/100)
            g = model.metric(t, np.array([x]))
            p, f = divergence_projections(g, tensor(t, x),
                (tensor(t+eps, x)-tensor(t-eps, x))/(2*eps),
                (tensor(t, x+eps)-tensor(t, x-eps))/(2*eps))
            c = fluid_coefficients(model, np.array([t]), np.array([x]))
            scalar = lambda key: float(c[key][0, 0])
            rest_power = scalar('gamma')*(p[0]-scalar('v')*f[0])
            rest_force = scalar('gamma')*(f[0]-scalar('v')*p[0])
            mt = .5*(mass[i+1, j]+mass[i+1, j+1]-mass[i, j]-mass[i, j+1])/dt
            reduced_power = mt/(scalar('lapse')*scalar('rest_volume'))
            reduced_force = energy(t, x)/scalar('rest_volume')*scalar('acceleration')
            endpoint_power = scalar('gamma')*(scalar('power')-scalar('v')*scalar('normal_force'))
            rows.append(dict(s=t, x=x, covariant_power=float(rest_power), reduced_power=reduced_power,
                power_identity_residual=float(rest_power-reduced_power),
                force_identity_residual=float(rest_force-reduced_force),
                endpoint_power=endpoint_power, matched_energy_residual=float(rest_power-endpoint_power)))
    frame = pd.DataFrame(rows)
    return frame, dict(points=len(frame),
        maximum_power_identity_residual=float(abs(frame.power_identity_residual).max()),
        maximum_force_identity_residual=float(abs(frame.force_identity_residual).max()),
        maximum_matched_energy_residual=float(abs(frame.matched_energy_residual).max()),
        matched_energy_sum_relative_residual=float(abs(frame.matched_energy_residual).sum()
            /max(1e-30, abs(frame.covariant_power).sum()+abs(frame.endpoint_power).sum())))


def run_case(spec):
    history, efficiency, recovery, voltage_fraction = spec
    label = f'{history}_eta{round(efficiency*100):03d}_recovery{round(recovery*100):03d}_voltage{round(voltage_fraction*100):03d}'
    path = HISTORIES[history]
    with np.load(str(path)+'_states.npz') as z:
        state = {key: z[key] for key in z.files}
    t, x, h = state['t'], state['x'], state['flux_energy']
    model = TabulatedActiveMedium(BASE/'active_transfer_reservoir/metric_fine.npz',
                                  BASE/'active_transfer_reservoir/medium_baseline.npz')
    tm, dt = (t[1:]+t[:-1])/2, np.diff(t)[:, None]
    c = fluid_coefficients(model, tm, x)
    charging = np.diff(h, axis=0)/(dt*c['lapse']*c['radius']**4)
    net = -c['gamma']*(c['power']-c['v']*c['normal_force'])
    proper_weight = c['lapse']*c['rest_volume']
    ports = conversion_ports(charging, net, efficiency=efficiency, recovery=recovery)
    stores = finite_local_stores(t, proper_weight, ports['bank_output'], ports['receiver_input'],
                                voltage_fraction=voltage_fraction)
    bound = work_reserve_lower_bound(t, proper_weight, charging, efficiency=efficiency,
                                    voltage_fraction=voltage_fraction)
    integrate_x = lambda array: 4*np.pi*np.trapezoid(array, x, axis=-1)
    throughput = lambda power: float(integrate_x(np.sum(proper_weight*power*dt, axis=0)))
    total = stores['bank']+stores['heat']
    wall = isotropic_wall_energy(stores['bank_capacity'], stores['heat_capacity'])
    cold_lower = BENCHMARK['cold_mass_energy_per_rated_energy']*bound['bank_capacity']
    cold_actual = BENCHMARK['cold_mass_energy_per_rated_energy']*stores['bank_capacity']
    energy_models = {
        'inventory_only': total,
        'isotropic_wall_bound': total+wall,
        'benchmark_bank_mass_only': np.broadcast_to(cold_actual, total.shape),
        'any_recovery_bank_mass_lower_bound': np.broadcast_to(cold_lower, total.shape),
    }
    tensors = {name: compact_cell_moments(energy, state) for name, energy in energy_models.items()}
    actual = fluid_moments(state['thermal'], h, state['number'], state)
    endpoint_force = state['gamma']*(state['normal_force']-state['v']*state['power'])
    summary = dict(case=label, history=history, efficiency=efficiency, recovery=recovery,
        voltage_fraction=voltage_fraction, cells=len(x)-1, intervals=len(t)-1,
        charging_work=throughput(np.maximum(charging, 0.)),
        available_discharge_work=throughput(np.maximum(-charging, 0.)),
        recovered_work=throughput(ports['recovered_work']), converter_loss=throughput(ports['converter_loss']),
        net_endpoint_work=throughput(net),
        heat_return=throughput(np.maximum(-ports['endpoint_heat'], 0.)),
        heat_supply=throughput(np.maximum(ports['endpoint_heat'], 0.)),
        heat_receiver_gain=throughput(np.maximum(ports['receiver_input'], 0.)),
        heat_receiver_release=throughput(np.maximum(-ports['receiver_input'], 0.)),
        bank_capacity=float(integrate_x(stores['bank_capacity'])),
        bank_initial=float(integrate_x(stores['bank_initial'])),
        heat_capacity=float(integrate_x(stores['heat_capacity'])),
        heat_initial=float(integrate_x(stores['heat_initial'])),
        initial_work_lower_bound_any_recovery=float(integrate_x(bound['initial_work'])),
        bank_capacity_lower_bound_any_recovery=float(integrate_x(bound['bank_capacity'])),
        maximum_rest_bank_power=float(abs(ports['bank_output']).max()),
        maximum_rest_receiver_power=float(abs(ports['receiver_input']).max()),
        minimum_packet_gap=float((abs(x[None, :]-t[:, None])-.35).min()),
        maximum_prescribed_velocity=float(abs(state['v']).max()),
        port_identity_residual=float(abs(ports['bank_output']-ports['receiver_input']-net).max()),
        store_energy_identity_residual=float(abs(total-total[0]+proper_prefix(t, proper_weight, net)).max()),
        bank_minimum_voltage_residual=float(abs(stores['bank'].min(axis=0)-voltage_fraction**2*stores['bank_capacity']).max()),
        minimum_thermal_inventory=float(stores['heat'].min()))

    source_rows, source_summaries = [], []
    archived = pd.read_csv(str(path)+'_points.csv')
    keys = ('rho', 'pr', 'j', 'pt')
    for time, frame in archived.groupby('s', sort=True):
        i = int(np.argmin(abs(t-time)))
        if abs(t[i]-time) > 1e-12 or not np.allclose(frame.l, x, rtol=0, atol=1e-12):
            raise RuntimeError('archived geometry and material grid mismatch')
        demand = frame[['geometry_'+k for k in keys]].to_numpy().T
        endpoint = frame[['endpoint_'+k for k in keys]].to_numpy().T
        old_supply = frame[['supply_'+k for k in keys]].to_numpy().T
        if not np.allclose(actual[:, i], old_supply, rtol=1e-10, atol=1e-12):
            raise RuntimeError('archived supply reconstruction mismatch')
        baseline = np.maximum(0., maximum_null(actual[:, i]+endpoint-demand)[0])
        for name, tensor in tensors.items():
            negative, direction = maximum_null(actual[:, i]+tensor[:, i]-demand)
            negative = np.maximum(0., negative)
            remainder = maximum_null(tensor[:, i]-endpoint)[0]
            energy = float(integrate_x(state['b'][i]*state['radius'][i]**2*tensor[0, i]))
            source_summaries.append(dict(s=float(time), model=name, required_negative_null=float(negative.max()),
                baseline_required_negative_null=float(baseline.max()), auxiliary_slice_energy=energy,
                required_negative_null_of_endpoint_remainder=float(max(0., remainder.max()))))
            for j, position in enumerate(x):
                source_rows.append(dict(s=float(time), x=float(position), model=name,
                    baseline_required_negative_null=float(baseline[j]), required_negative_null=float(negative[j]),
                    worst_direction=float(direction[j]), auxiliary_rho=float(tensor[0, i, j]),
                    endpoint_rho=float(endpoint[0, j]), geometry_rho=float(demand[0, j]),
                    endpoint_remainder_required_negative_null=float(max(0., remainder[j]))))
    summary['phases'] = source_summaries
    for name, energy in energy_models.items():
        rho = energy/state['rest_volume']
        summary[name+'_maximum_holding_force'] = float(abs(rho*state['acceleration']).max())
        summary[name+'_maximum_endpoint_force_remainder'] = float(abs(endpoint_force-rho*state['acceleration']).max())
        summary[name+'_maximum_auxiliary_null'] = float(maximum_null(tensors[name])[0].max())
    unit_mass = compact_cell_moments(np.broadcast_to(bound['bank_capacity'], total.shape), state)
    unit_peak = float(maximum_null(unit_mass)[0].max())
    supplied_peak = float(maximum_null(actual)[0].max())
    summary['specific_energy_for_bank_mass_null_to_equal_previous_supply_peak_J_per_kg'] = LIGHT_SPEED**2*unit_peak/supplied_peak
    summary['benchmark_mass_lower_null_over_previous_supply_peak'] = BENCHMARK['cold_mass_energy_per_rated_energy']*unit_peak/supplied_peak

    if efficiency == .98 and recovery == 1. and voltage_fraction == .5:
        checks, metrics = independent_cell_check(model, t, x, total+wall)
        checks.to_csv(OUTPUT/(label+'_covariant_checks.csv'), index=False)
        summary['covariant_checks'] = metrics
    write_json(OUTPUT/(label+'_summary.json'), summary)
    pd.DataFrame(source_rows).to_csv(OUTPUT/(label+'_source.csv'), index=False)
    pd.DataFrame(dict(s=t, bank_rest_energy=integrate_x(stores['bank']),
        heat_rest_energy=integrate_x(stores['heat']), wall_rest_energy=np.full_like(t, integrate_x(wall)),
        recovered_work_prefix=integrate_x(proper_prefix(t, proper_weight, ports['recovered_work'])),
        converter_loss_prefix=integrate_x(proper_prefix(t, proper_weight, ports['converter_loss']))
        )).to_csv(OUTPUT/(label+'_inventories.csv'), index=False)
    np.savez_compressed(OUTPUT/(label+'_states.npz'), t=t, x=x, s_midpoint=tm,
        **stores, **ports, initial_work_lower_bound=bound['initial_work'],
        bank_capacity_lower_bound=bound['bank_capacity'], isotropic_wall_energy=wall)
    print(f'{label}: bank capacity {summary["bank_capacity"]:.6g}; heat capacity {summary["heat_capacity"]:.6g}; '
          f'loss {summary["converter_loss"]:.6g}', flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('positive worker count required')
    if OUTPUT.exists():
        raise RuntimeError('output directory already exists; retain the completed stage')
    sources = [Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/regenerative_converter.py',
        ROOT/'toolkit/adm_harness_cli/tests/test_regenerative_converter.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/pressure_linked_storage.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/graded_electrothermal.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/active_transfer_reservoir.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/source_ledger.py',
        ROOT/'supporting_reports/REGENERATIVE_CONVERTER_EVALUATION.md',
        BASE/'active_transfer_reservoir/metric_fine.npz', BASE/'active_transfer_reservoir/medium_baseline.npz']
    input_audit = []
    for path in HISTORIES.values():
        manifest_path = path.parent/'manifest.json'
        manifest = json.loads(manifest_path.read_text())
        sources.append(manifest_path)
        for suffix in ('_states.npz', '_points.csv'):
            item = Path(str(path)+suffix)
            expected = manifest['output_sha256'][item.name]
            if sha256_file(item) != expected:
                raise RuntimeError('archived input integrity failure: '+str(item))
            sources.append(item)
            input_audit.append(dict(path=str(item.relative_to(ROOT)), sha256=expected, verified=True))
    before = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    OUTPUT.mkdir(parents=True)
    specs = [(history, eta, recovery, .5) for history in HISTORIES
             for eta in (1., .98, .95) for recovery in (0., 1.)]
    specs += [(history, 1., 1., 0.) for history in HISTORIES]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(run_case, specs))
    after = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    if before != after:
        raise RuntimeError('source/input changed during production')
    write_json(OUTPUT/'hardware_benchmark.json', BENCHMARK)
    pd.DataFrame([{k: v for k, v in result.items() if not isinstance(v, (dict, list))}
                  for result in results]).to_csv(OUTPUT/'comparison.csv', index=False)
    phase_rows = [dict(case=result['case'], **phase) for result in results for phase in result['phases']]
    pd.DataFrame(phase_rows).to_csv(OUTPUT/'phase_comparison.csv', index=False)
    metadata = dict(completed_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        git_revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        python_version=sys.version, python_executable=sys.executable,
        numpy_version=np.__version__, cases=len(results), archived_inputs_verified=input_audit,
        software_and_input_sha256=before, source_input_hashes_unchanged=before == after,
        output_sha256={str(p.relative_to(OUTPUT)): sha256_file(p) for p in OUTPUT.iterdir() if p.is_file()})
    write_json(OUTPUT/'manifest.json', metadata)


if __name__ == '__main__':
    main()
