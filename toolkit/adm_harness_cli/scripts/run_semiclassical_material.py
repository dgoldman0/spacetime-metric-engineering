#!/usr/bin/env python3
"""Solve and archive the first fixed-charge quantum/material block update."""
from pathlib import Path
import argparse
import json
import time

import numpy as np
import pandas as pd

from adm_harness.condensate_vacuum import JoinedProfile
from adm_harness.semiclassical_joint import SmoothJointSeed
from adm_harness.semiclassical_material import relax_material
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--regulator', type=float, default=8.)
    parser.add_argument('--tolerance', type=float, default=2e-6)
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('choose an empty output directory')
    started = time.monotonic()
    manifest_path = args.source/'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    data_path = args.source/'source_profile.csv'
    if sha256_file(data_path) != manifest['output_hashes'][data_path.name]:
        raise ValueError('changed quantum source input')
    data = pd.read_csv(data_path).query('regulator == @args.regulator').sort_values('proper')
    if data.empty:
        raise ValueError('requested regulator missing from source')
    profile = JoinedProfile(ROOT)
    seed = SmoothJointSeed(profile, manifest['width'], manifest['seed_spacing'])
    result, checks = relax_material(seed, data.proper.to_numpy(), data.polarization.to_numpy(), args.tolerance)
    checks['elapsed_seconds'] = time.monotonic()-started
    args.output.mkdir(parents=True, exist_ok=True)
    if checks['accepted']:
        l = np.arange(*seed.domain, .025)
        # Cover the closed interval for subsequent interpolation.
        l = np.r_[l, seed.domain[-1]]
        np.savez_compressed(args.output/'material.npz', proper=l,
            amplitudes=result.sol(l)[[0, 2, 4]], frequency=result.p[0],
            coefficients=result.sol.c, knots=result.sol.x,
            width=manifest['width'], seed_spacing=manifest['seed_spacing'])
    checks['source_hashes'] = {str(p): sha256_file(p) for p in [Path(__file__).resolve(), data_path,
        manifest_path, ROOT/'toolkit/adm_harness_cli/adm_harness/semiclassical_material.py']}
    checks['output_hashes'] = {p.name: sha256_file(p) for p in args.output.iterdir()}
    (args.output/'checks.json').write_text(json.dumps(checks, indent=2)+'\n')
    print(json.dumps(checks, indent=2), flush=True)


if __name__ == '__main__':
    main()
