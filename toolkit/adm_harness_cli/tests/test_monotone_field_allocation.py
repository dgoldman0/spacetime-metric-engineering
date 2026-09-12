import numpy as np
from adm_harness.monotone_field_allocation import monotone_allocation


def test_smooth_allocation_preserves_each_interval_cap_and_continuous_gradient():
    x=np.array([0.,.2,.5,.9,1.4]);cap=np.array([.4,.8,.6,.3])
    values=.98*np.r_[cap[0],np.minimum(cap[:-1],cap[1:]),cap[-1]]
    allocation=monotone_allocation(x,values)
    for i in range(len(cap)):
        at=np.linspace(x[i],x[i+1],101)
        y,dy=allocation(at)
        assert y.min()>=-1e-14
        assert y.max()<=cap[i]+1e-14
    for knot in x[1:-1]:
        slopes=allocation(np.array([knot-1e-9,knot+1e-9]))[1]
        assert abs(np.diff(slopes)[0])<1e-7
