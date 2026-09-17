"""Conditional photon endpoint bounds for independently partitioned rail cells.

The parent coupled certificate supplies the exact nonlinear contraction
inequality, including parameter derivatives. Here z=(x-h,p) is compared
with z*=(-k*h*h*n0,h*n0), n0=R0*N/M. Its tracking error obeys the same
contraction inequality; a receipt jump contributes h*abs(delta N) to the
scaled comparison state E=(M/R0)*sqrt(V_error).

In theta=t/delta units, throughout each smooth panel,

 E_dot <= -(alpha/R0) E + (Kg+Kh*Umax)/R0*abs(N)
          + chi/R0*((1+cmax)*abs(W_dot)+cmax*abs(Pi_g_dot)+Pbaseline)
          + hmax*abs(N_dot),
 abs(Psupport) <= Lf*E + Ls*abs(N) + Kw*abs(W_dot)
                 + Kc*abs(Pi_g_dot)+Pbaseline.

The quiet forcing is bounded for the entire history. Event forcing covers
two receipt jumps, guide preview, converter fill/drain, and reaction-line
fill/drain. A positive scalar recurrence encloses every time bin. The
stable two-delay inverse is bounded by an exact rational impulse prefix
and an analytic tail. These are comparison inequalities over intervals,
as distinct from sampled solutions of the nonlinear rotor equations.

Endpoint commands remain prescribed feedforward functions. Fixed capacity
fractions assign each cell its share of the two original support populations
and baseline duties. Equal axis populations and opposed copies split each
cell's scalar energy and flux while cancelling its net momentum. Spatial
packing, electrical conversion, local sensing
and traction propagation retain their separate physical requirements.
"""
from fractions import Fraction as F
from itertools import product

import numpy as np

from .coupled_holding_certificate import (
    C_MAX, DAMPING, H_MAX, H_MIN, ISS_DECAY, ISS_EPSILON, RADIAL_DOMAIN,
    U_MAX, _Interval, _coefficient_intervals, guide_trace_rate_bounds,
)
from .finite_reaction_transport import inverse_filter_certificate
from .scheduled_optical_transfer import (
    CONVERTER_DELAY, CONVERTER_RAMP, GUIDE_MASS, GUIDE_RADIUS, PILOT_POWER,
    RAMP_TIME, ROTOR_RADIUS, SPIN_FLOOR, guide_bounds,
)

WEIGHTED_TRACE_DUAL = .349
EQUILIBRIUM_RESIDUAL = .0243
EQUILIBRIUM_H_DERIVATIVE = 1.950
EQUILIBRIUM_OUTPUT = .0101
INPUT_NORM_SQUARED = 1.017
TRACE_GAIN = .334806
LINE_RATE_GAIN = .00429
INVERSE_L1 = 2.638292563
PHOTON_PEAK = 1.2
SHORT_DELAY = 1/64
MINIMUM_PILOT = .001
PILOT_CEILING = .011
QUIET_POWER_CEILING = .00125
RECEIPT_RATE_CEILING = .00525
BASELINE_POWER_CEILING = .00012
GUIDE_NETWORK_CEILING = .046292
GUIDE_NETWORK_RATE_CEILING = .050567
GUIDE_TRACE_RATE_CEILING = .000001
SAMPLES_PER_DELAY = 4
FILTER_TAPS = 96
COMPARISON_DECAY_LOWER = 8.2938
RADIUS_LOWER = .02652582384
CHI_UPPER = 1.008465
REMOTE_EVENT_COMMAND = 1e-12
ROUNDING_GUARD = 1e-10


def _partitions(a, b, count):
    a, b = F(str(a)), F(str(b))
    return [(a+(b-a)*i/count, a+(b-a)*(i+1)/count) for i in range(count)]


