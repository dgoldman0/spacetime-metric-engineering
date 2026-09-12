import numpy as np
from numpy.testing import assert_allclose

from adm_harness.joint_backing_link import elastic_basis,solve_joint,passive_heat_capacity_interval


def geometry(t,x):
    shape=(len(t),len(x));one=np.ones(shape);zero=np.zeros(shape)
    return dict(gamma=one,b=one,radius=2*one,rest_volume=4*one,v=zero,lapse=one,
                acceleration=zero,angular_gradient=zero,volume_rate=zero)


def test_cold_constituents_obey_independent_strain_energy_variations():
    t=np.linspace(0,1,11);x=np.array([0.,1.])
    c=geometry(t,x)
    c['b']=np.exp(.2*t[:,None])*np.ones((1,2))
    c['radius']=2*np.exp(.07*t[:,None])*np.ones((1,2))
    c['rest_volume']=c['b']*c['radius']**2
    c['volume_rate']=np.ones((11,2))*.34
    basis=elastic_basis(c,np.ones((11,2))*.07)
    rates=np.array([.2,-.2,.07,-.07,.14])[:,None,None]
    derivative=rates*basis['energy']
    work=-(basis['radial']*.2+2*basis['angular']*.07)*c['rest_volume']
    assert_allclose(derivative,work,atol=1e-15)
    assert np.all(basis['density']>=abs(basis['radial']))
    assert np.all(basis['density']>=abs(basis['angular']))


def test_static_force_can_be_transmitted_to_counted_end_tractions():
    t=np.array([0.,.5,1.]);x=np.linspace(0,1,9);c=geometry(t,x)
    reference=np.ones((3,9))*.3
    result=solve_joint(t,x,c,np.zeros_like(reference),reference,np.ones(9)*.1,
                       np.ones((3,8))*(-.02),np.zeros((3,9)),prestrain_floor=.01)
    assert result['success'],result
    assert result['max_raw_equality_residual']<1e-8
    # The manufactured metric has a=k=v=0. Its force integral is exactly
    # the difference in radial material pressure at the two ends.
    radial=result['tensor'][1]
    assert_allclose(radial[:,-1]-radial[:,0],-.02,atol=1e-8)
    assert_allclose(np.diff(result['thermal']+result['warm'],axis=0),0.,atol=1e-8)


def test_zero_end_traction_cannot_hide_a_nonzero_integrated_static_force():
    t=np.array([0.,.5,1.]);x=np.linspace(0,1,9);c=geometry(t,x)
    reference=np.ones((3,9))*.3
    result=solve_joint(t,x,c,np.zeros_like(reference),reference,np.ones(9)*.1,
                       np.ones((3,8))*(-.02),np.zeros((3,9)),ends='balanced')
    assert not result['success']
    assert result['status']==2


def test_heat_capacity_gate_detects_incompatible_temperature_orderings():
    t=np.arange(3.)
    # Warm-to-fluid followed by fluid-to-warm. The first history admits
    # capacity in [0.5,1.5]; the second would require >=2.5 and <=1.5.
    thermal=np.array([[1.,3.],[1.,3.],[5.,1.]])
    warm=np.array([[2.,5.],[1.,4.],[2.,6.]])
    result=passive_heat_capacity_interval(t,thermal,warm)
    assert result['admissible'][0]
    assert not result['admissible'][1]
