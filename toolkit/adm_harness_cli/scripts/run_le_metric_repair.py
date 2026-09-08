#!/usr/bin/env python3
"""Audit the combined C2 candidate and a bounded, uniform-rate repair family.

Produces numerical evidence and a figure. Narrative interpretation is manual.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone
from functools import partial
import json
import math
import multiprocessing
from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy.optimize import brentq

from run_le_geometry_boundary import ROOT, save_records, extrema, profile_burdens
from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.metric_regularity import regularized_scalars, rate_scaled_scalars
from adm_harness.receiver_regularity import repaired_receiver_scalars
from adm_harness.source_ledger import (
    SourceParams, live_packet_end, release_beta_interval, sha256_file,
    standing_support_packet_carve_shoulder_window,
    standing_support_packet_smooth_split_entry_window,
    standing_support_packet_smooth_split_catch_window,
    standing_support_packet_smooth_split_edge_window,
)

PARAMS = None
RATES = [1., .5, .25, .125, .0625, .03125, .015625]
CHANNELS = ["rho", "p_l", "j_l", "p_omega"]


def initialize(parameters):
    global PARAMS
    PARAMS = SourceParams(**parameters)


def point(phase, ell, level=2, rate=1., variant="combined", **extra):
    step = .0025/2**level
    return {"phase": float(phase), "s": float(phase/rate if rate else phase), "l": float(ell),
            "level": level, "rate": rate, "holding": rate == 0, "h_s": step/rate if rate else step,
            "h_l": step, "variant": variant, "width_factor": 1., **extra}


def evaluate(task):
    provider = repaired_receiver_scalars if task["variant"] == "receiver_only" else regularized_scalars
    if task["rate"] not in [0., 1.]:
        provider = partial(rate_scaled_scalars, rate=task["rate"])
    row = evaluate_demand(task["s"], task["l"], PARAMS, task["h_s"], task["h_l"],
                          h_theta=task.get("h_theta", 1e-4), holding=task["holding"], scalar_evaluator=provider)
    row.update(task)
    if not row["full_eigensystem_certified"]:
        raise ArithmeticError("uncertified demanded-tensor eigensystem")
    if row["stress_algebraic_type"] == "type_iv_flux_dominant" and row["raw_imaginary_eigenvalue_scale"] == 0:
        raise ArithmeticError("projected Type IV lacks a raw complex pair")
    return row


def batch(tasks):
    return [evaluate(task) for task in tasks]


def run(tasks, args, parameters, name):
    started = last = time.monotonic()
    records = []
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn"),
                             initializer=initialize, initargs=(parameters,)) as executor:
        for rows in executor.map(batch, [tasks[i:i+32] for i in range(0, len(tasks), 32)]):
            records.extend(rows)
            now = time.monotonic()
            if now-last > 20:
                print(f"{name}: {len(records)}/{len(tasks)}, {now-started:.0f} s", flush=True)
                last = now
    frame = save_records(records, args.output, name)
    print(f"{name}: {len(frame)} points, {time.monotonic()-started:.1f} s", flush=True)
    return frame


def join_tasks(params, phases):
    tasks, locations = [], []
    inner = params.Rth*params.support_edge_receiver_inner_multiplier
    outer = params.Rth*params.support_edge_receiver_outer_multiplier
    blend = (outer-inner)*.125
    for phase in [phases["reset_decompression"], phases["worst_dec"], -.63]:
        for ell in [0., -.1, .1, -inner, -inner-blend, -outer+blend, -outer]:
            locations.append(("radial", phase, ell))
            for level in range(8):
                for rate in [0., 1.]:
                    for variant in ["receiver_only", "combined"]:
                        tasks.append(point(phase, ell, level, rate, variant, study="radial_join", join_l=ell))
    catch_width = max(params.w_catch_beta, params.w_catch_packet)
    lo, hi = params.x_catch_packet-2*catch_width, params.x_catch_packet+2*catch_width
    anchor = params.x_catch_packet if params.support_shell_time_anchor is None else params.support_shell_time_anchor
    center = anchor-params.support_shell_catch_lead
    distance = abs(min(max(center, lo), hi)-center)
    start_radius = math.sqrt(distance**2-2*params.support_shell_temporal_width**2*math.log(.75))
    cap_joins = [center-distance, center+distance, center-start_radius, center+start_radius]
    release_start, release_end = release_beta_interval(params)
    temporal_joins = sorted(set(cap_joins+[params.q_t0, params.q_t0+params.q_Tr,
        params.x_catch_beta-2*params.w_catch_beta, params.x_catch_beta+2*params.w_catch_beta,
        lo, hi, release_start, release_end,
        release_end+params.support_edge_receiver_post_release_widths*params.w_beta,
        release_end+(params.support_edge_receiver_post_release_widths+2)*params.w_beta,
        lo-params.w_beta, lo+params.w_beta, hi-params.w_beta, hi+params.w_beta,
        live_packet_end(params)-params.w_beta, live_packet_end(params)+params.w_beta]))
    for phase in temporal_joins:
        for ell in [-1.8, -1.3, 0., 1.3]:
            locations.append(("temporal", phase, ell))
            for level in range(5):
                variants = ["receiver_only", "combined"] if phase in cap_joins else ["combined"]
                for variant in variants:
                    tasks.append(point(phase, ell, level, variant=variant, study="temporal_join", join_s=phase))
    for phase in [phases["worst_dec"], phases["reset_decompression"]]:
        for radius_multiplier, width_multiplier in [(1., 4.8), (1., 3.4), (1., 7.2), (1.7, 7.2)]:
            r, w = params.Rpass*radius_multiplier, params.w_pass*width_multiplier
            distance = math.sqrt(r*r+2*r*w-params.eps**2)
            for sign in [-1, 1]:
                ell = phase+sign*distance
                locations.append(("compact_radial", phase, ell))
                for level in range(5):
                    tasks.append(point(phase, ell, level, study="compact_join", join_l=ell))
    return tasks, locations


def metric_jets(locations, params, output):
    records = []
    for kind, phase, ell in locations:
        axis = "s" if kind == "temporal" else "l"
        for variant, provider in [("receiver_only", repaired_receiver_scalars), ("combined", regularized_scalars)]:
            for step in [.001, .0005, .00025]:
                center = provider(phase, ell, params)
                for key in ["alpha", "beta", "gamma_ll", "gamma_omega"]:
                    scale = max(1., abs(center[key]))
                    jets = []
                    for direction in [-1, 1]:
                        offsets = direction*np.arange(5.)
                        values = [(provider(phase+x*step if axis == "s" else phase,
                                            ell+x*step if axis == "l" else ell, params)[key]-center[key])/scale
                                  for x in offsets]
                        polynomial = np.polynomial.Polynomial.fit(offsets, values, 4).convert()
                        jets.append([polynomial.deriv(n)(0)/step**n for n in [1, 2]])
                    records.append({"kind": kind, "s": phase, "l": ell, "axis": axis, "variant": variant,
                        "field": key, "step": step, "value_scale": scale,
                        "first_left": jets[0][0], "first_right": jets[1][0],
                        "second_left": jets[0][1], "second_right": jets[1][1],
                        "first_jump": jets[1][0]-jets[0][0], "second_jump": jets[1][1]-jets[0][1]})
    pd.DataFrame(records).to_csv(output / "metric_join_jets.csv.gz", index=False, compression={"method": "gzip", "mtime": 0})


def root_job(job):
    phase, left, right, root_id = job
    records, summaries = [], []
    for level in [2, 3, 4]:
        def enthalpy(ell):
            row = evaluate(point(phase, ell, level, 0.))
            return row["rho"]+row["p_l"]
        root = brentq(enthalpy, left, right, xtol=1e-9, rtol=1e-12)
        static = evaluate(point(phase, root, level, 0., study="static_enthalpy_root", root_id=root_id))
        active = evaluate(point(phase, root, level, 1., study="static_enthalpy_root", root_id=root_id))
        h0 = static["rho"]+static["p_l"]
        h2 = active["rho"]+active["p_l"]-h0
        slope_step = .001
        slope = (enthalpy(root+slope_step)-enthalpy(root-slope_step))/(2*slope_step)
        threshold = 2*abs(active["j_l"]/h2) if h2 else float("inf")
        summaries.append({"phase": phase, "root_id": root_id, "level": level, "root_l": root,
            "static_enthalpy_residual": h0, "static_enthalpy_slope": slope,
            "unit_rate_j": active["j_l"], "dynamic_enthalpy_coefficient": h2,
            "rate_threshold_at_static_root": threshold})
        for rate in [0.]+RATES:
            row = static if rate == 0 else active if rate == 1 else evaluate(
                point(phase, root, level, rate, study="static_enthalpy_root", root_id=root_id))
            row["max_rate_scaling_error"] = max(abs(row[k]-(rate*active[k] if k == "j_l" else
                static[k]+rate**2*(active[k]-static[k]))) for k in CHANNELS)
            records.append(row)
    return records, summaries


def find_roots(profiles, args, parameters):
    jobs = []
    selected = profiles[profiles.holding & (profiles.level == 2)]
    for phase, group in selected.groupby("phase"):
        group = group.sort_values("l")
        h0 = (group.rho+group.p_l).to_numpy()
        ell = group.l.to_numpy()
        for i in range(len(group)-1):
            if h0[i]*h0[i+1] < 0:
                jobs.append((phase, ell[i], ell[i+1], len(jobs)))
    records, summaries = [], []
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn"),
                             initializer=initialize, initargs=(parameters,)) as executor:
        for rows, table in executor.map(root_job, jobs):
            records.extend(rows)
            summaries.extend(table)
    frame = save_records(records, args.output, "root_rate_eigensystems")
    summary = pd.DataFrame(summaries)
    summary.to_csv(args.output / "static_enthalpy_roots.csv", index=False)
    print(f"roots: {len(jobs)} crossing brackets, {len(frame)} certified rate samples", flush=True)
    return frame, summary


def carve_envelope(params, output):
    # Every schedule is in [0, 1]; replacing it by one gives a radial upper envelope.
    always = replace(params, standing_support_packet_exclusion_shoulder_schedule="always",
        standing_support_packet_smooth_split_entry_schedule="always",
        standing_support_packet_smooth_split_catch_schedule="always",
        standing_support_packet_smooth_split_edge_schedule="always")
    records = []
    for distance in np.linspace(0, 2, 2001):
        envelope = params.standing_support_packet_exclusion_shoulder*standing_support_packet_carve_shoulder_window(0., distance, always)
        envelope += params.standing_support_packet_smooth_split_entry_carve*standing_support_packet_smooth_split_entry_window(0., distance, always)
        envelope += params.standing_support_packet_smooth_split_catch_carve*standing_support_packet_smooth_split_catch_window(0., distance, always)
        envelope += params.standing_support_packet_smooth_split_edge_carve*standing_support_packet_smooth_split_edge_window(0., distance, always)
        records.append({"packet_distance": distance, "carve_upper_envelope": envelope})
    frame = pd.DataFrame(records)
    frame.to_csv(output / "carve_upper_envelope.csv", index=False)
    return float(frame.carve_upper_envelope.max())


def plots(output, joins, root_rates, local):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), constrained_layout=True)
    phase = float(root_rates.phase.max())
    origin = joins[(joins.study == "radial_join") & (joins.l == 0) & np.isclose(joins.phase, phase) & joins.holding]
    for variant, group in origin.groupby("variant"):
        axes[0].loglog(group.h_l, group.p_omega.abs(), ".-", label=variant.replace("_", " "))
    selected = local[(local.level == 4)]
    for rate, group in selected.groupby("rate"):
        axes[1].plot(group.scaled_offset, group.radial_block_discriminant/rate**2, label=f"rate {rate:g}")
    root = root_rates[(root_rates.root_id == int(local.root_id.iloc[0])) & (root_rates.level == 4) & (root_rates.rate > 0)]
    axes[2].loglog(root.rate, root.imaginary_eigenvalue_scale, ".-", label="projected tensor")
    axes[2].loglog(root.rate, root.raw_imaginary_eigenvalue_scale, "x", label="raw tensor")
    axes[0].set(xlabel="curvature step", ylabel="absolute angular pressure", title="Static throat regularity")
    axes[1].axhline(0, color="black", lw=.7)
    axes[1].set(xlabel="(ell − static root) / rate", ylabel="discriminant / rate²", title="Type IV layer under slowdown")
    axes[2].set(xlabel="rate", ylabel="complex eigenvalue magnitude", title="Persistent root witness")
    for axis in axes:
        axis.grid(alpha=.2)
        axis.legend(fontsize=8)
    fig.savefig(output / "bounded_repair_diagnostic.png", dpi=170)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_reports/data/le_metric_c2_repair")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    reference = ROOT / "supporting_reports/data/le_geometry_boundary"
    manifest = json.loads((reference / "manifest.json").read_text())
    parameters = manifest["params"]
    params = SourceParams(**parameters)
    source = ROOT / "toolkit/adm_harness_cli/adm_harness/source_ledger.py"
    if sha256_file(source) != manifest["source_manifests"]["dense"]["source_ledger_module_sha256"]:
        raise ValueError("frozen source kernel has changed")
    old_witnesses = pd.read_csv(reference / "witnesses.csv.gz")
    witness_tasks = [point(r.s, r.l, int(r.level), 0. if r.holding else 1., study="witness",
        h_s=r.h_s, h_l=r.h_l, h_theta=r.h_theta) for r in old_witnesses.itertuples()]
    witnesses = run(witness_tasks, args, parameters, "witnesses")
    witness_error = float(np.max(np.abs(witnesses[CHANNELS].to_numpy()-old_witnesses[CHANNELS].to_numpy())))
    tasks, locations = join_tasks(params, manifest["phases"])
    joins = run(tasks, args, parameters, "joins")
    metric_jets(locations, params, args.output)
    envelope_max = carve_envelope(params, args.output)
    old_profiles = pd.read_csv(reference / "phase_profiles.csv.gz")
    tasks = [point(r.s, r.l, int(r.level), 0. if r.holding else 1., study="phase_profile",
             h_s=r.h_s, h_l=r.h_l, h_theta=r.h_theta) for r in old_profiles.itertuples()]
    profiles = run(tasks, args, parameters, "phase_profiles")
    profile_burdens(profiles, args.output, "phase_profiles")
    roots, root_summary = find_roots(profiles, args, parameters)
    reset = manifest["phases"]["reset_decompression"]
    eligible = root_summary[(root_summary.level == 4) & np.isclose(root_summary.phase, reset)
                           & (root_summary.rate_threshold_at_static_root > 1.05)]
    if eligible.empty:
        raise ArithmeticError("the planned reset root witness requires reassessment")
    anchor = eligible.sort_values("root_l").iloc[0]
    tasks = []
    # Coordinate extent contracts with rate; the curvature step is refined independently.
    span = 4*abs(anchor.unit_rate_j/anchor.static_enthalpy_slope)
    for rate in [.125, .0625, .03125, .015625]:
        for level in [3, 4]:
            for offset in np.linspace(-span, span, 81):
                tasks.append(point(reset, anchor.root_l+rate*offset, level, rate,
                    study="root_layer", root_id=int(anchor.root_id), scaled_offset=float(offset)))
    local = run(tasks, args, parameters, "root_layer")
    pd.DataFrame([{"rate": rate, "level": level, **extrema(group)}
        for (rate, level), group in local.groupby(["rate", "level"])]).to_csv(args.output / "root_layer_summary.csv", index=False)
    tasks = [point(reset, ell, 2, rate, study="rate_profile") for rate in RATES
             for ell in np.linspace(-4, 4, 321)]
    rates = run(tasks, args, parameters, "rate_profiles")
    pd.DataFrame([{"rate": rate, **extrema(group)} for rate, group in rates.groupby("rate")]).to_csv(
        args.output / "rate_profile_summary.csv", index=False)
    plots(args.output, joins, roots, local)
    metadata = {"completed_utc": datetime.now(timezone.utc).isoformat(), "elapsed_seconds": time.monotonic()-started,
        "workers": args.workers, "params": parameters, "rates": RATES, "origin_width": .1, "cap_width": .25,
        "source_kernel_sha256": sha256_file(source), "reference_manifest_sha256": sha256_file(reference / "manifest.json"),
        "witness_max_channel_change": witness_error, "sampled_carve_envelope_max": envelope_max,
        "retained_curvature_samples": sum(len(f) for f in [witnesses, joins, profiles, roots, local, rates]),
        "root_solver_evaluations": "additional curvature calls used by bracketed root solves; retained root tensors listed separately",
        "max_rate_scaling_error": float(roots.max_rate_scaling_error.max()),
        "software_sha256": {str(path.relative_to(ROOT)): sha256_file(path) for path in [Path(__file__).resolve(),
            ROOT / "toolkit/adm_harness_cli/adm_harness/metric_regularity.py",
            ROOT / "toolkit/adm_harness_cli/adm_harness/receiver_regularity.py",
            ROOT / "toolkit/adm_harness_cli/adm_harness/geometry_boundary.py",
            ROOT / "toolkit/adm_harness_cli/adm_harness/radial_stress.py",
            ROOT / "toolkit/adm_harness_cli/scripts/run_le_geometry_boundary.py"]},
        "scope": "combined metric regularity candidate and uniform-rate diagnostic; physical sources and service gates remain separate",
        "output_bytes_before_manifest": sum(p.stat().st_size for p in args.output.iterdir() if p.is_file())}
    (args.output / "manifest.json").write_text(json.dumps(metadata, indent=2)+"\n")
    print(json.dumps({k: metadata[k] for k in ["elapsed_seconds", "retained_curvature_samples",
        "witness_max_channel_change", "max_rate_scaling_error", "output_bytes_before_manifest"]}), flush=True)


if __name__ == "__main__":
    main()
