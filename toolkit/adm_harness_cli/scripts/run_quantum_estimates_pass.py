#!/usr/bin/env python3
"""Quantum-field magnitudes on the trimmed compartment carry: trace anomaly, rear horizon, mode mixing; emit data only.

The trace anomaly fixes the trace of the renormalized stress of a conformal field from the local curvature alone,
in any state: (c W^2 - a E)/(16 pi^2) in units of hbar c/L^4, with the Weyl square W^2 and the Euler density E,
plus a Box R term that a finite R^2 counterterm shifts. The coefficients (a, c) are (1/360, 1/120) for a
conformally coupled scalar, (11/720, 1/40) for a two-component Weyl fermion and (31/180, 1/10) for the Maxwell
field; on a Ricci-flat background the scalar value reduces to the Kretschmann scalar over 2880 pi^2. The first stage
evaluates the three traces across the pattern and the cone at mid-acceleration, at the two moments the cone is half
extended, at mid-lane and at mid-deceleration, beside the demanded classical stress from the same curvature.

The second stage locates the rear horizon of the trimmed design, where the pattern's lapse rises through the
carry speed, and records its surface gravity, the Hawking-like temperature kappa/2 pi of the pattern's Killing time,
and the temperature kappa/(2 pi N) that passengers in the compartment read, with N the Killing norm there.

The third stage measures mode mixing in the region the pattern outruns. In the pattern's frame, positive- and
negative-norm field modes of one Killing frequency meet in the exterior, and scattering off the cone can convert
one into the other, which is pair creation. A complex packet of positive normal frequency arrives from ahead and
scatters off the cone. Once it has left the structure, a Fourier-Hankel transform of the field in flat space splits
it into positive- and negative-frequency parts. The negative part's share of the Klein-Gordon norm is the mixing
coefficient. A control places each packet in flat space astride the window's edge, with no evolution, and
records the negative share that the edge alone produces.

A last step restates the results in SI units at rail length scales L from 1 m to 1 km: stress in hbar c/L^4 and
c^4/(G L^2), temperature in hbar c/(k_B L). Narrative interpretation is maintained manually in supporting_reports.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import math
from pathlib import Path
import sys
import time
from types import SimpleNamespace

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.special import j0

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_front_surface_pass as front_pass
import run_geometry_closure_pass as closure
from adm_harness import front_surface as fs
from adm_harness import scalar_wave as sw
from adm_harness import source_scaling as ss
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
SIGMAS = (.75, 3.75, 6.75)
SPEEDS = (2.1, 10.)
SIGN = np.array([-1., 1., 1., 1.])
ANOMALY_FIELDS = {"scalar": (1/360, 1/120), "weyl_fermion": (11/720, 1/40), "maxwell": (31/180, 1/10)}
CORE_STEP, CONE_STEP = .125, .25
RAIL_SCALES_M = (1., 10., 100., 1000.)
HBAR, LIGHT, NEWTON, BOLTZMANN = 1.054571817e-34, 299792458., 6.67430e-11, 1.380649e-23
STEFAN_BOLTZMANN = 5.670374419e-8
MIXING_PACKETS = {
    "axis_wavelength_0p5": dict(r0=0., width_zeta=.75, width_r=.5, wavelength=.5),
    "axis_wavelength_1": dict(r0=0., width_zeta=1., width_r=.5, wavelength=1.),
    "axis_wavelength_2": dict(r0=0., width_zeta=1.5, width_r=1., wavelength=2.),
    "ring_wavelength_1": dict(r0=2., width_zeta=1., width_r=.5, wavelength=1.),
}
MIXING_GRID = dict(step=.04, back=-26., ahead=22., radius=14., start=12., end=15.,
                   layers=dict(back=3., front=2., outer=2., rate=6.))
WINDOW_CONTROL_DEPTHS = (4., 2., 1., 0., -1.)


# Trace anomaly

def invariants(fields):
    """Kretschmann scalar, Weyl square, Euler density and the demanded stress G/8 pi (normal frame) at each radius."""
    g, dg, ddg = ss.metric_jets(fields)
    frame = ss.frame_riemann(ss.riemann(g, dg, ddg), ss.normal_tetrad(fields))
    raise_ = np.einsum("a,b,c,d->abcd", SIGN, SIGN, SIGN, SIGN)
    kretschmann = np.einsum("nabcd,abcd->n", frame**2, raise_)
    ricci = np.einsum("a,nabad->nbd", SIGN, frame)
    scalar = np.einsum("b,nbb->n", SIGN, ricci)
    ricci2 = np.einsum("a,b,nab->n", SIGN, SIGN, ricci**2)
    weyl2 = kretschmann-2*ricci2+scalar**2/3
    euler = kretschmann-4*ricci2+scalar**2
    stress = (ricci-.5*np.diag(SIGN)[None]*scalar[:, None, None])/(8*math.pi)
    return kretschmann, weyl2, euler, stress


def anomaly_trace(weyl2, euler, field):
    """Trace anomaly of one conformal field, in units of hbar c/L^4 for curvature in units of 1/L^2."""
    a, c = ANOMALY_FIELDS[field]
    return (c*weyl2-a*euler)/(16*math.pi**2)


def sample_times(service, cone):
    """Mid-acceleration, mid-lane and mid-deceleration, and the two moments the cone is half extended."""
    half = sum(cone.extend)/2
    _, _, _, _, _, depart, accel_time, decel, decel_time = service.path
    rise = brentq(lambda s: service.carry_speed(s)-half, depart, depart+accel_time)
    fall = brentq(lambda s: service.carry_speed(s)-half, decel, decel+decel_time)
    return tuple(sorted((*SIGMAS, round(rise, 6), round(fall, 6))))


def anomaly_offsets(service, cone):
    """Offsets along the track and their trapezoid lengths: finer across the pattern, coarser along the cone."""
    core = np.arange(-service.extent-1., service.extent+1., CORE_STEP)
    ahead = np.arange(service.extent+1., cone.tip(service)+2.+CONE_STEP/2, CONE_STEP)
    offsets = np.round(np.concatenate([core, ahead]), 10)
    edges = np.concatenate([[offsets[0]], (offsets[1:]+offsets[:-1])/2, [offsets[-1]]])
    return offsets, np.diff(edges)


def anomaly_row(task):
    speed, s, offsets, lengths = task
    service, design, cone = closure.build_spec(closure.TRIM_SCALED, speed)
    radius, area = front_pass.radial_nodes(service, design, cone)
    centre = service.packet_position(s)
    rows = []
    for offset, length in zip(offsets, lengths):
        f = fs.fields(service, design, cone, s, centre+float(offset), radius)
        f["C"], f["C_r"], f["C_rr"] = radius.copy(), np.ones_like(radius), np.zeros_like(radius)
        kretschmann, weyl2, euler, stress = invariants(f)
        energy = np.abs(stress[:, 0, 0])
        component = np.abs(stress).max(axis=(1, 2))
        row = {"speed": speed, "s": s, "offset": float(offset), "length": float(length),
               "max_kretschmann": float(kretschmann.max()), "max_abs_weyl2": float(np.abs(weyl2).max()),
               "max_abs_euler": float(np.abs(euler).max()), "max_demand_energy": float(energy.max()),
               "max_demand_component": float(component.max()), "area_demand_component": float(np.sum(area*component))}
        inside = radius < service.hole_radius[0] if abs(offset) <= service.half_width else np.zeros_like(radius, bool)
        for field in ANOMALY_FIELDS:
            trace = anomaly_trace(weyl2, euler, field)
            i = int(np.argmax(np.abs(trace)))
            row[f"max_abs_trace_{field}"] = float(abs(trace[i]))
            row[f"r_at_max_{field}"] = float(radius[i])
            row[f"area_abs_trace_{field}"] = float(np.sum(area*np.abs(trace)))
            row[f"compartment_abs_trace_{field}"] = float(np.abs(trace[inside]).max()) if inside.any() else math.nan
        rows.append(row)
    return rows


def anomaly_summary(frame):
    """Per speed and sigma: peaks over the meridian plane and volume integrals over the pattern and the cone."""
    out = []
    for (speed, s), part in frame.groupby(["speed", "s"]):
        row = {"speed": speed, "s": s, "max_kretschmann": part.max_kretschmann.max(),
               "max_demand_energy": part.max_demand_energy.max(), "max_demand_component": part.max_demand_component.max(),
               "demand_component_content": float(np.sum(part.area_demand_component*part.length))}
        for field in ANOMALY_FIELDS:
            row[f"compartment_abs_trace_{field}"] = part[f"compartment_abs_trace_{field}"].max()
            i = part[f"max_abs_trace_{field}"].idxmax()
            row[f"max_abs_trace_{field}"] = part.loc[i, f"max_abs_trace_{field}"]
            row[f"offset_at_max_{field}"] = part.loc[i, "offset"]
            row[f"r_at_max_{field}"] = part.loc[i, f"r_at_max_{field}"]
            row[f"trace_content_{field}"] = float(np.sum(part[f"area_abs_trace_{field}"]*part.length))
        out.append(row)
    return pd.DataFrame(out)


# Rear horizon

def compartment_killing_norm(service, design, cone, s):
    """Norm sqrt(alpha^2 - b^2) of the pattern's Killing time at the packet's centre, b = beta + v."""
    c = service.packet_position(s)
    log_alpha, beta = fs.log_lapse_and_shift(service, design, cone, s, np.array([c]), np.array([0.]))
    b = beta[0]+service.carry_speed(s)
    return math.sqrt(math.exp(2*log_alpha[0])-b*b)


def rear_horizon(speed):
    service, design, cone = closure.build_spec(closure.TRIM_SCALED, speed)
    s = 3.75
    c = service.packet_position(s)
    v = service.carry_speed(s)
    norm = compartment_killing_norm(service, design, cone, s)
    rows = []
    for r in (0., 2., 4., 6., 8., 8.5, 9., 9.5, 10., 10.5, 11.):
        def a(x):
            return float(np.exp(fs.log_lapse_and_shift(service, design, cone, s, np.array([c+x]), np.array([r]))[0][0]))
        grid = np.linspace(-service.extent-.5, -service.fall_start+.5, 400)
        values = np.array([a(x)-v for x in grid])
        hits = np.flatnonzero(np.sign(values[:-1]) != np.sign(values[1:]))
        if not len(hits):
            continue
        x = brentq(lambda y: a(y)-v, grid[hits[0]], grid[hits[0]+1], xtol=1e-12)
        h = 1e-4
        kappa = (a(x+h)-a(x-h))/(2*h)
        gr = (float(np.exp(fs.log_lapse_and_shift(service, design, cone, s, np.array([c+x]), np.array([r+h]))[0][0]))
              - float(np.exp(fs.log_lapse_and_shift(service, design, cone, s, np.array([c+x]),
                                                    np.array([abs(r-h)]))[0][0])))/(2*h) if r > 0 else 0.
        rows.append({"speed": speed, "r": r, "offset": x, "kappa": kappa, "transverse_over_along": abs(gr)/abs(kappa),
                     "temperature": kappa/(2*math.pi), "compartment_killing_norm": norm,
                     "passenger_temperature": kappa/(2*math.pi*norm)})
    return rows


# Mode mixing

def mixing_background(speed):
    service, design, cone = closure.build_spec(closure.TRIM_SCALED, speed)
    s = 3.75
    c = service.packet_position(s)
    v = service.carry_speed(s)
    tip = cone.tip(service)
    surface = brentq(lambda x: float(np.exp(fs.log_lapse_and_shift(service, design, cone, s, np.array([c+x]),
                                                                   np.array([0.]))[0][0]))-v, tip-20., tip)
    step = MIXING_GRID["step"]
    zeta = surface+np.arange(MIXING_GRID["back"], MIXING_GRID["ahead"], step)+step/2
    r = np.arange(0., MIXING_GRID["radius"], step)+step/2
    zz, rr = np.meshgrid(zeta, r, indexing="ij")
    log_alpha, beta = fs.log_lapse_and_shift(service, design, cone, s, c+zz.ravel(), rr.ravel())
    alpha = np.exp(log_alpha).reshape(zz.shape)
    b = (beta+v).reshape(zz.shape)
    layers = MIXING_GRID["layers"]
    damping = sw.damping_layer(zeta, r, back=layers["back"], front=layers["front"], outer=layers["outer"],
                               rate=layers["rate"])
    return zeta, r, alpha, b, damping, surface


RADIAL_WAVENUMBERS = np.linspace(0., 40., 3001)


def hankel_forward(values, r):
    """Order-zero Hankel transform over the last axis, int f J0(k r) r dr on cell centres, to RADIAL_WAVENUMBERS.

    The midpoint rule's axis end contributes -(dr^2/24) g'(0) + (7 dr^4/5760) g'''(0) for the integrand
    g = r f J0(k r), with g'(0) = f(0) and g'''(0) = 6 (f2 - f(0) k^2/4) for f = f(0) + f2 r^2 near the axis; both
    terms are removed, with f(0) and f2 fitted to the first two centres.
    """
    dr = r[1]-r[0]
    k = RADIAL_WAVENUMBERS
    kernel = j0(np.outer(k, r))*r[None, :]*dr
    first, second = np.asarray(values[..., 0])[..., None], np.asarray(values[..., 1])[..., None]
    curvature = (second-first)/(2*dr*dr)
    axis_value = first-curvature*dr*dr/4
    return values@kernel.T-(dr*dr/24)*axis_value+(7*dr**4/960)*(curvature-axis_value*k*k/4)


def split_frequencies(wave_r, wave_i, zeta, r, window):
    """Positive- and negative-frequency Klein-Gordon norms of the complex field, weighted by the flat-space window."""
    phi = (wave_r.phi+1j*wave_i.phi)*window
    Pi = (wave_r.Pi+1j*wave_i.Pi)*window
    dz = zeta[1]-zeta[0]
    kz = 2*math.pi*np.fft.fftfreq(len(zeta), dz)
    kr = RADIAL_WAVENUMBERS
    phi_k = hankel_forward(np.fft.fft(phi, axis=0), r)
    Pi_k = hankel_forward(np.fft.fft(Pi, axis=0), r)
    k = np.hypot(kz[:, None], kr[None, :])
    live = k > 0
    safe = np.where(live, k, 1.)
    plus = (phi_k+1j*Pi_k/safe)/2
    minus = (phi_k-1j*Pi_k/safe)/2
    measure = kr[None, :]*np.gradient(kr)[None, :]
    n_plus = float(np.sum((2*safe*np.abs(plus)**2*measure)[live]))
    n_minus = float(np.sum((2*safe*np.abs(minus)**2*measure)[live]))
    return n_plus, n_minus


def positive_frequency_packet(zeta, r, centre, spec):
    """Complex packet built from flat-space modes of positive normal frequency: phi and Pi = -i omega phi.

    The envelope is Gaussian along the track about centre and Gaussian in r about r0 (mirrored, so the profile is
    even), with carrier wavelength spec["wavelength"] along the track; omega = sqrt(kz^2 + kr^2) for each mode.
    """
    dz = zeta[1]-zeta[0]
    radial = np.exp(-(r-spec["r0"])**2/(2*spec["width_r"]**2))
    if spec["r0"]:
        radial = radial+np.exp(-(r+spec["r0"])**2/(2*spec["width_r"]**2))
    kr = RADIAL_WAVENUMBERS
    radial_k = hankel_forward(radial, r)
    carrier = 2*math.pi/spec["wavelength"]
    along_k = np.fft.fft(np.exp(-(zeta-centre)**2/(2*spec["width_zeta"]**2)+1j*carrier*(zeta-centre)))
    kz = 2*math.pi*np.fft.fftfreq(len(zeta), dz)
    omega = np.hypot(kz[:, None], kr[None, :])
    spectrum = along_k[:, None]*radial_k[None, :]
    inverse = j0(np.outer(kr, r))*(kr*np.gradient(kr))[:, None]
    phi = np.fft.ifft(spectrum, axis=0)@inverse
    Pi = np.fft.ifft(-1j*omega*spectrum, axis=0)@inverse
    return phi, Pi


def flat_window(alpha, damping, step):
    """Smooth weight that is one deep in flat space and falls to zero within one unit of any structure."""
    from scipy.ndimage import binary_erosion, gaussian_filter
    flat = (np.abs(np.log(alpha)) < 1e-6) & (damping == 0)
    cells = int(round(1./step))
    mirrored = np.concatenate([flat[:, ::-1], flat], axis=1)
    core = binary_erosion(mirrored, iterations=cells, border_value=0)[:, flat.shape[1]:]
    return gaussian_filter(core.astype(float), sigma=cells/4)*flat, flat


def norm_density(wave_r, wave_i):
    return 2*(wave_i.phi*wave_r.Pi-wave_r.phi*wave_i.Pi)


def mixing_run(task):
    """A complex packet of positive normal frequency scattered off the cone; frequency split of the outgoing field."""
    speed, name = task
    spec = MIXING_PACKETS[name]
    zeta, r, alpha, b, damping, surface = mixing_background(speed)
    waves = [sw.AxisymmetricWave(zeta, r, alpha, b, damping, dissipation=.05) for _ in range(2)]
    centre = surface+MIXING_GRID["start"]
    phi, Pi = positive_frequency_packet(zeta, r, centre, spec)
    waves[0].phi, waves[1].phi = phi.real.copy(), phi.imag.copy()
    waves[0].Pi, waves[1].Pi = Pi.real.copy(), Pi.imag.copy()
    window, flat = flat_window(alpha, damping, zeta[1]-zeta[0])
    start_plus, start_minus = split_frequencies(*waves, zeta, r, window)
    volume = waves[0].cell_volume()
    start_norm = float(np.sum(norm_density(*waves)*volume))
    every = math.ceil(1./waves[0].stable_step(.45))
    dt = 1./every
    rows = []
    for step in range(1, int(round(MIXING_GRID["end"]))*every+1):
        for wave in waves:
            wave.step(dt)
        if step % every == 0:
            density = norm_density(*waves)*volume
            n_plus, n_minus = split_frequencies(*waves, zeta, r, window)
            rows.append({"speed": speed, "packet": name, "t": step//every,
                         "norm_total": float(np.sum(density[damping == 0]))/start_norm,
                         "norm_in_flat": float(np.sum(density[flat]))/start_norm,
                         "windowed_norm": float(np.sum(density*window))/start_norm,
                         "positive_part": n_plus, "negative_part": n_minus})
            print(f"mixing {name} t={step//every} windowed norm {rows[-1]['windowed_norm']:.3f} "
                  f"negative share {n_minus/(n_plus+n_minus):.2e}", flush=True)
    frame = pd.DataFrame(rows)
    frame["mixing_share"] = frame.negative_part/(frame.positive_part+frame.negative_part)
    return {"speed": speed, "packet": name, "start_positive": start_plus, "start_negative": start_minus,
            "start_negative_share": start_minus/(start_plus+start_minus), "start_norm": start_norm}, frame


def window_control(task):
    """Negative-frequency share that the window's edge alone gives a flat-space packet placed astride it.

    Each packet of positive normal frequency is centred at depths along the axis measured from the window's
    half contour ahead of the tip, positive into flat space, with no evolution.
    """
    speed, name = task
    zeta, r, alpha, b, damping, surface = mixing_background(speed)
    window, _ = flat_window(alpha, damping, zeta[1]-zeta[0])
    edge = zeta[(zeta > surface) & (window[:, 0] > .5)][0]
    rows = []
    for depth in WINDOW_CONTROL_DEPTHS:
        phi, Pi = positive_frequency_packet(zeta, r, edge+depth, MIXING_PACKETS[name])
        real, imag = SimpleNamespace(phi=phi.real, Pi=Pi.real), SimpleNamespace(phi=phi.imag, Pi=Pi.imag)
        plus, minus = split_frequencies(real, imag, zeta, r, window)
        density = norm_density(real, imag)*r[None, :]
        rows.append({"speed": speed, "packet": name, "depth": depth, "edge_past_surface": float(edge-surface),
                     "windowed_norm": float(np.sum(density*window)/np.sum(density)),
                     "negative_share": minus/(plus+minus)})
    return rows


# SI units

def physical_units(output):
    """Peak traces, demanded stress, contents and the rear temperatures in SI units at each rail scale."""
    summary = pd.read_csv(output/"trace_anomaly_summary.csv")
    rear = pd.read_csv(output/"rear_horizon.csv")
    rows = []
    for length in RAIL_SCALES_M:
        quantum_density = HBAR*LIGHT/length**4
        classical_density = LIGHT**4/(NEWTON*length**2)
        temperature_unit = HBAR*LIGHT/(BOLTZMANN*length)
        for speed, part in summary.groupby("speed"):
            axis = rear[(rear.speed == speed) & (rear.r == 0.)].iloc[0]
            passenger = axis.passenger_temperature*temperature_unit
            row = {"rail_scale_m": length, "speed": speed,
                   "demand_stress_peak_Pa": part.max_demand_component.max()*classical_density,
                   "demand_stress_content_J": part.demand_component_content.max()*classical_density*length**3,
                   "rear_kappa_axis": axis.kappa, "passenger_temperature_K": passenger,
                   "blackbody_flux_W_m2": STEFAN_BOLTZMANN*passenger**4,
                   "mixing_power_unit_W": HBAR*LIGHT**2/length**2}
            for field in ANOMALY_FIELDS:
                peak = part[f"max_abs_trace_{field}"].max()*quantum_density
                row[f"trace_peak_{field}_J_m3"] = peak
                row[f"trace_content_{field}_J"] = part[f"trace_content_{field}"].max()*quantum_density*length**3
                row[f"peak_ratio_{field}"] = peak/row["demand_stress_peak_Pa"]
            rows.append(row)
    frame = pd.DataFrame(rows)
    frame.to_csv(output/"physical_units.csv", index=False)
    return frame


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--output", type=Path, default=ROOT/"supporting_reports/data/quantum_estimates_pass")
    parser.add_argument("--stages", default="anomaly,rear,mixing,control,physical")
    args = parser.parse_args()
    stages = set(args.stages.split(","))
    started = time.time()
    args.output.mkdir(parents=True, exist_ok=True)
    record, times = {}, {}
    pd.set_option("display.width", 250)
    with ProcessPoolExecutor(args.workers) as pool:
        if "anomaly" in stages:
            tasks = []
            for speed in SPEEDS:
                service, _, cone = closure.build_spec(closure.TRIM_SCALED, speed)
                offsets, lengths = anomaly_offsets(service, cone)
                chunks = math.ceil(len(offsets)/40)
                times[speed] = sample_times(service, cone)
                tasks += [(speed, s, offsets[i::chunks], lengths[i::chunks]) for s in times[speed]
                          for i in range(chunks)]
            frame = pd.DataFrame([r for chunk in pool.map(anomaly_row, tasks) for r in chunk])
            frame = frame.sort_values(["speed", "s", "offset"])
            frame.to_csv(args.output/"trace_anomaly.csv", index=False)
            summary = anomaly_summary(frame)
            summary.to_csv(args.output/"trace_anomaly_summary.csv", index=False)
            record["anomaly"] = summary.to_dict("records")
            print(summary.T.to_string(), round(time.time()-started, 1), flush=True)
        if "rear" in stages:
            rows = [r for speed in SPEEDS for r in rear_horizon(speed)]
            pd.DataFrame(rows).to_csv(args.output/"rear_horizon.csv", index=False)
            record["rear"] = rows
            print(pd.DataFrame(rows).to_string(index=False), flush=True)
        if "control" in stages:
            rows = [r for chunk in pool.map(window_control, [(2.1, name) for name in MIXING_PACKETS]) for r in chunk]
            pd.DataFrame(rows).to_csv(args.output/"mixing_window_control.csv", index=False)
            record["control"] = rows
            print(pd.DataFrame(rows).to_string(index=False), flush=True)
        if "mixing" in stages:
            starts, histories = [], []
            futures = [pool.submit(mixing_run, (2.1, name)) for name in MIXING_PACKETS]
            for future in as_completed(futures):
                start, history = future.result()
                starts.append(start)
                histories.append(history)
                pd.DataFrame(starts).to_csv(args.output/"mixing_start.csv", index=False)
                pd.concat(histories).to_csv(args.output/"mixing_history.csv", index=False)
                print(f"mixing {start['packet']} done at {round(time.time()-started, 1)} s", flush=True)
            print(pd.DataFrame(starts).to_string(index=False), pd.concat(histories).to_string(index=False), flush=True)
    if "physical" in stages:
        physical = physical_units(args.output)
        record["physical"] = physical.to_dict("records")
        print(physical.T.to_string(), flush=True)
    manifest_path = args.output/"manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    hashes = {path: sha256_file(ROOT/"toolkit/adm_harness_cli"/path) for path in (
        "adm_harness/scalar_wave.py", "adm_harness/front_surface.py", "adm_harness/source_scaling.py",
        "scripts/run_quantum_estimates_pass.py")}
    stage_hashes = manifest.get("stage_software_sha256") or {}
    if not stage_hashes and "software_sha256" in manifest:
        # A manifest from a run before per-stage records: its hashes belong to the stages that run produced.
        stage_hashes = {stage: manifest["software_sha256"] for stage in ("anomaly", "rear", "mixing", "physical")}
    stage_hashes.update({stage: hashes for stage in stages})
    if times:
        manifest["sample_times"] = {str(speed): value for speed, value in times.items()}
    manifest.update({"sigmas": SIGMAS, "speeds": SPEEDS, "anomaly_fields": ANOMALY_FIELDS,
                     "anomaly_steps": {"core": CORE_STEP, "cone": CONE_STEP}, "rail_scales_m": RAIL_SCALES_M,
                     "mixing_packets": MIXING_PACKETS, "mixing_grid": MIXING_GRID,
                     "window_control_depths": WINDOW_CONTROL_DEPTHS, "trim": closure.TRIM_SCALED, **record,
                     f"elapsed_{'_'.join(sorted(stages))}": round(time.time()-started, 1),
                     "software_sha256": hashes, "stage_software_sha256": stage_hashes})
    manifest_path.write_text(json.dumps(manifest, indent=1, default=str)+"\n")


if __name__ == "__main__":
    main()
