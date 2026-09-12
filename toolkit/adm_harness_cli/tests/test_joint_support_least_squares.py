import numpy as np
import pytest

pytest.importorskip('osqp')
from adm_harness.joint_support_least_squares import solve_least_squares
from test_joint_support_residual import static_load


def coefficients(t,x):
    c=static_load(t,x)
    c['radius']=2*np.ones((len(t),len(x)))
    return c


def test_sparse_fit_closes_manufactured_load_with_explicit_end_reactions():
    t=np.linspace(0,1,5);x=np.linspace(0,2,9);shape=(len(t),len(x))
    r=solve_least_squares(t,x,coefficients,np.zeros(len(x)),np.zeros(shape),np.zeros((3,*shape)),
                          material_cap=.5,deadline=10.)
    assert r['success'],r['message']
    assert r['weighted_squared_divergence'] < 1e-12
    np.testing.assert_allclose(r['radial_volume'][:,-1]-r['radial_volume'][:,0],-.4,atol=1e-5)


def test_force_free_planar_end_layers_cannot_hide_the_transmitted_load():
    t=np.linspace(0,1,5);x=np.linspace(0,2,9);shape=(len(t),len(x))
    r=solve_least_squares(t,x,coefficients,np.zeros(len(x)),np.zeros(shape),np.zeros((3,*shape)),
                          material_cap=.5,surface_width=.1,electric=np.zeros(shape),deadline=10.)
    assert r['success'],r['message']
    assert r['weighted_squared_divergence'] > .01
    np.testing.assert_allclose(r['radial_volume'][:,[0,-1]],0.,atol=1e-7)
