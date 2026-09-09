"""Cold relativistic Thomas--Fermi screening of a charged Fermi wall.

The optical wall keeps its finite width. Its charge is a sheet at leading
order in wall_width/cloud_length and k*wall_width. The cloud calculation
is planar, static, and massless, with one screening Dirac species and
zero chemical potential at infinity. All energies include the electric
field and occupied screening particles. Curved equilibrium, finite-mass
tails, charged wall eigenstates, and dynamical response are separate.
"""
import numpy as np
from scipy.integrate import quad, solve_bvp

from .smooth_mirror import fermi_surface_match

# Registered illustrative coupling; 137 is a model benchmark, not a new
# measurement of the fine structure constant.
REFERENCE_CHARGE = np.sqrt(4*np.pi/137)


def _positive(*values):
    if any(not np.isfinite(v).all() or np.any(np.asarray(v) <= 0) for v in values):
        raise ValueError('finite positive parameters required')


def cold_cloud(sheet_number, charge=REFERENCE_CHARGE):
    """Planar charge-neutral cloud in microscopic hbar=c=1 units.

    u=e*A0=c/(|z|+a), c=sqrt(6)*pi/e, and -2*u'(0+)=e^2*n.
    Screening particles have p_F=u and two positive-energy spin states.
    Their kinetic energy is three times the electric field energy.
    """
    _positive(sheet_number, charge)
    n = np.asarray(sheet_number, float)
    c = np.sqrt(6)*np.pi/charge
    a = np.sqrt(2*c/(charge**2*n))
    energy = 8*np.pi**2/(charge**4*a**3)
    return {'cloud_length': a, 'potential_at_wall': c/a,
        'cloud_energy': energy, 'electric_energy': energy/4,
        'screening_particle_energy': 3*energy/4,
        'cloud_pressure': energy/2, 'integrated_normal_pressure': np.zeros_like(a),
        'bending_coefficient': energy*a*a/6}


def cold_cloud_profile(z, sheet_number, charge=REFERENCE_CHARGE):
    """Finite local classical stresses on either side of the charge sheet."""
    data = cold_cloud(sheet_number, charge)
    z = np.asarray(z, float)
    if not np.isfinite(z).all():
        raise ValueError('finite normal coordinates required')
    c = np.sqrt(6)*np.pi/charge
    u = c/(np.abs(z)+data['cloud_length'])
    electric_energy = u**4/(12*np.pi**2)
    return {'potential': u, 'screening_number_density': u**3/(3*np.pi**2),
        'electric_energy_density': electric_energy,
        'screening_energy_density': 3*electric_energy,
        'energy_density': 4*electric_energy,
        'normal_pressure': np.zeros_like(u), 'tangential_pressure': 2*electric_energy}


def restoring_fraction(q):
    """R/(P_cloud*k^2), q=k*a, after subtracting counted local pressure.

    Total cloud stiffness K_cloud=-P_cloud*k^2+R remains negative.
    The positive correction tends to P_cloud*k^2 at large q.
    """
    q = np.asarray(q, float)
    if np.any(q < 0) or not np.isfinite(q).all():
        raise ValueError('finite nonnegative wave numbers required')
    return q*q/(q*q+3*q+3)


def displacement_profile(x, q):
    """Decaying lab-frame dipole potential w, normalized to w(0)=1.

    w''=[q^2+6/(1+x)^2]*w for x=z/a>=0. The q=0 solution is
    translation of the original cloud. Return w and its x derivative.
    """
    x = np.asarray(x, float)
    if np.any(x < 0) or q < 0 or not np.isfinite(x).all() or not np.isfinite(q):
        raise ValueError('finite nonnegative coordinates and wave number required')
    s = 1+x
    polynomial = q*q+3*q/s+3/s**2
    prefactor = np.exp(-q*x)/(q*q+3*q+3)
    return prefactor*polynomial, prefactor*(-q*polynomial-3*q/s**2-6/s**3)


