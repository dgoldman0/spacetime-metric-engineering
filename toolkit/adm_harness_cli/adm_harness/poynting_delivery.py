"""Necessary causal energy and reaction screen for a finite guided work route.

Geometric-optics wave stresses propagate on the scheduled spherical metric.
The prescribed converter taps remove positive work and emit recovered work.
Guide fields, plasma inertia, transverse confinement, and converter dynamics
are additional construction requirements. Boundary energy is explicitly paid.
"""
from __future__ import annotations

import numpy as np


def minmod(a, b):
    return np.where(a*b > 0, np.sign(a)*np.minimum(abs(a), abs(b)), 0.)


def transport_rhs(energy, faces, gain, source, dx):
    """Positive-source finite-volume advection with zero incident boundary data.

Energy is the cell average of B R^2 mu. Limited piecewise-linear spatial
reconstruction and SSP RK2 stepping give a conservative, positivity-preserving
method at the runner's CFL. Boundary fluxes use one-sided constant states.
"""
    energy, faces, gain, source = map(np.asarray, (energy, faces, gain, source))
    if (energy.ndim != 1 or faces.shape != (len(energy)+1,)
            or gain.shape != energy.shape or source.shape != energy.shape or dx <= 0):
        raise ValueError('cell states, face velocities, and positive spacing required')
    slope = np.zeros_like(energy)
    slope[1:-1] = minmod(energy[1:-1]-energy[:-2], energy[2:]-energy[1:-1])
    left = np.r_[0., energy+.5*slope]
    right = np.r_[energy-.5*slope, 0.]
    flux = faces*np.where(faces >= 0., left, right)
    derivative = -(flux[1:]-flux[:-1])/dx+gain*energy+source
    terms = np.array([flux[0]-flux[-1], dx*np.sum(gain*energy), dx*np.sum(source)])
    return derivative, terms


def propagate(times, edges, coefficients, *, backwards=False, cfl=.35):
    """Solve an emitted stream forward, or its least prepared absorption backward.

coefficients(time, original_interval) returns (face velocity, homogeneous
gain, positive source). Physical absorption has a negative source. Reversing
its time gives positive emission, reversed advection, and negative gain.
Zero future inventory and zero outgoing physical flux give its least
nonnegative solution. The resulting incident flux is part of the evidence.
"""
    times, edges = np.asarray(times), np.asarray(edges)
    if (len(times) < 2 or len(edges) < 3 or np.any(np.diff(times) <= 0)
            or not np.allclose(np.diff(edges), np.diff(edges)[0])
            or not 0 < cfl <= .4):
        raise ValueError('ordered times, uniform cells, and CFL in (0,.4] required')
    dx = edges[1]-edges[0]
    history = np.zeros((len(times), len(edges)-1))
    records = []
    order = range(len(times)-2, -1, -1) if backwards else range(len(times)-1)
    sign = -1 if backwards else 1
    state = np.zeros(len(edges)-1)
    for i in order:
        start = times[i+1] if backwards else times[i]
        duration = times[i+1]-times[i]
        samples = [coefficients(float(tt), i) for tt in (times[i], (times[i]+times[i+1])/2, times[i+1])]
        speed = max(abs(item[0]).max() for item in samples)
        rate = max(abs(item[1]).max() for item in samples)
        count = max(1, int(np.ceil(duration*(speed/dx+rate)/cfl)))
        step = duration/count
        ledger = np.zeros(3)
        before = dx*state.sum()
        for j in range(count):
            now = start+sign*j*step

            def rhs(y, tt):
                velocity, gain, source = coefficients(float(tt), i)
                return transport_rhs(y, sign*velocity, sign*gain, source, dx)

            k1, l1 = rhs(state, now)
            trial = state+step*k1
            k2, l2 = rhs(trial, now+sign*step)
            state = .5*(state+trial+step*k2)
            if state.min() < -1e-11 or not np.isfinite(state).all():
                raise ArithmeticError('wave energy lost positivity or finiteness')
            ledger += .5*step*(l1+l2)
        target = i if backwards else i+1
        history[target] = state
        records.append(dict(interval=i, substeps=count, boundary=float(ledger[0]),
            geometric=float(ledger[1]), source=float(ledger[2]),
            inventory_change=float(dx*state.sum()-before),
            balance_residual=float(dx*state.sum()-before-ledger.sum())))
    return history, sorted(records, key=lambda item: item['interval'])


def wave_moments(positive, negative):
    total = np.asarray(positive)+np.asarray(negative)
    return np.array([total, total, np.asarray(positive)-negative, np.zeros_like(total)])


def guide_energy_bound(wave_rest_energy, drift_fraction):
    """Local single-travelling-wave guide requirement from E/B <= drift speed.

For E^2=B_wave^2=u_wave in c=1 units, u_guide=B_guide^2/2.
Separate outgoing/recovery channels avoid coherent counterwave interference.
The result omits return-field volume and transverse closure and is a bound.
"""
    if not 0 < drift_fraction < 1 or np.any(np.asarray(wave_rest_energy) < 0):
        raise ValueError('positive subluminal drift and nonnegative wave energy required')
    return .5*(drift_fraction**-2-1)*np.asarray(wave_rest_energy)


def reflection_guide_multiplier(amplitude_reflection, drift_fraction):
    """Worst coherent reflected phase, per incident wave's energy.

E_max=(1+|r|) sqrt(u_inc), B_trans,min=(1-|r|) sqrt(u_inc).
The bound enforces magnetic insulation with a specified drift margin.
"""
    if not 0 <= amplitude_reflection <= 1 or not 0 < drift_fraction < 1:
        raise ValueError('reflection in [0,1] and drift in (0,1) required')
    r = amplitude_reflection
    return .5*((1+r)**2/drift_fraction**2-(1-r)**2)
