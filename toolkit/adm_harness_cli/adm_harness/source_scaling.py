"""Source scaling test: how candidate source families supply the axial rail's transit demand.

The demanded tensor of the axial track falls as 1/L^2 with the rail's unit
length L, while its shape is fixed. A source family's supply follows its own
law, so the comparison reduces to a few dimensionless functionals of the
demand, computed here from the same field jets the gate uses:

- the Riemann tensor of the axial metric in coordinates (sigma, z, r, phi),
  from the second-order jets of alpha, A, beta and C;
- the orthonormal frame of the static source units at fixed (z, r, phi), the
  null-energy deficit they see, their acceleration and the local curvature
  radius. These set the sampling time a flat-space quantum inequality admits,
  and with it the number of free fields a given scale requires;
- null geodesics of the axial metric, the null energy along them, and the
  zero-energy solution of -d^2/dlambda^2 + 8 pi T(k, k). A curvature
  coupling F(phi) R with NEC-respecting matter needs F'' <= 8 pi T(k, k) F
  along every affinely parametrized null geodesic, so a bound state of that
  operator forces F to vanish on the ray;
- the Casimir cavity whose null-energy deficit matches the demand, and the
  energy of the thinnest electron plasma mirror that bounds it.

All tensors use G = c = 1 and rail length units.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from . import axial_track as ax

PLANCK_LENGTH = 1.616255e-35  # m
HBAR = 1.054571817e-34  # J s
LIGHT_SPEED = 2.99792458e8  # m/s
NEWTON = 6.67430e-11  # m^3 kg^-1 s^-2
ELECTRON_COMPTON = 3.8615926796e-13  # reduced Compton wavelength, m
FINE_STRUCTURE = 7.2973525693e-3
STRESS_UNIT = LIGHT_SPEED**4/NEWTON  # Pa m^2: geometric stress 1/L^2 at L = 1 m
QI_GAUSSIAN = 64*math.pi**2  # Fewster-Roman massless-scalar null QI, Gaussian g^2 of standard deviation tau
_DERIVS = ("s", "z", "r")


def _jet(fields, name):
    """Value, gradient over (sigma, z, r) and Hessian of one field from a radial_fields dict."""
    value = np.asarray(fields[name], dtype=float)
    n = value.shape[0]
    grad = np.zeros((n, 3))
    hess = np.zeros((n, 3, 3))
    if name == "C":
        grad[:, 2] = fields["C_r"]
        hess[:, 2, 2] = fields["C_rr"]
        return value, grad, hess
    for i, a in enumerate(_DERIVS):
        grad[:, i] = fields[f"{name}_{a}"]
        for j, b in enumerate(_DERIVS):
            key = "".join(sorted((a, b), key=_DERIVS.index))
            hess[:, i, j] = fields[f"{name}_{key}"]
    return value, grad, hess


def _product(f, g):
    fv, fg, fh = f
    gv, gg, gh = g
    return (fv*gv, fg*gv[:, None]+fv[:, None]*gg,
            fh*gv[:, None, None]+np.einsum("ni,nj->nij", fg, gg)+np.einsum("ni,nj->nij", gg, fg)
            + fv[:, None, None]*gh)


def _combine(*terms):
    return tuple(sum(term[k]*sign for sign, term in terms) for k in range(3))


def metric_jets(fields):
    """Covariant metric, its first and second coordinate derivatives, over the arrays in fields.

    Returns g (n, 4, 4), dg (n, 4, 4, 4) with dg[:, c] = d_c g and ddg
    (n, 4, 4, 4, 4) with ddg[:, c, d] = d_c d_d g, in coordinates
    (sigma, z, r, phi); phi derivatives vanish.
    """
    alpha, stretch, beta, circle = (_jet(fields, name) for name in ("alpha", "A", "beta", "C"))
    a2 = _product(alpha, alpha)
    s2 = _product(stretch, stretch)
    s2b = _product(s2, beta)
    s2b2 = _product(s2b, beta)
    g00 = _combine((-1., a2), (1., s2b2))
    c2 = _product(circle, circle)
    n = alpha[0].shape[0]
    g = np.zeros((n, 4, 4))
    dg = np.zeros((n, 4, 4, 4))
    ddg = np.zeros((n, 4, 4, 4, 4))
    for (a, b), component in {(0, 0): g00, (0, 1): s2b, (1, 1): s2, (3, 3): c2}.items():
        value, grad, hess = component
        for x, y in {(a, b), (b, a)}:
            g[:, x, y] = value
            dg[:, :3, x, y] = grad
            ddg[:, :3, :3, x, y] = hess
    g[:, 2, 2] = 1.
    return g, dg, ddg


def christoffel(g, dg):
    """Gamma^i_jk (n, 4, 4, 4) from the metric and its first derivatives."""
    inverse = np.linalg.inv(g)
    first_kind = .5*(np.einsum("njmk->nmjk", dg)+np.einsum("nkmj->nmjk", dg)-dg)
    return np.einsum("nim,nmjk->nijk", inverse, first_kind)


def riemann(g, dg, ddg):
    """Covariant Riemann tensor R_ijkl (n, 4, 4, 4, 4), with R^i_jkl = d_k Gamma^i_lj - d_l Gamma^i_kj + ..."""
    inverse = np.linalg.inv(g)
    first_kind = .5*(np.einsum("njmk->nmjk", dg)+np.einsum("nkmj->nmjk", dg)-dg)
    gamma = np.einsum("nim,nmjk->nijk", inverse, first_kind)
    d_first = .5*(np.einsum("nljmk->nlmjk", ddg)+np.einsum("nlkmj->nlmjk", ddg)-ddg)
    d_inverse = -np.einsum("nia,nlab,nbm->nlim", inverse, dg, inverse)
    d_gamma = np.einsum("nlim,nmjk->nlijk", d_inverse, first_kind)+np.einsum("nim,nlmjk->nlijk", inverse, d_first)
    mixed = (np.einsum("nkilj->nijkl", d_gamma)-np.einsum("nlikj->nijkl", d_gamma)
             + np.einsum("nikp,nplj->nijkl", gamma, gamma)-np.einsum("nilp,npkj->nijkl", gamma, gamma))
    return np.einsum("nai,nijkl->najkl", g, mixed)


def einstein_from_riemann(g, curvature):
    """G_jl from a covariant Riemann tensor, for checks against the generated kernel."""
    inverse = np.linalg.inv(g)
    ricci = np.einsum("nik,nijkl->njl", inverse, curvature)
    scalar = np.einsum("njl,njl->n", inverse, ricci)
    return ricci-.5*g*scalar[:, None, None]


def static_velocity(fields):
    """Speed of the static frame relative to the normal observers, A beta / alpha, along e_z."""
    return np.asarray(fields["A"])*np.asarray(fields["beta"])/np.asarray(fields["alpha"])


def normal_tetrad(fields):
    """Rows n, e_z, e_r, e_phi of the normal frame in coordinates (sigma, z, r, phi)."""
    alpha, stretch, beta, circle = (np.asarray(fields[k], dtype=float) for k in ("alpha", "A", "beta", "C"))
    e = np.zeros((len(alpha), 4, 4))
    e[:, 0, 0], e[:, 0, 1] = 1/alpha, -beta/alpha
    e[:, 1, 1] = 1/stretch
    e[:, 2, 2] = 1.
    e[:, 3, 3] = 1/circle
    return e


def static_boost(fields):
    """Lorentz matrix taking normal-frame components to the static frame u = gamma (n + v e_z)."""
    v = static_velocity(fields)
    if np.any(np.abs(v) >= 1):
        raise ValueError("the static frame is not timelike at every point")
    gamma = 1/np.sqrt(1-v*v)
    boost = np.zeros((len(v), 4, 4))
    boost[:, 0, 0] = boost[:, 1, 1] = gamma
    boost[:, 0, 1] = boost[:, 1, 0] = gamma*v
    boost[:, 2, 2] = boost[:, 3, 3] = 1.
    return boost


def static_tetrad(fields):
    """Rows u, e_z', e_r, e_phi of the static frame in coordinates; u is along d_sigma."""
    return np.einsum("nab,nbm->nam", static_boost(fields), normal_tetrad(fields))


