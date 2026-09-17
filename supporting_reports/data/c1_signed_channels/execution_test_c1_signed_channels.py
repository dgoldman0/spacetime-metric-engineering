import numpy as np
import pytest
from scipy.optimize import linprog

from adm_harness.c1_signed_channels import (
    angular_target_completion, boundary_exchange, bulk_completion_gate,
    channel_tensor, dec_projections, optical_partitions, quadrature, strip_tensor,
)


class AnalyticChart:
    def __init__(self, clock=1., curved=True):
        self.clock, self.curved = clock, curved
        self.coordinate = np.linspace(-2., 2., 4001)
        self.radius, self.lapse, self.radial_scale, *_ = self.jets(self.coordinate)

    def jets(self, x):
        x = np.asarray(x)
        r = np.sqrt(4.+x*x)
        a = self.clock*np.exp(.07*x*x+.12*x) if self.curved else np.full_like(x, self.clock)
        ap = .14*x+.12 if self.curved else np.zeros_like(x)
        app = np.full_like(x, .14 if self.curved else 0.)
        return r, a, np.ones_like(x), x/r, 4./r**3, ap, app


def test_strip_energy_against_regulated_dirichlet_mode_sum():
    length = 1.7
    tau = np.array([.04, .03, .02, .01])
    # Sum n exp(-tau*n) minus its continuum integral, extrapolated to tau=0.
    finite = np.exp(-tau)/np.expm1(-tau)**2-1./tau**2
    intercept = np.polynomial.polynomial.polyfit(tau*tau, finite, 3)[0]
    energy = np.pi/(2.*length)*intercept
    tensor = strip_tensor(2., 1., 0., 0., length)
    np.testing.assert_allclose(4.*np.pi*4.*length*tensor[0], energy, rtol=3e-10)
    np.testing.assert_allclose(energy, -np.pi/(24.*length), rtol=3e-10)


def test_pressure_matches_independent_flat_virtual_work():
    length, h = 2.1, 1e-4
    energy = lambda d: -np.pi/(24.*d)
    force = -(energy(length+h)-energy(length-h))/(2.*h)
    radial = strip_tensor(3., 1., 0., 0., length)[1]*4.*np.pi*9.
    np.testing.assert_allclose(radial, force, rtol=3e-9)


def test_proper_bulk_ward_identity_by_finite_difference():
    chart = AnalyticChart()
    ends, lengths = optical_partitions(chart, (-1.7, 1.6), 1)
    x, h = np.linspace(-1.5, 1.4, 117), 2e-5
    tensor = channel_tensor(chart, x, ends, lengths)
    derivative = (channel_tensor(chart, x+h, ends, lengths)[:, 1]
                  -channel_tensor(chart, x-h, ends, lengths)[:, 1])/(2.*h)
    r, _, _, rp, _, ap, _ = chart.jets(x)
    divergence = derivative+ap*(tensor[:, 0]+tensor[:, 1])+2.*rp/r*tensor[:, 1]
    assert abs(divergence).max() < 2e-13


def test_distributional_end_forces_close_weak_ward_identity():
    chart = AnalyticChart()
    ends, lengths = optical_partitions(chart, (-1.6, 1.7), 4)
    x, w = quadrature(chart, -1.9, 1.9, extra_cuts=ends)
    t = channel_tensor(chart, x, ends, lengths)
    r, a, b, _, _, ap, _ = chart.jets(x)
    phi, phi_x = 1.+.2*x+.1*x*x, .2+.2*x
    bulk = w @ (-a*r*r*t[:, 1]*phi_x+b*ap*a*r*r*t[:, 0]*phi)
    exchange = boundary_exchange(chart, ends, lengths)
    endpoint_a = chart.jets(ends)[1]
    boundary = np.sum(endpoint_a*exchange["force_on_material"]*(1.+.2*ends+.1*ends*ends))/(4.*np.pi)
    np.testing.assert_allclose(bulk+boundary, 0., atol=1e-12)
    assert exchange["force_on_material"][0] > 0
    assert exchange["force_on_material"][-1] < 0


