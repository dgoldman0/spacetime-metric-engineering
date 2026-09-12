#!/usr/bin/env python3
"""Archive reconstructed controls, discarding the previous wave solution."""
from datetime import datetime,timezone
from pathlib import Path
import argparse
import json
import subprocess
import numpy as np

from adm_harness.source_ledger import sha256_file
from adm_harness.virtual_cell_controls import canonical_actuation,canonical_matched_actuation
from run_poynting_delivery import BASE,ROOT,write_json


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',default='virtual_cell_wave_envelope')
    parser.add_argument('--output-name',default='virtual_cell_reconstructed_controls')
    args=parser.parse_args(); source=BASE/args.source; output=BASE/args.output_name
    if output.exists(): raise RuntimeError('preserve reconstructed control evidence')
    manifest=source/'manifest.json'; previous=json.loads(manifest.read_text())
    hashes=dict(previous['input_sha256']); hashes[str(manifest.relative_to(ROOT))]=sha256_file(manifest)
    for p in [Path(__file__),ROOT/'toolkit/adm_harness_cli/adm_harness/virtual_cell_controls.py',
              ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_controls.py']:
        hashes[str(p.relative_to(ROOT))]=sha256_file(p)
    for relative,expected in hashes.items():
        if sha256_file(ROOT/relative)!=expected: raise RuntimeError('changed dependency: '+relative)
    output.mkdir(); results=[]
    for path in sorted(source.glob('*_states.npz')):
        meta_path=path.with_name(path.name.replace('_states.npz','_summary.json'))
        for p in [path,meta_path]:
            if sha256_file(p)!=previous['output_sha256'][p.name]: raise RuntimeError('changed source control')
            hashes[str(p.relative_to(ROOT))]=sha256_file(p)
        meta=json.loads(meta_path.read_text())
        with np.load(path) as z: old={k:z[k] for k in z.files}
        matched=meta.get('matched_pair_phase_history',False)
        reconstruct=canonical_matched_actuation if matched else canonical_actuation
        amplitude,forward,reverse=reconstruct(old['amplitude'])
        label=meta['label']
        result={k:meta[k] for k in ['label','width','center','intervals','time_nodes','efficiency',
            'interface_sigma','coherent_cell_amplitudes','heat_return','guide_drift_bound','input']}
        result.update(source_control=str(path.relative_to(ROOT)),activation_reoptimized=False,
            matched_pair_phase_history=matched,
            control_construction='nonnegative phase amplitude; positive and negative parts of its exact time increment',
            maximum_amplitude_change=float(abs(amplitude-old['amplitude']).max()),
            maximum_forward_increment_increase=float(np.maximum(forward-old['positive_increment'],0).max()),
            maximum_reverse_increment_increase=float(np.maximum(reverse-old['negative_increment'],0).max()),
            raw_simultaneous_increment=float(np.minimum(old['positive_increment'],old['negative_increment']).max()),
            reconstructed_simultaneous_increment=0.,
            wave_solution_retained=False,independent_replay_required=True,
            microscopic_phase_fronts_solved=False,full_construction_supplied=False)
        np.savez_compressed(output/path.name,t=old['t'],x=old['x'],edges=old['edges'],
            amplitude=amplitude,positive_increment=forward,negative_increment=reverse)
        write_json(output/meta_path.name,result); results.append(result)
    write_json(output/'summary.json',dict(cases=results))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes,output_sha256={p.name:sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__=='__main__': main()
