#!/usr/bin/env python3
"""Finite reaction paths, prepared photons, shared supports and loss exposure."""
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

from adm_harness.finite_reaction_transport import inverse_filter_certificate, simulate_finite_branch

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "supporting_reports/data"
PARENTS = ("coupled_rail_reactions", "scheduled_optical_transfer", "shared_rail_reactions")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified(group, name):
    path = DATA / group / name
    if sha256(path) != json.loads((DATA / group / "manifest.json").read_text())["output_sha256"][name]:
        raise ValueError(f"Parent evidence mismatch: {path}")
    return path


def trial(task):
    name, context, direction, options, output = task
    left, right = (0., 1.) if direction == "up" else (1., 0.)
    r = simulate_finite_branch(left, right, context, **options)
    maximum_error = float(np.max(abs(r["complete_ledger_error"])))
    minimum_wave, minimum_incident = float(r["minimum_emitted_power"].min()), float(r["incident_margin"].min())
    if max(maximum_error, float(np.max(abs(r["output_balance_error"])))) > 2e-8 or min(minimum_wave, minimum_incident) < -1e-10:
        raise ValueError(f"Finite branch admission failed: {name}")
    # Retain a compact service record and every measured point near the receipt jumps.
    step = float(r["time"][1]-r["time"][0])
    stride = max(1, int(.04/step))
    selection = np.unique(np.r_[np.arange(0, len(r["time"]), stride),
                                np.flatnonzero((r["time"] >= -3) & (r["time"] <= 4)), len(r["time"])-1])
    keys = ("time", "state", "rotor_power", "support_power", "support_energy", "total_trace",
            "dynamic_trace", "modulation", "bias", "photon_energy", "photon_energy_rate",
            "minimum_emitted_power", "incident_margin", "thermal_energy", "complete_ledger_error")
    np.savez_compressed(Path(output) / (name+"_states.npz"),
                        **{key: r[key][..., selection] for key in keys})
    row = dict(name=name, context=context["name"], direction=direction, options=options,
        evaluated_points=len(r["time"]), archived_points=len(selection), evaluation_time_step=step,
        sampled_minimum_spin=float(r["state"][2].min()), final_state=r["state"][:, -1].tolist(),
        maximum_thermal_energy=float(r["thermal_energy"].max()),
        maximum_absolute_rotor_power=float(np.max(abs(r["rotor_power"]))),
        maximum_absolute_support_power=float(np.max(abs(r["support_power"]))),
        maximum_absolute_modulation=float(np.max(abs(r["modulation"]))),
        maximum_modulation_over_bias=float(np.max(abs(r["modulation"])/r["bias"])),
        maximum_photon_energy=float(r["photon_energy"].max()),
        maximum_absolute_dynamic_trace=float(np.max(abs(r["dynamic_trace"]))),
        initial_photon_energy=r["initial_photon_energy"], initial_support_energy=r["initial_support_energy"],
        additional_continuous_energy_ceiling=r["additional_continuous_energy_ceiling"],
        final_rotor_input_l2=float(r["rotor_input_l2"][-1]),
        final_support_work_throughput=float(r["support_work_throughput"][-1]),
        emitted_branch_energy=float(r["emitted_energy"][-1]),
        two_endpoint_optical_exposure=2*float(r["emitted_energy"][-1]),
        minimum_emitted_stream_power=minimum_wave, minimum_incident_margin=minimum_incident,
        maximum_complete_ledger_error=maximum_error,
        maximum_coupled_ledger_error=float(np.max(abs(r["coupled_ledger_error"]))),
        maximum_source_power_error=float(np.max(abs(r["source_power_error"]))),
        maximum_support_power_error=float(np.max(abs(r["support_power_error"]))),
        maximum_output_balance_error=float(np.max(abs(r["output_balance_error"]))))
    print(name, "spin", row["sampled_minimum_spin"], "wave floor", minimum_wave,
          "ledger", maximum_error, flush=True)
    return row


