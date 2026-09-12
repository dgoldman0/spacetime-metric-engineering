from types import SimpleNamespace

import numpy as np
from numpy.testing import assert_allclose

from adm_harness.active_transfer_reservoir import MetricJets,divergence_projections
from adm_harness.composite_capacitor import anisotropic_moments
from audit_joint_support import bilinear,continuum_check


def test_bilinear_values_and_derivatives_reproduce_mixed_polynomial():
    t=np.array([0.,.4,1.]);x=np.array([-1.,0.,2.])
    z=2+t[:,None]+3*x[None,:]+.7*t[:,None]*x[None,:]
    at=np.array([.2,.8]);ax=np.array([-.4,1.3])
    value,dt,dx=bilinear(t,x,z,at,ax)
    assert_allclose(value,2+at[:,None]+3*ax[None,:]+.7*at[:,None]*ax[None,:])
    assert_allclose(dt,np.broadcast_to(1+.7*ax[None,:],value.shape))
    assert_allclose(dx,np.broadcast_to(3+.7*at[:,None],value.shape))


class SmoothMetric:
    def metric(self,t,x):
        x=np.asarray(x);alpha=np.exp(.07*t+.11*x);b=np.exp(.09*t+.04*x)
        r=2*np.exp(.03*t+.06*x);beta=.08*np.exp(.02*t-.03*x)
        full=lambda a:np.full_like(x,a)
        return MetricJets(alpha,beta,b,r,.11*alpha,-.03*beta,full(.09),full(.04),full(.03),full(.06))

    def medium(self,t,x):
        z=np.zeros((4,len(x)));return z,z,z


def scalar_fields(t,x):
    return .3+.04*t+.02*x,.5+.03*t-.01*x,.07+.01*t+.02*x,-.02+.005*t-.001*x


def normal_tensor(model,t,x):
    g=model.metric(t,x);v=g.b*g.beta/g.alpha;d=g.b*g.radius**2/np.sqrt(1-v*v)
    u,m,pr,pt=scalar_fields(t,x)
    return anisotropic_moments((u+m)/d,(u/3+pr)/d,(u/3+pt)/d,v)


def test_complete_continuum_audit_matches_independent_covariant_power_and_force():
    model=SmoothMetric();t=np.array([.5,.55,.6]);x=np.array([-.3,0.,.3])
    zero=np.zeros((3,3));fields=scalar_fields(t[:,None],x[None,:])
    old=dict(t=t,x=x,flux_energy=zero,number=np.zeros(3),thermal=fields[0])
    h=SimpleNamespace(knots=x,reference=SimpleNamespace(h=SimpleNamespace(model=model,state=old),t=t,x=x),
        allocation=lambda positions:(np.zeros_like(positions),np.zeros_like(positions)),
        state=dict(heat=zero,heat_cap=np.zeros(3)))
    state=dict(t=t,x=x,thermal=zero,support_energy=fields[1],radial_volume=fields[2],angular_volume=fields[3])
    # The declared fixed-fluid control uses the full reference even when its
    # smaller-grid diagnostic array differs.
    actual=continuum_check(h,state,preserve_reference_fluid=True);eps=1e-5
    for i,time in enumerate(actual['t']):
        xx=actual['x'];g=model.metric(time,xx);v=g.b*g.beta/g.alpha
        tensor=normal_tensor(model,time,xx)
        dt=(normal_tensor(model,time+eps,xx)-normal_tensor(model,time-eps,xx))/(2*eps)
        dx=(normal_tensor(model,time,xx+eps)-normal_tensor(model,time,xx-eps))/(2*eps)
        power,force=divergence_projections(g,tensor,dt,dx)
        assert_allclose(actual['power'][i],(power-v*force)/np.sqrt(1-v*v),atol=3e-11,rtol=2e-8)
        assert_allclose(actual['force'][i],(force-v*power)/np.sqrt(1-v*v),atol=3e-11,rtol=2e-8)
