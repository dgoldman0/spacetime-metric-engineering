#!/usr/bin/env python3
"""Close the geometry of the compartment carry with the conical front; emit data only.

Four stages. The trimming screen applies a coarse gate and the demand census to variants of the compartment's lapse
structure: plateau height, shift-edge width, and the radial extent of the sheath and plateau. The reference stage
gives the adopted trimmed design, with a cone sized to its radius, the full gate, the census, the tip rates and the
swept-object audit. The speed scan raises the lane speed from 1.5 to 20. It scales the plateau and cone lapse by
the speed, which leaves the geometry around the shift the same up to a rescaling of time, and repeats the screen,
census, tip rates, swept objects and passenger figures. The path audits trace light in three dimensions through the
reference at 2.1 and 10. Escape follows light from the compartment outward and records when it leaves the
structure. Reachability traces light arriving at the compartment back to its origin. Bundles follow fans of
neighbouring rays for crossings and collapse. Narrative interpretation is maintained manually in supporting_reports.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd
from scipy.optimize import brentq

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_choreography_pass as choreography
import run_demand_census as census
import run_front_surface_pass as front_pass
from adm_harness import axial_track as ax
from adm_harness import compartment_service as cs
from adm_harness import front_surface as fs
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
BASE_SPEED = 2.1
TRIM = dict(service=dict(plateau_log=3., shift_width=1.), axial=dict(sheath_fall=(8.75, 2.), lapse_layer=(8.75, 2.)),
            cone=dict(base_radius=14.))
FLANK_SPEED = BASE_SPEED*math.sin(math.radians(15.))
TRIM_SCALED = dict(service=TRIM["service"], axial=TRIM["axial"], cone=dict(base_radius=14., flank_speed=FLANK_SPEED))
TRIM_SCREEN = {
    "previous_reference": ({}, {}),
    "plateau_e3": (dict(plateau_log=3.), {}),
    "shift_edge_1": (dict(shift_width=1.), {}),
    "outer_fall_8p75": ({}, dict(sheath_fall=(8.75, 2.), lapse_layer=(8.75, 2.))),
    "rise_4p5_fall_8p25": ({}, dict(sheath_rise=(3.75, 4.5), sheath_fall=(8.25, 2.), lapse_layer=(8.25, 2.))),
    "rise_4_fall_7p75": ({}, dict(sheath_rise=(3.75, 4.), sheath_fall=(7.75, 2.), lapse_layer=(7.75, 2.))),
    "rise_3_fall_7p25": ({}, dict(sheath_rise=(3.75, 3.), sheath_fall=(7.25, 2.5), lapse_layer=(7.25, 2.5))),
    "e3_fall_8p75": (dict(plateau_log=3.), dict(sheath_fall=(8.75, 2.), lapse_layer=(8.75, 2.))),
    "e3_fall_8p75_edge1": (dict(plateau_log=3., shift_width=1.), dict(sheath_fall=(8.75, 2.), lapse_layer=(8.75, 2.))),
    "e3_fall_8p75_edge0p75": (dict(plateau_log=3., shift_width=.75), dict(sheath_fall=(8.75, 2.), lapse_layer=(8.75, 2.))),
    "e2p5_fall_8p75_edge1": (dict(plateau_log=2.5, shift_width=1.), dict(sheath_fall=(8.75, 2.), lapse_layer=(8.75, 2.))),
    "e3_fall_8p75_edge1_sheath0p5": (dict(plateau_log=3., shift_width=1.),
                                     dict(sheath_log_lapse=.5, sheath_fall=(8.75, 2.), lapse_layer=(8.75, 2.))),
}
SPEEDS = (1.5, 2.1, 3., 5., 10., 20.)
AUDIT_SPEEDS = (2.1, 10.)
AUDIT_DECEL = 12.
LAUNCH_RADII = (.05, .5, 2., 5., 8., 11.)
SIGMA_RANGE = (-3.5, 10.)
PER_PANEL = front_pass.PER_PANEL
NOISE_FLOOR = choreography.NOISE_FLOOR


def build_spec(spec, speed=BASE_SPEED, decel=6., jet_step=choreography.JET_STEP, with_cone=True):
    """Service, axial design and cone for a design spec at a lane speed; plateau and cone lapse scale with speed."""
    scale = math.log(speed/BASE_SPEED)
    skw = dict(spec["service"])
    skw["plateau_log"] = skw.get("plateau_log", 4.)+scale
    service = cs.CompartmentService(path=(-1., 0., 0., speed, 0., 0., 1.5, decel, 1.5),
                                    schedule=(-2.5, decel+3., 1.), **skw)
    design = cs.axial_design(service, jet_step=jet_step, **spec["axial"])
    cone = None
    if with_cone:
        ckw = dict(spec["cone"])
        ckw["log_lapse"] = ckw.get("log_lapse", 1.5)+scale
        flank = ckw.pop("flank_speed", None)
        if flank is not None:
            ckw["half_angle"] = math.degrees(math.asin(flank/speed))
        cone = fs.ConeFront(**ckw)
    return service, design, cone


def screen_spec(name):
    skw, akw = TRIM_SCREEN[name]
    return dict(service=skw, axial=akw, cone={})


# Gate rows and census, shared by every stage

def gate_row(task):
    """Node types, band estimates and demand sums at one sigma over offsets, for a spec at a speed."""
    spec, speed, with_cone, s, offsets, jet_step, per_panel, with_census = task
    service, design, cone = build_spec(spec, speed, jet_step=jet_step, with_cone=with_cone)
    radius, area = front_pass.radial_nodes(service, design, cone, per_panel)
    centre = service.packet_position(s)
    rows = []
    for offset in offsets:
        z = centre+float(offset)
        f = fs.fields(service, design, cone, s, z, radius)
        tensor = ax.tensor_from_fields(f, radius, design, product_core=False)
        kinds = ax.classify(tensor, floor=NOISE_FLOOR)["type"]
        null = ax.min_null_energy(tensor)
        row = {"s": s, "offset": float(offset), "type_i": int((kinds == ax.TYPE_I).sum()),
               "type_iv": int((kinds == ax.TYPE_IV).sum()),
               "other": int(np.isin(kinds, [ax.UNRESOLVED, ax.TYPE_II_III]).sum()), "min_null": float(null.min()),
               "estimated_band_width": choreography.band_widths(tensor, radius),
               "envelope_ratio": float(2*design.core_radius*abs(f["beta_z"][0])/f["alpha"][0]),
               "max_abs_component": float(np.max(np.abs(tensor))), "max_alpha": float(f["alpha"].max())}
        if with_census:
            point = census.point_census(tensor, f, area, area)
            row.update({"nec_content": float(np.sum(area*np.maximum(-null, 0))),
                        "negative_energy": float(np.sum(area*np.minimum(tensor[:, 0, 0], 0))),
                        "positive_energy": float(np.sum(area*np.maximum(tensor[:, 0, 0], 0))),
                        "type_i_volume": float(area[point["type_i"]].sum())})
        rows.append(row)
    return rows


def windows(spec, speed, with_cone, sigma_step, pattern_step, front_step):
    service, _, cone = build_spec(spec, speed, with_cone=with_cone)
    sigma = np.round(np.arange(SIGMA_RANGE[0], SIGMA_RANGE[1]+sigma_step/2, sigma_step), 10)
    edge = service.extent+1.
    out = [("pattern", sigma, np.round(np.arange(-edge, edge+pattern_step/2, pattern_step), 10), pattern_step)]
    if cone is not None:
        out.append(("front", sigma[::max(1, round(.25/sigma_step))],
                    np.round(np.arange(edge+front_step, cone.tip(service)+2.+1e-9, front_step), 10), front_step))
    return out


def gate_and_demand(pool, spec, speed, with_cone=True, sigma_step=.1, pattern_step=.1, front_step=.25,
                    refine=True, resolve_bands=True):
    checks, sums, frames = {}, {}, []
    for label, sigma, offsets, step in windows(spec, speed, with_cone, sigma_step, pattern_step, front_step):
        gate = pd.DataFrame([r for chunk in pool.map(gate_row, [(spec, speed, with_cone, float(s), offsets,
                                                                  choreography.JET_STEP, PER_PANEL, True)
                                                                 for s in sigma], chunksize=2) for r in chunk])
        gate.insert(0, "window", label)
        frames.append(gate)
        entry = {"samples": len(gate), "type_i": int(gate.type_i.sum()), "type_iv": int(gate.type_iv.sum()),
                 "other": int(gate.other.sum()), "estimated_band_samples": int((gate.estimated_band_width > 0).sum()),
                 "envelope_violations": int((gate.envelope_ratio > 1).sum()),
                 "worst_envelope_ratio": float(gate.envelope_ratio.max()), "min_null": float(gate.min_null.min())}
        if refine:
            refined = pd.DataFrame([r for chunk in pool.map(gate_row, [
                (spec, speed, with_cone, float(s), offsets, choreography.JET_STEP/2, 2*PER_PANEL, False)
                for s in sigma[::2]], chunksize=2) for r in chunk])
            entry.update({"refined_samples": len(refined), "refined_type_i": int(refined.type_i.sum()),
                          "refined_type_iv": int(refined.type_iv.sum()), "refined_other": int(refined.other.sum())})
        if resolve_bands and label == "pattern":
            top = gate.nlargest(choreography.RESOLVED_SAMPLES, "estimated_band_width")
            top = top[top.estimated_band_width > 0]
            service, _, _ = build_spec(spec, speed, with_cone=with_cone)
            bands = list(pool.map(resolve, [(spec, speed, with_cone, float(r.s),
                                             service.packet_position(float(r.s))+float(r.offset))
                                            for _, r in top.iterrows()]))
            entry.update({"resolved_crossings": int(sum(b[0] for b in bands)),
                          "samples_with_band": int(sum(b[1] > 0 for b in bands)),
                          "max_band_width": float(max([b[1] for b in bands], default=0.))})
        checks[label] = entry
        sums[label] = gate.groupby("s")[["nec_content", "negative_energy", "positive_energy"]].sum()*step
    gate = pd.concat(frames, ignore_index=True)
    total = sums["pattern"].copy()
    if "front" in sums:
        total = total+sums["front"].reindex(total.index).interpolate(limit_direction="both")
    ds = float(np.diff(total.index.values).min())
    demand = {"peak_nec_content": float(total.nec_content.max()),
              "nec_content_over_sigma": float(total.nec_content.sum()*ds),
              "front_window_over_sigma": float(sums["front"].nec_content.sum()*max(ds, .25)) if "front" in sums
              else 0., "peak_negative_energy": float(-total.negative_energy.min()),
              "peak_positive_energy": float(total.positive_energy.max()),
              "peak_stress": float(gate.max_abs_component.max()), "max_alpha": float(gate.max_alpha.max())}
    return checks, demand, gate


def resolve(task):
    """Root-find flux-carrying null-sum crossings across the radial nodes and measure any Type IV band."""
    spec, speed, with_cone, s, z = task
    service, design, cone = build_spec(spec, speed, with_cone=with_cone)
    radius, _ = front_pass.radial_nodes(service, design, cone, 24)
    radius = radius[radius > design.core_radius]

    def tensor_at(x):
        return fs.frame_tensor(service, design, cone, s, z, np.atleast_1d(x))
    tensor = tensor_at(radius)
    widest, crossings = 0., 0
    for i in (2, 1):
        total = tensor[:, 0, 0]+tensor[:, i, i]
        for c in np.flatnonzero(np.sign(total[:-1])*np.sign(total[1:]) < 0):
            root = brentq(lambda x: (lambda t: t[0, 0]+t[i, i])(tensor_at(x)[0]), radius[c], radius[c+1], xtol=1e-15)
            at_root = tensor_at(root)[0]
            if abs(at_root[0, i]) <= 1e-14*max(np.max(np.abs(at_root)), 1e-300):
                continue
            crossings += 1
            for span in (1e-3, 1e-5, 1e-7, 1e-9):
                fine = np.linspace(root-span, root+span, 2001)
                band = fine[ax.classify(tensor_at(fine), floor=1e-12)["type"] == ax.TYPE_IV]
                if len(band):
                    widest = max(widest, band.max()-band.min()+(fine[1]-fine[0]))
                    break
    return crossings, widest


def alpha_v_radius(spec, speed):
    """Largest radius at which the pattern's own lapse exceeds the carry speed in its front fall, at mid-lane."""
    service, design, _ = build_spec(spec, speed, with_cone=False)
    s = 3.
    c = service.packet_position(s)
    radius = np.linspace(0., 18., 721)
    best = 0.
    for x in np.linspace(service.fall_start-.5, service.extent, 60):
        log_alpha, _ = fs.log_lapse_and_shift(service, design, None, s, np.full(radius.shape, c+x), radius)
        hit = radius[np.exp(log_alpha) >= service.carry_speed(s)]
        if len(hit):
            best = max(best, float(hit.max()))
    return best


