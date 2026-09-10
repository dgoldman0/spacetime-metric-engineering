"""Causal local strain relaxation with counted mechanical-to-thermal transfer.

The extra rest energy is kappa*n*(cosh(log(n)-z)-1). Its internal strain
z relaxes locally toward log(n) in proper time. Heat receives exactly the
released stored energy. The underlying mass and energy remain explicit.
"""
from __future__ import annotations

from dataclasses import dataclass
import time
import numpy as np

from .elastic_endpoint_reservoir import ElasticLaw, ElasticDomainError
from .material_ensemble import MaterialEnsemble, nodal_sum


@dataclass(frozen=True)
class StrainRelaxation:
    stiffness: float = .1
    proper_time: float = 1.
    enabled: bool = True


def relaxing_rest(law, n, q, z, stiffness):
    energy, pressure, _ = law.rest(n, q)
    delta = np.log(n)-z
    energy = energy+stiffness*n*(np.cosh(delta)-1)
    pressure = pressure+stiffness*n*np.sinh(delta)
    modulus = law.stiffness+stiffness*np.exp(-z)
    sound2 = modulus*n/(law.mass+q-law.stiffness-stiffness+modulus*n)
    return energy, pressure, sound2


class RelaxingMaterialEnsemble(MaterialEnsemble):
    def __init__(self, model, law, electrical, relaxation=StrainRelaxation(), **kwargs):
        if not 0 <= relaxation.stiffness < law.mass-law.stiffness or relaxation.proper_time <= 0:
            raise ValueError('0<=relaxation stiffness<mass-elastic stiffness and positive proper time required')
        self.physical_law, self.relaxation = law, relaxation
        # Expansion of the positive relaxation energy contains -kappa*n.
        effective = ElasticLaw(stiffness=law.stiffness, mass=law.mass-relaxation.stiffness, scale=law.scale)
        super().__init__(model, effective, electrical, **kwargs)

    def fields(self, t, state):
        cache = getattr(self, '_rhs_fields', None)
        if cache is not None and cache[0] == t and cache[1] is state:
            return cache[2]
        x, momentum, heat, charge = self.split(state)
        z = state[-(self.cells+1):]
        g, width, volume, a0, b0 = self.coefficients(t, x)
        kappa = self.relaxation.stiffness
        if not np.isfinite(z).all() or np.max(abs(z)) > 100:
            raise ElasticDomainError('internal strain left its finite registered domain')
        added = kappa*np.exp(-z)
        a = a0*(1+added/self.law.stiffness)
        b = b0*(1+kappa*np.exp(z)/self.law.stiffness)
        v = self.velocity(momentum, heat, g, a)
        gamma = 1/np.sqrt(1-v*v)
        c = self.law.mass+heat-self.law.stiffness
        momentum = self.law.scale*g.b*v*(self.mass*c*gamma+2*a)
        stretch = self.reference[None, :]/(width[None, :]*np.array([g.b[:-1]*gamma[:-1], g.b[1:]*gamma[1:]]))
        qcell, zcell = np.array([heat[:-1], heat[1:]]), np.array([z[:-1], z[1:]])
        rest, pressure, sound2 = relaxing_rest(self.physical_law, stretch, qcell, zcell, kappa)
        vv, gg = np.array([v[:-1], v[1:]]), np.array([gamma[:-1], gamma[1:]])
        energy = (rest+pressure)*gg**2-pressure
        current = (rest+pressure)*gg**2*vv
        radial = pressure+vv*current
        def lump(values):
            return .5*(np.r_[width*values[0], 0.]+np.r_[0., width*values[1]])
        energy_int, current_int, radial_int = lump(energy), lump(current), lump(radial)
        matter_adm = self.law.scale*g.b*energy_int
        field_adm = g.b*volume*charge**2/(2*g.radius**2)
        rms_n = np.sqrt(nodal_sum(self.reference**2/width)/volume)/(g.b*gamma)
        return dict(x=x, momentum=momentum, heat=heat, charge=charge, metric=g, width=width,
                    volume=volume, a=a, b=b, velocity=v, gamma=gamma, stretch=stretch,
                    pressure=pressure, sound2=sound2, energy_int=energy_int,
                    current_int=current_int, radial_int=radial_int, matter_adm=matter_adm,
                    field_adm=field_adm, canonical=g.alpha*(matter_adm+field_adm)-g.beta*momentum,
                    effective_n=self.mass/(g.b*gamma*volume), z=z, rms_n=rms_n,
                    minimum_rest_dec_margin=float(np.min(rest-abs(pressure))))

    def initial(self):
        base = super().initial()
        x, _, heat, charge = self.split(base)
        g, width, volume, a0, _ = self.coefficients(0., x)
        velocity = g.b*g.beta/g.alpha
        gamma = 1/np.sqrt(1-velocity**2)
        rms_n = np.sqrt(nodal_sum(self.reference**2/width)/volume)/(g.b*gamma)
        z = np.log(rms_n)
        a = a0*(1+self.relaxation.stiffness*np.exp(-z)/self.law.stiffness)
        momentum = self.law.scale*g.b*velocity*(self.mass*(self.law.mass+heat-self.law.stiffness)*gamma+2*a)
        return np.r_[self.pack(x, momentum, heat, charge), z]

    def rhs(self, t, state):
        f = self.fields(t, state)
        self._rhs_fields = (t, state, f)
        try:
            rate, diag = super().rhs(t, state)
        finally:
            del self._rhs_fields
        g, v, gamma = f['metric'], f['velocity'], f['gamma']
        delta = np.log(f['rms_n'])-f['z']
        frequency = g.alpha/(gamma*self.relaxation.proper_time) if self.relaxation.enabled else np.zeros_like(delta)
        zrate = frequency*delta
        qrelax = frequency*self.relaxation.stiffness*f['rms_n']/f['effective_n']*delta*np.sinh(delta)
        offset = 2*(self.cells-1)
        rate[offset:offset+self.cells+1] += qrelax
        # Correct the constrained-end momentum derivative for the extra
        # elastic modulus and the changing internal strain and heat.
        xrate = -g.beta+g.alpha*v/g.b
        xrate[[0, -1]] = 0.
        added = self.relaxation.stiffness*np.exp(-f['z'])
        extra_adot = -added*nodal_sum(self.reference**2*np.diff(xrate)/f['width']**2)/(2*g.b)
        extra_adot -= f['a']*added/(self.law.stiffness+added)*zrate
        extra_wall = self.law.scale*g.b*v*(self.mass*qrelax*gamma+2*extra_adot)
        diag['anchor_left'] += float(extra_wall[0])
        diag['anchor_right'] += float(extra_wall[-1])
        diag['maximum_anchor_force'] = float(np.max(abs(np.array([diag['anchor_left'], diag['anchor_right']]))
                                                    /(g.alpha[[0, -1]]*g.b[[0, -1]])))
        diag['heat_relaxation'] = float(self.law.scale*np.dot(self.mass, qrelax))
        diag['entropy_relaxation'] = float(self.law.scale*np.dot(self.mass, qrelax/f['heat']))
        diag['maximum_decay'] = max(diag['maximum_decay'], float(np.max(frequency*(1+abs(delta)))))
        return np.r_[rate, zrate], diag


