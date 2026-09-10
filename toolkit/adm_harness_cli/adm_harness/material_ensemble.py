"""Variational material-coordinate elastic, thermal, and radial Maxwell store.

Positions delimit material cells of conserved reference length. Endpoint
positions are constrained; their reaction forces are counted. Thermal energy
and electric flux follow the same material labels. The spatial discretization
uses a lumped-velocity quadrature of the relativistic material action.
"""
from __future__ import annotations

import time
import numpy as np

from .active_transfer_reservoir import divergence_projections, smooth_rise
from .elastic_endpoint_reservoir import ElasticDomainError, ElasticPatch, recover


def nodal_sum(cell_values):
    """Half of each neighboring cell contribution at a material node."""
    return .5*(np.r_[cell_values, 0.]+np.r_[0., cell_values])


class MaterialEnsemble:
    def __init__(self, model, law, electrical, cells=64, thermal_share=.75, forcing=1., edges=(-2.1, -.5)):
        if cells < 4 or not 0 <= thermal_share <= 1:
            raise ValueError('at least four cells and thermal share in [0,1] required')
        self.model, self.law, self.electrical = model, law, electrical
        self.cells, self.thermal_share, self.forcing, self.edges = cells, thermal_share, forcing, edges
        self.initial_x = np.linspace(*edges, cells+1)
        old = ElasticPatch(model, law, cells=cells, edges=edges, forcing=forcing)
        material = old.initial(initialization='prepared_reference')
        g = model.metric(0., old.x)
        f = recover(material, g.b, law)
        self.reference = material[0]*old.dx
        self.mass = nodal_sum(self.reference)
        self.initial_heat = np.interp(self.initial_x, old.x, f['thermal'])
        self.initial_cell_width = np.diff(self.initial_x)

    def split(self, state):
        n, inner = self.cells+1, self.cells-1
        x = np.r_[self.edges[0], state[:inner], self.edges[1]]
        momentum = np.r_[0., state[inner:2*inner], 0.]
        heat = state[2*inner:2*inner+n]
        charge = state[2*inner+n:2*inner+2*n]
        return x, momentum, heat, charge

    def pack(self, x, momentum, heat, charge):
        return np.r_[x[1:-1], momentum[1:-1], heat, charge]

    def coefficients(self, t, x):
        width = np.diff(x)
        if np.min(width) <= 1e-10 or not np.isfinite(x).all():
            raise ElasticDomainError('material cells reached the ordered-mesh boundary')
        g = self.model.metric(t, x)
        volume = nodal_sum(width)
        a = self.law.stiffness*nodal_sum(self.reference**2/width)/(2*g.b)
        b = .5*self.law.stiffness*g.b*volume
        return g, width, volume, a, b

    def velocity(self, momentum, heat, g, a):
        c = self.law.mass+heat-self.law.stiffness
        if np.min(heat) <= 0 or not np.isfinite(heat).all():
            raise ElasticDomainError('material thermal energy reached zero')
        target = momentum/(self.law.scale*self.mass*g.b)
        kappa = 2*a/self.mass
        # c*sinh(eta)+kappa*tanh(eta)=target is strictly increasing.
        eta = np.arcsinh(target/c)
        for _ in range(16):
            residual = c*np.sinh(eta)+kappa*np.tanh(eta)-target
            if np.all(abs(residual) <= 2e-14*(1+abs(target))):
                break
            derivative = c*np.cosh(eta)+kappa/np.cosh(eta)**2
            correction = np.clip(residual/derivative, -1., 1.)
            eta -= correction
        if np.max(abs(c*np.sinh(eta)+kappa*np.tanh(eta)-target)/(1+abs(target))) > 1e-10:
            raise ElasticDomainError('material canonical momentum inversion failed')
        v = np.tanh(eta)
        v[[0, -1]] = (g.b*g.beta/g.alpha)[[0, -1]]
        if np.max(abs(v)) >= 1:
            raise ElasticDomainError('material endpoint or velocity left its timelike domain')
        return v

    def fields(self, t, state):
        x, momentum, heat, charge = self.split(state)
        g, width, volume, a, b = self.coefficients(t, x)
        v = self.velocity(momentum, heat, g, a)
        gamma = 1/np.sqrt(1-v*v)
        c = self.law.mass+heat-self.law.stiffness
        momentum = self.law.scale*g.b*v*(self.mass*c*gamma+2*a)
        # Two endpoint quadrature values for each material cell.
        stretch = self.reference[None, :]/(width[None, :]*np.array([g.b[:-1]*gamma[:-1], g.b[1:]*gamma[1:]]))
        qcell = np.array([heat[:-1], heat[1:]])
        rest, pressure, sound2 = self.law.rest(stretch, qcell)
        vv, gg = np.array([v[:-1], v[1:]]), np.array([gamma[:-1], gamma[1:]])
        energy = (rest+pressure)*gg**2-pressure
        current = (rest+pressure)*gg**2*vv
        radial = pressure+vv*current
        def lump(values):
            return .5*(np.r_[width*values[0], 0.]+np.r_[0., width*values[1]])
        energy_int, current_int, radial_int = lump(energy), lump(current), lump(radial)
        matter_adm = self.law.scale*g.b*energy_int
        field_adm = g.b*volume*charge**2/(2*g.radius**2)
        canonical = g.alpha*(matter_adm+field_adm)-g.beta*momentum
        return dict(x=x, momentum=momentum, heat=heat, charge=charge, metric=g, width=width,
                    volume=volume, a=a, b=b, velocity=v, gamma=gamma, stretch=stretch,
                    pressure=pressure, sound2=sound2, energy_int=energy_int,
                    current_int=current_int, radial_int=radial_int, matter_adm=matter_adm,
                    field_adm=field_adm, canonical=canonical,
                    effective_n=self.mass/(g.b*gamma*volume))

    def initial(self):
        x, heat = self.initial_x.copy(), self.initial_heat.copy()
        g, width, volume, a, _ = self.coefficients(0., x)
        velocity = g.b*g.beta/g.alpha
        gamma = 1/np.sqrt(1-velocity**2)
        effective_n = self.mass/(g.b*gamma*volume)
        distance = np.minimum(x-x[0], x[-1]-x)
        window = smooth_rise(distance/self.electrical.edge_width)[0]
        charge = g.radius*np.sqrt(2*self.electrical.energy_ratio*self.law.scale*effective_n*heat)*window
        if self.electrical.profile == 'capacitor':
            target = np.sum(g.b*volume*charge**2/(2*g.radius**2))
            norm = np.sum(g.b*volume*window**2/(2*g.radius**2))
            charge = window*np.sqrt(target/norm)
        added_energy = g.b*volume*charge**2/(2*g.radius**2)
        heat += self.thermal_share*added_energy/(self.law.scale*self.mass*gamma)
        charge *= np.sqrt(1-self.thermal_share)
        momentum = self.law.scale*g.b*velocity*(self.mass*(self.law.mass+heat-self.law.stiffness)*gamma+2*a)
        return self.pack(x, momentum, heat, charge)

    def lapse_shift_time(self, t, x, g):
        # The production patch lies entirely inside the unblended spline
        # region; use its exact temporal derivatives when available.
        if hasattr(self.model, 'metric_splines') and np.max(abs(x)) < 5:
            tt = np.full_like(x, t)
            return (g.alpha*self.model.metric_splines[0].ev(tt, x, dx=1),
                    self.model.metric_splines[1].ev(tt, x, dx=1))
        h = 1e-5
        plus, minus = self.model.metric(t+h, x), self.model.metric(t-h, x)
        return (plus.alpha-minus.alpha)/(2*h), (plus.beta-minus.beta)/(2*h)

    def rhs(self, t, state):
        f = self.fields(t, state)
        g, volume, v, gamma = f['metric'], f['volume'], f['velocity'], f['gamma']
        heat, charge = f['heat'], f['charge']
        xrate = -g.beta+g.alpha*v/g.b
        xrate[[0, -1]] = 0.
        em_pressure = g.alpha*g.b*charge**2/(2*g.radius**2)
        traction = .5*self.law.scale*(g.alpha[:-1]*g.b[:-1]*f['pressure'][0]
                                      +g.alpha[1:]*g.b[1:]*f['pressure'][1])
        traction -= .5*(em_pressure[:-1]+em_pressure[1:])
        pressure_force = np.r_[0., traction]-np.r_[traction, 0.]
        # h_i=x_{i+1}-x_i: the left node receives -traction, the right +traction.
        explicit = self.law.scale*g.b*(f['energy_int']*g.alpha_x
                    -g.alpha*f['radial_int']*g.logb_x-g.b*f['current_int']*g.beta_x)
        explicit += g.alpha*f['field_adm']*(g.alpha_x/g.alpha+g.logb_x-2*g.logr_x)
        prate = pressure_force-explicit
        power, force = divergence_projections(g, *self.model.medium(t, f['x']))
        prate -= self.forcing*g.alpha*g.b**2*g.radius**2*volume*force
        factor = g.alpha*g.radius**2/(self.law.scale*f['effective_n'])
        qendpoint = self.forcing*factor*(-power+v*force)
        sigma = self.electrical.sigma(heat)
        qelectrical = factor*sigma*(charge/g.radius**2)**2/gamma
        qrate = qendpoint+qelectrical
        charge_rate = -g.alpha*sigma*charge/gamma
        alpha_t, beta_t = self.lapse_shift_time(t, f['x'], g)
        geometry = self.law.scale*g.b*(f['energy_int']*alpha_t
                    -g.alpha*f['radial_int']*g.logb_t-g.b*f['current_int']*beta_t)
        geometry += g.alpha*f['field_adm']*(alpha_t/g.alpha+g.logb_t-2*g.logr_t)
        port = -self.forcing*g.alpha*g.b*g.radius**2*volume*(g.alpha*power-g.beta*g.b*force)
        # Constrained end momenta change with the metric, strain, and heat.
        width_rate = np.diff(xrate)
        adot = -f['a']*g.logb_t-self.law.stiffness*nodal_sum(self.reference**2*width_rate/f['width']**2)/(2*g.b)
        vdot_wall = v*(g.logb_t-alpha_t/g.alpha)+g.b*beta_t/g.alpha
        c = self.law.mass+heat-self.law.stiffness
        pdot_wall = self.law.scale*g.b*(
            g.logb_t*v*(self.mass*c*gamma+2*f['a'])
            +self.mass*qrate*gamma*v+self.mass*c*gamma**3*vdot_wall
            +2*adot*v+2*f['a']*vdot_wall)
        reactions = pdot_wall[[0, -1]]-prate[[0, -1]]
        sound = np.sqrt(f['sound2'])
        # Material-relative longitudinal wave speeds bound the time step.
        cell_v = np.array([v[:-1], v[1:]])
        cell_alpha_b = np.array([g.alpha[:-1]/g.b[:-1], g.alpha[1:]/g.b[1:]])
        waves = cell_alpha_b*sound*(1-cell_v**2)/(1-abs(cell_v)*sound)
        inverse_dt = np.max(waves.max(axis=0)/f['width'])
        inverse_dt = max(inverse_dt, float(np.max(np.maximum(0., -width_rate)/f['width'])))
        diagnostics = dict(canonical_geometry=float(geometry.sum()), canonical_endpoint=float(port.sum()),
                           heat_endpoint=float(self.law.scale*np.dot(self.mass, qendpoint)),
                           heat_electrical=float(self.law.scale*np.dot(self.mass, qelectrical)),
                           momentum_free=float(prate.sum()), anchor_left=float(reactions[0]), anchor_right=float(reactions[1]),
                           inverse_step=float(inverse_dt), maximum_decay=float(np.max(g.alpha*sigma/gamma)),
                           maximum_anchor_force=float(np.max(abs(reactions)/(g.alpha[[0, -1]]*g.b[[0, -1]]))))
        return self.pack(xrate, prate, qrate, charge_rate), diagnostics


