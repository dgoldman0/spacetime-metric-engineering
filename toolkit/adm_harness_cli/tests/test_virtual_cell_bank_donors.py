import importlib.util
from pathlib import Path
import sys

import numpy as np
from numpy.testing import assert_allclose
import pytest

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
spec=importlib.util.spec_from_file_location('bank_donors',SCRIPTS/'audit_virtual_cell_bank_donors.py')
bank=importlib.util.module_from_spec(spec);spec.loader.exec_module(bank)


def test_positive_circulation_repairs_remaining_fluid_donor_without_changing_banks():
    r=bank.circulation_interval(0.,.5,.5,1.,.1,1.,fluid_turnover=1.,photon_turnover=1.)
    assert r['compatible']
    assert_allclose(r['absorption_lower'],.4)
    assert_allclose(r['candidate_counter_to_cold'],.4)
    assert_allclose(r['candidate_hot_to_counter'],.4)
    assert_allclose(r['candidate_hot_to_fluid'],.1)
    assert_allclose(r['candidate_fluid_to_cold'],.1)
    assert_allclose(r['candidate_hot_to_counter']-r['candidate_counter_to_cold'],0.)
    assert_allclose(r['candidate_hot_to_fluid']-r['candidate_fluid_to_cold'],0.)


def test_exhausted_hot_bank_prevents_circulation_repair():
    E=3.5e-6;qh=E;qc=.00367
    r=bank.circulation_interval(E,qh,qc,.00546,.01624,1.,fluid_turnover=10.)
    assert not r['compatible_unbounded_photon']
    assert_allclose(r['absorption_bank_upper'],0.)
    assert_allclose(r['minimum_possible_fluid_to_cold'],qc)
    assert r['minimum_fluid_donor_margin']<-.0027
    assert not any(key.startswith('candidate_') for key in r)


def test_zero_counter_donor_cannot_supply_finite_absorption():
    r=bank.circulation_interval(-.2,0.,.2,1.,1.,0.,fluid_turnover=10.,photon_turnover=10.)
    assert r['compatible_unbounded_photon'] and not r['compatible']
    assert r['active_empty_counter_donor']
    assert np.isinf(r['required_photon_turnover'])
    assert not any(key.startswith('candidate_') for key in r)


def test_finite_photon_rate_is_separate_from_unbounded_rate_and_tiny_donors_remain_positive():
    low=bank.circulation_interval(-.2,0.,.2,1.,1.,.01,photon_turnover=10.)
    assert low['compatible_unbounded_photon'] and not low['compatible']
    assert_allclose(low['required_photon_turnover'],20.)
    high=bank.circulation_interval(-.2,0.,.2,1.,1.,1e-20,photon_turnover=3e19)
    assert high['compatible'] and not high['active_empty_counter_donor']
    assert_allclose(high['required_photon_turnover'],2e19)


def test_full_candidate_is_absent_if_one_panel_fails_and_invalid_rates_reject():
    r=bank.circulation_interval(np.array([0.,.1]),np.array([.5,.1]),np.array([.5,.5]),
        1.,.1,1.,fluid_turnover=1.)
    assert r['compatible'][0] and not r['compatible'][1]
    assert not any(key.startswith('candidate_') for key in r)
    for kwargs in ({'fluid_turnover':0.},{'photon_turnover':-1.}):
        with pytest.raises(ValueError,match='turnover'):
            bank.circulation_interval(0.,0.,0.,1.,1.,1.,**kwargs)


def test_zero_objective_optimum_is_not_an_inventory_optimum():
    assert not bank.inventory_optimum_certified(dict(optimality_certified=True,
        inventory_minimization_requested=False,inventory_minimization_success=True))
    assert not bank.inventory_optimum_certified(dict(optimality_certified=True,
        inventory_minimization_requested=True,inventory_minimization_success=False))
    assert not bank.inventory_optimum_certified(dict(optimality_certified=True))
    assert bank.inventory_optimum_certified(dict(inventory_minimization_success=True))
