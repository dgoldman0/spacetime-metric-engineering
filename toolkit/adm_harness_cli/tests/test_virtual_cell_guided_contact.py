import importlib.util
from pathlib import Path
import sys

import numpy as np
from numpy.testing import assert_allclose
import pytest

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
spec=importlib.util.spec_from_file_location('guided_contact',SCRIPTS/'audit_virtual_cell_guided_contact.py')
guided=importlib.util.module_from_spec(spec);spec.loader.exec_module(guided)


def test_fixed_channel_coefficient_admits_correct_emission_absorption_order():
    power=np.array([[1.],[-1.]])
    result=guided.guided_interval(power,np.array([[1.],[3.]]),np.ones((2,1)),np.ones((2,1)))
    assert result['compatible'][0]
    assert_allclose(result['lower'],1.)
    assert_allclose(result['upper'],3.)
    assert result['lower_witness'][0]==0 and result['upper_witness'][0]==1
    # The same physical channel constant survives an area change when its
    # equilibrium density is correspondingly diluted as R^-2.
    scaled=guided.guided_interval(power,np.array([[.25],[.75]]),2*np.ones((2,1)),np.ones((2,1)))
    assert_allclose(scaled['lower'],result['lower'])
    assert_allclose(scaled['upper'],result['upper'])


def test_reversed_order_requires_incompatible_fixed_channel_constants():
    result=guided.guided_interval(np.array([[1.],[-1.]]),np.array([[3.],[1.]]),
                                  np.ones((2,1)),np.ones((2,1)))
    assert not result['compatible'][0]
    assert result['lower'][0]>result['upper'][0]


def test_empty_and_zero_temperature_limits_preserve_physical_direction():
    # Warm empty modes may receive emission. Positive populated modes may be
    # absorbed by a zero-temperature bath. The reversed transfers fail.
    power=np.array([[1.,-1.,1.,-1.]])
    density=np.array([[0.,1.,1.,0.]])
    temperature=np.array([[1.,0.,0.,1.]])
    result=guided.guided_interval(power,density,np.ones_like(power),temperature)
    assert result['compatible'].tolist()==[True,True,False,False]
    assert result['forbidden_emission'][0,2]
    assert result['forbidden_absorption'][0,3]
    assert np.isnan(result['ratio'][0,1])
    zero=guided.guided_interval(np.zeros((1,1)),np.zeros((1,1)),np.ones((1,1)),np.zeros((1,1)))
    assert zero['compatible'][0]


def test_small_strictly_positive_states_allow_finite_opacity_and_channel_constant():
    tiny_temperature=guided.TEMPERATURE_TOLERANCE/100
    tiny_density=guided.POPULATION_TOLERANCE/100
    # Emission into positive modes at a very small positive temperature needs
    # a large coefficient. Absorption from a small positive population needs
    # a small coefficient and potentially large opacity. Both remain finite.
    power=np.array([[1.,-1.]])
    density=np.array([[1.,tiny_density]])
    temperature=np.array([[tiny_temperature,1.]])
    result=guided.guided_interval(power,density,np.ones_like(power),temperature)
    assert result['compatible'].all()
    assert not result['forbidden_emission'].any()
    assert not result['forbidden_absorption'].any()
    assert_allclose(result['lower'][0],1/tiny_temperature**2)
    assert_allclose(result['upper'][1],tiny_density)
    a2=np.array([2*result['lower'][0],result['upper'][1]/2])
    opacity=power/(a2*temperature**2-density)
    assert np.isfinite(opacity).all() and np.all(opacity>0)


def test_fixed_deadbands_report_raw_negative_population_and_small_power():
    density=np.array([[-2*guided.POPULATION_TOLERANCE]])
    result=guided.guided_interval(np.array([[guided.POWER_TOLERANCE/2]]),density,
                                  np.ones((1,1)),np.ones((1,1)))
    assert result['bad_population'][0,0]
    assert not result['emission'][0,0]
    assert not result['compatible'][0]
    assert density[0,0]<0
    with pytest.raises(ValueError,match='positive tolerances'):
        guided.guided_interval(np.zeros((1,1)),np.ones((1,1)),np.ones((1,1)),
                               np.ones((1,1)),power_tolerance=0.)


def test_original_fluid_receiver_and_retained_support_power_are_counted_once():
    D=np.array([[8.]]);N=np.array([[2.]]);rate=np.array([[.3]])
    U0=np.array([[5.]]);U0t=np.array([[2.]]);Z0t=np.array([[.2]])
    Zt=np.array([[.3]]);Kt=np.array([[.8]])
    pc=guided.required_counter_power(U0,U0t,Z0t,Zt,Kt,N,D,rate)
    pf=Kt/(N*D**(4/3));p0=(U0t+U0*rate/3)/(N*D);pz0=Z0t/(N*D)
    original_loss=.1
    fixed=p0+pz0-original_loss
    contact=original_loss-Zt/(N*D)
    assert_allclose(pc,(2.+.5+.2-.3-.4)/16)
    assert_allclose(pf,contact+fixed-pc)
    # Exactly retaining old U,Z gives zero complementary-photon power even
    # when their baseline source duties are nonzero.
    K0t=D**(1/3)*(U0t+U0*rate/3)
    assert_allclose(guided.required_counter_power(U0,U0t,Z0t,Z0t,K0t,N,D,rate),0.)


def test_failed_parent_cannot_receive_an_overall_guided_pass():
    assert not guided.necessary_overall_pass(False,True,0.)
    assert not guided.necessary_overall_pass(True,False,0.)
    assert not guided.necessary_overall_pass(True,True,2*guided.POPULATION_TOLERANCE)
    assert guided.necessary_overall_pass(True,True,0.)


def test_reconstructed_receiver_derivative_preserves_positive_contacts_with_variable_loss():
    state=dict(contact_control_time=np.array([0.,1.,2.]),
        applied_hot_parent_proper_rate=np.array([[.3],[.5]]),
        applied_cold_parent_proper_rate=np.array([[.1],[.2]]))
    times=np.array([.25,.75,1.25,1.75]);lapse=np.array([[1.],[2.],[3.],[4.]])
    D=np.full_like(lapse,2.);loss=np.array([[.1],[.4],[.5],[.1]])
    rate,method=guided.receiver_inventory_rate(state,times,lapse,D,loss)
    assert_allclose(loss-rate/(lapse*D),np.array([[.1],[.1],[.15],[.15]]),atol=1e-15)
    assert 'saved parent proper' in method
    state['applied_hot_parent_proper_rate'][0,0]=-.1
    with pytest.raises(ValueError,match='nonnegative proper'):
        guided.receiver_inventory_rate(state,times,lapse,D,loss)