def to_static_frame(tensor, fields):
    """Static-frame components of normal-frame orthonormal tensors (n, 4, 4)."""
    boost = static_boost(fields)
    return np.einsum("nab,nbc,ndc->nad", boost, tensor, boost)


def frame_riemann(curvature, tetrad):
    out = np.einsum("nDd,nabcd->nabcD", tetrad, curvature)
    out = np.einsum("nCc,nabcD->nabCD", tetrad, out)
    out = np.einsum("nBb,nabCD->naBCD", tetrad, out)
    return np.einsum("nAa,naBCD->nABCD", tetrad, out)


def static_acceleration(g, dg):
    """Magnitude of the 4-acceleration of observers at fixed (z, r, phi)."""
    gamma = christoffel(g, dg)
    lapse2 = -g[:, 0, 0]
    if np.any(lapse2 <= 0):
        raise ValueError("static observers are not timelike at every point")
    accel = gamma[:, :, 0, 0]/lapse2[:, None]
    accel[:, 0] += dg[:, 0, 0, 0]/(2*lapse2*lapse2)
    return np.sqrt(np.maximum(np.einsum("na,nab,nb->n", accel, g, accel), 0.))


@dataclass(frozen=True)
class StaticDemand:
    """Static-frame demand at a set of points: null deficit, curvature radius, acceleration, local scale.

    static_lapse is d(proper time)/d(sigma) of the static observers.
    """
    null_energy: np.ndarray
    curvature_radius: np.ndarray
    acceleration: np.ndarray
    scale: np.ndarray
    static_speed: np.ndarray
    static_lapse: np.ndarray
    tensor: np.ndarray


