#!/usr/bin/env python3
"""Evaluate rounded population witnesses and empirical numerical sensitivity."""
from pathlib import Path
import argparse
import json
import shutil

import numpy as np

from adm_harness.c1_angular_absolute import conformal_log_source
from adm_harness.c1_signed_channels import dec_projections
from screen_c1_angular_absolute import chart
from screen_c1_angular_response import ROOT, digest, verify_manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data',type=Path,default=ROOT/'supporting_reports/data/c1_angular_absolute')
    args=parser.parse_args()
    verified=verify_manifest(args.data/'manifest.json')+verify_manifest(args.data/'audit_manifest.json')
    audit=json.loads((args.data/'audit.json').read_text())
    summary=json.loads((args.data/'summary.json').read_text())
    spec=json.loads((ROOT/summary['specification']).read_text())
    budget=audit['budget'];eta=budget['eta']
    # These envelopes exceed the observed controls. They describe empirical
    # sensitivity, not a rigorous truncation or physical uncertainty bound.
    envelope=dict(throat=3e-11,left_overlap=3e-7,right_overlap=6e-6)
    witnesses=[]
    for ell,nl,nr in ((2.,25100000,5000000),(4.,12000000,12000000)):
        case=next(r for r in budget['fixed_global_normalization_cases'] if r['reference_log']==ell)
        throat=np.array(budget['throat_target'])-nl*np.array(case['throat_one_field'])
        overlap=(np.array(budget['overlap_target'])-nl*np.array(case['overlap_left_one_field'])
                 -nr*np.array(case['overlap_right_one_field']))
        et=eta*nl*envelope['throat']
        eo=eta*(nl*envelope['left_overlap']+nr*envelope['right_overlap'])
        witnesses.append(dict(reference_log=ell,left_fields=nl,right_fields=nr,
            throat_remainder=throat.tolist(),overlap_remainder=overlap.tolist(),
            throat_dec_margins=dec_projections(throat).tolist(),overlap_dec_margins=dec_projections(overlap).tolist(),
            throat_margins_after_envelope=(dec_projections(throat)-2*et).tolist(),
            overlap_margins_after_envelope=(dec_projections(overlap)-2*eo).tolist()))
    curvature=[]
    for stride in (1,2,4):
        g=chart(spec,stride)
        curvature.append(dict(stride=stride,overlap_log_source=conformal_log_source(*g.proper_log_jets(.75)).tolist()))
    result=dict(verified_hashes=verified,empirical_one_field_component_envelopes=envelope,
                rounded_witnesses=witnesses,overlap_curvature_controls=curvature,
                physical_acceptance=False,scope='necessary bulk cone at two probes; physical boundary/material/exterior closure remains open')
    (args.data/'assessment.json').write_text(json.dumps(result,indent=2)+'\n')
    script=Path(__file__).resolve();snapshot=args.data/('execution_'+script.name)
    shutil.copy2(script,snapshot)
    inputs=[args.data/'audit.json',args.data/'audit_manifest.json',script]
    names=lambda p:str(p.resolve().relative_to(ROOT)) if p.resolve().is_relative_to(ROOT) else str(p.resolve())
    manifest=dict(input_sha256={names(p):digest(p) for p in inputs},
                  output_sha256={p.name:digest(p) for p in (args.data/'assessment.json',snapshot)})
    (args.data/'assessment_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
