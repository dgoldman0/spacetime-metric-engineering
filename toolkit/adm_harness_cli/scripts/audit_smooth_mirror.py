#!/usr/bin/env python3
"""Audit the smooth quantum benchmark and its leading material barrier."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import argparse
import json
import multiprocessing
from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

from adm_harness.smooth_mirror import fermi_surface_match, corrugation_energy
from adm_harness.smooth_mirror_material import (dirac_squared_levels, tree_level_match,
    optimal_zero_band_scale, zero_band_yukawa_threshold)
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]


def source_key(path):
    """Keep repository paths portable and permit external replay directories."""
    path = path.resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def spectrum(task):
    a, spacing = task
    zero, first = dirac_squared_levels(a, spacing)
    return {'localization': a, 'spacing': spacing, 'zero_eigenvalue': zero,
            'first_eigenvalue': first, 'exact_first_eigenvalue': 2*a-1,
            'maximum_error': max(abs(zero), abs(first-(2*a-1)))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--input', type=Path, default=ROOT/'supporting_reports/data/smooth_quantum_material')
    parser.add_argument('--output', type=Path, default=ROOT/'supporting_reports/data/smooth_quantum_material_audit')
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    started = time.monotonic()
    manifest = json.loads((args.input/'manifest.json').read_text())
    checks = {f'original_source:{path}': sha256_file(ROOT/path) == value
              for path, value in manifest['source_hashes'].items()}
    if not all(checks.values()):
        raise RuntimeError('original evidence source changed')
    sources = [Path(__file__).resolve(), ROOT/'toolkit/adm_harness_cli/adm_harness/smooth_mirror_material.py',
               *sorted(args.input.iterdir())]
    hashes = {source_key(p): sha256_file(p) for p in sources}
    q = pd.read_csv(args.input/'quadrature_convergence.csv', float_precision='round_trip')
    direct = pd.read_csv(args.input/'independent_quantum_checks.csv', float_precision='round_trip')
    checks['smooth_quantum_medium_fine_peak_error'] = bool(q[q.coarse_nodes == 512].peak_normalized_error.max() < 1e-8)
    checks['smooth_quantum_independent_integral'] = bool(direct.relative_error.max() < 1e-8)
    material = pd.read_csv(args.input/'fermi_junction_scan.csv.gz', float_precision='round_trip')
    checks['all_positive_energy_shells_compressed'] = bool((material.surface_pressure > 0).all())
    chosen = material.positive_components & (material.fermi_radial_frequency_squared > 0)
    checks['radial_survivors_fail_leading_shape_gate'] = bool(chosen.any() and (material.loc[chosen, 'normal_speed_squared'] < 0).all())
    m = fermi_surface_match(6.8, 1.5)
    tau, gas = float(m['wall_tension']), float(m['fermi_energy'])
    microscopic = []
    for width in [.025, .05, .1]:
        for flavors in [1, 4, 16, 64]:
            eta = optimal_zero_band_scale(width, gas, flavors)
            microscopic.append(tree_level_match(width, .1/width, tau, gas, eta, flavors))
    micro = pd.DataFrame(microscopic)
    checks['tree_matches_have_confined_zero_branch'] = bool(micro.only_zero_branch_filled.all())
    checks['tree_scalar_potential_bounded'] = bool((micro.quartic_determinant > 0).all())
    for key in ['tension_reconstruction_error', 'gas_reconstruction_error', 'optical_reconstruction_error']:
        checks[key] = bool(abs(micro[key]).max() < 1e-13)
    opt = minimize_scalar(lambda x: zero_band_yukawa_threshold(x, tau, gas),
                          bounds=(.01, 10), method='bounded')
    checks['independent_minimum_zero_band_yukawa'] = bool(abs(opt.x-np.sqrt(3)) < 1e-5)
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        spectra = pd.DataFrame(pool.map(spectrum, [(a, h) for a in [1.5, 2.1, 4.] for h in [.04, .02, .01]]))
    for a in [1.5, 2.1, 4.]:
        s = spectra[spectra.localization == a].set_index('spacing')
        checks[f'dirac_spectrum_convergence_{a}'] = bool(s.loc[.01, 'maximum_error'] < s.loc[.04, 'maximum_error']/15)
    # Direct shape-energy changes are refined independently of the stored mode table.
    k = np.sqrt(12*13)/6.8
    predicted = -float(m['surface_pressure'])*k*k/4
    energy = []
    for amplitude in [.002, .001, .0005, .00025]:
        for nodes in [128, 256, 512]:
            coefficient = corrugation_energy(amplitude, k, tau, gas, nodes)/amplitude**2
            energy.append({'amplitude': amplitude, 'nodes': nodes, 'coefficient': coefficient,
                          'predicted_coefficient': predicted, 'relative_error': abs(coefficient/predicted-1)})
    shape = pd.DataFrame(energy)
    checks['direct_shape_energy_is_negative'] = bool((shape.coefficient < 0).all())
    checks['direct_shape_quadratic_coefficient'] = bool(shape[shape.amplitude == .00025].relative_error.max() < 2e-7)
    modes = pd.read_csv(args.input/'shape_modes.csv', float_precision='round_trip')
    selected_mode = modes[(modes.width == .05)&(modes.angular_index == 12)].iloc[0].to_dict()
    selected_mode['proper_e_folding_time'] = 1/selected_mode['growth_rate']
    args.output.mkdir(parents=True, exist_ok=True)
    micro.to_csv(args.output/'microscopic_tree_matches.csv', index=False)
    spectra.to_csv(args.output/'fermion_spectrum_refinement.csv', index=False)
    shape.to_csv(args.output/'shape_energy_refinement.csv', index=False)
    for path in sources:
        checks[f'audit_input_unchanged:{source_key(path)}'] = sha256_file(path) == hashes[source_key(path)]
    size = sum(p.stat().st_size for p in args.output.iterdir())
    checks['resource_allowance'] = time.monotonic()-started < 600 and size < 20e6
    result = {'completed_utc': datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds': time.monotonic()-started, 'workers': args.workers,
        'checks': checks, 'all_checks_pass': bool(all(checks.values())),
        'source_hashes': hashes, 'best_zero_band_yukawa_one_flavor': float(opt.fun),
        'best_collective_yukawa_loop_measure': float(opt.fun**2/(16*np.pi**2)),
        'tree_matching_loop_measure': float(micro.collective_yukawa_loop_measure.iloc[0]),
        'selected_local_shape_mode': selected_mode,
        'verified_scope': 'Numerical benchmark and leading-material barrier. Positive microscopic tree parameters and planar fermion confinement are verified. Full vacuum dressing, bending response, and coupled curved-space stability remain separate.',
        'construction_status': 'Leading compressed surface has a normal gradient instability; promotion stops before the full curved quantum solve.'}
    (args.output/'audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'source_hashes'}, indent=2))
    if not result['all_checks_pass']:
        raise RuntimeError('smooth material audit failed')


if __name__ == '__main__':
    main()
