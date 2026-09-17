"""Steady guide loading, delayed optical paths and a receiving store.

The guide has a fixed operating point while useful output and recycling
share a downstream dispatch port. A delayed sampled regulator can change
the emitter power; the guide receives that power after the feed flight.
Microscopic splitters, store constitutive laws and path supports remain
separate assembly requirements.
"""
from __future__ import annotations

from bisect import bisect_left

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm

from .constitutive_joints_and_optics import ring_equilibrium, ring_rhs, ring_state


def transfer_envelope(peak_power, transit_delay, *, operating_fraction=.4,
                      escape_depth=1., radius_cap=1.5, energy_cap=1.4,
                      input_peak_multiple=1.5, buffer_floor_fraction=.25,
                      feed_delay_fraction=.5, output_delay_fraction=.5):
    """Count the guide, useful transit, both local paths and stored margin.

    For a tensile ring, x>=1 and h<=hcap imply q_out<=eta*(hcap-1)/(2*pi).
    This gives a rigorous path-energy ceiling conditional on that state
    envelope. Steady nominal operation is an exact solution for every
    demand between zero and the prepared useful peak.
    """
    peak, delay = np.broadcast_arrays(np.asarray(peak_power, float), np.asarray(transit_delay, float))
    values = (operating_fraction, escape_depth, radius_cap, energy_cap, input_peak_multiple,
              buffer_floor_fraction, feed_delay_fraction, output_delay_fraction)
    if (not all(np.isfinite(a).all() for a in (peak, delay)) or np.any(peak < 0) or np.any(delay <= 0)
            or not np.isfinite(values).all() or not 0 < operating_fraction < 1 or escape_depth <= 0
            or radius_cap <= 1 or energy_cap < 1/np.sqrt(1-operating_fraction)
            or radius_cap < 1/np.sqrt(1-operating_fraction) or input_peak_multiple < 1
            or min(buffer_floor_fraction, feed_delay_fraction, output_delay_fraction) < 0):
        raise ValueError("finite nonnegative powers and admissible positive preparation parameters required")
    C = peak*delay
    Rref = delay/(2*np.pi*radius_cap)
    M = 4*np.pi*Rref*peak/(escape_depth*operating_fraction)
    H0 = M/np.sqrt(1-operating_fraction)
    output_multiple = 2*(energy_cap-1)/operating_fraction
    feed_capacity = feed_delay_fraction*input_peak_multiple*C
    output_capacity = output_delay_fraction*output_multiple*C
    floor = buffer_floor_fraction*C
    prepared = (1+buffer_floor_fraction)*C+feed_capacity+output_capacity+energy_cap*M
    nominal_paths = (feed_delay_fraction+output_delay_fraction)*C
    return dict(reception_capacity=C, guide_reference_radius=Rref, guide_reference_inventory=M,
        nominal_guide_energy=H0, nominal_path_energy=nominal_paths,
        nominal_minimum_preparation=C+nominal_paths+H0, prepared_energy=prepared,
        buffer_floor=floor, initial_buffer=prepared-H0-nominal_paths,
        input_power_ceiling=input_peak_multiple*peak, output_power_ceiling=output_multiple*peak,
        feed_path_energy_ceiling=feed_capacity, output_path_energy_ceiling=output_capacity,
        guide_energy_ceiling=energy_cap*M)


def square_demand_integral(time, peak, half_period, duration):
    """Exact cumulative useful energy, with zero demand outside the stroke."""
    if not np.isfinite([peak, half_period, duration]).all() or peak < 0 or half_period <= 0 or duration < 0:
        raise ValueError("finite nonnegative peak/duration and positive half-period required")
    t = np.clip(np.asarray(time, float), 0, duration)
    cycles = np.floor(t/(2*half_period))
    phase = t-2*half_period*cycles
    return peak*(cycles*half_period+np.minimum(phase, half_period))


def dispatch_power(demand, arrived_ring_output):
    """Split arriving light and use the receiving store for any shortfall."""
    need, output = np.broadcast_arrays(np.asarray(demand, float), np.asarray(arrived_ring_output, float))
    if not np.isfinite(need).all() or not np.isfinite(output).all() or np.any(need < 0) or np.any(output < 0):
        raise ValueError("finite nonnegative request and ring output required")
    direct = np.minimum(need, output)
    return dict(direct=direct, bypass=need-direct, recycle=output-direct, delivered=need)


def regulator_command(state, *, operating_fraction=.4, escape_depth=1., mode="constant",
                      input_peak_multiple=1.5, action_gain=.02, momentum_gain=-.05):
    """Bounded optical-power command from a delayed ring-state sample.

    Constant loading needs no mechanical feedback. The feedback variant
    makes small corrections to photon action and radial momentum; the
    aggressive variant attempts rapid action regulation and velocity
    damping. Both are test controllers, with gains in Rref/c units.
    """
    equilibrium = ring_equilibrium(operating_fraction, escape_depth=escape_depth)
    q0, z0 = equilibrium["input_power"], equilibrium["state"][2]
    x, p, z = np.asarray(state)[:3]
    if mode == "constant":
        raw = q0
    elif mode == "feedback":
        raw = q0-action_gain*(z-z0)-momentum_gain*p
    elif mode == "aggressive":
        s = ring_state(x, p, z)
        raw = escape_depth*z/(2*np.pi*x*x)-s["gamma"]/x*((z-z0)+2*p)
    else:
        raise ValueError("unknown optical regulator")
    return float(np.clip(raw, 0., input_peak_multiple*q0))


