"""Original-row tests for a shared phase across otherwise local bank blocks."""
from pathlib import Path
import sys

import numpy as np
from numpy.testing import assert_allclose
import pytest
from scipy.optimize import OptimizeResult
from scipy.sparse import block_diag

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import run_virtual_cell_local_bank_relaxation as local
import run_virtual_cell_shared_phase_local as shared


def make_block(*,pressure=None,ell=1.,radius=1.):
    t=np.linspace(0,1,5);tm=(t[:-1]+t[1:])/2;D=ell*radius**2
    geometry=lambda n:{'radius':np.full(n,radius),'ell':np.full(n,ell),'D':np.full(n,D)}
    if pressure is None:
        target=np.array([np.full(len(t),2.),np.zeros(len(t)),np.zeros(len(t))])
        floor=.01;U0=.5+.1*t;U0m=.5+.1*tm;Z0=.2+.02*t;Z0m=.2+.02*tm
        capacity=1.;loss=.04*np.diff(t)
    else:
        target=np.array([np.ones(len(t)),np.full(len(t),pressure),np.zeros(len(t))])
        floor=0.;U0=Z0=np.zeros(len(t));U0m=Z0m=np.zeros(len(tm));capacity=0.;loss=np.zeros(len(tm))
    return local.solve_local(t,target,(target[:,:-1]+target[:,1:])/2,
        geometry(len(t)),geometry(len(tm)),reference_thermal_energy=U0,
        midpoint_reference_thermal_energy=U0m,reference_receiver_energy=Z0,
        midpoint_reference_receiver_energy=Z0m,cold_mass=.4,receiver_capacity=capacity,
        converter_loss=loss,temperature_floor=floor,proper_duration=np.diff(t),hot_donor_turnover=10.)


def test_compatible_local_blocks_keep_raw_rows_bounds_and_credits():
    first,a=make_block();second,b=make_block(ell=2.,radius=3.)
    assert first['success'] and second['success']
    summary,state=shared.solve_shared_phase([a,b,a,b])
    assert summary['success'] and summary['original_lp_rows_and_bounds_verified']
    assert summary['shared_phase_residual']<1e-9
    assert all(check['verified_feasible'] for check in summary['joint_candidate_original_local_checks'])
    expected_eq=block_diag([shared.raw_matrix(s,'equality') for s in [a,b,a,b]],format='csr')
    expected_ub=block_diag([shared.raw_matrix(s,'inequality') for s in [a,b,a,b]],format='csr')
    actual_eq=shared.raw_matrix(state,'equality');actual_ub=shared.raw_matrix(state,'inequality')
    assert (actual_eq[:expected_eq.shape[0]]!=expected_eq).nnz==0
    assert (actual_ub!=expected_ub).nnz==0
    assert summary['shared_phase_equalities']==3*len(a['t'])
    assert_allclose(state['lp_equality_rhs'][:expected_eq.shape[0]],
                    np.concatenate([s['lp_equality_rhs'] for s in [a,b,a,b]]),atol=0,rtol=0)
    assert_allclose(state['lp_inequality_rhs'],np.concatenate([s['lp_inequality_rhs'] for s in [a,b,a,b]]),atol=0,rtol=0)
    assert_allclose(state['lp_lower_bound'],np.concatenate([s['lp_lower_bound'] for s in [a,b,a,b]]),atol=0,rtol=0)
    assert_allclose(state['lp_upper_bound'],np.concatenate([s['lp_upper_bound'] for s in [a,b,a,b]]),atol=0,rtol=0)
    assert not state['lp_cost'].any()
    for j,original in enumerate([a,b,a,b]):
        for key in ('credited_target','midpoint_credited_target','original_power_panel',
                    'receiver_fixed_containment_energy','lp_x'):
            assert_allclose(state[f'local{j}_'+key],original[key],atol=0,rtol=0)
    assert any('hot_donor_endpoint' in label for label in state['lp_inequality_labels'])
    assert not any('cold_fluid_donor' in label for label in state['lp_inequality_labels'])
    assert summary['added_density']==0 and summary['reserved_density_fraction']==0


def test_independently_feasible_stress_targets_can_reject_common_phase():
    # rho=1, pr=-1 forces A=1, while rho=1, pr=+1 forces A=0.
    # Each static local target is feasible with zero bank and thermal energy.
    left,a=make_block(pressure=-1.)
    right,b=make_block(pressure=1.)
    assert left['success'] and right['success']
    assert_allclose(a['amplitude'],1.,atol=1e-10)
    assert_allclose(b['amplitude'],0.,atol=1e-10)
    joint,state=shared.solve_shared_phase([a,b])
    assert not joint['success'] and joint['status']==2
    assert not joint['infeasibility_independently_certified']
    assert state['shared_phase_rows']==len(a['t'])


def test_original_coherence_rows_reject_a_forged_optimal_claim(monkeypatch):
    _,a=make_block(pressure=-1.);_,b=make_block(pressure=1.)
    candidate=np.r_[a['lp_x'],b['lp_x']]
    monkeypatch.setattr(shared,'linprog',lambda *args,**kwargs:
        OptimizeResult(success=True,status=0,message='forged optimal claim',nit=0,x=candidate))
    summary,state=shared.solve_shared_phase([a,b])
    assert summary['ordinary_solver_success'] and not summary['success']
    assert not summary['original_lp_rows_and_bounds_verified']
    assert summary['equality_residual']>=1.-1e-10
    assert summary['shared_phase_residual']>=1.-1e-10
    assert all(check['verified_feasible'] for check in summary['joint_candidate_original_local_checks'])
    assert_allclose(state['lp_x'],candidate)


def test_original_local_floor_and_bounds_still_reject_forged_joint_states(monkeypatch):
    _,a=make_block()
    candidate=np.zeros(2*len(a['lp_cost']))
    monkeypatch.setattr(shared,'linprog',lambda *args,**kwargs:
        OptimizeResult(success=True,status=0,message='forged zero state',nit=0,x=candidate))
    summary,_=shared.solve_shared_phase([a,a])
    assert not summary['success'] and summary['inequality_violation']>0
    assert summary['shared_phase_residual']==0
    assert not all(check['verified_feasible'] for check in summary['joint_candidate_original_local_checks'])
    candidate[-1]=-.001
    summary,_=shared.solve_shared_phase([a,a])
    assert summary['lower_bound_violation']>=.001 and not summary['success']


def test_shared_gate_requires_compatible_blocks_and_bounded_time():
    _,a=make_block()
    for deadline in (0.,61.,float('nan')):
        with pytest.raises(ValueError,match='deadline'):
            shared.solve_shared_phase([a,a],deadline=deadline)
    with pytest.raises(ValueError,match='at least two'):
        shared.solve_shared_phase([a])
    with pytest.raises(ValueError,match='identical local time'):
        shared.solve_shared_phase([a,dict(a,t=a['t']+.001)])
    with pytest.raises(ValueError,match='zero-cost'):
        shared.solve_shared_phase([a,dict(a,lp_cost=np.ones(len(a['lp_cost'])))])
