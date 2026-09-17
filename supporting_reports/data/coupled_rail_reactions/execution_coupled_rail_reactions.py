"""Local rotor/support energy exchange with frozen macro support duties.

The reaction assembly uses exact series constitutive states. Its separate
bidirectional work branch is ideal and has zero flight time in this local
trial. Propagating interfaces, moving macro baselines and losses require
their own equations before applying a whole-history certificate.
"""
from dataclasses import dataclass
from math import asinh, exp, hypot, sqrt

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq, minimize_scalar

from .scheduled_optical_transfer import (
    CONVERTER_DELAY, CONVERTER_NET_POWER, CONVERTER_RAMP, GUIDE_MASS,
    GUIDE_RADIUS, PILOT_POWER, RAMP_TIME, ROTOR_MASS, SPIN_FLOOR,
    guide_radius, inverse_guide, preparation, rotor_optical_ports,
    rotor_rhs, rotor_state, smooth_step,
)
from .shared_rail_reactions import rotor_trace_and_rate, total_trace_bound


def scalar_sheet_state(tension, inventory, joint_inventory):
    """Scalar inversion of the same two-direction series law, for ODE use."""
    T, M, m, alpha = float(tension), float(inventory), float(joint_inventory), 1e-4
    if not np.isfinite([T, M, m]).all() or T < 0 or min(M, m) <= 0:
        raise ValueError("finite nonnegative duty and positive inventories required")
    scale = .9*M

    def values(t):
        root = hypot(t, scale)
        S = exp(asinh(t/scale)/2)
        force = t/S
        den = 1-2*alpha*force/m
        if den <= 0:
            return None
        j = 1/sqrt(den)
        tie = alpha*force*j
        return root, S, force, j, tie, den

    def residual(t):
        v = values(t)
        return 1e100 if v is None else t+v[4]-T

    t = 0. if T == 0 else brentq(residual, 0., T, xtol=1e-14, rtol=1e-14)
    root, S, force, j, tie, den = values(t)
    if den < 1e-8:
        raise ValueError("scalar solver requires a resolved joint force margin")
    fp = (1-t/(2*root))/S
    jp = alpha*fp*j**3/m
    D = 1+alpha*fp*j+alpha*force*jp
    return dict(energy=root+.1*M+m*(j+1/j),
        derivative=(t/root+2*alpha*force*jp)/D,
        core_stretch=S, joint_stretch=j, force_margin=den)


@dataclass
class FrozenReaction:
    tension: np.ndarray
    core_inventory: np.ndarray
    joint_inventory: np.ndarray
    trace_bound: float = total_trace_bound()

    def __post_init__(self):
        self.tension, self.core_inventory, self.joint_inventory = (
            np.asarray(a, float) for a in (self.tension, self.core_inventory, self.joint_inventory))
        if any(a.shape != (2,) for a in (self.tension, self.core_inventory, self.joint_inventory)):
            raise ValueError("two frozen support populations required")
        self.base = [scalar_sheet_state(*args) for args in
                     zip(self.tension, self.core_inventory, self.joint_inventory)]

    def state(self, trace):
        if abs(trace) > self.trace_bound*(1+1e-10):
            raise ValueError("reaction leaves its charged tensor envelope")
        bias = self.trace_bound/3
        amplitude = max(0., bias+trace/3)
        states = [scalar_sheet_state(T+weight*amplitude, M, m) for weight, T, M, m in
                  zip((1., .5), self.tension, self.core_inventory, self.joint_inventory)]
        return dict(energy=sum(s["energy"]-b["energy"] for s, b in zip(states, self.base))+3*bias,
            derivative=(states[0]["derivative"]+.5*states[1]["derivative"])/3,
            maximum_joint_stretch=max(s["joint_stretch"] for s in states))


def guide_trace_rate(guide):
    """Exact derivative of Pi_g=M_g(h_g-x/gamma), with prescribed radius."""
    v = guide["speed"]
    return (guide["energy_rate"]-GUIDE_MASS*v/GUIDE_RADIUS*np.sqrt(1-v*v)
            *(1-guide["acceleration_parameter"]))


def coupled_power(state, network_power, reaction, guide_trace=0., guide_rate=0.):
    r = rotor_trace_and_rate(state, 0.)
    support = reaction.state(float(r["trace"]+guide_trace))
    c, a = support["derivative"], r["input_rate_coefficient"]
    denominator = 1+c*a
    if denominator <= 0:
        raise ValueError("coupled work law has a singular input response")
    free_rate = r["trace_rate"]+guide_rate
    power = (network_power-c*free_rate)/denominator
    return dict(rotor_power=power, reaction_power=c*(free_rate+a*power),
        reaction_energy=support["energy"], energy_trace_derivative=c,
        total_trace=r["trace"]+guide_trace, denominator=denominator)


