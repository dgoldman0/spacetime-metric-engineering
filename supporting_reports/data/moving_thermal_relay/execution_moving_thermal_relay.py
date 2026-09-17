"""Retarded thermal routing between equal radially moving annular ports.

Two source/bath rings at z=+/-L and a distinct mixer ring at z=0 share
R(t). Guides move radially, with zero angular velocity. Photon directions
are aimed at the prescribed future endpoint, so delays vary with R(t).
Four-vector coordinates are (energy, radial, tangential, axial), c=1.
Guide forces are photon recoil per lab time; external drives supply the
opposite force, plus the separately assigned guide inertia.
"""
from dataclasses import dataclass

import numpy as np
from scipy.interpolate import CubicHermiteSpline

from .thermal_exchange_interfaces import passive_absorption_gain


@dataclass
class RadialTrajectory:
    """Cubic Hermite radius with a checked speed bound on every panel.

    Linear endpoint continuations preserve the endpoint speed. The finite
    query interval must retain positive radius; zero endpoint speeds give
    stationary continuations. Polynomial extrema check each full panel.
    """
    time: np.ndarray
    radius: np.ndarray
    speed: np.ndarray
    speed_ceiling: float = .00905

    def __post_init__(self):
        self.time, self.radius, self.speed = [np.asarray(v, float) for v in
                                             (self.time, self.radius, self.speed)]
        if (self.time.ndim != 1 or len(self.time) < 2
                or self.radius.shape != self.time.shape or self.speed.shape != self.time.shape
                or not all(np.isfinite(v).all() for v in (self.time, self.radius, self.speed))
                or np.any(np.diff(self.time) <= 0) or np.any(self.radius <= 0)
                or not np.isfinite(self.speed_ceiling) or not 0 <= self.speed_ceiling < 1):
            raise ValueError("ordered finite radii/speeds and a subluminal ceiling required")
        self._curve = CubicHermiteSpline(self.time, self.radius, self.speed, extrapolate=False)
        self._velocity = self._curve.derivative()
        speed_extrema = list(abs(self.speed))
        radius_extrema = list(self.radius)
        for index, length in enumerate(np.diff(self.time)):
            c3, c2, c1, _ = self._curve.c[:, index]
            if c3 != 0:
                critical = -c2/(3*c3)
                if 0 < critical < length:
                    speed_extrema.append(abs(float(self._velocity(self.time[index]+critical))))
            roots = np.roots([3*c3, 2*c2, c1]) if c3 != 0 else (
                np.roots([2*c2, c1]) if c2 != 0 else [])
            for critical in roots:
                if abs(np.imag(critical)) < 1e-13 and 0 < float(np.real(critical)) < length:
                    radius_extrema.append(float(self._curve(self.time[index]+float(np.real(critical)))))
        self.maximum_speed = max(speed_extrema)
        self.minimum_radius = min(radius_extrema)
        self.maximum_radius = max(radius_extrema)
        if self.maximum_speed > self.speed_ceiling*(1+2e-12)+1e-16 or self.minimum_radius <= 0:
            raise ValueError("interpolated trajectory exceeds its speed or radius domain")

    def state(self, query):
        t = np.asarray(query, float)
        if not np.isfinite(t).all():
            raise ValueError("finite trajectory query required")
        radius, speed = self._curve(t), self._velocity(t)
        for index, mask in ((0, t < self.time[0]), (-1, t > self.time[-1])):
            radius = np.where(mask, self.radius[index]+self.speed[index]*(t-self.time[index]), radius)
            speed = np.where(mask, self.speed[index], speed)
        if np.any(radius <= 0):
            raise ValueError("trajectory continuation has nonpositive radius")
        return radius, speed


