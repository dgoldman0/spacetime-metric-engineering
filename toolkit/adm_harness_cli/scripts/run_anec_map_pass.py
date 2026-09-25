#!/usr/bin/env python3
"""Averaged null energy along complete light rays through the trimmed compartment carry; emit data only.

The ANEC integral of a null geodesic is the integral of T(k, k) over its affine parameter. With sigma as the
parameter of the meridional tracer, d lambda = alpha d sigma/|k| and T(k, k) = |k|^2 T(e, e), where e = n + k/|k| in
the normal observers' frame, so the integrand is alpha |k| T(e, e) d sigma. Each ray here starts and ends in flat
space before the structure switches on and after it switches off, so its integral runs over the whole geodesic,
with k normalized to unit energy at the start.

The departure fan leaves the packet at the start of the carry in directions from straight ahead to straight back.
Traced in both directions, these rays are complete, and the first to reach a plane just past the packet's arrival
lies on the boundary of the departure event's causal future, which makes it achronal. The long lane lets the
first ray reach the cone's tip and ride it. The crossing families send light
through the pattern at mid-lane: from ahead against the pattern, from ahead along the axis where the pattern
overtakes it, inward from the side, and forward from behind. The run records each ray's integral, split by the
region it crosses, its arrival at the far plane, and the same quantities on a lane twice as long. Narrative
interpretation is maintained manually in supporting_reports.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_geometry_closure_pass as closure
from adm_harness import front_surface as fs
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
SAMPLE = .004
SPEEDS = (2.1, 10.)
DECELS = (6., 30.)
DEPARTURE_ANGLES = (0., .5, 1., 2., 5., 10., 20., 45., 90., 135., 180.)
REGIONS = ("compartment", "hole_boundary", "shift_region", "pattern_lapse", "cone", "flat")


def region(service, cone, s, z, r):
    """Region of a point: compartment, hole boundary, the shift's extent, the rest of the pattern, cone, or flat."""
    zeta, r = z-service.packet_position(s), abs(r)
    if service.schedule_value(s) == 0.:
        return "flat"
    shift_end = service.shift_start+service.shift_width
    if abs(zeta) <= service.half_width and r <= service.hole_radius[0]:
        return "compartment"
    if abs(zeta) <= service.half_width+service.hole_edge and r <= sum(service.hole_radius):
        return "hole_boundary"
    if abs(zeta) <= shift_end and r <= 6.25:
        return "shift_region"
    if -service.extent-.5 <= zeta <= service.extent+.5 and r <= 12.:
        return "pattern_lapse"
    if cone is not None and service.extent < zeta <= cone.tip(service)+1. and r <= cone.base_radius+cone.layer+1.:
        return "cone"
    return "flat"


def trace_dense(service, design, cone, span, z0, r0, k0):
    """Adaptive meridional null ray with dense output."""
    def rhs(s, y):
        return fs._rates(service, design, cone, s, np.asarray(y, dtype=float)[:, None], 0., 1e-5)[:, 0]
    return solve_ivp(rhs, span, [z0, r0, *k0], method="DOP853", rtol=1e-9, atol=1e-11, max_step=.01,
                     dense_output=True)


