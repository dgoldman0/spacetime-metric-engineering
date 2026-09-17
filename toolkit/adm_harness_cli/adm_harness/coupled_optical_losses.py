"""Coupled rotor encounters and absorption within the shared rail allocation.

L1 histories use continuous panel derivative bounds and exact endpoint
jumps. Partial absorption changes torque and thermal action while retaining
the prescribed total rotor power. Other component losses are energy
allowances; their heat hosts and replacement interfaces remain separate.
"""
import numpy as np

from .coupled_holding_certificate import (
    C_MAX, FLOAT_GUARD, H_MAX, PHOTON_PEAK, PHOTON_PILOT,
    RADIUS_ERROR_BOUND, SHORT_DELAY, guide_trace_rate_bounds,
)
from .scheduled_optical_transfer import (
    CONVERTER_DELAY, CONVERTER_NET_POWER, CONVERTER_RAMP, PILOT_POWER,
    RAMP_TIME, SPIN_FLOOR, guide_bounds, guide_radius, rotor_rhs, rotor_state,
)

ROTOR_L1_GAIN = 2.85


def effective_input_l1_bounds(panel_peak, left_power, right_power,
        derivative_bound, node_peak, duration, delay, baseline_power_bound):
    """Cumulative integrals divided by C_node, with upcoming edges prepaid.

    The delayed-receipt inequality is ||A-A(. -delta)||_1 <= delta TV(A).
    The guide contribution uses TV(Q)+TV(H) in delta-normalized units.
    A complete converter or reaction-line event pays its full photon-energy
    variation. The prepared reaction pilot stays present outside events.
    """
    P, L, R, D, peak, dt, delta, baseline = map(lambda a: np.asarray(a, float),
        (panel_peak, left_power, right_power, derivative_bound, node_peak,
         duration, delay, baseline_power_bound))
    if (P.ndim != 3 or any(a.shape != P.shape for a in (L, R, D))
            or peak.shape != (P.shape[0], P.shape[2]) or dt.shape != P.shape[1:]
            or delta.shape != (P.shape[2],) or baseline.shape != dt.shape
            or not all(np.isfinite(a).all() for a in (P, L, R, D, peak, dt, delta, baseline))
            or any(np.any(a < 0) for a in (P, D, peak, baseline))
            or np.any(dt <= 0) or np.any(delta <= 0)
            or np.any(P > peak[:, None]*(1+1e-12))):
        raise ValueError("matching finite bounded panel powers and positive durations required")
    normalize = lambda a: np.divide(a, peak[:, None], out=np.zeros_like(a),
                                    where=peak[:, None] > 0)
    normalized = normalize(P)
    left, right = normalize(np.maximum(L, 0)), normalize(np.maximum(R, 0))
    rate = normalize(D)*delta
    zero = np.zeros_like(P[:, :1])
    padded = np.concatenate([zero, normalized, zero], axis=1)
    steps = abs(np.diff(padded, axis=1))
    jump = abs(np.concatenate([left, zero], axis=1)
               -np.concatenate([zero, right], axis=1))
    events = (steps != 0) | (jump != 0)
    events[:, 0] |= peak > 0
    events[:, -1] |= peak > 0
    prefix = lambda a: np.cumsum(a, axis=1)[:, 1:]
    count = prefix(events)
    radius_variation = prefix(abs(np.diff(guide_radius(padded+PILOT_POWER), axis=1)))
    receipt = np.cumsum(rate*(dt/delta), axis=1)+prefix(jump)
    g = guide_bounds()
    guide = (g["output_power_variation_per_radius_change"]
             +g["guide_energy_variation_per_radius_change"])*radius_variation
    converter = 2*CONVERTER_DELAY*CONVERTER_NET_POWER/SPIN_FLOOR*count
    reaction = 6*SHORT_DELAY*(PHOTON_PEAK-PHOTON_PILOT)*count
    guide_trace = guide_trace_rate_bounds()["derivative_per_radius_change"]*RAMP_TIME*radius_variation
    baseline_work = np.cumsum(baseline*(dt/delta), axis=0)[None]*(peak[:, None] > 0)
    effective = receipt+guide+converter+(1+C_MAX)*reaction+C_MAX*guide_trace+baseline_work
    return dict(receipt=receipt, guide=guide, converter=converter,
        reaction_line=reaction, guide_trace=guide_trace, baseline=baseline_work,
        effective=np.nextafter(effective*(1+FLOAT_GUARD), np.inf),
        events=count, radius_variation=radius_variation)