def null_leg(time, motion, axial_distance, *, arrival_given=False):
    """Solve one exact null chord and its time-of-arrival Jacobian.

    J=dt_arrival/dt_emission=(1-n_r*v_emission)/(1-n_r*v_arrival).
    The contraction bound confines the positive delay to [L,gamma_max L].
    """
    t = np.asarray(time, float)
    L = float(axial_distance)
    if not np.isfinite(t).all() or not np.isfinite(L) or L <= 0:
        raise ValueError("finite times and positive axial distance required")
    gamma = 1/np.sqrt(1-motion.speed_ceiling**2)
    low, high = np.full(t.shape, L), np.full(t.shape, L*gamma*(1+8e-15))
    fixed_radius = motion.state(t)[0]
    sign = -1. if arrival_given else 1.
    for _ in range(48):
        delay = .5*(low+high)
        other_radius = motion.state(t+sign*delay)[0]
        residual = delay-np.hypot(other_radius-fixed_radius, L)
        low = np.where(residual < 0, delay, low)
        high = np.where(residual >= 0, delay, high)
    delay = .5*(low+high)
    departure, arrival = (t-delay, t) if arrival_given else (t, t+delay)
    r0, v0 = motion.state(departure)
    r1, v1 = motion.state(arrival)
    length = np.hypot(r1-r0, L)
    nr, nz = (r1-r0)/length, L/length
    return dict(departure=departure, arrival=arrival, delay=arrival-departure,
        radial_cosine=nr, axial_cosine=nz, departure_speed=v0, arrival_speed=v1,
        arrival_jacobian=(1-nr*v0)/(1-nr*v1), null_error=arrival-departure-length)


def elastic_redirect(power, incoming_direction, outgoing_direction, radial_speed):
    """Elastic guide scattering, including lab-time recoil and work.

    Directions have leading spatial-component index. Power and velocity
    share arbitrary broadcastable sample axes. Recoil four-force has its
    four-component index immediately before the final sample axis.
    """
    incoming, outgoing = np.asarray(incoming_direction, float), np.asarray(outgoing_direction, float)
    if incoming.shape[0] != 3 or outgoing.shape[0] != 3:
        raise ValueError("three direction components required")
    P, u, *d = np.broadcast_arrays(np.atleast_1d(np.asarray(power, float)), np.asarray(radial_speed, float),
                                   *incoming, *outgoing)
    if (not all(np.isfinite(v).all() for v in (P, u, *d)) or np.any(P < 0)
            or np.any(abs(u) >= 1)
            or not np.allclose(sum(v*v for v in d[:3]), 1., rtol=0., atol=2e-12)
            or not np.allclose(sum(v*v for v in d[3:]), 1., rtol=0., atol=2e-12)):
        raise ValueError("physical photon directions, powers and guide speeds required")
    ratio = (1-u*d[0])/(1-u*d[3])
    before, after = _ray(P, *d[:3]), _ray(P*ratio, *d[3:])
    recoil = before-after
    return dict(energy_ratio=ratio, incoming_four_force=before, outgoing_four_force=after,
        guide_four_force=recoil, work_to_photons=P*(ratio-1),
        work_orthogonality_error=recoil[..., 0, :]-u*recoil[..., 1, :])


def _ray(power, nr, nt, nz):
    return np.stack(np.broadcast_arrays(power, power*nr, power*nt, power*nz), axis=-2)


def _tensor(power, nr, nz):
    directions = _ray(np.ones_like(power), nr, 0., nz)
    return np.einsum("sen,sean,sebn->abn", power, directions, directions)


def annular_axis_ensemble(pair_tensor):
    """Integrate each annulus in azimuth, then sum three equal axis pairs.

    The input is one pair's integrated tensor in a local cylindrical basis.
    Axisymmetric annular integration cancels radial/tangential vectors and
    distributes the in-plane diagonal stress equally between two lab axes.
    Three pairs contain six rotors and carry three times the pair energy.
    """
    value = np.asarray(pair_tensor, float)
    if value.shape[:2] != (4, 4) or not np.isfinite(value).all():
        raise ValueError("finite local four-tensor required")
    annulus = np.zeros_like(value)
    annulus[0, 0] = value[0, 0]
    annulus[1, 1] = annulus[2, 2] = .5*(value[1, 1]+value[2, 2])
    annulus[3, 3] = value[3, 3]
    annulus[0, 3], annulus[3, 0] = value[0, 3], value[3, 0]
    permutations = ((0, 1, 2, 3), (0, 2, 3, 1), (0, 3, 1, 2))
    return sum(annulus[list(p)][:, list(p)] for p in permutations)


