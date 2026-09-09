#!/usr/bin/env python3
"""Count separate backbone, saved material, ideal quantum target, and host.

This reconstructs a target allocation, not a quantum or material field solve.
Independent backbone fractions run in parallel. Narrative findings are manual.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import csv
import hashlib
import json

import numpy as np
from scipy.integrate import simpson
from scipy.interpolate import PPoly
from scipy.optimize import minimize_scalar

from adm_harness.condensate_vacuum import JoinedProfile
from adm_harness.screened_condensate import field_stress
from adm_harness.semiclassical_joint import SmoothJointSeed
from adm_harness.vacuum_support import casimir_channels, minimum_dec_weights

ROOT = Path(__file__).resolve().parents[3]
CHANNELS = ('rho', 'pr', 'pt')


def flux_window(coordinate):
    """C2 plateau through |x|=1, terminating at |x|=3; return d/dx too."""
    x = np.asarray(coordinate)
    t = np.clip((abs(x)-1)/2, 0., 1.)
    value = 1-10*t**3+15*t**4-6*t**5
    derivative = -15*t*t*(1-t)**2*np.sign(x)
    return value, derivative


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--points', type=int, default=80001)
    parser.add_argument('--output', type=Path,
                        default=ROOT/'supporting_reports/data/coupled_reorientation/allocation')
    args = parser.parse_args()
    if args.workers < 1 or args.points < 1001 or args.points % 2 != 1:
        parser.error('positive workers and an odd point count >= 1001 required')
    material_path = ROOT/'supporting_reports/data/semiclassical_joint/material_update/material.npz'
    expected = json.loads(material_path.with_name('checks.json').read_text())['output_hashes']['material.npz']
    if hashlib.sha256(material_path.read_bytes()).hexdigest() != expected:
        raise RuntimeError('saved material hash mismatch')
    profile = JoinedProfile(ROOT)
    with np.load(material_path) as data:
        seed = SmoothJointSeed(profile, float(data['width']), float(data['seed_spacing']))
        material = PPoly.construct_fast(data['coefficients'].copy(), data['knots'].copy(), axis=1)
        omega = float(data['frequency'])
    minimum = minimize_scalar(lambda l: seed.values(l)[0], bounds=(-1., 1.), method='bounded')
    if not minimum.success:
        raise RuntimeError('throat location failed')
    throat = float(minimum.x)
    witness_x = np.array([-7., -4., -3., -2.5, -2., -1., .5, 1., 2., 2.5, 3., 4., 7.])
    witness_l = np.r_[throat, seed.proper_of_coordinate(witness_x)]

    def evaluate(proper, fraction):
        x = seed.coordinate_of_proper(proper)
        radius, lapse, _ = seed.values(proper)
        demanded = seed.demanded_tensor(proper).T
        fields = field_stress(material(proper)[:6], omega, profile.material, 1., lapse)
        matter = profile.eta*profile.v**4*np.array([fields[name] for name in
                 ('energy', 'radial_pressure', 'tangential_pressure')]).T
        window, derivative = flux_window(x)
        # pr(throat)=-1/(8 pi R0^2): this flux carries the declared share.
        flux = fraction/(8*np.pi)*window
        density = flux/radius**2
        backbone = np.stack([density, -density, 0*density], axis=-1)
        force = -fraction/(8*np.pi)*derivative*seed.coordinate_of_proper(proper, 1)/radius**2
        target = demanded-matter-backbone
        weights = minimum_dec_weights(target)
        null_weights = np.maximum(-np.stack([target[:, 0]+target[:, 1],
                                            target[:, 0]+target[:, 2]], axis=-1)/4, 0.)
        quantum = casimir_channels(weights[:, 0], weights[:, 1])
        host = target-quantum
        error = np.max(abs(backbone+matter+quantum+host-demanded))
        margin = np.min(host[:, 0, None]-abs(host[:, 1:]))
        if error > 1e-13 or margin < -1e-13:
            raise RuntimeError('source allocation failed tensor or DEC check')
        return dict(x=x, radius=radius, lapse=lapse, demanded=demanded, matter=matter,
                    backbone=backbone, quantum=quantum, host=host, weights=weights,
                    null_weights=null_weights, force=force, error=float(error), margin=float(margin))

    def fraction_case(fraction):
        integrals = []
        for points in (args.points, 2*args.points-1):
            proper = np.linspace(*seed.proper_of_coordinate(np.array([-40., 40.])), points)
            d = evaluate(proper, fraction)
            volume = 4*np.pi*d['radius']**2
            integrals.append(np.array([simpson(volume*d[name][:, 0], x=proper)
                                      for name in ('demanded', 'backbone', 'matter', 'quantum', 'host')]))
        witnesses = evaluate(witness_l, fraction)
        rows = []
        for i, witness_proper in enumerate(witness_l):
            row = dict(backbone_fraction=fraction, label='throat' if i == 0 else 'coordinate',
                       coordinate=float(witnesses['x'][i]), proper=float(witness_proper),
                       radius=float(witnesses['radius'][i]))
            for name in ('demanded', 'backbone', 'matter', 'quantum', 'host'):
                for k, channel in enumerate(CHANNELS):
                    row[name+'_'+channel] = float(witnesses[name][i, k])
            for k, name in enumerate(('radial', 'angular')):
                weight = float(witnesses['weights'][i, k])
                row[name+'_weight'] = weight
                row[name+'_null_only_lower_bound'] = float(witnesses['null_weights'][i, k])
                row[name+'_ideal_em_gap'] = float((profile.eta*np.pi**2/(720*weight))**.25) if weight > 0 else None
            row['backbone_radial_divergence'] = float(witnesses['force'][i])
            rows.append(row)
        demand = witnesses['demanded'][0]
        # Independent locally flat held cells cost at least 3 S in holders.
        # Even assigning ALL ordinary energy to those holders leaves this gap.
        s = d['weights'][:, 0]+2*d['weights'][:, 1]
        null_s = d['null_weights'][:, 0]+2*d['null_weights'][:, 1]
        holder_deficit = np.maximum(2*s-d['demanded'][:, 0], 0.)
        half_force_errors = []
        for edges, expected_force in (((-40., 0.), -fraction/2), ((0., 40.), fraction/2)):
            half_l = np.linspace(*seed.proper_of_coordinate(np.array(edges)), args.points)
            half = evaluate(half_l, fraction)
            area_force = simpson(4*np.pi*half['radius']**2*half['force'], x=half_l)
            half_force_errors.append(abs(area_force-expected_force))
        force_error = float(max(half_force_errors))
        if force_error > 1e-8:
            raise RuntimeError(f'backbone termination force needs refinement: {force_error}')
        summary = dict(backbone_fraction=fraction,
            throat_backbone_tension_share=float(witnesses['backbone'][0, 1]/demand[1]),
            throat_material_tension_share=float(witnesses['matter'][0, 1]/demand[1]),
            throat_quantum_radial_weight=float(witnesses['weights'][0, 0]),
            throat_quantum_angular_weight=float(witnesses['weights'][0, 1]),
            tensor_max_absolute_error=d['error'], host_min_dec_margin=d['margin'],
            maximum_backbone_force=float(np.max(abs(d['force']))),
            backbone_area_weighted_force_max_absolute_error=force_error,
            null_only_quantum_proper_energy_lower_magnitude=float(simpson(volume*null_s, x=proper)),
            maximum_independent_cell_holder_deficit=float(np.max(holder_deficit)),
            proper_energy_quadrature_max_absolute_change=float(np.max(abs(integrals[1]-integrals[0]))),
            proper_energy=dict(zip(('demanded','backbone','matter','quantum','host'), map(float,integrals[1]))))
        return summary, rows

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        cases = list(pool.map(fraction_case, (0., .5, .95)))
    paths = [Path(__file__), material_path,
             ROOT/'toolkit/adm_harness_cli/adm_harness/vacuum_support.py',
             ROOT/'toolkit/adm_harness_cli/adm_harness/semiclassical_joint.py',
             ROOT/'toolkit/adm_harness_cli/adm_harness/screened_condensate.py',
             ROOT/'toolkit/adm_harness_cli/adm_harness/condensate_vacuum.py',
             ROOT/'supporting_reports/data/condensate_joint/r12_q0.85_potential_x2_solution.npz']
    summary = dict(scope='Restored static target allocation; ideal tensor weights are unsupplied quantum targets and the host is fitted',
                   eta=profile.eta, v=profile.v, omega=omega, workers=args.workers,
                   fine_points=2*args.points-1, coordinate_extent=40.,
                   cases=[case[0] for case in cases],
                   source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    if max(case['proper_energy_quadrature_max_absolute_change'] for case in summary['cases']) > 5e-5:
        raise RuntimeError('allocation integrals need refinement')
    args.output.mkdir(parents=True, exist_ok=True)
    rows = [row for _, entries in cases for row in entries]
    with (args.output/'witnesses.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    (args.output/'allocation.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({key:value for key,value in summary.items() if key != 'source_hashes'}, indent=2))


if __name__ == '__main__':
    main()
