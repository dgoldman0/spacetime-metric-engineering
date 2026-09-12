import numpy as np
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
