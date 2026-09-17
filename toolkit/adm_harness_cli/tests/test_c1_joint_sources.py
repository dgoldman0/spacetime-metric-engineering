import numpy as np
import pytest

from adm_harness.c1_joint_sources import (
    RADIAL_ZONES, angular_rings, compact_population, joint_cone, radial_columns,
)
from adm_harness.c1_signed_channels import boundary_exchange, channel_tensor, dec_projections, optical_partitions


class Chart:
    def __init__(self, clock=1.):
        self.clock=clock
        self.coordinate=np.linspace(-2.,2.,2049)
        self.radius,self.lapse,self.radial_scale,*_=self.jets(self.coordinate)

    def jets(self,x):
        x=np.asarray(x,float);r=np.sqrt(4+x*x)
        return r,self.clock*np.exp(.12*x+.07*x*x),np.ones_like(x),x/r,4/r**3,.12+.14*x,np.full_like(x,.14)


def test_joint_populations_are_fixed_complete_tensors_with_distinct_spatial_support():
    target=np.array([[-2.,0.,0.],[-1.,0.,0.]])
    columns=np.zeros((2,2,3));columns[0,0]=[-1,0,-.5];columns[1,1]=[-1,0,.5]
    result=joint_cone(target,columns)
    np.testing.assert_allclose(result['coefficients'],[4.,2.],atol=1e-12)
    np.testing.assert_allclose(result['material'],[[2,0,2],[1,0,-1]],atol=1e-12)
    assert result['maximum_scaled_violation']<1e-12
    robust=joint_cone(target,columns,component_envelopes=np.diag([.01,.01]))
    np.testing.assert_allclose(robust['coefficients'],[2/.48,1/.48],rtol=1e-12)
    assert robust['minimum_margin_after_envelope']>-1e-12


def test_joint_sign_exclusion_and_empty_library():
    result=joint_cone(np.array([[-1.,0.,0.]]),np.array([[[1.,-1.,0.],[2.,0.,2.]]]))
    assert not result['feasible']
    assert result['direct_witness']['required']<0
    assert min(result['direct_witness']['all_source_projections'])>=0
    assert joint_cone(np.array([[1.,.5,.2]]),np.empty((1,0,3)))['feasible']
    assert not joint_cone(np.array([[1.,2.,.2]]),np.empty((1,0,3)))['feasible']
    with pytest.raises(ValueError):
        joint_cone(np.ones((1,3)),np.ones((1,1,3)),component_envelopes=[[-1.]])


def test_radial_population_columns_reproduce_independently_assembled_cells():
    chart=Chart();x=np.linspace(-1.9,1.9,501)
    parts=[optical_partitions(chart,domain,4) for domain in ((-1.8,.7),(.3,1.8))]
    charges=np.array([[1.,7.,2.,5.],[2.,3.,4.,6.]])
    row=dict(partitions=[dict(coordinate=e.tolist(),optical_lengths=l.tolist()) for e,l in parts],
             central_charge_per_compartment=charges.tolist())
    exact=np.zeros((len(x),3))
    for (ends,lengths),population in zip(parts,charges):
        for j,c in enumerate(population):
            exact+=channel_tensor(chart,x,ends[j:j+2],lengths[j:j+1],strength=.17*c)
    for mode,coefficient in (('module_scales',np.ones(2)),('compartments',charges.ravel()/13.)):
        columns,_,_=radial_columns(chart,x,row,.17,mode,charge_unit=13.)
        np.testing.assert_allclose(np.einsum('nsc,s->nc',columns,coefficient),exact,atol=1e-15)


def test_closed_channel_normalization_and_carrier_virtual_work():
    # A periodic real massless scalar has two travelling branches.
    # Exponential mode regulator, subtracting the infinite-line integral:
    # E = (2*pi/L) * lim(sum n exp(-epsilon*n) - 1/epsilon^2).
    epsilon=np.array([.04,.03,.02,.01])
    finite=np.exp(-epsilon)/np.expm1(-epsilon)**2-epsilon**-2
    intercept=np.polynomial.polynomial.polyfit(epsilon**2,finite,3)[0]
    chart=Chart();x=np.array([.4]);r=chart.jets(x)[0][0];mu=.03
    result=angular_rings(chart,x,1.,mu,1.)
    np.testing.assert_allclose(4*np.pi*r*r*result['quantum'][0,0],intercept/r,rtol=3e-10)
    energy=lambda radius:-1/(12*radius)+2*np.pi*mu*radius
    step=1e-5
    expected_pt=-(energy(r+step)-energy(r-step))/(2*step)/(8*np.pi*r)
    np.testing.assert_allclose(result['total'][0,2],expected_pt,rtol=2e-10)
    assert result['total'][0,1]==0.


def test_uniform_population_zones_cancel_internal_radial_wall_tractions():
    chart=Chart()
    parts=[optical_partitions(chart,domain,32) for domain in ((-1.8,.7),(.3,1.8))]
    row=dict(partitions=[dict(coordinate=e.tolist(),optical_lengths=l.tolist()) for e,l in parts],
             central_charge_per_compartment=np.ones((2,32)).tolist())
    x=np.linspace(-1.7,1.7,151)
    columns,weights,_=radial_columns(chart,x,row,.17,'zones',charge_unit=13.)
    assert columns.shape==(151,5,3)
    for (module,lo,hi),cost in zip(RADIAL_ZONES,weights):
        e,l=parts[module]
        assert cost==hi-lo
        force=boundary_exchange(chart,e[lo:hi+1],l[lo:hi],strength=2.21)['force_on_material']
        assert max(abs(force[1:-1]))<1e-9*max(abs(force))


def test_ring_exchange_matches_derivative_of_killing_energy_and_counts_carrier():
    chart=Chart();x=np.linspace(-1.5,1.5,31);mu=.01;h=2e-5
    result=angular_rings(chart,x,1.,mu,1.)
    def energy(coordinate):
        r,a,*_=chart.jets(coordinate)
        return a*(-1/(12*r)+2*np.pi*mu*r)
    r,a,*_=chart.jets(x)
    derivative=(energy(x+h)-energy(x-h))/(2*h)/(a*4*np.pi*r*r)
    np.testing.assert_allclose(-result['force_on_additional_support'],derivative,rtol=3e-10,atol=1e-13)
    # One fixed physical mu/c implies a changing ratio when R changes.
    np.testing.assert_allclose(result['carrier_over_quantum'],24*np.pi*mu*r*r)
    high=angular_rings(chart,x,1.,1.,1.)['total']
    assert np.all(dec_projections(high)[:,1]>0)


def test_compact_ring_population_has_resolved_flat_endpoints():
    lo,hi=-1.,1.;d=.15;h=1e-5
    assert compact_population(np.array([lo-.1,lo,hi,hi+.1]),(lo,hi),d).sum()==0
    np.testing.assert_allclose(compact_population(np.array([lo+d,0,hi-d]),(lo,hi),d),1.)
    assert compact_population(lo+h,(lo,hi),d)<4e-12