def tracking_coefficient_certificate():
    """Verify tracking and output coefficients with exact integer intervals."""
    maxima = [0, 0, 0, 0, 0, 0]
    eps, k = _Interval(ISS_EPSILON), _Interval(DAMPING)
    boxes = product(_partitions(0, C_MAX, 16), _partitions(H_MIN, H_MAX, 16),
                    _partitions(-RADIAL_DOMAIN, RADIAL_DOMAIN, 8),
                    _partitions(-RADIAL_DOMAIN, RADIAL_DOMAIN, 8))
    count = 0
    for box in boxes:
        c, h, C, db1, db2, _, (_, da12, _, da22) = _coefficient_intervals(box)
        w, v = _Interval(*box[2]), _Interval(*box[3])
        x, S = h+w, (1-v.square()).sqrt()
        a, denominator = 1-k*x*v, 1+c*(1-k*x*v)
        f1 = k*S-v/h
        df2 = k*k*(w+h*(1-S))+k*v*(S/(1+S)-x/(h*S))
        f2 = -1/h+df2
        dual = (f1.square()+2*eps*C*h*f1*f2+C*f2.square())/(C*(1-C*eps.square()*h.square()))
        g1, g2 = h*da12+db1, h*da22+db2
        residual = C*g1.square()-2*eps*C*h*g1*g2+g2.square()
        hnorm = C*(k*h).square()+2*eps*C*k*h.square()+1
        direct = c/denominator*(h*df2+a-1)
        weighted = ((c/denominator).square()*dual).sqrt()
        # A positive-definite Q proves the residual's norm is nonnegative;
        # dependency in the interval cross term can give a negative lower end.
        residual = _Interval.raw(max(0, residual.lo), residual.hi)
        intervals = (weighted, residual.sqrt(), hnorm.sqrt(), direct,
                     c/denominator, c/denominator*(1-a))
        for index, value in enumerate(intervals):
            maxima[index] = max(maxima[index], abs(value.lo), abs(value.hi))
        count += 1
    limits = (WEIGHTED_TRACE_DUAL, EQUILIBRIUM_RESIDUAL, EQUILIBRIUM_H_DERIVATIVE,
              EQUILIBRIUM_OUTPUT, TRACE_GAIN, LINE_RATE_GAIN)
    # c/(1+c*a) increases with c and decreases with a. This eliminates the
    # repeated-c dependency in the last two coarse interval enclosures.
    amin_fraction = 1-F(str(DAMPING))*(F(str(H_MAX))+F(str(RADIAL_DOMAIN)))*F(str(RADIAL_DOMAIN))
    gain_fraction = F(str(C_MAX))/(1+F(str(C_MAX))*amin_fraction)
    maxima[4] = _Interval(gain_fraction).hi
    maxima[5] = _Interval(gain_fraction*(1-amin_fraction)).hi
    if any(value > _Interval(limit).lo for value, limit in zip(maxima, limits)):
        raise ValueError(f"Tracking coefficient exceeds its declared enclosure: {[x/_Interval.SCALE for x in maxima]}")
    # a>1/2 gives (1+c*a)^2/(1+c)>=1. Bound the exact B^T P B numerator.
    V, H, epsf, kf = map(lambda x: F(str(x)), (RADIAL_DOMAIN, H_MAX, ISS_EPSILON, DAMPING))
    norm2 = 1+2*H*(kf-epsf)*V+(H*H*(kf*kf-2*kf*epsf)+1)*V*V
    amin = 1-kf*(H+F(str(RADIAL_DOMAIN)))*V
    if amin <= F(1, 2) or norm2 > F(str(INPUT_NORM_SQUARED)):
        raise ValueError("Sharpened input norm enclosure failed")
    if F(str(CHI_UPPER))**2 < F(str(INPUT_NORM_SQUARED)):
        raise ValueError("Input norm square root was rounded downward")
    return dict(exact_integer_interval_arithmetic=True, boxes=count,
        measured_upper=[value/_Interval.SCALE for value in maxima],
        declared_upper=list(limits), input_norm_squared_upper=INPUT_NORM_SQUARED,
        input_norm_numerator_upper=str(norm2), inherited_contraction_rate=ISS_DECAY)


