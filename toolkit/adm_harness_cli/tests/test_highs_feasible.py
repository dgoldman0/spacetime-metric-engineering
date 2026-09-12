"""Native feasible-primal retention is independent of backend status claims."""
from types import SimpleNamespace

import numpy as np
from numpy.testing import assert_allclose
import pytest
from scipy.optimize import linprog
from scipy.sparse import csr_matrix

from adm_harness.highs_feasible import (checked_highs_result, linprog_feasible,
                                      verify_candidate)


def test_native_optimum_preserves_original_objective_rows_bounds_and_options():
    # Initializing the ordinary scheduler first must remain harmless when no
    # explicit thread override is requested by this process.
    assert linprog([1.], bounds=[(0., 1.)]).success
    c=np.array([1.,2.]);au=csr_matrix([[-1.,0.]]);bu=np.array([-1.])
    ae=csr_matrix([[1.,1.]]);be=np.array([3.])
    result=linprog_feasible(c,A_ub=au,b_ub=bu,A_eq=ae,b_eq=be,
        bounds=[(0.,2.),(None,None)],options=dict(presolve=False,run_crossover=False,
        small_matrix_value=1e-12,ipm_optimality_tolerance=1e-10))
    assert result.success and result.optimality_certified
    assert_allclose(result.x,[2.,1.],atol=2e-7)
    assert_allclose(result.fun,c@result.x,atol=0.)
    assert_allclose(result.con,be-ae@result.x,atol=0.)
    assert_allclose(result.slack,bu-au@result.x,atol=0.)
    assert result.maximum_feasibility_violation<=2e-7
    assert result.crossover_nit==0
    assert result.backend_run_ok and result.backend_run_status==0


def test_forged_optimal_backend_claim_cannot_hide_original_row_violation():
    result=checked_highs_result([1.,1.],[0.,0.],value_valid=True,backend_status='Optimal',
        A_eq=[[1.,1.]],b_eq=[1.])
    assert not result.success and result.x is None
    assert not result.optimality_certified
    assert result.equality_residual==1.


@pytest.mark.parametrize('status',['Unknown','Time limit reached','Iteration limit reached'])
def test_verified_nonoptimal_candidate_is_retained_without_claiming_optimality(status):
    # x=2 is feasible but x=1 has a smaller objective; no timeout is needed to
    # exercise the native-result boundary and its independent verification.
    result=checked_highs_result([1.],[2.],value_valid=True,backend_status=status,
        A_ub=[[-1.]],b_ub=[-1.],bounds=[(0.,3.)])
    assert result.success and result.feasibility_only_success
    assert not result.optimality_certified
    assert_allclose(result.x,[2.])
    assert result.fun==2. and result.backend_model_status==status


def test_bounds_and_native_value_valid_are_both_required():
    violation=checked_highs_result([1.],[1.+3e-7],value_valid=True,backend_status='Unknown',
        bounds=[(0.,1.)])
    assert not violation.success and violation.upper_bound_violation>2e-7
    invalid=checked_highs_result([1.],[.5],value_valid=False,backend_status='Unknown',bounds=[(0.,1.)])
    assert invalid.verified_feasible and not invalid.success
    assert invalid.x is None
    fixed=verify_candidate([1.,1.],[.5,1e-6],bounds=[(0.,1.),(0.,0.)])
    assert not fixed.verified_feasible and fixed.upper_bound_violation==1e-6


@pytest.mark.parametrize('status',['Optimal','Unknown','Time limit reached'])
def test_backend_run_error_rejects_even_a_valid_feasible_candidate(status):
    result=checked_highs_result([1.],[.5],value_valid=True,backend_status=status,
        bounds=[(0.,1.)],backend_run_ok=False,backend_run_status=-1)
    assert result.verified_feasible and result.backend_value_valid
    assert not result.success and result.x is None and result.status==4
    assert not result.optimality_certified and not result.feasibility_only_success
    assert not result.backend_run_ok and result.backend_run_status==-1
    assert result.backend_model_status==status


@pytest.mark.parametrize('error_stage',['load','run'])
def test_native_load_and_run_errors_reach_the_retention_gate(monkeypatch,error_stage):
    from scipy.optimize._highspy import _core as core
    calls=[]
    error,ok=core.HighsStatus.kError,core.HighsStatus.kOk
    def run():
        calls.append('run')
        return error if error_stage=='run' else ok
    backend=SimpleNamespace(
        setOptionValue=lambda key,value:ok,
        passModel=lambda lp:error if error_stage=='load' else ok,
        run=run,getModelStatus=lambda:core.HighsModelStatus.kOptimal,
        modelStatusToString=lambda status:'Optimal',version=lambda:'test',
        getSolution=lambda:SimpleNamespace(col_value=[.5],value_valid=True,dual_valid=False),
        getInfo=lambda:SimpleNamespace(ipm_iteration_count=1,simplex_iteration_count=0,
            crossover_iteration_count=0,valid=True,max_primal_infeasibility=0.,
            max_dual_infeasibility=0.))
    monkeypatch.setattr(core,'_Highs',lambda:backend)
    result=linprog_feasible([1.],bounds=[(0.,1.)])
    assert result.verified_feasible and result.backend_value_valid
    assert not result.success and result.status==4 and result.x is None
    assert not result.backend_run_ok
    assert result.backend_run_status==int(error)
    assert result.backend_load_status==int(error if error_stage=='load' else ok)
    assert calls==([] if error_stage=='load' else ['run'])


def test_verification_uses_small_original_coefficients_and_rejects_nonfinite_candidates():
    # A solver may drop this coefficient; its finite product remains part of
    # the original physical constraint and must still be checked.
    result=verify_candidate([0.],[1e12],A_eq=csr_matrix([[1e-12]]),b_eq=[0.])
    assert result.equality_residual==1. and not result.verified_feasible
    for x in ([np.nan],[np.inf],[]):
        assert not verify_candidate([1.],x).verified_feasible


def test_native_adapter_rejects_invalid_options_and_never_repurposes_thread_scheduler():
    with pytest.raises(ValueError,match='threads'):
        linprog_feasible([1.],options={'threads':True})
    with pytest.raises(ValueError,match='rejected option'):
        linprog_feasible([1.],options={'not_a_highs_option':1})
    with pytest.raises(ValueError,match='bounds'):
        linprog_feasible([1.],bounds=[(2.,1.)])
    with pytest.raises(ValueError,match='at most'):
        verify_candidate([1.],[0.],feasibility_tolerance=1e-6)
    with pytest.raises(ValueError,match='backend_run_ok'):
        checked_highs_result([1.],[0.],value_valid=True,backend_status='Optimal',backend_run_ok='false')
