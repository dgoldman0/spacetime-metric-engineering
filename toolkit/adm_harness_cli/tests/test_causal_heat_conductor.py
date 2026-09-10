import numpy as np

from adm_harness.causal_heat_conductor import (
    HeatConductorLaw, HeatConductor, thermal_conserved, thermal_primitive,
    thermal_speeds, evolve_heat_conductor,
)


class FlatBackground:
    scale = .4

    def __init__(self, cells=129, amplitude=.1, duration=.2, tolman=False, velocity=0.):
        self.cells, self.amplitude, self.end_time, self.tolman = cells, amplitude, duration, tolman
        self.velocity = velocity
        self.faces = np.linspace(0., 1., cells+1)
        self.a = .5*(self.faces[:-1]+self.faces[1:])
        self.da = 1/cells

    def sample(self, t):
        one, zero = np.ones(self.cells), np.zeros(self.cells)
        alpha = np.exp(.2*self.a) if self.tolman else one
        aface = np.exp(.2*self.faces) if self.tolman else np.ones(self.cells+1)
        gamma = 1/np.sqrt(1-self.velocity**2)
        temperature = 1/alpha if self.tolman else 1+self.amplitude*np.cos(2*np.pi*self.a)
        center = dict(x=self.a/gamma+self.velocity*t, v=one*self.velocity, vt=zero, gamma=one*gamma, n=one, h=alpha/gamma,
                       proper_rate=alpha/gamma, acceleration_rate=.2*alpha if self.tolman else zero,
                       expansion=zero, alpha=alpha, beta=zero, b=one, radius=2*one,
                       alpha_t=zero, beta_t=zero, logb_t=zero, qbase=temperature,
                       source=zero, h_a=np.diff(aface)/self.da/gamma)
        return center, dict(v=np.full(self.cells+1, self.velocity), h=aface/gamma)

    def rest(self, q, r, bg):
        ratio = 2*abs(q*r)/(1+q)
        assert np.max(ratio) < 1
        return dict(energy=1+q, pressure=np.zeros_like(q), maximum_flux_enthalpy_ratio=float(ratio.max()))


def test_heat_state_inversion_survives_large_material_boosts():
    law = HeatConductorLaw(speed=.5)
    q = np.geomspace(.01, 100, 101)
    r = .2*np.sin(np.linspace(0, 6, 101))
    v = np.linspace(-.999, .999, 101)
    recovered = thermal_primitive(thermal_conserved(q, r, v, law), v, law)
    np.testing.assert_allclose(recovered[0], q, rtol=1e-10)
    np.testing.assert_allclose(recovered[1], r, atol=1e-10)


def test_heat_characteristics_transform_from_the_material_frame():
    law, r, v, h = HeatConductorLaw(speed=.3), np.array([.2]), np.array([-.95]), np.array([.7])
    rates, relative = thermal_speeds(r, v, h, law)
    np.testing.assert_allclose(relative**2-r*relative-law.speed**2, 0., atol=1e-15)
    np.testing.assert_allclose(rates, h*relative/(1+v*relative))
    assert np.max(abs(relative)) < 1


def test_heat_inversion_resolves_states_close_to_the_causal_boundary():
    for speed in (.3, 1/np.sqrt(3)):
        law = HeatConductorLaw(speed=speed)
        q = np.geomspace(1e-6, 100., 101)
        r = np.full_like(q, (1-speed**2)*(1-2e-8))
        v = np.full_like(q, -.99999)
        recovered = thermal_primitive(thermal_conserved(q, r, v, law), v, law)
        np.testing.assert_allclose(recovered[0], q, rtol=2e-7)
        np.testing.assert_allclose(recovered[1], r, atol=2e-8)


def test_entropy_identity_includes_flux_inertia_and_active_coefficients():
    law = HeatConductorLaw(speed=.3, proper_time=1.7)
    q, r, v = np.array([1.7]), np.array([.08]), np.array([-.7])
    h, ha, vt, c, proper, source, wa, ra = .6, -.2, .1, .3, .9, -.03, .4, -.1
    c2, w = law.speed**2, np.log(q)
    rate = np.array([-ha*q*r-h*q*(wa*r+ra)+source-c*q*r,
                      -c2*(ha*w+h*wa)-proper*r/law.proper_time-c2*c+c2*(vt+ha)*w])
    initial = thermal_conserved(q, r, v, law)
    step = 1e-6
    def entropy(state, velocity):
        temperature, flux = thermal_primitive(state, velocity, law)
        return np.log(temperature)-flux**2/(2*c2)+velocity*flux
    derivative = (entropy(initial+step*rate, v+step*vt)-entropy(initial-step*rate, v-step*vt))/(2*step)
    expected = source/q+proper*r*r/(law.proper_time*c2)
    np.testing.assert_allclose(derivative+ha*r+h*ra, expected, rtol=1e-7, atol=1e-9)


def test_closed_conductor_preserves_energy_and_produces_entropy():
    conductor = HeatConductor(FlatBackground(), HeatConductorLaw(speed=.3))
    result = evolve_heat_conductor(conductor, max_step=.001, snapshots=5)
    assert result['status'] == 'duration_completed'
    row = result['history'][-1]
    assert abs(row['tilted_heat_balance']) < 1e-11
    assert row['entropy_production_integral'] > 0
    assert row['entropy_inventory'] > result['history'][0]['entropy_inventory']
    assert row['entropy_excess'] > -1e-8


def test_resolved_heat_wave_matches_the_linear_telegraph_limit():
    amplitude, duration, speed, tau = 1e-4, .2, .3, 1.
    background = FlatBackground(amplitude=amplitude, duration=duration)
    conductor = HeatConductor(background, HeatConductorLaw(speed=speed, proper_time=tau))
    result = evolve_heat_conductor(conductor, max_step=.001, snapshots=3)
    bg, _ = background.sample(duration)
    q, _ = thermal_primitive(result['states'][-1], bg['v'], conductor.law)
    measured = 2*np.mean((q-1)*np.cos(2*np.pi*background.a))
    omega = np.sqrt((2*np.pi*speed)**2-1/(4*tau*tau))
    expected = amplitude*np.exp(-duration/(2*tau))*(np.cos(omega*duration)+np.sin(omega*duration)/(2*tau*omega))
    np.testing.assert_allclose(measured, expected, rtol=.002)


def test_static_tolman_profile_has_converging_heat_flux_including_insulated_ends():
    errors = []
    for cells in (65, 129):
        background = FlatBackground(cells=cells, duration=.05, tolman=True)
        conductor = HeatConductor(background, HeatConductorLaw(speed=.3))
        result = evolve_heat_conductor(conductor, max_step=.001, snapshots=3)
        bg, _ = background.sample(.05)
        _, r = thermal_primitive(result['states'][-1], bg['v'], conductor.law)
        errors.append(np.max(abs(r)))
    assert errors[1] < .35*errors[0]
    assert errors[1] < 1e-7


def test_moving_conductor_counts_the_force_work_needed_to_hold_its_motion():
    conductor = HeatConductor(FlatBackground(velocity=-.7), HeatConductorLaw(speed=.3))
    result = evolve_heat_conductor(conductor, max_step=.0005, snapshots=5)
    assert result['status'] == 'duration_completed'
    row = result['history'][-1]
    assert abs(row['tilted_heat_balance']) < 1e-11
    assert row['holding_positive_work_integral'] > 0
    assert abs(row['canonical_balance_residual']) < 1e-8
