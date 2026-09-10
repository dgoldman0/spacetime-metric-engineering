#!/usr/bin/env python3
"""Measure local heat response and force costs in archived conductor replays."""
from concurrent.futures import ProcessPoolExecutor
import argparse
import json
import multiprocessing
from pathlib import Path

import numpy as np
import pandas as pd

from adm_harness.causal_heat_conductor import (
    HeatConductorLaw, FrozenHeatBackground, HeatConductor, thermal_primitive,
)
from adm_harness.source_ledger import sha256_file
from audit_material_ensemble import ROOT, load_case


def audit_case(path):
    summary = json.loads(path.read_text())
    _, patch, times, states, _ = load_case(summary['archive'])
    background = FrozenHeatBackground(patch, times, states, cells=summary['cells'],
                                      band=summary['band'],
                                      tabulation_step=summary['background_tabulation_step'])
    law = HeatConductorLaw(**summary['heat_law'])
    conductor = HeatConductor(background, law)
    prefix = path.name.removesuffix('_summary.json')
    state_path = path.with_name(prefix+'_states.npz')
    rows = []
    with np.load(state_path) as saved:
        for t, state in zip(saved['t'], saved['state']):
            bg, _ = background.sample(float(t))
            q, r = thermal_primitive(state, bg['v'], law)
            rate, powers = conductor.rhs(float(t), state)
            c2 = law.speed**2
            aa = rate[0]/q-bg['vt']*r
            bb = rate[1]-c2*bg['vt']*np.log(q)
            wt = (aa-bg['v']*bb)/(1+bg['v']*r-c2*bg['v']**2)
            rt = bb-c2*bg['v']*wt
            delta = q-bg['qbase']
            force = (delta*bg['acceleration_rate']+q*(r*wt+rt))/bg['proper_rate']
            force += bg['expansion']*q*r
            receiver = int(np.argmin(abs(background.a-.8)))
            cold, peak_flux, peak_force = int(np.argmin(q)), int(np.argmax(abs(r))), int(np.argmax(abs(force)))
            measure = 4*np.pi*background.scale*background.da
            rows.append(dict(s=float(t), receiver_heat=float(q[receiver]),
                             receiver_archived_heat=float(bg['qbase'][receiver]),
                             receiver_heat_rate=float(q[receiver]*wt[receiver]),
                             receiver_prescribed_heat_rate=float(bg['source'][receiver]),
                             receiver_relative_flux=float(r[receiver]),
                             receiver_material_velocity=float(bg['v'][receiver]),
                             receiver_added_force_per_reference=float(force[receiver]),
                             minimum_heat_fraction=float(background.a[cold]/1.6),
                             maximum_flux_fraction=float(background.a[peak_flux]/1.6),
                             maximum_force_fraction=float(background.a[peak_force]/1.6),
                             thermal_inventory_difference=float(measure*delta.sum()),
                             **powers))
    frame = pd.DataFrame(rows)
    frame.to_csv(path.with_name(prefix+'_local_audit.csv'), index=False)
    result = dict(case=summary['case'],
                  maximum_added_force_per_reference=float(frame.maximum_added_force_per_reference.max()),
                  maximum_positive_holding_power=float(frame.holding_positive_work.max()),
                  final_local_state=rows[-1],
                  source_sha256={str(p.relative_to(ROOT)): sha256_file(p) for p in
                                 (path, state_path, Path(__file__),
                                  ROOT/'toolkit/adm_harness_cli/adm_harness/causal_heat_conductor.py')})
    path.with_name(prefix+'_local_audit.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    last = rows[-1]
    print(f'{summary["case"]}: receiver rate={last["receiver_heat_rate"]:.7g}; '
          f'prescribed={last["receiver_prescribed_heat_rate"]:.7g}; '
          f'final maximum force={last["maximum_added_force_per_reference"]:.7g}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 6:
        parser.error('one to six workers required')
    paths = sorted(args.directory.resolve().glob('*_summary.json'))
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        list(pool.map(audit_case, paths))


if __name__ == '__main__':
    main()
