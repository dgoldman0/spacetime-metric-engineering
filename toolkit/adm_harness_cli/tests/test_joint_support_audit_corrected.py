from types import SimpleNamespace

import numpy as np
from numpy.testing import assert_allclose

from adm_harness.active_transfer_reservoir import divergence_projections
from adm_harness.pressure_linked_storage import fluid_coefficients
from audit_joint_support_corrected import continuum_check
from test_joint_support_audit import SmoothMetric, scalar_fields


def test_time_dependent_electric_field_force_in_moving_frame():
    """Compare the complete field projection to an independent covariant divergence.

    This has nonzero field time derivative and material velocity: the earlier
    manufactured material-only audit could not detect the missing boost term.
    """
    model = SmoothMetric()
    t = np.array([.5, .55, .6])
    x = np.array([-.3, 0., .3])
    zero = np.zeros((3, 3))
    fields = scalar_fields(t[:, None], x[None, :])
    old = dict(t=t, x=x, flux_energy=zero, number=np.zeros(3), thermal=fields[0])
    history = SimpleNamespace(
        knots=x, reference=SimpleNamespace(h=SimpleNamespace(model=model, state=old), t=t, x=x),
        allocation=lambda positions: (np.zeros_like(positions), np.zeros_like(positions)),
        state=dict(heat=zero, heat_cap=np.zeros(3)))
    state = dict(t=t, x=x, thermal=zero, support_energy=fields[1],
                 radial_volume=fields[2], angular_volume=fields[3])
    baseline = continuum_check(history, state, preserve_reference_fluid=True)
    old['flux_energy'] = .7 - .03*t[:, None] + .08*x[None, :]
    actual = continuum_check(history, state, preserve_reference_fluid=True)
    at, ax = actual['t'], actual['x']
    c = fluid_coefficients(model, at, ax)
    charge = -.03/(c['lapse']*c['radius']**4)
    wave_force = np.maximum(charge, 0)/.98 + .98*np.maximum(-charge, 0)
    wave_power = -np.maximum(charge, 0)/.98 + .98*np.maximum(-charge, 0)

    def tensor(time, positions):
        g = model.metric(time, positions)
        energy = (.7 - .03*time + .08*positions)/g.radius**4
        return np.array([energy, -energy, np.zeros_like(energy), energy])

    eps = 1e-5
    for i, time in enumerate(at):
        g = model.metric(time, ax)
        dt = (tensor(time+eps, ax)-tensor(time-eps, ax))/(2*eps)
        dx = (tensor(time, ax+eps)-tensor(time, ax-eps))/(2*eps)
        power, force = divergence_projections(g, tensor(time, ax), dt, dx)
        assert_allclose(actual['force'][i]-baseline['force'][i]-wave_force[i],
                        c['gamma'][i]*(force-c['v'][i]*power), atol=2e-11, rtol=2e-8)
        assert_allclose(actual['power'][i]-baseline['power'][i]-wave_power[i],
                        c['gamma'][i]*(power-c['v'][i]*force), atol=2e-11, rtol=2e-8)
        # The omitted term is independently large enough to fail the tolerance.
        assert np.max(abs(c['v'][i]*charge[i])) > 1e-5
