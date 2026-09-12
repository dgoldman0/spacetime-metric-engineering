#!/usr/bin/env python3
"""Finite prestretch continuation and independent mesh/connection controls."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

import run_joint_backing_link as pilot
from adm_harness.source_ledger import sha256_file
from run_poynting_delivery import BASE,ROOT,write_json

OUTPUT=BASE/'joint_backing_link_continuation'


def evaluate(spec):
    pilot.OUTPUT=OUTPUT
    return pilot.evaluate(spec)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    if OUTPUT.exists():
        raise RuntimeError('preserve completed joint continuation evidence')
    preceding=BASE/'joint_backing_link/manifest.json'
    hashes=json.loads(preceding.read_text())['input_sha256']
    for path in (Path(__file__),preceding,
                 ROOT/'toolkit/adm_harness_cli/tests/test_joint_backing_link_force.py'):
        hashes[str(path.relative_to(ROOT))]=sha256_file(path)
    for path,expected in hashes.items():
        if sha256_file(ROOT/path)!=expected:
            raise RuntimeError(f'changed joint continuation input: {path}')
    OUTPUT.mkdir(parents=True)
    specs=[(32,8,delta,'exposed',False) for delta in (1e-6,1e-4,1e-3)]
    specs.extend([(64,4,0.,'exposed',False),(32,8,0.,'balanced',False),
                  (32,8,0.,'exposed',True)])
    with ProcessPoolExecutor(max_workers=min(4,args.workers),mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,specs))
    write_json(OUTPUT/'summary.json',dict(cases=results))
    write_json(OUTPUT/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),input_sha256=hashes,
        output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__=='__main__':
    main()
