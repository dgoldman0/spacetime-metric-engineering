import numpy as np
from numpy.testing import assert_allclose
import pytest

from adm_harness.thermal_exchange_interfaces import (
    matched_axial_relay, paired_absorption_exchange, passive_absorption_gain,
    radial_collector, tangential_emission, three_axis_average,
)


def test_each_emitted_stream_matches_two_lorentz_boosts_and_clock_conversion():
    for w, v in ((.83, .2), (-.83, -.2), (.3, -.1)):
        gt, gr = 1/np.sqrt(1-w*w), 1/np.sqrt(1-v*v)
        tangent = np.array([[gt, 0, gt*w, 0], [0, 1, 0, 0],
                            [gt*w, 0, gt, 0], [0, 0, 0, 1]])
        radial = np.array([[gr, gr*v, 0, 0], [gr*v, gr, 0, 0],
                           [0, 0, 1, 0], [0, 0, 0, 1]])
        result = tangential_emission(2.3, w, v)
        for i, direction in enumerate((1., -1.)):
            proper = 2.3/2*np.array([1., 0., direction, 0.])
            expected = radial@tangent@proper/(gr*gt)
            assert_allclose(result["stream_four_force"][i], expected, rtol=2e-15, atol=1e-15)


def test_cold_rotor_force_is_orthogonal_to_its_material_velocity():
    q = np.array([1., -1., .2, -.4])
    j = np.array([.83, .83, .3, .3])
    v = np.array([.2, -.2, .01, -.01])
    r = paired_absorption_exchange(q, j, .02, v)
    assert_allclose(r["incoming"]-r["outgoing"], q, atol=5e-16)
    assert_allclose(r["cold_four_force"]+r["emitted_four_force"], r["optical_four_force"])
    assert_allclose(r["paired_bath_four_force"][2:], 0, atol=1e-17)
    assert_allclose(r["paired_bath_four_force"][1], v*r["material_rest_heat_power"])
    for i, sign in enumerate((1., -1.)):
        cold = r["cold_four_force"][i]
        residual = cold[0]-v*cold[1]-sign*j*np.sqrt(1-v*v)*cold[2]
        assert_allclose(residual, 0, atol=3e-16)


def test_directed_emitter_delivers_zero_angular_momentum_with_recoil():
    j = np.array([.3, .83])
    r = tangential_emission(1., j, direction_bias=-j)
    assert_allclose(r["stream_four_force"][:, 0], np.broadcast_to((1-j*j)/2, (2, 2)))
    assert_allclose(r["total_four_force"][2], 0, atol=5e-17)
    proper_recoil = -(r["rest_stream_power"][0]-r["rest_stream_power"][1])
    assert_allclose(proper_recoil, j)


def test_passive_gain_bounds_both_power_directions_and_all_allowed_spins():
    j = np.linspace(.3, .95, 200)
    alpha = .02
    limit = passive_absorption_gain(alpha, .3)
    for sign in (-1, 1):
        r = paired_absorption_exchange(sign*np.ones_like(j), j, alpha)
        assert r["material_rest_heat_power"].max() <= limit*(1+1e-14)
    actual = paired_absorption_exchange(-1., .3, alpha)
    assert_allclose(actual["material_rest_heat_power"], limit)
    assert_allclose(actual["material_rest_heat_power"]/actual["directed_zero_J_heat_power"], 1/(1-.3**2))


def test_matched_finite_relay_retains_photon_momentum_and_local_guide_reactions():
    time = np.linspace(0, 12, 601)
    heat = np.where(time < 8, np.sin(np.pi*np.minimum(time, 8)/8)**2, 0.)
    heat[0] = heat[-1] = 0.
    spin = .6+.2*np.cos(time)
    result = matched_axial_relay(time, heat, spin, .8)
    assert_allclose(result["bath_arrival_stream_power"][:, 0],
                    result["bath_arrival_stream_power"][:, 1], atol=1e-16)
    assert_allclose(result["four_momentum_balance_error"], 0, atol=7e-16)
    assert_allclose(result["flight_energy_rate"],
                    result["source_total_power"]-result["bath_total_power"], atol=5e-16)
    assert result["source_guide_four_force"].max() > .2
    assert abs(result["central_guide_four_force"]).max() > .2
    tensor = result["flight_tensor"]
    assert_allclose(tensor[3, 3], result["flight_energy"])
    assert_allclose(tensor[2, 2], 0)
    assert_allclose(tensor[0, 1:], 0, atol=8e-16)
    average = three_axis_average(tensor)
    for axis in (1, 2, 3):
        assert_allclose(average[axis, axis], result["flight_energy"]/3)
    assert result["flight_energy"].max() <= .8*result["source_total_power"].max()
    assert_allclose(result["flight_energy"][-1], 0, atol=1e-14)


def test_moving_collector_recoil_obeys_work_and_null_ray_identities():
    rng = np.random.default_rng(991)
    direction = rng.normal(size=(3, 100))
    direction /= np.linalg.norm(direction, axis=0)
    result = radial_collector(1., np.linspace(-.2, .2, 100), direction,
                             np.where(np.arange(100) % 2, -1., 1.))
    assert_allclose(result["rest_frame_work_error"], 0, atol=5e-16)
    before, after = result["incoming_four_momentum"], result["outgoing_four_momentum"]
    assert_allclose(after[0]**2, (after[1:]**2).sum(axis=0), atol=8e-16)
    assert_allclose(before-after, result["guide_recoil_four_momentum"])


def test_axial_collector_has_the_stated_velocity_squared_energy_cost():
    v = .00905
    result = radial_collector(1., v, [0., 0., 1.])
    assert_allclose(result["energy_ratio"], 1/(1-v*v), rtol=2e-15)
    assert_allclose(result["mechanical_work_to_photon"], v*v/(1-v*v), atol=2e-16)


def test_invalid_ports_and_infinite_pulse_extensions_are_rejected():
    with pytest.raises(ValueError):
        passive_absorption_gain(.8, .3)
    with pytest.raises(ValueError):
        radial_collector(1., .1, [0., 0., 2.])
    with pytest.raises(ValueError):
        matched_axial_relay([0., 1., 2.], [1., 1., 1.], [.3, .3, .3], .1)
