#!/usr/bin/env python3
"""Census of the demanded stress of the gate-passing one-space rail; emit data only.

The census evaluates the chosen design of the choreography pass: the 2.1c lane
on the static support inside the wide staged boundary layer. At every node of
every (sigma, z) sample it records the rest-frame energy density, the
principal pressures and the source velocity, and assigns an energy-condition
class: ordinary (dominant energy condition), NEC-respecting (null energy
condition with the dominant condition violated) or NEC-violating. Sums over
coordinate and proper volume are kept per radial zone of the stack. The
standing snapshot is kept point by point. The census extends in z past the
gate samples to cover the sheath's ends, and it repeats the standing snapshot
for the boundary-layer variants of the sheath budget. Narrative
interpretation is maintained manually in supporting_reports.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, replace
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_choreography_pass as choreography
from adm_harness import axial_track as ax
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
LANE, SUPPORT = "lane_2p1", "static"
ETA = 2.4127904527582454e-5
STANDING = 10.
NOISE_FLOOR = choreography.NOISE_FLOOR
PER_PANEL = 12
W = choreography.WIDE_STACK
ZONES = (("service_region", 0., 1.75), ("conformal_rise", 1.75, 3.75), ("sheath_rise", 3.75, 8.75),
         ("sheath_plateau", 8.75, 9.25), ("outer_falls", 9.25, math.inf))
LAYERS = {key: W[key] for key in ("shift_layer", "stretch_layer", "lapse_layer")}
VARIANTS = {
    "single_layer": {},
    "staged_no_sheaths": dict(LAYERS),
    "conformal_only": dict(LAYERS, conformal_log_scale=W["conformal_log_scale"], conformal_rise=W["conformal_rise"],
                           conformal_fall=W["conformal_fall"]),
    "lapse_sheath_only": dict(LAYERS, sheath_log_lapse=W["sheath_log_lapse"], sheath_rise=W["sheath_rise"],
                              sheath_fall=W["sheath_fall"]),
    "wide_stack": dict(W),
}
SHEATH = dict(LAYERS, sheath_log_lapse=W["sheath_log_lapse"], sheath_rise=W["sheath_rise"], sheath_fall=W["sheath_fall"])
for scale in (2., 4., 6.):
    VARIANTS[f"sheath_conformal_e{scale:g}"] = dict(SHEATH, conformal_log_scale=scale, conformal_rise=W["conformal_rise"],
                                                    conformal_fall=W["conformal_fall"])
SCREENED = ("lapse_sheath_only", "sheath_conformal_e2", "sheath_conformal_e4", "sheath_conformal_e6", "wide_stack")
SCREEN_END = 3.
CLASSES = ("ordinary", "nec_respecting", "nec_violating")


def design_for(variant):
    return ax.AxialTrackDesign(track=choreography.track_for(LANE, SUPPORT), **VARIANTS[variant])


def point_census(tensor, fields, coord_weight, proper_weight):
    """Per-node classes and weighted integrands for one (sigma, z) slice."""
    kinds = ax.classify(tensor, floor=NOISE_FLOOR)
    frame = ax.principal_frame(tensor)
    null = ax.min_null_energy(tensor)
    rho = kinds["rest_energy_density"]
    pressures = kinds["principal_pressures"]
    vacuum = kinds["type"] == ax.VACUUM
    type_i = kinds["type"] == ax.TYPE_I
    violating = type_i & (np.min(rho[:, None]+pressures, axis=1) < 0)
    ordinary = type_i & ~violating & (rho >= np.max(np.abs(pressures), axis=1))
    respecting = type_i & ~violating & ~ordinary
    eulerian = tensor[:, 0, 0]
    trace = tensor[:, 0, 0]+tensor[:, 1, 1]+tensor[:, 2, 2]+tensor[:, 3, 3]
    # Source velocities are read only where the tensor rises above the noise floor.
    speed = np.where(vacuum, np.nan, np.hypot(frame["v_z"], frame["v_r"]))
    # Observers at fixed (z, r, phi) move along e_z at A beta/alpha relative to n; beyond one, none exist.
    static_speed = fields["A"]*fields["beta"]/fields["alpha"]
    with np.errstate(invalid="ignore", divide="ignore"):
        gamma = (1-frame["v_z"]*static_speed)/np.sqrt((1-speed**2)*(1-static_speed**2))
        speed_vs_static = np.where(np.abs(static_speed) < 1, np.sqrt(np.maximum(1-1/gamma**2, 0)), np.nan)
    direction = {axis: type_i & frame["generic"] & (rho+frame[f"p_{axis}"] < 0) for axis in ("z", "r", "phi")}
    return {"type": kinds["type"], "vacuum": vacuum, "type_i": type_i, "ordinary": ordinary,
            "nec_respecting": respecting, "nec_violating": violating, "rho": rho, "pressures": pressures,
            "eulerian": eulerian, "trace": trace, "null": null, "speed": speed, "direction": direction,
            "frame": frame, "scale": kinds["scale"], "coord": coord_weight, "proper": proper_weight,
            "alpha": fields["alpha"], "static_speed": static_speed, "speed_vs_static": speed_vs_static}


def zone_rows(census, radius, s, z, variant):
    rows = []
    for zone, lo, hi in ZONES:
        m = (radius >= lo) & (radius <= hi) if lo == 0. else (radius > lo) & (radius <= hi)
        if not m.any():
            continue
        c, p, alpha = census["coord"][m], census["proper"][m], census["alpha"][m]
        rho = np.nan_to_num(census["rho"][m])
        eulerian, null = census["eulerian"][m], census["null"][m]
        live_speed = census["speed"][m]
        rows.append({
            "variant": variant, "s": s, "z": z, "zone": zone, "nodes": int(m.sum()),
            "coord_volume": float(c.sum()), "proper_volume": float(p.sum()),
            **{f"proper_volume_{k}": float(p[census[k][m]].sum()) for k in CLASSES},
            "proper_volume_negative_rest_energy": float(p[census["type_i"][m] & (rho < 0)].sum()),
            "proper_volume_nec_respecting_negative_energy": float(p[census["nec_respecting"][m] & (rho < 0)].sum()),
            "proper_volume_without_static_frame": float(p[np.abs(census["static_speed"][m]) >= 1].sum()),
            **{f"proper_volume_violating_{a}": float(p[census["direction"][a][m]].sum()) for a in ("z", "r", "phi")},
            "type_iv": int((census["type"][m] == ax.TYPE_IV).sum()),
            "unresolved": int(np.isin(census["type"][m], [ax.UNRESOLVED, ax.TYPE_II_III]).sum()),
            "eulerian_positive": float(np.sum(p*np.maximum(eulerian, 0))),
            "eulerian_negative": float(np.sum(p*np.minimum(eulerian, 0))),
            "rest_negative": float(np.sum(p*np.minimum(rho, 0))),
            "killing_energy": float(np.sum(p*alpha*eulerian)),
            "komar_density": float(np.sum(p*alpha*census["trace"][m])),
            "komar_abs": float(np.sum(p*alpha*np.abs(census["trace"][m]))),
            "nec_content_coord": float(np.sum(c*np.maximum(-null, 0))),
            "nec_content_proper": float(np.sum(p*np.maximum(-null, 0))),
            "min_null": float(null.min()), "min_rest_energy": float(np.nanmin(census["rho"][m]))
            if np.isfinite(census["rho"][m]).any() else math.nan,
            "max_abs_component": float(census["scale"][m].max()),
            "max_source_speed": float(np.nanmax(live_speed)) if np.isfinite(live_speed).any() else math.nan,
            "max_static_frame_speed": float(np.max(np.abs(census["static_speed"][m]))),
            "max_source_speed_vs_static": float(np.nanmax(census["speed_vs_static"][m]))
            if np.isfinite(census["speed_vs_static"][m]).any() else math.nan,
            "max_alpha": float(alpha.max())})
    return rows


def slice_census(task):
    variant, s, z, keep_points = task
    design = design_for(variant)
    jet = ax.service_jet(s, z, choreography.params_for(LANE), design)
    nodes, weights = ax.wall_nodes(design, PER_PANEL)
    radius = np.concatenate([[0.], nodes])
    tensor = ax.frame_tensor(jet, radius, design, z=z)
    fields = ax.radial_fields(jet, radius, design, z=z)
    core_area = math.pi*design.core_radius**2
    coord = np.concatenate([[core_area], weights*2*math.pi*nodes])
    proper = coord*fields["A"]
    census = point_census(tensor, fields, coord, proper)
    exterior = float(np.max(np.abs(ax.frame_tensor(jet, [design.outer_radius+.5], design, z=z))))
    static = max(float(np.max(np.abs(jet[key]))) for key in ("s", "ss", "sz"))
    rows = zone_rows(census, radius, s, z, variant)
    for row in rows:
        row.update(exterior_max_abs=exterior, max_sigma_derivative=static)
    points = None
    if keep_points:
        frame = census["frame"]
        points = pd.DataFrame({
            "variant": variant, "s": s, "z": z, "r": radius, "coord_area": coord, "proper_area": proper,
            "alpha": fields["alpha"], "A": fields["A"], "beta": fields["beta"],
            "T_nn": tensor[:, 0, 0], "T_nz": tensor[:, 0, 1], "T_nr": tensor[:, 0, 2], "T_zz": tensor[:, 1, 1],
            "T_zr": tensor[:, 1, 2], "T_rr": tensor[:, 2, 2], "T_phiphi": tensor[:, 3, 3],
            "type": census["type"], "rest_energy": census["rho"], "p_z": frame["p_z"], "p_r": frame["p_r"],
            "p_phi": frame["p_phi"], "v_z": frame["v_z"], "v_r": frame["v_r"], "min_null": census["null"],
            "energy_class": np.select([census[k] for k in CLASSES], CLASSES, default="vacuum_or_other")})
    return rows, points


def run(tasks, workers):
    rows, points = [], []
    with ProcessPoolExecutor(workers) as pool:
        for slice_rows, slice_points in pool.map(slice_census, tasks, chunksize=8):
            rows += slice_rows
            if slice_points is not None:
                points.append(slice_points)
    return pd.DataFrame(rows), (pd.concat(points, ignore_index=True) if points else pd.DataFrame())


def axial_zone(z):
    a = np.abs(z)
    return np.select([a <= 2.4, a <= 5.5, a <= 6.5], ["support", "track", "sheath_end"], default="beyond")


SUMS = ["coord_volume", "proper_volume", *(f"proper_volume_{k}" for k in CLASSES),
        "proper_volume_negative_rest_energy", "proper_volume_nec_respecting_negative_energy",
        "proper_volume_without_static_frame", "proper_volume_violating_z", "proper_volume_violating_r",
        "proper_volume_violating_phi", "type_iv", "unresolved", "eulerian_positive", "eulerian_negative",
        "rest_negative", "killing_energy", "komar_density", "komar_abs", "nec_content_coord", "nec_content_proper"]
EXTREMES = {"min_null": "min", "min_rest_energy": "min", "max_abs_component": "max", "max_source_speed": "max",
            "max_static_frame_speed": "max", "max_source_speed_vs_static": "max", "max_alpha": "max"}


def tabulate(frame, dz, keys):
    """Integrals over z (per unit sigma) and extremes, grouped by keys."""
    grouped = frame.groupby(keys, sort=False)
    table = grouped[SUMS].sum()
    for column in [c for c in SUMS if c not in ("type_iv", "unresolved")]:
        table[column] *= dz
    for column, how in EXTREMES.items():
        table[column] = grouped[column].agg(how)
    return table.reset_index()


def transit(frame, dz, ds):
    """Sigma integral of each zone's excess over the standing snapshot."""
    standing = frame[frame.s == STANDING][["z", "zone", *SUMS]]
    live = frame[frame.s < STANDING].merge(standing, on=["z", "zone"], suffixes=("", "_standing"))
    excess = pd.DataFrame({column: live[column]-live[f"{column}_standing"] for column in SUMS})
    excess[["s", "z", "zone", "axial_zone"]] = live[["s", "z", "zone", "axial_zone"]]
    table = excess.groupby(["zone", "axial_zone"])[SUMS].sum()*dz*ds
    table["type_iv"] = live.groupby(["zone", "axial_zone"]).type_iv.sum()
    by_sigma = excess.groupby("s")[["eulerian_negative", "nec_content_coord", "nec_content_proper"]].sum()*dz
    return table.reset_index(), by_sigma.reset_index()


