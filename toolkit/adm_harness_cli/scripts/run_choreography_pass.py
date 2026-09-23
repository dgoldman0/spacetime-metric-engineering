#!/usr/bin/env python3
"""Evaluate the path choreography of the one-space rail; emit data only.

Every packet window and the carry speeds follow one prescribed packet path:
the packet enters at (sigma, l) = (-1.4, -1.4), accelerates to a lane speed
inside the support, decelerates to a coasting speed below light as it leaves
the support, and its carrier releases as it passes l = 2.6. The packet lapse
window runs with the rematch shift. The script searches the choreography
timing for the lead over a light signal launched with the packet, evaluates
the chosen lanes on a static support and on a held support with the moving
carve, runs the one-space boundary-layer gate with refinement and band
resolution, and runs the along-track service audits on a path-aware ledger.
Narrative interpretation is maintained manually in supporting_reports.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, replace
from datetime import datetime, timezone
from functools import lru_cache
import itertools
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
import run_constant_radius_service_checks as service_checks
from adm_harness import axial_track as ax
from adm_harness.constant_radius_track import (
    ConstantRadiusTrackDesign, packet_position, packet_velocity, service_fields, track_scalars,
)
from adm_harness.source_ledger import live_packet_end, release_beta_interval, sha256_file, stage_name
from adm_harness.warped_product import evaluate_spherical_demand

ROOT = Path(__file__).resolve().parents[3]
KEYS = ("v", "s", "z", "ss", "sz", "zz")
BASE = service_checks.PARAMS
ENVELOPE = replace(BASE, standing_support_packet_lapse_log_gain=3., standing_support_packet_lapse_radius_multiplier=2.5,
                   standing_support_packet_lapse_schedule="live_only")
ENTRY = (-1.4, -1.4)
RELEASE_AT = 2.6
TRACK_END = 5.
WIDE_STACK = dict(conformal_log_scale=8., conformal_rise=(1.75, 2.), conformal_fall=(9.25, 2.),
                  sheath_log_lapse=8., sheath_rise=(3.75, 5.), sheath_fall=(9.25, 4.),
                  shift_layer=(4.25, 2.), stretch_layer=(9.25, 2.), lapse_layer=(9.25, 4.))
LANES = {"lane_1p5": 1.5, "lane_1p8": 1.8, "lane_2p1": 2.1}
TIMING = dict(t_accel=.3, t_decel=.4, v_out=.95, l_exit=2.4)
JET_STEP = .0025
NOISE_FLOOR = 1e-8
RESOLVED_SAMPLES = 60
CASES = {
    "lane_1p5__static": ("lane_1p5", "static", JET_STEP, 12),
    "lane_1p8__static": ("lane_1p8", "static", JET_STEP, 12),
    "lane_2p1__static": ("lane_2p1", "static", JET_STEP, 12),
    "lane_2p1__static__refined": ("lane_2p1", "static", JET_STEP/2, 24),
    "lane_2p1__held_carve": ("lane_2p1", "held", JET_STEP, 12),
}
AUDITED = ("lane_2p1__static", "lane_1p8__static")
# Bundle rays cross the packet lapse window, whose ledger gradients need a finer step than the audit
# default of 0.5; crossing counts are unchanged between 0.1 and 0.02.
BUNDLE_STEP_SCALE = .1
STANDING_SNAPSHOT = 9.


@lru_cache(maxsize=512)
def choreography(v_lane, t_accel, t_decel, v_out, l_exit, v_in=.9):
    """Packet path and aligned service parameters.

    The deceleration ends as the packet reaches l_exit; the catch windows span
    the deceleration, and the release is timed so that the live window closes
    as the packet passes RELEASE_AT.
    """
    base = (*ENTRY, v_in, v_lane, v_out, ENTRY[0], t_accel)
    decel = brentq(lambda d: packet_position(d+t_decel, base+(d, t_decel))-l_exit, ENTRY[0]+1e-3, 20.)
    path = base+(decel, t_decel)
    catch = decel+t_decel/2
    params = replace(ENVELOPE, x_catch_packet=catch, x_catch_beta=catch, w_catch_packet=t_decel/4,
                     w_catch_beta=t_decel/4)
    release = brentq(lambda s: packet_position(s, path)-RELEASE_AT, ENTRY[0], 80.)
    _, end = release_beta_interval(params)
    margin = live_packet_end(params)-end
    params = replace(params, x_beta=params.x_beta+(release-margin)-end)
    return path, params


def track_for(lane, support):
    path, _ = choreography(LANES[lane], **TIMING)
    return ConstantRadiusTrackDesign(standing_support=support == "static", hold_support=support == "held",
                                     packet_path=path)


def params_for(lane):
    return choreography(LANES[lane], **TIMING)[1]


def path_metrics(task):
    """Arrival times, lead over light and packet norms along one choreography."""
    name, v_lane, t_accel, t_decel, v_out, l_exit, support = task
    try:
        path, params = choreography(v_lane, t_accel, t_decel, v_out, l_exit)
    except ValueError:
        return None
    standing, hold = support == "static", support == "held"
    end = live_packet_end(params)
    worst_live = -np.inf
    for s in np.arange(ENTRY[0], end+1e-9, .02):
        centre, speed = packet_position(s, path), packet_velocity(s, path)
        for offset in np.linspace(-params.Rpass, params.Rpass, 15):
            f = service_fields(s, centre+offset, params, standing=standing, hold=hold, packet_path=path)
            for velocity in (speed, f["U_packet"]/f["B"]):
                worst_live = max(worst_live, (-f["alpha"]**2+f["gamma_ll"]*(velocity+f["beta"])**2)/f["alpha"]**2)
    arrival = brentq(lambda s: packet_position(s, path)-TRACK_END, ENTRY[0], 100.)
    worst_after = -np.inf
    for s in np.arange(end, arrival+1e-9, .02):
        f = service_fields(s, packet_position(s, path), params, standing=standing, hold=hold, packet_path=path)
        worst_after = max(worst_after, (-f["alpha"]**2+f["gamma_ll"]*(packet_velocity(s, path)+f["beta"])**2)
                          / f["alpha"]**2)
    light = ENTRY[0]+(TRACK_END-ENTRY[1])
    exit_time = brentq(lambda s: packet_position(s, path)-l_exit, ENTRY[0], 100.)
    return {"name": name, "support": support, "v_lane": v_lane, "t_accel": t_accel, "t_decel": t_decel,
            "v_out": v_out, "l_exit": l_exit, "decel_start": path[7], "live_end": end,
            "support_exit_time": exit_time, "arrival_track_end": arrival, "light_arrival": light,
            "lead_over_light": light-arrival, "end_to_end_speed": (TRACK_END-ENTRY[1])/(arrival-ENTRY[0]),
            "worst_live_norm_over_alpha2": worst_live, "worst_coast_norm_over_alpha2": worst_after}


def jets_row(task):
    case, s, z_axis = task
    lane, support, step, _ = CASES[case]
    design = ax.AxialTrackDesign(track=track_for(lane, support), jet_step=step)
    out = np.empty((len(z_axis), 3, len(KEYS)))
    for index, z in enumerate(z_axis):
        jet = ax.service_jet(s, z, params_for(lane), design)
        out[index] = np.stack([jet[key] for key in KEYS], axis=1)
    return case, s, out


def design_for(case):
    lane, support, step, _ = CASES[case]
    return ax.AxialTrackDesign(track=track_for(lane, support), jet_step=step, **WIDE_STACK)


def band_widths(tensor, radius):
    scale = np.max(np.abs(tensor))
    widths = []
    for i in (2, 1):
        total = tensor[:, 0, 0]+tensor[:, i, i]
        flux = tensor[:, 0, i]
        for c in np.flatnonzero(np.sign(total[:-1])*np.sign(total[1:]) < 0):
            weight = total[c]/(total[c]-total[c+1])
            crossing_flux = flux[c]+weight*(flux[c+1]-flux[c])
            if abs(crossing_flux) > 1e-12*scale:
                widths.append(2*abs(crossing_flux)*(radius[c+1]-radius[c])/abs(total[c+1]-total[c]))
    return max(widths) if widths else 0.


def layer_row(task):
    case, s, z_axis, jets = task
    design = design_for(case)
    lane = CASES[case][0]
    path, params = choreography(LANES[lane], **TIMING)
    radius, weights = ax.wall_nodes(design, CASES[case][3])
    area = weights*2*math.pi*radius
    rows = []
    for z, array in zip(z_axis, jets):
        jet = {key: array[:, index] for index, key in enumerate(KEYS)}
        layer = ax.frame_tensor(jet, radius, design, z=float(z))
        core = ax.frame_tensor(jet, [0.], design, z=float(z))
        exterior = ax.frame_tensor(jet, [design.outer_radius+.5], design, z=float(z))
        kinds = ax.classify(np.concatenate([core, layer]), floor=NOISE_FLOOR)
        null = ax.min_null_energy(np.concatenate([core, layer]))
        types = kinds["type"][1:]
        live = ENTRY[0] <= s <= live_packet_end(params) and abs(z-packet_position(s, path)) <= params.Rpass
        rows.append({"case": case, "s": s, "z": z, "live": live, "core_type": kinds["type"][0], "core_min_null": null[0],
                     "layer_type_i": int((types == ax.TYPE_I).sum()), "layer_type_iv": int((types == ax.TYPE_IV).sum()),
                     "layer_type_ii_iii": int((types == ax.TYPE_II_III).sum()),
                     "layer_unresolved": int((types == ax.UNRESOLVED).sum()),
                     "layer_min_null": float(null[1:].min()),
                     "layer_negative_null": float(np.sum(area*np.maximum(-null[1:], 0))),
                     "estimated_band_width": band_widths(layer, radius),
                     "envelope_ratio": 2*design.core_radius*abs(jet["z"][2])/math.exp(jet["v"][0]),
                     "exterior_max_abs": float(np.max(np.abs(exterior)))})
    return rows


def resolve_bands(task):
    case, s, z = task
    design = design_for(case)
    jet = ax.service_jet(s, z, params_for(CASES[case][0]), design)
    radius, _ = ax.wall_nodes(design, 24)
    tensor = ax.frame_tensor(jet, radius, design, z=z)
    widest, crossings = 0., 0
    for i in (2, 1):
        total = tensor[:, 0, 0]+tensor[:, i, i]
        for c in np.flatnonzero(np.sign(total[:-1])*np.sign(total[1:]) < 0):
            root = brentq(lambda x: (lambda t: t[0, 0]+t[i, i])(ax.frame_tensor(jet, [x], design, z=z)[0]),
                          radius[c], radius[c+1], xtol=1e-15)
            at_root = ax.frame_tensor(jet, [root], design, z=z)[0]
            if abs(at_root[0, i]) <= 1e-14*max(np.max(np.abs(at_root)), 1e-300):
                continue
            crossings += 1
            for span in (1e-3, 1e-5, 1e-7, 1e-9):
                fine = np.linspace(root-span, root+span, 2001)
                band = fine[ax.classify(ax.frame_tensor(jet, fine, design, z=z), floor=1e-12)["type"] == ax.TYPE_IV]
                if len(band):
                    widest = max(widest, band.max()-band.min()+(fine[1]-fine[0]))
                    break
    return case, s, z, crossings, widest


def region(s, l, centre, params):
    al = abs(l)
    if abs(l-centre) <= params.Rpass:
        return "packet_in_support" if al <= params.Rth else "packet_outer"
    if al <= .65*params.Rth:
        return "core_throat"
    if al <= 1.2*params.Rth:
        return "support_edge"
    if al <= 1.85*params.Rth:
        return "outer_quarantine_shell"
    return "far_exterior"


def ledger_row(task):
    case, s, l = task
    lane, support = CASES[case][:2]
    track = track_for(lane, support)
    path, params = choreography(LANES[lane], **TIMING)
    centre = packet_position(s, path)
    fields = track_scalars(s, l, params, track)
    extra = service_fields(s, l, params, standing=track.standing_support, hold=track.hold_support, packet_path=path)
    alpha, beta, radial = fields["alpha"], fields["beta"], fields["gamma_ll"]
    result = evaluate_spherical_demand(s, l, params, .0025, .0025,
                                       scalar_evaluator=lambda a, b, p: track_scalars(a, b, p, track))
    plus, minus = alpha*alpha*result["null_energy_outgoing"], alpha*alpha*result["null_energy_ingoing"]
    live = bool(abs(l-centre) <= params.Rpass and ENTRY[0] <= s <= live_packet_end(params))
    # The packet body is carried rigidly along its path, so every packet point moves at the path speed.  The
    # construction field U/B equals the path speed only at the centre and is recorded separately.
    speed = packet_velocity(s, path)
    return {"case": case, "s": s, "l": l, "stage": stage_name(s, params), "region": region(s, l, centre, params),
            "inside_packet_geom": abs(l-centre) <= params.Rpass, "inside_packet_live": live,
            "alpha": alpha, "beta": beta, "gamma_ll": radial, "gamma_omega": fields["gamma_omega"],
            "packet_norm": -alpha*alpha+radial*(speed+beta)**2,
            "packet_norm_field": -alpha*alpha+radial*(extra["U_packet"]/extra["B"]+beta)**2,
            "gtt": -alpha*alpha+radial*beta*beta, "U_beta": extra["U_beta"], "U_packet": speed*extra["B"],
            "U_field": extra["U_packet"], "B": extra["B"], "q": extra["q"], "W": extra["W"], "rho_euler": result["rho"], "p_l_unit": result["p_l"],
            "j_l_unit": result["j_l"], "p_omega_unit": result["p_omega"], "Tkk_plus": plus, "Tkk_minus": minus,
            "Tkk_min_radial": min(plus, minus), "stress_algebraic_type": result["stress_algebraic_type"]}


def audits(args, audit_log):
    grid = pd.read_csv(service_checks.REFERENCE, usecols=["s", "l"])
    paths, rows = {}, []
    for case in AUDITED:
        with ProcessPoolExecutor(args.workers) as pool:
            ledger = pd.DataFrame(pool.map(ledger_row, [(case, float(s), float(l)) for s, l in zip(grid.s, grid.l)],
                                           chunksize=64))
        base = args.runs/case
        base.mkdir(parents=True, exist_ok=True)
        paths[case] = base/"source_ledger_point_ledger.csv"
        ledger.to_csv(paths[case], index=False)
        for script, extra in (
                ("run_horizon_escape_ladder.py", ["--outdir", base/"escape_seed120", "--seeds-per-scope", 120,
                                                  "--max-steps", 12000]),
                ("run_entry_packet_reachability.py", ["--outdir", base/"entry_reachability", "--entry-side", "lower",
                                                      "--entry-side", "upper"]),
                ("run_scheduled_adm_probe_evolution.py", ["--outdir", base/"scheduled_probe", "--red-tag-seeds", 120,
                                                          "--max-steps", 12000])):
            service_checks.audit(script, ["--point-ledger", paths[case], "--label", case, *extra], audit_log)
        service_checks.audit("run_trace_expansion_audit.py", ["--point-ledger", paths[case], "--seeds",
                             base/"scheduled_probe/scheduled_adm_probe_seeds.csv", "--outdir", base/"trace_expansion",
                             "--label", case], audit_log)
        service_checks.audit("run_dense_congruence_caustic_audit.py", ["--point-ledger", paths[case], "--trace-traces",
                             base/"trace_expansion/trace_expansion_audit_traces.csv", "--outdir",
                             base/"dense_bundles_all_centers", "--label", case, "--no-require-both-shrinking",
                             "--trace-step-scale", BUNDLE_STEP_SCALE, "--max-steps", 60000], audit_log)
        traces = pd.read_csv(base/"scheduled_probe/scheduled_adm_probe_traces.csv",
                             usecols=["probe_family", "trace_outcome", "max_packet_norm_along_trace", "final_s",
                                      "min_branch_abs_margin_along_trace"])
        transit = traces[traces.trace_outcome == "s_upper_boundary"]
        centre = traces[traces.probe_family == "packet_centerline"]
        live = ledger[ledger.inside_packet_live]
        rows.append({"case": case, "live_packet_points": len(live),
                     "spacelike_live_points": int((live.packet_norm >= 0).sum()),
                     "max_live_packet_norm": float(live.packet_norm.max()),
                     "max_live_packet_norm_field": float(live.packet_norm_field.max()),
                     "centerline_probes": len(centre),
                     "centerline_escaped": int(centre.trace_outcome.isin(["l_lower_boundary", "l_upper_boundary"]).sum()),
                     "centerline_max_packet_norm": float(centre.max_packet_norm_along_trace.max()),
                     "centerline_latest_exit": float(centre.final_s.max()),
                     "probes_in_transit_at_window_end": len(transit),
                     "in_transit_min_null_speed": float(transit.min_branch_abs_margin_along_trace.min())
                     if len(transit) else np.nan})
    safety = {case: service_checks.packet_safety(path) for case, path in paths.items()}
    return pd.DataFrame(rows), paths, safety


def comparison_table(paths, args, safety):
    rows = []
    for case, path in paths.items():
        base = args.runs/case
        escape = pd.read_csv(base/"escape_seed120/horizon_escape_trace_summary.csv")
        reach = pd.read_csv(base/"entry_reachability/entry_packet_reachability_summary.csv")
        probe = pd.read_csv(base/"scheduled_probe/scheduled_adm_probe_summary.csv")
        expansion = pd.read_csv(base/"trace_expansion/trace_expansion_audit_summary.csv")
        bundles = pd.read_csv(base/"dense_bundles_all_centers/dense_congruence_caustic_summary.csv")
        rows.append({"case": case, **{f"packet_safety_{k}": v for k, v in safety[case].items()},
                     "escape_traces": int(escape.traces.sum()), "escape_expected": int(escape.expected_escape_count.sum()),
                     "escape_escaped": int(escape.any_radial_escape_count.sum()),
                     "escape_stalled": int(escape.invalid_or_stalled_count.sum()),
                     "reachable_packet_hits": int(reach.reachable_packet_hits.sum()),
                     "service_stage_hits": int(reach.service_stage_hits.sum()),
                     "carry_stage_hits": int(reach.carry_stage_hits.sum()),
                     "probe_traces": int(probe.traces.sum()), "probe_escaped": int(probe.radial_escape_count.sum()),
                     "traces_entering_both_shrinking": int(expansion.traces_entering_both_shrinking.sum()),
                     "traces_sustained_to_end": int(expansion.traces_sustained_to_end.sum()),
                     "bundle_crossings": int(bundles.crossing_samples.sum()),
                     "bundle_caustic_like": int(bundles.caustic_like_collapse.sum()),
                     "bundle_max_initial_radius_width": float(bundles.initial_radius_width.max()),
                     "bundle_min_l_width_ratio": float(bundles.min_common_l_width_ratio.min())})
    return pd.DataFrame(rows)


def summarize(frame, case, step, resolved):
    design = design_for(case)
    bands = resolved[resolved.case == case]
    worst = frame.loc[frame.layer_min_null.idxmin()]
    standing = frame[frame.s == frame.s.iloc[(frame.s-10.).abs().argmin()]]
    return {"case": case, "samples": len(frame), "layer_nodes": len(ax.wall_nodes(design, CASES[case][3])[0]),
            "outer_radius": design.outer_radius,
            "layer_type_i": int(frame.layer_type_i.sum()), "layer_type_iv": int(frame.layer_type_iv.sum()),
            "layer_type_ii_iii": int(frame.layer_type_ii_iii.sum()), "layer_unresolved": int(frame.layer_unresolved.sum()),
            "samples_with_type_iv": int((frame.layer_type_iv > 0).sum()),
            "live_samples": int(frame.live.sum()), "live_samples_with_type_iv": int(((frame.layer_type_iv > 0) & frame.live).sum()),
            "envelope_violations": int((frame.envelope_ratio > 1).sum()), "worst_envelope_ratio": float(frame.envelope_ratio.max()),
            "max_estimated_band_width": float(frame.estimated_band_width.max()),
            "resolved_samples": len(bands), "resolved_flux_crossings": int(bands.crossings.sum()),
            "resolved_samples_with_band": int((bands.width > 0).sum()),
            "max_resolved_band_width": float(bands.width.max()) if len(bands) else math.nan,
            "exterior_max_abs": float(frame.exterior_max_abs.max()),
            "core_min_null": float(frame.core_min_null.min()),
            "layer_min_null": float(worst.layer_min_null), "layer_min_null_s": float(worst.s),
            "layer_min_null_z": float(worst.z),
            "standing_layer_content_per_sigma": float(standing.layer_negative_null.sum()*step),
            "layer_negative_null_integral": float(frame.layer_negative_null.sum()*step*step)}


def channel_fields(task):
    """log alpha and log A over the radial grid at one z of the standing configuration."""
    case, s, z, radius = task
    design = design_for(case)
    fraction = design.track.join_fraction
    blends = tuple(ax.layer_blend(radius, design.layers[name], fraction) for name in ("alpha", "A", "beta"))
    fields = ax.radial_jets(ax.service_jet(s, z, params_for(CASES[case][0]), design), None, None, None,
                            blends=blends, sheath=ax.sheath_terms(radius, z, design),
                            conformal=ax.conformal_terms(radius, z, design))
    return np.log(fields["alpha"]), np.log(fields["A"]), float(np.max(np.abs(fields["beta"])))


def light_channel(case, pool, step=.05):
    """Fastest light from the entry to the track end, both on the axis, through the standing configuration.

    After the release the shift vanishes and the metric is static, so light takes the path of least optical
    length sqrt(A^2 dz^2 + dr^2)/alpha. A shortest path on a 48-direction lattice gives the arrival time.
    """
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import dijkstra
    s = STANDING_SNAPSHOT
    z_axis = np.round(np.arange(ENTRY[1], TRACK_END+step/2, step), 10)
    radius = np.round(np.arange(0., design_for(case).outer_radius+.75+step/2, step), 10)
    parts = list(pool.map(channel_fields, [(case, s, float(z), radius) for z in z_axis]))
    log_alpha, log_a = np.array([p[0] for p in parts]), np.array([p[1] for p in parts])
    shift = max(p[2] for p in parts)
    nz, nr = log_alpha.shape
    index = np.arange(nz*nr).reshape(nz, nr)
    rows, cols, costs = [], [], []
    for a, b in ((a, b) for a in range(-4, 5) for b in range(-4, 5) if math.gcd(abs(a), abs(b)) == 1):
        i0, i1 = max(0, -a), nz-max(0, a)
        k0, k1 = max(0, -b), nr-max(0, b)
        here, there = (slice(i0, i1), slice(k0, k1)), (slice(i0+a, i1+a), slice(k0+b, k1+b))
        mid_alpha = np.exp(.5*(log_alpha[here]+log_alpha[there]))
        mid_a = np.exp(.5*(log_a[here]+log_a[there]))
        rows.append(index[here].ravel())
        cols.append(index[there].ravel())
        costs.append((np.sqrt((mid_a*a*step)**2+(b*step)**2)/mid_alpha).ravel())
    graph = coo_matrix((np.concatenate(costs), (np.concatenate(rows), np.concatenate(cols))),
                       shape=(nz*nr, nz*nr)).tocsr()
    distance, previous = dijkstra(graph, indices=index[0, 0], return_predecessors=True)
    node, route = index[-1, 0], []
    while node >= 0:
        route.append(node)
        node = previous[node]
    route_r = radius[np.array(route) % nr]
    ratio = np.exp(log_alpha-log_a)
    return {"case": case, "snapshot_sigma": s, "max_abs_shift": shift, "lattice_step": step,
            "max_along_track_light_speed": float(ratio.max()),
            "along_track_light_speed_at_max_radius": float(radius[np.unravel_index(ratio.argmax(), ratio.shape)[1]]),
            "min_axis_light_speed": float(ratio[:, 0].min()),
            "light_transit": float(distance[index[-1, 0]]), "light_arrival": ENTRY[0]+float(distance[index[-1, 0]]),
            "flat_light_arrival": ENTRY[0]+TRACK_END-ENTRY[1], "route_max_radius": float(route_r.max())}


def figures(search, chosen, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    sigma = np.linspace(-1.4, 6., 600)
    for _, row in chosen.iterrows():
        path, _ = choreography(row.v_lane, row.t_accel, row.t_decel, row.v_out, row.l_exit)
        axes[0].plot(sigma, [packet_position(s, path) for s in sigma], label=f"lane {row.v_lane:g}c")
        axes[1].plot(sigma, [packet_velocity(s, path) for s in sigma], label=f"lane {row.v_lane:g}c")
    axes[0].plot(sigma, sigma, "k--", lw=1, label="light from entry")
    axes[0].axhline(TRACK_END, color="grey", lw=.6)
    axes[0].set_ylim(-1.6, 6)
    axes[0].set_xlabel("sigma")
    axes[0].set_ylabel("packet position l")
    axes[1].axhline(1., color="k", lw=.8, ls="--")
    axes[1].set_xlabel("sigma")
    axes[1].set_ylabel("coordinate speed")
    axes[0].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output/"packet_paths.png", dpi=140)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--step", type=float, default=.1)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/choreography_pass")
    parser.add_argument("--runs", type=Path, default=service_checks.RUNS/"choreography_pass")
    parser.add_argument("--skip-audits", action="store_true", help="evaluate paths and boundary layers only")
    args = parser.parse_args()
    started = time.time()
    args.output.mkdir(parents=True, exist_ok=True)
    grid = list(itertools.product((1.2, 1.5, 1.8, 2.1), (.3, .6), (.4, .8), (.8, .9, .95), (1.8, 2.1, 2.4)))
    tasks = [(f"search_{i}", *g, "static") for i, g in enumerate(grid)]
    tasks += [(lane, v, *TIMING.values(), support) for lane, v in LANES.items() for support in ("static", "held")]
    with ProcessPoolExecutor(args.workers) as pool:
        metrics = pd.DataFrame([row for row in pool.map(path_metrics, tasks, chunksize=2) if row is not None])
    search = metrics[metrics.name.str.startswith("search_")]
    chosen = metrics[~metrics.name.str.startswith("search_")]
    search.to_csv(args.output/"choreography_search.csv", index=False)
    chosen.to_csv(args.output/"chosen_paths.csv", index=False)
    print("search", round(time.time()-started, 1), flush=True)

    s_axis = np.round(np.arange(-1.5, 10.+args.step/2, args.step), 10)
    z_axis = np.round(np.arange(-4.9, 4.9+args.step/2, args.step), 10)
    jets = {}
    with ProcessPoolExecutor(args.workers) as pool:
        for case, s, array in pool.map(jets_row, [(case, float(s), z_axis) for case in CASES for s in s_axis]):
            jets[(case, s)] = array
    with ProcessPoolExecutor(args.workers) as pool:
        rows = [r for chunk in pool.map(layer_row, [(case, float(s), z_axis, jets[(case, float(s))]) for case in CASES
                                                    for s in s_axis], chunksize=2) for r in chunk]
    samples = pd.DataFrame(rows)
    samples.to_csv(args.output/"samples.csv.gz", index=False, compression={"method": "gzip", "mtime": 0},
                   float_format="%.7g")
    print("layers", round(time.time()-started, 1), flush=True)
    targets = [(case, float(r.s), float(r.z)) for case in CASES
               for _, r in samples[samples.case == case].nlargest(RESOLVED_SAMPLES, "estimated_band_width").iterrows()]
    with ProcessPoolExecutor(args.workers) as pool:
        resolved = pd.DataFrame(list(pool.map(resolve_bands, targets)), columns=["case", "s", "z", "crossings", "width"])
    resolved.to_csv(args.output/"resolved_bands.csv", index=False)
    summary = pd.DataFrame([summarize(samples[samples.case == case], case, args.step, resolved) for case in CASES])
    summary.to_csv(args.output/"summary.csv", index=False)
    print("bands", round(time.time()-started, 1), flush=True)

    audit_log = []
    service = pd.DataFrame()
    if not args.skip_audits:
        service, paths, safety = audits(args, audit_log)
        service.to_csv(args.output/"service_summary.csv", index=False)
        comparison_table(paths, args, safety).to_csv(args.output/"audit_comparison.csv", index=False)
    with ProcessPoolExecutor(args.workers) as pool:
        channel = pd.DataFrame([light_channel("lane_2p1__static", pool)])
    channel.to_csv(args.output/"light_channel.csv", index=False)
    figures(search, chosen[chosen.support == "static"], args.output)
    manifest = {
        "completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time()-started, 1), "workers": args.workers, "step": args.step,
        "sigma_range": [float(s_axis[0]), float(s_axis[-1])], "entry": ENTRY, "release_at": RELEASE_AT,
        "track_end": TRACK_END, "lanes": LANES, "timing": TIMING, "wide_stack": WIDE_STACK, "cases": CASES,
        "envelope_params_changed": {k: v for k, v in asdict(ENVELOPE).items() if v != asdict(BASE)[k]},
        "bundle_step_scale": BUNDLE_STEP_SCALE, "standing_snapshot": STANDING_SNAPSHOT, "noise_floor": NOISE_FLOOR, "resolved_samples_per_case": RESOLVED_SAMPLES, "audit_log": audit_log,
        "reference_ledger_sha256": sha256_file(service_checks.REFERENCE),
        "software_sha256": {path: sha256_file(ROOT/"toolkit/adm_harness_cli"/path) for path in (
            "adm_harness/axial_track.py", "adm_harness/axial_einstein_generated.py",
            "adm_harness/constant_radius_track.py", "scripts/run_choreography_pass.py")},
    }
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=1, default=str)+"\n")
    pd.set_option("display.width", 250)
    print(chosen.T.to_string())
    print(summary.T.to_string())
    print(service.T.to_string())
    print(channel.T.to_string())


if __name__ == "__main__":
    main()
