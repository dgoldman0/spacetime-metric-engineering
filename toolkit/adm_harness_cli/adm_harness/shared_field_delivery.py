"""Allocate existing radial Maxwell stress to a paired magnetic work guide."""
from __future__ import annotations

import numpy as np

from .active_transfer_reservoir import smooth_rise


def electric_share_cap(times, field, lapse, *, rate_ceiling=1., electric_floor=.1):
    """Largest static subtraction retaining the archived exponential rate bound.

Both directions obey E_i >= decay E_(i-1). Subtracting constant S gives
S <= (H_i-decay H_(i-1))/(1-decay), and its reverse-time counterpart.
The electric energy floor supplies finite voltage and current margins.
"""
    times, field, lapse = map(np.asarray, (times, field, lapse))
    if (field.shape != lapse.shape or field.shape[0] != len(times)
            or field.ndim != 2 or np.any(field <= 0) or np.any(lapse <= 0)
            or np.any(np.diff(times) <= 0) or rate_ceiling <= 0
            or not 0 < electric_floor < 1):
        raise ValueError('positive fields and lapse, ordered times, and a finite floor required')
    exponent = -rate_ceiling*(lapse[1:]+lapse[:-1])*np.diff(times)[:, None]
    decay = np.exp(exponent)
    denominator = -np.expm1(exponent)
    limit = np.minimum(field[1:]-decay*field[:-1], field[:-1]-decay*field[1:])/denominator
    return np.maximum(0., np.minimum((1-electric_floor)*field.min(axis=0), limit.min(axis=0)))


def smooth_under_cap(positions, cap, knots, *, safety=.98):
    """C2 profile under a nonnegative piecewise-linear sampled cap.

Each knot value is bounded by both adjoining intervals' minima. Quintic
interpolation is convex between these values and has zero first and second
derivatives at each knot. Every interval therefore remains below its cap.
"""
    positions, cap, knots = map(np.asarray, (positions, cap, knots))
    if (positions.shape != cap.shape or positions.ndim != 1 or np.any(cap < 0)
            or np.any(np.diff(positions) <= 0) or np.any(np.diff(knots) <= 0)
            or knots[0] > positions[0] or knots[-1] < positions[-1]
            or not 0 < safety <= 1):
        raise ValueError('ordered covered samples, nonnegative cap, and finite safety required')
    minima = []
    for left, right in zip(knots[:-1], knots[1:]):
        points = np.r_[left, positions[(positions > left)&(positions < right)], right]
        minima.append(np.interp(points, positions, cap).min())
    minima = np.asarray(minima)
    values = safety*np.r_[minima[0], np.minimum(minima[:-1], minima[1:]), minima[-1]]
    index = np.clip(np.searchsorted(knots, positions, side='right')-1, 0, len(knots)-2)
    width = knots[index+1]-knots[index]
    rise, derivative = smooth_rise((positions-knots[index])/width)
    profile = values[index]+(values[index+1]-values[index])*rise
    gradient = (values[index+1]-values[index])*derivative/width
    return profile, gradient, values


def radial_field_moments(energy):
    energy = np.asarray(energy)
    return np.array([energy, -energy, np.zeros_like(energy), energy])


def average_electric_rate(times, field, lapse):
    return abs(np.diff(np.log(field), axis=0))/(np.diff(times)[:, None]*(lapse[1:]+lapse[:-1]))


def cold_current_velocities(kappa, mass_ratio=1.):
    """Cold longitudinal two-fluid travelling-wave current closure.

Extends Chen et al.'s equal-mass equations by conserving m_plus*q_plus +
m_minus*q_minus. Kappa=j/(e n0 c), q=gamma(1-beta). This is the local strong-
guide plane-wave model; transverse dynamics and kinetic stability are separate.
"""
    from scipy.optimize import brentq
    if mass_ratio <= 0 or not np.isfinite(kappa):
        raise ValueError('finite current ratio and positive mass ratio required')
    # Solve in q_minus to resolve the light species when mass_ratio is large.
    def equation(qm):
        qp = (mass_ratio+1-qm)/mass_ratio
        return 1/qp**2-1/qm**2-2*kappa
    qm = brentq(equation, 1e-9, mass_ratio+1-1e-9, xtol=1e-13)
    qp = (mass_ratio+1-qm)/mass_ratio
    beta = lambda q: (1-q*q)/(1+q*q)
    return beta(qp), beta(qm)
