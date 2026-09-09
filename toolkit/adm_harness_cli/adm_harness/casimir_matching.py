"""Finite interaction and bulk stresses of two disjoint scalar delta sheets.

Isolated sheet self-energies are absorbed in separately specified measured
surface masses. All returned interaction quantities retain their boundary
terms. Bulk profiles apply strictly away from the sheets.
"""
from functools import lru_cache

import numpy as np
from numpy.polynomial.legendre import leggauss


@lru_cache(maxsize=16)
def log_quadrature(nodes=512, upper=80.):
    x, weights = leggauss(nodes)
    low, high = -30., np.log(upper)
    logarithm = .5*(high-low)*x+.5*(high+low)
    y = np.exp(logarithm)
    return y, .5*(high-low)*weights*y


def scattering(y, x1, x2):
    r1, r2 = x1/(x1+y), x2/(x2+y)
    logarithm = -y-np.log1p(y/x1)-np.log1p(y/x2)
    denominator = -np.expm1(logarithm)
    odds = np.exp(logarithm)/denominator
    logdet_magnitude = np.where(logarithm > -np.log(2.),
        -np.log(denominator), -np.log1p(-np.exp(logarithm)))
    return r1, r2, denominator, odds, logdet_magnitude


def interaction(separation, lambda1, lambda2, nodes=512):
    if min(separation, lambda1, lambda2) <= 0:
        raise ValueError('positive separation and sheet couplings required')
    y, weights = log_quadrature(nodes)
    r1, r2, denominator, odds, magnitude = scattering(y, lambda1*separation, lambda2*separation)
    prefactor = 1/(32*np.pi**2*separation**3)
    binding = prefactor*float(weights@(y*y*magnitude))
    traction = prefactor/separation*float(weights@(y**3*odds))
    response_derivative = prefactor*float(weights@(y*y*(2-r1-r2)*odds))
    return {'energy': -binding, 'pressure': -traction,
        'opacity_scaling_derivative': response_derivative,
        'effective_exponent': separation*traction/binding,
        'minimum_dec_holding_energy': separation*traction,
        'zero_wall_mass_held_energy_floor': separation*traction-binding,
        'zero_wall_mass_released_energy': -binding,
        'virial_identity_error': separation*traction+response_derivative-3*binding}


def gap_profile(separation, lambda1, lambda2, fractions, xi=0., nodes=512):
    """Free-subtracted continuum scalar stress at interior gap positions.

    xi=0 is the preceding model's canonical/minimal stress. xi=1/6 is
    a separately identified gravitational-coupling control. Channels are
    energy, normal pressure, and each transverse pressure. Isolated-sheet
    vacuum polarization tails remain included in the local stress.
    """
    fractions = np.asarray(fractions, float)
    if min(separation, lambda1, lambda2) <= 0 or np.any((fractions < .01) | (fractions > .99)):
        raise ValueError('positive model parameters and gap fractions in [.01,.99] required')
    y, weights = log_quadrature(nodes, 1600.)
    r1, r2, denominator, odds, _ = scattering(y, lambda1*separation, lambda2*separation)
    pressure = -float(weights@(y**3*odds))/(32*np.pi**2*separation**4)
    reflections = (r1[:, None]*np.exp(-y[:, None]*fractions[None, :])
                   +r2[:, None]*np.exp(-y[:, None]*(1-fractions[None, :])))
    local = (weights*y**3/denominator)@reflections/(16*np.pi**2*separation**4)
    energy = pressure/3+(xi-1/6)*local
    return np.stack([energy, np.full_like(energy, pressure), -energy], axis=-1)


def interaction_partition(separation, lambda1, lambda2, xi=0., nodes=512):
    """Finite interaction energy partition including the explicit sheet term.

    Isolated-sheet self-energies have already been separated. The bulk
    interaction includes both the gap and its exterior.
    """
    values = interaction(separation, lambda1, lambda2, nodes)
    derivative = values['opacity_scaling_derivative']
    surface = -(1-4*xi)*derivative
    bulk = separation*values['pressure']/3-4*(xi-1/6)*derivative
    return {'surface': surface, 'bulk': bulk, 'total': surface+bulk,
            'interaction_energy': values['energy']}


def gaussian_overlap(separation, strength=8., width=.16):
    """Integral V1*V2 for the previous Gaussian walls, per transverse area."""
    return strength**2/(2*np.sqrt(np.pi)*width)*np.exp(-separation**2/(4*width**2))


def reference_placement(profile):
    """Slice measures and necessary stress signs for extended boundary placement."""
    from scipy.integrate import simpson
    r = profile.radius.to_numpy()
    rho = profile.energy.to_numpy()
    f = profile.f.to_numpy()
    alpha = profile.alpha.to_numpy()
    hr = profile.radial_enthalpy.to_numpy()
    mass = .5*r*(1-f)
    weights = {'coordinate_mass': 4*np.pi*r*r,
               'proper_energy': 4*np.pi*r*r/np.sqrt(f),
               'lapse_weighted_slice_energy': 4*np.pi*r*r*alpha/np.sqrt(f)}
    result = {'points': len(r), 'inner_radius': float(r[0]), 'outer_radius': float(r[-1]),
        'inner_misner_sharp_mass': float(mass[0]), 'outer_misner_sharp_mass': float(mass[-1]),
        'endpoint_mass_change': float(mass[-1]-mass[0]),
        'proper_radial_length': float(simpson(1/np.sqrt(f), x=r)),
        'positive_energy_points': int((rho > 0).sum()),
        'negative_radial_enthalpy_points': int((hr < 0).sum()),
        'positive_energy_with_negative_radial_enthalpy_points': int(((rho > 0)&(hr < 0)).sum())}
    crossings = []
    for i in np.flatnonzero((rho[1:] > 0) != (rho[:-1] > 0)):
        crossings.append(float(r[i]-rho[i]*(r[i+1]-r[i])/(rho[i+1]-rho[i])))
    result['linearly_interpolated_energy_zero_radii'] = crossings
    for name, weight in weights.items():
        result[name] = float(simpson(weight*rho, x=r))
        result[name+'_positive_part'] = float(simpson(weight*np.maximum(rho, 0.), x=r))
        result[name+'_negative_part'] = float(simpson(weight*np.minimum(rho, 0.), x=r))
    return result
