import math
from pathlib import Path
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))
import run_front_surface_pass as front_pass
import run_geometry_closure_pass as closure
import run_quantum_estimates_pass as quantum
from adm_harness import front_surface as fs


def test_scalar_anomaly_matches_the_riemann_and_ricci_form():
    """(W^2/120 - E/360)/16 pi^2 equals (K - Ric^2)/2880 pi^2, which is K/2880 pi^2 on Ricci-flat curvature."""
    rng = np.random.default_rng(3)
    kretschmann, ricci2, scalar = rng.normal(size=(3, 50))
    weyl2 = kretschmann-2*ricci2+scalar**2/3
    euler = kretschmann-4*ricci2+scalar**2
    expected = (kretschmann-ricci2)/(2880*math.pi**2)
    assert np.allclose(quantum.anomaly_trace(weyl2, euler, "scalar"), expected, rtol=1e-12, atol=0.)
    ricci_flat = quantum.anomaly_trace(kretschmann, kretschmann, "scalar")
    assert np.allclose(ricci_flat, kretschmann/(2880*math.pi**2), rtol=1e-12, atol=0.)


def _curvature(speed, s, offset):
    service, design, cone = closure.build_spec(closure.TRIM_SCALED, speed)
    radius, _ = front_pass.radial_nodes(service, design, cone)
    z = service.packet_position(s)+offset
    f = fs.fields(service, design, cone, s, z, radius)
    f["C"], f["C_r"], f["C_rr"] = radius.copy(), np.ones_like(radius), np.zeros_like(radius)
    return service, design, cone, radius, z, quantum.invariants(f)


@pytest.mark.parametrize("offset", [-5., -1.9, 2.5, 4.4])
def test_curvature_contractions_reproduce_the_demanded_stress(offset):
    service, design, cone, radius, z, (_, _, _, stress) = _curvature(2.1, 3.75, offset)
    demand = fs.frame_tensor(service, design, cone, 3.75, z, radius)
    assert np.max(np.abs(stress-demand)) < 1e-9*np.max(np.abs(demand))


@pytest.mark.parametrize("s", quantum.SIGMAS)
def test_trace_vanishes_in_the_flat_compartment(s):
    service, _, _, radius, _, (kretschmann, weyl2, euler, _) = _curvature(2.1, s, 0.)
    inside = radius < service.hole_radius[0]
    for field in quantum.ANOMALY_FIELDS:
        assert np.max(np.abs(quantum.anomaly_trace(weyl2, euler, field)[inside])) < 1e-20
    assert np.max(kretschmann[inside]) < 1e-18


def test_passengers_read_the_rear_temperature_at_unit_killing_norm():
    for speed in quantum.SPEEDS:
        service, design, cone = closure.build_spec(closure.TRIM_SCALED, speed)
        assert quantum.compartment_killing_norm(service, design, cone, 3.75) == pytest.approx(1., abs=1e-12)


@pytest.mark.parametrize("sigma", [.5, 1.])
def test_hankel_transform_of_a_gaussian(sigma):
    step = .04
    r = np.arange(0., 14., step)+step/2
    k = quantum.RADIAL_WAVENUMBERS
    error = np.abs(quantum.hankel_forward(np.exp(-r**2/(2*sigma**2)), r)-sigma**2*np.exp(-k**2*sigma**2/2))
    assert np.max(error[k < 15.]) < 1e-7*sigma**2
    assert np.max(error) < 5e-6*sigma**2


@pytest.mark.parametrize("name", list(quantum.MIXING_PACKETS))
def test_packet_carries_positive_frequency_only(name):
    step = .04
    zeta = np.arange(-12., 12., step)+step/2
    r = np.arange(0., 8., step)+step/2

    class Field:
        pass

    phi, Pi = quantum.positive_frequency_packet(zeta, r, 0., quantum.MIXING_PACKETS[name])
    real, imag = Field(), Field()
    real.phi, imag.phi, real.Pi, imag.Pi = phi.real, phi.imag, Pi.real, Pi.imag
    plus, minus = quantum.split_frequencies(real, imag, zeta, r, np.ones_like(phi.real))
    assert minus/(plus+minus) < 1e-8


def test_flat_window_reaches_the_axis_and_stays_inside_flat_space():
    step = .04
    zeta = np.arange(-6., 6., step)+step/2
    r = np.arange(0., 6., step)+step/2
    alpha = np.ones((len(zeta), len(r)))
    alpha[zeta > 3.] = 2.
    damping = np.zeros_like(alpha)
    damping[:, r > 5.] = 1.
    window, flat = quantum.flat_window(alpha, damping, step)
    assert window[np.argmin(np.abs(zeta)), 0] == pytest.approx(1., abs=1e-9)
    assert np.all(window[~flat] == 0.)
    assert np.all(window[zeta > 2.85] < 1e-3)
    assert np.all(window[:, r > 4.85] < 1e-3)


@pytest.mark.parametrize("speed", quantum.SPEEDS)
def test_sample_times_include_the_half_extended_cone(speed):
    service, _, cone = closure.build_spec(closure.TRIM_SCALED, speed)
    times = quantum.sample_times(service, cone)
    assert set(quantum.SIGMAS) <= set(times)
    extra = sorted(set(times)-set(quantum.SIGMAS))
    assert len(extra) == 2
    for s in extra:
        assert service.carry_speed(s) == pytest.approx(sum(cone.extend)/2, abs=1e-5)


def test_window_control_reads_the_floor_deep_in_flat_space_and_the_edge_astride_it():
    rows = {row["depth"]: row for row in quantum.window_control((2.1, "axis_wavelength_1"))}
    assert rows[4.]["windowed_norm"] == pytest.approx(1., abs=1e-6)
    assert rows[4.]["negative_share"] < 1e-8
    assert rows[0.]["negative_share"] > 1e-4
