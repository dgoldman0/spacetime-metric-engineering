"""Front elements that keep a carry faster than exterior light from trapping what it overtakes.

The compartment design carries its lapse structure at up to 2.1 times the exterior light speed. Ahead of the
packet its log-lapse falls from about 5.5 to zero, so the along-track light speed alpha passes through the carry
speed v inside that fall. The surface alpha = v moves with the pattern and gathers forward-moving light from both
sides: light ahead of it is slower than the pattern and gets overtaken, and light behind it outruns the pattern
and catches up. Matter at rest in the path ends on the same surface. Whatever gathers there gains energy at the
rate |d alpha/dz| of the fall for as long as the carry lasts, and the pattern releases it forward as it slows.

The two front elements here bound that gain for any carry length. Each adds a log-lapse term only where the shift
vanishes. There a pure lapse leaves a stress with zero energy and zero flux, Hawking-Ellis Type I for any profile.

- ForwardShelf holds the lapse at e^psi > v ahead of the pattern, out to a radius beyond the pattern's own lapse
  structure, so the local light speed ahead of the pattern exceeds the carry speed. The shelf fills in across the
  pattern's front fall and runs ahead to a leading edge. That edge moves faster than light inside the shelf, or
  the shelf is switched on along its whole length together with the pattern. The edge comes to rest at a terminal
  beyond the arrival.
- ConeFront raises the lapse inside a slender cone ahead of the pattern, peaked on the axis. At the cone's light
  surface the transverse lapse gradient exceeds the along-track gradient by the cotangent of the half-angle, so
  what the pattern overtakes slides off the cone within a bounded time. The cone extends while the carry speed
  rises through the exterior light speed and retracts as it falls back.

Both elements move with the pattern and follow its schedule. The helpers add a front's log-lapse jet to the
compartment fields, evaluate the demanded tensor with the transverse terms at every radius, and trace meridional
light rays and unit-mass particles through the result.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import expit

from . import axial_track as ax
from . import compartment_service as cs
from .constant_radius_track import _NODES, _WEIGHTS, packet_position, smooth_step


def step(t) -> np.ndarray:
    """C-infinity step on arrays: 0 for t <= 0, 1 for t >= 1, every derivative zero at both ends."""
    t = np.asarray(t, dtype=float)
    inside = (t > 0) & (t < 1)
    safe = np.where(inside, t, .5)
    return np.where(t >= 1, 1., np.where(inside, expit(1/(1-safe)-1/safe), 0.))


def transition_integral_array(t) -> np.ndarray:
    """Integral of the C-infinity step from 0 to t on arrays, by the quadrature of transition_integral."""
    t = np.asarray(t, dtype=float)
    out = np.where(t >= 1, t-.5, 0.)
    inside = (t > 0) & (t < 1)
    if inside.any():
        x = t[inside]
        low = x <= .5
        y = np.where(low, x, 1-x)
        part = .5*y*(step(.5*y[:, None]*(_NODES+1)) @ _WEIGHTS)
        out[inside] = np.where(low, part, x-.5+part)
    return out


@dataclass(frozen=True)
class ForwardShelf:
    """Lapse held at e^log_lapse ahead of the pattern, from its front fall to a leading edge.

    radius gives the start and width of the shelf's radial fall. The leading edge leaves the pattern's front
    extent when the lapse structure switches on and runs at lead_speed, above the light speed e^log_lapse inside
    the shelf. lead_speed = inf switches the shelf on along its whole length together with the pattern. The edge
    comes to rest over stop_time, with its fall starting terminal_gap beyond the pattern's front extent at arrival.
    """
    log_lapse: float = 1.
    radius: tuple[float, float] = (13.25, 4.)
    lead_speed: float = 3.5
    lead_width: float = 2.
    terminal_gap: float = 2.
    stop_time: float = 1.

    def __post_init__(self):
        values = (self.log_lapse, *self.radius, self.lead_width, self.terminal_gap, self.stop_time)
        if not all(math.isfinite(x) for x in values) or math.isnan(self.lead_speed):
            raise ValueError("shelf values must be finite; the lead speed may be infinite")
        if min(self.log_lapse, self.radius[1], self.lead_width, self.stop_time) <= 0 or self.terminal_gap < 0:
            raise ValueError("the shelf lapse and widths must be positive, the terminal gap nonnegative")
        if self.lead_speed <= math.exp(self.log_lapse):
            raise ValueError("the leading edge must outrun light inside the shelf")

    def terminal(self, service: cs.CompartmentService) -> float:
        """Where the leading edge's fall starts once the edge rests."""
        arrive = service.path[7]+service.path[8]
        return service.packet_position(arrive)+service.extent+self.terminal_gap

    def edge_path(self, service: cs.CompartmentService):
        """Packet-path tuple of the leading edge, or None for a shelf switched on along its whole length."""
        if math.isinf(self.lead_speed):
            return None
        on = service.schedule[0]
        start = service.packet_position(on)+service.extent
        u = self.lead_speed
        stop = on+(self.terminal(service)-u*self.stop_time/2-start)/u
        if stop <= on:
            raise ValueError("the terminal lies too close to the pattern's start for the edge to run")
        return (on, start, u, u, 0., on, 1., stop, self.stop_time)

    def edge_position(self, service: cs.CompartmentService, s: float) -> float:
        path = self.edge_path(service)
        return self.terminal(service) if path is None else packet_position(s, path)

    def log_lapse_at(self, service: cs.CompartmentService, s: float, z, r) -> np.ndarray:
        """Log-lapse term at points (z, r), broadcast together, at exterior time s."""
        z, r = np.broadcast_arrays(np.asarray(z, dtype=float), np.asarray(r, dtype=float))
        schedule = service.schedule_value(s)
        if schedule == 0.:
            return np.zeros(r.shape)
        zeta = z-service.packet_position(s)
        weight = schedule*step((zeta-service.fall_start)/service.fall_width)
        weight = weight*(1.-step((z-self.edge_position(service, s))/self.lead_width))
        return weight*self.log_lapse*(1.-step((r-self.radius[0])/self.radius[1]))


