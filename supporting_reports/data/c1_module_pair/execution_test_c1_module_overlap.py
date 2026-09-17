import numpy as np
import pytest
from scipy.integrate import simpson

from adm_harness.c1_module_overlap import (
    StaticGeometry, angular_support_floor, electric_pair, smooth_step, static_support,
    support_tensor_at,
)


def flat_geometry(x):
    z = np.zeros_like(x)
    return z+2., z+3., z+1.5, z, z


def test_maxwell_cross_term_is_half_the_energy_at_equal_field_shares():
    d = electric_pair(np.array([0.]), 2., 1., amplitude=3., overlap=(-1., 1.))
    np.testing.assert_allclose(d["module_flux"].sum(axis=-1), d["flux"])
    np.testing.assert_allclose(d["self_energy"].sum(axis=-1)+d["cross_energy"], d["energy"])
    np.testing.assert_allclose(d["cross_energy"], d["energy"]/2.)
    assert d["lorentz_force"][0, 0] < 0 < d["lorentz_force"][0, 1]
    np.testing.assert_allclose(d["lorentz_force"].sum(axis=-1), 0., atol=1e-15)


def test_finite_sources_have_zero_net_charge_with_both_end_returns_counted():
    x = np.linspace(-3., 3., 12001)
    r, b = np.sqrt(4.+x*x), 1.+.2*x*x
    d = electric_pair(x, r, b, amplitude=.7, overlap=(.25, 1.25))
    charge = simpson(4.*np.pi*(b*r*r)[:, None]*d["charge_density"], x=x, axis=0)
    np.testing.assert_allclose(charge, 0., atol=5e-12)
    np.testing.assert_allclose(d["module_flux"][[0, -1]], 0., atol=1e-15)
    np.testing.assert_allclose(d["lorentz_force"].sum(axis=-1), d["total_lorentz_force"], atol=1e-15)
    assert np.all(d["energy"] >= 0)


def test_maxwell_divergence_independently_matches_charge_force():
    x = np.linspace(-3.2, 3.2, 32001)
    r, b = np.sqrt(4.+x*x), 1.+.2*x*x
    d = electric_pair(x, r, b, amplitude=.7, overlap=(-.5, .5))
    # rho=u, pr=-u, pt=u: the lapse term cancels identically.
    divergence = -np.gradient(d["energy"], x, edge_order=2)/b-4.*x/(b*r*r)*d["energy"]
    np.testing.assert_allclose(divergence, -d["total_lorentz_force"], atol=2e-9)


def test_static_flat_capacitor_support_matches_the_analytic_energy_and_pressure():
    geometry = StaticGeometry(flat_geometry)

    def load(x):
        r, _, b, _, _ = geometry(x)
        d = electric_pair(x, r, b, amplitude=.7, overlap=(-.5, .5))
        return d["total_lorentz_force"], d["total_charge_density"]

    residuals = []
    for n in (193, 385):
        x = np.linspace(-3., 3., n)
        summary, state = static_support(x, geometry, load, domain=(-3., 3.))
        assert summary["success"]
        r, _, b, _, _ = geometry(x)
        d = electric_pair(x, r, b, amplitude=.7, overlap=(-.5, .5))
        np.testing.assert_allclose(state["radial_pressure"], d["energy"], atol=3e-12)
        expected = simpson(4.*np.pi*b*r*r*d["energy"], x=x)
        np.testing.assert_allclose(summary["proper_energy"], expected, rtol=5e-4)
        assert summary["duality_gap_relative"] < 1e-10
        assert summary["minimum_dec_margin"] > -1e-11
        offgrid = (x[1:]+x[:-1])/2.
        stress = support_tensor_at(offgrid, state, geometry, load)
        analytic = electric_pair(offgrid, 2., 1.5, amplitude=.7, overlap=(-.5, .5))
        np.testing.assert_allclose(stress[:, 1], analytic["energy"], atol=3e-11)
        residuals.append(summary["linear_pressure_force_residual_l1_relative"])
    assert residuals[1] < .6*residuals[0]


