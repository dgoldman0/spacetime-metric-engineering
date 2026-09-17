"""Shared longitudinal/jacket reaction states in the existing rail ensemble.

This module reallocates integrated stress and counts its constitutive state
energy. Spatial tractions, positive-pressure field hosts and the new reciprocal
work ports remain explicit physical and dynamical requirements.
"""
import numpy as np

from .constitutive_joints_and_optics import series_state
from .material_reconfiguration import PRESSURE_BASIS
from .scheduled_optical_transfer import GUIDE_MASS, guide_bounds, rotor_rhs, rotor_state, ROTOR_MASS, ROTOR_DAMPING
from .nonlinear_holding_certificate import history_certificate

SUPPORT_INDICES = (2, 5)  # Outer longitudinal sheet and auxiliary transverse sheet.


def guide_trace_bound():
    b = guide_bounds()
    v, a, x = b["maximum_speed"], b["maximum_acceleration_parameter"], b["radius_maximum"]
    gamma = 1/np.sqrt(1-v*v)
    return GUIDE_MASS*x*gamma*(v*v+a/(1-a))


def total_trace_bound():
    return history_certificate(np.array([0.]))["rotor_trace_magnitude_upper"]+guide_trace_bound()


def reaction_state(trace, bias, baseline_tension, core_inventory, joint_inventory, *, field_family="maxwell"):
    """Oppose an isotropic trace through two existing sheets and field bias.

    Let a=bias+trace/3. Increase longitudinal tension by a and transverse
    tension by a/2. An isotropic positive-pressure bias carries energy 3*bias.
    It can be represented by the existing Maxwell or photon tensor columns;
    the physical host and loss requirements differ between those choices.
    """
    trace, bias = np.broadcast_arrays(np.asarray(trace, float), np.asarray(bias, float))
    T, M, m = map(lambda x: np.asarray(x, float), (baseline_tension, core_inventory, joint_inventory))
    if T.shape[0] != 2 or np.any(bias < 0) or np.any(abs(trace) > 3*bias*(1+1e-12)):
        raise ValueError("two supported sheet duties and a bias covering the trace required")
    amplitude = bias+trace/3
    if np.min(amplitude) < -1e-14:
        raise ValueError("the prebiased sheet increment is negative")
    amplitude = np.maximum(amplitude, 0.)  # Roundoff at the zero endpoint only.
    added_tension = np.array([1., .5]).reshape((2,)+(1,)*amplitude.ndim)*amplitude
    before = series_state(T, M, m, dimension=2)
    after = series_state(T+added_tension, M, m, dimension=2)
    if field_family == "maxwell":
        weights = np.array([2., 1., 0., 0.])
    elif field_family == "photon":
        weights = np.array([0., 0., 1., 2.])
    else:
        raise ValueError("field_family must be maxwell or photon")
    fields = weights.reshape((4,)+(1,)*bias.ndim)*bias
    pressure = (np.einsum("ij,j...->i...", PRESSURE_BASIS[:, SUPPORT_INDICES], added_tension)
                +np.einsum("ij,j...->i...", PRESSURE_BASIS[:, 6:10], fields))
    error = pressure+np.array([1., 2.]).reshape((2,)+(1,)*trace.ndim)*trace/3
    energy = (after["total_energy"]-before["total_energy"]).sum(axis=0)+3*bias
    derivative = after["core_energy_derivative"]+after["joint_energy_derivative"]
    return dict(added_tension=added_tension, additional_field_energy=fields,
        pressure=pressure, stress_identity_error=error, additional_energy=energy,
        energy_trace_derivative=(derivative[0]+.5*derivative[1])/3,
        sheet_energy_derivative=derivative, joint_stretch=after["joint_stretch"],
        core_stretch=after["core_linear_stretch"], force_margin=after["force_margin"],
        # Each sheet's dE/dT <= 2; hence all states with |trace|<=3*bias
        # have added energy <= 9*bias, with the original inventories fixed.
        continuous_energy_ceiling=9*bias)


def rotor_trace_and_rate(state, power, *, inventory=ROTOR_MASS, damping=ROTOR_DAMPING):
    """Exact trace derivative, retaining radial damping and input momentum."""
    x, p, j, b = np.asarray(state, float)
    s = rotor_state(state)
    h, v, gamma = s["energy"], s["radial_speed"], s["gamma"]
    rhs = rotor_rhs(state, power, inventory=inventory, damping=damping)
    hd = power/inventory
    vd = (rhs[1]-v*hd)/h
    trace = inventory*(h-x/gamma-damping*x*p)
    rate = inventory*(hd-rhs[0]/gamma+x*v*vd*gamma-damping*(rhs[0]*p+x*rhs[1]))
    return dict(trace=trace, trace_rate=rate, input_rate_coefficient=1-damping*x*v)
