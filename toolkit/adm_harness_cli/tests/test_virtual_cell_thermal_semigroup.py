"""Counted distributed thermal exchange with explicit driven photon transport."""
import numpy as np
from numpy.testing import assert_allclose
import pytest

from adm_harness.virtual_cell_semigroup import solve_pair
from test_virtual_cell_transport import flat_problem


@pytest.mark.parametrize('solver_method,solver_crossover',[(None,None),('highs-ipm',None),('highs-ipm',False)])
def test_constant_shared_core_remains_feasible_with_distributed_thermal_gate(solver_method,solver_crossover):
    t=np.linspace(0,1,5);edges=np.linspace(-.01,.01,5)
    nodes,mids,waves=flat_problem(t,edges);one=np.ones((len(t),4));zero=np.zeros_like(one)
    result=solve_pair(t,edges,np.array([one,-one,zero]),nodes,mids,waves,
        efficiency=.98,matched_pair=True,wave_envelope=True,guide_drift=.5,thermal_eos=1/3,
        solver_method=solver_method,solver_crossover=solver_crossover)
    assert result['success'] and result['exact_added_density']<2e-8
    assert_allclose(result['amplitude'],1.,atol=2e-8)
    assert result['thermal_exchange_balance_residual']<1e-10
    assert_allclose(result['balanced_radiation_rest'],0.,atol=2e-8)
    assert_allclose(result['thermal_reservoir_rest'],0.,atol=2e-8)
    assert result['solver_method']==(solver_method or 'highs-ds')
    assert result['solver_crossover']==solver_crossover


def test_driven_thermal_to_core_conversion_counts_wave_counter_and_heat_inventory():
    t=np.linspace(0,1,9);edges=np.linspace(-.01,.01,5)
    nodes,mids,waves=flat_problem(t,edges);one=np.ones((len(t),4))
    progress=t[:,None]*one
    target=np.array([one,(1-4*progress)/3,(1-progress)/3])
    result=solve_pair(t,edges,target,nodes,mids,waves,efficiency=.98,
        matched_pair=True,wave_envelope=True,guide_drift=.5,thermal_eos=1/3)
    assert result['success'] and result['minimum_added_density']<.1
    assert np.min(result['amplitude'][-1]-result['amplitude'][0])>.5
    ua,ur=result['absorption_rest'],result['recovery_rest']
    W=result['balanced_radiation_rest'];B=result['thermal_reservoir_rest']
    assert ua.max()>1e-4 and result['thermal_return_rest'].max()>1e-6
    assert np.max(2*np.maximum(ua,ur)-W)<1e-8
    assert np.min(result['counterstream_rest']-abs(ua-ur))>-1e-8
    for ceiling in (result['absorption_panel_ceiling'],result['recovery_panel_ceiling']):
        assert np.max(2*ceiling-W[:-1])<1e-8
        assert np.max(2*ceiling-W[1:])<1e-8
        assert np.max(2*ceiling-(W[:-1]+W[1:])/2)<1e-8
    total=result['amplitude']+W+B
    assert_allclose(total,np.broadcast_to(total[0],total.shape),atol=1e-8)
    assert result['thermal_exchange_balance_residual']<1e-9
    # Independently reconstruct the complete remaining field/radiation/
    # membrane/rest cone, including the nonminimal complementary photons.
    a=result['amplitude'];p=target[1]+a-W-B/3;q=target[2]-B/3
    need=a+W+B+np.maximum.reduce([p+2*q,p-q,-2*p-q])
    assert np.max(need-target[0])<=result['minimum_added_density']+2e-8


def test_thermal_transport_cannot_hide_disappearing_total_energy_capacity():
    t=np.linspace(0,1,5);edges=np.linspace(-.01,.01,5)
    nodes,mids,waves=flat_problem(t,edges)
    rho=np.broadcast_to((1-t)[:,None],(len(t),4));zero=np.zeros_like(rho)
    result=solve_pair(t,edges,np.array([rho,-rho,zero]),nodes,mids,waves,
        efficiency=.98,matched_pair=True,wave_envelope=True,thermal_eos=1/3)
    assert result['success']
    assert result['minimum_added_density']>.1
    assert result['thermal_exchange_balance_residual']<1e-9


