"""Resolved Higgs-portal vacuum response on a saved joint condensate.

This is a neutral spectator scalar, not the coupled charged fluctuations of
the condensate. The finite response subtracts the massless ground state on
the SAME joined geometry. A controlled transparent plateau makes the two
operators identical near the interior observations. The absolute curved
vacuum and its geometric junction regularity remain separate quantities.
"""
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from scipy.interpolate import PPoly
from scipy.linalg import solve_banded
from scipy.linalg.lapack import dpttrf

from .condensate_joint import JointParameters, JointGeometry, physical_parameters
from .condensate_joint_audit import required_tensor
from .condensate_rail import load_retained_geometry
from .curved_boundary import radial_mesh, tensor_from_moments
from .screened_condensate import CondensateParameters, field_stress


class JoinedProfile:
    """Both asymptotic ends, with a continuous radial coordinate at the cut."""
    def __init__(self, root, branch='r12_q0.85_potential_x2'):
        self.path = Path(root)/'supporting_reports/data/condensate_joint'/f'{branch}_solution.npz'
        with np.load(self.path) as data:
            self.setup = JointParameters(**{k: float(data[k]) for k in JointParameters.__dataclass_fields__})
            self.solution = SimpleNamespace(sol=PPoly.construct_fast(data['coefficients'].copy(),
                data['knots'].copy(), axis=1), p=data['eigenparameters'].copy())
        self.retained = load_retained_geometry(root)
        self.core = JointGeometry(self.retained, self.setup)
        self.material = CondensateParameters()
        self.gravity, self.clock, self.omega = physical_parameters(self.solution.p, self.setup, self.material)
        self.v = self.setup.vacuum_scale
        self.eta = self.gravity/self.v**2
        self.cut = self.core.x_start
        self.slope = np.sqrt(self.core.boundary.inner_f)
        self.lapse_at_cut = float(self.retained.values(self.cut)[1])

    def values(self, coordinate):
        x = np.asarray(coordinate, float)
        rc, ac, bc = self.retained.values(x)
        r = self.setup.physical_join+(self.cut-x)*self.slope
        rout = np.maximum(self.v*r, self.setup.inner_radius)
        t = (rout-self.setup.inner_radius)/(self.setup.exterior_extent-self.setup.inner_radius)
        fields = self.solution.sol(np.clip(t, 0, 1))
        f = 1-2*fields[6]/rout
        sigma = np.where(t <= 1, np.exp(fields[7]), 1.)
        return (np.where(x < self.cut, r, rc),
                np.where(x < self.cut, sigma*np.sqrt(f), self.clock*ac/self.lapse_at_cut),
                np.where(x < self.cut, self.slope/np.sqrt(f), bc))

    def higgs(self, coordinate):
        x = np.asarray(coordinate, float)
        r = self.v*(self.setup.physical_join+(self.cut-x)*self.slope)
        t = (r-self.setup.inner_radius)/(self.setup.exterior_extent-self.setup.inner_radius)
        outer = self.solution.sol(np.clip(t, 0, 1))[2]
        outer = np.where(t <= 1, outer, 1.)
        core_t = self.core.fraction_at_coordinate(np.clip(x, self.cut, self.setup.positive_extent))
        inner = self.solution.sol(core_t)[10]
        inner = np.where(x <= self.setup.positive_extent, inner, 1.)
        return np.where(x < self.cut, outer, inner)

    def mass_squared(self, coordinate, portal, plateau=1e-7):
        """Portal mass with a C-infinity, numerically small transparent plateau.

        For |h| >= 2*plateau this is exactly portal*v^2*h^2. For
        |h| <= plateau it is zero. Varying plateau tests this approximation.
        """
        if portal < 0 or plateau <= 0:
            raise ValueError('nonnegative portal and positive plateau required')
        h = self.higgs(coordinate)
        t = np.clip(abs(h)/plateau-1, 1e-12, 1-1e-12)
        logit = 1/(1-t)-1/t
        switch = np.exp(-np.logaddexp(0., -logit))
        switch = np.where(abs(h) <= plateau, 0., np.where(abs(h) >= 2*plateau, 1., switch))
        return portal*self.v**2*h*h*switch

    def demanded_remainder(self, coordinate):
        t = self.core.fraction_at_coordinate(coordinate)
        _, a, _, _ = self.core.values(t)
        material = field_stress(self.solution.sol(t)[8:], self.omega, self.material, 1., self.clock*a)
        required = required_tensor(self.core, t)
        counted = self.gravity*self.v**2*np.array([material[k] for k in
            ['energy', 'radial_pressure', 'tangential_pressure']])
        remainder = required-counted
        return np.concatenate((remainder, [remainder[0]+remainder[1], remainder[0]+remainder[2]]), axis=0)


def schur_factors(diagonal, links):
    """Left and right Schur pivots of a positive tridiagonal operator."""
    left, _, info = dpttrf(diagonal.copy(), -links.copy())
    right, _, other = dpttrf(diagonal[::-1].copy(), -links[::-1].copy())
    if info or other:
        raise ValueError('Euclidean operator is not positive')
    return left, right[::-1]


def schur_difference(base, shifted, links, increment):
    """Positive difference recurrence, avoiding coincident Green cancellation."""
    n = len(increment)
    band = np.zeros((2, n))
    band[0] = 1.
    band[1, :-1] = -links**2/(base[:-1]*shifted[:-1])
    return solve_banded((1, 0), band, increment.copy(), check_finite=False)


