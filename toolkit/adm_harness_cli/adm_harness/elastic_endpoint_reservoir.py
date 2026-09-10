"""Longitudinal thermoelastic storage on the scheduled spherical rail metric.

Each radial material line has an inverse stretch n and stored thermal energy q.
The finite body has counted end tractions. The endpoint's archived divergence
supplies the opposite volume exchange; this is a forced constitutive response,
with endpoint feedback and end-anchor construction left for a subsequent rung.
"""
from __future__ import annotations

from dataclasses import dataclass
import time

import numpy as np

from .active_transfer_reservoir import divergence_projections


class ElasticDomainError(ValueError):
    pass


@dataclass(frozen=True)
class ElasticLaw:
    stiffness: float = .1
    mass: float = 1.
    scale: float = .1

    def __post_init__(self):
        if not 0 < self.stiffness < self.mass or self.scale <= 0:
            raise ValueError('positive density scale and 0<stiffness<mass required')

    def rest(self, density, thermal):
        n, q = np.asarray(density), np.asarray(thermal)
        energy = n*(self.mass+q)+.5*self.stiffness*(n-1)**2
        pressure = .5*self.stiffness*(n*n-1)
        sound2 = self.stiffness*n/(self.mass+q+self.stiffness*(n-1))
        return energy, pressure, sound2


def encode(n, velocity, thermal, b, law):
    n, v, q, b = np.broadcast_arrays(n, velocity, thermal, b)
    gamma = 1/np.sqrt(1-v*v)
    energy, pressure, _ = law.rest(n, q)
    e = (energy+pressure)*gamma**2-pressure
    j = (energy+pressure)*gamma**2*v
    return np.array([b*n*gamma, law.scale*b*e, law.scale*b*b*j])


def recover(state, b, law, *, check_thermal=True):
    d = state[0]/b
    e, j = state[1]/(law.scale*b), state[2]/(law.scale*b*b)
    if np.any(d <= 0) or np.any(e-abs(j) <= .5*law.stiffness) or not np.isfinite(state).all():
        raise ElasticDomainError('material left its positive timelike recovery domain')
    lo, hi = np.full_like(d, -1.), np.ones_like(d)
    for _ in range(43):
        v = .5*(lo+hi)
        pressure = .5*law.stiffness*(d*d*(1-v*v)-1)
        residual = (e+pressure)*v-j
        hi = np.where(residual > 0, v, hi)
        lo = np.where(residual <= 0, v, lo)
    v = .5*(lo+hi)
    n = d*np.sqrt(1-v*v)
    rest = e-v*j
    thermal = (rest-.5*law.stiffness*(n-1)**2)/n-law.mass
    energy, pressure, sound2 = law.rest(n, thermal)
    if check_thermal and np.min(thermal) <= 0:
        raise ElasticDomainError('stored thermal energy reached zero')
    if np.any(sound2 <= 0) or np.any(sound2 >= 1):
        raise ElasticDomainError('longitudinal characteristics left the causal domain')
    return dict(n=n, velocity=v, thermal=thermal, rest=energy, pressure=pressure,
                sound2=sound2, energy=e, current=j, radial=pressure+v*j)


def flux(state, g, law, fields=None):
    f = recover(state, g.b, law) if fields is None else fields
    return np.array([
        state[0]*(-g.beta+g.alpha*f['velocity']/g.b),
        law.scale*g.alpha*f['current']-g.beta*state[1],
        law.scale*g.alpha*g.b*f['radial']-g.beta*state[2],
    ])


def geometric_source(fields, g, law):
    e, j, p = fields['energy'], fields['current'], fields['radial']
    return np.array([
        np.zeros_like(e),
        law.scale*(g.alpha*g.b*g.k_l*p-g.alpha_x*j),
        law.scale*g.b*(-e*g.alpha_x+g.b*j*g.beta_x+g.alpha*p*g.logb_x),
    ])


def exchange_source(power, force, g):
    # P,F are the endpoint divergence in the ADM frame. Rod receives -P,-F.
    return np.array([np.zeros_like(power), -g.alpha*g.volume*power,
                     -g.alpha*g.b*g.volume*force])


def minmod(a, b, c):
    same = (np.sign(a) == np.sign(b)) & (np.sign(b) == np.sign(c))
    return np.where(same, np.sign(a)*np.minimum(np.minimum(abs(a), abs(b)), abs(c)), 0.)


