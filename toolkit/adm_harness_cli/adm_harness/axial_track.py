"""Axial track: the constant-radius service metric inside a tube of one asymptotically flat space.

Coordinates (sigma, z, r, phi), with phi a Killing direction:

    ds^2 = -alpha^2 dsigma^2 + A^2 (dz + beta dsigma)^2 + dr^2 + C(r)^2 dphi^2.

Inside the core r <= core_radius the fields alpha, A and beta equal the service
fields of the constant-radius track with the rail coordinate read as z, so the
spacetime is an exact product of the service (sigma, z) metric with the
transverse plane. A C-infinity wall of width wall_width returns log alpha,
log A and beta to zero; beyond it, and beyond the service cutoff in z, the
metric is exactly Minkowski. The transverse profile is flat (C = r) or carries
a string-core curvature string_curvature*chi(r), where chi is the wall blend,
so the core is a spherical cap and the exterior a cone.

The orthonormal Einstein tensor comes from axial_einstein_generated. In the
frame n = (d_sigma - beta d_z)/alpha, e_z = d_z/A, e_r = d_r, e_phi = d_phi/C,
the (n, z) block equals (C''/C) eta plus wall terms, the transverse diagonal
equals -K plus wall terms, where K is the Gaussian curvature of the (sigma, z)
metric at the same r, and every wall term carries an r-derivative of the
fields. e_phi is an eigenvector of the stress tensor everywhere.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import expit

from . import axial_einstein_generated as generated
from .constant_radius_track import ConstantRadiusTrackDesign, track_scalars
from .source_ledger import SourceParams

EIGHT_PI = 8*math.pi
TYPE_I = "type_i"
TYPE_II_III = "type_ii_or_iii"
TYPE_IV = "type_iv"
VACUUM = "vacuum"
UNRESOLVED = "unresolved"
_WALL_NODES, _WALL_WEIGHTS = np.polynomial.legendre.leggauss(24)


@dataclass(frozen=True)
class AxialTrackDesign:
    track: ConstantRadiusTrackDesign = field(default_factory=ConstantRadiusTrackDesign)
    core_radius: float = 1.75
    wall_width: float = 1.
    wall_spacing: str = "linear"
    string_curvature: float = 0.
    jet_step: float = .0025
    lapse_layer: tuple[float, float] | None = None
    stretch_layer: tuple[float, float] | None = None
    shift_layer: tuple[float, float] | None = None
    sheath_log_lapse: float = 0.
    sheath_rise: tuple[float, float] = (1.75, 1.)
    sheath_fall: tuple[float, float] = (4.75, 2.)
    sheath_length: tuple[float, float] = (5.5, 1.)
    conformal_log_scale: float = 0.
    conformal_rise: tuple[float, float] = (1.75, 1.)
    conformal_fall: tuple[float, float] = (5.25, 1.)

    def __post_init__(self):
        values = (self.core_radius, self.wall_width, self.string_curvature, self.jet_step, self.sheath_log_lapse,
                  *self.sheath_rise, *self.sheath_fall, *self.sheath_length, self.conformal_log_scale,
                  *self.conformal_rise, *self.conformal_fall,
                  *(x for layer in (self.lapse_layer, self.stretch_layer, self.shift_layer) if layer for x in layer))
        if not all(math.isfinite(x) for x in values):
            raise ValueError("axial design values must be finite")
        if min(self.core_radius, self.wall_width, self.jet_step) <= 0 or self.string_curvature < 0:
            raise ValueError("core radius, wall width and jet step must be positive; string curvature nonnegative")
        if self.wall_spacing not in {"linear", "logarithmic"}:
            raise ValueError("wall spacing is linear or logarithmic")
        if self.staged:
            if self.wall_spacing != "linear" or self.string_curvature != 0:
                raise ValueError("staged boundary layers use linear spacing and a flat transverse profile")
            spans = list(self.layers.values())
            if self.sheath_log_lapse:
                spans += [self.sheath_rise, self.sheath_fall]
            if self.conformal_log_scale:
                spans += [self.conformal_rise, self.conformal_fall]
            if any(start < self.core_radius or width <= 0 for start, width in spans):
                raise ValueError("every layer starts at or beyond the service-region radius with positive width")
            if min(self.sheath_length) <= 0:
                raise ValueError("the sheath length and its taper must be positive")

    @property
    def staged(self) -> bool:
        return any(layer is not None for layer in (self.lapse_layer, self.stretch_layer, self.shift_layer)) or \
            self.sheath_log_lapse != 0 or self.conformal_log_scale != 0

    @property
    def layers(self) -> dict[str, tuple[float, float]]:
        """Radial transition (start, width) of log alpha, log A and beta; the service-region wall by default."""
        default = (self.core_radius, self.wall_width)
        return {"alpha": self.lapse_layer or default, "A": self.stretch_layer or default,
                "beta": self.shift_layer or default}

    @property
    def outer_radius(self) -> float:
        if not self.staged:
            return self.core_radius+self.wall_width
        ends = [start+width for start, width in self.layers.values()]
        if self.sheath_log_lapse:
            ends.append(self.sheath_fall[0]+self.sheath_fall[1])
        if self.conformal_log_scale:
            ends.append(self.conformal_fall[0]+self.conformal_fall[1])
        return max(ends)


def step_jet(t, fraction):
    """Value, first and second derivative of the flattened minimum-jerk step at array t."""
    t = np.asarray(t, dtype=float)

    def smooth(x):
        inside = (x > 0) & (x < 1)
        y = np.where(inside, x, .5)
        g = 1/(1-y)-1/y
        g1 = 1/(1-y)**2+1/y**2
        g2 = 2/(1-y)**3-2/y**3
        value, other = expit(g), expit(-g)
        both = value*other
        psi = np.where(x >= 1, 1., np.where(inside, value, 0.))
        psi1 = np.where(inside, both*g1, 0.)
        psi2 = np.where(inside, both*((other-value)*g1*g1+g2), 0.)
        return psi, psi1, psi2

    m = t**3*(10+t*(-15+6*t))
    m1 = 30*t*t*(1-t)**2
    m2 = 60*t*(1-t)*(1-2*t)
    lower_psi, lower1, lower2 = smooth(t/fraction)
    upper_psi, upper1, upper2 = smooth((1-t)/fraction)
    lower = (m*lower_psi, m1*lower_psi+m*lower1/fraction, m2*lower_psi+2*m1*lower1/fraction+m*lower2/fraction**2)
    rest = 1-m
    upper = (1-rest*upper_psi, m1*upper_psi+rest*upper1/fraction,
             m2*upper_psi-2*m1*upper1/fraction-rest*upper2/fraction**2)
    first_half = t <= .5
    value, first, second = (np.where(first_half, a, b) for a, b in zip(lower, upper))
    value = np.where(t <= 0, 0., np.where(t >= 1, 1., value))
    first = np.where((t <= 0) | (t >= 1), 0., first)
    second = np.where((t <= 0) | (t >= 1), 0., second)
    return value, first, second


def wall_blend(r, design: AxialTrackDesign):
    """chi(r) = 1 - step(u(r)) with its first two r-derivatives; chi = 1 in the core and 0 outside."""
    r = np.asarray(r, dtype=float)
    if design.wall_spacing == "linear":
        u = (r-design.core_radius)/design.wall_width
        du, ddu = np.full_like(r, 1/design.wall_width), np.zeros_like(r)
    else:
        span = math.log(design.outer_radius/design.core_radius)
        safe = np.maximum(r, .5*design.core_radius)
        u = np.log(safe/design.core_radius)/span
        du, ddu = 1/(safe*span), -1/(safe*safe*span)
    value, first, second = step_jet(u, design.track.join_fraction)
    return 1-value, -first*du, -(second*du*du+first*ddu)


def layer_blend(r, layer, fraction):
    """1 - step((r - start)/width) with its first two r-derivatives for one field's transition layer."""
    start, width = layer
    value, first, second = step_jet((np.asarray(r, dtype=float)-start)/width, fraction)
    return 1-value, -first/width, -second/(width*width)


