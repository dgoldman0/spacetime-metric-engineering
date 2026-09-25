import math

import numpy as np
import pytest

from adm_harness import axial_track as ax
from adm_harness import source_scaling as ss
from adm_harness.numerical_einstein import einstein_fd
import run_lapse_staging_pass as lsp


def analytic_fields(s, z):
    return (.4*math.sin(.7*s+.3*z)+.2, .5*math.cos(.4*s-.6*z)-.1, .3*math.sin(.5*s*z+.2))


def static_lapse(s, z):
    return (.3*math.tanh(z)+.1, 0., 0.)


STAGED = lsp.design_for("lapse_staged")
STAGED_PARAMS = lsp.params_for("lapse_staged")


def fields_at(fields, design, s, z, r):
    jet = ax.stencil_jet(fields, s, z, 1e-4)
    return jet, ax.radial_fields(jet, np.atleast_1d(r), design, z=z, s=s)


@pytest.mark.parametrize("s,z", [(-1., -.2), (0., 1.3), (.5, 2.), (-2.5, -2.4)])
def test_riemann_reproduces_the_generated_einstein_tensor_on_the_staged_rail(s, z):
    jet = ax.service_jet(s, z, STAGED_PARAMS, STAGED)
    r = np.array([.5, 2.2, 4., 5.5, 7., 9.6, 11., 12.8])
    fields = ax.radial_fields(jet, r, STAGED, z=z, s=s)
    g, dg, ddg = ss.metric_jets(fields)
    curvature = ss.riemann(g, dg, ddg)
    tetrad = ss.normal_tetrad(fields)
    einstein = np.einsum("nAa,nBb,nab->nAB", tetrad, tetrad, ss.einstein_from_riemann(g, curvature))/ax.EIGHT_PI
    tensor = ax.frame_tensor(jet, r, STAGED, z=z, s=s)
    assert np.max(np.abs(einstein-tensor)) < 1e-12*max(np.max(np.abs(tensor)), 1.)
    scale = np.max(np.abs(curvature))
    assert np.max(np.abs(curvature+np.einsum("nijkl->njikl", curvature))) < 1e-12*scale
    assert np.max(np.abs(curvature+np.einsum("nijkl->nijlk", curvature))) < 1e-12*scale
    assert np.max(np.abs(curvature-np.einsum("nijkl->nklij", curvature))) < 1e-12*scale
    cyclic = curvature+np.einsum("nijkl->niklj", curvature)+np.einsum("nijkl->niljk", curvature)
    assert np.max(np.abs(cyclic)) < 1e-12*scale


def test_metric_jets_match_the_directly_built_metric():
    design = ax.AxialTrackDesign()
    s, z, r = .3, -.4, 2.3
    _, fields = fields_at(analytic_fields, design, s, z, r)
    g, dg, ddg = ss.metric_jets(fields)

    def metric(x):
        _, f = fields_at(analytic_fields, design, x[0], x[1], x[2])
        return ss.metric_jets(f)[0][0]

    h = 1e-4
    for c in range(3):
        step = np.zeros(4)
        step[c] = h
        numeric = (metric(np.array([s, z, r, 0.])+step)-metric(np.array([s, z, r, 0.])-step))/(2*h)
        assert np.max(np.abs(numeric-dg[0, c])) < 1e-5
    einstein = einstein_fd(metric, [s, z, r, 0.], 5e-4, varying=3)
    reference = ss.einstein_from_riemann(g, ss.riemann(g, dg, ddg))[0]
    assert np.max(np.abs(einstein-reference)) < 5e-4*max(np.max(np.abs(reference)), 1.)


def test_flat_fields_have_zero_curvature_and_unit_static_frame():
    design = ax.AxialTrackDesign()
    _, fields = fields_at(lambda s, z: (0., 0., 0.), design, .2, .1, np.array([.5, 2.2, 3.1]))
    g, dg, ddg = ss.metric_jets(fields)
    assert np.max(np.abs(ss.riemann(g, dg, ddg))) < 1e-12
    assert np.max(np.abs(ss.static_acceleration(g, dg))) < 1e-12
    assert np.allclose(ss.static_boost(fields), np.eye(4))


