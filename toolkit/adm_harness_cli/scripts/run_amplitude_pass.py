#!/usr/bin/env python3
"""Minimum-amplitude pass of the one-space rail; emit data only.

The demand census found that the standing energy follows the stretch alone
and grows with the largest stretch, the support stretch times the conformal
pre-sheath. This pass flattens the support stretch (C0 = B0 = 1) at several
support lapses and screens pre-sheath scales over the whole transit: node
types at full resolution, and root-found bands at each candidate's 60
widest-estimate samples. It selects the least-energy design that is Type I at
every node with no resolved band. The selected design then takes the full
treatment: the gate
with band resolution and refinement over the approach, carry and release;
the demand census; the path-aware service audits on a ledger that covers the
approach; and light through the standing geometry. Narrative interpretation
is maintained manually in supporting_reports.
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
AMPLITUDES = {
    "flat_lapse_1": dict(C0=1., B0=1., lam=1.),
    "flat_lapse_6": dict(C0=1., B0=1., lam=6.),
    "flat_lapse_60": dict(C0=1., B0=1., lam=60.),
    "flat_lapse_600": dict(C0=1., B0=1., lam=600.),
}
PRESHEATH = (3., 4., 5., 6., 6.5, 7., 8.)
SIGMA_START, SCREEN_END, STANDING = -8., 3., 10.
Z_MAX = 8.
NOISE_FLOOR = choreography.NOISE_FLOOR
PER_PANEL = 12
REFERENCE = ROOT/"supporting_reports/data/demand_census"


def params_for(amplitude):
    return replace(choreography.params_for(LANE), **AMPLITUDES[amplitude])


def stack(scale):
    layers = dict(choreography.WIDE_STACK)
    if scale == 0:
        for key in ("conformal_log_scale", "conformal_rise", "conformal_fall"):
            layers.pop(key)
    else:
        layers["conformal_log_scale"] = float(scale)
    return layers


def design_for(scale, jet_step=choreography.JET_STEP):
    return ax.AxialTrackDesign(track=choreography.track_for(LANE, "static"), jet_step=jet_step, **stack(scale))


def packet_safety_row(amplitude):
    """Worst normalized packet norm over the packet body, approach to track end, at path speed and field speed."""
    params = params_for(amplitude)
    path, _ = choreography.choreography(choreography.LANES[LANE], **choreography.TIMING)
    arrival = brentq(lambda s: packet_position(s, path)-choreography.TRACK_END, SIGMA_START, 100.)
    worst = {"path": -np.inf, "field": -np.inf}
    for s in np.arange(SIGMA_START, arrival+1e-9, .02):
        centre, speed = packet_position(s, path), packet_velocity(s, path)
        for offset in np.linspace(-params.Rpass, params.Rpass, 15):
            f = service_fields(s, centre+offset, params, standing=True, packet_path=path)
            for key, velocity in (("path", speed), ("field", f["U_packet"]/f["B"])):
                worst[key] = max(worst[key], (-f["alpha"]**2+f["gamma_ll"]*(velocity+f["beta"])**2)/f["alpha"]**2)
    return {"amplitude": amplitude, "worst_packet_norm_over_alpha2": worst["path"],
            "worst_field_norm_over_alpha2": worst["field"], "arrival_track_end": arrival}


def screen_row(task):
    """Node types of every pre-sheath scale at one sigma across z, for one support amplitude."""
    amplitude, s, z_axis = task
    params = params_for(amplitude)
    designs = {scale: design_for(scale) for scale in PRESHEATH}
    rows = {scale: {"amplitude": amplitude, "presheath": scale, "s": s, "type_iv": 0, "samples_with_type_iv": 0,
                    "unresolved": 0, "min_null": 0.} for scale in PRESHEATH}
    estimates = []
    for z in z_axis:
        jet = ax.service_jet(s, float(z), params, designs[PRESHEATH[0]])
        for scale, design in designs.items():
            radius = ax.wall_nodes(design, PER_PANEL)[0]
            tensor = ax.frame_tensor(jet, radius, design, z=float(z))
            width = choreography.band_widths(tensor, radius)
            if width > 0:
                estimates.append({"amplitude": amplitude, "presheath": scale, "s": s, "z": float(z),
                                  "estimated_band_width": width})
            kinds = ax.classify(tensor, floor=NOISE_FLOOR)["type"]
            count = int((kinds == ax.TYPE_IV).sum())
            row = rows[scale]
            row["type_iv"] += count
            row["samples_with_type_iv"] += int(count > 0)
            row["unresolved"] += int(np.isin(kinds, [ax.UNRESOLVED, ax.TYPE_II_III]).sum())
            row["min_null"] = min(row["min_null"], float(ax.min_null_energy(tensor).min()))
    return list(rows.values()), estimates


def census_slice(task):
    """Census zone rows of one (sigma, z) slice for one design."""
    amplitude, scale, s, z, keep = task
    design = design_for(scale)
    jet = ax.service_jet(s, z, params_for(amplitude), design)
    nodes, weights = ax.wall_nodes(design, PER_PANEL)
    radius = np.concatenate([[0.], nodes])
    tensor = ax.frame_tensor(jet, radius, design, z=z)
    fields = ax.radial_fields(jet, radius, design, z=z)
    coord = np.concatenate([[math.pi*design.core_radius**2], weights*2*math.pi*nodes])
    point = census.point_census(tensor, fields, coord, coord*fields["A"])
    rows = census.zone_rows(point, radius, s, z, f"{amplitude}|{scale:g}")
    for row in rows:
        row["exterior_max_abs"] = float(np.max(np.abs(ax.frame_tensor(jet, [design.outer_radius+.5], design, z=z))))
    points = None
    if keep:
        points = pd.DataFrame({"s": s, "z": z, "r": radius, "alpha": fields["alpha"], "A": fields["A"],
                               "T_nn": tensor[:, 0, 0], "min_null": point["null"],
                               "energy_class": np.select([point[k] for k in census.CLASSES], census.CLASSES,
                                                         default="vacuum_or_other")})
    return rows, points


def gate_jets(task):
    amplitude, s, z_axis, jet_step = task
    design = design_for(0., jet_step)
    params = params_for(amplitude)
    out = np.empty((len(z_axis), 3, len(choreography.KEYS)))
    for index, z in enumerate(z_axis):
        jet = ax.service_jet(s, float(z), params, design)
        out[index] = np.stack([jet[key] for key in choreography.KEYS], axis=1)
    return s, out


def gate_row(task):
    """Boundary-layer types, null minima and estimated band widths across z at one sigma."""
    amplitude, scale, s, z_axis, jets, per_panel, jet_step = task
    design = design_for(scale, jet_step)
    params = params_for(amplitude)
    path, _ = choreography.choreography(choreography.LANES[LANE], **choreography.TIMING)
    radius, _ = ax.wall_nodes(design, per_panel)
    rows = []
    for z, array in zip(z_axis, jets):
        jet = {key: array[:, index] for index, key in enumerate(choreography.KEYS)}
        layer = ax.frame_tensor(jet, radius, design, z=float(z))
        core = ax.frame_tensor(jet, [0.], design, z=float(z))
        kinds = ax.classify(np.concatenate([core, layer]), floor=NOISE_FLOOR)["type"][1:]
        null = ax.min_null_energy(np.concatenate([core, layer]))
        rows.append({"s": s, "z": float(z), "live": bool(abs(z-packet_position(s, path)) <= params.Rpass
                                                         and choreography.ENTRY[0] <= s <= live_packet_end(params)),
                     "layer_type_i": int((kinds == ax.TYPE_I).sum()), "layer_type_iv": int((kinds == ax.TYPE_IV).sum()),
                     "layer_other": int(np.isin(kinds, [ax.UNRESOLVED, ax.TYPE_II_III]).sum()),
                     "core_min_null": float(null[0]), "layer_min_null": float(null[1:].min()),
                     "estimated_band_width": choreography.band_widths(layer, radius),
                     "envelope_ratio": 2*design.core_radius*abs(jet["z"][2])/math.exp(jet["v"][0])})
    return rows


def resolve_bands(task):
    """Root-find every flux-carrying null-sum crossing at one sample and measure any Type IV band."""
    amplitude, scale, s, z = task
    design = design_for(scale)
    jet = ax.service_jet(s, z, params_for(amplitude), design)
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
    return s, z, crossings, widest


def ledger_row(task):
    amplitude, s, l = task
    params = params_for(amplitude)
    path, _ = choreography.choreography(choreography.LANES[LANE], **choreography.TIMING)
    track = choreography.track_for(LANE, "static")
    centre = packet_position(s, path)
    fields = track_scalars(s, l, params, track)
    extra = service_fields(s, l, params, standing=True, packet_path=path)
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


def audits(amplitude, args, audit_log):
    """Service audits on a ledger that spans the approach, carry, release and coast."""
    s_axis = np.round(np.arange(SIGMA_START, 15.+1e-9, 15/171), 10)
    l_axis = np.round(np.arange(-Z_MAX, Z_MAX+1e-9, .1), 10)
    tasks = [(amplitude, float(s), float(l)) for s in s_axis for l in l_axis]
    with ProcessPoolExecutor(args.workers) as pool:
        ledger = pd.DataFrame(pool.map(ledger_row, tasks, chunksize=64))
    base = args.runs/amplitude
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
        service_checks.audit(script, ["--point-ledger", path, "--label", amplitude, *extra], audit_log)
    service_checks.audit("run_trace_expansion_audit.py", ["--point-ledger", path, "--seeds",
                         base/"scheduled_probe/scheduled_adm_probe_seeds.csv", "--outdir", base/"trace_expansion",
                         "--label", amplitude], audit_log)
    service_checks.audit("run_dense_congruence_caustic_audit.py", [
        "--point-ledger", path, "--trace-traces", base/"trace_expansion/trace_expansion_audit_traces.csv",
        "--outdir", base/"dense_bundles_all_centers", "--label", amplitude, "--no-require-both-shrinking",
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
    return {"amplitude": amplitude, "ledger_points": len(ledger), "live_packet_points": len(live),
            "spacelike_live_points": int((live.packet_norm >= 0).sum()),
            "max_live_packet_norm": float(live.packet_norm.max()),
            "max_live_packet_norm_field": float(live.packet_norm_field.max()),
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
    amplitude, scale, z, radius = task
    design = design_for(scale)
    fields = ax.radial_fields(ax.service_jet(STANDING, z, params_for(amplitude), design), radius, design, z=z)
    return np.log(fields["alpha"]), np.log(fields["A"])


def light_channel(amplitude, scale, pool, step=.05):
    """Fastest light from the entry to the track end on the axis through the standing geometry."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import dijkstra
    z_axis = np.round(np.arange(choreography.ENTRY[1], choreography.TRACK_END+step/2, step), 10)
    radius = np.round(np.arange(0., design_for(scale).outer_radius+.75+step/2, step), 10)
    parts = list(pool.map(channel_fields, [(amplitude, scale, float(z), radius) for z in z_axis]))
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
    ratio = np.exp(log_alpha-log_a)
    return {"max_along_track_light_speed": float(ratio.max()), "light_transit": float(distance[index[-1, 0]]),
            "light_arrival": choreography.ENTRY[0]+float(distance[index[-1, 0]])}


