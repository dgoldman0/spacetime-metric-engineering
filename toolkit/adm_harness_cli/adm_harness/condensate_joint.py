"""Two-domain screened-condensate BVP across the retained rail throat.

The core metric is supplied, including its positive-side asymptotic tail.
The negative-side exterior follows the classical Einstein--matter equations.
The missing interior Einstein source remains a measured quantum requirement.
"""
from dataclasses import dataclass

import numpy as np
from scipy.integrate import cumulative_simpson, solve_bvp
from scipy.interpolate import CubicSpline, PchipInterpolator

from .condensate_rail import ExteriorBoundary, _trial_rhs
from .screened_condensate import field_stress


@dataclass(frozen=True)
class JointParameters:
    inner_radius: float = 20.
    physical_join: float = 6.8
    exterior_extent: float = 160.
    positive_extent: float = 48.
    local_frequency_fraction: float = .85
    metric_fraction: float = 1.

    def __post_init__(self):
        if not 0 < self.local_frequency_fraction < 1:
            raise ValueError('frequency must lie below the positive-end matter threshold')
        if self.inner_radius <= 0 or self.exterior_extent <= self.inner_radius or self.positive_extent <= 8:
            raise ValueError('positive scale and resolved asymptotic domains required')
        if not 0 <= self.metric_fraction <= 1:
            raise ValueError('metric continuation fraction must be in [0,1]')

    @property
    def vacuum_scale(self):
        return self.inner_radius/self.physical_join


class JointGeometry:
    """Proper-distance interpolation; the auxiliary metric scales log(A),log(B)."""
    def __init__(self, retained, parameters):
        self.parameters = parameters
        self.boundary = ExteriorBoundary.from_geometry(retained,
            physical_radius=parameters.physical_join, inner_radius=parameters.inner_radius)
        left = float(retained.negative_branch_coordinate(parameters.physical_join))
        x = np.unique(np.r_[left, retained.coordinate[retained.coordinate > left],
                           np.linspace(8., parameters.positive_extent, 2001)])
        r, a, b = retained.values(x)
        a, b = a**parameters.metric_fraction, b**parameters.metric_fraction
        # A=1 at the outer cut, including for the auxiliary metric.
        a /= a[0]
        s = cumulative_simpson(b, x=x, initial=0)
        self.length, self.x_start = float(s[-1]), left
        self._x = PchipInterpolator(s, x)
        self._s = PchipInterpolator(x, s)
        self._r = CubicSpline(s, np.log(r))
        self._a = CubicSpline(s, np.log(a))
        self._b = CubicSpline(s, np.log(b))

    def values(self, t):
        s = np.asarray(t)*self.length
        return (np.exp(self._r(s)), np.exp(self._a(s)),
                self._r(s, 1), self._a(s, 1))

    def coordinate(self, t):
        return self._x(np.asarray(t)*self.length)

    def fraction_at_coordinate(self, coordinate):
        return self._s(coordinate)/self.length


def physical_parameters(eigenparameters, setup, material):
    log_g, log_clock = eigenparameters
    gravity, clock = np.exp(log_g), np.exp(log_clock)
    omega = setup.local_frequency_fraction*np.sqrt(material.matter_coupling)*clock
    return gravity, clock, omega


def proper_matter_rhs(radius, lapse, rlog, alog, fields, omega, material):
    """Dimensionless proper-radius derivatives, with all fields normalized by v."""
    u, up, h, hp, a, ap = fields
    e, lam, mu = material.charge, material.higgs_coupling, material.matter_coupling
    ds, dg = 2*rlog+alog, 2*rlog-alog
    return np.array([up, -ds*up+(mu*h*h-(omega-e*a)**2/lapse**2)*u,
        hp, -ds*hp+(mu*u*u+lam*(h*h-1)/2-e*e*a*a/lapse**2)*h,
        ap, -dg*ap+2*e*e*a*(u*u+h*h)-2*e*omega*u*u])


def joint_rhs(t, fields, eigenparameters, geometry, material, *, trial=False):
    setup = geometry.parameters
    pars = np.clip(eigenparameters, [-20., -5.], [-2., .2]) if trial else eigenparameters
    gravity, clock, omega = physical_parameters(pars, setup, material)
    r_out = setup.inner_radius+(setup.exterior_extent-setup.inner_radius)*t
    if trial:
        outer = _trial_rhs(r_out, fields[:8], omega, gravity, material)
    else:
        from .screened_condensate import gravitating_rhs
        outer = gravitating_rhs(r_out, fields[:8], omega, gravity, material)
    r, a, rlog, alog = geometry.values(t)
    v = setup.vacuum_scale
    core = proper_matter_rhs(v*r, clock*a, rlog/v, alog/v, fields[8:], omega, material)
    return np.vstack((outer*(setup.exterior_extent-setup.inner_radius), core*(v*geometry.length)))


def joint_boundary(left, right, eigenparameters, geometry, material, *, trial=False):
    setup, b = geometry.parameters, geometry.boundary
    pars = np.clip(eigenparameters, [-20., -5.], [-2., .2]) if trial else eigenparameters
    gravity, clock, omega = physical_parameters(pars, setup, material)
    f = b.inner_f
    # Use the prescribed inner mass in the pressure evaluation. The independent
    # mass boundary residual then enforces the same metric in the final solution.
    sigma = np.exp(np.clip(left[7], -10, 5) if trial else left[7])
    pressure = field_stress(left[:6], omega, material, f, sigma)['radial_pressure']
    load = (b.inner_mass+4*np.pi*gravity*setup.inner_radius**3*pressure-
            setup.inner_radius**2*f*b.inner_lapse_gradient)/b.inner_mass
    rfar, _, rlog, _ = geometry.values(1.)
    k = np.array([np.sqrt(material.matter_coupling*(1-setup.local_frequency_fraction**2)),
                  np.sqrt(material.higgs_coupling), np.sqrt(2)*material.charge])
    asymptotic = right[[9, 11, 13]]+(k+rlog/setup.vacuum_scale)*(right[[8, 10, 12]]-[0., 1., 0.])
    return np.r_[right[0], right[2]-1, right[4], right[7],
        (left[6]-b.inner_mass)/b.inner_mass,
        left[[0, 2, 4]]-left[[8, 10, 12]],
        np.sqrt(f)*left[[1, 3, 5]]+left[[9, 11, 13]],
        left[7]+.5*np.log(f)-pars[1], load, asymptotic]


