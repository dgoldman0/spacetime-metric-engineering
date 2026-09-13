"""Manufactured local storage/stress gates with original-row verification."""
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
from numpy.testing import assert_allclose
import pytest
from scipy.optimize import OptimizeResult
from scipy.sparse import csr_matrix

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
spec=importlib.util.spec_from_file_location('local_bank_relaxation',SCRIPTS/'run_virtual_cell_local_bank_relaxation.py')
local=importlib.util.module_from_spec(spec);spec.loader.exec_module(local)


def problem(*,ell=1.,radius=1.):
    t=np.linspace(0,1,5);tm=(t[:-1]+t[1:])/2;D=ell*radius**2
    geometry=lambda at:dict(ell=np.full(len(at),ell),radius=np.full(len(at),radius),D=np.full(len(at),D))
    target=np.array([np.full(len(t),2.),np.zeros(len(t)),np.zeros(len(t))])
    midtarget=np.array([np.full(len(tm),2.),np.zeros(len(tm)),np.zeros(len(tm))])
    options=dict(reference_thermal_energy=.5+.1*t,midpoint_reference_thermal_energy=.5+.1*tm,
        reference_receiver_energy=.2+.02*t,midpoint_reference_receiver_energy=.2+.02*tm,
        cold_mass=.4,receiver_capacity=1.,converter_loss=.04*np.diff(t),temperature_floor=.01)
    return (t,target,midtarget,geometry(t),geometry(tm)),options


@pytest.mark.parametrize('floor',[0.,.01])
def test_flat_manufactured_feasible_gate_and_separate_ratings(floor):
    args,options=problem()
    result,state=local.solve_local(*args,**dict(options,temperature_floor=floor))
    assert result['success'] and result['original_lp_rows_and_bounds_verified']
    assert result['added_density']==0 and result['reserved_density_fraction']==0
    assert state['receiver_hot_energy'].max()+state['receiver_cold_energy'].max()<=1.+1e-9
    assert np.min(state['hot_contact_panel_heat'])>=-1e-9
    assert np.min(state['cold_contact_panel_heat'])>=-1e-9
    assert min(state['fluid_temperature'].min(),state['midpoint_fluid_temperature'].min())>=floor-1e-8
    assert result['variables']==5*len(args[0])+2


def test_changing_stress_closed_bank_rejects_unrestricted_thermal_exchange():
    t=np.array([0.,.5,1.]);zero=np.zeros(3)
    geometry=lambda n:{key:np.ones(n) for key in ('radius','ell','D')}
    target=np.array([[1.,1.2,1.],[1.,0.,-1.],[0.,.5,0.]])
    target_mid=(target[:,:-1]+target[:,1:])/2
    options=dict(reference_thermal_energy=zero,midpoint_reference_thermal_energy=zero[:-1],
        reference_receiver_energy=zero,midpoint_reference_receiver_energy=zero[:-1],
        cold_mass=1.,receiver_capacity=0.,converter_loss=zero[:-1],temperature_floor=0.)
    # Endpoints force conserved A+V+K=1 and K=0. Without bank routing the
    # middle can hold A=.1,K=.9,V=0. Routing through a zero-capacity bank
    # makes K constant, while middle stress then allows only A+V<=.7.
    unrestricted,state=local.solve_local(t,target,target_mid,geometry(3),geometry(2),bank_routing=False,**options)
    closed,unused=local.solve_local(t,target,target_mid,geometry(3),geometry(2),**options)
    assert unrestricted['success']
    assert state['thermal_inventory'][1]>.5
    assert not closed['success'] and closed['status']==2
    assert closed['bank_routing_enforced']


