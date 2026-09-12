#!/usr/bin/env python3
"""Independent dense work reconstruction, member cost, and end-load audit."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import multiprocessing
import subprocess
import time

import numpy as np
from numpy.polynomial.legendre import leggauss

from adm_harness.composite_capacitor import anisotropic_moments
from adm_harness.conserved_radial_prestress import admissible_amplitude, minimum_member_fraction
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.integrated_support_energy import IntegratedEnergy
from adm_harness.source_ledger import sha256_file
from adm_harness.surface_support_termination import minimum_surface_inventory
from audit_joint_support import bilinear
from run_joint_response_family import ResponseFamily
from run_joint_route_momentum_gate import RoutedHistory
from run_joint_route_response import routed_coefficients
from run_joint_time_projected_candidate import ProjectionHistory
from run_joint_spacetime_support import assemble_fixed
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'joint_dense_work_audit'


class DenseHistory:
    def __init__(self, kind, path):
        with np.load(path) as z: self.state = {k:z[k] for k in z.files}
        self.kind = kind
        if kind == 'fixed':
            self.source = ProjectionHistory(); self.coefficients = self.source.coefficients
        elif kind == 'route':
            summary = json.loads(path.with_name('summary.json').read_text())
            self.source = RoutedHistory((summary['absorption_left_fraction'], summary['recovery_left_fraction']))
            self.coefficients = self.source.coefficients
        else:
            self.source = ResponseFamily(); controls = self.state['parameters']
            if kind == 'family':
                self.coefficients = lambda t,x:self.source.selected_coefficients(controls, t, x)
            elif kind == 'routed_family':
                self.coefficients = lambda t,x:routed_coefficients(self.source, controls, t, x)
            else: raise ValueError('registered history kind required')
        self.h = self.source.h
        self.edges = np.unique(np.r_[self.state['t'], self.h.reference.h.state['t']])

    def pressure(self, t, x):
        s = self.state
        return bilinear(s['t'], s['x'], s['radial_pressure'], t, x)

    def energy(self, x):
        initial = np.interp(x, self.state['x'], self.state['support_energy'][0])
        def rhs(times):
            rows = []
            for begin in range(0, len(times), 48):
                t = times[begin:begin+48]; c = self.coefficients(t, x)
                p = self.pressure(t, x)[0]
                rows.append(-c['D']*p*c['log_ell_t']-2*c['Q']*c['log_radius_t']-
                            c['lapse']*c['D']*c['fixed_power'])
            return np.concatenate(rows)
        return IntegratedEnergy(self.edges, initial, rhs)


def surface_gate(history, amplitude=0.):
    t = history.edges; x = history.state['x'][[0, -1]]
    c = history.coefficients(t, x); p = history.pressure(t, x)[0]-amplitude/c['radius']**2
    old = history.h.reference.h.state
    u = bilinear(old['t'], old['x'], old['thermal'], t, x)[0]
    field = bilinear(old['t'], old['x'], old['flux_energy'], t, x)[0]
    electric = (field-history.h.allocation(x)[0])/c['radius']**4
    rows = []
    for j, sign in enumerate((-1., 1.)):
        result = minimum_surface_inventory(t, c['radius'][:,j], c['acceleration'][:,j],
            c['angular_gradient'][:,j], p[:,j]+u[:,j]/(3*c['D'][:,j])-electric[:,j],
            outward_sign=sign)
        rows.append(dict(end=('left', 'right')[j], **{k:v for k,v in result.items() if not isinstance(v,np.ndarray)}))
    return rows


def source_phases(history, amplitude=0.):
    if history.kind in ('route', 'routed_family'): return None
    x = history.state['x']; h = history.h
    times = np.array([row[1] for row in h.reference.phases]); c = history.coefficients(times, x)
    mass = history.energy(x).evaluate(times)[0]+amplitude*c['ell']
    pressure = history.pressure(times, x)[0]-amplitude/c['radius']**2
    old = h.reference.h.state
    u = bilinear(old['t'], old['x'], old['thermal'], times, x)[0]
    n = np.interp(x, old['x'], old['number'])
    tensor = anisotropic_moments((n+u+mass)/c['D'], u/(3*c['D'])+pressure,
                                 (u/3+c['Q'])/c['D'], c['v'])
    fixed, unused = assemble_fixed(h, times, x, c); rows = []
    for i, (unused, now, demand) in enumerate(h.reference.phases):
        geom = np.array([np.interp(x, h.reference.x, row) for row in demand])
        val = maximum_null(tensor[:,i]+fixed[:,i]-geom)[0]
        rows.append(dict(time=now, required_negative_null=float(val.max())))
    return rows


def evaluate(spec):
    kind, relative = spec; start = time.monotonic(); path = BASE/relative
    history = DenseHistory(kind, path); state = history.state
    label = path.parent.name+'_'+path.stem
    xe = np.unique(np.r_[state['x'], history.h.reference.h.state['x']])
    z, w = leggauss(3)
    x = (xe[:-1,None]+np.diff(xe)[:,None]*(z+1)/2).ravel()
    # Include the physical cuts in every member and prestress gate.
    x = np.r_[xe[0], x, xe[-1]]
    wx = np.r_[0., (np.diff(xe)[:,None]*w/2).ravel(), 0.]
    te = history.edges
    quadrature = (te[:-1,None]+np.diff(te)[:,None]*(z+1)/2).ravel()
    times = np.r_[quadrature, te]; wt = np.r_[(np.diff(te)[:,None]*w/2).ravel(), np.zeros(len(te))]
    order = np.argsort(times); times = times[order]; wt = wt[order]
    energy = history.energy(x)
    nf = npow = df = dp = 0.; maximum_force = maximum_power = maximum_change = 0.
    max_shortfall = -np.inf; min_rho = np.inf; witness = None; rows = []
    for begin in range(0, len(times), 24):
        t = times[begin:begin+24]; c = history.coefficients(t, x)
        m, mt = energy.evaluate(t); p, pt, px = history.pressure(t, x)
        q = c['Q']/c['D']; rho = m/c['D']
        inertia = (rho+p)*c['acceleration']; temporal = c['v']/c['lapse']*pt
        gradient = px/c['ell']; angular = 2*(p-q)*c['angular_gradient']
        support_power = (mt+c['D']*p*c['log_ell_t']+2*c['Q']*c['log_radius_t'])/(c['lapse']*c['D'])
        force = inertia+temporal+gradient+angular+c['fixed_force']; power = support_power+c['fixed_power']
        measure = wt[begin:begin+24,None]*wx[None,:]*c['lapse']*c['D']
        nf += np.sum(measure*abs(force)); npow += np.sum(measure*abs(power))
        df += np.sum(measure*(abs(inertia)+abs(temporal)+abs(gradient)+abs(angular)+
                              sum(abs(c[k]) for k in ('fluid_force','field_force','wave_force','heat_force'))))
        dp += np.sum(measure*(abs(support_power)+
                              sum(abs(c[k]) for k in ('fluid_power','field_power','wave_power','heat_power'))))
        maximum_force = max(maximum_force, float(abs(force).max()))
        maximum_power = max(maximum_power, float(abs(power).max()))
        original = bilinear(state['t'], state['x'], state['support_energy'], t, x)[0]
        maximum_change = max(maximum_change, float((abs(m-original)/c['D']).max()))
        shortfall = abs(p)+np.maximum(-q, 2*q)-rho
        if shortfall.max() > max_shortfall:
            i,j = np.unravel_index(np.argmax(shortfall),shortfall.shape)
            max_shortfall = float(shortfall[i,j])
            witness = dict(time=float(t[i]), x=float(x[j]), density=float(rho[i,j]),
                           radial_pressure=float(p[i,j]), angular_pressure=float(q[i,j]))
        min_rho = min(min_rho, float(rho.min()))
        rows.append((c['radius'].ravel(), rho.ravel(), p.ravel(), q.ravel()))
    arrays = tuple(np.concatenate([row[i] for row in rows]) for i in range(4))
    del rows
    amplitudes = {str(f):admissible_amplitude(*arrays, f) for f in (1., .9999, .999, .99, .95, .9, .75)}
    threshold = minimum_member_fraction(*arrays)
    summary = dict(label=label, kind=kind, input=str(path.relative_to(ROOT)),
        weighted_force_residual=float(nf/df), weighted_power_residual=float(npow/dp),
        maximum_force_residual=maximum_force, maximum_power_residual=maximum_power,
        maximum_work_reconstruction_density_change=maximum_change,
        maximum_member_density_shortfall=max(0.,max_shortfall), minimum_density=min_rho,
        worst_member_witness=witness, member_energy_admissible=bool(max_shortfall<1e-7 and min_rho>=0),
        sampled_prestress_intervals=amplitudes, minimum_prestress_member_fraction=threshold,
        end_jackets=surface_gate(history), source_phases=source_phases(history),
        temporal_samples=len(times), spatial_samples=len(x),
        constitutive_law_supplied=False, full_construction_supplied=False)
    if amplitudes['1.0']['feasible']:
        A = amplitudes['1.0']['lower']
        c0 = history.coefficients(np.array([te[0]]), state['x'])
        summary['minimum_conserved_prestress'] = dict(amplitude=A,
            added_initial_rest=float(4*np.pi*A*np.trapezoid(c0['ell'][0],state['x'])),
            end_jackets=surface_gate(history,A), source_phases=source_phases(history,A),
            radial_null_change=0., physical_material_supplied=False)
    summary['elapsed_seconds'] = time.monotonic()-start
    write_json(OUTPUT/(label+'_summary.json'), summary)
    print(label+': '+json.dumps(summary), flush=True)
    return summary


def main():
    if OUTPUT.exists(): raise RuntimeError('preserve completed dense work evidence')
    specs = [('fixed','joint_time_projected_candidate/n256_timefactor2_states.npz'),
             ('route','joint_route_momentum_gate/selected_states.npz'),
             ('family','joint_response_relaxation/fraction1_unbounded_states.npz')]
    route_summary = BASE/'joint_route_response/summary.json'
    if route_summary.exists():
        for row in json.loads(route_summary.read_text())['cases']:
            if row['success']: specs.append(('routed_family','joint_route_response/'+row['label']+'_states.npz'))
    sources = [Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/integrated_support_energy.py',
               ROOT/'toolkit/adm_harness_cli/adm_harness/conserved_radial_prestress.py',
               Path(__file__).with_name('run_joint_route_response.py'),
               Path(__file__).with_name('run_joint_route_momentum_gate.py')]
    hashes = {}
    for unused, relative in specs:
        p = BASE/relative; manifest = p.parent/'manifest.json'
        hashes.update(json.loads(manifest.read_text())['input_sha256']); sources.extend([p,manifest])
    for p in sources: hashes[str(p.relative_to(ROOT))] = sha256_file(p)
    for p, expected in hashes.items():
        if sha256_file(ROOT/p) != expected: raise RuntimeError('changed dense work input: '+p)
    OUTPUT.mkdir()
    with ProcessPoolExecutor(max_workers=2, mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(evaluate, specs))
    write_json(OUTPUT/'summary.json', dict(cases=results))
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes, output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__ == '__main__': main()
