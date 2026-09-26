"""Flat passenger compartment carried along the axial rail, with a chosen clock rate.

The compartment is a region around the packet where the lapse and the shift
are uniform in space at each service time. The metric there,
-alpha(sigma)^2 dsigma^2 + (dz + beta(sigma) dsigma)^2 + dr^2 + r^2 dphi^2,
is flat, so the normal observers are geodesics: a packet at rest on them
feels neither acceleration nor tidal stress, and its clock runs at the
compartment lapse.

The compartment is a hole cut into a lapse structure of the kind that passes
the demanded-source gate: a plateau of log-lapse L_p covering the shift, with
a convex rise of slope k across the shift's along-track edges, the lapse
sheath across the shift's radial transition, and a fall to the flat exterior
beyond the shift. The hole lowers the log-lapse from L_p to the compartment
value L_c inside |zeta| < W and r < r_c, with its boundary (along the track
over [W, W + hole_edge], radially over hole_radius) placed where the shift is
uniform in space. There a coordinate change z' = z + int beta dsigma removes
the shift, leaving a pure lapse, whose demanded tensor is Type I for any
profile. Every profile is attached to the packet, zeta = z - l_p(sigma), and
the packet rests on the normal observers, beta = -v(sigma) across the shift's
uniform zone. The lapse structure switches on before the carry and off after
it.

The falls to the flat exterior default to products of log-lapse steps.
pattern_space, pattern_warp, pattern_radial_warp and pattern_corner reshape
them through front_surface.pattern_correction; the mixed space keeps the
radial fall in the log-lapse and interpolates the lapse along the track. The
falls lie where the shift vanishes, so every shape leaves a Type I stress
there.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from . import axial_track as ax
from .constant_radius_track import (
    ConstantRadiusTrackDesign, check_packet_path, packet_position, packet_velocity, smooth_step,
    transition_integral,
)


@dataclass(frozen=True)
class CompartmentService:
    path: tuple[float, ...] = (-1., 0., 0., 2.1, 0., 0., 1.5, 6., 1.5)
    clock_log: float = 0.
    plateau_log: float = 4.
    slope: float = .5
    slope_ramp: float = .5
    half_width: float = 1.
    hole_edge: float = 1.
    hole_radius: tuple[float, float] = (1.75, 1.5)
    shift_gap: float = .25
    shift_width: float = 2.
    fall_margin: float = .5
    fall_width: float = 2.
    schedule: tuple[float, float, float] = (-2.5, 9., 1.)
    pattern_space: str = "log"
    pattern_warp: float = 1.
    pattern_corner: str = "product"
    pattern_rounding: float = .05
    pattern_radial_warp: float | None = None

    def __post_init__(self):
        check_packet_path(self.path)
        values = (self.clock_log, self.plateau_log, self.slope, self.slope_ramp, self.half_width, self.hole_edge,
                  *self.hole_radius, self.shift_gap, self.shift_width, self.fall_margin, self.fall_width,
                  *self.schedule, self.pattern_warp, self.pattern_rounding)
        if not all(math.isfinite(x) for x in values):
            raise ValueError("compartment values must be finite")
        radial = self.pattern_warp if self.pattern_radial_warp is None else self.pattern_radial_warp
        if self.pattern_space not in ("log", "alpha", "mixed") or self.pattern_corner not in ("product", "round") \
                or not 0 < self.pattern_warp <= 1 or not 0 < radial <= 1 or self.pattern_rounding <= 0 \
                or (self.pattern_space == "mixed" and self.pattern_corner == "round"):
            raise ValueError("pattern space is log, alpha or mixed (product corners), corners product or round, "
                             "warps in (0, 1]")
        if min(self.half_width, self.hole_edge, self.hole_radius[1], self.slope_ramp, self.shift_width,
               self.fall_width, self.schedule[2]) <= 0 or min(self.shift_gap, self.fall_margin, self.slope) < 0:
            raise ValueError("widths must be positive; gaps, margins and slope nonnegative")
        if self.slope_ramp > self.shift_gap+self.hole_edge:
            raise ValueError("the convex rise starts outside the compartment")
        on, off, ramp = self.schedule
        _, _, _, _, _, accel, _, decel, decel_time = self.path
        if on+ramp > accel or off < decel+decel_time:
            raise ValueError("the lapse structure must be on before the carry starts and stay on until it ends")

    @property
    def shaped(self) -> bool:
        """True when the pattern's outer falls take a shape other than the product of log-lapse steps."""
        return self.pattern_space != "log" or self.pattern_warp != 1. or self.pattern_corner != "product" \
            or self.pattern_radial_warp not in (None, 1.)

    @property
    def shift_start(self) -> float:
        return self.half_width+self.hole_edge+self.shift_gap

    @property
    def fall_start(self) -> float:
        return self.shift_start+self.shift_width+self.fall_margin

    @property
    def extent(self) -> float:
        """Half-length along the track beyond which every field is exactly Minkowski."""
        return self.fall_start+self.fall_width

    def schedule_value(self, s: float) -> float:
        on, off, ramp = self.schedule
        return smooth_step((s-on)/ramp)*(1.-smooth_step((s-off)/ramp))

    def packet_position(self, s: float) -> float:
        return packet_position(s, self.path)

    def carry_speed(self, s: float) -> float:
        return packet_velocity(s, self.path)

    def plateau(self, s: float, z: float) -> float:
        """Log-lapse of the gate-passing structure: plateau, convex rise across the shift edges, fall."""
        u = abs(z-self.packet_position(s))
        start = self.shift_start-self.slope_ramp
        rise = self.slope*self.slope_ramp*transition_integral((u-start)/self.slope_ramp)
        fall = smooth_step((u-self.fall_start)/self.fall_width)
        return self.schedule_value(s)*(self.plateau_log+rise)*(1.-fall)

    def hole(self, s: float, z: float) -> float:
        """Log-lapse subtracted inside the compartment, reaching the clock value on |zeta| <= W."""
        u = abs(z-self.packet_position(s))
        inside = 1.-smooth_step((u-self.half_width)/self.hole_edge)
        return -self.schedule_value(s)*(self.plateau_log-self.clock_log)*inside

    def shift(self, s: float, z: float) -> float:
        u = abs(z-self.packet_position(s))
        return -self.carry_speed(s)*(1.-smooth_step((u-self.shift_start)/self.shift_width))

    def core_fields(self, s: float, z: float) -> tuple[float, float, float]:
        """Plateau log-lapse, log A = 0 and the shift; the hole enters as a separate lapse term."""
        return self.plateau(s, z), 0., self.shift(s, z)

    def clock_rate(self, s: float) -> float:
        """Rate of the packet's proper time per unit exterior time: the compartment lapse."""
        return math.exp(self.clock_log*self.schedule_value(s))


