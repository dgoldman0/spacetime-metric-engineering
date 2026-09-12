import importlib.util
from pathlib import Path
import sys

import numpy as np
from numpy.testing import assert_allclose

SCRIPTS = Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
spec = importlib.util.spec_from_file_location('bank_capacity',SCRIPTS/'audit_virtual_cell_bank_capacity.py')
bank = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bank)


def test_large_opposed_exchange_needs_both_capacities_despite_zero_net_energy():
    positive=np.array([[10.],[0.]])
    negative=np.array([[0.],[10.]])
    result=bank.capacity_bounds(positive,negative,np.zeros_like(positive),np.array([1.]),np.array([1.]))
    assert_allclose(result['cumulative_net_counter'][-1],0.)
    assert_allclose(result['required_hot_initial'],10.)
    assert_allclose(result['required_cold_rating'],10.)
    assert_allclose(result['rate_independent_capacity_margin'],-19.)
    # A small nonzero net correction leaves almost the same large need.
    negative[1,0]=9.99
    nearby=bank.capacity_bounds(positive,negative,np.zeros_like(positive),np.array([1.]),np.array([1.]))
    assert_allclose(nearby['rate_independent_total_rating_lower'],19.99)


def test_converter_loss_can_supply_hot_energy_only_after_it_arrives():
    positive=np.array([[0.],[3.]])
    negative=np.array([[2.],[0.]])
    early_loss=np.array([[2.],[0.]])
    early=bank.capacity_bounds(positive,negative,early_loss,np.array([4.]),np.array([1.]))
    assert_allclose(early['required_hot_initial'],1.)
    assert_allclose(early['required_cold_rating'],2.)
    assert_allclose(early['rate_independent_capacity_margin'],1.)
    late=bank.capacity_bounds(positive[::-1],negative,early_loss[::-1],np.array([4.]),np.array([3.]))
    assert_allclose(late['required_hot_initial'],3.)
    assert_allclose(late['rate_independent_capacity_margin'],-1.)


def test_exact_counter_source_preserves_original_power_and_contact_signs():
    # D^(1/3)=2, lapse=3. Original source=11+6*2/3+7=22.
    source,zt=bank.counter_energy_source(6.,11.,2.,7.,10.,8.,3.,5.,2.,1.)
    assert_allclose(zt,2.)  # 5-3*2+3*1
    assert_allclose(source,15.)  # 22-2-10/2
    # Existing receiver heat is rerouted by exactly its proper power N*q.
    hotter,_=bank.counter_energy_source(6.,11.,2.,7.,10.,8.,3.,5.,3.,1.)
    colder,_=bank.counter_energy_source(6.,11.,2.,7.,10.,8.,3.,5.,2.,2.)
    assert_allclose(hotter-source,3.)
    assert_allclose(colder-source,-3.)


def test_turnover_is_separate_from_rate_independent_capacity():
    p=np.array([[.1]])
    r=bank.capacity_bounds(p,p,np.zeros_like(p),np.array([1.]),np.array([.1]),
        positive_proper_peak=np.array([100.]),turnover=10.)
    assert_allclose(r['rate_independent_capacity_margin'],.8)
    assert_allclose(r['capacity_margin_with_turnover'],-9.1)


def test_quadrature_splits_loss_and_source_knots_and_counts_opposite_signs():
    times=np.array([0.,1.])
    def rate(t):
        s=np.where(t<.25,12.,-4.)[:,None]
        loss=np.where(t<.25,4.,0.)[:,None]
        return np.array([np.maximum(s,0.),np.maximum(-s,0.),loss])
    four=bank.integrate_panels(times,np.array([.25]),rate,order=4)
    eight=bank.integrate_panels(times,np.array([.25]),rate,order=8)
    assert_allclose(four,eight,atol=2e-15)
    assert_allclose(eight[:,0,0],[3.,3.,1.])
    bound=bank.capacity_bounds(*eight,np.array([1.]),np.array([0.]))
    assert_allclose(bound['rate_independent_total_rating_lower'],5.)
