import numpy as np
from numpy.testing import assert_allclose
from adm_harness.integrated_support_energy import IntegratedEnergy


def test_dense_work_primitive_and_its_derivative_are_consistent():
    edges=np.array([0.,.2,.7,1.]);x=np.array([-.4,.5])
    rhs=lambda t:1+2*t[:,None]+3*t[:,None]**2+x[None,:]*t[:,None]**3
    history=IntegratedEnergy(edges,2+x,rhs)
    t=np.linspace(0,1,37);energy,derivative=history.evaluate(t)
    expected=2+x[None,:]+t[:,None]+t[:,None]**2+t[:,None]**3+x[None,:]*t[:,None]**4/4
    assert_allclose(energy,expected,atol=2e-14)
    assert_allclose(derivative,rhs(t),atol=2e-14)


def test_nonpolynomial_power_error_converges_with_panel_refinement():
    errors=[]
    for n in (5,17):
        h=IntegratedEnergy(np.linspace(0,1,n),np.array([1.]),lambda t:np.exp(t)[:,None])
        t=np.linspace(.001,.999,131);energy,power=h.evaluate(t)
        assert_allclose(energy[:,0],np.exp(t),atol=1e-7)
        errors.append(np.max(abs(power[:,0]-np.exp(t))))
    assert errors[1]<errors[0]/100
