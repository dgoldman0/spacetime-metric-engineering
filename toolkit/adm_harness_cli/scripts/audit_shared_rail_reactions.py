#!/usr/bin/env python3
"""Count a shared reaction allocation in four conserved-inventory histories."""
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

from adm_harness.shared_rail_reactions import (
    SUPPORT_INDICES, guide_trace_bound, reaction_state, total_trace_bound,
)

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "supporting_reports/data"
PARENTS = ("scheduled_optical_transfer", "constitutive_joints_and_optics",
           "nonlinear_holding_certificate")
LOSS = .62e-6


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified(group, name):
    path = DATA / group / name
    manifest = json.loads((DATA / group / "manifest.json").read_text())
    if sha256(path) != manifest["output_sha256"][name]:
        raise ValueError(f"Parent evidence mismatch: {path}")
    return path


def history(task):
    name, output = task
    sources = [verified(group, name+"_states.npz") for group in PARENTS[:2]]
    with np.load(sources[0]) as a, np.load(sources[1]) as j:
        capacity, labels = a["capacity"], a["x"]
        trace_bound = total_trace_bound()*capacity
        bias = trace_bound/3
        support = list(SUPPORT_INDICES)
        tension = j["effective_material_tension"][support]
        inventory = j["material_inventory"][support, None]
        joints = j["joint_inventory_per_direction"][support, None]
        # The analytic ceiling covers every intermediate baseline and trace.
        # The five allocations separately describe the sampled constitutive states.
        fractions = np.linspace(-1, 1, 5)
        worst_energy = np.zeros_like(capacity)
        min_gain, max_gain = np.full_like(capacity, np.inf), np.zeros_like(capacity)
        max_joint, max_core = np.zeros_like(capacity), np.zeros_like(capacity)
        force_margin = np.ones_like(capacity)
        tensor_error = 0.
        for fraction in fractions:
            r = reaction_state(fraction*trace_bound[None], bias[None], tension, inventory, joints)
            worst_energy = np.maximum(worst_energy, r["additional_energy"].max(axis=0))
            min_gain = np.minimum(min_gain, r["energy_trace_derivative"].min(axis=0))
            max_gain = np.maximum(max_gain, r["energy_trace_derivative"].max(axis=0))
            max_joint = np.maximum(max_joint, r["joint_stretch"].max(axis=(0, 1)))
            max_core = np.maximum(max_core, r["core_stretch"].max(axis=(0, 1)))
            force_margin = np.minimum(force_margin, r["force_margin"].min(axis=(0, 1)))
            tensor_error = max(tensor_error, float(np.max(abs(r["stress_identity_error"]))))
        continuous_cost = 3*trace_bound
        transfer_loss = LOSS*a["finite_loop_total_exposure_upper"]/(1-LOSS/.3)
        screened_margin = a["all_panel_reserve_lower_bound"]-transfer_loss-continuous_cost[None]
        margin = screened_margin.min(axis=0)
        if (np.any(margin <= 0) or np.any(force_margin <= 0)
                or np.any(worst_energy > continuous_cost*(1+1e-10))):
            raise ValueError(f"Shared reaction state screen failed: {name}")
    np.savez_compressed(Path(output) / (name+"_reactions.npz"), x=labels, capacity=capacity,
        trace_magnitude_upper=trace_bound, isotropic_bias=bias,
        continuous_additional_energy_ceiling=continuous_cost,
        sampled_additional_energy_maximum=worst_energy,
        sampled_energy_trace_derivative_minimum=min_gain,
        sampled_energy_trace_derivative_maximum=max_gain,
        sampled_maximum_joint_stretch=max_joint, sampled_maximum_core_stretch=max_core,
        sampled_force_margin_minimum=force_margin,
        old_transfer_loss_and_reaction_state_reserve_lower=margin)
    row = dict(label=name, input_sha256={str(p.relative_to(ROOT)): sha256(p) for p in sources},
        maximum_trace_demand=float(trace_bound.max()),
        continuous_energy_ceiling_maximum=float(continuous_cost.max()),
        sampled_additional_energy_maximum=float(worst_energy.max()),
        sampled_energy_trace_derivative_range=[float(min_gain.min()), float(max_gain.max())],
        sampled_maximum_joint_stretch=float(max_joint.max()),
        sampled_maximum_core_stretch=float(max_core.max()),
        sampled_minimum_joint_force_margin=float(force_margin.min()),
        maximum_tensor_identity_error=tensor_error,
        minimum_reserve_with_old_transfer_loss_and_reaction_state=float(margin.min()),
        state_energy_screen_passed=True)
    print(name, "state margin", row["minimum_reserve_with_old_transfer_loss_and_reaction_state"],
          "work gain", row["sampled_energy_trace_derivative_range"], flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=DATA / "shared_rail_reactions")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    prior = json.loads(verified(PARENTS[0], "summary.json").read_text())
    for group in PARENTS:
        manifest = json.loads((DATA / group / "manifest.json").read_text())
        for name, digest in manifest["runtime_sha256"].items():
            if sha256(ROOT / name) != digest:
                raise ValueError(f"Parent implementation changed: {name}")
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        histories = list(pool.map(history, [(h["label"], str(args.output)) for h in prior["histories"]]))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__), histories=histories,
        guide_trace_bound_over_C=guide_trace_bound(), total_trace_bound_over_C=total_trace_bound(),
        continuous_reaction_energy_ceiling_over_C=3*total_trace_bound(),
        inherited_transfer_loss_fraction=LOSS, field_bias_families=["maxwell", "photon"],
        integrated_stress_allocation_closed=True, fixed_original_support_inventories=True,
        reciprocal_work_inherited_history_recomputed=False,
        field_bias_hosts_and_holding_losses_included=False,
        spatial_interfaces_constructed=False, physical_material_realization_identified=False)
    (args.output / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(), ROOT / "toolkit/adm_harness_cli/adm_harness/shared_rail_reactions.py",
             ROOT / "toolkit/adm_harness_cli/tests/test_shared_rail_reactions.py"]
    for path in paths:
        shutil.copyfile(path, args.output / ("execution_"+path.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        parent_manifest_sha256={str((DATA / g / "manifest.json").relative_to(ROOT)):
            sha256(DATA / g / "manifest.json") for g in PARENTS},
        output_sha256={p.name: sha256(p) for p in sorted(args.output.iterdir()) if p.is_file() and p.name != "manifest.json"})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
