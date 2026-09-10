#!/usr/bin/env python3
"""Compare reservoir responses on common material labels; numerical evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from adm_harness.active_transfer_reservoir import TabulatedActiveMedium
from adm_harness.elastic_endpoint_reservoir import ElasticLaw
from adm_harness.electrothermal_endpoint import ElectricalLaw
from adm_harness.material_ensemble import MaterialEnsemble
from adm_harness.relaxing_material_ensemble import RelaxingMaterialEnsemble, StrainRelaxation
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT/'supporting_reports/data/material_ensemble'
INPUT = OUTPUT.parent/'active_transfer_reservoir'


def load_case(label):
    metadata = json.loads((OUTPUT/f'{label}_summary.json').read_text())
    model = TabulatedActiveMedium(INPUT/'metric_fine.npz', INPUT/f'medium_{metadata["medium"]}.npz')
    cls, extra = MaterialEnsemble, {}
    if 'relaxation' in metadata:
        cls, extra = RelaxingMaterialEnsemble, {'relaxation': StrainRelaxation(**metadata['relaxation'])}
    patch = cls(model, ElasticLaw(**metadata['material_law']),
                ElectricalLaw(**metadata['electrical_law']), cells=metadata['cells'],
                thermal_share=metadata['thermal_share'], forcing=metadata['forcing'], **extra)
    with np.load(OUTPUT/f'{label}_states.npz') as data:
        times, states, reference = data['t'], data['states'], data['reference']
    np.testing.assert_allclose(reference, patch.reference, rtol=1e-13, atol=1e-14)
    fraction = np.r_[0., np.cumsum(reference)]/reference.sum()
    return metadata, patch, times, states, fraction


def compare(first, second, name):
    a, b = load_case(first), load_case(second)
    common = np.linspace(0., 1., 1001)
    inside = (common >= .15) & (common <= .85)
    eulerian_x = np.linspace(max(a[1].edges[0], b[1].edges[0]), min(a[1].edges[1], b[1].edges[1]), 1001)
    rows = []
    for t in a[2]:
        indices = np.flatnonzero(abs(b[2]-t) < 1e-10)
        if not indices.size:
            continue
        ia = int(np.argmin(abs(a[2]-t)))
        values, eulerian = [], []
        for case, index in ((a, ia), (b, int(indices[0]))):
            _, patch, _, states, fraction = case
            f = patch.fields(float(t), states[index])
            g = f['metric']
            rho_em = .5*(f['charge']/g.radius**2)**2
            moments = dict(density=patch.law.scale*f['energy_int']/(f['volume']*g.radius**2)+rho_em,
                           radial=patch.law.scale*f['radial_int']/(f['volume']*g.radius**2)-rho_em,
                           current=patch.law.scale*f['current_int']/(f['volume']*g.radius**2), angular=rho_em)
            fields = {key: f[key] for key in ('x', 'velocity', 'heat', 'charge')}
            fields.update(moments)
            values.append({key: np.interp(common, fraction, value) for key, value in fields.items()})
            eulerian.append({key: np.interp(eulerian_x, f['x'], value) for key, value in moments.items()})
        row = dict(s=float(t))
        for key in values[0]:
            error = values[0][key]-values[1][key]
            row[f'{key}_maximum_difference'] = float(np.max(abs(error)))
            row[f'{key}_rms_difference'] = float(np.sqrt(np.trapezoid(error**2, common)))
            norm = float(np.sqrt(np.trapezoid(values[1][key]**2, common)))
            row[f'{key}_relative_rms_difference'] = row[f'{key}_rms_difference']/max(norm, 1e-12)
            interior_error = float(np.trapezoid(error[inside]**2, common[inside]))
            interior_norm = float(np.trapezoid(values[1][key][inside]**2, common[inside]))
            row[f'{key}_interior_relative_rms_difference'] = float(np.sqrt(interior_error/max(interior_norm, 1e-24)))
            all_error = float(np.trapezoid(error**2, common))
            row[f'{key}_end_regions_squared_error_fraction'] = 1-interior_error/max(all_error, 1e-30) if all_error > 0 else 0.
        g = b[1].model.metric(float(t), eulerian_x)
        weight = g.b*g.radius**2
        for key in eulerian[0]:
            difference = np.trapezoid(weight*abs(eulerian[0][key]-eulerian[1][key]), eulerian_x)
            norm = np.trapezoid(weight*abs(eulerian[1][key]), eulerian_x)
            row[f'{key}_eulerian_volume_relative_l1_difference'] = float(difference/max(norm, 1e-12))
        rows.append(row)
    frame = pd.DataFrame(rows)
    frame.to_csv(OUTPUT/f'{name}.csv', index=False)
    final = frame.iloc[-1].to_dict()
    result = dict(first=first, second=second, final=final, comparison_times=len(frame),
                  scope='same normalized material reference coordinate; positions and state must converge together; tensor comparison is evaluated on those material histories, not at an independently fixed Eulerian coordinate',
                  regional_scope='interior reference fraction [0.15,0.85] diagnoses localization of errors; the whole-body comparison remains the acceptance scope, including both anchor regions',
                  eulerian_scope='additional fixed-coordinate L1 stress difference weighted by the shared proper-volume factor B R^2; interpolated nodal stresses',
                  maximum_differences={key: float(frame[key].max()) for key in frame.columns if key != 's'},
                  source_sha256={str(p.relative_to(ROOT)): sha256_file(p) for p in [
                      Path(__file__), OUTPUT/f'{first}_states.npz', OUTPUT/f'{second}_states.npz',
                      OUTPUT/f'{first}_summary.json', OUTPUT/f'{second}_summary.json']})
    (OUTPUT/f'{name}.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'comparison': name, **{key: final[key] for key in (
        's', 'x_rms_difference', 'velocity_rms_difference', 'heat_rms_difference',
        'density_relative_rms_difference', 'radial_relative_rms_difference')}}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('first')
    parser.add_argument('second')
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    compare(args.first, args.second, args.name)


if __name__ == '__main__':
    main()
