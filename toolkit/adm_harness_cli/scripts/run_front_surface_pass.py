#!/usr/bin/env python3
"""Front light surface of the compartment design and two front elements that bound what it gathers; emit data only.

The compartment design's lapse falls through the carry speed ahead of the packet, and the surface where it does
gathers the light and matter that the pattern overtakes. This pass compares four fronts on the clock-1
compartment: the current front, a forward shelf whose leading edge runs ahead faster than light inside it, the
same shelf switched on along its whole length with the pattern, and a slender conical front.

For each front the run traces meridional light rays and unit-mass particles launched ahead of the pattern
through carries of three lengths, and records the energy they keep once the structure switches off. It also
applies the gate and the demand census around the pattern and across the front element, and traces a forward
signal from the packet along the axis against the arrival of each element at points along the route. A clock-rate
sweep of the compartment adds screen, demand and passenger data for rates from 0.1 to 5. Narrative
interpretation is maintained manually in supporting_reports.
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
from adm_harness import axial_track as ax
from adm_harness import compartment_service as cs
from adm_harness import front_surface as fs
from adm_harness.constant_radius_track import smooth_step
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
SPEED = 2.1
LANES = (6., 12., 18.)
FRONTS = {
    "current_front": None,
    "shelf_running": fs.ForwardShelf(),
    "shelf_static": fs.ForwardShelf(lead_speed=math.inf),
    "cone": fs.ConeFront(),
}
CLOCK_RATES = (.1, .2, .3, .5, .7, 1., 1.5, 2., 3., 5.)
LAUNCH_RADII = (.05, .5, 2., 5., 8., 11., 14., 17.)
TRACE_START = -3.
TRACE_STEP = .005
SIGMA_RANGE = (-3.5, 10.)
WINDOW = 8.25
PER_PANEL = 6
MAX_PANEL = .5
NOISE_FLOOR = choreography.NOISE_FLOOR


def build(front_name, decel=6., clock_log=0., jet_step=choreography.JET_STEP):
    service = cs.CompartmentService(path=(-1., 0., 0., SPEED, 0., 0., 1.5, decel, 1.5), clock_log=clock_log,
                                    schedule=(-2.5, decel+3., 1.))
    return service, cs.axial_design(service, jet_step=jet_step), FRONTS[front_name]


def reach(service, front):
    """Largest offset from the packet's final position that the lapse structure reaches."""
    arrive = service.path[7]+service.path[8]
    final = service.packet_position(arrive)
    if isinstance(front, fs.ForwardShelf):
        return front.terminal(service)+front.lead_width-final
    if isinstance(front, fs.ConeFront):
        return front.tip(service)
    return service.extent


def radial_nodes(service, design, front, per_panel=PER_PANEL, max_panel=MAX_PANEL):
    """Gauss-Legendre radii and area weights over (0, r_max], split at every layer's joins and at most max_panel wide."""
    fraction = design.track.join_fraction
    spans = [design.layers["alpha"], design.layers["beta"], design.sheath_rise, design.sheath_fall,
             service.hole_radius]
    if isinstance(front, fs.ForwardShelf):
        spans.append(front.radius)
    r_max = max(start+width for start, width in spans)+1.
    if isinstance(front, fs.ConeFront):
        r_max = max(r_max, front.base_radius+front.layer+2.)
    cuts = {0., design.core_radius, r_max}
    for start, width in spans:
        cuts.update(start+width*u for u in (0., fraction, .5, 1-fraction, 1.))
    cuts = sorted(c for c in cuts if 0 <= c <= r_max)
    edges = []
    for lo, hi in zip(cuts[:-1], cuts[1:]):
        pieces = max(1, math.ceil((hi-lo)/max_panel-1e-9))
        edges += list(np.linspace(lo, hi, pieces+1)[:-1])
    edges.append(r_max)
    nodes, weights = np.polynomial.legendre.leggauss(per_panel)
    radius = np.concatenate([lo+(hi-lo)*(nodes+1)/2 for lo, hi in zip(edges[:-1], edges[1:])])
    weight = np.concatenate([(hi-lo)/2*weights for lo, hi in zip(edges[:-1], edges[1:])])
    return radius, weight*2*math.pi*radius


# Swept objects

