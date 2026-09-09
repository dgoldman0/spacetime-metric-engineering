"""A compact, cold Einstein--Maxwell--Thomas--Fermi exterior atmosphere.

The boundary is a charged Fermi sheet outside an ultrastatic rail tail.
Screening particles occupy only the exterior. A finite-width exclusion
mechanism and coupled perturbations are separate material requirements.
Units are hbar=c=1, with Heaviside--Lorentz electric charge.
"""
from dataclasses import dataclass, asdict

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

REFERENCE_CHARGE = np.sqrt(4*np.pi/137)


@dataclass(frozen=True)
class AtmosphereParameters:
    radius: float = 6.8
    throat: float = 1.75
    edge_ratio: float = 1.5
    screening_mass_parameter: float = 3.
    loading: float = 1e-4
    flavors: int = 64
    charge: float = REFERENCE_CHARGE

    def __post_init__(self):
        values = [self.radius, self.throat, self.edge_ratio,
                  self.screening_mass_parameter, self.loading, self.charge]
        if not np.isfinite(values).all() or min(values) <= 0:
            raise ValueError('finite positive parameters required')
        if self.radius <= self.throat or self.edge_ratio <= 1:
            raise ValueError('wall outside throat and atmosphere edge outside wall required')
        if not isinstance(self.flavors, (int, np.integer)) or self.flavors < 1:
            raise ValueError('positive integer species count required')

    @property
    def chemical_scale(self):
        return np.sqrt(6)*np.pi/self.charge

    @property
    def eta(self):
        return self.loading*self.charge**4*self.radius**2/(12*np.pi**3)


def fermi_polynomials(chemical, rest_mass):
    """Return scaled energy, pressure, and momentum for a spin-two gas.

    Inputs are r*mu/c_e and r*m_s/c_e. The outputs obey
    4*pi*r^4*eta*rho/(loading*R^2)=energy and similarly for pressure.
    A nonrelativistic series avoids subtracting nearly equal logarithms.
    """
    u, w = np.broadcast_arrays(np.asarray(chemical, float), np.asarray(rest_mass, float))
    if np.any(u < 0) or np.any(w < 0) or not np.isfinite([u, w]).all():
        raise ValueError('finite nonnegative chemical potential and rest mass required')
    momentum = np.sqrt(np.maximum((u-w)*(u+w), 0))
    er, pr = np.zeros_like(u), np.zeros_like(u)
    massless = w == 0
    er[massless], pr[massless] = 3*u[massless]**4, u[massless]**4
    massive = ~massless
    x = np.divide(momentum, w, out=np.zeros_like(u), where=massive)
    series = massive & (x < .05)
    a, b = x[series], w[series]**4
    er[series] = 1.5*b*(8*a**3/3+4*a**5/5-a**7/7+a**9/18-5*a**11/176)
    pr[series] = .5*b*(8*a**5/5-4*a**7/7+a**9/3-5*a**11/22)
    direct = massive & ~series
    p, v, m = momentum[direct], u[direct], w[direct]
    logarithm = m**4*np.arcsinh(x[direct])
    er[direct] = 1.5*(p*v*(2*p*p+m*m)-logarithm)
    pr[direct] = .5*(p*v*(2*p*p-3*m*m)+3*logarithm)
    return er, pr, momentum


def atmosphere_rhs(t, y, parameters):
    """Log-radius equations for U, Z, m/R, log(lapse), e*A_t*R/c_e."""
    u, z, mass, phi, potential = y
    x = np.exp(t)
    # A floor is used only by trial integrator stages; the event and final
    # profile checks reject trajectories approaching a horizon.
    f = max(1-2*mass/x, 1e-10)
    er, pr, p = fermi_polynomials(max(u, 0.), parameters.screening_mass_parameter*x)
    h = (mass/x+parameters.loading*(pr-z*z)/x**2)/f
    return [(1-h)*u-z/np.sqrt(f), -2*p**3/np.sqrt(f),
            parameters.loading*(er+z*z)/x, h,
            -np.exp(phi)*z/(x*np.sqrt(f))]


def solve_atmosphere(parameters, adm_mass_ratio, *, rtol=2e-10, method='DOP853',
                     max_step=.01):
    """Integrate inward from a neutral zero-density edge.

    Vacuum beyond the edge is exactly Schwarzschild, with lapse normalized
    at that infinity. A negative mass at the wall is outside this search.
    Integration failure is raised separately from an absent surface match.
    """
    p = parameters
    if not np.isfinite(adm_mass_ratio) or not 0 < adm_mass_ratio < p.edge_ratio/2:
        raise ValueError('positive subhorizon ADM mass required')
    if rtol <= 0 or max_step <= 0:
        raise ValueError('positive integration controls required')
    edge_f = 1-2*adm_mass_ratio/p.edge_ratio
    initial = [p.screening_mass_parameter*p.edge_ratio, 0., adm_mass_ratio,
               .5*np.log(edge_f), 0.]

    def horizon(t, y):
        return 1-2*y[2]*np.exp(-t)-1e-6

    def negative_core_mass(t, y):
        return y[2]

    horizon.terminal = True
    negative_core_mass.terminal = True
    result = solve_ivp(lambda t, y: atmosphere_rhs(t, y, p),
        (np.log(p.edge_ratio), 0.), initial, method=method,
        rtol=rtol, atol=rtol*.01, max_step=max_step, dense_output=True,
        events=[horizon, negative_core_mass])
    if not result.success:
        raise RuntimeError('atmosphere integration failed: '+result.message)
    if result.t[-1] != 0.:
        reason = 'horizon threshold' if len(result.t_events[0]) else 'negative core mass'
        raise ValueError('profile left registered domain: '+reason)
    grid = np.linspace(0, np.log(p.edge_ratio), 1001)
    if np.min(1-2*result.sol(grid)[2]*np.exp(-grid)) <= 1e-6:
        raise ValueError('profile crosses horizon threshold')
    return result