# Tip rates, swept objects and passengers

def tip_rates(spec, speed):
    service, design, cone = build_spec(spec, speed)
    s = 3.75
    c = service.packet_position(s)
    v = service.carry_speed(s)

    def a(x, r):
        return float(np.exp(fs.log_lapse_and_shift(service, design, cone, s, np.array([c+x]), np.array([r]))[0][0]))
    tip = cone.tip(service)
    reach = max(20., 4*cone.layer/math.tan(math.radians(cone.half_angle)))
    zeta = brentq(lambda x: a(x, 0.)**2-v**2, tip-reach, tip, xtol=1e-12)
    h = 1e-4
    kappa = abs((a(zeta+h, 0.)-a(zeta-h, 0.))/(2*h))
    curvature = -2*(a(zeta, 1e-3)-a(zeta, 0.))/1e-6
    lam = (-kappa+math.sqrt(kappa**2+4*v*curvature))/2
    return {"speed": speed, "tip_offset": tip, "surface_offset": zeta, "kappa": kappa, "lambda": lam,
            "lambda_over_kappa": lam/kappa}


def swept(task):
    spec, speed, decel, kind, z0, r0 = task
    service, design, cone = build_spec(spec, speed, decel)
    mass = 0. if kind == "light" else 1.
    k = (1., 0.) if kind == "light" else (0., 0.)
    n = len(z0)
    y, peak, at = fs.trace_many(service, design, cone, (-3., decel+6.), z0, r0, np.full(n, k[0]), np.full(n, k[1]),
                                mass=mass, ds=front_pass.TRACE_STEP)
    start = math.sqrt(mass+k[0]**2)
    final = np.sqrt(mass+y[2]**2+y[3]**2)/start
    return [{"speed": speed, "decel": decel, "kind": kind, "z0": float(z0[i]), "r0": float(r0[i]),
             "final_energy": float(final[i]), "max_energy": float(peak[i]/start)} for i in range(n)]


