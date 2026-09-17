#!/usr/bin/env python3
"""Four-history conditional budget for finite paired thermal routes."""
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

from adm_harness.coupled_optical_losses import energy_only_replacement
from adm_harness.finite_thermal_budget import finite_heat_history
from adm_harness.scheduled_optical_transfer import preparation
from adm_harness.thermal_exchange_interfaces import passive_absorption_gain

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "supporting_reports/data"
PARENTS = ("coupled_holding_certificate", "coupled_optical_losses", "scheduled_optical_transfer",
           "thermal_exchange_interfaces")
ABSORPTION, COMMON_LOSS = .62e-6, .62e-6
THERMAL_ROUTE_ENCOUNTERS = 8
FLIGHT_DELAY = 1/64


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
             ("_certificate.npz", "_losses.npz", "_states.npz"))]
    parent = json.loads(verified(PARENTS[0], "summary.json").read_text())
    parent_history = next(h for h in parent["histories"] if h["label"] == name)
    with np.load(paths[0]) as c, np.load(paths[1]) as x, np.load(paths[2]) as a:
        for other in (c, x):
            for key in ("t", "x"):
                np.testing.assert_array_equal(a[key], other[key])
        Cnode, capacity = x["node_capacity"], x["capacity"]
        active = Cnode > 0
        values = dict(t=a["t"], x=a["x"], capacity=capacity, node_capacity=Cnode)
        variants = []
        for mass in (19., 20.):
            prefix = f"mass{mass:g}_"
            result = finite_heat_history(x["node_effective_input_l1_upper"][:, -1],
                c["node_forcing_l2_upper"], c[prefix+"energy_floor"], c[prefix+"energy_ceiling"],
                c[prefix+"reduced_input_peak_upper"], inventory=mass, absorption=ABSORPTION,
                flight_delay=FLIGHT_DELAY)
            np.testing.assert_allclose(result["passive_heat_gain"],
                                       passive_absorption_gain(ABSORPTION), rtol=3e-15)
            cumulative_ql1 = result["port_l1_gain"]*x["node_effective_input_l1_upper"]
            rotor_exposure = result["port_exposure_per_power"]*(Cnode[:, None]*cumulative_ql1).sum(axis=0)
            thermal_exposure = THERMAL_ROUTE_ENCOUNTERS*result["passive_heat_gain"]*(
                Cnode[:, None]*cumulative_ql1).sum(axis=0)
            exposure = x["fixed_encounter_exposure_upper"]+rotor_exposure+thermal_exposure
            feedback = result["port_l1_gain"]*(result["port_exposure_per_power"]
                       +THERMAL_ROUTE_ENCOUNTERS*result["passive_heat_gain"])
            allowance = energy_only_replacement(exposure, COMMON_LOSS, feedback_gain=feedback)
            original = next(v for v in parent_history["inventory_variants"] if v["inventory"] == mass)
            state_cost = (preparation(inventory=mass)["candidate_preparation"]
                -preparation()["candidate_preparation"]+original["support_and_line_energy_ceiling"]
                +result["additional_state_energy_ceiling"])
            reserve = a["all_panel_reserve_lower_bound"]-state_cost*capacity[None]-allowance
            for key, value in result.items():
                if isinstance(value, np.ndarray):
                    values[prefix+key] = value
            values.update({prefix+"encounter_exposure_upper": exposure,
                           prefix+"thermal_route_exposure_upper": thermal_exposure,
                           prefix+"reserve_after_replacement_allowance": reserve})
            checks = dict(radial_domain=bool(np.all(result["invariant_domain_passed"])),
                spin=bool(np.all(result["thermal_spin_passed"][active])),
                energy_allowance=bool(np.all(reserve > 0)))
            spin2 = float(result["spin_squared_lower"][active].min())
            variants.append(dict(inventory=mass, checks=checks,
                conditional_finite_thermal_screen_passed=all(checks.values()),
                minimum_spin_lower=float(np.sqrt(spin2)) if spin2 > 0 else None,
                maximum_absorption_action_bound=float(result["absorption_action_upper"][active].max()),
                maximum_damping_action_bound=float(result["damping_action_upper"][active].max()),
                maximum_combined_action_bound=float((result["damping_action_upper"]
                                                    +result["absorption_action_upper"])[active].max()),
                minimum_energy_floor=float(result["energy_floor"].min()),
                maximum_reduced_input_bound=float(result["reduced_input_peak"].max()),
                maximum_final_thermal_route_exposure=float(thermal_exposure[-1].max()),
                minimum_reserve_after_replacement_allowance=float(reserve.min()),
                **{k: v for k, v in result.items() if not isinstance(v, np.ndarray) and k != "inventory"}))
    np.savez_compressed(Path(output) / (name+"_thermal_budget.npz"), **values)
    row = dict(label=name, input_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
               inventory_variants=variants)
    print(name, [(v["inventory"], v["minimum_spin_lower"],
                  v["minimum_reserve_after_replacement_allowance"]) for v in variants], flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=DATA / "finite_thermal_budget")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    for group in PARENTS:
        for path, digest in json.loads((DATA / group / "manifest.json").read_text())["runtime_sha256"].items():
            if sha256(ROOT / path) != digest:
                raise ValueError(f"Parent implementation changed: {path}")
    parent = json.loads(verified(PARENTS[0], "summary.json").read_text())
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        histories = list(pool.map(history, [(h["label"], str(args.output)) for h in parent["histories"]]))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__),
        histories=histories, thermal_route_encounters_per_transferred_energy=THERMAL_ROUTE_ENCOUNTERS,
        matched_equal_delay_ports_assumed=True, additional_flight_energy_and_pressure_allocated=True,
        zero_additional_collector_work_assumed=True,
        three_axis_isotropic_route_partition_assumed=True,
        passive_opposed_emitter_heat_factor_included=True,
        radial_damping_response_to_thermal_flight_included=True,
        moving_collector_work_and_variable_delay_constructed=False,
        thermal_bath_host_and_holding_loss_law_identified=False,
        other_component_replacement_is_energy_allowance=True,
        complete_physical_rail_feasibility_established=False)
    (args.output / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(), ROOT / "toolkit/adm_harness_cli/adm_harness/finite_thermal_budget.py",
             ROOT / "toolkit/adm_harness_cli/tests/test_finite_thermal_budget.py"]
    for path in paths:
        shutil.copyfile(path, args.output / ("execution_"+path.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        parent_manifest_sha256={str((DATA / g / "manifest.json").relative_to(ROOT)):
            sha256(DATA / g / "manifest.json") for g in PARENTS},
        output_sha256={p.name: sha256(p) for p in sorted(args.output.iterdir())
                       if p.is_file() and p.name != "manifest.json"})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
