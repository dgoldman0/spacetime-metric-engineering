#!/usr/bin/env python3
"""Two checks on the conical front; emit data only.

The angle screen traces meridional light rays and unit-mass particles in a stationary model of the cone alone,
in the frame of a pattern moving at the carry speed. It records the energy that objects arriving from ahead keep
when they leave, for half-angles from 15 to 45 degrees, two layer widths and two tip roundings. The
long-carry check follows matter that sits inside the cone's volume when the cone extends at departure, through
carries whose lanes end at sigma = 18 and 36, to see where its kept energy levels off. Narrative interpretation is
maintained manually in supporting_reports.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import itertools
import json
import math
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_front_surface_pass as front_pass
from adm_harness import front_surface as fs
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
SPEED = 2.1
ANGLES = (15., 22., 30., 45.)
LAYERS = (2., 5.)
ROUNDINGS = (.5, 2.)
SCREEN_RADII = (.05, .2, .5, 1., 2., 4., 7., 10., 12.5)
BASE_RADIUS = 13.
INTERIOR_LOG_LAPSE = 1.5
H = 1e-5


def cone_log_lapse(p, zeta, r):
    """The stationary cone alone: log_lapse * step(d/layer), tip at zeta = 0, radius capped at the base."""
    radius = -np.logaddexp(math.tan(p["theta"])*zeta, -p["base"])
    depth = radius-(math.sqrt(r*r+p["eps"]**2)-p["eps"])
    return float(p["psi"]*fs.step(depth/p["layer"]))


def rates(t, y, p, mass):
    zeta, r, kz, kr = y
    a = math.exp(cone_log_lapse(p, zeta, abs(r)))
    a_z = (math.exp(cone_log_lapse(p, zeta+H, abs(r)))-math.exp(cone_log_lapse(p, zeta-H, abs(r))))/(2*H)
    a_r = (math.exp(cone_log_lapse(p, zeta, abs(r)+H))-math.exp(cone_log_lapse(p, zeta, abs(abs(r)-H))))/(2*H)
    a_r = a_r if r >= 0 else -a_r
    e = math.sqrt(mass+kz*kz+kr*kr)
    return [a*kz/e-SPEED, a*kr/e, -a_z*e, -a_r*e]


def screen(task):
    """Energy kept by forward light or matter at rest launched ahead of the stationary cone."""
    angle, layer, rounding, kind, r0 = task
    p = {"theta": math.radians(angle), "layer": layer, "eps": rounding, "base": BASE_RADIUS, "psi": INTERIOR_LOG_LAPSE}
    mass = 0. if kind == "light" else 1.
    k0 = (1., 0.) if kind == "light" else (0., 0.)
    leave = lambda t, y, *_: abs(y[1])-(BASE_RADIUS+layer+4.)
    leave.terminal = True
    past = lambda t, y, *_: y[0]+BASE_RADIUS/math.tan(p["theta"])+40.
    past.terminal = True
    sol = solve_ivp(rates, (0., 400.), [8., r0, *k0], args=(p, mass), method="DOP853", rtol=1e-9, atol=1e-11,
                    max_step=.05, events=(leave, past))
    kz, kr = sol.y[2, -1], sol.y[3, -1]
    status = "left sideways" if sol.t_events[0].size else ("passed" if sol.t_events[1].size else "held")
    return {"half_angle": angle, "layer": layer, "rounding": rounding, "kind": kind, "r0": r0,
            "kept_energy": math.sqrt(mass+kz*kz+kr*kr)/math.sqrt(mass+k0[0]**2), "status": status,
            "time": float(sol.t[-1]), "exit_angle_deg": math.degrees(math.atan2(abs(kr), kz))}


def long_carry(decel):
    """Matter at rest inside the cone's volume at departure, traced through a carry whose lane ends at decel."""
    z0 = np.array([7.75, 7.75, 7.75, 13.75, 13.75, 25.75, 25.75, 37.75])
    r0 = np.array([5., 8., 11., 8., 11., 5., 11., 8.])
    service, design, front = front_pass.build("cone", decel)
    y, peak, at = fs.trace_many(service, design, front, (front_pass.TRACE_START, decel+6.), z0, r0, np.zeros(8),
                                np.zeros(8), mass=1., ds=front_pass.TRACE_STEP)
    final = np.sqrt(1+y[2]**2+y[3]**2)
    return [{"decel": decel, "z0": float(z0[i]), "r0": float(r0[i]), "final_gamma": float(final[i]),
             "sigma_at_max": float(at[0, i])} for i in range(8)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/front_surface_pass")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    tasks = [(a, w, e, kind, r0) for a, w, e in itertools.product(ANGLES, LAYERS, ROUNDINGS)
             for kind in ("light", "matter") for r0 in SCREEN_RADII]
    with ProcessPoolExecutor(args.workers) as pool:
        rows = list(pool.map(screen, tasks, chunksize=4))
        carry = [r for chunk in pool.map(long_carry, (18., 36.)) for r in chunk]
    frame = pd.DataFrame(rows)
    frame.to_csv(args.output/"cone_angle_screen.csv", index=False)
    pd.DataFrame(carry).to_csv(args.output/"cone_inside_long_carry.csv", index=False)
    pd.set_option("display.width", 250)
    print(frame.pivot_table(index=["half_angle", "layer", "rounding", "kind"], columns="r0",
                            values="kept_energy").to_string(float_format=lambda x: f"{x:.3g}"))
    print(frame.groupby("status").size().to_string())
    print(pd.DataFrame(carry).pivot_table(index=["z0", "r0"], columns="decel", values="final_gamma").to_string())
    manifest = {"speed": SPEED, "angles": ANGLES, "layers": LAYERS, "roundings": ROUNDINGS, "radii": SCREEN_RADII,
                "base_radius": BASE_RADIUS, "interior_log_lapse": INTERIOR_LOG_LAPSE,
                "software_sha256": {path: sha256_file(ROOT/"toolkit/adm_harness_cli"/path) for path in (
                    "adm_harness/front_surface.py", "scripts/run_front_surface_pass.py",
                    "scripts/run_cone_front_checks.py")}}
    (args.output/"cone_checks_manifest.json").write_text(json.dumps(manifest, indent=1)+"\n")


if __name__ == "__main__":
    main()
