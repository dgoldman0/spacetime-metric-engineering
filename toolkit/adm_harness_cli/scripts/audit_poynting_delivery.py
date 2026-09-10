#!/usr/bin/env python3
"""Independent ray quadrature, refinement tables, figures, and evidence hashes."""
from datetime import datetime, timezone
from pathlib import Path
import json

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from adm_harness.source_ledger import sha256_file
from run_poynting_delivery import DeliveryHistory, BASE, ROOT, write_json

OUTPUT = BASE/'poynting_delivery/audit'


def direct_rays(h, seeds, subdivision):
    """RK4 quadrature of the integrating-factor solution, independently of FV.

X_t=v, log(g)_t=alpha K_l-sigma alpha_x/B-v_x. Initial D needed for
future absorption is integral of source/g along the ray until it exits.
Temporal steps split at every archived field-history knot.
"""
    y = np.zeros((3, len(seeds)))
    y[0] = seeds
    direction = -1
    st = h.state
    for i, duration in enumerate(np.diff(st['t'])):
        step = duration/subdivision
        hd = h.hdot[i]

        def rhs(tt, state):
            x, logarithm, unused = state
            g = h.model.metric(float(tt), x)
            v_material = g.b*g.beta/g.alpha
            velocity = -g.beta+direction*g.alpha/g.b
            vx = -g.beta_x+direction*(g.alpha_x-g.alpha*g.logb_x)/g.b
            gain = g.alpha*g.k_l-direction*g.alpha_x/g.b-vx
            drive = np.maximum(np.interp(x, st['x'], hd), 0)/.98
            active = (x >= st['x'][0])&(x <= st['x'][-1])
            source = active*g.b*drive/(g.radius**2*(1-direction*v_material))
            return np.array([velocity, gain, source*np.exp(-logarithm)])

        for j in range(subdivision):
            now = st['t'][i]+j*step
            k1 = rhs(now, y)
            k2 = rhs(now+step/2, y+step*k1/2)
            k3 = rhs(now+step/2, y+step*k2/2)
            k4 = rhs(now+step, y+step*k3)
            y += step*(k1+2*k2+2*k3+k4)/6
    return y[2]


def main():
    if OUTPUT.exists():
        raise RuntimeError('preserve the completed independent audit')
    OUTPUT.mkdir(parents=True)
    h = DeliveryHistory(1024)
    seeds = np.array([-1.95, -1.7, -1.4, -1.1, -.9, -.7, -.55])
    d4, d8 = direct_rays(h, seeds, 4), direct_rays(h, seeds, 8)
    ray_rows = []
    for cells in (512, 1024):
        z = np.load(BASE/f'poynting_delivery/spatial_refinement/right_n{cells}_t1_states.npz')
        g = h.model.metric(0., z['x'])
        fv = np.interp(seeds, z['x'], g.b*g.radius**2*z['mu_minus'][0])
        for j, x in enumerate(seeds):
            ray_rows.append(dict(cells=cells, x=float(x), finite_volume=float(fv[j]),
                independent_ray=float(d8[j]), ray_quadrature_relative_change=float(abs(d8[j]-d4[j])/max(d8[j], 1e-30)),
                relative_FV_difference=float(abs(fv[j]-d8[j])/max(d8[j], 1e-30))))
    pd.DataFrame(ray_rows).to_csv(OUTPUT/'independent_rays.csv', index=False)
    rows = []
    for directory in ('route_screen', 'spatial_refinement', 'time_refinement'):
        for p in sorted((BASE/'poynting_delivery'/directory).glob('*_summary.json')):
            d = json.loads(p.read_text())
            rows.append({key: d[key] for key in ('case', 'route', 'cells', 'temporal_factor',
                'initial_wave_slice_energy', 'initial_wave_material_inventory', 'absorbed_boundary_energy',
                'recovered_boundary_energy', 'final_wave_slice_energy', 'peak_wave_null')})
    pd.DataFrame(rows).to_csv(OUTPUT/'transport_comparison.csv', index=False)
    data = np.load(BASE/'poynting_delivery/shared_field/selected_n1024_states.npz')
    histories = pd.read_csv(BASE/'poynting_delivery/shared_field/selected_n1024_inventories.csv')
    old = pd.read_csv(BASE/'regenerative_converter/refined_eta098_recovery100_voltage050_inventories.csv')
    with plt.rc_context({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False}):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), constrained_layout=True)
        ax = axes[0]
        ax.stackplot(histories.s, histories.wave_slice_energy, histories.thermal_slice_energy,
            histories.extra_field_slice_energy, labels=['Travelling energy', 'Heat and enclosure bound', 'Additional radial field'],
            colors=['#3674a3', '#d58d48', '#6b9c72'], alpha=.85)
        ax.set(xlabel='Service time s', ylabel='Added ADM slice energy', title='Selected shared-field delivery')
        ax.legend(loc='upper left', fontsize=8)
        ax = axes[1]
        ax.plot(data['x'], data['guide_flux'], label='Paired guide requirement', color='#3674a3')
        ax.plot(data['x'], data['rate_cap'], label='Available electric allocation', color='#d58d48')
        ax.plot(data['x'], data['shared_flux'], label='Smooth allocated field', color='#6b9c72')
        ax.fill_between(data['x'], data['shared_flux'], data['guide_flux'], alpha=.15, color='#3674a3')
        ax.set(xlabel='Rail coordinate x', ylabel='Radial flux-energy H', title='Existing support supplies most guide energy')
        ax.legend(fontsize=8)
        fig.savefig(OUTPUT/'shared_field_delivery.png', dpi=160)
        fig.savefig(OUTPUT/'shared_field_delivery.pdf')
        plt.close(fig)
    checks = []
    for p in sorted((BASE/'poynting_delivery').glob('*/manifest.json')):
        if p.parent == OUTPUT:
            continue
        manifest = json.loads(p.read_text())
        for name, expected in manifest['output_sha256'].items():
            actual = sha256_file(p.parent/name)
            checks.append(dict(manifest=str(p.relative_to(ROOT)), kind='output', file=name, passed=actual==expected))
        for name, expected in manifest['input_sha256'].items():
            actual = sha256_file(ROOT/name)
            checks.append(dict(manifest=str(p.relative_to(ROOT)), kind='input', file=name, passed=actual==expected))
    if not all(row['passed'] for row in checks):
        raise RuntimeError('evidence hash failure')
    pd.DataFrame(checks).to_csv(OUTPUT/'hash_checks.csv', index=False)
    write_json(OUTPUT/'verification.json', dict(hash_checks=len(checks), failed_hash_checks=0,
        maximum_ray_quadrature_relative_change=max(row['ray_quadrature_relative_change'] for row in ray_rows),
        maximum_1024_FV_ray_difference=max(row['relative_FV_difference'] for row in ray_rows if row['cells']==1024)))
    sources = [Path(__file__), Path(__file__).with_name('run_poynting_delivery.py'),
        ROOT/'toolkit/adm_harness_cli/adm_harness/active_transfer_reservoir.py']
    sources += sorted((BASE/'poynting_delivery').glob('*/manifest.json'))
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        input_sha256={str(p.relative_to(ROOT)): sha256_file(p) for p in sources},
        output_sha256={p.name: sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))
    print('Independent ray and hash audit complete.', flush=True)


if __name__ == '__main__':
    main()
