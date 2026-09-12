#!/usr/bin/env python3
"""Bounded partial-unloading and attachment screen for capacitor composites.

Grants perfect local work reuse/conversion and ideal matched transport.
The old fluid and geometry stay pinned. The added heat inventory, finite
charge confinement, contact losses and physical backing dynamics remain open.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

import numpy as np
import pandas as pd

from adm_harness.composite_capacitor import anisotropic_moments
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.poynting_delivery import propagate, wave_moments
from adm_harness.shared_field_delivery import radial_field_moments
from adm_harness.source_ledger import sha256_file
from evaluate_capacitor_work_delivery import GeometryTable
from evaluate_composite_capacitor import family_history, history
from evaluate_finite_work_interface import InterfaceHistory
from evaluate_recovery_work_interface import recovery_state
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'composite_capacitor_transport'
UNLOAD = (0., .025, .05, .1, .25, .5, 1.)


def attachment_audit(model, state):
    """Pinned real-interface force still required with zero added cap material.

    A co-moving skin with pr=0 has F=rho*a-2*pt*s(ln R). The charged Fermi
    skin spans -rho<=pt<=rho/2; a wider DEC control spans +/-rho.
    Each sign test grants an arbitrary nonnegative local skin density.
    """
    c = model.cm
    wave = model.positive/.98+.98*model.negative
    heat = ((state['heat'][1:]+state['heat'][:-1])/2+state['heat_cap']/3)/c['rest_volume']*c['acceleration']
    field = state['derivative']/(c['gamma']*c['b']*c['radius']**4)
    endpoint = c['gamma']*(c['normal_force']-c['v']*c['power'])
    required = endpoint-wave-heat-field
    a, k = c['acceleration'], c['angular_gradient']
    weight = abs(required)*c['lapse']*c['rest_volume']*np.diff(model.t)[:,None]
    rows = []
    for name, q1, q2 in (('charged_fermi_skin', a-k, a+2*k),
                         ('any_DEC_skin', a-2*abs(k), a+2*abs(k))):
        low, high = np.minimum(q1,q2), np.maximum(q1,q2)
        allowed = ((required >= 0)&(high > 0))|((required <= 0)&(low < 0))|(abs(required) < 1e-12)
        bad = ~allowed
        it,j = np.unravel_index(np.argmax(abs(required)*bad), required.shape)
        rows.append(dict(skin=name, unsupported_force_weighted_fraction=float(np.sum(weight*bad)/np.sum(weight)),
            maximum_unsupported_force=float(np.max(abs(required)*bad)),
            unsupported_peak_time=float((model.t[it]+model.t[it+1])/2), unsupported_peak_x=float(model.x[j]),
            unsupported_peak_required_force=float(required[it,j]),
            force_per_energy_lower_at_peak=float(low[it,j]), force_per_energy_upper_at_peak=float(high[it,j])))
    return dict(maximum_required_holding_force=float(np.max(abs(required))),
                maximum_heat_holding_force=float(np.max(abs(heat))),
                skins=rows, radial_backing='Radial pressure gradients introduce a separate longitudinal force channel.'), required


def support_force(model, energy, radial, angular):
    """Mid-interval material force from a diagonal support tensor.

    F=(rho+pr)*a+s(pr)+2*(pr-pt)*s(log R). Spatial derivatives use the
    resolved center grid, with endpoint samples excluded from peak reporting.
    The supplied geometry and original temporal ledger are unchanged.
    """
    c = model.cm
    pr = (radial[1:]+radial[:-1])/2
    pt = (angular[1:]+angular[:-1])/2
    rho = (energy[1:]+energy[:-1])/(2*c['rest_volume'])
    pr_t = np.diff(radial,axis=0)/np.diff(model.t)[:,None]
    pr_x = np.gradient(pr,model.x,axis=1,edge_order=2)
    return ((rho+pr)*c['acceleration']+pr_x/(c['gamma']*c['b'])
            +c['v']*pr_t/c['lapse']+2*(pr-pt)*c['angular_gradient'])


def evaluate(spec):
    cells, subdivisions = spec
    model = InterfaceHistory(cells)
    state = recovery_state(model,1.)
    geometry = GeometryTable(model,subdivisions)
    h = history(model,state)
    c, cm = model.c, model.cm
    radius = c['radius']
    attachment, old_required = attachment_audit(model,state)
    cap = float(model.cap.max())
    # Full recovery already saturates the admissible shared electric profile.
    unused, share, derivative = model.allocation(cap)
    if np.max(abs(share-state['share'])) > 1e-12:
        raise ArithmeticError('transport control requires the same saturated allocation')
    cases, phase_rows, balances = [], [], []
    for family in ('dec_floor','directional','stiff_fluid','radiation_fluid'):
        f = family_history(h,family)
        for unload in (UNLOAD if family in ('dec_floor','directional') else (0.,1.)):
            energy = (1-unload)*f['retained_energy']+unload*f['minimum_energy']
            support = anisotropic_moments(energy/h['volume'], f['radial_pressure'],f['angular_pressure'],c['v'])
            joint_work = h['electrical']+unload*f['active_port']
            # The entire requested work is transported. An interpolation in
            # unloading fraction changes both the inventory and the source.
            power = joint_work/np.diff(model.t)[:,None]
            streams, local_balances = [], []
            for direction,supplied,backwards in ((-1,np.maximum(power,0),True),
                                                  (1,np.maximum(-power,0),False)):
                values, ledger = propagate(model.t,model.h.edges,
                    geometry.coefficients(direction,supplied),backwards=backwards)
                streams.append(values/model.volume)
                for row in ledger:
                    row.update(family=family,unload_fraction=unload,direction=direction)
                local_balances.extend(ledger)
            minus,plus = streams
            wave = wave_moments(plus,minus)
            peak = max(float(np.max(minus*c['gamma']**2*(1+c['v'])**2*radius**4)),
                       float(np.max(plus*c['gamma']**2*(1-c['v'])**2*radius**4)))
            guide = max(cap,2*1.03*1.5*peak)
            relaxed = max(cap,2*1.03*.5*(.9**-2-1)*peak)
            fields = dict(delivery_drift050=support+wave+radial_field_moments((guide-share)/radius**4),
                          delivery_drift090=support+wave+radial_field_moments((relaxed-share)/radius**4),
                          guide_omitted_tensor_bound=support+wave-radial_field_moments(share/radius**4))
            for route,auxiliary in fields.items():
                for it,time,demand in model.phases:
                    tensor = model.supply[:,it]+auxiliary[:,it]-demand
                    value,direction = maximum_null(tensor)
                    j = int(np.argmax(value))
                    phase_rows.append(dict(family=family,unload_fraction=unload,route=route,time=time,
                        required_negative_null=float(max(0.,value[j])),peak_x=float(model.x[j]),
                        peak_null_cosine=float(direction[j]),
                        auxiliary_ADM=float(model.integrate(model.volume[it]*auxiliary[0,it]))))
            mechanical = h['mechanical']+f['mechanical_work']
            work_error = float(abs(np.diff(h['energy']+energy,axis=0)-joint_work-mechanical).max())
            # This is an additional diagnostic on the ideal work route, whose
            # heat and finite coupling stresses are explicitly omitted. It
            # checks whether the assigned support by itself completes force.
            force = support_force(model,energy,f['radial_pressure'],f['angular_pressure'])
            endpoint = cm['gamma']*(cm['normal_force']-cm['v']*cm['power'])
            wave_force = abs(power)/(cm['lapse']*cm['rest_volume'])
            extra_field_force = derivative/(cm['gamma']*cm['b']*cm['radius']**4)
            remainder = endpoint-wave_force-extra_field_force-force
            core = remainder[:,1:-1]
            it,j0 = np.unravel_index(np.argmax(abs(core)),core.shape)
            j=j0+1
            cases.append(dict(family=family,unload_fraction=unload,cells=cells,time_subdivisions=subdivisions,
                initial_support_rest=float(model.integrate(energy[0])),final_support_rest=float(model.integrate(energy[-1])),
                joint_work_input=float(model.integrate(np.maximum(joint_work,0).sum(axis=0))),
                joint_work_export=float(model.integrate(np.maximum(-joint_work,0).sum(axis=0))),
                required_guide_flux=guide,relaxed_guide_flux=relaxed,
                initial_auxiliary_ADM=float(model.integrate(model.volume[0]*fields['delivery_drift050'][0,0])),
                maximum_work_identity_residual=work_error,
                maximum_stream_balance_residual=float(max(abs(row['balance_residual']) for row in local_balances)),
                ideal_route_remaining_force_max=float(abs(remainder[it,j])),
                ideal_route_force_peak_time=float((model.t[it]+model.t[it+1])/2),
                ideal_route_force_peak_x=float(model.x[j]),
                charge_material_and_contact_dynamics_supplied=False,thermal_coupling_included=False))
            balances.extend(local_balances)
        print(f'n{cells} geometry{subdivisions}: {family} transport complete',flush=True)
    stem=f'n{cells}_geometry{subdivisions}'
    write_json(OUTPUT/(stem+'_summary.json'),dict(cases=cases,attachment=attachment))
    pd.DataFrame(phase_rows).to_csv(OUTPUT/(stem+'_phases.csv'),index=False)
    pd.DataFrame(balances).to_csv(OUTPUT/(stem+'_balances.csv'),index=False)
    return cases


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--workers',type=int,default=3)
    args=parser.parse_args()
    if OUTPUT.exists():
        raise RuntimeError('preserve completed composite transport evidence')
    predecessor=BASE/'composite_capacitor/manifest.json'
    hashes=json.loads(predecessor.read_text())['input_sha256']
    for path in (Path(__file__),predecessor):
        hashes[str(path.relative_to(ROOT))]=sha256_file(path)
    for relative,expected in hashes.items():
        if sha256_file(ROOT/relative)!=expected:
            raise RuntimeError(f'input changed: {relative}')
    OUTPUT.mkdir(parents=True)
    with ProcessPoolExecutor(max_workers=min(3,args.workers),mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,((512,2),(1024,2),(1024,4))))
    if max(max(row['maximum_work_identity_residual'],row['maximum_stream_balance_residual'])
           for rows in results for row in rows)>1e-10:
        raise ArithmeticError('composite transport conservation failed')
    for relative,expected in hashes.items():
        if sha256_file(ROOT/relative)!=expected:
            raise RuntimeError(f'input changed during run: {relative}')
    write_json(OUTPUT/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes,
        output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__=='__main__':
    main()
