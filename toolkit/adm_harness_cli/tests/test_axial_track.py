import math
from dataclasses import replace

import numpy as np
import pytest

from adm_harness import axial_track as ax
from adm_harness.constant_radius_track import (
    ConstantRadiusTrackDesign, flattened_step, packet_position, track_scalars,
)
from adm_harness.numerical_einstein import einstein_fd
from adm_harness.source_ledger import smoothstep_minjerk
from adm_harness.warped_product import evaluate_spherical_demand
from run_constant_radius_service_checks import PARAMS


def analytic_fields(s, z):
    return (.4*math.sin(.7*s+.3*z)+.2, .5*math.cos(.4*s-.6*z)-.1, .3*math.sin(.5*s*z+.2))


def blended_metric(fields, design):
    """Four-dimensional metric of the axial model built directly from the field callable."""
    def metric(x):
        s, z, r, _ = x
        chi = ax.wall_blend(np.array([r]), design)[0][0]
        c = ax.transverse_profile(np.array([r]), design)[0][0]
        log_alpha, log_a, beta = fields(s, z)
        alpha, a, shift = math.exp(chi*log_alpha), math.exp(chi*log_a), chi*beta
        g = np.zeros((4, 4))
        g[0, 0] = -alpha*alpha+a*a*shift*shift
        g[0, 1] = g[1, 0] = a*a*shift
        g[1, 1] = a*a
        g[2, 2] = 1.
        g[3, 3] = c*c
        return g
    return metric


def brute_force_frame(fields, design, s, z, r, step=1e-3):
    metric = blended_metric(fields, design)
    einstein = einstein_fd(metric, [s, z, r, 0.], step, varying=3)
    g = metric([s, z, r, 0.])
    alpha = math.sqrt(-(g[0, 0]-g[0, 1]**2/g[1, 1]))
    a = math.sqrt(g[1, 1])
    shift = g[0, 1]/g[1, 1]
    frame = np.zeros((4, 4))
    frame[0, :2] = (1/alpha, -shift/alpha)
    frame[1, 1] = 1/a
    frame[2, 2] = 1.
    frame[3, 3] = 1/math.sqrt(g[3, 3])
    return frame@einstein@frame.T/ax.EIGHT_PI


def test_step_jet_matches_flattened_step_and_its_derivatives():
    t = np.linspace(-.1, 1.1, 241)
    value, first, second = ax.step_jet(t, .1)
    reference = np.array([flattened_step(x, smoothstep_minjerk, .1) for x in t])
    assert np.max(np.abs(value-reference)) < 1e-14
    h = 1e-5
    plus, minus = ax.step_jet(t+h, .1)[0], ax.step_jet(t-h, .1)[0]
    assert np.max(np.abs(first-(plus-minus)/(2*h))) < 1e-6
    plus1, minus1 = ax.step_jet(t+h, .1)[1], ax.step_jet(t-h, .1)[1]
    assert np.max(np.abs(second-(plus1-minus1)/(2*h))) < 1e-4


@pytest.mark.parametrize("spacing", ["linear", "logarithmic"])
def test_wall_blend_is_one_in_core_zero_outside_with_consistent_derivatives(spacing):
    design = ax.AxialTrackDesign(core_radius=1.5, wall_width=2., wall_spacing=spacing)
    r = np.linspace(.2, 4.2, 401)
    chi, d1, d2 = ax.wall_blend(r, design)
    assert np.all(chi[r <= 1.5] == 1) and np.all(chi[r >= 3.5] == 0)
    assert np.all(np.diff(chi) <= 0)
    h = 1e-6
    assert np.max(np.abs(d1-(ax.wall_blend(r+h, design)[0]-ax.wall_blend(r-h, design)[0])/(2*h))) < 1e-6
    assert np.max(np.abs(d2-(ax.wall_blend(r+h, design)[1]-ax.wall_blend(r-h, design)[1])/(2*h))) < 1e-5


