"""Loaded screened condensate exterior and its inward material continuation.

The exterior boundary data select a conditional solution. A complete source
also needs a regular continuation of all scalar and gauge Cauchy data through
the retained interior, followed by the quantum and perturbation calculations.
"""
from dataclasses import dataclass
import json
from pathlib import Path
import time

import numpy as np
from scipy.integrate import solve_bvp, solve_ivp

from .curved_boundary import StaticGeometry
from .screened_condensate import CondensateParameters, field_stress, gravitating_rhs
from .source_ledger import sha256_file


@dataclass(frozen=True)
class ExteriorBoundary:
    physical_radius: float = 6.8
    inner_radius: float = 20.
    inner_mass: float = (1.75/6.8)**2*10.
    inner_lapse_gradient: float = 0.  # d log(alpha) / d(v*r)
    matter_amplitude: float = 1.
    higgs_amplitude: float = .05
    radial_pressure: float = -.125

    @property
    def vacuum_scale(self):
        return self.inner_radius/self.physical_radius

    @property
    def inner_f(self):
        return 1-2*self.inner_mass/self.inner_radius

    @property
    def gravity(self):
        r = self.inner_radius
        return (r*r*self.inner_f*self.inner_lapse_gradient-self.inner_mass)/(4*np.pi*r**3*self.radial_pressure)

    @classmethod
    def from_geometry(cls, geometry, physical_radius=6.8, inner_radius=20., **kwargs):
        x = float(geometry.negative_branch_coordinate(physical_radius))
        r, _, scale = geometry.values(x)
        rlog, alog, _ = geometry.values(x, 1)
        f = float((r*rlog/scale)**2)
        v = inner_radius/physical_radius
        return cls(physical_radius=physical_radius, inner_radius=inner_radius,
            inner_mass=inner_radius*(1-f)/2,
            inner_lapse_gradient=float(alog/(r*rlog*v)), **kwargs)


def load_retained_geometry(root):
    """Read and verify the existing frozen geometry, without regenerating it."""
    root = Path(root)
    cache = root/'supporting_reports/data/curved_quantum_boundary/geometry.npz'
    metadata = json.loads(cache.with_suffix('.json').read_text())
    if sha256_file(cache) != metadata['cache_sha256']:
        raise RuntimeError('retained geometry cache hash mismatch')
    for name, expected in metadata['source_hashes'].items():
        if sha256_file(root/name) != expected:
            raise RuntimeError('retained geometry source mismatch: '+name)
    with np.load(cache) as data:
        return StaticGeometry(**dict(data))


def boundary_residual(left, right, omega, boundary, parameters):
    t = field_stress(left[:6], omega, parameters,
        1-2*left[6]/boundary.inner_radius, np.exp(left[7]))
    return np.array([left[0]-boundary.matter_amplitude,
        left[2]-boundary.higgs_amplitude, left[5],
        t['radial_pressure']-boundary.radial_pressure,
        left[6]-boundary.inner_mass, right[0], right[2]-1, right[4], right[7]])


def _trial_rhs(radius, fields, omega, gravity, parameters):
    # Newton trial iterates can leave the static chart. Protect their evaluation;
    # every accepted profile is checked against the original, unclipped equations.
    trial = fields.copy()
    trial[6] = np.minimum(trial[6], .5*radius*(1-1e-7))
    trial[7] = np.clip(trial[7], -20, 20)
    return gravitating_rhs(radius, trial, omega, gravity, parameters)


def validate_exterior(solution, boundary, parameters, gravity):
    # Quarter cells are independent of the endpoint/midpoint collocation equations.
    delta = np.diff(solution.x)
    r = np.unique(np.r_[solution.x, solution.x[:-1]+.25*delta, solution.x[:-1]+.75*delta])
    y = solution.sol(r)
    f = 1-2*y[6]/r
    if (not solution.success or not np.isfinite(y).all() or np.min(f) <= 1e-7
            or np.max(abs(y[7])) >= 20 or not 0 < solution.p[0] < np.sqrt(parameters.matter_coupling)):
        raise RuntimeError('exterior relaxation failed its physical chart or branch check')
    rhs = gravitating_rhs(r, y, solution.p[0], gravity, parameters)
    error = np.max(abs(solution.sol(r, 1)-rhs)/(1+abs(rhs)))
    bc = np.max(abs(boundary_residual(y[:, 0], y[:, -1], solution.p[0], boundary, parameters)))
    return {'maximum_original_equation_error': float(error),
            'maximum_boundary_error': float(bc), 'minimum_f': float(np.min(f))}


