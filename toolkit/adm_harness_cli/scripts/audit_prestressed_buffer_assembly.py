#!/usr/bin/env python3
"""Measure stress, velocity localization, and spatial agreement in the new assembly."""
from concurrent.futures import ProcessPoolExecutor
import argparse
import json
import multiprocessing
from pathlib import Path

import numpy as np
import pandas as pd

from adm_harness.active_transfer_reservoir import TabulatedActiveMedium
from adm_harness.elastic_endpoint_reservoir import ElasticLaw
from adm_harness.electrothermal_endpoint import ElectricalLaw
from adm_harness.relaxing_material_ensemble import RelaxingMaterialEnsemble, StrainRelaxation
from adm_harness.prestressed_buffer_assembly import PrestressedBufferAssembly
from adm_harness.source_ledger import sha256_file
from audit_material_ensemble import load_case
from run_prestressed_buffer_assembly import ROOT, INPUT


def load_assembly(path):
    metadata = json.loads(path.read_text())
    state_path = path.with_name(path.name.replace('_summary.json', '_states.npz'))
    with np.load(state_path) as z:
        times, states, weights, reference = z['t'], z['states'], z['backbone_weight'], z['thermal_reference']
    model = TabulatedActiveMedium(INPUT/'metric_fine.npz', INPUT/'medium_baseline.npz')
    template = RelaxingMaterialEnsemble(model, ElasticLaw(stiffness=.1, scale=.4),
                                         ElectricalLaw(energy_ratio=4., conductivity=.1, profile='capacitor'),
                                         relaxation=StrainRelaxation(stiffness=.1, proper_time=1.),
                                         cells=metadata['cells'], thermal_share=1., forcing=1.)
    patch = PrestressedBufferAssembly(template, backbone_scale=metadata['backbone_scale'])
    np.testing.assert_allclose(reference, patch.reference, rtol=1e-12, atol=1e-13)
    patch.backbone_weight = weights
    if metadata['case'] == 'unforced':
        patch.forcing = 0.
    return metadata, patch, times, states


def projected(patch, t, state):
    f = patch.fields(float(t), state)
    g = f['metric']
    density = patch.law.scale*f['energy_int']/(f['volume']*g.radius**2)
    radial = patch.law.scale*f['radial_int']/(f['volume']*g.radius**2)
    return dict(x=f['x'], velocity=f['velocity'], heat=f['heat'], density=density, radial=radial)


