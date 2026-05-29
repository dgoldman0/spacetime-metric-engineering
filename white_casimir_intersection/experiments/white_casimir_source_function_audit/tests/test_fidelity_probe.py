import numpy as np

from white_casimir_audit.fidelity_probe import loop_hits_cylinder_surface, loop_hits_sphere_surface


def test_loop_hits_sphere_surface_detects_segment_crossing():
    crossing = np.array([[[-2.0, 0.0, 0.0], [2.0, 0.0, 0.0], [-2.0, 0.0, 0.0]]])
    missing = np.array([[[2.0, 2.0, 0.0], [3.0, 2.0, 0.0], [2.0, 2.0, 0.0]]])
    loops = np.concatenate([crossing, missing], axis=0)
    assert loop_hits_sphere_surface(loops, radius_um=1.0).tolist() == [True, False]


def test_loop_hits_cylinder_surface_detects_finite_axis_crossing():
    crossing = np.array([[[0.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 0.0]]])
    outside_axis_range = np.array([[[2.0, 0.0, 0.0], [2.0, 2.0, 0.0], [2.0, 0.0, 0.0]]])
    loops = np.concatenate([crossing, outside_axis_range], axis=0)
    assert loop_hits_cylinder_surface(loops, radius_um=1.0, half_length_um=1.0).tolist() == [True, False]
