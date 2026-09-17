#!/usr/bin/env python3
"""Normalized stresses across the central radial group and left angular divisions."""
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import argparse
import json
import multiprocessing
import shutil
import subprocess

import numpy as np
from scipy.interpolate import CubicSpline

from screen_c1_angular_absolute import run_case as absolute_case
from screen_c1_angular_response import (
    ROOT,digest,load_chart,retained_rows,run_case as response_case,verify_manifest)


def run(task):
    kind,payload=task
    return kind,(absolute_case(payload) if kind=='absolute' else response_case(payload))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec',type=Path,default=ROOT/'toolkit/adm_harness_cli/specs/c1_population_boundary.json')
    p.add_argument('--output',type=Path,default=ROOT/'supporting_reports/data/c1_population_boundary')
    p.add_argument('--workers',type=int,default=4);args=p.parse_args()
    if args.workers<1 or (args.output.exists() and any(args.output.iterdir())):
        p.error('positive workers and an empty output directory required')
    control=json.loads(args.spec.read_text())
    spec=json.loads((ROOT/control['base_specification']).read_text())
    data=ROOT/control['parent_data']
    verified=sum(verify_manifest(data/name) for name in
        ('validation.json','assessment_manifest.json','spatial/assessment_manifest.json','audit_manifest.json'))
    parent=json.loads((data/'transitions.json').read_text())
    eta=json.loads((ROOT/spec['parent_specification']).read_text())['eta']
    row=retained_rows(spec)['broad'];g=load_chart(spec)
    domain=[row['partitions'][0]['coordinate'][i] for i in (0,-1)]
    old=json.loads((data/'spatial/assessment.json').read_text())['coordinate']
    points=sorted(set(control['absolute_coordinates']+[x for x in old if domain[0]<x<domain[1]]))
    optical=CubicSpline(g.coordinate,g.radial_scale/g.lapse).antiderivative()
    angular=CubicSpline(g.coordinate,g.radial_scale/g.radius).antiderivative()
    tasks=[]
    for split in control['angular_divisions']:
        for x in [domain[0]]+points+[domain[1]]:
            name='outer_left' if x==domain[0] else 'outer_right' if x==domain[1] else 'bulk'
            distance=float(abs(angular(split)-angular(x)))
            optical_distance=float(abs(optical(split)-optical(x)))
            for resolution in control['response_resolutions']:
                case=dict(id=len(tasks),source='broad_left',module=0,compartment_count=2,
                    domain=domain,compartment_domain=[domain[0],split] if x<split else [split,domain[1]],
                    walls=[split],division=split,probe_name=name,coordinate=x,
                    angular_max=max(24,int(np.ceil(16/distance))),frequency_scale=1/optical_distance,
                    minimum_angular_distance=distance,minimum_optical_distance=optical_distance,
                    name=resolution['name'],nodes=resolution['throat_nodes'] if abs(x)<.1 else resolution['nodes'],
                    frequency_nodes=resolution['frequency_nodes'],geometry_stride=1)
                tasks.append(('response',(spec,case,eta,str(args.output))))
    for x in control['absolute_coordinates']:
        for mass in control['regulator_masses']:
            for cut in control['cutoff_multipliers']:
                case=dict(id=len(tasks),source='broad_left',domain=domain,coordinate=x,
                    mass=mass,cut=cut,name='base',frequency_order=control['frequency_order'],
                    phase_step=control['phase_step'],proper_spacing=control['proper_spacing'],
                    attenuation=40.,stride=1)
                tasks.append(('absolute',(spec,case,parent['calibration'],str(args.output))))
    case=dict(case,id=len(tasks),mass=16.,cut=16.,name='numerical_control',
              frequency_order=32,phase_step=.02,proper_spacing=.005)
    tasks.append(('absolute',(spec,case,parent['calibration'],str(args.output))))
    args.output.mkdir(parents=True,exist_ok=True)
    scripts=[Path(__file__).resolve(),args.spec]
    for path in scripts:shutil.copy2(path,args.output/('execution_'+path.name))
    records={'absolute':[],'response':[]}
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
        for f in as_completed([pool.submit(run,t) for t in tasks]):
            kind,value=f.result();records[kind].append(value)
            if kind=='response':
                (args.output/f"response_case_{value['id']:03d}.json").write_text(json.dumps(value,indent=2)+'\n')
            print(f"{sum(map(len,records.values()))}/{len(tasks)} {kind} x={value['coordinate']:.6g} "
                  f"{value.get('mass',value.get('division'))} {value['name']}",flush=True)
    for values in records.values():values.sort(key=lambda r:r['id'])
    output=args.output/'summary.json'
    output.write_text(json.dumps(dict(verified_parent_hashes=verified,
        specification=str(args.spec.relative_to(ROOT)),eta=eta,**records),indent=2)+'\n')
    inputs=[ROOT/control['base_specification'],data/'transitions.json',data/'spatial/assessment.json',
            data/'validation.json',ROOT/spec['reference'],ROOT/spec['parent_specification'],ROOT/spec['parent_summary'],
            *[ROOT/'toolkit/adm_harness_cli/scripts'/name for name in
              ('screen_c1_angular_absolute.py','screen_c1_angular_response.py')],
            *[ROOT/'toolkit/adm_harness_cli/adm_harness'/name for name in
              ('c1_angular_absolute.py','c1_angular_absolute_kernel.c','c1_angular_response.py',
               'c1_angular_scalar.py','c1_signed_channels.py','geometry_opening.py','semiclassical_joint.py')]]
    inputs+=[args.output/('execution_'+path.name) for path in scripts]
    manifest=dict(base_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        workers=args.workers,input_sha256={str(p.relative_to(ROOT)):digest(p) for p in inputs},
        output_sha256={p.name:digest(p) for p in sorted(args.output.iterdir()) if p.is_file()})
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':main()
