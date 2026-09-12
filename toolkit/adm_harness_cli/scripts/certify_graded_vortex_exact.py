#!/usr/bin/env python3
"""Exact rational checks of both archived eliminated-amplitude certificates."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import multiprocessing
import subprocess

import certify_joint_family_exact as exact
from adm_harness.source_ledger import sha256_file
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'graded_vortex_exact_certificates'


def evaluate(intervals):
    exact.INPUT = BASE/'graded_vortex_eliminated_gate'/f'n{intervals}_certificate.npz'
    exact.OUTPUT = OUTPUT/f'n{intervals}'
    exact.main()
    summary = json.loads((exact.OUTPUT/'summary.json').read_text())
    return dict(intervals=intervals, **summary)


def main():
    if OUTPUT.exists():
        raise RuntimeError('preserve completed exact graded-vortex certificates')
    previous = BASE/'graded_vortex_eliminated_gate/manifest.json'
    hashes = dict(json.loads(previous.read_text())['input_sha256'])
    for path in [previous, Path(__file__), Path(exact.__file__)]:
        hashes[str(path.relative_to(ROOT))] = sha256_file(path)
    for relative, expected in hashes.items():
        if sha256_file(ROOT/relative) != expected:
            raise RuntimeError('changed exact graded-vortex input: '+relative)
    OUTPUT.mkdir()
    with ProcessPoolExecutor(max_workers=2, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(evaluate, [128, 256]))
    write_json(OUTPUT/'summary.json', dict(cases=results,
        scope='Archived normalized eliminated-amplitude coefficient matrices treated as exact dyadic rationals. Geometry discretization and floating-point construction of those matrices retain their numerical scope.'))
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        input_sha256=hashes,
        output_sha256={str(p.relative_to(OUTPUT)):sha256_file(p) for p in sorted(OUTPUT.rglob('*')) if p.is_file()}))


if __name__ == '__main__':
    main()