def audit_case(path):
    metadata, patch, times, states = load_assembly(path)
    rows = []
    labels = np.r_[0., np.cumsum(patch.reference)]/np.sum(patch.reference)
    measure = patch.mass/patch.mass.sum()
    reference = load_case('relaxing/thermal_only_baseline_n64_end3_dt0.0005_snap601_cfl0.05')
    _, old, old_times, old_states, _ = reference
    old_witnesses = []
    for t, state in zip(old_times, old_states):
        f = projected(old, t, state)
        old_witnesses.append([np.max(abs(f['velocity'])), np.max(f['density']), np.max(abs(f['radial']))])
    old_witnesses = np.array(old_witnesses)
    for t, state in zip(times, states):
        f = projected(patch, t, state)
        peak = int(np.argmax(abs(f['velocity'])))
        row = dict(s=float(t), peak_velocity=float(f['velocity'][peak]), peak_velocity_fraction=float(labels[peak]),
                   peak_velocity_l=float(f['x'][peak]),
                   material_fraction_above_09=float(np.sum(measure[abs(f['velocity']) > .9])),
                   material_fraction_above_099=float(np.sum(measure[abs(f['velocity']) > .99])),
                   maximum_density=float(f['density'].max()), maximum_radial_stress=float(abs(f['radial']).max()))
        if t <= old_times[-1]+1e-12:
            reference_values = [np.interp(t, old_times, old_witnesses[:, i]) for i in range(3)]
            row.update(reference_maximum_speed=float(reference_values[0]),
                       density_peak_over_reference=float(row['maximum_density']/reference_values[1]),
                       radial_peak_over_reference=float(row['maximum_radial_stress']/reference_values[2]))
        rows.append(row)
    frame = pd.DataFrame(rows)
    prefix = path.name.removesuffix('_summary.json')
    frame.to_csv(path.with_name(prefix+'_local_audit.csv'), index=False)
    body_peak = frame.iloc[abs(frame.peak_velocity).argmax()]
    result = dict(case=metadata['case'], cells=metadata['cells'],
                  velocity_peak_location=body_peak[['s', 'peak_velocity', 'peak_velocity_fraction', 'peak_velocity_l']].to_dict(),
                  maximum_material_fraction_above_09=float(frame.material_fraction_above_09.max()),
                  maximum_material_fraction_above_099=float(frame.material_fraction_above_099.max()),
                  maximum_density_peak_ratio_on_common_interval=float(frame.density_peak_over_reference.max()),
                  maximum_radial_peak_ratio_on_common_interval=float(frame.radial_peak_over_reference.max()),
                  source_sha256={str(p.relative_to(ROOT)):sha256_file(p) for p in
                                 (path, path.with_name(prefix+'_states.npz'), Path(__file__),
                                  ROOT/'toolkit/adm_harness_cli/adm_harness/prestressed_buffer_assembly.py')})
    path.with_name(prefix+'_local_audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(prefix+': '+json.dumps(result['velocity_peak_location']), flush=True)
    return str(path)


def compare(first, second, output):
    _, a, ta, ya = load_assembly(first)
    _, b, tb, yb = load_assembly(second)
    fa = np.r_[0., np.cumsum(a.reference)]/np.sum(a.reference)
    fb = np.r_[0., np.cumsum(b.reference)]/np.sum(b.reference)
    weight = b.mass/b.mass.sum()
    end_region = (fb < .15) | (fb > .85)
    rows = []
    for requested in (.25, .5, .745, .815, 1., 1.285, 3.):
        if requested > min(ta[-1], tb[-1])+1e-9:
            continue
        ia, ib = int(np.argmin(abs(ta-requested))), int(np.argmin(abs(tb-requested)))
        if abs(ta[ia]-tb[ib]) > 1e-7 or abs(ta[ia]-requested) > .003:
            continue
        pa, pb = projected(a, ta[ia], ya[ia]), projected(b, tb[ib], yb[ib])
        row = dict(s=float(tb[ib]))
        for name in pa:
            delta = np.interp(fb, fa, pa[name])-pb[name]
            rms = np.sqrt(np.dot(weight, delta**2))
            row[name+'_rms'] = float(rms)
            if name in ('density', 'radial'):
                row[name+'_relative_rms'] = float(rms/np.sqrt(np.dot(weight, pb[name]**2)))
                row[name+'_squared_error_at_ends'] = float(np.dot(weight[end_region], delta[end_region]**2)
                                                          /max(np.dot(weight, delta**2), 1e-30))
        rows.append(row)
    pd.DataFrame(rows).to_csv(output, index=False)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    paths = sorted(args.directory.resolve().glob('*_summary.json'))
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        list(pool.map(audit_case, paths))
    pairs = []
    for case in ('equilibrated', 'energy_matched'):
        subset = [path for path in paths if path.name.startswith(case+'_n')]
        subset.sort(key=lambda path:json.loads(path.read_text())['cells'])
        if len(subset)==2:
            target = args.directory/(case+'_spatial_comparison.csv')
            pairs.append(dict(first=str(subset[0].relative_to(ROOT)), second=str(subset[1].relative_to(ROOT)),
                              comparison=compare(*subset, target)))
    (args.directory/'spatial_comparison.json').write_text(json.dumps(pairs, indent=2)+'\n')


if __name__ == '__main__':
    main()
