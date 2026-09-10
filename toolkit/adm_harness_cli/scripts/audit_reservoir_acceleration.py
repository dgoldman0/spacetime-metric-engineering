#!/usr/bin/env python3
"""Record the archived cold-element force decomposition and slow-path kinematics."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from adm_harness.active_transfer_reservoir import divergence_projections
from adm_harness.source_ledger import sha256_file
from audit_material_ensemble import ROOT, OUTPUT as ARCHIVE, load_case

OUTPUT = ROOT/'supporting_reports/data/prestressed_buffer_assembly'
CASE = 'relaxing/thermal_only_baseline_n64_end3_dt0.0005_snap601_cfl0.05'


def main():
    OUTPUT.mkdir(exist_ok=True)
    _, patch, times, states, _ = load_case(CASE)
    rows = []
    for t, state in zip(times, states):
        f = patch.fields(float(t), state)
        g, node = f['metric'], patch.cells//2
        traction = .5*patch.law.scale*(g.alpha[:-1]*g.b[:-1]*f['pressure'][0]
                                        +g.alpha[1:]*g.b[1:]*f['pressure'][1])
        terms = dict(traction=np.r_[0., traction]-np.r_[traction, 0.],
                     lapse=-patch.law.scale*g.b*f['energy_int']*g.alpha_x,
                     radial_metric=patch.law.scale*g.alpha*g.b*f['radial_int']*g.logb_x,
                     shift=patch.law.scale*g.b**2*f['current_int']*g.beta_x)
        power, force = divergence_projections(g, *patch.model.medium(float(t), f['x']))
        terms['endpoint'] = -g.alpha*g.b**2*g.radius**2*f['volume']*force
        actual, _ = patch.rhs(float(t), state)
        measured = actual[patch.cells-1+node-1]
        rows.append(dict(s=float(t), x=float(f['x'][node]), velocity=float(f['velocity'][node]),
                         gamma=float(f['gamma'][node]), heat=float(f['heat'][node]),
                         effective_n=float(f['effective_n'][node]), momentum=float(f['momentum'][node]),
                         alpha=float(g.alpha[node]), b=float(g.b[node]),
                         coordinate_fixed_velocity=float((g.b*g.beta/g.alpha)[node]),
                         momentum_rate=float(measured),
                         decomposition_residual=float(sum(term[node] for term in terms.values())-measured),
                         **{key:float(value[node]) for key, value in terms.items()}))
    frame = pd.DataFrame(rows)
    frame.to_csv(OUTPUT/'archived_cold_element_force.csv', index=False)
    # The coordinate-stationary screen retains every active metric field.
    x = np.linspace(*patch.edges, 257)
    fixed = []
    for t in np.linspace(0., 3., 1201):
        g = patch.model.metric(float(t), x)
        velocity = g.b*g.beta/g.alpha
        fixed.append(dict(s=float(t), maximum_abs_velocity=float(abs(velocity).max()),
                          minimum_alpha=float(g.alpha.min()), maximum_alpha=float(g.alpha.max()),
                          minimum_b=float(g.b.min()), maximum_b=float(g.b.max()),
                          minimum_packet_gap=float(np.min(abs(x-t))-.35)))
    pd.DataFrame(fixed).to_csv(OUTPUT/'coordinate_fixed_kinematics.csv', index=False)
    sources = [Path(__file__), ARCHIVE/f'{CASE}_states.npz', ARCHIVE/f'{CASE}_summary.json',
               ROOT/'supporting_reports/data/active_transfer_reservoir/metric_fine.npz',
               ROOT/'supporting_reports/data/active_transfer_reservoir/medium_baseline.npz',
               ROOT/'toolkit/adm_harness_cli/adm_harness/material_ensemble.py',
               ROOT/'toolkit/adm_harness_cli/adm_harness/relaxing_material_ensemble.py',
               ROOT/'toolkit/adm_harness_cli/scripts/audit_material_ensemble.py']
    result = dict(archive=CASE,
                  maximum_force_decomposition_residual=float(abs(frame.decomposition_residual).max()),
                  maximum_coordinate_fixed_speed=max(row['maximum_abs_velocity'] for row in fixed),
                  minimum_coordinate_fixed_packet_gap=min(row['minimum_packet_gap'] for row in fixed),
                  scope='force decomposition on the archived thermal material; coordinate-fixed paths are a kinematic control with their holding stress still to be supplied',
                  source_sha256={str(path.relative_to(ROOT)): sha256_file(path) for path in sources})
    (OUTPUT/'force_audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key:value for key,value in result.items() if key not in ('source_sha256','scope')}, indent=2))


if __name__ == '__main__':
    main()
