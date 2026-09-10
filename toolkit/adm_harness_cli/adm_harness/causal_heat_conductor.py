"""Entropy-current heat conduction on specified active material motion.

The transported state is temperature q and relative heat flux r=J/(n*q).
Mechanical motion is an input to this bounded constitutive replay. The
additional force and its work are measured explicitly, rather than assumed
to be supplied by the archived mechanical solution.
"""
from __future__ import annotations

from dataclasses import dataclass
import time

import numpy as np
from scipy.interpolate import CubicHermiteSpline, CubicSpline

from .elastic_endpoint_reservoir import ElasticDomainError
from .relaxing_material_ensemble import relaxing_rest


@dataclass(frozen=True)
class HeatConductorLaw:
    speed: float = .3
    proper_time: float = 1.

    def __post_init__(self):
        if not 0 <= self.speed < 1 or self.proper_time <= 0:
            raise ValueError('0<=equilibrium heat speed<1 and positive proper relaxation time required')


def thermal_conserved(q, r, v, law):
    return np.array([q*(1+v*r), r+law.speed**2*v*np.log(q)])


def thermal_primitive(state, v, law):
    energy, conjugate = state
    if np.any(energy <= 0) or not np.isfinite(state).all():
        raise ElasticDomainError('conductor energy left its positive finite domain')
    c2 = law.speed**2
    limit = (1-c2)*(1-1e-8)
    def residual(r):
        return r+c2*v*(np.log(energy)-np.log1p(v*r))-conjugate
    if np.any(residual(-limit) > 0) or np.any(residual(limit) < 0):
        raise ElasticDomainError('heat-current characteristic reached the causal boundary')
    lower, upper = np.full_like(v, -limit), np.full_like(v, limit)
    r = np.clip(conjugate-c2*v*np.log(energy), lower, upper)
    for _ in range(24):
        error = residual(r)
        if np.max(abs(error)) < 2e-13:
            break
        lower = np.where(error < 0, r, lower)
        upper = np.where(error > 0, r, upper)
        trial = r-error/(1-c2*v*v/(1+v*r))
        r = np.where((trial > lower) & (trial < upper), trial, .5*(lower+upper))
    if np.max(abs(residual(r))) > 1e-10:
        raise ElasticDomainError('heat-current inversion failed')
    q = energy/(1+v*r)
    if np.min(q) < 1e-8:
        raise ElasticDomainError('conducting material reached the positive-temperature floor')
    return q, r


def thermal_speeds(r, v, h, law):
    root = np.sqrt(r*r+4*law.speed**2)
    relative = np.array([.5*(r-root), .5*(r+root)])
    return h*relative/(1+v*relative), relative


