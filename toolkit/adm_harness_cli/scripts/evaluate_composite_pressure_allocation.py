#!/usr/bin/env python3
"""Allow arbitrary resolved pressure sharing in the fade force comparison.

For a closed DEC-balanced capacitor let r=p-p_used be the pressure left in
the original fluid. Then max(p-u_E,0)<=r<=p, and the complete material has
rho+pr>=n+4p+2u_E, independent of the allocation. Positive acceleration gives
r_x <= -Gamma*B*a*(n+4p+2u_E) - Gamma*B*v*r_t/N. The final time coefficient
is extremely small. Its most favorable possible contribution is retained
for pressure histories linear across the final archived time interval.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import multiprocessing

import numpy as np
import pandas as pd
from scipy.integrate import cumulative_trapezoid

from adm_harness.active_transfer_reservoir import smooth_rise
from adm_harness.pressure_linked_storage import fluid_coefficients
from adm_harness.shared_field_delivery import smooth_under_cap
from adm_harness.source_ledger import sha256_file
from evaluate_finite_work_interface import InterfaceHistory
from evaluate_recovery_work_interface import recovery_state
from run_poynting_delivery import BASE,ROOT,write_json

OUTPUT=BASE/'composite_capacitor_pressure_allocation'


def bounded_drop_witness(x,lower,upper,required_drop_density,applicable):
    """Largest contradiction to r_x<=-drive within a connected valid interval.

    For every left/right pair, integral(drive)<=upper(left)-lower(right)
    is necessary. Prefix minima find the strongest pair in linear time.
    """
    x,lower,upper,drive,mask=map(np.asarray,(x,lower,upper,required_drop_density,applicable))
    if np.any(np.diff(x)<=0) or np.any(lower>upper):
        raise ValueError('ordered grid and consistent pressure bounds required')
    best=dict(gap=-np.inf)
    indices=np.flatnonzero(mask)
    for segment in np.split(indices,np.flatnonzero(np.diff(indices)>1)+1):
        if len(segment)<2:
            continue
        total=cumulative_trapezoid(drive[segment],x[segment],initial=0.)
        top=upper[segment]+total
        slack=lower[segment]+total-np.minimum.accumulate(top)
        j=int(np.argmax(slack))
        i=int(np.argmin(top[:j+1]))
        if slack[j]>best['gap']:
            best=dict(gap=float(slack[j]),left_index=int(segment[i]),right_index=int(segment[j]),
                left_x=float(x[segment[i]]),right_x=float(x[segment[j]]),
                required_pressure_drop=float(total[j]-total[i]),
                maximum_available_pressure_drop=float(upper[segment[i]]-lower[segment[j]]))
    if not np.isfinite(best['gap']):
        raise ValueError('no resolved applicable interval')
    return best


def evaluate(spec):
    pinned,cells=spec
    model=InterfaceHistory(pinned)
    state=recovery_state(model,1.)
    st=model.h.state;knots=st['x']
    edges=np.linspace(knots[0],knots[-1],cells+1);x=(edges[1:]+edges[:-1])/2
    unused,unused,values=smooth_under_cap(model.check_x,np.minimum(state['flux'],model.cap),knots)
    ix=np.clip(np.searchsorted(knots,x,side='right')-1,0,len(knots)-2)
    rise,unused=smooth_rise((x-knots[ix])/(knots[ix+1]-knots[ix]))
    share=values[ix]+(values[ix+1]-values[ix])*rise
    c=fluid_coefficients(model.h.model,model.t[-2:],x)
    thermal=np.array([np.interp(x,knots,row) for row in st['thermal'][-2:]])
    p=thermal/(3*c['rest_volume'])
    n=np.interp(x,knots,st['number'])/c['rest_volume'][-1]
    ue=(np.interp(x,knots,st['flux_energy'][-1])-share)/c['radius'][-1]**4
    lower=np.maximum(p[-1]-ue,0.);upper=p[-1]
    ell=c['gamma'][-1]*c['b'][-1]
    acceleration=c['acceleration'][-1]
    drive=ell*acceleration*(n+4*p[-1]+2*ue)
    time_coefficient=ell*c['v'][-1]/c['lapse'][-1]
    # Grants independently maximal help from a pressure derivative at every
    # point, before enforcing any joint EOS or energy schedule.
    derivative_bound=np.max(p,axis=0)/(model.t[-1]-model.t[-2])
    temporal_allowance=abs(time_coefficient)*derivative_bound
    mask=acceleration>0
    witness=bounded_drop_witness(x,lower,upper,drive-temporal_allowance,mask)
    i,j=witness['left_index'],witness['right_index']
    result=dict(pinned_cells=pinned,evaluation_cells=cells,time=float(model.t[-1]),**witness,
        maximum_fade_material_speed=float(abs(c['v'][-1]).max()),
        interval_minimum_acceleration=float(acceleration[i:j+1].min()),
        integrated_temporal_allowance=float(np.trapezoid(temporal_allowance[i:j+1],x[i:j+1])),
        omitted_positive_costs=['charge-carrier excess energy','heat receiver','work-wave momentum','extra retained support energy'],
        temporal_scope='Arbitrary pressure allocation at archived times, linear across the final interval; no subinterval pulses.')
    stem=f'pinned{pinned}_sample{cells}'
    write_json(OUTPUT/(stem+'_summary.json'),result)
    pd.DataFrame(dict(x=x,lower_free_pressure=lower,upper_free_pressure=upper,
        required_drop_density=drive,optimistic_temporal_allowance=temporal_allowance,
        positive_acceleration=mask)).to_csv(OUTPUT/(stem+'_pressure.csv'),index=False)
    return result


def main():
    if OUTPUT.exists():
        raise RuntimeError('preserve completed pressure-allocation evidence')
    predecessor=BASE/'composite_capacitor/manifest.json'
    hashes=json.loads(predecessor.read_text())['input_sha256']
    for path in (Path(__file__),predecessor,
                 ROOT/'toolkit/adm_harness_cli/tests/test_composite_pressure_allocation.py'):
        hashes[str(path.relative_to(ROOT))]=sha256_file(path)
    for path,expected in hashes.items():
        if sha256_file(ROOT/path)!=expected:
            raise RuntimeError(f'changed pressure witness input: {path}')
    OUTPUT.mkdir(parents=True)
    with ProcessPoolExecutor(max_workers=3,mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,((512,512),(1024,1024),(1024,4096))))
    write_json(OUTPUT/'summary.json',dict(cases=results))
    write_json(OUTPUT/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),input_sha256=hashes,
        output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))
    print('resolved pressure-allocation bound complete',flush=True)


if __name__=='__main__':
    main()
