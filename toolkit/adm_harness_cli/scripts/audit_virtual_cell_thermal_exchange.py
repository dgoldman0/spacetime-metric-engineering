#!/usr/bin/env python3
"""Bound counted local thermal exchange and joint phase/radiation schedules."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

import numpy as np
from numpy.polynomial.legendre import leggauss

from adm_harness.active_transfer_reservoir import TabulatedActiveMedium
from adm_harness.source_ledger import sha256_file
from adm_harness.virtual_cell_counterstream import material_kinematics
from adm_harness.virtual_cell_thermal_exchange import solve_thermal_exchange
from audit_virtual_cell_counterstream import (
    BASE, ROOT, find_control, geometry, verify_input_identity, write_json,
)


def panel_weights(model, times, position, w, order):
    """Exact-geometry Gauss averages for piecewise-linear A and K controls."""
    z, weights = leggauss(order)
    tt = ((times[:-1]+times[1:])[:, None]/2 +
          np.diff(times)[:, None]*z[None, :]/2).ravel()
    xx = np.full_like(tt, position)
    alpha = np.exp(model.metric_splines[0].ev(tt, xx))
    beta = model.metric_splines[1].ev(tt, xx)
    b = np.exp(model.metric_splines[2].ev(tt, xx))
    radius = np.exp(model.metric_splines[3].ev(tt, xx))
    ell = b/np.sqrt(1-(b*beta/alpha)**2)
    def average(values):
        return (values.reshape(-1, order)*weights[None, :]).sum(axis=1)/2
    return average(ell**2), average((ell*radius)**2/(ell*radius**2)**(1+w))


def evaluate(spec):
    filename, destination, strides, monotone, only_joint_radiation = spec
    path, output = Path(filename), Path(destination)
    meta = json.loads(path.with_name(path.name.replace('_states.npz', '_summary.json')).read_text())
    with np.load(path) as z:
        s = {key: z[key] for key in z.files}
    middle = len(s['x'])//2
    positions = s['x'][middle-1:middle+1]
    model = TabulatedActiveMedium(BASE/'active_transfer_reservoir/metric_fine.npz',
                                  BASE/'active_transfer_reservoir/medium_baseline.npz')
    if np.any(positions < model.x_min) or np.any(positions > model.x_max):
        raise ValueError('selected positions must lie within the registered metric')
    g = geometry(model, s['t'], positions)
    kin = material_kinematics(g)
    cases = []
    for side, index in enumerate((middle-1, middle)):
        for stride in strides:
            sample = np.arange(0, len(s['t']), stride)
            if sample[-1] != len(s['t'])-1:
                raise ValueError('temporal stride must preserve the final node')
            t, x = s['t'][sample], float(s['x'][index])
            fields = [s[key][sample, index] for key in
                      ('density', 'radial_pressure', 'angular_pressure', 'wall_rest')]
            radius, ell = g['radius'][sample, side], kin['ell'][sample, side]
            original_a = s['amplitude'][sample, index]
            actual_floor = 2*np.maximum(s['absorption_rest'][sample, index],
                s['work_return_rest'][sample, index]+s['heat_return_rest'][sample, index])
            equations = ((1/3, 'thermal_radiation'),) if only_joint_radiation else (
                (0., 'stored_excitation'), (1/3, 'thermal_radiation'))
            for w, eos_name in equations:
                mean4, exchange4 = panel_weights(model, t, x, w, 4)
                mean8, exchange8 = panel_weights(model, t, x, w, 8)
                for mode in (('joint_phase',) if only_joint_radiation else ('fixed_phase', 'joint_phase')):
                    fixed = original_a if mode == 'fixed_phase' else None
                    floor = actual_floor if mode == 'fixed_phase' else None
                    solved = solve_thermal_exchange(*fields, radius, ell, mean8, exchange8,
                        w=w, fixed_amplitude=fixed, radiation_floor=floor,
                        monotone_thermal=monotone, solver_threads=1)
                    label = meta['label']+f'_side{side}_stride{stride}_{eos_name}_{mode}'
                    scalars = {key: value for key, value in solved.items() if np.isscalar(value)}
                    result = dict(label=label, source=str(path.relative_to(ROOT)),
                        position=x, source_spatial_index=int(index), temporal_stride=int(stride),
                        time_samples=len(t), reservoir_eos=w, mode=mode,
                        phase_independently_reoptimized=mode == 'joint_phase',
                        registered_wave_inventory_floor_retained=mode == 'fixed_phase',
                        fixed_phase_conversion_efficiency=.98 if mode == 'fixed_phase' else None,
                        prepared_radiation_and_material_inventories_free=True,
                        interface_wall_energy_retained=True, guide_floor_retained=False,
                        extra_carrier_rest_mass_and_confinement_supplied=False,
                        radiation_current_zero=True, reservoir_current_zero=True,
                        local_phase_radiation_reservoir_power_sum=0.,
                        endpoint_external_power_added=0.,
                        monotonically_charged_adiabatic_inventory=monotone,
                        perfect_isotropic_zero_flux_comparison=bool(monotone and w == 1/3),
                        full_source_construction_supplied=False,
                        maximum_phase_weight_quadrature_change=float(abs(mean8-mean4).max()),
                        maximum_exchange_weight_quadrature_change=float(abs(exchange8-exchange4).max()),
                        sampled_energy_cone_passes=bool(solved['density_allowance'] < 1e-8),
                        positive_dual_density_gap=bool(solved['dual_lower_bound'] > 1e-8),
                        scope='sampled local power/cone gate with arbitrary reciprocal exchange; spatial transport, force law, opacity, entropy and physical carrier remain additional requirements',
                        **scalars)
                    arrays = {key: value for key, value in solved.items() if isinstance(value, np.ndarray)}
                    np.savez_compressed(output/(label+'_states.npz'), t=t, x=np.array(x),
                        density=fields[0], radial_pressure=fields[1], angular_pressure=fields[2],
                        wall_rest=fields[3], radius=radius, ell=ell,
                        material_lapse=kin['lapse'][sample, side],
                        radial_expansion=kin['theta_r'][sample, side],
                        angular_expansion=kin['theta_t'][sample, side],
                        material_acceleration=kin['acceleration'][sample, side],
                        original_amplitude=original_a, original_wave_inventory_floor=actual_floor,
                        panel_mean_ell_squared=mean8, panel_mean_exchange_weight=exchange8,
                        panel_mean_ell_squared_order4=mean4, panel_mean_exchange_weight_order4=exchange4,
                        **arrays)
                    write_json(output/(label+'_summary.json'), result)
                    print(f'{label}: extra density={solved["density_allowance"]:.12g}, '
                          f'dual={solved["dual_lower_bound"]:.12g}', flush=True)
                    cases.append(result)
    return cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=BASE/'virtual_cell_averaged_replay')
    parser.add_argument('--controls', type=Path, default=BASE/'virtual_cell_averaged_controls')
    parser.add_argument('--output', type=Path, default=BASE/'virtual_cell_thermal_exchange')
    parser.add_argument('--strides', type=int, nargs='+', default=[2, 1])
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--monotone-thermal', action='store_true')
    parser.add_argument('--only-joint-radiation', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.workers <= 2 or min(args.strides) < 1:
        parser.error('one or two workers and positive temporal strides required')
    source, output = args.source.resolve(), args.output.resolve()
    if output.exists():
        raise RuntimeError('preserve completed thermal-exchange audit')
    paths = sorted(source.glob('*_factor4_states.npz'))
    if not paths:
        raise ValueError('factor4 independent replay archives required')
    files = [source/'manifest.json', BASE/'active_transfer_reservoir/metric_fine.npz',
        BASE/'active_transfer_reservoir/medium_baseline.npz', Path(__file__),
        Path(__file__).with_name('audit_virtual_cell_counterstream.py'),
        ROOT/'toolkit/adm_harness_cli/adm_harness/virtual_cell_thermal_exchange.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/virtual_cell_counterstream.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/active_transfer_reservoir.py',
        ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_thermal_exchange.py']
    checked = []
    for path in paths:
        summary = path.with_name(path.name.replace('_states.npz', '_summary.json'))
        control = find_control(source, json.loads(summary.read_text())['label'], args.controls)
        checks, manifest = verify_input_identity(source, path, control)
        checked.extend(checks)
        files.extend([path, summary, control, manifest,
                      control.with_name(control.name.replace('_states.npz', '_summary.json'))])
    hashes = {str(path.relative_to(ROOT)): sha256_file(path) for path in files}
    output.mkdir(parents=True)
    with ProcessPoolExecutor(max_workers=min(args.workers, len(paths)),
                             mp_context=multiprocessing.get_context('spawn')) as pool:
        groups = list(pool.map(evaluate, [(str(path), str(output), args.strides,
            args.monotone_thermal, args.only_joint_radiation) for path in paths]))
    cases = [case for group in groups for case in group]
    write_json(output/'summary.json', dict(cases=cases))
    write_json(output/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        workers=min(args.workers, len(paths)), input_sha256=hashes,
        immutable_input_checks=checked,
        output_sha256={path.name: sha256_file(path) for path in sorted(output.iterdir()) if path.is_file()}))


if __name__ == '__main__':
    main()
