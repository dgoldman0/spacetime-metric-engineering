import numpy as np
from numpy.testing import assert_allclose

from adm_harness.joint_backing_link import build_problem


def test_prepared_frame_matches_accelerated_expanding_metric_force():
    # ds^2=-exp(2*a0*x)dt^2+exp(2*k*t)dx^2+4dOmega^2.
    # A=A0+A1*x, B=constant gives ell*F=-A1/4+2*a0*B/(4*ell^2).
    # This independent analytic result includes both the prestress gradient
    # and the inertial load of the compressed rod; all cold energy is adiabatic.
    t=np.linspace(0,1,7);x=np.linspace(0,1,9)
    one=np.ones((len(t),len(x)));zero=np.zeros_like(one)
    ell=np.exp(.2*t[:,None])*one;a0=.17
    c=dict(gamma=one,b=ell,radius=2*one,rest_volume=4*ell,v=zero,
           lapse=np.exp(a0*x[None,:])*one,acceleration=a0/ell,
           angular_gradient=zero,volume_rate=.2*one)
    reference=.3*one;number=np.full(len(x),.1)
    tension=.5+.13*x;compression=np.full(len(x),.4)
    rhs=(-.13/4+2*a0*.4/(4*ell**2))[:,:-1]
    p=build_problem(t,x,c,zero,reference,number,rhs,zero,prestrain_floor=.1)
    candidate=np.zeros(p['peak']+1);size=p['size']
    candidate[:size]=reference.ravel()
    candidate[2*size:2*size+len(x)]=tension
    candidate[2*size+len(x):2*size+2*len(x)]=compression
    candidate[-1]=10.
    assert_allclose(p['eq'].matrix()@candidate,p['eq'].rhs,atol=2e-15)
    assert np.max(p['ub'].matrix()@candidate-p['ub'].rhs)<1e-14
