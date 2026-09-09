"""Smooth scalar mirror benchmarks and the leading trapped-fermion material.

The vacuum calculation is planar and first order in the optical potential.
The surface material coefficients are effective measured quantities. Neither
calculation supplies a complete semiclassical spherical source.
"""
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad

from .spherical_support import outer_shell


def sech_optical_transform(q):
    """Fourier transform of (1/2) sech^2(z), with value one at q=0."""
    a = np.pi*np.abs(np.asarray(q, float))/2
    # The exponential form avoids overflow for the high-frequency tail.
    result = np.ones_like(a)
    np.divide(2*a*np.exp(-a), -np.expm1(-2*a), out=result, where=a != 0)
    return result


def smooth_born_stress(z, width, integrated_strength, mu, nodes=512, upper=40.):
    """All first-order planar stress channels, including points inside the wall.

    q=t^2 resolves the logarithmic origin of the Fourier integral. The
    omitted high-q tail decays exponentially. No delta sheets are used.
    """
    z = np.asarray(z, float)
    if (not np.isfinite(z).all() or min(width, integrated_strength, mu, upper) <= 0
            or nodes < 16):
        raise ValueError('finite coordinates, positive scales and >=16 nodes required')
    t, w = leggauss(nodes)
    t = .5*np.sqrt(upper)*(t+1)
    w = w*np.sqrt(upper)*t
    q = t*t
    kernel = w*q*q*np.log((q/(mu*width))**2)*sech_optical_transform(q)
    integral = np.cos(np.multiply.outer(z/width, q))@kernel
    energy = -integrated_strength*integral/(96*np.pi**3*width**3)
    return {'energy': energy, 'radial_pressure': np.zeros_like(energy),
            'angular_pressure': -energy, 'radial_enthalpy': energy,
            'angular_enthalpy': np.zeros_like(energy)}


def independent_born_energy(z, width, integrated_strength, mu):
    """Adaptive cosine integral, independent of the vector Gaussian quadrature."""
    def integrand(q):
        if q == 0:
            return 0.
        return q*q*np.log((q/(mu*width))**2)*float(sech_optical_transform(q))
    value, error = quad(integrand, 0., 60., weight='cos', wvar=z/width,
                        epsabs=2e-11, epsrel=2e-11, limit=400)
    prefactor = -integrated_strength/(96*np.pi**3*width**3)
    return prefactor*value, abs(prefactor)*error


def fermi_surface_match(radius, exterior_mass, throat=1.75):
    """Leading wall plus surface gas, with both radial and shape diagnostics."""
    result = outer_shell(radius, exterior_mass, throat)
    sigma, pressure = result['surface_energy'], result['surface_pressure']
    tension, fermi = (sigma-2*pressure)/3, 2*(sigma+pressure)/3
    denominator = 1/np.sqrt(1-2*np.asarray(exterior_mass)/radius)-1/np.sqrt(1-throat**2/radius**2)
    radial = 8*np.pi*(result['surface_pressure_derivative']-.5*result['surface_energy_derivative'])/denominator
    return {**result, 'wall_tension': tension, 'fermi_energy': fermi,
            'positive_components': (tension > 0)&(fermi > 0),
            'longitudinal_speed_squared': np.full_like(sigma, .5),
            'normal_speed_squared': -pressure/sigma,
            'fermi_radial_frequency_squared': radial,
            'energy_reconstruction_error': tension+fermi-sigma,
            'pressure_reconstruction_error': -tension+.5*fermi-pressure}


def corrugation_energy(amplitude, wave_number, tension, fermi_energy, nodes=256):
    """Energy per projected area at fixed particle number for h=a*cos(k*x).

    The gas may redistribute to its minimum energy on the enlarged area.
    This is the leading surface action, with zero added bending rigidity.
    """
    x, w = leggauss(nodes)
    slope2 = (amplitude*wave_number*np.sin(np.pi*(x+1)))**2
    # Compute the small area change without subtracting two nearly equal areas.
    area_change = .5*np.sum(w*slope2/(np.sqrt(1+slope2)+1))
    return tension*area_change+fermi_energy*np.expm1(-.5*np.log1p(area_change))


def normal_mode_requirements(radius, sigma, pressure, width, angular_indices):
    """Local membrane dispersion and required k^4 coefficient at each scale.

    k=sqrt(l(l+1))/R labels surface wavelengths; these are local modes, not
    eigenmodes of the coupled Einstein/material/quantum spherical problem.
    """
    ell = np.asarray(angular_indices, int)
    if min(radius, sigma, width) <= 0 or np.any(ell < 1):
        raise ValueError('positive scales and angular indices required')
    k = np.sqrt(ell*(ell+1))/radius
    omega2 = -pressure*k*k/sigma
    return {'angular_index': ell, 'wave_number': k, 'k_radius': k*radius,
            'k_width': k*width,
            'scale_window': (k*radius >= 10)&(k*width <= .2),
            'normal_frequency_squared': omega2,
            'growth_rate': np.sqrt(np.maximum(-omega2, 0)),
            'required_bending_coefficient': np.maximum(pressure, 0)/k**2,
            'required_bending_to_sigma_width_squared': np.maximum(pressure, 0)/(sigma*(k*width)**2)}
