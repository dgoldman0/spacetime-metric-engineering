"""A charge-symmetric straight-vortex carrier specialization.

Opposite Yukawa windings and axial gauge charges +/-1/2 give two
counterpropagating zero modes with identical transverse probability.
Their classical gauge and scalar source bilinears vanish separately.
This is a mean-field statement in a straight, stationary vortex; finite
curvature, massive transitions, quantum corrections and physical
manufacture remain additional requirements.
"""
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

from .coupled_holding_certificate import H_MIN, RADIUS_ERROR_BOUND
from .scheduled_optical_transfer import SPIN_FLOOR


def dirac_matrices():
    """Chiral basis with gamma5=diag(-1,-1,1,1), metric (+---)."""
    pauli = (np.array([[0, 1], [1, 0]], complex),
             np.array([[0, -1j], [1j, 0]]), np.diag([1., -1.]))
    zero, unit = np.zeros((2, 2)), np.eye(2)
    beta = np.block([[zero, unit], [unit, zero]])
    alpha = np.array([np.block([[-s, zero], [zero, s]]) for s in pauli])
    gamma5 = np.diag([-1., -1., 1., 1.])
    return beta, alpha, gamma5


def zero_mode_spinor(species=1):
    if species not in (-1, 1):
        raise ValueError("species must be +1 or -1")
    return np.array([1., 0., 0., 1j]) if species == 1 else np.array([0., 1., 1j, 0.])


def transverse_dirac_residual(radius, angle, scalar, gauge, mass_ratio, *,
                              amplitude=1., radial_derivative=None, species=1):
    """Apply the independent four-component transverse Hamiltonian.

    rho=e*eta*r; e*A_theta=-a/rho. Q=-species*gamma5/2, and
    the Yukawa mass matrix is beta*(g/e)*f*exp(i*species*gamma5*theta).
    F'=-(g/e*f+a/(2*rho))*F is supplied only when no derivative is given.
    """
    rho, phi, f, a, ratio, F = map(float, (radius, angle, scalar, gauge, mass_ratio, amplitude))
    if not np.isfinite([rho, phi, f, a, ratio, F]).all() or rho <= 0 or ratio <= 0:
        raise ValueError("finite fields and positive radius/mass ratio required")
    beta, alpha, gamma5 = dirac_matrices()
    psi = zero_mode_spinor(species)
    derivative = -(ratio*f+a/(2*rho))*F if radial_derivative is None else float(radial_derivative)
    ar = np.cos(phi)*alpha[0]+np.sin(phi)*alpha[1]
    at = -np.sin(phi)*alpha[0]+np.cos(phi)*alpha[1]
    charge = -species*gamma5/2
    mass = beta@np.diag(np.exp(1j*species*np.diag(gamma5)*phi))
    return (-1j*ar@(derivative*psi)-a/rho*at@charge@(F*psi)+ratio*f*mass@(F*psi))


def mode_bilinears(*, angle=.37, amplitude=1., species=1):
    """Local gauge four-current and Higgs amplitude/phase sources."""
    beta, alpha, gamma5 = dirac_matrices()
    psi = amplitude*zero_mode_spinor(species)
    charge = -species*gamma5/2
    phase = np.diag(np.exp(1j*species*np.diag(gamma5)*angle))
    density = np.vdot(psi, psi).real
    current = np.array([np.vdot(psi, a@charge@psi) for a in (np.eye(4), *alpha)])
    scalar = np.vdot(psi, beta@phase@psi)
    phase_source = np.vdot(psi, 1j*species*beta@gamma5@phase@psi)
    momentum = np.vdot(psi, alpha[2]@psi)
    return dict(probability_density=float(density), gauge_current=current,
                scalar_amplitude_source=scalar, scalar_phase_source=phase_source,
                longitudinal_velocity=float(momentum.real/density))


