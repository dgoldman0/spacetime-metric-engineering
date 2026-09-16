#!/usr/bin/env python3
"""Parallel bounded magnetic-loop comparison on authenticated thermal replays."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import shutil
import subprocess
import sys
import time

import numpy as np

from adm_harness.magnetic_load_balance import (
    radiation_inventory, loop_field, attached_bank, balance_pitch,
    loop_currents, carrier_limit, loop_work, straight_sleeve,
    conserved_sleeve_interval, sleeve_at_inventory, support_cone,
)
from adm_harness.source_ledger import sha256_file
from audit_joint_dense_work import DenseHistory
from audit_virtual_cell_material_bank import verify_outputs
from audit_virtual_cell_thermal_replay import geometry, integrate_panels, full_budget
from run_poynting_delivery import BASE, ROOT, write_json

ASPECTS = (.005, .01, .025, .05, .1, .2)


def limits(value):
    return dict(minimum=float(np.min(value)), maximum=float(np.max(value)))


def witness(state, value):
    i, j = np.unravel_index(np.argmax(value), value.shape)
    return dict(time=float(state["t"][i]), position=float(state["x"][j]),
                value=float(value[i, j]), time_index=int(i), position_index=int(j))


def evaluate(spec):
    path, output, current_order = spec
    path, output = Path(path), Path(output)
    started = time.monotonic()
    meta = json.loads(path.with_name(path.name.replace("_states.npz", "_summary.json")).read_text())
    if not meta.get("full_sampled_gate_passes"):
        raise ValueError("accepted full replay required")
    with np.load(path) as archive:
        state = {k: archive[k] for k in archive.files}
    t, D, R, ell = (state[k] for k in ("t", "D", "radius", "ell"))
    lr, lt = ell/ell[0], R/R[0]
    C = state["receiver_cold_energy"]
    heat = state["bank_fluid_cold_panel_heat"]+state["bank_photon_cold_panel_heat"]
    if not np.allclose(np.diff(C, axis=0), heat, atol=1e-10, rtol=0):
        raise ValueError("replay cold receipts differ from stored inventory")
    phase = state["amplitude"]/R**2
    drift = meta["guide_drift_bound"]
    old_short, _, _ = full_budget(*state["credited_target"], phase=phase,
        radiation=state["balanced_radiation_rest"], thermal=state["thermal_reservoir_rest"],
        receiver=state["receiver_rest"], wall=state["wall_rest"],
        incident=state["absorption_rest"],
        returned=state["work_return_rest"]+state["heat_return_rest"],
        guide_multiplier=0. if drift is None else .5*(drift**-2-1))
    replay_error = float(np.max(abs(old_short-state["density_shortfall"])))
    if replay_error > 1e-10:
        raise ValueError("original full tensor margin failed independent reconstruction")
    h = DenseHistory("routed_family", ROOT/meta["input"])
    model = h.h.reference.h.model
    means = {}
    for order in (4, 8):
        means[order] = integrate_panels(t, h.edges,
            lambda at: geometry(model, at, state["x"])["D"]**(1/3), order=order)/np.diff(t)[:, None]
    evolved = {order: radiation_inventory(C[0], heat, D, means[order]) for order in (4, 8)}
    E = evolved[8]["energy"]
    cases = []
    for mode, energy in (("frozen_energy", C), ("compression_evolved", E)):
        for share in (False, True):
            for aspect in ASPECTS:
                pitch = balance_pitch(state, energy, aspect=aspect, share_core=share)
                field = loop_field(energy, lr, lt, aspect=aspect, angle=pitch["angle"])
                result = attached_bank(state, energy, field, share_core=share)
                cases.append(dict(mode=mode, share_core_field=share, aspect=aspect,
                    angle_degrees=float(np.rad2deg(pitch["angle"])), **pitch,
                    worst_density=witness(state, result["shortfall"]),
                    minimum_added_rest_allowance=float((-D*result["shortfall"]).min()),
                    maximum_field_energy=float(field["energy"].max()),
                    maximum_core_field_overlap=float(result["core_field_overlap"].max()),
                    carrier_energy_included=False))
    # Fixed-history hot/both controls isolate the earlier startup obstruction.
    for reopened, key in (("hot", "receiver_hot_energy"), ("both", "receiver_thermal_energy")):
        energy = state[key]
        pitch = balance_pitch(state, energy, aspect=.01, reopened=reopened)
        cases.append(dict(mode="frozen_energy", reopened=reopened, aspect=.01,
                          angle_degrees=float(np.rad2deg(pitch["angle"])), **pitch))

    # A finite selected geometry, followed by explicitly counted current carriers.
    aspect = .01
    selected = balance_pitch(state, E, aspect=aspect)
    angle = 0. if selected["angle"] < 1e-4 else selected["angle"]
    selected["angle"] = angle
    field = loop_field(E, lr, lt, aspect=aspect, angle=angle)
    unloaded = attached_bank(state, E, field)
    tube_ratio, fill = .1, .1
    cell_width = state["edges"][-1]-state["edges"][0]
    # A capsule spans L*cos(theta)+2*a+2*r across the radial direction.
    # Its two straight legs occupy the same span on the outgoing/return paths.
    leg0 = .5*cell_width*ell[0]/(abs(np.cos(angle))+2*aspect*(1+tube_ratio))
    current = {}
    for order in (current_order, 2*current_order):
        current[order] = loop_currents(E, D, lr, lt, leg0, aspect=aspect, angle=angle,
                                       fill_fraction=fill, tube_ratio=tube_ratio, order=order)
    current_fine = current[2*current_order]
    unit_tensor = current_fine["unit_tensor"]
    coefficient, slopes = carrier_limit(unloaded["facets"], unit_tensor)
    sleeve0 = straight_sleeve(unloaded["facets"], E, D, lr, lt, aspect=aspect, angle=angle)
    H, f = sleeve0["hoop_energy_floor"], sleeve0["radial_tangent_fraction"]

    def fixed_sleeve(chi, fraction=1.):
        return conserved_sleeve_interval(unloaded["facets"]+chi*slopes, D, H, f,
                                        stress_fraction=fraction)

    low, high = 0., max(0., coefficient)
    for _ in range(24):
        midpoint = .5*(low+high)
        if fixed_sleeve(midpoint)["feasible"].all():
            low = midpoint
        else:
            high = midpoint
    sleeve_current_limit = low
    trial_coefficient = .5*sleeve_current_limit
    loaded = attached_bank(state, E, field, carrier_tensor=trial_coefficient*unit_tensor)
    sleeve_comparisons = []
    for fraction in (1., .99, .9, .75, .5, .25, .1, .01):
        flexible = straight_sleeve(loaded["facets"], E, D, lr, lt,
            aspect=aspect, angle=angle, stress_fraction=fraction)
        fixed = fixed_sleeve(trial_coefficient, fraction)
        sleeve_comparisons.append(dict(stress_fraction=fraction,
            adjustable_energy_maximum_shortfall=float(flexible["shortfall"].max()),
            conserved_energy_lower=limits(fixed["lower"]), conserved_energy_upper=limits(fixed["upper"]),
            conserved_energy_minimum_gap=fixed["minimum_gap"],
            feasible_labels=int(fixed["feasible"].sum())))
    thresholds = {}
    for name, chi in (("zero_current_cost", 0.), ("counted_currents", trial_coefficient)):
        low, high = .001, 1.
        if not fixed_sleeve(chi, high)["feasible"].all():
            thresholds[name] = None
            continue
        for _ in range(24):
            midpoint = .5*(low+high)
            if fixed_sleeve(chi, midpoint)["feasible"].all():
                high = midpoint
            else:
                low = midpoint
        thresholds[name] = high
    fixed = fixed_sleeve(trial_coefficient)
    if not fixed["feasible"].all():
        raise RuntimeError("selected loop fails even the unit-strength straight-sleeve comparison")
    sleeve_inventory = fixed["lower"]+.05*(fixed["upper"]-fixed["lower"])
    sleeve = sleeve_at_inventory(loaded["facets"], D, H, f, sleeve_inventory)
    complete = support_cone(*(loaded["residual_target"]-sleeve["tensor"]),
                            loaded["radial_field_floor"])
    sleeve_pressure = D*sleeve["tensor"][1:]
    sleeve_work = (-.5*(sleeve_pressure[0, 1:]+sleeve_pressure[0, :-1])*np.diff(np.log(ell), axis=0)
                   -(sleeve_pressure[1, 1:]+sleeve_pressure[1, :-1])*np.diff(np.log(R), axis=0))
    current_error = float(np.max(abs(current[current_order]["unit_tensor"]-unit_tensor))
                          /np.max(abs(unit_tensor)))
    coarse_coefficient, _ = carrier_limit(unloaded["facets"], current[current_order]["unit_tensor"])
    coefficient_error = abs(coefficient-coarse_coefficient)/max(abs(coefficient), 1e-300)
    mechanical = loop_work(t, field["energy"], field["radial"], ell, R)

    # The remaining auxiliary tensor gives the actual attachment loads.
    # Its spatial divergence and constitutive response have not been supplied.
    support_radial = complete["radial_wave"]-complete["field"]
    support_angular = complete["field"]+.5*complete["angular_wave"]-complete["membrane"]
    reconstruction_error = max(
        float(np.max(abs(support_radial+sleeve["tensor"][1]-loaded["residual_target"][1]))),
        float(np.max(abs(support_angular+sleeve["tensor"][2]-loaded["residual_target"][2]))),
        float(np.max(abs(complete["spare"]+complete["field"]+complete["radial_wave"]
                         +complete["angular_wave"]+complete["membrane"]+sleeve["tensor"][0]
                         -loaded["residual_target"][0]))))
    # Macroscopic contraction of the remaining support with the registered strain.
    aux_work = (-.5*(D[1:]*support_radial[1:]+D[:-1]*support_radial[:-1])*np.diff(np.log(ell), axis=0)
                -(D[1:]*support_angular[1:]+D[:-1]*support_angular[:-1])*np.diff(np.log(R), axis=0))
    # An admissible colder coefficient can always be reselected in this relaxed
    # caloric model: a_new <= a_old min(C_old * J / E_new).
    # This preserves/reduces cold temperatures; it changes the physical packing.
    cold_coefficient_factor = float(np.min(C*(D/D[0])/E))
    # Compression heats the bank; finite positive receipt keeps entropy proxy growing.
    entropy = E**.75*(D/D[0])**.25
    label = ("first" if np.mean(state["x"]) < -1.99 else "second")+f"_n{len(state['x'])}_t{len(t)}"
    summary = dict(label=label, input=str(path.relative_to(ROOT)),
        time_samples=len(t), spatial_samples=len(state["x"]), cases=cases,
        original_margin_reconstruction_error=replay_error,
        cold_final_reference_energy=limits(C[-1]), cold_final_evolved_energy=limits(E[-1]),
        maximum_compression_energy=float((E-C).max()),
        compression_work_per_label=limits(evolved[8]["compression_work"].sum(axis=0)),
        minimum_entropy_proxy_increment=float(np.diff(entropy, axis=0).min()),
        radiation_energy_quadrature_difference=float(abs(E-evolved[4]["energy"]).max()),
        radiation_balance_residual=float(abs(evolved[8]["balance_residual"]).max()),
        selected=dict(aspect=aspect, angle_degrees=float(np.rad2deg(angle)), **selected,
            fill_fraction=fill, tube_to_bend_radius_ratio=tube_ratio,
            whole_loop_radial_span_fraction=.5,
            maximum_angular_span_over_curvature_radius=float(np.max(
                (leg0*abs(np.sin(angle))+2*aspect*leg0*(1+tube_ratio))/R[0])),
            beta_limit=1., maximum_current_drift=current_fine["maximum_drift"],
            current_coefficient_unit="m/abs(q), c=mu0=1, same normalized Maxwell tensor as archived stresses",
            maximum_current_coefficient=coefficient,
            maximum_current_coefficient_with_conserved_straight_sleeve=sleeve_current_limit,
            tested_current_coefficient=trial_coefficient,
            current_inventory_rule="each of sheet/bend families retains sqrt(2)*max_t integral|J| times m/abs(q)",
            counted_current_rest_inventory=limits(trial_coefficient*(
                current_fine["unit_sheet_rest_inventory"]+current_fine["unit_bend_rest_inventory"])),
            straight_sleeve_conserved_energy=limits(sleeve_inventory),
            straight_sleeve_minimum_stress_fraction=thresholds,
            straight_sleeve_comparisons=sleeve_comparisons,
            straight_sleeve_axial_interval_violation=sleeve["axial_interval_violation"],
            straight_sleeve_work_input_to_hold_fixed_energy=limits(
                np.maximum(-sleeve_work, 0).sum(axis=0)),
            straight_sleeve_work_output_to_hold_fixed_energy=limits(
                np.maximum(sleeve_work, 0).sum(axis=0)),
            current_quadrature_orders=[current_order, 2*current_order],
            current_tensor_relative_quadrature_difference=current_error,
            current_coefficient_relative_quadrature_difference=coefficient_error,
            complete_loop_initial_energy=limits(field["energy"][0]),
            complete_loop_final_energy=limits(field["energy"][-1]),
            complete_loop_electrical_input=limits(np.maximum(mechanical["electrical"], 0).sum(axis=0)),
            complete_loop_electrical_output=limits(np.maximum(-mechanical["electrical"], 0).sum(axis=0)),
            complete_loop_mechanical_work=limits(mechanical["mechanical"].sum(axis=0)),
            complete_loop_work_identity_error=float(abs(mechanical["balance_residual"]).max()),
            remaining_support_radial_pressure=limits(support_radial),
            remaining_support_angular_pressure=limits(support_angular),
            remaining_support_mechanical_work=limits(aux_work.sum(axis=0)),
            tensor_reconstruction_error=reconstruction_error,
            worst_density_with_currents=witness(state, loaded["shortfall"]),
            minimum_added_rest_allowance_with_currents=float((-D*loaded["shortfall"]).min()),
            tensor_and_current_budget_passes=bool(coefficient > 0 and loaded["shortfall"].max() <= 0),
            worst_density_with_conserved_straight_sleeve=witness(state, complete["shortfall"]),
            straight_sleeve_necessary_gate_passes=bool(complete["shortfall"].max() <= 1e-12),
            cold_caloric_coefficient_factor_upper_bound=cold_coefficient_factor),
        scope=dict(shared_core_overlap_granted=True, exterior_loop_field_assumed_zero=True,
            full_return_and_bend_field_energy_counted=True,
            cold_compression_work_counted=True, current_kinetic_energy_and_pressure_counted=True,
            straight_section_boundary_pressure_counted=True,
            bend_mechanical_containment_supplied=False, straight_sleeve_constitutive_law_supplied=False,
            sleeve_mechanical_transfer_routed=False,
            fixed_heat_receipts_retained=True, old_cold_enclosure_credit_reallocated=True,
            current_host_constitutive_law_supplied=False, material_species_selected=False,
            full_spatial_force_equations_solved=False, field_induction_tensor_supplied=False,
            new_electrical_port_routed=False, changed_contact_network_replayed=False,
            full_thermal_material_or_device_validated=False,
            microscopic_field_sharing_with_phase_demonstrated=False,
            continuous_time_bound_certified=False),
        elapsed_seconds=time.monotonic()-started)
    np.savez_compressed(output/(label+"_states.npz"), t=t, x=state["x"],
        evolved_cold_energy=E, compression_work=evolved[8]["compression_work"],
        loop_radial_field_energy=field["radial"], loop_transverse_field_energy=field["transverse"],
        current_tensor=trial_coefficient*unit_tensor,
        shortfall_without_currents=unloaded["shortfall"],
        shortfall_with_currents=loaded["shortfall"],
        shortfall_with_straight_sleeve=complete["shortfall"],
        straight_sleeve_tensor=sleeve["tensor"], straight_sleeve_inventory=sleeve_inventory,
        straight_sleeve_mechanical_panel_work=sleeve_work,
        core_field_overlap=loaded["core_field_overlap"],
        support_radial_pressure=support_radial, support_angular_pressure=support_angular,
        loop_electrical_panel_transfer=mechanical["electrical"])
    write_json(output/(label+"_summary.json"), summary)
    print(json.dumps(dict(label=label, current_coefficient_limit=coefficient,
        sleeve_minimum_stress_fraction=thresholds["counted_currents"],
        final_density_shortfall=summary["selected"]["worst_density_with_conserved_straight_sleeve"]["value"],
        elapsed_seconds=summary["elapsed_seconds"])), flush=True)
    return summary


def default_sources():
    catalog = BASE/"virtual_cell_material_bank_fixed_history_verified/summary.json"
    rows = json.loads(catalog.read_text())["cases"]
    paths = [ROOT/row["replay_input"] for row in rows]
    coarse_meta = sorted((BASE/"virtual_cell_bank_fluid_donor_first_joint_temperature_endpoints").glob("*_summary.json"))
    if len(coarse_meta) != 1:
        raise ValueError("one registered first-location coarse temperature reference required")
    paths.append(ROOT/json.loads(coarse_meta[0].read_text())["input"])
    paths.append(paths[1].with_name(paths[1].name.replace("_factor4_", "_factor2_")))
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-name", required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--current-order", type=int, default=16)
    parser.add_argument("--sources", nargs="+")
    args = parser.parse_args()
    if not 1 <= args.workers <= 6 or args.current_order < 8:
        parser.error("one through six workers and current quadrature order >=8 required")
    output = BASE/args.output_name
    if output.exists():
        raise RuntimeError("preserve completed magnetic-load comparison")
    paths = [ROOT/p for p in args.sources] if args.sources else default_sources()
    hashes, historical = {}, []
    for path in paths:
        meta = path.with_name(path.name.replace("_states.npz", "_summary.json"))
        checked, history = verify_outputs(path.parent, [path.name, meta.name])
        hashes.update(checked); historical.extend(history)
    runtime = [Path(__file__), ROOT/"toolkit/adm_harness_cli/tests/test_magnetic_load_balance.py"]
    for module in list(sys.modules.values()):
        filename = getattr(module, "__file__", None)
        if filename:
            p = Path(filename).resolve()
            if p.suffix == ".py" and p.is_relative_to(ROOT):
                runtime.append(p)
    hashes.update({str(p.relative_to(ROOT)): sha256_file(p) for p in runtime})
    output.mkdir()
    workers = min(args.workers, len(paths))
    with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        cases = list(pool.map(evaluate, [(p, output, args.current_order) for p in paths]))
    for name, expected in hashes.items():
        if sha256_file(ROOT/name) != expected:
            raise RuntimeError("input changed during magnetic comparison: "+name)
    write_json(output/"summary.json", dict(cases=cases))
    snapshot = {}
    for p in (Path(__file__), ROOT/"toolkit/adm_harness_cli/adm_harness/magnetic_load_balance.py",
              ROOT/"toolkit/adm_harness_cli/tests/test_magnetic_load_balance.py"):
        name = "execution_"+p.name
        shutil.copyfile(p, output/name)
        snapshot[str(p.relative_to(ROOT))] = name
    write_json(output/"manifest.json", dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        workers=workers, input_sha256=hashes, historical_source=historical,
        source_snapshot=snapshot,
        output_sha256={p.name: sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__ == "__main__":
    main()
