#!/usr/bin/env python3
"""Compare literature's ideal conformal channels with the smooth rail seed.

This is a fixed-geometry, leading two-dimensional source screen. It does
not compute a four-dimensional renormalized fermion or vortex stress.
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
from adm_harness.semiclassical_joint import SmoothJointSeed

ROOT = Path(__file__).resolve().parents[3]
ETA = 2.4127904527582454e-5


def channel_tensor(radius, lapse, log_lapse_prime, log_lapse_second, optical_length):
    """Per unit c, averaged over a sphere; cylinder vacuum plus Weyl anomaly.

    c=1 for a nonchiral complex massless fermion or a real massless scalar.
    Derivatives use proper distance. A unitary cylinder vacuum is assumed;
    holonomy, mass terms, interactions, and transverse core stresses require
    separate calculations. The returned source has no factor of ETA.
    """
    casimir = -np.pi/(6*optical_length**2*lapse**2)
    rho = casimir+(2*log_lapse_second+log_lapse_prime**2)/(24*np.pi)
    pr = casimir-log_lapse_prime**2/(24*np.pi)
    return np.array([rho, pr, np.zeros_like(rho)])/(4*np.pi*radius**2)


def analytic_controls():
    # The flat cylinder and MMP's AdS2 throat are independent exact sources.
    flat = channel_tensor(2., 1., 0., 0., 9.)
    flat_expected = -np.pi/(6*9**2)/(4*np.pi*2**2)
    np.testing.assert_allclose(flat[:2], flat_expected, rtol=1e-14)
    re, ell = 3., 400.
    proper = np.linspace(-3*re, 3*re, 101)
    sech2 = 1/np.cosh(proper/re)**2
    lapse = re/ell*np.cosh(proper/re)
    ap = np.tanh(proper/re)/re
    app = sech2/re**2
    source = channel_tensor(re, lapse, ap, app, np.pi*ell)
    expected_h = -sech2/(16*np.pi**2*re**4)
    expected_trace = -(app+ap**2)/(12*np.pi)/(4*np.pi*re**2)
    h_error = float(np.max(abs((source[0]+source[1])/expected_h-1)))
    trace_error = float(np.max(abs((-source[0]+source[1])/expected_trace-1)))
    # Conservation on a varying-radius geometry, using a complex-step
    # pressure derivative independent of the null-stress identity above.
    def varying_source(l):
        return channel_tensor(2+.2*l*l, np.exp(.12*np.sin(l)+.03*l*l),
                              .12*np.cos(l)+.06*l, -.12*np.sin(l)+.06, 9.)
    point = .3
    rho, pr, pt = varying_source(point)
    terms = np.array([varying_source(point+1e-20j)[1].imag/1e-20,
                      (.12*np.cos(point)+.06*point)*(rho+pr),
                      2*(.4*point)/(2+.2*point**2)*(pr-pt)])
    ward_error = float(abs(terms.sum())/abs(terms).sum())
    if max(h_error, trace_error, ward_error) > 1e-12:
        raise RuntimeError('conformal channel failed an analytic source control')
    return {'flat_cylinder_pass': True, 'mmp_null_relative_error': h_error,
            'trace_anomaly_relative_error': trace_error,
            'varying_radius_ward_relative_error': ward_error}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path,
                        default=ROOT/'supporting_reports/data/longitudinal_literature_screen')
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('--workers must be positive')
    controls = analytic_controls()
    seed = SmoothJointSeed(JoinedProfile(ROOT))
    minimum = minimize_scalar(lambda l: seed.values(l)[0], bounds=(-10., 10.),
                              method='bounded')
    if not minimum.success:
        raise RuntimeError('throat location failed')
    throat = float(minimum.x)
    radius, lapse, _ = seed.values(throat)
    jets = seed.jets(throat)
    required = seed.demanded_tensor(throat)
    critical_length = 2*np.pi/(lapse*np.sqrt(jets[2, 1]))

    def interval_case(edge):
        lo, hi = seed.proper_of_coordinate(np.array([-edge, edge]))
        lengths = []
        for points in (20001, 40001):
            grid = np.linspace(lo, hi, points)
            lengths.append(float(simpson(1/seed.values(grid)[1], x=grid)))
        source = channel_tensor(radius, lapse, jets[1, 1], jets[2, 1], lengths[1])
        return {'coordinate_half_extent': edge,
                'proper_interval': float(hi-lo),
                'minimum_optical_loop_length': lengths[1],
                'optical_quadrature_relative_change': abs(lengths[1]/lengths[0]-1),
                'length_over_sign_threshold': float(lengths[1]/critical_length),
                'throat_rho_plus_pr_per_c': float(source[0]+source[1]),
                'geometric_throat_rho_plus_pr_per_c': float(ETA*(source[0]+source[1]))}

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        rows = list(pool.map(interval_case, (1., 2., 4., 6., 7., 10., 40.)))
    max_change = max(row['optical_quadrature_relative_change'] for row in rows)
    if max_change > 1e-7:
        raise RuntimeError('optical integral needs refinement')
    magnetic = []
    for coupling in (.1, .3, 1.):
        # Continuous interpolation of integer flux, for scale comparison only.
        flux = coupling*radius/np.sqrt(np.pi*ETA)
        ell = 16*radius**3/(ETA*flux)
        magnetic.append({'gauge_coupling': coupling, 'continuous_flux': float(flux),
                         'one_flavor_ell': float(ell),
                         'one_flavor_center_lapse': float(radius/ell),
                         'rail_lapse_over_mmp_lapse': float(lapse*ell/radius)})
    paths = [Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/semiclassical_joint.py',
             ROOT/'toolkit/adm_harness_cli/adm_harness/condensate_vacuum.py',
             ROOT/'supporting_reports/data/condensate_joint/r12_q0.85_potential_x2_solution.npz']
    summary = {
        'scope': 'Ideal static conformal channels on the fixed smooth seed; no joint solution',
        'loop_assumption': 'The channel spans the listed interval; exterior optical return length is set to zero for the most negative cylinder term',
        'eta': ETA, 'workers': args.workers,
        'throat_proper': throat, 'throat_coordinate': float(seed.coordinate_of_proper(throat)),
        'throat_radius': float(radius), 'throat_lapse': float(lapse),
        'radius_over_planck_length': float(radius/np.sqrt(ETA)),
        'required_tensor': required.tolist(),
        'throat_log_lapse_second': float(jets[2, 1]),
        'critical_optical_loop_length': float(critical_length),
        'checks': controls, 'optical_quadrature_max_relative_change': max_change,
        'magnetic_same_radius_comparisons': magnetic,
        'source_hashes': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in paths},
    }
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output/'loop_screen.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    (args.output/'screen.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
