"""Two-boundary magnetic jackets for the radial capsule reservoir.

The plasma core has radius r; a magnetic annulus extends to eta*r. Inner
and annular magnetic pressures are b and e times the reference field's
pressure. Both fields use the previously defined closed affine capsule.
Straight legs are radial and lambda_r <= lambda_t, so their reference
magnetic pressure equals the plasma pressure. The selected exterior
pressure e=1+b unloads the inner interface. The outer reaction is counted.

This module supplies a necessary straight-section material comparison.
It includes all loop field/current integrals, while bend mechanical
equilibrium and a microscopic shared phase field remain separate tasks.
"""
from __future__ import annotations

import numpy as np


def jacket_requirements(energy, volume, *, aspect, inner_pressure,
                        outer_pressure, radius_ratio):
    """Signed interface loads and their total hoop energy floor.

    The pressures at the two cylindrical interfaces, divided by plasma
    pressure, are 1+b-e and e. Their transverse virial weights are 1 and
    eta**2. The stored magnetic energy factor is b+e*(eta**2-1).
    e<=1+b keeps both required hoop stresses tensile. Their fixed ratio
    permits an exact split of a conserved total sleeve inventory.
    """
    E, D = np.broadcast_arrays(np.asarray(energy, float), np.asarray(volume, float))
    b, e, eta = inner_pressure, outer_pressure, radius_ratio
    if (E.ndim != 2 or not np.isfinite([aspect, b, e, eta]).all()
            or not np.isfinite(E).all() or not np.isfinite(D).all()
            or np.any(E <= 0) or np.any(D <= 0) or aspect <= 0
            or b < 0 or not 0 <= e <= 1+b or eta < 1
            or (e > 0 and eta <= 1)):
        raise ValueError("positive histories and a finite non-overcompressed jacket required")
    unit_hoop = 2*E/(3*D*(1+np.pi*aspect))
    inner = unit_hoop*(1+b-e)
    outer = unit_hoop*eta**2*e
    return dict(inner_hoop=inner, outer_hoop=outer, total_hoop=inner+outer,
                inner_pressure_ratio=1+b-e, outer_pressure_ratio=e,
                field_energy_factor=b+e*(eta*eta-1),
                inner_inventory_fraction=(1+b-e)/(1+b+e*(eta*eta-1)))


def straight_sheet_fraction(energy, volume, radial_stretch, transverse_stretch,
                            reference, *, aspect=.01, fill_fraction=.1):
    """Fraction of sheet carriers on radial straight legs at uniform drift."""
    E, D, lr, lt = map(lambda v: np.asarray(v, float),
                       (energy, volume, radial_stretch, transverse_stretch))
    L, r = reference["initial_leg"], reference["initial_tube_radius"]
    V0 = fill_fraction*D[0]
    amplitude = np.sqrt(2*E*lr*lt*lt/(3*V0*np.minimum(lr*lr, lt*lt)))
    current = 4*amplitude*V0*L*lr/(r*(2*L*(1+np.pi*aspect))*lt)
    fraction = current/reference["sheet_current_integral"]
    if not np.isfinite(fraction).all() or np.any((fraction < 0) | (fraction > 1+1e-12)):
        raise ValueError("inconsistent radial straight-section current reference")
    return fraction


