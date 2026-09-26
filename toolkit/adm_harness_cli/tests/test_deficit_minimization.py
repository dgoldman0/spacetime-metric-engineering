import copy
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))
import run_deficit_minimization_pass as dm

LOWERED = {"service": dict(dm.WARPS, shift_width=.75), "axial": dm.FALL_8P25}


def lowered(rise_width):
    changes = copy.deepcopy(LOWERED)
    changes["cone"] = {"log_lapse": 1., "rise_width": rise_width}
    return dm.variant_spec(changes)[0]


RECOMMENDED = "mixed_fall_8p25_shift_0p75_cone_1_rise_2"


def finalist():
    return dm.variant_spec(dm.all_variants()[RECOMMENDED])[0]


def test_reference_spec_reproduces_the_closure_cone_base():
    spec, radius = dm.variant_spec({})
    assert spec["cone"]["base_radius"] == 14.
    assert radius == pytest.approx(10.15, abs=.05)


@pytest.mark.parametrize("speed", [2.1, 10.])
def test_reference_carries_a_single_front(speed):
    spec, _ = dm.variant_spec({})
    assert dm.light_surfaces(spec, speed)["front_surfaces_max"] == 1


@pytest.mark.parametrize("speed", [2.1, 20.])
def test_reference_front_advances_slower_than_light(speed):
    assert dm.front_speed(dm.variant_spec({})[0], speed) < .8


@pytest.mark.parametrize("speed", [1.5, 2.1, 10., 20.])
def test_finalist_front_advances_slower_than_light_at_every_speed(speed):
    spec = finalist()
    assert dm.light_surfaces(spec, speed)["front_surfaces_max"] == 1
    assert dm.front_speed(spec, speed) < .8


def test_lapse_space_radial_fall_lets_a_front_piece_outrun_light_at_high_speed():
    spec = lowered(2.)
    assert dm.front_speed(spec, 10.) < .8
    assert dm.front_speed(spec, 20.) > 1.


def test_slow_cone_rise_opens_a_flat_front_at_speed():
    spec = lowered(3.)
    assert dm.light_surfaces(spec, 2.1)["front_surfaces_max"] == 1
    assert dm.light_surfaces(spec, 10.)["front_surfaces_max"] == 2
    assert dm.front_speed(spec, 10.) == pytest.approx(10., rel=1e-6)
