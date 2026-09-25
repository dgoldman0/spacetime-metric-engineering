#!/usr/bin/env python3
"""Source scaling test against the lapse-staged rail's transit demand; emit data only.

The selected one-space design (the 2.1c lane on a flat support, the convex
packet lapse plateau and the lapse sheath riding with the packet) demands a
stress that falls as 1/L^2 with the rail's unit length L. This run measures
the dimensionless functionals that decide how candidate source families scale
against it:

1. Quantum fields. Every static source unit's history of the static-frame
   null-energy deficit, with the curvature radius and acceleration that bound
   a flat-space quantum inequality's sampling time. A screen over the transit
   ranks worldlines; Gaussian samplings along the leading worldlines, with a
   fixed null direction and a self-consistent window, give the number of free
   massless scalars required per (L / l_P)^2.
2. Curvature-coupled classical fields. Null geodesics through the demand, the
   null-energy integral along each, and the zero-energy solution of
   -d^2/dlambda^2 + 8 pi T(k, k) from each end, whose zeros count bound states.
3. Casimir cavities. The cavity gap matching the peak deficit, and the rest
   energy of the thinnest plasma mirror bounding it.

Narrative interpretation is maintained manually in supporting_reports.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
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
import run_lapse_staging_pass as staging
from adm_harness import axial_track as ax
from adm_harness import source_scaling as ss
from adm_harness.constant_radius_track import packet_position
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
SELECTED, COMPARISON = "lapse_staged", "lapse_static"
SIGMA_RANGE = (-4.4, 3.4)
Z_MAX = 10.
PER_PANEL = 12
DEFICIT_FLOOR = 1e-7
FRACTIONS = (.01, .1, .3)
REFERENCE_FRACTION = .1
CANDIDATES = 50
WINDOW_SAMPLES = 30
HISTORY_STEP = .005
MAIN_DEMAND = .01
UNIT_LENGTHS = {"recorded normalization": 1/math.sqrt(2.4127904527582454e-5)*ss.PLANCK_LENGTH,
                "1 micrometre": 1e-6, "1 millimetre": 1e-3, "1 metre": 1., "1 kilometre": 1e3}
GRAVITY_TEST_LENGTH = 52e-6  # m, inverse-square law verified to this separation (Lee et al. 2020)
RAY_STEP = .02


def radius_nodes(design):
    nodes, weights = ax.wall_nodes(design, PER_PANEL)
    return (np.concatenate([[0.], nodes]),
            np.concatenate([[math.pi*design.core_radius**2], weights*2*math.pi*nodes]))


def scan_row(task):
    """Static-frame null energy, local scale and static lapse over (z, r) at one sigma."""
    name, s, z_axis = task
    design, params = staging.design_for(name), staging.params_for(name)
    radius, _ = radius_nodes(design)
    out = np.empty((3, len(z_axis), len(radius)), dtype=np.float32)
    for index, z in enumerate(z_axis):
        demand = ss.static_demand(ax.service_jet(s, float(z), params, design), radius, design, float(z), s)
        out[0, index], out[1, index], out[2, index] = (demand.null_energy, np.minimum(demand.scale, 1e30),
                                                       demand.static_lapse)
    return s, out


def screen(null, scale, lapse, step, fraction=REFERENCE_FRACTION, chunk=200):
    """Requirement 64 pi^2 max(0, -<n>) tau^4 on every static worldline, with a self-consistent window.

    Along each worldline (fixed z and r) the Gaussian's standard deviation tau
    obeys tau <= fraction * (smallest local scale within |t - t_i| <= 3 tau),
    with t the static observers' proper time. Iteration from tau = fraction *
    scale lowers tau until no window changes. <n> is the Gaussian average of
    the pointwise null minimum over the sampled history, zero outside it; a
    window narrower than a quarter of the local proper-time spacing takes the
    pointwise value.
    """
    null, scale, lapse = (np.asarray(x, dtype=float) for x in (null, scale, lapse))
    count = null.shape[0]
    proper = np.concatenate([np.zeros((1,)+lapse.shape[1:]),
                             np.cumsum(.5*(lapse[1:]+lapse[:-1])*step, axis=0)]).reshape(count, -1)
    values = null.reshape(count, -1).copy()
    values[np.abs(values) < DEFICIT_FLOOR] = 0.
    flat_scale = scale.reshape(count, -1)
    tau = fraction*flat_scale.copy()
    average = np.zeros_like(values)
    for lo in range(0, tau.shape[1], chunk):
        t = proper[:, lo:lo+chunk]
        local = flat_scale[:, lo:lo+chunk]
        gap = np.abs(t[:, None, :]-t[None, :, :])
        window = tau[:, lo:lo+chunk]
        for _ in range(40):
            nearest = np.where(gap <= 3*window[:, None, :], local[None, :, :], np.inf).min(axis=1)
            updated = np.minimum(window, fraction*nearest)
            if np.all(updated >= window*(1-1e-12)):
                break
            window = updated
        tau[:, lo:lo+chunk] = window
        weights = np.zeros_like(t)
        weights[1:-1] = .5*(t[2:]-t[:-2])
        weights[0], weights[-1] = .5*(t[1]-t[0]), .5*(t[-1]-t[-2])
        kernel = np.exp(-gap**2/(2*window[:, None, :]**2))/np.sqrt(2*np.pi*window[:, None, :]**2)
        smoothed = np.einsum("ijw,jw,jw->iw", kernel, values[:, lo:lo+chunk], weights)
        spacing = np.maximum(weights, 1e-300)
        average[:, lo:lo+chunk] = np.where(window < .25*spacing, values[:, lo:lo+chunk], smoothed)
    tau = tau.reshape(null.shape)
    deficit = np.maximum(-null, 0.)
    deficit[deficit < DEFICIT_FLOOR] = 0.
    requirement = ss.QI_GAUSSIAN*np.maximum(-average.reshape(null.shape), 0.)*tau**4
    return requirement, deficit, tau


def fixed_direction_history(name, z, r, s_centre, tau, direction):
    """T(l, l) along the static worldline for l = u + e with fixed static-triad components e.

    Steps take a proper time of at most tau / WINDOW_SAMPLES and at most
    HISTORY_STEP in sigma, and cover |t - t_centre| <= 4 tau within the
    sampled transit; the staged geometry is flat outside it, where T(l, l)
    vanishes and the Gaussian average receives nothing.
    """
    design, params = staging.design_for(name), staging.params_for(name)
    e = np.asarray(direction, dtype=float)
    vector = np.concatenate([[1.], e])

    def sample(s):
        demand = ss.static_demand(ax.service_jet(s, z, params, design), [r], design, z, s)
        return (float(vector@demand.tensor[0]@vector), float(demand.scale[0]), float(demand.static_lapse[0]))

    centre = sample(s_centre)
    rows = {0.: (s_centre, *centre)}
    for sign in (1., -1.):
        s, t, lapse = s_centre, 0., centre[2]
        while abs(t) < 4*tau and SIGMA_RANGE[0] <= s <= SIGMA_RANGE[1]:
            ds = sign*min(tau/(WINDOW_SAMPLES*lapse), HISTORY_STEP)
            value = sample(s+ds)
            t += .5*(lapse+value[2])*ds
            s, lapse = s+ds, value[2]
            rows[t] = (s, *value)
    times = np.array(sorted(rows))
    table = np.array([rows[t] for t in times])
    return times, table[:, 0], table[:, 1], table[:, 2]


def targeted_row(task):
    """Self-consistent Gaussian sampling of the fixed-direction null energy along one static worldline."""
    name, z, r, s_centre = task
    design, params = staging.design_for(name), staging.params_for(name)
    demand = ss.static_demand(ax.service_jet(s_centre, z, params, design), [r], design, z, s_centre)
    direction, minimum = ss.null_direction(demand.tensor[0])
    row = {"design": name, "z": z, "r": r, "s": s_centre, "null_minimum": minimum,
           "scale": float(demand.scale[0]), "curvature_radius": float(demand.curvature_radius[0]),
           "acceleration": float(demand.acceleration[0]), "static_lapse": float(demand.static_lapse[0]),
           "direction_z": direction[0], "direction_r": direction[1], "direction_phi": direction[2]}
    for fraction in FRACTIONS:
        tau = fraction*float(demand.scale[0])
        for _ in range(12):
            times, _, values, scales = fixed_direction_history(name, z, r, s_centre, tau, direction)
            inside = np.abs(times) <= 3*tau
            admissible = fraction*float(np.min(scales[inside]))
            if admissible >= tau*(1-1e-9):
                break
            tau = admissible
        requirement = ss.sampled_requirement(times, values, 0., tau)
        row[f"tau_{fraction:g}"] = tau
        row[f"requirement_{fraction:g}"] = requirement
        row[f"pointwise_{fraction:g}"] = float(ss.qi_requirement(minimum, tau/fraction, fraction))
        row[f"window_min_scale_{fraction:g}"] = float(np.min(scales[np.abs(times) <= 3*tau]))
    return row


def first_zero(lam, psi, xs):
    """Location of the first sign change of psi along the samples, or None."""
    change = np.flatnonzero(np.sign(psi[1:]) != np.sign(psi[:-1]))
    if not len(change):
        return None
    i = int(change[0])
    w = psi[i]/(psi[i]-psi[i+1])
    return float(lam[i]+w*(lam[i+1]-lam[i])), xs[i]+w*(xs[i+1]-xs[i])


def ray_row(task):
    """Trace one null geodesic both ways; its null potential, null integral and zero-energy solutions.

    The zero-energy solution runs from each end with psi = 1 and psi' = 0.
    Its bound-state count decides whether F > 0 with F'' <= 8 pi T(k, k) F
    exists on the ray; the first zero from each end bounds where F vanishes.
    """
    label, name, s, z, r, direction = task
    design, params = staging.design_for(name), staging.params_for(name)
    spacetime = ss.AxialSpacetime(design, params)
    start = np.array([s, z, r if r > 0 else .5*design.core_radius, 0.])
    _, fields = spacetime.fields(*start[:3])
    lam, xs, ks = ss.trace_null_geodesic(spacetime, start, ss.launch_vector(fields, direction), step=RAY_STEP)
    order = np.argsort(lam)
    lam, xs, ks = lam[order], xs[order], ks[order]
    potential, energy = ss.null_potential(spacetime, xs, ks)
    drift = []
    for x, k, e in zip(xs[::25], ks[::25], energy[::25]):
        g = ss.metric_jets(spacetime.fields(*x[:3])[1])[0][0]
        drift.append(abs(k@g@k)/float(e*e))
    left, left_slope = ss.zero_energy_solution(lam, potential)
    right, right_slope = ss.zero_energy_solution(-lam[::-1], potential[::-1])
    right, right_slope = right[::-1], -right_slope[::-1]
    integral = float(np.trapezoid(potential, lam))
    absolute = float(np.trapezoid(np.abs(potential), lam))
    lowest = int(np.argmin(potential))
    row = {"label": label, "design": name, "s": s, "z": z, "r": r, "direction_z": direction[0],
           "direction_r": direction[1], "direction_phi": direction[2], "points": len(lam),
           "affine_length": float(lam[-1]-lam[0]), "start_s": float(xs[0, 0]), "end_s": float(xs[-1, 0]),
           "start_r": float(xs[0, 2]), "end_r": float(xs[-1, 2]), "start_z": float(xs[0, 1]),
           "end_z": float(xs[-1, 1]), "min_potential": float(potential.min()),
           "min_potential_s": float(xs[lowest, 0]), "min_potential_z": float(xs[lowest, 1]),
           "min_potential_r": float(xs[lowest, 2]), "null_integral": integral,
           "null_integral_ratio": integral/absolute if absolute > 0 else 0.,
           "bound_states": ss.bound_state_count(left, left_slope),
           "bound_states_from_exit": ss.bound_state_count(right[::-1], -right_slope[::-1]),
           "exit_value": float(left[-1]), "exit_slope": float(left_slope[-1]),
           "end_potentials": float(max(abs(potential[0]), abs(potential[-1]))),
           "max_null_drift": float(max(drift)), "blueshift_range": float(energy.max()/energy.min())}
    for side, found in (("entry", first_zero(lam, left, xs)),
                        ("exit", first_zero(lam[::-1], right[::-1], xs[::-1]))):
        for key, value in zip(("lambda", "s", "z", "r"),
                              (math.nan,)*4 if found is None else (found[0], *found[1][:3])):
            row[f"{side}_zero_{key}"] = float(value)
    path = {"lam": lam, "x": xs, "potential": potential, "entry_psi": left, "exit_psi": right}
    return row, path


def distinct(rows, key, count, separation=.4):
    chosen = []
    for row in sorted(rows, key=lambda item: item[key], reverse=True):
        if all(abs(row["z"]-c["z"])+abs(row["r"]-c["r"])+abs(row["s"]-c["s"]) > separation for c in chosen):
            chosen.append(row)
        if len(chosen) == count:
            break
    return chosen


def ray_tasks(name, deficits, requirements):
    path = staging.design_for(name).track.packet_path
    tasks = []
    for index, row in enumerate(distinct(deficits, "deficit", 16)):
        tasks.append((f"deficit_{index:02d}", name, row["s"], row["z"], row["r"], row["direction"]))
    for index, row in enumerate(distinct(requirements, "requirement", 8)):
        tasks.append((f"requirement_{index:02d}", name, row["s"], row["z"], row["r"], row["direction"]))
    for s in (-3., -2., -1., -.5, 0., .5, 1., 2.):
        tasks.append((f"radial_s{s:+.1f}", name, s, packet_position(s, path), 2., (0., 1., 0.)))
    for s in (-1., .5):
        for r in (0., 3., 6., 9., 11.):
            tasks.append((f"axial_s{s:+.1f}_r{r:g}", name, s, packet_position(s, path)-1., r, (1., 0., 0.)))
    for r in (0., 11.):
        tasks.append((f"axial_back_s+0.5_r{r:g}", name, .5, packet_position(.5, path)+1., r, (-1., 0., 0.)))
    return tasks


ZONES = {"service region": (0., 1.75), "inner band": (1.75, 3.75), "sheath rise": (3.75, 8.75),
         "sheath plateau": (8.75, 9.25), "outer falls": (9.25, 13.25)}


def zone_of(r):
    return next(name for name, (lo, hi) in ZONES.items() if r <= hi)


def leading(array, s_axis, z_axis, radius, key, count, mask=None):
    """The count leading nodes of array, pairwise separated, optionally restricted to a radial mask."""
    data = array if mask is None else np.where(mask[None, None, :], array, 0.)
    candidates = []
    for index in np.argsort(data, axis=None)[::-1][:6000]:
        i, j, k = np.unravel_index(index, data.shape)
        if data[i, j, k] <= 0:
            break
        candidates.append({"s": float(s_axis[i]), "z": float(z_axis[j]), "r": float(radius[k]),
                           key: float(data[i, j, k])})
    return distinct(candidates, key, count)


def launch_rows(name, requirement, deficit, s_axis, z_axis, radius):
    """Leading deficit nodes, and leading requirement nodes in every radial zone, with minimizing directions."""
    design, params = staging.design_for(name), staging.params_for(name)
    rows = {"deficit": leading(deficit, s_axis, z_axis, radius, "deficit", 24), "requirement": []}
    main = deficit >= MAIN_DEMAND*deficit.max()
    for zone, (lo, hi) in ZONES.items():
        mask = (radius <= hi) & ((radius > lo) | (lo == 0))
        for row in leading(np.where(main, requirement, 0.), s_axis, z_axis, radius, "requirement",
                           CANDIDATES//len(ZONES), mask):
            rows["requirement"].append({**row, "zone": zone, "demand": "main"})
    for row in leading(np.where(main, 0., requirement), s_axis, z_axis, radius, "requirement", 10):
        rows["requirement"].append({**row, "zone": zone_of(row["r"]), "demand": "tail"})
    for row in rows["deficit"]+rows["requirement"]:
        demand = ss.static_demand(ax.service_jet(row["s"], row["z"], params, design), [row["r"]], design,
                                  row["z"], row["s"])
        row["direction"] = tuple(float(x) for x in ss.null_direction(demand.tensor[0])[0])
        row.setdefault("zone", zone_of(row["r"]))
    return rows


def figures(output, radius, z_axis, deficit, requirement, witness):
    """Transit footprints of the deficit and the screened requirement, and the radial witness ray."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.4))
    shown = radius.copy()
    shown[0] = 0.
    panels = ((axes[0], deficit.max(axis=0), "largest static-frame null deficit over the transit", {}),
              (axes[1], np.log10(np.maximum(requirement.max(axis=0), 1e-10)),
               r"largest log$_{10}$ fields per $(L/\ell_P)^2$ over the transit, $f=0.1$", {"vmin": -8}))
    for axis, data, title, limits in panels:
        mesh = axis.pcolormesh(z_axis, shown, data.T, shading="nearest", cmap="viridis", **limits)
        fig.colorbar(mesh, ax=axis)
        axis.set_xlabel("z")
        axis.set_ylabel("r")
        axis.set_ylim(0, 13.5)
        axis.set_title(title, fontsize=9)
    if witness is not None:
        row, path = witness
        r = path["x"][:, 2]
        axis_index = int(np.argmin(r))
        signed = np.where(np.arange(len(r)) < axis_index, -r, r)
        axis = axes[2]
        axis.plot(signed, path["potential"], color="C3", lw=1, label=r"$8\pi T(k,k)$")
        axis.set_yscale("symlog", linthresh=1.)
        axis.set_xlabel("radius along the ray (entry side negative)")
        axis.set_ylabel(r"$8\pi T(k,k)$")
        twin = axis.twinx()
        twin.plot(signed, np.clip(path["entry_psi"], -1.5, 1.5), color="C0", label=r"$\psi$ from entry")
        twin.plot(signed, np.clip(path["exit_psi"], -1.5, 1.5), color="C2", label=r"$\psi$ from exit")
        twin.axhline(0, color="k", lw=.5)
        twin.set_ylim(-1.6, 1.6)
        twin.set_ylabel(r"$\psi$ (clipped)")
        axis.set_title(f"radial ray through the packet, sigma = {row['s']:g}: {row['bound_states']} bound states",
                       fontsize=9)
        lines = axis.get_legend_handles_labels()
        extra = twin.get_legend_handles_labels()
        twin.legend(lines[0]+extra[0], lines[1]+extra[1], fontsize=8, loc="lower center")
    fig.tight_layout()
    fig.savefig(output/"source_scaling.png", dpi=130)
    plt.close(fig)


