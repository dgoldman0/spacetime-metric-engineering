from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))


J_SECTOR = "J_endpoint_junction_layer"
SUPPORT_ASSIGNMENT = "support_edge_endpoint_junction"
RESET_ASSIGNMENT = "reset_decompression_endpoint_junction"
SCOPES = {
    "J_total": None,
    "support_edge": SUPPORT_ASSIGNMENT,
    "reset_cap": RESET_ASSIGNMENT,
}


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if not math.isfinite(number):
        return default
    return number


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _load_labels(ledger_root: Path, requested: list[str] | None) -> list[str]:
    if requested:
        return list(requested)
    index_path = ledger_root / "stage2_candidate_ledgers_index.csv"
    if index_path.exists():
        index = pd.read_csv(index_path)
        if "label" in index.columns:
            return [str(label) for label in index["label"].tolist()]
    labels = []
    for child in sorted(ledger_root.iterdir()):
        if child.is_dir() and (child / "source_ledger_manifest.json").exists():
            labels.append(child.name)
    return labels


def _control_row(ledger_root: Path, label: str) -> dict[str, Any]:
    manifest_path = ledger_root / label / "source_ledger_manifest.json"
    manifest = _read_json(manifest_path)
    params = manifest.get("params", {})
    safety_path = ledger_root / label / "source_ledger_safety.csv"
    safety = pd.read_csv(safety_path).iloc[0].to_dict() if safety_path.exists() else {}
    return {
        "label": label,
        "case": str(manifest.get("case", "")),
        "edge_width_multiplier": _finite(
            params.get("standing_support_packet_smooth_split_edge_width_multiplier"), float("nan")
        ),
        "catch_width_multiplier": _finite(
            params.get("standing_support_packet_smooth_split_catch_width_multiplier"), float("nan")
        ),
        "edge_carve": _finite(params.get("standing_support_packet_smooth_split_edge_carve"), float("nan")),
        "current_guard_fraction": _finite(
            params.get("standing_support_packet_smooth_split_current_guard_fraction"), float("nan")
        ),
        "current_guard_mode": str(params.get("standing_support_packet_smooth_split_current_guard_mode", "")),
        "angular_log_gain": _finite(
            params.get("standing_support_packet_smooth_split_angular_log_gain"), float("nan")
        ),
        "support_radius_Rth": _finite(params.get("Rth"), float("nan")),
        "support_width_wth": _finite(params.get("w_th"), float("nan")),
        "angular_radius_ROmega": _finite(params.get("ROmega"), float("nan")),
        "angular_width_wOmega": _finite(params.get("wOmega"), float("nan")),
        "angular_amplitude_aOmega": _finite(params.get("aOmega"), float("nan")),
        "temporal_width_multiplier": _finite(
            params.get("standing_support_packet_smooth_split_temporal_width_multiplier"), float("nan")
        ),
        "release_choreography_mode": str(params.get("release_choreography_mode", "")),
        "release_matched_hold_widths": _finite(params.get("release_matched_hold_widths"), float("nan")),
        "release_beta_profile": str(params.get("release_beta_profile", "")),
        "release_beta_width_multiplier": _finite(params.get("release_beta_width_multiplier"), float("nan")),
        "release_lapse_lag_widths": _finite(params.get("release_lapse_lag_widths"), float("nan")),
        "release_carve_lag_widths": _finite(params.get("release_carve_lag_widths"), float("nan")),
        "receiver_enabled": bool(params.get("support_edge_receiver_enabled", False)),
        "receiver_memory_gain": _finite(params.get("support_edge_receiver_memory_gain"), float("nan")),
        "receiver_lapse_log_gain": _finite(params.get("support_edge_receiver_lapse_log_gain"), float("nan")),
        "receiver_radial_log_gain": _finite(params.get("support_edge_receiver_radial_log_gain"), float("nan")),
        "receiver_beta_relaxation_gain": _finite(
            params.get("support_edge_receiver_beta_relaxation_gain"), float("nan")
        ),
        "receiver_angular_log_gain": _finite(params.get("support_edge_receiver_angular_log_gain"), float("nan")),
        "receiver_angular_side": str(params.get("support_edge_receiver_angular_side", "")),
        "positive_packet_norm_live": int(_finite(safety.get("positive_packet_norm_live"), 0.0)),
        "max_packet_norm_live": _finite(safety.get("max_packet_norm_live"), float("nan")),
        "min_packet_norm_live": _finite(safety.get("min_packet_norm_live"), float("nan")),
        "live_points": int(_finite(safety.get("live_points"), 0.0)),
    }