def swept(task):
    """Energy each launched object keeps after the structure has passed and switched off."""
    front_name, decel, kind, z0, r0 = task
    service, design, front = build(front_name, decel)
    mass = 0. if kind == "light" else 1.
    k = (1., 0.) if kind == "light" else (0., 0.)
    count = len(z0)
    y, peak, at = fs.trace_many(service, design, front, (TRACE_START, decel+6.), z0, r0, np.full(count, k[0]),
                                np.full(count, k[1]), mass=mass, ds=TRACE_STEP)
    start = math.sqrt(mass+k[0]**2+k[1]**2)
    final = np.sqrt(mass+y[2]**2+y[3]**2)/start
    return [{"front": front_name, "decel": decel, "kind": kind, "z0": float(z0[i]), "r0": float(r0[i]),
             "final_energy": float(final[i]), "max_energy": float(peak[i]/start), "sigma_at_max": float(at[0, i]),
             "offset_at_max": float(at[1, i]), "r_at_max": float(at[2, i]), "final_z": float(y[0, i]),
             "final_r": float(abs(y[1, i])), "final_angle_deg": math.degrees(math.atan2(abs(y[3, i]), y[2, i]))}
            for i in range(count)]


def swept_tasks(chunk=40):
    """Launch grids ahead of each design, over its whole reach, split into batches of objects."""
    tasks = []
    for name, front in FRONTS.items():
        spacing = 6. if isinstance(front, fs.ConeFront) else 3.
        for decel in LANES:
            service, _, _ = build(name, decel)
            final = service.packet_position(decel+1.5)
            grid = [(float(z0), float(r0)) for z0 in np.arange(service.extent+1., final+reach(service, front)+1e-9,
                                                               spacing) for r0 in LAUNCH_RADII]
            for kind in ("light", "matter"):
                for i in range(0, len(grid), chunk):
                    part = grid[i:i+chunk]
                    tasks.append((name, decel, kind, np.array([g[0] for g in part]), np.array([g[1] for g in part])))
    return tasks


def swept_summary(frame):
    """Per front, carry and kind: area-weighted mean energy over the launch disk, the largest, and tail shares."""
    radii = np.array(LAUNCH_RADII)
    mids = np.concatenate([[0.], (radii[1:]+radii[:-1])/2, [radii[-1]]])
    area = dict(zip(LAUNCH_RADII, np.pi*(mids[1:]**2-mids[:-1]**2)))
    rows = []
    for (front, decel, kind), group in frame.groupby(["front", "decel", "kind"], sort=False):
        w = group.r0.map(area)
        rows.append({"front": front, "decel": decel, "kind": kind, "launches": len(group),
                     "mean_final_energy": float(np.sum(w*group.final_energy)/np.sum(w)),
                     "median_final_energy": float(group.final_energy.median()),
                     "max_final_energy": float(group.final_energy.max()),
                     "max_energy_along_path": float(group.max_energy.max()),
                     "share_above_10": float(np.sum(w*(group.final_energy > 10))/np.sum(w)),
                     "share_above_1e3": float(np.sum(w*(group.final_energy > 1e3))/np.sum(w))})
    return pd.DataFrame(rows)


# Gate and demand

def gate_row(task):
    """Node types, band estimates and demand sums at one sigma over a set of offsets from the packet."""
    front_name, clock_log, s, offsets, jet_step, per_panel, with_census = task
    service, design, front = build(front_name, 6., clock_log, jet_step)
    radius, area = radial_nodes(service, design, front, per_panel)
    centre = service.packet_position(s)
    rows = []
    for offset in offsets:
        z = centre+float(offset)
        f = fs.fields(service, design, front, s, z, radius)
        tensor = ax.tensor_from_fields(f, radius, design, product_core=False)
        kinds = ax.classify(tensor, floor=NOISE_FLOOR)["type"]
        null = ax.min_null_energy(tensor)
        row = {"s": s, "offset": float(offset), "z": z,
               "type_i": int((kinds == ax.TYPE_I).sum()), "type_iv": int((kinds == ax.TYPE_IV).sum()),
               "other": int(np.isin(kinds, [ax.UNRESOLVED, ax.TYPE_II_III]).sum()), "min_null": float(null.min()),
               "estimated_band_width": choreography.band_widths(tensor, radius),
               "envelope_ratio": float(2*design.core_radius*abs(f["beta_z"][0])/f["alpha"][0])}
        if with_census:
            point = census.point_census(tensor, f, area, area)
            speed = point["speed_vs_static"]
            row.update({"nec_content": float(np.sum(area*np.maximum(-null, 0))),
                        "negative_energy": float(np.sum(area*np.minimum(tensor[:, 0, 0], 0))),
                        "positive_energy": float(np.sum(area*np.maximum(tensor[:, 0, 0], 0))),
                        "max_abs_component": float(np.max(np.abs(tensor))), "max_alpha": float(f["alpha"].max()),
                        "max_source_speed_vs_static": float(np.nanmax(speed)) if np.isfinite(speed).any() else 0.,
                        "violating_volume_r": float(area[point["direction"]["r"]].sum()),
                        "violating_volume_z": float(area[point["direction"]["z"]].sum()),
                        "violating_volume_phi": float(area[point["direction"]["phi"]].sum()),
                        "type_i_volume": float(area[point["type_i"]].sum())})
        rows.append(row)
    return rows