def test_flat_fields_give_exact_vacuum_everywhere():
    jet = {key: np.zeros(3) for key in ("v", "s", "z", "ss", "sz", "zz")}
    design = ax.AxialTrackDesign()
    tensor = ax.frame_tensor(jet, np.linspace(0., 4., 81), design)
    assert np.max(np.abs(tensor)) == 0.
    assert np.all(ax.classify(tensor)["type"] == ax.VACUUM)


def test_static_string_core_is_a_nambu_goto_string_with_gauss_bonnet_deficit():
    design = ax.AxialTrackDesign(string_curvature=.2)
    jet = {key: np.zeros(3) for key in ("v", "s", "z", "ss", "sz", "zz")}
    r = np.linspace(.05, 3.5, 70)
    tensor = ax.frame_tensor(jet, r, design)
    curvature = ax.transverse_profile(r, design)[2]
    assert np.allclose(tensor[:, 0, 0], curvature/ax.EIGHT_PI, atol=1e-14)
    assert np.allclose(tensor[:, 1, 1], -curvature/ax.EIGHT_PI, atol=1e-14)
    others = tensor.copy()
    others[:, 0, 0] = others[:, 1, 1] = 0.
    assert np.max(np.abs(others)) == 0.
    radius, weights = ax.wall_nodes(design)
    value, _, k = ax.transverse_profile(radius, design)
    core = 1-math.cos(math.sqrt(.2)*design.core_radius)
    integral = 2*math.pi*(core+np.sum(weights*k*value))
    assert integral == pytest.approx(ax.deficit_angle(design), rel=1e-9)
    kind = ax.classify(tensor)
    string = r < design.outer_radius
    assert np.all(kind["type"][string] == ax.TYPE_I) and np.all(kind["type"][~string] == ax.VACUUM)
    assert np.allclose(kind["rest_null_margin"][string], 0., atol=1e-14)


def test_closing_string_core_is_rejected():
    with pytest.raises(ValueError):
        ax.transverse_profile(np.array([1.]), ax.AxialTrackDesign(string_curvature=1.))


@pytest.mark.parametrize("s,z,r", [(.3, -.4, 2.1), (1.1, .8, 2.45), (-.6, 1.3, 2.7), (.9, -1.2, 1.9)])
@pytest.mark.parametrize("curvature", [0., .15])
def test_generated_tensor_matches_brute_force_four_dimensional_kernel(s, z, r, curvature):
    design = ax.AxialTrackDesign(core_radius=1.75, wall_width=1., string_curvature=curvature)
    jet = ax.stencil_jet(analytic_fields, s, z, 1e-4)
    generated = ax.frame_tensor(jet, [r], design)[0]
    reference = brute_force_frame(analytic_fields, design, s, z, r)
    scale = np.max(np.abs(reference))
    assert scale > 1e-3
    assert np.max(np.abs(generated-reference)) < 2e-5*max(scale, 1.)


def test_core_is_an_exact_product_matching_the_spherical_track_angular_pressure():
    design = ax.AxialTrackDesign()
    for s, z in [(-.2, .1), (.5, .6), (1.2, 1.5), (2.4, -.8), (0., 0.), (1.6, 2.1)]:
        jet = ax.service_jet(s, z, PARAMS, design)
        tensor = ax.frame_tensor(jet, [0., .9, 1.7], design)
        assert np.max(np.abs(tensor[:, :2, :2])) == 0.
        assert np.max(np.abs(tensor[:, :3, 2][:, :2])) == 0.
        assert np.all(tensor[:, 2, 2] == tensor[:, 3, 3])
        spherical = evaluate_spherical_demand(s, z, PARAMS, .0025, .0025,
                                              scalar_evaluator=lambda a, b, p: track_scalars(a, b, p, design.track))
        assert abs(tensor[0, 2, 2]-spherical["p_omega"]) < 3e-4


