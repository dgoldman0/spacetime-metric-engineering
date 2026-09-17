#!/usr/bin/env python3
"""Audit moving annular heat paths and their finite radial work-photon ports."""
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

from adm_harness.moving_thermal_relay import (
    RadialTrajectory, annular_axis_ensemble, moving_paired_relay, radial_work_lead,
    reaction_work_allowance, relay_bounds, selected_route_bounds,
)

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT/"supporting_reports/data"
R0 = 1/(12*np.pi)
REFERENCE = 1.2*R0
HALF_EXCURSION = .132*R0
WORK_HALF_GAP = 1.1*HALF_EXCURSION


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trajectory(name):
    t = np.linspace(-.125, 1.125, 257)
    if name == "stationary":
        R, v = np.full_like(t, REFERENCE), np.zeros_like(t)
    elif name == "uniform":
        R, v = REFERENCE+.0045*(t-.5), np.full_like(t, .0045)
    else:
        omega = 6. if name == "slow_reversal" else 96.
        R, v = REFERENCE+.0089/omega*np.sin(omega*t), .0089*np.cos(omega*t)
    return RadialTrajectory(t, R, v)


def audit_case(task):
    name, output = task
    output = Path(output)
    time = np.linspace(-.0625, 1.0625, 1153)
    phase = np.clip(time/.75, 0., 1.)
    heat = np.sin(np.pi*phase)**2/6
    heat[(time <= 0) | (time >= .75)] = 0.
    spin = .57+.25*np.cos(8*time)
    motion = trajectory(name)
    obs = time[::4]
    relay = moving_paired_relay(time, heat, spin, motion, observation_time=obs,
                                quadrature_order=8, include_drive_function=True)
    drive, breaks = relay["radial_drive_function"], relay["radial_drive_breakpoints"]
    force = drive(time)
    leads = []
    for index in range(3):
        lead = radial_work_lead(time, force[index], motion, reference_radius=REFERENCE,
            half_gap=WORK_HALF_GAP, observation_time=obs,
            force_function=lambda q, stage=index: drive(q)[stage], additional_breakpoints=breaks)
        leads.append(lead)
        np.savez_compressed(output/f"{name}_work_stage_{index}.npz", **lead)
    work_energy = sum(lead["photon_energy"] for lead in leads)
    work_rate = sum(lead["photon_energy_rate"] for lead in leads)
    remote = sum(lead["remote_net_power"] for lead in leads)
    supplied = sum(lead["mechanical_power"] for lead in leads)
    combined_error = (relay["flight_energy_rate"]+work_rate-relay["source_total_power"]
                      +relay["bath_total_power"]-remote)
    actuator_tensor = np.zeros_like(relay["flight_tensor"])
    actuator_tensor[0, 0] = actuator_tensor[1, 1] = work_energy
    total_tensor = annular_axis_ensemble(relay["flight_tensor"]+actuator_tensor)
    total_energy = 3*(relay["flight_energy"]+work_energy)
    parity_error = abs(relay["bath_arrival_stream_power"][:, 0]
                       -relay["bath_arrival_stream_power"][:, 1]).max()
    work_error = abs(supplied-relay["guide_work_to_photons"]).max()
    errors = {key: float(abs(relay[key]).max()) for key in (
        "four_momentum_balance_error", "source_guide_work_error", "central_guide_work_error",
        "destination_guide_work_error", "energy_balance_error", "single_leg_null_error")}
    errors.update(combined_energy_balance=float(abs(combined_error).max()),
        exact_drive_matches_thermal_recoil=float(work_error),
        local_bath_counterstream_balance=float(parity_error),
        work_lead_four_momentum_balance=max(float(abs(lead[key]).max()) for lead in leads
            for key in ("energy_balance_error", "radial_momentum_balance_error", "mechanical_work_error")),
        six_rotor_isotropic_stress=max(float(abs(total_tensor[i, i]-total_energy/3).max()) for i in (1, 2, 3)),
        six_rotor_spatial_momentum=float(abs(total_tensor[0, 1:]).max()))
    refined = moving_paired_relay(time, heat, spin, motion, observation_time=obs[::4], quadrature_order=12)
    errors["thermal_inventory_quadrature_refinement"] = float(abs(
        refined["flight_tensor"]-relay["flight_tensor"][:, :, ::4]).max())
    refinement = []
    for index, lead in enumerate(leads):
        fine = radial_work_lead(time, force[index], motion, reference_radius=REFERENCE,
            half_gap=WORK_HALF_GAP, observation_time=obs[::4], quadrature_order=12,
            force_function=lambda q, stage=index: drive(q)[stage], additional_breakpoints=breaks)
        refinement.append(float(abs(fine["photon_energy"]-lead["photon_energy"][::4]).max()))
    errors["actuator_inventory_quadrature_refinement"] = max(refinement)
    if max(errors.values()) > 2e-11:
        raise ValueError(f"Moving relay verification failed: {name}: {errors}")
    b, peak = relay["bounds"], float(relay["source_total_power"].max())
    ceilings = dict(heat_flight=b["flight_energy_per_emitted_peak"]*peak,
        heat_arrival=b["bath_power_per_emitted_peak"]*peak,
        summed_absolute_guide_work=b["guide_work_peak_per_emitted_power"]*peak,
        summed_radial_guide_force=b["radial_guide_force_peak_per_emitted_power"]*peak)
    maxima = dict(heat_flight=float(relay["flight_energy"].max()),
        heat_arrival=float(relay["bath_total_power"].max()),
        summed_absolute_guide_work=float(abs(relay["guide_work_by_stage"]).sum(axis=0).max()),
        summed_radial_guide_force=float(abs(drive(obs)).sum(axis=0).max()))
    if any(maxima[key] > value*(1+1e-11)+2e-14 for key, value in ceilings.items()):
        raise ValueError(f"Uniform speed ceiling failed: {name}")
    archived = {key: value for key, value in relay.items() if isinstance(value, np.ndarray)}
    np.savez_compressed(output/f"{name}_thermal.npz", **archived, source_time=time,
        source_heat_per_rotor=heat, source_spin=spin, trajectory_time=motion.time,
        trajectory_radius=motion.radius, trajectory_speed=motion.speed,
        work_photon_energy=work_energy, remote_work_port_power=remote,
        combined_energy_balance_error=combined_error, complete_six_rotor_flight_tensor=total_tensor)
    return dict(name=name, source_samples=len(time), observed_samples=len(obs),
        checked_interpolated_speed=motion.maximum_speed, errors=errors,
        pair_maxima=maxima, pair_ceilings=ceilings,
        delay_range=[float(relay["total_retarded_delay"].min()), float(relay["total_retarded_delay"].max())],
        signed_guide_work_range=[float(relay["guide_work_to_photons"].min()), float(relay["guide_work_to_photons"].max())],
        pair_work_photon_energy_maximum=float(work_energy.max()),
        six_rotor_total_flight_energy_maximum=float(total_energy.max()),
        six_rotor_initial_flight_energy=float(total_energy[0]),
        six_rotor_final_flight_energy=float(total_energy[-1]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=DATA/"moving_thermal_relay")
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        parser.error("one to four workers required")
    args.output.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        cases = list(pool.map(audit_case, [(name, str(args.output)) for name in
            ("stationary", "uniform", "slow_reversal", "fast_reversal")]))
    parent = DATA/"hosted_reaction_dynamics/summary.json"
    parent_manifest = parent.with_name("manifest.json")
    expected = json.loads(parent_manifest.read_text())["output_sha256"][parent.name]
    if sha256(parent) != expected:
        raise ValueError("Published local endpoint comparison evidence changed")
    prior = json.loads(parent.read_text())
    local_margin = min(trial["floors"]["minimum_emitted_power"] for trial in prior["trials"])
    allowance = reaction_work_allowance(4.297704, maximum_actuator_gap=2.1*HALF_EXCURSION)
    summary = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__),
        geometry=dict(axial_half_separation=1/128, radial_reference=REFERENCE,
            assigned_rotor_radius_factor_range=[1.068, 1.332], radial_work_half_gap=WORK_HALF_GAP,
            assigned_work_gap_ceiling=2.1*HALF_EXCURSION, rotor_copies=6, axis_pairs=3),
        uniform_bounds=relay_bounds(), selected_route_bounds=selected_route_bounds(2.1*HALF_EXCURSION), cases=cases,
        conditional_M19_optical_peak_comparison=allowance,
        published_local_emitted_half_channel_margin=local_margin,
        local_margin_after_added_work_lead_inverse=local_margin-allowance["finite_reflector_half_channel_margin"],
        input_sha256={str(parent.relative_to(ROOT)): sha256(parent)},
        moving_null_paths_and_clock_jacobians_included=True,
        local_counterstream_balance_preserved=True,
        source_mixer_collector_recoil_retained=True,
        selected_guide_drive="radial reflector with finite stationary-port leads",
        thermal_and_work_photon_inventory_and_stress_counted=True,
        capacitor_drive_is_an_alternative_not_added_to_selected_inventory=True,
        full_coupled_history_recomputed=False,
        guide_rest_mass_inertia_torsion_and_axial_support_material_closed=False,
        added_optical_absorption_and_scatter_included=False,
        finite_aperture_aiming_and_thermal_material_interfaces_constructed=False)
    (args.output/"summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n")
    own = [Path(__file__).resolve(), ROOT/"toolkit/adm_harness_cli/adm_harness/moving_thermal_relay.py",
           ROOT/"toolkit/adm_harness_cli/tests/test_moving_thermal_relay.py"]
    imported = ROOT/"toolkit/adm_harness_cli/adm_harness/thermal_exchange_interfaces.py"
    for source in own:
        shutil.copyfile(source, args.output/("execution_"+source.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in [*own, imported]},
        input_sha256=summary["input_sha256"],
        output_sha256={p.name: sha256(p) for p in sorted(args.output.iterdir())
                       if p.is_file() and p.name != "manifest.json"})
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps(dict(cases=cases, allowance=allowance), indent=2), flush=True)


if __name__ == "__main__":
    main()
