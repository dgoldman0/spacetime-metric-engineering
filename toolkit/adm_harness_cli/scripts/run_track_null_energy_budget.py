#!/usr/bin/env python3
"""Null-energy budget of the constant-radius track under decompression schedules; emit data.

Each case evaluates the C-infinity constant-radius candidate with the
warped-product evaluator and records the algebraic class, the radial and
angular null energies and the service-time proxies of its schedule.
Narrative interpretation is maintained manually in supporting_reports.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adm_harness.constant_radius_track import ConstantRadiusTrackDesign, track_scalars, service_fields
from adm_harness.radial_stress import TYPE_I
from adm_harness.source_ledger import SourceParams, live_packet_end, live_packet_mask, sha256_file
from adm_harness.warped_product import evaluate_spherical_demand

ROOT = Path(__file__).resolve().parents[3]
PARAMS = SourceParams(**json.loads((ROOT / "supporting_reports/data/le_geometry_boundary/manifest.json").read_text())["params"])
DESIGN = ConstantRadiusTrackDesign()
LIVE_END = live_packet_end(PARAMS)
CASES = {
    "current_schedule": {},
    "decompression_removed": {"q_t0": 1e3},
    "after_service_rate_1": {"q_t0": LIVE_END+.4},
    "after_service_rate_1_2": {"q_t0": LIVE_END+.4, "q_Tr": 6.},
    "after_service_rate_1_4": {"q_t0": LIVE_END+.4, "q_Tr": 12.},
}


def evaluate(task):
    name, s, l = task
    params = replace(PARAMS, **CASES[name])
    result = evaluate_spherical_demand(s, l, params, .0025, .0025,
                                       scalar_evaluator=lambda a, b, p: track_scalars(a, b, p, DESIGN))
    return {"case": name, "s": s, "l": l, "type": result["stress_algebraic_type"],
            "certified": bool(result["full_eigensystem_certified"]), "rho": result["rho"], "p_l": result["p_l"],
            "j_l": result["j_l"], "p_omega": result["p_omega"],
            "radial_null": min(result["null_energy_outgoing"], result["null_energy_ingoing"]),
            "live": bool(live_packet_mask(s, l, PARAMS))}


def proxies(params):
    """Schedule-factor and packet-coordinate advantage ratios along the l = sigma centerline."""
    s = np.linspace(-1.4, LIVE_END, 4001)
    fields = [service_fields(x, x, params) for x in s]
    speed = np.array([f["U_packet"] for f in fields])
    capacity = np.array([f["B"] for f in fields])
    span = LIVE_END+1.4
    return float(np.trapezoid(speed, s)/span), float(np.trapezoid(speed/capacity, s)/span)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--step", type=float, default=.1)
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_reports/data/track_null_energy_budget")
    args = parser.parse_args()
    started = time.time()
    s_axis = np.round(np.arange(-1.5, 16.+args.step/2, args.step), 10)
    l_axis = np.round(np.arange(-7., 7.+args.step/2, args.step), 10)
    tasks = [(name, float(s), float(l)) for name in CASES for s in s_axis for l in l_axis]
    with ProcessPoolExecutor(args.workers) as pool:
        frame = pd.DataFrame(pool.map(evaluate, tasks, chunksize=64))
    frame["angular_null"] = frame.rho+frame.p_omega
    cell = args.step**2
    rows = []
    tolerance = 1e-9
    for name, group in frame.groupby("case", sort=False):
        track = group[group.l.abs() < DESIGN.track_half_length]
        ends = group[(group.l.abs() >= DESIGN.track_half_length) & (group.s == group.s.max())]
        live = group[group.live]
        worst = track.loc[track.angular_null.idxmin()]
        case_params = replace(PARAMS, **CASES[name])
        schedule_ratio, packet_ratio = proxies(case_params)
        rows.append({
            "case": name, "q_t0": case_params.q_t0, "q_Tr": case_params.q_Tr,
            "points": len(group), "type_i": int((group.type == TYPE_I).sum()), "uncertified": int((~group.certified).sum()),
            "track_max_abs_rho_plus_p_l": float((track.rho+track.p_l).abs().max()),
            "max_abs_j_l": float(group.j_l.abs().max()), "track_min_radial_null": float(track.radial_null.min()),
            "track_min_angular_null": float(worst.angular_null), "track_min_angular_null_s": float(worst.s),
            "track_min_angular_null_l": float(worst.l),
            "track_angular_violating_fraction": float((track.angular_null < -tolerance).mean()),
            "track_angular_deficit_integral": float(np.maximum(-track.angular_null, 0).sum()*cell),
            "track_max_abs_p_omega": float(track.p_omega.abs().max()),
            "live_points": len(live), "live_min_angular_null": float(live.angular_null.min()),
            "ends_min_radial_null": float(ends.radial_null.min()), "ends_min_angular_null": float(ends.angular_null.min()),
            "ends_min_rho": float(ends.rho.min()),
            "ends_radial_deficit_per_unit_time": float(np.maximum(-ends.radial_null, 0).sum()*args.step),
            "ends_angular_deficit_per_unit_time": float(np.maximum(-ends.angular_null, 0).sum()*args.step),
            "schedule_proxy_ratio": schedule_ratio, "packet_coordinate_proxy_ratio": packet_ratio,
        })
    summary = pd.DataFrame(rows)
    args.output.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output / "summary.csv", index=False)
    frame.to_csv(args.output / "samples.csv.gz", index=False, compression={"method": "gzip", "mtime": 0},
                 float_format="%.9g")
    manifest = {
        "completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time()-started, 1), "workers": args.workers, "step": args.step,
        "design": DESIGN.__dict__, "cases": CASES, "live_packet_end": LIVE_END,
        "software_sha256": {path: sha256_file(ROOT / "toolkit/adm_harness_cli" / path) for path in (
            "adm_harness/constant_radius_track.py", "adm_harness/warped_product.py", "adm_harness/radial_stress.py",
            "adm_harness/source_ledger.py", "scripts/run_track_null_energy_budget.py")},
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=1, default=float)+"\n")
    print(summary.T.to_string())


if __name__ == "__main__":
    main()
