#!/usr/bin/env python3
"""Audit angular response with an independent u=R phi consistent-mass operator."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import argparse
import hashlib
import json
import shutil
import multiprocessing

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.linalg import solveh_banded

from adm_harness.c1_angular_response import AngularResponse, improved_tensor, integrate_response
from adm_harness.c1_angular_scalar import mode_potential
from screen_c1_angular_response import ROOT, load_chart, verify_manifest


def optical_moments(problem, frequency, j):
    """Original scalar moments from the independently discretized u operator."""
    x, chart = problem.x, problem.chart
    h = np.diff(x)
    t, w = leggauss(6)
    t, w = (t+1)/2, w/2
    gx = x[:-1, None]+h[:, None]*t
    _, a, b, *_ = chart.jets(gx)
    derivative = np.sum(w*a/b, axis=1)/h
    potential = b/a*(frequency**2+mode_potential(chart, gx, angular_index=j))
    elements = [np.sum(h[:, None]*w*potential*f, axis=1)
                for f in ((1-t)**2, t*(1-t), t*t)]
    elements[0] += derivative
    elements[1] -= derivative
    elements[2] += derivative
    diagonal = elements[2][:-1]+elements[0][1:]
    band = np.zeros((2, len(diagonal)))
    band[0], band[1, :-1] = diagonal, elements[1][1:-1]
    rhs = np.zeros((len(diagonal), len(problem.walls)))
    rhs[problem.wall_nodes-1, np.arange(len(problem.walls))] = 1.
    u = np.pad(solveh_banded(band, rhs, lower=True, check_finite=False), ((1, 1), (0, 0)))
    r, _, _, rp, *_ = chart.jets(problem.probes)
    rw = chart.jets(problem.walls)[0]
    values = u[problem.probe_nodes]/(r[:, None]*rw[None, :])
    ul = np.einsum('pk,pkm->pm', problem.derivative_weights, u[problem.derivative_nodes])
    derivatives = (ul-rp[:, None]/r[:, None]*u[problem.probe_nodes])/(r[:, None]*rw[None, :])
    wall_green = u[problem.wall_nodes]/(rw[:, None]*rw[None, :])
    matrix = (wall_green+wall_green.T)/2
    vi, di = np.linalg.solve(matrix, values.T).T, np.linalg.solve(matrix, derivatives.T).T
    return (-np.sum(values*vi, axis=1), -2*np.sum(derivatives*vi, axis=1),
            -np.sum(derivatives*di, axis=1))


def relative(a, b):
    a, b = np.array(a), np.array(b)
    return float(abs(a-b).max()/max(abs(b).max(), 1e-100))


def conservation_control(task):
    spec, eta, row, nodes, output = task
    chart, x = load_chart(spec), row["coordinate"]
    # Sample a resolved interval away from new walls. A derivative of stresses
    # at tightly clustered anchored nodes amplifies spatial truncation error.
    step = min(.01, min(abs(np.array(row["walls"])-x))/12)
    probes = x+step*np.arange(-2, 3)
    problem = AngularResponse(chart, row["domain"], row["walls"], probes, nodes)
    value = integrate_response(problem, angular_max=row["angular_max"],
        frequency_nodes=80, frequency_scale=row["frequency_scale"], eta=eta)
    t, pr = value["tensor"][2], value["tensor"][:, 1]
    r, _, b, rp, _, ap, _ = chart.jets(np.array([x]))
    derivative = (pr[0]-8*pr[1]+8*pr[3]-pr[4])/(12*step*b[0])
    ward = derivative+ap[0]*(t[0]+t[1])+2*rp[0]/r[0]*(t[1]-t[2])
    name = f"ward_{row['id']:03d}_{nodes}.npz"
    np.savez_compressed(Path(output)/name, coordinate=probes, tensor=value["tensor"])
    return dict(fine_id=row["id"], nodes=nodes, coordinate_step=step,
        ward_residual_times_radius_over_tensor=float(abs(ward)*r[0]/max(abs(t).max(), 1e-100)),
        tensor_change_from_production=relative(t, row["tensor_per_real_field"]),
        artifact=name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT/"supporting_reports/data/c1_angular_response")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("positive workers required")
    verified = verify_manifest(args.data/"manifest.json")
    summary = json.loads((args.data/"summary.json").read_text())
    rows, spec = summary["cases"], summary["specification"]
    comparisons = []
    independent = []
    chart = load_chart(spec)
    keys = ("source", "compartment_count", "probe_name")
    for fine in (r for r in rows if r["name"] == "fine"):
        related = [r for r in rows if all(r[k] == fine[k] for k in keys) and r["name"] != "fine"]
        comparisons += [dict(id=r["id"], fine_id=fine["id"], control=r["name"],
            relative_tensor_change=relative(r["tensor_per_real_field"], fine["tensor_per_real_field"])) for r in related]
        problem = AngularResponse(chart, fine["domain"], fine["walls"],
                                  np.array([fine["coordinate"]]), 16385)
        for frequency, j in ((0., 0), (fine["frequency_scale"], 0),
                              (fine["frequency_scale"], max(1, fine["angular_max"]//16))):
            actual = improved_tensor(chart, problem.probes, frequency, j,
                                     *optical_moments(problem, frequency, j))
            expected = problem.tensor(frequency, j)
            independent.append(dict(fine_id=fine["id"], frequency=frequency, angular_index=j,
                relative_tensor_difference=relative(actual, expected)))
    jobs = []
    for row in (r for r in rows if r["name"] == "fine" and "force_increment_per_real_field" not in r):
        sizes = (32769, 65537) if row["probe_name"] == "throat" else (16385, 32769)
        jobs.extend((spec, summary["eta"], row, n, str(args.data)) for n in sizes)
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        conservation = list(pool.map(conservation_control, jobs))
    best = [max((r for r in conservation if r["fine_id"] == i), key=lambda r: r["nodes"])
            for i in sorted(set(r["fine_id"] for r in conservation))]
    result = dict(verified_production_hashes=verified, comparisons=comparisons,
        independent_u_operator_comparisons=independent,
        conservation_controls=conservation, workers=args.workers,
        maximum_independent_tensor_difference=max(r["relative_tensor_difference"] for r in independent),
        maximum_base_to_fine_change=max(r["relative_tensor_change"] for r in comparisons if r["control"] == "base"),
        maximum_frequency_control_change=max(r["relative_tensor_change"] for r in comparisons if r["control"] == "frequency_control"),
        maximum_metric_control_change=max(r["relative_tensor_change"] for r in comparisons if r["control"] == "metric_control"),
        maximum_fine_angular_tail=max(r["angular_tail_last_quarter_relative"] for r in rows if r["name"] == "fine"),
        maximum_clustered_probe_ward_residual=max(r.get("ward_residual_times_radius_over_tensor", 0) for r in rows if r["name"] == "fine"),
        maximum_refined_conservation_residual=max(r["ward_residual_times_radius_over_tensor"] for r in best),
        maximum_refined_conservation_tensor_change=max(r["tensor_change_from_production"] for r in best))
    (args.data/"audit.json").write_text(json.dumps(result, indent=2)+"\n")
    script = Path(__file__).resolve()
    shutil.copyfile(script, args.data/f"execution_{script.name}")
    paths = [args.data/"audit.json", args.data/f"execution_{script.name}",
             *[args.data/r["artifact"] for r in conservation]]
    parent_path = (args.data/"manifest.json").resolve()
    parent_name = str(parent_path.relative_to(ROOT)) if parent_path.is_relative_to(ROOT) else str(parent_path)
    manifest = dict(runtime_sha256={str(script.relative_to(ROOT)): hashlib.sha256(script.read_bytes()).hexdigest()},
        input_sha256={parent_name: hashlib.sha256(parent_path.read_bytes()).hexdigest()},
        output_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    (args.data/"audit_manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps({k: v for k, v in result.items() if k.startswith("maximum")}, indent=2))


if __name__ == "__main__":
    main()
