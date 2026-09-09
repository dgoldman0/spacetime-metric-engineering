"""Coupled proper-distance equations and covariant one-loop counterterms.

The quantum source is an input to the differential equations. Acceptance
requires an independently converged absolute stress and polarization from
one common effective action. A finite Pauli--Villars result is a regulator
control, and is deliberately kept separate from that acceptance decision.
"""
from functools import lru_cache

import numpy as np
from scipy.integrate import cumulative_simpson
from scipy.interpolate import PchipInterpolator, make_interp_spline
from scipy.ndimage import gaussian_filter1d

from .condensate_joint import proper_matter_rhs
from .screened_condensate import field_stress


PV_WEIGHTS = np.array([1., -3., 3., -1.])


def pv_masses(scale):
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError('positive finite regulator scale required')
    return np.arange(4)*scale**2


def curvature(log_radius, log_lapse):
    """Riemann sectional components and Einstein tensor in a proper chart.

    Inputs contain logarithms and their first two proper derivatives.
    Output sections are A''/A, A'R'/(AR), R''/R, (1-R'^2)/R^2.
    """
    r, rp, rpp = np.asarray(log_radius)[:3]
    _, ap, app = np.asarray(log_lapse)[:3]
    x, y, z, w = app+ap*ap, ap*rp, rpp+rp*rp, np.exp(-2*r)-rp*rp
    einstein = np.array([w-2*z, -w+2*y, x+y+z])
    ricci_scalar = -2*x-4*y-4*z+2*w
    ricci_squared = (x+2*y)**2+(x+2*z)**2+2*(w-y-z)**2
    return np.array([x, y, z, w]), einstein, ricci_scalar, ricci_squared


def coupled_rhs(proper, fields, omega, material, v, eta, quantum, polarization,
                portal=1.4):
    """Einstein and material equations at fixed v, G=eta, and species count.

    fields: log R, (log R)', log A, (log A)', u,u_s,h,h_s,a,a_s,N.
    Material derivatives u_s etc. use s=v*l; all other derivatives use l.
    quantum: absolute one-field [rho,pr,pt] in rail length units.
    polarization: absolute <chi^2> in rail length units, same subtraction.
    N is the matter number, whose endpoint difference fixes the charge.
    The radial Einstein equation is an independent constraint.
    """
    y = np.asarray(fields)
    r, rp, a, ap = y[:4]
    radius, lapse = np.exp(r), np.exp(a)
    stress = field_stress(y[4:10], omega, material, 1., lapse)
    source = eta*v**4*np.array([stress[k] for k in
        ('energy', 'radial_pressure', 'tangential_pressure')])+eta*np.asarray(quantum)
    rpp = .5*(np.exp(-2*r)-3*rp*rp-8*np.pi*source[0])
    app = 8*np.pi*source[2]-ap*ap-ap*rp-rpp-rp*rp
    matter = proper_matter_rhs(v*radius, lapse, rp/v, ap/v,
                              y[4:10], omega, material)
    # The complex-Higgs amplitude has kinetic term -(dh)^2. Varying
    # -kappa*v^2*h^2*chi^2/2 therefore adds kappa*h*<chi^2>/(2v^2).
    matter[3] += portal*y[6]*np.asarray(polarization)/(2*v*v)
    number = 4*np.pi*v**3*radius**2*stress['matter_number']
    return np.concatenate((np.array([rp, rpp, ap, app]), v*matter,
                           np.asarray(number)[None]), axis=0)


def radial_constraint(fields, omega, material, v, eta, quantum):
    r, rp, _, ap = np.asarray(fields)[:4]
    stress = field_stress(np.asarray(fields)[4:10], omega, material,
                         1., np.exp(fields[2]))
    return (-np.exp(-2*r)+rp*rp+2*rp*ap)/(8*np.pi)-eta*(
        v**4*stress['radial_pressure']+np.asarray(quantum)[1])


