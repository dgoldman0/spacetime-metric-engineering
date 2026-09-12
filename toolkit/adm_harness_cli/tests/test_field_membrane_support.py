import numpy as np
from scipy.optimize import linprog

from adm_harness.field_membrane_support import minimum_energy, decompose


def test_energy_cone_against_independent_component_program():
    rng = np.random.default_rng(19)
    basis = np.array([[-1.,1.,0.,0.,0.],[1.,0.,.5,-1.,0.]])
    for p, q in rng.normal(size=(20,2)):
        result = linprog(np.ones(5), A_eq=basis, b_eq=[p,q], bounds=(0.,None), method='highs')
        assert result.success
        np.testing.assert_allclose(minimum_energy(p,q),result.fun,atol=1e-10)
        rho = minimum_energy(p,q)+.2
        values = decompose(rho,p,q)
        assert values.min() >= -1e-12
        np.testing.assert_allclose(basis@values,[p,q],atol=1e-12)
        np.testing.assert_allclose(values.sum(),rho)


def test_radial_tension_pays_for_angular_field_reaction():
    assert minimum_energy(-1.,0.) == 2.
    np.testing.assert_array_equal(decompose(2.,-1.,0.),[1.,0.,0.,1.,0.])
