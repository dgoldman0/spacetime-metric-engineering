"""Physical identities and coupled evolution for the finite quantum-wall model."""
import numpy as np
import pytest

from adm_harness.quantum_boundary import PlanarField, prepare_mechanics, evolve


def test_positive_wall_and_translation_invariant_one_body_energy():
    field = PlanarField(8, 6)
    assert np.linalg.eigvalsh(field.wall(.23)).min() > -1e-13
    shifted = field.ground_energy(field.free+field.wall(.71))
    assert abs(shifted-field.single_energy) < 2e-12
    assert field.spectrum(field.operator(1.))[0].min() > 0


def test_casimir_force_is_interaction_energy_derivative():
    field = PlanarField(12, 8)
    h, a = .002, 1.
    derivative = (field.interaction_energy(a-2*h)-8*field.interaction_energy(a-h)
                  +8*field.interaction_energy(a+h)-field.interaction_energy(a+2*h))/(12*h)
    assert abs(field.ground_force(a)+derivative) < 2e-8
    assert field.interaction_energy(a) < 0


def test_full_hamiltonian_generates_wall_velocity_and_force():
    field = PlanarField(8, 6)
    mechanics = prepare_mechanics(field, 1., .5)
    f, p = field.ground_state(1.)
    a, momentum, h = .98, .04, 1e-5

    def hamiltonian(separation, mechanical_momentum):
        interaction = field.interaction_expectation(f, separation)
        return (field.field_energy(f, p, separation)
                +mechanics.energy(separation, mechanical_momentum, interaction))

    interaction = field.interaction_expectation(f, a)
    velocity = mechanics.velocity(a, momentum, interaction)
    chi = (mechanics.moving_rest_mass+interaction)/mechanics.boundary_energy(a, momentum, interaction)
    force = -chi*field.expectation(f, field.operator(a, 1))/2-mechanics.stiffness*(a-mechanics.natural)
    numerical_velocity = (hamiltonian(a, momentum+h)-hamiltonian(a, momentum-h))/(2*h)
    numerical_force = -(hamiltonian(a+h, momentum)-hamiltonian(a-h, momentum))/(2*h)
    assert abs(velocity-numerical_velocity) < 5e-9
    assert abs(force-numerical_force) < 5e-9


@pytest.mark.parametrize('velocity', [0., .02])
def test_coupled_energy_and_quantum_commutators(velocity):
    field = PlanarField(8, 6)
    mechanics = prepare_mechanics(field, 1., .5)
    result = evolve(field, mechanics, velocity, duration=.3, step=.01, snapshots=7)
    assert result['status'] == 'duration_completed'
    assert result['mode_normalization_error'] < 2e-12
    assert max(abs(row['energy_balance_error']) for row in result['histories']) < 2e-10
    assert min(row['excitation_above_instantaneous_ground'] for row in result['histories']) > -2e-10
    assert min(row['total_rest_separation_inertia'] for row in result['histories']) > 0
    if velocity == 0:
        assert max(abs(row['separation']-1) for row in result['histories']) < 1e-12
        assert abs(result['histories'][-1]['field_energy_change']) < 2e-10
    else:
        assert result['histories'][-1]['excitation_above_instantaneous_ground'] > 1e-7


def test_transparent_walls_have_free_motion_and_zero_field_stress():
    field = PlanarField(8, 6, strength=0.)
    mechanics = prepare_mechanics(field, 1., 0.)
    result = evolve(field, mechanics, .02, duration=.3, step=.02, snapshots=4)
    assert abs(result['histories'][-1]['separation']-1.006) < 1e-12
    assert abs(result['histories'][-1]['separation_velocity']-.02) < 1e-12
    assert max(abs(profile['free_subtracted_channels']).max() for profile in result['profiles']) < 2e-11


def test_temporal_refinement_improves_moving_wall_solution():
    field = PlanarField(8, 6)
    mechanics = prepare_mechanics(field, 1., .5)
    finals = []
    for step in [.04, .02, .01]:
        row = evolve(field, mechanics, .02, duration=.4, step=step, snapshots=3)['histories'][-1]
        finals.append(np.array([row['separation'], row['separation_velocity'], row['quantum_force']]))
    coarse, fine = np.linalg.norm(finals[0]-finals[1]), np.linalg.norm(finals[1]-finals[2])
    assert coarse > 2*fine > 0


def test_spatial_energy_integrates_to_dynamic_field_energy():
    field = PlanarField(8, 6)
    f, p = field.ground_state(1.)
    chi = .997
    z, channels, _ = field.spatial_profile(f, p, 1., points=1025, coupling_factor=chi)
    expected = field.field_energy(f, p, 1.)+(chi-1)*field.interaction_expectation(f, 1.)
    assert abs(np.trapezoid(channels[:, 0], x=z)-expected) < 2e-10
