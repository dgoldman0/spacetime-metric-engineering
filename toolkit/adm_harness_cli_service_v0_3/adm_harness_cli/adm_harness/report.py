from __future__ import annotations

from pathlib import Path
import json

import pandas as pd


def _md_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df is None or len(df) == 0:
        return "\n_no rows_\n"
    return df.head(max_rows).to_markdown(index=False)


def write_run_report(
    out_path: str | Path,
    run_name: str,
    decision: pd.DataFrame,
    peaks: pd.DataFrame,
    packet: pd.DataFrame,
    support: pd.DataFrame,
    catch: pd.DataFrame,
    status: dict,
) -> None:
    text = [
        f"# ADM harness report {run_name}",
        "",
        "## Decision sheet",
        _md_table(decision),
        "",
        "## Peak locations",
        _md_table(peaks),
        "",
        "## Packet exposure",
        _md_table(packet),
        "",
        "## Support shell load",
        _md_table(support),
        "",
        "## Catch/rematch localization",
        _md_table(catch),
        "",
        "## Status",
        "```json",
        json.dumps(status, indent=2, sort_keys=True),
        "```",
        "",
        "## Notes",
        "Absorber diagnostics are reported as sidecar metrics unless the config supplies a coupled field/ledger variant. This version does not synthesize a new ADM field from absorber coefficients.",
        "",
    ]
    Path(out_path).write_text("\n".join(text), encoding="utf-8")


def write_comparison_report(out_path: str | Path, decision: pd.DataFrame, rankings: pd.DataFrame) -> None:
    text = [
        "# ADM harness comparison report",
        "",
        "## Run decision sheets",
        _md_table(decision, max_rows=50),
        "",
        "## Delta metric rankings",
        _md_table(rankings, max_rows=50),
        "",
    ]
    Path(out_path).write_text("\n".join(text), encoding="utf-8")
