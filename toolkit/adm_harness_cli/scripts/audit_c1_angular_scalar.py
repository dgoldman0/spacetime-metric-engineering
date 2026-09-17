#!/usr/bin/env python3
"""Independent scalar-variable finite-volume audit of the C1 angular spectra."""
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import argparse
import hashlib
import json
import multiprocessing
import shutil

import numpy as np
from scipy.linalg import eigh_tridiagonal

from adm_harness.c1_signed_channels import einstein_source
from adm_harness.geometry_opening import StaticSlice

ROOT = Path(__file__).resolve().parents[3]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def independent_eigenvalues(chart, domain, *, nodes, boundary, angular_index=0):
    """Discretize the original scalar phi, without u=R phi or optical V_j.

    K_phi = int [A R^2/B phi_x^2 + A B (j(j+1)+R^2 R4/6) phi^2] dx.
    M_phi = int B R^2/A phi^2 dx. The Ricci scalar is reconstructed from
    the Einstein trace. natural_u supplies the explicit Robin surface term.
    """
    x = np.linspace(*domain, nodes)
    h = np.diff(x)
    volume = np.r_[h[0]/2., (h[:-1]+h[1:])/2., h[-1]/2.]
    r, a, b, rp, *_ = chart.jets(x)
    rm, am, bm, *_ = chart.jets((x[:-1]+x[1:])/2.)
    t = einstein_source(chart, x)
    ricci = 8.*np.pi*(t[:, 0]-t[:, 1]-2.*t[:, 2])
    links = am*rm*rm/(bm*h)
    diagonal = np.r_[links[0], links[:-1]+links[1:], links[-1]]
    diagonal += volume*a*b*(angular_index*(angular_index+1.)+r*r*ricci/6.)
    mass = volume*b*r*r/a
    off = -links
    if boundary == "dirichlet":
        diagonal, mass, off = diagonal[1:-1], mass[1:-1], off[1:-1]
    elif boundary == "natural_u":
        # [A R R' phi^2] at the two ends, with R' a proper derivative.
        diagonal[0] -= a[0]*r[0]*rp[0]
        diagonal[-1] += a[-1]*r[-1]*rp[-1]
    else:
        raise ValueError("unknown boundary condition")
    return eigh_tridiagonal(diagonal/mass, off/np.sqrt(mass[:-1]*mass[1:]),
        select="i", select_range=(0, 2), eigvals_only=True, tol=1e-12, lapack_driver="stebz")


def audit_case(task):
    reference, case, nodes = task
    with np.load(ROOT/reference) as z:
        chart = StaticSlice(*[z[k] for k in ("coordinate", "radius", "lapse", "radial_scale")])
    values = independent_eigenvalues(chart, case["domain"], nodes=nodes,
        boundary=case["boundary"], angular_index=case["angular_index"])
    saved = np.asarray(case["eigenvalues"])
    return dict(id=case["id"], nodes=nodes, independent_eigenvalues=values.tolist(),
        maximum_relative_difference=float(np.max(abs(values-saved)/abs(values))))


def case_key(row):
    return (row["layout"], row["module"], row["compartment_count"], row["compartment"],
            tuple(row["domain"]), row["boundary"], row["angular_index"])


