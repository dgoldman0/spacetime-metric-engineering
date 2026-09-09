#!/usr/bin/env python3
"""Independent continuous radial ODE and refinement audit of spherical stress."""
from concurrent.futures import ProcessPoolExecutor
import argparse
import json
import multiprocessing
from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

from adm_harness.curved_boundary import (StaticGeometry, RadialProblem, placements,
    tensor_from_moments, mode_moments, frequency_quadrature)
from adm_harness.metric_regularity import regularized_scalars
from adm_harness.source_ledger import SourceParams, sha256_file

ROOT = Path(__file__).resolve().parents[3]
CHANNELS = ['energy', 'radial_pressure', 'angular_pressure', 'radial_enthalpy', 'angular_enthalpy']


def continuous_green(geometry, extent, frequency, angular_index, probes, walls):
    """Ordered homogeneous solutions via continuous logarithmic derivatives.

    This uses neither the finite-volume matrix nor its discrete Green columns.
    Dirichlet endpoint series initialize each homogeneous solution.
    """
    def equation(x, state):
        r, n, a = geometry.values(x)
        rl, nl, al = geometry.values(x, 1)
        logarithmic_p = nl+2*rl-al
        q_over_p = a*a*(angular_index*(angular_index+1)/(r*r)+frequency**2/(n*n))
        return [q_over_p-logarithmic_p*state[0]-state[0]**2, state[0]]
    epsilon = 1e-5
    solutions = []
    for direction in [1., -1.]:
        start = -direction*(extent-epsilon)
        rl, nl, al = geometry.values(start, 1)
        initial = [direction/epsilon-.5*(nl+2*rl-al), np.log(epsilon)]
        result = solve_ivp(equation, (start, direction*(extent-epsilon)), initial,
                           method='DOP853', rtol=2e-10, atol=2e-11, dense_output=True)
        if not result.success:
            raise RuntimeError(result.message)
        solutions.append(result.sol)
    left, right = solutions
    lw, rw = left(walls), right(walls)
    r, n, a = geometry.values(walls)
    diagonal = 1/((n*r*r/a)*(lw[0]-rw[0]))
    def samples(x):
        lx, rx = left(x), right(x)
        choose_left = np.asarray(x)[:, None] <= walls[None, :]
        exponent = np.where(choose_left, lx[1, :, None]-lw[1, None, :],
                            rx[1, :, None]-rw[1, None, :])
        columns = diagonal[None, :]*np.exp(exponent)
        derivative = columns*np.where(choose_left, lx[0, :, None], rx[0, :, None])
        return columns, derivative
    values, derivatives = samples(probes)
    wall_green, _ = samples(walls)
    return values, derivatives, wall_green


def ode_check(task):
    cache, finest, frequency, angular_index = task
    with np.load(cache) as data:
        geometry = StaticGeometry(**dict(data))
    metadata = json.loads((finest/'manifest.json').read_text())
    saved = np.load(finest/'angular_moments.npz')
    probes = saved['coordinate']; saved.close()
    walls = pd.read_csv(finest/'walls.csv', float_precision='round_trip').coordinate.to_numpy()
    continuous = continuous_green(geometry, metadata['extent'], frequency, angular_index, probes, walls)
    rows = []
    for refinement in [1, 2, 4]:
        spacing = metadata['spacing']/refinement
        problem = RadialProblem.create(geometry, spacing, metadata['extent'], walls, probes)
        discrete = problem.samples(problem.green_columns(frequency, angular_index))
        for case in placements():
            ix = np.array(case['indices'])
            rw, nw, _ = geometry.values(walls[ix])
            tensors = []
            for values, derivatives, green in [continuous, discrete]:
                # A direct inverse and quadratic contractions form an independent
                # stress assembly from the two sets of radial solutions.
                inverse = np.linalg.inv(green[np.ix_(ix, ix)]+np.diag(1/(case['coupling']*nw*rw*rw)))
                diagonal = -np.einsum('pi,ij,pj->p', values[:, ix], inverse, values[:, ix])
                radial = -np.einsum('pi,ij,pj->p', derivatives[:, ix], inverse, derivatives[:, ix])
                r, n, a = geometry.values(probes)
                time_part, normal_part = -frequency**2*diagonal/(n*n), radial/(a*a)
                angular_part = angular_index*(angular_index+1)*diagonal/(2*r*r)
                tensors.append(np.stack([.5*(time_part+normal_part+2*angular_part),
                    .5*(time_part+normal_part-2*angular_part), .5*(time_part-normal_part)], axis=-1))
            scale = np.max(np.abs(tensors[0]), axis=1)
            relative = np.max(np.abs(tensors[1]-tensors[0]), axis=1)/np.maximum(scale, 1e-24)
            for i, error in enumerate(relative):
                rows.append({'frequency': frequency, 'angular_index': angular_index,
                    'core_spacing': spacing, 'spatial_refinement': refinement,
                    'arrangement': case['name'], 'coupling': case['coupling'], 'coordinate': probes[i],
                    'mode_tensor_scale': scale[i], 'relative_tensor_error': error})
    return rows


