"""Occupied neutral Dirac states in a counted scalar mass well.

Optical distance z satisfies dz=dl/A. The positive-energy Schur complement
of H=[[M,Q^T],[Q,-M]], Q=-d/dz+K A/R, is a scalar tridiagonal problem.
A staggered finite-volume discretization avoids a centered Dirac derivative's
duplicate low-energy branch. Vacuum polarization is a separate source.
"""
from dataclasses import dataclass

import numpy as np
from scipy.integrate import cumulative_simpson, simpson
from scipy.interpolate import CubicSpline, PchipInterpolator
from scipy.linalg import eigh_tridiagonal
from scipy.optimize import brentq

from .geometry_opening import StaticSlice


@dataclass
class MassWell:
    vacuum_scale: float = 12/6.8
    width: float = 1.
    radius: float = 6.8

    def __post_init__(self):
        if not np.isfinite([self.vacuum_scale, self.width, self.radius]).all() or min(
                self.vacuum_scale, self.width, self.radius) <= 0:
            raise ValueError('positive finite material parameters required')

    @property
    def quartic(self):
        return 8/(self.vacuum_scale*self.width)**2

    def values(self, proper, left, right):
        """Two separated 0-to-v interfaces of U=lambda*chi^2*(chi-v)^2/4."""
        tl = np.tanh((np.asarray(proper)-left)/self.width)
        tr = np.tanh((np.asarray(proper)-right)/self.width)
        sl, sr = 1-tl*tl, 1-tr*tr
        v, d = self.vacuum_scale, self.width
        chi = v*(1+(tr-tl)/2)
        first = v*(sr-sl)/(2*d)
        second = v*(tl*sl-tr*sr)/(d*d)
        potential = self.quartic*chi*chi*(chi-v)**2/4
        force = self.quartic*chi*(chi-v)*(2*chi-v)/2
        return chi, first, second, potential, force


class RailWell:
    """Repaired native static cache with its unit-lapse analytic tails."""

    def __init__(self, cache, well, tail_extent=48.):
        with np.load(cache) as data:
            x, r, a, b = [data[k] for k in ('coordinate', 'radius', 'lapse', 'radial_scale')]
        if tail_extent <= x[-1] or abs(x[0]+x[-1]) > 1e-10:
            raise ValueError('tail extent must extend both native cache ends')
        if max(abs(a[[0, -1]]-1).max(), abs(b[[0, -1]]-1).max()) > 1e-10:
            raise ValueError('unit-lapse, unit-radial-scale tails required')
        tail_r2 = r[[0, -1]]**2-x[[0, -1]]**2
        if np.ptp(tail_r2) > 1e-8 or tail_r2.min() <= 0:
            raise ValueError('common positive areal tail constant required')
        self.tail_r2 = float(tail_r2.mean())
        self.native = StaticSlice(x, r, a, b)
        self.well = well
        self.native_extent = float(x[-1])
        extra = np.linspace(x[-1], tail_extent, max(3, int((tail_extent-x[-1])*64)+1))[1:]
        full_x = np.r_[-extra[::-1], x, extra]
        full_a = np.r_[np.ones(len(extra)), a, np.ones(len(extra))]
        full_b = np.r_[np.ones(len(extra)), b, np.ones(len(extra))]
        z = cumulative_simpson(full_b/full_a, x=full_x, initial=0)
        proper = cumulative_simpson(full_b, x=full_x, initial=0)
        z -= np.interp(0, full_x, z)
        proper -= np.interp(0, full_x, proper)
        self.coordinate_of_z = PchipInterpolator(z, full_x)
        self.proper_of_x = PchipInterpolator(full_x, proper)
        self.z_of_x = PchipInterpolator(full_x, z)
        self.z_bounds = (float(z[0]), float(z[-1]))
        self.wall_coordinates = [brentq(lambda t: float(self.metric(t)[0])-well.radius,
                                       -self.native_extent, 0.),
                                 brentq(lambda t: float(self.metric(t)[0])-well.radius,
                                       0., self.native_extent)]
        self.wall_proper = self.proper_of_x(self.wall_coordinates)

    def metric(self, coordinate):
        x = np.asarray(coordinate)
        inside = abs(x) <= self.native_extent
        clipped = np.clip(x, -self.native_extent, self.native_extent)
        r, a, b, rp, rpp, ap, app = self.native.jets(clipped)
        rt = np.sqrt(x*x+self.tail_r2)
        return tuple(np.where(inside, first, second) for first, second in zip(
            (r, a, b, rp, rpp, ap, app),
            (rt, np.ones_like(x), np.ones_like(x), x/rt,
             self.tail_r2/rt**3, np.zeros_like(x), np.zeros_like(x))))

    def optical_fields(self, z, yukawa):
        x = self.coordinate_of_z(z)
        r, a, b, rp, rpp, ap, app = self.metric(x)
        proper = self.proper_of_x(x)
        chi, cp, cpp, potential, force = self.well.values(proper, *self.wall_proper)
        return dict(coordinate=x, proper=proper, radius=r, lapse=a,
                    radial_scale=b, radius_prime=rp, radius_second=rpp,
                    log_lapse_prime=ap, log_lapse_second=app,
                    chi=chi, chi_prime=cp, chi_second=cpp,
                    potential=potential, potential_prime=force,
                    mass=yukawa*chi, mass_prime=yukawa*cp,
                    M=a*yukawa*chi, w=a/r)


