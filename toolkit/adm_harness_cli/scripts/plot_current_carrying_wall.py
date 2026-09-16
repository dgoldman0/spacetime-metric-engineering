#!/usr/bin/env python3
"""Plot the archived scalar-wall equation of state and current diagnostics."""
from pathlib import Path
import argparse
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[3]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path,
                        default=ROOT / "supporting_reports/data/current_carrying_wall")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "supporting_reports/figures/current_carrying_wall")
    args = parser.parse_args()
    manifest = json.loads((args.input / "manifest.json").read_text())
    summary = json.loads((args.input / "summary.json").read_text())
    paths = [args.input / "summary.json"]
    rows = {}
    for branch in summary["branches"]:
        path = args.input / (branch["label"]+"_spacelike.csv")
        paths.append(path)
        rows[branch["label"]] = np.genfromtxt(path, delimiter=",", names=True)
    for path in paths:
        if digest(path) != manifest["output_sha256"][path.name]:
            raise ValueError(f"Input hash mismatch: {path}")
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "savefig.dpi": 180})
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 3.7), layout="constrained")
    central = next(b for b in summary["branches"] if b["label"] == "f0.40_refined")
    row = rows[central["label"]]
    horizontal = row["w"]/central["linear_quench_w"]
    axes[0].plot(horizontal, row["energy"], label=r"Energy $U$ / axial tension", color="#176b91")
    axes[0].plot(horizontal, -row["hoop_pressure"], label=r"Hoop tension $T_\theta$", color="#bd5438")
    axes[0].axhline(central["bare_tension"], color=".5", linestyle=":", label="Bare wall tension")
    axes[0].set(title="Axial tension remains tied to energy", ylabel="Surface energy or tension",
                xlabel=r"Squared phase gradient $w / w_{\rm c}$", xlim=(0, .95))
    axes[0].legend(fontsize=8, loc="lower right")
    colors = ["#317d6f", "#176b91", "#bd5438", "#8061a5"]
    branches = [b for b in summary["branches"] if "refined" not in b["label"]]
    for branch, color in zip(branches, colors):
        row = rows[branch["label"]]
        horizontal = row["w"]/branch["linear_quench_w"]
        axes[1].plot(horizontal, row["current_magnitude"], color=color,
                     label=f"f = {branch['parameters']['coupling']:.2f}")
        axes[2].plot(horizontal, row["current_mode_speed_squared"], color=color)
    axes[1].set(title="Each branch reaches a maximum current", ylabel="Integrated global current",
                xlabel=r"Squared phase gradient $w / w_{\rm c}$", xlim=(0, .95))
    axes[1].legend(fontsize=8)
    axes[2].axhline(0, color=".35", linewidth=1)
    axes[2].axhspan(-1.2, 0, color="#bd5438", alpha=.08)
    axes[2].text(.015, -.25, "Growing longitudinal mode", color="#8e402b", fontsize=9)
    axes[2].set(title="Current mode near the turnover", ylabel=r"Squared mode speed $c_L^2$",
                xlabel=r"Squared phase gradient $w / w_{\rm c}$", xlim=(0, .5), ylim=(-1.2, 1.05))
    for axis in axes:
        axis.grid(alpha=.15)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    outputs = [args.output.with_suffix(ext) for ext in (".png", ".pdf")]
    for path in outputs:
        fig.savefig(path)
    plt.close(fig)
    provenance = dict(source_sha256=digest(Path(__file__)),
        input_sha256={str(p.relative_to(ROOT)): digest(p) for p in paths},
        output_sha256={str(p.relative_to(ROOT)): digest(p) for p in outputs})
    args.output.with_name(args.output.name+"_manifest.json").write_text(json.dumps(provenance, indent=2)+"\n")
    print(*outputs, sep="\n")


if __name__ == "__main__":
    main()