def relay_bounds(maximum_speed=.00905, axial_half_separation=1/128):
    """Uniform bounds relative to total emitted power/energy of one pair."""
    v, L = float(maximum_speed), float(axial_half_separation)
    if not np.isfinite([v, L]).all() or not 0 <= v < 1 or L <= 0:
        raise ValueError("subluminal speed and positive half separation required")
    epsilon = v*v
    delta = 2*epsilon/(1-epsilon)
    ratio = 1+delta
    gamma = 1/np.sqrt(1-epsilon)
    return dict(maximum_radial_speed=v, axial_half_separation=L,
        maximum_single_leg_delay=gamma*L, maximum_total_delay=2*gamma*L,
        minimum_total_delay=2*L, single_turn_energy_factor=ratio,
        single_leg_arrival_jacobian_upper=ratio,
        total_guide_work_l1_per_emitted_energy=delta*(1+ratio+ratio**2),
        guide_work_peak_per_emitted_power=delta*(1+ratio**2+ratio**4),
        bath_energy_per_emitted_energy=ratio**3,
        bath_power_per_emitted_peak=ratio**5,
        flight_energy_per_emitted_peak=gamma*L*(ratio+ratio**3),
        flight_rate_l1_per_emitted_energy=2*ratio**2,
        flight_rate_peak_per_emitted_peak=ratio**4+delta*ratio**2,
        radial_guide_force_peak_per_emitted_power=2*v/(1-epsilon)*(1+ratio**2+ratio**4),
        radial_guide_impulse_l1_per_emitted_energy=2*v/(1-epsilon)*(1+ratio+ratio**2),
        guide_impulse_l1_per_emitted_energy=(1+ratio)*(1+ratio+ratio**2))


def selected_route_bounds(maximum_actuator_gap, *, maximum_speed=.00905,
                           axial_half_separation=1/128):
    """Combined thermal and selected radial-actuator photon ceilings.

    All coefficients multiply emitted heat peak or its time integral.
    P_remote integrates to guide work after both work leads empty, while
    its absolute integral is bounded by the actuator encounter exposure.
    W_total_dot=Qe-Qa+P_remote includes both finite photon inventories.
    """
    gap = float(maximum_actuator_gap)
    if not np.isfinite(gap) or gap <= 0:
        raise ValueError("positive actuator gap ceiling required")
    b = relay_bounds(maximum_speed, axial_half_separation)
    v, r = maximum_speed, b["single_turn_energy_factor"]
    remote_peak = .5*(1+v)/(1-v)*b["radial_guide_force_peak_per_emitted_power"]
    remote_l1 = b["radial_guide_impulse_l1_per_emitted_energy"]
    actuator_energy = gap*(1+v)*b["radial_guide_force_peak_per_emitted_power"]
    return dict(**b, maximum_actuator_gap=gap,
        remote_power_peak_per_emitted_peak=remote_peak,
        remote_power_l1_per_emitted_energy=remote_l1,
        actuator_energy_per_emitted_peak=actuator_energy,
        complete_flight_energy_per_emitted_peak=b["flight_energy_per_emitted_peak"]+actuator_energy,
        complete_flight_rate_peak_per_emitted_peak=r**5+remote_peak,
        complete_flight_rate_l1_per_emitted_energy=1+r**3+remote_l1)