def _rows_for_fraction(weights: np.ndarray, fraction: float) -> float:
    total = float(np.sum(weights))
    if len(weights) == 0 or total <= 0.0:
        return float("nan")
    ordered = np.sort(weights)[::-1]
    return float((np.searchsorted(np.cumsum(ordered), fraction * total) + 1) / len(weights))


def _top_share(weights: np.ndarray, row_fraction: float) -> float:
    total = float(np.sum(weights))
    if len(weights) == 0 or total <= 0.0:
        return float("nan")
    count = max(1, int(math.ceil(row_fraction * len(weights))))
    return float(np.sort(weights)[::-1][:count].sum() / total)


def _summarize_scope(frame: pd.DataFrame, scope: str, controls: dict[str, Any]) -> dict[str, Any]:
    volume = frame["volume_weight"].astype(float).to_numpy()
    density = frame["sector_selected_null_deficit_density"].astype(float).to_numpy()
    selected_volume = frame["sector_selected_null_deficit_density_volume"].astype(float).to_numpy()
    current_volume = frame["sector_abs_current_density_volume"].astype(float).to_numpy()
    pomega_volume = frame["sector_abs_pomega_density_volume"].astype(float).to_numpy()
    rho_plus_p = (frame["sector_rho"].astype(float) + frame["sector_p_l"].astype(float)).to_numpy()
    static_deficit_volume = np.maximum(-rho_plus_p, 0.0) * volume
    current_selected_volume = np.maximum(selected_volume - static_deficit_volume, 0.0)

    active_volume = float(np.sum(volume))
    selected = float(np.sum(selected_volume))
    density_l2_volume = float(np.sum(np.square(density) * volume))
    effective_volume = selected * selected / density_l2_volume if density_l2_volume > 0.0 else float("nan")
    mean_density = selected / active_volume if active_volume > 0.0 else float("nan")

    out = dict(controls)
    out.update({
        "scope": scope,
        "rows": int(len(frame)),
        "active_volume": active_volume,
        "selected_null_deficit": selected,
        "static_null_deficit": float(np.sum(static_deficit_volume)),
        "current_selected_deficit": float(np.sum(current_selected_volume)),
        "current_share_of_selected": (
            float(np.sum(current_selected_volume) / selected) if selected > 0.0 else float("nan")
        ),
        "abs_current": float(np.sum(current_volume)),
        "abs_pomega": float(np.sum(pomega_volume)),
        "mean_selected_density": mean_density,
        "peak_selected_density": float(np.max(density)) if len(density) else float("nan"),
        "peak_to_mean_density": (
            float(np.max(density) / mean_density) if len(density) and mean_density > 0.0 else float("nan")
        ),
        "peak_volume_burden": float(np.max(selected_volume)) if len(selected_volume) else float("nan"),
        "effective_burden_volume": effective_volume,
        "effective_volume_fraction": effective_volume / active_volume if active_volume > 0.0 else float("nan"),
        "rows_for_50pct_burden": _rows_for_fraction(selected_volume, 0.50),
        "rows_for_80pct_burden": _rows_for_fraction(selected_volume, 0.80),
        "top_1pct_burden_share": _top_share(selected_volume, 0.01),
        "top_5pct_burden_share": _top_share(selected_volume, 0.05),
        "top_10pct_burden_share": _top_share(selected_volume, 0.10),
        "current_to_selected_ratio": float(np.sum(current_volume) / selected) if selected > 0.0 else float("nan"),
        "pomega_to_selected_ratio": float(np.sum(pomega_volume) / selected) if selected > 0.0 else float("nan"),
    })
    return out


