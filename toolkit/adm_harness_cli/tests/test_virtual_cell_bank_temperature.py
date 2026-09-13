import importlib.util
from pathlib import Path
import sys

import numpy as np
from numpy.testing import assert_allclose

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
spec=importlib.util.spec_from_file_location('bank_temperature',SCRIPTS/'audit_virtual_cell_bank_temperature.py')
bank=importlib.util.module_from_spec(spec);spec.loader.exec_module(bank)


def limits(result):
    return {key:float(result[key].max() if key.startswith('L') else result[key].min())
            for key in ('Lf','Uf','Lg','Ug')}


def test_absent_fluid_cold_branch_places_no_fluid_temperature_bound_on_cold_bank():
    one=np.ones((2,1));zero=one*0
    r=bank.joint_temperature_bounds(zero,zero,np.array([[1.],[0.]]),np.array([[0.],[1.]]),
                                   .01*one,one,one,one,one)
    assert r['state_valid'].all() and np.isinf(r['Uf'][0])
    chosen=bank.choose_joint_coefficients(**limits(r))
    assert chosen['selection_possible']
    assert chosen['selected_cold_coefficient']**.25>.01
    assert_allclose(chosen['contrast_infimum'],1.)


def test_joint_photon_constraint_requires_larger_contrast_than_fluid_alone():
    one=np.ones((4,1));zero=one*0
    branches=[zero.copy() for _ in range(4)]
    for i in range(4):branches[i][i]=1.
    theta=np.array([[4**.25],[1.],[1.],[1.]])
    density=np.array([[1.],[1.],[10.],[1.]])
    r=bank.joint_temperature_bounds(*branches,theta,one,one,density,one)
    assert r['state_valid'].all()
    chosen=bank.choose_joint_coefficients(**limits(r))
    assert chosen['selection_possible']
    assert_allclose(chosen['fluid_contrast_infimum'],4.)
    assert_allclose(chosen['photon_contrast_infimum'],100.)
    assert_allclose(chosen['selected_cold_to_hot_volume_ratio'],400.)
    ah,ac,a2=[chosen[k] for k in ('selected_hot_coefficient','selected_cold_coefficient','selected_channel_coefficient')]
    assert ah>4 and ac<1 and ah*a2*a2>100 and ac*a2*a2<1
    # The fluid-only safety contrast 16 cannot meet the photon ratio >100.
    assert 4*chosen['fluid_contrast_infimum']<chosen['photon_contrast_infimum']


def test_empty_active_donors_reject_but_empty_cold_bank_can_receive():
    one=np.ones((1,1));zero=one*0
    empty_photon=bank.joint_temperature_bounds(zero,zero,zero,one,one,one,one,zero,one)
    assert not empty_photon['state_valid'][0] and empty_photon['forbidden_photon_cold'][0,0]
    empty_hot=bank.joint_temperature_bounds(one,zero,zero,zero,one,zero,one,one,one)
    assert not empty_hot['state_valid'][0] and empty_hot['forbidden_hot_emission'][0,0]
    empty_fluid=bank.joint_temperature_bounds(zero,one,zero,zero,zero,one,one,one,one)
    assert not empty_fluid['state_valid'][0]
    receiving=bank.joint_temperature_bounds(zero,zero,zero,one,one,one,zero,one,one)
    assert receiving['state_valid'][0] and np.isinf(receiving['Ug'][0])
    assert bank.choose_joint_coefficients(**limits(receiving))['selection_possible']


def test_tiny_positive_hot_and_photon_populations_are_not_treated_as_empty():
    one=np.ones((2,1));zero=one*0
    r=bank.joint_temperature_bounds(zero,zero,np.array([[1.],[0.]]),np.array([[0.],[1.]]),
        one,1e-20*one,one,1e-20*one,one)
    assert r['state_valid'].all()
    chosen=bank.choose_joint_coefficients(**limits(r))
    assert chosen['selection_possible']
    assert chosen['selected_channel_coefficient']>0


def test_invalid_or_degenerate_bounds_do_not_claim_finite_coefficient_selection():
    assert not bank.choose_joint_coefficients(1.,0.,1.,1.)['selection_possible']
    assert not bank.choose_joint_coefficients(np.inf,1.,1.,1.)['selection_possible']
    unforced=bank.choose_joint_coefficients(0.,np.inf,0.,np.inf)
    assert unforced['selection_possible'] and unforced['contrast_infimum']==0
