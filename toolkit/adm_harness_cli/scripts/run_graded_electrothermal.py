#!/usr/bin/env python3
"""Bounded radial-capacitor and finite-contact conservation/source screen."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing

import numpy as np
import pandas as pd

from adm_harness.active_transfer_reservoir import TabulatedActiveMedium, divergence_projections
from adm_harness.elastic_endpoint_reservoir import ElasticLaw
from adm_harness.electrothermal_endpoint import ElectricalLaw
from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.graded_electrothermal import (
    coefficients, fixed_kinematics, force_ports, hoop_force_cone, maximum_null,
    moments, solve_schedule,
)
from adm_harness.metric_regularity import regularized_scalars
from adm_harness.relaxing_material_ensemble import RelaxingMaterialEnsemble, StrainRelaxation
from adm_harness.reservoir_feasibility import radial_null
from adm_harness.source_ledger import SourceParams, sha256_file
from run_active_transfer_reservoir import parameters

ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT/'supporting_reports/data/active_transfer_reservoir'
OUTPUT = ROOT/'supporting_reports/data/graded_electrothermal'
PORTS = (-1.7, -1.3, -.9)
CASES = [
    ('continuous_n32', 32, 64, 1.285, (), 1e-8),
    ('continuous_n64', 64, 128, 1.285, (), 1e-8),
    ('segmented_n32', 32, 64, 1.285, PORTS, 1e-8),
    ('segmented_n64', 64, 128, 1.285, PORTS, 1e-8),
    ('segmented_time_refined', 64, 256, 1.285, PORTS, 1e-8),
    ('segmented_n128', 128, 256, 1.285, PORTS, 1e-8),
    ('segmented_reset', 64, 300, 3., PORTS, 1e-8),
    ('segmented_flux_floor', 64, 128, 1.285, PORTS, 1e-6),
]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def independent_checks(model, t, x, m, h, port_mask):
    rows = []
    for i in np.unique(np.linspace(0, len(t)-2, 17).astype(int)):
        for j in np.unique(np.linspace(0, len(x)-2, 17).astype(int)):
            if port_mask[j]:
                continue
            tt, xx = (t[i]+t[i+1])/2, (x[j]+x[j+1])/2
            def tensor_at(time, position):
                wt, wx = (time-t[i])/(t[i+1]-t[i]), (position-x[j])/(x[j+1]-x[j])
                def value(array):
                    return ((1-wt)*((1-wx)*array[i, j]+wx*array[i, j+1])
                            +wt*((1-wx)*array[i+1, j]+wx*array[i+1, j+1]))
                g = model.metric(float(time), np.array([position]))
                v = g.b*g.beta/g.alpha
                return moments(value(m), value(h), dict(gamma=1/np.sqrt(1-v*v), b=g.b,
                                                        radius=g.radius, v=v))
            eps = min(1e-5, (t[i+1]-t[i])/100, (x[j+1]-x[j])/100)
            g = model.metric(float(tt), np.array([xx]))
            power, force = divergence_projections(g, tensor_at(tt, xx),
                (tensor_at(tt+eps, xx)-tensor_at(tt-eps, xx))/(2*eps),
                (tensor_at(tt, xx+eps)-tensor_at(tt, xx-eps))/(2*eps))
            mp, mf = divergence_projections(g, *model.medium(float(tt), np.array([xx])))
            c = coefficients(model, np.array([tt]), np.array([xx]))
            v, gamma = float(c['v'][0, 0]), float(c['gamma'][0, 0])
            mt = .5*(m[i+1, j]+m[i+1, j+1]-m[i, j]-m[i, j+1])/(t[i+1]-t[i])
            ht = .5*(h[i+1, j]+h[i+1, j+1]-h[i, j]-h[i, j+1])/(t[i+1]-t[i])
            hx = .5*(h[i, j+1]+h[i+1, j+1]-h[i, j]-h[i+1, j])/(x[j+1]-x[j])
            local_m = np.mean(m[i:i+2, j:j+2])
            energy_scale = (abs(mt)+abs(float(c['c'][0, 0])*ht)+abs(float(c['source'][0, 0])))/(g.alpha[0]*g.volume[0])
            force_scale = (abs(hx)+abs(float(c['d'][0, 0])*mt)+abs(float(c['a'][0, 0])*local_m)
                           +abs(float(c['force'][0, 0])))/(gamma*g.b[0]*g.radius[0]**4)
            er = gamma*((power+mp)-v*(force+mf))
            fr = gamma*((force+mf)-v*(power+mp))
            rows.append(dict(s=tt, l=xx, rest_energy_residual=float(er[0]), rest_force_residual=float(fr[0]),
                             energy_term_scale=float(energy_scale), force_term_scale=float(force_scale),
                             endpoint_rest_power=float(gamma*(mp[0]-v*mf[0])),
                             endpoint_rest_force=float(gamma*(mf[0]-v*mp[0]))))
    frame = pd.DataFrame(rows)
    result = dict(points=len(frame))
    for name in ('energy', 'force'):
        residual = abs(frame['rest_'+name+'_residual'])
        result[name+'_maximum_absolute_residual'] = float(residual.max())
        result[name+'_sum_relative_term_residual'] = float(residual.sum()/max(frame[name+'_term_scale'].sum(), 1e-30))
    return frame, result


def run_case(task):
    spec, output = task
    name, cells, steps, duration, ports, floor = spec
    model = TabulatedActiveMedium(INPUT/'metric_fine.npz', INPUT/'medium_baseline.npz')
    patch = RelaxingMaterialEnsemble(model, ElasticLaw(stiffness=.1, scale=.4),
        ElectricalLaw(energy_ratio=4., conductivity=.1, profile='capacitor'),
        relaxation=StrainRelaxation(stiffness=.1, proper_time=1.), cells=cells, thermal_share=1.)
    initial = patch.fields(0., patch.initial())
    x = initial['x']
    t = np.unique(np.r_[np.linspace(0., duration, steps+1), .5, 1.285])
    number = patch.law.scale*patch.mass/initial['volume']
    m0 = number*(1+initial['heat'])
    c = coefficients(model, t, x)
    result = solve_schedule(t, x, c, number, m0, ports=ports, flux_floor=floor, deadline=180.)
    if not result['success']:
        write_json(output/(name+'_summary.json'), dict(case=name, **result))
        print(name+': '+result['message'], flush=True)
        return
    m, h, mask = (result.pop(key) for key in ('mass_energy', 'flux_energy', 'port_mask'))
    supplied = moments(m, h, c)
    peak_null, directions = maximum_null(supplied)
    energies = 4*np.pi*np.trapezoid(c['gamma']*m+c['b']*h/c['radius']**2, x, axis=1)
    field_energies = 4*np.pi*np.trapezoid(c['b']*h/c['radius']**2, x, axis=1)
    normal, proper, residual = force_ports(t, x, c, m, h)
    mid = {key: .5*(value[:, :-1]+value[:, 1:]) for key, value in c.items()}
    # Opposite divergence is required from a co-moving hoop-only support.
    allowed, cone_low, cone_high = hoop_force_cone(mid['acceleration'], mid['angular_gradient'], -proper)
    substantial = abs(proper) > 1e-8
    failed = (~allowed) & substantial & mask[None, :]
    integral = 4*np.pi*np.diff(x)[None, :]*mid['b']*mid['radius']**2*normal
    port_series, hoop_witnesses = [], []
    for center in ports:
        inside = abs(.5*(x[1:]+x[:-1])-center) < .05-1e-10
        for i, time in enumerate(t):
            port_series.append(dict(s=time, center=center, force_integral=float(integral[i, inside].sum()),
                maximum_abs_normal_force_density=float(abs(normal[i, inside]).max()),
                proper_width=float(np.dot(mid['b'][i, inside], np.diff(x)[inside])),
                hoop_cone_failed_cells=int(failed[i, inside].sum())))
    if failed.any():
        worst = np.unravel_index(np.argmax(np.where(failed, abs(proper), 0.)), failed.shape)
        i, j = worst
        hoop_witnesses.append(dict(s=float(t[i]), l=float(.5*(x[j]+x[j+1])),
            required_support_rest_divergence=float(-proper[i, j]), acceleration=float(mid['acceleration'][i, j]),
            twice_abs_angular_gradient=float(2*abs(mid['angular_gradient'][i, j])),
            allowed_force_per_density_low=float(cone_low[i, j]), allowed_force_per_density_high=float(cone_high[i, j])))
    check_frame, checks = independent_checks(model, t, x, m, h, mask)
    check_frame.to_csv(output/(name+'_independent_checks.csv'), index=False)
    sigma = np.log(h[:-1]/h[1:])/(2*np.diff(t)[:, None]*.5*(c['lapse'][:-1]+c['lapse'][1:]))
    summary = dict(case=name, cells=cells, time_intervals=len(t)-1, duration=duration, ports=list(ports),
        port_coordinate_width=.1, flux_floor=floor, **result,
        maximum_supplied_null=float(peak_null.max()), maximum_abs_velocity=float(abs(c['v']).max()),
        minimum_heat=float((m/number[None, :]-1).min()), maximum_heat=float((m/number[None, :]-1).max()),
        initial_slice_energy=float(energies[0]), maximum_slice_energy=float(energies.max()),
        final_slice_energy=float(energies[-1]), initial_field_slice_energy=float(field_energies[0]),
        maximum_electric_density=float((h/c['radius']**4).max()),
        maximum_radial_null=float(radial_null(supplied).max()), maximum_effective_discharge_conductivity=float(sigma.max()),
        maximum_charge_increase=float(np.maximum(np.diff(h, axis=0), 0).max()),
        minimum_packet_gap=float(np.min(abs(x[None, :]-t[:, None]))-.35),
        maximum_collared_normal_force_density=float(abs(normal[:, mask]).max()) if mask.any() else 0.,
        maximum_left_terminal_traction=float((h[:, 0]/c['radius'][:, 0]**4).max()),
        maximum_right_terminal_traction=float((h[:, -1]/c['radius'][:, -1]**4).max()),
        hoop_force_cone_failures=int(failed.sum()), hoop_witnesses=hoop_witnesses, independent_checks=checks)
    if port_series:
        pf = pd.DataFrame(port_series)
        pf.to_csv(output/(name+'_ports.csv'), index=False)
        summary['maximum_abs_integrated_collar_force'] = float(abs(pf.force_integral).max())
    phase_rows, points = [], []
    params = SourceParams(**parameters())
    for target in (0., .5, 1.285, 3.):
        if target > duration:
            continue
        ii = int(np.argmin(abs(t-target))); time = float(t[ii])
        medium = model.medium(time, x)[0]
        demands, coarse, splined = [np.zeros((4, len(x))) for _ in range(3)]
        def spline_scalars(tt, xx, unused):
            g = model.metric(tt, np.array([xx]))
            return dict(alpha=float(g.alpha[0]), beta=float(g.beta[0]),
                        gamma_ll=float(g.b[0]**2), gamma_omega=float(g.radius[0]**2))
        for j, position in enumerate(x):
            for array, step, evaluator in ((demands, .00125, regularized_scalars),
                                            (coarse, .0025, regularized_scalars),
                                            (splined, .00125, spline_scalars)):
                value = evaluate_demand(time, float(position), params, step, step, scalar_evaluator=evaluator)
                array[:, j] = [value[key] for key in ('rho', 'p_l', 'j_l', 'p_omega')]
        excess = supplied[:, ii]+medium-demands
        required, angle = maximum_null(excess)
        required = np.maximum(0., required)
        radial_required = np.maximum(0., radial_null(excess))
        negative_energy = np.maximum(excess[0], 0.)
        phase_rows.append(dict(s=time, slice_energy=float(energies[ii]), field_slice_energy=float(field_energies[ii]),
            required_negative_null_peak=float(required.max()), required_negative_radial_null_peak=float(radial_required.max()),
            required_negative_slice_energy_integral=float(4*np.pi*np.trapezoid(c['b'][ii]*c['radius'][ii]**2*negative_energy, x)),
            geometry_fd_difference=float(abs(demands-coarse).max()), geometry_spline_difference=float(abs(demands-splined).max())))
        for j, position in enumerate(x):
            row = dict(s=time, l=float(position), required_negative_null=float(required[j]),
                worst_null_direction_cosine=float(angle[j]), required_negative_radial_plus=float(radial_required[0, j]),
                required_negative_radial_minus=float(radial_required[1, j]), velocity=float(c['v'][ii, j]),
                heat=float(m[ii, j]/number[j]-1), electric_density=float(h[ii, j]/c['radius'][ii, j]**4))
            for prefix, values in (('geometry', demands), ('endpoint', medium), ('reservoir', supplied[:, ii])):
                row.update({prefix+'_'+key: float(values[k, j]) for k, key in enumerate(('rho', 'p_r', 'j', 'p_t'))})
            points.append(row)
    summary['phases'] = phase_rows
    np.savez_compressed(output/(name+'_states.npz'), t=t, x=x, mass_energy=m, flux_energy=h,
                        number=number, port_mask=mask, normal_port_force=normal, **c)
    pd.DataFrame(points).to_csv(output/(name+'_points.csv'), index=False)
    write_json(output/(name+'_summary.json'), summary)
    print(f'{name}: E0={energies[0]:.7g}; peak supplied null={peak_null.max():.7g}; '
          f'|v|={summary["maximum_abs_velocity"]:.7g}; hoop failures={failed.sum()}; '
          f'force check={checks["force_sum_relative_term_residual"]:.4g}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--cases', nargs='+', choices=[case[0] for case in CASES])
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    args.output.mkdir(parents=True, exist_ok=True)
    software = [Path(__file__), Path(__file__).with_name('run_active_transfer_reservoir.py')]
    software += [ROOT/'toolkit/adm_harness_cli/adm_harness'/name for name in (
        'graded_electrothermal.py', 'active_transfer_reservoir.py', 'elastic_endpoint_reservoir.py',
        'electrothermal_endpoint.py', 'material_ensemble.py', 'relaxing_material_ensemble.py',
        'reservoir_feasibility.py', 'geometry_boundary.py', 'metric_regularity.py', 'source_ledger.py', 'radial_stress.py')]
    inputs = [INPUT/'metric_fine.npz', INPUT/'medium_baseline.npz',
              ROOT/'supporting_reports/data/le_metric_c2_repair/manifest.json']
    hashes = {str(p.relative_to(ROOT)): sha256_file(p) for p in software+inputs}
    selected = [case for case in CASES if args.cases is None or case[0] in args.cases]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        list(pool.map(run_case, [(case, args.output) for case in selected]))
    for name, expected in hashes.items():
        if sha256_file(ROOT/name) != expected:
            raise RuntimeError('software or input changed during run: '+name)
    write_json(args.output/'manifest.json', dict(completed_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        cases=[case[0] for case in selected], software_and_input_sha256=hashes,
        scope='inverse conservation screen on active late patch; pressure-free local stores and passive radial Maxwell fields; segmented cases expose finite force collars; terminal material, current inertia, confinement, control dynamics and complete source remain open',
        output_sha256={p.name: sha256_file(p) for p in sorted(args.output.iterdir()) if p.name != 'manifest.json' and p.is_file()}))


if __name__ == '__main__':
    main()