def resolve(task):
    """Root-find every flux-carrying null-sum crossing across the radial nodes and measure any Type IV band."""
    front_name, s, z = task
    service, design, front = build(front_name)
    radius, _ = radial_nodes(service, design, front, 24)
    radius = radius[radius > design.core_radius]

    def tensor_at(x):
        return fs.frame_tensor(service, design, front, s, z, np.atleast_1d(x))

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
                kinds = ax.classify(tensor_at(fine), floor=1e-12)["type"]
                band = fine[kinds == ax.TYPE_IV]
                if len(band):
                    widest = max(widest, band.max()-band.min()+(fine[1]-fine[0]))
                    break
    return front_name, s, z, crossings, widest


def windows(front_name):
    """(label, sigma values, offsets, offset step) for the pattern window and, with a front element, the front window."""
    service, _, front = build(front_name)
    pattern = (np.round(np.arange(SIGMA_RANGE[0], SIGMA_RANGE[1]+.05, .1), 10),
               np.round(np.arange(-WINDOW, WINDOW+.05, .1), 10), .1)
    out = [("pattern",)+pattern]
    if front is not None:
        far = np.round(np.arange(WINDOW+.25, reach(service, front)+service.packet_position(7.5)+1.+1e-9, .25), 10)
        out.append(("front", np.round(np.arange(SIGMA_RANGE[0], SIGMA_RANGE[1]+.1, .25), 10), far, .25))
    return out


def gate_and_demand(front_name, pool, per_panel=PER_PANEL, refine=True):
    checks, sums, frames = {}, {}, []
    for label, sigma, offsets, step in windows(front_name):
        rows = [r for chunk in pool.map(gate_row, [(front_name, 0., float(s), offsets, choreography.JET_STEP,
                                                    per_panel, True) for s in sigma], chunksize=2) for r in chunk]
        gate = pd.DataFrame(rows)
        gate.insert(0, "window", label)
        frames.append(gate)
        entry = {"samples": len(gate), "type_i": int(gate.type_i.sum()), "type_iv": int(gate.type_iv.sum()),
                 "other": int(gate.other.sum()), "estimated_band_samples": int((gate.estimated_band_width > 0).sum()),
                 "envelope_violations": int((gate.envelope_ratio > 1).sum()), "min_null": float(gate.min_null.min())}
        if refine:
            refined = [r for chunk in pool.map(gate_row, [(front_name, 0., float(s), offsets, choreography.JET_STEP/2,
                                                           2*per_panel, False) for s in sigma[::2]], chunksize=2)
                       for r in chunk]
            refined = pd.DataFrame(refined)
            entry.update({"refined_samples": len(refined), "refined_type_i": int(refined.type_i.sum()),
                          "refined_type_iv": int(refined.type_iv.sum()), "refined_other": int(refined.other.sum())})
        if label == "pattern":
            top = gate.nlargest(choreography.RESOLVED_SAMPLES, "estimated_band_width")
            top = top[top.estimated_band_width > 0]
            resolved = pd.DataFrame(list(pool.map(resolve, [(front_name, float(r.s), float(r.z))
                                                            for _, r in top.iterrows()])),
                                    columns=["front", "s", "z", "crossings", "width"])
            entry.update({"resolved_crossings": int(resolved.crossings.sum()),
                          "samples_with_band": int((resolved.width > 0).sum()),
                          "max_band_width": float(resolved.width.max()) if len(resolved) else 0.})
        checks[label] = entry
        sums[label] = gate.groupby("s")[["nec_content", "negative_energy", "positive_energy"]].sum()*step
    gate = pd.concat(frames, ignore_index=True)
    total = sums["pattern"].copy()
    if "front" in sums:
        front = sums["front"].reindex(total.index).interpolate(limit_direction="both")
        total = total+front
    dsigma = .1
    volume = gate[["violating_volume_r", "violating_volume_z", "violating_volume_phi", "type_i_volume"]].sum()
    demand = {"front": front_name, "peak_nec_content": float(total.nec_content.max()),
              "nec_content_over_sigma": float(total.nec_content.sum()*dsigma),
              "pattern_window_over_sigma": float(sums["pattern"].nec_content.sum()*dsigma),
              "front_window_over_sigma": float(sums["front"].nec_content.sum()*.25) if "front" in sums else 0.,
              "peak_front_window_content": float(sums["front"].nec_content.max()) if "front" in sums else 0.,
              "peak_negative_energy": float(-total.negative_energy.min()),
              "peak_positive_energy": float(total.positive_energy.max()),
              "peak_stress": float(gate.max_abs_component.max()), "max_alpha": float(gate.max_alpha.max()),
              "max_source_speed_vs_static": float(gate.max_source_speed_vs_static.max()),
              "violating_share_r": float(volume.violating_volume_r/volume.type_i_volume),
              "violating_share_z": float(volume.violating_volume_z/volume.type_i_volume),
              "violating_share_phi": float(volume.violating_volume_phi/volume.type_i_volume)}
    return checks, demand, gate, total


