"""Constituent-resolved, pointwise containment allocation.

Local axes are (z, theta, n): tube axis, hoop and normal. Averaging theta/n
recovers the rail tensor (rho, p_radial, p_transverse). Equal averaged
tensors do not imply equal mechanical duties. The algebra below enforces
integrated hoop load and normal-stress cancellation explicitly.

These are ideal component allocations, not a spatial Maxwell/material
solution. Additional field currents, finite interfaces, bend forces and
constitutive time evolution require separate models and counted tensors.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import linprog


ASSEMBLY_NAMES = ("longitudinal_sheet", "hoop_strings", "transverse_sheet",
                  "hoop_maxwell", "field_host_inventory")
SUPPORT_NAMES = ("radial_maxwell", "radial_photons", "angular_photons",
                 "angular_membrane", "unassigned_inventory")
SUPPORT_BASIS = np.array([[1., 1., 1., 1., 1.],
                          [-1., 1., 0., 0., 0.],
                          [1., 0., .5, -1., 0.]])


def material_basis(*, transverse_strength=1., field_kind="hoop_maxwell"):
    """Columns are positive-energy constituents; rows (rho,p_z,p_theta,p_n).

    Strength modifies only the transverse sheet, independently of the other
    constituents. field_kind controls equal-average/different-duty tests.
    """
    k = float(transverse_strength)
    if not np.isfinite(k) or not 0 < k <= 1:
        raise ValueError("transverse-sheet stress fraction must be in (0,1]")
    fields = dict(hoop_maxwell=(1., 1., -1., 1.),
                  normal_maxwell=(1., 1., 1., -1.),
                  axial_photons=(1., 1., 0., 0.))
    if field_kind not in fields:
        raise ValueError("unknown local field orientation or type")
    return np.array([(1., -1., -1., 0.), (1., 0., -1., 0.),
                     (1., 0., -k, -k), fields[field_kind],
                     (1., 0., 0., 0.)]).T


def average_tensor(local):
    tensor = np.asarray(local, float)
    if tensor.shape[0] != 4:
        raise ValueError("four local stress-energy components required")
    return np.stack([tensor[0], tensor[1], (tensor[2]+tensor[3])/2])


def tensile_strength_floor(available_energy, hoop):
    """Necessary best-constituent strength for this closed-load ensemble.

    Let all tensile materials satisfy |p_i|<=k*rho. Let other components
    have positive energy, |p_i|<=rho and p_theta+p_n>=0 (Maxwell fields,
    radiation, dust). H<=2*k*E_material and H<=k*E_material+E_other imply
    E_total>=H*(1+k)/(2*k), even with internal normal-stress cancellation.
    Available energy here generously omits all remaining support duties.
    """
    energy, H = np.broadcast_arrays(np.asarray(available_energy, float), np.asarray(hoop, float))
    if (not np.isfinite(energy).all() or not np.isfinite(H).all()
            or np.any(energy <= 0) or np.any(H < 0)):
        raise ValueError("positive available energy and nonnegative hoop load required")
    return np.divide(H, 2*energy-H, out=np.full_like(H, np.inf), where=2*energy > H)


def allocate(facets, hoop, *, host_per_field=0., transverse_strength=1.):
    """Exact max-margin allocation in the stated five-component family.

    Write W for longitudinal-sheet energy, S for hoop strings, M for the
    transverse sheet, and b for hoop-directed Maxwell energy. Normal balance
    gives k*M=b; hoop balance gives W+S+2*b=H. Axial pressure z=b-W.
    For each z in [-H,H/2], the least-energy allocation has b=max(z,0).
    The extra energy above H is [1/k-1+host_per_field]*b.

    This piecewise-linear minimax problem attains its optimum at an endpoint,
    z=0, or the crossing of the decreasing/increasing support facets.
    """
    F = np.asarray(facets, float)
    H = np.asarray(hoop, float)
    material_basis(transverse_strength=transverse_strength)
    if (F.shape != (3,)+H.shape or not np.isfinite(F).all()
            or not np.isfinite(H).all() or np.any(H < 0)
            or not np.isfinite(host_per_field) or host_per_field < 0):
        raise ValueError("matching finite facets, nonnegative hoop and host cost required")
    A, B, C = F
    first = np.maximum(A+2*H, B+H/2)
    third = C+H/2
    choices = np.stack([-H, np.zeros_like(H), H/2,
                        np.clip((first-third)/3, -H, H/2)])
    penalty = 1/transverse_strength-1+host_per_field
    scores = np.maximum(first-choices, third+2*choices)+penalty*np.maximum(choices, 0.)
    which = scores.argmin(axis=0)[None, ...]
    axial = np.take_along_axis(choices, which, axis=0)[0]
    field = np.maximum(axial, 0.)
    wall = np.maximum(-axial, 0.)
    string = np.maximum(H-wall-2*field, 0.)
    components = np.stack([wall, string, field/transverse_strength,
                           field, host_per_field*field])
    local = np.einsum("ij,j...->i...", material_basis(transverse_strength=transverse_strength), components)
    return dict(components=components, local_tensor=local,
                averaged_tensor=average_tensor(local), axial_pressure=axial,
                minimum_shortfall=np.take_along_axis(scores, which, axis=0)[0])


def host_cost_threshold(facets, hoop, *, volume=1., iterations=42):
    """Bracket a uniform pressureless host-energy/extra-field-energy allowance.

    The bound is necessary within the ideal family. It does not estimate the
    actual currents or their stresses. Infinity means these data need no
    extra field, so a ratio to its zero energy supplies no finite constraint.
    """
    def worst(cost):
        return float(np.max(np.asarray(volume)*allocate(facets, hoop, host_per_field=cost)["minimum_shortfall"]))
    if worst(0.) > 1e-12:
        return dict(feasible_at_zero=False, lower=None, upper=None)
    if worst(1.) <= 0:
        return dict(feasible_at_zero=True, lower=None, upper=None, field_required=False)
    low, high = 0., 1.
    for _ in range(iterations):
        middle = (low+high)/2
        if worst(middle) <= 0:
            low = middle
        else:
            high = middle
    return dict(feasible_at_zero=True, lower=low, upper=high, field_required=True)


def component_program(target, field_floor, hoop, *, host_per_field=0.,
                      transverse_strength=1., field_kind="hoop_maxwell"):
    """Independent LP maximizes pressureless reserve after matching all loads.

    Variables are the five named assembly energies and five support energies.
    The three ledger equations and two mechanical equations have separate
    rows. The host energy is also explicitly constrained and counted once.
    """
    rho, axial, angular = np.asarray(target, float)
    H, floor, beta = float(hoop), float(field_floor), float(host_per_field)
    if (not np.isfinite([rho, axial, angular, H, floor, beta]).all()
            or min(H, floor, beta) < 0):
        raise ValueError("finite target and nonnegative load, floor and host cost required")
    local = material_basis(transverse_strength=transverse_strength, field_kind=field_kind)
    ledger = np.column_stack([average_tensor(local), SUPPORT_BASIS])
    hoop_row = np.r_[-local[2], np.zeros(5)]
    normal_row = np.r_[local[3], np.zeros(5)]
    host_row = np.zeros(10)
    host_row[4], host_row[3] = 1., -beta
    eq = np.vstack([ledger, hoop_row, normal_row, host_row])
    objective = np.zeros(10)
    objective[-1] = -1.
    result = linprog(objective, A_eq=eq,
                     b_eq=[rho, axial, angular, H, 0., 0.],
                     bounds=[(0., None)]*5+[(floor, None)]+[(0., None)]*4,
                     method="highs")
    return result


def required_exchange(energy, axial_pressure_energy, transverse_trace_energy,
                      axial_stretch, transverse_stretch):
    """Panel-integrated exchange implied by dE + P_i d log(lambda_i).

    Trapezoidal stress work gives the forcing required to traverse a supplied
    sequence of allocations. It supplies no dynamics, actuator or heat sink.
    """
    E, P, T = map(lambda a: np.asarray(a, float),
                  (energy, axial_pressure_energy, transverse_trace_energy))
    lr, lt = np.asarray(axial_stretch, float), np.asarray(transverse_stretch, float)
    if (E.shape != P.shape or E.shape != T.shape or E.ndim != 3
            or lr.shape != E.shape[1:] or lt.shape != lr.shape
            or min(np.min(lr), np.min(lt)) <= 0
            or not all(np.isfinite(a).all() for a in (E, P, T, lr, lt))):
        raise ValueError("finite component/time/label energies and positive matching stretches required")
    work = (.5*(P[:, 1:]+P[:, :-1])*np.diff(np.log(lr), axis=0)
            + .5*(T[:, 1:]+T[:, :-1])*np.diff(np.log(lt), axis=0))
    return np.diff(E, axis=1)+work
