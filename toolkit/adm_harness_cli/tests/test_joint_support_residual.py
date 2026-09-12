import numpy as np

from adm_harness.joint_support_residual import solve_residual


def static_load(t,x):
    one=np.ones((len(t),len(x))); zero=one*0
    return dict(ell=one,D=one,lapse=one,v=zero,gamma=one,acceleration=zero,
                angular_gradient=zero,log_ell_t=zero,log_radius_t=zero,volume_rate=zero,
                fixed_power=zero,fixed_force=.2*one)


def test_sufficient_member_inventory_closes_static_force_and_energy():
    t=np.linspace(0,1,5);x=np.linspace(0,2,9)
    r=solve_residual(t,x,static_load,np.zeros(len(x)),np.zeros((len(t),len(x))),
                     material_cap=.5,deadline=5.)
    assert r['success']
    assert r['resolved_divergence_bound'] < 1e-9
    np.testing.assert_allclose(r['radial_volume'][:,-1]-r['radial_volume'][:,0],-.4,atol=1e-8)


def test_insufficient_inventory_leaves_an_explicit_force_deficit():
    t=np.linspace(0,1,5);x=np.linspace(0,2,9)
    r=solve_residual(t,x,static_load,np.zeros(len(x)),np.zeros((len(t),len(x))),
                     material_cap=.05,deadline=5.)
    assert r['success']
    assert r['resolved_divergence_bound'] > .1
    residual=np.diff(r['radial_volume'],axis=1)/np.diff(x)+.2
    assert np.max(abs(residual)) <= r['resolved_divergence_bound']+1e-8
    assert r['material_peak_upper'] <= .05+1e-8