def jacket_currents(reference, volume, *, inner_pressure, outer_pressure,
                     radius_ratio, straight_fraction, aspect=.01, tube_ratio=.1):
    """All inner/outer sheets and both core/annular bend-current families.

    Reference integrals use the original r/a and half-cell radial span.
    Changing the outer radius slightly shortens L to retain that span.
    A sheet scales with field jump times radius, and bend volume current
    with field times cross-sectional area. Same-direction fields minimize
    the inner sheet current; its absolute jump is retained.
    Every family uses its own conserved sqrt(2)*max_t integrated current.
    """
    D = np.asarray(volume, float)
    straight = np.asarray(straight_fraction, float)
    b, e, eta = inner_pressure, outer_pressure, radius_ratio
    if (D.ndim != 2 or not np.isfinite(D).all() or np.any(D <= 0)
            or not np.isfinite([b, e, eta, aspect, tube_ratio]).all()
            or min(b, e) < 0 or eta < 1 or aspect <= 0
            or not 0 < tube_ratio < 1 or eta*tube_ratio >= 1
            or straight.shape != D.shape or not np.isfinite(straight).all()
            or np.any((straight < 0) | (straight > 1))):
        raise ValueError("physical jacket and current reference required")
    span_factor = (1+2*aspect*(1+eta*tube_ratio))/(1+2*aspect*(1+tube_ratio))
    factors = (abs(np.sqrt(e)-np.sqrt(b)), eta*np.sqrt(e),
               np.sqrt(b), (eta*eta-1)*np.sqrt(e))
    tensor = np.zeros((3,)+D.shape)
    rest = np.zeros(D.shape[1])
    records = {}
    for name, factor, source, direction in zip(
            ("inner_sheet", "outer_sheet", "core_bend", "annular_bend"), factors,
            ("sheet_current_integral", "sheet_current_integral",
             "bend_current_integral", "bend_current_integral"),
            (reference["sheet_radial_fraction"], reference["sheet_radial_fraction"],
             np.zeros_like(D), np.zeros_like(D))):
        current = np.asarray(reference[source], float)*factor*span_factor
        if current.shape != D.shape or not np.isfinite(current).all() or np.any(current < 0):
            raise ValueError("matching finite current integrals required")
        inventory = np.sqrt(2)*current.max(axis=0)
        speed = np.divide(current, inventory, out=np.zeros_like(current), where=inventory > 0)
        rho = inventory/(D*np.sqrt(1-speed*speed))
        family = np.stack([rho, rho*speed*speed*direction,
                           rho*speed*speed*(1-direction)/2])
        tensor += family
        rest += inventory
        # Rotating sheet carriers also require an inward mechanical reaction.
        # Their transverse kinetic-stress trace adds to the straight hoop load.
        kinetic_hoop = rho*speed*speed*straight if name.endswith("sheet") else np.zeros_like(D)
        records[name] = dict(unit_rest_inventory=inventory, unit_tensor=family,
                             current_integral=current, unit_straight_hoop=kinetic_hoop)
    return dict(unit_tensor=tensor, unit_rest_inventory=rest,
                families=records, span_factor=span_factor,
                sheet_factor=span_factor*(factors[0]+factors[1]),
                bend_factor=span_factor*(factors[2]+factors[3]))


def radial_sleeve_projection(facets, volume, hoop, *, boundary_hoops=None):
    """Reduce all time samples to exact fixed-energy radial-sleeve bounds.

    For density M/D and axial pressure z, the sleeve tensor is
    (M/D, z, -H/2). Write G=max(facet0+H,facet1-H/2) and Q=facet2-H/2.
    Eliminating z with |z|<=k*M/D yields
      (1-2k) M <= -D Q,
      (1-k) M <= -D G,
      3 M <= -D(2G+Q),   M >= D H/k.
    The time extrema therefore suffice for any k. Each label keeps its
    own inventory. Axial pressure remains independently adjustable.
    """
    F, D, H = map(lambda x: np.asarray(x, float), (facets, volume, hoop))
    if (D.ndim != 2 or F.shape != (3,)+D.shape or H.shape != D.shape
            or not all(np.isfinite(x).all() for x in (F, D, H))
            or np.any(D <= 0) or np.any(H < 0)):
        raise ValueError("matching finite radial sleeve arrays required")
    G = D*np.maximum(F[0]+H, F[1]-H/2)
    Q = D*(F[2]-H/2)
    floor = np.max(D*H, axis=0)
    if boundary_hoops is not None:
        parts = np.asarray(boundary_hoops, float)
        if (parts.ndim != 3 or parts.shape[1:] != D.shape
                or not np.isfinite(parts).all() or np.any(parts < 0)
                or not np.allclose(parts.sum(axis=0), H, rtol=1e-12, atol=1e-14)):
            raise ValueError("separate boundary hoop loads must sum to total hoop")
        # Each boundary retains its own inventory even if load peaks differ.
        floor = np.max(parts*D, axis=1).sum(axis=0)
    return dict(hoop_max=floor, G_max=np.max(G, axis=0),
                Q_max=np.max(Q, axis=0), mixed_max=np.max(2*G+Q, axis=0))


def radial_sleeve_interval(projection, stress_fraction):
    k = float(stress_fraction)
    if not np.isfinite(k) or not 0 < k <= 1:
        raise ValueError("stress fraction must lie in (0,1]")
    lower = projection["hoop_max"]/k
    upper = -projection["mixed_max"]/3
    valid = np.ones_like(lower, dtype=bool)
    for alpha, bound in ((1-2*k, -projection["Q_max"]),
                         (1-k, -projection["G_max"])):
        if alpha > 0:
            upper = np.minimum(upper, bound/alpha)
        elif alpha < 0:
            lower = np.maximum(lower, bound/alpha)
        else:
            valid &= bound >= 0
    return dict(lower=lower, upper=upper, feasible=valid & (lower <= upper),
                minimum_gap=float(np.min(upper-lower)))


def radial_sleeve_threshold(projection, *, iterations=32):
    """Smallest k passing all labels; None if k=1 already fails."""
    if not radial_sleeve_interval(projection, 1.)["feasible"].all():
        return None
    low, high = 0., 1.
    for _ in range(iterations):
        midpoint = .5*(low+high)
        if radial_sleeve_interval(projection, midpoint)["feasible"].all():
            high = midpoint
        else:
            low = midpoint
    return high
