import math

import numpy as np
import pytest

from adm_harness import scalar_wave as sw


def grid(length=16., radius=6., h=.05):
    zeta = np.arange(-length/2, length/2, h)+h/2
    r = np.arange(0., radius, h)+h/2
    return zeta, r


def centroid(wave):
    e = wave.energy_density()*wave.cell_volume()
    return float(np.sum(e*wave.zeta[:, None])/np.sum(e))


@pytest.mark.parametrize("shift", [0., -.5, .8])
def test_packet_moves_at_the_light_speed_and_keeps_its_energy_in_flat_space(shift):
    zeta, r = grid()
    shape = (len(zeta), len(r))
    wave = sw.AxisymmetricWave(zeta, r, np.ones(shape), np.full(shape, shift), np.zeros(shape), dissipation=.02)
    wave.set_packet(-3., 0., 1., 1.5, 1.)
    start, energy = centroid(wave), float(np.sum(wave.energy_density()*wave.cell_volume()))
    dt, t = wave.stable_step(), 0.
    while t < 2.:
        wave.step(dt)
        t += dt
    assert centroid(wave)-start == pytest.approx((1.-shift)*t, abs=.03)
    assert float(np.sum(wave.energy_density()*wave.cell_volume())) == pytest.approx(energy, rel=2e-3)


def test_killing_energy_is_conserved_on_a_stationary_background():
    zeta, r = grid(20., 7.)
    z, rr = zeta[:, None], r[None, :]
    alpha = 1.+1.5*np.exp(-z**2/8.-rr**2/6.)
    b = np.full(alpha.shape, 1.4)
    wave = sw.AxisymmetricWave(zeta, r, alpha, b, np.zeros(alpha.shape), dissipation=.02)
    wave.set_packet(4., 1., 1.5, 1.5, 3.)
    start = wave.killing_energy()
    dt, t = wave.stable_step(), 0.
    while t < 2.5:
        wave.step(dt)
        t += dt
    assert wave.killing_energy() == pytest.approx(start, rel=1e-3)


def test_axis_reflection_keeps_the_field_even_and_smooth():
    zeta, r = grid(12., 4.)
    shape = (len(zeta), len(r))
    wave = sw.AxisymmetricWave(zeta, r, np.ones(shape), np.zeros(shape), np.zeros(shape))
    wave.set_packet(0., 0., 1., .6, 1.)
    dt = wave.stable_step()
    for _ in range(200):
        wave.step(dt)
    profile = wave.phi[np.argmax(np.abs(wave.phi[:, 0])), :6]
    assert np.all(np.isfinite(wave.phi))
    assert abs(profile[1]-profile[0]) < .05*abs(profile[0])+1e-9


def test_damping_layer_rises_to_the_edges():
    zeta, r = grid()
    layer = sw.damping_layer(zeta, r, back=2., front=2., outer=1., rate=5.)
    assert layer[len(zeta)//2, 0] == 0.
    assert layer[0, 0] == pytest.approx(5., rel=.1) and layer[-1, 0] == pytest.approx(5., rel=.1)
    assert layer[len(zeta)//2, -1] == pytest.approx(5., rel=.1)
