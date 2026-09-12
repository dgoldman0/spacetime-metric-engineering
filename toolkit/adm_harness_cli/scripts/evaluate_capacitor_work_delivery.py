#!/usr/bin/env python3
"""Optimistic joint electric/insulating-field work through the existing route.

Grants perfect local work cancellation and conversion, ideal absorption,
maximum allowed electric-to-guide sharing, and zero added heat inventory.
This determines whether the active insulation direction survives an unusually
favorable transport screen before constructing another physical converter.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import multiprocessing

import numpy as np
import pandas as pd

from adm_harness.charged_capacitor import magnetic_cell_work, transverse_magnetic_moments
from adm_harness.finite_work_interface import capacitor_step_work
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.poynting_delivery import propagate, wave_moments
from adm_harness.shared_field_delivery import radial_field_moments
from adm_harness.source_ledger import sha256_file
from evaluate_finite_work_interface import InterfaceHistory
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'charged_capacitor_work_delivery'


class GeometryTable:
    """Piecewise-linear geometry coefficients, independently refined in time."""
    def __init__(self, model, subdivisions):
        self.t = model.t
        self.subdivisions = subdivisions
        self.times = np.r_[np.concatenate([np.linspace(a, b, subdivisions+1)[:-1]
                         for a, b in zip(model.t[:-1], model.t[1:])]), model.t[-1]]
        self.data = {direction: [] for direction in (-1, 1)}
        for time in self.times:
            g = model.h.model.metric(float(time), model.x)
            edge = model.h.model.metric(float(time), model.h.edges)
            v = g.b*g.beta/g.alpha
            gamma = 1/np.sqrt(1-v*v)
            for direction in (-1, 1):
                self.data[direction].append((
                    -edge.beta+direction*edge.alpha/edge.b,
                    g.alpha*g.k_l-direction*g.alpha_x/g.b,
                    1/(gamma*(1-direction*v))))
        self.data = {d: tuple(np.array([row[k] for row in rows]) for k in range(3))
                     for d, rows in self.data.items()}

    def coefficients(self, direction, label_power):
        def evaluate(time, interval):
            offset = np.clip((time-self.t[interval])/(self.t[interval+1]-self.t[interval]), 0., 1.)*self.subdivisions
            local = min(int(offset), self.subdivisions-1)
            fraction = offset-local
            j = interval*self.subdivisions+local
            faces, gain, conversion = [(1-fraction)*a[j]+fraction*a[j+1] for a in self.data[direction]]
            return faces, gain, conversion*label_power[interval]
        return evaluate


def evaluate(spec):
    cells, subdivisions = spec
    model = InterfaceHistory(cells)
    geometry = GeometryTable(model, subdivisions)
    c = model.c
    cap = float(model.cap.max())
    unused, share, unused = model.allocation(cap)
    flux = model.hf-share
    ell, radius = c['gamma']*c['b'], c['radius']
    electric = flux/radius**4
    electric_work = capacitor_step_work(np.sqrt(2*flux[:-1]), np.sqrt(2*flux[1:]),
                                       (ell/radius**2)[:-1], (ell/radius**2)[1:])[0]
    magnetic_work_unit = magnetic_cell_work(electric, ell, radius)[0]
    summaries, phases, ledgers = [], [], []
    for drift in (1., .9, .7, .5):
        work = electric_work+magnetic_work_unit/drift**2
        power = work/np.diff(model.t)[:, None]
        streams = []
        for direction, supplied, backwards in ((-1, np.maximum(power, 0), True),
                                                (1, np.maximum(-power, 0), False)):
            history, ledger = propagate(model.t, model.h.edges,
                geometry.coefficients(direction, supplied), backwards=backwards)
            streams.append(history/model.volume)
            for row in ledger:
                row.update(drift=drift, direction=direction)
            ledgers.extend(ledger)
        minus, plus = streams
        peak = max(float(np.max(minus*c['gamma']**2*(1+c['v'])**2*radius**4)),
                   float(np.max(plus*c['gamma']**2*(1-c['v'])**2*radius**4)))
        # Paired radial delivery guides retain their previous 0.5 frame-speed
        # target. Insulation drift is the independent capacitor-cell setting.
        guide = max(cap, 2*1.03*1.5*peak)
        extra = (guide-share)/radius**4
        unguided = (wave_moments(plus, minus)
                    +transverse_magnetic_moments(electric/drift**2, c['v']))
        auxiliary = unguided+radial_field_moments(extra)
        # A separate optimistic relaxed guide uses a 0.9 electric-free frame
        # speed, to locate dependence on that engineering comparison.
        relaxed_guide = max(cap, 2*1.03*.5*(.9**-2-1)*peak)
        for name, field in (('delivery_drift050', auxiliary),
                            ('delivery_drift090', auxiliary+radial_field_moments((relaxed_guide-guide)/radius**4)),
                            ('guide_omitted_tensor_bound', unguided-radial_field_moments(share/radius**4))):
            for it, time, demand in model.phases:
                residual = model.supply[:, it]+field[:, it]-demand
                value, direction = maximum_null(residual)
                j = int(np.argmax(value))
                phases.append(dict(cells=cells, time_subdivisions=subdivisions, insulation_drift=drift,
                    route=name, time=time, required_negative_null=float(max(0., value.max())),
                    peak_x=float(model.x[j]), peak_null_cosine=float(direction[j]),
                    maximum_radial_null=float(np.max(residual[0]+residual[1]+2*abs(residual[2]))),
                    auxiliary_ADM=float(model.integrate(model.volume[it]*field[0, it]))))
        summaries.append(dict(cells=cells, time_subdivisions=subdivisions, insulation_drift=drift,
            electric_share_saturation_cap=cap, required_guide_flux=guide,
            relaxed_guide_flux=relaxed_guide,
            wave_driven_guide_flux=2*1.03*1.5*peak,
            initial_auxiliary_ADM=float(model.integrate(model.volume[0]*auxiliary[0, 0])),
            initial_wave_ADM=float(model.integrate(model.volume[0]*(plus[0]+minus[0]))),
            null_field_limit=bool(drift == 1.),
            initial_electric_rest=float(model.integrate(electric[0]*c['rest_volume'][0])),
            net_work_input=float(model.integrate(np.maximum(work, 0).sum(axis=0))),
            net_work_export=float(model.integrate(np.maximum(-work, 0).sum(axis=0))),
            maximum_stream_balance_residual=float(max(abs(row['balance_residual']) for row in ledgers)),
            maximum_rate_limited_share_is_covered=bool(guide >= cap)))
    stem = f'n{cells}_geometry{subdivisions}'
    write_json(OUTPUT/(stem+'_summary.json'), summaries)
    pd.DataFrame(phases).to_csv(OUTPUT/(stem+'_phases.csv'), index=False)
    pd.DataFrame(ledgers).to_csv(OUTPUT/(stem+'_balances.csv'), index=False)
    print(f'{stem}: joint capacitor work transport complete', flush=True)
    return summaries


def main():
    if OUTPUT.exists():
        raise RuntimeError('preserve the joint capacitor transport evidence')
    OUTPUT.mkdir(parents=True)
    with ProcessPoolExecutor(max_workers=4, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(evaluate, ((512, 2), (1024, 2), (1024, 4))))
    if max(row['maximum_stream_balance_residual'] for result in results for row in result) > 1e-10:
        raise ArithmeticError('joint work transport energy balance failed')
    write_json(OUTPUT/'summary.json', dict(cases=[row for result in results for row in result],
        concessions=['Perfect local electric/magnetic work cancellation and conversion',
                     'Ideal matched absorption, no extra heat receiver tensor',
                     'Maximum allowed electric sharing, protected patch and old material history',
                     'Boundary, transverse-current, confinement and earlier-preparation costs omitted']))
    source = json.loads((BASE/'charged_capacitor_insulation/manifest.json').read_text())['input_sha256']
    source[str(Path(__file__).relative_to(ROOT))] = sha256_file(Path(__file__))
    source[str((BASE/'charged_capacitor_insulation/manifest.json').relative_to(ROOT))] = sha256_file(BASE/'charged_capacitor_insulation/manifest.json')
    for name, expected in source.items():
        if sha256_file(ROOT/name) != expected:
            raise ArithmeticError(f'input changed: {name}')
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        input_sha256=source,
        output_sha256={p.name: sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
