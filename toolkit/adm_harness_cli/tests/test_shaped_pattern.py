import math

import numpy as np
import pytest

from adm_harness import axial_track as ax
from adm_harness import compartment_service as cs
from adm_harness import front_surface as fs
from adm_harness import source_scaling as ss
from adm_harness.numerical_einstein import einstein_fd

TRIM_AXIAL = dict(sheath_fall=(8.75, 2.), lapse_layer=(8.75, 2.))
SHAPES = [dict(pattern_space="alpha"), dict(pattern_space="alpha", pattern_warp=.5),
          dict(pattern_space="alpha", pattern_warp=.5, pattern_corner="round"), dict(pattern_corner="round"),
          dict(pattern_space="alpha", pattern_warp=.35, pattern_radial_warp=.5),
          dict(pattern_space="mixed", pattern_warp=.35, pattern_radial_warp=1.)]


def build(shape):
    service = cs.CompartmentService(plateau_log=3., shift_width=1., **shape)
    return service, cs.axial_design(service, **TRIM_AXIAL)


def brute_force(service, design, front, s, z, r):
    """Frame tensor from finite differences of the metric that log_lapse_and_shift builds, and the jet tensor."""
    def metric(x):
        time, along, radius, _ = x
        log_alpha, shift = fs.point_log_lapse_and_shift(service, design, front, time, along, radius)
        alpha = math.exp(log_alpha)
        g = np.zeros((4, 4))
        g[0, 0] = -alpha*alpha+shift*shift
        g[0, 1] = g[1, 0] = shift
        g[1, 1] = g[2, 2] = 1.
        g[3, 3] = radius*radius
        return g
    generated = fs.frame_tensor(service, design, front, s, z, [r])[0]
    einstein = einstein_fd(metric, [s, z, r, 0.], 5e-4, varying=3)
    frame = ss.normal_tetrad(fs.fields(service, design, front, s, z, [r]))[0]
    return generated, frame@einstein@frame.T/ax.EIGHT_PI


def test_default_pattern_and_cone_are_unshaped():
    assert not cs.CompartmentService().shaped
    cone, same = fs.ConeFront(), fs.ConeFront(space="log", warp=1.)
    service = cs.CompartmentService()
    z = service.packet_position(3.)+np.array([10., 30., 50.])
    r = np.array([.5, 3., 6.])
    assert np.array_equal(cone.log_lapse_at(service, 3., z, r), same.log_lapse_at(service, 3., z, r))


@pytest.mark.parametrize("shape", SHAPES)
def test_shaped_pattern_equals_the_product_inside_the_core(shape):
    service, design = build(shape)
    s = 3.75
    z, r = np.meshgrid(service.packet_position(s)+np.array([-3.2, -1., 0., 2., 3.2]), [0., 2., 5., 7.5, 8.2])
    tolerance = 1e-6 if shape.get("pattern_corner") == "round" else 1e-12
    assert np.max(np.abs(fs.pattern_correction(service, design, s, z, r))) < tolerance


@pytest.mark.parametrize("shape", SHAPES)
def test_shaped_pattern_reaches_flat_space_beyond_its_falls(shape):
    service, design = build(shape)
    s = 3.75
    centre = service.packet_position(s)
    for z, r in ((centre+service.extent+.01, 3.), (centre, 10.76), (centre-service.extent-.5, 11.)):
        assert fs.pattern_log_lapse(service, design, s, np.array([z]), np.array([r]))[0] == 0.
        log_alpha, shift = fs.log_lapse_and_shift(service, design, None, s, np.array([z]), np.array([r]))
        assert abs(log_alpha[0]) < 1e-14 and shift[0] == 0.


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("offset,r", [(4.6, 3.), (0., 9.6), (4.6, 9.6), (5.2, 10.2), (4.1, 8.9), (-4.4, 9.3)])
def test_shaped_pattern_tensor_matches_brute_force(shape, offset, r):
    service, design = build(shape)
    s = 3.
    generated, reference = brute_force(service, design, None, s, service.packet_position(s)+offset, r)
    assert np.max(np.abs(generated-reference)) < 5e-5*max(np.max(np.abs(reference)), 1.)


@pytest.mark.parametrize("cone", [fs.ConeFront(space="alpha"), fs.ConeFront(space="alpha", warp=.5),
                                  fs.ConeFront(warp=.5)])
@pytest.mark.parametrize("offset,r", [(30., 8.4), (58., 1.1), (5.4, 14.6), (45., 3.)])
def test_shaped_cone_tensor_matches_brute_force(cone, offset, r):
    service = cs.CompartmentService()
    design = cs.axial_design(service)
    generated, reference = brute_force(service, design, cone, 3., service.packet_position(3.)+offset, r)
    assert np.max(np.abs(generated-reference)) < 5e-5*max(np.max(np.abs(reference)), 1.)


def test_lapse_space_cone_keeps_its_interior_and_exterior_values():
    service = cs.CompartmentService()
    cone = fs.ConeFront(space="alpha", warp=.5)
    z = service.packet_position(3.)+np.array([30., 30.])
    values = cone.log_lapse_at(service, 3., z, np.array([0., 12.]))
    assert values[0] == pytest.approx(cone.log_lapse, abs=1e-12)
    assert values[1] == 0.


def test_shape_validation():
    with pytest.raises(ValueError):
        cs.CompartmentService(pattern_space="cubic")
    with pytest.raises(ValueError):
        cs.CompartmentService(pattern_warp=1.5)
    with pytest.raises(ValueError):
        fs.ConeFront(warp=0.)
    with pytest.raises(ValueError):
        cs.CompartmentService(pattern_space="mixed", pattern_corner="round")
