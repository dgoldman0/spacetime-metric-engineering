#!/usr/bin/env python3
"""Absolute C1 angular-field regulator, quadrature and geometric controls."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import os
import platform
import shutil
import subprocess
import time

import numpy as np
import scipy

from adm_harness.c1_angular_absolute import (
    NativeMetric, AbsoluteComparison, cylinder_calibration, calibrated_tensor,
    integrate_comparison,
)
from screen_c1_angular_response import ROOT, digest, retained_rows, verify_manifest


def chart(spec, stride=1):
    with np.load(ROOT/spec['reference']) as z:
        return NativeMetric(*[z[k][::stride] for k in
                              ('coordinate','radius','lapse','radial_scale')])


def cases(spec, rows):
    domains = {label+'_left': [row['partitions'][0]['coordinate'][i] for i in (0,-1)]
               for label,row in rows.items()}
    domains['shared_right'] = [rows['broad']['partitions'][1]['coordinate'][i] for i in (0,-1)]
    result = []

    def add(source, x, mass, cut, name='base', **controls):
        result.append(dict(source=source,coordinate=x,domain=domains[source],mass=mass,
            cut=cut,name=name,frequency_order=spec['frequency_order'],
            phase_step=spec['throat_phase_step'] if x==0 else spec['overlap_phase_step'],
            proper_spacing=spec['proper_spacing'],attenuation=spec['attenuation'],stride=1)|controls)

    for mass in spec['throat_masses']:
        for cut in spec['throat_cutoffs']:
            add('broad_left',0.,mass,cut)
    for mass in (2.,4.):
        add('broad_left',0.,mass,64.,'cutoff_control')
    add('broad_left',0.,4.,32.,'shooting_control',phase_step=.01)
    add('broad_left',0.,4.,32.,'frequency_control',frequency_order=32)
    add('broad_left',0.,4.,32.,'metric_control',stride=2,proper_spacing=.005)
    add('narrow_left',0.,4.,32.,'narrow_throat')
    for source in ('broad_left','shared_right'):
        for mass in spec['overlap_masses']:
            add(source,.75,mass,16.)
        add(source,.75,8.,32.,'cutoff_control')
    for i,case in enumerate(result):
        case['id'] = i
    return result


def run_case(task):
    spec, case, calibration, output = task
    start = time.monotonic()
    g = chart(spec,case['stride'])
    problem = AbsoluteComparison(g,case['domain'],case['coordinate'],case['proper_spacing'])
    angular_max = int(np.ceil(case['cut']*case['mass']*problem.radius))
    value = integrate_comparison(problem,case['mass'],angular_max,case['cut']*case['mass'],
                                 case['frequency_order'],case['phase_step'],case['attenuation'])
    absolute = calibrated_tensor(problem,value['tensor'],case['mass'],calibration)
    record = dict(case,angular_max=angular_max,frequency_nodes=value['frequency_nodes'],
        raw_difference=value['tensor'].tolist(),
        **{key: item.tolist() if isinstance(item,np.ndarray) else item
           for key,item in absolute.items()},seconds=time.monotonic()-start)
    record['artifact'] = f"absolute_{case['id']:03d}.npz"
    np.savez_compressed(Path(output)/record['artifact'],harmonic_tensor=value['harmonic_tensor'])
    (Path(output)/f"case_{case['id']:03d}.json").write_text(json.dumps(record,indent=2)+'\n')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec',type=Path,default=ROOT/'toolkit/adm_harness_cli/specs/c1_angular_absolute.json')
    parser.add_argument('--output',type=Path,default=ROOT/'supporting_reports/data/c1_angular_absolute')
    parser.add_argument('--workers',type=int,default=4)
    args = parser.parse_args()
    if args.workers<1 or (args.output.exists() and any(args.output.iterdir())):
        parser.error('positive worker count and empty output directory required')
    spec = json.loads(args.spec.read_text())
    parent_verified = verify_manifest(ROOT/spec['parent_manifest'])
    rows = retained_rows(spec)
    g = chart(spec)
    calibration = cylinder_calibration(float(g.jets(np.array([0.]))[0][0]),spec['reference_log'])
    tasks = cases(spec,rows)
    args.output.mkdir(parents=True,exist_ok=True)
    records=[]
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn')) as pool:
        futures=[pool.submit(run_case,(spec,case,calibration,str(args.output))) for case in tasks]
        for future in as_completed(futures):
            record=future.result(); records.append(record)
            print(f"{len(records)}/{len(tasks)} {record['source']} x={record['coordinate']} "
                  f"M={record['mass']} cut={record['cut']} {record['name']}",flush=True)
    summary=dict(specification=str(args.spec.resolve().relative_to(ROOT)),calibration=calibration,
                 cases=sorted(records,key=lambda r:r['id']),parent_hashes_verified=parent_verified)
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    dependencies=[args.spec,Path(__file__).resolve(),
        ROOT/'toolkit/adm_harness_cli/scripts/screen_c1_angular_response.py',
        *[ROOT/'toolkit/adm_harness_cli/adm_harness'/name for name in
          ('c1_angular_absolute.py','c1_angular_absolute_kernel.c','semiclassical_joint.py',
           'c1_angular_scalar.py','c1_signed_channels.py')],
        *[ROOT/spec[key] for key in ('reference','parent_specification','parent_summary','parent_manifest')]]
    for path in dependencies[:2]+dependencies[3:5]:
        shutil.copy2(path,args.output/('execution_'+path.name))
    manifest=dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        workers=args.workers,python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
        compiler=subprocess.check_output(['cc','--version'],text=True).splitlines()[0],
        blas_threads={name:os.environ.get(name) for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')},
        input_sha256={str(p.relative_to(ROOT)):digest(p) for p in dependencies},
        output_sha256={p.name:digest(p) for p in sorted(args.output.iterdir()) if p.is_file()})
    (args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':
    main()
