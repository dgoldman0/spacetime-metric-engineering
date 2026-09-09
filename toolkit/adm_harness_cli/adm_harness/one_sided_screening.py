"""Leading planar response of an exterior-only, massless cold screening gas.

This is a local comparison for the massive gravitating atmosphere, not its
coupled curved-space eigenvalue problem. Charge remains fixed per material
patch. The empty side supports the perturbed electromagnetic field.
"""
import numpy as np
from scipy.integrate import quad, solve_bvp

from .screened_wall import REFERENCE_CHARGE, displacement_profile


def one_sided_cloud(number_per_area, eta=1., charge=REFERENCE_CHARGE):
    if not np.isfinite([number_per_area, eta, charge]).all() or min(number_per_area, eta, charge) <= 0:
        raise ValueError('finite positive number, conversion and charge required')
    c = np.sqrt(6)*np.pi/charge
    a = np.sqrt(c/(charge**2*number_per_area))
    energy = eta*4*np.pi**2/(charge**4*a**3)
    return {'cloud_length': a, 'cloud_energy': energy, 'cloud_pressure': energy/2,
        'chemical_at_wall': c/a, 'electric_energy_at_wall': eta*charge**2*number_per_area**2/2,
        'gas_energy_at_wall': 3*eta*charge**2*number_per_area**2/2}


def cloud_stiffness_ratio(q):
    """K_cloud/(P_cloud*k^2); negative at every positive wave number."""
    q = np.asarray(q, float)
    if not np.isfinite(q).all() or np.any(q < 0):
        raise ValueError('finite nonnegative wave number required')
    return -3*(q+2)*(q+1)/(2*q**3+6*q*q+9*q+6)


def boundary_amplitudes(q):
    if not np.isfinite(q) or q <= 0:
        raise ValueError('finite positive wave number required')
    d = q+3*(q+2)/(q*q+3*q+3)
    outside = (q+2)/(q+d)
    # Use the polynomial form to avoid cancellation near translation.
    inside = -q*q*(q+1)/(2*q**3+6*q*q+9*q+6)
    return outside, inside


def independent_energy_ratio(q):
    """Second variation of the on-shell field/occupied-gas energy."""
    outside, inside = boundary_amplitudes(q)

    def integrand(s):
        w, wp = displacement_profile(s, q)
        v = outside*w-(1+s)**-2
        vp = outside*wp+2*(1+s)**-3
        return vp*vp+q*q*(outside*w)**2+6*v*v/(1+s)**2

    exterior, error = quad(integrand, 0, np.inf, epsabs=1e-13, epsrel=2e-11, limit=300)
    interior = q*inside**2
    return {'energy_stiffness_ratio': -3*(exterior+interior)/(q*q),
            'quadrature_error_estimate': 3*error/(q*q)}


def independent_response_bvp(q, tolerance=1e-9):
    """Poisson response with the empty-side field eliminated by its Robin condition."""
    boundary_amplitudes(q)
    extent = max(30., 35/q)
    grid = np.expm1(np.linspace(0., np.log1p(extent), 350))
    initial = np.exp(-q*grid)/(1+grid)**2
    derivative = -(q+2/(1+grid))*initial

    def fun(s, y):
        return np.vstack((y[1], (q*q+6/(1+s)**2)*y[0]))

    def bc(left, right):
        return [left[1]-q*left[0]+q+2, right[0]]

    sol = solve_bvp(fun, bc, grid, np.vstack((initial, derivative)),
                    tol=tolerance, max_nodes=18000)
    if not sol.success:
        raise RuntimeError(sol.message)
    inside = sol.y[0, 0]-1
    return {'bvp_stiffness_ratio': 3*(q+2)*inside/(q*q),
            'bvp_nodes': len(sol.x), 'bvp_maximum_residual': float(np.max(sol.rms_residuals))}
