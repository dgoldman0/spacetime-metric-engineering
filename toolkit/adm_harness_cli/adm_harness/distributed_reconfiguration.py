"""Scheduled material duties and finite-distance work-transfer allowances.

The six material populations retain conserved reference inventories. A
whole-history field schedule replaces independent maximum-reserve choices.
Transport buffers obey a causal delay construction; their mechanical cost
is screened with ideal photon/string reaction pairs. Those reaction pairs
are a tensor-budget allowance, not a constitutive model of actual joints.
"""
from __future__ import annotations

import numpy as np

from .finite_containment import annular_factor
from .magnetic_load_balance import support_cone
from .material_reconfiguration import (
    MATERIAL_DIMENSIONS, PRESSURE_BASIS, elastic_state_from_tension,
    finite_ideal_allocation, inventory_for_minimum_stretch,
)


def lipschitz_interval_path(lower, upper, proper_time):
    """Minimum maximum slew through scalar intervals, independently per label.

    For a rate k, the lower Lipschitz envelope is max_j(lo_j-k*|t_i-t_j|).
    It fits exactly when it lies below every upper bound. Forward/backward
    cumulative extrema evaluate both envelopes in linear time. Their mean
    supplies a feasible schedule, including between linearly interpolated
    bounds. The schedule uses the prescribed history as a prepared command.
    """
    lo, hi, t = map(lambda a: np.asarray(a, float), (lower, upper, proper_time))
    if (lo.ndim != 2 or lo.shape != hi.shape or t.shape != lo.shape or len(t) < 2
            or not all(np.isfinite(a).all() for a in (lo, hi, t))
            or np.any(lo > hi) or np.any(np.diff(t, axis=0) <= 0)):
        raise ValueError("ordered finite intervals and increasing time per label required")
    t = t-t[:1]

    def envelopes(rate):
        kt = rate*t
        below = np.maximum(np.maximum.accumulate(lo+kt, axis=0)-kt,
            np.maximum.accumulate((lo-kt)[::-1], axis=0)[::-1]+kt)
        above = np.minimum(np.minimum.accumulate(hi-kt, axis=0)+kt,
            np.minimum.accumulate((hi+kt)[::-1], axis=0)[::-1]-kt)
        return below, above

    low = np.zeros(lo.shape[1])
    high = np.max(np.abs(np.diff((lo+hi)/2, axis=0))/np.diff(t, axis=0), axis=0)
    for _ in range(64):
        middle = (low+high)/2
        below, _ = envelopes(middle)
        fits = np.max(below-hi, axis=0) <= 0
        high, low = np.where(fits, middle, high), np.where(fits, low, middle)
    # The final outward rounding covers cancellation in the time envelopes.
    rate = high*(1+1e-11)+1e-14
    below, above = envelopes(rate)
    path = np.clip((below+above)/2, lo, hi)
    return dict(path=path, rate=rate, lower_rate_bracket=low,
                lower_envelope=below, upper_envelope=above)


