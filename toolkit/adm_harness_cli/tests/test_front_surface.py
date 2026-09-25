import math

import numpy as np
import pytest

from adm_harness import axial_track as ax
from adm_harness import compartment_service as cs
from adm_harness import front_surface as fs
from adm_harness import source_scaling as ss
from adm_harness.numerical_einstein import einstein_fd

SERVICE = cs.CompartmentService()
DESIGN = cs.axial_design(SERVICE)
SHELF = fs.ForwardShelf()
STATIC_SHELF = fs.ForwardShelf(lead_speed=math.inf)
CONE = fs.ConeFront()


def direct_metric(front):
    """Four-dimensional metric built from the profiles and the front term, without jets."""
    def metric(x):
        s, z, r, _ = x
        log_alpha, shift = fs.point_log_lapse_and_shift(SERVICE, DESIGN, front, s, z, r)
        alpha = math.exp(log_alpha)
        g = np.zeros((4, 4))
        g[0, 0] = -alpha*alpha+shift*shift
        g[0, 1] = g[1, 0] = shift
        g[1, 1] = 1.
        g[2, 2] = 1.
        g[3, 3] = r*r
        return g
    return metric


CASES = [(SHELF, 3., 9.5, 15.1), (SHELF, 3., 5.6, 6.), (SHELF, -2., 10.1, 4.), (STATIC_SHELF, 3., 13., 14.4),
         (CONE, 3., 60.3, .3), (CONE, 3., 58., 1.1), (CONE, 3., 30., 8.4), (CONE, 3., 5.4, 14.6),
         (CONE, 3., 4.5, 3.), (CONE, .6, 20., 1.5), (CONE, 3., 2.8, 4.9)]


@pytest.mark.parametrize("front,s,offset,r", CASES)
def test_front_tensor_matches_brute_force_kernel(front, s, offset, r):
    z = SERVICE.packet_position(s)+offset
    generated = fs.frame_tensor(SERVICE, DESIGN, front, s, z, [r])[0]
    einstein = einstein_fd(direct_metric(front), [s, z, r, 0.], 5e-4, varying=3)
    f = fs.fields(SERVICE, DESIGN, front, s, z, [r])
    frame = ss.normal_tetrad(f)[0]
    reference = frame@einstein@frame.T/ax.EIGHT_PI
    assert np.max(np.abs(generated-reference)) < 5e-5*max(np.max(np.abs(reference)), 1.)


@pytest.mark.parametrize("front", [SHELF, CONE])
def test_front_leaves_the_shift_region_unchanged(front):
    radius = np.array([.3, 2., 5., 9., 12.])
    for s in (-2., .7, 3., 6.4, 8.):
        c = SERVICE.packet_position(s)
        for offset in (-6., -2.5, 0., 2., 4.2):
            base = cs.fields(SERVICE, DESIGN, s, c+offset, radius)
            with_front = fs.fields(SERVICE, DESIGN, front, s, c+offset, radius)
            for key in base:
                assert np.allclose(base[key], with_front[key], rtol=0, atol=1e-13), key


@pytest.mark.parametrize("front,s,offset,r", [(SHELF, 3., 11., 15.), (SHELF, 3., 17.5, 2.), (CONE, 3., 40., 5.),
                                              (CONE, 3., 62., .4), (CONE, 3., 6., 15.)])
def test_front_regions_carry_stress_without_energy_or_flux(front, s, offset, r):
    z = SERVICE.packet_position(s)+offset
    tensor = fs.frame_tensor(SERVICE, DESIGN, front, s, z, [r])[0]
    assert np.max(np.abs(tensor)) > 1e-4
    assert abs(tensor[0, 0]) < 1e-10 and np.max(np.abs(tensor[0, 1:])) < 1e-10
    assert ax.classify(tensor[None], floor=1e-12)["type"][0] == ax.TYPE_I


def test_shelf_holds_the_lapse_above_the_carry_speed_ahead_of_the_pattern():
    s = 3.
    c = SERVICE.packet_position(s)
    edge = SHELF.edge_position(SERVICE, s)
    for z in np.linspace(c+SERVICE.extent, edge, 25):
        f = fs.fields(SERVICE, DESIGN, SHELF, s, z, [0., 6., 12.])
        assert np.all(f["alpha"] > SERVICE.carry_speed(s))
    assert SHELF.lead_speed > math.exp(SHELF.log_lapse)
    arrive = SERVICE.path[7]+SERVICE.path[8]
    assert SHELF.edge_position(SERVICE, arrive+1.) == pytest.approx(SHELF.terminal(SERVICE), abs=1e-9)
    assert STATIC_SHELF.edge_position(SERVICE, -2.) == STATIC_SHELF.terminal(SERVICE)