def test_service_wall_agreement_converges_at_second_order_in_the_brute_force_step():
    design = ax.AxialTrackDesign()
    fields = lambda a, b: ax.core_fields(a, b, PARAMS, design)
    generated = ax.frame_tensor(ax.service_jet(-.8, -1.6, PARAMS, design), [2.3], design)[0]
    errors = []
    for step in (5e-3, 2.5e-3, 1.25e-3):
        reference = brute_force_frame(fields, design, -.8, -1.6, 2.3, step=step)
        errors.append(np.max(np.abs(generated-reference))/np.max(np.abs(reference)))
    assert errors[0] < 1e-3 and errors[0]/errors[1] > 3.5 and errors[1]/errors[2] > 3.5


@pytest.mark.parametrize("s,z,r", [(.2, .3, 2.2), (1.4, 1.2, 2.5)])
def test_service_wall_tensor_matches_brute_force_kernel(s, z, r):
    design = ax.AxialTrackDesign()
    fields = lambda a, b: ax.core_fields(a, b, PARAMS, design)
    generated = ax.frame_tensor(ax.service_jet(s, z, PARAMS, design), [r], design)[0]
    reference = brute_force_frame(fields, design, s, z, r, step=2.5e-3)
    scale = np.max(np.abs(reference))
    assert np.max(np.abs(generated-reference)) < 2e-3*scale


def random_tensors(count, seed):
    generator = np.random.default_rng(seed)
    tensors = np.zeros((count, 4, 4))
    block = generator.normal(size=(count, 3, 3))
    tensors[:, :3, :3] = block+np.transpose(block, (0, 2, 1))
    tensors[:, 3, 3] = generator.normal(size=count)
    return tensors


def sampled_null_minimum(tensor, count=400):
    theta = np.linspace(0, math.pi, count)
    phi = np.linspace(0, 2*math.pi, 2*count)
    tt, pp = np.meshgrid(theta, phi, indexing="ij")
    e = np.stack([np.cos(tt), np.sin(tt)*np.cos(pp), np.sin(tt)*np.sin(pp)], axis=-1)
    k = np.concatenate([np.ones(e.shape[:-1]+(1,)), e], axis=-1)
    return float(np.min(np.einsum("...a,ab,...b->...", k, tensor, k)))


def test_null_energy_minimum_matches_dense_sphere_sampling():
    tensors = random_tensors(12, 3)
    exact = ax.min_null_energy(tensors)
    for tensor, value in zip(tensors, exact):
        sampled = sampled_null_minimum(tensor)
        assert value <= sampled+1e-12
        assert value == pytest.approx(sampled, abs=5e-4)


def test_null_energy_minimum_handles_the_hard_case_and_diagonal_tensors():
    diagonal = np.diag([1., -.3, .2, .5])[None]
    assert ax.min_null_energy(diagonal)[0] == pytest.approx(.7, abs=1e-14)
    hard = np.diag([0., -1., 1., 2.])
    hard[0, 2] = hard[2, 0] = .5
    assert ax.min_null_energy(hard[None])[0] == pytest.approx(sampled_null_minimum(hard), abs=5e-4)


def boost(tensor, rapidity):
    c, s = math.cosh(rapidity), math.sinh(rapidity)
    matrix = np.eye(4)
    matrix[:2, :2] = [[c, s], [s, c]]
    return matrix@tensor@matrix.T


def test_classifier_recovers_boosted_type_i_type_iv_and_null_dust():
    rest = np.diag([2., .3, -.5, .7])
    result = ax.classify(boost(rest, .8)[None])
    assert result["type"][0] == ax.TYPE_I and result["certified"][0]
    assert result["rest_energy_density"][0] == pytest.approx(2., rel=1e-10)
    assert sorted(result["principal_pressures"][0]) == pytest.approx([-.5, .3, .7], rel=1e-10)
    assert result["rest_null_margin"][0] == pytest.approx(1.5, rel=1e-10)
    type_iv = np.diag([1., -1., .2, .2])
    type_iv[0, 1] = type_iv[1, 0] = -.4
    result = ax.classify(type_iv[None])
    assert result["type"][0] == ax.TYPE_IV and result["certified"][0]
    null = np.array([1., 1., 0., 0.])
    dust = np.outer(null, null)+np.diag([0., 0., .3, .3])
    assert ax.classify(dust[None])["type"][0] == ax.TYPE_II_III
    degenerate = np.diag([0., 0., -.4, -.4])
    result = ax.classify(degenerate[None])
    assert result["type"][0] == ax.TYPE_I and result["certified"][0]
    assert result["rest_null_margin"][0] == pytest.approx(-.4)


