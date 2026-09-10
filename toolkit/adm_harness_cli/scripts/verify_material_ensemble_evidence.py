#!/usr/bin/env python3
"""Verify saved reservoir states, run provenance, and numerical-file hashes."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT/'supporting_reports/data/material_ensemble'


def git_versions(relative_path):
    commits = subprocess.run(['git', 'log', '--format=%H', '--', relative_path],
                              cwd=ROOT, check=True, capture_output=True, text=True).stdout.splitlines()
    versions = {}
    for commit in commits:
        blob = subprocess.run(['git', 'show', f'{commit}:{relative_path}'], cwd=ROOT,
                               check=True, capture_output=True).stdout
        versions[hashlib.sha256(blob).hexdigest()] = commit
    return versions


def verify_case(path):
    manifest = json.loads(path.read_text())
    prefix = str(path)[:-len('_manifest.json')]
    summary = json.loads(Path(prefix+'_summary.json').read_text())
    cells = summary['cells']
    with np.load(prefix+'_states.npz', allow_pickle=False) as data:
        t, states, reference = data['t'], data['states'], data['reference']
    assert reference.shape == (cells,) and np.all(reference > 0)
    expected = 5*cells+1 if 'relaxation' in summary else 4*cells
    assert states.shape == (len(t), expected)
    assert np.isfinite(states).all() and np.all(np.diff(t) >= 0)
    assert abs(t[-1]-summary['s']) < 1e-12
    x = np.column_stack((np.full(len(t), -2.1), states[:, :cells-1], np.full(len(t), -.5)))
    q = states[:, 2*(cells-1):2*(cells-1)+cells+1]
    assert np.all(np.diff(x, axis=1) > 0) and np.all(q > 0)
    if summary['status'] == 'duration_completed':
        assert abs(t[-1]-summary['duration']) < 1e-12
    else:
        assert summary['status'] in ('material_domain_limit', 'compute_budget_reached')
        assert t[-1] < summary['duration']
    for name, expected_hash in manifest['input_sha256'].items():
        assert sha256_file(OUTPUT.parent/'active_transfer_reservoir'/name) == expected_hash
    return dict(case=str(path.relative_to(OUTPUT)).removesuffix('_manifest.json'),
                 snapshots=len(t), status=summary['status'], final_time=float(t[-1]),
                 minimum_saved_heat=float(q.min()), minimum_saved_cell_width=float(np.diff(x, axis=1).min()))


def main():
    manifests = sorted(OUTPUT.rglob('*_manifest.json'))
    required = {}
    for path in manifests:
        for source, digest in json.loads(path.read_text())['software_sha256'].items():
            required.setdefault(source, set()).add(digest)
    software = {}
    for source, digests in required.items():
        current = sha256_file(ROOT/source)
        history = git_versions(source) if digests != {current} else {}
        versions = {}
        for digest in sorted(digests):
            assert digest == current or digest in history, (source, digest)
            versions[digest] = 'current_file' if digest == current else history[digest]
        software[source] = versions
    with ThreadPoolExecutor(max_workers=4) as pool:
        cases = list(pool.map(verify_case, manifests))
    target = OUTPUT/'evidence_integrity.json'
    files = [p for p in sorted(OUTPUT.rglob('*')) if p.is_file() and p != target]
    with ThreadPoolExecutor(max_workers=4) as pool:
        hashes = list(pool.map(sha256_file, files))
    result = dict(verified_utc=datetime.now(timezone.utc).isoformat(),
                  verifier_sha256=sha256_file(Path(__file__)),
                  run_count=len(cases), numerical_file_count=len(files),
                  numerical_file_bytes=sum(p.stat().st_size for p in files),
                  verified_cases=cases, production_software_versions=software,
                  numerical_sha256={str(p.relative_to(OUTPUT)): digest for p, digest in zip(files, hashes)})
    target.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({key: result[key] for key in ('run_count', 'numerical_file_count', 'numerical_file_bytes')}, indent=2))


if __name__ == '__main__':
    main()
