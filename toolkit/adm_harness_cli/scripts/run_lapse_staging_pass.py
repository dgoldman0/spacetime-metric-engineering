#!/usr/bin/env python3
"""Lapse-for-stretch and time-staging pass of the one-space rail; emit data only.

The demand census found that the standing energy follows the stretch alone.
This pass removes the stretch everywhere (support and pre-sheath) and makes
the lapse do the pre-sheath's work: a flat support with a convex packet lapse
plateau, live windows that switch on inside the service domain with the
lapse leading and lagging the shift, and a lapse sheath. With a flat spatial
metric the energy density is -(A beta_r / alpha)^2 / (32 pi), so the standing
energy vanishes. The staged variant carries the sheath with the packet on a
schedule, so the standing geometry is flat space.

The run screens the design choices near the packet (node types and
root-found bands), then gives both designs the full treatment: the gate with
band resolution and refinement, the demand census, the packet's clock rate,
the path-aware audits and light through the standing geometry. Narrative
interpretation is maintained manually in supporting_reports.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, replace
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
import run_constant_radius_service_checks as service_checks
import run_demand_census as census
from adm_harness import axial_track as ax
from adm_harness.constant_radius_track import packet_position, packet_velocity, service_fields, track_scalars
from adm_harness.source_ledger import live_packet_end, sha256_file, stage_name
from adm_harness.warped_product import evaluate_spherical_demand

ROOT = Path(__file__).resolve().parents[3]
LANE = "lane_2p1"
SIGMA_START, SCREEN_END, STANDING = -8., 3., 10.
Z_MAX = 10.
NOISE_FLOOR = choreography.NOISE_FLOOR
PER_PANEL = 12
LAPSE_SERVICE = dict(C0=1., B0=1., lam=1., eta_N=0., support_shell_overlay_enabled=False,
                     support_shell_clock_lapse_log_gain=0., standing_support_packet_smooth_split_null_cushion_log_gain=0.,
                     standing_support_packet_beta_rematch_temporal_profile="minjerk",
                     standing_support_packet_lapse_log_gain=4., standing_support_packet_lapse_radius_multiplier=7.8,
                     standing_support_packet_lapse_width_multiplier=15.)
LAPSE_TRACK = dict(live_start=-2.4, lapse_lead=1., lapse_release_lag=1.5, lapse_window_profile="compact_smoothstep7",
                   lapse_convexity=.3, service_inner=7.5, track_half_length=8.5)
LAPSE_STACK = {**{k: v for k, v in choreography.WIDE_STACK.items() if not k.startswith("conformal")},
               "sheath_log_lapse": 1.}
FOLLOW = dict(sheath_follow=(2.5, 1.), sheath_schedule=(-4., 1.5, 1.))
DESIGNS = {
    "lapse_static": dict(service=LAPSE_SERVICE, track=LAPSE_TRACK, stack=LAPSE_STACK),
    "lapse_staged": dict(service=LAPSE_SERVICE, track=LAPSE_TRACK, stack={**LAPSE_STACK, **FOLLOW}),
}
UNGATED = dict(live_start=None, lapse_lead=0., lapse_release_lag=0.)
SCREEN = {
    **DESIGNS,
    "ungated_windows": dict(service=LAPSE_SERVICE, track={**LAPSE_TRACK, **UNGATED}, stack=LAPSE_STACK),
    "flat_plateau": dict(service=LAPSE_SERVICE, track={**LAPSE_TRACK, "lapse_convexity": 0.}, stack=LAPSE_STACK),
    "convexity_0p05": dict(service=LAPSE_SERVICE, track={**LAPSE_TRACK, "lapse_convexity": .05}, stack=LAPSE_STACK),
    "packet_lapse_e3": dict(service={**LAPSE_SERVICE, "standing_support_packet_lapse_log_gain": 3.},
                            track=LAPSE_TRACK, stack=LAPSE_STACK),
    "sheath_e4": dict(service=LAPSE_SERVICE, track=LAPSE_TRACK, stack={**LAPSE_STACK, "sheath_log_lapse": 4.}),
    "sheath_e0p5": dict(service=LAPSE_SERVICE, track=LAPSE_TRACK, stack={**LAPSE_STACK, "sheath_log_lapse": .5}),
    "no_sheath": dict(service=LAPSE_SERVICE, track=LAPSE_TRACK, stack={**LAPSE_STACK, "sheath_log_lapse": 0.}),
    "flat_plateau_e10": dict(service={**LAPSE_SERVICE, "standing_support_packet_lapse_log_gain": 10.},
                             track={**LAPSE_TRACK, "lapse_convexity": 0.},
                             stack={**LAPSE_STACK, "sheath_log_lapse": 8.}),
}
NARROW_EDGE = {"standing_support_packet_lapse_radius_multiplier": 10., "standing_support_packet_lapse_width_multiplier": 5.}
CUTOFF_IN = {"service_inner": 4., "track_half_length": 5.}
SHAPES = {
    "narrow_edge_cutoff_in": dict(service={**LAPSE_SERVICE, **NARROW_EDGE}, track={**LAPSE_TRACK, **CUTOFF_IN},
                                  stack=LAPSE_STACK),
    "wide_edge_cutoff_in": dict(service=LAPSE_SERVICE, track={**LAPSE_TRACK, **CUTOFF_IN}, stack=LAPSE_STACK),
}
EARLIER = {
    "census_design": dict(service={}, track={}, stack=choreography.WIDE_STACK),
    "amplitude_design": dict(service=dict(C0=1., B0=1., lam=6.),
                             track={}, stack={**choreography.WIDE_STACK, "conformal_log_scale": 7.}),
}
CATALOGUE = {**SCREEN, **SHAPES, **EARLIER}


def params_for(name):
    return replace(choreography.params_for(LANE), **CATALOGUE[name]["service"])


def track_for(name):
    return replace(choreography.track_for(LANE, "static"), **CATALOGUE[name]["track"])


def design_for(name, jet_step=choreography.JET_STEP):
    return ax.AxialTrackDesign(track=track_for(name), jet_step=jet_step, **CATALOGUE[name]["stack"])


def service_at(name, s, ell):
    track = track_for(name)
    return service_fields(s, ell, params_for(name), standing=True, packet_path=track.packet_path,
                          lapse_lag=track.lapse_release_lag, live_start=track.live_start, lapse_lead=track.lapse_lead,
                          lapse_profile=track.lapse_window_profile, lapse_convexity=track.lapse_convexity)


def resolve(jet, design, s, z, radius):
    """Root-find every flux-carrying null-sum crossing across radius and measure any Type IV band."""
    tensor = ax.frame_tensor(jet, radius, design, z=z, s=s)
    widest, crossings = 0., 0
    for i in (2, 1):
        total = tensor[:, 0, 0]+tensor[:, i, i]
        for c in np.flatnonzero(np.sign(total[:-1])*np.sign(total[1:]) < 0):
            root = brentq(lambda x: (lambda t: t[0, 0]+t[i, i])(ax.frame_tensor(jet, [x], design, z=z, s=s)[0]),
                          radius[c], radius[c+1], xtol=1e-15)
            at_root = ax.frame_tensor(jet, [root], design, z=z, s=s)[0]
            if abs(at_root[0, i]) <= 1e-14*max(np.max(np.abs(at_root)), 1e-300):
                continue
            crossings += 1
            for span in (1e-3, 1e-5, 1e-7, 1e-9):
                fine = np.linspace(root-span, root+span, 2001)
                kinds = ax.classify(ax.frame_tensor(jet, fine, design, z=z, s=s), floor=1e-12)["type"]
                band = fine[kinds == ax.TYPE_IV]
                if len(band):
                    widest = max(widest, band.max()-band.min()+(fine[1]-fine[0]))
                    break
    return crossings, widest


def screen_row(task):
    """Node types, envelope and estimated bands within four units of the packet at one sigma.

    Offsets run at 0.02 within one unit of the packet, which resolves the packet bump's edges, and at 0.1 beyond.
    """
    name, s = task
    design, params = design_for(name), params_for(name)
    radius = ax.wall_nodes(design, PER_PANEL)[0]
    path = design.track.packet_path
    centre = packet_position(s, path)
    row = {"design": name, "s": s, "type_iv": 0, "samples_with_type_iv": 0, "unresolved": 0,
           "worst_envelope_ratio": 0., "estimates": []}
    offsets = np.concatenate([np.arange(-4., -1., .1), np.arange(-1., 1., .02), np.arange(1., 4.+1e-9, .1)])
    for z in np.round(centre+offsets, 10):
        z = float(z)
        jet = ax.service_jet(s, z, params, design)
        tensor = ax.frame_tensor(jet, radius, design, z=z, s=s)
        kinds = ax.classify(tensor, floor=NOISE_FLOOR)["type"]
        count = int((kinds == ax.TYPE_IV).sum())
        row["type_iv"] += count
        row["samples_with_type_iv"] += int(count > 0)
        row["unresolved"] += int(np.isin(kinds, [ax.UNRESOLVED, ax.TYPE_II_III]).sum())
        row["worst_envelope_ratio"] = max(row["worst_envelope_ratio"],
                                          2*design.core_radius*abs(jet["z"][2])/math.exp(jet["v"][0]))
        width = choreography.band_widths(tensor, radius)
        if width > 0:
            row["estimates"].append((width, z))
    row["estimates"] = sorted(row["estimates"], reverse=True)[:3]
    return row


def screen_resolve(task):
    name, s, z = task
    design = design_for(name)
    return (name, s, z, *resolve(ax.service_jet(s, z, params_for(name), design), design, s, z,
                                 ax.wall_nodes(design, 24)[0]))


def stress_row(task):
    """Largest orthonormal stress component over the rail at one sigma, and where it sits."""
    name, s, z_axis = task
    design, params = design_for(name), params_for(name)
    radius = np.concatenate([[0.], ax.wall_nodes(design, PER_PANEL)[0]])
    worst, where = 0., math.nan
    for z in z_axis:
        tensor = ax.frame_tensor(ax.service_jet(s, float(z), params, design), radius, design, z=float(z), s=s)
        value = float(np.max(np.abs(tensor)))
        if value > worst:
            worst, where = value, float(z)
    return {"design": name, "s": s, "max_abs_component": worst, "z": where}


def gate_jets(task):
    name, s, z_axis, jet_step = task
    design, params = design_for(name, jet_step), params_for(name)
    out = np.empty((len(z_axis), 3, len(choreography.KEYS)))
    for index, z in enumerate(z_axis):
        jet = ax.service_jet(s, float(z), params, design)
        out[index] = np.stack([jet[key] for key in choreography.KEYS], axis=1)
    return s, out


def gate_row(task):
    name, s, z_axis, jets, per_panel, jet_step = task
    design = design_for(name, jet_step)
    radius = ax.wall_nodes(design, per_panel)[0]
    rows = []
    for z, array in zip(z_axis, jets):
        jet = {key: array[:, index] for index, key in enumerate(choreography.KEYS)}
        layer = ax.frame_tensor(jet, radius, design, z=float(z), s=s)
        core = ax.frame_tensor(jet, [0.], design, z=float(z), s=s)
        kinds = ax.classify(np.concatenate([core, layer]), floor=NOISE_FLOOR)["type"][1:]
        null = ax.min_null_energy(np.concatenate([core, layer]))
        rows.append({"s": s, "z": float(z), "layer_type_i": int((kinds == ax.TYPE_I).sum()),
                     "layer_type_iv": int((kinds == ax.TYPE_IV).sum()),
                     "layer_other": int(np.isin(kinds, [ax.UNRESOLVED, ax.TYPE_II_III]).sum()),
                     "core_min_null": float(null[0]), "layer_min_null": float(null[1:].min()),
                     "estimated_band_width": choreography.band_widths(layer, radius),
                     "envelope_ratio": 2*design.core_radius*abs(jet["z"][2])/math.exp(jet["v"][0])})
    return rows


def gate_resolve(task):
    name, s, z = task
    design = design_for(name)
    return (s, z, *resolve(ax.service_jet(s, z, params_for(name), design), design, s, z,
                           ax.wall_nodes(design, 24)[0]))


def census_slice(task):
    name, s, z = task
    design = design_for(name)
    jet = ax.service_jet(s, z, params_for(name), design)
    nodes, weights = ax.wall_nodes(design, PER_PANEL)
    radius = np.concatenate([[0.], nodes])
    tensor = ax.frame_tensor(jet, radius, design, z=z, s=s)
    fields = ax.radial_fields(jet, radius, design, z=z, s=s)
    coord = np.concatenate([[math.pi*design.core_radius**2], weights*2*math.pi*nodes])
    rows = census.zone_rows(census.point_census(tensor, fields, coord, coord*fields["A"]), radius, s, z, name)
    exterior = float(np.max(np.abs(ax.frame_tensor(jet, [design.outer_radius+.5], design, z=z, s=s))))
    for row in rows:
        row["exterior_max_abs"] = exterior
    return rows


def packet_clock(name):
    """Packet proper time from sigma = -8 to the track end, at the path speed, with the arrival and lead."""
    path = design_for(name).track.packet_path
    arrival = brentq(lambda s: packet_position(s, path)-choreography.TRACK_END, SIGMA_START, 100.)
    sigma = np.linspace(SIGMA_START, arrival, 6001)
    rate, norm = [], -np.inf
    params = params_for(name)
    for s in sigma:
        centre, speed = packet_position(s, path), packet_velocity(s, path)
        f = service_at(name, s, centre)
        rate.append(math.sqrt(max(f["alpha"]**2-f["gamma_ll"]*(speed+f["beta"])**2, 0.)))
        for offset in np.linspace(-params.Rpass, params.Rpass, 7):
            g = service_at(name, s, centre+offset)
            norm = max(norm, (-g["alpha"]**2+g["gamma_ll"]*(speed+g["beta"])**2)/g["alpha"]**2)
    rate = np.array(rate)
    return {"design": name, "arrival_track_end": arrival,
            "lead_over_light": choreography.ENTRY[0]+choreography.TRACK_END-choreography.ENTRY[1]-arrival,
            "exterior_time": arrival-SIGMA_START, "packet_proper_time": float(np.trapezoid(rate, sigma)),
            "peak_clock_rate": float(rate.max()), "worst_packet_norm_over_alpha2": norm}


def ledger_row(task):
    name, s, l = task
    params, track = params_for(name), track_for(name)
    path = track.packet_path
    centre = packet_position(s, path)
    fields = track_scalars(s, l, params, track)
    extra = service_at(name, s, l)
    alpha, beta, radial = fields["alpha"], fields["beta"], fields["gamma_ll"]
    result = evaluate_spherical_demand(s, l, params, .0025, .0025,
                                       scalar_evaluator=lambda a, b, p: track_scalars(a, b, p, track))
    speed = packet_velocity(s, path)
    live = bool(abs(l-centre) <= params.Rpass and SIGMA_START <= s <= live_packet_end(params))
    return {"s": s, "l": l, "stage": stage_name(s, params), "region": choreography.region(s, l, centre, params),
            "inside_packet_geom": abs(l-centre) <= params.Rpass, "inside_packet_live": live,
            "alpha": alpha, "beta": beta, "gamma_ll": radial, "gamma_omega": fields["gamma_omega"],
            "packet_norm": -alpha*alpha+radial*(speed+beta)**2,
            "packet_norm_field": -alpha*alpha+radial*(extra["U_packet"]/extra["B"]+beta)**2,
            "gtt": -alpha*alpha+radial*beta*beta, "U_beta": extra["U_beta"], "U_packet": speed*extra["B"],
            "U_field": extra["U_packet"], "B": extra["B"], "q": extra["q"], "W": extra["W"],
            "rho_euler": result["rho"], "p_l_unit": result["p_l"], "j_l_unit": result["j_l"],
            "p_omega_unit": result["p_omega"], "Tkk_plus": alpha*alpha*result["null_energy_outgoing"],
            "Tkk_minus": alpha*alpha*result["null_energy_ingoing"],
            "Tkk_min_radial": alpha*alpha*min(result["null_energy_outgoing"], result["null_energy_ingoing"]),
            "stress_algebraic_type": result["stress_algebraic_type"]}


def audits(name, args, audit_log):
    """Service audits on the axis ledger; the sheath lies off the axis, so one ledger serves both designs."""
    s_axis = np.round(np.arange(SIGMA_START, 15.+1e-9, 15/171), 10)
    l_axis = np.round(np.arange(-Z_MAX, Z_MAX+1e-9, .1), 10)
    with ProcessPoolExecutor(args.workers) as pool:
        ledger = pd.DataFrame(pool.map(ledger_row, [(name, float(s), float(l)) for s in s_axis for l in l_axis],
                                       chunksize=64))
    base = args.runs/name
    base.mkdir(parents=True, exist_ok=True)
    path = base/"source_ledger_point_ledger.csv"
    ledger.to_csv(path, index=False)
    for script, extra in (
            ("run_horizon_escape_ladder.py", ["--outdir", base/"escape_seed120", "--seeds-per-scope", 120,
                                              "--max-steps", 12000]),
            ("run_entry_packet_reachability.py", ["--outdir", base/"entry_reachability", "--entry-side", "lower",
                                                  "--entry-side", "upper"]),
            ("run_scheduled_adm_probe_evolution.py", ["--outdir", base/"scheduled_probe", "--red-tag-seeds", 120,
                                                      "--max-steps", 12000])):
        service_checks.audit(script, ["--point-ledger", path, "--label", name, *extra], audit_log)
    service_checks.audit("run_trace_expansion_audit.py", ["--point-ledger", path, "--seeds",
                         base/"scheduled_probe/scheduled_adm_probe_seeds.csv", "--outdir", base/"trace_expansion",
                         "--label", name], audit_log)
    service_checks.audit("run_dense_congruence_caustic_audit.py", [
        "--point-ledger", path, "--trace-traces", base/"trace_expansion/trace_expansion_audit_traces.csv",
        "--outdir", base/"dense_bundles_all_centers", "--label", name, "--no-require-both-shrinking",
        "--trace-step-scale", choreography.BUNDLE_STEP_SCALE, "--max-steps", 60000], audit_log)
    traces = pd.read_csv(base/"scheduled_probe/scheduled_adm_probe_traces.csv")
    centre = traces[traces.probe_family == "packet_centerline"]
    transit = traces[traces.trace_outcome == "s_upper_boundary"]
    live = ledger[ledger.inside_packet_live]
    escape = pd.read_csv(base/"escape_seed120/horizon_escape_trace_summary.csv")
    reach = pd.read_csv(base/"entry_reachability/entry_packet_reachability_summary.csv")
    probe = pd.read_csv(base/"scheduled_probe/scheduled_adm_probe_summary.csv")
    expansion = pd.read_csv(base/"trace_expansion/trace_expansion_audit_summary.csv")
    bundles = pd.read_csv(base/"dense_bundles_all_centers/dense_congruence_caustic_summary.csv")
    return {"design": name, "ledger_points": len(ledger), "live_packet_points": len(live),
            "spacelike_live_points": int((live.packet_norm >= 0).sum()),
            "max_live_packet_norm": float(live.packet_norm.max()),
            "escape_traces": int(escape.traces.sum()), "escape_expected": int(escape.expected_escape_count.sum()),
            "escape_escaped": int(escape.any_radial_escape_count.sum()),
            "escape_stalled": int(escape.invalid_or_stalled_count.sum()),
            "reachable_packet_hits": int(reach.reachable_packet_hits.sum()),
            "probe_traces": int(probe.traces.sum()), "probe_escaped": int(probe.radial_escape_count.sum()),
            "centerline_probes": len(centre),
            "centerline_escaped": int(centre.trace_outcome.isin(["l_lower_boundary", "l_upper_boundary"]).sum()),
            "centerline_max_packet_norm": float(centre.max_packet_norm_along_trace.max()),
            "probes_in_transit_at_window_end": len(transit),
            "in_transit_min_null_speed": float(transit.min_branch_abs_margin_along_trace.min()) if len(transit)
            else math.nan,
            "traces_entering_both_shrinking": int(expansion.traces_entering_both_shrinking.sum()),
            "bundle_crossings": int(bundles.crossing_samples.sum()),
            "bundle_caustic_like": int(bundles.caustic_like_collapse.sum()),
            "bundle_min_l_width_ratio": float(bundles.min_common_l_width_ratio.min())}


def channel_fields(task):
    name, z, radius = task
    design = design_for(name)
    fields = ax.radial_fields(ax.service_jet(STANDING, z, params_for(name), design), radius, design, z=z,
                              s=STANDING)
    return np.log(fields["alpha"]), np.log(fields["A"])


def light_channel(name, pool, step=.05):
    """Fastest light from the entry to the track end on the axis through the standing geometry."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import dijkstra
    z_axis = np.round(np.arange(choreography.ENTRY[1], choreography.TRACK_END+step/2, step), 10)
    radius = np.round(np.arange(0., design_for(name).outer_radius+.75+step/2, step), 10)
    parts = list(pool.map(channel_fields, [(name, float(z), radius) for z in z_axis]))
    log_alpha, log_a = np.array([p[0] for p in parts]), np.array([p[1] for p in parts])
    nz, nr = log_alpha.shape
    index = np.arange(nz*nr).reshape(nz, nr)
    rows, cols, costs = [], [], []
    for a, b in ((a, b) for a in range(-4, 5) for b in range(-4, 5) if math.gcd(abs(a), abs(b)) == 1):
        i0, i1, k0, k1 = max(0, -a), nz-max(0, a), max(0, -b), nr-max(0, b)
        here, there = (slice(i0, i1), slice(k0, k1)), (slice(i0+a, i1+a), slice(k0+b, k1+b))
        rows.append(index[here].ravel())
        cols.append(index[there].ravel())
        costs.append((np.sqrt((np.exp(.5*(log_a[here]+log_a[there]))*a*step)**2+(b*step)**2)
                      / np.exp(.5*(log_alpha[here]+log_alpha[there]))).ravel())
    graph = coo_matrix((np.concatenate(costs), (np.concatenate(rows), np.concatenate(cols))),
                       shape=(nz*nr, nz*nr)).tocsr()
    distance = dijkstra(graph, indices=index[0, 0])
    return {"design": name, "max_along_track_light_speed": float(np.exp(log_alpha-log_a).max()),
            "light_arrival": choreography.ENTRY[0]+float(distance[index[-1, 0]])}