def test_principal_frame_recovers_source_velocity_and_axis_labels():
    rest = np.diag([2., .3, -.5, .7])
    frame = ax.principal_frame(boost(rest, .8)[None])
    assert frame["generic"][0]
    assert frame["energy_density"][0] == pytest.approx(2., rel=1e-10)
    assert (frame["p_z"][0], frame["p_r"][0], frame["p_phi"][0]) == pytest.approx((.3, -.5, .7), rel=1e-10)
    assert (frame["v_z"][0], frame["v_r"][0]) == pytest.approx((-math.tanh(.8), 0.), abs=1e-12)
    turn = np.eye(4)
    turn[1:3, 1:3] = [[math.cos(.3), -math.sin(.3)], [math.sin(.3), math.cos(.3)]]
    frame = ax.principal_frame((turn@boost(rest, -.5)@turn.T)[None])
    assert (frame["p_z"][0], frame["p_r"][0]) == pytest.approx((.3, -.5), rel=1e-10)
    assert (frame["v_z"][0], frame["v_r"][0]) == pytest.approx((math.tanh(.5)*math.cos(.3),
                                                                math.tanh(.5)*math.sin(.3)), rel=1e-10)
    repeated = ax.principal_frame(np.diag([0., 0., -.4, -.4])[None])
    assert not repeated["generic"][0] and np.isnan(repeated["v_z"][0])


def test_radial_fields_match_the_frame_tensor_fields_and_the_service_core():
    jet = ax.service_jet(.3, .2, PARAMS, STAGED)
    r = np.array([0., 1., 2.1, 3.3, 6.])
    fields = ax.radial_fields(jet, r, STAGED, z=.2)
    assert fields["alpha"][:2] == pytest.approx(np.exp(jet["v"][0])*np.ones(2), rel=1e-14)
    assert fields["A"][:2] == pytest.approx(np.exp(jet["v"][1])*np.ones(2), rel=1e-14)
    assert fields["alpha"][-1] == fields["A"][-1] == 1. and fields["beta"][-1] == 0.
    assert fields["C"] == pytest.approx(r)


def test_classifier_agrees_with_spherical_block_discriminant():
    generator = np.random.default_rng(5)
    for _ in range(40):
        rho, pressure, current, angular = generator.normal(size=4)
        tensor = np.diag([rho, pressure, angular, angular])
        tensor[0, 1] = tensor[1, 0] = -current
        expected = ax.TYPE_I if abs(rho+pressure) > 2*abs(current) else ax.TYPE_IV
        assert ax.classify(tensor[None])["type"][0] == expected


def test_wall_nodes_integrate_the_transverse_area():
    for spacing in ("linear", "logarithmic"):
        design = ax.AxialTrackDesign(core_radius=1.2, wall_width=2.5, wall_spacing=spacing)
        radius, weights = ax.wall_nodes(design)
        assert np.sum(weights*2*math.pi*radius) == pytest.approx(math.pi*(3.7**2-1.2**2), rel=1e-12)


def test_design_validation():
    with pytest.raises(ValueError):
        ax.AxialTrackDesign(wall_width=0.)
    with pytest.raises(ValueError):
        ax.AxialTrackDesign(wall_spacing="cubic")
    with pytest.raises(ValueError):
        ax.AxialTrackDesign(string_curvature=-.1)
    assert replace(ax.AxialTrackDesign(), track=ConstantRadiusTrackDesign(reset_front_start=-.4)).track.reset_front