def solve_auxiliary(boundary, parameters, extent=160.):
    """Fixed-Schwarzschild numerical seed, before material gravity is turned on."""
    r = np.linspace(boundary.inner_radius, extent, 1001)
    omega = .9
    step = np.exp(-(r-r[0])/8)
    u = boundary.matter_amplitude*step
    h = 1-(1-boundary.higgs_amplitude)*step
    a = omega/parameters.charge*u*u/(u*u+h*h)
    guess = np.array([u, np.gradient(u, r), h, np.gradient(h, r), a, np.gradient(a, r)])

    def rhs(r, y, frequency):
        full = np.vstack((y, np.full(len(r), boundary.inner_mass), np.zeros(len(r))))
        return gravitating_rhs(r, full, frequency[0], 0., parameters)[:6]

    def bc(left, right, frequency):
        full_left = np.r_[left, boundary.inner_mass, 0.]
        full_right = np.r_[right, boundary.inner_mass, 0.]
        residual = boundary_residual(full_left, full_right, frequency[0], boundary, parameters)
        return residual[[0, 1, 2, 3, 5, 6, 7]]

    solution = solve_bvp(rhs, bc, r, guess, p=[omega], tol=2e-5, max_nodes=20000)
    if not solution.success:
        raise RuntimeError('auxiliary branch location failed: '+solution.message)
    return solution


def continue_gravity(boundary, parameters, extent=160.):
    initial = solve_auxiliary(boundary, parameters, extent)
    r = np.linspace(boundary.inner_radius, extent, 2001)
    y = np.vstack((initial.sol(r), np.full(len(r), boundary.inner_mass), np.zeros(len(r))))
    omega = initial.p[0]
    fraction, target, step = 0., 0., .01
    trace, last = [], None
    for _ in range(70):
        started = time.monotonic()
        with np.errstate(over='ignore', invalid='ignore', divide='ignore'):
            s = solve_bvp(lambda r, y, p: _trial_rhs(r, y, p[0], target*boundary.gravity, parameters),
                lambda l, r, p: boundary_residual(l, r, p[0], boundary, parameters),
                r, y, p=[omega], tol=2e-6, max_nodes=30000)
        row = {'gravity_fraction': target, 'solver_success': bool(s.success),
            'status': int(s.status), 'nodes': len(s.x), 'seconds': time.monotonic()-started}
        try:
            checks = validate_exterior(s, boundary, parameters, target*boundary.gravity)
            accepted = checks['maximum_original_equation_error'] < 1e-4 and checks['maximum_boundary_error'] < 1e-5
            row.update(checks)
        except (RuntimeError, ValueError):
            accepted = False
        row['accepted'] = accepted
        trace.append(row)
        if accepted:
            last, fraction, omega = s, target, s.p[0]
            if target == 1.:
                return s, trace
            y = s.sol(r)
            step = min(step*1.3, .05)
            target = min(1., fraction+step)
        else:
            step *= .5
            if last is None or step < 2e-5:
                break
            target = fraction+step
    raise RuntimeError('bounded gravitational continuation exhausted before full coupling')


