#!/usr/bin/env python3
"""Reproduce continuous comparison bounds and revised pilots for four histories."""
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

from adm_harness.constitutive_joints_and_optics import series_state
from adm_harness.coupled_holding_certificate import FIELD_BIAS_ENERGY, H_MIN, H_MAX
from adm_harness.reaction_endpoint_certificate import (
    BASELINE_POWER_CEILING, FILTER_TAPS, GUIDE_NETWORK_CEILING, INVERSE_L1,
    MINIMUM_PILOT, PHOTON_PEAK, PILOT_CEILING, QUIET_POWER_CEILING,
    RECEIPT_RATE_CEILING, SHORT_DELAY, event_certificate, guide_derivative_certificate,
    quiet_pilot, separation_certificate, tracking_coefficient_certificate,
)
from adm_harness.scheduled_optical_transfer import GUIDE_MASS, SPIN_FLOOR, preparation
from adm_harness.shared_rail_reactions import SUPPORT_INDICES

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "supporting_reports/data"
PARENTS = ("coupled_holding_certificate", "scheduled_optical_transfer",
           "controlled_optical_transfer", "constitutive_joints_and_optics")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified(group, name):
    path = DATA / group / name
    manifest = json.loads((DATA / group / "manifest.json").read_text())
    if sha256(path) != manifest["output_sha256"][name]:
        raise ValueError(f"Parent output changed: {path}")
    return path


def history(task):
    name, destination = task
    sources = [verified(PARENTS[0], name+"_certificate.npz")]
    sources.extend(verified(group, name+"_states.npz") for group in PARENTS[1:])
    with np.load(sources[0]) as c, np.load(sources[1]) as s, np.load(sources[2]) as p, np.load(sources[3]) as j:
        for values in (s, p, j):
            np.testing.assert_array_equal(c["x"], values["x"])
            np.testing.assert_array_equal(c["t"], values["t"])
        capacity, active = c["node_capacity"], c["node_capacity"] > 0
        rate = s["loop_baseline_power_over_peak"]*2*SPIN_FLOOR/(1-SPIN_FLOOR)
        baseline = c["panel_baseline_power_upper"].max(axis=0)
        pilot = quiet_pilot(rate, baseline, active=active)
        durations = np.diff(j["proper_time"], axis=0)/p["transit_delay"]
        separation = separation_certificate(float(durations.min()))
        checks = dict(receipt_rate=bool(rate[active].max() <= RECEIPT_RATE_CEILING),
            baseline_power=bool(baseline.max() <= BASELINE_POWER_CEILING),
            quiet_support_power=bool(pilot["support_power_upper"][active].max() <= QUIET_POWER_CEILING),
            pilot=bool(pilot["pilot"][active].max() <= PILOT_CEILING),
            endpoint_quiet=bool(np.all(pilot["pilot"][active] >= pilot["command_upper"][active]/SPIN_FLOOR)))
        initial_line = 3*SHORT_DELAY*pilot["pilot"]
        support = list(SUPPORT_INDICES)
        T = j["effective_material_tension"][support, 0]/c["capacity"]
        M = j["material_inventory"][support]/c["capacity"]
        m = j["joint_inventory_per_direction"][support]/c["capacity"]
        original = series_state(T, M, m, dimension=2)["total_energy"]
        amplitude = (FIELD_BIAS_ENERGY+initial_line)/3
        state = series_state(T[:, None]+np.array([1., .5])[:, None, None]*amplitude[None],
                             M[:, None], m[:, None], dimension=2)
        initial_support = FIELD_BIAS_ENERGY+(state["total_energy"]-original[:, None]).sum(axis=0)
        old_initial_line = 3*SHORT_DELAY*MINIMUM_PILOT
        change_initial = initial_support-c["initial_support_energy_over_C"][None]
        energy_rows, arrays = [], dict(x=c["x"], t=c["t"], node_capacity=capacity, capacity=c["capacity"],
            fixed_support_partition=c["fixed_support_partition"], receipt_derivative_upper=rate,
            baseline_power_upper=baseline, proposed_pilot=pilot["pilot"],
            quiet_support_power_upper=pilot["support_power_upper"], quiet_command_upper=pilot["command_upper"],
            initial_line_energy_over_C=initial_line, initial_support_energy_over_C=initial_support,
            capacity_weighted_pilot=(pilot["pilot"]*capacity).sum(axis=0)/c["capacity"])
        for mass in (18., 19., 20.):
            low = c[f"mass{mass:g}_energy_floor"][None]+(change_initial+initial_line-old_initial_line)/mass
            high = c[f"mass{mass:g}_energy_ceiling"][None]+change_initial/mass
            passed = bool(np.all((low[active] >= H_MIN) & (high[active] <= H_MAX)))
            arrays[f"mass{mass:g}_revised_energy_floor"] = low
            arrays[f"mass{mass:g}_revised_energy_ceiling"] = high
            energy_rows.append(dict(inventory=mass, revised_energy_floor=float(low[active].min()),
                revised_energy_ceiling=float(high[active].max()), energy_domain_passed=passed))
        checks["revised_energy_domain"] = all(row["energy_domain_passed"] for row in energy_rows)
        # Extra pilot exposure only: full combined loss/reserve accounting has
        # its own parent audit, including the new rotor port encounter bound.
        hold_time = (j["proper_time"]-j["proper_time"][0])/p["transit_delay"]
        extra_pilot = ((pilot["pilot"]-MINIMUM_PILOT)*capacity).sum(axis=0)
        arrays["additional_pilot_endpoint_exposure_upper"] = 4*extra_pilot[None]*(hold_time+800)
        np.savez_compressed(Path(destination)/(name+"_endpoints.npz"), **arrays)
        row = dict(label=name, passed=all(checks.values()), checks=checks,
            input_sha256={str(path.relative_to(ROOT)): sha256(path) for path in sources},
            maximum_receipt_derivative=float(rate[active].max()), maximum_baseline_power=float(baseline.max()),
            maximum_quiet_support_power=float(pilot["support_power_upper"][active].max()),
            maximum_quiet_command=float(pilot["command_upper"][active].max()),
            maximum_proposed_pilot=float(pilot["pilot"][active].max()),
            maximum_capacity_weighted_pilot=float(arrays["capacity_weighted_pilot"].max()),
            maximum_extra_pilot_exposure=float(arrays["additional_pilot_endpoint_exposure_upper"].max()),
            current_pilot_closes_this_sufficient_bound=bool(np.all(MINIMUM_PILOT >= pilot["command_upper"][active]/SPIN_FLOOR)),
            failed_upper_bound_proves_physical_failure=False,
            energy_variants=energy_rows, separation=separation)
        if not row["passed"]:
            raise ValueError(f"History endpoint domain failed: {name}: {checks}")
    print(name, row["maximum_proposed_pilot"], flush=True)
    return row