def figure(frames, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for name, frame in frames.items():
        by_sigma = frame.groupby("s")[["nec_content_coord", "eulerian_negative"]].sum()*.1
        axes[0].plot(by_sigma.index, by_sigma.nec_content_coord, label=name)
        axes[1].plot(by_sigma.index, -by_sigma.eulerian_negative, label=name)
    reference = pd.read_csv(ROOT/"supporting_reports/data/amplitude_pass/standing_totals.csv").iloc[0]
    axes[0].axhline(reference.nec_content_coord, color="k", ls="--", lw=.8, label="amplitude pass, standing")
    axes[1].axhline(-reference.eulerian_negative, color="k", ls="--", lw=.8, label="amplitude pass, standing")
    axes[0].set_ylabel("instantaneous negative-null content")
    axes[1].set_ylabel("instantaneous negative energy")
    axes[1].set_yscale("symlog", linthresh=1e-8)
    for panel in axes:
        panel.set_xlabel("sigma")
        panel.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(output/"transit_demand.png", dpi=140)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--step", type=float, default=.1)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/lapse_staging_pass")
    parser.add_argument("--runs", type=Path, default=service_checks.RUNS/"lapse_staging_pass")
    parser.add_argument("--screen-only", action="store_true")
    args = parser.parse_args()
    started = time.time()
    args.output.mkdir(parents=True, exist_ok=True)
    s_axis = np.round(np.arange(SIGMA_START, STANDING+args.step/2, args.step), 10)
    z_axis = np.round(np.arange(-Z_MAX, Z_MAX+args.step/2, args.step), 10)
    screen_s = [float(s) for s in np.round(np.arange(SIGMA_START, SCREEN_END+1e-9, .2), 10)]

    with ProcessPoolExecutor(args.workers) as pool:
        rows = list(pool.map(screen_row, [(name, s) for name in SCREEN for s in screen_s], chunksize=2))
        targets = []
        for name in SCREEN:
            candidates = sorted([(w, r["s"], z) for r in rows if r["design"] == name for w, z in r["estimates"]],
                                reverse=True)[:24]
            targets += [(name, s, z) for _, s, z in candidates]
        bands = pd.DataFrame(list(pool.map(screen_resolve, targets)), columns=["design", "s", "z", "crossings", "width"])
        clocks = pd.DataFrame(list(pool.map(packet_clock, list(DESIGNS)+list(EARLIER))))
        shape_z = np.round(np.arange(-Z_MAX, Z_MAX+1e-9, .05), 10)
        stress = pd.DataFrame(list(pool.map(stress_row, [(name, float(s), shape_z) for name in
                                                          ["lapse_static", *SHAPES]
                                                          for s in np.round(np.arange(-4.5, 3.+1e-9, .1), 10)],
                                            chunksize=2)))
    screen = pd.DataFrame(rows).drop(columns="estimates")
    screen.to_csv(args.output/"screen_by_sigma.csv", index=False)
    bands.to_csv(args.output/"screen_resolved_bands.csv", index=False)
    summary = screen.groupby("design", sort=False).agg(
        type_iv=("type_iv", "sum"), samples_with_type_iv=("samples_with_type_iv", "sum"),
        unresolved=("unresolved", "sum"), worst_envelope_ratio=("worst_envelope_ratio", "max")).reset_index()
    band_summary = bands.groupby("design").agg(resolved_crossings=("crossings", "sum"),
                                               samples_with_band=("width", lambda w: int((w > 0).sum())),
                                               widest_band=("width", "max")).reset_index()
    summary = summary.merge(band_summary, on="design", how="left").fillna(
        {"resolved_crossings": 0, "samples_with_band": 0, "widest_band": 0.})
    summary.to_csv(args.output/"design_screen.csv", index=False)
    clocks.to_csv(args.output/"packet_clock.csv", index=False)
    stress.to_csv(args.output/"plateau_stress_by_sigma.csv", index=False)
    stress_table = stress.groupby("design", sort=False).agg(peak_stress=("max_abs_component", "max"),
                                                            median_peak_stress=("max_abs_component", "median"))
    stress_table.reset_index().to_csv(args.output/"plateau_stress.csv", index=False)
    print(stress_table.to_string(), flush=True)
    pd.set_option("display.width", 250)
    print(summary.to_string(index=False), flush=True)
    print(clocks.to_string(index=False), flush=True)
    print("screen", round(time.time()-started, 1), flush=True)

    checks, service, channel = {}, pd.DataFrame(), pd.DataFrame()
    if not args.screen_only:
        frames, standing_tables, transit_tables = {}, [], []
        for name in DESIGNS:
            with ProcessPoolExecutor(args.workers) as pool:
                gate = {}
                for label, jet_step, per_panel in (("gate", choreography.JET_STEP, PER_PANEL),
                                                    ("refined", choreography.JET_STEP/2, 2*PER_PANEL)):
                    jets = dict(pool.map(gate_jets, [(name, float(s), z_axis, jet_step) for s in s_axis]))
                    gate[label] = pd.DataFrame([r for chunk in pool.map(
                        gate_row, [(name, float(s), z_axis, jets[float(s)], per_panel, jet_step) for s in s_axis],
                        chunksize=2) for r in chunk])
                gate["gate"].to_csv(args.output/f"gate_samples_{name}.csv.gz", index=False,
                                    compression={"method": "gzip", "mtime": 0}, float_format="%.7g")
                top = gate["gate"].nlargest(choreography.RESOLVED_SAMPLES, "estimated_band_width")
                top = top[top.estimated_band_width > 0]
                resolved = pd.DataFrame(list(pool.map(gate_resolve, [(name, float(r.s), float(r.z))
                                                                     for _, r in top.iterrows()])),
                                        columns=["s", "z", "crossings", "width"])
                resolved.to_csv(args.output/f"resolved_bands_{name}.csv", index=False)
                frame = pd.DataFrame([r for chunk in pool.map(census_slice, [(name, float(s), float(z))
                                                                             for s in s_axis for z in z_axis],
                                                              chunksize=16) for r in chunk])
            frame["axial_zone"] = census.axial_zone(frame.z.values)
            frame.to_csv(args.output/f"zone_slices_{name}.csv.gz", index=False,
                         compression={"method": "gzip", "mtime": 0}, float_format="%.8g")
            frames[name] = frame
            standing = frame[frame.s == STANDING]
            standing_tables.append(census.tabulate(standing, args.step, ["variant"]))
            live = frame[frame.s < STANDING]
            peak = live.groupby("s")[["nec_content_coord", "eulerian_negative"]].sum()*args.step
            transit = census.tabulate(live, args.step, ["variant"])
            for column in [c for c in census.SUMS if c not in ("type_iv", "unresolved")]:
                transit[column] *= args.step
            transit["peak_nec_content"] = float(peak.nec_content_coord.max())
            transit["peak_negative_energy"] = float(-peak.eulerian_negative.min())
            transit_tables.append(transit)
            g, r = gate["gate"], gate["refined"]
            checks[name] = {
                "gate_samples": len(g), "gate_type_i": int(g.layer_type_i.sum()),
                "gate_type_iv": int(g.layer_type_iv.sum()), "gate_other": int(g.layer_other.sum()),
                "refined_type_i": int(r.layer_type_i.sum()), "refined_type_iv": int(r.layer_type_iv.sum()),
                "refined_other": int(r.layer_other.sum()), "estimated_band_samples": int((g.estimated_band_width > 0).sum()),
                "resolved_crossings": int(resolved.crossings.sum()), "samples_with_band": int((resolved.width > 0).sum()),
                "max_band_width": float(resolved.width.max()) if len(resolved) else 0.,
                "envelope_violations": int((g.envelope_ratio > 1).sum()),
                "worst_envelope_ratio": float(g.envelope_ratio.max()),
                "core_min_null": float(g.core_min_null.min()), "layer_min_null": float(g.layer_min_null.min()),
                "census_type_iv": int(frame.type_iv.sum()), "census_unresolved": int(frame.unresolved.sum()),
                "exterior_max_abs": float(frame.exterior_max_abs.max()),
                "start_matches_standing": float(np.max(np.abs(
                    frame[frame.s == frame.s.min()].sort_values(["z", "zone"])[census.SUMS].to_numpy()
                    - standing.sort_values(["z", "zone"])[census.SUMS].to_numpy())))}
            print(name, json.dumps(checks[name]), round(time.time()-started, 1), flush=True)
        pd.concat(standing_tables).to_csv(args.output/"standing_totals.csv", index=False)
        pd.concat(transit_tables).to_csv(args.output/"transit_totals.csv", index=False)
        figure(frames, args.output)
        with ProcessPoolExecutor(args.workers) as pool:
            channel = pd.DataFrame([light_channel("lapse_static", pool)])
        channel.to_csv(args.output/"light_channel.csv", index=False)
        audit_log = []
        service = pd.DataFrame([audits("lapse_static", args, audit_log)])
        service.to_csv(args.output/"service_summary.csv", index=False)
        checks["audit_log"] = audit_log
    manifest = {
        "completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time()-started, 1), "workers": args.workers, "step": args.step,
        "sigma_range": [float(s_axis[0]), float(s_axis[-1])], "screen_sigma_end": SCREEN_END, "z_max": Z_MAX,
        "lane": LANE, "lapse_service": LAPSE_SERVICE, "lapse_track": LAPSE_TRACK, "lapse_stack": LAPSE_STACK,
        "follow": FOLLOW, "screen": SCREEN, "shapes": SHAPES, "earlier": EARLIER, "per_panel": PER_PANEL,
        "noise_floor": NOISE_FLOOR,
        "checks": checks,
        "envelope_params_changed": {k: v for k, v in asdict(choreography.ENVELOPE).items()
                                    if v != asdict(choreography.BASE)[k]},
        "software_sha256": {path: sha256_file(ROOT/"toolkit/adm_harness_cli"/path) for path in (
            "adm_harness/axial_track.py", "adm_harness/axial_einstein_generated.py",
            "adm_harness/constant_radius_track.py", "scripts/run_choreography_pass.py",
            "scripts/run_demand_census.py", "scripts/run_lapse_staging_pass.py")},
    }
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=1, default=str)+"\n")
    print(service.T.to_string())
    print(channel.T.to_string())


if __name__ == "__main__":
    main()
