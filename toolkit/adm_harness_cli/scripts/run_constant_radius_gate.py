#!/usr/bin/env python3
"""Standing Le-gate evaluation of flat-throat geometry candidates; emit data and figures.

Narrative interpretation is maintained manually in supporting_reports.
Independent curvature samples run in separate worker processes.
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adm_harness.constant_radius_track import ConstantRadiusTrackDesign, track_scalars
from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.metric_regularity import regularized_scalars
from adm_harness.radial_stress import TYPE_I, TYPE_IV
from adm_harness.source_ledger import SourceParams, sha256_file
from adm_harness.warped_product import evaluate_spherical_demand

ROOT = Path(__file__).resolve().parents[3]
LE_DATA = ROOT / "supporting_reports/data/le_geometry_boundary"
REPAIR_DATA = ROOT / "supporting_reports/data/le_metric_c2_repair"
FROZEN_KERNEL_SHA = "c222300ddcbca1c6a2e8f938028485c08a56dff66f1f88c2cec006dd2b600fff"
PARAMS = SourceParams(**json.loads((LE_DATA / "manifest.json").read_text())["params"])
PHASES = json.loads((LE_DATA / "manifest.json").read_text())["phases"]
CANDIDATES = {
    "beta075_repaired_reference": None,
    "constant_radius_repaired_service": ConstantRadiusTrackDesign(smooth_service=False),
    "constant_radius_smooth": ConstantRadiusTrackDesign(),
}
VARIATIONS = {
    "transition_width_0p75": ConstantRadiusTrackDesign(transition_width=.75),
    "transition_width_3p0": ConstantRadiusTrackDesign(transition_width=3.),
    "track_half_length_4p5": ConstantRadiusTrackDesign(service_inner=3.5, track_half_length=4.5),
    "track_half_length_6p0": ConstantRadiusTrackDesign(service_inner=5., track_half_length=6.),
    "track_radius_1p4": ConstantRadiusTrackDesign(track_radius=1.4),
    "track_radius_2p14": ConstantRadiusTrackDesign(track_radius=2.14),
}
DESIGNS = CANDIDATES | VARIATIONS
STEPS = (.0025, .00125, .000625, .0003125)
MAP_FIELDS = ("rho", "p_l", "j_l", "p_omega", "null_energy_outgoing", "null_energy_ingoing",
              "imaginary_eigenvalue_scale", "nec_margin", "wec_margin", "dec_margin")
SOFTWARE = ["adm_harness/constant_radius_track.py", "adm_harness/warped_product.py", "adm_harness/radial_stress.py",
            "adm_harness/geometry_boundary.py", "adm_harness/metric_regularity.py",
            "adm_harness/receiver_regularity.py", "adm_harness/source_ledger.py", "scripts/run_constant_radius_gate.py"]


def evaluator(name):
    design = DESIGNS[name]
    if design is None:
        return regularized_scalars
    return lambda s, l, p: track_scalars(s, l, p, design)


def evaluate(task):
    name, s, l, step, holding, kind = task
    function = evaluate_spherical_demand if kind == "warped" else evaluate_demand
    result = function(s, l, PARAMS, step, step, scalar_evaluator=evaluator(name), holding=holding)
    if kind == "legacy":
        tensor = result["tensor_orthonormal"]
        h, j = tensor[0, 0]+tensor[1, 1], -tensor[0, 1]
        result["null_energy_outgoing"] = h-2*j
        result["null_energy_ingoing"] = h+2*j
    row = {"candidate": name, "s": s, "l": l, "step": step, "holding": holding, "evaluator": kind,
           "type": result["stress_algebraic_type"], "certified": bool(result["full_eigensystem_certified"])}
    row.update({key: float(result[key]) for key in MAP_FIELDS})
    return row


def run_tasks(tasks, workers, chunksize=48):
    with ProcessPoolExecutor(workers) as pool:
        return pd.DataFrame(pool.map(evaluate, tasks, chunksize=chunksize))


def grid(lo, hi, step):
    return np.round(np.arange(lo, hi+step/2, step), 10)


def type_counts(frame):
    return {"points": len(frame), "type_i": int((frame.type == TYPE_I).sum()),
            "type_iv": int((frame.type == TYPE_IV).sum()),
            "other_type": int((~frame.type.isin([TYPE_I, TYPE_IV])).sum()),
            "uncertified": int((~frame.certified).sum())}


def map_summary(frame, cell):
    counts = type_counts(frame)
    product = frame.null_energy_outgoing*frame.null_energy_ingoing
    worst = frame.loc[product.idxmin()]
    angular_nec = frame.rho+frame.p_omega
    radial_null = np.minimum(frame.null_energy_outgoing, frame.null_energy_ingoing)
    at = lambda series: (float(frame.s[series.idxmin()]), float(frame.l[series.idxmin()]))
    return counts | {
        "min_radial_null_at": at(radial_null), "min_angular_null_at": at(angular_nec),
        "max_abs_p_omega_at": at(-frame.p_omega.abs()),
        "min_null_energy_product": float(product.min()), "min_product_s": float(worst.s), "min_product_l": float(worst.l),
        "imaginary_eigenvalue_integral": float(frame.imaginary_eigenvalue_scale.sum()*cell),
        "max_imaginary_eigenvalue": float(frame.imaginary_eigenvalue_scale.max()),
        "min_radial_null_energy": float(radial_null.min()),
        "min_angular_null_energy": float(angular_nec.min()),
        "angular_null_deficit_integral": float(np.maximum(-angular_nec, 0).sum()*cell),
        "min_rho": float(frame.rho.min()), "max_abs_p_omega": float(frame.p_omega.abs().max()),
        "min_dec_type_i": float(frame.dec_margin.min()), "max_abs_j_l": float(frame.j_l.abs().max()),
    }


def save_frame(frame, path):
    frame.to_csv(path, index=False, compression={"method": "gzip", "mtime": 0}, float_format="%.12g")


def save_map(frame, s_axis, l_axis, path):
    shape = (len(s_axis), len(l_axis))
    ordered = frame.sort_values(["s", "l"])
    arrays = {key: ordered[key].to_numpy(np.float32).reshape(shape) for key in MAP_FIELDS}
    arrays["type_code"] = np.select([ordered.type == TYPE_I, ordered.type == TYPE_IV], [0, 1], 2).reshape(shape).astype(np.int8)
    arrays["certified"] = ordered.certified.to_numpy(bool).reshape(shape)
    np.savez_compressed(path, s=s_axis, l=l_axis, **arrays)


def witnesses(design):
    points = pd.read_csv(LE_DATA / "witnesses.csv.gz")[["s", "l"]].drop_duplicates()
    roots = pd.read_csv(REPAIR_DATA / "static_enthalpy_roots.csv")
    roots = roots[roots.level == roots.level.max()].rename(columns={"phase": "s", "root_l": "l"})[["s", "l"]]
    joins = [(s, sign*x) for s in PHASES.values() for sign in (-1, 1)
             for x in (0., design.service_inner, .5*(design.service_inner+design.track_half_length),
                       design.track_half_length, design.track_half_length+.5*design.transition_width,
                       design.track_half_length+design.transition_width)]
    joins = pd.DataFrame(joins, columns=["s", "l"])
    frame = pd.concat([points.assign(family="le_witness"), roots.assign(family="static_enthalpy_root"),
                       joins.assign(family="join")], ignore_index=True)
    return frame.drop_duplicates(["s", "l"]).reset_index(drop=True)


def static_opening(frame):
    """4 pi integral of (R/A) max[-(rho+p_r), 0] dl on a static late slice, with A=1 exterior."""
    late = frame[frame.s == frame.s.max()].sort_values("l")
    radius = np.array([math.sqrt(track_scalars(s, l, PARAMS, CANDIDATES["constant_radius_smooth"])["gamma_omega"])
                       for s, l in zip(late.s, late.l)])
    deficit = np.maximum(-(late.rho+late.p_l).to_numpy(), 0)
    return float(4*math.pi*np.trapezoid(radius*deficit, late.l.to_numpy()))


def figures(maps, reference_name, candidate_name, holding, profile, ladder, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import SymLogNorm

    fig, axes = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
    for column, name in enumerate((reference_name, candidate_name)):
        data = np.load(maps[name])
        extent = [data["l"][0], data["l"][-1], data["s"][0], data["s"][-1]]
        product = data["null_energy_outgoing"]*data["null_energy_ingoing"]
        image = axes[0, column].imshow(product, origin="lower", aspect="auto", extent=extent, cmap="coolwarm_r",
                                       norm=SymLogNorm(1e-9, vmin=-1e-3, vmax=1e-3))
        axes[0, column].set_title(f"{name}: T(k+,k+) T(k-,k-)")
        axes[1, column].imshow(data["type_code"] == 1, origin="lower", aspect="auto", extent=extent, cmap="Greys")
        axes[1, column].set_title(f"{name}: Type IV = black ({int((data['type_code'] == 1).sum())} points)")
        for axis in axes[:, column]:
            axis.set_xlabel("ell")
            axis.set_ylabel("sigma")
    fig.colorbar(image, ax=axes[0, :], label="radial null-energy product")
    fig.savefig(output / "classification_comparison.png", dpi=120)
    plt.close(fig)

    data = np.load(maps[candidate_name])
    extent = [data["l"][0], data["l"][-1], data["s"][0], data["s"][-1]]
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8), constrained_layout=True)
    image = axes[0].imshow(data["p_omega"], origin="lower", aspect="auto", extent=extent, cmap="coolwarm",
                           norm=SymLogNorm(1e-4, vmin=-.3, vmax=.3))
    fig.colorbar(image, ax=axes[0], label="angular pressure")
    axes[0].set_title(f"{candidate_name}: angular pressure")
    margin = data["rho"]+data["p_omega"]
    image = axes[1].imshow(margin, origin="lower", aspect="auto", extent=extent, cmap="coolwarm",
                           norm=SymLogNorm(1e-4, vmin=-.3, vmax=.3))
    fig.colorbar(image, ax=axes[1], label="rho + p_Omega")
    axes[1].set_title(f"{candidate_name}: angular null energy")
    for axis in axes:
        axis.set_xlabel("ell")
        axis.set_ylabel("sigma")
    fig.savefig(output / "angular_channel.png", dpi=120)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5), constrained_layout=True)
    late = profile.sort_values("l")
    axes[0].plot(late.l, late.rho, label="rho")
    axes[0].plot(late.l, late.p_l, label="p_l")
    axes[0].plot(late.l, late.p_omega, label="p_Omega")
    axes[0].plot(late.l, late.null_energy_outgoing, "k--", label="radial null energy")
    axes[0].set_xlabel("ell")
    axes[0].set_title(f"{candidate_name}: static slice sigma={late.s.iloc[0]:g}")
    axes[0].legend()
    track = ladder[(ladder.candidate == candidate_name) & (ladder.evaluator == "legacy")
                  & (ladder.l.abs() < CANDIDATES[candidate_name].track_half_length)]
    for (s, l), group in track.groupby(["s", "l"]):
        group = group.sort_values("step")
        axes[1].loglog(group.step, np.abs(group.rho+group.p_l)+1e-30, color="C0", alpha=.35)
        axes[1].loglog(group.step, np.abs(group.j_l)+1e-30, color="C1", alpha=.35)
    axes[1].loglog(STEPS, 2e-1*np.array(STEPS)**2, "k--", label="step^2")
    axes[1].set_xlabel("derivative step")
    axes[1].set_title("four-dimensional kernel along the track: |rho+p_l| (blue), |j| (orange)")
    axes[1].legend()
    fig.savefig(output / "static_profile_and_body_refinement.png", dpi=120)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--map-step", type=float, default=.025)
    parser.add_argument("--variation-step", type=float, default=.05)
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_reports/data/constant_radius_gate")
    args = parser.parse_args()
    if sha256_file(ROOT / "toolkit/adm_harness_cli/adm_harness/source_ledger.py") != FROZEN_KERNEL_SHA:
        raise ValueError("frozen source kernel hash mismatch")
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    started = time.time()
    summaries, maps = {}, {}

    s_axis, l_axis = grid(-1.5, 4., args.map_step), grid(-8., 8., args.map_step)
    for name in CANDIDATES:
        tasks = [(name, float(s), float(l), .0025, False, "warped") for s in s_axis for l in l_axis]
        frame = run_tasks(tasks, args.workers)
        maps[name] = output / f"map_{name}.npz"
        save_map(frame, s_axis, l_axis, maps[name])
        summaries[f"map/{name}"] = map_summary(frame, args.map_step**2)
        print(name, summaries[f"map/{name}"]["type_iv"], "Type IV", flush=True)

    late_s = [6., 10., 15.]
    late_l = grid(-8., 8., .05)
    late = run_tasks([(name, s, float(l), .0025, False, "warped") for name in CANDIDATES for s in late_s for l in late_l],
                     args.workers)
    save_frame(late, output / "late_static_slices.csv.gz")
    for name, group in late.groupby("candidate"):
        summaries[f"late/{name}"] = type_counts(group) | {
            "max_abs_j_l": float(group.j_l.abs().max()), "min_rho": float(group.rho.min())}
    summaries["late/constant_radius_smooth"]["opening_integral_sigma15"] = static_opening(
        late[late.candidate == "constant_radius_smooth"])

    v_s, v_l = grid(-1.5, 4., args.variation_step), grid(-9., 9., args.variation_step)
    for name in VARIATIONS:
        frame = run_tasks([(name, float(s), float(l), .0025, False, "warped") for s in v_s for l in v_l], args.workers)
        summaries[f"variation/{name}"] = map_summary(frame, args.variation_step**2)
        print(name, summaries[f"variation/{name}"]["type_iv"], "Type IV", flush=True)

    tasks = []
    for name, design in CANDIDATES.items():
        points = witnesses(design or CANDIDATES["constant_radius_smooth"])
        for s, l in zip(points.s, points.l):
            for step in STEPS:
                for kind in ("warped", "legacy"):
                    tasks.append((name, float(s), float(l), step, False, kind))
    ladder = run_tasks(tasks, args.workers, chunksize=8)
    save_frame(ladder, output / "refinement_ladder.csv.gz")
    for (name, kind), group in ladder.groupby(["candidate", "evaluator"]):
        finest = group[group.step == min(STEPS)]
        summaries[f"ladder/{name}/{kind}"] = type_counts(finest) | {
            "max_abs_rho_plus_p_finest": float((finest.rho+finest.p_l).abs().max()),
            "max_abs_j_finest": float(finest.j_l.abs().max())}

    hold_l = grid(-8., 8., args.map_step)
    holding = run_tasks([("constant_radius_smooth", float(s), float(l), .0025, True, "warped")
                         for s in PHASES.values() for l in hold_l], args.workers)
    save_frame(holding, output / "holding_controls.csv.gz")
    summaries["holding/constant_radius_smooth"] = type_counts(holding) | {"max_abs_j_l": float(holding.j_l.abs().max())}

    exterior = run_tasks([("constant_radius_smooth", s, sign*x, .0025, False, kind)
                          for s in (-1.5, .5, 1.9, 4., 15.) for sign in (-1, 1)
                          for x in (6.6, 7., 8., 12., 24., 48., 96.) for kind in ("warped", "legacy")], args.workers, 4)
    save_frame(exterior, output / "exterior_vacuum.csv.gz")
    channels = exterior[["rho", "p_l", "j_l", "p_omega"]].abs().max(axis=1)
    summaries["exterior/constant_radius_smooth"] = type_counts(exterior) | {"max_abs_channel": float(channels.max())}

    pd.DataFrame([{"scope": key, **value} for key, value in summaries.items()]).to_csv(output / "summary.csv", index=False)
    figures(maps, "beta075_repaired_reference", "constant_radius_smooth", holding,
            late[(late.candidate == "constant_radius_smooth") & (late.s == 15.)], ladder, output)
    manifest = {
        "completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time()-started, 1), "workers": args.workers,
        "map_step": args.map_step, "variation_step": args.variation_step, "derivative_steps": STEPS,
        "phases": PHASES, "params": json.loads((LE_DATA / "manifest.json").read_text())["params"],
        "designs": {name: (None if design is None else design.__dict__) for name, design in DESIGNS.items()},
        "frozen_kernel_sha256": FROZEN_KERNEL_SHA,
        "software_sha256": {path: sha256_file(ROOT / "toolkit/adm_harness_cli" / path) for path in SOFTWARE},
        "summaries": summaries,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=1, default=float)+"\n")
    print(json.dumps({k: v.get("type_iv") for k, v in summaries.items()}, indent=1))
    print(f"completed in {manifest['elapsed_seconds']} s")


if __name__ == "__main__":
    main()
