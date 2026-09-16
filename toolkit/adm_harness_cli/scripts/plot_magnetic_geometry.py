#!/usr/bin/env python3
"""Plot the retained magnetic-jacket parameter sweep."""
from pathlib import Path
import argparse
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary",type=Path)
    parser.add_argument("output",type=Path,help="output filename stem for PNG and PDF")
    args=parser.parse_args()
    data=json.loads(args.summary.read_text())["cases"]
    finest=max(row["spatial_samples"] for row in data)
    cases=sorted((row for row in data if row["spatial_samples"]==finest),key=lambda row:row["label"])
    fig,axes=plt.subplots(1,2,figsize=(10.2,4.7),sharey=True)
    colors=("#126b8a","#ce6925","#7d609b")
    for ax,case,title in zip(axes,cases,("First location","Second location")):
        for b,color in zip((0.,.1,1.),colors):
            rows=sorted((r for r in case["cases"] if r["family"]=="balanced_jacket"
                         and r["inner_pressure"]==b),key=lambda r:r["radius_ratio"])
            values=[r["minimum_stress_fraction_counted_currents"] for r in rows]
            ax.plot([r["radius_ratio"] for r in rows],
                    [np.nan if v is None else v for v in values],"o-",color=color,
                    label=f"Internal magnetic pressure = {b:g} × plasma pressure")
        baseline=next(r for r in case["cases"] if r["family"]=="original")
        ax.axhline(baseline["minimum_stress_fraction_counted_currents"],
                   color="#555555",linestyle="--",label="Original loop, same current-load accounting")
        ax.axhline(.5,color="#bbbbbb",linestyle=":")
        ax.set(title=title,xlabel="Outer radius / plasma-core radius",xlim=(.99,2.02),ylim=(.45,1.035))
        ax.set_xticks([1.,1.1,1.25,1.5,2.])
        ax.grid(alpha=.18)
    axes[0].set_ylabel("Minimum stress / total energy density, k")
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc="lower center",bbox_to_anchor=(.5,.055),ncol=2,fontsize=8,frameon=False)
    fig.suptitle("Exterior magnetic jackets reduce the second location's support burden",fontsize=12)
    fig.text(.5,.015,"Necessary straight-section test. Missing points have no feasible k ≤ 1; bend mechanics remain open.",
             ha="center",fontsize=8,color="#444444")
    fig.tight_layout(rect=(0,.19,1,.94))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    for suffix in (".png",".pdf"):
        fig.savefig(args.output.with_suffix(suffix),dpi=180)
    plt.close(fig)


if __name__=="__main__":main()
