#!/usr/bin/env python3
"""Audit frozen LE-gate inputs and classifier fixtures; write data tables only.

This reads the existing baseline/dense source products and regenerates a small
set of metric points. It performs no fitting, source retuning, or boundary sweep.
The narrative assessment is maintained manually in supporting_reports.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adm_harness.endpoint_j_source_class_screen import classify_endpoint_source_frame
from adm_harness.source_ledger import SourceParams, einstein_tensor_at, projections, sha256_file


ROOT = Path(__file__).resolve().parents[3]
RUNS = ROOT / "toolkit/adm_harness_cli/runs"
SURFACES = {
    "baseline": "beta_collar_generator_beta075_p003_mid_s15",
    "dense": "beta_collar_generator_beta075_p003_mid_dense377x241_sharded12",
}
CHANNELS = ["rho_euler", "p_l_unit", "j_l_unit", "p_omega_unit"]
SECTOR = ["sector_rho", "sector_p_l", "sector_j_l", "sector_p_omega"]
MEDIUM = ["regulated_sector_rho", "regulated_sector_p_l", "regulated_sector_j_l", "medium_angular_pressure"]
KEYS = ["case", "s", "l"]
METRIC = ["alpha", "beta", "gamma_ll", "gamma_omega"]
S0 = "S0_constant_flux_string_cloud"
J = "J_endpoint_junction_layer"


def read_json(path):
    return json.loads(path.read_text())


def columns(path):
    return pd.read_csv(path, nrows=0).columns.tolist()


def keyed(frame):
    result = frame.copy()
    result["s"] = result["s"].round(12)
    result["l"] = result["l"].round(12)
    if result.duplicated(KEYS).any():
        raise ValueError("duplicate spacetime keys")
    return result.set_index(KEYS)


def orthonormal_tensor(channels):
    """Covariant tensor in the (-+++) ADM orthonormal frame, j=-T_01."""
    values = np.asarray(channels, dtype=float)
    rho, pressure, current, angular = values.T
    tensor = np.zeros((len(values), 4, 4))
    tensor[:, 0, 0] = rho
    tensor[:, 0, 1] = tensor[:, 1, 0] = -current
    tensor[:, 1, 1] = pressure
    tensor[:, 2, 2] = tensor[:, 3, 3] = angular
    return tensor


def fixture_audit():
    # The expected types follow the explicit canonical tensors, independently
    # of the legacy radial discriminant classifier under examination.
    fixtures = [
        ("vacuum", [0, 0, 0, 0], "type_i_boost_diagonalizable", 0, 0),
        ("ordinary_diagonal", [2, 1, 0, .3], "type_i_boost_diagonalizable", 2, 1),
        ("radial_tension", [1, -1, 0, 0], "type_i_boost_diagonalizable", 1, -1),
        ("isotropic_degenerate", [1, -1, 0, -1], "type_i_boost_diagonalizable", 1, -1),
        ("negative_enthalpy", [1, -2, 0, 0], "type_i_boost_diagonalizable", 1, -2),
        ("null_dust", [1, 1, 1, 0], "type_ii_null_boundary", None, None),
        ("flux_dominant", [1, -1, .2, 0], "type_iv_flux_dominant", None, None),
    ]
    rows = []
    for name, values, expected, rest_rho, rest_p in fixtures:
        for scale in ([1.] if name == "vacuum" else [1e-8, 1., 1e8]):
            scaled = np.asarray(values) * scale
            frame = pd.DataFrame([dict(zip(SECTOR, scaled)) | {"volume_weight": 1.}])
            actual = classify_endpoint_source_frame(frame).iloc[0]
            mixed = np.diag([-1., 1., 1., 1.]) @ orthonormal_tensor([values])[0]
            eigenvalues, eigenvectors = np.linalg.eig(mixed)
            residual = np.max(np.abs(mixed @ eigenvectors - eigenvectors * eigenvalues))
            norms = np.einsum("ai,ab,bi->i", eigenvectors.conj(), np.diag([-1., 1., 1., 1.]), eigenvectors)
            expected_rest = rest_rho is not None
            if expected_rest:
                rest_ok = bool(np.isclose(actual.rest_frame_energy_density / scale, rest_rho, atol=1e-12)
                               and np.isclose(actual.rest_frame_radial_pressure / scale, rest_p, atol=1e-12))
            else:
                rest_ok = bool(pd.isna(actual.rest_frame_energy_density) and pd.isna(actual.rest_frame_radial_pressure))
            type_ok = actual.stress_algebraic_type == expected
            heat_ok = bool(actual.type_i_heat_flux_compatible) == expected_rest
            rows.append({
                "fixture": name, "amplitude_scale": scale,
                "expected_type": expected, "actual_type": actual.stress_algebraic_type,
                "type_pass": bool(type_ok), "rest_frame_pass": rest_ok,
                "heat_frame_flag_pass": heat_ok, "fixture_pass": bool(type_ok and rest_ok and heat_ok),
                "expected_rest_energy": None if rest_rho is None else rest_rho * scale,
                "actual_rest_energy": actual.rest_frame_energy_density,
                "actual_rest_radial_pressure": actual.rest_frame_radial_pressure,
                "reference_mixed_eigenvalues_at_unit_scale": json.dumps([[float(v.real), float(v.imag)] for v in eigenvalues]),
                "reference_eigenvector_causal_norms": json.dumps([float(v.real) for v in norms]),
                "reference_eigen_residual": float(residual),
                "reference_eigenbasis_rank": int(np.linalg.matrix_rank(eigenvectors)),
            })
    return pd.DataFrame(rows)


def audit_surface(label):
    base = RUNS / SURFACES[label]
    hashes = []

    def artifact(directory, manifest_name, key):
        manifest_path = base / directory / manifest_name
        manifest = read_json(manifest_path)
        stored = Path(manifest["files"][key])
        candidates = [stored, ROOT / stored, ROOT / "toolkit/adm_harness_cli" / stored,
                      manifest_path.parent / stored.name]
        path = next((p for p in candidates if p.is_file()), None)
        if path is None:
            raise FileNotFoundError(stored)
        path = path.resolve()
        expected = manifest.get("sha256", {}).get(key)
        if key == "point_ledger":
            expected = manifest.get("point_ledger_sha256", expected)
        observed = sha256_file(path)
        hashes.append({"surface": label, "path": str(path.relative_to(ROOT)),
                       "manifest": str(manifest_path.relative_to(ROOT)),
                       "manifest_sha256": sha256_file(manifest_path),
                       "expected_sha256": expected, "actual_sha256": observed,
                       "hash_matches": expected == observed if expected else None})
        return path, manifest

    ledger_path, source_manifest = artifact("ledgers/rematch_w6_t1p5", "source_ledger_manifest.json", "point_ledger")
    sector_path, _ = artifact("intermediate_rematch_w6_t1p5", "intermediate_source_model_manifest.json", "point_sector_stress")
    fit_path, _ = artifact("endpoint_j_freeze_source_model_rematch_w6_t1p5", "endpoint_j_closure_component_manifest.json", "fit_sector_stress")
    projection_path, _ = artifact("endpoint_medium_covariant_audit_freeze_rematch_w6_t1p5", "endpoint_medium_covariant_manifest.json", "point_projection")
    support_path, _ = artifact("endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5", "endpoint_support_stroke_exchange_manifest.json", "point_fit")
    component_path, _ = artifact("component_rematch_w6_t1p5", "component_source_manifest.json", "detail")
    coeff_path, _ = artifact("endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5", "endpoint_support_stroke_exchange_manifest.json", "coefficients")

    ledger = pd.read_csv(ledger_path, usecols=KEYS + METRIC + CHANNELS + ["volume_weight", "region", "inside_packet_live"])
    if not np.isfinite(ledger[METRIC + CHANNELS + ["volume_weight"]].to_numpy()).all():
        raise ValueError(f"nonfinite source or metric fields: {label}")
    ledger["point_index"] = np.arange(len(ledger))
    keyed(ledger)  # Enforce one source tensor per spacetime point.
    if (ledger[["alpha", "gamma_ll", "gamma_omega"]] <= 0).any().any():
        raise ValueError("invalid ADM metric")
    source = ledger.set_index("point_index")
    sectors = pd.read_csv(sector_path, usecols=KEYS + ["point_index", "sector", "assignment"] + SECTOR)
    if sectors.duplicated(["point_index", "sector"]).any():
        raise ValueError("duplicate intermediate sector")
    for _, group in sectors.groupby("sector"):
        expected = source.loc[group.point_index]
        if not np.allclose(group[["s", "l"]], expected[["s", "l"]], atol=1e-12, rtol=0):
            raise ValueError("intermediate point indices refer to different coordinates")
        if not np.array_equal(group.case.to_numpy(), expected.case.to_numpy()):
            raise ValueError("intermediate case mismatch")
    summed = sectors.groupby("point_index")[SECTOR].sum()
    reference = source.loc[summed.index]
    error = summed.to_numpy() - reference[CHANNELS].to_numpy()
    covered_weight = reference.volume_weight.to_numpy()
    complement = source.loc[~source.index.isin(summed.index)]
    target_j = sectors.loc[sectors.sector == J].set_index("point_index")
    fit = pd.read_csv(fit_path, usecols=["point_index", "sector"] + SECTOR).set_index("point_index")
    if not fit.index.is_unique or set(fit.index) != set(target_j.index):
        raise ValueError("frozen J fit and target J have different point sets")
    fit = fit.loc[target_j.index]

    tensor_cols = [f"Tcov_{a}{b}" for a in range(4) for b in range(4)]
    upper_cols = [f"Tuu_{a}{b}" for a in range(4) for b in range(4)]
    regulator_cols = ["regulator_delta_sector_rho", "regulator_delta_sector_p_l", "regulator_delta_sector_j_l"]
    medium = pd.read_csv(projection_path, usecols=KEYS + ["point_index", "regulator_safety_factor", "regulated_rest_frame_energy_density"] + METRIC + MEDIUM + SECTOR + regulator_cols + tensor_cols + upper_cols)
    if set(medium.point_index) != set(target_j.index):
        raise ValueError("endpoint medium and target J have different point sets")
    keyed(medium)
    medium = medium.set_index("point_index").loc[target_j.index]
    if not np.allclose(medium[["s", "l"]], source.loc[medium.index, ["s", "l"]], atol=1e-12, rtol=0):
        raise ValueError("medium coordinates do not match source")
    j_weights = source.loc[target_j.index, "volume_weight"].to_numpy()
    j_target_norm = float(np.sum(np.abs(target_j[SECTOR].to_numpy()) * j_weights[:, None]))
    full_source_norm = float((source[CHANNELS].abs().sum(axis=1) * source.volume_weight).sum())
    medium_delta = medium[MEDIUM].to_numpy() - target_j[SECTOR].to_numpy()
    fit_delta = fit[SECTOR].to_numpy() - target_j[SECTOR].to_numpy()
    medium_error_norm = float(np.sum(np.abs(medium_delta) * j_weights[:, None]))
    channel_errors = {}
    for i, channel in enumerate(CHANNELS):
        norm = float(np.sum(np.abs(target_j[SECTOR[i]].to_numpy()) * j_weights))
        abs_error = float(np.sum(np.abs(medium_delta[:, i]) * j_weights))
        channel_errors[channel] = {"target_weighted_l1": norm, "medium_error_weighted_l1": abs_error,
                                   "relative_l1": abs_error / norm if norm > 0 else None}
    medium_fit_delta = medium[MEDIUM].to_numpy()[:, :3] - fit[SECTOR].to_numpy()[:, :3]
    regulator_error = medium_fit_delta - medium[regulator_cols].to_numpy()

    # Independently recover ADM channels from the stored coordinate tensor.
    t_cov = medium[tensor_cols].to_numpy().reshape(-1, 4, 4)
    alpha, beta, radial, angular = medium[METRIC].to_numpy().T
    n = np.column_stack([1/alpha, -beta/alpha, np.zeros(len(medium)), np.zeros(len(medium))])
    e = np.zeros_like(n)
    e[:, 1] = 1 / np.sqrt(radial)
    extracted = np.column_stack([
        np.einsum("ni,nij,nj->n", n, t_cov, n),
        np.einsum("ni,nij,nj->n", e, t_cov, e),
        -np.einsum("ni,nij,nj->n", e, t_cov, n),
        (t_cov[:, 2, 2] + t_cov[:, 3, 3]) / (2 * angular),
    ])
    projection_error = extracted - medium[MEDIUM].to_numpy()

    # Sign-aware radial rest energy, cross-checked with a timelike eigenvector
    # at the worst discrepancy. This audit uses only well-resolved Type-I rows.
    rho, pressure, current, _ = medium[MEDIUM].to_numpy().T
    enthalpy = rho + pressure
    scale = np.maximum.reduce([np.abs(rho), np.abs(pressure), np.abs(current)])
    normalized_h = np.divide(enthalpy, scale, out=np.zeros_like(enthalpy), where=scale > 0)
    normalized_j = np.divide(current, scale, out=np.zeros_like(current), where=scale > 0)
    normalized_delta = normalized_h**2 - 4 * normalized_j**2
    resolved_type_i = normalized_delta > 1e-10
    corrected_rest_energy = .5 * (rho - pressure + np.sign(enthalpy) * scale * np.sqrt(np.maximum(normalized_delta, 0)))
    rest_error = np.abs(medium.regulated_rest_frame_energy_density.to_numpy() - corrected_rest_energy)
    rest_mismatch = resolved_type_i & (rest_error > 1e-10 * scale + 1e-14)
    rest_witness = None
    if rest_mismatch.any():
        worst = int(np.argmax(np.where(resolved_type_i, rest_error, -1)))
        witness = medium.iloc[worst]
        mixed = np.diag([-1., 1., 1., 1.]) @ orthonormal_tensor([witness[MEDIUM].to_numpy(dtype=float)])[0]
        eigenvalues, eigenvectors = np.linalg.eig(mixed)
        timelike = []
        for i in range(4):
            if abs(eigenvalues[i].imag) < 1e-12 and np.max(np.abs(eigenvectors[:, i].imag)) < 1e-12:
                vector = eigenvectors[:, i].real
                norm = float(vector @ np.diag([-1., 1., 1., 1.]) @ vector)
                if norm < -1e-8:
                    timelike.append((float(-eigenvalues[i].real), norm))
        if len(timelike) != 1 or not np.isclose(timelike[0][0], corrected_rest_energy[worst], atol=1e-12, rtol=1e-10):
            raise ValueError("rest-energy witness disagrees with independent causal eigenvector")
        rest_witness = {"point_index": int(witness.name), "s": float(witness.s), "l": float(witness.l),
                        "stored_rest_energy": float(witness.regulated_rest_frame_energy_density),
                        "causal_eigenvector_rest_energy": timelike[0][0], "eigenvector_metric_norm": timelike[0][1]}

    support_fields = columns(support_path)
    support = pd.read_csv(support_path, usecols=KEYS + upper_cols + ["medium_source_active", "fit_P", "fit_F"])
    joined = keyed(support).join(keyed(medium.reset_index())[upper_cols], rsuffix="_endpoint", how="left")
    active = joined.medium_source_active.astype(bool)
    if joined.loc[active, [c + "_endpoint" for c in upper_cols]].isna().any().any():
        raise ValueError("support active rows lack endpoint tensor")
    copied_error = joined.loc[active, upper_cols].to_numpy() - joined.loc[active, [c + "_endpoint" for c in upper_cols]].to_numpy()

    components = pd.read_csv(component_path, usecols=["point_index", "component", "channel"] + CHANNELS)
    repeated_error = components[CHANNELS].to_numpy() - source.loc[components.point_index, CHANNELS].to_numpy()
    counts = components.groupby("point_index").size()
    sample_ids = sorted(set([0, len(source)//2, len(source)-1,
                             int(source["rho_euler"].abs().idxmax()),
                             int(source["j_l_unit"].abs().idxmax()),
                             int(target_j.index[len(target_j)//2])]))
    params = SourceParams(**source_manifest["params"])
    grid = source_manifest["grid"]
    regenerated = []
    for idx in sample_ids:
        row = source.loc[idx]
        einstein, _ = einstein_tensor_at(row.s, row.l, params, grid["h_s"], grid["h_l"])
        calculated = projections(row.s, row.l, einstein, params)
        residual = np.asarray([calculated[c] - row[c] for c in CHANNELS])
        regenerated.append({"surface": label, "point_index": idx, "s": row.s, "l": row.l,
                            "max_abs_channel_error": float(np.abs(residual).max())})

    if len(source) != grid["ns"] * grid["nl"]:
        raise ValueError("source row count differs from grid specification")
    if ledger.s.nunique() != grid["ns"] or ledger.l.nunique() != grid["nl"]:
        raise ValueError("source axes differ from grid specification")

    edge = source.loc[np.isclose(np.abs(source.l), float(grid["l_max"]), atol=1e-12)]
    final_edge = edge.loc[np.isclose(edge.s, float(grid["s_max"]), atol=1e-12)]
    tail_rows = []
    for idx, row in final_edge.iterrows():
        amplitude = params.Rth**2 / (8 * np.pi * (row.l**2 + params.Rth**2)**2)
        predicted = np.array([-amplitude, -amplitude, 0., amplitude])
        tail_rows.append({"surface": label, "point_index": int(idx), "s": row.s, "l": row.l,
                          **{c: float(row[c]) for c in CHANNELS},
                          "ultrastatic_tail_amplitude": amplitude,
                          "tail_formula_max_abs_error": float(np.max(np.abs(row[CHANNELS].to_numpy(dtype=float)-predicted))),
                          "angular_metric_offset": float(row.gamma_omega-row.l**2)})

    summary = {
        "surface": label, "grid": grid, "params": source_manifest["params"],
        "source_module_sha_matches_manifest": sha256_file(ROOT / "toolkit/adm_harness_cli/adm_harness/source_ledger.py") == source_manifest["source_ledger_module_sha256"],
        "ledger_rows": len(source), "expected_grid_rows": grid["ns"] * grid["nl"],
        "source_channels_finite": True, "metric_positive": True,
        "intermediate_rows": len(sectors), "intermediate_unique_points": len(summed),
        "intermediate_full_grid_fraction": len(summed)/len(source),
        "intermediate_reconstruction_max_abs_error": float(np.abs(error).max()),
        "intermediate_reconstruction_weighted_abs_error": float(np.sum(np.abs(error)*covered_weight[:, None])),
        "full_grid_complement_points": len(complement),
        "full_grid_complement_nonzero_points": int((complement[CHANNELS].abs().max(axis=1) > 1e-12).sum()),
        "full_grid_complement_weighted_channel_l1": float((complement[CHANNELS].abs().sum(axis=1)*complement.volume_weight).sum()),
        "endpoint_medium_points": len(medium), "regulator_safety_factors": sorted(medium.regulator_safety_factor.unique().tolist()),
        "medium_projection_max_abs_error": float(np.abs(projection_error).max()),
        "medium_resolved_type_i_points": int(resolved_type_i.sum()),
        "medium_negative_radial_enthalpy_points": int((enthalpy < 0).sum()),
        "medium_stored_rest_energy_mismatch_points": int(rest_mismatch.sum()),
        "medium_stored_rest_energy_max_abs_error": float(rest_error[resolved_type_i].max()) if resolved_type_i.any() else None,
        "medium_stored_rest_energy_witness": rest_witness,
        "full_source_weighted_channel_l1": full_source_norm,
        "target_J_weighted_channel_l1": j_target_norm,
        "frozen_fit_vs_target_J_weighted_relative_l1": float(np.sum(np.abs(fit_delta)*j_weights[:, None]) / j_target_norm),
        "medium_vs_target_J_weighted_abs_error": medium_error_norm,
        "medium_vs_target_J_weighted_relative_l1": medium_error_norm / j_target_norm,
        "medium_replacement_error_relative_to_full_source_l1": medium_error_norm / full_source_norm,
        "medium_vs_target_J_by_channel": channel_errors,
        "medium_vs_target_J_max_abs_error": float(np.abs(medium_delta).max()),
        "regulator_already_in_medium_max_abs_identity_error": float(np.abs(regulator_error).max()),
        "support_exchange_rows": len(support),
        "support_inherited_endpoint_tensor_max_abs_error": float(np.abs(copied_error).max()),
        "support_inactive_inherited_tensor_max_abs": float(np.abs(joined.loc[~active, upper_cols].to_numpy()).max()) if (~active).any() else 0.,
        "support_explicit_stress_columns": [c for c in support_fields if c.startswith(("support_T", "Tsupport", "support_rho", "support_p_l"))],
        "component_assignment_rows": len(components), "component_unique_points": len(counts),
        "component_max_rows_per_point": int(counts.max()),
        "component_repeated_full_tensor_max_abs_error": float(np.abs(repeated_error).max()),
        "component_names": sorted(components.component.unique().tolist()),
        "end_of_domain_max_abs_source_channel": float(edge[CHANNELS].abs().to_numpy().max()),
        "artifact_hash_failures": sum(item["hash_matches"] is False for item in hashes),
        "regeneration_max_abs_error": max(r["max_abs_channel_error"] for r in regenerated),
        "support_coefficients_sha256": sha256_file(coeff_path),
    }
    return summary, hashes, regenerated, tail_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=ROOT / "supporting_reports/data/le_boundary_preflight")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be positive")
    args.outdir.mkdir(parents=True, exist_ok=True)
    fixtures = fixture_audit()
    if args.jobs == 1:
        results = [audit_surface(label) for label in SURFACES]
    else:
        with ProcessPoolExecutor(max_workers=min(args.jobs, len(SURFACES))) as pool:
            results = list(pool.map(audit_surface, SURFACES))
    summaries = [result[0] for result in results]
    parameter_differences = {key: [summaries[0]["params"].get(key), summaries[1]["params"].get(key)]
                             for key in set(summaries[0]["params"]) | set(summaries[1]["params"])
                             if summaries[0]["params"].get(key) != summaries[1]["params"].get(key)}
    for summary in summaries:
        del summary["params"]
    payload = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "script_sha256": sha256_file(Path(__file__)),
        "legacy_classifier_sha256": sha256_file(ROOT / "toolkit/adm_harness_cli/adm_harness/endpoint_j_source_class_screen.py"),
        "command": " ".join(sys.argv),
        "requested_jobs": args.jobs, "surface_workers": min(args.jobs, len(SURFACES)),
        "classifier_fixture_count": len(fixtures), "classifier_fixture_failures": int((~fixtures.fixture_pass).sum()),
        "classifier_type_failures": int((~fixtures.type_pass).sum()),
        "classifier_rest_frame_failures": int((~fixtures.rest_frame_pass).sum()),
        "same_source_parameters": not parameter_differences, "source_parameter_differences": parameter_differences,
        "same_tensor_difference_steps": all(summaries[0]["grid"][key] == summaries[1]["grid"][key] for key in ["h_s", "h_l"]),
        "checks": {
            "legacy_classifier_analytic_fixtures_pass": bool(fixtures.fixture_pass.all()),
            "source_inputs_and_sample_regeneration_pass": all(s["artifact_hash_failures"] == 0 and s["regeneration_max_abs_error"] < 1e-9 and s["source_module_sha_matches_manifest"] for s in summaries),
            "endpoint_covariant_tensor_identity_pass": all(s["medium_projection_max_abs_error"] < 1e-9 for s in summaries),
            "intermediate_reconstructs_its_declared_subset": all(s["intermediate_reconstruction_max_abs_error"] < 1e-9 for s in summaries),
            "intermediate_covers_entire_source_grid": all(s["intermediate_unique_points"] == s["ledger_rows"] for s in summaries),
        },
        "surfaces": summaries,
    }
    (args.outdir / "preflight.json").write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    fixtures.to_csv(args.outdir / "classifier_fixtures.csv", index=False)
    pd.DataFrame([r for result in results for r in result[1]]).to_csv(args.outdir / "artifact_hashes.csv", index=False)
    pd.DataFrame([r for result in results for r in result[2]]).to_csv(args.outdir / "metric_regeneration.csv", index=False)
    pd.DataFrame([r for result in results for r in result[3]]).to_csv(args.outdir / "exterior_samples.csv", index=False)
    print(json.dumps({"classifier_fixture_failures": payload["classifier_fixture_failures"],
                      "surfaces": summaries, "outputs": str(args.outdir)}, indent=2))


if __name__ == "__main__":
    main()
