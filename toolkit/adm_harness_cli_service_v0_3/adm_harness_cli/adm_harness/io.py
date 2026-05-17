from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def load_npz(path: str | Path) -> dict[str, np.ndarray]:
    path = Path(path)
    with np.load(path, allow_pickle=False) as z:
        return {k: z[k] for k in z.files}


def write_json(path: str | Path, obj: Any) -> None:
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_table(df: pd.DataFrame, path_base: str | Path, preferred: str = "csv") -> Path:
    path_base = Path(path_base)
    preferred = (preferred or "csv").lower()
    if preferred == "parquet":
        try:
            out = path_base.with_suffix(".parquet")
            df.to_parquet(out, index=False)
            return out
        except Exception:
            out = path_base.with_suffix(".csv")
            df.to_csv(out, index=False)
            return out
    if preferred == "jsonl":
        out = path_base.with_suffix(".jsonl")
        df.to_json(out, orient="records", lines=True)
        return out
    out = path_base.with_suffix(".csv")
    df.to_csv(out, index=False)
    return out


def read_table(path: str | Path, **kwargs) -> pd.DataFrame:
    path = Path(path)
    if path.suffix == ".parquet":
        return pd.read_parquet(path, **kwargs)
    if path.suffix == ".jsonl":
        return pd.read_json(path, orient="records", lines=True, **kwargs)
    return pd.read_csv(path, **kwargs)