def test_static_frame_is_orthonormal_and_transforms_tensors_consistently():
    design = ax.AxialTrackDesign()
    jet, fields = fields_at(analytic_fields, design, .3, -.4, np.array([.8, 2.3, 2.6]))
    g = ss.metric_jets(fields)[0]
    tetrad = ss.static_tetrad(fields)
    assert np.allclose(np.einsum("nAa,nab,nBb->nAB", tetrad, g, tetrad), np.diag([-1., 1., 1., 1.]), atol=1e-12)
    assert np.allclose(tetrad[:, 0, 1:], 0.)
    tensor = ax.frame_tensor(jet, [.8, 2.3, 2.6], design, z=-.4)
    normal = ss.normal_tetrad(fields)
    coordinate = np.einsum("nAa,nab,nBb->nAB", np.linalg.inv(normal), tensor, np.linalg.inv(normal))
    direct = np.einsum("nAa,nab,nBb->nAB", tetrad, coordinate, tetrad)
    assert np.allclose(ss.to_static_frame(tensor, fields), direct, atol=1e-12)


def test_static_acceleration_of_a_static_lapse_is_its_log_gradient():
    design = ax.AxialTrackDesign()
    _, fields = fields_at(static_lapse, design, 0., .4, np.array([.5, 1.]))
    g, dg, _ = ss.metric_jets(fields)
    expected = .3/math.cosh(.4)**2
    assert np.allclose(ss.static_acceleration(g, dg), expected, rtol=1e-6)


def test_gaussian_window_reproduces_the_fewster_roman_constant():
    for tau in (.05, .37, 2.):
        assert ss.gaussian_qi_constant(tau) == pytest.approx(1/(64*math.pi**2*tau**4), rel=1e-8)


def test_sampled_requirement_matches_the_pointwise_one_for_a_steady_deficit():
    t = np.linspace(-5., 5., 20001)
    assert ss.sampled_requirement(t, np.full_like(t, -.3), 0., .4) == pytest.approx(
        float(ss.qi_requirement(-.3, .4)), rel=1e-6)
    assert ss.qi_requirement(-.3, 2., .1) == pytest.approx(64*math.pi**2*.3*.2**4)
    assert ss.qi_requirement(.3, 2.) == 0.


def test_casimir_cavity_and_mirror_overhead():
    gap = ss.casimir_gap(.5, 1.)
    deficit = math.pi**2*ss.HBAR*ss.LIGHT_SPEED/(180*gap**4)
    assert deficit == pytest.approx(.5*ss.STRESS_UNIT, rel=1e-12)
    assert 90/(math.pi**2*ss.FINE_STRUCTURE) == pytest.approx(1249.6, rel=1e-4)
    crossover = 2*math.pi*ss.ELECTRON_COMPTON/math.sqrt(4*ss.FINE_STRUCTURE/(3*math.pi))
    assert crossover/ss.ELECTRON_COMPTON == pytest.approx(112.9, rel=1e-3)
    assert ss.mirror_overhead(2*crossover) == pytest.approx(1249.6*(2*crossover/ss.ELECTRON_COMPTON)**2, rel=1e-4)
    assert ss.mirror_overhead(1e-18) == ss.relativistic_mirror_overhead()
    assert ss.relativistic_mirror_overhead() == pytest.approx(1.195e7, rel=2e-3)
    assert ss.relativistic_mirror_overhead(2.) == pytest.approx(8*ss.relativistic_mirror_overhead())
    # the two regimes meet within a factor of two at the crossover
    assert .5 < ss.mirror_overhead(crossover*1.0001)/ss.relativistic_mirror_overhead() < 2