def axial_design(service: CompartmentService, *, sheath_log_lapse: float = 1., sheath_rise=(3.75, 5.),
                 sheath_fall=(9.25, 4.), shift_layer=(4.25, 2.), lapse_layer=(9.25, 4.), jet_step: float = .0025,
                 join_fraction: float = .1):
    """Axial design whose time-staged sheath follows the compartment across the shift's radial transition.

    The sheath falls along the track together with the plateau, so every field is Minkowski beyond extent.
    join_fraction sets the flattened ends of every radial step, the profile shape of the radial layers.
    """
    track = ConstantRadiusTrackDesign(packet_path=service.path, service_inner=900., track_half_length=1000.,
                                      join_fraction=join_fraction)
    return ax.AxialTrackDesign(track=track, jet_step=jet_step, lapse_layer=lapse_layer, stretch_layer=lapse_layer,
                               shift_layer=shift_layer, sheath_log_lapse=sheath_log_lapse, sheath_rise=sheath_rise,
                               sheath_fall=sheath_fall, sheath_length=(1000., 1.),
                               sheath_follow=(service.fall_start, service.fall_width),
                               sheath_schedule=service.schedule)


def fields(service: CompartmentService, design, s: float, z: float, r) -> dict[str, np.ndarray]:
    """alpha, A, beta and C with their jets at radii r: plateau, sheath and hole lapse terms and the shift."""
    r = np.atleast_1d(np.asarray(r, dtype=float))
    s, z = float(s), float(z)
    jet = ax.stencil_jet(service.core_fields, s, z, design.jet_step)
    hole = {key: float(value[0]) for key, value in
            ax.stencil_jet(lambda a, b: (service.hole(a, b), 0., 0.), s, z, design.jet_step).items()}
    fraction = design.track.join_fraction
    blends = tuple(ax.layer_blend(r, design.layers[name], fraction) for name in ("alpha", "A", "beta"))
    edge = ax.layer_blend(r, service.hole_radius, fraction)
    out = ax.radial_jets(jet, None, None, None, blends=blends, sheath=ax.sheath_jets(r, s, z, design),
                         lapse_terms=((edge, hole),))
    out.update(C=r.copy(), C_r=np.ones_like(r), C_rr=np.zeros_like(r))
    return out


def frame_tensor(service: CompartmentService, design, s: float, z: float, r) -> np.ndarray:
    """Orthonormal demanded tensors T_ab = G_ab/(8 pi) at radii r."""
    r = np.atleast_1d(np.asarray(r, dtype=float))
    return ax.tensor_from_fields(fields(service, design, s, z, r), r, design)
