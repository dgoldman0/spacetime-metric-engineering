import numpy as np
import pytest

from adm_harness.virtual_cell_ports import (beam_port_moments, counterstream_moments,
    instrumented_propagate, phase_port_traction, port_flux_from_rest)


def test_matched_beams_cancel_recoil_with_nonzero_traffic():
    incident=np.array([[3.,3.],[0.,0.]])
    returned=np.array([[1.,1.],[2.,2.]])
    heat=np.array([[.5,.5],[0.,0.]])
    supply,reaction=beam_port_moments(incident,returned,heat)
    np.testing.assert_allclose(supply.sum(axis=1),[3.,-4.])
    np.testing.assert_allclose(reaction.sum(axis=1),0.)
    np.testing.assert_allclose(abs(reaction).sum(axis=1),[9.,4.])


def test_asymmetric_emission_and_recovery_impulses_add():
    # One joule emitted to the right gives -1 recoil. One joule recovered
    # from the right also gives -1, although their net supplied work is zero.
    supply,reaction=beam_port_moments(np.array([[0.,1.]]),np.array([[0.,1.]]),np.zeros((1,2)))
    assert supply.sum()==0.
    assert reaction.sum()==-2.
    assert phase_port_traction(.4,.1)==pytest.approx(-1.2*np.pi)


@pytest.mark.parametrize('v',[-.6,0.,.4])
@pytest.mark.parametrize('direction',[-1,1])
def test_fixed_port_flux_boost_matches_material_stress(v,direction):
    alpha,b,radius,mu=2.7,1.4,3.2,.7
    gamma=1/np.sqrt(1-v*v); beta=v*alpha/b
    adm_volume_energy=b*radius**2*mu
    coordinate_speed=-beta+direction*alpha/b
    transformed=4*np.pi*abs(coordinate_speed)*adm_volume_energy*gamma*(1-direction*v)
    rest=gamma**2*(1-direction*v)**2*mu
    assert transformed==pytest.approx(port_flux_from_rest(rest,radius,alpha/gamma))


def test_counterstream_cancels_current_but_retains_positive_pressure():
    inc=np.array([3.,1.]); useful=np.array([1.,4.]); heat=np.array([.5,.25]); d=np.array([-1.,1.])
    tensor=counterstream_moments(inc,useful,heat,d)
    np.testing.assert_allclose(tensor[2]+d*(inc-useful-heat),0.)
    np.testing.assert_allclose(tensor[0],abs(tensor[2]))
    np.testing.assert_allclose(tensor[1],tensor[0])
    assert np.all(tensor[0]>0)


@pytest.mark.parametrize('backwards',[False,True])
def test_flat_single_cell_exact_inventory_and_physical_ledger(backwards):
    t=np.linspace(0.,2.,41); edges=np.array([0.,1.]); q=.3
    # A one-cell source with unit crossing rate has y'=q-y. Backward absorption
    # uses the same positive equation with reversed physical time.
    direction=-1 if backwards else 1
    def coefficients(now,interval):
        return np.full(2,float(direction)),np.zeros(1),np.full(1,q)
    r=instrumented_propagate(t,edges,coefficients,lambda now:(1.,1.),
        backwards=backwards,port_face=-1,cfl=.025)
    elapsed=2-t if backwards else t
    exact=q*(1-np.exp(-elapsed))
    np.testing.assert_allclose(r['state'][:,0],exact,atol=1.2e-5,rtol=0)
    assert abs(r['ledger'][:,4]).max()<1e-14
    physical_sign=-1 if backwards else 1
    assert r['ledger'][:,2].sum()==pytest.approx(physical_sign*4*np.pi*q*2)
    assert r['port_energy'].sum()==pytest.approx(4*np.pi*(q*2-exact.max()),abs=1.5e-4)
    assert r['ledger'][:,0].sum()==pytest.approx(-physical_sign*r['port_energy'].sum())


def test_pure_geometric_gain_and_synchronized_forward_backward_observations():
    t=np.array([0.,.2,.7]); steps=np.array([20,50])
    def coefficients(now,interval):
        return np.zeros(2),np.array([.5]),np.array([.3])
    a=instrumented_propagate(t,[0.,1.],coefficients,lambda now:(1.,1.),port_face=0,substeps=steps)
    b=instrumented_propagate(t,[0.,1.],coefficients,lambda now:(1.,1.),port_face=0,substeps=steps,backwards=True)
    np.testing.assert_array_equal(a['port_time'],b['port_time'])
    assert a['state'][-1,0]==pytest.approx(.6*(np.exp(.35)-1),abs=2e-6)
    assert b['state'][0,0]==pytest.approx(.6*(1-np.exp(-.35)),abs=2e-6)
    assert a['ledger'][:,1].sum()>0
    assert b['ledger'][:,1].sum()>0
    assert a['port_energy'].sum()==0.
    assert b['port_energy'].sum()==0.


def test_refuse_invalid_port_and_step_schedule():
    c=lambda t,i:(np.ones(2),np.zeros(1),np.ones(1))
    with pytest.raises(ValueError):
        instrumented_propagate([0.,1.],[0.,1.],c,lambda t:(1.,1.),port_face=1)
    with pytest.raises(ValueError):
        instrumented_propagate([0.,1.],[0.,1.],c,lambda t:(1.,1.),port_face=0,substeps=[0])


def test_linked_model_identity_and_tampering(tmp_path,monkeypatch):
    import hashlib
    import json
    from pathlib import Path
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'scripts'))
    from audit_virtual_cell_ports import verify_registered_model
    folder=tmp_path/'supporting_reports/data/active_transfer_reservoir'; folder.mkdir(parents=True)
    hashes={}
    for filename in ('metric_fine.npz','medium_baseline.npz'):
        path=folder/filename; path.write_bytes(filename.encode())
        hashes[str(path.relative_to(tmp_path))]=hashlib.sha256(path.read_bytes()).hexdigest()
    linked=tmp_path/'older/manifest.json'; linked.parent.mkdir()
    linked.write_text(json.dumps(dict(input_sha256=hashes)))
    source=tmp_path/'manifest.json'
    source.write_text(json.dumps(dict(input_sha256={str(linked.relative_to(tmp_path)):
        hashlib.sha256(linked.read_bytes()).hexdigest()})))
    verified=verify_registered_model(source,tmp_path)
    assert all(verified[key]==value for key,value in hashes.items())
    (folder/'metric_fine.npz').write_bytes(b'changed model')
    with pytest.raises(RuntimeError,match='changed registered model'):
        verify_registered_model(source,tmp_path)
    linked.write_text('{}')
    with pytest.raises(RuntimeError,match='changed model-manifest link'):
        verify_registered_model(source,tmp_path)


def test_known_panel_interpolation_preserves_registered_coefficients(monkeypatch):
    from pathlib import Path
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'scripts'))
    from audit_virtual_cell_ports import interp
    t=np.array([0.,.07,.2,1.285]); values=np.array([[1.,2.],[4.,-3.],[.4,.1],[2.,3.]])
    for i in range(len(t)-1):
        for now in np.linspace(t[i],t[i+1],9):
            expected=[np.interp(now,t,values[:,j]) for j in range(2)]
            np.testing.assert_allclose(interp(t,values,now,i),expected,atol=2e-15,rtol=0)
