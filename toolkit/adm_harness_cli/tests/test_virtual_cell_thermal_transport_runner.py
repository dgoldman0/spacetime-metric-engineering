"""Controlled guide/interface omission changes only the two supplied costs."""
from pathlib import Path
from types import SimpleNamespace
import sys

import numpy as np
from numpy.testing import assert_allclose
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import run_virtual_cell_thermal_transport as runner
import audit_virtual_cell_receiver_contact as contact


def specification(output,omit=False,*,budget=True,zero=True):
    return (-1.975,.0005,4,1,0.,str(output),60.,'highs-ipm',
            True,True,10.,budget,True,False,.01,True,True,False,True,True,
            True,False,zero,omit)


class FlatHistory:
    def __init__(self,*unused):
        t=np.array([0.,.5]);x=np.array([-2.1,-1.8]);one=np.ones((2,2))
        def metric(now,at):
            return SimpleNamespace(beta=np.zeros(len(at)),alpha=np.ones(len(at)),
                b=np.ones(len(at)),k_l=np.zeros(len(at)),alpha_x=np.zeros(len(at)))
        old=dict(t=t,x=x,thermal=.1*one,number=.2*np.ones(2))
        reference=SimpleNamespace(t=t,x=x,h=SimpleNamespace(state=old,model=SimpleNamespace(metric=metric)))
        self.h=SimpleNamespace(reference=reference,state=dict(heat=.2*one,heat_cap=np.ones(2)))
        self.state=dict(t=t)

    def coefficients(self,t,x):
        one=np.ones((len(t),len(x)))
        return dict(D=one,ell=one,radius=one,lapse=one,v=one*0,Q=one*0)

    def energy(self,x):
        return SimpleNamespace(evaluate=lambda t:(10*np.ones((len(t),len(x))),))

    def pressure(self,t,x):return (np.zeros((len(t),len(x))),)


def assert_same(left,right):
    if isinstance(left,np.ndarray):assert_allclose(left,right,atol=0,rtol=0)
    elif isinstance(left,dict):
        assert left.keys()==right.keys()
        for key in left:assert_same(left[key],right[key])
    elif isinstance(left,(tuple,list)):
        assert len(left)==len(right)
        for a,b in zip(left,right):assert_same(a,b)
    else:assert left==right


def test_omission_forwards_only_guide_interface_changes_and_records_scope(monkeypatch,tmp_path):
    monkeypatch.setattr(runner,'DenseHistory',FlatHistory)
    monkeypatch.setattr(contact,'integrated_loss',lambda h,t,x,order:
        (np.zeros((len(t)-1,len(x))),np.diff(t)[:,None]*np.ones((1,len(x)))))
    calls=[]
    def inspect_only(*args,**kwargs):
        calls.append((args,kwargs))
        return dict(success=False,status=1,message='manufactured interception; no solve')
    monkeypatch.setattr(runner,'solve_pair',inspect_only)
    regular=runner.evaluate(specification(tmp_path))
    relaxed=runner.evaluate(specification(tmp_path,True))
    assert len(calls)==2
    assert_same(calls[0][0],calls[1][0])
    for key,value in calls[0][1].items():
        if key not in ('interface_sigma','guide_drift'):assert_same(value,calls[1][1][key])
    assert calls[0][1]['interface_sigma']==1e-7 and calls[0][1]['guide_drift']==.5
    assert calls[1][1]['interface_sigma']==0 and calls[1][1]['guide_drift'] is None
    for key in ('coherent_cells','return_heat','wave_envelope','matched_pair','split_receiver',
                'bank_counter_relaxation','target_budget_only','zero_objective'):
        assert calls[1][1][key] is True
    assert calls[1][1]['receiver_contact'][2]==10.
    assert not regular['guide_interface_costs_omitted']
    assert relaxed['guide_interface_costs_omitted'] and relaxed['favorable_transport_only_relaxation']
    assert relaxed['guide_drift'] is None and relaxed['interface_sigma']==0
    assert relaxed['label'].endswith('_omit_guide_interface_costs')
    assert 'transport-only necessity relaxation' in relaxed['scope']
    assert not relaxed['full_source_construction_supplied']
    assert not relaxed['independent_curved_geometry_replay_supplied']
    assert not relaxed['guide_material_clearance_supplied']


@pytest.mark.parametrize('flags',[[],['--target-budget-only']])
def test_omission_cli_requires_fixed_budget_and_zero_objective(monkeypatch,flags):
    monkeypatch.setattr(sys,'argv',['runner','--omit-guide-interface-costs']+flags)
    with pytest.raises(SystemExit) as error:runner.main()
    assert error.value.code==2


@pytest.mark.parametrize('budget,zero',[(False,True),(True,False)])
def test_programmatic_omission_requires_same_contract(tmp_path,budget,zero):
    with pytest.raises(ValueError,match='fixed budget and zero objective'):
        runner.evaluate(specification(tmp_path,True,budget=budget,zero=zero))