def independent_response_bvp(q, tolerance=1e-9):
    """Numerical linearized Poisson problem, independent of closed-form w.

    The endpoint is at least 30 exponential lengths away; an outgoing
    exponential Robin condition approximates the remote algebraic factor.
    This returns K_cloud/(P_cloud*k^2), a static stiffness ratio.
    """
    _positive(q, tolerance)
    extent = max(40., 30/q)
    x = np.expm1(np.linspace(0., np.log1p(extent), 320))
    guess = np.exp(-q*x)/(1+x)**2
    guess_prime = -guess*(q+2/(1+x))
    solution = solve_bvp(lambda x, y: np.vstack((y[1], (q*q+6/(1+x)**2)*y[0])),
        lambda left, right: np.array([left[0]-1, right[1]+q*right[0]]),
        x, np.vstack((guess, guess_prime)), tol=tolerance, max_nodes=30000)
    if not solution.success:
        raise RuntimeError(solution.message)
    return {'cloud_stiffness_ratio': float(3*(2+solution.y[1, 0])/q**2),
        'wall_derivative': float(solution.y[1, 0]), 'nodes': len(solution.x),
        'maximum_residual': float(np.max(solution.rms_residuals)), 'extent': extent}


def independent_response_energy(q, tolerance=2e-11):
    """Second variation of the stationary electrostatic energy functional.

    In wall-following coordinates v=w-(1+x)^-2. Its positive integral
    I=int_0^inf [v'^2+q^2*w^2+6*v^2/(1+x)^2] dx gives K/Pc/k^2=-3I/q^2.
    This computes the energy variation independently of the wall-force
    formula; the electrostatic potential functional is extremized first.
    """
    _positive(q, tolerance)

    def integrand(x):
        w, wp = displacement_profile(x, q)
        v, vp = w-1/(1+x)**2, wp+2/(1+x)**3
        return vp*vp+q*q*w*w+6*v*v/(1+x)**2

    integral, error = quad(integrand, 0., np.inf, epsabs=tolerance*q*q,
                           epsrel=tolerance, limit=300)
    return {'cloud_stiffness_ratio': -3*integral/q**2,
            'quadrature_error_estimate': 3*error/q**2}


def screened_surface_match(radius, exterior_mass, flavors=1, charge=REFERENCE_CHARGE,
                           throat=1.75):
    """Count cloud energy and pressure in the leading neutral composite junction.

    Collapsing wall+neutralizing cloud to one surface preserves the vacuum
    exterior at this order. Both occupied components have P=energy/2.
    gamma=energy_cloud/energy_wall_fermions follows from their common charge
    density, one wall zero branch per flavor, and one screening Dirac field.
    """
    _positive(flavors, charge)
    if np.any(np.asarray(flavors) != np.floor(flavors)):
        raise ValueError('integer flavor count required')
    result = fermi_surface_match(radius, exterior_mass, throat)
    total_gas = result['fermi_energy']
    gamma = np.sqrt(np.sqrt(3)*charge/(4*np.sqrt(2)))*np.sqrt(flavors)
    gas = total_gas/(1+gamma)
    cloud = total_gas-gas
    sigma, pressure, tension = (result[k] for k in
        ['surface_energy', 'surface_pressure', 'wall_tension'])
    return {**result, 'fermi_energy': gas, 'cloud_energy': cloud,
        'cloud_pressure': cloud/2, 'cloud_to_fermi_ratio': np.full_like(sigma, gamma),
        'restoring_ceiling_over_required': cloud/(2*pressure),
        'energy_reconstruction_error': tension+gas+cloud-sigma,
        'pressure_reconstruction_error': -tension+(gas+cloud)/2-pressure}


def critical_cloud_wave_number(ceiling_over_required):
    """q needed for static nonnegative stiffness; infinity means no crossing."""
    b = np.asarray(ceiling_over_required, float)
    if not np.isfinite(b).all() or np.any(b < 0):
        raise ValueError('finite nonnegative stiffness ratio required')
    result = np.full_like(b, np.inf)
    chosen = b > 1
    result[chosen] = (3+np.sqrt(12*b[chosen]-3))/(2*(b[chosen]-1))
    return result


def junction_restoring_bound(radius, throat=1.75):
    """Analytic best mass and cloud-only upper bound across the static branch.

    P/Sigma has its minimum b/[2(R-b)] at M=R*b/(R+b).
    Allowing all gas energy to reside in the cloud is an optimistic
    relaxation of every finite-flavor charged-wall realization.
    """
    _positive(radius, throat)
    if radius <= throat:
        raise ValueError('radius must exceed throat')
    ceiling = (2*radius-throat)/(3*throat)
    return {'best_exterior_mass': radius*throat/(radius+throat),
        'minimum_pressure_to_energy': throat/(2*(radius-throat)),
        'maximum_cloud_restoring_ceiling': ceiling,
        'minimum_critical_q': float(critical_cloud_wave_number(ceiling))}
