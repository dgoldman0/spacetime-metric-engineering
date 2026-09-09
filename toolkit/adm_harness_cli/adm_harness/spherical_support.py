"""Outer-shell junction requirements and the local thin-sheet quantum limit."""
import numpy as np
from scipy.special import roots_laguerre


def outer_shell(radius, exterior_mass, throat=1.75):
    """Israel stresses for an ultrastatic rail tail and Schwarzschild exterior.

    Surface radial stability is conditional on the specified static bulks
    and a barotropic *total* surface response, including its momentum flux.
    It is separate from a microscopic quantum/material evolution.
    """
    r, mass = np.broadcast_arrays(np.asarray(radius, float), np.asarray(exterior_mass, float))
    fi, fo = 1-throat**2/(r*r), 1-2*mass/r
    if np.any(r <= throat) or np.any(fo <= 0) or np.any(mass < 0):
        raise ValueError('positive radius and static interior/exterior charts required')
    inside, outside = np.sqrt(fi), np.sqrt(fo)
    sigma = (inside-outside)/(4*np.pi*r)
    pressure = ((1-mass/r)/outside-inside)/(8*np.pi*r)
    inside_prime = throat**2/(r**3*inside)
    outside_prime = mass/(r*r*outside)
    sigma_prime = (inside_prime-outside_prime)/(4*np.pi*r)-sigma/r
    pressure_prime = (-mass**2/(r**3*outside**3)-inside_prime)/(8*np.pi*r)-pressure/r
    denominator = 1/outside-1/inside
    eta = np.divide(2*pressure, sigma+pressure, out=np.full_like(sigma, np.nan), where=sigma+pressure != 0)
    omega_squared = np.divide(8*np.pi*(pressure_prime-eta*sigma_prime), denominator,
        out=np.full_like(sigma, np.nan), where=denominator != 0)
    flux = throat**2/(4*np.pi*r**4*inside)
    return {'surface_energy': sigma, 'surface_pressure': pressure,
        'proper_shell_mass': 4*np.pi*r*r*sigma, 'interior_mass': throat**2/(2*r),
        'surface_energy_derivative': sigma_prime, 'surface_pressure_derivative': pressure_prime,
        'surface_momentum_flux': flux,
        'conservation_identity_residual': sigma_prime+2*(sigma+pressure)/r-flux,
        'fluid_sound_speed_squared': eta, 'fluid_radial_frequency_squared': omega_squared,
        'dec': (sigma >= np.abs(pressure)),
        'positive_causal_fluid': (sigma > pressure)&(pressure > 0)&(eta > 0)&(eta <= 1),
        'ordinary_surface_mass_density_ceiling': inside/(4*np.pi*r)}


def planar_sheet_limit(distance, coupling, nodes=128):
    """Exact off-sheet minimal scalar stress in the local planar reference.

    The finite-transparency ultraviolet asymptote is also the leading term
    beside a smooth curved background with a thin material sheet.
    """
    d = np.asarray(distance, float)
    if np.any(d <= 0) or coupling <= 0:
        raise ValueError('positive proper distance and optical coupling required')
    t, w = roots_laguerre(nodes)
    x = coupling*d
    integral = np.sum((w*t**3)[:, None]*x.ravel()[None, :]/(t[:, None]+x.ravel()[None, :]), axis=0).reshape(d.shape)
    magnitude = integral/(96*np.pi**2*d**4)
    asymptote = coupling/(48*np.pi**2*d**3)
    return {'energy': -magnitude, 'radial_pressure': np.zeros_like(d),
        'angular_pressure': magnitude, 'radial_enthalpy': -magnitude,
        'angular_enthalpy': np.zeros_like(d), 'asymptotic_magnitude': asymptote,
        'asymptotic_ratio': magnitude/asymptote}
