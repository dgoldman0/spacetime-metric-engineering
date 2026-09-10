#!/usr/bin/env python3
"""Bounded recovery policy and field-drift tradeoff for the work interface."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import multiprocessing
import subprocess

import numpy as np
import pandas as pd
from scipy.optimize import brentq, minimize_scalar

from adm_harness.finite_work_interface import reflected_guide_factor
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.poynting_delivery import wave_moments
from adm_harness.regenerative_converter import compact_cell_moments, proper_prefix
from adm_harness.shared_field_delivery import average_electric_rate, radial_field_moments
from adm_harness.source_ledger import sha256_file
from evaluate_finite_work_interface import InterfaceHistory, OUTPUT as INPUT_DIR, port_audit
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'finite_work_interface_recovery'


def recovery_state(model, fraction):
    """Constant recovered fraction; the established heat return takes the balance.

All remaining electric duty and the fluid's net energy exchange are fixed.
The reduced return wave and extra receiver heat conserve exactly the lost
electrical recovery at each material label in the quadrature representation.
"""
    if not 0 <= fraction <= 1:
        raise ValueError('finite recovered fraction required')
    c, cm = model.c, model.cm
    minus = model.absorption+model.free_minus
    plus = fraction*model.recovery+model.free_plus
    extra_heat = proper_prefix(model.t, cm['lapse']*cm['rest_volume'],
                              .98*(1-fraction)*model.negative)
    heat_unshifted = model.old_heat+extra_heat
    heat = heat_unshifted-heat_unshifted.min(axis=0)
    heat_cap = np.ptp(heat_unshifted, axis=0)
    if fraction == 1:
        heat, heat_cap = model.old_heat.copy(), model.old_heat_cap.copy()
    forward = minus*c['gamma']**2*(1+c['v'])**2*c['radius']**4
    returning = plus*c['gamma']**2*(1-c['v'])**2*c['radius']**4
    peak = max(forward.max(), returning.max())
    flux = 2*1.03*reflected_guide_factor(0)*peak
    check_share, share, derivative = model.allocation(flux)
    auxiliary = (wave_moments(plus, minus)+compact_cell_moments(heat+heat_cap/3, c)
                 +radial_field_moments((flux-share)/c['radius']**4))
    return dict(minus=minus, plus=plus, flux=flux, share=share, check_share=check_share,
                derivative=derivative, heat=heat, heat_cap=heat_cap, auxiliary=auxiliary,
                initial=float(model.integrate(model.volume[0]*auxiliary[0, 0])),
                extra_heat=float(model.integrate(extra_heat[-1])),
                heat_capacity=float(model.integrate(heat_cap)),
                forward_guide_peak=float(forward.max()), return_guide_peak=float(returning.max()))


def evaluate(cells):
    model = InterfaceHistory(cells)
    optimum = minimize_scalar(lambda f: recovery_state(model, f)['initial'], bounds=(.7, .999999),
                              method='bounded', options={'xatol': 1e-8})
    fractions = sorted(set((1., .98, .95, .9, .8, .7, float(optimum.x))))
    rows, phases = [], []
    for fraction in fractions:
        state = recovery_state(model, fraction)
        row = {key: state[key] for key in ('initial', 'extra_heat', 'heat_capacity',
               'flux', 'forward_guide_peak', 'return_guide_peak')}
        row.update(cells=cells, recovery_fraction=fraction)
        rows.append(row)
        for it, time, demand in model.phases:
            val = maximum_null(model.supply[:, it]+state['auxiliary'][:, it]-demand)[0]
            phases.append(dict(cells=cells, recovery_fraction=fraction, time=time,
                               required_negative_null=float(max(0., val.max()))))
    # Fully recovered nominal case must exactly reproduce the pinned route.
    original, control = model.state(.98), recovery_state(model, 1.)
    residual = float(np.max(abs(original['auxiliary']-control['auxiliary'])))
    if residual > 1e-12:
        raise ArithmeticError('full-recovery control changed')
    # Keep the source comparison alongside startup energy: f=.9 avoids most
    # of the return-driven guide increment with a smaller fade penalty than
    # the optimum of startup energy alone. The full tradeoff remains recorded.
    selected_fraction = .9
    state = recovery_state(model, selected_fraction)
    ports, port_rows = port_audit(model, state)
    cm = model.cm
    wave_force = model.positive/.98+.98*selected_fraction*model.negative
    heat_force = ((state['heat'][1:]+state['heat'][:-1])/2+state['heat_cap']/3)/cm['rest_volume']*cm['acceleration']
    extra_field_force = state['derivative']/(cm['gamma']*cm['b']*cm['radius']**4)
    endpoint_force = cm['gamma']*(cm['normal_force']-cm['v']*cm['power'])
    remainder = endpoint_force-wave_force-heat_force-extra_field_force
    checked_electric = model.check_h-state['check_share']
    rate = float(average_electric_rate(model.t, checked_electric, model.check_c['lapse']).max())
    if rate > 1+1e-7 or checked_electric.min() <= 0:
        raise ArithmeticError('selected recovery allocation violates electric response')
    envelopes = []
    c = model.c
    peak = max(state['forward_guide_peak'], state['return_guide_peak'])
    for drift in (.5, .55, .6):
        for amplitude in (0., .01, .02, .05, .1):
            new_flux = 2*1.03*reflected_guide_factor(amplitude, drift)*peak
            unused, new_share, unused_derivative = model.allocation(new_flux)
            guide_delta = ((new_flux-new_share)-(state['flux']-state['share']))/c['radius'][0]**4
            initial = state['initial']+float(model.integrate(model.volume[0]*guide_delta))
            envelopes.append(dict(drift_comparison=drift, reflected_amplitude=amplitude,
                auxiliary_energy_with_guide_margin=initial, guide_flux=new_flux,
                calculation='Field envelope; reflected propagation and plasma dynamics remain separate'))
    # Hold the guide fixed. This follows from E/B at the worst coherent phase;
    # the 3% guide margin is retained as an actual field, not silently discarded.
    fixed_guide = []
    for amplitude in (0., .01, .02, .05, .1):
        speed = (1+amplitude)/np.sqrt((1-amplitude)**2+3*1.03)
        fixed_guide.append(dict(reflected_amplitude=amplitude, field_drift=speed,
            meaning='Minimum E=0 frame speed; no maximum particle speed established'))
    write_json(OUTPUT/f'n{cells}_summary.json', dict(cases=rows, phases=phases,
        startup_only_optimum_recovery_fraction=float(optimum.x), selected_recovery_fraction=selected_fraction,
        full_recovery_tensor_residual=residual, maximum_electric_rate=rate,
        minimum_electric_flux_energy=float(checked_electric.min()),
        maximum_endpoint_force_remainder=float(abs(remainder).max()),
        maximum_heat_holding_force=float(abs(heat_force).max()),
        capacitor_port=ports, fixed_guide_reflection_drift=fixed_guide))
    pd.DataFrame(envelopes).to_csv(OUTPUT/f'n{cells}_drift_envelopes.csv', index=False)
    pd.DataFrame(port_rows).to_csv(OUTPUT/f'n{cells}_capacitive_ports.csv', index=False)
    np.savez_compressed(OUTPUT/f'n{cells}_selected_states.npz', t=model.t, x=model.x,
        mu_minus=state['minus'], mu_plus=state['plus'], guide_flux=state['flux'],
        shared_flux=state['share'], heat=state['heat'], heat_capacity=state['heat_cap'],
        recovery_fraction=selected_fraction, endpoint_force_remainder=remainder)
    print(f'recovery n={cells}: f={selected_fraction:.7f}, initial={state["initial"]:.7f}, '
          f'extra heat={state["extra_heat"]:.7f}', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if OUTPUT.exists():
        raise RuntimeError('preserve completed recovery-policy evidence')
    import json
    preceding = json.loads((INPUT_DIR/'manifest.json').read_text())
    sources = [ROOT/name for name in preceding['input_sha256']]
    sources += [Path(__file__), Path(__file__).with_name('evaluate_finite_work_interface.py'),
                INPUT_DIR/'manifest.json']
    before = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    OUTPUT.mkdir(parents=True)
    with ProcessPoolExecutor(max_workers=min(args.workers, 4), mp_context=multiprocessing.get_context('spawn')) as pool:
        list(pool.map(evaluate, (512, 1024)))
    if before != {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}:
        raise RuntimeError('input changed during recovery comparison')
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        input_sha256=before,
        output_sha256={p.name: sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