def test_nonunit_geometry_credits_and_raw_lp_energy_accounting():
    args,options=problem(ell=2.,radius=3.)
    result,state=local.solve_local(*args,**options)
    assert result['success']
    U0=options['reference_thermal_energy'];Z0=options['reference_receiver_energy']
    assert_allclose(state['credited_target'],args[1]+np.array([(U0+Z0)/18,U0/54,U0/54]),atol=1e-15)
    U0m=options['midpoint_reference_thermal_energy'];Z0m=options['midpoint_reference_receiver_energy']
    assert_allclose(state['midpoint_credited_target'],args[2]+np.array([(U0m+Z0m)/18,U0m/54,U0m/54]),atol=1e-15)
    assert_allclose(state['original_power_panel'],2*.12*np.diff(args[0]),atol=1e-15)
    actual=(np.diff(state['balanced_radiation_inventory'])+4*np.diff(state['amplitude'])
        +2/18**(1/3)*np.diff(state['thermal_inventory'])+2*np.diff(state['receiver_thermal_energy']))
    assert_allclose(actual,state['original_power_panel'],atol=1e-9)
    assert_allclose(state['actual_fluid_power_panel_energy'],
        state['retained_support_to_fluid_panel_energy']+state['hot_to_fluid_panel_heat']
        -state['fluid_to_cold_panel_heat'],atol=1e-9)
    assert np.max(state['counter_panel_energy']-state['hot_contact_panel_heat'])<1e-9
    assert np.max(-state['counter_panel_energy']-state['cold_contact_panel_heat'])<1e-9
    for kind in ('equality','inequality'):
        prefix='lp_'+kind
        matrix=csr_matrix((state[prefix+'_data'],state[prefix+'_indices'],state[prefix+'_indptr']),
                          shape=tuple(state[prefix+'_shape']))
        residual=matrix@state['lp_x']-state[prefix+'_rhs']
        assert (np.abs(residual).max() if kind=='equality' else residual.max())<1e-8
    assert_allclose(state['receiver_fixed_containment_energy'],1/3)


def test_actual_midpoint_stress_can_reject_a_node_feasible_history():
    args,options=problem()
    passed,unused=local.solve_local(*args,**options)
    assert passed['success']
    U0m=options['midpoint_reference_thermal_energy'];Z0m=options['midpoint_reference_receiver_energy']
    midpoint=-np.array([U0m+Z0m,U0m/3,U0m/3])
    rejected,unused=local.solve_local(args[0],args[1],midpoint,*args[3:],**options)
    assert not rejected['success'] and rejected['status']==2


def test_optimal_backend_claim_cannot_hide_original_floor_row_failure(monkeypatch):
    args,options=problem()
    monkeypatch.setattr(local,'linprog',lambda cost,**kwargs:
        OptimizeResult(success=True,status=0,message='manufactured backend claim',nit=0,x=np.zeros(len(cost))))
    result,state=local.solve_local(*args,**options)
    assert result['ordinary_solver_success'] and not result['success']
    assert result['candidate_finite'] and not result['original_lp_rows_and_bounds_verified']
    assert result['inequality_violation']>1e-3
    assert 'lp_x' in state


def test_physical_floor_and_bounded_deadline_are_explicit():
    args,options=problem()
    for extra in ({'temperature_floor':-.01},{'deadline':61.}):
        with pytest.raises(ValueError,match='deadline'):
            local.solve_local(*args,**dict(options,**extra))


def test_recursive_data_provenance_pins_model_and_receiver_without_old_python(tmp_path):
    data=tmp_path/'receiver.npz';data.write_bytes(b'original receiver')
    model=tmp_path/'model.npz';model.write_bytes(b'original model')
    python=tmp_path/'old.py';python.write_text('current runtime bytes')
    nested=tmp_path/'upstream'/'manifest.json';nested.parent.mkdir()
    nested.write_text(json.dumps(dict(input_sha256={'receiver.npz':local.sha256_file(data),
        'model.npz':local.sha256_file(model),'old.py':'historical-python-identity'})))
    source=tmp_path/'manifest.json'
    source.write_text(json.dumps(dict(input_sha256={'upstream/manifest.json':local.sha256_file(nested)})))
    hashes=local.verified_data_dependencies(source,tmp_path)
    assert hashes['receiver.npz']==local.sha256_file(data)
    assert hashes['model.npz']==local.sha256_file(model)
    assert hashes['upstream/manifest.json']==local.sha256_file(nested)
    assert 'old.py' not in hashes
    data.write_bytes(b'changed receiver')
    with pytest.raises(RuntimeError,match='changed upstream data: receiver.npz'):
        local.verified_data_dependencies(source,tmp_path)


