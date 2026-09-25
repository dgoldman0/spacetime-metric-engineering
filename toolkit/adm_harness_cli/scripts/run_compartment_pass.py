#!/usr/bin/env python3
"""Flat passenger compartment with a chosen clock rate; emit data only.

The lapse-staged rail carries its packet on a lapse plateau of e^4: the
packet's clock runs 55 times faster than exterior clocks, and the packet
rides in curvature that sets tidal and inertial accelerations of order
c^2/L. This pass carries the packet from rest to rest inside a compartment
where the lapse and the shift are uniform in space, a flat region whose
normal observers are geodesics. The compartment is a hole cut into a
gate-passing lapse structure where the shift is uniform, and its lapse sets
the packet's clock rate.

The run screens structural variants near the structure, then gives three
clock rates the full treatment: the gate with band resolution and
refinement, the demand census, the passenger history (clock rate, curvature,
acceleration and speed relative to the local free-fall frame) and the
arrival against light through flat space. Narrative interpretation is
maintained manually in supporting_reports.
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
from adm_harness import source_scaling as ss
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
SIGMA_RANGE = (-3.5, 10.)
MARGIN = 1.5
PER_PANEL = 12
NOISE_FLOOR = choreography.NOISE_FLOOR
DESIGNS = {
    "clock_1": dict(service=dict(clock_log=0.), axial={}),
    "clock_0p2": dict(service=dict(clock_log=math.log(.2)), axial={}),
    "clock_55": dict(service=dict(clock_log=4.), axial={}),
}
SCREEN = {
    **DESIGNS,
    "clock_0p05": dict(service=dict(clock_log=math.log(.05)), axial={}),
    "plateau_e3": dict(service=dict(plateau_log=3.), axial={}),
    "plateau_e2": dict(service=dict(plateau_log=2.), axial={}),
    "shift_edge_1": dict(service=dict(shift_width=1.), axial={}),
    "hole_edge_0p5": dict(service=dict(hole_edge=.5), axial={}),
    "slope_0": dict(service=dict(slope=0.), axial={}),
    "sheath_e0p5": dict(service={}, axial=dict(sheath_log_lapse=.5)),
    "no_sheath": dict(service={}, axial=dict(sheath_log_lapse=0.)),
}
ZONES = (("compartment_region", 0., 1.75), ("hole_boundary", 1.75, 3.25), ("inner_band", 3.25, 3.75),
         ("sheath_rise", 3.75, 8.75), ("sheath_plateau", 8.75, 9.25), ("outer_falls", 9.25, 13.25))


def build(name, jet_step=choreography.JET_STEP):
    entry = SCREEN[name]
    service = cs.CompartmentService(**entry["service"])
    return service, cs.axial_design(service, jet_step=jet_step, **entry["axial"])


def offsets(service, step):
    edge = service.extent+MARGIN
    return np.round(np.arange(-edge, edge+step/2, step), 10)


def screen_row(task):
    """Node types and estimated bands around the structure at one sigma."""
    name, s = task
    service, design = build(name)
    radius = np.concatenate([[0.], ax.wall_nodes(design, PER_PANEL)[0]])
    centre = service.packet_position(s)
    row = {"design": name, "s": s, "type_iv": 0, "samples_with_type_iv": 0, "unresolved": 0, "estimates": []}
    for offset in offsets(service, .1):
        z = centre+float(offset)
        tensor = cs.frame_tensor(service, design, s, z, radius)
        kinds = ax.classify(tensor, floor=NOISE_FLOOR)["type"]
        count = int((kinds == ax.TYPE_IV).sum())
        row["type_iv"] += count
        row["samples_with_type_iv"] += int(count > 0)
        row["unresolved"] += int(np.isin(kinds, [ax.UNRESOLVED, ax.TYPE_II_III]).sum())
        width = choreography.band_widths(tensor[1:], radius[1:])
        if width > 0:
            row["estimates"].append((width, z))
    row["estimates"] = sorted(row["estimates"], reverse=True)[:3]
    return row


def resolve(task):
    """Root-find every flux-carrying null-sum crossing across the boundary layer and measure any Type IV band."""
    name, s, z = task
    service, design = build(name)
    radius = ax.wall_nodes(design, 24)[0]

    def tensor_at(x):
        return cs.frame_tensor(service, design, s, z, np.atleast_1d(x))

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
    return name, s, z, crossings, widest


def zone_sums(point, radius, weight):
    out = {}
    for zone, lo, hi in ZONES:
        m = (radius >= lo) & (radius <= hi) if lo == 0. else (radius > lo) & (radius <= hi)
        out[f"nec_content_{zone}"] = float(np.sum(weight[m]*np.maximum(-point["null"][m], 0)))
    return out


def gate_row(task):
    """Gate counts, band estimates, envelope ratio and demand sums over the structure at one sigma."""
    name, s, per_panel, jet_step, step, with_census = task
    service, design = build(name, jet_step)
    nodes, weights = ax.wall_nodes(design, per_panel)
    radius = np.concatenate([[0.], nodes])
    area = np.concatenate([[math.pi*design.core_radius**2], weights*2*math.pi*nodes])
    centre = service.packet_position(s)
    rows = []
    for offset in offsets(service, step):
        z = centre+float(offset)
        f = cs.fields(service, design, s, z, radius)
        tensor = ax.tensor_from_fields(f, radius, design)
        kinds = ax.classify(tensor, floor=NOISE_FLOOR)["type"]
        null = ax.min_null_energy(tensor)
        row = {"s": s, "offset": float(offset), "z": z,
               "layer_type_i": int((kinds[1:] == ax.TYPE_I).sum()),
               "layer_type_iv": int((kinds[1:] == ax.TYPE_IV).sum()),
               "layer_other": int(np.isin(kinds[1:], [ax.UNRESOLVED, ax.TYPE_II_III]).sum()),
               "core_type_iv": int(kinds[0] == ax.TYPE_IV),
               "core_min_null": float(null[0]), "layer_min_null": float(null[1:].min()),
               "estimated_band_width": choreography.band_widths(tensor[1:], radius[1:]),
               "envelope_ratio": float(2*design.core_radius*abs(f["beta_z"][0])/f["alpha"][0])}
        if with_census:
            point = census.point_census(tensor, f, area, area)
            speed = point["speed_vs_static"]
            row.update({"nec_content": float(np.sum(area*np.maximum(-null, 0))),
                        "negative_energy": float(np.sum(area*np.minimum(tensor[:, 0, 0], 0))),
                        "positive_energy": float(np.sum(area*np.maximum(tensor[:, 0, 0], 0))),
                        "max_abs_component": float(np.max(np.abs(tensor))),
                        "max_alpha": float(f["alpha"].max()),
                        "max_source_speed_vs_static": float(np.nanmax(speed)) if np.isfinite(speed).any() else 0.,
                        "violating_volume_r": float(area[point["direction"]["r"]].sum()),
                        "violating_volume_z": float(area[point["direction"]["z"]].sum()),
                        "violating_volume_phi": float(area[point["direction"]["phi"]].sum()),
                        "type_i_volume": float(area[point["type_i"]].sum()),
                        "ordinary_volume": float(area[point["ordinary"]].sum()),
                        **zone_sums(point, radius, area)})
        rows.append(row)
    return rows


def passenger(name, step=.005):
    """Trip history of the packet: clock rate, proper time, curvature and acceleration in the compartment."""
    service, design = build(name)
    sigma = np.round(np.arange(SIGMA_RANGE[0], SIGMA_RANGE[1]+step/2, step), 10)
    rows = []
    for index, s in enumerate(sigma):
        centre = service.packet_position(s)
        f = cs.fields(service, design, s, centre, [0., .875])
        row = {"s": float(s), "z": centre, "carry_speed": service.carry_speed(s), "clock_rate": float(f["alpha"][0]),
               "speed_vs_normal": float((service.carry_speed(s)+f["beta"][0])/f["alpha"][0]),
               "acceleration": float(math.hypot(f["alpha_z"][0], f["alpha_r"][0])/f["alpha"][0])}
        if index % 20 == 0:
            worst = 0.
            for offset in np.linspace(-service.half_width, service.half_width, 9):
                g = cs.fields(service, design, s, centre+offset, [.875, 1.6])
                metric = ss.metric_jets(g)
                components = ss.frame_riemann(ss.riemann(*metric), ss.normal_tetrad(g))
                worst = max(worst, float(np.max(np.abs(components))))
            row["compartment_max_riemann"] = worst
        rows.append(row)
    frame = pd.DataFrame(rows)
    frame["proper_time"] = np.concatenate([[0.], np.cumsum(.5*(frame.clock_rate.values[1:]+frame.clock_rate.values[:-1])
                                                            * np.diff(frame.s.values))])
    frame.insert(0, "design", name)
    return frame


def arrival(name, trip):
    service, _ = build(name)
    _, z0, _, _, _, depart, _, decel, decel_time = service.path
    arrive = decel+decel_time
    distance = service.packet_position(arrive)-z0
    during = trip[(trip.s >= depart) & (trip.s <= arrive)]
    proper = float(np.trapezoid(during.clock_rate, during.s))
    return {"design": name, "departure": depart, "arrival": arrive, "distance": distance,
            "light_arrival": depart+distance, "lead_over_light": depart+distance-arrive,
            "mean_speed": distance/(arrive-depart), "passenger_proper_time": proper,
            "light_travel_time": distance, "passenger_time_over_light_time": proper/distance,
            "max_speed_vs_normal": float(np.max(np.abs(trip.speed_vs_normal))),
            "max_acceleration": float(trip.acceleration.max()),
            "max_compartment_riemann": float(trip.compartment_max_riemann.max()),
            "max_clock_rate": float(trip.clock_rate.max())}


def figure(output, trips):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    service, design = build("clock_1")
    s = 3.
    centre = service.packet_position(s)
    zeta = np.linspace(-service.extent-1, service.extent+1, 241)
    radius = np.linspace(0., 14., 141)
    log_alpha = np.empty((len(radius), len(zeta)))
    shift = np.empty_like(log_alpha)
    for j, x in enumerate(zeta):
        f = cs.fields(service, design, s, centre+x, radius)
        log_alpha[:, j], shift[:, j] = np.log(f["alpha"]), f["beta"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.4))
    mesh = axes[0].pcolormesh(zeta, radius, log_alpha, shading="nearest", cmap="viridis")
    fig.colorbar(mesh, ax=axes[0], label=r"$\log\alpha$")
    axes[0].contour(zeta, radius, -shift, levels=[.1, 1., 2.], colors="w", linewidths=.8)
    axes[0].set_xlabel(r"$z-\ell_p$")
    axes[0].set_ylabel("r")
    axes[0].set_title(r"clock-1 compartment at $\sigma=3$: log-lapse, with shift contours 0.1, 1, 2", fontsize=9)
    for name, trip in trips.items():
        axes[1].plot(trip.s, trip.proper_time, label=name.replace("_", " "))
    axes[1].plot(trips["clock_1"].s, trips["clock_1"].s-trips["clock_1"].s.iloc[0], "k:", lw=.8,
                 label="exterior time")
    axes[1].set_yscale("symlog", linthresh=1.)
    axes[1].set_xlabel(r"exterior time $\sigma$")
    axes[1].set_ylabel("packet proper time")
    axes[1].legend(fontsize=8)
    axes[1].set_title("passenger clock over the trip", fontsize=9)
    fig.tight_layout()
    fig.savefig(output/"compartment.png", dpi=130)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--step", type=float, default=.1)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/compartment_pass")
    args = parser.parse_args()
    started = time.time()
    args.output.mkdir(parents=True, exist_ok=True)
    screen_s = [float(s) for s in np.round(np.arange(SIGMA_RANGE[0], SIGMA_RANGE[1]+1e-9, .25), 10)]
    s_axis = [float(s) for s in np.round(np.arange(SIGMA_RANGE[0], SIGMA_RANGE[1]+args.step/2, args.step), 10)]

    with ProcessPoolExecutor(args.workers) as pool:
        rows = list(pool.map(screen_row, [(name, s) for name in SCREEN for s in screen_s], chunksize=2))
        targets = []
        for name in SCREEN:
            candidates = sorted([(w, r["s"], z) for r in rows if r["design"] == name for w, z in r["estimates"]],
                                reverse=True)[:24]
            targets += [(name, s, z) for _, s, z in candidates]
        bands = pd.DataFrame(list(pool.map(resolve, targets)), columns=["design", "s", "z", "crossings", "width"])
    screen = pd.DataFrame(rows).drop(columns="estimates")
    screen.to_csv(args.output/"screen_by_sigma.csv", index=False)
    bands.to_csv(args.output/"screen_resolved_bands.csv", index=False)
    summary = screen.groupby("design", sort=False).agg(type_iv=("type_iv", "sum"),
                                                       samples_with_type_iv=("samples_with_type_iv", "sum"),
                                                       unresolved=("unresolved", "sum")).reset_index()
    band_summary = bands.groupby("design").agg(resolved_crossings=("crossings", "sum"),
                                               samples_with_band=("width", lambda w: int((w > 0).sum())),
                                               widest_band=("width", "max")).reset_index()
    summary = summary.merge(band_summary, on="design", how="left").fillna(
        {"resolved_crossings": 0, "samples_with_band": 0, "widest_band": 0.})
    summary.to_csv(args.output/"design_screen.csv", index=False)
    pd.set_option("display.width", 250)
    print(summary.to_string(index=False), round(time.time()-started, 1), flush=True)

    checks, demand, trips, arrivals = {}, [], {}, []
    for name in DESIGNS:
        with ProcessPoolExecutor(args.workers) as pool:
            gate = pd.DataFrame([r for chunk in pool.map(
                gate_row, [(name, s, PER_PANEL, choreography.JET_STEP, args.step, True) for s in s_axis],
                chunksize=2) for r in chunk])
            refined = pd.DataFrame([r for chunk in pool.map(
                gate_row, [(name, s, 2*PER_PANEL, choreography.JET_STEP/2, args.step, False) for s in s_axis],
                chunksize=2) for r in chunk])
            top = gate.nlargest(choreography.RESOLVED_SAMPLES, "estimated_band_width")
            top = top[top.estimated_band_width > 0]
            resolved = pd.DataFrame(list(pool.map(resolve, [(name, float(r.s), float(r.z)) for _, r in top.iterrows()])),
                                    columns=["design", "s", "z", "crossings", "width"])
        gate.insert(0, "design", name)
        gate.to_csv(args.output/f"gate_samples_{name}.csv.gz", index=False, compression={"method": "gzip", "mtime": 0},
                    float_format="%.7g")
        resolved.to_csv(args.output/f"resolved_bands_{name}.csv", index=False)
        per_sigma = gate.groupby("s")[["nec_content", "negative_energy", "positive_energy"]].sum()*args.step
        zone_cols = [c for c in gate.columns if c.startswith("nec_content_")]
        zones = (gate[zone_cols].sum()*args.step*args.step).to_dict()
        total_volume = gate[["violating_volume_r", "violating_volume_z", "violating_volume_phi", "type_i_volume",
                             "ordinary_volume"]].sum()
        checks[name] = {
            "gate_samples": len(gate), "gate_type_i": int(gate.layer_type_i.sum()),
            "gate_type_iv": int(gate.layer_type_iv.sum()+gate.core_type_iv.sum()),
            "gate_other": int(gate.layer_other.sum()),
            "refined_type_i": int(refined.layer_type_i.sum()),
            "refined_type_iv": int(refined.layer_type_iv.sum()+refined.core_type_iv.sum()),
            "refined_other": int(refined.layer_other.sum()),
            "estimated_band_samples": int((gate.estimated_band_width > 0).sum()),
            "resolved_crossings": int(resolved.crossings.sum()), "samples_with_band": int((resolved.width > 0).sum()),
            "max_band_width": float(resolved.width.max()) if len(resolved) else 0.,
            "envelope_violations": int((gate.envelope_ratio > 1).sum()),
            "worst_envelope_ratio": float(gate.envelope_ratio.max()),
            "core_min_null": float(gate.core_min_null.min()), "layer_min_null": float(gate.layer_min_null.min())}
        demand.append({"design": name, "peak_nec_content": float(per_sigma.nec_content.max()),
                       "nec_content_over_sigma": float(per_sigma.nec_content.sum()*args.step),
                       "peak_negative_energy": float(-per_sigma.negative_energy.min()),
                       "peak_positive_energy": float(per_sigma.positive_energy.max()),
                       "peak_stress": float(gate.max_abs_component.max()), "max_alpha": float(gate.max_alpha.max()),
                       "max_source_speed_vs_static": float(gate.max_source_speed_vs_static.max()),
                       "violating_share_r": float(total_volume.violating_volume_r/total_volume.type_i_volume),
                       "violating_share_z": float(total_volume.violating_volume_z/total_volume.type_i_volume),
                       "violating_share_phi": float(total_volume.violating_volume_phi/total_volume.type_i_volume),
                       "ordinary_share": float(total_volume.ordinary_volume/total_volume.type_i_volume),
                       **zones})
        trips[name] = passenger(name)
        arrivals.append(arrival(name, trips[name]))
        print(name, json.dumps(checks[name]), json.dumps(demand[-1]), json.dumps(arrivals[-1]),
              round(time.time()-started, 1), flush=True)
    pd.DataFrame(demand).to_csv(args.output/"demand.csv", index=False)
    pd.DataFrame(arrivals).to_csv(args.output/"arrival_and_passenger.csv", index=False)
    pd.concat(trips.values()).to_csv(args.output/"passenger_history.csv.gz", index=False,
                                     compression={"method": "gzip", "mtime": 0}, float_format="%.9g")
    figure(args.output, trips)
    manifest = {
        "completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time()-started, 1), "workers": args.workers, "step": args.step,
        "sigma_range": list(SIGMA_RANGE), "margin": MARGIN, "per_panel": PER_PANEL, "noise_floor": NOISE_FLOOR,
        "designs": DESIGNS, "screen": SCREEN, "zones": ZONES,
        "service_defaults": cs.CompartmentService().__dict__, "checks": checks,
        "software_sha256": {path: sha256_file(ROOT/"toolkit/adm_harness_cli"/path) for path in (
            "adm_harness/compartment_service.py", "adm_harness/axial_track.py",
            "adm_harness/axial_einstein_generated.py", "adm_harness/constant_radius_track.py",
            "adm_harness/source_scaling.py", "scripts/run_compartment_pass.py")},
    }
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=1, default=str)+"\n")


if __name__ == "__main__":
    main()
