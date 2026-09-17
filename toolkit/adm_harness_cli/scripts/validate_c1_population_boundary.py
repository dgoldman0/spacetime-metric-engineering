#!/usr/bin/env python3
"""Close reproducibility and distinguish net wall forces from two face loads."""
from pathlib import Path
import json

import numpy as np

from screen_c1_angular_response import ROOT,digest,verify_manifest


def main():
    data=ROOT/'supporting_reports/data/c1_population_boundary'
    names=['manifest.json','response_controls/manifest.json','shooting_response/manifest.json',
           'assessment_manifest.json','audit_manifest.json','refinement/manifest.json','refinement/audit_manifest.json']
    verified=sum(verify_manifest(data/name) for name in names)
    original=json.loads((data/'assessment.json').read_text())
    a=json.loads((data/'refinement/assessment.json').read_text());ledgers=[]
    for i,c in enumerate(a['cases']):
        if not c['empirical_sensitivity'] or not c['allocation']['feasible']:continue
        r=a['radial_layouts'][c['radial_layout']]
        faces=np.array(r['cost']['force_matrix'])*np.array(c['radial_central_charges'])[None,:]
        net=faces.sum(axis=1)
        left=np.array([w['module']==0 for w in r['cost']['walls']])
        added=left & np.array([w['coordinate'] in r['added_wall'] for w in r['cost']['walls']])
        if max(abs(net-c['radial_wall_forces']))>1e-10:raise RuntimeError('face-load sum differs from wall reaction')
        ledgers.append(dict(case=i,radial_layout=c['radial_layout'],reference_log=c['reference_log'],
            added_radial_reflectors=int(added.sum()),maximum_left_net_force=float(abs(net[left]).max()),
            maximum_added_net_force=float(abs(net[added]).max()),
            maximum_added_single_face_force=float(abs(faces[added]).max()),
            sum_absolute_added_face_forces=float(abs(faces[added]).sum()),
            source_face_forces=faces[added].tolist(),
            material_scope='net reaction and individual face tractions supplied; reflector stress, surface energy, mass and recoil law remain open'))
    old=json.loads((ROOT/'supporting_reports/data/c1_joint_sources/spatial/assessment.json').read_text())
    previous=next(c for c in old['six_probe_cases'] if c['reference_log']==2 and c['radial_mode']=='zones' and c['empirical_sensitivity'])
    cc=np.array(previous['radial_central_charges']).ravel();cost=original['radial_layouts']['fixed']['cost']
    baseline=dict(scope='previous six-probe allocation; fails expanded spatial check',reference_log=2,
        radial_total_central_charge=float(cc.sum()),
        radial_charge_times_proper_length=float(np.array(cost['proper_length'])@cc),
        radial_killing_bulk_energy=float(np.array(cost['killing_energy'])@cc))
    summary=dict(verified_hash_entries=verified,
        original_allocations=len(original['cases']),original_feasible=sum(c['allocation']['feasible'] for c in original['cases']),
        refinement_allocations=len(a['cases']),refinement_feasible=sum(c['allocation']['feasible'] for c in a['cases']),
        refined_empirical_feasible=len(ledgers),radial_face_loads=ledgers,previous_six_probe_cost=baseline,
        geometry_changed=False,full_spatial_source_material_and_exterior_closure=False)
    script=Path(__file__).resolve();inputs=[script]+[data/n for n in names]
    inputs+=[data/'assessment.json',data/'refinement/assessment.json',
             ROOT/'supporting_reports/data/c1_joint_sources/spatial/assessment.json']
    summary['input_sha256']={str(p.relative_to(ROOT)):digest(p) for p in inputs}
    (data/'validation.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('radial_face_loads','input_sha256')},indent=2))


if __name__=='__main__':main()
