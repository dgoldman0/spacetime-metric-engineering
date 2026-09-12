"""Material and mechanical-port controls for an aligned capacitor composite.

All energies are per material label and solid angle. A charged tensile skin
and a separate radial backing are treated as distinct constituents. The
coverage and energy-condition controls are necessary tests, with their
unbalanced reactions and missing constitutive information exposed.
"""
from __future__ import annotations

import numpy as np


def anisotropic_moments(density, radial_pressure, angular_pressure, velocity):
    """Boost a diagonal material tensor into the rail's ADM normal frame."""
    rho, pr, pt, v = np.broadcast_arrays(density, radial_pressure, angular_pressure, velocity)
    if np.any(abs(v) >= 1):
        raise ValueError('timelike material velocity required')
    gamma2 = 1/(1-v*v)
    return np.array([gamma2*(rho+v*v*pr), gamma2*(pr+v*v*rho),
                     gamma2*v*(rho+pr), pt])


def charged_skin_eos(tension, surface_number, fermi_coefficient):
    """Tension plus an ultrarelativistic two-dimensional trapped Fermi gas.

    Sigma=tau+C*n^(3/2), P=-tau+C*n^(3/2)/2. The derivative dP/dSigma
    is 1/2 at fixed tau. This supplies the surface thermodynamics, without
    assuming that the required trapping phase or its coupling exists.
    """
    tau, n, coefficient = np.broadcast_arrays(tension, surface_number, fermi_coefficient)
    if np.any(tau < 0) or np.any(n < 0) or np.any(coefficient <= 0):
        raise ValueError('nonnegative tension and number, positive Fermi coefficient required')
    fermi = coefficient*n**1.5
    return tau+fermi, -tau+fermi/2


def charged_skin_work(area, number, tension, fermi_coefficient):
    """Exact discrete chemical/area work for U=tau*A+C*N^(3/2)/sqrt(A).

    Charge supplied through a contact changes N and therefore has a chemical
    work port in addition to the electrostatic capacitor work.
    """
    a, n, tau, coefficient = np.broadcast_arrays(area, number, tension, fermi_coefficient)
    if np.any(a <= 0) or np.any(n < 0) or np.any(tau < 0) or np.any(coefficient <= 0):
        raise ValueError('positive area/coefficient and nonnegative inventory/tension required')
    if np.any(np.diff(tau, axis=0)) or np.any(np.diff(coefficient, axis=0)):
        raise ValueError('material coefficients are fixed along each history')
    invroot = 1/np.sqrt(a)
    population = coefficient*n**1.5
    chemical = np.diff(population, axis=0)*(invroot[1:]+invroot[:-1])/2
    mechanical = tau[:-1]*np.diff(a, axis=0)+(population[1:]+population[:-1])/2*np.diff(invroot, axis=0)
    energy = tau*a+population*invroot
    return chemical, mechanical, energy


def prepared_skin_backing(electric_energy, radial_length, radius):
    """Least prepared passive coefficients covering both electric stresses.

    The zero-carrier-energy skin has U_s=tau(x)*R^2, pr=0, pt=-rho.
    A maximally stiff directional backing has U_b=K(x)/ell, pr=rho, pt=0.
    Coverage of the electric tractions is imposed at every supplied time.
    Excess backing pressure and skin tension require external reactions;
    coverage alone is not a force-balanced cell solution.
    """
    electric, ell, r = np.broadcast_arrays(electric_energy, radial_length, radius)
    if np.any(electric < 0) or np.any(ell <= 0) or np.any(r <= 0):
        raise ValueError('nonnegative field energy and positive dimensions required')
    tension = np.max(electric/r**2, axis=0)
    backing = np.max(electric*ell, axis=0)
    skin_energy = tension[None, :]*r*r
    backing_energy = backing[None, :]/ell
    return dict(skin_energy=skin_energy, backing_energy=backing_energy,
                skin_coefficient=tension, backing_coefficient=backing,
                excess_radial_stress_energy=backing_energy-electric,
                excess_angular_tension_energy=skin_energy-electric)


def adiabatic_balancing_support(electric_energy, electric_mechanical_work, minimum_ratio=1.):
    """Best initial inventory for a support with opposite integrated stresses.

    Its mechanical work is the negative of the electric mechanical work.
    Additional stored energy can have zero pressure. The floor rho>=a*u_E
    labels an optimistic material-cost class, not a supplied equation of state.
    """
    if minimum_ratio < 1:
        raise ValueError('DEC balancing support requires at least unit energy ratio')
    electric = np.asarray(electric_energy)
    mechanical = np.asarray(electric_mechanical_work)
    prefix = np.concatenate([np.zeros_like(electric[:1]), np.cumsum(mechanical, axis=0)], axis=0)
    initial = np.max(minimum_ratio*electric+prefix, axis=0)
    return initial[None, :]-prefix


def controlled_balancing_support(electric_energy, electric_mechanical_work, energy_ratio):
    """Minimum-inventory opposite-stress support with its unloading port.

    With rho=a*u_E, pr=u_E, pt=-u_E, the support must exchange
    a*Delta(U_E)+W_mechanical,E through an additional controlled port.
    Electric and support stresses cancel in the complete cell average.
    """
    if energy_ratio < 1:
        raise ValueError('positive DEC support requires energy ratio >= 1')
    energy = energy_ratio*np.asarray(electric_energy)
    port = np.diff(energy, axis=0)+electric_mechanical_work
    return energy, port


def pressure_shared_floor(electric_density, available_pressure, family):
    """Credit the existing isotropic pressure to an internally balanced cell.

    Existing pressure p_used supplies part of the radial backing and adds to
    the skin's tangential load. New directional backing plus tensile skins
    therefore still cost 2*u_E even with that pressure credit. Fluid backing
    has both angular pressures and requires skins with tension 2*u_E.
    The DEC floor allows a general anisotropic material with no supplied EOS.
    """
    u, p = np.broadcast_arrays(electric_density, available_pressure)
    if np.any(u < 0) or np.any(p < 0):
        raise ValueError('nonnegative electric density and available pressure required')
    used = np.minimum(u, p)
    densities = dict(dec_floor=u+used, directional=2*u,
                     stiff_fluid=3*u-used, radiation_fluid=5*u-3*used)
    if family not in densities:
        raise ValueError('unknown composite family')
    return dict(density=densities[family], radial_pressure=u-used,
                angular_pressure=-u-used, used_pressure=used)


def retained_support_energy(minimum_energy, mechanical_work):
    """Smallest prepared inventory above the floor, retaining all supplied work."""
    floor = np.asarray(minimum_energy)
    prefix = np.concatenate([np.zeros_like(floor[:1]), np.cumsum(mechanical_work, axis=0)], axis=0)
    initial = np.max(floor-prefix, axis=0)
    return initial[None, :]+prefix


def local_mechanical_reuse(first_work, second_work):
    """Optimistic colocated reuse; opposite rest-frame work cancels instantly.

    This specifies a coupling duty, not an implemented mechanism, transported
    energy, or a global conserved energy on the prescribed time-dependent metric.
    """
    first, second = np.broadcast_arrays(first_work, second_work)
    reused = np.minimum(np.maximum(-first, 0), np.maximum(second, 0))
    total = first+second
    return dict(reused=reused, remaining_export=np.maximum(-total, 0),
                remaining_input=np.maximum(total, 0))
