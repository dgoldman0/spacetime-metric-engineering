#!/usr/bin/env python3
"""Numeric comparison, exact-geometry witnesses, integrity, and figure only."""
from pathlib import Path
import hashlib
import json
import subprocess

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from adm_harness.active_transfer_reservoir import MetricJets, TabulatedActiveMedium
from adm_harness.graded_electrothermal import fixed_kinematics, maximum_null
from adm_harness.metric_regularity import regularized_scalars
from adm_harness.local_pressure_coupling import pressure_contact_slice
from adm_harness.source_ledger import SourceParams, sha256_file
from run_active_transfer_reservoir import parameters

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/'supporting_reports/data/graded_electrothermal'
DERIVED = BASE/'derived'


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def check_manifest(directory, revision):
    manifest = json.loads((directory/'manifest.json').read_text())
    failures, count = [], 0
    for name, expected in manifest['output_sha256'].items():
        count += 1
        if sha256_file(directory/name) != expected:
            failures.append(name)
    for name, expected in manifest['software_and_input_sha256'].items():
        count += 1
        if sha256_file(ROOT/name) == expected:
            continue
        historical = subprocess.run(['git', 'show', revision+':'+name], cwd=ROOT,
                                    capture_output=True, check=True).stdout
        if hashlib.sha256(historical).hexdigest() != expected:
            failures.append(name)
    return dict(revision=revision, checked=count, failures=failures)


def exact_witness(witness, params, step):
    t, x = witness['s'], witness['l']
    def values(t, x):
        g = regularized_scalars(t, x, params)
        return np.array([g['alpha'], g['beta'], np.sqrt(g['gamma_ll']), np.sqrt(g['gamma_omega'])])
    a, beta, b, r = values(t, x)
    dt = (values(t+step, x)-values(t-step, x))/(2*step)
    dx = (values(t, x+step)-values(t, x-step))/(2*step)
    jets = MetricJets(a, beta, b, r, dx[0], dx[1], dt[2]/b, dx[2]/b, dt[3]/r, dx[3]/r)
    _, _, _, acceleration, gradient = fixed_kinematics(jets, dt[0], dt[1])
    return dict(step=step, acceleration=float(acceleration), twice_abs_angular_gradient=float(2*abs(gradient)),
                allowed_force_per_density_low=float(acceleration-2*abs(gradient)),
                allowed_force_per_density_high=float(acceleration+2*abs(gradient)))


def pressure_comparison(interior):
    background = ROOT/'supporting_reports/data/active_transfer_reservoir'
    model = TabulatedActiveMedium(background/'metric_fine.npz', background/'medium_baseline.npz')
    rows, phases, profile_rows = [], [], []
    for case in ('smooth_joint_refined', 'smooth_reset'):
        summary = json.loads((interior/(case+'_summary.json')).read_text())
        if not summary['success']:
            continue
        points = pd.read_csv(interior/(case+'_points.csv'))
        with np.load(interior/(case+'_states.npz')) as states:
            times, amplitude = states['t'], states['contact_amplitudes']
        for time, group in points.groupby('s'):
            index = int(np.argmin(abs(times-time)))
            extra = np.zeros((4, len(group)))
            extra_energy = 0.
            for k, center in enumerate(summary['ports']):
                value = pressure_contact_slice(model, float(time), center, .1, float(amplitude[index, k]))
                coarse = pressure_contact_slice(model, float(time), center, .1, float(amplitude[index, k]), nodes=129)
                rows.append(dict(case=case, s=time, center=center, applied_contact_force=float(amplitude[index, k]),
                    loaded_end_pressure=value['loaded_end_pressure'], coupling_slice_energy=value['slice_energy'],
                    peak_coupling_supplied_null=value['peak_supplied_null'],
                    rest_heat_integral=value['heat_exchange_integral'],
                    maximum_abs_rest_heat_density=float(abs(value['required_rest_heat']).max()),
                    loaded_end_pressure_refinement_difference=abs(value['loaded_end_pressure']-coarse['loaded_end_pressure']),
                    density_ratio=3., sound_speed_squared=1/3))
                inside = abs(group.l.to_numpy()-center) <= .05+1e-12
                for channel in range(4):
                    extra[channel, inside] += np.interp(group.l.to_numpy()[inside], value['x'], value['moments'][channel])
                extra_energy += value['slice_energy']
                for j in range(len(value['x'])):
                    profile_rows.append(dict(case=case, s=time, center=center, l=value['x'][j],
                        pressure=value['pressure'][j], pressure_x=value['pressure_x'][j],
                        required_rest_force=value['required_rest_force'][j], required_rest_heat=value['required_rest_heat'][j]))
            keys = ('rho', 'p_r', 'j', 'p_t')
            excess = np.array([group['reservoir_'+key]+group['endpoint_'+key]-group['geometry_'+key] for key in keys])+extra
            phases.append(dict(case=case, s=time, added_coupling_slice_energy=extra_energy,
                partial_assembly_required_negative_null_peak=float(maximum_null(excess)[0].max()),
                scope='instantaneous rho=3p couplings with explicit loaded-end pressure and thermal ports; walls and transmission beyond the contact bands remain additional'))
    pd.DataFrame(rows).to_csv(DERIVED/'pressure_coupling_requirements.csv', index=False)
    pd.DataFrame(phases).to_csv(DERIVED/'pressure_coupling_source_requirements.csv', index=False)
    pd.DataFrame(profile_rows).to_csv(DERIVED/'pressure_coupling_profiles.csv', index=False)


