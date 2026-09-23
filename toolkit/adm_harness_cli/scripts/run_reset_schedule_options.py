#!/usr/bin/env python3
"""Compare reset schedules on the constant-radius track; emit data only.

Each variant changes the decompression schedule or the carry choreography of
the C-infinity constant-radius track. The script records the null-energy
budget, packet delivery under the window and velocity-field readings, reset
completion, and the existing service audits on ledgers whose stage, region and
packet labels are regenerated for the variant. Narrative interpretation is
maintained manually in supporting_reports.
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_constant_radius_service_checks as service_checks
from adm_harness.constant_radius_track import ConstantRadiusTrackDesign, service_fields, track_scalars
from adm_harness.radial_stress import TYPE_I
from adm_harness.source_ledger import (
    SourceParams, live_packet_end, live_packet_mask, region_name, sha256_file, stage_name,
)
from adm_harness.warped_product import evaluate_spherical_demand

ROOT = Path(__file__).resolve().parents[3]
BASE = service_checks.PARAMS
CARRY_SHIFTS = (.4, .8, 1.2, 2.2)
FRONT = dict(reset_front_start=-.4, reset_front_speed=1., reset_front_origin=-1.4, reset_front_ramp=.25)


def carried(shift):
    """Move the catch and release choreography later by shift, keeping the carry speed V."""
    return replace(BASE, x_catch_beta=BASE.x_catch_beta+shift, x_catch_packet=BASE.x_catch_packet+shift,
                   x_beta=BASE.x_beta+shift)


def after_live_window(params):
    """Quarter-rate decompression that begins 0.4 after the live window closes."""
    return replace(params, q_t0=live_packet_end(params)+.4, q_Tr=12.)


VARIANTS = {
    "current": (BASE, ConstantRadiusTrackDesign()),
    "after_live_window_quarter_rate": (after_live_window(BASE), ConstantRadiusTrackDesign()),
    "trailing_front": (BASE, ConstantRadiusTrackDesign(**FRONT, reset_front_duration=3.)),
    "trailing_front_half_rate": (BASE, ConstantRadiusTrackDesign(**FRONT, reset_front_duration=6.)),
    "trailing_front_quarter_rate": (BASE, ConstantRadiusTrackDesign(**FRONT, reset_front_duration=12.)),
    **{f"extended_carry_{shift:g}".replace(".", "p"): (after_live_window(carried(shift)), ConstantRadiusTrackDesign())
       for shift in CARRY_SHIFTS},
}


def reset_complete(params, design):
    if design.reset_front is None:
        return params.q_t0+params.q_Tr
    start, speed, origin, duration, ramp = design.reset_front
    return start+(design.track_half_length-origin-ramp/2)/speed+duration


def evaluate(task):
    name, s, l = task
    params, design = VARIANTS[name]
    result = evaluate_spherical_demand(s, l, params, .0025, .0025,
                                       scalar_evaluator=lambda a, b, p: track_scalars(a, b, p, design))
    return {"variant": name, "s": s, "l": l, "type": result["stress_algebraic_type"],
            "certified": bool(result["full_eigensystem_certified"]), "rho": result["rho"],
            "rho_plus_p_l": result["rho"]+result["p_l"], "j_l": result["j_l"], "p_omega": result["p_omega"],
            "live": bool(live_packet_mask(s, l, params))}


def velocity_delivery(params, design):
    """Integrate dl/dsigma = U_packet/B from the live entry.

    Returns arrival times at l = 1.75, 3 and 5 and the packet position when the
    live window closes, where the window reading places it at l = sigma.
    """
    s, l, ds, marks, live_end = -1.4, -1.4, 2e-3, {}, live_packet_end(params)
    while s < 60 and l < 5.:
        fields = service_fields(s, l, params, reset_front=design.reset_front)
        l += ds*fields["U_packet"]/fields["B"]
        s += ds
        if s >= live_end and "live_end" not in marks:
            marks["live_end"] = round(l, 3)
        for mark in (1.75, 3., 5.):
            if l >= mark and mark not in marks:
                marks[mark] = round(s, 3)
    return marks


def ledger_row(task):
    name, s, l = task
    params, design = VARIANTS[name]
    fields = track_scalars(s, l, params, design)
    service = service_fields(s, l, params, reset_front=design.reset_front)
    alpha, beta, radial = fields["alpha"], fields["beta"], fields["gamma_ll"]
    norm = -alpha*alpha+radial*(service["U_packet"]/service["B"]+beta)**2
    result = evaluate_spherical_demand(s, l, params, .0025, .0025,
                                       scalar_evaluator=lambda a, b, p: track_scalars(a, b, p, design))
    plus, minus = alpha*alpha*result["null_energy_outgoing"], alpha*alpha*result["null_energy_ingoing"]
    return {"case": name, "s": s, "l": l, "stage": stage_name(s, params), "region": region_name(s, l, params),
            "inside_packet_geom": abs(l-s) <= params.Rpass, "inside_packet_live": live_packet_mask(s, l, params),
            "alpha": alpha, "beta": beta, "gamma_ll": radial, "gamma_omega": fields["gamma_omega"],
            "packet_norm": norm, "gtt": -alpha*alpha+radial*beta*beta, "U_beta": service["U_beta"],
            "U_packet": service["U_packet"], "B": service["B"], "q": service["q"], "W": service["W"],
            "rho_euler": result["rho"], "p_l_unit": result["p_l"], "j_l_unit": result["j_l"],
            "p_omega_unit": result["p_omega"], "Tkk_plus": plus, "Tkk_minus": minus,
            "Tkk_min_radial": min(plus, minus), "stress_algebraic_type": result["stress_algebraic_type"]}


def figures(output):
    """Deficit, minimum and delivery tradeoff from the recorded summary."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    summary = pd.read_csv(output / "summary.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for axis, column, label in ((axes[0], "angular_deficit_integral", "angular deficit integral"),
                                (axes[1], "min_angular_null", "minimum angular null energy")):
        for _, row in summary.iterrows():
            marker = "s" if row.variant.startswith("extended") else "o"
            axis.scatter(row.velocity_reading_reaches_l_5, row[column], marker=marker)
            axis.annotate(row.variant.replace("_", " "), (row.velocity_reading_reaches_l_5, row[column]), fontsize=7,
                          xytext=(4, 3), textcoords="offset points")
        axis.set_xlabel("velocity-reading arrival at l = 5")
        axis.set_ylabel(label)
    axes[0].set_yscale("log")
    fig.tight_layout()
    fig.savefig(output / "reset_tradeoff.png", dpi=140)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--step", type=float, default=.1)
    parser.add_argument("--runs", type=Path, default=service_checks.RUNS / "reset_schedule_options")
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_reports/data/reset_schedule_options")
    parser.add_argument("--figures-only", action="store_true", help="redraw figures from the recorded summary")
    args = parser.parse_args()
    if args.figures_only:
        figures(args.output)
        return
    started = time.time()
    args.output.mkdir(parents=True, exist_ok=True)
    s_axis = np.round(np.arange(-1.5, 20.+args.step/2, args.step), 10)
    l_axis = np.round(np.arange(-4.9, 4.9+args.step/2, args.step), 10)
    with ProcessPoolExecutor(args.workers) as pool:
        budget = pd.DataFrame(pool.map(evaluate, [(n, float(s), float(l)) for n in VARIANTS for s in s_axis
                                                  for l in l_axis], chunksize=64))
    budget["angular_null"] = budget.rho+budget.p_omega
    budget.to_csv(args.output / "budget_samples.csv.gz", index=False, compression={"method": "gzip", "mtime": 0},
                  float_format="%.9g")

    grid = pd.read_csv(service_checks.REFERENCE, usecols=["s", "l"])
    audit_log, paths, manifests, rows = [], {}, {}, []
    for name, (params, design) in VARIANTS.items():
        with ProcessPoolExecutor(args.workers) as pool:
            ledger = pd.DataFrame(pool.map(ledger_row, [(name, float(s), float(l)) for s, l in zip(grid.s, grid.l)],
                                           chunksize=64))
        base = args.runs / name
        base.mkdir(parents=True, exist_ok=True)
        paths[name] = base / "source_ledger_point_ledger.csv"
        ledger.to_csv(paths[name], index=False)
        manifests[name] = base / "schedule_manifest.json"
        manifests[name].write_text(json.dumps({"params": asdict(params)}, default=float))
        service_checks.audit("run_horizon_escape_ladder.py", ["--point-ledger", paths[name], "--label", name, "--outdir",
                             base / "escape_seed120", "--seeds-per-scope", 120, "--max-steps", 12000], audit_log)
        service_checks.audit("run_entry_packet_reachability.py", ["--point-ledger", paths[name], "--label", name,
                             "--outdir", base / "entry_reachability", "--entry-side", "lower", "--entry-side", "upper"],
                             audit_log)
        service_checks.audit("run_scheduled_adm_probe_evolution.py", ["--point-ledger", paths[name], "--label", name,
                             "--outdir", base / "scheduled_probe", "--red-tag-seeds", 120, "--max-steps", 12000], audit_log)
        service_checks.audit("run_trace_expansion_audit.py", ["--point-ledger", paths[name], "--seeds",
                             base / "scheduled_probe/scheduled_adm_probe_seeds.csv", "--outdir", base / "trace_expansion",
                             "--label", name], audit_log)
        service_checks.audit("run_dense_congruence_caustic_audit.py", ["--point-ledger", paths[name], "--trace-traces",
                             base / "trace_expansion/trace_expansion_audit_traces.csv", "--outdir",
                             base / "dense_bundles_all_centers", "--label", name, "--no-require-both-shrinking"], audit_log)
        service_checks.audit("run_service_time_advantage_ledger.py", ["--point-ledger", paths[name], "--label", name,
                             "--manifest", manifests[name], "--outdir", base / "service_time"], audit_log)
        group = budget[budget.variant == name]
        worst = group.loc[group.angular_null.idxmin()]
        probe = pd.read_csv(base / "scheduled_probe/scheduled_adm_probe_summary.csv")
        centerline = probe[probe.probe_family == "packet_centerline"]
        traces = pd.read_csv(base / "scheduled_probe/scheduled_adm_probe_traces.csv",
                             usecols=["probe_family", "trace_outcome"])
        horizon = int(((traces.probe_family == "packet_centerline") & (traces.trace_outcome == "s_upper_boundary")).sum())
        delivery = velocity_delivery(params, design)
        rows.append({
            "variant": name, "catch_center": params.x_catch_packet, "live_window_end": live_packet_end(params),
            "reset_complete": reset_complete(params, design), "points": len(group),
            "type_i": int((group.type == TYPE_I).sum()), "uncertified": int((~group.certified).sum()),
            "max_abs_rho_plus_p_l": float(group.rho_plus_p_l.abs().max()), "max_abs_j_l": float(group.j_l.abs().max()),
            "min_angular_null": float(worst.angular_null), "min_angular_null_s": float(worst.s),
            "min_angular_null_l": float(worst.l), "angular_violating_fraction": float((group.angular_null < -1e-9).mean()),
            "angular_deficit_integral": float(np.maximum(-group.angular_null, 0).sum()*args.step**2),
            "live_min_angular_null": float(group[group.live].angular_null.min()),
            "min_p_omega": float(group.p_omega.min()),
            "p_omega_negative_fraction": float((group.p_omega < -1e-9).mean()),
            "p_omega_deficit_integral": float(np.maximum(-group.p_omega, 0).sum()*args.step**2),
            "velocity_reading_l_at_live_end": delivery.get("live_end", math.nan),
            "velocity_reading_reaches_l_1p75": delivery.get(1.75, math.nan),
            "velocity_reading_reaches_l_3": delivery.get(3., math.nan),
            "velocity_reading_reaches_l_5": delivery.get(5., math.nan),
            "window_reading_reaches_l_5": 5.,
            "centerline_probes_escaped": int(centerline.radial_escape_count.sum()),
            "centerline_probes": int(centerline.traces.sum()),
            "centerline_probes_at_ledger_time_limit": horizon,
            "max_live_packet_norm": service_checks.packet_safety(paths[name])["max_live_packet_norm"],
        })
    safety = {name: service_checks.packet_safety(path) for name, path in paths.items()}
    table = service_checks.comparison(paths, {name: args.runs / name for name in paths}, safety)
    table.pivot_table(index=["audit", "metric"], columns="ledger", values="value", aggfunc="first", sort=False).to_csv(
        args.output / "audit_comparison_wide.csv")
    summary = pd.DataFrame(rows)
    summary.to_csv(args.output / "summary.csv", index=False)
    manifest = {
        "completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time()-started, 1), "workers": args.workers, "step": args.step,
        "carry_shifts": CARRY_SHIFTS,
        "variants": {name: {"params_changed": {k: v for k, v in asdict(p).items() if v != asdict(BASE)[k]},
                            "design": design.__dict__} for name, (p, design) in VARIANTS.items()},
        "reference_ledger_sha256": sha256_file(service_checks.REFERENCE), "audit_log": audit_log,
        "packet_safety": safety,
        "software_sha256": {path: sha256_file(ROOT / "toolkit/adm_harness_cli" / path) for path in (
            "adm_harness/constant_radius_track.py", "adm_harness/warped_product.py",
            "scripts/run_reset_schedule_options.py", "scripts/run_constant_radius_service_checks.py")},
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=1, default=str)+"\n")
    figures(args.output)
    pd.set_option("display.width", 250)
    print(summary.T.to_string())


if __name__ == "__main__":
    main()
