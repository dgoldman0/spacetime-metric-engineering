import numpy as np
from scipy.optimize import linprog

from adm_harness.cutting_plane_lp import solve_with_cuts


def test_generated_constraints_recover_full_program():
    rng=np.random.default_rng(21)
    a=rng.normal(size=(130,4));b=.2+rng.random(130)
    cost=np.array([1.,-.3,.7,-.1]);bounds=[(-3.,3.)]*4
    reference=linprog(cost,A_ub=a,b_ub=b,bounds=bounds,method='highs')
    result=solve_with_cuts(cost,a,b,bounds,initial_count=5,add_count=8)
    assert reference.success and result.success
    assert len(result.cut_history)>1
    np.testing.assert_allclose(result.fun,reference.fun,atol=1e-8)
    assert (a@result.x-b).max()<2e-8


def test_infeasible_subset_certifies_full_infeasibility():
    a=np.ones((40,1));b=np.ones(40)
    a[7,0]=-1.;b[7]=-2.
    result=solve_with_cuts(np.array([1.]),a,b,[(0.,3.)],initial_count=3,add_count=5)
    assert not result.success and result.status==2
