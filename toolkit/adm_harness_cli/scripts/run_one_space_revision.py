#!/usr/bin/env python3
"""Evaluate the one-space service revision of the rail; emit data only.

The revision holds the support in its compressed state (no decompression)
while keeping the packet carve and windows, and puts the packet lapse window
on the live schedule with a larger gain and radius, so the lapse covers the
carried shift wherever the shift varies along the track. The lapse, stretch
and shift then receive separate transverse boundary layers, with a conformal
pre-sheath and a lapse sheath. The script evaluates boundary-layer designs on
the full (sigma, z) grid, checks the chosen design under jet-step and radial
refinement, resolves Type IV bands at the null-sum crossings of the samples
with the largest estimated widths, and runs the along-track service audits.
A fully static support without the carve is kept as a comparison. Narrative
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
import run_constant_radius_service_checks as service_checks
from adm_harness import axial_track as ax
from adm_harness.constant_radius_track import ConstantRadiusTrackDesign, service_fields, track_scalars
from adm_harness.source_ledger import live_packet_end, live_packet_mask, region_name, sha256_file, stage_name
from adm_harness.warped_product import evaluate_spherical_demand

ROOT = Path(__file__).resolve().parents[3]
KEYS = ("v", "s", "z", "ss", "sz", "zz")
BASE = service_checks.PARAMS
ENVELOPE = replace(BASE, standing_support_packet_lapse_log_gain=2., standing_support_packet_lapse_radius_multiplier=2.5,
                   standing_support_packet_lapse_schedule="live_only")
SERVICES = {
    "current": (BASE, ConstantRadiusTrackDesign()),
    "hold": (BASE, ConstantRadiusTrackDesign(hold_support=True)),
    "one_space": (ENVELOPE, ConstantRadiusTrackDesign(hold_support=True)),
    "static_one_space": (ENVELOPE, ConstantRadiusTrackDesign(standing_support=True)),
}
LAYERS = {
    "colocated": {},
    "staged_first_draft": dict(conformal_log_scale=4., conformal_rise=(1.75, 1.), conformal_fall=(4.5, 1.),
                               sheath_log_lapse=8., sheath_rise=(2.75, 1.5), sheath_fall=(4.5, 2.),
                               shift_layer=(3., 1.), stretch_layer=(4.5, 1.), lapse_layer=(4.5, 2.)),
    "staged": dict(conformal_log_scale=8., conformal_rise=(1.75, 1.), conformal_fall=(5.5, 1.),
                   sheath_log_lapse=8., sheath_rise=(2.75, 2.5), sheath_fall=(5.5, 2.),
                   shift_layer=(3., 1.), stretch_layer=(5.5, 1.), lapse_layer=(5.5, 2.)),
    "staged_wide": dict(conformal_log_scale=8., conformal_rise=(1.75, 2.), conformal_fall=(9.25, 2.),
                        sheath_log_lapse=8., sheath_rise=(3.75, 5.), sheath_fall=(9.25, 4.),
                        shift_layer=(4.25, 2.), stretch_layer=(9.25, 2.), lapse_layer=(9.25, 4.)),
}
JET_STEP = .0025
NOISE_FLOOR = 1e-8
CASES = {
    "current__colocated": ("current", "colocated", JET_STEP, 12),
    "hold__colocated": ("hold", "colocated", JET_STEP, 12),
    "one_space__colocated": ("one_space", "colocated", JET_STEP, 12),
    "one_space__staged_first_draft": ("one_space", "staged_first_draft", JET_STEP, 12),
    "one_space__staged": ("one_space", "staged", JET_STEP, 12),
    "one_space__staged__refined": ("one_space", "staged", JET_STEP/2, 24),
    "one_space__staged_wide": ("one_space", "staged_wide", JET_STEP, 12),
    "static_one_space__staged": ("static_one_space", "staged", JET_STEP, 12),
}
RESOLVED_SAMPLES = 60
STANDING_REFERENCE = (10., 0.)


def design_for(case: str) -> ax.AxialTrackDesign:
    service, layers, step, _ = CASES[case]
    return ax.AxialTrackDesign(track=SERVICES[service][1], jet_step=step, **LAYERS[layers])


def jets_row(task):
    service, step, s, z_axis = task
    params, track = SERVICES[service]
    design = ax.AxialTrackDesign(track=track, jet_step=step)
    out = np.empty((len(z_axis), 3, len(KEYS)))
    for index, z in enumerate(z_axis):
        jet = ax.service_jet(s, z, params, design)
        out[index] = np.stack([jet[key] for key in KEYS], axis=1)
    return service, step, s, out


def band_widths(tensor, radius):
    """Estimated Type IV band widths 2|flux|/|slope| at each null-sum crossing in the (n,r) and (n,z) blocks."""
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


def resolve_bands(task):
    """Root-find each null-sum crossing that carries flux and resolve the Type IV band around it."""
    case, s, z = task
    design = design_for(case)
    params = SERVICES[CASES[case][0]][0]
    jet = ax.service_jet(s, z, params, design)
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
                kinds = ax.classify(ax.frame_tensor(jet, fine, design, z=z), floor=1e-12)["type"]
                band = fine[kinds == ax.TYPE_IV]
                if len(band):
                    widest = max(widest, band.max()-band.min()+(fine[1]-fine[0]))
                    break
    return case, s, z, crossings, widest


def evaluate_point(jet, design, z, radius, weights):
    core = ax.frame_tensor(jet, [0.], design, z=z)
    layer = ax.frame_tensor(jet, radius, design, z=z)
    exterior = ax.frame_tensor(jet, [design.outer_radius+.5], design, z=z)
    kinds = ax.classify(np.concatenate([core, layer]), floor=NOISE_FLOOR)
    null = ax.min_null_energy(np.concatenate([core, layer]))
    types, margins = kinds["type"][1:], kinds["type_margin"][1:]
    area = weights*2*math.pi*radius
    deficit = np.maximum(-null[1:], 0)
    return {
        "log_alpha_core": jet["v"][0], "log_a_core": jet["v"][1], "beta_core": jet["v"][2],
        "beta_z_core": jet["z"][2], "core_type": kinds["type"][0], "core_min_null": null[0],
        "layer_type_i": int((types == ax.TYPE_I).sum()), "layer_type_iv": int((types == ax.TYPE_IV).sum()),
        "layer_type_ii_iii": int((types == ax.TYPE_II_III).sum()), "layer_vacuum": int((types == ax.VACUUM).sum()),
        "layer_unresolved": int((types == ax.UNRESOLVED).sum()),
        "layer_near_type_boundary": int(((types != ax.VACUUM) & (np.abs(margins) < 1e-3)).sum()),
        "layer_min_null": float(null[1:].min()), "layer_min_null_radius": float(radius[np.argmin(null[1:])]),
        "layer_negative_null": float(np.sum(area*deficit)),
        "core_negative_null": math.pi*design.core_radius**2*max(-null[0], 0.),
        "estimated_band_width": band_widths(layer, radius),
        "exterior_max_abs": float(np.max(np.abs(exterior))),
    }


def layer_row(task):
    case, s, z_axis, jets = task
    design = design_for(case)
    params = SERVICES[CASES[case][0]][0]
    radius, weights = ax.wall_nodes(design, CASES[case][3])
    rows = []
    for z, array in zip(z_axis, jets):
        jet = {key: array[:, index] for index, key in enumerate(KEYS)}
        rows.append({"case": case, "s": s, "z": z, "live": bool(live_packet_mask(s, z, params)),
                     **evaluate_point(jet, design, float(z), radius, weights)})
    return rows


def ledger_row(task):
    service, s, l = task
    params, track = SERVICES[service]
    fields = track_scalars(s, l, params, track)
    extra = service_fields(s, l, params, standing=track.standing_support, hold=track.hold_support)
    alpha, beta, radial = fields["alpha"], fields["beta"], fields["gamma_ll"]
    result = evaluate_spherical_demand(s, l, params, .0025, .0025,
                                       scalar_evaluator=lambda a, b, p: track_scalars(a, b, p, track))
    plus, minus = alpha*alpha*result["null_energy_outgoing"], alpha*alpha*result["null_energy_ingoing"]
    return {"case": service, "s": s, "l": l, "stage": stage_name(s, params), "region": region_name(s, l, params),
            "inside_packet_geom": abs(l-s) <= params.Rpass, "inside_packet_live": live_packet_mask(s, l, params),
            "alpha": alpha, "beta": beta, "gamma_ll": radial, "gamma_omega": fields["gamma_omega"],
            "packet_norm": -alpha*alpha+radial*(extra["U_packet"]/extra["B"]+beta)**2,
            "gtt": -alpha*alpha+radial*beta*beta, "U_beta": extra["U_beta"], "U_packet": extra["U_packet"],
            "B": extra["B"], "q": extra["q"], "W": extra["W"], "rho_euler": result["rho"], "p_l_unit": result["p_l"],
            "j_l_unit": result["j_l"], "p_omega_unit": result["p_omega"], "Tkk_plus": plus, "Tkk_minus": minus,
            "Tkk_min_radial": min(plus, minus), "stress_algebraic_type": result["stress_algebraic_type"]}


def velocity_delivery(params, track):
    s, l, ds, marks, live_end = -1.4, -1.4, 2e-3, {}, live_packet_end(params)
    while s < 80 and l < 5.:
        fields = service_fields(s, l, params, standing=track.standing_support, hold=track.hold_support,
                                reset_front=track.reset_front)
        l += ds*fields["U_packet"]/fields["B"]
        s += ds
        if s >= live_end and "live_end" not in marks:
            marks["live_end"] = round(l, 3)
        for mark in (1.75, 3., 5.):
            if l >= mark and mark not in marks:
                marks[mark] = round(s, 3)
    return marks


def service_audits(args, audit_log):
    grid = pd.read_csv(service_checks.REFERENCE, usecols=["s", "l"])
    rows, paths = [], {}
    for service in ("one_space", "static_one_space"):
        params, track = SERVICES[service]
        with ProcessPoolExecutor(args.workers) as pool:
            ledger = pd.DataFrame(pool.map(ledger_row, [(service, float(s), float(l)) for s, l in zip(grid.s, grid.l)],
                                           chunksize=64))
        base = args.runs/service
        base.mkdir(parents=True, exist_ok=True)
        paths[service] = base/"source_ledger_point_ledger.csv"
        ledger.to_csv(paths[service], index=False)
        manifest = base/"schedule_manifest.json"
        manifest.write_text(json.dumps({"params": asdict(params)}, default=float))
        for script, extra in (
                ("run_horizon_escape_ladder.py", ["--outdir", base/"escape_seed120", "--seeds-per-scope", 120,
                                                  "--max-steps", 12000]),
                ("run_entry_packet_reachability.py", ["--outdir", base/"entry_reachability", "--entry-side", "lower",
                                                      "--entry-side", "upper"]),
                ("run_scheduled_adm_probe_evolution.py", ["--outdir", base/"scheduled_probe", "--red-tag-seeds", 120,
                                                          "--max-steps", 12000])):
            service_checks.audit(script, ["--point-ledger", paths[service], "--label", service, *extra], audit_log)
        service_checks.audit("run_trace_expansion_audit.py", ["--point-ledger", paths[service], "--seeds",
                             base/"scheduled_probe/scheduled_adm_probe_seeds.csv", "--outdir", base/"trace_expansion",
                             "--label", service], audit_log)
        service_checks.audit("run_dense_congruence_caustic_audit.py", ["--point-ledger", paths[service], "--trace-traces",
                             base/"trace_expansion/trace_expansion_audit_traces.csv", "--outdir",
                             base/"dense_bundles_all_centers", "--label", service, "--no-require-both-shrinking"],
                             audit_log)
        service_checks.audit("run_service_time_advantage_ledger.py", ["--point-ledger", paths[service], "--label", service,
                             "--manifest", manifest, "--outdir", base/"service_time"], audit_log)
        traces = pd.read_csv(base/"scheduled_probe/scheduled_adm_probe_traces.csv",
                             usecols=["probe_family", "trace_outcome", "max_packet_norm_along_trace"])
        centerline = traces[traces.probe_family == "packet_centerline"]
        delivery = velocity_delivery(params, track)
        rows.append({"service": service, "live_packet_points": int(ledger.inside_packet_live.sum()),
                     "max_live_packet_norm": float(ledger[ledger.inside_packet_live].packet_norm.max()),
                     "centerline_probes": len(centerline),
                     "centerline_escaped": int(centerline.trace_outcome.isin(["l_lower_boundary", "l_upper_boundary"]).sum()),
                     "centerline_at_time_limit": int((centerline.trace_outcome == "s_upper_boundary").sum()),
                     "max_centerline_packet_norm": float(centerline.max_packet_norm_along_trace.max()),
                     "velocity_reading_l_at_live_end": delivery.get("live_end", math.nan),
                     "velocity_reading_reaches_l_1p75": delivery.get(1.75, math.nan),
                     "velocity_reading_reaches_l_5": delivery.get(5., math.nan)})
    safety = {name: service_checks.packet_safety(path) for name, path in paths.items()}
    table = service_checks.comparison(paths, {name: args.runs/name for name in paths}, safety)
    return pd.DataFrame(rows), table


def summarize(frame, case, step, resolved):
    design = design_for(case)
    bands = resolved[resolved.case == case]
    cell = step*step
    s_ref = float(frame.s.iloc[(frame.s-STANDING_REFERENCE[0]).abs().argmin()])
    z_ref = float(frame.z.iloc[(frame.z-STANDING_REFERENCE[1]).abs().argmin()])
    standing = frame[(frame.s == s_ref) & (frame.z == z_ref)]
    worst = frame.loc[frame.layer_min_null.idxmin()]
    return {
        "case": case, "service": CASES[case][0], "layers": CASES[case][1], "jet_step": design.jet_step,
        "nodes_per_panel": CASES[case][3], "layer_nodes": len(ax.wall_nodes(design, CASES[case][3])[0]),
        "outer_radius": design.outer_radius, "samples": len(frame),
        "layer_type_i": int(frame.layer_type_i.sum()), "layer_type_iv": int(frame.layer_type_iv.sum()),
        "layer_type_ii_iii": int(frame.layer_type_ii_iii.sum()), "layer_unresolved": int(frame.layer_unresolved.sum()),
        "samples_with_type_iv": int((frame.layer_type_iv > 0).sum()),
        "live_samples_with_type_iv": int(((frame.layer_type_iv > 0) & frame.live).sum()),
        "layer_near_type_boundary": int(frame.layer_near_type_boundary.sum()),
        "max_estimated_band_width": float(frame.estimated_band_width.max()),
        "samples_with_estimated_band": int((frame.estimated_band_width > 0).sum()),
        "resolved_samples": len(bands), "resolved_flux_crossings": int(bands.crossings.sum()) if len(bands) else 0,
        "resolved_samples_with_type_iv_band": int((bands.width > 0).sum()) if len(bands) else 0,
        "max_resolved_band_width": float(bands.width.max()) if len(bands) else math.nan,
        "exterior_max_abs": float(frame.exterior_max_abs.max()),
        "core_min_null": float(frame.core_min_null.min()), "layer_min_null": float(worst.layer_min_null),
        "layer_min_null_s": float(worst.s), "layer_min_null_z": float(worst.z),
        "layer_min_null_r": float(worst.layer_min_null_radius),
        "standing_layer_min_null": float(standing.layer_min_null.iloc[0]) if len(standing) else math.nan,
        "standing_layer_content_per_sigma": float(frame[frame.s == s_ref].layer_negative_null.sum()*step),
        "layer_negative_null_integral": float(frame.layer_negative_null.sum()*cell),
        "core_negative_null_integral": float(frame.core_negative_null.sum()*cell),
    }


def figures(samples, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cases = (("current__colocated", "transplanted service"), ("one_space__colocated", "one-space service, one layer"),
             ("one_space__staged", "one-space service, staged layers"))
    fig, axes = plt.subplots(1, 3, figsize=(15, 3.9), sharey=True)
    for axis, (case, title) in zip(axes, cases):
        frame = samples[samples.case == case]
        share = frame.layer_type_iv/np.maximum(frame.layer_type_i+frame.layer_type_iv+frame.layer_type_ii_iii, 1)
        grid = frame.assign(share=share).pivot(index="z", columns="s", values="share")
        mesh = axis.pcolormesh(grid.columns, grid.index, grid.values, cmap="magma_r", vmin=0, vmax=1, shading="nearest")
        axis.set_xlim(-1.5, 8)
        axis.set_title(title)
        axis.set_xlabel("sigma")
    axes[0].set_ylabel("z")
    fig.colorbar(mesh, ax=axes, label="Type IV share of non-vacuum boundary-layer nodes")
    fig.savefig(output/"type_iv_share_by_revision.png", dpi=140, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--step", type=float, default=.1)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/one_space_revision")
    parser.add_argument("--runs", type=Path, default=service_checks.RUNS/"one_space_revision")
    parser.add_argument("--figures-only", action="store_true", help="redraw figures from the recorded samples")
    parser.add_argument("--skip-audits", action="store_true", help="evaluate the boundary layers only")
    args = parser.parse_args()
    if args.figures_only:
        figures(pd.read_csv(args.output/"samples.csv.gz"), args.output)
        return
    started = time.time()
    args.output.mkdir(parents=True, exist_ok=True)
    s_axis = np.round(np.arange(-1.5, 20.+args.step/2, args.step), 10)
    z_axis = np.round(np.arange(-4.9, 4.9+args.step/2, args.step), 10)
    sources = sorted({(service, step) for service, _, step, _ in CASES.values()})
    jets = {}
    with ProcessPoolExecutor(args.workers) as pool:
        for service, step, s, array in pool.map(jets_row, [(name, step, float(s), z_axis) for name, step in sources
                                                           for s in s_axis]):
            jets[(service, step, s)] = array
    print("jets", round(time.time()-started, 1), flush=True)
    rows = []
    with ProcessPoolExecutor(args.workers) as pool:
        tasks = [(case, float(s), z_axis, jets[(CASES[case][0], CASES[case][2], float(s))]) for case in CASES
                 for s in s_axis]
        for chunk in pool.map(layer_row, tasks, chunksize=2):
            rows.extend(chunk)
    samples = pd.DataFrame(rows)
    samples.to_csv(args.output/"samples.csv.gz", index=False, compression={"method": "gzip", "mtime": 0},
                   float_format="%.7g")
    print("layers", round(time.time()-started, 1), flush=True)
    staged = [case for case in CASES if CASES[case][1] != "colocated"]
    targets = [(case, float(row.s), float(row.z)) for case in staged
               for _, row in samples[samples.case == case].nlargest(RESOLVED_SAMPLES, "estimated_band_width").iterrows()]
    with ProcessPoolExecutor(args.workers) as pool:
        resolved = pd.DataFrame(list(pool.map(resolve_bands, targets)), columns=["case", "s", "z", "crossings", "width"])
    resolved.to_csv(args.output/"resolved_bands.csv", index=False)
    print("bands", round(time.time()-started, 1), flush=True)
    summary = pd.DataFrame([summarize(samples[samples.case == case], case, args.step, resolved) for case in CASES])
    summary.to_csv(args.output/"summary.csv", index=False)
    audit_log = []
    services = pd.DataFrame()
    if not args.skip_audits:
        services, comparison = service_audits(args, audit_log)
        services.to_csv(args.output/"service_summary.csv", index=False)
        comparison.pivot_table(index=["audit", "metric"], columns="ledger", values="value", aggfunc="first",
                               sort=False).to_csv(args.output/"audit_comparison_wide.csv")
    figures(samples, args.output)
    manifest = {
        "completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time()-started, 1), "workers": args.workers, "step": args.step,
        "noise_floor": NOISE_FLOOR, "standing_reference": STANDING_REFERENCE,
        "envelope_params_changed": {k: v for k, v in asdict(ENVELOPE).items() if v != asdict(BASE)[k]},
        "resolved_samples_per_case": RESOLVED_SAMPLES,
        "layers": LAYERS, "cases": CASES, "audit_log": audit_log,
        "reference_ledger_sha256": sha256_file(service_checks.REFERENCE),
        "software_sha256": {path: sha256_file(ROOT/"toolkit/adm_harness_cli"/path) for path in (
            "adm_harness/axial_track.py", "adm_harness/axial_einstein_generated.py",
            "adm_harness/constant_radius_track.py", "scripts/run_one_space_revision.py")},
    }
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=1, default=str)+"\n")
    pd.set_option("display.width", 250)
    print(summary.T.to_string())
    print(services.T.to_string())


if __name__ == "__main__":
    main()
