"""Ishihara--Ogawa matter, Higgs and screened gauge condensates.

Fields and radius are normalized by the Higgs vacuum amplitude v.
The flat-space solitons are material controls; a rail source also requires
gravity, interior matching, and its quantum stress.
"""
from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_bvp, cumulative_trapezoid


@dataclass(frozen=True)
class CondensateParameters:
    charge: float = .1
    higgs_coupling: float = 1.
    matter_coupling: float = 1.4

    def __post_init__(self):
        values = [self.charge, self.higgs_coupling, self.matter_coupling]
        if not np.isfinite(values).all() or min(values) <= 0:
            raise ValueError('finite positive couplings required')


def field_stress(fields, omega, parameters, metric_f=1., sigma=1.):
    """Physical orthonormal stress and proper charge densities.

    Metric: ds^2=-sigma^2*f*dt^2+dr^2/f+r^2*dOmega^2.
    The six fields are u,u',h,h',A,A'. The phase of u is exp(i*omega*t).
    All constituent energies are positive for the registered action.
    """
    u, up, h, hp, a, ap = np.asarray(fields)[:6]
    e, lam, mu = parameters.charge, parameters.higgs_coupling, parameters.matter_coupling
    lapse = np.asarray(sigma)*np.sqrt(metric_f)
    matter_kinetic = (omega-e*a)**2*u*u/lapse**2
    higgs_kinetic = e*e*a*a*h*h/lapse**2
    gradient = metric_f*(up*up+hp*hp)
    potential = lam*(h*h-1)**2/4+mu*u*u*h*h
    electric = ap*ap/(2*np.asarray(sigma)**2)
    kinetic = matter_kinetic+higgs_kinetic
    return {'energy': kinetic+gradient+potential+electric,
        'radial_pressure': kinetic+gradient-potential-electric,
        'tangential_pressure': kinetic-gradient-potential+electric,
        'matter_kinetic': matter_kinetic, 'higgs_kinetic': higgs_kinetic,
        'gradient': gradient, 'potential': potential, 'electric': electric,
        'matter_number': 2*(omega-e*a)*u*u/lapse,
        'matter_charge': 2*e*(omega-e*a)*u*u/lapse,
        'higgs_charge': -2*e*e*a*h*h/lapse}


def flat_rhs(radius, fields, omega, parameters):
    """Regular part; the 2/r derivative terms are supplied through solve_bvp.S."""
    u, up, h, hp, a, ap = fields
    e, lam, mu = parameters.charge, parameters.higgs_coupling, parameters.matter_coupling
    return np.array([up, (mu*h*h-(e*a-omega)**2)*u,
        hp, (mu*u*u+lam*(h*h-1)/2-e*e*a*a)*h,
        ap, 2*e*e*a*(u*u+h*h)-2*e*omega*u*u])


def homogeneous_phase(omega, parameters):
    """Locally screened stationary branch, with gradients omitted."""
    e, lam, mu = parameters.charge, parameters.higgs_coupling, parameters.matter_coupling
    omega = np.asarray(omega, float)
    discriminant = mu*(2*lam+mu)*omega**2-mu*lam*(4*mu-lam)
    if mu <= lam or np.any(discriminant < 0):
        raise ValueError('homogeneous branch requires mu>lambda and nonnegative discriminant')
    a = ((mu-lam)*omega+np.sqrt(discriminant))/(e*(4*mu-lam))
    h = (omega-e*a)/np.sqrt(mu)
    u = np.sqrt(e*a*(omega-e*a)/mu)
    zero = np.zeros_like(u)
    fields = np.array([u, zero, h, zero, a, zero])
    return {'fields': fields, **field_stress(fields, omega, parameters),
        'minimum_stationary_frequency': np.sqrt(lam*(4*mu-lam)/(2*lam+mu)),
        'zero_pressure_frequency': np.sqrt(2*np.sqrt(lam*mu)-lam),
        'free_particle_mass': np.sqrt(mu)}


def flat_seed(kind, radius):
    """Explicit initial guesses for the two published reference frequencies."""
    if kind == 'homogeneous':
        p, omega = CondensateParameters(charge=1.), 1.170
        bulk = homogeneous_phase(omega, p)['fields']
        step = (1-np.tanh((radius-90.)/4))/2
        u, h, a = bulk[0]*step, 1+(bulk[2]-1)*step, bulk[4]*step
    elif kind == 'hollow':
        p, omega = CondensateParameters(), .8109
        bump = np.exp(-.5*((radius-90.)/5)**2)
        u, h = 4*bump, 1-.99*bump
        a = omega/p.charge*u*u/(u*u+h*h)
    else:
        raise ValueError('choose homogeneous or hollow reference')
    y = np.array([u, np.gradient(u, radius), h, np.gradient(h, radius),
                  a, np.gradient(a, radius)])
    return p, omega, y


