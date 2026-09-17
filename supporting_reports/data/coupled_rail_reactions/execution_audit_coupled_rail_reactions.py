#!/usr/bin/env python3
"""Audit exact local reaction-work feedback at inherited support states."""
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
import scipy

from adm_harness.coupled_rail_reactions import FrozenReaction, simulate_coupled_transition
from adm_harness.shared_rail_reactions import SUPPORT_INDICES, reaction_state, total_trace_bound

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "supporting_reports/data"
PARENTS = ("shared_rail_reactions", "scheduled_optical_transfer", "constitutive_joints_and_optics")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified(group, name):
    path = DATA / group / name
    expected = json.loads((DATA / group / "manifest.json").read_text())["output_sha256"][name]
    if sha256(path) != expected:
        raise ValueError(f"Parent evidence mismatch: {path}")
    return path


def contexts():
    rows = []
    for history in ("first_n32_t4113", "second_n32_t2057"):
        paths = [verified(g, history+"_states.npz") for g in PARENTS[1:]]
        with np.load(paths[0]) as a, np.load(paths[1]) as j:
            capacity = a["capacity"]
            indices = list(SUPPORT_INDICES)
            T = j["effective_material_tension"][indices]/capacity
            M = j["material_inventory"][indices]/capacity
            m = j["joint_inventory_per_direction"][indices]/capacity
            r = reaction_state(np.zeros((1, 1)), np.full((1, 1), total_trace_bound()/3),
                               T, M[:, None], m[:, None])
            gain = r["energy_trace_derivative"]
            for name, index in (("low", np.argmin(gain)), ("high", np.argmax(gain))):
                time, label = np.unravel_index(index, gain.shape)
                rows.append(dict(name=history.split("_")[0]+"_"+name, history=history,
                    sample_index=int(time), label_index=int(label), coordinate_time=float(j["t"][time]),
                    material_label=float(j["x"][label]), capacity=float(capacity[label]),
                    baseline_gain=float(gain[time, label]),
                    tension=T[:, time, label].tolist(), core_inventory=M[:, label].tolist(),
                    joint_inventory=m[:, label].tolist(),
                    input_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths}))
    return rows


def trial(task):
    context, direction, refined, output = task
    left, right = (0., 1.) if direction == "up" else (1., 0.)
    name = context["name"]+"_"+direction+("_refined" if refined else "")
    model = FrozenReaction(context["tension"], context["core_inventory"], context["joint_inventory"])
    options = dict(maximum_step=.06, output_step=.01, rtol=5e-10, atol=5e-12) if refined else dict(output_step=.02)
    r = simulate_coupled_transition(left, right, model, **options)
    ledger = float(np.max(abs(r["complete_ledger_error"])))
    margin = r["numerical_extrema"]["minimum_converter_incident_margin"]
    if not r["complete"] or ledger > 5e-8 or margin < -5e-9:
        raise ValueError(f"Coupled trial failed: {name}, {r['boundary']}, {ledger}, {margin}")
    np.savez_compressed(Path(output) / (name+"_states.npz"),
        **{k: v for k, v in r.items() if isinstance(v, np.ndarray)})
    row = dict(name=name, context=context["name"], left=left, right=right, refined=refined,
        options=options, complete=r["complete"],
        **r["numerical_extrema"],
        sampled_minimum_spin=float(r["state"][2].min()), maximum_spin=float(r["state"][2].max()),
        minimum_proper_stretch=float(r["proper_stretch"].min()),
        minimum_work_denominator=float(r["denominator"].min()),
        initial_reaction_energy=r["initial_reaction_energy"],
        maximum_reaction_energy_excursion=float(np.max(abs(r["reaction_energy"]-r["initial_reaction_energy"]))),
        final_rotor_input_l2=float(r["rotor_input_l2"][-1]),
        final_reaction_work_throughput=float(r["reaction_work_throughput"][-1]),
        final_rotor_reflective_exposure=float(r["rotor_reflective_exposure"][-1]),
        maximum_complete_ledger_error=ledger,
        maximum_coupled_energy_error=float(np.max(abs(r["coupled_energy_error"]))),
        maximum_reciprocal_power_error=float(np.max(abs(r["reciprocal_power_error"]))),
        maximum_output_port_balance_error=float(np.max(abs(r["converter_output_balance_error"]))))
    print(name, "spin", row["minimum_spin"], "peak reaction work", row["maximum_absolute_reaction_power"],
          "ledger", ledger, flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=DATA / "coupled_rail_reactions")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    for group in PARENTS:
        manifest = json.loads((DATA / group / "manifest.json").read_text())
        for path, digest in manifest["runtime_sha256"].items():
            if sha256(ROOT / path) != digest:
                raise ValueError(f"Parent implementation changed: {path}")
    support = contexts()
    tasks = [(c, direction, False, str(args.output)) for c in support for direction in ("up", "down")]
    tasks += [(c, direction, True, str(args.output)) for c in support if c["name"] == "first_high"
              for direction in ("up", "down")]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        trials = list(pool.map(trial, tasks))
    refinements = []
    for refined in (row for row in trials if row["refined"]):
        base = next(row for row in trials if row["name"] == refined["name"].removesuffix("_refined"))
        keys = ("minimum_spin", "maximum_thermal_energy", "final_rotor_input_l2",
                "final_reaction_work_throughput", "maximum_absolute_trace", "maximum_absolute_rotor_power")
        errors = {key: abs(refined[key]-base[key]) for key in keys}
        if max(errors.values()) > 1e-6:
            raise ValueError("Coupled refinement exceeds its declared tolerance")
        refinements.append(dict(name=refined["name"], absolute_metric_changes=errors))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        contexts=support, trials=trials, refinements=refinements,
        extrema_method="Dense-output local optimization seeded by eight strongest grid samples; one-sided forcing joins retained",
        exact_support_state_energy_used=True, guide_reaction_work_included=True,
        frozen_macro_support=True, ideal_bidirectional_reaction_branch=True,
        reaction_branch_flight_time=0.,
        full_history_coupled_heat_certificate=False, moving_macro_work_included=False,
        field_hosts_and_holding_losses_included=False, finite_actuator_slew_included=False,
        spatial_joint_reactions_constructed=False)
    (args.output / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(), ROOT / "toolkit/adm_harness_cli/adm_harness/coupled_rail_reactions.py",
             ROOT / "toolkit/adm_harness_cli/tests/test_coupled_rail_reactions.py"]
    for p in paths:
        shutil.copyfile(p, args.output / ("execution_"+p.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        parent_manifest_sha256={str((DATA / g / "manifest.json").relative_to(ROOT)):
            sha256(DATA / g / "manifest.json") for g in PARENTS},
        output_sha256={p.name: sha256(p) for p in sorted(args.output.iterdir()) if p.is_file() and p.name != "manifest.json"})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