def test_distributed_thermal_gate_rejects_shared_store_and_invalid_thread_options():
    t=np.linspace(0,1,3);edges=np.linspace(-.01,.01,5)
    nodes,mids,waves=flat_problem(t,edges);one=np.ones((3,4))
    args=(t,edges,np.array([one,-one,np.zeros_like(one)]),nodes,mids,waves)
    with pytest.raises(ValueError,match='separate distributed'):
        solve_pair(*args,thermal_eos=1/3,reservoir_eos=(0.,0.))
    with pytest.raises(ValueError,match='thermal_eos'):
        solve_pair(*args,thermal_eos=0.)
    with pytest.raises(ValueError,match='solver_threads'):
        solve_pair(*args,thermal_eos=1/3,solver_threads=True)
    with pytest.raises(ValueError,match='solver_method'):
        solve_pair(*args,thermal_eos=1/3,solver_method='highs')
    with pytest.raises(ValueError,match='thermal_reference_density'):
        solve_pair(*args,thermal_reference_density=one)
    with pytest.raises(ValueError,match='thermal_reference_density'):
        solve_pair(*args,thermal_eos=1/3,thermal_reference_density=-one)


def test_reallocated_fluid_preserves_original_power_and_counts_total_stress():
    t=np.linspace(0,1,5);edges=np.linspace(-.01,.01,5)
    nodes,mids,waves=flat_problem(t,edges);one=np.ones((len(t),4))
    reference=(1+t[:,None])*one
    # The backing needs no tensor. The growing reference fluid already owns
    # the required power port. It must remain present in the enlarged budget.
    target=np.zeros((3,len(t),4))
    result=solve_pair(t,edges,target,nodes,mids,waves,thermal_eos=1/3,
        matched_pair=True,wave_envelope=True,thermal_reference_density=reference)
    assert result['success'] and result['exact_added_density']<1e-8
    A=result['amplitude'];W=result['balanced_radiation_rest'];B=result['thermal_reservoir_rest']
    assert_allclose(np.diff(A+W+B,axis=0),np.diff(reference,axis=0),atol=1e-8)
    assert result['thermal_exchange_balance_residual']<1e-9
    p=reference/3+A-W-B/3;q=reference/3-B/3
    need=A+W+B+np.maximum.reduce([p+2*q,p-q,-2*p-q])
    assert np.max(need-reference)<1e-8
    assert_allclose(target,0.)


def test_reallocation_can_cool_existing_fluid_without_negative_total_energy():
    t=np.linspace(0,1,7);edges=np.linspace(-.01,.01,5)
    nodes,mids,waves=flat_problem(t,edges);one=np.ones((len(t),4))
    progress=t[:,None]*one
    # The total target evolves from isotropic thermal pressure to radial
    # tension. Reusing the fluid's constant energy can drive that conversion.
    total=np.array([one,(1-4*progress)/3,(1-progress)/3])
    baseline=np.array([one,one/3,one/3])
    result=solve_pair(t,edges,total-baseline,nodes,mids,waves,efficiency=.98,
        matched_pair=True,wave_envelope=True,thermal_eos=1/3,thermal_reference_density=one)
    assert result['success'] and result['minimum_added_density']<.1
    assert result['thermal_inventory_increment'].min()<-.5
    assert result['thermal_reservoir_rest'].min()>=-1e-9
    assert np.min(result['amplitude'][-1]-result['amplitude'][0])>.5


def test_receiver_exchange_counts_total_energy_and_keeps_rated_capacity():
    t=np.linspace(0,1,7);edges=np.linspace(-.01,.01,5)
    nodes,mids,waves=flat_problem(t,edges);one=np.ones((len(t),4));zero=one*0
    progress=t[:,None]*one
    target=np.array([zero,-progress,zero])
    result=solve_pair(t,edges,target,nodes,mids,waves,efficiency=.98,
        matched_pair=True,wave_envelope=True,thermal_eos=1/3,
        thermal_reference_density=zero,receiver_reference=(one,np.ones(4)))
    assert result['success'] and result['minimum_added_density']<.1
    A=result['amplitude'];W=result['balanced_radiation_rest'];B=result['thermal_reservoir_rest']
    Z=result['receiver_thermal_energy']
    # Prepared phase/radiation can substitute for receiver inventory at this
    # optimum; conservation and the full cone apply to either allocation.
    assert Z.min()>=-1e-9 and Z.max()<=1+1e-9
    assert_allclose(np.diff(A+W+B+Z,axis=0),0.,atol=1e-8)
    assert_allclose(result['receiver_contact_energy_to_fluid'],-np.diff(Z,axis=0),atol=1e-12)
    p=-progress+A-W-B/3;q=-B/3
    need=A+W+B+Z+np.maximum.reduce([p+2*q,p-q,-2*p-q])
    assert np.max(need-one)<=result['minimum_added_density']+2e-8
    assert result['receiver_capacity_violation']<1e-9


