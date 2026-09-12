#!/usr/bin/env python3
"""Construct a common phase by averaging two archived independent controls.

This is a deliberate new design, with fresh propagation required. It is
separate from roundoff reconstruction of an optimized matched pair.
"""
from datetime import datetime,timezone
from pathlib import Path
import argparse
import json
import subprocess

import numpy as np

from adm_harness.source_ledger import sha256_file
from adm_harness.virtual_cell_controls import canonical_actuation
from run_poynting_delivery import BASE,ROOT,write_json


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',default='virtual_cell_reconstructed_controls')
    parser.add_argument('--output-name',default='virtual_cell_averaged_controls')
    args=parser.parse_args();source=BASE/args.source;output=BASE/args.output_name
    if output.exists():raise RuntimeError('preserve completed common-phase controls')
    manifest=source/'manifest.json';previous=json.loads(manifest.read_text())
    files=[manifest,Path(__file__),ROOT/'toolkit/adm_harness_cli/adm_harness/virtual_cell_controls.py']
    rows=[];payload=[]
    for path in sorted(source.glob('*_states.npz')):
        meta_path=path.with_name(path.name.replace('_states.npz','_summary.json'))
        for item in (path,meta_path):
            if sha256_file(item)!=previous['output_sha256'][item.name]:
                raise RuntimeError('changed archived control: '+str(item))
            files.append(item)
        meta=json.loads(meta_path.read_text())
        target=ROOT/meta['input'];files.append(target)
        if sha256_file(target)!=previous['input_sha256'][meta['input']]:
            raise RuntimeError('changed support target')
        with np.load(path) as z:old={k:z[k] for k in z.files}
        raw=old['amplitude']
        common=np.broadcast_to(raw.mean(axis=1,keepdims=True),raw.shape).copy()
        amplitude,forward,reverse=canonical_actuation(common)
        result={k:meta[k] for k in ['label','width','center','intervals','time_nodes','efficiency',
            'interface_sigma','coherent_cell_amplitudes','heat_return','guide_drift_bound','input']}
        result.update(source_control=str(path.relative_to(ROOT)),activation_reoptimized=False,
            matched_pair_phase_history=True,
            control_construction='arithmetic mean of the two archived phases; exact positive/negative amplitude increments',
            deliberate_phase_design_change=True,
            maximum_amplitude_change=float(abs(amplitude-raw).max()),
            maximum_central_phase_jump=float(abs(amplitude[:,0]-amplitude[:,-1]).max()),
            reconstructed_simultaneous_increment=0.,wave_solution_retained=False,
            independent_replay_required=True,microscopic_phase_fronts_solved=False,
            full_construction_supplied=False)
        rows.append(result);payload.append((path.name,meta_path.name,old,amplitude,forward,reverse,result))
    if not rows:raise ValueError('source contains no controls')
    hashes={str(p.relative_to(ROOT)):sha256_file(p) for p in files}
    output.mkdir()
    for name,meta_name,old,amplitude,forward,reverse,result in payload:
        np.savez_compressed(output/name,t=old['t'],x=old['x'],edges=old['edges'],
            amplitude=amplitude,positive_increment=forward,negative_increment=reverse)
        write_json(output/meta_name,result)
    write_json(output/'summary.json',dict(cases=rows))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        provenance='direct immutable source controls and upstream manifest; current reconstruction runtime',
        input_sha256=hashes,
        output_sha256={p.name:sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__=='__main__':main()
