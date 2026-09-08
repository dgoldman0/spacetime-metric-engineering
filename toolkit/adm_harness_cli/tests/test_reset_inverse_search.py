import numpy as np
import pytest

from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.source_ledger import SourceParams
from adm_harness.reset_inverse_search import (
    ReferenceGrid, _history, construct, exchange_channels, infrastructure_boost,
    minimum_energy_lp, ordinary_energy_lower_bound, phase_blend, polar_areal_channels,
)


def schwarzschild_grid(nr=129, nt=17):
    r, u = np.linspace(2.15, 6.25, nr), np.linspace(0., 1., nt)
    shape = (nt, nr)
    mass = np.full(shape, .4)
    f = 1-2*mass/r
    fr = 2*mass/r**2
    nu = .5*np.log(f)
    nur = .4/(r*r*f)
    nurr = -.8/(r**3*f)-.32/(r**4*f*f)
    zero = np.zeros(shape)
    return ReferenceGrid(u, r, u, mass, zero, zero, zero, f, fr, nu, zero,
                         nur, nurr, zero, zero, zero, "analytic Schwarzschild")


def test_reduced_einstein_tensor_agrees_with_independent_four_dimensional_curvature():
    s, r = .73, 3.2
    def fields(t, x, params):
        f = .6+.03*np.sin(t)*np.exp(-(x-3)**2)
        nu = .08*np.cos(.7*t)/(x+1)+.03*x
        return {"alpha":np.exp(nu), "beta":0., "gamma_ll":1/f, "gamma_omega":x*x}
    v = .03*np.exp(-(r-3)**2)
    f = .6+v*np.sin(s)
    fr = -2*(r-3)*v*np.sin(s)
    ft, ftt = v*np.cos(s), -v*np.sin(s)
    nu = .08*np.cos(.7*s)/(r+1)+.03*r
    nur = -.08*np.cos(.7*s)/(r+1)**2+.03
    nurr = .16*np.cos(.7*s)/(r+1)**3
    nut = -.056*np.sin(.7*s)/(r+1)
    exact = polar_areal_channels(r, f, fr, ft, ftt, nu, nur, nurr, nut)
    errors = []
    for h in [.003, .0015, .00075]:
        row = evaluate_demand(s, r, SourceParams(), h, h, scalar_evaluator=fields)
        numeric = np.array([row[k] for k in ['rho','p_l','j_l','p_omega']])
        errors.append(np.max(abs(exact-numeric)))
    assert errors[-1] < 2e-8
    assert errors[1] < .4*errors[0]


def test_static_schwarzschild_and_de_sitter_sources():
    g = schwarzschild_grid()
    zero = np.zeros_like(g.f)
    source = polar_areal_channels(g.r, g.f, g.f_r, zero, zero, g.nu, g.nu_r, g.nu_rr, zero)
    assert np.max(abs(source)) < 1e-16
    r = np.linspace(1., 4., 101)
    hh = .01
    f = 1-hh*r*r
    nu = .5*np.log(f)
    nur = -hh*r/f
    nurr = -hh/f-2*hh*hh*r*r/f**2
    source = polar_areal_channels(r, f, -2*hh*r, 0., 0., nu, nur, nurr, 0.)
    density = 3*hh/(8*np.pi)
    assert np.allclose(source[:,0], density)
    assert np.allclose(source[:,[1,3]], -density)
    assert np.array_equal(source[:,2], np.zeros(len(r)))


def test_infrastructure_motion_preserves_radial_eigenvalue_discriminant_and_speed_bound():
    h = np.linspace(-.04, .04, 501)
    j = .007+0*h
    kinetic, jb, speed = infrastructure_boost(h, j, True)
    assert np.allclose((h+2*kinetic)**2-4*jb*jb, h*h, atol=1e-17)
    assert max(abs(speed)) <= .5+1e-14
    assert np.sign(kinetic[0]) == -1 and np.sign(kinetic[-1]) == 1
    assert kinetic[250] == jb[250] == speed[250] == 0


def test_analytic_energy_bounds_agree_with_independent_linear_program():
    rng = np.random.default_rng(441)
    h = rng.uniform(-.1,.1,31)
    j = rng.uniform(-.02,.02,31)
    weights = rng.uniform(.1,2.,31)
    carrier = .3*j
    result = minimum_energy_lp(h,j,weights,carrier_current=carrier)
    assert result.success
    bound = ordinary_energy_lower_bound(h,j,carrier_current=carrier)
    assert result.fun == pytest.approx(weights@bound,abs=1e-12)
    hn = -4*abs(j)-.01
    result = minimum_energy_lp(hn,j,weights,branch=-1,carrier_current=carrier)
    assert result.success
    assert result.fun == pytest.approx(weights@abs(carrier),abs=1e-12)
    bad = minimum_energy_lp(np.array([.01]),np.array([.02]),np.ones(1),branch=-1)
    assert bad.status == 2


def test_reservoir_mass_history_preserves_endpoints_and_has_conserved_net_transfer():
    g = schwarzschild_grid(513,257)
    controls = np.array([10., .2, .12, 2.65, .25, 4.8, .45, .5, 1., .25])
    h = _history(g,controls)
    assert np.max(abs(h['mass'][[0,-1]]-g.mass[[0,-1]])) < 1e-15
    assert np.max(abs(h['mass'][:,[0,-1]]-g.mass[:,[0,-1]])) < 1e-15
    assert np.max(abs(np.trapezoid(h['mass_t'],h['time'],axis=0))) < 1e-8
    receiver = np.trapezoid(h['reservoir_mass_density'],g.r,axis=1)
    donor = np.trapezoid(h['donor_mass_density'],g.r,axis=1)
    assert np.max(abs(receiver-h['storage_state'])) < 1e-8
    assert np.max(abs(receiver+donor)) < 1e-8


def test_lapse_source_solver_preserves_vacuum_control():
    g = schwarzschild_grid()
    controls = [10.,0.,0.,2.65,.25,4.8,.45,0.,.6,.25]
    result = construct(g,controls,retain=True)
    assert result['status'] == 'evaluated'
    assert result['max_momentum_residual'] < 1e-16
    assert result['max_angular_residual'] < 1e-7
    assert np.max(abs(result['fields']['alpha']-np.exp(g.nu))) < 1e-14


def test_radial_null_exchange_has_null_four_force():
    t,r = np.linspace(0,2,65),np.linspace(2.15,6.25,129)
    tt,rr = np.meshgrid(t,r,indexing='ij')
    f=.7+.02*np.sin(tt)/rr
    ft=.02*np.cos(tt)/rr
    nu=.05*tt/rr
    nur=-.05*tt/rr**2
    mu=.003*(1+.2*np.cos(tt-rr))/rr**2
    for direction in [-1,1]:
        null=np.stack([mu,mu,direction*mu,np.zeros_like(mu)],axis=-1)
        exchange=exchange_channels(t,r,f,ft,nur,np.exp(nu),null)
        assert np.max(abs(exchange[...,1]-direction*exchange[...,0])) < 1e-16


def test_settled_tail_interpolation_stays_inside_static_endpoint_values():
    phases=np.array([0.,1.,2.,5.,15.])
    values=np.array([0.,.5,.95,.99999,1.])
    value,first,second=phase_blend(phases,values,np.linspace(5.,15.,1001))
    assert value.min() >= .99999 and value.max() <= 1.
    assert np.all(np.diff(value)>=0)
    assert np.array_equal(first[[0,-1]],np.zeros(2))
    assert np.array_equal(second[[0,-1]],np.zeros(2))
