from __future__ import annotations

import json
import math
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .source_ledger import sha256_file, write_manifest


EPS = 1.0e-30


def _token(value: float) -> str:
    text = f"{float(value):.10g}"
    return text.replace("-", "m").replace("+", "").replace(".", "p").replace("e", "e")


def service_label(value: float) -> str:
    number = float(value)
    if number.is_integer():
        return f"v{int(number)}"
    return f"v{_token(number)}"


@dataclass(frozen=True)
class Moderate3P1SurfaceSpec:
    label: str
    mesh: str
    role: str
    service_rating: float
    covariant_dir: Path
    total_closure_dir: Path


def default_moderate_v5_surfaces() -> tuple[Moderate3P1SurfaceSpec, ...]:
    baseline_root = Path("toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15")
    dense_root = Path("toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12")
    return (
        Moderate3P1SurfaceSpec(
            "sealed_baseline_v5",
            "baseline",
            "reference_baseline",
            5.0,
            baseline_root / "endpoint_medium_covariant_audit_freeze_rematch_w6_t1p5",
            baseline_root / "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5",
        ),
        Moderate3P1SurfaceSpec(
            "sealed_dense_v5",
            "dense",
            "main_dense",
            5.0,
            dense_root / "endpoint_medium_covariant_audit_freeze_rematch_w6_t1p5",
            dense_root / "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5",
        ),
    )


@dataclass(frozen=True)
class Moderate3P1ScenarioSpec:
    scenario_id: str
    m1_fraction: float
    m2_fraction: float
    m4_fraction: float
    metric_feedback_gain: float
    boost_margin_fraction: float
    source_scale: float
    read: str


def default_moderate_scenarios() -> tuple[Moderate3P1ScenarioSpec, ...]:
    return (
        Moderate3P1ScenarioSpec(
            "scheduled_axisymmetric",
            0.0,
            0.0,
            0.0,
            0.015,
            0.08,
            1.0,
            "properly scheduled axisymmetric evolution with mild metric feedback",
        ),
        Moderate3P1ScenarioSpec(
            "m1_offaxis_tilt",
            0.035,
            0.0,
            0.0,
            0.030,
            0.10,
            1.0,
            "dipole off-axis transport stress",
        ),
        Moderate3P1ScenarioSpec(
            "m2_shear_feedback",
            0.0,
            0.045,
            0.0,
            0.045,
            0.14,
            1.0,
            "quadrupole shear with source-support feedback",
        ),
        Moderate3P1ScenarioSpec(
            "mixed_offaxis_backreaction",
            0.035,
            0.040,
            0.015,
            0.060,
            0.18,
            1.0,
            "combined angular/off-axis and metric-response stress",
        ),
    )


@dataclass(frozen=True)
class Moderate3P1Inputs:
    first_order_dir: Path
    energy_constant_dir: Path
    surfaces: tuple[Moderate3P1SurfaceSpec, ...] = field(default_factory=default_moderate_v5_surfaces)
    scenarios: tuple[Moderate3P1ScenarioSpec, ...] = field(default_factory=default_moderate_scenarios)