def exact_jet(log_alpha, log_a, beta):
    """Analytic (sigma, z) jet from callables returning (value, d_s, d_z, d_ss, d_sz, d_zz)."""
    def build(s, z):
        parts = [f(s, z) for f in (log_alpha, log_a, beta)]
        return {key: np.array([p[i] for p in parts]) for i, key in enumerate(("v", "s", "z", "ss", "sz", "zz"))}
    return build


def zero(s, z):
    return (0.,)*6


def moving_window(amplitude):
    def f(s, z):
        u = z-.7*s
        g = amplitude*math.exp(-u*u/.2)
        g1 = -2*u/.2*g
        g2 = (4*u*u/.04-2/.2)*g
        return (g, -.7*g1, g1, .49*g2, -.7*g2, g2)
    return f


def test_shift_wall_along_track_null_energies_follow_the_exact_shear_identity():
    design = ax.AxialTrackDesign(core_radius=1.5, wall_width=1.2)
    r = np.linspace(1.52, 2.68, 59)
    chi, d1, d2 = ax.wall_blend(r, design)
    for s, z in [(.1, .3), (.6, .2), (-.3, -.4)]:
        jet = exact_jet(zero, zero, moving_window(.6))(s, z)
        tensor = ax.frame_tensor(jet, r, design)
        beta = jet["v"][2]
        gradient, laplacian = d1*beta, (d2+d1/r)*beta
        for sign in (1, -1):
            null = tensor[:, 0, 0]+tensor[:, 1, 1]+2*sign*tensor[:, 0, 1]
            assert np.allclose(ax.EIGHT_PI*null, -(gradient**2+sign*laplacian), atol=1e-12)
    uniform = lambda s, z: (.6, 0., 0., 0., 0., 0.)
    jet = exact_jet(zero, zero, uniform)(0., 0.)
    tensor = ax.frame_tensor(jet, r, design)
    assert np.max(np.abs(tensor[:, 1, 2])) == 0. and np.max(np.abs(tensor[:, 0, 2])) == 0.
    gradient, laplacian = .6*d1, .6*(d2+d1/r)
    kinds = ax.classify(tensor, floor=1e-12)["type"]
    margin = np.abs(laplacian)-gradient**2
    assert np.all(kinds[margin > 1e-6] == ax.TYPE_IV) and np.all(kinds[margin < -1e-6] == ax.TYPE_I)
    assert (margin > 1e-6).sum() > 40 and (margin < -1e-6).sum() > 0


def test_radial_null_energies_follow_the_warped_product_hessian_identity():
    design = ax.AxialTrackDesign(core_radius=1.5, wall_width=1.2)
    time_only = lambda amplitude, rate: (lambda s, z: (amplitude*math.exp(-rate*s), -rate*amplitude*math.exp(-rate*s),
                                                      0., rate*rate*amplitude*math.exp(-rate*s), 0., 0.))
    r = np.linspace(1.52, 2.68, 59)
    chi, d1, d2 = ax.wall_blend(r, design)
    s = .4
    jet = exact_jet(time_only(1.3, .8), time_only(1.1, .5), zero)(s, 0.)
    tensor = ax.frame_tensor(jet, r, design)
    fields = ax.radial_jets(jet, chi, d1, d2)
    alpha, a = fields["alpha"], fields["A"]
    hess_ss = fields["A_ss"]-fields["alpha_s"]/alpha*fields["A_s"]-alpha*fields["alpha_r"]*fields["A_r"]
    hess_sr = fields["A_sr"]-fields["alpha_r"]/alpha*fields["A_s"]
    for sign in (1, -1):
        hessian = hess_ss/alpha**2+sign*2*hess_sr/alpha+fields["A_rr"]
        expected = -hessian/a+fields["alpha_r"]/(r*alpha)
        null = tensor[:, 0, 0]+tensor[:, 2, 2]+2*sign*tensor[:, 0, 2]
        assert np.allclose(ax.EIGHT_PI*null, expected, rtol=1e-10, atol=1e-10)


