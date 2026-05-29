"""Stage 0/1 report artifact generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import yaml

from .geometry import (
    CentralReadoutPath,
    PillarMidplaneCavity,
    ROLE_ORDER,
    SphereInCylinder,
    make_xy_grid,
    role_counts,
)


CLAIM_MANIFEST: dict[str, Any] = {
    "paper": "White et al. 2021, EPJC, Worldline numerics applied to custom Casimir geometry generates unanticipated intersection with Alcubierre warp metric",
    "architecture_under_test": "Casimir boundary geometry plus Alcubierre-shell interpretation",
    "not_modeled_as": "active rail",
    "geometry_plate_pillar": {
        "plate_gap_um": 4.0,
        "plate_width_um": 40.0,
        "plate_height_um": 40.0,
        "pillar_diameter_um": 1.0,
    },
    "geometry_sphere_cylinder": {
        "sphere_diameter_um": 1.0,
        "cylinder_diameter_um": 4.0,
        "sphere_position": "centered",
    },
    "reported_worldline_setup": {
        "sphere_cylinder_grid": "100 x 100",
        "unit_loop_ensemble": 2000,
        "cpu_count_reported": 660,
    },
    "claimed_observable": "transit-time difference through current/photon/electron path routed through center of sphere-cylinder array",
    "audit_goal": "distinguish Alcubierre-shell source relevance from visual Casimir morphology and ordinary EM propagation effects",
    "provenance_quarantine": "No active-rail candidate manifests, service-rating tables, packet-safety ledgers, or beta-collar artifacts are inputs to this audit.",
}

ROLE_COLORS = {
    "far_field_control": "#eeeeee",
    "source_shell_candidate": "#7fcdbb",
    "transit_readout_channel": "#2c7fb8",
    "ordinary_em_competitor_region": "#fdae61",
    "boundary_infrastructure": "#636363",
    "stress_shaping_body": "#d7191c",
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def plot_roles(path: Path, title: str, grid: dict[str, np.ndarray], roles: dict[str, np.ndarray]) -> None:
    image = np.zeros(grid["x"].shape, dtype=int)
    for idx, role in enumerate(ROLE_ORDER, start=1):
        image[roles[role]] = idx

    color_list = ["#ffffff"] + [ROLE_COLORS[role] for role in ROLE_ORDER]
    cmap = matplotlib.colors.ListedColormap(color_list)
    bounds = np.arange(len(color_list) + 1) - 0.5
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
    extent = [
        float(grid["x_values"][0]),
        float(grid["x_values"][-1]),
        float(grid["y_values"][0]),
        float(grid["y_values"][-1]),
    ]

    fig, ax = plt.subplots(figsize=(7.0, 4.8), constrained_layout=True)
    ax.imshow(image, origin="lower", extent=extent, cmap=cmap, norm=norm, interpolation="nearest", aspect="equal")
    ax.set_title(title)
    ax.set_xlabel("x [um]")
    ax.set_ylabel("section coordinate [um]")
    patches = [Patch(facecolor=ROLE_COLORS[role], edgecolor="black", label=role) for role in ROLE_ORDER]
    ax.legend(handles=patches, loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def generate_phase0_phase1(base_dir: Path) -> dict[str, Any]:
    outputs_dir = base_dir / "outputs"
    reports_dir = base_dir / "reports"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    claim_path = outputs_dir / "claim_manifest.json"
    claim_path.write_text(json.dumps(CLAIM_MANIFEST, indent=2) + "\n", encoding="utf-8")

    configs_dir = base_dir / "configs"
    plate_cfg = load_yaml(configs_dir / "paper_plate_pillar.yaml")
    sphere_cfg = load_yaml(configs_dir / "paper_sphere_cylinder.yaml")

    plate = PillarMidplaneCavity(
        gap_um=plate_cfg["plate_gap_um"],
        plate_width_um=plate_cfg["plate_width_um"],
        plate_height_um=plate_cfg["plate_height_um"],
        pillar_diameter_um=plate_cfg["pillar_diameter_um"],
        pillar_axis=plate_cfg.get("pillar_axis", "z"),
    )
    readout_cfg = sphere_cfg.get("readout_path", {})
    readout = CentralReadoutPath(
        length_um=sphere_cfg["cylinder_length_um"],
        radius_um=readout_cfg.get("radius_um", 0.05),
        mode=readout_cfg.get("mode", "open_bore"),
        conductor_radius_um=readout_cfg.get("conductor_radius_um", 0.0),
        participates_as_casimir_boundary=readout_cfg.get("participates_as_casimir_boundary", False),
    )
    sphere = SphereInCylinder(
        sphere_diameter_um=sphere_cfg["sphere_diameter_um"],
        cylinder_diameter_um=sphere_cfg["cylinder_diameter_um"],
        cylinder_length_um=sphere_cfg["cylinder_length_um"],
        bore_radius_um=readout.radius_um,
        readout_path=readout,
    )

    plate_grid = make_xy_grid(-4.0, 4.0, -3.0, 3.0, 220, 170)
    sphere_grid = make_xy_grid(-4.0, 4.0, -3.0, 3.0, 220, 170)
    plate_roles = plate.role_regions(plate_grid)
    sphere_roles = sphere.role_regions(sphere_grid)

    plate_fig = reports_dir / "fig_roles_plate_pillar.png"
    sphere_fig = reports_dir / "fig_roles_sphere_cylinder.png"
    plot_roles(plate_fig, "Plate-Pillar Role Regions", plate_grid, plate_roles)
    plot_roles(sphere_fig, "Sphere-Cylinder Role Regions", sphere_grid, sphere_roles)

    metadata = {
        "phase": "stage0_stage1_geometry_roles",
        "base_dir": str(base_dir),
        "claim_manifest": str(claim_path.relative_to(base_dir)),
        "role_figures": [str(plate_fig.relative_to(base_dir)), str(sphere_fig.relative_to(base_dir))],
        "geometry_conventions": {
            "plate_pillar": "plates separated along y; pillar axis z; plotted in x-y section at z=0",
            "sphere_cylinder": "cylinder/readout axis x; plotted in x-y section at z=0",
        },
        "readout_path_policy": {
            "first_phase": "role label only; not a Casimir boundary",
            "mode": readout.mode,
            "radius_um": readout.radius_um,
            "participates_as_casimir_boundary": readout.participates_as_casimir_boundary,
        },
        "role_pixel_counts": {
            "plate_pillar": role_counts(plate_roles),
            "sphere_cylinder": role_counts(sphere_roles),
        },
    }
    metadata_path = outputs_dir / "geometry_role_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


def main() -> None:
    default_base = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Generate Stage 0/1 White Casimir audit artifacts.")
    parser.add_argument("--base-dir", type=Path, default=default_base)
    args = parser.parse_args()
    metadata = generate_phase0_phase1(args.base_dir.resolve())
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
