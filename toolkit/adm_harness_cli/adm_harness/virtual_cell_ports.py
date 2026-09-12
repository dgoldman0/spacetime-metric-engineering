"""Port observables for the driven cells' explicit photon subledger.

These observables exclude the assigned counterstream, connector, and material
attachments. A signed radial component is expressed in the common material
tetrad; its sphere integral is not a Cartesian momentum of the whole rail.
"""
from __future__ import annotations

import numpy as np


def port_flux_from_rest(density, radius, lapse):
    """Local photon energy crossing a fixed material port per coordinate time."""
    return 4*np.pi*np.asarray(radius)**2*np.asarray(lapse)*np.asarray(density)


def beam_port_moments(incident, useful, heat):
    """Return signed energy supply and radial reaction, with left/right last.

    Positive supply enters the cells. Positive reaction points toward increasing
    x. Incoming and recovered photons give the same recoil on a given arm.
    """
    incident, useful, heat = map(np.asarray, (incident, useful, heat))
    if incident.shape != useful.shape or incident.shape != heat.shape or incident.shape[-1] != 2:
        raise ValueError('matching left/right beam arrays required')
    gross = incident+useful+heat
    reaction_by_side = gross*np.array([1., -1.])
    return incident-useful-heat, reaction_by_side


def counterstream_moments(absorption, useful, heat, direction):
    """Minimum positive radial null tensor cancelling the beam current.

    Returns rho, p_r, j, p_t in the material frame. This algebraic completion
    supplies no transport, conversion, or attachment equation.
    """
    current = np.asarray(direction)*(np.asarray(absorption)-np.asarray(useful)-np.asarray(heat))
    density = abs(current)
    return np.array([density, density, -current, np.zeros_like(density)])


def phase_port_traction(amplitude_left, amplitude_right):
    """Integrated core traction on the central interface, toward increasing x.

    The core has p_r=-A/R²; area times (p_left-p_right) is 4π(A_right-A_left).
    Material attachment and interface inertia are separate obligations.
    """
    return 4*np.pi*(np.asarray(amplitude_right)-np.asarray(amplitude_left))


def _rhs(state, faces, gain, source, dx):
    slope = np.zeros_like(state)
    a, b = state[1:-1]-state[:-2], state[2:]-state[1:-1]
    slope[1:-1] = np.where(a*b > 0, np.sign(a)*np.minimum(abs(a), abs(b)), 0.)
    left, right = np.r_[0., state+.5*slope], np.r_[state-.5*slope, 0.]
    flux = faces*np.where(faces >= 0, left, right)
    derivative = -(flux[1:]-flux[:-1])/dx+gain*state+source
    return derivative, np.array([flux[0]-flux[-1], dx*np.sum(gain*state), dx*np.sum(source)]), flux


def instrumented_propagate(times, edges, coefficients, port_geometry, *,
                           port_face, backwards=False, substeps=None, cfl=.35):
    """Independently replay SSP RK2 and integrate a material-frame port at stages.

    State is the ADM volume density b R² mu. ``port_geometry(t)`` returns
    (gamma*(1-sign*v), material lapse). Boundary states use the same one-sided
    constant reconstruction as the accepted wave replay. ``substeps`` lets all
    six streams share corrected-step observation times. Port energy is always
    positive crossing traffic; the ADM balance uses increasing physical time,
    including for the least-prepared backward absorption construction.
    """
    times, edges = np.asarray(times), np.asarray(edges)
    n, nt = len(edges)-1, len(times)
    if n < 1 or nt < 2 or np.any(np.diff(times) <= 0) or not np.allclose(np.diff(edges), np.diff(edges)[0]):
        raise ValueError('increasing times and uniform positive cells required')
    dx = edges[1]-edges[0]
    if dx <= 0 or port_face not in (0, -1) or not 0 < cfl <= .4:
        raise ValueError('positive spacing, boundary port and valid CFL required')
    if substeps is None:
        substeps = []
        for i, dt in enumerate(np.diff(times)):
            samples = [coefficients(float(t), i) for t in (times[i], (times[i]+times[i+1])/2, times[i+1])]
            speed = max(abs(c[0]).max() for c in samples)
            rate = max(abs(c[1]).max() for c in samples)
            substeps.append(max(1, int(np.ceil(dt*(speed/dx+rate)/cfl))))
    substeps = np.asarray(substeps, dtype=int)
    if substeps.shape != (nt-1,) or np.any(substeps < 1):
        raise ValueError('positive step count per interval required')
    offsets = np.r_[0, np.cumsum(substeps)]
    observation_time = np.r_[np.concatenate([times[i]+np.arange(count)*
        (times[i+1]-times[i])/count for i,count in enumerate(substeps)]), times[-1]]
    coordinate_power = np.zeros(len(observation_time)); proper_power = np.zeros_like(coordinate_power)
    history = np.zeros((nt,n)); ledger = np.zeros((nt-1,6)); port_energy = np.zeros(nt-1)
    state = np.zeros(n); sign = -1 if backwards else 1

    def observe(at, interval, y):
        t = observation_time[at]
        faces, gain, source = coefficients(float(t), interval)
        boost, lapse = port_geometry(float(t))
        boundary = y[0] if port_face == 0 else y[-1]
        coordinate_power[at] = 4*np.pi*abs(faces[port_face])*boundary*boost
        proper_power[at] = coordinate_power[at]/lapse

    observe(len(observation_time)-1 if backwards else 0, nt-2 if backwards else 0, state)
    for i in (range(nt-2,-1,-1) if backwards else range(nt-1)):
        before = dx*state.sum(); accumulated = np.zeros(3); port = 0.
        indexes = range(offsets[i+1]-1,offsets[i]-1,-1) if backwards else range(offsets[i],offsets[i+1])
        for k in indexes:
            lo, hi = observation_time[k], observation_time[k+1]
            start, end = (hi,lo) if backwards else (lo,hi); dt=hi-lo
            def stage(y, t):
                faces, gain, source = coefficients(float(t),i)
                derivative, terms, flux = _rhs(y,sign*faces,sign*gain,source,dx)
                boost, lapse = port_geometry(float(t))
                return derivative, terms, 4*np.pi*abs(flux[port_face])*boost
            k1, l1, p1 = stage(state,start)
            trial=state+dt*k1
            k2, l2, p2 = stage(trial,end)
            state=.5*(state+trial+dt*k2)
            if not np.isfinite(state).all() or state.min() < -1e-11:
                raise ArithmeticError('wave state lost positivity or finiteness')
            accumulated += .5*dt*(l1+l2); port += .5*dt*(p1+p2)
            observe(k if backwards else k+1,i,state)
        target=i if backwards else i+1; history[target]=state
        physical_change=sign*4*np.pi*(dx*state.sum()-before)
        boundary, geometric, source = sign*4*np.pi*accumulated
        ledger[i]=[boundary,geometric,source,physical_change,
                   physical_change-boundary-geometric-source,port]
        port_energy[i]=port
    return dict(state=history, ledger=ledger, port_energy=port_energy,
                port_time=observation_time, coordinate_power=coordinate_power,
                proper_power=proper_power, substeps=substeps)