def test_global_clock_normalization_changes_neither_stress_nor_forces():
    first, second = AnalyticChart(), AnalyticChart(clock=17.)
    e1, l1 = optical_partitions(first, (-1.5, 1.5), 7)
    e2, l2 = optical_partitions(second, (-1.5, 1.5), 7)
    np.testing.assert_allclose(e1, e2, atol=2e-13)
    np.testing.assert_allclose(l1, 17.*l2, rtol=2e-13)
    x = np.linspace(-1.4, 1.4, 177)
    np.testing.assert_allclose(channel_tensor(first, x, e1, l1),
                               channel_tensor(second, x, e2, l2), rtol=2e-12)
    np.testing.assert_allclose(boundary_exchange(first, e1, l1)["force_on_material"],
        boundary_exchange(second, e2, l2)["force_on_material"], rtol=2e-12, atol=2e-12)


def test_state_strength_cannot_change_trace_difference():
    one = strip_tensor(2.3, 7., .1, .2, .13)
    two = strip_tensor(2.3, 7., .1, .2, 12.)
    expected = (.2+.1**2)/(48.*np.pi**2*2.3**2)
    np.testing.assert_allclose(one[0]-one[1], expected, rtol=3e-14)
    np.testing.assert_allclose(two[0]-two[1], expected, rtol=3e-14)
    target = np.array([[-.002, -.001, 0.]])
    summary, _ = bulk_completion_gate(target, np.array([[one, two]]))
    assert summary["solver_status"] == 2
    assert summary["direct_exclusion_witness"]["target_projection"] < 0


def test_angular_completion_against_independent_linear_programs():
    rng = np.random.default_rng(439)
    for target in rng.normal(size=(70, 3)):
        v, ordinary = angular_target_completion(target)
        # Direct solve of rho +/- p constraints for a single angular weight.
        coefficients = np.array([0., 4., 4., 0.])
        result = linprog([1.], A_ub=-coefficients[:, None],
            b_ub=dec_projections(target), bounds=(0., None), method="highs")
        feasible = bool(np.min(dec_projections(ordinary)) >= -1e-12)
        assert result.success == feasible
        if feasible:
            np.testing.assert_allclose(v, result.x[0], atol=1e-12)


def test_independent_channels_and_unsupplied_angular_sector_remain_distinct():
    demand = np.array([[-2., 0., 0.], [-3., 0., 0.]])
    basis = np.zeros((2, 2, 3))
    basis[0, 0] = basis[1, 1] = [-1., -1., 0.]
    radial, _ = bulk_completion_gate(demand, basis)
    assert radial["solver_status"] == 2
    hybrid, fields = bulk_completion_gate(demand, basis, grant_angular_target=True)
    np.testing.assert_allclose(hybrid["scaled_channel_strengths"], [2., 3.])
    np.testing.assert_allclose(fields["angular_weight"], [.5, .75])
    assert not hybrid["boundary_material_closure_supplied"]
    assert hybrid["dual_stationarity_max"] < 1e-12


def test_compartments_increase_external_casimir_force_and_keep_internal_balance():
    chart = AnalyticChart(curved=False)
    one_ends, one_lengths = optical_partitions(chart, (-1.5, 1.5), 1)
    many_ends, many_lengths = optical_partitions(chart, (-1.5, 1.5), 8)
    one = boundary_exchange(chart, one_ends, one_lengths)["force_on_material"]
    many = boundary_exchange(chart, many_ends, many_lengths)["force_on_material"]
    np.testing.assert_allclose(many[[0, -1]], 64.*one, rtol=3e-14)
    np.testing.assert_allclose(many[1:-1], 0., atol=1e-13)
    np.testing.assert_allclose(channel_tensor(chart, np.array([-1.6, 1.6]),
                               many_ends, many_lengths), 0.)


def test_invalid_source_and_partition_arguments_are_rejected():
    with pytest.raises(ValueError):
        strip_tensor(1., 1., 0., 0., -1.)
    with pytest.raises(ValueError):
        strip_tensor(1., 1., 0., 0., 1., strength=-1.)
    with pytest.raises(ValueError):
        optical_partitions(AnalyticChart(), (-1., 1.), 0)
    with pytest.raises(ValueError):
        optical_partitions(AnalyticChart(), (-3., 1.), 3)
