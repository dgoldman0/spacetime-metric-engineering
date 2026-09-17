#!/usr/bin/env python3
"""Numerical evidence for physical-store, routing and optical-loss gates.

Four workers evaluate independent cases. Narrative findings are authored
separately; this script produces arrays, measurements, plots and hashes.
"""
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

from adm_harness.constitutive_joints_and_optics import series_panel_state, series_power_bounds
from adm_harness.optical_assembly import assembly_energy_screen, loss_budget, polygon_reactions, simulate_store

ROOT = Path(__file__).resolve().parents[3]
PARENT = ROOT / "supporting_reports/data/controlled_optical_transfer"
JOINTS = ROOT / "supporting_reports/data/constitutive_joints_and_optics"
MACRO = ROOT / "supporting_reports/data/material_reconfiguration"
HALF_PERIOD = 3.8238248063636506/(3*np.pi)
STORE_MASS = 8.
STORE_RADIUS = 1/(12*np.pi)
INITIAL_RADIUS = 1/np.sqrt(.6)
HYDROGEN_FRACTION = 120e6/299792458.**2


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified(directory, filename):
    path = directory / filename
    manifest = json.loads((directory / "manifest.json").read_text())
    if sha256(path) != manifest["output_sha256"][filename]:
        raise ValueError(f"Evidence hash mismatch: {path}")
    return path


def extrema(a):
    return dict(minimum=float(np.min(a)), maximum=float(np.max(a)))


def store_trial(task):
    name, parameters, save, output = task
    result = simulate_store(**parameters)
    balance = float(np.max(abs(result["balance_error"])))
    if balance > 2e-7 or np.min(np.diff(result["entropy_proxy"])) < -1e-8:
        raise ValueError("Store conservation or thermal monotonicity failed")
    row = dict(name=name, parameters=parameters, complete=result["complete"], boundary=result["boundary"],
        end_time=float(result["time"][-1]), radius=extrema(result["state"][0]),
        peak_speed=float(np.max(abs(result["speed"]))),
        peak_pressure_trace=float(np.max(abs(result["pressure_trace"]))),
        maximum_hoop_stress_energy_ratio=float(result["hoop_stress_energy_ratio"].max()),
        extraction_depth=extrema(result["extraction_depth"]),
        circulating_power=extrema(result["circulating_power"]),
        final_thermal_energy=float(result["thermal_energy"][-1]),
        maximum_thermal_energy=float(result["thermal_energy"].max()),
        minimum_coherent_action=float(result["state"][2].min()),
        maximum_energy_identity_error=balance, retained_orbit=result["retained_orbit"],
        initial_energy=result["initial_energy"], quasistatic_energy_floor=result["quasistatic_energy_floor"])
    if save:
        np.savez_compressed(Path(output) / (name+"_states.npz"),
            **{k: result[k] for k in ("time", "state", "energy", "speed", "pressure_trace",
                "elastic_radiation_trace", "viscous_trace", "hoop_stress_energy_ratio", "thermal_energy",
                "entropy_proxy", "input_power", "output_power", "extraction_depth", "circulating_power",
                "useful_power", "useful_energy", "inflight", "balance_error")})
    print(name, result["boundary"] or "completed", "t", row["end_time"], flush=True)
    return row


