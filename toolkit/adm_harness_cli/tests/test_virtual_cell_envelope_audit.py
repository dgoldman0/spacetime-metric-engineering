import numpy as np
from numpy.testing import assert_allclose
from scipy.optimize import linprog
from adm_harness.virtual_cell_transport import upwind_operator
from adm_harness.virtual_cell_envelope_audit import least_upwind_supersolution


def test_triangular_envelope_matches_independent_linear_optimization():
    rng=np.random.default_rng(823)
    for sign in [-1.,1.]:
        for unused in range(8):
            g=upwind_operator(sign*rng.uniform(.5,1.5,10),.03)-.1*np.eye(9)
            source=rng.uniform(0,1,9); initial=rng.uniform(0,.5,9)
            z=least_upwind_supersolution(g,source,initial)
            lp=linprog(np.ones(9),A_ub=g,b_ub=-source,bounds=list(zip(initial,[None]*9)),method='highs')
            assert lp.success
            assert_allclose(z,lp.x,atol=1e-10)
            assert np.max(g@z+source)<1e-12
