from dataclasses import replace
import json
from pathlib import Path

import numpy as np
import pytest

from adm_harness.geometry_boundary import evaluate_demand, metric_scalars
from adm_harness.receiver_regularity import c2_clipped_power, repaired_receiver_scalars
from adm_harness.source_ledger import SourceParams


@pytest.fixture(scope="module")
def params():
    path = Path(__file__).resolve().parents[3] / "supporting_reports/data/le_geometry_boundary/manifest.json"
    return SourceParams(**json.loads(path.read_text())["params"])


@pytest.mark.parametrize("power", [.1, .25, .5, 1., 2.])
def test_weight_is_bounded_monotone_and_preserves_bulk(power):
    positions = np.linspace(-.1, 1.1, 2401)
    weights = np.array([c2_clipped_power(z, power) for z in positions])
    assert weights.min() == 0
    assert weights.max() == 1
    assert np.all(np.diff(weights) >= -1e-14)
    for z in [.125, .25, .5, .75, .875]:
        assert c2_clipped_power(z, power) == z**power


@pytest.mark.parametrize("power", [.25, .5, 1., 2.])
@pytest.mark.parametrize("join", [0., .125, .875, 1.])
def test_value_and_two_derivatives_match_at_joins(power, join):
    step = 1e-4
    derivatives = []
    for direction in [-1, 1]:
        offsets = direction*np.arange(5.)
        samples = [c2_clipped_power(join+step*offset, power) for offset in offsets]
        polynomial = np.polynomial.Polynomial.fit(offsets, samples, 4).convert()
        derivatives.append([polynomial(0), polynomial.deriv(1)(0)/step, polynomial.deriv(2)(0)/step**2])
    if join == 0:
        expected = [0., 0., 0.]
    elif join == 1:
        expected = [1., 0., 0.]
    else:
        expected = [join**power, power*join**(power-1), power*(power-1)*join**(power-2)]
    assert np.allclose(derivatives, expected, rtol=2e-5, atol=5e-5)


@pytest.mark.parametrize("z,p,b", [(float("nan"), .5, .125), (.5, 0., .125), (.5, 3., .125), (.5, .5, 0.), (.5, .5, .5)])
def test_invalid_weight_parameters_are_explicit(z, p, b):
    with pytest.raises(ValueError):
        c2_clipped_power(z, p, b)


def test_candidate_changes_only_angular_metric_inside_repair_bands(params):
    for ell in [-.9, -.93, -1.71, -1.75]:
        before = metric_scalars(1.878989361702128, ell, params)
        after = repaired_receiver_scalars(1.878989361702128, ell, params)
        for key in ["alpha", "beta", "gamma_ll"]:
            assert after[key] == before[key]
        assert after["gamma_omega"] != before["gamma_omega"]
        assert after["gamma_omega"] > 0
    for ell in [-6., -1.8, -1.4, -.8, 0., .9, 1.8, 6.]:
        before = metric_scalars(1.878989361702128, ell, params)
        after = repaired_receiver_scalars(1.878989361702128, ell, params)
        for key in ["alpha", "beta", "gamma_ll", "gamma_omega"]:
            assert after[key] == before[key]


def test_existing_smooth_type_iv_witness_is_preserved(params):
    before = evaluate_demand(1.878989361702128, -1.8, params, .0025, .0025)
    after = evaluate_demand(1.878989361702128, -1.8, params, .0025, .0025, scalar_evaluator=repaired_receiver_scalars)
    assert np.array_equal(before["raw_tensor_orthonormal"], after["raw_tensor_orthonormal"])


@pytest.mark.parametrize("holding", [False, True])
def test_inner_edge_curvature_converges_to_receiver_free_value(params, holding):
    sigma, ell = 1.878989361702128, -.875
    angular_off = replace(params, support_edge_receiver_angular_log_gain=0.)
    reference = evaluate_demand(sigma, ell, angular_off, .00015625, .00015625, holding=holding)
    errors = []
    for h in [.00125, .000625, .0003125]:
        candidate = evaluate_demand(sigma, ell, params, h, h, holding=holding, scalar_evaluator=repaired_receiver_scalars)
        errors.append(np.max(np.abs(candidate["tensor_orthonormal"]-reference["tensor_orthonormal"])))
        assert candidate["full_eigensystem_certified"]
    assert errors[2] < .3*errors[0]


@pytest.mark.parametrize("field", ["support_edge_receiver_lapse_log_gain", "support_edge_receiver_radial_log_gain", "support_edge_receiver_beta_relaxation_gain"])
def test_unsupported_receiver_channels_require_explicit_reconstruction(params, field):
    with pytest.raises(ValueError, match="angular-only"):
        repaired_receiver_scalars(1.8, -1.8, replace(params, **{field: .1}))