def conservation_mode(task):
    cache, finest, angular_index = task
    with np.load(cache) as data:
        geometry = StaticGeometry(**dict(data))
    metadata = json.loads((finest/'manifest.json').read_text())
    with np.load(finest/'angular_moments.npz') as data:
        original_probes = data['coordinate']
    probes = np.unique(np.r_[original_probes, -1.5+np.array([-.032, -.016, -.008, -.004, 0, .004, .008, .016, .032])])
    walls = pd.read_csv(finest/'walls.csv', float_precision='round_trip').coordinate.to_numpy()
    problem = RadialProblem.create(geometry, metadata['spacing'], metadata['extent'], walls, probes)
    frequencies, weights = frequency_quadrature(metadata['frequency_nodes'], metadata['frequency_upper'], metadata['frequency_lower'])
    result = np.zeros((len(placements()), len(probes), 3))
    for frequency, weight in zip(frequencies, weights):
        result += weight*mode_moments(problem, frequency, angular_index)
    return probes, result*(2*angular_index+1)/(4*np.pi**2)


def refined_conservation(root, finest, results):
    from run_curved_boundary import conservation_rows
    probes = results[0][0]
    tensor = tensor_from_moments(sum(value for _, value in results))
    with np.load(root/'geometry.npz') as data:
        geometry = StaticGeometry(**dict(data))
    records = []
    for step in [.016, .008, .004]:
        records.extend([dict(row, stencil_step=step) for row in
            conservation_rows(geometry, probes, tensor, np.array([-1.5]), step)])
    pd.DataFrame(records).to_csv(root/'refined_conservation.csv', index=False)
    # The saved full angular sum independently bounds the omitted tail at
    # the five original stencil positions; nine modes exceed that requirement.
    with np.load(finest/'angular_moments.npz') as data:
        ix = np.flatnonzero(np.abs(data['coordinate']+1.5) < .033)
        full = tensor_from_moments(data['moments'][:, :, ix].sum(axis=0))
        low = tensor_from_moments(data['moments'][:9, :, ix].sum(axis=0))
    tail = np.max(np.max(np.abs(full-low), axis=-1)/np.maximum(np.max(np.abs(full), axis=-1), 1e-30))
    return records, float(tail)


def read_tensor(directory, angular_count=None):
    with np.load(directory/'angular_moments.npz') as data:
        moments = data['moments']
        if angular_count is not None:
            moments = moments[:angular_count]
        return tensor_from_moments(moments.sum(axis=0))


def comparison(name, first, second, first_count=None, second_count=None):
    a, b = read_tensor(first, first_count), read_tensor(second, second_count)
    errors = np.max(np.abs(a-b), axis=-1)/np.maximum(np.max(np.abs(b), axis=-1), 1e-30)
    outer = [i for i, case in enumerate(placements()) if case['name'] == 'outer']
    return {'comparison': name, 'max_relative_tensor_difference': float(errors.max()),
        'outer_max_relative_tensor_difference': float(errors[outer].max())}


