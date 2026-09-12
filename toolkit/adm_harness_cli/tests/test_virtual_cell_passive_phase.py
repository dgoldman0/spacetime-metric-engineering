import numpy as np
from numpy.testing import assert_allclose

from adm_harness.virtual_cell_passive_phase import passive_phase_problem, solve_passive_phase


def test_static_positive_material_and_prepared_phase_are_feasible():
    n=5;one=np.ones(n);zero=np.zeros(n)
    result=solve_passive_phase(one,-.2*one,.1*one,zero,one,one,one[:-1])
    assert_allclose(result['density_allowance'],0.,atol=1e-10)
    assert result['maximum_equality_residual']<1e-10
    assert result['maximum_inequality_violation']<1e-10
    assert abs(result['primal_dual_gap'])<1e-9


def test_two_instantaneously_feasible_states_require_energy_exchange():
    # Flat geometry conserves A+U. Initial negative radial pressure needs
    # A>=1; the final rho=0 target permits A=U=0. Each isolated time fits.
    rho=np.array([1.,0.]);p=np.array([-1.,0.]);zero=np.zeros(2);one=np.ones(2)
    result=solve_passive_phase(rho,p,zero,zero,one,one,np.ones(1))
    assert result['density_allowance']>.1
    assert result['dual_lower_bound']>.1
    assert_allclose(result['density_allowance'],.5,atol=1e-9)
    assert result['primal_dual_gap']<1e-8
    problem=passive_phase_problem(rho,p,zero,zero,one,one,np.ones(1))
    reproduced=problem['rhs']@result['dual_inequality']+np.minimum(
        problem['cost']-problem['inequality'].T@result['dual_inequality']-
        problem['equality'].T@result['dual_equality'],0.)@problem['upper']
    assert_allclose(reproduced,result['dual_lower_bound'],atol=1e-13)


def test_panel_law_uses_mean_geometry_and_correct_sign():
    n=3;one=np.ones(n);zero=np.zeros(n)
    problem=passive_phase_problem(10*one,zero,zero,zero,one,one,np.array([2.,3.]))
    amplitude=np.array([1.,2.,1.]);inventory=np.array([5.,3.,6.])
    assert_allclose(problem['equality']@np.r_[amplitude,inventory,0.],0.)
