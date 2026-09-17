#!/usr/bin/env python3
"""Independently reconstruct signed-channel tensors, endpoints and exclusions."""
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path
import argparse
import hashlib
import json
import multiprocessing

import numpy as np

from adm_harness.c1_signed_channels import quadrature
from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.geometry_opening import StaticSlice
from adm_harness.metric_regularity import regularized_scalars
from adm_harness.source_ledger import SourceParams

ROOT = Path(__file__).resolve().parents[3]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def geometry(spec, stride):
    with np.load(ROOT/spec["reference"]) as z:
        return StaticSlice(*[z[k][::stride] for k in
            ("coordinate", "radius", "lapse", "radial_scale")])


def direct_tensor(chart, x, row, strengths):
    """Direct strip equation, independent of the production field kernel."""
    r, a, _, _, _, ap, app = chart.jets(x)
    result = np.zeros((len(x), 3))
    for partition, amplitudes in zip(row["partitions"], strengths):
        for j, amplitude in enumerate(amplitudes):
            ends, lengths = partition["coordinate"], partition["optical_lengths"]
            use = (x >= ends[j]) & (x < ends[j+1])
            flat = -np.pi/(24.*lengths[j]**2*a[use]**2)
            factor = amplitude/(4.*np.pi*r[use]**2)
            result[use, 0] += factor*(flat+(2.*app[use]+ap[use]**2)/(24.*np.pi))
            result[use, 1] += factor*(flat-ap[use]**2/(24.*np.pi))
    return result


def direct_projections(t):
    return np.column_stack((t[:, 0]+t[:, 1], t[:, 0]-t[:, 1],
                            t[:, 0]+t[:, 2], t[:, 0]-t[:, 2]))