def audit_geometry(root):
    with np.load(root/'geometry.npz') as data:
        geometry = StaticGeometry(**dict(data))
    reference = pd.read_csv(ROOT/'supporting_reports/data/comer_two_current/reference_initial_profile.csv', float_precision='round_trip')
    x = geometry.negative_branch_coordinate(reference.radius.to_numpy())
    r, n, a = geometry.values(x); rl, _, _ = geometry.values(x, 1)
    f = (r*rl/a)**2
    parameters = SourceParams(**json.loads((ROOT/'supporting_reports/data/le_coupled_reset_source/manifest.json').read_text())['params'])
    interpolation = []
    for coordinate in np.linspace(-2.5, 2.5, 257)+.00027:
        exact = regularized_scalars(.745, float(coordinate), parameters)
        metric = np.array([np.sqrt(exact['gamma_omega']), exact['alpha'], np.sqrt(exact['gamma_ll'])])
        interpolation.append(np.abs(np.array(geometry.values(coordinate))/metric-1))
    return {'reference_radius_relative_error': float(np.max(np.abs(r/reference.radius-1))),
        'reference_lapse_relative_error': float(np.max(np.abs(n/reference.alpha-1))),
        'reference_f_relative_error': float(np.max(np.abs(f/reference.f-1))),
        'reference_f_absolute_error': float(np.max(np.abs(f-reference.f))),
        'off_grid_metric_interpolation_relative_error': float(np.max(interpolation))}