def reaction_work_allowance(optical_power_peak, *, absorption=.62e-6, spin_floor=.3,
                            maximum_speed=.00905, inverse_l1=2.638292563,
                            maximum_actuator_gap=None):
    """Incremental reversible work demand on existing bidirectional ports.

    This excludes guide kinetic inventory, actuator losses and changes to
    the parent nonlinear history. The reaction-line inverse maps bounded
    additional load G to |delta a|<=inverse_l1*||G||_infinity. Each emitted
    half-channel therefore needs half that additional positive margin.
    """
    peak, norm = float(optical_power_peak), float(inverse_l1)
    if not np.isfinite([peak, norm]).all() or peak < 0 or norm < 1:
        raise ValueError("nonnegative optical peak and an inverse norm at least one required")
    bounds = relay_bounds(maximum_speed)
    kappa = float(passive_absorption_gain(absorption, spin_floor))
    work = bounds["guide_work_peak_per_emitted_power"]*kappa*peak
    force = bounds["radial_guide_force_peak_per_emitted_power"]*kappa*peak
    remote = .5*(1+maximum_speed)/(1-maximum_speed)*force
    result = dict(optical_power_peak=peak, passive_heat_gain=kappa,
        maximum_additional_guide_work=work,
        maximum_additional_inverse_command=norm*work,
        required_additional_emitted_half_channel_margin=.5*norm*work,
        rotor_seed_power_allowance=(1+spin_floor)/(2*spin_floor)*work,
        guide_work_l1_per_optical_l1=bounds["total_guide_work_l1_per_emitted_energy"]*kappa,
        maximum_summed_radial_guide_force=force,
        finite_reflector_remote_net_power_peak=remote,
        finite_reflector_inverse_command_peak=norm*remote,
        finite_reflector_half_channel_margin=.5*norm*remote,
        added_reflector_exposure_l1_per_optical_l1=bounds["radial_guide_impulse_l1_per_emitted_energy"]*kappa)
    if maximum_actuator_gap is not None:
        gap = float(maximum_actuator_gap)
        if not np.isfinite(gap) or gap <= 0:
            raise ValueError("positive finite actuator gap required")
        result["actuator_photon_energy_ceiling"] = gap*(1+maximum_speed)*force
    return result


def radial_work_reflector(force, radial_speed):
    """Signed radial force supplied by one of two opposed optical ports.

    Incoming and outgoing powers cross the moving actuator facet per lab
    time. Their difference is F*u; their sum is |F|. Finite lead inventory
    and remote retarded powers belong to a separate propagation ledger.
    """
    F, u = np.broadcast_arrays(np.asarray(force, float), np.asarray(radial_speed, float))
    if not np.isfinite([F, u]).all() or np.any(abs(u) >= 1):
        raise ValueError("finite forces and subluminal speeds required")
    sign = np.where(F < 0, -1., 1.)
    incoming = .5*abs(F)*(1+sign*u)
    outgoing = .5*abs(F)*(1-sign*u)
    return dict(incoming=incoming, outgoing=outgoing, direction=sign,
        encountered_power=incoming+outgoing, mechanical_power=incoming-outgoing,
        force_error=sign*(incoming+outgoing)-F,
        work_error=incoming-outgoing-u*F)


def opposed_capacitor_drive(force, force_rate, radial_offset, radial_speed, *,
                            half_gap, bias_force, epsilon_area=1.):
    """Optional fixed-area planar drive, with its variable field inventory.

    Two distinct return electrodes have gaps g0-/+offset and attractive
    forces Fb+/-F/2. Electrical input equals dU/dt+F*u. The guide's radial
    motion and the fixed-area assumption are explicit local port inputs.
    This supplies no bandwidth bound from a speed bound alone.
    """
    F, Fdot, d, u = np.broadcast_arrays(*map(lambda a: np.asarray(a, float),
                                           (force, force_rate, radial_offset, radial_speed)))
    gap0, bias, area = map(float, (half_gap, bias_force, epsilon_area))
    if (not all(np.isfinite(v).all() for v in (F, Fdot, d, u)) or np.any(abs(u) >= 1)
            or not np.isfinite([gap0, bias, area]).all() or min(gap0, bias, area) <= 0
            or np.any(abs(d) >= gap0) or np.any(abs(F) >= 2*bias)):
        raise ValueError("positive capacitor gaps, loaded faces and subluminal motion required")
    sign = np.array([1., -1.]).reshape((2,)+(1,)*F.ndim)
    forces, rates, gaps = bias+sign*F/2, sign*Fdot/2, gap0-sign*d
    charge = np.sqrt(2*area*forces)
    charge_rate = area*rates/charge
    voltage = charge*gaps/area
    electrical = (voltage*charge_rate).sum(axis=0)
    energy = (forces*gaps).sum(axis=0)
    energy_rate = (rates*gaps-sign*forces*u).sum(axis=0)
    return dict(gap=gaps, attractive_force=forces, charge=charge,
        charge_rate=charge_rate, voltage=voltage, field_energy=energy,
        field_energy_rate=energy_rate, electrical_power=electrical,
        mechanical_power=F*u, energy_balance_error=electrical-energy_rate-F*u)


