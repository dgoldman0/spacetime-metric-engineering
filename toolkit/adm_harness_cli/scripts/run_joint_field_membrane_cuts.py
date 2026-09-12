#!/usr/bin/env python3
"""Apply constraint generation to the unchanged field/membrane response model.

The previous runner assembles the complete inequalities. This wrapper injects
the new LP solver and redirects output, preserving that earlier evidence.
Every accepted solution is checked against all original inequalities.
"""
from datetime import datetime,timezone
from pathlib import Path
import json
import subprocess

from adm_harness.cutting_plane_lp import solve_with_cuts
from adm_harness.source_ledger import sha256_file
import run_joint_field_membrane_gate as gate
from run_poynting_delivery import BASE,ROOT,write_json

OUTPUT=BASE/'joint_field_membrane_cuts'


def main():
    if OUTPUT.exists():raise RuntimeError('preserve completed constraint-generation evidence')
    previous=BASE/'joint_field_membrane_gate/manifest.json'
    hashes=json.loads(previous.read_text())['input_sha256']
    for p in (Path(__file__),previous,Path(__file__).with_name('run_joint_field_membrane_gate.py'),
              ROOT/'toolkit/adm_harness_cli/adm_harness/cutting_plane_lp.py'):
        hashes[str(p.relative_to(ROOT))]=sha256_file(p)
    for p,expected in hashes.items():
        if sha256_file(ROOT/p)!=expected:raise RuntimeError('changed cut-program input: '+p)
    OUTPUT.mkdir();history={}
    def solver(cost,*,A_ub,b_ub,bounds,**unused):
        result=solve_with_cuts(cost,A_ub,b_ub,bounds,deadline=180.)
        history.update(cut_history=result.cut_history,total_rows=result.total_rows,
                       maximum_full_violation=result.get('maximum_full_violation'))
        return result
    gate.retained_coefficient_program=solver;gate.OUTPUT=OUTPUT
    summary=gate.evaluate(True);summary.update(history)
    write_json(OUTPUT/'summary.json',summary)
    write_json(OUTPUT/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes,output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__=='__main__':main()
