import math

import numpy as np
import pytest

import run_geometry_closure_pass as closure
from adm_harness import front_surface as fs


@pytest.mark.parametrize("speed", [1.5, 10.])
def test_raising_the_plateau_with_the_speed_leaves_the_shift_region_unchanged(speed):
    """Scaling lapse and shift together rescales time: the demanded tensor around the shift keeps its values."""
    s = 3.75
    radius = np.array([.5, 2., 4.5, 5.3, 6., 7.5])
    base = closure.build_spec(closure.TRIM, 2.1)
    fast = closure.build_spec(closure.TRIM, speed)
    for offset in (-3., -2.8, 2.6, 3.):
        t0 = fs.frame_tensor(*base[:2], None, s, base[0].packet_position(s)+offset, radius)
        t1 = fs.frame_tensor(*fast[:2], None, s, fast[0].packet_position(s)+offset, radius)
        assert np.max(np.abs(t0-t1)) < 1e-3*max(np.max(np.abs(t0)), 1e-3)


def test_scaled_cone_keeps_its_flank_below_the_light_speed_along_its_normal():
    for speed in closure.SPEEDS:
        service, _, cone = closure.build_spec(closure.TRIM_SCALED, speed)
        assert speed*math.sin(math.radians(cone.half_angle)) == pytest.approx(closure.FLANK_SPEED, rel=1e-12)
        assert closure.FLANK_SPEED < 1.