def quiet_pilot(receipt_rate, baseline_power, *, active=None):
    """Counted constant pilot sufficient for quiet optical branch splitting.

    On a smooth panel, |A-A_delayed|<=L and |N_receipt_dot|<=2L.
    The converter baseline separately supplies (1-jmin)/(2*jmin)*L.
    For the reaction branch, return power is at least B0-aquiet, while
    Pin(-Psupport)<=Kplus*Pquiet. The chosen B0>=aquiet/jmin exceeds
    aquiet+Kplus*Pquiet for this inverse norm and spin floor. The existing
    guide pilot remains margin.
    """
    L, baseline = np.broadcast_arrays(np.asarray(receipt_rate, float), np.asarray(baseline_power, float))
    if not np.isfinite([L, baseline]).all() or np.any(np.minimum(L, baseline) < 0):
        raise ValueError("Finite nonnegative history bounds required")
    coeff = (WEIGHTED_TRACE_DUAL/ISS_DECAY*(EQUILIBRIUM_RESIDUAL+U_MAX*EQUILIBRIUM_H_DERIVATIVE)
             +EQUILIBRIUM_OUTPUT+2*WEIGHTED_TRACE_DUAL*H_MAX*ROTOR_RADIUS/ISS_DECAY)
    baseline_coeff = 1+WEIGHTED_TRACE_DUAL*np.sqrt(INPUT_NORM_SQUARED)/ISS_DECAY
    power = (coeff*L+baseline_coeff*baseline)*(1+1e-8)
    command = INVERSE_L1*power
    Kplus = (1+SPIN_FLOOR)/(2*SPIN_FLOOR)
    if INVERSE_L1/SPIN_FLOOR < INVERSE_L1+Kplus:
        raise ValueError("Pilot coefficient cannot supply signed reaction work")
    pilot = np.maximum(MINIMUM_PILOT, command/SPIN_FLOOR)*(1+1e-8)
    if active is not None:
        pilot = np.where(np.asarray(active, bool), pilot, MINIMUM_PILOT)
    return dict(support_power_upper=power, command_upper=command, pilot=pilot,
                receipt_coefficient=coeff, baseline_coefficient=baseline_coeff)


def guide_derivative_certificate():
    """Bound Nguide and its first derivative for either septic preview."""
    bounds = guide_bounds()
    lo, hi = bounds["radius_minimum"], bounds["radius_maximum"]
    amplitude = hi-lo
    xd, xdd, x3, x4 = (amplitude*m/RAMP_TIME**i for i, m in ((1, 2.1875), (2, 8), (3, 60), (4, 840)))
    gamma2 = 1/(1-(GUIDE_RADIUS*xd)**2)
    acc = gamma2*hi*GUIDE_RADIUS**2*xdd
    gd = gamma2*GUIDE_RADIUS**2*xd*xdd
    gdd = 2*gd*gd+gamma2*GUIDE_RADIUS**2*(xdd*xdd+xd*x3)
    ad = GUIDE_RADIUS**2*gamma2*((2*gd*hi+xd)*xdd+hi*x3)
    add = 2*gd*ad+GUIDE_RADIUS**2*gamma2*((2*gdd*hi+2*gd*xd+xdd)*xdd+(2*gd*hi+2*xd)*x3+hi*x4)
    log_rate = gd+xd/lo+ad/(1-acc)
    log_derivative = gdd+xdd/lo+xd*xd/lo**2+add/(1-acc)+ad*ad/(1-acc)**2
    hdd = GUIDE_MASS*np.sqrt(gamma2)*hi/(1-acc)*(log_rate**2+log_derivative)
    qd = amplitude*bounds["output_power_variation_per_radius_change"]/RAMP_TIME
    values = (bounds["maximum_nominal_store_net_power"]-1, 2*qd+hdd, guide_trace_rate_bounds()["peak"])
    limits = (GUIDE_NETWORK_CEILING, GUIDE_NETWORK_RATE_CEILING, GUIDE_TRACE_RATE_CEILING)
    if not RADIUS_LOWER < ROTOR_RADIUS or not COMPARISON_DECAY_LOWER < ISS_DECAY/ROTOR_RADIUS:
        raise ValueError("Comparison radius and decay require outward bounds")
    if any(value*(1+1e-9) >= limit for value, limit in zip(values, limits)):
        raise ValueError("Guide derivative exceeds the event envelope")
    return dict(measured_upper=list(values), declared_upper=list(limits),
                fourth_septic_derivative_bound=840/RAMP_TIME**4, floating_guard=1e-9)