def test_receiver_original_feed_is_preserved_and_invalid_capacity_rejected():
    t=np.linspace(0,1,4);edges=np.linspace(-.01,.01,5)
    nodes,mids,waves=flat_problem(t,edges);one=np.ones((len(t),4));zero=one*0
    Z0=(1+t[:,None])*one
    args=(t,edges,np.array([zero,zero,zero]),nodes,mids,waves)
    result=solve_pair(*args,matched_pair=True,thermal_eos=1/3,
        thermal_reference_density=zero,receiver_reference=(Z0,np.ones(4)*2))
    assert result['success'] and result['minimum_added_density']<1e-8
    total=(result['amplitude']+result['balanced_radiation_rest']+
           result['thermal_reservoir_rest']+result['receiver_thermal_energy'])
    assert_allclose(np.diff(total,axis=0),np.diff(Z0,axis=0),atol=1e-8)
    assert result['receiver_contact_energy_to_fluid'].max()>1e-3
    with pytest.raises(ValueError,match='receiver_reference'):
        solve_pair(*args,thermal_eos=1/3,receiver_reference=(Z0,np.ones(4)*2))
    with pytest.raises(ValueError,match='rated capacity'):
        solve_pair(*args,thermal_eos=1/3,thermal_reference_density=zero,
            receiver_reference=(Z0,np.ones(4)))


@pytest.mark.parametrize('split_receiver',[False,True])
def test_direct_budget_gate_pays_for_finite_donor_turnover_at_both_panel_ends(split_receiver):
    t=np.linspace(0,1,5);edges=np.linspace(-.01,.01,5)
    nodes,mids,waves=flat_problem(t,edges);one=np.ones((len(t),4));zero=one*0
    Z0=(1+t[:,None])*one;duration=np.diff(t)[:,None]*one[:-1]
    loss=.1*duration;rate=2.
    result=solve_pair(t,edges,np.array([zero,zero,zero]),nodes,mids,waves,
        matched_pair=True,thermal_eos=1/3,thermal_reference_density=zero,
        receiver_reference=(Z0,np.ones(4)*2),receiver_contact=(loss,duration,rate),
        target_budget_only=True,split_receiver=split_receiver)
    assert result['success'] and result['minimum_added_density']==0.
    assert result['second_optimization_success'] is None
    assert result['inventory_minimization_success']
    Z=result['receiver_thermal_energy'];U=result['thermal_reservoir_rest']
    H=loss-np.diff(Z,axis=0)
    for zz,uu in ((Z[:-1],U[:-1]),(Z[1:],U[1:])):
        assert np.max(H-rate*duration*zz)<1e-8
        assert np.max(-H-rate*duration*uu)<1e-8
    assert Z.max()>1e-3
    assert result['receiver_donor_energy_violation']<1e-8
    total=result['amplitude']+result['balanced_radiation_rest']+U+Z
    assert_allclose(np.diff(total,axis=0),np.diff(Z0,axis=0),atol=1e-8)
    if split_receiver:
        hot=result['receiver_hot_energy'];cold=result['receiver_cold_energy']
        qhot=loss-np.diff(hot,axis=0);qcold=np.diff(cold,axis=0)
        assert hot.min()>-1e-9 and cold.min()>-1e-9
        assert qhot.min()>-1e-9 and qcold.min()>-1e-9
        assert_allclose(hot+cold,Z,atol=1e-10)
        assert_allclose(qhot-qcold,H,atol=1e-10)
        assert np.max(hot.max(axis=0)+cold.max(axis=0))<=2+1e-9
        assert result['receiver_split_rating_violation']<1e-9
        for hh,uu in ((hot[:-1],U[:-1]),(hot[1:],U[1:])):
            assert np.max(qhot-rate*duration*hh)<1e-8
            assert np.max(qcold-rate*duration*uu)<1e-8


def test_uniform_thermal_floor_uses_counted_fluid_pressure_and_particle_number():
    t=np.linspace(0,1,4);edges=np.linspace(-.01,.01,5)
    nodes,mids,waves=flat_problem(t,edges);one=np.ones((len(t),4))
    number=np.ones(4)/3
    result=solve_pair(t,edges,np.array([one,one/3,one/3]),nodes,mids,waves,
        matched_pair=True,thermal_eos=1/3,target_budget_only=True,
        thermal_particle_number=number,maximize_thermal_floor=True)
    assert result['success'] and result['minimum_added_density']==0
    assert_allclose(result['maximum_uniform_fluid_temperature'],1.,atol=1e-8)
    assert result['retained_uniform_fluid_temperature']>=.99-1e-8
    assert np.min(result['thermal_reservoir_rest']/(3*number))>=.99-1e-8
    assert result['second_optimization_success']


