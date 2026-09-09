"""Microscopic tree matching and normal bound states for a scalar Fermi wall.

Quantum vacuum dressing, curvature, and normal-shape response are separate
from these planar occupied-mode calculations.
"""
import numpy as np
from scipy.linalg import eigh_tridiagonal


def transverse_gap_squared(localization):
    """Lowest excitation above the planar Dirac zero branch, in width units.

    Squaring the Dirac operator gives -d_u^2+a^2-a(a+1)sech^2(u).
    Bound eigenvalues are n(2a-n), with integers 0 <= n < a; the
    continuum starts at a^2. The smaller threshold limits zero-band filling.
    """
    a = np.asarray(localization, float)
    if np.any(a <= 0) or not np.isfinite(a).all():
        raise ValueError('finite positive localization required')
    return np.where(a > 1, 2*a-1, a*a)


def dirac_squared_levels(localization, spacing, extent=20.):
    """Independent centered finite-difference spectrum, with distant endpoints."""
    if min(localization, spacing, extent) <= 0:
        raise ValueError('positive spectral parameters required')
    intervals = int(np.ceil(2*extent/spacing))
    u = np.linspace(-extent, extent, intervals+1)[1:-1]
    h = 2*extent/intervals
    a = localization
    diagonal = 2/h**2+a*a-a*(a+1)/np.cosh(u)**2
    off = np.full(len(u)-1, -1/h**2)
    eigenvalues = eigh_tridiagonal(diagonal, off, eigvals_only=True,
        select='i', select_range=(0, 1), check_finite=False)
    return eigenvalues


def tree_level_match(width, integrated_strength, tension, gas_energy,
                     gravitational_quantum_scale, flavors=1, localization=2.1):
    """Couplings for a specified planar profile and occupied surface gas.

    eta=G*hbar/L^2 converts microscopic surface energies to geometric ones.
    flavors counts identical Dirac species, each with one positive-energy
    massless surface branch. Renormalized loop corrections are unevaluated.
    """
    if min(width, integrated_strength, tension, gas_energy,
           gravitational_quantum_scale, flavors, localization) <= 0:
        raise ValueError('positive matching data required')
    eta, d = gravitational_quantum_scale, width
    v2 = 3*tension*d/(4*eta)
    scalar_self = 2/(v2*d*d)
    optical = integrated_strength/(2*v2*d)
    vacuum_self = 2*optical**2/scalar_self
    yukawa = localization/(np.sqrt(v2)*d)
    fermi_momentum = (6*np.pi*gas_energy/(eta*flavors))**(1/3)
    bulk_mass = yukawa*np.sqrt(v2)
    gap = np.sqrt(transverse_gap_squared(localization))/d
    return {'width': d, 'integrated_strength': integrated_strength, 'flavors': flavors,
        'eta': eta, 'v_squared': v2, 'scalar_self_coupling': scalar_self,
        'optical_cross_coupling': optical, 'vacuum_self_coupling': vacuum_self,
        'yukawa_coupling': yukawa, 'localization': localization,
        'fermi_momentum': fermi_momentum, 'bulk_fermion_mass': bulk_mass,
        'first_transverse_gap': gap, 'confined_below_continuum': fermi_momentum < bulk_mass,
        'only_zero_branch_filled': fermi_momentum < gap,
        'quartic_determinant': scalar_self*vacuum_self-optical**2,
        'collective_yukawa_loop_measure': flavors*yukawa**2/(16*np.pi**2),
        'tension_reconstruction_error': eta*4*v2/(3*d)-tension,
        'gas_reconstruction_error': eta*flavors*fermi_momentum**3/(6*np.pi)-gas_energy,
        'optical_reconstruction_error': 2*optical*v2*d-integrated_strength}


def zero_band_yukawa_threshold(x, tension, gas_energy, flavors=1):
    """Minimum Yukawa at k_F*width=x for confinement to the zero branch.

    The thresholds coincide at x=1. For x>1, the first massive bound
    branch is stricter than escape into the bulk continuum.
    """
    x = np.asarray(x, float)
    if np.any(x <= 0) or min(tension, gas_energy, flavors) <= 0:
        raise ValueError('positive filling and material data required')
    localization = np.where(x <= 1, x, .5*(x*x+1))
    return np.sqrt(8*np.pi*gas_energy/(flavors*tension))*localization/x**1.5


def optimal_zero_band_scale(width, gas_energy, flavors=1):
    """Scale at the infimum x=sqrt(3); strict filling needs localization >2."""
    if min(width, gas_energy, flavors) <= 0:
        raise ValueError('positive scales required')
    return 2*np.pi*gas_energy*width**3/(np.sqrt(3)*flavors)
