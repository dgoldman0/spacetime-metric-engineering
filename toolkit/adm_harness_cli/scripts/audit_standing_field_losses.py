#!/usr/bin/env python3
"""Separate standing-field residence losses from scheduled work-port losses."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import multiprocessing
import platform
import shutil
import subprocess

import numpy as np

from adm_harness.material_reconfiguration import PRESSURE_BASIS
from adm_harness.standing_field_losses import (
    decay_rate_ceiling, photon_to_maxwell, residence_exposure,
)

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "supporting_reports/data"
PARENTS = ("scheduled_optical_transfer", "constitutive_joints_and_optics",
           "shared_rail_reactions", "controlled_optical_transfer")
LOSS = .62e-6
REPLACEMENT = 1/(1-LOSS/.3)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified(group, name):
    path = DATA / group / name
    expected = json.loads((DATA / group / "manifest.json").read_text())["output_sha256"][name]
    if sha256(path) != expected:
        raise ValueError(f"Parent evidence mismatch: {path}")
    return path


def limits(a):
    return [float(np.min(a)), float(np.max(a))]


def history(task):
    name, output = task
    paths = [verified(g, name+("_reactions.npz" if g == "shared_rail_reactions" else "_states.npz"))
             for g in PARENTS]
    with np.load(paths[0]) as a, np.load(paths[1]) as j, np.load(paths[2]) as r, np.load(paths[3]) as c:
        for parent in (j, r, c):
            np.testing.assert_array_equal(a["x"], parent["x"])
        E = j["component_energy"][12:16]
        dt = np.diff(j["proper_time"], axis=0)
        service = dt.sum(axis=0)
        delay = c["transit_delay"]
        reserve = (a["all_panel_reserve_lower_bound"]-LOSS*REPLACEMENT*a["finite_loop_total_exposure_upper"]
                   -r["continuous_additional_energy_ceiling"][None])
        np.testing.assert_allclose(reserve.min(axis=0), r["old_transfer_loss_and_reaction_state_reserve_lower"],
                                   rtol=3e-14)
        extras = r["isotropic_bias"]
        variants, arrays = [], dict(x=a["x"], service_duration=service, transfer_delay=delay)
        for family, weights in (("maxwell", [2., 1., 0., 0.]), ("photon", [0., 0., 1., 2.])):
            total = E+np.array(weights)[:, None, None]*extras[None, None]
            I = residence_exposure(total, dt)
            photons = I[2:].sum(axis=0)
            raw = decay_rate_ceiling(photons, reserve)
            screened = decay_rate_ceiling(photons, reserve, replacement_factor=REPLACEMENT)
            rate, panel = screened["rate"], screened["limiting_panel"]
            lifetime_over_service = 1/(rate*service)
            required_period = -np.log1p(-LOSS)/(rate*delay)
            weakest = int(np.argmin(rate))
            variants.append(dict(bias_family=family,
                common_photon_decay_rate_ceiling=limits(rate),
                raw_decay_rate_ceiling=limits(raw["rate"]),
                required_photon_energy_lifetime_over_service_duration=limits(lifetime_over_service),
                required_0_62_ppm_circuit_period_over_transfer_delay=limits(required_period),
                allowed_loss_per_transfer_delay=limits(-np.expm1(-rate*delay)),
                weakest_rate_label=float(a["x"][weakest]),
                weakest_rate_panel=int(panel[weakest]),
                weakest_rate_panel_end_proper_time=float(j["proper_time"][panel[weakest]+1, weakest]),
                original_photon_energy_time_integral_final=limits(
                    residence_exposure(E, dt)[2:, -1].sum(axis=0))))
            arrays[family+"_bias_photon_decay_rate_ceiling"] = rate
            arrays[family+"_bias_limiting_panel"] = panel
            arrays[family+"_bias_required_lifetime_over_service"] = lifetime_over_service
            arrays[family+"_bias_required_period_over_delay"] = required_period
            arrays[family+"_bias_final_field_residence_exposure"] = I[:, -1]
        # Equal-tensor field alternatives use the Maxwell bias already charged above.
        total = E+np.array([2., 1., 0., 0.])[:, None, None]*extras[None, None]
        substitutions = []
        for fraction in (.5, 1.):
            new = photon_to_maxwell(total, fraction)
            energy_error = float(np.max(abs(new.sum(axis=0)-total.sum(axis=0))))
            tensor_error = float(np.max(abs(np.einsum("ij,j...->i...", PRESSURE_BASIS[:, 6:10], new-total))))
            if max(energy_error, tensor_error) > 1e-12:
                raise ValueError("Field substitution changes the target tensor")
            I = residence_exposure(new, dt)
            magnetic_rate = decay_rate_ceiling(I[:2].sum(axis=0), reserve, replacement_factor=REPLACEMENT)["rate"]
            photon_rate = decay_rate_ceiling(I[2:].sum(axis=0), reserve, replacement_factor=REPLACEMENT)["rate"]
            substitutions.append(dict(photon_fraction_replaced=fraction,
                maximum_energy_identity_error=energy_error, maximum_stress_identity_error=tensor_error,
                maximum_added_maxwell_energy=float((new[:2].sum(axis=0)-E[:2].sum(axis=0)).max()),
                isolated_maxwell_decay_rate_ceiling=limits(magnetic_rate),
                isolated_photon_decay_rate_ceiling=limits(photon_rate) if np.isfinite(photon_rate).all() else None,
                all_standing_photon_energy_replaced=fraction == 1.))
            arrays[f"replacement_{fraction:g}_maxwell_decay_ceiling"] = magnetic_rate
        photon_fraction = E[2:].sum(axis=0)/j["component_energy"].sum(axis=0)
    np.savez_compressed(Path(output) / (name+"_loss_requirements.npz"), **arrays)
    row = dict(label=name, input_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        service_duration=limits(service), inherited_transfer_delay=limits(delay),
        maximum_original_photon_fraction_of_total_local_energy=float(photon_fraction.max()),
        minimum_energy_margin_before_standing_losses=float(reserve.min()),
        variants=variants, substitutions=substitutions)
    print(name, "photon gamma ceiling", variants[0]["common_photon_decay_rate_ceiling"],
          "required lifetime/service", variants[0]["required_photon_energy_lifetime_over_service_duration"], flush=True)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=DATA / "standing_field_losses")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    prior = json.loads(verified(PARENTS[0], "summary.json").read_text())
    for group in PARENTS:
        manifest = json.loads((DATA / group / "manifest.json").read_text())
        for path, digest in manifest["runtime_sha256"].items():
            if sha256(ROOT / path) != digest:
                raise ValueError(f"Parent implementation changed: {path}")
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        histories = list(pool.map(history, [(h["label"], str(args.output)) for h in prior["histories"]]))
    payload = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__), histories=histories,
        assigned_transfer_and_candidate_circuit_loss=LOSS,
        conditional_old_converter_replacement_factor=REPLACEMENT,
        exact_piecewise_linear_residence_integrals=True,
        continuous_panel_energy_screen=True,
        original_photon_holding_losses_present_in_prior_transfer_screen=False,
        decay_rate_bounds_share_one_remaining_budget=True,
        new_coupled_reaction_work_included=False,
        photon_confinement_geometry_constructed=False,
        substituted_maxwell_hosts_priced=False,
        full_source_realization_or_dynamical_loss_admission=False)
    (args.output / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False)+"\n")
    paths = [Path(__file__).resolve(), ROOT / "toolkit/adm_harness_cli/adm_harness/standing_field_losses.py",
             ROOT / "toolkit/adm_harness_cli/tests/test_standing_field_losses.py"]
    for p in paths:
        shutil.copyfile(p, args.output / ("execution_"+p.name))
    manifest = dict(runtime_sha256={str(p.relative_to(ROOT)): sha256(p) for p in paths},
        parent_manifest_sha256={str((DATA / g / "manifest.json").relative_to(ROOT)):
            sha256(DATA / g / "manifest.json") for g in PARENTS},
        output_sha256={p.name: sha256(p) for p in sorted(args.output.iterdir()) if p.is_file() and p.name != "manifest.json"})
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")


if __name__ == "__main__":
    main()
