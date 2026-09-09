"""Gaussian quantum scalar field coupled to a material separation coordinate.

Planar geometry; real normal Fourier modes, transverse radial quadrature,
and two finite Gaussian potentials. The field inside and outside the gap
is retained. Bare mechanical inertia is positive; the proper-time scalar
coupling adds field-dependent inertia. The finite regulator and
semiclassical wall motion are explicit.
"""
from __future__ import annotations

from dataclasses import dataclass
import time

import numpy as np
from numpy.polynomial.legendre import leggauss


@dataclass
class PlanarField:
    harmonics: int
    transverse_nodes: int
    cutoff: float = 8.
    length: float = 12.
    width: float = .16
    strength: float = 8.

    def __post_init__(self):
        if min(self.harmonics, self.transverse_nodes, self.cutoff, self.length, self.width) <= 0 or self.strength < 0:
            raise ValueError('positive field discretization and nonnegative wall strength required')
        m = np.arange(-self.harmonics, self.harmonics+1)
        self.wave = 2*np.pi*m/self.length
        self.size = len(m)
        transform = np.zeros((self.size, self.size), complex)
        transform[self.harmonics, 0] = 1.
        for j in range(1, self.harmonics+1):
            transform[self.harmonics+j, 2*j-1] = 1/np.sqrt(2)
            transform[self.harmonics-j, 2*j-1] = 1/np.sqrt(2)
            transform[self.harmonics+j, 2*j] = -1j/np.sqrt(2)
            transform[self.harmonics-j, 2*j] = 1j/np.sqrt(2)
        self.transform = transform
        self.difference = self.wave[None, :]-self.wave[:, None]
        self.envelope = self.strength/self.length*np.exp(-.5*self.width**2*self.difference**2)
        self.free = np.real(transform.conj().T@np.diag(self.wave**2)@transform)
        x, w = leggauss(self.transverse_nodes)
        self.transverse = .5*self.cutoff*(x+1)
        self.weights = .5*self.cutoff*w*self.transverse/(2*np.pi)
        self.free_energy = self.ground_energy(self.free)
        self.single_energy = self.ground_energy(self.free+self.wall(0.))

    def wall(self, position, derivative=0):
        complex_matrix = self.envelope*np.exp(1j*self.difference*position)*(1j*self.difference)**derivative
        matrix = np.real(self.transform.conj().T@complex_matrix@self.transform)
        return .5*(matrix+matrix.T)

    def operator(self, separation, derivative=0):
        if derivative == 0:
            return self.free+self.wall(-separation/2)+self.wall(separation/2)
        return (-.5)**derivative*self.wall(-separation/2, derivative)+.5**derivative*self.wall(separation/2, derivative)

    def spectrum(self, operator):
        values, vectors = np.linalg.eigh(operator)
        omega2 = values[None, :]+self.transverse[:, None]**2
        if omega2.min() <= 0:
            raise ValueError('nonpositive quantum field frequency')
        return np.sqrt(omega2), vectors

    def ground_energy(self, operator):
        omega, _ = self.spectrum(operator)
        return float(.5*self.weights@omega.sum(axis=1))

    def ground_state(self, separation):
        return self.operator_ground_state(self.operator(separation))

    def operator_ground_state(self, operator):
        omega, vectors = self.spectrum(operator)
        f = vectors[None, :, :]/np.sqrt(2*omega[:, None, :])
        p = -1j*vectors[None, :, :]*np.sqrt(omega[:, None, :]/2)
        return f.astype(complex), p

    def ground_force(self, separation):
        f, _ = self.ground_state(separation)
        return -self.expectation(f, self.operator(separation, 1))/2

    def interaction_energy(self, separation):
        return self.ground_energy(self.operator(separation))-2*self.single_energy+self.free_energy

    def expectation(self, f, matrix):
        return float(self.weights@np.einsum('kij,kij->k', f.conj(), matrix@f).real)

    def field_energy(self, f, p, separation):
        kinetic = np.sum(abs(p)**2, axis=(1, 2))
        mass_term = self.transverse**2*np.sum(abs(f)**2, axis=(1, 2))
        return .5*(float(self.weights@(kinetic+mass_term))+self.expectation(f, self.operator(separation)))

    def interaction_expectation(self, f, separation):
        return self.expectation(f, self.operator(separation)-self.free)/2

    def advance_field(self, f, p, operator, step):
        # Exact quantum evolution for the step's averaged spatial operator.
        omega, vectors = self.spectrum(operator)
        fq, pq = vectors.T@f, vectors.T@p
        cosine, sine = np.cos(omega*step)[:, :, None], np.sin(omega*step)[:, :, None]
        return (vectors@(cosine*fq+sine/omega[:, :, None]*pq),
                vectors@(-omega[:, :, None]*sine*fq+cosine*pq))

    def mode_normalization_error(self, f, p):
        dagger_f, dagger_p = np.swapaxes(f.conj(), -1, -2), np.swapaxes(p.conj(), -1, -2)
        first = dagger_f@p-dagger_p@f+1j*np.eye(self.size)
        second = np.swapaxes(f, -1, -2)@p-np.swapaxes(p, -1, -2)@f
        return float(max(abs(first).max(), abs(second).max()))

    def spatial_profile(self, f, p, separation, points=257, coupling_factor=1.):
        z = np.linspace(-self.length/2, self.length/2, points)
        exponential = np.exp(1j*z[:, None]*self.wave[None, :])/np.sqrt(self.length)
        basis = np.real(exponential@self.transform)
        derivative = np.real((exponential*(1j*self.wave[None, :]))@self.transform)
        qz, pz, dz = basis@f, basis@p, derivative@f
        q = np.einsum('k,kzi,kzi->z', self.weights, qz.conj(), qz).real
        a = np.einsum('k,kzi,kzi->z', self.weights, pz.conj(), pz).real
        b = np.einsum('k,kzi,kzi->z', self.weights, dz.conj(), dz).real
        c = np.einsum('k,kzi,kzi->z', self.weights*self.transverse**2, qz.conj(), qz).real
        current = -np.einsum('k,kzi,kzi->z', self.weights, pz.conj(), dz).real
        # Periodized Gaussian, consistent with the Fourier matrix elements.
        potential = coupling_factor*sum(
            self.strength/(np.sqrt(2*np.pi)*self.width)
            *np.exp(-.5*((z-sign*separation/2-image*self.length)/self.width)**2)
            for sign in [-1, 1] for image in [-1, 0, 1])
        channels = np.stack([.5*(a+b+c+potential*q), current,
                             .5*(a+b-c-potential*q), .5*(a-b-potential*q)], axis=-1)
        return z, channels, q