class ElasticPatch:
    def __init__(self, model, law, cells=128, edges=(-2.1, -.5), forcing=1.):
        self.model, self.law, self.forcing = model, law, float(forcing)
        self.faces = np.linspace(*edges, cells+1)
        self.x = .5*(self.faces[:-1]+self.faces[1:])
        self.dx = float(self.faces[1]-self.faces[0])

    def initial(self, t=0., inverse_stretch=.75, thermal=.25):
        g = self.model.metric(t, self.x)
        velocity = g.b*g.beta/g.alpha  # zero coordinate velocity initially
        if np.max(abs(velocity)) >= 1:
            raise ElasticDomainError('coordinate-fixed initial body is not timelike')
        return encode(np.full_like(self.x, inverse_stretch), velocity,
                      np.full_like(self.x, thermal), g.b, self.law)

    def rhs(self, t, state):
        g = self.model.metric(t, self.x)
        faces = self.model.metric(t, self.faces)
        f = recover(state, g.b, self.law)
        variables = np.array([np.log(f['n']), np.arctanh(f['velocity']), np.log(f['thermal'])])
        slopes = np.zeros_like(variables)
        slopes[:, 1:-1] = minmod(1.5*(variables[:, 1:-1]-variables[:, :-2]),
                                  .5*(variables[:, 2:]-variables[:, :-2]),
                                  1.5*(variables[:, 2:]-variables[:, 1:-1]))
        left = np.column_stack([variables[:, 0], variables+.5*slopes])
        right = np.column_stack([variables-.5*slopes, variables[:, -1]])
        wall_v = faces.b*faces.beta/faces.alpha
        if max(abs(wall_v[0]), abs(wall_v[-1])) >= 1:
            raise ElasticDomainError('an end worldtube became spacelike')
        left[1, 0] = 2*np.arctanh(wall_v[0])-right[1, 0]
        right[1, -1] = 2*np.arctanh(wall_v[-1])-left[1, -1]
        states, fields, physical_fluxes, speeds = [], [], [], []
        for values in (left, right):
            n, v, q = np.exp(values[0]), np.tanh(values[1]), np.exp(values[2])
            u = encode(n, v, q, faces.b, self.law)
            ff = recover(u, faces.b, self.law)
            sound = np.sqrt(ff['sound2'])
            plus = -faces.beta+faces.alpha/faces.b*(v+sound)/(1+v*sound)
            minus = -faces.beta+faces.alpha/faces.b*(v-sound)/(1-v*sound)
            speeds.append(np.maximum(abs(plus), abs(minus)))
            states.append(u); fields.append(ff); physical_fluxes.append(flux(u, faces, self.law, ff))
        speed = np.maximum(*speeds)
        face_flux = .5*(physical_fluxes[0]+physical_fluxes[1])-.5*speed*(states[1]-states[0])
        # A closed, coordinate-fixed end carries traction and ADM energy flux,
        # with zero particle transfer. Record both; anchors are external here.
        for i in (0, -1):
            face_flux[0, i] = 0.
            face_flux[1, i] = faces.beta[i]/faces.alpha[i]*face_flux[2, i]
        power, force = divergence_projections(g, *self.model.medium(t, self.x))
        exchange = self.forcing*exchange_source(power, force, g)
        geometric = geometric_source(f, g, self.law)
        rate = -np.diff(face_flux, axis=1)/self.dx+geometric+exchange
        return rate, f, dict(boundary=face_flux[:, 0]-face_flux[:, -1],
                            geometry=self.dx*geometric.sum(axis=1),
                            exchange=self.dx*exchange.sum(axis=1),
                            max_speed=float(speed.max()),
                            end_traction=face_flux[2, [0, -1]]/(faces.alpha[[0, -1]]*faces.b[[0, -1]]))


def evolve(patch, *, duration=3., cfl=.25, snapshots=61, deadline_seconds=180., max_steps=30000):
    state = patch.initial()
    t, steps = 0., 0
    targets = np.linspace(0., duration, snapshots)
    initial_integral = patch.dx*state.sum(axis=1)
    ledger = {key: np.zeros(3) for key in ('boundary', 'geometry', 'exchange')}
    records, stored, times = [], [], []
    started = time.monotonic()
    status, failure = 'duration_completed', ''
    for target in targets:
        while t < target-1e-13:
            if time.monotonic()-started >= deadline_seconds or steps >= max_steps:
                status = 'compute_budget_reached'; break
            try:
                rate, f, diag = patch.rhs(t, state)
            except ElasticDomainError as error:
                status, failure = 'constitutive_domain_limit', str(error); break
            dt = min(cfl*patch.dx/max(diag['max_speed'], 1e-15), target-t, .005)
            accepted = False
            for _ in range(16):
                try:
                    stage = state+dt*rate
                    second, _, other = patch.rhs(t+dt, stage)
                    candidate = .5*(state+stage+dt*second)
                    recover(candidate, patch.model.metric(t+dt, patch.x).b, patch.law)
                    accepted = True; break
                except ElasticDomainError as error:
                    failure = str(error); dt *= .5
            if not accepted or dt < 1e-9:
                status = 'constitutive_domain_limit'; break
            for key in ledger:
                ledger[key] += .5*dt*(diag[key]+other[key])
            state, t, steps = candidate, t+dt, steps+1
        g = patch.model.metric(t, patch.x)
        f = recover(state, g.b, patch.law)
        integral = patch.dx*state.sum(axis=1)
        residual = integral-initial_integral-sum(ledger.values())
        rho = patch.law.scale*f['energy']/g.radius**2
        radial = patch.law.scale*f['radial']/g.radius**2
        row = dict(s=t, steps=steps, minimum_thermal=float(f['thermal'].min()),
                   minimum_inverse_stretch=float(f['n'].min()), maximum_inverse_stretch=float(f['n'].max()),
                   maximum_abs_velocity=float(abs(f['velocity']).max()),
                   minimum_sound2=float(f['sound2'].min()), maximum_sound2=float(f['sound2'].max()),
                   maximum_density=float(rho.max()), maximum_abs_radial_stress=float(abs(radial).max()),
                   proper_energy=float(4*np.pi*integral[1]),
                   thermal_inventory=float(4*np.pi*patch.law.scale*patch.dx*np.sum(state[0]*f['thermal'])),
                   minimum_packet_distance=float(np.min(abs(patch.x-t))-.35))
        for i, name in enumerate(('material', 'energy', 'momentum')):
            row[f'{name}_balance_residual'] = float(residual[i])
            for key in ledger:
                row[f'{name}_{key}_integral'] = float(ledger[key][i])
        records.append(row); stored.append(state.copy()); times.append(t)
        if status != 'duration_completed':
            break
    return dict(status=status, failure=failure if status != 'duration_completed' else '',
                final_time=t, elapsed_seconds=time.monotonic()-started, steps=steps,
                history=records, states=np.array(stored), times=np.array(times))
