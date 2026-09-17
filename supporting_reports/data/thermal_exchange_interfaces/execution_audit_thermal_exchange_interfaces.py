#!/usr/bin/env python3
"""Audit paired thermal four-vectors, frozen relays, and moving collectors."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import multiprocessing
import platform
import shutil
import subprocess

import numpy as np

from adm_harness.thermal_exchange_interfaces import (
    matched_axial_relay, paired_absorption_exchange, passive_absorption_gain,
    radial_collector, three_axis_average,
)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = ROOT/"supporting_reports/data/thermal_exchange_interfaces"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relay_case(task):
    delay, output = task
    time = np.linspace(0., 60., 6001)
    heat = np.where(time < 40, .5*np.sin(np.pi*np.minimum(time, 40)/40)**2, 0.)
    heat[0] = heat[-1] = 0.
    spin = .565+.265*np.cos(time/7)
    result = matched_axial_relay(time, heat, spin, delay)
    average = three_axis_average(result["flight_tensor"])
    balance = float(abs(result["four_momentum_balance_error"]).max())
    counterstream = float(abs(result["bath_arrival_stream_power"][:, 0]
                             -result["bath_arrival_stream_power"][:, 1]).max())
    isotropy = max(float(abs(average[axis, axis]-result["flight_energy"]/3).max())
                   for axis in (1, 2, 3))
    ceiling = delay*float(result["source_total_power"].max())
    if max(balance, counterstream, isotropy) > 2e-12 or result["flight_energy"].max() > ceiling+2e-12:
        raise ValueError(f"Thermal relay verification failed: {delay}")
    name = f"relay_delay_{delay:g}"
    np.savez_compressed(Path(output)/(name+".npz"), **result, three_axis_flight_tensor=average,
        rest_heat_per_rotor=heat, spin=spin)
    return dict(name=name, delay=delay, maximum_four_momentum_balance_error=balance,
        maximum_local_bath_counterstream_imbalance=counterstream,
        maximum_three_axis_stress_error=isotropy,
        maximum_flight_energy=float(result["flight_energy"].max()), flight_energy_ceiling=ceiling,
        final_flight_energy=float(result["flight_energy"][-1]),
        maximum_source_guide_force=float(abs(result["source_guide_four_force"][:, :, 1:]).max()),
        maximum_central_guide_force=float(abs(result["central_guide_four_force"][:, 1:]).max()),
        maximum_destination_guide_force=float(abs(result["destination_guide_four_force"][:, :, 1:]).max()))


def local_ports(output, vmax):
    q, spin, alpha, radial = (a.ravel() for a in np.meshgrid(
        [-1., -.2, 0., .2, 1.], [.3, .5, np.sqrt(.69)], [0., .62e-6, .001, .1],
        [-vmax, 0., vmax], indexing="ij"))
    result = paired_absorption_exchange(q, spin, alpha, radial)
    errors = []
    for index, sign in enumerate((1., -1.)):
        force = result["cold_four_force"][index]
        errors.append(force[0]-radial*force[1]-sign*spin*np.sqrt(1-radial**2)*force[2])
    cold_error = float(np.max(np.abs(errors)))
    energy_error = float(abs(result["incoming"]-result["outgoing"]-q).max())
    momentum_error = float(abs(result["paired_bath_four_force"][2:]).max())
    if max(cold_error, energy_error, momentum_error) > 2e-12:
        raise ValueError("Paired thermal source verification failed")
    np.savez_compressed(output/"paired_port_four_vectors.npz", q=q, spin=spin,
        absorption=alpha, radial_speed=radial, **result)
    return dict(cases=len(q), maximum_cold_force_orthogonality_error=cold_error,
        maximum_optical_energy_error=energy_error, maximum_pair_tangential_momentum=momentum_error,
        passive_gain_at_0_62_ppm_floor_0_3=float(passive_absorption_gain(.62e-6, .3)),
        passive_over_directed_worst_gain_ratio=1/(1-.3**2))


def collectors(output, vmax):
    velocity, incoming_radial, sign = (a.ravel() for a in np.meshgrid(
        np.linspace(-vmax, vmax, 21), np.linspace(-vmax, vmax, 21), [-1., 1.], indexing="ij"))
    incoming = np.stack((incoming_radial, np.zeros_like(velocity), np.sqrt(1-incoming_radial**2)))
    result = radial_collector(1., velocity, incoming, sign)
    error = float(abs(result["rest_frame_work_error"]).max())
    if error > 2e-12:
        raise ValueError("Moving collector work verification failed")
    np.savez_compressed(output/"moving_collector_four_vectors.npz", radial_speed=velocity,
        incoming_direction=incoming, outgoing_sign=sign, **result)
    return dict(assigned_radial_speed_bound=vmax, cases=len(velocity),
        maximum_rest_frame_work_error=error,
        axial_incidence_energy_gain=1/(1-vmax*vmax),
        axial_incidence_extra_work_over_incident_energy=vmax*vmax/(1-vmax*vmax),
        inherited_radial_cosine_extra_work_bound=2*vmax*vmax/(1-vmax*vmax),
        arbitrary_incoming_direction_extra_work_bound=vmax/(1-vmax))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--maximum-radial-speed", type=float, default=.00905)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4 or not 0 <= args.maximum_radial_speed < 1:
        parser.error("one to four workers and a subluminal radial-speed bound required")
    args.output.mkdir(parents=True, exist_ok=True)
    ports = local_ports(args.output, args.maximum_radial_speed)
    collector = collectors(args.output, args.maximum_radial_speed)
    with ProcessPoolExecutor(max_workers=args.workers,
            mp_context=multiprocessing.get_context("spawn")) as pool:
        relays = list(pool.map(relay_case, [(d, str(args.output)) for d in (.01, .1, 1., 4.)]))
    summary = dict(created_utc=datetime.now(timezone.utc).isoformat(), workers=args.workers,
        base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        runtime=dict(python=platform.python_version(), numpy=np.__version__),
        four_vector_coordinates=["energy", "radial", "tangential", "axial"],
        ports=ports, moving_collectors=collector, frozen_relays=relays,
        paired_source_and_cold_recoil_verified=True,
        matched_frozen_routes_and_each_local_bath_verified=True,
        photon_flight_energy_and_tensor_included=True,
        source_central_and_destination_guide_impulses_included=True,
        instantaneous_moving_collector_work_included=True,
        constant_delay_moving_geometry_constructed=False,
        moving_guide_work_closed_into_rotor_history=False,
        guide_host_inventory_and_stress_constitutive_law_constructed=False,
        finite_temperature_reciprocal_heat_fluxes_constructed=False,
        physical_thermal_material_interface_constructed=False)
    (args.output/"summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n")
    sources = [Path(__file__).resolve(),
        ROOT/"toolkit/adm_harness_cli/adm_harness/thermal_exchange_interfaces.py",
        ROOT/"toolkit/adm_harness_cli/tests/test_thermal_exchange_interfaces.py"]
    for path in sources:
        shutil.copyfile(path, args.output/("execution_"+path.name))
    manifest = dict(runtime_sha256={str(path.relative_to(ROOT)): sha256(path) for path in sources},
        output_sha256={path.name: sha256(path) for path in sorted(args.output.iterdir())
                       if path.is_file() and path.name != "manifest.json"})
    (args.output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
