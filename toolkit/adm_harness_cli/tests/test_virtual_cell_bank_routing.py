import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest
from numpy.testing import assert_allclose

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0,str(SCRIPTS))
spec=importlib.util.spec_from_file_location('bank_routing',SCRIPTS/'audit_virtual_cell_bank_routing.py')
bank=importlib.util.module_from_spec(spec);spec.loader.exec_module(bank)


def test_valid_reroute_preserves_both_bank_duties_and_fluid_power():
    p=np.array([[.3],[-.2]]);qh=np.array([[.5],[.1]]);qc=np.array([[.2],[.4]])
    fixed=np.array([[.07],[-.04]])
    result=bank.routing_traffic(p,qh,qc)
    assert result['compatible'].all()
    assert_allclose(result['emission']-result['absorption'],p)
    assert_allclose(result['redirected_hot_to_fluid']+result['emission'],qh)
    assert_allclose(result['redirected_fluid_to_cold']+result['absorption'],qc)
    assert_allclose(result['redirected_hot_to_fluid']-result['redirected_fluid_to_cold']+fixed,
                    qh-qc+fixed-p)


def test_failed_traffic_cannot_be_repaired_by_an_extra_simultaneous_cycle():
    p=np.array([[.6],[-.5]]);qh=np.array([[.5],[.1]]);qc=np.array([[.2],[.4]])
    minimum=bank.routing_traffic(p,qh,qc)
    extra=bank.routing_traffic(p,qh,qc,extra_cycle=.3)
    assert not minimum['compatible'].any() and not extra['compatible'].any()
    assert np.all(extra['hot_margin']<=minimum['hot_margin'])
    assert np.all(extra['cold_margin']<=minimum['cold_margin'])
    assert_allclose(extra['emission']-extra['absorption'],p)


def test_hot_cold_temperature_interval_can_resolve_incompatible_fluid_ordering():
    p=np.array([[1.],[-1.]]);counter=np.array([[4.],[1.]])
    radius=np.ones((2,1));fluid=np.ones((2,1))
    original=bank.guided_interval(p,counter,radius,fluid)
    assert not original['compatible'][0]
    mixed=bank.mixed_bank_interval(p,counter,radius,2*fluid,.5*fluid)
    assert mixed['compatible'][0]
    assert_allclose(mixed['lower'],1.)
    assert_allclose(mixed['upper'],4.)
    # Photon positivity remains necessary even when both bath temperatures
    # would otherwise provide a wide interval.
    empty=bank.mixed_bank_interval(-np.ones((1,1)),np.zeros((1,1)),np.ones((1,1)),
                                    np.ones((1,1)),.1*np.ones((1,1)))
    assert not empty['compatible'][0]


def test_counter_donor_rate_keeps_small_positive_populations_and_flags_empty():
    rate,empty,unresolved=bank.counter_donor_rate(
        np.array([1.,1.,1.]),np.array([1e-20,0.,1e-320]),np.ones(3,bool))
    assert_allclose(rate[0],1e20)
    assert not empty[0] and not unresolved[0]
    assert empty[1] and not unresolved[1]
    assert unresolved[2] and not empty[2]


def test_archive_verification_checks_products_and_recorded_data_dependencies(tmp_path,monkeypatch):
    monkeypatch.setattr(bank,'ROOT',tmp_path)
    folder=tmp_path/'archive';folder.mkdir()
    product=folder/'state.npz';product.write_bytes(b'original product')
    dependency=tmp_path/'upstream.json';dependency.write_text('{}')
    manifest=dict(output_sha256={product.name:bank.sha256_file(product)},
        input_sha256={'upstream.json':bank.sha256_file(dependency)})
    (folder/'manifest.json').write_text(json.dumps(manifest))
    _,checked=bank.verify_archive(folder)
    assert 'archive/state.npz' in checked and 'upstream.json' in checked
    product.write_bytes(b'changed product')
    with pytest.raises(RuntimeError,match='changed parent product'):
        bank.verify_archive(folder)
    product.write_bytes(b'original product')
    dependency.write_text('{"changed":true}')
    with pytest.raises(RuntimeError,match='changed parent data dependency'):
        bank.verify_archive(folder)