def test_shift_free_wall_with_static_spatial_metric_carries_no_energy_flux():
    design = ax.AxialTrackDesign(core_radius=1.5, wall_width=1.2)
    lapse = lambda s, z: (1.5*math.sin(s)*math.cos(z), 1.5*math.cos(s)*math.cos(z), -1.5*math.sin(s)*math.sin(z),
                          -1.5*math.sin(s)*math.cos(z), -1.5*math.cos(s)*math.sin(z), -1.5*math.sin(s)*math.cos(z))
    stretch = lambda s, z: (2*math.cos(.8*z), 0., -1.6*math.sin(.8*z), 0., 0., -1.28*math.cos(.8*z))
    r = np.linspace(1.52, 2.68, 59)
    tensor = ax.frame_tensor(exact_jet(lapse, stretch, zero)(.7, .3), r, design)
    assert np.max(np.abs(tensor[:, 0, 1:])) < 1e-12
    kinds = ax.classify(tensor, floor=1e-12)
    assert np.all(kinds["type"] == ax.TYPE_I)


STAGED = ax.AxialTrackDesign(lapse_layer=(2.2, 2.5), stretch_layer=(1.75, .8), shift_layer=(2.6, .9),
                             sheath_log_lapse=3., sheath_rise=(1.75, 1.2), sheath_fall=(3.2, 1.5), sheath_length=(.5, .6))


def staged_metric(fields, design):
    """Four-dimensional metric with separate field layers and the log-lapse sheath, built directly."""
    fraction = design.track.join_fraction

    def metric(x):
        s, z, r, _ = x
        radius = np.array([r])
        chi = {name: ax.layer_blend(radius, design.layers[name], fraction)[0][0] for name in ("alpha", "A", "beta")}
        (e, _, _), (h, _, _) = ax.sheath_terms(radius, z, design)
        (ec, _, _), (hc, _, _) = ax.conformal_terms(radius, z, design)
        log_alpha, log_a, beta = fields(s, z)
        alpha = math.exp(chi["alpha"]*log_alpha+h*e[0]+hc*ec[0])
        a, shift = math.exp(chi["A"]*log_a+hc*ec[0]), chi["beta"]*beta
        g = np.zeros((4, 4))
        g[0, 0] = -alpha*alpha+a*a*shift*shift
        g[0, 1] = g[1, 0] = a*a*shift
        g[1, 1] = a*a
        g[2, 2] = 1.
        g[3, 3] = r*r
        return g
    return metric


def test_equal_staged_layers_reproduce_the_single_blend_exactly():
    staged = ax.AxialTrackDesign(lapse_layer=(1.75, 1.), stretch_layer=(1.75, 1.), shift_layer=(1.75, 1.))
    jet = ax.stencil_jet(analytic_fields, .4, -.3, 1e-4)
    r = np.linspace(1.6, 2.9, 27)
    assert np.allclose(ax.frame_tensor(jet, r, staged), ax.frame_tensor(jet, r, ax.AxialTrackDesign()),
                       rtol=1e-12, atol=1e-14)


@pytest.mark.parametrize("s,z,r", [(.3, .2, 2.0), (-.5, .7, 2.4), (.8, .9, 2.9), (.1, -.8, 3.6)])
def test_staged_tensor_with_sheath_matches_brute_force_kernel(s, z, r):
    jet = ax.stencil_jet(analytic_fields, s, z, 1e-4)
    generated = ax.frame_tensor(jet, [r], STAGED, z=z)[0]
    metric = staged_metric(analytic_fields, STAGED)
    einstein = einstein_fd(metric, [s, z, r, 0.], 5e-4, varying=3)
    g = metric([s, z, r, 0.])
    alpha = math.sqrt(-(g[0, 0]-g[0, 1]**2/g[1, 1]))
    frame = np.zeros((4, 4))
    frame[0, :2] = (1/alpha, -(g[0, 1]/g[1, 1])/alpha)
    frame[1, 1] = 1/math.sqrt(g[1, 1])
    frame[2, 2] = 1.
    frame[3, 3] = 1/r
    reference = frame@einstein@frame.T/ax.EIGHT_PI
    assert np.max(np.abs(generated-reference)) < 5e-5*max(np.max(np.abs(reference)), 1.)