def shelf_cross_section(front_name):
    """Negative-null content per unit length of a shelf's standing section, from one cross-section at mid-lane."""
    service, design, front = build(front_name)
    radius, area = radial_nodes(service, design, front, 24, .25)
    s = 3.
    z = .5*(service.packet_position(s)+service.extent+front.edge_position(service, s))
    f = fs.fields(service, design, front, s, z, radius)
    tensor = ax.tensor_from_fields(f, radius, design, product_core=False)
    null = ax.min_null_energy(tensor)
    return {"front": front_name, "s": s, "z": z, "alpha_axis": float(f["alpha"][0]),
            "nec_content_per_length": float(np.sum(area*np.maximum(-null, 0))),
            "max_abs_component": float(np.max(np.abs(tensor))), "max_abs_energy": float(np.max(np.abs(tensor[:, 0, 0])))}


# Choreography

def first_crossing(g, lo, hi, samples=2001):
    """First time in [lo, hi] at which g turns nonnegative, located on a grid and refined; nan if it never does."""
    grid = np.linspace(lo, hi, samples)
    values = np.array([g(s) for s in grid])
    hits = np.flatnonzero(values >= 0)
    if not len(hits):
        return math.nan
    if hits[0] == 0:
        return lo
    return brentq(g, grid[hits[0]-1], grid[hits[0]], xtol=1e-10)


def element_arrival(service, front, z):
    """Exterior times at which the pattern's front extent and the front element first reach route position z."""
    lo, hi = service.schedule[0], service.path[7]+service.path[8]+1.
    pattern = first_crossing(lambda s: service.packet_position(s)+service.extent-z, lo, hi)
    if isinstance(front, fs.ForwardShelf):
        element = first_crossing(lambda s: front.edge_position(service, s)+front.lead_width-z, lo, hi)
    elif isinstance(front, fs.ConeFront):
        shift_end = service.shift_start+service.shift_width
        low, high = front.extend

        def tip(s):
            grow = smooth_step((service.carry_speed(s)-low)/(high-low))
            return service.packet_position(s)+shift_end+(front.tip(service)-shift_end)*grow-z
        element = first_crossing(tip, lo, hi)
    else:
        element = pattern
    return pattern, element


def signal_rows(task):
    """Forward signal along the axis from the packet at one launch time, against each element's arrival."""
    front_name, decel, launch = task
    service, design, front = build(front_name, decel)
    start = service.packet_position(launch)
    sol = fs.trace(service, design, front, (launch, decel+6.), start, 0., (1., 0.), mass=0., max_step=.02,
                   rtol=1e-9, atol=1e-11)
    s_ray, z_ray = sol.t, sol.y[0]
    rows = []
    final = service.packet_position(decel+1.5)
    for z in np.arange(math.ceil(start+service.extent+1.), final+reach(service, front)+1e-9, 2.):
        reached = np.flatnonzero(z_ray >= z)
        signal = float(np.interp(z, z_ray[:reached[0]+1], s_ray[:reached[0]+1])) if len(reached) else math.nan
        pattern, element = element_arrival(service, front, z)
        rows.append({"front": front_name, "decel": decel, "launch": launch, "z": float(z), "signal_arrival": signal,
                     "pattern_arrival": pattern, "element_arrival": element,
                     "lead_over_pattern": pattern-signal if np.isfinite(signal) and np.isfinite(pattern) else math.nan,
                     "lead_over_element": element-signal if np.isfinite(signal) and np.isfinite(element) else math.nan,
                     "packet_arrival": decel+1.5})
    return rows


