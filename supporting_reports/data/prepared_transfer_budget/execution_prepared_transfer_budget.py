"""Joint preparation and endpoint bounds with finite passive thermal flight.

The endpoint theorem uses lossless two-delay work paths. Its uniform
comparison margins can absorb the independently bounded thermal flight
drive. Replacement of losses in other components remains an energy
allowance until its waveforms and material hosts are constructed.
"""
import numpy as np

from .coupled_holding_certificate import C_MAX, H_MIN, H_MAX, ISS_DECAY
from .finite_thermal_budget import finite_heat_closure
from .reaction_endpoint_certificate import (
    CHI_UPPER, INVERSE_L1, LINE_RATE_GAIN, WEIGHTED_TRACE_DUAL,
)
from .scheduled_optical_transfer import (
    CONVERTER_DELAY, GUIDE_MASS, PILOT_POWER, SPIN_FLOOR,
    guide_radius, preparation,
)


def cold_preparation(plateau, main_loop_pilot, *, inventory=19., initial_heat=1e-8):
    """Prepare a radial equilibrium while paying the main-loop photons.

    Two half-delay guide legs together retain A+Pguide, the useful delivery
    leg retains A, and the converter loop retains tau_converter*Bmain.
    The two-delay reaction pilot and support field have their own already
    allocated state ceiling; they are recorded separately in the audit.
    """
    A, B = np.broadcast_arrays(np.asarray(plateau, float), np.asarray(main_loop_pilot, float))
    if (not np.isfinite([A, B]).all() or np.any((A < 0) | (A > 1) | (B < 0) | (B > 5))
            or not np.isfinite(initial_heat) or initial_heat < 0 or not 18 <= inventory <= 20):
        raise ValueError("plateau in [0,1], main pilot in [0,5] and nonnegative heat required")
    guide = GUIDE_MASS*guide_radius(A+PILOT_POWER)
    paths = 2*A+PILOT_POWER
    main_loop = CONVERTER_DELAY*B
    budget = preparation(inventory=inventory)["initial_dynamic_energy"]
    h = (budget-guide-paths-main_loop)/inventory
    j2 = h*h-1-2*initial_heat
    if np.any(j2 <= SPIN_FLOOR**2) or np.any((h < H_MIN) | (h > H_MAX)):
        raise ValueError("prepared rotor leaves the certified energy/spin domain")
    return dict(radius=h, momentum=np.zeros_like(h), spin=np.sqrt(j2),
                thermal_action=np.full_like(h, initial_heat), energy=h,
                guide_energy=guide, guide_and_delivery_flight_energy=paths,
                main_converter_flight_energy=main_loop,
                counted_dynamic_energy=inventory*h+guide+paths+main_loop)


def thermal_endpoint_perturbation(*, inventory=19., absorption=.62e-6, flight_delay=1/64):
    """Uniform comparison increment caused by finite thermal flight.

    For X=|W_heat_dot|_infinity, the tracking-state increment is at most
    chi*(1+cmax)*X/alpha. The support-power output adds Lf times this
    state and Kw*X directly. The reaction inverse adds at most ||H||_1*dP.
    At the rotor, q_port=N-W_work_dot-Psupport, so thermal flight enters
    its incident-power demand through this support perturbation.
    """
    heat = finite_heat_closure(absorption, inventory=inventory, flight_delay=flight_delay)
    X = heat["heat_power_peak"]
    state = CHI_UPPER*(1+C_MAX)/ISS_DECAY*X
    support = WEIGHTED_TRACE_DUAL*state+LINE_RATE_GAIN*X
    command = INVERSE_L1*support
    Kplus = (1+SPIN_FLOOR)/(2*SPIN_FLOOR)
    return dict(thermal_flight_derivative_peak=X, tracking_comparison_increment=state,
                support_power_increment=support, command_increment=command,
                emitted_margin_debit=command,
                incident_margin_debit=command+Kplus*support)


def apply_pilot_preparation(old_thermal_floor, old_spin_squared, revised_cold_floor,
                            revised_ceiling, *, thermal_state_ceiling, inventory):
    """Update h/spin bounds while preserving the counted total state ceiling."""
    floor0, spin0, floor1, ceiling = np.broadcast_arrays(*map(
        lambda v: np.asarray(v, float),
        (old_thermal_floor, old_spin_squared, revised_cold_floor, revised_ceiling)))
    if (not all(np.isfinite(v).all() for v in (floor0, spin0, floor1, ceiling))
            or not np.isfinite(thermal_state_ceiling) or thermal_state_ceiling < 0
            or not 18 <= inventory <= 20):
        raise ValueError("finite compatible energy bounds and nonnegative thermal state required")
    floor = floor1-thermal_state_ceiling/inventory
    spin2 = spin0+(floor-floor0)*(floor+floor0)
    return dict(energy_floor=floor, energy_ceiling=ceiling,
                spin_squared_lower=spin2,
                energy_domain_passed=(floor >= H_MIN) & (ceiling <= H_MAX),
                spin_passed=spin2 > SPIN_FLOOR**2)
