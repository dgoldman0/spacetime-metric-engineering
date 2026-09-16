"""Canonical scalar wall with a localized complex carrier condensate.

The action is Peter, hep-ph/9503408, equations (1)-(8), in c=hbar=1.
The normal coordinate is n; z is axial and theta is the hoop direction.
Numerical profiles use the global U(1) model. The containment tests are
necessary stress tests, with carrier replacement and external magnetic
energy accounted for by the caller. They supply no SI material assignment.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.integrate import simpson, solve_bvp
from scipy.optimize import linprog


@dataclass(frozen=True)
class WallParameters:
    coupling: float = .4
    mass_squared: float = .2
    vacuum: float = 1.
    wall_quartic: float = 1.
    carrier_quartic: float = 1.

    def __post_init__(self):
        values = (self.coupling, self.mass_squared, self.vacuum,
                  self.wall_quartic, self.carrier_quartic)
        if not np.isfinite(values).all() or min(values) <= 0:
            raise ValueError("positive finite couplings, mass squared and vacuum required")
        # Minimize the potential over |Sigma|^2 at each phi^2 >= 0.
        gap = max(2*self.coupling*self.vacuum**2-self.mass_squared, 0.)
        if gap**2 > self.wall_quartic*self.carrier_quartic*self.vacuum**4/2:
            raise ValueError("potential must be nonnegative relative to the chosen vacuum")

    @property
    def inverse_width(self):
        return .5*np.sqrt(self.wall_quartic)*self.vacuum

    @property
    def bare_tension(self):
        return 2*np.sqrt(self.wall_quartic)*self.vacuum**3/3

    @property
    def carrier_index(self):
        return .5*(np.sqrt(1+32*self.coupling/self.wall_quartic)-1)

    @property
    def linear_quench_w(self):
        """Zero of the lowest carrier fluctuation eigenvalue on the bare kink."""
        return self.inverse_width**2*self.carrier_index**2-self.mass_squared


def potential(phi, sigma, params):
    delta = np.asarray(phi)**2-params.vacuum**2
    sigma2 = np.asarray(sigma)**2
    return (params.wall_quartic*delta**2/8 + params.coupling*sigma2*delta
            + params.mass_squared*sigma2/2 + params.carrier_quartic*sigma2**2/4)


def equations(n, fields, params, w):
    phi, dphi, sigma, dsigma = fields
    delta = phi**2-params.vacuum**2
    return np.array([dphi, (params.wall_quartic*delta/2
                           + 2*params.coupling*sigma**2)*phi,
                     dsigma, (w+2*params.coupling*delta+params.mass_squared
                              + params.carrier_quartic*sigma**2)*sigma])


def stress_components(fields, params, *, omega=0., axial_k=0., hoop_k=0.):
    """Return (rho, p_z, p_theta, p_n), including all scalar field energy.

    Time/spatial phase gradients can coexist; the diagonal components remain
    valid even when mixed stresses also occur. Opposed populations may cancel
    those mixed components. This function makes no such cancellation claim.
    """
    phi, dphi, sigma, dsigma = np.asarray(fields)
    normal = (dphi**2+dsigma**2)/2
    temporal, axial, hoop = [k*k*sigma**2/2 for k in (omega, axial_k, hoop_k)]
    V = potential(phi, sigma, params)
    return np.array([temporal+normal+axial+hoop+V,
                     temporal-normal+axial-hoop-V,
                     temporal-normal-axial+hoop-V,
                     temporal+normal-axial-hoop-V])


def solve_profile(params, w, *, previous=None, extent=40., tolerance=1e-8,
                  initial_nodes=401):
    """Odd kink / even condensate BVP on one half of the wall.

    Vacuum boundary conditions at finite extent approximate the decaying
    tails. Continuation on w selects the populated branch. A failed solve
    raises an error and is never returned as a physical profile.
    """
    if (not np.isfinite([w, extent, tolerance]).all() or extent <= 0
            or tolerance <= 0 or initial_nodes < 5
            or params.mass_squared+w <= 0):
        raise ValueError("positive domain/tolerance and exponentially localized carrier required")
    n = np.linspace(0, extent, initial_nodes)
    if previous is None:
        width = .7*params.inverse_width
        amplitude = .9*np.sqrt(max(2*params.coupling*params.vacuum**2
                                   - params.mass_squared-w, 0.)/params.carrier_quartic)
        th, sech = np.tanh(width*n), 1/np.cosh(width*n)
        seed = np.array([params.vacuum*th, params.vacuum*width*sech**2,
                         amplitude*sech, -amplitude*width*sech*th])
    else:
        seed = previous.sol(n)

    def boundary(left, right):
        return np.array([left[0], left[3], right[0]-params.vacuum, right[2]])

    solution = solve_bvp(lambda x, y: equations(x, y, params, w), boundary,
                         n, seed, tol=tolerance, max_nodes=30000)
    if not solution.success:
        raise RuntimeError(f"wall profile failed at w={w}: {solution.message}")
    return solution


def profile_observables(solution, params, w, *, integration_nodes=8193):
    n = np.linspace(0, solution.x[-1], integration_nodes)
    fields = solution.sol(n)
    stress = stress_components(fields, params, omega=np.sqrt(max(-w, 0.)),
                               hoop_k=np.sqrt(max(w, 0.)))
    U, pz, ptheta, pn = 2*simpson(stress, x=n, axis=-1)
    I = float(2*simpson(fields[2]**2, x=n))
    return dict(w=float(w), energy=float(U), axial_pressure=float(pz),
                hoop_pressure=float(ptheta), normal_pressure_integral=float(pn),
                condensate_integral=I, current_magnitude=float(np.sqrt(abs(w))*I),
                center_condensate=float(fields[2, 0]),
                max_normal_pressure=float(np.max(np.abs(stress[3]))),
                minimum_potential=float(np.min(potential(fields[0], fields[2], params))),
                max_bvp_residual=float(np.max(solution.rms_residuals)),
                outer_tail_derivative=float(np.max(np.abs(fields[[1, 3], -1]))),
                nodes=int(solution.x.size))


def necessary_wall_gaps(facets, hoop):
    """Positive gaps reject classes; negative gaps alone provide no pass.

    All variables are local densities. u may vary freely at every sample.
    The membrane's averaged tensor is (u,z,-H/2); allowing integrated normal
    pressure N changes its last component to (N-H)/2.
    """
    A, B, C = np.asarray(facets, float)
    H = np.asarray(hoop, float)
    if (not np.isfinite(facets).all() or not np.isfinite(H).all()
            or np.any(H < 0)):
        raise ValueError("finite facets and nonnegative hoop tension required")
    G = np.maximum(A+H, B-H/2)
    return dict(
        # Canonical scalar identity: z+H <= u-N for V >= 0. N >= 0
        # preserves these two bounds even for a finite layer.
        canonical_joint_stress=G+H,
        # The actual static hoop-current ansatz has z=-u, u>=H.
        hoop_current_plane_stress=np.maximum.reduce([H, C-H/2, np.zeros_like(H)])+G/2,
        # Second residual facet >= B+3H/2 for z=-u, u>=H, N>=0.
        hoop_current_normal_compression=B+1.5*H)


def component_feasibility(target, field_floor, hoop, *, law):
    """Independent support-component LP at a single point.

    Target and hoop should be scaled to comparable order-one units by the
    caller. Variables are (u,z,N,radial B,radial photons,angular photons,
    angular membrane,dust). Mixed stresses are assumed to cancel.
    """
    rho, axial, angular = np.asarray(target, float)
    H, floor = float(hoop), float(field_floor)
    if not np.isfinite([rho, axial, angular, H, floor]).all() or min(H, floor) < 0:
        raise ValueError("finite tensor and nonnegative hoop/field floor required")
    eq = [[1., 0., 0., 1., 1., 1., 1., 1.],
          [0., 1., 0., -1., 1., 0., 0., 0.],
          [0., 0., .5, 1., 0., .5, -1., 0.]]
    rhs = [rho, axial, angular+H/2]
    # DEC in the axial and normal directions; u>=H handles the hoop.
    ub = [[-1., 1., 0., 0., 0., 0., 0., 0.],
          [-1., -1., 0., 0., 0., 0., 0., 0.],
          [-1., 0., 1., 0., 0., 0., 0., 0.]]
    b_ub = [0., 0., 0.]
    normal_bound = (0., 0.)
    if law in ("hoop_current_plane_stress", "hoop_current_normal_compression"):
        eq.append([1., 1., 0., 0., 0., 0., 0., 0.])
        rhs.append(0.)
        if law == "hoop_current_normal_compression":
            normal_bound = (0., None)
    elif law == "canonical_joint_stress":
        # Allow finite normal compression for a stronger independent check.
        ub.append([-1., 1., 1., 0., 0., 0., 0., 0.])
        b_ub.append(-H)
        normal_bound = (0., None)
    elif law != "free_axial_stress":
        raise ValueError("unknown constitutive class")
    return linprog(np.zeros(8), A_eq=eq, b_eq=rhs, A_ub=ub, b_ub=b_ub,
                   bounds=[(H, None), (None, None), normal_bound, (floor, None)]
                          + [(0., None)]*4, method="highs")
