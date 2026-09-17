#!/usr/bin/env python3
"""Verify C1 source artifacts, refinement, force checks and provenance."""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np

ROOT = Path(__file__).resolve().parents[3]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT/"supporting_reports/data/c1_module_pair")
    args = parser.parse_args()
    manifest_path = args.data/"manifest.json"
    manifest = json.loads(manifest_path.read_text())
    verified = 0
    for group in ("runtime_sha256", "input_sha256", "inherited_source_hashes", "output_sha256"):
        root = args.data if group == "output_sha256" else ROOT
        for name, expected in manifest[group].items():
            if digest(root/name) != expected:
                raise ValueError(f"Hash mismatch: {root/name}")
            verified += 1
    summary = json.loads((args.data/"summary.json").read_text())
    worst = dict(duality_gap=0., weighted_equilibrium=0., dual_stationarity=0.,
                 maxwell_partition=0., lorentz_partition=0., net_module_charge=0.)
    unresolved = []
    for row in summary["cases"]:
        with np.load(args.data/row["artifact"]) as d:
            for name in d.files:
                if not np.isfinite(d[name]).all():
                    raise ValueError(f"Nonfinite state: {row['artifact']} {name}")
            x, r, b = d["coordinate"], d["radius"], d["radial_scale"]
            np.testing.assert_allclose(d["module_flux"].sum(axis=-1), d["flux"], atol=1e-14)
            np.testing.assert_allclose(d["charge_density"], d["module_flux_x"]/(b*r*r)[:, None], atol=1e-14)
            e_error = float(abs(d["self_energy"].sum(axis=-1)+d["cross_energy"]-d["energy"]).max())
            f_error = float(abs(d["lorentz_force"].sum(axis=-1)-d["total_lorentz_force"]).max())
            worst["maxwell_partition"] = max(worst["maxwell_partition"], e_error)
            worst["lorentz_partition"] = max(worst["lorentz_partition"], f_error)
            np.testing.assert_allclose(d["module_flux"][[0, -1]], 0., atol=1e-14)
            for i, c in enumerate(row["components"]):
                if not c["success"]:
                    if c["solver_status"] == 4:
                        unresolved.append(dict(label=row["label"], component=i,
                            cells_per_coordinate_unit=row["cells_per_coordinate_unit"],
                            message=c["solver_message"]))
                    elif c["solver_status"] != 2:
                        raise ValueError(f"Numerically unresolved support LP: {row['label']}: {c}")
                    continue
                prefix = "connected_" if row["connected"] else f"module{i}_"
                for boundary in c["domain"]:
                    j = int(np.flatnonzero(x == boundary)[0])
                    for name in ("density", "radial_pressure", "angular_pressure"):
                        if abs(d[prefix+name][j]) > 1e-10:
                            raise ValueError("Finite material boundary is loaded")
                worst["duality_gap"] = max(worst["duality_gap"], c["duality_gap_relative"])
                worst["weighted_equilibrium"] = max(worst["weighted_equilibrium"], c["max_weighted_equilibrium_residual"])
                worst["dual_stationarity"] = max(worst["dual_stationarity"], c["max_dual_stationarity_residual"])
                worst["net_module_charge"] = max(worst["net_module_charge"], abs(c["net_charge"]))
                if c["minimum_dec_margin"] < -1e-9:
                    raise ValueError("Nodal material stress bound failed")
    if max(worst.values()) > 1e-7:
        raise ValueError(f"Numerical identity/provenance check failed: {worst}")
    label = summary["lowest_sampled_pair_support_energy_case"]
    lead = sorted((r for r in summary["cases"] if r["label"] == label and
        r["support_envelope"]["label"] == "bounded" and
        r["geometry_stride"] == 1 and r["quadrature_order"] == 8),
        key=lambda r: r["cells_per_coordinate_unit"])
    fine, previous = lead[-1], lead[-2]
    energy_change = abs(fine["support_proper_energy"]/previous["support_proper_energy"]-1.)
    if energy_change > 1e-3:
        raise ValueError("Leading finite-density comparison needs spatial refinement")
    force_error = max(c["independent_force_residual_relative_to_peak_load"] for c in fine["components"])
    density_excess = max(c["maximum_offgrid_density"]/c["density_ceiling"]-1. for c in fine["components"])
    gradient_excess = max(c["maximum_offgrid_density_or_angular_gradient"]/c["proper_gradient_limit"]-1.
                          for c in fine["components"])
    dec_error = max(0., -fine["minimum_reconstructed_offgrid_dec_margin"])
    if force_error > 1e-5 or density_excess > 1e-4 or gradient_excess > 1e-4 or dec_error > 1e-8:
        raise ValueError("Leading pair needs additional off-grid resolution")
    control = next(r for r in summary["cases"] if r["connected"] and
        r["support_envelope"]["label"] == "bounded" and
        r["cells_per_coordinate_unit"] == fine["cells_per_coordinate_unit"])
    np.testing.assert_allclose(fine["field_proper_energy"], control["field_proper_energy"], rtol=1e-12)
    np.testing.assert_allclose(fine["absolute_charge_inventory"], 2.*control["absolute_charge_inventory"], rtol=1e-12)
    broad_cases = sorted((r for r in summary["cases"] if r["label"] == "center1p5_width2" and
        r["support_envelope"]["label"] == "bounded" and r["geometry_stride"] == 1 and r["quadrature_order"] == 8),
        key=lambda r: r["cells_per_coordinate_unit"])
    broad, broad_previous = broad_cases[-1], broad_cases[-2]
    broad_change = abs(broad["support_proper_energy"]/broad_previous["support_proper_energy"]-1.)
    if (not broad["all_static_support_lps_solved"] or broad_change > 1e-3 or
            broad["independent_force_residual_relative_to_peak_load"] > 1e-5 or
            broad["minimum_reconstructed_offgrid_dec_margin"] < -1e-8 or
            any(c["maximum_offgrid_density"] > c["density_ceiling"]*(1.+1e-4) or
                c["maximum_offgrid_density_or_angular_gradient"] > c["proper_gradient_limit"]*(1.+1e-4)
                for c in broad["components"])):
        raise ValueError("Broad C1 bracket needs additional resolution")
    if not all(r["same_longitudinal_source_family_excluded"] for r in summary["inherited_longitudinal_source_gate"]):
        raise ValueError("Inherited source-family outcome changed")
    result = dict(verified_hashes=verified, cases=len(summary["cases"]),
        cases_with_all_static_support_lps_solved=sum(r["all_static_support_lps_solved"] for r in summary["cases"]),
        numerically_unresolved_support_lps=unresolved,
        worst_identity_errors=worst, leading_case=label,
        leading_cells_per_coordinate_unit=fine["cells_per_coordinate_unit"],
        last_refinement_support_energy_relative_change=energy_change,
        leading_independent_force_residual_relative_to_peak_load=force_error,
        leading_offgrid_density_relative_excess=max(density_excess, 0.),
        leading_offgrid_gradient_relative_excess=max(gradient_excess, 0.),
        leading_offgrid_dec_absolute_error=dec_error,
        broad_c1_case=broad["label"], broad_c1_support_energy=broad["support_proper_energy"],
        broad_c1_last_refinement_energy_relative_change=broad_change,
        broad_c1_overlap_fraction_of_shorter_module=broad["overlap_fraction_of_shorter_module"],
        pair_added_support_proper_energy=fine["support_proper_energy"]-control["support_proper_energy"],
        pair_support_energy_ratio=fine["support_proper_energy"]/control["support_proper_energy"],
        pair_total_field_and_support_energy_ratio=(fine["field_proper_energy"]+fine["support_proper_energy"])/
            (control["field_proper_energy"]+control["support_proper_energy"]),
        numerical_screen_verified=True, complete_physical_assembly_certified=False)
    output = args.data/"verification.json"
    output.write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    shutil_target = args.data/("execution_"+Path(__file__).name)
    shutil_target.write_bytes(Path(__file__).read_bytes())
    audit_manifest = dict(parent_manifest_sha256=digest(manifest_path),
        runtime_sha256={str(Path(__file__).resolve().relative_to(ROOT)): digest(Path(__file__))},
        output_sha256={p.name: digest(p) for p in (output, shutil_target)})
    (args.data/"verification_manifest.json").write_text(json.dumps(audit_manifest, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
