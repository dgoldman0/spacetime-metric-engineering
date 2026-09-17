"""Independent field, carrier, terminal and finite-flight energy controls."""
import numpy as np
import pytest
from scipy.constants import c, epsilon_0, proton_mass, elementary_charge

from adm_harness.finite_electrical_leads import (
    ElectricalScale, FiniteCoax, ReconstructedWorkPorts, choose_carrier_inventory,
    hardware_screen, required_power_scale, sheet_acceleration,
    geometrized_cell_scale,
)
from adm_harness.reaction_work_interfaces import sheet_boundary_state


CONTEXT = dict(tension=[2.867644925605486, 221.17442092455755],
    core_inventory=[23.198641561182807, 372.4405548938416],
    joint_inventory=[.03942331204631685, .6329181032242602])


def local_ports():
    t = np.linspace(-2, 2, 201)
    return ReconstructedWorkPorts(t, .07+.04*np.tanh(t), CONTEXT, reconstruction_step=None)


class HarmonicPorts:
    """Four independent known terminal waveforms, including signed recovery."""
    def __init__(self, frequency=1.7):
        self.frequency = frequency

    def __call__(self, time):
        t = np.asarray(time)
        a = np.arange(1., 5.).reshape((4,)+(1,)*t.ndim)
        w = self.frequency
        V = 1+.07*a*np.sin(w*t+.1*a)
        I = .13*a*np.cos(w*t-.2*a)
        Vd, Id = .07*a*w*np.cos(w*t+.1*a), -.13*a*w*np.sin(w*t-.2*a)
        return dict(voltage=V, current=I, voltage_rate=Vd, current_rate=Id,
            electrical_power=V*I)


def finite_line():
    charge = np.array([1., 2., 3., 4.])
    return FiniteCoax(.4, .01, np.e, .02/charge, charge, .01, .1)


def test_physical_scaling_matches_charge_field_energy_and_carrier_mass():
    chi, delta = .001, .03
    power = required_power_scale(chi)
    scale = ElectricalScale(power*delta, delta)
    np.testing.assert_allclose(scale.carrier_coefficient(proton_mass/elementary_charge), chi)
    np.testing.assert_allclose(scale.charge**2, epsilon_0*scale.cell_energy_joule*c*delta)
    electric, magnetic = scale.fields(2., 2.)
    np.testing.assert_allclose(electric, c*magnetic)
    np.testing.assert_allclose(epsilon_0*electric**2*scale.length**3/scale.cell_energy_joule, 4.)
    first = geometrized_cell_scale(3e-5, 1e-7, 100., 2e-12)
    larger = geometrized_cell_scale(3e-5, 1e-7, 10000., 2e-12)
    np.testing.assert_allclose(first.cell_energy_joule/first.flight_time_second,
        larger.cell_energy_joule/larger.flight_time_second)
    np.testing.assert_allclose(first.carrier_coefficient(proton_mass/elementary_charge),
        larger.carrier_coefficient(proton_mass/elementary_charge))


def test_four_fixed_area_terminal_banks_return_complementary_work_and_bias():
    p = local_ports()
    t = np.arange(-1.7, 1.7, .02)+.0073
    s = p(t)
    np.testing.assert_allclose(s["energy"].sum(axis=0), .62, atol=2e-16)
    np.testing.assert_allclose(s["electrical_power"].sum(axis=0), s["mechanical_power"], atol=1e-16)
    # Charge/current and voltage derivatives are checked from independent
    # nearby constitutive states, away from the PCHIP panel junctions.
    qplus, qminus = p(t+1e-4), p(t-1e-4)
    np.testing.assert_allclose((qplus["charge"]-qminus["charge"])/2e-4,
        s["current"], rtol=2e-4, atol=2e-9)
    np.testing.assert_allclose((qplus["voltage"]-qminus["voltage"])/2e-4,
        s["voltage_rate"], rtol=3e-5, atol=3e-8)
    np.testing.assert_allclose((qplus["current"]-qminus["current"])/2e-4,
        s["current_rate"], rtol=2e-4, atol=2e-7)


def test_exact_sheet_acceleration_against_independent_span_and_force_difference():
    t, step = .37, .002
    duty = lambda x: 3+.2*x+.09*x*x
    common = dict(inventory=7., joints=.08, reference_span=.003)
    acceleration = sheet_acceleration(duty(t), tension_rate=.2+.18*t,
        tension_acceleration=.18, **common)
    states = [sheet_boundary_state(duty(t+shift), tension_rate=0., **common)
        for shift in (-step, 0., step)]
    for value, derivative in (("length", "length_acceleration"), ("force_per_facet", "force_acceleration")):
        second = (states[0][value]-2*states[1][value]+states[2][value])/step**2
        np.testing.assert_allclose(second, acceleration[derivative], rtol=2e-6)


