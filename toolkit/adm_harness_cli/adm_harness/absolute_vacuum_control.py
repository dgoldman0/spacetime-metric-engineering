"""Bounded Pauli--Villars mode controls for an absolute scalar source.

The continuum regulator limit and all mode/mesh limits require independent
verification. Returned finite-cutoff values are diagnostic estimates.
"""
from dataclasses import dataclass

import numpy as np
from scipy.linalg.lapack import dpttrf
from scipy.special import ive, kve

from .semiclassical_joint import PV_WEIGHTS, pv_masses


def flat_mode(frequency, harmonic, scale, radius=2., potential=1.):
    """Exact continuum regular-origin/decaying-infinity Bessel mode control."""
    omega = np.asarray(frequency)[..., None]
    masses = pv_masses(scale)
    k = np.sqrt(omega*omega+potential+masses)
    z, nu = k*radius, harmonic+.5
    iv, kv = ive(nu, z), kve(nu, z)
    good = (iv > 0) & np.isfinite(kv)
    with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
        product = iv*kv
        zi = z*ive(nu-1, z)/iv-nu
        zk = -z*kve(nu-1, z)/kv-nu
    if not np.all(good):
        zz = np.asarray(z[~good], np.longdouble)
        if nu < 20 or np.any(zz > .4*nu):
            raise FloatingPointError('Bessel fallback requires large order/small argument')
        sums, derivatives = [], []
        for order in (nu, -nu):
            term = np.ones_like(zz)
            total, deriv = term.copy(), np.zeros_like(term)
            for n in range(1, min(80, int(nu/2))):
                term *= zz*zz/(4*n*(n+order))
                total += term
                deriv += 2*n*term
            sums.append(total)
            derivatives.append(deriv/total)
        product[~good] = sums[0]*sums[1]/(2*nu)
        zi[~good], zk[~good] = nu+derivatives[0], -nu+derivatives[1]
    green = product/radius
    pl, qr = (zi-.5)/radius, (zk-.5)/radius
    mixed = pl*qr*green
    time = -omega*omega*green
    angular = harmonic*(harmonic+1)*green/(2*radius**2)
    mass = (potential+masses)*green
    values = np.stack([.5*(time+mixed+2*angular+mass),
        .5*(time+mixed-2*angular-mass), .5*(time-mixed-mass), green], axis=-1)
    return np.sum(np.asarray(values, np.longdouble)*PV_WEIGHTS[:, None], axis=-2)


def probe_mesh(probe, domain, spacing, core_radius=3., far_spacing=.04):
    """Fine equal cells near the witness, gently graded cells toward both ends."""
    if spacing <= 0 or spacing > far_spacing or not domain[0] < probe < domain[1]:
        raise ValueError('ordered domain and resolved positive spacing required')
    sides = []
    for sign, end in ((-1, domain[0]), (1, domain[1])):
        distance, step, points = 0., spacing, [probe]
        while distance < abs(end-probe):
            step = min(far_spacing, step*(1.02 if distance > core_radius else 1.))
            distance = min(distance+step, abs(end-probe))
            points.append(probe+sign*distance)
        sides.append(np.array(points))
    return np.r_[sides[0][:0:-1], sides[1]]


@dataclass
class AbsoluteRadialControl:
    coordinate: np.ndarray
    radius: np.ndarray
    lapse: np.ndarray
    potential: np.ndarray
    geometric_potential: np.ndarray
    probe: int
    log_amplitude_gradient: float

    @classmethod
    def from_seed(cls, seed, proper, spacing=.01, far_spacing=.04):
        x = probe_mesh(proper, seed.domain, spacing, far_spacing=far_spacing)
        jets = seed.jets(x, 2)
        r, a, v = seed.values(x)
        rp, rpp, ap, app = jets[1, 0], jets[2, 0], jets[1, 1], jets[2, 1]
        c = rpp+rp*rp+app/2+ap*ap/4+ap*rp
        i = int(np.argmin(abs(x-proper)))
        return cls(x, r, a, v, c, i, rp[i]+ap[i]/2)

    @classmethod
    def flat(cls, radius=2., potential=1., spacing=.01, extent=40., far_spacing=.04):
        x = probe_mesh(radius, (0., extent), spacing, core_radius=min(radius/2, 3.),
                       far_spacing=far_spacing)
        i = int(np.argmin(abs(x-radius)))
        return cls(x, x, np.ones_like(x), np.full_like(x, potential),
                   np.zeros_like(x), i, 1/radius)

    def mode(self, frequency, harmonic, scale, correct_local=True):
        x, i = self.coordinate, self.probe
        h = np.diff(x)
        volume = (h[:-1]+h[1:])/2
        links = 1/h
        q0 = frequency**2/self.lapse[1:-1]**2+harmonic*(harmonic+1)/self.radius[1:-1]**2
        q0 += self.potential[1:-1]+self.geometric_potential[1:-1]
        s = self.log_amplitude_gradient
        channels = []
        for mass in pv_masses(scale):
            q = q0+mass
            diagonal = links[:-1]+links[1:]+volume*q
            dl, _, il = dpttrf(diagonal.copy(), -links[1:-1].copy())
            dr, _, ir = dpttrf(diagonal[::-1].copy(), -links[1:-1][::-1].copy())
            if il or ir:
                raise ValueError('nonpositive Euclidean mode operator')
            ii = i-1
            right = dr[::-1][ii]
            green = 1/(dl[ii]+right-diagonal[ii])
            zl = dl[ii]-links[i]-h[i]*q[ii]/2
            zr = -(right-links[i-1]-h[i-1]*q[ii]/2)
            mixed = (zl-s)*(zr-s)*green
            if correct_local and q[ii] > 0:
                if abs(h[i]/h[i-1]-1) > 1e-7:
                    raise ValueError('local lattice correction needs equal probe cells')
                k = np.sqrt(q[ii])
                # Exact constant-potential dispersion correction. Its remaining
                # gradient error is measured by independent mesh refinement.
                shift = np.sqrt(1+(h[i]*k/2)**2)
                dg = (1-1/shift)/(2*k)
                db = k*(shift-1)/2
                green += dg
                mixed += db+s*s*dg
            norm = self.lapse[i]*self.radius[i]**2
            green, mixed = green/norm, mixed/norm
            time = -frequency**2/self.lapse[i]**2*green
            angular = harmonic*(harmonic+1)/(2*self.radius[i]**2)*green
            mass_term = (self.potential[i]+mass)*green
            channels.append([.5*(time+mixed+2*angular+mass_term),
                .5*(time+mixed-2*angular-mass_term),
                .5*(time-mixed-mass_term), green])
        return np.sum(np.asarray(channels, np.longdouble)*PV_WEIGHTS[:, None], axis=0)