def anec(service, design, cone, z_launch, r_launch, s_launch, k_launch, far_plane):
    """Complete ray through (s_launch, z, r) with covariant spatial momentum k_launch: ANEC by region and arrival."""
    start, end = -3., service.path[7]+service.path[8]+12.
    back = trace_dense(service, design, cone, (s_launch, start), z_launch, r_launch, k_launch)
    ahead = trace_dense(service, design, cone, (s_launch, end), z_launch, r_launch, k_launch)
    k_start = np.hypot(back.y[2, -1], back.y[3, -1])
    grid = np.arange(start, end+SAMPLE/2, SAMPLE)
    y = np.where(grid[:, None] <= s_launch, back.sol(np.minimum(grid, s_launch)).T, ahead.sol(np.maximum(grid, s_launch)).T)
    sums = dict.fromkeys(REGIONS, 0.)
    cumulative, lowest, integrand_min = 0., 0., 0.
    for s, (z, x, kz, kx) in zip(grid, y):
        kn = math.hypot(kz, kx)/k_start
        e = np.array([1., kz/math.hypot(kz, kx), (1. if x >= 0 else -1.)*kx/math.hypot(kz, kx), 0.])
        log_alpha, _ = fs.log_lapse_and_shift(service, design, cone, s, np.array([z]), np.array([abs(x)]))
        if abs(log_alpha[0]) < 1e-12 and service.schedule_value(s) == 0.:
            value = 0.
        else:
            tensor = fs.frame_tensor(service, design, cone, s, z, [max(abs(x), 1e-3)])[0]
            value = math.exp(log_alpha[0])*kn*float(e@tensor@e)
        piece = value*SAMPLE
        sums[region(service, cone, s, z, x)] += piece
        cumulative += piece
        lowest = min(lowest, cumulative)
        integrand_min = min(integrand_min, value)
    z_end = y[:, 0]
    crossed = np.flatnonzero(z_end >= far_plane)
    arrival = float(grid[crossed[0]]) if len(crossed) else math.nan
    return {"anec": sum(sums.values()), **{f"anec_{k}": v for k, v in sums.items()}, "lowest_partial": lowest,
            "most_negative_integrand": integrand_min, "far_plane_arrival": arrival,
            "final_energy": float(math.hypot(*y[-1, 2:]))/k_start}


def task_rows(task):
    family, speed, decel, label, s0, zeta0, r0, angle = task
    service, design, cone = closure.build_spec(closure.TRIM_SCALED, speed, decel)
    final = service.packet_position(decel+1.5)
    far_plane = final+2.
    z0 = service.packet_position(s0)+zeta0
    result = anec(service, design, cone, z0, r0, s0, (math.cos(angle), math.sin(angle)), far_plane)
    depart = service.packet_position(0.)
    return {"family": family, "speed": speed, "decel": decel, "label": label, "launch": s0, "zeta0": zeta0, "r0": r0,
            "angle_deg": math.degrees(angle), "far_plane": far_plane,
            "exterior_light_arrival": far_plane-depart if family == "departure" else math.nan, **result}


def tasks():
    out = []
    for speed in SPEEDS:
        for decel in DECELS:
            for angle in DEPARTURE_ANGLES:
                out.append(("departure", speed, decel, f"departure_{angle:g}", 0., 0., 0., math.radians(angle)))
            service, _, cone = closure.build_spec(closure.TRIM_SCALED, speed, decel)
            tip = cone.tip(service)
            lead = 13.*speed
            crossing = [("against_axis", 3., tip+4., 0., math.pi), ("against_r3", 3., tip+4., 3., math.pi),
                        ("overtaken_axis", 3., tip+4., 0., 0.), ("overtaken_r1", 3., tip+4., 1., 0.),
                        ("overtaken_r6", 3., tip+4., 6., 0.), ("side_at_packet", 3., lead, 13., -math.pi/2),
                        ("side_at_shift", 3., 3.+lead, 13., -math.pi/2),
                        ("side_at_cone", 3., .5*tip+8.*speed, 13., -math.pi/2), ("behind_forward", 3., -20., 0., 0.)]
            for label, s0, zeta0, r0, angle in crossing:
                out.append(("crossing", speed, decel, label, s0, zeta0, r0, angle))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/anec_map_pass")
    args = parser.parse_args()
    started = time.time()
    args.output.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(args.workers) as pool:
        frame = pd.DataFrame(list(pool.map(task_rows, tasks())))
    frame.to_csv(args.output/"anec_rays.csv", index=False)
    pd.set_option("display.width", 250)
    print(frame[["family", "speed", "decel", "label", "anec", "anec_compartment", "anec_shift_region",
                 "anec_pattern_lapse", "anec_cone", "far_plane_arrival", "exterior_light_arrival"]].to_string(
        index=False, float_format=lambda x: f"{x:.4g}"), flush=True)
    manifest = {"sample": SAMPLE, "speeds": SPEEDS, "decels": DECELS, "departure_angles": DEPARTURE_ANGLES,
                "trim": closure.TRIM_SCALED, "elapsed_seconds": round(time.time()-started, 1),
                "software_sha256": {path: sha256_file(ROOT/"toolkit/adm_harness_cli"/path) for path in (
                    "adm_harness/front_surface.py", "scripts/run_geometry_closure_pass.py",
                    "scripts/run_anec_map_pass.py")}}
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=1, default=str)+"\n")


if __name__ == "__main__":
    main()
