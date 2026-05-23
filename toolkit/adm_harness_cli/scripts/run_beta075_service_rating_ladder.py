from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
REPO_ROOT = PACKAGE_ROOT.parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from adm_harness.beta075_first_order_3p1_coupling import (  # noqa: E402
    FirstOrder3P1Inputs,
    FirstOrder3P1RunSpec,
    FirstOrder3P1Spec,
    build_first_order_3p1_coupling,
    write_first_order_3p1_coupling_outputs,
)
from adm_harness.beta075_moderate_3p1_capstone import (  # noqa: E402
    Moderate3P1Inputs,
    Moderate3P1Spec,
    Moderate3P1SurfaceSpec,
    run_moderate_3p1_v5_capstone,
    service_label,
)
from adm_harness.source_ledger import sha256_file, write_manifest  # noqa: E402


DEFAULT_SOURCE_MANIFEST = Path(
    "toolkit/adm_harness_cli/runs/scheduled_adm_confidence_beta075_s15_189x121/"
    "ledgers/horizon_escape_beta075_p003_mid/source_ledger_manifest.json"
)
DEFAULT_EQUATION_DIR = Path("toolkit/adm_harness_cli/runs/stage2_beta075_source_family_equations")
DEFAULT_ENERGY_DIR = Path("toolkit/adm_harness_cli/runs/stage2_beta075_source_family_energy_constant_audit")
DEFAULT_CANDIDATE = "rematch_w6_t1p5:gain=1.8,width=6.0,temporal=1.5,floor=0.6,shape=trailing_edge"


def _truth(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _stage(status_rows: list[dict[str, Any]], name: str, status: str, **values: Any) -> None:
    row = {"stage": name, "status": status}
    row.update(values)
    status_rows.append(row)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _write_status(outdir: Path, status_rows: list[dict[str, Any]], final_status: str, **extra: Any) -> dict[str, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    status_csv = outdir / "beta075_service_rating_ladder_status.csv"
    status_json = outdir / "beta075_service_rating_ladder_status.json"
    pd.DataFrame(status_rows).to_csv(status_csv, index=False)
    payload = {
        "final_status": final_status,
        "stages": status_rows,
        **extra,
    }
    status_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"status_csv": status_csv, "status_json": status_json}


def _run_command(cmd: list[str], stage: str, status_rows: list[dict[str, Any]]) -> None:
    print(json.dumps({"event": "stage_start", "stage": stage, "cmd": cmd}), flush=True)
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)
    _stage(status_rows, stage, "pass")
    print(json.dumps({"event": "stage_pass", "stage": stage}), flush=True)


def _candidate_label(candidate: str) -> str:
    label, sep, _body = candidate.partition(":")
    if not sep or not label.strip():
        raise ValueError(f"candidate must look like label:key=value,key=value, got {candidate!r}")
    return label.strip()


def _float_token(value: float) -> str:
    text = f"{float(value):.10g}"
    return text.replace("-", "m").replace("+", "").replace(".", "p").replace("e", "e")


def _clone_source_manifest(base_manifest: Path, outdir: Path, service_rating: float) -> Path:
    manifest = _read_json(base_manifest)
    params = dict(manifest.get("params", {}))
    params["V"] = float(service_rating)
    manifest["params"] = params
    base_case = str(manifest.get("case", "horizon_escape_beta075_p003_mid"))
    base_case = base_case.replace("V5_", "")
    label = service_label(service_rating)
    manifest["case"] = f"V{_float_token(service_rating)}_{base_case}"
    manifest["note"] = (
        f"V={service_rating:g} service-rating clone of the beta075 p003 mid source manifest; "
        "all non-service parameters are inherited for a fresh same-quality ladder."
    )
    manifest["parent_source_manifest"] = str(base_manifest)
    manifest["service_rating"] = float(service_rating)
    outdir.mkdir(parents=True, exist_ok=True)
    cloned = outdir / f"source_manifest_{label}_from_horizon_escape_beta075_p003_mid.json"
    write_manifest(cloned, manifest)
    return cloned


