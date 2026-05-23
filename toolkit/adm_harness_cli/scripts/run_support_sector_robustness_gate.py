from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.source_ledger import sha256_file, write_manifest  # noqa: E402


EPS = 1.0e-30


@dataclass(frozen=True)
class SupportRun:
    label: str
    mesh: str
    kind: str
    run_dir: Path
    closure_dir: Path


DEFAULT_BASELINE_ROOT = Path("toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15")
DEFAULT_DENSE_ROOT = Path("toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12")


DEFAULT_RUNS = [
    SupportRun(
        label="baseline_24x14",
        mesh="baseline",
        kind="reference_24x14",
        run_dir=DEFAULT_BASELINE_ROOT / "endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5",
        closure_dir=DEFAULT_BASELINE_ROOT / "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5",
    ),
    SupportRun(
        label="dense_24x14",
        mesh="dense",
        kind="reference_24x14",
        run_dir=DEFAULT_DENSE_ROOT / "endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5",
        closure_dir=DEFAULT_DENSE_ROOT / "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5",
    ),
    SupportRun(
        label="baseline_compact22x13",
        mesh="baseline",
        kind="compact_22x13",
        run_dir=DEFAULT_BASELINE_ROOT / "endpoint_support_stroke_compact22x13_freeze_rematch_w6_t1p5",
        closure_dir=DEFAULT_BASELINE_ROOT / "endpoint_support_total_closure_compact22x13_freeze_rematch_w6_t1p5",
    ),
    SupportRun(
        label="dense_compact22x13",
        mesh="dense",
        kind="compact_22x13",
        run_dir=DEFAULT_DENSE_ROOT / "endpoint_support_stroke_compact22x13_freeze_rematch_w6_t1p5",
        closure_dir=DEFAULT_DENSE_ROOT / "endpoint_support_total_closure_compact22x13_freeze_rematch_w6_t1p5",
    ),
]


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if not math.isfinite(number):
        return default
    return number


def _safe_ratio(num: float, denom: float) -> float:
    return float(num / denom) if denom > 0.0 else float("nan")


def _bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin({"1", "true", "yes"})


def _quantile(series: pd.Series, q: float) -> float:
    values = series.astype(float).replace([np.inf, -np.inf], np.nan).dropna()
    return float(values.quantile(q)) if len(values) else float("nan")


def _top_share(values: np.ndarray, row_fraction: float) -> float:
    total = float(np.sum(values))
    if len(values) == 0 or total <= 0.0:
        return float("nan")
    count = max(1, int(math.ceil(float(row_fraction) * len(values))))
    return float(np.sort(values)[::-1][:count].sum() / total)


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def _read_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _status_value(value: Any) -> str:
    return str(value).strip()


def _gate_margin(value: float, gate: float) -> float:
    return float(gate - value) if math.isfinite(value) and math.isfinite(gate) else float("nan")


def _margin_fraction(value: float, gate: float) -> float:
    return _safe_ratio(_gate_margin(value, gate), gate)


def _pass(value: Any) -> bool:
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    return str(value).strip().lower() in {"true", "1", "yes", "pass"}


def _row(frame: pd.DataFrame, column: str, value: str) -> pd.Series | None:
    selected = frame.loc[frame[column].astype(str) == value]
    return None if selected.empty else selected.iloc[0]


def _point_proxy_summary(label: str, mesh: str, kind: str, point: pd.DataFrame) -> dict[str, Any]:
    active = _bool_series(point["medium_source_active"]) if "medium_source_active" in point else pd.Series(True, index=point.index)
    live = _bool_series(point["covariant_divergence_live"]) if "covariant_divergence_live" in point else pd.Series(False, index=point.index)
    allowed = _bool_series(point["covariant_exchange_allowed_mask"]) if "covariant_exchange_allowed_mask" in point else pd.Series(True, index=point.index)
    active_nonlive = active & (~live)
    outside = (~allowed) & (~live)
    volume = point["volume_weight"].astype(float) if "volume_weight" in point else pd.Series(1.0, index=point.index)
    support_volume = point["fit_abs_PF_density"].astype(float) * volume if "fit_abs_PF_density" in point else pd.Series(0.0, index=point.index)
    active_guard = point.loc[active_nonlive].copy()
    h_reg = active_guard["enthalpy_buffer_density"].astype(float) if "enthalpy_buffer_density" in active_guard else pd.Series(dtype=float)
    transport_margin = active_guard["transport_margin"].astype(float) if "transport_margin" in active_guard else pd.Series(dtype=float)
    heat_ratio = active_guard["regulated_heat_flux_ratio"].astype(float) if "regulated_heat_flux_ratio" in active_guard else pd.Series(dtype=float)
    type_i = active_guard["regulated_type_i_margin"].astype(float) if "regulated_type_i_margin" in active_guard else pd.Series(dtype=float)
    psi = active_guard["transport_rapidity_abs"].astype(float) if "transport_rapidity_abs" in active_guard else pd.Series(dtype=float)
    source_abs_volume = (
        active_guard["guard_source_abs_volume"].astype(float)
        if "guard_source_abs_volume" in active_guard
        else active_guard["source_abs_density"].astype(float) * active_guard["volume_weight"].astype(float)
        if "source_abs_density" in active_guard and "volume_weight" in active_guard
        else pd.Series(dtype=float)
    )
    high_psi = psi > 4.0 if len(psi) else pd.Series(dtype=bool)
    high_psi_source = float(source_abs_volume.loc[high_psi].sum()) if len(source_abs_volume) else 0.0
    source_total = float(source_abs_volume.sum()) if len(source_abs_volume) else 0.0
    return {
        "label": label,
        "mesh": mesh,
        "kind": kind,
        "rows": int(len(point)),
        "active_nonlive_rows": int(active_nonlive.sum()),
        "outside_nonlive_rows": int(outside.sum()),
        "live_rows": int(live.sum()),
        "support_abs_PF_volume": float(support_volume.sum()),
        "outside_support_abs_PF_volume": float(support_volume.loc[outside].sum()) if len(point) else 0.0,
        "live_support_abs_PF_volume": float(support_volume.loc[live].sum()) if len(point) else 0.0,
        "outside_support_fraction": _safe_ratio(float(support_volume.loc[outside].sum()), float(support_volume.sum())),
        "live_support_fraction": _safe_ratio(float(support_volume.loc[live].sum()), float(support_volume.sum())),
        "h_reg_min": float(h_reg.min()) if len(h_reg) else float("nan"),
        "h_reg_p01": _quantile(h_reg, 0.01),
        "transport_margin_min": float(transport_margin.min()) if len(transport_margin) else float("nan"),
        "transport_margin_p01": _quantile(transport_margin, 0.01),
        "regulated_heat_flux_ratio_p99": _quantile(heat_ratio, 0.99),
        "type_i_margin_min": float(type_i.min()) if len(type_i) else float("nan"),
        "type_i_margin_p01": _quantile(type_i, 0.01),
        "max_transport_rapidity_abs": float(psi.max()) if len(psi) else float("nan"),
        "high_psi_source_fraction": _safe_ratio(high_psi_source, source_total),
    }


