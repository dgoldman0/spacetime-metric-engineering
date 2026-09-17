#!/usr/bin/env python3
"""Price finite electrical leads on linked local work-interface histories."""
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
from scipy.constants import c, G

from adm_harness.finite_electrical_leads import (
    ReconstructedWorkPorts, choose_carrier_inventory, hardware_screen, required_power_scale,
)

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT/"supporting_reports/data"
PARENTS = ("hosted_reaction_dynamics", "prepared_transfer_budget", "controlled_optical_transfer")
CHI = .0005


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified(group, name):
    path = DATA/group/name
    manifest = json.loads((DATA/group/"manifest.json").read_text())
    if sha256(path) != manifest["output_sha256"][name]:
        raise ValueError(f"Parent evidence mismatch: {path}")
    return path


def sample_grid(start, end, refinement):
    spacing = .25/refinement
    return np.unique(np.r_[np.arange(start, end, spacing), end,
        np.arange(-.15, .15, 1/(1024*refinement)),
        np.arange(.85, 1.15, 1/(1024*refinement))])


def trial(task):
    name, context, output, refinement = task
    path = verified("hosted_reaction_dynamics", name+"_states.npz")
    with np.load(path) as a:
        p = ReconstructedWorkPorts(a["time"], a["total_trace"], context)
        t = sample_grid(a["time"][0], a["time"][-1], refinement)
        state = p(t)
        line = choose_carrier_inventory(p, t, host_coefficient=CHI)
        result = line.evaluate(p, t, quadrature=8 if refinement == 1 else 12,
            source_capacitance=.01*state["capacitance"][:, 0])
        screen = hardware_screen(p, t, line, result)
        original = p.from_trace(a["total_trace"], a["total_trace_rate"], 0.)
        reconstruction = p(a["time"])
        raw_controls = []
        for boundary in (0., 1.):
            j = int(np.searchsorted(a["time"], boundary))
            raw_controls.append(dict(time=boundary,
                archived_adjacent_current_jump=float(abs(original["current"][:, j]-original["current"][:, j-1]).max()),
                archived_sample_separation=float(a["time"][j]-a["time"][j-1])))
        errors = dict(terminal_power=float(abs(state["port_work_error"]).max()),
            fixed_bias_energy=float(abs(state["energy"].sum(axis=0)-.62).max()),
            quadrature_effective_energy_theorem=float(abs(result["quadrature_energy_theorem_error"]).max()),
            pump_work_identity=float(abs(result["source_pump_power"].sum(axis=0)
                -state["mechanical_power"]-result["source_pump_correction"].sum(axis=0)).max()),
            trace_reconstruction=float(abs(reconstruction["total_trace"]-a["total_trace"]).max()),
            trace_rate_reconstruction=float(abs(reconstruction["total_trace_rate"]-a["total_trace_rate"]).max()))
        if max(errors[k] for k in ("terminal_power", "fixed_bias_energy", "pump_work_identity")) > 1e-10:
            raise ValueError(f"Electrical port accounting failed: {name}, {errors}")
        if errors["quadrature_effective_energy_theorem"] > 1e-8:
            raise ValueError(f"Partitioned finite-line quadrature failed: {name}, {errors}")
        if max(screen["maximum_drift"], screen["maximum_charge_fraction"]) >= .01:
            raise ValueError("Chosen finite carrier inventory exceeds its declared perturbation domain")
        optical = verified("controlled_optical_transfer", context["history"]+"_states.npz")
        with np.load(optical) as o:
            index = context["label_index"]
            delay, capacity = o["transit_delay"][index], o["reception_capacity"][:, index].sum()
            np.testing.assert_allclose(capacity, context["capacity"], rtol=2e-13)
            required_measure = required_power_scale(CHI)/(c**5/G*(capacity/delay))
        # A larger charge/mass coefficient already fails on the necessary
        # neutral electrode inventory alone, before fixture details matter.
        heavy_electrode_lower = 2*.01/.01*np.max(abs(original["charge"]), axis=1).sum()
    suffix = "" if refinement == 1 else "_refined"
    arrays = {k: v for k, v in result.items() if isinstance(v, np.ndarray)}
    arrays.update(time=t, load_voltage=state["voltage"], load_current=state["current"],
        load_current_rate=state["current_rate"], mechanical_power=state["mechanical_power"],
        load_field_energy=state["energy"], trace=state["total_trace"], trace_rate=state["total_trace_rate"],
        source_capacitance=.01*state["capacitance"][:, 0],
        lead_charge_per_length=line.absolute_charge_per_length, lead_kinetic_inductance=line.kinetic_inductance)
    np.savez_compressed(Path(output)/(name+suffix+"_leads.npz"), **arrays)
    row = dict(name=name+suffix, context=context["name"], refinement=refinement, evaluated_points=len(t),
        parent_input_sha256={str(path.relative_to(ROOT)): sha256(path), str(optical.relative_to(ROOT)): sha256(optical)},
        energy_and_host_screen=screen, errors=errors, ideal_step_controls=raw_controls,
        fixed_reconstruction_step=p.reconstruction_step,
        minimum_current_rise_to_transit_ratio=float(p.reconstruction_step/line.delay.max()),
        peak_bounded_piecewise_current_acceleration=float(abs(state["current_rate"]).max()),
        maximum_lead_kinetic_fraction=float((line.kinetic_inductance/line.magnetic_inductance).max()),
        lead_length=line.length, lead_inner_radius=line.inner_radius, lead_outer_radius=line.inner_radius*line.radius_ratio,
        finite_preview=float(line.delay.max()), prepared_line_and_source_energy=float(
            (result["line_energy"][:, 0]+result["source_capacitor_energy"][:, 0]).sum()),
        necessary_load_electrode_energy_at_chi_point01=heavy_electrode_lower,
        normalization=dict(capacity_per_label=float(capacity), delay=float(delay),
            desired_energy_per_time_watt=required_power_scale(CHI),
            required_label_solid_angle_measure=float(required_measure),
            cell_measure_and_spatial_packing_selected=False,
            global_metric_homothety_changes_energy_per_time=False),
        fixture_trace_and_evolving_work_closed=False, physical_converter_law_constructed=False,
        coupled_rotor_replay=False, local_frozen_macro_support=True)
    print(row["name"], "extra C", screen["added_energy_over_C"], "pump correction",
          screen["maximum_pump_power_correction"], "quadrature", errors["quadrature_effective_energy_theorem"], flush=True)
    return row


