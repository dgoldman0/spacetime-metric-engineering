#!/usr/bin/env python3
"""Fields at the conical front's tip, against a flat front with the same axis profile; emit data only.

During the lane the pattern is stationary in its own frame, and the surface where the co-moving Killing vector
turns null, alpha^2 = b^2 with b = beta + v, bounds the region the pattern outruns. The geometry stage locates
that surface for the current front and for the cone at mid-lane. It records the surface's causal character (it is
null where the transverse gradient of alpha^2 - b^2 vanishes), the along-track rate kappa = |d_zeta alpha| and, at
the cone's tip, the transverse curvature of the lapse and the rate lambda at which it pushes rays off the axis.

The wave stage evolves a massless scalar field, axisymmetric, on the cone's stationary background around its tip
and on a flat front that repeats the cone's lapse along the axis at every radius out to 6. Wave packets arrive from
ahead, as the field that the pattern overtakes, and from inside the cone, as field moving forward through the
pattern. Each run records the energy density that the normal observers measure at the tip, the energy there and
in the whole domain, and the Killing energy away from the absorbing layers. Narrative interpretation is maintained
manually in supporting_reports.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
import pandas as pd
from scipy.optimize import brentq

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adm_harness import compartment_service as cs
from adm_harness import front_surface as fs
from adm_harness import scalar_wave as sw
from adm_harness.constant_radius_track import smooth_step
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
SIGMA = 3.75
SPEED = 2.1
H = 1e-4
GRID_STEP = .03
COURANT = .45
DISSIPATION = .05
DOMAIN = (-12., 14., 8.)
LAYERS = {"back": 2.5, "front": 2., "outer": 1.5, "rate": 8.}
FLAT_RADIUS = (6., 1.)
TIP_BOX = (1.5, 1.)
RECORD_EVERY = .05
REFINED = {"grid_step": .015, "domain": (-9., 5., 7.), "layers": {"back": 1.5, "front": 1.5, "outer": 1.2, "rate": 8.}}
PACKETS = {
    "ahead_axis_short": dict(offset=4., r0=0., width_zeta=1., width_r=.5, wavelength=1., end=10.),
    "ahead_axis_wide": dict(offset=4., r0=0., width_zeta=1., width_r=1.5, wavelength=1., end=10.),
    "ahead_axis_long": dict(offset=7., r0=0., width_zeta=1.5, width_r=1.5, wavelength=3., end=13.),
    "ahead_ring": dict(offset=4., r0=1.5, width_zeta=1., width_r=.5, wavelength=1., end=10.),
    "inside_axis": dict(offset=-5., r0=0., width_zeta=1., width_r=.5, wavelength=1., end=8.),
    "inside_axis_wide": dict(offset=-5., r0=0., width_zeta=1., width_r=1.5, wavelength=1., end=8.),
    "inside_axis_refined": dict(offset=-4.5, r0=0., width_zeta=1., width_r=.5, wavelength=1., end=3.5, refined=True),
    "inside_axis_wide_refined": dict(offset=-4.5, r0=0., width_zeta=1., width_r=1.5, wavelength=1., end=3.5,
                                     refined=True),
}


def build():
    service = cs.CompartmentService()
    return service, cs.axial_design(service), fs.ConeFront()


def alpha_and_b(service, design, front, zeta, r):
    """Co-moving lapse and shift b = beta + v at offsets zeta from the packet and radii r, at mid-lane."""
    centre = service.packet_position(SIGMA)
    log_alpha, beta = fs.log_lapse_and_shift(service, design, front, SIGMA, centre+np.asarray(zeta), np.asarray(r))
    return np.exp(log_alpha), beta+service.carry_speed(SIGMA)


def surface_row(task):
    """Where alpha^2 = b^2 along one radius, with the surface's normal and the along-track rate there."""
    name, radius, side = task
    service, design, cone = build()
    front = cone if name == "cone" else None

    def g(zeta):
        a, b = alpha_and_b(service, design, front, np.array([zeta]), np.array([radius]))
        return float(a[0]**2-b[0]**2)
    lo, hi = ((4.3, 72.) if side == "front" else (-7.5, -4.3))
    grid = np.linspace(lo, hi, 4001)
    values = np.array([g(z) for z in grid])
    hits = np.flatnonzero(np.sign(values[:-1]) != np.sign(values[1:]))
    if not len(hits):
        return {"front": name, "side": side, "r": radius, "zeta": math.nan}
    i = hits[-1] if side == "front" else hits[0]
    zeta = brentq(g, grid[i], grid[i+1], xtol=1e-12)

    def a(z, r):
        return float(alpha_and_b(service, design, front, np.array([z]), np.array([abs(r)]))[0][0])
    a_zeta = (a(zeta+H, radius)-a(zeta-H, radius))/(2*H)
    a_r = (a(zeta, radius+H)-a(zeta, radius-H))/(2*H) if radius > H else 0.
    return {"front": name, "side": side, "r": radius, "zeta": zeta, "alpha": a(zeta, radius),
            "d_zeta_alpha": a_zeta, "d_r_alpha": a_r, "kappa": abs(a_zeta),
            "transverse_over_along": abs(a_r)/abs(a_zeta), "normal_norm": 4*a(zeta, radius)**2*a_r**2}