def analytic_controls():
    class ConformalCylinder:
        def __init__(self, deformation):
            self.deformation = deformation

        def jets(self, x):
            x = np.asarray(x)
            k = self.deformation
            omega = np.exp(k*x*x)
            return (2.*omega, omega, omega, 4.*k*x, 4.*k/omega,
                    2.*k*x/omega, 2.*k*(1.-2.*k*x*x)/omega**2)

    results = []
    for deformation in (0., .12):
        for boundary in ("dirichlet", "natural_u"):
            values = independent_eigenvalues(ConformalCylinder(deformation), (-1.5, 1.5),
                                            nodes=4097, boundary=boundary)
            n = np.arange(1, 4) if boundary == "dirichlet" else np.arange(3)
            expected = (n*np.pi/3.)**2+1./12.
            error = float(np.max(abs(values-expected)/expected))
            results.append(dict(conformal_deformation=deformation, boundary=boundary,
                                maximum_relative_error=error))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/c1_angular_scalar")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("positive worker count required")
    summary_path, manifest_path = args.output/"summary.json", args.output/"manifest.json"
    summary = json.loads(summary_path.read_text())
    if summary["specification"]["coupling"] != 1./6. or summary["specification"]["mass"] != 0.:
        raise ValueError("this independent audit is for the registered massless conformal scalar")
    manifest = json.loads(manifest_path.read_text())
    verified = 0
    for group, mapping in manifest.items():
        base = args.output if group == "output_sha256" else ROOT
        for name, expected in mapping.items():
            if digest(base/name) != expected:
                raise RuntimeError(f"hash mismatch: {name}")
            verified += 1
    records = summary["cases"]
    selected = [row for row in records if "artifact" in row]
    tasks = [(summary["specification"]["reference"], case, nodes)
             for case in selected for nodes in (4097, 8193)]
    with ProcessPoolExecutor(max_workers=args.workers,
            mp_context=multiprocessing.get_context("spawn")) as pool:
        independent = list(pool.map(audit_case, tasks))
    groups = {}
    for row in records:
        if row["control"] == "mesh":
            groups.setdefault(case_key(row), []).append(row)
    mesh = []
    for key, rows in groups.items():
        rows.sort(key=lambda row: row["nodes"])
        middle, fine = [np.asarray(row["eigenvalues"]) for row in rows[-2:]]
        mesh.append(dict(id=rows[-1]["id"], maximum_relative_change=float(
            np.max(abs(middle-fine)/abs(fine)))))
    metric = []
    for row in records:
        if row["control"] != "metric":
            continue
        base = groups[case_key(row)][-1]
        metric.append(dict(id=row["id"], maximum_relative_change=float(np.max(
            abs(np.asarray(row["eigenvalues"])-base["eigenvalues"])/np.asarray(base["eigenvalues"])))))
    eigenvectors = []
    for row in selected:
        with np.load(args.output/row["artifact"]) as z:
            assert np.array_equal(z["eigenvalues"], row["eigenvalues"])
            assert np.isfinite(z["modes"]).all()
            if row["boundary"] == "dirichlet":
                assert np.array_equal(z["modes"][[0, -1]], np.zeros((2, 3)))
            eigenvectors.append(row["id"])
    finest = [r for r in independent if r["nodes"] == 8193]
    maximum_independent = max(r["maximum_relative_difference"] for r in finest)
    maximum_mesh = max(r["maximum_relative_change"] for r in mesh)
    maximum_metric = max(r["maximum_relative_change"] for r in metric)
    positive = all(min(r["eigenvalues"]) > 0 for r in records)
    independent_positive = all(min(r["independent_eigenvalues"]) > 0 for r in independent)
    controls = analytic_controls()
    passed = (positive and independent_positive and maximum_independent < 1e-3
              and maximum_mesh < 1e-3 and maximum_metric < 1e-3
              and max(c["maximum_relative_error"] for c in controls) < 1e-5
              and summary["maximum_eigen_residual"] < 1e-7)
    verification = dict(verified_primary_hashes=verified, spectral_comparisons=len(records),
        independent_scalar_variable_comparisons=independent, mesh_refinement=mesh,
        metric_refinement=metric, checked_mode_artifacts=eigenvectors,
        maximum_independent_relative_difference=maximum_independent,
        maximum_mesh_relative_change=maximum_mesh, maximum_metric_relative_change=maximum_metric,
        all_sampled_squared_frequencies_positive=positive,
        all_independent_squared_frequencies_positive=independent_positive,
        independent_analytic_controls=controls,
        spectral_audit_passed=passed,
        exterior_state_certified=False, renormalized_stress_certified=False)
    (args.output/"verification.json").write_text(json.dumps(verification, indent=2, allow_nan=False)+"\n")
    snapshot = args.output/f"execution_{Path(__file__).name}"
    shutil.copyfile(Path(__file__), snapshot)
    audit_manifest = dict(runtime_sha256={str(Path(__file__).resolve().relative_to(ROOT)): digest(__file__)},
        input_sha256={p.name: digest(p) for p in (summary_path, manifest_path)},
        output_sha256={p.name: digest(p) for p in (args.output/"verification.json", snapshot)})
    (args.output/"audit_manifest.json").write_text(json.dumps(audit_manifest, indent=2)+"\n")
    print(json.dumps({k: v for k, v in verification.items()
        if not isinstance(v, list)}, indent=2))
    if not passed:
        raise SystemExit("spectral audit requires investigation")


if __name__ == "__main__":
    main()
