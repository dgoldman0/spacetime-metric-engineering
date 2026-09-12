import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_allclose

from adm_harness.virtual_cell_counterstream import (
    directional_adm_exchange, minimal_counterstream, passive_scattering_rate,
    passive_total_radiation_interval, tetrad_exchange,
)


def metric(t, x, hubble=0., velocity=0.):
    tt, xx = np.meshgrid(t, x, indexing='ij')
    scale = np.exp(hubble*tt)
    zero = np.zeros_like(tt)
    one = np.ones_like(tt)
    return dict(alpha=one, beta=velocity/scale, b=scale, radius=scale*xx,
        alpha_t=zero, beta_t=-hubble*velocity/scale, alpha_x=zero, beta_x=zero,
        logb_t=hubble*one, logb_x=zero, logr_t=hubble*one, logr_x=1/xx)


def test_manufactured_source_free_outgoing_spherical_wave():
    t = np.linspace(0, .2, 101); x = np.linspace(1., 2., 801)
    g = metric(t, x)
    energy = (2+x[None, :]-t[:, None])/x[None, :]**2
    p, f = directional_adm_exchange(energy, energy, t, x, g)
    assert_allclose(p, 0., atol=3e-11)
    assert_allclose(f, 0., atol=3e-11)
    p2, f2 = tetrad_exchange(energy, energy, t, x, g)
    assert np.max(abs(p2[2:-2, 2:-2])) < 2e-5
    assert_allclose(p2, f2, atol=1e-12)


def test_constant_outgoing_injection_requires_counterstream_absorption():
    t = np.linspace(0, .2, 51); x = np.linspace(1., 2., 401)
    g = metric(t, x)
    wave = np.broadcast_to((1+x)/x**2, (len(t), len(x)))
    c, j = minimal_counterstream(wave, 0., 1.)
    pw, fw = directional_adm_exchange(wave, wave, t, x, g)
    pc, fc = directional_adm_exchange(c, j, t, x, g)
    exact = np.broadcast_to(1/x**2, wave.shape)
    assert_allclose(pw, exact, rtol=2e-11, atol=2e-11)
    assert_allclose(pc, -exact, rtol=2e-11, atol=2e-11)
    assert_allclose(fc, -pc, atol=1e-13)
    assert_allclose(fw, pw, atol=1e-13)
    _, permitted = passive_scattering_rate(c, j, pc, fc)
    assert not permitted.any()


def test_directional_geometry_and_material_tetrad_agree_under_refinement():
    errors = []
    for n in (101, 201):
        t = np.linspace(0, .3, n); x = np.linspace(1., 2., n)
        g = metric(t, x, hubble=.17, velocity=.23)
        tt, xx = np.meshgrid(t, x, indexing='ij')
        plus = (1+.2*np.sin(xx-tt))/g['radius']**2
        minus = (.4+.1*np.cos(xx+2*tt))/g['radius']**2
        p, f = directional_adm_exchange(plus+minus, plus-minus, t, x, g)
        p2, f2 = tetrad_exchange(plus+minus, plus-minus, t, x, g)
        errors.append(max(np.max(abs((p-p2)[2:-2, 2:-2])),
                          np.max(abs((f-f2)[2:-2, 2:-2]))))
    assert errors[1] < errors[0]/3.5
    assert errors[1] < 2e-4


def test_passive_total_radiation_interval_with_prepared_balance():
    # A freely transported rising beam can be balanced by a falling
    # counter-beam without local power, if their constant sum fits every time.
    ua = np.array([[.05], [.15]])
    one = np.ones_like(ua); zero = np.zeros_like(ua)
    result = passive_total_radiation_interval(ua, zero, 1.2*one, zero, zero,
        zero, one, one, zero)
    assert_allclose(result['initial_constant_lower'], .3)
    assert_allclose(result['initial_constant_upper'], .4)
    assert_allclose(result['radiation_density_shortfall'], 0.)
    assert np.all(result['counter_density'] >= ua-1e-14)


def test_passive_interval_rejects_incompatible_initial_capacity():
    # Each instant permits the minimal tensor, but a zero-power total
    # radiation inventory cannot rise from <=.2 to >=.3.
    ua = np.array([[.05], [.15]])
    one = np.ones_like(ua); zero = np.zeros_like(ua)
    result = passive_total_radiation_interval(ua, zero, np.array([[.6], [1.2]]),
        zero, zero, zero, one, one, zero)
    assert np.all(result['instantaneous_lower'] <= result['instantaneous_upper'])
    assert_allclose(result['constant_interval_gap'], .1)
    assert_allclose(result['radiation_density_shortfall'], .1)
    assert np.all(result['zero_inventory_constant_gap'] <= result['constant_interval_gap'])


def test_phase_work_can_fail_even_with_zero_radiation_floor():
    ua=np.zeros((3,1)); one=np.ones_like(ua)
    result=passive_total_radiation_interval(ua,ua,.3*one,ua,ua,ua,one,one,
                                           np.array([[0.],[.5],[0.]]))
    assert_allclose(result['zero_inventory_constant_lower'],.5)
    assert_allclose(result['initial_constant_upper'],.1)
    assert_allclose(result['zero_inventory_constant_gap'],.4)


def test_replay_identity_follows_registered_model_manifest_and_rejects_changes(tmp_path):
    script=Path(__file__).resolve().parents[1]/'scripts/audit_virtual_cell_counterstream.py'
    spec=importlib.util.spec_from_file_location('counterstream_cli',script)
    cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(cli)
    cli.ROOT=tmp_path;cli.BASE=tmp_path/'data'
    replay_dir=cli.BASE/'replay';control_dir=cli.BASE/'controls'
    model_dir=cli.BASE/'active_transfer_reservoir'
    for directory in (replay_dir,control_dir,model_dir):directory.mkdir(parents=True)
    replay=replay_dir/'case_factor4_states.npz';control=control_dir/'case_states.npz'
    replay_summary=replay_dir/'case_factor4_summary.json'
    control_summary=control_dir/'case_summary.json'
    model_paths=[model_dir/name for name in ('metric_fine.npz','medium_baseline.npz')]
    for path in [replay,control,replay_summary,control_summary,*model_paths]:
        path.write_bytes(path.name.encode())
    def hashes(paths,relative=False):
        return {(str(path.relative_to(tmp_path)) if relative else path.name):cli.sha256_file(path)
                for path in paths}
    upstream=cli.BASE/'manifest.json'
    upstream.write_text(json.dumps(dict(input_sha256=hashes(model_paths,True))))
    control_manifest=control_dir/'manifest.json'
    control_manifest.write_text(json.dumps(dict(output_sha256=hashes([control,control_summary]),
        input_sha256=hashes([upstream],True))))
    replay_manifest=replay_dir/'manifest.json'
    replay_manifest.write_text(json.dumps(dict(output_sha256=hashes([replay,replay_summary]),
        input_sha256=hashes([control,control_manifest],True))))
    verified,_=cli.verify_input_identity(replay_dir,replay,control)
    assert all(str(path.relative_to(tmp_path)) in {row['path'] for row in verified} for path in model_paths)
    model_paths[0].write_bytes(b'changed')
    with pytest.raises(ValueError,match='changed immutable input'):
        cli.verify_input_identity(replay_dir,replay,control)