def simulate_coupled_transition(left, right, reaction, *, initial_heat=1e-8,
                                maximum_step=.12, output_step=.08,
                                rtol=2e-9, atol=2e-11):
    """A scheduled step whose support energy feeds back into rotor power."""
    if min(left, right) < 0 or max(left, right) > 1 or initial_heat <= 0:
        raise ValueError("unit-bounded receipts and positive initial heat required")
    prep = preparation()
    onset = -RAMP_TIME-.5 if right >= left else -.5

    def guide(t):
        return inverse_guide(t-onset, left+PILOT_POWER, right+PILOT_POWER)

    initial_h = (prep["initial_dynamic_energy"]-GUIDE_MASS*guide_radius(left+PILOT_POWER)
                 -(left+PILOT_POWER)-left)/ROTOR_MASS
    spin2 = initial_h**2-1-2*initial_heat
    if spin2 <= SPIN_FLOOR**2:
        raise ValueError("initial heat exceeds the prepared spin allowance")
    state = np.array([initial_h, 0., sqrt(spin2), initial_heat])
    initial_reaction_energy = reaction.state(0.)["energy"]
    loop_begin = min(onset-.5, 0.)-CONVERTER_RAMP-CONVERTER_DELAY-1
    loop_end = max(onset+RAMP_TIME+.5, 1.)+1

    def loop_out(t):
        return CONVERTER_NET_POWER/SPIN_FLOOR*(smooth_step(t-loop_begin, CONVERTER_RAMP)[0]
                                              -smooth_step(t-loop_end, CONVERTER_RAMP)[0])

    start = min(-RAMP_TIME-2, loop_begin-1)
    end = max(RAMP_TIME+8, loop_end+CONVERTER_RAMP+8)
    cuts = [s+shift for s in (loop_begin, loop_begin+CONVERTER_RAMP,
                              loop_end, loop_end+CONVERTER_RAMP)
            for shift in (0., CONVERTER_DELAY)]
    cuts = sorted(set([start, end, 0., 1., onset, onset-.5, onset+.5,
                       onset+RAMP_TIME, onset+RAMP_TIME-.5, onset+RAMP_TIME+.5, *cuts]))
    cuts = [t for t in cuts if start <= t <= end]

    def spin(t, y):
        return y[2]-SPIN_FLOOR

    def causal(t, y):
        return .999-y[2]

    def tensile(t, y):
        return y[0]/sqrt(1-y[2]**2)-1

    for event in (spin, causal, tensile):
        event.terminal, event.direction = True, -1
    times, records, segments, boundary = [], [], [], None
    y0 = np.r_[state, 0., 0., 0., 0.]
    for low, high in zip(cuts[:-1], cuts[1:]):
        midpoint = (low+high)/2
        receipt_difference = (left if midpoint < 1 else right)-(left if midpoint < 0 else right)

        def rhs(t, y):
            g = guide(t)
            network = (receipt_difference+guide(t-.5)["output_power"]-guide(t+.5)["input_power"]
                       +loop_out(t-CONVERTER_DELAY)-loop_out(t))
            c = coupled_power(y[:4], network, reaction, g["pressure_trace"], guide_trace_rate(g))
            return np.r_[rotor_rhs(y[:4], c["rotor_power"]), network, c["rotor_power"]**2,
                         abs(c["reaction_power"]), abs(c["rotor_power"])/y[2]]

        solution = solve_ivp(rhs, (low, high), y0, method="DOP853", dense_output=True,
            max_step=maximum_step, rtol=rtol, atol=atol, events=(spin, causal, tensile))
        if not solution.success:
            raise ValueError(solution.message)
        stop = solution.t[-1]
        grid = np.linspace(low, stop, max(2, int(np.ceil((stop-low)/output_step))+1))
        if times:
            grid = grid[1:]
        times.append(grid)
        records.append(solution.sol(grid))
        segments.append((low, stop, solution.sol, receipt_difference))
        y0 = solution.y[:, -1]
        if solution.status:
            boundary = ("spin", "causal", "tensile")[next(i for i, e in enumerate(solution.t_events) if len(e))]
            break
    time, values = np.concatenate(times), np.concatenate(records, axis=1)
    s, g = rotor_state(values[:4]), guide(time)
    network = (np.where(time < 1, left, right)-np.where(time < 0, left, right)
               +guide(time-.5)["output_power"]-guide(time+.5)["input_power"]
               +loop_out(time-CONVERTER_DELAY)-loop_out(time))
    gd = guide_trace_rate(g)
    coupled = [coupled_power(values[:4, i], network[i], reaction, g["pressure_trace"][i], gd[i])
               for i in range(len(time))]
    coupled = {key: np.array([row[key] for row in coupled]) for key in coupled[0]}
    nodes, weights = np.polynomial.legendre.leggauss(20)
    feed = .25*np.sum(weights[:, None]*guide(time[None]+.25*(nodes[:, None]+1))["input_power"], axis=0)
    output = .25*np.sum(weights[:, None]*guide(time[None]-.25*(nodes[:, None]+1))["output_power"], axis=0)
    useful = left+(right-left)*np.clip(time, 0, 1)
    converter = CONVERTER_DELAY/2*np.sum(weights[:, None]*loop_out(
        time[None]-CONVERTER_DELAY/2*(nodes[:, None]+1)), axis=0)
    rotor_energy = ROTOR_MASS*s["energy"]
    ledger = rotor_energy+coupled["reaction_energy"]+g["energy"]+feed+output+useful+converter
    ports = rotor_optical_ports(coupled["rotor_power"], values[2])
    reaction_power = coupled["reaction_power"]
    available = (np.where(time < 1, left, right)+guide(time-.5)["output_power"]
                 -np.where(time < 0, left, right)+loop_out(time-CONVERTER_DELAY)
                 +np.maximum(-reaction_power, 0.))
    demanded = guide(time+.5)["input_power"]+loop_out(time)+np.maximum(reaction_power, 0.)
    bypass = available-ports["incoming"]
    result = dict(time=time, state=values[:4], network_power=network, **coupled,
        rotor_energy=rotor_energy, guide_energy=g["energy"], converter_energy=converter,
        thermal_energy=ROTOR_MASS*s["thermal_energy"], proper_stretch=s["proper_stretch"],
        radial_speed=s["radial_speed"], rotor_input_l2=values[5],
        reaction_work_throughput=values[6], rotor_reflective_exposure=values[7],
        initial_reaction_energy=initial_reaction_energy,
        coupled_energy_error=rotor_energy+coupled["reaction_energy"]
            -ROTOR_MASS*initial_h-initial_reaction_energy-values[4],
        complete_ledger_error=ledger-prep["initial_dynamic_energy"]-initial_reaction_energy,
        converter_incident_margin=bypass,
        converter_output_balance_error=bypass+ports["outgoing"]-demanded,
        reciprocal_power_error=coupled["rotor_power"]+reaction_power-network,
        complete=boundary is None, boundary=boundary)
    # Locate narrow response extrema on the solver's dense polynomial.
    # Brackets are seeded by the eight strongest recorded values and split
    # at every forcing join, retaining both one-sided power limits.
    metrics = dict(minimum_spin=(values[2], 1.),
        maximum_thermal_energy=(result["thermal_energy"], -1.),
        maximum_absolute_trace=(abs(coupled["total_trace"]), -1.),
        maximum_absolute_rotor_power=(abs(coupled["rotor_power"]), -1.),
        maximum_absolute_reaction_power=(abs(reaction_power), -1.),
        minimum_converter_incident_margin=(bypass, 1.))

    def metric_at(t, segment, key):
        _, _, dense, difference = segment
        y = dense(t)[:4]
        gnow = guide(t)
        N = (difference+guide(t-.5)["output_power"]-guide(t+.5)["input_power"]
             +loop_out(t-CONVERTER_DELAY)-loop_out(t))
        cp = coupled_power(y, N, reaction, gnow["pressure_trace"], guide_trace_rate(gnow))
        available = (difference+guide(t-.5)["output_power"]+loop_out(t-CONVERTER_DELAY)
                     +max(-cp["reaction_power"], 0.))
        return dict(minimum_spin=y[2], maximum_thermal_energy=ROTOR_MASS*rotor_state(y)["thermal_energy"],
            maximum_absolute_trace=abs(cp["total_trace"]), maximum_absolute_rotor_power=abs(cp["rotor_power"]),
            maximum_absolute_reaction_power=abs(cp["reaction_power"]),
            minimum_converter_incident_margin=available-rotor_optical_ports(cp["rotor_power"], y[2])["incoming"])[key]

    extrema = {}
    for key, (sampled, sign) in metrics.items():
        best = float(np.min(sign*sampled))
        for i in np.argsort(sign*sampled)[:8]:
            lo, hi = time[max(0, i-1)], time[min(len(time)-1, i+1)]
            for segment in segments:
                a, b = max(lo, segment[0]), min(hi, segment[1])
                if b <= a:
                    continue
                objective = lambda t: sign*metric_at(t, segment, key)
                optimum = minimize_scalar(objective, bounds=(a, b), method="bounded", options={"xatol": 1e-10})
                best = min(best, objective(a), objective(b), float(optimum.fun))
        extrema[key] = sign*best
    result["numerical_extrema"] = extrema
    return result
