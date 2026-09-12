import numpy as np

from adm_harness.active_transfer_reservoir import divergence_projections
from adm_harness.composite_capacitor import anisotropic_moments
from adm_harness.joint_support_gauss import build_spacetime, solve_spacetime
from adm_harness.pressure_linked_storage import fluid_coefficients, retained_coefficient_program
from test_joint_support_audit import SmoothMetric
from test_joint_support_projection import manufactured_fields


def test_spacetime_rows_match_covariant_manufactured_tensor():
    model = SmoothMetric()

    def tensor(t,x):
        g = model.metric(t,x); v = g.b*g.beta/g.alpha
        d = g.b*g.radius**2/np.sqrt(1-v*v)
        m,p,q = manufactured_fields(t,x)
        return anisotropic_moments(m/d,p/d,q/d,v)

    def coefficients(t,x):
        c = fluid_coefficients(model,t,x)
        powers,forces,rates = [],[],[]; eps = 1e-5
        for i,time in enumerate(t):
            g = model.metric(time,x)
            dt = (tensor(time+eps,x)-tensor(time-eps,x))/(2*eps)
            dx = (tensor(time,x+eps)-tensor(time,x-eps))/(2*eps)
            power,force = divergence_projections(g,tensor(time,x),dt,dx)
            powers.append(-c['gamma'][i]*(power-c['v'][i]*force))
            forces.append(-c['gamma'][i]*(force-c['v'][i]*power)); rates.append(g.logr_t)
        lr = np.array(rates)
        c.update(ell=c['gamma']*c['b'],D=c['rest_volume'],log_radius_t=lr,
                 log_ell_t=c['volume_rate']-2*lr,fixed_power=np.array(powers),fixed_force=np.array(forces))
        return c

    t = np.linspace(.5,.8,9); x = np.linspace(-.3,.3,17)
    problem = build_spacetime(t,x,coefficients,np.zeros(len(x)),np.zeros((len(t),len(x))))
    m,p,q = manufactured_fields(t[:,None],x[None,:])
    vector = np.r_[m.ravel(),p.ravel(),q.ravel(),100.]
    er = problem['eq'].matrix()@vector-problem['eq'].rhs
    assert abs(er).max() < 2e-9
    assert np.max(problem['ub'].matrix()@vector-problem['ub'].rhs) < 0


def test_joint_spacetime_static_force_exposes_unpaid_anchor():
    def c(t,x):
        one = np.ones((len(t),len(x))); zero = one*0
        return dict(ell=one,D=one,lapse=one,v=zero,gamma=one,acceleration=zero,
                    angular_gradient=zero,log_ell_t=zero,log_radius_t=zero,volume_rate=zero,
                    fixed_power=zero,fixed_force=.2*one)
    t = np.linspace(0,1,5); x = np.linspace(0,2,9)
    number = np.ones(len(x)); thermal = np.zeros((len(t),len(x)))
    r = solve_spacetime(t,x,c,number,thermal,deadline=5.)
    assert r['success']
    np.testing.assert_allclose(r['radial_volume'][:,-1]-r['radial_volume'][:,0],-.4,atol=1e-9)
    p = build_spacetime(t,x,c,number,thermal)
    for i in range(len(t)):
        for j in (0,len(x)-1):
            p['eq'].add([(p['size']+i*len(x)+j,1.)])
    r = retained_coefficient_program(p['cost'],method='highs-ipm',deadline=5.,
        A_eq=p['eq'].matrix(),b_eq=p['eq'].rhs,A_ub=p['ub'].matrix(),b_ub=p['ub'].rhs,bounds=p['bounds'])
    assert r.status == 2
