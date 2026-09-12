"""Independent convex programs and physically controlled tube histories."""
import numpy as np
from numpy.testing import assert_allclose
from scipy.optimize import linprog, minimize_scalar

from adm_harness.field_membrane_support import minimum_energy as old_energy
from adm_harness.scalar_flux_support import (
    BASIS, bag_invariant_interval, decompose, equilibrium_vortex_interval,
    invariant_summary, minimum_energy, potential_interval,
)


def test_cone_matches_independent_component_linear_programs():
    rng = np.random.default_rng(8271)
    for p, q in rng.uniform(-3., 3., (60, 2)):
        result = linprog(np.ones(6), A_eq=BASIS[1:], b_eq=[p, q],
                         bounds=(0., None), method='highs')
        assert result.success
        assert_allclose(result.fun, minimum_energy(p, q), atol=2e-12)
        rho = result.fun+.13
        components = decompose(rho, p, q)
        assert components.min() >= -2e-12
        assert_allclose(BASIS@components, [rho, p, q], atol=2e-12)


def test_conserved_vortex_interval_matches_full_component_program():
    rng = np.random.default_rng(665)
    basis = np.column_stack([BASIS[:, [0, 2, 3, 4, 5]], [1., -1., 0.]])
    for unused in range(30):
        target = basis@rng.uniform(.01, 2., 6)
        radius = rng.uniform(.3, 3.)
        lo, hi = equilibrium_vortex_interval(*target, radius)
        for sign, expected in [(1., lo), (-1., hi)]:
            cost = np.zeros(6); cost[-1] = sign*radius**2
            result = linprog(cost, A_eq=basis, b_eq=target, bounds=(0., None))
            assert result.success
            assert_allclose(sign*result.fun, expected, atol=2e-12)


def test_bag_product_bounds_against_independent_scalar_optimization():
    rng = np.random.default_rng(455)
    for unused in range(40):
        target = BASIS@rng.uniform(.02, 2., 6)
        rho, p, q = target; radius = rng.uniform(.5, 2.)
        vl, vh = potential_interval(*target)
        low, high = bag_invariant_interval(*target, radius)
        # Optimize E*V on every feasible polygon edge, independently of the
        # stationary point used by the analytic product-bound function.
        upper = minimize_scalar(lambda v: -v*(rho-p+q-v)/3,
                                bounds=(vl, vh), method='bounded')
        maximum = max(-upper.fun, vl*(rho-p+q-vl)/3, vh*(rho-p+q-vh)/3)
        points = np.r_[np.linspace(vl, vh, 2001), np.clip(-p, vl, vh)]
        minimum = np.min(points*np.maximum(0., -p-points))
        assert_allclose(high**2/(4*radius**4), maximum, rtol=1e-8, atol=1e-12)
        assert_allclose(low**2/(4*radius**4), minimum, atol=1e-12)


def test_expanding_equilibrium_and_squeezed_bag_controls():
    t = np.linspace(0., 1., 7); x = np.linspace(-2., -.5, 9)
    radius = 2.+.2*t[:, None]+.1*x[None, :]
    amplitude = 1.7
    density = amplitude/radius**2
    lo, hi = equilibrium_vortex_interval(density, -density, 0., radius)
    assert_allclose(lo, amplitude); assert_allclose(hi, amplitude)
    area = np.exp(.3*np.sin(2*t[:, None]+x[None, :]))
    field = amplitude/(2*radius**2*area)
    potential = amplitude*area/(2*radius**2)
    rho, p, q = field+potential, -field-potential, field-potential
    lo, hi = bag_invariant_interval(rho, p, q, radius)
    assert_allclose(lo, amplitude, atol=1e-12)
    assert_allclose(hi, amplitude, atol=1e-12)


def test_missing_potential_and_time_varying_population_are_detected():
    assert old_energy(-1., 0.) == 2.
    assert minimum_energy(-1., 0.) == 1.
    amplitude = np.array([[1., 1.], [2., 2.]])
    lo, hi = equilibrium_vortex_interval(amplitude, -amplitude, 0., 1.)
    result = invariant_summary(lo, hi, [0., 1.], [-1., 1.])
    assert result['local_intervals_nonempty']
    assert not result['common_invariant_feasible']
    assert not result['static_spatial_grading_feasible']
    assert result['positions_requiring_time_variation'] == 2
