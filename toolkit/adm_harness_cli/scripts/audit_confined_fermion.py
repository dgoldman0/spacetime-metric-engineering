#!/usr/bin/env python3
"""Independent controls and comparison tables for the occupied-state audit."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.integrate import cumulative_simpson, simpson, solve_bvp
from scipy.interpolate import PchipInterpolator

from adm_harness.confined_fermion import DiracMesh, MassWell, RailWell, occupied_tensor

ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT/'supporting_reports/data/archived_geometry_opening/reference_metric.npz'
ETA = 2.4127904527582454e-5


def published_negative_control(spacing):
    """Weinbaum eq. (112), with u=x/300 and tau=300t; mass stays one.

    Reported ANEC restores the paper's angular-average and affine-time
    normalization from our filled |K|=1 multiplet.
    """
    u = np.linspace(-48., 48., 196609)
    lapse = 1-.8*np.exp(-u*u)
    original_z = cumulative_simpson(1/lapse**2, x=u, initial=0)
    original_z -= np.interp(0, u, original_z)
    inverse = PchipInterpolator(original_z, u)
    z = np.linspace(original_z[0], original_z[-1],
                    int(np.ceil(np.ptp(original_z)/spacing))+1)

    def fields(points):
        x = inverse(points)
        a = 1-.8*np.exp(-x*x)
        r = 1/(1/np.sqrt(x*x+1)+300*a*np.exp(-(900*x)**2))
        return a, r

    a, r = fields(z)
    af, rf = fields((z[1:]+z[:-1])/2)
    modes = DiracMesh(z, a, af, af/rf).roots(.45)
    if len(modes) != 1:
        raise RuntimeError('published control requires its isolated sub-.45 mode')
    mode = modes[0]
    tensor, _ = occupied_tensor(dict(lapse=a, radius=r, mass=np.ones_like(z)), mode, 1)
    anec = float(simpson(tensor[0]+tensor[1], x=z))*2*np.pi/300
    omega = mode['frequency']*300
    if abs(omega-111.88) > .02 or abs(anec+3.59) > .02:
        raise RuntimeError('published negative-ANEC control failed')
    return dict(spacing=spacing, points=len(z), published_frequency_units=omega,
                published_anec_units=anec, minimum_radial_null=float((tensor[0]+tensor[1]).min()))


def collocation_control():
    """Full first-order Dirac + norm BVP, independent of the Schur discretization."""
    background = RailWell(CACHE, MassWell(), tail_extent=32.)
    low, high = background.z_bounds
    z = np.linspace(low, high, int(np.ceil((high-low)*256))+1)
    fields = background.optical_fields(z, 1.)
    faces = background.optical_fields((z[1:]+z[:-1])/2, 1.)
    mode = DiracMesh(z, fields['M'], faces['M'], faces['w']).roots(.9*12/6.8)[0]
    norm = cumulative_simpson(mode['f']**2+mode['g']**2, x=z, initial=0)
    norm /= norm[-1]
    # Include the initially resolved mode shape without retaining every point.
    indexes = np.unique(np.r_[np.arange(0, len(z), 8), len(z)-1])
    guess = np.array([mode['f'], mode['g'], norm])[:, indexes]

    def rhs(points, values, frequency):
        f, g, number = values
        sample = background.optical_fields(points, 1.)
        M, W = sample['M'], sample['w']
        omega = frequency[0]
        return np.array([W*f-(omega+M)*g, (omega-M)*f-W*g, f*f+g*g])

    def bc(left, right, frequency):
        return np.array([left[0], right[0], left[2], right[2]-1])

    result = solve_bvp(rhs, bc, z[indexes], guess, p=[mode['frequency']],
                       tol=1e-7, max_nodes=20000)
    if not result.success:
        raise RuntimeError('independent Dirac collocation failed: '+result.message)
    f, g, number = result.sol(z)
    tensor, scalar = occupied_tensor(fields, dict(f=f, g=g, frequency=float(result.p[0])), 1, ETA)
    b = float(-4*np.pi*simpson(fields['radius']*(tensor[0]+tensor[1]), x=z))
    schur_tensor, _ = occupied_tensor(fields, mode, 1, ETA)
    bs = float(-4*np.pi*simpson(fields['radius']*(schur_tensor[0]+schur_tensor[1]), x=z))
    return dict(solver_success=True, nodes=len(result.x), collocation_frequency=float(result.p[0]),
                schur_frequency=mode['frequency'], frequency_relative_difference=abs(result.p[0]/mode['frequency']-1),
                maximum_solver_residual=float(result.rms_residuals.max()),
                collocation_opening=b, schur_opening=bs,
                opening_relative_difference=abs(b/bs-1), norm=float(simpson(f*f+g*g, x=z)))


def compare(first, second):
    rows = {}
    for label in first['cases'].keys() & second['cases'].keys():
        a, b = first['cases'][label], second['cases'][label]
        ma = {(m['angular'], m['radial_index']): m for m in a['modes']}
        mb = {(m['angular'], m['radial_index']): m for m in b['modes']}
        common = ma.keys() & mb.keys()
        rows[label] = dict(same_modes=ma.keys() == mb.keys(), modes_compared=len(common),
            max_frequency_relative_change=max((abs(ma[k]['frequency']/mb[k]['frequency']-1) for k in common), default=0),
            max_opening_relative_change=max((abs(ma[k]['opening']/mb[k]['opening']-1) for k in common), default=0),
            angular_bound_relative_change=abs(a['sampled_angular_bound']/b['sampled_angular_bound']-1),
            ward_residual_first=a['maximum_ward_relative_l1'], ward_residual_second=b['maximum_ward_relative_l1'],
            positive_opening_modes_first=a['positive_opening_states'], positive_opening_modes_second=b['positive_opening_states'])
    return rows


def spatial_read(directory):
    source = json.loads((directory/'summary.json').read_text())
    output = {}
    native = RailWell(CACHE, MassWell(), tail_extent=64.)
    for label, row in source['cases'].items():
        with np.load(directory/f'{label}_occupied_profiles.npz') as data:
            x, values = data['coordinate'], data['tensor_and_scalar']
        r, a, b, *_ = native.metric(x)
        modes = row['modes']
        fractions, peaks = [], []
        mask = abs(x) <= 2
        for mode, profile in zip(modes, values):
            s = profile[0]*(4*np.pi*a*a*r*r)/(ETA*2*abs(mode['angular'])*mode['frequency'])
            fractions.append(float(simpson(s[mask]*b[mask]/a[mask], x=x[mask])))
            peaks.append(float(x[np.argmax(s)]))
        output[label] = dict(maximum_core_probability_from_saved_probes=max(fractions, default=0),
            minimum_abs_probability_peak_coordinate=min(map(abs, peaks), default=0),
            maximum_abs_probability_peak_coordinate=max(map(abs, peaks), default=0),
            probe_points=len(x), core_coordinate_extent=2.)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT/'supporting_reports/data/confined_fermion')
    parser.add_argument('--reuse-controls', action='store_true')
    args = parser.parse_args()
    output = args.root/'audit'
    output.mkdir(exist_ok=True)
    if args.reuse_controls:
        prior = json.loads((output/'audit.json').read_text())
        module = ROOT/'toolkit/adm_harness_cli/adm_harness/confined_fermion.py'
        if prior['source_hashes'][str(module.relative_to(ROOT))] != hashlib.sha256(module.read_bytes()).hexdigest():
            raise RuntimeError('rerun independent controls after a model-code change')
        result = {key: prior[key] for key in ('published_control', 'independent_collocation')}
        result['control_source_hashes'] = prior.get('control_source_hashes', {
            key: value for key, value in prior['source_hashes'].items() if key.endswith('.py')})
    else:
        result = dict(published_control=[published_negative_control(h) for h in (1/128, 1/256, 1/512)],
                      independent_collocation=collocation_control())
    runs = {p.name: json.loads((p/'summary.json').read_text()) for p in args.root.iterdir()
            if p.is_dir() and (p/'summary.json').exists()}
    comparisons = {}
    for first, second in [('initial', 'refined'), ('higher_ceiling', 'far_boundary'),
                          ('complete_band', 'complete_band_far')]:
        if first in runs and second in runs:
            comparisons[f'{first}_to_{second}'] = compare(runs[first], runs[second])
    result['comparisons'] = comparisons
    result['spatial_read'] = spatial_read(args.root/'refined')
    paths = [Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/confined_fermion.py']
    paths += [args.root/name/'summary.json' for name in runs]
    result['source_hashes'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (output/'audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
