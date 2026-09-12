import numpy as np
from numpy.testing import assert_allclose

from adm_harness.active_transfer_reservoir import divergence_projections
from adm_harness.composite_capacitor import anisotropic_moments
from adm_harness.joint_support_projection import project_balance
from adm_harness.pressure_linked_storage import fluid_coefficients
from test_joint_support_audit import SmoothMetric


def manufactured_fields(t, x):
    return 2+.1*t+.2*x+.03*t*x, .05+.003*t+.007*x, .01+.002*t+np.zeros_like(x)


def test_projection_recovers_manufactured_curved_shifted_tensor():
    model = SmoothMetric()

    def tensor(t, x):
        g = model.metric(t, x)
        v = g.b*g.beta/g.alpha
        d = g.b*g.radius**2/np.sqrt(1-v*v)
        m, p, q = manufactured_fields(t, x)
        return anisotropic_moments(m/d, p, q/d, v)

    def coefficients(t, x):
        c = fluid_coefficients(model, t, x)
        powers, forces, radial_rate = [], [], []
        eps = 1e-5
        for i, time in enumerate(t):
            g = model.metric(time, x)
            dt = (tensor(time+eps, x)-tensor(time-eps, x))/(2*eps)
            dx = (tensor(time, x+eps)-tensor(time, x-eps))/(2*eps)
            power, force = divergence_projections(g, tensor(time, x), dt, dx)
            powers.append(-c['gamma'][i]*(power-c['v'][i]*force))
            forces.append(-c['gamma'][i]*(force-c['v'][i]*power))
            radial_rate.append(g.logr_t)
        lr = np.array(radial_rate)
        c.update(ell=c['gamma']*c['b'], D=c['rest_volume'], log_radius_t=lr,
                 log_ell_t=c['volume_rate']-2*lr,
                 Q=manufactured_fields(t[:, None], x[None, :])[2],
                 fixed_power=np.array(powers), fixed_force=np.array(forces))
        return c

    t = np.linspace(.5, .8, 9); x = np.linspace(-.3, .3, 17)
    m, p, unused = manufactured_fields(t[:, None], x[None, :])
    actual = project_balance(t, x, coefficients, m[0], p[:, 0])
    assert_allclose(actual['support_energy'], m, atol=3e-8, rtol=1e-8)
    assert_allclose(actual['radial_pressure'], p, atol=3e-8, rtol=1e-8)
    assert actual['maximum_block_residual'] < 1e-10


def test_static_force_requires_a_transmitted_end_reaction():
    def c(t, x):
        one = np.ones((len(t), len(x))); zero = 0*one
        return dict(ell=one, D=one, lapse=one, v=zero, acceleration=zero,
                    angular_gradient=zero, log_ell_t=zero, log_radius_t=zero,
                    Q=zero, fixed_power=zero, fixed_force=.2*one)
    t = np.linspace(0, 1, 5); x = np.linspace(0, 2, 9)
    result = project_balance(t, x, c, np.ones(len(x)), np.zeros(len(t)))
    assert_allclose(result['radial_pressure'], np.broadcast_to(-.2*x, (len(t),len(x))), atol=1e-13)
    assert_allclose(result['support_energy'], 1.)
    assert_allclose(result['radial_pressure'][:, -1], -.4)
