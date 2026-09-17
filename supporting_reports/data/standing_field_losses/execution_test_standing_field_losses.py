import numpy as np
from numpy.testing import assert_allclose

from adm_harness.material_reconfiguration import PRESSURE_BASIS
from adm_harness.standing_field_losses import (
    decay_rate_ceiling, photon_to_maxwell, residence_exposure,
)


def test_field_substitution_preserves_energy_and_each_pressure_channel():
    rng = np.random.default_rng(915)
    fields = rng.uniform(0, 2, (4, 7, 5))
    for fraction in (0., .3, 1.):
        replaced = photon_to_maxwell(fields, fraction)
        assert np.all(replaced >= 0)
        assert_allclose(replaced.sum(axis=0), fields.sum(axis=0), rtol=3e-16)
        assert_allclose(np.einsum("ij,j...->i...", PRESSURE_BASIS[:, 6:10], replaced),
                        np.einsum("ij,j...->i...", PRESSURE_BASIS[:, 6:10], fields), atol=2e-15)


def test_residence_integral_and_continuous_panel_screen():
    times = np.array([0., .2, 1., 3.])
    fields = np.broadcast_to((2+times)[None, :, None], (4, 4, 2))
    dt = np.broadcast_to(np.diff(times)[:, None], (3, 2))
    I = residence_exposure(fields, dt)
    expected = 2*times[1:]+times[1:]**2/2
    assert_allclose(I, np.broadcast_to(expected[None, :, None], I.shape))
    reserve = np.array([[.1, .2], [.3, .4], [.2, .5]])
    result = decay_rate_ceiling(I[2:].sum(axis=0), reserve, replacement_factor=1.2)
    assert_allclose(result["rate"], np.min(reserve/(2*expected[:, None]*1.2), axis=0))
    for panel in range(3):
        for t in np.linspace(times[panel], times[panel+1], 11):
            cost = 1.2*result["rate"]*2*(2*t+t*t/2)
            assert np.all(cost <= reserve[panel]*(1+1e-14))


def test_zero_photon_exposure_has_no_photon_decay_charge():
    r = decay_rate_ceiling(np.zeros((3, 2)), np.ones((3, 2)))
    assert np.isinf(r["rate"]).all()