def plot_profiles(frame, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figure, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    chosen = frame[frame.main_witness & frame.coupling.eq(8.)].sort_values('radius')
    for name, label in [('inner_pair', 'two inner sheets'), ('outer', 'outer sheet'), ('spanning_pair', 'spanning pair')]:
        local = chosen[chosen.arrangement.eq(name)]
        for ax, channel in zip(axes, ['radial_enthalpy', 'angular_enthalpy']):
            ax.plot(local.radius, local[channel], label=label)
    local = chosen[chosen.arrangement.eq('outer')]
    for ax, channel, label in zip(axes, ['radial_enthalpy', 'angular_enthalpy'], ['Radial null channel', 'Angular null channel']):
        ax.plot(local.radius, local['demanded_'+channel], color='black', linestyle='--', label='rail demand')
        ax.set(xlabel='areal radius', ylabel='null-channel stress', title=label,
               yscale='symlog', ylim=(-.06, .08))
        ax.set_yscale('symlog', linthresh=1e-7)
        ax.axhline(0., color='gray', linewidth=.5)
        ax.axvspan(2.15, 2.945503, color='gray', alpha=.08)
        ax.grid(alpha=.2)
        ax.legend(fontsize=8)
    figure.savefig(output, dpi=160)
    plt.close(figure)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT/'supporting_reports/data/curved_quantum_boundary')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    started = time.monotonic()
    finest = args.root/'final_extent_384'
    pairs = [('core_128_to_256', 'spatial_128', 'spatial_256', None, None),
             ('core_256_to_512', 'spatial_256', 'spatial_512', None, None),
             ('frequency_96_to_144', 'spatial_512', 'spectrum_96', 65, 65),
             ('angular_64_to_96', 'spectrum_96', 'spectrum_96', 65, None),
             ('extent_48_to_96', 'spectrum_96', 'extent_96', None, None),
             ('frequency_144_to_192_and_endpoints', 'extent_96', 'spectrum_128', 97, 97),
             ('angular_96_to_128', 'spectrum_128', 'spectrum_128', 97, None),
             ('core_512_to_1024', 'spectrum_128', 'spatial_1024', None, None),
             ('core_1024_to_2048', 'spatial_1024', 'spatial_2048', None, None),
             ('extent_96_to_384', 'spectrum_128', 'extent_384', None, None),
             ('extent_384_to_1536', 'extent_384', 'extent_1536', None, None)]
    comparisons = [comparison(name, args.root/a, args.root/b, ac, bc) for name, a, b, ac, bc in pairs]
    pd.DataFrame(comparisons).to_csv(args.root/'convergence.csv', index=False)
    tasks = [(args.root/'geometry.npz', finest, frequency, angular_index)
             for frequency in [.03, .3, 3.] for angular_index in [0, 1, 4]]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        records = [row for group in pool.map(ode_check, tasks) for row in group]
        print(f'continuous ODE checks complete after {time.monotonic()-started:.1f} s', flush=True)
        stencil_results = list(pool.map(conservation_mode, [(args.root/'geometry.npz', finest, j) for j in range(9)]))
    ode = pd.DataFrame(records)
    ode.to_csv(args.root/'continuous_ode_audit.csv.gz', index=False)
    stencil_rows, stencil_tail = refined_conservation(args.root, finest, stencil_results)
    stencil = pd.DataFrame(stencil_rows)
    refined_ode_error = float(ode[ode.spatial_refinement.eq(4)].relative_tensor_error.max())
    frame = pd.read_csv(finest/'boundary_profiles.csv.gz', float_precision='round_trip')
    summaries = []
    for (name, coupling), group in frame[frame.main_witness].groupby(['arrangement', 'coupling']):
        required = group.demanded_angular_enthalpy < 0
        summaries.append({'arrangement': name, 'coupling': coupling, 'witnesses': len(group),
            'negative_radial_response': int((group.radial_enthalpy < 0).sum()),
            'negative_angular_demand': int(required.sum()),
            'negative_angular_response_where_required': int(((group.angular_enthalpy < 0)&required).sum()),
            'simultaneous_negative_response_where_required': int(((group.angular_enthalpy < 0)&(group.radial_enthalpy < 0)&required).sum())})
    pd.DataFrame(summaries).to_csv(args.root/'placement_summary.csv', index=False)
    source_match = True
    for manifest_path in args.root.glob('*/manifest.json'):
        metadata = json.loads(manifest_path.read_text())
        source_match &= metadata['geometry_cache_sha256'] == sha256_file(args.root/'geometry.npz')
        for key, value in metadata['source_hashes'].items():
            source_match &= sha256_file(ROOT/key) == value
    geometry_check = audit_geometry(args.root)
    conservation = pd.read_csv(finest/'conservation.csv', float_precision='round_trip')
    combined_conservation_error = max(float(conservation[~conservation.coordinate.eq(-1.5)].relative_residual.abs().max()),
        float(stencil[stencil.stencil_step.eq(.004)].relative_residual.abs().max()))
    plot_profiles(frame, args.root/'curved_boundary_response.png')
    checks = {'source_hashes_match': bool(source_match),
        'reference_metric_agrees_below_0p000001': geometry_check['reference_f_relative_error'] < 1e-6
            and geometry_check['reference_lapse_relative_error'] < 1e-6,
        'metric_interpolation_agrees_below_0p00000001': geometry_check['off_grid_metric_interpolation_relative_error'] < 1e-8,
        'final_spatial_difference_below_0p002': comparisons[8]['max_relative_tensor_difference'] < .002,
        'outer_spatial_difference_below_0p00002': comparisons[8]['outer_max_relative_tensor_difference'] < 2e-5,
        'last_frequency_difference_below_0p0001': comparisons[5]['max_relative_tensor_difference'] < 1e-4,
        'last_angular_tail_below_0p0001': comparisons[6]['max_relative_tensor_difference'] < 1e-4,
        'outer_end_boundary_difference_below_0p001': comparisons[10]['outer_max_relative_tensor_difference'] < .001,
        'refined_continuous_ode_agrees_below_0p002': refined_ode_error < .002,
        'conservation_stencil_omitted_angular_tail_below_1e_m10': stencil_tail < 1e-10,
        'refined_conservation_relative_residual_below_0p0001': combined_conservation_error < 1e-4}
    result = {'elapsed_seconds': time.monotonic()-started, 'workers': args.workers,
        'ode_modes': len(tasks), 'ode_tensor_checks': len(ode),
        'max_continuous_ode_relative_tensor_error': float(ode.relative_tensor_error.max()),
        'max_refined_continuous_ode_relative_tensor_error': refined_ode_error,
        'continuous_ode_errors_by_refinement': {str(key): float(value) for key, value in ode.groupby('spatial_refinement').relative_tensor_error.max().items()},
        'max_conservation_relative_residual': float(conservation.relative_residual.abs().max()),
        'max_refined_conservation_relative_residual': combined_conservation_error,
        'conservation_errors_by_stencil_step': {str(key): float(value) for key, value in stencil.groupby('stencil_step').relative_residual.apply(lambda x: x.abs().max()).items()},
        'conservation_stencil_omitted_angular_tail': stencil_tail,
        'comparisons': comparisons, 'geometry_check': geometry_check, 'checks': checks, 'passed': bool(all(checks.values())),
        'audit_script_sha256': sha256_file(Path(__file__))}
    (args.root/'audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    if not result['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
