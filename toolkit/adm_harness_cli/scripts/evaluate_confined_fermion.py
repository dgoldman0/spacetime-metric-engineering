#!/usr/bin/env python3
"""Bounded occupied-state audit; writes numerical evidence only."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import resource
import time

import numpy as np
from scipy.integrate import simpson

from adm_harness.confined_fermion import (
    DiracMesh, MassWell, RailWell, angular_tail_bound, occupied_tensor, opening)

ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT/'supporting_reports/data/archived_geometry_opening/reference_metric.npz'
ETA = 2.4127904527582454e-5


def checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_problem(spec):
    well = MassWell(width=spec['width'])
    background = RailWell(CACHE, well, tail_extent=spec['extent'])
    low, high = background.z_bounds
    z = np.linspace(low, high, int(np.ceil((high-low)/spec['spacing']))+1)
    fields = background.optical_fields(z, spec['yukawa'])
    faces = background.optical_fields((z[1:]+z[:-1])/2, spec['yukawa'])
    return well, background, z, fields, faces


def solve_sector(task):
    spec, angular, deadline = task
    if time.monotonic() > deadline:
        raise TimeoutError('registered time allowance expired')
    started = time.monotonic()
    well, background, z, fields, faces = make_problem(spec)
    cutoff = spec['cutoff_fraction']*spec['yukawa']*well.vacuum_scale
    mesh = DiracMesh(z, fields['M'], faces['M'], angular*faces['w'])
    modes = mesh.roots(cutoff)
    records, profiles = [], []
    probes = np.linspace(-8, 8, 257)
    for index, mode in enumerate(modes):
        if time.monotonic() > deadline:
            raise TimeoutError('registered time allowance expired')
        tensor, scalar = occupied_tensor(fields, mode, angular, ETA)
        rho, pr, pt = tensor
        h = rho+pr
        terms = np.array([np.gradient(pr, z, edge_order=2)/fields['lapse'],
            fields['log_lapse_prime']*h,
            2*fields['radius_prime']/fields['radius']*(pr-pt),
            fields['mass_prime']*scalar])
        weight = fields['lapse']*fields['radius']**2
        # Omit the artificial end boundary; its amplitude is recorded below.
        interior = (z > z[0]+1.) & (z < z[-1]-1.)
        ward_numerator = simpson(weight[interior]*abs(terms[:, interior].sum(axis=0)), x=z[interior])
        ward_denominator = simpson(weight[interior]*np.sum(abs(terms[:, interior]), axis=0), x=z[interior])
        norm_density = mode['f']**2+mode['g']**2
        edge = (z < z[0]+1.) | (z > z[-1]-1.)
        boundary_peak = float(norm_density[edge].max()/norm_density.max())
        b = opening(z, fields['radius'], tensor)
        helpful = float(4*np.pi*simpson(fields['radius']*np.maximum(-h, 0), x=z))
        energy = float(4*np.pi*simpson(fields['lapse']**2*fields['radius']**2*rho, x=z))
        expected_energy = ETA*2*abs(angular)*mode['frequency']
        record = dict(angular=angular, radial_index=index, frequency=mode['frequency'],
            opening=b, helpful_opening=helpful,
            opposing_opening=helpful-b, minimum_radial_null=float(h.min()),
            minimum_density=float(rho.min()), boundary_peak_fraction=boundary_peak,
            ward_relative_l1=float(ward_numerator/max(ward_denominator, 1e-30)),
            energy_relative_error=abs(energy/expected_energy-1),
            schur_residual=mode['schur_residual'])
        records.append(record)
        profiles.append(np.array([np.interp(probes, fields['coordinate'], channel)
                                  for channel in np.vstack((tensor, scalar))]))
    return dict(spec=spec['label'], angular=angular, points=len(z), records=records,
                profiles=profiles, elapsed_seconds=time.monotonic()-started,
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--yukawa', type=float, nargs='+', default=[1., 2., 4.])
    parser.add_argument('--spacing', type=float, default=1/128)
    parser.add_argument('--width', type=float, default=1.)
    parser.add_argument('--extent', type=float, default=64.)
    parser.add_argument('--cutoff-fraction', type=float, default=.9)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--seconds', type=float, default=900.)
    args = parser.parse_args()
    if (not 1 <= args.workers <= 6 or args.spacing <= 0 or args.width <= 0
            or args.seconds <= 0 or not 0 < args.cutoff_fraction < 1
            or min(args.yukawa) <= 0):
        raise ValueError('positive parameters, subthreshold cutoff, and 1--6 workers required')
    if args.output.exists() and any(args.output.iterdir()):
        raise FileExistsError('use an empty output directory for a new evidence run')
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    deadline = started+args.seconds
    summaries, tasks = {}, []
    for yukawa in args.yukawa:
        label = f'y{yukawa:g}_d{args.width:g}'
        spec = dict(label=label, yukawa=yukawa, spacing=args.spacing, width=args.width,
                    extent=args.extent, cutoff_fraction=args.cutoff_fraction)
        well, background, z, fields, faces = make_problem(spec)
        cutoff = args.cutoff_fraction*yukawa*well.vacuum_scale
        bound, derivative, quadratic = angular_tail_bound(fields, cutoff)
        # A margin above the sampled sufficient bound; an independent finer
        # run checks the continuum envelope before this is an angular cutoff.
        angular_limit = max(2, int(np.ceil(1.05*bound.max()))+1)
        scalar_tensor = ETA*np.array([.5*fields['chi_prime']**2+fields['potential'],
            .5*fields['chi_prime']**2-fields['potential'],
            -.5*fields['chi_prime']**2-fields['potential']])
        r, a, rp, rpp, ap = [fields[k] for k in
                             ('radius', 'lapse', 'radius_prime', 'radius_second', 'log_lapse_prime')]
        h_geom = (ap*rp-rpp)/(4*np.pi*r)
        required = float(rp[-1]/a[-1]-rp[0]/a[0])
        integrated = float(-4*np.pi*simpson(r*h_geom, x=z))
        margin = fields['M']-cutoff+angular_limit**2*quadratic-angular_limit*abs(derivative)
        summaries[label] = dict(spec=spec, points=len(z), angular_limit=angular_limit,
            sampled_angular_bound=float(bound.max()), angular_tail_potential_minimum=float(margin.min()),
            scalar_quartic=well.quartic, scalar_opening=opening(z, r, scalar_tensor),
            geometric_opening=required, geometric_integral=integrated,
            geometric_identity_relative_error=abs(integrated/required-1),
            wall_coordinates=background.wall_coordinates, wall_proper=background.wall_proper.tolist(),
            modes=[], worker_seconds=0., max_rss_kib=0)
        tasks += [(spec, sign*k, deadline) for k in range(1, angular_limit+1) for sign in (-1, 1)]
        np.savez_compressed(args.output/f'{label}_background.npz',
            coordinate=fields['coordinate'], z=z, radius=r, lapse=a, chi=fields['chi'],
            scalar_tensor=scalar_tensor, geometric_radial_null=h_geom,
            scalar_equation_residual=fields['chi_second']+(ap+2*rp/r)*fields['chi_prime']-fields['potential_prime'])
        print(json.dumps(dict(case=label, sectors=2*angular_limit, points=len(z),
                              scalar_opening=summaries[label]['scalar_opening'])), flush=True)
    profile_records = {key: [] for key in summaries}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        pending = [pool.submit(solve_sector, task) for task in tasks]
        for future in as_completed(pending):
            result = future.result()
            row = summaries[result['spec']]
            row['modes'] += result['records']
            profile_records[result['spec']] += result['profiles']
            row['worker_seconds'] += result['elapsed_seconds']
            row['max_rss_kib'] = max(row['max_rss_kib'], result['max_rss_kib'])
            if result['records']:
                print(json.dumps(dict(case=result['spec'], angular=result['angular'],
                    states=len(result['records']),
                    best_opening=max(m['opening'] for m in result['records']))), flush=True)
    for label, row in summaries.items():
        modes = row['modes']
        row['states'] = len(modes)
        row['filled_opening'] = sum(m['opening'] for m in modes)
        row['best_arbitrary_occupation_opening'] = sum(max(m['opening'], 0) for m in modes)
        row['helpful_only_opening'] = sum(m['helpful_opening'] for m in modes)
        row['positive_opening_states'] = sum(m['opening'] > 0 for m in modes)
        for key in ('ward_relative_l1', 'boundary_peak_fraction', 'energy_relative_error', 'schur_residual'):
            row['maximum_'+key] = max((m[key] for m in modes), default=0.)
        np.savez_compressed(args.output/f'{label}_occupied_profiles.npz',
            coordinate=np.linspace(-8, 8, 257), tensor_and_scalar=np.array(profile_records[label]))
    sources = [Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/confined_fermion.py',
               ROOT/'toolkit/adm_harness_cli/adm_harness/geometry_opening.py', CACHE]
    report = dict(model='neutral Dirac Yukawa mass well; occupied-state increment only',
        eta=ETA, workers=args.workers, elapsed_seconds=time.monotonic()-started,
        source_hashes={str(p.relative_to(ROOT)): checksum(p) for p in sources},
        cases=summaries)
    (args.output/'summary.json').write_text(json.dumps(report, indent=2)+'\n')
    size = sum(p.stat().st_size for p in args.output.iterdir() if p.is_file())
    if size > 20_000_000:
        raise RuntimeError('registered retained-output allowance exceeded')
    print(json.dumps(dict(elapsed_seconds=report['elapsed_seconds'], output_bytes=size,
        results={key: {k: row[k] for k in ('states', 'positive_opening_states',
            'filled_opening', 'best_arbitrary_occupation_opening', 'helpful_only_opening',
            'scalar_opening', 'maximum_ward_relative_l1', 'maximum_boundary_peak_fraction')}
            for key, row in summaries.items()})), flush=True)


if __name__ == '__main__':
    main()
