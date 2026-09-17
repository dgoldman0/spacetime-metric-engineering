import numpy as np
import pytest
from numpy.testing import assert_allclose

from adm_harness.moving_thermal_relay import (
    RadialTrajectory, annular_axis_ensemble, elastic_redirect, moving_paired_relay,
    null_leg, opposed_capacitor_drive, radial_work_lead, radial_work_reflector,
    reaction_work_allowance, relay_bounds, selected_route_bounds,
)


def harmonic_motion(omega=25., speed=.0089):
    t = np.linspace(-.1, 1.1, 241)
    return RadialTrajectory(t, .032+speed/omega*np.sin(omega*t), speed*np.cos(omega*t))


def pulse():
    t = np.linspace(0., 1., 201)
    q = np.where(t < .8, np.sin(np.pi*np.minimum(t, .8)/.8)**2/6, 0.)
    q[0] = q[-1] = 0.
    j = .6+.2*np.sin(9*t)
    return t, q, j


def test_speed_certificate_checks_inside_hermite_panels():
    with pytest.raises(ValueError, match="interpolated trajectory"):
        RadialTrajectory([0., 1.], [.03, .03675], [0., 0.], speed_ceiling=.00905)
    motion = harmonic_motion()
    assert motion.maximum_speed <= motion.speed_ceiling
    assert motion.minimum_radius > 0


def test_null_leg_is_retarded_and_flux_jacobian_matches_time_derivative():
    motion = harmonic_motion(omega=70.)
    t = np.linspace(.05, .92, 43)
    leg = null_leg(t, motion, .013)
    inverse = null_leg(leg["arrival"], motion, .013, arrival_given=True)
    assert_allclose(inverse["departure"], t, atol=2e-15, rtol=0.)
    assert abs(leg["null_error"]).max() < 2e-15
    assert abs(leg["radial_cosine"]).max() <= motion.speed_ceiling
    h = 2e-6
    numerical = (null_leg(t+h, motion, .013)["arrival"]
                 -null_leg(t-h, motion, .013)["arrival"])/(2*h)
    assert_allclose(numerical, leg["arrival_jacobian"], rtol=1e-9)
    assert np.ptp(leg["delay"]) > 1e-8


def test_scatter_conserves_rest_energy_and_has_mechanical_work():
    u = np.array([-.00905, -.004, 0., .004, .00905])
    nr = -u
    incoming = np.stack((nr, np.zeros_like(u), np.sqrt(1-nr*nr)))
    outgoing = np.stack((u, np.sqrt(1-u*u), np.zeros_like(u)))
    scatter = elastic_redirect(np.ones_like(u), incoming, outgoing, u)
    before, after = scatter["incoming_four_force"], scatter["outgoing_four_force"]
    gamma = 1/np.sqrt(1-u*u)
    assert_allclose(gamma*(before[0]-u*before[1]), gamma*(after[0]-u*after[1]), atol=2e-16)
    assert abs(scatter["work_orthogonality_error"]).max() < 3e-16
    assert scatter["work_to_photons"].max() > 1e-4


def test_uniform_motion_has_nonzero_flight_delay_and_zero_guide_work():
    t, Q, j = pulse()
    v, L = .00905, .0078125
    motion = RadialTrajectory([-.1, 1.1], [.03-.1*v, .03+1.1*v], [v, v])
    result = moving_paired_relay(t, Q, j, motion, axial_half_separation=L,
                                observation_time=t[::4])
    delay = 2*L/np.sqrt(1-v*v)
    assert_allclose(result["total_retarded_delay"], delay, atol=2e-16, rtol=0.)
    assert abs(result["guide_work_to_photons"]).max() < 2e-16
    assert_allclose(result["bath_total_power"], 2*np.interp(t[::4]-delay, t, Q, left=0., right=0.), atol=3e-16)
    assert_allclose(result["total_arrival_jacobian"], 1., atol=2e-16)
    assert result["flight_energy"].max() > 0.
    assert result["flight_energy"][-1] == 0.