def figure(table, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for amplitude, group in table.groupby("amplitude", sort=False):
        group = group.sort_values("presheath")
        line, = axes[0].plot(group.presheath, group.eulerian_positive, marker="o", label=amplitude)
        failed = group[(group.type_iv > 0) | (group.unresolved > 0) | (group.samples_with_band > 0)]
        axes[0].scatter(failed.presheath, failed.eulerian_positive, s=90, facecolors="none",
                        edgecolors=line.get_color())
        axes[1].plot(group.presheath, np.maximum(group.max_band_width, 1e-7), marker="o", label=amplitude)
    reference = pd.read_csv(REFERENCE/"standing_totals.csv").set_index("variant")
    axes[0].axhline(reference.loc["wide_stack", "eulerian_positive"], color="k", ls="--", lw=.8,
                    label="census design (support stretch, e^8)")
    axes[0].set_yscale("log")
    axes[0].set_xlabel("pre-sheath log scale")
    axes[0].set_ylabel("standing energy of each sign (ringed: fails the gate)")
    axes[0].legend(fontsize=7)
    axes[1].set_yscale("log")
    axes[1].set_xlabel("pre-sheath log scale")
    axes[1].set_ylabel("widest resolved band (none drawn at 1e-7)")
    fig.tight_layout()
    fig.savefig(output/"amplitude_screen.png", dpi=140)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--step", type=float, default=.1)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/amplitude_pass")
    parser.add_argument("--runs", type=Path, default=service_checks.RUNS/"amplitude_pass")
    parser.add_argument("--screen-only", action="store_true")
    args = parser.parse_args()
    started = time.time()
    args.output.mkdir(parents=True, exist_ok=True)
    s_axis = np.round(np.arange(SIGMA_START, STANDING+args.step/2, args.step), 10)
    z_axis = np.round(np.arange(-Z_MAX, Z_MAX+args.step/2, args.step), 10)
    screen_s = [float(s) for s in s_axis if s <= SCREEN_END+1e-9]

    with ProcessPoolExecutor(args.workers) as pool:
        safety = pd.DataFrame(list(pool.map(packet_safety_row, AMPLITUDES)))
        results = list(pool.map(screen_row, [(a, s, z_axis) for a in AMPLITUDES for s in screen_s], chunksize=2))
        screen = pd.DataFrame([r for rows, _ in results for r in rows])
        estimates = pd.DataFrame([e for _, found in results for e in found])
        targets = [(a, float(scale), float(r.s), float(r.z)) for (a, scale), group in
                   estimates.groupby(["amplitude", "presheath"], sort=False)
                   for _, r in group.nlargest(choreography.RESOLVED_SAMPLES, "estimated_band_width").iterrows()]
        screen_bands = pd.DataFrame([(a, scale, *result) for (a, scale, _, _), result in
                                     zip(targets, pool.map(resolve_bands, targets, chunksize=2))],
                                    columns=["amplitude", "presheath", "s", "z", "crossings", "width"])
        standing_rows = [r for rows, _ in pool.map(census_slice, [(a, scale, STANDING, float(z), False)
                                                                  for a in AMPLITUDES for scale in PRESHEATH
                                                                  for z in z_axis], chunksize=16) for r in rows]
    screen.to_csv(args.output/"screen_by_sigma.csv", index=False)
    screen_bands.to_csv(args.output/"screen_resolved_bands.csv", index=False)
    band_table = screen_bands.groupby(["amplitude", "presheath"]).agg(
        resolved_crossings=("crossings", "sum"), samples_with_band=("width", lambda w: int((w > 0).sum())),
        max_band_width=("width", "max")).reset_index()
    standing = pd.DataFrame(standing_rows)
    standing[["amplitude", "presheath"]] = standing.variant.str.split("|", expand=True)
    standing["presheath"] = standing.presheath.astype(float)
    standing_table = census.tabulate(standing, args.step, ["amplitude", "presheath"]).rename(
        columns={"type_iv": "standing_type_iv", "unresolved": "standing_unresolved"})
    screen_table = screen.groupby(["amplitude", "presheath"], sort=False).agg(
        type_iv=("type_iv", "sum"), samples_with_type_iv=("samples_with_type_iv", "sum"),
        unresolved=("unresolved", "sum"), transit_min_null=("min_null", "min")).reset_index()
    table = (screen_table.merge(band_table, on=["amplitude", "presheath"], how="left")
             .fillna({"resolved_crossings": 0, "samples_with_band": 0, "max_band_width": 0.})
             .merge(standing_table, on=["amplitude", "presheath"]).merge(safety, on="amplitude"))
    table.to_csv(args.output/"amplitude_screen.csv", index=False)
    figure(table, args.output)
    clean = table[(table.type_iv == 0) & (table.unresolved == 0) & (table.samples_with_band == 0)
                  & (table.worst_packet_norm_over_alpha2 < 0)]
    chosen = clean.sort_values(["eulerian_positive", "nec_content_coord"]).iloc[0]
    amplitude, scale = str(chosen.amplitude), float(chosen.presheath)
    print(table[["amplitude", "presheath", "type_iv", "unresolved", "samples_with_band", "max_band_width",
                 "eulerian_positive", "nec_content_coord", "nec_content_proper",
                 "worst_packet_norm_over_alpha2"]].to_string(index=False), flush=True)
    print("chosen", amplitude, scale, round(time.time()-started, 1), flush=True)
    selection = {"amplitude": amplitude, "support": AMPLITUDES[amplitude], "presheath": scale,
                 "rule": "least standing energy, then least coordinate content, among designs with no Type IV or "
                         "unresolved node over the transit, no band at the 60 widest-estimate samples, and a "
                         "timelike packet"}
    (args.output/"selection.json").write_text(json.dumps(selection, indent=1)+"\n")
    checks, service = {}, pd.DataFrame()
    if not args.screen_only:
        with ProcessPoolExecutor(args.workers) as pool:
            gate = {}
            for label, jet_step, per_panel in (("gate", choreography.JET_STEP, PER_PANEL),
                                                ("refined", choreography.JET_STEP/2, 2*PER_PANEL)):
                jets = dict(pool.map(gate_jets, [(amplitude, float(s), z_axis, jet_step) for s in s_axis]))
                rows = [r for chunk in pool.map(gate_row, [(amplitude, scale, float(s), z_axis, jets[float(s)],
                                                            per_panel, jet_step) for s in s_axis], chunksize=2)
                        for r in chunk]
                gate[label] = pd.DataFrame(rows)
            gate["gate"].to_csv(args.output/"gate_samples.csv.gz", index=False,
                                compression={"method": "gzip", "mtime": 0}, float_format="%.7g")
            targets = [(amplitude, scale, float(r.s), float(r.z)) for _, r in
                       gate["gate"].nlargest(choreography.RESOLVED_SAMPLES, "estimated_band_width").iterrows()]
            resolved = pd.DataFrame(list(pool.map(resolve_bands, targets)), columns=["s", "z", "crossings", "width"])
            resolved.to_csv(args.output/"resolved_bands.csv", index=False)
            slices = list(pool.map(census_slice, [(amplitude, scale, float(s), float(z), s == STANDING)
                                                  for s in s_axis for z in z_axis], chunksize=16))
            channel = light_channel(amplitude, scale, pool)
        frame = pd.DataFrame([r for rows, _ in slices for r in rows])
        points = pd.concat([p for _, p in slices if p is not None], ignore_index=True)
        points.to_csv(args.output/"standing_points.csv.gz", index=False, compression={"method": "gzip", "mtime": 0},
                      float_format="%.7g")
        frame["axial_zone"] = census.axial_zone(frame.z.values)
        frame.to_csv(args.output/"zone_slices.csv.gz", index=False, compression={"method": "gzip", "mtime": 0},
                     float_format="%.8g")
        final_standing = frame[frame.s == STANDING]
        census.tabulate(final_standing, args.step, ["zone", "axial_zone"]).to_csv(args.output/"standing_by_zone.csv",
                                                                                 index=False)
        census.tabulate(final_standing, args.step, ["variant"]).to_csv(args.output/"standing_totals.csv", index=False)
        by_zone, by_sigma = census.transit(frame, args.step, args.step)
        by_zone.to_csv(args.output/"transit_excess_by_zone.csv", index=False)
        by_sigma.to_csv(args.output/"transit_excess_by_sigma.csv", index=False)
        census.tabulate(frame[frame.s < STANDING], args.step, ["zone"]).to_csv(
            args.output/"transit_extremes_by_zone.csv", index=False)
        audit_log = []
        service = pd.DataFrame([audits(amplitude, args, audit_log)])
        service.to_csv(args.output/"service_summary.csv", index=False)
        g, r = gate["gate"], gate["refined"]
        checks = {
            "gate_samples": len(g), "gate_type_i": int(g.layer_type_i.sum()), "gate_type_iv": int(g.layer_type_iv.sum()),
            "gate_other": int(g.layer_other.sum()), "refined_type_i": int(r.layer_type_i.sum()),
            "refined_type_iv": int(r.layer_type_iv.sum()), "refined_other": int(r.layer_other.sum()),
            "envelope_violations": int((g.envelope_ratio > 1).sum()), "worst_envelope_ratio": float(g.envelope_ratio.max()),
            "resolved_crossings": int(resolved.crossings.sum()), "samples_with_band": int((resolved.width > 0).sum()),
            "max_band_width": float(resolved.width.max()), "core_min_null": float(g.core_min_null.min()),
            "layer_min_null": float(g.layer_min_null.min()),
            "exterior_max_abs": float(frame.exterior_max_abs.max()),
            "census_type_iv": int(frame.type_iv.sum()), "census_unresolved": int(frame.unresolved.sum()),
            "start_matches_standing": float(np.max(np.abs(
                frame[frame.s == frame.s.min()].sort_values(["z", "zone"])[census.SUMS].to_numpy()
                - final_standing.sort_values(["z", "zone"])[census.SUMS].to_numpy()))),
            "standing_energy_balance": float((final_standing.eulerian_positive+final_standing.eulerian_negative).sum()
                                             / (final_standing.eulerian_positive-final_standing.eulerian_negative).sum()),
            **channel, "audit_log": audit_log}
    manifest = {
        "completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time()-started, 1), "workers": args.workers, "step": args.step,
        "sigma_range": [float(s_axis[0]), float(s_axis[-1])], "screen_sigma_end": SCREEN_END, "z_max": Z_MAX,
        "lane": LANE, "amplitudes": AMPLITUDES, "presheath_scales": PRESHEATH, "selection": selection,
        "wide_stack": choreography.WIDE_STACK, "per_panel": PER_PANEL, "noise_floor": NOISE_FLOOR, "checks": checks,
        "envelope_params_changed": {k: v for k, v in asdict(choreography.ENVELOPE).items()
                                    if v != asdict(choreography.BASE)[k]},
        "software_sha256": {path: sha256_file(ROOT/"toolkit/adm_harness_cli"/path) for path in (
            "adm_harness/axial_track.py", "adm_harness/axial_einstein_generated.py",
            "adm_harness/constant_radius_track.py", "scripts/run_choreography_pass.py",
            "scripts/run_demand_census.py", "scripts/run_amplitude_pass.py")},
    }
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=1, default=str)+"\n")
    print(json.dumps({k: v for k, v in checks.items() if k != "audit_log"}, indent=1))
    pd.set_option("display.width", 250)
    print(service.T.to_string())


if __name__ == "__main__":
    main()