def refine_exterior(seed, boundary, parameters, tolerance=1e-8, extent=160., points=2001):
    if extent < seed.x[-1] or tolerance <= 0 or points < 201:
        raise ValueError('positive tolerance, sufficient mesh and unshortened exterior required')
    r = np.linspace(boundary.inner_radius, extent, points)
    y = seed.sol(np.minimum(r, seed.x[-1]))
    outside = r > seed.x[-1]
    y[:, outside] = np.array([0., 0., 1., 0., 0., 0., seed.y[6, -1], 0.])[:, None]
    s = solve_bvp(lambda r, y, p: _trial_rhs(r, y, p[0], boundary.gravity, parameters),
        lambda l, r, p: boundary_residual(l, r, p[0], boundary, parameters),
        r, y, p=seed.p, tol=tolerance, max_nodes=40000)
    checks = validate_exterior(s, boundary, parameters, boundary.gravity)
    if checks['maximum_original_equation_error'] > 20*tolerance or checks['maximum_boundary_error'] > 10*tolerance:
        raise RuntimeError('original exterior equations or boundary conditions exceed tolerance')
    return s


class InteriorMetric:
    """Analytic tail control or retained rail snapshot, with matched clock scale."""
    def __init__(self, kind, geometry, boundary, inner_log_sigma):
        if kind not in ('analytic', 'retained'):
            raise ValueError('choose analytic or retained interior geometry')
        self.kind, self.geometry = kind, geometry
        self.alpha_inner = np.exp(inner_log_sigma)*np.sqrt(boundary.inner_f)
        self.throat = geometry.throat_parameter
        if kind == 'analytic':
            self.start = -np.sqrt(boundary.physical_radius**2-self.throat**2)
            self.lapse_norm = 1.
        else:
            self.start = float(geometry.negative_branch_coordinate(boundary.physical_radius))
            self.lapse_norm = float(geometry.values(self.start)[1])

    def values(self, coordinate):
        if self.kind == 'analytic':
            r = np.sqrt(coordinate**2+self.throat**2)
            return r, self.alpha_inner, 1., coordinate/(r*r), 0., 0.
        r, a, b = self.geometry.values(coordinate)
        dr, da, db = self.geometry.values(coordinate, 1)
        return float(r), float(self.alpha_inner*a/self.lapse_norm), float(b), float(dr), float(da), float(db)


def interior_rhs(coordinate, fields, omega, vacuum_scale, parameters, metric):
    u, up, h, hp, a, ap = fields
    _, alpha, radial_scale, rlog, alog, blog = metric.values(coordinate)
    e, lam, mu = parameters.charge, parameters.higgs_coupling, parameters.matter_coupling
    scalar_friction = 2*rlog+alog-blog
    gauge_friction = 2*rlog-alog-blog
    scale = (radial_scale*vacuum_scale)**2
    return np.array([up, -scalar_friction*up+scale*(mu*h*h-(omega-e*a)**2/alpha**2)*u,
        hp, -scalar_friction*hp+scale*(mu*u*u+lam*(h*h-1)/2-e*e*a*a/alpha**2)*h,
        ap, -gauge_friction*ap+scale*(2*e*e*a*(u*u+h*h)-2*e*omega*u*u)])


def continue_inward(exterior, boundary, parameters, geometry, *, kind='retained',
                    threshold=100., method='DOP853', tolerance=1e-10, max_step=.004):
    initial = exterior.sol(boundary.inner_radius)[:6].copy()
    metric = InteriorMetric(kind, geometry, boundary, exterior.sol(boundary.inner_radius)[7])
    radial_scale = metric.values(metric.start)[2]
    # Positive x points inward on the negative branch. Match normal derivatives,
    # including the change from v*r to the retained physical coordinate x.
    initial[[1, 3, 5]] *= -boundary.vacuum_scale*radial_scale*np.sqrt(boundary.inner_f)
    if threshold <= max(abs(initial[0]), abs(initial[2])):
        raise ValueError('amplitude threshold must exceed its initial value')

    def amplitude_event(x, y):
        return threshold-max(abs(y[0]), abs(y[2]))

    amplitude_event.terminal = True
    amplitude_event.direction = -1
    solution = solve_ivp(lambda x, y: interior_rhs(x, y, exterior.p[0], boundary.vacuum_scale, parameters, metric),
        (metric.start, 0.), initial, method=method, rtol=tolerance, atol=tolerance*.01,
        max_step=max_step, events=amplitude_event, dense_output=True)
    if not solution.success:
        raise RuntimeError('inward integration failed before its registered event: '+solution.message)
    return solution, metric