@dataclass(frozen=True)
class ConeFront:
    """Raised lapse inside a slender cone ahead of the pattern, peaked on the axis.

    The cone's radius r_c = min(tan(half_angle) (zeta_tip - zeta), base_radius), softened over base_softness,
    reaches base_radius at the pattern's front extent. Its log-lapse log_lapse * step(d/layer) rises across a layer
    inside the surface d = r_c - (sqrt(r^2 + rounding^2) - rounding) = 0. The rounding sets the lapse curvature on
    the axis near the tip. The term rises along the track over rise_width from the shift's front edge, into the
    pattern's front fall where the pattern's own lapse still exceeds the carry speed. The cone extends from the
    shift's front edge as the carry speed rises through extend. With space = "alpha" the layer interpolates
    alpha - 1 in place of the log-lapse, and warp < 1 moves the onset of its fall toward the cone's interior.
    """
    half_angle: float = 15.
    log_lapse: float = 1.5
    layer: float = 3.
    rounding: float = .5
    base_radius: float = 16.
    base_softness: float = 1.
    rise_width: float = 1.5
    extend: tuple[float, float] = (.6, 1.)
    space: str = "log"
    warp: float = 1.

    def __post_init__(self):
        values = (self.half_angle, self.log_lapse, self.layer, self.rounding, self.base_radius, self.base_softness,
                  self.rise_width, *self.extend, self.warp)
        if not all(math.isfinite(x) for x in values):
            raise ValueError("cone values must be finite")
        if self.space not in ("log", "alpha") or not 0 < self.warp <= 1:
            raise ValueError("the cone's space is log or alpha and its warp lies in (0, 1]")
        if not 0 < self.half_angle < 90 or min(self.log_lapse, self.layer, self.rounding, self.base_radius,
                                               self.base_softness, self.rise_width) <= 0 \
                or self.extend[1] <= self.extend[0]:
            raise ValueError("the half-angle lies in (0, 90); widths, radii and lapse are positive; extend rises")

    def tip(self, service: cs.CompartmentService) -> float:
        """Offset of the fully extended cone's tip ahead of the packet."""
        return service.extent+self.base_radius/math.tan(math.radians(self.half_angle))

    def log_lapse_at(self, service: cs.CompartmentService, s: float, z, r) -> np.ndarray:
        """Log-lapse term at points (z, r), broadcast together, at exterior time s."""
        z, r = np.broadcast_arrays(np.asarray(z, dtype=float), np.asarray(r, dtype=float))
        schedule = service.schedule_value(s)
        if schedule == 0.:
            return np.zeros(r.shape)
        shift_end = service.shift_start+service.shift_width
        zeta = z-service.packet_position(s)
        weight = schedule*step((zeta-shift_end)/self.rise_width)
        low, high = self.extend
        grow = smooth_step((service.carry_speed(s)-low)/(high-low))
        tip = shift_end+(self.tip(service)-shift_end)*grow
        cone = math.tan(math.radians(self.half_angle))*(tip-zeta)
        radius = -self.base_softness*np.logaddexp(-cone/self.base_softness, -self.base_radius/self.base_softness)
        depth = radius-(np.sqrt(r*r+self.rounding**2)-self.rounding)
        if self.space == "log" and self.warp == 1.:
            return weight*self.log_lapse*step(depth/self.layer)
        profile = 1-shaped_step(1-depth/self.layer, self.warp)
        if self.space == "alpha":
            return np.log1p(np.expm1(weight*self.log_lapse)*profile)
        return weight*self.log_lapse*profile


