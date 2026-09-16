#!/usr/bin/env python3
"""Compute scalar-wall branches and screen the fixed magnetic histories.

Independent coupling and history calculations use a process pool. Outputs
are numerical evidence, source snapshots and a manifest; the accompanying
research report is authored separately.
"""
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import argparse
import csv
import hashlib
import json
import multiprocessing
import platform
import shutil

import numpy as np
import scipy
from scipy.linalg import eigh_tridiagonal

from adm_harness.current_carrying_wall import (
    WallParameters, component_feasibility, necessary_wall_gaps,
    profile_observables, solve_profile,
)
from adm_harness.magnetic_geometry import jacket_requirements
from adm_harness.magnetic_load_balance import attached_bank, support_cone


ROOT = Path(__file__).resolve().parents[3]
PARENT = ROOT / "supporting_reports/data/magnetic_geometry"
PREFIX = "shared_candidate_"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extrema(array):
    return dict(minimum=float(np.min(array)), maximum=float(np.max(array)))


def branch_diagnostics(rows, *, timelike):
    rows.sort(key=lambda row: row["w"])
    w = np.array([row["w"] for row in rows])
    I = np.array([row["condensate_integral"] for row in rows])
    derivative = np.gradient(I, w, edge_order=2)
    factor = 1+2*w*derivative/I
    speed = 1/factor if timelike else factor
    action = np.array([row["energy"]+min(row["w"], 0.)*row["condensate_integral"]
                       for row in rows])
    # Variational envelope identity, using centered finite differences.
    error = np.gradient(action, w, edge_order=2)-I/2
    for i, row in enumerate(rows):
        row.update(current_mode_speed_squared=float(speed[i]),
                   axial_transverse_speed_squared=-row["axial_pressure"]/row["energy"],
                   hoop_transverse_speed_squared=-row["hoop_pressure"]/row["energy"],
                   envelope_derivative_error=float(error[i]))
    return rows


def run_branch(task):
    _, f, refined = task
    params = WallParameters(coupling=f, mass_squared=2*f-.6)
    extent = max(40., 14/np.sqrt(.7*params.mass_squared)) * (1.5 if refined else 1.)
    tolerance = 2.5e-10 if refined else 1e-8
    nodes = 601 if refined else 401
    integration_nodes = 16385 if refined else 8193
    count = 161 if refined else 81
    negative_count = 61 if refined else 31
    # For timelike profiles the stationary functional uses V+w*sigma^2/2.
    # Keep a margin from the loss of its nonnegative-vacuum condition.
    stationary_vacuum_window = (np.sqrt(params.wall_quartic*params.carrier_quartic/2)
                               * params.vacuum**2
                               - (2*f*params.vacuum**2-params.mass_squared))
    timelike_minimum = -min(.3*params.mass_squared, .75*stationary_vacuum_window)
    zero = solve_profile(params, 0., extent=extent, tolerance=tolerance, initial_nodes=nodes)
    first = profile_observables(zero, params, 0., integration_nodes=integration_nodes)
    branches = {}
    for name, grid in (
        ("spacelike", np.linspace(0, .95*params.linear_quench_w, count)),
        ("timelike", np.linspace(0, timelike_minimum, negative_count))):
        rows, previous = [dict(first)], zero
        for w in grid[1:]:
            previous = solve_profile(params, w, previous=previous, extent=extent,
                                     tolerance=tolerance, initial_nodes=nodes)
            row = profile_observables(previous, params, w, integration_nodes=integration_nodes)
            if row["center_condensate"] < 1e-5:
                raise ValueError("Continuation left the populated branch")
            rows.append(row)
        branches[name] = branch_diagnostics(rows, timelike=name == "timelike")
    # Independent finite-difference eigenvalue of the bare-kink carrier operator.
    eigenvalues = []
    for intervals in (2000, 4000):
        axis = np.linspace(-extent, extent, intervals+1)
        step = axis[1]-axis[0]
        V = (params.mass_squared
             - 2*f*params.vacuum**2/np.cosh(params.inverse_width*axis[1:-1])**2)
        value = eigh_tridiagonal(2/step**2+V, np.full(intervals-2, -1/step**2),
                                select="i", select_range=(0, 0), eigvals_only=True)[0]
        eigenvalues.append(dict(intervals=intervals, value=float(value),
                                error=float(value+params.linear_quench_w)))
    positive = branches["spacelike"]
    peak = max(positive, key=lambda row: row["current_magnitude"])
    stable = [row for row in positive if 0 <= row["current_mode_speed_squared"] <= 1
              and 0 <= row["hoop_transverse_speed_squared"] <= 1]
    sign_change = next(i for i, row in enumerate(positive)
                       if row["current_mode_speed_squared"] < 0)
    all_rows = positive + branches["timelike"]
    label = f"f{f:.2f}" + ("_refined" if refined else "")
    return dict(kind="branch", label=label, parameters=asdict(params), extent=extent,
                tolerance=tolerance, integration_nodes=integration_nodes,
                timelike_minimum_w=timelike_minimum,
                stationary_vacuum_window=stationary_vacuum_window,
                linear_quench_w=params.linear_quench_w, bare_tension=params.bare_tension,
                bare_carrier_eigenvalue_checks=eigenvalues,
                peak_sample=peak, current_mode_zero_bracket=[positive[sign_change-1]["w"],
                                                           positive[sign_change]["w"]],
                sampled_stable_hoop_tension_over_energy=extrema(
                    [row["hoop_transverse_speed_squared"] for row in stable]),
                maximum_normal_pressure_error=max(row["max_normal_pressure"] for row in all_rows),
                maximum_bvp_residual=max(row["max_bvp_residual"] for row in all_rows),
                branches=branches)


