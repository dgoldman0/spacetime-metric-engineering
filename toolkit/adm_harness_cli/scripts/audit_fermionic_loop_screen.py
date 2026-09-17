#!/usr/bin/env python3
"""Compare finite-radius carrier diagnostics without imposing a bulk-mass cut."""
from concurrent.futures import ProcessPoolExecutor
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

import numpy as np

from adm_harness.fermionic_loop_screen import required_loop_radius, required_node_action, rotor_lab_fermi_bound

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "supporting_reports/data"
PARENTS = ("fermionic_string_material", "controlled_optical_transfer")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified(group, name):
    path = DATA / group / name
    digest = json.loads((DATA / group / "manifest.json").read_text())["output_sha256"][name]
    if sha256(path) != digest:
        raise ValueError(f"Parent evidence mismatch: {path}")
    return path


def candidate(task):
    beta, B, rho, g, e, role = task
    energy = rotor_lab_fermi_bound()["fermi_energy_over_sqrt_mu"] if role == "rotor_forward_branch" else np.sqrt(2*np.pi)
    r = required_loop_radius(B, rho, yukawa=g, gauge_coupling=e,
                            lab_fermi_energy_over_sqrt_mu=energy,
                            radial_speed_bound=.00905 if role == "rotor_forward_branch" else 0.)
    return dict(beta=beta, tension_factor_B=B, yukawa=g, gauge_coupling=e, role=role,
        **r, quartic_loop_to_tree_diagnostic=g**4/(16*np.pi*np.pi*beta*e*e),
        minimum_node_action_for_six_rotors=float(required_node_action(r["required_radius_sqrt_mu"])),
        geometric_and_exponent_diagnostics_met=bool(r["core_over_loop_radius"] <= .01*(1+1e-12)
            and (r["exterior_wkb_exponent"] is None or r["exterior_wkb_exponent"] >= 100*(1-1e-11))),
        local_string_decay_rate_proved=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=DATA / "fermionic_loop_screen")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    for group in PARENTS:
        for path, digest in json.loads((DATA / group / "manifest.json").read_text())["runtime_sha256"].items():
            if sha256(ROOT / path) != digest:
                raise ValueError(f"Parent implementation changed: {path}")
    material_path = verified(PARENTS[0], "summary.json")
    material = json.loads(material_path.read_text())
    tasks = []
    for case in material["cases"]:
        d = case["diagnostics"]["extended"]
        for g in (.3, 1., 2.):
            for e in (.3, 1.):
                for role in ("rotor_forward_branch", "relaxed_stationary_string"):
                    tasks.append((case["beta"], d["tension_factor_B"],
                                  d["scalar_radius_rho"]["0.99"], g, e, role))
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        cases = list(pool.map(candidate, tasks))
    representatives = [c for c in cases if c["role"] == "rotor_forward_branch"
        and c["gauge_coupling"] == 1. and ((c["beta"] == 1. and c["yukawa"] in (.3, 1., 2.))
                                       or (c["beta"] == .1 and c["yukawa"] == 1.))]
    threshold = material["rotor_duty_threshold"]
    diag = threshold["diagnostics"]
    old = candidate((threshold["beta"], diag["tension_factor_B"], diag["scalar_radius_rho"]["0.99"],
                     np.sqrt(.1*16*np.pi*np.pi), 1., "rotor_forward_branch"))
    representatives.append(dict(old, comparison="earlier illustrative kF/m=.3 threshold"))
    inputs = {str(material_path.relative_to(ROOT)): sha256(material_path)}
    histories = []
    for name in ("first_n16_t2057", "first_n32_t4113", "second_n16_t1029", "second_n32_t2057"):
        path = verified(PARENTS[1], name+"_states.npz")
        inputs[str(path.relative_to(ROOT))] = sha256(path)
        with np.load(path) as a:
            action = a["reception_capacity"]*a["transit_delay"]
            active = action > 0
            histories.append(dict(label=name, active_node_labels=int(active.sum()),
                normalized_C_times_delta_range=[float(action[active].min()), float(action[active].max())],
                six_rotor_common_action_unit_requirements=[dict(
                    beta=c["beta"], yukawa=c["yukawa"], gauge_coupling=c["gauge_coupling"],
                    minimum_energy_time_unit_over_hbar=float(c["minimum_node_action_for_six_rotors"]/action[active].min()))
                    for c in representatives]))
    with (args.output / "candidate_geometry.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(cases[0]))
        writer.writeheader()
        writer.writerows(cases)
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__),
        input_sha256=inputs, candidate_count=len(cases), representative_candidates=representatives,
        history_action_scales=histories, rotor_lab_energy_bound=rotor_lab_fermi_bound(),
        primary_source=dict(url="https://arxiv.org/html/2412.12259v1",
            publication="JHEP 03 (2025) 063", sections=["2.2", "4.2", "5.2"],
            distinction="large-loop quasi-bound modes and energy-dependent escape"),
        exterior_action_derived_by_direct_radial_integration=True,
        exponent_target=100., scalar_amplitude_at_exterior=.99,
        maximum_core_to_curvature_radius=.01, counted_rotor_copies=6,
        minimum_normalized_rotor_radius=1.068,
        exponent_is_a_semiclassical_diagnostic=True,
        independent_lab_energy_and_radial_speed_envelope=True,
        moving_background_transition_rate_calculated=False,
        tunneling_prefactor_or_operating_lifetime_calculated=False,
        applicability_to_two_branch_local_string_numerically_established=False,
        curved_higgs_dirac_solution_or_massive_mode_occupancy_solved=False,
        quantum_corrected_potential_solved=False,
        absolute_energy_length_or_cell_volume_assigned=False,
        full_material_feasibility_established=False)
    (args.output / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(), ROOT / "toolkit/adm_harness_cli/adm_harness/fermionic_loop_screen.py",
             ROOT / "toolkit/adm_harness_cli/tests/test_fermionic_loop_screen.py"]
    for path in paths:
        shutil.copyfile(path, args.output / ("execution_"+path.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        parent_manifest_sha256={str((DATA / g / "manifest.json").relative_to(ROOT)):
            sha256(DATA / g / "manifest.json") for g in PARENTS},
        output_sha256={p.name: sha256(p) for p in sorted(args.output.iterdir())
                       if p.is_file() and p.name != "manifest.json"})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    for row in representatives:
        print(row["beta"], row["yukawa"], row["required_radius_sqrt_mu"],
              row["minimum_node_action_for_six_rotors"], flush=True)


if __name__ == "__main__":
    main()