def evolve_relaxing_ensemble(patch, *, duration=.5, snapshots=101, max_step=.0005, cfl=.05,
                            deadline_seconds=360., max_steps=60000):
    state = patch.initial()
    first = patch.fields(0., state)
    h0, p0 = first['canonical'].sum(), first['momentum'].sum()
    q0 = patch.law.scale*np.dot(patch.mass, first['heat'])
    keys = ('canonical_geometry', 'canonical_endpoint', 'heat_endpoint', 'heat_electrical',
            'heat_relaxation', 'entropy_relaxation', 'momentum_free', 'anchor_left', 'anchor_right')
    ledger = {key: 0. for key in keys}
    states, times, history = [], [], []
    t, steps, start = 0., 0, time.monotonic()
    status, failure = 'duration_completed', ''
    for target in np.linspace(0., duration, snapshots):
        while t < target-1e-13:
            if time.monotonic()-start > deadline_seconds or steps >= max_steps:
                status = 'compute_budget_reached'; break
            first_rate, d1 = patch.rhs(t, state)
            dt = min(max_step, target-t, cfl/max(d1['inverse_step'], 1e-15), cfl/max(d1['maximum_decay'], 1e-15))
            accepted = False
            for _ in range(20):
                try:
                    second, d2 = patch.rhs(t+.5*dt, state+.5*dt*first_rate)
                    third, d3 = patch.rhs(t+.5*dt, state+.5*dt*second)
                    fourth, d4 = patch.rhs(t+dt, state+dt*third)
                    candidate = state+dt*(first_rate+2*second+2*third+fourth)/6
                    f = patch.fields(t+dt, candidate)
                    if np.min(f['heat']) < 1e-8:
                        raise ElasticDomainError('material heat reached the registered positive-temperature floor')
                    if np.min(f['width']/patch.initial_cell_width) < 1e-6:
                        raise ElasticDomainError('material compression reached the registered mesh-resolution limit')
                    accepted = True; break
                except ElasticDomainError as error:
                    failure = str(error); dt *= .5
            if not accepted or dt < 1e-10:
                status = 'material_domain_limit'; break
            for key in keys:
                ledger[key] += dt*(d1[key]+2*d2[key]+2*d3[key]+d4[key])/6
            state, t, steps = candidate, t+dt, steps+1
        f = patch.fields(t, state)
        thermal = patch.law.scale*np.dot(patch.mass, f['heat'])
        row = dict(s=t, steps=steps, minimum_heat=float(f['heat'].min()),
                   coldest_l=float(f['x'][np.argmin(f['heat'])]),
                   maximum_abs_velocity=float(abs(f['velocity']).max()), maximum_sound2=float(f['sound2'].max()),
                   minimum_stretch=float(f['stretch'].min()), maximum_stretch=float(f['stretch'].max()),
                   minimum_relative_cell_width=float(np.min(f['width']/patch.initial_cell_width)),
                   minimum_packet_gap=float(np.min(abs(f['x']-t))-.35),
                   minimum_rest_dec_margin=f['minimum_rest_dec_margin'],
                   maximum_relaxation_strain=float(np.max(abs(np.log(f['rms_n'])-f['z']))),
                   canonical_energy=float(4*np.pi*f['canonical'].sum()),
                   slice_energy=float(4*np.pi*np.sum(f['matter_adm']+f['field_adm'])),
                   field_slice_energy=float(4*np.pi*f['field_adm'].sum()), thermal_inventory=float(4*np.pi*thermal),
                   canonical_balance_residual=float(4*np.pi*(f['canonical'].sum()-h0-ledger['canonical_geometry']-ledger['canonical_endpoint'])),
                   momentum_balance_residual=float(f['momentum'].sum()-p0-ledger['momentum_free']-ledger['anchor_left']-ledger['anchor_right']),
                   thermal_balance_residual=float(4*np.pi*(thermal-q0-ledger['heat_endpoint']-ledger['heat_electrical']-ledger['heat_relaxation'])))
        row.update({f'{key}_integral': float(value) for key, value in ledger.items()})
        history.append(row); states.append(state.copy()); times.append(t)
        if status != 'duration_completed':
            break
    return dict(status=status, failure=failure if status != 'duration_completed' else '', final_time=t,
                elapsed_seconds=time.monotonic()-start, steps=steps,
                states=np.array(states), times=np.array(times), history=history)
