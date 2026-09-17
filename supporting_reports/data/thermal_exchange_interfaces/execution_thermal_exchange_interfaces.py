"""Paired thermal emission, finite frozen relays, and moving photon collectors.

Four-vectors use (energy, radial, tangential, axial) coordinates with c=1.
Emission powers are per emitter proper time in its material rest frame;
returned four-forces are per laboratory time. Frozen relay guides are
separate stationary hosts. Their impulses are retained explicitly.
"""
import numpy as np


def passive_absorption_gain(absorption, spin_floor=.3):
    """Maximum rest-heat power / |optical power| for a paired passive bath."""
    a, j = np.broadcast_arrays(np.asarray(absorption, float), np.asarray(spin_floor, float))
    if (not all(np.isfinite(x).all() for x in (a, j)) or np.any((a < 0) | (a >= 1))
            or np.any((j <= 0) | (j >= 1)) or np.any(2*j-a*(1+j) <= 0)):
        raise ValueError("positive extractable spin and subunit absorption required")
    return a/(2*j-a*(1+j))


def tangential_emission(rest_heat_power, signed_spin, radial_speed=0., *, direction_bias=0.):
    """Two tangential rest-frame streams with mean direction `direction_bias`.

    Bias zero gives equal proper-frame emission. Bias=-signed_spin instead
    produces equal radial-frame streams, with the corresponding recoil.
    Stream order is positive, negative tangential direction.
    """
    Q, w, v, m = np.broadcast_arrays(*map(lambda x: np.asarray(x, float),
        (rest_heat_power, signed_spin, radial_speed, direction_bias)))
    if (not all(np.isfinite(x).all() for x in (Q, w, v, m)) or np.any(Q < 0)
            or np.any(abs(w) >= 1) or np.any(abs(v) >= 1) or np.any(abs(m) > 1)):
        raise ValueError("nonnegative heat, subluminal motion, and physical direction bias required")
    direction = np.array([1., -1.]).reshape((2,)+(1,)*Q.ndim)
    proper = .5*Q*(1+direction*m)
    power = (1+direction*w)*proper
    streams = np.stack((power, v*power, direction*np.sqrt(1-v*v)*power,
                        np.zeros_like(power)), axis=1)
    return dict(rest_stream_power=proper, stream_four_force=streams,
        total_four_force=streams.sum(axis=0), proper_heat_power=Q)


def paired_absorption_exchange(power, spin, absorption, radial_speed=0.):
    """Optical absorption and passive thermal emission from equal opposed rotors.

    `power` is total optical power into the pair. Each rotor emits half the
    returned material-rest heat power. Subsequent spatial mixing belongs
    to a separate relay. Cold four-forces include emission momentum loss.
    """
    q, j, a, v = np.broadcast_arrays(*map(lambda x: np.asarray(x, float),
        (power, spin, absorption, radial_speed)))
    passive_absorption_gain(a, j)
    if not np.isfinite(q).all() or not np.isfinite(v).all() or np.any(abs(v) >= 1):
        raise ValueError("finite power and subluminal radial motion required")
    s = np.where(q < 0, -1., 1.)
    denominator = 2*j+s*a*(1-s*j)
    incoming = abs(q)*(1+s*j)/denominator
    outgoing = (1-a)*(1-s*j)/(1+s*j)*incoming
    impulse = s*(incoming+outgoing)
    Q = a*abs(q)/denominator
    directed_heat = (1-j*j)*Q
    sigma = np.array([1., -1.]).reshape((2,)+(1,)*q.ndim)
    signs = np.broadcast_to(sigma, (2,)+q.shape)
    optical = np.stack((np.broadcast_to(q/2, signs.shape),
        np.broadcast_to(v*q/2, signs.shape), signs*impulse*np.sqrt(1-v*v)/2,
        np.zeros_like(signs)), axis=1)
    emission = tangential_emission(Q/2, signs*j, v)
    # tangential_emission's leading index is ray direction; put rotor first.
    emitted_streams = np.swapaxes(emission["stream_four_force"], 0, 2)
    emitted_streams = np.swapaxes(emitted_streams, 1, 2)
    emitted = emitted_streams.sum(axis=1)
    return dict(incoming=incoming, outgoing=outgoing, signed_optical_impulse=impulse,
        material_rest_heat_power=Q, directed_zero_J_heat_power=directed_heat,
        optical_four_force=optical, emitted_stream_four_force=emitted_streams,
        emitted_four_force=emitted, cold_four_force=optical-emitted,
        paired_bath_four_force=emitted.sum(axis=0),
        cold_signed_impulse=impulse-j*Q)