@dataclass
class DiracMesh:
    z: np.ndarray
    mass_nodes: np.ndarray
    mass_faces: np.ndarray
    angular_faces: np.ndarray

    def __post_init__(self):
        self.z = np.asarray(self.z, float)
        h = np.diff(self.z)
        if len(h) < 5 or np.any(h <= 0) or np.ptp(h) > 1e-10*h.mean():
            raise ValueError('uniform increasing optical mesh required')
        self.spacing = float(h.mean())
        if (np.shape(self.mass_nodes) != self.z.shape
                or np.shape(self.mass_faces) != h.shape
                or np.shape(self.angular_faces) != h.shape
                or not np.isfinite(np.r_[self.mass_nodes, self.mass_faces, self.angular_faces]).all()
                or min(np.min(self.mass_nodes), np.min(self.mass_faces)) < 0):
            raise ValueError('aligned nonnegative masses and finite angular potential required')

    def schur(self, frequency):
        if frequency <= 0 or not np.isfinite(frequency):
            raise ValueError('positive finite physical frequency required')
        left = 1/self.spacing+self.angular_faces/2
        right = -1/self.spacing+self.angular_faces/2
        inverse = 1/(frequency+self.mass_faces)
        diagonal = self.mass_nodes[1:-1]+left[1:]**2*inverse[1:]+right[:-1]**2*inverse[:-1]
        links = (left*right*inverse)[1:-1]
        return diagonal, links

    def roots(self, cutoff, max_states=256):
        """All positive modes below a specified chemical-potential ceiling."""
        diagonal, links = self.schur(cutoff)
        upper = eigh_tridiagonal(diagonal, links, eigvals_only=True, select='v',
                                 select_range=(-1., cutoff), check_finite=False)
        if len(upper) > max_states:
            raise RuntimeError('registered state-count allowance exceeded')
        found = []
        for index in range(len(upper)):
            def residual(omega):
                d, e = self.schur(omega)
                return float(eigh_tridiagonal(d, e, eigvals_only=True, select='i',
                    select_range=(index, index), check_finite=False)[0]-omega)
            floor = max(1e-7, cutoff*1e-7)
            if residual(floor) <= 0:
                raise RuntimeError('frequency floor failed to bracket an occupied state')
            omega = brentq(residual, floor, cutoff, xtol=1e-11, rtol=1e-10)
            d, e = self.schur(omega)
            eigenvalue, vector = eigh_tridiagonal(d, e, select='i',
                select_range=(index, index), check_finite=False)
            f = np.r_[0., vector[:, 0], 0.]
            g = ((f[:-1]-f[1:])/self.spacing+self.angular_faces*(f[:-1]+f[1:])/2
                 )/(omega+self.mass_faces)
            norm = np.sqrt(self.spacing*(np.sum(f*f)+np.sum(g*g)))
            f, g = f/norm, g/norm
            gn = np.r_[g[0], (g[:-1]+g[1:])/2, g[-1]]
            found.append(dict(frequency=float(omega), f=f, g=gn, g_faces=g,
                              schur_residual=float(abs(eigenvalue[0]-omega))))
        return found


def occupied_tensor(fields, mode, angular_number, eta=1.):
    """One fully occupied 2|K|-state angular multiplet, per Dirac species.

    Yukawa mass belongs to the Dirac tensor once; scalar gradients/potential
    belong to the material tensor. All frequencies refer to the same static
    Killing time. Signed K labels the two spherical parity sectors.
    """
    f, g, omega = mode['f'], mode['g'], mode['frequency']
    s, d, p = f*f+g*g, f*f-g*g, 2*f*g
    a, r, m = fields['lapse'], fields['radius'], fields['mass']
    factor = eta*2*abs(angular_number)/(4*np.pi*a*a*r*r)
    rho = factor*omega*s
    pr = factor*(omega*s-a*m*d-angular_number*a/r*p)
    pt = factor*angular_number*a/(2*r)*p
    scalar_density = factor*a*d
    return np.array([rho, pr, pt]), scalar_density


def angular_tail_bound(fields, cutoff):
    """Sufficient continuum Schur potential bound for both parity signs.

    For |K| above the returned pointwise envelope, the Schur form at cutoff
    is nonnegative. Its frequency monotonicity then excludes lower modes.
    Sampling/refinement of the envelope remains the caller's responsibility.
    """
    a, r, m = fields['lapse'], fields['radius'], fields['mass']
    ap, rp, mp = fields['log_lapse_prime'], fields['radius_prime'], fields['mass_prime']
    M, w = a*m, a/r
    mz = a*a*(ap*m+mp)
    wz = a*w*(ap-rp/r)
    aw = w/(cutoff+M)
    derivative = wz/(cutoff+M)-w*mz/(cutoff+M)**2
    quadratic = w*w/(cutoff+M)
    need = np.maximum(cutoff-M, 0.)
    root = (abs(derivative)+np.sqrt(derivative*derivative+4*quadratic*need))/(2*quadratic)
    return root, derivative, quadratic


def opening(z, radius, tensor):
    """-4pi integral R H dz, equivalent to -4pi integral (R/A) H dl."""
    h = np.asarray(tensor)[0]+np.asarray(tensor)[1]
    return float(-4*np.pi*simpson(radius*h, x=z))
