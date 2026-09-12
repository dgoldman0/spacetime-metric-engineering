import numpy as np
from numpy.testing import assert_allclose
import pytest

from adm_harness.virtual_cell_thermal_exchange import thermal_exchange_problem,solve_thermal_exchange


def test_counted_pressureless_store_can_supply_and_recover_phase_energy():
    one=np.ones(3);zero=np.zeros(3);phase=np.array([0.,.2,0.])
    result=solve_thermal_exchange(.3*one,.1-phase,zero,zero,one,one,one[:-1],one[:-1],
        w=0.,fixed_amplitude=phase,radiation_floor=.1*one)
    assert_allclose(result['density_allowance'],0.,atol=1e-10)
    assert_allclose(result['amplitude'],phase,atol=1e-13)
    assert_allclose(result['radiation_density'],.1,atol=1e-9)
    assert_allclose(result['thermal_density'],[.2,0.,.2],atol=1e-9)
    assert result['maximum_equality_residual']<1e-10


def test_counted_store_cannot_hide_energy_after_target_capacity_disappears():
    rho=np.array([1.,0.]);p=np.array([-1.,0.]);zero=np.zeros(2);one=np.ones(2)
    args=(rho,p,zero,zero,one,one,np.ones(1),np.ones(1))
    result=solve_thermal_exchange(*args,w=0.,fixed_amplitude=rho)
    assert_allclose(result['density_allowance'],1.,atol=1e-9)
    assert_allclose(result['dual_lower_bound'],1.,atol=1e-9)
    problem=thermal_exchange_problem(*args,w=0.,fixed_amplitude=rho)
    reduced=problem['cost']-problem['inequality'].T@result['dual_inequality']-\
        problem['equality'].T@result['dual_equality']
    bound=problem['rhs']@result['dual_inequality']+np.maximum(reduced,0.)@problem['lower']+\
        np.minimum(reduced,0.)@problem['upper']
    assert_allclose(bound,result['dual_lower_bound'],atol=1e-13)
    competitor=problem['feasible_competitor']
    assert np.max(problem['inequality']@competitor-problem['rhs'])<=1e-10
    assert_allclose(problem['equality']@competitor,0.,atol=1e-13)


def test_joint_phase_relaxation_differs_from_fixed_phase_storage():
    rho=np.array([1.,0.]);zero=np.zeros(2);one=np.ones(2)
    args=(rho,zero,zero,zero,one,one,np.ones(1),np.ones(1))
    fixed=solve_thermal_exchange(*args,w=0.,fixed_amplitude=np.array([.4,0.]))
    free=solve_thermal_exchange(*args,w=0.)
    assert fixed['dual_lower_bound']>.1
    assert_allclose(free['density_allowance'],0.,atol=1e-10)
    assert fixed['fixed_amplitude'] and not free['fixed_amplitude']


def test_isotropic_radiation_reservoir_pays_its_full_stress():
    one=np.ones(3);zero=np.zeros(3)
    problem=thermal_exchange_problem(.2*one,one/15,one/15,zero,one,one,
        one[:-1],one[:-1],w=1/3)
    inventory=np.r_[zero,zero,.2*one,0.]
    assert_allclose(problem['inequality']@inventory-problem['rhs'],0.,atol=1e-15)
    assert_allclose(problem['equality']@inventory,0.,atol=1e-15)


def test_panel_law_contains_weighted_material_storage():
    one=np.ones(3);zero=np.zeros(3)
    problem=thermal_exchange_problem(100*one,zero,zero,zero,one,one,
        np.array([2.,3.]),np.array([.5,.25]),w=0.)
    inventory=np.r_[[1.,2.,1.],[5.,5.,5.],[10.,6.,18.],0.]
    assert_allclose(problem['equality']@inventory,0.,atol=1e-14)


def test_thread_and_reservoir_arguments_are_checked_before_solve():
    one=np.ones(3);zero=np.zeros(3)
    args=(one,zero,zero,zero,one,one,one[:-1],one[:-1])
    for invalid in (0,-1,True,1.5):
        with pytest.raises(ValueError,match='solver_threads'):
            solve_thermal_exchange(*args,w=0.,solver_threads=invalid)
    with pytest.raises(ValueError,match='w must'):
        thermal_exchange_problem(*args,w=.2)
    with pytest.raises(ValueError,match='radiation_floor'):
        thermal_exchange_problem(*args,w=0.,radiation_floor=-one)


def test_monotone_angular_reservoir_accepts_radial_isotropization():
    one=np.ones(3);zero=np.zeros(3)
    radial=np.array([.2,.15,.1]);angular=np.array([0.,.05,.1])
    result=solve_thermal_exchange(.2*one,radial+angular/3,angular/3,zero,
        one,one,one[:-1],one[:-1],w=1/3,fixed_amplitude=zero,
        radiation_floor=radial,monotone_thermal=True)
    assert_allclose(result['density_allowance'],0.,atol=1e-10)
    assert result['maximum_thermal_monotonicity_violation']<1e-10
    assert result['maximum_equality_residual']<1e-10


def test_monotone_reservoir_rejects_required_thermal_depletion_and_has_valid_competitor():
    one=np.ones(3);zero=np.zeros(3);phase=np.array([0.,.2,0.])
    thermal=np.array([.2,0.,.2]);radial=.1*one
    args=(.3*one,-phase+radial+thermal/3,thermal/3,zero,one,one,one[:-1],one[:-1])
    kwargs=dict(w=1/3,fixed_amplitude=phase,radiation_floor=radial)
    unrestricted=solve_thermal_exchange(*args,**kwargs)
    monotone=solve_thermal_exchange(*args,**kwargs,monotone_thermal=True)
    assert_allclose(unrestricted['density_allowance'],0.,atol=1e-10)
    assert monotone['dual_lower_bound']>.01
    problem=thermal_exchange_problem(*args,**kwargs,monotone_thermal=True)
    competitor=problem['feasible_competitor']
    assert np.max(problem['inequality']@competitor-problem['rhs'])<=1e-10
    assert_allclose(problem['equality']@competitor,0.,atol=1e-13)
    assert np.all(competitor>=problem['lower']-1e-13)
    assert np.all(competitor<=problem['upper']+1e-13)
    reduced=problem['cost']-problem['inequality'].T@monotone['dual_inequality']-\
        problem['equality'].T@monotone['dual_equality']
    dual=problem['rhs']@monotone['dual_inequality']+np.maximum(reduced,0.)@problem['lower']+\
        np.minimum(reduced,0.)@problem['upper']
    assert_allclose(dual,monotone['dual_lower_bound'],atol=1e-13)