def event(task):
    direction, refinement, destination = task
    row, arrays = event_certificate(direction, samples_per_delay=refinement)
    if refinement == 4:
        np.savez_compressed(Path(destination)/("up_event.npz" if direction else "down_event.npz"), **arrays)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=DATA / "reaction_endpoint_certificate")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    for group in PARENTS:
        manifest = json.loads((DATA / group / "manifest.json").read_text())
        for path, digest in manifest["runtime_sha256"].items():
            if sha256(ROOT / path) != digest:
                raise ValueError(f"Parent runtime changed: {path}")
    parent = json.loads(verified(PARENTS[0], "summary.json").read_text())
    coefficients, guide = tracking_coefficient_certificate(), guide_derivative_certificate()
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        histories = list(pool.map(history, [(h["label"], str(args.output)) for h in parent["histories"]]))
        events = list(pool.map(event, [(direction, refinement, str(args.output))
                                     for refinement in (4, 8) for direction in (True, False)]))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__),
        tracking_coefficients=coefficients, guide_derivative_bounds=guide, histories=histories, events=events,
        minimum_separation=separation_certificate(784), inverse_l1_upper=INVERSE_L1, impulse_prefix_taps=FILTER_TAPS,
        finite_line_peak=PHOTON_PEAK, short_delay=SHORT_DELAY, guide_network_ceiling=GUIDE_NETWORK_CEILING,
        inherited_spin_floor=SPIN_FLOOR, independent_fixed_capacity_cells=True,
        equal_axis_and_opposed_wave_population_partition_required=True,
        baseline_constitutive_work_included=True, revised_per_cell_pilots_required=True,
        maximum_flight_inventory_unchanged=True, pilot_preparation_from_counted_inventory_required=True,
        nonlinear_parent_domain_and_spin_floor_required=True,
        all_interval_endpoints_and_interiors_covered=True,
        finite_line_endpoint_power_positivity_certified_conditionally_over_histories=True,
        rotor_incident_and_bypass_power_certified_conditionally_over_histories=True,
        prescribed_feedforward_commands=True, distributed_feedback_controller_constructed=False,
        finite_line_delay_propagation_model="lossless",
        assigned_route_loss_replacement_waveforms_included=False,
        physical_electrical_transducer_dynamics_certified=False,
        capacitor_gap_field_energy_time_evolution_included=False,
        updated_total_loss_and_heat_accounting_owned_by_separate_audit=True,
        electrical_holding_losses_included=False, spatial_partition_and_charge_returns_constructed=False,
        added_geometric_macro_traction_work_closed=False, full_history_physical_transfer_closed=False)
    (args.output / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    own_paths = [Path(__file__).resolve(), ROOT / "toolkit/adm_harness_cli/adm_harness/reaction_endpoint_certificate.py",
                 ROOT / "toolkit/adm_harness_cli/tests/test_reaction_endpoint_certificate.py"]
    for path in own_paths:
        shutil.copyfile(path, args.output / ("execution_"+path.name))
    manifest = dict(runtime_sha256={str(path.relative_to(ROOT)): sha256(path) for path in own_paths},
        parent_manifest_sha256={str((DATA / group / "manifest.json").relative_to(ROOT)):
            sha256(DATA / group / "manifest.json") for group in PARENTS},
        output_sha256={path.name: sha256(path) for path in sorted(args.output.iterdir())
                       if path.is_file() and path.name != "manifest.json"})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