def screen_row(task):
    """Node types of the sheathed variants at one sigma across z: the pre-sheath scale screen."""
    s, z_axis = task
    designs = {variant: design_for(variant) for variant in SCREENED}
    params = choreography.params_for(LANE)
    rows = {variant: {"s": s, "variant": variant, "type_iv": 0, "samples_with_type_iv": 0, "unresolved": 0,
                      "min_null": 0.} for variant in SCREENED}
    for z in z_axis:
        jet = ax.service_jet(s, float(z), params, designs["wide_stack"])
        for variant, design in designs.items():
            tensor = ax.frame_tensor(jet, ax.wall_nodes(design, PER_PANEL)[0], design, z=float(z))
            kinds = ax.classify(tensor, floor=NOISE_FLOOR)["type"]
            row = rows[variant]
            count = int((kinds == ax.TYPE_IV).sum())
            row["type_iv"] += count
            row["samples_with_type_iv"] += int(count > 0)
            row["unresolved"] += int(np.isin(kinds, [ax.UNRESOLVED, ax.TYPE_II_III]).sum())
            row["min_null"] = min(row["min_null"], float(ax.min_null_energy(tensor).min()))
    return list(rows.values())


def approach_gate(s_axis, z_axis, workers):
    """The choreography pass's gate on the approach samples it left out: node types and resolved bands."""
    case = "lane_2p1__static"
    s_values = [float(s) for s in s_axis if s < -1.5-1e-9]
    with ProcessPoolExecutor(workers) as pool:
        jets = {s: array for _, s, array in pool.map(choreography.jets_row, [(case, s, z_axis) for s in s_values])}
        rows = [r for chunk in pool.map(choreography.layer_row, [(case, s, z_axis, jets[s]) for s in s_values],
                                        chunksize=2) for r in chunk]
        samples = pd.DataFrame(rows)
        targets = [(case, float(r.s), float(r.z)) for _, r in
                   samples.nlargest(choreography.RESOLVED_SAMPLES, "estimated_band_width").iterrows()]
        resolved = pd.DataFrame(list(pool.map(choreography.resolve_bands, targets)),
                                columns=["case", "s", "z", "crossings", "width"])
    return samples, resolved


