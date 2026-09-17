#!/usr/bin/env python3
"""Numerical evidence for scheduled transfer and mechanical holding.

Independent histories and transition trials use a bounded worker pool.
Narrative interpretation is authored separately from these measurements.
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
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

from adm_harness.constitutive_joints_and_optics import series_panel_state, series_power_bounds
from adm_harness.scheduled_optical_transfer import (
    CONVERTER_DELAY, CONVERTER_RAMP, INITIAL_ROTOR_ENERGY, PILOT_POWER, RAMP_TIME,
    ROTOR_DAMPING, ROTOR_MASS, ROTOR_RADIUS, SPIN_FLOOR,
    delayed_receipt_l2_bound, finite_loop_bounds, frozen_thermal_gain, guide_bounds, guide_drive_l2_bound,
    inverse_guide, preparation, receipt_derivative_bound, reflect_seed,
    rotor_rhs, rotor_state, schedule_exposure, simulate_transition, smooth_step,
)

ROOT = Path(__file__).resolve().parents[3]
PARENT = ROOT / "supporting_reports/data/controlled_optical_transfer"
JOINTS = ROOT / "supporting_reports/data/constitutive_joints_and_optics"
MACRO = ROOT / "supporting_reports/data/material_reconfiguration"
ASSEMBLY = ROOT / "supporting_reports/data/optical_assembly"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified(directory, name):
    path = directory / name
    expected = json.loads((directory / "manifest.json").read_text())["output_sha256"][name]
    if sha256(path) != expected:
        raise ValueError(f"Evidence hash mismatch: {path}")
    return path


def extrema(a):
    return dict(minimum=float(np.min(a)), maximum=float(np.max(a)))


def history_audit(task):
    name, output = task
    paths = [verified(d, name+"_states.npz") for d in (PARENT, JOINTS, MACRO, ASSEMBLY)]
    for directory, dependency in ((PARENT, paths[1]), (JOINTS, paths[2]), (ASSEMBLY, paths[0])):
        summary = json.loads(verified(directory, "summary.json").read_text())
        history = next(h for h in summary["histories"] if h["label"] == name)
        if history["input_sha256"][str(dependency.relative_to(ROOT))] != sha256(dependency):
            raise ValueError("Linked history provenance differs")
    with np.load(paths[0]) as a:
        parent = {k: a[k] for k in ("t", "x", "node_peak_power", "transit_delay", "reception_capacity")}
    with np.load(paths[1]) as a:
        joints = {k: a[k] for k in ("t", "x", "proper_time", "effective_material_tension", "material_inventory",
            "joint_inventory_per_direction", "component_energy", "remaining_reserve", "all_panel_reserve_lower_bound")}
    with np.load(paths[2]) as a:
        target, lr, lt, dt = (a[k] for k in ("target", "lr", "lt", "proper_panel_duration"))
        np.testing.assert_array_equal(parent["t"], a["t"])
        np.testing.assert_array_equal(parent["x"], a["x"])
    for key in ("t", "x"):
        np.testing.assert_array_equal(parent[key], joints[key])
    args = (joints["effective_material_tension"], joints["material_inventory"],
            joints["joint_inventory_per_direction"], joints["component_energy"][12:16], target, lr, lt, dt)
    powers = np.maximum(series_power_bounds(*args)["upper"], 0)
    peak, delay, Cnode = (parent[k] for k in ("node_peak_power", "transit_delay", "reception_capacity"))
    np.testing.assert_allclose(Cnode, peak*delay, rtol=2e-14, atol=1e-30)
    exposure = schedule_exposure(powers, peak, dt, delay)
    p0, p1 = (series_panel_state(*args, f)["power"] for f in (0., 1.))
    derivative = receipt_derivative_bound(*args)
    loop = finite_loop_bounds(powers, peak, dt, delay, derivative, p0, p1)
    prep, C = preparation(), Cnode.sum(axis=0)
    reserve = joints["remaining_reserve"]-prep["candidate_preparation"]*C
    continuous = joints["all_panel_reserve_lower_bound"]-prep["candidate_preparation"]*C
    if continuous.min() <= 0:
        raise ValueError("Scheduled preparation exceeds an inherited energy reserve")
    optical = (exposure["total_exposure_upper"]-exposure["bootstrap_upper"]
               +loop["restart_exposure_upper"]+loop["loop_exposure_upper"])
    # Replacing alpha*exposure through the matched converter adds at most
    # 1/jmin optical exposure per unit replacement, including its own loss.
    loss_ceiling = np.min(continuous/(optical+continuous/SPIN_FLOOR), axis=0)
    nominal = peak.sum(axis=0)*joints["proper_time"][1:]
    comparisons = []
    for alpha in (.62e-6, .74e-6, 1e-6, 3e-6, 1-10**(-.4/10)):
        replacement_factor = 1/(1-alpha/SPIN_FLOOR)
        replacement_cost = alpha*optical*replacement_factor
        remaining = continuous-replacement_cost
        # beta is fractional total prepared rotor energy dissipated per delta.
        # This is energy headroom only; local retained drag heat also needs
        # a separate thermal-action/spin allocation in every rotor.
        drag_ceiling = np.min(remaining/(replacement_factor*ROTOR_MASS*INITIAL_ROTOR_ENERGY*nominal), axis=0)
        comparisons.append(dict(assigned_loss_per_exposure=alpha,
            minimum_continuous_reserve_after_loss=float(remaining.min()),
            minimum_final_reserve_after_loss=float((reserve[-1]-replacement_cost[-1]).min()),
            labels_with_negative_continuous_bound=int(np.count_nonzero(np.min(remaining, axis=0) < 0)),
            final_loss_replacement_cost_upper=extrema(replacement_cost[-1]),
            energy_only_holding_drag_fraction_per_delay_ceiling=extrema(drag_ceiling)))
    receipt_l2 = delayed_receipt_l2_bound(p0, p1, derivative, peak, dt, delay)
    guide_l2 = guide_drive_l2_bound(powers, peak)
    ideal_q2 = 2*(receipt_l2+guide_l2)
    # Minkowski combines the previous source bound with loop fill/drain.
    q2 = (np.sqrt(ideal_q2)+np.sqrt(loop["loop_drive_l2_upper"]))**2
    hfloor = prep["quasistatic_rotor_energy_floor"]
    gain = float(max(frozen_thermal_gain(hfloor), frozen_thermal_gain(INITIAL_ROTOR_ENERGY)))
    frozen_heat = gain*q2
    cumulative_heat = (Cnode[:, None]*frozen_heat).sum(axis=0)
    sweep = []
    for mass, damping in ((14., .2), (14., .4), (16., .4), (18., .2), (18., .4), (20., .4)):
        candidate = preparation(inventory=mass)
        g = float(max(frozen_thermal_gain(candidate["quasistatic_rotor_energy_floor"], inventory=mass, damping=damping),
                      frozen_thermal_gain(INITIAL_ROTOR_ENERGY, inventory=mass, damping=damping)))
        heat = g*q2[:, -1]
        headroom = joints["all_panel_reserve_lower_bound"]-candidate["candidate_preparation"]*C
        sweep.append(dict(rotor_reference_inventory=mass, damping=damping,
            preparation=candidate["candidate_preparation"],
            quasistatic_heat_capacity=candidate["quasistatic_heat_energy_capacity"],
            maximum_frozen_linear_heat_over_C=float(heat.max()),
            maximum_frozen_heat_to_capacity_ratio=float(heat.max()/candidate["quasistatic_heat_energy_capacity"]),
            minimum_continuous_reserve_after_0_62_ppm=float((headroom-.62e-6*optical/(1-.62e-6/SPIN_FLOOR)).min())))
    np.savez_compressed(Path(output) / (name+"_states.npz"), t=parent["t"], x=parent["x"],
        capacity=C, prepared_energy=prep["candidate_preparation"]*C,
        remaining_reserve=reserve, all_panel_reserve_lower_bound=continuous,
        sufficient_common_loss_fraction=loss_ceiling,
        finite_loop_total_exposure_upper=optical,
        loop_exposure_upper=loop["loop_exposure_upper"],
        loop_restart_exposure_upper=loop["restart_exposure_upper"],
        loop_baseline_power_over_peak=loop["baseline_loop_power_over_peak"],
        nominal_guide_exposure=nominal, **{k: exposure[k] for k in (
            "useful_upper", "guide_upper", "converter_upper", "bootstrap_upper", "total_exposure_upper", "changed_plateaus")},
        cumulative_frozen_linear_heat=cumulative_heat,
        node_final_receipt_l2_upper=receipt_l2[:, -1], node_final_guide_l2_upper=guide_l2[:, -1],
        node_final_loop_l2_upper=loop["loop_drive_l2_upper"][:, -1],
        node_final_frozen_linear_heat_over_C=frozen_heat[:, -1])
    row = dict(label=name, samples=list(reserve.shape), input_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        preparation=extrema(prep["candidate_preparation"]*C),
        minimum_remaining_reserve=float(reserve.min()), all_panel_reserve_bound=float(continuous.min()),
        sufficient_common_loss_fraction=extrema(loss_ceiling),
        final_guide_over_old_nominal=extrema(exposure["guide_upper"][-1]/nominal[-1]),
        final_total_exposure_over_old_nominal=extrema(optical[-1]/nominal[-1]),
        maximum_final_useful_upper=float(exposure["useful_upper"][-1].max()),
        maximum_final_guide_upper=float(exposure["guide_upper"][-1].max()),
        maximum_final_converter_upper=float(exposure["converter_upper"][-1].max()),
        maximum_final_bootstrap_upper=float(exposure["bootstrap_upper"][-1].max()),
        maximum_final_loop_exposure_upper=float(loop["loop_exposure_upper"][-1].max()),
        maximum_loop_baseline_over_peak=float(loop["baseline_loop_power_over_peak"].max()),
        maximum_converter_events=int(loop["converter_events"].max()),
        minimum_panel_over_delay=exposure["minimum_panel_over_delay"],
        maximum_changed_plateaus_per_node=int(exposure["changed_plateaus"].max()),
        maximum_receipt_l2_upper=float(receipt_l2[:, -1].max()),
        maximum_guide_l2_upper=float(guide_l2[:, -1].max()),
        maximum_frozen_linear_heat_over_C=float(frozen_heat[:, -1].max()),
        maximum_ideal_port_frozen_heat_over_C=float((gain*ideal_q2[:, -1]).max()),
        maximum_frozen_heat_to_capacity_ratio=float(frozen_heat[:, -1].max()/prep["quasistatic_heat_energy_capacity"]),
        frozen_linear_heat_diagnostic_is_nonlinear_certificate=False,
        inventory_and_damping_sweep=sweep, retained_loss_comparisons=comparisons)
    print(name, "reserve", row["all_panel_reserve_bound"], "loss ppm", 1e6*loss_ceiling.min(), flush=True)
    return row


def transition_trial(task):
    name, parameters, save, output = task
    r = simulate_transition(**parameters)
    energy_error = float(abs(r["complete_ledger_error"]).max())
    if energy_error > 2e-6 or np.diff(r["state"][3]).min() < -1e-10:
        raise ValueError("Transition energy or thermal-action check failed")
    row = dict(name=name, parameters=parameters, complete=r["complete"], boundary=r["boundary"],
        spin=extrema(r["state"][2]), radius=extrema(r["state"][0]),
        minimum_proper_stretch=float(r["proper_stretch"].min()),
        maximum_radial_speed=float(abs(r["radial_speed"]).max()),
        maximum_reaction_trace=float(abs(r["pressure_trace"]).max()),
        minimum_receipt_envelope_margin=float((r["guide_output"]-r["required_receipt"]).min()),
        maximum_thermal_energy=float(r["thermal_energy"].max()), final_thermal_energy=float(r["thermal_energy"][-1]),
        final_heat_action_increase=float(r["heat_action_increase"][-1]),
        maximum_energy_identity_error=energy_error,
        maximum_rotor_identity_error=float(abs(r["rotor_energy_balance_error"]).max()),
        maximum_net_power=float(abs(r["net_power"]).max()),
        minimum_converter_incident_margin=float(r["converter_incident_margin"].min()),
        maximum_converter_photon_energy=float(r["converter_photon_energy"].max()),
        maximum_total_port_exposure=float(r["ports"]["total_port_exposure"].max()))
    if parameters.get("finite_converter_loop") and (row["minimum_converter_incident_margin"] < -1e-10
            or row["maximum_converter_photon_energy"] > preparation()["converter_photon_capacity"]*(1+1e-12)):
        raise ValueError("Finite-loop allocation or photon capacity failed")
    if save:
        np.savez_compressed(Path(output) / (name+"_states.npz"), **{k: v for k, v in r.items()
            if isinstance(v, np.ndarray)}, port_input=r["ports"]["incoming"], port_output=r["ports"]["outgoing"])
    print(name, r["boundary"] or "completed", "heat", row["final_thermal_energy"], flush=True)
    return row


def seed_trial(equilibrium, output):
    """Local finite-recoil startup with counted, ideal redirected flights.

    The seed and final packet are included in the rotor-plus-packet ledger.
    Last-pass partial reflection holds the packet at its capacity. Direction
    matching, splitting and finite-loop regulation remain separate gates.
    """
    seed = PILOT_POWER*CONVERTER_DELAY
    h = equilibrium-seed/ROTOR_MASS
    y = np.array([h, 0., np.sqrt(h*h-1-2e-8), 1e-8])
    packet, target = seed, preparation()["converter_photon_capacity"]
    time, records, photons, clock = [0.], [y.copy()], [packet], 0.
    reflections = []
    initial_energy = ROTOR_MASS*rotor_state(y)["energy"]+packet
    maximum_error = 0.
    for _ in range(30):
        if packet >= target*(1-1e-12):
            break
        # Propagation permits free radial relaxation; stationary ideal turns
        # conserve packet energy and have reaction loads priced separately.
        sol = solve_ivp(lambda t, state: rotor_rhs(state, 0.), (0., CONVERTER_DELAY), y,
            method="DOP853", rtol=2e-11, atol=2e-13, max_step=.004)
        if not sol.success:
            raise ValueError(sol.message)
        y = sol.y[:, -1]
        clock += CONVERTER_DELAY
        def outgoing_total(incident):
            return packet if incident == 0 else packet-incident+reflect_seed(y, incident)["outgoing_energy"]
        incident = packet
        if outgoing_total(incident) > target:
            incident = brentq(lambda e: outgoing_total(e)-target, 0., packet, xtol=1e-15)
        r = reflect_seed(y, incident)
        old_packet = packet
        packet = packet-incident+r["outgoing_energy"]
        y = r["state"]
        rotor_state(y)
        if y[2] <= SPIN_FLOOR:
            raise ValueError("Seed bootstrap exhausted usable spin")
        error = ROTOR_MASS*rotor_state(y)["energy"]+packet-initial_energy
        maximum_error = max(maximum_error, abs(error))
        reflections.append(dict(time=clock, incident_energy=incident, outgoing_energy=r["outgoing_energy"],
            reflected_fraction=incident/old_packet, single_pass_gain=r["outgoing_energy"]/incident,
            packet_energy=packet, spin=float(y[2])))
        time.append(clock)
        records.append(y.copy())
        photons.append(packet)
    if packet < target*(1-1e-10) or maximum_error > 2e-9:
        raise ValueError("Finite seed trial failed capacity or conservation check")
    label = f"seed_h{equilibrium:g}"
    np.savez_compressed(Path(output) / (label+"_states.npz"), time=time, state=np.array(records).T, photon_energy=photons)
    return dict(name=label, nominal_preseed_equilibrium_radius=equilibrium,
        actual_initial_radius=float(records[0][0]), seed_energy=seed,
        reflections=reflections, latency=clock, maximum_photon_energy=max(photons),
        final_thermal_energy=float(ROTOR_MASS*rotor_state(y)["thermal_energy"]),
        maximum_energy_identity_error=float(maximum_error), minimum_spin=float(np.array(records)[:, 2].min()),
        complete_converter_controller_constructed=False, spatial_redirection_and_splitter_ideal=True)


def ramp_admission():
    bound = guide_bounds()
    powers = np.linspace(PILOT_POWER, 1+PILOT_POWER, 101)
    time = np.linspace(0, RAMP_TIME, 1001)
    minimum_input, maximum_input, minimum_photons = np.inf, 0., np.inf
    maximum_guide_trace = 0.
    for left in powers:
        g = inverse_guide(time[:, None], left, powers[None])
        minimum_input = min(minimum_input, float(g["input_power"].min()))
        maximum_input = max(maximum_input, float(g["input_power"].max()))
        minimum_photons = min(minimum_photons, float(g["photon_action"].min()))
        maximum_guide_trace = max(maximum_guide_trace, float(abs(g["pressure_trace"]).max()))
    if minimum_input <= 0 or minimum_photons <= 0 or maximum_input > bound["maximum_input_power"]:
        raise ValueError("Guide ramp admission failed")
    phase = np.linspace(0, CONVERTER_RAMP+CONVERTER_DELAY, 100001)
    maximum = 1.5/SPIN_FLOOR
    f = maximum*smooth_step(phase, CONVERTER_RAMP)[0]
    returning = maximum*smooth_step(phase-CONVERTER_DELAY, CONVERTER_RAMP)[0]
    difference = f-returning
    fill_margin = returning+PILOT_POWER-(1-SPIN_FLOOR)/(2*SPIN_FLOOR)*difference
    drain_margin = maximum-returning+PILOT_POWER-(1+SPIN_FLOOR)/(2*SPIN_FLOOR)*difference
    if min(fill_margin.min(), drain_margin.min()) <= 0:
        raise ValueError("Worst-spin loop ramp power allocation failed")
    return dict(endpoint_power_values=len(powers), phase_samples=len(time),
        minimum_input_power=minimum_input, maximum_input_power=maximum_input,
        minimum_photon_action=minimum_photons, maximum_guide_reaction_trace=maximum_guide_trace,
        loop_phase_samples=len(phase), minimum_worst_spin_loop_fill_margin=float(fill_margin.min()),
        minimum_worst_spin_loop_drain_margin=float(drain_margin.min()),
        input_positivity_is_grid_admission=True)


def plot_evidence(output, histories):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(3, 1, figsize=(8.2, 8.2), constrained_layout=True)
    for label, color in (("loop_up", "#1665a5"), ("loop_down", "#bd3b35")):
        with np.load(output / (label+"_states.npz")) as a:
            axes[0].plot(a["time"], a["rotor_energy"], label=label.replace("loop_", ""), color=color)
            axes[1].plot(a["time"], a["pressure_trace"], color=color)
            axes[2].plot(a["time"], a["thermal_energy"], color=color)
    axes[0].set(ylabel="Rotor energy / C")
    axes[0].legend()
    axes[1].set(ylabel="Rotor pressure trace / C")
    axes[2].set(ylabel="Contained thermal energy / C", xlabel="Time / useful transit delay")
    for ax in axes:
        ax.grid(alpha=.2)
    fig.savefig(output / "scheduled_transition.png", dpi=170)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(8.2, 4.5), sharey=True, constrained_layout=True)
    for ax, label, title, color in zip(axes,
            ("first_n32_t4113", "second_n32_t2057"),
            ("First location", "Second location"), ("#1665a5", "#bd3b35")):
        with np.load(output / (label+"_states.npz")) as a:
            ax.plot(a["x"], a["sufficient_common_loss_fraction"]*1e6, color=color)
        ax.axhline(.62, color="#555555", linestyle=":", label="Assigned 0.62 ppm")
        ax.set(xlabel="Material label", title=title, yscale="log")
        ax.grid(alpha=.2)
        ax.ticklabel_format(axis="x", style="sci", useOffset=True)
    axes[0].set_ylabel("Sufficient common loss allowance (ppm)")
    axes[1].legend(fontsize=9)
    fig.savefig(output / "scheduled_loss_allowance.png", dpi=170)
    plt.close(fig)
    return matplotlib.__version__


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_reports/data/scheduled_optical_transfer")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    cases = [("up", dict(left=0., right=1.), True), ("down", dict(left=1., right=0.), True),
             ("warm_up", dict(left=0., right=1., initial_heat=.02), True),
             ("warm_down", dict(left=1., right=0., initial_heat=.02), True),
             ("elastic_up", dict(left=0., right=1., damping=0.), True),
             ("small_store_up", dict(left=0., right=1., inventory=14., damping=.2), True)]
    cases += [("loop_up", dict(left=0., right=1., finite_converter_loop=True), True),
              ("loop_down", dict(left=1., right=0., finite_converter_loop=True), True),
              ("loop_warm_down", dict(left=1., right=0., initial_heat=.06, finite_converter_loop=True), True)]
    for left in (0., .25, .5, 1.):
        for right in (0., .25, .5, 1.):
            if left != right and (left, right) not in ((0., 1.), (1., 0.)):
                cases.append((f"step_{left:g}_{right:g}", dict(left=left, right=right), False))
    for name in ("up", "down", "warm_up", "loop_up"):
        base = next(p for n, p, _ in cases if n == name)
        cases.append((name+"_refined", dict(base, maximum_step=.02, rtol=2e-11, atol=2e-13), True))
    names = [h["label"] for h in json.loads(verified(PARENT, "summary.json").read_text())["histories"]]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        histories = list(pool.map(history_audit, [(n, str(args.output)) for n in names]))
        trials = list(pool.map(transition_trial, [(n, p, save, str(args.output)) for n, p, save in cases]))
    refinements = []
    for name in ("up", "down", "warm_up", "loop_up"):
        with np.load(args.output / (name+"_states.npz")) as a, np.load(args.output / (name+"_refined_states.npz")) as b:
            np.testing.assert_array_equal(a["time"], b["time"])
            error = float(abs(a["state"]-b["state"]).max())
            if error > 2e-7:
                raise ValueError("Transition refinement disagrees")
            refinements.append(dict(name=name, shared_samples=len(a["time"]), maximum_state_difference=error))
    seeds = [seed_trial(h, args.output) for h in (1.3, 1.12)]
    ramps = ramp_admission()
    matplotlib_version = plot_evidence(args.output, histories)
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, matplotlib=matplotlib_version),
        preparation=preparation(), rotor_reference_inventory=ROTOR_MASS, rotor_reference_radius=ROTOR_RADIUS,
        rotor_damping=ROTOR_DAMPING, spin_floor=SPIN_FLOOR, ramp_time=RAMP_TIME,
        guide_pilot=PILOT_POWER, converter_flight_time=CONVERTER_DELAY,
        converter_envelope_ramp_time=CONVERTER_RAMP,
        histories=histories, transition_trials=trials, refinement_checks=refinements,
        finite_seed_trials=seeds, ramp_grid_admission=ramps,
        physical_stiff_material_identified=False, finite_loop_step_power_allocation_tested=True,
        full_history_converter_port_feasibility_certified=False, finite_slew_converter_controller_constructed=False,
        optical_spectral_losses_qualified=False, full_history_nonlinear_thermal_evolution_integrated=False,
        variable_load_route_material_evolution_closed=False, actual_target_tensor_and_macro_work_rematched=False,
        physical_current_hosts_resolved=False, full_containment_established=False)
    (args.output / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    modules = ("scheduled_optical_transfer", "constitutive_joints_and_optics", "material_reconfiguration",
               "finite_containment", "containment_ensemble", "magnetic_load_balance")
    paths = [Path(__file__).resolve(), ROOT / "toolkit/adm_harness_cli/tests/test_scheduled_optical_transfer.py",
             *[ROOT / "toolkit/adm_harness_cli/adm_harness" / (n+".py") for n in modules]]
    for path in paths:
        shutil.copyfile(path, args.output / ("execution_"+path.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        parent_manifest_sha256={str((d / "manifest.json").relative_to(ROOT)): sha256(d / "manifest.json")
                                for d in (PARENT, JOINTS, MACRO, ASSEMBLY)},
        output_sha256={p.name: sha256(p) for p in sorted(args.output.iterdir()) if p.is_file() and p.name != "manifest.json"})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
