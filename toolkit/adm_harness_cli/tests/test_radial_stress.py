from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from adm_harness.endpoint_j_source_class_screen import classify_endpoint_source_frame
from adm_harness.radial_stress import (
    ETA, TYPE_I, TYPE_II, TYPE_IV, UNRESOLVED,
    certify_radial_eigensystem, classify_radial_stress, radial_tensor,
)


@pytest.mark.parametrize("scale", [1e-100, 1e-8, 1., 1e8, 1e100])
@pytest.mark.parametrize("channels,kind,rest_energy,rest_pressure", [
    ([0, 0, 0, 0], TYPE_I, 0, 0),
    ([2, 1, 0, .3], TYPE_I, 2, 1),
    ([1, -1, 0, 0], TYPE_I, 1, -1),
    ([1, -1, 0, -1], TYPE_I, 1, -1),
    ([1, -2, 0, 0], TYPE_I, 1, -2),
    ([1, 1, 1, 0], TYPE_II, None, None),
    ([1, -1, .2, 0], TYPE_IV, None, None),
])
def test_canonical_tensors_at_multiple_amplitudes(scale, channels, kind, rest_energy, rest_pressure):
    values = np.asarray(channels)*scale
    result = certify_radial_eigensystem(radial_tensor(*values))
    assert result["stress_algebraic_type"] == kind
    assert result["full_eigensystem_certified"]
    frame = pd.DataFrame([dict(zip(["sector_rho", "sector_p_l", "sector_j_l", "sector_p_omega"], values)) | {"volume_weight": 1}])
    classified = classify_endpoint_source_frame(frame).iloc[0]
    assert classified.stress_algebraic_type == kind
    if rest_energy is None:
        assert np.isnan(classified.rest_frame_energy_density)
        assert np.isnan(classified.boost_velocity_to_flux_frame)
        assert not classified.type_i_heat_flux_compatible
    else:
        assert classified.rest_frame_energy_density/scale == pytest.approx(rest_energy, abs=1e-12)
        assert classified.rest_frame_radial_pressure/scale == pytest.approx(rest_pressure, abs=1e-12)
        assert classified.type_i_heat_flux_compatible


@pytest.mark.parametrize("velocity", [-.99, -.7, .2, .9])
@pytest.mark.parametrize("energy,pressure,angular", [(2., 1., .3), (1., -2., .3), (1., -1., -1.)])
def test_rest_energy_and_margins_are_radial_boost_invariant(velocity, energy, pressure, angular):
    gamma = 1/np.sqrt(1-velocity**2)
    lorentz = np.eye(4)
    lorentz[:2, :2] = gamma*np.array([[1, -velocity], [-velocity, 1]])
    assert np.allclose(lorentz.T @ ETA @ lorentz, ETA)
    tensor = lorentz.T @ radial_tensor(energy, pressure, 0, angular) @ lorentz
    # A boost of an exactly degenerate block can introduce floating-point
    # cancellation; restore its known exact off-diagonal zero in this fixture.
    if energy + pressure == 0:
        tensor[0, 1] = tensor[1, 0] = 0.
    result = certify_radial_eigensystem(tensor)
    assert result["stress_algebraic_type"] == TYPE_I
    assert result["full_eigensystem_certified"]
    assert result["rest_frame_energy_density"] == pytest.approx(energy, rel=1e-10)
    assert result["rest_frame_radial_pressure"] == pytest.approx(pressure, rel=1e-10)
    assert result["nec_margin"] == pytest.approx(min(energy+pressure, energy+angular), abs=1e-10)
    assert result["dec_margin"] == pytest.approx(min(energy-abs(pressure), energy-abs(angular)), abs=1e-10)


def test_near_null_boundary_is_unresolved_with_no_material_rest_frame():
    result = classify_radial_stress([1, 1], [1, 1], [1-1e-14, 1+1e-14], [0, 0])
    assert np.all(result["stress_algebraic_type"] == UNRESOLVED)
    assert np.isnan(result["rest_frame_energy_density"]).all()
    assert not result["type_i_heat_flux_compatible"].any()


def test_exact_null_dust_has_a_defective_null_eigenspace():
    result = certify_radial_eigensystem(radial_tensor(1, 1, -1, 0))
    assert result["eigenbasis_rank"] == 3
    assert result["jordan_chain_error"] < 1e-12
    assert abs(result["eigenvector_metric_norms"][0]) < 1e-12


def test_full_tensor_with_transverse_current_requires_another_classifier():
    tensor = radial_tensor(1, .5, .1, .2)
    tensor[0, 2] = tensor[2, 0] = .05
    with pytest.raises(ValueError, match="angular flux"):
        certify_radial_eigensystem(tensor)


@pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf])
def test_invalid_source_is_rejected(value):
    with pytest.raises(ValueError, match="finite"):
        classify_radial_stress(value, 0, 0, 0)


def test_small_current_boost_avoids_subtractive_cancellation():
    result = classify_radial_stress(2., 1., 1e-20, 0.)
    assert result["boost_velocity_to_flux_frame"][0] == pytest.approx(1e-20/3, rel=1e-12, abs=0)
