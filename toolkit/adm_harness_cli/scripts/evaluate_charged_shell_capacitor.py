#!/usr/bin/env python3
"""Bounded parallel charged-shell controls, separate from the active rail metric."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import multiprocessing

import numpy as np
import pandas as pd
from scipy.integrate import quad

from adm_harness.charged_capacitor import (
    condenser_parameters, electric_gap_energy, electrovacuum_jet,
    shell_potential_jet, shell_state,
)
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT/'supporting_reports/data/charged_capacitor_shells'
B_VALUES = (1.05, 1.2, 1.5, 2., 4., 10., 30.)
Q_VALUES = np.unique(np.r_[np.geomspace(.01, .2, 36), np.linspace(.2, 1.15, 64)])
MI_VALUES = np.unique(np.r_[np.geomspace(1e-5, .05, 72), np.linspace(.05, .98, 96)])
FRACTIONS = np.unique(np.r_[np.geomspace(1e-9, .04, 96), np.linspace(.04, .98, 96)])


def scan_radius(b):
    mi, fraction = np.meshgrid(MI_VALUES, FRACTIONS, indexing='ij')
    rows, best = [], {}
    counts = dict(sampled=0, horizon_free=0, DEC=0, DEC_radial_causal=0,
                  compressive_radial_half_slope=0)
    for q in Q_VALUES:
        mu, mass, mo, minimum_f = condenser_parameters(b, q, mi, fraction)
        good = (minimum_f > 1e-8)&(mass > 0)&(2*mass/b < 1)
        counts['sampled'] += mi.size
        counts['horizon_free'] += int(good.sum())
        if not good.any():
            continue
        mii, frac, mu, mass, mo, minimum_f = [v[good] for v in (mi, fraction, mu, mass, mo, minimum_f)]
        si, pi = shell_state(1., 0., 0., mu, q)
        so, po = shell_state(b, mu, q, mass, 0.)
        dec = (si >= abs(pi))&(so >= abs(po))
        counts['DEC'] += int(dec.sum())
        # V'' is affine in dp/dsigma. The interval endpoint maximum suffices
        # for existence of a stable radial slope in the specified interval.
        vi0 = shell_potential_jet(1., 0., 0., mu, q, 0.)[2]
        vi1 = shell_potential_jet(1., 0., 0., mu, q, 1.)[2]
        vo0 = shell_potential_jet(b, mu, q, mass, 0., 0.)[2]
        vo1 = shell_potential_jet(b, mu, q, mass, 0., 1.)[2]
        causal = dec&(np.maximum(vi0, vi1) > 1e-7)&(np.maximum(vo0, vo1)*b*b > 1e-7)
        compressive = (dec&(pi >= 0)&(po >= 0)&(pi <= si/2)&(po <= so/2)
                       &(np.maximum(vi0, (vi0+vi1)/2) > 1e-7)
                       &(np.maximum(vo0, (vo0+vo1)/2)*b*b > 1e-7))
        counts['DEC_radial_causal'] += int(causal.sum())
        counts['compressive_radial_half_slope'] += int(compressive.sum())
        compactness = np.maximum.reduce([2*mu, np.full_like(mu, q*q), 2*mass/b])
        # The gap energy depends only on q, b and the inner shell. Evaluate
        # it once per inner mass, then use the exact same value for each outer
        # fraction. This keeps the deterministic scan small in memory.
        unique_mu, inverse = np.unique(mu, return_inverse=True)
        # Near-extreme gaps have a narrow proper-volume peak. Adaptive
        # integration splits at the metric minimum, preserving that energy.
        integrals = []
        for mu_value in unique_mu:
            critical = q*q/mu_value
            points = [critical] if 1 < critical < b else None
            integrals.append(quad(lambda r: q*q/(2*r*r*np.sqrt(
                electrovacuum_jet(r, mu_value, q)[0])), 1., b, points=points,
                epsabs=1e-13, epsrel=1e-11)[0])
        u = np.asarray(integrals)[inverse]
        ratio = u/(mii+mo)
        for name, mask in (('DEC', dec), ('DEC_radial_causal', causal),
                           ('weak_DEC_radial_causal', causal&(compactness <= .01)),
                           ('compressive_radial_half_slope', compressive)):
            if not mask.any():
                continue
            indices = np.flatnonzero(mask)
            j = indices[np.argmax(ratio[indices])]
            eta_max = .5 if name == 'compressive_radial_half_slope' else 1.
            ei = eta_max if vi1[j] >= vi0[j] else 0.
            eo = eta_max if vo1[j] >= vo0[j] else 0.
            record = dict(family=name, outer_radius=b, charge=float(q),
                inner_rest_mass=float(mii[j]), outer_fraction=float(frac[j]),
                outer_rest_mass=float(mo[j]), gap_mass=float(mu[j]), ADM_mass=float(mass[j]),
                proper_field_energy=float(u[j]), field_to_wall_rest_energy=float(ratio[j]),
                inner_pressure_ratio=float(pi[j]/si[j]), outer_pressure_ratio=float(po[j]/so[j]),
                inner_sound_squared=ei, outer_sound_squared=eo,
                inner_Vpp=float(vi0[j]+ei*(vi1[j]-vi0[j])),
                outer_Vpp=float(vo0[j]+eo*(vo1[j]-vo0[j])),
                compactness_measure=float(compactness[j]), minimum_gap_f=float(minimum_f[j]),
                matched_Killing_field_energy=float((1-frac[j])*q*q/2*(1-1/b)))
            rows.append(record)
            if name not in best or record['field_to_wall_rest_energy'] > best[name]['field_to_wall_rest_energy']:
                best[name] = record
    print(f'b/a={b:g}: {counts["DEC_radial_causal"]} DEC/radial-slope passes', flush=True)
    return dict(radius=b, counts=counts, best=list(best.values()), rows=rows)


def main():
    if OUTPUT.exists():
        raise RuntimeError('preserve completed capacitor-shell evidence')
    OUTPUT.mkdir(parents=True)
    with ProcessPoolExecutor(max_workers=4, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(scan_radius, B_VALUES))
    pd.DataFrame([row for result in results for row in result.pop('rows')]).to_csv(OUTPUT/'charge_envelopes.csv', index=False)
    selected = [row for result in results for row in result['best']]
    pd.DataFrame(selected).to_csv(OUTPUT/'best_sampled.csv', index=False)
    checks = []
    for row in selected:
        args = (1., row['outer_radius'], row['gap_mass'], row['charge'])
        refined = float(electric_gap_energy(*args, order=1024)[0])
        checks.append(dict(family=row['family'], outer_radius=row['outer_radius'],
            relative_quadrature_change=abs(refined/row['proper_field_energy']-1)))
    pd.DataFrame(checks).to_csv(OUTPUT/'quadrature_checks.csv', index=False)
    if max(row['relative_quadrature_change'] for row in checks) > 1e-7:
        raise ArithmeticError('selected gap energy needs finer quadrature')
    summary = dict(created_utc=datetime.now(timezone.utc).isoformat(), results=results,
        grid=dict(b=list(B_VALUES), charge=list(Q_VALUES), inner_rest_mass=list(MI_VALUES), outer_fraction=list(FRACTIONS)),
        stability='Fixed shell charges and electrovacuum masses; independent local radial perturbations. '
                  'The sound slope may differ on each shell. Finite layers, angular modes and a physical EOS remain open.',
        role='Spherical boundary analogue; no replacement of the scheduled rail geometry or its tensor.',
        weak_gravity_DEC_field_to_wall_bound='2*(b-a)/(b+a), for positive-energy isolated spherical charged shells.')
    (OUTPUT/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    paths = [Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/charged_capacitor.py',
             ROOT/'toolkit/adm_harness_cli/tests/test_charged_capacitor.py']
    manifest = dict(input_sha256={str(p.relative_to(ROOT)): sha256_file(p) for p in paths},
                    output_sha256={p.name: sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()})
    (OUTPUT/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')


if __name__ == '__main__':
    main()
