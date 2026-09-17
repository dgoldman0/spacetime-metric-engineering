import numpy as np
import pytest

from adm_harness.c1_angular_absolute import (
    AbsoluteComparison, NativeMetric, conformal_anomaly, conformal_log_source,
    cylinder_pv, integrate_comparison,
)
from adm_harness.c1_angular_response import cylinder_green_excess, improved_tensor


def cylinder(clock=1., radius=2.):
    x = np.linspace(-4., 4., 129)
    return NativeMetric(x, np.full_like(x, radius), np.full_like(x, clock), np.ones_like(x))


@pytest.mark.parametrize('frequency,j', [(0., 0), (.8, 1), (2., 3)])
def test_continuum_shooting_matches_exact_cylinder_images(frequency, j):
    chart = cylinder(clock=3.)
    domain, x = (-3., 3.), .2
    moments = cylinder_green_excess(3*frequency, j, np.array([x]), domain, 2., 3.)
    exact = 3*improved_tensor(chart, np.array([x]), 3*frequency, j, *moments)[0]
    problem = AbsoluteComparison(chart, domain, x)
    value = problem.differences(frequency, j, 0., phase_step=.02, single_mass=True)
    np.testing.assert_allclose(value, exact, rtol=3e-8, atol=1e-15)


def test_clock_normalization_and_pv_linearity():
    a = AbsoluteComparison(cylinder(), (-3., 3.), .2)
    b = AbsoluteComparison(cylinder(clock=7.), (-3., 3.), .2)
    frequencies, harmonics = np.array([0., .8, 1.]), np.array([0, 1, 2])
    value = a.differences(frequencies, harmonics, .7)
    np.testing.assert_allclose(b.differences(frequencies, harmonics, .7), value, atol=5e-16)
    direct = sum(c*a.differences(frequencies, harmonics, np.sqrt(i)*.7, single_mass=True)
                 for i,c in enumerate([1,-3,3,-1]))
    np.testing.assert_allclose(value, direct, atol=3e-16)


def test_proper_jets_against_analytic_coordinate_change():
    x = np.linspace(-.5, .5, 129)
    # l=exp(x), log R=l^2, log A=l^3; B=exp(x).
    chart = NativeMetric(x, np.exp(np.exp(2*x)), np.exp(np.exp(3*x)), np.exp(x))
    jets = chart.proper_log_jets(.11)
    l = np.exp(.11)
    np.testing.assert_allclose(jets, [[l*l,2*l,2,0,0],[l**3,3*l*l,6*l,6,0]], atol=8e-5)


def test_curvature_counterterm_and_trace_on_cylinder():
    r = np.array([np.log(2.),0,0,0,0])
    a = np.zeros(5)
    k = 1/(2880*np.pi**2*2**4)
    np.testing.assert_allclose(conformal_log_source(r,a), k*np.array([1,-1,1]), rtol=5e-15)
    np.testing.assert_allclose(conformal_anomaly(r,a), 2*k, rtol=5e-15)
    curved = r + np.array([0,.01,.03,-.02,.04])
    h = conformal_log_source(curved, np.array([0.,.01,-.02,.03,.04]))
    assert abs(-h[0]+h[1]+2*h[2]) < 1e-18


def test_independent_cylinder_pv_limit_and_precision():
    radius = 2.1
    masses = np.array([8.,16.,32.])
    values = np.array([cylinder_pv(radius,m)['renormalized_tensor'] for m in masses])
    limit = np.polynomial.polynomial.polyfit(masses**-2, values, 2)[0]
    k = 1/(2880*np.pi**2*radius**4)
    np.testing.assert_allclose(-limit[0]+limit[1]+2*limit[2], 2*k, rtol=2e-8)
    np.testing.assert_allclose(cylinder_pv(radius,16.,dps=70)['renormalized_tensor'], values[1], rtol=1e-13)


def test_finite_cylinder_regulators_decouple_from_boundary_interaction():
    problem = AbsoluteComparison(cylinder(), (-1.,1.), .15)
    settings = dict(angular_max=24, frequency_max=32., frequency_order=16, phase_step=.04)
    low = integrate_comparison(problem,4.,**settings)['tensor']
    high = integrate_comparison(problem,8.,**settings)['tensor']
    # Compare against the same frequency measure with only the physical field.
    from adm_harness.c1_angular_response import frequency_rule
    w, measure = frequency_rule(64,1.)
    j = np.arange(25)
    v = problem.differences(w[None,:],j[:,None],0.,single_mass=True)
    exact = np.einsum('jwk,w,j->k',v,measure,2*j+1)/(4*np.pi**2)
    assert np.linalg.norm(high-exact) < .08*np.linalg.norm(low-exact)


@pytest.mark.parametrize('frequency,j,scale', [(-1.,0,1.),(1.,.5,1.),(1.,0,0.)])
def test_invalid_modes_rejected(frequency,j,scale):
    with pytest.raises(ValueError):
        AbsoluteComparison(cylinder(),(-1.,1.),0.).differences(frequency,j,scale)
