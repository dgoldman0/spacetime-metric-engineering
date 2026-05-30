"""Shared data structures for the White Casimir Stage 5 readout ladder."""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import pandas as pd


DEFAULT_STAGE3_DIR = Path(
    "/media/kir/9CDCBD3EDCBD140C/Research/"
    "white_casimir_tensor_scale_probe/stage3_focused_20260530"
)
DEFAULT_STAGE4_DIR = Path(
    "/media/kir/9CDCBD3EDCBD140C/Research/"
    "white_casimir_synthetic_discrimination/stage4_block_bootstrap_geometry_sbr_refine_20260530"
)
DEFAULT_STAGE5_BASE = Path("/media/kir/9CDCBD3EDCBD140C/Research/white_casimir_stage5_readout_ladder")

CLAIM_CLASSES = ("casimir_boundary", "material_response", "metric_proxy", "control")
SCENARIOS = ("conservative", "nominal", "optimistic")


@dataclass(frozen=True)
class ReadoutCandidate:
    candidate_id: str
    claim_class: str
    observable_name: str
    observable_unit: str
    transduction_family: str
    sensitivity_floor: float
    sensitivity_floor_unit: str
    dominant_nuisances: tuple[str, ...]
    control_requirements: tuple[str, ...]
    allowed_claim: str
    model_status: str = "analytic_first_pass_requires_fidelity_upgrade"
    notes: str = ""


@dataclass(frozen=True)
class TransductionResult:
    candidate_id: str
    scenario: str
    schedule_step: str
    schedule_order: int
    shell_observable: float
    shell_observable_unit: str
    background_observable_rms: float
    predicted_sbr: float
    required_gain_to_stage4_gate: float
    claim_class: str
    allowed_claim: str
    dominant_nuisance: str
    model_status: str
    model_provenance: str
    optimism_level: str
    model_notes: str


@dataclass(frozen=True)
class Stage5Config:
    preset: str
    run_id: str
    source_stage3_dir: str
    source_stage4_dir: str
    outdir: str
    base_seed: int
    shell_datasets_per_candidate: int
    em_only_datasets_per_candidate: int
    chunk_size: int
    heartbeat_interval_s: float
    noise_sigma: float = 0.05
    nuisance_sigma: float = 1.0
    ridge_alpha: float = 1.0e-3
    shell_detection_z: float = 2.0
    recovery_threshold: float = 0.80
    false_positive_threshold: float = 0.05
    preferred_correlation_threshold: float = 0.85
    candidate_ids: tuple[str, ...] = ()
    backend_mode: str = "analytic"
    physical_cases_per_branch: int = 9


class Stage5ProgressRecorder:
    """Append progress events and keep a small machine-readable dashboard."""

    def __init__(self, outdir: Path):
        self.outdir = outdir
        self.started = time.time()
        self.progress_path = outdir / "progress.jsonl"
        self.latest_path = outdir / "latest_status.json"
        self.report_path = outdir / "reports" / "stage5_readout_ladder_readout.md"
        (outdir / "reports").mkdir(parents=True, exist_ok=True)
        self.progress_path.write_text("", encoding="utf-8")

    def record(self, event: str, payload: Mapping[str, Any]) -> None:
        elapsed = time.time() - self.started
        row = {
            "utc": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "elapsed_s": elapsed,
            **dict(payload),
        }
        with self.progress_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        self.latest_path.write_text(json.dumps(row, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self._write_machine_readout(row)
        print(f"[stage5] {event}: {payload.get('label', '')} elapsed={elapsed:.1f}s", flush=True)

    def _write_machine_readout(self, row: Mapping[str, Any]) -> None:
        text = (
            "# Stage 5 Readout Ladder Readout\n\n"
            "Status: machine-generated heartbeat, not interpretive report.\n\n"
            f"- latest event: `{row.get('event')}`\n"
            f"- elapsed: `{float(row.get('elapsed_s', 0.0)):.1f} s`\n"
            f"- latest label: `{row.get('label', '')}`\n"
            f"- output path: `{self.outdir}`\n\n"
            "Large ledgers are written as zstd-compressed parquet files.\n"
        )
        self.report_path.write_text(text, encoding="utf-8")


def git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return "unknown"
    return result.stdout.strip()


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_frame(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".parquet":
        frame.to_parquet(path, index=False, compression="zstd")
    else:
        frame.to_csv(path, index=False)


def dataclass_frame(items: list[Any]) -> pd.DataFrame:
    return pd.DataFrame([asdict(item) for item in items])
