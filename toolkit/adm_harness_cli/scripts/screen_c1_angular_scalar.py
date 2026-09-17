#!/usr/bin/env python3
"""Compute C1 angular-scalar spectra and applicability diagnostics; numerical output only."""
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
import sys
import time

import numpy as np
import scipy

from adm_harness.c1_angular_scalar import cylindrical_indicators, lowest_modes
from adm_harness.c1_signed_channels import (
    angular_target_completion, channel_tensor, optical_partitions, quadrature,
)
from adm_harness.geometry_opening import StaticSlice

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SPEC = ROOT/"toolkit/adm_harness_cli/specs/c1_angular_scalar.json"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_chart(spec, stride=1):
    with np.load(ROOT/spec["reference"]) as z:
        return StaticSlice(*[z[k][::stride] for k in ("coordinate", "radius", "lapse", "radial_scale")])


def verify_manifest(path):
    manifest = json.loads(path.read_text())
    count = 0
    for group, mapping in manifest.items():
        if not group.endswith("sha256"):
            continue
        base = path.parent if group == "output_sha256" else ROOT
        for name, expected in mapping.items():
            if digest(base/name) != expected:
                raise RuntimeError(f"parent hash mismatch: {name}")
            count += 1
    return count


def make_cases(spec, parent, chart):
    cases = []
    em_spec = json.loads((ROOT/parent["parent_specification"]).read_text())
    extent, inset = em_spec["field_extent_coordinate"], parent["material_domain_inset_coordinate"]
    for layout in parent["cases"]:
        broad = layout["label"]
        # These are precisely the inherited inset quantum module domains.
        domains = [(-extent+inset, layout["overlap"][1]-inset),
                   (layout["overlap"][0]+inset, extent-inset)]
        for module, domain in enumerate(domains):
            for count in spec["compartment_counts"]:
                ends, _ = optical_partitions(chart, domain, count, order=8)
                for compartment, limits in enumerate(zip(ends[:-1], ends[1:])):
                    base = dict(layout=broad, module=module, compartment_count=count,
                        compartment=compartment, domain=list(limits), boundary="dirichlet",
                        angular_index=0, geometry_stride=1)
                    for nodes in spec["mode_nodes"]:
                        cases.append(dict(base, nodes=nodes, control="mesh"))
                    if count == 1 or compartment in (0, count//2, count-1):
                        for stride in spec["geometry_strides"][1:]:
                            cases.append(dict(base, nodes=spec["mode_nodes"][-1],
                                              geometry_stride=stride, control="metric"))
                    if count == 1:
                        for j in spec["angular_indices"][1:]:
                            cases.append(dict(base, nodes=spec["mode_nodes"][-1],
                                              angular_index=j, control="angular"))
    for domain in spec["auxiliary_domains"]:
        for boundary in ("dirichlet", "natural_u"):
            for nodes in spec["whole_interval_nodes"]:
                cases.append(dict(layout="auxiliary", module=-1, compartment_count=0,
                    compartment=-1, domain=domain, boundary=boundary, angular_index=0,
                    geometry_stride=1, nodes=nodes, control="mesh"))
    for index, case in enumerate(cases):
        case["id"] = index
    return cases


def run_case(task):
    spec, case, output = task
    chart = load_chart(spec, case["geometry_stride"])
    result = lowest_modes(chart, case["domain"], modes=spec["modes_retained"],
        nodes=case["nodes"], order=spec["quadrature_order"],
        angular_index=case["angular_index"], mass=spec["mass"], coupling=spec["coupling"],
        boundary=case["boundary"])
    record = dict(case, eigenvalues=result["eigenvalues"].tolist(),
        relative_residual=result["relative_residual"].tolist(),
        mass_orthogonality_error=result["mass_orthogonality_error"],
        quadrature_potential_lower_bound=result["quadrature_potential_lower_bound"])
    # Keep mode shapes for whole modules, auxiliary cuts and representative
    # small compartments. Scalar records retain every other comparison.
    finest = case["nodes"] == (spec["whole_interval_nodes"][-1]
        if case["layout"] == "auxiliary" else spec["mode_nodes"][-1])
    selected = (case["layout"] == "auxiliary" or case["compartment_count"] == 1
        or (case["compartment_count"] == 32 and case["compartment"] in (0, 16, 31)))
    if finest and selected and case["control"] == "mesh":
        name = f"modes_{case['id']:04d}.npz"
        np.savez_compressed(Path(output)/name, coordinate=result["coordinate"],
                            modes=result["modes"], eigenvalues=result["eigenvalues"])
        record["artifact"] = name
    return record


def applicability(spec, parent, chart, output):
    """Weight local cylindrical diagnostics by the inherited angular duty.

    No cylindrical tensor is used to replace an actual source in this screen.
    The previous radial populations and target allocation are reconstructed.
    """
    summary_path = ROOT/spec["parent_summary"]
    previous = json.loads(summary_path.read_text())
    rows, inputs = [], [summary_path]
    for label in ("broad", "narrow"):
        old = next(row for row in previous["cases"] if row["label"] == label
            and row["compartments_per_module"] == 32
            and row["strength_pattern"] == "independent_per_compartment"
            and row["bulk_samples"] == 8193 and row["geometry_stride"] == 1
            and row["quadrature_order"] == 16)
        path = summary_path.parent/old["artifact"]
        inputs.append(path)
        with np.load(path) as z:
            stored_v = z["angular_weight"]
            recalculated_v, _ = angular_target_completion(z["target_after_maxwell"]-z["quantum"])
            reconstruction = float(abs(stored_v-recalculated_v).max())
        partitions = old["partitions"]
        walls = np.concatenate([p["coordinate"] for p in partitions])
        x, w = quadrature(chart, *parent["bulk_comparison_domain"], order=8, extra_cuts=walls)
        # Reconstruct the target inside each compartment from the inherited
        # radial law and populations; integrate across each jump separately.
        q = np.zeros((len(x), 3))
        for part, central in zip(partitions, old["central_charge_per_compartment"]):
            ends = np.asarray(part["coordinate"])
            index = np.clip(np.searchsorted(ends, x, side="right")-1, 0, len(central)-1)
            q += channel_tensor(chart, x, ends, part["optical_lengths"],
                strength=parent["eta"])*np.asarray(central)[index, None]
        # Maxwell source and Einstein target use the inherited implementations.
        from adm_harness.c1_module_overlap import electric_pair
        from adm_harness.c1_signed_channels import einstein_source
        em_spec = json.loads((ROOT/parent["parent_specification"]).read_text())
        r, _, b, *_ = chart.jets(x)
        em = electric_pair(x, r, b, amplitude=chart.throat_radius*np.sqrt(
            em_spec["throat_maxwell_tension_fraction"]/(4.*np.pi)), overlap=old["overlap"],
            plateau=em_spec["field_plateau_coordinate"], extent=em_spec["field_extent_coordinate"])["energy"]
        target = einstein_source(chart, x)-em[:, None]*np.array([1., -1., 1.])-q
        v, _ = angular_target_completion(target)
        _, indicator = cylindrical_indicators(chart, x)
        measure = w*4.*np.pi*b*r*r*2.*v
        energy = float(measure.sum())
        fractions = {str(cut): float(measure[indicator > cut].sum()/energy)
                     for cut in spec["cylindrical_indicator_thresholds"]}
        record = dict(layout=label, inherited_angular_energy_magnitude=energy,
            recorded_angular_energy_magnitude=-old["bulk_proper_energies"]["angular_target"],
            target_reconstruction_error=reconstruction,
            maximum_cylindrical_indicator=float(indicator.max()),
            angular_energy_fraction_above_indicator=fractions)
        rows.append(record)
        sx = np.unique(np.r_[np.linspace(-2.9, 2.9, 2049), -2.5, 0., 2.5])
        entries, largest = cylindrical_indicators(chart, sx)
        np.savez_compressed(output/f"cylindrical_indicators_{label}.npz", coordinate=sx,
                            components=entries, maximum=largest)
    witnesses = []
    for x in (-2.5, 0., 2.5):
        values, indicator = cylindrical_indicators(chart, np.array([x]))
        witnesses.append(dict(coordinate=x, components=values[0].tolist(), maximum=float(indicator[0])))
    return dict(layouts=rows, witnesses=witnesses), inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/c1_angular_scalar")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("positive worker count required")
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("use an empty output directory")
    spec = json.loads(args.spec.read_text())
    parent = json.loads((ROOT/spec["parent_specification"]).read_text())
    verified = verify_manifest(ROOT/spec["parent_manifest"])
    args.output.mkdir(parents=True, exist_ok=True)
    chart = load_chart(spec)
    cases = make_cases(spec, parent, chart)
    started = time.monotonic()
    records = []
    with ProcessPoolExecutor(max_workers=args.workers,
            mp_context=multiprocessing.get_context("spawn")) as pool:
        futures = [pool.submit(run_case, (spec, case, args.output)) for case in cases]
        for future in as_completed(futures):
            records.append(future.result())
            if len(records) % 100 == 0:
                print(f"Completed {len(records)}/{len(cases)} spectral comparisons", flush=True)
    records.sort(key=lambda row: row["id"])
    diagnostics, extra_inputs = applicability(spec, parent, chart, args.output)
    result = dict(created_utc=datetime.now(timezone.utc).isoformat(),
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv],
        specification=spec, verified_parent_hashes=verified, workers=args.workers,
        runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        elapsed_seconds=time.monotonic()-started, cases=records, cylindrical_applicability=diagnostics,
        minimum_eigenvalue=min(row["eigenvalues"][0] for row in records),
        maximum_eigen_residual=max(max(row["relative_residual"]) for row in records),
        absolute_angular_stress_supplied=False, boundary_material_stress_supplied=False,
        exterior_state_supplied=False)
    (args.output/"summary.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    columns = ["id", "layout", "module", "compartment_count", "compartment", "domain", "boundary",
               "angular_index", "geometry_stride", "nodes", "control", "lowest_squared_frequency"]
    with (args.output/"spectra.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in records:
            writer.writerow({key: row["eigenvalues"][0] if key == "lowest_squared_frequency"
                             else row[key] for key in columns})
    runtime = [Path(__file__).resolve(), args.spec.resolve(),
        ROOT/"toolkit/adm_harness_cli/adm_harness/c1_angular_scalar.py",
        ROOT/"toolkit/adm_harness_cli/tests/test_c1_angular_scalar.py",
        ROOT/"toolkit/adm_harness_cli/adm_harness/c1_signed_channels.py",
        ROOT/"toolkit/adm_harness_cli/adm_harness/c1_module_overlap.py",
        ROOT/"toolkit/adm_harness_cli/adm_harness/geometry_opening.py"]
    for path in runtime[:4]:
        shutil.copyfile(path, args.output/f"execution_{path.name}")
    inputs = [ROOT/spec[key] for key in ("reference", "parent_manifest", "parent_specification")]
    inputs += [ROOT/parent["parent_specification"], *extra_inputs]
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): digest(p) for p in runtime},
        input_sha256={str(p.relative_to(ROOT)): digest(p) for p in inputs},
        output_sha256={p.name: digest(p) for p in sorted(args.output.iterdir()) if p.is_file()})
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps({key: result[key] for key in
        ("elapsed_seconds", "minimum_eigenvalue", "maximum_eigen_residual")}, indent=2))


if __name__ == "__main__":
    main()