def swept_tasks(spec, speed, decels, spacing_count=10, chunk=30):
    tasks = []
    for decel in decels:
        service, _, cone = build_spec(spec, speed, decel)
        final = service.packet_position(decel+1.5)
        reach = final+cone.tip(service)
        grid = [(float(z0), float(r0)) for z0 in np.linspace(service.extent+1., reach, spacing_count)
                for r0 in LAUNCH_RADII]
        for kind in ("light", "matter"):
            for i in range(0, len(grid), chunk):
                part = grid[i:i+chunk]
                tasks.append((spec, speed, decel, kind, np.array([g[0] for g in part]), np.array([g[1] for g in part])))
    return tasks


def passenger(spec, speed):
    service, _, _ = build_spec(spec, speed, with_cone=False)
    _, z0, _, _, _, depart, _, decel, decel_time = service.path
    arrive = decel+decel_time
    distance = service.packet_position(arrive)-z0
    return {"speed": speed, "trip_distance": distance, "exterior_time": arrive-depart,
            "lead_over_light": depart+distance-arrive, "mean_speed": distance/(arrive-depart),
            "passenger_time_clock_1": arrive-depart, "passenger_days_per_light_year": 365.25/speed}


# Path audits

def exterior(service, design, cone, s, z, r):
    """True when (z, r) lies in flat space outside the lapse structure and the shift at time s."""
    log_alpha, beta = fs.log_lapse_and_shift(service, design, cone, s, np.array([z]), np.array([abs(r)]))
    return abs(log_alpha[0]) < 1e-6 and abs(beta[0]) < 1e-12


