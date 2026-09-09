#!/usr/bin/env python3
"""Bound longitudinal quantum support after allowing independent ordinary roles.

The radius profile is retained. Clock changes have fixed endpoint values and
slopes, while their interior shape is free within the declared pointwise box.
Independent channel strengths and spatial extents run in parallel.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import csv
import hashlib
import json

import numpy as np
from scipy.integrate import simpson
from scipy.optimize import minimize_scalar

from adm_harness.condensate_vacuum import JoinedProfile
from adm_harness.longitudinal_balance import weighted_balance, lapse_box_from_integrals
from adm_harness.semiclassical_joint import SmoothJointSeed

ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--points', type=int, default=80001)
    parser.add_argument('--output', type=Path,
                        default=ROOT/'supporting_reports/data/coupled_reorientation/longitudinal_gate')
    args = parser.parse_args()
    if args.workers < 1 or args.points < 10001 or args.points % 2 != 1:
        parser.error('positive workers and odd points >= 10001 required')
    profile = JoinedProfile(ROOT)
    seed = SmoothJointSeed(profile)
    minimum = minimize_scalar(lambda l: seed.values(l)[0], bounds=(-1., 1.), method='bounded')
    if not minimum.success:
        raise RuntimeError('throat location failed')
    r0 = float(seed.values(minimum.x)[0])
    cached = {}
    for extent in (7., 40.):
        for points in (args.points, 2*args.points-1):
            l = np.linspace(*seed.proper_of_coordinate(np.array([-extent, extent])), points)
            y = seed.jets(l, 2)
            r, a = np.exp(y[0, :2])
            cached[extent, points] = (l, r, a, r*y[1, 0], r*(y[2, 0]+y[1, 0]**2),
                                     y[1, 1], y[2, 1], abs(seed.coordinate_of_proper(l)) <= 7.)
    ratios = (profile.eta/(12*np.pi*r0*r0), 1e-6, 1e-5, 1e-4, .001, .01, .03, .1, .3, .6, .9)

    def case(parameters):
        extent, ratio = parameters
        k = ratio*r0*r0
        rows, balances, upper_bounds = [], [], []
        for points in (args.points, 2*args.points-1):
            l, r, a, rp, rpp, ap, app, mask = cached[extent, points]
            result = weighted_balance(l, r, a, rp, rpp, ap, k, r0)
            balances.append(result)
            inner_data = cached[7., points]
            inner = weighted_balance(*inner_data[:6], k, r0)
            upper_bounds.append([lapse_box_from_integrals(result['numerator'], result['optical_length'],
                inner['numerator'], inner['optical_length'], fraction) for fraction in (0., .1, .5, .9)])
        h_geometry = (ap*rp-rpp)/(4*np.pi*r)
        h_quantum = k/(4*np.pi*r*r)*(app-4*np.pi**2/(result['optical_length']**2*a*a))
        direct = 4*np.pi/k*simpson(result['weight']*r*r*(h_geometry-h_quantum), x=l)
        identity = abs(direct-result['residual'])/max(abs(result['required']),abs(result['supply']),1e-30)
        refinement = max(abs(result[key]-balances[0][key])/max(abs(result[key]),1e-30)
                         for key in ('required','supply','optical_length'))
        refinement = max(refinement, float(np.max(abs(np.array(upper_bounds[1])/upper_bounds[0]-1))))
        if identity > 2e-5 or refinement > 2e-5:
            raise RuntimeError(f'weighted gate needs refinement: {parameters}, {identity}, {refinement}')
        for fraction, upper in zip((0., .1, .5, .9), upper_bounds[1]):
            rows.append(dict(coordinate_half_extent=extent, kappa_over_r0_squared=ratio,
                central_charge=k*12*np.pi/profile.eta, lapse_fractional_change=fraction,
                minimum_optical_length=result['optical_length'], required=result['required'],
                endpoint_term=result['endpoint_demand'], original_supply=result['supply'],
                optimistic_supply_upper_bound=upper, upper_bound_over_required=upper/result['required'],
                necessary_gate_excludes=bool(upper < result['required']*(1-1e-4)),
                identity_scaled_error=identity, quadrature_relative_change=refinement))
        return rows

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        groups = list(pool.map(case, [(extent, ratio) for extent in (7.,40.) for ratio in ratios]))
    rows = [row for group in groups for row in group]
    paths = [Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/longitudinal_balance.py',
             ROOT/'toolkit/adm_harness_cli/adm_harness/semiclassical_joint.py',
             ROOT/'toolkit/adm_harness_cli/adm_harness/condensate_vacuum.py',
             ROOT/'supporting_reports/data/condensate_joint/r12_q0.85_potential_x2_solution.npz']
    summary = dict(scope='Necessary gate for a constant-c radial CFT channel plus an aggregate with nonnegative radial null stress; no full field solve',
        radius_profile='Retained smooth seed', clock_variable_region='|x| <= 7, fixed endpoint jets',
        clock_boxes='Exploratory pointwise ranges; service admissibility is untested',
        optical_return='Zero for the most favorable lower bound on the full loop length',
        eta=profile.eta, throat_radius=r0, workers=args.workers, fine_points=2*args.points-1,
        cases=len(rows), excluded_cases=sum(row['necessary_gate_excludes'] for row in rows),
        checks=dict(identity_scaled_error=max(row['identity_scaled_error'] for row in rows),
                    quadrature_relative_change=max(row['quadrature_relative_change'] for row in rows)),
        source_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output/'gate.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    (args.output/'gate.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({key:value for key,value in summary.items() if key!='source_hashes'}, indent=2))


if __name__ == '__main__':
    main()
