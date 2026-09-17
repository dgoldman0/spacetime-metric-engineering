"""Mechanical work ports and field allocations for the existing support sheets.

Four boundary facets represent two loaded sheet directions. Capacitor
fields can occupy part of the standing Maxwell allocation; the remaining
field populations then retain their own work and holding obligations.
"""
import numpy as np

from .constitutive_joints_and_optics import series_state


def sheet_boundary_state(tension, inventory, joints, tension_rate, reference_span):
    """Sheet span, four equal facet forces, and exact boundary work."""
    T, rate, reference = np.broadcast_arrays(tension, tension_rate, reference_span)
    if np.any(reference <= 0) or not np.isfinite(rate).all():
        raise ValueError("positive reference spans and finite rates required")
    s = series_state(T, inventory, joints, dimension=2)
    length = reference*(s["core_linear_stretch"]+1e-4*s["joint_stretch"])
    length_rate = length*s["cell_log_derivative"]*rate
    force = T/length
    velocity = length_rate/2
    energy_rate = (s["core_energy_derivative"]+s["joint_energy_derivative"])*rate
    return dict(length=length, length_rate=length_rate, force_per_facet=force,
        force_rate_per_facet=(rate-force*length_rate)/length,
        facet_velocity=velocity, mechanical_power=4*force*velocity,
        material_energy_rate=energy_rate, material_energy=s["total_energy"])


def reflector_ports(force_per_facet, velocity):
    """Lab-frame arrival/departure powers at four load-bearing mirrors, c=1."""
    F, v = np.broadcast_arrays(force_per_facet, velocity)
    if (not np.isfinite(F).all() or not np.isfinite(v).all()
            or np.any(F < 0) or np.any(abs(v) >= 1)):
        raise ValueError("nonnegative force and subluminal facets required")
    return dict(incoming=2*F*(1+v), outgoing=2*F*(1-v),
                encountered_power=4*F, mechanical_power=4*F*v)


def capacitor_bank(boundary, baseline_length, baseline_gap, *, epsilon_area=1.):
    """Four vacuum gaps with fixed outer plates during the local reaction.

    Each gap attracts its moving sheet boundary outward. In SI form,
    F=Q^2/(2 epsilon A), U=F g and V=Q g/(epsilon A). The default units
    normalize epsilon*A; the mechanical and energy results are independent
    of that choice. Return plates, their hosts and leads are separate parts.
    """
    if not np.isfinite(epsilon_area) or epsilon_area <= 0:
        raise ValueError("positive epsilon times plate area required")
    F, Fdot = boundary["force_per_facet"], boundary["force_rate_per_facet"]
    gap = np.asarray(baseline_gap)-(boundary["length"]-baseline_length)/2
    if np.any(gap <= 0) or np.any(F <= 0):
        raise ValueError("positive gap and loaded facets required")
    charge = np.sqrt(2*epsilon_area*F)
    charge_rate = epsilon_area*Fdot/charge
    voltage = charge*gap/epsilon_area
    electrical = 4*voltage*charge_rate
    mechanical = boundary["mechanical_power"]
    field_rate = 4*(gap*Fdot-F*boundary["facet_velocity"])
    return dict(gap=gap, charge_per_facet=charge, charge_rate_per_facet=charge_rate,
        voltage_per_facet=voltage, field_energy=4*F*gap,
        electrical_power=electrical, mechanical_power=mechanical,
        field_energy_rate=field_rate, balance_error=electrical-mechanical-field_rate)


def capacitor_field_split(outer_energy, angular_energy):
    """Maxwell basis (hoop, radial) for the two existing sheet populations.

    Outer-sheet facets share radial/tangential normals equally; the
    angular-sheet facets have tangential normals. Opposed plates have
    the same quadratic Maxwell stress and zero field momentum at rest.
    """
    outer, angular = np.broadcast_arrays(outer_energy, angular_energy)
    return np.stack((.5*outer+angular, .5*outer))


def periodic_capacitor_cell(boundary, lattice_pitch, *, epsilon_area=1.):
    """Return electrodes are the facing boundaries of adjacent equal cells.

    Two complete gaps are assigned to each two-directional sheet cell.
    Four shared half-gaps give identical energy/work bookkeeping. The
    lattice pitch is held fixed during this local reaction; its slower
    positioning work remains a separate macro port.
    """
    pitch = np.asarray(lattice_pitch)
    bank = capacitor_bank(boundary, pitch, np.zeros_like(pitch), epsilon_area=epsilon_area)
    return dict(**bank, full_gap=2*bank["gap"],
                full_gap_voltage=2*bank["voltage_per_facet"], full_gaps_per_cell=2)


def minimum_field_conversion(fields, maxwell_demand):
    """Smallest common photon substitution fraction supplying given fields."""
    E, demand = np.asarray(fields, float), np.asarray(maxwell_demand, float)
    if E.shape[0] != 4 or demand.shape != E[:2].shape or np.any(E < 0) or np.any(demand < 0):
        raise ValueError("four positive field channels and two matched demands required")
    supplies = np.stack((E[2]+.5*E[3], .5*E[3]))
    deficit = np.maximum(demand-E[:2], 0.)
    required = np.divide(deficit, supplies, out=np.full_like(deficit, np.inf), where=supplies > 0)
    required = np.where(deficit == 0, 0., required)
    return required.max(axis=0)


def capacitor_energy_upper(tension_lower, tension_upper, inventory, joints,
                           load_increment, *, clearance_fraction=.1):
    """Continuous panel ceiling for reaction-stroke capacitor energy.

    A slow positioning stage tracks the baseline material span. The gap
    spans half the full added extension plus the stated fractional
    clearance. Fixed reference length cancels from F*g. Monotonic core
    force and joint stretch bound the derivative of the complete span.
    """
    lo, hi, inc = np.broadcast_arrays(tension_lower, tension_upper, load_increment)
    if np.any(hi < lo) or np.any(inc <= 0) or clearance_fraction <= 0:
        raise ValueError("ordered baseline loads, positive increment/clearance required")
    low = series_state(lo, inventory, joints, dimension=2)
    high = series_state(hi+inc, inventory, joints, dimension=2)
    root_lower = np.hypot(low["core_tension"], .9*np.asarray(inventory))
    joint_derivative_upper = 1e-4*low["force_derivative"]*high["joint_stretch"]**3/np.asarray(joints)
    # dt_core/dT <= 1 supplies the final denominator bound.
    span_derivative_upper = high["core_linear_stretch"]/(2*root_lower)+1e-4*joint_derivative_upper
    force_upper = high["force_times_core_reference_span"]
    local_bound = 2*(1+clearance_fraction)*force_upper*span_derivative_upper*inc
    # T=F*L and monotone force give F_hi*(L_hi-L_lo) <= T_hi-T_lo
    # for each baseline, independent of its location inside this panel.
    global_bound = 2*(1+clearance_fraction)*inc
    return np.minimum(local_bound, global_bound)