def run_history(task):
    _, name = task
    path = PARENT / name
    meta = json.loads(path.read_text())
    archive_path = path.with_name(meta["label"]+"_states.npz")
    state_path = ROOT / meta["input"]
    manifest = json.loads((PARENT / "manifest.json").read_text())
    expected = {path: manifest["output_sha256"][path.name],
                archive_path: manifest["output_sha256"][archive_path.name],
                state_path: manifest["input_sha256"][meta["input"]]}
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
    field = {k: saved[PREFIX+"loop_"+k+"_field_energy"] for k in ("radial", "transverse")}
    old = attached_bank(state, saved["evolved_cold_energy"], field,
                        carrier_tensor=saved[PREFIX+"carrier_tensor"])
    old_wall = sum(saved[PREFIX+side+"_sleeve_tensor"] for side in ("inner", "outer"))
    residual = saved[PREFIX+"remaining_support_tensor"]
    error = float(np.max(np.abs(old["residual_target"]-old_wall-residual)))
    if error > 1e-12 or np.max(support_cone(*residual, old["radial_field_floor"])["shortfall"]) > 1e-12:
        raise ValueError("Parent tensor reconstruction failed")
    # Native carriers replace the old particle model. Grant every bend and
    # return current zero additional cost, and remove its old hoop reaction.
    loaded = attached_bank(state, saved["evolved_cold_energy"], field, carrier_tensor=None)
    case = next(c for c in meta["cases"] if c["inner_pressure"] == .1
                and c["outer_pressure"] == 1.1 and c["radius_ratio"] == 1.01)
    H = jacket_requirements(saved["evolved_cold_energy"], state["D"],
        aspect=meta["geometry"]["aspect"], inner_pressure=case["inner_pressure"],
        outer_pressure=case["outer_pressure"], radius_ratio=case["radius_ratio"])["total_hoop"]
    D = state["D"]
    gaps = necessary_wall_gaps(loaded["facets"], H)
    results = {}
    for law, gap in gaps.items():
        integrated = D*gap
        idx = np.unravel_index(np.argmax(integrated), D.shape)
        scale = float(D[idx])
        target = loaded["residual_target"][:, idx[0], idx[1]]*scale
        floor, hoop = float(loaded["radial_field_floor"][idx]*scale), float(H[idx]*scale)
        lp = component_feasibility(target, floor, hoop, law=law)
        control = component_feasibility(target, floor, hoop, law="free_axial_stress")
        if integrated[idx] > 1e-12 and lp.status != 2:
            raise ValueError("Independent component LP disagrees with rejection")
        if not control.success:
            raise ValueError("Free-axial-stress positive control failed")
        results[law] = dict(integrated_gap=extrema(integrated),
            violating_samples=int(np.count_nonzero(integrated > 1e-12)),
            violating_labels=int(np.count_nonzero(np.any(integrated > 1e-12, axis=0))),
            worst_sample=dict(time_index=int(idx[0]), position_index=int(idx[1]),
                time=float(saved["t"][idx[0]]), position=float(saved["x"][idx[1]]),
                integrated_target=target.tolist(), integrated_field_floor=floor,
                integrated_hoop=hoop, integrated_gap=float(integrated[idx]),
                independent_lp_status=int(lp.status), free_axial_control_status=int(control.status),
                free_axial_control_components=control.x.tolist()))
    return dict(kind="history", label=meta["label"], input_sha256=hashes,
                time_samples=D.shape[0], spatial_samples=D.shape[1],
                parent_reconstruction_error=error,
                released_old_carrier_energy=extrema(D*saved[PREFIX+"carrier_tensor"][0]),
                tests=results)