def test_positive_kinetic_inductance_has_subluminal_speed_and_counted_rest():
    line = finite_line()
    result = line.evaluate(HarmonicPorts(), np.linspace(0, 1, 11))
    assert np.all(result["speed"] < 1)
    assert np.min(result["carrier_kinetic_energy"]) > 0
    np.testing.assert_allclose(result["carrier_rest_energy"], .08*np.arange(1., 5.))
    with pytest.raises(ValueError, match="both counted"):
        FiniteCoax(.4, .01, np.e, np.ones(4), np.ones(4), .01, .1)


def test_finite_characteristics_match_volume_energy_and_recover_signed_load_work():
    line = finite_line()
    p = HarmonicPorts()
    t = np.linspace(-2, 2, 1001)
    s = line.evaluate(p, t, quadrature=20, source_capacitance=np.full(4, .03))
    np.testing.assert_allclose(s["quadrature_energy_theorem_error"], 0., atol=3e-15)
    assert np.any(s["load_power"] < 0) and np.any(s["load_power"] > 0)
    # Differentiate a separately evaluated stored state; this does not use
    # the boundary-power definition of line_energy_rate.
    h = 2e-5
    plus = line.evaluate(p, t+h, quadrature=20, source_capacitance=np.full(4, .03))
    minus = line.evaluate(p, t-h, quadrature=20, source_capacitance=np.full(4, .03))
    change = ((plus["line_energy"]+plus["source_capacitor_energy"])
        -(minus["line_energy"]+minus["source_capacitor_energy"]))/2/h
    np.testing.assert_allclose(change, s["source_pump_power"]-s["load_power"], atol=5e-10)
    np.testing.assert_allclose((plus["unbalanced_added_trace"]-minus["unbalanced_added_trace"])/2/h,
        s["unbalanced_added_trace_rate"], atol=5e-10)


def test_coax_static_maxwell_stress_and_pressure_from_volume_fields():
    class Static(HarmonicPorts):
        def __call__(self, t):
            shape = (4,)+np.asarray(t).shape
            V, zero = np.full(shape, 2.), np.zeros(shape)
            return dict(voltage=V, current=zero, voltage_rate=zero,
                current_rate=zero, electrical_power=zero)
    line = finite_line()
    s = line.evaluate(Static(), np.linspace(0, 1, 9))
    field_energy = .5*line.capacitance_per_length*4*line.length
    np.testing.assert_allclose(s["line_energy"], field_energy)
    np.testing.assert_allclose(s["required_axial_host_stress"], field_energy)
    np.testing.assert_allclose(s["circumferential_host_stress_sum"], 2*field_energy)
    np.testing.assert_allclose(s["peak_inner_radial_pressure"], .5*(2/line.inner_radius)**2)
    assert np.min(s["carrier_rest_energy"]) > 0
    np.testing.assert_allclose(s["field_momentum"], 0.)


def test_reconstruction_retains_raw_step_as_separate_infinite_acceleration_control():
    t = np.array([-1., -.1, 0., .1, 1., 1.1, 2.])
    trace = .03+.02*np.clip(t, 0., 1.)
    p = ReconstructedWorkPorts(t, trace, CONTEXT)
    raw = p.from_trace(.03, np.array([0., .02]), 0.)
    assert np.max(abs(np.diff(raw["current"], axis=1))) > 0
    # A nonzero ideal current jump would require an impulse in Lk*dI/dt.
    # The reconstructed path instead has continuous current through it.
    nearby = p(np.array([-1e-9, 0., 1e-9]))
    assert np.max(abs(np.diff(nearby["current"], axis=1))) < 1e-8
    assert np.isfinite(nearby["current_rate"]).all()
    endpoint = p(np.array([-2., -1., 2., 3.]))
    np.testing.assert_allclose(endpoint["current"], 0., atol=1e-16)


def test_host_screen_keeps_fixed_electrode_inventory_and_fixture_scope():
    p = local_ports()
    t = np.linspace(-2, 2, 121)
    line = choose_carrier_inventory(p, t, host_coefficient=.001)
    state = line.evaluate(p, t, source_capacitance=.01*p(t)["capacitance"][:, 0])
    a = hardware_screen(p, t, line, state, electrode_charge_fraction=.01)
    b = hardware_screen(p, t, line, state, electrode_charge_fraction=1.)
    np.testing.assert_allclose(a["added_electrode_rest_over_C"], 100*b["added_electrode_rest_over_C"])
    assert a["added_energy_over_C"] > b["added_energy_over_C"]
    assert a["maximum_charge_fraction"] < .01 and a["maximum_drift"] < .01
    assert not a["fixture_trace_cancellation_claimed"]
    assert not a["fixture_evolving_work_included"]
    assert not a["full_maxwell_matter_completion"]
    with pytest.raises(ValueError, match="charge spreading"):
        choose_carrier_inventory(p, t, host_coefficient=.001, length_fraction=.1)