def sampled_control_modes(*, mode="constant", operating_fraction=.4, escape_depth=1.,
                          sample_period=3*np.pi/20, actuator_time=.25,
                          total_flight_delay=3*np.pi, action_gain=.02, momentum_gain=-.05):
    """Exact linear sampled map for an integer signal-plus-power delay.

    The emitter's first-order response commutes with a pure flight delay.
    Four local states (ring and applied input power) therefore receive a
    held command from an integer number of past samples. Matrix exponentials
    resolve the continuous plant exactly between these controller samples.
    Saturation and finite perturbations are tested by the nonlinear solver.
    """
    if (not np.isfinite([sample_period, actuator_time, total_flight_delay, action_gain, momentum_gain]).all()
            or min(sample_period, actuator_time) <= 0 or total_flight_delay < 0):
        raise ValueError("finite gains, positive controller times and nonnegative delay required")
    steps = int(round(total_flight_delay/sample_period))
    if abs(steps*sample_period-total_flight_delay) > 1e-10:
        raise ValueError("linear sampled map requires an integer number of delay samples")
    eq = ring_equilibrium(operating_fraction, escape_depth=escape_depth)
    x, _, z = eq["state"]
    b = escape_depth/(2*np.pi)
    A = np.array([[0., 1/x, 0., 0.], [-1/x, 0., 1/x**2, 0.],
                  [b*operating_fraction, 0., -b/x, x], [0., 0., 0., -1/actuator_time]])
    if mode == "constant":
        feedback = np.zeros(4)
    elif mode == "feedback":
        feedback = np.array([0., -momentum_gain, -action_gain, 0.])
    elif mode == "aggressive":
        feedback = np.array([-2*eq["input_power"]/x, -2/x, b/x**2-1/x, 0.])
    else:
        raise ValueError("unknown optical regulator")
    generator = np.zeros((5, 5))
    generator[:4, :4] = A
    generator[3, 4] = 1/actuator_time
    transition = expm(generator*sample_period)
    update = np.zeros((4*(steps+1), 4*(steps+1)))
    update[:4, :4] = transition[:4, :4]
    update[:4, -4:] += np.outer(transition[:4, 4], feedback)
    if steps:
        update[4:, :-4] = np.eye(4*steps)
    eigenvalues = np.linalg.eigvals(update)
    radius = float(np.max(abs(eigenvalues)))
    return dict(continuous_matrix=A, command_derivative=feedback, update_matrix=update,
                eigenvalues=eigenvalues, spectral_radius=radius, delay_samples=steps,
                asymptotic_exponent=float(np.log(radius)/sample_period))


