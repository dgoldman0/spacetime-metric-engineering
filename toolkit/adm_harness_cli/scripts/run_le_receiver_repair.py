#!/usr/bin/env python3
"""Evaluate the local C2 angular-receiver repair against the frozen diagnostic.

Emit numerical data and figures. The narrative report is maintained manually.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from functools import partial
import json
import multiprocessing
from pathlib import Path
import time

import numpy as np
import pandas as pd

from run_le_geometry_boundary import ROOT, WINDOWS, save_records, extrema, profile_burdens
from adm_harness.geometry_boundary import evaluate_demand, metric_scalars
from adm_harness.receiver_regularity import repaired_receiver_scalars
from adm_harness.source_ledger import SourceParams, sha256_file

PARAMS = None


def initialize(parameters):
    global PARAMS
    PARAMS = SourceParams(**parameters)


def batch(tasks):
    records = []
    for task in tasks:
        blend = task["blend_fraction"]
        provider = metric_scalars if blend == 0 else partial(repaired_receiver_scalars, blend_fraction=blend)
        row = evaluate_demand(task["s"], task["l"], PARAMS, task["h_s"], task["h_l"],
                              h_theta=task.get("h_theta", 1e-4), holding=task["holding"], scalar_evaluator=provider)
        row.update(task)
        fields = provider(task["s"], task["l"], PARAMS)
        reference = metric_scalars(task["s"], task["l"], PARAMS)
        row.update({key: fields[key] for key in WINDOWS})
        for key in ["alpha", "beta", "gamma_ll", "gamma_omega"]:
            row[key+"_change"] = fields[key]-reference[key]
        row["relative_gamma_omega_change"] = row["gamma_omega_change"]/reference["gamma_omega"]
        scale = max(abs(row[key]) for key in ["rho", "p_l", "j_l", "p_omega"])
        row["transverse_to_density"] = abs(row["p_omega"])/max(abs(row["rho"]), 1e-12*scale, np.finfo(float).tiny)
        if not row["full_eigensystem_certified"]:
            raise ArithmeticError("candidate eigensystem failed certification")
        if row["stress_algebraic_type"] == "type_iv_flux_dominant" and row["raw_imaginary_eigenvalue_scale"] == 0:
            raise ArithmeticError("projected Type IV lacks a raw complex pair")
        records.append(row)
    return records


def run(tasks, args, parameters, name):
    started = time.monotonic()
    last = started
    records = []
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn"),
                             initializer=initialize, initargs=(parameters,)) as executor:
        for rows in executor.map(batch, [tasks[i:i+32] for i in range(0, len(tasks), 32)]):
            records.extend(rows)
            now = time.monotonic()
            if now-last > 20:
                print(f"{name}: {len(records)}/{len(tasks)} samples, {now-started:.0f} s", flush=True)
                last = now
    frame = save_records(records, args.output, name)
    print(f"{name}: {len(frame)} points, {time.monotonic()-started:.1f} s", flush=True)
    return frame


def task(study, s, l, level, holding, blend=.125, **extra):
    return {"study": study, "s": float(s), "l": float(l), "level": level, "holding": bool(holding),
            "h_s": .0025/2**level, "h_l": .0025/2**level, "blend_fraction": blend,
            "width_factor": blend/.125, **extra}


def matched_tasks(frame, study, blend=.125):
    return [task(study, row.s, row.l, int(row.level), row.holding, blend,
                 h_s=row.h_s, h_l=row.h_l, h_theta=row.h_theta) for row in frame.itertuples()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--reference", type=Path, default=ROOT / "supporting_reports/data/le_geometry_boundary")
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_reports/data/le_receiver_c2_repair")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    if args.output.resolve() == args.reference.resolve():
        parser.error("candidate output must be separate from the reference")
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    manifest = json.loads((args.reference / "manifest.json").read_text())
    parameters = manifest["params"]
    source = ROOT / "toolkit/adm_harness_cli/adm_harness/source_ledger.py"
    if sha256_file(source) != manifest["source_manifests"]["dense"]["source_ledger_module_sha256"]:
        raise ValueError("frozen source kernel has changed")
    sigma = manifest["phases"]["reset_decompression"]
    inner = parameters["Rth"]*parameters["support_edge_receiver_inner_multiplier"]
    outer = parameters["Rth"]*parameters["support_edge_receiver_outer_multiplier"]
    span = outer-inner
    reference_witnesses = pd.read_csv(args.reference / "witnesses.csv.gz")
    witnesses = run(matched_tasks(reference_witnesses, "witness", 0.)+matched_tasks(reference_witnesses, "witness"),
                    args, parameters, "witnesses")
    baseline = witnesses[witnesses.blend_fraction == 0].reset_index(drop=True)
    candidate = witnesses[witnesses.blend_fraction == .125].reset_index(drop=True)
    channels = ["rho", "p_l", "j_l", "p_omega"]
    reference_error = float(np.max(np.abs(baseline[channels].to_numpy()-reference_witnesses[channels].to_numpy())))
    if reference_error > 1e-9:
        raise ArithmeticError("baseline no longer reproduces the retained witness channels")
    comparison = candidate[["s", "l", "holding", "level", "radial_block_discriminant", "stress_algebraic_type"]].copy()
    comparison["baseline_delta"] = baseline.radial_block_discriminant
    comparison["max_channel_change"] = np.max(np.abs(candidate[channels].to_numpy()-baseline[channels].to_numpy()), axis=1)
    comparison.to_csv(args.output / "witness_comparison.csv", index=False)
    tasks = []
    for blend in [0., .125]:
        b = .125*span
        for s in [sigma, manifest["phases"]["worst_dec"]]:
            for edge, ell in [("inner", -inner), ("inner_join", -inner-b), ("outer_join", -outer+b), ("outer", -outer)]:
                for level in range(8):
                    for holding in [False, True]:
                        tasks.append(task("joins", s, ell, level, holding, blend, edge=edge))
    joins = run(tasks, args, parameters, "joins")
    reference_profiles = pd.read_csv(args.reference / "phase_profiles.csv.gz")
    profiles = run(matched_tasks(reference_profiles, "phase_profile"), args, parameters, "phase_profiles")
    summary = profile_burdens(profiles, args.output, "phase_profiles")
    old_summary = pd.read_csv(args.reference / "phase_profiles_summary.csv")
    pd.concat([old_summary.assign(variant="baseline"), summary.assign(variant="c2")]).to_csv(args.output / "phase_profile_comparison.csv", index=False)
    old_patch = pd.read_csv(args.reference / "local_patch.csv.gz")
    patch = run(matched_tasks(old_patch, "local_patch"), args, parameters, "local_patch")
    pd.DataFrame([{"level": level, **extrema(group)} for level, group in patch.groupby("level")]).to_csv(args.output / "local_patch_summary.csv", index=False)
    old_side = pd.read_csv(args.reference / "receiver_one_sided.csv.gz")
    side_tasks = [task("inner_one_sided", row.s, row.l, 0, row.holding, distance=row.distance,
                       h_s=row.h_s, h_l=row.h_l, distance_per_h_l=row.distance_per_h_l) for row in old_side.itertuples()]
    side = run(side_tasks, args, parameters, "inner_one_sided")
    integrals = []
    for (holding, resolution), group in side.groupby(["holding", "distance_per_h_l"]):
        group = group.sort_values("distance")
        for cutoff in [1e-2, 1e-3, 1e-4, 1e-5]:
            selected = group[group.distance >= cutoff]
            integrals.append({"holding": holding, "distance_per_h_l": resolution, "cutoff": cutoff,
                              "source_frame_norm_proper_integral": np.trapezoid(selected.source_frame_frobenius*np.sqrt(selected.gamma_ll), selected.distance)})
    pd.DataFrame(integrals).to_csv(args.output / "inner_truncated_burden.csv", index=False)
    tasks = [task("blend_sensitivity", sigma, ell, level, holding, blend) for blend in [.0625, .25]
             for level in range(3) for holding in [False, True] for ell in np.linspace(-4, 4, 80*2**level+1)]
    sensitivity = run(tasks, args, parameters, "blend_sensitivity")
    combined = pd.concat([sensitivity, profiles[np.isclose(profiles.s, sigma)].assign(study="blend_sensitivity")])
    profile_burdens(combined, args.output, "blend_sensitivity")
    old_tail = pd.read_csv(args.reference / "exterior_tail.csv.gz")
    tail = run(matched_tasks(old_tail, "exterior_tail"), args, parameters, "exterior_tail")
    tail_error = float(np.max(np.abs(tail[channels].to_numpy()-old_tail[channels].to_numpy())))
    plots(args, sigma, joins, profiles, reference_profiles, side, old_side)
    metadata = {
        "completed_utc": datetime.now(timezone.utc).isoformat(), "elapsed_seconds": time.monotonic()-started,
        "workers": args.workers, "params": parameters, "nominal_blend_fraction": .125,
        "blend_physical_width": .125*span, "blend_variants": [.0625, .125, .25],
        "fresh_points": sum(len(frame) for frame in [witnesses, joins, profiles, patch, side, sensitivity, tail]),
        "reference_manifest_sha256": sha256_file(args.reference / "manifest.json"),
        "baseline_witness_max_channel_error": reference_error, "tail_max_channel_change": tail_error,
        "source_kernel_sha256": sha256_file(source),
        "software_sha256": {str(path.relative_to(ROOT)): sha256_file(path) for path in [Path(__file__).resolve(),
            ROOT / "toolkit/adm_harness_cli/adm_harness/receiver_regularity.py",
            ROOT / "toolkit/adm_harness_cli/adm_harness/geometry_boundary.py",
            ROOT / "toolkit/adm_harness_cli/adm_harness/radial_stress.py",
            ROOT / "toolkit/adm_harness_cli/scripts/run_le_geometry_boundary.py"]},
        "interpretation_scope": "local angular-receiver regularity repair; the physical source and service gates require separate validation",
    }
    metadata["output_bytes_before_manifest"] = sum(path.stat().st_size for path in args.output.iterdir() if path.is_file())
    (args.output / "manifest.json").write_text(json.dumps(metadata, indent=2)+"\n")
    print(json.dumps({key: metadata[key] for key in ["elapsed_seconds", "fresh_points", "baseline_witness_max_channel_error", "tail_max_channel_change", "output_bytes_before_manifest"]}), flush=True)


def plots(args, sigma, joins, profiles, reference_profiles, side, old_side):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for (blend, holding), group in joins[(joins.edge == "inner") & np.isclose(joins.s, sigma)].groupby(["blend_fraction", "holding"]):
        label = ("original" if blend == 0 else "C2 repair")+(" static" if holding else " active")
        axes[0].loglog(group.h_l, group.rho.abs(), ".-", label=label)
    for label, frame in [("original", old_side), ("C2 repair", side)]:
        selected = frame[(frame.distance_per_h_l == 32) & frame.holding].sort_values("distance")
        axes[1].loglog(selected.distance, selected.source_frame_frobenius, label=label+" static")
    axes[0].set(xlabel="curvature step", ylabel="absolute Eulerian density", title="Exact inner edge")
    axes[1].set(xlabel="distance from inner edge", ylabel="ADM-frame tensor norm", title="Approach from the receiver side")
    for axis in axes:
        axis.legend(fontsize=8)
        axis.grid(alpha=.2)
    fig.savefig(args.output / "regularity_comparison.png", dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for label, frame in [("original", reference_profiles), ("C2 repair", profiles)]:
        selected = frame[np.isclose(frame.s, sigma) & (~frame.holding) & (frame.level == 2)].sort_values("l")
        axes[0].plot(selected.l, selected.radial_block_discriminant, label=label)
        axes[1].plot(selected.l, selected.imaginary_eigenvalue_scale, label=label)
    axes[0].set(xlabel="ell", ylabel="radial discriminant", ylim=(-.0025, .0005), title="Reset slice: Type IV range")
    axes[1].set(xlabel="ell", ylabel="imaginary eigenvalue magnitude", title="Remaining Type IV demand")
    for axis in axes:
        axis.set_xlim(-2.5, -.5)
        axis.legend()
        axis.grid(alpha=.2)
    fig.savefig(args.output / "type_iv_comparison.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
