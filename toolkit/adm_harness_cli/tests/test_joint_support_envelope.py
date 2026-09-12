import numpy as np
from numpy.testing import assert_allclose

from adm_harness.joint_support_envelope import build_envelope,solve_envelope


def static_geometry(t,x):
    one=np.ones((len(t),len(x)));zero=np.zeros_like(one)
    return dict(gamma=one,b=one,radius=2*one,rest_volume=4*one,v=zero,
        lapse=one,acceleration=zero,angular_gradient=zero,volume_rate=zero)


def test_envelope_transmits_static_load_with_finite_stress_fraction():
    t=np.array([0.,.5,1.]);x=np.linspace(0,1,9);c=static_geometry(t,x)
    u=np.ones((3,9))*.3
    r=solve_envelope(t,x,c,0*u,u,np.ones(9)*.1,np.full((3,8),-.02),0*u,
                     stress_fraction=.5,freeze_fluid=True)
    assert r['success'],r
    assert_allclose(np.diff(r['support_energy'],axis=0),0.,atol=2e-9)
    assert_allclose(r['radial_volume'][:,-1]-r['radial_volume'][:,0],-.08,atol=2e-9)
    assert np.max(abs(r['radial_volume'])-.5*r['support_energy'])<2e-9


def test_envelope_counts_work_and_local_heat_exchange_separately():
    t=np.linspace(0,1,5);x=np.linspace(0,1,5);c=static_geometry(t,x)
    ell=np.exp(.2*t[:,None])*np.ones((1,len(x)))
    c['b']=ell;c['rest_volume']=4*ell;c['volume_rate']=np.full_like(ell,.2)
    u=np.full_like(ell,.3);p=build_envelope(t,x,c,0*u,u,np.ones(5)*.1,np.zeros((5,4)),0*u)
    size=p['size'];a=np.zeros(p['peak']+1);a[:size]=u.ravel()
    # Constant pressure-volume P=-.2 delivers .2*dln(ell) into the support.
    # Geometry has no acceleration or radial gradients, so its force is zero.
    m=np.ones_like(ell)+.2*np.log(ell)
    a[size:2*size]=m.ravel();a[2*size:3*size]=-.2;a[-1]=10.
    assert_allclose(p['eq'].matrix()@a,p['eq'].rhs,atol=2e-15)
    assert np.max(p['ub'].matrix()@a-p['ub'].rhs)<1e-14


def test_envelope_balanced_ends_reject_unpaid_integrated_static_load():
    t=np.array([0.,.5,1.]);x=np.linspace(0,1,9);c=static_geometry(t,x)
    u=np.ones((3,9))*.3
    r=solve_envelope(t,x,c,0*u,u,np.ones(9)*.1,np.full((3,8),-.02),0*u,ends='balanced')
    assert not r['success']
    assert r['status']==2
