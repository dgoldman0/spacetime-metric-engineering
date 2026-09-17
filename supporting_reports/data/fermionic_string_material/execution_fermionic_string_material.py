"""Finite-width Abelian-Higgs vortices and conditional fermion duty screens.

The bulk normalization is L = |D Phi|^2/2 - H^2/4
- lambda_h (|Phi|^2-eta^2)^2/8, as in Ringeval, hep-ph/0007015,
Eqs. (2), (3), (10).  With e=q*c_phi, rho=e*eta*r and
beta=lambda_h/e^2, a unit vortex has mu=pi*eta^2*B(beta).

This module solves the uncharged classical vortex background. Carrier spectra,
backreaction and quantum stability require separate calculations. All masses
and Fermi momenta use hbar=c=1.
"""
from dataclasses import dataclass

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import solve_bvp
from scipy.interpolate import CubicHermiteSpline
from scipy.optimize import brentq


_CARRIER_COEFFICIENTS = {
    "canonical_two_branches": 2.,
    "printed_ringeval_two_branches": 1.,
}


@dataclass
class VortexProfile:
    beta: float
    log_rho: np.ndarray
    state: np.ndarray
    state_derivative: np.ndarray
    tolerance: float
    maximum_rms_residual: float
    iterations: int

    def evaluate_log(self, log_rho, derivative=0):
        spline = CubicHermiteSpline(self.log_rho, self.state.T,
                                   self.state_derivative.T, extrapolate=False)
        return np.moveaxis(spline(log_rho, nu=derivative), -1, 0)


def vortex_rhs(log_rho, state, beta):
    """State is (f, df/dlog(rho), a, da/dlog(rho))."""
    f, p, a, q = state
    radius_squared = np.exp(2*np.asarray(log_rho))
    return np.array([p, (1-a)**2*f + .5*beta*radius_squared*f*(f*f-1),
                     q, 2*q-radius_squared*f*f*(1-a)])


def _vortex_jac(log_rho, state, beta):
    f, _, a, _ = state
    radius_squared = np.exp(2*np.asarray(log_rho))
    jac = np.zeros((4, 4, len(log_rho)))
    jac[0, 1] = jac[2, 3] = 1
    jac[1, 0] = (1-a)**2+.5*beta*radius_squared*(3*f*f-1)
    jac[1, 2] = -2*(1-a)*f
    jac[3, 0] = -2*radius_squared*f*(1-a)
    jac[3, 2] = radius_squared*f*f
    jac[3, 3] = 2
    return jac


def _boundary(left, right):
    # Regular Frobenius behavior f~c*rho, a~d*rho^2 at the small inner cut.
    return np.array([left[1]-left[0], left[3]-2*left[2],
                     right[0]-1, right[2]-1])


def _initial_state(log_rho, beta, previous):
    rho = np.exp(log_rho)
    if previous is None:
        scale = beta**(-.125)
        f = np.tanh(rho/scale)
        p = rho/scale*(1-f*f)
        a = rho*rho/(rho*rho+scale*scale)
        return np.array([f, p, a, 2*a*(1-a)])
    clipped = np.clip(log_rho, previous.log_rho[0], previous.log_rho[-1])
    state = previous.evaluate_log(clipped)
    outer = log_rho > previous.log_rho[-1]
    state[:, outer] = np.array([1., 0., 1., 0.])[:, None]
    inner = log_rho < previous.log_rho[0]
    ratio = np.exp(log_rho[inner]-previous.log_rho[0])
    state[:2, inner] *= ratio
    state[2:, inner] *= ratio**2
    return state


def solve_vortex(beta, *, mesh_points=500, tolerance=2e-6, inner_radius=1e-5,
                 outer_tail=20., outer_minimum=30., max_nodes=30000,
                 previous=None):
    """Solve one unit-winding vortex on a logarithmic radial mesh.

    The outer cut is max(outer_minimum, outer_tail/sqrt(beta)). Continuation
    from a neighboring beta is optional. Positive solutions are checked in
    the audit, independently of the collocation solver's success status.
    """
    if not np.isfinite(beta) or beta <= 0:
        raise ValueError("beta must be positive and finite")
    if (not all(np.isfinite(v) for v in (tolerance, inner_radius, outer_tail, outer_minimum))
            or mesh_points < 20 or max_nodes < mesh_points or not 0 < tolerance < 1
            or not 0 < inner_radius < 1 or outer_tail <= 0 or outer_minimum <= 1):
        raise ValueError("invalid vortex resolution, tolerance, or domain")
    outer_radius = max(outer_minimum, outer_tail/np.sqrt(beta))
    grid = np.linspace(np.log(inner_radius), np.log(outer_radius), mesh_points)
    result = solve_bvp(lambda t, y: vortex_rhs(t, y, beta), _boundary, grid,
                       _initial_state(grid, beta, previous), tol=tolerance,
                       fun_jac=lambda t, y: _vortex_jac(t, y, beta),
                       max_nodes=max_nodes)
    if not result.success:
        raise RuntimeError(f"vortex beta={beta:g}: {result.message}")
    return VortexProfile(float(beta), result.x, result.y,
                         vortex_rhs(result.x, result.y, beta), float(tolerance),
                         float(np.max(result.rms_residuals)), int(result.niter))


