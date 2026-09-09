import numpy as np
from scipy.optimize import linprog

from adm_harness.vacuum_support import (
    casimir_channels, initial_ordinary, minimum_dec_weights,
    minimum_vacuum_split, static_force, supported_cell_floor,
)


def independent_lp(target, cap, radial_only):
    # Five unknowns: Cr,Ct,host E,host Pr,host Pt. Equality constraints use
    # complete tensors, independently of the production two-variable bounds.
    aeq = np.array([[-1., -2., 1., 0., 0.],
                    [-3., 2., 0., 1., 0.], [1., -2., 0., 0., 1.]])
    aub = np.array([[0., 0., -cap, 1., 0.], [0., 0., -cap, -1., 0.],
                    [0., 0., -cap, 0., 1.], [0., 0., -cap, 0., -1.]])
    return linprog([1., 2., 0., 0., 0.], A_eq=aeq, b_eq=target,
        A_ub=aub, b_ub=np.zeros(4),
        bounds=[(0., None), (0., 0. if radial_only else None), (0., None), (None, None), (None, None)],
        method='highs')


def test_vacuum_tensor_has_correct_null_projections_and_trace():
    cr, ct = np.array([0., .2, 1.]), np.array([.4, .1, 0.])
    q = casimir_channels(cr, ct)
    np.testing.assert_allclose(q[:, 0]+q[:, 1], -4*cr, atol=1e-15)
    np.testing.assert_allclose(q[:, 0]+q[:, 2], -4*ct, atol=1e-15)
    np.testing.assert_allclose(-q[:, 0]+q[:, 1]+2*q[:, 2], 0., atol=1e-15)


def test_minimum_weights_match_independent_five_variable_linear_programs():
    rng = np.random.default_rng(248619)
    targets = np.vstack([rng.normal(size=(40, 3)), [0., 0., 0.], [1., -.5, .5], [-1., -3., 1.]])
    for cap in [1., .5]:
        for radial_only in [False, True]:
            result = minimum_vacuum_split(targets, cap, radial_only)
            for i, target in enumerate(targets):
                lp = independent_lp(target, cap, radial_only)
                assert result['feasible'][i] == lp.success
                if lp.success:
                    np.testing.assert_allclose(result['vacuum_magnitude'][i], lp.fun, atol=3e-12)
                    assert np.min(result['host_margins'][i]) > -3e-12
                    np.testing.assert_allclose(result['vacuum'][i]+result['host'][i], target, atol=1e-14)
                else:
                    assert np.isnan(result['weights'][i]).all()


def test_closed_form_dec_bound_and_scale_covariance():
    rng = np.random.default_rng(52271)
    targets = rng.normal(size=(73, 3))
    result = minimum_vacuum_split(targets)
    np.testing.assert_allclose(result['weights'], minimum_dec_weights(targets), atol=2e-15)
    for scale in [1e-24, 1e-8, 1e9]:
        other = minimum_vacuum_split(scale*targets)
        np.testing.assert_allclose(other['weights']/scale, result['weights'], atol=2e-15)


def test_radial_vacuum_cannot_supply_negative_angular_enthalpy_with_dec_host():
    target = np.array([[-1., -1., .2], [-.2, -1., .2]])
    radial = minimum_vacuum_split(target, radial_only=True)
    assert not radial['feasible'][0]
    assert radial['feasible'][1]
    assert minimum_vacuum_split(target)['feasible'].all()


def test_opposite_ordinary_currents_preserve_initial_energy_and_both_positive_enthalpies():
    r = np.linspace(2.15, 6.25, 65)
    ordinary, states = initial_ordinary(r, .01, .04)
    rn, vn, rs, vs = states.T
    j = 1.2*rn*vn/(1-vn*vn)+(4/3)*rs*vs/(1-vs*vs)
    np.testing.assert_allclose(j, 0., atol=2e-21)
    assert np.min(ordinary[:, 0]+ordinary[:, 1]) > 0
    assert np.min(ordinary[:, 0]+ordinary[:, 2]) > 0
    np.testing.assert_allclose(initial_ordinary(r, 0., 0.)[0], 0.)


def test_static_force_recovers_conserved_tension_profile_and_cell_cost():
    r = np.linspace(2., 4., 65)
    energy = .3+.2*r*r
    source = np.stack([energy, -energy, -energy-.2*r*r], axis=-1)
    np.testing.assert_allclose(static_force(r, np.ones_like(r), r*r, source), 0., atol=2e-13)
    cr, ct = .2, .3
    vacuum = casimir_channels(cr, ct)
    minimum_strut_energy = 3*(cr+2*ct)
    np.testing.assert_allclose(vacuum[0]+minimum_strut_energy, supported_cell_floor(cr, ct))
