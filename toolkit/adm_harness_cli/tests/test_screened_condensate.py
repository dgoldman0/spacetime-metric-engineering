import numpy as np
import pytest
from scipy.integrate import simpson

from adm_harness.screened_condensate import (CondensateParameters, field_stress,
    flat_rhs, homogeneous_phase, solve_flat_reference, gravitating_rhs)


def test_homogeneous_state_is_screened_and_stationary():
    p = CondensateParameters(charge=1.)
    for omega in [1.164, 1.170, 1.180]:
        state = homogeneous_phase(omega, p)
        assert np.max(abs(flat_rhs(1., state['fields'], omega, p))) < 1e-14
        assert abs(state['matter_charge']+state['higgs_charge']) < 1e-15
        assert np.isclose(state['energy']+state['radial_pressure'], omega*state['matter_number'])
    zero = homogeneous_phase(homogeneous_phase(1.170, p)['zero_pressure_frequency'], p)
    assert abs(zero['radial_pressure']) < 1e-15


def test_homogeneous_thermodynamic_derivative_counts_matter_number():
    p = CondensateParameters()
    omega, delta = 1.170, 1e-6
    dp = (homogeneous_phase(omega+delta, p)['radial_pressure']-
          homogeneous_phase(omega-delta, p)['radial_pressure'])/(2*delta)
    assert np.isclose(dp, homogeneous_phase(omega, p)['matter_number'], rtol=1e-8)


def test_stress_channels_and_null_contractions_from_constituent_energies():
    p = CondensateParameters()
    rng = np.random.default_rng(7249)
    fields = rng.normal(size=(6, 30))
    t = field_stress(fields, .8, p, metric_f=.7, sigma=.9)
    kinetic = t['matter_kinetic']+t['higgs_kinetic']
    assert np.allclose(t['energy']+t['radial_pressure'], 2*(kinetic+t['gradient']))
    assert np.allclose(t['energy']+t['tangential_pressure'], 2*(kinetic+t['electric']))
    assert np.all(t['energy'] >= abs(t['radial_pressure']))
    assert np.all(t['energy'] >= abs(t['tangential_pressure']))


def test_gravitating_equations_reduce_to_flat_fields_and_vacuum_schwarzschild():
    p = CondensateParameters()
    fields = np.array([.2, .01, .8, .02, .4, -.1])
    actual = gravitating_rhs(5., np.r_[fields, 0., 0.], .9, 0., p)
    expected = flat_rhs(5., fields, .9, p)
    expected[[1, 3, 5]] -= 2/5*fields[[1, 3, 5]]
    assert np.allclose(actual[:6], expected)
    assert np.array_equal(actual[6:], [0., 0.])
    vacuum = gravitating_rhs(5., [0., 0., 1., 0., 0., 0., 1., 0.], .9, 1e-3, p)
    assert np.array_equal(vacuum, np.zeros(8))


@pytest.mark.parametrize('kind', ['homogeneous', 'hollow'])
def test_reference_charge_mass_binding_and_full_stress_conservation(kind):
    p, omega, solution = solve_flat_reference(kind)
    r = np.linspace(0, 250, 12001)
    t = field_stress(solution.sol(r), omega, p)
    energy = simpson(r*r*t['energy'], x=r)
    number = simpson(r*r*t['matter_number'], x=r)
    charge = simpson(r*r*(t['matter_charge']+t['higgs_charge']), x=r)
    assert abs(charge)/(p.charge*number) < 2e-7
    assert abs(simpson(r*r*(t['radial_pressure']+2*t['tangential_pressure']), x=r))/energy < 2e-7
    assert energy < np.sqrt(p.matter_coupling)*number
    assert np.min(t['tangential_pressure']) < 0 < np.max(t['tangential_pressure'])
    assert np.isclose(2*simpson(t['tangential_pressure'], x=r),
                      simpson(t['radial_pressure'], x=r), atol=1e-6)


@pytest.mark.parametrize('changes', [{'charge': 0.}, {'matter_coupling': -1.}, {'higgs_coupling': np.nan}])
def test_invalid_couplings_rejected(changes):
    with pytest.raises(ValueError):
        CondensateParameters(**changes)