def _quadrature(profile, order):
    nodes, weights = leggauss(order)
    width = np.diff(profile.log_rho)
    middle = .5*(profile.log_rho[:-1]+profile.log_rho[1:])
    points = middle[:, None]+.5*width[:, None]*nodes
    measure = .5*width[:, None]*weights
    return points.ravel(), measure.ravel()


def energy_terms(log_rho, state, beta):
    """Integrands per dlog(rho): radial, angular, magnetic, potential."""
    f, p, a, q = state
    radius_squared = np.exp(2*np.asarray(log_rho))
    return np.array([p*p, (1-a)**2*f*f, q*q/radius_squared,
                     .25*beta*radius_squared*(1-f*f)**2])


def profile_energy(profile, *, order=12):
    points, weights = _quadrature(profile, order)
    return energy_terms(points, profile.evaluate_log(points), profile.beta) @ weights


def profile_diagnostics(profile):
    """Energy, Derrick identity, widths and independent quadrature checks."""
    points, weights = _quadrature(profile, 16)
    state = profile.evaluate_log(points)
    f, p, a, q = state
    rho = np.exp(points)
    terms = energy_terms(points, state, profile.beta)
    energies = terms @ weights
    lower_order = profile_energy(profile, order=8)
    f0, _, a0, _ = profile.state[:, 0]
    radius0 = np.exp(profile.log_rho[0])
    core = np.array([.5*f0*f0, .5*f0*f0, 2*a0*a0/radius0**2,
                     profile.beta*radius0**2/8])
    total = float(energies.sum()+core.sum())
    bps_squares = ((p-(1-a)*f)**2
                   +(q/rho-.5*rho*(1-f*f))**2) @ weights
    topological_boundary = 1-((1-a0)*f0*f0+a0)
    legacy_completion = (topological_boundary+bps_squares
                         +(profile.beta-1)/profile.beta*energies[3])
    # The separate gauge square and beta correction grow as 1/beta.
    # Combine them before integration to retain the same identity and
    # absolute accuracy when their individual integrals become very large.
    completion_kernel = ((p-(1-a)*f)**2+q*q/(rho*rho)
                         -q*(1-f*f)+.25*profile.beta*rho*rho*(1-f*f)**2)
    completion = topological_boundary+completion_kernel @ weights
    def radius_at(component, threshold):
        root = brentq(lambda t: profile.evaluate_log(t)[component]-threshold,
                      profile.log_rho[0], profile.log_rho[-1], xtol=1e-12)
        return float(np.exp(root))
    scalar_widths = {str(frac): radius_at(0, frac) for frac in (.5, .9, .99)}
    flux_widths = {str(frac): radius_at(2, frac) for frac in (.5, .9, .99)}
    panel_energy = (terms.sum(axis=0)*weights).reshape(-1, 16).sum(axis=1)
    prefix = np.concatenate([[0.], np.cumsum(panel_energy)])
    nodes, gauss_weights = leggauss(16)
    def energy_radius(frac):
        target = frac*prefix[-1]
        panel = int(np.searchsorted(prefix, target)-1)
        left, right = profile.log_rho[panel:panel+2]
        def partial(t):
            samples = .5*(left+t)+.5*(t-left)*nodes
            integral = .5*(t-left)*np.dot(gauss_weights,
                energy_terms(samples, profile.evaluate_log(samples), profile.beta).sum(axis=0))
            return prefix[panel]+integral-target
        return float(np.exp(brentq(partial, left, right, xtol=1e-12)))
    energy_widths = {str(frac): energy_radius(frac) for frac in (.5, .9, .99)}
    return dict(beta=profile.beta, tension_factor_B=total,
        energy_integral_truncated=float(energies.sum()),
        regular_inner_core_energy_estimate=float(core.sum()),
        energy_contributions=dict(zip(("scalar_radial", "scalar_angular", "magnetic", "potential"),
                                      (float(v) for v in energies+core))),
        gauss8_gauss16_difference=float(np.max(abs(energies-lower_order))),
        virial_magnetic_minus_potential=float(energies[2]+core[2]-energies[3]-core[3]),
        virial_relative_to_total=float(abs(energies[2]+core[2]-energies[3]-core[3])/total),
        square_completion_identity_error=float(abs(energies.sum()-completion)),
        square_completion_legacy_unstable_error=float(abs(energies.sum()-legacy_completion)),
        square_completion_evaluation="expanded gauge square plus beta correction before integration",
        topological_derivative_integral_error=float(abs(
            (2*p*(1-a)*f+q*(1-f*f)) @ weights-topological_boundary)),
        bps_squares_integral=float(bps_squares),
        scalar_radius_rho=scalar_widths, enclosed_flux_radius_rho=flux_widths,
        enclosed_energy_radius_rho=energy_widths,
        inner_radius_rho=float(radius0), outer_radius_rho=float(np.exp(profile.log_rho[-1])),
        scalar_range=[float(f.min()), float(f.max())],
        gauge_range=[float(a.min()), float(a.max())],
        minimum_scalar_log_derivative=float(p.min()), minimum_gauge_log_derivative=float(q.min()),
        maximum_collocation_rms_residual=profile.maximum_rms_residual,
        solver_nodes=len(profile.log_rho), solver_iterations=profile.iterations,
        requested_tolerance=profile.tolerance)


