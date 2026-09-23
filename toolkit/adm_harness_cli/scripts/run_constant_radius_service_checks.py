#!/usr/bin/env python3
"""Replay the beta075 service audits on flat-throat candidate ledgers; emit comparison data.

Candidate point ledgers reuse the reference s=15 grid and its stage, region and
packet labels, with every metric and demanded-source column recomputed from the
candidate geometry. The existing audit scripts then run unchanged on the
reference and candidate ledgers. Narrative interpretation is maintained manually
in supporting_reports.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adm_harness.constant_radius_track import ConstantRadiusTrackDesign, track_scalars, service_fields
from adm_harness.source_ledger import SourceParams, scalars, sha256_file
from adm_harness.warped_product import evaluate_spherical_demand

ROOT = Path(__file__).resolve().parents[3]
HARNESS = ROOT / "toolkit/adm_harness_cli"
RUNS = HARNESS / "runs"
REFERENCE = RUNS / "beta_collar_generator_beta075_p003_mid_s15/ledgers/rematch_w6_t1p5/source_ledger_point_ledger.csv"
REFERENCE_SHA = "4c63e7bf43faced91caba846af14aff24fd62762e3df9627197447700219b473"
REFERENCE_MANIFEST = REFERENCE.with_name("source_ledger_manifest.json")
SEEDS = RUNS / "scheduled_adm_confidence_beta075_s15_189x121/scheduled_adm_probe/scheduled_adm_probe_seeds.csv"
PARAMS = SourceParams(**json.loads((ROOT / "supporting_reports/data/le_geometry_boundary/manifest.json").read_text())["params"])
CANDIDATES = {
    "constant_radius_repaired_service": ConstantRadiusTrackDesign(smooth_service=False),
    "constant_radius_smooth": ConstantRadiusTrackDesign(),
}
LABELS = ["case", "s", "l", "stage", "region", "inside_packet_geom", "inside_packet_live", "cell_area",
          "point_weight", "volume_weight"]


def candidate_row(task):
    name, s, l = task
    design = CANDIDATES[name]
    fields = track_scalars(s, l, PARAMS, design)
    if design.smooth_service:
        service = service_fields(s, l, PARAMS, smooth=True, abs_width=design.abs_width, cap_width=design.cap_width,
                                 join_fraction=design.join_fraction)
    else:
        service = scalars(s, l, PARAMS)
    alpha, beta, radial = fields["alpha"], fields["beta"], fields["gamma_ll"]
    vcoord = service["U_packet"]/service["B"]
    norm = -alpha*alpha+radial*(vcoord+beta)**2
    result = evaluate_spherical_demand(s, l, PARAMS, .0025, .0025,
                                       scalar_evaluator=lambda a, b, p: track_scalars(a, b, p, design))
    rho, pressure, current = result["rho"], result["p_l"], result["j_l"]
    packet_density = math.nan
    if norm < 0:
        a, b = alpha, math.sqrt(radial)*(vcoord+beta)
        packet_density = (a*a*rho-2*a*b*current+b*b*pressure)/(-norm)
    plus, minus = alpha*alpha*result["null_energy_outgoing"], alpha*alpha*result["null_energy_ingoing"]
    return {"s": s, "l": l, "alpha": alpha, "beta": beta, "gamma_ll": radial, "gamma_omega": fields["gamma_omega"],
            "packet_norm": norm, "gtt": -alpha*alpha+radial*beta*beta,
            "spatial_volume_density": math.sqrt(radial)*fields["gamma_omega"],
            "U_beta": service["U_beta"], "U_packet": service["U_packet"], "B": service["B"], "q": service["q"],
            "W": service["W"], "rho_euler": rho, "p_l_unit": pressure, "j_l_unit": current,
            "p_omega_unit": result["p_omega"], "rho_packet": packet_density, "Tkk_plus": plus, "Tkk_minus": minus,
            "Tkk_min_radial": min(plus, minus), "stress_algebraic_type": result["stress_algebraic_type"]}


def build_ledgers(output, workers):
    if sha256_file(REFERENCE) != REFERENCE_SHA:
        raise ValueError("reference point ledger hash mismatch")
    reference = pd.read_csv(REFERENCE)
    labels = reference[LABELS]
    paths = {"beta075_rematch_w6_t1p5": REFERENCE}
    for name in CANDIDATES:
        tasks = [(name, float(s), float(l)) for s, l in zip(labels.s, labels.l)]
        with ProcessPoolExecutor(workers) as pool:
            rows = pd.DataFrame(pool.map(candidate_row, tasks, chunksize=64))
        ledger = labels.drop(columns=["s", "l"]).assign(case=name).join(rows)
        path = output / name / "source_ledger_point_ledger.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        ledger.to_csv(path, index=False)
        paths[name] = path
    return paths


def audit(script, arguments, log, recorded_outcome=None):
    """Run one audit script; recorded_outcome names an expected, reportable stop message."""
    command = [sys.executable, str(HARNESS / "scripts" / script), *map(str, arguments)]
    environment = os.environ | {"PYTHONPATH": str(HARNESS), "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1",
                                "MKL_NUM_THREADS": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    started = time.time()
    result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, text=True)
    log.append({"script": script, "arguments": [str(x) for x in arguments], "returncode": result.returncode,
                "seconds": round(time.time()-started, 2), "stderr_tail": result.stderr[-2000:]})
    if result.returncode and not (recorded_outcome and recorded_outcome in result.stderr):
        raise RuntimeError(f"{script} failed: {result.stderr[-2000:]}")
    log[-1]["recorded_outcome"] = recorded_outcome if result.returncode else None


def run_audits(paths, output, log):
    """Run every audit on each ledger; candidates also trace bundles from the reference centers."""
    outputs, reference_traces = {}, None
    for label, ledger in paths.items():
        base = output / label
        outputs[label] = base
        audit("run_horizon_escape_ladder.py", ["--point-ledger", ledger, "--label", label, "--outdir",
              base / "escape_seed120", "--seeds-per-scope", 120, "--max-steps", 12000], log)
        audit("run_entry_packet_reachability.py", ["--point-ledger", ledger, "--label", label, "--outdir",
              base / "entry_reachability", "--entry-side", "lower", "--entry-side", "upper"], log)
        audit("run_scheduled_adm_probe_evolution.py", ["--point-ledger", ledger, "--label", label, "--outdir",
              base / "scheduled_probe", "--red-tag-seeds", 120, "--max-steps", 12000], log)
        audit("run_trace_expansion_audit.py", ["--point-ledger", ledger, "--seeds", SEEDS, "--outdir",
              base / "trace_expansion", "--label", label], log)
        traces = base / "trace_expansion" / "trace_expansion_audit_traces.csv"
        reference_traces = reference_traces or traces
        audit("run_dense_congruence_caustic_audit.py", ["--point-ledger", ledger, "--trace-traces", traces,
              "--outdir", base / "dense_bundles", "--label", label], log,
              recorded_outcome="no minus-branch branch-band centers were available")
        audit("run_dense_congruence_caustic_audit.py", ["--point-ledger", ledger, "--trace-traces", traces,
              "--outdir", base / "dense_bundles_all_centers", "--label", label, "--no-require-both-shrinking"], log)
        if traces != reference_traces:
            audit("run_dense_congruence_caustic_audit.py", ["--point-ledger", ledger, "--trace-traces",
                  reference_traces, "--outdir", base / "dense_bundles_reference_centers", "--label", label], log)
        audit("run_service_time_advantage_ledger.py", ["--point-ledger", ledger, "--label", label, "--manifest",
              REFERENCE_MANIFEST, "--outdir", base / "service_time"], log)
    return outputs


def read(path):
    return pd.read_csv(path) if path.exists() else None


def comparison(paths, outputs, safety):
    """Collect the headline measurements of every audit into one tidy table."""
    rows = []

    def add(label, audit_name, metric, value):
        rows.append({"ledger": label, "audit": audit_name, "metric": metric, "value": value})

    for label, base in outputs.items():
        for key, value in safety[label].items():
            add(label, "packet_safety", key, value)
        escape = read(base / "escape_seed120/horizon_escape_trace_summary.csv")
        add(label, "radial_escape", "traces", int(escape.traces.sum()))
        add(label, "radial_escape", "expected_escape", int(escape.expected_escape_count.sum()))
        add(label, "radial_escape", "escaped", int(escape.any_radial_escape_count.sum()))
        add(label, "radial_escape", "stalled", int(escape.invalid_or_stalled_count.sum()))
        reach = read(base / "entry_reachability/entry_packet_reachability_summary.csv")
        for key in ("reachable_packet_hits", "service_stage_hits", "carry_stage_hits"):
            add(label, "entry_reachability", key, int(reach[key].sum()))
        probe = read(base / "scheduled_probe/scheduled_adm_probe_summary.csv")
        add(label, "scheduled_probe", "traces", int(probe.traces.sum()))
        add(label, "scheduled_probe", "escaped", int(probe.radial_escape_count.sum()))
        add(label, "scheduled_probe", "max_packet_norm", float(probe.max_packet_norm.max()))
        add(label, "scheduled_probe", "min_areal_expansion_proxy", float(probe.min_areal_expansion_proxy.min()))
        expansion = read(base / "trace_expansion/trace_expansion_audit_summary.csv")
        for key in ("traces", "radial_escape_count", "traces_entering_both_shrinking", "traces_sustained_to_end"):
            add(label, "trace_expansion", key, int(expansion[key].sum()))
        add(label, "trace_expansion", "max_integrated_trapped_like_strength",
            float(expansion.max_integrated_trapped_like_strength.max()))
        for name in ("dense_bundles", "dense_bundles_reference_centers", "dense_bundles_all_centers"):
            bundles = read(base / name / "dense_congruence_caustic_summary.csv")
            if bundles is None:
                continue
            add(label, name, "bundles", len(bundles))
            add(label, name, "rays", int(bundles.rays.sum()))
            add(label, name, "escaped", int(bundles.radial_escape_count.sum()))
            add(label, name, "crossing_samples", int(bundles.crossing_samples.sum()))
            add(label, name, "caustic_like_flags", int(bundles.caustic_like_collapse.sum()))
            add(label, name, "min_common_l_width_ratio", float(bundles.min_common_l_width_ratio.min()))
            add(label, name, "min_common_adjacent_l_gap_ratio", float(bundles.min_common_adjacent_l_gap_ratio.min()))
            add(label, name, "min_all_both_l_width_ratio", float(bundles.min_all_both_l_width_ratio.min()))
            add(label, name, "max_initial_radius_width", float(bundles.initial_radius_width.max()))
        service = read(base / "service_time/service_time_advantage_summary.csv").iloc[0]
        for key in ("prepared_service_time", "schedule_factor_distance", "packet_coord_proxy_distance",
                    "schedule_factor_advantage_ratio", "packet_coord_proxy_advantage_ratio",
                    "request_schedule_factor_advantage_ratio", "request_packet_coord_proxy_advantage_ratio"):
            add(label, "service_time", key, float(service[key]))
    return pd.DataFrame(rows)


def packet_safety(ledger):
    points = pd.read_csv(ledger, usecols=["s", "l", "inside_packet_live", "packet_norm", "stage"])
    live = points[points.inside_packet_live.astype(str).str.lower().isin({"true", "1"})]
    return {"live_points": len(live), "positive_live_packet_norm": int((live.packet_norm >= 0).sum()),
            "max_live_packet_norm": float(live.packet_norm.max())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--runs", type=Path, default=RUNS / "constant_radius_service")
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_reports/data/constant_radius_service")
    args = parser.parse_args()
    started = time.time()
    args.runs.mkdir(parents=True, exist_ok=True)
    args.output.mkdir(parents=True, exist_ok=True)
    paths = build_ledgers(args.runs, args.workers)
    log = []
    outputs = run_audits(paths, args.runs, log)
    safety = {label: packet_safety(path) for label, path in paths.items()}
    table = comparison(paths, outputs, safety)
    table.to_csv(args.output / "comparison.csv", index=False)
    table.pivot_table(index=["audit", "metric"], columns="ledger", values="value", aggfunc="first", sort=False).to_csv(
        args.output / "comparison_wide.csv")
    manifest = {
        "completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time()-started, 1), "workers": args.workers,
        "reference_ledger": str(REFERENCE.relative_to(ROOT)), "reference_sha256": REFERENCE_SHA,
        "reference_manifest_sha256": sha256_file(REFERENCE_MANIFEST),
        "seeds": str(SEEDS.relative_to(ROOT)), "seeds_sha256": sha256_file(SEEDS),
        "ledgers": {label: {"path": str(Path(path).relative_to(ROOT)), "sha256": sha256_file(Path(path))}
                    for label, path in paths.items()},
        "audit_outputs": {label: str(path.relative_to(ROOT)) for label, path in outputs.items()},
        "designs": {name: design.__dict__ for name, design in CANDIDATES.items()},
        "packet_safety": safety, "audit_log": log,
        "software_sha256": {path: sha256_file(HARNESS / path) for path in (
            "adm_harness/constant_radius_track.py", "adm_harness/warped_product.py", "scripts/run_constant_radius_service_checks.py",
            "scripts/run_horizon_escape_ladder.py", "scripts/run_entry_packet_reachability.py",
            "scripts/run_scheduled_adm_probe_evolution.py", "scripts/run_trace_expansion_audit.py",
            "scripts/run_dense_congruence_caustic_audit.py", "scripts/run_service_time_advantage_ledger.py")},
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=1, default=str)+"\n")
    print(json.dumps(safety, indent=1))
    print(f"completed in {manifest['elapsed_seconds']} s")


if __name__ == "__main__":
    main()
