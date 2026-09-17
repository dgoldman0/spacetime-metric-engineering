#!/usr/bin/env python3
"""Verify coupled storage inequalities and screen four partitioned histories."""
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

from adm_harness.coupled_holding_certificate import (
    ADDED_DUTY_LIMITS, BASELINE_C_RATE_BOUND, C_MAX, EXTERNAL_TRACE_RATE_BOUND,
    FIELD_BIAS_ENERGY, FLOAT_GUARD, H_MAX, H_MIN, N_MAX, PHOTON_PEAK,
    PHOTON_PILOT, SHORT_DELAY, TRACE_CURVATURE_BOUND, constitutive_panel_bounds,
    forcing_history_bounds, history_result, input_l1_certificate, matrix_certificate, reaction_initial_energy,
)
from adm_harness.scheduled_optical_transfer import (
    CONVERTER_RAMP, RAMP_TIME, ROTOR_RADIUS, SPIN_FLOOR, preparation,
)
from adm_harness.nonlinear_holding_certificate import guide_input_certificate
from adm_harness.shared_rail_reactions import SUPPORT_INDICES, guide_trace_bound

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "supporting_reports/data"
PARENTS = ("scheduled_optical_transfer", "constitutive_joints_and_optics", "controlled_optical_transfer",
           "nonlinear_holding_certificate")