def sheath_terms(r, z, design: AxialTrackDesign, rise=None, fall=None, amplitude=None):
    """Log sheath amplitude h(z) E(r): its r-profile E and z-profile h, each with two derivatives.

    E rises across rise and falls across fall (the lapse sheath's by default);
    h equals the amplitude along the track and tapers to zero past
    |z| = sheath_length[0] over sheath_length[1].
    """
    fraction = design.track.join_fraction
    rise = rise or design.sheath_rise
    fall = fall or design.sheath_fall
    amplitude = design.sheath_log_lapse if amplitude is None else amplitude
    up, up1, up2 = step_jet((np.asarray(r, dtype=float)-rise[0])/rise[1], fraction)
    down, down1, down2 = step_jet((np.asarray(r, dtype=float)-fall[0])/fall[1], fraction)
    up1, up2 = up1/rise[1], up2/rise[1]**2
    down1, down2 = down1/fall[1], down2/fall[1]**2
    e = up*(1-down)
    e1 = up1*(1-down)-up*down1
    e2 = up2*(1-down)-2*up1*down1-up*down2
    length, taper = design.sheath_length
    taper_value, taper1, taper2 = (float(x[0]) for x in step_jet(np.array([(abs(z)-length)/taper]), fraction))
    h = amplitude*(1-taper_value)
    h1 = -amplitude*math.copysign(1., z)*taper1/taper
    h2 = -amplitude*taper2/taper**2
    return (e, e1, e2), (h, h1, h2)


