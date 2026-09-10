#!/usr/bin/env python3
"""Track the first depleted material element and its physical heat balance."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid

from adm_harness.active_transfer_reservoir import TabulatedActiveMedium, divergence_projections
from adm_harness.elastic_endpoint_reservoir import ElasticLaw, recover
from adm_harness.source_ledger import sha256_file
from audit_active_transfer_reservoir import DirectMetricMedium, parameters


ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT/'supporting_reports/data/active_transfer_reservoir'
OUTPUT = ROOT/'supporting_reports/data/elastic_endpoint_reservoir'


def audit(label):
    summary = json.loads((OUTPUT/f'{label}_summary.json').read_text())
    law = ElasticLaw(**summary['law'])
    paths = INPUT/'metric_fine.npz', INPUT/f'medium_{summary["medium"]}.npz'
    model = TabulatedActiveMedium(*paths)
    direct = DirectMetricMedium(*paths, parameters(), 1e-5)
    with np.load(OUTPUT/f'{label}_states.npz') as data:
        times, x, states = data['t'], data['x'], data['states']
    dx = x[1]-x[0]
    final = recover(states[-1], model.metric(times[-1], x).b, law)
    coldest = int(np.argmin(final['thermal']))
    label_value = dx*(np.cumsum(states[-1, 0])-.5*states[-1, 0])[coldest]
    records = []
    for t, state in zip(times, states):
        g = model.metric(t, x)
        fields = recover(state, g.b, law)
        labels = dx*(np.cumsum(state[0])-.5*state[0])
        location = float(np.interp(label_value, labels, x))
        n, v, q = [float(np.interp(label_value, labels, fields[key])) for key in ('n', 'velocity', 'thermal')]
        metric = model.metric(t, np.array([location]))
        power, force = divergence_projections(metric, *model.medium(t, np.array([location])))
        power, force = float(power[0]), float(force[0])
        factor = float(metric.alpha[0]*metric.radius[0]**2/(law.scale*n))
        records.append(dict(s=t, l=location, material_label=label_value, n=n, velocity=v,
                            thermal=q, endpoint_power=power, endpoint_force=force,
                            heat_power_part=-factor*power, heat_force_work_part=factor*v*force,
                            heat_rate=factor*(-power+v*force),
                            packet_edge_distance=abs(location-t)-.35))
    frame = pd.DataFrame(records)
    frame['integrated_heat_rate'] = cumulative_trapezoid(frame.heat_rate, frame.s, initial=0.)
    frame['heat_from_material_balance'] = frame.thermal.iloc[0]+frame.integrated_heat_rate
    frame.to_csv(OUTPUT/f'{label}_material_heat_audit.csv', index=False)
    t, position = float(times[-1]), float(x[coldest])
    primitive = {key: float(final[key][coldest]) for key in ('n', 'velocity', 'thermal')}
    source_comparison = {}
    for name, evaluator in [('interpolated', model), ('direct', direct)]:
        metric = evaluator.metric(t, np.array([position]))
        power, force = divergence_projections(metric, *evaluator.medium(t, np.array([position])))
        factor = metric.alpha[0]*metric.radius[0]**2/(law.scale*primitive['n'])
        source_comparison[name] = dict(power=float(power[0]), force=float(force[0]),
            heat_rate=float(factor*(-power[0]+primitive['velocity']*force[0])))
    result = dict(case=label, final_time=t, first_depleted_l=position,
                   material_initial_l=float(frame.l.iloc[0]),
                   material_initial_thermal=float(frame.thermal.iloc[0]),
                   material_final_thermal=float(frame.thermal.iloc[-1]),
                   integrated_material_heat_rate=float(frame.integrated_heat_rate.iloc[-1]),
                   material_heat_balance_residual=float(frame.thermal.iloc[-1]-frame.heat_from_material_balance.iloc[-1]),
                   minimum_packet_edge_distance=float(frame.packet_edge_distance.min()),
                   source_comparison=source_comparison,
                   scope='material labels inferred from conserved particle integrals; trapezoidal heat balance along interpolated snapshots; direct metric checks the local source with pinned physical n,v, not a reintegrated solution',
                   source_sha256={p.name: sha256_file(p) for p in (OUTPUT/f'{label}_states.npz', OUTPUT/f'{label}_summary.json')})
    (OUTPUT/f'{label}_heat_audit.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: result[k] for k in ('case', 'material_initial_l', 'material_initial_thermal',
                                            'integrated_material_heat_rate', 'material_heat_balance_residual')}, indent=2))
    return frame


def plot(frame):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.2), layout='constrained')
    axes[0].plot(frame.s, frame.thermal, color='#a32438', label='Evolved material heat')
    axes[0].plot(frame.s, frame.heat_from_material_balance, '--', color='#246c8b', label='Integrated heat balance')
    axes[0].axhline(0., color='#555', lw=.7)
    axes[0].set(xlabel='Service coordinate s', ylabel='Thermal energy per material unit', title='First depleted material element')
    axes[0].legend(frameon=False)
    axes[1].plot(frame.s, frame.heat_power_part, label='Endpoint power contribution', color='#246c8b')
    axes[1].plot(frame.s, frame.heat_force_work_part, label='Force-work contribution', color='#916825')
    axes[1].plot(frame.s, frame.heat_rate, label='Net material heating rate', color='#a32438')
    axes[1].axhline(0., color='#555', lw=.7)
    axes[1].set(xlabel='Service coordinate s', ylabel='Thermal energy rate', title='Power and force determine local heating')
    axes[1].legend(frameon=False)
    for axis in axes:
        axis.grid(alpha=.18)
    fig.savefig(OUTPUT/'prepared_elastic_heat_witness.png', dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cases', nargs='+')
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    for i, name in enumerate(args.cases):
        frame = audit(name)
        if args.plot and i == 0:
            plot(frame)


if __name__ == '__main__':
    main()
