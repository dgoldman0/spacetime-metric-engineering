#!/usr/bin/env python3
"""Price load-bearing optical facets and allocate short-gap electric work ports."""
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

from adm_harness.constitutive_joints_and_optics import series_state
from adm_harness.reaction_work_interfaces import (
    sheet_boundary_state, reflector_ports, capacitor_bank, capacitor_field_split,
    minimum_field_conversion, capacitor_energy_upper,
    periodic_capacitor_cell,
)
from adm_harness.scheduled_optical_transfer import ROTOR_RADIUS
from adm_harness.shared_rail_reactions import total_trace_bound

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "supporting_reports/data"
PARENTS = ("finite_reaction_transport", "constitutive_joints_and_optics", "scheduled_optical_transfer")
FIELD_BIAS_OVER_C = .62


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified(group, name):
    path = DATA / group / name
    digest = json.loads((DATA / group / "manifest.json").read_text())["output_sha256"][name]
    if sha256(path) != digest:
        raise ValueError(f"Parent evidence mismatch: {path}")
    return path


def history(task):
    name, output = task
    paths = [verified(g, name+"_states.npz") for g in PARENTS[1:]]
    with np.load(paths[0]) as j, np.load(paths[1]) as a:
        T = j["effective_material_tension"][[2, 5]]
        M = j["material_inventory"][[2, 5], None]
        m = j["joint_inventory_per_direction"][[2, 5], None]
        C, delta = a["capacity"], j["local_transit_delay"]
        A, Wmax, bias = total_trace_bound()*C, .05625*C, FIELD_BIAS_OVER_C*C
        increment = np.array([1., .5])[:, None, None]*(2*A+Wmax)/3
        minimum_load = T+np.array([1., .5])[:, None, None]*(bias-A)/3
        cap = capacitor_energy_upper(np.minimum(minimum_load[:, :-1], minimum_load[:, 1:]),
            np.maximum(minimum_load[:, :-1], minimum_load[:, 1:]), M, m, increment)
        demand = capacitor_field_split(cap[0], cap[1])
        fields = j["component_energy"][12:16].copy()
        fields[0] += 2*bias/3
        fields[1] += bias/3
        floor = np.minimum(fields[:, :-1], fields[:, 1:])
        fraction = minimum_field_conversion(floor, demand)
        # Individual field minima are conservative for every interpolated panel.
        maximum_fraction = float(fraction.max())
        if maximum_fraction > 1:
            raise ValueError(f"Available standing fields cannot host all work gaps: {name}, {maximum_fraction}")
        fixed_fraction = max(maximum_fraction, 0.)
        available = floor[:2]+fixed_fraction*np.stack((floor[2]+.5*floor[3], .5*floor[3]))
        field_margin = available-demand
        dt = np.diff(j["proper_time"], axis=0)
        # Optimistic c_s=1 and maximum permitted span. Shorter actual spans
        # increase the load-bearing reflector exposure.
        response_span = .1*ROTOR_RADIUS*delta
        exposure = np.cumsum(2*(T[:, :-1]+T[:, 1:]).sum(axis=0)*dt/response_span, axis=0)
        optimistic_allowance = a["remaining_reserve"][1:]
        mirror_ceiling = np.min(optimistic_allowance/exposure, axis=0)
        benchmark_over_allowance = .62e-6*exposure/optimistic_allowance
        # Keep the inherited combined energy-trace derivative<=1 ceiling;
        # two extra bias units bound field preparation plus added support.
        finite = np.load(verified("finite_reaction_transport", name+"_energy_screen.npz"))
        reserve = finite["minimum_reserve"]-2*(bias-A)
        finite.close()
        if reserve.min() <= 0:
            raise ValueError(f"Enlarged work-gap bias exhausts the panel energy screen: {name}")
        np.savez_compressed(Path(output)/(name+"_interfaces.npz"), x=j["x"],
            panel_capacitor_energy_upper=cap, panel_maxwell_demand_upper=demand,
            panel_required_conversion_fraction=fraction, panel_field_margin=field_margin,
            reflector_exposure_lower=exposure,
            optimistic_reflector_loss_fraction_ceiling=mirror_ceiling,
            causal_response_span=response_span, minimum_rail_reserve_after_bias=reserve)
    row = dict(label=name, input_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        maximum_required_common_photon_conversion_fraction=maximum_fraction,
        fixed_conversion_fraction=fixed_fraction,
        minimum_allocated_field_margin=float(field_margin.min()),
        maximum_capacitor_energy_upper=float(cap.sum(axis=0).max()),
        maximum_capacitor_energy_upper_over_C=float((cap.sum(axis=0)/C).max()),
        minimum_rail_reserve_after_bias=float(reserve.min()),
        isotropic_reaction_bias_over_C=FIELD_BIAS_OVER_C,
        most_restrictive_optimistic_reflector_loss_fraction=float(mirror_ceiling.min()),
        minimum_over_labels_peak_reflector_benchmark_over_allowance=float(benchmark_over_allowance.max(axis=0).min()),
        maximum_reflector_benchmark_over_allowance=float(benchmark_over_allowance.max()),
        causal_response_span_over_transfer_time=.1*ROTOR_RADIUS,
        support_boundary_signal_speed_assumed=1.,
        capacitor_energy_drawn_from_existing_field_populations=True,
        slow_positioning_stage_assumed=True)
    print(name, "field fraction", maximum_fraction, "mirror ceiling", mirror_ceiling.min(), flush=True)
    return row


