import numpy as np
from numpy.testing import assert_allclose
from adm_harness.time_support_projection import evolve_support


def test_implicit_pressure_evolution_converges_through_negative_shift():
    def true_p(t,x):return .2+.01*np.sin(3*t)*(1+x)
    def coefficients(t,x):
        one=np.ones((len(t),len(x)));zero=one*0;v=-.2*one
        force=-(-.2*.03*np.cos(3*t[:,None])*(1+x[None,:])+.01*np.sin(3*t[:,None]))
        return dict(ell=one,D=one,lapse=one,v=v,acceleration=zero,angular_gradient=zero,
                    log_ell_t=zero,log_radius_t=zero,Q=zero,fixed_power=zero,fixed_force=force)
    errors=[]
    for n in (17,65):
        t=np.linspace(0,1,n);x=np.linspace(0,1,n)
        r=evolve_support(t,x,coefficients,np.ones(n),true_p(t,1.),.03*(1+x),
                         initial_pressure=true_p(0.,x))
        errors.append(np.max(abs(r['radial_pressure']-true_p(t[:,None],x[None,:]))))
        assert_allclose(r['support_energy'],1.)
        assert r['maximum_step_force_residual']<1e-12
    assert errors[1]<errors[0]/3


def test_zero_shift_uses_spatial_equilibrium_without_a_singular_time_update():
    def c(t,x):
        one=np.ones((len(t),len(x)));zero=one*0
        return dict(ell=one,D=one,lapse=one,v=zero,acceleration=zero,angular_gradient=zero,
                    log_ell_t=zero,log_radius_t=zero,Q=zero,fixed_power=zero,fixed_force=.2*one)
    t=np.linspace(0,1,7);x=np.linspace(0,2,9)
    r=evolve_support(t,x,c,np.ones(len(x)),np.zeros(len(t)),np.zeros(len(x)))
    assert_allclose(r['radial_pressure'],np.broadcast_to(.2*(2-x),(len(t),len(x))),atol=1e-13)
    assert_allclose(r['support_energy'],1.)