def test_null_direction_matches_the_trust_region_minimum():
    rng = np.random.default_rng(3)
    for _ in range(5):
        a = rng.normal(size=(4, 4))
        tensor = a+a.T
        tensor[:3, 3] = tensor[3, :3] = 0.
        e, value = ss.null_direction(tensor)
        assert np.linalg.norm(e) == pytest.approx(1.)
        assert value == pytest.approx(float(ax.min_null_energy(tensor[None])[0]), rel=1e-8, abs=1e-10)


class FlatSpacetime(ss.AxialSpacetime):
    def __init__(self, fields=lambda s, z: (0., 0., 0.)):
        super().__init__(ax.AxialTrackDesign(), None)
        self.callable = fields

    def fields(self, s, z, r):
        jet = ax.stencil_jet(self.callable, float(s), float(z), 1e-4)
        return jet, ax.radial_fields(jet, [abs(float(r))], self.design, z=float(z), s=float(s))


def test_null_geodesics_of_flat_space_are_straight_and_cross_the_axis():
    spacetime = FlatSpacetime()
    _, fields = spacetime.fields(0., 0., 1.)
    k = ss.launch_vector(fields, (0., -1., 0.))
    lam, xs, ks = ss.trace_null_geodesic(spacetime, np.array([0., 0., 1., 0.]), k, step=.02,
                                         bounds=((-3., 3.), (-3., 3.), 2.5))
    assert np.allclose(ks[:, 0], 1., atol=1e-10)
    assert np.allclose(np.abs(ks[:, 2]), 1., atol=1e-10)
    assert np.allclose(xs[:, 1], 0., atol=1e-10)
    assert np.allclose(np.abs(xs[:, 2]-0.), np.abs(1.-(xs[:, 0]-0.)), atol=1e-8)
    assert np.all(np.diff(lam) > 0)


def test_null_geodesics_stay_null_and_carry_the_generated_null_energy():
    spacetime = FlatSpacetime(analytic_fields)
    _, fields = spacetime.fields(.1, .2, 2.2)
    k = ss.launch_vector(fields, (.3, .8, .5))
    lam, xs, ks = ss.trace_null_geodesic(spacetime, np.array([.1, .2, 2.2, 0.]), k, step=.005,
                                         bounds=((-.3, .5), (-.5, .9), 3.))
    norms = [ss.metric_jets(spacetime.fields(*x[:3])[1])[0][0] for x in xs[::20]]
    drift = [abs(kk@g@kk)/(kk@kk) for kk, g in zip(ks[::20], norms)]
    assert max(drift) < 1e-7
    value, energy = spacetime.null_energy(xs[0], ks[0])
    jet, f = spacetime.fields(*xs[0][:3])
    tensor = ax.frame_tensor(jet, [xs[0][2]], spacetime.design, z=xs[0][1], s=xs[0][0])[0]
    frame_k = np.linalg.solve(ss.normal_tetrad(f)[0].T, ks[0])
    assert value == pytest.approx(frame_k@tensor@frame_k, rel=1e-12)
    assert energy > 0


def test_zero_energy_solution_counts_bound_states_of_known_wells():
    lam = np.linspace(-4., 4., 801)
    for depth, expected in ((.5, 1), (4., 2), (-1., 0)):
        potential = np.where(np.abs(lam) <= 1, -depth, 0.)
        psi, slope = ss.zero_energy_solution(lam, potential)
        # a square well of half-width 1 and depth V0 has 1 + floor(2 sqrt(V0) / pi) bound states for V0 > 0
        if depth > 0:
            assert expected == 1+int(2*math.sqrt(depth)/math.pi)
        assert ss.bound_state_count(psi, slope) == expected
    lam = np.sort(np.concatenate([np.linspace(0., 3., 97), [.013, 1.2345, 2.71]]))
    for value, exact in ((-2.25, np.cos(1.5*lam)), (1., np.cosh(lam))):
        psi, slope = ss.zero_energy_solution(lam, np.full_like(lam, value))
        assert np.max(np.abs(psi-exact)) < 1e-9
