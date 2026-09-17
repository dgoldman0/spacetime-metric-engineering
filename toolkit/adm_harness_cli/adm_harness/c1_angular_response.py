"""Normalized changes of the separate C1 conformal scalar's vacuum stress.

The comparison adds Dirichlet walls inside an existing Dirichlet module on
the SAME metric. Away from added walls the difference is finite and independent
of the common bulk renormalization constants. Absolute vacuum stress and the
new walls' renormalized self/material stresses are separate quantities.
"""
from dataclasses import dataclass

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.linalg import solveh_banded

from .c1_angular_scalar import scalar_curvature
from .c1_signed_channels import einstein_source


def improved_tensor(chart, coordinate, frequency, angular_index, diagonal,
                    first, mixed, coupling=1./6.):
    """Stress integrand from Green difference and proper-distance derivatives.

    first differentiates the coincident diagonal; mixed differentiates its
    two arguments separately. The homogeneous field equation supplies the
    second diagonal derivative. The Euclidean time continuation supplies the
    minus sign in <(partial_hat_t phi)^2>.
    """
    r, a, _, rp, _, ap, _ = chart.jets(coordinate)
    curvature = scalar_curvature(chart, coordinate)
    time = -frequency**2/a**2*diagonal
    angular = angular_index*(angular_index+1.)/(2*r*r)*diagonal
    second = (2*(frequency**2/a**2+angular_index*(angular_index+1.)/r**2
                 +coupling*curvature)*diagonal+2*mixed-(ap+2*rp/r)*first)
    minimal = np.stack((.5*(time+mixed+2*angular),
                        .5*(time+mixed-2*angular), .5*(time-mixed)), axis=-1)
    einstein = 8*np.pi*einstein_source(chart, coordinate)
    improvement = einstein*diagonal[..., None]+np.stack(
        (-second-2*rp/r*first, (ap+2*rp/r)*first,
         second+(ap+rp/r)*first), axis=-1)
    return minimal+coupling*improvement


@dataclass
class AngularResponse:
    """Finite-volume original-field Green problem with exact wall/probe nodes."""
    chart: object
    domain: tuple
    walls: np.ndarray
    probes: np.ndarray
    nodes: int = 8193

    def __post_init__(self):
        lo, hi = self.domain
        self.walls, self.probes = np.asarray(self.walls, float), np.asarray(self.probes, float)
        if (not self.chart.coordinate[0] <= lo < hi <= self.chart.coordinate[-1]
                or not isinstance(self.nodes, (int, np.integer)) or self.nodes < 33
                or self.walls.ndim != 1 or self.probes.ndim != 1
                or not len(self.walls) or not len(self.probes)
                or not np.isfinite(np.r_[self.walls, self.probes]).all()
                or np.any((self.walls <= lo) | (self.walls >= hi))
                or np.any((self.probes < lo) | (self.probes > hi))
                or len(np.unique(self.walls)) != len(self.walls)
                or np.any(self.walls[:, None] == self.probes[None, :])):
            raise ValueError("resolved in-chart module, interior walls and off-wall probes required")
        anchors = np.unique(np.r_[lo, hi, self.walls, self.probes])
        base = np.linspace(lo, hi, self.nodes)
        h = (hi-lo)/(self.nodes-1)
        # Avoid ill-conditioned sliver cells around anchors.
        keep = np.min(abs(base[:, None]-anchors[None, :]), axis=1) > .15*h
        self.x = np.unique(np.r_[base[keep], anchors])
        self.wall_nodes = np.searchsorted(self.x, self.walls)
        self.probe_nodes = np.searchsorted(self.x, self.probes)
        self.h = np.diff(self.x)
        rm, am, bm, *_ = self.chart.jets((self.x[1:]+self.x[:-1])/2)
        self.links = am*rm*rm/(bm*self.h)
        self.volume = (self.h[1:]+self.h[:-1])/2
        self.r, self.a, self.b, *_ = self.chart.jets(self.x[1:-1])
        self.curvature = scalar_curvature(self.chart, self.x[1:-1])
        self.probe_b = self.chart.jets(self.probes)[2]
        self.derivative_nodes, self.derivative_weights = [], []
        for i, b in zip(self.probe_nodes, self.probe_b):
            start = int(np.clip(i-2, 0, len(self.x)-5))
            indices = np.arange(start, start+5)
            dx = self.x[indices]-self.x[i]
            scale = max(abs(dx))
            weights = np.linalg.solve(np.stack([(dx/scale)**k for k in range(5)]),
                                      [0., 1., 0., 0., 0.])/scale
            self.derivative_nodes.append(indices)
            self.derivative_weights.append(weights/b)
        self.derivative_nodes = np.asarray(self.derivative_nodes)
        self.derivative_weights = np.asarray(self.derivative_weights)
        zero, one = np.zeros(len(self.probes)), np.ones(len(self.probes))
        basis = [(one, zero, zero), (zero, one, zero), (zero, zero, one)]
        self.stress_matrix = np.stack([improved_tensor(self.chart, self.probes, 0., 0, *v)
                                      for v in basis], axis=-1)
        self.frequency_column = (improved_tensor(self.chart, self.probes, 1., 0, *basis[0])
                                 -self.stress_matrix[..., 0])
        self.angular_column = (improved_tensor(self.chart, self.probes, 0., 1, *basis[0])
                               -self.stress_matrix[..., 0])/2

    def moments(self, frequency, angular_index):
        if frequency < 0 or not np.isfinite(frequency) or angular_index < 0:
            raise ValueError("finite nonnegative frequency and angular index required")
        q = self.a*self.b*(angular_index*(angular_index+1.)
            +self.r**2*(frequency**2/self.a**2+self.curvature/6.))
        diagonal = self.links[:-1]+self.links[1:]+self.volume*q
        band = np.zeros((2, len(diagonal)))
        band[0], band[1, :-1] = diagonal, -self.links[1:-1]
        rhs = np.zeros((len(diagonal), len(self.walls)))
        rhs[self.wall_nodes-1, np.arange(len(self.walls))] = 1.
        interior = solveh_banded(band, rhs, lower=True, check_finite=False,
                                overwrite_ab=True, overwrite_b=True)
        columns = np.pad(interior, ((1, 1), (0, 0)))
        values = columns[self.probe_nodes]
        derivative = np.einsum('pk,pkm->pm', self.derivative_weights, columns[self.derivative_nodes])
        wall_green = columns[self.wall_nodes]
        wall_green = (wall_green+wall_green.T)/2
        inv_values = np.linalg.solve(wall_green, values.T).T
        inv_derivative = np.linalg.solve(wall_green, derivative.T).T
        f = -np.sum(values*inv_values, axis=1)
        first = -2*np.sum(derivative*inv_values, axis=1)
        mixed = -np.sum(derivative*inv_derivative, axis=1)
        return f, first, mixed

    def tensor(self, frequency, angular_index):
        moments = np.array(self.moments(frequency, angular_index)).T
        return (np.einsum('pij,pj->pi', self.stress_matrix, moments)
                +(frequency**2*self.frequency_column
                  +angular_index*(angular_index+1.)*self.angular_column)*moments[:, :1])