def static_demand(jet, radius, design, z, s):
    """Static-frame null energy and local scale of the demand at radii for one (sigma, z) jet.

    The service region is an exact product with the flat transverse plane, so
    a radius at the axis is evaluated at half the service-region radius, where
    the polar coordinates are regular and every field takes its axis value.
    """
    radius = np.atleast_1d(np.asarray(radius, dtype=float))
    radius = np.where(radius <= 0, .5*design.core_radius, radius)
    fields = ax.radial_fields(jet, radius, design, z=z, s=s)
    tensor = ax.frame_tensor(jet, radius, design, z=z, s=s)
    static = to_static_frame(tensor, fields)
    null = ax.min_null_energy(static)
    g, dg, ddg = metric_jets(fields)
    components = frame_riemann(riemann(g, dg, ddg), static_tetrad(fields))
    largest = np.max(np.abs(components.reshape(len(radius), -1)), axis=1)
    curvature_radius = np.where(largest > 0, 1/np.sqrt(np.where(largest > 0, largest, 1.)), np.inf)
    accel = static_acceleration(g, dg)
    inverse_accel = np.where(accel > 0, 1/np.where(accel > 0, accel, 1.), np.inf)
    return StaticDemand(null, curvature_radius, accel, np.minimum(curvature_radius, inverse_accel),
                        static_velocity(fields), np.sqrt(-g[:, 0, 0]), static)


def qi_requirement(null_energy, scale, fraction=1.):
    """Free massless scalars needed per (L / l_P)^2 to supply a steady null deficit.

    A Gaussian g^2 of standard deviation tau = fraction * scale samples the
    static-frame deficit d = max(0, -T(k, k)) with u.k = -1; the Fewster-Roman
    bound -1/(64 pi^2 tau^4) per field then requires N >= 64 pi^2 d tau^4
    (L / l_P)^2.
    """
    deficit = np.maximum(-np.asarray(null_energy, dtype=float), 0.)
    return QI_GAUSSIAN*deficit*(fraction*np.asarray(scale, dtype=float))**4


def sampled_requirement(proper_time, null_energy, centre, tau):
    """The same requirement from the explicit Gaussian average of a sampled deficit history."""
    t = np.asarray(proper_time, dtype=float)
    weight = np.exp(-(t-centre)**2/(2*tau*tau))/math.sqrt(2*math.pi*tau*tau)
    average = np.trapezoid(np.asarray(null_energy, dtype=float)*weight, t)
    return QI_GAUSSIAN*max(-average, 0.)*tau**4


def gaussian_qi_constant(tau, samples=20001):
    """(1/12 pi^2) int g''^2 for the Gaussian window, checked against 1/(64 pi^2 tau^4)."""
    t = np.linspace(-12*tau, 12*tau, samples)
    g = (2*math.pi*tau*tau)**-.25*np.exp(-t*t/(4*tau*tau))
    second = g*(t*t/(4*tau**4)-1/(2*tau*tau))
    return np.trapezoid(second*second, t)/(12*math.pi**2)


def fields_required(requirement, unit_length_m):
    """Number of free fields for a rail of unit length L, given the requirement per (L / l_P)^2."""
    return requirement*(unit_length_m/PLANCK_LENGTH)**2


def casimir_gap(null_deficit, unit_length_m):
    """Ideal-mirror cavity gap whose null-energy deficit pi^2 hbar c / (180 a^4) matches the demand, in m."""
    demand = null_deficit*STRESS_UNIT/unit_length_m**2
    return (math.pi**2*HBAR*LIGHT_SPEED/(180*demand))**.25


