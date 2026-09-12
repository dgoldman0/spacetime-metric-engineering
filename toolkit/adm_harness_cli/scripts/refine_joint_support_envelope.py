#!/usr/bin/env python3
"""Stress margin and mesh controls retaining the original pressure medium."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

import run_joint_support_envelope as pilot
from adm_harness.source_ledger import sha256_file
from run_poynting_delivery import BASE,ROOT,write_json

OUTPUT=BASE/'joint_support_envelope_refinement'


def evaluate(spec):
    pilot.OUTPUT=OUTPUT
    return pilot.evaluate(spec)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    if OUTPUT.exists():
        raise RuntimeError('preserve completed joint envelope refinement evidence')
    preceding=BASE/'joint_support_envelope/manifest.json'
    hashes=json.loads(preceding.read_text())['input_sha256']
    for path in (Path(__file__),preceding):
        hashes[str(path.relative_to(ROOT))]=sha256_file(path)
    for path,expected in hashes.items():
        if sha256_file(ROOT/path)!=expected:
            raise RuntimeError(f'changed joint refinement input: {path}')
    OUTPUT.mkdir(parents=True)
    specs=[(32,8,f,'exposed',True) for f in (.9,.75)]
    specs.extend([(64,4,1.,'exposed',True),(64,2,1.,'exposed',True)])
    with ProcessPoolExecutor(max_workers=min(4,args.workers),mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,specs))
    write_json(OUTPUT/'summary.json',dict(cases=results))
    write_json(OUTPUT/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),input_sha256=hashes,
        output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__=='__main__':
    main()