def local(context, name):
    path = verified("finite_reaction_transport", name+"_states.npz")
    with np.load(path) as d:
        t, trace = d["time"], d["total_trace"]
        T, M, m = (np.array(context[k]) for k in ("tension", "core_inventory", "joint_inventory"))
        A, Wmax = total_trace_bound(), .05625
        weight = np.array([1., .5])
        minimum_tension = T+weight*(FIELD_BIAS_OVER_C-A)/3
        low = series_state(minimum_tension, M, m, dimension=2)
        high = series_state(minimum_tension+weight*(2*A+Wmax)/3, M, m, dimension=2)
        span_low = low["core_linear_stretch"]+1e-4*low["joint_stretch"]
        span_high = high["core_linear_stretch"]+1e-4*high["joint_stretch"]
        reference = .1*ROTOR_RADIUS/span_high
        baseline_length = reference*span_low
        baseline_gap = .55*reference*(span_high-span_low)
        old_tension = T[:, None]+weight[:, None]*(A+trace)/3
        old_state = series_state(old_tension, M[:, None], m[:, None], dimension=2)
        old_derivative = old_state["core_energy_derivative"]+old_state["joint_energy_derivative"]
        trace_rate = d["support_power"]/((old_derivative*weight[:, None]).sum(axis=0)/3)
        tension = T[:, None]+weight[:, None]*(FIELD_BIAS_OVER_C+trace)/3
        rate = weight[:, None]*trace_rate/3
        boundary = sheet_boundary_state(tension, M[:, None], m[:, None], rate, reference[:, None])
        mirrors = reflector_ports(boundary["force_per_facet"], boundary["facet_velocity"])
        caps = periodic_capacitor_cell(boundary, (baseline_length+2*baseline_gap)[:, None])
        assert np.max(abs(boundary["mechanical_power"]-boundary["material_energy_rate"])) < 1e-12
        combined = (boundary["material_energy"]+caps["field_energy"]).sum(axis=0)
        # Exact tensor substitution increases the complementary standing field
        # energy by precisely the energy the capacitors release.
        complement_change = caps["field_energy"][:, :1].sum()-caps["field_energy"].sum(axis=0)
        full_ensemble = combined+complement_change
        support_only = boundary["material_energy"].sum(axis=0)
        residual = (full_ensemble-full_ensemble[0])-(support_only-support_only[0])
        row = dict(name=name, parent_state_sha256=sha256(path),
            maximum_facet_speed=float(np.max(abs(boundary["facet_velocity"]))),
            minimum_gap_over_baseline_span=float(np.min(caps["gap"]/baseline_length[:, None])),
            maximum_gap_over_baseline_span=float(np.max(caps["gap"]/baseline_length[:, None])),
            peak_capacitor_energy=float(caps["field_energy"].sum(axis=0).max()),
            support_energy_range=float(np.ptp(support_only)),
            isolated_support_plus_capacitor_energy_range=float(np.ptp(combined)),
            complete_support_and_reallocated_field_energy_range=float(np.ptp(full_ensemble)),
            maximum_field_reallocation_energy_identity_error=float(np.max(abs(residual))),
            maximum_electrical_port_power=float(np.max(abs(caps["electrical_power"].sum(axis=0)))),
            maximum_support_mechanical_power=float(np.max(abs(boundary["mechanical_power"].sum(axis=0)))),
            maximum_work_change_from_parent_bias=float(np.max(abs(boundary["mechanical_power"].sum(axis=0)-d["support_power"]))),
            maximum_terminal_energy_identity_error=float(np.max(abs(caps["balance_error"]))),
            sampled_reflector_endpoint_exposure=float(np.trapezoid(mirrors["encountered_power"].sum(axis=0), t)))
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=DATA/"reaction_work_interfaces")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("positive worker count required")
    args.output.mkdir(parents=True, exist_ok=True)
    prior = json.loads(verified("finite_reaction_transport", "summary.json").read_text())
    for group in PARENTS:
        for name, digest in json.loads((DATA/group/"manifest.json").read_text())["runtime_sha256"].items():
            if sha256(ROOT/name) != digest:
                raise ValueError(f"Parent source changed: {name}")
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        histories = list(pool.map(history, [(h["label"], str(args.output)) for h in prior["histories"]]))
    trials = [local(c, c["name"]+"_"+d) for c in prior["contexts"] for d in ("up", "down")]
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__), histories=histories, trials=trials,
        local_trials_replay_prescribed_parent_trace=True, enlarged_bias_over_C=FIELD_BIAS_OVER_C,
        terminal_charge_work_and_field_energy_included=True, capacitor_maxwell_stress_included=True,
        complementary_standing_field_work_required=True,
        periodic_return_electrode_geometry_constructed=True,
        electrode_carrier_material_and_positioning_stage_constructed=False,
        finite_electromagnetic_leads_and_spatial_traction_constructed=False,
        capacitor_holding_loss_law_identified=False, physical_material_feasibility=False)
    (args.output/"summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(), ROOT/"toolkit/adm_harness_cli/adm_harness/reaction_work_interfaces.py",
             ROOT/"toolkit/adm_harness_cli/tests/test_reaction_work_interfaces.py"]
    for p in paths:
        shutil.copyfile(p, args.output/("execution_"+p.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        parent_manifest_sha256={str((DATA/g/"manifest.json").relative_to(ROOT)): sha256(DATA/g/"manifest.json") for g in PARENTS},
        output_sha256={p.name: sha256(p) for p in sorted(args.output.iterdir()) if p.is_file() and p.name != "manifest.json"})
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
