#!/usr/bin/env python3
"""Bounded joint pressure-path, heat-pressure, and radial-field construction."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

import numpy as np
import pandas as pd

from adm_harness.active_transfer_reservoir import TabulatedActiveMedium, divergence_projections
from adm_harness.elastic_endpoint_reservoir import ElasticLaw
from adm_harness.electrothermal_endpoint import ElectricalLaw
from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.graded_electrothermal import maximum_null, smooth_spline_scalars
from adm_harness.metric_regularity import regularized_scalars
from adm_harness.pressure_linked_storage import (
    balanced_end_witness, fluid_coefficients, fluid_moments, minimum_positive_pressure, reduced_divergence,
    solve_connected_schedule,
)
from adm_harness.relaxing_material_ensemble import RelaxingMaterialEnsemble, StrainRelaxation
from adm_harness.reservoir_feasibility import radial_null
from adm_harness.source_ledger import SourceParams, sha256_file
from run_active_transfer_reservoir import parameters

ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT/'supporting_reports/data/active_transfer_reservoir'
OUTPUT = ROOT/'supporting_reports/data/pressure_linked_storage'
PREVIOUS = ROOT/'supporting_reports/data/graded_electrothermal/finite_contacts/interior_solver'
# case, cells, steps, end time, initial preparation, end load, discharge limit
CASES = [
    ('fixed_exposed_n32', 32, 64, 1.285, 'fixed', 'exposed', 1.),
    ('prepared_exposed_n32', 32, 64, 1.285, 'prepared', 'exposed', 1.),
    ('fixed_balanced_n32', 32, 64, 1.285, 'fixed', 'balanced', 1.),
    ('prepared_balanced_n32', 32, 64, 1.285, 'prepared', 'balanced', 1.),
    ('prepared_exposed_n64', 64, 128, 1.285, 'prepared', 'exposed', 1.),
    ('prepared_exposed_time', 64, 256, 1.285, 'prepared', 'exposed', 1.),
    ('prepared_exposed_space', 128, 128, 1.285, 'prepared', 'exposed', 1.),
    ('prepared_exposed_joint', 128, 256, 1.285, 'prepared', 'exposed', 1.),
    ('prepared_exposed_fast', 64, 128, 1.285, 'prepared', 'exposed', 10.),
    ('prepared_balanced_free_rate', 32, 64, 1.285, 'prepared', 'balanced', None),
    ('fixed_exposed_free_rate', 32, 64, 1.285, 'fixed', 'exposed', None),
    ('prepared_exposed_free_rate', 64, 128, 1.285, 'prepared', 'exposed', None),
    ('prepared_fast_joint', 128, 256, 1.285, 'prepared', 'exposed', 10.),
    ('prepared_reset', 64, 300, 3., 'prepared', 'exposed', 1.),
]
CASES = [case+(True,) for case in CASES]
CASES += [('powered_exposed_n64', 64, 128, 1.285, 'prepared', 'exposed', None, False)]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def independent_checks(model, t, x, u, h, number):
    rows = []
    for i in np.unique(np.linspace(0, len(t)-2, 17).astype(int)):
        for j in np.unique(np.linspace(0, len(x)-2, 17).astype(int)):
            tt, xx = (t[i]+t[i+1])/2, (x[j]+x[j+1])/2
            def interpolate(array, time, position):
                wt, wx = (time-t[i])/(t[i+1]-t[i]), (position-x[j])/(x[j+1]-x[j])
                return ((1-wt)*((1-wx)*array[i, j]+wx*array[i, j+1])
                        +wt*((1-wx)*array[i+1, j]+wx*array[i+1, j+1]))
            def fields(time, position):
                cc = fluid_coefficients(model, np.array([time]), np.array([position]))
                nn = np.interp(position, x[j:j+2], number[j:j+2])
                uu, hh = (interpolate(a, time, position) for a in (u, h))
                return cc, nn, uu, hh
            def tensor(time, position):
                cc, nn, uu, hh = fields(time, position)
                return fluid_moments(uu, hh, nn, cc)[:, 0]
            eps = min(1e-5, (t[i+1]-t[i])/100, (x[j+1]-x[j])/100)
            g = model.metric(float(tt), np.array([xx]))
            power, force = divergence_projections(g, tensor(tt, xx),
                (tensor(tt+eps, xx)-tensor(tt-eps, xx))/(2*eps),
                (tensor(tt, xx+eps)-tensor(tt, xx-eps))/(2*eps))
            mp, mf = divergence_projections(g, *model.medium(float(tt), np.array([xx])))
            cc, nn, uu, hh = fields(tt, xx)
            v, gamma = (float(cc[key][0, 0]) for key in ('v', 'gamma'))
            ut = .5*(u[i+1, j]+u[i+1, j+1]-u[i, j]-u[i, j+1])/(t[i+1]-t[i])
            ht = .5*(h[i+1, j]+h[i+1, j+1]-h[i, j]-h[i, j+1])/(t[i+1]-t[i])
            hx = .5*(h[i, j+1]+h[i+1, j+1]-h[i, j]-h[i+1, j])/(x[j+1]-x[j])
            def pressure(position):
                cp, _, up, _ = fields(tt, position)
                return up/(3*cp['rest_volume'])
            px = (pressure(xx+eps)-pressure(xx-eps))/(2*eps)
            zero = np.zeros_like(cc['v'])
            terms = []
            for n0, u0, ut0, px0, ht0, hx0 in ((0, 0, ut, zero, 0, 0),
                    (nn, uu, 0, zero, 0, 0), (0, 0, 0, px, 0, 0), (0, 0, 0, zero, ht, hx)):
                terms.append(reduced_divergence(cc, n0, u0, ut0, px0, ht0, hx0))
            ep, ef = gamma*(mp-v*mf), gamma*(mf-v*mp)
            terms.append((ep, ef))
            energy_scale, force_scale = [sum(float(abs(term[k]).max()) for term in terms) for k in (0, 1)]
            rows.append(dict(s=tt, l=xx,
                energy_residual=float((gamma*(power+mp-v*(force+mf)))[0]),
                force_residual=float((gamma*(force+mf-v*(power+mp)))[0]),
                energy_term_scale=energy_scale, force_term_scale=force_scale))
    frame = pd.DataFrame(rows)
    metrics = dict(points=len(frame))
    for kind in ('energy', 'force'):
        residual = abs(frame[kind+'_residual'])
        metrics[kind+'_max_absolute'] = float(residual.max())
        metrics[kind+'_sum_relative_term_residual'] = float(residual.sum()/max(1e-30, frame[kind+'_term_scale'].sum()))
    return frame, metrics


def source_comparison(model, t, x, c, u, h, number):
    phases, points = [], []
    params = SourceParams(**parameters())
    tensor = fluid_moments(u, h, number, c)
    for target in (0., .5, 1.285, 3.):
        if target > t[-1]:
            continue
        i = int(np.argmin(abs(t-target))); time = float(t[i])
        demand, coarse, spline = [np.zeros((4, len(x))) for _ in range(3)]
        for j, position in enumerate(x):
            for array, step, evaluator in ((demand, .00125, regularized_scalars),
                    (coarse, .0025, regularized_scalars),
                    (spline, .00125, lambda tt, xx, unused: smooth_spline_scalars(model, tt, xx))):
                val = evaluate_demand(time, float(position), params, step, step, scalar_evaluator=evaluator)
                array[:, j] = [val[key] for key in ('rho', 'p_l', 'j_l', 'p_omega')]
        endpoint = model.medium(time, x)[0]
        excess = tensor[:, i]+endpoint-demand
        required, direction = maximum_null(excess)
        required = np.maximum(0., required)
        energy = 4*np.pi*np.trapezoid(c['b'][i]*c['radius'][i]**2*tensor[0, i], x)
        phases.append(dict(s=time, slice_energy=float(energy),
            required_negative_null=float(required.max()), required_negative_radial_null=float(max(0., radial_null(excess).max())),
            geometry_fd_difference=float(abs(demand-coarse).max()), geometry_spline_difference=float(abs(demand-spline).max())))
        for j, position in enumerate(x):
            row = dict(s=time, l=float(position), required_negative_null=float(required[j]),
                       worst_direction_cosine=float(direction[j]))
            for prefix, values in (('geometry', demand), ('endpoint', endpoint), ('supply', tensor[:, i])):
                row.update({prefix+'_'+key: float(values[k, j]) for k, key in enumerate(('rho', 'pr', 'j', 'pt'))})
            points.append(row)
    return phases, pd.DataFrame(points)


def run_case(task):
    spec, output = task
    name, cells, steps, duration, preparation, ends, rate, passive = spec
    model = TabulatedActiveMedium(INPUT/'metric_fine.npz', INPUT/'medium_baseline.npz')
    patch = RelaxingMaterialEnsemble(model, ElasticLaw(stiffness=.1, scale=.4),
        ElectricalLaw(energy_ratio=4., conductivity=.1, profile='capacitor'),
        relaxation=StrainRelaxation(stiffness=.1, proper_time=1.), cells=cells, thermal_share=1.)
    initial = patch.fields(0., patch.initial())
    x = initial['x']
    t = np.unique(np.r_[np.linspace(0., duration, steps+1), .5, 1.285])
    number = patch.law.scale*patch.mass/initial['volume']
    u0 = number*initial['heat']
    c = fluid_coefficients(model, t, x)
    result = solve_connected_schedule(t, x, c, number, u0, initial_mode=preparation,
        ends=ends, conductivity_ceiling=rate, passive=passive, deadline=180., secondary_deadline=60.)
    metadata = dict(case=name, cells=cells, intervals=len(t)-1, duration=duration,
                    initial_mode=preparation, ends=ends, conductivity_ceiling=rate, kappa=3., passive=passive)
    if not result['success']:
        write_json(output/(name+'_summary.json'), dict(**metadata, **result))
        print(name+': '+result['message'], flush=True)
        return
    u, h = result.pop('thermal'), result.pop('flux_energy')
    tensor = fluid_moments(u, h, number, c)
    energy = 4*np.pi*np.trapezoid(c['b']*c['radius']**2*tensor[0], x, axis=1)
    pressure = u/(3*c['rest_volume'])
    traction = pressure-h/c['radius']**4
    sigma = np.log(h[:-1]/h[1:])/((c['lapse'][:-1]+c['lapse'][1:])*np.diff(t)[:, None])
    checks, check_metrics = independent_checks(model, t, x, u, h, number)
    checks.to_csv(output/(name+'_checks.csv'), index=False)
    phases, points = source_comparison(model, t, x, c, u, h, number)
    points.to_csv(output/(name+'_points.csv'), index=False)
    pd.DataFrame(dict(s=t, left_pressure=pressure[:, 0], right_pressure=pressure[:, -1],
        left_net_traction=traction[:, 0], right_net_traction=traction[:, -1],
        left_integrated_traction=4*np.pi*c['radius'][:, 0]**2*traction[:, 0],
        right_integrated_traction=4*np.pi*c['radius'][:, -1]**2*traction[:, -1], slice_energy=energy)).to_csv(output/(name+'_ports.csv'), index=False)
    summary = dict(**metadata, **result, maximum_supplied_null=float(maximum_null(tensor)[0].max()),
        maximum_velocity=float(abs(c['v']).max()), minimum_heat=float((u/number).min()),
        initial_slice_energy=float(energy[0]), final_slice_energy=float(energy[-1]),
        maximum_slice_energy=float(energy.max()), maximum_pressure=float(pressure.max()),
        maximum_left_traction=float(abs(traction[:, 0]).max()), maximum_right_traction=float(abs(traction[:, -1]).max()),
        maximum_discharge_rate=float(sigma.max()), maximum_field_increase=float(max(0., np.diff(h, axis=0).max())),
        maximum_sound_speed_squared=float((4*pressure/(3*(number/c['rest_volume']+4*pressure))).max()),
        minimum_packet_gap=float((abs(x[None, :]-t[:, None])-.35).min()), independent_checks=check_metrics, phases=phases)
    np.savez_compressed(output/(name+'_states.npz'), t=t, x=x, thermal=u, flux_energy=h, number=number, **c)
    write_json(output/(name+'_summary.json'), summary)
    print(f'{name}: peak={summary["maximum_supplied_null"]:.7g}, E0={energy[0]:.7g}, '
          f'end loads={summary["maximum_left_traction"]:.6g},{summary["maximum_right_traction"]:.6g}; '
          f'force check={check_metrics["force_sum_relative_term_residual"]:.5g}', flush=True)


def archived_pressure_path(task):
    time, nodes, output = task
    model = TabulatedActiveMedium(INPUT/'metric_fine.npz', INPUT/'medium_baseline.npz')
    with np.load(PREVIOUS/'smooth_joint_refined_states.npz') as state:
        i = int(np.argmin(abs(state['t']-time)))
        amplitude = state['contact_amplitudes'][i]
    x = np.linspace(-2.1, -.5, nodes)
    c = fluid_coefficients(model, np.array([time]), x)
    c = {key: value[0] for key, value in c.items()}
    applied = np.zeros_like(x)
    for center, force in zip((-1.7, -1.3, -.9), amplitude):
        z = 2*(x-center)/.1
        profile = np.maximum(0., 1-z*z)**3/(16*.1/35)
        applied -= force*profile/(4*np.pi*c['radius']**2)
    p, exponent = minimum_positive_pressure(x, 4*c['gamma']*c['b']*c['acceleration'], applied)
    stress = fluid_moments(3*c['rest_volume']*p, np.zeros_like(p), np.zeros_like(p), c)
    label = f'path_s{time:g}_n{nodes}'
    pd.DataFrame(dict(l=x, pressure=p, integrating_exponent=exponent, drive=applied)).to_csv(output/(label+'.csv'), index=False)
    summary = dict(s=time, nodes=nodes, instantaneous_pressure_time_derivative=0,
        left_pressure=float(p[0]), right_pressure=float(p[-1]), maximum_pressure=float(p.max()),
        logarithmic_pressure_gain=float(exponent.max()-exponent.min()),
        maximum_supplied_null=float(maximum_null(stress)[0].max()),
        slice_energy=float(4*np.pi*np.trapezoid(c['b']*c['radius']**2*stress[0], x)))
    write_json(output/(label+'_summary.json'), summary)
    print(f'{label}: peak pressure={p.max():.7g}, field-fluid path E={summary["slice_energy"]:.7g}', flush=True)


def force_witnesses(output):
    model = TabulatedActiveMedium(INPUT/'metric_fine.npz', INPUT/'medium_baseline.npz')
    with np.load(PREVIOUS/'smooth_joint_refined_states.npz') as state:
        oldx, oldnumber = state['x'], state['number']
    rows = []
    for nodes in (257, 513, 1025, 2049):
        x = np.linspace(-2.1, -.5, nodes)
        c = fluid_coefficients(model, np.array([1.285]), x)
        c = {key: value[0] for key, value in c.items()}
        number = np.interp(x, oldx, oldnumber)
        g = model.metric(1.285, x)
        for rate in (1., 10.):
            witness = balanced_end_witness(x, c, number, g.logr_x, rate)
            rows.append(dict(nodes=nodes, s=1.285, conductivity_ceiling=rate,
                weighted_drive_integral=witness['weighted_drive_integral'],
                minimum_field_coefficient=witness['minimum_field_coefficient'],
                terminal_weight=float(witness['weight'][-1]), maximum_velocity=float(abs(c['v']).max())))
            if nodes == 2049 and rate == 1.:
                pd.DataFrame(dict(l=x, weight=witness['weight'], drive=witness['drive'],
                    minimum_field_coefficient=witness['field_min'])).to_csv(output/'balanced_end_witness_profile.csv', index=False)
    pd.DataFrame(rows).to_csv(output/'balanced_end_witness.csv', index=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--cases', nargs='+', choices=[case[0] for case in CASES], default=[case[0] for case in CASES[:4]])
    parser.add_argument('--output', type=Path, default=OUTPUT/'first_round')
    parser.add_argument('--pressure-paths', action='store_true')
    parser.add_argument('--force-witnesses', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('use a new empty output directory to preserve stage evidence')
    args.output.mkdir(parents=True, exist_ok=True)
    software = [Path(__file__), Path(__file__).with_name('run_active_transfer_reservoir.py')]
    software += [ROOT/'toolkit/adm_harness_cli/adm_harness'/name for name in (
        'pressure_linked_storage.py', 'graded_electrothermal.py', 'active_transfer_reservoir.py',
        'elastic_endpoint_reservoir.py', 'electrothermal_endpoint.py', 'material_ensemble.py',
        'relaxing_material_ensemble.py', 'geometry_boundary.py', 'metric_regularity.py', 'source_ledger.py',
        'reservoir_feasibility.py', 'radial_stress.py')]
    inputs = [INPUT/'metric_fine.npz', INPUT/'medium_baseline.npz',
        ROOT/'supporting_reports/data/le_metric_c2_repair/manifest.json', PREVIOUS/'smooth_joint_refined_states.npz']
    hashes = {str(path.relative_to(ROOT)): sha256_file(path) for path in software+inputs}
    selected = [case for case in CASES if case[0] in args.cases]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        list(pool.map(run_case, [(case, args.output) for case in selected]))
        if args.pressure_paths:
            list(pool.map(archived_pressure_path, [(time, nodes, args.output) for time in (0., .5, 1.285) for nodes in (513, 1025)]))
    if args.force_witnesses:
        force_witnesses(args.output)
    for name, expected in hashes.items():
        if sha256_file(ROOT/name) != expected:
            raise RuntimeError('software or input changed during run: '+name)
    write_json(args.output/'manifest.json', dict(completed_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        cases=args.cases, pressure_paths=args.pressure_paths, force_witnesses=args.force_witnesses, software_and_input_sha256=hashes,
        git_revision=subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip(),
        scope='inverse full-patch thermal-fluid and radial-field conservation; prescribed active worldlines, explicit end loads, actual EOS and charge transport completion open',
        output_sha256={p.name: sha256_file(p) for p in sorted(args.output.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