def _up(value):
    return np.nextafter(value, np.inf)


def _down(value):
    return np.nextafter(value, -np.inf)


def _positive_product(*values, upward=True):
    result = np.ones_like(np.asarray(values[0], float))
    direction = _up if upward else _down
    for value in values:
        result = direction(result*value)
    return np.maximum(result, 0.)


def _septic_lower(s):
    """Positive Bernstein sum, avoiding cancellation near the endpoints."""
    s = np.clip(s, 0., 1.)
    result = np.zeros_like(s)
    for power, coefficient in ((4, 35), (5, 21), (6, 7), (7, 1)):
        term = _positive_product(np.full_like(s, coefficient), *([s]*power), *([np.maximum(_down(1-s), 0.)]*(7-power)), upward=False)
        result = _down(result+term)
    return np.maximum(result, 0.)


def _shape_lower(t, begin, end):
    # Coordinates and time steps are dyadic, so these divisions/subtractions
    # are exact on the bounded event interval.
    return _septic_lower(np.where(t < end, (t-begin)/CONVERTER_RAMP,
                                 1-(t-end)/CONVERTER_RAMP))


def _ramp_derivative_upper(left, right, begin, end, order):
    result = np.zeros_like(left)
    for start in (begin, end):
        lo = np.clip((left-start)/CONVERTER_RAMP, 0, 1)
        hi = np.clip((right-start)/CONVERTER_RAMP, 0, 1)
        if order == 1:
            term = _positive_product(np.full_like(lo, 140/CONVERTER_RAMP), hi, hi, hi, 1-lo, 1-lo, 1-lo)
        elif order == 2:
            term = _positive_product(np.full_like(lo, 420/CONVERTER_RAMP**2), hi, hi, 1-lo, 1-lo,
                                     np.maximum(abs(1-2*lo), abs(1-2*hi)))
        else:
            raise ValueError("First or second derivative required")
        result = _up(result+np.where((right > start) & (left < start+CONVERTER_RAMP), term, 0.))
    return result


def _impulse_prefix(taps=FILTER_TAPS):
    h = [F(1), F(-1, 2)]
    for _ in range(2, taps):
        h.append(-(h[-1]+h[-2])/2)
    return np.nextafter(np.array([float(abs(value)) for value in h]), np.inf)


def _delay(array, lag, initial=0.):
    return np.r_[np.full(lag, initial), array[:-lag]]


