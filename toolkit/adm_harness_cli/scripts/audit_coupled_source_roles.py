#!/usr/bin/env python3
"""Audit source allocation and geometric stress roles on the saved smooth rail.

Reuses the existing metric and relaxed material. Independent spatial bands
run in parallel. Outputs are numerical evidence; the report is written by hand.
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
from adm_harness.semiclassical_joint import SmoothJointSeed, curvature

ROOT = Path(__file__).resolve().parents[3]
CHANNELS = ('rho', 'pr', 'pt')
BANDS = ((-40., -3.), (-3., -2.), (-2., -1.), (-1., 1.),
         (1., 2.), (2., 3.), (3., 40.))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analytic_controls():
    """Flat space, a cylinder, an Ellis throat, and a de Sitter static patch."""
    l = np.linspace(.4, 2., 101)
    zero = np.zeros_like(l)
    flat = curvature([np.log(l), 1/l, -1/l**2], [zero]*3)[1]
    np.testing.assert_allclose(flat, 0., atol=5e-15)
    cylinder = curvature([np.log(l*0+2), zero, zero], [zero]*3)[1]
    np.testing.assert_allclose(cylinder, np.array([.25, -.25, 0.])[:, None]
                               * np.ones_like(l), atol=5e-15)
    b = 1.75
    square = l*l+b*b
    ellis = curvature([.5*np.log(square), l/square,
                       (b*b-l*l)/square**2], [zero]*3)[1]
    np.testing.assert_allclose(ellis, np.array([-1., -1., 1.])[:, None]
                               * b*b/square**2, rtol=1e-13, atol=1e-15)
    h = .1
    desitter = curvature([np.log(np.sin(h*l)/h), h/np.tan(h*l),
                          -h*h/np.sin(h*l)**2],
                         [np.log(np.cos(h*l)), -h*np.tan(h*l),
                          -h*h/np.cos(h*l)**2])[1]
    np.testing.assert_allclose(desitter, np.array([1., -1., -1.])[:, None]
                               * 3*h*h*np.ones_like(l), rtol=1e-12, atol=1e-14)
    return {'flat_space': True, 'constant_radius_cylinder': True,
            'ellis_throat': True, 'de_sitter_static_patch': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--points', type=int, default=30001,
                        help='coarse proper-distance points per band; fine uses 2N-1')
    parser.add_argument('--output', type=Path,
                        default=ROOT/'supporting_reports/data/coupled_source_roles')
    args = parser.parse_args()
    if args.workers < 1 or args.points < 1001 or args.points % 2 != 1:
        parser.error('use positive workers and an odd point count of at least 1001')
    checks = analytic_controls()
    material_path = ROOT/'supporting_reports/data/semiclassical_joint/material_update/material.npz'
    material_checks = json.loads(material_path.with_name('checks.json').read_text())
    if digest(material_path) != material_checks['output_hashes']['material.npz']:
        raise RuntimeError('saved material hash mismatch')
    profile = JoinedProfile(ROOT)
    with np.load(material_path) as data:
        seed = SmoothJointSeed(profile, float(data['width']), float(data['seed_spacing']))
        material = PPoly.construct_fast(data['coefficients'].copy(),
                                       data['knots'].copy(), axis=1)
        omega = float(data['frequency'])

    def band_case(bounds):
        ends = seed.proper_of_coordinate(np.array(bounds))
        integrals = []
        for points in (args.points, 2*args.points-1):
            l = np.linspace(*ends, points)
            jets = seed.jets(l, 2)
            r, a = np.exp(jets[0, :2])
            sections, einstein, _, _ = curvature(jets[:, 0], jets[:, 1])
            x, y, z, w = sections
            rho, pr, pt = einstein/(8*np.pi)
            integrals.append(np.array([
                simpson(4*np.pi*r/a*np.maximum(-rho-pr, 0.), x=l),
                simpson(-4*np.pi*r/a*(rho+pr), x=l),
                simpson(r/a*z, x=l), simpson(-r/a*y, x=l)]))
        endpoint = float(np.diff(r[[0, -1]]*jets[1, 0, [0, -1]]/a[[0, -1]])[0])
        # Differentiate the radial pressure and check the Bianchi identity.
        rp, ap = jets[1, :2]
        rpp, app = jets[2, :2]
        wp = -2*np.exp(-2*jets[0, 0])*rp-2*rp*rpp
        yp = app*rp+ap*rpp
        terms = np.array([(-wp+2*yp)/(8*np.pi), ap*(rho+pr),
                          2*rp*(pr-pt)])
        ward = float(np.max(abs(terms.sum(axis=0)))/max(np.max(abs(terms).sum(axis=0)), 1e-30))
        lapse_error = float(np.max(abs(x+2*y-4*np.pi*(rho+pr+2*pt))))
        fine = integrals[-1]
        return {'coordinate_lo': bounds[0], 'coordinate_hi': bounds[1],
                'negative_null_balance': float(fine[0]),
                'signed_opening_balance': float(fine[1]),
                'radius_curvature_balance': float(fine[2]),
                'clock_gradient_balance': float(fine[3]),
                'endpoint_opening': endpoint,
                'negative_quadrature_relative_change': float(abs(fine[0]/integrals[0][0]-1)),
                'signed_quadrature_absolute_change': float(abs(fine[1]-integrals[0][1])),
                'endpoint_absolute_error': float(abs(fine[1]-endpoint)),
                'conservation_scaled_error': ward, 'lapse_equation_absolute_error': lapse_error}

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        bands = list(pool.map(band_case, BANDS))
    checks.update({key: max(row[key] for row in bands) for key in (
        'negative_quadrature_relative_change', 'signed_quadrature_absolute_change',
        'endpoint_absolute_error', 'conservation_scaled_error', 'lapse_equation_absolute_error')})
    if (checks['negative_quadrature_relative_change'] > 1e-5
            or checks['endpoint_absolute_error'] > 1e-7
            or checks['conservation_scaled_error'] > 1e-12
            or checks['lapse_equation_absolute_error'] > 1e-12):
        raise RuntimeError('geometry audit requires further numerical refinement')

    throat_result = minimize_scalar(lambda l: seed.values(l)[0], bounds=(-1., 1.), method='bounded')
    if not throat_result.success:
        raise RuntimeError('throat location failed')
    throat = float(throat_result.x)
    coordinates = np.array([-8., -6., -4., -3., -2., -1., 0., .5, 1., 1.5, 2., 3., 4., 8., 40.])
    locations = [('throat', throat)] + [('coordinate', float(l)) for l in seed.proper_of_coordinate(coordinates)]
    witnesses = []
    for label, l in locations:
        jets = seed.jets(l, 2)
        sections, einstein, _, _ = curvature(jets[:, 0], jets[:, 1])
        required = einstein/(8*np.pi)
        rho, pr, pt = required
        radius, lapse = np.exp(jets[0, :2])
        stress = field_stress(material(l)[:6], omega, profile.material, 1., lapse)
        counted = profile.eta*profile.v**4*np.array([stress[k] for k in
                                                   ('energy', 'radial_pressure', 'tangential_pressure')])
        # Restricted local basis: radial Maxwell, positive potential, and a
        # traceless longitudinal term. No field equation follows from this fit.
        electric, potential, longitudinal = (rho-pr+2*pt)/4, (rho-pr-2*pt)/4, (rho+pr)/2
        reconstructed = np.array([electric+potential+longitudinal,
                                  -electric-potential+longitudinal, electric-potential])
        np.testing.assert_allclose(reconstructed, required, rtol=1e-12, atol=1e-16)
        row = {'label': label, 'coordinate': float(seed.coordinate_of_proper(l)),
               'proper': l, 'radius': float(radius), 'lapse': float(lapse)}
        row.update(dict(zip(('X', 'Y', 'Z', 'W'), map(float, sections))))
        for prefix, source in [('required', required), ('material', counted),
                               ('assigned_quantum_remainder', required-counted)]:
            row.update({prefix+'_'+channel: float(value) for channel, value in zip(CHANNELS, source)})
        row.update({'radial_null': float(rho+pr), 'angular_null': float(rho+pt),
                    'active_lapse_source': float(rho+pr+2*pt),
                    'formal_electric': float(electric), 'formal_potential': float(potential),
                    'formal_longitudinal': float(longitudinal)})
        witnesses.append(row)

    negative = sum(row['negative_null_balance'] for row in bands)
    outside_two = sum(row['negative_null_balance'] for row in bands
                      if row['coordinate_hi'] <= -2 or row['coordinate_lo'] >= 2)
    two_to_three = sum(row['negative_null_balance'] for row in bands
                       if (row['coordinate_lo'], row['coordinate_hi']) in ((-3., -2.), (2., 3.)))
    central = witnesses[0]
    paths = [Path(__file__), material_path, material_path.with_name('checks.json'), profile.path,
             ROOT/'supporting_reports/data/curved_quantum_boundary/geometry.npz',
             ROOT/'supporting_reports/data/curved_quantum_boundary/geometry.json']
    paths += [ROOT/'toolkit/adm_harness_cli/adm_harness'/name for name in (
        'semiclassical_joint.py', 'condensate_vacuum.py', 'condensate_rail.py',
        'condensate_joint.py', 'curved_boundary.py', 'screened_condensate.py')]
    summary = {'scope': 'Saved static smooth geometry and relaxed material; no new field solve',
               'source_units': 'Geometric G*T; assigned remainder is a requirement, not supplied quantum stress',
               'coordinate_bands': 'Integration bins in the existing coordinate, not material interfaces',
               'workers': args.workers, 'coarse_points_per_band': args.points,
               'fine_points_per_band': 2*args.points-1,
               'eta': float(profile.eta), 'material_scale': float(profile.v), 'frequency': omega,
               'signed_opening_balance': sum(row['signed_opening_balance'] for row in bands),
               'negative_null_balance': negative,
               'negative_balance_fraction_outside_abs_coordinate_2': outside_two/negative,
               'negative_balance_fraction_abs_coordinate_2_to_3': two_to_three/negative,
               'throat_material_density_fraction': central['material_rho']/central['required_rho'],
               'throat_material_radial_tension_fraction': central['material_pr']/central['required_pr'],
               'checks': checks,
               'source_hashes': {str(p.relative_to(ROOT)): digest(p) for p in paths}}
    args.output.mkdir(parents=True, exist_ok=True)
    for name, rows in [('bands.csv', bands), ('witnesses.csv', witnesses)]:
        with (args.output/name).open('w') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
    (args.output/'audit.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'source_hashes'}, indent=2))


if __name__ == '__main__':
    main()