def source_case(task):
    spec, row, directory = task
    chart = geometry(spec, row["geometry_stride"])
    n = row["compartments_per_module"]
    strength = spec["eta"]*spec["reference_central_charge"]
    failures_verified = 0
    for name in ("radial_only", "with_angular_target"):
        gate = row[name]
        if gate["sampled_bulk_inequalities_solved"]:
            continue
        if gate["solver_status"] != 2 or "direct_exclusion_witness" not in gate:
            raise ValueError("unsupplied numerical exclusion certificate")
        witness = gate["direct_exclusion_witness"]
        x = np.array([witness["coordinate"]])
        # Recompute every independent compartment. This also certifies a
        # uniform-module family because its basis columns are positive sums.
        values = []
        for module in range(2):
            for compartment in range(n):
                amplitudes = np.zeros((2, n))
                amplitudes[module, compartment] = strength
                values.append(float(direct_projections(direct_tensor(chart, x, row, amplitudes))[
                    0, witness["projection_index"]]))
        if min(values) < -1e-14 or witness["target_projection"] >= 0.:
            raise ValueError("pointwise separating projection failed")
        # The target value is independently checked against the saved common metric.
        r, _, b, rp, rpp, ap, app = chart.jets(x)
        t = np.column_stack((((1.-rp**2)/r**2-2.*rpp/r)/(8.*np.pi),
            (-(1.-rp**2)/r**2+2.*ap*rp/r)/(8.*np.pi),
            (app+ap**2+ap*rp/r+rpp/r)/(8.*np.pi)))
        parent = json.loads((ROOT/spec["parent_specification"]).read_text())
        z = np.clip((abs(x)-parent["field_plateau_coordinate"])/(
            parent["field_extent_coordinate"]-parent["field_plateau_coordinate"]), 0., 1.)
        flux = chart.throat_radius*np.sqrt(parent["throat_maxwell_tension_fraction"]/(4.*np.pi))*(
            1.-z**3*(10.-15.*z+6.*z*z))
        t -= (flux**2/(2.*r**4))[:, None]*np.array([1., -1., 1.])
        np.testing.assert_allclose(direct_projections(t)[0, witness["projection_index"]],
                                   witness["target_projection"], rtol=1e-10, atol=1e-12)
        failures_verified += 1
    result = dict(pointwise_exclusions_verified=failures_verified,
                  tensor_error=0., weak_ward_error=0., boundary_force_error=0.,
                  bulk_reconstruction_error=0., dual_gap=0.)
    if "artifact" not in row:
        return result
    strengths = spec["eta"]*np.asarray(row["central_charge_per_compartment"])
    with np.load(Path(directory)/row["artifact"]) as z:
        if any(not np.isfinite(z[key]).all() for key in z.files):
            raise ValueError("nonfinite retained source state")
        actual = direct_tensor(chart, z["coordinate"], row, strengths)
        result["tensor_error"] = float(abs(actual-z["quantum"]).max())
        angular = z["angular_weight"][:, None]*np.array([-2., 2., -2.])
        result["bulk_reconstruction_error"] = float(abs(actual+angular+z["material"]-z["target_after_maxwell"]).max())
        if np.min(direct_projections(z["material"])) < -1e-9:
            raise ValueError("saved sampled bulk inequality failed")
    gate = row["with_angular_target"]
    result["dual_gap"] = abs(gate["objective"]-gate["dual_objective"])/max(1., gate["objective"])
    # The weak Ward identity retains every quantum momentum jump. The test
    # function varies across the entire channel, including the actual ends.
    for module, (partition, amplitudes, saved) in enumerate(zip(
            row["partitions"], strengths, row["optimized_wall_forces"])):
        ends = np.asarray(partition["coordinate"])
        lengths = np.asarray(partition["optical_lengths"])
        rr, aa, _, _, _, aap, _ = chart.jets(ends)
        left, right = np.zeros(len(ends)), np.zeros(len(ends))
        left[1:] = amplitudes*(-np.pi/(24.*lengths**2*aa[1:]**2)-aap[1:]**2/(24.*np.pi))
        right[:-1] = amplitudes*(-np.pi/(24.*lengths**2*aa[:-1]**2)-aap[:-1]**2/(24.*np.pi))
        force = left-right
        result["boundary_force_error"] = max(result["boundary_force_error"],
            float(abs(force-np.asarray(saved["force_on_material"])).max()/max(1., abs(force).max())))
        x, w = quadrature(chart, ends[0], ends[-1], order=16, extra_cuts=ends)
        own = np.zeros_like(strengths)
        own[module] = amplitudes
        t = direct_tensor(chart, x, row, own)
        r, a, b, _, _, ap, _ = chart.jets(x)
        phi, dphi = 1.+.17*x+.031*x*x, .17+.062*x
        integrand = -a*r*r*t[:, 1]*dphi+b*ap*a*r*r*t[:, 0]*phi
        boundary_terms = aa*force*(1.+.17*ends+.031*ends*ends)/(4.*np.pi)
        residual = float(w @ integrand+boundary_terms.sum())
        scale = max(float(w @ abs(integrand)+sum(abs(boundary_terms))), 1e-30)
        result["weak_ward_error"] = max(result["weak_ward_error"], abs(residual)/scale)
    if (result["tensor_error"] > 1e-10 or result["bulk_reconstruction_error"] > 1e-10
            or result["boundary_force_error"] > 1e-10 or result["weak_ward_error"] > 1e-8
            or result["dual_gap"] > 1e-8 or gate["dual_stationarity_max"] > 1e-8):
        raise ValueError(f"source identity failed: {result}")
    return result


