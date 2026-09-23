#!/usr/bin/env python3
"""Attribute the beta075 Type IV demand to service features; emit data only.

Each control switches features of the regularity-repaired beta075 geometry off
and evaluates the frozen four-dimensional curvature kernel with the certified
classifier on a common grid. Narrative interpretation is maintained manually
in supporting_reports.
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
from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.metric_regularity import regularized_scalars
from adm_harness.radial_stress import TYPE_IV
from adm_harness.source_ledger import SourceParams, sha256_file

ROOT = Path(__file__).resolve().parents[3]
BASE = SourceParams(**json.loads((ROOT / "supporting_reports/data/le_geometry_boundary/manifest.json").read_text())["params"])
PACKET_OFF = dict(
    standing_support_packet_exclusion_shoulder=0., standing_support_packet_lapse_log_gain=0.,
    standing_support_packet_smooth_split_enabled=False, standing_support_packet_radial_log_gain=0.,
    standing_support_packet_radial_shoulder_log_gain=0., standing_support_packet_radial_skirt_log_gain=0.,
    standing_support_packet_beta_rematch_gain=0.)
FROZEN = dict(q_t0=1e3, xOmega=1e3)
CONTROLS = {
    "repaired_beta075": ({}, False),
    "decompression_removed": (dict(q_t0=1e3), False),
    "decompression_and_jacket_decay_removed": (FROZEN, False),
    "static_support_packet_windows_zero_shift": (FROZEN, True),
    "static_support_carrying_flow_only": (FROZEN | PACKET_OFF, False),
    "static_support_without_shell_and_receiver": (FROZEN | dict(support_shell_overlay_enabled=False,
                                                               support_edge_receiver_enabled=False), False),
    "decompression_alone": (PACKET_OFF | dict(support_shell_overlay_enabled=False,
                                              support_edge_receiver_enabled=False), True),
}


def zero_shift(s, l, params):
    return regularized_scalars(s, l, params) | {"beta": 0.}


def evaluate(task):
    name, s, l = task
    overrides, shift_removed = CONTROLS[name]
    result = evaluate_demand(s, l, replace(BASE, **overrides), .0025, .0025,
                             scalar_evaluator=zero_shift if shift_removed else regularized_scalars)
    return {"control": name, "s": s, "l": l, "type": result["stress_algebraic_type"],
            "certified": bool(result["full_eigensystem_certified"]), "rho": result["rho"], "p_l": result["p_l"],
            "j_l": result["j_l"], "p_omega": result["p_omega"], "imaginary": result["imaginary_eigenvalue_scale"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--step", type=float, default=.1)
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_reports/data/type_iv_attribution")
    args = parser.parse_args()
    started = time.time()
    s_axis = np.round(np.arange(-1.5, 2.9+args.step/2, args.step), 10)
    l_axis = np.round(np.arange(-4., 4.+args.step/2, args.step), 10)
    tasks = [(name, float(s), float(l)) for name in CONTROLS for s in s_axis for l in l_axis]
    with ProcessPoolExecutor(args.workers) as pool:
        frame = pd.DataFrame(pool.map(evaluate, tasks, chunksize=64))
    args.output.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output / "attribution.csv.gz", index=False, compression={"method": "gzip", "mtime": 0},
                 float_format="%.12g")
    summary = frame.assign(type_iv=frame.type.eq(TYPE_IV)).groupby("control", sort=False).agg(
        points=("type_iv", "size"), type_iv=("type_iv", "sum"), certified_fraction=("certified", "mean"),
        imaginary_integral=("imaginary", lambda x: float(x.sum()*args.step**2))).reset_index()
    summary.to_csv(args.output / "summary.csv", index=False)
    manifest = {
        "completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time()-started, 1), "workers": args.workers, "step": args.step,
        "controls": {name: {"overrides": overrides, "shift_removed": removed}
                     for name, (overrides, removed) in CONTROLS.items()},
        "software_sha256": {path: sha256_file(ROOT / "toolkit/adm_harness_cli" / path) for path in (
            "adm_harness/geometry_boundary.py", "adm_harness/metric_regularity.py", "adm_harness/radial_stress.py",
            "adm_harness/source_ledger.py", "scripts/run_type_iv_attribution.py")},
        "summary": summary.to_dict(orient="records"),
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=1, default=float)+"\n")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
