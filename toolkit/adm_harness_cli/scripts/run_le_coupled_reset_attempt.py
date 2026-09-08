#!/usr/bin/env python3
"""Test the registered reset source and solve its necessary radial constraints.

Numerical outputs only. The design and interpretation are maintained manually.
A failed source or radial-metric condition stops this single candidate before
spacetime evolution and boundary matching.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from datetime import datetime, timezone
import json
import multiprocessing
from pathlib import Path
import time

import numpy as np
import pandas as pd

from run_le_geometry_boundary import ROOT, save_records
from adm_harness.coupled_reset_constraints import ResetSourceSpec, prescribed_reset_source, solve_radial_constraints
from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.metric_regularity import regularized_scalars
from adm_harness.radial_stress import TYPE_IV, certify_radial_eigensystem, radial_tensor
from adm_harness.source_ledger import SourceParams, release_beta_interval, sha256_file

PARAMS = None
CHANNELS = ["rho", "p_l", "j_l", "p_omega"]


def initialize(parameters):
    global PARAMS
    PARAMS = SourceParams(**parameters)


def batch(tasks):
    records = []
    for task in tasks:
        s, ell, h = task["s"], task["l"], task["h_l"]
        def radius(x):
            return np.sqrt(regularized_scalars(s, float(x), PARAMS)["gamma_omega"])
        r = radius(ell)
        r_l = (radius(ell-2*h)-8*radius(ell-h)+8*radius(ell+h)-radius(ell+2*h))/(12*h)
        for holding in [False, True]:
            row = evaluate_demand(s, ell, PARAMS, h, h, holding=holding, scalar_evaluator=regularized_scalars)
            row.update(task)
            row["areal_radius"] = r
            row["areal_radial_derivative"] = r_l
            row["reference_static_mass"] = .5*r*(1.-r_l*r_l/row["gamma_ll"])
            records.append(row)
    return records


def sample_reference(tasks, args, parameters):
    records = []
    started = last = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn"),
                             initializer=initialize, initargs=(parameters,)) as pool:
        for rows in pool.map(batch, [tasks[i:i+24] for i in range(0, len(tasks), 24)]):
            records.extend(rows)
            if time.monotonic()-last > 20:
                print(f"reference tensors: {len(records)}/{2*len(tasks)}, {time.monotonic()-started:.0f} s", flush=True)
                last = time.monotonic()
    return save_records(records, args.output, "reference_tensors")


def evaluate_candidate(reference, args, spec):
    records, summary, component_arrays = [], [], []
    for (s, level), group in reference.groupby(["s", "level"], sort=False):
        static = group[group.holding].sort_values("areal_radius").reset_index(drop=True)
        active = group[~group.holding].sort_values("areal_radius").reset_index(drop=True)
        if not np.array_equal(static.l.to_numpy(), active.l.to_numpy()):
            raise ArithmeticError("active/static reference alignment failed")
        radius = static.areal_radius.to_numpy()
        bg = static[CHANNELS].to_numpy()
        parts = prescribed_reset_source(radius, bg, -active.j_l.to_numpy(), spec)
        solution = solve_radial_constraints(radius, static.reference_static_mass.to_numpy(), bg[:, 0],
                                             parts["total"], float(static.alpha.iloc[-1]))
        control = solve_radial_constraints(radius, static.reference_static_mass.to_numpy(), bg[:, 0],
                                           bg, float(static.alpha.iloc[-1]))
        if not control["stationary_areal_domain"]:
            raise ArithmeticError("matched static reference does not admit the chosen areal chart")
        for i, source in enumerate(parts["total"]):
            tensor = radial_tensor(*source)
            row = certify_radial_eigensystem(tensor)
            row.update({"s": float(s), "l": float(static.l.iloc[i]), "level": int(level),
                "h_l": float(static.h_l.iloc[i]), "areal_radius": radius[i],
                **dict(zip(CHANNELS, source)), "tensor_orthonormal": tensor,
                "imaginary_eigenvalue_scale": float(np.max(np.abs(row["eigenvalues"].imag))),
                "reference_active_delta": float(active.radial_block_discriminant.iloc[i]),
                "reference_static_mass": float(static.reference_static_mass.iloc[i]),
                "reference_f": float(control["f"][i]), "candidate_f": float(solution["f"][i]),
                "candidate_mass": float(solution["mass"][i]), "mass_increment": float(solution["mass_increment"][i]),
                "candidate_lapse": float(solution["lapse"][i]), "reference_lapse": float(static.alpha.iloc[i]),
                "required_mass_time_derivative": float(solution["mass_time_derivative"][i]),
                "static_lapse_quadrature_error": float(control["lapse"][i]-static.alpha.iloc[i]),
                "handoff_window": float(parts["window"][i]),
                "released_string_density": float(parts["released_string_density"][i]),
                "transfer_density": float(parts["transfer_density"][i]),
                "reservoir_weight": float(parts["reservoir_weight"][i]),
                "background_enthalpy": float(bg[i, 0]+bg[i, 1]),
            })
            if not row["full_eigensystem_certified"]:
                raise ArithmeticError("uncertified prescribed-source eigensystem")
            records.append(row)
            component_arrays.append(np.array([radial_tensor(*parts[k][i]) for k in
                ["infrastructure", "endpoint", "reservoir", "outgoing", "incoming"]]))
        selected = records[-len(radius):]
        worst = min(selected, key=lambda row: row["radial_block_discriminant"])
        first_bad = np.flatnonzero(solution["f"] <= 0)
        summary.append({"s": s, "level": int(level), "points": len(radius),
            "type_iv": sum(row["stress_algebraic_type"] == TYPE_IV for row in selected),
            "min_source_delta": float(worst["radial_block_discriminant"]), "min_delta_l": worst["l"],
            "min_candidate_f": float(np.min(solution["f"])), "min_reference_f": float(np.min(control["f"])),
            "stationary_areal_domain": solution["stationary_areal_domain"],
            "first_nonpositive_f_l": float(static.l.iloc[first_bad[0]]) if len(first_bad) else np.nan,
            "outer_mass_change": float(solution["mass_increment"][-1]),
            "max_static_lapse_quadrature_error": float(np.max(np.abs(control["lapse"]-static.alpha.to_numpy()))),
            "endpoint_stored_coordinate_energy": float(np.trapezoid(4*np.pi*radius**2*parts["endpoint"][:, 0], radius)),
            "reservoir_stored_coordinate_energy": float(np.trapezoid(4*np.pi*radius**2*parts["reservoir"][:, 0], radius)),
        })
    frame = save_records(records, args.output, "prescribed_source")
    np.savez_compressed(args.output / "component_tensors.npz", tensor=np.array(component_arrays),
        row_index=np.arange(len(records)), components=np.array(["infrastructure", "endpoint", "reservoir", "outgoing", "incoming"]))
    table = pd.DataFrame(summary)
    table.to_csv(args.output / "constraint_summary.csv", index=False)
    return frame, table


def plots(output, frame, reset):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    group = frame[np.isclose(frame.s, reset) & (frame.level == 2)].sort_values("l")
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), constrained_layout=True)
    axes[0].plot(group.l, group.reference_active_delta, label="reference geometry demand")
    axes[0].plot(group.l, group.radial_block_discriminant, label="prescribed total source")
    axes[0].set_yscale("symlog", linthresh=1e-5)
    axes[0].set(xlabel="ell", ylabel="radial discriminant", title="Source closure condition")
    axes[1].plot(group.l, group.reference_f, label="static reference")
    axes[1].plot(group.l, group.candidate_f, label="Einstein mass response")
    axes[1].set(xlabel="ell", ylabel="1 − 2m/r", title="Stationary material domain")
    axes[2].plot(group.l, group.background_enthalpy, label="background rho + p_r")
    axes[2].plot(group.l, group.rho+group.p_l, label="total rho + p_r")
    axes[2].plot(group.l, 2*group.j_l.abs(), "--", label="2 |current|")
    axes[2].plot(group.l, -2*group.j_l.abs(), "--", color="gray")
    axes[2].set(xlabel="ell", ylabel="orthonormal source channel", title="Current and radial stress balance")
    for axis in axes:
        axis.axhline(0, color="black", lw=.7)
        axis.grid(alpha=.2)
        axis.legend(fontsize=7)
    fig.savefig(output / "coupled_reset_constraints.png", dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_reports/data/le_coupled_reset_source")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("positive worker count required")
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    reference_path = ROOT / "supporting_reports/data/le_geometry_boundary/manifest.json"
    manifest = json.loads(reference_path.read_text())
    parameters = manifest["params"]
    p = SourceParams(**parameters)
    source = ROOT / "toolkit/adm_harness_cli/adm_harness/source_ledger.py"
    if sha256_file(source) != manifest["source_manifests"]["dense"]["source_ledger_module_sha256"]:
        raise ValueError("frozen source kernel has changed")
    start, release_end = release_beta_interval(p)
    phases = [start, release_end, manifest["phases"]["worst_dec"],
        release_end+p.support_edge_receiver_post_release_widths*p.w_beta,
        manifest["phases"]["reset_decompression"],
        release_end+(p.support_edge_receiver_post_release_widths+2)*p.w_beta,
        p.q_t0+p.q_Tr, 5., 15.]
    features = [-1.8, -.98127772623317, -.875, -.98984375, -1.67890625, -1.79375]
    tasks = []
    for s in phases:
        for level in range(3):
            ell = np.unique(np.r_[np.linspace(-6., -.5, 128*2**level+1), features])
            for l in ell:
                tasks.append({"s": float(s), "l": float(l), "level": level, "h_l": .00125/2**level})
    reference = sample_reference(tasks, args, parameters)
    spec = ResetSourceSpec()
    frame, summary = evaluate_candidate(reference, args, spec)
    plots(args.output, frame, manifest["phases"]["reset_decompression"])
    source_failed = bool((summary.type_iv > 0).any())
    metric_failed = bool((~summary.stationary_areal_domain).any())
    metadata = {"completed_utc": datetime.now(timezone.utc).isoformat(), "elapsed_seconds": time.monotonic()-started,
        "workers": args.workers, "params": parameters, "source_spec": asdict(spec), "phases": phases,
        "reference_curvature_evaluations": len(reference), "candidate_source_evaluations": len(frame),
        "source_type_iv_failure": source_failed, "stationary_areal_metric_failure": metric_failed,
        "status": "rejected_before_evolution" if source_failed or metric_failed else "requires_spacetime_compatibility_solve",
        "full_spacetime_evolution_performed": False,
        "scope": "one explicit source candidate and its necessary radial Einstein constraints; source and geometric tensors are distinguished",
        "source_kernel_sha256": sha256_file(source), "reference_manifest_sha256": sha256_file(reference_path),
        "software_sha256": {str(path.relative_to(ROOT)): sha256_file(path) for path in [Path(__file__).resolve(),
            ROOT / "toolkit/adm_harness_cli/adm_harness/coupled_reset_constraints.py",
            ROOT / "toolkit/adm_harness_cli/adm_harness/metric_regularity.py",
            ROOT / "toolkit/adm_harness_cli/adm_harness/geometry_boundary.py",
            ROOT / "toolkit/adm_harness_cli/adm_harness/radial_stress.py"]},
        "output_bytes_before_manifest": sum(path.stat().st_size for path in args.output.iterdir() if path.is_file())}
    (args.output / "manifest.json").write_text(json.dumps(metadata, indent=2)+"\n")
    print(json.dumps({k: metadata[k] for k in ["elapsed_seconds", "reference_curvature_evaluations",
        "candidate_source_evaluations", "status", "source_type_iv_failure", "stationary_areal_metric_failure",
        "output_bytes_before_manifest"]}), flush=True)


if __name__ == "__main__":
    main()
