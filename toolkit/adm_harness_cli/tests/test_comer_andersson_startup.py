import numpy as np
import pytest

from adm_harness.comer_andersson_startup import (
    areal_rates, cattaneo_required_drive, entropy_embedding, fit_constant_rate_response,
    heat_from_energy_current, kinetic_conditions, minimum_heat_energy,
    quadratic_rate_action, quadratic_rate_channels,
)
from adm_harness.geometry_boundary import evaluate_demand
from adm_harness.source_ledger import SourceParams


def test_rate_stresses_equal_independent_weak_variation_of_the_action():
    t, weights = np.polynomial.legendre.leggauss(128)
    lapse = np.exp(.1*np.cos(.8*t))
    nu_t = -.08*np.sin(.8*t)
    qr, qt = .05*np.sin(1.7*t), .07*np.cos(1.2*t)
    vr, vt = .085*np.cos(1.7*t), -.084*np.sin(1.2*t)
    ar, at = -.1445*np.sin(1.7*t), -.1008*np.cos(1.2*t)
    hr, ht = vr/lapse, vt/lapse
    dhr, dht = (ar-vr*nu_t)/lapse**2, (at-vt*nu_t)/lapse**2
    a, b = .017, .023
    stress = quadratic_rate_channels(hr,ht,dhr,dht,a,b)
    bump, bump_t = (1-t*t)**3, -6*t*(1-t*t)**2
    eps = 1e-5
    for direction in ['lapse','radial','angular']:
        actions = []
        for sign in [-1,1]:
            n = lapse*np.exp(sign*eps*bump) if direction=='lapse' else lapse
            qrr = qr+sign*eps*bump if direction=='radial' else qr
            qtt = qt+sign*eps*bump if direction=='angular' else qt
            rr = vr+sign*eps*bump_t if direction=='radial' else vr
            tt = vt+sign*eps*bump_t if direction=='angular' else vt
            actions.append(weights@(n*np.exp(qrr+2*qtt)*quadratic_rate_action(rr/n,tt/n,a,b)))
        variation = (actions[1]-actions[0])/(2*eps)
        component = {'lapse':-stress[:,0], 'radial':stress[:,1], 'angular':2*stress[:,3]}[direction]
        expected = weights@(lapse*np.exp(qr+2*qt)*component*bump)
        assert variation == pytest.approx(expected,rel=2e-8,abs=1e-11)


def test_angular_variation_survives_an_action_that_vanishes_on_the_areal_path():
    t, weights = np.polynomial.legendre.leggauss(128)
    qr = .04*np.sin(1.3*t)
    hr, dhr = .052*np.cos(1.3*t), -.0676*np.sin(1.3*t)
    a, b = 1/(8*np.pi), -1/(8*np.pi)
    assert np.array_equal(quadratic_rate_action(hr,0.,a,b),np.zeros_like(hr))
    stress = quadratic_rate_channels(hr,0.,dhr,0.,a,b)
    bump, bump_t = (1-t*t)**3, -6*t*(1-t*t)**2
    eps = 2e-6
    action = []
    for sign in [-1,1]:
        qt, ht = sign*eps*bump, sign*eps*bump_t
        action.append(weights@(np.exp(qr+2*qt)*quadratic_rate_action(hr,ht,a,b)))
    measured = (action[1]-action[0])/(2*eps)
    expected = weights@(np.exp(qr)*2*stress[:,3]*bump)
    assert abs(expected)>1e-5
    assert measured == pytest.approx(expected,rel=1e-8,abs=1e-11)


def test_quadratic_sector_matches_dynamic_curvature_with_independent_four_dimensional_check():
    def fields(t,r,params):
        f = .7+.02*np.sin(t)/r
        return {'alpha':np.exp(.1*np.cos(t)/(r+1)), 'beta':0., 'gamma_ll':1/f, 'gamma_omega':r*r}
    t, r = .73, 3.2
    f, ft, ftt = .7+.02*np.sin(t)/r, .02*np.cos(t)/r, -.02*np.sin(t)/r
    alpha = fields(t,r,None)['alpha']
    h, dh = areal_rates(f,ft,ftt,alpha,-.1*np.sin(t)/(r+1))
    target = quadratic_rate_channels(h,0.,dh,0.,1/(8*np.pi),-1/(8*np.pi))
    target[2] = ft/(8*np.pi*r*alpha*np.sqrt(f))
    errors = []
    for step in [.003,.0015,.00075]:
        dynamic = evaluate_demand(t,r,SourceParams(),step,step,scalar_evaluator=fields)
        static = evaluate_demand(t,r,SourceParams(),step,step,holding=True,scalar_evaluator=fields)
        measured = np.array([dynamic[k]-static[k] for k in ['rho','p_l','j_l','p_omega']])
        errors.append(max(abs(measured-target)))
    assert errors[-1]<2e-8
    assert errors[1]<.5*errors[0]


