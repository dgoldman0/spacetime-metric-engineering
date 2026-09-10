#!/usr/bin/env python3
"""Count paired feed/recovery guides with separate finite load-zone endings."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

import numpy as np
import pandas as pd

from adm_harness.poynting_delivery import propagate, wave_moments, reflection_guide_multiplier
from adm_harness.pressure_linked_storage import fluid_coefficients, fluid_moments
from adm_harness.regenerative_converter import compact_cell_moments
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.source_ledger import sha256_file
from run_poynting_delivery import DeliveryHistory, ROOT, BASE, INPUT, STORES, write_json


def run_case(spec):
    branches, cells, output = spec
    output = Path(output)
    h = DeliveryHistory(cells)
    x, t = h.x, h.t
    dx = h.edges[1]-h.edges[0]
    c = fluid_coefficients(h.model, t, x)
    volume = c['b']*c['radius']**2
    integrate = lambda a: 4*np.pi*dx*np.sum(a, axis=-1)
    faces = np.linspace(0, cells, branches+1).astype(int)
    guide_flux = np.zeros_like(x)
    plus, minus = np.zeros_like(volume), np.zeros_like(volume)
    legs, balance = [], []
    for leg, (lo, hi) in enumerate(zip(faces[:-1], faces[1:])):
        load = np.zeros_like(x)
        load[lo:hi] = 1.
        fluxes, energies = [], []
        for purpose, sign in (('absorption', -1), ('recovery', 1)):
            state, rows = propagate(t, h.edges, h.coefficients(sign, load, purpose),
                                    backwards=purpose == 'absorption')
            mu = state/volume
            if sign == -1:
                minus += mu
            else:
                plus += mu
            # Equal-area paired guides: both legs carry the larger flux demand.
            rest = mu*c['gamma']**2*(1-sign*c['v'])**2
            fluxes.append(float(np.max(rest*c['radius']**4)))
            energies.append(float(integrate(state[0])))
            for row in rows:
                row.update(leg=leg, purpose=purpose)
            balance.extend(rows)
        peak_flux = max(fluxes)
        guide_flux[lo:] += 2*peak_flux
        legs.append(dict(leg=leg, load_left=float(h.edges[lo]), load_right=float(h.edges[hi]),
            guide_left=float(h.edges[lo]), guide_right=float(h.edges[-1]),
            absorption_flux_requirement=fluxes[0], recovery_flux_requirement=fluxes[1],
            paired_guide_flux_per_multiplier=2*peak_flux,
            initial_wave_slice_energy=sum(energies)))
    wave = wave_moments(plus, minus)
    with np.load(STORES) as z:
        heat = h.interpolate_state(z['heat'])
        heat_capacity = h.spatial(z['heat_capacity'])[0]
    thermal = compact_cell_moments(heat+heat_capacity[None, :]/3, c)
    supply = fluid_moments(h.interpolate_state(h.state['thermal']),
        h.interpolate_state(h.state['flux_energy']), h.spatial(h.state['number'])[0], c)
    archived = pd.read_csv(str(INPUT)+'_points.csv')
    summaries, sources, turns = [], [], []
    for speed in (.2, .5, .8):
        for reflection in (0., .1):
            k = reflection_guide_multiplier(reflection, speed)
            guide = k*guide_flux[None, :]/c['radius']**4
            total = wave+thermal+np.array([guide, -guide, np.zeros_like(guide), guide])
            # r=.1 is a guide margin sensitivity; reflected wave propagation,
            # its extra energy, and receiver dissipation are a separate gate.
            for time, frame in archived.groupby('s'):
                it = int(np.argmin(abs(t-time)))
                demand = np.array([np.interp(x, frame.l, frame['geometry_'+key])
                                   for key in ('rho', 'pr', 'j', 'pt')])
                value, direction = maximum_null(supply[:, it]+total[:, it]-demand)
                summaries.append(dict(branches=branches, cells=cells, s=float(time),
                    drift_comparison=speed, reflected_amplitude_margin=reflection,
                    required_negative_null=float(max(0, value.max())),
                    guide_slice_energy=float(integrate(volume[it]*guide[it])),
                    auxiliary_slice_energy=float(integrate(volume[it]*total[0, it]))))
                if reflection == 0.:
                    sources.extend(dict(s=float(time), drift_comparison=speed, x=float(xx),
                        required_negative_null=float(max(0, value[j])), worst_direction=float(direction[j]))
                        for j, xx in enumerate(x))
            for leg in legs:
                boundary = leg['guide_left']
                radius = np.array([h.model.metric(float(tt), np.array([boundary])).radius[0] for tt in t])
                traction = k*leg['paired_guide_flux_per_multiplier']/radius**4
                force = 4*np.pi*radius**2*traction
                turns.append(dict(leg=leg['leg'], x=boundary, drift_comparison=speed,
                    reflected_amplitude_margin=reflection, peak_cut_traction=float(traction.max()),
                    peak_integrated_cut_force=float(force.max()),
                    # Thin-turn geometry: this coefficient times its chosen
                    # proper path length gives the leading field energy.
                    peak_turn_energy_per_unit_proper_path_length=float(force.max())))
    label = f'paired_b{branches}_n{cells}'
    write_json(output/(label+'_summary.json'), dict(case=label, branches=branches, cells=cells,
        initial_wave_slice_energy=float(integrate(volume[0]*(plus[0]+minus[0]))),
        initial_wave_material_inventory=float(integrate(volume[0]*c['gamma'][0]
            *((1-c['v'][0])*plus[0]+(1+c['v'][0])*minus[0]))),
        final_wave_slice_energy=float(integrate(volume[-1]*(plus[-1]+minus[-1]))),
        maximum_wave_slice_energy=float(integrate(volume*(plus+minus)).max()),
        maximum_balance_residual=float(max(abs(row['balance_residual']) for row in balance)),
        legs=legs, phases=summaries, turn_ports=turns,
        maximum_prescribed_material_velocity=float(abs(c['v']).max()),
        packet_gap=float(abs(h.edges[-1]-t[0])-.35)))
    pd.DataFrame(sources).to_csv(output/(label+'_source.csv'), index=False)
    pd.DataFrame(balance).to_csv(output/(label+'_balance.csv'), index=False)
    np.savez_compressed(output/(label+'_states.npz'), t=t, x=x, guide_flux_per_multiplier=guide_flux,
                        mu_plus=plus, mu_minus=minus)
    selected = [r for r in summaries if r['drift_comparison']==.5 and r['reflected_amplitude_margin']==0.]
    print(label, [(r['s'], round(r['required_negative_null'],6), round(r['guide_slice_energy'],3))
                  for r in selected], flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--cells', type=int, default=256)
    parser.add_argument('--branches', type=int, nargs='+', default=[1, 2, 4, 8])
    parser.add_argument('--output', type=Path, default=BASE/'poynting_delivery/branched_guides')
    args = parser.parse_args()
    if args.workers < 1 or min(args.branches) < 1 or args.cells < max(args.branches)*8:
        parser.error('positive worker count and resolved load zones required')
    if args.output.exists():
        raise RuntimeError('preserve completed evidence and choose a fresh output directory')
    files = [Path(__file__), Path(__file__).with_name('run_poynting_delivery.py'),
        ROOT/'toolkit/adm_harness_cli/adm_harness/poynting_delivery.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/active_transfer_reservoir.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/pressure_linked_storage.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/graded_electrothermal.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/regenerative_converter.py',
        Path(str(INPUT)+'_states.npz'), Path(str(INPUT)+'_points.csv'), STORES,
        BASE/'active_transfer_reservoir/metric_fine.npz', BASE/'active_transfer_reservoir/medium_baseline.npz']
    before = {str(p.relative_to(ROOT)): sha256_file(p) for p in files}
    args.output.mkdir(parents=True)
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        list(pool.map(run_case, [(b, args.cells, str(args.output)) for b in args.branches]))
    if before != {str(p.relative_to(ROOT)): sha256_file(p) for p in files}:
        raise RuntimeError('source mutation during computation')
    write_json(args.output/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        workers=args.workers, input_sha256=before,
        output_sha256={p.name: sha256_file(p) for p in sorted(args.output.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