def history_audit(task):
    name, output = task
    paths = [verified(d, name+"_states.npz") for d in (PARENT, JOINTS, MACRO)]
    for directory, dependency in ((PARENT, paths[1]), (JOINTS, paths[2])):
        summary = json.loads(verified(directory, "summary.json").read_text())
        history = next(h for h in summary["histories"] if h["label"] == name)
        if history["input_sha256"][str(dependency.relative_to(ROOT))] != sha256(dependency):
            raise ValueError("Linked optical, joint and macro provenance differs")
    with np.load(paths[0]) as saved:
        parent = {k: saved[k] for k in ("t", "x", "node_peak_power", "transit_delay", "reception_capacity",
            "prepared_energy", "initial_buffer", "remaining_reserve", "all_panel_reserve_lower_bound")}
    with np.load(paths[1]) as saved:
        joints = {k: saved[k] for k in ("t", "x", "proper_time", "effective_material_tension",
            "material_inventory", "joint_inventory_per_direction", "component_energy", "remaining_reserve")}
    with np.load(paths[2]) as saved:
        target, lr, lt, dt = (saved[k] for k in ("target", "lr", "lt", "proper_panel_duration"))
        np.testing.assert_array_equal(parent["t"], saved["t"])
        np.testing.assert_array_equal(parent["x"], saved["x"])
    np.testing.assert_array_equal(parent["t"], joints["t"])
    np.testing.assert_array_equal(parent["x"], joints["x"])
    candidate = assembly_energy_screen(parent["reception_capacity"], parent["prepared_energy"],
                                       parent["initial_buffer"])
    C = parent["reception_capacity"].sum(axis=0)
    extra = candidate["added_energy"].sum(axis=0)
    reserve = parent["remaining_reserve"]-extra
    continuous = parent["all_panel_reserve_lower_bound"]-extra
    if continuous.min() <= 0:
        raise ValueError("Candidate static store and routing inventory exhaust the inherited reserve")
    nominal_power = parent["node_peak_power"].sum(axis=0)
    traffic = nominal_power*joints["proper_time"][1:]
    effective_limit = np.min(continuous/traffic, axis=0)
    sampled_limit = np.min(reserve[1:]/traffic, axis=0)
    # Quasistatic store has h=x and loses at most C to useful transit.
    # These circulation bounds apply to that family, not arbitrary motion.
    minimum_radius = INITIAL_RADIUS-1/STORE_MASS
    circulation_lo = 1+STORE_MASS/(4*np.pi*STORE_RADIUS)*(1-minimum_radius**-2)
    circulation_hi = 1+STORE_MASS/(4*np.pi*STORE_RADIUS)*(1-INITIAL_RADIUS**-2)
    # Actual positive-exchange bounds diagnose whether idle guide power is
    # responsible for the stringent screen. No idle-gating law is assumed.
    args = (joints["effective_material_tension"], joints["material_inventory"],
            joints["joint_inventory_per_direction"], joints["component_energy"][12:16], target, lr, lt, dt)
    bound = series_power_bounds(*args)
    useful_lower = (np.maximum(bound["lower"], 0).sum(axis=0)*dt).sum(axis=0)
    useful_upper = (np.maximum(bound["upper"], 0).sum(axis=0)*dt).sum(axis=0)
    p0 = series_panel_state(*args, 0.)["power"]
    p1 = series_panel_state(*args, 1.)["power"]
    jumps = abs(np.maximum(p0[:, 1:], 0)-np.maximum(p1[:, :-1], 0))
    jump_fraction = np.divide(jumps, parent["node_peak_power"][:, None],
                             out=np.zeros_like(jumps), where=parent["node_peak_power"][:, None] > 0)
    # A deliberately generous ordinary-store lower bound gives all the
    # pre-optical reserve to fuel rest mass and charges no vessel or optics.
    chemical_available = joints["remaining_reserve"].min(axis=0)
    required_specific_fraction = C/chemical_available
    benchmarks = []
    for label, mirror_loss, splitter_loss, multiple in (
        ("0.62 ppm absorption, one encounter per guide circuit", .62e-6, 0., 1.),
        ("0.62 ppm absorption, guide plus quasistatic store lower circulation", .62e-6, 0., circulation_lo),
        ("0.74 ppm A+S, guide plus quasistatic store lower circulation", .74e-6, 0., circulation_lo),
        ("0.4 dB splitter deficit, entirely unrecovered", 0., 1-10**(-.4/10), 1.)):
        effective = multiple*mirror_loss+splitter_loss
        budget = loss_budget(reserve[1:], traffic, circulation_multiple=multiple,
                             round_trip_loss=mirror_loss, splitter_unrecovered=splitter_loss)
        final_loss = budget["required_replacement_energy"][-1]
        benchmarks.append(dict(label=label, effective_fraction=effective,
            final_replacement_energy=extrema(final_loss),
            minimum_final_reserve_after_replacement=float(np.min(reserve[-1]-final_loss)),
            minimum_sampled_reserve_after_replacement=float(budget["remaining_reserve"].min()),
            labels_with_sampled_negative_reserve=int(np.count_nonzero(np.min(budget["remaining_reserve"], axis=0) < 0)),
            worst_ratio_to_sufficient_allowance=float(np.max(effective/effective_limit))))
    active_nodes = np.sum(parent["node_peak_power"] > 0, axis=0)
    cycles = joints["proper_time"][-1]/(2*HALF_PERIOD*parent["transit_delay"])
    drive_ceiling = continuous.min(axis=0)/(active_nodes*cycles)
    np.savez_compressed(Path(output) / (name+"_states.npz"), t=parent["t"], x=parent["x"],
        capacity=C, added_energy=extra, candidate_preparation=candidate["candidate_preparation"].sum(axis=0),
        remaining_reserve=reserve, all_panel_reserve_lower_bound=continuous,
        effective_retained_loss_ceiling=effective_limit,
        sampled_retained_loss_ceiling=sampled_limit,
        round_trip_loss_ceiling_with_quasistatic_circulation=effective_limit/circulation_hi,
        required_chemical_specific_fraction=required_specific_fraction,
        useful_energy_lower=useful_lower, useful_energy_upper=useful_upper,
        zero_optical_loss_drive_energy_per_cycle_ceiling=drive_ceiling)
    row = dict(label=name, samples=list(reserve.shape),
        input_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        candidate_preparation=extrema(candidate["candidate_preparation"].sum(axis=0)),
        minimum_remaining_reserve=float(reserve.min()), all_panel_reserve_bound=float(continuous.min()),
        required_chemical_specific_fraction=extrema(required_specific_fraction),
        worst_hydrogen_reference_mass_to_available_ratio=float(np.max(required_specific_fraction/HYDROGEN_FRACTION)),
        sufficient_effective_retained_loss_fraction=extrema(effective_limit),
        sampled_effective_retained_loss_ceiling=extrema(sampled_limit),
        sufficient_round_trip_loss_fraction_with_quasistatic_circulation=extrema(effective_limit/circulation_hi),
        quasistatic_circulation_multiple=[circulation_lo, circulation_hi],
        useful_to_nominal_throughput_lower=extrema(useful_lower/traffic[-1]),
        useful_to_nominal_throughput_upper=extrema(useful_upper/traffic[-1]),
        maximum_prescribed_receipt_jump_over_node_peak=float(jump_fraction.max()),
        zero_optical_loss_drive_energy_per_cycle_ceiling=extrema(drive_ceiling),
        retained_loss_comparisons=benchmarks, candidate_screen_is_energy_only=True,
        actual_full_history_store_dynamics_integrated=False, routing_target_tensor_matched=False,
        prior_perturbed_controller_certificate_carried_over=False)
    print(name, "candidate reserve", row["all_panel_reserve_bound"], flush=True)
    return row


