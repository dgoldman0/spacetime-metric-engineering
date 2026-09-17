#!/usr/bin/env python3
"""Compute normalized C1 angular boundary differences and source-budget controls."""
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import multiprocessing
import platform
import shutil
import subprocess
import sys
import time

import numpy as np
import scipy
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq

from adm_harness.c1_angular_response import AngularResponse, cylinder_interaction, integrate_response
from adm_harness.c1_angular_scalar import cylinder_tensor, cylindrical_indicators
from adm_harness.c1_module_overlap import electric_pair
from adm_harness.c1_signed_channels import channel_tensor, dec_projections, einstein_source
from adm_harness.geometry_opening import StaticSlice

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SPEC = ROOT/"toolkit/adm_harness_cli/specs/c1_angular_response.json"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_chart(spec, stride=1):
    with np.load(ROOT/spec["reference"]) as z:
        return StaticSlice(*[z[k][::stride] for k in ("coordinate", "radius", "lapse", "radial_scale")])


def verify_manifest(path):
    count = 0
    for group, mapping in json.loads(path.read_text()).items():
        if group.endswith("sha256"):
            base = path.parent if group == "output_sha256" else ROOT
            for name, expected in mapping.items():
                if digest(base/name) != expected:
                    raise RuntimeError(f"parent hash mismatch: {name}")
                count += 1
    return count


def retained_rows(spec):
    previous = json.loads((ROOT/spec["parent_summary"]).read_text())
    return {label: next(row for row in previous["cases"] if row["label"] == label
        and row["compartments_per_module"] == 32
        and row["strength_pattern"] == "independent_per_compartment"
        and row["bulk_samples"] == 8193 and row["geometry_stride"] == 1
        and row["quadrature_order"] == 16) for label in ("broad", "narrow")}


def remainder(chart, x, row, parent):
    """Exact inherited component laws at these probes, with populations fixed."""
    x = np.asarray(x, float)
    quantum = np.zeros((len(x), 3))
    for part, central in zip(row["partitions"], row["central_charge_per_compartment"]):
        ends = np.array(part["coordinate"])
        index = np.clip(np.searchsorted(ends, x, side="right")-1, 0, len(central)-1)
        quantum += channel_tensor(chart, x, ends, part["optical_lengths"],
            strength=parent["eta"])*np.asarray(central)[index, None]
    em_spec = json.loads((ROOT/parent["parent_specification"]).read_text())
    r, _, b, *_ = chart.jets(x)
    em = electric_pair(x, r, b, amplitude=chart.throat_radius*np.sqrt(
        em_spec["throat_maxwell_tension_fraction"]/(4*np.pi)), overlap=row["overlap"],
        plateau=em_spec["field_plateau_coordinate"], extent=em_spec["field_extent_coordinate"])["energy"]
    return einstein_source(chart, x)-em[:, None]*np.array([1., -1., 1.])-quantum


