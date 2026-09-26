#!/usr/bin/env python3
"""Minimize the null-energy deficit of the trimmed compartment carry over its layer widths and shapes; emit data only.

The deficit is the negative-null content, the integral of max(0, -min_k T(k, k)) over the pattern at one exterior
time, whose peak over the transit the closure pass trimmed from 333 to 252 at carry speed 2.1. At mid-lane it lies
in the lapse falls (radial, along the track, and the corners where they meet) and in the cone. In a shift-free
radial lapse fall the deficit along radial light integrates to a quarter of the log-lapse drop per unit length for
any width or profile, a floor; the rest follows the curvature of the lapse across the layer.

The screen varies one lever at a time about the trimmed reference: the widths of the along-track and radial falls,
the radial packing of the sheath and the outer fall, the edges of the shift and of the compartment's hole, the
flattened ends of the radial steps, and the cone's lapse, layer, rise and rounding. The shape stage reshapes the
outer falls, which lie where the shift vanishes: interpolation in the lapse in place of the log-lapse, an onset
warped toward the plateau, rounded corners where the radial and along-track falls meet, and the same for the cone.
Each variant's cone takes the base the closure pass used, the radius out to which the pattern's own lapse exceeds
the carry speed plus the cone's layer plus 0.8, so levers that widen the pattern lengthen the cone. The coarse gate of the trimming screen runs on
the pattern and the cone together, and a split at mid-lane records where the deficit lies and its floors. Each
row also counts the front-type light surfaces, where the lapse falls below |beta + v| going forward, at several
radii; one per radius means the cone's flank carries the only front. The combination stage joins the levers that
pay, and the full stage takes finalists through the full gate at 2.1, the tip rates, the swept energies and a
speed-10 gate. Narrative interpretation is maintained manually in
supporting_reports.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import copy
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_front_surface_pass as front_pass
import run_geometry_closure_pass as closure
from adm_harness import axial_track as ax
from adm_harness import front_surface as fs
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
BASE_SPEED = closure.BASE_SPEED
FAST_SPEED = 10.
CONE_MARGIN = .8
SPLIT_TIME = 3.75
VARIANTS = {
    "reference": {},
    "end_fall_3": {"service": {"fall_width": 3.}},
    "end_fall_4": {"service": {"fall_width": 4.}},
    "end_fall_6": {"service": {"fall_width": 6.}},
    "radial_fall_3": {"axial": {"sheath_fall": (8.75, 3.), "lapse_layer": (8.75, 3.)}},
    "radial_fall_4": {"axial": {"sheath_fall": (8.75, 4.), "lapse_layer": (8.75, 4.)}},
    "radial_fall_from_8p25": {"axial": {"sheath_rise": (3.75, 4.5), "sheath_fall": (8.25, 2.),
                                        "lapse_layer": (8.25, 2.)}},
    "radial_fall_3_from_8p25": {"axial": {"sheath_rise": (3.75, 4.5), "sheath_fall": (8.25, 3.),
                                          "lapse_layer": (8.25, 3.)}},
    "shift_edge_0p75": {"service": {"shift_width": .75}},
    "hole_edge_1p5": {"service": {"hole_edge": 1.5}},
    "hole_radial_edge_2": {"service": {"hole_radius": (1.75, 2.)}},
    "join_0p25": {"axial": {"join_fraction": .25}},
    "join_0p4": {"axial": {"join_fraction": .4}},
    "cone_lapse_1": {"cone": {"log_lapse": 1.}},
    "cone_lapse_1p25": {"cone": {"log_lapse": 1.25}},
    "cone_layer_4": {"cone": {"layer": 4.}},
    "cone_rise_3": {"cone": {"rise_width": 3.}},
    "cone_rounding_1": {"cone": {"rounding": 1.}},
}
ALPHA = {"pattern_space": "alpha"}
ROUND = {"pattern_corner": "round"}
SHAPES = {
    "alpha_falls": {"service": ALPHA},
    "alpha_falls_warp_0p5": {"service": {**ALPHA, "pattern_warp": .5}},
    "alpha_falls_warp_0p35": {"service": {**ALPHA, "pattern_warp": .35}},
    "round_corners": {"service": ROUND},
    "alpha_round": {"service": {**ALPHA, **ROUND}},
    "alpha_round_warp_0p5": {"service": {**ALPHA, **ROUND, "pattern_warp": .5}},
    "alpha_round_warp_0p5_fall_from_8p25": {"service": {**ALPHA, **ROUND, "pattern_warp": .5},
                                            "axial": {"sheath_fall": (8.25, 2.), "lapse_layer": (8.25, 2.)}},
    "alpha_round_warp_0p5_end_fall_3": {"service": {**ALPHA, **ROUND, "pattern_warp": .5, "fall_width": 3.}},
    "cone_alpha": {"cone": {"space": "alpha"}},
    "cone_alpha_warp_0p5": {"cone": {"space": "alpha", "warp": .5}},
    "alpha_round_warp_0p5_cone_alpha_warp_0p5": {"service": {**ALPHA, **ROUND, "pattern_warp": .5},
                                                 "cone": {"space": "alpha", "warp": .5}},
}
WARPS = {**ALPHA, "pattern_warp": .35, "pattern_radial_warp": .5}
FALL_8P25 = {"sheath_fall": (8.25, 2.), "lapse_layer": (8.25, 2.)}
CONE = {"log_lapse": 1., "rise_width": 3.}
COMBINATIONS = {
    "warps": {"service": WARPS},
    "warps_fall_8p25": {"service": WARPS, "axial": FALL_8P25},
    "warps_fall_8p25_cone": {"service": WARPS, "axial": FALL_8P25, "cone": CONE},
    "warps_fall_8p25_cone_alpha": {"service": WARPS, "axial": FALL_8P25,
                                   "cone": {**CONE, "space": "alpha", "warp": .5}},
    "warps_radial_1_fall_8p25_cone": {"service": {**WARPS, "pattern_radial_warp": 1.}, "axial": FALL_8P25,
                                      "cone": CONE},
    "warps_fall_7p75_cone": {"service": WARPS, "axial": {"sheath_fall": (7.75, 2.), "lapse_layer": (7.75, 2.)},
                             "cone": CONE},
    "warps_fall_8p25_cone_shift_0p75": {"service": {**WARPS, "shift_width": .75}, "axial": FALL_8P25, "cone": CONE},
    "warps_fall_8p25_cone_end_3": {"service": {**WARPS, "fall_width": 3.}, "axial": FALL_8P25, "cone": CONE},
    "warps_fall_8p25_cone_hole_1p5": {"service": {**WARPS, "hole_edge": 1.5}, "axial": FALL_8P25, "cone": CONE},
}
MIXED_FALLS = {"pattern_space": "mixed", "pattern_warp": .35, "pattern_radial_warp": 1.}
MIXED = {
    "mixed_shift_0p75_cone_1": {"service": {**MIXED_FALLS, "shift_width": .75}, "cone": {"log_lapse": 1.}},
    "mixed_fall_8p25_shift_0p75_cone_1": {"service": {**MIXED_FALLS, "shift_width": .75}, "axial": FALL_8P25,
                                          "cone": {"log_lapse": 1.}},
    "mixed_radial_warp_0p7_fall_8p25_shift_0p75_cone_1": {
        "service": {**MIXED_FALLS, "pattern_radial_warp": .7, "shift_width": .75}, "axial": FALL_8P25,
        "cone": {"log_lapse": 1.}},
    "mixed_fall_8p25_shift_0p75_cone_1_alpha": {"service": {**MIXED_FALLS, "shift_width": .75}, "axial": FALL_8P25,
                                                "cone": {"log_lapse": 1., "space": "alpha", "warp": .5}},
    "mixed_fall_8p25_shift_0p75_cone_1_rise_2": {"service": {**MIXED_FALLS, "shift_width": .75}, "axial": FALL_8P25,
                                                 "cone": {"log_lapse": 1., "rise_width": 2.}},
    "mixed_warp_0p5_fall_8p25_shift_0p75_cone_1": {"service": {**MIXED_FALLS, "pattern_warp": .5, "shift_width": .75},
                                                   "axial": FALL_8P25, "cone": {"log_lapse": 1.}},
    "mixed_fall_8p25_cone_1": {"service": MIXED_FALLS, "axial": FALL_8P25, "cone": {"log_lapse": 1.}},
    "mixed_fall_8p25_shift_0p75_cone_1p25": {"service": {**MIXED_FALLS, "shift_width": .75}, "axial": FALL_8P25,
                                             "cone": {"log_lapse": 1.25}},
}
FINALISTS = ("warps_fall_8p25_cone_shift_0p75", "warps_fall_8p25_cone", "mixed_fall_8p25_shift_0p75_cone_1_rise_2")
LIGHT_RADII = (0., 1., 2., 4., 6., 8., 9., 10., 11.)
FRONT_RADII = tuple(np.arange(.5, 14.01, .5))
FRONT_SPEEDS = (1.5, 2.1, 3., 5., 7., 10., 15., 20.)


def variant_spec(changes):
    """The trimmed reference with changes applied and the cone's base set by the pattern's lapse radius."""
    spec = copy.deepcopy(closure.TRIM_SCALED)
    for part, update in changes.items():
        spec[part].update(update)
    radius = closure.alpha_v_radius(spec, BASE_SPEED)
    layer = spec["cone"].get("layer", fs.ConeFront.layer)
    spec["cone"]["base_radius"] = math.ceil((radius+layer+CONE_MARGIN)/.25-1e-9)*.25
    return spec, radius


def all_variants():
    return {**VARIANTS, **SHAPES, **COMBINATIONS, **MIXED}


def sizes(spec, speed=BASE_SPEED):
    service, design, cone = closure.build_spec(spec, speed)
    start, width = design.layers["alpha"]
    return {"extent": service.extent, "outer_radius": start+width, "cone_base": cone.base_radius,
            "cone_tip": cone.tip(service), "cone_half_angle": cone.half_angle}


def light_surfaces(spec, speed=BASE_SPEED, s=SPLIT_TIME):
    """Front-type crossings of alpha = |beta + v| along the track at each radius: one each marks a single front."""
    service, design, cone = closure.build_spec(spec, speed)
    centre, v = service.packet_position(s), service.carry_speed(s)
    zeta = np.arange(-service.extent-1., cone.tip(service)+2., .01)
    counts = []
    for r in LIGHT_RADII:
        log_alpha, beta = fs.log_lapse_and_shift(service, design, cone, s, centre+zeta, np.full(zeta.shape, r))
        above = np.exp(log_alpha) > np.abs(beta+v)
        counts.append(int(np.sum(above[:-1] & ~above[1:])))
    return {"front_surfaces_max": max(counts), "front_surfaces_min": min(counts)}


def front_speed(spec, speed, s=SPLIT_TIME):
    """Fastest normal speed v |n_z| of the front light surface off the axis, where alpha falls below |beta + v|.

    A piece that advances along its normal faster than light traps what the pattern overtakes; the cone's flank
    advances at 0.54 by construction. The axis at the tip, the one null point, is left to the tip rates.
    """
    service, design, cone = closure.build_spec(spec, speed)
    centre, v = service.packet_position(s), service.carry_speed(s)
    zeta = np.arange(-service.extent-1., cone.tip(service)+2., .005)

    def excess(z, r):
        log_alpha, beta = fs.log_lapse_and_shift(service, design, cone, s, np.array([centre+z]), np.array([r]))
        return float(np.exp(log_alpha[0])-abs(beta[0]+v))
    worst, h = 0., 1e-3
    for r in FRONT_RADII:
        log_alpha, beta = fs.log_lapse_and_shift(service, design, cone, s, centre+zeta, np.full(zeta.shape, r))
        above = np.exp(log_alpha) > np.abs(beta+v)
        for i in np.flatnonzero(above[:-1] & ~above[1:]):
            dz = (excess(zeta[i]+h, r)-excess(zeta[i]-h, r))/(2*h)
            dr = (excess(zeta[i], r+h)-excess(zeta[i], r-h))/(2*h)
            worst = max(worst, v*abs(dz)/math.hypot(dz, dr))
    return worst


def front_task(task):
    name, spec, speed = task
    return name, speed, front_speed(spec, speed)


def deficit_split(task):
    """Deficit at one exterior time by region, with the radial-light floors of the radial fall and the cone."""
    name, spec, speed, s = task
    service, design, cone = closure.build_spec(spec, speed)
    radius, area = front_pass.radial_nodes(service, design, cone)
    centre = service.packet_position(s)
    start, width = design.layers["alpha"]
    tip = cone.tip(service)
    offsets = np.concatenate([np.arange(-service.extent-1., service.extent+1., .05),
                              np.arange(service.extent+1., tip+2., .1)])
    lengths = np.gradient(offsets)
    names = ("radial_fall", "end_falls", "corners", "interior", "cone", "rest")
    content = dict.fromkeys(names, 0.)
    floor = {"radial_fall": 0., "cone": 0.}
    for zeta, length in zip(offsets, lengths):
        tensor = fs.frame_tensor(service, design, cone, s, centre+zeta, radius)
        deficit = area*np.maximum(-ax.min_null_energy(tensor), 0.)*length
        radial_light = area*np.maximum(-tensor[:, 2, 2], 0.)*length
        u = abs(zeta)
        outer = radius >= start-.25
        if zeta > service.extent+1.:
            regions = {"cone": np.ones_like(radius, bool)}
        elif u > service.extent:
            regions = {"rest": np.ones_like(radius, bool)}
        elif u > service.fall_start:
            regions = {"corners": outer, "end_falls": ~outer}
        else:
            regions = {"radial_fall": outer & (radius <= start+width+.25), "interior": ~outer,
                       "rest": radius > start+width+.25}
        for region, mask in regions.items():
            content[region] += float(deficit[mask].sum())
        if "radial_fall" in regions:
            floor["radial_fall"] += float(radial_light[regions["radial_fall"]].sum())
        if "cone" in regions:
            floor["cone"] += float(radial_light.sum())
    log_alpha, _ = fs.log_lapse_and_shift(service, design, cone, s, np.full(2, centre), np.array([start-.3, start+width+.3]))
    return {"variant": name, "speed": speed, "s": s, "total": sum(content.values()),
            **{f"content_{k}": v for k, v in content.items()},
            "floor_radial_fall": floor["radial_fall"], "floor_cone": floor["cone"],
            "radial_log_lapse_drop": float(log_alpha[0]-log_alpha[1]),
            "analytic_radial_floor": float((log_alpha[0]-log_alpha[1])/4*2*service.fall_start)}


def screen(pool, names, speed, started, output, label, front_speeds=False):
    table = all_variants()
    specs = {name: variant_spec(table[name]) for name in names}
    splits = [pool.submit(deficit_split, (name, spec, speed, SPLIT_TIME)) for name, (spec, _) in specs.items()]
    fronts = [pool.submit(front_task, (name, spec, v)) for name, (spec, _) in specs.items() for v in FRONT_SPEEDS] \
        if front_speeds else []
    rows = []
    for name, (spec, radius) in specs.items():
        checks, demand, _ = closure.gate_and_demand(pool, spec, speed, with_cone=True, sigma_step=.5, pattern_step=.2,
                                                    front_step=.5, refine=False, resolve_bands=False)
        row = {"variant": name, "speed": speed, "alpha_v_radius": radius, **sizes(spec, speed),
               **light_surfaces(spec, speed), **demand,
               **{f"pattern_{k}": v for k, v in checks["pattern"].items()},
               **{f"front_{k}": v for k, v in checks["front"].items()}}
        rows.append(row)
        pd.DataFrame(rows).to_csv(output/f"{label}.csv", index=False)
        print(label, json.dumps({k: row[k] for k in ("variant", "peak_nec_content", "peak_stress", "pattern_type_iv",
                                                      "front_type_iv", "pattern_other", "pattern_worst_envelope_ratio",
                                                      "cone_base", "cone_tip", "front_surfaces_max")}),
              round(time.time()-started, 1), flush=True)
    split = pd.DataFrame([f.result() for f in splits])
    split.to_csv(output/f"{label}_split.csv", index=False)
    print(split.to_string(index=False), flush=True)
    if fronts:
        table = pd.DataFrame([f.result() for f in fronts], columns=["variant", "speed", "front_normal_speed"])
        table = table.pivot(index="variant", columns="speed", values="front_normal_speed").reset_index()
        table.to_csv(output/f"{label}_front_speeds.csv", index=False)
        print(table.to_string(index=False), flush=True)
    return rows, split


def full(pool, name, started, output):
    spec, radius = variant_spec(all_variants()[name])
    gz = {"method": "gzip", "mtime": 0}
    checks, demand, gate = closure.gate_and_demand(pool, spec, BASE_SPEED)
    gate.to_csv(output/f"gate_samples_{name}.csv.gz", index=False, compression=gz, float_format="%.7g")
    rates = closure.tip_rates(spec, BASE_SPEED)
    swept = pd.DataFrame([r for chunk in pool.map(closure.swept, closure.swept_tasks(spec, BASE_SPEED, (6., 12.), 12))
                          for r in chunk])
    swept.to_csv(output/f"swept_{name}.csv.gz", index=False, compression=gz, float_format="%.9g")
    fast_checks, fast_demand, _ = closure.gate_and_demand(pool, spec, FAST_SPEED, sigma_step=.25, pattern_step=.1,
                                                          front_step=.25, refine=False, resolve_bands=False)
    record = {"variant": name, "spec": spec, "alpha_v_radius": radius, "sizes": sizes(spec), "checks": checks,
              "demand": demand, "tip_rates": rates, "passenger": closure.passenger(spec, BASE_SPEED),
              "swept": swept.groupby(["decel", "kind"]).final_energy.agg(["max", "median"]).reset_index()
              .to_dict("records"),
              "light_surfaces": light_surfaces(spec), "light_surfaces_10": light_surfaces(spec, FAST_SPEED),
              "front_normal_speed": {str(v): front_speed(spec, v) for v in FRONT_SPEEDS},
              "speed_10": {"alpha_v_radius": closure.alpha_v_radius(spec, FAST_SPEED), "sizes": sizes(spec, FAST_SPEED),
                           "checks": fast_checks, "demand": fast_demand,
                           "tip_rates": closure.tip_rates(spec, FAST_SPEED)},
              "split_2p1": deficit_split((name, spec, BASE_SPEED, SPLIT_TIME)),
              "split_10": deficit_split((name, spec, FAST_SPEED, SPLIT_TIME))}
    print("full", json.dumps(record, default=str), round(time.time()-started, 1), flush=True)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/deficit_minimization_pass")
    parser.add_argument("--stages", default="screen,shapes,combine,full")
    parser.add_argument("--speed", type=float, default=BASE_SPEED)
    parser.add_argument("--finalists", default=",".join(FINALISTS))
    args = parser.parse_args()
    stages = set(args.stages.split(","))
    started = time.time()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest_path = args.output/"manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    pd.set_option("display.width", 250)
    suffix = "" if args.speed == BASE_SPEED else f"_{args.speed:g}"
    with ProcessPoolExecutor(args.workers) as pool:
        if "screen" in stages:
            screen(pool, list(VARIANTS), args.speed, started, args.output, f"screen{suffix}")
        if "shapes" in stages:
            screen(pool, list(SHAPES), args.speed, started, args.output, f"shapes{suffix}")
        if "combine" in stages and COMBINATIONS:
            screen(pool, list(COMBINATIONS), args.speed, started, args.output, f"combinations{suffix}")
        if "fronts" in stages:
            table = all_variants()
            names = list(COMBINATIONS)
            jobs = [pool.submit(front_task, (name, variant_spec(table[name])[0], v)) for name in names
                    for v in FRONT_SPEEDS]
            fronts = pd.DataFrame([f.result() for f in jobs], columns=["variant", "speed", "front_normal_speed"])
            fronts.pivot(index="variant", columns="speed", values="front_normal_speed").reset_index().to_csv(
                args.output/"combinations_front_speeds.csv", index=False)
        if "mixed" in stages:
            screen(pool, list(MIXED), args.speed, started, args.output, f"mixed{suffix}", front_speeds=True)
        if "full" in stages:
            for name in args.finalists.split(","):
                manifest.setdefault("finalists", {})[name] = full(pool, name, started, args.output)
                manifest_path.write_text(json.dumps(manifest, indent=1, default=str)+"\n")
    hashes = {path: sha256_file(ROOT/"toolkit/adm_harness_cli"/path) for path in (
        "adm_harness/compartment_service.py", "adm_harness/front_surface.py", "adm_harness/axial_track.py",
        "scripts/run_geometry_closure_pass.py", "scripts/run_deficit_minimization_pass.py")}
    manifest.setdefault("stage_software_sha256", {}).update({f"{stage}{suffix}": hashes for stage in stages})
    manifest.update({"variants": VARIANTS, "shapes": SHAPES, "combinations": COMBINATIONS, "mixed": MIXED,
                     "front_radii": FRONT_RADII, "front_speeds": FRONT_SPEEDS,
                     "finalists": manifest.get("finalists", {}),
                     "cone_margin": CONE_MARGIN, "split_time": SPLIT_TIME, "trim": closure.TRIM_SCALED,
                     f"elapsed_{'_'.join(sorted(stages))}{suffix}": round(time.time()-started, 1),
                     "software_sha256": hashes})
    manifest_path.write_text(json.dumps(manifest, indent=1, default=str)+"\n")


if __name__ == "__main__":
    main()
