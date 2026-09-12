"""Independent energy checks for a shared store and two driven phase cells."""
import numpy as np
import pytest
from numpy.testing import assert_allclose
from scipy.integrate import quad
from adm_harness.virtual_cell_semigroup import transport_map, solve_pair
from test_virtual_cell_transport import flat_problem


def test_integrated_port_observable_matches_continuous_single_cell_solution():
    dt=.8; decay=1.7; initial=.6; increment=.3
    matrix,response,row,constant=transport_map(dt,np.array([0.,decay]),
        np.zeros(1),np.ones(1),1.,observable=np.array([decay]))
    expected=quad(lambda t:decay*(initial*np.exp(-decay*t)
        +increment/dt*(1-np.exp(-decay*t))/decay),0,dt)[0]
    assert_allclose(row@np.array([initial])+constant*increment,expected,atol=1e-13)
    final=matrix@np.array([initial])+response*increment
    assert_allclose(final+expected,initial+increment,atol=1e-13)


@pytest.mark.parametrize('eta',[1.,.98])
def test_closed_flat_cells_conserve_core_wave_store_and_exported_heat(eta):
    t=np.linspace(0,1,17); edges=np.linspace(-.015,.015,9)
    n,m,w=flat_problem(t,edges)
    rho=np.broadcast_to(1+t[:,None],(len(t),len(edges)-1))
    target=np.array([rho,-rho,np.zeros_like(rho)])
    result=solve_pair(t,edges,target,n,m,w,efficiency=eta,reservoir_eos=(0.,0.))
    assert result['success'] and result['reservoir_balance_residual']<1e-8
    inventory=4*np.pi*(edges[1]-edges[0])*np.sum(result['amplitude']
        +result['absorption_state']+result['recovery_state'],axis=1)
    inventory+=result['reservoir_energy']
    heat_export=np.r_[0.,np.cumsum(result['reservoir_exported_heat_panel_energy'])]
    assert_allclose(inventory+heat_export,inventory[0],atol=2e-8)
    assert result['reservoir_exported_heat_panel_energy'].min()>-1e-9
    if eta<1: assert heat_export[-1]>1e-5


def test_closed_store_cannot_improve_on_an_unrestricted_external_port():
    t=np.linspace(0,1,11); edges=np.linspace(-.02,.02,9)
    n,m,w=flat_problem(t,edges)
    rho=np.broadcast_to(1+t[:,None],(len(t),len(edges)-1))
    target=np.array([rho,-rho,np.zeros_like(rho)])
    opened=solve_pair(t,edges,target,n,m,w)
    closed=solve_pair(t,edges,target,n,m,w,reservoir_eos=(0.,0.))
    assert opened['success'] and closed['success']
    assert closed['minimum_added_density']>opened['minimum_added_density']+1e-4


def test_axial_confinement_gate_restricts_the_directed_store():
    t=np.linspace(0,1,11); edges=np.linspace(-.02,.02,9)
    n,m,w=flat_problem(t,edges)
    rho=np.broadcast_to(1+t[:,None],(len(t),len(edges)-1))
    target=np.array([rho,-rho,np.zeros_like(rho)])
    bare=solve_pair(t,edges,target,n,m,w,reservoir_eos=(1.,0.))
    confined=solve_pair(t,edges,target,n,m,w,reservoir_eos=(1.,0.),confine_reservoir=True)
    assert bare['success'] and confined['success']
    assert confined['minimum_added_density']>=bare['minimum_added_density']-1e-8
    volume=4*np.pi*(edges[-1]-edges[0])
    assert confined['reservoir_minimum_integrated_axial_tension_margin']>=-volume*confined['minimum_added_density']/3-2e-8
