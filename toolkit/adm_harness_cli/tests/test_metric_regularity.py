from dataclasses import replace
from functools import partial
import json
from pathlib import Path

import numpy as np
import pytest

from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.metric_regularity import c2_radius, c2_upper_cap, regularized_scalars, rate_scaled_scalars
from adm_harness.receiver_regularity import repaired_receiver_scalars
from adm_harness.source_ledger import SourceParams


@pytest.fixture(scope="module")
def params():
    path = Path(__file__).resolve().parents[3] / "supporting_reports/data/le_geometry_boundary/manifest.json"
    return SourceParams(**json.loads(path.read_text())["params"])


def one_sided_jets(function, join, step=1e-4):
    result = []
    for direction in [-1, 1]:
        offsets = direction*np.arange(5.)
        values = [function(join+step*x) for x in offsets]
        polynomial = np.polynomial.Polynomial.fit(offsets, values, 4).convert()
        result.append([polynomial.deriv(n)(0)/step**n for n in range(3)])
    return np.array(result)


@pytest.mark.parametrize("join,expected", [(-.1, [.1, -1., 0.]), (0., [0., 0., 37.5]), (.1, [.1, 1., 0.])])
def test_radius_has_even_origin_and_c2_patch_joins(join, expected):
    assert np.allclose(one_sided_jets(c2_radius, join), expected, rtol=1e-5, atol=1e-5)


def test_radius_preserves_exterior_and_is_monotone():
    radii = np.linspace(0, .2, 1001)
    values = np.array([c2_radius(r) for r in radii])
    assert np.all(np.diff(values) >= 0)
    assert np.all(values <= radii+1e-15)
    assert all(c2_radius(-r) == c2_radius(r) for r in radii)
    assert all(c2_radius(r) == r for r in [.1, .5, 4.])


@pytest.mark.parametrize("join,expected", [(.75, [.75, 1., 0.]), (1., [1., 0., 0.])])
def test_upper_cap_has_c2_joins_and_preserves_the_tail(join, expected):
    assert np.allclose(one_sided_jets(c2_upper_cap, join), expected, rtol=1e-5, atol=1e-5)
    values = np.array([c2_upper_cap(x) for x in np.linspace(0, 2, 2001)])
    assert values.min() == 0 and values.max() == 1
    assert np.all(np.diff(values) >= -1e-14)
    assert c2_upper_cap(1e-20) == 1e-20


@pytest.mark.parametrize("function,args", [(c2_radius, (0., 0.)), (c2_radius, (float("inf"),)),
    (c2_upper_cap, (-1.,)), (c2_upper_cap, (1., .5)), (c2_upper_cap, (float("nan"),))])
def test_invalid_primitive_parameters_are_explicit(function, args):
    with pytest.raises(ValueError):
        function(*args)


def test_existing_smooth_witness_is_preserved(params):
    args = (1.878989361702128, -1.8, params, .0025, .0025)
    original = evaluate_demand(*args, scalar_evaluator=repaired_receiver_scalars)
    candidate = evaluate_demand(*args, scalar_evaluator=regularized_scalars)
    assert np.array_equal(original["raw_tensor_orthonormal"], candidate["raw_tensor_orthonormal"])


def test_shell_repair_reconstructs_every_metric_channel_and_downstream_rematch(params):
    params = replace(params, support_shell_rail_stretch_log_gain=.1, support_shell_throat_capacity_log_gain=-.05)
    s, ell = -.63, 1.3
    zero = replace(params, support_shell_amplitude=0., support_shell_clock_lapse_log_gain=0.,
                   support_shell_rail_stretch_log_gain=0., support_shell_throat_capacity_log_gain=0.)
    base = repaired_receiver_scalars(s, ell, zero)
    candidate = regularized_scalars(s, ell, params)
    window = candidate["support_shell_window"]
    assert window != repaired_receiver_scalars(s, ell, params)["support_shell_window"]
    for key, gain in [("alpha", params.support_shell_clock_lapse_log_gain),
                      ("gamma_ll", params.support_shell_rail_stretch_log_gain),
                      ("gamma_omega", params.support_shell_throat_capacity_log_gain)]:
        assert candidate[key] == pytest.approx(base[key]*np.exp(gain*window), rel=1e-13)
    rematch = 1-params.standing_support_packet_beta_rematch_gain*base["standing_support_packet_beta_rematch_window"]
    assert candidate["beta"] == pytest.approx(base["beta"]+params.support_shell_amplitude*window*rematch, rel=1e-13)


@pytest.mark.parametrize("axis,join,other", [("l", 0., 1.878989361702128), ("l", -.1, 1.878989361702128),
    ("l", .1, 1.878989361702128), ("s", -.64, 1.3)])
def test_repaired_full_metric_has_matching_one_sided_jets(params, axis, join, other):
    for key in ["alpha", "beta", "gamma_ll", "gamma_omega"]:
        function = (lambda x: regularized_scalars(other, x, params)[key]) if axis == "l" else (
            lambda x: regularized_scalars(x, other, params)[key])
        scale = max(1., abs(function(join)))
        jets = one_sided_jets(lambda x: function(x)/scale, join, step=5e-5)
        assert np.allclose(jets[0], jets[1], rtol=2e-5, atol=2e-4)


@pytest.mark.parametrize("holding", [False, True])
def test_throat_curvature_converges_after_origin_repair(params, holding):
    rows = [evaluate_demand(1.878989361702128, 0., params, h, h, holding=holding,
                           scalar_evaluator=regularized_scalars) for h in [.00125, .000625, .0003125]]
    changes = [np.max(np.abs(b["tensor_orthonormal"]-a["tensor_orthonormal"])) for a, b in zip(rows, rows[1:])]
    assert changes[1] < .4*changes[0]
    assert abs(rows[-1]["p_omega"]) < .1


@pytest.mark.parametrize("phase,ell", [(1.878989361702128, -1.8), (-.63, 1.3)])
def test_uniform_rate_tensor_obeys_adm_scaling(params, phase, ell):
    step = .000625
    static = evaluate_demand(phase, ell, params, step, step, holding=True, scalar_evaluator=regularized_scalars)
    active = evaluate_demand(phase, ell, params, step, step, scalar_evaluator=regularized_scalars)
    for rate in [1., .5, .125]:
        provider = partial(rate_scaled_scalars, rate=rate)
        fields = provider(phase/rate, ell, params)
        reference = regularized_scalars(phase, ell, params)
        for key in ["alpha", "gamma_ll", "gamma_omega"]:
            assert fields[key] == reference[key]
        assert fields["beta"] == rate*reference["beta"]
        row = evaluate_demand(phase/rate, ell, params, step/rate, step, scalar_evaluator=provider)
        assert row["j_l"] == pytest.approx(rate*active["j_l"], abs=1e-10)
        for key in ["rho", "p_l", "p_omega"]:
            assert row[key] == pytest.approx(static[key]+rate**2*(active[key]-static[key]), abs=1e-10)