def conformal_terms(r, z, design: AxialTrackDesign):
    """The conformal sheath, added equally to log alpha and log A."""
    return sheath_terms(r, z, design, design.conformal_rise, design.conformal_fall, design.conformal_log_scale)


@lru_cache(maxsize=64)
def _string_core_solution(design: AxialTrackDesign):
    k = math.sqrt(design.string_curvature)
    start = (math.sin(k*design.core_radius)/k, math.cos(k*design.core_radius))

    def rhs(r, y):
        chi = wall_blend(np.array([r]), design)[0][0]
        return [y[1], -design.string_curvature*chi*y[0]]

    solution = solve_ivp(rhs, (design.core_radius, design.outer_radius), start, method="DOP853",
                         rtol=1e-12, atol=1e-14, dense_output=True)
    if not solution.success:
        raise ArithmeticError("string-core profile integration failed")
    end = solution.y[:, -1]
    if end[1] <= 0:
        raise ValueError("string-core curvature closes the transverse space; the deficit must stay below 2 pi")
    return solution, float(end[0]), float(end[1])


_PROFILE_CACHE: dict = {}


def transverse_profile(r, design: AxialTrackDesign):
    """C, C' and the curvature K with C'' = -K C; the exterior is a cone with slope C'(outer)."""
    r = np.asarray(r, dtype=float)
    key = (design, r.tobytes())
    if key in _PROFILE_CACHE:
        return tuple(item.copy() for item in _PROFILE_CACHE[key])
    result = _transverse_profile(r, design)
    if len(_PROFILE_CACHE) < 256:
        _PROFILE_CACHE[key] = tuple(item.copy() for item in result)
    return result


def _transverse_profile(r, design: AxialTrackDesign):
    chi = wall_blend(r, design)[0]
    curvature = design.string_curvature*chi
    if design.string_curvature == 0:
        return r.copy(), np.ones_like(r), curvature
    k = math.sqrt(design.string_curvature)
    solution, end_value, end_slope = _string_core_solution(design)
    value = np.where(r <= design.core_radius, np.sin(k*r)/k, end_value+end_slope*(r-design.outer_radius))
    slope = np.where(r <= design.core_radius, np.cos(k*r), end_slope)
    wall = (r > design.core_radius) & (r < design.outer_radius)
    if wall.any():
        interior = solution.sol(r[wall])
        value[wall], slope[wall] = interior[0], interior[1]
    return value, slope, curvature