@dataclass
class WallMechanics:
    wall_mass: float
    stiffness: float
    natural: float
    holding_mass: float

    @property
    def inertia(self):
        return self.wall_mass/2+self.holding_mass/12

    @property
    def moving_rest_mass(self):
        return 4*self.inertia

    def potential(self, separation):
        return .5*self.stiffness*(separation-self.natural)**2

    def boundary_energy(self, separation, momentum, interaction):
        return np.sqrt((self.moving_rest_mass+interaction)**2+4*momentum**2)

    def velocity(self, separation, momentum, interaction):
        return 4*momentum/self.boundary_energy(separation, momentum, interaction)

    def energy(self, separation, momentum, interaction):
        return (self.boundary_energy(separation, momentum, interaction)-interaction
                +self.potential(separation)+2*self.holding_mass/3)


def prepare_mechanics(field, wall_mass, stiffness):
    if wall_mass <= 0 or stiffness < 0:
        raise ValueError('positive wall inertia and nonnegative stiffness required')
    natural = 1.-field.ground_force(1.)/stiffness if stiffness else 1.
    holding_mass = 4*stiffness*1.2**2
    return WallMechanics(wall_mass, stiffness, natural, holding_mass)


def coupled_step(field, mechanics, f, p, separation, momentum, step):
    """Implicit energy-conserving discrete gradient with exact field substeps.

    The proper-time wall coupling places its positive interaction energy
    in the moving boundary's inertia. A common discrete gradient of the
    square-root boundary Hamiltonian evolves its momentum and the Gaussian
    field, preserving their summed energy.
    """
    old_potential = field.operator(separation)-field.free
    old_interaction = field.expectation(f, old_potential)/2
    old_mass = mechanics.moving_rest_mass+old_interaction
    old_boundary = np.sqrt(old_mass**2+4*momentum**2)
    chi = old_mass/old_boundary
    guess = separation+step*4*momentum/old_boundary
    guess_momentum = momentum
    for iteration in range(20):
        new_potential = field.operator(guess)-field.free
        fn, pn = field.advance_field(f, p, field.free+.5*chi*(old_potential+new_potential), step)
        new_interaction = field.expectation(fn, new_potential)/2
        new_mass = mechanics.moving_rest_mass+new_interaction
        new_boundary = np.sqrt(new_mass**2+4*guess_momentum**2)
        next_chi = (old_mass+new_mass)/(old_boundary+new_boundary)
        change = guess-separation
        derivative = ((new_potential-old_potential)/change if abs(change) > 1e-7
                      else field.operator(.5*(guess+separation), 1))
        force = -.25*next_chi*(field.expectation(f, derivative)+field.expectation(fn, derivative))
        spring_force = -mechanics.stiffness*(.5*(guess+separation)-mechanics.natural)
        next_momentum = momentum+step*(force+spring_force)
        next_separation = separation+step*4*(momentum+guess_momentum)/(old_boundary+new_boundary)
        if max(abs(next_separation-guess), abs(next_momentum-guess_momentum), abs(next_chi-chi)) < 2e-13:
            return fn, pn, next_separation, next_momentum, iteration+1
        guess, guess_momentum, chi = next_separation, next_momentum, next_chi
    raise RuntimeError('coupled discrete-gradient step did not converge')


