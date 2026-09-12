import numpy as np
from numpy.testing import assert_allclose

from evaluate_composite_pressure_allocation import bounded_drop_witness


def test_hydrostatic_pressure_budget_reproduces_uniform_slab_limit():
    x=np.linspace(0,2,81)
    result=bounded_drop_witness(x,np.zeros_like(x),np.ones_like(x),np.full_like(x,.75),np.ones_like(x,dtype=bool))
    assert_allclose(result['required_pressure_drop'],1.5)
    assert_allclose(result['maximum_available_pressure_drop'],1.)
    assert_allclose(result['gap'],.5)
    assert_allclose([result['left_x'],result['right_x']],[0,2])


def test_exact_hydrostatic_profile_satisfies_all_pairwise_drop_bounds():
    x=np.linspace(0,1,81)
    pressure=2-x-x*x/2
    result=bounded_drop_witness(x,pressure,pressure,1+x,np.ones_like(x,dtype=bool))
    assert result['gap']<1e-13


def test_disconnected_acceleration_domains_keep_independent_pressure_budgets():
    x=np.linspace(0,3,301)
    mask=(x<1)|(x>2)
    result=bounded_drop_witness(x,np.zeros_like(x),np.ones_like(x),np.ones_like(x),mask)
    assert result['gap']<=1e-12