def scheduled_replay(target, floor, inner_hoop, outer_hoop, proper_duration, *, eta=1.01,
                     inventory_fraction=.25, auxiliary_bias_fraction=.5,
                     retained_reserve_fraction=.1, field_fraction_floor=.001,
                     outer_sheet_fraction=1.):
    """Keep boundary roles engaged and minimize added-field slew.

    Inner hoop strings carry Hi. A fixed fraction of Ho-2*R*U goes to the
    outer sheet, with the remainder on strings. The default uses the sheet.
    The annular sheet carries R*U, and the auxiliary sheet
    retains a small tensile bias, offset by counted angular photons.

    A uniform energy allowance pays for all relaxed material, the maximum
    auxiliary bias cost, and a specified reserve. Eliminating the support
    cone gives an interval for U at every time. The field follows a minimum
    slew path through those intervals. Current hosts remain the inherited
    independent construction requirement.
    """
    T, f, hi, ho, dt = map(lambda a: np.asarray(a, float),
                          (target, floor, inner_hoop, outer_hoop, proper_duration))
    if (hi.ndim != 2 or ho.shape != hi.shape or f.shape != hi.shape
            or T.shape != (3,)+hi.shape or dt.shape != (hi.shape[0]-1, hi.shape[1])
            or not all(np.isfinite(a).all() for a in (T, f, hi, ho, dt))
            or not np.isfinite([inventory_fraction, auxiliary_bias_fraction,
                retained_reserve_fraction, field_fraction_floor, outer_sheet_fraction]).all()
            or np.any(hi < 0) or np.any(ho <= 0) or np.any(f < 0) or np.any(dt <= 0)
            or not 0 < inventory_fraction < 1 or auxiliary_bias_fraction < 0
            or not 0 < retained_reserve_fraction < 1 or not 0 < field_fraction_floor < .5
            or not 0 <= outer_sheet_fraction <= 1):
        raise ValueError("compatible finite histories and positive preparation parameters required")
    R, H = annular_factor(eta), hi+ho
    ideal = finite_ideal_allocation(T, f, hi, ho, eta=eta)
    reference_reserve = ideal["support"]["spare"].min(axis=0)
    if np.any(reference_reserve <= 0):
        raise ValueError("positive reference reserve required")
    total_inventory = inventory_fraction*reference_reserve
    bias = auxiliary_bias_fraction*total_inventory
    guaranteed_reserve = retained_reserve_fraction*reference_reserve
    margin = total_inventory+3*bias+guaranteed_reserve
    F = support_cone(*T, f)["facets"]
    a, c = np.maximum(F[0]+2*H, F[1]+H/2), F[2]+H/2
    cap, beta = ho/(2*R), outer_sheet_fraction
    upper_slope = 3-R+4*beta*R
    if upper_slope <= 0:
        raise ValueError("this interval construction requires positive upper-facet slope")
    lower = np.maximum(field_fraction_floor*cap, (a+beta*ho+margin)/(R*(1+2*beta)))
    upper = np.minimum((1-field_fraction_floor)*cap, (2*beta*ho-c-margin)/upper_slope)
    if np.any(lower > upper):
        raise ValueError("prepared role shares exceed the field interval")
    tau = np.concatenate([np.zeros_like(dt[:1]), np.cumsum(dt, axis=0)])
    schedule = lipschitz_interval_path(lower, upper, tau)
    U = schedule["path"]
    outer = ho-2*R*U
    assembly = np.stack([H+(1-R)*U, U-beta*outer, -H/2])
    support = support_cone(*(T-assembly), f)
    auxiliary = np.maximum(support["membrane"], bias)
    bias_increment = auxiliary-support["membrane"]
    tension = np.stack([np.zeros_like(hi), hi, beta*outer, (1-beta)*outer, R*U, auxiliary])
    inventory = inventory_for_minimum_stretch(tension.max(axis=1), total_inventory)["inventory"]
    eps = np.where(MATERIAL_DIMENSIONS == 2, .1, 0.)[:, None, None]
    law = elastic_state_from_tension(tension, inventory[:, None], shear_fraction=eps)
    fields = np.stack([U, support["field"], support["radial_wave"],
                       support["angular_wave"]+2*bias_increment])
    reserve = T[0]-law["energy"].sum(axis=0)-fields.sum(axis=0)
    energy = np.concatenate([law["energy"], fields, reserve[None]])
    stress_weights = np.concatenate([tension, fields, reserve[None]])
    pressure = PRESSURE_BASIS[:, :, None, None]*stress_weights[None]
    tensor = np.stack([energy.sum(axis=0), pressure[0].sum(axis=0), pressure[1].sum(axis=0)/2])
    return dict(target=T, material_tension=tension, inventory=inventory, law=law,
                component_energy=energy, component_pressure=pressure,
                remaining_reserve=reserve, guaranteed_reserve=guaranteed_reserve,
                reconstructed_tensor=tensor, field_energy=U, field_lower=lower,
                field_upper=upper, field_slew=schedule["rate"], proper_time=tau,
                auxiliary_bias=bias, reference_reserve=reference_reserve)


def instantaneous_exchange_power(replay, lr, lt, proper_duration, fraction):
    """True power along linear duties/fields and log-linear macro stretches.

    Elastic energy follows its fixed nonlinear law. The final node is the
    complementary rail port. Each evaluated set of powers sums to zero.
    """
    u = np.asarray(fraction)
    if np.any(u < 0) or np.any(u > 1):
        raise ValueError("panel fraction must lie in [0,1]")
    tension, M = replay["material_tension"], replay["inventory"]
    energy, pressure, target = (replay[k] for k in ("component_energy", "component_pressure", "target"))
    dt = np.asarray(proper_duration)
    dz, da = np.diff(np.log(lr), axis=0)/dt, np.diff(np.log(lt), axis=0)/dt
    T = (1-u)*tension[:, :-1]+u*tension[:, 1:]
    dT = np.diff(tension, axis=1)/dt
    eps = np.where(MATERIAL_DIMENSIONS == 2, .1, 0.)[:, None, None]
    material_derivative = dT*T/np.hypot(T, (1-eps)*M[:, None])
    P = (1-u)*pressure[:, :, :-1]+u*pressure[:, :, 1:]
    derivative = np.diff(energy[6:10], axis=1)/dt
    rho_derivative = np.diff(target[0], axis=0)/dt
    dust_derivative = rho_derivative-material_derivative.sum(axis=0)-derivative.sum(axis=0)
    rates = np.concatenate([material_derivative, derivative, dust_derivative[None]])
    rates += P[0]*dz+P[1]*da
    p = (1-u)*target[1, :-1]+u*target[1, 1:]
    q = (1-u)*target[2, :-1]+u*target[2, 1:]
    rail = -rho_derivative-p*dz-2*q*da
    return np.concatenate([rates, rail[None]])


