#!/usr/bin/env python3
"""Resolve neutral zero-mode profiles, pair-escape thresholds and flavor costs."""
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

from adm_harness.fermionic_string_material import VortexProfile
from adm_harness.fermionic_loop_screen import required_loop_radius, required_node_action, rotor_lab_fermi_bound
from adm_harness.neutral_fermionic_hosts import (
    flavor_screen, mode_bilinears, normalized_zero_mode, rotor_proper_stretch_lower,
    transverse_dirac_residual,
)

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "supporting_reports/data"
PARENTS = ("fermionic_string_material", "coupled_holding_certificate", "fermionic_loop_screen")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified(group, name):
    path = DATA/group/name
    expected = json.loads((DATA/group/"manifest.json").read_text())["output_sha256"][name]
    if sha256(path) != expected:
        raise ValueError(f"Parent evidence mismatch: {path}")
    return path


def profile_case(task):
    row, ratio, output = task
    path = verified(PARENTS[0], row["archive"])
    values, diagnostics = {}, {}
    with np.load(path) as archive:
        for resolution in ("coarse", "extended"):
            d = row["diagnostics"][resolution]
            p = VortexProfile(row["beta"], archive[resolution+"_log_rho"],
                archive[resolution+"_state"], archive[resolution+"_state_derivative"],
                d["requested_tolerance"], d["maximum_collocation_rms_residual"], d["solver_iterations"])
            mode = normalized_zero_mode(p, mass_ratio=ratio)
            values[resolution+"_log_rho"] = mode.pop("log_rho")
            values[resolution+"_amplitude"] = mode.pop("radial_amplitude")
            diagnostics[resolution] = mode
    error = max(abs(diagnostics["coarse"]["probability_radius_rho"][key]/
                        diagnostics["extended"]["probability_radius_rho"][key]-1)
                for key in ("0.5", "0.9", "0.99"))
    if error > 1e-5:
        raise ValueError(f"Carrier profile refinement failed: {row['beta']}, {ratio}, {error}")
    filename = f"beta{row['beta']:.8g}_ratio{ratio:g}.npz"
    np.savez_compressed(Path(output)/filename, **values)
    return dict(beta=row["beta"], mass_ratio=ratio, archive=filename,
        input_sha256={str(path.relative_to(ROOT)): sha256(path)},
        diagnostics=diagnostics, maximum_probability_radius_relative_change=error)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=DATA/"neutral_fermionic_hosts")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    for group in PARENTS:
        for path, digest in json.loads((DATA/group/"manifest.json").read_text())["runtime_sha256"].items():
            if sha256(ROOT/path) != digest:
                raise ValueError(f"Parent runtime changed: {path}")
    parent_path = verified(PARENTS[0], "summary.json")
    parent = json.loads(parent_path.read_text())
    selected = [c for c in parent["cases"] if np.log10(c["beta"]) in (-1., -.5, 0.)]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        profiles = list(pool.map(profile_case, [(c, ratio, str(args.output))
                            for c in selected for ratio in (.3, .5, 1., 2.)]))
    cases = []
    for row in selected:
        B = row["diagnostics"]["extended"]["tension_factor_B"]
        for g in (.3, .5, 1., 2.):
            for e in (.3, .5, 1.):
                for pairs in (1, 2, 4, 8, 16, 32, 64, 70, 128, 256):
                    result = flavor_screen(B, beta=row["beta"], yukawa=g,
                                           gauge_coupling=e, pair_flavors=pairs)
                    loops = [v for k, v in result.items() if k.startswith("unit_coefficient_")]
                    cases.append(dict(beta=row["beta"], tension_factor_B=B, yukawa=g, gauge_coupling=e,
                        **result, all_unit_coefficient_loop_diagnostics_below_point3=max(loops) < .3))
    residual, sources = 0., 0.
    for row in selected:
        path = verified(PARENTS[0], row["archive"])
        with np.load(path) as p:
            for index in np.linspace(0, len(p["extended_log_rho"])-1, 100).astype(int):
                rho = np.exp(p["extended_log_rho"][index])
                f, _, a, _ = p["extended_state"][:, index]
                for species in (-1, 1):
                    for angle in (0., .2, .9, 2.4, 5.5):
                        residual = max(residual, float(abs(transverse_dirac_residual(rho, angle, f, a, 1., species=species)).max()))
                        b = mode_bilinears(angle=angle, species=species)
                        sources = max(sources, float(abs(b["gauge_current"]).max()),
                            float(abs(b["scalar_amplitude_source"])), float(abs(b["scalar_phase_source"])))
    representatives = [c for c in cases if c["beta"] == 1. and (
        (c["pair_flavors"] == 1 and c["yukawa"] == c["gauge_coupling"] == 1.)
        or (c["pair_flavors"] in (64, 70) and c["yukawa"] == c["gauge_coupling"] == .5))]
    geometries = []
    for candidate in representatives:
        source = next(c for c in selected if c["beta"] == candidate["beta"])["diagnostics"]["extended"]
        energy = rotor_lab_fermi_bound()["fermi_energy_over_sqrt_mu"]/np.sqrt(candidate["pair_flavors"])
        geometry = required_loop_radius(source["tension_factor_B"], source["scalar_radius_rho"]["0.99"],
            yukawa=candidate["yukawa"], gauge_coupling=candidate["gauge_coupling"],
            lab_fermi_energy_over_sqrt_mu=energy, radial_speed_bound=.00905)
        geometries.append(dict(pair_flavors=candidate["pair_flavors"], beta=candidate["beta"],
            yukawa=candidate["yukawa"], gauge_coupling=candidate["gauge_coupling"],
            **geometry, minimum_node_action_for_six_rotors=float(
                required_node_action(geometry["required_radius_sqrt_mu"]))))
    with (args.output/"flavor_requirements.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(cases[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(cases)
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__),
        input_sha256={str(parent_path.relative_to(ROOT)): sha256(parent_path)},
        profile_cases=profiles, candidate_count=len(cases), representative_flavor_cases=representatives,
        representative_loop_geometry=geometries,
        proper_rotor_stretch_lower=rotor_proper_stretch_lower(),
        maximum_four_component_dirac_residual=residual, maximum_local_source_bilinear=sources,
        scalar_and_gauge_field_classical_mean_sources_cancel_per_species=True,
        half_integer_carriers_retain_residual_Z2_gauge_charge=True,
        gauge_and_gravitational_anomalies_cancel_per_pair=True,
        independent_conserved_flavor_numbers_assumed=True,
        changing_spin_requires_additional_branch_occupation_interface=True,
        torque_driven_branch_conversion_constructed=False,
        massive_final_pair_fraction_is_kinematic_only=True,
        multi_flavor_unit_loop_diagnostics_include_all_species=True,
        massive_mode_transition_matrix_elements_or_decay_rates_calculated=False,
        quantum_corrected_vortex_or_finite_curvature_spectrum_solved=False,
        two_dimensional_material_network_or_junction_law_constructed=False,
        optical_reflection_or_work_transducer_supplied_by_carrier_model=False,
        empirical_material_realization_identified=False,
        primary_model_source="https://arxiv.org/pdf/hep-ph/0007015",
        occupied_massive_mode_source="https://arxiv.org/abs/hep-ph/0106179",
        homogeneous_one_loop_potential_source="https://arxiv.org/pdf/hep-ph/0111209",
        full_material_feasibility_established=False)
    (args.output/"summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(), ROOT/"toolkit/adm_harness_cli/adm_harness/neutral_fermionic_hosts.py",
             ROOT/"toolkit/adm_harness_cli/tests/test_neutral_fermionic_hosts.py"]
    for path in paths:
        shutil.copyfile(path, args.output/("execution_"+path.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        parent_manifest_sha256={str((DATA/g/"manifest.json").relative_to(ROOT)):
            sha256(DATA/g/"manifest.json") for g in PARENTS},
        output_sha256={p.name: sha256(p) for p in sorted(args.output.iterdir())
                       if p.is_file() and p.name != "manifest.json"})
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    for row in representatives:
        print(row, flush=True)


if __name__ == "__main__":
    main()