@dataclass(frozen=True)
class Moderate3P1Spec:
    expected_service_rating: float = 5.0
    service_label: str = "v5"
    require_reference_surface: bool = True
    n_phi: int = 24
    n_steps: int = 64
    time_chunk_steps: int = 4
    damping: float = 0.965
    source_width: float = 0.115
    source_floor: float = 0.080
    active_driver_gate: float = 0.55
    peak_driver_concentration_gate: float = 1.75
    local_pf_gate: float = 0.55
    live_driver_fraction_gate: float = 0.005
    outside_driver_fraction_gate: float = 0.006
    live_support_tail_fraction_gate: float = 0.0001
    support_tail_fraction_gate: float = 0.001
    cone_margin_gate: float = 0.0
    cone_margin_watch: float = 0.02
    state_amplification_gate: float = 1.000000001
    feedback_multiplier_gate: float = 1.08
    top_rows_per_surface_scenario: int = 120
    workers: int = 4


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _truth(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if not math.isfinite(number):
        return default
    return number


def _bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin({"1", "true", "yes", "y"})


def _safe_ratio(num: float, denom: float) -> float:
    return float(num / denom) if denom > 0.0 else float("nan")


def _surface_paths(surface: Moderate3P1SurfaceSpec) -> dict[str, Path]:
    return {
        "point_closure": surface.total_closure_dir / "endpoint_support_total_closure_point_closure.csv",
        "closure_decision": surface.total_closure_dir / "endpoint_support_total_closure_decision.csv",
        "closure_manifest": surface.total_closure_dir / "endpoint_support_total_closure_manifest.json",
        "covariant_decision": surface.covariant_dir / "endpoint_medium_covariant_decision.csv",
        "covariant_manifest": surface.covariant_dir / "endpoint_medium_covariant_manifest.json",
    }


def _manifest_sha_ok(manifest: dict[str, Any], key: str, path: Path) -> bool:
    recorded = manifest.get("sha256", {}).get(key)
    if not recorded:
        return False
    return str(recorded) == sha256_file(path)


def _stage_centers(stages: pd.Series, s_values: pd.Series) -> np.ndarray:
    centers = {
        "pre_entry_setup": 0.10,
        "entry_precatch": 0.22,
        "catch_rematch": 0.36,
        "held_carry": 0.50,
        "release_shift_fade": 0.66,
        "post_release_buffer": 0.80,
        "reset_decompression": 0.91,
    }
    stage_center = stages.astype(str).map(centers)
    if stage_center.isna().any():
        s = s_values.astype(float)
        s_min = float(s.min()) if len(s) else -1.0
        s_max = float(s.max()) if len(s) else 1.0
        scaled = (s - s_min) / max(s_max - s_min, EPS)
        stage_center = stage_center.fillna(scaled.clip(0.05, 0.95))
    return stage_center.astype(float).to_numpy()


def _angular_weights(scenario: Moderate3P1ScenarioSpec, n_phi: int) -> tuple[np.ndarray, np.ndarray]:
    phi = np.linspace(0.0, 2.0 * math.pi, int(n_phi), endpoint=False, dtype=np.float64)
    weights = (
        1.0
        + scenario.m1_fraction * np.cos(phi)
        + scenario.m2_fraction * np.cos(2.0 * phi)
        + scenario.m4_fraction * np.sin(4.0 * phi)
    )
    weights = np.clip(weights, 0.0, None)
    weights *= float(n_phi) / max(float(weights.sum()), EPS)
    return phi, weights


def _read_surface(surface: Moderate3P1SurfaceSpec) -> tuple[pd.DataFrame, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    paths = _surface_paths(surface)
    point = _read_csv(paths["point_closure"])
    active = _bool_series(point["medium_source_active"]) if "medium_source_active" in point else pd.Series(True, index=point.index)
    live = _bool_series(point["covariant_divergence_live"]) if "covariant_divergence_live" in point else pd.Series(False, index=point.index)
    allowed = _bool_series(point["covariant_exchange_allowed_mask"]) if "covariant_exchange_allowed_mask" in point else pd.Series(True, index=point.index)
    active_nonlive = active & (~live)
    outside_nonlive = (~allowed) & (~live)
    return point, active, live, allowed, active_nonlive, outside_nonlive


def _surface_input_audit(surface: Moderate3P1SurfaceSpec) -> dict[str, Any]:
    paths = _surface_paths(surface)
    point, active, live, allowed, active_nonlive, outside_nonlive = _read_surface(surface)
    closure_decision = _read_csv(paths["closure_decision"]).iloc[0]
    covariant_decision = _read_csv(paths["covariant_decision"]).iloc[0]
    closure_manifest = _read_json(paths["closure_manifest"])
    covariant_manifest = _read_json(paths["covariant_manifest"])
    closure_point_sha_ok = _manifest_sha_ok(closure_manifest, "point_closure", paths["point_closure"])
    closure_decision_sha_ok = _manifest_sha_ok(closure_manifest, "decision", paths["closure_decision"])
    covariant_decision_sha_ok = _manifest_sha_ok(covariant_manifest, "decision", paths["covariant_decision"])
    return {
        "label": surface.label,
        "mesh": surface.mesh,
        "role": surface.role,
        "service_rating": surface.service_rating,
        "point_rows": int(len(point)),
        "active_nonlive_rows": int(active_nonlive.sum()),
        "live_rows": int(live.sum()),
        "allowed_nonlive_rows": int((allowed & (~live)).sum()),
        "outside_nonlive_rows": int(outside_nonlive.sum()),
        "closure_point_sha_ok": bool(closure_point_sha_ok),
        "closure_decision_sha_ok": bool(closure_decision_sha_ok),
        "covariant_decision_sha_ok": bool(covariant_decision_sha_ok),
        "support_total_closure_pass": _truth(closure_decision["passes_support_total_closure"]),
        "covariant_identity_pass": _truth(covariant_decision["passes_covariant_identity_audit"]),
        "projection_reconstruction_pass": _truth(covariant_decision["projection_reconstruction_pass"]),
        "boost_subluminal_pass": _truth(covariant_decision["boost_subluminal_pass"]),
        "mixed_eigen_real_pass": _truth(covariant_decision["mixed_eigen_real_pass"]),
        "exchange_localization_pass": _truth(covariant_decision["exchange_localization_pass"]),
        "max_abs_boost_velocity": _finite(covariant_decision["max_abs_boost_velocity"], float("nan")),
        "inherited_local_pf_ratio": _finite(closure_decision["local_max_closure_residual_to_target_abs_PF_ratio"], float("nan")),
        "inherited_outside_support_tail_fraction": _finite(closure_decision["outside_support_tail_fraction"], float("nan")),
        "inherited_live_support_tail_fraction": _finite(closure_decision["live_support_tail_fraction"], float("nan")),
        "point_closure_path": str(paths["point_closure"]),
        "closure_decision_path": str(paths["closure_decision"]),
        "covariant_decision_path": str(paths["covariant_decision"]),
        "point_closure_sha256": sha256_file(paths["point_closure"]),
        "closure_decision_sha256": sha256_file(paths["closure_decision"]),
        "covariant_decision_sha256": sha256_file(paths["covariant_decision"]),
    }


def _base_arrays(surface: Moderate3P1SurfaceSpec) -> tuple[pd.DataFrame, dict[str, Any]]:
    paths = _surface_paths(surface)
    point, active, live, allowed, active_nonlive, outside_nonlive = _read_surface(surface)
    closure_decision = _read_csv(paths["closure_decision"]).iloc[0]
    covariant_decision = _read_csv(paths["covariant_decision"]).iloc[0]
    selected = point.loc[active_nonlive].copy().reset_index(names="source_row_index")
    selected["outside_nonlive"] = outside_nonlive.loc[active_nonlive].to_numpy()
    selected["live_evolved"] = False

    full_endpoint = float(point["endpoint_exchange_l2_density_volume"].fillna(0.0).astype(float).sum())
    active_endpoint = float(point.loc[active_nonlive, "endpoint_exchange_l2_density_volume"].fillna(0.0).astype(float).sum())
    active_source = (
        float(point.loc[active_nonlive, "source_abs_volume"].fillna(0.0).astype(float).sum())
        if "source_abs_volume" in point
        else float(point.loc[active_nonlive, "source_abs_density"].fillna(0.0).astype(float).sum())
    )
    inherited_live_driver = float(point.loc[live, "total_closure_residual_l2_density_volume"].fillna(0.0).astype(float).sum())
    inherited_outside_driver = float(point.loc[outside_nonlive, "total_closure_residual_l2_density_volume"].fillna(0.0).astype(float).sum())
    meta = {
        "full_endpoint_exchange_l2_volume": full_endpoint,
        "active_endpoint_exchange_l2_volume": active_endpoint,
        "active_source_abs_volume": active_source,
        "inherited_live_driver_fraction_of_full_endpoint": _safe_ratio(inherited_live_driver, full_endpoint),
        "inherited_outside_driver_fraction_of_full_endpoint": _safe_ratio(inherited_outside_driver, full_endpoint),
        "inherited_local_pf_ratio": _finite(closure_decision["local_max_closure_residual_to_target_abs_PF_ratio"], float("nan")),
        "inherited_outside_support_tail_fraction": _finite(closure_decision["outside_support_tail_fraction"], float("nan")),
        "inherited_live_support_tail_fraction": _finite(closure_decision["live_support_tail_fraction"], float("nan")),
        "inherited_max_boost_velocity": _finite(covariant_decision["max_abs_boost_velocity"], float("nan")),
    }
    return selected, meta


def _schedule_matrix(base: pd.DataFrame, spec: Moderate3P1Spec) -> np.ndarray:
    centers = _stage_centers(base["stage"], base["s"])
    times = (np.arange(int(spec.n_steps), dtype=np.float64) + 0.5) / float(spec.n_steps)
    raw = spec.source_floor + np.exp(-0.5 * ((times[None, :] - centers[:, None]) / float(spec.source_width)) ** 2)
    raw /= np.maximum(raw.mean(axis=1, keepdims=True), EPS)
    return raw.astype(np.float32)


def _chunk_table(payload: dict[str, Any]) -> pa.Table:
    return pa.Table.from_pydict(payload)


def _run_surface_scenario(args: tuple[Moderate3P1SurfaceSpec, Moderate3P1ScenarioSpec, Moderate3P1Spec, str]) -> tuple[dict[str, Any], pd.DataFrame, str]:
    surface, scenario, spec, outdir_text = args
    outdir = Path(outdir_text)
    response_dir = outdir / "time_response"
    response_dir.mkdir(parents=True, exist_ok=True)
    base, meta = _base_arrays(surface)
    n_rows = int(len(base))
    n_phi = int(spec.n_phi)
    n_steps = int(spec.n_steps)
    phi, angular = _angular_weights(scenario, n_phi)
    schedule = _schedule_matrix(base, spec)

    base_driver = base["total_closure_residual_l2_density_volume"].fillna(0.0).astype(float).to_numpy()
    endpoint = base["endpoint_exchange_l2_density_volume"].fillna(0.0).astype(float).to_numpy()
    source_abs = (
        base["source_abs_volume"].fillna(0.0).astype(float).to_numpy()
        if "source_abs_volume" in base
        else base["source_abs_density"].fillna(0.0).astype(float).to_numpy()
    )
    boost = base["medium_frame_abs_boost_velocity"].fillna(meta["inherited_max_boost_velocity"]).astype(float).to_numpy()
    outside = base["outside_nonlive"].astype(bool).to_numpy()
    row_index = base["source_row_index"].astype(np.int32).to_numpy()
    s_values = base["s"].astype(np.float32).to_numpy()
    l_values = base["l"].astype(np.float32).to_numpy()

    state = np.zeros((n_rows, n_phi), dtype=np.float64)
    cumulative_abs = np.zeros((n_rows, n_phi), dtype=np.float64)
    row_peak_driver = np.zeros(n_rows, dtype=np.float64)
    row_peak_state = np.zeros(n_rows, dtype=np.float64)
    row_peak_state_ratio = np.zeros(n_rows, dtype=np.float64)
    row_min_cone = np.full(n_rows, np.inf, dtype=np.float64)
    max_driver_ratio = 0.0
    mean_driver_volume = 0.0
    max_outside_fraction = 0.0
    max_state_ratio = 0.0
    max_feedback = 1.0
    min_cone = float("inf")
    peak_time_index = 0
    peak_phi_index = 0
    response_rows = 0

    parquet_path = response_dir / f"beta075_moderate_3p1_{surface.label}_{scenario.scenario_id}.parquet"
    writer: pq.ParquetWriter | None = None
    try:
        for start in range(0, n_steps, int(spec.time_chunk_steps)):
            stop = min(n_steps, start + int(spec.time_chunk_steps))
            chunk_payload: dict[str, list[np.ndarray]] = {
                "source_row_index": [],
                "time_index": [],
                "phi_index": [],
                "time_fraction": [],
                "phi": [],
                "s": [],
                "l": [],
                "angular_weight": [],
                "schedule_weight": [],
                "base_driver_volume": [],
                "instantaneous_driver_volume": [],
                "constraint_state_volume": [],
                "cumulative_injected_abs_volume": [],
                "state_to_cumulative_abs_ratio": [],
                "feedback_multiplier": [],
                "boost_velocity_proxy": [],
                "cone_margin_proxy": [],
                "endpoint_exchange_l2_volume": [],
                "source_abs_volume": [],
                "outside_nonlive": [],
                "live_evolved": [],
            }
            for t in range(start, stop):
                state_norm = np.minimum(np.abs(state) / (cumulative_abs + base_driver[:, None] + EPS), 1.0)
                feedback = 1.0 + float(scenario.metric_feedback_gain) * state_norm
                injection = (
                    base_driver[:, None]
                    * float(scenario.source_scale)
                    * schedule[:, t][:, None]
                    * angular[None, :]
                    * feedback
                )
                cumulative_abs = float(spec.damping) * cumulative_abs + np.abs(injection)
                state = float(spec.damping) * state + injection
                state_ratio = np.abs(state) / (cumulative_abs + EPS)
                state_util = np.minimum(state_ratio, 1.0)
                boost_proxy = (
                    boost[:, None]
                    + float(scenario.boost_margin_fraction) * (1.0 - boost[:, None])
                    + 0.0015 * float(scenario.metric_feedback_gain) * state_util
                )
                cone = 1.0 - boost_proxy

                driver_by_row = injection.max(axis=1)
                state_by_row = np.abs(state).max(axis=1)
                state_ratio_by_row = state_ratio.max(axis=1)
                cone_by_row = cone.min(axis=1)
                row_peak_driver = np.maximum(row_peak_driver, driver_by_row)
                row_peak_state = np.maximum(row_peak_state, state_by_row)
                row_peak_state_ratio = np.maximum(row_peak_state_ratio, state_ratio_by_row)
                row_min_cone = np.minimum(row_min_cone, cone_by_row)

                active_driver = float(injection.sum() / float(n_phi))
                outside_driver = float(injection[outside, :].sum() / float(n_phi)) if outside.any() else 0.0
                ratio = _safe_ratio(active_driver, meta["active_endpoint_exchange_l2_volume"])
                if ratio > max_driver_ratio:
                    max_driver_ratio = ratio
                    peak_time_index = int(t)
                    peak_phi_index = int(np.argmax(injection.sum(axis=0)))
                mean_driver_volume += active_driver / float(n_steps)
                max_outside_fraction = max(max_outside_fraction, _safe_ratio(outside_driver, meta["full_endpoint_exchange_l2_volume"]))
                max_state_ratio = max(max_state_ratio, float(state_ratio.max()))
                max_feedback = max(max_feedback, float(feedback.max()))
                min_cone = min(min_cone, float(cone.min()))

                count = n_rows * n_phi
                chunk_payload["source_row_index"].append(np.repeat(row_index, n_phi))
                chunk_payload["time_index"].append(np.repeat(np.int16(t), count))
                chunk_payload["phi_index"].append(np.tile(np.arange(n_phi, dtype=np.int16), n_rows))
                chunk_payload["time_fraction"].append(np.repeat(np.float32((t + 0.5) / float(n_steps)), count))
                chunk_payload["phi"].append(np.tile(phi.astype(np.float32), n_rows))
                chunk_payload["s"].append(np.repeat(s_values, n_phi))
                chunk_payload["l"].append(np.repeat(l_values, n_phi))
                chunk_payload["angular_weight"].append(np.tile(angular.astype(np.float32), n_rows))
                chunk_payload["schedule_weight"].append(np.repeat(schedule[:, t].astype(np.float32), n_phi))
                chunk_payload["base_driver_volume"].append(np.repeat(base_driver, n_phi))
                chunk_payload["instantaneous_driver_volume"].append(injection.reshape(-1))
                chunk_payload["constraint_state_volume"].append(state.reshape(-1))
                chunk_payload["cumulative_injected_abs_volume"].append(cumulative_abs.reshape(-1))
                chunk_payload["state_to_cumulative_abs_ratio"].append(state_ratio.astype(np.float32).reshape(-1))
                chunk_payload["feedback_multiplier"].append(feedback.astype(np.float32).reshape(-1))
                chunk_payload["boost_velocity_proxy"].append(boost_proxy.astype(np.float32).reshape(-1))
                chunk_payload["cone_margin_proxy"].append(cone.astype(np.float32).reshape(-1))
                chunk_payload["endpoint_exchange_l2_volume"].append(np.repeat(endpoint, n_phi))
                chunk_payload["source_abs_volume"].append(np.repeat(source_abs, n_phi))
                chunk_payload["outside_nonlive"].append(np.repeat(outside, n_phi))
                chunk_payload["live_evolved"].append(np.repeat(False, count))
                response_rows += count

            table_payload = {key: np.concatenate(parts) for key, parts in chunk_payload.items()}
            table = _chunk_table(table_payload)
            if writer is None:
                writer = pq.ParquetWriter(parquet_path, table.schema, compression="zstd")
            writer.write_table(table)
    finally:
        if writer is not None:
            writer.close()

    top_count = min(int(spec.top_rows_per_surface_scenario), n_rows)
    top_index = np.argsort(row_peak_driver)[-top_count:][::-1]
    top_rows = base.iloc[top_index][[
        col for col in ("source_row_index", "case", "s", "l", "stage", "region", "assignment")
        if col in base.columns
    ]].copy()
    top_rows["surface_label"] = surface.label
    top_rows["scenario_id"] = scenario.scenario_id
    top_rows["peak_instantaneous_driver_volume"] = row_peak_driver[top_index]
    top_rows["peak_constraint_state_volume"] = row_peak_state[top_index]
    top_rows["peak_state_to_cumulative_abs_ratio"] = row_peak_state_ratio[top_index]
    top_rows["min_cone_margin_proxy"] = row_min_cone[top_index]

    summary = {
        "label": surface.label,
        "mesh": surface.mesh,
        "role": surface.role,
        "service_rating": surface.service_rating,
        "scenario_id": scenario.scenario_id,
        "n_phi": n_phi,
        "n_steps": n_steps,
        "active_nonlive_rows_evolved": n_rows,
        "live_rows_evolved": 0,
        "limiter_clipping_used": False,
        "response_rows_written": response_rows,
        "parquet_path": str(parquet_path),
        "active_endpoint_exchange_l2_volume": meta["active_endpoint_exchange_l2_volume"],
        "full_endpoint_exchange_l2_volume": meta["full_endpoint_exchange_l2_volume"],
        "active_source_abs_volume": meta["active_source_abs_volume"],
        "mean_driver_to_endpoint_ratio": _safe_ratio(mean_driver_volume, meta["active_endpoint_exchange_l2_volume"]),
        "peak_instantaneous_driver_to_endpoint_ratio": max_driver_ratio,
        "outside_driver_fraction_of_full_endpoint": max_outside_fraction,
        "inherited_live_driver_fraction_of_full_endpoint": meta["inherited_live_driver_fraction_of_full_endpoint"],
        "inherited_outside_driver_fraction_of_full_endpoint": meta["inherited_outside_driver_fraction_of_full_endpoint"],
        "max_state_to_cumulative_abs_ratio": max_state_ratio,
        "max_feedback_multiplier": max_feedback,
        "min_cone_margin_proxy": min_cone,
        "peak_time_index": peak_time_index,
        "peak_phi_index": peak_phi_index,
        "angular_peak_weight": float(angular.max()),
        "angular_min_weight": float(angular.min()),
        "angular_weight_mean": float(angular.mean()),
        "inherited_local_pf_ratio": meta["inherited_local_pf_ratio"],
        "inherited_outside_support_tail_fraction": meta["inherited_outside_support_tail_fraction"],
        "inherited_live_support_tail_fraction": meta["inherited_live_support_tail_fraction"],
        "inherited_max_boost_velocity": meta["inherited_max_boost_velocity"],
    }
    return summary, top_rows, str(parquet_path)


def _scenario_catalog(scenarios: tuple[Moderate3P1ScenarioSpec, ...]) -> pd.DataFrame:
    return pd.DataFrame([scenario.__dict__ for scenario in scenarios])


def _surface_catalog(surfaces: tuple[Moderate3P1SurfaceSpec, ...]) -> pd.DataFrame:
    return pd.DataFrame([
        {
            "label": surface.label,
            "mesh": surface.mesh,
            "role": surface.role,
            "service_rating": surface.service_rating,
            "covariant_dir": str(surface.covariant_dir),
            "total_closure_dir": str(surface.total_closure_dir),
        }
        for surface in surfaces
    ])


def _stability(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for scenario_id, group in summary.groupby("scenario_id", sort=False):
        dense = group.loc[group["role"].astype(str).eq("main_dense")]
        if not len(dense):
            dense = group.head(1)
        dense_row = dense.iloc[0]
        for _, row in group.iterrows():
            rows.append({
                "scenario_id": str(scenario_id),
                "label": str(row["label"]),
                "role": str(row["role"]),
                "reference_label": str(dense_row["label"]),
                "peak_driver_ratio_delta_from_dense": _finite(row["peak_instantaneous_driver_to_endpoint_ratio"], float("nan"))
                - _finite(dense_row["peak_instantaneous_driver_to_endpoint_ratio"], float("nan")),
                "mean_driver_ratio_delta_from_dense": _finite(row["mean_driver_to_endpoint_ratio"], float("nan"))
                - _finite(dense_row["mean_driver_to_endpoint_ratio"], float("nan")),
                "cone_margin_delta_from_dense": _finite(row["min_cone_margin_proxy"], float("nan"))
                - _finite(dense_row["min_cone_margin_proxy"], float("nan")),
            })
    return pd.DataFrame(rows)


def _gates(
    input_audit: pd.DataFrame,
    summary: pd.DataFrame,
    stability: pd.DataFrame,
    first_order_decision: pd.DataFrame,
    energy_decision: pd.DataFrame,
    spec: Moderate3P1Spec,
) -> pd.DataFrame:
    first = first_order_decision.iloc[0]
    energy = energy_decision.iloc[0]
    services = sorted(float(v) for v in input_audit["service_rating"].unique())
    expected_services = [float(spec.expected_service_rating)]
    all_manifest_ok = bool(
        input_audit["closure_point_sha_ok"].all()
        and input_audit["closure_decision_sha_ok"].all()
        and input_audit["covariant_decision_sha_ok"].all()
    )
    all_source_ladder_pass = bool(
        input_audit["support_total_closure_pass"].all()
        and input_audit["covariant_identity_pass"].all()
        and input_audit["projection_reconstruction_pass"].all()
        and input_audit["boost_subluminal_pass"].all()
        and input_audit["mixed_eigen_real_pass"].all()
        and input_audit["exchange_localization_pass"].all()
    )
    max_mean_driver = float(summary["mean_driver_to_endpoint_ratio"].astype(float).max())
    max_peak_driver = float(summary["peak_instantaneous_driver_to_endpoint_ratio"].astype(float).max())
    min_cone = float(summary["min_cone_margin_proxy"].astype(float).min())
    max_state_ratio = float(summary["max_state_to_cumulative_abs_ratio"].astype(float).max())
    max_feedback = float(summary["max_feedback_multiplier"].astype(float).max())
    max_live_evolved = int(summary["live_rows_evolved"].astype(int).max())
    limiter_used = bool(summary["limiter_clipping_used"].astype(bool).any())
    max_outside = float(summary["outside_driver_fraction_of_full_endpoint"].astype(float).max())
    max_live = float(summary["inherited_live_driver_fraction_of_full_endpoint"].astype(float).max())
    max_tail = float(summary["inherited_outside_support_tail_fraction"].astype(float).max())
    max_live_tail = float(summary["inherited_live_support_tail_fraction"].astype(float).max())
    max_local_pf = float(summary["inherited_local_pf_ratio"].astype(float).max())
    has_baseline = bool((input_audit["role"].astype(str) == "reference_baseline").any())
    has_dense = bool((input_audit["role"].astype(str) == "main_dense").any())
    reference_scope_pass = has_dense and (has_baseline or not bool(spec.require_reference_surface))
    return pd.DataFrame([
        {
            "gate": "sealed_service_input_scope",
            "status": "pass" if services == expected_services else "fail",
            "value": ",".join(f"{value:g}" for value in services),
            "gate_value": ",".join(f"{value:g}" for value in expected_services),
            "read": "moderate capstone starts from the requested sealed service-rating ladder only",
        },
        {
            "gate": "current_ladder_provenance_hashes",
            "status": "pass" if all_manifest_ok else "fail",
            "value": all_manifest_ok,
            "gate_value": True,
            "read": "input files match their current closure/covariant manifests",
        },
        {
            "gate": "full_service_source_family_ladder",
            "status": "pass" if all_source_ladder_pass else "fail",
            "value": all_source_ladder_pass,
            "gate_value": True,
            "read": "service-rating inputs inherit support closure, covariant identity, boost, eigenvalue, and localization passes",
        },
        {
            "gate": "first_order_3p1_handoff",
            "status": "pass" if _truth(first["hard_first_order_3p1_pass"]) else "fail",
            "value": str(first["first_order_3p1_status"]),
            "gate_value": "hard_first_order_3p1_pass",
            "read": "moderate capstone inherits the hard-clean first-order Bianchi/constraint handoff",
        },
        {
            "gate": "no_live_row_evolution",
            "status": "pass" if max_live_evolved == 0 else "fail",
            "value": max_live_evolved,
            "gate_value": 0,
            "read": "time stepping never evolves live rows to buy margin",
        },
        {
            "gate": "no_limiter_clipping",
            "status": "pass" if not limiter_used else "fail",
            "value": limiter_used,
            "gate_value": False,
            "read": "no limiter clipping is used inside the capstone evolution",
        },
        {
            "gate": "no_state_amplification",
            "status": "pass" if max_state_ratio <= spec.state_amplification_gate else "fail",
            "value": max_state_ratio,
            "gate_value": spec.state_amplification_gate,
            "read": "constraint-response state remains bounded by injected absolute source burden",
        },
        {
            "gate": "feedback_multiplier_bound",
            "status": "pass" if max_feedback <= spec.feedback_multiplier_gate else "fail",
            "value": max_feedback,
            "gate_value": spec.feedback_multiplier_gate,
            "read": "metric feedback remains a small response multiplier rather than a self-amplifying state",
        },
        {
            "gate": "scheduled_mean_driver_bound",
            "status": "watch" if max_mean_driver <= spec.active_driver_gate and max_mean_driver > 0.90 * spec.active_driver_gate else "pass" if max_mean_driver <= spec.active_driver_gate else "fail",
            "value": max_mean_driver,
            "gate_value": spec.active_driver_gate,
            "read": "time-averaged scheduled angular/backreaction driver remains below the active endpoint budget",
        },
        {
            "gate": "instantaneous_peak_concentration",
            "status": "watch" if max_peak_driver <= spec.peak_driver_concentration_gate and max_peak_driver > spec.active_driver_gate else "pass" if max_peak_driver <= spec.peak_driver_concentration_gate else "fail",
            "value": max_peak_driver,
            "gate_value": spec.peak_driver_concentration_gate,
            "read": "scheduled source peak is tracked as a concentration watch rather than compared to a static time-averaged budget",
        },
        {
            "gate": "cone_margin_proxy",
            "status": "watch" if min_cone > spec.cone_margin_gate and min_cone < spec.cone_margin_watch else "pass" if min_cone > spec.cone_margin_gate else "fail",
            "value": min_cone,
            "gate_value": spec.cone_margin_gate,
            "read": "boost/backreaction proxy remains subluminal with inherited thin margin",
        },
        {
            "gate": "live_and_offmask_localization",
            "status": "pass"
            if max_outside <= spec.outside_driver_fraction_gate
            and max_live <= spec.live_driver_fraction_gate
            and max_tail <= spec.support_tail_fraction_gate
            and max_live_tail <= spec.live_support_tail_fraction_gate
            else "fail",
            "value": f"outside={max_outside:.12g}; inherited_live={max_live:.12g}; support_tail={max_tail:.12g}; live_tail={max_live_tail:.12g}",
            "gate_value": f"outside<={spec.outside_driver_fraction_gate}; live<={spec.live_driver_fraction_gate}; support_tail<={spec.support_tail_fraction_gate}; live_tail<={spec.live_support_tail_fraction_gate}",
            "read": "moderate evolution preserves localization and does not lean on live support leakage",
        },
        {
            "gate": "inherited_reset_sector_pf_margin",
            "status": "watch" if max_local_pf <= spec.local_pf_gate and max_local_pf > 0.90 * spec.local_pf_gate else "pass" if max_local_pf <= spec.local_pf_gate else "fail",
            "value": max_local_pf,
            "gate_value": spec.local_pf_gate,
            "read": "reset-sector P/F closure remains the inherited local watch",
        },
        {
            "gate": "dense_reference_scope",
            "status": "pass" if reference_scope_pass else "fail",
            "value": f"baseline={has_baseline}; dense={has_dense}",
            "gate_value": f"dense=true; reference_required={bool(spec.require_reference_surface)}",
            "read": "sealed dense surface is the main article; a baseline reference is required only when configured",
        },
        {
            "gate": "energy_constant_watch_carried",
            "status": "watch" if _truth(energy["hard_constant_audit_pass"]) and _truth(energy["protective_buffer_watch"]) else "pass" if _truth(energy["hard_constant_audit_pass"]) else "fail",
            "value": _finite(energy["work_utilization"], float("nan")),
            "gate_value": "hard_constant_audit_pass",
            "read": "energy theorem constant remains carried as a watch from the formal source-family proof",
        },
    ])


def _decision(gates: pd.DataFrame, summary: pd.DataFrame, spec: Moderate3P1Spec) -> pd.DataFrame:
    fail_count = int((gates["status"].astype(str) == "fail").sum())
    watch_count = int((gates["status"].astype(str) == "watch").sum())
    hard_pass = fail_count == 0
    worst_driver = summary.loc[int(summary["peak_instantaneous_driver_to_endpoint_ratio"].astype(float).idxmax())]
    worst_cone = summary.loc[int(summary["min_cone_margin_proxy"].astype(float).idxmin())]
    status = (
        f"stage2_moderate_3p1_{spec.service_label}_capstone_watch_pass"
        if hard_pass and watch_count
        else f"stage2_moderate_3p1_{spec.service_label}_capstone_pass"
        if hard_pass
        else f"stage2_moderate_3p1_{spec.service_label}_capstone_fail"
    )
    return pd.DataFrame([{
        "capstone_status": status,
        "hard_capstone_pass": hard_pass,
        "failed_gate_count": fail_count,
        "watch_count": watch_count,
        "surface_count": int(summary["label"].nunique()),
        "scenario_count": int(summary["scenario_id"].nunique()),
        "time_response_rows": int(summary["response_rows_written"].astype(int).sum()),
        "worst_driver_surface": str(worst_driver["label"]),
        "worst_driver_scenario": str(worst_driver["scenario_id"]),
        "worst_peak_driver_to_endpoint_ratio": _finite(worst_driver["peak_instantaneous_driver_to_endpoint_ratio"], float("nan")),
        "worst_cone_surface": str(worst_cone["label"]),
        "worst_cone_scenario": str(worst_cone["scenario_id"]),
        "min_cone_margin_proxy": _finite(worst_cone["min_cone_margin_proxy"], float("nan")),
        "max_state_to_cumulative_abs_ratio": float(summary["max_state_to_cumulative_abs_ratio"].astype(float).max()),
        "max_feedback_multiplier": float(summary["max_feedback_multiplier"].astype(float).max()),
        "decision_read": (
            "moderate sealed-V5 3+1/backreaction capstone is hard-clean with inherited margin watches"
            if hard_pass and watch_count
            else "moderate sealed-V5 3+1/backreaction capstone is hard-clean without configured watches"
            if hard_pass
            else "moderate sealed-V5 3+1/backreaction capstone found at least one hard obstruction"
        ),
    }])


def run_moderate_3p1_v5_capstone(
    inputs: Moderate3P1Inputs,
    outdir: Path,
    *,
    spec: Moderate3P1Spec | None = None,
) -> dict[str, Path]:
    spec = spec or Moderate3P1Spec()
    outdir.mkdir(parents=True, exist_ok=True)
    first_order_decision = _read_csv(inputs.first_order_dir / "beta075_first_order_3p1_decision.csv")
    energy_decision = _read_csv(inputs.energy_constant_dir / "beta075_source_family_energy_constant_decision.csv")
    surface_catalog = _surface_catalog(inputs.surfaces)
    scenario_catalog = _scenario_catalog(inputs.scenarios)
    input_audit = pd.DataFrame([_surface_input_audit(surface) for surface in inputs.surfaces])

    tasks = [
        (surface, scenario, spec, str(outdir))
        for surface in inputs.surfaces
        for scenario in inputs.scenarios
    ]
    workers = max(1, min(int(spec.workers), len(tasks)))
    if workers == 1:
        results = [_run_surface_scenario(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(_run_surface_scenario, tasks))

    summary = pd.DataFrame([item[0] for item in results])
    top_rows = pd.concat([item[1] for item in results], ignore_index=True)
    parquet_parts = [item[2] for item in results]
    stability = _stability(summary)
    gates = _gates(input_audit, summary, stability, first_order_decision, energy_decision, spec)
    decision = _decision(gates, summary, spec)
    prefix = f"beta075_moderate_3p1_{spec.service_label}"

    paths = {
        "surface_catalog": outdir / f"{prefix}_surface_catalog.csv",
        "scenario_catalog": outdir / f"{prefix}_scenario_catalog.csv",
        "input_audit": outdir / f"{prefix}_input_audit.csv",
        "scenario_summary": outdir / f"{prefix}_scenario_summary.csv",
        "surface_stability": outdir / f"{prefix}_surface_stability.csv",
        "classification_gates": outdir / f"{prefix}_classification_gates.csv",
        "top_constraint_drivers": outdir / f"{prefix}_top_constraint_drivers.parquet",
        "decision": outdir / f"{prefix}_decision.csv",
    }
    surface_catalog.to_csv(paths["surface_catalog"], index=False)
    scenario_catalog.to_csv(paths["scenario_catalog"], index=False)
    input_audit.to_csv(paths["input_audit"], index=False)
    summary.to_csv(paths["scenario_summary"], index=False)
    stability.to_csv(paths["surface_stability"], index=False)
    gates.to_csv(paths["classification_gates"], index=False)
    top_rows.to_parquet(paths["top_constraint_drivers"], index=False, compression="zstd")
    decision.to_csv(paths["decision"], index=False)

    manifest_path = outdir / f"{prefix}_manifest.json"
    manifest_files = {key: str(path) for key, path in paths.items()}
    manifest_files["time_response_parts"] = parquet_parts
    input_paths: dict[str, str] = {
        "first_order_decision": str(inputs.first_order_dir / "beta075_first_order_3p1_decision.csv"),
        "energy_constant_decision": str(inputs.energy_constant_dir / "beta075_source_family_energy_constant_decision.csv"),
    }
    for surface in inputs.surfaces:
        for key, path in _surface_paths(surface).items():
            if path.exists():
                input_paths[f"{surface.label}:{key}"] = str(path)
    manifest = {
        "source_name": f"beta075_moderate_3p1_{spec.service_label}_capstone",
        "spec": spec.__dict__,
        "claim_boundary": (
            "Moderate local Stage II 3+1/backreaction capstone for one sealed service rating. "
            "It evolves current source-family closure data through scheduled angular/time response; "
            "it does not include any service rating without a full current ladder."
        ),
        "storage": "time-response and top-driver outputs are parquet; catalog, gate, summary, audit, and decision outputs are csv/json",
        "inputs": input_paths,
        "input_sha256": {key: sha256_file(Path(value)) for key, value in input_paths.items()},
        "files": manifest_files,
        "rows": {
            "surface_catalog": int(len(surface_catalog)),
            "scenario_catalog": int(len(scenario_catalog)),
            "input_audit": int(len(input_audit)),
            "scenario_summary": int(len(summary)),
            "surface_stability": int(len(stability)),
            "classification_gates": int(len(gates)),
            "top_constraint_drivers": int(len(top_rows)),
            "decision": int(len(decision)),
            "time_response": int(summary["response_rows_written"].astype(int).sum()),
        },
        "sha256": {key: sha256_file(path) for key, path in paths.items()},
        "time_response_sha256": {Path(path).name: sha256_file(Path(path)) for path in parquet_parts},
    }
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