def exchange_power_bounds(replay, lr, lt, proper_duration):
    """Exact extrema of component power on every prescribed replay panel.

    Material power has the form a*T/hypot(T,s)-b*T. Besides its endpoints,
    its sole possible stationary point satisfies (T*T+s*s)**(3/2)=a*s*s/b.
    Field and rail powers are affine. Dust power decreases because elastic
    energy is convex, so its two endpoint values also bound the whole panel.
    """
    dt = np.asarray(proper_duration)
    endpoints = [instantaneous_exchange_power(replay, lr, lt, dt, u) for u in (0., 1.)]
    lower, upper = np.minimum(*endpoints), np.maximum(*endpoints)
    tension, M = replay["material_tension"], replay["inventory"]
    a = np.diff(tension, axis=1)/dt
    dz, da = np.diff(np.log(lr), axis=0)/dt, np.diff(np.log(lt), axis=0)/dt
    b = -(PRESSURE_BASIS[0, :6, None, None]*dz+PRESSURE_BASIS[1, :6, None, None]*da)
    s = np.where(MATERIAL_DIMENSIONS[:, None] == 2, .9, 1.)*M
    ratio = np.divide(a*s[:, None]**2, b, out=np.zeros_like(a), where=b != 0)
    root_squared = np.cbrt(ratio)**2-s[:, None]**2
    star = np.sqrt(np.maximum(root_squared, 0.))
    valid = ((ratio > 0) & (root_squared >= 0)
             & (star >= np.minimum(tension[:, :-1], tension[:, 1:]))
             & (star <= np.maximum(tension[:, :-1], tension[:, 1:])))
    value = a*star/np.hypot(star, s[:, None])-b*star
    lower[:6] = np.where(valid, np.minimum(lower[:6], value), lower[:6])
    upper[:6] = np.where(valid, np.maximum(upper[:6], value), upper[:6])
    return dict(lower=lower, upper=upper,
                endpoint_balance_error=max(float(np.max(np.abs(e.sum(axis=0)))) for e in endpoints))


def transport_capacity(positive_power_bound, maximum_delay):
    """Sufficient fixed reception inventory for arbitrary delays <= tau.

    If A_i is the instantaneous receipt in a zero-delay reciprocal routing,
    B_i=C_i-outstanding_i remains nonnegative for C_i=tau*sup(A_i).
    Buffers plus energy in flight sum to sum(C_i); the in-flight energy is
    not added a second time. Reaction stresses are accounted separately.
    """
    power, delay = np.asarray(positive_power_bound), np.asarray(maximum_delay)
    if (power.ndim != 3 or delay.shape != power.shape[2:]
            or not np.isfinite(power).all() or not np.isfinite(delay).all()
            or np.any(delay < 0)):
        raise ValueError("component/panel/label power bounds and nonnegative label delays required")
    peaks = np.maximum(power.max(axis=1), 0.)
    capacity = peaks*delay
    return dict(node_capacity=capacity, total_capacity=capacity.sum(axis=0),
                node_positive_power_peak=peaks)


def joint_transport_envelope(tension, reception_capacity, attachment_fraction):
    """Conditional energy ceiling for ideal joints and isotropic transit.

    An extra joint length h per loaded side d has h/d=zeta and tensile
    energy zeta*T for each material direction. All these new ties are
    counted separately. Transit radiation of energy u<=C has axial and
    transverse-trace stresses u/3 and 2u/3. Reuse those stresses against
    the joints, adding ideal photons/strings for only the remaining signed
    stresses. Their energy is |Jz-u/3|+|Jt-2u/3|.

    Reception buffers plus photons in flight cost C together. The maximum
    package energy occurs at u=0 or u=C. This supplies a diagonal tensor
    allowance with unit-strength ideal ties; finite geometry, their fixed
    material inventories, actuators, optics and binding costs remain open.
    """
    T, C, zeta = np.asarray(tension), np.asarray(reception_capacity), np.asarray(attachment_fraction)
    if (T.ndim != 3 or T.shape[0] != 6 or C.shape != T.shape[2:]
            or not all(np.isfinite(a).all() for a in (T, C, zeta))
            or np.any(T < 0) or np.any(C < 0) or np.any(zeta < 0)):
        raise ValueError("six tensile histories, nonnegative capacities and attachment fraction required")
    axial = zeta*(T[0]+T[2])
    transverse = zeta*(T[0]+T[1]+T[2]+T[3]+2*T[4]+2*T[5])
    joint = axial+transverse
    mismatch = np.abs(axial-C/3)+np.abs(transverse-2*C/3)
    overhead = C+joint+np.maximum(joint, mismatch)
    return dict(energy_ceiling=overhead, axial_joint_tension=axial,
                transverse_joint_tension=transverse,
                separate_package_ceiling=2*C+2*joint)
