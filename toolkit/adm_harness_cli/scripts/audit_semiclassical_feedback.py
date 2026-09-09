#!/usr/bin/env python3
"""Numerical evidence audit and scientific figure for the bounded joint round."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import subprocess
import platform

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.integrate import simpson
from scipy.interpolate import PchipInterpolator, PPoly
from scipy.linalg import eigh_tridiagonal

from adm_harness.condensate_vacuum import JoinedProfile
from adm_harness.semiclassical_joint import SmoothJointSeed
from adm_harness.semiclassical_material import UpdatedMaterialSeed
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
HISTORY = ('d4512da', 'b040b9b', '868b938', 'b040588')


def source_version(name, expected):
    path = Path(name)
    path = path if path.is_absolute() else ROOT/path
    if path.is_absolute() and not path.is_relative_to(ROOT) and ROOT.name in path.parts:
        # Archives remain verifiable after moving the checkout.
        index = max(i for i, part in enumerate(path.parts) if part == ROOT.name)
        path = ROOT.joinpath(*path.parts[index+1:])
    if path.exists() and sha256_file(path) == expected:
        return 'working tree'
    if path.is_relative_to(ROOT):
        rel = str(path.relative_to(ROOT))
        for revision in HISTORY:
            result = subprocess.run(['git', 'show', revision+':'+rel], cwd=ROOT,
                capture_output=True, check=False)
            if result.returncode == 0 and hashlib.sha256(result.stdout).hexdigest() == expected:
                return revision
    raise ValueError('unresolved source version: '+name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ROOT/'supporting_reports/data/semiclassical_joint')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = args.output or args.data/'audit'
    output.mkdir(parents=True, exist_ok=True)
    source_versions, manifests = {}, {}
    for path in sorted(args.data.glob('*/manifest.json')):
        manifest = json.loads(path.read_text())
        if 'output_hashes' not in manifest:
            continue
        for name, expected in manifest['output_hashes'].items():
            if sha256_file(path.parent/name) != expected:
                raise ValueError('changed output: '+str(path.parent/name))
        for name, expected in manifest['source_hashes'].items():
            key = name+' @ '+expected
            if key not in source_versions:
                source_versions[key] = source_version(name, expected)
        manifests[path.parent.name] = manifest
    material = json.loads((args.data/'material_update/checks.json').read_text())
    if sha256_file(args.data/'material_update/material.npz') != material['output_hashes']['material.npz']:
        raise ValueError('changed material archive')
    for name, expected in material['source_hashes'].items():
        source_versions[name+' @ '+expected] = source_version(name, expected)
    spec = importlib.util.spec_from_file_location('tail_audit', Path(__file__).with_name('summarize_semiclassical_controls.py'))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    local, fits = [], []
    for name in ('annulus_192', 'annulus_384', 'throat_control', 'ward_left', 'ward_right',
                 'material_ward_left', 'material_ward_center', 'material_ward_right'):
        _, rows, tails = module.read_run(args.data/name)
        local.append(rows); fits.extend(tails)
    local = pd.concat(local, ignore_index=True)
    local.to_csv(output/'local_source_controls.csv', index=False)
    pd.DataFrame(fits).to_csv(output/'angular_tail_controls.csv', index=False)
    profile = JoinedProfile(ROOT)
    seed = SmoothJointSeed(profile)
    center = float(seed.proper_of_coordinate(-4.))
    jets = seed.jets(center)
    ward = []
    for scale in (4., 8.):
        rows = [local.query('run == @name and regulator == @scale').iloc[0]
                for name in ('ward_left', 'annulus_192', 'ward_right')]
        left, c, right = rows
        terms = np.array([(right.pr-left.pr)/.04, jets[1, 1]*(c.rho+c.pr),
            2*jets[1, 0]*(c.pr-c.pt), 1.4*profile.v**2*jets[0, 3]*jets[1, 3]*c.polarization])
        ward.append({'location': 'annulus', 'regulator': scale, 'pressure_derivative': terms[0],
            'lapse_term': terms[1], 'angular_term': terms[2], 'material_exchange': terms[3],
            'relative_residual': abs(terms.sum())/abs(terms).sum()})
    for scale in (4., 8.):
        left, c, right = [local.query('run == @name and regulator == @scale').iloc[0]
            for name in ('material_ward_left', 'material_ward_center', 'material_ward_right')]
        m = manifests['material_ward_center']
        terms = np.array([(right.pr-left.pr)/.04,
            m['log_lapse_gradient']*(c.rho+c.pr),
            2*m['log_radius_gradient']*(c.pr-c.pt),
            .5*m['mass_squared_gradient']*c.polarization])
        ward.append({'location': 'Higgs transition', 'regulator': scale,
            'pressure_derivative': terms[0], 'lapse_term': terms[1], 'angular_term': terms[2],
            'material_exchange': terms[3], 'relative_residual': abs(terms.sum())/abs(terms).sum()})
    pd.DataFrame(ward).to_csv(output/'ward_identity.csv', index=False)
    names = ['initial_profile', 'updated_192', 'updated_fine']
    tables = {name: pd.read_csv(args.data/name/'source_profile.csv') for name in names}
    with np.load(args.data/'material_update/material.npz') as saved:
        updated_seed = UpdatedMaterialSeed(seed, saved['proper'], saved['amplitudes'])
        material_solution = PPoly.construct_fast(saved['coefficients'].copy(), saved['knots'].copy(), axis=1)
    spectral = []
    for name, background in (('initial', seed), ('updated', updated_seed)):
        for spacing in (.04, .02, .01):
            ends = background.proper_of_coordinate(np.array([-48., 48.]))
            grid = np.linspace(*ends, int(np.ceil(np.diff(ends)[0]/spacing))+1)
            step = grid[1]-grid[0]
            jj = background.jets(grid[1:-1], 2)
            _, aa, vv = background.values(grid[1:-1])
            cc = jj[2, 0]+jj[1, 0]**2+jj[2, 1]/2+jj[1, 1]**2/4+jj[1, 1]*jj[1, 0]
            eigenvalues = eigh_tridiagonal(aa*aa*(2/step**2+vv+cc),
                -aa[1:]*aa[:-1]/step**2, select='i', select_range=(0, 1), eigvals_only=True, tol=1e-11)
            spectral.append({'background': name, 'spacing': step,
                'lowest_squared_frequency': eigenvalues[0], 'second_squared_frequency': eigenvalues[1],
                'lowest_frequency': np.sqrt(eigenvalues[0]), 'second_frequency': np.sqrt(eigenvalues[1])})
    pd.DataFrame(spectral).to_csv(output/'spectral_gap.csv', index=False)
    profile_ward = []
    for scale, data in tables['updated_fine'].groupby('regulator'):
        data = data.sort_values('proper')
        ll = data.proper.to_numpy()
        jj = updated_seed.jets(ll, 1)
        vh = 2*1.4*profile.v**2*jj[0, 3]*jj[1, 3]
        terms = np.zeros((len(ll)-4, 4))
        for i in range(2, len(ll)-2):
            offsets = ll[i-2:i+3]-ll[i]
            scale_l = max(abs(offsets))
            matrix = (offsets[None]/scale_l)**np.arange(5)[:, None]
            weights = np.linalg.solve(matrix, np.array([0., 1., 0., 0., 0.]))/scale_l
            c = data.iloc[i]
            terms[i-2] = [weights@data.pr.to_numpy()[i-2:i+3],
                jj[1, 1, i]*(c.rho+c.pr), 2*jj[1, 0, i]*(c.pr-c.pt),
                .5*c.polarization*vh[i]]
        magnitude = abs(terms).sum(axis=1)
        active = magnitude > 1e-4*magnitude.max()
        residual = abs(terms.sum(axis=1))
        for i, row in enumerate(terms):
            profile_ward.append({'regulator': scale, 'coordinate': data.coordinate.iloc[i+2],
                'pressure_derivative': row[0], 'lapse_term': row[1], 'angular_term': row[2],
                'material_exchange': row[3], 'active': bool(active[i]),
                'absolute_residual': residual[i], 'relative_residual': residual[i]/max(magnitude[i], 1e-30)})
    profile_ward = pd.DataFrame(profile_ward)
    profile_ward.to_csv(output/'profile_ward_identity.csv', index=False)
    balances = []
    for name in names:
        b = pd.read_csv(args.data/name/'opening_balance.csv'); b.insert(0, 'run', name)
        balances.append(b)
    balances = pd.concat(balances, ignore_index=True)
    balances.to_csv(output/'opening_comparisons.csv', index=False)
    low = max(t.proper.min() for t in tables.values())
    high = min(t.proper.max() for t in tables.values())
    l = np.linspace(low, high, 48001)
    r, a, _ = seed.values(l)
    profiles, tails = [], []
    for name in names:
        for _, data in tables[name].groupby('regulator'):
            profiles.append(PchipInterpolator(data.proper, data.radial_enthalpy)(l))
            tails.append(PchipInterpolator(data.proper, abs(data.radial_enthalpy_tail))(l))
    profiles, tails = np.array(profiles), np.array(tails)
    # Empirical envelope from the observed regulators, material change, and
    # spatial/mode refinements; this is not a rigorous continuum error bound.
    envelope = np.maximum(-profiles.min(axis=0), 0.)+np.ptp(profiles, axis=0)+tails.max(axis=0)
    envelope_balance = 4*np.pi*profile.eta*simpson(r/a*envelope, x=l)
    geometric = seed.demanded_tensor(l)
    demand = -4*np.pi*simpson(r/a*geometric[:2].sum(axis=0), x=l)
    original = tables['initial_profile'].query('regulator == 8')
    recalculated = tables['updated_fine'].query('regulator == 8')
    phi_old = PchipInterpolator(original.proper, original.polarization)(l)
    phi_new = PchipInterpolator(recalculated.proper, recalculated.polarization)(l)
    higgs = material_solution(l)[2]
    changed_material_force = 1.4*higgs*(phi_new-phi_old)/(2*profile.v)
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.1), constrained_layout=True)
    selected = tables['updated_fine'].query('regulator == 8').sort_values('coordinate')
    axes[0].plot(selected.coordinate, selected.required_radial_enthalpy, label='Geometry requires', color='#374151')
    axes[0].plot(selected.coordinate, profile.eta*selected.radial_enthalpy, label='Absolute scalar estimate', color='#2563eb')
    axes[0].set_yscale('symlog', linthresh=1e-10)
    axes[0].set(xlabel='Original rail coordinate', ylabel='Radial null stress (geometric units)', xlim=(-16, 10))
    axes[0].legend(frameon=False)
    labels = ['Required', 'Initial', 'Material updated', 'Refined', 'Measured envelope']
    values = [demand, *[float(balances.query('run == @name').maximum_quantum_opening_balance.max()) for name in names], envelope_balance]
    axes[1].bar(np.arange(len(values)), values, color=['#374151', '#93c5fd', '#60a5fa', '#2563eb', '#a78bfa'])
    axes[1].set_yscale('log')
    axes[1].set_xticks(np.arange(len(values)), labels, rotation=20, ha='right')
    axes[1].set(ylabel='Integrated opening balance', ylim=(1e-6, 5.))
    for ax in axes:
        ax.grid(axis='y', alpha=.18)
    fig.savefig(output/'joint_opening_balance.png', dpi=180)
    plt.close(fig)
    checks = {'source_versions': source_versions,
        'opening_required': demand, 'empirical_envelope_opening_balance': envelope_balance,
        'empirical_envelope_fraction': envelope_balance/demand,
        'twofold_weight_step_fraction_with_empirical_envelope': 2*envelope_balance/demand,
        'largest_local_ward_relative_residual': max(x['relative_residual'] for x in ward),
        'broad_profile_derivative_stencil_converged': False,
        'broad_profile_derivative_stencil_active_maximum': float(profile_ward.query('active').relative_residual.max()),
        'broad_profile_derivative_stencil_active_median': float(profile_ward.query('active').relative_residual.median()),
        'broad_profile_derivative_stencil_largest_absolute_residual': float(profile_ward.absolute_residual.max()),
        'material_equation_change_after_quantum_recalculation': float(abs(changed_material_force).max()),
        'lowest_updated_scalar_frequency': float(spectral[-1]['lowest_frequency']),
        'python_version': platform.python_version(), 'numpy_version': np.__version__,
        'retained_mode_seconds': sum(m['elapsed_seconds'] for m in manifests.values()),
        'largest_worker_rss_kib': max(m.get('worker_peak_rss_kib', 0) for m in manifests.values()),
        'material': {k: material[k] for k in ('target_matter_number', 'frequency', 'independent_equation_residual',
            'boundary_residual', 'maximum_field_change', 'accepted')},
        'source_sha256': sha256_file(Path(__file__)),
        'inputs': {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): sha256_file(p)
                   for p in args.data.glob('*/manifest.json') if p.parent != output},
        'output_hashes': {p.name: sha256_file(p) for p in output.iterdir() if p.name != 'audit.json'}}
    (output/'audit.json').write_text(json.dumps(checks, indent=2)+'\n')
    print(json.dumps({k: v for k, v in checks.items() if k not in ('source_versions', 'inputs', 'output_hashes')}, indent=2))


if __name__ == '__main__':
    main()
