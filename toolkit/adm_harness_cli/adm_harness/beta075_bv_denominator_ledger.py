from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from .source_ledger import sha256_file, write_manifest


MEDIUM_SAFETY_FACTOR = 1.10
LOCAL_EXCHANGE_BOUND = 0.8
SUPPORT_CLOSURE_BOUND = 0.55
ENERGY_WORK_BOUND = 2.5


@dataclass(frozen=True)
class BVDenominatorLedgerInputs:
    baseline_admissibility: Path
    dense_admissibility: Path
    cross_surface_point_symbol: Path
    energy_point: Path
    geometric_anec_traces: Path
    residual_trimmed_anec_traces: Path


@dataclass(frozen=True)
class BVDenominatorLedgerSpec:
    max_workers: int = 6
    top_rows_per_metric: int = 80


def default_bv_denominator_inputs() -> BVDenominatorLedgerInputs:
    base = Path("toolkit/adm_harness_cli/runs")
    baseline_root = base / "beta_collar_generator_beta075_p003_mid_s15"
    dense_root = base / "beta_collar_generator_beta075_p003_mid_dense377x241_sharded12"
    return BVDenominatorLedgerInputs(
        baseline_admissibility=baseline_root
        / "endpoint_medium_admissibility_audit_freeze_rematch_w6_t1p5"
        / "endpoint_medium_admissibility_point_screen.csv",
        dense_admissibility=dense_root
        / "endpoint_medium_admissibility_audit_freeze_rematch_w6_t1p5"
        / "endpoint_medium_admissibility_point_screen.csv",
        cross_surface_point_symbol=base
        / "stage2_beta075_source_family_cross_surface_robustness"
        / "beta075_source_family_cross_surface_point_symbol.csv",
        energy_point=base
        / "stage2_beta075_source_family_energy_certificate"
        / "beta075_source_family_energy_point.csv",
        geometric_anec_traces=base
        / "finite_domain_anec_rematch_w6_t1p5_s15_parallel"
        / "finite_domain_anec_traces.parquet",
        residual_trimmed_anec_traces=base
        / "finite_domain_anec_rematch_w6_t1p5_s15_parallel_no_closure_no_live_trim"
        / "finite_domain_anec_traces.parquet",
    )


def _read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def _numeric(frame: pd.DataFrame, column: str, default: float = float("nan")) -> pd.Series:
    if column not in frame:
        return pd.Series(default, index=frame.index, dtype="float64")
    return pd.to_numeric(frame[column], errors="coerce")


def _bool_series(frame: pd.DataFrame, column: str, default: bool = False) -> pd.Series:
    if column not in frame:
        return pd.Series(default, index=frame.index, dtype="bool")
    series = frame[column]
    if series.dtype == bool:
        return series.fillna(default)
    return series.astype(str).str.lower().map({"true": True, "false": False}).fillna(default)


def _finite_quantile(series: pd.Series, q: float) -> float:
    finite = pd.to_numeric(series, errors="coerce").dropna()
    if finite.empty:
        return float("nan")
    return float(finite.quantile(q))


def _summary_row(
    *,
    table: str,
    metric: str,
    frame: pd.DataFrame,
    value_column: str,
    group: dict[str, Any],
    low_is_tight: bool,
) -> dict[str, Any]:
    series = pd.to_numeric(frame[value_column], errors="coerce")
    finite = series.dropna()
    row: dict[str, Any] = {
        "table": table,
        "metric": metric,
        "low_is_tight": bool(low_is_tight),
        "rows": int(len(frame)),
        "finite_rows": int(len(finite)),
        "min": float(finite.min()) if not finite.empty else float("nan"),
        "p01": _finite_quantile(finite, 0.01),
        "median": _finite_quantile(finite, 0.50),
        "p99": _finite_quantile(finite, 0.99),
        "max": float(finite.max()) if not finite.empty else float("nan"),
    }
    row.update(group)
    if finite.empty:
        row["tight_value"] = float("nan")
    elif low_is_tight:
        row["tight_value"] = row["min"]
    else:
        row["tight_value"] = row["max"]
    return row


