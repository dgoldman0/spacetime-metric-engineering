from dataclasses import replace

import numpy as np
import pytest

from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.source_ledger import SourceParams, einstein_tensor_at, projections
from adm_harness.radial_stress import TYPE_I


@pytest.mark.parametrize("s,l", [(-1.2, -1.8), (.6, 1.8), (1.9, -1.8), (15., 6.)])
def test_cached_curvature_matches_established_kernel(s, l):
    params = SourceParams()
    source, _ = einstein_tensor_at(s, l, params, .0025, .0025)
    expected = projections(s, l, source, params)
    actual = evaluate_demand(s, l, params, .0025, .0025)
    for new, old in [("rho", "rho_euler"), ("p_l", "p_l_unit"), ("legacy_j_l", "j_l_unit"), ("p_omega", "p_omega_unit")]:
        assert actual[new] == pytest.approx(expected[old], rel=1e-9, abs=1e-11)
    assert actual["full_eigensystem_certified"]
    raw = actual["raw_tensor_orthonormal"]
    assert actual["j_l"] == -.5*(raw[0, 1]+raw[1, 0])
    assert np.max(np.abs(raw-actual["tensor_orthonormal"])) == actual["spherical_projection_absolute_error"]


def test_holding_control_preserves_spatial_profile_and_has_zero_current():
    params = SourceParams()
    active = evaluate_demand(.3, 1.7, params, .0025, .0025)
    holding = evaluate_demand(.3, 1.7, params, .0025, .0025, holding=True)
    for field in ["alpha", "gamma_ll", "gamma_omega"]:
        assert holding[field] == active[field]
    assert holding["beta"] == 0
    assert holding["j_l"] == pytest.approx(0, abs=1e-12)
    assert holding["stress_algebraic_type"] == TYPE_I
    assert holding["full_eigensystem_certified"]


def test_ultrastatic_throat_agrees_with_analytic_stress():
    params = replace(SourceParams(), C0=1., lam=1., B0=1., eta_N=0., aOmega=0., V=0., v_exit=0.)
    ell = 6.
    result = evaluate_demand(15., ell, params, .0025, .0025)
    magnitude = params.Rth**2/(8*np.pi*(ell**2+params.Rth**2)**2)
    assert np.allclose([result[k] for k in ["rho", "p_l", "j_l", "p_omega"]],
                       [-magnitude, -magnitude, 0., magnitude], rtol=2e-5, atol=1e-10)


def test_curvature_symmetry_residual_converges():
    coarse = evaluate_demand(.6, 1.8, SourceParams(), .0025, .0025)
    fine = evaluate_demand(.6, 1.8, SourceParams(), .00125, .00125)
    assert fine["spherical_projection_absolute_error"] < .3*coarse["spherical_projection_absolute_error"]