def test_fitted_tensor_match_is_a_degenerate_gravitational_kinetic_point():
    t = np.linspace(.01,.99,101)
    h, dh = -.2*np.sin(np.pi*t)**2, -.4*np.pi*np.sin(np.pi*t)*np.cos(np.pi*t)
    fit = fit_constant_rate_response(h,dh)
    assert fit['a_times_8pi'] == pytest.approx(1.)
    assert fit['b_times_8pi'] == pytest.approx(-1.)
    assert fit['max_stress_residual']<1e-15
    assert abs(fit['tensor_kinetic_ratio'])<1e-14
    assert not fit['tensor_kinetic_strictly_positive']
    # Independent trace-free velocity perturbation of the total kinetic action.
    velocities = np.array([.003,-.003,0.])
    for a,b in [(.01,.02),(1/(8*np.pi),-1/(8*np.pi)),(.03,-.05)]:
        einstein = (velocities@velocities-velocities.sum()**2)/(16*np.pi)
        material = .5*(a*velocities.sum()**2+b*(velocities@velocities))
        assert (einstein+material)/einstein == pytest.approx(kinetic_conditions(a,b)['tensor_kinetic_ratio'],abs=1e-14)


def test_entropy_function_has_the_derived_action_and_changes_sign_during_a_cycle():
    t = np.linspace(0.,1.,2001)
    h = -.01*np.sin(np.pi*t)**2
    dh = -.02*np.pi*np.sin(np.pi*t)*np.cos(np.pi*t)
    volume_log = -.005*t+.005*np.sin(2*np.pi*t)/(2*np.pi)
    base = .1*np.exp(-4*volume_log/3)
    a, b = .02, .03
    q, dq = .5*(a+b)*h*h, (a+b)*h*dh
    result = entropy_embedding(base,q,dq,h)
    assert result['valid'].all()
    assert np.max(abs(base*result['entropy_factor']**(4/3)-(base-q)))<5e-17
    rate = result['entropy_rate_per_entropy']
    assert rate[200]<0 and rate[1800]>0
    # Independent numerical derivative along the specified material trajectory.
    numerical = np.gradient(np.log(result['entropy_factor']),t,edge_order=2)
    fine_error = np.max(abs(numerical[20:-20]-rate[20:-20]))
    coarse = np.gradient(np.log(result['entropy_factor'][::2]),t[::2],edge_order=2)
    coarse_error = np.max(abs(coarse[10:-10]-rate[20:-20:2]))
    assert fine_error<3e-10 and fine_error<.3*coarse_error
    assert result['entropy_factor'][0] == result['entropy_factor'][-1] == 1.


def test_preloaded_heat_carrier_has_positive_rest_energy_and_prices_the_drift():
    current = np.linspace(-.01,.01,101)
    energy = np.maximum(minimum_heat_energy(current,maximum_drift=.1),1e-4)
    carrier = heat_from_energy_current(energy,current)
    v, rest = carrier['velocity'],carrier['rest_energy']
    assert max(abs(v))<=.1+1e-14
    assert min(rest)>0
    reconstructed = 4*rest*v/(3*(1-v*v))
    assert np.max(abs(reconstructed-current))<1e-16
    e,p,j,_ = np.moveaxis(carrier['channels'],-1,0)
    assert np.max(abs((e+p)**2-4*j*j-(4*rest/3)**2))<1e-16
    q = .01*np.sin(np.linspace(0.,1.,31))
    dq = .01*np.cos(np.linspace(0.,1.,31))
    drive = cattaneo_required_drive(q,dq,.3,.2)
    assert np.max(abs(.3*dq+q+.2*drive))<1e-16