def escape_row(task):
    """Light leaving the compartment in one direction: when it first stands outside the structure."""
    spec, speed, s0, zeta0, r0, angle = task
    service, design, cone = build_spec(spec, speed, AUDIT_DECEL)
    z0 = service.packet_position(s0)+zeta0
    end = service.path[7]+service.path[8]+4.
    k0 = (math.cos(angle), math.sin(angle))
    sol = fs.trace(service, design, cone, (s0, end), z0, r0, k0, mass=0., max_step=.01, rtol=1e-8, atol=1e-10)
    out_time = math.nan
    for s, z, r in zip(sol.t, sol.y[0], sol.y[1]):
        if exterior(service, design, cone, s, z, r):
            out_time = float(s)
            break
    energy = np.hypot(sol.y[2], sol.y[3])
    release = service.path[7]
    return {"speed": speed, "launch": s0, "zeta0": zeta0, "r0": r0, "angle_deg": math.degrees(angle),
            "escape_time": out_time, "escaped_during_carry": bool(np.isfinite(out_time) and out_time < release),
            "time_to_escape": out_time-s0 if np.isfinite(out_time) else math.nan,
            "max_energy_gain": float(energy.max()), "final_energy_gain": float(energy[-1]), "status": sol.status}


def reach_row(task):
    """Light arriving at the compartment centre from one direction, traced back to before switch-on."""
    spec, speed, s0, angle = task
    service, design, cone = build_spec(spec, speed, AUDIT_DECEL)
    z0 = service.packet_position(s0)
    k0 = (math.cos(angle), math.sin(angle))
    sol = fs.trace(service, design, cone, (s0, -3.), z0, 0., k0, mass=0., max_step=.01, rtol=1e-8, atol=1e-10)
    z, r = sol.y[0, -1], abs(sol.y[1, -1])
    start = service.packet_position(-3.)
    rel = z-start
    origin = "ahead" if rel > service.extent+1. else ("behind" if rel < -service.extent-1. else "alongside")
    if r > 22.:
        origin = "side"
    return {"speed": speed, "arrival": s0, "arrival_direction_deg": math.degrees(angle), "origin": origin,
            "origin_offset": float(rel), "origin_r": float(r), "energy_ratio_at_origin": float(np.hypot(*sol.y[2:, -1])),
            "status": sol.status}