def mirror_overhead(gap_m, plasma_factor=1.):
    """Energy of the thinnest electron plasma mirror over the cavity's null-energy deficit, per unit area.

    The mirror reflects the cavity modes when its plasma frequency is at least
    plasma_factor * 2 pi c / a, and it is at least one skin depth thick. While
    its degenerate electrons stay non-relativistic, a >= 2 pi k lambda_C /
    sqrt(4 alpha / 3 pi) (about 113 k lambda_C), their rest energy alone
    exceeds the deficit by 90 k / (pi^2 alpha) (a / lambda_C)^2. At smaller
    gaps the electrons are ultra-relativistic; with omega_p^2 = (4 alpha / 3 pi)
    c^2 k_F^2 and energy density hbar c k_F^4 / (4 pi^2), one skin depth
    carries a gap-independent multiple of the deficit. Ions or positrons only
    add to either value.
    """
    crossover = 2*math.pi*plasma_factor*ELECTRON_COMPTON/math.sqrt(4*FINE_STRUCTURE/(3*math.pi))
    if gap_m >= crossover:
        return 90*plasma_factor/(math.pi**2*FINE_STRUCTURE)*(gap_m/ELECTRON_COMPTON)**2
    return relativistic_mirror_overhead(plasma_factor)


def relativistic_mirror_overhead(plasma_factor=1.):
    """Energy of one skin depth of degenerate ultra-relativistic electrons over the cavity deficit, per area."""
    ratio = math.sqrt(4*FINE_STRUCTURE/(3*math.pi))
    fermi = 2*math.pi*plasma_factor/ratio  # k_F a
    per_area = fermi**3/(4*math.pi**2*ratio)  # (energy density) * (skin depth), in hbar c / a^3
    return per_area/(math.pi**2/180)


class AxialSpacetime:
    """Point evaluation of the axial metric's fields, Christoffel symbols and demanded tensor."""

    def __init__(self, design, params):
        self.design, self.params = design, params

    def fields(self, s, z, r):
        jet = ax.service_jet(float(s), float(z), self.params, self.design)
        return jet, ax.radial_fields(jet, [abs(float(r))], self.design, z=float(z), s=float(s))

    def christoffel(self, x):
        _, fields = self.fields(x[0], x[1], x[2])
        g, dg, _ = metric_jets(fields)
        return christoffel(g, dg)[0], g[0]

    def null_energy(self, x, k):
        """T_ab k^a k^b for coordinate k, from the generated orthonormal tensor, and the static energy -u.k."""
        jet, fields = self.fields(x[0], x[1], x[2])
        tensor = ax.frame_tensor(jet, [abs(float(x[2]))], self.design, z=float(x[1]), s=float(x[0]))[0]
        frame_k = np.linalg.solve(normal_tetrad(fields)[0].T, np.asarray(k, dtype=float))
        energy = static_boost(fields)[0, 0]@(frame_k*np.array([1., -1., -1., -1.]))
        return float(frame_k@tensor@frame_k), float(energy)


def null_direction(tensor, samples=4000):
    """Unit direction e in a frame's spatial triad minimizing T(u + e, u + e), and that minimum.

    A Fibonacci sphere locates the minimum and a local search on the two
    angles refines it; the refined value matches min_null_energy.
    """
    from scipy.optimize import minimize

    tensor = np.asarray(tensor, dtype=float)

    def value(e):
        return tensor[0, 0]+2*tensor[0, 1:]@e+e@tensor[1:, 1:]@e

    index = np.arange(samples)+.5
    polar = np.arccos(1-2*index/samples)
    azimuth = math.pi*(1+math.sqrt(5))*index
    sphere = np.stack([np.cos(polar), np.sin(polar)*np.cos(azimuth), np.sin(polar)*np.sin(azimuth)], axis=1)
    values = tensor[0, 0]+2*sphere@tensor[0, 1:]+np.einsum("ni,ij,nj->n", sphere, tensor[1:, 1:], sphere)
    start = sphere[np.argmin(values)]

    def unit(angles):
        a, b = angles
        return np.array([math.cos(a), math.sin(a)*math.cos(b), math.sin(a)*math.sin(b)])

    angles = np.array([math.acos(np.clip(start[0], -1, 1)), math.atan2(start[2], start[1])])
    best = minimize(lambda x: value(unit(x)), angles, method="Nelder-Mead",
                    options={"xatol": 1e-10, "fatol": 1e-14, "maxiter": 4000})
    e = unit(best.x)
    return e, float(value(e))


