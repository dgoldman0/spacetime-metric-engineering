#!/usr/bin/env python3
"""Bounded, parallel rail matching and interior regularity audit for condensates."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, replace
from datetime import datetime, timezone
import json
import multiprocessing
from pathlib import Path
import resource
import time

import numpy as np
import pandas as pd
from scipy.integrate import simpson, cumulative_simpson

from adm_harness.condensate_rail import (ExteriorBoundary, load_retained_geometry,
    continue_gravity, refine_exterior, validate_exterior, continue_inward)
from adm_harness.screened_condensate import CondensateParameters, field_stress
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]


def exterior_checks(solution, boundary, parameters):
    r = np.linspace(boundary.inner_radius, solution.x[-1], 24001)
    y = solution.sol(r)
    f, sigma = 1-2*y[6]/r, np.exp(y[7])
    t = field_stress(y[:6], solution.p[0], parameters, f, sigma)
    qm, qh = [4*np.pi*simpson(r*r*t[key]/np.sqrt(f), x=r)
              for key in ['matter_charge', 'higgs_charge']]
    flux = 4*np.pi*r*r*y[5]/sigma
    integrated_mass = 4*np.pi*boundary.gravity*simpson(r*r*t['energy'], x=r)
    cumulative = cumulative_simpson(r*r*t['energy'], x=r, initial=0)
    radii = np.interp(np.array([.05, .5, .95])*cumulative[-1], cumulative, r)/boundary.vacuum_scale
    k = (y[6]+4*np.pi*boundary.gravity*r**3*t['radial_pressure'])/(r*r*f)
    force = -(t['energy']+t['radial_pressure'])*k+2*(t['tangential_pressure']-t['radial_pressure'])/r
    dp = np.gradient(t['radial_pressure'], r, edge_order=2)
    active = (t['energy'] > np.max(t['energy'])*1e-8)
    active[:2] = False
    active[-2:] = False
    stress_scale = boundary.gravity*boundary.vacuum_scale**2
    return {'omega': float(solution.p[0]), 'gravity_Gv2': boundary.gravity,
        'eta_G_in_rail_units': boundary.gravity/boundary.vacuum_scale**2,
        'higgs_vacuum_scale': boundary.vacuum_scale,
        'inner_mass_rail_units': boundary.inner_mass/boundary.vacuum_scale,
        'adm_mass_rail_units': y[6, -1]/boundary.vacuum_scale,
        'sigma_inner': sigma[0], 'lapse_inner': sigma[0]*np.sqrt(f[0]),
        'inner_radial_pressure_rail_units': t['radial_pressure'][0]*stress_scale,
        'inner_matter_derivative': y[1, 0], 'inner_higgs_derivative': y[3, 0],
        'inner_gauge_potential': y[4, 0], 'inner_electric_derivative': y[5, 0],
        'matter_charge': qm, 'higgs_charge': qh,
        'net_charge_relative_error': abs(qm+qh)/abs(qm),
        'gauss_integral_relative_error': abs(qm+qh+flux[-1]-flux[0])/abs(qm),
        'outer_electric_flux_relative': abs(flux[-1])/abs(qm),
        'mass_integral_relative_error': abs(integrated_mass/(y[6, -1]-y[6, 0])-1),
        'inner_lapse_gradient_error': abs(k[0]-boundary.inner_lapse_gradient),
        'force_conservation_relative_error': np.max(abs(dp[active]-force[active]))/np.max(abs(force[active])),
        'energy_r05_rail_units': radii[0], 'energy_r50_rail_units': radii[1],
        'energy_r95_rail_units': radii[2], 'energy_peak_radius_rail_units': r[np.argmax(t['energy'])]/boundary.vacuum_scale,
        'maximum_collocation_residual': np.max(solution.rms_residuals),
        **validate_exterior(solution, boundary, parameters, boundary.gravity)}


def refine_task(task):
    seed, boundary, parameters, tolerance, extent, points = task
    started = time.monotonic()
    solution = refine_exterior(seed, boundary, parameters, tolerance=tolerance, extent=extent, points=points)
    row = {'tolerance': tolerance, 'extent': extent, 'initial_points': points,
        **exterior_checks(solution, boundary, parameters), 'seconds': time.monotonic()-started,
        'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    return solution, row


def inward_result(solution, boundary, parameters, geometry, kind, threshold, method, tolerance, max_step):
    started = time.monotonic()
    inward, metric = continue_inward(solution, boundary, parameters, geometry,
        kind=kind, threshold=threshold, method=method, tolerance=tolerance, max_step=max_step)
    x, field = inward.t[-1], inward.y[:, -1]
    radius, _, scale, *_ = metric.values(x)
    event = bool(len(inward.t_events[0]))
    # Leading large-field balance gives h ~ sqrt(2/mu)/(B*v*(x_pole-x))
    # and |u|/h -> sqrt(1-lambda/(2*mu)). This is an asymptotic diagnostic.
    pole_estimate = float(x+np.sqrt(2/parameters.matter_coupling)/(scale*boundary.vacuum_scale*field[2])) if event else None
    row = {'geometry': kind, 'amplitude_threshold': threshold, 'method': method,
        'ivp_tolerance': tolerance, 'max_step': max_step, 'reached_core_coordinate': not event,
        'amplitude_event': event, 'last_coordinate': x, 'last_areal_radius': radius,
        'last_matter_amplitude': field[0], 'last_higgs_amplitude': field[2],
        'last_gauge_potential': field[4], 'large_field_amplitude_ratio': abs(field[0]/field[2]),
        'predicted_large_field_ratio': np.sqrt(1-parameters.higgs_coupling/(2*parameters.matter_coupling)),
        'higgs_pole_slope_ratio': field[3]/field[2]**2/(scale*boundary.vacuum_scale*np.sqrt(parameters.matter_coupling/2)),
        'pole_coordinate_estimate': pole_estimate,
        'pole_radius_estimate': float(metric.values(pole_estimate)[0]) if event else None,
        'integration_steps': len(inward.t), 'seconds': time.monotonic()-started}
    return row, inward, metric


def inward_task(task):
    solution, boundary, parameters, geometry, exterior_tolerance, kind, threshold, method, tolerance, max_step = task
    row, inward, metric = inward_result(solution, boundary, parameters, geometry, kind, threshold, method, tolerance, max_step)
    row['exterior_tolerance'] = exterior_tolerance
    profile = None
    if exterior_tolerance == 1e-10 and threshold == 100. and method == 'DOP853':
        x = np.linspace(inward.t[0], inward.t[-1], 1201)
        field = inward.sol(x)
        profile = {'coordinate': x, 'areal_radius': np.array([metric.values(xx)[0] for xx in x]),
            'matter_field': field[0], 'matter_derivative': field[1], 'higgs_field': field[2],
            'higgs_derivative': field[3], 'gauge_potential': field[4], 'gauge_derivative': field[5]}
    return row, profile


def neighborhood_task(task):
    seed, boundary, parameters, geometry, matter, higgs = task
    local = replace(boundary, matter_amplitude=matter, higgs_amplitude=higgs)
    row = {'inner_matter_amplitude': matter, 'inner_higgs_amplitude': higgs}
    try:
        solution = refine_exterior(seed, local, parameters, tolerance=1e-7)
    except (RuntimeError, ValueError) as error:
        return {**row, 'exterior_converged': False, 'numerical_failure': str(error)}
    check, _, _ = inward_result(solution, local, parameters, geometry, 'retained', 100., 'DOP853', 1e-9, .004)
    return {**row, 'exterior_converged': True, **exterior_checks(solution, local, parameters), **check}


def plot(exterior, inward, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.7), constrained_layout=True)
    r = exterior['radius_rail_units']
    ax[0].plot(r, exterior['matter_field'], label='Matter')
    ax[0].plot(r, exterior['higgs_field'], label='Higgs')
    ax[0].plot(r, exterior['gauge_potential'], label='Gauge potential')
    ax[0].set(title='Matched gravitational exterior', xlim=(6.8, 25), xlabel='Areal radius, rail units')
    for key, label in [('energy', 'Energy'), ('radial_pressure', 'Radial pressure'), ('tangential_pressure', 'Angular pressure')]:
        ax[1].plot(r, exterior[key], label=label)
    ax[1].set(title='Full material tensor', xlim=(6.8, 25), xlabel='Areal radius, rail units', ylabel='Stress / Higgs vacuum scale⁴')
    for kind, profile in inward.items():
        ax[2].semilogy(profile['areal_radius'], np.maximum(abs(profile['higgs_field']), 1e-7), label=kind.capitalize()+' interior')
    ax[2].set(title='Inward Higgs-field growth', xlim=(6.8, 4.1), xlabel='Areal radius, rail units', ylabel='Higgs amplitude / vacuum amplitude')
    for panel in ax:
        panel.grid(alpha=.2)
        panel.legend(fontsize=8)
    fig.savefig(output, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/condensate_rail')
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    geometry = load_retained_geometry(ROOT)
    boundary, parameters = ExteriorBoundary.from_geometry(geometry), CondensateParameters()
    sources = [Path(__file__).resolve(), *(ROOT/'toolkit/adm_harness_cli/adm_harness'/name
        for name in ['screened_condensate.py', 'condensate_rail.py', 'curved_boundary.py']),
        ROOT/'supporting_reports/data/curved_quantum_boundary/geometry.npz',
        ROOT/'supporting_reports/data/curved_quantum_boundary/geometry.json']
    hashes = {str(path.relative_to(ROOT)): sha256_file(path) for path in sources}
    started = time.monotonic()
    seed, trace = continue_gravity(boundary, parameters)
    tasks = [(seed, boundary, parameters, tolerance, extent, points)
        for tolerance, extent, points in [(1e-6, 160., 2001), (1e-8, 160., 2001),
                                         (1e-10, 160., 2001), (1e-8, 200., 2601)]]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        refined = list(pool.map(refine_task, tasks))
        primary = refined[2][0]
        inward_tasks = [(solution, boundary, parameters, geometry, row['tolerance'], kind,
            threshold, method, tol, step)
            for solution, row in [refined[0], refined[2]]
            for kind in ['analytic', 'retained']
            for threshold, method, tol, step in [(10., 'DOP853', 1e-10, .004),
                (100., 'DOP853', 1e-10, .004), (1000., 'DOP853', 1e-11, .002),
                (100., 'Radau', 1e-10, .004)]]
        inward = list(pool.map(inward_task, inward_tasks))
        nearby = list(pool.map(neighborhood_task, [(primary, boundary, parameters, geometry, matter, higgs)
            for matter in [.9, 1., 1.1] for higgs in [.03, .05, .07]]))
    args.output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(trace).to_csv(args.output/'gravitational_continuation.csv', index=False)
    pd.DataFrame([row for _, row in refined]).to_csv(args.output/'exterior_refinements.csv', index=False)
    pd.DataFrame([row for row, _ in inward]).to_csv(args.output/'interior_regularities.csv', index=False)
    pd.DataFrame(nearby).to_csv(args.output/'boundary_neighborhood.csv', index=False)
    r = np.linspace(boundary.inner_radius, primary.x[-1], 2401)
    y = primary.sol(r)
    profile = {'radius_dimensionless': r, 'radius_rail_units': r/boundary.vacuum_scale,
        'matter_field': y[0], 'matter_derivative': y[1], 'higgs_field': y[2], 'higgs_derivative': y[3],
        'gauge_potential': y[4], 'gauge_derivative': y[5], 'mass_dimensionless': y[6], 'log_sigma': y[7],
        **field_stress(y[:6], primary.p[0], parameters, 1-2*y[6]/r, np.exp(y[7]))}
    pd.DataFrame(profile).to_csv(args.output/'exterior_profile.csv.gz', index=False)
    interior_profiles = {row['geometry']: data for row, data in inward if data is not None}
    for kind, data in interior_profiles.items():
        pd.DataFrame(data).to_csv(args.output/('interior_'+kind+'.csv.gz'), index=False)
    plot(profile, interior_profiles, args.output/'condensate_rail_profiles.png')
    for path in sources:
        if sha256_file(path) != hashes[str(path.relative_to(ROOT))]:
            raise RuntimeError('input changed during computation')
    manifest = {'created_utc': datetime.now(timezone.utc).isoformat(), 'workers': args.workers,
        'seconds': time.monotonic()-started, 'input_sha256': hashes, 'boundary': asdict(boundary),
        'couplings': asdict(parameters), 'retained_geometry_phase': .745,
        'model': 'Ishihara-Ogawa screened scalar and Higgs fields, static gravitational exterior',
        'primary_exterior_tolerance': 1e-10, 'reference': 'https://arxiv.org/abs/2409.07818',
        'full_perturbation_stability_evaluated': False, 'absolute_quantum_stress_evaluated': False,
        'quantum_stress_in_exterior_einstein_equations': False,
        'interior_metric': 'retained rail snapshot, time derivatives omitted for the stationary material gate',
        'inward_gate_counts': {'cases': len(inward),
            'reached_core_coordinate': sum(row['reached_core_coordinate'] for row, _ in inward)},
        'neighborhood_counts': {'cases': len(nearby),
            'exterior_converged': sum(row['exterior_converged'] for row in nearby),
            'reached_core_coordinate': sum(row.get('reached_core_coordinate', False) for row in nearby)},
        'output_sha256': {path.name: sha256_file(path) for path in args.output.iterdir()}}
    (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    size = sum(path.stat().st_size for path in args.output.iterdir())
    if manifest['seconds'] > 600 or size > 5e6:
        raise RuntimeError('bounded runtime or retained-size allowance exceeded')
    print(pd.DataFrame([row for _, row in refined])[
        ['tolerance', 'extent', 'omega', 'adm_mass_rail_units', 'net_charge_relative_error', 'maximum_original_equation_error']].to_string(index=False))
    print(pd.DataFrame(nearby)[['inner_matter_amplitude', 'inner_higgs_amplitude',
        'exterior_converged', 'reached_core_coordinate', 'last_areal_radius']].to_string(index=False))
    print(json.dumps({'seconds': manifest['seconds'], 'retained_bytes': size,
                     'interior': manifest['inward_gate_counts'], 'nearby': manifest['neighborhood_counts']}))


if __name__ == '__main__':
    main()
