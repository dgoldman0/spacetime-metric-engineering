"""Shared-store bounds for moving thermal relays and finite reflector work paths.

The relay guide motion follows the rotor radius. Its reversible recoil work
is paid through separate finite optical leads. Both photon inventories enter
the existing support trace. Guide host rest energy, inertia, tangential/axial
traction paths and actual coating loss remain additional material duties.
"""
import numpy as np

from .coupled_holding_certificate import (
    C_MAX, HEAT_GAIN, H_MAX, H_MIN, N_MAX, RADIAL_DOMAIN, RADIUS_ERROR_BOUND, SPEED_BOUND, U_MAX,
)
from .coupled_optical_losses import ROTOR_L1_GAIN, absorption_gain
from .finite_thermal_budget import passive_heat_gain
from .moving_thermal_relay import relay_bounds
from .scheduled_optical_transfer import ROTOR_RADIUS, SPIN_FLOOR


def moving_heat_closure(absorption=.62e-6, *, inventory=19., maximum_speed=SPEED_BOUND,
                        axial_half_separation=1/128, maximum_actuator_gap=None):
    """Small gain for qrotor=qsource-d(Wthermal+Vwork)/dt.

    Qe<=kappa*|qport|, while qport=qrotor+Qe-Qa. With remote work
    input Premote, Wtotal_dot=Qe-Qa+Premote. Positive packets bound
    integrated arrival by r^3 and peak arrival by r^5.
    """
    if not 18 <= inventory <= 20:
        raise ValueError("inventory must lie in [18,20]")
    bounds = relay_bounds(maximum_speed, axial_half_separation)
    kappa = float(passive_heat_gain(absorption))
    v, r = maximum_speed, bounds["single_turn_energy_factor"]
    gap = (2.1*.5*(H_MAX-H_MIN+2*RADIAL_DOMAIN)*ROTOR_RADIUS
           if maximum_actuator_gap is None else float(maximum_actuator_gap))
    if not np.isfinite(gap) or gap <= 0:
        raise ValueError("positive maximum reflector-work gap required")
    force_l1 = bounds["radial_guide_impulse_l1_per_emitted_energy"]
    force_peak = bounds["radial_guide_force_peak_per_emitted_power"]
    remote_peak = .5*(1+v)/(1-v)*force_peak
    heat_difference_l1 = 1+r**3
    flight_l1 = heat_difference_l1+force_l1
    flight_peak = r**5+remote_peak
    denominator = 1-kappa*(ROTOR_L1_GAIN*(1+C_MAX)*flight_l1+heat_difference_l1)
    peak_denominator = 1-kappa*r**5
    if min(denominator, peak_denominator) <= 0:
        raise ValueError("thermal and work photon feedback must be contractive")
    qpeak = inventory*U_MAX/ROTOR_RADIUS/peak_denominator
    thermal_inventory = bounds["flight_energy_per_emitted_peak"]*kappa*qpeak
    work_inventory = gap*(1+v)*force_peak*kappa*qpeak
    inventory_total = thermal_inventory+work_inventory
    encounters = 8*r**3+2*force_l1
    return dict(absorption=float(absorption), inventory=inventory, maximum_radial_speed=float(v),
        axial_half_separation=axial_half_separation, maximum_actuator_gap=gap,
        passive_heat_gain=kappa, feedback_denominator=denominator,
        port_l1_gain=ROTOR_L1_GAIN/denominator, port_power_peak=qpeak,
        thermal_flight_energy_ceiling=thermal_inventory, work_flight_energy_ceiling=work_inventory,
        total_extra_flight_energy_ceiling=inventory_total,
        additional_state_energy_ceiling=(1+C_MAX)*inventory_total,
        total_flight_rate_l1_per_port_l1=kappa*flight_l1,
        total_flight_rate_peak=kappa*flight_peak*qpeak,
        additional_effective_power_peak=(1+C_MAX)*kappa*flight_peak*qpeak,
        arriving_heat_l1_per_port_l1=kappa*r**3,
        remote_work_net_power_peak=remote_peak*kappa*qpeak,
        remote_work_incident_power_peak=remote_peak*kappa*qpeak,
        thermal_and_work_encounters_per_port_l1=encounters*kappa,
        port_exposure_per_power=(1+float(absorption_gain(absorption)))/SPIN_FLOOR)


def moving_heat_history(effective_l1, effective_l2, energy_floor, energy_ceiling,
                         reduced_peak, *, inventory=19., absorption=.62e-6,
                         maximum_speed=SPEED_BOUND, initial_heat=1e-8):
    """Couple the moving relay to the original nonlinear heat and spin bounds."""
    L1, L2, low, high, peak = np.broadcast_arrays(*map(lambda x: np.asarray(x, float),
        (effective_l1, effective_l2, energy_floor, energy_ceiling, reduced_peak)))
    if (L1.ndim != 2 or not all(np.isfinite(v).all() for v in (L1, L2, low, high, peak))
            or np.any(np.minimum(L1, L2) < 0)
            or not np.isfinite(initial_heat) or initial_heat < 0):
        raise ValueError("finite matching node/label bounds and nonnegative forcing required")
    b = moving_heat_closure(absorption, inventory=inventory, maximum_speed=maximum_speed)
    ql1 = b["port_l1_gain"]*L1
    flight_l2 = b["total_flight_rate_peak"]*b["total_flight_rate_l1_per_port_l1"]*ql1
    combined_l2 = (np.sqrt(L2)+(1+C_MAX)*np.sqrt(flight_l2))**2
    damping = initial_heat+HEAT_GAIN*ROTOR_RADIUS/inventory**2*combined_l2
    absorbed = (H_MAX+RADIUS_ERROR_BOUND)/inventory*b["arriving_heat_l1_per_port_l1"]*ql1
    hlow = low-b["additional_state_energy_ceiling"]/inventory
    new_peak = peak+ROTOR_RADIUS/inventory*b["additional_effective_power_peak"]
    S = np.sqrt(1-SPEED_BOUND**2)
    penalty = RADIUS_ERROR_BOUND**2+2*H_MAX*(H_MAX+RADIUS_ERROR_BOUND)*(1-S)
    spin2 = hlow*hlow-1-2*(damping+absorbed)-penalty
    return dict(**b, port_input_l1_upper=ql1, total_flight_drive_l2_upper=flight_l2,
        combined_effective_l2_upper=combined_l2, damping_action_upper=damping,
        absorption_action_upper=absorbed, energy_floor=hlow, energy_ceiling=high,
        reduced_input_peak=new_peak, spin_squared_lower=spin2,
        invariant_domain_passed=(hlow >= H_MIN) & (high <= H_MAX) & (new_peak <= N_MAX),
        thermal_spin_passed=spin2 > SPIN_FLOOR**2)
