import numpy as np

from adm_harness.graded_electrothermal import SparseRows
from run_joint_coupled_passivity import add_coupling_constraints


def test_cross_coupled_positive_stiffness_can_reverse_the_axial_change():
    ell = np.array([1., 1.1, 1.2])[:, None]
    radius = np.array([2., 1.8, 1.6])[:, None]
    g1, g2 = ell+.8*radius, .8*ell+radius
    m = .5*ell**2+.8*ell*radius+.5*radius**2
    p, q = -ell*g1, -.5*radius*g2
    assert np.all(np.diff(g1[:,0])*np.diff(ell[:,0]) < 0)
    for mode in ('tangent', 'pairs', 'planes'):
        problem = dict(size=3, ub=SparseRows(13))
        add_coupling_constraints(problem, ell, radius, mode)
        v = np.r_[np.zeros(3), m[:,0], p[:,0], q[:,0], 0.]
        assert np.max(problem['ub'].matrix()@v) < -1e-3
        # Reversing the energy potential also reverses every monotonicity.
        assert np.min(problem['ub'].matrix()@(-v)) > 1e-3