def normalized_zero_mode(profile, *, mass_ratio=1., order=16):
    """Normalize the analytic first-order zero mode on a resolved vortex.

    The integration uses the parent Hermite background and a separate
    high-order quadrature. The inner regular-core and asymptotic exterior
    estimates are retained explicitly in the normalization diagnostics.
    """
    ratio = float(mass_ratio)
    if not np.isfinite(ratio) or ratio <= 0 or order < 4:
        raise ValueError("positive mass ratio and quadrature order >=4 required")
    grid = profile.log_rho
    def rhs(t, _):
        f, _, a, _ = profile.evaluate_log(t)
        return [-ratio*np.exp(t)*f-a/2]
    solution = solve_ivp(rhs, (grid[0], grid[-1]), [0.], method="DOP853",
                         rtol=2e-11, atol=2e-12, dense_output=True, max_step=.08)
    if not solution.success:
        raise RuntimeError(solution.message)
    nodes, weights = leggauss(order)
    left, right = grid[:-1], grid[1:]
    points = .5*(left+right)[:, None]+.5*(right-left)[:, None]*nodes
    measures = .5*(right-left)[:, None]*weights
    logs = solution.sol(points.ravel())[0].reshape(points.shape)
    integrand = 4*np.pi*np.exp(2*points+2*logs)
    panels = (integrand*measures).sum(axis=1)
    inner = 2*np.pi*np.exp(2*grid[0])
    outer = 2*np.pi*np.exp(grid[-1]+2*solution.sol(grid[-1])[0])/ratio
    norm = inner+panels.sum()+outer
    prefix = np.r_[inner, inner+np.cumsum(panels)]
    def probability_radius(fraction):
        target = fraction*norm
        panel = min(len(left)-1, max(0, int(np.searchsorted(prefix, target)-1)))
        lo = left[panel]
        def cumulative(t):
            samples = .5*(lo+t)+.5*(t-lo)*nodes
            kernel = 4*np.pi*np.exp(2*samples+2*solution.sol(samples)[0])
            return prefix[panel]+.5*(t-lo)*np.dot(weights, kernel)-target
        return float(np.exp(brentq(cumulative, lo, right[panel], xtol=2e-12)))
    amplitude = np.exp(solution.sol(grid)[0])/np.sqrt(norm)
    return dict(log_rho=grid.copy(), radial_amplitude=amplitude,
                unnormalized_probability=float(norm), inner_probability_fraction=float(inner/norm),
                exterior_probability_fraction=float(outer/norm),
                probability_radius_rho={str(p): probability_radius(p) for p in (.5, .9, .99)},
                mass_ratio=ratio, quadrature_order=order)


def collision_pair_fraction(fermi_over_mass):
    """Fraction of filled opposite-branch number pairs with k1*k2>m^2.

    This is kinematic phase space for equal-mass bulk final particles,
    independent of transition amplitudes, Pauli factors of other states,
    background recoil and operating lifetime.
    """
    ratio = np.asarray(fermi_over_mass, float)
    if not np.isfinite(ratio).all() or np.any(ratio <= 0):
        raise ValueError("positive finite Fermi/bulk mass ratio required")
    threshold = 1/np.maximum(ratio, 1.)**2
    return np.maximum(0., 1-threshold+threshold*np.log(threshold))


def rotor_proper_stretch_lower():
    """Independent certified x and spin bounds in the material rest frame."""
    return (H_MIN-RADIUS_ERROR_BOUND)/np.sqrt(1-SPIN_FLOOR**2)


def flavor_screen(tension_factor, *, pair_flavors=1, yukawa=1., gauge_coupling=1.,
                  beta=1., stretch=None):
    """Count balanced species while preserving U=mu*(1+lambda^-2).

    Each pair adds two Dirac species with axial charges of magnitude 1/2.
    The equal occupation of N pairs gives u=N*kF^2/(2*pi). Fixed numbers
    under a uniform stretch retain the same elastic law. Loop diagnostics
    count species with a unit coefficient, without selecting a quantum
    renormalization prescription.
    """
    B, g, e, coupling, lam = map(float, (tension_factor, yukawa, gauge_coupling,
        beta, rotor_proper_stretch_lower() if stretch is None else stretch))
    if (not isinstance(pair_flavors, int) or pair_flavors < 1
            or not all(np.isfinite(v) and v > 0 for v in (B, g, e, coupling, lam))):
        raise ValueError("positive scales and integer flavor-pair count required")
    N = pair_flavors
    ratio = np.pi*np.sqrt(2*B/N)/(lam*g)
    return dict(pair_flavors=N, dirac_species=2*N, proper_stretch=lam,
        proper_fermi_over_bulk_mass=ratio,
        opposite_branch_open_pair_fraction=float(collision_pair_fraction(ratio)),
        two_bulk_equal_mass_channel_kinematically_closed=bool(ratio < 1),
        unit_coefficient_collective_yukawa_loop=2*N*g*g/(16*np.pi*np.pi),
        unit_coefficient_collective_quartic_over_tree=2*N*g**4/(16*np.pi*np.pi*coupling*e*e),
        homogeneous_MS_fermion_CW_log_coefficient_over_tree=16*N*g**4/(16*np.pi*np.pi*coupling*e*e),
        unit_coefficient_charge_weighted_gauge_loop=N*e*e/(16*np.pi*np.pi),
        mean_field_local_gauge_and_scalar_source_zero=True,
        quantum_corrected_potential_control_established=False,
        transition_rate_or_material_lifetime_computed=False)
