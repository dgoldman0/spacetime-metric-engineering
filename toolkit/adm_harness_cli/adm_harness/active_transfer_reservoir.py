"""Causal radial transfer stress on a scheduled spherical ADM background.

The medium is a pinned continuous interpolation of its archived orthonormal
moments, with explicit smooth support and packet exclusion. Its covariant
divergence drives two null streams. No static holding geometry is used.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.interpolate import RectBivariateSpline


def smooth_rise(z):
    z = np.asarray(z, dtype=float)
    u = np.clip(z, 0., 1.)
    value = u**3*(10+u*(-15+6*u))
    derivative = np.where((z > 0) & (z < 1), 30*u*u*(1-u)**2, 0.)
    return value, derivative


def medium_mask(t, x, *, outer=2.1, edge=.2, packet_radius=.35, packet_edge=.1):
    """C2 compact medium, excluded from the moving packet throughout the run."""
    x = np.asarray(x, dtype=float)
    body, db = smooth_rise((outer-np.abs(x))/edge)
    db_dx = -np.sign(x)*db/edge
    distance = x-t
    excluded, de = smooth_rise((np.abs(distance)-packet_radius)/packet_edge)
    de_dx = np.sign(distance)*de/packet_edge
    return body*excluded, -body*de_dx, db_dx*excluded+body*de_dx


@dataclass
class MetricJets:
    alpha: np.ndarray
    beta: np.ndarray
    b: np.ndarray
    radius: np.ndarray
    alpha_x: np.ndarray
    beta_x: np.ndarray
    logb_t: np.ndarray
    logb_x: np.ndarray
    logr_t: np.ndarray
    logr_x: np.ndarray

    @property
    def volume(self):
        return self.b*self.radius**2

    @property
    def k_l(self):
        return (self.beta_x+self.beta*self.logb_x-self.logb_t)/self.alpha

    @property
    def k_omega(self):
        return (self.beta*self.logr_x-self.logr_t)/self.alpha


def divergence_projections(g: MetricJets, moments, dt, dx):
    """P=-n_nu nabla_mu T^mu,nu and F=e_nu nabla_mu T^mu,nu.

    Moments are (rho, radial pressure, outward current, angular pressure).
    The two equations follow covariant energy and covariant radial-momentum
    conservation. Tests compare them with an independent 4D divergence.
    """
    rho, pressure, current, angular = moments
    rho_t, _, current_t, _ = dt
    rho_x, pressure_x, current_x, _ = dx
    a, b, beta = g.alpha, g.b, g.beta
    logv_t = g.logb_t+2*g.logr_t
    logv_x = g.logb_x+2*g.logr_x
    energy_flux = a*current/b-beta*rho
    energy_flux_x = ((g.alpha_x*current+a*current_x-a*current*g.logb_x)/b
                     -g.beta_x*rho-beta*rho_x)
    power = ((rho_t+logv_t*rho+logv_x*energy_flux+energy_flux_x)/a
             -g.k_l*pressure-2*g.k_omega*angular+current*g.alpha_x/(a*b))
    momentum_flux = a*pressure/b-beta*current
    momentum_flux_x = ((g.alpha_x*pressure+a*pressure_x-a*pressure*g.logb_x)/b
                       -g.beta_x*current-beta*current_x)
    force = ((current_t+(2*g.logb_t+2*g.logr_t)*current
              +(2*g.logb_x+2*g.logr_x)*momentum_flux+momentum_flux_x)/a
             +rho*g.alpha_x/(a*b)-current*g.beta_x/a
             -(pressure*g.logb_x+2*angular*g.logr_x)/b)
    return power, force


class TabulatedActiveMedium:
    def __init__(self, metric_path, medium_path):
        with np.load(metric_path) as data:
            self.t_min, self.t_max = float(data['t'][0]), float(data['t'][-1])
            self.x_min, self.x_max = float(data['x'][0]), float(data['x'][-1])
            self.core_radius = float(data['core_radius'])
            self.metric_splines = [RectBivariateSpline(data['t'], data['x'], data[k])
                                   for k in ('log_alpha', 'beta', 'log_b', 'log_r')]
        with np.load(medium_path) as data:
            self.medium_splines = [RectBivariateSpline(data['t'], data['x'], data[k])
                                   for k in ('rho', 'pressure', 'current', 'angular')]

    def metric(self, t, x):
        x = np.asarray(x, dtype=float)
        times = np.full_like(x, float(t))
        inside = (x >= self.x_min) & (x <= self.x_max)
        values = [np.zeros_like(x) for _ in range(4)]
        values[3] = .5*np.log(x*x+self.core_radius**2)
        dt = [np.zeros_like(x) for _ in range(4)]
        dx = [np.zeros_like(x) for _ in range(4)]
        dx[3] = x/(x*x+self.core_radius**2)
        for i, spline in enumerate(self.metric_splines):
            values[i][inside] = spline.ev(times[inside], x[inside])
            dx[i][inside] = spline.ev(times[inside], x[inside], dy=1)
            if i in (2, 3):
                dt[i][inside] = spline.ev(times[inside], x[inside], dx=1)
        # Complete the tabulated exterior with C2 matching. The medium is
        # confined to |x|<2.1; this blend occupies 5<|x|<6 and is separately
        # measured against the exact source evaluator.
        weight, derivative = smooth_rise((6.-np.abs(x)))
        derivative = -np.sign(x)*derivative
        background = .5*np.log(x*x+self.core_radius**2)
        background_x = x/(x*x+self.core_radius**2)
        for i in range(4):
            reference = background if i == 3 else np.zeros_like(x)
            reference_x = background_x if i == 3 else np.zeros_like(x)
            delta = values[i]-reference
            dx[i] = reference_x+weight*(dx[i]-reference_x)+derivative*delta
            dt[i] *= weight
            values[i] = reference+weight*delta
        alpha, beta, b, radius = np.exp(values[0]), values[1], np.exp(values[2]), np.exp(values[3])
        return MetricJets(alpha, beta, b, radius, alpha*dx[0], dx[1], dt[2], dx[2], dt[3], dx[3])

    def medium(self, t, x):
        x = np.asarray(x, dtype=float)
        times = np.full_like(x, float(t))
        mask, mask_t, mask_x = medium_mask(t, x)
        active = mask != 0
        values, dt, dx = [np.zeros((4, x.size)) for _ in range(3)]
        for i, spline in enumerate(self.medium_splines):
            v = spline.ev(times[active], x[active])
            values[i, active] = v*mask[active]
            dt[i, active] = spline.ev(times[active], x[active], dx=1)*mask[active]+v*mask_t[active]
            dx[i, active] = spline.ev(times[active], x[active], dy=1)*mask[active]+v*mask_x[active]
        return values, dt, dx

    def coefficients(self, t, x, direction):
        g = self.metric(t, x)
        power, force = divergence_projections(g, *self.medium(t, x))
        velocity = -g.beta+direction*g.alpha/g.b
        velocity_x = -g.beta_x+direction*(g.alpha_x-g.alpha*g.logb_x)/g.b
        gain = g.alpha*g.k_l-direction*g.alpha_x/g.b-velocity_x
        # Opposite exchange to the explicitly reconstructed medium.
        source = -.5*g.alpha*g.volume*(power+direction*force)
        return velocity, gain, source


def trace_characteristics(model, seeds, times, direction):
    """Integrate position, homogeneous log gain, and source in that frame.

    D=B R^2 mu, D(t)=exp(log_gain)*(D_initial+integral). The sampled minimum
    of the source integral gives a lower bound on every positive completion's
    required initial energy. Additional nonnegative preload increases D.
    """
    seeds, times = np.asarray(seeds, dtype=float), np.asarray(times, dtype=float)
    if direction not in (-1, 1) or np.any(np.diff(times) <= 0) or seeds.ndim != 1:
        raise ValueError('ordered times, one-dimensional seeds, and direction +/-1 required')
    history = np.zeros((len(times), 3, len(seeds)))
    history[0, 0] = seeds

    def rhs(t, state):
        velocity, gain, source = model.coefficients(t, state[0], direction)
        if np.any(np.abs(state[1]) > 500):
            raise ArithmeticError('homogeneous gain exceeded the registered numerical range')
        return np.array([velocity, gain, source*np.exp(-state[1])])

    for i, step in enumerate(np.diff(times)):
        t, y = times[i], history[i]
        k1 = rhs(t, y)
        k2 = rhs(t+.5*step, y+.5*step*k1)
        k3 = rhs(t+.5*step, y+.5*step*k2)
        k4 = rhs(t+step, y+step*k3)
        history[i+1] = y+step*(k1+2*k2+2*k3+k4)/6
        if not np.isfinite(history[i+1]).all():
            raise ArithmeticError('nonfinite characteristic state')
    return history


def required_preload(integral):
    integral = np.asarray(integral, dtype=float)
    if integral.ndim != 2 or not np.isfinite(integral).all():
        raise ValueError('finite time-by-characteristic source integrals required')
    return np.maximum(0., -np.min(integral, axis=0))
