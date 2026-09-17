import numpy as np
from numpy.testing import assert_allclose

from adm_harness.constitutive_joints_and_optics import series_state
from adm_harness.reaction_work_interfaces import (
    sheet_boundary_state, reflector_ports, capacitor_bank, capacitor_field_split,
    minimum_field_conversion, capacitor_energy_upper,
    periodic_capacitor_cell,
)
from adm_harness.standing_field_losses import photon_to_maxwell


def test_boundary_work_and_mirror_doppler_balance():
    T = np.array([.3, 20., 300.])
    b = sheet_boundary_state(T, 2., 1., [-.1, .2, -.3], .004)
    assert_allclose(b["mechanical_power"], b["material_energy_rate"], rtol=2e-14)
    ports = reflector_ports(b["force_per_facet"], b["facet_velocity"])
    assert_allclose(ports["outgoing"]/ports["incoming"],
                    (1-b["facet_velocity"])/(1+b["facet_velocity"]), rtol=2e-14)
    assert_allclose(ports["incoming"]-ports["outgoing"], b["mechanical_power"], atol=1e-10)


def test_capacitor_field_derivative_and_terminal_power():
    T, rate, dt = 20., .2, 1e-4
    b = sheet_boundary_state(T, 2., 1., rate, .004)
    initial_length = b["length"]
    c = capacitor_bank(b, initial_length, .00003, epsilon_area=3.)
    before = capacitor_bank(sheet_boundary_state(T-rate*dt, 2., 1., rate, .004),
                            initial_length, .00003, epsilon_area=3.)
    after = capacitor_bank(sheet_boundary_state(T+rate*dt, 2., 1., rate, .004),
                           initial_length, .00003, epsilon_area=3.)
    assert_allclose((after["field_energy"]-before["field_energy"])/(2*dt),
                    c["field_energy_rate"], rtol=2e-8)
    assert_allclose(4*c["voltage_per_facet"]*c["charge_rate_per_facet"], c["electrical_power"])
    assert abs(c["balance_error"]) < 1e-15


def test_capacitor_stress_is_counted_in_existing_field_tensor():
    fields = np.array([.01, .02, .4, .3])
    demand = capacitor_field_split(.08, .15)
    eta = minimum_field_conversion(fields, demand)
    after = photon_to_maxwell(fields, eta)
    remaining = after.copy(); remaining[:2] -= demand
    assert remaining.min() >= -1e-15
    basis = np.array([[1, 1, 1, 1], [1, -1, 1, 0], [0, 2, 0, 1]])
    capacitor_tensor = np.array([.08+.15, .15, .08])
    assert_allclose(basis@remaining+capacitor_tensor, basis@fields, atol=1e-15)


def test_continuous_capacitor_energy_ceiling_covers_interior_baselines():
    M, m, increment = 2., .2, .4
    upper = capacitor_energy_upper(.1, 100., M, m, increment)
    for T in np.geomspace(.1, 100., 24):
        low = series_state(T, M, m, dimension=2)
        high = series_state(T+increment, M, m, dimension=2)
        L0 = low["core_linear_stretch"]+1e-4*low["joint_stretch"]
        L1 = high["core_linear_stretch"]+1e-4*high["joint_stretch"]
        for shift in np.linspace(0, increment, 9):
            b = sheet_boundary_state(T+shift, M, m, 0., 1.)
            c = capacitor_bank(b, L0, .55*(L1-L0))
            assert c["field_energy"] <= upper


def test_unavailable_radial_field_is_identified():
    assert np.isinf(minimum_field_conversion(np.array([0., 0., 1., 0.]), np.array([0., .1])))


def test_periodic_return_plates_count_each_gap_once():
    b = sheet_boundary_state(20., 2., 1., .2, .004)
    c = periodic_capacitor_cell(b, b["length"]+.00006, epsilon_area=3.)
    assert_allclose(c["field_energy"], .5*2*c["charge_per_facet"]*c["full_gap_voltage"])
    assert_allclose(c["electrical_power"], 2*c["full_gap_voltage"]*c["charge_rate_per_facet"])
    assert_allclose(c["mechanical_power"], 2*b["force_per_facet"]*b["length_rate"])