def deficit_angle(design: AxialTrackDesign) -> float:
    if design.string_curvature == 0:
        return 0.
    return 2*math.pi*(1-_string_core_solution(design)[2])


def stencil_jet(fields, s: float, z: float, step: float) -> dict[str, np.ndarray]:
    """(sigma, z) jet of a callable returning (log alpha, log A, beta), from a nine-point central stencil.

    Each entry holds the three fields in that order; keys are v, s, z, ss, sz, zz.
    """
    grid = np.empty((3, 3, 3))
    for i, ds in enumerate((-step, 0., step)):
        for k, dz in enumerate((-step, 0., step)):
            grid[:, i, k] = fields(s+ds, z+dz)
    return {"v": grid[:, 1, 1], "s": (grid[:, 2, 1]-grid[:, 0, 1])/(2*step),
            "z": (grid[:, 1, 2]-grid[:, 1, 0])/(2*step),
            "ss": (grid[:, 2, 1]-2*grid[:, 1, 1]+grid[:, 0, 1])/step**2,
            "sz": (grid[:, 2, 2]-grid[:, 2, 0]-grid[:, 0, 2]+grid[:, 0, 0])/(4*step*step),
            "zz": (grid[:, 1, 2]-2*grid[:, 1, 1]+grid[:, 1, 0])/step**2}


def core_fields(s: float, z: float, params: SourceParams, design: AxialTrackDesign) -> tuple[float, float, float]:
    """log alpha, log A and beta of the core: the constant-radius track's service fields along z."""
    f = track_scalars(float(s), float(z), params, design.track)
    return math.log(f["alpha"]), .5*math.log(f["gamma_ll"]), f["beta"]


def service_jet(s: float, z: float, params: SourceParams, design: AxialTrackDesign) -> dict[str, np.ndarray]:
    return stencil_jet(lambda a, b: core_fields(a, b, params, design), s, z, design.jet_step)


def radial_jets(jet, chi, d1, d2, *, blends=None, sheath=None, conformal=None):
    """Full jets of alpha = exp(chi_a a + s0 h E), A = exp(chi_b b) and beta = chi_s beta_s over arrays of r.

    Without blends, one blend (chi, d1, d2) serves all three fields. blends
    gives one (chi, chi', chi'') per field in the order alpha, A, beta. sheath
    is ((E, E', E''), (h, h', h'')) for the log-lapse sheath, and conformal has
    the same form for a sheath added equally to log alpha and log A.
    """
    blends = blends or ((chi, d1, d2),)*3
    out = {}
    for index, name in enumerate(("alpha", "A")):
        f = {key: jet[key][index] for key in jet}
        c, c1, c2 = blends[index]
        g = {"v": c*f["v"], "s": c*f["s"], "z": c*f["z"], "r": c1*f["v"], "ss": c*f["ss"], "sz": c*f["sz"],
             "zz": c*f["zz"], "sr": c1*f["s"], "zr": c1*f["z"], "rr": c2*f["v"]}
        for term in ((sheath,) if index == 0 else ())+(conformal,):
            if term is None:
                continue
            (e, e1, e2), (h, h1, h2) = term
            g["v"] = g["v"]+h*e
            g["z"] = g["z"]+h1*e
            g["r"] = g["r"]+h*e1
            g["zz"] = g["zz"]+h2*e
            g["zr"] = g["zr"]+h1*e1
            g["rr"] = g["rr"]+h*e2
        value = np.exp(g["v"])
        out[name] = value
        for key in ("s", "z", "r"):
            out[f"{name}_{key}"] = value*g[key]
        for key in ("ss", "sz", "zz", "sr", "zr", "rr"):
            out[f"{name}_{key}"] = value*(g[key]+g[key[0]]*g[key[1]])
    b = {key: jet[key][2] for key in jet}
    c, c1, c2 = blends[2]
    out["beta"] = c*b["v"]
    for key in ("s", "z", "ss", "sz", "zz"):
        out[f"beta_{key}"] = c*b[key]
    out["beta_r"], out["beta_sr"], out["beta_zr"], out["beta_rr"] = c1*b["v"], c1*b["s"], c1*b["z"], c2*b["v"]
    return out


