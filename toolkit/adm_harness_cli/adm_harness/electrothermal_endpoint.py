"""Confined radial Maxwell storage coupled to the active elastic reservoir.

The evolved energy includes both tensors. Q=R^2 E is stored on faces;
Q=0 at both ends gives zero total charge and vanishing exterior field in
this spherical electric specialization. All support-end tractions remain
explicit ports. The endpoint forcing is the previously pinned history.
"""
from __future__ import annotations

from dataclasses import dataclass
import time

import numpy as np

from .active_transfer_reservoir import divergence_projections, smooth_rise
from .elastic_endpoint_reservoir import ElasticDomainError, ElasticPatch, minmod, recover


@dataclass(frozen=True)
class ElectricalLaw:
    energy_ratio: float = 1.
    conductivity: float = .1
    heat_target: float = .25
    edge_width: float = .15

    def __post_init__(self):
        if (self.energy_ratio < 0 or self.conductivity < 0
                or self.heat_target <= 0 or self.edge_width <= 0):
            raise ValueError('nonnegative electrical preload/conductivity and positive scales required')

    def sigma(self, thermal):
        # A local passive switch. Its coefficients depend on the current
        # material temperature; future endpoint demand is absent here.
        return self.conductivity*smooth_rise(1-np.asarray(thermal)/self.heat_target)[0]


def maxwell_moments(charge, radius):
    density = .5*(np.asarray(charge)/radius**2)**2
    return np.array([density, -density, np.zeros_like(density), density])


def maxwell_currents(g, charge, charge_t, charge_x):
    """Gauss and Ampere laws, in rationalized c=1 electromagnetic units."""
    electric = charge/g.radius**2
    density = charge_x/g.volume
    current = (g.beta*charge_x-charge_t)/(g.alpha*g.radius**2)
    return electric, density, current


def em_conserved_energy(charge_faces, g):
    charge = .5*(charge_faces[:-1]+charge_faces[1:])
    return g.volume*.5*(charge/g.radius**2)**2


def advective_gradient(values, velocity, dx):
    """Second-order ENO one-sided derivatives for the face Q equation."""
    first = np.diff(values)/dx
    second = np.diff(first)/dx
    curvature = np.zeros_like(values)
    curvature[1:-1] = second
    left_curve = minmod(curvature[1:-1], curvature[:-2], curvature[1:-1])
    right_curve = minmod(curvature[1:-1], curvature[2:], curvature[1:-1])
    backward = first[:-1]+.5*dx*left_curve
    forward = first[1:]-.5*dx*right_curve
    result = np.zeros_like(values)
    result[1:-1] = np.where(velocity[1:-1] >= 0, backward, forward)
    return result


class ElectrothermalPatch(ElasticPatch):
    def __init__(self, model, law, electrical, *, allocation='field', **kwargs):
        super().__init__(model, law, **kwargs)
        if allocation not in ('field', 'material'):
            raise ValueError('allocation must be field or material')
        self.electrical, self.allocation = electrical, allocation

    def initial_pair(self):
        material = super().initial(initialization='prepared_reference')
        g = self.model.metric(0., self.x)
        faces = self.model.metric(0., self.faces)
        f = recover(material, g.b, self.law)
        n = np.interp(self.faces, self.x, f['n'])
        q = np.interp(self.faces, self.x, f['thermal'])
        distance = np.minimum(self.faces-self.faces[0], self.faces[-1]-self.faces)
        window = smooth_rise(distance/self.electrical.edge_width)[0]
        charge = faces.radius*np.sqrt(2*self.electrical.energy_ratio*self.law.scale*n*q)*window
        charge[[0, -1]] = 0.
        total = material.copy()
        total[1] += em_conserved_energy(charge, g)
        if self.allocation == 'material':
            # Identical conserved D, total energy, and total momentum in
            # every cell; redistribute the field contribution into matter.
            charge *= 0.
            recover(total, g.b, self.law)
        return total, charge

    def material_fields(self, t, total, charge):
        g = self.model.metric(t, self.x)
        material = total.copy()
        material[1] -= em_conserved_energy(charge, g)
        return g, material, recover(material, g.b, self.law)

    def pair_rhs(self, t, total, charge):
        g, material, f = self.material_fields(t, total, charge)
        rate, _, diag = super().rhs(t, material)
        gf = self.model.metric(t, self.faces)
        energy = em_conserved_energy(charge, g)
        rho = energy/g.volume
        face_rho = .5*(charge/gf.radius**2)**2
        em_flux = np.array([np.zeros_like(charge), -gf.beta*gf.volume*face_rho,
                            -gf.alpha*gf.b*gf.radius**2*face_rho])
        em_geometry = np.array([
            np.zeros_like(rho),
            g.alpha*g.volume*rho*(-g.k_l+2*g.k_omega),
            g.volume*rho*(-g.alpha_x-g.alpha*g.logb_x+2*g.alpha*g.logr_x),
        ])
        rate += -np.diff(em_flux, axis=1)/self.dx+em_geometry
        diag['boundary'] += em_flux[:, 0]-em_flux[:, -1]
        diag['geometry'] += self.dx*em_geometry.sum(axis=1)
        face_v = np.interp(self.faces, self.x, f['velocity'])
        face_v[[0, -1]] = (gf.b*gf.beta/gf.alpha)[[0, -1]]
        face_heat = np.interp(self.faces, self.x, f['thermal'])
        coord_v = -gf.beta+gf.alpha*face_v/gf.b
        decay = gf.alpha*self.electrical.sigma(face_heat)*np.sqrt(1-face_v*face_v)
        charge_rate = -coord_v*advective_gradient(charge, coord_v, self.dx)-decay*charge
        charge_rate[[0, -1]] = 0.
        gamma = 1/np.sqrt(1-f['velocity']**2)
        power, force = divergence_projections(g, *self.model.medium(t, self.x))
        heat_endpoint = -self.forcing*gamma*(power-f['velocity']*force)
        heat_electrical = 2*rho*self.electrical.sigma(f['thermal'])
        diag['thermal_endpoint'] = float(self.dx*np.sum(g.alpha*g.volume*heat_endpoint))
        diag['thermal_electrical'] = float(self.dx*np.sum(g.alpha*g.volume*heat_electrical))
        diag['maximum_decay'] = float(decay.max())
        diag['max_speed'] = max(diag['max_speed'], float(abs(coord_v).max()))
        return rate, charge_rate, diag


