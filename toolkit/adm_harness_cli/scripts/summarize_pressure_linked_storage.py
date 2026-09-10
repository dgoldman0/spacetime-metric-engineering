#!/usr/bin/env python3
"""Numeric channel requirements, comparison plots, and artifact integrity."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from adm_harness.active_transfer_reservoir import TabulatedActiveMedium
from adm_harness.pressure_linked_storage import fluid_coefficients, balanced_end_witness
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT/'supporting_reports/data/pressure_linked_storage'
OUTPUT = DATA/'derived'
FIGURES = ROOT/'supporting_reports/figures'
INPUT = ROOT/'supporting_reports/data/active_transfer_reservoir'


def interface_requirements(model, path):
    with np.load(path) as z:
        t, x, h = z['t'], z['x'], z['flux_energy']
    midpoint = .5*(t[1:]+t[:-1]); dt = np.diff(t)[:, None]
    c = fluid_coefficients(model, midpoint, x)
    charging = np.diff(h, axis=0)/(dt*c['lapse']*c['radius']**4)
    net = -c['gamma']*(c['power']-c['v']*c['normal_force'])
    # One explicit split: endpoint work feeds positive charging; field
    # discharge feeds fluid heat. The complementary endpoint channel is heat.
    work = np.maximum(charging, 0.)
    heat = net-work
    weight = 4*np.pi*c['lapse']*c['rest_volume']
    integrate = lambda value: float(np.sum(np.trapezoid(weight*value, x, axis=1)*np.diff(t)))
    channels = dict(charging_work=work, endpoint_heat_return=np.maximum(-heat, 0.),
                    endpoint_heat_input=np.maximum(heat, 0.), endpoint_net=net,
                    endpoint_net_input=np.maximum(net, 0.), endpoint_net_output=np.maximum(-net, 0.),
                    heat_return_during_net_endpoint_input=np.where(net >= 0, np.maximum(-heat, 0.), 0.))
    result = dict(case=path.stem.removesuffix('_states'), stage=path.parent.name)
    for name, value in channels.items():
        result[name+'_rest_throughput'] = integrate(value)
        result[name+'_maximum_rest_power_density'] = float(abs(value).max())
    result['split_identity_maximum_residual'] = float(abs(work+heat-net).max())
    result['interpretation'] = 'proper-worldtube integrals of rest power; processed work and heat, not minimum initial store capacity or conserved Killing energy'
    label = path.parent.name+'_'+result['case']
    series = dict(s=midpoint)
    for name, value in channels.items():
        series[name+'_worldtube_rate'] = np.trapezoid(weight*value, x, axis=1)
    pd.DataFrame(series).to_csv(OUTPUT/(label+'_channels.csv'), index=False)
    np.savez_compressed(OUTPUT/(label+'_channel_maps.npz'), s=midpoint, x=x, charging_work=work,
                        endpoint_heat_return=np.maximum(-heat, 0.), endpoint_net=net)
    return result, (midpoint, x, work, np.maximum(-heat, 0.), net)


def verify_stages():
    rows = []
    for manifest in sorted(DATA.glob('*/manifest.json')):
        if manifest.parent == OUTPUT:
            continue
        stage = json.loads(manifest.read_text())
        revision = stage['git_revision']
        for relative, expected in stage['software_and_input_sha256'].items():
            path = ROOT/relative
            actual = sha256_file(path)
            if actual != expected:
                historical = subprocess.run(['git', 'show', revision+':'+relative], cwd=ROOT, capture_output=True, check=True).stdout
                actual = hashlib.sha256(historical).hexdigest()
            rows.append(dict(stage=manifest.parent.name, kind='source_or_input', path=relative, match=actual == expected))
        for relative, expected in stage['output_sha256'].items():
            rows.append(dict(stage=manifest.parent.name, kind='output', path=relative,
                             match=sha256_file(manifest.parent/relative) == expected))
    frame = pd.DataFrame(rows)
    frame.to_csv(OUTPUT/'integrity.csv', index=False)
    if not frame['match'].all():
        raise RuntimeError('stage integrity failure')
    return len(frame)


def main():
    OUTPUT.mkdir(exist_ok=True); FIGURES.mkdir(exist_ok=True)
    rows = []
    for path in sorted(DATA.glob('*/*_summary.json')):
        item = json.loads(path.read_text())
        if 'case' not in item:
            continue
        row = dict(stage=path.parent.name, case=item['case'], success=item['success'], message=item.get('message', ''))
        for key in ('initial_slice_energy', 'final_slice_energy', 'maximum_supplied_null',
                    'secondary_energy_optimization_succeeded', 'maximum_charge_rate', 'maximum_discharge_rate',
                    'maximum_left_traction', 'maximum_right_traction', 'maximum_raw_equality_residual'):
            row[key] = item.get(key)
        row['fade_required_negative_null'] = next((p['required_negative_null'] for p in item.get('phases', []) if p['s'] == 1.285), None)
        rows.append(row)
    pd.DataFrame(rows).to_csv(OUTPUT/'case_comparison.csv', index=False)
    model = TabulatedActiveMedium(INPUT/'metric_fine.npz', INPUT/'medium_baseline.npz')
    requirements = []
    for stage, case in (('conversion_controls', 'powered_finite_n64'),
                        ('retained_coefficients', 'powered_finite_joint'),
                        ('retained_coefficients', 'heat_engine_n64')):
        result, maps = interface_requirements(model, DATA/stage/(case+'_states.npz'))
        requirements.append(result)
        if case == 'powered_finite_joint':
            selected = maps
    pd.DataFrame(requirements).to_csv(OUTPUT/'interface_requirements.csv', index=False)

    # Extend the reaction witness to finite charging and discharging. The
    # coefficient minimum now covers r in [-2 sigma N, +2 sigma N].
    with np.load(DATA/'retained_coefficients/powered_finite_joint_states.npz') as state:
        oldx, number = state['x'], state['number']
    witness_rows = []
    for nodes in (1025, 2049):
        x = np.linspace(-2.1, -.5, nodes)
        c = {key: value[0] for key, value in fluid_coefficients(model, np.array([1.285]), x).items()}
        for sigma in (1., 10.):
            witness = balanced_end_witness(x, c, np.interp(x, oldx, number), model.metric(1.285, x).logr_x, sigma)
            b = 4*c['v']/(3*c['lapse']*c['radius']**2)
            minimum = witness['coefficient']-4*model.metric(1.285, x).logr_x-abs(b*c['rest_volume'])*2*sigma*c['lapse']
            inertia = -c['gamma']*c['b']*c['acceleration']*np.interp(x, oldx, number)/c['rest_volume']
            witness_rows.append(dict(nodes=nodes, sigma=sigma, weighted_drive=witness['weighted_drive_integral'],
                minimum_field_coefficient=float(minimum.min()),
                cold_inertia_drive=float(np.trapezoid(witness['weight']*inertia, x))))
    pd.DataFrame(witness_rows).to_csv(OUTPUT/'bidirectional_reaction_witness.csv', index=False)

    tm, x, work, returned, net = selected
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.3), constrained_layout=True, sharex=True, sharey=True)
    for ax, value, title in zip(axes, (work, returned), ('Electrical work for charging', 'Heat returned to the endpoint')):
        picture = ax.pcolormesh(x, tm, value, shading='auto', cmap='magma', vmin=0, vmax=max(work.max(), returned.max()))
        ax.set(title=title, xlabel='Rail coordinate x')
    axes[0].set_ylabel('Active time s')
    fig.colorbar(picture, ax=axes, label='Required rest power density (model units)', shrink=.9)
    fig.suptitle('Separate work and heat duties in the connected storage assembly', fontsize=12)
    for suffix in ('png', 'pdf'):
        fig.savefig(FIGURES/('pressure_linked_interface.'+suffix), dpi=180)
    plt.close(fig)
    comparisons = verify_stages()
    files = [p for p in OUTPUT.iterdir() if p.is_file() and p.name != 'manifest.json']
    files += [FIGURES/('pressure_linked_interface.'+suffix) for suffix in ('png', 'pdf')]
    metadata = dict(completed_utc=datetime.now(timezone.utc).isoformat(), stage_hash_comparisons=comparisons,
                    software_sha256={str(Path(__file__).relative_to(ROOT)): sha256_file(Path(__file__)),
                        'toolkit/adm_harness_cli/adm_harness/pressure_linked_storage.py': sha256_file(ROOT/'toolkit/adm_harness_cli/adm_harness/pressure_linked_storage.py')},
                    output_sha256={str(p.relative_to(ROOT)): sha256_file(p) for p in files})
    (OUTPUT/'manifest.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps(dict(integrity_comparisons=comparisons, interfaces=requirements), indent=2))


if __name__ == '__main__':
    main()