def simulate_transfer(*, mode="constant", operating_fraction=.4, escape_depth=1.,
                      initial_radius_fraction=0., initial_momentum=0., initial_action_fraction=0.,
                      half_period=3.8238248063636506, demand_intervals=80,
                      sample_period=3*np.pi/20, actuator_time=.25, maximum_step=.125,
                      output_step=.125, action_gain=.02, momentum_gain=-.05,
                      rtol=2e-9, atol=2e-11):
    """Integrate a ring with two flight paths and delayed sampled control.

    Time and energy units are Rref/c and the guide reference inventory.
    The feed, outgoing and sensor flight times are delta/2, where delta
    is the inherited path scale 2*pi*1.5. The source command is held for
    sample_period and its emitter has a first-order actuator. A method of
    steps queries completed dense-output segments for all delayed values.
    The store is reconstructed independently from cumulative port flows.
    """
    if (not np.isfinite([sample_period, actuator_time, maximum_step, output_step, half_period,
                        initial_radius_fraction, initial_momentum, initial_action_fraction,
                        action_gain, momentum_gain, rtol, atol]).all()
            or min(sample_period, actuator_time, maximum_step, output_step, half_period, rtol, atol) <= 0
            or demand_intervals < 1 or int(demand_intervals) != demand_intervals):
        raise ValueError("positive finite solver/controller parameters and an integer demand length required")
    eq = ring_equilibrium(operating_fraction, escape_depth=escape_depth)
    q0, initial = eq["input_power"], eq["state"].copy()
    initial[0] *= 1+initial_radius_fraction
    initial[1] = initial_momentum
    initial[2] *= 1+initial_action_fraction
    initial_energy = float(ring_state(*initial)["energy"])
    if not 1 < initial[0] < 1.5 or initial_energy >= 1.4:
        raise ValueError("initial guide state must lie inside the prepared tensile envelope")
    delay = 2*np.pi*1.5
    feed_delay = output_delay = sensor_delay = delay/2
    if sample_period > min(feed_delay, output_delay, sensor_delay):
        raise ValueError("sample period must fit the method-of-steps causal interval")
    envelope = transfer_envelope(q0, delay, operating_fraction=operating_fraction, escape_depth=escape_depth)
    demand_duration = demand_intervals*half_period
    final_time = demand_duration+delay
    # x, p, z, emitted power, integrated ring input, integrated ring output,
    # integrated emitter output. The last three coordinates start at zero.
    initial_state = np.r_[initial, q0, 0., 0., 0.]
    prehistory = np.r_[eq["state"], q0, 0., 0., 0.]
    ends, solutions = [], []

    def past(t):
        if t < 0:
            value = prehistory.copy()
            value[4:] = q0*t
            return value
        if t == 0:
            return initial_state
        index = bisect_left(ends, t)
        if index >= len(ends):
            raise ValueError("delayed query reached an uncomputed state")
        return solutions[index](t)

    def tensile(t, y):
        return y[0]-1.
    def radius_limit(t, y):
        return 1.5-y[0]
    def energy_limit(t, y):
        return 1.4-ring_state(*y[:3])["energy"]
    for event in (tensile, radius_limit, energy_limit):
        event.terminal = True
        event.direction = -1
    times, records, commands = [], [], []
    current, t0, boundary = initial_state.copy(), 0., None
    while t0 < final_time-1e-12:
        t1 = min(t0+sample_period, final_time)
        command = regulator_command(past(t0-sensor_delay), mode=mode,
                                    operating_fraction=operating_fraction, escape_depth=escape_depth,
                                    action_gain=action_gain, momentum_gain=momentum_gain)
        def rhs(t, y):
            incoming = max(float(past(t-feed_delay)[3]), 0.)
            ring = ring_rhs(y[:3], incoming, escape_depth=escape_depth)
            outgoing = escape_depth*y[2]/(2*np.pi*y[0]**2)
            return np.r_[ring[:3], (command-y[3])/actuator_time, incoming, outgoing, y[3]]
        solution = solve_ivp(rhs, (t0, t1), current, method="DOP853", dense_output=True,
                             max_step=maximum_step, rtol=rtol, atol=atol,
                             events=(tensile, radius_limit, energy_limit))
        if not solution.success:
            raise ValueError(solution.message)
        end = float(solution.t[-1])
        ends.append(end)
        solutions.append(solution.sol)
        grid = np.linspace(t0, end, int(np.ceil((end-t0)/output_step))+1)
        times.append(grid)
        records.append(solution.sol(grid))
        commands.append(np.full(grid.shape, command))
        current, t0 = solution.y[:, -1], end
        if solution.status == 1:
            boundary = ("tensile", "radius", "energy")[next(i for i, a in enumerate(solution.t_events) if len(a))]
            break
    time, history, command = np.concatenate(times), np.concatenate(records, axis=1), np.concatenate(commands)
    state = ring_state(*history[:3])
    old_feed = np.column_stack([past(t-feed_delay) for t in time])
    old_output = np.column_stack([past(t-output_delay) for t in time])
    output = escape_depth*history[2]/(2*np.pi*history[0]**2)
    arrived_output = escape_depth*old_output[2]/(2*np.pi*old_output[0]**2)
    # The prehistory guide is at equilibrium, and both local paths are
    # prefilled. Useful donor traffic starts at t=0 and drains after demand.
    cumulative_demand = square_demand_integral(time, q0, half_period, demand_duration)
    cumulative_arrivals = square_demand_integral(time-delay, q0, half_period, demand_duration)
    inflight = cumulative_demand-cumulative_arrivals
    feed_energy = history[6]-old_feed[6]
    output_energy = history[5]-old_output[5]
    initial_buffer = float(envelope["prepared_energy"])-initial_energy-delay*q0
    buffer = initial_buffer+cumulative_arrivals-cumulative_demand+old_output[5]+output_delay*q0-history[6]
    request = np.where((time < demand_duration) & (np.mod(time, 2*half_period) < half_period), q0, 0.)
    dispatch = dispatch_power(request, arrived_output)
    ledger = buffer+state["energy"]+inflight+feed_energy+output_energy
    balance = state["energy"]-initial_energy-history[4]+history[5]
    return dict(time=time, history=history, command=command, input_power=old_feed[3],
        output_power=output, arrived_output_power=arrived_output, useful_power=request,
        useful_energy=cumulative_demand, external_inflight_energy=inflight,
        feed_path_energy=feed_energy, output_path_energy=output_energy, buffer_energy=buffer,
        ledger_energy=ledger, ring_energy_balance_error=balance, envelope=envelope,
        boundary=boundary, complete=boundary is None, demand_duration=demand_duration,
        requested_useful_energy=float(square_demand_integral(demand_duration, q0, half_period, demand_duration)),
        initial_guide_state=initial, equilibrium=eq, dispatch=dispatch, ring=state)
