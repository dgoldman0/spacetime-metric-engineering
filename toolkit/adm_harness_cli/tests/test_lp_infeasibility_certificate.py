import numpy as np
from adm_harness.lp_infeasibility_certificate import certificate


def test_nonnegative_combination_proves_contradiction():
    result=certificate(np.array([[1.],[-1.]]),np.array([1.,-2.]),[(None,None)])
    assert result['valid']
    np.testing.assert_allclose(result['matrix'].T@result['weights'],0.,atol=1e-12)
    assert result['rhs']@result['weights']<0


def test_bounds_count_and_feasible_problem_has_no_certificate():
    assert certificate(np.array([[-1.]]),np.array([-2.]),[(0.,1.)])['valid']
    assert not certificate(np.array([[-1.]]),np.array([0.]),[(0.,1.)])['valid']
