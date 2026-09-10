#!/usr/bin/env python3
"""Audit explicit field response, source compensation, and physical scale."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import argparse
import json
import multiprocessing
from pathlib import Path

import numpy as np
import pandas as pd

from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.metric_regularity import regularized_scalars
from adm_harness.reservoir_feasibility import (
    classical_completion_requirement, field_decomposition,
    minimize_initial_null_requirement, radial_null, scale_coefficients,
    taub_mathews_pressure,
)
from adm_harness.source_ledger import SourceParams, sha256_file
from audit_prestressed_buffer_assembly import load_assembly
from audit_material_ensemble import load_case
from run_active_transfer_reservoir import parameters

ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = ROOT/'supporting_reports/data/prestressed_buffer_assembly/finite_stiffness'
OUTPUT = ROOT/'supporting_reports/data/reservoir_feasibility'
CHANNELS = ('rho', 'p_l', 'j_l', 'p_omega')


def source_at(t, x, params, evaluator, step):
    value = evaluate_demand(float(t), float(x), params, step, step,
                            scalar_evaluator=evaluator)
    return np.array([value[k] for k in CHANNELS])


def run_case(task):
    label, cells, output = task
    if label == 'prior_thermal':
        archive_name = 'relaxing/thermal_only_baseline_n64_end3_dt0.0005_snap601_cfl0.05'
        _, patch, times, states, _ = load_case(archive_name)
        source_files = [ROOT/'supporting_reports/data/material_ensemble'/
                        (archive_name+suffix) for suffix in ('_summary.json', '_states.npz')]
    else:
        source_path = ARCHIVE/f'{label}_n{cells}_end1.285_dt0.0005_cfl0.05_summary.json'
        _, patch, times, states = load_assembly(source_path)
        source_files = [source_path, source_path.with_name(source_path.name.replace('_summary.json', '_states.npz'))]
    params = SourceParams(**parameters())
    name = f'{label}_n{cells}'
    inputs_before = {str(p.relative_to(ROOT)):sha256_file(p) for p in source_files}

    def spline_scalars(t, x, unused):
        g = patch.model.metric(t, np.array([x]))
        return dict(alpha=float(g.alpha[0]), beta=float(g.beta[0]),
                    gamma_ll=float(g.b[0]**2), gamma_omega=float(g.radius[0]**2))

    rows, phases, optimizations = [], [], []
    requested = (0., .5, .815) if label == 'prior_thermal' else (0., .5, 1.285)
    for target in requested:
        index = int(np.argmin(abs(times-target)))
        t = float(times[index])
        if abs(t-target) > .003:
            continue
        state = states[index]
        f = patch.fields(t, state)
        g, volume = f['metric'], f['volume']
        factor = patch.law.scale/(volume*g.radius**2)
        supplied = factor*np.array([f['energy_int'], f['radial_int'],
                                    f['current_int'], np.zeros_like(volume)])
        medium = patch.model.medium(t, f['x'])[0]
        demands, coarse, spline = [np.empty_like(supplied) for _ in range(3)]
        for i, x in enumerate(f['x']):
            demands[:, i] = source_at(t, x, params, regularized_scalars, .00125)
            coarse[:, i] = source_at(t, x, params, regularized_scalars, .0025)
            spline[:, i] = source_at(t, x, params, spline_scalars, .00125)
        remainder, required = classical_completion_requirement(demands, medium+supplied)
        _, prior_required = classical_completion_requirement(demands, medium)
        _, spline_required = classical_completion_requirement(spline, medium+supplied)
        labels = np.r_[0., np.cumsum(patch.reference)]/patch.reference.sum()
        bulk = (labels >= .15) & (labels <= .85)
        measure = 4*np.pi*g.b*volume*g.radius**2
        row = dict(case=name, s=t, maximum_negative_null_requirement=float(required.max()),
                   maximum_bulk_negative_null_requirement=float(required[:, bulk].max()),
                   maximum_requirement_before_reservoir=float(prior_required.max()),
                   maximum_geometry_abs_null=float(abs(radial_null(demands)).max()),
                   maximum_geometry_fd_difference=float(abs(demands-coarse).max()),
                   maximum_geometry_spline_difference=float(abs(demands-spline).max()),
                   maximum_requirement_spline_difference=float(abs(required-spline_required).max()),
                   required_negative_slice_energy_integral=float(np.dot(measure, np.maximum(-remainder[0], 0.))),
                   slice_energy=float(np.dot(measure, supplied[0])),
                   material_fraction_requiring_negative_null=float(np.dot(patch.mass/patch.mass.sum(),
                                                                                 required.max(axis=0) > 1e-8)),
                   maximum_density=float(supplied[0].max()), maximum_abs_radial_pressure=float(abs(supplied[1]).max()))
        decomposition = None
        if label != 'prior_thermal':
            decomposition = field_decomposition(patch, t, state)
            qpressure = taub_mathews_pressure(decomposition['rest_mass'], f['heat'])
            scales = scale_coefficients(decomposition['magnetic'], supplied[0], row['slice_energy'])
            row.update(decomposition_absolute_error=decomposition['decomposition_absolute_error'],
                       maximum_magnetic_rest_energy=float(decomposition['magnetic'].max()),
                       minimum_magnetization=float(decomposition['sigma'].min()),
                       maximum_magnetization=float(decomposition['sigma'].max()),
                       maximum_gas_pressure_over_magnetic=float(np.max(qpressure/np.maximum(decomposition['magnetic'], 1e-30))),
                       maximum_gas_pressure_over_buffer_energy=float(np.max(qpressure/decomposition['buffer'])),
                       magnetic_tesla_metres=float(scales['magnetic_tesla_metres'].max()),
                       peak_energy_density_joule_metres_inverse=float(scales['pressure_pascal_metres_squared'].max()),
                       slice_energy_joules_per_metre=float(scales['slice_energy_joules_per_metre']))
        worst = np.unravel_index(np.argmax(required), required.shape)
        row.update(worst_null_direction=1 if worst[0] == 0 else -1,
                   worst_material_fraction=float(labels[worst[1]]), worst_x=float(f['x'][worst[1]]),
                   worst_geometry_null=float(radial_null(demands)[worst]),
                   worst_supplied_null=float(radial_null(medium+supplied)[worst]))
        phases.append(row)
        for i, x in enumerate(f['x']):
            local = dict(case=name, s=t, node=i, fraction=float(labels[i]), l=float(x),
                         velocity=float(f['velocity'][i]), heat=float(f['heat'][i]),
                         required_negative_null_plus=float(required[0, i]),
                         required_negative_null_minus=float(required[1, i]),
                         required_before_plus=float(prior_required[0, i]), required_before_minus=float(prior_required[1, i]),
                         fd_error=float(abs(demands[:, i]-coarse[:, i]).max()),
                         spline_error=float(abs(demands[:, i]-spline[:, i]).max()))
            for prefix, values in (('geometry', demands), ('reservoir', supplied), ('endpoint', medium), ('remainder', remainder)):
                local.update({prefix+'_'+key:float(values[k, i]) for k, key in enumerate(CHANNELS)})
            if decomposition is not None:
                local.update({key:float(decomposition[key][i]) for key in
                              ('magnetic', 'string', 'buffer', 'rest_mass', 'sigma', 'fast_speed2', 'extra_enthalpy_at_speed_half')})
                local['gas_pressure'] = float(qpressure[i])
            rows.append(local)
        if label == 'equilibrated' and t == 0:
            for speed in (0., .3, .5):
                result = minimize_initial_null_requirement(patch, demands, medium, minimum_sound_speed=speed)
                result.update(minimum_sound_speed_requested=speed, case=name)
                optimizations.append(result)
        print(f'{name} s={t:.6g}: negative-null requirement={row["maximum_negative_null_requirement"]:.7g}; '
              f'bulk={row["maximum_bulk_negative_null_requirement"]:.7g}; fd={row["maximum_geometry_fd_difference"]:.3g}', flush=True)
    for path, expected in inputs_before.items():
        if sha256_file(ROOT/path) != expected:
            raise RuntimeError('input changed during audit: '+path)
    pd.DataFrame(rows).to_csv(output/(name+'_points.csv'), index=False)
    result = dict(phases=phases, preload_optimization=optimizations, input_sha256=inputs_before)
    (output/(name+'_summary.json')).write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    args.output.mkdir(parents=True, exist_ok=True)
    software = [Path(__file__), ROOT/'toolkit/adm_harness_cli/scripts/audit_prestressed_buffer_assembly.py',
                ROOT/'toolkit/adm_harness_cli/scripts/audit_material_ensemble.py']
    software += [ROOT/'toolkit/adm_harness_cli/adm_harness'/name for name in (
        'reservoir_feasibility.py', 'prestressed_buffer_assembly.py', 'material_ensemble.py',
        'relaxing_material_ensemble.py', 'active_transfer_reservoir.py', 'elastic_endpoint_reservoir.py',
        'electrothermal_endpoint.py', 'geometry_boundary.py', 'radial_stress.py',
        'metric_regularity.py', 'source_ledger.py')]
    inputs = [ROOT/'supporting_reports/data/active_transfer_reservoir'/name for name in ('metric_fine.npz', 'medium_baseline.npz')]
    inputs += [ROOT/'supporting_reports/data/le_metric_c2_repair/manifest.json']
    hashes = {str(p.relative_to(ROOT)):sha256_file(p) for p in software+inputs}
    tasks = [('equilibrated', 64, args.output), ('equilibrated', 128, args.output),
             ('energy_matched', 64, args.output), ('prior_thermal', 64, args.output)]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(run_case, tasks))
    for path, expected in hashes.items():
        if sha256_file(ROOT/path) != expected:
            raise RuntimeError('software or background changed during audit: '+path)
    phases = [row for result in results for row in result['phases']]
    pd.DataFrame(phases).to_csv(args.output/'phase_summary.csv', index=False)
    manifest = dict(completed_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
                    scope='full active geometric tensor and reconstructed endpoint; archived evolved reservoir states; local averaged Maxwell/string decomposition; no magnetic return or confinement solution and no assumed quantum capacity',
                    software_and_background_sha256=hashes,
                    output_sha256={p.name:sha256_file(p) for p in sorted(args.output.glob('*')) if p.suffix in ('.json', '.csv') and p.name != 'manifest.json'})
    (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
