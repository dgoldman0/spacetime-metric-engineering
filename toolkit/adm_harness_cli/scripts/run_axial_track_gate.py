#!/usr/bin/env python3
"""Evaluate the axial track, the constant-radius service metric in a tube of one flat space; emit data only.

The (sigma, z) jets of the service fields are computed once per reset
schedule. Each wall design then evaluates the core and 96 composite
Gauss-Legendre wall radii at every (sigma, z) sample: Hawking-Ellis type,
Eulerian-normalized minimum null energy, Eulerian energy per coordinate length
and radial null crossing integrals, together with an exterior vacuum check.
Attribution cases keep one or two of the fields log alpha, log A and beta in
the core and set the others flat, and a refinement case halves the jet step.
Narrative interpretation is maintained manually in supporting_reports.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from adm_harness import axial_track as ax
from adm_harness.source_ledger import live_packet_mask, sha256_file
from run_reset_schedule_options import VARIANTS as SCHEDULE_VARIANTS

ROOT = Path(__file__).resolve().parents[3]
KEYS = ("v", "s", "z", "ss", "sz", "zz")
SCHEDULES = ("current", "trailing_front", "trailing_front_quarter_rate", "after_live_window_quarter_rate")
STRING_CURVATURE = 1/1.75**2
WALLS = {
    "base": {},
    "wall_0p5": {"wall_width": .5},
    "wall_2": {"wall_width": 2.},
    "wall_4": {"wall_width": 4.},
    "wall_4_log": {"wall_width": 4., "wall_spacing": "logarithmic"},
    "wall_16_log": {"wall_width": 16., "wall_spacing": "logarithmic"},
    "core_1": {"core_radius": 1.},
    "core_3": {"core_radius": 3.},
    "string_core": {"string_curvature": STRING_CURVATURE},
}
JET_STEP = .0025
NOISE_FLOOR = 1e-8
FIELDS = {"all": (0, 1, 2), "lapse_only": (0,), "stretch_only": (1,), "shift_only": (2,), "lapse_and_stretch": (0, 1)}
CASES = {f"current__{wall}": ("current", wall, JET_STEP, "all") for wall in WALLS}
CASES.update({f"{schedule}__base": (schedule, "base", JET_STEP, "all") for schedule in SCHEDULES[1:]})
CASES["trailing_front_quarter_rate__string_core"] = ("trailing_front_quarter_rate", "string_core", JET_STEP, "all")
CASES["current__base__half_jet_step"] = ("current", "base", JET_STEP/2, "all")
CASES.update({f"current__base__{fields}": ("current", "base", JET_STEP, fields) for fields in FIELDS if fields != "all"})
REFERENCE_POINTS = {"static_support": (-1.5, 0.), "catch": (0., 0.), "reset": (1.6, 1.)}


def design_for(case: str) -> ax.AxialTrackDesign:
    schedule, wall, step, _ = CASES[case]
    return ax.AxialTrackDesign(track=SCHEDULE_VARIANTS[schedule][1], jet_step=step, **WALLS[wall])


def jets_row(task):
    schedule, step, s, z_axis = task
    params, track = SCHEDULE_VARIANTS[schedule]
    design = ax.AxialTrackDesign(track=track, jet_step=step)
    out = np.empty((len(z_axis), 3, len(KEYS)))
    for index, z in enumerate(z_axis):
        jet = ax.service_jet(s, z, params, design)
        out[index] = np.stack([jet[key] for key in KEYS], axis=1)
    return schedule, step, s, out


def core_area(design: ax.AxialTrackDesign) -> float:
    if design.string_curvature == 0:
        return math.pi*design.core_radius**2
    k = math.sqrt(design.string_curvature)
    return 2*math.pi*(1-math.cos(k*design.core_radius))/design.string_curvature


def evaluate_point(jet, design, radius, weights):
    """Core, wall and exterior diagnostics at one (sigma, z) for a wall design."""
    value = ax.transverse_profile(radius, design)[0]
    area = weights*2*math.pi*value
    chi = ax.wall_blend(radius, design)[0]
    alpha, stretch = np.exp(chi*jet["v"][0]), np.exp(chi*jet["v"][1])
    core = ax.frame_tensor(jet, [0.], design)
    wall = ax.frame_tensor(jet, radius, design)
    exterior = ax.frame_tensor(jet, [design.outer_radius+.5], design)
    kinds = ax.classify(np.concatenate([core, wall]), floor=NOISE_FLOOR)
    null = ax.min_null_energy(np.concatenate([core, wall]))
    core_null, wall_null = null[0], null[1:]
    wall_types = kinds["type"][1:]
    crossing = [wall[:, 0, 0]+sign*2*wall[:, 0, 2]+wall[:, 2, 2] for sign in (1, -1)]
    deficit = np.maximum(-wall_null, 0)
    type_i = wall_types == ax.TYPE_I
    wall_margin = kinds["type_margin"][1:]
    near_boundary = (wall_types != ax.VACUUM) & (np.abs(wall_margin) < 1e-3)
    opposite = (crossing[0] < 0) != (crossing[1] < 0)
    iv = wall_types == ax.TYPE_IV
    return {
        "service_curvature": -ax.EIGHT_PI*core[0, 2, 2], "log_alpha_core": jet["v"][0], "log_a_core": jet["v"][1],
        "beta_core": jet["v"][2], "log_alpha_rate": jet["s"][0], "log_a_rate": jet["s"][1], "beta_rate": jet["s"][2],
        "core_type": kinds["type"][0], "core_certified": bool(kinds["certified"][0]),
        "core_min_null": core_null, "core_energy_density": core[0, 0, 0],
        "wall_min_null": float(wall_null.min()), "wall_min_null_radius": float(radius[np.argmin(wall_null)]),
        "wall_type_i": int(type_i.sum()), "wall_type_iv": int((wall_types == ax.TYPE_IV).sum()),
        "wall_type_ii_iii": int((wall_types == ax.TYPE_II_III).sum()),
        "wall_vacuum": int((wall_types == ax.VACUUM).sum()),
        "wall_unresolved": int((wall_types == ax.UNRESOLVED).sum()),
        "wall_uncertified": int((~kinds["certified"][1:]).sum()),
        "wall_near_type_boundary": int(near_boundary.sum()),
        "wall_min_type_i_margin": float(wall_margin[type_i].min()) if type_i.any() else math.nan,
        "wall_max_type_iv_margin": float(wall_margin[iv].max()) if iv.any() else math.nan,
        "wall_opposite_radial_null": int(opposite.sum()),
        "wall_type_iv_inner_radius": float(radius[iv].min()) if iv.any() else math.nan,
        "wall_type_iv_outer_radius": float(radius[iv].max()) if iv.any() else math.nan,
        "wall_negative_fraction": float(np.sum(area*(wall_null < -1e-12))/np.sum(area)),
        "wall_negative_null": float(np.sum(area*deficit)),
        "wall_negative_null_proper": float(np.sum(area*deficit*alpha*stretch)),
        "core_negative_null": core_area(design)*max(-core_null, 0.),
        "core_negative_null_proper": core_area(design)*max(-core_null, 0.)*math.exp(jet["v"][0]+jet["v"][1]),
        "wall_line_energy": float(np.sum(area*wall[:, 0, 0]*stretch)),
        "core_line_energy": core_area(design)*core[0, 0, 0]*math.exp(jet["v"][1]),
        "radial_crossing": float(min(np.sum(weights*c) for c in crossing)),
        "radial_crossing_anec": float(min(np.sum(weights*c/alpha) for c in crossing)),
        "exterior_max_abs": float(np.max(np.abs(exterior))),
    }


def wall_row(task):
    case, s, z_axis, jets = task
    design = design_for(case)
    params = SCHEDULE_VARIANTS[CASES[case][0]][0]
    radius, weights = ax.wall_nodes(design)
    kept = np.zeros(3)
    kept[list(FIELDS[CASES[case][3]])] = 1.
    rows = []
    for z, array in zip(z_axis, jets):
        jet = {key: array[:, index]*kept for index, key in enumerate(KEYS)}
        rows.append({"case": case, "s": s, "z": z, "live": bool(live_packet_mask(s, z, params)),
                     **evaluate_point(jet, design, radius, weights)})
    return rows


def radial_profile(case, s, z, jet):
    design = design_for(case)
    radius = np.linspace(0., design.outer_radius+.5, 601)
    tensor = ax.frame_tensor(jet, radius, design)
    kinds = ax.classify(tensor, floor=NOISE_FLOOR)
    chi = ax.wall_blend(radius, design)[0]
    return pd.DataFrame({
        "case": case, "s": s, "z": z, "r": radius, "chi": chi, "rho": tensor[:, 0, 0], "p_z": tensor[:, 1, 1],
        "p_r": tensor[:, 2, 2], "p_phi": tensor[:, 3, 3], "flux_nz": tensor[:, 0, 1], "flux_nr": tensor[:, 0, 2],
        "shear_zr": tensor[:, 1, 2], "min_null": ax.min_null_energy(tensor), "type": kinds["type"],
        "alpha": np.exp(chi*jet["v"][0]), "stretch": np.exp(chi*jet["v"][1])})


def summarize(frame, case, step):
    design = design_for(case)
    wall_nodes = len(ax.wall_nodes(design)[0])
    worst = frame.loc[frame.wall_min_null.idxmin()]
    core_worst = frame.loc[frame.core_min_null.idxmin()]
    s_ref, z_ref = REFERENCE_POINTS["static_support"]
    nearest = frame.loc[((frame.s-s_ref)**2+(frame.z-z_ref)**2).idxmin()]
    static = frame[(frame.s == nearest.s) & (frame.z == nearest.z)]
    cell = step*step
    return {
        "case": case, "schedule": CASES[case][0], "wall": CASES[case][1], "fields": CASES[case][3],
        "jet_step": design.jet_step,
        "core_radius": design.core_radius,
        "wall_width": design.wall_width, "wall_spacing": design.wall_spacing,
        "string_curvature": design.string_curvature, "deficit_angle": ax.deficit_angle(design),
        "samples": len(frame), "wall_points": len(frame)*wall_nodes,
        "core_type_i": int((frame.core_type == ax.TYPE_I).sum()), "core_vacuum": int((frame.core_type == ax.VACUUM).sum()),
        "wall_type_i": int(frame.wall_type_i.sum()), "wall_type_iv": int(frame.wall_type_iv.sum()),
        "wall_type_ii_iii": int(frame.wall_type_ii_iii.sum()), "wall_vacuum": int(frame.wall_vacuum.sum()),
        "wall_unresolved": int(frame.wall_unresolved.sum()), "wall_uncertified": int(frame.wall_uncertified.sum()),
        "wall_near_type_boundary": int(frame.wall_near_type_boundary.sum()),
        "wall_min_type_i_margin": float(frame.wall_min_type_i_margin.min()),
        "wall_max_type_iv_margin": float(frame.wall_max_type_iv_margin.max()),
        "wall_opposite_radial_null": int(frame.wall_opposite_radial_null.sum()),
        "samples_with_wall_type_iv": int((frame.wall_type_iv > 0).sum()),
        "live_samples_with_wall_type_iv": int(((frame.wall_type_iv > 0) & frame.live).sum()),
        "exterior_max_abs": float(frame.exterior_max_abs.max()),
        "core_min_null": float(core_worst.core_min_null), "core_min_null_s": float(core_worst.s),
        "core_min_null_z": float(core_worst.z),
        "wall_min_null": float(worst.wall_min_null), "wall_min_null_s": float(worst.s),
        "wall_min_null_z": float(worst.z), "wall_min_null_r": float(worst.wall_min_null_radius),
        "live_wall_min_null": float(frame[frame.live].wall_min_null.min()),
        "core_negative_null_integral": float(frame.core_negative_null.sum()*cell),
        "wall_negative_null_integral": float(frame.wall_negative_null.sum()*cell),
        "core_negative_null_proper_integral": float(frame.core_negative_null_proper.sum()*cell),
        "wall_negative_null_proper_integral": float(frame.wall_negative_null_proper.sum()*cell),
        "min_wall_line_energy": float(frame.wall_line_energy.min()),
        "min_radial_crossing": float(frame.radial_crossing.min()),
        "min_radial_crossing_anec": float(frame.radial_crossing_anec.min()),
        "static_wall_min_null": float(static.wall_min_null.iloc[0]),
        "static_wall_line_energy": float(static.wall_line_energy.iloc[0]),
        "static_core_line_energy": float(static.core_line_energy.iloc[0]),
        "static_radial_crossing_anec": float(static.radial_crossing_anec.iloc[0]),
        "static_wall_negative_fraction": float(static.wall_negative_fraction.iloc[0]),
    }


def figures(samples, profiles, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    base = samples[samples.case == "current__base"]
    grid = base.pivot(index="z", columns="s", values="wall_min_null")
    fig, ax_map = plt.subplots(figsize=(8, 4.2))
    limit = float(np.nanmax(np.abs(grid.values)))
    mesh = ax_map.pcolormesh(grid.columns, grid.index, grid.values, cmap="RdBu", vmin=-limit, vmax=limit,
                             shading="nearest")
    fig.colorbar(mesh, label="minimum null energy in the wall")
    ax_map.set_xlabel("sigma")
    ax_map.set_ylabel("z")
    ax_map.set_xlim(-1.5, 8)
    fig.tight_layout()
    fig.savefig(output/"wall_min_null_map_base.png", dpi=140)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for axis, case in zip(axes, ("current__base", "current__string_core")):
        profile = profiles[(profiles.case == case) & (profiles.s == profiles.s.min())]
        for label, values in (("rho + p_z", profile.rho+profile.p_z), ("rho + p_r", profile.rho+profile.p_r),
                              ("rho + p_phi", profile.rho+profile.p_phi), ("rho", profile.rho),
                              ("min null", profile.min_null)):
            axis.plot(profile.r, values, label=label)
        axis.axhline(0, color="k", lw=.6)
        axis.set_title(case.replace("current__", "")+" at sigma=-1.5, z=0")
        axis.set_xlabel("r")
    axes[0].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output/"static_wall_profiles.png", dpi=140)
    plt.close(fig)
    cases = (("current__base", "all fields"), ("current__base__shift_only", "shift only"),
             ("current__base__stretch_only", "stretch only"), ("current__base__lapse_only", "lapse only"))
    fig, axes = plt.subplots(1, 4, figsize=(16, 3.8), sharey=True)
    for axis, (case, title) in zip(axes, cases):
        frame = samples[samples.case == case]
        share = frame.wall_type_iv/np.maximum(frame.wall_type_i+frame.wall_type_iv+frame.wall_type_ii_iii, 1)
        grid = frame.assign(share=share).pivot(index="z", columns="s", values="share")
        mesh = axis.pcolormesh(grid.columns, grid.index, grid.values, cmap="magma_r", vmin=0, vmax=1, shading="nearest")
        axis.set_xlim(-1.5, 8)
        axis.set_title(title)
        axis.set_xlabel("sigma")
    axes[0].set_ylabel("z")
    fig.colorbar(mesh, ax=axes, label="Type IV share of non-vacuum wall nodes")
    fig.savefig(output/"wall_type_iv_attribution.png", dpi=140, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--step", type=float, default=.1)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/axial_track_gate")
    parser.add_argument("--figures-only", action="store_true", help="redraw figures from the recorded samples")
    args = parser.parse_args()
    if args.figures_only:
        figures(pd.read_csv(args.output/"samples.csv.gz"), pd.read_csv(args.output/"radial_profiles.csv.gz"),
                args.output)
        return
    started = time.time()
    args.output.mkdir(parents=True, exist_ok=True)
    s_axis = np.round(np.arange(-1.5, 20.+args.step/2, args.step), 10)
    z_axis = np.round(np.arange(-4.9, 4.9+args.step/2, args.step), 10)
    jets = {}
    sources = sorted({(schedule, step) for schedule, _, step, _ in CASES.values()})
    with ProcessPoolExecutor(args.workers) as pool:
        for schedule, step, s, array in pool.map(jets_row, [(name, step, float(s), z_axis) for name, step in sources
                                                            for s in s_axis]):
            jets[(schedule, step, s)] = array
    print("jets", round(time.time()-started, 1), flush=True)
    rows = []
    with ProcessPoolExecutor(args.workers) as pool:
        tasks = [(case, float(s), z_axis, jets[(CASES[case][0], CASES[case][2], float(s))]) for case in CASES
                 for s in s_axis]
        for chunk in pool.map(wall_row, tasks, chunksize=4):
            rows.extend(chunk)
    samples = pd.DataFrame(rows)
    print("walls", round(time.time()-started, 1), flush=True)
    samples.to_csv(args.output/"samples.csv.gz", index=False, compression={"method": "gzip", "mtime": 0},
                   float_format="%.7g")
    profiles = []
    for case in CASES:
        frame = samples[samples.case == case]
        worst = frame.loc[frame.wall_min_null.idxmin()]
        points = dict(REFERENCE_POINTS, worst=(float(worst.s), float(worst.z)))
        for s, z in points.values():
            s, z = float(s_axis[np.argmin(np.abs(s_axis-s))]), float(z_axis[np.argmin(np.abs(z_axis-z))])
            array = jets[(CASES[case][0], CASES[case][2], s)][int(np.argmin(np.abs(z_axis-z)))]
            kept = np.zeros(3)
            kept[list(FIELDS[CASES[case][3]])] = 1.
            jet = {key: array[:, index]*kept for index, key in enumerate(KEYS)}
            profiles.append(radial_profile(case, float(s), float(z), jet))
    profiles = pd.concat(profiles)
    profiles.to_csv(args.output/"radial_profiles.csv.gz", index=False, compression={"method": "gzip", "mtime": 0},
                    float_format="%.7g")
    summary = pd.DataFrame([summarize(samples[samples.case == case], case, args.step) for case in CASES])
    summary.to_csv(args.output/"summary.csv", index=False)
    figures(samples, profiles, args.output)
    manifest = {
        "completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time()-started, 1), "workers": args.workers, "step": args.step,
        "s_range": [float(s_axis[0]), float(s_axis[-1])], "z_range": [float(z_axis[0]), float(z_axis[-1])],
        "wall_nodes": len(ax.wall_nodes(ax.AxialTrackDesign())[0]), "reference_points": REFERENCE_POINTS,
        "noise_floor": NOISE_FLOOR,
        "cases": {case: {"schedule": schedule, "wall": wall, "fields": fields,
                         "design": {k: v for k, v in asdict(design_for(case)).items() if k != "track"}}
                  for case, (schedule, wall, _, fields) in CASES.items()},
        "software_sha256": {path: sha256_file(ROOT/"toolkit/adm_harness_cli"/path) for path in (
            "adm_harness/axial_track.py", "adm_harness/axial_einstein_generated.py",
            "adm_harness/constant_radius_track.py", "scripts/run_axial_track_gate.py",
            "scripts/derive_axial_track_einstein.py", "scripts/run_reset_schedule_options.py")},
    }
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=1, default=str)+"\n")
    pd.set_option("display.width", 250)
    print(summary.T.to_string())


if __name__ == "__main__":
    main()