def test_cone_extends_with_the_carry_speed_and_peaks_on_the_axis():
    c = SERVICE.packet_position(3.)
    tip = CONE.tip(SERVICE)
    axis = CONE.log_lapse_at(SERVICE, 3., c+tip-3., np.array([0., .5, 1.]))
    assert axis[0] > axis[1] > axis[2]
    assert CONE.log_lapse_at(SERVICE, 3., c+tip+.5, np.array([0.]))[0] == 0.
    rest = SERVICE.packet_position(-2.)
    assert np.all(CONE.log_lapse_at(SERVICE, -2., rest+10., np.linspace(0., 20., 9)) == 0.)
    base = CONE.log_lapse_at(SERVICE, 3., c+SERVICE.fall_start+1., np.linspace(0., 13., 14))
    assert np.all(np.exp(base) > 2.1+.5)


def test_point_evaluator_matches_fields():
    for front in (None, SHELF, CONE):
        for s, offset, r in ((3., 1.2, .4), (3., 6., 10.), (.8, 30., 2.), (7.1, -5., 12.)):
            z = SERVICE.packet_position(s)+offset
            log_alpha, shift = fs.point_log_lapse_and_shift(SERVICE, DESIGN, front, s, z, r)
            f = fs.fields(SERVICE, DESIGN, front, s, z, [r])
            assert math.exp(log_alpha) == pytest.approx(f["alpha"][0], rel=1e-12)
            assert shift == pytest.approx(f["beta"][0], abs=1e-13)


def test_trace_keeps_light_null_in_flat_space():
    sol = fs.trace(SERVICE, DESIGN, None, (-4., -3.), -40., 5., (.6, .8), mass=0.)
    z, r, kz, kr = sol.y[:, -1]
    assert z == pytest.approx(-40.+.6, abs=1e-9) and r == pytest.approx(5.+.8, abs=1e-9)
    assert (kz, kr) == pytest.approx((.6, .8), abs=1e-12)


def test_front_validation():
    with pytest.raises(ValueError):
        fs.ForwardShelf(lead_speed=2.5)
    with pytest.raises(ValueError):
        fs.ForwardShelf(log_lapse=0.)
    with pytest.raises(ValueError):
        fs.ConeFront(half_angle=95.)
    with pytest.raises(ValueError):
        fs.ConeFront(extend=(1., .6))


def test_array_helpers_match_their_scalar_forms():
    from adm_harness.constant_radius_track import transition_integral
    t = np.array([-.3, 0., .1, .37, .5, .63, .99, 1., 1.7])
    assert np.allclose(fs.transition_integral_array(t), [transition_integral(x) for x in t], rtol=0, atol=1e-15)
    radius = np.array([0., 4., 6.5, 9., 11.5, 14.])
    for s, offset in ((-2., 1.), (3., 5.9), (8.5, -6.)):
        z = SERVICE.packet_position(s)+offset
        (e, _, _), h = ax.sheath_jets(radius, s, z, DESIGN)
        assert np.allclose(fs.sheath_value(DESIGN, s, z, radius), h["v"]*e, rtol=0, atol=1e-15)


@pytest.mark.parametrize("front,decel,mass,z0,r0", [(None, 6., 1., 7.75, .5), (SHELF, 6., 1., 10.75, 2.),
                                                    (CONE, 6., 0., 40.75, 3.), (CONE, 6., 1., 70.75, .5)])
def test_batch_tracer_matches_the_adaptive_tracer(front, decel, mass, z0, r0):
    service = cs.CompartmentService(path=(-1., 0., 0., 2.1, 0., 0., 1.5, decel, 1.5), schedule=(-2.5, decel+3., 1.))
    design = cs.axial_design(service)
    k0 = (0., 0.) if mass else (1., 0.)
    span = (-3., decel+6.)
    sol = fs.trace(service, design, front, span, z0, r0, k0, mass=mass, max_step=.02, rtol=1e-10, atol=1e-12)
    y, peak, _ = fs.trace_many(service, design, front, span, [z0], [r0], [k0[0]], [k0[1]], mass=mass, ds=.005)
    energy = math.sqrt(mass+sol.y[2, -1]**2+sol.y[3, -1]**2)
    assert math.sqrt(mass+y[2, 0]**2+y[3, 0]**2) == pytest.approx(energy, rel=1e-4)
    assert y[0, 0] == pytest.approx(sol.y[0, -1], rel=1e-4)
    assert abs(y[1, 0]) == pytest.approx(abs(sol.y[1, -1]), rel=1e-4, abs=1e-4)
