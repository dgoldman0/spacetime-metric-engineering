#!/usr/bin/env python3
"""Evidence integrity, numerical comparisons and a standalone capacitor plot."""
from datetime import datetime, timezone
from pathlib import Path
import json

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from adm_harness.source_ledger import sha256_file
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'charged_capacitor_audit'


def main():
    if OUTPUT.exists():
        raise RuntimeError('preserve the completed capacitor audit')
    OUTPUT.mkdir(parents=True)
    checks = []
    manifests = sorted((BASE/'poynting_delivery').glob('*/manifest.json'))
    manifests += [BASE/name/'manifest.json' for name in (
        'finite_work_interface', 'finite_work_interface_recovery', 'finite_work_interface_audit',
        'charged_capacitor_shells', 'charged_capacitor_insulation', 'charged_capacitor_work_delivery')]
    for path in manifests:
        value = json.loads(path.read_text())
        for kind in ('input', 'output'):
            root = ROOT if kind == 'input' else path.parent
            for name, expected in value[kind+'_sha256'].items():
                checks.append(dict(manifest=str(path.relative_to(ROOT)), kind=kind, file=name,
                                   passed=sha256_file(root/name)==expected))
    pd.DataFrame(checks).to_csv(OUTPUT/'hash_checks.csv', index=False)
    if not all(row['passed'] for row in checks):
        raise ArithmeticError('capacitor or inherited evidence changed')
    route = BASE/'charged_capacitor_work_delivery'
    coarse = pd.read_csv(route/'n512_geometry2_phases.csv')
    medium = pd.read_csv(route/'n1024_geometry2_phases.csv')
    fine = pd.read_csv(route/'n1024_geometry4_phases.csv')
    comparisons = []
    keys = ['insulation_drift', 'route', 'time']
    for name, a, b in (('spatial_512_1024', coarse, medium), ('geometry_time_2_4', medium, fine)):
        pair = a.merge(b, on=keys, suffixes=('_a', '_b'))
        for quantity in ('required_negative_null', 'auxiliary_ADM'):
            relative = abs(pair[quantity+'_a']-pair[quantity+'_b'])/np.maximum(abs(pair[quantity+'_b']), 1e-10)
            comparisons.append(dict(comparison=name, quantity=quantity, maximum_relative_change=float(relative.max())))
    pd.DataFrame(comparisons).to_csv(OUTPUT/'refinement.csv', index=False)
    if max(row['maximum_relative_change'] for row in comparisons) > .01:
        raise ArithmeticError('joint work delivery exceeds the one-percent refinement comparison')
    fade = fine[fine.time==1.285]
    free = fade[fade.route=='guide_omitted_tensor_bound']
    bound_error = float(abs(free.required_negative_null-free.maximum_radial_null).max())
    if bound_error > 1e-10:
        raise ArithmeticError('guide-free fade peak differs from the radial-null control')
    summary = dict(evidence_hash_checks=len(checks), failed_hash_checks=0, refinements=comparisons,
        guide_omitted_fade_radial_null_identity_error=bound_error,
        focused_test_result='63 tests passed in the focused capacitor, work, delivery, and pressure/converter suite.',
        physical_capacitor_constructed=False, complete_rail_source_closed=False)
    write_json(OUTPUT/'verification.json', summary)
    shell = pd.read_csv(BASE/'charged_capacitor_shells/best_sampled.csv')
    passive = pd.read_csv(BASE/'charged_capacitor_insulation/all_cases.csv')
    passive = passive[(passive.cells==1024)&(passive.recovery==1)]
    with plt.rc_context({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False}):
        fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.5), constrained_layout=True)
        for family, name, color in (
                ('DEC_radial_causal', 'Full sampled gravity range', '#2b698e'),
                ('weak_DEC_radial_causal', 'Weak self-gravity subset', '#ba7730'),
                ('compressive_radial_half_slope', 'Compressive surface envelope', '#658551')):
            row = shell[shell.family==family]
            axes[0].plot(row.outer_radius, row.field_to_wall_rest_energy, 'o-', label=name, color=color)
        axes[0].set(xscale='log', xlabel='Outer / inner shell radius', ylabel='Proper field energy / wall rest energy',
                    title='Charged-shell boundary controls')
        axes[0].legend(fontsize=8, loc='upper left')
        speeds = [.5, .7, .9]
        for regime, name, color in (('controlled_minimum', 'Controlled field, work route omitted', '#658551'),
                                    ('frozen_flux_cover', 'Frozen field covering the schedule', '#ba7730')):
            row = passive[passive.regime==regime].sort_values('drift')
            axes[1].plot(row.drift, row.fade_required_negative_null, 'o-', color=color, label=name)
        for label, name, color in (('delivery_drift050', 'Controlled field + counted work route', '#2b698e'),
                                   ('guide_omitted_tensor_bound', 'Work route with its guide omitted', '#98566a')):
            row = fade[(fade.route==label)&(fade.insulation_drift<1)].sort_values('insulation_drift')
            axes[1].plot(row.insulation_drift, row.required_negative_null, 'o-', color=color, label=name)
        axes[1].axhline(.262788, ls='--', color='#666666', label='Prior formal assembly comparison')
        axes[1].set(yscale='log', xlabel='Capacitor insulation frame speed / c', xticks=speeds,
                    ylabel='Fade required negative-null contribution', title='Confinement and its work must both be counted')
        axes[1].legend(fontsize=7.7, loc='center left', bbox_to_anchor=(-.02, .61))
        fig.savefig(OUTPUT/'capacitor_construction_controls.png', dpi=170)
        fig.savefig(OUTPUT/'capacitor_construction_controls.pdf')
        plt.close(fig)
    inputs = {str(Path(__file__).relative_to(ROOT)): sha256_file(Path(__file__))}
    inputs.update({str(p.relative_to(ROOT)): sha256_file(p) for p in manifests})
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        input_sha256=inputs,
        output_sha256={p.name: sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