def _integrate_panels(function, lower, upper, breakpoints, order):
    """Gauss integration with each prescribed pulse/trajectory knot retained."""
    edges = np.asarray(breakpoints, float)
    starts, stops, owners = [], [], []
    for index, (lo, hi) in enumerate(zip(lower, upper)):
        inside = edges[np.searchsorted(edges, lo, side="right"):np.searchsorted(edges, hi)]
        cuts = np.r_[lo, inside, hi]
        starts.extend(cuts[:-1]); stops.extend(cuts[1:]); owners.extend([index]*(len(cuts)-1))
    starts, stops, owners = np.asarray(starts), np.asarray(stops), np.asarray(owners)
    nodes, weights = np.polynomial.legendre.leggauss(order)
    half = .5*(stops-starts)
    query = .5*(stops+starts)[:, None]+half[:, None]*nodes
    value = function(query.ravel())
    shape = value.shape[:-1]
    values = value.reshape((-1, len(starts), order))
    panels = np.einsum("apn,n,p->ap", values, weights, half)
    result = np.zeros((len(panels), len(lower)))
    for index in range(len(panels)):
        np.add.at(result[index], owners, panels[index])
    return result.reshape(shape+(len(lower),))


def radial_work_lead(time, force, motion, *, reference_radius, half_gap,
                     observation_time=None, quadrature_order=8,
                     force_function=None, additional_breakpoints=()):
    """Two fixed radial optical ports drive the moving guide by reflection.

    At the facet, side s has gap g_s=g0+s*(R-Rref), incoming direction s
    and reflected direction -s. Its remote emission and return times are
    t_e=t-g_s(t), t_r=t+g_s(t). Powers include both exact clock Jacobians.
    A supplied force function, or the default linear interpolation, gives
    a concrete feedforward actuator command.
    Remote net power equals guide work plus actuator-photon inventory rate.
    """
    t, F = np.asarray(time, float), np.asarray(force, float)
    obs = t if observation_time is None else np.asarray(observation_time, float)
    reference, gap0 = float(reference_radius), float(half_gap)
    if (t.ndim != 1 or len(t) < 3 or F.shape != t.shape or obs.ndim != 1
            or not all(np.isfinite(v).all() for v in (t, F, obs)) or np.any(np.diff(t) <= 0)
            or F[0] != 0 or F[-1] != 0 or not np.isfinite([reference, gap0]).all()
            or min(reference, gap0) <= 0):
        raise ValueError("finite zero-ended force and positive radial lead geometry required")
    offset = max(abs(motion.minimum_radius-reference), abs(motion.maximum_radius-reference))
    if gap0 <= offset:
        raise ValueError("stationary radial ports must enclose the complete motion")
    gap_min, gap_max = gap0-offset, gap0+offset

    def side_state(query, sign):
        radius, velocity = motion.state(query)
        gap = gap0+sign*(radius-reference)
        if np.any(gap <= 0) or np.any(gap > gap_max*(1+1e-11)):
            raise ValueError("queried continuation leaves the fixed radial ports")
        command = (np.interp(query, t, F, left=0., right=0.) if force_function is None
                   else np.asarray(force_function(query), float))
        if command.shape != query.shape or not np.isfinite(command).all():
            raise ValueError("force function must match the finite query axis")
        load = np.maximum(sign*command, 0.)
        return gap, velocity, .5*load*(1+sign*velocity), .5*load*(1-sign*velocity)

    def event(query, sign, future):
        lo, hi = np.full(query.shape, gap_min), np.full(query.shape, gap_max)
        for _ in range(48):
            delay = .5*(lo+hi)
            target = query+delay if future else query-delay
            gap = gap0+sign*(motion.state(target)[0]-reference)
            residual = delay-gap
            lo = np.where(residual < 0, delay, lo)
            hi = np.where(residual >= 0, delay, hi)
        delay = .5*(lo+hi)
        return query+delay if future else query-delay

    zeros = []
    for index in np.flatnonzero(F[:-1]*F[1:] < 0):
        zeros.append(t[index]-F[index]*(t[index+1]-t[index])/(F[index+1]-F[index]))
    breaks = np.unique(np.r_[t, motion.time, zeros, additional_breakpoints])
    outputs = []
    for sign in (1., -1.):
        future, past = event(obs, sign, True), event(obs, sign, False)
        _, ua, pina, _ = side_state(future, sign)
        _, ub, _, poutb = side_state(past, sign)
        gap, u, pin, pout = side_state(obs, sign)
        emitted, returned = pina/(1-sign*ua), poutb/(1+sign*ub)
        inbound = _integrate_panels(lambda q: side_state(q, sign)[2], obs, future, breaks, quadrature_order)
        outbound = _integrate_panels(lambda q: side_state(q, sign)[3], past, obs, breaks, quadrature_order)
        outputs.append(dict(future=future, past=past, emitted=emitted, returned=returned,
            pin=pin, pout=pout, inbound=inbound, outbound=outbound, gap=gap))
    collected = {key: np.stack([o[key] for o in outputs]) for key in outputs[0]}
    sign = np.array([1., -1.])[:, None]
    remote = (collected["emitted"]-collected["returned"]).sum(axis=0)
    work = (collected["pin"]-collected["pout"]).sum(axis=0)
    energy = (collected["inbound"]+collected["outbound"]).sum(axis=0)
    momentum = (sign*(collected["inbound"]-collected["outbound"])).sum(axis=0)
    energy_rate = (collected["emitted"]-collected["pin"]+collected["pout"]-collected["returned"]).sum(axis=0)
    momentum_rate = (sign*(collected["emitted"]-collected["pin"]-collected["pout"]+collected["returned"])).sum(axis=0)
    actual_force = (sign*(collected["pin"]+collected["pout"])).sum(axis=0)
    stationary_force = (-sign*(collected["emitted"]+collected["returned"])).sum(axis=0)
    return dict(time=obs, force=actual_force, radial_speed=motion.state(obs)[1],
        source_emitted_power=collected["emitted"], source_returned_power=collected["returned"],
        facet_incoming_power=collected["pin"], facet_outgoing_power=collected["pout"],
        remote_net_power=remote, mechanical_power=work, photon_energy=energy,
        photon_radial_momentum=momentum, photon_energy_rate=energy_rate,
        photon_radial_momentum_rate=momentum_rate, stationary_port_radial_force=stationary_force,
        energy_balance_error=remote-work-energy_rate,
        radial_momentum_balance_error=momentum_rate+actual_force+stationary_force,
        mechanical_work_error=work-actual_force*motion.state(obs)[1],
        future_facet_time=collected["future"], past_facet_time=collected["past"],
        current_gap=collected["gap"], gap_ceiling=gap_max)