def casimir_table(peak):
    """Ideal-mirror cavity matching the peak deficit at each unit length, with its mode energy and mirror bound."""
    rows = []
    for label, length in UNIT_LENGTHS.items():
        gap = ss.casimir_gap(peak, length)
        rows.append({"unit_length": label, "unit_length_m": length, "gap_m": gap,
                     "gap_over_electron_compton": gap/ss.ELECTRON_COMPTON,
                     "mode_energy_MeV": 2*math.pi*ss.HBAR*ss.LIGHT_SPEED/gap/1.602176634e-13,
                     "electron_mirror_overhead": ss.mirror_overhead(gap)})
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--step", type=float, default=.05)
    parser.add_argument("--z-step", type=float, default=.1)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/source_scaling_test")
    parser.add_argument("--scratch", type=Path, default=Path("/tmp/rail-source-scaling"))
    parser.add_argument("--reuse-scan", action="store_true", help="load saved scans from the scratch directory")
    args = parser.parse_args()
    started = time.time()
    args.output.mkdir(parents=True, exist_ok=True)
    args.scratch.mkdir(parents=True, exist_ok=True)
    s_axis = np.round(np.arange(SIGMA_RANGE[0], SIGMA_RANGE[1]+args.step/2, args.step), 10)
    z_axis = np.round(np.arange(-Z_MAX, Z_MAX+args.z_step/2, args.z_step), 10)
    summary, screens = {}, {}
    for name in (SELECTED, COMPARISON):
        design = staging.design_for(name)
        radius, area = radius_nodes(design)
        saved = args.scratch/f"scan_{name}.npz"
        if args.reuse_scan and saved.exists():
            with np.load(saved) as data:
                if not (np.array_equal(data["s"], s_axis) and np.array_equal(data["z"], z_axis)):
                    raise ValueError("the saved scan uses a different grid")
                null, scale, lapse = data["null"], np.minimum(data["scale"], 1e30), data["lapse"]
        else:
            with ProcessPoolExecutor(args.workers) as pool:
                parts = dict(pool.map(scan_row, [(name, float(s), z_axis) for s in s_axis], chunksize=1))
            null, scale, lapse = np.stack([parts[float(s)] for s in s_axis], axis=1)
            np.savez_compressed(saved, s=s_axis, z=z_axis, r=radius, null=null, scale=scale, lapse=lapse)
        requirement, deficit, window = screen(null, scale, lapse, args.step)
        screens[name] = requirement, deficit
        weight = deficit*area[None, None, :]*args.z_step
        per_sigma = weight.sum(axis=(1, 2))
        where = np.unravel_index(np.argmax(requirement), requirement.shape)
        deepest = np.unravel_index(np.argmax(deficit), deficit.shape)
        positive = requirement > 0
        weighted = np.sort(np.log10(requirement[positive]))
        order = np.argsort(np.log10(requirement[positive]))
        cumulative = np.cumsum(weight[positive][order])/weight[positive].sum()
        summary[name] = {
            "scan_points": int(null.size), "static_lapse_max": float(lapse.max()),
            "peak_deficit": float(deficit.max()), "peak_deficit_at": [float(s_axis[deepest[0]]),
                                                                      float(z_axis[deepest[1]]),
                                                                      float(radius[deepest[2]])],
            "peak_deficit_volume_per_sigma": float(per_sigma.max()),
            "screen_requirement_max": float(requirement.max()),
            "screen_requirement_at": [float(s_axis[where[0]]), float(z_axis[where[1]]), float(radius[where[2]])],
            "screen_deficit_at_max": float(deficit[where]), "screen_tau_at_max": float(window[where]),
            "screen_requirement_deficit_weighted_median": float(10**weighted[np.searchsorted(cumulative, .5)]),
            "screen_requirement_deficit_weighted_p90": float(10**weighted[np.searchsorted(cumulative, .9)]),
            "min_scale_where_deficit_above_1pct": float(np.asarray(scale, dtype=float)[deficit > .01*deficit.max()].min()),
            "deficit_weighted_median_tau": float(np.sort(window[positive])[
                np.searchsorted(np.cumsum(weight[positive][np.argsort(window[positive])])/weight[positive].sum(),
                                .5)]),
        }
        print(name, json.dumps(summary[name]), round(time.time()-started, 1), flush=True)

    name = SELECTED
    design = staging.design_for(name)
    radius, _ = radius_nodes(design)
    requirement, deficit = screens[name]
    launches = launch_rows(name, requirement, deficit, s_axis, z_axis, radius)
    with ProcessPoolExecutor(args.workers) as pool:
        targeted = pd.DataFrame(list(pool.map(targeted_row, [(name, row["z"], row["r"], row["s"])
                                                             for row in launches["requirement"]])))
    targeted.insert(1, "zone", [row["zone"] for row in launches["requirement"]])
    targeted.insert(2, "demand", [row["demand"] for row in launches["requirement"]])
    targeted.insert(3, "screen_requirement", [row["requirement"] for row in launches["requirement"]])
    targeted.to_csv(args.output/"targeted_requirements.csv", index=False)
    main_rows = targeted[targeted.demand == "main"]
    governing = main_rows.loc[main_rows[f"requirement_{REFERENCE_FRACTION:g}"].idxmax()]
    print(targeted.sort_values(f"requirement_{REFERENCE_FRACTION:g}", ascending=False).head(12).to_string(),
          round(time.time()-started, 1), flush=True)

    tasks = ray_tasks(name, launches["deficit"], launches["requirement"])
    with ProcessPoolExecutor(args.workers) as pool:
        results = list(pool.map(ray_row, tasks))
    rays = pd.DataFrame([row for row, _ in results])
    rays.to_csv(args.output/"null_rays.csv", index=False)
    np.savez_compressed(args.scratch/"null_rays.npz", **{f"{row['label']}__{key}": value for row, path in results
                                                         for key, value in path.items()})
    witness = next(((row, path) for row, path in results if row["label"] == "radial_s+0.0"), None)
    print(rays.to_string(), round(time.time()-started, 1), flush=True)

    peak = summary[name]["peak_deficit"]
    casimir = casimir_table(peak)
    casimir.to_csv(args.output/"casimir_cavities.csv", index=False)
    fields = []
    for (fraction, demand) in [(f, d) for f in FRACTIONS for d in ("main", "with tails")]:
        pool_rows = main_rows if demand == "main" else targeted
        q = float(pool_rows[f"requirement_{fraction:g}"].max())
        for label, length in UNIT_LENGTHS.items():
            fields.append({"fraction": fraction, "demand": demand, "unit_length": label, "unit_length_m": length,
                           "requirement": q, "fields": ss.fields_required(q, length),
                           "species_length_over_unit": math.sqrt(q),
                           "species_length_m": math.sqrt(q)*length,
                           "largest_unit_for_gravity_tests_m": GRAVITY_TEST_LENGTH/math.sqrt(q)})
    fields = pd.DataFrame(fields)
    fields.to_csv(args.output/"field_requirements.csv", index=False)
    figures(args.output, radius, z_axis, deficit, requirement, witness)
    rows = []
    for key in ("deficit", "requirement"):
        for row in launches[key]:
            rows.append({"kind": key, **{k: v for k, v in row.items() if k != "direction"},
                         "direction_z": row["direction"][0], "direction_r": row["direction"][1],
                         "direction_phi": row["direction"][2]})
    pd.DataFrame(rows).to_csv(args.output/"launch_nodes.csv", index=False)
    manifest = {
        "completed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": round(time.time()-started, 1), "workers": args.workers, "step": args.step,
        "z_step": args.z_step,
        "sigma_range": list(SIGMA_RANGE), "z_max": Z_MAX, "per_panel": PER_PANEL, "deficit_floor": DEFICIT_FLOOR,
        "fractions": FRACTIONS, "reference_fraction": REFERENCE_FRACTION, "window_samples": WINDOW_SAMPLES,
        "ray_step": RAY_STEP, "history_step": HISTORY_STEP, "main_demand_fraction": MAIN_DEMAND,
        "unit_lengths_m": UNIT_LENGTHS, "gravity_test_length_m": GRAVITY_TEST_LENGTH,
        "summary": summary,
        "governing": {k: (float(v) if isinstance(v, (int, float, np.floating)) else v) for k, v in governing.items()},
        "rays": {"count": len(rays), "with_bound_states": int((rays.bound_states > 0).sum()),
                 "negative_null_integral": int((rays.null_integral < 0).sum()),
                 "max_end_potential": float(rays.end_potentials.max()),
                 "max_null_drift": float(rays.max_null_drift.max())},
        "software_sha256": {path: sha256_file(ROOT/"toolkit/adm_harness_cli"/path) for path in (
            "adm_harness/source_scaling.py", "adm_harness/axial_track.py", "adm_harness/axial_einstein_generated.py",
            "adm_harness/constant_radius_track.py", "scripts/run_lapse_staging_pass.py",
            "scripts/run_source_scaling_test.py")},
    }
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=1, default=str)+"\n")
    print(fields.to_string(), casimir.to_string(), json.dumps(manifest["rays"]), sep="\n")


if __name__ == "__main__":
    main()