def initial_guess(t, geometry, material, *, kind='potential', inner_transition=0.):
    setup, b = geometry.parameters, geometry.boundary
    v, e = setup.vacuum_scale, material.charge
    clock = .8
    omega = setup.local_frequency_fraction*np.sqrt(material.matter_coupling)*clock
    r = setup.inner_radius+(setup.exterior_extent-setup.inner_radius)*t
    transition = setup.inner_radius+10.
    step = (1-np.tanh((r-transition)/3))/2
    gauge_step = (1-np.tanh((r-transition)/7))/2
    u, h, a = 1.6*step, 1-step, omega/e*gauge_step
    mass = b.inner_mass+4*(1-step)
    logs = np.log(clock/np.sqrt(b.inner_f))*gauge_step
    outer = np.array([u, np.gradient(u, r), h, np.gradient(h, r),
                      a, np.gradient(a, r), mass, logs])
    s = t*geometry.length*v
    center = float(geometry.fraction_at_coordinate(inner_transition))*geometry.length*v
    if kind == 'potential':
        step_core = (1-np.tanh((s-center)/3))/2
        step_gauge = (1-np.tanh((s-center)/7))/2
        uc, hc, ac = 1.6*step_core, 1-step_core, omega/e*step_gauge
    elif kind == 'hollow':
        step_core = np.exp(-s/3)
        uc, hc, ac = u[0]*step_core, 1-(1-h[0])*step_core, a[0]*np.exp(-s/7)
    else:
        raise ValueError('choose potential or hollow branch guess')
    core = np.array([uc, np.gradient(uc, s), hc, np.gradient(hc, s),
                     ac, np.gradient(ac, s)])
    gravity = b.inner_mass/(np.pi*setup.inner_radius**3*material.higgs_coupling)
    return np.vstack((outer, core)), np.log([gravity, clock])


def solve_joint(geometry, material, *, seed=None, kind='potential', inner_transition=0.,
                tolerance=2e-5, points=2001, max_nodes=18000):
    t = np.linspace(0., 1., points)
    if seed is None:
        fields, eigenparameters = initial_guess(t, geometry, material,
            kind=kind, inner_transition=inner_transition)
    else:
        old_solution, old_geometry = seed
        fields = old_solution.sol(t)
        # Carry the core profile at the same physical coordinate during the
        # metric homotopy; its proper length changes as log(B) is switched on.
        x = geometry.coordinate(t)
        old_t = np.clip(old_geometry.fraction_at_coordinate(x), 0., 1.)
        old_core = old_solution.sol(old_t)[8:]
        old_b = np.exp(old_geometry._b(old_t*old_geometry.length))
        new_b = np.exp(geometry._b(t*geometry.length))
        old_core[[1, 3, 5]] *= old_b/new_b
        fields[8:] = old_core
        eigenparameters = old_solution.p
    with np.errstate(over='ignore', invalid='ignore', divide='ignore'):
        solution = solve_bvp(lambda t, y, p: joint_rhs(t, y, p, geometry, material, trial=True),
            lambda l, r, p: joint_boundary(l, r, p, geometry, material, trial=True),
            t, fields, p=eigenparameters, tol=tolerance, max_nodes=max_nodes)
    return solution


def joint_checks(solution, geometry, material):
    setup = geometry.parameters
    g, clock, omega = physical_parameters(solution.p, setup, material)
    dt = np.diff(solution.x)
    t = np.unique(np.r_[solution.x, solution.x[:-1]+.25*dt, solution.x[:-1]+.75*dt])
    y = solution.sol(t)
    r = setup.inner_radius+(setup.exterior_extent-setup.inner_radius)*t
    f = 1-2*y[6]/r
    chart = (np.isfinite(y).all() and np.min(f)>1e-7 and np.max(abs(y[7]))<10
        and -20 < solution.p[0] < -2 and -5 < solution.p[1] < .2
        and omega < np.sqrt(material.matter_coupling))
    equation_error, boundary_error = float('inf'), float('inf')
    if chart:
        rhs = joint_rhs(t, y, solution.p, geometry, material)
        equation_error = float(np.max(abs(solution.sol(t, 1)-rhs)/(1+abs(rhs))))
        boundary_error = float(np.max(abs(joint_boundary(y[:, 0], y[:, -1], solution.p, geometry, material))))
    return {'solver_success': bool(solution.success), 'status': int(solution.status),
        'chart_and_asymptotic_mass_gap': bool(chart), 'gravity_Gv2': float(g),
        'positive_end_clock': float(clock), 'omega': float(omega),
        'maximum_equation_error': equation_error, 'maximum_boundary_error': boundary_error,
        'minimum_exterior_f': float(np.min(f)), 'maximum_scalar_amplitude': float(np.max(abs(y[[0, 2, 8, 10]]))),
        'adm_mass_rail_units': float(y[6, -1]/setup.vacuum_scale), 'nodes': len(solution.x),
        'maximum_collocation_residual': float(np.max(solution.rms_residuals))}
