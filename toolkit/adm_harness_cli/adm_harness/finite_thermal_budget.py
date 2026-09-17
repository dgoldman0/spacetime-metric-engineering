"""Conditional finite routing bounds for paired rotor thermal emission.

Matched opposite-rotor emitters feed zero-angular-momentum baths through
equal-delay routes with zero additional guide work. Their flight energy and
isotropically averaged pressure are assigned to the existing reaction
supports. Moving collectors add guide work and recoil outside this bound.
The emitter, turning surfaces and bath confinement require material laws.
"""
import numpy as np

from .coupled_holding_certificate import (
    C_MAX, HEAT_GAIN, H_MAX, H_MIN, N_MAX, RADIUS_ERROR_BOUND, SPEED_BOUND, U_MAX,
)
from .coupled_optical_losses import ROTOR_L1_GAIN, absorption_gain
from .scheduled_optical_transfer import ROTOR_RADIUS, SPIN_FLOOR


def passive_heat_gain(absorption, spin_floor=SPIN_FLOOR):
    """Bound equal material-rest-frame tangential emission Q'/|q_port|."""
    a, j = np.broadcast_arrays(np.asarray(absorption, float), np.asarray(spin_floor, float))
    return absorption_gain(a, j)/(1-j*j)


def finite_heat_closure(absorption=.62e-6, *, inventory=19., flight_delay=1/64):
    """Small-gain constants for q_rotor=q_port-dW_heat/dt.

    W_heat(t)=integral[t-tau,t] Q'(s) ds, Q' <= kappa*|q_port|.
    Thus ||Wdot||_1 <= 2*kappa*||q_port||_1 and
    |Wdot| <= kappa*||q_port||_infinity. The original coupled gain acts
    on F0-(1+c)Wdot; q_port also includes Wdot directly.
    """
    if not 18 <= inventory <= 20 or not np.isfinite(flight_delay) or flight_delay <= 0:
        raise ValueError("inventory in [18,20] and positive finite flight delay required")
    kappa = float(passive_heat_gain(absorption))
    denominator = 1-2*kappa*(ROTOR_L1_GAIN*(1+C_MAX)+1)
    if denominator <= 0 or kappa >= 1:
        raise ValueError("finite thermal feedback must be contractive")
    qpeak = inventory*U_MAX/ROTOR_RADIUS/(1-kappa)
    Wmax = flight_delay*kappa*qpeak
    return dict(absorption=float(absorption), inventory=inventory, flight_delay=flight_delay,
        passive_heat_gain=kappa, feedback_denominator=denominator,
        port_l1_gain=ROTOR_L1_GAIN/denominator, port_power_peak=qpeak,
        heat_power_peak=kappa*qpeak, flight_energy_ceiling=Wmax,
        additional_state_energy_ceiling=(1+C_MAX)*Wmax,
        additional_effective_power_peak=(1+C_MAX)*kappa*qpeak,
        port_exposure_per_power=(1+float(absorption_gain(absorption)))/SPIN_FLOOR)


def finite_heat_history(effective_l1, effective_l2, energy_floor, energy_ceiling,
                        reduced_peak, *, inventory=19., absorption=.62e-6,
                        flight_delay=1/64, initial_heat=1e-8):
    """Retain both radial damping heat and delayed passive absorption heat."""
    L1, L2 = np.broadcast_arrays(np.asarray(effective_l1, float), np.asarray(effective_l2, float))
    floor, ceiling, peak = map(lambda a: np.asarray(a, float),
                              (energy_floor, energy_ceiling, reduced_peak))
    if (L1.ndim != 2 or any(a.shape != (L1.shape[1],) for a in (floor, ceiling, peak))
            or not all(np.isfinite(a).all() for a in (L1, L2, floor, ceiling, peak))
            or np.any(L1 < 0) or np.any(L2 < 0)
            or not np.isfinite(initial_heat) or initial_heat < 0):
        raise ValueError("nonnegative forcing with matching node and label axes required")
    b = finite_heat_closure(absorption, inventory=inventory, flight_delay=flight_delay)
    ql1 = b["port_l1_gain"]*L1
    flight_l2 = 2*b["passive_heat_gain"]**2*b["port_power_peak"]*ql1
    combined_l2 = (np.sqrt(L2)+(1+C_MAX)*np.sqrt(flight_l2))**2
    damping = initial_heat+HEAT_GAIN*ROTOR_RADIUS/inventory**2*combined_l2
    absorption_action = (H_MAX+RADIUS_ERROR_BOUND)/inventory*b["passive_heat_gain"]*ql1
    hlow = floor-b["additional_state_energy_ceiling"]/inventory
    new_peak = peak+ROTOR_RADIUS/inventory*b["additional_effective_power_peak"]
    S = np.sqrt(1-SPEED_BOUND**2)
    penalty = RADIUS_ERROR_BOUND**2+2*H_MAX*(H_MAX+RADIUS_ERROR_BOUND)*(1-S)
    spin2 = hlow[None]**2-1-2*(damping+absorption_action)-penalty
    return dict(**b, port_input_l1_upper=ql1, thermal_flight_drive_l2_upper=flight_l2,
        combined_effective_l2_upper=combined_l2, damping_action_upper=damping,
        absorption_action_upper=absorption_action, energy_floor=hlow,
        reduced_input_peak=new_peak, spin_squared_lower=spin2,
        invariant_domain_passed=(hlow >= H_MIN) & (ceiling <= H_MAX) & (new_peak <= N_MAX),
        thermal_spin_passed=spin2 > SPIN_FLOOR**2)
