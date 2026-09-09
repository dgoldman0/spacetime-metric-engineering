#!/usr/bin/env python3
"""Bounded branch location, metric continuation and joint-condensate audit."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, replace
from datetime import datetime, timezone
import json
import multiprocessing
from pathlib import Path
import resource
import signal
import time

import numpy as np
import pandas as pd

from adm_harness.condensate_joint import (JointParameters, JointGeometry, solve_joint,
    joint_checks, physical_parameters)
from adm_harness.condensate_joint_audit import integral_audit, remainder_profile
from adm_harness.condensate_rail import load_retained_geometry
from adm_harness.screened_condensate import CondensateParameters, field_stress
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]


def timeout(*args):
    raise TimeoutError('registered relaxation time limit')


def accepted(row, tolerance=2e-5):
    return (row.get('solver_success', False) and row.get('chart_and_asymptotic_mass_gap', False)
        and row['maximum_equation_error'] < 25*tolerance and row['maximum_boundary_error'] < tolerance)


def locate(task):
    inner, frequency, transition, kind = task
    material = CondensateParameters()
    setup = JointParameters(inner_radius=inner, local_frequency_fraction=frequency, metric_fraction=0.)
    geometry = JointGeometry(load_retained_geometry(ROOT), setup)
    name = f'r{inner:g}_q{frequency:g}_{kind}_x{transition:g}'
    row = {'case': name, 'inner_radius': inner, 'frequency_fraction': frequency,
        'transition_seed': transition, 'kind': kind}
    started = time.monotonic()
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(35)
    solution = None
    try:
        solution = solve_joint(geometry, material, kind=kind, inner_transition=transition,
                               points=1201, max_nodes=12000)
        row.update(joint_checks(solution, geometry, material))
    except (RuntimeError, ValueError, TimeoutError) as error:
        row['numerical_failure'] = str(error)
    finally:
        signal.alarm(0)
    row.update(seconds=time.monotonic()-started, accepted=accepted(row))
    return row, solution if row['accepted'] else None, geometry


def continue_metric(result):
    initial, solution, geometry = result
    retained, material = load_retained_geometry(ROOT), CondensateParameters()
    fraction, step = 0., .025
    rows, started = [], time.monotonic()
    signal.signal(signal.SIGALRM, timeout)
    for iteration in range(80):
        target = min(1., fraction+step)
        trial_geometry = JointGeometry(retained, replace(geometry.parameters, metric_fraction=target))
        row = {'case': initial['case'], 'metric_fraction': target, 'iteration': iteration}
        tick = time.monotonic()
        try:
            signal.alarm(25)
            trial = solve_joint(trial_geometry, material, seed=(solution, geometry),
                                points=1601, max_nodes=18000)
            row.update(joint_checks(trial, trial_geometry, material))
        except (RuntimeError, ValueError, TimeoutError) as error:
            row['numerical_failure'] = str(error)
        finally:
            signal.alarm(0)
        row.update(seconds=time.monotonic()-tick, accepted=accepted(row))
        rows.append(row)
        if row['accepted']:
            solution, geometry, fraction = trial, trial_geometry, target
            if target == 1.:
                break
            step = min(step*1.3, .08)
        else:
            step *= .5
            if step < .0004:
                break
        if time.monotonic()-started > 180:
            break
    summary = {'case': initial['case'], 'final_metric_fraction': fraction, 'attempts': len(rows),
        'seconds': time.monotonic()-started, **joint_checks(solution, geometry, material)}
    return summary, solution, geometry, rows


def refine(task):
    summary, seed, old_geometry, tolerance, far = task
    setup = replace(old_geometry.parameters, positive_extent=far,
                    exterior_extent=200. if far > 48 else 160.)
    retained, material = load_retained_geometry(ROOT), CondensateParameters()
    geometry = JointGeometry(retained, setup)
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(50)
    started = time.monotonic()
    try:
        solution = solve_joint(geometry, material, seed=(seed, old_geometry), tolerance=tolerance,
                               points=2401, max_nodes=30000)
        row = joint_checks(solution, geometry, material)
        if not accepted(row, tolerance):
            raise RuntimeError('refinement failed original-equation or boundary audit')
        row.update(integral_audit(solution, geometry, material))
    finally:
        signal.alarm(0)
    row.update(case=summary['case'], tolerance=tolerance, positive_extent=far,
        exterior_extent=setup.exterior_extent, seconds=time.monotonic()-started,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return row, solution, geometry


def save_primary(row, solution, geometry, output, retained):
    material = CondensateParameters()
    setup = geometry.parameters
    gravity, clock, omega = physical_parameters(solution.p, setup, material)
    name = row['case']
    np.savez_compressed(output/(name+'_solution.npz'), knots=solution.sol.x,
        coefficients=solution.sol.c, eigenparameters=solution.p,
        **{key: value for key, value in asdict(setup).items()})
    x = np.unique(np.r_[np.linspace(geometry.x_start, 8., 4001), np.linspace(8., setup.positive_extent, 801)])
    t = geometry.fraction_at_coordinate(x)
    y = solution.sol(t)[8:]
    r, a, _, _ = geometry.values(t)
    core = {'coordinate': x, 'radius': r, 'proper_coordinate': t*geometry.length,
        'lapse': clock*a, 'matter_field': y[0], 'matter_derivative': y[1],
        'higgs_field': y[2], 'higgs_derivative': y[3], 'gauge_potential': y[4], 'gauge_derivative': y[5],
        **field_stress(y, omega, material, 1., clock*a)}
    pd.DataFrame(core).to_csv(output/(name+'_interior.csv.gz'), index=False)
    r = np.linspace(setup.inner_radius, setup.exterior_extent, 2401)
    y = solution.sol((r-setup.inner_radius)/(setup.exterior_extent-setup.inner_radius))[:8]
    outer = {'radius': r/setup.vacuum_scale, 'matter_field': y[0], 'matter_derivative': y[1],
        'higgs_field': y[2], 'higgs_derivative': y[3], 'gauge_potential': y[4], 'gauge_derivative': y[5],
        'mass': y[6]/setup.vacuum_scale, 'log_sigma': y[7],
        **field_stress(y[:6], omega, material, 1-2*y[6]/r, np.exp(y[7]))}
    pd.DataFrame(outer).to_csv(output/(name+'_exterior.csv.gz'), index=False)
    remainder = remainder_profile(solution, geometry, material, retained)
    pd.DataFrame(remainder).to_csv(output/(name+'_required_remainder.csv.gz'), index=False)
    additional = {}
    for channel in ['radial', 'angular']:
        target = remainder['required_'+channel+'_enthalpy']
        host = remainder['material_'+channel+'_enthalpy']
        selected = target < 0
        ratio = host[selected]/-target[selected]
        additional.update({channel+'_negative_required_count': int(np.count_nonzero(selected)),
            channel+'_material_burden_ratio_median': float(np.median(ratio)),
            channel+'_material_burden_ratio_maximum': float(np.max(ratio)),
            channel+'_maximum_material_enthalpy': float(np.max(host[selected]))})
    return {**row, **additional}, (core, outer, remainder)


def plot(profiles, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(len(profiles), 3, figsize=(12, 3.3*len(profiles)), constrained_layout=True, squeeze=False)
    for panels, (name, (core, outer, remainder)) in zip(axes, profiles.items()):
        for key, label in [('matter_field', 'Matter'), ('higgs_field', 'Higgs'), ('gauge_potential', 'Gauge')]:
            panels[0].plot(core['coordinate'], core[key], label=label)
            panels[1].plot(outer['radius'], outer[key], label=label)
        panels[0].set(xlim=(-6.8, 8), xlabel='Interior coordinate', title=name)
        panels[1].set(xlim=(6.8, 25), xlabel='Exterior areal radius', title='Matched outer fields')
        for prefix, label in [('required_', 'Rail requirement'), ('material_', 'Condensate'), ('remainder_', 'Remaining source')]:
            panels[2].plot(remainder['radius'], remainder[prefix+'radial_enthalpy'], label=label)
        panels[2].set(yscale='symlog', ylim=(-.04, .0001), xlabel='Negative-branch areal radius', title='Radial null stress, rail units')
        panels[2].set_yscale('symlog', linthresh=1e-6)
        for ax in panels:
            ax.grid(alpha=.2)
            ax.legend(fontsize=7)
    fig.savefig(output, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/condensate_joint')
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    source_names = ['screened_condensate.py', 'condensate_rail.py', 'condensate_joint.py',
                    'condensate_joint_audit.py', 'curved_boundary.py']
    sources = [Path(__file__).resolve(), *(ROOT/'toolkit/adm_harness_cli/adm_harness'/name for name in source_names),
        ROOT/'supporting_reports/data/curved_quantum_boundary/geometry.npz',
        ROOT/'supporting_reports/data/curved_quantum_boundary/geometry.json']
    hashes = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    started = time.monotonic()
    tasks = [(inner, q, transition, 'potential') for inner in [12., 20.]
             for q in [.7, .85, .97] for transition in [0., 2.]]
    tasks += [(20., q, 0., 'hollow') for q in [.7, .85, .97]]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        located = list(pool.map(locate, tasks))
        print('Auxiliary solutions:', sum(row['accepted'] for row, _, _ in located), flush=True)
        continued = list(pool.map(continue_metric, [r for r in located if r[0]['accepted']]))
        full = [r for r in continued if r[0]['final_metric_fraction'] == 1.]
        print('Retained-geometry solutions:', len(full), flush=True)
        refined = list(pool.map(refine, [(row, solution, geometry, tol, far)
            for row, solution, geometry, _ in full
            for tol, far in [(1e-5, 48.), (1e-6, 48.), (1e-8, 48.), (1e-8, 64.)]]))
    args.output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([row for row, _, _ in located]).to_csv(args.output/'branch_location.csv', index=False)
    pd.DataFrame([row for row, _, _, _ in continued]).to_csv(args.output/'continuation_summary.csv', index=False)
    pd.DataFrame([row for _, _, _, rows in continued for row in rows]).to_csv(args.output/'continuation_trace.csv', index=False)
    pd.DataFrame([row for row, _, _ in refined]).to_csv(args.output/'refinements.csv', index=False)
    summaries, profiles = [], {}
    retained = load_retained_geometry(ROOT)
    for row, solution, geometry in refined:
        if row['tolerance'] == 1e-8 and row['positive_extent'] == 48.:
            summary, profile = save_primary(row, solution, geometry, args.output, retained)
            summaries.append(summary)
            profiles[row['case']] = profile
    pd.DataFrame(summaries).to_csv(args.output/'primary_summaries.csv', index=False)
    if profiles:
        plot(profiles, args.output/'joint_condensate_profiles.png')
    for path in sources:
        if sha256_file(path) != hashes[str(path.relative_to(ROOT))]:
            raise RuntimeError('input changed during the registered run')
    manifest = {'created_utc': datetime.now(timezone.utc).isoformat(), 'workers': args.workers,
        'seconds': time.monotonic()-started, 'input_sha256': hashes,
        'branch_location_cases': len(tasks), 'auxiliary_solutions': sum(r[0]['accepted'] for r in located),
        'full_retained_solutions': len(full), 'refinements': len(refined),
        'preferred_branch': 'r12_q0.85_potential_x2',
        'couplings': asdict(CondensateParameters()),
        'core_einstein_source': 'required quantum remainder measured; quantum expectation unevaluated',
        'coupled_angular_stability_evaluated': False, 'time_dependent_rail_service_evaluated': False,
        'output_sha256': {p.name: sha256_file(p) for p in args.output.iterdir()}}
    (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    size = sum(p.stat().st_size for p in args.output.iterdir())
    if manifest['seconds'] > 600 or size > 20e6:
        raise RuntimeError('registered time or retained-size allowance exceeded')
    print(pd.DataFrame(summaries)[['case', 'gravity_Gv2', 'omega', 'adm_mass_rail_units',
        'resolved_higgs_sign_changes', 'radial_material_burden_ratio_maximum']].to_string(index=False))
    print(json.dumps({'seconds': manifest['seconds'], 'retained_bytes': size}))


if __name__ == '__main__':
    main()