def test_fixed_thermal_floor_uses_one_inventory_solve_and_cannot_buy_extra_density(monkeypatch):
    import adm_harness.virtual_cell_semigroup as module
    t=np.linspace(0,1,4);edges=np.linspace(-.01,.01,5)
    nodes,mids,waves=flat_problem(t,edges);one=np.ones((len(t),4))
    number=np.ones(4)/3
    calls=[];original=module.linprog
    def counted(*args,**kwargs):
        calls.append(1)
        return original(*args,**kwargs)
    monkeypatch.setattr(module,'linprog',counted)
    args=(t,edges,np.array([one,one/3,one/3]),nodes,mids,waves)
    result=solve_pair(*args,matched_pair=True,thermal_eos=1/3,target_budget_only=True,
        thermal_particle_number=number,minimum_thermal_floor=.03)
    assert result['success'] and len(calls)==1
    assert result['second_optimization_success'] is None
    assert result['minimum_added_density']==0
    assert result['minimum_observed_fluid_temperature']>=.03-1e-8
    assert result['thermal_floor_violation']<1e-8
    assert_allclose(result['retained_uniform_fluid_temperature'],.03)
    impossible=solve_pair(*args,matched_pair=True,thermal_eos=1/3,target_budget_only=True,
        thermal_particle_number=number,minimum_thermal_floor=1.01)
    assert not impossible['success'] and len(calls)==2


def test_explicit_midpoint_capacity_rejects_a_dip_missed_by_endpoint_averaging():
    t=np.linspace(0,1,4);edges=np.linspace(-.01,.01,5)
    nodes,mids,waves=flat_problem(t,edges);one=np.ones((len(t),4));zero=one*0
    args=(t,edges,np.array([one,-one,zero]),nodes,mids,waves)
    options=dict(matched_pair=True,thermal_eos=1/3,target_budget_only=True,wave_envelope=True)
    averaged=solve_pair(*args,**options)
    assert averaged['success']
    exact=solve_pair(*args,midpoint_credited_target=np.zeros((3,len(t)-1,4)),**options)
    assert not exact['success']
    assert exact['explicit_credited_midpoint_target']


def test_feasible_native_inventory_is_separate_from_an_optimized_bound(monkeypatch):
    import adm_harness.highs_feasible as native
    original=native.linprog_feasible
    def unfinished_but_verified(*args,**kwargs):
        result=original(*args,**kwargs)
        assert result.verified_feasible
        result.optimality_certified=False
        result.feasibility_only_success=True
        result.status=4
        return result
    monkeypatch.setattr(native,'linprog_feasible',unfinished_but_verified)
    t=np.linspace(0,1,4);edges=np.linspace(-.01,.01,5)
    nodes,mids,waves=flat_problem(t,edges);one=np.ones((len(t),4))
    args=(t,edges,np.array([one,one/3,one/3]),nodes,mids,waves)
    options=dict(matched_pair=True,thermal_eos=1/3,thermal_particle_number=np.ones(4)/3,
                 minimum_thermal_floor=.03,solver_method='highs-ipm',solver_crossover=False,
                 retain_feasible_interior=True)
    result=solve_pair(*args,target_budget_only=True,**options)
    assert result['success'] and result['verified_feasible']
    assert result['minimum_added_density']==0 and result['status']==4
    assert result['feasibility_only_success'] and not result['inventory_minimization_success']
    with pytest.raises(ValueError,match='fixed direct budget'):
        solve_pair(*args,**dict(options,minimum_thermal_floor=None))


def test_fixed_thermal_floor_and_midpoint_inputs_require_their_declared_contract():
    t=np.linspace(0,1,3);edges=np.linspace(-.01,.01,5)
    nodes,mids,waves=flat_problem(t,edges);one=np.ones((3,4))
    args=(t,edges,np.array([one,one/3,one/3]),nodes,mids,waves)
    options=dict(thermal_eos=1/3,target_budget_only=True,thermal_particle_number=np.ones(4))
    for bad in (True,-.01,float('nan'),'0.03'):
        with pytest.raises(ValueError,match='minimum_thermal_floor'):
            solve_pair(*args,minimum_thermal_floor=bad,**options)
    with pytest.raises(ValueError,match='mutually exclusive'):
        solve_pair(*args,minimum_thermal_floor=.03,maximize_thermal_floor=True,**options)
    with pytest.raises(ValueError,match='positive particle inventory'):
        solve_pair(*args,thermal_eos=1/3,target_budget_only=True,minimum_thermal_floor=.03)
    with pytest.raises(ValueError,match='midpoint_credited_target'):
        solve_pair(*args,midpoint_credited_target=np.zeros((3,3,4)),**options)