def bundle_row(task):
    """A fan of neighbouring parallel rays: smallest spacing relative to the start, and order crossings."""
    spec, speed, label, s0, zeta0, r0, angle, count, spacing = task
    service, design, cone = build_spec(spec, speed, AUDIT_DECEL)
    z0 = service.packet_position(s0)+zeta0
    normal = (-math.sin(angle), math.cos(angle))
    offsets = (np.arange(count)-(count-1)/2)*spacing
    zs, rs = z0+offsets*normal[0], r0+offsets*normal[1]
    end = min(s0+12., service.path[7]+service.path[8]+2.)
    ks = np.full(count, math.cos(angle)), np.full(count, math.sin(angle))
    sols = [fs.trace(service, design, cone, (s0, end), float(zs[i]), float(rs[i]), (ks[0][i], ks[1][i]), mass=0.,
                     max_step=.01, rtol=1e-9, atol=1e-11) for i in range(count)]
    grid = np.linspace(s0, end, 601)
    zz = np.array([np.interp(grid, sol.t, sol.y[0]) for sol in sols])
    xx = np.array([np.interp(grid, sol.t, sol.y[1]) for sol in sols])
    gaps = np.hypot(np.diff(zz, axis=0), np.diff(xx, axis=0))
    ratio = gaps.min(axis=0)/spacing
    along = (zz-zz.mean(axis=0))*normal[0]+(xx-xx.mean(axis=0))*normal[1]
    crossings = int(np.sum(np.diff(along, axis=0)[:, 1:]*np.diff(along, axis=0)[:, :-1] < 0))
    return {"speed": speed, "bundle": label, "launch": s0, "zeta0": zeta0, "r0": r0, "angle_deg": math.degrees(angle),
            "min_width_ratio": float(ratio.min()), "time_of_min": float(grid[int(np.argmin(ratio))]),
            "final_width_ratio": float(ratio[-1]), "crossing_samples": crossings}


