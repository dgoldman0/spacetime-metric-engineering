"""Finite spherical boundary response on a specified static curved geometry.

The returned tensor is the with-boundary minus without-boundary vacuum
expectation on the same metric. It excludes the absolute curved vacuum,
the sheets' matched material tensor, and points on the sheets.
"""
from dataclasses import dataclass
from itertools import product

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import cumulative_simpson
from scipy.interpolate import CubicSpline, PchipInterpolator
from scipy.linalg import solveh_banded


@dataclass
class StaticGeometry:
    coordinate: np.ndarray
    radius: np.ndarray
    lapse: np.ndarray
    radial_scale: np.ndarray
    throat_parameter: float = 1.75

    def __post_init__(self):
        arrays = (self.coordinate, self.radius, self.lapse, self.radial_scale)
        if any(np.ndim(a) != 1 or not np.isfinite(a).all() for a in arrays):
            raise ValueError('finite one-dimensional geometry arrays required')
        if any(len(a) != len(self.coordinate) for a in arrays):
            raise ValueError('geometry arrays must align')
        if np.any(np.diff(self.coordinate) <= 0) or min(np.min(a) for a in arrays[1:]) <= 0:
            raise ValueError('increasing coordinate and positive metric required')
        self._splines = [CubicSpline(self.coordinate, np.log(a)) for a in arrays[1:]]

    def values(self, coordinate, derivative=0):
        x = np.asarray(coordinate, float)
        inside = (x >= self.coordinate[0]) & (x <= self.coordinate[-1])
        tabulated_x = np.clip(x, self.coordinate[0], self.coordinate[-1])
        radius = np.sqrt(x*x+self.throat_parameter**2)
        tail = [radius, np.ones_like(x), np.ones_like(x)]
        tail_log_derivative = [x/(radius*radius), np.zeros_like(x), np.zeros_like(x)]
        if derivative not in (0, 1):
            raise ValueError('values or logarithmic first derivatives supported')
        return tuple(np.where(inside, np.exp(s(tabulated_x)) if derivative == 0 else s(tabulated_x, 1), t)
                     for s, t in zip(self._splines, tail if derivative == 0 else tail_log_derivative))

    def negative_branch_coordinate(self, radius):
        selected = self.coordinate < -.4
        rr, xx = self.radius[selected][::-1], self.coordinate[selected][::-1]
        if np.any(np.diff(rr) <= 0):
            raise ValueError('selected branch must have monotone areal radius')
        values = np.asarray(radius, float)
        if np.any((values < rr[0]) | (values > rr[-1])):
            raise ValueError('requested radius is outside the tabulated negative branch')
        return PchipInterpolator(rr, xx)(values)

    def proper_coordinate(self, coordinate):
        primitive = cumulative_simpson(self.radial_scale, x=self.coordinate, initial=0.)
        return CubicSpline(self.coordinate, primitive)(coordinate)


def placements():
    arrangements = {'inner': (1,), 'inner_pair': (0, 1),
                    'spanning_pair': (0, 2), 'outer': (2,)}
    return [{'name': name, 'indices': indices, 'coupling': coupling}
            for name, coupling in product(arrangements, (1., 8., 64.))
            for indices in [arrangements[name]]]


def radial_mesh(spacing, extent, anchors=()):
    """Uniform resolved core and graded asymptotic tails, with exact anchors."""
    if spacing <= 0 or extent <= 8:
        raise ValueError('positive core spacing and extent above eight required')
    intervals = int(np.ceil(16/spacing))
    core = np.linspace(-8., 8., intervals+1)
    tail_intervals = int(np.ceil(np.log(extent/8.)/(spacing/8.)))
    # Tail spacing grows with distance while preserving the core resolution.
    tail = np.geomspace(8., extent, tail_intervals+1)
    points = np.sort(np.r_[-tail[1:], core, tail[1:]])
    anchors = np.asarray(anchors, float)
    if np.any(np.abs(anchors) >= extent):
        raise ValueError('anchors must be strictly interior')
    if len(anchors):
        # Avoid a nearly zero cell when an anchor coincides with a core node.
        keep = np.min(np.abs(points[:, None]-anchors[None, :]), axis=1) > spacing*1e-5
        points = np.unique(np.r_[points[keep], anchors])
    return points