def _diagnostic_read(row: pd.Series) -> str:
    if int(row.get("positive_packet_norm_live", 0)) > 0:
        return "worsens_live_gate"
    ratio = abs(_finite(row.get("J_delta_fraction_vs_base"), 0.0))
    eff_delta = abs(_finite(row.get("J_effective_volume_fraction_delta_vs_base"), 0.0))
    if ratio < 1.0e-3 and eff_delta < 1.0e-3:
        return "endpoint_invariant_no_relief"
    if _finite(row.get("J_delta_fraction_vs_base"), 0.0) < -2.0e-2:
        return "possible_endpoint_relief"
    return "small_mixed_change"


def _contrast(summary: pd.DataFrame, labels: list[str]) -> pd.DataFrame:
    j = summary.loc[summary["scope"] == "J_total"].copy()
    if j.empty:
        return pd.DataFrame()
    baseline = j.loc[j["label"] == labels[0]]
    if baseline.empty:
        baseline = j.iloc[[0]]
    base = baseline.iloc[0]
    rows: list[dict[str, Any]] = []
    for _, row in j.iterrows():
        label = str(row["label"])
        if label == str(base["label"]):
            change = "baseline"
        elif "receiver" in label:
            change = (
                "receiver "
                f"lapse_log_gain {row['receiver_lapse_log_gain']:.3g}; "
                f"radial_log_gain {row['receiver_radial_log_gain']:.3g}; "
                f"beta_relax {row['receiver_beta_relaxation_gain']:.3g}; "
                f"angular_log_gain {row['receiver_angular_log_gain']:.3g}"
            )
        elif "edge_wide" in label and "ang" in label:
            change = (
                f"edge_width {base['edge_width_multiplier']:.3g}->{row['edge_width_multiplier']:.3g}; "
                f"angular_log_gain {base['angular_log_gain']:.3g}->{row['angular_log_gain']:.3g}"
            )
        elif "edge_wide" in label:
            change = f"edge_width {base['edge_width_multiplier']:.3g}->{row['edge_width_multiplier']:.3g}"
        elif "catch_edge" in label:
            change = (
                f"catch_width {base['catch_width_multiplier']:.3g}->{row['catch_width_multiplier']:.3g}; "
                f"edge_width {base['edge_width_multiplier']:.3g}->{row['edge_width_multiplier']:.3g}"
            )
        elif "edge_soft" in label:
            change = f"edge_carve {base['edge_carve']:.3g}->{row['edge_carve']:.3g}"
        elif "guard_blend" in label:
            change = f"current_guard_fraction {base['current_guard_fraction']:.3g}->{row['current_guard_fraction']:.3g}"
        elif "ang" in label:
            change = f"angular_log_gain {base['angular_log_gain']:.3g}->{row['angular_log_gain']:.3g}"
        elif "temporal" in label:
            change = f"temporal_width {base['temporal_width_multiplier']:.3g}->{row['temporal_width_multiplier']:.3g}"
        elif "hold" in label:
            change = f"release_hold {base['release_matched_hold_widths']:.3g}->{row['release_matched_hold_widths']:.3g}"
        elif "beta" in label:
            change = f"release_beta_width {base['release_beta_width_multiplier']:.3g}->{row['release_beta_width_multiplier']:.3g}"
        elif "lapse_lag" in label:
            change = f"release_lapse_lag {base['release_lapse_lag_widths']:.3g}->{row['release_lapse_lag_widths']:.3g}"
        elif "carve_lag" in label:
            change = f"release_carve_lag {base['release_carve_lag_widths']:.3g}->{row['release_carve_lag_widths']:.3g}"
        elif "lag_pair" in label:
            change = (
                f"release_lapse/carve_lag "
                f"{base['release_lapse_lag_widths']:.3g}/{base['release_carve_lag_widths']:.3g}->"
                f"{row['release_lapse_lag_widths']:.3g}/{row['release_carve_lag_widths']:.3g}"
            )
        else:
            change = "variant"
        out = {
            "label": label,
            "control_change": change,
            "positive_packet_norm_live": int(row["positive_packet_norm_live"]),
            "max_packet_norm_live": float(row["max_packet_norm_live"]),
            "J_selected_null_deficit": float(row["selected_null_deficit"]),
            "J_delta_vs_base": float(row["selected_null_deficit"] - base["selected_null_deficit"]),
            "J_delta_fraction_vs_base": float(
                (row["selected_null_deficit"] - base["selected_null_deficit"]) / base["selected_null_deficit"]
            ),
            "J_mean_density_delta_vs_base": float(row["mean_selected_density"] - base["mean_selected_density"]),
            "J_peak_density_delta_vs_base": float(row["peak_selected_density"] - base["peak_selected_density"]),
            "J_effective_volume_fraction": float(row["effective_volume_fraction"]),
            "J_effective_volume_fraction_delta_vs_base": float(
                row["effective_volume_fraction"] - base["effective_volume_fraction"]
            ),
            "J_rows_for_50pct_burden": float(row["rows_for_50pct_burden"]),
            "J_rows_for_80pct_burden": float(row["rows_for_80pct_burden"]),
            "J_current_share_of_selected": float(row["current_share_of_selected"]),
            "J_current_to_selected_ratio": float(row["current_to_selected_ratio"]),
            "J_pomega_to_selected_ratio": float(row["pomega_to_selected_ratio"]),
        }
        out["diagnostic_read"] = _diagnostic_read(pd.Series(out))
        rows.append(out)
    return pd.DataFrame(rows)