def absorbing_rotor_ports(power, spin, absorption=0.):
    """Partial absorption in the instantaneous tangential mirror rest frame.

    The incident direction s is the sign of prescribed total power q.
    Pout=(1-a)*(1-s*j)/(1+s*j)*Pin. Angular impulse per radius is
    s*(Pin+Pout); the remainder q-j*impulse enters the thermal state.
    Radial boosts are already represented by the rotor equations. The heat
    term is generalized power after removing ordered torque work. Putting
    it in the zero-angular-momentum radiation bath requires an explicit
    transfer from the moving absorbing facet.
    """
    q, j, a = np.broadcast_arrays(*map(lambda x: np.asarray(x, float),
                                      (power, spin, absorption)))
    if (not all(np.isfinite(x).all() for x in (q, j, a))
            or np.any((j <= 0) | (j >= 1)) or np.any((a < 0) | (a >= 1))
            or np.any(2*j-a*(1+j) <= 0)):
        raise ValueError("subluminal positive spin and extractable absorption fraction required")
    direction = np.where(q < 0, -1., 1.)
    denominator = 2*j+direction*a*(1-direction*j)
    incoming = abs(q)*(1+direction*j)/denominator
    outgoing = (1-a)*(1-direction*j)/(1+direction*j)*incoming
    heat = a*(1-direction*j)*incoming
    impulse = direction*(incoming+outgoing)
    return dict(incoming=incoming, outgoing=outgoing, heating=heat,
        signed_impulse=impulse, total_port_exposure=incoming+outgoing)


def absorption_gain(absorption, spin_floor=SPIN_FLOOR):
    """Upper bound H/|q|; the discharge branch at minimum spin is worst."""
    a, j = np.broadcast_arrays(np.asarray(absorption, float), np.asarray(spin_floor, float))
    if (not np.isfinite([a, j]).all() or np.any((a < 0) | (a >= 1))
            or np.any((j <= 0) | (j >= 1)) or np.any(2*j-a*(1+j) <= 0)):
        raise ValueError("positive extractable spin and absorption fraction required")
    return a*(1-j*j)/(2*j-a*(1+j))


def absorbing_rotor_rhs(state, net_power, *, absorption=0., inventory=19.,
                         damping=.8):
    """Conditional transfer into the existing zero-angular-momentum bath.

    This conserves total energy and photon torque. A physical absorbing
    facet additionally needs the bath-transfer interface; its own comoving
    heat generally has tangential momentum.
    """
    s = rotor_state(state)
    ports = absorbing_rotor_ports(net_power, state[2], absorption)
    derivative = rotor_rhs(state, net_power, inventory=inventory, damping=damping)
    heat_action = state[0]*ports["heating"]/(s["gamma"]*inventory)
    derivative[2] -= heat_action/state[2]
    derivative[3] += heat_action
    return derivative


def retained_rotor_heat_bound(effective_l1, *, absorption, inventory=19.):
    """Additional b for absorption at prescribed total-power ports.

    At fixed x,p,h, j^2+2b is unchanged by the added heat/torque terms.
    Thus the parent radial invariant and support law remain valid until the
    reconstructed spin reaches its floor. The x/gamma factor is bounded by
    H_MAX+RADIUS_ERROR_BOUND. Initial absorption heat is zero.
    """
    value = np.asarray(effective_l1, float)
    if not np.isfinite(value).all() or np.any(value < 0) or not 18 <= inventory <= 20:
        raise ValueError("nonnegative L1 bound and inventory in [18,20] required")
    return ((H_MAX+RADIUS_ERROR_BOUND)/inventory
            *absorption_gain(absorption)*ROTOR_L1_GAIN*value)


def rotor_absorption_ceiling(effective_l1, action_headroom, *, inventory=19.):
    """Largest constant rest-frame absorption allowed by the retained-heat bound."""
    l1, headroom = np.broadcast_arrays(np.asarray(effective_l1, float),
                                       np.asarray(action_headroom, float))
    if (not np.isfinite([l1, headroom]).all() or np.any(l1 < 0)
            or not 18 <= inventory <= 20):
        raise ValueError("finite heat headroom and nonnegative L1 bound required")
    coefficient = (H_MAX+RADIUS_ERROR_BOUND)/inventory*ROTOR_L1_GAIN*l1
    h = np.maximum(headroom, 0)
    den = coefficient*(1-SPIN_FLOOR**2)+h*(1+SPIN_FLOOR)
    return np.divide(2*SPIN_FLOOR*h, den, out=np.zeros_like(den), where=den > 0)


def energy_only_replacement(exposure, retained_loss, *, feedback_gain=ROTOR_L1_GAIN/SPIN_FLOOR):
    """Scalar budget for separately replenished loss, conditional on routing.

    X <= X0+feedback_gain*E and E <= alpha*X give this fixed point.
    Its realization must also satisfy peak, heat, route and state bounds.
    """
    X, alpha = np.broadcast_arrays(np.asarray(exposure, float), np.asarray(retained_loss, float))
    if (not np.isfinite([X, alpha]).all() or np.any(X < 0) or np.any(alpha < 0)
            or not np.isfinite(feedback_gain) or feedback_gain < 0
            or np.any(alpha*feedback_gain >= 1)):
        raise ValueError("nonnegative exposure and contractive replacement gain required")
    return alpha*X/(1-alpha*feedback_gain)