def _summarize_metrics(
    frame: pd.DataFrame,
    *,
    table: str,
    metrics: list[tuple[str, str, bool]],
    group_columns: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    existing_groups = [column for column in group_columns if column in frame.columns]
    if existing_groups:
        grouped = frame.groupby(existing_groups, dropna=False)
        for keys, group in grouped:
            key_tuple = keys if isinstance(keys, tuple) else (keys,)
            group_values = dict(zip(existing_groups, key_tuple))
            for metric, column, low_is_tight in metrics:
                if column in group:
                    rows.append(
                        _summary_row(
                            table=table,
                            metric=metric,
                            frame=group,
                            value_column=column,
                            group=group_values,
                            low_is_tight=low_is_tight,
                        )
                    )
    for metric, column, low_is_tight in metrics:
        if column in frame:
            rows.append(
                _summary_row(
                    table=table,
                    metric=metric,
                    frame=frame,
                    value_column=column,
                    group={"summary_scope": "all"},
                    low_is_tight=low_is_tight,
                )
            )
    return pd.DataFrame(rows)


def _top_rows(
    frame: pd.DataFrame,
    *,
    table: str,
    metrics: list[tuple[str, str, bool]],
    n: int,
    columns: list[str],
) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for metric, column, low_is_tight in metrics:
        if column not in frame:
            continue
        keep_columns = [candidate for candidate in columns if candidate in frame.columns and candidate != column]
        working = frame[keep_columns + [column]].copy()
        working["_sort_value"] = pd.to_numeric(working[column], errors="coerce")
        working = working.dropna(subset=["_sort_value"])
        if working.empty:
            continue
        working = working.sort_values("_sort_value", ascending=low_is_tight).head(n)
        working.insert(0, "table", table)
        working.insert(1, "metric", metric)
        working.insert(2, "tight_value", working["_sort_value"].to_numpy())
        rows.append(working.drop(columns=["_sort_value"]))
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def _risk_tags(frame: pd.DataFrame, flag_columns: list[str]) -> pd.Series:
    tags: list[str] = []
    for _, row in frame[flag_columns].iterrows():
        active = [column for column in flag_columns if bool(row.get(column, False))]
        tags.append("|".join(active) if active else "none")
    return pd.Series(tags, index=frame.index)


def _process_medium(path: Path, mesh: str) -> dict[str, pd.DataFrame]:
    frame = _read_table(path)
    frame = frame.copy()
    frame.insert(0, "analysis_table", "medium_admissibility")
    frame["mesh"] = mesh
    heat_ratio = _numeric(frame, "regulated_heat_flux_ratio")
    frame["h_reg_linear"] = _numeric(frame, "transport_margin", 1.0 - heat_ratio)
    frame["h_reg_quadratic"] = 1.0 - heat_ratio.pow(2)
    frame["boost_headroom"] = 1.0 - _numeric(frame, "regulated_abs_boost_velocity").abs()
    frame["type_i_margin"] = _numeric(frame, "regulated_type_i_margin")
    frame["local_regulator_ratio"] = _numeric(frame, "regulator_to_local_source_abs_density")
    frame["decision_safety_factor_row"] = (
        (_numeric(frame, "regulator_safety_factor") - MEDIUM_SAFETY_FACTOR).abs() < 1.0e-9
    )
    frame["near_heat_boundary"] = heat_ratio >= 0.99
    frame["thin_transport_margin"] = frame["h_reg_linear"] <= 0.01
    frame["thin_type_i_margin"] = frame["type_i_margin"] <= 1.0e-7
    frame["thin_boost_headroom"] = frame["boost_headroom"] <= 0.02
    frame["order_one_local_regulator"] = frame["local_regulator_ratio"] >= 1.0
    frame["angular_inertia_negative_flag"] = _bool_series(frame, "angular_inertia_negative")
    frame["live_regulator_flag"] = _bool_series(frame, "inside_packet_live") & _bool_series(frame, "regulator_active")
    frame["type_iv_after_regulator_flag"] = frame.get("regulated_stress_algebraic_type", "").astype(str).str.contains("type_iv", na=False)
    frame["superluminal_or_undefined_boost_flag"] = _bool_series(frame, "boost_superluminal_or_nan")
    flag_columns = [
        "near_heat_boundary",
        "thin_transport_margin",
        "thin_type_i_margin",
        "thin_boost_headroom",
        "order_one_local_regulator",
        "angular_inertia_negative_flag",
        "live_regulator_flag",
        "type_iv_after_regulator_flag",
        "superluminal_or_undefined_boost_flag",
    ]
    frame["risk_tags"] = _risk_tags(frame, flag_columns)

    decision = frame[frame["decision_safety_factor_row"]].copy()
    metrics = [
        ("h_reg_linear", "h_reg_linear", True),
        ("h_reg_quadratic", "h_reg_quadratic", True),
        ("transport_margin", "transport_margin", True),
        ("type_i_margin", "type_i_margin", True),
        ("boost_headroom", "boost_headroom", True),
        ("regulated_heat_flux_ratio", "regulated_heat_flux_ratio", False),
        ("regulated_abs_boost_velocity", "regulated_abs_boost_velocity", False),
        ("local_regulator_ratio", "local_regulator_ratio", False),
        ("regulator_gradient_cost_density", "regulator_gradient_cost_density", False),
        ("rest_frame_angular_inertia_density", "rest_frame_angular_inertia_density", True),
    ]
    summary = _summarize_metrics(
        decision,
        table="medium_admissibility",
        metrics=metrics,
        group_columns=["mesh", "assignment", "stage", "region"],
    )
    top = _top_rows(
        decision,
        table="medium_admissibility",
        metrics=metrics,
        n=80,
        columns=[
            "mesh",
            "regulator_safety_factor",
            "point_index",
            "s",
            "l",
            "assignment",
            "stage",
            "region",
            "inside_packet_live",
            "regulated_heat_flux_ratio",
            "transport_margin",
            "h_reg_quadratic",
            "regulated_abs_boost_velocity",
            "boost_headroom",
            "regulated_type_i_margin",
            "local_regulator_ratio",
            "rest_frame_angular_inertia_density",
            "risk_tags",
        ],
    )
    gate = pd.DataFrame([
        {
            "table": "medium_admissibility",
            "mesh": mesh,
            "decision_safety_factor": MEDIUM_SAFETY_FACTOR,
            "decision_rows": int(len(decision)),
            "live_regulator_rows": int(decision["live_regulator_flag"].sum()),
            "post_regulator_type_iv_rows": int(decision["type_iv_after_regulator_flag"].sum()),
            "superluminal_or_undefined_boost_rows": int(decision["superluminal_or_undefined_boost_flag"].sum()),
            "near_heat_boundary_rows": int(decision["near_heat_boundary"].sum()),
            "order_one_local_regulator_rows": int(decision["order_one_local_regulator"].sum()),
            "angular_inertia_negative_rows": int(decision["angular_inertia_negative_flag"].sum()),
            "min_transport_margin": float(decision["h_reg_linear"].min()),
            "min_h_reg_quadratic": float(decision["h_reg_quadratic"].min()),
            "min_type_i_margin": float(decision["type_i_margin"].min()),
            "max_heat_flux_ratio": float(_numeric(decision, "regulated_heat_flux_ratio").max()),
            "max_abs_boost_velocity": float(_numeric(decision, "regulated_abs_boost_velocity").max()),
            "max_local_regulator_ratio": float(decision["local_regulator_ratio"].max()),
        }
    ])
    return {"medium_points": frame, "metric_summary": summary, "top_rows": top, "gate_summary": gate}


def _process_symbol(path: Path) -> dict[str, pd.DataFrame]:
    frame = _read_table(path)
    frame = frame.copy()
    frame.insert(0, "analysis_table", "source_family_point_symbol")
    frame["cone_margin"] = _numeric(frame, "relative_cone_margin")
    frame["cone_headroom"] = frame["cone_margin"]
    frame["local_P_headroom"] = LOCAL_EXCHANGE_BOUND - _numeric(frame, "operator_local_P_error")
    frame["local_F_headroom"] = LOCAL_EXCHANGE_BOUND - _numeric(frame, "operator_local_F_error")
    frame["local_exchange_error"] = pd.concat(
        [_numeric(frame, "operator_local_P_error"), _numeric(frame, "operator_local_F_error")],
        axis=1,
    ).max(axis=1)
    frame["local_exchange_headroom"] = LOCAL_EXCHANGE_BOUND - frame["local_exchange_error"]
    frame["thin_cone_margin"] = frame["cone_margin"] <= 1.0e-4
    frame["near_local_exchange_gate"] = frame["local_exchange_headroom"] <= 0.25
    frame["support_active"] = _bool_series(frame, "medium_source_active")
    frame["active_hard_symbol_failure"] = frame["support_active"] & ~_bool_series(frame, "hard_formal_symbol_pass", True)
    frame["live_support_flag"] = ~_bool_series(frame, "no_live_support_pass", True)
    flag_columns = ["thin_cone_margin", "near_local_exchange_gate", "live_support_flag"]
    frame["risk_tags"] = _risk_tags(frame, flag_columns)
    metrics = [
        ("cone_margin", "cone_margin", True),
        ("transport_margin", "transport_margin", True),
        ("transport_rapidity_abs", "transport_rapidity_abs", False),
        ("local_P_headroom", "local_P_headroom", True),
        ("local_F_headroom", "local_F_headroom", True),
        ("local_exchange_error", "local_exchange_error", False),
        ("operator_support_sound", "operator_support_sound", False),
    ]
    summary = _summarize_metrics(
        frame,
        table="source_family_point_symbol",
        metrics=metrics,
        group_columns=["label", "role", "assignment", "stage", "region"],
    )
    top = _top_rows(
        frame,
        table="source_family_point_symbol",
        metrics=metrics,
        n=80,
        columns=[
            "label",
            "mesh",
            "role",
            "s",
            "l",
            "assignment",
            "stage",
            "region",
            "medium_source_active",
            "relative_cone_margin",
            "transport_margin",
            "transport_rapidity_abs",
            "operator_local_P_error",
            "operator_local_F_error",
            "local_exchange_headroom",
            "risk_tags",
        ],
    )
    gate = (
        frame.groupby(["label", "role"], dropna=False)
        .agg(
            rows=("label", "size"),
            active_rows=("support_active", "sum"),
            active_hard_symbol_failures=("active_hard_symbol_failure", "sum"),
            live_support_flags=("live_support_flag", "sum"),
            thin_cone_rows=("thin_cone_margin", "sum"),
            min_cone_margin=("cone_margin", "min"),
            p01_cone_margin=("cone_margin", lambda s: _finite_quantile(s, 0.01)),
            max_transport_rapidity_abs=("transport_rapidity_abs", "max"),
            max_local_exchange_error=("local_exchange_error", "max"),
            min_local_exchange_headroom=("local_exchange_headroom", "min"),
        )
        .reset_index()
    )
    gate.insert(0, "table", "source_family_point_symbol")
    return {"symbol_points": frame, "metric_summary": summary, "top_rows": top, "gate_summary": gate}


def _process_energy(path: Path) -> dict[str, pd.DataFrame]:
    frame = _read_table(path)
    frame = frame.copy()
    frame.insert(0, "analysis_table", "source_family_energy_point")
    frame["energy_flux_headroom"] = _numeric(frame, "energy_flux_margin")
    frame["energy_work_headroom"] = ENERGY_WORK_BOUND - _numeric(frame, "energy_work_constant")
    frame["support_closure_headroom"] = SUPPORT_CLOSURE_BOUND - _numeric(frame, "support_total_closure_ratio")
    frame["local_exchange_headroom"] = LOCAL_EXCHANGE_BOUND - _numeric(frame, "local_exchange_shape")
    frame["thin_energy_flux"] = frame["energy_flux_headroom"] <= 1.0e-4
    frame["near_work_bound"] = frame["energy_work_headroom"] <= 0.5
    frame["near_support_closure_gate"] = frame["support_closure_headroom"] <= 0.01
    frame["near_local_exchange_gate"] = frame["local_exchange_headroom"] <= 0.25
    flag_columns = ["thin_energy_flux", "near_work_bound", "near_support_closure_gate", "near_local_exchange_gate"]
    frame["risk_tags"] = _risk_tags(frame, flag_columns)
    metrics = [
        ("energy_flux_headroom", "energy_flux_headroom", True),
        ("energy_work_headroom", "energy_work_headroom", True),
        ("support_closure_headroom", "support_closure_headroom", True),
        ("local_exchange_headroom", "local_exchange_headroom", True),
        ("energy_work_constant", "energy_work_constant", False),
        ("support_work_ratio", "support_work_ratio", False),
        ("support_total_closure_ratio", "support_total_closure_ratio", False),
        ("local_exchange_shape", "local_exchange_shape", False),
    ]
    summary = _summarize_metrics(
        frame,
        table="source_family_energy_point",
        metrics=metrics,
        group_columns=["label", "role", "assignment", "stage", "region"],
    )
    top = _top_rows(
        frame,
        table="source_family_energy_point",
        metrics=metrics,
        n=80,
        columns=[
            "label",
            "role",
            "assignment",
            "stage",
            "region",
            "energy_flux_margin",
            "energy_work_constant",
            "energy_work_headroom",
            "support_total_closure_ratio",
            "support_closure_headroom",
            "local_exchange_shape",
            "local_exchange_headroom",
            "risk_tags",
        ],
    )
    gate = (
        frame.groupby(["label", "role"], dropna=False)
        .agg(
            rows=("label", "size"),
            hard_energy_failures=("hard_energy_pass", lambda s: int((~s.astype(bool)).sum())),
            thin_energy_flux_rows=("thin_energy_flux", "sum"),
            near_work_bound_rows=("near_work_bound", "sum"),
            near_support_closure_gate_rows=("near_support_closure_gate", "sum"),
            min_energy_flux_margin=("energy_flux_headroom", "min"),
            max_energy_work_constant=("energy_work_constant", "max"),
            min_energy_work_headroom=("energy_work_headroom", "min"),
            max_support_total_closure_ratio=("support_total_closure_ratio", "max"),
            min_support_closure_headroom=("support_closure_headroom", "min"),
        )
        .reset_index()
    )
    gate.insert(0, "table", "source_family_energy_point")
    return {"energy_points": frame, "metric_summary": summary, "top_rows": top, "gate_summary": gate}


def _process_anec(path: Path, mode: str) -> dict[str, pd.DataFrame]:
    frame = _read_table(path)
    frame = frame.copy()
    frame.insert(0, "analysis_table", "finite_domain_anec_trace")
    frame["anec_mode"] = mode
    frame["negative_depth"] = (-_numeric(frame, "anec_total_integral")).clip(lower=0.0)
    frame["positive_depth"] = _numeric(frame, "anec_total_integral").clip(lower=0.0)
    for sector in [
        "sector_closure_residual",
        "live_handoff_trim",
        "infrastructure_angular_capacity",
        "infrastructure_radial_support",
        "reset_current_sink",
        "distributed_current_relaxation_H",
    ]:
        column = f"sector::{sector}::negative_part"
        frame[f"{sector}_negative_part"] = _numeric(frame, column, 0.0)
    frame["trace_touches_domain_boundary"] = (
        _bool_series(frame, "touches_s_lower")
        | _bool_series(frame, "touches_s_upper")
        | _bool_series(frame, "touches_l_lower")
        | _bool_series(frame, "touches_l_upper")
    )
    frame["anec_negative_flag"] = frame["negative_depth"] > 0.0
    frame["live_center_flag"] = _bool_series(frame, "center_inside_packet_live")
    metrics = [
        ("negative_depth", "negative_depth", False),
        ("anec_total_integral", "anec_total_integral", True),
        ("sector_closure_residual_negative_part", "sector_closure_residual_negative_part", False),
        ("live_handoff_trim_negative_part", "live_handoff_trim_negative_part", False),
        ("infrastructure_angular_capacity_negative_part", "infrastructure_angular_capacity_negative_part", False),
        ("trace_lambda_span", "trace_lambda_span", False),
    ]
    summary = _summarize_metrics(
        frame,
        table="finite_domain_anec_trace",
        metrics=metrics,
        group_columns=["anec_mode", "branch", "dominant_negative_sector", "center_stage", "center_region"],
    )
    top = _top_rows(
        frame,
        table="finite_domain_anec_trace",
        metrics=metrics,
        n=80,
        columns=[
            "anec_mode",
            "branch",
            "seed_point_index",
            "seed_sources",
            "center_s",
            "center_l",
            "center_stage",
            "center_region",
            "center_inside_packet_live",
            "anec_total_integral",
            "negative_depth",
            "anec_positive_part",
            "anec_negative_part",
            "dominant_negative_sector",
            "sector_closure_residual_negative_part",
            "live_handoff_trim_negative_part",
            "infrastructure_angular_capacity_negative_part",
            "trace_lambda_span",
        ],
    )
    gate = (
        frame.groupby(["anec_mode", "branch"], dropna=False)
        .agg(
            traces=("branch", "size"),
            negative_traces=("anec_negative_flag", "sum"),
            live_center_traces=("live_center_flag", "sum"),
            boundary_touching_traces=("trace_touches_domain_boundary", "sum"),
            worst_anec_total_integral=("anec_total_integral", "min"),
            p01_anec_total_integral=("anec_total_integral", lambda s: _finite_quantile(s, 0.01)),
            median_anec_total_integral=("anec_total_integral", "median"),
            max_negative_depth=("negative_depth", "max"),
            max_sector_closure_negative_part=("sector_closure_residual_negative_part", "max"),
            max_live_handoff_negative_part=("live_handoff_trim_negative_part", "max"),
            max_angular_capacity_negative_part=("infrastructure_angular_capacity_negative_part", "max"),
        )
        .reset_index()
    )
    gate.insert(0, "table", "finite_domain_anec_trace")
    return {"anec_traces": frame, "metric_summary": summary, "top_rows": top, "gate_summary": gate}


def _run_task(task: dict[str, Any]) -> dict[str, pd.DataFrame]:
    kind = task["kind"]
    path = Path(task["path"])
    if kind == "medium":
        return _process_medium(path, task["mesh"])
    if kind == "symbol":
        return _process_symbol(path)
    if kind == "energy":
        return _process_energy(path)
    if kind == "anec":
        return _process_anec(path, task["mode"])
    raise ValueError(f"unknown task kind: {kind}")


def _concat(results: list[dict[str, pd.DataFrame]], key: str) -> pd.DataFrame:
    frames = [result[key] for result in results if key in result and not result[key].empty]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def build_bv_denominator_ledger(
    inputs: BVDenominatorLedgerInputs,
    *,
    spec: BVDenominatorLedgerSpec | None = None,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    spec = spec or BVDenominatorLedgerSpec()
    tasks = [
        {"kind": "medium", "path": str(inputs.baseline_admissibility), "mesh": "baseline"},
        {"kind": "medium", "path": str(inputs.dense_admissibility), "mesh": "dense"},
        {"kind": "symbol", "path": str(inputs.cross_surface_point_symbol)},
        {"kind": "energy", "path": str(inputs.energy_point)},
        {"kind": "anec", "path": str(inputs.geometric_anec_traces), "mode": "geometric_total"},
        {"kind": "anec", "path": str(inputs.residual_trimmed_anec_traces), "mode": "residual_and_live_trim_removed"},
    ]
    workers = max(1, min(int(spec.max_workers), len(tasks)))
    results: list[dict[str, pd.DataFrame]] = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_run_task, task) for task in tasks]
        for future in as_completed(futures):
            results.append(future.result())

    outputs = {
        "medium_points": _concat(results, "medium_points"),
        "symbol_points": _concat(results, "symbol_points"),
        "energy_points": _concat(results, "energy_points"),
        "anec_traces": _concat(results, "anec_traces"),
        "metric_summary": _concat(results, "metric_summary"),
        "top_tight_rows": _concat(results, "top_rows"),
        "gate_summary": _concat(results, "gate_summary"),
    }
    input_paths = {
        "baseline_admissibility": inputs.baseline_admissibility,
        "dense_admissibility": inputs.dense_admissibility,
        "cross_surface_point_symbol": inputs.cross_surface_point_symbol,
        "energy_point": inputs.energy_point,
        "geometric_anec_traces": inputs.geometric_anec_traces,
        "residual_trimmed_anec_traces": inputs.residual_trimmed_anec_traces,
    }
    metadata = {
        "source_name": "beta075_bv_denominator_ledger",
        "workers": workers,
        "spec": spec.__dict__,
        "inputs": {key: str(path) for key, path in input_paths.items()},
        "input_sha256": {key: sha256_file(path) for key, path in input_paths.items()},
        "storage": "all tabular outputs are zstd parquet; manifest is json",
        "claim_boundary": (
            "Rail-specific Barcelo--Visser analogue boundedness ledger for the sealed beta075 source family. "
            "This computes denominator, transport, support-exchange, energy-work, and finite-domain ANEC margins "
            "from existing sealed point/traces. It is a fixed-background diagnostic, not a final matter action "
            "or coupled Einstein-matter theorem."
        ),
    }
    return outputs, metadata


def write_bv_denominator_ledger_outputs(
    outdir: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "medium_points": outdir / "beta075_bv_medium_denominator_points.parquet",
        "symbol_points": outdir / "beta075_bv_symbol_denominator_points.parquet",
        "energy_points": outdir / "beta075_bv_energy_denominator_points.parquet",
        "anec_traces": outdir / "beta075_bv_anec_trace_margins.parquet",
        "metric_summary": outdir / "beta075_bv_metric_summary.parquet",
        "top_tight_rows": outdir / "beta075_bv_top_tight_rows.parquet",
        "gate_summary": outdir / "beta075_bv_gate_summary.parquet",
    }
    for key, path in paths.items():
        outputs[key].to_parquet(path, index=False, compression="zstd")
    manifest_path = outdir / "beta075_bv_denominator_ledger_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths
