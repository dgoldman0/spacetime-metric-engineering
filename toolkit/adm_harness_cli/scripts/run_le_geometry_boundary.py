#!/usr/bin/env python3
"""Reproducible geometry-demand boundary diagnostic; emit data and figures.

Narrative interpretation is maintained manually in supporting_reports.
Independent curvature samples run in separate processes with bounded batches.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone
import json
import multiprocessing
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adm_harness.geometry_boundary import evaluate_demand, metric_scalars
from adm_harness.radial_stress import TYPE_I, TYPE_IV, certify_radial_eigensystem, radial_tensor
from adm_harness.source_ledger import SourceParams, sha256_file

ROOT = Path(__file__).resolve().parents[3]
RUNS = ROOT / "toolkit/adm_harness_cli/runs"
SURFACES = {
    "baseline": "beta_collar_generator_beta075_p003_mid_s15",
    "dense": "beta_collar_generator_beta075_p003_mid_dense377x241_sharded12",
}
CHANNELS = ["rho_euler", "p_l_unit", "j_l_unit", "p_omega_unit"]
WINDOWS = ["W_raw", "support_shell_window", "support_edge_receiver_radial_cap_window",
           "support_edge_receiver_angular_flange_window", "standing_support_packet_beta_rematch_window"]
ARRAY_FIELDS = ["eigenvalues", "eigenvectors", "eigenvector_metric_norms", "tensor_orthonormal",
                "raw_tensor_orthonormal", "raw_eigenvalues"]
PARAMS = None


def load_surface(name):
    directory = RUNS / SURFACES[name] / "ledgers/rematch_w6_t1p5"
    path = directory / "source_ledger_manifest.json"
    manifest = json.loads(path.read_text())
    ledger = directory / "source_ledger_point_ledger.csv"
    if sha256_file(ledger) != manifest["point_ledger_sha256"]:
        raise ValueError(f"source ledger hash mismatch: {name}")
    module = ROOT / "toolkit/adm_harness_cli/adm_harness/source_ledger.py"
    if sha256_file(module) != manifest["source_ledger_module_sha256"]:
        raise ValueError("frozen source module hash mismatch")
    frame = pd.read_csv(ledger, usecols=["s", "l", "stage", "region", "gamma_ll", "gamma_omega"]+CHANNELS+WINDOWS)
    return manifest, frame.sort_values(["s", "l"]).reset_index(drop=True)


def save_records(records, output, name):
    arrays = {k: np.stack([r[k] for r in records]) for k in ARRAY_FIELDS if k in records[0]}
    frame = pd.DataFrame([{k: v for k, v in r.items() if k not in ARRAY_FIELDS} for r in records])
    arrays["s"] = frame.s.to_numpy()
    arrays["l"] = frame.l.to_numpy()
    arrays["row_index"] = np.arange(len(frame))
    np.savez_compressed(output / f"{name}_eigensystems.npz", **arrays)
    frame.to_csv(output / f"{name}.csv.gz", index=False, compression={"method": "gzip", "mtime": 0})
    return frame


def extrema(frame):
    index = frame.radial_block_discriminant.idxmin()
    worst = frame.loc[index]
    return {
        "points": len(frame), "type_i": int((frame.stress_algebraic_type == TYPE_I).sum()),
        "type_iv": int((frame.stress_algebraic_type == TYPE_IV).sum()),
        "other_type": int((~frame.stress_algebraic_type.isin([TYPE_I, TYPE_IV])).sum()),
        "uncertified": int((~frame.full_eigensystem_certified).sum()),
        "min_delta": float(worst.radial_block_discriminant), "min_delta_s": float(worst.s), "min_delta_l": float(worst.l),
        "min_nec_type_i": frame.nec_margin.min(), "min_wec_type_i": frame.wec_margin.min(),
        "min_dec_type_i": frame.dec_margin.min(), "max_abs_p_omega": frame.p_omega.abs().max(),
        "max_abs_j_l": frame.j_l.abs().max(), "max_imaginary_eigenvalue": frame.imaginary_eigenvalue_scale.max(),
        "max_eigen_equation_error": frame.eigen_equation_relative_error.max(),
    }


def stored_map(frame, output, name):
    records = []
    for row in frame.itertuples(index=False):
        tensor = radial_tensor(*[getattr(row, key) for key in CHANNELS])
        result = certify_radial_eigensystem(tensor)
        result.update({"s": row.s, "l": row.l, "stage": row.stage, "region": row.region,
                       "rho": row.rho_euler, "p_l": row.p_l_unit, "j_l": row.j_l_unit, "p_omega": row.p_omega_unit,
                       "tensor_orthonormal": tensor,
                       "imaginary_eigenvalue_scale": float(np.max(np.abs(result["eigenvalues"].imag)))})
        records.append(result)
    result = save_records(records, output, f"stored_{name}")
    tables = [{"surface": name, "group": "all", **extrema(result)}]
    for key in ["stage", "region"]:
        tables += [{"surface": name, "group": key+":"+str(label), **extrema(group)} for label, group in result.groupby(key)]
    return result, tables


def interface_tables(source, diagnostic, output):
    """Geometry-window transitions, with each time slice normalized separately.

    These masks identify metric tapers. Physical component tensors remain a
    separate assembly question. Masks may overlap; they partition no material.
    """
    summaries, landmarks = [], []
    for window in WINDOWS:
        masks = np.zeros(len(source), dtype=bool)
        slopes = np.zeros(len(source))
        peak_global = float(source[window].abs().max())
        for sigma, group in source.groupby("s", sort=False):
            values = group[window].to_numpy()
            peak = float(np.max(np.abs(values)))
            if peak <= max(1e-10, 1e-6*peak_global):
                continue
            ell = group.l.to_numpy()
            derivative = np.abs(np.gradient(values, ell))
            normalized = np.abs(values)/peak
            masks[group.index] = ((normalized >= .001) & (normalized <= .999)) | (derivative > .05*derivative.max())
            slopes[group.index] = derivative
            for a in range(len(ell)-1):
                for fraction in [.9, .5, .1]:
                    if (normalized[a]-fraction)*(normalized[a+1]-fraction) < 0:
                        crossing = ell[a]+(ell[a+1]-ell[a])*(fraction-normalized[a])/(normalized[a+1]-normalized[a])
                        landmarks.append({"window": window, "s": sigma, "fraction": fraction, "l": crossing,
                                          "direction": "falling" if normalized[a+1] < normalized[a] else "rising", "slice_peak": peak})
        group = diagnostic.loc[masks]
        if len(group):
            peak_index = int(np.argmax(slopes))
            summaries.append({"window": window, **extrema(group), "max_abs_dwindow_dl": slopes.max(),
                              "gradient_peak_s": source.loc[peak_index, "s"], "gradient_peak_l": source.loc[peak_index, "l"]})
    pd.DataFrame(summaries).to_csv(output / "geometry_interface_summary.csv", index=False)
    pd.DataFrame(landmarks).to_csv(output / "geometry_interface_landmarks.csv.gz", index=False,
                                compression={"method": "gzip", "mtime": 0})


def init_worker(parameters):
    global PARAMS
    PARAMS = SourceParams(**parameters)


def sample_batch(tasks):
    records = []
    for task in tasks:
        params = replace(PARAMS, w_th=PARAMS.w_th*task["width_factor"])
        result = evaluate_demand(task["s"], task["l"], params, task["h"], task["h"],
                                 holding=task["holding"], h_theta=task.get("h_theta", 1e-4))
        result.update(task)
        fields = metric_scalars(task["s"], task["l"], params)
        result.update({k: fields[k] for k in WINDOWS})
        magnitude = max(abs(result["rho"]), abs(result["p_l"]), abs(result["j_l"]), abs(result["p_omega"]))
        result["transverse_to_density"] = abs(result["p_omega"])/max(abs(result["rho"]), 1e-12*magnitude, np.finfo(float).tiny)
        records.append(result)
    return records


def run_samples(tasks, parameters, workers, output, name):
    start = time.monotonic()
    records = []
    batches = [tasks[i:i+32] for i in range(0, len(tasks), 32)]
    last = start
    with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("spawn"),
                             initializer=init_worker, initargs=(parameters,)) as executor:
        for batch in executor.map(sample_batch, batches):
            records.extend(batch)
            now = time.monotonic()
            if now-last > 20:
                print(f"{name}: {len(records)}/{len(tasks)} samples, {now-start:.0f} s", flush=True)
                last = now
    frame = save_records(records, output, name)
    print(f"{name}: complete, {len(frame)} samples, {time.monotonic()-start:.1f} s", flush=True)
    return frame


def task(study, s, l, level, holding=False, width_factor=1., **extra):
    return {"study": study, "s": float(s), "l": float(l), "level": level,
            "h": .0025/2**level, "holding": holding, "width_factor": width_factor, **extra}


def profile_burdens(frame, output, name):
    rows = []
    for keys, group in frame.groupby(["study", "width_factor", "s", "level", "holding"], sort=False):
        group = group.sort_values("l")
        ell = group.l.to_numpy()
        proper = np.sqrt(group.gamma_ll.to_numpy())
        volume = 4*np.pi*proper*group.gamma_omega.to_numpy()
        type_iv = (group.stress_algebraic_type == TYPE_IV).to_numpy()
        rows.append(dict(zip(["study", "width_factor", "s", "level", "holding"], keys)) | extrema(group) | {
            "l_min": ell[0], "l_max": ell[-1],
            "source_frame_norm_proper_integral": np.trapezoid(group.source_frame_frobenius*proper, ell),
            "source_frame_norm_volume_integral": np.trapezoid(group.source_frame_frobenius*volume, ell),
            "type_iv_proper_length": np.trapezoid(type_iv*proper, ell),
            "imaginary_eigenvalue_proper_integral": np.trapezoid(group.imaginary_eigenvalue_scale*proper, ell),
            "max_projection_relative_error": group.spherical_projection_relative_error.max(),
            "max_transverse_to_density": group.transverse_to_density.max(),
        })
    pd.DataFrame(rows).to_csv(output / f"{name}_summary.csv", index=False)
    return pd.DataFrame(rows)


def plots(output, dense, profiles, patch, widths):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import SymLogNorm

    plt.rcParams.update({"font.size": 10, "savefig.dpi": 160})
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), constrained_layout=True)
    grid = dense.pivot(index="s", columns="l", values="radial_block_discriminant")
    mesh = axes[0].pcolormesh(grid.columns, grid.index, grid, shading="nearest", cmap="coolwarm",
                               norm=SymLogNorm(linthresh=1e-6, vmin=-.003, vmax=.003))
    fig.colorbar(mesh, ax=axes[0], label="Radial discriminant")
    kinds = (dense.stress_algebraic_type == TYPE_IV).astype(int)
    types = dense.assign(type_iv=kinds).pivot(index="s", columns="l", values="type_iv")
    mesh = axes[1].pcolormesh(types.columns, types.index, types, shading="nearest", cmap="Greys", vmin=0, vmax=1)
    axes[0].set_title("Frozen geometry demand: existing dense grid")
    axes[1].set_title("Type IV = black; stored-channel map, recomputed witnesses below")
    for axis in axes:
        axis.set(xlabel="ell", ylabel="sigma", ylim=(-1.5, 4))
    fig.savefig(output / "demand_maps.png")
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for level, group in patch.groupby("level"):
        at_min = group.loc[group.radial_block_discriminant.idxmin()]
        axes[0].plot(at_min.h, -at_min.radial_block_discriminant, "o", label=f"grid {21*2**level-(2**level-1)} squared")
    witnesses = pd.read_csv(output / "witnesses.csv.gz")
    worst_s = dense.loc[dense.radial_block_discriminant.idxmin(), "s"]
    w = witnesses[(witnesses.s == worst_s) & (~witnesses.holding)].sort_values("h")
    if len(w):
        axes[0].plot(w.h, -w.radial_block_discriminant, "k.-", label="fixed dense-grid witness")
    for holding, group in profiles[(profiles.s == worst_s) & (profiles.level == 2)].groupby("holding"):
        axes[1].plot(group.l, group.radial_block_discriminant, label="static profile" if holding else "active")
    axes[0].set(xscale="log", xlabel="curvature step h", ylabel="minus minimum discriminant", title="Fixed physical geometry convergence")
    axes[1].set(xlabel="ell", ylabel="radial discriminant", xlim=(-3, 3), ylim=(-.0025, .004), title=f"Matched controls at sigma={worst_s:.4f}")
    for axis in axes:
        axis.legend()
        axis.grid(alpha=.2)
    fig.savefig(output / "convergence_and_holding.png")
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for factor, group in widths[(widths.level == 2) & (~widths.holding)].groupby("width_factor"):
        axes[0].plot(group.l, group.radial_block_discriminant, label=f"w_th x {factor:g}")
        axes[1].plot(group.l, group.source_frame_frobenius, label=f"w_th x {factor:g}")
    for axis in axes:
        axis.set(xlabel="ell", xlim=(-3.5, 3.5))
        axis.legend()
        axis.grid(alpha=.2)
    axes[0].set(ylabel="radial discriminant", title="Physical standing-taper sensitivity")
    axes[1].set(ylabel="ADM-frame tensor Frobenius norm", yscale="log")
    fig.savefig(output / "physical_width_sensitivity.png")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_reports/data/le_geometry_boundary")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    map_summaries = []
    manifests = {}
    for name in SURFACES:
        manifest, source = load_surface(name)
        manifests[name] = manifest
        print(f"Certifying stored {name} map ({len(source)} points)", flush=True)
        diagnostic, summary = stored_map(source, output, name)
        map_summaries.extend(summary)
    pd.DataFrame(map_summaries).to_csv(output / "stored_map_summary.csv", index=False)
    if manifests["baseline"]["params"] != manifests["dense"]["params"]:
        raise ValueError("baseline and dense geometries differ")
    parameters = manifests["dense"]["params"]
    dense = diagnostic
    interface_tables(source, dense, output)
    selected = set()
    phases = {}
    for stage, group in dense.groupby("stage", sort=False):
        worst = group.loc[group.radial_block_discriminant.idxmin()]
        selected.add((float(worst.s), float(worst.l)))
        phases[stage] = float(worst.s)
    for _, group in dense.groupby("region"):
        worst = group.loc[group.radial_block_discriminant.idxmin()]
        selected.add((float(worst.s), float(worst.l)))
    worst_dec = dense.loc[dense.dec_margin.idxmin()]
    selected.add((float(worst_dec.s), float(worst_dec.l)))
    phases["worst_dec"] = float(worst_dec.s)
    witnesses = run_samples([task("witness", s, l, level, holding) for s, l in sorted(selected)
                            for level in range(4) for holding in [False, True]], parameters, args.workers, output, "witnesses")
    worst = dense.loc[dense.radial_block_discriminant.idxmin()]
    strong = witnesses[(witnesses.s == worst.s) & (witnesses.l == worst.l) & (~witnesses.holding)].sort_values("level")
    delta = strong.radial_block_discriminant.to_numpy()
    converged_failure = bool(len(delta) == 4 and np.all(delta < 0) and abs(delta[-1]-delta[-2])/abs(delta[-1]) < .005
                             and strong.full_eigensystem_certified.all() and (strong.raw_imaginary_eigenvalue_scale > 0).all())
    tasks = [task("phase_profile", s, l, level, holding, phase=stage) for stage, s in phases.items()
             for level in range(3) for holding in [False, True] for l in np.linspace(-4, 4, 80*2**level+1)]
    profiles = run_samples(tasks, parameters, args.workers, output, "phase_profiles")
    profile_burdens(profiles, output, "phase_profiles")
    tasks = [task("local_patch", s, l, level) for level in range(3)
             for s in np.linspace(worst.s-.2, worst.s+.2, 20*2**level+1)
             for l in np.linspace(worst.l-.2, worst.l+.2, 20*2**level+1)]
    patch = run_samples(tasks, parameters, args.workers, output, "local_patch")
    pd.DataFrame([{"level": level, "h": group.h.iloc[0], **extrema(group)} for level, group in patch.groupby("level")]).to_csv(output / "local_patch_summary.csv", index=False)
    tails = run_samples([task("exterior_tail", 15., sign*l, level, h_theta=theta) for level in range(3)
                         for theta in [1e-4, 5e-5] for sign in [-1, 1] for l in [6., 12., 24., 48., 96.]],
                        parameters, args.workers, output, "exterior_tail")
    a = parameters["Rth"]
    tails["analytic_magnitude"] = a*a/(8*np.pi*(tails.l**2+a*a)**2)
    tails["analytic_channel_max_relative_error"] = np.max(np.abs(tails[["rho", "p_l", "j_l", "p_omega"]].to_numpy()
                 - tails.analytic_magnitude.to_numpy()[:, None]*np.array([-1, -1, 0, 1])), axis=1)/tails.analytic_magnitude
    tails["analytic_both_ends_norm_volume_beyond_L"] = 2*a*np.arctan(a/tails.l.abs())
    tails.to_csv(output / "exterior_tail_analytic_comparison.csv", index=False)
    if not converged_failure:
        raise RuntimeError("Fixed-point failure did not satisfy convergence criterion; review before width sensitivity")
    tasks = [task("physical_width", worst.s, l, level, holding, factor) for factor in [.5, 2.]
             for level in range(3) for holding in [False, True] for l in np.linspace(-4, 4, 80*2**level+1)]
    variants = run_samples(tasks, parameters, args.workers, output, "physical_width_variants")
    nominal = profiles[profiles.s == worst.s].copy()
    nominal["study"] = "physical_width"
    widths = pd.concat([nominal, variants], ignore_index=True)
    profile_burdens(widths, output, "physical_width")
    plots(output, dense, profiles, patch, widths)
    metadata = {
        "completed_utc": datetime.now(timezone.utc).isoformat(), "elapsed_seconds": time.monotonic()-started,
        "workers": args.workers, "params": parameters, "source_manifests": manifests,
        "stored_points": sum(row["points"] for row in map_summaries if row["group"] == "all"),
        "fresh_points": len(witnesses)+len(profiles)+len(patch)+len(tails)+len(variants),
        "fixed_point_type_iv_survives_refinement": converged_failure,
        "phases": phases, "scope": "geometry-demand G/(8*pi), no physical-sector assembly",
        "holding_definition": "At each sigma, freeze lapse and spatial metric through the curvature stencil; set beta to zero.",
        "physical_width_variation": "Multiply w_th only; evaluate all dependent metric fields anew; preserve the frozen nominal source.",
        "stored_map_representation": "Spherical tensor reconstructed from existing orthonormal channels, including original one-sided current projection.",
        "fresh_representation": "Retain raw 4x4 curvature, raw spectrum, symmetric spherical projection, and projection residual; certify projected full mixed tensor.",
        "software_sha256": {str(path.relative_to(ROOT)): sha256_file(path) for path in [Path(__file__).resolve(),
            ROOT / "toolkit/adm_harness_cli/adm_harness/geometry_boundary.py", ROOT / "toolkit/adm_harness_cli/adm_harness/radial_stress.py"]},
    }
    metadata["output_bytes_before_manifest"] = sum(path.stat().st_size for path in output.iterdir() if path.is_file())
    (output / "manifest.json").write_text(json.dumps(metadata, indent=2)+"\n")
    print(json.dumps({key: metadata[key] for key in ["elapsed_seconds", "stored_points", "fresh_points", "fixed_point_type_iv_survives_refinement", "output_bytes_before_manifest"]}), flush=True)


if __name__ == "__main__":
    main()