def moving_paired_relay(time, rest_heat_per_rotor, spin, motion, *,
                        axial_half_separation=1/128, quadrature_order=8,
                        observation_time=None, include_drive_function=False):
    """Finite two-leg relay with exact moving events and retarded fluxes.

    Input powers (1+sigma*epsilon*j)*Q/2 are interpolated linearly and
    vanish outside the supplied pulse. There are two equal opposed rotors,
    two independent eventual tangent-direction channels and a 50:50 mixer.
    R(t) and all guide angles are prescribed feedforward trajectories.
    """
    t, Q, j = [np.asarray(v, float) for v in (time, rest_heat_per_rotor, spin)]
    obs = t if observation_time is None else np.asarray(observation_time, float)
    if (t.ndim != 1 or len(t) < 3 or Q.shape != t.shape or j.shape != t.shape
            or obs.ndim != 1 or not len(obs) or np.any(np.diff(t) <= 0)
            or not all(np.isfinite(v).all() for v in (t, Q, j, obs))
            or np.any(Q < 0) or np.any((j < 0) | (j >= 1)) or Q[0] != 0 or Q[-1] != 0
            or not isinstance(quadrature_order, int) or quadrature_order < 2):
        raise ValueError("ordered finite zero-ended heat pulses, spin and observation times required")
    L = float(axial_half_separation)
    bounds = relay_bounds(motion.speed_ceiling, L)
    sigma = np.array([1., -1.])[:, None, None]
    epsilon = np.array([1., -1.])[None, :, None]
    pulse = .5*Q*(1+sigma*epsilon*j)

    def source_power(query):
        return np.array([np.interp(query, t, row, left=0., right=0.)
                         for row in pulse.reshape(4, len(t))]).reshape(2, 2, -1)

    def source(query):
        leg = null_leg(query, motion, L)
        P = source_power(query)
        u, nr = leg["departure_speed"], leg["radial_cosine"]
        factor = (1-u*u)/(1-u*nr)
        return dict(leg=leg, raw=P, power=P*factor, factor=factor)

    def middle(query):
        previous = null_leg(query, motion, L, arrival_given=True)
        inbound = source(previous["departure"])
        pin = inbound["power"]/previous["arrival_jacobian"]
        onward = null_leg(query, motion, L)
        u = onward["departure_speed"]
        factor = (1-u*previous["radial_cosine"])/(1-u*onward["radial_cosine"])
        pout = np.broadcast_to(.5*pin.sum(axis=0)[None]*factor, pin.shape).copy()
        return dict(previous=previous, onward=onward, incoming=pin, outgoing=pout, factor=factor)

    now = source(obs)
    mid = middle(obs)
    last = null_leg(obs, motion, L, arrival_given=True)
    prior_mid = middle(last["departure"])
    pin_end = prior_mid["outgoing"]/last["arrival_jacobian"]
    u = last["arrival_speed"]
    destination_factor = (1-u*last["radial_cosine"])/(1-u*u)
    arrived = pin_end*destination_factor
    source_raw = _ray(now["raw"], u, epsilon*np.sqrt(1-u*u), 0.)
    source_out = _ray(now["power"], now["leg"]["radial_cosine"], 0.,
                      -sigma*now["leg"]["axial_cosine"])
    middle_in = _ray(mid["incoming"], mid["previous"]["radial_cosine"], 0.,
                    -sigma*mid["previous"]["axial_cosine"])
    middle_out = _ray(mid["outgoing"], mid["onward"]["radial_cosine"], 0.,
                     sigma*mid["onward"]["axial_cosine"])
    destination_in = _ray(pin_end, last["radial_cosine"], 0., sigma*last["axial_cosine"])
    destination_out = _ray(arrived, u, epsilon*np.sqrt(1-u*u), 0.)
    source_guide = source_raw-source_out
    central_guide = (middle_in-middle_out).sum(axis=0)
    destination_guide = destination_in-destination_out
    flight_rate = (source_out-middle_in+middle_out-destination_in).sum(axis=(0, 1))
    total_guide = source_guide.sum(axis=(0, 1))+central_guide.sum(axis=0)+destination_guide.sum(axis=(0, 1))
    balance = (source_raw-destination_out).sum(axis=(0, 1))-total_guide-flight_rate
    work = np.stack((-source_guide[:, :, 0].sum(axis=(0, 1)),
                     -central_guide[:, 0].sum(axis=0),
                     -destination_guide[:, :, 0].sum(axis=(0, 1))))

    def inbound_tensor(query):
        value = source(query)
        return _tensor(value["power"], value["leg"]["radial_cosine"],
                       -sigma*value["leg"]["axial_cosine"])

    def outbound_tensor(query):
        value = middle(query)
        return _tensor(value["outgoing"], value["onward"]["radial_cosine"],
                       sigma*value["onward"]["axial_cosine"])

    knots = np.unique(np.r_[t, motion.time])
    middle_knots = np.unique(np.r_[knots, null_leg(knots, motion, L)["arrival"]])
    inbound = _integrate_panels(inbound_tensor, last["departure"], obs, knots, quadrature_order)
    outbound = _integrate_panels(outbound_tensor, last["departure"], obs, middle_knots, quadrature_order)
    tensor = inbound+outbound
    earliest = prior_mid["previous"]["departure"]
    total_jacobian = prior_mid["previous"]["arrival_jacobian"]*last["arrival_jacobian"]
    emitted_power = now["raw"].sum(axis=(0, 1))
    arrival_power = arrived.sum(axis=(0, 1))
    result = dict(time=obs, source_stream_power=now["raw"], bath_arrival_stream_power=arrived,
        source_guide_four_force=source_guide, central_guide_four_force=central_guide,
        destination_guide_four_force=destination_guide, guide_work_by_stage=work,
        guide_work_to_photons=work.sum(axis=0), source_total_power=emitted_power,
        bath_total_power=arrival_power, inbound_flight_tensor=inbound,
        outbound_flight_tensor=outbound, flight_tensor=tensor, flight_energy=tensor[0, 0],
        flight_four_momentum_rate=flight_rate, flight_energy_rate=flight_rate[0],
        four_momentum_balance_error=balance,
        energy_balance_error=flight_rate[0]-emitted_power+arrival_power-work.sum(axis=0),
        source_guide_work_error=source_guide[:, :, 0]-u*source_guide[:, :, 1],
        central_guide_work_error=central_guide[:, 0]-u*central_guide[:, 1],
        destination_guide_work_error=destination_guide[:, :, 0]-u*destination_guide[:, :, 1],
        bath_matched_radial_momentum_error=destination_out[:, :, 1]-u*arrived,
        emission_time_for_current_arrival=earliest, total_arrival_jacobian=total_jacobian,
        total_retarded_delay=obs-earliest, single_leg_null_error=last["null_error"],
        incoming_radial_cosine=last["radial_cosine"], radial_speed=u,
        six_rotor_flight_tensor=annular_axis_ensemble(tensor), bounds=bounds)
    if include_drive_function:
        def drive(query):
            query = np.asarray(query, float)
            emitted, mixer = source(query), middle(query)
            ending = null_leg(query, motion, L, arrival_given=True)
            earlier = middle(ending["departure"])
            incoming = earlier["outgoing"]/ending["arrival_jacobian"]
            speed, nr = ending["arrival_speed"], ending["radial_cosine"]
            bath = incoming*(1-speed*nr)/(1-speed*speed)
            return np.stack(((emitted["power"]*emitted["leg"]["radial_cosine"]-emitted["raw"]*speed).sum(axis=(0, 1)),
                (mixer["outgoing"]*mixer["onward"]["radial_cosine"]
                  -mixer["incoming"]*mixer["previous"]["radial_cosine"]).sum(axis=(0, 1)),
                (bath*speed-incoming*nr).sum(axis=(0, 1))))
        result["radial_drive_function"] = drive
        arrival_knots = null_leg(knots, motion, L)["arrival"]
        result["radial_drive_breakpoints"] = np.unique(np.r_[knots, arrival_knots,
                                            null_leg(arrival_knots, motion, L)["arrival"]])
    return result