def evolve_material_ensemble(patch, *, duration=.5, snapshots=101, max_step=.002, cfl=.2,
                            deadline_seconds=240., initial=None, max_steps=60000):
    state = patch.initial() if initial is None else initial.copy()
    initial_fields = patch.fields(0., state)
    h0, p0 = initial_fields['canonical'].sum(), initial_fields['momentum'].sum()
    q0 = patch.law.scale*np.dot(patch.mass, initial_fields['heat'])
    keys = ('canonical_geometry', 'canonical_endpoint', 'heat_endpoint', 'heat_electrical',
            'momentum_free', 'anchor_left', 'anchor_right')
    ledger = {key: 0. for key in keys}
    states, times, history = [], [], []
    t, steps = 0., 0
    status, failure = 'duration_completed', ''
    start = time.monotonic()
    for target in np.linspace(0., duration, snapshots):
        while t < target-1e-13:
            if time.monotonic()-start > deadline_seconds or steps >= max_steps:
                status = 'compute_budget_reached'; break
            first, d1 = patch.rhs(t, state)
            dt = min(max_step, target-t, cfl/max(d1['inverse_step'], 1e-15), cfl/max(d1['maximum_decay'], 1e-15))
            accepted = False
            for _ in range(20):
                try:
                    second, d2 = patch.rhs(t+.5*dt, state+.5*dt*first)
                    third, d3 = patch.rhs(t+.5*dt, state+.5*dt*second)
                    fourth, d4 = patch.rhs(t+dt, state+dt*third)
                    candidate = state+dt*(first+2*second+2*third+fourth)/6
                    ff = patch.fields(t+dt, candidate)
                    if np.min(ff['heat']) < 1e-8:
                        raise ElasticDomainError('material heat reached the registered positive-temperature floor')
                    if np.min(ff['width']/patch.initial_cell_width) < 1e-6:
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
        h, p = f['canonical'].sum(), f['momentum'].sum()
        thermal = patch.law.scale*np.dot(patch.mass, f['heat'])
        _, diag = patch.rhs(t, state)
        row = dict(s=t, steps=steps, minimum_heat=float(f['heat'].min()),
                   coldest_l=float(f['x'][np.argmin(f['heat'])]),
                   maximum_abs_velocity=float(abs(f['velocity']).max()), maximum_sound2=float(f['sound2'].max()),
                   minimum_stretch=float(f['stretch'].min()), maximum_stretch=float(f['stretch'].max()),
                   minimum_relative_cell_width=float(np.min(f['width']/patch.initial_cell_width)),
                   minimum_packet_gap=float(np.min(abs(f['x']-t))-.35),
                   canonical_energy=float(4*np.pi*h), slice_energy=float(4*np.pi*np.sum(f['matter_adm']+f['field_adm'])),
                   field_slice_energy=float(4*np.pi*f['field_adm'].sum()), thermal_inventory=float(4*np.pi*thermal),
                   canonical_balance_residual=float(4*np.pi*(h-h0-ledger['canonical_geometry']-ledger['canonical_endpoint'])),
                   momentum_balance_residual=float(p-p0-ledger['momentum_free']-ledger['anchor_left']-ledger['anchor_right']),
                   thermal_balance_residual=float(4*np.pi*(thermal-q0-ledger['heat_endpoint']-ledger['heat_electrical'])),
                   maximum_anchor_force=diag['maximum_anchor_force'])
        row.update({f'{key}_integral': float(value) for key, value in ledger.items()})
        history.append(row); states.append(state.copy()); times.append(t)
        if status != 'duration_completed':
            break
    return dict(status=status, failure=failure if status != 'duration_completed' else '', final_time=t,
                elapsed_seconds=time.monotonic()-start, steps=steps,
                states=np.array(states), times=np.array(times), history=history)