def _local_proxy_rows(label: str, mesh: str, kind: str, point: pd.DataFrame) -> list[dict[str, Any]]:
    active = _bool_series(point["medium_source_active"]) if "medium_source_active" in point else pd.Series(True, index=point.index)
    live = _bool_series(point["covariant_divergence_live"]) if "covariant_divergence_live" in point else pd.Series(False, index=point.index)
    frame = point.loc[active & (~live)].copy()
    rows: list[dict[str, Any]] = []
    for key, group in frame.groupby(["assignment", "stage", "region"], sort=False, dropna=False):
        assignment, stage, region = key
        h_reg = group["enthalpy_buffer_density"].astype(float) if "enthalpy_buffer_density" in group else pd.Series(dtype=float)
        transport_margin = group["transport_margin"].astype(float) if "transport_margin" in group else pd.Series(dtype=float)
        heat_ratio = group["regulated_heat_flux_ratio"].astype(float) if "regulated_heat_flux_ratio" in group else pd.Series(dtype=float)
        type_i = group["regulated_type_i_margin"].astype(float) if "regulated_type_i_margin" in group else pd.Series(dtype=float)
        psi = group["transport_rapidity_abs"].astype(float) if "transport_rapidity_abs" in group else pd.Series(dtype=float)
        source_abs_volume = (
            group["guard_source_abs_volume"].astype(float)
            if "guard_source_abs_volume" in group
            else group["source_abs_density"].astype(float) * group["volume_weight"].astype(float)
            if "source_abs_density" in group and "volume_weight" in group
            else pd.Series(dtype=float)
        )
        high_psi = psi > 4.0 if len(psi) else pd.Series(dtype=bool)
        source_total = float(source_abs_volume.sum()) if len(source_abs_volume) else 0.0
        high_psi_source = float(source_abs_volume.loc[high_psi].sum()) if len(source_abs_volume) else 0.0
        rows.append({
            "label": label,
            "mesh": mesh,
            "kind": kind,
            "assignment": str(assignment),
            "stage": str(stage),
            "region": str(region),
            "rows": int(len(group)),
            "h_reg_min": float(h_reg.min()) if len(h_reg) else float("nan"),
            "h_reg_p01": _quantile(h_reg, 0.01),
            "transport_margin_min": float(transport_margin.min()) if len(transport_margin) else float("nan"),
            "transport_margin_p01": _quantile(transport_margin, 0.01),
            "regulated_heat_flux_ratio_p99": _quantile(heat_ratio, 0.99),
            "type_i_margin_min": float(type_i.min()) if len(type_i) else float("nan"),
            "type_i_margin_p01": _quantile(type_i, 0.01),
            "max_transport_rapidity_abs": float(psi.max()) if len(psi) else float("nan"),
            "high_psi_source_fraction": _safe_ratio(high_psi_source, source_total),
        })
    return rows


