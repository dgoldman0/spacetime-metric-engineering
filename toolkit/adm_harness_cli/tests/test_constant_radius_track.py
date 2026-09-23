from dataclasses import replace
import json
import math
from pathlib import Path

import numpy as np
import pytest

from adm_harness.constant_radius_track import (
    ConstantRadiusTrackDesign, areal_radius, transition_integral, track_scalars, flattened_step, service_cutoff,
    service_fields, smooth_abs, smooth_cap, smooth_step,
)
from adm_harness.radial_stress import TYPE_I
from adm_harness.source_ledger import SourceParams, scalars, smoothstep_minjerk
from adm_harness.warped_product import evaluate_spherical_demand


@pytest.fixture(scope="module")
def params():
    path = Path(__file__).resolve().parents[3] / "supporting_reports/data/le_geometry_boundary/manifest.json"
    return SourceParams(**json.loads(path.read_text())["params"])


def derivatives(function, x, step=2e-3, order=6):
    """Central finite differences of orders 0..3 on a nine-point stencil."""
    offsets = np.arange(-4, 5)
    values = np.array([function(x+step*k) for k in offsets])
    fit = np.polynomial.Polynomial.fit(offsets, values, order).convert()
    return np.array([fit.deriv(n)(0)/step**n for n in range(4)])


@pytest.mark.parametrize("function,step", [(smooth_step, 2e-3), (lambda t: flattened_step(t, smoothstep_minjerk, .1), 2e-4)])
def test_steps_are_flat_at_both_ends_and_monotone(function, step):
    for join, value in ((0., 0.), (1., 1.)):
        error = np.abs(derivatives(function, join, step=step)-[value, 0, 0, 0])
        assert np.all(error < [1e-12, 1e-8, 1e-5, 1e-2])
    grid = np.linspace(-.2, 1.2, 4001)
    values = np.array([function(t) for t in grid])
    assert np.all(np.diff(values) >= -1e-15) and values[0] == 0 and values[-1] == 1
    assert function(.5) == pytest.approx(.5)


def test_flattened_step_keeps_the_interior_polynomial():
    for t in np.linspace(.1, .9, 33):
        assert flattened_step(t, smoothstep_minjerk, .1) == pytest.approx(float(smoothstep_minjerk(t)), abs=1e-15)
    worst = max(abs(flattened_step(t, smoothstep_minjerk, .1)-float(smoothstep_minjerk(t)))
                for t in np.linspace(0, 1, 2001))
    assert worst <= float(smoothstep_minjerk(.1))


def test_smooth_abs_and_cap_are_even_monotone_and_exact_where_expected():
    assert smooth_abs(-.3, .02) == smooth_abs(.3, .02)
    assert abs(smooth_abs(1.05, .02)-1.05) < 1e-40
    assert np.allclose(derivatives(lambda x: smooth_abs(x, .02), 0., step=1e-3), [0, 0, 100., 0], rtol=1e-4, atol=1e-6)
    values = [smooth_cap(x, .25) for x in np.linspace(0, 3, 3001)]
    assert np.all(np.diff(values) >= -1e-15) and max(values) == 1
    assert smooth_cap(.7, .25) == .7 and smooth_cap(1.3, .25) == 1.


def test_transition_integral_is_exact_at_the_ends():
    assert transition_integral(1.) == .5 and transition_integral(2.5) == 2.
    fine = np.linspace(0, 1, 200001)
    reference = np.trapezoid([smooth_step(t) for t in fine], fine)
    assert transition_integral(1-1e-12) == pytest.approx(reference, abs=1e-9)
    partial = np.linspace(0, .3, 60001)
    assert transition_integral(.3) == pytest.approx(np.trapezoid([smooth_step(t) for t in partial], partial), abs=1e-9)


