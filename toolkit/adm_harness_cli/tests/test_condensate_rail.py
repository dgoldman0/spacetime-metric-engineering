from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import simpson

from adm_harness.condensate_rail import (ExteriorBoundary, load_retained_geometry,
    continue_gravity, refine_exterior, continue_inward, interior_rhs, validate_exterior)
from adm_harness.screened_condensate import CondensateParameters, field_stress, gravitating_rhs

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope='module')
def loaded_exterior():
    geometry = load_retained_geometry(ROOT)
    boundary, parameters = ExteriorBoundary.from_geometry(geometry), CondensateParameters()
    seed, trace = continue_gravity(boundary, parameters)
    assert trace[-1]['gravity_fraction'] == 1. and trace[-1]['accepted']
    solution = refine_exterior(seed, boundary, parameters, tolerance=1e-8)
    return solution, boundary, parameters, geometry


def test_interior_coordinate_equations_agree_with_schwarzschild_areal_equations():
    # A nontrivial radial metric tests both log-lapse and log-radial-scale signs,
    # the v factors, and the opposite gauge/scalar lapse friction terms.
    p, v, mass, sigma, x, omega = CondensateParameters(), 2.7, .4, .8, 5., .9

    class Metric:
        def values(self, r):
            f, fp = 1-2*mass/r, 2*mass/r**2
            return r, sigma*np.sqrt(f), 1/np.sqrt(f), 1/r, fp/(2*f), -fp/(2*f)

    fields = np.array([.2, .03, .8, -.04, .4, -.1])
    coordinate_fields = fields.copy()
    coordinate_fields[[1, 3, 5]] *= v
    actual = interior_rhs(x, coordinate_fields, omega, v, p, Metric())
    expected = gravitating_rhs(v*x, np.r_[fields, v*mass, np.log(sigma)], omega, 0., p)[:6]
    expected[[0, 2, 4]] *= v
    expected[[1, 3, 5]] *= v*v
    assert np.allclose(actual, expected, rtol=1e-13, atol=1e-13)


def test_loaded_exterior_matches_rail_geometry_and_integrated_sources(loaded_exterior):
    solution, boundary, p, geometry = loaded_exterior
    r = np.linspace(boundary.inner_radius, solution.x[-1], 18001)
    y = solution.sol(r)
    f, sigma = 1-2*y[6]/r, np.exp(y[7])
    t = field_stress(y[:6], solution.p[0], p, f, sigma)
    x = geometry.negative_branch_coordinate(boundary.physical_radius)
    radius, _, scale = geometry.values(x)
    rlog, alog, _ = geometry.values(x, 1)
    assert np.isclose(f[0], (radius*rlog/scale)**2, rtol=1e-13)
    exterior_k = (y[6, 0]+4*np.pi*boundary.gravity*r[0]**3*t['radial_pressure'][0])/(r[0]**2*f[0])
    assert abs(exterior_k*boundary.vacuum_scale-alog/(radius*rlog)) < 1e-12
    assert abs(t['radial_pressure'][0]-boundary.radial_pressure) < 1e-10
    mass_increment = 4*np.pi*boundary.gravity*simpson(r*r*t['energy'], x=r)
    assert np.isclose(y[6, -1]-y[6, 0], mass_increment, rtol=1e-8)
    charge = 4*np.pi*simpson(r*r*(t['matter_charge']+t['higgs_charge'])/np.sqrt(f), x=r)
    matter_charge = 4*np.pi*simpson(r*r*t['matter_charge']/np.sqrt(f), x=r)
    outer_flux = 4*np.pi*r[-1]**2*y[5, -1]/sigma[-1]
    assert abs(charge+outer_flux)/matter_charge < 1e-8
    assert abs(charge)/matter_charge < 1e-7
    check = validate_exterior(solution, boundary, p, boundary.gravity)
    assert check['maximum_original_equation_error'] < 2e-7
    assert check['minimum_f'] > .6


@pytest.mark.parametrize('kind', ['analytic', 'retained'])
def test_selected_cauchy_data_reach_large_field_growth_before_the_core(loaded_exterior, kind):
    exterior, boundary, p, geometry = loaded_exterior
    solution, metric = continue_inward(exterior, boundary, p, geometry, kind=kind, threshold=100.)
    assert solution.success and len(solution.t_events[0]) == 1
    assert solution.t[-1] < -3.
    assert 4. < metric.values(solution.t[-1])[0] < 5.
    u, _, h, hp, _, _ = solution.y[:, -1]
    assert np.isclose(abs(u/h), np.sqrt(1-p.higgs_coupling/(2*p.matter_coupling)), rtol=2e-4)
    scale = metric.values(solution.t[-1])[2]*boundary.vacuum_scale
    assert np.isclose(hp/h**2, scale*np.sqrt(p.matter_coupling/2), rtol=.002)


def test_inward_field_derivatives_match_the_normal_derivative(loaded_exterior):
    exterior, boundary, p, geometry = loaded_exterior
    solution, metric = continue_inward(exterior, boundary, p, geometry, threshold=10.)
    initial = exterior.sol(boundary.inner_radius)
    radial_scale = metric.values(metric.start)[2]
    normal_inside = -solution.y[[1, 3, 5], 0]/radial_scale
    normal_outside = boundary.vacuum_scale*np.sqrt(boundary.inner_f)*initial[[1, 3, 5]]
    assert np.allclose(normal_inside, normal_outside, rtol=1e-14, atol=1e-14)
