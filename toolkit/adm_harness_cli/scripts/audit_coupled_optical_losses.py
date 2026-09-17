#!/usr/bin/env python3
"""Evaluate coupled encounters, retained rotor absorption, and energy allowances."""
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

from adm_harness.constitutive_joints_and_optics import series_panel_state, series_power_bounds
from adm_harness.coupled_optical_losses import (
    ROTOR_L1_GAIN, absorption_gain, effective_input_l1_bounds,
    energy_only_replacement, retained_rotor_heat_bound, rotor_absorption_ceiling,
)
from adm_harness.scheduled_optical_transfer import SPIN_FLOOR, preparation, receipt_derivative_bound

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "supporting_reports/data"
PARENTS = ("coupled_holding_certificate", "scheduled_optical_transfer",
           "controlled_optical_transfer", "constitutive_joints_and_optics",
           "material_reconfiguration")
ABSORPTION = .62e-6
ENCOUNTER_LOSS = .62e-6


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified(group, name):
    directory = DATA / group
    path = directory / name
    expected = json.loads((directory / "manifest.json").read_text())["output_sha256"][name]
    if sha256(path) != expected:
        raise ValueError(f"Parent evidence mismatch: {path}")
    return path


def history(task):
    name, output = task
    paths = [verified(g, name+("_certificate.npz" if g == PARENTS[0] else "_states.npz"))
             for g in PARENTS]
    with np.load(paths[0]) as c, np.load(paths[1]) as a, np.load(paths[2]) as p, \
            np.load(paths[3]) as j, np.load(paths[4]) as m:
        for parent in (c, p, j, m):
            for key in ("t", "x"):
                np.testing.assert_array_equal(a[key], parent[key])
        args = (j["effective_material_tension"], j["material_inventory"],
                j["joint_inventory_per_direction"], j["component_energy"][12:16],
                m["target"], m["lr"], m["lt"], m["proper_panel_duration"])
        powers = np.maximum(series_power_bounds(*args)["upper"], 0)
        left, right = (series_panel_state(*args, f)["power"] for f in (0., 1.))
        derivative = receipt_derivative_bound(*args)
        bounds = effective_input_l1_bounds(powers, left, right, derivative,
            p["node_peak_power"], m["proper_panel_duration"], p["transit_delay"],
            c["panel_baseline_power_upper"])
        np.testing.assert_array_equal(bounds["events"][:, -1], c["finite_line_events"])
        capacity, Cnode = a["capacity"], p["reception_capacity"]
        active = Cnode > 0
        np.testing.assert_allclose(Cnode.sum(axis=0), capacity, rtol=2e-14)
        rotor = (ROTOR_L1_GAIN/SPIN_FLOOR*(1+absorption_gain(ABSORPTION))
                 *(Cnode[:, None]*bounds["effective"]).sum(axis=0))
        # Preserve guide, useful flight, converter recirculation and new
        # reaction endpoints. Replace both old converter-net and restart
        # terms with the L1 bound that already includes loop fill/drain.
        fixed = (3*a["guide_upper"]+a["useful_upper"]+a["loop_exposure_upper"]
                 +c["additional_line_endpoint_exposure_upper"])
        exposure = fixed+rotor
        legacy = a["finite_loop_total_exposure_upper"]+c["additional_line_endpoint_exposure_upper"]
        replacement_gain = ROTOR_L1_GAIN*(1+absorption_gain(ABSORPTION))/SPIN_FLOOR
        allowance = energy_only_replacement(exposure, ENCOUNTER_LOSS, feedback_gain=replacement_gain)
        parent_summary = json.loads(verified(PARENTS[0], "summary.json").read_text())
        parent_history = next(h for h in parent_summary["histories"] if h["label"] == name)
        values = dict(t=a["t"], x=a["x"], capacity=capacity, node_capacity=Cnode,
            node_effective_input_l1_upper=bounds["effective"],
            node_final_receipt_l1_upper=bounds["receipt"][:, -1],
            node_final_guide_l1_upper=bounds["guide"][:, -1],
            node_final_converter_l1_upper=bounds["converter"][:, -1],
            node_final_reaction_line_l1_upper=bounds["reaction_line"][:, -1],
            node_final_guide_trace_l1_upper=bounds["guide_trace"][:, -1],
            node_final_baseline_l1_upper=bounds["baseline"][:, -1],
            rotor_encounter_exposure_upper=rotor, fixed_encounter_exposure_upper=fixed,
            total_encounter_exposure_upper=exposure, legacy_exposure_upper=legacy,
            replacement_energy_allowance=allowance)
        variants = []
        for variant in parent_history["inventory_variants"]:
            mass = variant["inventory"]
            prefix = f"mass{mass:g}_"
            b0 = c[prefix+"thermal_action_upper"]
            capacity_b = c[prefix+"thermal_action_capacity"]
            babs = retained_rotor_heat_bound(bounds["effective"][:, -1],
                                             absorption=ABSORPTION, inventory=mass)
            spin2 = c[prefix+"spin_squared_lower"]-2*babs
            ceilings = rotor_absorption_ceiling(bounds["effective"][:, -1],
                                                capacity_b[None]-b0, inventory=mass)
            charge = (preparation(inventory=mass)["candidate_preparation"]
                      -preparation()["candidate_preparation"]
                      +variant["support_and_line_energy_ceiling"])
            reserve = a["all_panel_reserve_lower_bound"]-charge*capacity[None]-allowance
            values.update({prefix+"absorption_action_upper": babs,
                           prefix+"spin_squared_lower_with_absorption": spin2,
                           prefix+"rest_frame_absorption_ceiling": ceilings,
                           prefix+"reserve_after_replacement_allowance": reserve})
            checks = dict(variant["checks"])
            checks["thermal_spin_with_rotor_absorption"] = bool(np.all(spin2[active] > SPIN_FLOOR**2))
            checks["revised_energy_allowance"] = bool(np.all(reserve > 0))
            minimum_spin2 = float(spin2[active].min())
            variants.append(dict(inventory=mass, checks=checks,
                conditional_absorption_and_energy_screen_passed=all(checks.values()),
                maximum_absorption_action_bound=float(babs[active].max()),
                maximum_combined_thermal_action_bound=float((b0+babs)[active].max()),
                minimum_spin_squared_lower=minimum_spin2,
                minimum_spin_lower=float(np.sqrt(minimum_spin2)) if minimum_spin2 > 0 else None,
                minimum_rest_frame_absorption_ceiling=float(ceilings[active].min()),
                minimum_reserve_after_replacement_allowance=float(reserve.min())))
    np.savez_compressed(Path(output) / (name+"_losses.npz"), **values)
    row = dict(label=name,
        input_sha256={str(path.relative_to(ROOT)): sha256(path) for path in paths},
        final_exposure_range=[float(exposure[-1].min()), float(exposure[-1].max())],
        legacy_final_exposure_range=[float(legacy[-1].min()), float(legacy[-1].max())],
        maximum_final_exposure_ratio=float((exposure[-1]/legacy[-1]).max()),
        maximum_final_rotor_exposure=float(rotor[-1].max()),
        maximum_final_effective_l1=float(bounds["effective"][:, -1][active].max()),
        maximum_replacement_energy_allowance=float(allowance[-1].max()),
        inventory_variants=variants)
    print(name, [(v["inventory"], v["minimum_spin_lower"],
                  v["minimum_reserve_after_replacement_allowance"]) for v in variants], flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=DATA / "coupled_optical_losses")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    for group in PARENTS:
        manifest = json.loads((DATA / group / "manifest.json").read_text())
        for path, digest in manifest["runtime_sha256"].items():
            if sha256(ROOT / path) != digest:
                raise ValueError(f"Parent implementation changed: {path}")
    parent = json.loads(verified(PARENTS[0], "summary.json").read_text())
    if parent["input_l1_certificate"]["rotor_to_effective_network_l1_gain"] != ROTOR_L1_GAIN:
        raise ValueError("L1 constant differs from the exact certificate")
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        histories = list(pool.map(history, [(h["label"], str(args.output)) for h in parent["histories"]]))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__),
        rest_frame_rotor_absorption_fraction=ABSORPTION, assigned_common_encounter_loss=ENCOUNTER_LOSS,
        rotor_l1_gain=ROTOR_L1_GAIN, histories=histories,
        rotor_heat_retained_in_existing_thermal_state=True,
        transfer_to_zero_angular_momentum_bath_assumed=True,
        physical_facet_to_bath_interface_constructed=False,
        rotor_net_power_prescribed_in_absorbing_port_law=True,
        rotor_energy_and_radial_dynamics_preserved_by_absorption_torque_split=True,
        new_rotor_encounter_envelope_included=True,
        other_component_loss_replacement_is_energy_allowance=True,
        other_component_heat_hosts_and_routing_constructed=False,
        finite_line_and_converter_endpoint_history_positivity_closed=False,
        physical_mirror_material_and_absorption_spectrum_identified=False,
        complete_physical_rail_feasibility_established=False)
    (args.output / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(), ROOT / "toolkit/adm_harness_cli/adm_harness/coupled_optical_losses.py",
             ROOT / "toolkit/adm_harness_cli/tests/test_coupled_optical_losses.py"]
    for path in paths:
        shutil.copyfile(path, args.output / ("execution_"+path.name))
    manifest = dict(runtime_sha256={str(path.relative_to(ROOT)): sha256(path) for path in paths},
        parent_manifest_sha256={str((DATA / g / "manifest.json").relative_to(ROOT)):
            sha256(DATA / g / "manifest.json") for g in PARENTS},
        output_sha256={path.name: sha256(path) for path in sorted(args.output.iterdir())
                       if path.is_file() and path.name != "manifest.json"})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
