import numpy as np
from numpy.testing import assert_allclose

from adm_harness.thermal_receiver_contact import photon_contact_interval


def test_receiver_temperature_must_reverse_order_with_total_contact():
    # Tf**4/Z is 1 when sending and 16 when receiving: alpha**4 in (1,16).
    power=np.array([[2.,2.],[-1.,-1.]])
    fluid=np.array([[3.,6.],[6.,3.]])
    r=photon_contact_interval(power,fluid,np.ones((2,2)),np.ones(2))
    assert_allclose(r['lower'],[1,16]);assert_allclose(r['upper'],[16,1])
    assert r['compatible'].tolist()==[True,False]


def test_empty_receiver_cannot_send_heat_and_zero_contact_can_be_switched_off():
    r=photon_contact_interval(np.array([[1.,-1.,0.]]),np.array([[3.,3.,3.]]),
        np.zeros((1,3)),np.ones(3))
    assert r['compatible'].tolist()==[False,True,True]
    assert r['zero_energy_positive_outflow'].tolist()==[[True,False,False]]


def test_equal_temperatures_do_not_supply_finite_nonzero_exchange():
    r=photon_contact_interval(np.array([[1.],[-1.]]),np.ones((2,1))*3,
        np.ones((2,1)),np.ones(1))
    assert not r['compatible'][0]
    assert r['lower'][0]==r['upper'][0]==1.