def surface_match(parameters, solution):
    """Israel stress and charge-constrained Fermi-sheet energy at the wall."""
    p = parameters
    u, z, mass, phi, potential = solution.sol(0.)
    er, pr, momentum = fermi_polynomials(u, p.screening_mass_parameter)
    f = 1-2*mass
    h = (mass+p.loading*(pr-z*z))/f
    inside, outside = np.sqrt(1-(p.throat/p.radius)**2), np.sqrt(f)
    energy = inside-outside
    pressure = (outside*(1+h)-inside)/2
    gas_required, tension = 2*(energy+pressure)/3, (energy-2*pressure)/3
    gas_actual = p.loading*4*6**.75*z**1.5/(9*np.sqrt(p.charge*p.flavors))
    scale = 4*np.pi*p.radius
    n = p.chemical_scale*z/(p.charge**2*p.radius**2)
    alpha = np.exp(phi)
    screening_mu = p.chemical_scale*u/p.radius
    screening_mass = p.chemical_scale*p.screening_mass_parameter/p.radius
    electric_potential = p.chemical_scale*potential/p.radius
    kf = np.sqrt(4*np.pi*n/p.flavors)
    adm = float(solution.y[2, 0])
    return {**asdict(p), 'adm_mass_ratio': adm, 'wall_mass_ratio': float(mass),
        'adm_mass': adm*p.radius, 'wall_mass': float(mass*p.radius),
        'cloud_adm_mass': float((adm-mass)*p.radius), 'eta': p.eta,
        'wall_lapse': float(alpha), 'wall_log_lapse_slope': float(h),
        'wall_U': float(u), 'wall_Z': float(z),
        'surface_energy': float(energy/scale), 'surface_pressure': float(pressure/scale),
        'wall_tension': float(tension/scale), 'surface_gas_energy': float(gas_required/scale),
        'charge_predicted_gas_energy': float(gas_actual/scale),
        'scaled_matching_residual': float(gas_actual-gas_required),
        'positive_components': bool(min(energy, gas_required, tension) > 0),
        'tensile_wall': bool(pressure < 0),
        'wall_only_transverse_speed_squared': float(-pressure/energy),
        'wall_number_per_area': float(n), 'wall_fermi_momentum': float(kf),
        'wall_charge': float(4*np.pi*p.chemical_scale*z/p.charge),
        'screening_rest_mass': float(screening_mass),
        'screening_chemical_at_wall': float(screening_mu),
        'electric_potential_energy_at_wall': float(electric_potential),
        'screening_klein_energy': float(alpha*screening_mu-electric_potential),
        'wall_fermi_energy_at_infinity': float(alpha*kf+electric_potential)}


def find_surface_equilibrium(parameters, *, rtol=2e-10, method='DOP853'):
    """Return all bracketed physical matches in the registered mass interval.

    The interval 0.12 <= M/R <= 0.40 is a bounded search, not an existence
    theorem. Failed integrators propagate; inadmissible core masses break
    a bracket and are counted independently.
    """
    roots, rejected, previous = [], 0, None

    def residual(mass):
        sol = solve_atmosphere(parameters, mass, rtol=rtol, method=method)
        return surface_match(parameters, sol)['scaled_matching_residual']

    for mass in np.linspace(.12, .40, 57):
        try:
            value = residual(mass)
        except ValueError:
            rejected += 1
            previous = None
            continue
        if previous is not None and previous[1]*value < 0:
            root = brentq(residual, previous[0], mass, xtol=2e-13, rtol=2e-13)
            solution = solve_atmosphere(parameters, root, rtol=rtol, method=method)
            row = surface_match(parameters, solution)
            if row['positive_components']:
                roots.append((row, solution))
        elif value == 0:
            solution = solve_atmosphere(parameters, mass, rtol=rtol, method=method)
            row = surface_match(parameters, solution)
            if row['positive_components']:
                roots.append((row, solution))
        previous = mass, value
    return roots, rejected


def atmosphere_profile(parameters, solution, points=2001):
    """Small, outward-ordered radial profile; geometric stresses include eta."""
    p = parameters
    t = np.linspace(0, np.log(p.edge_ratio), points)
    x = np.exp(t)
    u, z, mass, phi, potential = solution.sol(t)
    er, pr, momentum = fermi_polynomials(u, p.screening_mass_parameter*x)
    f, alpha = 1-2*mass/x, np.exp(phi)
    scale = p.loading/(4*np.pi*p.radius**2*x**4)
    chemical = p.chemical_scale*u/(p.radius*x)
    potential = p.chemical_scale*potential/p.radius
    kf = p.chemical_scale*momentum/(p.radius*x)
    return {'log_radius_ratio': t, 'radius': p.radius*x, 'mass': p.radius*mass,
        'metric_f': f, 'lapse': alpha, 'chemical_potential': chemical,
        'fermi_momentum': kf, 'screening_number_density': kf**3/(3*np.pi**2),
        'charge': 4*np.pi*p.chemical_scale*z/p.charge,
        'electric_potential_energy': potential,
        'klein_energy': alpha*chemical-potential,
        'gas_energy_density': scale*er, 'gas_pressure': scale*pr,
        'electric_energy_density': scale*z*z,
        'total_energy_density': scale*(er+z*z),
        'radial_pressure': scale*(pr-z*z), 'tangential_pressure': scale*(pr+z*z)}
