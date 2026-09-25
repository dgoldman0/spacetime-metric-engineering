import math

import numpy as np
import pytest

from adm_harness import axial_track as ax
from adm_harness import compartment_service as cs
from adm_harness import source_scaling as ss
from adm_harness.numerical_einstein import einstein_fd

SERVICE = cs.CompartmentService()
DESIGN = cs.axial_design(SERVICE)


def direct_metric(service, design):
    """Four-dimensional metric of the compartment design built from its profiles, without jets."""
    fraction = design.track.join_fraction

    def metric(x):
        s, z, r, _ = x
        radius = np.array([r])
        chi = {name: ax.layer_blend(radius, design.layers[name], fraction)[0][0] for name in ("alpha", "beta")}
        (e, _, _), h = ax.sheath_jets(radius, s, z, design)
        edge = ax.layer_blend(radius, service.hole_radius, fraction)[0][0]
        log_alpha = chi["alpha"]*service.plateau(s, z)+h["v"]*e[0]+edge*service.hole(s, z)
        alpha, shift = math.exp(log_alpha), chi["beta"]*service.shift(s, z)
        g = np.zeros((4, 4))
        g[0, 0] = -alpha*alpha+shift*shift
        g[0, 1] = g[1, 0] = shift
        g[1, 1] = 1.
        g[2, 2] = 1.
        g[3, 3] = r*r
        return g
    return metric


@pytest.mark.parametrize("s,offset,r", [(.5, -1.4, 2.4), (3., 2.8, 4.9), (3., -1.7, 3.0), (6.6, 3.3, 5.6),
                                        (-2.2, .6, 2.1), (8.4, -4.9, 9.7)])
def test_compartment_tensor_matches_brute_force_kernel(s, offset, r):
    z = SERVICE.packet_position(s)+offset
    generated = cs.frame_tensor(SERVICE, DESIGN, s, z, [r])[0]
    metric = direct_metric(SERVICE, DESIGN)
    einstein = einstein_fd(metric, [s, z, r, 0.], 5e-4, varying=3)
    f = cs.fields(SERVICE, DESIGN, s, z, [r])
    frame = ss.normal_tetrad(f)[0]
    reference = frame@einstein@frame.T/ax.EIGHT_PI
    assert np.max(np.abs(generated-reference)) < 5e-5*max(np.max(np.abs(reference)), 1.)


@pytest.mark.parametrize("clock_log", [0., math.log(.2), 4.])
def test_compartment_is_flat_and_the_packet_rests_on_normal_observers(clock_log):
    service = cs.CompartmentService(clock_log=clock_log)
    design = cs.axial_design(service)
    for s in (-2.2, .4, 1.2, 3., 6.3, 7.2, 8.6):
        c = service.packet_position(s)
        for offset in np.linspace(-service.half_width, service.half_width, 5):
            f = cs.fields(service, design, s, c+offset, [.875, 1.6])
            g, dg, ddg = ss.metric_jets(f)
            components = ss.frame_riemann(ss.riemann(g, dg, ddg), ss.normal_tetrad(f))
            assert np.max(np.abs(components)) < 1e-12
            assert f["alpha"][0] == pytest.approx(service.clock_rate(s), rel=1e-12)
            assert f["beta"][0] == pytest.approx(-service.carry_speed(s), abs=1e-14)
            assert abs(f["alpha_z"][0]) < 1e-12 and abs(f["alpha_r"][0]) < 1e-12
        tensor = cs.frame_tensor(service, design, s, c, [0., 1.])
        assert np.max(np.abs(tensor)) < 1e-12


def test_exterior_and_times_outside_the_schedule_are_minkowski():
    radius = np.array([0., 5., 12., 14.])
    for s, offset in ((-4., 0.), (10.5, 0.), (3., SERVICE.extent+.5), (3., -SERVICE.extent-.5)):
        z = SERVICE.packet_position(s)+offset
        assert np.max(np.abs(cs.frame_tensor(SERVICE, DESIGN, s, z, radius))) < 1e-12
    assert np.max(np.abs(cs.frame_tensor(SERVICE, DESIGN, 3., SERVICE.packet_position(3.), [13.5]))) < 1e-12


def test_compartment_validation():
    with pytest.raises(ValueError):
        cs.CompartmentService(schedule=(-.5, 9., 1.))
    with pytest.raises(ValueError):
        cs.CompartmentService(schedule=(-2.5, 6., 1.))
    with pytest.raises(ValueError):
        cs.CompartmentService(hole_edge=0.)
    with pytest.raises(ValueError):
        cs.CompartmentService(slope_ramp=2.)