def build_endpoint_coupling_diagnostic(
    *,
    ledger_root: Path,
    intermediate_dir: Path,
    labels: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    selected_labels = _load_labels(ledger_root, labels)
    point_path = intermediate_dir / "intermediate_source_point_sector_stress.csv"
    sectors = pd.read_csv(point_path)
    rows: list[dict[str, Any]] = []
    for label in selected_labels:
        controls = _control_row(ledger_root, label)
        j = sectors.loc[(sectors["label"].astype(str) == label) & (sectors["sector"].astype(str) == J_SECTOR)].copy()
        for scope, assignment in SCOPES.items():
            frame = j if assignment is None else j.loc[j["assignment"].astype(str) == assignment].copy()
            rows.append(_summarize_scope(frame, scope, controls))
    summary = pd.DataFrame(rows)
    contrast = _contrast(summary, selected_labels)
    metadata = {
        "ledger_root": str(ledger_root),
        "intermediate_dir": str(intermediate_dir),
        "point_sector_stress": str(point_path),
        "point_sector_stress_sha256": _sha256_file(point_path),
        "labels": selected_labels,
        "note": (
            "Endpoint effective-coupling proxy. It tests whether the demanded J-layer "
            "burden dilutes over active/effective support volume under thickness and "
            "coupling knobs; it is not a continuum stress-energy conservation proof."
        ),
    }
    return summary, contrast, metadata


def write_outputs(outdir: Path, summary: pd.DataFrame, contrast: pd.DataFrame, metadata: dict[str, Any]) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    files = {
        "summary": outdir / "endpoint_coupling_diagnostic_summary.csv",
        "contrast": outdir / "endpoint_coupling_diagnostic_contrast.csv",
        "manifest": outdir / "endpoint_coupling_diagnostic_manifest.json",
    }
    summary.to_csv(files["summary"], index=False)
    contrast.to_csv(files["contrast"], index=False)
    manifest = dict(metadata)
    manifest["files"] = {key: str(path) for key, path in files.items() if key != "manifest"}
    files["manifest"].write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build endpoint J-layer effective-volume and coupling proxy diagnostics."
    )
    parser.add_argument("--ledger-root", type=Path, required=True)
    parser.add_argument("--intermediate-dir", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--label", action="append", default=None, help="Optional label filter; repeat to include many.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary, contrast, metadata = build_endpoint_coupling_diagnostic(
        ledger_root=args.ledger_root,
        intermediate_dir=args.intermediate_dir,
        labels=args.label,
    )
    files = write_outputs(args.outdir, summary, contrast, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {
            "summary": int(len(summary)),
            "contrast": int(len(contrast)),
        },
        "files": {key: str(path) for key, path in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