class SmoothJointSeed:
    """Smooth numerical seed over both ends in one proper-distance chart.

    A Gaussian mollifier acts on log R, log A, and all three material
    amplitudes. This changes the seed's demanded stress, which is recomputed.
    The mollification width is a physical seed parameter, separate from
    quadrature and interpolation resolution. No Einstein solution is implied.
    """
    def __init__(self, profile, width=.25, spacing=.025, extent=180.):
        if width < 4*spacing or extent < 100:
            raise ValueError('resolve the smoothing width and both vacuum ends')
        self.profile, self.width, self.spacing = profile, width, spacing
        x = np.unique(np.r_[np.linspace(-extent, profile.cut, 16001),
            np.linspace(profile.cut, 8., 32001), np.linspace(8., extent, 16001)])
        rr, aa, bb = profile.values(x)
        distance = cumulative_simpson(bb, x=x, initial=0.)
        offset = float(PchipInterpolator(x, distance)(0.))
        distance -= offset
        self.coordinate_of_proper = PchipInterpolator(distance, x)
        self.proper_of_coordinate = PchipInterpolator(x, distance)
        l = np.arange(distance[0]+10*width, distance[-1]-10*width, spacing)
        xx = self.coordinate_of_proper(l)
        rr, aa, _ = profile.values(xx)
        t_core = profile.core.fraction_at_coordinate(np.clip(xx, profile.cut,
            profile.setup.positive_extent))
        inner = profile.solution.sol(t_core)[[8, 10, 12]]
        rout = profile.v*(profile.setup.physical_join+(profile.cut-xx)*profile.slope)
        tout = (rout-profile.setup.inner_radius)/(
            profile.setup.exterior_extent-profile.setup.inner_radius)
        outer = profile.solution.sol(np.clip(tout, 0., 1.))[[0, 2, 4]]
        vacuum = np.array([0., 1., 0.])[:, None]
        outer = np.where(tout[None] <= 1., outer, vacuum)
        inner = np.where(xx[None] <= profile.setup.positive_extent, inner, vacuum)
        matter = np.where(xx[None] < profile.cut, outer, inner)
        raw = np.vstack((np.log(rr), np.log(aa), matter))
        smoothed = gaussian_filter1d(raw, width/spacing, axis=1, mode='nearest', truncate=9.)
        self.domain = np.array([l[0]+10*width, l[-1]-10*width])
        self.spline = make_interp_spline(l, smoothed, k=5, axis=1)

    def jets(self, proper, order=4):
        return np.array([self.spline(proper, nu=n) for n in range(order+1)])

    def values(self, proper):
        y = self.spline(proper)
        return np.exp(y[0]), np.exp(y[1]), 1.4*self.profile.v**2*y[3]**2

    def state(self, proper):
        y, dy = self.jets(proper, 1)
        return np.array([y[0], dy[0], y[1], dy[1], y[2], dy[2]/self.profile.v,
            y[3], dy[3]/self.profile.v, y[4], dy[4]/self.profile.v,
            np.zeros_like(y[0])])

    def demanded_tensor(self, proper):
        jets = self.jets(proper, 2)
        return curvature(jets[:, 0], jets[:, 1])[1]/(8*np.pi)


def heavy_coefficients(scale, reference_mass_squared):
    """Coefficients of the regulator fields' a0,a1,a2 local action.

    W_heavy = integral sqrt(g) [F(V)+J(V)R+k1 R^2+k2 Ricci^2].
    Euler density and total derivatives have zero compact bulk variation.
    """
    m = pv_masses(scale)[1:]
    c = PV_WEIGHTS[1:]
    log = np.log(m/reference_mass_squared)
    c4 = np.sum(c*m*m*(log-1.5))
    c2 = np.sum(c*m*(log-1.))
    c0 = np.sum(c*log)
    return np.array([c4, 2*c2, c0, -c2/3, -c0/3, c0/60, c0/30])/(64*np.pi**2)


