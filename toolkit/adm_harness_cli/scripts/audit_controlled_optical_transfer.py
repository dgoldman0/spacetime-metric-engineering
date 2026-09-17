#!/usr/bin/env python3
"""Audit delayed optical control, dispatch and inherited transfer budgets.

Independent drive trials and rail histories use four workers. This script
emits numerical evidence; its accompanying narrative is written manually.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from itertools import product
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

from adm_harness.constitutive_joints_and_optics import series_panel_state
from adm_harness.controlled_optical_transfer import sampled_control_modes, simulate_transfer, transfer_envelope


ROOT = Path(__file__).resolve().parents[3]
PARENT = ROOT / "supporting_reports/data/constitutive_joints_and_optics"
MATERIAL = ROOT / "supporting_reports/data/material_reconfiguration"
GAINS = dict(action_gain=.02, momentum_gain=-.05)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extrema(array):
    return dict(minimum=float(np.min(array)), maximum=float(np.max(array)))


def verified(directory, filename):
    manifest = json.loads((directory / "manifest.json").read_text())
    path = directory / filename
    if sha256(path) != manifest["output_sha256"][filename]:
        raise ValueError(f"Evidence hash mismatch: {path}")
    return path


def control_modes():
    grid = []
    for action, momentum in product((0., .01, .02, .05, .1, .2), (-.2, -.1, -.05, -.02, 0., .02, .05, .1)):
        result = sampled_control_modes(mode="feedback", action_gain=action, momentum_gain=momentum)
        grid.append(dict(action_gain=action, momentum_gain=momentum,
                         spectral_radius=result["spectral_radius"], asymptotic_exponent=result["asymptotic_exponent"]))
    best = min(grid, key=lambda r: r["spectral_radius"])
    if any(best[k] != v for k, v in GAINS.items()):
        raise ValueError("Selected gains differ from the reproduced finite-grid result")
    sensitivity = []
    for fraction, delay_samples, actuator in product((.35, .4, .45), (16, 18, 20, 22, 24), (.125, .25, .5)):
        result = sampled_control_modes(mode="feedback", operating_fraction=fraction,
            total_flight_delay=delay_samples*3*np.pi/20, actuator_time=actuator, **GAINS)
        sensitivity.append(dict(operating_fraction=fraction, delay_samples=delay_samples,
            actuator_time=actuator, spectral_radius=result["spectral_radius"]))
    modes = []
    for mode in ("constant", "feedback", "aggressive"):
        result = sampled_control_modes(mode=mode, **GAINS)
        modes.append(dict(mode=mode, spectral_radius=result["spectral_radius"],
            asymptotic_exponent=result["asymptotic_exponent"],
            eigenvalues=[[float(v.real), float(v.imag)] for v in result["eigenvalues"]]))
    return dict(sample_period=3*np.pi/20, total_signal_and_power_delay=3*np.pi,
                actuator_time=.25, selected_gains=GAINS, gain_grid=grid,
                sensitivity_grid=sensitivity, nominal_modes=modes)


def optical_trial(task):
    name, output_directory, parameters, refined = task
    arguments = dict(parameters, **GAINS)
    if refined:
        arguments.update(maximum_step=.0625, rtol=2e-11, atol=2e-13)
    result = simulate_transfer(**arguments)
    state, history, env = result["ring"], result["history"], result["envelope"]
    error = np.linalg.norm(history[:3]-result["equilibrium"]["state"][:, None], axis=0)
    above = np.flatnonzero(error > .01*error[0]) if error[0] > 1e-14 else np.array([], dtype=int)
    settling = None if len(above) and above[-1] == len(error)-1 else (
        float(result["time"][above[-1]+1]) if len(above) else 0.)
    ledger_error = float(np.max(abs(result["ledger_energy"]-env["prepared_energy"])))
    ring_error = float(np.max(abs(result["ring_energy_balance_error"])))
    peak = result["equilibrium"]["input_power"]
    path_error = max(float(np.max(result["feed_path_energy"]-env["feed_path_energy_ceiling"])),
                     float(np.max(result["output_path_energy"]-env["output_path_energy_ceiling"])), 0.)
    q_error = max(float(history[3].max()-env["input_power_ceiling"]),
                  float(result["output_power"].max()-env["output_power_ceiling"]), 0.)
    if ledger_error > 2e-8 or ring_error > 2e-9 or path_error > 1e-9 or q_error > 1e-10:
        raise ValueError("Delayed optical energy or power-cap verification failed")
    if result["buffer_energy"].min() < env["buffer_floor"]-1e-10:
        raise ValueError("The receiving-store floor failed")
    if parameters["mode"] == "aggressive":
        if result["complete"] or result["boundary"] != "tensile":
            raise ValueError("The unstable delayed-controller control failed to reproduce")
    elif (not result["complete"] or abs(result["useful_energy"][-1]-result["requested_useful_energy"]) > 1e-12
          or abs(result["external_inflight_energy"][-1]) > 1e-12):
        raise ValueError("A selected drive failed to deliver and drain its complete request")
    np.savez_compressed(Path(output_directory) / (name+"_states.npz"),
        time=result["time"], radius=history[0], momentum=history[1], photon_action=history[2],
        emitted_power=history[3], command_power=result["command"], guide_input_power=result["input_power"],
        guide_output_power=result["output_power"], arrived_output_power=result["arrived_output_power"],
        useful_power=result["useful_power"], useful_energy=result["useful_energy"],
        bypass_power=result["dispatch"]["bypass"], recycle_power=result["dispatch"]["recycle"],
        external_inflight_energy=result["external_inflight_energy"], feed_path_energy=result["feed_path_energy"],
        output_path_energy=result["output_path_energy"], buffer_energy=result["buffer_energy"],
        ledger_energy=result["ledger_energy"], guide_energy=state["energy"],
        radial_speed=state["speed"], pressure_trace=state["pressure_trace"])
    row = dict(name=name, parameters=arguments, refined=refined, complete=result["complete"],
        boundary=result["boundary"], end_time=float(result["time"][-1]), radius=extrema(history[0]),
        maximum_speed=float(np.max(abs(state["speed"]))), pressure_trace=extrema(state["pressure_trace"]),
        maximum_guide_energy=float(state["energy"].max()), minimum_buffer=float(result["buffer_energy"].min()),
        guaranteed_buffer_floor=float(env["buffer_floor"]), prepared_total_energy=float(env["prepared_energy"]),
        emitter_power_over_useful_peak=extrema(history[3]/peak),
        maximum_bypass_over_useful_peak=float(result["dispatch"]["bypass"].max()/peak),
        requested_useful_energy=result["requested_useful_energy"], delivered_useful_energy=float(result["useful_energy"][-1]),
        observed_one_percent_settling_time=settling, final_state_error=float(error[-1]),
        maximum_ledger_error=ledger_error, maximum_ring_energy_error=ring_error,
        maximum_path_bound_excess=path_error, maximum_power_bound_excess=q_error)
    print(name, "complete", row["complete"], "pressure", row["pressure_trace"],
          "buffer", row["minimum_buffer"], "settling", settling, flush=True)
    return row


def history_audit(task):
    name, output_directory = task
    archive = verified(PARENT, name+"_states.npz")
    macro = verified(MATERIAL, name+"_states.npz")
    parent_summary = verified(PARENT, "summary.json")
    parent = next(h for h in json.loads(parent_summary.read_text())["histories"] if h["label"] == name)
    if parent["input_sha256"][str(macro.relative_to(ROOT))] != sha256(macro):
        raise ValueError("Macro and joint history provenance differs")
    with np.load(archive) as saved:
        source = {k: saved[k] for k in ("t", "x", "node_names", "effective_material_tension", "material_inventory",
            "joint_inventory_per_direction", "component_energy", "remaining_reserve", "all_panel_reserve_lower_bound",
            "node_positive_power_peak", "local_transit_delay", "total_reception_capacity", "proper_time")}
    with np.load(macro) as saved:
        target, lr, lt, dt = (saved[k] for k in ("target", "lr", "lt", "proper_panel_duration"))
        np.testing.assert_array_equal(source["t"], saved["t"])
        np.testing.assert_array_equal(source["x"], saved["x"])
    peaks, delay = source["node_positive_power_peak"], source["local_transit_delay"]
    envelope = transfer_envelope(peaks, delay[None])
    C, cost = envelope["reception_capacity"].sum(axis=0), envelope["prepared_energy"].sum(axis=0)
    np.testing.assert_allclose(C, source["total_reception_capacity"], rtol=2e-14)
    np.testing.assert_allclose(cost, (23/3)*C, rtol=2e-14)
    remaining = source["remaining_reserve"]-cost
    continuous = source["all_panel_reserve_lower_bound"]-cost
    if continuous.min() <= 0:
        raise ValueError("Counted guide, paths and buffer exhaust the energy reserve")
    peak_error, balance_error, route_error = 0., 0., 0.
    maximum_receipt_fraction = 0.
    route_records, route_points = [], []
    for fraction in (0., .5, 1.):
        actual = series_panel_state(source["effective_material_tension"], source["material_inventory"],
            source["joint_inventory_per_direction"], source["component_energy"][12:16], target, lr, lt, dt, fraction)
        powers = actual["power"]
        demand, supply = np.maximum(powers, 0.), np.maximum(-powers, 0.)
        peak_error = max(peak_error, float(np.max(demand-peaks[:, None])))
        balance_error = max(balance_error, float(np.max(abs(powers.sum(axis=0)))))
        ratio = np.divide(demand, peaks[:, None], out=np.zeros_like(demand), where=peaks[:, None] > 0)
        maximum_receipt_fraction = max(maximum_receipt_fraction, float(ratio.max()))
        candidates = {(0, 0), (dt.shape[0]-1, dt.shape[1]-1),
            tuple(np.unravel_index(np.max(demand, axis=0).argmax(), dt.shape))}
        for panel, label in sorted(candidates):
            A, D = demand[:, panel, label], supply[:, panel, label]
            routing = np.outer(D, A)/A.sum() if A.sum() else np.zeros((len(A), len(A)))
            route_error = max(route_error, float(np.max(abs(routing.sum(axis=0)-A))),
                              float(np.max(abs(routing.sum(axis=1)-D))))
            route_records.append(routing)
            route_points.append((fraction, panel, label))
    if max(peak_error, balance_error, route_error) > 2e-9:
        raise ValueError("Inherited positive receipts or reciprocal routing failed")
    total_peak = peaks.sum(axis=0)
    # All nominal guide throughput is charged in this retained-heat screen.
    # Its energy-only limit leaves thermal pressure and export unresolved.
    loss_ceiling = np.min(remaining[1:]/(total_peak*source["proper_time"][1:]), axis=0)
    sufficient_loss = np.min(continuous/(total_peak*source["proper_time"][1:]), axis=0)
    np.savez_compressed(Path(output_directory) / (name+"_states.npz"),
        t=source["t"], x=source["x"], node_names=source["node_names"], node_peak_power=peaks,
        transit_delay=delay, **{k: v for k, v in envelope.items()},
        total_prepared_energy=cost, remaining_reserve=remaining, all_panel_reserve_lower_bound=continuous,
        sampled_throughput_loss_fraction_ceiling=loss_ceiling, sufficient_throughput_loss_fraction=sufficient_loss,
        routing_check_points=np.asarray(route_points), checked_routing_matrices=np.asarray(route_records))
    row = dict(label=name, samples=list(lr.shape),
        input_sha256={str(p.relative_to(ROOT)): sha256(p) for p in (archive, macro, parent_summary)},
        reception_capacity=extrema(C), prepared_total_energy=extrema(cost),
        guide_reference_inventory=extrema(envelope["guide_reference_inventory"].sum(axis=0)),
        nominal_minimum_preparation=extrema(envelope["nominal_minimum_preparation"].sum(axis=0)),
        minimum_remaining_reserve=float(remaining.min()), all_panel_remaining_reserve_bound=float(continuous.min()),
        maximum_fraction_of_label_minimum_reserve=float(np.max(cost/source["remaining_reserve"].min(axis=0))),
        minimum_nominal_receiver_energy=float(np.min(envelope["initial_buffer"].sum(axis=0)-C)),
        sampled_throughput_loss_fraction_ceiling=extrema(loss_ceiling), sufficient_throughput_loss_fraction=extrema(sufficient_loss),
        nominal_guide_solution_exact=True, positive_receipts_bounded_for_continuous_interpolation=True,
        nominal_external_and_internal_flight_energy_counted=True,
        dynamic_envelope_is_conditional=True, physical_store_and_splitter_supplied=False,
        external_path_and_splitter_stresses_matched=False,
        verification=dict(maximum_peak_power_excess=peak_error, maximum_power_balance_error=balance_error,
            maximum_routing_error=route_error, maximum_sampled_receipt_fraction=maximum_receipt_fraction,
            checked_routing_matrices=len(route_records)),
        inherited_current_host_rejections=parent["inherited_current_host_rejections"])
    print(name, "counted control reserve", row["all_panel_remaining_reserve_bound"], flush=True)
    return row


def plot_response(output):
    """Plot measured trajectories without generating narrative text."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    equilibrium = np.array([1/np.sqrt(.6), 0., 1/3])
    figure, axes = plt.subplots(2, 1, figsize=(8, 6), constrained_layout=True)
    cases = [("passive_reference", "Constant loading", "#64748b"),
             ("feedback_reference_refined", "Selected feedback", "#1665a5"),
             ("aggressive_reference_refined", "Aggressive feedback", "#bd3b35")]
    for name, label, color in cases:
        with np.load(output / (name+"_states.npz")) as data:
            state = np.vstack([data["radius"], data["momentum"], data["photon_action"]])
            error = np.linalg.norm(state-equilibrium[:, None], axis=0)
            axes[0].plot(data["time"], data["pressure_trace"], label=label, color=color, linewidth=1.4)
            axes[1].semilogy(data["time"], np.maximum(error/error[0], 1e-12), color=color, linewidth=1.4)
    axes[0].set(xlim=(0, 80), ylabel=r"Pressure trace / $M_g$")
    axes[0].legend(loc="upper right", fontsize=9)
    axes[1].axhline(.01, color="#444444", linestyle=":", linewidth=1., label="1% of initial state error")
    axes[1].set(xlim=(0, 220), ylim=(1e-7, 20), ylabel="State error / initial error", xlabel=r"Time / $(R_0/c)$")
    axes[1].legend(loc="lower left", fontsize=9)
    for axis in axes:
        axis.grid(alpha=.2)
    figure.savefig(output / "delayed_control_response.png", dpi=180)
    plt.close(figure)
    return matplotlib.__version__


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_reports/data/controlled_optical_transfer")
    args = parser.parse_args()
    if args.workers < 1 or args.output.exists():
        parser.error("positive workers and a fresh output directory required")
    args.output.mkdir(parents=True)
    control = control_modes()
    ref = dict(initial_radius_fraction=.02, initial_momentum=.01, initial_action_fraction=-.02)
    cases = [("nominal_resonant_demand", dict(mode="constant"), False),
        ("passive_reference", dict(mode="constant", **ref), False),
        ("feedback_reference", dict(mode="feedback", **ref), False),
        ("feedback_reference_refined", dict(mode="feedback", **ref), True),
        ("aggressive_reference", dict(mode="aggressive", **ref), False),
        ("aggressive_reference_refined", dict(mode="aggressive", **ref), True)]
    for ix, ip, iz in product((-1, 1), repeat=3):
        if (ix, ip, iz) == (1, 1, -1):
            continue
        label = "feedback_corner_"+"".join("p" if a > 0 else "m" for a in (ix, ip, iz))
        cases.append((label, dict(mode="feedback", initial_radius_fraction=.02*ix,
            initial_momentum=.01*ip, initial_action_fraction=.02*iz), False))
    names = [h["label"] for h in json.loads(verified(PARENT, "summary.json").read_text())["histories"]]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        trials = list(pool.map(optical_trial, [(name, str(args.output), parameters, refined)
                                             for name, parameters, refined in cases]))
        histories = list(pool.map(history_audit, [(name, str(args.output)) for name in names]))
    refinements = []
    for name in ("feedback_reference", "aggressive_reference"):
        coarse_row = next(r for r in trials if r["name"] == name)
        fine_row = next(r for r in trials if r["name"] == name+"_refined")
        end_error = abs(coarse_row["end_time"]-fine_row["end_time"])
        with np.load(args.output / (name+"_states.npz")) as coarse, np.load(args.output / (name+"_refined_states.npz")) as fine:
            # An event changes the final short output grid. Earlier complete
            # sample intervals have identical output times under refinement.
            cutoff = min(coarse["time"][-1], fine["time"][-1])-3*np.pi/20
            valid = coarse["time"] <= cutoff
            errors = {key: float(np.max(abs(coarse[key][valid]-np.interp(coarse["time"][valid], fine["time"], fine[key]))))
                      for key in ("radius", "momentum", "photon_action", "guide_energy", "buffer_energy", "pressure_trace")}
        if max(errors.values()) > 2e-7 or end_error > 2e-7:
            raise ValueError("Delayed control refinement disagrees")
        refinements.append(dict(name=name, event_time_error=end_error, maximum_state_differences=errors))
    plot_version = plot_response(args.output)
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, matplotlib=plot_version),
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        scope="Steady optical guide loading with exact nominal dispatch; counted flight paths and store; delayed bounded feedback trials",
        parameters=dict(operating_fraction=.4, escape_depth=1., radius_cap=1.5, energy_cap=1.4,
            input_peak_multiple=1.5, output_peak_multiple=2., receiver_floor_fraction=.25,
            feed_delay_over_external_delay=.5, output_delay_over_external_delay=.5),
        control=control, optical_trials=trials, refinement_checks=refinements, histories=histories,
        nominal_continuous_transfer_construction=True, nonlinear_global_controller_certificate=False,
        physical_receiver_and_splitter_supplied=False, routing_reactions_matched=False,
        thermal_losses_closed=False, current_hosts_solved=False, physical_material_identified=False,
        full_containment_established=False)
    (args.output / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(), *[ROOT / "toolkit/adm_harness_cli/adm_harness" / (name+".py") for name in
        ("controlled_optical_transfer", "constitutive_joints_and_optics", "material_reconfiguration",
         "finite_containment", "containment_ensemble", "magnetic_load_balance")],
        ROOT / "toolkit/adm_harness_cli/tests/test_controlled_optical_transfer.py"]
    for path in paths:
        shutil.copyfile(path, args.output / ("execution_"+path.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        parent_manifest_sha256={str(p.relative_to(ROOT)): sha256(p) for p in (PARENT / "manifest.json", MATERIAL / "manifest.json")},
        output_sha256={p.name: sha256(p) for p in args.output.iterdir() if p.is_file()})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
