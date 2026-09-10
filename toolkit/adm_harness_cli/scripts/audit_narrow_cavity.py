#!/usr/bin/env python3
"""Independent derivatives and resolution evidence for finite cavity sources."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from adm_harness.narrow_cavity import interaction_logdet, planar_interaction
from evaluate_narrow_cavity import make_problem

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT/'supporting_reports/data/narrow_cavity'


def main():
    initial = json.loads((DATA/'curved_initial/summary.json').read_text())
    refined = json.loads((DATA/'curved_refined/summary.json').read_text())
    planar = json.loads((DATA/'planar/summary.json').read_text())
    selected = planar['best']
    best_refined = planar_interaction(selected['q'], selected['s'], 1024, 256)
    wider = [planar_interaction(q, s, 512, 256) for s in (4., 8.)
             for q in np.geomspace(1e-4, 1e4, 81)]
    # Fixed physical peak mass and half-width as the empty gap shrinks.
    fixed = [dict(gap=a, **planar_interaction(selected['q']*a*a, selected['s']/a, 512, 256))
             for a in (1., .5, .25, .125, .0625)]
    for row in fixed:
        row['physical_helpful_null'] = row['helpful_null']/row['gap']**3
        row['physical_mirror_null_g1'] = row['mirror_null_at_g1']/row['gap']**3
    comparison = {}
    for key, r in refined['cases'].items():
        i = initial['cases'][key]
        comparison[key] = dict(
            opening_relative_change=abs(i['interaction_opening']/r['interaction_opening']-1),
            mirror_relative_change=abs(i['mirror_opening_g1']/r['mirror_opening_g1']-1),
            crossing_relative_change=abs(i['crossing_coupling']/r['crossing_coupling']-1),
            refined_last_quarter_fraction=abs(sum(m['opening'] for m in r['modes']
                if m['angular'] > .75*r['angular_max'])/r['interaction_opening']))
    args = SimpleNamespace(cells=64, spacing=1/128, extent=48.,
                           frequency_nodes=96, angular_factor=12., seconds=900.)
    p = make_problem(6.8, .25, selected['q'], selected['s'], args)
    variation = []
    for j, scaled_frequency in [(0, .3), (4, 1.), (12, 2.)]:
        frequency = scaled_frequency*p['center_lapse']/p['gap']
        freq = p['frequency_term']*frequency**2
        ang = p['angular_term']*j*(j+1)
        links = p['links']
        dl = 2*p['fm']*links
        diagonal = links[:-1]+links[1:]+freq+ang
        dd = dl[:-1]+dl[1:]-2*p['f']*freq
        value, derivative = interaction_logdet(diagonal, links[1:-1], *p['increments'],
                                              p['cut'], (dd, dl[1:-1]))
        row = dict(angular=j, scaled_frequency=scaled_frequency, analytic_tangent=derivative,
                   differences=[])
        for step in (.02, .01, .005):
            values = []
            for epsilon in (-step, step):
                le = links*np.exp(2*epsilon*p['fm'])
                de = le[:-1]+le[1:]+ang+freq*np.exp(-2*epsilon*p['f'])
                values.append(interaction_logdet(de, le[1:-1], *p['increments'], p['cut']))
            difference = (values[1]-values[0])/(2*step)
            row['differences'].append(dict(step=step, tangent=difference,
                                          relative_error=abs(difference/derivative-1)))
        variation.append(row)
    result = dict(planar_selected_refined=best_refined,
        wider_best=min(wider, key=lambda r: r['crossing_coupling'] or float('inf')),
        wider_cases=wider, fixed_material=fixed, comparisons=comparison, metric_variations=variation)
    far = DATA/'curved_far/summary.json'
    if far.exists():
        result['boundary_comparisons'] = {k: dict(
            opening_relative_change=abs(v['interaction_opening']/refined['cases'][k]['interaction_opening']-1),
            mirror_relative_change=abs(v['mirror_opening_g1']/refined['cases'][k]['mirror_opening_g1']-1))
            for k,v in json.loads(far.read_text())['cases'].items()}
    paths = [Path(__file__), ROOT/'toolkit/adm_harness_cli/scripts/evaluate_narrow_cavity.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/narrow_cavity.py']
    paths += list(DATA.glob('*/summary.json'))
    result['source_hashes'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (DATA/'audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('wider_cases','source_hashes')}, indent=2))


if __name__ == '__main__':
    main()
