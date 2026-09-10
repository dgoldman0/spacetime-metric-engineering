"""Finite-speed signal access to archived active material worldlines."""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq


class MaterialHistory:
    """Convex interpolation for a causal-access audit of saved material data.

    The metric remains independently evaluated at each spacetime point.
    Saved frame velocities are interpolated within their timelike range.
    This object supplies archived motion, not new mechanical evolution.
    """
    def __init__(self, patch, times, states):
        self.patch, self.model = patch, patch.model
        self.times = np.asarray(times)
        self.reference = np.r_[0., np.cumsum(patch.reference)]
        self.fraction = self.reference/self.reference[-1]
        self.fields = [patch.fields(float(t), y) for t, y in zip(times, states)]
        self.arrays = {key: np.array([f[key] for f in self.fields])
                       for key in ('x', 'velocity', 'heat', 'effective_n')}
        self.edges = patch.edges

    def sample(self, t):
        if not self.times[0]-1e-12 <= t <= self.times[-1]+1e-12:
            raise ValueError('requested time is outside the archived material history')
        i = int(np.clip(np.searchsorted(self.times, t), 1, len(self.times)-1))
        w = (t-self.times[i-1])/(self.times[i]-self.times[i-1])
        return {key: (1-w)*values[i-1]+w*values[i] for key, values in self.arrays.items()}

    def velocity(self, t, x):
        f = self.sample(t)
        return np.interp(x, f['x'], f['velocity'])

    def material_fraction(self, t, x):
        return np.interp(x, self.sample(t)['x'], self.fraction)

    def material_position(self, t, fraction):
        return np.interp(fraction, self.fraction, self.sample(t)['x'])


def signal_velocity(metric, material_velocity, speed, direction):
    if not 0 < speed <= 1 or direction not in (-1, 1):
        raise ValueError('0<relative speed<=1 and direction +/-1 required')
    normal = direction*np.ones_like(material_velocity) if speed == 1 else (
        material_velocity+direction*speed)/(1+direction*speed*material_velocity)
    return -metric.beta+metric.alpha*normal/metric.b


def trace_past_signal(history, event_time, event_x, speed, direction, *, max_step=.002):
    """Trace one edge of the past reachable set inside the material body.

    At a body end the earlier reachable edge follows that timelike end.
    Null-ray frequency gain is evaluated only along the freely propagating
    segment. No photon redshift is assigned to subluminal heat signals.
    """
    def rhs(t, state):
        x = state[:1]
        g = history.model.metric(t, x)
        v = history.velocity(t, x)
        rate = signal_velocity(g, v, speed, direction)
        frequency = g.alpha*g.k_l-direction*g.alpha_x/g.b if speed == 1 else np.zeros_like(rate)
        return np.array([rate[0], frequency[0]])

    bound = history.edges[0] if direction == 1 else history.edges[1]
    def boundary(t, state):
        return state[0]-bound
    boundary.terminal = True
    solution = solve_ivp(rhs, (event_time, float(history.times[0])), [event_x, 0.],
                          events=boundary, dense_output=True, rtol=2e-9, atol=2e-11,
                          max_step=max_step)
    if not solution.success:
        raise ArithmeticError(solution.message)
    first_time = float(solution.t[-1])

    def position(t):
        return float(solution.sol(max(t, first_time))[0])

    def latest_emission(fraction):
        def difference(t):
            return position(t)-history.material_position(t, fraction)
        lo, hi = float(history.times[0]), event_time
        if difference(lo)*difference(hi) > 0:
            return None
        return float(brentq(difference, lo, hi, xtol=1e-11))

    def null_comoving_gain(emission_time):
        if speed != 1 or emission_time < first_time:
            return None
        x0, log_frequency = solution.sol(emission_time)
        v0 = float(history.velocity(emission_time, np.array([x0]))[0])
        v1 = float(history.velocity(event_time, np.array([event_x]))[0])
        factor0 = (1-direction*v0)/np.sqrt(1-v0*v0)
        factor1 = (1-direction*v1)/np.sqrt(1-v1*v1)
        return float(factor1*np.exp(-log_frequency)/factor0)

    return dict(position=position, latest_emission=latest_emission,
                null_comoving_gain=null_comoving_gain,
                first_time=first_time, solution=solution)
