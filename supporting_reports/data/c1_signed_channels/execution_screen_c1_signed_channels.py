#!/usr/bin/env python3
"""Screen finite reflecting quantum channels; write numerical evidence only.

The static metric, electric populations and C1 overlap brackets are inherited
unchanged. Independent source-placement and resolution cases run in processes.
The accompanying scientific report is written manually.
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import argparse
import csv
import hashlib
import json
import multiprocessing
import platform
import shutil
import subprocess
import time

import numpy as np
import scipy

from adm_harness.c1_module_overlap import electric_pair
from adm_harness.c1_signed_channels import (
    angular_target_completion, boundary_exchange, bulk_completion_gate,
    channel_tensor, dec_projections, einstein_source, optical_partitions,
    quadrature, trace_witness,
)
from adm_harness.geometry_opening import StaticSlice

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SPEC = ROOT/"toolkit/adm_harness_cli/specs/c1_signed_channels.json"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_chart(spec, stride=1):
    with np.load(ROOT/spec["reference"]) as z:
        return StaticSlice(*[z[k][::stride] for k in
            ("coordinate", "radius", "lapse", "radial_scale")])


def fields(chart, x, parent, overlap):
    r, _, b, *_ = chart.jets(x)
    result = electric_pair(x, r, b, amplitude=chart.throat_radius*np.sqrt(
        parent["throat_maxwell_tension_fraction"]/(4.*np.pi)), overlap=overlap,
        plateau=parent["field_plateau_coordinate"], extent=parent["field_extent_coordinate"])
    return result["energy"]


def make_basis(chart, x, partitions, strength, pattern):
    columns = []
    for ends, lengths in partitions:
        tensor = channel_tensor(chart, x, ends, lengths, strength=strength)
        if pattern == "uniform_per_module":
            columns.append(tensor[:, None, :])
        elif pattern == "independent_per_compartment":
            index = np.clip(np.searchsorted(ends, x, side="right")-1, 0, len(lengths)-1)
            columns.append(tensor[:, None, :]*np.eye(len(lengths))[index, :, None])
        else:
            raise ValueError("unknown channel strength pattern")
    return np.concatenate(columns, axis=1)


def per_compartment_coefficients(coefficients, count, pattern):
    return (np.repeat(coefficients, count).reshape(2, count)
            if pattern == "uniform_per_module" else np.asarray(coefficients).reshape(2, count))


def wall_forces(chart, partitions, strengths):
    result = []
    for (ends, lengths), amplitudes in zip(partitions, strengths):
        force = np.zeros(len(ends))
        for j, amplitude in enumerate(amplitudes):
            force[j:j+2] += boundary_exchange(chart, ends[j:j+2], lengths[j:j+1],
                                             strength=float(amplitude))["force_on_material"]
        result.append(dict(coordinate=ends.tolist(), force_on_material=force.tolist()))
    return result


def run_case(task):
    spec, parent, case, count, pattern, samples, stride, order, output = task
    started = time.monotonic()
    chart = load_chart(spec, stride)
    extent, inset = parent["field_extent_coordinate"], spec["material_domain_inset_coordinate"]
    overlap = case["overlap"]
    domains = [(-extent+inset, overlap[1]-inset), (overlap[0]+inset, extent-inset)]
    partitions = [optical_partitions(chart, domain, count, order=order) for domain in domains]
    lo, hi = spec["bulk_comparison_domain"]
    # Evaluate both limits near internal walls; no surface tensor is smeared.
    walls = np.concatenate([ends for ends, _ in partitions])
    near_walls = np.r_[walls-1e-9, walls+1e-9]
    x = np.unique(np.r_[np.linspace(lo, hi, samples), -2.5, 2.5,
                       near_walls[(near_walls >= lo) & (near_walls <= hi)]])
    strength = spec["eta"]*spec["reference_central_charge"]
    basis = make_basis(chart, x, partitions, strength, pattern)
    energy = fields(chart, x, parent, overlap)
    target = einstein_source(chart, x)-energy[:, None]*np.array([1., -1., 1.])
    weights = np.full(2, count) if pattern == "uniform_per_module" else np.ones(2*count)
    radial, _ = bulk_completion_gate(target, basis, inventory_weights=weights)
    angular, state = bulk_completion_gate(target, basis, grant_angular_target=True,
                                         inventory_weights=weights)
    for gate in (radial, angular):
        if "direct_exclusion_witness" in gate:
            gate["direct_exclusion_witness"]["coordinate"] = float(x[gate["direct_exclusion_witness"]["sample_index"]])
    row = dict(label=case["label"], overlap=overlap,
        trial_quantum_overlap=[domains[1][0], domains[0][1]], compartments_per_module=count,
        strength_pattern=pattern, bulk_samples=samples, geometry_stride=stride,
        quadrature_order=order, channel_domains=[list(d) for d in domains],
        partitions=[dict(coordinate=ends.tolist(), optical_lengths=lengths.tolist())
                    for ends, lengths in partitions], radial_only=radial,
        with_angular_target=angular,
        reference_strength_wall_forces=wall_forces(chart, partitions,
            np.full((2, count), strength)),
        maximum_partition_optical_spread=max(float(np.ptp(lengths)/np.mean(lengths))
                                             for _, lengths in partitions))
    if state:
        coefficients = np.asarray(angular["scaled_channel_strengths"])
        compartment = per_compartment_coefficients(coefficients, count, pattern)
        row["central_charge_per_compartment"] = (spec["reference_central_charge"]*compartment).tolist()
        row["summed_compartment_central_charge"] = float(spec["reference_central_charge"]*angular["objective"])
        row["optimized_wall_forces"] = wall_forces(chart, partitions, strength*compartment)
        row["maximum_absolute_wall_force"] = max(max(map(abs, item["force_on_material"]))
                                                 for item in row["optimized_wall_forces"])
        # Independent offset samples detect missed bulk stress minima.
        check_x = np.linspace(lo, hi, 2*samples)[:-1]+(hi-lo)/(2*(2*samples-1))
        check_basis = make_basis(chart, check_x, partitions, strength, pattern)
        check_energy = fields(chart, check_x, parent, overlap)
        check_target = einstein_source(chart, check_x)-check_energy[:, None]*np.array([1., -1., 1.])
        check_q = np.einsum("nmc,m->nc", check_basis, coefficients)
        _, check_m = angular_target_completion(check_target-check_q)
        offgrid_margin = float(dec_projections(check_m).min())
        row["offgrid_minimum_dec_margin"] = offgrid_margin
        row["offgrid_violation_over_peak_geometric_stress"] = max(0., -offgrid_margin)/float(abs(einstein_source(chart, check_x)).max())
        # Integrate the relaxed bulk allocation only over its declared interval.
        qx, qw = quadrature(chart, lo, hi, order=order, extra_cuts=walls)
        qbasis = make_basis(chart, qx, partitions, strength, pattern)
        qenergy = fields(chart, qx, parent, overlap)
        qtarget = einstein_source(chart, qx)-qenergy[:, None]*np.array([1., -1., 1.])
        quantum = np.einsum("nmc,m->nc", qbasis, coefficients)
        v, material = angular_target_completion(qtarget-quantum)
        r, a, b, *_ = chart.jets(qx)
        volume = 4.*np.pi*b*r*r
        row["bulk_proper_energies"] = dict(radial_quantum=float(qw @ (volume*quantum[:, 0])),
            angular_target=float(qw @ (-2.*volume*v)), ordinary_target=float(qw @ (volume*material[:, 0])),
            maxwell=float(qw @ (volume*qenergy)), geometric=float(qw @ (volume*einstein_source(chart, qx)[:, 0])))
        row["maximum_ordinary_target_density"] = float(material[:, 0].max())
        row["maximum_angular_target_weight"] = float(v.max())
        row["bulk_radial_opening"] = float(qw @ (-4.*np.pi*r*b/a*(quantum[:, 0]+quantum[:, 1])))
        artifact = f"{case['label']}_{pattern}_n{count}_s{samples}_g{stride}_q{order}.npz"
        np.savez_compressed(Path(output)/artifact, coordinate=x, target_after_maxwell=target,
                            **state, coefficients=coefficients)
        row["artifact"] = artifact
    row["elapsed_seconds"] = time.monotonic()-started
    return row


def geometry_requirements(spec, parent):
    chart = load_chart(spec)
    witnesses = []
    for value in (-2.5, 2.5):
        x = np.array([value])
        em = fields(chart, x, parent, spec["cases"][0]["overlap"])
        values = trace_witness(chart, x, em)
        witnesses.append(dict(coordinate=value, **{key: np.asarray(val).tolist()[0]
                                                   for key, val in values.items()}))
    scan_x = np.linspace(-3., 3., 8193)
    scan = trace_witness(chart, scan_x, fields(chart, scan_x, parent, spec["cases"][0]["overlap"]))
    mask = scan["excludes_radial_conformal_plus_dec"]
    changes = np.diff(np.r_[False, mask, False].astype(int))
    bands = [dict(first_sample=float(scan_x[start]), last_sample=float(scan_x[end-1]),
                  minimum_after_maxwell_rho_minus_pr=float(scan["after_maxwell_rho_minus_pr"][start:end].min()))
             for start, end in zip(np.flatnonzero(changes == 1), np.flatnonzero(changes == -1))]
    regions = []
    for lo, hi in ((-8., -3.), (-3., 3.), (3., 8.)):
        x, w = quadrature(chart, lo, hi, order=16)
        r, a, b, *_ = chart.jets(x)
        t = einstein_source(chart, x)
        measure = 4.*np.pi*r*r*b
        regions.append(dict(domain=[lo, hi], negative_density=float(w @ (measure*np.maximum(-t[:, 0], 0.))),
            negative_radial_null=float(w @ (measure*np.maximum(-t[:, 0]-t[:, 1], 0.))),
            negative_angular_null=float(w @ (measure*np.maximum(-t[:, 0]-t[:, 2], 0.))),
            radial_opening=float(w @ (-4.*np.pi*r*b/a*(t[:, 0]+t[:, 1])))))
    return dict(radial_conformal_trace_witnesses=witnesses, sampled_trace_exclusion_bands=bands,
                source_coverage_regions=regions,
                exterior_source_assumed_zero_for_compact_channel_trial=True,
                physical_field_support_may_extend_beyond_material=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/c1_signed_channels")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("positive worker count required")
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("use an empty output directory for reproducible evidence")
    spec = json.loads(args.spec.read_text())
    parent = json.loads((ROOT/spec["parent_specification"]).read_text())
    manifest_path = ROOT/spec["parent_manifest"]
    parent_manifest = json.loads(manifest_path.read_text())
    parent_verified = 0
    for group in ("runtime_sha256", "input_sha256", "inherited_source_hashes", "output_sha256"):
        root = manifest_path.parent if group == "output_sha256" else ROOT
        for name, expected in parent_manifest[group].items():
            if digest(root/name) != expected:
                raise ValueError(f"parent evidence changed: {root/name}")
            parent_verified += 1
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    tasks = [(spec, parent, case, n, pattern, samples, 1, 8, str(args.output))
        for case in spec["cases"] for n in spec["compartments_per_module"]
        for pattern in spec["channel_strength_patterns"] for samples in spec["bulk_samples"]]
    # Independent metric and Gaussian controls for the most finely segmented cases.
    tasks += [(spec, parent, case, max(spec["compartments_per_module"]), pattern,
               max(spec["bulk_samples"]), stride, order, str(args.output))
        for case in spec["cases"] for pattern in spec["channel_strength_patterns"]
        for stride, order in ((2, 8), (1, 16))]
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        for future in as_completed([pool.submit(run_case, task) for task in tasks]):
            row = future.result()
            rows.append(row)
            print(row["label"], row["compartments_per_module"], row["strength_pattern"], row["bulk_samples"],
                  "bulk+angular", row["with_angular_target"]["solver_status"], flush=True)
    rows.sort(key=lambda r: (r["label"], r["strength_pattern"], r["compartments_per_module"],
                            r["bulk_samples"], r["geometry_stride"], r["quadrature_order"]))
    summary = dict(created_utc=datetime.now(timezone.utc).isoformat(),
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        specification=spec, verified_parent_hashes=parent_verified,
        workers=args.workers, runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        elapsed_seconds=time.monotonic()-started, cases=rows,
        geometry_requirements=geometry_requirements(spec, parent),
        physical_scope=dict(actual_finite_reflector_material_supplied=False,
            full_four_dimensional_quantum_tensor_supplied=False,
            angular_quantum_source_supplied=False, complete_einstein_source_closed=False,
            geometry_altered=False, existing_electric_source_placement_altered=False,
            existing_electric_overlap_brackets_altered=False,
            trial_quantum_overlap_differs_from_electric_overlap=True, trial_quantum_partitions_added=True,
            promoted_quantum_layout=None))
    (args.output/"summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n")
    columns = ["label", "compartments_per_module", "strength_pattern", "bulk_samples", "geometry_stride",
        "quadrature_order", "radial_only_status", "angular_relaxation_status", "summed_compartment_central_charge",
        "maximum_absolute_wall_force", "maximum_ordinary_target_density", "offgrid_minimum_dec_margin"]
    with (args.output/"comparison.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            record = {k: row.get(k) for k in columns}
            record.update(radial_only_status=row["radial_only"]["solver_status"],
                          angular_relaxation_status=row["with_angular_target"]["solver_status"])
            writer.writerow(record)
    runtime = [Path(__file__).resolve(), args.spec.resolve(),
        ROOT/"toolkit/adm_harness_cli/adm_harness/c1_signed_channels.py",
        ROOT/"toolkit/adm_harness_cli/adm_harness/c1_module_overlap.py",
        ROOT/"toolkit/adm_harness_cli/adm_harness/geometry_opening.py",
        ROOT/"toolkit/adm_harness_cli/tests/test_c1_signed_channels.py"]
    for path in runtime:
        shutil.copyfile(path, args.output/("execution_"+path.name))
    products = [args.output/name for name in ("summary.json", "comparison.csv")]
    products += [args.output/row["artifact"] for row in rows if "artifact" in row]
    products += [args.output/("execution_"+path.name) for path in runtime]
    inputs = [manifest_path, ROOT/spec["reference"], ROOT/spec["parent_specification"]]
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): digest(p) for p in runtime},
        input_sha256={str(p.relative_to(ROOT)): digest(p) for p in inputs},
        output_sha256={p.name: digest(p) for p in sorted(products)})
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps(dict(cases=len(rows), seconds=summary["elapsed_seconds"],
        radial_only_bulk_passes=sum(r["radial_only"]["sampled_bulk_inequalities_solved"] for r in rows),
        angular_relaxation_bulk_passes=sum(r["with_angular_target"]["sampled_bulk_inequalities_solved"] for r in rows)), indent=2))


if __name__ == "__main__":
    main()