FOLLOW_PATH = (-1.4, -1.4, .9, 2.1, .95, -1.4, .3, .2, .4)
STAGED_FOLLOW = replace(STAGED, track=ConstantRadiusTrackDesign(packet_path=FOLLOW_PATH), sheath_length=(5., 1.),
                        sheath_follow=(.2, .8), sheath_schedule=(-.9, .6, .8))


def time_staged_metric(fields, design):
    """Four-dimensional metric with a lapse sheath that follows the packet on a schedule, built directly."""
    fraction = design.track.join_fraction

    def metric(x):
        s, z, r, _ = x
        radius = np.array([r])
        chi = {name: ax.layer_blend(radius, design.layers[name], fraction)[0][0] for name in ("alpha", "A", "beta")}
        (e, _, _), h = ax.sheath_jets(radius, s, z, design)
        log_alpha, log_a, beta = fields(s, z)
        alpha = math.exp(chi["alpha"]*log_alpha+h["v"]*e[0])
        a, shift = math.exp(chi["A"]*log_a), chi["beta"]*beta
        g = np.zeros((4, 4))
        g[0, 0] = -alpha*alpha+a*a*shift*shift
        g[0, 1] = g[1, 0] = a*a*shift
        g[1, 1] = a*a
        g[2, 2] = 1.
        g[3, 3] = r*r
        return g
    return metric


def test_time_staged_sheath_jets_match_finite_differences():
    r = np.array([2.2, 2.9])
    h = 1e-4

    def value(s, z):
        return ax.sheath_jets(r, s, z, STAGED_FOLLOW)[1]["v"]

    for s, offset in ((-.6, .5), (-.2, -.6), (.3, .35), (.7, -.4)):
        z = packet_position(s, FOLLOW_PATH)+offset
        jet = ax.sheath_jets(r, s, z, STAGED_FOLLOW)[1]
        assert jet["s"] == pytest.approx((value(s+h, z)-value(s-h, z))/(2*h), rel=1e-5, abs=1e-8)
        assert jet["z"] == pytest.approx((value(s, z+h)-value(s, z-h))/(2*h), rel=1e-5, abs=1e-8)
        assert jet["ss"] == pytest.approx((value(s+h, z)-2*value(s, z)+value(s-h, z))/h**2, rel=1e-3, abs=1e-5)
        assert jet["zz"] == pytest.approx((value(s, z+h)-2*value(s, z)+value(s, z-h))/h**2, rel=1e-3, abs=1e-5)
        mixed = (value(s+h, z+h)-value(s+h, z-h)-value(s-h, z+h)+value(s-h, z-h))/(4*h*h)
        assert jet["sz"] == pytest.approx(mixed, rel=1e-3, abs=1e-5)


@pytest.mark.parametrize("s,offset,r", [(-.6, .5, 2.2), (-.2, -.6, 2.9), (.3, .35, 3.6), (.7, -.4, 4.1)])
def test_time_staged_sheath_tensor_matches_brute_force_kernel(s, offset, r):
    z = packet_position(s, FOLLOW_PATH)+offset
    jet = ax.stencil_jet(analytic_fields, s, z, 1e-4)
    generated = ax.frame_tensor(jet, [r], STAGED_FOLLOW, z=z, s=s)[0]
    metric = time_staged_metric(analytic_fields, STAGED_FOLLOW)
    einstein = einstein_fd(metric, [s, z, r, 0.], 5e-4, varying=3)
    g = metric([s, z, r, 0.])
    alpha = math.sqrt(-(g[0, 0]-g[0, 1]**2/g[1, 1]))
    frame = np.zeros((4, 4))
    frame[0, :2] = (1/alpha, -(g[0, 1]/g[1, 1])/alpha)
    frame[1, 1] = 1/math.sqrt(g[1, 1])
    frame[2, 2] = 1.
    frame[3, 3] = 1/r
    reference = frame@einstein@frame.T/ax.EIGHT_PI
    assert np.max(np.abs(generated-reference)) < 5e-5*max(np.max(np.abs(reference)), 1.)
    with pytest.raises(ValueError):
        ax.frame_tensor(jet, [r], STAGED_FOLLOW, z=z)


