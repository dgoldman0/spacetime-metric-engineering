#!/usr/bin/env python3
"""Rebuild quantum-wall energies and operators independently from retained states."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import multiprocessing
from pathlib import Path
import time

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]


def audit_case(task):
    row, output = task
    output = Path(output)
    data = np.load(output/f'{row["case"]}_final.npz')
    history = pd.read_csv(output/f'{row["case"]}_history.csv', float_precision='round_trip')
    final, initial = history.iloc[-1], history.iloc[0]
    m, length, width, strength = int(row['harmonics']), 12., .16, 8.
    # Direct real-space quadrature, independent of the evolution's analytic
    # complex Fourier convolution for its potential matrices.
    z = np.linspace(-length/2, length/2, 4096, endpoint=False)
    basis = np.ones((len(z), 2*m+1))/np.sqrt(length)
    waves = np.zeros(2*m+1)
    for j in range(1, m+1):
        basis[:, 2*j-1] = np.sqrt(2/length)*np.cos(2*np.pi*j*z/length)
        basis[:, 2*j] = np.sqrt(2/length)*np.sin(2*np.pi*j*z/length)
        waves[2*j-1:2*j+1] = 2*np.pi*j/length

    def potential(a, derivative=False):
        v = np.zeros(len(z))
        for sign in [-1, 1]:
            for image in [-1, 0, 1]:
                delta = z-sign*a/2-image*length
                wall = strength/(np.sqrt(2*np.pi)*width)*np.exp(-.5*(delta/width)**2)
                v += wall*(sign*delta/(2*width**2) if derivative else 1.)
        return basis.T@(v[:, None]*basis)*(length/len(z))

    free = np.diag(waves**2)
    vi, vf, derivative = potential(1.), potential(final.separation), potential(final.separation, True)
    operator_error = max(abs(data['free']-free).max(), abs(data['initial_operator']-free-vi).max(),
                         abs(data['final_operator']-free-vf).max(), abs(data['final_derivative']-derivative).max())
    k, w = data['transverse'], data['weights']
    values, vectors = np.linalg.eigh(free+vi)
    frequencies = np.sqrt(values[None, :]+k[:, None]**2)
    fi = vectors[None, :, :]/np.sqrt(2*frequencies[:, None, :])
    pi = -1j*vectors[None, :, :]*np.sqrt(frequencies[:, None, :]/2)
    f, p = data['f'], data['p']
    free_ground = .5*w@np.sqrt(waves[None, :]**2+k[:, None]**2).sum(axis=1)
    moving_mass = 2*row['wall_mass']+row['holding_mass']/3

    def energies(q, qp, a, momentum, v):
        quantum_free = .5*w@np.sum(abs(qp)**2+(waves[None, :, None]**2+k[:, None, None]**2)*abs(q)**2, axis=(1, 2))
        interaction = .5*w@np.einsum('kij,kij->k', q.conj(), v@q).real
        boundary = np.sqrt((moving_mass+interaction)**2+4*momentum**2)
        spring = .5*row['stiffness']*(a-row['natural_separation'])**2
        complete = quantum_free+boundary+spring+2*row['holding_mass']/3-free_ground
        return float(complete), float(quantum_free+interaction-free_ground), float(interaction), float(boundary)

    ei, efi, ui, bi = energies(fi, pi, 1., initial.separation_momentum, vi)
    ef, eff, uf, bf = energies(f, p, final.separation, final.separation_momentum, vf)
    chi = (moving_mass+uf)/bf
    force = -.5*chi*w@np.einsum('kij,kij->k', f.conj(), derivative@f).real
    omega2 = np.linalg.eigvalsh(free+chi*vf)[None, :]+k[:, None]**2
    excitation = eff+(chi-1)*uf+free_ground-.5*w@np.sqrt(omega2).sum(axis=1)
    dagger = lambda matrix: np.swapaxes(matrix.conj(), -1, -2)
    wronskian = max(abs(dagger(f)@p-dagger(p)@f+1j*np.eye(2*m+1)).max(),
                    abs(np.swapaxes(f, -1, -2)@p-np.swapaxes(p, -1, -2)@f).max())
    # Reconstruct the final spatial profile directly from the retained modes.
    profiles = pd.read_csv(output/f'{row["case"]}_profiles.csv.gz', float_precision='round_trip')
    profile = profiles[profiles.time.eq(final.time)]
    position = profile.z.to_numpy()
    b = np.ones((len(position), 2*m+1))/np.sqrt(length)
    db = np.zeros_like(b)
    for j in range(1, m+1):
        angle = 2*np.pi*j*position/length
        b[:, 2*j-1], b[:, 2*j] = np.sqrt(2/length)*np.cos(angle), np.sqrt(2/length)*np.sin(angle)
        db[:, 2*j-1], db[:, 2*j] = -waves[2*j]*b[:, 2*j], waves[2*j]*b[:, 2*j-1]
    free_omega = np.sqrt(waves[None, :]**2+k[:, None]**2)
    f0 = np.eye(2*m+1)[None, :, :]/np.sqrt(2*free_omega[:, None, :])
    p0 = -1j*np.eye(2*m+1)[None, :, :]*np.sqrt(free_omega[:, None, :]/2)
    def local(q, qp, coupling):
        qz, qtz, qzz = b@q, b@qp, db@q
        phi2 = np.einsum('k,kzi->z', w, abs(qz)**2)
        a = np.einsum('k,kzi->z', w, abs(qtz)**2)
        normal = np.einsum('k,kzi->z', w, abs(qzz)**2)
        transverse = np.einsum('k,kzi->z', w*k*k, abs(qz)**2)
        v = coupling*sum(strength/(np.sqrt(2*np.pi)*width)*np.exp(-.5*((position-sign*final.separation/2-image*length)/width)**2)
                        for sign in [-1, 1] for image in [-1, 0, 1])
        current = -np.einsum('k,kzi,kzi->z', w, qtz.conj(), qzz).real
        return np.stack([.5*(a+normal+transverse+v*phi2), current,
                         .5*(a+normal-transverse-v*phi2), .5*(a-normal-v*phi2)], axis=-1)
    reconstructed = local(f, p, chi)-local(f0, p0, 0.)
    profile_error = abs(reconstructed-profile[['energy', 'current', 'radial', 'angular']].to_numpy()).max()
    balance = max(abs(ef-ei), abs(history.energy_balance_error).max())
    scalar_error = max(abs(ef-final.complete_regulated_energy), abs(eff-final.free_subtracted_field_energy),
        abs(force-final.quantum_force), abs(excitation-final.excitation_above_instantaneous_ground),
        abs(4*final.separation_momentum/bf-final.separation_velocity))
    passed = bool(operator_error < 1e-10 and balance < 2e-7 and scalar_error < 1e-8
                  and wronskian < 1e-9 and profile_error < 1e-8 and omega2.min() > 0
                  and ef > 0 and excitation > -1e-8)
    return {'case': row['case'], 'operator_quadrature_error': operator_error,
        'energy_balance_error': balance, 'saved_scalar_error': scalar_error,
        'quantum_normalization_error': wronskian, 'profile_error': profile_error,
        'min_final_frequency_squared': omega2.min(), 'complete_energy': ef,
        'final_excitation': excitation, 'passed': passed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/quantum_boundary')
    args = parser.parse_args()
    started = time.monotonic()
    manifest = json.loads((args.output/'manifest.json').read_text())
    sources_match = all(hashlib.sha256((ROOT/key).read_bytes()).hexdigest() == value
                        for key, value in manifest['source_hashes'].items())
    summaries = pd.read_csv(args.output/'summaries.csv', float_precision='round_trip')
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        checks = pd.DataFrame(pool.map(audit_case, [(row, str(args.output)) for row in summaries.to_dict('records')]))
    checks.to_csv(args.output/'independent_checks.csv', index=False)
    refinement = []
    for scenario in ['released', 'moving_held']:
        subset = summaries[summaries.scenario.eq(scenario) & summaries.harmonics.eq(24)].sort_values('step', ascending=False)
        for key in ['final_separation', 'final_velocity']:
            values = subset[key].to_numpy()
            coarse, fine = abs(values[0]-values[1]), abs(values[1]-values[2])
            refinement.append({'scenario': scenario, 'quantity': key, 'coarse_difference': coarse,
                               'fine_difference': fine, 'ratio': coarse/fine})
    pd.DataFrame(refinement).to_csv(args.output/'temporal_refinement.csv', index=False)
    result = {'elapsed_seconds': time.monotonic()-started, 'workers': args.workers,
        'sources_match': sources_match, 'cases_checked': len(checks), 'all_passed': bool(checks.passed.all() and sources_match),
        'max_operator_error': float(checks.operator_quadrature_error.max()),
        'max_energy_balance_error': float(checks.energy_balance_error.max()),
        'max_saved_scalar_error': float(checks.saved_scalar_error.max()),
        'max_quantum_normalization_error': float(checks.quantum_normalization_error.max()),
        'max_spatial_profile_error': float(checks.profile_error.max()),
        'minimum_temporal_refinement_ratio': float(min(r['ratio'] for r in refinement)),
        'audit_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'method': 'Real-space barrier quadrature; raw-mode Hamiltonian, commutators and scalar stress; matched-bandwidth time-step comparisons.'}
    (args.output/'audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    if not result['all_passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