def tip_rates():
    service, design, cone = build()

    def a(z, r):
        return float(alpha_and_b(service, design, cone, np.array([z]), np.array([r]))[0][0])
    zeta = brentq(lambda z: a(z, 0.)**2-SPEED**2, 55., cone.tip(service), xtol=1e-12)
    kappa = abs((a(zeta+H, 0.)-a(zeta-H, 0.))/(2*H))
    step = 1e-3
    curvature = -2*(a(zeta, step)-a(zeta, 0.))/step**2
    lam = (-kappa+math.sqrt(kappa**2+4*SPEED*curvature))/2
    return {"tip_offset": cone.tip(service), "surface_offset": zeta, "kappa": kappa, "transverse_curvature": curvature,
            "lambda": lam, "lambda_over_kappa": lam/kappa, "field_decay_rate": 2*(lam-kappa),
            "flat_growth_rate": 2*kappa}


def background(kind, surface, refined=False):
    """Grid, lapse, shift and damping around the tip; the flat front repeats the axis lapse out to FLAT_RADIUS."""
    service, design, cone = build()
    step = REFINED["grid_step"] if refined else GRID_STEP
    back, ahead, radius = REFINED["domain"] if refined else DOMAIN
    layers = REFINED["layers"] if refined else LAYERS
    zeta = surface+np.arange(back, ahead, step)+step/2
    r = np.arange(0., radius, step)+step/2
    zz, rr = np.meshgrid(zeta, r, indexing="ij")
    alpha, b = alpha_and_b(service, design, cone, zz.ravel(), rr.ravel())
    alpha, b = alpha.reshape(zz.shape), b.reshape(zz.shape)
    if kind == "flat":
        axis, _ = alpha_and_b(service, design, cone, zeta, np.zeros_like(zeta))
        start, width = FLAT_RADIUS
        blend = 1-np.array([smooth_step((x-start)/width) for x in r])
        alpha = 1+(axis[:, None]-1)*blend[None, :]
    damping = sw.damping_layer(zeta, r, back=layers["back"], front=layers["front"], outer=layers["outer"],
                               rate=layers["rate"])
    return zeta, r, alpha, b, damping


def run(task):
    kind, packet_name, surface = task
    spec = PACKETS[packet_name]
    zeta, r, alpha, b, damping = background(kind, surface, spec.get("refined", False))
    wave = sw.AxisymmetricWave(zeta, r, alpha, b, damping, dissipation=DISSIPATION)
    wave.set_packet(surface+spec["offset"], spec["r0"], spec["width_zeta"], spec["width_r"], spec["wavelength"])
    free = damping == 0
    box = (np.abs(zeta[:, None]-surface) < TIP_BOX[0]) & (r[None, :] < TIP_BOX[1])
    dt = wave.stable_step(COURANT)
    every = max(1, round(RECORD_EVERY/dt))
    volume = wave.cell_volume()
    rows, t, step = [], 0., 0
    reference = float(wave.energy_density().max())
    started = time.time()
    while t <= spec["end"]+1e-9:
        if step % every == 0:
            e = wave.energy_density()
            where = np.unravel_index(np.argmax(np.where(free, e, 0.)), e.shape)
            rows.append({"background": kind, "packet": packet_name, "t": t,
                         "tip_peak_density": float(e[box].max())/reference,
                         "tip_energy": float(np.sum((e*volume)[box])),
                         "free_energy": float(np.sum((e*volume)[free])),
                         "max_density": float(e[free].max())/reference,
                         "max_density_offset": float(zeta[where[0]]-surface), "max_density_r": float(r[where[1]]),
                         "killing_energy_free": wave.killing_energy(free)})
        wave.step(dt)
        t += dt
        step += 1
    frame = pd.DataFrame(rows)
    frame["tip_energy"] /= frame.free_energy.iloc[0]
    frame["free_energy"] /= frame.free_energy.iloc[0]
    return frame, round(time.time()-started, 1)


