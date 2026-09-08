#!/usr/bin/env python3
"""Resolve receiver-edge regularity exposed by the geometry boundary sweep.

Writes numerical data/figures; narrative interpretation is maintained manually.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone
import json
import multiprocessing
from pathlib import Path
import time

import numpy as np
import pandas as pd

from run_le_geometry_boundary import ROOT, WINDOWS, save_records, profile_burdens
from adm_harness.geometry_boundary import evaluate_demand, metric_scalars
from adm_harness.source_ledger import SourceParams, einstein_tensor_at, projections, sha256_file

PARAMS = None


def initialize(parameters):
    global PARAMS
    PARAMS = SourceParams(**parameters)


def batch(tasks):
    result = []
    for task in tasks:
        changes = {}
        if task.get("receiver_angular_off", False):
            changes["support_edge_receiver_angular_log_gain"] = 0.
        if "receiver_width" in task:
            changes["support_edge_receiver_radial_width"] = task["receiver_width"]
        params = replace(PARAMS, **changes)
        row = evaluate_demand(task["s"], task["l"], params, task["h_s"], task["h_l"], holding=task["holding"])
        row.update(task)
        fields = metric_scalars(task["s"], task["l"], params)
        row.update({k: fields[k] for k in WINDOWS})
        scale = max(abs(row[k]) for k in ["rho", "p_l", "j_l", "p_omega"])
        row["transverse_to_density"] = abs(row["p_omega"])/max(abs(row["rho"]), 1e-12*scale, np.finfo(float).tiny)
        result.append(row)
    return result


def run(tasks, args, parameters, name):
    records = []
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn"),
                             initializer=initialize, initargs=(parameters,)) as executor:
        for rows in executor.map(batch, [tasks[i:i+32] for i in range(0, len(tasks), 32)]):
            records.extend(rows)
    frame = save_records(records, args.output, name)
    print(f"{name}: {len(frame)} points", flush=True)
    return frame


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_reports/data/le_geometry_boundary")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    start = time.monotonic()
    original = args.output / "manifest.json"
    manifest = json.loads(original.read_text())
    parameters = manifest["params"]
    sigma = manifest["phases"]["reset_decompression"]
    params = SourceParams(**parameters)
    inner = params.Rth*params.support_edge_receiver_inner_multiplier
    outer = params.Rth*params.support_edge_receiver_outer_multiplier
    width = (outer-inner)/8 if params.support_edge_receiver_radial_width is None else params.support_edge_receiver_radial_width
    tasks = []
    for angular_off in [False, True]:
        for edge, ell in [("negative_inner", -inner), ("negative_outer", -outer), ("positive_inner", inner), ("positive_outer", outer)]:
            for holding in [False, True]:
                for level in range(8):
                    h = .0025/2**level
                    tasks.append({"study": "receiver_exact_edge", "s": sigma, "l": ell, "edge": edge,
                                  "level": level, "h_s": h, "h_l": h, "holding": holding, "receiver_angular_off": angular_off})
    edges = run(tasks, args, parameters, "receiver_exact_edges")
    tasks = []
    distances = np.unique(np.r_[np.geomspace(1e-5, .02, 241), [1e-2, 1e-3, 1e-4, 1e-5]])
    for holding in [False, True]:
        for resolution in [16, 32]:
            for distance in distances:
                tasks.append({"study": "receiver_inner_one_sided", "s": sigma, "l": -inner-distance,
                              "distance": distance, "h_s": .000625, "h_l": distance/resolution,
                              "holding": holding, "distance_per_h_l": resolution})
    one_sided = run(tasks, args, parameters, "receiver_one_sided")
    integrals = []
    for (holding, resolution), group in one_sided.groupby(["holding", "distance_per_h_l"]):
        group = group.sort_values("distance")
        for cutoff in [1e-2, 1e-3, 1e-4, 1e-5]:
            selected = group[group.distance >= cutoff]
            integrals.append({"holding": holding, "distance_per_h_l": resolution, "cutoff": cutoff,
                              "upper_distance": .02, "points": len(selected),
                              "source_frame_norm_proper_integral": np.trapezoid(selected.source_frame_frobenius*np.sqrt(selected.gamma_ll), selected.distance)})
    pd.DataFrame(integrals).to_csv(args.output / "receiver_inner_truncated_burden.csv", index=False)
    fields = []
    for distance in np.geomspace(1e-8, 1e-2, 61):
        sc = metric_scalars(sigma, -inner-distance, params)
        window = sc["support_edge_receiver_angular_flange_window"]
        fields.append({"distance": distance, "angular_window": window, "window_over_sqrt_distance": window/np.sqrt(distance),
                       "delta_gamma_omega": sc["support_edge_receiver_delta_gamma_omega"],
                       "delta_gamma_omega_over_sqrt_distance": sc["support_edge_receiver_delta_gamma_omega"]/np.sqrt(distance)})
    pd.DataFrame(fields).to_csv(args.output / "receiver_inner_metric_asymptotic.csv", index=False)
    tasks = []
    for factor in [.5, 1., 2.]:
        for level in range(3):
            for holding in [False, True]:
                for ell in np.linspace(-2.5, -1.5, 20*2**level+1):
                    tasks.append({"study": "receiver_width", "s": sigma, "l": float(ell), "level": level,
                                  "h_s": .0025/2**level, "h_l": .0025/2**level, "holding": holding,
                                  "width_factor": factor, "receiver_width": width*factor})
    widths = run(tasks, args, parameters, "receiver_width_variants")
    profile_burdens(widths, args.output, "receiver_width")
    crosschecks = []
    for s, ell in [(sigma, -1.8), (sigma, -inner), (sigma, -outer), (15., 6.), (-.6662234042553191, -.85)]:
        for h in [.0025, .000625]:
            source, _ = einstein_tensor_at(s, ell, params, h, h)
            reference = projections(s, ell, source, params)
            fresh = evaluate_demand(s, ell, params, h, h)
            pairs = [("rho", "rho_euler"), ("p_l", "p_l_unit"), ("legacy_j_l", "j_l_unit"), ("p_omega", "p_omega_unit")]
            errors = {new+"_absolute_error": abs(fresh[new]-reference[old]) for new, old in pairs}
            if max(errors.values()) > 1e-9:
                raise ArithmeticError("cached evaluator differs from frozen source kernel")
            crosschecks.append({"s": s, "l": ell, "h": h, **errors})
    pd.DataFrame(crosschecks).to_csv(args.output / "frozen_kernel_crosschecks.csv", index=False)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for (holding, off), group in edges[edges.edge == "negative_inner"].groupby(["holding", "receiver_angular_off"]):
        label = ("static" if holding else "active")+("; angular term off" if off else "; frozen geometry")
        axes[0].loglog(group.h_l, group.rho.abs(), ".-", label=label)
    frozen = edges[(edges.edge == "negative_inner") & (~edges.holding) & (~edges.receiver_angular_off)].sort_values("h_l")
    axes[0].loglog(frozen.h_l, abs(frozen.rho.iloc[0])*(frozen.h_l/frozen.h_l.iloc[0])**-1.5, "k--", label="h^(-3/2) reference")
    for holding, group in pd.DataFrame(integrals).query("distance_per_h_l == 32").groupby("holding"):
        axes[1].loglog(group.cutoff, group.source_frame_norm_proper_integral, ".-", label="static" if holding else "active")
    axes[0].set(xlabel="curvature step h", ylabel="absolute Eulerian density", title="Receiver inner-edge regularity")
    axes[1].set(xlabel="excluded distance from inner edge", ylabel="truncated proper integral of ADM-frame norm", title="One-sided absolute burden, outer distance 0.02")
    for axis in axes:
        axis.legend(fontsize=8)
        axis.grid(alpha=.2)
    fig.savefig(args.output / "receiver_edge_regularity.png", dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for factor, group in widths[(widths.level == 2) & (~widths.holding)].groupby("width_factor"):
        axes[0].plot(group.l, group.radial_block_discriminant, label=f"receiver width x {factor:g}")
        axes[1].plot(group.l, group.imaginary_eigenvalue_scale, label=f"receiver width x {factor:g}")
    axes[0].set(ylabel="radial discriminant", title="Receiver outer transition: active demand")
    axes[1].set(ylabel="imaginary eigenvalue magnitude", title="Invariant Type IV burden")
    for axis in axes:
        axis.set(xlabel="ell")
        axis.legend(fontsize=8)
        axis.grid(alpha=.2)
    fig.savefig(args.output / "receiver_width_comparison.png", dpi=160)
    plt.close(fig)
    metadata = {"completed_utc": datetime.now(timezone.utc).isoformat(), "workers": args.workers,
                "elapsed_seconds": time.monotonic()-start, "fresh_points": len(edges)+len(one_sided)+len(widths),
                "base_manifest_sha256": sha256_file(original), "inner": inner, "outer": outer, "receiver_width": width,
                "frozen_kernel_crosscheck_points": len(crosschecks),
                "source_ledger_sha256": sha256_file(ROOT / "toolkit/adm_harness_cli/adm_harness/source_ledger.py"),
                "software_sha256": {str(path.relative_to(ROOT)): sha256_file(path) for path in [Path(__file__).resolve(),
                    ROOT / "toolkit/adm_harness_cli/scripts/run_le_geometry_boundary.py",
                    ROOT / "toolkit/adm_harness_cli/adm_harness/geometry_boundary.py"]}}
    (args.output / "receiver_manifest.json").write_text(json.dumps(metadata, indent=2)+"\n")
    print(json.dumps(metadata), flush=True)


if __name__ == "__main__":
    main()