def audit_tasks(spec, speed):
    service, _, cone = build_spec(spec, speed, AUDIT_DECEL)
    escape, reach, bundles = [], [], []
    for s0 in (-2., .75, 3., 7., AUDIT_DECEL+.75, AUDIT_DECEL+2.5):
        for zeta0, r0 in ((0., 0.), (.8, 1.)):
            for angle in np.linspace(0., 2*math.pi, 16, endpoint=False):
                escape.append((spec, speed, s0, zeta0, r0, float(angle)))
    for s0 in (.75, 3., 7., AUDIT_DECEL+.75):
        for angle in np.linspace(0., 2*math.pi, 16, endpoint=False):
            reach.append((spec, speed, s0, float(angle)))
    fans = [("overtaken_axis", 3., 12., 0., 0.), ("overtaken_offaxis", 3., 20., 4., 0.),
            ("side_inward", 3., 0., 18., -math.pi/2), ("rear_forward", 3., -12., 3., 0.),
            ("compartment_forward", 3., 0., .3, 0.), ("compartment_backward", 3., 0., .3, math.pi),
            ("compartment_sideways", 3., 0., .3, math.pi/2), ("tip_graze", 3., cone.tip(service)+3., 1., 0.)]
    for label, s0, zeta0, r0, angle in fans:
        bundles.append((spec, speed, label, s0, zeta0, r0, angle, 15, .05))
    return escape, reach, bundles


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/geometry_closure_pass")
    parser.add_argument("--stages", default="trim,reference,speed,audit")
    args = parser.parse_args()
    stages = set(args.stages.split(","))
    started = time.time()
    args.output.mkdir(parents=True, exist_ok=True)
    gz = {"method": "gzip", "mtime": 0}
    record = {}
    pd.set_option("display.width", 250)
    with ProcessPoolExecutor(args.workers) as pool:
        if "trim" in stages:
            rows = []
            for name in TRIM_SCREEN:
                spec = screen_spec(name)
                checks, demand, _ = gate_and_demand(pool, spec, BASE_SPEED, with_cone=False, sigma_step=.5,
                                                    pattern_step=.2, refine=False, resolve_bands=False)
                rows.append({"variant": name, **checks["pattern"], **demand,
                             "alpha_v_radius": alpha_v_radius(spec, BASE_SPEED)})
                print("trim", json.dumps(rows[-1]), round(time.time()-started, 1), flush=True)
            pd.DataFrame(rows).to_csv(args.output/"trim_screen.csv", index=False)

        if "reference" in stages:
            checks, demand, gate = gate_and_demand(pool, TRIM, BASE_SPEED)
            gate.to_csv(args.output/"gate_samples_reference.csv.gz", index=False, compression=gz, float_format="%.7g")
            rates = tip_rates(TRIM, BASE_SPEED)
            swept_frame = pd.DataFrame([r for chunk in pool.map(swept, swept_tasks(TRIM, BASE_SPEED, (6., 12.), 12))
                                        for r in chunk])
            swept_frame.to_csv(args.output/"swept_reference.csv.gz", index=False, compression=gz, float_format="%.9g")
            record["reference"] = {"checks": checks, "demand": demand, "tip_rates": rates,
                                   "alpha_v_radius": alpha_v_radius(TRIM, BASE_SPEED),
                                   "swept": swept_frame.groupby(["decel", "kind"]).final_energy.agg(
                                       ["max", "median"]).reset_index().to_dict("records")}
            print("reference", json.dumps(record["reference"], default=str), round(time.time()-started, 1), flush=True)

        for stage, spec, suffix in (("speed", TRIM, ""), ("speed_scaled", TRIM_SCALED, "_scaled")):
            if stage not in stages:
                continue
            rows, sweeps = [], []
            for speed in SPEEDS:
                checks, demand, _ = gate_and_demand(pool, spec, speed, sigma_step=.25, pattern_step=.1,
                                                    front_step=.25, refine=False, resolve_bands=False)
                rates = tip_rates(spec, speed)
                frame = pd.DataFrame([r for chunk in pool.map(swept, swept_tasks(spec, speed, (6., 9.), 8))
                                      for r in chunk])
                sweeps.append(frame)
                _, _, cone = build_spec(spec, speed)
                rows.append({"speed": speed, "cone_half_angle": cone.half_angle, "cone_length": cone.tip(build_spec(
                             spec, speed)[0]), **{f"pattern_{k}": v for k, v in checks["pattern"].items()},
                             **{f"front_{k}": v for k, v in checks["front"].items()}, **demand, **rates,
                             **passenger(spec, speed),
                             "alpha_v_radius": alpha_v_radius(spec, speed),
                             "swept_matter_max": float(frame[frame.kind == "matter"].final_energy.max()),
                             "swept_light_max": float(frame[frame.kind == "light"].final_energy.max()),
                             "swept_matter_max_short": float(frame[(frame.kind == "matter") & (frame.decel == 6.)]
                                                             .final_energy.max()),
                             "swept_matter_max_long": float(frame[(frame.kind == "matter") & (frame.decel == 9.)]
                                                            .final_energy.max())})
                print(stage, json.dumps(rows[-1], default=str), round(time.time()-started, 1), flush=True)
                pd.DataFrame(rows).to_csv(args.output/f"speed_scan{suffix}.csv", index=False)
            pd.concat(sweeps).to_csv(args.output/f"swept_speed_scan{suffix}.csv.gz", index=False, compression=gz,
                                     float_format="%.9g")

        for stage, spec, speeds, suffix in (("audit", TRIM, AUDIT_SPEEDS, ""),
                                            ("audit_scaled", TRIM_SCALED, (10.,), "_scaled")):
            if stage not in stages:
                continue
            escapes, reaches, bundles = [], [], []
            for speed in speeds:
                e, r, b = audit_tasks(spec, speed)
                escapes += list(pool.map(escape_row, e, chunksize=2))
                reaches += list(pool.map(reach_row, r, chunksize=2))
                bundles += list(pool.map(bundle_row, b))
                print(stage, speed, round(time.time()-started, 1), flush=True)
                pd.DataFrame(escapes).to_csv(args.output/f"audit_escape{suffix}.csv", index=False)
                pd.DataFrame(reaches).to_csv(args.output/f"audit_reachability{suffix}.csv", index=False)
                pd.DataFrame(bundles).to_csv(args.output/f"audit_bundles{suffix}.csv", index=False)

    manifest_path = args.output/"manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    manifest.update({"completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                     f"elapsed_seconds_{'_'.join(sorted(stages))}": round(time.time()-started, 1),
                     "workers": args.workers, "trim": TRIM, "trim_scaled": TRIM_SCALED, "trim_screen": TRIM_SCREEN,
                     "speeds": SPEEDS,
                     "audit_speeds": AUDIT_SPEEDS, "audit_decel": AUDIT_DECEL, "launch_radii": LAUNCH_RADII, "sigma_range": SIGMA_RANGE,
                     **record,
                     f"software_sha256_{'_'.join(sorted(stages))}": {path: sha256_file(ROOT/"toolkit/adm_harness_cli"/path) for path in (
                         "adm_harness/front_surface.py", "adm_harness/compartment_service.py",
                         "adm_harness/axial_track.py", "scripts/run_front_surface_pass.py",
                         "scripts/run_geometry_closure_pass.py")}})
    manifest_path.write_text(json.dumps(manifest, indent=1, default=str)+"\n")


if __name__ == "__main__":
    main()
