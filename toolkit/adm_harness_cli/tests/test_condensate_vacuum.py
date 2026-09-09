from pathlib import Path

import numpy as np
import pytest
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad

from adm_harness.condensate_vacuum import (JoinedProfile, SmoothRadialProblem,
    schur_factors, schur_difference, join_curvature, junction_asymptote,
    local_born_reflection)

ROOT = Path(__file__).resolve().parents[3]


def test_schur_response_matches_dense_inverse_and_resolves_small_changes():
    n = 31
    links = np.full(n-1, 2.)
    diagonal = np.full(n, 4.3)
    extra = np.zeros(n)
    extra[-5:] = .7
    left, right = schur_factors(diagonal, links)
    ml, mr = schur_factors(diagonal+extra, links)
    dl = schur_difference(left, ml, links, extra)
    dr = schur_difference(right[::-1], mr[::-1], links[::-1], extra[::-1])[::-1]
    denominator = left+right-diagonal
    change = dl+dr-extra
    result = -change/(denominator*(denominator+change))
    matrix = np.diag(diagonal)+np.diag(-links, 1)+np.diag(-links, -1)
    expected = np.diag(np.linalg.inv(matrix+np.diag(extra))-np.linalg.inv(matrix))
    assert np.allclose(result, expected, rtol=2e-5, atol=2e-15)
    tiny = schur_difference(left, left, links, extra[::-1]*1e-100)
    assert np.all(tiny > 0) and np.isfinite(tiny).all()


def test_zero_portal_and_clock_rescaling():
    profile = JoinedProfile(ROOT)
    probes = profile.retained.negative_branch_coordinate([3., 4., 5.])
    problem = SmoothRadialProblem.create(profile, probes, spacing=1/64, extent=48)
    assert np.array_equal(problem.mode(.3, 1, [0.]), np.zeros((1, 3, 3)))
    result = problem.mode(.3, 1, [1.4])
    # A global clock change sends frequency to c*frequency and each
    # Green moment to moment/c; the integrated physical stress is fixed.
    c = 2.7
    changed = SmoothRadialProblem(problem.coordinate, problem.radius, c*problem.lapse,
        problem.radial_scale, c*problem.links, problem.mass_squared, problem.probes)
    assert np.allclose(c*changed.mode(c*.3, 1, [1.4]), result, rtol=2e-10, atol=1e-19)


def test_joined_profile_matches_fields_geometry_and_uses_actual_conversion():
    profile = JoinedProfile(ROOT)
    eps = 1e-6
    values = np.array(profile.values(np.array([profile.cut-eps, profile.cut+eps])))
    assert np.allclose(values[:, 0], values[:, 1], rtol=1e-6)
    assert abs(np.diff(profile.higgs(np.array([profile.cut-eps, profile.cut+eps])))[0]) < 1e-13
    x = profile.retained.negative_branch_coordinate(np.linspace(2.18, 6.2, 65))
    assert np.all(profile.mass_squared(x, 1.4) == 0)
    assert profile.eta == pytest.approx(2.4127904527582454e-5)
    jump = join_curvature(profile)
    assert abs(jump['outside_tensor'][1]-jump['inside_tensor'][1]) < 1e-12
    assert jump['ricci_jump_outside_minus_inside'][-1] > .008


@pytest.mark.parametrize('cosine', [0., .4, 1.])
def test_quadratic_metric_born_reflection_matches_direct_integral(cosine):
    a, b, k, scale = -.0013, -.0015, 3., .8
    def potential(z):
        exponential = np.exp(-z/scale)
        second = exponential*(2-4*z/scale+z*z/scale**2)
        return ((b/2+a/4)*second-k*k*(a*cosine**2+b*(1-cosine**2))*z*z*exponential)
    direct = -quad(lambda z: np.exp(-2*k*z)*potential(z), 0, np.inf,
                   epsabs=1e-16)[0]/(2*k)
    assert local_born_reflection(k, cosine, a, b, scale) == pytest.approx(direct, rel=2e-12)
    high = 1e7
    coefficient = -((1-cosine**2)*a+(1+cosine**2)*b)/8
    assert high**2*local_born_reflection(high, cosine, a, b, scale) == pytest.approx(coefficient, rel=1e-6)


def test_junction_tensor_follows_angular_moments_and_trace_identity():
    profile = JoinedProfile(ROOT)
    jump = join_curvature(profile)
    result = junction_asymptote(jump['inside_tensor'], jump['outside_tensor'])
    a, b = result['lapse_second_jump'], result['radius_second_over_radius_jump']
    c, w = leggauss(24)
    q = (1-c*c)*a+(1+c*c)*b
    moments = np.array([np.sum(w*c*c*q), -np.sum(w*q), -np.sum(w*(1-c*c)*q)/2])/(256*np.pi**2)
    at, radial, angular = moments
    tensor = np.array([(at+radial+2*angular)/2, (at+radial-2*angular)/2,
        (at-radial)/2, at+radial, at+angular])
    assert np.allclose(tensor, result['tensor_d_minus_2'], rtol=1e-12, atol=1e-21)
    rho, pr, pt = tensor[:3]
    assert -rho+pr+2*pt == pytest.approx(-result['ricci_scalar_jump']/(192*np.pi**2))
    assert rho > 0 and tensor[-1] < 0
    assert result['ricci_scalar_jump'] == pytest.approx(jump['ricci_jump_outside_minus_inside'][-1], rel=1e-9)


def test_smooth_join_has_zero_curvature_step_term():
    tensor = np.array([.001, -.0003, .0004])
    result = junction_asymptote(tensor, tensor)
    assert np.array_equal(result['tensor_d_minus_2'], np.zeros(5))
