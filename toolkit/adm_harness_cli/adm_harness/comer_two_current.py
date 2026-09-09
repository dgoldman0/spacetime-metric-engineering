"""Spherical two-current evolution with an explicit conserved support source.

The particles and entropy obey separate barotropic Euler equations with an
equal/opposite covariant resistance. Their summed stress determines the mass
and polar lapse at every stage. The signed support has E=I(r), Pr=-I(r),
Pt=-I-r I'/2; it is separately conserved in every polar-areal metric.
This support law changes the reference initial pressure. Junction residuals
are independent acceptance conditions, not part of the evolution closure.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import CubicSpline

from .reset_inverse_search import reference_grid


class EvolutionDomainError(ValueError):
    pass


def fluid_moments(rest, velocity, w):
    rest, velocity = np.broadcast_arrays(rest, velocity)
    gamma2 = 1/(1-velocity*velocity)
    enthalpy = (1+w)*rest
    return np.stack([enthalpy*gamma2-w*rest, enthalpy*gamma2*velocity,
                     enthalpy*gamma2*velocity*velocity+w*rest, w*rest], axis=-1)


def recover_fluid(energy, current, w):
    energy, current = np.broadcast_arrays(energy, current)
    if np.any(energy <= 0) or np.any(abs(current) >= energy) or not np.isfinite(energy+current).all():
        raise EvolutionDomainError('ordinary fluid left its timelike positive-energy domain')
    z = current/energy
    velocity = 2*z/(1+w+np.sqrt((1+w)**2-4*w*z*z))
    rest = energy*(1-velocity*velocity)/(1+w*velocity*velocity)
    gamma = 1/np.sqrt(1-velocity*velocity)
    return rest, velocity, gamma


def resistance(rho_n, v_n, rho_s, v_s, relaxation, w_n=.2, w_s=1/3):
    """R^a=Rcal [u_s^a-gamma_relative u_n^a], in an orthonormal frame.

    u_n.R=0 conserves the particle flux. The entropy receives -R, giving
    T Gamma_s=u_s.R=Rcal (gamma_relative^2-1)>=0 exactly. The coefficient
    varies with both instantaneous rest-frame enthalpies.
    """
    if relaxation <= 0:
        raise ValueError('positive relaxation scale required')
    gn, gs = 1/np.sqrt(1-v_n*v_n), 1/np.sqrt(1-v_s*v_s)
    hn, hs = (1+w_n)*rho_n, (1+w_s)*rho_s
    coefficient = hn*hs/(hn+hs)/relaxation
    relative_gamma = gn*gs*(1-v_n*v_s)
    # Rapidity identities preserve the small-relative-drift entropy sign.
    relative_sinh = gn*gs*(v_s-v_n)
    force_j = coefficient*gn*relative_sinh
    force_e = v_n*force_j
    temperature = (1+w_s)*rho_s**(w_s/(1+w_s))
    entropy_creation = coefficient*relative_sinh**2/temperature
    return force_e, force_j, entropy_creation, relative_gamma


def minmod(a, b, c):
    same = (np.sign(a) == np.sign(b)) & (np.sign(b) == np.sign(c))
    return np.where(same, np.sign(a)*np.minimum(np.minimum(abs(a), abs(b)), abs(c)), 0.)


def reconstruct(values):
    slopes = np.zeros_like(values)
    slopes[1:-1] = minmod(1.5*(values[1:-1]-values[:-2]),
                          .5*(values[2:]-values[:-2]), 1.5*(values[2:]-values[1:-1]))
    left = np.r_[values[0], values+.5*slopes]
    right = np.r_[values-.5*slopes, values[-1]]
    return left, right


@dataclass
class TwoCurrentDomain:
    r: np.ndarray
    faces: np.ndarray
    volume: np.ndarray
    reference_mass: np.ndarray
    reference_face_mass: np.ndarray
    reference_alpha: np.ndarray
    reference_pressure: np.ndarray
    reference_transverse: np.ndarray
    initial_fluid_energy: np.ndarray
    support_energy: np.ndarray
    support_transverse: np.ndarray
    w_n: float = .2
    w_s: float = 1/3

    @property
    def cells(self):
        return len(self.r)


def prepare_domain(reference, cells, preload_fraction, initial_drift):
    if cells < 16 or not 0 < preload_fraction <= 1 or abs(initial_drift) > .1:
        raise ValueError('at least 16 cells, positive bounded preload, and drift <=0.1 required')
    # Cell centres lie strictly inside the same retained areal annulus.
    face_grid = reference_grid(reference, cells+1, 2, path_kind='direct')
    dense = reference_grid(reference, max(2049, 4*cells+1), 2, path_kind='direct')
    faces = face_grid.r
    r = .5*(faces[:-1]+faces[1:])
    volume = np.diff(faces**3)/3
    mf = CubicSpline(dense.r, dense.mass[0])
    alpha = np.exp(CubicSpline(dense.r, dense.nu[0])(r))
    pressure = CubicSpline(dense.r, dense.pressure[0])(r)
    transverse = CubicSpline(dense.r, dense.transverse[0])(r)
    initial_energy = mf(r, 1)/(4*np.pi*r*r)
    span = faces[-1]-faces[0]
    x = np.pi*(r-faces[0])/span
    window = np.sin(x)**4
    window_r = 4*np.pi*np.sin(x)**3*np.cos(x)/span
    scale = .039783*preload_fraction
    preload = scale*(window+1e-8)/(r*r)
    preload_r = scale*(window_r/(r*r)-2*(window+1e-8)/r**3)
    support = initial_energy-preload
    support_r = (mf(r, 2)/r**2-2*mf(r, 1)/r**3)/(4*np.pi)-preload_r
    domain = TwoCurrentDomain(r, faces, volume, mf(r), mf(faces), alpha, pressure,
                              transverse, preload, support, -support-.5*r*support_r)
    en, es = .5*preload, .5*preload
    vn = initial_drift*window
    jn = en*(1+domain.w_n)*vn/(1+domain.w_n*vn*vn)
    # Opposing initial heat current preserves the net initial momentum.
    state = np.r_[np.stack([en, jn, es, -jn], axis=-1).ravel(), 0.]
    recover_fluid(es, -jn, domain.w_s)
    return domain, state


def metric_and_fluids(domain, state):
    y = state[:-1].reshape(domain.cells, 4)
    en, jn, es, js = y.T
    rn, vn, gn = recover_fluid(en, jn, domain.w_n)
    rs, vs, gs = recover_fluid(es, js, domain.w_s)
    pn, ps = domain.w_n*rn, domain.w_s*rs
    prn, prs = jn*vn+pn, js*vs+ps
    perturbation = en+es-domain.initial_fluid_energy
    cell_mass = 4*np.pi*domain.volume*perturbation
    before = np.r_[0., np.cumsum(cell_mass)[:-1]]+state[-1]
    left_volume = (domain.r**3-domain.faces[:-1]**3)/3
    mass = domain.reference_mass+before+4*np.pi*left_volume*perturbation
    face_mass = domain.reference_face_mass+state[-1]+np.r_[0., np.cumsum(cell_mass)]
    f, face_f = 1-2*mass/domain.r, 1-2*face_mass/domain.faces
    if np.min(f) <= 0 or np.min(face_f) <= 0:
        raise EvolutionDomainError('the polar-areal domain reached f<=0')
    total_pr = -domain.support_energy+prn+prs
    nu_r = (mass+4*np.pi*domain.r**3*total_pr)/(domain.r**2*f)
    integral = cumulative_trapezoid(nu_r, domain.r, initial=0.)
    # Outer lapse is fixed at the boundary face, with a half-cell integral.
    nu = integral-integral[-1]-.5*(domain.faces[-1]-domain.faces[-2])*nu_r[-1]
    if np.min(nu) < -100 or np.max(nu) > 20:
        raise EvolutionDomainError('polar lapse left the registered numerical range')
    alpha = np.exp(nu)
    face_nu = np.r_[nu[0]-.5*(domain.faces[1]-domain.faces[0])*nu_r[0],
                    .5*(nu[:-1]+nu[1:]), 0.]
    face_alpha = np.exp(face_nu)
    total_j = jn+js
    log_a_t = -4*np.pi*domain.r*alpha*total_j/np.sqrt(f)
    return {'energy_n': en, 'current_n': jn, 'energy_s': es, 'current_s': js,
            'rest_n': rn, 'rest_s': rs, 'velocity_n': vn, 'velocity_s': vs,
            'gamma_n': gn, 'gamma_s': gs, 'pressure_n': pn, 'pressure_s': ps,
            'radial_n': prn, 'radial_s': prs, 'mass': mass, 'face_mass': face_mass,
            'f': f, 'face_f': face_f, 'alpha': alpha, 'face_alpha': face_alpha,
            'nu_r': nu_r, 'log_a_t': log_a_t, 'total_current': total_j,
            'total_energy': domain.support_energy+en+es, 'total_radial': total_pr,
            'total_angular': domain.support_transverse+pn+ps}


def fluid_flux(rest, velocity, w, face_alpha, faces):
    rl, rr = reconstruct(np.log(rest))
    vl, vr = reconstruct(np.arctanh(velocity))
    rl, rr, vl, vr = np.exp(rl), np.exp(rr), np.tanh(vl), np.tanh(vr)
    ml, mr = fluid_moments(rl, vl, w), fluid_moments(rr, vr, w)
    sound = np.sqrt(w)
    speed = np.maximum((abs(vl)+sound)/(1+abs(vl)*sound), (abs(vr)+sound)/(1+abs(vr)*sound))
    flux = .5*(ml[:, [1, 2]]+mr[:, [1, 2]])-.5*speed[:, None]*(mr[:, :2]-ml[:, :2])
    # Diode boundaries admit material leaving the domain. Opposite motion
    # sees zero normal velocity and its own pressure, supplying no inflow.
    for index, sign in [(0, -1), (-1, 1)]:
        vv = sign*max(sign*velocity[index], 0.)
        boundary = fluid_moments(rest[index], vv, w)
        flux[index] = boundary[[1, 2]]
    return face_alpha[:, None]*faces[:, None]**2*flux


def rhs(domain, state, relaxation):
    fields = metric_and_fluids(domain, state)
    alpha, rootf, r = fields['alpha'], np.sqrt(fields['f']), domain.r
    force_e, force_j, gamma_s, _ = resistance(fields['rest_n'], fields['velocity_n'],
        fields['rest_s'], fields['velocity_s'], relaxation, domain.w_n, domain.w_s)
    result = np.zeros((domain.cells, 4))
    boundary_energy = np.zeros(2)
    boundary_particles, boundary_entropy = [], []
    for offset, name, w, sign in [(0, 'n', domain.w_n, 1), (2, 's', domain.w_s, -1)]:
        e, j, pr, p = [fields[f'{key}_{name}'] for key in ['energy', 'current', 'radial', 'pressure']]
        flux = fluid_flux(fields[f'rest_{name}'], fields[f'velocity_{name}'], w,
                          fields['face_alpha'], domain.faces)
        rate = -rootf[:, None]*np.diff(flux, axis=0)/domain.volume[:, None]
        acceleration = alpha*rootf*fields['nu_r']
        rate[:, 0] += -acceleration*j-fields['log_a_t']*(e+pr)+sign*alpha*force_e
        shell_geometry = np.diff(domain.faces**2)/domain.volume
        rate[:, 1] += -acceleration*e+alpha*rootf*p*shell_geometry-2*fields['log_a_t']*j+sign*alpha*force_j
        result[:, offset:offset+2] = rate
        boundary_energy += flux[[0, -1], 0]
        density = fields[f'rest_{name}']**(1/(1+w))
        velocity = fields[f'velocity_{name}'][[0, -1]]
        velocity = np.array([min(velocity[0], 0.), max(velocity[1], 0.)])
        number_flux = fields['face_alpha'][[0, -1]]*domain.faces[[0, -1]]**2*density[[0, -1]]*velocity/np.sqrt(1-velocity*velocity)
        if name == 'n':
            boundary_particles = number_flux
        else:
            boundary_entropy = number_flux
    inner_mass_rate = -4*np.pi*np.sqrt(fields['face_f'][0])*boundary_energy[0]
    diagnostics = {'entropy_creation': gamma_s, 'boundary_particles': np.asarray(boundary_particles),
                   'boundary_entropy': np.asarray(boundary_entropy), 'boundary_energy': boundary_energy}
    return np.r_[result.ravel(), inner_mass_rate], fields, diagnostics


def conserved_integrals(domain, fields):
    measure = 4*np.pi*domain.volume/np.sqrt(fields['f'])
    n = fields['rest_n']**(1/(1+domain.w_n))
    s = fields['rest_s']**(1/(1+domain.w_s))
    return float(measure@(n*fields['gamma_n'])), float(measure@(s*fields['gamma_s']))


def timestep(domain, fields, relaxation, cfl=.3):
    speed = np.zeros(domain.cells)
    for name, w in [('n', domain.w_n), ('s', domain.w_s)]:
        v = abs(fields[f'velocity_{name}'])
        speed = np.maximum(speed, (v+np.sqrt(w))/(1+v*np.sqrt(w)))
    coordinate_speed = fields['alpha']*np.sqrt(fields['f'])*speed
    advective = cfl*np.min(np.diff(domain.faces)/coordinate_speed)
    force_scale = np.max(abs(fields['alpha']*np.sqrt(fields['f'])*fields['nu_r']))
    return min(float(advective), .08*relaxation/float(fields['alpha'].max()), .08/max(force_scale, 1e-30))


def evolve(domain, initial, relaxation, duration=4., snapshots=81, max_steps=30000, deadline=None):
    import time
    state, t = initial.copy(), 0.
    targets = np.linspace(0., duration, snapshots)
    times, histories, records = [], [], []
    escaped_n = escaped_s = created_s = escaped_mass = 0.
    first_n = first_s = first_mass = None
    steps = 0
    status = 'duration_completed'
    for target in targets:
        while t < target-1e-14:
            if deadline is not None and time.monotonic() > deadline:
                status = 'compute_budget_reached'
                break
            if steps >= max_steps:
                status = 'step_budget_reached'
                break
            base_rate, fields, diag = rhs(domain, state, relaxation)
            dt = min(timestep(domain, fields, relaxation), target-t)
            accepted = False
            for _ in range(12):
                try:
                    stage = state+dt*base_rate
                    stage_rate, stage_fields, stage_diag = rhs(domain, stage, relaxation)
                    candidate = .5*(state+stage+dt*stage_rate)
                    metric_and_fluids(domain, candidate)
                    accepted = True
                    break
                except EvolutionDomainError:
                    dt *= .5
            if not accepted or dt < 1e-10:
                status = 'polar_or_fluid_domain_limit'
                break
            for weight, ff, dd in [(.5, fields, diag), (.5, stage_fields, stage_diag)]:
                escaped_n += dt*weight*4*np.pi*np.diff(dd['boundary_particles'])[0]
                escaped_s += dt*weight*4*np.pi*np.diff(dd['boundary_entropy'])[0]
                created_s += dt*weight*4*np.pi*np.dot(domain.volume*ff['alpha']/np.sqrt(ff['f']), dd['entropy_creation'])
                escaped_mass += dt*weight*4*np.pi*np.sqrt(ff['face_f'][-1])*dd['boundary_energy'][-1]
            state = candidate
            t += dt
            steps += 1
        rate, fields, diag = rhs(domain, state, relaxation)
        number, entropy = conserved_integrals(domain, fields)
        if first_n is None:
            first_n, first_s, first_mass = number, entropy, fields['face_mass'][-1]
        times.append(t)
        histories.append({key: value.copy() for key, value in fields.items()})
        records.append({'time': t, 'steps': steps, 'min_f': float(min(fields['f'].min(), fields['face_f'].min())),
            'min_alpha': float(fields['alpha'].min()),
            'max_particle_speed': float(abs(fields['velocity_n']).max()),
            'max_entropy_speed': float(abs(fields['velocity_s']).max()),
            'max_relative_drift': float(abs((fields['velocity_s']-fields['velocity_n'])/(1-fields['velocity_s']*fields['velocity_n'])).max()),
            'min_rest_energy': float(min(fields['rest_n'].min(), fields['rest_s'].min())),
            'min_entropy_creation': float(diag['entropy_creation'].min()),
            'max_entropy_creation': float(diag['entropy_creation'].max()),
            'particle_number': number, 'entropy': entropy, 'created_entropy': created_s,
            'escaped_particles': escaped_n, 'escaped_entropy': escaped_s,
            'particle_balance_relative_error': (number+escaped_n-first_n)/first_n,
            'entropy_balance_relative_error': (entropy+escaped_s-first_s-created_s)/first_s,
            'outer_mass_balance_error': fields['face_mass'][-1]+escaped_mass-first_mass,
            'max_current': float(abs(fields['total_current']).max()),
            'max_mass_change': float(abs(fields['mass']-domain.reference_mass).max()),
            'min_radial_discriminant': float(((fields['total_energy']+fields['total_radial'])**2-4*fields['total_current']**2).min())})
        if status != 'duration_completed':
            break
    return {'status': status, 'time': np.asarray(times),
            'fields': {key: np.stack([h[key] for h in histories]) for key in histories[0]},
            'records': records, 'state': state, 'steps': steps}