def rate(frame, column, window):
    part = frame[(frame.t >= window[0]) & (frame.t <= window[1]) & (frame[column] > 0)]
    if len(part) < 5:
        return math.nan
    return float(np.polyfit(part.t, np.log(part[column]), 1)[0])


def summarize(frame):
    """Peak and rates at the tip within the resolved window, where the Killing energy holds to 1%."""
    deviation = (frame.killing_energy_free/frame.killing_energy_free.iloc[0]-1).abs()
    broken = np.flatnonzero(deviation.values > .01)
    t_valid = float(frame.t.iloc[broken[0]]) if len(broken) else float(frame.t.iloc[-1])
    frame = frame[frame.t <= t_valid]
    peak = frame.loc[frame.tip_peak_density.idxmax()]
    after = frame[frame.t >= peak.t]
    rising = frame[frame.tip_peak_density > .3]
    return {"background": frame.background.iloc[0], "packet": frame.packet.iloc[0], "resolved_until": t_valid,
            "rate_while_above_0p3": float(np.polyfit(rising.t, np.log(rising.tip_peak_density), 1)[0])
            if len(rising) > 5 else math.nan,
            "tip_peak_over_initial_peak": float(peak.tip_peak_density), "time_of_tip_peak": float(peak.t),
            "tip_rate_after_peak": rate(after[after.tip_peak_density > 1e-8], "tip_peak_density",
                                        (peak.t, t_valid)),
            "tip_energy_peak": float(frame.tip_energy.max()),
            "tip_energy_rate_after_peak": rate(after[after.tip_energy > 1e-12], "tip_energy", (peak.t, t_valid)),
            "final_tip_peak_density": float(frame.tip_peak_density.iloc[-1]),
            "max_density_over_run": float(frame.max_density.max()),
            "free_energy_final": float(frame.free_energy.iloc[-1])}


def resolved(frame):
    """The part of a history before its free-region Killing energy departs from conservation by 1%."""
    deviation = (frame.killing_energy_free/frame.killing_energy_free.iloc[0]-1).abs()
    broken = np.flatnonzero(deviation.values > .01)
    return frame.iloc[:broken[0]+1] if len(broken) else frame


FIGURE_PACKETS = {"ahead_axis_short": "C0", "ahead_axis_wide": "C1", "ahead_axis_long": "C2", "ahead_ring": "C3",
                  "inside_axis_refined": "C4", "inside_axis_wide_refined": "C5"}
FRONT_COLOURS = {"current_front": "C3", "cone": "C0"}