def independent_curvature(task):
    spec, x = task
    chart = geometry(spec, 1)
    params_path = ROOT/"supporting_reports/data/le_coupled_reset_source/manifest.json"
    controls_path = ROOT/"toolkit/adm_harness_cli/specs/archived_geometry_opening.json"
    base = json.loads(params_path.read_text())["params"]
    control = next(c for c in json.loads(controls_path.read_text()) if c["label"] == "reference")
    params = replace(SourceParams(**base), **control["overrides"])
    r, a, b, rp, rpp, ap, app = chart.jets(x)
    predicted = ((1.-rp*rp)/r**2-rpp/r-ap*rp/r)/(4.*np.pi)
    rows = []
    for step in (.0005, .00025, .000125):
        direct = evaluate_demand(.745, x, params, step, step, holding=True,
                                 scalar_evaluator=regularized_scalars)
        difference = direct["rho"]-direct["p_l"]
        rows.append(dict(coordinate=x, stencil_step=step, four_dimensional_rho_minus_pr=difference,
            relative_difference=abs(difference-predicted)/abs(predicted)))
    if rows[-1]["relative_difference"] > 1e-3 or rows[-1]["four_dimensional_rho_minus_pr"] >= 0.:
        raise ValueError("independent four-dimensional tensor witness failed")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT/"supporting_reports/data/c1_signed_channels")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("positive worker count required")
    manifest_path = args.data/"manifest.json"
    manifest = json.loads(manifest_path.read_text())
    verified = 0
    for group in ("runtime_sha256", "input_sha256", "output_sha256"):
        root = args.data if group == "output_sha256" else ROOT
        for name, expected in manifest[group].items():
            if digest(root/name) != expected:
                raise ValueError(f"hash mismatch: {root/name}")
            verified += 1
    summary = json.loads((args.data/"summary.json").read_text())
    spec, rows = summary["specification"], summary["cases"]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        checks = list(pool.map(source_case, [(spec, row, str(args.data)) for row in rows]))
        curvature = [r for group in pool.map(independent_curvature,
            [(spec, -2.5), (spec, 2.5)]) for r in group]
    fine = [r for r in rows if r["bulk_samples"] == max(spec["bulk_samples"])
        and r["geometry_stride"] == 1 and r["quadrature_order"] == 8 and "artifact" in r]
    controls = []
    for row in fine:
        compare = [r for r in rows if r["label"] == row["label"]
            and r["strength_pattern"] == row["strength_pattern"]
            and r["compartments_per_module"] == row["compartments_per_module"] and "artifact" in r]
        measures = dict(label=row["label"], pattern=row["strength_pattern"],
            maximum_inventory_control_relative_change=max(abs(r["summed_compartment_central_charge"]/
                row["summed_compartment_central_charge"]-1.) for r in compare),
            offgrid_violation_over_peak_geometric_stress=row["offgrid_violation_over_peak_geometric_stress"])
        if measures["maximum_inventory_control_relative_change"] > 1e-3 or measures["offgrid_violation_over_peak_geometric_stress"] > 1e-5:
            raise ValueError(f"bulk allocation needs refinement: {measures}")
        controls.append(measures)
    errors = {name: max(c[name] for c in checks) for name in
        ("tensor_error", "weak_ward_error", "boundary_force_error", "bulk_reconstruction_error", "dual_gap")}
    result = dict(verified_hashes=verified, verified_parent_hashes=summary["verified_parent_hashes"],
        cases=len(rows), pointwise_exclusions_verified=sum(c["pointwise_exclusions_verified"] for c in checks),
        radial_only_bulk_passes=sum(r["radial_only"]["sampled_bulk_inequalities_solved"] for r in rows),
        angular_target_bulk_passes=sum(r["with_angular_target"]["sampled_bulk_inequalities_solved"] for r in rows),
        maximum_identity_errors=errors, refinement_controls=controls,
        independent_curvature_witnesses=curvature, numerical_screen_verified=True,
        complete_physical_source_supplied=False,
        change_record=spec["change_record"])
    output = args.data/"verification.json"
    output.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    snapshot = args.data/("execution_"+Path(__file__).name)
    snapshot.write_bytes(Path(__file__).read_bytes())
    runtime = [Path(__file__).resolve(), *[ROOT/"toolkit/adm_harness_cli/adm_harness"/name for name in
        ("geometry_boundary.py", "metric_regularity.py", "source_ledger.py", "receiver_regularity.py")]]
    inputs = [ROOT/"supporting_reports/data/le_coupled_reset_source/manifest.json",
              ROOT/"toolkit/adm_harness_cli/specs/archived_geometry_opening.json"]
    audit_manifest = dict(parent_manifest_sha256=digest(manifest_path),
        runtime_sha256={str(p.relative_to(ROOT)): digest(p) for p in runtime},
        input_sha256={str(p.relative_to(ROOT)): digest(p) for p in inputs},
        output_sha256={p.name: digest(p) for p in (output, snapshot)})
    (args.data/"verification_manifest.json").write_text(json.dumps(audit_manifest, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
