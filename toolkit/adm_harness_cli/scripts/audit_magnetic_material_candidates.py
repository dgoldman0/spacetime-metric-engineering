#!/usr/bin/env python3
"""Material screening of saved magnetic jackets; emits numerical evidence only.

The geometry, field, currents, and absorbed-heat histories remain fixed.
For sleeve energy density u, axial pressure z, and local hoop tension H,
the averaged sleeve tensor is (u, z, -H/2). The first two residual support
facets require z >= u + G, G = max(F0+H, F1-H/2). Materials satisfying
z + H <= u therefore require G + H <= 0, independently of inventory.
Positive values certify rejection of that particular constitutive class.
Negative values alone provide no certificate of feasibility or stability.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import multiprocessing

import numpy as np
from scipy.optimize import linprog

from adm_harness.magnetic_load_balance import attached_bank, support_cone


ROOT = Path(__file__).resolve().parents[3]
PARENT = ROOT / "supporting_reports/data/magnetic_geometry"
PREFIX = "shared_candidate_"
C_SI = 299792458.


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(values):
    return {"minimum": float(np.min(values)), "maximum": float(np.max(values))}


def audit(path):
    meta = json.loads(path.read_text())
    archive_path = path.with_name(meta["label"] + "_states.npz")
    state_path = ROOT / meta["input"]
    manifest = json.loads((PARENT / "manifest.json").read_text())
    expected = {
        path: manifest["output_sha256"][path.name],
        archive_path: manifest["output_sha256"][archive_path.name],
        state_path: manifest["input_sha256"][meta["input"]],
    }
    hashes = {str(p.relative_to(ROOT)): sha256(p) for p in expected}
    for p, digest in expected.items():
        if hashes[str(p.relative_to(ROOT))] != digest:
            raise ValueError(f"Parent hash mismatch: {p}")
    with np.load(archive_path) as archive:
        saved = {k: archive[k] for k in archive.files if k.startswith(PREFIX)
                 or k in ("t", "x", "evolved_cold_energy")}
    with np.load(state_path) as archive:
        state = {k: archive[k] for k in archive.files}
    for axis in ("t", "x"):
        np.testing.assert_array_equal(saved[axis], state[axis])
    field = {k: saved[PREFIX + "loop_" + k + "_field_energy"]
             for k in ("radial", "transverse")}
    loaded = attached_bank(state, saved["evolved_cold_energy"], field,
                           carrier_tensor=saved[PREFIX + "carrier_tensor"])
    wall = sum(saved[PREFIX + side + "_sleeve_tensor"]
               for side in ("inner", "outer"))
    H = sum(saved[PREFIX + side + "_hoop"] for side in ("inner", "outer"))
    residual = saved[PREFIX + "remaining_support_tensor"]
    reconstruction = float(np.max(np.abs(loaded["residual_target"] - wall - residual)))
    if reconstruction > 1e-12:
        raise ValueError("Saved wall and residual failed reconstruction")
    cone = support_cone(*residual, loaded["radial_field_floor"])
    if np.max(cone["shortfall"]) > 1e-12:
        raise ValueError("Saved unconstrained-strength witness fails support cone")

    D, F = state["D"], loaded["facets"]
    G = np.maximum(F[0] + H, F[1] - H/2)
    gap = D * (G + H)
    index = np.unravel_index(np.argmax(gap), gap.shape)
    # Independent component reconstruction at this sample. Variables are
    # (u, z, radial B, radial photons, angular photons, angular membrane, dust).
    # This uses the component tensors directly, without the eliminated facets.
    f0, f1, f2 = F[:, index[0], index[1]]
    h = float(H[index])
    rho, radial, angular = loaded["residual_target"][:, index[0], index[1]]
    floor = float(loaded["radial_field_floor"][index])
    lp = linprog(np.zeros(7),
        A_eq=[[1., 0., 1., 1., 1., 1., 1.],
              [0., 1., -1., 1., 0., 0., 0.],
              [0., 0., 1., 0., .5, -1., 0.]],
        b_eq=[rho, radial, angular+h/2],
        A_ub=[[-1., 1., 0., 0., 0., 0., 0.],
              [-1., -1., 0., 0., 0., 0., 0.]],
        b_ub=[-h, 0.],
        bounds=[(h, None), (None, None), (floor, None)] + [(0., None)]*4,
        method="highs")
    if gap[index] > 1e-12 and lp.status != 2:
        raise ValueError("Independent pointwise LP disagrees with rejection")
    case = next(row for row in meta["cases"]
                if row["inner_pressure"] == .1 and row["outer_pressure"] == 1.1
                and row["radius_ratio"] == 1.01)
    sides = {}
    for side in ("inner", "outer"):
        tensor = saved[PREFIX + side + "_sleeve_tensor"]
        hoop = saved[PREFIX + side + "_hoop"]
        if np.any(tensor[0] <= 0):
            raise ValueError("Positive sleeve energy required")
        sides[side] = {
            "axial_pressure_over_energy": bounds(tensor[1]/tensor[0]),
            "hoop_tension_over_energy": bounds(hoop/tensor[0]),
            "maximum_axial_plus_hoop_over_energy": float(np.max((tensor[1]+hoop)/tensor[0])),
        }
    return {
        "label": meta["label"], "time_samples": int(D.shape[0]),
        "spatial_samples": int(D.shape[1]), "input_sha256": hashes,
        "current_coefficient": meta["current_coefficient"],
        "minimum_stress_fraction": case["minimum_stress_fraction_counted_currents"],
        "closed_jacket_energy_only_lower_bound": meta["absolute_pointwise_strength_lower_bound"],
        "saved_witness_strength_fraction": case["witness"]["stress_fraction"],
        "saved_witness_boundaries": sides,
        "tensor_reconstruction_error": reconstruction,
        "saved_witness_maximum_support_shortfall": float(np.max(cone["shortfall"])),
        "additive_class_rejection": {
            "law": "axial_pressure + hoop_tension <= sleeve_energy_density",
            "integrated_gap": bounds(gap), "positive_gap_tolerance": 1e-12,
            "violating_samples": int(np.count_nonzero(gap > 1e-12)),
            "violating_labels": int(np.count_nonzero(np.any(gap > 1e-12, axis=0))),
            "worst_sample": {
                "time_index": int(index[0]), "position_index": int(index[1]),
                "time": float(saved["t"][index[0]]), "position": float(saved["x"][index[1]]),
                "integrated_gap": float(gap[index]),
                "original_facets": [float(f0), float(f1), float(f2)], "hoop": h,
                "residual_target": [float(rho), float(radial), float(angular)],
                "radial_field_floor": floor,
                "independent_lp_status": int(lp.status),
            },
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path,
        default=ROOT / "supporting_reports/data/magnetic_material_screen")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    if args.output.exists():
        parser.error("choose a fresh output directory")
    paths = sorted(PARENT.glob("*_summary.json"))
    if len(paths) != 4:
        raise ValueError("Expected both saved resolutions at both locations")
    with ProcessPoolExecutor(max_workers=args.workers,
            mp_context=multiprocessing.get_context("spawn")) as pool:
        results = list(pool.map(audit, paths))
    examples = {
        "graphene_intrinsic_sheet": 42./7.6e-7,
        "carbon_plate_nanolattice_2020": 3.75e6,
        "optimized_carbon_nanolattice_2025": 2.03e6,
        "continuous_carbon_fiber_lattice_2026": 782e3,
    }
    comparison = {name: {"specific_strength_J_per_kg": value,
                         "strength_over_rest_energy_density": value/C_SI**2}
                  for name, value in examples.items()}
    # Equation (84) of arXiv:2409.10602v1, rewritten in principal inverse
    # stretches. This is a pointwise algebraic example, without stability,
    # current, finite-temperature, or registered-history validation.
    eps, x, y = .8, 6., 1./6.
    density = .5*((1-eps)*(1+x*y)+eps*(x+y))
    axial = .5*((1-eps)*(x*y-1)+eps*(x-y))
    azimuthal = .5*((1-eps)*(x*y-1)-eps*(x-y))
    np.testing.assert_allclose([axial/density, azimuthal/density], [.875, -.875])
    runtime_paths = [Path(__file__).resolve(),
                    ROOT / "toolkit/adm_harness_cli/adm_harness/magnetic_load_balance.py",
                    PARENT / "manifest.json"]
    payload = {
        "created_utc": datetime.now(timezone.utc).isoformat(), "workers": args.workers,
        "scope": "Fixed saved common jacket; constitutive rejection and unit conversions",
        "runtime_sha256": {str(p.relative_to(ROOT)): sha256(p) for p in runtime_paths},
        "speed_of_light_m_per_s": C_SI,
        "literature_specific_strength_conversions": comparison,
        "rigid_membrane_algebraic_example": {
            "source": "https://arxiv.org/html/2409.10602v1#S3.SS1", "epsilon": eps,
            "inverse_axial_stretch_squared": x, "inverse_hoop_stretch_squared": y,
            "density_over_reference": density,
            "axial_pressure_over_density": axial/density,
            "hoop_pressure_over_density": azimuthal/density,
            "full_containment_pass": False,
        },
        "histories": results,
    }
    args.output.mkdir(parents=True)
    output = args.output / "summary.json"
    output.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    print(output.relative_to(ROOT) if output.is_relative_to(ROOT) else output)
    for row in results:
        rejected = row["additive_class_rejection"]
        print(f"{row['label']}: {rejected['violating_samples']} violating samples; "
              f"maximum integrated gap {rejected['integrated_gap']['maximum']:.9g}; "
              f"LP status {rejected['worst_sample']['independent_lp_status']}")


if __name__ == "__main__":
    main()