def frequency_rule(nodes, scale):
    """Gauss quadrature of the whole positive frequency axis."""
    if not isinstance(nodes, (int, np.integer)) or nodes < 8 or scale <= 0:
        raise ValueError("at least eight nodes and a positive frequency scale required")
    t, w = leggauss(nodes)
    t, w = (t+1)/2, w/2
    return scale*t/(1-t), scale*w/(1-t)**2


def integrate_response(problem, *, angular_max, frequency_nodes, frequency_scale, eta):
    """One real field; arrays retain each harmonic to audit angular tails."""
    if not isinstance(angular_max, (int, np.integer)) or angular_max < 0 or eta <= 0:
        raise ValueError("nonnegative integer harmonic cutoff and positive conversion required")
    frequencies, weights = frequency_rule(frequency_nodes, frequency_scale)
    harmonic = np.zeros((angular_max+1, len(problem.probes), 3))
    for j in range(angular_max+1):
        for frequency, weight in zip(frequencies, weights):
            harmonic[j] += weight*problem.tensor(frequency, j)
        harmonic[j] *= eta*(2*j+1)/(4*np.pi**2)
    return dict(tensor=harmonic.sum(axis=0), harmonic_tensor=harmonic)


def cylinder_green_excess(frequency, angular_index, coordinate, domain, radius, lapse=1.):
    """Analytic cylinder Green moments relative to the infinite cylinder.

    Boundary-dependent expressions avoid subtracting the common ultraviolet
    terms. Normalization is the original scalar variable, including A R².
    """
    x = np.asarray(coordinate, float)
    lo, hi = domain
    if np.any((x < lo) | (x > hi)) or radius <= 0 or lapse <= 0:
        raise ValueError("in-interval probes and positive cylinder metric required")
    k = np.sqrt(frequency**2/lapse**2+(angular_index*(angular_index+1.)+1./3.)/radius**2)
    left, right = np.exp(-2*k*(x-lo)), np.exp(-2*k*(hi-x))
    both, norm = np.exp(-2*k*(hi-lo)), -np.expm1(-2*k*(hi-lo))
    f = (-left-right+2*both)/(2*k*norm)
    first = (left-right)/norm
    mixed = -k*(left+right+2*both)/(2*norm)
    return np.array([f, first, mixed])/(lapse*radius**2)


def cylinder_interaction(radius, length, *, angular_max=256, winding_max=256, eta=1.):
    """Finite two-end interaction energy, pressures and optimistic holding cost.

    Exact product-cylinder benchmark. The local clock is proper time. Isolated
    end self energies and measured material rest energies remain separate.
    Axial DEC holding floor assumes a direct static support in this cylinder.
    """
    from scipy.special import kv
    if radius <= 0 or length <= 0 or eta <= 0 or min(angular_max, winding_max) < 1:
        raise ValueError("positive radius, length, conversion and sum limits required")
    j, n = np.arange(angular_max+1)[:, None], np.arange(1, winding_max+1)[None, :]
    mass = np.sqrt(j*(j+1)+1./3.)/radius
    arg = 2*length*mass*n
    degeneracy = 2*j+1
    energy = -eta*np.sum(degeneracy*mass*kv(1, arg)/n)/(2*np.pi)
    force = -eta*np.sum(degeneracy*mass**2*(kv(0, arg)+kv(2, arg)))/(2*np.pi)
    area = 4*np.pi*radius**2
    rho, pr = energy/(area*length), force/area
    return dict(energy=float(energy), force=float(force),
        energy_over_cavity_volume=float(rho), force_over_area=float(pr),
        radius_virtual_work_over_volume=float((rho-pr)/2),
        axial_dec_holding_floor=float(length*abs(force)),
        interaction_plus_axial_floor=float(energy+length*abs(force)))
