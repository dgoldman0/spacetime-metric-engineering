from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def _maybe_import_matplotlib():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def plot_fields(df: pd.DataFrame, out_dir: str | Path, fields: list[str] | None = None) -> list[Path]:
    plt = _maybe_import_matplotlib()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    fields = fields or ["rho", "j_l", "delta_rho", "delta_j_l"]
    s_vals = np.sort(df["s"].unique())
    l_vals = np.sort(df["l"].unique())
    paths: list[Path] = []
    # Map rows back into s/l grid with pivot; avoids relying on row order.
    for field in fields:
        if field not in df.columns:
            continue
        pivot = df.pivot_table(index="s", columns="l", values=field, aggfunc="first").reindex(index=s_vals, columns=l_vals)
        arr = pivot.to_numpy()
        fig = plt.figure(figsize=(8, 4.5))
        ax = fig.add_subplot(111)
        im = ax.imshow(
            arr,
            aspect="auto",
            origin="lower",
            extent=[float(l_vals.min()), float(l_vals.max()), float(s_vals.min()), float(s_vals.max())],
        )
        ax.set_xlabel("l")
        ax.set_ylabel("sigma")
        ax.set_title(field)
        fig.colorbar(im, ax=ax)
        path = out / f"{field}.png"
        fig.tight_layout()
        fig.savefig(path, dpi=150)
        plt.close(fig)
        paths.append(path)
    return paths