def dense_balances(z=5., count=200001):
    """Energy and Komar balances of one standing z-slice on a dense radial trapezoid rule, over their scales."""
    design = design_for("wide_stack")
    jet = ax.service_jet(STANDING, z, choreography.params_for(LANE), design)
    radius = np.linspace(design.core_radius, design.outer_radius, count)
    tensor = ax.frame_tensor(jet, radius, design, z=z)
    fields = ax.radial_fields(jet, radius, design, z=z)
    weight = 2*math.pi*radius*fields["A"]
    energy = weight*tensor[:, 0, 0]
    komar = weight*fields["alpha"]*(tensor[:, 0, 0]+tensor[:, 1, 1]+tensor[:, 2, 2]+tensor[:, 3, 3])
    return {f"dense_energy_balance_z{z:g}": float(np.trapezoid(energy, radius)/np.trapezoid(np.abs(energy), radius)),
            f"dense_komar_balance_z{z:g}": float(np.trapezoid(komar, radius)/np.trapezoid(np.abs(komar), radius))}


def energy_balance(standing, worst=False):
    """Net Eulerian energy over its absolute scale, for the whole wide-stack slice or its worst z-slice."""
    wide = standing[standing.variant == "wide_stack"].groupby("z")[["eulerian_positive", "eulerian_negative"]].sum()
    net, scale = wide.eulerian_positive+wide.eulerian_negative, wide.eulerian_positive-wide.eulerian_negative
    if worst:
        return float((net.abs()/scale.where(scale > 0)).max())
    return float(net.sum()/scale.sum())


