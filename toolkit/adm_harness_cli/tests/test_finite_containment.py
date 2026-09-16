import numpy as np
import pytest
from numpy.testing import assert_allclose
from scipy.integrate import quad
from scipy.optimize import linprog

from adm_harness.containment_ensemble import required_exchange
from adm_harness.finite_containment import (
    EVOLUTION_BASIS, allocate_field, annular_factor, controlled_material_history,
    field_interfaces, geometry, necessary_host_bound, particle_inventory,
    reservoir_interval,
)
from adm_harness.magnetic_load_balance import support_cone


def sample_geometry(eta=1.2):
    lr = np.array([[1.], [.8], [.6]])
    lt = np.array([[1.], [1.1], [1.2]])
    return geometry(10*lr*lt**2, lr, lt, [2.], .2, eta=eta), lr, lt


def test_finite_coax_energy_ampere_currents_end_force_and_torque():
    g, _, _ = sample_geometry()
    B = np.full((3, 1), .7)
    f = field_interfaces(B, g, background_axial_field=.3)
    for i in range(3):
        r, L, nc = (g[k][i, 0] for k in ("inner_radius", "leg", "cartridges"))
        ro, C = g["eta"]*r, f["inner_field"][i, 0]*r
        energy = nc*L*quad(lambda s: .5*(C/s)**2*2*np.pi*s, r, ro)[0]
        end_force = nc*quad(lambda s: .5*(C/s)**2*2*np.pi*s, r, ro)[0]
        torque = nc*quad(lambda s: s*.3*(C/s)*2*np.pi*s, r, ro)[0]
        axial_current = nc*(2*np.pi*r*L*C/r+2*np.pi*ro*L*C/ro)
        return_current = 2*nc*quad(lambda s: C/s*2*np.pi*s, r, ro)[0]
        assert_allclose(energy, B[i, 0])
        assert_allclose(end_force, f["axial_force_per_end_set"][i, 0])
        assert_allclose(torque, f["torque_per_end_set"][i, 0])
        assert_allclose(axial_current, f["axial_current_integral"][i, 0])
        assert_allclose(return_current, f["return_current_integral"][i, 0])
        # Surface charge flux is continuous through all four faces.
        for radius in (r, (r+ro)/2, ro):
            assert_allclose(2*np.pi*radius*C/radius, f["current_per_cartridge"][i, 0])


def test_radial_stress_divergence_and_two_separate_boundary_reactions():
    r, eta, C, L = 2., 1.3, .7, 3.
    m = C*C/(2*r*r)
    for s in np.linspace(r, eta*r, 20):
        b = C*C/(2*s*s)
        pr, pt = b-m, -b-m
        derivative = -C*C/s**3
        assert_allclose(derivative+(pr-pt)/s, 0., atol=1e-16)
    M = m*np.pi*r*r*(eta**2-1)*L
    U = np.pi*L*C*C*np.log(eta)
    assert_allclose(M, annular_factor(eta)*U)
    assert_allclose(m-m, 0.)
    assert_allclose(2*np.pi*(eta*r)**2*L*(m/eta**2-m), -2*M)


def test_reallocation_counts_return_reactions_and_reconstructs_trace():
    target = np.array([5., .4, -.3])
    result = allocate_field(target, .1, .2, .8, .2, eta=1.1,
                            carrier_energy=.3, carrier_axial_pressure=.1, return_pressure=.02)
    parts = result["components"]
    assert np.min(parts) >= -1e-14
    assert_allclose(parts[0]+parts[1], .2)
    assert_allclose(parts[2]+parts[3]+2*parts[4], .8)
    assert_allclose(result["tensor"][2], -.5)
    assert_allclose(result["tensor"][0], parts.sum())
    assert_allclose(result["shortfall"], support_cone(*(target-result["tensor"]), .1)["shortfall"])


def test_carriers_keep_charge_when_the_current_switches_off():
    J = np.array([[2., 0.], [4., 0.], [0., 0.]])
    r = particle_inventory(J, .2, peak_speed=.9)
    assert_allclose(r["charge_inventory"]*r["speed"], J)
    assert_allclose(r["energy"]**2*(1-r["speed"]**2), (.2*r["charge_inventory"][None])**2*np.ones_like(J))
    assert r["energy"][-1, 0] > 0
    assert np.max(r["speed"]) < 1