def solve_flat_reference(kind, *, tolerance=1e-7, extent=250., points=1001,
                         reduced_number=None):
    if tolerance <= 0 or extent < 180 or points < 201:
        raise ValueError('positive tolerance, sufficient extent and initial resolution required')
    radius = np.linspace(0., 250., 1001)
    p, omega, guess = flat_seed(kind, radius)

    def bc(left, right):
        return [left[1], left[3], left[5], right[0], right[2]-1, right[4]]

    regularity = np.diag([0., -2., 0., -2., 0., -2.])
    # First locate the branch, then refine it. A failed relaxation raises an
    # error; its last iterate is never counted as a soliton or an exclusion.
    first = solve_bvp(lambda r, y: flat_rhs(r, y, omega, p), bc, radius, guess,
                     S=regularity, tol=2e-5, max_nodes=28000)
    if not first.success:
        raise RuntimeError('reference branch solve failed: '+first.message)
    # The published frequencies are rounded. Fix particle number during
    # refinement and solve for frequency, avoiding a near-degenerate radius
    # mode at the rounded shell frequency. N = 4*pi*reduced_number.
    target = ({'homogeneous': 58000., 'hollow': 85600.}[kind]
              if reduced_number is None else reduced_number)
    if not np.isfinite(target) or target <= 0:
        raise ValueError('finite positive particle number required')
    radius = np.linspace(0., extent, points)
    initial = first.sol(np.minimum(radius, 250.))
    initial[:, radius > 250.] = np.array([0., 0., 1., 0., 0., 0.])[:, None]
    stress = field_stress(initial, omega, p)
    number = cumulative_trapezoid(radius**2*stress['matter_number'], radius, initial=0)/target
    guess = np.vstack((initial, number))

    def numbered_rhs(r, y, frequency):
        n = 2*(frequency[0]-p.charge*y[4])*y[0]**2
        return np.vstack((flat_rhs(r, y[:6], frequency[0], p), r*r*n/target))

    def numbered_bc(left, right, frequency):
        return [left[1], left[3], left[5], right[0], right[2]-1, right[4],
                left[6], right[6]-1]

    solution = solve_bvp(numbered_rhs, numbered_bc, radius, guess, p=[omega],
        S=np.diag([0., -2., 0., -2., 0., -2., 0.]), tol=tolerance, max_nodes=35000)
    if not solution.success:
        raise RuntimeError('reference refinement failed: '+solution.message)
    if np.max(abs(solution.y[0])) < .01:
        raise RuntimeError('relaxation reached vacuum instead of the registered soliton')
    return p, float(solution.p[0]), solution


def gravitating_rhs(radius, fields, omega, gravity, parameters):
    """Einstein--matter equations with mass function m and log(sigma).

    gravity=G*v^2. The function is for r>0; all returned stresses remain in
    v^4 units until multiplied by the common gravitational conversion.
    """
    u, up, h, hp, a, ap, mass, log_sigma = fields
    sigma = np.exp(log_sigma)
    metric_f = 1-2*mass/radius
    if np.any(metric_f <= 0):
        raise ValueError('static exterior chart requires 1-2m/r>0')
    stress = field_stress(fields[:6], omega, parameters, metric_f, sigma)
    mass_prime = 4*np.pi*gravity*radius**2*stress['energy']
    log_sigma_prime = 8*np.pi*gravity*radius*(stress['matter_kinetic']+
        stress['higgs_kinetic']+stress['gradient'])/metric_f
    f_prime = -2*mass_prime/radius+2*mass/radius**2
    friction = 2/radius+log_sigma_prime+f_prime/metric_f
    e, lam, mu = parameters.charge, parameters.higgs_coupling, parameters.matter_coupling
    return np.array([up, -friction*up+(mu*h*h-(omega-e*a)**2/(sigma*sigma*metric_f))*u/metric_f,
        hp, -friction*hp+(mu*u*u+lam*(h*h-1)/2-e*e*a*a/(sigma*sigma*metric_f))*h/metric_f,
        ap, -(2/radius-log_sigma_prime)*ap+
        (2*e*e*a*(u*u+h*h)-2*e*omega*u*u)/metric_f,
        mass_prime, log_sigma_prime])
