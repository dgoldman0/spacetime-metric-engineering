#!/usr/bin/env python3
"""Audit constituent versus assembly constraints on the saved magnetic jacket.

Four independent history jobs retain the original magnetic fields and their
full particle-carrier costs. New allocations retain local stress directions,
hoop sharing, integrated normal balance, and each component's energy.
Only numerical evidence and provenance are emitted; narrative is authored
separately in the supporting report.
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

from adm_harness.containment_ensemble import (
    ASSEMBLY_NAMES, SUPPORT_NAMES, SUPPORT_BASIS, allocate, average_tensor,
    component_program, host_cost_threshold, material_basis, required_exchange,
    tensile_strength_floor,
)
from adm_harness.current_carrying_wall import necessary_wall_gaps, component_feasibility
from adm_harness.magnetic_load_balance import attached_bank, support_cone


ROOT = Path(__file__).resolve().parents[3]
PARENT = ROOT / "supporting_reports/data/magnetic_geometry"
PREFIX = "shared_candidate_"
SCENARIOS = (("ideal_ensemble", 0., 1.), ("host_0p1", .1, 1.),
             ("transverse_sheet_0p85", 0., .85),
             ("sheet_0p85_host_0p1", .1, .85), ("host_1", 1., 1.))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extrema(values):
    return dict(minimum=float(np.min(values)), maximum=float(np.max(values)))


def worst_record(values, state):
    index = np.unravel_index(np.argmax(values), values.shape)
    return dict(time_index=int(index[0]), position_index=int(index[1]),
                time=float(state["t"][index[0]]), position=float(state["x"][index[1]]),
                value=float(values[index]))


def audit(task):
    name, output_name = task
    path, output = PARENT / name, Path(output_name)
    meta = json.loads(path.read_text())
    archive_path = path.with_name(meta["label"]+"_states.npz")
    state_path = ROOT / meta["input"]
    manifest = json.loads((PARENT / "manifest.json").read_text())
    expected = {path: manifest["output_sha256"][path.name],
                archive_path: manifest["output_sha256"][archive_path.name],
                state_path: manifest["input_sha256"][meta["input"]]}
    hashes = {str(p.relative_to(ROOT)): sha256(p) for p in expected}
    for p, value in expected.items():
        if hashes[str(p.relative_to(ROOT))] != value:
            raise ValueError(f"Parent hash mismatch: {p}")
    with np.load(archive_path) as a:
        saved = {k: a[k] for k in a.files if k.startswith(PREFIX)
                 or k in ("t", "x", "evolved_cold_energy")}
    with np.load(state_path) as a:
        state = {k: a[k] for k in a.files}
    for axis in ("t", "x"):
        np.testing.assert_array_equal(state[axis], saved[axis])
    D = state["D"]
    field = {k: saved[PREFIX+"loop_"+k+"_field_energy"] for k in ("radial", "transverse")}
    loaded = attached_bank(state, saved["evolved_cold_energy"], field,
                           carrier_tensor=saved[PREFIX+"carrier_tensor"])
    old_wall = sum(saved[PREFIX+side+"_sleeve_tensor"] for side in ("inner", "outer"))
    old_residual = saved[PREFIX+"remaining_support_tensor"]
    reconstruction = float(np.max(np.abs(loaded["residual_target"]-old_wall-old_residual)))
    if reconstruction > 1e-12:
        raise ValueError("Parent tensor reconstruction failed")
    hoops = [saved[PREFIX+side+"_hoop"] for side in ("inner", "outer")]
    H = sum(hoops)
    F, target, floor = loaded["facets"], loaded["residual_target"], loaded["radial_field_floor"]
    old_tests, indices = {}, set()
    for law, gap in necessary_wall_gaps(F, H).items():
        integrated = D*gap
        record = worst_record(integrated, state)
        idx = (record["time_index"], record["position_index"])
        indices.add(idx)
        lp = component_feasibility(target[:, idx[0], idx[1]]*D[idx], floor[idx]*D[idx],
                                   H[idx]*D[idx], law=law)
        old_tests[law] = dict(maximum_integrated_gap=float(np.max(integrated)),
            violating_samples=int(np.count_nonzero(integrated > 1e-12)),
            worst_sample=record, independent_lp_status=int(lp.status))
        if record["value"] > 1e-12 and lp.status != 2:
            raise ValueError("Legacy necessary bound failed its independent check")
    rng = np.random.default_rng(522)
    for flat in rng.choice(D.size, size=min(96, D.size), replace=False):
        indices.add(tuple(np.unravel_index(flat, D.shape)))

    scenarios, archived = {}, {}
    for key, host, strength in SCENARIOS:
        result = allocate(F, H, host_per_field=host, transverse_strength=strength)
        residual = target-result["averaged_tensor"]
        cone = support_cone(*residual, floor)
        np.testing.assert_allclose(cone["shortfall"], result["minimum_shortfall"], atol=2e-12)
        gaps = D*cone["shortfall"]
        record = worst_record(gaps, state)
        indices.add((record["time_index"], record["position_index"]))
        scenarios[key] = dict(host_per_field=host, transverse_sheet_strength=strength,
            maximum_integrated_shortfall=float(np.max(gaps)),
            minimum_integrated_inventory_reserve=float(np.min(D*cone["spare"])),
            violating_samples=int(np.count_nonzero(gaps > 1e-12)), worst_sample=record)
        if key == "ideal_ensemble":
            base, base_cone = result, cone
            support = np.stack([cone[k] for k in ("field", "radial_wave", "angular_wave", "membrane", "spare")])
            energies = np.concatenate([result["components"], support])*D
            basis = np.column_stack([average_tensor(material_basis()), SUPPORT_BASIS])
            reconstructed = np.einsum("ij,j...->i...", basis, energies)/D
            tensor_error = float(np.max(np.abs(reconstructed-target)))
            if tensor_error > 2e-12 or np.min(energies) < -1e-12:
                raise ValueError("Ensemble allocation failed full tensor or positivity check")
            local = result["local_tensor"]
            boundary_error = 0.
            for side, hoop in zip(("inner", "outer"), hoops):
                fraction = hoop/H
                boundary_error = max(boundary_error, float(np.max(np.abs(-local[2]*fraction-hoop))),
                                     float(np.max(np.abs(local[3]*fraction))))
                archived[side+"_component_energy"] = result["components"]*D*fraction
            lr = state["ell"]/state["ell"][0]
            lt = state["radius"]/state["radius"][0]
            exchange = required_exchange(energies, energies*basis[1, :, None, None],
                                         2*energies*basis[2, :, None, None], lr, lt)
            total = required_exchange((D*target[0])[None], (D*target[1])[None],
                                      (2*D*target[2])[None], lr, lt)[0]
            exchange_error = float(np.max(np.abs(exchange.sum(axis=0)-total)))
            if exchange_error > 1e-11:
                raise ValueError("Component exchange failed total-accounting identity")
            archived.update(t=state["t"], x=state["x"], D=D,
                component_names=np.array(ASSEMBLY_NAMES+SUPPORT_NAMES), component_energy=energies,
                component_required_exchange=exchange, local_assembly_tensor=local,
                residual_support_tensor=residual, inner_hoop=hoops[0], outer_hoop=hoops[1],
                integrated_shortfall=gaps, retained_old_carrier_tensor=saved[PREFIX+"carrier_tensor"])
    # Check different derivations, all legacy worst points, each scenario's
    # weakest point, and seeded points across the rest of the histories.
    maximum_lp_error = 0.
    for key, host, strength in SCENARIOS:
        result = allocate(F, H, host_per_field=host, transverse_strength=strength)
        checks = []
        for idx in sorted(indices):
            scale = D[idx]
            lp = component_program(target[:, idx[0], idx[1]]*scale, floor[idx]*scale,
                                   H[idx]*scale, host_per_field=host, transverse_strength=strength)
            gap = float(scale*result["minimum_shortfall"][idx])
            if gap > 1e-10:
                if lp.status != 2:
                    raise ValueError("Independent ensemble LP disagrees with rejection")
            elif gap < -1e-10:
                if not lp.success:
                    raise ValueError("Independent ensemble LP disagrees with feasibility")
                error = abs(lp.fun-gap)
                maximum_lp_error = max(maximum_lp_error, error)
                if error > 2e-9:
                    raise ValueError("Independent ensemble LP disagrees with reserve")
            checks.append(dict(time_index=int(idx[0]), position_index=int(idx[1]),
                               status=int(lp.status), integrated_shortfall=gap))
        scenarios[key]["component_lp_checks"] = checks
    control = old_tests["canonical_joint_stress"]["worst_sample"]
    idx = (control["time_index"], control["position_index"])
    orientation_tests = {}
    for kind in ("hoop_maxwell", "normal_maxwell", "axial_photons"):
        lp = component_program(target[:, idx[0], idx[1]]*D[idx], floor[idx]*D[idx],
                               H[idx]*D[idx], field_kind=kind)
        orientation_tests[kind] = dict(status=int(lp.status),
            components=lp.x.tolist() if lp.success else None)
    if [orientation_tests[k]["status"] for k in orientation_tests] != [0, 2, 2]:
        raise ValueError("Equal-average/different-duty control gave an unexpected result")
    bound = host_cost_threshold(F, H, volume=D)
    fractions = base["components"][:4]/H
    # The transverse sheet contributes k*M; baseline k=1 here.
    summaries = {name: dict(integrated_energy=extrema(archived["component_energy"][i]),
        net_required_exchange=extrema(archived["component_required_exchange"][i].sum(axis=0)),
        gross_positive_component_exchange=extrema(np.maximum(archived["component_required_exchange"][i], 0.).sum(axis=0)))
        for i, name in enumerate(ASSEMBLY_NAMES+SUPPORT_NAMES)}
    output_file = output / (meta["label"]+"_states.npz")
    np.savez_compressed(output_file, **archived)
    return dict(label=meta["label"], time_samples=int(D.shape[0]), spatial_samples=int(D.shape[1]),
        input_sha256=hashes, output_archive=output_file.name,
        retained_carrier_energy=extrema(D*saved[PREFIX+"carrier_tensor"][0]),
        parent_reconstruction_error=reconstruction, assembly_tensor_reconstruction_error=tensor_error,
        separate_boundary_hoop_and_normal_error=boundary_error,
        required_exchange_accounting_error=exchange_error, maximum_lp_reserve_error=maximum_lp_error,
        legacy_restricted_tests=old_tests, ensemble_scenarios=scenarios,
        same_average_orientation_control=dict(sample=control, tests=orientation_tests),
        pressureless_field_host_allowance=bound,
        closed_ensemble_best_tensile_constituent_strength_lower_bound=worst_record(
            tensile_strength_floor(target[0], H), state),
        transverse_sheet_strength_floor_with_other_constituents_ideal=1/(1+bound["lower"]),
        ideal_hoop_load_fractions={name: extrema(fractions[i]) for i, name in enumerate(ASSEMBLY_NAMES[:4])},
        components=summaries,
        net_required_exchange_of_whole_allocated_group=extrema(
            archived["component_required_exchange"].sum(axis=(0, 1))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "supporting_reports/data/containment_ensemble")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    if args.output.exists():
        parser.error("choose a fresh output directory")
    paths = sorted(PARENT.glob("*_summary.json"))
    if len(paths) != 4:
        raise ValueError("Expected two resolutions at both locations")
    args.output.mkdir(parents=True)
    with ProcessPoolExecutor(max_workers=args.workers,
                             mp_context=multiprocessing.get_context("spawn")) as pool:
        results = list(pool.map(audit, [(p.name, str(args.output)) for p in paths]))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        scope="Pointwise constituent-resolved tensor and integrated load allocation on fixed saved histories",
        axes=["tube_axis", "hoop", "normal"], assembly_component_names=ASSEMBLY_NAMES,
        local_component_tensors=material_basis().T.tolist(), support_component_names=SUPPORT_NAMES,
        retained_constraints=dict(original_field_and_heat_history=True, original_carrier_energy=True,
            original_carrier_centrifugal_hoop_load=True, separate_inner_outer_loads=True,
            each_constituent_energy_counted_once=True, total_integrated_normal_stress=0.),
        remaining_construction_requirements=["finite spatial material and Maxwell solution",
            "currents and host stress for the added hoop field", "interface and bend force closure",
            "constitutive histories and their reciprocal exchanges", "thermal response and coupled stability"],
        histories=results)
    (args.output / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    runtime_paths = [Path(__file__).resolve(),
        ROOT / "toolkit/adm_harness_cli/adm_harness/containment_ensemble.py",
        ROOT / "toolkit/adm_harness_cli/adm_harness/current_carrying_wall.py",
        ROOT / "toolkit/adm_harness_cli/adm_harness/magnetic_load_balance.py",
        ROOT / "toolkit/adm_harness_cli/tests/test_containment_ensemble.py"]
    for path in runtime_paths:
        shutil.copyfile(path, args.output / ("execution_"+path.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in runtime_paths},
        parent_manifest_sha256=sha256(PARENT / "manifest.json"),
        output_sha256={p.name: sha256(p) for p in sorted(args.output.iterdir()) if p.is_file()})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    for row in results:
        ideal = row["ensemble_scenarios"]["ideal_ensemble"]
        print(row["label"], "violations", ideal["violating_samples"],
              "reserve", ideal["minimum_integrated_inventory_reserve"],
              "host allowance", row["pressureless_field_host_allowance"]["lower"], flush=True)


if __name__ == "__main__":
    main()