class FrozenHeatBackground:
    """Smooth material worldsheet over the central, resolved material band.

    Cubic temporal Hermite interpolation uses stored positions and their
    physical velocities. A linear spatial interpolation of archived heat
    preserves positivity and commutes with its temporal derivative.
    """
    def __init__(self, patch, times, states, cells=129, band=(.375, .625), tabulation_step=.0005):
        self.patch, self.model, self.cells, self.band = patch, patch.model, cells, band
        self.end_time = float(times[-1])
        self.scale = patch.law.scale
        reference = np.r_[0., np.cumsum(patch.reference)]
        self.faces = np.linspace(band[0]*reference[-1], band[1]*reference[-1], cells+1)
        self.a = .5*(self.faces[:-1]+self.faces[1:])
        self.da = float(self.faces[1]-self.faces[0])
        saved = [patch.fields(float(t), y) for t, y in zip(times, states)]
        positions = np.array([f['x'] for f in saved])
        velocities = np.array([-f['metric'].beta+f['metric'].alpha*f['velocity']/f['metric'].b for f in saved])
        velocities[:, [0, -1]] = 0.
        heat = np.array([f['heat'] for f in saved])
        offset = 2*(patch.cells-1)
        heat_rate = np.array([patch.rhs(float(t), y)[0][offset:offset+patch.cells+1] for t, y in zip(times, states)])
        position_spline = CubicHermiteSpline(times, positions, velocities, axis=0)
        heat_spline = CubicHermiteSpline(times, heat, heat_rate, axis=0)
        z_spline = CubicSpline(times, np.array([f['z'] for f in saved]), axis=0)
        charge_spline = CubicSpline(times, np.array([f['charge'] for f in saved]), axis=0)
        self.times = np.linspace(0., self.end_time, int(np.ceil(self.end_time/tabulation_step))+1)
        tables, face_tables = [], []
        aa = np.r_[self.a, self.faces]
        for t in self.times:
            splines = [CubicSpline(reference, position_spline(t, nu=k), bc_type='natural') for k in (0, 1, 2)]
            x, xt, xtt = [spline(aa) for spline in splines]
            xa, xat = splines[0](aa, 1), splines[1](aa, 1)
            g = self.model.metric(float(t), x)
            tt = np.full_like(x, t)
            logalpha_t = self.model.metric_splines[0].ev(tt, x, dx=1)
            beta_t = self.model.metric_splines[1].ev(tt, x, dx=1)
            v = g.b*(xt+g.beta)/g.alpha
            if np.max(abs(v)) >= 1 or np.min(xa) <= 0:
                raise ElasticDomainError('interpolated material worldsheet left its timelike ordered domain')
            gamma = 1/np.sqrt(1-v*v)
            vt = g.b*(xtt+beta_t+g.beta_x*xt)/g.alpha
            vt += v*(g.logb_t+g.logb_x*xt-logalpha_t-g.alpha_x*xt/g.alpha)
            n = 1/(g.b*gamma*xa)
            logn_t = -g.logb_t-g.logb_x*xt-gamma**2*v*vt-xat/xa
            proper_rate = g.alpha/gamma
            h = proper_rate*n
            acceleration_rate = gamma**2*vt+g.alpha_x/g.b-g.alpha*v*g.k_l
            table = dict(x=x, v=v, vt=vt, gamma=gamma, n=n, h=h, proper_rate=proper_rate,
                          acceleration_rate=acceleration_rate,
                          expansion=-logn_t/proper_rate,
                          alpha=g.alpha, beta=g.beta, b=g.b, radius=g.radius,
                          alpha_t=g.alpha*logalpha_t, beta_t=beta_t, logb_t=g.logb_t,
                          qbase=np.interp(aa, reference, heat_spline(t)),
                          source=np.interp(aa, reference, heat_spline(t, nu=1)),
                          z=np.interp(aa, reference, z_spline(t)),
                          charge=np.interp(aa, reference, charge_spline(t)))
            if np.min(table['qbase']) <= 0:
                raise ElasticDomainError('interpolated reference temperature became nonpositive')
            tables.append({k: value[:cells] for k, value in table.items()})
            face_tables.append({k: table[k][cells:] for k in ('v', 'h')})
        self.tables = {k: np.array([row[k] for row in tables]) for k in tables[0]}
        self.face_tables = {k: np.array([row[k] for row in face_tables]) for k in face_tables[0]}

    def sample(self, t):
        i = int(np.clip(np.searchsorted(self.times, t), 1, len(self.times)-1))
        w = (t-self.times[i-1])/(self.times[i]-self.times[i-1])
        def interpolate(tables):
            return {key: (1-w)*values[i-1]+w*values[i] for key, values in tables.items()}
        center, faces = interpolate(self.tables), interpolate(self.face_tables)
        center['h_a'] = np.diff(faces['h'])/self.da
        return center, faces

    def rest(self, q, r, bg):
        law = self.patch.physical_law
        energy, pressure, _ = relaxing_rest(law, bg['n'], q, bg['z'], self.patch.relaxation.stiffness)
        flux = bg['n']*q*r
        # Convert the Maxwell contribution to the same line-density units.
        field = bg['radius']**2/self.scale*.5*(bg['charge']/bg['radius']**2)**2
        total_energy, total_pressure = energy+field, pressure-field
        discriminant = (total_energy+total_pressure)**2-4*flux**2
        if np.min(discriminant) <= 0:
            raise ElasticDomainError('combined conducting stress left its Type-I domain')
        density_rest = .5*(total_energy-total_pressure+np.sqrt(discriminant))
        if np.min(density_rest-field) < 0 or np.min(total_energy-total_pressure) < 0:
            raise ElasticDomainError('combined conducting stress left its dominant-energy domain')
        return dict(energy=total_energy, pressure=total_pressure, flux=flux,
                    maximum_flux_enthalpy_ratio=float(np.max(2*abs(flux)/(total_energy+total_pressure))))


def limited_slopes(values):
    left, right = values-np.roll(values, 1), np.roll(values, -1)-values
    slope = np.where(left*right > 0, np.sign(left)*np.minimum(np.minimum(2*abs(left), 2*abs(right)), .5*abs(left+right)), 0.)
    slope[[0, -1]] = 0.
    return slope


