#!/usr/bin/env python3
"""Resolve finite-width vortex tension and conditional fermionic carrier duty."""
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
import scipy
from scipy.optimize import brentq

from adm_harness.fermionic_string_material import (
    VortexProfile, critical_tension_factor, fermion_duty, profile_diagnostics,
    radius_at_fixed_tension, solve_vortex,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = ROOT / "supporting_reports/data/fermionic_string_material"
STRETCHES = (2.3349, 1.17, 1.)
ESCAPE_RATIOS = (1., .5, .3, .1)
GAUGE_COUPLINGS = (.1, .3, 1.)
NORMALIZATIONS = ("canonical_two_branches", "printed_ringeval_two_branches")
THRESHOLD_STRETCH, THRESHOLD_ESCAPE, THRESHOLD_LOOP = 1.17, .3, .1
WIDTH_GROUPS = ("scalar_radius_rho", "enclosed_flux_radius_rho", "enclosed_energy_radius_rho")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_profiles(path, profiles, beta):
    archive = dict(beta=beta, log10_beta=np.log10(beta))
    for name, profile in profiles.items():
        archive[name+"_log_rho"] = profile.log_rho
        archive[name+"_state"] = profile.state
        archive[name+"_state_derivative"] = profile.state_derivative
    np.savez_compressed(path, **archive)


def read_profile(output, row):
    diagnostic = row["diagnostics"]["extended"]
    with np.load(Path(output)/row["archive"]) as archive:
        return VortexProfile(row["beta"], archive["extended_log_rho"], archive["extended_state"],
            archive["extended_state_derivative"], diagnostic["requested_tolerance"],
            diagnostic["maximum_collocation_rms_residual"], diagnostic["solver_iterations"])


def valid_profile(diagnostic):
    d = diagnostic
    passed = (d["virial_relative_to_total"] < 2e-7
        and d["square_completion_identity_error"] < 2e-8
        and d["gauss8_gauss16_difference"] < 1e-10
        and d["maximum_collocation_rms_residual"] <= d["requested_tolerance"]
        and d["scalar_range"][0] >= 0 and d["scalar_range"][1] <= 1+1e-9
        and d["gauge_range"][0] >= 0 and d["gauge_range"][1] <= 1+1e-9
        and d["minimum_scalar_log_derivative"] >= -1e-9
        and d["minimum_gauge_log_derivative"] >= -1e-9)
    if d["beta"] == 1.:
        passed = passed and abs(d["tension_factor_B"]-1.) < 2e-8 and d["bps_squares_integral"] < 1e-12
    return bool(passed)


def width_difference(left, right):
    return max(abs(left[group][fraction]/right[group][fraction]-1)
        for group in WIDTH_GROUPS for fraction in ("0.5", "0.9", "0.99"))


def fixed_tension_widths(diagnostic):
    return {group: {fraction: float(radius_at_fixed_tension(value, diagnostic["tension_factor_B"]))
        for fraction, value in diagnostic[group].items()} for group in WIDTH_GROUPS}


def solve_case(task):
    index, exponent, output = task
    beta = 10.**exponent
    # Each independent job uses bounded continuation from the validated BPS end.
    continuation = np.linspace(0., exponent, max(1, int(np.ceil(-exponent)))+1)
    previous = None
    for value in continuation:
        previous = solve_vortex(10.**value, previous=previous)
    coarse = previous
    refined = solve_vortex(beta, mesh_points=1000, tolerance=2e-8, previous=coarse)
    extended = solve_vortex(beta, mesh_points=1400, tolerance=2e-9,
        inner_radius=1e-6, outer_tail=30., outer_minimum=45., previous=refined)
    profiles = dict(coarse=coarse, refined=refined, extended=extended)
    diagnostics = {name: profile_diagnostics(profile) for name, profile in profiles.items()}
    filename = f"beta_{index:02d}_profiles.npz"
    save_profiles(Path(output)/filename, profiles, beta)
    best = diagnostics["extended"]
    B = best["tension_factor_B"]
    resolution_difference = abs(B-diagnostics["coarse"]["tension_factor_B"])
    extension_difference = abs(B-diagnostics["refined"]["tension_factor_B"])
    width_change = width_difference(best, diagnostics["refined"])
    passed = (resolution_difference < 2e-7 and extension_difference < 2e-8
        and width_change < 2e-6 and valid_profile(best))
    if not passed:
        raise ValueError(f"Vortex verification failed at beta={beta:g}: {diagnostics}")
    screens = [fermion_duty(B, stretch, escape_ratio=ratio, gauge_coupling=e,
        beta=beta, normalization=normalization)
        for normalization in NORMALIZATIONS for stretch in STRETCHES
        for ratio in ESCAPE_RATIOS for e in GAUGE_COUPLINGS]
    print(f"beta={beta:.6g} B={B:.10f} scalar90={best['scalar_radius_rho']['0.9']:.6g} "
          f"virial={best['virial_relative_to_total']:.3g}", flush=True)
    return dict(beta=beta, log10_beta=exponent, archive=filename,
        diagnostics=diagnostics, coarse_to_extended_B_difference=resolution_difference,
        refined_to_extended_B_difference=extension_difference,
        refined_to_extended_maximum_relative_width_change=width_change,
        fixed_mu_widths_times_e=fixed_tension_widths(best),
        numerical_verification_passed=bool(passed), carrier_screens=screens)


def locate_threshold(rows, output):
    """Bracket and refine the canonical rotor-duty rectangle on computed B."""
    target = critical_tension_factor(THRESHOLD_STRETCH, THRESHOLD_ESCAPE, THRESHOLD_LOOP)
    result = dict(stretch=THRESHOLD_STRETCH, escape_ratio=THRESHOLD_ESCAPE,
        maximum_yukawa_loop_size=THRESHOLD_LOOP, critical_tension_factor_B=target,
        normalization=NORMALIZATIONS[0], threshold_bracketed=False, root_evaluations=[])
    bracket = next(((lo, hi) for lo, hi in zip(rows[:-1], rows[1:])
        if lo["diagnostics"]["extended"]["tension_factor_B"] <= target
        <= hi["diagnostics"]["extended"]["tension_factor_B"]), None)
    if bracket is None:
        return result, None
    low, high = bracket
    seed = read_profile(output, high)
    cache = {}

    def residual(exponent):
        profile = solve_vortex(10.**exponent, mesh_points=1400, tolerance=2e-9,
            inner_radius=1e-6, outer_tail=30., outer_minimum=45., previous=seed)
        diagnostic = profile_diagnostics(profile)
        if not valid_profile(diagnostic):
            raise ValueError(f"Threshold profile verification failed: {diagnostic}")
        cache[exponent] = profile, diagnostic
        B = diagnostic["tension_factor_B"]
        result["root_evaluations"].append(dict(log10_beta=exponent, beta=profile.beta, B=B))
        return B-target

    exponent = brentq(residual, low["log10_beta"], high["log10_beta"], xtol=2e-10)
    if exponent not in cache:
        residual(exponent)
    profile, diagnostic = cache[exponent]
    filename = "threshold_reference_profile.npz"
    save_profiles(Path(output)/filename, dict(reference=profile), profile.beta)
    result.update(threshold_bracketed=True, beta=profile.beta, log10_beta=exponent,
        bracket_beta=[low["beta"], high["beta"]], archive=filename,
        diagnostics=diagnostic, fixed_mu_widths_times_e=fixed_tension_widths(diagnostic))
    return result, profile


def stronger_domain_check(task):
    name, previous, output = task
    profile = solve_vortex(previous.beta, mesh_points=2400, tolerance=2e-10,
        inner_radius=1e-7, outer_tail=50., outer_minimum=75., max_nodes=60000, previous=previous)
    before, best = profile_diagnostics(previous), profile_diagnostics(profile)
    difference = abs(best["tension_factor_B"]-before["tension_factor_B"])
    width_change = width_difference(best, before)
    if not (valid_profile(best) and difference < 2e-8 and width_change < 2e-6):
        raise ValueError(f"Stronger vortex verification failed: {name}, {best}")
    filename = name+"_stronger_profile.npz"
    save_profiles(Path(output)/filename, dict(stronger=profile), profile.beta)
    screens = [fermion_duty(best["tension_factor_B"], stretch,
        escape_ratio=THRESHOLD_ESCAPE, gauge_coupling=e, beta=profile.beta, normalization=normalization)
        for normalization in NORMALIZATIONS for stretch in STRETCHES for e in GAUGE_COUPLINGS]
    return dict(name=name, beta=profile.beta, archive=filename, diagnostics=best,
        energy_change_from_standard_extended=difference,
        maximum_relative_width_change_from_standard_extended=width_change,
        fixed_mu_widths_times_e=fixed_tension_widths(best), carrier_screens=screens,
        numerical_verification_passed=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--minimum-log10-beta", type=float, default=-12.)
    parser.add_argument("--beta-samples", type=int, default=25)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        parser.error("workers must lie between one and four")
    if not -12 <= args.minimum_log10_beta < 0 or args.beta_samples < 2:
        parser.error("bounded negative minimum log beta and at least two samples required")
    args.output.mkdir(parents=True, exist_ok=True)
    exponents = np.linspace(args.minimum_log10_beta, 0., args.beta_samples)
    tasks = [(i, float(value), str(args.output)) for i, value in enumerate(exponents)]
    with ProcessPoolExecutor(max_workers=args.workers,
            mp_context=multiprocessing.get_context("spawn")) as pool:
        rows = list(pool.map(solve_case, tasks))
        threshold, crossing_profile = locate_threshold(rows, args.output)
        checks = [("minimum_beta", read_profile(args.output, rows[0]), str(args.output))]
        if crossing_profile is not None:
            checks.append(("threshold", crossing_profile, str(args.output)))
        stronger_checks = list(pool.map(stronger_domain_check, checks))
    if not np.all(np.diff([row["diagnostics"]["extended"]["tension_factor_B"] for row in rows]) > 0):
        raise ValueError("Sampled vortex tension is not increasing with beta")
    summary = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        minimum_log10_beta=args.minimum_log10_beta, beta_samples=args.beta_samples,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        normalization=dict(mu="pi*eta^2*B", rho="e*eta*r", beta="lambda_h/e^2",
            higgs_mass="sqrt(lambda_h)*eta", vector_mass="e*eta", fermion_bulk_mass="g*eta",
            energy="integral rho*(f_rho^2+(1-a)^2*f^2/rho^2+a_rho^2/rho^2+beta*(1-f^2)^2/4) drho",
            canonical_tradeoff="(kF/m_bulk)^2 * g^2/(16*pi^2) = B/(8*stretch^2)",
            printed_ringeval_tradeoff="B/(16*stretch^2)",
            fixed_mu_width="r*sqrt(mu) = rho*sqrt(pi*B)/e",
            fixed_mu_widths_times_e="stored radius equals e*r*sqrt(mu)"),
        primary_sources=[dict(url="https://arxiv.org/pdf/hep-ph/0007015",
            equations="2,3,10,111,119,128,129,150,151"),
            dict(url="https://arxiv.org/pdf/2102.05412", equations="4.1,4.2"),
            dict(url="https://arxiv.org/pdf/hep-ph/0011308", equations="19,22,25")],
        stretches=list(STRETCHES), escape_ratios=list(ESCAPE_RATIOS),
        gauge_couplings=list(GAUGE_COUPLINGS), cases=rows, rotor_duty_threshold=threshold,
        stronger_domain_and_resolution_checks=stronger_checks,
        stronger_check_parameters=dict(mesh_points=2400, tolerance=2e-10,
            inner_radius=1e-7, outer_tail=50., outer_minimum=75., max_nodes=60000),
        numerical_classical_vortex_screen_passed=True,
        carrier_normalization_discrepancy_retained=True,
        loop_size_diagnostic_coefficient=1., loop_size_diagnostic_is_a_no_go_theorem=False,
        fermion_transverse_eigenproblem_solved=False, charged_backreaction_solved=False,
        quantum_corrected_potential_solved=False, leakage_rate_calculated=False,
        physical_radius_or_energy_scale_assigned=False, physical_material_window_established=False)
    (args.output/"summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n")
    with (args.output/"vortex_tension_and_widths.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["beta", "B", "scalar_rho50", "scalar_rho90", "scalar_rho99",
            "flux_rho90", "energy_rho90", "coarse_extended_B_difference",
            "refined_extended_B_difference", "virial_relative_to_total",
            "scalar_r90_sqrt_mu_times_e", "flux_r90_sqrt_mu_times_e", "energy_r90_sqrt_mu_times_e"])
        for row in rows:
            best = row["diagnostics"]["extended"]
            writer.writerow([row["beta"], best["tension_factor_B"],
                *[best["scalar_radius_rho"][q] for q in ("0.5", "0.9", "0.99")],
                best["enclosed_flux_radius_rho"]["0.9"], best["enclosed_energy_radius_rho"]["0.9"],
                row["coarse_to_extended_B_difference"], row["refined_to_extended_B_difference"],
                best["virial_relative_to_total"],
                *[row["fixed_mu_widths_times_e"][group]["0.9"] for group in WIDTH_GROUPS]])
    flat = [dict(beta=row["beta"], B=row["diagnostics"]["extended"]["tension_factor_B"], **screen)
            for row in rows for screen in row["carrier_screens"]]
    with (args.output/"carrier_diagnostics.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(flat[0]))
        writer.writeheader()
        writer.writerows(flat)
    paths = [Path(__file__).resolve(),
        ROOT/"toolkit/adm_harness_cli/adm_harness/fermionic_string_material.py",
        ROOT/"toolkit/adm_harness_cli/tests/test_fermionic_string_material.py"]
    for path in paths:
        shutil.copyfile(path, args.output/("execution_"+path.name))
    manifest = dict(runtime_sha256={str(path.relative_to(ROOT)): sha256(path) for path in paths},
        output_sha256={path.name: sha256(path) for path in sorted(args.output.iterdir())
                       if path.is_file() and path.name != "manifest.json"})
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