# Clock sweep

def clock_sweep(pool):
    rows = []
    sigma = np.round(np.arange(SIGMA_RANGE[0], SIGMA_RANGE[1]+.05, .2), 10)
    offsets = np.round(np.arange(-WINDOW, WINDOW+.05, .1), 10)
    for rate in CLOCK_RATES:
        clock_log = math.log(rate)
        gate = pd.DataFrame([r for chunk in pool.map(gate_row, [(
            "current_front", clock_log, float(s), offsets, choreography.JET_STEP, PER_PANEL, True) for s in sigma],
            chunksize=2) for r in chunk])
        per_sigma = gate.groupby("s")[["nec_content", "negative_energy"]].sum()*.1
        service, design, _ = build("current_front", clock_log=clock_log)
        static_reach = []
        for s in (2., 3., 4.):
            c = service.packet_position(s)
            f = fs.fields(service, design, None, s, c, np.linspace(0., 6., 121))
            missing = np.abs(f["beta"]) >= f["alpha"]
            static_reach.append(float(np.linspace(0., 6., 121)[missing].max()) if missing.any() else 0.)
        rows.append({"clock_rate": rate, "clock_log": clock_log, "samples": len(gate),
                     "type_i": int(gate.type_i.sum()), "type_iv": int(gate.type_iv.sum()),
                     "other": int(gate.other.sum()), "min_null": float(gate.min_null.min()),
                     "peak_nec_content": float(per_sigma.nec_content.max()),
                     "nec_content_over_sigma": float(per_sigma.nec_content.sum()*.2),
                     "peak_negative_energy": float(-per_sigma.negative_energy.min()),
                     "peak_stress": float(gate.max_abs_component.max()),
                     "radius_without_static_frame": max(static_reach),
                     "passenger_time_test_trip": rate*7.5,
                     "passenger_years_per_light_year": rate/SPEED})
        print("clock", rate, json.dumps(rows[-1]), flush=True)
    return pd.DataFrame(rows)


# Figures

