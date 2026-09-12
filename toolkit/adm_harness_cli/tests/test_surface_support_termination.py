import numpy as np
from numpy.testing import assert_allclose

from adm_harness.surface_support_termination import minimum_surface_inventory


def test_static_termination_recovers_laplace_pressure_and_counts_skin_energy():
    t=np.linspace(0,1,9);r=2*np.ones_like(t);zero=0*t
    out=minimum_surface_inventory(t,r,zero,1/r,.3*np.ones_like(t),stress_fraction=.8)
    assert out['success']
    assert_allclose(out['surface_angular_stress']/r**2,-.3)
    assert_allclose(out['surface_energy']/r**2,.3/.8)
    assert out['max_work_residual'] < 1e-12


def test_accelerated_jacket_cannot_supply_opposite_force_with_positive_energy():
    t=np.linspace(0,1,9);one=np.ones_like(t)
    out=minimum_surface_inventory(t,2*one,2*one,.1*one,-.3*one)
    assert not out['success']
    assert out['pointwise_force_cone_incompatible']
    assert_allclose(out['witness_force_interval_per_unit_energy'],[1.8,2.2])


def test_expanding_tension_skin_has_consistent_strain_work_under_refinement():
    errors=[]
    for n in (17,65):
        t=np.linspace(0,1,n);r=2*np.exp(.05*t)
        # Pure constant surface tension provides an exact admissible solution.
        out=minimum_surface_inventory(t,r,0*t,1/r,.6/r)
        assert out['success']
        assert out['max_stress_cone_violation'] < 1e-9
        exact=.3*r*r
        errors.append(float(abs(out['surface_energy']-exact).max()))
    assert errors[1] < errors[0]/10
