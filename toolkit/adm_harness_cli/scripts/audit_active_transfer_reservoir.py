#!/usr/bin/env python3
"""Numerical audits of the active transfer witness and input representation.

The direct-metric cases bypass the metric interpolant and exterior completion.
Only numerical evidence is generated; the investigation report is manual.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import json
import multiprocessing
from pathlib import Path

import numpy as np
import pandas as pd

from adm_harness.active_transfer_reservoir import (
    MetricJets, TabulatedActiveMedium, divergence_projections, medium_mask,
    trace_characteristics,
)
from adm_harness.metric_regularity import regularized_scalars
from adm_harness.source_ledger import SourceParams, sha256_file


ROOT = Path(__file__).resolve().parents[3]
CASES = [
    ('interpolated_baseline', 'baseline', False, .00125, 0.),
    ('direct_baseline', 'baseline', True, .0025, .00002),
    ('direct_refined_baseline', 'baseline', True, .00125, .00001),
    ('direct_dense', 'dense', True, .0025, .00002),
]


class DirectMetricMedium(TabulatedActiveMedium):
    def __init__(self, metric_path, medium_path, params, step):
        super().__init__(metric_path, medium_path)
        self.params, self.step = params, step

    def fields(self, t, x):
        rows = []
        for point in x:
            g = regularized_scalars(float(t), float(point), self.params)
            rows.append([np.log(g['alpha']), g['beta'],
                         .5*np.log(g['gamma_ll']), .5*np.log(g['gamma_omega'])])
        return np.array(rows).T

    def metric(self, t, x):
        x = np.asarray(x, dtype=float)
        h = self.step
        values = self.fields(t, x)
        dx = (self.fields(t, x+h)-self.fields(t, x-h))/(2*h)
        dt = (self.fields(t+h, x)-self.fields(t-h, x))/(2*h)
        a, beta, b, r = np.exp(values[0]), values[1], np.exp(values[2]), np.exp(values[3])
        return MetricJets(a, beta, b, r, a*dx[0], dx[1], dt[2], dx[2], dt[3], dx[3])


def parameters():
    manifest = ROOT/'supporting_reports/data/le_metric_c2_repair/manifest.json'
    return SourceParams(**json.loads(manifest.read_text())['params'])


def audit_witness(task):
    case, output = task
    name, surface, direct, step, derivative_step = case
    output = Path(output)
    paths = (output/'metric_fine.npz', output/f'medium_{surface}.npz')
    model = (DirectMetricMedium(*paths, parameters(), derivative_step) if direct
             else TabulatedActiveMedium(*paths))
    times = np.linspace(-1.5, .48, round(1.98/step)+1)
    history = trace_characteristics(model, np.array([-1.305]), times, -1)
    x, log_gain, integral = history[:, 0, 0], history[:, 1, 0], history[:, 2, 0]
    # This bound uses only the single specified later event. It is independent
    # of the ray's later encounter with the outer taper or exterior completion.
    preload = max(0., -float(integral[-1]))
    index = int(np.argmin(abs(times+.5525)))
    t, position = times[index], x[index]
    g = model.metric(t, np.array([position]))
    density = np.exp(log_gain[index])*(preload+integral[index])/g.volume[0]
    power, force = divergence_projections(g, *model.medium(t, np.array([position])))
    row = dict(case=name, medium=surface, direct_metric=direct, dt=step,
               derivative_step=derivative_step, initial_l=-1.305,
               witness_s=t, witness_l=position, future_s=times[-1], future_l=x[-1],
               future_integral=integral[-1], witness_integral=integral[index],
               necessary_preload=preload, witness_stream_density=density,
               witness_power=power[0], witness_force=force[0],
               max_abs_l_until_future=float(abs(x).max()),
               packet_edge_distance=parameters().Rpass-abs(position-t))
    pd.DataFrame(dict(s=times, l=x, log_gain=log_gain, source_integral=integral,
                      preload_bound=preload)).to_csv(output/f'audit_{name}_ray.csv', index=False)
    print(f'{name}: required packet density {density:.9g}', flush=True)
    return row


def representation_audit(output):
    params = parameters()
    rows = []
    for surface in ('baseline', 'dense'):
        with np.load(output/f'medium_{surface}.npz') as data:
            t, x = data['t'], data['x']
            chosen = (t >= -1.5) & (t <= 3.)
            t = t[chosen]
            mask = medium_mask(t[:, None], x[None, :])[0]
            integrate = lambda a: float(np.trapezoid(np.trapezoid(a, x, axis=1), t))
            total, removed = 0., 0.
            for key in ('rho', 'pressure', 'current', 'angular'):
                raw = abs(data[key][chosen])
                norm, difference = integrate(raw), integrate(raw*(1-mask))
                total += norm; removed += difference
                rows.append(dict(medium=surface, moment=key, coordinate_L1=norm,
                                 mask_removed_L1=difference, removed_fraction=difference/norm))
            rows.append(dict(medium=surface, moment='sum_absolute_moments', coordinate_L1=total,
                             mask_removed_L1=removed, removed_fraction=removed/total))
    pd.DataFrame(rows).to_csv(output/'medium_representation_audit.csv', index=False)
    rows = []
    model = TabulatedActiveMedium(output/'metric_fine.npz', output/'medium_baseline.npz')
    for t in np.linspace(-1.5, 3., 17):
        for x in np.r_[np.linspace(-8., -5., 25), np.linspace(5., 8., 25)]:
            reference = regularized_scalars(float(t), float(x), params)
            observed = model.metric(t, np.array([x]))
            for key, value in [('alpha', observed.alpha[0]), ('beta', observed.beta[0]),
                               ('gamma_ll', observed.b[0]**2), ('gamma_omega', observed.radius[0]**2)]:
                scale = max(abs(reference[key]), 1.) if key == 'beta' else abs(reference[key])
                rows.append(dict(s=t, l=x, field=key, reference=reference[key],
                                 interpolated=value, relative_error=abs(value-reference[key])/scale))
    pd.DataFrame(rows).to_csv(output/'exterior_completion_audit.csv', index=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/active_transfer_reservoir')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('use between one and six workers')
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        rows = list(pool.map(audit_witness, [(case, str(args.output)) for case in CASES]))
    pd.DataFrame(rows).to_csv(args.output/'direct_metric_witness_audit.csv', index=False)
    representation_audit(args.output)
    files = [Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/active_transfer_reservoir.py']
    inputs = [args.output/name for name in ('input_manifest.json', 'run_manifest.json',
              'metric_fine.npz', 'medium_baseline.npz', 'medium_dense.npz')]
    manifest = {
        'completed_utc': datetime.now(timezone.utc).isoformat(), 'workers': args.workers,
        'software_sha256': {str(p.relative_to(ROOT)): sha256_file(p) for p in files},
        'input_sha256': {p.name: sha256_file(p) for p in inputs},
        'metric_representation': 'raw metric grids retained; transport evaluation uses a C2 exterior blend over 5<|l|<6; direct-metric witnesses bypass both interpolation and completion',
        'prior_input_manifest_note': 'input_manifest.json describes raw preparation before the C2 exterior evaluation update; run_manifest software hashes identify the actual transport implementation',
        'medium_norm': 'coordinate spacetime L1 of archived knot values over -1.5<=s<=3; sum uses absolute moments separately; this is a representation diagnostic, not proper energy or a source-closure norm',
        'single_future_event_bound': 'nonnegative stream density at s=0.48 sets a necessary preload and earlier packet-density bound on initial ray l=-1.305',
    }
    (args.output/'audit_manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
