"""Axisymmetric massless scalar field on a stationary background moving with the pattern.

In the frame that moves with the pattern during the lane, the metric reads
-alpha^2 dt^2 + (dzeta + b dt)^2 + dr^2 + r^2 dphi^2, with the lapse alpha(zeta, r) and the co-moving shift
b = beta + v fixed in time. With the normal derivative Pi = (d_t phi - b d_zeta phi)/alpha, the wave equation
box phi = 0 becomes

    d_t phi = alpha Pi + b d_zeta phi,
    d_t Pi  = d_zeta(b Pi) + d_zeta(alpha d_zeta phi) + (1/r) d_r(r alpha d_r phi).

The normal observers measure the energy density (Pi^2 + (d_zeta phi)^2 + (d_r phi)^2)/2, and the Killing energy
integral of alpha e + b Pi d_zeta phi over the slice is conserved away from absorbing layers. The solver uses
fourth-order central differences on a grid cell-centred in r, with the axis handled by the even reflection
phi(-r) = phi(r), sixth-order Kreiss-Oliger dissipation, damping layers at the grid edges, and classical RK4 in t.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math

import numpy as np

GHOST = 3


def _d1(f, axis, h):
    """Fourth-order central first derivative of a padded array along axis, on the interior."""
    s = [slice(GHOST, -GHOST)]*2

    def shift(k):
        idx = list(s)
        idx[axis] = slice(GHOST+k, f.shape[axis]-GHOST+k)
        return f[tuple(idx)]
    return (shift(-2)-8*shift(-1)+8*shift(1)-shift(2))/(12*h)


def _d2(f, axis, h):
    """Fourth-order central second derivative of a padded array along axis, on the interior."""
    s = [slice(GHOST, -GHOST)]*2

    def shift(k):
        idx = list(s)
        idx[axis] = slice(GHOST+k, f.shape[axis]-GHOST+k)
        return f[tuple(idx)]
    return (-shift(-2)+16*shift(-1)-30*shift(0)+16*shift(1)-shift(2))/(12*h*h)


def _dissipation(f, axis, h, strength):
    """Sixth-order Kreiss-Oliger dissipation along axis, on the interior."""
    s = [slice(GHOST, -GHOST)]*2

    def shift(k):
        idx = list(s)
        idx[axis] = slice(GHOST+k, f.shape[axis]-GHOST+k)
        return f[tuple(idx)]
    return strength/(64*h)*(shift(-3)-6*shift(-2)+15*shift(-1)-20*shift(0)+15*shift(1)-6*shift(2)+shift(3))


@dataclass
class AxisymmetricWave:
    """Grid, background and state for the axisymmetric scalar field.

    zeta and r are the cell coordinates (r cell-centred from dr/2). alpha and b are background arrays on the
    grid, and damping is the absorbing-layer rate. phi and Pi hold the state.
    """
    zeta: np.ndarray
    r: np.ndarray
    alpha: np.ndarray
    b: np.ndarray
    damping: np.ndarray
    dissipation: float = .05
    phi: np.ndarray = field(init=False)
    Pi: np.ndarray = field(init=False)

    def __post_init__(self):
        self.dz = float(self.zeta[1]-self.zeta[0])
        self.dr = float(self.r[1]-self.r[0])
        if abs(self.r[0]-self.dr/2) > 1e-12*self.dr:
            raise ValueError("r must be cell-centred, starting at dr/2")
        shape = (len(self.zeta), len(self.r))
        for name in ("alpha", "b", "damping"):
            if getattr(self, name).shape != shape:
                raise ValueError(f"{name} must have shape {shape}")
        self.alpha_z = _d1(self._pad(self.alpha, hold=True), 0, self.dz)
        self.alpha_r = _d1(self._pad(self.alpha, hold=True), 1, self.dr)
        self.rr = self.r[None, :]
        self.phi = np.zeros(shape)
        self.Pi = np.zeros(shape)
        self._buffers = [np.zeros((shape[0]+2*GHOST, shape[1]+2*GHOST)) for _ in range(3)]

    def _fill(self, index, f):
        """Write f into a preallocated padded buffer with the axis reflection; the other ghosts stay zero."""
        buffer = self._buffers[index]
        buffer[GHOST:-GHOST, GHOST:-GHOST] = f
        buffer[GHOST:-GHOST, GHOST-1::-1] = f[:, :GHOST]
        return buffer

    def _pad(self, f, hold=False):
        """Ghost cells: even reflection across the axis, zero (or the edge value, hold=True) at the other edges."""
        out = np.zeros((f.shape[0]+2*GHOST, f.shape[1]+2*GHOST))
        out[GHOST:-GHOST, GHOST:-GHOST] = f
        for k in range(GHOST):
            out[GHOST:-GHOST, GHOST-1-k] = f[:, k]
        if hold:
            out[:GHOST, :] = out[GHOST:GHOST+1, :]
            out[-GHOST:, :] = out[-GHOST-1:-GHOST, :]
            out[:, -GHOST:] = out[:, -GHOST-1:-GHOST]
        return out

    def rates(self, phi, Pi):
        pp, pq, bq = self._fill(0, phi), self._fill(1, Pi), self._fill(2, self.b*Pi)
        phi_z, phi_r = _d1(pp, 0, self.dz), _d1(pp, 1, self.dr)
        dphi = self.alpha*Pi+self.b*phi_z
        dPi = (_d1(bq, 0, self.dz)+self.alpha*_d2(pp, 0, self.dz)+self.alpha_z*phi_z
               + self.alpha*(_d2(pp, 1, self.dr)+phi_r/self.rr)+self.alpha_r*phi_r)
        if self.dissipation:
            dphi += _dissipation(pp, 0, self.dz, self.dissipation)+_dissipation(pp, 1, self.dr, self.dissipation)
            dPi += _dissipation(pq, 0, self.dz, self.dissipation)+_dissipation(pq, 1, self.dr, self.dissipation)
        return dphi-self.damping*phi, dPi-self.damping*Pi

    def step(self, dt):
        k1 = self.rates(self.phi, self.Pi)
        k2 = self.rates(self.phi+dt/2*k1[0], self.Pi+dt/2*k1[1])
        k3 = self.rates(self.phi+dt/2*k2[0], self.Pi+dt/2*k2[1])
        k4 = self.rates(self.phi+dt*k3[0], self.Pi+dt*k3[1])
        self.phi = self.phi+dt/6*(k1[0]+2*k2[0]+2*k3[0]+k4[0])
        self.Pi = self.Pi+dt/6*(k1[1]+2*k2[1]+2*k3[1]+k4[1])

    def stable_step(self, courant=.4):
        speed_z = float(np.max(np.abs(self.b)+self.alpha))
        speed_r = float(np.max(self.alpha))
        return courant*min(self.dz/speed_z, self.dr/speed_r)

    def energy_density(self):
        pp = self._pad(self.phi)
        return .5*(self.Pi**2+_d1(pp, 0, self.dz)**2+_d1(pp, 1, self.dr)**2)

    def cell_volume(self):
        return 2*math.pi*self.rr*self.dr*self.dz*np.ones_like(self.phi)

    def killing_energy(self, mask=None):
        pp = self._pad(self.phi)
        density = self.alpha*self.energy_density()+self.b*self.Pi*_d1(pp, 0, self.dz)
        volume = self.cell_volume()
        return float(np.sum((density*volume) if mask is None else (density*volume)[mask]))

    def set_packet(self, zeta0, r0, width_zeta, width_r, wavelength, amplitude=1., direction=1.):
        """Gaussian ring (on the axis when r0 = 0) with a carrier along zeta, moving along +zeta (direction 1) or
        -zeta (direction -1) relative to the normal observers."""
        z, r = self.zeta[:, None], self.rr
        envelope = np.exp(-(z-zeta0)**2/(2*width_zeta**2)-(r-r0)**2/(2*width_r**2))
        if r0:
            envelope = envelope+np.exp(-(z-zeta0)**2/(2*width_zeta**2)-(r+r0)**2/(2*width_r**2))
        k = 2*math.pi/wavelength
        self.phi = amplitude*envelope*np.cos(k*(z-zeta0))
        pp = self._pad(self.phi)
        self.Pi = -direction*_d1(pp, 0, self.dz)


def damping_layer(zeta, r, *, back, front, outer, rate):
    """Absorbing-layer rate rising as the square of the depth into layers of the given widths at the edges."""
    z, rr = zeta[:, None], r[None, :]
    depth = np.zeros((len(zeta), len(r)))
    if back:
        depth = np.maximum(depth, np.clip((zeta[0]+back-z)/back, 0, 1))
    if front:
        depth = np.maximum(depth, np.clip((z-(zeta[-1]-front))/front, 0, 1))
    if outer:
        depth = np.maximum(depth, np.clip((rr-(r[-1]-outer))/outer, 0, 1))
    return rate*depth**2
