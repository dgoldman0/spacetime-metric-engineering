#!/usr/bin/env python3
"""Audit conserved series joints and reduced optical-ring dynamics.

Independent histories and optical drive trials use four workers. Outputs
are numerical evidence; the supporting narrative is written manually.
Optical sizing is a conditional projection, with residual stresses saved.
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
from scipy.integrate import quad_vec, solve_ivp

from adm_harness.constitutive_joints_and_optics import (
    panel_reserve_lower_bound, prepare_series_joints, ring_equilibrium, ring_rhs,
    ring_state, series_panel_state, series_power_bounds,
)
from adm_harness.material_reconfiguration import MATERIAL_DIMENSIONS, MATERIAL_NAMES, PRESSURE_BASIS


ROOT = Path(__file__).resolve().parents[3]
PARENT = ROOT / "supporting_reports/data/distributed_reconfiguration"
MATERIAL = ROOT / "supporting_reports/data/material_reconfiguration"
ALPHA = 1e-4
BIAS, PEAK, ESCAPE = .25, .4, 1.
RADIUS_CAP, ENERGY_CAP = 1.5, 1.30


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extrema(array):
    return dict(minimum=float(np.min(array)), maximum=float(np.max(array)))


def read_verified(directory, name):
    manifest = json.loads((directory / "manifest.json").read_text())
    path = directory / name
    if sha256(path) != manifest["output_sha256"][name]:
        raise ValueError(f"Parent evidence hash mismatch: {path}")
    return path


def optical_trial(task):
    name, output_directory, bias, peak, escape, resonant, refined = task
    output = Path(output_directory)
    start = ring_equilibrium(bias, escape_depth=escape)
    state = np.r_[start["state"], 0.]
    duration = np.pi/np.sqrt(1-(bias+peak)/2) if resonant else 500.
    segments = 160 if resonant else 4
    step = .125 if refined else .25
    clock = 0.
    times, states, commands = [], [], []
    crossing = None
    def tensile_boundary(t, y):
        return y[0]-1
    tensile_boundary.terminal = True
    tensile_boundary.direction = -1
    for segment in range(segments):
        fraction = peak if segment % 2 == 0 else bias
        power = ring_equilibrium(fraction, escape_depth=escape)["input_power"]
        solution = solve_ivp(lambda t, y: ring_rhs(y, power, escape_depth=escape),
            (0, duration), state, method="DOP853", dense_output=True, max_step=step,
            rtol=2e-11 if refined else 2e-9, atol=2e-13 if refined else 2e-11,
            events=tensile_boundary)
        if not solution.success:
            raise ValueError(solution.message)
        actual_duration = float(solution.t[-1])
        # Nested output grids compare identical physical times under
        # refinement, avoiding interpolation error between curved orbits.
        intervals = int(np.ceil(actual_duration/.25))*(2 if refined else 1)
        grid = np.linspace(0, actual_duration, intervals+1)
        history = solution.sol(grid)
        times.append(clock+grid)
        states.append(history)
        commands.append(np.full(grid.shape, power))
        state = history[:, -1]
        clock += actual_duration
        if solution.status == 1:
            crossing = clock
            break
    time, y, command = np.concatenate(times), np.concatenate(states, axis=1), np.concatenate(commands)
    values = ring_state(*y[:3])
    energy_error = float(np.max(np.abs(values["energy"]-ring_state(*start["state"])["energy"]-y[3])))
    if energy_error > 1e-8 or not np.all(np.diff(time) >= 0):
        raise ValueError("Optical energy integral or time ordering failed")
    np.savez_compressed(output / (name+"_states.npz"), time=time, radius=y[0], radial_momentum=y[1],
        photon_action=y[2], integrated_port_power=y[3], input_power=command, **values)
    result = dict(name=name, bias_fraction=bias, peak_fraction=peak, escape_depth=escape,
        near_resonance=resonant, switching_interval=duration, requested_segments=segments,
        completed_time=clock, sample_spacing_bound=step, refined=refined,
        tensile_boundary_crossing_time=crossing, radius=extrema(y[0]),
        maximum_radial_speed=float(np.max(abs(values["speed"]))), energy=extrema(values["energy"]),
        maximum_kinetic_energy=float(values["kinetic_energy"].max()),
        pressure_trace=extrema(values["pressure_trace"]), maximum_energy_balance_error=energy_error,
        steady_bias_eigenvalues=[[float(v.real), float(v.imag)] for v in start["eigenvalues"]],
        within_selected_radius_and_energy_caps=bool(crossing is None and y[0].max() <= RADIUS_CAP
                                                    and values["energy"].max() <= ENERGY_CAP))
    print(name, "radius", result["radius"], "peak speed", result["maximum_radial_speed"],
          "tensile boundary", crossing, flush=True)
    return result


def audit_history(task):
    name, output_directory = task
    output = Path(output_directory)
    archive = read_verified(PARENT, name+"_states.npz")
    macro_archive = read_verified(MATERIAL, name+"_states.npz")
    summary = read_verified(PARENT, "summary.json")
    parent = next(h for h in json.loads(summary.read_text())["histories"] if h["label"] == name)
    if parent["input_sha256"][str(macro_archive.relative_to(ROOT))] != sha256(macro_archive):
        raise ValueError("Scheduled history and macro history have different provenance")
    with np.load(archive) as saved:
        T, M, previous_energy, gap, time, labels = (saved[k] for k in
            ("material_tension", "material_inventory", "component_energy", "local_transit_delay", "t", "x"))
    with np.load(macro_archive) as saved:
        target, lr, lt, dt = (saved[k] for k in ("target", "lr", "lt", "proper_panel_duration"))
        np.testing.assert_array_equal(time, saved["t"])
        np.testing.assert_array_equal(labels, saved["x"])
    fields = previous_energy[6:10]
    prep = prepare_series_joints(T, M, reference_fraction=ALPHA)
    joint_M, state = prep["joint_inventory_per_direction"], prep["state"]
    energies = np.concatenate([state["core_energy"],
        MATERIAL_DIMENSIONS[:, None, None]*state["joint_energy_per_direction"], fields])
    reserve = target[0]-energies.sum(axis=0)
    energies = np.concatenate([energies, reserve[None]])
    stresses = np.einsum("ki,itj->kitj", PRESSURE_BASIS[:, :6], state["core_tension"])
    joint_stresses = np.einsum("ki,itj->kitj", PRESSURE_BASIS[:, :6], state["joint_tension"])
    field_stresses = np.einsum("ki,itj->kitj", PRESSURE_BASIS[:, 6:10], fields)
    pressure = np.concatenate([stresses, joint_stresses, field_stresses, np.zeros((2, 1, *lr.shape))], axis=1)
    reconstructed = np.stack([energies.sum(axis=0), pressure[0].sum(axis=0), .5*pressure[1].sum(axis=0)])
    tensor_error = float(np.max(np.abs(reconstructed-target)))
    force_error = float(np.max(np.abs(state["joint_tension"]/(ALPHA*state["joint_stretch"])
                                             -state["core_tension"]/state["core_linear_stretch"])))
    virtual_work_error = float(np.max(np.abs(state["core_energy_derivative"]+state["joint_energy_derivative"]
                           -MATERIAL_DIMENSIONS[:, None, None]*T*state["cell_log_derivative"])))
    bound = series_power_bounds(T, M, joint_M, fields, target, lr, lt, dt, reference_fraction=ALPHA)
    reserve_bound = panel_reserve_lower_bound(reserve, dt, bound["lower"][-2], bound["upper"][-2])
    bound_error, balance_error = 0., 0.
    minimum_checked_interior = np.inf
    for u in (0., .25, .5, .75, 1.):
        actual = series_panel_state(T, M, joint_M, fields, target, lr, lt, dt, u, reference_fraction=ALPHA)
        bound_error = max(bound_error, float(np.max(actual["power"]-bound["upper"])),
                          float(np.max(bound["lower"]-actual["power"])))
        balance_error = max(balance_error, float(np.max(abs(actual["power"].sum(axis=0)))))
        if np.min(actual["remaining_reserve"]-reserve_bound) < -2e-12:
            raise ValueError("Interior reserve fell below its derivative-envelope bound")
        minimum_checked_interior = min(minimum_checked_interior, float(actual["remaining_reserve"].min()))
    if tensor_error > 2e-12 or force_error > 2e-12 or virtual_work_error > 2e-12 or bound_error > 2e-9 or balance_error > 2e-9:
        raise ValueError("Series force, tensor, virtual work or operating-power verification failed")
    if reserve_bound.min() <= 0 or state["joint_stretch"].max() > 2+2e-12:
        raise ValueError("Constitutive reserve or prepared stretch limit failed")

    # Integrate powers and pressure work separately, testing the energy
    # derivatives of the implicit constitutive law on selected panels.
    rng = np.random.default_rng(8237)
    panels = {tuple(np.unravel_index(i, dt.shape)) for i in rng.choice(dt.size, 16, replace=False)}
    panels.add(tuple(np.unravel_index(np.max(bound["upper"], axis=0).argmax(), dt.shape)))
    integral_error = 0.
    for i, j in sorted(panels):
        sl = (slice(i, i+2), slice(j, j+1))
        panel_dt = dt[i:i+1, j:j+1]
        def evaluate(u):
            return series_panel_state(T[:, sl[0], sl[1]], M[:, j:j+1], joint_M[:, j:j+1],
                fields[:, sl[0], sl[1]], target[:, sl[0], sl[1]], lr[sl], lt[sl], panel_dt, u)
        integrated, _ = quad_vec(lambda u: evaluate(u)["power"][:, 0, 0]*dt[i, j],
                                  0, 1, epsabs=1e-12, epsrel=1e-10)
        def pressure_work(u):
            st = evaluate(u)["state"]
            core = PRESSURE_BASIS[:, :6]*st["core_tension"][:, 0, 0]
            joints = PRESSURE_BASIS[:, :6]*st["joint_tension"][:, 0, 0]
            ff = PRESSURE_BASIS[:, 6:10]*((1-u)*fields[:, i, j]+u*fields[:, i+1, j])
            stress = np.concatenate([core, joints, ff, np.zeros((2, 1))], axis=1)
            return stress[0]*np.log(lr[i+1, j]/lr[i, j])+stress[1]*np.log(lt[i+1, j]/lt[i, j])
        work, _ = quad_vec(pressure_work, 0, 1, epsabs=1e-12, epsrel=1e-10)
        expected = energies[:, i+1, j]-energies[:, i, j]+work
        expected = np.r_[expected, -expected.sum()]
        integral_error = max(integral_error, float(np.max(abs(integrated-expected))))
    if integral_error > 1e-10:
        raise ValueError("Independent energy/work integration failed")

    peaks = np.maximum(bound["upper"].max(axis=1), 0.)
    total_peak = peaks.sum(axis=0)
    capacity = gap*total_peak
    reference_radius = gap/(2*np.pi*RADIUS_CAP)
    guide_M = 4*np.pi*reference_radius*total_peak/(ESCAPE*(PEAK-BIAS))
    initial_energy = 1/np.sqrt(1-BIAS)
    buffer_precharge = capacity+guide_M*(ENERGY_CAP-initial_energy)
    projection_cost = capacity+guide_M*ENERGY_CAP
    projected_reserve = reserve-projection_cost
    projected_bound = reserve_bound-projection_cost
    proper_time = np.concatenate([np.zeros((1, dt.shape[1])), np.cumsum(dt, axis=0)], axis=0)
    bias_power = BIAS/(PEAK-BIAS)*total_peak
    sampled_loss_ceiling = np.min(projected_reserve[1:]/(bias_power*proper_time[1:]), axis=0)
    sufficient_loss_fraction = np.min(projected_bound/(bias_power*proper_time[1:]), axis=0)
    if projected_bound.min() <= 0:
        raise ValueError("Selected optical sizing projection exceeds the energy budget")
    names = MATERIAL_NAMES+tuple(n+"_series_joints" for n in MATERIAL_NAMES)+(
        "hoop_maxwell", "radial_maxwell", "radial_photons", "angular_photons", "remaining_inventory", "retained_rail_port")
    np.savez_compressed(output / (name+"_states.npz"), t=time, x=labels, node_names=np.array(names),
        material_inventory=M, joint_inventory_per_direction=joint_M, effective_material_tension=T,
        core_tension=state["core_tension"], joint_tension=state["joint_tension"],
        core_linear_stretch=state["core_linear_stretch"], joint_stretch=state["joint_stretch"],
        joint_to_core_span=state["joint_to_core_span"], component_energy=energies,
        remaining_reserve=reserve, all_panel_reserve_lower_bound=reserve_bound,
        node_positive_power_peak=peaks, local_transit_delay=gap, total_reception_capacity=capacity,
        guide_reference_radius=reference_radius, guide_reference_inventory=guide_M,
        buffer_precharge=buffer_precharge, optical_projection_cost=projection_cost,
        remaining_reserve_after_optical_projection=projected_reserve,
        all_panel_projected_reserve_lower_bound=projected_bound, recycled_bias_power=bias_power,
        proper_time=proper_time, sampled_retained_loss_fraction_ceiling=sampled_loss_ceiling,
        sufficient_retained_loss_fraction=sufficient_loss_fraction)
    row = dict(label=name, samples=list(lr.shape),
        input_sha256={str(p.relative_to(ROOT)): sha256(p) for p in (archive, macro_archive, summary)},
        series_joints=dict(reference_length_fraction=ALPHA,
            total_joint_reference_inventory=extrema(prep["total_joint_reference_energy"]),
            maximum_joint_stretch=float(state["joint_stretch"].max()),
            maximum_core_stretch=float(state["core_linear_stretch"].max()),
            actual_joint_to_core_span_ratio=extrema(state["joint_to_core_span"]),
            minimum_reserve=float(reserve.min()), all_panel_minimum_reserve_bound=float(reserve_bound.min()),
            minimum_checked_interior_reserve=minimum_checked_interior),
        optical_sizing_projection=dict(reception_capacity=extrema(capacity),
            summed_useful_peak_power=extrema(total_peak), guide_reference_inventory=extrema(guide_M),
            guide_reference_radius=extrema(reference_radius), buffer_precharge=extrema(buffer_precharge),
            prepared_total_energy=extrema(projection_cost), minimum_remaining_reserve=float(projected_reserve.min()),
            all_panel_remaining_reserve_bound=float(projected_bound.min()),
            maximum_fraction_of_label_minimum_reserve=float(np.max(projection_cost/reserve.min(axis=0))),
            recycled_bias_power=extrema(bias_power),
            sampled_retained_loss_fraction_ceiling=extrema(sampled_loss_ceiling),
            sufficient_retained_loss_fraction=extrema(sufficient_loss_fraction),
            minimum_macro_panel_over_optical_reference_time=float(np.min(dt/reference_radius)),
            energy_cap_is_tested_envelope=True, arbitrary_drive_cap_certified=False,
            external_path_and_port_reactions_counted=False, transient_pressure_target_rematched=False),
        verification=dict(maximum_tensor_error=tensor_error, maximum_force_error=force_error,
            maximum_virtual_work_error=virtual_work_error, maximum_power_balance_error=balance_error,
            maximum_power_bound_error=bound_error, independently_integrated_panels=len(panels),
            maximum_power_integral_error=integral_error),
        inherited_current_host_rejections=parent["inherited_current_host_rejections"])
    print(name, "series reserve", reserve.min(), "conditional optical reserve", projected_bound.min(), flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_reports/data/constitutive_joints_and_optics")
    args = parser.parse_args()
    if args.workers < 1 or args.output.exists():
        parser.error("positive workers and a fresh output directory required")
    args.output.mkdir(parents=True)
    cases = [("optical_steps", BIAS, PEAK, ESCAPE, False, False),
             ("optical_steps_refined", BIAS, PEAK, ESCAPE, False, True),
             ("optical_half_escape", BIAS, PEAK, .5, False, False),
             ("optical_resonant", BIAS, PEAK, ESCAPE, True, False),
             ("optical_resonant_refined", BIAS, PEAK, ESCAPE, True, True),
             ("optical_low_bias_resonant", .1, PEAK, ESCAPE, True, False)]
    parent_summary = read_verified(PARENT, "summary.json")
    names = [h["label"] for h in json.loads(parent_summary.read_text())["histories"]]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        optical = list(pool.map(optical_trial, [(c[0], str(args.output), *c[1:]) for c in cases]))
        histories = list(pool.map(audit_history, [(name, str(args.output)) for name in names]))
    refinements = []
    for name in ("optical_steps", "optical_resonant"):
        with np.load(args.output / (name+"_states.npz")) as coarse, np.load(args.output / (name+"_refined_states.npz")) as fine:
            errors = {key: float(np.max(abs(coarse[key]-np.interp(coarse["time"], fine["time"], fine[key]))))
                      for key in ("radius", "radial_momentum", "photon_action", "energy", "pressure_trace")}
        if max(errors.values()) > 2e-8:
            raise ValueError("Optical integration refinement disagrees")
        refinements.append(dict(name=name, maximum_state_differences=errors))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        scope="Conserved force-matched local series joints; axisymmetric optical dynamics; conditional energy sizing",
        parameters=dict(joint_reference_fraction=ALPHA, maximum_prepared_joint_stretch=2.,
            optical_bias_fraction=BIAS, optical_peak_fraction=PEAK, optical_escape_depth=ESCAPE,
            optical_radius_envelope=RADIUS_CAP, optical_energy_envelope=ENERGY_CAP),
        optical_envelope_is_empirical=True, full_history_optical_dynamics_integrated=False,
        optical_transient_pressure_target_rematched=False, external_optical_port_reactions_supplied=False,
        microscopic_reflectors_supplied=False, spatial_joint_embedding_solved=False,
        current_hosts_solved=False, physical_material_identified=False, full_containment_established=False,
        optical_trials=optical, refinement_checks=refinements, histories=histories)
    (args.output / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(), *[ROOT / "toolkit/adm_harness_cli/adm_harness" / (name+".py") for name in
        ("constitutive_joints_and_optics", "material_reconfiguration", "distributed_reconfiguration",
         "finite_containment", "containment_ensemble", "magnetic_load_balance")],
        ROOT / "toolkit/adm_harness_cli/tests/test_constitutive_joints_and_optics.py"]
    for path in paths:
        shutil.copyfile(path, args.output / ("execution_"+path.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        parent_manifest_sha256={str(p.relative_to(ROOT)): sha256(p) for p in (PARENT / "manifest.json", MATERIAL / "manifest.json")},
        output_sha256={p.name: sha256(p) for p in args.output.iterdir() if p.is_file()})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
