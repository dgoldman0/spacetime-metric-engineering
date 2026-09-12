import numpy as np
from numpy.testing import assert_allclose
from adm_harness.virtual_cell_semigroup import transport_map,solve_pair
from adm_harness.virtual_cell_transport import upwind_operator
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


def test_positive_supersolution_bounds_transient_wave_inventory_between_samples():
    from scipy.linalg import expm
    generator=upwind_operator(np.ones(9),.1)
    source=np.linspace(.2,.8,8)
    ceiling=np.linalg.solve(-generator,source)
    # An independently shaped starting profile exercises nonstationary
    # transit; the envelope must hold at all these intermediate times.
    initial=ceiling*np.array([.1,.8,.2,.7,.3,.6,.4,.5])
    for now in np.linspace(0,.8,101):
        state=ceiling+expm(now*generator)@(initial-ceiling)
        assert state.min()>-1e-13
        assert np.max(state-ceiling)<1e-13


def test_full_panel_bound_is_stronger_than_sampled_budgets():
    t=np.linspace(0,1,9); edges=np.linspace(-.02,.02,9)
    n,m,w=flat_problem(t,edges)
    rho=np.broadcast_to(1+t[:,None],(len(t),len(edges)-1))
    target=np.array([rho,-rho,np.zeros_like(rho)])
    sampled=solve_pair(t,edges,target,n,m,w)
    bounded=solve_pair(t,edges,target,n,m,w,wave_envelope=True)
    assert sampled['success'] and bounded['success']
    assert bounded['minimum_added_density']>=sampled['minimum_added_density']-1e-8
    assert bounded['within_panel_wave_bound']