class HeatConductor:
    def __init__(self, background, law):
        self.background, self.law = background, law

    def initial(self):
        bg, _ = self.background.sample(0.)
        return thermal_conserved(bg['qbase'], np.zeros_like(bg['qbase']), bg['v'], self.law)

    def rhs(self, t, state):
        bg, face = self.background.sample(t)
        q, r = thermal_primitive(state, bg['v'], self.law)
        self.background.rest(q, r, bg)
        w = np.log(q)
        sw, sr = limited_slopes(w), limited_slopes(r)
        # Insulation fixes the relative heat flux. Temperature can retain a
        # gravitational equilibrium gradient right up to the material end.
        sw[0], sw[-1] = w[1]-w[0], w[-1]-w[-2]
        wl, wr = np.r_[w[0], w+.5*sw], np.r_[w-.5*sw, w[-1]]
        wl[0], wr[-1] = wr[0], wl[-1]
        rl, rr = np.r_[-r[0], r+.5*sr], np.r_[r-.5*sr, -r[-1]]
        ql, qr = np.exp(wl), np.exp(wr)
        ul = thermal_conserved(ql, rl, face['v'], self.law)
        ur = thermal_conserved(qr, rr, face['v'], self.law)
        fl = np.array([face['h']*ql*rl, self.law.speed**2*face['h']*wl])
        fr = np.array([face['h']*qr*rr, self.law.speed**2*face['h']*wr])
        left_speed, _ = thermal_speeds(rl, face['v'], face['h'], self.law)
        right_speed, _ = thermal_speeds(rr, face['v'], face['h'], self.law)
        speed = np.maximum(np.max(abs(left_speed), axis=0), np.max(abs(right_speed), axis=0))
        flux = .5*(fl+fr)-.5*speed*(ur-ul)
        flux[0, [0, -1]] = 0.
        c2, decay = self.law.speed**2, bg['proper_rate']/self.law.proper_time
        source = np.array([bg['source']-bg['acceleration_rate']*q*r,
                           -decay*r-c2*bg['acceleration_rate']+c2*(bg['vt']+bg['h_a'])*w])
        rate = -np.diff(flux, axis=1)/self.background.da+source
        aa = rate[0]/q-bg['vt']*r
        bb = rate[1]-c2*bg['vt']*w
        wt = (aa-bg['v']*bb)/(1+bg['v']*r-c2*bg['v']**2)
        rt = bb-c2*bg['v']*wt
        heat_source = bg['source']
        entropy_production = decay*r*r/c2 if c2 else np.zeros_like(r)
        delta = q-bg['qbase']
        force_per_reference = delta*bg['acceleration_rate']/bg['proper_rate']
        force_per_reference += q*(r*wt+rt)/bg['proper_rate']+bg['expansion']*q*r
        # D=(Gamma/alpha) partial_s = partial_s/proper_rate.
        holding_power = bg['alpha']*(bg['alpha']*bg['v']-bg['b']*bg['beta'])*force_per_reference
        de = bg['n']*bg['gamma']**2*(delta+2*q*r*bg['v'])
        dj = bg['n']*bg['gamma']**2*(delta*bg['v']+q*r*(1+bg['v']**2))
        ds = bg['n']*bg['gamma']**2*(delta*bg['v']**2+2*q*r*bg['v'])
        geometric_power = (de*bg['alpha_t']-bg['alpha']*ds*bg['logb_t']-bg['b']*dj*bg['beta_t'])/(bg['n']*bg['gamma'])
        measure = 4*np.pi*self.background.scale*self.background.da
        diagnostics = dict(inverse_step=float(speed.max()/self.background.da), maximum_decay=float(decay.max()),
                           heat_input=float(measure*heat_source.sum()),
                           acceleration_work=float(-measure*np.sum(bg['acceleration_rate']*q*r)),
                           entropy_supply=float(measure*np.sum(heat_source/q)),
                           entropy_production=float(measure*entropy_production.sum()),
                           holding_work=float(measure*holding_power.sum()),
                           holding_positive_work=float(measure*np.maximum(holding_power, 0.).sum()),
                           holding_negative_work=float(measure*np.minimum(holding_power, 0.).sum()),
                           geometric_work=float(measure*geometric_power.sum()),
                           maximum_added_force_per_reference=float(np.max(abs(force_per_reference))))
        return rate, diagnostics

    def diagnostics(self, t, state, ledger, initial):
        bg, _ = self.background.sample(t)
        q, r = thermal_primitive(state, bg['v'], self.law)
        rest = self.background.rest(q, r, bg)
        _, relative_speeds = thermal_speeds(r, bg['v'], bg['h'], self.law)
        measure = 4*np.pi*self.background.scale*self.background.da
        entropy = np.log(q)+bg['v']*r
        if self.law.speed:
            entropy -= r*r/(2*self.law.speed**2)
        hdelta = bg['gamma']*((bg['alpha']-bg['b']*bg['beta']*bg['v'])*(q-bg['qbase'])
                               +(2*bg['alpha']*bg['v']-bg['b']*bg['beta']*(1+bg['v']**2))*q*r)
        reference_rest = self.background.rest(bg['qbase'], np.zeros_like(r), bg)
        reference_energy = (reference_rest['energy']+reference_rest['pressure'])*bg['gamma']**2-reference_rest['pressure']
        added_energy = bg['n']*bg['gamma']**2*(q-bg['qbase']+2*q*r*bg['v'])
        return dict(s=t, minimum_heat=float(q.min()), minimum_reference_heat=float(bg['qbase'].min()),
                    receiver_heat=float(np.interp(.5*sum(self.background.faces[[0, -1]]), self.background.a, q)),
                    maximum_relative_heat_flux=float(abs(r).max()),
                    maximum_material_frame_signal_speed=float(abs(relative_speeds).max()),
                    maximum_flux_enthalpy_ratio=rest['maximum_flux_enthalpy_ratio'],
                    maximum_relative_added_normal_density=float(np.max(abs(added_energy)/reference_energy)),
                    thermal_inventory=float(measure*q.sum()),
                    tilted_heat_inventory=float(measure*state[0].sum()),
                    tilted_heat_balance=float(measure*state[0].sum()-initial['heat']-ledger['heat_input']-ledger['acceleration_work']),
                    entropy_inventory=float(measure*entropy.sum()),
                    entropy_excess=float(measure*entropy.sum()-initial['entropy']-ledger['entropy_supply']-ledger['entropy_production']),
                    canonical_energy_change=float(measure*hdelta.sum()),
                    canonical_balance_residual=float(measure*hdelta.sum()-ledger['holding_work']-ledger['geometric_work']),
                    **{key+'_integral': float(value) for key, value in ledger.items()})