def test_following_sheath_validation():
    with pytest.raises(ValueError):
        replace(STAGED, sheath_follow=(.2, .8))
    with pytest.raises(ValueError):
        replace(STAGED_FOLLOW, sheath_schedule=(0., .5, .8))


def test_lapse_sheath_alone_carries_no_energy_flux_and_is_type_i():
    jet = {key: np.zeros(3) for key in ("v", "s", "z", "ss", "sz", "zz")}
    r = np.linspace(1.76, 4.69, 120)
    for z in (0., .4, .8):
        tensor = ax.frame_tensor(jet, r, STAGED, z=z)
        assert np.max(np.abs(tensor[:, 0, 1:])) == 0.
        kinds = ax.classify(tensor, floor=1e-12)["type"]
        assert np.all(np.isin(kinds, [ax.TYPE_I, ax.VACUUM]))


def test_staged_boundary_nodes_integrate_the_layer_area():
    radius, weights = ax.wall_nodes(STAGED)
    assert radius.min() >= STAGED.core_radius and radius.max() <= STAGED.outer_radius
    assert np.sum(weights*2*math.pi*radius) == pytest.approx(math.pi*(STAGED.outer_radius**2-1.75**2), rel=1e-12)


def test_staged_design_validation():
    with pytest.raises(ValueError):
        ax.AxialTrackDesign(stretch_layer=(1.5, 1.))
    with pytest.raises(ValueError):
        ax.AxialTrackDesign(shift_layer=(2., 1.), string_curvature=.1)


CONFORMAL = replace(STAGED, conformal_log_scale=2.5, conformal_rise=(1.75, .7), conformal_fall=(3.4, 1.))


@pytest.mark.parametrize("s,z,r", [(.3, .2, 2.1), (-.4, .6, 2.9), (.7, -.9, 3.9)])
def test_conformal_sheath_matches_brute_force_kernel(s, z, r):
    jet = ax.stencil_jet(analytic_fields, s, z, 1e-4)
    generated = ax.frame_tensor(jet, [r], CONFORMAL, z=z)[0]
    metric = staged_metric(analytic_fields, CONFORMAL)
    einstein = einstein_fd(metric, [s, z, r, 0.], 5e-4, varying=3)
    g = metric([s, z, r, 0.])
    alpha = math.sqrt(-(g[0, 0]-g[0, 1]**2/g[1, 1]))
    frame = np.zeros((4, 4))
    frame[0, :2] = (1/alpha, -(g[0, 1]/g[1, 1])/alpha)
    frame[1, 1] = 1/math.sqrt(g[1, 1])
    frame[2, 2] = 1.
    frame[3, 3] = 1/r
    reference = frame@einstein@frame.T/ax.EIGHT_PI
    assert np.max(np.abs(generated-reference)) < 5e-5*max(np.max(np.abs(reference)), 1.)


def test_conformal_rise_carries_no_flux_under_a_moving_shift():
    design = ax.AxialTrackDesign(lapse_layer=(4., 1.), stretch_layer=(4., 1.), shift_layer=(4., 1.),
                                 conformal_log_scale=3., conformal_rise=(1.75, 1.5), conformal_fall=(3.5, .4))
    jet = ax.stencil_jet(analytic_fields, .3, .2, 1e-4)
    r = np.linspace(1.76, 3.24, 60)
    tensor = ax.frame_tensor(jet, r, design, z=.2)
    assert np.max(np.abs(tensor[:, 0, 1:])) < 1e-9*np.max(np.abs(tensor))