def event_certificate(upward, *, samples_per_delay=SAMPLES_PER_DELAY):
    """Continuous-bin endpoint/incident bounds for every unit-sized event.

    Any receipt jump is at most one. The incoming/outgoing receipt jumps
    occur one delta apart. A guide change has arbitrary magnitude in [0,1].
    The baseline bounds cover smooth receipt and time-varying support work.
    Previous separated events contribute the explicit remote-event margin.
    """
    if samples_per_delay < 2 or samples_per_delay > 16 or samples_per_delay & (samples_per_delay-1):
        raise ValueError("A power-of-two delay resolution between 2 and 16 is required")
    step = SHORT_DELAY/samples_per_delay
    onset = -RAMP_TIME-.5 if upward else -.5
    begin = min(onset-.5, 0.)-CONVERTER_RAMP-CONVERTER_DELAY-1
    end = max(onset+RAMP_TIME+.5, 1.)+1
    start, finish = begin-1, end+CONVERTER_RAMP+12
    left = start+np.arange(round((finish-start)/step))*step
    right = left+step
    pulse = ((right > 0) & (left < 1)).astype(float)
    guide = ((right > onset-.5) & (left < onset+RAMP_TIME+.5)).astype(float)
    # The event increment is below these full peak amplitudes for every
    # permitted quiet pilot. Past/future derivative intervals include flight.
    loop_rate = _up((5*CONVERTER_DELAY)*_ramp_derivative_upper(left-CONVERTER_DELAY, right, begin, end, 1))
    loop_second = _up((5*CONVERTER_DELAY)*_ramp_derivative_upper(left-CONVERTER_DELAY, right, begin, end, 2))
    line_rate = _up((3*SHORT_DELAY*PHOTON_PEAK)*_ramp_derivative_upper(left-2*SHORT_DELAY, right, begin, end, 1))
    guide_trace = _up(guide*GUIDE_TRACE_RATE_CEILING)
    network = _up(_up(pulse+_up(guide*GUIDE_NETWORK_CEILING))+loop_rate)
    network_rate = _up(_up(guide*GUIDE_NETWORK_RATE_CEILING)+loop_second)
    residual = _up(EQUILIBRIUM_RESIDUAL+_up(U_MAX*EQUILIBRIUM_H_DERIVATIVE))
    forcing = _up(_up(_up(residual/RADIUS_LOWER)*network)
                  +_up(_up(CHI_UPPER/RADIUS_LOWER)*_up(_up((1+C_MAX)*line_rate)+_up(C_MAX*guide_trace))))
    forcing = _up(forcing+_up(H_MAX*network_rate))
    jump = np.zeros_like(left)
    jump[(left == 0) | (left == 1)] = H_MAX
    # exp(-lambda*dt) <= 1-lambda*dt+(lambda*dt)^2/2. Its input
    # convolution is <=dt*forcing. Every operation rounds outward.
    ld = F(str(COMPARISON_DECAY_LOWER))*F(step)
    decay = _up(float(1-ld+ld*ld/2))
    if not 0 < decay < 1:
        raise ValueError("Comparison recurrence must contract")
    before, state = np.empty_like(left), np.empty_like(left)
    value = 0.
    for index in range(len(left)):
        initial = _up(value+jump[index])
        value = _up(_up(decay*initial)+_up(step*forcing[index]))
        before[index], state[index] = initial, value
    comparison = np.maximum(before, state)
    power = _up(_up(WEIGHTED_TRACE_DUAL*comparison)+_up(EQUILIBRIUM_OUTPUT*network))
    power = _up(_up(power+_up(LINE_RATE_GAIN*line_rate))+_up(TRACE_GAIN*guide_trace))
    inverse_forcing = _up(power+_up(line_rate/2))
    command = np.zeros_like(left)
    for index, coefficient in enumerate(_impulse_prefix()):
        lag = index*samples_per_delay
        delayed = _delay(inverse_forcing, lag) if lag else inverse_forcing
        command = _up(command+_up(coefficient*delayed))
    # Uniform P<=1 is proved below; it encloses any older impulse samples.
    tail = inverse_filter_certificate(FILTER_TAPS)["tail_upper"]
    command = _up(command+tail+REMOTE_EVENT_COMMAND)
    initial_tail = REMOTE_EVENT_COMMAND+tail
    command_delayed = _up(.5*_up(_delay(command, samples_per_delay, initial_tail)
                                +_delay(command, 2*samples_per_delay, initial_tail)))
    shape = np.minimum(_shape_lower(left, begin, end), _shape_lower(right, begin, end))
    returned_shape = np.minimum(_shape_lower(left-CONVERTER_DELAY, begin, end),
                                _shape_lower(right-CONVERTER_DELAY, begin, end))
    line_increment = _down((PHOTON_PEAK-PILOT_CEILING)*shape)
    # Quiet B0 >= aquiet/jmin leaves at least (1-jmin)*B0 at either emitter.
    emitted = _down(_down((1-SPIN_FLOOR)*MINIMUM_PILOT+line_increment)-command)-ROUNDING_GUARD
    quiet_loop = (1-SPIN_FLOOR)/(2*SPIN_FLOOR)*RECEIPT_RATE_CEILING
    loop_increment = _down((5-quiet_loop)*returned_shape)
    Kplus = (1+SPIN_FLOOR)/(2*SPIN_FLOOR)
    # Source return >= B-|a_delayed|-|dB|. The separate rotor power
    # -Psupport-Wdot requires at most Kplus*(|Psupport|+|Wdot|).
    # Quiet B0 pays aquiet+Kplus*Pquiet; only event increments remain.
    use = _up(_up(Kplus*loop_rate)+command_delayed)
    use = _up(_up(use+_up(Kplus*power))+_up((Kplus+.5)*line_rate))
    ramp_margin = _down(_down(_down(PILOT_POWER+loop_increment)+line_increment)-use)-ROUNDING_GUARD
    # While guide/receipt transitions run, the full main loop supplies at
    # least 5-1. The reaction endpoints are already positive above.
    qpeak = _up(_up(1+GUIDE_NETWORK_CEILING)+_up(power+QUIET_POWER_CEILING))
    qpeak = _up(_up(qpeak+line_rate)+loop_rate)
    event_margin = _down(4-_up(Kplus*qpeak))-ROUNDING_GUARD
    event_active = (right > onset-.5) & (left < max(onset+RAMP_TIME+.5, 1))
    margin = np.where(event_active, event_margin, ramp_margin)
    # A uniform extra incoming allowance covers small changes to the ideal
    # moving-reflector power ratio, without entering this proof's dynamics.
    absorption_allowance = 4e-6
    margin_after_allowance = margin-absorption_allowance
    if (comparison.max() >= 2 or inverse_forcing.max()+INVERSE_L1*QUIET_POWER_CEILING >= 1
            or np.min(emitted) <= 0 or np.min(margin_after_allowance) <= 0):
        raise ValueError("Endpoint or incident-power envelope failed")
    row = dict(upward=bool(upward), bins=len(left), samples_per_delay=samples_per_delay,
        bin_width=step, start=start, finish=finish, event_begin=begin, event_end=end,
        maximum_event_support_power=float(power.max()), maximum_event_command=float(command.max()),
        minimum_emitted_margin=float(emitted.min()), minimum_incident_margin=float(margin.min()),
        minimum_incident_margin_after_allowance=float(margin_after_allowance.min()),
        additional_incident_allowance=absorption_allowance, maximum_event_rotor_power=float(qpeak.max()),
        allowed_extra_encounter_fraction=2*SPIN_FLOOR*absorption_allowance/float(qpeak.max()),
        inverse_tail_upper=tail, comparison_decay_upper=float(decay),
        maximum_comparison_state=float(comparison.max()), final_comparison_state=float(state[-1]),
        fixed_bin_outward_rounding=True, complete_bin_enclosures=True,
        unmodeled_float_guard=ROUNDING_GUARD)
    arrays = dict(time_left=left, time_right=right, event_support_power_upper=power,
        event_command_upper=command, emitted_margin_lower=emitted,
        incident_margin_lower=margin_after_allowance, comparison_state_upper=comparison)
    return row, arrays