def _source_safety_pass(path: Path) -> tuple[bool, dict[str, Any]]:
    safety = pd.read_csv(path)
    positive = int(pd.to_numeric(safety["positive_packet_norm_live"], errors="coerce").fillna(0).max())
    max_packet = float(pd.to_numeric(safety["max_packet_norm_live"], errors="coerce").max())
    live_points = int(pd.to_numeric(safety["live_points"], errors="coerce").fillna(0).max())
    return positive == 0, {
        "positive_packet_norm_live": positive,
        "max_packet_norm_live": max_packet,
        "live_points": live_points,
    }


def _decision_pass(path: Path, column: str) -> tuple[bool, dict[str, Any]]:
    decision = pd.read_csv(path)
    row = decision.iloc[0].to_dict()
    return _truth(row[column]), row


def _record_decision(
    outdir: Path,
    status_rows: list[dict[str, Any]],
    stage: str,
    path: Path,
    column: str,
    *,
    stop_on_fail: bool,
) -> bool:
    passed, row = _decision_pass(path, column)
    _stage(status_rows, stage, "pass" if passed else "fail", decision_path=str(path), decision=row)
    if passed:
        print(json.dumps({"event": "gate_pass", "stage": stage, "decision_path": str(path)}), flush=True)
        return True
    if stop_on_fail:
        _write_status(outdir, status_rows, f"{stage}_fail", failed_stage=stage)
    print(json.dumps({"event": "gate_fail", "stage": stage, "decision_path": str(path)}), flush=True)
    return not stop_on_fail


def _run_first_order(outdir: Path, label: str, root: Path, equation_dir: Path, energy_dir: Path) -> dict[str, Path]:
    first_order_dir = root / f"beta075_first_order_3p1_coupling_{label}"
    run = FirstOrder3P1RunSpec(
        f"sealed_dense_{label}",
        "dense",
        f"sealed_beta075_{label}",
        "main_dense",
        root / "endpoint_medium_covariant_audit_freeze_rematch_w6_t1p5",
        root / "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5",
    )
    inputs = FirstOrder3P1Inputs(
        equation_dir=equation_dir,
        energy_constant_dir=energy_dir,
        runs=(run,),
    )
    outputs, metadata = build_first_order_3p1_coupling(
        inputs,
        spec=FirstOrder3P1Spec(required_surface_count=1),
    )
    files = write_first_order_3p1_coupling_outputs(first_order_dir, outputs, metadata)
    return files