def dispatch(task):
    return run_branch(task) if task[0] == "branch" else run_history(task)


def convergence_comparison(branches):
    coarse, fine = [next(b for b in branches if b["label"] == label)
                    for label in ("f0.40", "f0.40_refined")]
    result = {}
    for name in ("spacelike", "timelike"):
        a, b = coarse["branches"][name], fine["branches"][name][::2]
        np.testing.assert_allclose([row["w"] for row in a], [row["w"] for row in b], atol=1e-14)
        result[name] = {key: max(abs(x[key]-y[key]) for x, y in zip(a, b))
            for key in ("energy", "hoop_pressure", "current_magnitude", "center_condensate",
                        "current_mode_speed_squared")}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "supporting_reports/data/current_carrying_wall")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    if args.output.exists():
        parser.error("choose a fresh output directory")
    histories = sorted(PARENT.glob("*_summary.json"))
    if len(histories) != 4:
        raise ValueError("Expected two resolutions at each location")
    tasks = [("branch", f, False) for f in (.35, .4, .45, .5)]
    tasks += [("branch", .4, True)] + [("history", p.name) for p in histories]
    results = []
    with ProcessPoolExecutor(max_workers=args.workers,
                             mp_context=multiprocessing.get_context("spawn")) as pool:
        for row in pool.map(dispatch, tasks):
            results.append(row)
            print(f"Completed {row['kind']}: {row['label']}", flush=True)
    branches = [row for row in results if row["kind"] == "branch"]
    history_results = [row for row in results if row["kind"] == "history"]
    comparison = convergence_comparison(branches)
    args.output.mkdir(parents=True)
    for result in branches:
        for name, rows in result["branches"].items():
            with (args.output / f"{result['label']}_{name}.csv").open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
    summary = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        action_source="https://arxiv.org/abs/hep-ph/9503408",
        scope="Global scalar-wall profiles; necessary fixed-jacket stress tests with native-carrier credit",
        benchmark_units="c=hbar=vacuum=wall_quartic=carrier_quartic=1; no SI or rail scale assignment",
        screening_assumptions=dict(freely_changing_wall_energy=True, extra_bend_current_cost=0.,
                                   extra_control_and_thermal_cost=0., old_carriers_fully_replaced=True),
        convergence_comparison=comparison,
        branches=[{k: v for k, v in row.items() if k != "branches"} for row in branches],
        histories=history_results)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n")
    runtime_paths = [Path(__file__).resolve(),
        ROOT / "toolkit/adm_harness_cli/adm_harness/current_carrying_wall.py",
        ROOT / "toolkit/adm_harness_cli/adm_harness/magnetic_load_balance.py",
        ROOT / "toolkit/adm_harness_cli/adm_harness/magnetic_geometry.py",
        ROOT / "toolkit/adm_harness_cli/tests/test_current_carrying_wall.py"]
    for path in runtime_paths:
        shutil.copyfile(path, args.output / ("execution_"+path.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in runtime_paths},
        parent_manifest_sha256=sha256(PARENT / "manifest.json"),
        output_sha256={p.name: sha256(p) for p in sorted(args.output.iterdir()) if p.is_file()})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(args.output, flush=True)


if __name__ == "__main__":
    main()