def test_variable_relay_includes_retarded_flux_recoil_and_six_rotor_tensor():
    t, Q, j = pulse()
    result = moving_paired_relay(t, Q, j, harmonic_motion(omega=60.), observation_time=t[::2])
    for key in ("four_momentum_balance_error", "energy_balance_error", "source_guide_work_error",
                "central_guide_work_error", "destination_guide_work_error",
                "bath_matched_radial_momentum_error"):
        assert abs(result[key]).max() < 5e-16
    baths = result["bath_arrival_stream_power"]
    assert_allclose(baths[:, 0], baths[:, 1], atol=2e-16)
    tensor = result["flight_tensor"]
    assert_allclose(tensor[1, 1]+tensor[2, 2]+tensor[3, 3], tensor[0, 0], atol=2e-17)
    ensemble = result["six_rotor_flight_tensor"]
    assert_allclose(ensemble[0, 0], 3*result["flight_energy"], atol=2e-17)
    for axis in (1, 2, 3):
        assert_allclose(ensemble[axis, axis], result["flight_energy"], atol=2e-17)
        assert abs(ensemble[0, axis]).max() < 2e-17
    assert result["guide_work_to_photons"].max() > 1e-7
    assert result["guide_work_to_photons"].min() < -1e-7


def test_integrated_flight_four_momentum_derivative_matches_boundary_flux():
    t, Q, j = pulse()
    centers = np.array([.07321, .2173, .3918, .5777, .7401])
    h = 2e-5
    obs = np.r_[centers-h, centers, centers+h]
    result = moving_paired_relay(t, Q, j, harmonic_motion(omega=60.),
                                observation_time=obs, quadrature_order=10)
    count = len(centers)
    momentum = result["flight_tensor"][0]
    numerical = (momentum[:, 2*count:]-momentum[:, :count])/(2*h)
    assert_allclose(numerical, result["flight_four_momentum_rate"][:, count:2*count],
                    atol=3e-10, rtol=2e-7)


def test_relay_ceilings_and_reaction_work_are_small_but_counted():
    t, Q, j = pulse()
    result = moving_paired_relay(t, Q, j, harmonic_motion(omega=80.), observation_time=t)
    b = relay_bounds()
    peak = 2*Q.max()
    assert result["flight_energy"].max() <= b["flight_energy_per_emitted_peak"]*peak
    assert result["bath_total_power"].max() <= b["bath_power_per_emitted_peak"]*peak
    assert abs(result["guide_work_by_stage"]).sum(axis=0).max() <= b["guide_work_peak_per_emitted_power"]*peak
    assert abs(result["flight_energy_rate"]).max() <= b["flight_rate_peak_per_emitted_peak"]*peak
    allowance = reaction_work_allowance(4.297704)
    assert 2e-9 < allowance["maximum_additional_guide_work"] < 2.3e-9
    assert allowance["required_additional_emitted_half_channel_margin"] < 3e-9
    assert 5e-10 < allowance["guide_work_l1_per_optical_l1"] < 5.2e-10
    assert b["maximum_total_delay"] > b["minimum_total_delay"]


def test_annular_average_keeps_axial_momentum_until_opposed_routes_cancel():
    tensor = np.zeros((4, 4, 1))
    tensor[0, 0] = tensor[3, 3] = tensor[0, 3] = tensor[3, 0] = 1.
    ensemble = annular_axis_ensemble(tensor)
    assert_allclose(ensemble[0, 1:, 0], 1.)
    assert_allclose(ensemble[0, 0], 3.)


def test_radial_reflector_counts_force_throughput_at_zero_work():
    F = np.array([-3e-8, -1e-8, 0., 1e-8, 3e-8])
    u = np.array([.00905, -.00905, 0., .00905, -.00905])
    ports = radial_work_reflector(F, u)
    assert abs(ports["force_error"]).max() < 1e-23
    assert abs(ports["work_error"]).max() < 1e-23
    held = radial_work_reflector(F, 0.)
    assert_allclose(held["encountered_power"], abs(F), atol=0.)
    assert_allclose(held["mechanical_power"], 0., atol=0.)