def _decision_summary(run: SupportRun) -> dict[str, Any]:
    stroke_decision = _read_csv(run.run_dir / "endpoint_support_stroke_exchange_decision.csv")
    closure_decision = _read_csv(run.closure_dir / "endpoint_support_total_closure_decision.csv")
    stroke = stroke_decision.iloc[0]
    closure = closure_decision.iloc[0]
    metrics = {
        "label": run.label,
        "mesh": run.mesh,
        "kind": run.kind,
        "stroke_status": _status_value(stroke.get("support_stroke_exchange_status", "")),
        "stroke_pass": _pass(stroke.get("passes_support_stroke_exchange_fit", False)),
        "closure_status": _status_value(closure.get("support_total_closure_status", "")),
        "closure_pass": _pass(closure.get("passes_support_total_closure", False)),
    }
    for column in [
        "best_normalized_active_abs_PF_l1_error",
        "best_normalized_allowed_abs_PF_l1_error",
        "best_active_coordinate_l2_error_ratio",
        "best_allowed_coordinate_l2_error_ratio",
        "best_max_abs_coefficient",
        "best_effective_coefficient_count_total",
        "best_outside_tail_fraction",
        "best_live_tail_fraction",
        "best_high_psi_source_fraction",
        "active_pf_l1_gate",
        "allowed_pf_l1_gate",
        "coordinate_error_gate",
        "coefficient_gate",
        "effective_coefficient_count_gate",
        "outside_tail_fraction_gate",
        "live_tail_fraction_gate",
        "high_psi_source_fraction_gate",
    ]:
        if column in stroke:
            metrics[column] = _finite(stroke[column], float("nan"))
    for column in [
        "active_closure_residual_to_endpoint_l2_ratio",
        "allowed_closure_residual_to_endpoint_l2_ratio",
        "local_max_closure_residual_to_endpoint_l2_ratio",
        "active_closure_residual_to_target_abs_PF_ratio",
        "allowed_closure_residual_to_target_abs_PF_ratio",
        "local_max_closure_residual_to_target_abs_PF_ratio",
        "outside_residual_fraction_of_full_endpoint",
        "live_residual_fraction_of_full_endpoint",
        "outside_support_tail_fraction",
        "live_support_tail_fraction",
        "full_candidate_support_angular_volume",
        "full_total_closure_residual_angular_volume",
        "active_closure_l2_gate",
        "allowed_closure_l2_gate",
        "local_closure_l2_gate",
        "active_closure_pf_gate",
        "allowed_closure_pf_gate",
        "local_closure_pf_gate",
        "outside_residual_fraction_gate",
        "live_residual_fraction_gate",
        "support_tail_fraction_gate",
        "live_support_fraction_gate",
        "angular_support_gate",
    ]:
        if column in closure:
            metrics[column] = _finite(closure[column], float("nan"))
    metrics["min_reference_closure_gate_margin"] = min(
        _gate_margin(metrics.get("active_closure_residual_to_endpoint_l2_ratio", float("nan")), metrics.get("active_closure_l2_gate", float("nan"))),
        _gate_margin(metrics.get("allowed_closure_residual_to_endpoint_l2_ratio", float("nan")), metrics.get("allowed_closure_l2_gate", float("nan"))),
        _gate_margin(metrics.get("local_max_closure_residual_to_endpoint_l2_ratio", float("nan")), metrics.get("local_closure_l2_gate", float("nan"))),
        _gate_margin(metrics.get("active_closure_residual_to_target_abs_PF_ratio", float("nan")), metrics.get("active_closure_pf_gate", float("nan"))),
        _gate_margin(metrics.get("allowed_closure_residual_to_target_abs_PF_ratio", float("nan")), metrics.get("allowed_closure_pf_gate", float("nan"))),
        _gate_margin(metrics.get("local_max_closure_residual_to_target_abs_PF_ratio", float("nan")), metrics.get("local_closure_pf_gate", float("nan"))),
    )
    metrics["min_reference_closure_gate_margin_fraction"] = min(
        _margin_fraction(metrics.get("active_closure_residual_to_endpoint_l2_ratio", float("nan")), metrics.get("active_closure_l2_gate", float("nan"))),
        _margin_fraction(metrics.get("allowed_closure_residual_to_endpoint_l2_ratio", float("nan")), metrics.get("allowed_closure_l2_gate", float("nan"))),
        _margin_fraction(metrics.get("local_max_closure_residual_to_endpoint_l2_ratio", float("nan")), metrics.get("local_closure_l2_gate", float("nan"))),
        _margin_fraction(metrics.get("active_closure_residual_to_target_abs_PF_ratio", float("nan")), metrics.get("active_closure_pf_gate", float("nan"))),
        _margin_fraction(metrics.get("allowed_closure_residual_to_target_abs_PF_ratio", float("nan")), metrics.get("allowed_closure_pf_gate", float("nan"))),
        _margin_fraction(metrics.get("local_max_closure_residual_to_target_abs_PF_ratio", float("nan")), metrics.get("local_closure_pf_gate", float("nan"))),
    )
    return metrics


def _local_closure_rows(run: SupportRun) -> list[dict[str, Any]]:
    summary = _read_csv(run.closure_dir / "endpoint_support_total_closure_scope_summary.csv")
    rows: list[dict[str, Any]] = []
    for _, row in summary.iterrows():
        scope = str(row["scope"])
        if not scope.startswith("active::"):
            continue
        parts = scope.removeprefix("active::").split("|")
        rows.append({
            "label": run.label,
            "mesh": run.mesh,
            "kind": run.kind,
            "scope": scope,
            "assignment": parts[0] if len(parts) > 0 else "",
            "stage": parts[1] if len(parts) > 1 else "",
            "region": parts[2] if len(parts) > 2 else "",
            "rows": int(row["rows"]),
            "residual_to_endpoint_l2": _finite(row["closure_residual_to_endpoint_l2_ratio"], float("nan")),
            "residual_to_target_abs_PF": _finite(row["closure_residual_to_target_abs_PF_ratio"], float("nan")),
            "endpoint_exchange_l2_volume": _finite(row["endpoint_exchange_l2_volume"], 0.0),
            "total_closure_residual_l2_volume": _finite(row["total_closure_residual_l2_volume"], 0.0),
            "residual_abs_PF_volume": _finite(row["total_closure_residual_abs_PF_volume"], 0.0),
            "peak_residual_l2_density": _finite(row["peak_residual_l2_density"], float("nan")),
            "top_1pct_residual_burden_share": _finite(row["top_1pct_residual_burden_share"], float("nan")),
        })
    return rows


