from __future__ import annotations

from pathlib import Path

import pandas as pd


PARQUET_SUFFIXES = {".parquet", ".pq"}


def read_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in PARQUET_SUFFIXES:
        return pd.read_parquet(path)
    return pd.read_csv(path)


def write_table(frame: pd.DataFrame, path: Path) -> None:
    suffix = path.suffix.lower()
    if suffix in PARQUET_SUFFIXES:
        frame.to_parquet(path, index=False, compression="zstd")
        return
    frame.to_csv(path, index=False)
