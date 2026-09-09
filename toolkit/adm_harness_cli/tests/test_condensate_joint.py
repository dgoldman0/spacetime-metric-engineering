from pathlib import Path

import numpy as np
import pytest

from adm_harness.condensate_joint import (JointParameters, JointGeometry,
    proper_matter_rhs, initial_guess, joint_rhs, joint_boundary, physical_parameters)
from adm_harness.condensate_rail import load_retained_geometry
from adm_harness.screened_condensate import CondensateParameters, field_stress

ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize('lapse,rlog,alog', [(1., .2, 0.), (50., -.03, .01), (.7, .1, -.2)])
def test_vacuum_and_potential_plateau_solve_matter_equations(lapse, rlog, alog):
    p, omega = CondensateParameters(), .8
    for fields in [np.array([0., 0., 1., 0., 0., 0.]),
                   np.array([1.6, 0., 0., 0., omega/p.charge, 0.])]:
        assert np.allclose(proper_matter_rhs(5., lapse, rlog, alog, fields, omega, p), 0., atol=1e-14)
    t = field_stress(fields, omega, p, metric_f=1., sigma=lapse)
    assert t['energy'] == .25 and t['radial_pressure'] == -.25


def test_proper_tensor_conservation_uses_scalar_and_gauge_gradients():
    p, omega, lapse, rlog, alog = CondensateParameters(), .8, .7, -.2, .3
    fields = np.array([.2, .03, .8, -.02, .6, -.04])
    derivative = proper_matter_rhs(5., lapse, rlog, alog, fields, omega, p)
    step = 1e-6
    plus = field_stress(fields+step*derivative, omega, p, 1., lapse*np.exp(step*alog))
    minus = field_stress(fields-step*derivative, omega, p, 1., lapse*np.exp(-step*alog))
    t = field_stress(fields, omega, p, 1., lapse)
    dp = (plus['radial_pressure']-minus['radial_pressure'])/(2*step)
    expected = -alog*(t['energy']+t['radial_pressure'])+2*rlog*(t['tangential_pressure']-t['radial_pressure'])
    assert np.isclose(dp, expected, rtol=1e-8, atol=1e-10)


def test_proper_geometry_retains_asymmetric_throat_and_boundary_data():
    q = load_retained_geometry(ROOT)
    setup = JointParameters()
    g = JointGeometry(q, setup)
    for x in [-6., -1., 0., 1., 6., 30.]:
        t = g.fraction_at_coordinate(x)
        r, a, dr, da = g.values(t)
        rr, aa, b = q.values(x)
        rrlog, aal, _ = q.values(x, 1)
        assert np.isclose(r, rr, rtol=2e-6)
        assert np.isclose(a, aa, rtol=2e-6)
        assert np.isclose(dr, rrlog/b, rtol=3e-5, atol=1e-10)
        assert np.isclose(da, aal/b, rtol=3e-5, atol=1e-10)
    assert g.values(g.fraction_at_coordinate(-1.))[1] > 4*g.values(g.fraction_at_coordinate(1.))[1]
    fields, pars = initial_guess(np.linspace(0, 1, 1001), g, CondensateParameters())
    assert joint_rhs(np.linspace(0, 1, 1001), fields, pars, g, CondensateParameters()).shape == fields.shape
    assert joint_boundary(fields[:, 0], fields[:, -1], pars, g, CondensateParameters()).shape == (16,)


def test_frequency_parameter_keeps_positive_end_bound_and_rejects_threshold():
    p = CondensateParameters()
    setup = JointParameters(local_frequency_fraction=.97)
    gravity, clock, omega = physical_parameters(np.log([3e-5, .7]), setup, p)
    assert omega/clock < np.sqrt(p.matter_coupling)
    with pytest.raises(ValueError):
        JointParameters(local_frequency_fraction=1.)
