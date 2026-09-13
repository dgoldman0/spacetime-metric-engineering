import sys
from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_allclose

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_virtual_cell_photon_contact_capacity import passive_port_capacity,reciprocal_star


def test_passive_channel_capacity_and_signed_energy_are_independent_of_rate10():
    a=np.ones((2,1))
    r=passive_port_capacity(2*a,24*a,a,a,.01*a,a,a,.2*a,a)
    assert r['capacity_pass'].all()
    assert_allclose(r['total_transmission_budget'],.26)
    assert_allclose(r['material_recoil_force_density'],5.2)
    assert_allclose(r['photon_power_residual'],0.)


def test_joint_passive_budget_can_fail_even_when_each_bank_fits_separately():
    a=np.ones((1,1))
    r=passive_port_capacity(.6*a,.6*a,a,a,a,a,a,0*a,a)
    assert np.all(r['hot_transmission_budget']<1)
    assert np.all(r['cold_transmission_budget']<1)
    assert not r['capacity_pass'].any()


def test_positive_heat_with_closed_temperature_gap_rejects():
    a=np.ones((1,1))
    r=passive_port_capacity(0*a,a,a,a,a,a,0*a,0*a,a)
    assert not r['state_and_gap_valid'].any()
    assert not r['capacity_pass'].any()


def test_balanced_counterstream_has_zero_grey_recoil():
    a=np.ones((1,1))
    r=passive_port_capacity(a,a,a,a,.1*a,a,a,0*a,a)
    assert_allclose(r['material_recoil_force_density'],0.)


def test_unphysical_directional_population_and_negative_heat_reject():
    a=np.ones((1,1))
    r=passive_port_capacity(a,a,a,a,.1*a,a,a,2*a,a)
    assert not r['capacity_pass'].any()
    with pytest.raises(ValueError):
        passive_port_capacity(-a,a,a,a,.1*a,a,a,0*a,a)


def test_reciprocal_star_is_unitary_and_has_required_bank_bypass():
    hot=np.array([0.,.2,.4]);cold=np.array([.3,.3,.6])
    r=reciprocal_star(hot,cold);matrix=r['scattering_matrix']
    assert r['valid'].all()
    assert_allclose(matrix@np.swapaxes(matrix,-1,-2),np.broadcast_to(np.eye(3),matrix.shape),atol=1e-14)
    assert_allclose(matrix[...,0,1]**2,hot,atol=1e-14)
    assert_allclose(matrix[...,0,2]**2,cold,atol=1e-14)
    assert_allclose(matrix[...,1,2]**2,r['direct_bank_transmission'],atol=1e-14)
    assert r['direct_bank_transmission'][0]==0
    assert np.all(r['direct_bank_transmission'][1:]>0)


def test_star_rejects_transmissions_exceeding_one():
    assert not reciprocal_star(.6,.6)['valid']
