#!/usr/bin/env python3
"""Parallel bounded comparison of finite work routes on the pinned active history."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

import numpy as np
import pandas as pd

from adm_harness.active_transfer_reservoir import TabulatedActiveMedium
from adm_harness.pressure_linked_storage import fluid_coefficients, fluid_moments
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.poynting_delivery import propagate, wave_moments, guide_energy_bound
from adm_harness.regenerative_converter import compact_cell_moments
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/'supporting_reports/data'
INPUT = BASE/'pressure_linked_storage/retained_coefficients/powered_finite_joint'
STORES = BASE/'regenerative_converter/refined_eta098_recovery100_voltage050_states.npz'
ETA = .98


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


class DeliveryHistory:
    def __init__(self, cells, temporal_factor=1):
        self.model = TabulatedActiveMedium(BASE/'active_transfer_reservoir/metric_fine.npz',
                                          BASE/'active_transfer_reservoir/medium_baseline.npz')
        with np.load(str(INPUT)+'_states.npz') as z:
            self.state = {key: z[key] for key in z.files}
        st = self.state
        self.edges = np.linspace(st['x'][0], st['x'][-1], cells+1)
        self.x = (self.edges[1:]+self.edges[:-1])/2
        self.dt = np.diff(st['t'])
        self.hdot = np.diff(st['flux_energy'], axis=0)/self.dt[:, None]
        self.t = np.r_[np.concatenate([np.linspace(a, b, temporal_factor+1)[:-1]
                         for a, b in zip(st['t'][:-1], st['t'][1:])]), st['t'][-1]]
        self.interval_map = np.repeat(np.arange(len(self.dt)), temporal_factor)
        self.cache = {}

    def spatial(self, array):
        return np.array([np.interp(self.x, self.state['x'], row) for row in np.atleast_2d(array)])

    def interpolate_state(self, array):
        at_x = self.spatial(array)
        return np.array([np.interp(self.t, self.state['t'], col) for col in at_x.T]).T

    def geometry(self, t):
        key = round(t, 13)
        if key not in self.cache:
            g = self.model.metric(t, self.x)
            edge = self.model.metric(t, self.edges)
            v = g.b*g.beta/g.alpha
            self.cache[key] = g, edge, v
        return self.cache[key]

    def coefficients(self, direction, assignment, purpose):
        def evaluate(t, interval):
            g, edge, v = self.geometry(t)
            hd = np.interp(self.x, self.state['x'], self.hdot[self.interval_map[interval]])
            drive = np.maximum(hd, 0)/ETA if purpose == 'absorption' else ETA*np.maximum(-hd, 0)
            # alpha*B*R^2*q/[Gamma(1-direction*v)] after substituting q.
            source = g.b*drive*assignment/(g.radius**2*(1-direction*v))
            return (-edge.beta+direction*edge.alpha/edge.b,
                    g.alpha*g.k_l-direction*g.alpha_x/g.b, source)
        return evaluate


def run_case(spec):
    route, cells, temporal_factor, output = spec
    output = Path(output)
    label = f'{route}_n{cells}_t{temporal_factor}'
    h = DeliveryHistory(cells, temporal_factor)
    x, t, dx = h.x, h.t, h.edges[1]-h.edges[0]
    c = fluid_coefficients(h.model, t, x)
    volume = c['b']*c['radius']**2
    if route == 'left':
        plus = np.ones_like(x)
    elif route == 'right':
        plus = np.zeros_like(x)
    elif route == 'split':
        plus = (x < -.5*(2.1+.5)).astype(float)
    else:
        raise ValueError('registered route required')
    integrate = lambda a: 4*np.pi*dx*np.sum(a, axis=-1)
    waves, ledgers, streams = {}, [], []
    for direction, assignment in ((1, plus), (-1, 1-plus)):
        for purpose in ('absorption', 'recovery'):
            sign = direction if purpose == 'absorption' else -direction
            key = f'{purpose}_{direction:+d}'
            state, ledger = propagate(t, h.edges, h.coefficients(sign, assignment, purpose),
                                      backwards=purpose == 'absorption')
            mu = state/volume
            waves[key] = mu
            for row in ledger:
                row.update(stream=key, propagation_direction=sign)
            ledgers.extend(ledger)
            integral = lambda term: float(4*np.pi*sum(row[term] for row in ledger))
            streams.append(dict(stream=key, propagation_direction=sign,
                initial_slice_energy=float(integrate(state[0])), final_slice_energy=float(integrate(state[-1])),
                boundary_energy=float(-integral('boundary')),
                geometric_energy=float((-1 if purpose == 'absorption' else 1)*integral('geometric')),
                exchanged_ADM_energy=integral('source'),
                balance_residual_max=float(max(abs(row['balance_residual']) for row in ledger))))
    mu_plus = waves['absorption_+1']+waves['recovery_-1']
    mu_minus = waves['absorption_-1']+waves['recovery_+1']
    wave = wave_moments(mu_plus, mu_minus)
    rest_waves = {}
    for item in streams:
        key, sign = item['stream'], item['propagation_direction']
        rest_waves[key] = waves[key]*c['gamma']**2*(1-sign*c['v'])**2
    with np.load(STORES) as z:
        heat = h.interpolate_state(z['heat'])
        heat_capacity = h.spatial(z['heat_capacity'])[0]
    thermal_cells = compact_cell_moments(heat+heat_capacity[None, :]/3, c)
    supply = fluid_moments(h.interpolate_state(h.state['thermal']),
                          h.interpolate_state(h.state['flux_energy']),
                          h.spatial(h.state['number'])[0], c)
    tensors = {'wave_and_heat_bound': wave+thermal_cells}
    guides, guide_data = {}, []
    for speed in (.2, .5, .8):
        local = sum(guide_energy_bound(w, speed) for w in rest_waves.values())
        flux = sum(float(np.max(guide_energy_bound(w, speed)*c['radius']**4)) for w in rest_waves.values())
        constant = flux/c['radius']**4
        for kind, energy in (('local_bound', local), ('constant_flux', constant)):
            name = f'guide_{kind}_v{round(100*speed):03d}'
            guides[name] = energy
            tensors[name] = wave+thermal_cells+np.array([energy, -energy, np.zeros_like(energy), energy])
            guide_data.append(dict(model=name, drift_comparison=speed,
                initial_guide_slice_energy=float(integrate(volume[0]*energy[0])),
                maximum_guide_slice_energy=float(integrate(volume*energy).max()),
                maximum_guide_density=float(energy.max()),
                maximum_left_end_traction=float(energy[:, 0].max()),
                maximum_right_end_traction=float(energy[:, -1].max()),
                flux_energy_constant=flux if kind == 'constant_flux' else None))
    archived = pd.read_csv(str(INPUT)+'_points.csv')
    phases, source_rows = [], []
    for time, frame in archived.groupby('s'):
        it = int(np.argmin(abs(t-time)))
        if abs(t[it]-time) > 1e-11:
            raise RuntimeError('missing archived tensor phase')
        demand = np.array([np.interp(x, frame.l, frame['geometry_'+k]) for k in ('rho', 'pr', 'j', 'pt')])
        endpoint = np.array([np.interp(x, frame.l, frame['endpoint_'+k]) for k in ('rho', 'pr', 'j', 'pt')])
        baseline = float(maximum_null(supply[:, it]+endpoint-demand)[0].max())
        for name, tensor in tensors.items():
            negative, direction = maximum_null(supply[:, it]+tensor[:, it]-demand)
            remainder = maximum_null(tensor[:, it]-endpoint)[0]
            phases.append(dict(s=float(time), model=name,
                required_negative_null=float(max(0, negative.max())),
                baseline_required_negative_null=baseline,
                auxiliary_slice_energy=float(integrate(volume[it]*tensor[0, it])),
                endpoint_remainder_negative_null=float(max(0, remainder.max()))))
            for j, xx in enumerate(x):
                source_rows.append(dict(s=float(time), model=name, x=float(xx),
                    required_negative_null=float(max(0, negative[j])), worst_direction=float(direction[j]),
                    auxiliary_rho=float(tensor[0, it, j])))
    tm = (t[1:]+t[:-1])/2
    cm = fluid_coefficients(h.model, tm, x)
    hd = h.spatial(h.hdot[h.interval_map])
    charge = np.maximum(hd, 0)/(ETA*cm['lapse']*cm['radius']**4)
    recovery = ETA*np.maximum(-hd, 0)/(cm['lapse']*cm['radius']**4)
    tap_force_on_route = -(2*plus[None, :]-1)*(charge+recovery)
    heat_force = (.5*(heat[1:]+heat[:-1])+heat_capacity[None, :]/3)/cm['rest_volume']*cm['acceleration']
    endpoint_force = cm['gamma']*(cm['normal_force']-cm['v']*cm['power'])
    total_wave = mu_plus+mu_minus
    summary = dict(case=label, route=route, cells=cells, temporal_factor=temporal_factor,
        efficiency=ETA, streams=streams, guides=guide_data, phases=phases,
        initial_wave_slice_energy=float(integrate(volume[0]*total_wave[0])),
        initial_wave_material_inventory=float(integrate(volume[0]*c['gamma'][0]
            *((1-c['v'][0])*mu_plus[0]+(1+c['v'][0])*mu_minus[0]))),
        maximum_wave_slice_energy=float(integrate(volume*total_wave).max()),
        final_wave_slice_energy=float(integrate(volume[-1]*total_wave[-1])),
        peak_wave_null=float(maximum_null(wave)[0].max()),
        absorbed_boundary_energy=sum(row['boundary_energy'] for row in streams if 'absorption' in row['stream']),
        recovered_boundary_energy=sum(row['boundary_energy'] for row in streams if 'recovery' in row['stream']),
        heat_capacity=float(integrate(heat_capacity)), heat_initial=float(integrate(heat[0])),
        maximum_tap_force=float(abs(tap_force_on_route).max()),
        maximum_heat_holding_force=float(abs(heat_force).max()),
        maximum_endpoint_force_remainder=float(abs(endpoint_force-heat_force-tap_force_on_route).max()),
        minimum_packet_gap=float(abs(h.edges[-1]-t[0])-.35),
        maximum_prescribed_material_velocity=float(abs(c['v']).max()),
        maximum_wave_density=float(total_wave.max()))
    pd.DataFrame(ledgers).to_csv(output/(label+'_balance.csv'), index=False)
    pd.DataFrame(source_rows).to_csv(output/(label+'_source.csv'), index=False)
    np.savez_compressed(output/(label+'_states.npz'), t=t, x=x, edges=h.edges,
        mu_plus=mu_plus, mu_minus=mu_minus, heat=heat, heat_capacity=heat_capacity,
        **waves, **guides)
    pd.DataFrame(dict(s=t, wave_slice_energy=integrate(volume*total_wave),
                     thermal_slice_energy=integrate(volume*thermal_cells[0]))).to_csv(
                     output/(label+'_inventory.csv'), index=False)
    write_json(output/(label+'_summary.json'), summary)
    print(f'{label}: initial travelling field {summary["initial_wave_slice_energy"]:.6g}; '
          f'input {summary["absorbed_boundary_energy"]:.6g}; '
          f'wave peak {summary["maximum_wave_density"]:.6g}', flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--cells', type=int, nargs='+', default=[128, 256])
    parser.add_argument('--routes', nargs='+', choices=['left', 'right', 'split'], default=['left', 'right', 'split'])
    parser.add_argument('--temporal-factor', type=int, default=1)
    parser.add_argument('--output', type=Path, default=BASE/'poynting_delivery/route_screen')
    args = parser.parse_args()
    if args.workers < 1 or min(args.cells) < 16 or args.temporal_factor < 1:
        parser.error('positive workers, at least 16 cells, and positive time factor required')
    if args.output.exists():
        raise RuntimeError('retain completed evidence; choose a fresh output directory')
    sources = [Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/poynting_delivery.py',
        ROOT/'toolkit/adm_harness_cli/tests/test_poynting_delivery.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/active_transfer_reservoir.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/pressure_linked_storage.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/regenerative_converter.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/graded_electrothermal.py',
        Path(str(INPUT)+'_states.npz'), Path(str(INPUT)+'_points.csv'), STORES,
        BASE/'active_transfer_reservoir/metric_fine.npz', BASE/'active_transfer_reservoir/medium_baseline.npz']
    verified = []
    for item, manifest_path in [(sources[7], INPUT.parent/'manifest.json'),
                               (sources[8], INPUT.parent/'manifest.json'),
                               (STORES, STORES.parent/'manifest.json')]:
        manifest = json.loads(manifest_path.read_text())
        expected = manifest['output_sha256'][item.name]
        if expected != sha256_file(item):
            raise RuntimeError('input hash mismatch: '+str(item))
        verified.append(str(item.relative_to(ROOT)))
    before = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    args.output.mkdir(parents=True)
    specs = [(route, cells, args.temporal_factor, str(args.output))
             for route in args.routes for cells in args.cells]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(run_case, specs))
    after = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    if before != after:
        raise RuntimeError('source mutation during calculation')
    write_json(args.output/'summary.json', results)
    write_json(args.output/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        workers=args.workers, input_sha256=before, verified_archived_inputs=verified,
        output_sha256={p.name: sha256_file(p) for p in sorted(args.output.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
