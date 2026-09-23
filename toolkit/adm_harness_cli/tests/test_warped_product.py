import json
import math
from pathlib import Path

import numpy as np
import pytest

from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.metric_regularity import regularized_scalars
from adm_harness.radial_stress import TYPE_I, TYPE_IV
from adm_harness.source_ledger import SourceParams
from adm_harness.warped_product import evaluate_spherical_demand


@pytest.fixture(scope="module")
def params():
    path = Path(__file__).resolve().parents[3] / "supporting_reports/data/le_geometry_boundary/manifest.json"
    return SourceParams(**json.loads(path.read_text())["params"])


def fields(alpha=1., beta=0., radial=1., angular=1.):
    return {"alpha": alpha, "beta": beta, "gamma_ll": radial, "gamma_omega": angular}


def test_ellis_throat_matches_the_analytic_tensor():
    a = 1.75
    evaluator = lambda s, l, p: fields(angular=l*l+a*a)
    for ell in (0., .7, -2.3, 6.):
        result = evaluate_spherical_demand(3., ell, None, 1e-3, 1e-3, scalar_evaluator=evaluator)
        amplitude = a*a/(8*math.pi*(ell*ell+a*a)**2)
        assert result["rho"] == pytest.approx(-amplitude, rel=1e-6)
        assert result["p_l"] == pytest.approx(-amplitude, rel=1e-6)
        assert result["p_omega"] == pytest.approx(amplitude, rel=1e-6)
        assert result["j_l"] == 0 and result["stress_algebraic_type"] == TYPE_I


def test_dust_cosmology_checks_time_dependent_radius_terms():
    evaluator = lambda s, l, p: fields(radial=s**(4/3), angular=(s**(2/3)*l)**2)
    for sigma, ell in ((2., .5), (3.5, 1.2)):
        result = evaluate_spherical_demand(sigma, ell, None, 1e-3, 1e-3, scalar_evaluator=evaluator)
        assert result["rho"] == pytest.approx(1/(6*math.pi*sigma*sigma), rel=1e-6)
        for key in ("p_l", "p_omega", "j_l"):
            assert abs(result[key]) < 1e-8
        assert result["null_energy_outgoing"] == pytest.approx(result["null_energy_ingoing"], rel=1e-6)


def test_painleve_gullstrand_schwarzschild_is_vacuum_with_shift():
    mass = .4
    evaluator = lambda s, l, p: fields(beta=math.sqrt(2*mass/l), angular=l*l)
    for radius in (1.5, 3., 7.):
        result = evaluate_spherical_demand(.2, radius, None, 1e-3, 1e-3, scalar_evaluator=evaluator)
        tensor = np.array([result[k] for k in ("rho", "p_l", "j_l", "p_omega")])
        assert np.max(np.abs(tensor)) < 1e-6*mass/radius**3


def test_constant_radius_gives_an_exact_string_cloud_under_any_two_metric(params):
    radius = 1.9
    evaluator = lambda s, l, p: regularized_scalars(s, l, p) | {"gamma_omega": radius*radius}
    for sigma, ell in ((1.878989361702128, -1.8), (.3, .35), (-.6, -.7), (1., -2.2)):
        result = evaluate_spherical_demand(sigma, ell, params, .0025, .0025, scalar_evaluator=evaluator)
        assert result["radius_constant_on_stencil"]
        assert result["rho"]+result["p_l"] == 0 and result["j_l"] == 0
        assert result["rho"] == pytest.approx(1/(8*math.pi*radius*radius), rel=1e-15)
        assert result["null_energy_outgoing"] == 0 == result["null_energy_ingoing"]
        assert result["stress_algebraic_type"] == TYPE_I and result["full_eigensystem_certified"]
        legacy = evaluate_demand(sigma, ell, params, .0025, .0025, scalar_evaluator=evaluator)
        assert result["p_omega"] == pytest.approx(legacy["p_omega"], rel=1e-6)


@pytest.mark.parametrize("sigma,ell", [(1.878989361702128, -1.8), (.3, .35), (1., -2.2)])
def test_agrees_with_the_frozen_kernel_at_second_order(params, sigma, ell):
    errors = []
    for step in (.0025, .00125):
        new = evaluate_spherical_demand(sigma, ell, params, step, step, scalar_evaluator=regularized_scalars)
        old = evaluate_demand(sigma, ell, params, step, step, scalar_evaluator=regularized_scalars)
        assert new["stress_algebraic_type"] == old["stress_algebraic_type"]
        errors.append(max(abs(new[k]-old[k]) for k in ("rho", "p_l", "j_l", "p_omega")))
    assert errors[1] < errors[0]/3.5
    assert errors[1] < 5e-5*np.max(np.abs(old["tensor_orthonormal"]))


def test_type_iv_is_opposite_signed_radial_null_energy(params):
    result = evaluate_spherical_demand(1.878989361702128, -1.8, params, .0025, .0025,
                                       scalar_evaluator=regularized_scalars)
    assert result["stress_algebraic_type"] == TYPE_IV
    assert result["null_energy_outgoing"]*result["null_energy_ingoing"] < 0
    h, j = result["rho"]+result["p_l"], result["j_l"]
    product = result["null_energy_outgoing"]*result["null_energy_ingoing"]
    assert product == pytest.approx(h*h-4*j*j, rel=1e-9)


def test_holding_control_has_exactly_zero_current(params):
    result = evaluate_spherical_demand(1.878989361702128, -1.8, params, .0025, .0025,
                                       scalar_evaluator=regularized_scalars, holding=True)
    assert result["j_l"] == 0 and result["beta"] == 0
    assert result["stress_algebraic_type"] == TYPE_I


@pytest.mark.parametrize("args", [(0., 0., 0., 1e-3), (0., float("nan"), 1e-3, 1e-3), (0., 0., 1e-3, -1.)])
def test_invalid_inputs_are_explicit(args):
    with pytest.raises(ValueError):
        evaluate_spherical_demand(args[0], args[1], None, args[2], args[3], scalar_evaluator=lambda *x: fields())
