"""Independent continuous amplitude optimization and interval equivalence."""
import numpy as np
from numpy.testing import assert_allclose
from scipy.optimize import differential_evolution

from adm_harness.driven_condensate_cells import (
    controller_energy, core_height_interval, loaded_minimum_energy,
    two_cell_phase_inventory,
)
from adm_harness.field_membrane_support import minimum_energy as auxiliary_energy
from adm_harness.scalar_flux_support import BASIS


def test_complete_scalar_energy_counts_equilibrium_controller():
    z = np.linspace(0, 1, 23)
    h = 1.7
    v = h*(1-z)**2
    interaction = 2*h*z*(1-z)
    assert_allclose(controller_energy(v, h), v+2*interaction, atol=2e-15)
    assert_allclose(controller_energy(np.array([0., h]), h), [0., h])


def test_amplitude_minimum_matches_independent_global_optimizer():
    rng = np.random.default_rng(92012)
    for p, q, h in np.column_stack([rng.uniform(-2, 2, (30, 2)), rng.uniform(.05, 3, 30)]):
        exact, v = loaded_minimum_energy(p, q, h)
        def cost(a):
            vv = float(a[0])
            return float(controller_energy(vv, h)+auxiliary_energy(p+vv, q+vv))
        r = differential_evolution(cost, [(0, h)], seed=823, tol=1e-10, polish=True)
        independent = min(r.fun, cost([0]), cost([h]))
        assert_allclose(exact, independent, atol=2e-8)
        assert_allclose(exact, cost([v]), atol=2e-12)


def test_height_interval_matches_independent_fixed_height_minima():
    rng = np.random.default_rng(31512)
    for unused in range(40):
        target = BASIS@rng.uniform(.01, 1, 6)
        lo, hi = core_height_interval(*target)
        heights = np.r_[np.geomspace(.0001, 100, 75), lo*.999, lo*1.001]
        if np.isfinite(hi):
            heights = np.r_[heights, hi*.999, hi*1.001]
        need, unused = loaded_minimum_energy(target[1], target[2], heights)
        assert np.array_equal(need <= target[0]+1e-12, (heights >= lo-1e-12)&(heights <= hi+1e-12))


def test_shared_reservoir_counts_recovery_and_converter_loss():
    t = np.linspace(0, 2, 101)
    p = np.column_stack([np.ones_like(t), -np.ones_like(t)])
    m = np.column_stack([1+t, 3-t])
    ideal = two_cell_phase_inventory(t, m, p)
    assert_allclose(ideal['reservoir_energy'], 0, atol=1e-15)
    loss = two_cell_phase_inventory(t, m, p, efficiency=.8)
    assert_allclose(loss['initial_energy'], 2*(1/.8-.8), atol=1e-14)
