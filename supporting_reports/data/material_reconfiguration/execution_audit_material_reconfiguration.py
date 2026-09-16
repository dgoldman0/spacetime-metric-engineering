#!/usr/bin/env python3
"""Replay elastic reconfiguration on four independent saved histories.

Numerical evidence and provenance are emitted here. The supporting report
is written manually. Added current hosts, actuator hardware and end forces
remain the separate construction gates identified by the parent audit.
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
from scipy.integrate import quad

from adm_harness.containment_ensemble import required_exchange
from adm_harness.finite_containment import geometry
from adm_harness.material_reconfiguration import (
    COMPONENT_NAMES, MATERIAL_DIMENSIONS, MATERIAL_NAMES, configuration_coordinates,
    configuration_rate_bound, elastic_replay, elastic_state_from_strain,
    elastic_state_from_tension, isometric_pool_bounds, isometric_pool_program,
    reciprocal_routes,
)


ROOT = Path(__file__).resolve().parents[3]
PARENT = ROOT / "supporting_reports/data/finite_containment"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extrema(value):
    return dict(minimum=float(np.min(value)), maximum=float(np.max(value)))


def audit(task):
    name, output_directory = task
    output = Path(output_directory)
    manifest = json.loads((PARENT / "manifest.json").read_text())
    parent_summary = json.loads((PARENT / "summary.json").read_text())
    parent = next(h for h in parent_summary["histories"] if h["label"] == name)
    path = PARENT / (name+"_states.npz")
    if sha256(path) != manifest["output_sha256"][path.name]:
        raise ValueError("Parent evidence hash mismatch")
    with np.load(path) as data:
        saved = {k: data[k] for k in ("t", "x", "target", "field_floor", "inner_hoop", "outer_hoop", "lr", "lt")}
    meta_path = ROOT / "supporting_reports/data/magnetic_geometry" / (name+"_summary.json")
    if sha256(meta_path) != parent["input_sha256"][str(meta_path.relative_to(ROOT))]:
        raise ValueError("Geometry metadata hash mismatch")
    meta = json.loads(meta_path.read_text())
    source_path = ROOT / meta["input"]
    if sha256(source_path) != parent["input_sha256"][meta["input"]]:
        raise ValueError("Source history hash mismatch")
    with np.load(source_path) as data:
        state = {k: data[k] for k in ("t", "x", "D", "ell", "radius", "edges", "lapse")}
    for key in ("t", "x"):
        np.testing.assert_array_equal(state[key], saved[key])
    target, floor, hi, ho, lr, lt = (saved[k] for k in ("target", "field_floor", "inner_hoop", "outer_hoop", "lr", "lt"))
    bounds = isometric_pool_bounds(target, floor)
    lower, upper = bounds["lower"].max(axis=0), bounds["upper"].min(axis=0)
    extrema_indices = np.stack([bounds["lower"].argmax(axis=0), bounds["upper"].argmin(axis=0)])
    lp_status = []
    for j, indices in enumerate(extrema_indices.T):
        lp = isometric_pool_program(target[:, indices, j], floor[indices, j])
        lp_status.append(int(lp.status))
        if lower[j] > upper[j]+1e-10 and lp.status != 2:
            raise ValueError("Independent fixed-inventory LP disagrees with rejection")
    result = elastic_replay(target, floor, hi, ho)
    energy, pressure = result["component_energy"], result["component_pressure"]
    law, tension, inventory = result["law"], result["material_tension"], result["inventory"]
    tensor_error = float(np.max(np.abs(result["reconstructed_tensor"]-target)))
    if tensor_error > 1e-12 or result["remaining_reserve"].min() <= 0:
        raise ValueError("Material replay lost the tensor budget")
    eps = np.where(MATERIAL_DIMENSIONS == 2, .1, 0.)[:, None, None]
    equal_inventory = .25*result["ideal"]["support"]["spare"].min(axis=0)/6
    equal_state = elastic_state_from_tension(tension, equal_inventory, shear_fraction=eps)
    equal_control = dict(maximum_linear_stretch=float(np.max(
        equal_state["strain"]**(1/MATERIAL_DIMENSIONS[:, None, None]))),
        minimum_remaining_reserve=float(np.min(result["ideal"]["support"]["spare"]
            -(equal_state["energy"]-tension).sum(axis=0))))
    del equal_state
    forward = elastic_state_from_strain(law["strain"], inventory[:, None], shear_fraction=eps)
    strain_error = float(max(np.max(np.abs(forward["energy"]-energy[:6])),
                             np.max(np.abs(forward["tension"]-tension))))
    if strain_error > 1e-12:
        raise ValueError("Forward constitutive law failed to recover the inverse history")
    reserve_floor = .75*result["ideal"]["support"]["spare"].min(axis=0)
    if np.min(result["remaining_reserve"]-reserve_floor) < -1e-12:
        raise ValueError("Conserved inventory exceeded the reserved allowance")
    q = configuration_coordinates(law["log_strain"], lr, lt)
    macro = np.stack([lr*lt, lt, lr*lt, lt, lt*lt, lt*lt])
    coordinate_error = float(np.max(np.abs(q.sum(axis=1)+np.log(macro)-law["log_strain"])))
    exchange = required_exchange(energy, pressure[0], pressure[1], lr, lt)
    target_exchange = required_exchange(target[0][None], target[1][None], 2*target[2][None], lr, lt)[0]
    exchange_error = float(np.max(np.abs(exchange.sum(axis=0)-target_exchange)))
    routes = reciprocal_routes(exchange)
    route_error = float(np.max(np.abs(routes["rail_exchange"]+target_exchange)))
    if max(exchange_error, route_error, routes["maximum_unmatched_exchange"]) > 2e-12:
        raise ValueError("Energy exchange failed reciprocal closure")

    # A continuous interpolation: tensile duties and field energies are
    # linear per panel; macro stretches are log-linear. Convex E(T) leaves
    # at least the interpolated endpoint inventory reserve throughout.
    minimum_interior_reserve = np.inf
    maximum_convexity_error = -np.inf
    for u in (.25, .5, .75):
        tmid = (1-u)*tension[:, :-1]+u*tension[:, 1:]
        emid = elastic_state_from_tension(tmid, inventory[:, None], shear_fraction=eps)["energy"]
        linear_energy = (1-u)*energy[:6, :-1]+u*energy[:6, 1:]
        correction = (linear_energy-emid).sum(axis=0)
        reserve = ((1-u)*result["remaining_reserve"][:-1]
                   +u*result["remaining_reserve"][1:]+correction)
        minimum_interior_reserve = min(minimum_interior_reserve, float(reserve.min()))
        maximum_convexity_error = max(maximum_convexity_error, float(np.max(emid-linear_energy)))
    if maximum_convexity_error > 1e-12 or minimum_interior_reserve <= 0:
        raise ValueError("Interior constitutive interpolation lost positivity")
    # Check the shape-work integral independently on seeded panels and the
    # strongest material-energy change. Work is integral T d(log J).
    rng = np.random.default_rng(902)
    checks = set()
    for flat in rng.choice(tension[:, :-1].size, size=36, replace=False):
        checks.add(tuple(np.unravel_index(flat, tension[:, :-1].shape)))
    checks.add(tuple(np.unravel_index(np.argmax(np.abs(np.diff(energy[:6], axis=1))), tension[:, :-1].shape)))
    maximum_work_error = 0.
    for i, t, j in checks:
        T0, T1 = tension[i, t:t+2, j]
        alpha = inventory[i, j]*(.9 if MATERIAL_DIMENSIONS[i] == 2 else 1.)
        work = quad(lambda u: (T0+u*(T1-T0))*(T1-T0)/np.hypot(T0+u*(T1-T0), alpha),
                    0., 1., epsabs=1e-13, epsrel=1e-11, limit=200)[0]
        maximum_work_error = max(maximum_work_error, abs(work-(energy[i, t+1, j]-energy[i, t, j])))
    if maximum_work_error > 1e-10:
        raise ValueError("Constitutive work quadrature disagrees")

    dtau = .5*(state["lapse"][1:]+state["lapse"][:-1])*np.diff(state["t"])[:, None]
    rates = configuration_rate_bound(tension, inventory, lr, lt, dtau)
    geom = geometry(state["D"], lr, lt, state["ell"][0], state["edges"][-1]-state["edges"][0])
    gap = (geom["eta"]-1)*geom["inner_radius"]
    gap_panel = np.maximum(gap[:-1], gap[1:])
    leg_panel = np.maximum(geom["leg"][:-1], geom["leg"][1:])
    gap_speed = .5*rates*gap_panel
    leg_speed = .5*rates*leg_panel
    span_at_point_one_c = .2/rates.max(axis=1)
    reference_size_cap = np.min(gap[None]/np.exp(law["log_strain"]/MATERIAL_DIMENSIONS[:, None, None]), axis=1)

    np.savez_compressed(output / (name+"_states.npz"),
        **saved, component_names=np.array(COMPONENT_NAMES), material_names=np.array(MATERIAL_NAMES),
        material_dimensions=MATERIAL_DIMENSIONS, isometric_lower=bounds["lower"],
        isometric_upper=bounds["upper"], isometric_witness_indices=extrema_indices,
        material_relaxed_inventory=inventory, material_tension=tension,
        material_strain=law["strain"], material_configuration=q,
        material_control_rate_bound=rates, gap_patch_control_speed_bound=gap_speed,
        reference_patch_size_cap=reference_size_cap,
        out_of_plane_speed_squared=law["out_of_plane_speed_squared"],
        longitudinal_speed_squared=law["longitudinal_speed_squared"],
        in_plane_shear_speed_squared=law["in_plane_shear_speed_squared"],
        component_energy=energy, component_pressure=pressure, component_exchange=exchange,
        remaining_reserve=result["remaining_reserve"], material_surcharge=result["material_surcharge"],
        added_field_energy=result["ideal"]["field_energy"],
        rail_port_exchange=routes["rail_exchange"], transfer_totals=routes["transfer_totals"],
        proper_panel_duration=dtau)
    worst_label = int(np.argmax(lower-upper))
    component_summary = {}
    for i, component in enumerate(MATERIAL_NAMES):
        component_summary[component] = dict(relaxed_inventory=extrema(inventory[i]),
            energy=extrema(energy[i]), tensile_duty=extrema(tension[i]),
            strain=extrema(law["strain"][i]),
            linear_stretch=extrema(law["strain"][i]**(1/MATERIAL_DIMENSIONS[i])),
            largest_strain_ratio=float(np.max(law["strain"][i].max(axis=0)/law["strain"][i].min(axis=0))),
            net_shape_work=extrema(exchange[i].sum(axis=0)),
            gross_positive_shape_work=extrema(np.maximum(exchange[i], 0.).sum(axis=0)),
            maximum_panel_mean_shape_power=float(np.max(np.abs(exchange[i])/dtau)),
            maximum_gap_patch_speed=float(gap_speed[i].max()),
            maximum_leg_patch_speed=float(leg_speed[i].max()),
            span_limit_for_point_one_c=extrema(span_at_point_one_c[i]))
    row = dict(label=name, samples=list(lr.shape),
        input_sha256={str(p.relative_to(ROOT)): sha256(p) for p in (path, meta_path, source_path)},
        fixed_area_and_length_pool=dict(rejected_labels=int(np.count_nonzero(lower > upper+1e-10)),
            independent_two_time_lp_status=lp_status, inventory_gap=extrema(lower-upper),
            relaxed_all_sheet_area_ratio_lower_bound=extrema(lower/upper),
            worst_pair=dict(position=float(state["x"][worst_label]),
                required_energy=float(lower[worst_label]), required_time=float(state["t"][extrema_indices[0, worst_label]]),
                allowed_energy=float(upper[worst_label]), allowed_time=float(state["t"][extrema_indices[1, worst_label]]))),
        elastic_material_replay=dict(violating_samples=int(np.count_nonzero(result["remaining_reserve"] < -1e-12)),
            initial_inventory_policy="minimize the maximum linear stretch across all constituents",
            equal_inventory_control=equal_control,
            maximum_linear_stretch=float(np.max(law["strain"]**(1/MATERIAL_DIMENSIONS[:, None, None]))),
            minimum_ideal_reserve=float(result["ideal"]["support"]["spare"].min()),
            minimum_remaining_reserve=float(result["remaining_reserve"].min()),
            conserved_relaxed_energy=extrema(inventory.sum(axis=0)),
            maximum_material_surcharge=float(result["material_surcharge"].max()),
            minimum_interior_reserve=minimum_interior_reserve,
            maximum_tensor_error=tensor_error, maximum_forward_constitutive_error=strain_error,
            maximum_configuration_reconstruction_error=coordinate_error,
            maximum_constitutive_work_integral_error=maximum_work_error,
            independent_work_integrals=len(checks),
            maximum_component_exchange_sum_error=exchange_error,
            maximum_retained_port_error=route_error,
            maximum_unmatched_routed_exchange=routes["maximum_unmatched_exchange"],
            maximum_interpolation_convexity_error=maximum_convexity_error,
            maximum_gap_patch_control_speed=float(gap_speed.max()),
            maximum_leg_patch_control_speed=float(leg_speed.max()),
            maximum_retained_port_mean_power=float(np.max(np.abs(routes["rail_exchange"])/dtau)),
            additional_net_exchange_beyond_retained_target=0., components=component_summary),
        inherited_open_gates=dict(current_coefficient=parent["current_coefficient"],
            independent_new_current_hosts_certified_rejections=parent["continuous_current_bound"]["certified_rejected_samples"],
            current_hosts_reoptimized_in_this_replay=False,
            finite_junctions_and_end_torques_closed=False,
            coupled_reconfiguration_embedding_solved=False,
            kinetic_actuator_stress_counted=False,
            new_hardware_energy_counted=False,
            physical_containment_established=False))
    print(name, "fixed pool rejected labels", row["fixed_area_and_length_pool"]["rejected_labels"],
          "elastic reserve", row["elastic_material_replay"]["minimum_remaining_reserve"],
          "gap-size patch speed", row["elastic_material_replay"]["maximum_gap_patch_control_speed"], flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_reports/data/material_reconfiguration")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    if args.output.exists():
        parser.error("choose a fresh output directory")
    args.output.mkdir(parents=True)
    parent = json.loads((PARENT / "summary.json").read_text())
    names = [h["label"] for h in parent["histories"]]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        results = list(pool.map(audit, [(name, str(args.output)) for name in names]))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        executed_sources="Exact source snapshots and SHA-256 hashes in manifest.json",
        scope="Inverse driven strain replay with fixed relaxed inventories; constitutive and sampled tensor budget gate",
        membrane_law_source="https://arxiv.org/html/2409.10602v2", sheet_shear_fraction=.1,
        initial_relaxed_inventory_fraction_of_minimum_reserve=.25,
        initial_inventory_policy="balanced maximum linear stretch; each role has a 1e-6 fraction inventory floor",
        continuous_interpolation=dict(tensile_duties="linear per panel", macro_stretches="log-linear per panel",
            material_energy="fixed constitutive law evaluated along tensile trajectory",
            remaining_inventory="target energy minus every counted component"),
        original_fields_and_current_costs_retained=True,
        added_field_hosts_and_actuator_hardware_supplied=False,
        material_identified_in_nature=False, full_physical_containment_established=False,
        histories=results)
    (args.output / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(),
        ROOT / "toolkit/adm_harness_cli/adm_harness/material_reconfiguration.py",
        ROOT / "toolkit/adm_harness_cli/adm_harness/finite_containment.py",
        ROOT / "toolkit/adm_harness_cli/adm_harness/containment_ensemble.py",
        ROOT / "toolkit/adm_harness_cli/adm_harness/magnetic_load_balance.py",
        ROOT / "toolkit/adm_harness_cli/tests/test_material_reconfiguration.py"]
    for path in paths:
        shutil.copyfile(path, args.output / ("execution_"+path.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        parent_manifest_sha256=sha256(PARENT / "manifest.json"),
        output_sha256={p.name: sha256(p) for p in args.output.iterdir() if p.is_file()})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