def service_curvature(jet) -> float:
    """Gaussian curvature K of the core (sigma, z) metric; the core transverse pressures are -K/(8 pi)."""
    one = np.ones(1)
    fields = radial_jets(jet, one, 0*one, 0*one)
    fields.update(C=one, C_r=0*one, C_rr=0*one)
    return float(-generated.product_rr(fields)[0])


def frame_tensor(jet, r, design: AxialTrackDesign, z: float = 0.) -> np.ndarray:
    """Orthonormal stress tensors T_ab = G_ab/(8 pi) at radii r for one (sigma, z) jet; shape (len(r), 4, 4).

    The rail coordinate z enters through the sheath's taper along the track.
    """
    r = np.atleast_1d(np.asarray(r, dtype=float))
    value, slope, curvature = transverse_profile(r, design)
    if design.staged:
        fraction = design.track.join_fraction
        blends = tuple(layer_blend(r, design.layers[name], fraction) for name in ("alpha", "A", "beta"))
        sheath = sheath_terms(r, z, design) if design.sheath_log_lapse else None
        conformal = conformal_terms(r, z, design) if design.conformal_log_scale else None
        fields = radial_jets(jet, None, None, None, blends=blends, sheath=sheath, conformal=conformal)
    else:
        chi, d1, d2 = wall_blend(r, design)
        fields = radial_jets(jet, chi, d1, d2)
    fields.update(C=value, C_r=slope, C_rr=-curvature*value)
    wall = r > design.core_radius
    tensor = np.zeros((len(r), 4, 4))
    transverse = generated.product_rr({**fields, "C": np.ones_like(r)})
    tensor[:, 0, 0] = curvature
    tensor[:, 1, 1] = -curvature
    tensor[:, 2, 2] = transverse
    tensor[:, 3, 3] = transverse
    if wall.any():
        sub = {key: (item[wall] if isinstance(item, np.ndarray) and item.shape == r.shape else item)
               for key, item in fields.items()}
        for (a, b), function in {(0, 0): generated.wall_nn, (0, 1): generated.wall_nz, (1, 1): generated.wall_zz,
                                 (0, 2): generated.wall_nr, (1, 2): generated.wall_zr, (2, 2): generated.wall_rr,
                                 (3, 3): generated.wall_pp}.items():
            tensor[wall, a, b] += function(sub)
    tensor[:, 1, 0], tensor[:, 2, 0], tensor[:, 2, 1] = tensor[:, 0, 1], tensor[:, 0, 2], tensor[:, 1, 2]
    return tensor/EIGHT_PI


def min_null_energy(tensor: np.ndarray) -> np.ndarray:
    """Minimum of T(k, k) over null k = n + e with |e| = 1, by the exact trust-region dual.

    min_e T_nn + 2 t.e + e.S.e equals T_nn + lambda_1 - delta - sum_i t_i^2/(lambda_i - lambda_1 + delta),
    where delta >= 0 solves sum_i t_i^2/(lambda_i - lambda_1 + delta)^2 = 1, or delta = 0 when no root
    exists. The computation runs on each tensor divided by its largest component.
    """
    tensor = np.asarray(tensor, dtype=float)
    count = len(tensor)
    scale = np.max(np.abs(tensor.reshape(count, -1)), axis=1)
    safe = np.where(scale > 0, scale, 1.)
    unit = tensor/safe[:, None, None]
    lam, vectors = np.linalg.eigh(unit[:, 1:, 1:])
    t = np.einsum("nji,nj->ni", vectors, unit[:, 0, 1:])
    gaps = lam-lam[:, :1]
    weight = np.where(t*t <= 1e-28, 0., t*t)

    def secular(delta):
        with np.errstate(divide="ignore", invalid="ignore"):
            terms = np.where(weight > 0, weight/(gaps+delta[:, None])**2, 0.)
        return terms.sum(axis=1)-1

    lo = np.maximum(np.sqrt(weight[:, 0]), 1e-18)
    hi = np.maximum(np.sqrt(weight.sum(axis=1)), lo)*(1+1e-12)+1e-18
    hard = secular(np.zeros(count)) <= 0
    for _ in range(80):
        mid = np.sqrt(lo*hi)
        above = secular(mid) > 0
        lo, hi = np.where(above, mid, lo), np.where(above, hi, mid)
    delta = np.where(hard, 0., np.sqrt(lo*hi))
    with np.errstate(divide="ignore", invalid="ignore"):
        penalty = np.where(weight > 0, weight/(gaps+delta[:, None]), 0.).sum(axis=1)
    return (unit[:, 0, 0]+lam[:, 0]-delta-penalty)*safe