def test_radius_profile_has_a_constant_body_and_an_exactly_linear_exterior():
    design = ConstantRadiusTrackDesign()
    assert areal_radius(0., design) == areal_radius(-5., design) == 1.75
    start = design.track_half_length+design.transition_width
    for ell in (start, start+1.3, -start-7.):
        assert areal_radius(ell, design) == pytest.approx(1.75+.75+abs(ell)-start, rel=1e-15)
    jets = derivatives(lambda x: areal_radius(x, design), 5.75)
    assert jets[1] == pytest.approx(.5, abs=1e-6) and jets[2] > 0
    assert np.allclose(derivatives(lambda x: areal_radius(x, design), 5.), [1.75, 0, 0, 0], atol=1e-7)
    assert np.allclose(derivatives(lambda x: areal_radius(x, design), 6.5)[1:], [1, 0, 0], atol=1e-7)


def test_cutoff_confines_service_fields_inside_the_body():
    design = ConstantRadiusTrackDesign()
    assert service_cutoff(3.9, design) == 1 and service_cutoff(-5., design) == 0
    for ell in (5., -5.4, 7.):
        fields = track_scalars(.8, ell, None, design)
        assert (fields["alpha"], fields["beta"], fields["gamma_ll"]) == (1., 0., 1.)


def test_legacy_primitives_reproduce_the_frozen_kernel_exactly(params):
    rng = np.random.default_rng(3)
    for s, ell in np.column_stack([rng.uniform(-1.6, 3.5, 300), rng.uniform(-6, 6, 300)]):
        frozen = scalars(float(s), float(ell), params)
        rebuilt = service_fields(float(s), float(ell), params, smooth=False)
        assert all(frozen[k] == rebuilt[k] for k in ("alpha", "beta", "gamma_ll"))


def test_smooth_service_metric_stays_close_to_the_reference(params):
    rng = np.random.default_rng(5)
    for s, ell in np.column_stack([rng.uniform(-1.6, 3.5, 300), rng.uniform(-4, 4, 300)]):
        frozen = scalars(float(s), float(ell), params)
        smooth = service_fields(float(s), float(ell), params)
        assert smooth["alpha"] == pytest.approx(frozen["alpha"], rel=.01)
        assert smooth["gamma_ll"] == pytest.approx(frozen["gamma_ll"], rel=.02)
        assert abs(smooth["beta"]-frozen["beta"]) < .02


def test_unsupported_configurations_are_explicit(params):
    for change in ({"causal_margin_guard_enabled": True}, {"catch_profile": "tanh"},
                   {"support_edge_receiver_radial_log_gain": .1}):
        with pytest.raises(ValueError):
            service_fields(0., 0., replace(params, **change))
    for change in ({"transition_width": 0.}, {"service_inner": 6.}, {"join_fraction": .6}):
        with pytest.raises(ValueError):
            ConstantRadiusTrackDesign(**change)


@pytest.mark.parametrize("sigma,ell", [(1.878989361702128, -1.8), (-.6, -.7), (.3, .35), (2., 4.6), (1., 5.7)])
def test_candidate_is_certified_type_i_along_the_track_and_its_end_transitions(params, sigma, ell):
    design = ConstantRadiusTrackDesign()
    result = evaluate_spherical_demand(sigma, ell, params, .0025, .0025,
                                       scalar_evaluator=lambda s, l, p: track_scalars(s, l, p, design))
    assert result["stress_algebraic_type"] == TYPE_I and result["full_eigensystem_certified"]
    assert result["j_l"] == 0
    if abs(ell) < design.track_half_length:
        assert result["rho"]+result["p_l"] == 0
    else:
        assert result["null_energy_outgoing"] == result["null_energy_ingoing"] < 0


def test_exterior_is_flat_space(params):
    design = ConstantRadiusTrackDesign()
    for sigma, ell in ((-1.5, 6.6), (1., -8.), (15., 30.)):
        result = evaluate_spherical_demand(sigma, ell, params, .0025, .0025,
                                           scalar_evaluator=lambda s, l, p: track_scalars(s, l, p, design))
        assert np.max(np.abs(result["tensor_orthonormal"])) < 1e-9
