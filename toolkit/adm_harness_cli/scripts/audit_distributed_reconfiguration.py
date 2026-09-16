#!/usr/bin/env python3
"""Audit scheduled materials, delayed transport and ideal joint allowances.

Four independent histories use separate workers. This program emits
numerical evidence; the accompanying supporting report is written manually.
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
from scipy.integrate import quad_vec
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

from adm_harness.containment_ensemble import required_exchange
from adm_harness.distributed_reconfiguration import (
    exchange_power_bounds, instantaneous_exchange_power, joint_transport_envelope, joint_work_capacity,
    scheduled_replay, transport_capacity,
)
from adm_harness.finite_containment import geometry
from adm_harness.material_reconfiguration import (
    COMPONENT_NAMES, MATERIAL_DIMENSIONS, MATERIAL_NAMES, configuration_rate_bound,
    elastic_state_from_tension,
)


ROOT = Path(__file__).resolve().parents[3]
PARENT = ROOT / "supporting_reports/data/material_reconfiguration"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extrema(array):
    return dict(minimum=float(np.min(array)), maximum=float(np.max(array)))


def interval_program(lower, upper, proper_time):
    """Independent sparse LP over every field sample and one maximum rate."""
    n = len(lower)
    i = np.arange(n-1)
    rows = np.concatenate([2*i, 2*i, 2*i, 2*i+1, 2*i+1, 2*i+1])
    columns = np.concatenate([i, i+1, np.full(n-1, n), i, i+1, np.full(n-1, n)])
    dt = np.diff(proper_time)
    values = np.concatenate([-np.ones(n-1), np.ones(n-1), -dt,
                              np.ones(n-1), -np.ones(n-1), -dt])
    matrix = coo_matrix((values, (rows, columns)), shape=(2*(n-1), n+1)).tocsr()
    result = linprog(np.r_[np.zeros(n), 1.], A_ub=matrix, b_ub=np.zeros(2*(n-1)),
        bounds=[*zip(lower, upper), (0, None)], method="highs",
        options={"primal_feasibility_tolerance": 1e-10, "dual_feasibility_tolerance": 1e-10})
    if not result.success:
        raise ValueError(f"Independent schedule LP failed: {result.message}")
    dual = lower @ result.lower.marginals[:-1]+upper @ result.upper.marginals[:-1]
    return dict(optimum=float(result.fun), dual_lower_bound=float(dual),
                maximum_constraint_error=float(np.max(matrix @ result.x)))


def audit(task):
    name, output_directory = task
    output = Path(output_directory)
    manifest = json.loads((PARENT / "manifest.json").read_text())
    summary_path = PARENT / "summary.json"
    if sha256(summary_path) != manifest["output_sha256"][summary_path.name]:
        raise ValueError("Parent summary hash mismatch")
    parent = next(h for h in json.loads(summary_path.read_text())["histories"] if h["label"] == name)
    archive = PARENT / (name+"_states.npz")
    if sha256(archive) != manifest["output_sha256"][archive.name]:
        raise ValueError("Parent state hash mismatch")
    with np.load(archive) as data:
        saved = {k: data[k] for k in ("t", "x", "target", "field_floor", "inner_hoop", "outer_hoop",
                                      "lr", "lt", "proper_panel_duration")}
    meta_path = ROOT / "supporting_reports/data/magnetic_geometry" / (name+"_summary.json")
    if sha256(meta_path) != parent["input_sha256"][str(meta_path.relative_to(ROOT))]:
        raise ValueError("Geometry metadata hash mismatch")
    meta = json.loads(meta_path.read_text())
    source = ROOT / meta["input"]
    if sha256(source) != parent["input_sha256"][meta["input"]]:
        raise ValueError("Source geometry hash mismatch")
    with np.load(source) as data:
        state = {k: data[k] for k in ("t", "x", "D", "ell", "radius", "edges", "lapse")}
    for axis in ("t", "x"):
        np.testing.assert_array_equal(state[axis], saved[axis])
    lr, lt, dt = (saved[k] for k in ("lr", "lt", "proper_panel_duration"))
    np.testing.assert_allclose(lr, state["ell"]/state["ell"][0], rtol=0, atol=0)
    np.testing.assert_allclose(lt, state["radius"]/state["radius"][0], rtol=0, atol=0)
    recomputed_dt = .5*(state["lapse"][1:]+state["lapse"][:-1])*np.diff(state["t"])[:, None]
    np.testing.assert_allclose(dt, recomputed_dt, rtol=0, atol=0)
    result = scheduled_replay(saved["target"], saved["field_floor"],
                              saved["inner_hoop"], saved["outer_hoop"], dt)
    tension, energy, pressure = (result[k] for k in ("material_tension", "component_energy", "component_pressure"))
    reserve = result["remaining_reserve"]
    tensor_error = float(np.max(np.abs(result["reconstructed_tensor"]-saved["target"])))
    if tensor_error > 2e-12 or np.min(reserve-result["guaranteed_reserve"]) < -2e-12:
        raise ValueError("Scheduled materials lost their tensor or reserve guarantee")
    measured_slew = np.max(np.abs(np.diff(result["field_energy"], axis=0))/dt, axis=0)
    if np.max(measured_slew-result["field_slew"]) > 2e-9:
        raise ValueError("Field schedule violates its slew bound")
    selected = sorted(set([0, lr.shape[1]//2, lr.shape[1]-1, int(result["field_slew"].argmax())]))
    lp_checks = []
    for j in selected:
        check = interval_program(result["field_lower"][:, j], result["field_upper"][:, j],
                                 result["proper_time"][:, j])
        if max(abs(check["optimum"]-result["field_slew"][j]),
               abs(check["optimum"]-check["dual_lower_bound"])) > 2e-7:
            raise ValueError("Independent LP disagrees with the minimum-slew schedule")
        lp_checks.append(dict(label_index=j, envelope_rate=float(result["field_slew"][j]), **check))

    power = exchange_power_bounds(result, lr, lt, dt)
    exchange = required_exchange(energy, pressure[0], pressure[1], lr, lt)
    target_exchange = required_exchange(saved["target"][0][None], saved["target"][1][None],
                                       2*saved["target"][2][None], lr, lt)[0]
    exchange_error = float(np.max(np.abs(exchange.sum(axis=0)-target_exchange)))
    peak_bound_error = 0.
    minimum_interior_reserve = np.inf
    eps = np.where(MATERIAL_DIMENSIONS == 2, .1, 0.)[:, None, None]
    for u in (.125, .375, .625, .875):
        actual = instantaneous_exchange_power(result, lr, lt, dt, u)
        peak_bound_error = max(peak_bound_error, float(np.max(actual-power["upper"])),
                               float(np.max(power["lower"]-actual)))
        midT = (1-u)*tension[:, :-1]+u*tension[:, 1:]
        elastic = elastic_state_from_tension(midT, result["inventory"][:, None], shear_fraction=eps)["energy"]
        linear_material = (1-u)*energy[:6, :-1]+u*energy[:6, 1:]
        mid_reserve = (1-u)*reserve[:-1]+u*reserve[1:]+(linear_material-elastic).sum(axis=0)
        minimum_interior_reserve = min(minimum_interior_reserve, float(mid_reserve.min()))
    if peak_bound_error > 1e-9 or power["endpoint_balance_error"] > 1e-9 or exchange_error > 2e-12:
        raise ValueError("Instantaneous work or reciprocal power checks failed")
    rng = np.random.default_rng(947)
    panels = {tuple(np.unravel_index(i, dt.shape)) for i in rng.choice(dt.size, 23, replace=False)}
    panels.add(tuple(np.unravel_index(np.max(power["upper"], axis=0).argmax(), dt.shape)))
    maximum_integral_error = 0.
    for i, j in sorted(panels):
        tiny = {k: result[k][..., i:i+2, j:j+1] for k in
                ("target", "component_energy", "component_pressure", "material_tension")}
        tiny["inventory"] = result["inventory"][:, j:j+1]
        sl, sp = (slice(i, i+2), slice(j, j+1)), (slice(i, i+1), slice(j, j+1))
        integral, _ = quad_vec(lambda u: instantaneous_exchange_power(tiny, lr[sl], lt[sl], dt[sp], u)[:, 0, 0]*dt[i, j],
                               0., 1., epsabs=1e-12, epsrel=1e-11)
        expected = np.r_[exchange[:, i, j], -target_exchange[i, j]]
        maximum_integral_error = max(maximum_integral_error, float(np.max(np.abs(integral-expected))))
    if maximum_integral_error > 1e-10:
        raise ValueError("Independent instantaneous-power integration failed")

    geom = geometry(state["D"], lr, lt, state["ell"][0], state["edges"][-1]-state["edges"][0])
    gap = (geom["eta"]-1)*geom["inner_radius"]
    gap_panel = np.maximum(gap[:-1], gap[1:])
    rates = configuration_rate_bound(tension, result["inventory"], lr, lt, dt)
    speeds = .5*rates*gap_panel
    # A fixed worst-case latency covers every shorter local path. Delay is
    # length/c in the inherited c=1 units, including the complementary rail port.
    transport = transport_capacity(power["upper"], gap.max(axis=0))
    base_capacity = transport["total_capacity"]
    leg_transport = transport_capacity(power["upper"], geom["leg"].max(axis=0))
    minimum_reserve = reserve.min(axis=0)
    transport_fraction = 2*base_capacity/minimum_reserve
    max_delay = minimum_reserve/(2*transport["node_positive_power_peak"].sum(axis=0))

    # For the fixed scheduled materials, a neutral package containing new
    # ideal ties has energy >=2*sum(d*T)*zeta, even with its transit reused.
    joint_weight = np.einsum("i,itj->tj", MATERIAL_DIMENSIONS, tension)
    joint_necessary_ceiling = np.min(reserve/(2*joint_weight), axis=0)
    # The joints add four explicit work ports, and their changing energy
    # changes the old dust port. Cache the resulting piecewise-linear peak
    # power expression so the joint-size search also counts its own traffic.
    unit = joint_work_capacity(result, power, lr, lt, dt, gap.max(axis=0), 1.)
    joint_peak = np.maximum(unit["expanded_power_upper"][11:15].max(axis=1), 0.).sum(axis=0)
    dust_correction = unit["dust_power_correction"]
    other_peaks = transport["node_positive_power_peak"].sum(axis=0)-transport["node_positive_power_peak"][10]
    def capacity_at(fraction):
        dust_peak = np.maximum((power["upper"][10]+fraction*dust_correction).max(axis=0), 0.)
        return gap.max(axis=0)*(other_peaks+dust_peak+fraction*joint_peak)
    del unit
    low, high = np.zeros_like(base_capacity), joint_necessary_ceiling.copy()
    if np.any(2*base_capacity > minimum_reserve):
        raise ValueError("The gap-latency transport allowance already exceeds the reserve")
    for _ in range(56):
        middle = .5*(low+high)
        overhead = 2*middle*joint_weight+2*capacity_at(middle)
        fits = np.all(overhead <= reserve, axis=0)
        low, high = np.where(fits, middle, low), np.where(fits, high, middle)
    chosen_fraction = 1e-4
    expanded = joint_work_capacity(result, power, lr, lt, dt, gap.max(axis=0), chosen_fraction)
    C = expanded["total_capacity"]
    np.testing.assert_allclose(C, capacity_at(chosen_fraction), atol=2e-15, rtol=2e-13)
    joint_power_balance_error = max(float(np.max(np.abs(p.sum(axis=0)+expanded["dust_power_correction"])))
                                    for p in expanded["joint_endpoint_power"])
    if joint_power_balance_error > 1e-10:
        raise ValueError("Added joints lost reciprocal operating power")
    final_reserve = reserve-expanded["total_energy_allowance"]
    if final_reserve.min() <= 0:
        raise ValueError("Selected joint/transport allowance exceeds the sampled reserve")
    sensitivities = []
    for fraction in (1e-4, 1e-3, 1e-2):
        upper = 2*fraction*joint_weight+2*capacity_at(fraction)
        floor = 2*fraction*joint_weight
        sensitivities.append(dict(attachment_fraction=fraction,
            envelope_exceedances=int(np.count_nonzero(upper > reserve+1e-12)),
            ideal_neutral_joint_floor_exceedances=int(np.count_nonzero(floor > reserve+1e-12)),
            minimum_reserve_after_envelope=float(np.min(reserve-upper))))
    # The package ceiling is convex in linear tensile duties. Subtracting
    # it from the concave elastic reserve preserves the endpoint lower bound.
    interior_package_minimum = np.inf
    for u in (.25, .5, .75):
        midT = (1-u)*tension[:, :-1]+u*tension[:, 1:]
        emid = elastic_state_from_tension(midT, result["inventory"][:, None], shear_fraction=eps)["energy"]
        mid_reserve = (1-u)*reserve[:-1]+u*reserve[1:]+((1-u)*energy[:6, :-1]+u*energy[:6, 1:]-emid).sum(axis=0)
        mid_cost = 2*chosen_fraction*np.einsum("i,itj->tj", MATERIAL_DIMENSIONS, midT)+2*C
        interior_package_minimum = min(interior_package_minimum, float((mid_reserve-mid_cost).min()))
    if interior_package_minimum <= 0:
        raise ValueError("Interior joint/transport allowance lost positive reserve")

    np.savez_compressed(output / (name+"_states.npz"), t=saved["t"], x=saved["x"],
        component_names=np.array(COMPONENT_NAMES), material_names=np.array(MATERIAL_NAMES),
        field_energy=result["field_energy"], field_lower=result["field_lower"], field_upper=result["field_upper"],
        field_slew=result["field_slew"], material_tension=tension, material_inventory=result["inventory"],
        component_energy=energy, component_exchange=exchange, material_rate_bound=rates,
        gap_patch_control_speed_bound=speeds, remaining_reserve=reserve,
        transport_node_names=np.array(COMPONENT_NAMES+("axial_joint_ties", "transverse_joint_ties",
            "axial_joint_photons", "transverse_joint_photons", "retained_rail_port")),
        node_positive_power_peak=expanded["node_positive_power_peak"], node_reception_capacity=expanded["node_capacity"],
        local_transit_delay=gap.max(axis=0), total_reception_capacity=C,
        joint_fraction_guaranteed=low, joint_fraction_necessary_ceiling=joint_necessary_ceiling,
        selected_joint_fraction=chosen_fraction, joint_transport_energy_ceiling=expanded["total_energy_allowance"],
        remaining_reserve_after_allowance=final_reserve)
    linear_stretch = result["law"]["strain"]**(1/MATERIAL_DIMENSIONS[:, None, None])
    old = parent["elastic_material_replay"]
    row = dict(label=name, samples=list(lr.shape),
        input_sha256={str(p.relative_to(ROOT)): sha256(p) for p in (archive, summary_path, meta_path, source)},
        scheduled_materials=dict(minimum_reserve=float(reserve.min()),
            minimum_interior_reserve=minimum_interior_reserve,
            minimum_guaranteed_reserve=float(result["guaranteed_reserve"].min()),
            maximum_linear_stretch=float(linear_stretch.max()),
            previous_maximum_linear_stretch=old["maximum_linear_stretch"],
            maximum_gap_patch_control_speed=float(speeds.max()),
            previous_maximum_gap_patch_control_speed=old["maximum_gap_patch_control_speed"],
            control_speed_peak_reduction_factor=old["maximum_gap_patch_control_speed"]/float(speeds.max()),
            maximum_field_slew=float(result["field_slew"].max()),
            conserved_reference_inventory=extrema(result["inventory"].sum(axis=0)),
            independent_field_programs=lp_checks),
        work_transfer=dict(maximum_instantaneous_component_power=float(np.max(np.maximum(abs(power["lower"]), abs(power["upper"])))),
            reception_inventory=extrema(C), maximum_delay=extrema(gap.max(axis=0)),
            maximum_fraction_of_minimum_reserve_for_original_traffic=float(transport_fraction.max()),
            maximum_fraction_of_minimum_reserve_with_joint_traffic=float(np.max(2*C/minimum_reserve)),
            joint_traffic_capacity_multiplier=extrema(C/base_capacity),
            maximum_supported_delay_over_gap=extrema(max_delay/gap.max(axis=0)),
            leg_delay_transport_fraction=extrema(2*leg_transport["total_capacity"]/minimum_reserve),
            fixed_inventory_includes_transit_energy=True,
            ideal_reaction_energy_counted=True, additional_joint_operating_power_counted=True,
            optical_guide_reaction_operating_power_closed=False),
        ideal_joints=dict(guaranteed_uniform_attachment_fraction=float(low.min()),
            per_label_guaranteed_fraction=extrema(low),
            uniform_necessary_ceiling=float(joint_necessary_ceiling.min()),
            chosen_attachment_fraction=chosen_fraction,
            minimum_reserve_after_allowance=float(final_reserve.min()),
            minimum_interior_reserve_after_allowance=interior_package_minimum,
            sensitivities=sensitivities,
            shared_stress_allowance_comparison_minimum_reserve=float(np.min(reserve-
                joint_transport_envelope(tension, C, chosen_fraction)["energy_ceiling"])),
            transport_power_multiplier_sensitivity=[dict(multiplier=m,
                minimum_reserve=float(np.min(reserve-expanded["joint_energy"]-2*m*C))) for m in (1., 2., 4., 8., 16.)],
            scope="Additional ideal strings and photon reactions with counted joint work; fixed scheduled material duties; unit strength; joint constitutive inventories and embedding pending"),
        verification=dict(maximum_tensor_error=tensor_error, maximum_exchange_error=exchange_error,
            maximum_power_balance_error=power["endpoint_balance_error"], maximum_power_bound_error=peak_bound_error,
            maximum_joint_power_balance_error=joint_power_balance_error,
            independently_integrated_panels=len(panels), maximum_power_integral_error=maximum_integral_error),
        inherited_current_host_rejections=parent["inherited_open_gates"]["independent_new_current_hosts_certified_rejections"])
    print(name, "reserve after allowance", row["ideal_joints"]["minimum_reserve_after_allowance"],
          "gap control speed", row["scheduled_materials"]["maximum_gap_patch_control_speed"], flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_reports/data/distributed_reconfiguration")
    args = parser.parse_args()
    if args.workers < 1 or args.output.exists():
        parser.error("positive workers and a fresh output directory required")
    args.output.mkdir(parents=True)
    parent = json.loads((PARENT / "summary.json").read_text())
    names = [h["label"] for h in parent["histories"]]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        histories = list(pool.map(audit, [(name, str(args.output)) for name in names]))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        scope="Scheduled constitutive replay and conditional causal transport/ideal joint tensor allowance",
        parameters=dict(reference_inventory_fraction=.25, auxiliary_bias_fraction=.5,
            guaranteed_reserve_fraction=.1, field_fraction_floor=.001, outer_sheet_fraction=1.,
            selected_joint_attachment_fraction=1e-4, sheet_shear_fraction=.1),
        exact_sources_archived=True, current_hosts_solved=False, finite_joint_embedding_solved=False,
        joint_constitutive_inventories_solved=False, actuator_kinetic_tensor_counted=False,
        joint_operating_power_counted=True, optical_guide_reaction_dynamics_closed=False,
        photon_conversion_and_optics_supplied=False, physical_material_identified=False,
        full_containment_established=False, histories=histories)
    (args.output / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(), *[ROOT / "toolkit/adm_harness_cli/adm_harness" / (name+".py") for name in
        ("distributed_reconfiguration", "material_reconfiguration", "finite_containment", "containment_ensemble", "magnetic_load_balance")],
        ROOT / "toolkit/adm_harness_cli/tests/test_distributed_reconfiguration.py"]
    for path in paths:
        shutil.copyfile(path, args.output / ("execution_"+path.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        parent_manifest_sha256=sha256(PARENT / "manifest.json"),
        output_sha256={p.name: sha256(p) for p in args.output.iterdir() if p.is_file()})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