def vacuum_finite_coefficients(reference_mass_squared):
    """Keep the flat h=1 vacuum, Higgs mass, and measured G.

    mu^2=kappa*v^2. The added F=mu^2 V/(32pi^2)-mu^4/(128pi^2)
    sets the potential and its first two V derivatives at V=mu^2 to zero.
    The added J=-mu^2/(192pi^2) fixes the vacuum Newton coefficient.
    Finite R^2, Ricci^2 and V*R couplings are zero at this scale.
    """
    m = reference_mass_squared
    return np.array([-m*m/2, 2*m, 0., -m/3, 0., 0., 0.])/(64*np.pi**2)


@lru_cache(maxsize=1)
def local_variation_function():
    """Symbolic Euler derivatives, retaining radial lapse until variation.

    SymPy is used only to derive executable algebra, never narrative reports.
    This avoids gauge fixing the radial Einstein constraint out of the action.
    """
    import sympy as sp
    jets = [sp.symbols(f'{name}0:5') for name in ('a', 'b', 'r', 'v')]
    a, b, r, v = jets
    f0, f1, f2, j0, j1, k1, k2 = coeff = sp.symbols('f0 f1 f2 j0 j1 k1 k2')
    x = sp.exp(-2*b[0])*(a[2]+a[1]**2-a[1]*b[1])
    y = sp.exp(-2*b[0])*a[1]*r[1]
    z = sp.exp(-2*b[0])*(r[2]+r[1]**2-r[1]*b[1])
    w = sp.exp(-2*r[0])-sp.exp(-2*b[0])*r[1]**2
    scalar = -2*x-4*y-4*z+2*w
    ricci2 = (x+2*y)**2+(x+2*z)**2+2*(w-y-z)**2
    volume = sp.exp(a[0]+b[0]+2*r[0])
    density = volume*(f0+f1*v[0]+f2*v[0]**2+(j0+j1*v[0])*scalar+
                      k1*scalar**2+k2*ricci2)

    def derivative(expr):
        return sp.expand(sum(sp.diff(expr, row[i])*row[i+1]
            for row in jets for i in range(4)))

    gauge = {term: 0 for term in b}
    result = []
    for row, factor in ((a, 1), (b, -1), (r, sp.Rational(-1, 2))):
        euler = sp.diff(density, row[0])-derivative(sp.diff(density, row[1]))
        euler += derivative(derivative(sp.diff(density, row[2])))
        result.append(sp.simplify((factor*euler/volume).subs(gauge)))
    result.append(2*(f1+2*f2*v[0]+j1*scalar.subs(gauge)))
    return sp.lambdify([*a, *r, *v, *coeff], result, 'numpy', cse=True)


def local_action_source(log_radius, log_lapse, mass_squared, coefficients):
    """Return rho,pr,pt,<chi^2> from one local effective action."""
    fn = local_variation_function()
    a, r, v = np.broadcast_arrays(log_lapse, log_radius, mass_squared)
    raw = fn(*a, *r, *v, *coefficients)
    return np.array(np.broadcast_arrays(*raw))


def flat_pv_source(potential, scale, reference_mass_squared):
    """Exact continuum PV tensor/polarization in homogeneous flat space."""
    m2 = np.asarray(potential)+pv_masses(scale)
    if np.any(m2 < 0):
        raise ValueError('nonnegative total masses required')
    log = np.log(np.maximum(m2, 1e-300)/reference_mass_squared)
    energy = np.sum(PV_WEIGHTS*m2*m2*(log-1.5))/(64*np.pi**2)
    polarization = np.sum(PV_WEIGHTS*m2*(log-1))/(16*np.pi**2)
    return np.array([energy, -energy, -energy, polarization])


def flat_renormalized_source(potential, reference_mass_squared):
    """Exact homogeneous one-loop source with the registered vacuum conditions."""
    v, m = np.asarray(potential), reference_mass_squared
    if np.any(v < 0) or m <= 0:
        raise ValueError('nonnegative potential and positive reference mass required')
    log = np.log(np.maximum(v, 1e-300)/m)
    energy = (v*v*(log-1.5)+2*m*v-.5*m*m)/(64*np.pi**2)
    polarization = (v*(log-1)+m)/(16*np.pi**2)
    return np.array([energy, -energy, -energy, polarization])