def history(task):
    name, output = task
    sources = [verified("scheduled_optical_transfer", name+"_states.npz"),
               verified("shared_rail_reactions", name+"_reactions.npz")]
    alpha, peak, pilot, ell = .62e-6, 1.2, .001, 1/64
    with np.load(sources[0]) as s, np.load(sources[1]) as r:
        # Every photon meets an emission and a receiving endpoint. The old
        # converter envelope supplies a conservative bound on event windows.
        additional = 4*pilot*s["nominal_guide_exposure"]+4*peak/5*s["loop_exposure_upper"]
        line_cost = 6*ell*peak*s["capacity"]
        reserve = (s["all_panel_reserve_lower_bound"]-r["continuous_additional_energy_ceiling"][None]
            -line_cost[None]-alpha*(s["finite_loop_total_exposure_upper"]+additional)/(1-alpha/.3))
        if reserve.min() <= 0:
            raise ValueError(f"Finite path energy screen fails: {name}")
        np.savez_compressed(Path(output) / (name+"_energy_screen.npz"), x=s["x"],
            capacity=s["capacity"], additional_path_and_support_ceiling=line_cost,
            minimum_reserve=reserve.min(axis=0), final_additional_endpoint_exposure=additional[-1])
    row = dict(label=name, input_sha256={str(p.relative_to(ROOT)): sha256(p) for p in sources},
        minimum_energy_reserve=float(reserve.min()), maximum_additional_preparation=float(line_cost.max()),
        maximum_final_additional_endpoint_exposure=float(additional[-1].max()),
        added_path_and_support_cost_over_C=6*ell*peak,
        inherited_transfer_loss_fraction=alpha,
        full_history_commands_and_transducer_losses_included=False)
    print(name, "finite path energy margin", row["minimum_energy_reserve"], flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=DATA / "finite_reaction_transport")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("positive worker count required")
    args.output.mkdir(parents=True, exist_ok=True)
    parents = {g: json.loads(verified(g, "summary.json").read_text()) for g in PARENTS}
    for group in PARENTS:
        manifest = json.loads((DATA / group / "manifest.json").read_text())
        for name, digest in manifest["runtime_sha256"].items():
            if sha256(ROOT / name) != digest:
                raise ValueError(f"Parent implementation changed: {name}")
    contexts = [c for c in parents["coupled_rail_reactions"]["contexts"] if c["name"] in ("first_high", "second_low")]
    first = next(c for c in contexts if c["name"] == "first_high")
    tasks = [(c["name"]+"_"+d, c, d, {}, str(args.output)) for c in contexts for d in ("up", "down")]
    tasks += [(f"first_high_up_delay_{denominator}", first, "up", dict(short_delay=1/denominator), str(args.output))
              for denominator in (16, 256)]
    tasks += [("first_high_"+d+"_refined", first, d,
               dict(samples_per_delay=8, maximum_step=.06, rtol=5e-10, atol=5e-12), str(args.output))
              for d in ("up", "down")]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        histories = list(pool.map(history, [(h["label"], str(args.output)) for h in parents["scheduled_optical_transfer"]["histories"]]))
        trials = list(pool.map(trial, tasks))
    refinements = []
    for refined in (t for t in trials if t["name"].endswith("_refined")):
        base = next(t for t in trials if t["name"] == refined["name"].removesuffix("_refined"))
        error = float(np.max(abs(np.array(base["final_state"])-refined["final_state"])))
        l2_error = abs(base["final_rotor_input_l2"]-refined["final_rotor_input_l2"])
        if max(error, l2_error) > 1e-7:
            raise ValueError("Finite-path refinement tolerance exceeded")
        refinements.append(dict(name=refined["name"], final_state_error=error, rotor_input_l2_error=l2_error,
            sampled_spin_minimum_change=abs(base["sampled_minimum_spin"]-refined["sampled_minimum_spin"])))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        inverse_filter_certificate=inverse_filter_certificate(), contexts=contexts,
        histories=histories, trials=trials, refinements=refinements,
        finite_work_propagation_included=True, photon_stress_and_support_work_included=True,
        prepared_bidirectional_pilot=True, prescribed_synchronized_endpoint_commands=True,
        distributed_feedback_controller_constructed=False, frozen_macro_support=True,
        mechanical_transducer_constructed=False, local_traction_propagation_constructed=False,
        whole_history_coupled_heat_certificate=False, standing_field_holding_losses_included=False)
    (args.output / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(), ROOT / "toolkit/adm_harness_cli/adm_harness/finite_reaction_transport.py",
             ROOT / "toolkit/adm_harness_cli/tests/test_finite_reaction_transport.py"]
    for path in paths:
        shutil.copyfile(path, args.output / ("execution_"+path.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        parent_manifest_sha256={str((DATA / g / "manifest.json").relative_to(ROOT)):
            sha256(DATA / g / "manifest.json") for g in PARENTS},
        output_sha256={p.name: sha256(p) for p in sorted(args.output.iterdir()) if p.is_file() and p.name != "manifest.json"})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
