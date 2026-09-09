import numpy as np
from scipy.optimize import minimize_scalar

from adm_harness.smooth_mirror import fermi_surface_match
from adm_harness.smooth_mirror_material import (dirac_squared_levels,
    transverse_gap_squared, tree_level_match, optimal_zero_band_scale,
    zero_band_yukawa_threshold)


def test_independent_dirac_spectrum_converges_to_zero_and_first_bound_branch():
    for a in [1.5, 2.1, 4.]:
        exact = np.array([0., 2*a-1])
        errors = [np.max(abs(dirac_squared_levels(a, h)-exact)) for h in [.04, .02, .01]]
        assert errors[-1] < errors[0]/15
        assert errors[-1] < .002


def test_zero_branch_filling_uses_first_excitation_and_bulk_threshold():
    assert np.isclose(transverse_gap_squared(.5), .25)
    assert np.isclose(transverse_gap_squared(1), 1)
    assert np.isclose(transverse_gap_squared(2.1), 3.2)
    assert transverse_gap_squared(2.1) < 2.1**2


def test_tree_match_counts_common_quantum_scale_and_keeps_occupied_branch_confined():
    m = fermi_surface_match(6.8, 1.5)
    tau, gas = m['wall_tension'], m['fermi_energy']
    for flavors in [1, 4, 16, 64]:
        eta = optimal_zero_band_scale(.05, gas, flavors)
        row = tree_level_match(.05, 2., tau, gas, eta, flavors)
        assert row['only_zero_branch_filled'] and row['confined_below_continuum']
        assert row['quartic_determinant'] > 0
        assert abs(row['tension_reconstruction_error']) < 1e-17
        assert abs(row['gas_reconstruction_error']) < 1e-17
        assert abs(row['optical_reconstruction_error']) < 1e-14


def test_yukawa_threshold_minimum_agrees_with_independent_optimization():
    m = fermi_surface_match(6.8, 1.5)
    tau, gas = m['wall_tension'], m['fermi_energy']
    measures = []
    for flavors in [1, 4, 64]:
        opt = minimize_scalar(lambda x: zero_band_yukawa_threshold(x, tau, gas, flavors),
                              bounds=(.01, 10), method='bounded')
        assert np.isclose(opt.x, np.sqrt(3), atol=1e-5)
        expected = np.sqrt(32*np.pi*gas/(3*np.sqrt(3)*flavors*tau))
        assert np.isclose(opt.fun, expected, rtol=1e-11)
        measures.append(flavors*opt.fun**2/(16*np.pi**2))
    assert np.allclose(measures, 2*gas/(3*np.sqrt(3)*np.pi*tau), rtol=1e-11)
