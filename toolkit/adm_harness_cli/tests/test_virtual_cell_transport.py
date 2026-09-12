"""Manufactured finite-cell controls for the common-port transport gate."""
import numpy as np
from numpy.testing import assert_allclose
from adm_harness.virtual_cell_transport import solve_pair, upwind_operator


def flat_problem(t,edges):
    nx=len(edges)-1
    def coefficients(nt):
        c={key:np.ones((nt,nx)) for key in ['radius','ell','lapse','gamma','b','D']}
        c['v']=np.zeros((nt,nx)); return c
    waves={sign:dict(faces=sign*np.ones((len(t)-1,nx+1)),
                     gain=np.zeros((len(t)-1,nx))) for sign in [-1,1]}
    return coefficients(len(t)),coefficients(len(t)-1),waves


def test_finite_volume_operator_counts_only_boundary_transport():
    y=np.array([.2,.6,.5,.8]); dx=.25
    assert_allclose(dx*np.sum(upwind_operator(np.ones(5),dx)@y),-y[-1])
    assert_allclose(dx*np.sum(upwind_operator(-np.ones(5),dx)@y),-y[0])


def test_constant_balanced_tube_needs_no_conversion_inventory():
    t=np.linspace(0,1,7); edges=np.linspace(-.2,.2,9)
    n,m,w=flat_problem(t,edges)
    rho=np.ones((len(t),len(edges)-1))
    r=solve_pair(t,edges,np.array([rho,-rho,np.zeros_like(rho)]),n,m,w)
    assert r['success']
    assert r['exact_added_density']<2e-8
    assert_allclose(r['amplitude'],rho,atol=2e-8)
    assert np.max(r['absorption_rest']+r['recovery_rest'])<2e-8


def test_varying_pure_tension_requires_counted_transport():
    t=np.linspace(0,1,9); edges=np.linspace(-.2,.2,9)
    n,m,w=flat_problem(t,edges)
    rho=np.broadcast_to(1+t[:,None],(len(t),len(edges)-1))
    r=solve_pair(t,edges,np.array([rho,-rho,np.zeros_like(rho)]),n,m,w)
    assert r['success'] and r['minimum_added_density']>1e-4
    assert np.max(r['absorption_rest']+r['recovery_rest'])>0
    shorter=edges/10
    short=solve_pair(t,shorter,np.array([rho,-rho,np.zeros_like(rho)]),n,m,w)
    assert short['minimum_added_density']<r['minimum_added_density']


def test_conversion_heat_and_finite_interfaces_are_charged():
    t=np.linspace(0,1,9); edges=np.linspace(-.2,.2,9)
    n,m,w=flat_problem(t,edges)
    rho=np.broadcast_to(1+t[:,None],(len(t),len(edges)-1))
    target=np.array([rho,-rho,np.zeros_like(rho)])
    r=solve_pair(t,edges,target,n,m,w,efficiency=.98,interface_sigma=.001)
    assert r['success']
    assert r['heat_rest'][-1].max()>0
    assert_allclose(r['wall_rest'],.01)
    assert_allclose(np.diff(r['heat_rest'],axis=0),
        (1/.98-1)*r['positive_increment']+.02*r['negative_increment'],atol=2e-8)