def figure(output, frames, surfaces, rates):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
    for name, colour in FIGURE_PACKETS.items():
        for kind, style in (("cone", "-"), ("flat", "--")):
            if (kind, name) not in frames:
                continue
            part = resolved(frames[(kind, name)])
            axes[0].plot(part.t, part.tip_peak_density, style, color=colour,
                         label=name.replace("_refined", "").replace("_", " ") if kind == "cone" else None)
            if kind == "flat":
                axes[0].plot(part.t.iloc[-1], part.tip_peak_density.iloc[-1], "x", color=colour)
    axes[0].set_yscale("log")
    axes[0].set_ylim(1e-9, 3e2)
    axes[0].set_xlabel("time in the pattern's frame")
    axes[0].set_ylabel("peak energy density at the tip / initial peak")
    axes[0].set_title("solid: cone; dashed: flat front with the same axis lapse (x: grid limit)", fontsize=9)
    axes[0].legend(fontsize=7)
    for name, marker in (("current_front", "o-"), ("cone", "s-")):
        part = surfaces[(surfaces.front == name) & (surfaces.side == "front")].dropna()
        axes[1].plot(part.r, part.transverse_over_along, marker, color=FRONT_COLOURS[name],
                     label=name.replace("_", " "))
        axes[2].plot(part.zeta, part.r, marker, color=FRONT_COLOURS[name], label=name.replace("_", " "))
    axes[1].set_xlabel("r")
    axes[1].set_ylabel(r"$|\partial_r\alpha|/|\partial_\zeta\alpha|$ on the surface $\alpha=b$")
    axes[1].set_yscale("symlog", linthresh=1e-3)
    axes[1].legend(fontsize=8)
    axes[1].set_title("zero: null surface, a horizon; positive: timelike, crossable", fontsize=9)
    axes[2].set_xlabel(r"offset from the packet $\zeta$")
    axes[2].set_ylabel("r")
    axes[2].set_title(f"surface alpha = b at mid-lane; tip: kappa = {rates['kappa']:.2f}, lambda = {rates['lambda']:.2f}",
                      fontsize=9)
    axes[2].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output/"cone_tip_fields.png", dpi=120)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/cone_tip_field_pass")
    parser.add_argument("--refined-only", action="store_true",
                        help="run only the refined inside packets and merge them with the stored histories")
    parser.add_argument("--figure-only", action="store_true", help="redraw the figure from the stored outputs")
    args = parser.parse_args()
    started = time.time()
    if args.figure_only:
        stored = pd.read_csv(args.output/"tip_histories.csv.gz")
        figure(args.output, {key: group.reset_index(drop=True) for key, group in
                             stored.groupby(["background", "packet"], sort=False)},
               pd.read_csv(args.output/"light_surfaces.csv"), json.loads((args.output/"tip_rates.json").read_text()))
        manifest_path = args.output/"manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())
            manifest["software_sha256"] = {path: sha256_file(ROOT/"toolkit/adm_harness_cli"/path) for path in (
                "adm_harness/scalar_wave.py", "adm_harness/front_surface.py", "scripts/run_cone_tip_field_pass.py")}
            manifest_path.write_text(json.dumps(manifest, indent=1, default=str)+"\n")
        return
    args.output.mkdir(parents=True, exist_ok=True)
    radii = (0., .5, 1., 2., 3.5, 5., 6.5, 8., 9., 10., 11., 11.5, 12., 13.)
    tasks = [(name, r, side) for name in ("current_front", "cone") for r in radii for side in ("front", "rear")]
    refined = [name for name, spec in PACKETS.items() if spec.get("refined")]
    with ProcessPoolExecutor(args.workers) as pool:
        if args.refined_only:
            surfaces = pd.read_csv(args.output/"light_surfaces.csv")
            rates = json.loads((args.output/"tip_rates.json").read_text())
            stored = pd.read_csv(args.output/"tip_histories.csv.gz")
            stored = stored[~stored.packet.isin(refined)]
            names = refined
        else:
            surfaces = pd.DataFrame(list(pool.map(surface_row, tasks)))
            surfaces.to_csv(args.output/"light_surfaces.csv", index=False)
            rates = tip_rates()
            (args.output/"tip_rates.json").write_text(json.dumps(rates, indent=1)+"\n")
            print(surfaces.to_string(index=False), json.dumps(rates), round(time.time()-started, 1), flush=True)
            stored = None
            names = list(PACKETS)
        results = list(pool.map(run, [(kind, name, rates["surface_offset"]) for name in names
                                      for kind in ("cone", "flat")]))
    frames = {}
    if stored is not None:
        frames = {key: group.reset_index(drop=True) for key, group in stored.groupby(["background", "packet"],
                                                                                     sort=False)}
    frames.update({(frame.background.iloc[0], frame.packet.iloc[0]): frame for frame, _ in results})
    pd.concat(frames.values()).to_csv(args.output/"tip_histories.csv.gz", index=False,
                                      compression={"method": "gzip", "mtime": 0}, float_format="%.7g")
    summary = pd.DataFrame([summarize(frame) for frame in frames.values()])
    summary.to_csv(args.output/"tip_summary.csv", index=False)
    pd.set_option("display.width", 250)
    print(summary.to_string(index=False), flush=True)
    figure(args.output, frames, surfaces, rates)
    seconds = {f"{f.background.iloc[0]}:{f.packet.iloc[0]}": s for f, s in results}
    manifest_path = args.output/"manifest.json"
    if args.refined_only and manifest_path.exists():
        previous = json.loads(manifest_path.read_text())
        seconds = {**previous.get("run_seconds", {}), **seconds}
    manifest = {"sigma": SIGMA, "speed": SPEED, "grid_step": GRID_STEP, "courant": COURANT,
                "dissipation": DISSIPATION, "domain": DOMAIN, "layers": LAYERS, "refined": REFINED,
                "flat_radius": FLAT_RADIUS, "tip_box": TIP_BOX, "packets": PACKETS, "cone": fs.ConeFront().__dict__,
                "tip_rates": rates, "run_seconds": seconds, "elapsed_seconds": round(time.time()-started, 1),
                "software_sha256": {path: sha256_file(ROOT/"toolkit/adm_harness_cli"/path) for path in (
                    "adm_harness/scalar_wave.py", "adm_harness/front_surface.py",
                    "scripts/run_cone_tip_field_pass.py")}}
    manifest_path.write_text(json.dumps(manifest, indent=1, default=str)+"\n")

if __name__ == "__main__":
    main()
