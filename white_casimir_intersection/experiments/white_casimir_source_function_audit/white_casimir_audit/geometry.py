"""Geometry and role-label helpers for the first audit phase.

Coordinate conventions:

- plate-pillar cavity: plates are separated along ``y`` and the pillar axis is
  ``z``;
- sphere-cylinder toy model: the cylinder and readout path axis is ``x``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np

DEFAULT_BOUNDARY_THICKNESS_UM = 0.05

ROLE_ORDER = (
    "far_field_control",
    "source_shell_candidate",
    "transit_readout_channel",
    "ordinary_em_competitor_region",
    "boundary_infrastructure",
    "stress_shaping_body",
)


def _point(point: object) -> np.ndarray:
    arr = np.asarray(point, dtype=float)
    if arr.shape != (3,):
        raise ValueError(f"expected a 3-vector point, got shape {arr.shape}")
    return arr


def make_xy_grid(
    x_min_um: float,
    x_max_um: float,
    y_min_um: float,
    y_max_um: float,
    nx: int,
    ny: int,
    z_um: float = 0.0,
) -> dict[str, np.ndarray]:
    xs = np.linspace(x_min_um, x_max_um, nx)
    ys = np.linspace(y_min_um, y_max_um, ny)
    x, y = np.meshgrid(xs, ys, indexing="xy")
    z = np.full_like(x, z_um, dtype=float)
    return {"x": x, "y": y, "z": z, "x_values": xs, "y_values": ys}


def _empty_roles(shape: tuple[int, ...]) -> dict[str, np.ndarray]:
    return {role: np.zeros(shape, dtype=bool) for role in ROLE_ORDER}


def _grid_half_step(grid: Mapping[str, np.ndarray]) -> float:
    steps: list[float] = []
    for key in ("x_values", "y_values"):
        if key in grid:
            values = np.asarray(grid[key], dtype=float)
            if values.size > 1:
                diffs = np.diff(values)
                positive = np.abs(diffs[diffs != 0.0])
                if positive.size:
                    steps.append(float(np.min(positive)))
    return 0.5 * min(steps) if steps else 0.0


@dataclass(frozen=True)
class CentralReadoutPath:
    length_um: float
    radius_um: float
    mode: str = "open_bore"
    conductor_radius_um: float = 0.0
    participates_as_casimir_boundary: bool = False
    axis: str = "x"

    def contains(self, point: object) -> bool:
        x, y, z = _point(point)
        radial = np.hypot(y, z)
        return abs(x) <= 0.5 * self.length_um and radial <= self.radius_um

    def mask(self, grid: Mapping[str, np.ndarray]) -> np.ndarray:
        x = grid["x"]
        y = grid["y"]
        z = grid["z"]
        radial = np.hypot(y, z)
        effective_radius = max(self.radius_um, _grid_half_step(grid))
        return (np.abs(x) <= 0.5 * self.length_um) & (radial <= effective_radius)


class SamplingIntersectionMixin:
    sample_step_um = 0.02

    def body_ids_for_points(self, points: object) -> np.ndarray:
        arr = np.asarray(points, dtype=float)
        flat = arr.reshape(-1, 3)
        ids = np.array([self.body_id(point) or 0 for point in flat], dtype=np.int16)
        return ids.reshape(arr.shape[:-1])

    def intersects_segment(self, p0: object, p1: object) -> set[int]:
        a = _point(p0)
        b = _point(p1)
        length = float(np.linalg.norm(b - a))
        n_samples = max(32, min(2048, int(np.ceil(length / self.sample_step_um)) + 1))
        hits: set[int] = set()
        for t in np.linspace(0.0, 1.0, n_samples):
            body = self.body_id(a + t * (b - a))
            if body is not None:
                hits.add(body)
        return hits

    def intersects_loop(self, points: object) -> set[int]:
        arr = np.asarray(points, dtype=float)
        if arr.ndim != 2 or arr.shape[1] != 3:
            raise ValueError("loop points must have shape (n_points, 3)")
        hits: set[int] = set()
        for idx in range(len(arr)):
            hits.update(self.intersects_segment(arr[idx], arr[(idx + 1) % len(arr)]))
        return hits


@dataclass(frozen=True)
class ParallelPlates(SamplingIntersectionMixin):
    gap_um: float
    width_um: float
    height_um: float
    thickness_um: float | None = None

    @property
    def effective_thickness_um(self) -> float:
        return self.thickness_um or DEFAULT_BOUNDARY_THICKNESS_UM

    def body_id(self, point: object) -> int | None:
        x, y, z = _point(point)
        if abs(x) > 0.5 * self.width_um or abs(z) > 0.5 * self.height_um:
            return None
        half_gap = 0.5 * self.gap_um
        half_t = 0.5 * self.effective_thickness_um
        if abs(y + half_gap) <= half_t:
            return 1
        if abs(y - half_gap) <= half_t:
            return 2
        return None

    def body_ids_for_points(self, points: object) -> np.ndarray:
        arr = np.asarray(points, dtype=float)
        x = arr[..., 0]
        y = arr[..., 1]
        z = arr[..., 2]
        ids = np.zeros(x.shape, dtype=np.int16)
        in_footprint = (np.abs(x) <= 0.5 * self.width_um) & (np.abs(z) <= 0.5 * self.height_um)
        half_gap = 0.5 * self.gap_um
        half_t = 0.5 * self.effective_thickness_um
        ids[in_footprint & (np.abs(y + half_gap) <= half_t)] = 1
        ids[in_footprint & (np.abs(y - half_gap) <= half_t)] = 2
        return ids

    def contains_body(self, point: object) -> bool:
        return self.body_id(point) is not None

    def role_regions(self, grid: Mapping[str, np.ndarray]) -> dict[str, np.ndarray]:
        x = grid["x"]
        y = grid["y"]
        z = grid["z"]
        roles = _empty_roles(x.shape)
        in_footprint = (np.abs(x) <= 0.5 * self.width_um) & (np.abs(z) <= 0.5 * self.height_um)
        half_gap = 0.5 * self.gap_um
        half_t = max(0.5 * self.effective_thickness_um, _grid_half_step(grid))
        lower = in_footprint & (np.abs(y + half_gap) <= half_t)
        upper = in_footprint & (np.abs(y - half_gap) <= half_t)
        interior = in_footprint & (np.abs(y) < half_gap) & ~(lower | upper)
        roles["boundary_infrastructure"] = lower | upper
        roles["source_shell_candidate"] = interior
        roles["ordinary_em_competitor_region"] = lower | upper
        roles["far_field_control"] = ~in_footprint | (np.abs(y) > half_gap + self.effective_thickness_um)
        return roles


@dataclass(frozen=True)
class PillarMidplaneCavity(SamplingIntersectionMixin):
    gap_um: float
    plate_width_um: float
    plate_height_um: float
    pillar_diameter_um: float
    pillar_axis: str = "z"
    thickness_um: float | None = None

    @property
    def pillar_radius_um(self) -> float:
        return 0.5 * self.pillar_diameter_um

    @property
    def effective_thickness_um(self) -> float:
        return self.thickness_um or DEFAULT_BOUNDARY_THICKNESS_UM

    def _plate_body_id(self, point: np.ndarray) -> int | None:
        return ParallelPlates(
            self.gap_um,
            self.plate_width_um,
            self.plate_height_um,
            self.effective_thickness_um,
        ).body_id(point)

    def body_id(self, point: object) -> int | None:
        p = _point(point)
        plate_id = self._plate_body_id(p)
        if plate_id is not None:
            return plate_id
        x, y, z = p
        if self.pillar_axis != "z":
            raise ValueError("first-phase pillar geometry only supports pillar_axis='z'")
        radial = np.hypot(x, y)
        if radial <= self.pillar_radius_um and abs(z) <= 0.5 * self.plate_height_um:
            return 3
        return None

    def body_ids_for_points(self, points: object) -> np.ndarray:
        arr = np.asarray(points, dtype=float)
        x = arr[..., 0]
        y = arr[..., 1]
        z = arr[..., 2]
        ids = np.zeros(x.shape, dtype=np.int16)
        in_footprint = (np.abs(x) <= 0.5 * self.plate_width_um) & (np.abs(z) <= 0.5 * self.plate_height_um)
        half_gap = 0.5 * self.gap_um
        half_t = 0.5 * self.effective_thickness_um
        ids[in_footprint & (np.abs(y + half_gap) <= half_t)] = 1
        ids[in_footprint & (np.abs(y - half_gap) <= half_t)] = 2
        radial = np.hypot(x, y)
        pillar = (radial <= self.pillar_radius_um) & (np.abs(z) <= 0.5 * self.plate_height_um)
        ids[pillar] = 3
        return ids

    def contains_body(self, point: object) -> bool:
        return self.body_id(point) is not None

    def role_regions(self, grid: Mapping[str, np.ndarray]) -> dict[str, np.ndarray]:
        x = grid["x"]
        y = grid["y"]
        z = grid["z"]
        roles = _empty_roles(x.shape)
        half_gap = 0.5 * self.gap_um
        half_t = max(0.5 * self.effective_thickness_um, _grid_half_step(grid))
        in_footprint = (np.abs(x) <= 0.5 * self.plate_width_um) & (np.abs(z) <= 0.5 * self.plate_height_um)
        lower = in_footprint & (np.abs(y + half_gap) <= half_t)
        upper = in_footprint & (np.abs(y - half_gap) <= half_t)
        radial = np.hypot(x, y)
        pillar = (radial <= self.pillar_radius_um) & (np.abs(z) <= 0.5 * self.plate_height_um)
        interior = in_footprint & (np.abs(y) < half_gap) & ~(lower | upper | pillar)
        near_pillar = interior & (radial <= max(1.5 * self.pillar_radius_um, self.pillar_radius_um + 0.25))
        roles["boundary_infrastructure"] = lower | upper
        roles["stress_shaping_body"] = pillar
        roles["source_shell_candidate"] = near_pillar
        roles["ordinary_em_competitor_region"] = lower | upper | pillar
        roles["transit_readout_channel"] = pillar & (radial <= min(self.pillar_radius_um, 0.1))
        roles["far_field_control"] = ~in_footprint | (np.abs(y) > half_gap + self.effective_thickness_um)
        return roles


@dataclass(frozen=True)
class SphereInCylinder(SamplingIntersectionMixin):
    sphere_diameter_um: float
    cylinder_diameter_um: float
    cylinder_length_um: float
    bore_radius_um: float = 0.0
    readout_path: CentralReadoutPath | None = None
    wall_thickness_um: float = DEFAULT_BOUNDARY_THICKNESS_UM
    sphere_offset_um: tuple[float, float, float] = (0.0, 0.0, 0.0)

    @property
    def sphere_radius_um(self) -> float:
        return 0.5 * self.sphere_diameter_um

    @property
    def cylinder_radius_um(self) -> float:
        return 0.5 * self.cylinder_diameter_um

    @property
    def active_readout_path(self) -> CentralReadoutPath:
        if self.readout_path is not None:
            return self.readout_path
        radius = self.bore_radius_um if self.bore_radius_um > 0.0 else 0.05
        return CentralReadoutPath(self.cylinder_length_um, radius)

    def body_id(self, point: object) -> int | None:
        p = _point(point)
        center = np.asarray(self.sphere_offset_um, dtype=float)
        if np.linalg.norm(p - center) <= self.sphere_radius_um:
            return 1
        x, y, z = p
        radial = np.hypot(y, z)
        half_len = 0.5 * self.cylinder_length_um
        half_wall = 0.5 * self.wall_thickness_um
        if abs(x) <= half_len and abs(radial - self.cylinder_radius_um) <= half_wall:
            return 2
        return None

    def body_ids_for_points(self, points: object) -> np.ndarray:
        arr = np.asarray(points, dtype=float)
        x = arr[..., 0]
        y = arr[..., 1]
        z = arr[..., 2]
        center = np.asarray(self.sphere_offset_um, dtype=float)
        sphere_radial = np.sqrt(
            (x - center[0]) ** 2 + (y - center[1]) ** 2 + (z - center[2]) ** 2
        )
        transverse = np.hypot(y, z)
        ids = np.zeros(x.shape, dtype=np.int16)
        ids[sphere_radial <= self.sphere_radius_um] = 1
        wall = (
            (np.abs(x) <= 0.5 * self.cylinder_length_um)
            & (np.abs(transverse - self.cylinder_radius_um) <= 0.5 * self.wall_thickness_um)
        )
        ids[wall] = 2
        return ids

    def contains_body(self, point: object) -> bool:
        return self.body_id(point) is not None

    def role_regions(self, grid: Mapping[str, np.ndarray]) -> dict[str, np.ndarray]:
        x = grid["x"]
        y = grid["y"]
        z = grid["z"]
        roles = _empty_roles(x.shape)
        ox, oy, oz = self.sphere_offset_um
        sphere_radial = np.sqrt((x - ox) ** 2 + (y - oy) ** 2 + (z - oz) ** 2)
        transverse = np.hypot(y, z)
        half_len = 0.5 * self.cylinder_length_um
        half_wall = max(0.5 * self.wall_thickness_um, _grid_half_step(grid))
        sphere = sphere_radial <= self.sphere_radius_um
        wall = (np.abs(x) <= half_len) & (np.abs(transverse - self.cylinder_radius_um) <= half_wall)
        interior = (np.abs(x) <= half_len) & (transverse < self.cylinder_radius_um) & ~sphere
        gap_shell = interior & (sphere_radial >= 0.85 * self.sphere_radius_um)
        readout = self.active_readout_path.mask(grid)
        roles["boundary_infrastructure"] = wall
        roles["stress_shaping_body"] = sphere
        roles["source_shell_candidate"] = gap_shell
        roles["transit_readout_channel"] = readout
        roles["ordinary_em_competitor_region"] = readout | wall
        roles["far_field_control"] = (np.abs(x) > half_len) | (transverse > self.cylinder_radius_um + self.wall_thickness_um)
        return roles


@dataclass(frozen=True)
class SphereOnlyControl(SamplingIntersectionMixin):
    sphere_diameter_um: float

    @property
    def sphere_radius_um(self) -> float:
        return 0.5 * self.sphere_diameter_um

    def body_id(self, point: object) -> int | None:
        return 1 if np.linalg.norm(_point(point)) <= self.sphere_radius_um else None

    def contains_body(self, point: object) -> bool:
        return self.body_id(point) is not None

    def role_regions(self, grid: Mapping[str, np.ndarray]) -> dict[str, np.ndarray]:
        x = grid["x"]
        roles = _empty_roles(x.shape)
        sphere = np.sqrt(grid["x"] ** 2 + grid["y"] ** 2 + grid["z"] ** 2) <= self.sphere_radius_um
        roles["stress_shaping_body"] = sphere
        roles["far_field_control"] = ~sphere
        return roles


@dataclass(frozen=True)
class CylinderOnlyControl(SphereInCylinder):
    def __init__(self, cylinder_diameter_um: float, cylinder_length_um: float):
        super().__init__(0.0, cylinder_diameter_um, cylinder_length_um)

    def body_id(self, point: object) -> int | None:
        x, y, z = _point(point)
        radial = np.hypot(y, z)
        if abs(x) <= 0.5 * self.cylinder_length_um and abs(radial - self.cylinder_radius_um) <= 0.5 * self.wall_thickness_um:
            return 2
        return None


@dataclass(frozen=True)
class EmptyBoreControl(SamplingIntersectionMixin):
    cylinder_length_um: float
    bore_radius_um: float

    def body_id(self, point: object) -> int | None:
        return None

    def contains_body(self, point: object) -> bool:
        return False

    def role_regions(self, grid: Mapping[str, np.ndarray]) -> dict[str, np.ndarray]:
        roles = _empty_roles(grid["x"].shape)
        readout = CentralReadoutPath(self.cylinder_length_um, self.bore_radius_um).mask(grid)
        roles["transit_readout_channel"] = readout
        roles["ordinary_em_competitor_region"] = readout
        roles["far_field_control"] = ~readout
        return roles


class OffsetSphereInCylinder(SphereInCylinder):
    def __init__(
        self,
        sphere_diameter_um: float,
        cylinder_diameter_um: float,
        cylinder_length_um: float,
        offset_um: float | tuple[float, float, float],
    ):
        if isinstance(offset_um, tuple):
            offset = offset_um
        else:
            offset = (0.0, float(offset_um), 0.0)
        super().__init__(sphere_diameter_um, cylinder_diameter_um, cylinder_length_um, sphere_offset_um=offset)


def role_counts(roles: Mapping[str, np.ndarray]) -> dict[str, int]:
    return {role: int(np.count_nonzero(mask)) for role, mask in roles.items()}