def test_capacitor_work_includes_energy_and_needs_force_rate_information():
    t = np.linspace(0., 1., 11)
    F, d = 2e-8*np.sin(3*t), .002*np.sin(2*t)
    Fdot, u = 6e-8*np.cos(3*t), .004*np.cos(2*t)
    cell = opposed_capacitor_drive(F, Fdot, d, u, half_gap=.004, bias_force=2e-8)
    assert abs(cell["energy_balance_error"]).max() < 2e-25
    assert_allclose(cell["field_energy"], 2*2e-8*.004-F*d, atol=5e-26)
    assert_allclose(cell["electrical_power"], -Fdot*d, atol=5e-26)
    fast = opposed_capacitor_drive(F, 100*Fdot, d, u, half_gap=.004, bias_force=2e-8)
    assert_allclose(fast["electrical_power"], 100*cell["electrical_power"], atol=5e-24)
    assert_allclose(fast["mechanical_power"], cell["mechanical_power"], atol=0.)


def test_fixed_work_ports_retain_variable_delay_and_photon_energy():
    t = np.linspace(0., 1., 201)
    force = 2e-7*np.sin(7*np.pi*t)*np.sin(np.pi*t)**2
    force[0] = force[-1] = 0.
    motion = harmonic_motion(omega=50.)
    centers = np.array([.1371, .2931, .4121, .6977, .8241])
    h = 2e-5
    obs = np.r_[centers-h, centers, centers+h]
    lead = radial_work_lead(t, force, motion, reference_radius=.032, half_gap=.003,
                            observation_time=obs, quadrature_order=10)
    for key in ("energy_balance_error", "radial_momentum_balance_error", "mechanical_work_error"):
        assert abs(lead[key]).max() < 2e-22
    for value, derivative in (("photon_energy", "photon_energy_rate"),
                              ("photon_radial_momentum", "photon_radial_momentum_rate")):
        num = (lead[value][10:]-lead[value][:5])/(2*h)
        assert_allclose(num, lead[derivative][5:10], atol=4e-16, rtol=2e-6)
    assert lead["photon_energy"].min() > 0.
    assert abs(lead["remote_net_power"]-lead["mechanical_power"]).max() > 1e-10


def test_thermal_guide_radial_recoil_has_explicit_reflective_work_ports():
    t, Q, j = pulse()
    motion = harmonic_motion(omega=60.)
    thermal = moving_paired_relay(t, Q, j, motion)
    forces = np.stack((-thermal["source_guide_four_force"][:, :, 1].sum(axis=(0, 1)),
        -thermal["central_guide_four_force"][:, 1].sum(axis=0),
        -thermal["destination_guide_four_force"][:, :, 1].sum(axis=(0, 1))))
    for index, force in enumerate(forces):
        lead = radial_work_lead(t, force, motion, reference_radius=.032, half_gap=.003)
        assert_allclose(lead["mechanical_power"], thermal["guide_work_by_stage"][index], atol=2e-16)
        assert lead["photon_energy"].max() > 0.
        assert lead["photon_energy"][-1] == 0.


def test_selected_route_bounds_reduce_to_stationary_heat_delay():
    b = selected_route_bounds(.0074, maximum_speed=0., axial_half_separation=.02)
    assert b["complete_flight_energy_per_emitted_peak"] == .04
    assert b["complete_flight_rate_peak_per_emitted_peak"] == 1.
    assert b["complete_flight_rate_l1_per_emitted_energy"] == 2.
    assert b["actuator_energy_per_emitted_peak"] == 0.
    moving = selected_route_bounds(.0074)
    assert 2 < moving["complete_flight_rate_l1_per_emitted_energy"] < 2.06
    assert moving["complete_flight_rate_peak_per_emitted_peak"] < 1.03
