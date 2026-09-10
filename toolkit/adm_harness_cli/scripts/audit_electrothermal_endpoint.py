#!/usr/bin/env python3
"""Independent material-label heat audit of the confined-field response."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import multiprocessing
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid

from adm_harness.active_transfer_reservoir import TabulatedActiveMedium, divergence_projections
from adm_harness.elastic_endpoint_reservoir import ElasticLaw
from adm_harness.electrothermal_endpoint import ElectricalLaw, ElectrothermalPatch
from adm_harness.source_ledger import sha256_file
from audit_active_transfer_reservoir import DirectMetricMedium, parameters

ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT/'supporting_reports/data/active_transfer_reservoir'
OUTPUT = ROOT/'supporting_reports/data/electrothermal_endpoint'


def audit(label):
    summary_path = OUTPUT/f'{label}_summary.json'
    state_path = OUTPUT/f'{label}_states.npz'
    summary = json.loads(summary_path.read_text())
    paths = INPUT/'metric_fine.npz', INPUT/f'medium_{summary["medium"]}.npz'
    model = TabulatedActiveMedium(*paths)
    patch = ElectrothermalPatch(model, ElasticLaw(**summary['material_law']),
                               ElectricalLaw(**summary['electrical_law']), cells=summary['cells'],
                               forcing=summary['forcing'], allocation=summary['allocation'])
    with np.load(state_path) as data:
        times, states, charges = data['t'], data['states'], data['charges']
        if not (np.isfinite(states).all() and np.isfinite(charges).all()
                and np.all(np.diff(times) > 0)):
            raise ValueError('finite states and strictly increasing snapshot times required')
        np.testing.assert_array_equal(data['x'], patch.x)
    _, _, final = patch.material_fields(times[-1], states[-1], charges[-1])
    initial_metric = model.metric(times[0], patch.x)
    initial_electric = .5*(charges[0, :-1]+charges[0, 1:])/initial_metric.radius**2
    initial_electric_force = initial_electric*np.diff(charges[0])/(patch.dx*initial_metric.volume)
    _, initial_endpoint_force = divergence_projections(initial_metric, *model.medium(times[0], patch.x))
    initial_force = {}
    for name, force in [('field', initial_electric_force), ('endpoint', initial_endpoint_force)]:
        index = int(np.argmax(abs(force)))
        initial_force[name] = dict(peak_absolute_force=float(abs(force[index])), peak_l=float(patch.x[index]),
                                  weighted_absolute_force=float(patch.dx*np.sum(initial_metric.alpha*initial_metric.volume*abs(force))))
    coldest = int(np.argmin(final['thermal']))
    labels = patch.dx*(np.cumsum(states[-1, 0])-.5*states[-1, 0])
    label_value = labels[coldest]
    rows = []
    for t, state, charge in zip(times, states, charges):
        g, _, f = patch.material_fields(t, state, charge)
        labels = patch.dx*(np.cumsum(state[0])-.5*state[0])
        position = float(np.interp(label_value, labels, patch.x))
        n, v, q = [float(np.interp(label_value, labels, f[k])) for k in ('n', 'velocity', 'thermal')]
        # Interpolate the primary flux Q; evaluate E on the witness metric.
        flux = float(np.interp(position, patch.faces, charge))
        gg = model.metric(t, np.array([position]))
        electric = flux/gg.radius[0]**2
        power, force = divergence_projections(gg, *model.medium(t, np.array([position])))
        factor = gg.alpha[0]*gg.radius[0]**2/(patch.law.scale*n)
        endpoint_heat = patch.forcing*factor*(-power[0]+v*force[0])
        ohmic_heat = factor*patch.electrical.sigma(q)*electric**2*np.sqrt(1-v*v)
        rows.append(dict(s=float(t), l=position, material_label=float(label_value), n=n, velocity=v,
                         thermal=q, electric_flux=flux, electric_field=float(electric),
                         endpoint_heat_rate=float(endpoint_heat), ohmic_heat_rate=float(ohmic_heat),
                         heat_rate=float(endpoint_heat+ohmic_heat),
                         packet_edge_distance=abs(position-t)-.35))
    frame = pd.DataFrame(rows)
    for key in ('endpoint_heat_rate', 'ohmic_heat_rate', 'heat_rate'):
        frame[f'integrated_{key}'] = cumulative_trapezoid(frame[key], frame.s, initial=0.)
    frame['heat_from_material_balance'] = frame.thermal.iloc[0]+frame.integrated_heat_rate
    frame.to_csv(OUTPUT/f'{label}_material_heat_audit.csv', index=False)
    source_comparison = {}
    direct = DirectMetricMedium(*paths, parameters(), 1e-5)
    last = frame.iloc[-1]
    for name, evaluator in [('interpolated', model), ('direct', direct)]:
        g = evaluator.metric(last.s, np.array([last.l]))
        power, force = divergence_projections(g, *evaluator.medium(last.s, np.array([last.l])))
        factor = g.alpha[0]*g.radius[0]**2/(patch.law.scale*last.n)
        endpoint = patch.forcing*factor*(-power[0]+last.velocity*force[0])
        ohmic = factor*patch.electrical.sigma(last.thermal)*(last.electric_flux/g.radius[0]**2)**2*np.sqrt(1-last.velocity**2)
        source_comparison[name] = dict(endpoint_heat_rate=float(endpoint), ohmic_heat_rate=float(ohmic),
                                       heat_rate=float(endpoint+ohmic))
    result = dict(case=label, final_time=float(times[-1]), status=summary['status'],
                  material_initial_l=float(frame.l.iloc[0]), material_final_l=float(last.l),
                  material_initial_thermal=float(frame.thermal.iloc[0]), material_final_thermal=float(last.thermal),
                  integrated_endpoint_heat=float(last.integrated_endpoint_heat_rate),
                  integrated_ohmic_heat=float(last.integrated_ohmic_heat_rate),
                  material_heat_balance_residual=float(last.thermal-last.heat_from_material_balance),
                  minimum_packet_distance=float(frame.packet_edge_distance.min()),
                  source_comparison=source_comparison,
                  initial_force_comparison=initial_force,
                  scope='material labels from conserved mass; snapshot-interpolated heat equation; final direct-metric source check at pinned physical state and electric flux; no direct-metric reintegration',
                  source_sha256={p.name: sha256_file(p) for p in (state_path, summary_path)},
                  audit_software_sha256=sha256_file(Path(__file__)))
    (OUTPUT/f'{label}_heat_audit.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(f'{label}: initial q={result["material_initial_thermal"]:.6g}; '
          f'endpoint heat={result["integrated_endpoint_heat"]:.6g}; '
          f'Ohmic heat={result["integrated_ohmic_heat"]:.6g}; '
          f'heat residual={result["material_heat_balance_residual"]:.6g}', flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cases', nargs='+')
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        for future in as_completed([pool.submit(audit, case) for case in args.cases]):
            future.result()


if __name__ == '__main__':
    main()