def plot_trials(output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(3, 1, figsize=(8.2, 8.2), constrained_layout=True)
    for name, label, color in [("original_store", "Original radius", "#bd3b35"),
            ("smaller_store", "Radius / 4", "#1665a5"),
            ("damped_original", "Original + counted damping", "#588344")]:
        with np.load(output / (name+"_states.npz")) as d:
            axes[0].plot(d["time"], d["state"][0], label=label, color=color)
            axes[1].plot(d["time"], d["pressure_trace"], color=color)
            axes[2].plot(d["time"], d["thermal_energy"], color=color)
    axes[0].axhline(1, linestyle=":", color="#555555")
    axes[0].set(ylabel="Store radius / reference radius", xlim=(0, 34))
    axes[0].legend(fontsize=9)
    axes[1].set(ylabel="Total pressure trace / C", xlim=(0, 34))
    axes[2].set(ylabel="Contained thermal energy / C", xlabel="Time / useful transit delay", xlim=(0, 34))
    for ax in axes:
        ax.grid(alpha=.2)
    fig.savefig(output / "store_reaction_and_heat.png", dpi=170)
    plt.close(fig)
    return matplotlib.__version__


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_reports/data/optical_assembly")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    cases = [
        ("original_store", dict(), True),
        ("smaller_store", dict(reference_radius=STORE_RADIUS), True),
        ("smaller_nearby_resonance", dict(reference_radius=STORE_RADIUS, half_period=.1025), True),
        ("damped_original", dict(damping=.2), True),
        ("damped_original_extended", dict(damping=.2, intervals=400), True),
        ("damped_smaller_resonance", dict(reference_radius=STORE_RADIUS, half_period=.1025, damping=.2), True),
        ("damped_smaller_resonance_extended", dict(reference_radius=STORE_RADIUS, half_period=.1025,
                                                   damping=.2, intervals=400), True),
        ("smaller_finite_phase", dict(reference_radius=STORE_RADIUS, transition=HALF_PERIOD/4), True),
    ]
    for factor in (1., .5, .25):
        for h in (.1, .15, .3, .5, 1., 2.):
            cases.append((f"radius_{factor:g}_half_{h:g}", dict(reference_radius=factor/(3*np.pi), half_period=h), False))
    for h in np.linspace(.085, .125, 17):
        if abs(h-.1) < 1e-10 or abs(h-.1025) < 1e-10:
            continue
        cases.append((f"smaller_nearby_{h:g}", dict(reference_radius=STORE_RADIUS, half_period=float(h)), False))
    for name in ("original_store", "smaller_store", "smaller_nearby_resonance", "damped_original_extended",
                 "damped_smaller_resonance_extended"):
        base = next(p for n, p, _ in cases if n == name)
        cases.append((name+"_refined", dict(base, maximum_step=.01, rtol=2e-11, atol=2e-13), True))
    names = [h["label"] for h in json.loads(verified(PARENT, "summary.json").read_text())["histories"]]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        trials = list(pool.map(store_trial, [(n, p, s, str(args.output)) for n, p, s in cases]))
        histories = list(pool.map(history_audit, [(n, str(args.output)) for n in names]))
    refinements = []
    for fine in [r for r in trials if r["name"].endswith("_refined")]:
        base = next(r for r in trials if r["name"] == fine["name"].removesuffix("_refined"))
        with np.load(args.output / (base["name"]+"_states.npz")) as a, np.load(args.output / (fine["name"]+"_states.npz")) as b:
            # End-of-event interpolation uses different final grids. All
            # earlier complete forcing segments share the same grid.
            common = np.intersect1d(a["time"], b["time"])
            ia, ib = np.searchsorted(a["time"], common), np.searchsorted(b["time"], common)
            error = float(np.max(abs(a["state"][:, ia]-b["state"][:, ib])))
        time_error = abs(base["end_time"]-fine["end_time"])
        if max(error, time_error) > 2e-6 or base["boundary"] != fine["boundary"]:
            raise ValueError("Store refinement disagrees")
        refinements.append(dict(name=base["name"], shared_samples=len(common),
                                maximum_state_error=error, event_time_error=time_error))
    vertices = np.array([[0, 0, 0], [1.2, .2, .4], [1, 1, .7], [-.3, .4, .2]])
    polygon = polygon_reactions(vertices)
    np.savez_compressed(args.output / "polygon_reactions.npz", vertices=vertices, **polygon)
    if np.max(abs(polygon["wall_tensor"]+polygon["photon_tensor"])) > 2e-13:
        raise ValueError("Static path virial balance failed")
    initial_depth = 2*np.pi*STORE_RADIUS*INITIAL_RADIUS**2/(STORE_MASS*.5*(INITIAL_RADIUS**2-1))
    lifetime_numerator = 2*np.pi*STORE_RADIUS*INITIAL_RADIUS*np.log(1/initial_depth)
    matplotlib_version = plot_trials(args.output)
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, matplotlib=matplotlib_version),
        parameters=dict(store_reference_inventory_over_C=STORE_MASS, store_reference_radius_over_delay=STORE_RADIUS,
            initial_store_radius=INITIAL_RADIUS, baseline_half_period_over_delay=HALF_PERIOD,
            hydrogen_specific_energy_fraction=HYDROGEN_FRACTION),
        store_trials=trials, refinement_checks=refinements, histories=histories,
        idle_absorption=dict(initial_extraction_depth=initial_depth,
            lifetime_times_absorption_depth_over_delay=lifetime_numerator,
            lifetime_at_0_62_ppm_over_delay=lifetime_numerator/.62e-6,
            assumptions="Quasistatic idle store; coherent absorption becomes trapped heat; no loss-replacement source"),
        finite_splitter=dict(phase_ramp_time_over_delay=HALF_PERIOD/4,
            maximum_delivery_energy_lag_over_C=HALF_PERIOD/8,
            exact_prescribed_receipts_recovered=False, reference_capacitance_F=1e-12,
            reference_halfwave_voltage_V=1.5, estimated_electrical_cycle_energy_J=2.25e-12,
            dimensional_energy_mapping_assigned=False),
        physical_store_material_identified=False, physical_splitter_fits_assembly_budget=False,
        all_frequency_store_stability_established=False, variable_load_route_material_evolution_closed=False,
        actual_target_tensor_and_macro_work_rematched=False, heat_export_and_replacement_supply_closed=False,
        physical_current_hosts_resolved=False, full_containment_established=False)
    (args.output / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    modules = ("optical_assembly", "constitutive_joints_and_optics", "controlled_optical_transfer",
               "material_reconfiguration", "finite_containment", "containment_ensemble", "magnetic_load_balance")
    paths = [Path(__file__).resolve(), ROOT / "toolkit/adm_harness_cli/tests/test_optical_assembly.py",
             *[ROOT / "toolkit/adm_harness_cli/adm_harness" / (n+".py") for n in modules]]
    for p in paths:
        shutil.copyfile(p, args.output / ("execution_"+p.name))
    outputs = {p.name: sha256(p) for p in sorted(args.output.iterdir()) if p.is_file() and p.name != "manifest.json"}
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        parent_manifest_sha256={str((d / "manifest.json").relative_to(ROOT)): sha256(d / "manifest.json")
                                for d in (PARENT, JOINTS, MACRO)}, output_sha256=outputs)
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