def figure(points, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap, SymLogNorm
    standing = points[(points.variant == "wide_stack") & (points.s == STANDING)]
    codes = {"vacuum_or_other": 0, "ordinary": 1, "nec_respecting": 2, "nec_violating": 3}
    zs = np.sort(standing.z.unique())
    rs = np.sort(standing.r.unique())
    grid = standing.pivot(index="r", columns="z", values="energy_class").reindex(index=rs, columns=zs)
    code = grid.apply(lambda col: col.map(codes)).to_numpy(dtype=float)
    density = standing.pivot(index="r", columns="z", values="T_nn").reindex(index=rs, columns=zs).to_numpy()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4), sharey=True)
    cmap = ListedColormap(["#f2f2f2", "#4c8bd6", "#e3b448", "#c8463d"])
    axes[0].pcolormesh(zs, rs, code, cmap=cmap, vmin=-.5, vmax=3.5, shading="nearest")
    axes[0].set_title("energy-condition class")
    handles = [plt.Rectangle((0, 0), 1, 1, color=cmap(i)) for i in range(4)]
    axes[0].legend(handles, ["vacuum", "ordinary (DEC)", "NEC-respecting", "NEC-violating"], fontsize=7,
                   loc="upper right")
    mesh = axes[1].pcolormesh(zs, rs, density, cmap="RdBu", norm=SymLogNorm(1e-2, vmin=-10, vmax=10),
                              shading="nearest")
    axes[1].set_title("Eulerian energy density")
    fig.colorbar(mesh, ax=axes[1])
    for panel in axes:
        panel.set_xlabel("z")
        panel.set_ylim(0, rs.max())
    axes[0].set_ylabel("r")
    fig.tight_layout()
    fig.savefig(output/"standing_classes.png", dpi=140)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--step", type=float, default=.1)
    parser.add_argument("--z-max", type=float, default=8.)
    parser.add_argument("--sigma-start", type=float, default=-8., help="a sigma at which the geometry is standing")
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/demand_census")
    args = parser.parse_args()
    started = time.time()
    args.output.mkdir(parents=True, exist_ok=True)
    s_axis = np.round(np.arange(args.sigma_start, STANDING+args.step/2, args.step), 10)
    z_axis = np.round(np.arange(-args.z_max, args.z_max+args.step/2, args.step), 10)
    tasks = [("wide_stack", float(s), float(z), bool(s == STANDING)) for s in s_axis for z in z_axis]
    tasks += [(variant, STANDING, float(z), False) for variant in VARIANTS if variant != "wide_stack" for z in z_axis]
    frame, points = run(tasks, args.workers)
    print("census", round(time.time()-started, 1), flush=True)
    frame.to_csv(args.output/"zone_slices.csv.gz", index=False, compression={"method": "gzip", "mtime": 0},
                 float_format="%.8g")
    points.to_csv(args.output/"standing_points.csv.gz", index=False, compression={"method": "gzip", "mtime": 0},
                  float_format="%.7g")
    frame["axial_zone"] = axial_zone(frame.z.values)
    standing = frame[frame.s == STANDING]
    tabulate(standing, args.step, ["variant", "zone", "axial_zone"]).to_csv(args.output/"standing_by_zone.csv",
                                                                           index=False)
    tabulate(standing, args.step, ["variant"]).to_csv(args.output/"standing_totals.csv", index=False)
    wide = frame[frame.variant == "wide_stack"]
    by_zone, by_sigma = transit(wide, args.step, args.step)
    by_zone.to_csv(args.output/"transit_excess_by_zone.csv", index=False)
    by_sigma.to_csv(args.output/"transit_excess_by_sigma.csv", index=False)
    live = tabulate(wide[wide.s < STANDING], args.step, ["zone"])
    live.to_csv(args.output/"transit_extremes_by_zone.csv", index=False)
    checks = {
        "type_iv_points": int(wide.type_iv.sum()), "unresolved_points": int(wide.unresolved.sum()),
        "type_iv_points_beyond_gate_samples": int(wide[(np.abs(wide.z) > 4.9+1e-9) | (wide.s < -1.5-1e-9)].type_iv.sum()),
        "unresolved_points_beyond_gate_samples": int(wide[(np.abs(wide.z) > 4.9+1e-9)
                                                          | (wide.s < -1.5-1e-9)].unresolved.sum()),
        "start_matches_standing": float(np.max(np.abs(
            wide[wide.s == wide.s.min()].sort_values(["z", "zone"])[SUMS].to_numpy()
            - standing[standing.variant == "wide_stack"].sort_values(["z", "zone"])[SUMS].to_numpy()))),
        "exterior_max_abs": float(frame.exterior_max_abs.max()),
        "standing_max_sigma_derivative": float(standing[standing.variant == "wide_stack"].max_sigma_derivative.max()),
        # At the static snapshot both integrals are total divergences: rho sqrt(gamma) = -d_r(r d_r A)/(8 pi)
        # on every z-slice, and alpha (rho + sum p) sqrt(gamma) = D^2 alpha sqrt(gamma)/(4 pi).
        "standing_energy_balance": energy_balance(standing),
        "standing_worst_slice_energy_balance": energy_balance(standing, worst=True),
        "standing_komar_relative": float(standing[standing.variant == "wide_stack"].komar_density.sum()
                                         / standing[standing.variant == "wide_stack"].komar_abs.sum()),
        **dense_balances(),
        "max_source_speed": float(wide.max_source_speed.max()),
        "max_static_frame_speed": float(wide.max_static_frame_speed.max()),
        "max_source_speed_vs_static": float(wide.max_source_speed_vs_static.max()),
    }
    with ProcessPoolExecutor(args.workers) as pool:
        screen = pd.DataFrame([r for rows in pool.map(screen_row, [(float(s), z_axis) for s in s_axis
                                                                    if s <= SCREEN_END+1e-9]) for r in rows])
    screen.to_csv(args.output/"presheath_screen_by_sigma.csv", index=False)
    summary = screen.groupby("variant", sort=False).agg(type_iv=("type_iv", "sum"),
                                                        samples_with_type_iv=("samples_with_type_iv", "sum"),
                                                        unresolved=("unresolved", "sum"), min_null=("min_null", "min"))
    summary.join(tabulate(standing, args.step, ["variant"]).set_index("variant")[
        ["eulerian_positive", "nec_content_coord", "nec_content_proper", "proper_volume"]]).reset_index().to_csv(
        args.output/"presheath_screen.csv", index=False)
    samples, resolved = approach_gate(s_axis, z_axis, args.workers)
    resolved.to_csv(args.output/"approach_resolved_bands.csv", index=False)
    checks.update(approach_samples=len(samples), approach_layer_type_i=int(samples.layer_type_i.sum()),
                  approach_layer_type_iv=int(samples.layer_type_iv.sum()),
                  approach_layer_unresolved=int(samples.layer_unresolved.sum()+samples.layer_type_ii_iii.sum()),
                  approach_envelope_violations=int((samples.envelope_ratio > 1).sum()),
                  approach_resolved_crossings=int(resolved.crossings.sum()),
                  approach_samples_with_band=int((resolved.width > 0).sum()),
                  approach_max_band_width=float(resolved.width.max()))
    figure(points, args.output)
    manifest = {
        "completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time()-started, 1), "workers": args.workers, "step": args.step,
        "sigma_range": [float(s_axis[0]), float(s_axis[-1])], "z_range": [float(z_axis[0]), float(z_axis[-1])],
        "lane": LANE, "support": SUPPORT, "standing_sigma": STANDING, "eta": ETA,
        "planck_lengths_per_unit": 1/math.sqrt(ETA), "per_panel": PER_PANEL, "noise_floor": NOISE_FLOOR,
        "zones": ZONES, "variants": VARIANTS, "screened": SCREENED, "screen_sigma_end": SCREEN_END, "checks": checks,
        "envelope_params_changed": {k: v for k, v in asdict(choreography.ENVELOPE).items()
                                    if v != asdict(choreography.BASE)[k]},
        "software_sha256": {path: sha256_file(ROOT/"toolkit/adm_harness_cli"/path) for path in (
            "adm_harness/axial_track.py", "adm_harness/axial_einstein_generated.py",
            "adm_harness/constant_radius_track.py", "scripts/run_choreography_pass.py",
            "scripts/run_demand_census.py")},
    }
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=1, default=str)+"\n")
    pd.set_option("display.width", 250)
    print(json.dumps(checks, indent=1))
    print(tabulate(standing, args.step, ["variant"]).T.to_string())


if __name__ == "__main__":
    main()