def _run_capstone(
    root: Path,
    label: str,
    service_rating: float,
    first_order_dir: Path,
    energy_dir: Path,
    args: argparse.Namespace,
) -> dict[str, Path]:
    capstone_dir = root / f"stage2_beta075_moderate_3p1_{label}_capstone"
    surface = Moderate3P1SurfaceSpec(
        f"sealed_dense_{label}",
        "dense",
        "main_dense",
        float(service_rating),
        root / "endpoint_medium_covariant_audit_freeze_rematch_w6_t1p5",
        root / "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5",
    )
    inputs = Moderate3P1Inputs(
        first_order_dir=first_order_dir,
        energy_constant_dir=energy_dir,
        surfaces=(surface,),
    )
    return run_moderate_3p1_v5_capstone(
        inputs,
        capstone_dir,
        spec=Moderate3P1Spec(
            expected_service_rating=float(service_rating),
            service_label=label,
            require_reference_surface=False,
            n_phi=int(args.n_phi),
            n_steps=int(args.n_steps),
            time_chunk_steps=int(args.time_chunk_steps),
            workers=int(args.capstone_workers),
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a fresh beta075 same-quality ladder for one service rating and run its local 3+1 capstone."
    )
    parser.add_argument("--service-rating", type=float, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--source-manifest", type=Path, default=DEFAULT_SOURCE_MANIFEST)
    parser.add_argument("--equation-dir", type=Path, default=DEFAULT_EQUATION_DIR)
    parser.add_argument("--energy-constant-dir", type=Path, default=DEFAULT_ENERGY_DIR)
    parser.add_argument("--candidate", default=DEFAULT_CANDIDATE)
    parser.add_argument("--jobs", type=int, default=6)
    parser.add_argument("--s-shards", type=int, default=None)
    parser.add_argument("--ns", type=int, default=377)
    parser.add_argument("--nl", type=int, default=241)
    parser.add_argument("--s-min", type=float, default=-1.5)
    parser.add_argument("--s-max", type=float, default=15.0)
    parser.add_argument("--l-min", type=float, default=-6.0)
    parser.add_argument("--l-max", type=float, default=6.0)
    parser.add_argument("--h-s", type=float, default=0.0025)
    parser.add_argument("--h-l", type=float, default=0.0025)
    parser.add_argument("--n-phi", type=int, default=24)
    parser.add_argument("--n-steps", type=int, default=64)
    parser.add_argument("--time-chunk-steps", type=int, default=4)
    parser.add_argument("--capstone-workers", type=int, default=4)
    parser.add_argument("--skip-capstone", action="store_true")
    parser.add_argument(
        "--gate-policy",
        choices=("stop", "collect"),
        default="stop",
        help="stop exits on the first failed proof gate; collect records failures and runs later reachable diagnostics.",
    )
    return parser


def run(args: argparse.Namespace) -> dict[str, Path]:
    label = service_label(float(args.service_rating))
    candidate_label = _candidate_label(args.candidate)
    outdir = args.outdir
    status_rows: list[dict[str, Any]] = []
    stop_on_fail = str(args.gate_policy) == "stop"

    source_manifest = _clone_source_manifest(args.source_manifest, outdir, float(args.service_rating))
    _stage(
        status_rows,
        "source_manifest_clone",
        "pass",
        source_manifest=str(source_manifest),
        source_manifest_sha256=sha256_file(source_manifest),
    )

    ledger_dir = outdir / "ledgers" / candidate_label
    _run_command(
        [
            sys.executable,
            str(SCRIPT_DIR / "run_beta_collar_generator_screen.py"),
            "--source-manifest",
            str(source_manifest),
            "--outdir",
            str(outdir),
            "--label",
            f"beta_collar_generator_beta075_p003_mid_{label}_dense377x241",
            "--candidate",
            args.candidate,
            "--force",
            "--quiet",
            "--point-format",
            "parquet",
            "--stream-shards",
            "--jobs",
            str(int(args.jobs)),
            "--ns",
            str(int(args.ns)),
            "--nl",
            str(int(args.nl)),
            "--s-min",
            str(float(args.s_min)),
            "--s-max",
            str(float(args.s_max)),
            "--l-min",
            str(float(args.l_min)),
            "--l-max",
            str(float(args.l_max)),
            "--h-s",
            str(float(args.h_s)),
            "--h-l",
            str(float(args.h_l)),
            *([] if args.s_shards is None else ["--s-shards", str(int(args.s_shards))]),
        ],
        "source_ledger",
        status_rows,
    )
    source_ok, source_values = _source_safety_pass(ledger_dir / "source_ledger_safety.csv")
    _stage(status_rows, "source_safety", "pass" if source_ok else "fail", **source_values)
    if not source_ok and stop_on_fail:
        return _write_status(outdir, status_rows, "source_safety_fail", service_label=label)
    if not source_ok:
        print(json.dumps({"event": "source_safety_fail_collecting", "service_label": label, **source_values}), flush=True)
    else:
        print(json.dumps({"event": "source_safety_pass", "service_label": label, **source_values}), flush=True)

    component_dir = outdir / "component_rematch_w6_t1p5"
    string_dir = outdir / "string_rematch_w6_t1p5"
    intermediate_dir = outdir / "intermediate_rematch_w6_t1p5"
    structured_dir = outdir / "endpoint_j_structured_source_freeze_reset_bounded_rematch_w6_t1p5"
    closure_dir = outdir / "endpoint_j_freeze_source_model_rematch_w6_t1p5"
    medium_dir = outdir / "endpoint_medium_field_closure_validation_freeze_rematch_w6_t1p5"
    covariant_dir = outdir / "endpoint_medium_covariant_audit_freeze_rematch_w6_t1p5"
    stroke_dir = outdir / "endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5"
    total_dir = outdir / "endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5"

    _run_command(
        [
            sys.executable,
            str(SCRIPT_DIR / "run_component_source_ledger.py"),
            "--ledger-dir",
            str(ledger_dir),
            "--label",
            f"{candidate_label}_{label}_dense377x241",
            "--outdir",
            str(component_dir),
        ],
        "component_source_ledger",
        status_rows,
    )
    _run_command(
        [
            sys.executable,
            str(SCRIPT_DIR / "run_radial_string_cloud_replacement.py"),
            "--component-dir",
            str(component_dir),
            "--outdir",
            str(string_dir),
        ],
        "radial_string_cloud_replacement",
        status_rows,
    )
    _run_command(
        [
            sys.executable,
            str(SCRIPT_DIR / "run_intermediate_source_model.py"),
            "--component-dir",
            str(component_dir),
            "--string-cloud-dir",
            str(string_dir),
            "--outdir",
            str(intermediate_dir),
        ],
        "intermediate_source_model",
        status_rows,
    )
    _run_command(
        [
            sys.executable,
            str(SCRIPT_DIR / "run_endpoint_j_structured_source_model.py"),
            "--intermediate-dir",
            str(intermediate_dir),
            "--outdir",
            str(structured_dir),
            "--label",
            f"{candidate_label}_{label}_dense377x241",
        ],
        "endpoint_j_structured_source",
        status_rows,
    )
    _run_command(
        [
            sys.executable,
            str(SCRIPT_DIR / "run_endpoint_j_closure_component.py"),
            "--intermediate-dir",
            str(intermediate_dir),
            "--structured-source-dir",
            str(structured_dir),
            "--outdir",
            str(closure_dir),
            "--label",
            f"{candidate_label}_{label}_dense377x241",
        ],
        "endpoint_j_closure_component",
        status_rows,
    )
    _run_command(
        [
            sys.executable,
            str(SCRIPT_DIR / "run_endpoint_medium_field_closure_validation.py"),
            "--fit-dir",
            str(closure_dir),
            "--outdir",
            str(medium_dir),
            "--source-name",
            "endpoint_j_frozen_source",
        ],
        "endpoint_medium_field_closure",
        status_rows,
    )
    if not _record_decision(
        outdir,
        status_rows,
        "endpoint_medium_field_closure_gate",
        medium_dir / "endpoint_medium_field_closure_decision.csv",
        "passes_constrained_field_closure",
        stop_on_fail=stop_on_fail,
    ):
        return {"status_csv": outdir / "beta075_service_rating_ladder_status.csv"}

    _run_command(
        [
            sys.executable,
            str(SCRIPT_DIR / "run_endpoint_medium_covariant_audit.py"),
            "--field-closure-dir",
            str(medium_dir),
            "--outdir",
            str(covariant_dir),
            "--point-ledger",
            str(ledger_dir / "source_ledger_point_ledger.parquet"),
        ],
        "endpoint_medium_covariant_audit",
        status_rows,
    )
    if not _record_decision(
        outdir,
        status_rows,
        "endpoint_medium_covariant_gate",
        covariant_dir / "endpoint_medium_covariant_decision.csv",
        "passes_covariant_identity_audit",
        stop_on_fail=stop_on_fail,
    ):
        return {"status_csv": outdir / "beta075_service_rating_ladder_status.csv"}

    _run_command(
        [
            sys.executable,
            str(SCRIPT_DIR / "run_endpoint_support_stroke_exchange.py"),
            "--covariant-dir",
            str(covariant_dir),
            "--outdir",
            str(stroke_dir),
            "--fit-scopes",
            "phase_region",
            "--fit-domains",
            "allowed",
            "--s-centers",
            "24",
            "--l-centers",
            "14",
            "--width-multipliers",
            "0.3",
            "--ridges",
            "1e-5",
        ],
        "endpoint_support_stroke_exchange",
        status_rows,
    )
    if not _record_decision(
        outdir,
        status_rows,
        "endpoint_support_stroke_exchange_gate",
        stroke_dir / "endpoint_support_stroke_exchange_decision.csv",
        "passes_support_stroke_exchange_fit",
        stop_on_fail=stop_on_fail,
    ):
        return {"status_csv": outdir / "beta075_service_rating_ladder_status.csv"}

    _run_command(
        [
            sys.executable,
            str(SCRIPT_DIR / "run_endpoint_support_total_closure.py"),
            "--stroke-dir",
            str(stroke_dir),
            "--outdir",
            str(total_dir),
        ],
        "endpoint_support_total_closure",
        status_rows,
    )
    if not _record_decision(
        outdir,
        status_rows,
        "endpoint_support_total_closure_gate",
        total_dir / "endpoint_support_total_closure_decision.csv",
        "passes_support_total_closure",
        stop_on_fail=stop_on_fail,
    ):
        return {"status_csv": outdir / "beta075_service_rating_ladder_status.csv"}

    first_order_files = _run_first_order(outdir, label, outdir, args.equation_dir, args.energy_constant_dir)
    first_order_dir = outdir / f"beta075_first_order_3p1_coupling_{label}"
    _stage(
        status_rows,
        "first_order_3p1_coupling",
        "pass",
        decision_path=str(first_order_files["decision"]),
    )
    if not _record_decision(
        outdir,
        status_rows,
        "first_order_3p1_coupling_gate",
        first_order_files["decision"],
        "hard_first_order_3p1_pass",
        stop_on_fail=stop_on_fail,
    ):
        return {"status_csv": outdir / "beta075_service_rating_ladder_status.csv"}

    capstone_files: dict[str, Path] = {}
    if args.skip_capstone:
        _stage(status_rows, "moderate_3p1_capstone", "skipped")
    else:
        capstone_files = _run_capstone(
            outdir,
            label,
            float(args.service_rating),
            first_order_dir,
            args.energy_constant_dir,
            args,
        )
        _stage(
            status_rows,
            "moderate_3p1_capstone",
            "pass",
            decision_path=str(capstone_files["decision"]),
        )
        if not _record_decision(
            outdir,
            status_rows,
            "moderate_3p1_capstone_gate",
            capstone_files["decision"],
            "hard_capstone_pass",
            stop_on_fail=stop_on_fail,
        ):
            return {"status_csv": outdir / "beta075_service_rating_ladder_status.csv"}

    failed_stages = [row["stage"] for row in status_rows if row.get("status") == "fail"]
    final_status = (
        "service_rating_ladder_complete"
        if not failed_stages
        else "service_rating_ladder_diagnostic_failures_collected"
        if not stop_on_fail
        else "service_rating_ladder_fail"
    )
    final_files = _write_status(
        outdir,
        status_rows,
        final_status,
        service_label=label,
        service_rating=float(args.service_rating),
        gate_policy=str(args.gate_policy),
        failed_stages=failed_stages,
        source_manifest=str(source_manifest),
        first_order_files={key: str(path) for key, path in first_order_files.items()},
        capstone_files={key: str(path) for key, path in capstone_files.items()},
    )
    print(
        json.dumps({
            "event": "ladder_complete",
            "service_label": label,
            "outdir": str(outdir),
            "final_status": final_status,
            "failed_stages": failed_stages,
        }),
        flush=True,
    )
    return final_files


def main() -> int:
    files = run(build_parser().parse_args())
    print(json.dumps({"ok": True, "files": {key: str(path) for key, path in files.items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
