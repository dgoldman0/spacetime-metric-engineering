import numpy as np
from numpy.testing import assert_allclose
from adm_harness.virtual_cell_semigroup import transport_map,solve_pair
from test_virtual_cell_transport import flat_problem


def test_exact_map_matches_single_cell_analytic_decay_and_input():
    dt=.7; source=np.array([.3]); decay=2.
    matrix,response=transport_map(dt,np.array([0.,decay]),np.zeros(1),source,1.)
    assert_allclose(matrix,[[np.exp(-decay*dt)]],atol=1e-14)
    assert_allclose(response,source*(1-np.exp(-decay*dt))/(decay*dt),atol=1e-14)


def test_maps_preserve_positivity_for_large_transit_courant_number():
    for back in [False,True]:
        m,s=transport_map(1.,np.ones(9),np.zeros(8),np.ones(8),.0001,back)
        assert m.min()>=0 and s.min()>=0
        assert np.all(m.sum(axis=0)<=1+1e-12)


def test_coherent_constant_tube_has_zero_route_and_heat_cost():
    t=np.linspace(0,1,7); edges=np.linspace(-.1,.1,9)
    n,m,w=flat_problem(t,edges); rho=np.ones((len(t),len(edges)-1))
    r=solve_pair(t,edges,np.array([rho,-rho,np.zeros_like(rho)]),n,m,w,efficiency=.98)
    assert r['success'] and r['exact_added_density']<2e-8
    assert_allclose(r['amplitude'],rho,atol=2e-8)
    assert r['thermal_return_rest'].max()<2e-8


def test_counted_guide_cannot_lower_the_minimum_required_energy():
    t=np.linspace(0,1,9); edges=np.linspace(-.1,.1,9)
    n,m,w=flat_problem(t,edges)
    rho=np.broadcast_to(1+t[:,None],(len(t),len(edges)-1))
    target=np.array([rho,-rho,np.zeros_like(rho)])
    bare=solve_pair(t,edges,target,n,m,w)
    guided=solve_pair(t,edges,target,n,m,w,guide_drift=.2)
    assert bare['success'] and guided['success']
    assert guided['minimum_added_density']>=bare['minimum_added_density']-1e-8