def radial_collector(incident_energy, radial_speed, incoming_direction, outgoing_sign=1.):
    """Elastic redirection by a guide moving radially at speed u.

    The outgoing ray has radial cosine u and tangential cosine
    sign*sqrt(1-u^2). Guide recoil obeys delta E=u*delta p_radial.
    This is an instantaneous port law; it supplies no moving path geometry.
    """
    direction = np.asarray(incoming_direction, float)
    if direction.shape[0] != 3:
        raise ValueError("three incoming direction components required")
    E, u, sign, nr, nt, nz = np.broadcast_arrays(*map(lambda x: np.asarray(x, float),
        (incident_energy, radial_speed, outgoing_sign, *direction)))
    if (not all(np.isfinite(x).all() for x in (E, u, sign, nr, nt, nz))
            or np.any(E < 0) or np.any(abs(u) >= 1) or np.any(abs(sign) != 1)
            or not np.allclose(nr*nr+nt*nt+nz*nz, 1., rtol=0., atol=2e-12)):
        raise ValueError("nonnegative energy, physical rays and subluminal guide speed required")
    ratio = (1-u*nr)/(1-u*u)
    outgoing = E*ratio
    before = np.stack((E, E*nr, E*nt, E*nz))
    after = np.stack((outgoing, outgoing*u, outgoing*sign*np.sqrt(1-u*u), np.zeros_like(E)))
    recoil = before-after
    return dict(energy_ratio=ratio, incoming_four_momentum=before,
        outgoing_four_momentum=after, guide_recoil_four_momentum=recoil,
        mechanical_work_to_photon=outgoing-E,
        rest_frame_work_error=recoil[0]-u*recoil[1])


def _linear_pulse(time, values, query):
    """Value and exact primitive of a zero-extended piecewise linear pulse."""
    shape = values.shape[:-1]
    rows = values.reshape((-1, len(time)))
    slopes = np.diff(rows)/np.diff(time)
    prefix = np.concatenate((np.zeros((len(rows), 1)),
        np.cumsum(.5*(rows[:, 1:]+rows[:, :-1])*np.diff(time), axis=1)), axis=1)
    t = np.clip(query, time[0], time[-1])
    panel = np.clip(np.searchsorted(time, t, side="right")-1, 0, len(time)-2)
    offset = t-time[panel]
    value = rows[:, panel]+slopes[:, panel]*offset
    value[:, (query < time[0]) | (query > time[-1])] = 0.
    integral = prefix[:, panel]+rows[:, panel]*offset+.5*slopes[:, panel]*offset**2
    return value.reshape(shape+query.shape), integral.reshape(shape+query.shape)