def make_cases(spec, rows, chart):
    optical = CubicSpline(chart.coordinate, chart.radial_scale/chart.lapse).antiderivative()
    angular = CubicSpline(chart.coordinate, chart.radial_scale/chart.radius).antiderivative()
    sources = [("broad_left", rows["broad"], 0), ("narrow_left", rows["narrow"], 0),
               ("shared_right", rows["broad"], 1)]
    cases = []
    for name, row, module in sources:
        fine_ends = np.array(row["partitions"][module]["coordinate"])
        lo, hi = fine_ends[[0, -1]]
        probes = [("outer_left", lo), ("outer_right", hi), ("overlap", .75)]
        if lo < 0 < hi:
            probes.append(("throat", 0.))
        target = -2.5 if module == 0 else 2.5
        i = np.searchsorted(fine_ends, target)-1
        mid = (optical(fine_ends[i])+optical(fine_ends[i+1]))/2
        center = brentq(lambda x: optical(x)-mid, fine_ends[i], fine_ends[i+1])
        probes.append(("transition_cell_center", center))
        for count in spec["angular_compartment_counts"]:
            ends = fine_ends[::32//count]
            for probe_name, x in probes:
                # Dirichlet isolation means the nearest added walls supply the
                # complete response at this probe, including original endpoints.
                i = int(np.clip(np.searchsorted(ends, x, side="right")-1, 0, count-1))
                walls = ends[i:i+2]
                walls = walls[(walls > lo) & (walls < hi)]
                angle_distance = float(np.min(abs(angular(walls)-angular(x))))
                optical_distance = float(np.min(abs(optical(walls)-optical(x))))
                angular_max = max(spec["minimum_angular_max"],
                    int(np.ceil(spec["angular_attenuation_cut"]/angle_distance)))
                base = dict(source=name, module=module, compartment_count=count,
                    domain=[lo, hi], compartment_domain=ends[i:i+2].tolist(),
                    walls=walls.tolist(), probe_name=probe_name, coordinate=float(x),
                    angular_max=angular_max, frequency_scale=1/optical_distance,
                    minimum_angular_distance=angle_distance,
                    minimum_optical_distance=optical_distance)
                for resolution in spec["resolutions"]:
                    selected = dict(resolution)
                    if probe_name == "throat":
                        selected["nodes"] = spec["throat_nodes"][selected["name"]]
                    cases.append(dict(base, **selected, geometry_stride=1))
                # Separate frequency and metric controls at representative
                # normalization and force witnesses, independent of mesh changes.
                if count == 32 and probe_name in ("throat", "outer_right"):
                    fine = spec["resolutions"][-1]
                    if probe_name == "throat":
                        fine = dict(fine, nodes=spec["throat_nodes"]["fine"])
                    cases.append(dict(base, **dict(fine, name="frequency_control",
                        frequency_nodes=160), geometry_stride=1))
                    cases.append(dict(base, **dict(fine, name="metric_control"), geometry_stride=2))
    for i, case in enumerate(cases):
        case["id"] = i
    return cases


def run_case(task):
    spec, case, eta, output = task
    chart = load_chart(spec, case["geometry_stride"])
    x = case["coordinate"]
    # Interior five-point samples provide a Ward identity check at fixed
    # frequency-integrated state. End force uses its one-sided derivative.
    if case["probe_name"].startswith("outer_"):
        probes = np.array([x])
    else:
        step = min(5e-4, min(abs(np.array(case["walls"])-x))/100)
        probes = x+step*np.arange(-2, 3)
    problem = AngularResponse(chart, case["domain"], case["walls"], probes, case["nodes"])
    value = integrate_response(problem, angular_max=case["angular_max"],
        frequency_nodes=case["frequency_nodes"], frequency_scale=case["frequency_scale"], eta=eta)
    index = len(probes)//2
    tensor = value["tensor"][index]
    tail = value["harmonic_tensor"][3*len(value["harmonic_tensor"])//4:, index].sum(axis=0)
    record = dict(case, tensor_per_real_field=tensor.tolist(),
        dec_projections_per_real_field=dec_projections(tensor).tolist(),
        trace_difference=float(-tensor[0]+tensor[1]+2*tensor[2]),
        angular_tail_last_quarter_relative=float(abs(tail).max()/max(abs(tensor).max(), 1e-100)))
    if len(probes) == 1:
        area = 4*np.pi*float(chart.jets(np.array([x]))[0][0])**2
        orientation = -1 if case["probe_name"] == "outer_left" else 1
        record["force_increment_per_real_field"] = float(orientation*area*tensor[1])
    else:
        r, _, b, rp, _, ap, _ = chart.jets(np.array([x]))
        v = value["tensor"][:, 1]
        derivative = (v[0]-8*v[1]+8*v[3]-v[4])/(12*step*b[0])
        ward = derivative+ap[0]*(tensor[0]+tensor[1])+2*rp[0]/r[0]*(tensor[1]-tensor[2])
        record["ward_residual_times_radius_over_tensor"] = float(abs(ward)*r[0]/max(abs(tensor).max(), 1e-100))
    name = f"response_{case['id']:03d}.npz"
    np.savez_compressed(Path(output)/name, coordinate=probes, tensor=value["tensor"],
                        harmonic_tensor=value["harmonic_tensor"])
    record["artifact"] = name
    return record


def benchmark(spec, parent, rows, chart):
    x = np.array([0.])
    r = float(chart.jets(x)[0][0])
    result = []
    for label, row in rows.items():
        target = remainder(chart, x, row, parent)[0]
        for logarithm in spec["cylinder_reference_logs"]:
            tensor = cylinder_tensor(r, r, logarithm, strength=parent["eta"])
            t, s = dec_projections(target), dec_projections(tensor)
            lower = max(0., max((a/b for a, b in zip(t, s) if b < 0), default=0.))
            upper = min((a/b for a, b in zip(t, s) if b > 0), default=np.inf)
            feasible = upper >= lower and all(a >= 0 for a, b in zip(t, s) if b == 0)
            result.append(dict(layout=label, reference_log=logarithm,
                one_field_tensor=tensor.tolist(), retained_remainder=target.tolist(),
                local_cylinder_minimum_integer_fields=int(np.ceil(lower)) if feasible else None,
                applicability_indicator=float(cylindrical_indicators(chart, x)[1][0])))
    interactions = [dict(length_over_radius=ratio,
        **cylinder_interaction(r, ratio*r, eta=parent["eta"]))
        for ratio in spec["cylinder_length_over_radius"]]
    return dict(throat_radius=r, normalization_comparisons=result,
                finite_cylinder_interactions=interactions)


def combined_budget(records, benchmarks, rows, chart, parent):
    fine = [r for r in records if r["name"] == "fine"]
    result = []
    for label, row in rows.items():
        n = next(r["local_cylinder_minimum_integer_fields"] for r in benchmarks["normalization_comparisons"]
                 if r["layout"] == label and r["reference_log"] == 1.)
        for count in (8, 32):
            selected = [r for r in fine if r["source"] in (label+"_left", "shared_right")
                        and r["compartment_count"] == count]
            overlap = sum((np.array(r["tensor_per_real_field"]) for r in selected
                           if r["probe_name"] == "overlap"), np.zeros(3))
            target = remainder(chart, np.array([.75]), row, parent)[0]
            forces = []
            for r in selected:
                if "force_increment_per_real_field" in r:
                    i = 0 if r["probe_name"] == "outer_left" else -1
                    previous = row["optimized_wall_forces"][r["module"]]["force_on_material"][i]
                    delta = n*r["force_increment_per_real_field"]
                    forces.append(dict(source=r["source"], end=r["probe_name"],
                        coordinate=r["coordinate"], retained_radial_force=previous,
                        angular_force_increment_per_real_field=r["force_increment_per_real_field"],
                        angular_increment_at_benchmark_multiplicity=delta,
                        radial_plus_angular_increment_at_benchmark_multiplicity=previous+delta))
            result.append(dict(layout=label, compartment_count=count,
                illustrative_multiplicity_from_cylinder=n,
                pair_overlap_tensor_increment_per_real_field_per_module=overlap.tolist(),
                retained_overlap_remainder=target.tolist(),
                overlap_remainder_after_increment_at_benchmark_multiplicity=(target-n*overlap).tolist(),
                forces=forces,
                missing_terms=["absolute one-compartment angular vacuum", "new reflector self/material stress",
                               "physical exterior and transition source", "complete support and recoil law"]))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/c1_angular_response")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.workers < 1 or (args.output.exists() and any(args.output.iterdir())):
        parser.error("positive workers and an empty output directory required")
    spec = json.loads(args.spec.read_text())
    parent = json.loads((ROOT/spec["parent_specification"]).read_text())
    verified = verify_manifest(ROOT/spec["parent_manifest"])
    args.output.mkdir(parents=True, exist_ok=True)
    rows, chart = retained_rows(spec), load_chart(spec)
    cases, records = make_cases(spec, rows, chart), []
    started = time.monotonic()
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        futures = [pool.submit(run_case, (spec, case, parent["eta"], args.output)) for case in cases]
        for future in as_completed(futures):
            records.append(future.result())
            if len(records) % 5 == 0:
                print(f"Completed {len(records)}/{len(cases)} angular-response comparisons", flush=True)
    records.sort(key=lambda r: r["id"])
    benchmarks = benchmark(spec, parent, rows, chart)
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(),
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], specification=spec, verified_parent_hashes=verified,
        workers=args.workers, runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        elapsed_seconds=time.monotonic()-started, eta=parent["eta"], cases=records, benchmarks=benchmarks,
        combined_budget=combined_budget(records, benchmarks, rows, chart, parent))
    (args.output/"summary.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    runtime = [Path(__file__).resolve(), args.spec.resolve(),
        ROOT/"toolkit/adm_harness_cli/adm_harness/c1_angular_response.py",
        ROOT/"toolkit/adm_harness_cli/tests/test_c1_angular_response.py",
        *[ROOT/f"toolkit/adm_harness_cli/adm_harness/{name}.py" for name in
          ("c1_angular_scalar", "c1_signed_channels", "c1_module_overlap", "geometry_opening")]]
    for path in runtime[:4]:
        shutil.copyfile(path, args.output/f"execution_{path.name}")
    inputs = [ROOT/spec[k] for k in ("reference", "parent_summary", "parent_manifest", "parent_specification")]
    inputs.append(ROOT/parent["parent_specification"])
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): digest(p) for p in runtime},
        input_sha256={str(p.relative_to(ROOT)): digest(p) for p in inputs},
        output_sha256={p.name: digest(p) for p in sorted(args.output.iterdir()) if p.is_file()})
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(f"Recorded {len(records)} comparisons in {time.monotonic()-started:.1f} seconds", flush=True)


if __name__ == "__main__":
    main()