def test_flat_closed_support_rejects_unbalanced_force():
    geometry = StaticGeometry(flat_geometry)

    def load(x):
        return (1.-x*x)**2, np.zeros_like(x)

    result, state = static_support(np.linspace(-1., 1., 65), geometry, load,
                                   domain=(-1., 1.))
    assert not result["success"]
    assert result["solver_status"] == 2
    assert not state


def test_local_angular_contact_cone_keeps_both_force_signs_and_zero_load():
    d = angular_support_floor(np.array([-1., 1., 0.]), 3., .2)
    assert d["feasible"].tolist() == [False, True, True]
    np.testing.assert_allclose(d["density"][1:], [1./3.4, 0.])
    both = angular_support_floor(np.array([-1., 1.]), 0., .2)
    np.testing.assert_allclose(both["density"], 2.5)
    assert not angular_support_floor(1., 0., 0.)["feasible"]


def test_overlap_width_controls_force_and_preserves_complete_charge_inventory():
    x = np.linspace(-1., 1., 8001)
    inventories, peaks = [], []
    for width in (.5, 1.):
        d = electric_pair(x, 2., 1., amplitude=.7, overlap=(-width/2., width/2.))
        inventories.append(simpson(abs(d["charge_density"][:, 0])*4., x=x))
        peaks.append(abs(d["lorentz_force"][:, 0]).max())
    np.testing.assert_allclose(inventories, .7, rtol=1e-12)
    np.testing.assert_allclose(peaks[0], 2.*peaks[1])


def test_invalid_boundaries_and_uncontained_load_are_rejected():
    geometry = StaticGeometry(flat_geometry)
    x = np.linspace(-1., 1., 33)
    with pytest.raises(ValueError):
        electric_pair(x, 2., 1., amplitude=1., overlap=(1., -1.))
    with pytest.raises(ValueError):
        static_support(x, geometry, lambda v: (v*0., v*0.), domain=(-.99, 1.))
    with pytest.raises(ValueError):
        static_support(x, geometry, lambda v: (v*0.+1., v*0.), domain=(-1., 1.))
    with pytest.raises(ValueError):
        smooth_step(np.nan)


def test_reconstructed_pressure_obeys_independently_differentiated_curved_force_law():
    def metric(x):
        r = 2.+.1*x
        return r, np.exp(.02*x), np.ones_like(x), np.zeros_like(x)+.1, np.zeros_like(x)+.02

    geometry = StaticGeometry(metric)

    def load(x):
        p = .01*(1.-x*x)**3
        force = -.06*x*(1.-x*x)**2+.08*p+.16/(2.+.1*x)*p
        return force, np.zeros_like(x)

    x = np.linspace(-1., 1., 129)
    summary, state = static_support(x, geometry, load, domain=(-1., 1.),
                                   density_ceiling=.2, proper_gradient_limit=1.)
    assert summary["success"]
    probes = x[:-1]+.37*np.diff(x)
    h = 1e-5
    plus = support_tensor_at(probes+h, state, geometry, load)
    minus = support_tensor_at(probes-h, state, geometry, load)
    mid = support_tensor_at(probes, state, geometry, load)
    derivative = (plus[:, 1]-minus[:, 1])/(2.*h)
    divergence = derivative+.02*(mid[:, 0]+mid[:, 1])+.2/(2.+.1*probes)*(mid[:, 1]-mid[:, 2])
    np.testing.assert_allclose(divergence, load(probes)[0], atol=1e-9)
    assert summary["max_density"] <= .2+1e-10
    assert summary["duality_gap_relative"] < 1e-8


def test_density_envelope_can_exclude_an_otherwise_feasible_closed_capacitor():
    geometry = StaticGeometry(flat_geometry)

    def load(x):
        d = electric_pair(x, 2., 1.5, amplitude=.7, overlap=(-.5, .5))
        return d["total_lorentz_force"], d["total_charge_density"]

    result, _ = static_support(np.linspace(-3., 3., 193), geometry, load,
                               domain=(-3., 3.), density_ceiling=.001)
    assert not result["success"]
    assert result["solver_status"] == 2