def matched_axial_relay(time, rest_heat_per_rotor, spin, delay):
    """Finite matched 50:50 thermal routing in a frozen local inertial frame.

    Rotors/baths lie at z=+/-delay/2. Tangential source rays turn toward a
    central mixer, which sends half of each input to each destination.
    Separate channels preserve the eventual tangential ray direction.
    Source and destination turns use stationary nonrotating guide hosts.
    Every route has flight time `delay`; pulses are linear between samples.
    Returned guide forces and the axial photon tensor require their own
    physical hosts. Their dynamic embedding is outside this frozen replay.
    """
    t, Q, j = map(lambda x: np.asarray(x, float), (time, rest_heat_per_rotor, spin))
    if (t.ndim != 1 or len(t) < 3 or Q.shape != t.shape or j.shape != t.shape
            or not all(np.isfinite(x).all() for x in (t, Q, j))
            or np.any(np.diff(t) <= 0) or np.any(Q < 0) or np.any((j < 0) | (j >= 1))
            or Q[0] != 0 or Q[-1] != 0 or not np.isfinite(delay) or delay <= 0):
        raise ValueError("ordered finite pulse, subluminal spin and positive delay required")
    sigma = np.array([1., -1.])[:, None, None]
    direction = np.array([1., -1.])[None, :, None]
    source = .5*Q*(1+sigma*direction*j)
    now, I0 = _linear_pulse(t, source, t)
    middle, Ihalf = _linear_pulse(t, source, t-delay/2)
    arrived_source, Ifull = _linear_pulse(t, source, t-delay)
    arrival = np.broadcast_to(.5*arrived_source.sum(axis=0), source.shape).copy()
    entering = now-middle
    leaving = np.broadcast_to(.5*(middle-arrived_source).sum(axis=0), source.shape).copy()
    Ein = I0-Ihalf
    Eout = np.broadcast_to(.5*(Ihalf-Ifull).sum(axis=0), source.shape).copy()
    axial_in = np.stack((np.ones(2), np.zeros(2), np.zeros(2), -sigma[:, 0, 0]), axis=1)
    axial_out = axial_in.copy(); axial_out[:, 3] *= -1
    tensor = (np.einsum("isn,ia,ib->sabn", Ein, axial_in, axial_in)
              +np.einsum("isn,ia,ib->sabn", Eout, axial_out, axial_out))
    flight_rate = (np.einsum("isn,ia->san", entering, axial_in)
                   +np.einsum("isn,ia->san", leaving, axial_out))
    source_guides = np.zeros((2, 2, 4, len(t)))
    source_guides[:, :, 2] = direction*now
    source_guides[:, :, 3] = sigma*now
    central_guides = np.zeros((2, 4, len(t)))
    central_guides[:, 3] = -(sigma*middle).sum(axis=0)
    destination_guides = np.zeros_like(source_guides)
    destination_guides[:, :, 2] = -direction*arrival
    destination_guides[:, :, 3] = sigma*arrival
    source_flux, bath_flux = np.zeros((2, 4, len(t))), np.zeros((2, 4, len(t)))
    source_flux[:, 0], bath_flux[:, 0] = now.sum(axis=0), arrival.sum(axis=0)
    source_flux[:, 2] = direction[0]*source_flux[:, 0]
    bath_flux[:, 2] = direction[0]*bath_flux[:, 0]
    guide_force = source_guides.sum(axis=0)+central_guides+destination_guides.sum(axis=0)
    balance = source_flux-bath_flux-guide_force-flight_rate
    return dict(time=t, source_stream_power=now, bath_arrival_stream_power=arrival,
        inbound_photon_energy=Ein, outbound_photon_energy=Eout,
        flight_tensor_per_direction=tensor, flight_tensor=tensor.sum(axis=0),
        flight_four_momentum_rate_per_direction=flight_rate,
        source_guide_four_force=source_guides, central_guide_four_force=central_guides,
        destination_guide_four_force=destination_guides,
        four_momentum_balance_error=balance,
        source_total_power=now.sum(axis=(0, 1)), bath_total_power=arrival.sum(axis=(0, 1)),
        flight_energy=tensor[:, 0, 0].sum(axis=0),
        flight_energy_rate=flight_rate[:, 0].sum(axis=0))


def three_axis_average(tensor):
    """Equal rotated copies, preserving total energy and exposing mean stress."""
    value = np.asarray(tensor, float)
    if value.shape[:2] != (4, 4) or not np.isfinite(value).all():
        raise ValueError("finite four-dimensional tensor required")
    permutations = ((0, 1, 2, 3), (0, 2, 3, 1), (0, 3, 1, 2))
    return sum(value[list(p)][:, list(p)] for p in permutations)/3
