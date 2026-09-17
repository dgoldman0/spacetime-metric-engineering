#!/usr/bin/env python3
"""Price moving thermal collection and finite optical work leads in four histories."""
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

from adm_harness.coupled_holding_certificate import C_MAX, ISS_DECAY
from adm_harness.coupled_optical_losses import absorption_gain, energy_only_replacement
from adm_harness.moving_thermal_budget import moving_heat_history
from adm_harness.reaction_endpoint_certificate import (
    CHI_UPPER, INVERSE_L1, LINE_RATE_GAIN, WEIGHTED_TRACE_DUAL,
)
from adm_harness.scheduled_optical_transfer import SPIN_FLOOR, preparation

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT/"supporting_reports/data"
PARENTS = ("coupled_holding_certificate", "coupled_optical_losses",
    "scheduled_optical_transfer", "reaction_endpoint_certificate",
    "prepared_transfer_budget", "moving_thermal_relay")
ABSORPTION = COMMON_LOSS = .62e-6


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified(group, name):
    path = DATA/group/name
    digest = json.loads((DATA/group/"manifest.json").read_text())["output_sha256"][name]
    if sha256(path) != digest:
        raise ValueError(f"Parent output changed: {path}")
    return path


def history(task):
    name, output = task
    paths = [verified(g, name+s) for g, s in zip(PARENTS,
        ("_certificate.npz", "_losses.npz", "_states.npz", "_endpoints.npz", "_prepared_budget.npz"))]
    coupled = json.loads(verified(PARENTS[0], "summary.json").read_text())
    base_history = next(h for h in coupled["histories"] if h["label"] == name)
    endpoint = json.loads(verified(PARENTS[3], "summary.json").read_text())
    with np.load(paths[0]) as c, np.load(paths[1]) as x, np.load(paths[2]) as s, np.load(paths[3]) as e, np.load(paths[4]) as p:
        for other in (x, s, e, p):
            for key in ("x", "t"):
                np.testing.assert_array_equal(c[key], other[key])
        Cnode, capacity = x["node_capacity"], x["capacity"]
        active = Cnode > 0
        values = dict(t=c["t"], x=c["x"], node_capacity=Cnode, capacity=capacity)
        variants = []
        for mass in (19., 20.):
            prefix = f"mass{mass:g}_"
            b = moving_heat_history(x["node_effective_input_l1_upper"][:, -1], c["node_forcing_l2_upper"],
                e[prefix+"revised_energy_floor"], e[prefix+"revised_energy_ceiling"],
                c[prefix+"reduced_input_peak_upper"], inventory=mass, absorption=ABSORPTION)
            ql1 = b["port_l1_gain"]*x["node_effective_input_l1_upper"]
            total_ql1 = (Cnode[:, None]*ql1).sum(axis=0)
            exposure = (x["fixed_encounter_exposure_upper"]
                +(b["port_exposure_per_power"]+b["thermal_and_work_encounters_per_port_l1"])*total_ql1
                +p["additional_pilot_endpoint_exposure_upper"])
            feedback = b["port_l1_gain"]*(b["port_exposure_per_power"]+b["thermal_and_work_encounters_per_port_l1"])
            loss = energy_only_replacement(exposure, COMMON_LOSS, feedback_gain=feedback)
            parent = next(v for v in base_history["inventory_variants"] if v["inventory"] == mass)
            state_cost = (preparation(inventory=mass)["candidate_preparation"]-preparation()["candidate_preparation"]
                +parent["support_and_line_energy_ceiling"]+b["additional_state_energy_ceiling"])
            reserve = s["all_panel_reserve_lower_bound"]-state_cost*capacity[None]-loss
            E = CHI_UPPER*(1+C_MAX)/ISS_DECAY*b["total_flight_rate_peak"]
            dP = WEIGHTED_TRACE_DUAL*E+LINE_RATE_GAIN*b["total_flight_rate_peak"]
            da = INVERSE_L1*dP
            Kplus = (1+SPIN_FLOOR)/(2*SPIN_FLOOR)
            emitter = min(ev["minimum_emitted_margin"] for ev in endpoint["events"])-da
            # qport=qsource-Premote; an incoming remote photon branch also
            # consumes splitting capacity while its return is in flight.
            incident_debit = da+Kplus*(dP+b["remote_work_net_power_peak"])+b["remote_work_incident_power_peak"]
            xi = float(absorption_gain(ABSORPTION))
            incident_debit += xi*(dP+b["remote_work_net_power_peak"])/(2*SPIN_FLOOR)
            incident = min(ev["minimum_incident_margin_after_allowance"] for ev in endpoint["events"])-incident_debit
            checks = dict(invariant_domain=bool(np.all(b["invariant_domain_passed"][active])),
                thermal_spin=bool(np.all(b["thermal_spin_passed"][active])),
                endpoint_emission=bool(emitter > 0), endpoint_incidence=bool(incident > 0),
                energy_allowance=bool(np.all(reserve > 0)))
            for key, value in b.items():
                if isinstance(value, np.ndarray):
                    values[prefix+key] = value
            values[prefix+"reserve_after_all_counted_allowances"] = reserve
            values[prefix+"encounter_exposure_upper"] = exposure
            variants.append(dict(inventory=mass, checks=checks, conditional_moving_relay_screen_passed=all(checks.values()),
                minimum_spin_lower=float(np.sqrt(b["spin_squared_lower"][active].min())),
                minimum_energy_reserve=float(reserve.min()),
                maximum_reserve_debit_relative_to_frozen_relay=float((p[prefix+"reserve_after_all_counted_allowances"]-reserve).max()),
                minimum_emitted_margin=emitter, minimum_incident_margin=incident,
                tracking_state_increment=E, support_power_increment=dP,
                maximum_total_heat_action=float((b["damping_action_upper"]+b["absorption_action_upper"])[active].max()),
                **{key: value for key, value in b.items() if not isinstance(value, np.ndarray) and key != "inventory"}))
        if not all(v["conditional_moving_relay_screen_passed"] for v in variants):
            raise ValueError(f"Moving relay budget failed: {name}: {variants}")
    np.savez_compressed(Path(output)/(name+"_moving_budget.npz"), **values)
    print(name, [(v["inventory"], v["minimum_spin_lower"], v["minimum_energy_reserve"]) for v in variants], flush=True)
    return dict(label=name, input_sha256={str(path.relative_to(ROOT)): sha256(path) for path in paths},
                inventory_variants=variants)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=DATA/"moving_thermal_budget")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    for group in PARENTS:
        for path, digest in json.loads((DATA/group/"manifest.json").read_text())["runtime_sha256"].items():
            if sha256(ROOT/path) != digest:
                raise ValueError(f"Parent implementation changed: {path}")
    parent = json.loads(verified(PARENTS[0], "summary.json").read_text())
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        histories = list(pool.map(history, [(h["label"], str(args.output)) for h in parent["histories"]]))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__), histories=histories,
        moving_relay_retarded_time_and_energy_jacobians_included=True,
        radial_reflector_work_ports_and_finite_photon_inventory_included=True,
        capacitor_drive_alternative_selected=False,
        common_radial_trajectory_required=True, equal_axis_and_opposed_population_partition_required=True,
        additional_guide_host_rest_and_kinetic_energy_counted=False,
        nonradial_guide_traction_paths_constructed=False,
        actual_thermalization_and_coating_material_laws_identified=False,
        common_loss_replacement_waveforms_constructed=False,
        electrical_lead_and_converter_material_inventories_counted=False,
        complete_physical_rail_feasibility_established=False)
    (args.output/"summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(), ROOT/"toolkit/adm_harness_cli/adm_harness/moving_thermal_budget.py",
             ROOT/"toolkit/adm_harness_cli/tests/test_moving_thermal_budget.py"]
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
