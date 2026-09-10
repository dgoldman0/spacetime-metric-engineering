#!/usr/bin/env python3
"""Resolve local reservoir heat duties and independent energy derivatives."""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd

from adm_harness.active_transfer_reservoir import divergence_projections
from adm_harness.source_ledger import sha256_file
from audit_material_ensemble import ROOT, OUTPUT, load_case


def audit(label):
    metadata, patch, times, states, fraction = load_case(label)
    state, t = states[-1], float(times[-1])
    f = patch.fields(t, state)
    rate, diag = patch.rhs(t, state)
    g = f['metric']
    power, force = divergence_projections(g, *patch.model.medium(t, f['x']))
    factor = g.alpha*g.radius**2/(patch.law.scale*f['effective_n'])
    endpoint = patch.forcing*factor*(-power+f['velocity']*force)
    electrical = factor*patch.electrical.sigma(f['heat'])*(f['charge']/g.radius**2)**2/f['gamma']
    offset = 2*(patch.cells-1)
    total = rate[offset:offset+patch.cells+1]
    relaxation = total-endpoint-electrical
    capacity = 4*np.pi*patch.law.scale*patch.mass
    frame = pd.DataFrame(dict(reference_fraction=fraction, l=f['x'], heat=f['heat'],
                               velocity=f['velocity'], effective_n=f['effective_n'],
                               endpoint_heat_rate=endpoint, electrical_heat_rate=electrical,
                               relaxation_heat_rate=relaxation, net_heat_rate=total,
                               thermal_inventory=capacity*f['heat'],
                               field_slice_inventory=4*np.pi*f['field_adm'],
                               endpoint_power=power, endpoint_force=force))
    frame.to_csv(OUTPUT/f'{label}_final_ports.csv', index=False)
    cold = int(np.argmin(f['heat']))
    derivatives = []
    for target in (.1, .3, .5, .75, 1., 1.285, 2., 3.):
        available = np.flatnonzero(times <= target+1e-12)
        if target > times[-1]+1e-12 or not available.size:
            continue
        index = int(available[-1])
        tt, yy = float(times[index]), states[index]
        rr, dd = patch.rhs(tt, yy)
        ff = patch.fields(tt, yy)
        # Scale the finite-difference displacement to the actual rate while
        # retaining a comfortably positive thermal state on both sides.
        h = min(1e-6, 1e-5/max(1., float(np.max(abs(rr)))))
        qr = rr[offset:offset+patch.cells+1]
        h = min(h, float(np.min(.05*ff['heat']/(abs(qr)+1e-30))))
        samples = []
        for hh in (h, h/2):
            plus, minus = patch.fields(tt+hh, yy+hh*rr), patch.fields(tt-hh, yy-hh*rr)
            hd = (plus['canonical'].sum()-minus['canonical'].sum())/(2*hh)
            momentum_derivative = (plus['momentum'].sum()-minus['momentum'].sum())/(2*hh)
            expected_h = dd['canonical_geometry']+dd['canonical_endpoint']
            expected_p = dd['momentum_free']+dd['anchor_left']+dd['anchor_right']
            samples.append(dict(step=hh, canonical_rate=hd, expected_canonical_rate=expected_h,
                                 relative_canonical_error=abs(hd-expected_h)/max(1., abs(expected_h)),
                                 momentum_rate=momentum_derivative, expected_momentum_rate=expected_p,
                                 relative_momentum_error=abs(momentum_derivative-expected_p)/max(1., abs(expected_p))))
        derivatives.append(dict(s=tt, samples=samples))
    result = dict(case=label, s=t, status=metadata['status'],
                  coldest_node=frame.iloc[cold].to_dict(),
                  initial_thermal_inventory=metadata['initial_thermal_inventory'],
                  final_thermal_inventory=float(frame.thermal_inventory.sum()),
                  total_endpoint_heat_rate=float(np.dot(capacity, endpoint)),
                  total_electrical_heat_rate=float(np.dot(capacity, electrical)),
                  total_relaxation_heat_rate=float(np.dot(capacity, relaxation)),
                  reference_fraction_cooling=float(patch.mass[total < 0].sum()/patch.mass.sum()),
                  maximum_anchor_force=diag['maximum_anchor_force'],
                  directional_derivative_checks=derivatives,
                  scope='material heat and local counter-exchange on the saved trajectory; heat inventory uses reference weights, with relativistic geometric work separately recorded in the canonical ledger',
                  source_sha256={str(p.relative_to(ROOT)): sha256_file(p) for p in [
                      OUTPUT/f'{label}_states.npz', OUTPUT/f'{label}_summary.json',
                      ROOT/'toolkit/adm_harness_cli/scripts/audit_material_ensemble.py',
                      ROOT/'toolkit/adm_harness_cli/scripts/audit_material_ensemble_ports.py']})
    (OUTPUT/f'{label}_ports.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({key: result[key] for key in ('case', 's', 'coldest_node',
                                                   'initial_thermal_inventory', 'final_thermal_inventory')}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cases', nargs='+')
    args = parser.parse_args()
    for label in args.cases:
        audit(label)


if __name__ == '__main__':
    main()
