#!/usr/bin/env python3
"""Replay finite reaction transport with updated damping, bias and electric ports."""
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

from adm_harness.hosted_reaction_dynamics import simulate_hosted_transition

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT/"supporting_reports/data"
PARENTS = ("finite_reaction_transport", "reaction_work_interfaces")


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def trial(task):
    name, context, direction, options, output = task
    left, right = (0., 1.) if direction == "up" else (1., 0.)
    r = simulate_hosted_transition(left, right, context, **options)
    errors = {k: float(np.max(abs(r[k]))) for k in
        ("complete_ledger_error", "output_balance_error", "endpoint_mechanical_error", "terminal_work_error")}
    floors = {k: float(r[k].min()) for k in
        ("minimum_emitted_power", "incident_margin", "complementary_field_energy", "capacitor_gap")}
    if max(errors.values()) > 5e-8 or min(floors.values()) <= 0:
        raise ValueError(f"Hosted reaction admission failed: {name}, {errors}, {floors}")
    step = float(r["time"][1]-r["time"][0])
    stride = max(1, int(.04/step))
    select = np.unique(np.r_[np.arange(0, len(r["time"]), stride),
        np.flatnonzero((r["time"] >= -3) & (r["time"] <= 4)), len(r["time"])-1])
    np.savez_compressed(Path(output)/(name+"_states.npz"),
        **{k: v[..., select] for k, v in r.items() if isinstance(v, np.ndarray)})
    row = dict(name=name, context=context["name"], direction=direction, options=options,
        evaluated_points=len(r["time"]), archived_points=len(select), final_state=r["state"][:, -1].tolist(),
        minimum_spin=float(r["state"][2].min()), peak_thermal_energy=float(r["thermal_energy"].max()),
        peak_rotor_power=float(np.max(abs(r["rotor_power"]))), peak_support_power=float(np.max(abs(r["support_power"]))),
        peak_electric_terminal_power=float(np.max(abs(r["capacitor_electrical_power"]))),
        peak_complementary_field_power=float(np.max(abs(r["complementary_field_power"]))),
        peak_dynamic_trace=float(np.max(abs(r["dynamic_trace"]))),
        peak_capacitor_energy=float(r["capacitor_energy"].max()),
        maximum_modulation_ratio=float(r["modulation_ratio"].max()),
        maximum_facet_speed=float(np.max(abs(r["facet_velocity"]))),
        final_rotor_input_l2=float(r["rotor_input_l2"][-1]),
        initial_support_energy=r["initial_support_energy"], errors=errors, floors=floors)
    print(name, "spin", row["minimum_spin"], "heat", row["peak_thermal_energy"],
          "ledger", errors["complete_ledger_error"], flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=DATA/"hosted_reaction_dynamics")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("positive worker count required")
    args.output.mkdir(parents=True, exist_ok=True)
    for group in PARENTS:
        m = json.loads((DATA/group/"manifest.json").read_text())
        for name, digest in m["runtime_sha256"].items():
            if sha256(ROOT/name) != digest:
                raise ValueError(f"Parent implementation changed: {name}")
        if sha256(DATA/group/"summary.json") != m["output_sha256"]["summary.json"]:
            raise ValueError(f"Parent summary changed: {group}")
    contexts = json.loads((DATA/"finite_reaction_transport/summary.json").read_text())["contexts"]
    first = next(c for c in contexts if c["name"] == "first_high")
    tasks = [(c["name"]+"_"+d, c, d, {}, str(args.output)) for c in contexts for d in ("up", "down")]
    tasks += [("first_high_"+d+"_refined", first, d,
        dict(samples_per_delay=8, maximum_step=.06, rtol=5e-10, atol=5e-12), str(args.output)) for d in ("up", "down")]
    tasks += [("first_high_"+d+"_inventory18", first, d, dict(inventory=18.), str(args.output)) for d in ("up", "down")]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        trials = list(pool.map(trial, tasks))
    refinements = []
    for r in (r for r in trials if r["name"].endswith("_refined")):
        b = next(t for t in trials if t["name"] == r["name"].removesuffix("_refined"))
        error = float(np.max(abs(np.array(b["final_state"])-r["final_state"])))
        input_error = abs(b["final_rotor_input_l2"]-r["final_rotor_input_l2"])
        if max(error, input_error) > 1e-7:
            raise ValueError("Updated hosted dynamics fails refinement tolerance")
        refinements.append(dict(name=r["name"], final_state_error=error, input_l2_error=input_error))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        default_inventory=19., damping=.8, field_bias_over_C=.62, contexts=contexts, trials=trials, refinements=refinements,
        finite_work_paths_and_photon_stress_included=True,
        periodic_capacitor_and_complementary_field_ports_included=True,
        frozen_macro_support=True, prescribed_synchronized_endpoint_commands=True,
        finite_electrical_leads_and_elastic_propagation_included=False,
        electrode_material_and_holding_loss_law_identified=False)
    (args.output/"summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(), ROOT/"toolkit/adm_harness_cli/adm_harness/hosted_reaction_dynamics.py",
             ROOT/"toolkit/adm_harness_cli/tests/test_hosted_reaction_dynamics.py"]
    for p in paths:
        shutil.copyfile(p, args.output/("execution_"+p.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        parent_manifest_sha256={str((DATA/g/"manifest.json").relative_to(ROOT)): sha256(DATA/g/"manifest.json") for g in PARENTS},
        output_sha256={p.name: sha256(p) for p in sorted(args.output.iterdir()) if p.is_file() and p.name != "manifest.json"})
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