def classify(tensor: np.ndarray, *, imaginary_tolerance: float = 1e-6, null_tolerance: float = 1e-6,
             floor: float = 0.) -> dict[str, np.ndarray]:
    """Hawking-Ellis type of frame tensors whose e_phi direction is an eigenvector.

    Eigenvalues of the (n, z, r) block of T^a_b, normalized by the largest
    tensor component, come from the backward-stable QR algorithm. A complex
    pair whose imaginary part exceeds imaginary_tolerance is Type IV, with
    margin minus that imaginary part. A real spectrum with a timelike
    eigenvector is Type I, with margin the magnitude of that eigenvector's
    Minkowski norm at unit Euclidean length; the margin falls to zero at the
    null (Type II) boundary. Nearly repeated eigenvalues are resolved from
    eigenspace dimensions and the Minkowski Gram matrix of each eigenspace.
    Tensors whose largest component is at or below floor are vacuum. Type I
    points report the rest-frame energy density, principal pressures
    (including p_phi) and the rest-frame null-energy margin.
    """
    tensor = np.asarray(tensor, dtype=float)
    count = len(tensor)
    scale = np.max(np.abs(tensor.reshape(count, -1)), axis=1)
    safe = np.where(scale > 0, scale, 1.)
    mixed = np.diag([-1., 1., 1.])[None]@tensor[:, :3, :3]/safe[:, None, None]
    kind = np.full(count, UNRESOLVED, dtype=object)
    margin = np.full(count, np.nan)
    energy = np.full(count, np.nan)
    pressures = np.full((count, 3), np.nan)
    values, vectors = np.linalg.eig(mixed)
    imaginary = np.max(np.abs(values.imag), axis=1)
    vacuum = scale <= floor
    kind[vacuum] = VACUUM
    complex_pair = ~vacuum & (imaginary > imaginary_tolerance)
    kind[complex_pair] = TYPE_IV
    margin[complex_pair] = -imaginary[complex_pair]
    real = ~vacuum & ~complex_pair
    spectrum, basis = values.real, vectors.real
    norms = -basis[:, 0, :]**2+basis[:, 1, :]**2+basis[:, 2, :]**2
    which = np.argmin(norms, axis=1)
    rows = np.arange(count)
    timelike_norm = norms[rows, which]
    gap = np.min(np.abs(spectrum[:, [0, 0, 1]]-spectrum[:, [1, 2, 2]]), axis=1)
    residual = np.max(np.abs(mixed@basis-basis*spectrum[:, None, :]), axis=(1, 2))
    generic = (real & (gap > 1e-6) & (timelike_norm < -null_tolerance)
               & ((norms < -null_tolerance).sum(axis=1) == 1) & (residual < 1e-8))
    kind[generic] = TYPE_I
    margin[generic] = -timelike_norm[generic]
    energy[generic] = -spectrum[rows, which][generic]*safe[generic]
    pressures[generic, 0] = spectrum[rows, (which+1) % 3][generic]*safe[generic]
    pressures[generic, 1] = spectrum[rows, (which+2) % 3][generic]*safe[generic]
    for index in np.flatnonzero(real & ~generic):
        result = _resolve_degenerate(mixed[index], null_tolerance)
        if result is None:
            continue
        kind[index], margin[index], value, others = result
        if kind[index] == TYPE_I:
            energy[index] = -value*safe[index]
            pressures[index, :2] = np.asarray(others)*safe[index]
    type_i = kind == TYPE_I
    pressures[type_i, 2] = tensor[type_i, 3, 3]
    rest_null = np.min(energy[:, None]+pressures, axis=1)
    certified = vacuum | complex_pair | type_i
    return {"type": kind, "certified": certified, "type_margin": margin, "scale": scale,
            "rest_energy_density": energy, "principal_pressures": pressures, "rest_null_margin": rest_null}