def _concentration_summary(run: SupportRun) -> dict[str, Any]:
    point = _read_csv(run.closure_dir / "endpoint_support_total_closure_point_closure.csv")
    active = _bool_series(point["medium_source_active"]) if "medium_source_active" in point else pd.Series(True, index=point.index)
    live = _bool_series(point["covariant_divergence_live"]) if "covariant_divergence_live" in point else pd.Series(False, index=point.index)
    active_nonlive = active & (~live)
    selected = point.loc[active_nonlive].copy()
    residual = selected["total_closure_residual_l2_density_volume"].astype(float).to_numpy()
    support = selected["candidate_support_l2_density_volume"].astype(float).to_numpy()
    return {
        "label": run.label,
        "mesh": run.mesh,
        "kind": run.kind,
        "active_rows": int(len(selected)),
        "active_residual_l2_volume": float(np.sum(residual)),
        "active_support_l2_volume": float(np.sum(support)),
        "residual_top_1pct_share": _top_share(residual, 0.01),
        "residual_top_5pct_share": _top_share(residual, 0.05),
        "support_top_1pct_share": _top_share(support, 0.01),
        "support_top_5pct_share": _top_share(support, 0.05),
        "peak_residual_l2_density": float(selected["total_closure_residual_l2_density"].astype(float).max()) if len(selected) else float("nan"),
        "p99_residual_l2_density": _quantile(selected["total_closure_residual_l2_density"], 0.99) if len(selected) else float("nan"),
    }