def log_lapse_jet(function, s: float, z: float, r, h: float) -> dict[str, np.ndarray]:
    """Central-difference (sigma, z, r) jet of a log-lapse term function(s, z, r), even in r."""
    r = np.asarray(r, dtype=float)

    def f(ds, dz, dr):
        return np.asarray(function(s+ds, z+dz, np.abs(r+dr)), dtype=float)

    v = f(0., 0., 0.)
    pairs = {"s": (h, 0., 0.), "z": (0., h, 0.), "r": (0., 0., h)}
    plus = {key: f(*d) for key, d in pairs.items()}
    minus = {key: f(*(-x for x in d)) for key, d in pairs.items()}
    jet = {"v": v}
    for key in pairs:
        jet[key] = (plus[key]-minus[key])/(2*h)
        jet[key+key] = (plus[key]-2*v+minus[key])/(h*h)
    for a, b in (("s", "z"), ("s", "r"), ("z", "r")):
        da, db = np.array(pairs[a]), np.array(pairs[b])
        jet[a+b] = (f(*(da+db))-f(*(da-db))-f(*(db-da))+f(*(-da-db)))/(4*h*h)
    return jet


def add_log_lapse(fields: dict[str, np.ndarray], jet: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Fields with log alpha raised by a term given as a (sigma, z, r) jet."""
    alpha = fields["alpha"]
    g = {key: fields[f"alpha_{key}"]/alpha for key in ("s", "z", "r")}
    for key in ("ss", "sz", "zz", "sr", "zr", "rr"):
        g[key] = fields[f"alpha_{key}"]/alpha-g[key[0]]*g[key[1]]
    g = {key: value+jet[key] for key, value in g.items()}
    value = alpha*np.exp(jet["v"])
    out = dict(fields)
    out["alpha"] = value
    for key in ("s", "z", "r"):
        out[f"alpha_{key}"] = value*g[key]
    for key in ("ss", "sz", "zz", "sr", "zr", "rr"):
        out[f"alpha_{key}"] = value*(g[key]+g[key[0]]*g[key[1]])
    return out


def fields(service: cs.CompartmentService, design, front, s: float, z: float, r) -> dict[str, np.ndarray]:
    """Compartment fields at radii r with the front element's log-lapse added (front None leaves them unchanged)."""
    r = np.atleast_1d(np.asarray(r, dtype=float))
    out = cs.fields(service, design, s, z, r)
    if service.shaped:
        out = add_log_lapse(out, log_lapse_jet(lambda a, b, c: pattern_correction(service, design, a, b, c),
                                               float(s), float(z), r, design.jet_step/4))
    if front is None:
        return out
    jet = log_lapse_jet(lambda a, b, c: front.log_lapse_at(service, a, b, c), float(s), float(z), r,
                        design.jet_step)
    return add_log_lapse(out, jet)


def frame_tensor(service: cs.CompartmentService, design, front, s: float, z: float, r) -> np.ndarray:
    """Orthonormal demanded tensors at radii r > 0, with the transverse terms evaluated at every radius."""
    r = np.atleast_1d(np.asarray(r, dtype=float))
    return ax.tensor_from_fields(fields(service, design, front, s, z, r), r, design, product_core=False)


def sheath_value(design, s: float, z, r) -> np.ndarray:
    """Log-lapse of the time-staged sheath at points (z, r), as sheath_jets builds it."""
    fraction = design.track.join_fraction
    rise, fall = design.sheath_rise, design.sheath_fall
    e = ax.step_jet((r-rise[0])/rise[1], fraction)[0]*(1-ax.step_jet((r-fall[0])/fall[1], fraction)[0])
    length, taper = design.sheath_length
    value = design.sheath_log_lapse*(1-ax.step_jet((np.abs(z)-length)/taper, fraction)[0])*e
    if design.sheath_schedule is not None:
        on, off, ramp = design.sheath_schedule
        up, down = ax.step_jet(np.array([(s-on)/ramp, (s-off)/ramp]), fraction)[0]
        value = value*up*(1-down)
    if design.sheath_follow is not None:
        half, edge = design.sheath_follow
        offset = z-packet_position(s, design.track.packet_path)
        value = value*(1-ax.step_jet((np.abs(offset)-half)/edge, fraction)[0])
    return value


def shaped_step(t, warp: float = 1.) -> np.ndarray:
    """C-infinity step of t**warp on [0, 1]; warp < 1 moves the onset toward t = 0 and lengthens the landing."""
    t = np.clip(np.asarray(t, dtype=float), 0., 1.)
    return step(t**warp)


def pattern_log_lapse(service: cs.CompartmentService, design, s: float, z, r) -> np.ndarray:
    """Log-lapse of the plateau and the sheath with the outer falls shaped as the service sets.

    Inside the falls the level, plateau plus convex rise plus the sheath's radial rise, keeps its value. The falls
    take the factor (1 - shaped_step(x)) (1 - shaped_step(y)) along the track and in r, with the radial warp set
    apart when the service gives one, or, with rounded corners,
    1 - shaped_step(d) of the softened distance d from the plateau's core. In lapse space the factor scales
    alpha - 1, in log space the log-lapse; the mixed space scales the log-lapse across the radial fall and
    alpha - 1 along the track. The radial fall of plateau and sheath both follow the lapse layer, and
    the falls lie where the shift vanishes.
    """
    z, r = np.broadcast_arrays(np.asarray(z, dtype=float), np.abs(np.asarray(r, dtype=float)))
    fraction = design.track.join_fraction
    u = np.abs(z-service.packet_position(s))
    start = service.shift_start-service.slope_ramp
    rise = service.slope*service.slope_ramp*transition_integral_array((u-start)/service.slope_ramp)
    sheath = design.sheath_log_lapse*ax.step_jet((r-design.sheath_rise[0])/design.sheath_rise[1], fraction)[0]
    length, taper = design.sheath_length
    sheath = sheath*(1-ax.step_jet((np.abs(z)-length)/taper, fraction)[0])
    if design.sheath_schedule is not None:
        on, off, ramp = design.sheath_schedule
        up, down = ax.step_jet(np.array([(s-on)/ramp, (s-off)/ramp]), fraction)[0]
        sheath = sheath*up*(1-down)
    level = service.schedule_value(s)*(service.plateau_log+rise)+sheath
    fall_start, fall_width = design.layers["alpha"]
    x = (u-service.fall_start)/service.fall_width
    y = (r-fall_start)/fall_width
    if service.pattern_corner == "round":
        width = service.pattern_rounding
        distance = np.hypot(width*np.logaddexp(0., x/width), width*np.logaddexp(0., y/width))
        keep = 1-shaped_step(distance, service.pattern_warp)
    else:
        radial = service.pattern_warp if service.pattern_radial_warp is None else service.pattern_radial_warp
        along, across = 1-shaped_step(x, service.pattern_warp), 1-shaped_step(y, radial)
        if service.pattern_space == "mixed":
            return np.log1p(np.expm1(level*across)*along)
        keep = along*across
    if service.pattern_space == "alpha":
        return np.log1p(np.expm1(level)*keep)
    return level*keep


def product_pattern_log_lapse(service: cs.CompartmentService, design, s: float, z, r) -> np.ndarray:
    """Log-lapse of the plateau and the sheath as products of log-lapse steps, the unshaped pattern."""
    z, r = np.broadcast_arrays(np.asarray(z, dtype=float), np.abs(np.asarray(r, dtype=float)))
    u = np.abs(z-service.packet_position(s))
    start = service.shift_start-service.slope_ramp
    rise = service.slope*service.slope_ramp*transition_integral_array((u-start)/service.slope_ramp)
    plateau = service.schedule_value(s)*(service.plateau_log+rise)*(1.-step((u-service.fall_start)/service.fall_width))
    chi_alpha = ax.layer_blend(r, design.layers["alpha"], design.track.join_fraction)[0]
    return chi_alpha*plateau+sheath_value(design, s, z, r)


def pattern_correction(service: cs.CompartmentService, design, s: float, z, r) -> np.ndarray:
    """Log-lapse that turns the unshaped pattern into the shaped one; it vanishes inside the plateau's core."""
    return pattern_log_lapse(service, design, s, z, r)-product_pattern_log_lapse(service, design, s, z, r)


def log_lapse_and_shift(service: cs.CompartmentService, design, front, s: float, z, r):
    """log alpha and beta at points (z, r), broadcast together, at exterior time s, directly from the profiles."""
    z, r = np.broadcast_arrays(np.asarray(z, dtype=float), np.abs(np.asarray(r, dtype=float)))
    fraction = design.track.join_fraction
    centre, speed, schedule = service.packet_position(s), service.carry_speed(s), service.schedule_value(s)
    u = np.abs(z-centre)
    start = service.shift_start-service.slope_ramp
    rise = service.slope*service.slope_ramp*transition_integral_array((u-start)/service.slope_ramp)
    plateau = schedule*(service.plateau_log+rise)*(1.-step((u-service.fall_start)/service.fall_width))
    hole = -schedule*(service.plateau_log-service.clock_log)*(1.-step((u-service.half_width)/service.hole_edge))
    shift = -speed*(1.-step((u-service.shift_start)/service.shift_width))
    chi_alpha = ax.layer_blend(r, design.layers["alpha"], fraction)[0]
    chi_beta = ax.layer_blend(r, design.layers["beta"], fraction)[0]
    edge = ax.layer_blend(r, service.hole_radius, fraction)[0]
    log_alpha = chi_alpha*plateau+sheath_value(design, s, z, r)+edge*hole
    if service.shaped:
        log_alpha = log_alpha+pattern_correction(service, design, s, z, r)
    if front is not None:
        log_alpha = log_alpha+front.log_lapse_at(service, s, z, r)
    return log_alpha, chi_beta*shift


def point_log_lapse_and_shift(service: cs.CompartmentService, design, front, s: float, z: float,
                              r: float) -> tuple[float, float]:
    """log alpha and beta at one point."""
    log_alpha, shift = log_lapse_and_shift(service, design, front, s, np.array([float(z)]), np.array([float(r)]))
    return float(log_alpha[0]), float(shift[0])


def _rates(service, design, front, s, y, mass, h):
    """sigma-derivatives of (z, r, kz, kr) for columns of y, from the Hamiltonian alpha sqrt(mass+k^2) - beta kz."""
    z, r, kz, kr = y
    points_z = np.concatenate([z, z+h, z-h, z, z])
    points_r = np.concatenate([r, r, r, np.abs(r)+h, np.abs(r)-h])
    log_alpha, shift = log_lapse_and_shift(service, design, front, s, points_z, points_r)
    a, b = np.exp(log_alpha).reshape(5, -1), shift.reshape(5, -1)
    side = np.where(r >= 0, 1., -1.)
    a_z, b_z = (a[1]-a[2])/(2*h), (b[1]-b[2])/(2*h)
    a_r, b_r = side*(a[3]-a[4])/(2*h), side*(b[3]-b[4])/(2*h)
    e = np.sqrt(mass+kz*kz+kr*kr)
    return np.stack([a[0]*kz/e-b[0], a[0]*kr/e, -a_z*e+b_z*kz, -a_r*e+b_r*kz])


def trace(service: cs.CompartmentService, design, front, s_span, z0: float, r0: float, k0, *, mass: float,
          h: float = 1e-5, max_step: float = .02, rtol: float = 1e-9, atol: float = 1e-11):
    """Meridional ray (mass 0) or unit-mass particle through the design, with sigma as the time.

    The Hamiltonian alpha sqrt(mass + kz^2 + kr^2) - beta kz generates z, r and the covariant momenta (kz, kr);
    sqrt(mass + |k|^2) is the energy measured by the normal observers, which rest in the flat exterior. The
    meridional coordinate r runs through the axis to negative values. Returns the solve_ivp solution with
    y = (z, r, kz, kr).
    """
    def rhs(s, y):
        return _rates(service, design, front, s, np.asarray(y, dtype=float)[:, None], mass, h)[:, 0]

    return solve_ivp(rhs, s_span, [z0, r0, *k0], method="DOP853", rtol=rtol, atol=atol, max_step=max_step)


def trace_many(service: cs.CompartmentService, design, front, s_span, z0, r0, kz0, kr0, *, mass: float,
               ds: float = .01, h: float = 1e-5):
    """Many meridional rays or unit-mass particles advanced together by classical RK4 steps of about ds.

    Returns the final state (z, r, kz, kr) and, for each object, the largest normal-observer energy along the way
    with the sigma, offset from the packet and |r| where it occurred.
    """
    y = np.stack([np.asarray(x, dtype=float) for x in (z0, r0, kz0, kr0)])
    count = max(1, math.ceil((s_span[1]-s_span[0])/ds-1e-9))
    ds = (s_span[1]-s_span[0])/count
    peak = np.sqrt(mass+y[2]**2+y[3]**2)
    at = np.stack([np.full(y.shape[1], float(s_span[0])), y[0]-service.packet_position(s_span[0]), np.abs(y[1])])
    for i in range(count):
        s = s_span[0]+i*ds
        k1 = _rates(service, design, front, s, y, mass, h)
        k2 = _rates(service, design, front, s+ds/2, y+ds/2*k1, mass, h)
        k3 = _rates(service, design, front, s+ds/2, y+ds/2*k2, mass, h)
        k4 = _rates(service, design, front, s+ds, y+ds*k3, mass, h)
        y = y+ds/6*(k1+2*k2+2*k3+k4)
        energy = np.sqrt(mass+y[2]**2+y[3]**2)
        higher = energy > peak
        if higher.any():
            peak = np.where(higher, energy, peak)
            at[:, higher] = np.stack([np.full(higher.sum(), s+ds), y[0, higher]-service.packet_position(s+ds),
                                      np.abs(y[1, higher])])
    return y, peak, at
