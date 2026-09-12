#!/usr/bin/env python3
"""Test the counted homogeneous condensate controller before field evolution."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

import numpy as np
from numpy.polynomial.legendre import leggauss

from adm_harness.driven_condensate_cells import core_height_interval, loaded_minimum_energy
from adm_harness.source_ledger import sha256_file
from audit_joint_dense_work import DenseHistory
from run_scalar_flux_support_gate import tensors
from run_poynting_delivery import BASE, ROOT, write_json


def location(values, t, x, maximum=True):
    i, j = np.unravel_index(np.argmax(values) if maximum else np.argmin(values), values.shape)
    return dict(value=float(values[i, j]), time=float(t[i]), x=float(x[j]))


def evaluate(spec):
    relative, label, dense, output = spec
    history = DenseHistory('routed_family', ROOT/relative)
    s = history.state
    if dense:
        xe = np.unique(np.r_[s['x'], history.h.reference.h.state['x']])
        te = history.edges
        z, w = leggauss(3)
        gx = (xe[:-1, None]+np.diff(xe)[:, None]*(z+1)/2).ravel()
        gt = (te[:-1, None]+np.diff(te)[:, None]*(z+1)/2).ravel()
        x = np.unique(np.r_[xe, gx]); t = np.unique(np.r_[te, gt])
        wx = np.zeros(len(x)); wt = np.zeros(len(t))
        np.add.at(wx, np.searchsorted(x, gx), (np.diff(xe)[:, None]*w/2).ravel())
        np.add.at(wt, np.searchsorted(t, gt), (np.diff(te)[:, None]*w/2).ravel())
    else:
        t, x = s['t'], s['x']; wx = wt = None
    (rho, p, q, radius), conservation = tensors(history, t, x, dense, wt, wx)
    lower, upper = core_height_interval(rho, p, q)
    low_x, high_x = lower.max(axis=0), upper.min(axis=0)
    ratio = np.divide(low_x, high_x, out=np.full_like(low_x, np.inf), where=high_x>0)
    ratio[low_x == 0] = 0
    j = int(np.argmax(ratio))
    il, ih = int(np.argmax(lower[:, j])), int(np.argmin(upper[:, j]))
    # The lower witness alone requires at least this V0. Since every cost
    # increases with V0 at fixed V, failure at this value also excludes all
    # larger core heights. Allowing V0(x) separately makes the gate more
    # permissive than a shared two-cell controller.
    costs, potential = loaded_minimum_energy(p, q, low_x[None, :])
    deficit = costs-rho
    k = int(np.argmin(abs(x+2.)))
    result = dict(label=label, dense=dense, temporal_samples=len(t), spatial_samples=len(x),
        common_core_height_feasible=bool(lower.max() <= upper.min()),
        arbitrary_static_spatial_grading_feasible=bool(np.all(low_x <= high_x)),
        positions_requiring_different_actuation=int(np.sum(low_x > high_x)),
        common_required_height=location(lower, t, x),
        common_permitted_height=location(upper, t, x, False),
        worst_temporal_conflict=dict(x=float(x[j]), required_height=float(low_x[j]),
            permitted_height=float(high_x[j]), ratio=float(ratio[j]),
            required_at=float(t[il]), permitted_at=float(t[ih])),
        startup_bottleneck=dict(x=float(x[k]), required_height=float(low_x[k]),
            permitted_height=float(high_x[k]), ratio=float(ratio[k])),
        least_permitted_height_replay=dict(maximum_density_shortfall=float(max(0., deficit.max())),
            witness=location(deficit, t, x)),
        conservation=conservation,
        scope='adiabatic homogeneous amplitude control with counted matter and interaction energy',
        phase_volume_conversion_tested=False, driven_field_equations_solved=False,
        currents_gradients_interfaces_and_continuing_connections_supplied=False)
    stem=label+('_dense' if dense else '_nodes')
    write_json(Path(output)/(stem+'_summary.json'), result)
    # Store only witnesses and each location's temporal interval. Full input
    # tensors can be independently reconstructed from the hashed history.
    np.savez_compressed(Path(output)/(stem+'_intervals.npz'), x=x,
        core_height_lower=low_x, core_height_upper=high_x,
        lower_witness_times=t[np.argmax(lower, axis=0)],
        upper_witness_times=t[np.argmin(upper, axis=0)],
        worst_x_times=t, worst_x_density=rho[:, j], worst_x_radial=p[:, j],
        worst_x_angular=q[:, j], worst_x_lower=lower[:, j], worst_x_upper=upper[:, j])
    print(stem+': graded='+str(result['arbitrary_static_spatial_grading_feasible'])+
          ', worst ratio='+str(result['worst_temporal_conflict']['ratio']), flush=True)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--output-name', default='virtual_cell_controller_gate')
    args=parser.parse_args()
    output=BASE/args.output_name
    if output.exists():
        raise RuntimeError('preserve completed controller evidence')
    sources=[('joint_refined_response', 'members_fraction0.99', 'retained'),
             ('scalar_flux_support_blend', 'fraction0.9', 'improved')]
    hashes={}; specs=[]
    for directory, name, label in sources:
        path=BASE/directory/(name+'_states.npz'); manifest=path.parent/'manifest.json'
        previous=json.loads(manifest.read_text())
        if sha256_file(path) != previous['output_sha256'][path.name]:
            raise RuntimeError('changed source: '+str(path))
        hashes.update(previous['input_sha256'])
        for item in (manifest, path): hashes[str(item.relative_to(ROOT))]=sha256_file(item)
        for dense in (False, True):
            specs.append((str(path.relative_to(ROOT)), label, dense, str(output)))
    for source in (Path(__file__),
            ROOT/'toolkit/adm_harness_cli/adm_harness/driven_condensate_cells.py',
            ROOT/'toolkit/adm_harness_cli/tests/test_driven_condensate_cells.py',
            Path(__file__).with_name('run_scalar_flux_support_gate.py'),
            Path(__file__).with_name('audit_joint_dense_work.py')):
        hashes[str(source.relative_to(ROOT))]=sha256_file(source)
    for path, expected in hashes.items():
        if sha256_file(ROOT/path) != expected: raise RuntimeError('changed dependency: '+path)
    output.mkdir()
    with ProcessPoolExecutor(max_workers=max(1,min(args.workers,len(specs))),
                             mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,specs))
    write_json(output/'summary.json',dict(cases=results))
    write_json(output/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes,
        output_sha256={p.name:sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