def separation_certificate(minimum_panel):
    """Bound old event tails before the next prescribed fill starts.

    A falling event's latest forcing ends at +385+1/16; the next rising
    comparison starts at panel-387-1/16. At a 784-delta separation the
    gap is at least 11.875. The slow scalar comparison decays at rate >=8.
    Its comparison state is globally below 2. Positive inverse coefficients
    have l1<3; ninety-six retained taps require another 1.5 delta.
    """
    if not np.isfinite(minimum_panel) or minimum_panel < 784:
        raise ValueError("Endpoint event proof requires at least 784 delta between interfaces")
    certified_panel = 784.
    gap = certified_panel-2*CONVERTER_RAMP-2*RAMP_TIME-2*CONVERTER_DELAY-4
    # Use only rational inequalities: exp(-x)<=2^-floor(x), since e>2.
    exponent = int(np.floor(8*(gap-FILTER_TAPS*SHORT_DELAY)))
    single = F(12, 2**exponent)
    series = single/(1-F(1, 2**int(8*certified_panel)))
    if gap <= FILTER_TAPS*SHORT_DELAY or series >= F(str(REMOTE_EVENT_COMMAND)):
        raise ValueError("Separated-event tail exceeds its budget")
    return dict(minimum_panel_over_delay=float(minimum_panel), certified_separation=certified_panel, forcing_gap_lower=float(gap),
        remote_command_upper=float(series), allocated_remote_command=REMOTE_EVENT_COMMAND)