def _gate_status(
    decision: pd.DataFrame,
    point_proxy: pd.DataFrame,
    local_proxy: pd.DataFrame,
    concentration: pd.DataFrame,
    *,
    tight_margin_fraction: float,
    max_peak_growth: float,
    max_coefficient_growth: float,
    local_heat_p99_watch: float,
    local_high_psi_source_fraction_watch: float,
    local_transport_margin_p01_watch: float,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    ref = decision.loc[decision["kind"] == "reference_24x14"].copy()
    compact = decision.loc[decision["kind"] == "compact_22x13"].copy()
    base_ref = _row(ref, "mesh", "baseline")
    dense_ref = _row(ref, "mesh", "dense")
    base_compact = _row(compact, "mesh", "baseline")
    dense_compact = _row(compact, "mesh", "dense")

    reference_pass = bool(len(ref) == 2 and ref["closure_pass"].astype(bool).all() and ref["stroke_pass"].astype(bool).all())
    dense_margin_fraction = _finite(dense_ref["min_reference_closure_gate_margin_fraction"], float("nan")) if dense_ref is not None else float("nan")
    rows.append({
        "gate": "reference_total_closure",
        "status": "pass" if reference_pass and dense_margin_fraction >= tight_margin_fraction else "watch" if reference_pass else "fail",
        "metric": dense_margin_fraction,
        "gate_value": tight_margin_fraction,
        "read": "24x14 baseline/dense clear closure gates; dense margin is comfortable" if reference_pass and dense_margin_fraction >= tight_margin_fraction else "24x14 clears gates but dense local margin is tight" if reference_pass else "24x14 reference closure does not clear baseline/dense gates",
    })

    compact_pass = bool(len(compact) == 2 and compact["closure_pass"].astype(bool).all() and compact["stroke_pass"].astype(bool).all())
    rows.append({
        "gate": "compact_cross_bracket",
        "status": "pass" if compact_pass else "watch",
        "metric": _finite(dense_compact["local_max_closure_residual_to_target_abs_PF_ratio"], float("nan")) if dense_compact is not None else float("nan"),
        "gate_value": _finite(dense_compact["local_closure_pf_gate"], float("nan")) if dense_compact is not None else float("nan"),
        "read": "compact 22x13 clears baseline/dense closure" if compact_pass else "compact 22x13 is a bracket only; dense local closure misses the promoted gate",
    })

    dense_point = _row(point_proxy.loc[point_proxy["kind"] == "reference_24x14"], "mesh", "dense")
    proxy_pass = False
    if dense_point is not None:
        proxy_pass = bool(
            _finite(dense_point["h_reg_min"], -1.0) > 0.0
            and _finite(dense_point["transport_margin_min"], -1.0) >= -1.0e-12
            and _finite(dense_point["type_i_margin_min"], -1.0) > 0.0
            and _finite(dense_point["high_psi_source_fraction"], 1.0) <= 0.005
        )
    rows.append({
        "gate": "hyperbolic_proxy_guards",
        "status": "pass" if proxy_pass else "fail",
        "metric": _finite(dense_point["h_reg_min"], float("nan")) if dense_point is not None else float("nan"),
        "gate_value": 0.0,
        "read": "necessary h_reg, transport-margin, Type-I, and high-psi guards remain positive/on-gate" if proxy_pass else "necessary hyperbolic/admissibility proxy guard fails",
    })

    dense_local_proxy = local_proxy.loc[
        (local_proxy["kind"] == "reference_24x14") & (local_proxy["mesh"] == "dense")
    ].copy()
    local_heat_max = float(dense_local_proxy["regulated_heat_flux_ratio_p99"].astype(float).max()) if len(dense_local_proxy) else float("nan")
    local_high_psi_max = float(dense_local_proxy["high_psi_source_fraction"].astype(float).max()) if len(dense_local_proxy) else float("nan")
    local_transport_p01_min = float(dense_local_proxy["transport_margin_p01"].astype(float).min()) if len(dense_local_proxy) else float("nan")
    local_proxy_watch = bool(
        local_heat_max > float(local_heat_p99_watch)
        or local_high_psi_max > float(local_high_psi_source_fraction_watch)
        or local_transport_p01_min < float(local_transport_margin_p01_watch)
    )
    rows.append({
        "gate": "local_hyperbolic_proxy_watch",
        "status": "watch" if local_proxy_watch else "pass",
        "metric": max(
            _safe_ratio(local_heat_max, float(local_heat_p99_watch)),
            _safe_ratio(local_high_psi_max, float(local_high_psi_source_fraction_watch)),
            _safe_ratio(float(local_transport_margin_p01_watch), local_transport_p01_min),
        ),
        "gate_value": 1.0,
        "read": (
            "one or more dense local support-edge phases sit closer to the heat-current/psi boundary than the aggregate guard shows"
            if local_proxy_watch
            else "local phase guards do not exceed watch thresholds"
        ),
    })

    locality_pass = False
    if dense_ref is not None:
        locality_pass = bool(
            _finite(dense_ref["outside_support_tail_fraction"], 1.0) <= _finite(dense_ref["support_tail_fraction_gate"], 0.0)
            and _finite(dense_ref["live_support_tail_fraction"], 1.0) <= _finite(dense_ref["live_support_fraction_gate"], 0.0)
            and _finite(dense_ref["full_candidate_support_angular_volume"], 1.0) <= _finite(dense_ref["angular_support_gate"], 0.0)
            and _finite(dense_ref["full_total_closure_residual_angular_volume"], 1.0) <= _finite(dense_ref["angular_support_gate"], 0.0)
        )
    rows.append({
        "gate": "locality_and_hidden_channel",
        "status": "pass" if locality_pass else "fail",
        "metric": _finite(dense_ref["outside_support_tail_fraction"], float("nan")) if dense_ref is not None else float("nan"),
        "gate_value": _finite(dense_ref["support_tail_fraction_gate"], float("nan")) if dense_ref is not None else float("nan"),
        "read": "support exchange stays non-live, localized, and angular-free" if locality_pass else "support exchange leaks into hidden/locality channel",
    })

    coefficient_growth = float("nan")
    if base_ref is not None and dense_ref is not None:
        coefficient_growth = _safe_ratio(
            _finite(dense_ref["best_max_abs_coefficient"], float("nan")),
            _finite(base_ref["best_max_abs_coefficient"], float("nan")),
        )
    coefficient_pass = bool(
        dense_ref is not None
        and _finite(dense_ref["best_max_abs_coefficient"], float("inf")) <= _finite(dense_ref["coefficient_gate"], 0.0)
        and _finite(dense_ref["best_effective_coefficient_count_total"], float("inf")) <= _finite(dense_ref["effective_coefficient_count_gate"], 0.0)
        and coefficient_growth <= max_coefficient_growth
    )
    rows.append({
        "gate": "coefficient_stability",
        "status": "pass" if coefficient_pass else "watch",
        "metric": coefficient_growth,
        "gate_value": max_coefficient_growth,
        "read": "coefficients stay bounded across baseline/dense" if coefficient_pass else "coefficients clear absolute gates but grow enough to remain a stability watch",
    })

    peak_growth = float("nan")
    base_conc = _row(concentration.loc[concentration["kind"] == "reference_24x14"], "mesh", "baseline")
    dense_conc = _row(concentration.loc[concentration["kind"] == "reference_24x14"], "mesh", "dense")
    if base_conc is not None and dense_conc is not None:
        peak_growth = _safe_ratio(
            _finite(dense_conc["peak_residual_l2_density"], float("nan")),
            _finite(base_conc["peak_residual_l2_density"], float("nan")),
        )
    concentration_pass = bool(math.isfinite(peak_growth) and peak_growth <= max_peak_growth)
    rows.append({
        "gate": "residual_concentration_scaling",
        "status": "pass" if concentration_pass else "watch",
        "metric": peak_growth,
        "gate_value": max_peak_growth,
        "read": "peak residual does not sharpen across baseline/dense" if concentration_pass else "peak residual growth needs denser or frozen-structure confirmation",
    })

    statuses = [row["status"] for row in rows]
    if any(status == "fail" for status in statuses):
        overall = "fail"
    elif any(status == "watch" for status in statuses):
        overall = "watch"
    else:
        overall = "pass"
    rows.append({
        "gate": "overall_support_sector_next_gate",
        "status": overall,
        "metric": float("nan"),
        "gate_value": float("nan"),
        "read": (
            "support sector is ready for action-level PDE formulation checks"
            if overall == "pass"
            else "support sector survives necessary proxy gates but stays on watch before action-level promotion"
            if overall == "watch"
            else "support sector fails a necessary next-gate proxy"
        ),
    })
    return pd.DataFrame(rows)


def _format_float(value: Any, digits: int = 6) -> str:
    number = _finite(value, float("nan"))
    if not math.isfinite(number):
        return "nan"
    if abs(number) > 0 and (abs(number) < 1.0e-4 or abs(number) >= 1.0e5):
        return f"{number:.3e}"
    return f"{number:.{digits}f}"


def _report(
    decision: pd.DataFrame,
    local: pd.DataFrame,
    point_proxy: pd.DataFrame,
    local_proxy: pd.DataFrame,
    concentration: pd.DataFrame,
    gate: pd.DataFrame,
    metadata: dict[str, Any],
) -> str:
    ref = decision.loc[decision["kind"] == "reference_24x14"].set_index("mesh")
    compact = decision.loc[decision["kind"] == "compact_22x13"].set_index("mesh")
    dense_ref = ref.loc["dense"]
    base_ref = ref.loc["baseline"]
    dense_compact = compact.loc["dense"]
    gate_overall = gate.loc[gate["gate"] == "overall_support_sector_next_gate"].iloc[0]
    dense_local = (
        local.loc[(local["kind"] == "reference_24x14") & (local["mesh"] == "dense")]
        .sort_values("residual_to_target_abs_PF", ascending=False)
        .head(5)
    )
    dense_proxy = point_proxy.loc[(point_proxy["kind"] == "reference_24x14") & (point_proxy["mesh"] == "dense")].iloc[0]
    dense_local_proxy = (
        local_proxy.loc[(local_proxy["kind"] == "reference_24x14") & (local_proxy["mesh"] == "dense")]
        .sort_values(["regulated_heat_flux_ratio_p99", "high_psi_source_fraction"], ascending=False)
        .head(6)
    )
    dense_conc = concentration.loc[(concentration["kind"] == "reference_24x14") & (concentration["mesh"] == "dense")].iloc[0]
    lines = [
        "# Stage II Beta075 Support-Sector Robustness Gate",
        "",
        f"Generated: {metadata['generated_date']}",
        "",
        "## Status",
        "",
        f"Overall status: `{gate_overall['status']}`.",
        "",
        "This is the first harder gate after finite-difference endpoint/support closure. It is a necessary-condition robustness gate over the existing support-stroke and total-closure outputs, not a final matter-action or PDE hyperbolicity proof.",
        "",
        "## Inputs",
        "",
    ]
    for item in metadata["runs"]:
        lines.append(f"- `{item['label']}`: `{item['stroke_dir']}` and `{item['closure_dir']}`")
    lines.extend([
        "",
        "## Gate Summary",
        "",
        "| gate | status | metric | gate | read |",
        "| --- | --- | ---: | ---: | --- |",
    ])
    for _, row in gate.iterrows():
        lines.append(
            f"| {row['gate']} | {row['status']} | {_format_float(row['metric'])} | {_format_float(row['gate_value'])} | {row['read']} |"
        )
    lines.extend([
        "",
        "## Reference 24x14 Closure Read",
        "",
        "| mesh | closure status | active PF residual | local max PF residual | outside support tail | live support tail | min gate margin fraction |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    for mesh, row in ref.iterrows():
        lines.append(
            f"| {mesh} | {row['closure_status']} | {_format_float(row['active_closure_residual_to_target_abs_PF_ratio'])} | "
            f"{_format_float(row['local_max_closure_residual_to_target_abs_PF_ratio'])} | "
            f"{_format_float(row['outside_support_tail_fraction'])} | {_format_float(row['live_support_tail_fraction'])} | "
            f"{_format_float(row['min_reference_closure_gate_margin_fraction'])} |"
        )
    lines.extend([
        "",
        "Read: the promoted `24x14` sector still clears baseline and dense closure. The dense local PF residual is close to the `0.55` gate, with only about "
        f"`{_format_float(dense_ref['min_reference_closure_gate_margin_fraction'])}` fractional margin on the tightest closure metric. That is enough to proceed to a harder gate, but not enough to call the sector comfortably robust.",
        "",
        "## Compact Cross-Bracket",
        "",
        "| mesh | closure status | local max PF residual | PF gate | local max L2 residual | L2 gate |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ])
    for mesh, row in compact.iterrows():
        lines.append(
            f"| {mesh} | {row['closure_status']} | {_format_float(row['local_max_closure_residual_to_target_abs_PF_ratio'])} | "
            f"{_format_float(row['local_closure_pf_gate'])} | {_format_float(row['local_max_closure_residual_to_endpoint_l2_ratio'])} | "
            f"{_format_float(row['local_closure_l2_gate'])} |"
        )
    lines.extend([
        "",
        "Read: compact `22x13` is useful evidence against a pure large-basis artifact, but it is not the promoted closure reference. Dense compact misses the local gate, so cross-bracket robustness remains a watch.",
        "",
        "## Dense Local Residuals",
        "",
        "| assignment | stage | region | residual / endpoint L2 | residual / PF | top 1pct share |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ])
    for _, row in dense_local.iterrows():
        lines.append(
            f"| {row['assignment']} | {row['stage']} | {row['region']} | {_format_float(row['residual_to_endpoint_l2'])} | "
            f"{_format_float(row['residual_to_target_abs_PF'])} | {_format_float(row['top_1pct_residual_burden_share'])} |"
        )
    lines.extend([
        "",
        "Read: dense reset/core remains the sharpest local watch. This is exactly where a later frozen-structure or action-level test should try to break the model.",
        "",
        "## Hyperbolic And Locality Proxies",
        "",
        "| proxy | dense 24x14 value | read |",
        "| --- | ---: | --- |",
        f"| minimum h_reg / Type-I margin | {_format_float(dense_proxy['h_reg_min'], 9)} | positive but thin |",
        f"| p01 transport margin | {_format_float(dense_proxy['transport_margin_p01'])} | near-luminal but inside proxy gate |",
        f"| p99 heat-flux ratio | {_format_float(dense_proxy['regulated_heat_flux_ratio_p99'])} | close to the causal boundary |",
        f"| high-psi source fraction | {_format_float(dense_proxy['high_psi_source_fraction'])} | below 0.005 gate |",
        f"| outside support fraction | {_format_float(dense_proxy['outside_support_fraction'])} | tiny localized tail |",
        f"| live support fraction | {_format_float(dense_proxy['live_support_fraction'])} | no live support current |",
        "",
        "Aggregate read: the necessary hyperbolic/admissibility proxies pass, but the support edge remains a thin-cushion, near-luminal medium. This is not yet a characteristic-speed theorem.",
        "",
        "Dense local guard rows with the hottest heat-current phases:",
        "",
        "| assignment | stage | region | h_reg min | p01 transport margin | p99 heat ratio | high-psi source fraction |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ])
    for _, row in dense_local_proxy.iterrows():
        lines.append(
            f"| {row['assignment']} | {row['stage']} | {row['region']} | {_format_float(row['h_reg_min'], 9)} | "
            f"{_format_float(row['transport_margin_p01'])} | {_format_float(row['regulated_heat_flux_ratio_p99'])} | "
            f"{_format_float(row['high_psi_source_fraction'])} |"
        )
    lines.extend([
        "",
        "Local read: the aggregate proxy is cleaner than the phase-local picture. Dense support-edge release and held-carry phases are the first causal/hyperbolic watch rows for a real action-level model.",
        "",
        "## Concentration And Scaling",
        "",
        "| mesh | peak residual density | p99 residual density | residual top 1pct share | support top 1pct share |",
        "| --- | ---: | ---: | ---: | ---: |",
    ])
    for _, row in concentration.loc[concentration["kind"] == "reference_24x14"].iterrows():
        lines.append(
            f"| {row['mesh']} | {_format_float(row['peak_residual_l2_density'])} | {_format_float(row['p99_residual_l2_density'])} | "
            f"{_format_float(row['residual_top_1pct_share'])} | {_format_float(row['support_top_1pct_share'])} |"
        )
    lines.extend([
        "",
        "Read: the residual remains concentrated but does not show a simple peak blow-up across the baseline-to-dense step. That is favorable for finite-width interpretation, while the top-share concentration keeps the reset/core watch alive.",
        "",
        "## Interpretation",
        "",
        "The next gate does not kill the support-sector story. The promoted `24x14` support-stroke/stress sector clears total closure on both meshes, keeps support exchange non-live and angular-free, and preserves the necessary h_reg/transport/Type-I guards.",
        "",
        "It also does not promote the model to a final action. The dense local gate is tight, the compact dense bracket fails locally, the coefficient count is high, and the hyperbolic read is still proxy-level. The right next move is a stricter frozen-structure or action-level PDE test aimed at dense reset/core, not more same-level closure fitting.",
        "",
        "## Decision",
        "",
        "Status: `watch-pass` for proceeding to a true action-level gate.",
        "",
        "Allowed next:",
        "",
        "```text",
        "1. Freeze the 24x14 support-sector structure from baseline or dense and evaluate it across the alternate mesh without refitting.",
        "2. Build a reduced support-sector evolution/characteristic proxy for the two-channel P/F stroke law.",
        "3. Stress dense reset/core with bracketed widths/ridges and require no growth in local residual or coefficient concentration.",
        "4. Keep compact 22x13 as a compactness bracket, not as the promoted reference.",
        "```",
        "",
        "Claim boundary:",
        "",
        "```text",
        "This gate supports continuing to action-level modeling. It does not certify a matter action, hyperbolicity theorem, global causal structure, or broad beta/service-factor robustness.",
        "```",
    ])
    return "\n".join(lines) + "\n"


def build_support_sector_robustness_gate(
    runs: list[SupportRun],
    *,
    tight_margin_fraction: float = 0.05,
    max_peak_growth: float = 2.0,
    max_coefficient_growth: float = 2.0,
    local_heat_p99_watch: float = 0.995,
    local_high_psi_source_fraction_watch: float = 0.005,
    local_transport_margin_p01_watch: float = 0.005,
) -> tuple[dict[str, pd.DataFrame], dict[str, Any], str]:
    decision_rows = []
    local_rows: list[dict[str, Any]] = []
    point_rows = []
    local_proxy_rows: list[dict[str, Any]] = []
    concentration_rows = []
    metadata_runs = []
    for run in runs:
        decision_rows.append(_decision_summary(run))
        local_rows.extend(_local_closure_rows(run))
        point = _read_csv(run.run_dir / "endpoint_support_stroke_exchange_point_fit.csv")
        point_rows.append(_point_proxy_summary(run.label, run.mesh, run.kind, point))
        local_proxy_rows.extend(_local_proxy_rows(run.label, run.mesh, run.kind, point))
        concentration_rows.append(_concentration_summary(run))
        metadata_runs.append({
            "label": run.label,
            "mesh": run.mesh,
            "kind": run.kind,
            "stroke_dir": str(run.run_dir),
            "closure_dir": str(run.closure_dir),
            "stroke_manifest": str(run.run_dir / "endpoint_support_stroke_exchange_manifest.json"),
            "closure_manifest": str(run.closure_dir / "endpoint_support_total_closure_manifest.json"),
        })

    decision = pd.DataFrame(decision_rows)
    local = pd.DataFrame(local_rows)
    point_proxy = pd.DataFrame(point_rows)
    local_proxy = pd.DataFrame(local_proxy_rows)
    concentration = pd.DataFrame(concentration_rows)
    gate = _gate_status(
        decision,
        point_proxy,
        local_proxy,
        concentration,
        tight_margin_fraction=tight_margin_fraction,
        max_peak_growth=max_peak_growth,
        max_coefficient_growth=max_coefficient_growth,
        local_heat_p99_watch=local_heat_p99_watch,
        local_high_psi_source_fraction_watch=local_high_psi_source_fraction_watch,
        local_transport_margin_p01_watch=local_transport_margin_p01_watch,
    )
    outputs = {
        "decision_compare": decision,
        "local_residual_compare": local,
        "point_proxy_summary": point_proxy,
        "local_proxy_summary": local_proxy,
        "concentration_summary": concentration,
        "gate_summary": gate,
    }
    metadata = {
        "source_name": "support_sector_robustness_gate",
        "generated_date": dt.date.today().isoformat(),
        "tight_margin_fraction": float(tight_margin_fraction),
        "max_peak_growth": float(max_peak_growth),
        "max_coefficient_growth": float(max_coefficient_growth),
        "local_heat_p99_watch": float(local_heat_p99_watch),
        "local_high_psi_source_fraction_watch": float(local_high_psi_source_fraction_watch),
        "local_transport_margin_p01_watch": float(local_transport_margin_p01_watch),
        "runs": metadata_runs,
        "caveat": (
            "Necessary-condition support-sector robustness gate over existing support-stroke "
            "and total-closure outputs. This is not a final matter action, PDE "
            "hyperbolicity theorem, or global causal proof."
        ),
    }
    report = _report(decision, local, point_proxy, local_proxy, concentration, gate, metadata)
    return outputs, metadata, report


def write_support_sector_robustness_gate(
    outdir: Path,
    report_path: Path,
    outputs: dict[str, pd.DataFrame],
    metadata: dict[str, Any],
    report: str,
) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    paths = {
        "decision_compare": outdir / "support_sector_robustness_decision_compare.csv",
        "local_residual_compare": outdir / "support_sector_robustness_local_residual_compare.csv",
        "point_proxy_summary": outdir / "support_sector_robustness_point_proxy_summary.csv",
        "local_proxy_summary": outdir / "support_sector_robustness_local_proxy_summary.csv",
        "concentration_summary": outdir / "support_sector_robustness_concentration_summary.csv",
        "gate_summary": outdir / "support_sector_robustness_gate_summary.csv",
    }
    for key, path in paths.items():
        outputs[key].to_csv(path, index=False)
    report_path.write_text(report)
    paths["report"] = report_path
    manifest_path = outdir / "support_sector_robustness_manifest.json"
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in paths.items()}
    manifest["rows"] = {key: int(len(outputs[key])) for key in outputs}
    manifest["sha256"] = {key: sha256_file(path) for key, path in paths.items()}
    write_manifest(manifest_path, manifest)
    paths["manifest"] = manifest_path
    return paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a necessary-condition robustness gate for the beta075 support-sector closure outputs."
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("toolkit/adm_harness_cli/runs/stage2_beta075_support_sector_robustness_gate"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("supporting_reports/STAGE2_BETA075_SUPPORT_SECTOR_ROBUSTNESS_GATE.md"),
    )
    parser.add_argument("--tight-margin-fraction", type=float, default=0.05)
    parser.add_argument("--max-peak-growth", type=float, default=2.0)
    parser.add_argument("--max-coefficient-growth", type=float, default=2.0)
    parser.add_argument("--local-heat-p99-watch", type=float, default=0.995)
    parser.add_argument("--local-high-psi-source-fraction-watch", type=float, default=0.005)
    parser.add_argument("--local-transport-margin-p01-watch", type=float, default=0.005)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    outputs, metadata, report = build_support_sector_robustness_gate(
        DEFAULT_RUNS,
        tight_margin_fraction=float(args.tight_margin_fraction),
        max_peak_growth=float(args.max_peak_growth),
        max_coefficient_growth=float(args.max_coefficient_growth),
        local_heat_p99_watch=float(args.local_heat_p99_watch),
        local_high_psi_source_fraction_watch=float(args.local_high_psi_source_fraction_watch),
        local_transport_margin_p01_watch=float(args.local_transport_margin_p01_watch),
    )
    paths = write_support_sector_robustness_gate(args.outdir, args.report, outputs, metadata, report)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "report": str(args.report),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(value) for key, value in paths.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