def _resolve_degenerate(matrix, null_tolerance):
    """Type of a real, nearly degenerate or nearly null block from its eigenspaces.

    Returns (type, margin, timelike eigenvalue, other two eigenvalues), or None
    when the block sits within tolerance of the null boundary.
    """
    spectrum = np.sort(np.linalg.eigvals(matrix).real)
    clusters = [[spectrum[0]]]
    for value in spectrum[1:]:
        if abs(value-clusters[-1][-1]) <= 1e-6:
            clusters[-1].append(value)
        else:
            clusters.append([value])
    eta = np.diag([-1., 1., 1.])
    spaces = []
    for cluster in clusters:
        centre = float(np.mean(cluster))
        _, singular, right = np.linalg.svd(matrix-centre*np.eye(3))
        dimension = int(np.sum(singular <= 1e-6*max(1., singular[0])))
        spaces.append((centre, len(cluster), right[3-dimension:].T if dimension else np.zeros((3, 0))))
    if any(space.shape[1] < multiplicity for _, multiplicity, space in spaces):
        return TYPE_II_III, 0., math.nan, (math.nan, math.nan)
    for centre, multiplicity, space in spaces:
        orthonormal = np.linalg.qr(space)[0]
        lowest = float(np.linalg.eigvalsh(orthonormal.T@eta@orthonormal)[0])
        if lowest < -null_tolerance:
            others = list(spectrum)
            others.remove(min(others, key=lambda v: abs(v-centre)))
            return TYPE_I, -lowest, centre, tuple(others)
    return None


def wall_nodes(design: AxialTrackDesign, per_panel: int = 24):
    """Composite Gauss-Legendre radii and weights over the boundary layer, split at the flattened joins.

    Staged designs split at every layer's joins and use per_panel nodes on each panel.
    """
    fraction = design.track.join_fraction
    if design.staged:
        nodes, node_weights = np.polynomial.legendre.leggauss(per_panel)
        spans = list(design.layers.values())
        if design.sheath_log_lapse:
            spans += [design.sheath_rise, design.sheath_fall]
        if design.conformal_log_scale:
            spans += [design.conformal_rise, design.conformal_fall]
        cuts = {design.core_radius, design.outer_radius}
        for start, width in spans:
            cuts.update(start+width*u for u in (0., fraction, .5, 1-fraction, 1.))
        cuts = np.array(sorted(c for c in cuts if design.core_radius <= c <= design.outer_radius))
        radius = np.concatenate([lo+(hi-lo)*(nodes+1)/2 for lo, hi in zip(cuts[:-1], cuts[1:])])
        weights = np.concatenate([(hi-lo)/2*node_weights for lo, hi in zip(cuts[:-1], cuts[1:])])
        return radius, weights
    edges = (0., fraction, .5, 1-fraction, 1.)
    u_nodes, u_weights = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        u_nodes.append(lo+(hi-lo)*(_WALL_NODES+1)/2)
        u_weights.append((hi-lo)/2*_WALL_WEIGHTS)
    u, weights = np.concatenate(u_nodes), np.concatenate(u_weights)
    if design.wall_spacing == "linear":
        return design.core_radius+design.wall_width*u, weights*design.wall_width
    span = math.log(design.outer_radius/design.core_radius)
    radius = design.core_radius*np.exp(span*u)
    return radius, weights*span*radius
