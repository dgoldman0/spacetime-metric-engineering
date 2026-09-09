#!/usr/bin/env python3
"""Numeric regulator, angular-tail, and Ward-identity audit tables."""
from pathlib import Path
import argparse
import json

import numpy as np
import pandas as pd
from scipy.special import zeta

from adm_harness.source_ledger import sha256_file


def tail_candidates(moments, first=None):
    """Measured tail extrapolations; direct extended sums validate their use.

    The flat-reference subtraction removes the leading homogeneous tail.
    Inverse fifth and higher odd powers describe the remaining large-order
    expansion while the frequency cutoff lies above the fitted mode range.
    """
    last = len(moments)-1
    starts = sorted(set([max(16, last//2), max(16, 2*last//3), max(16, 3*last//4)]))
    if first is not None:
        starts = [first]
    rows = []
    for start in starts:
        if last-start < 12:
            continue
        nu = np.arange(start, last+1)+.5
        for terms in (3, 4, 5):
            powers = np.arange(5, 5+2*terms, 2)
            matrix = (last/nu[:, None])**powers
            coefficients = np.linalg.lstsq(matrix, moments[start:], rcond=None)[0]
            tail = (float(last)**powers*zeta(powers, last+1.5))@coefficients
            residual = np.max(abs(matrix@coefficients-moments[start:]), axis=0)
            rows.append((start, terms, tail, residual))
    return rows


def read_run(directory):
    directory = Path(directory)
    manifest = json.loads((directory/'manifest.json').read_text())
    for name, value in manifest['output_hashes'].items():
        if sha256_file(directory/name) != value:
            raise ValueError('changed result: '+str(directory/name))
    moments = np.load(directory/'angular_sums.npz')['moments']
    estimates = pd.read_csv(directory/'estimates.csv')
    rows, tails = [], []
    names = ['rho', 'pr', 'pt', 'polarization']
    for i, scale in enumerate(manifest['regulators']):
        candidates = tail_candidates(moments[:, i])
        center = np.median([x[2] for x in candidates], axis=0)
        spread = np.ptp([x[2] for x in candidates], axis=0)
        corrected = estimates.loc[i, ['estimate_'+n for n in names]].to_numpy(float)+center
        rows.append({'run': directory.name, 'regulator': scale,
            **{n: corrected[k] for k, n in enumerate(names)},
            **{'tail_'+n: center[k] for k, n in enumerate(names)},
            **{'tail_spread_'+n: spread[k] for k, n in enumerate(names)},
            'radial_enthalpy': corrected[0]+corrected[1]})
        for start, terms, tail, residual in candidates:
            tails.append({'run': directory.name, 'regulator': scale, 'first_harmonic': start,
                'terms': terms, **{'tail_'+n: tail[k] for k, n in enumerate(names)},
                **{'fit_residual_'+n: residual[k] for k, n in enumerate(names)}})
    return manifest, pd.DataFrame(rows), tails


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', nargs='+', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--ward', nargs=3, metavar=('LEFT', 'CENTER', 'RIGHT'))
    args = parser.parse_args()
    summaries, tails, manifests = [], [], {}
    for run in args.runs:
        manifest, rows, fits = read_run(run)
        summaries.append(rows); tails.extend(fits)
        manifests[run.name] = manifest
    summary = pd.concat(summaries, ignore_index=True)
    args.output.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output/'source_estimates.csv', index=False)
    pd.DataFrame(tails).to_csv(args.output/'tail_fits.csv', index=False)
    ward = []
    if args.ward:
        left, center, right = args.ward
        data = [summary[summary.run == name].set_index('regulator') for name in args.ward]
        available = sorted(set.intersection(*(set(t.index) for t in data)))
        delta = manifests[right]['proper_coordinate']-manifests[left]['proper_coordinate']
        for mass in available:
            c = data[1].loc[mass]
            terms = [(data[2].loc[mass, 'pr']-data[0].loc[mass, 'pr'])/delta,
                manifests[center]['log_lapse_gradient']*(c.rho+c.pr),
                2*manifests[center]['log_radius_gradient']*(c.pr-c.pt),
                .5*c.polarization*manifests[center]['mass_squared_gradient']]
            ward.append({'regulator': mass, 'proper_difference_interval': delta,
                'pressure_derivative': terms[0], 'lapse_term': terms[1],
                'angular_term': terms[2], 'material_exchange': terms[3],
                'sum': sum(terms), 'relative_residual': abs(sum(terms))/sum(abs(x) for x in terms)})
        pd.DataFrame(ward).to_csv(args.output/'ward_identity.csv', index=False)
    audit = {'scope': 'Tail-fit comparisons; acceptance also requires direct mode and regulator refinements',
        'inputs': {str(p/'manifest.json'): sha256_file(p/'manifest.json') for p in args.runs},
        'source_sha256': sha256_file(Path(__file__)),
        'outputs': {p.name: sha256_file(p) for p in args.output.iterdir() if p.suffix == '.csv'}}
    (args.output/'audit.json').write_text(json.dumps(audit, indent=2)+'\n')
    print(summary.to_string(index=False))
    if ward:
        print(pd.DataFrame(ward).to_string(index=False))


if __name__ == '__main__':
    main()
