"""Charged-shell boundary controls and transverse insulation on a prescribed rail.

The spherical electrovacuum cells are boundary analogues, with flat centers
and neutral exteriors. They do not replace the scheduled active-rail metric.
Surface energy conditions and a radial sound-slope test are necessary
material controls; finite layers and a physical constitutive law remain open.
"""
from __future__ import annotations

import numpy as np
from numpy.polynomial.legendre import leggauss


def electrovacuum_jet(radius, mass, charge):
    r = np.asarray(radius)
    return (1-2*mass/r+charge**2/r**2,
            2*mass/r**2-2*charge**2/r**3,
            -4*mass/r**3+6*charge**2/r**4)


def shell_state(radius, inner_mass, inner_charge, outer_mass, outer_charge):
    """Static Israel surface density and isotropic tangential pressure."""
    fi, dpi, unused = electrovacuum_jet(radius, inner_mass, inner_charge)
    fo, dpo, unused = electrovacuum_jet(radius, outer_mass, outer_charge)
    if np.any(fi <= 0) or np.any(fo <= 0):
        raise ValueError('the static exterior branch requires positive metric factors')
    si, so = np.sqrt(fi), np.sqrt(fo)
    sigma = (si-so)/(4*np.pi*radius)
    pressure = (dpo/so-dpi/si)/(16*np.pi)-sigma/2
    return sigma, pressure


def shell_potential_jet(radius, inner_mass, inner_charge, outer_mass,
                        outer_charge, sound_squared):
    """V,V',V'' for Rdot^2+V=0 at a static fixed-charge shell.

    The two electrovacuum mass/charge parameters stay fixed under this local
    radial perturbation. Surface conservation gives m'=-8 pi R p and
    sigma'=-2(sigma+p)/R; sound_squared is the local dp/dsigma.
    """
    r = radius
    sigma, pressure = shell_state(r, inner_mass, inner_charge, outer_mass, outer_charge)
    if np.any(sigma <= 0):
        raise ValueError('positive surface energy required for the potential')
    fi, fip, fipp = electrovacuum_jet(r, inner_mass, inner_charge)
    fo, fop, fopp = electrovacuum_jet(r, outer_mass, outer_charge)
    d, dp, dpp = fi-fo, fip-fop, fipp-fopp
    y = 4*np.pi*r*sigma
    yp = -4*np.pi*(sigma+2*pressure)
    ypp = 8*np.pi*(1+2*sound_squared)*(sigma+pressure)/r
    value = (fi+fo)/2-y*y/4-d*d/(4*y*y)
    first = (fip+fop)/2-y*yp/2-d*dp/(2*y*y)+d*d*yp/(2*y**3)
    second = ((fipp+fopp)/2-(yp*yp+y*ypp)/2
              -(dp*dp+d*dpp)/(2*y*y)+2*d*dp*yp/y**3
              +d*d*ypp/(2*y**3)-3*d*d*yp*yp/(2*y**4))
    return value, first, second


def condenser_parameters(outer_radius, charge, inner_rest_mass, outer_fraction):
    """a=1 parametrization with positive shell energy on the exterior branch.

    outer_fraction=m_outer/(b sqrt(f_gap(b))) lies strictly between 0 and 1.
    A separate minimum-of-f check is needed throughout the electric gap.
    """
    b, q, mi, fraction = np.broadcast_arrays(
        outer_radius, charge, inner_rest_mass, outer_fraction)
    if np.any(b <= 1) or np.any((mi <= 0)|(mi >= 1)) or np.any((fraction <= 0)|(fraction >= 1)):
        raise ValueError('ordered shells and positive exterior-branch mass fractions required')
    gap_mass = (q*q+2*mi-mi*mi)/2
    fb = electrovacuum_jet(b, gap_mass, q)[0]
    mo = fraction*b*np.sqrt(np.maximum(fb, 0))
    outer_mass = gap_mass-q*q/(2*b)+mo*np.sqrt(np.maximum(fb, 0))-mo*mo/(2*b)
    minimum_radius = np.clip(q*q/gap_mass, 1, b)
    minimum_f = electrovacuum_jet(minimum_radius, gap_mass, q)[0]
    return gap_mass, outer_mass, mo, minimum_f


def electric_gap_energy(inner_radius, outer_radius, gap_mass, charge, order=96):
    """Proper field energy and the gap's infinity-normalized Killing energy.

    The latter also needs multiplication by the matching clock factor A,
    where g_tt=-A^2 f_gap and A^2=f_outer(b)/f_gap(b).
    """
    a, b, mass, q = np.broadcast_arrays(inner_radius, outer_radius, gap_mass, charge)
    nodes, weights = leggauss(order)
    r = (a[..., None]+b[..., None])/2+(b-a)[..., None]*nodes/2
    f = electrovacuum_jet(r, mass[..., None], q[..., None])[0]
    if np.any(f <= 0):
        raise ValueError('positive metric throughout the electric gap required')
    proper = q*q*(b-a)/4*np.sum(weights/(r*r*np.sqrt(f)), axis=-1)
    coordinate_killing = q*q/2*(1/a-1/b)
    return proper, coordinate_killing


def transverse_magnetic_moments(density, velocity):
    """Paired transverse B fields, averaged over the two angular directions.

    Their material-frame tensor is (u,+u,0,0) in (rho,pr,j,pt).
    Oppositely directed cell Poynting fluxes are assumed to cancel in the
    angular average. This is a necessary tensor, without boundary hardware.
    """
    u, v = np.broadcast_arrays(density, velocity)
    gamma_squared = 1/(1-v*v)
    energy = gamma_squared*(1+v*v)*u
    return np.array([energy, energy, 2*gamma_squared*v*u, np.zeros_like(u)])


def magnetic_cell_work(density, radial_length, radius):
    """Exact endpoint split for transverse flux variable K=u (ell R)^2.

    Per unit material label volume U=K/ell; two equal transverse orientations
    have zero net angular pressure. Changes of K are external field work;
    changes of 1/ell are the radial compression work. Includes no new losses.
    """
    u, ell, r = np.broadcast_arrays(density, radial_length, radius)
    k = u*(ell*r)**2
    inverse_length = 1/ell
    electrical = np.diff(k, axis=0)*(inverse_length[1:]+inverse_length[:-1])/2
    mechanical = np.diff(inverse_length, axis=0)*(k[1:]+k[:-1])/2
    energy = u*ell*r*r
    return electrical, mechanical, energy