@dataclass
class RadialProblem:
    coordinate: np.ndarray
    radius: np.ndarray
    lapse: np.ndarray
    radial_scale: np.ndarray
    kinetic_midpoint: np.ndarray
    wall_nodes: np.ndarray
    probe_nodes: np.ndarray

    @classmethod
    def create(cls, geometry, spacing, extent, walls, probes):
        x = radial_mesh(spacing, extent, np.r_[walls, probes])
        r, alpha, a = geometry.values(x)
        rm, nm, am = geometry.values(.5*(x[1:]+x[:-1]))
        return cls(x, r, alpha, a, nm*rm*rm/am,
                   np.searchsorted(x, walls), np.searchsorted(x, probes))

    def green_columns(self, frequency, angular_index):
        """Continuum-normalized Green columns from a positive finite-volume form."""
        if frequency < 0 or angular_index < 0:
            raise ValueError('nonnegative Euclidean frequency and angular index required')
        h = np.diff(self.coordinate)
        links = self.kinetic_midpoint/h
        volume = .5*(h[1:]+h[:-1])
        r, n, a = self.radius[1:-1], self.lapse[1:-1], self.radial_scale[1:-1]
        q = n*a*(angular_index*(angular_index+1)+frequency**2*r*r/(n*n))
        diagonal = links[1:]+links[:-1]+volume*q
        band = np.zeros((2, len(diagonal)))
        band[0] = diagonal
        band[1, :-1] = -links[1:-1]
        rhs = np.zeros((len(diagonal), len(self.wall_nodes)))
        rhs[self.wall_nodes-1, np.arange(len(self.wall_nodes))] = 1.
        interior = solveh_banded(band, rhs, lower=True, check_finite=False,
                                overwrite_ab=True, overwrite_b=True)
        columns = np.zeros((len(self.coordinate), len(self.wall_nodes)))
        columns[1:-1] = interior
        return columns

    def samples(self, columns):
        i = self.probe_nodes
        hl, hr = self.coordinate[i]-self.coordinate[i-1], self.coordinate[i+1]-self.coordinate[i]
        derivative = ((-hr/(hl*(hl+hr)))[:, None]*columns[i-1]
                      +((hr-hl)/(hl*hr))[:, None]*columns[i]
                      +(hl/(hr*(hl+hr)))[:, None]*columns[i+1])
        return columns[i], derivative, columns[self.wall_nodes]


def response_kernel(values, derivatives, wall_green, optical_weights):
    """Coincident difference and its mixed radial derivative for passive sheets."""
    weights = np.asarray(optical_weights, float)
    if np.any(weights <= 0) or not np.isfinite(weights).all():
        raise ValueError('positive finite optical weights required')
    matrix = .5*(wall_green+wall_green.T)+np.diag(1/weights)
    inverse_values = np.linalg.solve(matrix, values.T).T
    inverse_derivatives = np.linalg.solve(matrix, derivatives.T).T
    diagonal = -np.sum(values*inverse_values, axis=1)
    mixed_derivative = -np.sum(derivatives*inverse_derivatives, axis=1)
    return diagonal, mixed_derivative


def mode_moments(problem, frequency, angular_index, cases=None):
    cases = placements() if cases is None else cases
    columns = problem.green_columns(frequency, angular_index)
    values, derivatives, wall_green = problem.samples(columns)
    probe, walls = problem.probe_nodes, problem.wall_nodes
    r, n, a = problem.radius[probe], problem.lapse[probe], problem.radial_scale[probe]
    result = []
    for case in cases:
        indices = np.asarray(case['indices'])
        chosen_walls = walls[indices]
        optical = case['coupling']*problem.lapse[chosen_walls]*problem.radius[chosen_walls]**2
        diagonal, mixed = response_kernel(values[:, indices], derivatives[:, indices],
            wall_green[np.ix_(indices, indices)], optical)
        result.append(np.stack([-frequency**2*diagonal/(n*n), mixed/(a*a),
            angular_index*(angular_index+1)*diagonal/(2*r*r)], axis=-1))
    return np.array(result)


def tensor_from_moments(moments):
    a, b, c = np.moveaxis(np.asarray(moments), -1, 0)
    return np.stack([.5*(a+b+2*c), .5*(a+b-2*c), .5*(a-b), a+b, a+c], axis=-1)


def frequency_quadrature(nodes, upper=2048., lower=1e-7):
    if nodes < 8 or not 0 < lower < upper:
        raise ValueError('at least eight nodes and positive ordered frequency endpoints required')
    x, w = leggauss(nodes)
    low, high = np.log(lower), np.log(upper)
    frequency = np.exp(.5*(high-low)*x+.5*(high+low))
    return frequency, .5*(high-low)*w*frequency


def constant_green(frequency, coordinate, walls, extent):
    """Dirichlet Green function of -d²/dx² + frequency² on [-extent, extent]."""
    k = float(frequency)
    x, y = np.asarray(coordinate, float)[:, None], np.asarray(walls, float)[None, :]
    lo, hi = np.minimum(x, y), np.maximum(x, y)
    if k == 0:
        return (lo+extent)*(extent-hi)/(2*extent)
    return (np.exp(-k*(hi-lo))*(-np.expm1(-2*k*(lo+extent)))
            *(-np.expm1(-2*k*(extent-hi)))/(2*k*(-np.expm1(-4*k*extent))))
