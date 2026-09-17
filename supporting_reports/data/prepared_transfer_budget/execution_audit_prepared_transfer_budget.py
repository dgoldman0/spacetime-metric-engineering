#!/usr/bin/env python3
"""Combine prepared endpoint pilots, finite thermal flight, and encounter costs."""
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

from adm_harness.coupled_optical_losses import absorption_gain, energy_only_replacement
from adm_harness.prepared_transfer_budget import (
    apply_pilot_preparation, cold_preparation, thermal_endpoint_perturbation,
)
from adm_harness.reaction_endpoint_certificate import PHOTON_PEAK, SHORT_DELAY

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "supporting_reports/data"
PARENTS = ("reaction_endpoint_certificate", "finite_thermal_budget",
           "scheduled_optical_transfer", "coupled_holding_certificate")
COMMON_LOSS = .62e-6


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified(group, name):
    path = DATA / group / name
    expected = json.loads((DATA / group / "manifest.json").read_text())["output_sha256"][name]
    if sha256(path) != expected:
        raise ValueError(f"Parent evidence mismatch: {path}")
    return path


def history(task):
    name, output = task
    paths = [verified(g, name+suffix) for g, suffix in zip(PARENTS,
        ("_endpoints.npz", "_thermal_budget.npz", "_states.npz", "_certificate.npz"))]
    summaries = [json.loads(verified(g, "summary.json").read_text()) for g in PARENTS]
    endpoint_history = next(h for h in summaries[0]["histories"] if h["label"] == name)
    thermal_history = next(h for h in summaries[1]["histories"] if h["label"] == name)
    coupled_history = next(h for h in summaries[3]["histories"] if h["label"] == name)
    with np.load(paths[0]) as e, np.load(paths[1]) as h, np.load(paths[2]) as s, np.load(paths[3]) as c:
        for other in (h, s, c):
            for key in ("t", "x"):
                np.testing.assert_array_equal(e[key], other[key])
        capacity, active = e["node_capacity"], e["node_capacity"] > 0
        extra = e["additional_pilot_endpoint_exposure_upper"][1:]
        arrays = dict(t=e["t"], x=e["x"], node_capacity=capacity, capacity=e["capacity"],
                      additional_pilot_endpoint_exposure_upper=extra,
                      reaction_pilot=e["proposed_pilot"], main_loop_pilot=s["loop_baseline_power_over_peak"])
        rows = []
        for mass in (19., 20.):
            prefix = f"mass{mass:g}_"
            thermal = next(v for v in thermal_history["inventory_variants"] if v["inventory"] == mass)
            coupled = next(v for v in coupled_history["inventory_variants"] if v["inventory"] == mass)
            update = apply_pilot_preparation(h[prefix+"energy_floor"], h[prefix+"spin_squared_lower"],
                e[prefix+"revised_energy_floor"], e[prefix+"revised_energy_ceiling"],
                thermal_state_ceiling=thermal["additional_state_energy_ceiling"], inventory=mass)
            initial_total = e["initial_support_energy_over_C"]+e["initial_line_energy_over_C"]
            preparation_margin = coupled["support_and_line_energy_ceiling"]-initial_total
            preparation_rows = []
            for plateau in (0., 1.):
                prep = cold_preparation(plateau, s["loop_baseline_power_over_peak"], inventory=mass)
                preparation_rows.append(dict(plateau=plateau,
                    minimum_rotor_energy=float(prep["energy"][active].min()),
                    maximum_rotor_energy=float(prep["energy"][active].max()),
                    minimum_spin=float(prep["spin"][active].min())))
            feedback = thermal["port_l1_gain"]*(thermal["port_exposure_per_power"]
                +summaries[1]["thermal_route_encounters_per_transferred_energy"]*thermal["passive_heat_gain"])
            extra_loss = energy_only_replacement(extra, COMMON_LOSS, feedback_gain=feedback)
            reserve = h[prefix+"reserve_after_replacement_allowance"]-extra_loss
            perturbation = thermal_endpoint_perturbation(inventory=mass, absorption=thermal["absorption"],
                                                         flight_delay=thermal["flight_delay"])
            emitted = min(ev["minimum_emitted_margin"] for ev in summaries[0]["events"])-perturbation["emitted_margin_debit"]
            incident = min(ev["minimum_incident_margin_after_allowance"] for ev in summaries[0]["events"])-perturbation["incident_margin_debit"]
            allowed_absorption = min(ev["allowed_extra_encounter_fraction"] for ev in summaries[0]["events"])
            xi = float(absorption_gain(thermal["absorption"]))
            # A thermal perturbation also slightly changes the qpeak used to
            # reserve incident power for the imperfect optical reflection.
            largest_q = max(ev["maximum_event_rotor_power"] for ev in summaries[0]["events"])
            imperfect_extra = xi*perturbation["support_power_increment"]/.6
            incident -= imperfect_extra
            checks = dict(parent_endpoints=endpoint_history["passed"],
                energy_domain=bool(np.all(update["energy_domain_passed"][active])),
                thermal_spin=bool(np.all(update["spin_passed"][active])),
                parent_forcing_domain=thermal["checks"]["radial_domain"],
                prepared_state_counted=bool(np.all(preparation_margin[active] > 0)),
                reaction_photon_capacity=bool(np.all(e["initial_line_energy_over_C"][active] <= 3*SHORT_DELAY*PHOTON_PEAK)),
                thermal_endpoint_perturbation=bool(emitted > 0 and incident > 0),
                rotor_absorption_incident_allowance=bool(xi < allowed_absorption),
                energy_allowance=bool(np.all(reserve > 0)))
            for key, value in update.items():
                arrays[prefix+key] = value
            arrays[prefix+"additional_pilot_loss_allowance"] = extra_loss
            arrays[prefix+"reserve_after_all_counted_allowances"] = reserve
            rows.append(dict(inventory=mass, conditional_combined_screen_passed=all(checks.values()),
                checks=checks, minimum_spin_lower=float(np.sqrt(update["spin_squared_lower"][active].min())),
                minimum_energy_floor=float(update["energy_floor"][active].min()),
                maximum_energy_ceiling=float(update["energy_ceiling"][active].max()),
                minimum_prepared_state_margin=float(preparation_margin[active].min()),
                minimum_energy_reserve=float(reserve.min()), maximum_extra_pilot_loss=float(extra_loss.max()),
                minimum_emitted_margin=emitted, minimum_incident_margin=incident,
                maximum_event_rotor_power_with_thermal_perturbation=largest_q+perturbation["support_power_increment"],
                rotor_absorption_extra_encounter_fraction=xi,
                thermal_endpoint_perturbation=perturbation, cold_preparation_envelopes=preparation_rows))
        if not all(row["conditional_combined_screen_passed"] for row in rows):
            raise ValueError(f"Combined prepared transfer screen failed: {name}: {rows}")
    np.savez_compressed(Path(output)/(name+"_prepared_budget.npz"), **arrays)
    print(name, [(r["inventory"], r["minimum_spin_lower"], r["minimum_energy_reserve"]) for r in rows], flush=True)
    return dict(label=name, input_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
                maximum_extra_pilot_exposure=float(extra.max()), inventory_variants=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=DATA / "prepared_transfer_budget")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    for group in PARENTS:
        for path, digest in json.loads((DATA / group / "manifest.json").read_text())["runtime_sha256"].items():
            if sha256(ROOT / path) != digest:
                raise ValueError(f"Parent runtime changed: {path}")
    parent = json.loads(verified(PARENTS[0], "summary.json").read_text())
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        histories = list(pool.map(history, [(h["label"], str(args.output)) for h in parent["histories"]]))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__), histories=histories,
        main_converter_initial_pilot_paid_from_existing_rotor_energy=True,
        reaction_initial_pilot_within_counted_state_ceiling=True,
        finite_thermal_forcing_in_endpoint_comparison=True,
        maximum_reaction_flight_inventory_unchanged=True,
        assigned_loss_coefficient=COMMON_LOSS,
        guide_work_and_variable_thermal_delay_included=False,
        electrical_lead_and_converter_host_inventories_included=False,
        other_component_loss_replacement_waveforms_constructed=False,
        lossless_work_route_endpoint_theorem=True,
        prescribed_feedforward_commands=True,
        complete_physical_rail_feasibility_established=False)
    (args.output/"summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(), ROOT/"toolkit/adm_harness_cli/adm_harness/prepared_transfer_budget.py",
             ROOT/"toolkit/adm_harness_cli/tests/test_prepared_transfer_budget.py"]
    for path in paths:
        shutil.copyfile(path, args.output/("execution_"+path.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        parent_manifest_sha256={str((DATA/g/"manifest.json").relative_to(ROOT)):
            sha256(DATA/g/"manifest.json") for g in PARENTS},
        output_sha256={p.name: sha256(p) for p in sorted(args.output.iterdir())
                       if p.is_file() and p.name != "manifest.json"})
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