def figure(output, swept_frame, clock):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    s = 3.
    fig, axes = plt.subplots(3, 1, figsize=(13, 10.5))
    for panel, name in zip(axes, ("current_front", "shelf_running", "cone")):
        service, design, front = build(name)
        c = service.packet_position(s)
        far = min(reach(service, front)+service.packet_position(7.5)-c, 72.) if front is not None else 12.
        zeta = np.linspace(-service.extent-1., far+2., 400)
        radius = np.linspace(0., 22., 111)
        log_alpha = np.empty((len(radius), len(zeta)))
        for j, x in enumerate(zeta):
            for i, r in enumerate(radius):
                log_alpha[i, j] = fs.point_log_lapse_and_shift(service, design, front, s, c+x, r)[0]
        mesh = panel.pcolormesh(zeta, radius, log_alpha, shading="nearest", cmap="viridis", vmin=0., vmax=6.5)
        panel.contour(zeta, radius, log_alpha, levels=[math.log(SPEED)], colors="w", linewidths=1.)
        panel.set_ylabel("r")
        panel.set_title(f"{name.replace('_', ' ')} at sigma = 3: log-lapse, white contour where the lapse equals "
                        f"the carry speed {SPEED}", fontsize=9)
        fig.colorbar(mesh, ax=panel, label=r"$\log\alpha$")
    axes[-1].set_xlabel(r"offset from the packet $z-\ell_p$")
    fig.tight_layout()
    fig.savefig(output/"fronts.png", dpi=120)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))
    styles = {6.: "-", 12.: "--", 18.: ":"}
    for name, colour in zip(FRONTS, ("C3", "C0", "C2", "C1")):
        for decel, style in styles.items():
            group = swept_frame[(swept_frame.front == name) & (swept_frame.decel == decel)
                                & (swept_frame.kind == "matter")]
            by_radius = group.groupby("r0").final_energy.max()
            axes[0].plot(by_radius.index, by_radius.values, style, color=colour,
                         label=name.replace("_", " ") if decel == 6. else None)
    axes[0].set_yscale("log")
    axes[0].set_xlabel("launch radius")
    axes[0].set_ylabel("largest final gamma of matter at rest ahead")
    axes[0].set_title("matter overtaken by the pattern; solid, dashed, dotted: carries ending at 7.5, 13.5, 19.5",
                      fontsize=8)
    axes[0].legend(fontsize=8)
    axes[1].plot(clock.clock_rate, clock.peak_stress, "o-", label="peak stress")
    axes[1].plot(clock.clock_rate, clock.peak_nec_content/100., "s-", label="peak negative-null content / 100")
    axes[1].set_xscale("log")
    axes[1].set_xlabel("compartment clock rate")
    axes[1].legend(fontsize=8)
    axes[1].set_title("demand of the compartment against its clock rate", fontsize=9)
    axes[2].plot(clock.clock_rate, 12*clock.passenger_years_per_light_year, "o-")
    axes[2].set_xscale("log")
    axes[2].set_yscale("log")
    axes[2].set_xlabel("compartment clock rate")
    axes[2].set_ylabel("passenger months per light-year at 2.1c")
    axes[2].set_title("passenger aging along a long lane", fontsize=9)
    fig.tight_layout()
    fig.savefig(output/"swept_and_clock.png", dpi=120)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/front_surface_pass")
    parser.add_argument("--skip-swept", action="store_true", help="reuse swept_objects.csv.gz from the output")
    args = parser.parse_args()
    started = time.time()
    args.output.mkdir(parents=True, exist_ok=True)
    gz = {"method": "gzip", "mtime": 0}

    with ProcessPoolExecutor(args.workers) as pool:
        if args.skip_swept:
            swept_frame = pd.read_csv(args.output/"swept_objects.csv.gz")
        else:
            swept_frame = pd.DataFrame([r for chunk in pool.map(swept, swept_tasks(), chunksize=1) for r in chunk])
            swept_frame.to_csv(args.output/"swept_objects.csv.gz", index=False, compression=gz, float_format="%.9g")
        summary = swept_summary(swept_frame)
        summary.to_csv(args.output/"swept_summary.csv", index=False)
        pd.set_option("display.width", 250)
        print(summary.to_string(index=False), round(time.time()-started, 1), flush=True)

        signals = pd.DataFrame([r for chunk in pool.map(signal_rows, [(name, decel, launch) for name in FRONTS
                                                                      for decel in (6., 18.) for launch in (0., 3.)])
                                for r in chunk])
        signals.to_csv(args.output/"signals.csv", index=False)
        print("signals", round(time.time()-started, 1), flush=True)

        checks, demand, per_sigma = {}, [], []
        for name in FRONTS:
            checks[name], entry, gate, total = gate_and_demand(name, pool)
            demand.append(entry)
            gate.insert(0, "front", name)
            gate.to_csv(args.output/f"gate_samples_{name}.csv.gz", index=False, compression=gz, float_format="%.7g")
            total.insert(0, "front", name)
            per_sigma.append(total.reset_index())
            print(name, json.dumps(checks[name]), json.dumps(entry), round(time.time()-started, 1), flush=True)
        pd.DataFrame(demand).to_csv(args.output/"demand.csv", index=False)
        pd.concat(per_sigma).to_csv(args.output/"demand_by_sigma.csv", index=False)
        cross = pd.DataFrame([shelf_cross_section(name) for name in ("shelf_running", "shelf_static")])
        cross.to_csv(args.output/"shelf_cross_section.csv", index=False)

        clock = clock_sweep(pool)
        clock.to_csv(args.output/"clock_sweep.csv", index=False)

    figure(args.output, swept_frame, clock)
    manifest = {
        "completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time()-started, 1), "workers": args.workers, "speed": SPEED, "lanes": LANES,
        "fronts": {name: (None if front is None else {"type": type(front).__name__, **front.__dict__})
                   for name, front in FRONTS.items()},
        "clock_rates": CLOCK_RATES, "launch_radii": LAUNCH_RADII, "trace_start": TRACE_START,
        "trace_step": TRACE_STEP,
        "sigma_range": SIGMA_RANGE, "window": WINDOW, "per_panel": PER_PANEL, "max_panel": MAX_PANEL,
        "noise_floor": NOISE_FLOOR, "service_defaults": cs.CompartmentService().__dict__, "checks": checks,
        "software_sha256": {path: sha256_file(ROOT/"toolkit/adm_harness_cli"/path) for path in (
            "adm_harness/front_surface.py", "adm_harness/compartment_service.py", "adm_harness/axial_track.py",
            "adm_harness/axial_einstein_generated.py", "adm_harness/constant_radius_track.py",
            "scripts/run_front_surface_pass.py")},
    }
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=1, default=str)+"\n")


if __name__ == "__main__":
    main()
