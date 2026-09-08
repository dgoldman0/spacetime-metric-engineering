import numpy as np
import pytest

from adm_harness.coupled_reset_constraints import prescribed_reset_source, solve_radial_constraints
from adm_harness.radial_stress import certify_radial_eigensystem, radial_tensor


def test_source_accounting_and_positive_carrier_energy():
    r = np.linspace(2., 6., 101)
    background = np.column_stack([.04/r**2, -.04/r**2, 0*r, 0*r])
    parts = prescribed_reset_source(r, background, .003*np.sin(r))
    summed = sum(parts[k] for k in ["infrastructure", "endpoint", "reservoir", "outgoing", "incoming"])
    assert np.array_equal(summed, parts["total"])
    assert np.all(parts["transfer_density"] >= abs(parts["commanded_current"]))
    assert np.all(parts["outgoing"][:, 0] >= 0) and np.all(parts["incoming"][:, 0] >= 0)
    assert np.allclose(parts["total"][:, 0]-background[:, 0],
                       2*parts["transfer_density"]-parts["released_string_density"])
    assert np.array_equal(parts["total"][[0, -1]], background[[0, -1]])
    for stream in ["outgoing", "incoming"]:
        source = parts[stream]
        assert np.allclose(source[:, 0]+source[:, 1], 2*abs(source[:, 2]))


def test_redistributing_radial_string_support_leaves_background_enthalpy_unchanged():
    r = np.linspace(2., 6., 51)
    bg = np.column_stack([.01+0*r, -.015+0*r, 0*r, .001+0*r])
    parts = prescribed_reset_source(r, bg, .002+0*r)
    h = parts["total"][:, 0]+parts["total"][:, 1]
    assert np.allclose(h, bg[:, 0]+bg[:, 1]+3*parts["transfer_density"])
    middle = len(r)//2
    result = certify_radial_eigensystem(radial_tensor(*parts["total"][middle]))
    assert result["stress_algebraic_type"] == "type_iv_flux_dominant"


def test_vacuum_constraints_reproduce_schwarzschild_lapse():
    errors = []
    for count in [501, 1001, 2001]:
        r = np.linspace(2., 10., count)
        mass = .4+0*r
        source = np.zeros((len(r), 4))
        solution = solve_radial_constraints(r, mass, 0*r, source, np.sqrt(1.-.8/r[-1]))
        assert solution["stationary_areal_domain"]
        assert np.array_equal(solution["mass"], mass)
        errors.append(np.max(abs(solution["lapse"]-np.sqrt(1.-.8/r))))
    assert errors[-1] < 3e-7
    assert errors[1] < .26*errors[0] and errors[2] < .26*errors[1]


def test_positive_added_energy_changes_the_metric_and_can_exhaust_mass_headroom():
    r = np.linspace(2., 4., 1001)
    mass0 = .99*r/2
    bg = np.zeros_like(r)
    target = np.column_stack([.01+0*r, 0*r, 0*r, 0*r])
    solution = solve_radial_constraints(r, mass0, bg, target, 1.)
    expected_increment = 4*np.pi*.01*(r**3-r[0]**3)/3
    assert np.allclose(solution["mass_increment"], expected_increment, atol=2e-7)
    assert not solution["stationary_areal_domain"]
    assert np.isnan(solution["lapse"]).all()
    assert solution["f"].min() < 0


def test_invalid_static_source_is_explicit():
    r = np.linspace(2., 4., 11)
    with pytest.raises(ValueError, match="static"):
        prescribed_reset_source(r, np.ones((len(r), 4)), 0*r)
