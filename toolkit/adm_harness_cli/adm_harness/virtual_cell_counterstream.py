"""Required exchange of a counted, current-cancelling radial null stream.

The exchange belongs to the counterstream's partner. It is not a new net
four-force on the complete backing tensor, whose assigned current stays zero.
"""
from __future__ import annotations

import numpy as np


def derivatives(values, times, positions, split=None):
    values = np.asarray(values)
    dt = np.gradient(values, times, axis=0, edge_order=2)
    dx = np.empty_like(values)
    edges = (0, len(positions)) if split is None else (0, int(split), len(positions))
    for left, right in zip(edges[:-1], edges[1:]):
        dx[:, left:right] = np.gradient(values[:, left:right], positions[left:right],
                                        axis=1, edge_order=2)
    return dt, dx


def material_kinematics(g):
    """Material worldlines are x=constant; g includes alpha_t and beta_t."""
    v = g['b']*g['beta']/g['alpha']
    gamma = 1/np.sqrt(1-v*v)
    lapse = g['alpha']/gamma
    ell = gamma*g['b']
    vt = v*(g['logb_t']-g['alpha_t']/g['alpha'])+g['b']*g['beta_t']/g['alpha']
    kl = (g['beta_x']+g['beta']*g['logb_x']-g['logb_t'])/g['alpha']
    acceleration = gamma*(gamma*gamma*vt/g['alpha']+
                          g['alpha_x']/(g['alpha']*g['b'])-v*kl)
    angular_gradient = g['logr_x']/ell+v*g['logr_t']/lapse
    log_ell_t = g['logb_t']+gamma*gamma*v*vt
    return dict(v=v, gamma=gamma, lapse=lapse, ell=ell,
                theta_r=log_ell_t/lapse, theta_t=g['logr_t']/lapse,
                acceleration=acceleration, angular_gradient=angular_gradient)


def tetrad_exchange(energy, current, times, positions, g, split=None):
    """P=-u.div(T), F=s.div(T), with rho=p_r=energy and p_t=0."""
    c = material_kinematics(g)
    et, ex = derivatives(energy, times, positions, split)
    jt, jx = derivatives(current, times, positions, split)
    theta = c['theta_r']+c['theta_t']
    curvature = c['acceleration']+c['angular_gradient']
    power = (et/c['lapse']+2*theta*energy+jx/c['ell']+
             c['v']*jt/c['lapse']+2*curvature*current)
    force = (ex/c['ell']+c['v']*et/c['lapse']+2*curvature*energy+
             jt/c['lapse']+2*theta*current)
    return power, force


def directional_adm_exchange(energy, current, times, positions, g, split=None):
    """Independent conservative directional ADM transport residual.

Y_sigma=B R^2 c_sigma/[Gamma^2(1-sigma*v)^2]. Its equation is
Y_t + ([-beta+sigma*alpha/B] Y)_x - gain_sigma Y = source.
The returned source is projected into the same material frame as above.
"""
    k = material_kinematics(g)
    volume = g['b']*g['radius']**2
    kl = (g['beta_x']+g['beta']*g['logb_x']-g['logb_t'])/g['alpha']
    sources = []
    for sign in (1., -1.):
        density = (energy+sign*current)/2
        y = volume*density/(k['gamma']**2*(1-sign*k['v'])**2)
        speed = -g['beta']+sign*g['alpha']/g['b']
        gain = g['alpha']*kl-sign*g['alpha_x']/g['b']
        yt = derivatives(y, times, positions, split)[0]
        flux_x = derivatives(speed*y, times, positions, split)[1]
        residual = yt+flux_x-gain*y
        sources.append(k['gamma']*(1-sign*k['v'])*residual/(g['alpha']*volume))
    return sources[0]+sources[1], sources[0]-sources[1]


def minimal_counterstream(absorption, returned, direction):
    wave_current = np.asarray(direction)*(np.asarray(absorption)-np.asarray(returned))
    return np.abs(wave_current), -wave_current


def passive_scattering_rate(energy, current, power, force, tolerance=1e-10):
    """Necessary conditions for symmetric, material-frame elastic scattering.

For finite kappa>=0, S_+=kappa(c_--c_+), S_-=-S_+, hence P=0,
F=-2*kappa*j. At j=0 require F=0; the rate is then undetermined.
Strictly minimal current cancellation has one populated null direction.
There P=0 implies F=0, so a nonzero elastic scattering completion requires
additional counterpropagating inventory and a new component-budget check.
"""
    energy, current, power, force = np.broadcast_arrays(energy, current, power, force)
    rate = np.full_like(power, np.nan, dtype=float)
    moving = np.abs(current)>tolerance
    rate[moving] = -force[moving]/(2*current[moving])
    allowed = ((np.abs(power)<=tolerance) & (energy>=np.abs(current)-tolerance) &
               np.where(moving, rate>=-tolerance, np.abs(force)<=tolerance))
    return rate, allowed


def passive_total_radiation_interval(absorption, returned, density, radial,
                                      angular, core, ell, radius,
                                      integrated_phase_work):
    """All zero-power counterstreams with arbitrary prepared spatial grading.

Explicit drive/work/heat waves obey P_wave=-A_t/(N R^2). With j_counter
equal to -j_wave and P_counter=0, total radial radiation W obeys
[(ell R)^2 W]_t=-ell^2 A_t. Thus W=(C-I)/(ell R)^2, where I is the
supplied integral of ell^2 A_t from the initial time. The full component
cone gives W<= (rho+2*p_r+p_t+core)/3. Nonnegative directional counter
populations give W>=2*max(absorption,returned). No finite-rate scattering
law, guide construction or auxiliary force law is supplied by this test.
"""
    arrays = np.broadcast_arrays(absorption, returned, density, radial, angular,
                                core, ell, radius, integrated_phase_work)
    ua, ur, rho, pr, pt, s, length, r, work = arrays
    if ua.ndim != 2 or np.any(length<=0) or np.any(r<=0):
        raise ValueError('positive geometry and two-dimensional time/space arrays required')
    measure = (length*r)**2
    low = 2*np.maximum(ua, ur)
    high = (rho+2*pr+pt+s)/3
    lower_history = work+measure*low
    upper_history = work+measure*high
    lower = lower_history.max(axis=0)
    upper = upper_history.min(axis=0)
    zero_inventory_lower = work.max(axis=0)
    total = (lower[None, :]-work)/measure
    shortfall = np.maximum(total-high, 0.).max(axis=0)
    return dict(initial_constant_lower=lower, initial_constant_upper=upper,
        lower_witness_index=lower_history.argmax(axis=0),
        upper_witness_index=upper_history.argmin(axis=0),
        constant_interval_gap=lower-upper, radiation_density_shortfall=shortfall,
        zero_inventory_constant_lower=zero_inventory_lower,
        zero_inventory_lower_witness_index=work.argmax(axis=0),
        zero_inventory_constant_gap=zero_inventory_lower-upper,
        total_radiation=total, counter_density=total-ua-ur,
        instantaneous_lower=low, instantaneous_upper=high)