def launch_vector(fields, direction):
    """Coordinate null vector u + e for a unit spatial direction e in the static frame (z', r, phi)."""
    e = np.asarray(direction, dtype=float)
    e = e/np.linalg.norm(e)
    tetrad = static_tetrad(fields)[0]
    return tetrad[0]+e[0]*tetrad[1]+e[1]*tetrad[2]+e[2]*tetrad[3]


def trace_null_geodesic(spacetime, x0, k0, *, step=.01, bounds=((-8., 8.), (-11., 11.), 14.), max_steps=40000):
    """Classical RK4 integration of a null geodesic in both directions from (x0, k0).

    The parameter is the Euclidean coordinate arc length mu, with
    dx/dmu = k/|k| and dk/dmu = -Gamma(k, k)/|k|; the affine parameter lambda
    follows from dlambda/dmu = 1/|k|. A ray reaching the axis continues on the
    opposite side, which in these coordinates flips k^r. Integration stops
    outside the sigma, z or r bounds. Returns arrays lam, x, k ordered by lambda.
    """
    (s_lo, s_hi), (z_lo, z_hi), r_max = bounds

    def euclid(x, k):
        return math.sqrt(k[0]**2+k[1]**2+k[2]**2+(x[2]*k[3])**2)

    def rhs(y):
        x, k = y[:4], y[4:8]
        gamma, _ = spacetime.christoffel(x)
        norm = euclid(x, k)
        return np.concatenate([k/norm, -np.einsum("ijk,j,k->i", gamma, k, k)/norm, [1/norm]])

    def run(sign):
        y = np.concatenate([np.asarray(x0, dtype=float), np.asarray(k0, dtype=float), [0.]])
        path = [y.copy()]
        h = sign*step
        for _ in range(max_steps):
            a = rhs(y)
            b = rhs(y+.5*h*a)
            c = rhs(y+.5*h*b)
            d = rhs(y+h*c)
            y = y+h*(a+2*b+2*c+d)/6
            if y[2] < 0:
                y[2], y[6] = -y[2], -y[6]
                y[3] += math.pi
            path.append(y.copy())
            if not (s_lo <= y[0] <= s_hi and z_lo <= y[1] <= z_hi and y[2] <= r_max):
                break
        return np.array(path)

    forward, backward = run(1.), run(-1.)
    path = np.concatenate([backward[::-1], forward[1:]])
    return path[:, 8], path[:, :4], path[:, 4:8]


def null_potential(spacetime, xs, ks):
    """8 pi T(k, k) along a traced ray, with the static-frame energy -u.k at each point."""
    potential, energy = np.empty(len(xs)), np.empty(len(xs))
    for i, (x, k) in enumerate(zip(xs, ks)):
        value, energy[i] = spacetime.null_energy(x, k)
        potential[i] = ax.EIGHT_PI*value
    return potential, energy


def zero_energy_solution(lam, potential, substeps=16):
    """psi'' = V psi along the ray from psi = 1, psi' = 0 at the first sample, V linear between samples.

    For V with compact support, the number of negative eigenvalues of
    -d^2/dlambda^2 + V on the whole line equals the zeros of this solution,
    counting the zero its linear continuation reaches beyond the last sample
    when psi and psi' there have opposite signs. Any F > 0 with F'' <= V F
    that is constant at the incoming end satisfies F <= F_inf psi up to the
    first zero, so F must vanish there or earlier. Returns psi and psi' at the
    samples.
    """
    lam = np.asarray(lam, dtype=float)
    potential = np.asarray(potential, dtype=float)
    psi, slope = np.empty(len(lam)), np.empty(len(lam))
    y = np.array([1., 0.])
    psi[0], slope[0] = y
    for i in range(len(lam)-1):
        a, b = lam[i], lam[i+1]
        h = (b-a)/substeps
        va, vb = potential[i], potential[i+1]

        def f(x, y):
            v = va+(vb-va)*(x-a)/(b-a) if b > a else va
            return np.array([y[1], v*y[0]])

        x = a
        for _ in range(substeps):
            k1 = f(x, y)
            k2 = f(x+h/2, y+h/2*k1)
            k3 = f(x+h/2, y+h/2*k2)
            k4 = f(x+h, y+h*k3)
            y = y+h*(k1+2*k2+2*k3+k4)/6
            x += h
        psi[i+1], slope[i+1] = y
    return psi, slope


def bound_state_count(psi, slope):
    """Zeros of the zero-energy solution, including the one its linear continuation reaches."""
    zeros = int(np.sum(np.sign(psi[1:]) != np.sign(psi[:-1])))
    return zeros+int(psi[-1]*slope[-1] < 0)