def test_all_speed_bound_applies_to_arbitrary_particle_velocity_mixtures():
    rng = np.random.default_rng(425)
    for _ in range(100):
        v, mass = rng.uniform(0, .999, (2, 12))
        E = mass/np.sqrt(1-v*v)
        P, Q, chiJ = np.sum(E*v*v), np.sum(E*(1-v*v)), np.sum(mass*v)
        assert P*Q >= chiJ**2-1e-12
    # A synthetic strict rejection: the available Q is tiny even though
    # the available total energy is comparatively large.
    H, Ho = .05, .045
    F = np.array([.02-2*H, -2., -6.7-H/2])
    bound = necessary_host_bound(F, H-Ho, Ho, 1., 1., eta=1.01)
    assert bound["rejected"]
    for B in np.linspace(0, bound["field_cap"], 500):
        for v in (.2, .7, .98, .999, .99999):
            E = np.sqrt(B)/(v*np.sqrt(1-v*v))
            P = E*v*v
            a = bound["a"]-annular_factor(1.01)*B+E-P
            c = F[2]+H/2+(3-annular_factor(1.01))*B+E+2*P
            W = np.clip((c-a)/3, 0, H-2*annular_factor(1.01)*B)
            assert max(a+W, c-2*W) > 0


def direct_history_lp(F, hi, ho, lr, lt, eta):
    """Independent formulation keeps every field energy as an LP variable."""
    n, R = len(hi), annular_factor(eta)
    rows, rhs = [], []
    for t in range(n):
        material = np.zeros((5, n+6))
        for k, scale in enumerate((lr[t]*lt[t], lt[t], lr[t]*lt[t], lt[t], lt[t]**2)):
            material[k, k] = scale
        wi, ki, wo, ko, A = material
        b = np.zeros(n+6); b[5+t] = 1
        deficit = np.zeros(n+6); deficit[-1] = 1
        W, K, H = wi+wo, ki+ko, hi[t]+ho[t]
        rows.extend([wi, -wi-ki, wo+2*R*b, -wo-ko-2*R*b, R*b-A,
                     3*W+2*K+3*A-deficit, 3*W+2*K+3*A-deficit,
                     2*K+3*A+3*b-deficit])
        rhs.extend([hi[t], -hi[t], ho[t], -ho[t], 0.,
                    -F[0, t], -F[1, t]+1.5*H, -F[2, t]+1.5*H])
    objective = np.zeros(n+6); objective[-1] = 1
    return linprog(objective, A_ub=rows, b_ub=rhs,
                   bounds=[(0, None)]*(n+5)+[(None, None)], method="highs")


@pytest.mark.parametrize("eta", [1.01, 1.2])
def test_material_history_matches_uneliminated_lp_and_dual(eta):
    rng = np.random.default_rng(932)
    lr, lt = np.linspace(1, .6, 15), np.linspace(1, 1.1, 15)
    for _ in range(4):
        hi, ho = rng.uniform(.01, .1, (2, 15))
        F = rng.uniform(-1, .3, (3, 15))
        result = controlled_material_history(F, hi, ho, lr, lt, eta=eta)
        independent = direct_history_lp(F, hi, ho, lr, lt, eta)
        assert independent.success
        assert_allclose(result["shortfall"], independent.fun, atol=1e-9)
        assert_allclose(result["shortfall"], result["dual_lower_bound"], atol=1e-9)
        assert result["dual_stationarity_error"] < 1e-9
        assert result["maximum_primal_violation"] < 1e-9
        E = result["energy"]
        assert E.min() > -1e-9
        assert_allclose((EVOLUTION_BASIS @ E)[2], -hi-ho, atol=1e-9)


def test_passive_populations_obey_work_law_and_bus_is_reciprocal():
    t = np.linspace(0, 1, 1001)[:, None]
    lr, lt = np.exp(-.3*t), np.exp(.1*t)
    E = np.stack([lr*lt, lt, lr*lt, lt, lt*lt])
    P = E*EVOLUTION_BASIS[1, :5, None, None]
    T = E*EVOLUTION_BASIS[2, :5, None, None]
    Q = required_exchange(E, P, T, lr, lt)
    assert np.max(np.abs(Q)) < 2e-12
    exchanges = np.array([[.2], [-.1], [.3]])
    bus = reservoir_interval(exchanges, np.ones((4, 1)))
    assert bus["capacity_gap"] < 0
    assert_allclose(np.diff(bus["store_energy"], axis=0)+exchanges, 0., atol=1e-16)
    assert reservoir_interval(exchanges, np.full((4, 1), .1))["capacity_gap"] > 0


def test_invalid_field_and_superluminal_inventory_are_rejected():
    with pytest.raises(ValueError):
        annular_factor(1.)
    with pytest.raises(ValueError):
        particle_inventory(np.ones((2, 1)), 1., peak_speed=1.)
    with pytest.raises(ValueError):
        allocate_field(np.ones(3), 0., 0., .1, 1.)