def main():
    DERIVED.mkdir(parents=True, exist_ok=True)
    interior = BASE/'finite_contacts/interior_solver'
    interior_revision = json.loads((interior/'manifest.json').read_text())['git_revision']
    integrity = {'initial': check_manifest(BASE, '0448351'),
                 'finite': check_manifest(BASE/'finite_contacts', '16e7cd3'),
                 'interior': check_manifest(interior, interior_revision)}
    if any(value['failures'] for value in integrity.values()):
        raise RuntimeError('evidence integrity failed')
    rows, phases, witnesses = [], [], []
    params = SourceParams(**parameters())
    for suite, directory in (('relaxed', BASE), ('finite', BASE/'finite_contacts'), ('interior', interior)):
        for path in sorted(directory.glob('*_summary.json')):
            summary = json.loads(path.read_text())
            row = dict(suite=suite, case=summary['case'], success=summary['success'])
            if not summary['success']:
                row['message'] = summary['message']; rows.append(row); continue
            for key in ('cells', 'duration', 'initial_slice_energy', 'maximum_slice_energy', 'final_slice_energy',
                        'maximum_supplied_null', 'maximum_abs_velocity', 'minimum_heat', 'maximum_heat',
                        'maximum_collared_normal_force_density', 'maximum_abs_integrated_collar_force',
                        'maximum_effective_discharge_conductivity', 'hoop_force_cone_failures',
                        'secondary_energy_optimization_used', 'normalized_equality_residual', 'raw_equality_residual',
                        'primary_dual_gap', 'inequality_violation'):
                row[key] = summary.get(key)
            row.update(summary['independent_checks'])
            rows.append(row)
            for phase in summary['phases']:
                phases.append(dict(suite=suite, case=summary['case'], **phase))
            for witness in summary['hoop_witnesses']:
                for step in (1e-4, 5e-5):
                    witnesses.append(dict(suite=suite, case=summary['case'], **witness, **{'exact_'+key: value
                        for key, value in exact_witness(witness, params, step).items()}))
    frame, pf = pd.DataFrame(rows), pd.DataFrame(phases)
    frame.to_csv(DERIVED/'assembly_comparison.csv', index=False)
    pf.to_csv(DERIVED/'phase_comparison.csv', index=False)
    pd.DataFrame(witnesses).to_csv(DERIVED/'exact_geometry_contact_witnesses.csv', index=False)

    # Same angular maximization for the archived freely evolved backbone.
    old = pd.read_csv(ROOT/'supporting_reports/data/reservoir_feasibility/equilibrated_n128_points.csv')
    old_rows = []
    keys = ('rho', 'p_l', 'j_l', 'p_omega')
    for phase, group in old.groupby('s'):
        excess = np.array([group['reservoir_'+k]+group['endpoint_'+k]-group['geometry_'+k] for k in keys])
        old_rows.append(dict(case='prestressed_n128', s=phase, required_negative_null_peak=float(maximum_null(excess)[0].max())))
    pd.DataFrame(old_rows).to_csv(DERIVED/'prestressed_angular_comparison.csv', index=False)
    pressure_comparison(interior)

    selected = ['continuous_recheck', 'smooth_n32', 'smooth_n64', 'smooth_time_refined', 'smooth_space_refined', 'smooth_joint_refined', 'smooth_fast_discharge']
    available = frame[frame.case.isin(selected) & frame.success & (frame.suite == 'interior')].copy()
    available = available.set_index('case').loc[[key for key in selected if key in available.case.to_list()]].reset_index()
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.7), layout='constrained')
    labels = {'continuous_recheck': 'Continuous field', 'smooth_n32': 'Smooth contacts / 32',
              'smooth_n64': 'Smooth contacts / 64', 'smooth_time_refined': 'Finer time / 64',
              'smooth_space_refined': 'Finer space / 128', 'smooth_joint_refined': 'Finer space + time / 128',
              'smooth_fast_discharge': 'Faster response / 64'}
    for axis, column, title in ((axes[0], 'initial_slice_energy', 'Initial local slice energy'),
                                (axes[1], 'maximum_supplied_null', 'Peak supplied null stress')):
        for optimized, color, marker, label in ((True, '#277b92', 'o', 'Energy tie-break completed'),
                                                (False, '#b2672a', 's', 'Primary solution retained')):
            use = available.secondary_energy_optimization_used == optimized
            axis.scatter(available.loc[use, column], np.flatnonzero(use), color=color, marker=marker, label=label, s=45)
        axis.set_yticks(np.arange(len(available)), [labels[k] for k in available.case])
        axis.invert_yaxis()
        axis.set_xscale('log'); axis.set_title(title); axis.set_xlabel('Model units; field and buffers')
        axis.grid(axis='x', alpha=.2); axis.set_axisbelow(True)
    axes[0].legend(loc='lower right', fontsize=8)
    fig.suptitle('Active late-patch conservation screen through carrying-flow fade', fontsize=12)
    target = ROOT/'supporting_reports/figures/graded_electrothermal_comparison'
    target.parent.mkdir(parents=True, exist_ok=True)
    for extension in ('png', 'pdf'):
        fig.savefig(target.with_suffix('.'+extension), dpi=180)
    plt.close(fig)
    pressure = pd.read_csv(DERIVED/'pressure_coupling_profiles.csv')
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.9), layout='constrained')
    for axis, center in zip(axes, (-1.7, -1.3, -.9)):
        local = pressure[(pressure.case == 'smooth_joint_refined') & np.isclose(pressure.center, center)]
        for time, group in local.groupby('s'):
            axis.plot(group.l, group.pressure, label=f's={time:g}')
        axis.set_title(f'Contact centered at x={center:g}')
        axis.set_xlabel('Rail coordinate x'); axis.grid(alpha=.2)
    axes[0].set_ylabel('Fluid pressure, model units'); axes[-1].legend(fontsize=8)
    fig.suptitle('Instantaneous positive-pressure couplings (ρ=3p); loaded ends remain transmission ports', fontsize=11)
    pressure_target = target.with_name('graded_pressure_couplings')
    for extension in ('png', 'pdf'):
        fig.savefig(pressure_target.with_suffix('.'+extension), dpi=180)
    plt.close(fig)
    integrity['postprocessor_sha256'] = sha256_file(Path(__file__))
    integrity['pressure_kernel_sha256'] = sha256_file(ROOT/'toolkit/adm_harness_cli/adm_harness/local_pressure_coupling.py')
    integrity['derived_sha256'] = {p.name: sha256_file(p) for p in sorted(DERIVED.glob('*.csv'))}
    integrity['figure_sha256'] = {str(target.with_suffix('.'+ext).relative_to(ROOT)): sha256_file(target.with_suffix('.'+ext))
                                  for ext in ('png', 'pdf')}
    integrity['figure_sha256'].update({str(pressure_target.with_suffix('.'+ext).relative_to(ROOT)): sha256_file(pressure_target.with_suffix('.'+ext))
                                      for ext in ('png', 'pdf')})
    write_json(DERIVED/'integrity.json', integrity)
    print(frame.to_string(index=False, columns=['case', 'success', 'initial_slice_energy', 'maximum_supplied_null',
                                               'maximum_collared_normal_force_density', 'hoop_force_cone_failures']))


if __name__ == '__main__':
    main()