def critical_tension_factor(stretch, escape_ratio, maximum_loop_size, *,
                            normalization="canonical_two_branches"):
    """Largest B meeting the specified escape and Yukawa-loop diagnostics.

    These two dimensionless cuts define an illustrative screening rectangle.
    Their intersection supplies neither a leakage rate nor a loop correction
    to the scalar potential.
    """
    lam, ratio, loop = map(float, (stretch, escape_ratio, maximum_loop_size))
    if not all(np.isfinite(v) and v > 0 for v in (lam, ratio, loop)):
        raise ValueError("positive finite carrier-screen limits required")
    if normalization not in _CARRIER_COEFFICIENTS:
        raise ValueError("unknown carrier normalization")
    return 16*lam*lam*ratio*ratio*loop/_CARRIER_COEFFICIENTS[normalization]


def radius_at_fixed_tension(radius_rho, tension_factor, *, gauge_coupling=1.):
    """Return r*sqrt(mu) from rho=e*eta*r and mu=pi*eta^2*B."""
    rho, B, e = np.broadcast_arrays(radius_rho, tension_factor, gauge_coupling)
    if not all(np.isfinite(v).all() and np.all(v > 0) for v in (rho, B, e)):
        raise ValueError("positive finite radii, tension factors and couplings required")
    return rho*np.sqrt(np.pi*B)/e


def fermion_duty(tension_factor, stretch, *, escape_ratio=1., gauge_coupling=1.,
                 beta=1., normalization="canonical_two_branches"):
    """Required g and dimensionless diagnostics for two balanced branches.

    escape_ratio specifies k_F/(g*eta), not a proved leakage rate. The printed
    Ringeval coefficient is retained as a separately named sensitivity case.
    No flavor or particle/antiparticle degeneracy is silently introduced.
    delta_lambda is an order-of-magnitude loop-size diagnostic with unit
    coefficient; no renormalization prescription or stability claim is made.
    """
    B, lam, ratio, e, coupling_ratio = map(float,
        (tension_factor, stretch, escape_ratio, gauge_coupling, beta))
    if not all(np.isfinite(v) and v > 0 for v in (B, lam, ratio, e, coupling_ratio)):
        raise ValueError("positive finite material-screen parameters required")
    if normalization not in _CARRIER_COEFFICIENTS:
        raise ValueError("unknown carrier normalization")
    coefficient = _CARRIER_COEFFICIENTS[normalization]
    k_over_eta = np.pi*np.sqrt(coefficient*B)/lam
    g = k_over_eta/ratio
    loop = g*g/(16*np.pi*np.pi)
    quartic_loop = g**4/(16*np.pi*np.pi)
    lambda_h = coupling_ratio*e*e
    return dict(normalization=normalization, stretch=lam,
        carrier_energy_over_bare_tension=1/(lam*lam),
        tension_over_energy=(lam*lam-1)/(lam*lam+1),
        target_fermi_momentum_over_bulk_mass=ratio,
        fermi_momentum_over_eta=float(k_over_eta), required_yukawa_g=float(g),
        yukawa_loop_size_g2_over_16pi2=float(loop),
        escape_ratio_squared_times_yukawa_loop_size=float(ratio*ratio*loop),
        gauge_coupling=e, scalar_self_coupling=float(lambda_h),
        scalar_quartic_loop_size_g4_over_16pi2=float(quartic_loop),
        quartic_loop_size_over_scalar_self_coupling=float(quartic_loop/lambda_h),
        bulk_fermion_mass_over_vector_mass=float(g/e),
        bulk_fermion_mass_over_higgs_mass=float(g/(e*np.sqrt(coupling_ratio))),
        fermion_asymptotic_tail_over_vector_length=float(e/g),
        fermion_asymptotic_tail_over_higgs_length=float(e*np.sqrt(coupling_ratio)/g))
