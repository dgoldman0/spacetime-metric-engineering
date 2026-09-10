import numpy as np
from numpy.testing import assert_allclose

from adm_harness.magnetic_circuits import loop_integrals, magnetic_budget


def flat_fields(proper, clock=1.):
    x = np.asarray(proper)
    return np.full_like(x, 50.), np.full_like(x, clock), np.zeros_like(x), np.zeros_like(x)


def test_flat_circle_and_capsule_with_full_return():
    radius, field = .4, 3.7
    for leg in (0., .3, 2.):
        result = loop_integrals(flat_fields, 0., leg, radius)
        length = 2*leg+2*np.pi*radius
        expected_q = np.pi/(6*length**2)*(4*leg+3*np.pi*radius)/50
        expected_b = np.pi*radius/50
        assert_allclose(result['proper_length'], length, rtol=1e-13)
        assert_allclose(result['quantum_coefficient'], expected_q, rtol=1e-13)
        assert_allclose(result['bend_integral'], expected_b, rtol=1e-13)
        if leg == 0:
            ratio = result['quantum_coefficient']/(2*np.pi*field*result['bend_integral'])
            assert_allclose(ratio, 1/(16*np.pi**2*field*radius**2), rtol=1e-13)


def test_clock_normalization_preserves_the_counted_ratio():
    def metric(l, clock=1.):
        x = np.asarray(l)
        return 5+.03*x*x, clock*np.exp(.06*np.cos(x)), .06*x/(5+.03*x*x), -.06*np.sin(x)
    first = loop_integrals(metric, .2, 2., .3)
    second = loop_integrals(lambda l: metric(l, 7.), .2, 2., .3)
    a, b = magnetic_budget(first, 8, 5), magnetic_budget(second, 8, 5)
    assert_allclose(a['field'], b['field'], rtol=1e-13)
    assert_allclose(a['required_flavors_times_e_squared'], b['required_flavors_times_e_squared'], rtol=1e-13)


def test_geometric_tube_bound_and_landau_separation():
    loop = loop_integrals(flat_fields, 0., 2., .4)
    row = magnetic_budget(loop, 24, 5)
    assert row['tube_radius'] <= 1/(5*loop['maximum_curvature'])*(1+1e-14)
    assert row['tube_radius'] <= loop['half_angle']*loop['minimum_radius']/5*(1+1e-14)
    assert row['landau_ratio'] <= .1*(1+1e-14)
    assert_allclose(np.pi*row['tube_radius']**2*row['field'], 2*np.pi*24, rtol=1e-14)


def test_closed_loop_anomaly_matches_direct_second_derivative():
    def metric(l):
        x = np.asarray(l)
        return 5+.03*x*x, np.exp(.06*np.cos(x)), .06*x/(5+.03*x*x), -.06*np.sin(x)
    row = loop_integrals(metric, .2, 2., .3,
                         second_log_lapse=lambda l: -.06*np.cos(l))
    assert_allclose(row['anomaly_coefficient'], row['anomaly_by_direct_derivative'],
                    rtol=2e-11, atol=1e-14)