def evolve_heat_conductor(conductor, *, max_step=.0005, cfl=.3, snapshots=101, deadline_seconds=180.):
    state = conductor.initial()
    bg, _ = conductor.background.sample(0.)
    measure = 4*np.pi*conductor.background.scale*conductor.background.da
    initial = dict(heat=float(measure*state[0].sum()), entropy=float(measure*np.log(bg['qbase']).sum()))
    keys = ('heat_input', 'acceleration_work', 'entropy_supply', 'entropy_production', 'holding_work',
            'holding_positive_work', 'holding_negative_work', 'geometric_work')
    ledger = {key: 0. for key in keys}
    times, states, history = [], [], []
    t, steps, start, failure = 0., 0, time.monotonic(), ''
    status = 'duration_completed'
    for target in np.linspace(0., conductor.background.end_time, snapshots):
        while t < target-1e-13:
            if time.monotonic()-start > deadline_seconds:
                status = 'compute_budget_reached'; break
            try:
                k1, d1 = conductor.rhs(t, state)
            except ElasticDomainError as error:
                status, failure = 'constitutive_domain_limit', str(error); break
            dt = min(max_step, target-t, cfl/max(d1['inverse_step'], 1e-15), .2/max(d1['maximum_decay'], 1e-15))
            accepted = False
            for _ in range(20):
                try:
                    k2, d2 = conductor.rhs(t+dt, state+dt*k1)
                    middle = .75*state+.25*(state+dt*k1+dt*k2)
                    k3, d3 = conductor.rhs(t+.5*dt, middle)
                    candidate = state/3+2*(middle+dt*k3)/3
                    ff, _ = conductor.background.sample(t+dt)
                    qq, rr = thermal_primitive(candidate, ff['v'], conductor.law)
                    conductor.background.rest(qq, rr, ff)
                    accepted = True; break
                except ElasticDomainError as error:
                    failure = str(error); dt *= .5
            if not accepted or dt < 1e-10:
                status = 'constitutive_domain_limit'; break
            for key in keys:
                ledger[key] += dt*(d1[key]/6+d2[key]/6+2*d3[key]/3)
            state, t, steps = candidate, t+dt, steps+1
        history.append(conductor.diagnostics(t, state, ledger, initial))
        states.append(state.copy()); times.append(t)
        if status != 'duration_completed':
            break
    return dict(status=status, failure=failure if status != 'duration_completed' else '',
                elapsed_seconds=time.monotonic()-start, steps=steps,
                times=np.array(times), states=np.array(states), history=history)