def _pin_histories(monkeypatch, histories):
    """Fix a physical witness while leaving the original LP checks intact."""
    original=local.linprog
    def pinned(cost,**kwargs):
        bounds=np.array(kwargs['bounds'],copy=True)
        for block,values in enumerate(histories):
            for i,value in enumerate(values):bounds[block*len(values)+i]=value
        return original(cost,**dict(kwargs,bounds=bounds))
    monkeypatch.setattr(local,'linprog',pinned)


def test_hot_donor_rejects_zero_inventory_converter_passthrough(monkeypatch):
    args,options=problem();t=args[0];zero=np.zeros(len(t))
    _pin_histories(monkeypatch,[zero,np.full(len(t),.1),.1*t,zero,zero])
    options.update(reference_thermal_energy=.1*t,
        midpoint_reference_thermal_energy=.1*(t[:-1]+t[1:])/2,
        reference_receiver_energy=zero,midpoint_reference_receiver_energy=zero[:-1],
        converter_loss=.02*np.diff(t),temperature_floor=0.,proper_duration=np.diff(t))
    unbounded,_=local.solve_local(*args,**options)
    bounded,_=local.solve_local(*args,hot_donor_turnover=10.,**options)
    assert unbounded['success']
    assert not bounded['success'] and bounded['status']==2
    assert bounded['hot_endpoint_donor_bound_enforced']
    assert bounded['local_necessary_relaxation_passes'] is False


def test_prepared_hot_inventory_covers_finite_endpoint_donor_rows(monkeypatch):
    args,options=problem();t=args[0];zero=np.zeros(len(t))
    _pin_histories(monkeypatch,[zero,np.full(len(t),.1),.1*t,np.full(len(t),.1),zero])
    options.update(reference_thermal_energy=.1*t,
        midpoint_reference_thermal_energy=.1*(t[:-1]+t[1:])/2,
        reference_receiver_energy=zero,midpoint_reference_receiver_energy=zero[:-1],
        converter_loss=.02*np.diff(t),temperature_floor=0.,proper_duration=np.diff(t))
    result,state=local.solve_local(*args,hot_donor_turnover=1.,**options)
    assert result['success'] and result['original_lp_rows_and_bounds_verified']
    assert_allclose(state['hot_endpoint_donor_margin'],.08*np.diff(t)[None,:]+np.zeros((2,len(t)-1)))
    assert result['hot_endpoint_donor_violation']==0.
    assert sum('hot_donor_endpoint' in tag for tag in state['lp_inequality_labels'])==2*(len(t)-1)


def test_conservative_cold_bound_can_reject_valid_photon_supplied_receipt(monkeypatch):
    args,options=problem();t=args[0];zero=np.zeros(len(t))
    _pin_histories(monkeypatch,[zero,.5-.2*t,zero,zero,.2*t])
    options.update(reference_thermal_energy=zero,midpoint_reference_thermal_energy=zero[:-1],
        reference_receiver_energy=zero,midpoint_reference_receiver_energy=zero[:-1],
        converter_loss=zero[:-1],temperature_floor=0.,proper_duration=np.diff(t))
    relaxed,state=local.solve_local(*args,hot_donor_turnover=10.,**options)
    conservative,_=local.solve_local(*args,hot_donor_turnover=10.,cold_fluid_donor_turnover=10.,**options)
    assert relaxed['success']
    assert_allclose(state['counter_to_cold_panel_heat'],.2*np.diff(t),atol=1e-12)
    assert not conservative['success'] and conservative['status']==2
    assert conservative['local_necessary_relaxation_passes'] is None
    assert conservative['local_conservative_donor_comparison_passes'] is False
    assert conservative['cold_fluid_bound_is_sufficient_conservative_comparison']


def test_donor_options_require_positive_turnover_and_proper_duration():
    args,options=problem()
    for key in ('hot_donor_turnover','cold_fluid_donor_turnover'):
        for invalid in (0.,-1.,float('nan'),True):
            with pytest.raises(ValueError,match=key):
                local.solve_local(*args,**dict(options,**{key:invalid}))
        with pytest.raises(ValueError,match='proper_duration'):
            local.solve_local(*args,**dict(options,**{key:10.}))
        with pytest.raises(ValueError,match='proper duration'):
            local.solve_local(*args,**dict(options,proper_duration=np.zeros(4),**{key:10.}))
