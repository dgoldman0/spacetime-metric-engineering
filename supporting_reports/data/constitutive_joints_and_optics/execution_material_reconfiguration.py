"""Conserved elastic constituents with driven internal reconfiguration.

The reference material remains fixed; its strain energy and orientation
may change. Each tensile duty is supplied by its own elastic constituent,
including the auxiliary angular membrane already in the support budget.
Current hosts and end fixtures remain separate finite-construction gates.

The membrane law uses the isotropically strained rigid-membrane family of
Mourao, Natario and Vicente, arXiv:2409.10602v2, equations 84--88. Parameter
J is proper area/reference area (length ratio for the rigid string law).
This module constructs an inverse driven material history. It does not
solve the embedding, junction forces, or kinetic actuator tensor.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import linprog

from .finite_containment import allocate_field, annular_factor
from .magnetic_load_balance import support_cone


MATERIAL_NAMES = ("inner_longitudinal_sheet", "inner_hoop_string",
                  "outer_longitudinal_sheet", "outer_hoop_string",
                  "annular_transverse_sheet", "auxiliary_transverse_sheet")
COMPONENT_NAMES = MATERIAL_NAMES+(
    "hoop_maxwell", "radial_maxwell", "radial_photons", "angular_photons", "remaining_inventory")
# Pressures are multiplied by tensile duty for materials and energy for fields.
PRESSURE_BASIS = np.array([[-1., 0., -1., 0., 0., 0., 1., -1., 1., 0., 0.],
                           [-1., -1., -1., -1., -2., -2., 0., 2., 0., 1., 0.]])
MATERIAL_DIMENSIONS = np.array([2, 1, 2, 1, 2, 2])


def isometric_pool_bounds(target, floor):
    """Exact relaxed quasistatic bounds for freely oriented tensile pools.

    Grant arbitrary sheet/string orientation, redistribution between all
    duties, and the existing Maxwell/photon/dust support cone. Finite hoop
    and interface restrictions are omitted. If A is sheet energy, K string
    energy, and P=p+2q, eliminating the orientations gives
      2A+K >= max(2(f-q), f-P, 0),
      3A+2K >= max(-2(p+q), 0),   3A+2K <= rho-P.
    Sheets are the most efficient choice for this relaxed problem. Thus an
    all-sheet pool has the interval below, and no fixed A,K mixture works
    through a history when max(lower)>min(upper). The law grants zero cost
    to rotation and transport; relativistic moving-material stress needs a
    separate analysis.
    """
    rho, p, q = np.asarray(target, float)
    f = np.broadcast_to(floor, rho.shape)
    lower = np.maximum.reduce([f-q, .5*(f-p-2*q), -2*(p+q)/3, np.zeros_like(p)])
    upper = (rho-p-2*q)/3
    return dict(lower=lower, upper=upper)


def isometric_pool_program(target, floor):
    """Independent LP keeps orientations and support components at each time.

    A and K are fixed throughout the supplied history. Per-time variables
    are longitudinal/transverse sheets, axial/transverse strings, radial B,
    axial/angular photons, and dust. It grants every material all duties.
    """
    T = np.asarray(target, float)
    if T.ndim != 2 or T.shape[0] != 3:
        raise ValueError("target must contain one label's time history")
    n = T.shape[1]
    f = np.broadcast_to(floor, (n,))
    basis = np.array([[1., 1., 1., 1., 1., 1., 1., 1.],
                      [-1., 0., -1., 0., -1., 1., 0., 0.],
                      [-.5, -1., 0., -.5, 1., 0., .5, 0.]])
    eq = np.zeros((5*n, 2+8*n))
    rhs = np.zeros(5*n)
    bounds = [(0., None), (0., None)]
    for i in range(n):
        start = 2+8*i
        eq[5*i:5*i+3, start:start+8] = basis
        rhs[5*i:5*i+3] = T[:, i]
        eq[5*i+3, [0, start, start+1]] = [-1, 1, 1]
        eq[5*i+4, [1, start+2, start+3]] = [-1, 1, 1]
        bounds.extend([(0., None)]*4+[(float(f[i]), None)]+[(0., None)]*3)
    objective = np.r_[3., 2., np.zeros(8*n)]
    return linprog(objective, A_eq=eq, b_eq=rhs, bounds=bounds, method="highs")


def finite_ideal_allocation(target, floor, inner_hoop, outer_hoop, *, eta=1.01):
    """Exact finite-interface max-reserve allocation with free new hosts.

    After eliminating longitudinal sheet duty W, the optimum shortfall at
    fixed U is max(a-RU, (2a+c)/3+(1-R)U, c-2H+3(1+R)U).
    R>1 makes the first two terms decreasing and the last increasing. Check
    their intersections and both endpoints over 0<=U<=Ho/(2R).
    """
    F = support_cone(*np.asarray(target), floor)["facets"]
    hi, ho = np.asarray(inner_hoop), np.asarray(outer_hoop)
    H, R = hi+ho, annular_factor(eta)
    a, c, cap = np.maximum(F[0]+2*H, F[1]+H/2), F[2]+H/2, ho/(2*R)
    choices = np.stack([np.zeros_like(H), cap,
        np.clip((a-c+2*H)/(3+4*R), 0, cap),
        np.clip((a-c+3*H)/(3+6*R), 0, cap)])
    scores = np.maximum.reduce([a-R*choices, (2*a+c)/3+(1-R)*choices,
                                 c-2*H+3*(1+R)*choices])
    index = np.argmin(scores, axis=0)[None]
    U = np.take_along_axis(choices, index, axis=0)[0]
    result = allocate_field(target, floor, hi, ho, U, eta=eta)
    return dict(field_energy=U, **result)


def elastic_state_from_tension(tension_energy, relaxed_energy, *, shear_fraction=0.):
    """Invert a single fixed constitutive law, preserving relaxed inventory.

    For a sheet with epsilon in (0,1), E=M/2*((1-epsilon)*(J+1/J)+2epsilon),
    T=M/2*(1-epsilon)*(J-1/J), J>=1. The string law is the epsilon=0
    one-dimensional analogue. E(1)=M and dE/d(log J)=T. Sheet sound speeds
    here apply to an isotropically strained patch, not the assembled device.
    """
    T, M, eps = np.broadcast_arrays(*map(lambda x: np.asarray(x, float),
                                       (tension_energy, relaxed_energy, shear_fraction)))
    if (not all(np.isfinite(x).all() for x in (T, M, eps)) or np.any(T < 0)
            or np.any(M <= 0) or np.any(eps < 0) or np.any(eps >= 1)):
        raise ValueError("nonnegative tension, positive inventory, and 0<=epsilon<1 required")
    scale = (1-eps)*M
    root = np.hypot(T, scale)
    logJ = np.arcsinh(T/scale)
    E = root+eps*M
    return dict(energy=E, log_strain=logJ, strain=np.exp(logJ),
                tension=T, relaxed_energy=M,
                out_of_plane_speed_squared=T/E,
                longitudinal_speed_squared=np.ones_like(E),
                in_plane_shear_speed_squared=eps/(eps+(1-eps)*np.exp(-logJ)))


def elastic_state_from_strain(strain, relaxed_energy, *, shear_fraction=0.):
    J, M, eps = np.broadcast_arrays(strain, relaxed_energy, shear_fraction)
    if (not all(np.isfinite(x).all() for x in (J, M, eps)) or np.any(J < 1)
            or np.any(M <= 0) or np.any(eps < 0) or np.any(eps >= 1)):
        raise ValueError("tensile strains J>=1 and positive relaxed energy required")
    E = .5*M*((1-eps)*(J+1/J)+2*eps)
    T = .5*M*(1-eps)*(J-1/J)
    return dict(energy=E, tension=T)


def inventory_for_minimum_stretch(peak_tension, total_inventory, *, sheet_shear_fraction=.1,
                                  minimum_fraction=1e-6):
    """Minimize the largest proper linear stretch over the whole ensemble.

    At a common linear-stretch cap L, a d-dimensional constituent needs
    M>=2*Tmax/((1-epsilon)*(L**d-L**(-d))). The required inventory decreases
    monotonically with L; bisection gives the optimal cap for a fixed total.
    A small positive floor also prepares unloaded roles. Allocation is made
    once before the replay, and each resulting inventory stays conserved.
    """
    peak, total = np.asarray(peak_tension, float), np.asarray(total_inventory, float)
    if (peak.shape != (6,)+total.shape or not np.isfinite(peak).all()
            or not np.isfinite(total).all() or np.min(peak) < 0 or np.min(total) <= 0
            or not 0 < minimum_fraction < 1/6 or not 0 < sheet_shear_fraction < 1):
        raise ValueError("six nonnegative peak duties, positive budget and valid inventory floor required")
    dims = MATERIAL_DIMENSIONS.reshape((6,)+(1,)*total.ndim)
    eps = np.where(dims == 2, sheet_shear_fraction, 0.)
    def required(stretch):
        denominator = (1-eps)*2*np.sinh(dims*np.log(stretch))
        amount = np.divide(2*peak, denominator, out=np.full_like(peak, np.inf), where=denominator > 0)
        amount = np.where(peak == 0, 0., amount)
        return np.maximum(minimum_fraction*total, amount)
    low, high = np.ones_like(total), np.full_like(total, 2.)
    for _ in range(100):
        insufficient = required(high).sum(axis=0) > total
        if not insufficient.any():
            break
        high = np.where(insufficient, 2*high, high)
    else:
        raise ValueError("Unable to bracket the material stretch")
    for _ in range(72):
        middle = .5*(low+high)
        insufficient = required(middle).sum(axis=0) > total
        low = np.where(insufficient, middle, low)
        high = np.where(insufficient, high, middle)
    return dict(inventory=required(high), linear_stretch_cap=high)


def elastic_replay(target, floor, inner_hoop, outer_hoop, *, eta=1.01,
                   reserve_fraction=.25, sheet_shear_fraction=.1, inventory_policy="balanced_stretch"):
    """Count six fixed relaxed inventories and construct their strain states.

    A quarter (by default) of each label's minimum ideal reserve is prepared
    as relaxed material energy. The six inventories remain fixed. For each
    constituent 0<=E-T<=M, so the total surcharge is bounded by this single
    reserved amount, even at zero load. Pressure duties are retained exactly.
    This is a conditional material replay with free added field hosts.
    """
    if not 0 < reserve_fraction < 1 or not 0 < sheet_shear_fraction < 1:
        raise ValueError("reserve and sheet shear fractions must lie in (0,1)")
    ideal = finite_ideal_allocation(target, floor, inner_hoop, outer_hoop, eta=eta)
    minimum = np.min(ideal["support"]["spare"], axis=0)
    if np.min(minimum) <= 0:
        raise ValueError("positive ideal reserve required for the driven material construction")
    tension = np.concatenate([ideal["components"][:5], ideal["support"]["membrane"][None]])
    # Surface decomposition can produce signed rounding at an exactly empty role.
    if np.min(tension) < -1e-12:
        raise ValueError("negative material duty")
    tension = np.maximum(tension, 0.)
    if inventory_policy == "balanced_stretch":
        inventory = inventory_for_minimum_stretch(tension.max(axis=1), reserve_fraction*minimum,
            sheet_shear_fraction=sheet_shear_fraction)["inventory"]
    elif inventory_policy == "equal":
        inventory = np.broadcast_to(reserve_fraction*minimum/6, (6,)+minimum.shape).copy()
    else:
        raise ValueError("unknown initial material allocation policy")
    eps = np.where(MATERIAL_DIMENSIONS == 2, sheet_shear_fraction, 0.)[:, None, None]
    law = elastic_state_from_tension(tension, inventory[:, None], shear_fraction=eps)
    surcharge = (law["energy"]-tension).sum(axis=0)
    spare = ideal["support"]["spare"]-surcharge
    field_parts = np.stack([ideal["field_energy"], ideal["support"]["field"],
        ideal["support"]["radial_wave"], ideal["support"]["angular_wave"], spare])
    energy = np.concatenate([law["energy"], field_parts])
    stress_weights = np.concatenate([tension, field_parts])
    pressures = PRESSURE_BASIS[:, :, None, None]*stress_weights[None]
    tensor = np.stack([energy.sum(axis=0), pressures[0].sum(axis=0), pressures[1].sum(axis=0)/2])
    return dict(ideal=ideal, material_tension=tension, inventory=inventory, law=law,
                component_energy=energy, component_pressure=pressures,
                reconstructed_tensor=tensor, remaining_reserve=spare,
                material_surcharge=surcharge)


def configuration_coordinates(log_strain, lr, lt):
    """Internal strains beyond the rail's affine motion, by constituent.

    Each sheet patch is locally isotropic: its two proper stretches equal
    sqrt(J). Internal anchor motion supplies the difference from the macro
    stretches. Strings have one stretch J. Zero second coordinate for strings.
    """
    logJ = np.asarray(log_strain)
    if logJ.shape != (6,)+np.asarray(lr).shape or np.asarray(lt).shape != np.asarray(lr).shape:
        raise ValueError("six material strain histories and matching macro stretches required")
    q = np.zeros((6, 2)+np.asarray(lr).shape)
    for i, dimension in enumerate(MATERIAL_DIMENSIONS):
        if dimension == 1:
            q[i, 0] = logJ[i]-np.log(lt)
        else:
            q[i, 0] = .5*logJ[i]-np.log(lr if i in (0, 2) else lt)
            q[i, 1] = .5*logJ[i]-np.log(lt)
    return q


def configuration_rate_bound(tension, inventory, lr, lt, proper_duration, *, sheet_shear_fraction=.1):
    """Maximum internal logarithmic strain rate on each replay panel.

    T varies linearly in panel proper time, while macro stretches vary
    log-linearly. Then d(log J)/dt=dot(T)/hypot(T,(1-epsilon)M).
    Every anchor-rate vector is affine in this monotone scalar, so its
    norm reaches its maximum at an endpoint. A rectangular patch with
    current side lengths <=d has a corner control-speed bound d*rate/2.
    This is local kinematics; the moving-body tensor and spatial joining
    of those patches require a subsequent embedding calculation.
    """
    T, M, dt = np.asarray(tension), np.asarray(inventory), np.asarray(proper_duration)
    if (T.shape != (6,)+np.asarray(lr).shape or np.asarray(lt).shape != np.asarray(lr).shape
            or M.shape != (6, T.shape[-1]) or dt.shape != (T.shape[1]-1, T.shape[2])
            or not all(np.isfinite(x).all() for x in (T, M, dt, lr, lt))
            or np.min(dt) <= 0 or np.min(M) <= 0 or np.min(T) < 0
            or np.min(lr) <= 0 or np.min(lt) <= 0 or not 0 < sheet_shear_fraction < 1):
        raise ValueError("compatible material, inventory, geometry and positive proper-time panels required")
    eps = np.where(MATERIAL_DIMENSIONS == 2, sheet_shear_fraction, 0.)[:, None, None]
    dT = np.diff(T, axis=1)/dt
    macro_z = np.diff(np.log(lr), axis=0)/dt
    macro_t = np.diff(np.log(lt), axis=0)/dt
    result = np.zeros_like(dT)
    for endpoint in (T[:, :-1], T[:, 1:]):
        dlogJ = dT/np.hypot(endpoint, (1-eps)*M[:, None])
        for i, dim in enumerate(MATERIAL_DIMENSIONS):
            if dim == 1:
                norm = abs(dlogJ[i]-macro_t)
            else:
                first = .5*dlogJ[i]-(macro_z if i in (0, 2) else macro_t)
                second = .5*dlogJ[i]-macro_t
                norm = np.hypot(first, second)
            result[i] = np.maximum(result[i], norm)
    return result


def reciprocal_routes(component_exchange):
    """Route panel energy between named nodes and the retained rail port.

    Positive Q means energy received. The final node is the complementary
    rail subsystem, whose required exchange is -sum(Q). A deterministic
    donor/receiver match counts each transfer once. The returned gross
    matrix is integrated over time; its transpose is the reciprocal flow.
    Hardware, conversion efficiency and power limits remain separate gates.
    """
    Q = np.asarray(component_exchange, float)
    if Q.ndim != 3 or not np.isfinite(Q).all():
        raise ValueError("finite component/panel/label exchanges required")
    rail = -Q.sum(axis=0)
    all_Q = np.concatenate([Q, rail[None]])
    need, supply = np.maximum(all_Q, 0.).copy(), np.maximum(-all_Q, 0.).copy()
    totals = np.zeros((len(all_Q), len(all_Q), all_Q.shape[-1]))
    largest = 0.
    for donor in range(len(all_Q)):
        for receiver in range(len(all_Q)):
            flow = np.minimum(supply[donor], need[receiver])
            supply[donor] -= flow
            need[receiver] -= flow
            totals[donor, receiver] = flow.sum(axis=0)
            largest = max(largest, float(np.max(flow)))
    return dict(rail_exchange=rail, transfer_totals=totals,
                maximum_unmatched_exchange=float(max(supply.max(), need.max())),
                maximum_panel_transfer=largest)
