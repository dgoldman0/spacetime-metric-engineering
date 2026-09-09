"""Shared radial solves for the joint source's integrated Einstein balance."""
from dataclasses import dataclass

import numpy as np
from scipy.linalg.lapack import dpttrf

from .absolute_vacuum_control import flat_mode
from .semiclassical_joint import PV_WEIGHTS, pv_masses


@dataclass
class ProfileRadialControl:
    coordinate: np.ndarray
    radius: np.ndarray
    lapse: np.ndarray
    potential: np.ndarray
    geometric_potential: np.ndarray
    probes: np.ndarray
    amplitude_gradient: np.ndarray

    @classmethod
    def from_seed(cls, seed, witnesses, spacing=.005, end_coordinate=25.):
        ends = seed.proper_of_coordinate(np.array([-end_coordinate, end_coordinate]))
        x = np.linspace(ends[0], ends[1], int(np.ceil(np.diff(ends)[0]/spacing))+1)
        jets = seed.jets(x, 2)
        r, a, v = seed.values(x)
        rp, rpp, ap, app = jets[1, 0], jets[2, 0], jets[1, 1], jets[2, 1]
        c = rpp+rp*rp+app/2+ap*ap/4+ap*rp
        targets = seed.proper_of_coordinate(np.asarray(witnesses))
        probes = np.unique(np.round((targets-x[0])/(x[1]-x[0])).astype(int))
        if np.any((probes <= 0) | (probes >= len(x)-1)):
            raise ValueError('observations must lie inside the radial domain')
        return cls(x, r, a, v, c, probes, (rp+ap/2)[probes])

    def mode(self, frequency, harmonic, scale):
        h = self.coordinate[1]-self.coordinate[0]
        q0 = frequency**2/self.lapse[1:-1]**2+harmonic*(harmonic+1)/self.radius[1:-1]**2
        q0 += self.potential[1:-1]+self.geometric_potential[1:-1]
        s, ii = self.amplitude_gradient, self.probes-1
        channels = []
        for mass in pv_masses(scale):
            q = q0+mass
            diagonal = 2/h+h*q
            links = np.full(len(diagonal)-1, -1/h)
            dl, _, il = dpttrf(diagonal.copy(), links.copy())
            dr, _, ir = dpttrf(diagonal[::-1].copy(), links)
            if il or ir:
                raise ValueError('nonpositive Euclidean mode operator')
            right = dr[::-1][ii]
            green = 1/(dl[ii]+right-diagonal[ii])
            zl = dl[ii]-1/h-h*q[ii]/2
            zr = -(right-1/h-h*q[ii]/2)
            mixed = (zl-s)*(zr-s)*green
            k = np.sqrt(np.maximum(q[ii], 1e-100))
            shift = np.sqrt(1+(h*k/2)**2)
            dg = (1-1/shift)/(2*k)
            green += dg
            mixed += k*(shift-1)/2+s*s*dg
            norm = self.lapse[self.probes]*self.radius[self.probes]**2
            green, mixed = green/norm, mixed/norm
            time = -frequency**2/self.lapse[self.probes]**2*green
            angular = harmonic*(harmonic+1)/(2*self.radius[self.probes]**2)*green
            mass_term = (self.potential[self.probes]+mass)*green
            channels.append(np.stack([.5*(time+mixed+2*angular+mass_term),
                .5*(time+mixed-2*angular-mass_term),
                .5*(time-mixed-mass_term), green], axis=-1))
        return np.sum(np.asarray(channels, np.longdouble)*PV_WEIGHTS[:, None, None], axis=0)

    def flat_references(self, frequencies, harmonic, scale):
        return np.array([flat_mode(frequencies/self.lapse[i], harmonic, scale,
            self.radius[i], self.potential[i])/self.lapse[i] for i in self.probes]).transpose(1, 0, 2)