def evolve(field, mechanics, velocity, duration=3., step=.005, snapshots=61, deadline=np.inf):
    if abs(velocity)/2 > .10 or duration < 0 or step <= 0 or snapshots < 2:
        raise ValueError('bounded wall speed, nonnegative duration, positive step and at least two snapshots required')
    f, p = field.ground_state(1.)
    separation, t = 1., 0.
    initial_interaction = field.interaction_expectation(f, separation)
    momentum = (mechanics.moving_rest_mass+initial_interaction)*velocity/(4*np.sqrt(1-velocity**2/4))
    initial_field = field.field_energy(f, p, separation)
    initial_mechanical = mechanics.energy(separation, momentum, initial_interaction)
    histories, profiles = [], []
    max_iterations, status = 0, 'duration_completed'
    free_f, free_p = field.operator_ground_state(field.free)
    z, free_profile, _ = field.spatial_profile(free_f, free_p, 1., coupling_factor=0.)
    for index, target in enumerate(np.linspace(0., duration, snapshots)):
        while t < target-1e-12 and status == 'duration_completed':
            if time.monotonic() > deadline:
                status = 'compute_allowance_reached'
                break
            h = min(step, target-t)
            f, p, separation, momentum, iterations = coupled_step(field, mechanics, f, p, separation, momentum, h)
            max_iterations = max(max_iterations, iterations)
            t += h
            if not .65 <= separation <= 1.2:
                status = 'separation_guard'
            elif abs(mechanics.velocity(separation, momentum, field.interaction_expectation(f, separation)))/2 > .10:
                status = 'wall_speed_guard'
        ef = field.field_energy(f, p, separation)
        interaction = field.interaction_expectation(f, separation)
        em = mechanics.energy(separation, momentum, interaction)
        eg = field.ground_energy(field.operator(separation))
        chi = (mechanics.moving_rest_mass+interaction)/mechanics.boundary_energy(separation, momentum, interaction)
        dynamic_operator = field.free+chi*(field.operator(separation)-field.free)
        dynamic_energy = ef+(chi-1)*interaction
        dynamic_ground = field.ground_energy(dynamic_operator)
        ground_f, _ = field.operator_ground_state(dynamic_operator)
        force = -chi*field.expectation(f, field.operator(separation, 1))/2
        adiabat = -chi*field.expectation(ground_f, field.operator(separation, 1))/2
        histories.append({'time': t, 'separation': separation,
            'separation_momentum': momentum, 'coupling_factor': chi,
            'separation_velocity': mechanics.velocity(separation, momentum, interaction),
            'interaction_inertia': interaction/4, 'total_rest_separation_inertia': mechanics.inertia+interaction/4,
            'field_energy_change': ef-initial_field, 'mechanical_energy_change': em-initial_mechanical,
            'energy_balance_error': (ef-initial_field)+(em-initial_mechanical),
            'excitation_above_instantaneous_ground': dynamic_energy-dynamic_ground,
            'vacuum_interaction_energy': eg-2*field.single_energy+field.free_energy,
            'free_subtracted_field_energy': ef-field.free_energy,
            'dynamic_field_energy_free_subtracted': dynamic_energy-field.free_energy,
            'complete_regulated_energy': ef-field.free_energy+em,
            'quantum_force': force, 'instantaneous_ground_force': adiabat,
            'nonadiabatic_force': force-adiabat,
            'holding_energy_margin': mechanics.holding_mass+mechanics.potential(separation)
                -abs(mechanics.stiffness*(separation-mechanics.natural))*separation})
        if index in [0, snapshots//4, snapshots//2, 3*snapshots//4, snapshots-1] or status != 'duration_completed':
            z, channels, q = field.spatial_profile(f, p, separation, coupling_factor=chi)
            profiles.append({'time': t, 'separation': separation, 'z': z,
                             'coupling_factor': chi,
                             'free_subtracted_channels': channels-free_profile, 'phi_squared': q})
        if status != 'duration_completed':
            break
    return {'f': f, 'p': p, 'histories': histories, 'profiles': profiles,
            'status': status, 'max_iterations': max_iterations,
            'mode_normalization_error': field.mode_normalization_error(f, p)}
