import numpy as np

from adm_harness.vacuum_support import casimir_channels, minimum_vacuum_split
from adm_harness.vacuum_support_elasticity import (
    action_increment, action_kinetic_hessian, kinetic_from_stress,
    stiffness_controls, stored_energy,
)


def test_virtual_work_from_stored_energy_reproduces_all_fitted_pressures():
    target = np.array([-.01, -.02, .03])
    result = minimum_vacuum_split(target, .5)
    host, weights = result['host'], result['weights']
    for hessian in stiffness_controls(host[0]).values():
        np.testing.assert_allclose(stored_energy(np.eye(3), host, weights, hessian), target[0], atol=1e-16)
        for i, pressure in enumerate([target[1], target[2], target[2]]):
            # Vary a principal proper length: B_ii=lambda_i^-2. Work gives
            # P_i = -rho - partial rho / partial log(lambda_i).
            eps = 1e-4
            def rho(x):
                b = np.eye(3)
                b[i, i] = np.exp(-2*x)
                return stored_energy(b, host, weights, hessian)
            derivative = (rho(-2*eps)-8*rho(-eps)+8*rho(eps)-rho(2*eps))/(12*eps)
            np.testing.assert_allclose(-target[0]-derivative, pressure, atol=3e-13)


def test_general_symbolic_stiffness_cannot_change_the_time_kinetic_matrix():
    import sympy as sp
    velocities = sp.symbols('vx vy vz', real=True)
    h = sp.symbols('hr hy hz', real=True)
    vx, vy, vz = velocities
    delta = sp.Matrix([-vx**2, -vy**2, -vz**2, -vy*vz, -vx*vz, -vx*vy])
    coefficients = iter(sp.symbols('c0:21', real=True))
    stiffness = sp.zeros(6)
    for i in range(6):
        for j in range(i, 6):
            stiffness[i, j] = stiffness[j, i] = next(coefficients)
    lagrangian = sum(h[i]*velocities[i]**2/2 for i in range(3))-(delta.T*stiffness*delta)[0]/2
    kinetic = sp.hessian(lagrangian, velocities).subs(dict.fromkeys(velocities, 0))
    assert kinetic == sp.diag(*h)


def test_direct_action_hessian_matches_stress_for_arbitrary_anisotropic_fits():
    rng = np.random.default_rng(301992)
    targets = rng.normal(size=(47, 3))
    split = minimum_vacuum_split(targets, .5)
    for hessian in stiffness_controls(split['host'][:, 0]).values():
        for step in [.04, .02, .01]:
            actual = action_kinetic_hessian(split['host'], split['weights'], hessian, step)
            np.testing.assert_allclose(actual, kinetic_from_stress(targets), atol=2e-14)


def test_positive_material_and_pure_casimir_have_opposite_kinetic_controls():
    host = np.array([2., .3, .4])
    np.testing.assert_allclose(action_kinetic_hessian(host, [0., 0.], np.eye(6)),
                               np.diag([2.3, 2.4, 2.4]), atol=2e-15)
    np.testing.assert_allclose(action_kinetic_hessian(np.zeros(3), [.2, .1], np.zeros((6, 6))),
                               np.diag([-.8, -.4, -.4]), atol=1e-15)
    vacuum = casimir_channels(.2, .1)
    velocity = np.array([.001, 0., 0.])
    assert action_increment(velocity, np.zeros(3), [.2, .1], np.zeros((6, 6))) < 0
    assert kinetic_from_stress(vacuum)[0, 0] < 0
