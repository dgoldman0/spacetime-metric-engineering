#!/usr/bin/env python3
"""Archive a short checked contradiction for the restricted material family."""
from datetime import datetime,timezone
from pathlib import Path
import json
import subprocess

import numpy as np

import adm_harness.cutting_plane_lp as cuts
from adm_harness.lp_infeasibility_certificate import certificate
from adm_harness.source_ledger import sha256_file
import run_joint_field_membrane_gate as gate
from run_poynting_delivery import BASE,ROOT,write_json

OUTPUT=BASE/'joint_field_membrane_certificate'


def main():
    if OUTPUT.exists():raise RuntimeError('preserve completed certificate evidence')
    previous=BASE/'joint_field_membrane_gate/manifest.json'
    hashes=json.loads(previous.read_text())['input_sha256']
    for p in (Path(__file__),previous,Path(__file__).with_name('run_joint_field_membrane_gate.py'),
              ROOT/'toolkit/adm_harness_cli/adm_harness/cutting_plane_lp.py',
              ROOT/'toolkit/adm_harness_cli/adm_harness/lp_infeasibility_certificate.py'):
        hashes[str(p.relative_to(ROOT))]=sha256_file(p)
    for p,expected in hashes.items():
        if sha256_file(ROOT/p)!=expected:raise RuntimeError('changed certificate input: '+p)
    OUTPUT.mkdir();captured={};original=cuts.linprog
    def record(cost,**kwargs):
        result=original(cost,**kwargs)
        if result.status==2:
            proof=certificate(kwargs['A_ub'],kwargs['b_ub'],kwargs['bounds'])
            if not proof['valid']:raise ArithmeticError('infeasibility certificate failed its independent check')
            arrays={k:v for k,v in proof.items() if isinstance(v,np.ndarray)}
            np.savez_compressed(OUTPUT/'certificate.npz',**arrays)
            captured.update({k:v for k,v in proof.items() if not isinstance(v,np.ndarray)})
            captured['retained_constraint_count']=len(proof['weights'])
        return result
    cuts.linprog=record
    def solver(cost,*,A_ub,b_ub,bounds,**unused):
        result=cuts.solve_with_cuts(cost,A_ub,b_ub,bounds,deadline=180.)
        captured['cut_history']=result.cut_history
        return result
    gate.retained_coefficient_program=solver;gate.OUTPUT=OUTPUT
    result=gate.evaluate(True)
    if result['status']!=2 or not captured.get('valid'):
        raise ArithmeticError('the expected restricted-family contradiction was not reproduced')
    write_json(OUTPUT/'summary.json',dict(family_result=result,certificate=captured,
        scope='Pinned 27-control material response plus two bounded directional work fractions; finite 128-cell/258-time representation'))
    write_json(OUTPUT/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes,output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__=='__main__':main()