def compare_budgets(extra, output):
    summary = json.loads(verified("prepared_transfer_budget", "summary.json").read_text())
    rows = []
    for history in summary["histories"]:
        name = history["label"]
        path = verified("prepared_transfer_budget", name+"_prepared_budget.npz")
        with np.load(path) as a:
            capacity = a["capacity"]
            arrays = dict(capacity=capacity, t=a["t"], x=a["x"])
            variants = []
            for mass in (19, 20):
                base = a[f"mass{mass}_reserve_after_all_counted_allowances"]
                projected = base-extra*capacity
                allowance = float(np.min(base/capacity))
                variants.append(dict(inventory=mass,
                    uniform_extra_energy_allowance_over_C=allowance,
                    minimum_projected_reserve=float(projected.min()),
                    conditional_energy_projection_passed=bool(projected.min() > 0)))
                arrays[f"mass{mass}_reserve_after_uniform_lead_projection"] = projected
        np.savez_compressed(Path(output)/(name+"_energy_projection.npz"), **arrays)
        rows.append(dict(label=name, inherited_input_sha256={str(path.relative_to(ROOT)): sha256(path)},
            inventory_variants=variants))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=DATA/"finite_electrical_leads")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("positive worker count required")
    args.output.mkdir(parents=True, exist_ok=True)
    for group in PARENTS:
        for name, digest in json.loads((DATA/group/"manifest.json").read_text())["runtime_sha256"].items():
            if sha256(ROOT/name) != digest:
                raise ValueError(f"Parent runtime changed: {name}")
    parent = json.loads(verified("hosted_reaction_dynamics", "summary.json").read_text())
    tasks = [(context["name"]+"_"+direction, context, str(args.output), 1)
        for context in parent["contexts"] for direction in ("up", "down")]
    tasks.extend([(name, context, output, 2) for name, context, output, _ in tasks if context["name"] == "first_high"])
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        trials = list(pool.map(trial, tasks))
    extra = max(r["energy_and_host_screen"]["added_energy_over_C"] for r in trials)
    projections = compare_budgets(extra, args.output)
    refinement = []
    for row in (r for r in trials if r["refinement"] == 2):
        base = next(r for r in trials if r["name"] == row["name"].removesuffix("_refined"))
        differences = {key: abs(base["energy_and_host_screen"][key]-row["energy_and_host_screen"][key])
            for key in ("added_energy_over_C", "maximum_added_trace_over_C", "maximum_added_trace_rate",
                        "maximum_pump_power_correction")}
        refinement.append(dict(name=row["name"], absolute_changes=differences,
            continuous_extrema_enclosure=False))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        host_coefficient=CHI, carrier_and_electrode_charge_fraction=.01,
        fixture_energy_to_stress_allocation=2., extra_energy_projection_over_C=extra,
        trials=trials, mesh_refinement=refinement, inherited_budget_projections=projections,
        finite_effective_line_energy_identity=True, carrier_kinetic_and_rest_inventory_counted=True,
        complementary_field_terminal_work_counted=True, complementary_fixed_fixture_allocation_counted=True,
        load_field_bias_counted_once=True, source_capacitor_states_counted=True,
        passive_matched_load_sink_introduced=False, fixed_rise_reconstruction_distinct_from_coupled_replay=True,
        ideal_step_requires_unbounded_bandwidth=True, reconstruction_strictly_bandlimited=False,
        added_trace_unbalanced_until_fixture_law=True, fixture_constitutive_law_constructed=False,
        fixture_work_and_optical_electrical_transducer_closed=False,
        full_history_hardware_envelope_established=False, complete_physical_rail_feasibility_established=False,
        inherited_matched_zero_work_thermal_relay_condition=True,
        moving_thermal_relay_corrections_in_this_inherited_projection=False,
        normalization=dict(source_stress="G_mu_nu/(8*pi), geometric units",
            inherited_capacity="D-weighted energy per radial label and solid angle; D=ell*R^2, ell=gamma*b",
            physical_energy="(c^4/G)*Lg*C_hat*Delta_x_hat*Delta_Omega",
            physical_delay="Lg*delta_hat/c",
            physical_energy_per_time="(c^5/G)*(C_hat/delta_hat)*Delta_x_hat*Delta_Omega",
            extra_proper_volume_factor_required=False, label_measure_and_packing_required=True,
            independent_absolute_energy_and_delay_for_same_homothetic_rail=False),
        primary_sources=[dict(title="Haus and Melcher, Electromagnetic Fields and Energy, section 14.2",
            url="https://web.mit.edu/6.013_book/www/chapter14/14.2.html", supports="Coax fields and ideal-line Poynting energy theorem"),
            dict(title="Boaventura et al., IEEE Transactions on Applied Superconductivity 30, 1500507 (2020)",
            url="https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=928652",
            supports="Separate positive carrier kinetic inductance in effective superconducting line models; supplies no rail material endorsement")])
    (args.output/"summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(), ROOT/"toolkit/adm_harness_cli/adm_harness/finite_electrical_leads.py",
        ROOT/"toolkit/adm_harness_cli/tests/test_finite_electrical_leads.py"]
    normalization_sources = [ROOT/"active_rail_technical_disclosure.tex",
        ROOT/"toolkit/adm_harness_cli/scripts/audit_finite_containment.py",
        ROOT/"toolkit/adm_harness_cli/scripts/audit_virtual_cell_thermal_replay.py"]
    for path in paths:
        shutil.copyfile(path, args.output/("execution_"+path.name))
    manifest = dict(runtime_sha256={str(path.relative_to(ROOT)): sha256(path) for path in paths},
        normalization_source_sha256={str(path.relative_to(ROOT)): sha256(path) for path in normalization_sources},
        parent_manifest_sha256={str((DATA/group/"manifest.json").relative_to(ROOT)):
            sha256(DATA/group/"manifest.json") for group in PARENTS},
        output_sha256={path.name: sha256(path) for path in sorted(args.output.iterdir())
            if path.is_file() and path.name != "manifest.json"})
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