def evolve_electrothermal(patch, *, duration=.5, snapshots=101, cfl=.25,
                         deadline_seconds=240., max_steps=40000):
    total, charge = patch.initial_pair()
    initial = patch.dx*total.sum(axis=1)
    ledger = {key: np.zeros(3) for key in ('boundary', 'geometry', 'exchange')}
    thermal_ledger = dict(thermal_endpoint=0., thermal_electrical=0.)
    records, states, charges, times = [], [], [], []
    initial_thermal = None
    t, steps = 0., 0
    status, failure = 'duration_completed', ''
    start = time.monotonic()
    for target in np.linspace(0., duration, snapshots):
        while t < target-1e-13:
            if time.monotonic()-start >= deadline_seconds or steps >= max_steps:
                status = 'compute_budget_reached'; break
            try:
                rate, qrate, diag = patch.pair_rhs(t, total, charge)
            except ElasticDomainError as error:
                status, failure = 'constitutive_domain_limit', str(error); break
            dt = min(cfl*patch.dx/max(diag['max_speed'], 1e-15),
                     .2/max(diag['maximum_decay'], 1e-15), target-t, .005)
            accepted = False
            for _ in range(16):
                try:
                    stage, qstage = total+dt*rate, charge+dt*qrate
                    second, qsecond, other = patch.pair_rhs(t+dt, stage, qstage)
                    candidate = .5*(total+stage+dt*second)
                    qcandidate = .5*(charge+qstage+dt*qsecond)
                    patch.material_fields(t+dt, candidate, qcandidate)
                    if not np.isfinite(qcandidate).all() or np.min(qcandidate) < -1e-13:
                        raise ElasticDomainError('electric charge profile left its nonnegative finite domain')
                    accepted = True; break
                except ElasticDomainError as error:
                    failure = str(error); dt *= .5
            if not accepted or dt < 1e-9:
                status = 'constitutive_domain_limit'; break
            for key in ledger:
                ledger[key] += .5*dt*(diag[key]+other[key])
            for key in thermal_ledger:
                thermal_ledger[key] += .5*dt*(diag[key]+other[key])
            total, charge, t, steps = candidate, qcandidate, t+dt, steps+1
        g, material, f = patch.material_fields(t, total, charge)
        integral = patch.dx*total.sum(axis=1)
        residual = integral-initial-sum(ledger.values())
        thermal = float(patch.law.scale*patch.dx*np.sum(total[0]*f['thermal']))
        if initial_thermal is None:
            initial_thermal = thermal
        em_energy = float(patch.dx*em_conserved_energy(charge, g).sum())
        charge_density = np.diff(charge)/(patch.dx*g.volume)
        row = dict(s=t, steps=steps, minimum_thermal=float(f['thermal'].min()),
                   coldest_l=float(patch.x[np.argmin(f['thermal'])]),
                   maximum_abs_velocity=float(abs(f['velocity']).max()),
                   maximum_sound2=float(f['sound2'].max()),
                   minimum_inverse_stretch=float(f['n'].min()),
                   maximum_inverse_stretch=float(f['n'].max()),
                   total_slice_energy=float(4*np.pi*integral[1]),
                   field_slice_energy=float(4*np.pi*em_energy),
                   material_slice_energy=float(4*np.pi*(integral[1]-em_energy)),
                   thermal_inventory=float(4*np.pi*thermal),
                   thermal_balance_residual=float(4*np.pi*(thermal-initial_thermal-sum(thermal_ledger.values()))),
                   net_charge=float(4*np.pi*(charge[-1]-charge[0])),
                   maximum_abs_charge_density=float(abs(charge_density).max()),
                   maximum_field_density=float(np.max(em_conserved_energy(charge, g)/g.volume)),
                   maximum_end_traction=float(abs(patch.pair_rhs(t, total, charge)[2]['end_traction']).max()))
        row.update({key: float(4*np.pi*value) for key, value in thermal_ledger.items()})
        for i, name in enumerate(('material', 'energy', 'momentum')):
            row[f'{name}_balance_residual'] = float(residual[i])
            for key in ledger:
                row[f'{name}_{key}_integral'] = float(ledger[key][i])
        records.append(row); states.append(total.copy()); charges.append(charge.copy()); times.append(t)
        if status != 'duration_completed':
            break
    return dict(status=status, failure=failure if status != 'duration_completed' else '',
                final_time=t, elapsed_seconds=time.monotonic()-start, steps=steps,
                history=records, states=np.array(states), charges=np.array(charges), times=np.array(times))
