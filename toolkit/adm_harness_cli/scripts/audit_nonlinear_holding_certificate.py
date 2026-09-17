#!/usr/bin/env python3
"""Verify exact certificate matrices and apply them to four archived histories."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import multiprocessing
import platform
import shutil
import subprocess

import numpy as np

from adm_harness.nonlinear_holding_certificate import (
    guide_input_certificate, history_certificate, rational_certificate,
)

ROOT = Path(__file__).resolve().parents[3]
PARENT = ROOT / "supporting_reports/data/scheduled_optical_transfer"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified(name):
    path = PARENT / name
    if sha256(path) != json.loads((PARENT / "manifest.json").read_text())["output_sha256"][name]:
        raise ValueError(f"Parent evidence mismatch: {name}")
    return path


def history(task):
    name, output = task
    source = verified(name+"_states.npz")
    with np.load(source) as a:
        q2 = (np.sqrt(2*(a["node_final_receipt_l2_upper"]+a["node_final_guide_l2_upper"]))
              +np.sqrt(a["node_final_loop_l2_upper"]))**2
        # Preserve a small numerical margin around the archived floating bounds.
        q2 = np.nextafter(q2*(1+1e-10), np.inf)
        result = history_certificate(q2)
        labels, capacity = a["x"], a["capacity"]
    if not np.all(result["passed"]):
        raise ValueError(f"Nonlinear heat/spin certificate fails: {name}")
    np.savez_compressed(Path(output) / (name+"_certificate.npz"), x=labels,
        capacity=capacity, input_l2_upper=q2,
        thermal_action_upper=result["thermal_action_upper"], thermal_energy_upper=result["thermal_energy_upper"],
        spin_squared_lower=result["spin_squared_lower"],
        rotor_trace_bound_per_label=result["rotor_trace_magnitude_upper"]*capacity)
    index = np.unravel_index(np.argmax(result["thermal_action_upper"]), q2.shape)
    row = dict(label=name, input_sha256={str(source.relative_to(ROOT)): sha256(source)},
        maximum_input_l2=float(q2.max()), maximum_thermal_action=float(result["thermal_action_upper"].max()),
        nonlinear_thermal_action_ceiling=result["thermal_action_ceiling"],
        maximum_thermal_energy_over_C=float(result["thermal_energy_upper"].max()),
        minimum_spin=float(np.sqrt(result["spin_squared_lower"].min())),
        maximum_spin=float(np.sqrt(result["spin_upper_squared"])),
        minimum_radius=result["radius_minimum"], rotor_trace_bound_over_C=result["rotor_trace_magnitude_upper"],
        worst_node_index=int(index[0]), worst_material_label_index=int(index[1]),
        worst_material_label=float(labels[index[1]]), all_nodes_certified=True)
    print(name, "spin lower", row["minimum_spin"], "heat action", row["maximum_thermal_action"], flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_reports/data/nonlinear_holding_certificate")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    certificate, guide = rational_certificate(), guide_input_certificate()
    prior = json.loads(verified("summary.json").read_text())
    # The proof uses the same mathematical forcing construction as its parent.
    parent_manifest = json.loads((PARENT / "manifest.json").read_text())
    for name, digest in parent_manifest["runtime_sha256"].items():
        if sha256(ROOT / name) != digest:
            raise ValueError(f"Parent implementation changed: {name}")
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        histories = list(pool.map(history, [(h["label"], str(args.output)) for h in prior["histories"]]))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__),
        guide_input_certificate=guide, rational_certificate=certificate, histories=histories,
        initial_radial_error=[0., 0.], initial_thermal_action=1e-8,
        nonlinear_axisymmetric_rotor_certificate=True,
        absorption_and_rotational_drag_included=False, finite_actuator_slew_closed=False,
        spatial_route_constitutive_evolution_closed=False, full_rail_tensor_and_macro_work_closed=False,
        physical_material_realization_identified=False)
    (args.output / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(), ROOT / "toolkit/adm_harness_cli/adm_harness/nonlinear_holding_certificate.py",
             ROOT / "toolkit/adm_harness_cli/tests/test_nonlinear_holding_certificate.py"]
    for p in paths:
        shutil.copyfile(p, args.output / ("execution_"+p.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        parent_manifest_sha256={str((PARENT / "manifest.json").relative_to(ROOT)): sha256(PARENT / "manifest.json")},
        output_sha256={p.name: sha256(p) for p in sorted(args.output.iterdir()) if p.is_file() and p.name != "manifest.json"})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