@dataclass
class SmoothRadialProblem:
    coordinate: np.ndarray
    radius: np.ndarray
    lapse: np.ndarray
    radial_scale: np.ndarray
    links: np.ndarray
    mass_squared: np.ndarray
    probes: np.ndarray

    @classmethod
    def create(cls, profile, probes, spacing=1/256, extent=96., plateau=1e-7):
        x = radial_mesh(spacing, extent, np.r_[profile.cut, probes])
        r, a, b = profile.values(x)
        rm, am, bm = profile.values((x[1:]+x[:-1])/2)
        links = am*rm*rm/(bm*np.diff(x))
        mass = profile.mass_squared(x, 1., plateau)
        indexes = np.searchsorted(x, probes)
        if np.any(mass[indexes] != 0):
            raise ValueError('response witnesses must lie in the common massless region')
        return cls(x, r, a, b, links, mass, indexes)

    def mode(self, frequency, angular_index, portals):
        h = np.diff(self.coordinate)
        volume = (h[:-1]+h[1:])/2
        r, a, b = self.radius[1:-1], self.lapse[1:-1], self.radial_scale[1:-1]
        q = a*b*(angular_index*(angular_index+1)+frequency**2*r*r/(a*a))
        diagonal = self.links[:-1]+self.links[1:]+volume*q
        inner_links = self.links[1:-1]
        left, right = schur_factors(diagonal, inner_links)
        i = self.probes-1
        denominator = left[i]+right[i]-diagonal[i]
        green = 1/denominator
        # Reconstruct normal fluxes from face fluxes and half-cell source.
        zl = left[i]-self.links[i+1]-h[i+1]*q[i]/2
        zr = -(right[i]-self.links[i]-h[i]*q[i]/2)
        p = a[i]*r[i]**2/b[i]
        result = []
        for portal in portals:
            delta_q = portal*a*b*r*r*self.mass_squared[1:-1]
            increment = volume*delta_q
            ml, mr = schur_factors(diagonal+increment, inner_links)
            dl = schur_difference(left, ml, inner_links, increment)[i]
            dr = schur_difference(right[::-1], mr[::-1], inner_links[::-1], increment[::-1])[::-1][i]
            ds = dl+dr-increment[i]
            gm = 1/(denominator+ds)
            dg = -ds*green*gm
            dzl = dl-h[i+1]*delta_q[i]/2
            dzr = -dr+h[i]*delta_q[i]/2
            mixed = ((dzl*zr+zl*dzr+dzl*dzr)*gm+zl*zr*dg)/(p*p)
            result.append(np.stack((-frequency**2*dg/(a[i]**2),
                mixed/(b[i]**2), angular_index*(angular_index+1)*dg/(2*r[i]**2)), axis=-1))
        return np.array(result)


def join_curvature(profile):
    """One-sided Ricci data from the two Einstein tensors at the internal cut."""
    y = profile.solution.sol(0.)
    material = field_stress(y[:6], profile.omega, profile.material,
        profile.core.boundary.inner_f, np.exp(y[7]))
    outside = profile.gravity*profile.v**2*np.array([material[k] for k in
        ['energy', 'radial_pressure', 'tangential_pressure']])
    inside = required_tensor(profile.core, 0.)
    # R_hat00=4pi(rho+pr+2pt), R_hatrr=4pi(rho+pr-2pt),
    # R_hatthetatheta=4pi(rho-pr). The scalar is 8pi(rho-pr-2pt).
    def ricci(t):
        e, p, q = t
        return np.array([4*np.pi*(e+p+2*q), 4*np.pi*(e+p-2*q),
                         4*np.pi*(e-p), 8*np.pi*(e-p-2*q)])
    return {'inside_tensor': inside.tolist(), 'outside_tensor': outside.tolist(),
        'inside_ricci_00_rr_tt_scalar': ricci(inside).tolist(),
        'outside_ricci_00_rr_tt_scalar': ricci(outside).tolist(),
        'ricci_jump_outside_minus_inside': (ricci(outside)-ricci(inside)).tolist()}


def junction_asymptote(inside, outside):
    """Interior d^-2 coefficients for one minimal scalar at a C1 metric join.

    d is proper distance to the cut. These are the leading reflected vacuum
    terms relative to a smooth continuation of the interior. Smooth local
    renormalization terms cannot change these one-sided bulk coefficients.
    """
    inside, outside = np.asarray(inside), np.asarray(outside)
    de, dp, dt = outside-inside
    if abs(dp) > 1e-8*max(np.max(abs(inside)), np.max(abs(outside))):
        raise ValueError('a curvature-only join requires continuous radial pressure')
    radial_second_jump = -4*np.pi*de
    lapse_second_jump = 8*np.pi*dt-radial_second_jump
    a, r = lapse_second_jump, radial_second_jump
    rho = -(2*a+3*r)/(480*np.pi**2)
    pt = (3*a+7*r)/(960*np.pi**2)
    return {'lapse_second_jump': a, 'radius_second_over_radius_jump': r,
        'ricci_scalar_jump': -2*a-4*r,
        'tensor_d_minus_2': np.array([rho, 0., pt, rho, rho+pt])}


def local_born_reflection(k, cosine, lapse_jump, radius_jump, envelope_length=1.):
    """First Born reflection from a compact C1 quadratic metric perturbation.

    On z>0: delta(log A)=a*z^2*exp(-z/L)/2 and
    delta(log R)=b*z^2*exp(-z/L)/2. A direct Laplace transform
    integrates the full linearized radial potential, including the
    frequency-dependent principal coefficients and their derivatives.
    """
    k, c = np.asarray(k), np.asarray(cosine)
    a, b, rate = lapse_jump, radius_jump, 1/envelope_length
    t = 2*k+rate
    # Integral of (z^2 exp(-rate*z))'' exp(-2k*z).
    second = 8*k*k/t**3
    potential_integral = (b/2+a/4)*second-2*k*k*(a*c*c+b*(1-c*c))/t**3
    return -potential_integral/(2*k)
