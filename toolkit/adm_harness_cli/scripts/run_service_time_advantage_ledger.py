from __future__ import annotations

import argparse
import json
import math
import subprocess
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def _git_commit(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return None
    return result.stdout.strip() or None


def _bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.lower().isin({"true", "1", "yes"})


def _load_manifest(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _release_choreography_enabled(params: dict[str, Any]) -> bool:
    return str(params.get("release_choreography_mode", "legacy")).strip().lower() not in {"legacy", "off", "none"}


def _release_beta_interval(params: dict[str, Any]) -> tuple[float, float]:
    x_beta = float(params.get("x_beta", 0.7))
    w_beta = float(params.get("w_beta", 0.18))
    hold_widths = float(params.get("release_matched_hold_widths", 0.0))
    if not _release_choreography_enabled(params):
        return x_beta - 2.0 * w_beta, x_beta + 2.0 * w_beta
    start = x_beta + hold_widths * w_beta
    duration = max(4.0 * w_beta * float(params.get("release_beta_width_multiplier", 1.0)), 1.0e-12)
    return start, start + duration


def _live_bounds(points: pd.DataFrame, manifest: dict[str, Any]) -> tuple[float, float, str]:
    params = dict(manifest.get("params", {}))
    live = points.loc[points["inside_packet_live_bool"]]
    observed_start = float(live["s"].min()) if len(live) else float(points["s"].min())
    observed_end = float(live["s"].max()) if len(live) else float(points["s"].max())
    if not params:
        return observed_start, observed_end, "observed_live_grid"
    start = params.get("live_packet_start")
    departure = float(start) if start is not None else observed_start
    _release_start, release_end = _release_beta_interval(params)
    arrival = release_end + float(params.get("live_packet_end_margin_widths", 2.0)) * float(params.get("w_beta", 0.18))
    return departure, arrival, "manifest_schedule"


def _centerline(points: pd.DataFrame) -> pd.DataFrame:
    rows: list[pd.Series] = []
    for _s, group in points.groupby("s", sort=True):
        index = (group["l"] - group["s"]).abs().to_numpy().argmin()
        rows.append(group.iloc[int(index)])
    center = pd.DataFrame(rows).sort_values("s").copy()
    center["packet_coord_proxy_speed"] = center["U_packet"] / np.maximum(center["B"], 1.0e-12)
    center["centerline_speed"] = 1.0
    return center


def _interp_series(x: np.ndarray, y: np.ndarray, x_value: float) -> float:
    if x_value <= x[0]:
        return float(y[0])
    if x_value >= x[-1]:
        return float(y[-1])
    return float(np.interp(x_value, x, y))


def _integrate(center: pd.DataFrame, column: str, start: float, end: float) -> float:
    if end <= start:
        return 0.0
    x_all = center["s"].to_numpy(dtype=float)
    y_all = center[column].to_numpy(dtype=float)
    mask = (x_all > start) & (x_all < end)
    x = np.concatenate([[start], x_all[mask], [end]])
    y = np.concatenate([
        [_interp_series(x_all, y_all, start)],
        y_all[mask],
        [_interp_series(x_all, y_all, end)],
    ])
    order = np.argsort(x)
    return float(np.trapezoid(y[order], x[order]))


def _prepare_points(path: Path) -> pd.DataFrame:
    points = pd.read_csv(path)
    required = ["s", "l", "U_packet", "B", "inside_packet_live"]
    missing = [column for column in required if column not in points.columns]
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")
    for column in ["s", "l", "U_packet", "B"]:
        points[column] = pd.to_numeric(points[column], errors="coerce")
    points = points.dropna(subset=["s", "l", "U_packet", "B"]).copy()
    points["stage"] = points["stage"].astype(str) if "stage" in points else ""
    points["region"] = points["region"].astype(str) if "region" in points else ""
    points["inside_packet_live_bool"] = _bool_series(points["inside_packet_live"])
    return points


def _case_row(path: Path, label: str, manifest_path: Path | None) -> tuple[dict[str, Any], pd.DataFrame]:
    points = _prepare_points(path)
    manifest = _load_manifest(manifest_path)
    params = dict(manifest.get("params", {}))
    center = _centerline(points)
    departure_s, arrival_s, boundary_source = _live_bounds(points, manifest)
    request_start_s = float(points["s"].min())
    prepared_time = arrival_s - departure_s
    request_triggered_time = arrival_s - request_start_s
    schedule_distance = _integrate(center, "U_packet", departure_s, arrival_s)
    coord_distance = _integrate(center, "packet_coord_proxy_speed", departure_s, arrival_s)
    centerline_distance = max(arrival_s - departure_s, 0.0)
    request_schedule_distance = schedule_distance
    request_coord_distance = coord_distance
    live_slice = center[(center["s"] >= departure_s) & (center["s"] <= arrival_s)].copy()
    plateau_schedule_speed = float(params.get("V", live_slice["U_packet"].max() if len(live_slice) else math.nan))
    departure_coord_speed = _interp_series(
        center["s"].to_numpy(dtype=float),
        center["packet_coord_proxy_speed"].to_numpy(dtype=float),
        departure_s,
    )
    schedule_ratio = schedule_distance / prepared_time if prepared_time > 0.0 else math.nan
    coord_ratio = coord_distance / prepared_time if prepared_time > 0.0 else math.nan
    if schedule_ratio > 1.0 and coord_ratio > 1.0:
        decision = "advantage_under_schedule_and_packet_coord_proxy"
    elif schedule_ratio > 1.0:
        decision = "advantage_under_schedule_factor_proxy_only"
    else:
        decision = "no_service_time_advantage_in_tested_proxies"
    row = {
        "label": label,
        "point_ledger": str(path),
        "manifest": str(manifest_path) if manifest_path else "",
        "boundary_source": boundary_source,
        "departure_s": departure_s,
        "arrival_s": arrival_s,
        "request_start_s": request_start_s,
        "prepared_service_time": prepared_time,
        "request_triggered_service_time": request_triggered_time,
        "schedule_factor_distance": schedule_distance,
        "packet_coord_proxy_distance": coord_distance,
        "centerline_l_equals_s_distance": centerline_distance,
        "request_schedule_factor_distance": request_schedule_distance,
        "request_packet_coord_proxy_distance": request_coord_distance,
        "schedule_factor_advantage_ratio": schedule_ratio,
        "packet_coord_proxy_advantage_ratio": coord_ratio,
        "centerline_control_ratio": centerline_distance / prepared_time if prepared_time > 0.0 else math.nan,
        "request_schedule_factor_advantage_ratio": (
            request_schedule_distance / request_triggered_time if request_triggered_time > 0.0 else math.nan
        ),
        "request_packet_coord_proxy_advantage_ratio": (
            request_coord_distance / request_triggered_time if request_triggered_time > 0.0 else math.nan
        ),
        "plateau_schedule_speed": plateau_schedule_speed,
        "departure_packet_coord_proxy_speed": departure_coord_speed,
        "max_live_packet_coord_proxy_speed": float(live_slice["packet_coord_proxy_speed"].max()) if len(live_slice) else math.nan,
        "mean_live_packet_coord_proxy_speed": float(live_slice["packet_coord_proxy_speed"].mean()) if len(live_slice) else math.nan,
        "decision": decision,
        "caveat": (
            "Operational service-time rating only; not a packet-safety, finite-bundle, "
            "source-family, global-horizon, or physical matter-model gate."
        ),
    }
    return row, center


def _extension_rows(summary: pd.DataFrame, extensions: list[float]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for _, case in summary.iterrows():
        for extension in extensions:
            extension = float(extension)
            time = float(case["prepared_service_time"]) + extension
            schedule_distance = float(case["schedule_factor_distance"]) + float(case["plateau_schedule_speed"]) * extension
            coord_distance = (
                float(case["packet_coord_proxy_distance"])
                + float(case["departure_packet_coord_proxy_speed"]) * extension
            )
            rows.append({
                "label": case["label"],
                "plateau_extension_time": extension,
                "prepared_service_time_with_extension": time,
                "schedule_factor_distance_with_extension": schedule_distance,
                "packet_coord_proxy_distance_with_extension": coord_distance,
                "schedule_factor_advantage_ratio": schedule_distance / time if time > 0.0 else math.nan,
                "packet_coord_proxy_advantage_ratio": coord_distance / time if time > 0.0 else math.nan,
            })
    return pd.DataFrame(rows)


def _markdown_report(summary: pd.DataFrame, extension: pd.DataFrame) -> str:
    lines = [
        "# Stage II Service-Time Advantage Ledger",
        "",
        "## Purpose",
        "",
        "This ledger asks the operational A-to-B question: for the reconstructed packet service sequence, "
        "does the restored arrival event beat an exterior null reference signal over the same inferred endpoint separation?",
        "",
        "This is a narrative/rating ledger. It is not a packet-timelikeness, dense-bundle, source-family, "
        "global-horizon, or physical matter-model gate.",
        "",
        "## Main Summary",
        "",
    ]
    cols = [
        "label",
        "prepared_service_time",
        "schedule_factor_distance",
        "schedule_factor_advantage_ratio",
        "packet_coord_proxy_distance",
        "packet_coord_proxy_advantage_ratio",
        "centerline_control_ratio",
        "decision",
    ]
    lines.append(summary[cols].to_markdown(index=False))
    lines.extend([
        "",
        "## Request-Triggered Accounting",
        "",
        "Prepared standing-plant time can be accounted separately. If setup is request-triggered, "
        "the service clock starts at the first sampled setup row.",
        "",
    ])
    request_cols = [
        "label",
        "request_triggered_service_time",
        "request_schedule_factor_distance",
        "request_schedule_factor_advantage_ratio",
        "request_packet_coord_proxy_distance",
        "request_packet_coord_proxy_advantage_ratio",
    ]
    lines.append(summary[request_cols].to_markdown(index=False))
    lines.extend([
        "",
        "## Plateau Extension Check",
        "",
        "The extension table inserts additional carried-shift duration at the observed schedule plateau. "
        "It shows the long-baseline trend without rebuilding a longer metric ledger.",
        "",
    ])
    ext_cols = [
        "label",
        "plateau_extension_time",
        "schedule_factor_advantage_ratio",
        "packet_coord_proxy_advantage_ratio",
    ]
    lines.append(extension[ext_cols].to_markdown(index=False))
    lines.extend([
        "",
        "## Interpretation",
        "",
        "The schedule-factor distance is the direct service-factor A-to-B rating. The packet-coordinate proxy "
        "uses the centerline `U_packet / B` comparison from the source ledger. The strict centerline control "
        "uses the modeled tube relation `l = s`; it is expected to sit at unity and is included to keep the "
        "coordinate bookkeeping honest.",
        "",
    ])
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build an operational service-time advantage ledger.")
    parser.add_argument("--point-ledger", type=Path, action="append", required=True)
    parser.add_argument("--label", action="append", required=True)
    parser.add_argument("--manifest", type=Path, action="append", default=[])
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--plateau-extension", type=float, action="append", default=[0.0, 1.0, 3.0, 10.0, 100.0])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if len(args.point_ledger) != len(args.label):
        raise SystemExit("--point-ledger and --label counts must match")
    if args.manifest and len(args.manifest) != len(args.point_ledger):
        raise SystemExit("--manifest count must match --point-ledger count when provided")
    manifests = args.manifest or [None] * len(args.point_ledger)
    started = time.perf_counter()
    rows: list[dict[str, Any]] = []
    center_paths: dict[str, str] = {}
    args.outdir.mkdir(parents=True, exist_ok=True)
    for path, label, manifest in zip(args.point_ledger, args.label, manifests):
        row, center = _case_row(path, label, manifest)
        rows.append(row)
        center_path = args.outdir / f"{label}_service_time_centerline.csv"
        center.to_csv(center_path, index=False)
        center_paths[label] = str(center_path)
    summary = pd.DataFrame(rows)
    extension = _extension_rows(summary, args.plateau_extension)
    paths = {
        "summary": args.outdir / "service_time_advantage_summary.csv",
        "plateau_extension": args.outdir / "service_time_plateau_extension.csv",
        "report": args.outdir / "service_time_advantage_report.md",
        "metadata": args.outdir / "service_time_advantage_metadata.json",
    }
    summary.to_csv(paths["summary"], index=False)
    extension.to_csv(paths["plateau_extension"], index=False)
    paths["report"].write_text(_markdown_report(summary, extension), encoding="utf-8")
    repo_root = Path(__file__).resolve().parents[3]
    paths["metadata"].write_text(
        json.dumps(
            {
                "cases": [
                    {"label": label, "point_ledger": str(path), "manifest": str(manifest) if manifest else ""}
                    for path, label, manifest in zip(args.point_ledger, args.label, manifests)
                ],
                "plateau_extensions": args.plateau_extension,
                "centerline_files": center_paths,
                "elapsed_s": round(time.perf_counter() - started, 3),
                "commit": _git_commit(repo_root),
                "files": {key: str(value) for key, value in paths.items() if key != "metadata"},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "outdir": str(args.outdir), "cases": len(summary)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