ASSIGNED_OLD_LOSS = .62e-6


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
    sources = [verified(group, name+"_states.npz") for group in PARENTS[:3]]
    with np.load(sources[0]) as a, np.load(sources[1]) as j, np.load(sources[2]) as p:
        for key in ("t", "x"):
            np.testing.assert_array_equal(a[key], j[key])
            np.testing.assert_array_equal(a[key], p[key])
        capacity, node_capacity, labels = a["capacity"], p["reception_capacity"], a["x"]
        np.testing.assert_allclose(node_capacity.sum(axis=0), capacity, rtol=2e-14)
        weights = node_capacity/capacity
        np.testing.assert_allclose(weights.sum(axis=0), 1., rtol=2e-14)
        active = node_capacity > 0
        support = list(SUPPORT_INDICES)
        tension = j["effective_material_tension"][support]/capacity
        inventory = j["material_inventory"][support]/capacity
        joints = j["joint_inventory_per_direction"][support]/capacity
        duration = np.diff(j["proper_time"], axis=0)/p["transit_delay"]
        if duration.min() <= 2*(CONVERTER_RAMP+RAMP_TIME+8):
            raise ValueError("Finite-line event derivatives overlap their inherited separation domain")
        bounds = constitutive_panel_bounds(tension, inventory, joints, duration)
        forcing = forcing_history_bounds(a["node_final_receipt_l2_upper"],
            a["node_final_guide_l2_upper"], a["node_final_loop_l2_upper"],
            bounds["baseline_power_l2_upper"], bounds["baseline_power_upper"].max(axis=0))
        E0 = reaction_initial_energy(tension[:, 0], inventory, joints)
        rate_checks = dict(
            gain=bool(bounds["gain_upper"].max() <= C_MAX),
            curvature=bool(bounds["trace_curvature_upper"].max() <= TRACE_CURVATURE_BOUND),
            baseline_rate=bool(bounds["baseline_cprime_upper"].max() <= BASELINE_C_RATE_BOUND),
            external_trace_rate=bool(forcing["external_trace_rate_upper"] <= EXTERNAL_TRACE_RATE_BOUND))
        values = dict(x=labels, t=a["t"], capacity=capacity, node_capacity=node_capacity,
            fixed_support_partition=weights, initial_support_energy_over_C=E0,
            node_forcing_l2_upper=forcing["power_l2_upper"],
            node_inherited_network_l2_upper=forcing["inherited_network_l2"],
            node_finite_line_l2_upper=forcing["finite_line_l2"],
            node_guide_trace_l2_upper=forcing["guide_trace_l2"],
            finite_line_events=forcing["events"],
            baseline_power_l2_upper=bounds["baseline_power_l2_upper"],
            panel_baseline_power_upper=bounds["baseline_power_upper"],
            panel_gain_upper=bounds["gain_upper"],
            panel_trace_curvature_upper=bounds["trace_curvature_upper"],
            panel_baseline_cprime_upper=bounds["baseline_cprime_upper"])
        variants = []
        old_prep = preparation()
        old_loss = ASSIGNED_OLD_LOSS*a["finite_loop_total_exposure_upper"]/(1-ASSIGNED_OLD_LOSS/SPIN_FLOOR)
        # A photon meets an emission and a receiving endpoint. The parent
        # converter envelope overbounds all new branch event windows.
        extra_exposure = (4*PHOTON_PILOT*a["nominal_guide_exposure"]
                          +4*PHOTON_PEAK/5*a["loop_exposure_upper"]
                          +4*PHOTON_PILOT*2*(RAMP_TIME+CONVERTER_RAMP+16)*capacity[None])
        extra_loss = ASSIGNED_OLD_LOSS*extra_exposure/(1-ASSIGNED_OLD_LOSS/SPIN_FLOOR)
        values["additional_line_endpoint_exposure_upper"] = extra_exposure
        values["additional_line_loss_energy_upper"] = extra_loss
        for mass in (18., 19., 20.):
            prep = preparation(inventory=mass)
            result = history_result(forcing["power_l2_upper"], E0, inventory=mass,
                original_energy_floor=prep["quasistatic_rotor_energy_floor"],
                original_dynamic_energy=prep["initial_dynamic_energy"], guide_trace_bound=guide_trace_bound())
            reduced_peak = ROTOR_RADIUS*forcing["power_peak_upper"]/mass
            input_passed = bool(np.max(reduced_peak) <= N_MAX)
            energy_passed = bool(np.all(result["energy_domain_passed"]))
            heat_passed = bool(np.all(result["spin_passed"][active]))
            allocation_passed = bool(result["added_outer_duty_upper"] <= ADDED_DUTY_LIMITS[0]
                                     and result["dynamic_trace_upper"] < FIELD_BIAS_ENERGY)
            reserve = (a["all_panel_reserve_lower_bound"]-old_loss
                       -(prep["candidate_preparation"]-old_prep["candidate_preparation"]
                         +result["support_and_line_energy_ceiling"])*capacity[None])
            prefix = f"mass{mass:g}_"
            values.update({prefix+key: value for key, value in result.items() if isinstance(value, np.ndarray)})
            values[prefix+"reduced_input_peak_upper"] = reduced_peak
            values[prefix+"reserve_after_old_loss_and_extra_state"] = reserve.min(axis=0)
            known_reserve = reserve-extra_loss
            values[prefix+"reserve_after_known_loss_and_extra_state"] = known_reserve.min(axis=0)
            checks = dict(constitutive_rate=all(rate_checks.values()), input=input_passed,
                energy_domain=energy_passed, thermal_spin=heat_passed, support_allocation=allocation_passed)
            failing = [key for key, passed in checks.items() if not passed]
            minimum_spin2 = float(result["spin_squared_lower"][active].min())
            maximum = np.where(active, result["thermal_action_upper"], -np.inf)
            worst = np.unravel_index(np.argmax(maximum), maximum.shape)
            variants.append(dict(inventory=mass, conditional_history_bound_passed=not failing,
                conditional_bound_and_known_loss_budget_passed=not failing and bool(np.all(known_reserve > 0)),
                checks=checks, open_or_exceeded_sufficient_bounds=failing,
                maximum_reduced_input_bound=float(reduced_peak.max()),
                energy_floor=float(result["energy_floor"].min()), energy_ceiling=float(result["energy_ceiling"].max()),
                maximum_thermal_action_bound=float(maximum.max()),
                minimum_thermal_action_capacity=float(result["thermal_action_capacity"].min()),
                minimum_spin_squared_lower=minimum_spin2,
                minimum_spin_lower=float(np.sqrt(minimum_spin2)) if minimum_spin2 > 0 else None,
                maximum_thermal_energy_over_C=float(result["thermal_energy_upper"][active].max()),
                support_and_line_energy_ceiling=result["support_and_line_energy_ceiling"],
                dynamic_trace_upper=result["dynamic_trace_upper"],
                added_outer_duty_upper=result["added_outer_duty_upper"],
                minimum_reserve_with_old_loss_and_extra_state=float(reserve.min()),
                existing_loss_and_state_reserve_passed=bool(np.all(reserve > 0)),
                minimum_reserve_with_known_loss_and_extra_state=float(known_reserve.min()),
                known_loss_and_state_reserve_passed=bool(np.all(known_reserve > 0)),
                worst_heat_node=int(worst[0]), worst_heat_material_label=float(labels[worst[1]]),
                failed_upper_bound_proves_physical_failure=False))
    np.savez_compressed(Path(output) / (name+"_certificate.npz"), **values)
    row = dict(label=name, input_sha256={str(path.relative_to(ROOT)): sha256(path) for path in sources},
        maximum_constitutive_gain_bound=float(bounds["gain_upper"].max()),
        maximum_trace_curvature_bound=float(bounds["trace_curvature_upper"].max()),
        maximum_baseline_constitutive_rate_bound=float(bounds["baseline_cprime_upper"].max()),
        maximum_baseline_power_bound=float(bounds["baseline_power_upper"].max()),
        maximum_baseline_power_l2_bound=float(bounds["baseline_power_l2_upper"].max()),
        maximum_external_trace_rate_bound=forcing["external_trace_rate_upper"],
        maximum_inherited_network_l2=float(forcing["inherited_network_l2"].max()),
        maximum_finite_line_l2=float(forcing["finite_line_l2"].max()),
        maximum_combined_power_l2=float(forcing["power_l2_upper"].max()),
        maximum_final_additional_line_exposure=float(extra_exposure[-1].max()),
        maximum_final_additional_line_loss=float(extra_loss[-1].max()),
        initial_support_energy_range=[float(E0.min()), float(E0.max())],
        minimum_constitutive_force_margin=bounds["minimum_force_margin"],
        minimum_panel_over_delay=float(duration.min()),
        rate_checks=rate_checks, inventory_variants=variants)
    print(name, [(v["inventory"], v["conditional_history_bound_passed"],
                  v["minimum_spin_squared_lower"]) for v in variants], flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=DATA / "coupled_holding_certificate")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    for group in PARENTS:
        manifest = json.loads((DATA / group / "manifest.json").read_text())
        for path, digest in manifest["runtime_sha256"].items():
            if sha256(ROOT / path) != digest:
                raise ValueError(f"Parent implementation changed: {path}")
    matrix, guide = matrix_certificate(), guide_input_certificate()
    prior = json.loads(verified(PARENTS[0], "summary.json").read_text())
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        histories = list(pool.map(history, [(h["label"], str(args.output)) for h in prior["histories"]]))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__), matrix_certificate=matrix,
        input_l1_certificate=input_l1_certificate(),
        inherited_guide_input_positive_bound=guide["input_power_lower_bound"],
        histories=histories, field_bias_energy_over_C=FIELD_BIAS_ENERGY,
        added_duty_enclosure=ADDED_DUTY_LIMITS.tolist(),
        finite_line=dict(short_delay=SHORT_DELAY, peak=PHOTON_PEAK, pilot=PHOTON_PILOT),
        constitutive_history_float_guard=FLOAT_GUARD,
        initial_radial_error=[0., 0.], initial_thermal_action=1e-8,
        cold_prepared_initial_state_assumed=True,
        fixed_capacity_partition_of_original_supports=True,
        constitutive_inventory_and_baseline_tensor_partition_exact=True,
        changing_baseline_constitutive_power_included=True,
        independent_scalar_cell_nonlinear_certificate=True,
        finite_line_endpoint_power_positivity_certified_over_histories=False,
        physical_electrical_transducer_dynamics_certified=False,
        capacitor_gap_field_energy_time_evolution_included=False,
        inherited_loss_fraction=ASSIGNED_OLD_LOSS,
        new_line_endpoint_encounter_losses_priced=True,
        coupled_rotor_reflective_loss_envelope_recomputed=False,
        assigned_loss_replacement_and_absorption_heat_in_dynamics=False,
        electrical_holding_losses_included=False,
        spatial_partition_and_charge_returns_constructed=False,
        added_geometric_macro_traction_work_closed=False,
        full_history_physical_transfer_closed=False)
    (args.output / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(), ROOT / "toolkit/adm_harness_cli/adm_harness/coupled_holding_certificate.py",
             ROOT / "toolkit/adm_harness_cli/tests/test_coupled_holding_certificate.py"]
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
