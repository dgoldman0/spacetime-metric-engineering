#!/usr/bin/env python3
"""Numerical comparison of complete magnetic circuits and field spreading."""
import hashlib
import json
from pathlib import Path

import numpy as np

from adm_harness.magnetic_circuits import RailChart, loop_integrals, magnetic_budget

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT/'supporting_reports/data/magnetic_circuits'
CACHE = ROOT/'supporting_reports/data/archived_geometry_opening/reference_metric.npz'


def key(row):
    return row['center_coordinate'], row['leg'], row['cap']


def compare(first, second):
    a = {key(r):r for r in first['loops']}
    b = {key(r):r for r in second['loops']}
    assert a.keys() == b.keys()
    comparisons=[]
    for k,r in b.items():
        old=a[k]
        pairs=zip(old['budgets'],r['budgets'])
        comparisons.append(dict(center=k[0],leg=k[1],cap=k[2],
            quantum_relative_change=abs(old['quantum_coefficient']/r['quantum_coefficient']-1),
            normalized_quantum_change=abs(old['quantum_coefficient']-r['quantum_coefficient'])/
                max(abs(r['casimir_coefficient']),abs(r['anomaly_coefficient']),1e-30),
            sign_preserved=(old['quantum_coefficient'] > 0)==(r['quantum_coefficient'] > 0),
            maximum_magnetic_relative_change=max(abs(x['magnetic_load_at_e1']/y['magnetic_load_at_e1']-1)
                                                  for x,y in pairs)))
    return comparisons


def main():
    runs={p.parent.name:json.loads(p.read_text()) for p in DATA.glob('*/summary.json')}
    comparisons={f'{a}_to_{b}':compare(runs[a],runs[b]) for a,b in
                 [('initial','refined'),('spreading','spreading_refined')]}
    fixed={key(r):r for r in runs['refined']['loops']}
    changes=[]
    candidates=[]
    per_center={}
    for row in runs['spreading_refined']['loops']:
        for old,budget in zip(fixed[key(row)]['budgets'],row['budgets']):
            changes.append(1-budget['magnetic_load_at_e1']/old['magnetic_load_at_e1'])
            if budget['required_loop_measure'] is not None:
                candidates.append((budget['required_loop_measure'],row,budget))
                center=str(row['center_coordinate'])
                per_center[center]=min(per_center.get(center,float('inf')),budget['required_loop_measure'])
    candidates.sort(key=lambda value:value[0])
    chart=RailChart(CACHE)
    fine=[]
    seen=set()
    for threshold,row,budget in candidates:
        if key(row) in seen:
            continue
        seen.add(key(row))
        recalculated=loop_integrals(chart.fields,row['center'],row['leg'],row['cap'],
                                   nodes=512,resolve_profiles=True)
        rb=magnetic_budget(recalculated,budget['flux'],budget['margin'],adaptive=True)
        fine.append(dict(center=row['center_coordinate'],leg=row['leg'],cap=row['cap'],
            old_required_loop_measure=threshold,new_required_loop_measure=rb['required_loop_measure'],
            relative_change=abs(rb['required_loop_measure']/threshold-1)))
        if len(fine)==8:
            break
    best=runs['spreading_refined']['best']
    geometry=best['geometry']
    def rescaled_fields(l):
        r,a,u,ap=chart.fields(l)
        return r,7*a,u,ap
    rescaled=loop_integrals(rescaled_fields,geometry['center'],geometry['leg'],geometry['cap'],
                           nodes=256,resolve_profiles=True)
    rb=magnetic_budget(rescaled,best['budget']['flux'],best['budget']['margin'],adaptive=True)
    cross=best['budget']['required_flavors_times_e_squared']
    result=dict(comparisons=comparisons,per_center_minimum_required_loop_measure=per_center,
        best_source=best,maximum_fractional_bend_cost_reduction=max(changes),
        finer_best_geometries=fine,
        native_clock_rescaling_relative_error=abs(rb['required_flavors_times_e_squared']/cross-1),
        best_load_to_vacuum_ratio_preferred_ladder=cross/8,
        best_load_to_vacuum_ratio_entire_ladder=cross/54,
        best_load_to_vacuum_ratio_continuous_loop_measure_0_1=best['budget']['required_loop_measure']/.1)
    paths=[Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/magnetic_circuits.py',CACHE]
    paths+=list(DATA.glob('*/summary.json'))
    result['source_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (DATA/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    overview={k:v for k,v in result.items() if k not in ('comparisons','source_hashes')}
    overview['comparison_maxima']={k:dict(
        normalized_quantum=max(r['normalized_quantum_change'] for r in rows),
        magnetic=max(r['maximum_magnetic_relative_change'] for r in rows),
        all_signs_preserved=all(r['sign_preserved'] for r in rows)) for k,rows in comparisons.items()}
    print(json.dumps(overview,indent=2))


if __name__=='__main__':
    main()
