#!/usr/bin/env python3
"""Screen separate finite electrostatic modules on a common standing geometry.

Independent cases/resolutions run in four processes by default. Artifacts are
numerical evidence; the architectural report is maintained manually.
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
from numpy.polynomial.legendre import leggauss
import scipy

from adm_harness.c1_module_overlap import (
    StaticGeometry, angular_support_floor, electric_pair, static_support, support_tensor_at,
)
from adm_harness.geometry_opening import StaticSlice

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SPEC = ROOT/"toolkit/adm_harness_cli/specs/c1_module_pair.json"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_geometry(path, stride=1):
    with np.load(path) as d:
        chart = StaticSlice(*[d[k][::stride] for k in
                              ("coordinate", "radius", "lapse", "radial_scale")])

    def evaluate(x):
        r, a, b, rp, _, ap, _ = chart.jets(x)
        return r, a, b, rp, ap

    return chart, StaticGeometry(evaluate)


def run_case(task):
    spec, case, resolution, output, stride, order, envelope = task
    started = time.monotonic()
    chart, geometry = load_geometry(ROOT/spec["reference"], stride)
    extent = spec["field_extent_coordinate"]
    x = np.linspace(-extent, extent, int(2*extent*resolution)+1)
    amplitude = chart.throat_radius*np.sqrt(spec["throat_maxwell_tension_fraction"]/(4.*np.pi))
    reference_density = spec["throat_maxwell_tension_fraction"]/(8.*np.pi*chart.throat_radius**2)
    density_limit = (envelope["density_multiple"]*reference_density
                     if envelope["density_multiple"] is not None else None)
    gradient_limit = density_limit/envelope["proper_gradient_length"] if density_limit is not None else None

    def fields(xx):
        r, _, b, _, _ = geometry(xx)
        return electric_pair(xx, r, b, amplitude=amplitude, overlap=case["overlap"],
            plateau=spec["field_plateau_coordinate"], extent=extent)

    def load_for(index):
        def load(xx):
            d = fields(xx)
            if index is None:
                return d["total_lorentz_force"], d["total_charge_density"]
            return d["lorentz_force"][..., index], d["charge_density"][..., index]
        return load

    qnodes, qw = leggauss(16)
    dx = np.diff(x)
    xx = x[:-1, None]+dx[:, None]*(qnodes+1.)/2.
    ww = dx[:, None]*qw/2.
    r, a, b, rp, rpp, ap, app = chart.jets(xx)
    volume = 4.*np.pi*b*r*r
    field = fields(xx)
    demanded = np.stack((((1.-rp*rp)/(r*r)-2.*rpp/r)/(8.*np.pi),
        (-(1.-rp*rp)/(r*r)+2.*ap*rp/r)/(8.*np.pi),
        (app+ap*ap+ap*rp/r+rpp/r)/(8.*np.pi)), axis=-1)
    support = np.zeros_like(demanded)
    arrays = dict(coordinate=x, radius=geometry(x)[0], lapse=geometry(x)[1],
                  radial_scale=geometry(x)[2], **fields(x))
    components = []
    indices = [None] if case["connected"] else [0, 1]
    for index in indices:
        domain = (-extent, extent) if index is None else (
            (-extent, case["overlap"][1]) if index == 0 else (case["overlap"][0], extent))
        load = load_for(index)
        summary, state = static_support(x, geometry, load, domain=domain,
            mass_per_charge=spec["host_mass_per_charge"], quadrature_order=order,
            density_ceiling=density_limit, proper_gradient_limit=gradient_limit)
        f, charge = load(xx)
        local = angular_support_floor(f, ap, rp/r)
        active = abs(f) > max(float(abs(f).max())*1e-10, 1e-14)
        summary["angular_only_contact_failed_active_samples"] = int(np.sum(active & ~local["feasible"]))
        summary["angular_only_contact_active_samples"] = int(np.sum(active))
        summary["peak_lorentz_force"] = float(abs(f).max())
        summary["peak_charge_density"] = float(abs(charge).max())
        if state:
            tensor = support_tensor_at(xx, state, geometry, load)
            support += tensor
            # Differentiate the reconstructed pressure independently inside each cell.
            probes = x[:-1]+.413*dx
            h = np.minimum(.01*dx, 1e-4)
            plus = support_tensor_at(probes+h, state, geometry, load)[:, 1]
            minus = support_tensor_at(probes-h, state, geometry, load)[:, 1]
            mid = support_tensor_at(probes, state, geometry, load)
            rr, aa, bb, rrp, aap = geometry(probes)
            divergence = ((plus-minus)/(2.*h*bb)+aap*(mid[:, 0]+mid[:, 1])
                          +2.*rrp/rr*(mid[:, 1]-mid[:, 2]))
            force, _ = load(probes)
            summary["independent_force_residual_max"] = float(abs(divergence-force).max())
            summary["independent_force_residual_relative_to_peak_load"] = float(
                abs(divergence-force).max()/max(float(abs(force).max()), 1e-30))
            prefix = "connected_" if index is None else f"module{index}_"
            arrays.update({prefix+k: v for k, v in state.items() if k != "coordinate"})
        components.append(summary)
    all_solved = all(c["success"] for c in components)
    u = field["energy"]
    em = np.stack((u, -u, u), axis=-1)
    remainder = demanded-em-support
    ae, be = case["overlap"]
    # A separate high-order mesh resolves both the metric knots and interval ends.
    cuts = np.unique(np.r_[ae, chart.coordinate[(chart.coordinate > ae) & (chart.coordinate < be)], be])
    cuts_dx = np.diff(cuts)
    overlap_x = cuts[:-1, None]+cuts_dx[:, None]*(qnodes+1.)/2.
    overlap_w = cuts_dx[:, None]*qw/2.
    _, oa, ob, _, _ = geometry(overlap_x)
    lengths = [float(np.sum(ww*b*((xx >= c["domain"][0]) & (xx <= c["domain"][1]))))
               for c in components]
    overlap_length = float(np.sum(overlap_w*ob))
    cross_error = field["self_energy"].sum(axis=-1)+field["cross_energy"]-u
    force_error = field["lorentz_force"].sum(axis=-1)-field["total_lorentz_force"]
    row = dict(label=case["label"], connected=case["connected"], overlap=case["overlap"],
        support_envelope=envelope, density_ceiling=density_limit, proper_gradient_limit=gradient_limit,
        cells_per_coordinate_unit=resolution, geometry_stride=stride, quadrature_order=order,
        all_static_support_lps_solved=all_solved,
        field_amplitude=amplitude, field_proper_energy=float(np.sum(ww*volume*u)),
        cross_field_proper_energy=float(np.sum(ww*volume*field["cross_energy"])),
        individual_field_self_energy=float(np.sum(ww[..., None]*volume[..., None]*field["self_energy"])),
        maximum_maxwell_energy_partition_error=float(abs(cross_error).max()),
        maximum_lorentz_force_partition_error=float(abs(force_error).max()),
        module_proper_lengths=lengths, overlap_proper_length=overlap_length,
        overlap_fraction_of_shorter_module=overlap_length/min(lengths),
        overlap_static_light_time=float(np.sum(overlap_w*ob/oa)),
        components=components, elapsed_seconds=time.monotonic()-started)
    if all_solved:
        row.update(support_proper_energy=sum(c["proper_energy"] for c in components),
            supplied_proper_energy=float(np.sum(ww*volume*(u+support[..., 0]))),
            minimum_remaining_radial_null=float((remainder[..., 0]+remainder[..., 1]).min()),
            minimum_remaining_angular_null=float((remainder[..., 0]+remainder[..., 2]).min()),
            required_negative_radial_null_integral=float(np.sum(ww*volume*np.maximum(
                -remainder[..., 0]-remainder[..., 1], 0.))),
            required_negative_angular_null_integral=float(np.sum(ww*volume*np.maximum(
                -remainder[..., 0]-remainder[..., 2], 0.))),
            absolute_charge_inventory=sum(c["absolute_charge_inventory"] for c in components),
            max_density=sum(c["max_density"] for c in components),
            minimum_reconstructed_offgrid_dec_margin=min(c["minimum_reconstructed_offgrid_dec_margin"] for c in components),
            independent_force_residual_relative_to_peak_load=max(
                c["independent_force_residual_relative_to_peak_load"] for c in components))
    suffix = f"_{envelope['label']}_{resolution}_g{stride}_q{order}"
    path = Path(output)/(case["label"]+suffix+".npz")
    np.savez_compressed(path, **arrays)
    row["artifact"] = path.name
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/c1_module_pair")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("positive worker count required")
    spec = json.loads(args.spec.read_text())
    parent_path = ROOT/spec["parent_summary"]
    parent = json.loads(parent_path.read_text())
    reference = next(c for c in parent["candidates"] if c["label"] == "reference")
    if sha256(ROOT/spec["reference"]) != reference["cache_sha256"]:
        raise ValueError("reference metric hash differs from its archived source screen")
    for path, digest in parent["source_hashes"].items():
        if sha256(ROOT/path) != digest:
            raise ValueError(f"inherited implementation/input changed: {path}")
    if len({c["label"] for c in spec["cases"]}) != len(spec["cases"]):
        raise ValueError("distinct case labels required")
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    tasks = [(spec, c, n, str(args.output), 1, 8, envelope) for c in spec["cases"]
             for n in spec["cells_per_coordinate_unit"] for envelope in spec["support_envelopes"]]
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        for future in as_completed([pool.submit(run_case, task) for task in tasks]):
            row = future.result()
            rows.append(row)
            print(row["label"], row["support_envelope"]["label"], row["cells_per_coordinate_unit"],
                  row.get("support_proper_energy", "LP unresolved"), flush=True)
        fine_n = max(spec["cells_per_coordinate_unit"])
        fine = [r for r in rows if r["cells_per_coordinate_unit"] == fine_n and
                r["all_static_support_lps_solved"] and not r["connected"] and
                r["support_envelope"]["label"] == "bounded"]
        best = min(fine, key=lambda r: r["support_proper_energy"]) if fine else None
        if best:
            selected = next(c for c in spec["cases"] if c["label"] == best["label"])
            envelope = best["support_envelope"]
            control = next(c for c in spec["cases"] if c["connected"])
            sensitive = next(c for c in spec["cases"] if c["label"] == "center1p5_width0p5")
            broad = next(c for c in spec["cases"] if c["label"] == "center1p5_width2")
            checks = [(spec, selected, fine_n, str(args.output), 2, 8, envelope),
                      (spec, selected, fine_n, str(args.output), 1, 16, envelope),
                      (spec, selected, 2*fine_n, str(args.output), 1, 8, envelope),
                      (spec, control, 2*fine_n, str(args.output), 1, 8, envelope),
                      (spec, sensitive, 2*fine_n, str(args.output), 1, 8, envelope),
                      (spec, broad, 2*fine_n, str(args.output), 1, 8, envelope),
                      (spec, selected, fine_n, str(args.output), 1, 8,
                       dict(label="bounded_tight", density_multiple=2., proper_gradient_length=1.)),
                      (spec, selected, fine_n, str(args.output), 1, 8,
                       dict(label="bounded_broad", density_multiple=8., proper_gradient_length=1.))]
            for row in pool.map(run_case, checks):
                rows.append(row)
                print("Checked", row["label"], row["geometry_stride"], row["quadrature_order"], flush=True)
    rows.sort(key=lambda r: (r["label"], r["support_envelope"]["label"], r["cells_per_coordinate_unit"],
                             r["geometry_stride"], r["quadrature_order"]))
    chart, _ = load_geometry(ROOT/spec["reference"])
    inherited = []
    kappa = .01*parent["reference_r0"]**2
    for extent in (3., 5., 7.):
        balance = chart.quadrature(-extent, extent, kappa, order=16).balance(kappa)
        inherited.append(dict(coordinate_half_extent=extent, kappa=kappa,
            supply_over_required=balance["supply_over_required"],
            optimistic_50_percent_clock_box_ratio=9.*balance["supply_over_required"],
            same_longitudinal_source_family_excluded=bool(9.*balance["supply_over_required"] < 1.)))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(),
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        workers=args.workers, runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        elapsed_seconds=time.monotonic()-started, specification=spec, cases=rows,
        lowest_sampled_pair_support_energy_case=best["label"] if best else None,
        inherited_longitudinal_source_gate=inherited,
        physical_scope=dict(static_common_geometry=True, finite_neutral_maxwell_sources=True,
            maxwell_cross_stress_counted=True, separate_zero_end_traction_supports=True,
            support_constitutive_evolution_supplied=False, physical_charge_species_assigned=False,
            angular_packing_and_material_separation_constructed=False,
            quantum_opening_source_supplied=False, full_einstein_source_closed=False,
            actual_handoff_or_reset_evolved=False, module_recoil_or_rotation_evolved=False,
            c1_physical_feasibility_established=False))
    (args.output/"summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    columns = ("label", "support_envelope_label", "cells_per_coordinate_unit", "geometry_stride", "quadrature_order",
        "all_static_support_lps_solved", "support_proper_energy", "field_proper_energy",
        "cross_field_proper_energy", "absolute_charge_inventory", "overlap_proper_length",
        "overlap_fraction_of_shorter_module", "overlap_static_light_time", "required_negative_radial_null_integral",
        "required_negative_angular_null_integral", "minimum_reconstructed_offgrid_dec_margin",
        "independent_force_residual_relative_to_peak_load")
    with (args.output/"comparison.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows({key: row.get(key) if key != "support_envelope_label" else row["support_envelope"]["label"]
                          for key in columns} for row in rows)
    paths = [Path(__file__).resolve(), args.spec.resolve(),
        ROOT/"toolkit/adm_harness_cli/adm_harness/c1_module_overlap.py",
        ROOT/"toolkit/adm_harness_cli/tests/test_c1_module_overlap.py",
        ROOT/"toolkit/adm_harness_cli/adm_harness/geometry_opening.py"]
    for path in paths:
        shutil.copyfile(path, args.output/("execution_"+path.name))
    products = [args.output/row["artifact"] for row in rows]
    products += [args.output/name for name in ("summary.json", "comparison.csv")]
    products += [args.output/("execution_"+p.name) for p in paths]
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        input_sha256={str(p.relative_to(ROOT)): sha256(p) for p in (parent_path, ROOT/spec["reference"])},
        inherited_source_hashes=parent["source_hashes"],
        output_sha256={p.name: sha256(p) for p in sorted(products)})
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps(dict(cases=len(rows), best=payload["lowest_sampled_pair_support_energy_case"],
                         elapsed_seconds=payload["elapsed_seconds"]), indent=2), flush=True)


if __name__ == "__main__":
    main()
