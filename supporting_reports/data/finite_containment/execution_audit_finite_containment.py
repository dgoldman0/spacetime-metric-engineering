#!/usr/bin/env python3
"""Construct coaxial interfaces and audit current hosts/material evolution.

Four independent histories run in separate worker processes. Numerical
archives and provenance are generated here; the report is authored manually.
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

import numpy as np
import scipy

from adm_harness.containment_ensemble import required_exchange
from adm_harness.finite_containment import (
    EVOLUTION_BASIS, EVOLUTION_NAMES, allocate_field, annular_factor,
    controlled_material_history, field_interfaces, geometry, necessary_host_bound,
    particle_inventory, pointwise_particle_search, reservoir_interval,
)
from adm_harness.magnetic_load_balance import attached_bank, support_cone
from adm_harness.magnetic_geometry import jacket_requirements


ROOT = Path(__file__).resolve().parents[3]
PARENT = ROOT / "supporting_reports/data/magnetic_geometry"
ENSEMBLE = ROOT / "supporting_reports/data/containment_ensemble"
PREFIX = "shared_candidate_"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extrema(value):
    return dict(minimum=float(np.min(value)), maximum=float(np.max(value)))


def worst(value, state):
    idx = np.unravel_index(np.argmax(value), value.shape)
    return dict(value=float(value[idx]), time_index=int(idx[0]), label_index=int(idx[1]),
                time=float(state["t"][idx[0]]), position=float(state["x"][idx[1]]))


def score(value, state):
    return dict(maximum_shortfall=float(np.max(value)),
                violating_samples=int(np.count_nonzero(value > 1e-10)),
                worst=worst(value, state))


def audit(task):
    name, output_directory = task
    output = Path(output_directory)
    meta_path = PARENT / (name+"_summary.json")
    meta = json.loads(meta_path.read_text())
    source_path, archive_path = ROOT / meta["input"], PARENT / (name+"_states.npz")
    ensemble_path = ENSEMBLE / (name+"_states.npz")
    manifest = json.loads((PARENT / "manifest.json").read_text())
    em = json.loads((ENSEMBLE / "manifest.json").read_text())
    expected = {meta_path: manifest["output_sha256"][meta_path.name],
        source_path: manifest["input_sha256"][meta["input"]],
        archive_path: manifest["output_sha256"][archive_path.name],
        ensemble_path: em["output_sha256"][ensemble_path.name]}
    hashes = {str(p.relative_to(ROOT)): sha256(p) for p in expected}
    for path, value in expected.items():
        if hashes[str(path.relative_to(ROOT))] != value:
            raise ValueError(f"Input hash mismatch: {path}")
    with np.load(source_path) as a:
        state = {k: a[k] for k in a.files}
    with np.load(archive_path) as a:
        saved = {k: a[k] for k in a.files}
    with np.load(ensemble_path) as a:
        prior = {k: a[k] for k in ("component_energy", "t", "x")}
    for axis in ("t", "x"):
        np.testing.assert_array_equal(state[axis], prior[axis])
        np.testing.assert_array_equal(state[axis], saved[axis])
    D = state["D"]
    lr, lt = state["ell"]/state["ell"][0], state["radius"]/state["radius"][0]
    field = {k: saved[PREFIX+"loop_"+k+"_field_energy"] for k in ("radial", "transverse")}
    loaded = attached_bank(state, saved["evolved_cold_energy"], field,
                           carrier_tensor=saved[PREFIX+"carrier_tensor"])
    target, floor, facets = (D*loaded[k] for k in ("residual_target", "radial_field_floor", "facets"))
    hi, ho = (D*saved[PREFIX+side+"_hoop"] for side in ("inner", "outer"))
    chi, eta = meta["current_coefficient"], 1.01
    geom = geometry(D, lr, lt, state["ell"][0], state["edges"][-1]-state["edges"][0], eta=eta)
    R = annular_factor(eta)
    background = np.sqrt(2*1.1*saved["evolved_cold_energy"]/(3*.1*D)
                         *lr**2/np.minimum(lr**2, lt**2))
    old_B = prior["component_energy"][3]
    old_field = field_interfaces(old_B, geom, background)
    # The old maximizing witness is only a demand diagnostic. Its finite
    # interfaces are reoptimized independently below.
    old_cost_floor = 2*chi*(old_field["axial_current_integral"]+old_field["return_current_integral"])
    bound = necessary_host_bound(facets, hi, ho, geom["axial_current_per_root_energy"], chi, eta=eta)
    baseline = allocate_field(target, floor, hi, ho, np.zeros_like(D), eta=eta)
    point = pointwise_particle_search(target, floor, hi, ho, geom, chi)
    point_field = field_interfaces(point["field_energy"], geom, background)
    point_pass = point["shortfall"] <= 1e-10
    if np.any(bound["rejected"] & point_pass):
        raise ValueError("Current-host witness contradicts the continuous rejection bound")
    # Replaying the searched field with fixed populations retains rest energy
    # at zero current. Several speeds are witnesses, not an exhaustive search.
    replays, replay_archive = {}, {}
    for speed in (1/np.sqrt(2), .98, .999):
        axial = particle_inventory(point_field["axial_current_integral"], chi, peak_speed=speed)
        ret = particle_inventory(point_field["return_current_integral"], chi, peak_speed=speed)
        allocation = allocate_field(target, floor, hi, ho, point["field_energy"], eta=eta,
            carrier_energy=axial["energy"]+ret["energy"],
            carrier_axial_pressure=axial["pressure"], return_pressure=ret["pressure"])
        key = f"peak_speed_{speed:.6f}"
        replays[key] = dict(**score(allocation["shortfall"], state),
            peak_speed=speed, rest_energy=extrema(chi*(axial["charge_inventory"]+ret["charge_inventory"])),
            maximum_charge_balance_error=float(max(
                np.max(np.abs(axial["charge_inventory"]*axial["speed"]-point_field["axial_current_integral"])),
                np.max(np.abs(ret["charge_inventory"]*ret["speed"]-point_field["return_current_integral"])))) )
        replay_archive[key+"_shortfall"] = allocation["shortfall"]
        replay_archive[key+"_axial_charge"] = axial["charge_inventory"]
        replay_archive[key+"_return_charge"] = ret["charge_inventory"]

    # A passive transverse population fixes B proportional to lt**2.
    # Even with free currents, each label needs M0 >= max(a/lt**2),
    # whereas a tensile outer boundary requires M0 <= min(ho/(2*lt**2)).
    passive_lower = np.maximum(np.max(bound["a"]/lt**2, axis=0), 0.)
    passive_upper = np.min(ho/(2*lt**2), axis=0)

    histories = [controlled_material_history(facets[:, :, j], hi[:, j], ho[:, j],
                                            lr[:, j], lt[:, j], eta=eta)
                 for j in range(D.shape[1])]
    # Also grant all original current hosts and their centrifugal reactions
    # for free. This sensitivity prevents attributing an inventory obstruction
    # solely to retaining separate original and added carrier populations.
    free_loaded = attached_bank(state, saved["evolved_cold_energy"], field)
    magnetic = jacket_requirements(saved["evolved_cold_energy"], D, aspect=.01,
        inner_pressure=.1, outer_pressure=1.1, radius_ratio=eta)
    free_F = D*free_loaded["facets"]
    free_hi, free_ho = (D*magnetic[side+"_hoop"] for side in ("inner", "outer"))
    free_histories = [controlled_material_history(free_F[:, :, j], free_hi[:, j],
        free_ho[:, j], lr[:, j], lt[:, j], eta=eta) for j in range(D.shape[1])]
    free_deficits = np.array([r["shortfall"] for r in free_histories])
    free_duals = np.array([r["dual_lower_bound"] for r in free_histories])
    np.testing.assert_allclose(free_deficits, free_duals, atol=2e-8)
    energies = np.stack([r["energy"] for r in histories], axis=-1)
    tensor_trace = np.einsum("ij,j...->i...", EVOLUTION_BASIS, energies)
    tensor = tensor_trace.copy()
    tensor[2] /= 2
    cone = support_cone(*(target-tensor), floor)
    deficits = np.array([r["shortfall"] for r in histories])
    duals = np.array([r["dual_lower_bound"] for r in histories])
    np.testing.assert_allclose(np.max(cone["shortfall"], axis=0), deficits, atol=2e-8)
    np.testing.assert_allclose(tensor_trace[2], -hi-ho, atol=2e-8)
    np.testing.assert_allclose(deficits, duals, atol=2e-8)
    if energies.min() < -2e-8:
        raise ValueError("Negative population in history witness")
    exchange = required_exchange(energies, energies*EVOLUTION_BASIS[1, :, None, None],
                                 energies*EVOLUTION_BASIS[2, :, None, None], lr, lt)
    total_exchange = required_exchange(tensor_trace[0][None], tensor_trace[1][None],
                                       tensor_trace[2][None], lr, lt)[0]
    exchange_error = float(np.max(np.abs(exchange.sum(axis=0)-total_exchange)))
    bus = reservoir_interval(exchange.sum(axis=0), cone["spare"])
    reciprocal_error = float(np.max(np.abs(np.diff(bus["store_energy"], axis=0)+exchange.sum(axis=0))))
    initial = np.stack([r["initial_populations"] for r in histories], axis=-1)
    scales = np.stack([lr*lt, lt, lr*lt, lt, lt**2])
    population_error = float(np.max(np.abs(energies[:5]/scales-initial[:, None])))

    # Proper-time variation of the searched current compared with one leg's
    # light crossing time. This is a rate diagnostic for the static replay.
    dtau = .5*(state["lapse"][1:]+state["lapse"][:-1])*np.diff(state["t"])[:, None]
    peak_I = np.max(point_field["current_per_cartridge"], axis=0)
    rate = np.divide(np.abs(np.diff(point_field["current_per_cartridge"], axis=0)),
                     dtau*peak_I, out=np.zeros_like(dtau), where=peak_I > 0)
    rate *= .5*(geom["leg"][1:]+geom["leg"][:-1])
    np.savez_compressed(output / (name+"_states.npz"),
        t=state["t"], x=state["x"], target=target, field_floor=floor,
        inner_hoop=hi, outer_hoop=ho, lr=lr, lt=lt,
        prior_field_energy=old_B, prior_field_minimum_particle_energy=old_cost_floor,
        all_speed_host_rejection=bound["rejected"], host_product_excess=bound["product_excess"],
        pointwise_field_energy=point["field_energy"], pointwise_drift_speed=point["speed"],
        pointwise_components=point["components"], pointwise_shortfall=point["shortfall"],
        pointwise_axial_end_force=point_field["axial_force_per_end_set"],
        pointwise_end_torque=point_field["torque_per_end_set"],
        pointwise_full_end_capacity=point["full_support_end_capacity"],
        pointwise_above_floor_end_capacity=point["above_floor_end_capacity"],
        pointwise_static_rate_parameter=rate,
        passive_initial_lower=passive_lower, passive_initial_upper=passive_upper,
        evolution_component_names=np.array(EVOLUTION_NAMES), evolution_component_energy=energies,
        evolution_initial_populations=initial, evolution_tensor=tensor,
        evolution_shortfall=cone["shortfall"], evolution_primal_deficit=deficits,
        evolution_dual_lower_bound=duals, evolution_component_exchange=exchange,
        all_current_hosts_free_evolution_deficit=free_deficits,
        all_current_hosts_free_evolution_dual=free_duals,
        evolution_control_store=bus["store_energy"],
        evolution_control_store_initial_lower=bus["lower_initial_energy"],
        evolution_control_store_initial_upper=bus["upper_initial_energy"], **replay_archive)
    result = dict(label=name, samples=list(D.shape), input_sha256=hashes,
        current_coefficient=chi, finite_annular_factor=R,
        previous_witness_current_demand=dict(field_energy=extrema(old_B),
            minimum_new_particle_energy=extrema(old_cost_floor),
            outer_overcompression_samples=int(np.count_nonzero(2*R*old_B > ho+1e-12)),
            maximum_return_to_axial_current_ratio=float(np.max(geom["return_to_axial_current_ratio"]))),
        zero_added_field=score(baseline["shortfall"], state),
        continuous_current_bound=dict(certified_rejected_samples=int(np.count_nonzero(bound["rejected"])),
            necessary_coefficient_upper=float(np.min(bound["coefficient_upper"])),
            worst_product_excess=worst(np.where(bound["applicable"], bound["product_excess"], -1.), state),
            scope="Independent new axial particle hosts; all speeds; free return, end and shear hardware"),
        pointwise_current_search=dict(**score(point["shortfall"], state),
            passing_samples=int(point_pass.sum()),
            unresolved_search_failures=int(np.count_nonzero(~point_pass & ~bound["rejected"])),
            positive_field_drift_speeds=extrema(point["speed"][point["field_energy"] > 0]),
            field_energy=extrema(point["field_energy"]),
            full_support_end_capacity_failures_on_passing_samples=int(np.count_nonzero(point_pass & (point["full_support_end_capacity"] < -1e-10))),
            above_floor_end_capacity_failures_on_passing_samples=int(np.count_nonzero(point_pass & (point["above_floor_end_capacity"] < -1e-10))),
            maximum_end_force=float(np.max(point_field["axial_force_per_end_set"])),
            maximum_end_torque=float(np.max(np.abs(point_field["torque_per_end_set"]))),
            maximum_static_rate_parameter=float(np.max(rate))),
        self_closed_axial_ends=dict(necessary_failure_samples=int(np.count_nonzero(bound["self_closed_end_gap"] > 1e-12)),
            worst_gap=worst(bound["self_closed_end_gap"], state)),
        conserved_particle_replays=replays,
        passive_transverse_population=dict(required_initial_energy=extrema(passive_lower),
            allowed_initial_energy=extrema(passive_upper),
            rejected_labels=int(np.count_nonzero(passive_lower > passive_upper+1e-12)),
            maximum_inventory_gap=float(np.max(passive_lower-passive_upper))),
        controlled_material_evolution=dict(uniform_energy_deficit=extrema(deficits),
            rejected_labels=int(np.count_nonzero(deficits > 1e-8)),
            currents_and_end_hardware_cost="zero in this optimistic test",
            initial_populations=initial.tolist(), minimum_component_energy=float(energies.min()),
            maximum_primal_violation=max(r["maximum_primal_violation"] for r in histories),
            maximum_dual_stationarity_error=max(r["dual_stationarity_error"] for r in histories),
            maximum_primal_dual_gap=float(np.max(np.abs(deficits-duals))),
            maximum_positive_dual_multiplier=max(r["maximum_dual_inequality_multiplier"] for r in histories),
            minimum_dual_bound_slack=min(r["minimum_dual_bound_slack"] for r in histories),
            maximum_fixed_population_error=population_error,
            maximum_exchange_sum_error=exchange_error,
            maximum_passive_panel_exchange=float(np.max(np.abs(exchange[:5]))),
            maximum_reciprocal_bus_error=reciprocal_error,
            closed_control_store_capacity_gap=extrema(bus["capacity_gap"]),
            net_component_exchange={name: extrema(exchange[i].sum(axis=0)) for i, name in enumerate(EVOLUTION_NAMES)}),
        all_current_hosts_free_evolution=dict(uniform_energy_deficit=extrema(free_deficits),
            rejected_labels=int(np.count_nonzero(free_deficits > 1e-8)),
            maximum_primal_dual_gap=float(np.max(np.abs(free_deficits-free_duals))),
            scope="Original and added current hosts and centrifugal reactions free; same fixed material and photon-control laws"))
    print(name, "certified host rejections", result["continuous_current_bound"]["certified_rejected_samples"],
          "history deficit", result["controlled_material_evolution"]["uniform_energy_deficit"], flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT / "supporting_reports/data/finite_containment")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    if args.output.exists():
        parser.error("choose a fresh output directory")
    names = [p.name.removesuffix("_summary.json") for p in sorted(PARENT.glob("*_n*_summary.json"))]
    if len(names) != 4:
        raise ValueError("Expected four parent histories")
    args.output.mkdir(parents=True)
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        results = list(pool.map(audit, [(n, str(args.output)) for n in names]))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        scope="Finite static coaxial interfaces, particle-host necessary tests, and fixed-material history programs",
        physical_containment_established=False,
        retained_inputs=["heat and geometry histories", "original magnetic fields", "original carrier tensors",
                         "original carrier hoop reactions", "existing support field floor"],
        explicit_relaxations=["ideal zero-thickness surfaces", "free bending and shear hardware in host bound",
            "pointwise search permits population changes", "history LP grants free added current hosts",
            "lossless, unlimited-rate control exchanges"],
        open_alternatives=["shared helical current populations", "different current coefficient or coil dimensions",
            "material rearrangement or a different constitutive law", "explicit shared axial/shear reaction paths"],
        histories=results)
    (args.output / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(),
        ROOT / "toolkit/adm_harness_cli/adm_harness/finite_containment.py",
        ROOT / "toolkit/adm_harness_cli/adm_harness/containment_ensemble.py",
        ROOT / "toolkit/adm_harness_cli/adm_harness/magnetic_load_balance.py",
        ROOT / "toolkit/adm_harness_cli/adm_harness/magnetic_geometry.py",
        ROOT / "toolkit/adm_harness_cli/tests/test_finite_containment.py"]
    for path in paths:
        shutil.copyfile(path, args.output / ("execution_"+path.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        parent_manifest_sha256={str(p.relative_to(ROOT)): sha256(p) for p in
                               (PARENT / "manifest.json", ENSEMBLE / "manifest.json")},
        output_sha256={p.name: sha256(p) for p in sorted(args.output.iterdir()) if p.is_file()})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
