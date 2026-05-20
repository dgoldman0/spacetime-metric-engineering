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

from adm_harness.source_screening import resolve_manifest_path  # noqa: E402


J_SECTOR = "J_endpoint_junction_layer"
SUPPORT_ASSIGNMENT = "support_edge_endpoint_junction"
RESET_ASSIGNMENT = "reset_decompression_endpoint_junction"
TARGET_COLUMNS = {
    "selected": "sector_selected_null_deficit_density_volume",
    "current": "sector_abs_current_density_volume",
    "angular": "sector_abs_pomega_density_volume",
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


def _safe_ratio(num: float, denom: float) -> float:
    return float(num / denom) if denom > 0.0 else float("nan")


def _bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin({"1", "true", "yes"})


def _load_point_ledger(ledger_root: Path, label: str) -> pd.DataFrame:
    manifest_path = ledger_root / label / "source_ledger_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    value = manifest.get("files", {}).get("point_ledger", "source_ledger_point_ledger.csv")
    point_path = resolve_manifest_path(manifest_path.parent, value)
    points = pd.read_csv(point_path)
    points["point_index"] = np.arange(len(points), dtype=int)
    return points


def _load_j(intermediate_dir: Path, label: str, assignment: str) -> pd.DataFrame:
    sectors = pd.read_csv(intermediate_dir / "intermediate_source_point_sector_stress.csv")
    frame = sectors.loc[
        (sectors["label"].astype(str) == label)
        & (sectors["sector"].astype(str) == J_SECTOR)
        & (sectors["assignment"].astype(str) == assignment)
    ].copy()
    return frame


def _positive_delta(
    *,
    base: pd.DataFrame,
    variant: pd.DataFrame,
    target_col: str,
    mode: str,
) -> pd.DataFrame:
    joined = base[["point_index", target_col]].merge(
        variant[["point_index", target_col]],
        on="point_index",
        how="outer",
        suffixes=("_base", "_variant"),
    ).fillna(0.0)
    if mode == "base_minus_variant":
        joined["delta"] = joined[f"{target_col}_base"] - joined[f"{target_col}_variant"]
    elif mode == "variant_minus_base":
        joined["delta"] = joined[f"{target_col}_variant"] - joined[f"{target_col}_base"]
    else:
        raise ValueError(f"Unknown delta mode: {mode}")
    joined["positive_delta"] = joined["delta"].clip(lower=0.0)
    return joined[["point_index", "delta", "positive_delta"]]


def _scale(values: pd.Series) -> pd.Series:
    numeric = values.astype(float).replace([np.inf, -np.inf], np.nan).fillna(0.0).clip(lower=0.0)
    max_value = float(numeric.max()) if len(numeric) else 0.0
    if max_value <= 0.0:
        return pd.Series(np.zeros(len(numeric), dtype=float), index=numeric.index)
    return numeric / max_value


def _context_for_support(points: pd.DataFrame, support_points: pd.Series) -> pd.DataFrame:
    usecols = [
        "point_index",
        "s",
        "l",
        "stage",
        "region",
        "inside_packet_live",
        "inside_packet_geom",
        "volume_weight",
        "release_profile_slope_abs",
        "beta",
        "beta_base",
        "beta_pre_packet_rematch",
        "standing_support_packet_smooth_split_edge_window",
        "standing_support_packet_smooth_split_guarded_edge_window",
        "standing_support_packet_smooth_split_angular_window",
        "standing_support_packet_smooth_split_current_guard_window",
        "standing_support_packet_radial_window",
        "standing_support_packet_radial_shoulder_window",
        "standing_support_packet_beta_rematch_window",
        "support_edge_receiver_memory_driver",
        "support_edge_receiver_radial_cap_window",
        "support_edge_receiver_angular_flange_window",
    ]
    present = [col for col in usecols if col in points.columns]
    out = points.loc[points["point_index"].isin(set(support_points.astype(int))), present].copy()
    out["inside_packet_live"] = _bool_series(out["inside_packet_live"]) if "inside_packet_live" in out else False
    out["inside_packet_geom"] = _bool_series(out["inside_packet_geom"]) if "inside_packet_geom" in out else False
    out["beta_delta_abs"] = (
        out.get("beta", 0.0).astype(float) - out.get("beta_base", 0.0).astype(float)
    ).abs()
    out["beta_release_abs"] = (
        out.get("beta_pre_packet_rematch", out.get("beta", 0.0)).astype(float)
        - out.get("beta_base", 0.0).astype(float)
    ).abs()
    return out


def _add_basis_columns(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    release_slope = _scale(out.get("release_profile_slope_abs", pd.Series(0.0, index=out.index)))
    beta_delta = _scale(out.get("beta_delta_abs", pd.Series(0.0, index=out.index)))
    beta_release = _scale(out.get("beta_release_abs", pd.Series(0.0, index=out.index)))
    edge = _scale(out.get("standing_support_packet_smooth_split_edge_window", pd.Series(0.0, index=out.index)))
    guarded_edge = _scale(
        out.get("standing_support_packet_smooth_split_guarded_edge_window", pd.Series(0.0, index=out.index))
    )
    radial = _scale(out.get("standing_support_packet_radial_window", pd.Series(0.0, index=out.index)))
    radial_shoulder = _scale(
        out.get("standing_support_packet_radial_shoulder_window", pd.Series(0.0, index=out.index))
    )
    beta_rematch = _scale(out.get("standing_support_packet_beta_rematch_window", pd.Series(0.0, index=out.index)))
    angular_window = _scale(
        out.get("standing_support_packet_smooth_split_angular_window", pd.Series(0.0, index=out.index))
    )
    guard_window = _scale(
        out.get("standing_support_packet_smooth_split_current_guard_window", pd.Series(0.0, index=out.index))
    )
    receiver_memory = _scale(out.get("support_edge_receiver_memory_driver", pd.Series(0.0, index=out.index)))
    receiver_radial = _scale(out.get("support_edge_receiver_radial_cap_window", pd.Series(0.0, index=out.index)))
    receiver_angular = _scale(out.get("support_edge_receiver_angular_flange_window", pd.Series(0.0, index=out.index)))
    non_live = (~_bool_series(out.get("inside_packet_live", pd.Series(False, index=out.index)))).astype(float)
    stage = out.get("stage", pd.Series("", index=out.index)).astype(str)
    post_release = stage.eq("post_release_buffer").astype(float)
    release_or_post = stage.isin({"release_shift_fade", "post_release_buffer"}).astype(float)
    release_to_post_tail = np.maximum(release_slope.to_numpy(), post_release.to_numpy())
    l_abs = out.get("l", pd.Series(0.0, index=out.index)).astype(float).abs()
    l_outer = _scale(l_abs)
    l_positive = (out.get("l", pd.Series(0.0, index=out.index)).astype(float) > 0.0).astype(float)
    l_negative = (out.get("l", pd.Series(0.0, index=out.index)).astype(float) < 0.0).astype(float)

    out["basis_release_slope"] = release_slope * non_live
    out["basis_beta_delta"] = beta_delta * non_live
    out["basis_beta_release"] = beta_release * non_live
    out["basis_support_edge_cap_uniform"] = non_live
    out["basis_post_release_cap"] = post_release * non_live
    out["basis_release_or_post_cap"] = release_or_post * non_live
    out["basis_release_tail_cap"] = release_to_post_tail * non_live
    out["basis_post_release_outer_cap"] = post_release * l_outer * non_live
    out["basis_release_or_post_outer_cap"] = release_or_post * l_outer * non_live
    out["basis_release_tail_outer_cap"] = release_to_post_tail * l_outer * non_live
    out["basis_post_release_pos_outer_cap"] = post_release * l_positive * l_outer * non_live
    out["basis_post_release_neg_outer_cap"] = post_release * l_negative * l_outer * non_live
    out["basis_release_or_post_pos_outer_cap"] = release_or_post * l_positive * l_outer * non_live
    out["basis_release_or_post_neg_outer_cap"] = release_or_post * l_negative * l_outer * non_live
    out["basis_release_x_edge"] = release_slope * edge * non_live
    out["basis_release_x_guarded_edge"] = release_slope * guarded_edge * non_live
    out["basis_release_x_radial"] = release_slope * radial * non_live
    out["basis_release_x_radial_shoulder"] = release_slope * radial_shoulder * non_live
    out["basis_beta_delta_x_edge"] = beta_delta * edge * non_live
    out["basis_beta_delta_x_radial"] = beta_delta * radial * non_live
    out["basis_beta_release_x_edge"] = beta_release * edge * non_live
    out["basis_beta_release_x_radial"] = beta_release * radial * non_live
    out["basis_beta_rematch_x_edge"] = beta_rematch * edge * non_live
    out["basis_angular_window"] = angular_window * non_live
    out["basis_guard_window"] = guard_window * non_live
    out["basis_receiver_memory"] = receiver_memory * non_live
    out["basis_receiver_radial_cap"] = receiver_radial * non_live
    out["basis_receiver_angular_flange"] = receiver_angular * non_live
    return out


def _distribution_metrics(target: pd.Series, weight: pd.Series) -> dict[str, float]:
    t = target.astype(float).clip(lower=0.0).to_numpy()
    w = weight.astype(float).clip(lower=0.0).to_numpy()
    total_t = float(t.sum())
    total_w = float(w.sum())
    if total_t <= 0.0 or total_w <= 0.0:
        return {
            "fit_scale": float("nan"),
            "normalized_l1_error": float("nan"),
            "distribution_overlap": float("nan"),
            "top_10pct_target_share_by_basis": float("nan"),
            "top_20pct_target_share_by_basis": float("nan"),
            "basis_rows_for_50pct_weight": float("nan"),
            "basis_rows_for_80pct_weight": float("nan"),
            "pearson_corr": float("nan"),
        }
    denom = float(np.dot(w, w))
    scale = float(np.dot(t, w) / denom) if denom > 0.0 else float("nan")
    pred = np.clip(scale, 0.0, np.inf) * w
    l1 = float(np.abs(t - pred).sum() / total_t)
    tn = t / total_t
    wn = w / total_w
    overlap = float(np.minimum(tn, wn).sum())
    order = np.argsort(w)[::-1]
    n = len(order)
    top_10 = max(1, int(math.ceil(0.10 * n)))
    top_20 = max(1, int(math.ceil(0.20 * n)))
    top_10_share = float(t[order[:top_10]].sum() / total_t)
    top_20_share = float(t[order[:top_20]].sum() / total_t)
    cumulative = np.cumsum(w[order])
    rows_50 = float((np.searchsorted(cumulative, 0.50 * total_w) + 1) / n)
    rows_80 = float((np.searchsorted(cumulative, 0.80 * total_w) + 1) / n)
    corr = float(np.corrcoef(t, w)[0, 1]) if np.std(t) > 0.0 and np.std(w) > 0.0 else float("nan")
    return {
        "fit_scale": scale,
        "normalized_l1_error": l1,
        "distribution_overlap": overlap,
        "top_10pct_target_share_by_basis": top_10_share,
        "top_20pct_target_share_by_basis": top_20_share,
        "basis_rows_for_50pct_weight": rows_50,
        "basis_rows_for_80pct_weight": rows_80,
        "pearson_corr": corr,
    }


def _rows_for_transfer_summary(
    *,
    label: str,
    base_reset: pd.DataFrame,
    variant_reset: pd.DataFrame,
    base_support: pd.DataFrame,
    variant_support: pd.DataFrame,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for target, col in TARGET_COLUMNS.items():
        reset = _positive_delta(base=base_reset, variant=variant_reset, target_col=col, mode="base_minus_variant")
        support = _positive_delta(base=base_support, variant=variant_support, target_col=col, mode="variant_minus_base")
        reset_total = float(reset["positive_delta"].sum())
        support_total = float(support["positive_delta"].sum())
        rows.append({
            "label": label,
            "target": target,
            "reset_relief": reset_total,
            "support_transfer": support_total,
            "support_transfer_per_reset_relief": _safe_ratio(support_total, reset_total),
            "net_j_relief": reset_total - support_total,
            "net_j_relief_per_reset_relief": _safe_ratio(reset_total - support_total, reset_total),
            "reset_changed_points": int((reset["positive_delta"] > 0.0).sum()),
            "support_changed_points": int((support["positive_delta"] > 0.0).sum()),
        })
    return rows


def build_receiver_basis(
    *,
    ledger_root: Path,
    intermediate_dir: Path,
    base_label: str,
    variant_labels: list[str],
) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    base_reset = _load_j(intermediate_dir, base_label, RESET_ASSIGNMENT)
    base_support = _load_j(intermediate_dir, base_label, SUPPORT_ASSIGNMENT)
    transfer_rows: list[dict[str, Any]] = []
    basis_rows: list[dict[str, Any]] = []
    point_frames: list[pd.DataFrame] = []

    for label in variant_labels:
        variant_reset = _load_j(intermediate_dir, label, RESET_ASSIGNMENT)
        variant_support = _load_j(intermediate_dir, label, SUPPORT_ASSIGNMENT)
        transfer_rows.extend(
            _rows_for_transfer_summary(
                label=label,
                base_reset=base_reset,
                variant_reset=variant_reset,
                base_support=base_support,
                variant_support=variant_support,
            )
        )

        support_points = variant_support["point_index"]
        context = _context_for_support(_load_point_ledger(ledger_root, label), support_points)
        frame = variant_support[[
            "point_index",
            "s",
            "l",
            "stage",
            "region",
            "inside_packet_live",
            "volume_weight",
        ]].merge(context.drop(columns=[col for col in ["s", "l", "stage", "region", "inside_packet_live", "volume_weight"] if col in context.columns]), on="point_index", how="left")
        frame["label"] = label
        frame = _add_basis_columns(frame)

        for target, col in TARGET_COLUMNS.items():
            support_delta = _positive_delta(
                base=base_support,
                variant=variant_support,
                target_col=col,
                mode="variant_minus_base",
            ).rename(columns={"positive_delta": f"target_{target}_transfer", "delta": f"target_{target}_raw_delta"})
            frame = frame.merge(support_delta, on="point_index", how="left")
            frame[f"target_{target}_transfer"] = frame[f"target_{target}_transfer"].fillna(0.0)
            frame[f"target_{target}_raw_delta"] = frame[f"target_{target}_raw_delta"].fillna(0.0)

        basis_cols = [col for col in frame.columns if col.startswith("basis_")]
        live = _bool_series(frame["inside_packet_live"])
        for target in TARGET_COLUMNS:
            target_col = f"target_{target}_transfer"
            target_total = float(frame[target_col].sum())
            for basis_col in basis_cols:
                metrics = _distribution_metrics(frame[target_col], frame[basis_col])
                weight_total = float(frame[basis_col].sum())
                live_weight = float(frame.loc[live, basis_col].sum())
                basis_rows.append({
                    "label": label,
                    "target": target,
                    "basis": basis_col.replace("basis_", ""),
                    "target_transfer": target_total,
                    "basis_weight_total": weight_total,
                    "basis_live_weight_fraction": _safe_ratio(live_weight, weight_total),
                    **metrics,
                })
        point_frames.append(frame)

    outputs = {
        "transfer_summary": pd.DataFrame(transfer_rows),
        "basis_summary": pd.DataFrame(basis_rows),
        "point_basis": pd.concat(point_frames, ignore_index=True) if point_frames else pd.DataFrame(),
    }
    metadata = {
        "ledger_root": ledger_root,
        "intermediate_dir": intermediate_dir,
        "base_label": base_label,
        "variant_labels": variant_labels,
        "target_columns": TARGET_COLUMNS,
        "note": (
            "First-pass beta-coupled support-edge receiver diagnostic. Candidate basis weights "
            "are overlap tests against observed support-edge transfer, not physical source terms."
        ),
    }
    return outputs, metadata


def write_outputs(outdir: Path, outputs: dict[str, pd.DataFrame], metadata: dict[str, Any]) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    paths = {
        "transfer_summary": outdir / "beta_support_receiver_transfer_summary.csv",
        "basis_summary": outdir / "beta_support_receiver_basis_summary.csv",
        "point_basis": outdir / "beta_support_receiver_point_basis.csv",
    }
    for key, path in paths.items():
        outputs.get(key, pd.DataFrame()).to_csv(path, index=False)
    manifest_path = outdir / "beta_support_receiver_basis_manifest.json"
    manifest = {
        "ledger_root": str(metadata["ledger_root"]),
        "intermediate_dir": str(metadata["intermediate_dir"]),
        "base_label": metadata["base_label"],
        "variant_labels": metadata["variant_labels"],
        "target_columns": metadata["target_columns"],
        "note": metadata["note"],
        "files": {key: str(path) for key, path in paths.items()},
        "rows": {key: int(len(outputs.get(key, pd.DataFrame()))) for key in paths},
        "sha256": {key: _sha256_file(path) for key, path in paths.items()},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    paths["manifest"] = manifest_path
    return paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a beta-coupled support-edge receiver-basis diagnostic."
    )
    parser.add_argument("--ledger-root", type=Path, required=True)
    parser.add_argument("--intermediate-dir", type=Path, required=True)
    parser.add_argument("--base-label", default="codesign_base_beta025")
    parser.add_argument(
        "--variant-label",
        action="append",
        default=None,
        help="Variant label to compare against the base. Repeat to include multiple variants.",
    )
    parser.add_argument("--outdir", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    variants = args.variant_label or ["codesign_beta075", "codesign_beta100"]
    outputs, metadata = build_receiver_basis(
        ledger_root=args.ledger_root,
        intermediate_dir=args.intermediate_dir,
        base_label=args.base_label,
        variant_labels=variants,
    )
    files = write_outputs(args.outdir, outputs, metadata)
    print(json.dumps({
        "ok": True,
        "outdir": str(args.outdir),
        "rows": {key: int(len(value)) for key, value in outputs.items()},
        "files": {key: str(path) for key, path in files.items()},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
